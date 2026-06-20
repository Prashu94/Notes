---
name: deploy-kit
description: "Deploy-kit skill: generates cloud-agnostic Terraform IaC, Dockerfiles, and Helm charts for Kubernetes deployment. Supports AWS, GCP, Azure. Reads aikit/config.yaml and blueprint.yaml for all inputs. Outputs to aikit/outputs/deploy/."
applyTo: ".github/agents/deploy-kit.agent.md"
---

# Deploy Kit Skill

## Purpose
Generate production-ready deployment artifacts: Terraform IaC, Dockerfiles, and Helm charts. Cloud provider is determined by `technology.cloud` in `config.yaml`. The kit never blocks on missing cloud credentials — all cloud-specific values are written as `TODO` placeholders.

## References
- [terraform-guide.md](references/terraform-guide.md) — Terraform module patterns, state management, variable conventions
- [helm-charts-guide.md](references/helm-charts-guide.md) — Helm best practices, values hierarchy, health probes

---

## Step-by-Step Procedure

### Step 1 — Bootstrap
1. Read `aikit/config.yaml` → extract `outputs.deploy`, `technology`, `blueprint.path`, `module.id`
2. Read `aikit/blueprint/modules/<module-id>.yaml` → extract `services[]`, `deployment`, `infrastructure`
3. Read `aikit/logs/stage-tracker.yaml` → verify `test` stage status == `complete`
4. If test stage not complete: **abort** and report which test stage is incomplete
5. Load `terraform-guide.md` and `helm-charts-guide.md` from skill references

### Step 2 — Terraform Infrastructure
For each resource group in blueprint `deployment.infrastructure`:
1. Invoke `@deploy-terraform` with mode `vpc-networking`
2. Invoke `@deploy-terraform` with mode `database` (if DB is cloud-managed)
3. Invoke `@deploy-terraform` with mode `cache` (if Redis/Memcached in blueprint)
4. Invoke `@deploy-terraform` with mode `message-broker` (if Kafka/Pub Sub in blueprint)
5. Invoke `@deploy-terraform` with mode `secrets-iam`

Output root: `aikit/outputs/deploy/terraform/`

### Step 3 — Dockerfiles
For each service in `services[]`:
1. Invoke `@deploy-terraform` with mode `dockerfile` and service technology
2. Check if `Dockerfile` already exists at service scaffold path (brownfield: skip if exists and unchanged)
3. Write `Dockerfile` + `.dockerignore` to service source directory

### Step 4 — Helm Charts (queued, 1 service per batch)
```
FOR each service in services[]:
  Invoke @deploy-helm with mode=service-chart, service=<service-name>
  Wait for completion
  Record output path in deployment manifest
END FOR
Invoke @deploy-helm with mode=global-config
```

Output root: `aikit/outputs/deploy/helm/`

### Step 5 — Global Kubernetes Config
1. Generate `helm/global/namespace.yaml`
2. Generate `helm/global/ingress-nginx.yaml` (if ingress enabled)
3. Generate cluster-level HPA defaults if specified in blueprint

### Step 6 — Deployment Guide
Generate `aikit/outputs/deploy/deployment-guide.md` with:
- Prerequisites checklist (tools: terraform, helm, kubectl, docker)
- Step-by-step apply order: Terraform → Docker build/push → Helm install
- Environment-specific commands (staging vs production)
- Secret injection instructions (never commit `.tfvars` with real values)
- Rollback procedure

### Step 7 — Completion
1. Update `aikit/logs/stage-tracker.yaml` → `deploy: complete`
2. Append to `aikit/logs/audit.log`:
   ```
   [TIMESTAMP] deploy-kit completed for module <module-id>
   Terraform modules: <count>
   Dockerfiles: <service-list>
   Helm charts: <service-list>
   ```

---

## Queue Mechanism
- **Terraform**: invoked once per resource group — typically 5–6 invocations total
- **Dockerfiles**: invoked once per service — no batching needed (small output)
- **Helm charts**: **1 service per invocation** — strictly sequential to avoid context overflow

## Brownfield Behavior
- If `Dockerfile` exists in service directory → compare with generated; only overwrite if `FORCE=true` in config
- If `helm/<service>/` exists → skip generation, log `[SKIPPED - existing chart]`
- Terraform: always regenerate (infrastructure drift is managed by Terraform state)

## Cloud-Agnostic Defaults
| Resource | AWS | GCP | Azure | Default placeholder |
|---|---|---|---|---|
| Container Registry | ECR | GCR | ACR | `# TODO: ECR/GCR/ACR URI` |
| Kubernetes | EKS | GKE | AKS | k8s cluster |
| Managed DB | RDS | Cloud SQL | Azure SQL | `# TODO: connection string` |
| Secrets | Secrets Manager | Secret Manager | Key Vault | `# TODO: secret ARN/path` |
| Load Balancer | ALB | Cloud Load Balancing | Azure LB | nginx-ingress (default) |
