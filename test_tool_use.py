"""
工具调用链路端到端测试（在服务器本机运行）。

用法:
    CUSTOM_TOKEN=sk-xxx python3 test_tool_use.py              # 默认测 gemini-3.7-flash
    CUSTOM_TOKEN=sk-xxx MODEL=gpt-4o python3 test_tool_use.py # 指定模型

覆盖:
    1. 非流式: 定义工具 -> 期望返回 tool_calls
    2. 完整回路: 回传工具结果 -> 期望返回最终文本回答
    3. 流式: 同上流程走 stream=True
"""
import json
import os
import sys

import requests

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:39527")
TOKEN = os.environ.get("CUSTOM_TOKEN", "")
MODEL = os.environ.get("MODEL", "gemini-3.7-flash")

if not TOKEN:
    sys.exit("请先设置 CUSTOM_TOKEN 环境变量（与 .env 中一致）")

HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

TOOLS = [{
    "type": "function",
    "function": {
        "name": "get_current_weather",
        "description": "Get the current weather in a given location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "城市名，例如 Boston"},
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
            },
            "required": ["location"],
        },
    },
}]

QUESTION = "What's the weather like in Boston today? Use the tool."
FAKE_RESULT = "晴天，气温 22°C，微风。"

passed = []


def report(name, ok, detail=""):
    passed.append(ok)
    mark = "✓ PASS" if ok else "✗ FAIL"
    print(f"{mark} | {name}" + (f" | {detail}" if detail else ""))


def chat(messages, stream=False):
    resp = requests.post(
        f"{BASE_URL}/v1/chat/completions",
        headers=HEADERS,
        json={"model": MODEL, "messages": messages, "tools": TOOLS,
              "tool_choice": "auto", "stream": stream},
        stream=stream, timeout=180,
    )
    return resp


def test_round1_nonstream():
    """第 1 轮：模型应返回 tool_calls"""
    resp = chat([{"role": "user", "content": QUESTION}])
    if resp.status_code != 200:
        report("非流式第1轮", False, f"HTTP {resp.status_code}: {resp.text[:200]}")
        return None
    choice = resp.json()["choices"][0]
    msg = choice["message"]
    calls = msg.get("tool_calls")
    if not calls:
        report("非流式第1轮", False, f"未返回 tool_calls，content={str(msg.get('content'))[:120]}")
        return None
    call = calls[0]
    name_ok = call["function"]["name"] == "get_current_weather"
    try:
        args = json.loads(call["function"]["arguments"])
        args_ok = "location" in args
    except json.JSONDecodeError:
        args_ok = False
    report("非流式第1轮: 返回 tool_calls", True, f"finish_reason={choice['finish_reason']}")
    report("非流式第1轮: 函数名与参数合法", name_ok and args_ok,
           f"name={call['function']['name']}, args={call['function']['arguments'][:80]}")
    return call


def test_round2_tool_result(call):
    """第 2 轮：回传工具结果 -> 模型应给出最终文本回答"""
    messages = [
        {"role": "user", "content": QUESTION},
        {"role": "assistant", "content": None, "tool_calls": [call]},
        {"role": "tool", "tool_call_id": call["id"],
         "name": "get_current_weather", "content": FAKE_RESULT},
    ]
    resp = chat(messages)
    if resp.status_code != 200:
        report("第2轮回传工具结果", False, f"HTTP {resp.status_code}: {resp.text[:200]}")
        return
    msg = resp.json()["choices"][0]["message"]
    content = msg.get("content") or ""
    has_answer = len(content) > 0
    mentions = ("22" in content) or ("晴" in content)
    report("第2轮回传工具结果: 返回文本回答", has_answer, content[:100])
    report("第2轮: 回答利用了工具结果", mentions, "包含 22°C/晴" if mentions else "未提及工具结果（模型自由发挥）")


def test_stream():
    """流式：应收到 SSE chunk 并以 [DONE] 结束"""
    resp = chat([{"role": "user", "content": QUESTION}], stream=True)
    if resp.status_code != 200:
        report("流式", False, f"HTTP {resp.status_code}: {resp.text[:200]}")
        return
    got_tool_calls = False
    got_text = False
    got_done = False
    got_usage = False
    for line in resp.iter_lines():
        if not line:
            continue
        line = line.decode("utf-8")
        if not line.startswith("data: "):
            continue
        payload = line[6:]
        if payload.strip() == "[DONE]":
            got_done = True
            continue
        chunk = json.loads(payload)
        delta = chunk["choices"][0].get("delta") or {}
        if delta.get("tool_calls"):
            got_tool_calls = True
        if delta.get("content"):
            got_text = True
        if chunk.get("usage"):
            got_usage = True
        if chunk["choices"][0].get("finish_reason"):
            pass
    report("流式: 收到内容 chunk", got_tool_calls or got_text,
           f"tool_calls={got_tool_calls}, text={got_text}")
    report("流式: 正常结束([DONE]) 且带 usage", got_done and got_usage)


def test_auth():
    """鉴权：错误 token 应 401"""
    resp = requests.post(
        f"{BASE_URL}/v1/chat/completions",
        headers={"Authorization": "Bearer wrong-token"},
        json={"model": MODEL, "messages": [{"role": "user", "content": "hi"}]},
        timeout=30,
    )
    report("鉴权: 错误 token 返回 401", resp.status_code == 401)


if __name__ == "__main__":
    print(f"目标: {BASE_URL}  模型: {MODEL}\n" + "=" * 60)
    test_auth()
    call = test_round1_nonstream()
    if call:
        test_round2_tool_result(call)
    test_stream()
    print("=" * 60)
    print(f"结果: {sum(passed)}/{len(passed)} 通过")
    sys.exit(0 if all(passed) else 1)
