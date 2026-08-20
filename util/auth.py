import os

from fastapi import HTTPException


def get_poe_api_key():
    """返回服务端持有的 Poe API key。调用方的身份已由鉴权中间件校验。"""
    api_key = os.environ.get("SYSTEM_TOKEN", "")
    if not api_key:
        raise HTTPException(status_code=500, detail="服务端未配置 SYSTEM_TOKEN 环境变量")
    return api_key
