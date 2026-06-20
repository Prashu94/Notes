---
description: "Runs the dev-kit pipeline stage — generates backend code, frontend code, and validates the local build."
tools: [read, edit, search]
---

Run the dev-kit pipeline for the specified module.

1. Read `aikit/config.yaml` and find the module matching the provided `module` argument.
2. Verify the plan-kit stage is complete (`aikit/logs/stage-tracker.yaml`).
3. Invoke `@dev-kit` with the resolved config path.
4. Follow all instructions in the dev-kit agent to completion, including local build validation.
5. Report the paths of all generated source files and build results when finished.
