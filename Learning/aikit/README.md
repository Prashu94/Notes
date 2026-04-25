# AIKit — AI-Powered Software Delivery Pipeline

AIKit is a GitHub Copilot agent orchestration framework that guides your product from raw requirements through review, design, planning, development, testing, and deployment. Each "kit" is a specialized Copilot agent backed by dedicated skills and sub-agents.

---

## Architecture Overview

```
aikit/
├── config.yaml              ← Master config per module (EDIT THIS FIRST)
├── inputs/requirements/     ← Drop .docx / .xlsx / .csv requirements files here
├── outputs/                 ← All generated artifacts land here (per kit)
├── blueprint/               ← Accumulated cross-module blueprint (auto-managed)
└── logs/                    ← Audit logs & stage tracker (auto-managed)

.github/
├── agents/                  ← 7 kit agents + sub-agents
├── skills/                  ← 7 skill folders (SKILL.md + references)
├── prompts/                 ← /slash-command entry points for each kit
└── instructions/            ← Always-on aikit conventions
```

---

## Kits & Responsibilities

| Kit | Command | Input | Output |
|-----|---------|-------|--------|
| **requirement-kit** | `/requirement-kit` | `.docx / .xlsx / .csv` | `requirements.md`, `BRD.md`, business rules, workflows |
| **review-kit** | `/review-kit` | Requirement artifacts | `epics.md`, `features.md`, `stories.md`, `tech-stack.md` |
| **design-kit** | `/design-kit` | Review artifacts | MMD diagrams, service scaffolds, UX stubs |
| **plan-kit** | `/plan-kit` | Design artifacts | `blueprint.yaml`, `tech-decisions.yaml`, `db-schema.yaml` |
| **dev-kit** | `/dev-kit` | Plan blueprints | Full source code, build report |
| **test-kit** | `/test-kit` | Dev code + stories | Test cases, build gate report, coverage |
| **deploy-kit** | `/deploy-kit` | Dev + plan artifacts | Terraform, Helm charts, deployment guide |

---

## Quick Start

### 1. Copy and configure

```bash
cp aikit/config.yaml.template aikit/config.yaml
```

Edit `aikit/config.yaml` — set `module.id`, `module.name`, `module.type`, and tech stack fields.

### 2. Drop requirements

Place your `.docx`, `.xlsx`, or `.csv` files into `aikit/inputs/requirements/`.

### 3. Run the pipeline sequentially

```
@requirement-kit  Process requirements for module: <module-id>
@review-kit       Review and create stories for module: <module-id>
@design-kit       Create design artifacts for module: <module-id>
@plan-kit         Build blueprint for module: <module-id>
@dev-kit          Generate code for module: <module-id>
@test-kit         Run test generation and gate for module: <module-id>
@deploy-kit       Generate deployment artifacts for module: <module-id>
```

Or use the slash prompts:

```
/requirement-kit  module=<module-id> path=aikit/inputs/requirements/
/review-kit       module=<module-id>
/design-kit       module=<module-id>
/plan-kit         module=<module-id>
/dev-kit          module=<module-id>
/test-kit         module=<module-id>
/deploy-kit       module=<module-id>
```

---

## Greenfield vs Brownfield

**Greenfield** — set `module.type: greenfield`. The pipeline starts fresh.

**Brownfield** — set `module.type: brownfield` and provide `inputs.existing_codebase`. The plan-kit will scan the existing code and the blueprint's `cross-cutting.yaml` to identify reusable components, avoid duplication, and ensure new stories integrate cleanly.

### Adding a new story or requirement to an existing module

1. Add the new requirement file(s) to `aikit/inputs/requirements/`
2. Run `@requirement-kit` — it will append to existing artifacts (incremental mode)
3. Run `@review-kit` — it will add new stories without touching existing ones
4. Continue the pipeline from that stage onward

---

## Cross-Module Blueprint

The `aikit/blueprint/` directory accumulates facts across all modules:

```
blueprint/
├── module-registry.yaml       ← All modules and their status
├── cross-cutting.yaml         ← Shared APIs, models, components
└── modules/
    ├── <module-id>.yaml       ← Per-module blueprint snapshot
    └── ...
```

When developing a new module, the plan-kit reads `cross-cutting.yaml` so the dev-kit can reuse shared components correctly.

---

## Audit Trail

Every kit writes to:

- `aikit/logs/audit.log` — timestamped action log
- `aikit/logs/stage-tracker.yaml` — stage status (not-started / in-progress / completed / failed)

---

## Stage Prerequisite Gates

Each kit checks the `stages` block in `config.yaml` before running. If a prerequisite stage is not `completed`, it will warn you rather than proceeding on incomplete data.

| Kit | Prerequisite stage |
|-----|--------------------|
| review-kit | requirement_kit = completed |
| design-kit | review_kit = completed |
| plan-kit | design_kit = completed |
| dev-kit | plan_kit = completed |
| test-kit | dev_kit = completed |
| deploy-kit | plan_kit = completed |

---

## File Naming Convention

Generated agent files follow a consistent naming scheme so sub-agents can reference each other:

- Main agents: `<kit-name>.agent.md`
- Sub-agents: `<kit>-<role>.agent.md` (e.g., `req-parser.agent.md`)
- Skills: `.github/skills/<kit-name>/SKILL.md`
- Prompts: `.github/prompts/<kit-name>.prompt.md`
