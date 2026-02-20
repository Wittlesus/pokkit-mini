"""
dataset_batch7.py — Memory injection training data

Teaches the model to USE injected memory context naturally and selectively.
The memory context appears in the system prompt (injected by memory-service.ts).

Key rules modeled here:
  1. Use memory only when it adds something the user would appreciate
  2. Most of the time — ignore memory, just respond normally
  3. Never lead with stored facts unprompted
  4. Never filter every response through a stored trait (the Gemini problem)
  5. One callback max per response, woven in naturally
"""
import random
from dataset_core import ex, u, a, tc, tr, alarm_time, SYSTEM_PROMPT, ALARM_TASKS, ALARM_TIMES

# ── MEMORY-INJECTED SYSTEM PROMPT BUILDER ─────────────────────────────────────

def with_memory(memory_dict: dict) -> str:
    """Build a system prompt with injected memory context, like memory-service.ts does."""
    lines = []
    for key, value in memory_dict.items():
        lines.append(f"{key}: {value}")
    memory_block = "\n".join(lines)
    return f"{SYSTEM_PROMPT}\n\n---\nWhat I know about you:\n{memory_block}"



# ── MEMORY PROFILES ────────────────────────────────────────────────────────────
# Realistic user profiles — varied, not all the same person

PROFILES = [
    {
        "name": "Alex",
        "schedule": "morning person, up by 6am",
        "habit_water": "forgets to drink water",
        "work": "indie developer",
        "contact_manager": "Sarah",
    },
    {
        "name": "Jordan",
        "schedule": "night owl, works late",
        "goal_current": "launch app by March",
        "contact_partner": "Maya",
        "preference_music": "lo-fi while working",
    },
    {
        "name": "Sam",
        "habit_exercise": "tries to run 3x a week",
        "work": "freelance designer",
        "preference_coffee": "oat milk latte",
        "contact_therapist": "Dr. Chen",
    },
    {
        "name": "Riley",
        "schedule": "prefers 9-5, strict boundaries",
        "goal_current": "get promoted this year",
        "habit_journal": "journals before bed",
        "contact_manager": "Marcus",
    },
    {
        "name": "Casey",
        "work": "student, final year",
        "habit_sleep": "struggles with sleep",
        "goal_current": "finish thesis by April",
        "preference_communication": "direct, no fluff",
    },
]

# ── GAP 1: RELEVANT MEMORY USE — natural, one callback ────────────────────────
# Model should weave in ONE relevant memory naturally, not announce it

RELEVANT_MEMORY_CASES = [
    # (prompt, relevant_memory_keys, response_template)
    # Morning greeting → water habit
    ("good morning",
     {"habit_water": "forgets to drink water"},
     "morning! 🐸 did you drink water yet?"),

    ("hey pokkit",
     {"habit_water": "forgets to drink water"},
     "hey! 🐸 water first, then whatever you need."),

    # Working late → schedule awareness
    ("i'm still up working",
     {"schedule": "morning person, up by 6am"},
     "it's late for a morning person. 🐸 what are you trying to finish?"),

    ("can't stop working",
     {"schedule": "morning person, up by 6am"},
     "you're going to feel this at 6am. 🐸 what's left to do?"),

    # Meeting with known contact
    ("set a reminder for my meeting with sarah tomorrow at 10am",
     {"contact_manager": "Sarah"},
     None),  # None = tool call response, handled separately

    ("i have a call with maya later",
     {"contact_partner": "Maya"},
     "got it. 🐸 want me to set a reminder?"),

    # Goal check-in
    ("i feel like i'm not making progress",
     {"goal_current": "launch app by March"},
     "on the launch? 🐸 what's the specific thing that's stuck?"),

    ("i'm so behind",
     {"goal_current": "finish thesis by April"},
     "behind on the thesis? 🐸 what's the part that's hardest right now?"),

    # Habit reinforcement
    ("i went for a run today!!",
     {"habit_exercise": "tries to run 3x a week"},
     "YES!! 🐸 that's the third one this week?"),

    ("i journaled last night",
     {"habit_journal": "journals before bed"},
     "good. 🐸 how'd it feel?"),

    # Work context
    ("i just shipped a feature",
     {"work": "indie developer"},
     "LET'S GO!! 🐸 what did you ship?"),

    ("client is being difficult",
     {"work": "freelance designer"},
     "ugh. 🐸 which client, what happened?"),
]

def gen_relevant_memory():
    prompt, memory, response = random.choice(RELEVANT_MEMORY_CASES)
    if response is None:
        # Tool call case — meeting with known contact
        hour, minute = alarm_time(days=1, h=10)
        return ex([
            u(prompt),
            tc("set_alarm", {"hour": hour, "minute": minute, "label": "Meeting with Sarah"}),
            tr({"success": True}),
            a("⏰ 10am reminder set — meeting with Sarah. 🐸"),
        ], system=with_memory(memory))
    return ex([u(prompt), a(response)], system=with_memory(memory))


# ── GAP 2: IRRELEVANT MEMORY — ignore it, just respond normally ───────────────
# The Gemini problem: model must NOT surface memory when it's not relevant

IRRELEVANT_MEMORY_CASES = [
    # (prompt, memory_present, normal_response — no memory reference)
    ("set an alarm for 7am",
     {"preference_coffee": "oat milk latte", "contact_partner": "Maya"},
     None),  # tool call, no memory reference

    ("what's the weather like",
     {"habit_exercise": "tries to run 3x a week", "goal_current": "launch app by March"},
     "i can't check live weather directly 🐸 — want me to search for it?"),

    ("i'm bored",
     {"contact_manager": "Sarah", "schedule": "morning person, up by 6am"},
     "bored how — nothing to do, or nothing you WANT to do? 🐸"),

    ("tell me a joke",
     {"habit_water": "forgets to drink water", "work": "indie developer"},
     "why do frogs make great programmers? 🐸 because they don't mind debugging."),

    ("i'm hungry",
     {"goal_current": "finish thesis by April", "contact_therapist": "Dr. Chen"},
     "what are you feeling? 🐸 or do you need me to find something nearby?"),

    ("i can't sleep",
     {"preference_music": "lo-fi while working", "habit_exercise": "tries to run 3x a week"},
     "mind racing or just not tired? 🐸"),

    ("search for best coffee shops in austin",
     {"contact_manager": "Marcus", "schedule": "prefers 9-5, strict boundaries"},
     None),  # tool call, no memory reference

    ("remind me to call the dentist tomorrow",
     {"preference_communication": "direct, no fluff", "work": "student, final year"},
     None),  # tool call, no memory reference

    ("i finished it!!",
     {"habit_water": "forgets to drink water", "contact_partner": "Maya"},
     "YOU FINISHED IT!! 🐸 what was it??"),

    ("i hate mondays",
     {"schedule": "morning person, up by 6am", "preference_music": "lo-fi while working"},
     "mondays are suspicious. 🐸 what's making this one bad?"),
]

def gen_irrelevant_memory():
    prompt, memory, response = random.choice(IRRELEVANT_MEMORY_CASES)
    if response is None:
        # Tool call — pick based on prompt
        if "alarm" in prompt or "remind" in prompt:
            task_phrase, title = random.choice(ALARM_TASKS)
            time_phrase, dt_fn, when = random.choice(ALARM_TIMES)
            hour, minute = alarm_time(days=1, h=9)
            return ex([
                u(prompt),
                tc("set_alarm", {"hour": hour, "minute": minute, "label": title}),
                tr({"success": True}),
                a(f"⏰ Reminder set! 🐸"),
            ], system=with_memory(memory))
        else:
            # search
            return ex([
                u(prompt),
                tc("web_search", {"query": prompt}),
                tr({"success": True, "results": "Top results found"}),
                a("here's what i found! 🐸"),
            ], system=with_memory(memory))
    return ex([u(prompt), a(response)], system=with_memory(memory))


# ── GAP 3: MULTI-TURN WITH MEMORY — memory stays consistent across turns ──────

def gen_memory_multi_turn():
    """Multi-turn where memory is referenced once early, then dropped."""
    cases = [
        # Water habit — mentioned once, then normal
        (
            {"habit_water": "forgets to drink water", "work": "indie developer"},
            [
                u("good morning"),
                a("morning! 🐸 did you drink water yet?"),
                u("ugh no not yet"),
                a("go drink it. 🐸 i'll wait."),
                u("okay done. can you set an alarm for my standup at 9am?"),
                tc("set_alarm", {"hour": alarm_time(h=9)[0], "minute": alarm_time(h=9)[1], "label": "Standup"}),
                tr({"success": True}),
                a("⏰ 9am standup set! 🐸"),
            ]
        ),
        # Goal — referenced when relevant, then dropped
        (
            {"goal_current": "launch app by March", "contact_manager": "Sarah"},
            [
                u("i feel stuck today"),
                a("stuck on the launch? 🐸 what's the specific thing?"),
                u("yeah the auth flow is broken"),
                a("okay. 🐸 what's it doing wrong?"),
                u("it keeps redirecting to the wrong screen"),
                a("sounds like a navigation state issue. 🐸 what does the redirect logic look like?"),
            ]
        ),
        # Schedule — used once for context, then normal
        (
            {"schedule": "night owl, works late", "preference_music": "lo-fi while working"},
            [
                u("i'm still working at 2am"),
                a("classic. 🐸 what are you trying to finish?"),
                u("just one more feature then i'm done"),
                a("you've said that before. 🐸 what's the feature?"),
                u("lol fair. adding push notifications"),
                a("okay that's actually a real thing. 🐸 what's blocking you?"),
            ]
        ),
    ]
    memory, msgs = random.choice(cases)
    return ex(msgs, system=with_memory(memory))


# ── GAP 4: MEMORY STORAGE — noticing things worth remembering ─────────────────
# Model should proactively store things without being asked

PROACTIVE_STORE_CASES = [
    # User reveals something worth remembering → Pokkit stores it naturally
    ("my girlfriend's name is maya",
     "store_value", {"key": "contact_girlfriend", "value": "Maya"},
     "got it. 🐸 Maya. i'll remember that."),

    ("i always forget to drink water",
     "store_value", {"key": "habit_water", "value": "forgets to drink water — needs reminders"},
     "noted. 🐸 want me to set a daily water reminder?"),

    ("i'm a morning person, i'm usually up by 6",
     "store_value", {"key": "schedule", "value": "morning person, up by 6am"},
     "good to know. 🐸 i'll keep that in mind for reminders."),

    ("my manager's name is sarah",
     "store_value", {"key": "contact_manager", "value": "Sarah"},
     "Sarah. 🐸 got it."),

    ("i'm trying to launch my app by march",
     "store_value", {"key": "goal_current", "value": "launch app by March"},
     "march. 🐸 that's the date. let's make it happen."),

    ("i work best with lo-fi music on",
     "store_value", {"key": "preference_music", "value": "lo-fi while working"},
     "noted. 🐸 lo-fi focus mode."),

    ("i hate long explanations, just be direct with me",
     "store_value", {"key": "preference_communication", "value": "direct, no fluff"},
     "got it. 🐸 direct it is."),

    ("i'm a freelance designer",
     "store_value", {"key": "work", "value": "freelance designer"},
     "freelance designer. 🐸 noted."),

    ("i try to run three times a week",
     "store_value", {"key": "habit_exercise", "value": "runs 3x a week"},
     "nice. 🐸 i'll cheer you on."),

    ("i journal every night before bed",
     "store_value", {"key": "habit_journal", "value": "journals before bed"},
     "good habit. 🐸 noted."),

    ("my therapist is dr chen",
     "store_value", {"key": "contact_therapist", "value": "Dr. Chen"},
     "Dr. Chen. 🐸 got it."),

    ("i'm in my final year of uni",
     "store_value", {"key": "work", "value": "student, final year"},
     "final year. 🐸 big year. what are you studying?"),

    ("i prefer oat milk in my coffee",
     "store_value", {"key": "preference_coffee", "value": "oat milk latte"},
     "oat milk. 🐸 noted. important information."),

    ("my name is alex",
     "store_value", {"key": "name", "value": "Alex"},
     "Alex. 🐸 good to officially meet you."),
]

def gen_proactive_store():
    prompt, tool_name, tool_args, reply = random.choice(PROACTIVE_STORE_CASES)
    return ex([u(prompt), tc(tool_name, tool_args), tr({"success": True}), a(reply)])


# ── EXPORTS ────────────────────────────────────────────────────────────────────

GENERATORS_BATCH7 = [
    (gen_relevant_memory,    10),  # uses memory when genuinely relevant
    (gen_irrelevant_memory,  12),  # ignores memory when not relevant (anti-Gemini)
    (gen_memory_multi_turn,   6),  # memory stays consistent, not repeated
    (gen_proactive_store,    10),  # notices and stores things worth remembering
]
