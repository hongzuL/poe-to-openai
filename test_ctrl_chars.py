import sys, json
sys.path.insert(0, '.')
from api.poe_api import parse_tool_calls_from_text, _repair_json

# 构造与用户截图一致的真实失败样本：arguments.command 含原始换行（非法 JSON）
cmd = 'python3 -c "\nimport json\nwith open(\'models.json\', \'r\') as f:\n    data = json.load(f)\nprint(list(data.keys()))\n"'
# 手工拼出"非法 JSON"文本（字符串内含真实换行）
raw_text = '```json\n{"tool_calls": [{"name": "Bash", "arguments": {"command": "' + cmd.replace('\\', '\\\\').replace('"', '\\"') + '", "description": "Inspect structure of models.json"}}]}\n```'
# 注意：上面的 replace 只转义了引号和反斜杠，换行保持原始 -> 非法 JSON
with open('/tmp/sample.txt', 'w') as f:
    f.write(raw_text)

print('--- 样本前 200 字符 ---')
print(repr(raw_text[:200]))

calls = parse_tool_calls_from_text(raw_text)
assert calls, f'FAIL: 未解析出工具调用'
assert calls[0]['function']['name'] == 'Bash', calls
args = json.loads(calls[0]['function']['arguments'])
assert 'import json' in args['command'], args
assert args['description'] == 'Inspect structure of models.json'
print('PASS: 含原始换行的非法 JSON 被修复并正确解析')

# 合法 JSON 不受影响
good = '{"tool_calls": [{"name": "read_file", "arguments": {"path": "a.txt"}}]}'
assert _repair_json(good)['tool_calls'][0]['name'] == 'read_file'
print('PASS: 合法 JSON 不受影响')

# 已转义的 \n 不重复转义
escaped = '{"a": "line1\\nline2"}'
r2 = _repair_json(escaped)
assert r2['a'] == 'line1\nline2', repr(r2)
print('PASS: 已转义换行不重复转义')

# 纯文本不产生工具调用
assert parse_tool_calls_from_text('只是普通回答') is None
print('PASS: 纯文本不误报')

print('ALL PASS')
