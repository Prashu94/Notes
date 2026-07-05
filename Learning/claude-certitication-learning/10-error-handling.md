# Chapter 10: Error Handling in Multi-agent Systems

---

## 10.1 Error Categories

| Category | Examples | Retryable? | Agent Action |
|----------|----------|------------|--------------|
| **Transient** | Timeout, 503, network failure | Yes | Retry with exponential backoff |
| **Validation** | Invalid input, missing required field | No (fix input) | Modify request and retry |
| **Business** | Policy violation, threshold exceeded | No | Explain to user; propose alternative |
| **Permission** | Access denied | No | Escalate |

---

## 10.2 Error-handling Anti-patterns

| Anti-pattern | Problem | Correct Approach |
|--------------|---------|------------------|
| Generic status "search unavailable" | Coordinator can't decide recovery | Return error type, query, partial results, alternatives |
| Silent suppression (empty = success) | Coordinator thinks no matches | Distinguish "no results" from "search failure" |
| Abort whole workflow on one failure | Lose all partial results | Continue with partial results; annotate gaps |
| Infinite retries in subagent | Latency, wasted resources | Local recovery (1–2 retries), then propagate to coordinator |

---

## 10.3 Structured Subagent Error

```json
{
  "status": "partial_failure",
  "failure_type": "timeout",
  "attempted_query": "AI impact on music industry 2024",
  "partial_results": [
    {"title": "AI Music Generation Report", "url": "...", "relevance": 0.8}
  ],
  "alternative_approaches": [
    "Try a narrower query: 'AI music composition tools'",
    "Use an alternative data source"
  ],
  "coverage_impact": "Not covered: AI impact on music production"
}
```

Coordinator decides: retry? use partial? different subagent? continue with gap?

---

## 10.4 Coverage Annotations in Final Synthesis

```markdown
## Report: AI Impact on Creative Industries

### Visual Art (FULL COVERAGE)
[research results]

### Music (PARTIAL COVERAGE — search agent timeout)
[partial results]
⚠️ Note: coverage for this section is limited due to timeout in search agent.

### Literature (FULL COVERAGE)
[research results]
```

---

## Local Recovery vs Coordinator Escalation

### PDF Processing Failures (Exam)

Subagent fails on corrupted PDFs, password-protected files, parsing hangs. Currently any exception terminates subagent.

**Fix:** Implement local recovery in subagent for transient failures; escalate to coordinator only errors it cannot resolve, with attempted steps and partial results.

**NOT:** Dedicated error-handling agent with shared queue; always return success with error metadata; coordinator pre-validates all documents.

### Corrupted PDF

**Fix:** Return error with context to coordinator — let coordinator decide skip, alternative parsing, or notify user.

**NOT:** Silently skip; infinite retries; terminate entire workflow.

---

## Conflicting Data from Sources

Two credible sources: government report 40% growth vs industry analysis 12%.

**Fix:** Complete analysis with both numbers, explicitly annotate conflict with source attribution, let coordinator reconcile before synthesis.

**NOT:** Pick most credible via heuristics; pass both without conflict marking; stop and escalate immediately.

---

## Memory Aids

| Situation | Approach |
|-----------|----------|
| Subagent timeout | Structured error to coordinator |
| Mixed-quality inputs to synthesis | Coverage annotations |
| Transient PDF parse failure | Local recovery first |
| Timeout vs 0 results | Different coordinator actions |
| Corrupted file | Error with context to coordinator |
