# Cross-Module Guide

## Purpose

The `aikit/blueprint/` directory serves as a **shared memory** across all modules processed through aikit. It prevents duplicated implementations and ensures integration correctness.

## When Cross-Cutting Applies

### Detecting Shared Components

During plan-kit, scan the new module's blueprint for:

1. **Shared Data Models**: An entity that appears in multiple modules
   - Signal: same entity name (User, Product, Organization) in multiple services
   - Action: Add to `cross-cutting.yaml`.`shared_data_models`

2. **Shared APIs**: An API one service provides that other services consume
   - Signal: `service.dependencies` reference a service from another module
   - Action: Add to `cross-cutting.yaml`.`shared_apis`

3. **Shared Frontend Components**: MFE components exported to shell
   - Signal: `frontend.mfe_config.exposes` entries
   - Action: Add to `cross-cutting.yaml`.`shared_components`

4. **Infrastructure Decisions**: Broker, cache, monitoring choices affect all modules
   - Signal: New infrastructure added (Kafka, Redis, etc.)
   - Action: Add to `cross-cutting.yaml`.`infrastructure_decisions`

## Module Snapshot Format

Each module gets a snapshot at `aikit/blueprint/modules/<module-id>.yaml`:

```yaml
module_id: order-service
name: "Order Service"
version: "1.0.0"
blueprint_generated: "2026-04-25T10:00:00Z"

# Summary of what this module provides
provides:
  apis:
    - base_path: /api/v1/orders
      service: order-service
  events:
    - OrderCreated
    - OrderCancelled
  data_models:
    - name: Order
      db_table: orders
  frontend_routes:
    - /orders
    - /orders/new

# What this module consumes from other modules
consumes:
  apis:
    - from: auth-service
      path: /api/v1/auth
  data_models:
    - from: user-service
      model: User
```

## Brownfield Analysis Procedure

When `module.type = brownfield`:

1. **Read all existing snapshots** in `aikit/blueprint/modules/`
2. **Build dependency graph** — which modules depend on which
3. **Identify conflicts**:
   - Does the new module change an API already consumed by another module?
   - Does it add a new column to a shared table?
   - Does it introduce a conflicting infrastructure choice?
4. **Report conflicts to user** before proceeding
5. **List reuse opportunities** — shared components the new module can use

## Incremental Update Procedure

When adding a new story to an existing module:
1. Read the existing `modules/<id>.yaml`
2. Check if new story adds new API endpoints → update `provides.apis`
3. Check if new story uses new cross-cutting component → update `consumes`
4. Re-run cross-cutting conflict check

## Registry Format

```yaml
# module-registry.yaml
modules:
  - id: auth-service
    name: "Auth Service"
    type: greenfield
    version: "1.0.0"
    config: aikit/config.yaml
    snapshot: aikit/blueprint/modules/auth-service.yaml
    pipeline_status:
      requirement_kit: completed
      review_kit: completed
      design_kit: completed
      plan_kit: completed
      dev_kit: completed
      test_kit: completed
      deploy_kit: completed
    last_updated: "2026-04-25T10:00:00Z"
```
