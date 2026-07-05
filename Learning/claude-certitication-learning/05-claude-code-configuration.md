# Chapter 5: Claude Code — Configuration and Workflows

**Official docs:** [Overview](https://code.claude.com/docs/en/overview) | [Memory/CLAUDE.md](https://code.claude.com/docs/en/memory) | [Skills](https://code.claude.com/docs/en/skills) | [Hooks](https://code.claude.com/docs/en/hooks) | [Sub-agents](https://code.claude.com/docs/en/sub-agents) | [MCP](https://code.claude.com/docs/en/mcp) | [GitHub Actions](https://code.claude.com/docs/en/github-actions) | [Headless](https://code.claude.com/docs/en/headless)

---

## 5.1 The CLAUDE.md Hierarchy

Three-level hierarchy:

```
1. User-level:     ~/.claude/CLAUDE.md
   - Only that user; NOT in VCS
   - Personal preferences and working style

2. Project-level:  .claude/CLAUDE.md  OR  root CLAUDE.md
   - All project contributors; managed via VCS
   - Coding standards, testing, architecture

3. Directory-level: CLAUDE.md in subdirectories
   - Applies when working with files in that directory
   - Conventions for that part of codebase
```

### Common Mistake (Exam Favorite)

New team member doesn't receive project instructions because they were placed in `~/.claude/CLAUDE.md` (user-level) instead of `.claude/CLAUDE.md` (project-level).

**Fix:** Move guidance to project-level file.

---

## 5.2 `@path` Syntax (File Imports)

CLAUDE.md can reference external files for modular configuration:

```markdown
# Project CLAUDE.md
Coding standards are described in @./standards/coding-style.md
Test requirements are in @./standards/testing-requirements.md
Project overview is in @README.md and dependencies are in @package.json
```

### Rules for `@path`
- Use `@` immediately before file path (no space)
- Relative and absolute paths supported
- Relative paths resolved relative to containing file
- Maximum import nesting depth: **5**

---

## 5.3 The `.claude/rules/` Directory

Alternative to monolithic CLAUDE.md — organize rules by topic:

```
.claude/rules/
  testing.md          -- testing conventions
  api-conventions.md  -- API conventions
  deployment.md       -- deployment rules
  react-patterns.md   -- React patterns
```

### YAML Frontmatter with `paths` (Conditional Loading)

```markdown
---
paths: ["src/api/**/*"]
---
For API files, use async/await with explicit error handling.
Each endpoint must return a standard response wrapper.

---
paths: ["**/*.test.tsx", "**/*.test.ts"]
---
Tests must use describe/it blocks.
Use data factories instead of hardcoding.
Do not mock the database—use a test database.
```

**How it works:** Rule loads **only** when Claude Code edits a file matching the `paths` pattern. Saves context and tokens.

### When to Use What

| Approach | Best For |
|----------|----------|
| `.claude/rules/` with `paths` | Conventions across many directories (tests, migrations) |
| Directory-level CLAUDE.md | Conventions tied to specific directory |

**Exam answer:** Tests co-located across codebase → `.claude/rules/` with glob `**/*.test.tsx`

---

## 5.4 Custom Slash Commands and Skills

**Note:** Custom commands (`.claude/commands/`) unified with skills (`.claude/skills/`). Both create `/name` commands. Exam references both formats.

### Project Commands (Shared via VCS)
```
.claude/commands/review.md        -- legacy format
.claude/skills/review/SKILL.md    -- current format
```

### User Commands (Personal)
```
~/.claude/commands/
~/.claude/skills/
```

### Exam: Team `/review` Command
**Answer:** `.claude/commands/` in project repository (version-controlled, available to all on clone).

---

## 5.5 Skills — `.claude/skills/`

Advanced commands with SKILL.md frontmatter:

```markdown
---
context: fork
allowed-tools: ["Read", "Grep", "Glob"]
argument-hint: "Path to the directory to analyze"
---
Analyze the code structure in the specified directory.
Output a report on dependencies and architectural patterns.
```

| Parameter | Description |
|-----------|-------------|
| `context: fork` | Runs in isolated subagent — verbose output doesn't pollute main session |
| `allowed-tools` | Restricts available tools (security) |
| `argument-hint` | Prompts for argument when invoked without parameters |

### Skill vs CLAUDE.md

| Skill | CLAUDE.md |
|-------|-----------|
| On-demand invocation for specific task | Always-loaded general standards |
| Loads context only when needed | Loads every session |

### Personal Skills
Create under `~/.claude/skills/` with **different name** (e.g., `/my-commit` not `/commit`). Project skills take precedence over personal skills with same name.

### Exam: `/migration` Skill Issues

Three problems → three fixes:
1. Missing arguments → `argument-hint` in frontmatter
2. Schema leakage from prior conversations → `context: fork`
3. Destructive operations → `allowed-tools` restricted to file-write only

---

## 5.6 Planning Mode vs Direct Execution

### Planning Mode
- Model only investigates and plans — **no changes**
- Uses Read, Grep, Glob to explore
- Produces implementation plan for user approval
- Safe exploration, no side effects

### When to Use Planning Mode
- Large changes (dozens of files)
- Multiple plausible approaches (microservices boundaries)
- Architectural decisions (framework, structure)
- Unfamiliar codebase
- Library migrations affecting 45+ files
- Ambiguous requirements (Slack integration: webhooks vs bot tokens vs Slack Apps)

### When to Use Direct Execution
- Single-file fixes with clear stack trace
- Adding one validation check
- Well-understood, unambiguous changes

### Combined Approach
1. Planning mode for investigation and design
2. User approves plan
3. Direct execution to implement

### Explore Subagent
- Isolates verbose output from main context
- Returns only summary
- Prevents context-window exhaustion in multi-phase tasks

**Exam:** 120-file error-handling refactor, Phase 1 fills context → Use Explore subagent for discovery, continue design/implementation in main session.

---

## 5.7 The `/compact` Command

- Summarizes prior history to free context window
- Used in long investigation sessions
- **Risk:** Exact numeric values, dates, specific details lost during summarization

---

## 5.8 The `/memory` Command

- Opens CLAUDE.md for editing
- Persists notes, preferences, context across sessions
- Automatically loaded on startup

---

## 5.9 Claude Code CLI for CI/CD

### Non-Interactive Mode: `-p` / `--print`

```bash
claude -p "Analyze this pull request for security issues"
```

- Processes prompt, prints to stdout, exits
- Does not wait for user input
- **Only correct way** to run Claude in CI/CD pipelines

**Exam trap:** `CLAUDE_HEADLESS=true`, `--batch`, redirecting stdin from `/dev/null` — all wrong.

### Structured Output for CI

```bash
claude -p "Review this PR" --output-format json --json-schema '{"type":"object",...}'
```

- `--output-format json` — output in JSON
- `--json-schema` — validate output against schema
- Parse result to post inline PR comments via GitHub API

### Session Context Isolation

Same Claude session that generated code is less effective at reviewing it (retains reasoning, less likely to challenge own decisions). Use **independent instance** for review.

### Preventing Duplicate Comments

When re-reviewing after new commits, include prior review results and instruct Claude to report only new or unresolved issues.

### CLAUDE.md for Large Monolithic Files

**Problem:** 400+ lines mixing standards, review, deployment.

**Answer:** Keep universal standards in CLAUDE.md; create Skills for workflow-specific guidance (PR review, deploy, migrations) invoked on demand.

**Also valid:** Split into `.claude/rules/` topical files (testing.md, api-conventions.md).

---

## Memory Aids

| Question | Answer |
|----------|--------|
| Team command location? | `.claude/commands/` in repo |
| Tests across codebase? | `.claude/rules/` with glob paths |
| Verbose skill pollutes context? | `context: fork` |
| CI hangs waiting for input? | `-p` flag |
| Structured PR comments? | `--output-format json --json-schema` |
| New dev missing instructions? | Check user vs project CLAUDE.md |
| Microservices split? | Planning mode first |
