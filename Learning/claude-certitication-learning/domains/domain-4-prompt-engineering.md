# Domain 4: Prompt Engineering and Structured Output (20%)

---

## 4.1 Explicit Criteria

**Key knowledge:**
- Explicit criteria > vague instructions
- "Be conservative" worse than concrete categorical criteria
- False positives in some categories undermine trust in accurate ones

**Key skills:**
- Define what to report vs ignore
- Temporarily disable high-FP categories
- Severity criteria with code examples

---

## 4.2 Few-shot Prompting

**Key knowledge:**
- Most effective for consistent, actionable output
- Demonstrates ambiguous case handling
- Generalizes to new patterns; reduces hallucinations

**Key skills:**
- 2–4 targeted examples with rationale
- Format examples (location, issue, severity, fix)
- Acceptable vs problematic code examples
- Extraction from different document structures

---

## 4.3 Structured Output with tool_use

**Key knowledge:**
- `tool_use` + JSON Schema = most reliable structured output
- `tool_choice: "auto"` can return text; `"any"` must call tool
- Schemas eliminate syntax errors, not semantic errors
- Required vs optional; enums with "other" + detail

**Key skills:**
- Parse from `tool_use` results
- `tool_choice: "any"` for guaranteed structured output
- Force specific tool for execution order
- Nullable fields when source may lack information
- `"unclear"` and `"other"` enums

---

## 4.4 Validation, Retries, Feedback Loops

**Key knowledge:**
- Retry-with-feedback: include concrete validation errors
- Retry ineffective when info absent from source
- `detected_pattern` for false-positive analysis
- Semantic vs syntax errors

**Key skills:**
- Retry with document + incorrect extraction + specific error
- Identify when retry won't help
- Self-correction: `calculated_total` vs `stated_total`

---

## 4.5 Batch Processing Strategies

**Key knowledge:**
- 50% savings, up to 24h, no SLA
- Batch for non-blocking; sync for blocking
- No multi-turn tool calling in batch
- `custom_id` for correlation

**Key skills:**
- Sync for blocking; batch for overnight/weekly
- SLA planning with submission windows
- Re-submit only failed documents by `custom_id`

---

## 4.6 Multi-instance and Multi-pass Review

**Key knowledge:**
- Self-review limitation: model won't challenge own reasoning
- Independent review instance finds subtle issues
- Multi-pass: per-file + integration to avoid attention dilution

**Key skills:**
- Second independent instance for review
- Per-file passes + integration pass
- Verification with confidence routing

---

## Top Exam Answers for Domain 4

| Question Pattern | Answer |
|------------------|--------|
| Inconsistent review output | Few-shot examples (3–4) |
| Vague comment checking | Explicit contradiction criteria |
| 14-file PR review | Per-file + integration pass |
| Self-review misses issues | Independent review instance |
| Guaranteed JSON output | tool_use + schema + tool_choice |
| Batch for pre-merge check | NO — use synchronous |
| Iterative tool-calling + batch | Incompatible — no mid-request tools |
