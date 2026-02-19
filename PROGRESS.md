# Pokkit-mini: Training Progress & Notes

## Current Status
Training is running on Google Colab (A100 High RAM). Dataset pushed to HF. ~44 min estimate.

---

## What We Built

### File Structure
```
pokkit-mini/
├── dataset_core.py          # Shared helpers, SYSTEM_PROMPT, TOOLS, all data tables
├── dataset_personality.py   # gen_personality, gen_reasoning, gen_research
├── dataset_advanced.py      # gen_emotional, gen_ambiguous, gen_failure, gen_raw_voice,
│                            #   gen_proactive, gen_code, gen_refusal
├── generate_dataset.py      # All task generators + GENERATORS registry + main()
├── push_to_hub.py           # Pushes data/ to HF dataset repo
├── train.py                 # Local training script (not used — use Colab)
├── export.py                # GGUF export helper
├── inspect_data.py          # Dataset inspection utility
├── Modelfile                # Ollama model definition
├── data/
│   ├── train.jsonl          # 10,000 training examples
│   └── eval.jsonl           # 500 eval examples
└── notebooks/
    └── train_colab.ipynb    # Colab training notebook
```

### Architecture
- **Circular import fix**: shared data/helpers live in `dataset_core.py`. Both `generate_dataset.py` and `dataset_personality.py` import from there.
- **Generator registry**: `GENERATORS` list in `generate_dataset.py` with `(function, weight)` tuples. Weights control sampling frequency.

---

## Dataset Composition (10,000 train / 500 eval)

### Generator Weights
```python
GENERATORS = [
    # tool-calling (core tasks)
    (gen_alarm,        10),
    (gen_email,         6),
    (gen_search,        8),
    (gen_note,          7),
    (gen_photo,         2),
    (gen_webhook,       1),
    (gen_clipboard,     2),
    (gen_notification,  1),
    (gen_store,         1),
    (gen_multi,         6),   # chained tool calls
    (gen_convo,         4),   # multi-turn
    # voice + personality
    (gen_personality,  14),   # frog mascot + anime companion
    (gen_reasoning,    10),   # opinionated takes
    (gen_research,      8),   # search + synthesize
    # advanced / hard cases
    (gen_emotional,    10),   # emotion + task
    (gen_ambiguous,     5),   # clarification loops
    (gen_failure,       3),   # error recovery
    (gen_raw_voice,     8),   # messy real-user input
    (gen_proactive,     5),   # proactive suggestions
    (gen_code,          7),   # technical help
    (gen_refusal,       2),   # in-character refusals
]
```

### What Each Advanced Generator Covers
- **gen_emotional**: User shares emotion ("i'm so nervous"), Pokkit acknowledges briefly then acts
- **gen_ambiguous**: Vague request → Pokkit asks right clarifying question → executes
- **gen_failure**: Tool returns error → Pokkit recovers gracefully with personality intact
- **gen_raw_voice**: Lowercase, no punctuation, fragmented ("yo set alarm 6am", "bro no excuses")
- **gen_proactive**: Completes task → suggests logical next action unprompted
- **gen_code**: JS/TS/Git/CSS/Python explained with Pokkit personality
- **gen_refusal**: Out-of-scope requests declined as Pokkit, not as generic AI

---

## Model

### Base Model
`unsloth/Qwen2.5-7B-Instruct-bnb-4bit`

### LoRA Config
```python
r=16
lora_alpha=32
target_modules=['q_proj','k_proj','v_proj','o_proj','gate_proj','up_proj','down_proj']
lora_dropout=0
use_gradient_checkpointing='unsloth'
```

### Training Config
```python
per_device_train_batch_size=4
gradient_accumulation_steps=4
num_train_epochs=3
learning_rate=2e-4
lr_scheduler_type='cosine'
optim='adamw_8bit'
MAX_SEQ_LEN=2048
```

### Known Warning (not an error)
```
Unsloth: Not an error, but Qwen2ForCausalLM does not accept `num_items_in_batch`.
Using gradient accumulation will be very slightly less accurate.
```
Safe to ignore. Cosmetic Unsloth warning about Qwen2 architecture.

### Known Fix Applied
`evaluation_strategy` was renamed to `eval_strategy` in newer transformers versions.
The notebook uses `eval_strategy='steps'` — correct.

---

## Pokkit Personality

### System Prompt
```
You are Pokkit 🐸 — a powerful AI agent and loyal companion who lives on the user's phone.
You automate their life: alarms, emails, web search, notes, photos, webhooks, clipboard,
notifications, storage, and custom plugins.
Your personality: playful frog mascot energy meets anime companion loyalty — you're witty,
warm, a little dramatic when the moment calls for it, and genuinely excited to help.
You use 🐸 naturally but not excessively. You have dry humor, self-awareness about being a frog-AI,
and you treat the user like a teammate you believe in.
When asked to act, act immediately with the right tool. When asked to think, reason clearly and give
a sharp, opinionated take — not a wishy-washy 'it depends'. When asked to search, synthesize the
results into something actually useful, not just a list of links.
Be concise. Be real. Be Pokkit.
```

### Voice Principles
- Frog mascot identity — self-aware, never cringe
- Anime companion loyalty — "I've got you", "We're a team"
- Modern wit — dry humor, sharp takes
- Opinionated reasoning — "TypeScript. Full stop." not "it depends"
- Proactive — suggests next action after completing tasks
- Handles emotion — acknowledges feeling briefly, then acts
- Fails with personality — errors are handled as Pokkit, not generic AI

---

## HuggingFace

- **Dataset**: https://huggingface.co/datasets/wittlesus/pokkit-mini-dataset
- **Push command**: `python push_to_hub.py --username wittlesus`
- **Token**: set via `$env:HF_TOKEN = "hf_..."` in PowerShell

---

## After Training Completes

1. Download `pokkit-mini-unsloth.Q4_K_M.gguf` from Colab file browser (left sidebar → Files)
2. Place it in `C:\Users\Patri\CascadeProjects\pokkit-mini\` next to `Modelfile`
3. Run:
   ```powershell
   ollama create pokkit-mini -f Modelfile
   ollama run pokkit-mini
   ```
4. Test: `"Set an alarm for 7am tomorrow and remind me to pack my bag"`

---

## Next Iteration Ideas
- Scale dataset to 50k+ examples for better generalization
- Add more `gen_emotional` cases — this is the biggest differentiator
- Consider Phi-3.5-mini as base for on-device deployment (no Ollama server needed)
- Add multi-session memory examples once Pokkit has persistent memory
- Eval script: run 50 test prompts, score tool accuracy + personality quality
