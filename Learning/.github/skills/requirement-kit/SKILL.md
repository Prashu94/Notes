---
name: "requirement-kit"
description: "AIKit requirement processing skill. Use when parsing .docx, .xlsx, .csv requirements, extracting business rules, generating BRD, and converting requirements to structured markdown. Invoked by requirement-kit agent. Handles greenfield and brownfield scenarios."
argument-hint: "module=<module-id>"
---

# Requirement Kit Skill

Parses raw requirement source files and produces structured requirement artifacts.

## When to Use
- Processing new requirements for a greenfield module
- Adding requirements to an existing module (incremental)
- Extracting business rules and workflows from requirement documents
- Generating a formal BRD

## Procedure

### Step 1 — Read Config
Read `aikit/config.yaml`. Extract:
- `module.id`, `module.type`
- `inputs.requirements_dir`
- `outputs.requirements.*`
- `logs.audit_log`, `logs.stage_tracker`

### Step 2 — Validate Prerequisites
Check `stages.requirement_kit` in stage-tracker. If run_count > 0, run in incremental mode.

### Step 3 — Queue Files
List all files in `inputs.requirements_dir`. Build ordered queue.
Batch size: **1 file per sub-agent call** (prevents context overflow).

### Step 4 — Parse Each File (Queue)
For each file in queue:
- Invoke `@req-parser` with single file path
- Append output to `outputs.requirements.requirements_md`
- Log: `[REQUIREMENT-KIT] [FILE] [completed] Parsed <filename>`

### Step 5 — Extract Business Rules & Workflows
- Invoke `@req-brd` with task=`extract-rules-and-workflows`
- Output: `business-rules.md`, `workflows.md`

### Step 6 — Generate BRD
- Invoke `@req-brd` with task=`generate-brd`
- Output: `BRD.md`
- Follow: [BRD Template](./references/brd-template.md)

### Step 7 — Complete
- Update config.yaml stage status
- Update stage-tracker.yaml
- Append to audit.log
- Report summary to user

## Reference Files
- [BRD Template](./references/brd-template.md) — Full BRD document structure
- [Business Rules Guide](./references/business-rules-guide.md) — How to identify and classify rules
- [Workflow Extraction Guide](./references/workflow-extraction-guide.md) — How to extract and model workflows
