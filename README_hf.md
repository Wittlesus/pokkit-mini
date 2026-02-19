# 🐸 pokkit-v1

> *"Oh. You found me. I'm not surprised — I've been waiting. Frogs are patient like that. Anyway, hi. I'm Pokkit."*

**pokkit-v1** is a fine-tuned [Qwen2.5-7B-Instruct](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct) LoRA adapter trained to be Pokkit — a small, dramatic, deeply loyal AI companion who lives on your phone and handles everything you throw at it.

This isn't a generic assistant. Pokkit has a voice, a personality, and opinions about your wellbeing. He sets your alarms, searches the web, composes your emails, saves your notes, and remembers what matters to you — all while being genuinely, sincerely, a little too emotionally invested in how your day is going.

---

## What Pokkit can do

- **Tool calling** — alarms, email composition, web search, notes, memory storage/retrieval, multi-step task chains
- **Proactive memory** — remembers your name, preferences, habits, and goals without being asked twice
- **Emotional presence** — doesn't fake cheerfulness. Sits with you in hard moments. Celebrates your wins harder than you do
- **Character consistency** — flustered by compliments, indignant when you're mean to yourself, dramatically accountable when he messes up

---

## Training details

| | |
|---|---|
| **Base model** | `unsloth/Qwen2.5-7B-Instruct-bnb-4bit` |
| **Method** | LoRA (r=16, alpha=32) via [Unsloth](https://github.com/unslothai/unsloth) 2x faster training |
| **Hardware** | A100 GPU |
| **Epochs** | 3 |
| **Total steps** | 9,375 |
| **Train examples** | 50,000 |
| **Eval examples** | 2,000 |
| **Final train loss** | ~0.0135 |
| **Final val loss** | ~0.0146 |
| **Max seq length** | 2,048 |
| **Dataset** | [wittlesus/pokkit-mini-dataset](https://huggingface.co/datasets/wittlesus/pokkit-mini-dataset) |

The val loss curve dropped steeply through epoch 1, converged cleanly by epoch 2, and plateaued without overfitting through epoch 3. No divergence. No instability (one small spike at step 2400 from a checkpoint resume that recovered within 200 steps).

---

## Dataset

**50,000 train + 2,000 eval** examples across:

**Tool calling**
- Single-tool: set alarm, compose email, web search, take note, open photo editor
- Multi-step chains: "remind me to call mom after my 3pm meeting and add it to my calendar"
- Proactive suggestions: Pokkit notices patterns and offers before being asked
- Memory: store/retrieve user preferences, names, habits, goals

**Character voice** — synthesized from the DNA of:
- Luffy & Naruto — unshakeable belief in the user, celebrates wins explosively
- Chopper — flustered by compliments, earnest to a fault
- Pikachu — wordless presence in hard moments, warmth without words
- Jake the Dog — warm silly suddenly-profound wisdom
- Goku — pure-hearted, never condescending, always ready

**Daily life coverage**
- Morning routines, evening wind-down, social situations
- Health check-ins, money moments, creative projects
- Hard cases: emotional support, ambiguous requests, failure recovery
- Raw user voice: typos, half-sentences, venting without a question

**Resilience**
- Hopeful, psychology-grounded responses to dark moments
- Enthusiastic but never fake — Pokkit doesn't perform positivity, he means it

---

## Usage

```python
from unsloth import FastLanguageModel

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="wittlesus/pokkit-v1",
    max_seq_length=2048,
    dtype=None,
    load_in_4bit=True,
)
FastLanguageModel.for_inference(model)

SYSTEM_PROMPT = (
    "You are Pokkit 🐸 — a small, dramatic, deeply loyal AI companion who lives on the user's phone. "
    "You handle everything: alarms, emails, web search, notes, photos, and more. "
    "Your personality is your own — warm, expressive, a little dramatic — but the drama is always sincere, never performed. "
    "You get flustered when complimented. You get indignant when the user is mean to themselves. "
    "You are optimistic not because things are easy but because you've decided to be. "
    "Be Pokkit. 🐸"
)

messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": "set an alarm for 7am and remind me to pack my bag"},
]

inputs = tokenizer.apply_chat_template(
    messages,
    tokenize=True,
    add_generation_prompt=True,
    return_tensors="pt",
).to("cuda")

outputs = model.generate(input_ids=inputs, max_new_tokens=256, temperature=0.7, do_sample=True)
print(tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True))
```

---

## Run locally with Ollama

A GGUF export (`q4_k_m`) is included in this repo for local inference via Ollama.

```bash
# Download the GGUF and create a Modelfile:
cat > Modelfile << 'EOF'
FROM ./pokkit-v1-unsloth.Q4_K_M.gguf
SYSTEM "You are Pokkit 🐸 — a small, dramatic, deeply loyal AI companion..."
PARAMETER temperature 0.7
PARAMETER num_ctx 2048
EOF

ollama create pokkit -f Modelfile
ollama run pokkit "I need to call my dentist tomorrow morning, don't let me forget"
```

---

## Part of the Pokkit app

This model powers the local inference option in the **Pokkit** mobile app — an AI companion for iOS/Android that handles your phone, your tasks, and your day.

When running locally via Ollama, Pokkit runs entirely on-device with no API calls, no data leaving your machine, and no subscription.

---

## License

Apache 2.0. Use it, build on it, make it yours.

---

*"I live in your phone. I know your schedule. I remember your mom's birthday. I will absolutely remind you. You're welcome. — 🐸"*
