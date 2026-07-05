# Exam Overview & Scenarios

## Certification Purpose

The **Claude Certified Architect — Foundations** certification confirms you can make sound trade-off decisions when implementing real-world Claude-based solutions. The exam tests:

- **Claude Code** — CLAUDE.md, MCP servers, Agent Skills, planning mode
- **Claude Agent SDK** — multi-agent orchestration, subagents, tool integration, lifecycle hooks
- **Claude API** — Messages API, tool_use, structured output
- **Model Context Protocol (MCP)** — tools and resources for backend integration

## Target Candidate Profile

Ideal candidate: **solution architect** with **6+ months** hands-on experience designing and shipping production Claude applications.

Required experience areas:
- Multi-agent orchestration, subagent delegation, lifecycle hooks
- CLAUDE.md, MCP servers, Agent Skills, planning mode
- MCP tools and resources for backend integration
- JSON schemas, few-shot examples, data extraction templates
- Long documents, multi-agent context passing
- CI/CD: automated code review, test generation
- Error handling, human-in-the-loop, escalation

---

## Exam Format

| Parameter | Value |
|-----------|-------|
| Question type | Multiple choice (1 of 4) |
| Scoring | 100–1000 scale |
| **Passing score** | **720** |
| Guessing penalty | **None** — always answer |
| Scenarios per exam | **4 of 6** (randomly selected) |

---

## Five Exam Domains

| Domain | Weight | Core Topics |
|--------|--------|-------------|
| 1. Agent architecture and orchestration | **27%** | Agent loops, coordinator/subagent, Task tool, hooks, sessions |
| 2. Tool design and MCP integration | **18%** | Tool descriptions, isError, tool_choice, MCP config, built-in tools |
| 3. Claude Code configuration and workflows | **20%** | CLAUDE.md hierarchy, skills, rules, planning mode, CI/CD |
| 4. Prompt engineering and structured output | **20%** | Few-shot, JSON schemas, validation/retry, batch processing |
| 5. Context management and reliability | **15%** | Context window, escalation, error propagation, provenance |

---

## Six Exam Scenarios

You will encounter **4 of these 6** on any given exam. Study all six.

### Scenario 1: Customer Support Agent

**Setup:** Agent handles returns, billing disputes, account issues using Claude Agent SDK.

**MCP tools:** `get_customer`, `lookup_order`, `process_refund`, `escalate_to_human`

**Target:** 80%+ first-contact resolution with appropriate escalation

**Key exam themes:**
- Tool sequencing (verify customer before order operations)
- Tool description quality and misrouting
- Escalation calibration (when to escalate vs resolve)
- Programmatic enforcement via hooks vs prompt instructions
- Case facts block for preserving transactional details
- Multi-issue request decomposition
- Structured handoff on escalation

---

### Scenario 2: Code Generation with Claude Code

**Setup:** Accelerate development — code generation, refactoring, debugging, documentation.

**Key exam themes:**
- Custom slash commands in `.claude/commands/` (team-shared via VCS)
- CLAUDE.md hierarchy (user vs project vs directory)
- `.claude/rules/` with YAML `paths` frontmatter
- Skills with `context: fork`, `allowed-tools`, `argument-hint`
- Planning mode vs direct execution
- Personal skills in `~/.claude/skills/` with different names
- MCP server configuration in `.mcp.json` with `${ENV_VAR}`

---

### Scenario 3: Multi-Agent Research System

**Setup:** Coordinator delegates to specialized subagents — web research, document analysis, synthesis, report generation.

**Requirement:** Complete reports with citations

**Key exam themes:**
- Hub-and-spoke architecture (coordinator as central hub)
- Explicit context passing to subagents (no automatic inheritance)
- Parallel Task spawning
- Coordinator task decomposition breadth (don't decompose too narrowly)
- Structured error propagation from subagents
- Coverage annotations in synthesis
- Provenance preservation (claim → source mappings)
- Lost-in-the-middle mitigation in aggregated inputs
- Least-privilege tool access per subagent

---

### Scenario 4: Developer Productivity Tools

**Setup:** Help engineers explore unfamiliar codebases, generate boilerplate, automate routine tasks.

**Tools:** Built-in (Read, Write, Bash, Grep, Glob) + MCP servers

**Key exam themes:**
- Incremental investigation (Grep → Read → Grep → Read)
- Tool selection: Glob for file patterns, Grep for content search
- Edit vs Read+Write fallback
- Explore subagent for verbose discovery
- Context protection via subagent delegation

---

### Scenario 5: Claude Code for Continuous Integration

**Setup:** Integrate Claude Code into CI/CD for automated code reviews, test generation, PR feedback.

**Requirement:** Minimize false positives; structured output for inline PR comments

**Key exam themes:**
- `-p` / `--print` for non-interactive CI mode
- `--output-format json` + `--json-schema` for structured findings
- Session context isolation (separate instance for review vs generation)
- Message Batches API: 50% savings, up to 24h, no multi-turn tool calling
- Multi-pass review (per-file + integration pass)
- Few-shot examples for actionable feedback format
- Include prior review results to avoid duplicate comments
- Include existing test files to avoid duplicate test suggestions

---

### Scenario 6: Structured Data Extraction

**Setup:** Extract information from unstructured documents, validate with JSON schemas, maintain high accuracy.

**Key exam themes:**
- `tool_use` with JSON schemas for syntactically valid output
- Nullable fields vs required fields (avoid fabrication)
- Enums with `"other"` + detail, `"unclear"` for honest uncertainty
- Validation + retry-with-feedback loops
- Pydantic for structural and semantic validation
- Self-correction (stated_total vs calculated_total)
- Field-level confidence scores and human routing
- Batch processing for bulk document workloads

---

## Exam Decision Framework

When stuck between two answers, ask:

1. **Does this need a deterministic guarantee?** → Hooks / programmatic preconditions (not prompts)
2. **Is this about tool selection?** → Fix descriptions first (lowest effort, highest impact)
3. **Is this about context?** → Case facts, trimming, subagent isolation, position-aware input
4. **Is this about multi-agent?** → Coordinator hub, explicit context, structured errors
5. **Is this about CI/CD?** → `-p` flag, JSON schema output, session isolation
6. **Is this about batch vs sync?** → Blocking = sync; overnight/weekly = batch
7. **Is this about escalation?** → Explicit criteria + few-shot; NOT sentiment or self-confidence

## What's NOT on the Exam

See [README.md](./README.md) for the full out-of-scope list. Key exclusions: fine-tuning, auth/billing, MCP hosting infrastructure, streaming API, computer use, vision, token counting internals.
