# Chapter 3: Claude Agent SDK — Building Agentic Systems

**Official docs:** [Overview](https://platform.claude.com/docs/en/agent-sdk/overview) | [Hooks](https://platform.claude.com/docs/en/agent-sdk/hooks) | [Subagents](https://platform.claude.com/docs/en/agent-sdk/subagents) | [Sessions](https://platform.claude.com/docs/en/agent-sdk/sessions)

---

## 3.1 What is an Agentic Loop?

The agentic loop is the core pattern for autonomous task execution:

```
1. Send request to Claude with tools
2. Receive response
3. Check stop_reason:
   - "tool_use" → execute tool, append result, go to step 1
   - "end_turn" → task complete, show result
4. Repeat until completion
```

**Model-driven approach:** Claude decides which tool to call next based on context and prior results. Differs from hard-coded decision trees.

### Anti-patterns
- Parsing assistant text for completion
- Arbitrary iteration limits as primary stop condition
- Checking for textual content as completion signal

### Correct Approach
Only reliable completion: `stop_reason == "end_turn"`

---

## 3.2 `AgentDefinition` Configuration

```python
agent = AgentDefinition(
    name="customer_support",
    description="Handles customer requests for returns and order issues",
    system_prompt="You are a customer support agent...",
    allowed_tools=["get_customer", "lookup_order", "process_refund", "escalate_to_human"],
    # Coordinator also needs "Task" in allowed_tools
)
```

| Parameter | Purpose |
|-----------|---------|
| `name` / `description` | Agent identification |
| `system_prompt` | Instructions |
| `allowed_tools` | **Principle of least privilege** — only role-relevant tools |

---

## 3.3 Hub-and-Spoke: Coordinator and Subagents

```
         Coordinator
        /     |      \
   Subagent1  Subagent2  Subagent3
    (search)   (analysis)   (synthesis)
```

### Coordinator Responsibilities
- Decompose task into subtasks
- Decide which subagents are needed (dynamic selection)
- Delegate work to subagents
- Aggregate and validate results
- Handle errors and retries
- Communicate results to user

### Critical Principle: Isolated Context

Subagents do **NOT** automatically inherit coordinator's conversation history.

- All required context must be **explicitly passed** in subagent prompt
- Subagents do not share memory across calls
- All communication flows through coordinator (observability + error control)

### Exam Trap: Narrow Decomposition

Coordinator decomposes "creative industries" into only visual art subtopics → misses music, literature, film. Subagents executed correctly — problem is coordinator's decomposition breadth.

---

## 3.4 The `Task` Tool for Spawning Subagents

```python
coordinator_agent = AgentDefinition(
    allowed_tools=["Task", "get_customer"]  # Must include "Task"
)
```

### Explicit Context Passing (Mandatory)

```text
# BAD — subagent has no context
Task: "Analyze the document"

# GOOD — full context in prompt
Task: "Analyze the following document.
Document: [full document text]
Prior search results: [web search results]
Output format requirements: [schema]"
```

### Parallel Spawning

Coordinator can call multiple `Task`s in one response — subagents run concurrently:

```text
Task 1: "Search for articles about X"
Task 2: "Analyze document Y"
Task 3: "Search for articles about Z"
# All three run concurrently
```

### Research Space Partitioning

When web-search and doc-analysis agents duplicate work → coordinator should **partition research space before delegating**, assigning distinct subtopics or source types.

---

## 3.5 Hooks in the Agent SDK

Hooks intercept and transform at specific lifecycle points.

### PostToolUse Hook
Intercepts tool result before model sees it:

```python
@hook("PostToolUse")
def normalize_dates(tool_result):
    # Convert Unix timestamp → ISO 8601
    # Convert "Mar 5, 2025" → "2025-03-05"
    return normalized_result
```

### PreToolUse Hook (Outgoing Interception)
Blocks policy-violating actions:

```python
@hook("PreToolUse")
def enforce_refund_limit(tool_call):
    if tool_call.name == "process_refund" and tool_call.args.amount > 500:
        return redirect_to_escalation(tool_call)
```

### Hooks vs Prompt Instructions

| Attribute | Hooks | Prompt Instructions |
|-----------|-------|---------------------|
| Guarantee | **Deterministic (100%)** | Probabilistic (>90%) |
| When to use | Critical business rules, financial ops, compliance | General preferences, formatting |
| Example | Block refunds > $500 | "Try to solve before escalating" |

**Rule:** When failure has financial, legal, or safety consequences → **use hooks, not prompts**.

### Available SDK Hooks
`PreToolUse`, `PostToolUse`, `Stop`, `SessionStart`, `SessionEnd`, `UserPromptSubmit`, and more.

---

## 3.6 `fork_session` and Session Management

### `--resume <session-name>`
```bash
claude --resume investigation-auth-bug
```
- Continues prior conversation with saved context
- Useful for long investigations across sessions
- **Risk:** Files changed since prior session → stale tool results

### `fork_session`
Creates independent branch from shared context:

```
Codebase investigation
         |
    fork_session
    /           \
Approach A:      Approach B:
Redux            Context API
```
- Both forks inherit context up to branch point
- Afterwards diverge independently
- Useful for comparing approaches

### When to Start New Session Instead of Resuming
- Tool results are stale (files changed)
- Long time passed, context degraded
- Better to restart with summary: "Here is what we found: ..."

### SDK Sessions
Capture `session_id` from first query, then `resume=session_id` for continuation with full context.

---

## Agent SDK vs Client SDK

| Client SDK | Agent SDK |
|------------|-----------|
| You implement the tool loop | Claude handles tools autonomously |
| Direct API access | Built-in tool execution |
| Full control | Faster to build agents |

---

## Memory Aids

| Concept | Key Point |
|---------|-----------|
| Subagent context | Never automatic — always explicit |
| Task tool | Coordinator's `allowed_tools` must include `"Task"` |
| Hooks | Deterministic; use for financial/legal rules |
| Coordinator hub | All communication through coordinator |
| Narrow decomposition | Root cause of incomplete research coverage |
| Parallel tasks | Multiple Task calls in one coordinator response |
