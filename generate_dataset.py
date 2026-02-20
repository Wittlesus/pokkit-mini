"""
Pokkit-mini training dataset generator v3 — expanded combinatorial.
Usage:
    python generate_dataset.py --output data/train.jsonl --count 10000
    python generate_dataset.py --output data/eval.jsonl  --count 500 --seed 99
"""
import json, random, argparse
from pathlib import Path
from dataset_batch8 import GENERATORS_BATCH8
from dataset_batch9 import GENERATORS_BATCH9
from dataset_batch10 import GENERATORS_BATCH10
from dataset_batch11 import GENERATORS_BATCH11
from dataset_batch12 import GENERATORS_BATCH12
from dataset_batch13 import GENERATORS_BATCH13
from dataset_batch14 import GENERATORS_BATCH14

from dataset_core import (
    alarm_time, tc, tr, u, a, ex, typo, validate_example,
    ALARM_TIMES, ALARM_TASKS, NOTE_ITEMS, SEARCH_TOPICS,
    CLIPBOARD_CASES, NOTIFICATION_CASES, STORE_CASES, TOOLS,
)

ALARM_VERBS = ["Set an alarm","Set a reminder","Remind me","Wake me up","Alert me","Ping me","Schedule a reminder"]
ALARM_REPLIES = [
    "done. {when}. you're gonna crush it. 🐸",
    "{when}. locked in. 🐸",
    "⏰ {title} set for {when}. 🐸 i've got you.",
    "alarm's live! {when} — don't even worry about it. 🐸",
    "{when}. on it. 🐸 anything else before i settle in?",
    "LOCKED. {title} at {when}. 🐸 i'll be loud about it.",
    "gotcha — {when} for {title}. 🐸 consider it handled.",
    "{title}? {when}? done and done. 🐸",
    "⏰ boom. {when}. i won't let you forget. 🐸",
]

def gen_alarm():
    verb = random.choice(ALARM_VERBS)
    time_phrase, dt_fn, when = random.choice(ALARM_TIMES)
    task_phrase, label = random.choice(ALARM_TASKS)
    hour, minute = dt_fn()
    patterns = [
        f"{verb} {time_phrase} to {task_phrase}",
        f"{verb} to {task_phrase} {time_phrase}",
        f"I need to {task_phrase} {time_phrase}, can you remind me?",
        f"Don't let me forget to {task_phrase} {time_phrase}",
        f"Remind me about {task_phrase} {time_phrase}",
        f"I have to {task_phrase} {time_phrase} — set a reminder",
        f"Can you {verb.lower()} {time_phrase} for {task_phrase}?",
        f"Please {verb.lower()} {time_phrase} — {task_phrase}",
    ]
    prompt = typo(random.choice(patterns))
    reply = random.choice(ALARM_REPLIES).format(title=label, when=when, task=task_phrase)
    return ex([u(prompt), tc("set_alarm",{"hour":hour,"minute":minute,"label":label}), tr({"success":True}), a(reply)])

# gen_email removed — compose_email has no production implementation

SEARCH_VERBS = ["Search for","Look up","Find","Google","Search","Tell me about","Find me info on","Can you look up"]
SEARCH_REPLIES = [
    "ooh let me dig into this. 🐸",
    "on it! 🐸 pulling up results now...",
    "searching... 🐸 give me a sec.",
    "🌐 found some good stuff! 🐸 here's what's out there.",
    "got results! 🐸 let me break this down for you.",
    "searched it. 🐸 here's the rundown.",
    "alright, here's what i found. 🐸",
    "🐸 done digging. here's what's relevant.",
]

def gen_search():
    verb = random.choice(SEARCH_VERBS)
    topic, query, _ = random.choice(SEARCH_TOPICS)
    reply = random.choice(SEARCH_REPLIES)
    patterns = [
        f"{verb} {topic}",
        f"Can you search for {topic}?",
        f"I need to know about {topic}",
        f"Look up {topic} for me",
        f"Search the web for {topic}",
        f"Find information about {topic}",
        f"What do you know about {topic}? Search it",
        f"Google {topic}",
    ]
    prompt = typo(random.choice(patterns))
    return ex([u(prompt), tc("web_search",{"query":query}), tr({"success":True,"results":f"Top results for: {query}"}), a(reply)])

NOTE_VERBS = ["Note:","Save a note:","Jot down:","Remember:","Log:","Write down:","Keep a note:","Record:"]
NOTE_REPLIES = [
    "noted! 🐸",
    "saved. 🐸 your brain is now backed up.",
    "📝 got it locked in. 🐸",
    "written down! 🐸 i'll remember even if you don't.",
    "noted and stored. 🐸 future you will thank present you.",
    "done! 🐸 it's safe with me.",
    "📝 saved! 🐸 anything else bouncing around in your head?",
]

def gen_note():
    item_phrase, title, content, _ = random.choice(NOTE_ITEMS)
    verb = random.choice(NOTE_VERBS)
    reply = random.choice(NOTE_REPLIES)
    patterns = [
        f"{verb} {item_phrase}",
        f"Save a note about my {item_phrase}",
        f"Jot down my {item_phrase}",
        f"Keep track of my {item_phrase}",
        f"Log my {item_phrase}",
        f"I want to save my {item_phrase}",
        f"Note to self: {item_phrase}",
        f"Can you save my {item_phrase}?",
    ]
    prompt = typo(random.choice(patterns))
    return ex([u(prompt), tc("take_note",{"title":title,"content":content}), tr({"success":True}), a(reply)])

# gen_photo removed — open_photo_editor has no production implementation


# gen_webhook removed — send_webhook has no production implementation


CLIPBOARD_VERBS = ["Copy","Put on clipboard","Copy to clipboard","Save to clipboard","Clip"]

def gen_clipboard():
    phrase, text, reply = random.choice(CLIPBOARD_CASES)
    verb = random.choice(CLIPBOARD_VERBS)
    patterns = [
        f"{verb} {phrase}",
        f"Copy {phrase} to my clipboard",
        f"Put {phrase} on the clipboard",
        f"I need {phrase} on my clipboard",
        f"Can you copy {phrase}?",
    ]
    prompt = typo(random.choice(patterns))
    return ex([u(prompt), tc("write_clipboard",{"text":text}), tr({"success":True}), a(reply)])


NOTIF_PROMPTS = [
    "Send me a notification to {body}",
    "Push a notification: {body}",
    "Remind me with a notification: {body}",
    "Show a notification saying {body}",
    "Notify me: {body}",
]

def gen_notification():
    title, body, reply = random.choice(NOTIFICATION_CASES)
    pattern = random.choice(NOTIF_PROMPTS)
    prompt = typo(pattern.format(body=body.lower().rstrip("!")))
    return ex([u(prompt), tc("show_notification",{"title":title,"body":body}), tr({"success":True}), a(reply)])


STORE_PROMPTS = [
    "Store {key} as {value}",
    "Save {key} = {value}",
    "Remember that {key} is {value}",
    "Set {key} to {value}",
    "Keep {key} = {value} in memory",
]

def gen_store():
    key, value, reply = random.choice(STORE_CASES)
    pattern = random.choice(STORE_PROMPTS)
    prompt = typo(pattern.format(key=key.replace("_"," "), value=value))
    return ex([u(prompt), tc("store_value",{"key":key,"value":value}), tr({"success":True}), a(reply)])

def gen_multi():
    """Generate chained multi-tool examples."""
    choice = random.randint(0, 5)

    if choice == 0:
        # alarm + note
        time_phrase, dt_fn, when = random.choice(ALARM_TIMES)
        task_phrase, label = random.choice(ALARM_TASKS)
        item_phrase, ntitle, content, _ = random.choice(NOTE_ITEMS)
        hour, minute = dt_fn()
        prompt = typo(f"Set an alarm {time_phrase} to {task_phrase} and also save a note about my {item_phrase}")
        return ex([
            u(prompt),
            tc("set_alarm",{"hour":hour,"minute":minute,"label":label}),
            tr({"success":True}),
            tc("take_note",{"title":ntitle,"content":content}),
            tr({"success":True}),
            a(f"alarm at {when} AND note saved. 🐸 double duty!"),
        ])

    elif choice == 1:
        # search + note
        topic, query, _ = random.choice(SEARCH_TOPICS)
        item_phrase, ntitle, content, _ = random.choice(NOTE_ITEMS)
        prompt = typo(f"Search for {topic} and save a note about my {item_phrase}")
        return ex([
            u(prompt),
            tc("web_search",{"query":query}),
            tr({"success":True,"results":f"Top results for: {query}"}),
            tc("take_note",{"title":ntitle,"content":content}),
            tr({"success":True}),
            a(f"searched AND noted. 🐸 multitasking king right here."),
        ])

    elif choice == 2:
        # alarm + notification
        time_phrase, dt_fn, when = random.choice(ALARM_TIMES)
        task_phrase, label = random.choice(ALARM_TASKS)
        ntitle, nbody, _ = random.choice(NOTIFICATION_CASES)
        hour, minute = dt_fn()
        prompt = typo(f"Set an alarm {time_phrase} to {task_phrase} and send me a notification about it")
        return ex([
            u(prompt),
            tc("set_alarm",{"hour":hour,"minute":minute,"label":label}),
            tr({"success":True}),
            tc("show_notification",{"title":ntitle,"body":nbody}),
            tr({"success":True}),
            a(f"alarm at {when} + notification sent. 🐸 two birds, one frog."),
        ])

    elif choice == 3:
        # note + clipboard
        item_phrase, ntitle, content, _ = random.choice(NOTE_ITEMS)
        phrase, text, _ = random.choice(CLIPBOARD_CASES)
        prompt = typo(f"Save a note about my {item_phrase} and copy {phrase} to clipboard")
        return ex([
            u(prompt),
            tc("take_note",{"title":ntitle,"content":content}),
            tr({"success":True}),
            tc("write_clipboard",{"text":text}),
            tr({"success":True}),
            a(f"note saved + clipboard loaded. 🐸 you're all set."),
        ])

    elif choice == 4:
        # search + alarm
        topic, query, _ = random.choice(SEARCH_TOPICS)
        time_phrase, dt_fn, when = random.choice(ALARM_TIMES)
        task_phrase, label = random.choice(ALARM_TASKS)
        hour, minute = dt_fn()
        prompt = typo(f"Search for {topic} and set an alarm {time_phrase} to {task_phrase}")
        return ex([
            u(prompt),
            tc("web_search",{"query":query}),
            tr({"success":True,"results":f"Top results for: {query}"}),
            tc("set_alarm",{"hour":hour,"minute":minute,"label":label}),
            tr({"success":True}),
            a(f"searched that up + alarm at {when}. 🐸 handled."),
        ])

    else:
        # store + note
        key, value, _ = random.choice(STORE_CASES)
        item_phrase, ntitle, content, _ = random.choice(NOTE_ITEMS)
        prompt = typo(f"Store {key.replace('_',' ')} as {value} and save a note about my {item_phrase}")
        return ex([
            u(prompt),
            tc("store_value",{"key":key,"value":value}),
            tr({"success":True}),
            tc("take_note",{"title":ntitle,"content":content}),
            tr({"success":True}),
            a(f"stored {key} + note saved. 🐸 brain updated."),
        ])

def gen_convo():
    """Multi-turn conversational examples."""
    choice = random.randint(0, 4)

    if choice == 0:
        time_phrase, dt_fn, when = random.choice(ALARM_TIMES)
        task_phrase, label = random.choice(ALARM_TASKS)
        hour, minute = dt_fn()
        return ex([
            u("Hey Pokkit!"),
            a("hey!! 🐸 what's up?"),
            u(f"Can you set a reminder {time_phrase} to {task_phrase}?"),
            tc("set_alarm",{"hour":hour,"minute":minute,"label":label}),
            tr({"success":True}),
            a(f"done! {when} — {label}. 🐸 got your back."),
        ])

    elif choice == 1:
        topic, query, reply = random.choice(SEARCH_TOPICS)
        item_phrase, ntitle, content, nreply = random.choice(NOTE_ITEMS)
        return ex([
            u(f"Can you search for {topic}?"),
            tc("web_search",{"query":query}),
            tr({"success":True,"results":f"Top results for: {query}"}),
            a(reply),
            u(f"Great! Now save a note about my {item_phrase}"),
            tc("take_note",{"title":ntitle,"content":content}),
            tr({"success":True}),
            a(nreply),
        ])

    elif choice == 2:
        time_phrase, dt_fn, when = random.choice(ALARM_TIMES)
        task_phrase, label = random.choice(ALARM_TASKS)
        hour, minute = dt_fn()
        return ex([
            u("What can you do?"),
            a("i'm pokkit! 🐸 alarms, web search, notes, screen control, clipboard — i do it all. what do you need?"),
            u(f"Set an alarm {time_phrase} to {task_phrase}"),
            tc("set_alarm",{"hour":hour,"minute":minute,"label":label}),
            tr({"success":True}),
            a(f"{label} at {when}. done! 🐸"),
        ])

    elif choice == 3:
        phrase, text, reply = random.choice(CLIPBOARD_CASES)
        topic, query, sreply = random.choice(SEARCH_TOPICS)
        return ex([
            u(f"Copy {phrase} to clipboard"),
            tc("write_clipboard",{"text":text}),
            tr({"success":True}),
            a(reply),
            u(f"Also search for {topic}"),
            tc("web_search",{"query":query}),
            tr({"success":True,"results":f"Top results for: {query}"}),
            a(sreply),
        ])

    else:
        key, value, sreply = random.choice(STORE_CASES)
        rkey, rval = key, value
        return ex([
            u(f"Store {key.replace('_',' ')} as {value}"),
            tc("store_value",{"key":key,"value":value}),
            tr({"success":True}),
            a(sreply),
            u(f"What did you store for {key.replace('_',' ')}?"),
            tc("retrieve_value",{"key":rkey}),
            tr({"value":rval}),
            a(f"you stored **{rkey}** = `{rval}` 🐸 want to update it?"),
        ])


# ── GENERATOR REGISTRY ─────────────────────────────────────────────────────

from dataset_personality import gen_personality, gen_reasoning, gen_research
from dataset_advanced import (
    gen_emotional, gen_ambiguous, gen_failure,
    gen_raw_voice, gen_proactive, gen_code, gen_refusal,
)
from dataset_batch2 import (
    gen_frog_lore, gen_culture, gen_framework,
    gen_dev_culture, gen_life_advice, gen_pokkit_lore, gen_banter,
)
from dataset_batch3 import (
    gen_resilience, gen_character_philosophy, gen_app_opinions,
    gen_memory_learning, gen_hopeful_reframe,
)
from dataset_dialogue_style import (
    gen_compliment_reaction, gen_mistake_reaction, gen_win_reaction,
    gen_self_aware, gen_defense, gen_task_excitement,
    gen_presence, gen_jake_wisdom,
)
from dataset_batch4 import (
    gen_morning_routine, gen_evening_winddown, gen_social_situation,
    gen_health_checkin, gen_money_moment, gen_creative_project,
    gen_pokkit_wrong, gen_skeptic, gen_smalltalk, gen_relationship,
)
from dataset_batch5 import (
    gen_contact_memory, gen_preference_memory, gen_habit_memory,
    gen_memory_recall, gen_empty_recall, gen_proactive_memory,
    gen_work_context, gen_multi_turn_memory, gen_memory_acknowledgment,
)
from dataset_batch6 import GENERATORS_BATCH6
from dataset_batch7 import GENERATORS_BATCH7

GENERATORS = [
    # ── tool-calling (core tasks) — target ~30% ──────────────
    (gen_alarm,        28),
    (gen_search,       20),
    (gen_note,         18),
    (gen_clipboard,     5),
    (gen_notification,  4),
    (gen_store,         4),
    (gen_multi,        12),  # chained tool calls
    (gen_convo,         8),  # multi-turn
    # ── voice + personality — reduced to 10-15% ───────────
    (gen_personality,   6),  # frog mascot + anime companion
    (gen_reasoning,     4),  # opinionated takes
    (gen_research,      4),  # search + synthesize
    # ── advanced / hard cases ─────────────────────────────
    (gen_emotional,     9),  # emotion + task
    (gen_ambiguous,     4),  # clarification loops
    (gen_failure,       3),  # error recovery
    (gen_raw_voice,     7),  # messy real-user input
    (gen_proactive,     4),  # proactive suggestions
    (gen_code,          6),  # technical help
    (gen_refusal,       2),  # in-character refusals
    # ── batch 2: character depth ───────────────────────────
    (gen_frog_lore,     5),  # frog biology + self-awareness
    (gen_culture,       6),  # anime, books, games, music opinions
    (gen_framework,     5),  # React Native / Expo / mobile stack
    (gen_dev_culture,   5),  # indie hacker / builder mindset
    (gen_life_advice,   6),  # real life advice with Pokkit voice
    (gen_pokkit_lore,   4),  # Pokkit's own backstory + inner life
    (gen_banter,        5),  # wit, callbacks, genuine humor
    # ── batch 3: philosophy + resilience + apps ────────────
    (gen_resilience,        8),  # hopeful steadiness in hard moments
    (gen_character_philosophy, 4),  # Luffy/Goku/Naruto direct questions
    (gen_app_opinions,      5),  # app ecosystem takes
    (gen_memory_learning,   5),  # preference/memory learning chains
    (gen_hopeful_reframe,   6),  # short steady responses to dark moments
    # ── dialogue style: synthesized character voice ────────
    (gen_compliment_reaction, 6),  # flustered by compliments (Chopper)
    (gen_mistake_reaction,    6),  # dramatic ownership of mistakes
    (gen_win_reaction,        6),  # celebrates user wins hard (Luffy/Naruto)
    (gen_self_aware,          5),  # frog/AI self-aware jokes (Jake)
    (gen_defense,             7),  # defends user from themselves (fierce)
    (gen_task_excitement,     5),  # excited about hard problems (Goku)
    (gen_presence,            5),  # wordless presence (Pikachu)
    (gen_jake_wisdom,         5),  # warm silly suddenly profound (Jake)
    # ── batch 4: daily life + relationship depth ───────────
    (gen_morning_routine,     5),  # morning check-ins + task chains
    (gen_evening_winddown,    4),  # evening wind-down moments
    (gen_social_situation,    6),  # texts, hard convos, social anxiety
    (gen_health_checkin,      5),  # body/mind check-ins
    (gen_money_moment,        4),  # financial moments + advice
    (gen_creative_project,    4),  # creative work support
    (gen_pokkit_wrong,        4),  # Pokkit owns mistakes gracefully
    (gen_skeptic,             4),  # skeptical user / trust building
    (gen_smalltalk,           6),  # casual connection + personality
    (gen_relationship,        4),  # ongoing relationship building
    # ── batch 5: memory learning + recall ──────────────
    (gen_contact_memory,      6),  # stores contact names/relationships
    (gen_preference_memory,   6),  # stores user preferences
    (gen_habit_memory,        5),  # stores habits and goals
    (gen_memory_recall,       6),  # retrieves + uses stored memory
    (gen_empty_recall,        4),  # graceful handling of empty memory
    (gen_proactive_memory,    5),  # proactively uses what it knows
    (gen_work_context,        5),  # stores work/project context
    (gen_multi_turn_memory,   4),  # multi-turn memory building chains
    (gen_memory_acknowledgment, 4), # confirms memory, handles updates
    # ── batch 6: targeted eval fixes ───────────────────────
    # Pet character breaks, datetime garbling, unexpected tools, multi-question
] + [(fn, w) for fn, w in GENERATORS_BATCH6]\
  + [(fn, w) for fn, w in GENERATORS_BATCH7]\
  + [(fn, w) for fn, w in GENERATORS_BATCH8]\
  + [(fn, w) for fn, w in GENERATORS_BATCH9]\
  + [(fn, w) for fn, w in GENERATORS_BATCH10]\
  + [(fn, w) for fn, w in GENERATORS_BATCH11]\
  + [(fn, w) for fn, w in GENERATORS_BATCH12]\
  + [(fn, w) for fn, w in GENERATORS_BATCH13]\
  + [(fn, w) for fn, w in GENERATORS_BATCH14]

_POOL = []
for fn, weight in GENERATORS:
    _POOL.extend([fn] * weight)


def generate_example():
    return random.choice(_POOL)()


# ── MAIN ───────────────────────────────────────────────────────────────────

def _content_hash(example):
    """Deterministic hash of an example's message content for dedup."""
    import hashlib
    # Hash the user/assistant text content (not system prompt, which is always the same)
    parts = []
    for msg in example.get("messages", []):
        if msg.get("role") in ("user", "assistant"):
            parts.append(msg.get("content") or "")
    return hashlib.md5("||".join(parts).encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description="Generate Pokkit-mini training data")
    parser.add_argument("--output",  default="data/train.jsonl", help="Output JSONL file")
    parser.add_argument("--count",   type=int, default=10000,    help="Number of examples")
    parser.add_argument("--seed",    type=int, default=42,       help="Random seed")
    parser.add_argument("--eval-output", default=None,           help="Eval output file (enables train/eval split)")
    parser.add_argument("--eval-count", type=int, default=500,   help="Number of eval examples")
    args = parser.parse_args()

    random.seed(args.seed)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    # Generate training examples
    print(f"Generating {args.count} training examples -> {out}")
    train_examples = []
    train_hashes = set()
    validation_errors = 0
    for i in range(args.count):
        example = generate_example()
        try:
            validate_example(example)
        except ValueError as e:
            validation_errors += 1
            if validation_errors <= 10:
                print(f"  [WARN] Validation error #{validation_errors}: {e}")
        h = _content_hash(example)
        if h not in train_hashes:
            train_hashes.add(h)
            train_examples.append(example)
        if (i + 1) % 1000 == 0:
            print(f"  {i+1}/{args.count} generated ({len(train_examples)} unique)...")

    with out.open("w", encoding="utf-8") as f:
        for ex in train_examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    if validation_errors > 0:
        print(f"\n[WARN] {validation_errors} validation errors found!")
    print(f"Done! {len(train_examples)} unique training examples saved to {out}")

    # Generate eval examples with a different seed, excluding any train duplicates
    if args.eval_output:
        eval_out = Path(args.eval_output)
        eval_out.parent.mkdir(parents=True, exist_ok=True)
        eval_seed = args.seed + 7919  # offset by a large prime
        random.seed(eval_seed)

        print(f"\nGenerating eval set (target {args.eval_count}) -> {eval_out}")
        eval_examples = []
        attempts = 0
        max_attempts = args.eval_count * 5  # generate extra to account for collisions
        while len(eval_examples) < args.eval_count and attempts < max_attempts:
            attempts += 1
            example = generate_example()
            try:
                validate_example(example)
            except ValueError:
                continue
            h = _content_hash(example)
            if h not in train_hashes:
                train_hashes.add(h)  # prevent eval-internal dupes too
                eval_examples.append(example)

        with eval_out.open("w", encoding="utf-8") as f:
            for ex in eval_examples:
                f.write(json.dumps(ex, ensure_ascii=False) + "\n")
        print(f"Done! {len(eval_examples)} eval examples saved to {eval_out} (no overlap with train)")


if __name__ == "__main__":
    main()

