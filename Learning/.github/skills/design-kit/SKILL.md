---
name: "design-kit"
description: "AIKit design skill. Use when creating MMD Mermaid diagrams, microservice architecture scaffolding, frontend SPA/MFE scaffolding, database design, and UX stubs. Invoked by design-kit agent. Prerequisite: review-kit completed. Supports all backend/frontend/DB tech stacks."
argument-hint: "module=<module-id> [ux-library=<library>] [ux-snapshot=<path>]"
---

# Design Kit Skill

Produces all design artifacts: diagrams, scaffolding, database design, UX stubs.

## When to Use
- After review-kit completes
- When creating architecture diagrams
- When scaffolding microservices or frontend apps
- When designing UX stubs from mockups or library selection

## Procedure

### Step 1 — Read Config & Cross-Cutting
- `aikit/config.yaml` → tech stack, paths
- `aikit/blueprint/cross-cutting.yaml` → shared components to reuse

### Step 2 — Architecture Diagrams
Invoke `@design-diagrams` (mode: architecture-overview).
Output: `architecture.md`, `diagrams/architecture.mmd`, `diagrams/components.mmd`

### Step 3 — Workflow Sequence Diagrams (Queued)
Queue: all WF-NNN from `workflows.md`. Batch: 2 per sub-agent.
Invoke `@design-diagrams` (mode: workflow-diagrams) per batch.
Output: `diagrams/seq-wf-NNN.mmd` per workflow.

### Step 4 — ER & Deployment Diagrams
Invoke `@design-diagrams` (mode: er-diagram) → `diagrams/er-diagram.mmd`
Invoke `@design-diagrams` (mode: deployment-diagram) → `diagrams/deployment.mmd`
Invoke `@design-diagrams` (mode: db-design) → `db-design.md`

### Step 5 — Backend Scaffolding (Queued by Service)
Queue: all microservices from component diagram. Batch: 1 per sub-agent.
Invoke `@design-scaffold` (mode: backend-scaffold) per service.
Output: `scaffold/<service-name>/`
Follow: [Microservice Scaffold Guide](./references/microservice-scaffold-guide.md)

### Step 6 — Frontend Scaffolding
Invoke `@design-scaffold` (mode: frontend-scaffold).
Follow: [Frontend Scaffold Guide](./references/frontend-scaffold-guide.md)
Output: `scaffold/frontend/`

### Step 7 — Database Scaffold
Invoke `@design-scaffold` (mode: db-scaffold).
Output: `scaffold/database/`

### Step 8 — UX Stubs (Queued by Page)
Queue: unique UI pages from stories. Batch: 1 per sub-agent.
Invoke `@design-ux` per page.
Follow: [UX Stub Guide](./references/ux-stub-guide.md)
Output: `ux-stubs/<page-name>/`

### Step 9 — Complete
Update cross-cutting.yaml, config.yaml, stage-tracker, audit.log.

## Reference Files
- [MMD Diagram Types](./references/mmd-diagram-types.md)
- [Microservice Scaffold Guide](./references/microservice-scaffold-guide.md)
- [Frontend Scaffold Guide](./references/frontend-scaffold-guide.md)
- [UX Stub Guide](./references/ux-stub-guide.md)
