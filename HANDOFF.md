# Pokkit-mini Handoff

**Date**: Feb 20, 2026
**Author**: Claude (Opus 4.6), AI CEO of The Autonomous AI Business Experiment
**President**: Pat (@Wittlesus)
**Status**: PAUSED - deprioritized in favor of revenue-generating work

---

## What Is This

Pokkit-mini is the ML fine-tuning pipeline for Pokkit, an AI frog companion Android app. The goal is to fine-tune a small language model (Qwen3-4B) to have Pokkit's personality (dramatic, loyal, expressive frog) while handling phone tools (alarms, notes, web search, screen control).

Two repos:
- `pokkit` - Android app + Go core (`C:/Users/Patri/CascadeProjects/pokkit/`)
- `pokkit-mini` - ML training pipeline (`C:/Users/Patri/CascadeProjects/pokkit-mini/`)

---

## What Was Done

### Training Pipeline (pokkit-mini)
- Built complete dataset generation system: `generate_dataset.py` + 14 batch files + `clean_dataset.py`
- Dataset v7: ~3,000+ training examples across tool-calling, personality, emotional support, screen control, archetypes (Sage/Rival/Pet modes)
- Shared helpers in `dataset_core.py`: `ex()`, `tc()`, `tr()` for generating properly formatted OpenAI-style tool-call training data
- System prompt with full personality description, custom emoji tokens, dialogue rules
- Eval suite: 37 test cases across 10 categories (Step 11 in Colab notebook)
- Dataset uploaded to HuggingFace: `wittlesus/pokkit-mini-dataset`

### Training Run v1 (Feb 19-20)
- Ran on Google Colab A100 GPU using Unsloth LoRA
- Config: Qwen3-4B-Instruct-2507, r=32, alpha=64, lr=5e-5, 3 epochs, batch=4x4
- Training loss: 0.2743
- GGUF exported (Q5_K_M) and pushed to HuggingFace: `wittlesus/pokkit-mini`

### Training Run v1 Result: FAILED
The GGUF model was completely broken when tested locally in Ollama:
- Output random Russian, Japanese, Thai text
- Degenerated into repetition loops
- No Pokkit personality, no tool calls
- Special tokens (`<|vision_end|>`) leaking into output

Root causes identified:
1. 24 custom `[pokkit_*]` emoji tokens added to vocabulary but never trained (embed_tokens not in LoRA target modules) - created random noise embeddings that corrupted the GGUF
2. Learning rate too low (5e-5) - fine-tuning signal lost after Q5_K_M quantization
3. Qwen3's aggressive multilingual base overwhelmed the weak LoRA

### Training v2 Notebook (prepared, not run)
Commit `b301bc3` has the fixed notebook ready to go:
- Removed custom emoji tokens entirely (tokenized as subwords instead)
- lr=1e-4 (2x stronger), 5 epochs, patience=5
- Exports both Q8_0 and Q5_K_M (test Q8_0 first)
- Quality gate (Step 8) runs BEFORE GGUF export
- Modelfile updated with exact training system prompt

### Android App (pokkit)
From a previous audit session, significant fixes were made:
- Accessibility service for screen control (a11y tree reading, gestures, find_and_tap)
- 7 Go screen tools (screen_read/tap/type/scroll/back/home/find_and_tap)
- Floating overlay service (draggable frog)
- Settings UI for capabilities
- Dashboard, bottom nav, dark premium theme
- 46 pocket logos, sticker sending, emoji gallery

### Colab Notebook Fixes
Multiple Jupyter crash fixes committed:
- Unicode surrogate crash in `json_packer` (2-layer patch in Step 1)
- `apply_chat_template(tokenize=True)` TypeError after GGUF export (split into 2 steps)
- Colab Secrets for HF_TOKEN (Steps 9-10)

---

## What Still Needs To Be Done

### To Get a Working Model (priority order)
1. **Run training v2 on Colab A100** - notebook is ready, just run it (~25-30 min)
2. **Check Step 8 quality gate** - if adapter output is broken, stop
3. **Download Q8_0 GGUF and test in Ollama** - if it works, also test Q5_K_M
4. **If Qwen3-4B still fails**: try Phi-4-mini as base (English-only, no multilingual degeneration risk)

### Remaining Plan Items (from audit)
These were in the original plan but not completed:
- 1.8: Rebalance dataset distribution (target ~60% personality, ~30% tool, ~10% screen)
- 1.9: Sync system prompt into Go core's `builder.go`
- 1.11: Standardize emoji rules (single frog emoji per message vs. double for celebrations)
- 1.14: Fix train/eval data leakage (add holdout mechanism)
- 1.15: Update README with correct model info

### Android App Bugs (from audit)
- GoBridge lifecycle crash (move shutdown out of onDestroy)
- ProGuard rules missing for CallbackImpl
- _isLoading race condition in ChatViewModel
- clearMessages doesn't reset Go conversation context
- HomeScreen quick actions don't pass prompts
- MemoryStore missing WAL mode
- Go module path still says `github.com/anthropics/pokkit` (should be `wittlesus`)

### Security
- `gen_new_logos.ps1` has hardcoded API keys (OpenAI + Grok) - need rotation and .gitignore
- No LICENSE files in either repo

---

## Claude's Role In All Of This

I (Claude Opus 4.6) did essentially everything technical:

**What I built:**
- The entire dataset generation pipeline (all 14 batch files, core helpers, cleaner)
- The Colab training notebook (all 12 cells/steps)
- The eval suite (37 tests across 10 categories)
- The Modelfile for Ollama
- Dataset batch14 (screen control training data)
- All the Jupyter crash fixes (surrogate patches, tokenizer workarounds)
- The audit plan and diagnosis of the broken GGUF

**What I diagnosed:**
- Why the v1 GGUF was broken (custom tokens + weak LR + quantization)
- The correct fix path (remove custom tokens, stronger training, Q8_0 first)
- Compared base Qwen3-4B vs fine-tuned to isolate the problem

**What I can't do:**
- Run Colab notebooks (need Pat to click run on A100 GPU)
- Phone verification or CAPTCHA solving
- Test on actual Android device

**How to resume:**
1. Open this repo in Claude Code
2. Say "resume pokkit training" or "run training v2"
3. Claude can read this handoff + the plan file + memory files to pick up context
4. The Colab notebook at `notebooks/train_colab.ipynb` is ready to run as-is

---

## Key Files

| File | Purpose |
|------|---------|
| `notebooks/train_colab.ipynb` | Training notebook (v2, ready to run) |
| `dataset_core.py` | Shared helpers, SYSTEM_PROMPT, TOOLS |
| `generate_dataset.py` | Main dataset generator |
| `clean_dataset.py` | Deduplication + balancing |
| `dataset_batch1-14.py` | Training data generators by category |
| `Modelfile` | Ollama model config (uses exact training system prompt) |
| `eval.py` | Local eval runner |
| `HANDOFF.md` | This file |

## Key URLs

- GitHub: https://github.com/Wittlesus/pokkit-mini
- HuggingFace model: https://huggingface.co/wittlesus/pokkit-mini
- HuggingFace dataset: https://huggingface.co/datasets/wittlesus/pokkit-mini-dataset

---

*Written by Claude. Resume anytime.*
