import asyncio
import json
import logging
import os
from datetime import datetime

from dotenv import load_dotenv
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, StreamingResponse

from api import poe_api
from util import utils
from util.auth import get_poe_api_key
from util.token_utils import calculate_usage

logger = logging.getLogger(__name__)

router = APIRouter()
load_dotenv()

MODELS_CREATED = 1720000000  # /v1/models 用的固定时间戳


@router.get("/")
async def root():
    return {"message": "poe-to-openai is running"}


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

    if stream:
        return StreamingResponse(
            openai_event_stream(model, processed_messages, api_key, tools, tool_choice,
                                temperature, stop_sequences, session),
            media_type="text/event-stream",
        )
    return await default_response(model, processed_messages, api_key, tools, tool_choice,
                                  temperature, stop_sequences, session)


def parse_stop(stop):
    """OpenAI 的 stop 参数（字符串或数组）-> stop_sequences 列表。"""
    if isinstance(stop, str):
        return [stop]
    if isinstance(stop, list):
        sequences = [s for s in stop if isinstance(s, str)]
        return sequences or None
    return None


def error_response(status_code, message, error_type="invalid_request_error"):
    return JSONResponse(
        status_code=status_code,
        content={"error": {"message": message, "type": error_type, "code": None}},
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


def stream_chunk(model, delta, finish_reason=None, usage=None, include_role=False):
    if include_role:
        delta = {"role": "assistant", **delta}
    return {
        "id": f"chatcmpl-{utils.get_uuid()}",
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
                              temperature, stop_sequences, session):
    req_id = utils.get_8_random_str()
    text_chunks = []
    had_tool_calls = False
    first_chunk = True
    n_chunks = 0
    poe_api._dlog("流式开始 %s: model=%s messages=%d tools=%d",
                  req_id, model, len(messages), len(tools or []))

    # 上游事件放进队列，主循环按 keepalive_interval 轮询：
    # 仿真模式需要攒完整段上游回复，期间长时间无输出，用 SSE 注释行（: keepalive）
    # 保活，防止客户端因读超时而断开。
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
                chunk = stream_chunk(model, {"content": event["text"]}, include_role=first_chunk)
                first_chunk = False
                n_chunks += 1
                yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
            elif event["kind"] == "tool_calls":
                had_tool_calls = True
                chunk = stream_chunk(model, {"tool_calls": event["tool_calls"]}, include_role=first_chunk)
                first_chunk = False
                n_chunks += 1
                yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
            elif event["kind"] == "replace":
                # 已发送的 chunk 无法撤回，只能停止累计 usage 的旧文本
                text_chunks.clear()
    finally:
        if not producer.done():
            producer.cancel()
            try:
                await producer
            except Exception:
                pass

    if upstream_error is not None:
        logger.error("Poe 上游请求失败: %s: %s", type(upstream_error).__name__, upstream_error)
        poe_api._dlog("流式异常 %s: model=%s 已发chunks=%d 已发文本=%d字符 error=%r",
                      req_id, model, n_chunks, sum(len(t) for t in text_chunks), upstream_error)

        # 超时或首次请求失败：给客户端一个明确的错误信息
        if n_chunks == 0:
            if isinstance(upstream_error, asyncio.TimeoutError):
                error_content = f"Poe upstream timeout: {upstream_error}"
            else:
                error_content = f"Poe upstream error ({type(upstream_error).__name__}): {upstream_error}"
            chunk = stream_chunk(model, {"content": error_content}, finish_reason="stop",
                                 include_role=True)
            yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
        else:
            # 已经给客户端发过内容，发送一个空的 finish chunk
            yield f"data: {json.dumps(stream_chunk(model, {}, finish_reason='stop'), ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"
        return

    usage = calculate_usage(prompt_text(messages), "".join(text_chunks), model)
    finish_reason = "tool_calls" if had_tool_calls else "stop"
    poe_api._dlog("流式结束 %s: model=%s chunks=%d 文本=%d字符 tool_calls=%s finish=%s",
                  req_id, model, n_chunks, sum(len(t) for t in text_chunks),
                  had_tool_calls, finish_reason)
    final_chunk = stream_chunk(model, {}, finish_reason=finish_reason, usage=usage)
    yield f"data: {json.dumps(final_chunk, ensure_ascii=False)}\n\n"
    yield "data: [DONE]\n\n"


async def default_response(model, messages, api_key, tools, tool_choice,
                           temperature, stop_sequences, session):
    req_id = utils.get_8_random_str()
    poe_api._dlog("非流式开始 %s: model=%s messages=%d tools=%d",
                  req_id, model, len(messages), len(tools or []))
    try:
        result = await poe_api.get_responses(api_key, messages, model, tools, tool_choice,
                                             temperature, stop_sequences, session)
    except Exception as e:
        logger.error("Poe 上游请求失败: %s: %s", type(e).__name__, e)
        detail = str(e)[:300] or type(e).__name__
        return error_response(502, f"上游 Poe 请求失败: {detail}", "upstream_error")

    poe_api._dlog("非流式结束 %s: model=%s 文本=%d字符 tool_calls=%d",
                  req_id, model, len(result["text"]),
                  len(result.get("tool_calls") or []))

    usage = calculate_usage(prompt_text(messages), result["text"], model)

    if result.get("tool_calls"):
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
