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

## Snapshot & Rollback

### Snapshot (taken automatically before every kit run)

Before any kit writes its first output file, it MUST create a snapshot of all existing output files for that kit's output directory:

```
Snapshot path: aikit/outputs/<module-id>/snapshots/<kit-name>/<ISO-date>T<HH-MM-SS>/
```

Copy every file currently in the kit's output dir into the snapshot folder (preserve sub-directory structure). If the output dir does not yet exist (first run), no snapshot is needed.

Also snapshot the two tracking files:
- `aikit/logs/stage-tracker.yaml` → snapshot folder as `stage-tracker.yaml`
- `aikit/inputs/<module-id>/config.yaml` → snapshot folder as `config.yaml`

Log the snapshot: `[ISO-8601] [KIT-NAME] [MODULE] [SNAPSHOT] [completed] Snapshot saved to aikit/outputs/<module-id>/snapshots/<kit>/<timestamp>/`

### Rollback (user-triggered)

When the user says **"rollback <kit-name>"** or **"rollback <kit-name> to <timestamp>"**:

```
1. List available snapshots in aikit/outputs/<module-id>/snapshots/<kit-name>/
   - If no timestamp specified: use the most recent snapshot
   - If timestamp specified: use that exact folder
2. Display the snapshot timestamp and list of files to be restored — ask user to confirm: "Restore these N files from snapshot <timestamp>? (yes/no)"
3. On confirmation:
   a. Copy all files from the snapshot folder back to their original output paths (overwrite current)
   b. Restore stage-tracker.yaml from snapshot
   c. Restore config.yaml from snapshot
   d. Log: [ISO-8601] [KIT-NAME] [MODULE] [ROLLBACK] [completed] Rolled back to snapshot <timestamp>
4. Report to user: "Rollback complete. <kit-name> stage is now restored to its state at <timestamp>."
```

### Listing Snapshots

When the user says **"list snapshots"** or **"list snapshots for <kit-name>"**:
- List all folders under `aikit/outputs/<module-id>/snapshots/<kit-name>/`
- Show: snapshot timestamp, number of files, and the stage status captured in the snapshot's `stage-tracker.yaml`

### Snapshot Retention

Keep the last **5 snapshots** per kit per module. When a 6th snapshot is created, delete the oldest automatically. Log the deletion: `[SNAPSHOT] [cleanup] Deleted oldest snapshot <timestamp> (kept 5 most recent)`

## Amendment Mode

Amendment is a **targeted, interactive edit** of an already-completed kit — without requiring a full rollback and re-run. It is the preferred option when the user wants to change specific parts of the kit's output rather than regenerate everything.

### Triggering Amendment

When the user says **"amend <kit-name>"** or **"amend <kit-name> for <module-id>"**:

```
1. Verify the kit's status in stage-tracker.yaml. Only kits with status = "completed" can be amended.
   - If status != "completed": inform user and suggest running the kit first.
2. Take a snapshot (same as the automatic pre-run snapshot — see Snapshot section above).
3. Enter Interactive Amendment Interview:
   a. Display a summary of the kit's current output files with a one-line description of each.
   b. Ask: "What would you like to change? You can specify:
        - A file to update (e.g., 'update stories.md')
        - A section within a file (e.g., 'change the tech stack database layer')
        - A specific item (e.g., 'amend US-007', 'remove FEAT-012', 'add a new epic for reporting')
      Enter your changes, or type 'done' when finished."
   c. Collect all requested changes before proceeding.
   d. For each change, confirm scope: "You've asked to [description of change]. Does this look right? (yes / edit)"
4. Apply all confirmed changes to the relevant output files (PATCH only — do not regenerate unaffected content).
5. Update `module.updated_at` in config.yaml.
6. Keep `stages.<kit>.status = "completed"` and increment `run_count`.
7. Log: [ISO-8601] [KIT-NAME] [MODULE] [AMEND] [completed] Amended: <brief summary of changes>
8. Report to user: list every file modified and a one-line summary of what changed in each.
```

### Amendment vs Incremental Update vs Rollback + Re-run

| Scenario | Use |
|---|---|
| Add new requirements/stories to an existing completed kit | **Incremental Update** (run_count > 0 path) |
| Change or correct specific content in completed kit output | **Amendment** |
| Undo all changes and restore to a previous state | **Rollback** |
| Regenerate entire kit output from scratch | **Rollback** → re-run |

### Amendment Audit Actions

Add `AMEND` to the set of valid audit log actions. Each amended file gets its own log entry:
```
[ISO-8601] [KIT-NAME] [MODULE] [AMEND] [completed] Modified <filename>: <change summary>
```

## Audit Log Format

```
[ISO-8601] [KIT-NAME] [MODULE-ID] [ACTION] [STATUS] message
```

Actions: START, FILE, ARTIFACT, SUBAGENT, QUEUE, GATE, COMPLETE, ERROR, SNAPSHOT, ROLLBACK, AMEND

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
