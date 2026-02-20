"""
Export pokkit-mini LoRA adapter to GGUF (for Ollama) and optionally ONNX.

Usage:
    python export.py --lora ./pokkit-mini-lora --output pokkit-mini.gguf
    python export.py --lora ./pokkit-mini-lora --output pokkit-mini.gguf --quant q4_k_m
"""

import argparse
import subprocess
import sys
from pathlib import Path

QUANT_OPTIONS = ["q4_k_m", "q5_k_m", "q8_0", "f16"]

parser = argparse.ArgumentParser()
parser.add_argument("--lora", default="./pokkit-mini-lora", help="Path to saved LoRA adapter")
parser.add_argument("--output", default="pokkit-mini.gguf")
parser.add_argument("--quant", default="q5_k_m", choices=QUANT_OPTIONS,
                    help="GGUF quantization level (q5_k_m recommended — better personality preservation)")
parser.add_argument("--base_model", default="qwen2.5-7b",
                    choices=["qwen2.5-7b", "qwen2.5-3b", "qwen2.5-1.5b", "phi-3.5-mini", "gemma-2-2b"])
args = parser.parse_args()

MODEL_MAP = {
    "qwen2.5-7b":   "unsloth/Qwen2.5-7B-Instruct-bnb-4bit",
    "qwen2.5-3b":   "unsloth/Qwen2.5-3B-Instruct-bnb-4bit",
    "qwen2.5-1.5b": "unsloth/Qwen2.5-1.5B-Instruct-bnb-4bit",
    "phi-3.5-mini": "unsloth/Phi-3.5-mini-instruct-bnb-4bit",
    "gemma-2-2b":   "unsloth/gemma-2-2b-it-bnb-4bit",
}

print(f"\n🐸 Pokkit-mini export")
print(f"   LoRA adapter : {args.lora}")
print(f"   Output       : {args.output}")
print(f"   Quantization : {args.quant}\n")

# ── Step 1: Merge LoRA into base model ────────────────────────────────────

merged_path = Path(args.lora).parent / "pokkit-mini-merged"
print(f"Step 1: Merging LoRA into base model → {merged_path}")

from unsloth import FastLanguageModel

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=args.lora,
    max_seq_length=2048,
    dtype=None,
    load_in_4bit=True,
)

model.save_pretrained_merged(str(merged_path), tokenizer, save_method="merged_16bit")
print(f"   ✅ Merged model saved to {merged_path}")

# ── Step 2: Convert to GGUF ───────────────────────────────────────────────

print(f"\nStep 2: Converting to GGUF ({args.quant})...")

# Use unsloth's built-in GGUF export
model.save_pretrained_gguf(
    str(Path(args.output).stem),
    tokenizer,
    quantization_method=args.quant,
)

print(f"   ✅ GGUF saved: {args.output}")

# ── Step 3: Instructions ──────────────────────────────────────────────────

print(f"""
✅ Export complete!

Next steps:
1. Copy {args.output} to your Ollama models directory or use the Modelfile:

   ollama create pokkit-mini -f Modelfile

2. Test it:
   ollama run pokkit-mini "Set an alarm for 7am tomorrow"

3. In the Pokkit app:
   Settings → Provider → Ollama → Model → pokkit-mini

File sizes (approximate):
  q4_k_m : ~1.8GB  ← recommended, best quality/size tradeoff
  q5_k_m : ~2.1GB  ← slightly better quality
  q8_0   : ~3.2GB  ← near-lossless
  f16    : ~6.0GB  ← full precision
""")
