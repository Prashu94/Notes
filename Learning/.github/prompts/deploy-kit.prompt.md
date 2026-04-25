---
description: "Runs the deploy-kit pipeline stage — generates Terraform IaC, Dockerfiles, Helm charts, and a deployment guide."
tools: [read, edit, search]
---

Run the deploy-kit pipeline for the specified module.

1. Read `aikit/config.yaml` and find the module matching the provided `module` argument.
2. Verify the test-kit stage is complete (`aikit/logs/stage-tracker.yaml`).
3. Invoke `@deploy-kit` with the resolved config path.
4. Follow all instructions in the deploy-kit agent to completion.
5. Report the paths of all generated Terraform modules, Dockerfiles, Helm charts, and the deployment guide when finished.
