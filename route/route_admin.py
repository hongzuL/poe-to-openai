import json
import logging
import os
import platform
import sys
from typing import Any, Dict, Optional

import httpx
from fastapi import APIRouter, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from api import poe_api
from util.env_manager import (
    generate_custom_token,
    get_sanitized_config,
    read_env_raw,
    save_env_config,
)
from util.process_manager import (
    get_latest_logs,
    get_server_status,
    start_server_process,
    stop_server_process,
)

router = APIRouter(prefix="/api/admin", tags=["admin"])


class ConfigUpdateRequest(BaseModel):
    SYSTEM_TOKEN: Optional[str] = None
    CUSTOM_TOKEN: Optional[str] = None
    HOST: Optional[str] = None
    PORT: Optional[int] = None
    MODEL_MAPPING: Optional[Any] = None
    ALLOWED_ORIGINS: Optional[str] = None
    PROXY_TYPE: Optional[str] = None
    PROXY_HOST: Optional[str] = None
    PROXY_PORT: Optional[str] = None
    PROXY_USERNAME: Optional[str] = None
    PROXY_PASSWORD: Optional[str] = None
    POE_SIMPLIFY_SCHEMAS: Optional[bool] = None
    POE_TOOL_MODE: Optional[str] = None
    POE_EMULATE_BOTS: Optional[str] = None
    POE_KEEPALIVE_SECONDS: Optional[int] = None
    POE_STREAM_TIMEOUT: Optional[int] = None
    POE_FIRST_EVENT_TIMEOUT: Optional[int] = None
    POE_IDLE_TIMEOUT: Optional[int] = None
    POE_RETRY_COUNT: Optional[int] = None
    POE_DEBUG_LOG: Optional[bool] = None
    LOG_LEVEL: Optional[str] = None


class TestPoeRequest(BaseModel):
    system_token: Optional[str] = None
    bot_name: Optional[str] = "gpt-4o-mini"
    prompt: Optional[str] = "Hello, please reply with 'OK'."


@router.get("/status")
async def get_status():
    """获取当前服务状态和系统信息"""
    cfg = read_env_raw()
    port = int(cfg.get("PORT", 39527))
    status = get_server_status(expected_port=port)
    status["host"] = cfg.get("HOST", "0.0.0.0")
    status["has_system_token"] = bool(cfg.get("SYSTEM_TOKEN"))
    status["has_custom_token"] = bool(cfg.get("CUSTOM_TOKEN"))
    status["platform_details"] = {
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "python": sys.version.split()[0],
    }
    return status


@router.get("/config")
async def get_config():
    """获取脱敏配置信息"""
    return get_sanitized_config()


@router.post("/config")
async def update_config(req: ConfigUpdateRequest):
    """更新配置信息"""
    try:
        data = req.model_dump(exclude_unset=True)
        save_env_config(data)
        return {"success": True, "message": "配置已保存至 .env", "config": get_sanitized_config()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存配置失败: {str(e)}")


@router.post("/token/generate")
async def generate_token():
    """生成一个新的强随机访问令牌"""
    token = generate_custom_token()
    return {"token": token}


@router.post("/server/start")
async def start_server():
    """启动后端服务"""
    res = start_server_process()
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("message"))
    return res


@router.post("/server/stop")
async def stop_server():
    """停止后端服务"""
    res = stop_server_process()
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("message"))
    return res


@router.post("/server/restart")
async def restart_server():
    """重启后端服务"""
    stop_res = stop_server_process()
    start_res = start_server_process()
    if not start_res.get("success"):
        raise HTTPException(status_code=400, detail=f"重启失败: {start_res.get('message')}")
    return {"success": True, "message": "服务已成功重启", "pid": start_res.get("pid")}


@router.get("/logs")
async def get_logs(lines: int = 100):
    """获取最新日志"""
    logs = get_latest_logs(lines=lines)
    return {"logs": logs}


@router.get("/poe-models")
async def list_poe_models():
    """从 Poe 官方 API 拉取当前账号可用的模型列表（含定价/上下文/tools 支持），
    供 Web UI 模型映射表选择。价格统一换算为 美元/1M tokens。"""
    raw_cfg = read_env_raw()
    api_key = raw_cfg.get("SYSTEM_TOKEN", "")
    if not api_key:
        raise HTTPException(status_code=400, detail="未配置 Poe API key (SYSTEM_TOKEN)")

    try:
        # 复用 poe_api 的会话工厂（自动带上出站代理配置）
        async with poe_api.create_client() as session:
            resp = await session.get(
                "https://api.poe.com/v1/models",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=30.0,
            )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"请求 Poe 模型列表失败: {e}")

    if resp.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=f"Poe 返回 HTTP {resp.status_code}: {resp.text[:200]}",
        )

    def per_million(v):
        try:
            return round(float(v) * 1_000_000, 4) if v is not None else None
        except (TypeError, ValueError):
            return None

    models = []
    for m in resp.json().get("data", []):
        arch = m.get("architecture") or {}
        pricing = m.get("pricing") or {}
        features = m.get("supported_features") or []
        models.append({
            "id": m.get("id"),
            "name": (m.get("metadata") or {}).get("display_name") or m.get("id"),
            "owned_by": m.get("owned_by") or "",
            "context_length": m.get("context_length")
                or (m.get("context_window") or {}).get("context_length"),
            "price_in": per_million(pricing.get("prompt")),
            "price_out": per_million(pricing.get("completion")),
            "price_image": pricing.get("image"),  # 图像模型按张计费，保持原始美元值
            "tools": "tools" in features,
            "output": "+".join(arch.get("output_modalities") or ["text"]),
        })
    models.sort(key=lambda x: x["id"] or "")
    return {"success": True, "count": len(models), "models": models}


@router.post("/test-poe")
async def test_poe_connection(req: TestPoeRequest):
    """测试与 Poe 上游的连通性"""
    raw_cfg = read_env_raw()
    api_key = req.system_token or raw_cfg.get("SYSTEM_TOKEN", "")
    if not api_key:
        return {"success": False, "message": "未配置 Poe API key (SYSTEM_TOKEN)"}

    # 简易检测 key 格式
    if len(api_key) < 20:
        return {"success": False, "message": "Poe API key 长度异常"}

    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get("https://api.poe.com/bot/info", headers=headers)
            # Poe 目前部分接口如果没有直接开放 info，可以通过尝试发请求测试
            return {
                "success": resp.status_code in (200, 404, 400),
                "status_code": resp.status_code,
                "message": f"连接上游响应正常 (HTTP {resp.status_code})" if resp.status_code in (200, 404, 400) else f"上游响应异常: HTTP {resp.status_code}",
            }
    except Exception as e:
        return {"success": False, "message": f"连接上游失败: {str(e)}"}