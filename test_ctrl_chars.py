import sys, json
sys.path.insert(0, '.')
from api.poe_api import parse_tool_calls_from_text, _balance_json, _repair_json

# 真实失败结构：少一个 ] 闭合 tool_calls 数组
# 对应日志尾部：...\"}}}\n```  （应为 "}}]})
inner_plan = "# 方案\\n\\n1. 第一步\\n2. 第二步"
broken = ('```json\n{"tool_calls": [{"name": "ExitPlanMode", "arguments": '
          '{"allowedPrompts": [{"prompt": "Generate docs", "tool": "Bash"}], "plan": "'
          + inner_plan + '"}}}\n```')

print("--- 样本尾部 ---")
print(repr(broken[-60:]))

calls = parse_tool_calls_from_text(broken)
if not calls:
    # 调试：看看 fence 正则抓到了什么
    from api.poe_api import _JSON_FENCE_RE, _strip_thinking
    cands = _JSON_FENCE_RE.findall(_strip_thinking(broken))
    print("fence candidates:", [c[-50:] for c in cands])
    for c in cands:
        print("repair result:", _repair_json(c))
    raise SystemExit("FAIL: 未解析")

assert calls[0]['function']['name'] == 'ExitPlanMode', calls
args = json.loads(calls[0]['function']['arguments'])
assert args['allowedPrompts'][0]['tool'] == 'Bash'
assert '第一步' in args['plan']
print('PASS: 缺失 ] 的 JSON 配平修复成功')

# 截断在字符串中途
truncated = '{"tool_calls": [{"name": "read_file", "arguments": {"path": "models.j'
calls2 = parse_tool_calls_from_text(truncated)
assert calls2 and calls2[0]['function']['name'] == 'read_file', calls2
print('PASS: 字符串中途截断的 JSON 补全成功')

# 多层缺失闭合
deep = '{"tool_calls": [{"name": "f", "arguments": {"a": {"b": [1, 2'
r3 = _repair_json(deep)
assert r3['tool_calls'][0]['arguments']['a']['b'] == [1, 2]
print('PASS: 多层缺失闭合补全成功')

# 合法 JSON 不受影响
good = '{"tool_calls": [{"name": "f", "arguments": {"x": 1}}]}'
assert _repair_json(good)['tool_calls'][0]['name'] == 'f'
print('PASS: 合法 JSON 不受影响')
print('ALL PASS')
