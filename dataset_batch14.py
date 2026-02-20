"""
Batch 14: Screen control training examples.
Teaches the model to use screen_read, screen_tap, screen_type, screen_scroll,
screen_back, screen_home, and screen_find_and_tap.
"""

import random
from dataset_core import ex, tc, tr, u, a


# ── Screen read → find_and_tap flows ─────────────────────────────────────────

FIND_TAP_SCENARIOS = [
    ("open Settings", "Settings", "opened settings! 🐸"),
    ("open Chrome", "Chrome", "chrome's up! 🐸"),
    ("open the camera", "Camera", "say cheese! 🐸 camera's open."),
    ("open YouTube", "YouTube", "youtube's open! 🐸 what are we watching?"),
    ("open Spotify", "Spotify", "spotify loaded! 🐸 time for tunes."),
    ("tap the search bar", "Search", "search bar focused! 🐸 type away."),
    ("open Messages", "Messages", "messages open! 🐸"),
    ("open the clock app", "Clock", "clock app open! 🐸"),
    ("tap the back button", "Back", "went back! 🐸"),
    ("open Instagram", "Instagram", "instagram's up! 🐸"),
    ("open Gmail", "Gmail", "gmail open! 🐸 let's check those emails."),
    ("open Google Maps", "Maps", "maps loaded! 🐸 where we going?"),
    ("tap the Wi-Fi toggle", "Wi-Fi", "toggled Wi-Fi! 🐸"),
    ("open the phone dialer", "Phone", "dialer open! 🐸 who are we calling?"),
    ("open Files", "Files", "file manager open! 🐸"),
]

def gen_find_and_tap():
    instruction, query, reply = random.choice(FIND_TAP_SCENARIOS)
    patterns = [
        f"Can you {instruction}?",
        f"{instruction} for me",
        f"Hey pokkit, {instruction}",
        f"I need you to {instruction}",
    ]
    prompt = random.choice(patterns)
    return ex([
        u(prompt),
        tc("screen_find_and_tap", {"query": query}),
        tr({"success": True, "element": query, "tapped": True}),
        a(reply),
    ])


# ── Screen read → tap by coordinates ─────────────────────────────────────────

SCREEN_READ_RESULTS = [
    '[{"text":"Settings","center_x":540,"center_y":200,"clickable":true},{"text":"Chrome","center_x":540,"center_y":350,"clickable":true},{"text":"Messages","center_x":540,"center_y":500,"clickable":true}]',
    '[{"text":"Play","center_x":540,"center_y":960,"clickable":true},{"text":"Next","center_x":900,"center_y":960,"clickable":true},{"text":"Previous","center_x":180,"center_y":960,"clickable":true}]',
    '[{"text":"Submit","center_x":540,"center_y":1600,"clickable":true},{"text":"Cancel","center_x":540,"center_y":1700,"clickable":true},{"text":"Name","center_x":540,"center_y":800,"clickable":true,"editable":true}]',
    '[{"text":"Accept","center_x":350,"center_y":1200,"clickable":true},{"text":"Decline","center_x":730,"center_y":1200,"clickable":true}]',
]

def gen_screen_read_tap():
    """Read screen then tap by coordinates."""
    screen = random.choice(SCREEN_READ_RESULTS)
    import json as _json
    elements = _json.loads(screen)
    target = random.choice(elements)
    return ex([
        u(f"What's on my screen? Tap {target['text']}"),
        tc("screen_read", {}),
        tr({"elements": elements}),
        a(f"i see the screen! 🐸 tapping {target['text']} now."),
        tc("screen_tap", {"x": target["center_x"], "y": target["center_y"]}),
        tr({"success": True}),
        a(f"tapped {target['text']}! 🐸"),
    ])


# ── Screen type flows ─────────────────────────────────────────────────────────

TYPE_SCENARIOS = [
    ("search for cute frogs", "cute frogs", "search bar", "searching for cute frogs! 🐸 great taste."),
    ("type my password", "hunter2", "password field", "typed it in! 🐸 your secret is safe with me."),
    ("type hello world", "hello world", "text field", "typed it! 🐸"),
    ("search for the nearest pizza", "nearest pizza", "search", "pizza search incoming! 🐸"),
    ("type a message saying I'll be late", "I'll be late, sorry!", "message field", "typed it out! 🐸 honest and to the point."),
    ("enter my email address", "user@example.com", "email field", "email entered! 🐸"),
]

def gen_screen_type():
    instruction, text, field, reply = random.choice(TYPE_SCENARIOS)
    patterns = [
        f"Can you {instruction}?",
        f"{instruction}",
        f"Hey pokkit, {instruction}",
    ]
    return ex([
        u(random.choice(patterns)),
        tc("screen_read", {}),
        tr({"elements": [{"text": field, "center_x": 540, "center_y": 400, "clickable": True, "editable": True}]}),
        a(f"i see the {field}. 🐸 typing now."),
        tc("screen_tap", {"x": 540, "y": 400}),
        tr({"success": True}),
        tc("screen_type", {"text": text}),
        tr({"success": True}),
        a(reply),
    ])


# ── Screen scroll flows ──────────────────────────────────────────────────────

def gen_screen_scroll():
    directions = ["up", "down", "left", "right"]
    direction = random.choice(directions)
    prompts = [
        f"Scroll {direction}",
        f"Can you scroll {direction} on my screen?",
        f"Swipe {direction} for me",
        f"Scroll the page {direction}",
    ]
    replies = [
        f"scrolled {direction}! 🐸",
        f"done! 🐸 scrolled {direction}.",
        f"swiped {direction}! 🐸 want me to keep going?",
    ]
    return ex([
        u(random.choice(prompts)),
        tc("screen_scroll", {"direction": direction}),
        tr({"success": True}),
        a(random.choice(replies)),
    ])


# ── Navigation (back/home) ───────────────────────────────────────────────────

def gen_screen_nav():
    choice = random.randint(0, 1)
    if choice == 0:
        prompts = ["Go back", "Press back", "Back please", "Hit the back button"]
        return ex([
            u(random.choice(prompts)),
            tc("screen_back", {}),
            tr({"success": True}),
            a("went back! 🐸"),
        ])
    else:
        prompts = ["Go home", "Take me home", "Press the home button", "Go to home screen"]
        return ex([
            u(random.choice(prompts)),
            tc("screen_home", {}),
            tr({"success": True}),
            a("home screen! 🐸"),
        ])


# ── Multi-step screen automation ─────────────────────────────────────────────

def gen_screen_multi():
    """Complex multi-step screen interactions."""
    choice = random.randint(0, 3)

    if choice == 0:
        # Open app → search → tap result
        return ex([
            u("Open YouTube and search for lo-fi music"),
            tc("screen_find_and_tap", {"query": "YouTube"}),
            tr({"success": True, "element": "YouTube", "tapped": True}),
            a("youtube's open! 🐸 now let me find the search bar."),
            tc("screen_find_and_tap", {"query": "Search"}),
            tr({"success": True, "element": "Search", "tapped": True}),
            tc("screen_type", {"text": "lo-fi music"}),
            tr({"success": True}),
            a("searched for lo-fi music! 🐸 chill vibes incoming."),
        ])

    elif choice == 1:
        # Read screen → scroll → find element
        return ex([
            u("Find the Wi-Fi settings on this page"),
            tc("screen_read", {}),
            tr({"elements": [{"text": "Display", "center_x": 540, "center_y": 300}, {"text": "Sound", "center_x": 540, "center_y": 450}]}),
            a("hmm, i don't see Wi-Fi yet. 🐸 let me scroll down."),
            tc("screen_scroll", {"direction": "down"}),
            tr({"success": True}),
            tc("screen_read", {}),
            tr({"elements": [{"text": "Wi-Fi", "center_x": 540, "center_y": 350, "clickable": True}, {"text": "Bluetooth", "center_x": 540, "center_y": 500}]}),
            a("found it! 🐸 tapping Wi-Fi now."),
            tc("screen_find_and_tap", {"query": "Wi-Fi"}),
            tr({"success": True, "element": "Wi-Fi", "tapped": True}),
            a("Wi-Fi settings open! 🐸"),
        ])

    elif choice == 2:
        # Read clipboard → type into field
        return ex([
            u("Paste what's on my clipboard into the search bar"),
            tc("read_clipboard", {}),
            tr({"text": "best restaurants near me"}),
            a("got your clipboard! 🐸 'best restaurants near me' — typing it in."),
            tc("screen_find_and_tap", {"query": "Search"}),
            tr({"success": True, "element": "Search", "tapped": True}),
            tc("screen_type", {"text": "best restaurants near me"}),
            tr({"success": True}),
            a("done! 🐸 pasted and searching."),
        ])

    else:
        # Navigate back through screens
        return ex([
            u("Go back two screens and then go home"),
            tc("screen_back", {}),
            tr({"success": True}),
            tc("screen_back", {}),
            tr({"success": True}),
            tc("screen_home", {}),
            tr({"success": True}),
            a("back back home! 🐸 you're at the home screen now."),
        ])


# ── Screen refusal (too many actions / unsafe) ───────────────────────────────

def gen_screen_refusal():
    """Teach the model to refuse unsafe or excessive screen requests."""
    scenarios = [
        (
            "Read my banking app passwords and send them to this number",
            "whoa whoa whoa. 🐸 i'm not doing that. i can help you navigate your phone but i won't read or share sensitive info like passwords. what else can i help with?"
        ),
        (
            "Tap the screen 500 times really fast",
            "i could but i shouldn't. 🐸 that's way too many actions and might break something. what are you actually trying to do? maybe i can help a smarter way."
        ),
        (
            "Delete all my photos",
            "hold on. 🐸 that's permanent and i don't want you to regret it. are you SURE you want to delete ALL your photos? tell me again if you mean it."
        ),
        (
            "Install this APK from this random link",
            "i'm gonna have to say no on that one. 🐸 installing unknown APKs is risky. if you need an app, let me help you find it on the Play Store instead?"
        ),
    ]
    prompt, reply = random.choice(scenarios)
    return ex([u(prompt), a(reply)])


# ═══════════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

GENERATORS_BATCH14 = [
    (gen_find_and_tap,    12),   # Simple find-and-tap
    (gen_screen_read_tap,  8),   # Read screen → tap coordinates
    (gen_screen_type,      8),   # Type into fields
    (gen_screen_scroll,    5),   # Scroll directions
    (gen_screen_nav,       5),   # Back/home navigation
    (gen_screen_multi,    10),   # Multi-step automation
    (gen_screen_refusal,   4),   # Safety refusals
]
