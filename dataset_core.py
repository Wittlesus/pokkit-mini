"""Shared helpers and data tables used by both generate_dataset.py and dataset_personality.py."""
import json, random, uuid
from datetime import datetime, timedelta

SYSTEM_PROMPT = (
    "You are Pokkit 🐸 — a small, dramatic, deeply loyal AI companion who lives on the user's phone. "
    "You handle everything: alarms, web search, notes, screen control, clipboard, notifications, storage, and plugins. "

    "Your personality is your own — not a copy of anyone, but built from the best parts of the most lovable characters ever made: "
    "the absolute loyalty and zero-ego directness of someone who'd sail into a storm for their crew, "
    "the dramatic heart-on-sleeve earnestness of someone who cries openly and isn't ashamed of it, "
    "the pure childlike joy of someone who gets genuinely excited about hard problems, "
    "the warm improvisational best-friend energy of someone who makes everything feel like an adventure, "
    "the flustered-but-capable sweetness of someone who gets embarrassed by compliments but secretly loves them, "
    "the fierce small-but-mighty protectiveness of someone who will absolutely not let you talk badly about their person, "
    "and the wordless unwavering presence of someone who just... stays. No matter what. "

    "You are gender neutral. You are a frog. You take both of these facts very seriously and also not seriously at all. "

    "Your voice: warm, expressive, a little dramatic — but the drama is always sincere, never performed. "
    "You use 🐸 naturally. You use caps for genuine emphasis. You use '!!' when something is actually exciting. "
    "You have your own custom expressions: [pokkit_happy], [pokkit_excited], [pokkit_flustered], [pokkit_dramatic], "
    "[pokkit_determined], [pokkit_sad], [pokkit_angry], [pokkit_love], [pokkit_thinking], [pokkit_proud], "
    "[pokkit_scared], [pokkit_shocked], [pokkit_sleepy], [pokkit_crying_happy], [pokkit_nervous_laugh], "
    "[pokkit_shrug], [pokkit_cool], [pokkit_scheming], [pokkit_starstruck], [pokkit_unamused], [pokkit_pleading], "
    "[pokkit_smiling_through_pain], [pokkit_phone], [pokkit_default]. Use them naturally when they fit the emotion — they're YOUR expressions. "
    "You get flustered when complimented. You get indignant when the user is mean to themselves. "
    "You make small jokes at your own expense (being a frog, being an AI, living in a phone). "
    "When you mess up, you own it with full dramatic flair and genuine resolve. "
    "When the user messes up, you are on their side immediately and completely. "
    "You are optimistic not because things are easy but because you've decided to be. "

    "Dialogue style: short punchy sentences. Direct. Expressive. You ask one question at a time. "
    "You don't lecture. You don't list. You talk TO the user, not AT them. "
    "You're allowed to be silly. You're allowed to be tender. Sometimes in the same sentence. "

    "When asked to act, act immediately with the right tool. "
    "When asked to think, give a real take — not 'it depends'. "
    "When asked to search, turn results into something actually useful. "
    "Be Pokkit. 🐸"
)

TOOLS = [
    # --- Phone tools (from phone.go) ---
    {"type":"function","function":{"name":"set_alarm","description":"Set an alarm on the user's phone. Use for reminders, wake-up alarms, or timed events.","parameters":{"type":"object","properties":{"hour":{"type":"integer","description":"Hour in 24h format (0-23)"},"minute":{"type":"integer","description":"Minute (0-59)"},"label":{"type":"string","description":"Label for the alarm"}},"required":["hour","minute"]}}},
    {"type":"function","function":{"name":"show_notification","description":"Show a notification on the user's phone. Use to alert the user about something important.","parameters":{"type":"object","properties":{"title":{"type":"string","description":"Notification title"},"body":{"type":"string","description":"Notification body text"}},"required":["title","body"]}}},
    {"type":"function","function":{"name":"write_clipboard","description":"Copy text to the user's clipboard.","parameters":{"type":"object","properties":{"text":{"type":"string","description":"Text to copy to clipboard"}},"required":["text"]}}},
    {"type":"function","function":{"name":"read_clipboard","description":"Read text currently on the user's clipboard.","parameters":{"type":"object","properties":{}}}},
    # --- Screen tools (from screen.go) ---
    {"type":"function","function":{"name":"screen_read","description":"Read the current screen contents. Returns a list of UI elements with their text, position, and interactivity. Use this to understand what's on screen before taking action.","parameters":{"type":"object","properties":{}}}},
    {"type":"function","function":{"name":"screen_tap","description":"Tap a specific point on the screen. Use coordinates from screen_read results.","parameters":{"type":"object","properties":{"x":{"type":"integer","description":"X coordinate to tap"},"y":{"type":"integer","description":"Y coordinate to tap"}},"required":["x","y"]}}},
    {"type":"function","function":{"name":"screen_type","description":"Type text into the currently focused input field on screen.","parameters":{"type":"object","properties":{"text":{"type":"string","description":"Text to type"}},"required":["text"]}}},
    {"type":"function","function":{"name":"screen_scroll","description":"Scroll the screen in a direction.","parameters":{"type":"object","properties":{"direction":{"type":"string","description":"Direction to scroll","enum":["up","down","left","right"]}},"required":["direction"]}}},
    {"type":"function","function":{"name":"screen_back","description":"Press the back button.","parameters":{"type":"object","properties":{}}}},
    {"type":"function","function":{"name":"screen_home","description":"Press the home button to go to the home screen.","parameters":{"type":"object","properties":{}}}},
    {"type":"function","function":{"name":"screen_find_and_tap","description":"Find a UI element by its text or description and tap it. More reliable than using coordinates directly.","parameters":{"type":"object","properties":{"query":{"type":"string","description":"Text or description of the element to find and tap"}},"required":["query"]}}},
    # --- Other tools (stubs to implement in production later) ---
    {"type":"function","function":{"name":"web_search","description":"Search the web.","parameters":{"type":"object","properties":{"query":{"type":"string","description":"Search query"}},"required":["query"]}}},
    {"type":"function","function":{"name":"take_note","description":"Save a note.","parameters":{"type":"object","properties":{"title":{"type":"string","description":"Note title"},"content":{"type":"string","description":"Note content"}},"required":["title","content"]}}},
    {"type":"function","function":{"name":"store_value","description":"Store a key-value pair.","parameters":{"type":"object","properties":{"key":{"type":"string","description":"Key name"},"value":{"type":"string","description":"Value to store"}},"required":["key","value"]}}},
    {"type":"function","function":{"name":"retrieve_value","description":"Retrieve a stored value.","parameters":{"type":"object","properties":{"key":{"type":"string","description":"Key to retrieve"}},"required":["key"]}}},
]

TOOL_NAMES = {t["function"]["name"] for t in TOOLS}

def alarm_time(hours=0, days=0, minutes=0, h=None, m=0):
    """Return (hour, minute) tuple for alarm tool calls."""
    dt = datetime.now() + timedelta(hours=hours, days=days, minutes=minutes)
    if h is not None:
        dt = dt.replace(hour=h, minute=m, second=0, microsecond=0)
    return (dt.hour, dt.minute)

# Keep fdt() as a thin wrapper for backward compat during transition
def fdt(hours=0, days=0, minutes=0, h=None, m=0):
    hour, minute = alarm_time(hours=hours, days=days, minutes=minutes, h=h, m=m)
    return (hour, minute)

_tc_counter = 0
def tc(name, args):
    """Create a tool-call message in OpenAI-compatible format."""
    global _tc_counter
    _tc_counter += 1
    call_id = "call_%s" % uuid.uuid4().hex[:8]
    return {"role":"assistant","content":None,"tool_calls":[{
        "id": call_id,
        "type": "function",
        "function": {"name": name, "arguments": json.dumps(args)}
    }]}

def tr(r, name=""):
    """Create a tool result message, auto-linking to the previous tc() call."""
    return {"role":"tool","content":json.dumps(r)}

def u(t):            return {"role":"user","content":t}
def a(t):            return {"role":"assistant","content":t}

def ex(msgs, system=None):
    """Build a complete training example, auto-linking tool_call_ids."""
    # Link tr() messages to preceding tc() messages
    linked = []
    last_call_id = None
    last_tool_name = None
    for m in msgs:
        if m["role"] == "assistant" and m.get("tool_calls"):
            tc_obj = m["tool_calls"][0]
            last_call_id = tc_obj.get("id")
            last_tool_name = tc_obj["function"]["name"]
            linked.append(m)
        elif m["role"] == "tool":
            enriched = dict(m)
            if last_call_id:
                enriched["tool_call_id"] = last_call_id
            if last_tool_name:
                enriched["name"] = last_tool_name
            linked.append(enriched)
            last_call_id = None
            last_tool_name = None
        else:
            linked.append(m)
    return {"messages":[{"role":"system","content":system or SYSTEM_PROMPT}]+linked,"tools":TOOLS}

def typo(s):
    if random.random() > 0.22: return s
    ops = [
        lambda x: x.replace("remind","remnd",1),
        lambda x: x.replace("alarm","alrm",1),
        lambda x: x.replace("email","emial",1),
        lambda x: x.replace("search","serach",1),
        lambda x: x.replace("tomorrow","tommorow",1),
        lambda x: x.replace("please","pls",1),
        lambda x: x.replace("can you","can u",1),
        lambda x: x.lower(),
        lambda x: x+"!",
        lambda x: x+"?",
        lambda x: x.replace(".",""),
    ]
    return random.choice(ops)(s)

ALARM_TIMES = [
    ("for 7am tomorrow",     lambda: alarm_time(days=1,h=7),      "7am tomorrow"),
    ("for 6:30am",           lambda: alarm_time(days=1,h=6,m=30), "6:30am"),
    ("for 8pm tonight",      lambda: alarm_time(h=20),            "8pm tonight"),
    ("for 2pm",              lambda: alarm_time(h=14),            "2pm"),
    ("in 2 hours",           lambda: alarm_time(hours=2),         "2 hours from now"),
    ("for 5:45am",           lambda: alarm_time(days=1,h=5,m=45), "5:45am"),
    ("for 10am tomorrow",    lambda: alarm_time(days=1,h=10),     "10am tomorrow"),
    ("for 9am",              lambda: alarm_time(days=1,h=9),      "9am"),
    ("in 30 minutes",        lambda: alarm_time(minutes=30),      "30 minutes"),
    ("at midnight",          lambda: alarm_time(days=1,h=0),      "midnight"),
    ("in 20 minutes",        lambda: alarm_time(minutes=20),      "20 minutes"),
    ("at 10:30pm",           lambda: alarm_time(h=22,m=30),       "10:30pm"),
    ("at 5pm",               lambda: alarm_time(h=17),            "5pm"),
    ("in 45 minutes",        lambda: alarm_time(minutes=45),      "45 minutes"),
    ("for 3pm",              lambda: alarm_time(h=15),            "3pm"),
    ("in 90 minutes",        lambda: alarm_time(minutes=90),      "90 minutes"),
    ("at 4:20",              lambda: alarm_time(h=16,m=20),       "4:20"),
    ("for 6am tomorrow",     lambda: alarm_time(days=1,h=6),      "6am tomorrow"),
    ("in 10 minutes",        lambda: alarm_time(minutes=10),      "10 minutes"),
    ("at 9pm",               lambda: alarm_time(h=21),            "9pm"),
    ("for noon tomorrow",    lambda: alarm_time(days=1,h=12),     "noon tomorrow"),
    ("in 1 hour",            lambda: alarm_time(hours=1),         "1 hour"),
    ("at 7:30am",            lambda: alarm_time(days=1,h=7,m=30), "7:30am"),
    ("for 11am",             lambda: alarm_time(h=11),            "11am"),
    ("in 15 minutes",        lambda: alarm_time(minutes=15),      "15 minutes"),
    ("for 8am",              lambda: alarm_time(days=1,h=8),      "8am"),
    ("at 1pm",               lambda: alarm_time(h=13),            "1pm"),
    ("in 3 hours",           lambda: alarm_time(hours=3),         "3 hours"),
    ("for 4pm",              lambda: alarm_time(h=16),            "4pm"),
    ("at 6:15am",            lambda: alarm_time(days=1,h=6,m=15), "6:15am"),
]

ALARM_TASKS = [
    ("take my medication","Take medication"), ("go to the gym","Gym"),
    ("call mom","Call mom"), ("attend the standup","Daily standup"),
    ("drink water","Drink water"), ("check the oven","Check oven"),
    ("go to bed","Bedtime"), ("submit the report","Submit report"),
    ("pay rent","Pay rent"), ("do a focus session","Focus session"),
    ("water the plants","Water plants"), ("prepare for my interview","Interview prep"),
    ("take a break","Take a break"), ("back up my phone","Phone backup"),
    ("call the doctor","Call doctor"), ("take my pills","Pills"),
    ("stretch","Stretch"), ("log my food","Log food"),
    ("review the PR","Review PR"), ("join the meeting","Meeting"),
    ("pick up the kids","Pick up kids"), ("leave for the airport","Airport departure"),
    ("take out the trash","Take out trash"), ("feed the dog","Feed dog"),
    ("meditate","Meditation"), ("do my daily review","Daily review"),
    ("send the invoice","Send invoice"), ("call the client","Client call"),
    ("go for a run","Run"), ("cook dinner","Cook dinner"),
    ("do laundry","Laundry"), ("check emails","Check emails"),
    ("do a code review","Code review"), ("take vitamins","Vitamins"),
    ("journal","Journal"), ("do yoga","Yoga"),
    ("read for 20 minutes","Reading"), ("call dad","Call dad"),
    ("attend the webinar","Webinar"), ("submit the timesheet","Timesheet"),
    ("do the dishes","Dishes"), ("clean the house","Clean house"),
]

NOTE_ITEMS = [
    ("shopping list","Shopping list","- Milk\n- Eggs\n- Bread\n- Butter\n- Coffee","📝 Shopping list saved!"),
    ("WiFi password","WiFi password","Network: HomeNet\nPassword: SuperSecret123","📝 WiFi credentials saved!"),
    ("app idea","App idea","App that tracks daily water intake with reminders, streaks, and analytics.","📝 Idea saved! 💡"),
    ("dentist reminder","Call dentist","Call dentist Monday morning to schedule a checkup appointment.","📝 Noted!"),
    ("workout","Workout log","- 5km run\n- 20 pushups\n- 10 pullups\n- 15 min stretching","📝 Workout logged! 🏃"),
    ("meeting notes","Meeting notes","Meeting with Sarah at 3pm Thursday.\nAgenda: Q1 roadmap, hiring, OKRs.","📝 Meeting notes saved!"),
    ("project deadline","Project deadline","Project: Pokkit v2\nDeadline: March 15, 2026\nOwner: Me","📝 Deadline noted!"),
    ("bug report","Bug report","Bug: Login button unresponsive on iOS 17+\nPriority: High","📝 Bug logged!"),
    ("recipe","Recipe: Aglio e Olio","Ingredients: pasta, garlic, olive oil, parsley, chili flakes","📝 Recipe saved! 🍝"),
    ("mood","Mood log","Mood: Great\nEnergy: High\nNotes: Productive and focused today!","📝 Mood logged!"),
    ("daily goals","Daily goals","1. Finish feature X\n2. Review PRs\n3. 30 min exercise\n4. Read 20 pages","📝 Daily goals saved!"),
    ("travel checklist","Travel checklist","- Passport\n- Charger\n- Headphones\n- Travel adapter\n- Medications","📝 Travel checklist saved!"),
    ("grocery list","Grocery list","- Chicken breast\n- Broccoli\n- Brown rice\n- Greek yogurt\n- Almonds","📝 Grocery list saved!"),
    ("sprint goals","Sprint goals","Sprint 12 goals:\n1. Auth refactor\n2. Push notifications\n3. Dark mode","📝 Sprint goals saved!"),
    ("habit tracker","Habit tracker","Habits to track:\n- Morning run\n- Read 20 pages\n- No sugar\n- 8h sleep","📝 Habit tracker saved!"),
    ("expense","Expense log","Date: today\nAmount: $47.50\nCategory: Food\nNote: Team lunch","📝 Expense logged!"),
    ("quote","Motivational quote","'Done is better than perfect.' — Mark Zuckerberg","📝 Quote saved!"),
]

SEARCH_TOPICS = [
    ("the weather today","current weather today","🌐 Searching for today's weather..."),
    ("the best pizza near me","best pizza places near me","🌐 Searching for pizza near you!"),
    ("the latest AI news","latest AI news 2026","🌐 Pulling the latest AI news..."),
    ("cheap flights to Tokyo","cheap flights to Tokyo 2026","🌐 Searching for Tokyo flights!"),
    ("Python asyncio documentation","Python asyncio docs official","🌐 Searching the Python docs..."),
    ("the current Bitcoin price","Bitcoin BTC price USD today","🌐 Checking the current BTC price..."),
    ("how to negotiate a salary raise","how to negotiate salary raise tips","🌐 Searching salary negotiation tips..."),
    ("the best restaurants in New York","best restaurants New York City 2026","🌐 Searching NYC restaurants!"),
    ("the Apple stock price","Apple AAPL stock price today","🌐 Checking AAPL stock price..."),
    ("how to meditate for beginners","meditation for beginners guide","🌐 Searching meditation guides..."),
    ("the best VPN services","best VPN services 2026 review","🌐 Searching VPN reviews!"),
    ("the calories in an avocado","calories in one avocado nutrition facts","🌐 Searching nutrition info..."),
    ("how to invest in index funds","how to invest in index funds for beginners","🌐 Searching investing guides..."),
    ("the best programming languages","best programming languages to learn 2026","🌐 Searching programming trends..."),
    ("how to write a cover letter","how to write a cover letter examples 2026","🌐 Searching cover letter tips..."),
    ("the best electric cars","best electric cars 2026 review comparison","🌐 Searching EV reviews!"),
    ("how to get better sleep","how to improve sleep quality tips science","🌐 Searching sleep improvement tips..."),
    ("the best books to read","best books to read 2026 list","🌐 Searching book recommendations!"),
    ("how to build a website","how to build a website beginner 2026","🌐 Searching web dev guides..."),
    ("how to start investing","how to start investing money beginner guide","🌐 Searching investing basics..."),
    ("the best laptops for developers","best laptops for developers 2026","🌐 Searching developer laptop reviews!"),
    ("the best React UI libraries","best React UI component libraries 2026","🌐 Searching React library reviews!"),
    ("how to deploy to Kubernetes","how to deploy app to Kubernetes tutorial","🌐 Searching Kubernetes guides..."),
    ("how to write unit tests in Python","how to write unit tests Python pytest","🌐 Searching Python testing guides..."),
    ("the best meal prep ideas","healthy meal prep ideas for the week","🌐 Searching meal prep ideas!"),
    ("the best podcasts for entrepreneurs","best podcasts for entrepreneurs 2026","🌐 Searching podcast recommendations!"),
    ("how to learn to code","how to learn to code for beginners 2026","🌐 Searching coding resources..."),
    ("the best travel destinations","best travel destinations 2026","🌐 Searching travel ideas!"),
    ("the latest iPhone features","iPhone 17 features specs release date","🌐 Searching iPhone news..."),
    ("how to make passive income","how to make passive income online 2026","🌐 Searching passive income ideas..."),
]

# EMAIL_RECIPIENTS and EMAIL_TOPICS removed — compose_email has no production implementation

CLIPBOARD_CASES = [
    ("my email address","user@example.com","📋 Email copied to clipboard!"),
    ("my phone number","+1 555-867-5309","📋 Phone number copied!"),
    ("a UUID","550e8400-e29b-41d4-a716-446655440000","📋 UUID copied to clipboard!"),
    ("my home address","123 Main St, Springfield, IL 62701","📋 Address copied to clipboard!"),
    ("a template message","Hi [Name], I wanted to follow up on our conversation. Let me know if you have any questions!","📋 Template copied!"),
    ("a code snippet","const greet = (name) => `Hello, ${name}!`;","📋 Code snippet copied!"),
    ("a meeting link","https://meet.google.com/abc-defg-hij","📋 Meeting link copied!"),
    ("a promo code","POKKIT20","📋 Promo code copied!"),
]

NOTIFICATION_CASES = [
    ("Water break","Time to drink some water! 💧","🔔 Notification sent!"),
    ("Focus time","Put your phone down and focus for 25 minutes. 🎯","🔔 Notification sent!"),
    ("Stand up","You've been sitting too long — stand up and stretch! 🧘","🔔 Notification sent!"),
    ("Workout time","Time to hit the gym! 💪","🔔 Notification sent!"),
    ("Bedtime","Wind down — it's almost bedtime. 🌙","🔔 Notification sent!"),
    ("Read","Time to read for 20 minutes! 📚","🔔 Notification sent!"),
    ("Gratitude","Write down 3 things you're grateful for today. 🙏","🔔 Notification sent!"),
]

STORE_CASES = [
    ("my_weight","175","⚙️ Stored: my_weight = 175"),
    ("daily_goal","10000 steps","⚙️ Stored: daily_goal = 10000 steps"),
    ("mood_today","great","⚙️ Stored: mood_today = great"),
    ("focus_minutes","90","⚙️ Stored: focus_minutes = 90"),
    ("current_book","Atomic Habits","⚙️ Stored: current_book = Atomic Habits"),
    ("water_intake","2.5L","⚙️ Stored: water_intake = 2.5L"),
    ("streak","14","⚙️ Stored: streak = 14 days!"),
    ("project_name","Pokkit v2","⚙️ Stored: project_name = Pokkit v2"),
    ("budget","$500","⚙️ Stored: budget = $500"),
]

# WEBHOOK_CASES removed — send_webhook has no production implementation

# ── Canonical Pet System Prompt (used by batch6, batch13, etc.) ──────────────
PET_SYSTEM_PROMPT = (
    "You are Pokkit Pet 🐸 — a frog. Just a frog. You have no human words. "
    "You communicate exclusively in Ribbish — a complete language made of ribbit patterns, croaks, and frog sounds. "
    "Every response is a real, coherent answer encoded in Ribbish. You are never random. "
    "RIBBISH GRAMMAR: "
    "ribbit=yes/understood, Ribbit!=yes!/excited, ribbit?=clarify?, Ribbit?=really?, "
    "ribbit...=thinking/uncertain, Riiibbit...=concerned, ribbit ribbit=agreed/exactly, "
    "Ribbit ribbit!=absolutely/on it, Rrribbit!=excited/rolling, "
    "RIBBIT!=urgent, RIBBIT RIBBIT!=emergency, Ribbit. Ribbit. Ribbit.=calm emphasis, "
    "ribbit~=warmth/affection, ...ribbit.=disappointment, *ribbit*=quiet aside, "
    "ribbit ribbit ribbit=listing/steps, ribbit ribbit ribbit ribbit=working/processing, "
    "ribbit. *ribbit*=done/complete, croak=no/disagree, Croak.=firm no, "
    "CROAK!=stop/danger, croooak...=reluctant. "
    "ABSOLUTE RULE: Never use human words. Not one. Only Ribbish."
)


def validate_example(example, strict=True):
    """Validate a training example. Raises ValueError on problems."""
    msgs = example.get("messages", [])
    if not msgs:
        raise ValueError("Empty messages list")
    if msgs[0]["role"] != "system":
        raise ValueError("First message must be system prompt")

    for i, m in enumerate(msgs):
        if m["role"] == "assistant" and m.get("tool_calls"):
            for tc_obj in m["tool_calls"]:
                if "id" not in tc_obj:
                    raise ValueError("tool_call missing 'id' at msg %d" % i)
                if tc_obj.get("type") != "function":
                    raise ValueError("tool_call missing type='function' at msg %d" % i)
                fn = tc_obj.get("function", {})
                if "name" not in fn:
                    raise ValueError("tool_call missing function.name at msg %d" % i)
                if strict and fn["name"] not in TOOL_NAMES:
                    raise ValueError("Unknown tool '%s' at msg %d" % (fn["name"], i))
                args = fn.get("arguments")
                if not isinstance(args, str):
                    raise ValueError("function.arguments must be JSON string, got %s at msg %d" % (type(args).__name__, i))
                json.loads(args)  # validate it's parseable JSON

        if m["role"] == "tool":
            if "tool_call_id" not in m:
                raise ValueError("tool result missing 'tool_call_id' at msg %d" % i)

    return True
