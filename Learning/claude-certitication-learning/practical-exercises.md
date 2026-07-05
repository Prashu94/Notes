# Practical Exercises

Four hands-on exercises from the official exam guide, mapped to exam domains.

---

## Exercise 1: Multi-tool Agent with Escalation Logic

**Goal:** Design an agent loop with tool integration, structured error handling, and escalation.

**Domains:** 1 (Agent architecture), 2 (Tools and MCP), 5 (Context and reliability)

### Steps

1. **Define 3–4 MCP tools** with detailed descriptions
   - Include two similar tools (e.g., `get_customer` and `lookup_order`) to test tool selection
   - Descriptions must include: what it does, input formats, examples, when-to-use vs alternatives

2. **Implement agent loop** checking `stop_reason`
   - Continue on `"tool_use"`, stop on `"end_turn"`
   - Append tool results to conversation history between iterations

3. **Add structured error responses**
   ```json
   {
     "isError": true,
     "content": {
       "errorCategory": "transient|validation|business|permission",
       "isRetryable": true,
       "message": "Human-readable description",
       "attempted_query": "...",
       "partial_results": null
     }
   }
   ```

4. **Implement interceptor hook**
   - Block operations above threshold (e.g., refunds > $500)
   - Redirect to `escalate_to_human`

5. **Test with multi-aspect requests**
   - "I need a refund for order #1234 and want to update shipping for order #5678"
   - Verify decomposition and correct tool sequencing

### Success Criteria
- [ ] Agent never skips `get_customer` before financial operations (hook enforced)
- [ ] Wrong tool selection fixable by improving descriptions
- [ ] Errors include structured context for recovery decisions
- [ ] Multi-issue requests handled with separated parameters

---

## Exercise 2: Configuring Claude Code for Team Development

**Goal:** Configure CLAUDE.md, custom commands, path-specific rules, and MCP servers.

**Domains:** 3 (Claude Code configuration), 2 (Tools and MCP)

### Steps

1. **Create project-level CLAUDE.md** with universal standards
   - Coding style, testing requirements, project overview
   - Use `@path` imports for modular organization

2. **Create `.claude/rules/` files** with YAML frontmatter
   ```markdown
   ---
   paths: ["src/api/**/*"]
   ---
   API conventions here...

   ---
   paths: ["**/*.test.*"]
   ---
   Test conventions here...
   ```

3. **Create project skill** under `.claude/skills/`
   ```markdown
   ---
   context: fork
   allowed-tools: ["Read", "Grep", "Glob"]
   argument-hint: "Path to analyze"
   ---
   Skill instructions here...
   ```

4. **Configure MCP server** in `.mcp.json`
   ```json
   {
     "mcpServers": {
       "github": {
         "command": "npx",
         "args": ["-y", "@modelcontextprotocol/server-github"],
         "env": { "GITHUB_TOKEN": "${GITHUB_TOKEN}" }
       }
     }
   }
   ```
   - Add personal override in `~/.claude.json` for experiments

5. **Test planning mode vs direct execution**
   - Planning: microservices boundary design
   - Direct: single-file bug fix with stack trace

### Success Criteria
- [ ] New team member clones repo and gets all project instructions
- [ ] Test conventions apply to `**/*.test.tsx` regardless of directory
- [ ] Skill runs in forked context without polluting main session
- [ ] MCP server works with env var token (not committed)

---

## Exercise 3: Structured Data Extraction Pipeline

**Goal:** JSON schemas, `tool_use` for structured output, validation/retry loops, batch processing.

**Domains:** 4 (Prompt engineering), 5 (Context and reliability)

### Steps

1. **Define extraction tool** with JSON schema
   - Required vs optional fields
   - Enums with `"other"` + detail string
   - Nullable fields: `"type": ["string", "null"]`
   - Confidence score per field

2. **Build validation loop**
   ```text
   Extract → Validate (Pydantic) → On failure:
     Retry with: original document + incorrect extraction + specific error
   ```

3. **Add few-shot examples** for different document structures
   - Inline citations vs bibliography references
   - Informal measurements ("two handfuls of rice")

4. **Batch processing** via Message Batches API
   - 100 documents with `custom_id` per document
   - Handle failures: identify by `custom_id`, modify strategy, re-submit only failures

5. **Human routing**
   - Field-level confidence scores
   - Route low-confidence to human review
   - Analyze accuracy by document type

### Success Criteria
- [ ] Output is syntactically valid JSON (schema enforced)
- [ ] Semantic errors caught by validation + retry
- [ ] Batch failures re-processed individually via `custom_id`
- [ ] Low-confidence extractions routed to human review

---

## Exercise 4: Multi-agent Research Pipeline

**Goal:** Subagent orchestration, context passing, error propagation, synthesis with source tracking.

**Domains:** 1 (Agent architecture), 2 (Tools and MCP), 5 (Context and reliability)

### Steps

1. **Build coordinator** with 2+ subagents
   - Coordinator `allowedTools` includes `"Task"`
   - Pass context explicitly in Task prompts (document text, prior results, output format)

2. **Run subagents in parallel**
   - Multiple Task calls in single coordinator response
   - Partition research space to avoid duplication

3. **Require structured subagent output**
   ```json
   {
     "claim": "...",
     "quote": "...",
     "source_url": "...",
     "publication_date": "..."
   }
   ```

4. **Simulate subagent timeout**
   - Return structured error with partial results and alternatives
   - Coordinator continues with coverage annotations

5. **Test conflicting data**
   - Two sources with different statistics
   - Preserve both with attribution
   - Separate confirmed vs disputed findings in final report

### Success Criteria
- [ ] Coordinator decomposes broadly enough (not just visual art for "creative industries")
- [ ] Subagents receive full explicit context
- [ ] Timeout returns structured error, not empty success
- [ ] Final report includes claim → source mappings
- [ ] Conflicting data preserved with attribution, not arbitrarily chosen

---

## Self-Assessment Checklist

After completing all four exercises, verify you can answer:

- [ ] When to use hooks vs prompts vs few-shot?
- [ ] When to use planning mode vs direct execution?
- [ ] When to use Batch API vs synchronous API?
- [ ] How to fix tool misrouting (in order of preference)?
- [ ] How to preserve context across long conversations?
- [ ] When to escalate to a human?
- [ ] How to structure MCP error responses?
- [ ] How to configure team vs personal Claude Code settings?
