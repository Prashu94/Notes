# Answer format (every `questions.md` follows this)

Each question uses this structure so answers are **interview-ready** — speak for **2–3 minutes**, not flashcards.

```markdown
### N. Question text?

**Short answer:** 4–6 sentences — the headline a panel remembers, with one trade-off or failure mode.

#### What it is
Plain-language definition and where it sits in the stack (3–5 sentences).

#### How it works (internals)
Mechanism, JVM/broker/framework behavior, defaults, flags (4–6 sentences).

#### When to use / when NOT to use
Trade-offs. What you would pick in prod and why (3–5 sentences).

#### Production example
Concrete scenario (Spring service, Kafka consumer, pipeline, on-call, etc.) — 4–6 sentences with outcome.

#### Common mistakes
What breaks at 2 a.m.; what juniors say wrong (3–5 bullets or sentences).

#### Interview follow-ups (with model answers)

**Q:** First follow-up the interviewer will ask?
**A:** 80–120 words — direct answer, one production detail, optional command or flag.

**Q:** Second follow-up?
**A:** ...

#### Scenario probe
Mini case tied to this topic (2–3 sentence situation + 100–150 word model answer).

#### Code / config (when useful)
```language
...
```
```

At the **end** of each `questions.md` (before any appendix such as rapid-fire):

```markdown
## Scenario-based interview drills

### S1. Title (production incident or design walk-through)

**Situation:** Realistic context — service, scale, symptom, constraint.

**What they're testing:** Depth area (e.g. GC, N+1, saga, idempotency).

**How to structure your answer:** Outline bullets for a 2-minute response.

**Model answer:** 250–400 words — what a 10+ year engineer would say out loud.

**Common weak answers:** What to avoid saying.

**Follow-up probes (with answers):**

**Q:** ...
**A:** ...
```

**Target length per main question:** ~350–500 words (excluding code).  
**Scenario drills:** 10 per topic file, unique from the 50 main questions.
