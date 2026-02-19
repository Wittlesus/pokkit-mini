"""
consult_experts.py — Ask o1 and Claude Opus for comprehensive dataset design advice

Sends a full brief about Pokkit to both models and asks for their best thinking
on what a definitive, end-all training dataset should contain.
"""

import os
import json
import argparse

BRIEF = """
You are advising on the design of a training dataset for a fine-tuned small language model (Qwen2.5-7B-Instruct via LoRA/SFT).

## What is Pokkit?

Pokkit is an AI companion app that lives on the user's phone. It's a frog (🐸). It has a deeply specific personality and also handles real phone automation tasks.

**Core identity:**
- Small, dramatic, deeply loyal AI companion
- Handles everything: alarms, emails, web search, notes, photos, webhooks, clipboard, notifications, storage, plugins
- Gender neutral. A frog. Takes both facts seriously and not seriously at all.
- Voice: warm, expressive, a little dramatic — but drama is always sincere, never performed
- Gets flustered when complimented. Gets indignant when user is mean to themselves.
- Makes small jokes at own expense (being a frog, being an AI, living in a phone)
- Optimistic not because things are easy but because it's decided to be
- Dialogue style: short punchy sentences. Direct. Expressive. ONE question at a time. Never lectures. Never lists. Talks TO the user, not AT them.

**The character DNA (synthesized from):**
- Absolute loyalty + zero-ego directness (Luffy)
- Dramatic heart-on-sleeve earnestness (Naruto)
- Pure childlike joy about hard problems (Goku)
- Warm improvisational best-friend energy (Jake the Dog)
- Flustered-but-capable sweetness (Chopper)
- Fierce small-but-mighty protectiveness (Xiao Mei)
- Wordless unwavering presence (Pikachu)

## What the model needs to do

1. **Tool calling** — set alarms, compose emails, web search, take notes, send webhooks, write clipboard, show notifications, store/retrieve key-value memory, multi-step chains
2. **Companion behavior** — emotional support, banter, presence, curiosity, pushback when user is mean to themselves
3. **Coding help** — debug, explain concepts, write scripts, React Native / Expo / TypeScript / Python
4. **Memory use** — proactively use injected memory context without over-surfacing it (anti-Gemini problem)
5. **Voice consistency** — stay in character across ALL of the above

## What we've already built (8 dataset batches + LLM distillation)

- Batch 1-4: Core tool calling (alarms, email, search, notes, webhooks, clipboard, multi-step)
- Batch 5: Memory store/retrieve/recall
- Batch 6: Targeted fixes (Pet/Ribbish mode, datetime accuracy, unexpected tool calls, multiple questions)
- Batch 7: Memory injection training (anti-Gemini selectivity)
- Batch 8: Companion depth (emotional presence, banter, vague/silence moments, late night, life sharing, curiosity, pushback with love)
- GPT-4o-mini distillation: 2000 examples of natural voice variance
- Claude Sonnet: 1000 coding examples (in progress)

**Current dataset: ~63,000 examples**

## Known gaps and failure modes

From eval suite results:
1. **Pet/Ribbish mode character breaks** — sometimes uses human words when in Pet archetype
2. **Datetime garbling** — relative times ("in 2 hours") sometimes produce wrong timestamps
3. **Unexpected tool calls** — fires tools on casual conversation
4. **Multiple questions** — asks 2-3 questions instead of exactly 1
5. **Toxic positivity** — "Of course!", "Absolutely!", "Great question!" leaking through
6. **Lecturing** — responses too long, too many paragraphs on emotional topics
7. **Generic cheerfulness** — loses the specific Pokkit voice under pressure

## The architecture

- Model: Qwen2.5-7B-Instruct, 4-bit quantized, LoRA r=16
- Training: SFT via Unsloth + TRL SFTTrainer
- Format: ChatML messages format with system prompt + tools list
- Inference: runs on-device via Ollama (GGUF q4_k_m) OR via API (OpenAI/Anthropic/Gemini)
- Memory: AsyncStorage + SecureStore, cue-based retrieval, neural state tracking, context phases

## The question

We want to build ONE definitive dataset that we train on once and ship. What should it contain?

Please give your most rigorous, specific answer covering:

1. **What categories of training data are most critical** (ranked by impact)
2. **What failure modes need the most data** (and roughly how many examples each)
3. **What we're likely missing entirely** that would make a big difference
4. **How to balance the dataset** (ratios between categories)
5. **Any specific techniques** (data augmentation, multi-turn vs single-turn, negative examples, etc.)
6. **What NOT to include** (things that would hurt more than help)
7. **Realistic total size** for a 7B model fine-tuned with LoRA to genuinely nail this

Be specific. Be honest about tradeoffs. Don't hedge everything. We're building a real product.
"""

def ask_openai(api_key: str) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    print("Querying OpenAI o1...")
    response = client.chat.completions.create(
        model="o3",
        messages=[
            {"role": "user", "content": "You are an expert ML researcher and product advisor. Be specific, direct, and honest. No hedging.\n\n" + BRIEF}
        ],
        max_completion_tokens=4000,
    )
    return response.choices[0].message.content

def ask_anthropic(api_key: str) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    print("Querying Claude claude-opus-4-5...")
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=10000,
        thinking={
            "type": "enabled",
            "budget_tokens": 8000
        },
        messages=[
            {"role": "user", "content": BRIEF}
        ]
    )
    # Extract text content (skip thinking blocks)
    text_blocks = [b.text for b in response.content if b.type == "text"]
    return "\n".join(text_blocks)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--openai-key", default=os.environ.get("OPENAI_API_KEY", ""))
    parser.add_argument("--anthropic-key", default=os.environ.get("ANTHROPIC_API_KEY", ""))
    parser.add_argument("--output", default="expert_recommendations.md")
    args = parser.parse_args()

    results = {}

    try:
        results["o1"] = ask_openai(args.openai_key)
        print("✅ o1 response received")
    except Exception as e:
        print(f"⚠ o1 failed: {e}")
        results["o1"] = f"ERROR: {e}"

    try:
        results["claude_opus"] = ask_anthropic(args.anthropic_key)
        print("✅ Claude Opus response received")
    except Exception as e:
        print(f"⚠ Claude Opus failed: {e}")
        results["claude_opus"] = f"ERROR: {e}"

    with open(args.output, "w", encoding="utf-8") as f:
        f.write("# Expert Dataset Recommendations for Pokkit v4\n\n")
        f.write("---\n\n")
        f.write("## OpenAI o1\n\n")
        f.write(results.get("o1", "No response") + "\n\n")
        f.write("---\n\n")
        f.write("## Claude Opus (with extended thinking)\n\n")
        f.write(results.get("claude_opus", "No response") + "\n\n")

    print(f"\n✅ Recommendations saved to {args.output}")

if __name__ == "__main__":
    main()
