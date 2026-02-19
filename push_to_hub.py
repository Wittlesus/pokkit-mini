"""
Push pokkit-mini training dataset to Hugging Face Hub.

Usage:
    Set HF_TOKEN env var first, then:
    python push_to_hub.py --username your-hf-username
"""

import argparse
import os
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--username", required=True, help="Your Hugging Face username")
parser.add_argument("--repo", default="pokkit-mini-dataset", help="Dataset repo name")
args = parser.parse_args()

token = os.environ.get("HF_TOKEN")
if not token:
    print("ERROR: Set HF_TOKEN environment variable first.")
    print("  PowerShell: $env:HF_TOKEN = 'hf_...'")
    exit(1)

repo_id = f"{args.username}/{args.repo}"
print(f"\n🐸 Pushing pokkit-mini dataset to {repo_id}")

try:
    from huggingface_hub import HfApi, create_repo
except ImportError:
    print("Installing huggingface_hub...")
    import subprocess
    subprocess.check_call(["pip", "install", "huggingface_hub", "-q"])
    from huggingface_hub import HfApi, create_repo

api = HfApi(token=token)

# Create repo if it doesn't exist
try:
    create_repo(repo_id, repo_type="dataset", token=token, exist_ok=True)
    print(f"  ✅ Repo ready: https://huggingface.co/datasets/{repo_id}")
except Exception as e:
    print(f"  Repo note: {e}")

# Upload files
files = [
    ("data/train.jsonl", "data/train.jsonl"),
    ("data/eval.jsonl",  "data/eval.jsonl"),
    ("README.md",        "README.md"),
    ("generate_dataset.py", "generate_dataset.py"),
]

for local, remote in files:
    if Path(local).exists():
        api.upload_file(
            path_or_fileobj=local,
            path_in_repo=remote,
            repo_id=repo_id,
            repo_type="dataset",
            token=token,
        )
        print(f"  ✅ Uploaded {local}")
    else:
        print(f"  ⚠️  Skipped {local} (not found)")

print(f"\n✅ Done! Dataset live at:")
print(f"   https://huggingface.co/datasets/{repo_id}")
print(f"\nIn train_colab.ipynb, load it with:")
print(f'   from datasets import load_dataset')
print(f'   ds = load_dataset("{repo_id}")')
