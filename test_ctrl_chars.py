import sys, json
sys.path.insert(0, '.')
from api.poe_api import (parse_tool_calls_from_text, strip_tool_json_block,
                         _parse_tool_calls_v2, _format_tool_call_v2, fold_tool_history)

# ============ v2 格式解析 ============

# 用用户贴出的真实失败内容：含原始换行、未转义引号、f-string、中文
evil_code = '''import json
import os
from collections import defaultdict

def format_tokens(num):
    if num is None:
        return "-"
    if num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M".replace(".0M", "M")
    print(f"Total models loaded: {len(models)}")
    lines.append("# Poe 可用模型与定价一览表 (Poe Models & Pricing Catalog)\\n")
'''

v2_text = '''<<<tool_call>>>
name: Write
arg:file_path: /Users/test/generate_models_doc.py
arg:content: <<<
''' + evil_code + '''
>>>
<<<end>>>'''

calls = parse_tool_calls_from_text(v2_text)
assert calls and len(calls) == 1, f'FAIL: {calls}'
assert calls[0]['function']['name'] == 'Write'
args = json.loads(calls[0]['function']['arguments'])
assert args['file_path'] == '/Users/test/generate_models_doc.py'
assert 'import json' in args['content']
assert 'f"{num / 1_000_000:.1f}M"' in args['content']  # 引号原样保留
assert 'Poe 可用模型与定价一览表' in args['content']  # 中文原样保留
print('PASS: v2 heredoc 完美解析含原始换行+未转义引号+中文的代码')

# 多个工具调用
multi = '''<<<tool_call>>>
name: Read
arg:file_path: a.txt
<<<end>>>
<<<tool_call>>>
name: Bash
arg:command: <<<
echo "hello" && ls -la
>>>
arg:timeout: 30
<<<end>>>'''
calls = parse_tool_calls_from_text(multi)
assert len(calls) == 2
assert calls[0]['function']['name'] == 'Read'
assert json.loads(calls[1]['function']['arguments'])['command'] == 'echo "hello" && ls -la'
assert json.loads(calls[1]['function']['arguments'])['timeout'] == 30  # 数字类型转换
print('PASS: 多工具调用 + 类型转换')

# thinking 前缀 + v2 块
with_thinking = '*Thinking...*\n\n> **Planning**\n> \n> I should write the file.\n> \n\n\n' + v2_text
calls = parse_tool_calls_from_text(with_thinking)
assert calls and calls[0]['function']['name'] == 'Write'
print('PASS: thinking 前缀 + v2 块')

# 剩余文本剥离
rest = strip_tool_json_block(with_thinking)
assert '<<<' not in rest and 'tool_call' not in rest, repr(rest[:100])
print('PASS: v2 块从正文剥离')

# ============ JSON 兼容回退 ============
legacy = '```json\n{"tool_calls": [{"name": "Read", "arguments": {"file_path": "a.txt"}}]}\n```'
calls = parse_tool_calls_from_text(legacy)
assert calls and calls[0]['function']['name'] == 'Read'
print('PASS: 旧 JSON 格式兼容')

# ============ 历史折叠为 v2 格式 ============
hist = [
    {'role': 'user', 'content': '写个脚本'},
    {'role': 'assistant', 'content': '', 'tool_calls': [
        {'id': 'c1', 'type': 'function', 'function': {'name': 'Write', 'arguments': json.dumps({'file_path': 'x.py', 'content': 'print("hi")\nprint("bye")'})}}
    ]},
    {'role': 'tool', 'tool_call_id': 'c1', 'name': 'Write', 'content': 'ok'},
]
folded = fold_tool_history(hist)
assert '<<<tool_call>>>' in folded[1]['content']
assert 'print("hi")' in folded[1]['content']  # 引号不转义
assert '\\"' not in folded[1]['content']
print('PASS: 历史折叠为 v2 格式')
print()
print(folded[1]['content'])
print()
print('ALL PASS')
