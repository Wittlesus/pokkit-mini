"""
Pokkit-mini training dataset generator v3 — expanded combinatorial.
Usage:
    python generate_dataset.py --output data/train.jsonl --count 10000
    python generate_dataset.py --output data/eval.jsonl  --count 500 --seed 99
"""
import json, random, argparse
from pathlib import Path
from dataset_batch8 import GENERATORS_BATCH8

from dataset_core import (
    fdt, tc, tr, u, a, ex, typo,
    ALARM_TIMES, ALARM_TASKS, NOTE_ITEMS, SEARCH_TOPICS,
    EMAIL_RECIPIENTS, EMAIL_TOPICS, CLIPBOARD_CASES,
    NOTIFICATION_CASES, STORE_CASES, WEBHOOK_CASES,
)

ALARM_VERBS = ["Set an alarm","Set a reminder","Remind me","Wake me up","Alert me","Ping me","Schedule a reminder"]
ALARM_REPLIES = [
    "⏰ {title} alarm set for {when}!",
    "✅ Reminder set for {when} — {title}!",
    "Done! ⏰ I'll remind you to {task} at {when}.",
    "🐸 Got it — {title} reminder locked in for {when}!",
    "⏰ {when} alarm set. I've got you covered!",
    "✅ {title} — reminder set for {when}!",
    "🔔 Reminder created: {title} at {when}!",
]

def gen_alarm():
    verb = random.choice(ALARM_VERBS)
    time_phrase, dt_fn, when = random.choice(ALARM_TIMES)
    task_phrase, title = random.choice(ALARM_TASKS)
    dt = dt_fn()
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
    reply = random.choice(ALARM_REPLIES).format(title=title, when=when, task=task_phrase)
    return ex([u(prompt), tc("set_alarm",{"title":title,"datetime":dt}), tr({"success":True}), a(reply)])

EMAIL_VERBS = ["Email","Write an email to","Send an email to","Draft an email to","Compose an email to","Message","Write to"]
EMAIL_REPLIES = [
    "✉️ Email drafted for {name}!",
    "✉️ {topic} email drafted — review and send!",
    "Done! ✉️ Email to {name} is ready to go.",
    "✉️ Draft ready for {name}. Hit send when you're ready!",
    "🐸 Email drafted! Just review and send.",
    "✉️ Got it — {name} email is composed and ready!",
]

def gen_email():
    verb = random.choice(EMAIL_VERBS)
    name, to, short_name = random.choice(EMAIL_RECIPIENTS)
    topic_phrase, subject, body = random.choice(EMAIL_TOPICS)
    patterns = [
        f"{verb} {name} about {topic_phrase}",
        f"Help me email {name} about {topic_phrase}",
        f"Write an email to {name} regarding {topic_phrase}",
        f"I need to email {name} about {topic_phrase}",
        f"Draft an email to {name} — {topic_phrase}",
        f"Can you email {name} about {topic_phrase}?",
        f"Compose a message to {name} about {topic_phrase}",
    ]
    prompt = typo(random.choice(patterns))
    reply = random.choice(EMAIL_REPLIES).format(name=short_name, topic=topic_phrase.split()[0].capitalize())
    return ex([u(prompt), tc("compose_email",{"to":to,"subject":subject,"body":body}), tr({"success":True}), a(reply)])

SEARCH_VERBS = ["Search for","Look up","Find","Google","Search","Tell me about","Find me info on","Can you look up"]

def gen_search():
    verb = random.choice(SEARCH_VERBS)
    topic, query, reply = random.choice(SEARCH_TOPICS)
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

def gen_note():
    item_phrase, title, content, reply = random.choice(NOTE_ITEMS)
    verb = random.choice(NOTE_VERBS)
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

PHOTO_CASES = [
    ("edit a photo","Edit the photo","📸 Photo picker open — select your photo!"),
    ("crop a photo","Crop the photo","📸 Select the photo to crop!"),
    ("brighten a photo","Brighten the photo","📸 Photo picker open — I'll brighten it up!"),
    ("add a filter to a photo","Apply a filter to the photo","📸 Select the photo to apply a filter!"),
    ("remove the background from a photo","Remove background from photo","📸 Select the photo — I'll remove the background!"),
    ("make a photo black and white","Convert photo to black and white","📸 Select the photo to convert!"),
    ("rotate a photo","Rotate the photo","📸 Select the photo to rotate!"),
    ("resize a photo","Resize the photo","📸 Select the photo to resize!"),
    ("enhance a photo","Enhance photo quality","📸 Select the photo to enhance!"),
    ("add text to a photo","Add text overlay to photo","📸 Select the photo to add text to!"),
    ("blur the background of a photo","Blur photo background","📸 Select the photo — I'll blur the background!"),
    ("fix the lighting in a photo","Fix photo lighting","📸 Select the photo to fix the lighting!"),
    ("sharpen a photo","Sharpen the photo","📸 Select the photo to sharpen!"),
    ("compress a photo","Compress photo file size","📸 Select the photo to compress!"),
    ("collage some photos","Create photo collage","📸 Select the photos for your collage!"),
]

PHOTO_VERBS = ["Edit","Open","Fix","Enhance","Crop","Filter","Adjust"]

def gen_photo():
    phrase, instruction, reply = random.choice(PHOTO_CASES)
    patterns = [
        f"Can you {phrase}?",
        f"I want to {phrase}",
        f"Help me {phrase}",
        f"{phrase.capitalize()} for me",
        f"Open the photo editor to {phrase}",
        f"I need to {phrase}",
    ]
    prompt = typo(random.choice(patterns))
    return ex([u(prompt), tc("open_photo_editor",{"instruction":instruction}), tr({"success":True}), a(reply)])


WEBHOOK_PROMPTS = [
    "Fire my Zapier webhook",
    "Trigger my Discord webhook",
    "Send a webhook to Slack",
    "Hit my webhook endpoint",
    "Trigger my n8n workflow via webhook",
    "Fire my Make.com webhook",
    "Send a POST to my webhook",
    "Trigger my automation webhook",
]

def gen_webhook():
    url, payload, reply = random.choice(WEBHOOK_CASES)
    prompt = typo(random.choice(WEBHOOK_PROMPTS))
    return ex([u(prompt), tc("send_webhook",{"url":url,"payload":payload}), tr({"success":True,"status":200}), a(reply)])


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
    choice = random.randint(0, 7)

    if choice == 0:
        # alarm + note
        time_phrase, dt_fn, when = random.choice(ALARM_TIMES)
        task_phrase, title = random.choice(ALARM_TASKS)
        item_phrase, ntitle, content, _ = random.choice(NOTE_ITEMS)
        dt = dt_fn()
        prompt = typo(f"Set an alarm {time_phrase} to {task_phrase} and also save a note about my {item_phrase}")
        return ex([
            u(prompt),
            tc("set_alarm",{"title":title,"datetime":dt}),
            tr({"success":True}),
            tc("take_note",{"title":ntitle,"content":content}),
            tr({"success":True}),
            a(f"⏰ Alarm set for {when} and 📝 note saved!"),
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
            a(f"🌐 Searched for {topic} and 📝 saved your note!"),
        ])

    elif choice == 2:
        # alarm + email
        time_phrase, dt_fn, when = random.choice(ALARM_TIMES)
        task_phrase, title = random.choice(ALARM_TASKS)
        name, to, short_name = random.choice(EMAIL_RECIPIENTS)
        topic_phrase, subject, body = random.choice(EMAIL_TOPICS)
        dt = dt_fn()
        prompt = typo(f"Set a reminder {time_phrase} to {task_phrase} and email {name} about {topic_phrase}")
        return ex([
            u(prompt),
            tc("set_alarm",{"title":title,"datetime":dt}),
            tr({"success":True}),
            tc("compose_email",{"to":to,"subject":subject,"body":body}),
            tr({"success":True}),
            a(f"⏰ Reminder set for {when} and ✉️ email drafted for {short_name}!"),
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
            a(f"📝 Note saved and 📋 {phrase} copied to clipboard!"),
        ])

    elif choice == 4:
        # search + alarm
        topic, query, _ = random.choice(SEARCH_TOPICS)
        time_phrase, dt_fn, when = random.choice(ALARM_TIMES)
        task_phrase, title = random.choice(ALARM_TASKS)
        dt = dt_fn()
        prompt = typo(f"Search for {topic} and set an alarm {time_phrase} to {task_phrase}")
        return ex([
            u(prompt),
            tc("web_search",{"query":query}),
            tr({"success":True,"results":f"Top results for: {query}"}),
            tc("set_alarm",{"title":title,"datetime":dt}),
            tr({"success":True}),
            a(f"🌐 Searched for {topic} and ⏰ alarm set for {when}!"),
        ])

    elif choice == 5:
        # webhook + notification
        url, payload, _ = random.choice(WEBHOOK_CASES)
        ntitle, nbody, _ = random.choice(NOTIFICATION_CASES)
        prompt = typo("Trigger my webhook and send me a notification when done")
        return ex([
            u(prompt),
            tc("send_webhook",{"url":url,"payload":payload}),
            tr({"success":True,"status":200}),
            tc("show_notification",{"title":ntitle,"body":nbody}),
            tr({"success":True}),
            a("🔗 Webhook fired and 🔔 notification sent!"),
        ])

    elif choice == 6:
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
            a(f"⚙️ Stored {key} and 📝 note saved!"),
        ])

    else:
        # email + alarm
        name, to, short_name = random.choice(EMAIL_RECIPIENTS)
        topic_phrase, subject, body = random.choice(EMAIL_TOPICS)
        time_phrase, dt_fn, when = random.choice(ALARM_TIMES)
        task_phrase, title = random.choice(ALARM_TASKS)
        dt = dt_fn()
        prompt = typo(f"Email {name} about {topic_phrase} and remind me {time_phrase} to {task_phrase}")
        return ex([
            u(prompt),
            tc("compose_email",{"to":to,"subject":subject,"body":body}),
            tr({"success":True}),
            tc("set_alarm",{"title":title,"datetime":dt}),
            tr({"success":True}),
            a(f"✉️ Email drafted for {short_name} and ⏰ reminder set for {when}!"),
        ])

def gen_convo():
    """Multi-turn conversational examples."""
    choice = random.randint(0, 5)

    if choice == 0:
        time_phrase, dt_fn, when = random.choice(ALARM_TIMES)
        task_phrase, title = random.choice(ALARM_TASKS)
        dt = dt_fn()
        return ex([
            u("Hey Pokkit!"),
            a("Hey! 🐸 What can I do for you?"),
            u(f"Can you set a reminder {time_phrase} to {task_phrase}?"),
            tc("set_alarm",{"title":title,"datetime":dt}),
            tr({"success":True}),
            a(f"⏰ Done! Reminder set for {when} — {title}!"),
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
        name, to, short_name = random.choice(EMAIL_RECIPIENTS)
        topic_phrase, subject, body = random.choice(EMAIL_TOPICS)
        return ex([
            u(f"I need to email {name}"),
            a(f"Sure! What's the email about?"),
            u(f"About {topic_phrase}"),
            tc("compose_email",{"to":to,"subject":subject,"body":body}),
            tr({"success":True}),
            a(f"✉️ Email to {short_name} drafted and ready to send!"),
        ])

    elif choice == 3:
        time_phrase, dt_fn, when = random.choice(ALARM_TIMES)
        task_phrase, title = random.choice(ALARM_TASKS)
        dt = dt_fn()
        return ex([
            u("What can you do?"),
            a("I'm Pokkit! 🐸 I can set alarms, send emails, search the web, take notes, edit photos, fire webhooks, manage your clipboard, and more. What do you need?"),
            u(f"Set an alarm {time_phrase} to {task_phrase}"),
            tc("set_alarm",{"title":title,"datetime":dt}),
            tr({"success":True}),
            a(f"⏰ {title} alarm set for {when}!"),
        ])

    elif choice == 4:
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
            a(f"I stored **{rkey}** = `{rval}` 🐸"),
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
    # ── tool-calling (core tasks) ──────────────────────────
    (gen_alarm,        10),
    (gen_email,         6),
    (gen_search,        8),
    (gen_note,          7),
    (gen_photo,         2),
    (gen_webhook,       1),
    (gen_clipboard,     2),
    (gen_notification,  1),
    (gen_store,         1),
    (gen_multi,         6),  # chained tool calls
    (gen_convo,         4),  # multi-turn
    # ── voice + personality ────────────────────────────────
    (gen_personality,  12),  # frog mascot + anime companion
    (gen_reasoning,     8),  # opinionated takes
    (gen_research,      7),  # search + synthesize
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
] + [(fn, w) for fn, w in GENERATORS_BATCH6] + [(fn, w) for fn, w in GENERATORS_BATCH7] + [(fn, w) for fn, w in GENERATORS_BATCH8]

_POOL = []
for fn, weight in GENERATORS:
    _POOL.extend([fn] * weight)


def generate_example():
    return random.choice(_POOL)()


# ── MAIN ───────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Generate Pokkit-mini training data")
    parser.add_argument("--output",  default="data/train.jsonl", help="Output JSONL file")
    parser.add_argument("--count",   type=int, default=10000,    help="Number of examples")
    parser.add_argument("--seed",    type=int, default=42,       help="Random seed")
    args = parser.parse_args()

    random.seed(args.seed)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    print(f"Generating {args.count} examples → {out}")
    with out.open("w", encoding="utf-8") as f:
        for i in range(args.count):
            example = generate_example()
            f.write(json.dumps(example, ensure_ascii=False) + "\n")
            if (i + 1) % 1000 == 0:
                print(f"  {i+1}/{args.count} written...")

    print(f"Done! {args.count} examples saved to {out}")


if __name__ == "__main__":
    main()

