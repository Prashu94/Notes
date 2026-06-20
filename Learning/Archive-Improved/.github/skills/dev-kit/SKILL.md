---
name: "dev-kit"
description: "AIKit code generation skill. Use when generating backend service code, frontend page implementation, database migrations, and validating local builds. Reads blueprint.yaml and fills in scaffold TODOs. Supports Spring Boot, FastAPI, NestJS, Express, Angular, React, all major databases. Prerequisite: plan-kit completed."
argument-hint: "module=<module-id> [story=US-NNN] [service=<service-id>]"
---

# Dev Kit Skill

Generates complete, buildable implementation code from the blueprint.

## When to Use
- After plan-kit completes
- When generating backend service implementation
- When implementing frontend pages from UX stubs
- When creating database migrations
- When validating local builds

## Procedure

### Step 1 — Read Blueprint
- `blueprint.yaml` — service definitions, stories map, API contracts ref
- `tech-decisions.yaml` — versions, patterns to follow
- `db-schema.yaml` — tables and constraints
- `api-contracts.yaml` — endpoint signatures
- `aikit/blueprint/cross-cutting.yaml` — shared APIs/models to REUSE

### Step 2 — Generate DB Migrations
Invoke `@dev-backend` (task: database).
Output: `scaffold/database/migrations/`
Follow: [Backend Codegen Guide](./references/backend-codegen-guide.md)

### Step 3 — Generate Backend Services (Queued)
Queue: services from `blueprint.yaml`. One service per sub-agent call.
Invoke `@dev-backend` per service.
Output: fills in `scaffold/<service-name>/` TODOs.

### Step 4 — Generate Frontend Pages (Queued)
Queue: pages from `blueprint.frontend.pages`. 2 pages per sub-agent.
Invoke `@dev-frontend` per batch.
Output: fills in `ux-stubs/<page>/` TODOs.
Follow: [Frontend Codegen Guide](./references/frontend-codegen-guide.md)

### Step 5 — Build Validation (Per Service)
For each generated service, invoke `@dev-buildcheck`.
Auto-fix up to 3 iterations.
Follow: [Build Validation Guide](./references/build-validation-guide.md)
Output: `build-report.md`

### Step 6 — Complete
Update config.yaml, stage-tracker, audit.log.

## Reference Files
- [Backend Codegen Guide](./references/backend-codegen-guide.md)
- [Frontend Codegen Guide](./references/frontend-codegen-guide.md)
- [Build Validation Guide](./references/build-validation-guide.md)
