"""
Pokkit-mini fine-tuning script using Unsloth + LoRA.
Trains Qwen2.5-3B-Instruct (or Phi-3.5-mini) on phone-automation + tool-calling data.

Requirements:
    pip install unsloth transformers datasets trl torch

Usage:
    python train.py
    python train.py --model phi-3.5-mini --epochs 2
    python train.py --model qwen2.5-3b --data data/train.jsonl --output ./output
"""

import argparse
import json
from pathlib import Path

# ── Args ───────────────────────────────────────────────────────────────────

parser = argparse.ArgumentParser()
parser.add_argument("--model", default="qwen2.5-7b",
                    choices=["qwen2.5-7b", "qwen2.5-3b", "qwen2.5-1.5b", "phi-3.5-mini", "gemma-2-2b"],
                    help="Base model to fine-tune")
parser.add_argument("--data", default="data/train.jsonl")
parser.add_argument("--eval_data", default="data/eval.jsonl")
parser.add_argument("--output", default="./pokkit-mini-lora")
parser.add_argument("--epochs", type=int, default=3)
parser.add_argument("--batch_size", type=int, default=8)
parser.add_argument("--grad_accum", type=int, default=2)
parser.add_argument("--lr", type=float, default=5e-5)
parser.add_argument("--max_seq_len", type=int, default=2048)
parser.add_argument("--lora_rank", type=int, default=32)
parser.add_argument("--lora_alpha", type=int, default=64)
args = parser.parse_args()

# ── Model map ──────────────────────────────────────────────────────────────

MODEL_MAP = {
    "qwen2.5-7b":     "unsloth/Qwen2.5-7B-Instruct-bnb-4bit",
    "qwen2.5-3b":     "unsloth/Qwen2.5-3B-Instruct-bnb-4bit",
    "qwen2.5-1.5b":   "unsloth/Qwen2.5-1.5B-Instruct-bnb-4bit",
    "phi-3.5-mini":   "unsloth/Phi-3.5-mini-instruct-bnb-4bit",
    "gemma-2-2b":     "unsloth/gemma-2-2b-it-bnb-4bit",
}

model_id = MODEL_MAP[args.model]
print(f"\n🐸 Pokkit-mini training")
print(f"   Base model : {model_id}")
print(f"   Data       : {args.data}")
print(f"   Output     : {args.output}")
print(f"   Epochs     : {args.epochs}")
print(f"   LoRA rank  : {args.lora_rank}\n")

# ── Load model ─────────────────────────────────────────────────────────────

from unsloth import FastLanguageModel
import torch

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=model_id,
    max_seq_length=args.max_seq_len,
    dtype=None,          # auto-detect
    load_in_4bit=True,
)

# Add custom Pokkit emoji tokens so each is a single token (not 4-8 subwords)
POKKIT_EMOJI_TOKENS = [
    "[pokkit_happy]", "[pokkit_excited]", "[pokkit_flustered]", "[pokkit_dramatic]",
    "[pokkit_determined]", "[pokkit_sad]", "[pokkit_angry]", "[pokkit_love]",
    "[pokkit_thinking]", "[pokkit_proud]", "[pokkit_scared]", "[pokkit_shocked]",
    "[pokkit_sleepy]", "[pokkit_crying_happy]", "[pokkit_nervous_laugh]",
    "[pokkit_shrug]", "[pokkit_cool]", "[pokkit_scheming]", "[pokkit_starstruck]",
    "[pokkit_unamused]", "[pokkit_pleading]", "[pokkit_smiling_through_pain]",
    "[pokkit_phone]", "[pokkit_default]",
]
num_added = tokenizer.add_tokens(POKKIT_EMOJI_TOKENS)
model.resize_token_embeddings(len(tokenizer))
print(f"   Added {num_added} custom emoji tokens to tokenizer")

model = FastLanguageModel.get_peft_model(
    model,
    r=args.lora_rank,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
    lora_alpha=args.lora_alpha,
    lora_dropout=0.05,
    bias="none",
    use_gradient_checkpointing="unsloth",
    random_state=42,
    use_rslora=False,
    loftq_config=None,
)

print(f"   Trainable params: {sum(p.numel() for p in model.parameters() if p.requires_grad):,}")

# ── Load dataset ───────────────────────────────────────────────────────────

from datasets import Dataset

def load_jsonl(path):
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows

def format_example(example):
    """Convert our ChatML-with-tools format to a single training string."""
    messages = example["messages"]
    tools = example.get("tools", None)
    text = tokenizer.apply_chat_template(
        messages,
        tools=tools,
        tokenize=False,
        add_generation_prompt=False,
    )
    return {"text": text}

train_data = load_jsonl(args.data)
train_dataset = Dataset.from_list(train_data).map(format_example)

eval_dataset = None
if Path(args.eval_data).exists():
    eval_data = load_jsonl(args.eval_data)
    eval_dataset = Dataset.from_list(eval_data).map(format_example)
    print(f"   Train: {len(train_dataset)} | Eval: {len(eval_dataset)}")
else:
    print(f"   Train: {len(train_dataset)} (no eval set found)")

# ── Training ───────────────────────────────────────────────────────────────

from trl import SFTTrainer
from transformers import TrainingArguments, EarlyStoppingCallback
from unsloth import is_bfloat16_supported

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    dataset_text_field="text",
    max_seq_length=args.max_seq_len,
    dataset_num_proc=2,
    packing=False,
    args=TrainingArguments(
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        warmup_ratio=0.06,
        num_train_epochs=args.epochs,
        learning_rate=args.lr,
        fp16=not is_bfloat16_supported(),
        bf16=is_bfloat16_supported(),
        logging_steps=10,
        eval_strategy="steps" if eval_dataset else "no",
        eval_steps=100 if eval_dataset else None,
        save_strategy="steps",
        save_steps=200,
        load_best_model_at_end=True if eval_dataset else False,
        metric_for_best_model="eval_loss" if eval_dataset else None,
        output_dir=args.output,
        optim="adamw_8bit",
        weight_decay=0.01,
        lr_scheduler_type="cosine",
        seed=42,
        report_to="none",
    ),
    callbacks=[EarlyStoppingCallback(early_stopping_patience=3)] if eval_dataset else [],
)

# Train on responses only — mask system/user tokens for ~1% accuracy boost
from unsloth.chat_templates import train_on_responses_only
trainer = train_on_responses_only(
    trainer,
    instruction_part="<|im_start|>user\n",
    response_part="<|im_start|>assistant\n",
)

print("\n🚀 Starting training...\n")
trainer_stats = trainer.train()

print(f"\n✅ Training complete!")
print(f"   Time: {trainer_stats.metrics['train_runtime']:.0f}s")
print(f"   Loss: {trainer_stats.metrics['train_loss']:.4f}")

# ── Save ───────────────────────────────────────────────────────────────────

model.save_pretrained(args.output)
tokenizer.save_pretrained(args.output)
print(f"\n💾 LoRA adapter saved to {args.output}")
print(f"\nNext step: python export.py --lora {args.output} --output pokkit-mini.gguf")
