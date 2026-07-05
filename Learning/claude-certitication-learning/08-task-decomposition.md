# Chapter 8: Task Decomposition Strategies

---

## 8.1 Fixed Pipelines (Prompt Chaining)

Each step defined in advance:

```
Document → Metadata extraction → Data extraction → Validation → Enrichment → Final output
```

### When to Use
- Task structure is predictable (reviews always follow same template)
- All steps known up front
- Need stability and reproducibility

---

## 8.2 Dynamic Adaptive Decomposition

Subtasks generated based on intermediate results:

```text
1. "Add tests for a legacy codebase"
2. → Map structure (Glob, Grep)
3. → Found: 3 modules with no tests, 2 with partial coverage
4. → Prioritize: payments module (high risk)
5. → Discovered dependency on external API
6. → Adapt: add mock for external API before writing tests
```

### When to Use
- Open-ended investigative tasks
- Full scope unknown up front
- Each step depends on previous step's results

---

## 8.3 Multi-pass Code Review

For pull requests with 10+ files:

```text
Pass 1 (per-file): Analyze auth.ts → local issues
Pass 1 (per-file): Analyze database.ts → local issues
Pass 1 (per-file): Analyze routes.ts → local issues
...
Pass 2 (integration): Analyze relationships between files
  → Cross-file issues: inconsistent types, circular dependencies
```

### Why Single Pass Over 14 Files Fails
- **Attention dilution:** deep for some, shallow for others
- **Inconsistent comments:** pattern flagged in one file, approved in another
- **Missed bugs:** obvious errors skipped due to cognitive overload

### What Does NOT Fix It
- Larger context window / bigger model
- Requiring developers to split PRs
- Three independent passes requiring consensus (suppresses real bugs)

---

## Comparison Table

| Strategy | Predictability | Best For |
|----------|----------------|----------|
| Fixed pipeline | High | Code review, extraction pipelines |
| Dynamic decomposition | Low | Legacy codebase exploration, test planning |
| Multi-pass review | High | Large PRs (per-file + integration) |

---

## Complex Billing Request Pattern

**Problem:** Agent investigates issues sequentially, redundant `get_customer` calls, 12+ tool calls, 54% success.

**Fix:** Decompose into separate issues, investigate in parallel with shared customer context, synthesize single resolution.

---

## Memory Aids

| Scenario | Strategy |
|----------|----------|
| 14-file PR inconsistent review | Per-file + integration pass |
| Unknown scope test writing | Dynamic decomposition |
| Document extraction pipeline | Fixed pipeline |
| Multi-issue customer message | Decompose + few-shot sequencing |
