# Practice Exam — Key Insights (72 Questions)

This summarizes all **12 example questions** and **60 practice test questions** from the official guide, organized by scenario with the correct answer pattern and reasoning.

---

## Customer Support Agent (Questions 1–3, 46–60)

| # | Situation | Correct Answer | Why |
|---|-----------|----------------|-----|
| 1 | 12% skip `get_customer`, call `lookup_order` with name only | **Programmatic precondition** blocking `lookup_order`/`process_refund` until verified ID | Deterministic guarantee; prompts can't enforce sequence |
| 2 | Calls `get_customer` instead of `lookup_order` for orders | **Expand tool descriptions** with formats, examples, boundaries | Descriptions = primary selection mechanism |
| 3 | 55% resolution, wrong escalation calibration | **Explicit escalation criteria + few-shot** | Addresses unclear decision boundaries |
| 46 | `get_customer` instead of `lookup_order` for order status | **Check tool descriptions first** | First diagnostic for wrong tool selection |
| 47 | Multi-issue messages, 58% accuracy | **Few-shot for multi-issue decomposition** | Agent handles single issues well; needs pattern guidance |
| 48 | Complex billing: 12+ tool calls, redundant lookups | **Decompose + parallel investigation with shared context** | Eliminates redundant retrieval |
| 49 | 55% resolution, wrong escalation | **Explicit escalation criteria + few-shot** | Not sentiment, confidence, or classifier |
| 50 | When to escalate after having all data | **Competitor price matching (policy gap)** | Policy silent on competitor matching |
| 51 | 12% skip verification before order ops | **Programmatic precondition** | Same as Q1 |
| 52 | Correct resolution but poor explanations | **Self-critique stage** (evaluator-optimizer) | Catches case-specific explanation gaps |
| 53 | Sequential tool calls when both needed | **Prompt to bundle tool requests in one turn** | Claude can request multiple tools at once |
| 54 | Discount % lost after summarization | **Case facts block** outside summarized history | Summarization inherently loses precise details |
| 55 | Multiple customer matches, 15% wrong picks | **Ask for additional identifier** | User has definitive identity knowledge |
| 56 | "Account" keyword steers to `get_customer` | **System prompt keyword-sensitive instructions** | 78% vs 93% pattern indicates prompt routing |
| 57 | Minimal similar tool descriptions | **Expand descriptions** with formats, examples, boundaries | First step before few-shot or routing layer |
| 58 | Agent loop stop condition | **`stop_reason`: `tool_use` continue, `end_turn` stop** | Only reliable structured signal |
| 59 | Inconsistent date formats from MCP tools | **PostToolUse hook** for normalization | Centralized, deterministic; works on third-party tools |
| 60 | Few-shot for ambiguous tool selection | **4–6 targeted ambiguous examples with rationale** | Teaches comparative decision process |

---

## Code Generation with Claude Code (Questions 4–6, 31–45)

| # | Situation | Correct Answer | Why |
|---|-----------|----------------|-----|
| 4 | Team `/review` command | **`.claude/commands/` in project repo** | VCS-shared, available on clone |
| 5 | Monolith → microservices (dozens of files) | **Planning mode** | Large changes, architectural decisions |
| 6 | Different conventions, tests co-located | **`.claude/rules/` with glob patterns** | Path-based auto-application |
| 31 | API transform output inconsistent | **2–3 concrete input-output examples** | Removes prose ambiguity |
| 32 | Slack integration, ambiguous approach | **Planning mode** to evaluate options | Multiple valid approaches |
| 33 | 400-line CLAUDE.md, mixed content | **Standards in CLAUDE.md + Skills for workflows** | Always-load vs on-demand |
| 34 | Monolith → microservices | **Planning mode** | Same as Q5 |
| 35 | `/analyze-codebase` pollutes session | **`context: fork`** in skill frontmatter | Isolates verbose output |
| 36 | Personal `/commit` customization | **`~/.claude/skills/my-commit`** (different name) | Project skills take precedence over same name |
| 37 | New dev missing team guidance | **Move from user `~/.claude/CLAUDE.md` to project** | User-level not shared |
| 38 | Endpoint examples only for generation | **Skill invoked on demand** | Loads context only when needed |
| 39 | Migration skill: missing args, context leak, destructive ops | **`argument-hint` + `context: fork` + `allowed-tools`** | Three problems, three config features |
| 40 | Cross-cutting conventions (distributed tests) | **`.claude/rules/` with glob patterns** | Same as Q6 |
| 41 | Team `/review` command location | **`.claude/commands/` in repo** | Same as Q4 |
| 42 | 500-line CLAUDE.md organization | **`.claude/rules/` topical files** | testing.md, api-conventions.md, etc. |
| 43 | `/explore-alternatives` pollutes implementation | **`context: fork`** | Isolates exploration context |
| 44 | Team GitHub MCP, personal tokens | **`.mcp.json` with `${GITHUB_TOKEN}`** | VCS config + env var secrets |
| 45 | 120-file refactor, Phase 1 fills context | **Explore subagent for Phase 1** | Isolates verbose discovery |

---

## Multi-agent Research System (Questions 7–9, 1–15)

| # | Situation | Correct Answer | Why |
|---|-----------|----------------|-----|
| 7 | Reports cover only visual art | **Coordinator decomposition too narrow** | Subagents executed correctly |
| 8 | Web-search timeout error propagation | **Structured error context to coordinator** | Failure type, query, partial results, alternatives |
| 9 | Synthesis verification overhead (85% simple) | **Limited `verify_fact` tool for synthesis** | Least privilege; coordinator for complex 15% |
| 1 | Conflicting statistics from sources | **Both values with conflict annotation to coordinator** | Preserve attribution; coordinator reconciles |
| 2 | Next step after subagents complete | **Coordinator passes to synthesis agent** | Hub-and-spoke pattern |
| 3 | PDF parsing failures, excessive coordinator involvement | **Local recovery in subagent; escalate unrecoverable** | Handle at lowest capable level |
| 4 | Only visual art in "creative industries" report | **Coordinator decomposition too narrow** | Same as Q7 |
| 5 | Mixed-quality inputs to synthesis | **Coverage annotations** | Graceful degradation with transparency |
| 6 | Corrupted PDF | **Return error with context to coordinator** | Coordinator decides skip/retry/notify |
| 7 | `analyze_content` vs `analyze_document` overlap | **Rename to `extract_web_results` + clarify description** | Eliminates semantic overlap |
| 8 | Why coordinator as central hub | **Observe interactions, uniform error handling, control info flow** | Primary advantages of star topology |
| 9 | Web-search timeout | **Structured error context** | Same as Q8 |
| 10 | `fetch_url` misused for web search | **Replace with `load_document` validating URL format** | Constrains capability at interface |
| 11 | Duplicate research between agents | **Coordinator partitions research space before delegating** | Prevents duplication before work begins |
| 12 | Timeout vs "0 results" | **Distinguish access failure from valid empty result** | Different coordinator actions |
| 13 | Synthesis misses middle 50K tokens | **Key-findings summary at start + section headings** | Mitigates lost-in-the-middle |
| 14 | 155K tokens to synthesis (best under 50K) | **Upstream agents return structured data** | Fix at source, not intermediate summarizer |
| 15 | Synthesis verification loops | **Limited `verify_fact` tool** | Same as Q9 |

---

## Claude Code for CI/CD (Questions 10–12, 16–30)

| # | Situation | Correct Answer | Why |
|---|-----------|----------------|-----|
| 10 | CI pipeline hangs | **`claude -p "..."`** | Documented non-interactive mode |
| 11 | Move both workflows to Batch API | **Batch only for overnight report; sync for pre-merge** | 24h window unacceptable for blocking |
| 12 | 14-file PR inconsistent review | **Per-file pass + integration pass** | Addresses attention dilution |
| 16 | Narrative output, need inline PR comments | **`--output-format json --json-schema`** | Enforces structured CLI output |
| 17 | Self-review misses own issues | **Second independent Claude instance** | Avoids confirmation bias |
| 18 | Iterative tool-calling + batch evaluation | **Batch can't execute tools mid-request** | Primary technical limitation |
| 19 | Three CI workflows API selection | **Sync for PR checks; batch for weekly audit + nightly tests** | Match latency requirements |
| 20 | Inconsistent actionable feedback | **3–4 few-shot examples** with exact format | More reliable than instructions alone |
| 21 | Which mode for batch processing | **Deep analysis only** (overnight, polling) | Pre-merge blocks developers |
| 22 | Vague comment checking criteria | **Explicit: flag only when comment contradicts code** | Replaces vague instruction |
| 23 | High FP erodes developer trust | **Temporarily disable high-FP categories** | Stops trust erosion immediately |
| 24 | Duplicate test suggestions | **Include existing test file in context** | Claude needs to know what's covered |
| 25 | Duplicate comments after new commits | **Include prior review findings; report only new/unresolved** | Claude distinguishes fixed vs new |
| 26 | CI hangs waiting for input | **`claude -p`** | Same as Q10 |
| 27 | 14-file PR review | **Per-file + integration pass** | Same as Q12 |
| 28 | High investigation time per finding | **Include rationale and confidence in each finding** | All findings visible; faster triage |
| 29 | Category-specific false positive rates | **Disable high-FP categories temporarily** | Same as Q23 |
| 30 | Manager proposes batch for both workflows | **Batch only for tech debt; sync for pre-merge** | Same as Q11 |

---

## Answer Selection Heuristics

When two answers seem plausible:

1. **Prefer root-cause fixes** over workarounds (descriptions before classifiers)
2. **Prefer deterministic** over probabilistic (hooks before prompts)
3. **Prefer simplest proportional fix** (few-shot before new infrastructure)
4. **Prefer least privilege** (scoped tools, limited verify_fact)
5. **Prefer coordinator hub** over direct subagent communication
6. **Prefer structured errors** over generic messages
7. **Prefer sync for blocking**, batch for overnight/weekly
8. **Avoid:** sentiment analysis, self-confidence routing, routing classifiers, larger context as fix for attention dilution
