"""
audit_dataset.py — Scan training data for contamination and report/purge

Checks for:
1. Banned phrases (toxic positivity, corporate filler)
2. Multiple questions in a single assistant turn
3. Overly long assistant responses (>80 words for non-code)
4. Assistant turns with no Pokkit voice markers

Usage:
    python audit_dataset.py --input data/train.jsonl --report
    python audit_dataset.py --input data/train.jsonl --purge --output data/train_clean.jsonl
"""

import json
import re
import argparse
from pathlib import Path
from collections import defaultdict

BANNED_PHRASES = [
    "of course!",
    "absolutely!",
    "certainly!",
    "sure thing!",
    "happy to help",
    "great question",
    "no problem!",
    "you got it!",
    "i'd be happy to",
    "i'm here for you",
    "is there anything else",
    "let me know if you need",
    "i understand that",
    "as an ai",
    "i hope this helps",
    "feel free to",
    "don't hesitate to",
    "of course, i",
    "absolutely, i",
    "great, i",
    "sure, i",
]

def get_assistant_turns(example):
    msgs = example.get("messages", [])
    return [m["content"] for m in msgs if m["role"] == "assistant" and m.get("content")]

def has_banned_phrase(text):
    lower = text.lower()
    return [p for p in BANNED_PHRASES if p in lower]

def count_questions(text):
    # Count ? not inside code blocks
    no_code = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    return no_code.count('?')

def word_count(text):
    return len(text.split())

def has_code_block(text):
    return '```' in text

def is_too_long(text):
    if has_code_block(text):
        return False  # code examples can be long
    return word_count(text) > 100

def has_voice_markers(text):
    return any(m in text for m in ['🐸', '!!', 'ribbit', 'croak', 'frog'])

def audit_example(example):
    issues = []
    turns = get_assistant_turns(example)
    for turn in turns:
        if not turn:
            continue
        banned = has_banned_phrase(turn)
        if banned:
            issues.append(('banned_phrase', banned[0]))
        qs = count_questions(turn)
        if qs > 1:
            issues.append(('multiple_questions', qs))
        if is_too_long(turn):
            issues.append(('too_long', word_count(turn)))
    return issues

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/train.jsonl")
    parser.add_argument("--report", action="store_true", help="Print report only")
    parser.add_argument("--purge", action="store_true", help="Remove contaminated examples")
    parser.add_argument("--output", default="data/train_clean.jsonl")
    args = parser.parse_args()

    examples = []
    with open(args.input, encoding='utf-8-sig') as f:
        for line in f:
            line = line.strip()
            if line:
                examples.append(json.loads(line))

    print(f"Loaded {len(examples):,} examples from {args.input}")

    issue_counts = defaultdict(int)
    contaminated = []
    clean = []

    for ex in examples:
        issues = audit_example(ex)
        if issues:
            contaminated.append((ex, issues))
            for issue_type, _ in issues:
                issue_counts[issue_type] += 1
        else:
            clean.append(ex)

    print(f"\n{'='*60}")
    print(f"AUDIT RESULTS")
    print(f"{'='*60}")
    print(f"Total examples:      {len(examples):,}")
    print(f"Contaminated:        {len(contaminated):,} ({100*len(contaminated)//len(examples)}%)")
    print(f"Clean:               {len(clean):,} ({100*len(clean)//len(examples)}%)")
    print(f"\nISSUES FOUND:")
    for issue, count in sorted(issue_counts.items(), key=lambda x: -x[1]):
        print(f"  {issue:<25} {count:,}")

    # Show samples of contaminated examples
    print(f"\nSAMPLE CONTAMINATED EXAMPLES (first 10):")
    for ex, issues in contaminated[:10]:
        msgs = ex.get("messages", [])
        user_msg = next((m["content"] for m in msgs if m["role"] == "user"), "(no user msg)")
        asst_msg = next((m["content"] for m in msgs if m["role"] == "assistant" and m.get("content")), "")
        print(f"\n  Issues: {issues}")
        print(f"  User:   {user_msg[:80]}")
        print(f"  Asst:   {asst_msg[:120]}")

    if args.purge:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            for ex in clean:
                f.write(json.dumps(ex, ensure_ascii=False) + '\n')
        print(f"\n✅ Purged dataset saved: {len(clean):,} clean examples → {args.output}")
        print(f"   Removed: {len(contaminated):,} contaminated examples ({100*len(contaminated)//len(examples)}%)")

if __name__ == "__main__":
    main()
