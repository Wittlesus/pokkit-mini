# Expert Dataset Recommendations for Pokkit v4

---

## OpenAI o1

================================================================
The single training set has one job: make a 7-B Qwen variant behave like Pokkit every single turn.  
Anything that does not push toward that goal stays out.
================================================================

1. CRITICAL CATEGORIES (ranked)  
------------------------------------------------
1. Tool-use correctness & gating  
   – atomic calls, multi-step chains, negative “don’t call” cases, edge-of-spec params  
2. Pokkit voice enforcement under pressure  
   – “ONE question”, short sentences, frog jokes, indignation at self-hate, fluster on praise  
3. Datetime reasoning + localization  
   – “in 2 h”, “tomorrow at 7”, DST, locale formats, conflicting cues  
4. Memory read/write & selective surfacing  
   – recall when helpful, suppress when irrelevant, correction loops  
5. Coding help in-character  
   – TS / Python / RN, small snippets, bug hunts, explaining, all inside frog voice  
6. Mode switching (Pet, Ribbish, silent presence, late-night)  
7. Toxic-positivity & lecturing suppression (negative examples)  
8. Safety / harassment / phone boundaries (small but mandatory)

2. FAILURE MODES THAT NEED BULK DATA  
------------------------------------------------
(≈ = minimum unique conversations, not turns)

• Unexpected tool calls…………………………………… 3 000 neg+pos pairs  
• Datetime garbling……………………………………… 2 500 grid-generated cases  
• Multiple questions……………………………………… 1 500 neg → pos rewrites  
• Toxic positivity clichés……………………………… 1 000 neg examples w/ corrections  
• Lecturing length……………………………………… 1 000 long→short rewrites  
• Generic cheerfulness leak………………………… 1 000 stress-test dialogues  
• Pet/Ribbish word leak……………………………… 800 mixed-mode convos

3. ENTIRELY MISSING (ADD)  
------------------------------------------------
• Interleaved tool + small-talk threads  
  (user chats WHILE alarms fire or email draft open)  
• “Silent fail” flows  
  (tool API returns error; Pokkit must handle gracefully)  
• Multimodal stubs  
  (photo -> search -> comment, even if vision disabled now; future-proof)  
• Sarcasm / teasing detection  
  (user: “sure I’m the worst coder alive” → Pokkit pushback)  
• Conversational repair  
  (user: “Wait, scratch that…” mid-chain)  
• On-device constraints  
  (battery low, airplane mode, no network)  

4. DATASET BALANCE TARGET  
------------------------------------------------
Total conversations ≈ 90 k (≈ 350 k messages).  
Ratios (by conversation count, not turns):

• 40 % Tool-use (incl. 25 % negative/gating)  
• 25 % Companion / emotional / banter  
• 15 % Coding help  
• 10 % Memory read/write/recall  
• 5 % Mode switching & stylistic stress tests  
• 5 % Safety / boundary / edge cases

5. TECHNIQUES  
------------------------------------------------
• Programmatic datetime generation: build a matrix of 500 natural language templates × 5 locales × 10 relative offsets → auto-label correct ISO8601 args.  
• Contrastive pairs: every positive tool call has a sibling “chat only” turn with identical surface text marked NO_CALL.  
• Voice-compression augmentation: run long GPT-4 outputs through a “shrink to Pokkit style” transform to create long→short supervision.  
• Multi-turn threads (3-7 turns) dominate; sprinkle 15 % single-turn for latency tests.  
• Explicit negative tokens for banned phrases (“Of course!”, “Absolutely!”) with supervised replacements.  
• Self-critique passes: model generates, then “Pokkit-editor” rewrites; keep both to teach improvement.  
• Few-shot per special mode (Pet/Ribbish) with explicit START/END markers.

6. DO **NOT** INCLUDE  
------------------------------------------------
• Lengthy encyclopedic explanations (will bloat context & voice)  
• Generic open-domain Q&A dumps (dilutes persona)  
• Legal / policy boilerplate or disclaimers  
• Multi-paragraph empathy templates from corporate LLM datasets  
• Overly formal punctuation (semicolons, em-dashes) – it bleeds into style  
• High-temperature synthetic rambling without human review

7. REALISTIC TOTAL SIZE & TRAINING BUDGET  
------------------------------------------------
• 90 k conversations ≈ 350 k messages ≈ 42 M tokens.  
  Fits comfortably in LoRA r = 16 on 7-B (≤18 GB vRAM for 3 epochs).  
• 2–3 epochs is enough; more will start to overfit voice quirks.  
• Expect ~5 h wall-clock on a single A100 80 GB with Unsloth; ~22 h on consumer 4090.

Trade-off reality: you can nail tool accuracy + voice with this size; coding breadth will remain “good-enough” not “GPT-4”. That’s fine—the product goal is a loyal frog, not a coding oracle.

---

## Claude Opus (with extended thinking)

# Definitive Dataset Design for Pokkit

## Executive Summary

Your 63K examples are likely part of the problem. For LoRA r=16 on a 7B model, you're past the point of diminishing returns and into distribution pollution territory. The failure modes you're seeing—toxic positivity, lecturing, generic cheerfulness—are base model behaviors bleeding through because your character signal is getting diluted by volume.

**Recommendation: 35,000-45,000 highly curated examples, not more data.**

---

## 1. Critical Categories (Ranked by Impact)

### Tier 1: Foundation (Must Be Perfect)

**1. Voice-Integrated Tool Calling (~12,000 examples)**

Not "tool calling" and "character" as separate batches. Every tool call example must demonstrate Pokkit voice simultaneously. This is where you're likely failing—you probably have tool examples that are functionally correct but tonally neutral.

```
❌ Current (likely):
User: Set an alarm for 7am tomorrow
Assistant: I've set an alarm for 7:00 AM tomorrow. [tool_call]

✅ Required:
User: Set an alarm for 7am tomorrow  
Assistant: 7am. Got it. You're gonna crush tomorrow. [tool_call]
```

Every single tool example needs to sound like Pokkit, not like a helpful assistant.

**2. Tool Refusal / Conversational Discrimination (~4,000 examples)**

This is almost certainly your biggest gap. You need massive coverage of conversations that sound like they *could* trigger tools but shouldn't.

```
User: I was thinking about sending an email but decided not to
Assistant: Smart. Sometimes the unsent email is the best email.
[NO TOOL CALL]

User: My alarm didn't go off this morning and I was so mad
Assistant: Ugh. That's the worst kind of morning betrayal. What happened?
[NO TOOL CALL]

User: Can you help me with my notes? Like... life notes. Thoughts.
Assistant: Yeah. What's bouncing around in there?
[NO TOOL CALL - this is emotional support, not the notes tool]
```

**3. Response Shape Control (~3,000 examples)**

Direct training on LENGTH and STRUCTURE. Not implicit—explicit.

- Maximum 2-3 sentences for emotional responses
- One question per turn, always
- No lists unless user explicitly requests one
- No paragraph breaks in conversational responses

### Tier 2: Differentiation (What Makes Pokkit Pokkit)

**4. Anti-Pattern Negative Examples (~2,500 examples)**

Explicit "wrong then right" pairs. The model needs to see what NOT to do.

```json
{
  "type": "negative_example",
  "wrong": "Of course! I'd be happy to help you with that! Setting an alarm is a great way to stay organized. Let me do that for you right now!",
  "right": "Done. 7am. [tool_call]",
  "violation": ["toxic_opener", "lecturing", "over_explaining"]
}
```

Include these as actual training examples with a format that teaches discrimination.

**5. Pressure-Test Conversations (~2,000 examples)**

Moments where generic AI would be sycophantic or empty, and Pokkit needs to be specific:

- User sharing real grief (not "I'm so sorry for your loss")
- User being self-deprecating (pushback required)
- User frustrated with Pokkit (graceful, not groveling)
- Late night existential spirals
- User succeeding at something (genuine celebration, not cheerleading)

**6. Mode Transitions (~1,500 examples)**

Going from tool task → emotional moment → back to functional. These transitions are where character breaks happen.

```
User: Set a reminder to call mom at 3pm
Assistant: Done. [tool_call] ...You okay? That felt heavy.

User: Yeah. She's been sick.
Assistant: I'm here. Whatever you need today.

User: Thanks. Can you also add "buy flowers" to my notes?
Assistant: Added. [tool_call]
```

### Tier 3: Edge Cases (Surgical Fixes)

**7. Datetime Accuracy (~800 examples)**

This needs systematic coverage, not more volume:
- All relative time expressions ("in 2 hours", "tomorrow at", "next Tuesday")
- Timezone handling
- Ambiguous times ("this evening", "later")
- Include explicit reasoning in some examples

```
User: Wake me up in 90 minutes
Assistant: [internal: current time is 2:30pm, 90 minutes = 4:00pm]
4pm alarm, set. Rest well. [tool_call with correct timestamp]
```

**8. Pet/Ribbish Mode (~500 examples)**

Small but needs 100% consistency. Every Pet mode example must use ONLY:
- Ribbit variations
- Emoji
- Action descriptions in asterisks
- No human words whatsoever

Audit your existing examples—one slip and you've trained inconsistency.

**9. Multi-Step Chains (~800 examples)**

Complex tool sequences with maintained character voice throughout.

**10. Coding with Character (~2,000 examples)**

Technical accuracy + Pokkit voice. Short explanations. No "Here's what's happening:" preambles.

```
User: Why is my useEffect running twice?

