# CopilotWorkspaces — Project Guidelines

## AIKit Pipeline
This workspace includes an AI-powered software delivery pipeline under `aikit/`. When working on any kit-related task, always read `aikit/config.yaml` first to understand module context, output paths, and stage statuses.

See [aikit/README.md](../aikit/README.md) for full usage guide.

## Conventions
- All generated artifacts go to paths defined in `config.yaml` — never hardcode paths.
- Always append to `aikit/logs/audit.log` when completing a kit stage.
- Always update `aikit/logs/stage-tracker.yaml` when changing stage status.
- Cross-module shared components must be registered in `aikit/blueprint/cross-cutting.yaml`.
