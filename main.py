import logging
import os
import secrets
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from api import poe_api
from route.route_chat import router as chat_router
from route.route_image import router as image_router

load_dotenv()


class ApiKeyAuthMiddleware(BaseHTTPMiddleware):
    """所有 /v1/ 接口必须携带与 CUSTOM_TOKEN 匹配的 Bearer token，否则 401。"""

    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS" or not request.url.path.startswith("/v1/"):
            return await call_next(request)

        expected = os.environ.get("CUSTOM_TOKEN", "")
        auth = request.headers.get("authorization", "")
        token = auth[7:].strip() if auth.lower().startswith("bearer ") else ""
        if not expected or not token or not secrets.compare_digest(token, expected):
            return JSONResponse(
                status_code=401,
                content={"error": {
                    "message": "Missing or invalid API key",
                    "type": "invalid_request_error",
                    "code": "invalid_api_key",
                }},
            )
        return await call_next(request)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    if not os.environ.get("CUSTOM_TOKEN"):
        logging.warning("未设置 CUSTOM_TOKEN，所有 /v1/ 请求都会被拒绝")
    if not os.environ.get("SYSTEM_TOKEN"):
        logging.warning("未设置 SYSTEM_TOKEN（Poe API key），上游请求会失败")

    app.state.http_session = poe_api.create_client()
    yield
    await app.state.http_session.aclose()


app = FastAPI(lifespan=lifespan)

app.add_middleware(ApiKeyAuthMiddleware)

# 默认不启用 CORS（纯 API 客户端不需要）；需要浏览器直连时在 .env 配置 ALLOWED_ORIGINS
allowed_origins = [o.strip() for o in os.environ.get("ALLOWED_ORIGINS", "").split(",") if o.strip()]
if allowed_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )

app.include_router(chat_router)
app.include_router(image_router)
