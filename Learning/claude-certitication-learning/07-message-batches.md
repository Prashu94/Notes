# Chapter 7: Message Batches API

**Official docs:** [Message Batches](https://platform.claude.com/docs/en/build-with-claude/message-batches)

---

## 7.1 Overview

The Message Batches API submits batches of requests for **asynchronous processing**.

| Attribute | Value |
|-----------|-------|
| **Savings** | **50%** compared to synchronous calls |
| **Processing window** | Up to **24 hours** (no latency SLA guarantee) |
| **Multi-turn tool calling** | **Not supported** (one request = one response) |
| **Correlation** | `custom_id` field links request and response |

---

## 7.2 When to Use Batch API vs Synchronous API

| Task | API | Why |
|------|-----|-----|
| Pre-merge PR check | **Synchronous** | Developer waiting; 24h unacceptable |
| Overnight tech-debt report | **Batch** | Needed by morning; 50% savings |
| Weekly security audit | **Batch** | Not urgent; 50% savings |
| Interactive code review | **Synchronous** | Immediate response required |
| Processing 10,000 documents | **Batch** | Bulk processing; significant savings |

### Three-Workflow Example (Exam)

| Workflow | API |
|----------|-----|
| PR style checks (blocks merge) | Synchronous |
| Weekly security audit | Batch |
| Nightly test generation | Batch |

### Manager Proposal Trap

"Move both pre-merge check AND overnight report to Batch API for 50% savings."

**Answer:** Batch only for overnight report. Pre-merge is blocking — 24h window unacceptable.

---

## 7.3 Using `custom_id`

```json
{
  "custom_id": "doc-invoice-2024-001",
  "params": {
    "model": "claude-sonnet-4-6",
    "max_tokens": 1024,
    "messages": [{"role": "user", "content": "Extract data from: ..."}]
  }
}
```

`custom_id` allows you to:
- Link result to original document
- On failure, re-submit only failed documents
- Avoid re-processing successful documents

---

## 7.4 Handling Failures in Batches

1. Submit batch of 100 documents
2. 95 succeed; 5 fail (context limit exceeded)
3. Identify failures by `custom_id`
4. Modify strategy (split long documents into chunks)
5. Re-submit only the 5 failed documents

---

## 7.5 SLA Planning

If you need result in 30 hours and Batch API can take up to 24 hours:

```
Submission window = 30 - 24 = 6 hours
```

Batches must be submitted no later than 24 hours before deadline. For frequent submissions, split into 4-hour windows.

---

## Primary Technical Limitation (Exam Favorite)

**Iterative tool-calling workflows are incompatible with Batch API.**

The async "fire-and-forget" model cannot:
1. Intercept a tool call mid-request
2. Execute the tool
3. Return results for Claude to continue analysis

This is the **primary** limitation — not missing correlation IDs, not missing tool definitions, not just latency.

---

## Memory Aids

| Signal | Answer |
|--------|--------|
| Developer waiting at merge | Synchronous |
| Overnight / weekly report | Batch |
| 50% savings | Batch |
| Multi-turn tool calling in one request | NOT Batch |
| Re-process only failures | `custom_id` |
| Up to 24h processing | Batch (no SLA) |
