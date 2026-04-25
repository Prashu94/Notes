---
description: "Runs the requirement-kit pipeline stage — parses input documents and generates a BRD with business rules and workflows."
tools: [read, edit, search]
---

Run the requirement-kit pipeline for the specified module.

1. Read `aikit/config.yaml` and find the module matching the provided `module` argument.
2. Invoke `@requirement-kit` with the resolved config path.
3. Follow all instructions in the requirement-kit agent to completion.
4. Report the paths of all generated artifacts when finished.
