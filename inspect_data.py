import json, collections

with open('data/train.jsonl') as f:
    rows = [json.loads(l) for l in f]

tool_calls = collections.Counter()
for r in rows:
    for m in r['messages']:
        if m.get('tool_calls'):
            tool_calls[m['tool_calls'][0]['name']] += 1

print('Total examples:', len(rows))
avg = sum(len(r['messages']) for r in rows) / len(rows)
print('Avg messages per example:', round(avg, 1))
print()
print('Tool call distribution:')
for name, count in sorted(tool_calls.items(), key=lambda x: -x[1]):
    bar = '#' * (count // 10)
    print(f'  {name:<25} {count:4d}  {bar}')

print()
print('=== Example 5 (single-turn) ===')
for m in rows[5]['messages']:
    role = m['role']
    if m.get('tool_calls'):
        tc = m['tool_calls'][0]
        args = json.dumps(tc['arguments'])[:90]
        print(f'  [{role}] CALL {tc["name"]}  args={args}')
    elif role != 'system':
        print(f'  [{role}] {str(m.get("content") or "")[:100]}')

print()
print('=== Example 42 ===')
for m in rows[42]['messages']:
    role = m['role']
    if m.get('tool_calls'):
        tc = m['tool_calls'][0]
        args = json.dumps(tc['arguments'])[:90]
        print(f'  [{role}] CALL {tc["name"]}  args={args}')
    elif role != 'system':
        print(f'  [{role}] {str(m.get("content") or "")[:100]}')

print()
print('=== First multi-step example ===')
multi = next((r for r in rows if len(r['messages']) > 8), None)
if multi:
    for m in multi['messages']:
        role = m['role']
        if m.get('tool_calls'):
            tc = m['tool_calls'][0]
            print(f'  [{role}] CALL {tc["name"]}')
        elif role != 'system':
            print(f'  [{role}] {str(m.get("content") or "")[:100]}')

print()
print('=== Eval set ===')
with open('data/eval.jsonl') as f:
    eval_rows = [json.loads(l) for l in f]
print('Eval examples:', len(eval_rows))
