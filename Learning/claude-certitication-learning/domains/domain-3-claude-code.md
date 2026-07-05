# Domain 3: Claude Code Configuration and Workflows (20%)

---

## 3.1 CLAUDE.md Hierarchy and Organization

**Key knowledge:**
- Hierarchy: user (`~/.claude/CLAUDE.md`) → project (`.claude/CLAUDE.md`) → directory-level
- User-level not shared via VCS
- `@path` syntax for modular imports (max depth 5)
- `.claude/rules/` for topic-focused files

**Key skills:**
- Diagnose user-level vs project-level issues
- Use `@./standards/testing.md` for selective inclusion
- Split large CLAUDE.md into `.claude/rules/` files

---

## 3.2 Slash Commands and Skills

**Key knowledge:**
- Project: `.claude/commands/` or `.claude/skills/` (VCS shared)
- User: `~/.claude/commands/` or `~/.claude/skills/`
- SKILL.md frontmatter: `context: fork`, `allowed-tools`, `argument-hint`
- Personal skills need different names

**Key skills:**
- Project commands in `.claude/commands/` for team
- `context: fork` for verbose skills
- `allowed-tools` for security restriction
- `argument-hint` for required parameters

---

## 3.3 Path-specific Rules

**Key knowledge:**
- `.claude/rules/` with YAML `paths` frontmatter
- Rules load only when editing matching files
- Glob patterns for cross-directory conventions (tests)

**Key skills:**
- `paths: ["terraform/**/*"]` for conditional loading
- `**/*.test.tsx` for file-type conventions
- Prefer path rules over directory CLAUDE.md for scattered files

---

## 3.4 Planning Mode vs Direct Execution

**Key knowledge:**
- Planning: large changes, multiple approaches, architecture
- Direct: simple, well-understood, single-file fixes
- Explore subagent isolates verbose discovery

**Key skills:**
- Planning for microservices, 45+ file migrations
- Direct for clear stack trace, single file
- Combined: plan then execute

---

## 3.5 Iterative Refinement

**Key knowledge:**
- Concrete I/O examples most effective
- Test-driven iteration
- Interview pattern for design considerations

**Key skills:**
- 2–3 input/output examples for transformations
- Test sets with edge cases before implementation
- Interview pattern for cache invalidation, failure modes

---

## 3.6 CI/CD Integration

**Key knowledge:**
- `-p` / `--print` for non-interactive mode
- `--output-format json` + `--json-schema`
- Session isolation: separate instance for review
- Include prior review results on re-run

**Key skills:**
- `claude -p` in CI pipelines
- JSON schema for inline PR comments
- Document test standards in CLAUDE.md
- Include existing test files in context

---

## Top Exam Answers for Domain 3

| Question Pattern | Answer |
|------------------|--------|
| Team `/review` command | `.claude/commands/` in repo |
| Tests across codebase | `.claude/rules/` with globs |
| Skill pollutes main context | `context: fork` |
| CI hangs | `-p` flag |
| Structured PR comments | `--output-format json --json-schema` |
| New dev missing rules | Move from user to project CLAUDE.md |
| Monolith → microservices | Planning mode |
| Personal commit skill | `~/.claude/skills/my-commit` (different name) |
| Migration skill 3 issues | argument-hint + context:fork + allowed-tools |
