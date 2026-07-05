# Chapter 4: Model Context Protocol (MCP)

**Official docs:** [MCP](https://modelcontextprotocol.io/) | [Tools](https://modelcontextprotocol.io/docs/concepts/tools) | [Resources](https://modelcontextprotocol.io/docs/concepts/resources) | [Servers](https://modelcontextprotocol.io/docs/concepts/servers)

---

## 4.1 What is MCP?

The Model Context Protocol (MCP) is an open protocol for connecting external systems to Claude. Three primary resource types:

| Type | Purpose | Example |
|------|---------|---------|
| **Tools** | Functions agent calls to perform actions | CRUD, API calls, command execution |
| **Resources** | Data agent reads for context | Documentation, DB schemas, content catalogs |
| **Prompts** | Predefined prompt templates | Common task templates |

---

## 4.2 MCP Servers

An MCP server is a process implementing the MCP protocol and providing tools/resources.

When connected:
- All tools discovered automatically
- Tools from all connected servers available simultaneously
- Tool descriptions determine how model uses them

**Prefer community MCP servers** for standard integrations (Jira, GitHub, Slack). Build custom only for unique team-specific workflows.

---

## 4.3 Configuring MCP Servers

### Project Configuration (`.mcp.json`) — Team Usage

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "jira": {
      "command": "npx",
      "args": ["-y", "mcp-server-jira"],
      "env": {
        "JIRA_TOKEN": "${JIRA_TOKEN}"
      }
    }
  }
}
```

| Point | Detail |
|-------|--------|
| Location | Project root, managed in version control |
| Secrets | `${GITHUB_TOKEN}` env var substitution — tokens not committed |
| Availability | All project contributors |

### User Configuration (`~/.claude.json`) — Personal/Experimental

- Stored in user's home directory
- Not shared via version control
- Suitable for personal experiments and testing

### Exam Answer Pattern: Team GitHub MCP

**Correct:** Add to project `.mcp.json` with `${GITHUB_TOKEN}` env var substitution + document in README.

**Wrong:** Commit tokens, placeholder tokens, per-developer only in user scope (loses team consistency).

---

## 4.4 The `isError` Flag in MCP

When MCP tool encounters error, use `isError: true` in response.

### Structured Error (Good)

```json
{
  "isError": true,
  "content": {
    "errorCategory": "transient",
    "isRetryable": true,
    "message": "The service is temporarily unavailable. Timeout while calling the orders API.",
    "attempted_query": "order_id=12345",
    "partial_results": null
  }
}
```

### Generic Error (Anti-pattern)

```json
{
  "isError": true,
  "content": "Operation failed"
}
```

Generic errors give agent no information for decision-making.

### Error Categories

| Category | Examples | Retryable? | Action |
|----------|----------|------------|--------|
| **Transient** | Timeout, 503, network failure | Yes | Retry with backoff |
| **Validation** | Invalid input, missing field | No (fix input) | Modify request and retry |
| **Business** | Policy violation, threshold exceeded | No | Explain to user; alternative |
| **Permission** | Access denied | No | Escalate |

### Distinguish Access Failures from Empty Results

- **Timeout** (access failure) → coordinator should decide to retry
- **"0 results"** (valid empty) → successful query, informative finding

**Exam trap:** Reporting both as failures, or returning empty results marked as success.

---

## 4.5 MCP Resources

Resources = data agent requests for context **without taking actions**:

- Content catalogs (project tasks, hierarchical navigation)
- Database schemas
- Documentation (API references, internal guides)
- Issue/task summaries

**Advantage:** Agent doesn't need exploratory tool calls to understand what data exists. Resource provides immediate "map."

---

## Error Handling Anti-patterns

| Anti-pattern | Problem | Correct Approach |
|--------------|---------|------------------|
| Generic "search unavailable" | Coordinator can't decide recovery | Return error type, query, partial results, alternatives |
| Silent suppression (empty = success) | Coordinator thinks no matches | Distinguish "no results" from "search failure" |
| Abort whole workflow on one failure | Lose all partial results | Continue with partial results; annotate gaps |
| Infinite retries in subagent | Latency, wasted resources | Local recovery (1–2 retries), then propagate to coordinator |

---

## Structured Subagent Error (Exam Pattern)

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

Coordinator can decide: retry? use partial results? delegate to different subagent? continue with gap annotation?

---

## Memory Aids

| Concept | Remember |
|---------|----------|
| Team MCP | `.mcp.json` + env vars |
| Personal MCP | `~/.claude.json` |
| isError | Must be structured with category, retryable flag |
| Resources | Read-only context maps — reduce exploratory calls |
| Timeout vs 0 results | Different semantics, different coordinator actions |
