---
description: "Runs the test-kit pipeline stage — generates unit and integration tests, runs them, and validates coverage targets."
tools: [read, edit, search]
---

Run the test-kit pipeline for the specified module.

1. Read `aikit/config.yaml` and find the module matching the provided `module` argument.
2. Verify the dev-kit stage is complete (`aikit/logs/stage-tracker.yaml`).
3. Invoke `@test-kit` with the resolved config path.
4. Follow all instructions in the test-kit agent to completion, including build gate validation and coverage reporting.
5. Report test results, coverage percentages, and the path to the coverage report when finished.
