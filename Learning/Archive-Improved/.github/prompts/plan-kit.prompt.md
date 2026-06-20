---
description: "Runs the plan-kit pipeline stage — generates blueprint.yaml, ADRs, DB schema, and OpenAPI contracts."
tools: [read, edit, search]
---

Run the plan-kit pipeline for the specified module.

1. Read `aikit/config.yaml` and find the module matching the provided `module` argument.
2. Verify the design-kit stage is complete (`aikit/logs/stage-tracker.yaml`).
3. Invoke `@plan-kit` with the resolved config path.
4. Follow all instructions in the plan-kit agent to completion.
5. Report the paths of all generated blueprint, ADRs, schema, and API contract files when finished.
