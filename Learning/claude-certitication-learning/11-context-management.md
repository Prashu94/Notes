# Chapter 11: Context Management in Production Systems

---

## 11.1 Extract Facts into a Separate Block

Instead of relying on conversation history (degrades during summarization), extract key facts into structured block:

```text
=== CASE FACTS (updated whenever a new fact appears) ===
Customer ID: CUST-12345
Order ID: ORD-67890
Order Date: 2025-01-15
Order Amount: $89.99
Issue: Damaged item on delivery
Customer Request: Full refund
Status: Pending manager approval
===
```

Include this block in **every prompt**, regardless of how history is summarized.

**Exam:** Customer references "15% discount" from 20+ turns ago, agent responds with wrong values after summarization → **case facts block**.

---

## 11.2 Trimming Tool Results

If `lookup_order` returns 40+ fields but only 5 needed:

```python
@hook("PostToolUse", tool="lookup_order")
def trim_order_fields(result):
    return {
        "order_id": result["order_id"],
        "status": result["status"],
        "total": result["total"],
        "items": result["items"],
        "return_eligible": result["return_eligible"]
    }
```

Conserves context and reduces noise.

---

## 11.3 Position-aware Input

Place critical information with lost-in-the-middle effect in mind:

```text
[KEY FINDINGS — at the top]
Found 3 critical vulnerabilities...

[DETAILED RESULTS — middle]
=== File auth.ts ===
...

[ACTION ITEMS — at the end]
Priority: fix auth.ts vulnerabilities before merge.
```

**Exam:** 75K token aggregated input, synthesis misses middle 50K → key-findings summary at start + explicit section headings.

---

## 11.4 Scratchpad Files

In long investigations, write key findings to scratchpad:

```markdown
# investigation-scratchpad.md
## Key findings
- PaymentProcessor in src/payments/processor.ts inherits from BaseProcessor
- refund() called from 3 places: OrderController, AdminPanel, CronJob
- External PaymentGateway API rate limit: 100 req/min
- Migration #47 added refund_reason (NOT NULL) — 2024-12-01
```

When context degrades or in new session, consult scratchpad instead of re-running discovery.

---

## 11.5 Delegating to Subagents to Protect Context

```text
Main agent: "Investigate dependencies of payments module"
  → Subagent (Explore): reads 15 files, traces imports
  → Returns: "Payments depends on AuthService, OrderModel, PaymentGateway API"
Main agent: keeps one line instead of 15 files
```

### Separate Context Layer
- Each subagent operates within limited context budget
- Coordinator aggregates outputs, stores global state, allocates context
- Prevents "context leakage" — one agent consuming window with irrelevant info

### Constrained Context Budgets
- Send minimal context: specific task + necessary data
- Instruct subagent to return structured results, not raw dumps
- Use `allowedTools` to limit subagent toolset

**Exam:** 85K + 70K = 155K tokens to synthesis (best under 50K) → modify upstream agents to return structured data (key facts, quotes, relevance scores).

---

## 11.6 Structured State Persistence (Crash Recovery)

Each agent exports state:

```json
// agent-state/web-search-agent.json
{
  "status": "completed",
  "queries_executed": ["AI music 2024", "AI music composition"],
  "results_count": 12,
  "key_findings": [...],
  "coverage": ["music composition", "music production"],
  "gaps": ["music distribution", "music licensing"]
}
```

Coordinator loads manifest on resume:

```json
// agent-state/manifest.json
{
  "web-search": "completed",
  "doc-analysis": "in_progress",
  "synthesis": "not_started"
}
```

---

## `/compact` Risks

Summarizes history to free context but loses exact numeric values, dates, specific details. Use case facts block as safeguard.

---

## Memory Aids

| Problem | Solution |
|---------|----------|
| Lost numbers after summarization | Case facts block |
| 40+ tool result fields | PostToolUse trim hook |
| Missed middle of long input | Key findings at top |
| Long investigation | Scratchpad file |
| Verbose discovery | Subagent delegation |
| 155K tokens to synthesis | Structured upstream output |
| Crash mid-pipeline | State persistence + manifest |
