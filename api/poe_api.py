"""
Poe 协议层：OpenAI 格式与 Poe 官方 API（fastapi_poe SDK）之间的转换。

关键设计（对应 fastapi_poe 0.0.70 的协议事实）：
- 工具调用历史通过 Poe 协议的顶层 tool_calls / tool_results 字段传递
  （而不是塞进消息列表），只有 stream_request_base 支持这两个字段。
- Poe 协议没有 tool_choice，按以下规则模拟：
    "none"                                        -> 不发送任何工具定义
    {"type": "function", "function": {"name": X}} -> 只发送名为 X 的工具
    "required" / "auto" / None                    -> 照常发送全部工具
  其中 required 无法被协议强制，只是尽力而为。
- QueryRequest 的 pydantic 模型会静默丢弃额外字段，reasoning 参数经 QueryRequest
  传递是无效的；reasoning 标记由路由层以文本形式附加到最后一条用户消息上。

工具调用的两种模式（环境变量 POE_TOOL_MODE 控制：auto / native / emulate）：
- native：tools 直接透传给 Poe 协议（要求该 bot 在 Poe 侧支持 tools）。
- emulate：prompt 仿真 —— 把工具 schema 注入提示词、要求模型输出约定格式的
  JSON，代理解析后构造标准 OpenAI tool_calls 返回。用于 Poe 未接入工具协议的
  bot（如 gemini-3.7-flash）。auto 模式下先尝试原生，被 Poe 拒绝后自动降级为
  仿真，并在进程内缓存结论（每个 bot 只探测一次）。
"""

import asyncio
import json
import logging
import os
import re
import time

import httpx
from fastapi_poe import (
    ProtocolMessage,
    QueryRequest,
    ToolCallDefinition,
    ToolDefinition,
    ToolResultDefinition,
    get_bot_response,
)
from fastapi_poe.client import stream_request_base

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 600

DEFAULT_BOT = "gpt-4o"

# 进程内缓存：记录已知不支持原生 tools 的 bot（auto 模式下避免重复探测失败）
_NATIVE_TOOLS_UNSUPPORTED = {}


def _get_stream_timeout():
    """POE_STREAM_TIMEOUT：整个 Poe 流的超时秒数（默认 120）。"""
    try:
        return max(10, int(os.environ.get("POE_STREAM_TIMEOUT", "120")))
    except ValueError:
        return 120


def _get_first_event_timeout():
    """POE_FIRST_EVENT_TIMEOUT：首个事件的超时秒数（默认 30）。"""
    try:
        return max(5, int(os.environ.get("POE_FIRST_EVENT_TIMEOUT", "30")))
    except ValueError:
        return 30


# ---------- 诊断日志（POE_DEBUG_LOG=1 时启用，输出到 WARNING，前缀 DIAG） ----------

def _debug_enabled():
    return os.environ.get("POE_DEBUG_LOG", "").lower() in ("1", "true", "yes")


def _dlog(msg, *args):
    """诊断日志。仅在 POE_DEBUG_LOG 开启时输出；可能包含内容片段，仅用于临时排障。"""
    if _debug_enabled():
        logger.warning("DIAG " + msg, *args)


# ---------- 流超时控制 ----------

async def _stream_with_timeout(generator, first_timeout, total_timeout):
    """
    为异步生成器的每个 item 添加超时保护：
    - first_timeout：首个 item 的超时（秒），防止 Poe 连接后无响应
    - total_timeout：整个流的超时（秒），防止单次请求无限挂起
    超时抛出 asyncio.TimeoutError。
    """
    start_time = time.monotonic()
    agen = generator.__aiter__()
    first = True

    while True:
        if first:
            timeout = first_timeout
            first = False
        else:
            elapsed = time.monotonic() - start_time
            remaining = total_timeout - elapsed
            if remaining <= 0:
                raise asyncio.TimeoutError(
                    f"Poe stream total timeout ({total_timeout}s) exceeded after {elapsed:.0f}s"
                )
            timeout = min(remaining, 30)  # 每个后续 chunk 最多等 30 秒

        try:
            item = await asyncio.wait_for(agen.__anext__(), timeout)
            yield item
        except StopAsyncIteration:
            break


# ---------- 模型映射 ----------

def _load_model_mapping():
    try:
        return json.loads(os.environ.get("MODEL_MAPPING", "{}"))
    except json.JSONDecodeError:
        logger.warning("MODEL_MAPPING 不是合法 JSON，按空映射处理")
        return {}


def get_bot(model):
    return _load_model_mapping().get(model, DEFAULT_BOT)


def list_models():
    return list(_load_model_mapping().keys())


# ---------- HTTP 会话 ----------

def create_client():
    proxy_url = _build_proxy_url()
    if proxy_url:
        return httpx.AsyncClient(timeout=DEFAULT_TIMEOUT, proxy=proxy_url)
    return httpx.AsyncClient(timeout=DEFAULT_TIMEOUT)


def _build_proxy_url():
    proxy_type = (os.environ.get("PROXY_TYPE") or "").lower()
    host = os.environ.get("PROXY_HOST")
    port = os.environ.get("PROXY_PORT")
    if not host or not port or proxy_type not in ("http", "socks"):
        return None
    username = os.environ.get("PROXY_USERNAME") or ""
    password = os.environ.get("PROXY_PASSWORD") or ""
    auth = f"{username}:{password}@" if username else ""
    scheme = "http" if proxy_type == "http" else "socks5"
    return f"{scheme}://{auth}{host}:{port}"


# ---------- 消息转换 ----------

def extract_text(content):
    """把 OpenAI 的 content（字符串或多模态数组）拍平成纯文本，非文本部分丢弃。"""
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                if item.get("type") == "text":
                    parts.append(str(item.get("text", "")))
            else:
                parts.append(str(item))
        return "".join(parts)
    return str(content)


def convert_messages(messages):
    """
    OpenAI messages -> (poe_messages, tool_calls, tool_results)

    assistant 消息携带的 tool_calls 和 role="tool" 的工具结果不进消息列表，
    而是收集为协议顶层字段 —— 这是 Poe 协议表达工具历史的唯一通道。
    """
    poe_messages = []
    tool_calls = []
    tool_results = []

    for message in messages:
        if not isinstance(message, dict):
            continue
        role = message.get("role")

        if role in ("system", "developer"):
            content = extract_text(message.get("content"))
            if content:
                poe_messages.append(ProtocolMessage(role="system", content=content))

        elif role == "user":
            poe_messages.append(
                ProtocolMessage(role="user", content=extract_text(message.get("content")))
            )

        elif role == "assistant":
            content = extract_text(message.get("content"))
            if content:
                poe_messages.append(ProtocolMessage(role="bot", content=content))
            for call in message.get("tool_calls") or []:
                function = call.get("function") or {}
                arguments = function.get("arguments", "")
                if not isinstance(arguments, str):
                    arguments = json.dumps(arguments, ensure_ascii=False)
                tool_calls.append(ToolCallDefinition(
                    id=call.get("id") or f"call_{len(tool_calls)}",
                    type=call.get("type") or "function",
                    function=ToolCallDefinition.FunctionDefinition(
                        name=function.get("name", ""),
                        arguments=arguments,
                    ),
                ))

        elif role == "tool":
            tool_results.append(ToolResultDefinition(
                role="tool",
                name=message.get("name") or "",
                tool_call_id=message.get("tool_call_id") or "",
                content=extract_text(message.get("content")),
            ))

    return poe_messages, tool_calls or None, tool_results or None


# ---------- 工具定义转换 ----------

def convert_openai_tool_to_poe_tool(tool):
    """OpenAI tool -> Poe ToolDefinition。properties 默认原样保留完整 JSON Schema。"""
    if not isinstance(tool, dict) or "function" not in tool:
        return None
    function = tool.get("function") or {}
    params = function.get("parameters") or {}
    properties = params.get("properties") or {}

    if os.environ.get("POE_SIMPLIFY_SCHEMAS", "").lower() in ("1", "true", "yes"):
        # 兼容模式：某些客户端（如旧版 claude-code-router）的复杂 schema 会被 Poe
        # 拒绝时才开启，会把 allOf / 联合类型降级为简单类型
        properties = {
            name: _simplify_parameter_definition(definition)
            for name, definition in properties.items()
        }

    return ToolDefinition(
        type="function",
        function=ToolDefinition.FunctionDefinition(
            name=function.get("name", ""),
            description=function.get("description", ""),
            parameters=ToolDefinition.FunctionDefinition.ParametersDefinition(
                type=params.get("type", "object"),
                properties=properties,
                required=params.get("required") or None,
            ),
        ),
    )


def _simplify_parameter_definition(param_def):
    """把 allOf / 联合类型等复杂参数定义降级为简单类型（兼容模式专用）。"""
    if not isinstance(param_def, dict):
        return param_def

    if "allOf" in param_def:
        simplified = {}
        for schema in param_def["allOf"]:
            if isinstance(schema, dict) and "type" in schema:
                param_type = schema["type"]
                simplified["type"] = param_type[0] if isinstance(param_type, list) else param_type
                break
        for key in ("default", "description"):
            if key in param_def:
                simplified[key] = param_def[key]
        return simplified

    if isinstance(param_def.get("type"), list):
        simplified = dict(param_def)
        simplified["type"] = param_def["type"][0]
        return simplified

    return param_def


def select_tools(tools, tool_choice):
    """按 tool_choice 过滤要发给 Poe 的工具（模拟规则见模块 docstring）。"""
    if not tools:
        return None
    if tool_choice == "none":
        return None
    if isinstance(tool_choice, dict) and tool_choice.get("type") == "function":
        name = (tool_choice.get("function") or {}).get("name")
        selected = [t for t in tools if (t.get("function") or {}).get("name") == name]
        if selected:
            return selected
        logger.warning("tool_choice 指定的函数 %r 不在 tools 中，忽略该限制", name)
    elif tool_choice == "required":
        logger.info("tool_choice=required 无法被 Poe 协议强制，按 auto 处理")
    return tools


# ---------- prompt 仿真模式（为不支持原生 tools 的 bot 补齐工具调用） ----------

_TOOLS_PROMPT_TEMPLATE = """
# Tools

You have access to the following functions:

{schemas}

When you need to call one or more functions, your ENTIRE reply must be a single
json code block in EXACTLY this format, with no other text before or after it:

```json
{{"tool_calls": [{{"name": "<function_name>", "arguments": {{"<arg>": "<value>"}}}}]}}
```

Rules:
- "arguments" must be a JSON object matching the function's parameters schema.
- Call a function ONLY when it helps answer the user's request; otherwise reply
  normally in plain text, WITHOUT any json block.
- Do not wrap the json block in any explanation. Do not invent functions that
  are not listed above.{extra}"""

_TOOLS_PROMPT_REQUIRED = "\n- In this conversation you MUST call at least one function."
_TOOLS_PROMPT_FORCED = "\n- In this conversation you MUST call the function \"{name}\"."


def build_tools_prompt(tools, tool_choice=None):
    """把 OpenAI tools 定义渲染成注入系统提示词的文本。"""
    schemas = json.dumps(
        [t.get("function", {}) for t in tools if isinstance(t, dict)],
        ensure_ascii=False, indent=2,
    )
    extra = ""
    if tool_choice == "required":
        extra = _TOOLS_PROMPT_REQUIRED
    elif isinstance(tool_choice, dict) and tool_choice.get("type") == "function":
        name = (tool_choice.get("function") or {}).get("name")
        if name:
            extra = _TOOLS_PROMPT_FORCED.format(name=name)
    return _TOOLS_PROMPT_TEMPLATE.format(schemas=schemas, extra=extra)


def fold_tool_history(messages):
    """
    仿真模式下折叠工具历史：
    - assistant 的 tool_calls 序列化为约定格式的 json 代码块（与提示词约定一致）
    - role="tool" 的工具结果包装成 user 文本消息
    """
    folded = []
    for message in messages:
        if not isinstance(message, dict):
            continue
        role = message.get("role")

        if role == "assistant":
            # 剥离历史消息中的思考块，避免模型模仿历史 thinking 风格而不再调用工具
            # （gemini 系模型看到历史中的 thinking 文本会陷入"只思考不行动"的循环）
            text = _strip_thinking(extract_text(message.get("content")))
            calls = []
            for call in message.get("tool_calls") or []:
                function = call.get("function") or {}
                arguments = function.get("arguments", {})
                if isinstance(arguments, str):
                    try:
                        arguments = json.loads(arguments)
                    except json.JSONDecodeError:
                        pass
                calls.append({"name": function.get("name", ""), "arguments": arguments})
            if calls:
                block = "```json\n" + json.dumps(
                    {"tool_calls": calls}, ensure_ascii=False
                ) + "\n```"
                text = (text + "\n\n" + block).strip() if text else block
            if text:
                folded.append({"role": "assistant", "content": text})

        elif role == "tool":
            name = message.get("name") or message.get("tool_call_id") or "tool"
            content = extract_text(message.get("content"))
            folded.append({
                "role": "user",
                "content": f"[Tool result for {name}]\n{content}",
            })

        else:
            folded.append(message)
    return folded


_TOOL_FORMAT_REMINDER = (
    "IMPORTANT: You have access to tools. When you need to use a tool, "
    "your ENTIRE response must be ONLY a ```json code block with this format:\n"
    '{"tool_calls": [{"name": "function_name", "arguments": {...}}]}\n'
    "Do NOT include any other text — no explanation, no thinking, no markdown — "
    "just the json block. If you do not need to use a tool, respond normally."
)


def inject_tools_prompt(messages, tools, tool_choice=None):
    """在消息列表中注入工具提示词（追加到已有 system 消息，或新建一条）。
    同时在对话末尾插入独立的 system 格式提醒，防止长对话中被淹没。"""
    prompt = build_tools_prompt(tools, tool_choice)
    messages = [dict(m) for m in messages if isinstance(m, dict)]

    # 1. 注入完整工具 schema 到 system 消息
    for m in messages:
        if m.get("role") == "system":
            m["content"] = extract_text(m.get("content")) + "\n" + prompt
            break
    else:
        messages.insert(0, {"role": "system", "content": prompt})

    # 2. 在最后一条 user 消息之前插入独立的 system 格式提醒
    #    保证长对话中模型一定能在最近上下文看到格式要求
    for i in range(len(messages) - 1, -1, -1):
        if messages[i].get("role") == "user":
            messages.insert(i, {"role": "system", "content": _TOOL_FORMAT_REMINDER.strip()})
            break

    return messages


_JSON_FENCE_RE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)
_THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL)
# Poe 上 gemini 系模型的思考块格式：*Thinking...* 后跟一串 "> " 引用行
_POE_THINK_RE = re.compile(
    r"\*Thinking[^\n]*\*[ \t]*\n(?:[ \t]*\n)*(?:>[^\n]*\n?)+",
    re.IGNORECASE,
)


def _strip_thinking(text):
    """剥离模型输出中的思考块：<think>...</think> 标签和 Poe 风格的 *Thinking...* 引用块。"""
    if not text:
        return ""
    cleaned = _THINK_RE.sub("", text)
    cleaned = _POE_THINK_RE.sub("", cleaned)
    return cleaned.strip()


def _escape_control_chars_in_strings(text):
    """转义 JSON 字符串值内部的原始控制字符（\\n \\r \\t 等）。
    模型经常在 arguments 里输出带原始换行的多行命令/代码，导致非法 JSON。
    逐字符扫描，仅在双引号字符串内部转义，不影响字符串外的合法空白。"""
    result = []
    in_string = False
    escaped = False
    for ch in text:
        if escaped:
            result.append(ch)
            escaped = False
            continue
        if ch == "\\":
            result.append(ch)
            escaped = True
            continue
        if ch == '"':
            in_string = not in_string
            result.append(ch)
            continue
        if in_string and ch in "\n\r\t":
            result.append({"\n": "\\n", "\r": "\\r", "\t": "\\t"}[ch])
            continue
        result.append(ch)
    return "".join(result)


def _repair_json(text):
    """尝试修复常见的 JSON 格式问题（模型输出 JSON 时常犯的错误）。"""
    # 1. 转义字符串内的原始控制字符（多行命令/代码参数最常见）
    text = _escape_control_chars_in_strings(text)
    # 2. 去除尾部逗号（如 {"a": 1,}）
    text = re.sub(r",(\s*[}\]])", r"\1", text)
    # 3. 尝试标准 JSON 解析
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # 3. 尝试用 ast.literal_eval 解析 Python 字典格式
    try:
        import ast
        obj = ast.literal_eval(text)
        if isinstance(obj, dict):
            return obj
    except (ValueError, SyntaxError):
        pass
    return None


def _try_parse_json(text):
    """尝试解析 JSON，失败时返回 None。"""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        repaired = _repair_json(text)
        if repaired is not None:
            return repaired
    return None


def parse_tool_calls_from_text(text):
    """
    从模型纯文本输出中解析工具调用。
    成功返回 OpenAI delta 格式的 tool_calls 列表；没有工具调用返回 None。
    能容忍 <think> 思考块、json 代码块、以及夹杂在正文里的裸 JSON。
    """
    if not text:
        return None

    cleaned = _strip_thinking(text)
    candidates = _JSON_FENCE_RE.findall(cleaned)

    # 裸 JSON 兜底：用 raw_decode 扫描每个 "{" 起始的对象
    decoder = json.JSONDecoder()
    idx = cleaned.find("{")
    while idx != -1:
        try:
            obj, _ = decoder.raw_decode(cleaned[idx:])
            if isinstance(obj, dict):
                candidates.append(json.dumps(obj))
            idx = cleaned.find("{", idx + 1)
        except json.JSONDecodeError:
            idx = cleaned.find("{", idx + 1)

    for candidate in candidates:
        parsed = _try_parse_json(candidate)
        if parsed is None:
            continue
        calls = parsed.get("tool_calls") if isinstance(parsed, dict) else None
        if isinstance(parsed, list):
            calls = parsed
        if not isinstance(calls, list) or not calls:
            continue

        result = []
        for i, call in enumerate(calls):
            if not isinstance(call, dict):
                break
            function = call.get("function") or {}
            name = call.get("name") or function.get("name")
            if not name:
                break
            arguments = call.get("arguments", function.get("arguments", {}))
            if not isinstance(arguments, str):
                arguments = json.dumps(arguments, ensure_ascii=False)
            result.append({
                "index": i,
                "id": call.get("id") or f"call_{i}",
                "type": "function",
                "function": {"name": name, "arguments": arguments},
            })
        else:
            if result:
                return result
    return None


def strip_tool_json_block(text):
    """解析出工具调用后，把 json 代码块和思考块从正文中剔除，返回剩余文本。"""
    if not text:
        return ""
    cleaned = _strip_thinking(text)
    cleaned = _JSON_FENCE_RE.sub("", cleaned)
    return cleaned.strip()


# ---------- 查询构造 ----------

def _build_query(poe_messages, temperature=None, stop_sequences=None):
    return QueryRequest(
        query=poe_messages,
        user_id="",
        conversation_id="",
        message_id="",
        version="1.0",
        type="query",
        temperature=temperature if temperature is not None else 0.7,
        skip_system_prompt=False,
        logit_bias={},
        stop_sequences=stop_sequences or [],
    )


def _normalize_tool_delta(raw):
    """把 Poe 返回的原始 tool_calls 增量归一化为 OpenAI delta 格式。"""
    if not isinstance(raw, dict):
        raw = raw.model_dump() if hasattr(raw, "model_dump") else {}
    function = raw.get("function") or {}
    return {
        "index": raw.get("index") or 0,
        "id": raw.get("id"),
        "type": raw.get("type") or "function",
        "function": {
            "name": function.get("name"),
            "arguments": function.get("arguments") or "",
        },
    }


def merge_tool_delta(aggregated, delta):
    """把一条 tool_calls 增量合并进按 index 聚合的字典（就地修改）。"""
    index = delta["index"]
    entry = aggregated.setdefault(index, {
        "index": index,
        "id": None,
        "type": "function",
        "function": {"name": None, "arguments": ""},
    })
    if delta.get("id"):
        entry["id"] = delta["id"]
    if delta.get("type"):
        entry["type"] = delta["type"]
    function = delta.get("function") or {}
    if function.get("name"):
        entry["function"]["name"] = function["name"]
    if function.get("arguments"):
        entry["function"]["arguments"] += function["arguments"]


def _is_transient_error(exception):
    """判断是否是可重试的瞬态错误（BotError、空响应等 Poe 后端偶发故障）。"""
    msg = str(exception).lower()
    return any(kw in msg for kw in ("error communicating with bot", "internal server error",
                                      "service unavailable", "rate limit", "timeout",
                                      "empty response"))


def _get_retry_count():
    """POE_RETRY_COUNT：瞬态错误时的重试次数（默认 2）。
    仿真模式下 gemini 系模型有概率性"只思考不回答"故障，重试是最有效的缓解手段。"""
    try:
        return max(0, min(3, int(os.environ.get("POE_RETRY_COUNT", "2"))))
    except ValueError:
        return 2


def _get_emulate_bots():
    """POE_EMULATE_BOTS：逗号分隔的 bot 名单，带 tools 请求时直接使用仿真模式，
    跳过原生探测（省去每次进程重启后的两次失败调用和积分消耗）。"""
    raw = os.environ.get("POE_EMULATE_BOTS", "")
    return {b.strip() for b in raw.split(",") if b.strip()}


# ---------- 底层查询流（原生协议） ----------

async def _native_stream(api_key, messages, model, tools=None, tool_choice=None,
                         temperature=None, stop_sequences=None, session=None):
    """
    直接走 Poe 协议的查询流，产出归一化事件：
      {"kind": "text", "text": str}
      {"kind": "tool_calls", "tool_calls": [delta...]}
      {"kind": "replace"}
    """
    poe_messages, history_tool_calls, history_tool_results = convert_messages(messages)
    query = _build_query(poe_messages, temperature, stop_sequences)

    selected = select_tools(tools, tool_choice)
    poe_tools = None
    if selected:
        converted = (convert_openai_tool_to_poe_tool(t) for t in selected)
        poe_tools = [t for t in converted if t is not None] or None

    if session is None:
        session = create_client()

    bot_name = get_bot(model)
    _dlog("native_stream 开始: bot=%s messages=%d tools=%d history_calls=%d history_results=%d",
          bot_name, len(poe_messages), len(poe_tools or []),
          len(history_tool_calls or []), len(history_tool_results or []))

    event_count = 0
    text_len = 0
    stream_gen = stream_request_base(
        request=query,
        bot_name=bot_name,
        api_key=api_key,
        tools=poe_tools,
        tool_calls=history_tool_calls,
        tool_results=history_tool_results,
        session=session,
    )
    try:
        async for message in _stream_with_timeout(
            stream_gen,
            _get_first_event_timeout(),
            _get_stream_timeout(),
        ):
            event_count += 1
            data = getattr(message, "data", None)

            # OpenAI 风格的增量块（带工具定义的查询走这里）
            if data and data.get("choices"):
                choice = data["choices"][0]
                if choice.get("finish_reason") is not None:
                    _dlog("native_stream: bot=%s 收到 finish_reason=%s (events=%d 文本=%d字符)",
                          bot_name, choice.get("finish_reason"), event_count, text_len)
                    continue
                delta = choice.get("delta") or {}
                if delta.get("tool_calls"):
                    yield {
                        "kind": "tool_calls",
                        "tool_calls": [_normalize_tool_delta(d) for d in delta["tool_calls"]],
                    }
                elif delta.get("content"):
                    text_len += len(delta["content"])
                    yield {"kind": "text", "text": delta["content"]}
                continue

            # 普通文本事件（不带工具定义的查询走这里）
            if getattr(message, "is_suggested_reply", False):
                continue
            if getattr(message, "is_replace_response", False):
                _dlog("native_stream: bot=%s 收到 replace_response（清空已收文本）", bot_name)
                yield {"kind": "replace"}
            text = getattr(message, "text", "")
            if text:
                text_len += len(text)
                yield {"kind": "text", "text": text}
    except asyncio.TimeoutError as e:
        _dlog("native_stream 超时: bot=%s events=%d 已收文本=%d字符 timeout=%s",
              bot_name, event_count, text_len, e)
        raise
    except Exception as e:
        _dlog("native_stream 异常: bot=%s events=%d 已收文本=%d字符 error=%r",
              bot_name, event_count, text_len, e)
        raise

    if event_count == 0:
        raise RuntimeError(
            f"Poe returned empty response for bot {bot_name} "
            f"(0 events, messages={len(poe_messages)}, tools={len(poe_tools or [])})"
        )

    _dlog("native_stream 结束: bot=%s events=%d 文本=%d字符", bot_name, event_count, text_len)


# ---------- 仿真模式查询 ----------

async def _emulated_events(api_key, messages, model, tools, tool_choice,
                           temperature, stop_sequences, session):
    """
    prompt 仿真：注入工具提示词 + 折叠工具历史 -> 普通查询 -> 解析输出。
    注意：工具调用的判定依赖完整回复，所以仿真模式会先聚合全部文本再产出事件。
    """
    emulated_messages = fold_tool_history(messages)
    emulated_messages = inject_tools_prompt(emulated_messages, tools, tool_choice)

    text_parts = []
    async for event in _native_stream(
        api_key, emulated_messages, model, tools=None, tool_choice=None,
        temperature=temperature, stop_sequences=stop_sequences, session=session,
    ):
        if event["kind"] == "text":
            text_parts.append(event["text"])
        elif event["kind"] == "replace":
            text_parts.clear()

    full_text = "".join(text_parts)
    tool_calls = parse_tool_calls_from_text(full_text)
    if tool_calls:
        remaining = strip_tool_json_block(full_text)
        _dlog("emulated: bot=%s 原文=%d字符 -> 解析出 %d 个工具调用，剩余文本 %d 字符",
              get_bot(model), len(full_text), len(tool_calls), len(remaining))
        if remaining:
            yield {"kind": "text", "text": remaining}
        yield {"kind": "tool_calls", "tool_calls": tool_calls}
    else:
        # 未解析到工具调用：记录原文长度和尾部预览（判断是否被 Poe 截断在 JSON 中途）
        _dlog("emulated: bot=%s 原文=%d字符，未解析到工具调用。尾部预览: %r",
              get_bot(model), len(full_text), full_text[-120:])
        # 纯思考响应（剥离 thinking 后为空）：gemini 系模型的"只思考不回答"概率性故障，
        # 作为瞬态错误抛出，由 query_stream 的重试循环重试
        stripped = _strip_thinking(full_text)
        if not stripped:
            raise RuntimeError(
                f"Poe returned empty response (thinking-only) for bot {get_bot(model)}"
            )
        # 合法文本回答：剥离 thinking 块后再返回给客户端，避免噪声混入答案
        yield {"kind": "text", "text": stripped}


# ---------- 对外统一入口 ----------

async def query_stream(api_key, messages, model, tools=None, tool_choice=None,
                       temperature=None, stop_sequences=None, session=None):
    """
    归一化的事件流。带 tools 时按 POE_TOOL_MODE 决定走原生协议还是 prompt 仿真：
      auto（默认）：先试原生，被 Poe 以"不支持 tools"拒绝后自动降级仿真并缓存结论
      native：只用原生协议
      emulate：只用 prompt 仿真
    """
    mode = os.environ.get("POE_TOOL_MODE", "auto").lower()
    bot = get_bot(model)
    emulate_bots = _get_emulate_bots()

    use_emulation = False
    if tools and tool_choice != "none":
        if mode == "emulate":
            use_emulation = True
        elif mode == "auto" and (bot in emulate_bots or _NATIVE_TOOLS_UNSUPPORTED.get(bot)):
            use_emulation = True

    _dlog("query_stream: model=%s bot=%s POE_TOOL_MODE=%s tools=%d tool_choice=%s -> %s",
          model, bot, mode, len(tools or []), tool_choice,
          "emulate" if use_emulation else ("native" if tools else "无工具普通查询"))

    if tools and not use_emulation:
        yielded_any = False
        try:
            async for event in _native_stream(
                api_key, messages, model, tools, tool_choice,
                temperature, stop_sequences, session,
            ):
                yielded_any = True
                yield event
            return
        except Exception as e:
            # 已经给客户端发过内容就不能降级了；原生强制模式下也不降级
            if yielded_any or mode == "native" or not _is_tool_rejection(e):
                raise
            _NATIVE_TOOLS_UNSUPPORTED[bot] = True
            logger.warning("bot %s 不支持原生 tools（%s），本次起切换为 prompt 仿真", bot, e)
            use_emulation = True

    if use_emulation:
        retries = _get_retry_count()
        for attempt in range(retries + 1):
            try:
                async for event in _emulated_events(
                    api_key, messages, model, tools, tool_choice,
                    temperature, stop_sequences, session,
                ):
                    yield event
                return
            except Exception as e:
                if attempt < retries and _is_transient_error(e):
                    logger.warning("bot %s 仿真模式请求失败（%s），第 %d/%d 次重试",
                                   bot, e, attempt + 1, retries)
                    await asyncio.sleep(1.0 * (attempt + 1))
                    continue
                raise
        return

    async for event in _native_stream(
        api_key, messages, model, tools, tool_choice,
        temperature, stop_sequences, session,
    ):
        yield event


async def get_responses(api_key, messages, model, tools=None, tool_choice=None,
                        temperature=None, stop_sequences=None, session=None):
    """非流式查询：聚合完整文本和完整的 tool_calls 列表。"""
    text_parts = []
    aggregated = {}

    async for event in query_stream(
        api_key, messages, model, tools, tool_choice, temperature, stop_sequences, session
    ):
        if event["kind"] == "text":
            text_parts.append(event["text"])
        elif event["kind"] == "replace":
            text_parts.clear()
        elif event["kind"] == "tool_calls":
            for delta in event["tool_calls"]:
                merge_tool_delta(aggregated, delta)

    tool_calls = [aggregated[i] for i in sorted(aggregated)] or None
    if tool_calls:
        # 非流式响应要求完整的 tool_call 对象
        for i, call in enumerate(tool_calls):
            call["id"] = call["id"] or f"call_{i}"
            call["type"] = call["type"] or "function"
            call["function"]["name"] = call["function"]["name"] or ""

    return {"text": "".join(text_parts), "tool_calls": tool_calls}


# ---------- 图像生成 ----------

async def get_image(api_key, prompt, model="dall-e-3", session=None):
    """调用 Poe 图像机器人，返回 markdown 图片链接或附件 URL。"""
    if session is None:
        session = create_client()

    result = ""
    async for partial in get_bot_response(
        messages=[ProtocolMessage(role="user", content=prompt)],
        bot_name=get_bot(model),
        api_key=api_key,
        skip_system_prompt=False,
        session=session,
    ):
        attachment = getattr(partial, "attachment", None)
        if attachment is not None and getattr(attachment, "url", ""):
            result = attachment.url
        elif partial.text and ("http" in partial.text or partial.text.startswith("![")):
            result = partial.text

    return result
