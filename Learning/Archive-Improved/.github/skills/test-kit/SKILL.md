---
name: "test-kit"
description: "AIKit test generation and validation skill. Use when generating unit tests, integration tests, running build gates, executing tests, and producing coverage and test reports per user story. Validates all acceptance criteria and business rules are tested. Prerequisite: dev-kit completed."
argument-hint: "module=<module-id> [story=US-NNN]"
---

# Test Kit Skill

Generates tests for every story, validates build gate, runs tests, and produces reports.

## When to Use
- After dev-kit completes
- When generating unit and integration tests per story
- When running build gate validation
- When verifying acceptance criteria coverage

## Procedure

### Step 1 — Read Artifacts
- `stories.md` → story list + ACs + business rules
- `api-contracts.yaml` → endpoint signatures to test
- `blueprint.yaml` → service ↔ story mapping
- `build-report.md` → service build status

### Step 2 — Build Gate
Invoke `@test-validator` (mode: build-gate).
Output: `gate-report.md`
Follow: [Build Gate Guide](./references/build-gate-guide.md)

### Step 3 — Generate Tests (Queued by Story)
Queue: all stories. 1 story per sub-agent.
Invoke `@test-generator` per story.
Output: `test-cases/US-NNN/`
Follow: [Test Strategy Guide](./references/test-strategy-guide.md)

### Step 4 — Run Tests (Per Service)
For each service, invoke `@test-validator` (mode: run-tests).
Append results to `test-report.md`.

### Step 5 — Coverage Analysis
Invoke `@test-validator` (mode: coverage).
Output: `coverage-report.md`

### Step 6 — Complete
Update config.yaml, stage-tracker, audit.log.

## Reference Files
- [Test Strategy Guide](./references/test-strategy-guide.md)
- [Build Gate Guide](./references/build-gate-guide.md)
