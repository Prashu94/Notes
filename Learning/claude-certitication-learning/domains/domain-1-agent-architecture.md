# Domain 1: Agent Architecture and Orchestration (27%)

**Highest weighted domain — study thoroughly.**

---

## 1.1 Designing Agentic Loops

**Key knowledge:**
- Agent loop: send request → check `stop_reason` (`tool_use` vs `end_turn`) → execute tools → append results → repeat
- Tool results appended to conversation history
- Model-driven (Claude chooses next tool) vs hard-coded decision trees

**Key skills:**
- Continue loop when `stop_reason = "tool_use"`; stop on `"end_turn"`
- Append tool results between iterations

**Anti-patterns:** Parsing text for completion; arbitrary iteration limits

---

## 1.2 Orchestrating Multi-agent Systems

**Key knowledge:**
- Hub-and-spoke: coordinator owns communication, error handling, routing
- Subagents have **isolated context** — no automatic history inheritance
- Coordinator: decompose, delegate, aggregate, dynamic subagent selection
- Risk of overly narrow decomposition

**Key skills:**
- Split research coverage to minimize duplication
- Iterative refinement loops (coordinator evaluates, re-routes)
- Route all communication through coordinator

---

## 1.3 Subagent Calls, Context Passing, Spawning

**Key knowledge:**
- `Task` tool spawns subagents; coordinator `allowedTools` must include `"Task"`
- Context must be **explicitly** in prompt
- `AgentDefinition`: descriptions, system prompts, tool constraints
- `fork_session` for exploring alternatives

**Key skills:**
- Include full prior agent outputs in subagent prompt
- Structured formats separating data from metadata
- Parallel subagents via multiple `Task` calls in one turn
- Coordinator prompts in terms of goals/quality criteria, not step-by-step

---

## 1.4 Multi-step Workflows with Enforcement

**Key knowledge:**
- Programmatic enforcement (hooks, preconditions) vs prompt guidance
- Prompts insufficient for deterministic guarantees (identity before financial ops)
- Structured handoff on escalation

**Key skills:**
- Preconditions blocking `process_refund` until `get_customer` returns verified ID
- Decompose multi-aspect requests into separate items
- Structured escalation summaries

---

## 1.5 Agent SDK Hooks

**Key knowledge:**
- `PostToolUse` intercepts results before model consumes
- Outgoing interception enforces compliance (block refunds > threshold)
- Hooks = deterministic; prompts = probabilistic

**Key skills:**
- PostToolUse for normalizing dates (Unix → ISO 8601)
- Interception hooks redirect to escalation
- Choose hooks over prompts for guaranteed compliance

---

## 1.6 Task Decomposition Strategies

**Key knowledge:**
- Fixed pipelines (prompt chaining) vs dynamic adaptive decomposition
- Prompt chaining: per-file analysis then integration pass

**Key skills:**
- Chaining for predictable reviews; dynamic for open-ended investigations
- Split large reviews: per-file + cross-file integration
- Open-ended: map structure first, then prioritized plan

---

## 1.7 Session State, Resuming, Forking

**Key knowledge:**
- `--resume <session-name>` continues named sessions
- `fork_session` creates independent branches
- Inform agent about file changes when resuming
- New session with summary > resuming with stale results

**Key skills:**
- `--resume` for ongoing investigations
- `fork_session` to compare approaches in parallel
- Choose resume vs new session based on staleness

---

## Top Exam Answers for Domain 1

| Question Pattern | Answer |
|------------------|--------|
| Agent skips verification step | Programmatic precondition (hook) |
| Agent loop stop condition | `stop_reason == "end_turn"` |
| Subagent missing context | Explicit context in Task prompt |
| Research covers only subset | Coordinator decomposition too narrow |
| Subagent timeout | Structured error to coordinator |
| Synthesis needs simple fact check | Limited `verify_fact` tool (least privilege) |
| Date format inconsistency | PostToolUse hook |
| Parallel research duplication | Coordinator partitions space before delegating |
