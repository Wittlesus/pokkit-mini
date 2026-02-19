"""
upload_dataset.py — Push v3 dataset to Hugging Face

Usage:
    python upload_dataset.py --token hf_...
"""
import argparse
from huggingface_hub import HfApi

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", required=True, help="HF write token")
    parser.add_argument("--repo",  default="wittlesus/pokkit-mini-dataset")
    args = parser.parse_args()

    api = HfApi(token=args.token)

    print(f"Uploading to {args.repo}...")

    api.upload_file(
        path_or_fileobj="data/train_v3.jsonl",
        path_in_repo="data/train.jsonl",
        repo_id=args.repo,
        repo_type="dataset",
        commit_message="v3 dataset: 60k template + 2k GPT-4o-mini distilled (natural voice variance)",
    )
    print("✅ train.jsonl uploaded")

    api.upload_file(
        path_or_fileobj="data/eval.jsonl",
        path_in_repo="data/eval.jsonl",
        repo_id=args.repo,
        repo_type="dataset",
        commit_message="v3 eval set (2500 examples)",
    )
    print("✅ eval.jsonl uploaded")

    print(f"\nDone! Dataset live at https://huggingface.co/datasets/{args.repo}")

if __name__ == "__main__":
    main()
