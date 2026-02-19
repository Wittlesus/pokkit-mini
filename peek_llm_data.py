import json, random
lines = open('data/llm_train.jsonl', encoding='utf-8').readlines()
sample = random.sample(lines, min(10, len(lines)))
for i, l in enumerate(sample):
    ex = json.loads(l)
    prompt = ex["messages"][1]["content"]
    response = ex["messages"][2]["content"]
    print(f"--- Example {i+1} ---")
    print(f"PROMPT:   {prompt}")
    print(f"RESPONSE: {response}")
    print()
