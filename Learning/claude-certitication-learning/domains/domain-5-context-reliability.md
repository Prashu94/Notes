# Domain 5: Context Management and Reliability (15%)

---

## 5.1 Managing Conversation Context

**Key knowledge:**
- Progressive summarization loses numbers, dates, percentages
- Lost-in-the-middle: start/end reliable, middle unreliable
- Tool outputs accumulate disproportionately
- Must send full history in API requests

**Key skills:**
- Case facts block outside summarized history
- Trim verbose tool outputs
- Key findings at beginning with section headings
- Subagents include metadata (dates, sources) in structured output

---

## 5.2 Escalation Patterns

**Key knowledge:**
- Triggers: explicit human request, policy gaps, inability to progress
- Immediate vs attempt-to-resolve escalation
- Sentiment and self-confidence unreliable
- Multiple matches → ask for identifiers

**Key skills:**
- Explicit escalation criteria with few-shot
- Immediate escalation on explicit human request
- Escalate on policy ambiguity
- Ask for identifiers on multiple matches

---

## 5.3 Error Propagation in Multi-agent Systems

**Key knowledge:**
- Structured error context enables coordinator recovery
- Distinguish access failures from empty results
- Generic errors hide context
- Silent suppression and full abort are anti-patterns

**Key skills:**
- Return failure type, attempted query, partial results, alternatives
- Local recovery in subagents; propagate non-recoverable
- Coverage annotations in synthesis

---

## 5.4 Context in Large Codebases

**Key knowledge:**
- Long sessions → unstable answers, "typical patterns" instead of specifics
- Scratchpad files preserve findings
- Subagent delegation isolates verbose output
- Structured state persistence for crash recovery

**Key skills:**
- Subagents for specific questions
- Scratchpad files for key findings
- Summarize before spawning next-phase subagents
- `/compact` during long investigations

---

## 5.5 Human Oversight and Confidence Calibration

**Key knowledge:**
- Aggregate 97% accuracy can mask 40% errors per document type
- Stratified random sampling for high-confidence extractions
- Field-level confidence calibration on labeled sets
- Validate by document type and field before automating

**Key skills:**
- Stratified sampling for new error patterns
- Analyze accuracy by document type and field
- Field-level confidence scores with calibrated thresholds
- Route low-confidence to human review

---

## 5.6 Preserving Provenance

**Key knowledge:**
- Attribution lost without claim → source mappings
- Conflicting statistics: annotate, don't arbitrarily choose
- Publication dates prevent temporal misinterpretation

**Key skills:**
- Subagents output claim → source mappings
- Separate stable findings from disputed
- Preserve conflicting values with annotations
- Render by content type

---

## Top Exam Answers for Domain 5

| Question Pattern | Answer |
|------------------|--------|
| Lost discount % after summarization | Case facts block |
| Synthesis misses middle content | Key findings at top + headings |
| 155K tokens to synthesis | Structured upstream output |
| Conflicting source statistics | Preserve both with attribution |
| Multiple customer matches | Ask for additional identifier |
| High FP erodes trust | Disable noisy categories temporarily |
| Subagent timeout in synthesis | Coverage annotations |
