# Claude Certified Architect — Foundations Learning Guide

A comprehensive, travel-friendly study guide based on the official **Claude Certified Architect — Foundations** exam guide. Every concept, domain, scenario, and practice question pattern from the source material is covered here.

## How to Use This Guide (While Traveling)

1. **Start with** [00-exam-overview.md](./00-exam-overview.md) — exam format, domains, and all 6 scenarios.
2. **Study Part I (Theory)** in order — chapters 01–13 build foundational knowledge.
3. **Review Part II (Domains)** — maps theory to the 5 weighted exam domains.
4. **Drill** [practice-exam-insights.md](./practice-exam-insights.md) — 72 questions with answer patterns.
5. **Memorize** [quick-reference-cheat-sheet.md](./quick-reference-cheat-sheet.md) before the exam.
6. **Hands-on** [practical-exercises.md](./practical-exercises.md) when you have a laptop.

## Exam at a Glance

| Parameter | Value |
|-----------|-------|
| Question type | Multiple choice (1 correct out of 4) |
| Score range | 100–1000 |
| **Passing score** | **720** |
| Guessing penalty | **None** — answer every question |
| Scenarios | 4 out of 6 randomly selected |

## Domain Weights

| # | Domain | Weight |
|---|--------|--------|
| 1 | Agent architecture and orchestration | **27%** |
| 2 | Tool design and MCP integration | **18%** |
| 3 | Claude Code configuration and workflows | **20%** |
| 4 | Prompt engineering and structured output | **20%** |
| 5 | Context management and reliability | **15%** |

## Guide Structure

### Part I — Theory Foundations

| File | Topics |
|------|--------|
| [01-claude-api-fundamentals.md](./01-claude-api-fundamentals.md) | Messages API, roles, stop_reason, system prompt, context window |
| [02-tools-and-tool-use.md](./02-tools-and-tool-use.md) | tool_use, tool_choice, JSON schemas, syntax vs semantic errors |
| [03-claude-agent-sdk.md](./03-claude-agent-sdk.md) | Agent loops, AgentDefinition, subagents, hooks, sessions |
| [04-model-context-protocol.md](./04-model-context-protocol.md) | MCP servers, tools, resources, isError, configuration |
| [05-claude-code-configuration.md](./05-claude-code-configuration.md) | CLAUDE.md, rules, skills, planning mode, CI/CD |
| [06-prompt-engineering.md](./06-prompt-engineering.md) | Few-shot, explicit criteria, chaining, validation, self-correction |
| [07-message-batches.md](./07-message-batches.md) | Batch API, custom_id, SLA planning, when to use |
| [08-task-decomposition.md](./08-task-decomposition.md) | Fixed pipelines, dynamic decomposition, multi-pass review |
| [09-escalation-and-hitl.md](./09-escalation-and-hitl.md) | Escalation triggers, handoff protocols, confidence calibration |
| [10-error-handling.md](./10-error-handling.md) | Error categories, anti-patterns, structured subagent errors |
| [11-context-management.md](./11-context-management.md) | Case facts, trimming, scratchpads, subagent delegation |
| [12-preserving-provenance.md](./12-preserving-provenance.md) | Attribution, conflicts, dates, content-type rendering |
| [13-claude-code-builtin-tools.md](./13-claude-code-builtin-tools.md) | Read, Write, Edit, Bash, Grep, Glob selection |

### Part II — Exam Domain Notes

| File | Weight |
|------|--------|
| [domains/domain-1-agent-architecture.md](./domains/domain-1-agent-architecture.md) | 27% |
| [domains/domain-2-tool-design-mcp.md](./domains/domain-2-tool-design-mcp.md) | 18% |
| [domains/domain-3-claude-code.md](./domains/domain-3-claude-code.md) | 20% |
| [domains/domain-4-prompt-engineering.md](./domains/domain-4-prompt-engineering.md) | 20% |
| [domains/domain-5-context-reliability.md](./domains/domain-5-context-reliability.md) | 15% |

### Practice & Reference

| File | Purpose |
|------|---------|
| [practice-exam-insights.md](./practice-exam-insights.md) | All 72 practice questions — patterns and why answers are correct |
| [quick-reference-cheat-sheet.md](./quick-reference-cheat-sheet.md) | One-page decision trees and exam traps |
| [official-documentation-links.md](./official-documentation-links.md) | Every official link from the exam guide |
| [practical-exercises.md](./practical-exercises.md) | 4 hands-on exercises mapped to domains |

## Out of Scope (Will NOT Be on Exam)

- Fine-tuning or custom model training
- API authentication, billing, account management
- Deploying/hosting MCP servers (infrastructure)
- Claude's internal architecture, RLHF, Constitutional AI
- Embedding models, vector DB implementation
- Computer use, Vision, streaming API
- Rate limiting, OAuth, cloud-provider configs
- Prompt caching implementation details
- Token counting algorithms

## Preparation Checklist

- [ ] Build an agent with Claude Agent SDK (full loop + subagents)
- [ ] Configure Claude Code for a real project (CLAUDE.md, rules, skills, MCP)
- [ ] Design MCP tools with differentiated descriptions and structured errors
- [ ] Build a data extraction pipeline (tool_use + validation + batch)
- [ ] Practice few-shot prompting and multi-pass code review
- [ ] Study context management (case facts, scratchpads, subagent delegation)
- [ ] Understand escalation patterns and confidence-based routing
- [ ] Complete the 60-question practice test in this guide
