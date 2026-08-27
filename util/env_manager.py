import json
import os
import platform
import re
import secrets
from pathlib import Path
from typing import Any, Dict, Optional

ENV_PATH = Path(".env")
EXAMPLE_PATH = Path(".env.example")

DEFAULT_MODEL_MAPPING = {
    "gpt-5.4": "gpt-5.4",
    "gpt-4o": "gpt-4o",
    "gpt-4o-mini": "gpt-4o-mini",
    "claude-sonnet-4.6": "claude-sonnet-4.6",
    "claude-opus-4.8": "claude-opus-4.8",
    "gemini-3.5-flash": "gemini-3.5-flash",
    "gemini-3.1-pro": "gemini-3.1-pro",
    "grok-4.6": "grok-4.6",
    "dall-e-3": "gpt-image-2",
    "nano-banana-2": "nano-banana-2",
}

DEFAULT_CONFIG = {
    "SYSTEM_TOKEN": "",
    "CUSTOM_TOKEN": "",
    "HOST": "0.0.0.0",
    "PORT": "39527",
    "MODEL_MAPPING": json.dumps(DEFAULT_MODEL_MAPPING, ensure_ascii=False),
    "ALLOWED_ORIGINS": "",
    "PROXY_TYPE": "",
    "PROXY_HOST": "",
    "PROXY_PORT": "",
    "PROXY_USERNAME": "",
    "PROXY_PASSWORD": "",
    "POE_SIMPLIFY_SCHEMAS": "false",
    "POE_TOOL_MODE": "auto",
    "POE_EMULATE_BOTS": "gemini-3.7-flash,gemini-3.6-flash",
    "POE_KEEPALIVE_SECONDS": "15",
    "POE_STREAM_TIMEOUT": "120",
    "POE_FIRST_EVENT_TIMEOUT": "30",
    "POE_RETRY_COUNT": "2",
    "POE_DEBUG_LOG": "0",
}


def generate_custom_token() -> str:
    """生成强随机 sk- 访问令牌。"""
    return f"sk-{secrets.token_hex(24)}"


def read_env_raw() -> Dict[str, str]:
    """读取 .env 文件并返回键值对字典。"""
    config = DEFAULT_CONFIG.copy()
    if not ENV_PATH.exists():
        return config

    try:
        content = ENV_PATH.read_text(encoding="utf-8")
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip()
            if (v.startswith("'") and v.endswith("'")) or (v.startswith('"') and v.endswith('"')):
                v = v[1:-1]
            config[k] = v
    except Exception as e:
        print(f"Warning: Failed to read .env: {e}")
    return config


def mask_token(token: str) -> str:
    """脱敏显示 token"""
    if not token:
        return ""
    if len(token) <= 8:
        return "********"
    return token[:4] + "*" * (len(token) - 8) + token[-4:]


def get_sanitized_config() -> Dict[str, Any]:
    """返回适合前端 UI 展示的安全配置数据。"""
    raw = read_env_raw()
    model_mapping = {}
    try:
        model_mapping = json.loads(raw.get("MODEL_MAPPING", "{}"))
    except Exception:
        model_mapping = DEFAULT_MODEL_MAPPING.copy()

    return {
        "has_system_token": bool(raw.get("SYSTEM_TOKEN")),
        "system_token_preview": mask_token(raw.get("SYSTEM_TOKEN", "")),
        "custom_token": raw.get("CUSTOM_TOKEN", ""),
        "host": raw.get("HOST", "0.0.0.0"),
        "port": int(raw.get("PORT", 39527)),
        "model_mapping": model_mapping,
        "allowed_origins": raw.get("ALLOWED_ORIGINS", ""),
        "proxy_type": raw.get("PROXY_TYPE", ""),
        "proxy_host": raw.get("PROXY_HOST", ""),
        "proxy_port": raw.get("PROXY_PORT", ""),
        "proxy_username": raw.get("PROXY_USERNAME", ""),
        "proxy_password_set": bool(raw.get("PROXY_PASSWORD", "")),
        "poe_simplify_schemas": raw.get("POE_SIMPLIFY_SCHEMAS", "false").lower() == "true",
        "poe_tool_mode": raw.get("POE_TOOL_MODE", "auto"),
        "poe_emulate_bots": raw.get("POE_EMULATE_BOTS", "gemini-3.7-flash,gemini-3.6-flash"),
        "poe_keepalive_seconds": int(raw.get("POE_KEEPALIVE_SECONDS", "15")),
        "poe_stream_timeout": int(raw.get("POE_STREAM_TIMEOUT", "120")),
        "poe_first_event_timeout": int(raw.get("POE_FIRST_EVENT_TIMEOUT", "30")),
        "poe_retry_count": int(raw.get("POE_RETRY_COUNT", "2")),
        "poe_debug_log": raw.get("POE_DEBUG_LOG", "0") == "1",
    }


def save_env_config(updates: Dict[str, Any]) -> None:
    """将前端提交的数据安全保存到 .env 文件。"""
    current = read_env_raw()

    # 处理 SYSTEM_TOKEN (如果前端传空或星号，保留旧值)
    sys_token = updates.get("SYSTEM_TOKEN")
    if sys_token is not None and sys_token.strip() and not sys_token.startswith("***"):
        clean_token = re.sub(r"\s+", "", sys_token.strip())
        # 检测重复粘贴
        if len(clean_token) > 80:
            half = len(clean_token) // 2
            if clean_token[:half] == clean_token[half:]:
                clean_token = clean_token[:half]
        current["SYSTEM_TOKEN"] = clean_token

    # 处理 CUSTOM_TOKEN
    custom_token = updates.get("CUSTOM_TOKEN")
    if custom_token is not None and custom_token.strip():
        current["CUSTOM_TOKEN"] = custom_token.strip()
    elif not current.get("CUSTOM_TOKEN"):
        current["CUSTOM_TOKEN"] = generate_custom_token()

    if "HOST" in updates:
        current["HOST"] = str(updates["HOST"]).strip()
    if "PORT" in updates:
        current["PORT"] = str(updates["PORT"]).strip()

    if "MODEL_MAPPING" in updates:
        mapping = updates["MODEL_MAPPING"]
        if isinstance(mapping, dict):
            current["MODEL_MAPPING"] = json.dumps(mapping, ensure_ascii=False)
        elif isinstance(mapping, str):
            current["MODEL_MAPPING"] = mapping.strip()

    for k in [
        "ALLOWED_ORIGINS",
        "PROXY_TYPE",
        "PROXY_HOST",
        "PROXY_PORT",
        "PROXY_USERNAME",
        "POE_TOOL_MODE",
        "POE_EMULATE_BOTS",
        "POE_KEEPALIVE_SECONDS",
        "POE_STREAM_TIMEOUT",
        "POE_FIRST_EVENT_TIMEOUT",
        "POE_RETRY_COUNT",
    ]:
        if k in updates:
            current[k] = str(updates[k]).strip()

    # 处理代理密码
    if "PROXY_PASSWORD" in updates and updates["PROXY_PASSWORD"] is not None:
        if updates["PROXY_PASSWORD"] != "KEEP_UNCHANGED":
            current["PROXY_PASSWORD"] = str(updates["PROXY_PASSWORD"])

    if "POE_SIMPLIFY_SCHEMAS" in updates:
        val = updates["POE_SIMPLIFY_SCHEMAS"]
        current["POE_SIMPLIFY_SCHEMAS"] = "true" if str(val).lower() in ("true", "1") else "false"

    if "POE_DEBUG_LOG" in updates:
        val = updates["POE_DEBUG_LOG"]
        current["POE_DEBUG_LOG"] = "1" if str(val).lower() in ("true", "1") else "0"

    # 生成 .env 文本
    lines = [
        "# poe-to-openai configuration file",
        f"SYSTEM_TOKEN={current.get('SYSTEM_TOKEN', '')}",
        f"CUSTOM_TOKEN={current.get('CUSTOM_TOKEN', '')}",
        f"HOST={current.get('HOST', '0.0.0.0')}",
        f"PORT={current.get('PORT', '39527')}",
        f"MODEL_MAPPING='{current.get('MODEL_MAPPING', json.dumps(DEFAULT_MODEL_MAPPING))}'",
        f"ALLOWED_ORIGINS={current.get('ALLOWED_ORIGINS', '')}",
        f"PROXY_TYPE={current.get('PROXY_TYPE', '')}",
        f"PROXY_HOST={current.get('PROXY_HOST', '')}",
        f"PROXY_PORT={current.get('PROXY_PORT', '')}",
        f"PROXY_USERNAME={current.get('PROXY_USERNAME', '')}",
        f"PROXY_PASSWORD={current.get('PROXY_PASSWORD', '')}",
        f"POE_SIMPLIFY_SCHEMAS={current.get('POE_SIMPLIFY_SCHEMAS', 'false')}",
        f"POE_TOOL_MODE={current.get('POE_TOOL_MODE', 'auto')}",
        f"POE_EMULATE_BOTS={current.get('POE_EMULATE_BOTS', 'gemini-3.7-flash,gemini-3.6-flash')}",
        f"POE_KEEPALIVE_SECONDS={current.get('POE_KEEPALIVE_SECONDS', '15')}",
        f"POE_STREAM_TIMEOUT={current.get('POE_STREAM_TIMEOUT', '120')}",
        f"POE_FIRST_EVENT_TIMEOUT={current.get('POE_FIRST_EVENT_TIMEOUT', '30')}",
        f"POE_RETRY_COUNT={current.get('POE_RETRY_COUNT', '2')}",
        f"POE_DEBUG_LOG={current.get('POE_DEBUG_LOG', '0')}",
        "",
    ]

    ENV_PATH.write_text("\n".join(lines), encoding="utf-8")
    if platform.system() != "Windows":
        try:
            os.chmod(ENV_PATH, 0o600)
        except Exception:
            pass