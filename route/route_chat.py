import asyncio
import json
import logging
import os
import time
from datetime import datetime

from dotenv import load_dotenv
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, StreamingResponse

from api import poe_api
from util import utils
from util.auth import get_poe_api_key
from util.logging_utils import get_current_request_id, set_current_request_id
from util.token_utils import calculate_usage

logger = logging.getLogger(__name__)

router = APIRouter()
load_dotenv()

MODELS_CREATED = 1720000000  # /v1/models 用的固定时间戳


@router.get("/v1/models")
async def list_models():
    return {
        "object": "list",
        "data": [
            {"id": name, "object": "model", "created": MODELS_CREATED, "owned_by": "poe"}
            for name in poe_api.list_models()
        ],
    }


@router.post("/v1/chat/completions")
async def chat_proxy(request: Request):
    req_id = set_current_request_id(request.headers.get("x-request-id"))

    try:
        body = await request.json()
    except json.JSONDecodeError:
        return error_response(400, "请求体不是合法的 JSON")
    if not isinstance(body, dict):
        return error_response(400, "请求体必须是 JSON 对象")

    model = body.get("model") or "gpt-3.5-turbo"
    messages = body.get("messages")
    if not isinstance(messages, list) or not messages:
        return error_response(400, "messages 必须是非空数组")

    # 模型必须存在于映射表，不做静默回退（避免"请求 A 模型实际走了 B 模型"）
    if not poe_api.get_bot(model):
        return error_response(
            404,
            f"模型 '{model}' 未在 MODEL_MAPPING 中配置。可用模型见 GET /v1/models；"
            f"可在 Web UI 的模型映射表中添加映射，保存后即时生效",
            param="model",
            code="model_not_found",
        )

    stream = bool(body.get("stream", False))
    tools = body.get("tools")
    tool_choice = body.get("tool_choice")
    temperature = body.get("temperature")
    reasoning_effort = body.get("reasoning_effort")
    max_reasoning_tokens = body.get("max_reasoning_tokens")
    stop_sequences = parse_stop(body.get("stop"))

    # reasoning 参数无法通过 Poe 协议字段传递，以文本标记附加到最后一条用户消息
    processed_messages = preprocess_last_user_message(messages, reasoning_effort, max_reasoning_tokens)

    api_key = get_poe_api_key()
    session = getattr(request.app.state, "http_session", None)

    logger.info("request_start: req_id=%s model=%s stream=%s tools=%d messages=%d",
                req_id, model, stream, len(tools or []), len(messages))

    headers = {
        "X-Request-ID": req_id,
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",
    }

    if stream:
        return StreamingResponse(
            openai_event_stream(model, processed_messages, api_key, tools, tool_choice,
                                temperature, stop_sequences, session, req_id),
            media_type="text/event-stream",
            headers=headers,
        )
    resp = await default_response(model, processed_messages, api_key, tools, tool_choice,
                                  temperature, stop_sequences, session, req_id)
    resp.headers["X-Request-ID"] = req_id
    return resp


def parse_stop(stop):
    """OpenAI 的 stop 参数（字符串或数组）-> stop_sequences 列表。"""
    if isinstance(stop, str):
        return [stop]
    if isinstance(stop, list):
        sequences = [s for s in stop if isinstance(s, str)]
        return sequences or None
    return None


def error_response(status_code, message, error_type="invalid_request_error", param=None, code=None):
    return JSONResponse(
        status_code=status_code,
        content={"error": {"message": message, "type": error_type, "param": param, "code": code}},
    )


def preprocess_last_user_message(messages, reasoning_effort=None, max_reasoning_tokens=None):
    """预处理最后一条用户消息，添加 reasoning 参数标记"""
    if not messages:
        return messages

    # 创建消息副本以避免修改原始列表
    processed_messages = [msg.copy() for msg in messages]

    # 获取最后一条消息
    last_message = processed_messages[-1]

    # 检查是否为用户消息且内容为字符串
    if last_message.get("role") == "user" and isinstance(last_message.get("content"), str):
        content = last_message["content"]

        # 检查是否已包含标记
        has_reasoning_effort = "--reasoning_effort=" in content
        has_thinking_budget = "--thinking_budget=" in content

        # 构建要追加的标记
        append_parts = []

        # 处理 reasoning_effort
        if reasoning_effort and reasoning_effort in ["minimal", "low", "medium", "high"] and not has_reasoning_effort:
            append_parts.append(f" --reasoning_effort={reasoning_effort}")

        # 处理 max_reasoning_tokens
        if max_reasoning_tokens is not None and not has_thinking_budget:
            try:
                budget = int(max_reasoning_tokens)
                # 裁剪范围到 0-30768
                budget = max(0, min(budget, 30768))
                append_parts.append(f" --thinking_budget={budget}")
            except (ValueError, TypeError):
                pass  # 忽略无效值

        # 如果有要追加的内容，则追加到消息末尾
        if append_parts:
            # 去除尾部空格后再追加
            content = content.rstrip()
            content += "".join(append_parts)
            last_message["content"] = content

    return processed_messages


def prompt_text(messages):
    return "\n".join(poe_api.extract_text(msg.get("content")) for msg in messages if isinstance(msg, dict))


def stream_chunk(model, delta, finish_reason=None, usage=None, include_role=False, completion_id=None):
    if include_role:
        delta = {"role": "assistant", **delta}
    return {
        "id": completion_id or f"chatcmpl-{utils.get_uuid()}",
        "object": "chat.completion.chunk",
        "created": int(datetime.now().timestamp()),
        "model": model,
        "choices": [{"index": 0, "delta": delta, "finish_reason": finish_reason}],
        "usage": usage,
    }


def keepalive_interval():
    try:
        return max(1, int(os.environ.get("POE_KEEPALIVE_SECONDS", "15")))
    except ValueError:
        return 15


async def openai_event_stream(model, messages, api_key, tools, tool_choice,
                              temperature, stop_sequences, session, req_id=None):
    if req_id:
        set_current_request_id(req_id)
    completion_id = f"chatcmpl-{utils.get_uuid()}"
    start_time = time.monotonic()
    text_chunks = []
    had_tool_calls = False
    first_chunk = True
    n_chunks = 0
    keepalive_count = 0
    finish_reason_from_upstream = None

    queue = asyncio.Queue()

    async def produce():
        try:
            async for event in poe_api.query_stream(api_key, messages, model, tools, tool_choice,
                                                    temperature, stop_sequences, session):
                await queue.put(("event", event))
        except Exception as e:
            await queue.put(("error", e))
        else:
            await queue.put(("done", None))

    producer = asyncio.create_task(produce())
    upstream_error = None
    try:
        while True:
            try:
                kind, payload = await asyncio.wait_for(queue.get(), timeout=keepalive_interval())
            except asyncio.TimeoutError:
                keepalive_count += 1
                yield ": keepalive\n\n"
                continue

            if kind == "done":
                break
            if kind == "error":
                upstream_error = payload
                break

            event = payload
            if event["kind"] == "text":
                text_chunks.append(event["text"])
                chunk = stream_chunk(model, {"content": event["text"]},
                                     include_role=first_chunk, completion_id=completion_id)
                first_chunk = False
                n_chunks += 1
                yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
            elif event["kind"] == "tool_calls":
                had_tool_calls = True
                chunk = stream_chunk(model, {"tool_calls": event["tool_calls"]},
                                     include_role=first_chunk, completion_id=completion_id)
                first_chunk = False
                n_chunks += 1
                yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
            elif event["kind"] == "finish":
                finish_reason_from_upstream = event.get("finish_reason")
            elif event["kind"] == "replace":
                text_chunks.clear()
    except asyncio.CancelledError:
        elapsed = time.monotonic() - start_time
        logger.warning("stream_cancelled: req_id=%s model=%s after=%.2fs chunks=%d",
                       req_id, model, elapsed, n_chunks)
        raise
    finally:
        if not producer.done():
            producer.cancel()
            try:
                await producer
            except Exception:
                pass

    elapsed = time.monotonic() - start_time

    if upstream_error is not None:
        logger.error("stream_error: req_id=%s model=%s error_type=%s error=%s elapsed=%.2fs chunks=%d",
                     req_id, model, type(upstream_error).__name__, upstream_error, elapsed, n_chunks)

        err_payload = {
            "error": {
                "message": str(upstream_error) or type(upstream_error).__name__,
                "type": "upstream_error",
                "code": "poe_upstream_error",
            }
        }
        # 输出符合 OpenAI 规范的错误 SSE 消息，明确告知客户端失败，不再追加虚假的 stop + [DONE]
        yield f"data: {json.dumps(err_payload, ensure_ascii=False)}\n\n"
        return

    usage = calculate_usage(prompt_text(messages), "".join(text_chunks), model)
    finish_reason = finish_reason_from_upstream or ("tool_calls" if had_tool_calls else "stop")
    logger.info("stream_completed: req_id=%s model=%s elapsed=%.2fs chunks=%d chars=%d tool_calls=%s keepalive=%d finish=%s",
                req_id, model, elapsed, n_chunks, sum(len(t) for t in text_chunks),
                had_tool_calls, keepalive_count, finish_reason)

    final_chunk = stream_chunk(model, {}, finish_reason=finish_reason, usage=usage, completion_id=completion_id)
    yield f"data: {json.dumps(final_chunk, ensure_ascii=False)}\n\n"
    yield "data: [DONE]\n\n"


async def default_response(model, messages, api_key, tools, tool_choice,
                           temperature, stop_sequences, session, req_id=None):
    if req_id:
        set_current_request_id(req_id)
    start_time = time.monotonic()
    try:
        result = await poe_api.get_responses(api_key, messages, model, tools, tool_choice,
                                             temperature, stop_sequences, session)
    except Exception as e:
        elapsed = time.monotonic() - start_time
        logger.error("nonstream_error: req_id=%s model=%s error_type=%s error=%s elapsed=%.2fs",
                     req_id, model, type(e).__name__, e, elapsed)
        detail = str(e)[:300] or type(e).__name__
        return error_response(502, f"上游 Poe 请求失败: {detail}", "upstream_error")

    elapsed = time.monotonic() - start_time
    usage = calculate_usage(prompt_text(messages), result["text"], model)
    had_tool_calls = bool(result.get("tool_calls"))

    logger.info("nonstream_completed: req_id=%s model=%s elapsed=%.2fs chars=%d tool_calls=%s",
                req_id, model, elapsed, len(result["text"]), had_tool_calls)

    if had_tool_calls:
        message = {
            "role": "assistant",
            "content": result["text"] or None,
            "tool_calls": result["tool_calls"],
        }
        finish_reason = "tool_calls"
    else:
        message = {"role": "assistant", "content": result["text"]}
        finish_reason = "stop"

    data = {
        "id": f"chatcmpl-{utils.get_uuid()}",
        "object": "chat.completion",
        "created": int(datetime.now().timestamp()),
        "model": model,
        "choices": [{
            "index": 0,
            "message": message,
            "logprobs": None,
            "finish_reason": finish_reason,
        }],
        "usage": usage,
    }
    return JSONResponse(content=data)
