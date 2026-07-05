# Quick Reference Cheat Sheet

**Print or save this for last-minute review before the exam.**

---

## Exam Facts
- Passing score: **720** / 1000
- No guessing penalty — **answer everything**
- 4 of 6 scenarios per exam
- Domains: 27% / 18% / 20% / 20% / 15%

---

## Agent Loop
```
stop_reason == "tool_use"  → execute tool → continue
stop_reason == "end_turn"  → STOP (only reliable signal)
```
❌ Don't parse text, don't use max_iterations as primary stop

---

## Hooks vs Prompts
| Need | Use |
|------|-----|
| Financial/legal/safety rules | **Hooks** (100% deterministic) |
| Preferences, formatting | Prompts (~90%) |
| Block refund > $500 | **PreToolUse hook** |
| Normalize date formats | **PostToolUse hook** |
| Force tool sequence | **Precondition hook**, not prompt |

---

## Tool Selection Fix Order
1. **Expand descriptions** (formats, examples, boundaries, when-to-use)
2. Rename overlapping tools (`extract_web_results` not `analyze_content`)
3. Constrain tools (`load_document` not `fetch_url`)
4. Few-shot for ambiguous cases (with rationale)
5. Last resort: routing classifier

---

## tool_choice
| Value | Effect |
|-------|--------|
| `auto` | Model decides tool or text |
| `any` | Must call a tool (guaranteed structured output) |
| `tool` + name | Must call specific tool (forced order) |

---

## JSON Schema Rules
- Required only if always available (else model fabricates)
- Use `["string", "null"]` for missing data
- Add `"other"` + detail, `"unclear"` for honest uncertainty
- Schema fixes **syntax**; validation fixes **semantics**

---

## Multi-Agent Architecture
```
        Coordinator (hub)
       /      |       \
  Subagent1  Subagent2  Subagent3
```
- Subagents: **isolated context** — pass explicitly via Task prompt
- Coordinator `allowedTools` must include **"Task"**
- All communication through coordinator
- Parallel: multiple Task calls in one response
- Narrow decomposition → incomplete coverage

---

## MCP Configuration
| Scope | File | Use |
|-------|------|-----|
| Team | `.mcp.json` | `${GITHUB_TOKEN}` env vars |
| Personal | `~/.claude.json` | Experiments |

**isError response must include:** errorCategory, isRetryable, message, attempted_query, partial_results

**Timeout ≠ "0 results"** — different coordinator actions

---

## Claude Code Hierarchy
```
~/.claude/CLAUDE.md          → personal (NOT in VCS)
.claude/CLAUDE.md            → project (VCS)
CLAUDE.md in subdirs         → directory-specific
.claude/rules/ + paths: []   → conditional by glob
.claude/commands/            → team slash commands
.claude/skills/SKILL.md      → skills with frontmatter
```

### Skill Frontmatter
| Flag | Purpose |
|------|---------|
| `context: fork` | Isolate verbose output in subagent |
| `allowed-tools` | Restrict tool access |
| `argument-hint` | Prompt for required args |

---

## Planning vs Direct
| Planning Mode | Direct Execution |
|---------------|------------------|
| Dozens of files | Single file fix |
| Architecture decisions | Clear stack trace |
| Multiple approaches | Unambiguous change |
| Unfamiliar codebase | Well-understood change |
| 45+ file migrations | One validation check |

---

## CI/CD
```bash
claude -p "prompt"                           # non-interactive (ONLY correct way)
claude -p "..." --output-format json --json-schema '{...}'  # structured output
```
- Review in **separate instance** from generation
- Include **prior review results** on re-run
- Include **existing test files** to avoid duplicates

---

## Batch API
| Attribute | Value |
|-----------|-------|
| Savings | 50% |
| Window | Up to 24h (no SLA) |
| Multi-turn tools | **NOT supported** |
| Correlation | `custom_id` |

| Use Sync | Use Batch |
|----------|-----------|
| Pre-merge checks | Overnight reports |
| Interactive review | Weekly audits |
| Tool-calling workflows | Bulk document processing |

---

## Context Management
| Problem | Fix |
|---------|-----|
| Lost numbers after summarization | **Case facts block** |
| 40+ tool result fields | **PostToolUse trim** |
| Missed middle of long input | **Key findings at top** |
| Verbose discovery | **Subagent / Explore** |
| 155K tokens to synthesis | **Structured upstream output** |
| Long investigation | **Scratchpad file** |
| Context full | `/compact` (loses details) |

---

## Escalation
| Trigger | Action |
|---------|--------|
| "Get me a manager" | **Immediate** escalate |
| Policy gap | Escalate |
| Multiple customer matches | **Ask for identifier** |
| Dissatisfaction (no manager request) | Acknowledge + offer resolution |
| Financial threshold | **Hook** enforcement |

❌ NOT reliable: sentiment, self-confidence 1-10, classifiers

---

## Code Review
```
Pass 1: Each file individually (local issues)
Pass 2: Integration pass (cross-file issues)
```
❌ Bigger context window doesn't fix attention dilution

---

## Built-in Tools
| Need | Tool |
|------|------|
| File by pattern | **Glob** |
| Content search | **Grep** |
| Read full file | **Read** |
| Create file | **Write** |
| Precise edit | **Edit** (Read+Write if non-unique) |
| Run command | **Bash** |

---

## Provenance
- Always: claim → source URL, name, date
- Conflicts: preserve both, don't pick one
- Include dates to avoid false contradictions

---

## Common Wrong Answers
| Trap Answer | Why Wrong |
|-------------|-----------|
| Routing classifier | Overengineering; fix descriptions first |
| Sentiment analysis | Mood ≠ complexity |
| Self-confidence 1-10 | Model confidently wrong |
| Larger context window | Doesn't fix attention quality |
| Three-pass consensus | Suppresses real bugs |
| `CLAUDE_HEADLESS=true` | Doesn't exist |
| `--batch` flag for CI | Doesn't exist |
| Intermediate summarization agent | Fix at source (structured output) |
| Pre-validate all documents at coordinator | Wrong layer for local errors |
