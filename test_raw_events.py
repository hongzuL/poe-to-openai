"""用与代理完全一致的输入直连 Poe，dump 全部原始事件，确认流结束方式。"""
import asyncio
import os
import sys
sys.path.insert(0, '.')
from dotenv import load_dotenv
load_dotenv()
from api.poe_api import create_client, build_tools_prompt, fold_tool_history, inject_tools_prompt, convert_messages, _build_query
from fastapi_poe.client import stream_request_base

TOOLS = [
    {"type": "function", "function": {"name": "read_file", "description": "Read a file", "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}},
    {"type": "function", "function": {"name": "write_file", "description": "Write a file", "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]}}},
]

MESSAGES = [
    {"role": "user", "content": "能不能把所有poe可用模型和价格写在文档里"},
    {"role": "assistant", "content": "*Thinking...*\n\n> **Exploring Model Options**\n> \n> I am currently examining our models.json file to identify all available Poe models and their associated pricing. This will help me determine the most suitable location for this information.\n> \n"},
    {"role": "user", "content": "继续"},
]


async def main():
    # 走和代理完全相同的管线：fold -> inject -> convert -> query
    folded = fold_tool_history(MESSAGES)
    injected = inject_tools_prompt(folded, TOOLS, None)
    poe_messages, tc, tr = convert_messages(injected)
    query = _build_query(poe_messages, None, None)

    print(f"poe_messages count: {len(poe_messages)}")
    for i, m in enumerate(poe_messages):
        print(f"  [{i}] role={m.role} len={len(m.content or '')}")
    print("=" * 60)

    session = create_client()
    events = 0
    full = ""
    try:
        async for message in stream_request_base(
            request=query, bot_name="gemini-3.7-flash",
            api_key=os.environ["SYSTEM_TOKEN"], session=session,
        ):
            events += 1
            text = getattr(message, "text", "") or ""
            full += text
            raw = getattr(message, "raw_response", None)
            rtype = raw.get("type") if isinstance(raw, dict) else None
            print(f"[event {events}] type={rtype} text_len={len(text)} replace={getattr(message, 'is_replace_response', None)} suggested={getattr(message, 'is_suggested_reply', None)}")
    except Exception as e:
        print(f"EXCEPTION: {type(e).__name__}: {e}")
    finally:
        await session.aclose()

    print("=" * 60)
    print(f"TOTAL events={events} chars={len(full)}")
    print(f"FULL: {full!r}")


if __name__ == "__main__":
    asyncio.run(main())
