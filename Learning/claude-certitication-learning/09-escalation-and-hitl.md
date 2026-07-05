# Chapter 9: Escalation and Human-in-the-Loop

---

## 9.1 When to Escalate to a Human

### Reliable Escalation Triggers

| Situation | Action |
|-----------|--------|
| Customer explicitly asks "get me a manager" | **Escalate immediately** — do not attempt to solve |
| Policy does not cover the request | Escalate (e.g., competitor price matching when policy silent) |
| Agent cannot make progress | Escalate after reasonable attempts |
| Financial operation above threshold | Escalate (preferably via **hook**, not prompt) |
| Multiple customer matches | Ask for additional identifiers — **do not guess** |

### What is NOT a Reliable Trigger

| Unreliable Method | Why It Fails |
|-------------------|--------------|
| Sentiment analysis | Mood ≠ case complexity |
| Model self-rated confidence (1–10) | Model can be confidently wrong |
| Automatic classifier | Overengineering; needs training data |

---

## 9.2 Escalation Patterns

### Immediate Escalation
```text
Customer: "I want to speak to a manager"
Agent: [immediately calls escalate_to_human]
NOT: "I can help with your issue, let me..."
```

### Escalation After Attempt to Resolve
```text
Customer: "My refrigerator broke two days after purchase"
Agent: [checks order, offers warranty replacement]
If customer not satisfied → escalate
```

### Nuanced Escalation (Acknowledge → Resolve → Escalate on Reiteration)
```text
Customer: "This is outrageous, I'm very unhappy!"
Agent: [acknowledges] "I understand your frustration."
       [offers resolution] "I can offer replacement or refund."
Customer: "No, I want to talk to someone!"
Agent: [customer insists again → immediate escalation]
```

**Key:** Do NOT escalate on first expression of dissatisfaction. That is not the same as requesting a manager.

### Policy Gap Escalation
```text
Customer: "Competitor X has this 30% cheaper—give me a discount"
Policy: price adjustments only on your own site
Agent: [escalates — policy silent on competitor matching]
```

---

## 9.3 Structured Handoff Protocols

On escalation, pass structured summary to human:

```json
{
  "customer_id": "CUST-12345",
  "customer_name": "Ivan Petrov",
  "issue_summary": "Refund request for a damaged item",
  "order_id": "ORD-67890",
  "root_cause": "Item arrived damaged; photos attached",
  "actions_taken": [
    "Verified customer via get_customer",
    "Confirmed order via lookup_order",
    "Offered standard replacement — customer insists on refund"
  ],
  "refund_amount": "$89.99",
  "recommended_action": "Approve a full refund",
  "escalation_reason": "Customer requested to speak with a manager"
}
```

Human operator does **not** have full conversation transcript — summary must be complete and self-contained.

---

## 9.4 Confidence Calibration and Human Oversight

### For Data Extraction Systems

1. **Field-level confidence scores** per extracted field
2. **Calibration** using labeled validation sets to tune thresholds
3. **Routing:**
   - High confidence + stable accuracy → automated processing
   - Low confidence or ambiguous sources → human review

### Stratified Random Sampling
- Even for high-confidence extractions, regularly audit a sample
- Aggregate 97% accuracy can hide 40% errors for particular document type
- Analyze accuracy by **document type** and **field**, not only overall

---

## Exam Scenarios: Escalation Calibration

**Problem:** 55% resolution (target 80%). Escalates simple cases, handles complex policy exceptions autonomously.

**Fix:** Explicit escalation criteria with few-shot examples showing when to escalate vs resolve.

**NOT:** Self-rated confidence, sentiment analysis, separate classifier.

---

## Ambiguous Customer Match

**Problem:** `get_customer` returns multiple matches, agent picks most recent order → wrong account 15% of time.

**Fix:** Request additional identifier (email, phone, order number) when multiple matches.

**NOT:** Confidence scoring, returning single "most likely" match, few-shot alone.

---

## Memory Aids

| Trigger | Action |
|---------|--------|
| "Get me a manager" | Immediate escalate |
| Policy gap (competitor pricing) | Escalate |
| Multiple matches | Ask for identifier |
| Dissatisfaction (no manager request) | Acknowledge + offer resolution |
| Financial threshold | Hook enforcement |
| Low calibration | Few-shot escalation criteria |
