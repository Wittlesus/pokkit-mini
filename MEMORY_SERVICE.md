# Pokkit Memory Service — Architecture Spec

Pokkit currently starts fresh every conversation. This document specifies how to give it persistent memory across sessions, ported from the brain system's hippocampus architecture.

---

## The Problem

Right now Pokkit can use `store_value` / `retrieve_value` tools during a conversation, but:
- It has to explicitly call those tools — it doesn't automatically notice what's worth remembering
- Nothing is injected back into context at the start of a new session
- There's no intelligence about *what* to surface — it's just a key/value lookup

The brain system solves all three of these problems. We're porting that logic into Pokkit.

---

## Architecture Overview

```
User sends message
        ↓
Memory Service intercepts (runs BEFORE Pokkit sees the message)
        ↓
Hippocampus: keyword scan → retrieve relevant memories
        ↓
Relevant memories injected into system prompt context
        ↓
Pokkit responds (with memory context)
        ↓
After response: Pokkit decides what to store (or Memory Service auto-detects)
        ↓
Memory written to persistent store
```

---

## Three Layers of Memory

### Layer 1: User Preferences (Permanent)
Things that are always true about the user. Injected every session.

```json
{
  "schedule": "morning person, prefers 6-7am",
  "communication": "direct, hates long explanations",
  "work": "indie developer, building Pokkit",
  "name": "prefers first name only",
  "manager": "Sarah",
  "focus_music": "lo-fi"
}
```

**How it gets populated:** Pokkit notices preference signals in conversation and calls `store_value`. The memory service promotes frequently-used values to the permanent layer.

---

### Layer 2: Episodic Memory (Session-scoped, decays)
Things that happened recently. Injected when relevant.

```json
{
  "last_project": "pokkit-mini training run",
  "last_mood": "tired but productive",
  "pending": ["follow up with Sarah", "check training results"],
  "recent_wins": ["shipped 50k dataset", "fixed batch4 bug"],
  "recent_struggles": ["colab auth issues"]
}
```

**How it gets populated:** End-of-session consolidation. Pokkit summarizes what happened and writes it. Decays after 7 days if not reinforced.

---

### Layer 3: Cue-based Retrieval (On-demand)
The hippocampus layer — keyword-triggered retrieval of relevant past context.

User says "i'm stressed about the launch" → retrieves memories tagged `launch`, `stress`, `shipping`.

User says "set an alarm for my meeting with Sarah" → retrieves `contact_manager = Sarah`, `user_preference_schedule = morning`.

---

## Implementation Plan

### Phase 1: Smart `store_value` (Now — dataset work)

Train Pokkit to notice and store things automatically without being asked:

```
User: "i always forget to drink water"
Pokkit: [calls store_value("habit_water_reminder", "true")]
        "noted!! 🐸 want me to set recurring reminders?"
```

```
User: "my girlfriend's name is Maya"  
Pokkit: [calls store_value("contact_girlfriend", "Maya")]
        "got it!! 🐸 Maya. i'll remember that."
```

This is already partially in the dataset. Needs more examples covering:
- Contact names and relationships
- Preferences (schedule, communication style, food, music)
- Recurring struggles ("i always forget X")
- Goals ("i'm trying to Y this year")
- Work context (job, projects, teammates)

---

### Phase 2: Memory Injection Service (Backend — Node/Python)

A lightweight service that runs alongside the app and wraps every Pokkit request.

**File:** `pokkit-memory/memory_service.py` (or TypeScript equivalent)

```python
class PokkitMemoryService:
    
    def before_message(self, user_message: str, user_id: str) -> str:
        """
        Runs before Pokkit sees the message.
        Returns additional context to inject into the system prompt.
        """
        memories = []
        
        # Always inject: core preferences
        prefs = self.get_permanent_memories(user_id)
        if prefs:
            memories.append(f"[What I know about you: {prefs}]")
        
        # Conditionally inject: episodic + cue-based
        relevant = self.hippocampus_retrieval(user_message, user_id)
        if relevant:
            memories.append(f"[Relevant context: {relevant}]")
        
        return "\n".join(memories)
    
    def hippocampus_retrieval(self, prompt: str, user_id: str) -> str:
        """
        Keyword-based retrieval — port of the brain system's prefrontal_retrieval.
        Scans prompt for cue words, retrieves tagged memories.
        """
        prompt_lower = prompt.lower()
        matched_memories = []
        
        all_memories = self.get_all_memories(user_id)
        
        for key, value in all_memories.items():
            # Direct key match
            if any(word in prompt_lower for word in key.split("_")):
                matched_memories.append(f"{key}: {value}")
            
            # Tag-based match (memories can have tags)
            if hasattr(value, 'tags'):
                for tag in value.tags:
                    if tag in prompt_lower:
                        matched_memories.append(f"{key}: {value.content}")
                        break
        
        return ", ".join(matched_memories[:5])  # cap at 5 to save context
    
    def after_message(self, pokkit_response: str, user_id: str):
        """
        Runs after Pokkit responds.
        Extracts any store_value tool calls and persists them.
        Also runs importance scoring — should this go to permanent memory?
        """
        # Parse tool calls from response
        tool_calls = self.extract_tool_calls(pokkit_response)
        for call in tool_calls:
            if call['name'] == 'store_value':
                self.write_memory(
                    user_id=user_id,
                    key=call['args']['key'],
                    value=call['args']['value'],
                    importance=self.score_importance(call['args']['key'])
                )
    
    def score_importance(self, key: str) -> str:
        """
        Port of amygdala_weight — score how important a memory is.
        High importance → permanent layer. Low → episodic (decays).
        """
        HIGH_IMPORTANCE = {'name', 'manager', 'partner', 'schedule', 'goal', 'health'}
        MEDIUM_IMPORTANCE = {'preference', 'habit', 'contact', 'project'}
        
        for word in HIGH_IMPORTANCE:
            if word in key:
                return 'permanent'
        for word in MEDIUM_IMPORTANCE:
            if word in key:
                return 'episodic'
        return 'session'
```

---

### Phase 3: Consolidation (End of session)

Port of the hippocampus consolidation system. After N messages, Pokkit summarizes what it learned this session and writes it to episodic memory.

```
Every 10 messages → Pokkit internally asks:
  "What have I learned about this person today that I should remember?"
  
Writes to episodic store:
  - mood/energy level
  - what they were working on
  - any preferences revealed
  - wins and struggles
  - pending things they mentioned
```

This is the "Pokkit remembers you" feature. Not just facts — emotional context too.

---

### Phase 4: On-device Storage

**For React Native / Expo (the Pokkit app):**

```typescript
// lib/memory.ts
import * as SecureStore from 'expo-secure-store';
import AsyncStorage from '@react-native-async-storage/async-storage';

export class PokkitMemory {
  
  // Permanent memories → SecureStore (encrypted, persists forever)
  async setPermanent(key: string, value: string) {
    await SecureStore.setItemAsync(`pokkit_perm_${key}`, value);
  }
  
  // Episodic memories → AsyncStorage (persists, but we can expire)
  async setEpisodic(key: string, value: string, ttlDays = 7) {
    const entry = {
      value,
      expires: Date.now() + (ttlDays * 24 * 60 * 60 * 1000)
    };
    await AsyncStorage.setItem(`pokkit_ep_${key}`, JSON.stringify(entry));
  }
  
  // Build context injection for system prompt
  async buildContextInjection(userMessage: string): Promise<string> {
    const permanent = await this.getAllPermanent();
    const relevant = await this.getRelevantEpisodic(userMessage);
    
    const parts = [];
    if (Object.keys(permanent).length > 0) {
      parts.push(`What I know about you: ${JSON.stringify(permanent)}`);
    }
    if (relevant.length > 0) {
      parts.push(`Recent context: ${relevant.join(', ')}`);
    }
    
    return parts.join('\n');
  }
  
  // Keyword-based retrieval (hippocampus port)
  async getRelevantEpisodic(prompt: string): Promise<string[]> {
    const keys = await AsyncStorage.getAllKeys();
    const episodicKeys = keys.filter(k => k.startsWith('pokkit_ep_'));
    const results: string[] = [];
    
    for (const key of episodicKeys) {
      const raw = await AsyncStorage.getItem(key);
      if (!raw) continue;
      const entry = JSON.parse(raw);
      if (entry.expires < Date.now()) {
        await AsyncStorage.removeItem(key); // expired
        continue;
      }
      // Simple keyword match — upgrade to tag-based later
      const cleanKey = key.replace('pokkit_ep_', '').replace(/_/g, ' ');
      if (prompt.toLowerCase().includes(cleanKey)) {
        results.push(`${cleanKey}: ${entry.value}`);
      }
    }
    
    return results.slice(0, 5); // cap context injection
  }
}
```

---

## What This Looks Like in Practice

**Session 1:**
> User: "i always forget to drink water"
> Pokkit: stores `habit_water = "forgets water, needs reminders"` → sets recurring alarm

**Session 2 (next day):**
> User: "good morning pokkit"
> Memory service injects: `[What I know about you: habit_water: forgets water, needs reminders]`
> Pokkit: "good morning!! 🐸 did you drink water yet??"

**Session 5:**
> User: "i have a meeting with Sarah"
> Memory service injects: `contact_manager: Sarah`
> Pokkit: "got it!! 🐸 want me to set a prep reminder before it?"
> (Pokkit already knows Sarah is the manager — doesn't ask)

---

## Priority Order

1. **Now:** Expand dataset with more `store_value` examples (Pokkit noticing things worth remembering)
2. **Next:** Build `lib/memory.ts` in the Pokkit app — on-device storage with SecureStore + AsyncStorage
3. **Then:** Wire memory injection into the system prompt before each request
4. **Later:** Consolidation — end-of-session summarization
5. **Eventually:** Tag-based retrieval (full hippocampus port) for smarter cue matching

The first two steps can happen before v2 training finishes. The memory injection (step 3) is what makes Pokkit actually feel like it remembers you.

---

## Files to Create

```
pokkit-app/
  lib/
    memory.ts          ← on-device storage (Phase 2)
    memory-service.ts  ← context injection wrapper (Phase 3)
  
pokkit-mini/
  dataset_batch5.py   ← more store_value training examples (Phase 1)
```
