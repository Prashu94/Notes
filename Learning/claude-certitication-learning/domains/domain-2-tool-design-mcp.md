# Domain 2: Tool Design and MCP Integration (18%)

---

## 2.1 Designing Tool Interfaces

**Key knowledge:**
- Tool descriptions = **primary selection mechanism**
- Include: input formats, examples, edge cases, boundaries
- Overlapping descriptions → misrouting
- System prompt can create unintended tool associations

**Key skills:**
- Distinguish each tool from similar alternatives in description
- Rename to eliminate overlap (`analyze_content` → `extract_web_results`)
- Split general tools into specialized ones

---

## 2.2 Structured Error Responses for MCP

**Key knowledge:**
- `isError` flag in MCP responses
- Transient vs validation vs business vs permission errors
- Generic "Operation failed" prevents recovery
- Retryable vs non-retryable

**Key skills:**
- Return `errorCategory`, `isRetryable`, human-readable message
- `retryable: false` for business-rule violations
- Local recovery in subagents; propagate non-recoverable with partial results
- Distinguish access failures from valid empty results

---

## 2.3 Allocating Tools Across Agents

**Key knowledge:**
- Too many tools (18 vs 4–5) reduces selection reliability
- Scoped tool access per role
- `tool_choice`: `"auto"`, `"any"`, forced `{"type": "tool", "name": "..."}`

**Key skills:**
- Restrict subagent toolset to role-relevant tools
- Replace `fetch_url` with constrained `load_document`
- `tool_choice: "any"` for guaranteed tool call
- Force specific tool for execution order

---

## 2.4 Integrating MCP Servers

**Key knowledge:**
- Project `.mcp.json` for teams vs user `~/.claude.json` for experiments
- `${GITHUB_TOKEN}` env var substitution
- All connected server tools available simultaneously
- MCP resources as content catalogs

**Key skills:**
- Configure shared servers in `.mcp.json` with env-var tokens
- Personal servers in `~/.claude.json`
- Prefer community servers for standard integrations

---

## 2.5 Built-in Tools

**Key knowledge:**
- Grep: content search; Glob: file patterns
- Read/Write: full files; Edit: precise unique-match changes
- Edit fails → Read + Write fallback

**Key skills:**
- Grep for content, Glob for file discovery
- Incremental: Grep entry points → Read → trace flows

---

## Top Exam Answers for Domain 2

| Question Pattern | Answer |
|------------------|--------|
| Wrong tool selected (minimal descriptions) | Expand descriptions first |
| Overlapping tool names | Rename + clarify description |
| Agent misuses general URL tool | Replace with constrained `load_document` |
| MCP tool fails generically | Structured error with category |
| Team GitHub MCP setup | `.mcp.json` + `${GITHUB_TOKEN}` |
| Timeout vs 0 results | Different semantics — retry vs accept |
