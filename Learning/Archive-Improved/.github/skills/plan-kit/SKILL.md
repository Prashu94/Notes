---
name: "plan-kit"
description: "AIKit planning and blueprint skill. Use when creating blueprint.yaml, tech-decisions.yaml (ADRs), db-schema.yaml, and api-contracts.yaml from all prior kit outputs. Updates cross-module blueprint registry. Prerequisite: design-kit completed."
argument-hint: "module=<module-id>"
---

# Plan Kit Skill

Consolidates all prior kit outputs into a machine-readable blueprint for dev-kit, test-kit, and deploy-kit.

## When to Use
- After design-kit completes
- When formalizing architecture decisions as ADRs
- When creating database schema and API contracts
- When accumulating cross-module shared components

## Procedure

### Step 1 — Read All Artifacts
Load (from paths in config.yaml):
- `requirements.md`, `BRD.md`, `business-rules.md`, `workflows.md`
- `epics.md`, `features.md`, `stories.md`, `tech-stack.md`
- `architecture.md`, `db-design.md`, `diagrams/`
- `aikit/blueprint/cross-cutting.yaml`

### Step 2 — Generate Blueprint
Invoke `@plan-blueprint` (mode: generate-blueprint).
Follow: [Blueprint Schema](./references/blueprint-schema.md)
Output: `blueprint.yaml`

### Step 3 — Tech Decisions (ADRs)
Invoke `@plan-blueprint` (mode: tech-decisions).
Output: `tech-decisions.yaml`

### Step 4 — Database Schema
Invoke `@plan-blueprint` (mode: db-schema).
Output: `db-schema.yaml`

### Step 5 — API Contracts
Invoke `@plan-blueprint` (mode: api-contracts).
Output: `api-contracts.yaml`

### Step 6 — Cross-Module Updates
Invoke `@plan-blueprint` (mode: cross-cutting-update).
Follow: [Cross-Module Guide](./references/cross-module-guide.md)
Update: `aikit/blueprint/cross-cutting.yaml`, `module-registry.yaml`, `modules/<id>.yaml`

### Step 7 — Complete
Update config.yaml, stage-tracker, audit.log.

## Reference Files
- [Blueprint Schema](./references/blueprint-schema.md) — Full blueprint.yaml structure
- [Cross-Module Guide](./references/cross-module-guide.md) — How to manage cross-module dependencies
