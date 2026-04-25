---
description: "Runs the review-kit pipeline stage — clarifies requirements, selects tech stack, and generates Epics, Features, and User Stories."
tools: [read, edit, search]
---

Run the review-kit pipeline for the specified module.

1. Read `aikit/config.yaml` and find the module matching the provided `module` argument.
2. Verify the requirement-kit stage is complete (`aikit/logs/stage-tracker.yaml`).
3. Invoke `@review-kit` with the resolved config path.
4. Follow all instructions in the review-kit agent to completion, including the interactive clarification phase.
5. Report the paths of all generated artifacts when finished.
