# Chapter 1: Claude API — Fundamentals of Model Interaction

**Official docs:** [Messages API](https://platform.claude.com/docs/en/api/messages) | [Prompt Engineering](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview)

---

## 1.1 API Request Structure

The Claude API follows a **request–response model**. Each Messages API request includes:

```json
{
  "model": "claude-sonnet-4-6",
  "max_tokens": 1024,
  "system": "You are a helpful assistant.",
  "messages": [
    {"role": "user", "content": "Hi!"},
    {"role": "assistant", "content": "Hello!"},
    {"role": "user", "content": "How are you?"}
  ],
  "tools": [...],
  "tool_choice": {"type": "auto"}
}
```

### Key Fields

| Field | Purpose |
|-------|---------|
| `model` | Model selection: `claude-opus-4-6`, `claude-sonnet-4-6`, `claude-haiku-4-5` |
| `max_tokens` | Maximum tokens in the response |
| `system` | System prompt — defines model behavior (separate from messages) |
| `messages` | **Full conversation history** — you must send complete history every request |
| `tools` | Definitions of available tools |
| `tool_choice` | Tool selection strategy (`auto`, `any`, forced) |

**Critical:** The model does **not** persist state between requests. Each API call is independent.

---

## 1.2 Message Roles

The `messages` array uses three roles:

| Role | Description |
|------|-------------|
| `user` | User messages |
| `assistant` | Model responses (included when sending history) |
| `tool` | Tool call results (appears as `tool_result` content block) |

**Exam trap:** Forgetting to send full conversation history breaks coherence and tool loop continuity.

---

## 1.3 The `stop_reason` Field

The response includes `stop_reason` — why the model stopped generating:

| Value | Description | Action |
|-------|-------------|--------|
| `"end_turn"` | Model finished its response | Show result to user; **stop the agent loop** |
| `"tool_use"` | Model wants to call a tool | Execute tool, append result, **continue loop** |
| `"max_tokens"` | Token limit reached | Response truncated; increase limit |
| `"stop_sequence"` | Stop sequence encountered | Handle per application logic |

### Agent Loop Control

For agentic systems, `"tool_use"` and `"end_turn"` control the loop:

```
1. Send request with tools
2. Check stop_reason:
   - "tool_use" → execute tool → append result → go to step 1
   - "end_turn" → task complete → present to user
```

**Anti-patterns (avoid on exam):**
- Parsing assistant text for "Task completed"
- Using `max_iterations=5` as primary stop condition
- Checking whether assistant produced text as completion signal

**Correct approach:** Only reliable completion signal is `stop_reason == "end_turn"`.

---

## 1.4 System Prompt

The system prompt:
- Is **not** part of the `messages` array — passed in `system` field
- Has **priority** over user messages
- Is loaded once and applies throughout the conversation
- Defines role, constraints, and output format

### Exam Trap: Unintended Tool Associations

System prompt wording can create unintended tool associations.

**Example:** "Always verify the customer" → model overuses `get_customer` even when unnecessary.

**Example:** Word "account" in system prompt → 78% of the time calls `get_customer` first, even for order queries.

**Fix:** Review system prompt for keyword-sensitive routing instructions that override clear tool descriptions.

---

## 1.5 Context Window

The context window = total tokens the model processes at once:

- System prompt
- Full message history
- Tool definitions
- Tool results

### Key Context Window Problems

#### 1. Lost-in-the-Middle Effect
Models reliably process information at the **start and end** of long inputs but miss details in the **middle**.

**Mitigation:**
- Place key information near beginning or end
- Add key-findings summary at the start of aggregated inputs
- Use explicit section headings for navigation

#### 2. Accumulation of Tool Results
Every tool call adds output to context. If a tool returns 40+ fields but only 5 matter, most context is wasted.

**Mitigation:** PostToolUse hooks to trim tool results to relevant fields.

#### 3. Progressive Summarization
When compressing history, numeric values, percentages, and dates get lost → vague summaries ("about", "roughly", "a few").

**Mitigation:** Extract transactional facts into a persistent "case facts" block outside summarized history.

---

## Memory Aids

| Concept | Remember |
|---------|----------|
| State | API is stateless — send full history every call |
| Loop control | `stop_reason`: `tool_use` = continue, `end_turn` = stop |
| System prompt | Can accidentally steer tool selection via keywords |
| Context | Start/end reliable; middle unreliable; summarization loses numbers |

## Related Chapters

- [02-tools-and-tool-use.md](./02-tools-and-tool-use.md) — tool_use, tool_choice
- [11-context-management.md](./11-context-management.md) — production context strategies
