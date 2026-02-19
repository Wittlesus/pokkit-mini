"""Quick spot-check of the updated voice prompt — runs 15 test prompts and prints results."""
import os
from openai import OpenAI
from generate_with_llm import GENERATION_SYSTEM_PROMPT

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

TEST_PROMPTS = [
    "pineapple on pizza",
    "do you remember our conversations",
    "what do you actually want",
    "i'm such an idiot",
    "i got the job!!",
    "i feel like i'm failing at everything",
    "do you have feelings",
    "can frogs even use phones",
    "i hate mondays",
    "i'm so stressed i can't think straight",
    "you're the best",
    "i stood up for myself today",
    "what's it like being a frog ai",
    "i don't want to talk about it",
    "how do i stop overthinking",
]

for prompt in TEST_PROMPTS:
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": GENERATION_SYSTEM_PROMPT},
            {"role": "user",   "content": prompt},
        ],
        temperature=0.9,
        max_tokens=150,
    )
    print(f"USER: {prompt}")
    print(f"POKKIT: {resp.choices[0].message.content.strip()}")
    print()
