---
description: "Runs the design-kit pipeline stage — generates architecture diagrams, service scaffolds, and UX stubs."
tools: [read, edit, search]
---

Run the design-kit pipeline for the specified module.

1. Read `aikit/config.yaml` and find the module matching the provided `module` argument.
2. Verify the review-kit stage is complete (`aikit/logs/stage-tracker.yaml`).
3. Invoke `@design-kit` with the resolved config path.
4. Follow all instructions in the design-kit agent to completion.
5. Report the paths of all generated diagrams, scaffolds, and UX stubs when finished.
