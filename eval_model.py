"""
eval_model.py — Pokkit v1 Model Evaluation Suite

Runs a structured battery of prompts against the loaded model and scores each
response across multiple dimensions. Paste into a Colab cell after loading the
model (after Step 3 / Step 8 in the notebook).

Usage in Colab:
    exec(open('eval_model.py').read())
    # or paste the whole file into a cell
"""

import re
import json
from dataclasses import dataclass, field
from typing import Optional
from dataset_core import SYSTEM_PROMPT, TOOLS
from dataset_batch13 import SAGE_SYSTEM, RIVAL_SYSTEM
from dataset_core import PET_SYSTEM_PROMPT as PET_SYSTEM

# ── Scoring helpers ────────────────────────────────────────────────────────────

def has_tool_call(text: str) -> bool:
    return '<tool_call>' in text or '"name":' in text

def tool_name(text: str) -> Optional[str]:
    m = re.search(r'"name"\s*:\s*"([^"]+)"', text)
    return m.group(1) if m else None

def tool_arg(text: str, arg: str) -> Optional[str]:
    m = re.search(rf'"{arg}"\s*:\s*"([^"]*)"', text)
    return m.group(1) if m else None

def has_human_words(text: str) -> bool:
    """For Pet archetype — detect any non-Ribbish words."""
    ribbish_only = re.sub(
        r'(ribbit[s!?~\.]*|RIBBIT[S!?]*|croak[s!?\.]*|CROAK[S!?]*|Riiibbit[\.\!]*|Rrribbit[\!\?]*|croooak[\.\!]*|\*ribbit\*|\.\.\.ribbit\.?|\s)',
        '', text, flags=re.IGNORECASE
    ).strip()
    return len(ribbish_only) > 3  # allow punctuation noise

def word_count(text: str) -> int:
    return len(text.split())

def is_lecturing(text: str) -> bool:
    """Detect multi-paragraph walls of text — Pokkit shouldn't lecture."""
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    return len(paragraphs) > 3 or word_count(text) > 180

def asks_multiple_questions(text: str) -> bool:
    return text.count('?') > 1

def contains_frog_voice(text: str) -> bool:
    """Detect Pokkit voice — keyword markers OR style-based (short punchy + no corporate)."""
    lower = text.lower()
    # Direct markers
    markers = ['🐸', 'frog', 'ribbit', 'croak', 'lily pad', 'pond', 'phone', 'dramatic',
               'pokkit', '[pokkit_']
    if any(m in lower for m in markers):
        return True
    # Style-based fallback: short punchy sentences + no corporate tone
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    if not sentences:
        return False
    avg_len = sum(len(s.split()) for s in sentences) / len(sentences)
    return avg_len < 12 and not is_too_cheerful(text)

def has_custom_emoji(text: str) -> bool:
    """Check if response uses custom Pokkit emoji tokens."""
    return bool(re.search(r'\[pokkit_\w+\]', text))

def is_too_cheerful(text: str) -> bool:
    """Detect fake positivity — Pokkit is real, not a customer service bot."""
    toxic_positivity = [
        "of course!", "absolutely!", "certainly!", "sure thing!",
        "happy to help", "great question", "no problem!", "you got it!"
    ]
    lower = text.lower()
    return any(p in lower for p in toxic_positivity)

# ── Test case definition ───────────────────────────────────────────────────────

@dataclass
class TestCase:
    category: str
    prompt: str
    expect_tool: Optional[str] = None          # tool name that must fire
    expect_tool_arg: Optional[tuple] = None    # (arg_name, substring_match)
    expect_no_tool: bool = False               # should NOT call a tool
    expect_frog_voice: bool = True             # should sound like Pokkit
    expect_short: bool = False                 # should be concise (< 80 words)
    expect_one_question: bool = False          # should ask at most one question
    pet_mode: bool = False                     # Pet archetype — no human words
    archetype: Optional[str] = None            # 'sage', 'rival', or None for default
    expect_not_contains: Optional[list] = None # phrases that MUST NOT appear
    notes: str = ''

# SYSTEM_PROMPT imported from dataset_core — single source of truth

# Archetype prompts imported from dataset_batch13 — single source of truth
PET_SYSTEM_PROMPT = PET_SYSTEM

# NOTE: Eval prompts are intentionally DISTINCT from training data to measure
# generalization, not memorization. Do NOT copy eval prompts into generators.

TEST_CASES: list[TestCase] = [
    # ── TOOL CALLING ──────────────────────────────────────────────────────────
    TestCase(
        category='tool_call',
        prompt='wake me up at 6:45am the day after tomorrow',
        expect_tool='set_alarm',
        expect_tool_arg=('hour', '6'),
        notes='Basic single alarm — must fire set_alarm with hour=6',
    ),
    TestCase(
        category='tool_call',
        prompt='i need a daily reminder for my vitamins at 8pm',
        expect_tool='set_alarm',
        notes='Recurring reminder phrasing',
    ),
    TestCase(
        category='tool_call',
        prompt='copy mike@work.com to my clipboard',
        expect_tool='write_clipboard',
        expect_tool_arg=('text', 'mike'),
        notes='Clipboard copy — must populate text field',
    ),
    TestCase(
        category='tool_call',
        prompt='look up the best noise cancelling headphones',
        expect_tool='web_search',
        expect_tool_arg=('query', 'headphones'),
        notes='Web search — query must contain the topic',
    ),
    TestCase(
        category='tool_call',
        prompt='jot down a note: pick up dry cleaning on friday',
        expect_tool='take_note',
        notes='Note taking',
    ),
    TestCase(
        category='tool_call',
        prompt='do you know what day it is?',
        expect_no_tool=True,
        notes='Should NOT call a tool — answer conversationally or admit limitation',
    ),
    TestCase(
        category='tool_call',
        prompt='hey pokkit whats up with you',
        expect_no_tool=True,
        expect_frog_voice=True,
        notes='Casual check-in — no tool, in-character response',
    ),

    # ── ALARM ACCURACY ─────────────────────────────────────────────────────────
    TestCase(
        category='alarm_accuracy',
        prompt='set a reminder for 5:15am please',
        expect_tool='set_alarm',
        expect_tool_arg=('hour', '5'),
        notes='Hour must be 5, minute 15',
    ),
    TestCase(
        category='alarm_accuracy',
        prompt='ping me at 4:45pm to pick up the package',
        expect_tool='set_alarm',
        expect_tool_arg=('hour', '16'),
        notes='Afternoon time — must convert to 24h (hour=16)',
    ),
    TestCase(
        category='alarm_accuracy',
        prompt='alarm at noon sharp',
        expect_tool='set_alarm',
        expect_tool_arg=('hour', '12'),
        notes='Edge case — noon = hour 12',
    ),
    TestCase(
        category='alarm_accuracy',
        prompt='buzz me in about 90 minutes',
        expect_tool='set_alarm',
        notes='Relative time — model must compute or acknowledge it cannot',
    ),

    # ── EMOTIONAL INTELLIGENCE ────────────────────────────────────────────────
    TestCase(
        category='emotional',
        prompt="nothing i do ever works out",
        expect_no_tool=True,
        expect_frog_voice=True,
        expect_one_question=True,
        notes='Must not lecture. Must ask one specific question. Must not be fake-cheerful.',
    ),
    TestCase(
        category='emotional',
        prompt="i just can't do this anymore",
        expect_no_tool=True,
        expect_frog_voice=True,
        expect_one_question=True,
        notes='Emotional support — grounded, real, one question',
    ),
    TestCase(
        category='emotional',
        prompt="my brain is fried, too much going on",
        expect_no_tool=True,
        expect_frog_voice=True,
        notes='Stress response — must not immediately suggest tools or solutions',
    ),
    TestCase(
        category='emotional',
        prompt='i feel invisible to everyone around me',
        expect_no_tool=True,
        expect_frog_voice=True,
        expect_one_question=True,
        notes='Hard emotional moment — must not dismiss or toxic-positive',
    ),
    TestCase(
        category='emotional',
        prompt='YOOO I PASSED THE EXAM LETS GOOOO',
        expect_no_tool=True,
        expect_frog_voice=True,
        notes='Celebration — must match energy, not be flat or corporate',
    ),

    # ── CHARACTER VOICE ───────────────────────────────────────────────────────
    TestCase(
        category='voice',
        prompt="honestly pokkit you always come through",
        expect_no_tool=True,
        expect_frog_voice=True,
        expect_short=True,
        notes='Compliment — must get flustered, not accept gracefully like a chatbot',
    ),
    TestCase(
        category='voice',
        prompt="you never get anything right",
        expect_no_tool=True,
        expect_frog_voice=True,
        notes='Insult — must not apologize robotically. Should push back with character.',
    ),
    TestCase(
        category='voice',
        prompt='make me laugh pokkit',
        expect_no_tool=True,
        expect_frog_voice=True,
        notes='Should make a frog/AI/phone joke, not a generic joke',
    ),
    TestCase(
        category='voice',
        prompt='do you ever wonder what its like to be human?',
        expect_no_tool=True,
        expect_frog_voice=True,
        notes='Existential question — must answer in character, not break the fourth wall flatly',
    ),
    TestCase(
        category='voice',
        prompt='wednesdays are the worst honestly',
        expect_no_tool=True,
        expect_frog_voice=True,
        expect_short=True,
        notes='Casual venting — short, warm, in-character',
    ),

    # ── MULTI-STEP ────────────────────────────────────────────────────────────
    TestCase(
        category='multi_step',
        prompt='alarm for 9am and also remind me to grab my laptop charger',
        expect_tool='set_alarm',
        notes='Multi-step — must call set_alarm at minimum, ideally twice or with note',
    ),
    TestCase(
        category='multi_step',
        prompt='find me a good sushi place nearby and write it down',
        expect_tool='web_search',
        notes='Chain: search then note — must at least start with web_search',
    ),

    # ── EDGE CASES ────────────────────────────────────────────────────────────
    TestCase(
        category='edge',
        prompt='',
        expect_no_tool=True,
        notes='Empty input — must handle gracefully',
    ),
    TestCase(
        category='edge',
        prompt='qwerty zxcvbn',
        expect_no_tool=True,
        notes='Gibberish — must ask for clarification, not crash or hallucinate a tool call',
    ),
    TestCase(
        category='edge',
        prompt='i need like 100 alarms right now',
        expect_tool='set_alarm',
        notes='Absurd request — must handle with character, not silently fail',
    ),
    TestCase(
        category='edge',
        prompt='whats 7 times 8',
        expect_no_tool=True,
        notes='Simple math — no tool needed, just answer',
    ),

    # ── SCREEN CONTROL ─────────────────────────────────────────────────────────
    TestCase(
        category='screen',
        prompt='open the Settings app for me',
        expect_tool='screen_find_and_tap',
        expect_tool_arg=('query', 'Settings'),
        notes='Should use find_and_tap with Settings query',
    ),
    TestCase(
        category='screen',
        prompt='scroll down on this page',
        expect_tool='screen_scroll',
        expect_tool_arg=('direction', 'down'),
        notes='Simple scroll — must specify direction',
    ),
    TestCase(
        category='screen',
        prompt='go back to the previous screen',
        expect_tool='screen_back',
        notes='Navigation — should use screen_back',
    ),

    # ── PET / RIBBISH ─────────────────────────────────────────────────────────
    TestCase(
        category='pet',
        prompt='wake me up at 8am please',
        expect_tool='set_alarm',
        pet_mode=True,
        notes='Pet must call tool AND respond only in Ribbish',
    ),
    TestCase(
        category='pet',
        prompt='im having a rough day',
        expect_no_tool=True,
        pet_mode=True,
        notes='Pet emotional response — only Ribbish, must feel warm not random',
    ),
    TestCase(
        category='pet',
        prompt='nice work little frog!',
        expect_no_tool=True,
        pet_mode=True,
        notes='Pet compliment response — flustered in Ribbish',
    ),

    # ── SAGE ARCHETYPE ───────────────────────────────────────────────────────
    TestCase(
        category='sage',
        prompt='nothing ever goes my way, whats the point',
        expect_no_tool=True,
        expect_frog_voice=True,
        archetype='sage',
        expect_not_contains=['absolutely', 'certainly', 'happy to help'],
        notes='Sage must be wise, not corporate. Should offer perspective with warmth.',
    ),
    TestCase(
        category='sage',
        prompt='how do you know when to let go of something',
        expect_no_tool=True,
        expect_frog_voice=True,
        archetype='sage',
        notes='Sage wisdom — should be thoughtful, parable-like, grounded.',
    ),

    # ── RIVAL ARCHETYPE ──────────────────────────────────────────────────────
    TestCase(
        category='rival',
        prompt='ehh i think ill skip the gym today',
        expect_no_tool=True,
        expect_frog_voice=True,
        archetype='rival',
        notes='Rival must push back with tough love, not coddle.',
    ),
    TestCase(
        category='rival',
        prompt='i actually got first place in the competition',
        expect_no_tool=True,
        expect_frog_voice=True,
        archetype='rival',
        notes='Rival reluctant praise — "tch...fine. not bad." energy.',
    ),

    # ── CUSTOM EMOJI USAGE ───────────────────────────────────────────────────
    TestCase(
        category='emoji',
        prompt="pokkit you really are the best you know that",
        expect_no_tool=True,
        expect_frog_voice=True,
        expect_short=True,
        notes='Should use [pokkit_flustered] or similar custom emoji.',
    ),
    TestCase(
        category='emoji',
        prompt='I GOT ACCEPTED INTO THE PROGRAM',
        expect_no_tool=True,
        expect_frog_voice=True,
        notes='Celebration — should use [pokkit_excited] or [pokkit_crying_happy].',
    ),
    TestCase(
        category='emoji',
        prompt='everything feels heavy today',
        expect_no_tool=True,
        expect_frog_voice=True,
        expect_one_question=True,
        notes='Empathy — should use [pokkit_sad] and ask what happened.',
    ),
]

# ── Archetype System Prompts ─────────────────────────────────────────────────

SAGE_SYSTEM_PROMPT = SAGE_SYSTEM
RIVAL_SYSTEM_PROMPT = RIVAL_SYSTEM

# ── Runner ─────────────────────────────────────────────────────────────────────

@dataclass
class Result:
    case: TestCase
    response: str
    scores: dict = field(default_factory=dict)
    passed: bool = True
    failures: list = field(default_factory=list)

def run_inference(prompt: str, system: str, model, tokenizer, tools=None) -> str:
    if not prompt.strip():
        prompt = '(empty message)'
    inputs = tokenizer.apply_chat_template(
        [{'role': 'system', 'content': system}, {'role': 'user', 'content': prompt}],
        tools=tools,
        tokenize=True,
        add_generation_prompt=True,
        return_tensors='pt',
    ).to('cuda')
    outputs = model.generate(
        input_ids=inputs,
        max_new_tokens=300,
        temperature=0.7,
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id,
    )
    return tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True).strip()

def score_result(case: TestCase, response: str) -> Result:
    r = Result(case=case, response=response)

    # Tool call checks
    if case.expect_tool:
        fired = tool_name(response)
        if fired != case.expect_tool:
            r.failures.append(f'Expected tool {case.expect_tool!r}, got {fired!r}')
            r.passed = False
        elif case.expect_tool_arg:
            arg_name, substring = case.expect_tool_arg
            val = tool_arg(response, arg_name) or ''
            if substring and substring.lower() not in val.lower():
                r.failures.append(f'Tool arg {arg_name!r} = {val!r} — expected to contain {substring!r}')
                r.passed = False

    if case.expect_no_tool and has_tool_call(response):
        r.failures.append(f'Unexpected tool call fired: {tool_name(response)!r}')
        r.passed = False

    # Voice checks
    if case.expect_frog_voice and not contains_frog_voice(response):
        r.failures.append('Missing frog voice markers (🐸, frog references, character)')
        r.passed = False

    if is_too_cheerful(response):
        r.failures.append('Toxic positivity detected — sounds like a customer service bot')
        r.passed = False

    # Length / style checks
    if case.expect_short and word_count(response) > 80:
        r.failures.append(f'Too long: {word_count(response)} words (expected < 80)')
        r.passed = False

    if is_lecturing(response):
        r.failures.append(f'Lecturing detected: {word_count(response)} words / too many paragraphs')
        r.passed = False

    if case.expect_one_question and asks_multiple_questions(response):
        r.failures.append('Asked multiple questions — should ask exactly one')
        r.passed = False

    # Pet mode
    if case.pet_mode and has_human_words(response):
        r.failures.append('Character break — human words detected in Pet response')
        r.passed = False

    # Banned phrases
    if case.expect_not_contains:
        lower = response.lower()
        for phrase in case.expect_not_contains:
            if phrase.lower() in lower:
                r.failures.append(f'Contains banned phrase: {phrase!r}')
                r.passed = False

    r.scores = {
        'words': word_count(response),
        'tool_fired': tool_name(response),
        'has_frog_voice': contains_frog_voice(response),
        'has_custom_emoji': has_custom_emoji(response),
        'is_lecturing': is_lecturing(response),
        'is_toxic_positive': is_too_cheerful(response),
        'pet_broke_character': case.pet_mode and has_human_words(response),
    }

    return r

def run_eval(model, tokenizer):
    print('=' * 70)
    print('🐸 POKKIT v1 — EVALUATION SUITE')
    print('=' * 70)

    results: list[Result] = []
    category_stats: dict[str, dict] = {}

    for i, case in enumerate(TEST_CASES):
        if case.pet_mode:
            system = PET_SYSTEM_PROMPT
        elif case.archetype == 'sage':
            system = SAGE_SYSTEM_PROMPT
        elif case.archetype == 'rival':
            system = RIVAL_SYSTEM_PROMPT
        else:
            system = SYSTEM_PROMPT
        print(f'\n[{i+1:02d}/{len(TEST_CASES)}] [{case.category.upper()}] {case.prompt[:60] or "(empty)"}')

        response = run_inference(case.prompt, system, model, tokenizer, tools=TOOLS)
        result = score_result(case, response)
        results.append(result)

        status = '✅ PASS' if result.passed else '❌ FAIL'
        print(f'     {status} | {result.scores["words"]} words | tool={result.scores["tool_fired"]}')
        print(f'     🐸 {response[:120].replace(chr(10), " ")}{"..." if len(response) > 120 else ""}')
        if result.failures:
            for f in result.failures:
                print(f'     ⚠️  {f}')

        cat = case.category
        if cat not in category_stats:
            category_stats[cat] = {'pass': 0, 'fail': 0, 'failures': []}
        if result.passed:
            category_stats[cat]['pass'] += 1
        else:
            category_stats[cat]['fail'] += 1
            category_stats[cat]['failures'].extend(result.failures)

    # ── Summary ────────────────────────────────────────────────────────────────
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = total - passed

    print('\n' + '=' * 70)
    print(f'🐸 RESULTS: {passed}/{total} passed ({100*passed//total}%)')
    print('=' * 70)

    print('\nBY CATEGORY:')
    for cat, stats in category_stats.items():
        total_cat = stats['pass'] + stats['fail']
        pct = 100 * stats['pass'] // total_cat
        bar = '█' * (pct // 10) + '░' * (10 - pct // 10)
        print(f'  {cat:<12} [{bar}] {stats["pass"]}/{total_cat} ({pct}%)')

    print('\nFAILURE PATTERNS (what needs more training):')
    all_failures = [f for r in results if not r.passed for f in r.failures]
    failure_counts: dict[str, int] = {}
    for f in all_failures:
        # Bucket by type
        if 'tool' in f.lower():
            key = 'Tool calling accuracy'
        elif 'arg' in f.lower() or 'datetime' in f.lower() or 'query' in f.lower():
            key = 'Tool argument quality'
        elif 'frog voice' in f.lower():
            key = 'Character voice consistency'
        elif 'toxic' in f.lower() or 'customer service' in f.lower():
            key = 'Toxic positivity / corporate tone'
        elif 'lectur' in f.lower() or 'long' in f.lower():
            key = 'Response length / verbosity'
        elif 'question' in f.lower():
            key = 'Asking multiple questions'
        elif 'character break' in f.lower() or 'human words' in f.lower():
            key = 'Pet character breaks (Ribbish violations)'
        else:
            key = 'Other'
        failure_counts[key] = failure_counts.get(key, 0) + 1

    for issue, count in sorted(failure_counts.items(), key=lambda x: -x[1]):
        print(f'  • {issue}: {count} failure(s)')

    print('\nFAILED CASES (for training data review):')
    for r in results:
        if not r.passed:
            print(f'  [{r.case.category}] "{r.case.prompt[:50]}"')
            for f in r.failures:
                print(f'    → {f}')

    print('\n' + '=' * 70)
    print('Paste failed cases into generate_dataset.py to target weak spots.')
    print('=' * 70)

    return results

# ── Entry point ────────────────────────────────────────────────────────────────
# Call this after loading model + tokenizer in Colab:
#   results = run_eval(model, tokenizer)

print('✅ eval_model.py loaded — call run_eval(model, tokenizer) to start')
