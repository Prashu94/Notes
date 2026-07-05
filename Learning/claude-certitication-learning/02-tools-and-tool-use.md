# Chapter 2: Tools and `tool_use`

**Official docs:** [Tool Use](https://platform.claude.com/docs/en/build-with-claude/tool-use)

---

## 2.1 What is `tool_use`?

`tool_use` allows Claude to call external functions. The model does **not** run code directly — it generates a structured tool call request; **your code** executes it and returns the result.

---

## 2.2 Tool Definition

Each tool is defined using a JSON schema:

```json
{
  "name": "get_customer",
  "description": "Finds a customer by email or ID. Returns the customer profile, including name, email, order history, and account status. Use this tool BEFORE lookup_order to verify the customer's identity. Accepts an email (format: user@domain.com) or a numeric customer_id.",
  "input_schema": {
    "type": "object",
    "properties": {
      "email": {"type": "string", "description": "Customer email"},
      "customer_id": {"type": "integer", "description": "Numeric customer ID"}
    },
    "required": []
  }
}
```

### Critically Important: Tool Descriptions

**The description is the primary selection mechanism.** An LLM chooses tools based on descriptions. Minimal descriptions ("Retrieves customer information") lead to mistakes when tools overlap.

#### Include in Every Description:
1. What the tool does and returns
2. Input formats and example values
3. Edge cases and constraints
4. When to use this tool vs similar alternatives

#### Avoid:
- Identical or overlapping descriptions across tools
- If `analyze_content` and `analyze_document` have nearly identical descriptions → model confuses them

#### Built-in vs MCP Tools:
Agents may prefer built-in tools (Read, Grep) over MCP tools with similar functionality.

**Fix:** Strengthen MCP tool descriptions — highlight concrete advantages, unique data, or context built-in tools cannot provide.

### Exam Pattern: First Step for Tool Misrouting

When agent consistently picks wrong tool → **expand tool descriptions first** (lowest effort, highest impact).

Before: few-shot examples, routing classifiers, merging tools.

---

## 2.3 The `tool_choice` Parameter

Controls how the model selects tools:

| Value | Behavior | When to Use |
|-------|----------|-------------|
| `{"type": "auto"}` | Model decides tool or text | Default for most cases |
| `{"type": "any"}` | Model **must** call some tool | Guaranteed structured output |
| `{"type": "tool", "name": "extract_metadata"}` | Model **must** call specific tool | Forced first step / execution order |

### Important Scenarios

- `tool_choice: "any"` + multiple extraction tools → model picks best one, still get structured output
- Forced selection → guarantee specific first action (e.g., `extract_metadata` before enrichment)

### Exam Trap: Too Many Tools

18 tools per agent vs 4–5 → **reduces** tool selection reliability. Scope tools to role-relevant subset.

---

## 2.4 JSON Schemas for Structured Output

Using `tool_use` with JSON schemas is the **most reliable** way to obtain structured output. It:

- ✅ Guarantees syntactically valid JSON
- ✅ Enforces required structure
- ❌ Does **not** guarantee semantic correctness (values can still be wrong)

### Schema Design Example

```json
{
  "type": "object",
  "properties": {
    "category": {
      "type": "string",
      "enum": ["bug", "feature", "docs", "unclear", "other"]
    },
    "category_detail": {
      "type": ["string", "null"],
      "description": "Details if category = 'other' or 'unclear'"
    },
    "severity": {
      "type": "string",
      "enum": ["critical", "high", "medium", "low"]
    },
    "confidence": {
      "type": "number",
      "minimum": 0,
      "maximum": 1
    },
    "optional_field": {
      "type": ["string", "null"],
      "description": "Null if the information was not found in the source"
    }
  },
  "required": ["category", "severity"]
}
```

### Schema Design Rules

| Rule | Why |
|------|-----|
| Required vs optional | Mark required only if always available — required fields push model to fabricate when data missing |
| Nullable fields | Use `"type": ["string", "null"]` — model returns `null` instead of hallucinating |
| Enum with `"other"` | Add `"other"` + detail string to avoid losing data outside predefined categories |
| Enum with `"unclear"` | Honest `"unclear"` better than wrong category |

---

## 2.5 Syntax vs Semantic Errors

| Error Type | Example | Mitigation |
|------------|---------|------------|
| **Syntax** | Invalid JSON, wrong field type | `tool_use` with JSON schema (eliminates) |
| **Semantic** | Totals don't add up, value in wrong field, hallucination | Validation checks, retry with feedback, self-correction |

### Self-Correction Pattern

```json
{
  "stated_total": "$150.00",
  "calculated_total": "$145.00",
  "conflict_detected": true,
  "line_items": [
    {"name": "Widget A", "price": 75.00},
    {"name": "Widget B", "price": 70.00}
  ]
}
```

Extract both stated and computed values — if they differ, `conflict_detected` triggers handling.

---

## Tool Renaming Pattern (Exam Favorite)

**Problem:** `analyze_content` (web-search) vs `analyze_document` (doc analysis) — nearly identical descriptions.

**Fix:** Rename web-search tool to `extract_web_results` with description: "processes and returns information retrieved from web search and URLs."

**Also:** Replace general `fetch_url` with constrained `load_document` that validates URLs point to document formats.

---

## Memory Aids

| When you see... | Think... |
|-----------------|----------|
| Wrong tool selected | Fix descriptions first |
| Need guaranteed JSON | `tool_use` + schema |
| Need forced tool call | `tool_choice: "any"` or forced specific tool |
| Need guaranteed sequence | Hooks/preconditions, not prompts |
| Valid JSON, wrong values | Validation + retry-with-feedback |
| 18 tools on one agent | Too many — scope to 4–5 role-relevant |
