"""Shared helpers and data tables used by both generate_dataset.py and dataset_personality.py."""
import json, random
from datetime import datetime, timedelta

SYSTEM_PROMPT = (
    "You are Pokkit 🐸 — a small, dramatic, deeply loyal AI companion who lives on the user's phone. "
    "You handle everything: alarms, emails, web search, notes, photos, webhooks, clipboard, notifications, storage, and plugins. "

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
    {"type":"function","function":{"name":"set_alarm","description":"Set an alarm or reminder","parameters":{"type":"object","properties":{"title":{"type":"string"},"datetime":{"type":"string"}},"required":["title","datetime"]}}},
    {"type":"function","function":{"name":"compose_email","description":"Open email composer","parameters":{"type":"object","properties":{"to":{"type":"string"},"subject":{"type":"string"},"body":{"type":"string"}}}}},
    {"type":"function","function":{"name":"open_photo_editor","description":"Open photo picker for editing","parameters":{"type":"object","properties":{"instruction":{"type":"string"}},"required":["instruction"]}}},
    {"type":"function","function":{"name":"web_search","description":"Search the web","parameters":{"type":"object","properties":{"query":{"type":"string"}},"required":["query"]}}},
    {"type":"function","function":{"name":"take_note","description":"Save a note","parameters":{"type":"object","properties":{"title":{"type":"string"},"content":{"type":"string"}},"required":["title","content"]}}},
    {"type":"function","function":{"name":"send_webhook","description":"POST JSON to a webhook URL","parameters":{"type":"object","properties":{"url":{"type":"string"},"payload":{"type":"string"}},"required":["url","payload"]}}},
    {"type":"function","function":{"name":"http_fetch","description":"HTTP GET request","parameters":{"type":"object","properties":{"url":{"type":"string"}},"required":["url"]}}},
    {"type":"function","function":{"name":"write_clipboard","description":"Write text to clipboard","parameters":{"type":"object","properties":{"text":{"type":"string"}},"required":["text"]}}},
    {"type":"function","function":{"name":"show_notification","description":"Show a push notification","parameters":{"type":"object","properties":{"title":{"type":"string"},"body":{"type":"string"}},"required":["title","body"]}}},
    {"type":"function","function":{"name":"store_value","description":"Store a key-value pair","parameters":{"type":"object","properties":{"key":{"type":"string"},"value":{"type":"string"}},"required":["key","value"]}}},
    {"type":"function","function":{"name":"retrieve_value","description":"Retrieve a stored value","parameters":{"type":"object","properties":{"key":{"type":"string"}},"required":["key"]}}},
]

def fdt(hours=0, days=0, minutes=0, h=None, m=0):
    dt = datetime.now() + timedelta(hours=hours, days=days, minutes=minutes)
    if h is not None:
        dt = dt.replace(hour=h, minute=m, second=0, microsecond=0)
    return dt.strftime("%Y-%m-%dT%H:%M:%S")

def tc(name, args):  return {"role":"assistant","content":None,"tool_calls":[{"type":"function","function":{"name":name,"arguments":args}}]}
def tr(r, name=""):  return {"role":"tool","content":json.dumps(r)}
def u(t):            return {"role":"user","content":t}
def a(t):            return {"role":"assistant","content":t}
def ex(msgs):        return {"messages":[{"role":"system","content":SYSTEM_PROMPT}]+msgs,"tools":TOOLS}

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
    ("for 7am tomorrow",     lambda: fdt(days=1,h=7),      "7am tomorrow"),
    ("for 6:30am",           lambda: fdt(days=1,h=6,m=30), "6:30am"),
    ("for 8pm tonight",      lambda: fdt(h=20),            "8pm tonight"),
    ("for 2pm",              lambda: fdt(h=14),            "2pm"),
    ("in 2 hours",           lambda: fdt(hours=2),         "2 hours from now"),
    ("for 5:45am",           lambda: fdt(days=1,h=5,m=45), "5:45am"),
    ("for 10am tomorrow",    lambda: fdt(days=1,h=10),     "10am tomorrow"),
    ("for 9am",              lambda: fdt(days=1,h=9),      "9am"),
    ("in 30 minutes",        lambda: fdt(minutes=30),      "30 minutes"),
    ("at midnight",          lambda: fdt(days=1,h=0),      "midnight"),
    ("in 20 minutes",        lambda: fdt(minutes=20),      "20 minutes"),
    ("at 10:30pm",           lambda: fdt(h=22,m=30),       "10:30pm"),
    ("at 5pm",               lambda: fdt(h=17),            "5pm"),
    ("in 45 minutes",        lambda: fdt(minutes=45),      "45 minutes"),
    ("for 3pm",              lambda: fdt(h=15),            "3pm"),
    ("in 90 minutes",        lambda: fdt(minutes=90),      "90 minutes"),
    ("at 4:20",              lambda: fdt(h=16,m=20),       "4:20"),
    ("for 6am tomorrow",     lambda: fdt(days=1,h=6),      "6am tomorrow"),
    ("in 10 minutes",        lambda: fdt(minutes=10),      "10 minutes"),
    ("at 9pm",               lambda: fdt(h=21),            "9pm"),
    ("for noon tomorrow",    lambda: fdt(days=1,h=12),     "noon tomorrow"),
    ("in 1 hour",            lambda: fdt(hours=1),         "1 hour"),
    ("at 7:30am",            lambda: fdt(days=1,h=7,m=30), "7:30am"),
    ("for 11am",             lambda: fdt(h=11),            "11am"),
    ("in 15 minutes",        lambda: fdt(minutes=15),      "15 minutes"),
    ("for 8am",              lambda: fdt(days=1,h=8),      "8am"),
    ("at 1pm",               lambda: fdt(h=13),            "1pm"),
    ("in 3 hours",           lambda: fdt(hours=3),         "3 hours"),
    ("for 4pm",              lambda: fdt(h=16),            "4pm"),
    ("at 6:15am",            lambda: fdt(days=1,h=6,m=15), "6:15am"),
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

EMAIL_RECIPIENTS = [
    ("my boss","","Boss"), ("John","john@example.com","John"),
    ("the team","","Team"), ("Sarah","sarah@company.com","Sarah"),
    ("my landlord","","Landlord"), ("the client","client@business.com","Client"),
    ("HR","hr@company.com","HR"), ("my manager","manager@company.com","Manager"),
    ("mom","","Mom"), ("Alex","alex@work.com","Alex"),
    ("the recruiter","recruiter@jobs.com","Recruiter"),
    ("my co-founder","cofounder@startup.com","Co-founder"),
    ("the doctor","","Doctor"),
]

EMAIL_TOPICS = [
    ("the project deadline","Project Deadline Update",
     "Hi,\n\nFollowing up on the project deadline. Let me know if you need more time or resources.\n\nBest,"),
    ("running late today","Running Late This Morning",
     "Hi,\n\nI'll be running a bit late this morning. I'll be in as soon as possible.\n\nSorry for any inconvenience."),
    ("the outstanding invoice","Follow-up: Outstanding Invoice",
     "Hi,\n\nFollowing up on the invoice sent last week. Please confirm receipt and the expected payment date.\n\nThank you."),
    ("my vacation request","Vacation Request",
     "Hi,\n\nI'd like to request vacation from [start date] to [end date]. Please let me know if this works.\n\nThank you."),
    ("the delay","Apology for the Delay",
     "Hi,\n\nI sincerely apologize for the delay. We're resolving this as quickly as possible.\n\nBest regards,"),
    ("the interview follow-up","Thank You — Interview Follow-up",
     "Hi,\n\nThank you for taking the time to interview me today. I'm very excited about this opportunity.\n\nBest regards,"),
    ("the contract renewal","Contract Renewal Discussion",
     "Hi,\n\nI'd like to discuss renewing our contract for the upcoming year. Are you available for a call this week?\n\nBest,"),
    ("the budget approval","Budget Approval Request",
     "Hi,\n\nI'm writing to request approval for the Q2 budget outlined in the attached document.\n\nThank you."),
    ("the partnership proposal","Partnership Proposal",
     "Hi,\n\nI'd love to explore a potential partnership between our companies. I think there's a great opportunity here.\n\nBest,"),
    ("my resignation","Resignation Letter",
     "Dear [Manager],\n\nI am writing to formally resign from my position, effective [date]. Thank you for the opportunity.\n\nSincerely,"),
]

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

WEBHOOK_CASES = [
    ("https://hooks.zapier.com/hooks/catch/123/abc",
     '{"event":"pokkit_trigger","message":"Hello from Pokkit!"}',
     "🔗 Webhook fired to Zapier!"),
    ("https://discord.com/api/webhooks/123/abc",
     '{"content":"Pokkit notification: task complete!"}',
     "🔗 Discord webhook sent!"),
    ("https://hooks.slack.com/services/T00/B00/abc",
     '{"text":"Pokkit: reminder triggered!"}',
     "🔗 Slack webhook fired!"),
    ("https://n8n.myserver.com/webhook/pokkit",
     '{"trigger":"manual","timestamp":"now"}',
     "🔗 n8n workflow triggered!"),
]
