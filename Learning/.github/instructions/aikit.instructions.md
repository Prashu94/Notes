---
description: "Use when working with any aikit kit (requirement-kit, review-kit, design-kit, plan-kit, dev-kit, test-kit, deploy-kit). Covers aikit conventions, config.yaml structure, stage gating, audit logging, blueprint management, and cross-module patterns."
name: "AIKit Conventions"
---

# AIKit Conventions

## Config.yaml is the Single Source of Truth

Every kit MUST:
1. Read `aikit/config.yaml` at startup.
2. Resolve all input and output paths from `config.yaml` — never hardcode paths.
3. Check prerequisite stages in `stages` block before proceeding.
4. Update `stages.<kit>.status` to `in-progress` when starting.
5. Update `stages.<kit>.status` to `completed` or `failed` when done.
6. Append to `aikit/logs/audit.log` for every significant action.
7. Update `aikit/logs/stage-tracker.yaml` on stage transitions.

## Stage Gate Check Pattern

Before any kit runs its main logic:

```
1. Read aikit/config.yaml
2. For each prerequisite in stages.<this_kit>.prerequisites:
   - Read aikit/logs/stage-tracker.yaml
   - If prerequisite.status != "completed": WARN user, offer to proceed anyway
3. Update stage-tracker: set status = "in-progress", started_at = now()
4. Increment run_count
```

## Audit Log Format

```
[ISO-8601] [KIT-NAME] [MODULE-ID] [ACTION] [STATUS] message
```

Actions: START, FILE, ARTIFACT, SUBAGENT, QUEUE, GATE, COMPLETE, ERROR

## Queue Mechanism for Sub-Agents

To prevent context window overflow, each kit MUST use a queue pattern:

```
1. Build a work queue (list of items: files, stories, services, etc.)
2. Process queue items in batches (default batch size: 3-5 items)
3. For each batch: invoke a focused sub-agent with ONLY that batch's context
4. Collect sub-agent output, append to growing artifact
5. Log each batch completion to audit.log
6. Continue until queue is empty
```

Never load ALL requirements/stories/services into a single agent context.

## Greenfield vs Brownfield Mode

- **Greenfield** (`module.type: greenfield`): Create all artifacts from scratch.
- **Brownfield** (`module.type: brownfield`):
  - Read `inputs.existing_codebase` path
  - Read `aikit/blueprint/cross-cutting.yaml` for shared components
  - Read `aikit/blueprint/modules/` for all prior module blueprints
  - Identify reuse opportunities BEFORE generating new code

## Incremental Updates (Adding Stories/Requirements to Existing Module)

When `stages.<kit>.run_count > 0`:
1. Read existing artifact files (do not overwrite, APPEND/MERGE)
2. Add `[INCREMENTAL - <date>]` section heading to appended content
3. Update `module.updated_at` in config.yaml
4. Only process new/changed input files (compare against last run artifacts)

## Cross-Module Blueprint Updates

After plan-kit completes, ALWAYS:
1. Update `aikit/blueprint/modules/<module-id>.yaml` with this module's blueprint snapshot
2. Scan for shared components and update `aikit/blueprint/cross-cutting.yaml`
3. Update `aikit/blueprint/module-registry.yaml` with this module's status

## Output File Naming

- Requirements: `requirements.md`, `BRD.md`, `business-rules.md`, `workflows.md`
- Review: `epics.md`, `features.md`, `stories.md`, `tech-stack.md`, `clarifications.md`
- Design: `architecture.md`, `diagrams/<name>.mmd`, `scaffold/<service>/`, `ux-stubs/<page>/`
- Plan: `blueprint.yaml`, `tech-decisions.yaml`, `db-schema.yaml`, `api-contracts.yaml`
- Dev: `src/<service>/`, `build-report.md`
- Test: `test-cases/<story-id>/`, `test-report.md`, `coverage-report.md`, `gate-report.md`
- Deploy: `terraform/`, `helm/`, `deployment-guide.md`
