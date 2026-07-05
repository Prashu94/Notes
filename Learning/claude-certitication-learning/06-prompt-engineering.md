# Chapter 6: Prompt Engineering — Advanced Techniques

**Official docs:** [Prompt Engineering](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview) | [Anthropic Cookbook](https://github.com/anthropics/anthropic-cookbook)

---

## 6.1 Few-shot Prompting

Few-shot = including **2–4 input/output examples** in prompt to demonstrate expected behavior.

### Why Few-shot Beats Textual Descriptions
- Vague instruction "be more precise" → many interpretations
- Example unambiguously shows format and decision logic
- Model generalizes pattern to new cases (doesn't just repeat examples)

### Types of Few-shot Examples

#### 1. Ambiguous Scenarios (with rationale)
```text
Request: "My order is broken"
Action: Call get_customer → lookup_order → check status.
Rationale: "broken" may mean damaged item; need order details.

Request: "Get me a manager"
Action: Immediately call escalate_to_human.
Rationale: Customer explicitly requests human. Do not attempt autonomous solve.
```

#### 2. Output Formatting
```json
{
  "location": "src/auth/login.ts:42",
  "issue": "SQL injection in the username parameter",
  "severity": "critical",
  "suggested_fix": "Use a parameterized query"
}
```

#### 3. Acceptable vs Problematic Code
```javascript
// Acceptable (do not flag):
const items = data.filter(x => x.active);

// Problem (flag):
const items = data.filter(x => x.active == true); // Use strict equality ===
```

#### 4. Extraction from Different Document Formats
```text
"As shown in the study (Smith, 2023), the rate is 42%."
→ {"value": "42%", "source": "Smith, 2023", "type": "inline_citation"}

"The rate is 42%. [1]"
→ {"value": "42%", "source": "reference_1", "type": "bibliography"}
```

#### 5. Informal Measurements
```text
"about two handfuls of rice" → {"amount": "~100g", "original_text": "two handfuls", "precision": "approximate"}
"a pinch of salt" → {"amount": "~1g", "original_text": "a pinch", "precision": "approximate"}
```

### Exam: Targeted vs Generic Few-shot

**Best for ambiguous tool selection:** 4–6 examples targeted at ambiguous scenarios with rationale for why one tool over alternatives.

**Less effective:** 10–15 clear unambiguous examples; grouping all scenarios by tool without rationale.

### Format Normalization Rules
Add to prompt when using strict JSON schemas:
```text
Normalization:
- Dates: always ISO 8601 (YYYY-MM-DD)
- Currency: numeric amount + currency code; "five bucks" → {"amount": 5, "currency": "USD"}
- Percentages: decimal fraction; "half" → 0.5
```

---

## 6.2 Explicit Criteria vs Vague Instructions

### Bad (Vague)
```text
Check code comments for accuracy.
Be conservative—report only high-confidence findings.
```

### Good (Explicit Criteria)
```text
Flag a comment as problematic ONLY if:
1. The comment describes behavior that CONTRADICTS the actual code behavior
2. The comment references a non-existent function or variable
3. A TODO/FIXME refers to a bug already fixed in code

Do NOT flag:
- Comments merely stylistically outdated
- Comments with minor wording inaccuracies
- Missing comments (separate category)
```

### Severity Criteria with Examples
```text
CRITICAL: Runtime failure for users
  Example: NullPointerException while processing a payment
HIGH: Security vulnerability
  Example: SQL injection, XSS, missing authorization checks
MEDIUM: Logic bug without immediate impact
  Example: Wrong sorting, off-by-one error
LOW: Code quality
  Example: Duplication, suboptimal algorithm for small data
```

### False Positive Trust Erosion

High false-positive categories (style 52%, docs 48%) erode trust in accurate categories (security 8%).

**Fix:** Temporarily disable high-FP categories while improving prompts. Don't just add confidence scores or uniform strictness reduction.

---

## 6.3 Prompt Chaining

Break complex task into sequence of focused steps:

```text
Step 1: Analyze auth.ts (local issues only) → list of issues
Step 2: Analyze database.ts (local issues only) → list of issues
Step 3: Integration pass (cross-file dependencies) → boundary issues
```

### Why It Matters
- Avoids **attention dilution** — too many files at once → shallow analysis
- Consistent analysis quality per file
- Separate cross-file interaction analysis

### Chaining vs Dynamic Decomposition

| Prompt Chaining | Dynamic Decomposition |
|-----------------|----------------------|
| Predictable, repeatable tasks | Open-ended investigations |
| Code review, file migrations | Subtasks clear only during execution |

---

## 6.4 The "Interview" Pattern

Before implementing, Claude asks clarifying questions:

```text
"Before implementing caching for the API, a few questions:
1. Which cache invalidation strategy—TTL or event-based?
2. Is stale data acceptable when cache unavailable?
3. Per-user or global caching?
4. Expected data volume to cache?"
```

**Useful for:** Unfamiliar domains, tasks with non-obvious implications, multiple viable approaches.

---

## 6.5 Validation and Retry-with-Feedback

```text
Step 1: Extract data from document
Step 2: Validate (Pydantic, JSON Schema, business rules)
Step 3: If error — retry with:
  - Original document
  - Previous (incorrect) extraction
  - Specific error: "Field 'total' = 150, but sum(line_items) = 145. Re-check values."
```

### When Retry Helps
- Format errors (date in wrong format)
- Structural errors (field in wrong location)
- Arithmetic inconsistencies (model can re-check)

### When Retry Does NOT Help
- Information absent from source document
- Required context in external document not provided

### Pydantic (Exam Knowledge)
- **Structural validation:** types, requiredness, enums
- **Semantic validation:** custom validators (sum equals total; start < end)
- **Validate-retry loops:** on failure, construct error message and re-prompt
- **JSON Schema generation:** Pydantic models → JSON Schema for `tool_use`

---

## 6.6 Self-correction

Extract both stated and computed values:

```json
{
  "stated_total": "$150.00",
  "calculated_total": "$145.00",
  "conflict_detected": true
}
```

### Self-Critique Stage (Evaluator-Optimizer)

Agent evaluates draft response for completeness before presenting — catches case-specific gaps in explanations (policy context, timelines, next steps).

---

## Memory Aids

| Situation | Best Technique |
|-----------|----------------|
| Inconsistent output format | Few-shot examples (3–4) |
| Vague review criteria | Explicit criteria with examples |
| 14-file PR review | Per-file pass + integration pass |
| Ambiguous tool selection | Few-shot with rationale at edge cases |
| Wrong comment flagging | Explicit contradiction criteria |
| Developer distrust | Disable noisy categories temporarily |
| API response transformation | Concrete input-output examples |
