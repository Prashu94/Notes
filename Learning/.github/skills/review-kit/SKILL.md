---
name: "review-kit"
description: "AIKit review and story generation skill. Use when conducting BA/architect requirement clarification, selecting tech stack, and generating Epics, Features, User Stories with BDD acceptance criteria. Invoked by review-kit agent. Prerequisite: requirement-kit completed."
argument-hint: "module=<module-id>"
---

# Review Kit Skill

Transforms requirement artifacts into actionable Agile work items and confirms technology decisions.

## When to Use
- After requirement-kit completes
- When BA/architect need to clarify requirements interactively
- When generating Epics, Features, Stories with acceptance criteria
- When selecting tech stack for the module

## Procedure

### Step 1 — Read Artifacts
From `aikit/config.yaml` paths, read:
- `requirements.md`, `BRD.md`, `business-rules.md`, `workflows.md`

### Step 2 — Clarification Session
Invoke `@review-clarifier` (mode: requirement-clarification).
Present questions category by category. Wait for user answers.
Write answers to `clarifications.md`.

### Step 3 — Tech Stack
If technology fields in config.yaml are null:
- Invoke `@review-clarifier` (mode: tech-stack)
- Record decisions in `tech-stack.md` and `config.yaml`

### Step 4 — Generate Epics
Invoke `@review-stories` (mode: generate-epics).
Write to `epics.md`. Aim for 3–7 epics per module.

### Step 5 — Generate Features (Queued)
Queue: all Epics. Batch: 2 epics per call.
Invoke `@review-stories` (mode: generate-features) per batch.
Append to `features.md`.

### Step 6 — Generate Stories (Queued)
Queue: all Features. Batch: 3 features per call.
Invoke `@review-stories` (mode: generate-stories) per batch.
Append to `stories.md`.

### Step 7 — Coverage Check
Every FR-NNN and WF-NNN must map to at least one story.
Report gaps.

### Step 8 — Complete
Update config.yaml, stage-tracker, audit.log.

## Reference Files
- [Epics, Features & Stories Template](./references/epics-features-stories-template.md)
- [Tech Stack Guide](./references/tech-stack-guide.md)
