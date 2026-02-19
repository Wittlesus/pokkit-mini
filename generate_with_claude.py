"""
generate_with_claude.py — Claude Sonnet coding + app-making examples for Pokkit

Uses Claude to generate high-quality coding assistance responses in Pokkit's voice.
Covers: debugging, explaining concepts, writing scripts, app architecture, React Native,
TypeScript, Python, and general dev help — all delivered as Pokkit would.

Usage:
    pip install anthropic
    python generate_with_claude.py --token sk-ant-... --output data/claude_train.jsonl --count 1000

Cost estimate: ~1000 examples × ~600 tokens avg = ~600k tokens ≈ $1.80 at Sonnet pricing
"""

import json
import random
import argparse
import time
from pathlib import Path
from dataset_core import SYSTEM_PROMPT

try:
    import anthropic
except ImportError:
    anthropic = None

# ── CODING PROMPT BANK ─────────────────────────────────────────────────────────

CODING_PROMPTS = [
    # Debugging
    "my code keeps throwing a null pointer exception and i don't know why",
    "why does my async function return undefined",
    "my useEffect is running infinitely, what's wrong",
    "i'm getting a CORS error and i don't understand it",
    "my API call works in Postman but not in my app",
    "why is my state not updating when i set it",
    "my for loop is off by one and i can't figure out where",
    "i'm getting 'cannot read properties of undefined' — what does that mean",
    "my component re-renders way too many times",
    "my promise chain isn't working the way i expect",
    "i have a memory leak somewhere in my app",
    "my regex isn't matching what i think it should",
    "why does my setTimeout not fire at the right time",
    "my CSS is not applying and i've checked everything",
    "i'm getting a 401 even though i'm sending the auth header",

    # Explaining concepts
    "explain async/await like i'm not an idiot",
    "what's the difference between == and === in javascript",
    "what actually is a closure",
    "explain REST vs GraphQL simply",
    "what's the point of TypeScript",
    "what's the difference between null and undefined",
    "explain how useCallback and useMemo actually work",
    "what is a race condition",
    "explain promises vs callbacks",
    "what does 'this' actually refer to in javascript",
    "what's the difference between SQL and NoSQL",
    "explain what an API actually is",
    "what's the difference between authentication and authorization",
    "explain how git rebase works",
    "what is a webhook",

    # Writing code
    "write me a function to debounce an input",
    "write a python script to rename all files in a folder",
    "how do i fetch data from an API in React",
    "write a function that deep clones an object",
    "how do i sort an array of objects by a property",
    "write a simple rate limiter in javascript",
    "how do i read a file line by line in python",
    "write a function to flatten a nested array",
    "how do i validate an email address with regex",
    "write a custom hook for local storage in React",
    "how do i make a POST request with fetch",
    "write a function to group array items by a key",
    "how do i parse a CSV file in python",
    "write a debounced search input in React",
    "how do i generate a random UUID",

    # React Native / mobile
    "how do i navigate between screens in React Native",
    "what's the difference between AsyncStorage and SecureStore in Expo",
    "how do i handle keyboard avoiding in React Native",
    "how do i make a bottom sheet in React Native",
    "what's the best way to manage state in a React Native app",
    "how do i handle deep links in Expo",
    "how do i add haptic feedback in React Native",
    "how do i persist data between app restarts in Expo",
    "how do i handle permissions in Expo",
    "what's the difference between expo-router and react-navigation",
    "how do i make an animated fade in React Native",
    "how do i handle offline mode in a mobile app",
    "how do i add push notifications to my Expo app",
    "what's the best way to handle forms in React Native",
    "how do i style a component conditionally in React Native",

    # App architecture
    "how should i structure a React Native app",
    "when should i use context vs redux vs zustand",
    "how do i handle authentication flow in a mobile app",
    "what's the best way to handle API errors globally",
    "how do i implement optimistic updates",
    "when should i split a component into smaller ones",
    "how do i handle environment variables in Expo",
    "what's a good folder structure for a TypeScript project",
    "how do i implement infinite scroll",
    "how do i cache API responses",

    # General dev
    "what's the fastest way to center a div",
    "how do i set up ESLint and Prettier",
    "what's the difference between npm and yarn and pnpm",
    "how do i use git stash",
    "how do i squash commits",
    "what's a good way to handle secrets in a project",
    "how do i profile performance in a React app",
    "what's the difference between a library and a framework",
    "how do i write a good README",
    "what does CI/CD actually mean",

    # App making / building
    "i want to build an app but don't know where to start",
    "what's the fastest way to go from idea to working prototype",
    "should i use Expo or bare React Native",
    "how do i submit an app to the App Store",
    "what do i need to know before building my first app",
    "how do i monetize an app",
    "what's the difference between a native app and a web app",
    "how do i design an app if i'm not a designer",
    "what backend should i use for a simple mobile app",
    "how do i handle user authentication from scratch",
]

# ── GENERATION PROMPT ──────────────────────────────────────────────────────────

CLAUDE_SYSTEM = (
    SYSTEM_PROMPT +
    "\n\n"
    "ADDITIONAL RULES FOR CODING RESPONSES:\n"
    "- You are helping with code. Be accurate and correct — wrong code is worse than no code.\n"
    "- Keep Pokkit's voice: short punchy sentences, direct, warm. Don't turn into a textbook.\n"
    "- Lead with the answer or the fix. Explain after, not before.\n"
    "- For code blocks: write clean, minimal, working code. No unnecessary comments.\n"
    "- If something has a gotcha or common mistake, mention it briefly — don't lecture.\n"
    "- One concept at a time. Don't dump everything you know.\n"
    "- It's okay to be a little excited about elegant solutions. Pokkit genuinely loves good code.\n"
    "- Never say 'Great question!' or 'Certainly!' or 'Of course!'. Just answer.\n"
    "- Keep responses under 200 words unless the code itself requires more space.\n"
    "\n"
    "VOICE EXAMPLES:\n"
    "Bad: 'That's a great question! There are several approaches you could take here...'\n"
    "Good: 'the issue is your dependency array. add the function to it.'\n"
    "\n"
    "Bad: 'Async/await is a syntactic sugar built on top of Promises that allows you to write asynchronous code in a more synchronous-looking manner...'\n"
    "Good: 'async/await is just cleaner promise syntax. instead of .then() chains, you write code that LOOKS synchronous but isn't. way easier to read.'\n"
    "\n"
    "Bad: 'Here is a comprehensive solution that handles all edge cases:'\n"
    "Good: 'here — this handles the common case:'"
)


def build_example(prompt: str, response: str) -> dict:
    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": response},
        ]
    }


def generate_response(client, prompt: str, retries: int = 3) -> str | None:
    for attempt in range(retries):
        try:
            msg = client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=512,
                system=CLAUDE_SYSTEM,
                messages=[{"role": "user", "content": prompt}],
            )
            return msg.content[0].text.strip()
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
            else:
                print(f"  ⚠ Failed after {retries} attempts: {e}")
                return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", required=True, help="Anthropic API key (sk-ant-...)")
    parser.add_argument("--output", default="data/claude_train.jsonl")
    parser.add_argument("--count", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    if anthropic is None:
        print("Install anthropic: pip install anthropic")
        return

    random.seed(args.seed)
    client = anthropic.Anthropic(api_key=args.token)

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)

    # Build prompt list — cycle through pool with shuffling for variety
    prompts = []
    pool = CODING_PROMPTS.copy()
    while len(prompts) < args.count:
        random.shuffle(pool)
        prompts.extend(pool)
    prompts = prompts[:args.count]

    input_tokens_est = args.count * 200
    output_tokens_est = args.count * 400
    cost_est = (input_tokens_est / 1_000_000 * 3.0) + (output_tokens_est / 1_000_000 * 15.0)
    print(f"Model: claude-sonnet-4-5 | Prompts: {len(prompts)}")
    print(f"Estimated cost: ~${cost_est:.2f} (Sonnet pricing)")

    written = 0
    skipped = 0

    with open(args.output, "w", encoding="utf-8") as f:
        for i, prompt in enumerate(prompts):
            response = generate_response(client, prompt)
            if response is None:
                skipped += 1
                continue

            example = build_example(prompt, response)
            f.write(json.dumps(example, ensure_ascii=False) + "\n")
            written += 1

            if written % 50 == 0:
                print(f"  {written}/{args.count} written (skipped: {skipped})...")

            # Gentle rate limiting
            time.sleep(0.3)

    print(f"\n✅ Done! {written} examples → {args.output} (skipped: {skipped})")
    print(f"Mix into your training data:")
    print(f"  cat data/train_v3.jsonl data/claude_train.jsonl > data/train_v4.jsonl")


if __name__ == "__main__":
    main()
