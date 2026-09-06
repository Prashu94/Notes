# Terraform — 55 Senior Interview Questions

**Bar:** State, providers, modules, Azure, blast radius. You will be asked even as an app engineer.

---

### 1. What Terraform is vs Helm vs ARM/Bicep.

**Short answer:** Terraform declares cloud platform resources—networks, AKS, SQL, IAM—while Helm renders Kubernetes manifests inside a cluster. ARM/Bicep is Azure-native IaC. Platform TF plus GitOps/Helm for apps avoids dual ownership of the same Deployment.

#### What it is
Terraform is multi-cloud IaC with HCL and provider plugins. Helm packages Kubernetes objects. Bicep compiles to ARM for Azure RM deployments. Java-on-AKS shops typically split: platform TF repo, app Helm/Argo repos.

#### How it works (internals)
TF builds a dependency graph, refreshes state, plans diffs, applies via providers. Helm renders templates and calls the Kubernetes API. State tracks cloud IDs; Helm tracks release revisions in cluster secrets.

#### When to use / when NOT to use
Use TF for shared platform foundations. Use Helm/GitOps for microservice deploy cadence. Do not manage the same Deployment in TF kubernetes provider and Helm.

#### Production example
TF provisions RG, VNET, AKS, SQL; Helm/Argo deploys `order-service` by digest. Portal hotfix to Deployment is reverted by GitOps—not TF.

#### Common mistakes
- Dual-managing Deployments in TF and Argo
- Helm for Azure SQL
- No RACI between platform and app

#### Interview follow-ups (with model answers)

**Q:** Why not Kubernetes Deployments in TF?
**A:** GitOps gives PR rollbacks and per-service drift detection. TF suits slow platform resources. App teams ship daily—Helm/Argo matches that. TF cluster credentials in app pipelines widen blast radius.

**Q:** Bicep vs TF on Azure-only?
**A:** Bicep fits Azure-only mandates and deployment stacks. TF wins multi-cloud and mature module ecosystem. Pick based on enterprise architecture, not religion.

**Q:** Bad responsibility split?
**A:** App TF for namespace resources while platform module recreates NSG rules—perpetual churn. Fix with RACI, separate state, versioned module outputs.

#### Scenario probe

Platform creates `kubernetes_deployment` in TF while Argo CD manages the same namespace—OutOfSync every five minutes.

Remove app Deployments from TF scope. TF outputs cluster and ACR; apps promote digests via GitOps PR. One-time bootstrap only with handoff to Argo—never dual controllers.

#### Code / config (when useful)
```hcl
module "aks" { source = "./modules/aks" }
# Apps: Helm/Argo — not kubernetes_deployment
```

---

### 2. Desired state and graph.

**Short answer:** HCL becomes a DAG; plan computes create/update/destroy to match desired config. Implicit deps from references; explicit `depends_on` only when hidden ordering is required.

#### What it is
Desired-state IaC reconciles reality to config. Graph orders operations—subnet before private endpoint.

#### How it works (internals)
Plan walks graph, Read APIs, diffs attributes. Apply parallelizes safe steps. `terraform graph` exports DOT. `-target` breaks safety—emergency only.

#### When to use / when NOT to use
Review graph for blast radius. Avoid serializing everything with `depends_on`. Never `-target` in routine CI.

#### Production example
Private endpoint references subnet ID—plan orders correctly. Cyclic module refs fail with Cycle error.

#### Common mistakes
- Overusing depends_on
- Ignoring `-/+` replace
- Apply without reading destroy count

#### Interview follow-ups (with model answers)

**Q:** Difference between `~` and `-/+`?
**A:** Tilde is in-place update. Min/plus is replace—new ID, downtime risk. Azure ForceNew on SKU/location. Treat `-/+` as data-loss review.

**Q:** When is depends_on justified?
**A:** Hidden ordering—IAM propagation, null_resource triggers. Document why; prefer attribute refs.

**Q:** Slow plan debug?
**A:** Split stacks, upgrade batching providers, avoid `-refresh=false` unless trusted, check API throttling.

#### Scenario probe

Tag change on parent RG triggers 47 resource updates in plan.

Confirm tag-only in-place vs ForceNew for AKS. Consider Azure Policy for tags instead of TF-wide churn. Use `ignore_changes` only with governance elsewhere.

---

### 3. State: what it is and why it's sacred.

**Short answer:** Terraform state is the authoritative mapping between your HCL addresses and real cloud resource IDs, plus cached attributes providers need for planning. Without it, Terraform cannot know whether to create, update, or destroy—it may try to recreate everything or delete resources it thinks are unmanaged. Treat state like production data: encrypt at rest, version backups, restrict RBAC, and never commit it to Git. State corruption or loss is a platform incident, not a developer inconvenience.

#### What it is
State is a JSON document (local or remote) recording `resource_type.name` keys tied to Azure resource IDs, dependencies, and metadata. It is not a source of truth for desired configuration—that is your `.tf` files—but it is the memory Terraform needs to reconcile reality. Remote backends (Azure Blob, Terraform Cloud) centralize state so teams collaborate without passing files around.

#### How it works (internals)
On `plan`/`apply`, Terraform loads state, refreshes live attributes from provider APIs, compares desired config from HCL, and computes a graph of changes. Writes are atomic per operation; concurrent applies require locking. Sensitive values may be marked in state; providers store enough attrs to diff without re-reading everything each time.

#### When to use / when NOT to use
Always use remote state for shared platform stacks (network, AKS, data). Local state is acceptable only for personal sandboxes. Split state by blast radius—never one monolithic state for an entire subscription. Import brownfield resources into state before managing them declaratively.

#### Production example
Platform team stores state in `stplatformtfstate` with versioning enabled. A mistaken `terraform state rm` on a SQL server was recovered from blob version history within minutes; without versioning, Friday's apply would have planned destroy/recreate on a 2 TB database.

#### Common mistakes
- Committing `terraform.tfstate` to Git
- Sharing one state file across unrelated teams
- Applying without reviewing plan destroys
- Skipping backup/versioning on the state container

#### Interview follow-ups (with model answers)

**Q:** What happens if state is lost entirely?
**A:** Terraform loses all ID bindings and typically plans to create duplicates of existing resources—or destroy orphans if config was removed. Recovery path: restore state from Blob versioning, backup vault, or Terraform Cloud history. If no backup, painful import of every live resource by ARM ID. Prevention: enable soft delete and versioning on the storage account, restrict delete permissions, and run quarterly restore drills. Never 'start fresh' on production without executive sign-off.

**Q:** How do you split state for blast radius?
**A:** Separate backends per domain and environment: `network/prod.tfstate`, `aks/prod.tfstate`, `data/prod.tfstate`. Use `terraform_remote_state` data sources to pass outputs (subnet IDs, AKS OIDC issuer) without merging state files. One apply cannot delete the entire platform. Document ownership per stack in the platform runbook.

**Q:** Can two people apply the same stack safely?
**A:** Only with remote state locking—Azure Blob lease or Terraform Cloud lock. Second apply blocks until the first completes or lock is force-unlocked after verifying no active job. CI should be the only prod applier; laptops plan only. Stale locks after crashed agents need documented force-unlock procedure with audit trail.

#### Scenario probe

**Situation:** On-call reports Terraform wants to destroy 40 resources after someone copied `terraform.tfstate` from dev to prod backend.

**Model answer:** Stop all applies immediately. Restore prod state from Blob version history to the pre-copy timestamp—never apply from dev state against prod resources. Run `terraform state list` and compare to Azure Resource Graph. Expect drift; import or refresh before any apply. Post-incident: RBAC so only CI service principal can write state, enable versioning alerts, and train that state is not portable between environments.

---

### 4. Remote state backend (Azure).

**Short answer:** Remote state on Azure Blob is the production standard: durable storage, native lease locking, versioning for rollback, and integration with Azure RBAC and private endpoints. Configure encryption, soft delete, and deny public access on the storage account holding state. CI authenticates via OIDC federated credentials—never store storage account keys in pipeline variables. The backend block is part of bootstrap; protect it like root CA material.

#### What it is
The `backend "azurerm"` block stores state in a blob (`key = "prod/network.tfstate"`) inside a dedicated storage account, often in a separate management subscription. Locking uses blob leases during apply. Terraform Cloud and Spacelift are alternatives but many Azure enterprises stay DIY with Blob plus GitHub Actions.

#### How it works (internals)
At `terraform init`, Terraform configures the backend and may migrate local state to remote. Each workspace/stack uses a unique `key` path. Lease acquisition prevents concurrent writes; `-lock=false` is break-glass only. Versioning lets you restore `terraform.tfstate` to a prior blob version after corruption.

#### When to use / when NOT to use
Use remote backend for any stack touched by more than one person or CI job. Use separate storage accounts or containers per sensitivity tier if compliance requires. Do not use local state for QA shared environments—drift and overwrite accidents are guaranteed.

#### Production example
Bootstrap stack creates `rg-tfstate-prod` and storage account with private endpoint only; all platform pipelines use `backend.tf` with OIDC `azurerm` provider auth. Keys were never generated—only RBAC role `Storage Blob Data Contributor` on the container for the CI SP.

#### Common mistakes
- Storage account keys in `ARM_ACCESS_KEY`
- Public network access on state storage
- Same blob key for dev and prod
- No versioning—unrecoverable state deletes

#### Interview follow-ups (with model answers)

**Q:** How bootstrap the backend without chicken-and-egg?
**A:** First apply uses local state or a minimal bootstrap stack with local/CI temporary backend to create RG + storage. Then `terraform init -migrate-state` moves state into the new backend. Document one-time bootstrap in runbook; some teams keep bootstrap stack read-only forever.

**Q:** OIDC vs storage account key for CI?
**A:** OIDC: GitHub/Azure DevOps federated credential to Entra app, role assignment on state container—no rotating secrets. Keys: simpler but leak risk and manual rotation. Production should be OIDC with least privilege; keys only for break-glass automation with vault storage.

**Q:** What if Blob is unavailable during apply?
**A:** Apply may fail mid-graph leaving partial resources and state partially updated. Halt further applies; restore connectivity; re-run plan from same commit. If state write failed, verify blob version—never apply from divergent local copy. Monitor storage availability like any tier-0 dependency.

#### Scenario probe

**Situation:** Friday prod apply fails with `Error acquiring state lock` but no pipeline is running.

**Model answer:** Check Azure Portal blob lease on the state object—stale lease from crashed agent. Confirm no active `terraform apply` via CI logs. If truly stale, `terraform force-unlock <id>` with ticket and second approver. Re-run plan from saved artifact—never unlock while another apply might be running. Add lock timeout alerts and CI job heartbeat.

---

### 5. State lock.

**Short answer:** State locking prevents two applies from writing state concurrently, which corrupts JSON and can orphan or duplicate cloud resources. Azure Blob backend uses lease locks; Terraform Cloud uses managed locks. If apply crashes, a stale lock blocks the next run—`terraform force-unlock` is break-glass after proving no active apply. Never disable locking in shared environments.

#### What it is
Locking is a backend feature, not optional safety on team stacks. When `apply` starts, Terraform acquires a lease on the state blob; other operations wait or fail fast with lock ID. Force-unlock removes the lock metadata without touching cloud resources.

#### How it works (internals)
Lock duration ties to apply length—long AKS applies hold locks for 30+ minutes. CI should use `-lock-timeout` for graceful wait. `plan` also locks briefly on some backends. DynamoDB (AWS) and Blob leases differ but semantics are the same: one writer at a time.

#### When to use / when NOT to use
Always enable locking with remote state. Disable only for read-only `plan` in automation if backend supports plan without lock (prefer lock). Force-unlock requires platform admin role and incident ticket.

#### Production example
Saturday morning lock after CI agent OOM during AKS node pool upgrade. On-call verified no running job in GitHub Actions, checked blob lease in portal, force-unlocked with manager approval, resumed apply from saved plan file—no state corruption.

#### Common mistakes
- Force-unlock while another apply runs
- Ignoring lock errors and applying locally
- No lock-timeout causing flaky CI
- Shared `-lock=false` in pipeline 'to go faster'

#### Interview follow-ups (with model answers)

**Q:** How verify it's safe to force-unlock?
**A:** Check CI/CD for in-progress jobs, Azure Activity Log for ongoing resource operations from the SP, and blob lease holder metadata. Ping last operator. Document lock ID in ticket. If any doubt, wait or escalate—corrupted state is worse than delay.

**Q:** Does `plan` need locking?
**A:** On azurerm backend, plan acquires a short lock during refresh/write of state metadata. Concurrent plans can queue. For high churn, some teams use `-refresh=false` on plan-only jobs with scheduled full refresh—trade accuracy for speed, document risk.

**Q:** What corrupt state looks like?
**A:** JSON parse errors, duplicate resource addresses, missing dependencies. Recovery: restore versioned blob, or `terraform state pull/push` from known good backup. Never hand-edit state without `terraform state` subcommands unless expert.

#### Scenario probe

**Situation:** Two engineers run `terraform apply` simultaneously on the same stack from laptops during a drill.

**Model answer:** Second should fail with lock error—if both used `-lock=false`, state may be corrupt. Stop immediately; compare `terraform state list` outputs; restore from versioning; run plan. Policy: only CI applies prod; laptops are plan-only. Drill lesson: enforce branch protection on apply workflows.

---

### 6. `terraform plan` is not a promise.

**Short answer:** `terraform plan` shows intent at a point in time—not a guarantee apply will succeed or match if the cloud changes mid-pipeline. API errors, quota limits, policy denies, and concurrent portal edits cause plan/apply skew. Save plans with `terraform plan -out=tfplan` and apply that exact file in CI so prod applies what reviewers approved. Re-plan if significant time passes or another team deployed.

#### What it is
Plan is a dry-run diff: refresh state, evaluate graph, show create/update/destroy. Exit codes: 0 no changes, 1 error, 2 changes (with -detailed-exitcode). Plan files are binary bundles of config + state snapshot—not portable across machines without same provider versions.

#### How it works (internals)
Providers call Read during plan; some changes only appear at apply (e.g., eventual consistency). `-refresh-only` updates state without changes. Plan does not run apply-time provisioners reliably for preview.

#### When to use / when NOT to use
Attach plan text to every PR. Apply saved plan in prod within SLA (same day). Re-plan after approval if wait > few hours or incident window.

#### Production example
Approved plan showed 2 updates; apply failed on SQL firewall—Azure Policy had added deny since plan. Fix: policy exception or update config; re-plan mandatory.

#### Common mistakes
- Applying days-old plan
- Plan without -detailed-exitcode in CI
- Trusting plan when refresh skipped

#### Interview follow-ups (with model answers)

**Q:** Why apply saved plan?
**A:** Binds apply to reviewed artifact—prevents surprise drift between approval and execution. Same provider versions and vars required.

**Q:** Plan vs speculative plan on PR?
**A:** PR plan may use read-only creds; ensure same backend and vars as apply job or label as approximate.

**Q:** Partial apply after plan?
**A:** State updated per resource; re-plan before retry—never assume original plan still valid.

#### Scenario probe

**Situation:** Plan approved at 9 AM; apply at 4 PM fails with new resources conflicting.

**Model answer:** Re-run plan from same SHA; diff against morning artifact; identify portal or parallel deploy drift. Apply only new plan with re-approval if destroys appear. Add policy denying manual creates in managed RGs.

---

### 7. Drift.

**Short answer:** Drift is when live infrastructure differs from Terraform state and code—portal hotfixes, failed applies, or external automation. `terraform plan` surfaces drift as unexpected updates or destroys. Scheduled plan jobs with exit code 2 alert Slack before drift becomes outage. Decide per resource: adopt in code, import, or revert portal change—not silent ignore.

#### What it is
Refresh compares state to APIs; drift appears as `~` updates or `-/+` replacements. Some attrs are write-only or computed—noisy drift possible. `ignore_changes` suppresses specific attrs when Policy owns tags.

#### How it works (internals)
Drift detection cron: `terraform plan -detailed-exitcode` nightly. Azure Policy can complement for deny/audit. GitOps drift is separate problem for in-cluster resources.

#### When to use / when NOT to use
Run drift detection on all prod stacks. Use `ignore_changes` sparingly with documented owner. Do not `-refresh=false` on prod apply.

#### Production example
Nightly plan flagged NSG rule added manually for 'quick debug'—apply would remove it; ticket filed, rule removed after proper TF change.

#### Common mistakes
- Ignoring drift alerts
- refresh=false as default
- Manual portal as permanent fix

#### Interview follow-ups (with model answers)

**Q:** Drift vs config change?
**A:** Drift: live changed without TF. Config change: .tf edited—plan expected.

**Q:** Who fixes drift?
**A:** Platform owns infra RGs; app teams own their resources per RACI.

**Q:** Terraform vs Argo drift?
**A:** TF for Azure RM; Argo for cluster—use right detector per layer.

#### Scenario probe

**Situation:** Plan wants to destroy load balancer listener ops added during incident.

**Model answer:** Confirm if listener still needed; if yes, codify in TF and import if missing from state; if temporary, coordinate removal. Never apply destroy without understanding incident context.

---

### 8. Import.

**Short answer:** Bind existing cloud resources into state. import blocks (1.5+) codify imports; CLI one-off for emergencies. Pin provider and module versions in CI. Review every plan for unexpected destroys before production apply.

#### What it is
Import is a core Terraform concern for Azure platform teams supporting Java microservices on AKS. Interviewers want operational judgment: how this topic affects state safety, plan review, blast radius, and handoff to GitOps—not HCL trivia. You should connect infra changes to application deploy paths, on-call pain, and compliance gates.

#### How it works (internals)
For Import, Terraform builds a dependency DAG from HCL references, refreshes state via Azure RM provider APIs, and computes create/update/destroy. Provider schemas mark immutable attributes as ForceNew—plan symbols `-/+` mean replace, not in-place tweak. CI runs fmt, validate, tflint, Checkov, and emits a saved plan; prod apply uses OIDC with least-privilege RBAC on target resource groups and state storage.

#### When to use / when NOT to use
Apply Import patterns when platform ownership requires declarative, reviewable infrastructure. Avoid Terraform for fast-moving app Deployments better owned by Argo CD. Push back on permanent portal hotfixes—import or codify within SLA. Use separate state stacks so a mistake here cannot delete unrelated production data.

#### Production example
Platform squad changed import via PR #4821: plan artifact attached, Checkov passed, QA apply from main, prod apply next day with SoD approver using the same `tfplan` and commit SHA. Java teams consumed outputs through `terraform_remote_state`—no duplicate subnets or ACR instances. Rollback was `git revert` plus plan review, not portal edits.

#### Common mistakes
- Applying without plan review
- Unpinned modules/providers
- Shared state across unrelated teams
- Ignoring `-/+` in plan

#### Interview follow-ups (with model answers)

**Q:** What would a bad plan look like?
**A:** Unexpected `-/+` replaces, destroys on databases, or creates duplicates—always attach plan to PR.

**Q:** How split blast radius?
**A:** Separate state per domain and environment; remote outputs between stacks.

**Q:** Common Azure gotcha?
**A:** Many SKU and name changes ForceNew—read plan symbols carefully.

#### Scenario probe

**Situation:** Platform apply related to Import fails mid-run with partial resources created.

**Model answer:** Bind existing cloud resources into state. import blocks (1.5+) codify imports; CLI one-off for emergencies. Stop applies, verify state lock, compare Activity Log to `terraform state list`, restore state version if needed, import orphans, re-plan from approved SHA—never blind re-apply.

---

### 9. `terraform state mv` / `rm`.

**Short answer:** mv renames addresses without cloud change. rm removes from state only—orphans live resources. Pin provider and module versions in CI. Review every plan for unexpected destroys before production apply.

#### What it is
`terraform state mv` / `rm` is a core Terraform concern for Azure platform teams supporting Java microservices on AKS. Interviewers want operational judgment: how this topic affects state safety, plan review, blast radius, and handoff to GitOps—not HCL trivia. You should connect infra changes to application deploy paths, on-call pain, and compliance gates.

#### How it works (internals)
For `terraform state mv` / `rm`, Terraform builds a dependency DAG from HCL references, refreshes state via Azure RM provider APIs, and computes create/update/destroy. Provider schemas mark immutable attributes as ForceNew—plan symbols `-/+` mean replace, not in-place tweak. CI runs fmt, validate, tflint, Checkov, and emits a saved plan; prod apply uses OIDC with least-privilege RBAC on target resource groups and state storage.

#### When to use / when NOT to use
Apply `terraform state mv` / `rm` patterns when platform ownership requires declarative, reviewable infrastructure. Avoid Terraform for fast-moving app Deployments better owned by Argo CD. Push back on permanent portal hotfixes—import or codify within SLA. Use separate state stacks so a mistake here cannot delete unrelated production data.

#### Production example
Platform squad changed `terraform state mv` / `rm` via PR #4821: plan artifact attached, Checkov passed, QA apply from main, prod apply next day with SoD approver using the same `tfplan` and commit SHA. Java teams consumed outputs through `terraform_remote_state`—no duplicate subnets or ACR instances. Rollback was `git revert` plus plan review, not portal edits.

#### Common mistakes
- Applying without plan review
- Unpinned modules/providers
- Shared state across unrelated teams
- Ignoring `-/+` in plan

#### Interview follow-ups (with model answers)

**Q:** What would a bad plan look like?
**A:** Unexpected `-/+` replaces, destroys on databases, or creates duplicates—always attach plan to PR.

**Q:** How split blast radius?
**A:** Separate state per domain and environment; remote outputs between stacks.

**Q:** Common Azure gotcha?
**A:** Many SKU and name changes ForceNew—read plan symbols carefully.

#### Scenario probe

**Situation:** Platform apply related to `terraform state mv` / `rm` fails mid-run with partial resources created.

**Model answer:** mv renames addresses without cloud change. rm removes from state only—orphans live resources. Stop applies, verify state lock, compare Activity Log to `terraform state list`, restore state version if needed, import orphans, re-plan from approved SHA—never blind re-apply.

---

### 10. Workspaces vs directories.

**Short answer:** Workspaces share code, separate state keys—OK for small envs. Directory-per-env scales teams and RBAC better. Pin provider and module versions in CI. Review every plan for unexpected destroys before production apply.

#### What it is
Workspaces vs directories is a core Terraform concern for Azure platform teams supporting Java microservices on AKS. Interviewers want operational judgment: how this topic affects state safety, plan review, blast radius, and handoff to GitOps—not HCL trivia. You should connect infra changes to application deploy paths, on-call pain, and compliance gates.

#### How it works (internals)
For Workspaces vs directories, Terraform builds a dependency DAG from HCL references, refreshes state via Azure RM provider APIs, and computes create/update/destroy. Provider schemas mark immutable attributes as ForceNew—plan symbols `-/+` mean replace, not in-place tweak. CI runs fmt, validate, tflint, Checkov, and emits a saved plan; prod apply uses OIDC with least-privilege RBAC on target resource groups and state storage.

#### When to use / when NOT to use
Apply Workspaces vs directories patterns when platform ownership requires declarative, reviewable infrastructure. Avoid Terraform for fast-moving app Deployments better owned by Argo CD. Push back on permanent portal hotfixes—import or codify within SLA. Use separate state stacks so a mistake here cannot delete unrelated production data.

#### Production example
Platform squad changed workspaces vs directories via PR #4821: plan artifact attached, Checkov passed, QA apply from main, prod apply next day with SoD approver using the same `tfplan` and commit SHA. Java teams consumed outputs through `terraform_remote_state`—no duplicate subnets or ACR instances. Rollback was `git revert` plus plan review, not portal edits.

#### Common mistakes
- Applying without plan review
- Unpinned modules/providers
- Shared state across unrelated teams
- Ignoring `-/+` in plan

#### Interview follow-ups (with model answers)

**Q:** What would a bad plan look like?
**A:** Unexpected `-/+` replaces, destroys on databases, or creates duplicates—always attach plan to PR.

**Q:** How split blast radius?
**A:** Separate state per domain and environment; remote outputs between stacks.

**Q:** Common Azure gotcha?
**A:** Many SKU and name changes ForceNew—read plan symbols carefully.

#### Scenario probe

**Situation:** Platform apply related to Workspaces vs directories fails mid-run with partial resources created.

**Model answer:** Workspaces share code, separate state keys—OK for small envs. Directory-per-env scales teams and RBAC better. Stop applies, verify state lock, compare Activity Log to `terraform state list`, restore state version if needed, import orphans, re-plan from approved SHA—never blind re-apply.

---

### 11. Modules.

**Short answer:** Reusable parameterized bundles. Source from registry or Git with version pins. Pin provider and module versions in CI. Review every plan for unexpected destroys before production apply.

#### What it is
Modules is a core Terraform concern for Azure platform teams supporting Java microservices on AKS. Interviewers want operational judgment: how this topic affects state safety, plan review, blast radius, and handoff to GitOps—not HCL trivia. You should connect infra changes to application deploy paths, on-call pain, and compliance gates.

#### How it works (internals)
For Modules, Terraform builds a dependency DAG from HCL references, refreshes state via Azure RM provider APIs, and computes create/update/destroy. Provider schemas mark immutable attributes as ForceNew—plan symbols `-/+` mean replace, not in-place tweak. CI runs fmt, validate, tflint, Checkov, and emits a saved plan; prod apply uses OIDC with least-privilege RBAC on target resource groups and state storage.

#### When to use / when NOT to use
Apply Modules patterns when platform ownership requires declarative, reviewable infrastructure. Avoid Terraform for fast-moving app Deployments better owned by Argo CD. Push back on permanent portal hotfixes—import or codify within SLA. Use separate state stacks so a mistake here cannot delete unrelated production data.

#### Production example
Platform squad changed modules via PR #4821: plan artifact attached, Checkov passed, QA apply from main, prod apply next day with SoD approver using the same `tfplan` and commit SHA. Java teams consumed outputs through `terraform_remote_state`—no duplicate subnets or ACR instances. Rollback was `git revert` plus plan review, not portal edits.

#### Common mistakes
- Applying without plan review
- Unpinned modules/providers
- Shared state across unrelated teams
- Ignoring `-/+` in plan

#### Interview follow-ups (with model answers)

**Q:** What would a bad plan look like?
**A:** Unexpected `-/+` replaces, destroys on databases, or creates duplicates—always attach plan to PR.

**Q:** How split blast radius?
**A:** Separate state per domain and environment; remote outputs between stacks.

**Q:** Common Azure gotcha?
**A:** Many SKU and name changes ForceNew—read plan symbols carefully.

#### Scenario probe

**Situation:** Platform apply related to Modules fails mid-run with partial resources created.

**Model answer:** Reusable parameterized bundles. Source from registry or Git with version pins. Stop applies, verify state lock, compare Activity Log to `terraform state list`, restore state version if needed, import orphans, re-plan from approved SHA—never blind re-apply.

---

### 12. Module versioning.

**Short answer:** Pin `?ref=v1.2.3` on Git modules. Semver tags; never `@main` in prod. Pin provider and module versions in CI. Review every plan for unexpected destroys before production apply.

#### What it is
Module versioning is a core Terraform concern for Azure platform teams supporting Java microservices on AKS. Interviewers want operational judgment: how this topic affects state safety, plan review, blast radius, and handoff to GitOps—not HCL trivia. You should connect infra changes to application deploy paths, on-call pain, and compliance gates.

#### How it works (internals)
For Module versioning, Terraform builds a dependency DAG from HCL references, refreshes state via Azure RM provider APIs, and computes create/update/destroy. Provider schemas mark immutable attributes as ForceNew—plan symbols `-/+` mean replace, not in-place tweak. CI runs fmt, validate, tflint, Checkov, and emits a saved plan; prod apply uses OIDC with least-privilege RBAC on target resource groups and state storage.

#### When to use / when NOT to use
Apply Module versioning patterns when platform ownership requires declarative, reviewable infrastructure. Avoid Terraform for fast-moving app Deployments better owned by Argo CD. Push back on permanent portal hotfixes—import or codify within SLA. Use separate state stacks so a mistake here cannot delete unrelated production data.

#### Production example
Platform squad changed module versioning via PR #4821: plan artifact attached, Checkov passed, QA apply from main, prod apply next day with SoD approver using the same `tfplan` and commit SHA. Java teams consumed outputs through `terraform_remote_state`—no duplicate subnets or ACR instances. Rollback was `git revert` plus plan review, not portal edits.

#### Common mistakes
- Applying without plan review
- Unpinned modules/providers
- Shared state across unrelated teams
- Ignoring `-/+` in plan

#### Interview follow-ups (with model answers)

**Q:** What would a bad plan look like?
**A:** Unexpected `-/+` replaces, destroys on databases, or creates duplicates—always attach plan to PR.

**Q:** How split blast radius?
**A:** Separate state per domain and environment; remote outputs between stacks.

**Q:** Common Azure gotcha?
**A:** Many SKU and name changes ForceNew—read plan symbols carefully.

#### Scenario probe

**Situation:** Platform apply related to Module versioning fails mid-run with partial resources created.

**Model answer:** Pin `?ref=v1.2.3` on Git modules. Semver tags; never `@main` in prod. Stop applies, verify state lock, compare Activity Log to `terraform state list`, restore state version if needed, import orphans, re-plan from approved SHA—never blind re-apply.

---

### 13. Provider configuration and aliases.

**Short answer:** Multiple regions/subscriptions via provider aliases. Pass explicitly to resources. Pin provider and module versions in CI. Review every plan for unexpected destroys before production apply.

#### What it is
Provider configuration and aliases is a core Terraform concern for Azure platform teams supporting Java microservices on AKS. Interviewers want operational judgment: how this topic affects state safety, plan review, blast radius, and handoff to GitOps—not HCL trivia. You should connect infra changes to application deploy paths, on-call pain, and compliance gates.

#### How it works (internals)
For Provider configuration and aliases, Terraform builds a dependency DAG from HCL references, refreshes state via Azure RM provider APIs, and computes create/update/destroy. Provider schemas mark immutable attributes as ForceNew—plan symbols `-/+` mean replace, not in-place tweak. CI runs fmt, validate, tflint, Checkov, and emits a saved plan; prod apply uses OIDC with least-privilege RBAC on target resource groups and state storage.

#### When to use / when NOT to use
Apply Provider configuration and aliases patterns when platform ownership requires declarative, reviewable infrastructure. Avoid Terraform for fast-moving app Deployments better owned by Argo CD. Push back on permanent portal hotfixes—import or codify within SLA. Use separate state stacks so a mistake here cannot delete unrelated production data.

#### Production example
Platform squad changed provider configuration and aliases via PR #4821: plan artifact attached, Checkov passed, QA apply from main, prod apply next day with SoD approver using the same `tfplan` and commit SHA. Java teams consumed outputs through `terraform_remote_state`—no duplicate subnets or ACR instances. Rollback was `git revert` plus plan review, not portal edits.

#### Common mistakes
- Applying without plan review
- Unpinned modules/providers
- Shared state across unrelated teams
- Ignoring `-/+` in plan

#### Interview follow-ups (with model answers)

**Q:** What would a bad plan look like?
**A:** Unexpected `-/+` replaces, destroys on databases, or creates duplicates—always attach plan to PR.

**Q:** How split blast radius?
**A:** Separate state per domain and environment; remote outputs between stacks.

**Q:** Common Azure gotcha?
**A:** Many SKU and name changes ForceNew—read plan symbols carefully.

#### Scenario probe

**Situation:** Platform apply related to Provider configuration and aliases fails mid-run with partial resources created.

**Model answer:** Multiple regions/subscriptions via provider aliases. Pass explicitly to resources. Stop applies, verify state lock, compare Activity Log to `terraform state list`, restore state version if needed, import orphans, re-plan from approved SHA—never blind re-apply.

---

### 14. `count` vs `for_each`.

**Short answer:** for_each on map/set for stable keys; count index shifts destroy/recreate siblings. Pin provider and module versions in CI. Review every plan for unexpected destroys before production apply.

#### What it is
`count` vs `for_each` is a core Terraform concern for Azure platform teams supporting Java microservices on AKS. Interviewers want operational judgment: how this topic affects state safety, plan review, blast radius, and handoff to GitOps—not HCL trivia. You should connect infra changes to application deploy paths, on-call pain, and compliance gates.

#### How it works (internals)
For `count` vs `for_each`, Terraform builds a dependency DAG from HCL references, refreshes state via Azure RM provider APIs, and computes create/update/destroy. Provider schemas mark immutable attributes as ForceNew—plan symbols `-/+` mean replace, not in-place tweak. CI runs fmt, validate, tflint, Checkov, and emits a saved plan; prod apply uses OIDC with least-privilege RBAC on target resource groups and state storage.

#### When to use / when NOT to use
Apply `count` vs `for_each` patterns when platform ownership requires declarative, reviewable infrastructure. Avoid Terraform for fast-moving app Deployments better owned by Argo CD. Push back on permanent portal hotfixes—import or codify within SLA. Use separate state stacks so a mistake here cannot delete unrelated production data.

#### Production example
Platform squad changed `count` vs `for_each` via PR #4821: plan artifact attached, Checkov passed, QA apply from main, prod apply next day with SoD approver using the same `tfplan` and commit SHA. Java teams consumed outputs through `terraform_remote_state`—no duplicate subnets or ACR instances. Rollback was `git revert` plus plan review, not portal edits.

#### Common mistakes
- Applying without plan review
- Unpinned modules/providers
- Shared state across unrelated teams
- Ignoring `-/+` in plan

#### Interview follow-ups (with model answers)

**Q:** What would a bad plan look like?
**A:** Unexpected `-/+` replaces, destroys on databases, or creates duplicates—always attach plan to PR.

**Q:** How split blast radius?
**A:** Separate state per domain and environment; remote outputs between stacks.

**Q:** Common Azure gotcha?
**A:** Many SKU and name changes ForceNew—read plan symbols carefully.

#### Scenario probe

**Situation:** Platform apply related to `count` vs `for_each` fails mid-run with partial resources created.

**Model answer:** for_each on map/set for stable keys; count index shifts destroy/recreate siblings. Stop applies, verify state lock, compare Activity Log to `terraform state list`, restore state version if needed, import orphans, re-plan from approved SHA—never blind re-apply.

---

### 15. `create_before_destroy` vs `prevent_destroy`.

**Short answer:** Lifecycle meta-arguments for zero-downtime replace vs prod safety nets. Pin provider and module versions in CI. Review every plan for unexpected destroys before production apply.

#### What it is
`create_before_destroy` vs `prevent_destroy` is a core Terraform concern for Azure platform teams supporting Java microservices on AKS. Interviewers want operational judgment: how this topic affects state safety, plan review, blast radius, and handoff to GitOps—not HCL trivia. You should connect infra changes to application deploy paths, on-call pain, and compliance gates.

#### How it works (internals)
For `create_before_destroy` vs `prevent_destroy`, Terraform builds a dependency DAG from HCL references, refreshes state via Azure RM provider APIs, and computes create/update/destroy. Provider schemas mark immutable attributes as ForceNew—plan symbols `-/+` mean replace, not in-place tweak. CI runs fmt, validate, tflint, Checkov, and emits a saved plan; prod apply uses OIDC with least-privilege RBAC on target resource groups and state storage.

#### When to use / when NOT to use
Apply `create_before_destroy` vs `prevent_destroy` patterns when platform ownership requires declarative, reviewable infrastructure. Avoid Terraform for fast-moving app Deployments better owned by Argo CD. Push back on permanent portal hotfixes—import or codify within SLA. Use separate state stacks so a mistake here cannot delete unrelated production data.

#### Production example
Platform squad changed `create_before_destroy` vs `prevent_destroy` via PR #4821: plan artifact attached, Checkov passed, QA apply from main, prod apply next day with SoD approver using the same `tfplan` and commit SHA. Java teams consumed outputs through `terraform_remote_state`—no duplicate subnets or ACR instances. Rollback was `git revert` plus plan review, not portal edits.

#### Common mistakes
- Applying without plan review
- Unpinned modules/providers
- Shared state across unrelated teams
- Ignoring `-/+` in plan

#### Interview follow-ups (with model answers)

**Q:** What would a bad plan look like?
**A:** Unexpected `-/+` replaces, destroys on databases, or creates duplicates—always attach plan to PR.

**Q:** How split blast radius?
**A:** Separate state per domain and environment; remote outputs between stacks.

**Q:** Common Azure gotcha?
**A:** Many SKU and name changes ForceNew—read plan symbols carefully.

#### Scenario probe

**Situation:** Platform apply related to `create_before_destroy` vs `prevent_destroy` fails mid-run with partial resources created.

**Model answer:** Lifecycle meta-arguments for zero-downtime replace vs prod safety nets. Stop applies, verify state lock, compare Activity Log to `terraform state list`, restore state version if needed, import orphans, re-plan from approved SHA—never blind re-apply.

---

### 16. Force replacement.

**Short answer:** Plan `-/+` from taint or immutable attr change. Expect downtime and new IDs. Pin provider and module versions in CI. Review every plan for unexpected destroys before production apply.

#### What it is
Force replacement is a core Terraform concern for Azure platform teams supporting Java microservices on AKS. Interviewers want operational judgment: how this topic affects state safety, plan review, blast radius, and handoff to GitOps—not HCL trivia. You should connect infra changes to application deploy paths, on-call pain, and compliance gates.

#### How it works (internals)
For Force replacement, Terraform builds a dependency DAG from HCL references, refreshes state via Azure RM provider APIs, and computes create/update/destroy. Provider schemas mark immutable attributes as ForceNew—plan symbols `-/+` mean replace, not in-place tweak. CI runs fmt, validate, tflint, Checkov, and emits a saved plan; prod apply uses OIDC with least-privilege RBAC on target resource groups and state storage.

#### When to use / when NOT to use
Apply Force replacement patterns when platform ownership requires declarative, reviewable infrastructure. Avoid Terraform for fast-moving app Deployments better owned by Argo CD. Push back on permanent portal hotfixes—import or codify within SLA. Use separate state stacks so a mistake here cannot delete unrelated production data.

#### Production example
Platform squad changed force replacement via PR #4821: plan artifact attached, Checkov passed, QA apply from main, prod apply next day with SoD approver using the same `tfplan` and commit SHA. Java teams consumed outputs through `terraform_remote_state`—no duplicate subnets or ACR instances. Rollback was `git revert` plus plan review, not portal edits.

#### Common mistakes
- Applying without plan review
- Unpinned modules/providers
- Shared state across unrelated teams
- Ignoring `-/+` in plan

#### Interview follow-ups (with model answers)

**Q:** What would a bad plan look like?
**A:** Unexpected `-/+` replaces, destroys on databases, or creates duplicates—always attach plan to PR.

**Q:** How split blast radius?
**A:** Separate state per domain and environment; remote outputs between stacks.

**Q:** Common Azure gotcha?
**A:** Many SKU and name changes ForceNew—read plan symbols carefully.

#### Scenario probe

**Situation:** Platform apply related to Force replacement fails mid-run with partial resources created.

**Model answer:** Plan `-/+` from taint or immutable attr change. Expect downtime and new IDs. Stop applies, verify state lock, compare Activity Log to `terraform state list`, restore state version if needed, import orphans, re-plan from approved SHA—never blind re-apply.

---

### 17. Sensitive values.

**Short answer:** Mark sensitive; redacted in logs. Still in state—encrypt backend. Pin provider and module versions in CI. Review every plan for unexpected destroys before production apply.

#### What it is
Sensitive values is a core Terraform concern for Azure platform teams supporting Java microservices on AKS. Interviewers want operational judgment: how this topic affects state safety, plan review, blast radius, and handoff to GitOps—not HCL trivia. You should connect infra changes to application deploy paths, on-call pain, and compliance gates.

#### How it works (internals)
For Sensitive values, Terraform builds a dependency DAG from HCL references, refreshes state via Azure RM provider APIs, and computes create/update/destroy. Provider schemas mark immutable attributes as ForceNew—plan symbols `-/+` mean replace, not in-place tweak. CI runs fmt, validate, tflint, Checkov, and emits a saved plan; prod apply uses OIDC with least-privilege RBAC on target resource groups and state storage.

#### When to use / when NOT to use
Apply Sensitive values patterns when platform ownership requires declarative, reviewable infrastructure. Avoid Terraform for fast-moving app Deployments better owned by Argo CD. Push back on permanent portal hotfixes—import or codify within SLA. Use separate state stacks so a mistake here cannot delete unrelated production data.

#### Production example
Platform squad changed sensitive values via PR #4821: plan artifact attached, Checkov passed, QA apply from main, prod apply next day with SoD approver using the same `tfplan` and commit SHA. Java teams consumed outputs through `terraform_remote_state`—no duplicate subnets or ACR instances. Rollback was `git revert` plus plan review, not portal edits.

#### Common mistakes
- Applying without plan review
- Unpinned modules/providers
- Shared state across unrelated teams
- Ignoring `-/+` in plan

#### Interview follow-ups (with model answers)

**Q:** What would a bad plan look like?
**A:** Unexpected `-/+` replaces, destroys on databases, or creates duplicates—always attach plan to PR.

**Q:** How split blast radius?
**A:** Separate state per domain and environment; remote outputs between stacks.

**Q:** Common Azure gotcha?
**A:** Many SKU and name changes ForceNew—read plan symbols carefully.

#### Scenario probe

**Situation:** Platform apply related to Sensitive values fails mid-run with partial resources created.

**Model answer:** Mark sensitive; redacted in logs. Still in state—encrypt backend. Stop applies, verify state lock, compare Activity Log to `terraform state list`, restore state version if needed, import orphans, re-plan from approved SHA—never blind re-apply.

---

### 18. `terraform.tfvars` vs env vs CI.

**Short answer:** Layer vars: defaults, tfvars per env, CI `-var` for secrets from vault. Pin provider and module versions in CI. Review every plan for unexpected destroys before production apply.

#### What it is
`terraform.tfvars` vs env vs CI is a core Terraform concern for Azure platform teams supporting Java microservices on AKS. Interviewers want operational judgment: how this topic affects state safety, plan review, blast radius, and handoff to GitOps—not HCL trivia. You should connect infra changes to application deploy paths, on-call pain, and compliance gates.

#### How it works (internals)
For `terraform.tfvars` vs env vs CI, Terraform builds a dependency DAG from HCL references, refreshes state via Azure RM provider APIs, and computes create/update/destroy. Provider schemas mark immutable attributes as ForceNew—plan symbols `-/+` mean replace, not in-place tweak. CI runs fmt, validate, tflint, Checkov, and emits a saved plan; prod apply uses OIDC with least-privilege RBAC on target resource groups and state storage.

#### When to use / when NOT to use
Apply `terraform.tfvars` vs env vs CI patterns when platform ownership requires declarative, reviewable infrastructure. Avoid Terraform for fast-moving app Deployments better owned by Argo CD. Push back on permanent portal hotfixes—import or codify within SLA. Use separate state stacks so a mistake here cannot delete unrelated production data.

#### Production example
Platform squad changed `terraform.tfvars` vs env vs ci via PR #4821: plan artifact attached, Checkov passed, QA apply from main, prod apply next day with SoD approver using the same `tfplan` and commit SHA. Java teams consumed outputs through `terraform_remote_state`—no duplicate subnets or ACR instances. Rollback was `git revert` plus plan review, not portal edits.

#### Common mistakes
- Applying without plan review
- Unpinned modules/providers
- Shared state across unrelated teams
- Ignoring `-/+` in plan

#### Interview follow-ups (with model answers)

**Q:** What would a bad plan look like?
**A:** Unexpected `-/+` replaces, destroys on databases, or creates duplicates—always attach plan to PR.

**Q:** How split blast radius?
**A:** Separate state per domain and environment; remote outputs between stacks.

**Q:** Common Azure gotcha?
**A:** Many SKU and name changes ForceNew—read plan symbols carefully.

#### Scenario probe

**Situation:** Platform apply related to `terraform.tfvars` vs env vs CI fails mid-run with partial resources created.

**Model answer:** Layer vars: defaults, tfvars per env, CI `-var` for secrets from vault. Stop applies, verify state lock, compare Activity Log to `terraform state list`, restore state version if needed, import orphans, re-plan from approved SHA—never blind re-apply.

---

### 19. Data sources.

**Short answer:** Read-only API lookups without manage lifecycle—existing RG, subnet, DNS. Pin provider and module versions in CI. Review every plan for unexpected destroys before production apply.

#### What it is
Data sources is a core Terraform concern for Azure platform teams supporting Java microservices on AKS. Interviewers want operational judgment: how this topic affects state safety, plan review, blast radius, and handoff to GitOps—not HCL trivia. You should connect infra changes to application deploy paths, on-call pain, and compliance gates.

#### How it works (internals)
For Data sources, Terraform builds a dependency DAG from HCL references, refreshes state via Azure RM provider APIs, and computes create/update/destroy. Provider schemas mark immutable attributes as ForceNew—plan symbols `-/+` mean replace, not in-place tweak. CI runs fmt, validate, tflint, Checkov, and emits a saved plan; prod apply uses OIDC with least-privilege RBAC on target resource groups and state storage.

#### When to use / when NOT to use
Apply Data sources patterns when platform ownership requires declarative, reviewable infrastructure. Avoid Terraform for fast-moving app Deployments better owned by Argo CD. Push back on permanent portal hotfixes—import or codify within SLA. Use separate state stacks so a mistake here cannot delete unrelated production data.

#### Production example
Platform squad changed data sources via PR #4821: plan artifact attached, Checkov passed, QA apply from main, prod apply next day with SoD approver using the same `tfplan` and commit SHA. Java teams consumed outputs through `terraform_remote_state`—no duplicate subnets or ACR instances. Rollback was `git revert` plus plan review, not portal edits.

#### Common mistakes
- Applying without plan review
- Unpinned modules/providers
- Shared state across unrelated teams
- Ignoring `-/+` in plan

#### Interview follow-ups (with model answers)

**Q:** What would a bad plan look like?
**A:** Unexpected `-/+` replaces, destroys on databases, or creates duplicates—always attach plan to PR.

**Q:** How split blast radius?
**A:** Separate state per domain and environment; remote outputs between stacks.

**Q:** Common Azure gotcha?
**A:** Many SKU and name changes ForceNew—read plan symbols carefully.

#### Scenario probe

**Situation:** Platform apply related to Data sources fails mid-run with partial resources created.

**Model answer:** Read-only API lookups without manage lifecycle—existing RG, subnet, DNS. Stop applies, verify state lock, compare Activity Log to `terraform state list`, restore state version if needed, import orphans, re-plan from approved SHA—never blind re-apply.

---

### 20. `depends_on` smell.

**Short answer:** Explicit depends_on when no attribute ref—code smell; refactor to outputs/data. Pin provider and module versions in CI. Review every plan for unexpected destroys before production apply.

#### What it is
`depends_on` smell is a core Terraform concern for Azure platform teams supporting Java microservices on AKS. Interviewers want operational judgment: how this topic affects state safety, plan review, blast radius, and handoff to GitOps—not HCL trivia. You should connect infra changes to application deploy paths, on-call pain, and compliance gates.

#### How it works (internals)
For `depends_on` smell, Terraform builds a dependency DAG from HCL references, refreshes state via Azure RM provider APIs, and computes create/update/destroy. Provider schemas mark immutable attributes as ForceNew—plan symbols `-/+` mean replace, not in-place tweak. CI runs fmt, validate, tflint, Checkov, and emits a saved plan; prod apply uses OIDC with least-privilege RBAC on target resource groups and state storage.

#### When to use / when NOT to use
Apply `depends_on` smell patterns when platform ownership requires declarative, reviewable infrastructure. Avoid Terraform for fast-moving app Deployments better owned by Argo CD. Push back on permanent portal hotfixes—import or codify within SLA. Use separate state stacks so a mistake here cannot delete unrelated production data.

#### Production example
Platform squad changed `depends_on` smell via PR #4821: plan artifact attached, Checkov passed, QA apply from main, prod apply next day with SoD approver using the same `tfplan` and commit SHA. Java teams consumed outputs through `terraform_remote_state`—no duplicate subnets or ACR instances. Rollback was `git revert` plus plan review, not portal edits.

#### Common mistakes
- Applying without plan review
- Unpinned modules/providers
- Shared state across unrelated teams
- Ignoring `-/+` in plan

#### Interview follow-ups (with model answers)

**Q:** What would a bad plan look like?
**A:** Unexpected `-/+` replaces, destroys on databases, or creates duplicates—always attach plan to PR.

**Q:** How split blast radius?
**A:** Separate state per domain and environment; remote outputs between stacks.

**Q:** Common Azure gotcha?
**A:** Many SKU and name changes ForceNew—read plan symbols carefully.

#### Scenario probe

**Situation:** Platform apply related to `depends_on` smell fails mid-run with partial resources created.

**Model answer:** Explicit depends_on when no attribute ref—code smell; refactor to outputs/data. Stop applies, verify state lock, compare Activity Log to `terraform state list`, restore state version if needed, import orphans, re-plan from approved SHA—never blind re-apply.

---

### 21. Terraform Cloud vs DIY backend.

**Short answer:** TFC gives remote run, policy, UI; DIY Blob+Actions cheaper at scale with more ops burden.

#### What it is
Terraform Cloud vs DIY backend is a core Terraform concern for Azure platform teams supporting Java microservices on AKS. Interviewers want operational judgment: how this topic affects state safety, plan review, blast radius, and handoff to GitOps—not HCL trivia. You should connect infra changes to application deploy paths, on-call pain, and compliance gates.

#### How it works (internals)
For Terraform Cloud vs DIY backend, Terraform builds a dependency DAG from HCL references, refreshes state via Azure RM provider APIs, and computes create/update/destroy. Provider schemas mark immutable attributes as ForceNew—plan symbols `-/+` mean replace, not in-place tweak. CI runs fmt, validate, tflint, Checkov, and emits a saved plan; prod apply uses OIDC with least-privilege RBAC on target resource groups and state storage.

#### When to use / when NOT to use
Apply Terraform Cloud vs DIY backend patterns when platform ownership requires declarative, reviewable infrastructure. Avoid Terraform for fast-moving app Deployments better owned by Argo CD. Push back on permanent portal hotfixes—import or codify within SLA. Use separate state stacks so a mistake here cannot delete unrelated production data.

#### Production example
Platform squad changed terraform cloud vs diy backend via PR #4821: plan artifact attached, Checkov passed, QA apply from main, prod apply next day with SoD approver using the same `tfplan` and commit SHA. Java teams consumed outputs through `terraform_remote_state`—no duplicate subnets or ACR instances. Rollback was `git revert` plus plan review, not portal edits.

#### Common mistakes
- Applying without plan review
- Unpinned modules/providers
- Shared state across unrelated teams
- Ignoring `-/+` in plan

#### Interview follow-ups (with model answers)

**Q:** What would a bad plan look like?
**A:** Unexpected `-/+` replaces, destroys on databases, or creates duplicates—always attach plan to PR.

**Q:** How split blast radius?
**A:** Separate state per domain and environment; remote outputs between stacks.

**Q:** Common Azure gotcha?
**A:** Many SKU and name changes ForceNew—read plan symbols carefully.

#### Scenario probe

**Situation:** Platform apply related to Terraform Cloud vs DIY backend fails mid-run with partial resources created.

**Model answer:** TFC gives remote run, policy, UI; DIY Blob+Actions cheaper at scale with more ops burden. Stop applies, verify state lock, compare Activity Log to `terraform state list`, restore state version if needed, import orphans, re-plan from approved SHA—never blind re-apply.

---

### 22. Policy as code.

**Short answer:** OPA/Sentinel/Checkov block bad plans—public IPs, missing tags, open NSG. Pin provider and module versions in CI. Review every plan for unexpected destroys before production apply.

#### What it is
Policy as code is a core Terraform concern for Azure platform teams supporting Java microservices on AKS. Interviewers want operational judgment: how this topic affects state safety, plan review, blast radius, and handoff to GitOps—not HCL trivia. You should connect infra changes to application deploy paths, on-call pain, and compliance gates.

#### How it works (internals)
For Policy as code, Terraform builds a dependency DAG from HCL references, refreshes state via Azure RM provider APIs, and computes create/update/destroy. Provider schemas mark immutable attributes as ForceNew—plan symbols `-/+` mean replace, not in-place tweak. CI runs fmt, validate, tflint, Checkov, and emits a saved plan; prod apply uses OIDC with least-privilege RBAC on target resource groups and state storage.

#### When to use / when NOT to use
Apply Policy as code patterns when platform ownership requires declarative, reviewable infrastructure. Avoid Terraform for fast-moving app Deployments better owned by Argo CD. Push back on permanent portal hotfixes—import or codify within SLA. Use separate state stacks so a mistake here cannot delete unrelated production data.

#### Production example
Platform squad changed policy as code via PR #4821: plan artifact attached, Checkov passed, QA apply from main, prod apply next day with SoD approver using the same `tfplan` and commit SHA. Java teams consumed outputs through `terraform_remote_state`—no duplicate subnets or ACR instances. Rollback was `git revert` plus plan review, not portal edits.

#### Common mistakes
- Applying without plan review
- Unpinned modules/providers
- Shared state across unrelated teams
- Ignoring `-/+` in plan

#### Interview follow-ups (with model answers)

**Q:** What would a bad plan look like?
**A:** Unexpected `-/+` replaces, destroys on databases, or creates duplicates—always attach plan to PR.

**Q:** How split blast radius?
**A:** Separate state per domain and environment; remote outputs between stacks.

**Q:** Common Azure gotcha?
**A:** Many SKU and name changes ForceNew—read plan symbols carefully.

#### Scenario probe

**Situation:** Platform apply related to Policy as code fails mid-run with partial resources created.

**Model answer:** OPA/Sentinel/Checkov block bad plans—public IPs, missing tags, open NSG. Stop applies, verify state lock, compare Activity Log to `terraform state list`, restore state version if needed, import orphans, re-plan from approved SHA—never blind re-apply.

---

### 23. AzureRM provider: resource groups and tags.

**Short answer:** RG is scope boundary; consistent tags via locals merge and Policy. Pin provider and module versions in CI. Review every plan for unexpected destroys before production apply.

#### What it is
AzureRM provider: resource groups and tags is a core Terraform concern for Azure platform teams supporting Java microservices on AKS. Interviewers want operational judgment: how this topic affects state safety, plan review, blast radius, and handoff to GitOps—not HCL trivia. You should connect infra changes to application deploy paths, on-call pain, and compliance gates.

#### How it works (internals)
For AzureRM provider: resource groups and tags, Terraform builds a dependency DAG from HCL references, refreshes state via Azure RM provider APIs, and computes create/update/destroy. Provider schemas mark immutable attributes as ForceNew—plan symbols `-/+` mean replace, not in-place tweak. CI runs fmt, validate, tflint, Checkov, and emits a saved plan; prod apply uses OIDC with least-privilege RBAC on target resource groups and state storage.

#### When to use / when NOT to use
Apply AzureRM provider: resource groups and tags patterns when platform ownership requires declarative, reviewable infrastructure. Avoid Terraform for fast-moving app Deployments better owned by Argo CD. Push back on permanent portal hotfixes—import or codify within SLA. Use separate state stacks so a mistake here cannot delete unrelated production data.

#### Production example
Platform squad changed azurerm provider: resource groups and tags via PR #4821: plan artifact attached, Checkov passed, QA apply from main, prod apply next day with SoD approver using the same `tfplan` and commit SHA. Java teams consumed outputs through `terraform_remote_state`—no duplicate subnets or ACR instances. Rollback was `git revert` plus plan review, not portal edits.

#### Common mistakes
- Applying without plan review
- Unpinned modules/providers
- Shared state across unrelated teams
- Ignoring `-/+` in plan

#### Interview follow-ups (with model answers)

**Q:** What would a bad plan look like?
**A:** Unexpected `-/+` replaces, destroys on databases, or creates duplicates—always attach plan to PR.

**Q:** How split blast radius?
**A:** Separate state per domain and environment; remote outputs between stacks.

**Q:** Common Azure gotcha?
**A:** Many SKU and name changes ForceNew—read plan symbols carefully.

#### Scenario probe

**Situation:** Platform apply related to AzureRM provider: resource groups and tags fails mid-run with partial resources created.

**Model answer:** RG is scope boundary; consistent tags via locals merge and Policy. Stop applies, verify state lock, compare Activity Log to `terraform state list`, restore state version if needed, import orphans, re-plan from approved SHA—never blind re-apply.

---

### 24. Provisioners (`local-exec`) are last resort.

**Short answer:** Run scripts on apply—fragile, non-declarative. Prefer cloud-native or pipeline steps. Pin provider and module versions in CI. Review every plan for unexpected destroys before production apply.

#### What it is
Provisioners (`local-exec`) are last resort is a core Terraform concern for Azure platform teams supporting Java microservices on AKS. Interviewers want operational judgment: how this topic affects state safety, plan review, blast radius, and handoff to GitOps—not HCL trivia. You should connect infra changes to application deploy paths, on-call pain, and compliance gates.

#### How it works (internals)
For Provisioners (`local-exec`) are last resort, Terraform builds a dependency DAG from HCL references, refreshes state via Azure RM provider APIs, and computes create/update/destroy. Provider schemas mark immutable attributes as ForceNew—plan symbols `-/+` mean replace, not in-place tweak. CI runs fmt, validate, tflint, Checkov, and emits a saved plan; prod apply uses OIDC with least-privilege RBAC on target resource groups and state storage.

#### When to use / when NOT to use
Apply Provisioners (`local-exec`) are last resort patterns when platform ownership requires declarative, reviewable infrastructure. Avoid Terraform for fast-moving app Deployments better owned by Argo CD. Push back on permanent portal hotfixes—import or codify within SLA. Use separate state stacks so a mistake here cannot delete unrelated production data.

#### Production example
Platform squad changed provisioners (`local-exec`) are last resort via PR #4821: plan artifact attached, Checkov passed, QA apply from main, prod apply next day with SoD approver using the same `tfplan` and commit SHA. Java teams consumed outputs through `terraform_remote_state`—no duplicate subnets or ACR instances. Rollback was `git revert` plus plan review, not portal edits.

#### Common mistakes
- Applying without plan review
- Unpinned modules/providers
- Shared state across unrelated teams
- Ignoring `-/+` in plan

#### Interview follow-ups (with model answers)

**Q:** What would a bad plan look like?
**A:** Unexpected `-/+` replaces, destroys on databases, or creates duplicates—always attach plan to PR.

**Q:** How split blast radius?
**A:** Separate state per domain and environment; remote outputs between stacks.

**Q:** Common Azure gotcha?
**A:** Many SKU and name changes ForceNew—read plan symbols carefully.

#### Scenario probe

**Situation:** Platform apply related to Provisioners (`local-exec`) are last resort fails mid-run with partial resources created.

**Model answer:** Run scripts on apply—fragile, non-declarative. Prefer cloud-native or pipeline steps. Stop applies, verify state lock, compare Activity Log to `terraform state list`, restore state version if needed, import orphans, re-plan from approved SHA—never blind re-apply.

---

### 25. `null_resource` / `terraform_data`.

**Short answer:** Triggers for one-off glue; replace with native resources when possible. Pin provider and module versions in CI. Review every plan for unexpected destroys before production apply.

#### What it is
`null_resource` / `terraform_data` is a core Terraform concern for Azure platform teams supporting Java microservices on AKS. Interviewers want operational judgment: how this topic affects state safety, plan review, blast radius, and handoff to GitOps—not HCL trivia. You should connect infra changes to application deploy paths, on-call pain, and compliance gates.

#### How it works (internals)
For `null_resource` / `terraform_data`, Terraform builds a dependency DAG from HCL references, refreshes state via Azure RM provider APIs, and computes create/update/destroy. Provider schemas mark immutable attributes as ForceNew—plan symbols `-/+` mean replace, not in-place tweak. CI runs fmt, validate, tflint, Checkov, and emits a saved plan; prod apply uses OIDC with least-privilege RBAC on target resource groups and state storage.

#### When to use / when NOT to use
Apply `null_resource` / `terraform_data` patterns when platform ownership requires declarative, reviewable infrastructure. Avoid Terraform for fast-moving app Deployments better owned by Argo CD. Push back on permanent portal hotfixes—import or codify within SLA. Use separate state stacks so a mistake here cannot delete unrelated production data.

#### Production example
Platform squad changed `null_resource` / `terraform_data` via PR #4821: plan artifact attached, Checkov passed, QA apply from main, prod apply next day with SoD approver using the same `tfplan` and commit SHA. Java teams consumed outputs through `terraform_remote_state`—no duplicate subnets or ACR instances. Rollback was `git revert` plus plan review, not portal edits.

#### Common mistakes
- Applying without plan review
- Unpinned modules/providers
- Shared state across unrelated teams
- Ignoring `-/+` in plan

#### Interview follow-ups (with model answers)

**Q:** What would a bad plan look like?
**A:** Unexpected `-/+` replaces, destroys on databases, or creates duplicates—always attach plan to PR.

**Q:** How split blast radius?
**A:** Separate state per domain and environment; remote outputs between stacks.

**Q:** Common Azure gotcha?
**A:** Many SKU and name changes ForceNew—read plan symbols carefully.

#### Scenario probe

**Situation:** Platform apply related to `null_resource` / `terraform_data` fails mid-run with partial resources created.

**Model answer:** Triggers for one-off glue; replace with native resources when possible. Stop applies, verify state lock, compare Activity Log to `terraform state list`, restore state version if needed, import orphans, re-plan from approved SHA—never blind re-apply.

---

### 26. Output between stacks.

**Short answer:** Remote state data source or well-versioned outputs—contract between platform stacks. Pin provider and module versions in CI. Review every plan for unexpected destroys before production apply.

#### What it is
Output between stacks is a core Terraform concern for Azure platform teams supporting Java microservices on AKS. Interviewers want operational judgment: how this topic affects state safety, plan review, blast radius, and handoff to GitOps—not HCL trivia. You should connect infra changes to application deploy paths, on-call pain, and compliance gates.

#### How it works (internals)
For Output between stacks, Terraform builds a dependency DAG from HCL references, refreshes state via Azure RM provider APIs, and computes create/update/destroy. Provider schemas mark immutable attributes as ForceNew—plan symbols `-/+` mean replace, not in-place tweak. CI runs fmt, validate, tflint, Checkov, and emits a saved plan; prod apply uses OIDC with least-privilege RBAC on target resource groups and state storage.

#### When to use / when NOT to use
Apply Output between stacks patterns when platform ownership requires declarative, reviewable infrastructure. Avoid Terraform for fast-moving app Deployments better owned by Argo CD. Push back on permanent portal hotfixes—import or codify within SLA. Use separate state stacks so a mistake here cannot delete unrelated production data.

#### Production example
Platform squad changed output between stacks via PR #4821: plan artifact attached, Checkov passed, QA apply from main, prod apply next day with SoD approver using the same `tfplan` and commit SHA. Java teams consumed outputs through `terraform_remote_state`—no duplicate subnets or ACR instances. Rollback was `git revert` plus plan review, not portal edits.

#### Common mistakes
- Applying without plan review
- Unpinned modules/providers
- Shared state across unrelated teams
- Ignoring `-/+` in plan

#### Interview follow-ups (with model answers)

**Q:** What would a bad plan look like?
**A:** Unexpected `-/+` replaces, destroys on databases, or creates duplicates—always attach plan to PR.

**Q:** How split blast radius?
**A:** Separate state per domain and environment; remote outputs between stacks.

**Q:** Common Azure gotcha?
**A:** Many SKU and name changes ForceNew—read plan symbols carefully.

#### Scenario probe

**Situation:** Platform apply related to Output between stacks fails mid-run with partial resources created.

**Model answer:** Remote state data source or well-versioned outputs—contract between platform stacks. Stop applies, verify state lock, compare Activity Log to `terraform state list`, restore state version if needed, import orphans, re-plan from approved SHA—never blind re-apply.

---

### 27. Blast radius.

**Short answer:** Split state by domain/env so one bad apply cannot flatten entire estate. Pin provider and module versions in CI. Review every plan for unexpected destroys before production apply.

#### What it is
Blast radius is a core Terraform concern for Azure platform teams supporting Java microservices on AKS. Interviewers want operational judgment: how this topic affects state safety, plan review, blast radius, and handoff to GitOps—not HCL trivia. You should connect infra changes to application deploy paths, on-call pain, and compliance gates.

#### How it works (internals)
For Blast radius, Terraform builds a dependency DAG from HCL references, refreshes state via Azure RM provider APIs, and computes create/update/destroy. Provider schemas mark immutable attributes as ForceNew—plan symbols `-/+` mean replace, not in-place tweak. CI runs fmt, validate, tflint, Checkov, and emits a saved plan; prod apply uses OIDC with least-privilege RBAC on target resource groups and state storage.

#### When to use / when NOT to use
Apply Blast radius patterns when platform ownership requires declarative, reviewable infrastructure. Avoid Terraform for fast-moving app Deployments better owned by Argo CD. Push back on permanent portal hotfixes—import or codify within SLA. Use separate state stacks so a mistake here cannot delete unrelated production data.

#### Production example
Platform squad changed blast radius via PR #4821: plan artifact attached, Checkov passed, QA apply from main, prod apply next day with SoD approver using the same `tfplan` and commit SHA. Java teams consumed outputs through `terraform_remote_state`—no duplicate subnets or ACR instances. Rollback was `git revert` plus plan review, not portal edits.

#### Common mistakes
- Applying without plan review
- Unpinned modules/providers
- Shared state across unrelated teams
- Ignoring `-/+` in plan

#### Interview follow-ups (with model answers)

**Q:** What would a bad plan look like?
**A:** Unexpected `-/+` replaces, destroys on databases, or creates duplicates—always attach plan to PR.

**Q:** How split blast radius?
**A:** Separate state per domain and environment; remote outputs between stacks.

**Q:** Common Azure gotcha?
**A:** Many SKU and name changes ForceNew—read plan symbols carefully.

#### Scenario probe

**Situation:** Platform apply related to Blast radius fails mid-run with partial resources created.

**Model answer:** Split state by domain/env so one bad apply cannot flatten entire estate. Stop applies, verify state lock, compare Activity Log to `terraform state list`, restore state version if needed, import orphans, re-plan from approved SHA—never blind re-apply.

---

### 28. Applying DB changes.

**Short answer:** TF manages server/firewall; schema via Flyway in app pipeline—not TF provisioners. Pin provider and module versions in CI. Review every plan for unexpected destroys before production apply.

#### What it is
Applying DB changes is a core Terraform concern for Azure platform teams supporting Java microservices on AKS. Interviewers want operational judgment: how this topic affects state safety, plan review, blast radius, and handoff to GitOps—not HCL trivia. You should connect infra changes to application deploy paths, on-call pain, and compliance gates.

#### How it works (internals)
For Applying DB changes, Terraform builds a dependency DAG from HCL references, refreshes state via Azure RM provider APIs, and computes create/update/destroy. Provider schemas mark immutable attributes as ForceNew—plan symbols `-/+` mean replace, not in-place tweak. CI runs fmt, validate, tflint, Checkov, and emits a saved plan; prod apply uses OIDC with least-privilege RBAC on target resource groups and state storage.

#### When to use / when NOT to use
Apply Applying DB changes patterns when platform ownership requires declarative, reviewable infrastructure. Avoid Terraform for fast-moving app Deployments better owned by Argo CD. Push back on permanent portal hotfixes—import or codify within SLA. Use separate state stacks so a mistake here cannot delete unrelated production data.

#### Production example
Platform squad changed applying db changes via PR #4821: plan artifact attached, Checkov passed, QA apply from main, prod apply next day with SoD approver using the same `tfplan` and commit SHA. Java teams consumed outputs through `terraform_remote_state`—no duplicate subnets or ACR instances. Rollback was `git revert` plus plan review, not portal edits.

#### Common mistakes
- Applying without plan review
- Unpinned modules/providers
- Shared state across unrelated teams
- Ignoring `-/+` in plan

#### Interview follow-ups (with model answers)

**Q:** What would a bad plan look like?
**A:** Unexpected `-/+` replaces, destroys on databases, or creates duplicates—always attach plan to PR.

**Q:** How split blast radius?
**A:** Separate state per domain and environment; remote outputs between stacks.

**Q:** Common Azure gotcha?
**A:** Many SKU and name changes ForceNew—read plan symbols carefully.

#### Scenario probe

**Situation:** Platform apply related to Applying DB changes fails mid-run with partial resources created.

**Model answer:** TF manages server/firewall; schema via Flyway in app pipeline—not TF provisioners. Stop applies, verify state lock, compare Activity Log to `terraform state list`, restore state version if needed, import orphans, re-plan from approved SHA—never blind re-apply.

---

### 29. AKS in TF.

**Short answer:** Cluster, node pools, identity, network plugin in platform stack. Addons via Helm/GitOps often cleaner. Pin provider and module versions in CI. Review every plan for unexpected destroys before production apply.

#### What it is
AKS in TF is a core Terraform concern for Azure platform teams supporting Java microservices on AKS. Interviewers want operational judgment: how this topic affects state safety, plan review, blast radius, and handoff to GitOps—not HCL trivia. You should connect infra changes to application deploy paths, on-call pain, and compliance gates.

#### How it works (internals)
For AKS in TF, Terraform builds a dependency DAG from HCL references, refreshes state via Azure RM provider APIs, and computes create/update/destroy. Provider schemas mark immutable attributes as ForceNew—plan symbols `-/+` mean replace, not in-place tweak. CI runs fmt, validate, tflint, Checkov, and emits a saved plan; prod apply uses OIDC with least-privilege RBAC on target resource groups and state storage.

#### When to use / when NOT to use
Apply AKS in TF patterns when platform ownership requires declarative, reviewable infrastructure. Avoid Terraform for fast-moving app Deployments better owned by Argo CD. Push back on permanent portal hotfixes—import or codify within SLA. Use separate state stacks so a mistake here cannot delete unrelated production data.

#### Production example
Platform squad changed aks in tf via PR #4821: plan artifact attached, Checkov passed, QA apply from main, prod apply next day with SoD approver using the same `tfplan` and commit SHA. Java teams consumed outputs through `terraform_remote_state`—no duplicate subnets or ACR instances. Rollback was `git revert` plus plan review, not portal edits.

#### Common mistakes
- Applying without plan review
- Unpinned modules/providers
- Shared state across unrelated teams
- Ignoring `-/+` in plan

#### Interview follow-ups (with model answers)

**Q:** What would a bad plan look like?
**A:** Unexpected `-/+` replaces, destroys on databases, or creates duplicates—always attach plan to PR.

**Q:** How split blast radius?
**A:** Separate state per domain and environment; remote outputs between stacks.

**Q:** Common Azure gotcha?
**A:** Many SKU and name changes ForceNew—read plan symbols carefully.

#### Scenario probe

**Situation:** Platform apply related to AKS in TF fails mid-run with partial resources created.

**Model answer:** Cluster, node pools, identity, network plugin in platform stack. Addons via Helm/GitOps often cleaner. Stop applies, verify state lock, compare Activity Log to `terraform state list`, restore state version if needed, import orphans, re-plan from approved SHA—never blind re-apply.

---

### 30. Kubernetes/Helm providers inside TF.

**Short answer:** Use for bootstrap addons only; avoid app Deployments if GitOps exists. Pin provider and module versions in CI. Review every plan for unexpected destroys before production apply.

#### What it is
Kubernetes/Helm providers inside TF is a core Terraform concern for Azure platform teams supporting Java microservices on AKS. Interviewers want operational judgment: how this topic affects state safety, plan review, blast radius, and handoff to GitOps—not HCL trivia. You should connect infra changes to application deploy paths, on-call pain, and compliance gates.

#### How it works (internals)
For Kubernetes/Helm providers inside TF, Terraform builds a dependency DAG from HCL references, refreshes state via Azure RM provider APIs, and computes create/update/destroy. Provider schemas mark immutable attributes as ForceNew—plan symbols `-/+` mean replace, not in-place tweak. CI runs fmt, validate, tflint, Checkov, and emits a saved plan; prod apply uses OIDC with least-privilege RBAC on target resource groups and state storage.

#### When to use / when NOT to use
Apply Kubernetes/Helm providers inside TF patterns when platform ownership requires declarative, reviewable infrastructure. Avoid Terraform for fast-moving app Deployments better owned by Argo CD. Push back on permanent portal hotfixes—import or codify within SLA. Use separate state stacks so a mistake here cannot delete unrelated production data.

#### Production example
Platform squad changed kubernetes/helm providers inside tf via PR #4821: plan artifact attached, Checkov passed, QA apply from main, prod apply next day with SoD approver using the same `tfplan` and commit SHA. Java teams consumed outputs through `terraform_remote_state`—no duplicate subnets or ACR instances. Rollback was `git revert` plus plan review, not portal edits.

#### Common mistakes
- Applying without plan review
- Unpinned modules/providers
- Shared state across unrelated teams
- Ignoring `-/+` in plan

#### Interview follow-ups (with model answers)

**Q:** What would a bad plan look like?
**A:** Unexpected `-/+` replaces, destroys on databases, or creates duplicates—always attach plan to PR.

**Q:** How split blast radius?
**A:** Separate state per domain and environment; remote outputs between stacks.

**Q:** Common Azure gotcha?
**A:** Many SKU and name changes ForceNew—read plan symbols carefully.

#### Scenario probe

**Situation:** Platform apply related to Kubernetes/Helm providers inside TF fails mid-run with partial resources created.

**Model answer:** Use for bootstrap addons only; avoid app Deployments if GitOps exists. Stop applies, verify state lock, compare Activity Log to `terraform state list`, restore state version if needed, import orphans, re-plan from approved SHA—never blind re-apply.

---

### 31. `azurerm` vs `azapi`.

**Short answer:** azurerm stable resources; azapi for preview/new API properties not yet in azurerm. Pin provider and module versions in CI. Review every plan for unexpected destroys before production apply.

#### What it is
`azurerm` vs `azapi` is a core Terraform concern for Azure platform teams supporting Java microservices on AKS. Interviewers want operational judgment: how this topic affects state safety, plan review, blast radius, and handoff to GitOps—not HCL trivia. You should connect infra changes to application deploy paths, on-call pain, and compliance gates.

#### How it works (internals)
For `azurerm` vs `azapi`, Terraform builds a dependency DAG from HCL references, refreshes state via Azure RM provider APIs, and computes create/update/destroy. Provider schemas mark immutable attributes as ForceNew—plan symbols `-/+` mean replace, not in-place tweak. CI runs fmt, validate, tflint, Checkov, and emits a saved plan; prod apply uses OIDC with least-privilege RBAC on target resource groups and state storage.

#### When to use / when NOT to use
Apply `azurerm` vs `azapi` patterns when platform ownership requires declarative, reviewable infrastructure. Avoid Terraform for fast-moving app Deployments better owned by Argo CD. Push back on permanent portal hotfixes—import or codify within SLA. Use separate state stacks so a mistake here cannot delete unrelated production data.

#### Production example
Platform squad changed `azurerm` vs `azapi` via PR #4821: plan artifact attached, Checkov passed, QA apply from main, prod apply next day with SoD approver using the same `tfplan` and commit SHA. Java teams consumed outputs through `terraform_remote_state`—no duplicate subnets or ACR instances. Rollback was `git revert` plus plan review, not portal edits.

#### Common mistakes
- Applying without plan review
- Unpinned modules/providers
- Shared state across unrelated teams
- Ignoring `-/+` in plan

#### Interview follow-ups (with model answers)

**Q:** What would a bad plan look like?
**A:** Unexpected `-/+` replaces, destroys on databases, or creates duplicates—always attach plan to PR.

**Q:** How split blast radius?
**A:** Separate state per domain and environment; remote outputs between stacks.

**Q:** Common Azure gotcha?
**A:** Many SKU and name changes ForceNew—read plan symbols carefully.

#### Scenario probe

**Situation:** Platform apply related to `azurerm` vs `azapi` fails mid-run with partial resources created.

**Model answer:** azurerm stable resources; azapi for preview/new API properties not yet in azurerm. Stop applies, verify state lock, compare Activity Log to `terraform state list`, restore state version if needed, import orphans, re-plan from approved SHA—never blind re-apply.

---

### 32. Timeouts.

**Short answer:** Provider timeouts for long creates—AKS, SQL. Tune create/update/delete. Pin provider and module versions in CI. Review every plan for unexpected destroys before production apply.

#### What it is
Timeouts is a core Terraform concern for Azure platform teams supporting Java microservices on AKS. Interviewers want operational judgment: how this topic affects state safety, plan review, blast radius, and handoff to GitOps—not HCL trivia. You should connect infra changes to application deploy paths, on-call pain, and compliance gates.

#### How it works (internals)
For Timeouts, Terraform builds a dependency DAG from HCL references, refreshes state via Azure RM provider APIs, and computes create/update/destroy. Provider schemas mark immutable attributes as ForceNew—plan symbols `-/+` mean replace, not in-place tweak. CI runs fmt, validate, tflint, Checkov, and emits a saved plan; prod apply uses OIDC with least-privilege RBAC on target resource groups and state storage.

#### When to use / when NOT to use
Apply Timeouts patterns when platform ownership requires declarative, reviewable infrastructure. Avoid Terraform for fast-moving app Deployments better owned by Argo CD. Push back on permanent portal hotfixes—import or codify within SLA. Use separate state stacks so a mistake here cannot delete unrelated production data.

#### Production example
Platform squad changed timeouts via PR #4821: plan artifact attached, Checkov passed, QA apply from main, prod apply next day with SoD approver using the same `tfplan` and commit SHA. Java teams consumed outputs through `terraform_remote_state`—no duplicate subnets or ACR instances. Rollback was `git revert` plus plan review, not portal edits.

#### Common mistakes
- Applying without plan review
- Unpinned modules/providers
- Shared state across unrelated teams
- Ignoring `-/+` in plan

#### Interview follow-ups (with model answers)

**Q:** What would a bad plan look like?
**A:** Unexpected `-/+` replaces, destroys on databases, or creates duplicates—always attach plan to PR.

**Q:** How split blast radius?
**A:** Separate state per domain and environment; remote outputs between stacks.

**Q:** Common Azure gotcha?
**A:** Many SKU and name changes ForceNew—read plan symbols carefully.

#### Scenario probe

**Situation:** Platform apply related to Timeouts fails mid-run with partial resources created.

**Model answer:** Provider timeouts for long creates—AKS, SQL. Tune create/update/delete. Stop applies, verify state lock, compare Activity Log to `terraform state list`, restore state version if needed, import orphans, re-plan from approved SHA—never blind re-apply.

---

### 33. Targeting (`-target`).

**Short answer:** Emergency partial apply; skips drift elsewhere—never standard CI. Pin provider and module versions in CI. Review every plan for unexpected destroys before production apply.

#### What it is
Targeting (`-target`) is a core Terraform concern for Azure platform teams supporting Java microservices on AKS. Interviewers want operational judgment: how this topic affects state safety, plan review, blast radius, and handoff to GitOps—not HCL trivia. You should connect infra changes to application deploy paths, on-call pain, and compliance gates.

#### How it works (internals)
For Targeting (`-target`), Terraform builds a dependency DAG from HCL references, refreshes state via Azure RM provider APIs, and computes create/update/destroy. Provider schemas mark immutable attributes as ForceNew—plan symbols `-/+` mean replace, not in-place tweak. CI runs fmt, validate, tflint, Checkov, and emits a saved plan; prod apply uses OIDC with least-privilege RBAC on target resource groups and state storage.

#### When to use / when NOT to use
Apply Targeting (`-target`) patterns when platform ownership requires declarative, reviewable infrastructure. Avoid Terraform for fast-moving app Deployments better owned by Argo CD. Push back on permanent portal hotfixes—import or codify within SLA. Use separate state stacks so a mistake here cannot delete unrelated production data.

#### Production example
Platform squad changed targeting (`-target`) via PR #4821: plan artifact attached, Checkov passed, QA apply from main, prod apply next day with SoD approver using the same `tfplan` and commit SHA. Java teams consumed outputs through `terraform_remote_state`—no duplicate subnets or ACR instances. Rollback was `git revert` plus plan review, not portal edits.

#### Common mistakes
- Applying without plan review
- Unpinned modules/providers
- Shared state across unrelated teams
- Ignoring `-/+` in plan

#### Interview follow-ups (with model answers)

**Q:** What would a bad plan look like?
**A:** Unexpected `-/+` replaces, destroys on databases, or creates duplicates—always attach plan to PR.

**Q:** How split blast radius?
**A:** Separate state per domain and environment; remote outputs between stacks.

**Q:** Common Azure gotcha?
**A:** Many SKU and name changes ForceNew—read plan symbols carefully.

#### Scenario probe

**Situation:** Platform apply related to Targeting (`-target`) fails mid-run with partial resources created.

**Model answer:** Emergency partial apply; skips drift elsewhere—never standard CI. Stop applies, verify state lock, compare Activity Log to `terraform state list`, restore state version if needed, import orphans, re-plan from approved SHA—never blind re-apply.

---

### 34. Refresh skip.

**Short answer:** `-refresh=false` faster plan when state trusted; dangerous if cloud drifted. Pin provider and module versions in CI. Review every plan for unexpected destroys before production apply.

#### What it is
Refresh skip is a core Terraform concern for Azure platform teams supporting Java microservices on AKS. Interviewers want operational judgment: how this topic affects state safety, plan review, blast radius, and handoff to GitOps—not HCL trivia. You should connect infra changes to application deploy paths, on-call pain, and compliance gates.

#### How it works (internals)
For Refresh skip, Terraform builds a dependency DAG from HCL references, refreshes state via Azure RM provider APIs, and computes create/update/destroy. Provider schemas mark immutable attributes as ForceNew—plan symbols `-/+` mean replace, not in-place tweak. CI runs fmt, validate, tflint, Checkov, and emits a saved plan; prod apply uses OIDC with least-privilege RBAC on target resource groups and state storage.

#### When to use / when NOT to use
Apply Refresh skip patterns when platform ownership requires declarative, reviewable infrastructure. Avoid Terraform for fast-moving app Deployments better owned by Argo CD. Push back on permanent portal hotfixes—import or codify within SLA. Use separate state stacks so a mistake here cannot delete unrelated production data.

#### Production example
Platform squad changed refresh skip via PR #4821: plan artifact attached, Checkov passed, QA apply from main, prod apply next day with SoD approver using the same `tfplan` and commit SHA. Java teams consumed outputs through `terraform_remote_state`—no duplicate subnets or ACR instances. Rollback was `git revert` plus plan review, not portal edits.

#### Common mistakes
- Applying without plan review
- Unpinned modules/providers
- Shared state across unrelated teams
- Ignoring `-/+` in plan

#### Interview follow-ups (with model answers)

**Q:** What would a bad plan look like?
**A:** Unexpected `-/+` replaces, destroys on databases, or creates duplicates—always attach plan to PR.

**Q:** How split blast radius?
**A:** Separate state per domain and environment; remote outputs between stacks.

**Q:** Common Azure gotcha?
**A:** Many SKU and name changes ForceNew—read plan symbols carefully.

#### Scenario probe

**Situation:** Platform apply related to Refresh skip fails mid-run with partial resources created.

**Model answer:** `-refresh=false` faster plan when state trusted; dangerous if cloud drifted. Stop applies, verify state lock, compare Activity Log to `terraform state list`, restore state version if needed, import orphans, re-plan from approved SHA—never blind re-apply.

---

### 35. Upgrade TF and providers.

**Short answer:** Pin versions; upgrade in dev first. Read provider CHANGELOG for ForceNew. Pin provider and module versions in CI. Review every plan for unexpected destroys before production apply.

#### What it is
Upgrade TF and providers is a core Terraform concern for Azure platform teams supporting Java microservices on AKS. Interviewers want operational judgment: how this topic affects state safety, plan review, blast radius, and handoff to GitOps—not HCL trivia. You should connect infra changes to application deploy paths, on-call pain, and compliance gates.

#### How it works (internals)
For Upgrade TF and providers, Terraform builds a dependency DAG from HCL references, refreshes state via Azure RM provider APIs, and computes create/update/destroy. Provider schemas mark immutable attributes as ForceNew—plan symbols `-/+` mean replace, not in-place tweak. CI runs fmt, validate, tflint, Checkov, and emits a saved plan; prod apply uses OIDC with least-privilege RBAC on target resource groups and state storage.

#### When to use / when NOT to use
Apply Upgrade TF and providers patterns when platform ownership requires declarative, reviewable infrastructure. Avoid Terraform for fast-moving app Deployments better owned by Argo CD. Push back on permanent portal hotfixes—import or codify within SLA. Use separate state stacks so a mistake here cannot delete unrelated production data.

#### Production example
Platform squad changed upgrade tf and providers via PR #4821: plan artifact attached, Checkov passed, QA apply from main, prod apply next day with SoD approver using the same `tfplan` and commit SHA. Java teams consumed outputs through `terraform_remote_state`—no duplicate subnets or ACR instances. Rollback was `git revert` plus plan review, not portal edits.

#### Common mistakes
- Applying without plan review
- Unpinned modules/providers
- Shared state across unrelated teams
- Ignoring `-/+` in plan

#### Interview follow-ups (with model answers)

**Q:** What would a bad plan look like?
**A:** Unexpected `-/+` replaces, destroys on databases, or creates duplicates—always attach plan to PR.

**Q:** How split blast radius?
**A:** Separate state per domain and environment; remote outputs between stacks.

**Q:** Common Azure gotcha?
**A:** Many SKU and name changes ForceNew—read plan symbols carefully.

#### Scenario probe

**Situation:** Platform apply related to Upgrade TF and providers fails mid-run with partial resources created.

**Model answer:** Pin versions; upgrade in dev first. Read provider CHANGELOG for ForceNew. Stop applies, verify state lock, compare Activity Log to `terraform state list`, restore state version if needed, import orphans, re-plan from approved SHA—never blind re-apply.

---

### 36. Moving from portal to TF.

**Short answer:** Import in waves; align tags; freeze portal edits; CI drift detection. Pin provider and module versions in CI. Review every plan for unexpected destroys before production apply.

#### What it is
Moving from portal to TF is a core Terraform concern for Azure platform teams supporting Java microservices on AKS. Interviewers want operational judgment: how this topic affects state safety, plan review, blast radius, and handoff to GitOps—not HCL trivia. You should connect infra changes to application deploy paths, on-call pain, and compliance gates.

#### How it works (internals)
For Moving from portal to TF, Terraform builds a dependency DAG from HCL references, refreshes state via Azure RM provider APIs, and computes create/update/destroy. Provider schemas mark immutable attributes as ForceNew—plan symbols `-/+` mean replace, not in-place tweak. CI runs fmt, validate, tflint, Checkov, and emits a saved plan; prod apply uses OIDC with least-privilege RBAC on target resource groups and state storage.

#### When to use / when NOT to use
Apply Moving from portal to TF patterns when platform ownership requires declarative, reviewable infrastructure. Avoid Terraform for fast-moving app Deployments better owned by Argo CD. Push back on permanent portal hotfixes—import or codify within SLA. Use separate state stacks so a mistake here cannot delete unrelated production data.

#### Production example
Platform squad changed moving from portal to tf via PR #4821: plan artifact attached, Checkov passed, QA apply from main, prod apply next day with SoD approver using the same `tfplan` and commit SHA. Java teams consumed outputs through `terraform_remote_state`—no duplicate subnets or ACR instances. Rollback was `git revert` plus plan review, not portal edits.

#### Common mistakes
- Applying without plan review
- Unpinned modules/providers
- Shared state across unrelated teams
- Ignoring `-/+` in plan

#### Interview follow-ups (with model answers)

**Q:** What would a bad plan look like?
**A:** Unexpected `-/+` replaces, destroys on databases, or creates duplicates—always attach plan to PR.

**Q:** How split blast radius?
**A:** Separate state per domain and environment; remote outputs between stacks.

**Q:** Common Azure gotcha?
**A:** Many SKU and name changes ForceNew—read plan symbols carefully.

#### Scenario probe

**Situation:** Platform apply related to Moving from portal to TF fails mid-run with partial resources created.

**Model answer:** Import in waves; align tags; freeze portal edits; CI drift detection. Stop applies, verify state lock, compare Activity Log to `terraform state list`, restore state version if needed, import orphans, re-plan from approved SHA—never blind re-apply.

---

### 37. Naming conventions.

**Short answer:** Consistent `{org}-{env}-{service}-{region}` aids ops and state grep. Pin provider and module versions in CI. Review every plan for unexpected destroys before production apply.

#### What it is
Naming conventions is a core Terraform concern for Azure platform teams supporting Java microservices on AKS. Interviewers want operational judgment: how this topic affects state safety, plan review, blast radius, and handoff to GitOps—not HCL trivia. You should connect infra changes to application deploy paths, on-call pain, and compliance gates.

#### How it works (internals)
For Naming conventions, Terraform builds a dependency DAG from HCL references, refreshes state via Azure RM provider APIs, and computes create/update/destroy. Provider schemas mark immutable attributes as ForceNew—plan symbols `-/+` mean replace, not in-place tweak. CI runs fmt, validate, tflint, Checkov, and emits a saved plan; prod apply uses OIDC with least-privilege RBAC on target resource groups and state storage.

#### When to use / when NOT to use
Apply Naming conventions patterns when platform ownership requires declarative, reviewable infrastructure. Avoid Terraform for fast-moving app Deployments better owned by Argo CD. Push back on permanent portal hotfixes—import or codify within SLA. Use separate state stacks so a mistake here cannot delete unrelated production data.

#### Production example
Platform squad changed naming conventions via PR #4821: plan artifact attached, Checkov passed, QA apply from main, prod apply next day with SoD approver using the same `tfplan` and commit SHA. Java teams consumed outputs through `terraform_remote_state`—no duplicate subnets or ACR instances. Rollback was `git revert` plus plan review, not portal edits.

#### Common mistakes
- Applying without plan review
- Unpinned modules/providers
- Shared state across unrelated teams
- Ignoring `-/+` in plan

#### Interview follow-ups (with model answers)

**Q:** What would a bad plan look like?
**A:** Unexpected `-/+` replaces, destroys on databases, or creates duplicates—always attach plan to PR.

**Q:** How split blast radius?
**A:** Separate state per domain and environment; remote outputs between stacks.

**Q:** Common Azure gotcha?
**A:** Many SKU and name changes ForceNew—read plan symbols carefully.

#### Scenario probe

**Situation:** Platform apply related to Naming conventions fails mid-run with partial resources created.

**Model answer:** Consistent `{org}-{env}-{service}-{region}` aids ops and state grep. Stop applies, verify state lock, compare Activity Log to `terraform state list`, restore state version if needed, import orphans, re-plan from approved SHA—never blind re-apply.

---

### 38. `dynamic` blocks.

**Short answer:** Generate repeated nested blocks—NSG rules, backend pools—from maps. Pin provider and module versions in CI. Review every plan for unexpected destroys before production apply.

#### What it is
`dynamic` blocks is a core Terraform concern for Azure platform teams supporting Java microservices on AKS. Interviewers want operational judgment: how this topic affects state safety, plan review, blast radius, and handoff to GitOps—not HCL trivia. You should connect infra changes to application deploy paths, on-call pain, and compliance gates.

#### How it works (internals)
For `dynamic` blocks, Terraform builds a dependency DAG from HCL references, refreshes state via Azure RM provider APIs, and computes create/update/destroy. Provider schemas mark immutable attributes as ForceNew—plan symbols `-/+` mean replace, not in-place tweak. CI runs fmt, validate, tflint, Checkov, and emits a saved plan; prod apply uses OIDC with least-privilege RBAC on target resource groups and state storage.

#### When to use / when NOT to use
Apply `dynamic` blocks patterns when platform ownership requires declarative, reviewable infrastructure. Avoid Terraform for fast-moving app Deployments better owned by Argo CD. Push back on permanent portal hotfixes—import or codify within SLA. Use separate state stacks so a mistake here cannot delete unrelated production data.

#### Production example
Platform squad changed `dynamic` blocks via PR #4821: plan artifact attached, Checkov passed, QA apply from main, prod apply next day with SoD approver using the same `tfplan` and commit SHA. Java teams consumed outputs through `terraform_remote_state`—no duplicate subnets or ACR instances. Rollback was `git revert` plus plan review, not portal edits.

#### Common mistakes
- Applying without plan review
- Unpinned modules/providers
- Shared state across unrelated teams
- Ignoring `-/+` in plan

#### Interview follow-ups (with model answers)

**Q:** What would a bad plan look like?
**A:** Unexpected `-/+` replaces, destroys on databases, or creates duplicates—always attach plan to PR.

**Q:** How split blast radius?
**A:** Separate state per domain and environment; remote outputs between stacks.

**Q:** Common Azure gotcha?
**A:** Many SKU and name changes ForceNew—read plan symbols carefully.

#### Scenario probe

**Situation:** Platform apply related to `dynamic` blocks fails mid-run with partial resources created.

**Model answer:** Generate repeated nested blocks—NSG rules, backend pools—from maps. Stop applies, verify state lock, compare Activity Log to `terraform state list`, restore state version if needed, import orphans, re-plan from approved SHA—never blind re-apply.

---

### 39. `try`, `coalesce`, `nonsensitive`.

**Short answer:** Defensive expressions; nonsensitive only when redaction blocks outputs legitimately. Pin provider and module versions in CI. Review every plan for unexpected destroys before production apply.

#### What it is
`try`, `coalesce`, `nonsensitive` is a core Terraform concern for Azure platform teams supporting Java microservices on AKS. Interviewers want operational judgment: how this topic affects state safety, plan review, blast radius, and handoff to GitOps—not HCL trivia. You should connect infra changes to application deploy paths, on-call pain, and compliance gates.

#### How it works (internals)
For `try`, `coalesce`, `nonsensitive`, Terraform builds a dependency DAG from HCL references, refreshes state via Azure RM provider APIs, and computes create/update/destroy. Provider schemas mark immutable attributes as ForceNew—plan symbols `-/+` mean replace, not in-place tweak. CI runs fmt, validate, tflint, Checkov, and emits a saved plan; prod apply uses OIDC with least-privilege RBAC on target resource groups and state storage.

#### When to use / when NOT to use
Apply `try`, `coalesce`, `nonsensitive` patterns when platform ownership requires declarative, reviewable infrastructure. Avoid Terraform for fast-moving app Deployments better owned by Argo CD. Push back on permanent portal hotfixes—import or codify within SLA. Use separate state stacks so a mistake here cannot delete unrelated production data.

#### Production example
Platform squad changed `try`, `coalesce`, `nonsensitive` via PR #4821: plan artifact attached, Checkov passed, QA apply from main, prod apply next day with SoD approver using the same `tfplan` and commit SHA. Java teams consumed outputs through `terraform_remote_state`—no duplicate subnets or ACR instances. Rollback was `git revert` plus plan review, not portal edits.

#### Common mistakes
- Applying without plan review
- Unpinned modules/providers
- Shared state across unrelated teams
- Ignoring `-/+` in plan

#### Interview follow-ups (with model answers)

**Q:** What would a bad plan look like?
**A:** Unexpected `-/+` replaces, destroys on databases, or creates duplicates—always attach plan to PR.

**Q:** How split blast radius?
**A:** Separate state per domain and environment; remote outputs between stacks.

**Q:** Common Azure gotcha?
**A:** Many SKU and name changes ForceNew—read plan symbols carefully.

#### Scenario probe

**Situation:** Platform apply related to `try`, `coalesce`, `nonsensitive` fails mid-run with partial resources created.

**Model answer:** Defensive expressions; nonsensitive only when redaction blocks outputs legitimately. Stop applies, verify state lock, compare Activity Log to `terraform state list`, restore state version if needed, import orphans, re-plan from approved SHA—never blind re-apply.

---

### 40. Testing.

**Short answer:** terraform test (1.6+), terratest, plan-only CI on PR. Pin provider and module versions in CI. Review every plan for unexpected destroys before production apply.

#### What it is
Testing is a core Terraform concern for Azure platform teams supporting Java microservices on AKS. Interviewers want operational judgment: how this topic affects state safety, plan review, blast radius, and handoff to GitOps—not HCL trivia. You should connect infra changes to application deploy paths, on-call pain, and compliance gates.

#### How it works (internals)
For Testing, Terraform builds a dependency DAG from HCL references, refreshes state via Azure RM provider APIs, and computes create/update/destroy. Provider schemas mark immutable attributes as ForceNew—plan symbols `-/+` mean replace, not in-place tweak. CI runs fmt, validate, tflint, Checkov, and emits a saved plan; prod apply uses OIDC with least-privilege RBAC on target resource groups and state storage.

#### When to use / when NOT to use
Apply Testing patterns when platform ownership requires declarative, reviewable infrastructure. Avoid Terraform for fast-moving app Deployments better owned by Argo CD. Push back on permanent portal hotfixes—import or codify within SLA. Use separate state stacks so a mistake here cannot delete unrelated production data.

#### Production example
Platform squad changed testing via PR #4821: plan artifact attached, Checkov passed, QA apply from main, prod apply next day with SoD approver using the same `tfplan` and commit SHA. Java teams consumed outputs through `terraform_remote_state`—no duplicate subnets or ACR instances. Rollback was `git revert` plus plan review, not portal edits.

#### Common mistakes
- Applying without plan review
- Unpinned modules/providers
- Shared state across unrelated teams
- Ignoring `-/+` in plan

#### Interview follow-ups (with model answers)

**Q:** What would a bad plan look like?
**A:** Unexpected `-/+` replaces, destroys on databases, or creates duplicates—always attach plan to PR.

**Q:** How split blast radius?
**A:** Separate state per domain and environment; remote outputs between stacks.

**Q:** Common Azure gotcha?
**A:** Many SKU and name changes ForceNew—read plan symbols carefully.

#### Scenario probe

**Situation:** Platform apply related to Testing fails mid-run with partial resources created.

**Model answer:** terraform test (1.6+), terratest, plan-only CI on PR. Stop applies, verify state lock, compare Activity Log to `terraform state list`, restore state version if needed, import orphans, re-plan from approved SHA—never blind re-apply.

---

### 41. `tflint` / `tfsec` / `checkov`.

**Short answer:** Lint and security scan before plan—shift left. Pin provider and module versions in CI. Review every plan for unexpected destroys before production apply.

#### What it is
`tflint` / `tfsec` / `checkov` is a core Terraform concern for Azure platform teams supporting Java microservices on AKS. Interviewers want operational judgment: how this topic affects state safety, plan review, blast radius, and handoff to GitOps—not HCL trivia. You should connect infra changes to application deploy paths, on-call pain, and compliance gates.

#### How it works (internals)
For `tflint` / `tfsec` / `checkov`, Terraform builds a dependency DAG from HCL references, refreshes state via Azure RM provider APIs, and computes create/update/destroy. Provider schemas mark immutable attributes as ForceNew—plan symbols `-/+` mean replace, not in-place tweak. CI runs fmt, validate, tflint, Checkov, and emits a saved plan; prod apply uses OIDC with least-privilege RBAC on target resource groups and state storage.

#### When to use / when NOT to use
Apply `tflint` / `tfsec` / `checkov` patterns when platform ownership requires declarative, reviewable infrastructure. Avoid Terraform for fast-moving app Deployments better owned by Argo CD. Push back on permanent portal hotfixes—import or codify within SLA. Use separate state stacks so a mistake here cannot delete unrelated production data.

#### Production example
Platform squad changed `tflint` / `tfsec` / `checkov` via PR #4821: plan artifact attached, Checkov passed, QA apply from main, prod apply next day with SoD approver using the same `tfplan` and commit SHA. Java teams consumed outputs through `terraform_remote_state`—no duplicate subnets or ACR instances. Rollback was `git revert` plus plan review, not portal edits.

#### Common mistakes
- Applying without plan review
- Unpinned modules/providers
- Shared state across unrelated teams
- Ignoring `-/+` in plan

#### Interview follow-ups (with model answers)

**Q:** What would a bad plan look like?
**A:** Unexpected `-/+` replaces, destroys on databases, or creates duplicates—always attach plan to PR.

**Q:** How split blast radius?
**A:** Separate state per domain and environment; remote outputs between stacks.

**Q:** Common Azure gotcha?
**A:** Many SKU and name changes ForceNew—read plan symbols carefully.

#### Scenario probe

**Situation:** Platform apply related to `tflint` / `tfsec` / `checkov` fails mid-run with partial resources created.

**Model answer:** Lint and security scan before plan—shift left. Stop applies, verify state lock, compare Activity Log to `terraform state list`, restore state version if needed, import orphans, re-plan from approved SHA—never blind re-apply.

---

### 42. IAM for CI.

**Short answer:** OIDC federated credential to Azure—no SP secret in GitHub secrets long-term. Pin provider and module versions in CI. Review every plan for unexpected destroys before production apply.

#### What it is
IAM for CI is a core Terraform concern for Azure platform teams supporting Java microservices on AKS. Interviewers want operational judgment: how this topic affects state safety, plan review, blast radius, and handoff to GitOps—not HCL trivia. You should connect infra changes to application deploy paths, on-call pain, and compliance gates.

#### How it works (internals)
For IAM for CI, Terraform builds a dependency DAG from HCL references, refreshes state via Azure RM provider APIs, and computes create/update/destroy. Provider schemas mark immutable attributes as ForceNew—plan symbols `-/+` mean replace, not in-place tweak. CI runs fmt, validate, tflint, Checkov, and emits a saved plan; prod apply uses OIDC with least-privilege RBAC on target resource groups and state storage.

#### When to use / when NOT to use
Apply IAM for CI patterns when platform ownership requires declarative, reviewable infrastructure. Avoid Terraform for fast-moving app Deployments better owned by Argo CD. Push back on permanent portal hotfixes—import or codify within SLA. Use separate state stacks so a mistake here cannot delete unrelated production data.

#### Production example
Platform squad changed iam for ci via PR #4821: plan artifact attached, Checkov passed, QA apply from main, prod apply next day with SoD approver using the same `tfplan` and commit SHA. Java teams consumed outputs through `terraform_remote_state`—no duplicate subnets or ACR instances. Rollback was `git revert` plus plan review, not portal edits.

#### Common mistakes
- Applying without plan review
- Unpinned modules/providers
- Shared state across unrelated teams
- Ignoring `-/+` in plan

#### Interview follow-ups (with model answers)

**Q:** What would a bad plan look like?
**A:** Unexpected `-/+` replaces, destroys on databases, or creates duplicates—always attach plan to PR.

**Q:** How split blast radius?
**A:** Separate state per domain and environment; remote outputs between stacks.

**Q:** Common Azure gotcha?
**A:** Many SKU and name changes ForceNew—read plan symbols carefully.

#### Scenario probe

**Situation:** Platform apply related to IAM for CI fails mid-run with partial resources created.

**Model answer:** OIDC federated credential to Azure—no SP secret in GitHub secrets long-term. Stop applies, verify state lock, compare Activity Log to `terraform state list`, restore state version if needed, import orphans, re-plan from approved SHA—never blind re-apply.

---

### 43. Breaking a module: `moved` blocks.

**Short answer:** Refactor addresses without destroy—TF 1.1+ moved block. Pin provider and module versions in CI. Review every plan for unexpected destroys before production apply.

#### What it is
Breaking a module: `moved` blocks is a core Terraform concern for Azure platform teams supporting Java microservices on AKS. Interviewers want operational judgment: how this topic affects state safety, plan review, blast radius, and handoff to GitOps—not HCL trivia. You should connect infra changes to application deploy paths, on-call pain, and compliance gates.

#### How it works (internals)
For Breaking a module: `moved` blocks, Terraform builds a dependency DAG from HCL references, refreshes state via Azure RM provider APIs, and computes create/update/destroy. Provider schemas mark immutable attributes as ForceNew—plan symbols `-/+` mean replace, not in-place tweak. CI runs fmt, validate, tflint, Checkov, and emits a saved plan; prod apply uses OIDC with least-privilege RBAC on target resource groups and state storage.

#### When to use / when NOT to use
Apply Breaking a module: `moved` blocks patterns when platform ownership requires declarative, reviewable infrastructure. Avoid Terraform for fast-moving app Deployments better owned by Argo CD. Push back on permanent portal hotfixes—import or codify within SLA. Use separate state stacks so a mistake here cannot delete unrelated production data.

#### Production example
Platform squad changed breaking a module: `moved` blocks via PR #4821: plan artifact attached, Checkov passed, QA apply from main, prod apply next day with SoD approver using the same `tfplan` and commit SHA. Java teams consumed outputs through `terraform_remote_state`—no duplicate subnets or ACR instances. Rollback was `git revert` plus plan review, not portal edits.

#### Common mistakes
- Applying without plan review
- Unpinned modules/providers
- Shared state across unrelated teams
- Ignoring `-/+` in plan

#### Interview follow-ups (with model answers)

**Q:** What would a bad plan look like?
**A:** Unexpected `-/+` replaces, destroys on databases, or creates duplicates—always attach plan to PR.

**Q:** How split blast radius?
**A:** Separate state per domain and environment; remote outputs between stacks.

**Q:** Common Azure gotcha?
**A:** Many SKU and name changes ForceNew—read plan symbols carefully.

#### Scenario probe

**Situation:** Platform apply related to Breaking a module: `moved` blocks fails mid-run with partial resources created.

**Model answer:** Refactor addresses without destroy—TF 1.1+ moved block. Stop applies, verify state lock, compare Activity Log to `terraform state list`, restore state version if needed, import orphans, re-plan from approved SHA—never blind re-apply.

---

### 44. Destroy.

**Short answer:** Orderly teardown; prevent_destroy on prod DB. Know dependency destroy chain. Pin provider and module versions in CI. Review every plan for unexpected destroys before production apply.

#### What it is
Destroy is a core Terraform concern for Azure platform teams supporting Java microservices on AKS. Interviewers want operational judgment: how this topic affects state safety, plan review, blast radius, and handoff to GitOps—not HCL trivia. You should connect infra changes to application deploy paths, on-call pain, and compliance gates.

#### How it works (internals)
For Destroy, Terraform builds a dependency DAG from HCL references, refreshes state via Azure RM provider APIs, and computes create/update/destroy. Provider schemas mark immutable attributes as ForceNew—plan symbols `-/+` mean replace, not in-place tweak. CI runs fmt, validate, tflint, Checkov, and emits a saved plan; prod apply uses OIDC with least-privilege RBAC on target resource groups and state storage.

#### When to use / when NOT to use
Apply Destroy patterns when platform ownership requires declarative, reviewable infrastructure. Avoid Terraform for fast-moving app Deployments better owned by Argo CD. Push back on permanent portal hotfixes—import or codify within SLA. Use separate state stacks so a mistake here cannot delete unrelated production data.

#### Production example
Platform squad changed destroy via PR #4821: plan artifact attached, Checkov passed, QA apply from main, prod apply next day with SoD approver using the same `tfplan` and commit SHA. Java teams consumed outputs through `terraform_remote_state`—no duplicate subnets or ACR instances. Rollback was `git revert` plus plan review, not portal edits.

#### Common mistakes
- Applying without plan review
- Unpinned modules/providers
- Shared state across unrelated teams
- Ignoring `-/+` in plan

#### Interview follow-ups (with model answers)

**Q:** What would a bad plan look like?
**A:** Unexpected `-/+` replaces, destroys on databases, or creates duplicates—always attach plan to PR.

**Q:** How split blast radius?
**A:** Separate state per domain and environment; remote outputs between stacks.

**Q:** Common Azure gotcha?
**A:** Many SKU and name changes ForceNew—read plan symbols carefully.

#### Scenario probe

**Situation:** Platform apply related to Destroy fails mid-run with partial resources created.

**Model answer:** Orderly teardown; prevent_destroy on prod DB. Know dependency destroy chain. Stop applies, verify state lock, compare Activity Log to `terraform state list`, restore state version if needed, import orphans, re-plan from approved SHA—never blind re-apply.

---

### 45. Partial apply failure.

**Short answer:** Some resources created; state updated. Re-plan; taint or import as needed. Pin provider and module versions in CI. Review every plan for unexpected destroys before production apply.

#### What it is
Partial apply failure is a core Terraform concern for Azure platform teams supporting Java microservices on AKS. Interviewers want operational judgment: how this topic affects state safety, plan review, blast radius, and handoff to GitOps—not HCL trivia. You should connect infra changes to application deploy paths, on-call pain, and compliance gates.

#### How it works (internals)
For Partial apply failure, Terraform builds a dependency DAG from HCL references, refreshes state via Azure RM provider APIs, and computes create/update/destroy. Provider schemas mark immutable attributes as ForceNew—plan symbols `-/+` mean replace, not in-place tweak. CI runs fmt, validate, tflint, Checkov, and emits a saved plan; prod apply uses OIDC with least-privilege RBAC on target resource groups and state storage.

#### When to use / when NOT to use
Apply Partial apply failure patterns when platform ownership requires declarative, reviewable infrastructure. Avoid Terraform for fast-moving app Deployments better owned by Argo CD. Push back on permanent portal hotfixes—import or codify within SLA. Use separate state stacks so a mistake here cannot delete unrelated production data.

#### Production example
Platform squad changed partial apply failure via PR #4821: plan artifact attached, Checkov passed, QA apply from main, prod apply next day with SoD approver using the same `tfplan` and commit SHA. Java teams consumed outputs through `terraform_remote_state`—no duplicate subnets or ACR instances. Rollback was `git revert` plus plan review, not portal edits.

#### Common mistakes
- Applying without plan review
- Unpinned modules/providers
- Shared state across unrelated teams
- Ignoring `-/+` in plan

#### Interview follow-ups (with model answers)

**Q:** What would a bad plan look like?
**A:** Unexpected `-/+` replaces, destroys on databases, or creates duplicates—always attach plan to PR.

**Q:** How split blast radius?
**A:** Separate state per domain and environment; remote outputs between stacks.

**Q:** Common Azure gotcha?
**A:** Many SKU and name changes ForceNew—read plan symbols carefully.

#### Scenario probe

**Situation:** Platform apply related to Partial apply failure fails mid-run with partial resources created.

**Model answer:** Some resources created; state updated. Re-plan; taint or import as needed. Stop applies, verify state lock, compare Activity Log to `terraform state list`, restore state version if needed, import orphans, re-plan from approved SHA—never blind re-apply.

---

### 46. Secrets rotation.

**Short answer:** Rotate in Key Vault; update TF vars; rolling restart apps—avoid secrets in TF state plaintext.

#### What it is
Secrets rotation is a core Terraform concern for Azure platform teams supporting Java microservices on AKS. Interviewers want operational judgment: how this topic affects state safety, plan review, blast radius, and handoff to GitOps—not HCL trivia. You should connect infra changes to application deploy paths, on-call pain, and compliance gates.

#### How it works (internals)
For Secrets rotation, Terraform builds a dependency DAG from HCL references, refreshes state via Azure RM provider APIs, and computes create/update/destroy. Provider schemas mark immutable attributes as ForceNew—plan symbols `-/+` mean replace, not in-place tweak. CI runs fmt, validate, tflint, Checkov, and emits a saved plan; prod apply uses OIDC with least-privilege RBAC on target resource groups and state storage.

#### When to use / when NOT to use
Apply Secrets rotation patterns when platform ownership requires declarative, reviewable infrastructure. Avoid Terraform for fast-moving app Deployments better owned by Argo CD. Push back on permanent portal hotfixes—import or codify within SLA. Use separate state stacks so a mistake here cannot delete unrelated production data.

#### Production example
Platform squad changed secrets rotation via PR #4821: plan artifact attached, Checkov passed, QA apply from main, prod apply next day with SoD approver using the same `tfplan` and commit SHA. Java teams consumed outputs through `terraform_remote_state`—no duplicate subnets or ACR instances. Rollback was `git revert` plus plan review, not portal edits.

#### Common mistakes
- Applying without plan review
- Unpinned modules/providers
- Shared state across unrelated teams
- Ignoring `-/+` in plan

#### Interview follow-ups (with model answers)

**Q:** What would a bad plan look like?
**A:** Unexpected `-/+` replaces, destroys on databases, or creates duplicates—always attach plan to PR.

**Q:** How split blast radius?
**A:** Separate state per domain and environment; remote outputs between stacks.

**Q:** Common Azure gotcha?
**A:** Many SKU and name changes ForceNew—read plan symbols carefully.

#### Scenario probe

**Situation:** Platform apply related to Secrets rotation fails mid-run with partial resources created.

**Model answer:** Rotate in Key Vault; update TF vars; rolling restart apps—avoid secrets in TF state plaintext. Stop applies, verify state lock, compare Activity Log to `terraform state list`, restore state version if needed, import orphans, re-plan from approved SHA—never blind re-apply.

---

### 47. Multi-region.

**Short answer:** Provider aliases, separate modules, traffic manager/front door in TF. Pin provider and module versions in CI. Review every plan for unexpected destroys before production apply.

#### What it is
Multi-region is a core Terraform concern for Azure platform teams supporting Java microservices on AKS. Interviewers want operational judgment: how this topic affects state safety, plan review, blast radius, and handoff to GitOps—not HCL trivia. You should connect infra changes to application deploy paths, on-call pain, and compliance gates.

#### How it works (internals)
For Multi-region, Terraform builds a dependency DAG from HCL references, refreshes state via Azure RM provider APIs, and computes create/update/destroy. Provider schemas mark immutable attributes as ForceNew—plan symbols `-/+` mean replace, not in-place tweak. CI runs fmt, validate, tflint, Checkov, and emits a saved plan; prod apply uses OIDC with least-privilege RBAC on target resource groups and state storage.

#### When to use / when NOT to use
Apply Multi-region patterns when platform ownership requires declarative, reviewable infrastructure. Avoid Terraform for fast-moving app Deployments better owned by Argo CD. Push back on permanent portal hotfixes—import or codify within SLA. Use separate state stacks so a mistake here cannot delete unrelated production data.

#### Production example
Platform squad changed multi-region via PR #4821: plan artifact attached, Checkov passed, QA apply from main, prod apply next day with SoD approver using the same `tfplan` and commit SHA. Java teams consumed outputs through `terraform_remote_state`—no duplicate subnets or ACR instances. Rollback was `git revert` plus plan review, not portal edits.

#### Common mistakes
- Applying without plan review
- Unpinned modules/providers
- Shared state across unrelated teams
- Ignoring `-/+` in plan

#### Interview follow-ups (with model answers)

**Q:** What would a bad plan look like?
**A:** Unexpected `-/+` replaces, destroys on databases, or creates duplicates—always attach plan to PR.

**Q:** How split blast radius?
**A:** Separate state per domain and environment; remote outputs between stacks.

**Q:** Common Azure gotcha?
**A:** Many SKU and name changes ForceNew—read plan symbols carefully.

#### Scenario probe

**Situation:** Platform apply related to Multi-region fails mid-run with partial resources created.

**Model answer:** Provider aliases, separate modules, traffic manager/front door in TF. Stop applies, verify state lock, compare Activity Log to `terraform state list`, restore state version if needed, import orphans, re-plan from approved SHA—never blind re-apply.

---

### 48. Cost in TF.

**Short answer:** Tags for cost allocation; right-size SKUs in review; Infracost in CI optional. Pin provider and module versions in CI. Review every plan for unexpected destroys before production apply.

#### What it is
Cost in TF is a core Terraform concern for Azure platform teams supporting Java microservices on AKS. Interviewers want operational judgment: how this topic affects state safety, plan review, blast radius, and handoff to GitOps—not HCL trivia. You should connect infra changes to application deploy paths, on-call pain, and compliance gates.

#### How it works (internals)
For Cost in TF, Terraform builds a dependency DAG from HCL references, refreshes state via Azure RM provider APIs, and computes create/update/destroy. Provider schemas mark immutable attributes as ForceNew—plan symbols `-/+` mean replace, not in-place tweak. CI runs fmt, validate, tflint, Checkov, and emits a saved plan; prod apply uses OIDC with least-privilege RBAC on target resource groups and state storage.

#### When to use / when NOT to use
Apply Cost in TF patterns when platform ownership requires declarative, reviewable infrastructure. Avoid Terraform for fast-moving app Deployments better owned by Argo CD. Push back on permanent portal hotfixes—import or codify within SLA. Use separate state stacks so a mistake here cannot delete unrelated production data.

#### Production example
Platform squad changed cost in tf via PR #4821: plan artifact attached, Checkov passed, QA apply from main, prod apply next day with SoD approver using the same `tfplan` and commit SHA. Java teams consumed outputs through `terraform_remote_state`—no duplicate subnets or ACR instances. Rollback was `git revert` plus plan review, not portal edits.

#### Common mistakes
- Applying without plan review
- Unpinned modules/providers
- Shared state across unrelated teams
- Ignoring `-/+` in plan

#### Interview follow-ups (with model answers)

**Q:** What would a bad plan look like?
**A:** Unexpected `-/+` replaces, destroys on databases, or creates duplicates—always attach plan to PR.

**Q:** How split blast radius?
**A:** Separate state per domain and environment; remote outputs between stacks.

**Q:** Common Azure gotcha?
**A:** Many SKU and name changes ForceNew—read plan symbols carefully.

#### Scenario probe

**Situation:** Platform apply related to Cost in TF fails mid-run with partial resources created.

**Model answer:** Tags for cost allocation; right-size SKUs in review; Infracost in CI optional. Stop applies, verify state lock, compare Activity Log to `terraform state list`, restore state version if needed, import orphans, re-plan from approved SHA—never blind re-apply.

---

### 49. Common Azure gotchas.

**Short answer:** features{} block, globally unique storage names, AKS subnet sizing, SQL PE vs firewall. Pin provider and module versions in CI. Review every plan for unexpected destroys before production apply.

#### What it is
Common Azure gotchas is a core Terraform concern for Azure platform teams supporting Java microservices on AKS. Interviewers want operational judgment: how this topic affects state safety, plan review, blast radius, and handoff to GitOps—not HCL trivia. You should connect infra changes to application deploy paths, on-call pain, and compliance gates.

#### How it works (internals)
For Common Azure gotchas, Terraform builds a dependency DAG from HCL references, refreshes state via Azure RM provider APIs, and computes create/update/destroy. Provider schemas mark immutable attributes as ForceNew—plan symbols `-/+` mean replace, not in-place tweak. CI runs fmt, validate, tflint, Checkov, and emits a saved plan; prod apply uses OIDC with least-privilege RBAC on target resource groups and state storage.

#### When to use / when NOT to use
Apply Common Azure gotchas patterns when platform ownership requires declarative, reviewable infrastructure. Avoid Terraform for fast-moving app Deployments better owned by Argo CD. Push back on permanent portal hotfixes—import or codify within SLA. Use separate state stacks so a mistake here cannot delete unrelated production data.

#### Production example
Platform squad changed common azure gotchas via PR #4821: plan artifact attached, Checkov passed, QA apply from main, prod apply next day with SoD approver using the same `tfplan` and commit SHA. Java teams consumed outputs through `terraform_remote_state`—no duplicate subnets or ACR instances. Rollback was `git revert` plus plan review, not portal edits.

#### Common mistakes
- Applying without plan review
- Unpinned modules/providers
- Shared state across unrelated teams
- Ignoring `-/+` in plan

#### Interview follow-ups (with model answers)

**Q:** What would a bad plan look like?
**A:** Unexpected `-/+` replaces, destroys on databases, or creates duplicates—always attach plan to PR.

**Q:** How split blast radius?
**A:** Separate state per domain and environment; remote outputs between stacks.

**Q:** Common Azure gotcha?
**A:** Many SKU and name changes ForceNew—read plan symbols carefully.

#### Scenario probe

**Situation:** Platform apply related to Common Azure gotchas fails mid-run with partial resources created.

**Model answer:** features{} block, globally unique storage names, AKS subnet sizing, SQL PE vs firewall. Stop applies, verify state lock, compare Activity Log to `terraform state list`, restore state version if needed, import orphans, re-plan from approved SHA—never blind re-apply.

---

### 50. Senior TF workflow.

**Short answer:** PR → fmt/validate/lint/scan → plan artifact → human review → apply same plan → GitOps for apps.

#### What it is
Senior TF workflow is a core Terraform concern for Azure platform teams supporting Java microservices on AKS. Interviewers want operational judgment: how this topic affects state safety, plan review, blast radius, and handoff to GitOps—not HCL trivia. You should connect infra changes to application deploy paths, on-call pain, and compliance gates.

#### How it works (internals)
For Senior TF workflow, Terraform builds a dependency DAG from HCL references, refreshes state via Azure RM provider APIs, and computes create/update/destroy. Provider schemas mark immutable attributes as ForceNew—plan symbols `-/+` mean replace, not in-place tweak. CI runs fmt, validate, tflint, Checkov, and emits a saved plan; prod apply uses OIDC with least-privilege RBAC on target resource groups and state storage.

#### When to use / when NOT to use
Apply Senior TF workflow patterns when platform ownership requires declarative, reviewable infrastructure. Avoid Terraform for fast-moving app Deployments better owned by Argo CD. Push back on permanent portal hotfixes—import or codify within SLA. Use separate state stacks so a mistake here cannot delete unrelated production data.

#### Production example
Platform squad changed senior tf workflow via PR #4821: plan artifact attached, Checkov passed, QA apply from main, prod apply next day with SoD approver using the same `tfplan` and commit SHA. Java teams consumed outputs through `terraform_remote_state`—no duplicate subnets or ACR instances. Rollback was `git revert` plus plan review, not portal edits.

#### Common mistakes
- Applying without plan review
- Unpinned modules/providers
- Shared state across unrelated teams
- Ignoring `-/+` in plan

#### Interview follow-ups (with model answers)

**Q:** What would a bad plan look like?
**A:** Unexpected `-/+` replaces, destroys on databases, or creates duplicates—always attach plan to PR.

**Q:** How split blast radius?
**A:** Separate state per domain and environment; remote outputs between stacks.

**Q:** Common Azure gotcha?
**A:** Many SKU and name changes ForceNew—read plan symbols carefully.

#### Scenario probe

**Situation:** Platform apply related to Senior TF workflow fails mid-run with partial resources created.

**Model answer:** PR → fmt/validate/lint/scan → plan artifact → human review → apply same plan → GitOps for apps. Stop applies, verify state lock, compare Activity Log to `terraform state list`, restore state version if needed, import orphans, re-plan from approved SHA—never blind re-apply.

---

### 51. OpenTofu vs Terraform — fork implications for teams.

**Short answer:** OpenTofu is the Linux Foundation fork of Terraform after BSL license change. Functionally similar for most HCL; provider ecosystem largely shared. Teams must pick registry, support, and long-term license posture—avoid mixed CLI in same pipeline without pinning. Pin provider and module versions in CI. Review every plan for unexpected destroys before production apply.

#### What it is
OpenTofu maintains MPL-2.0 fork with community governance. HashiCorp Terraform moved to BSL for >=1.6. State files and HCL largely compatible; provider sources may differ (`opentofu/` registry mirrors).

#### How it works (internals)
CLI commands match for plan/apply. Provider version constraints same syntax. Enterprise support differs—HCPT vs community/Spacelift variants for OpenTofu.

#### When to use / when NOT to use
Greenfield without HC enterprise may pick OpenTofu for license clarity. Existing HC contracts may stay on Terraform. Do not mix apply tools on same state without testing.

#### Production example
Platform team standardizes on OpenTofu 1.8 in CI with `tofu init`; module sources pinned; legal reviewed BSL vs MPL for vendor risk.

#### Common mistakes
- Different CLI on laptop vs CI
- Unpinned provider source flip
- Ignoring license audit for SaaS resale

#### Interview follow-ups (with model answers)

**Q:** What would a bad plan look like?
**A:** Unexpected `-/+` replaces, destroys on databases, or creates duplicates—always attach plan to PR.

**Q:** How split blast radius?
**A:** Separate state per domain and environment; remote outputs between stacks.

**Q:** Common Azure gotcha?
**A:** Many SKU and name changes ForceNew—read plan symbols carefully.

#### Scenario probe

Legal asks whether new repos must use OpenTofu while legacy stays Terraform 1.5.

Define sunset timeline, forbid new BSL-only features on legacy, single CI image per repo, document `terraform` vs `tofu` binary in runbooks. Pilot OpenTofu on network stack with plan diff zero before mandating.

---

### 52. `import` blocks (Terraform 1.5+) vs `terraform import` CLI.

**Short answer:** Import blocks declare imports in HCL—reviewable in PR, repeatable across envs. CLI import is one-off binding. Prefer blocks for brownfield adoption at scale. Pin provider and module versions in CI. Review every plan for unexpected destroys before production apply.

#### What it is
Import block maps resource address to ID in config; plan shows import action. CLI `terraform import addr id` mutates state immediately without PR review of import mapping.

#### How it works (internals)
Plan with import blocks shows Import in resource_changes. Multiple imports in one apply. CLI better for emergency single resource under fire.

#### When to use / when NOT to use
Brownfield migration waves use import blocks in Git. CLI for break-glass only. Always follow with plan showing no unexpected changes.

#### Production example
Fifty existing RGs imported via import blocks in module; CI plan-only on PR proves no drift before apply.

#### Common mistakes
- Import without matching config shape
- CLI import not committed
- Wrong resource ID format

#### Interview follow-ups (with model answers)

**Q:** What would a bad plan look like?
**A:** Unexpected `-/+` replaces, destroys on databases, or creates duplicates—always attach plan to PR.

**Q:** How split blast radius?
**A:** Separate state per domain and environment; remote outputs between stacks.

**Q:** Common Azure gotcha?
**A:** Many SKU and name changes ForceNew—read plan symbols carefully.

#### Scenario probe

Migration PR adds import blocks but plan wants to change tags on all imported RGs.

Align config tags with live before apply or use lifecycle ignore_changes temporarily with ticket to normalize tags via Policy.

---

### 53. Terraform test framework (`terraform test`) with mock providers.

**Short answer:** Native `terraform test` runs assertions on plan/apply with mock providers—fast module tests without cloud cost. Complements terratest integration tests.

#### What it is
Tests in `.tftest.hcl` reference modules, run plan/apply against mocks, assert outputs and resource counts. Mock providers simulate API responses.

#### How it works (internals)
Run in CI on every module PR. Mock for unit-level; real cloud sandbox for integration sparingly.

#### When to use / when NOT to use
Module authors adopt tests before publishing semver tags. Do not mock away ForceNew behavior you rely on—add one real plan job.

#### Production example
Network module tests assert subnet count and CIDR outputs with azurerm mock; fails PR when output rename breaks contract.

#### Common mistakes
- No tests on shared module used by 20 stacks
- Mock too optimistic vs real Azure errors
- Testing only validate not plan

#### Interview follow-ups (with model answers)

**Q:** What would a bad plan look like?
**A:** Unexpected `-/+` replaces, destroys on databases, or creates duplicates—always attach plan to PR.

**Q:** How split blast radius?
**A:** Separate state per domain and environment; remote outputs between stacks.

**Q:** Common Azure gotcha?
**A:** Many SKU and name changes ForceNew—read plan symbols carefully.

#### Scenario probe

Module refactor passes validate but breaks consumers' remote state outputs.

Add test asserting output keys and types; semver major when removing outputs; consumer contract tests in platform repo.

---

### 54. CDK for Terraform (CDKTF) — when teams pick it.

**Short answer:** CDKTF generates Terraform JSON from TypeScript/Python/Java—appeals when teams want IDE typing and constructs over raw HCL. Trade-off: another abstraction layer and synth/debug complexity.

#### What it is
CDK for Terraform lets developers define infrastructure in familiar languages; `cdktf synth` emits JSON/HCL consumed by the normal TF/OpenTofu workflow.

#### How it works (internals)
Developers write CDK constructs; synth emits TF config; apply still TF/OpenTofu CLI. Shares provider ecosystem and state backends.

#### When to use / when NOT to use
Pick when platform team is already TypeScript-heavy and needs reusable OOP constructs. Avoid when ops team only knows HCL—onboarding cost.

#### Production example
Platform team ships VPC construct library in TS; services instantiate with props; CI synths and plans.

#### Common mistakes
- Synth drift not committed
- Debugging generated JSON
- Junior cannot read HCL plan output

#### Interview follow-ups (with model answers)

**Q:** What would a bad plan look like?
**A:** Unexpected `-/+` replaces, destroys on databases, or creates duplicates—always attach plan to PR.

**Q:** How split blast radius?
**A:** Separate state per domain and environment; remote outputs between stacks.

**Q:** Common Azure gotcha?
**A:** Many SKU and name changes ForceNew—read plan symbols carefully.

#### Scenario probe

Java team wants CDKTF but on-call only knows `terraform plan` on HCL.

Require synth in CI committing JSON or plan from synth artifact; train on-call on reading plan not TS; keep break-glass HCL modules for critical paths.

---

### 55. `check` blocks and postconditions for guardrails.

**Short answer:** Check blocks and resource postconditions fail apply when invariants break—e.g., storage must have encryption, public access false. Guardrails as code beyond external policy scanners. Pin provider and module versions in CI. Review every plan for unexpected destroys before production apply.

#### What it is
Terraform 1.5+ check blocks and resource-level postconditions assert expressions after plan/apply phases, turning module contracts into hard failures.

#### How it works (internals)
Postconditions on resources assert expressions after apply. Check blocks validate broader conditions. Fail fast instead of silent misconfig.

#### When to use / when NOT to use
Add postconditions on security-sensitive resources. Combine with Checkov for defense in depth—not a replacement.

#### Production example
Postcondition on storage account asserts `public_network_access_enabled == false`; apply fails if module regression opens public access.

#### Common mistakes
- Postcondition too strict blocks legit dev env
- Checks not run in plan-only CI
- Duplicating Checkov without value

#### Interview follow-ups (with model answers)

**Q:** What would a bad plan look like?
**A:** Unexpected `-/+` replaces, destroys on databases, or creates duplicates—always attach plan to PR.

**Q:** How split blast radius?
**A:** Separate state per domain and environment; remote outputs between stacks.

**Q:** Common Azure gotcha?
**A:** Many SKU and name changes ForceNew—read plan symbols carefully.

#### Scenario probe

Module upgrade passes Checkov but disables SQL auditing via default change.

Add postcondition asserting auditing enabled; catches provider default drift Checkov rule missed.

---

## Scenario-based interview drills

### S1. State loss scare during Blob outage

**Situation:** Platform on-call gets alert: state blob unavailable mid-apply. Partial resources created in Azure. Second engineer wants to `terraform apply` from laptop with local state.

**What they're testing:** State recovery, backup discipline, never apply without remote state alignment.

**How to structure your answer:** Stop → verify backup/version → restore state → plan → reconcile partial resources → communicate.

**Model answer:** I'd halt all applies immediately and confirm no second apply is running. Pull previous state version from Blob versioning or backup vault—never accept local state from a laptop. Restore to known good version, run plan against the exact Git commit used for failed apply. Expect to see resources to import or refresh if partial creates happened. Use Azure Activity Log to list creates during outage window. Import or destroy orphans deliberately—never blind apply. Post-incident: test restore quarterly, alert on state blob availability, require plan artifact approval.

**Common weak answers:** Re-init with empty local state and apply (recreate everything). Force-unlock without checking leases.

**Follow-up probes (with answers):**

**Q:** How prove state backup good?
**A:** Quarterly restore drill to scratch storage, plan against prod code expecting no changes.

**Q:** Partial apply signs?
**A:** Resources in Azure not in state—plan wants create; duplicates if re-created.

---
### S2. Module pin drift breaks prod plan

**Situation:** QA passed with module v2.1.0. Prod plan fails: module v2.2.0 pulled due to loose constraint `~> 2.1` and wants to replace AKS node pool.

**What they're testing:** Semver constraints, prod pin strategy, plan review.

**How to structure your answer:** Identify version diff → read changelog → pin exact ref → test in QA → promote.

**Model answer:** Loose pessimistic constraint allowed patch that included ForceNew. I'd pin exact Git ref or registry version in prod tfvars, re-run QA plan on same SHA, attach diff to change ticket. For emergency, hold prod apply until QA replays with exact prod pins. Long-term: Renovate bot PRs with plan artifacts; prod uses exact pins only.

**Common weak answers:** Allow `~>` on prod modules without CI plan on Renovate PRs.

**Follow-up probes (with answers):**

**Q:** Pin strategy?
**A:** Exact version in prod; ranges only in dev with automated plan CI.

**Q:** Rollback module?
**A:** Revert ref in Git; plan may still `-/+` if forward change destructive—have backup.

---
### S3. Import brownfield without change freeze

**Situation:** Team imports 200 resources while ops still edit tags in portal. Every plan shows hundreds of tag diffs.

**What they're testing:** Import process, change freeze, drift detection.

**How to structure your answer:** Freeze portal → import blocks PR → plan zero unexpected → enable drift cron.

**Model answer:** Declare change freeze during migration window. Import blocks in batches by RG. Plan must show import only or expected in-place tag alignment—if mass diff, stop and sync config to reality or Azure Policy. After cutover, cron plan alerts on portal drift.

**Common weak answers:** Import during business hours without freeze; apply all tag reversions blindly.

**Follow-up probes (with answers):**

**Q:** Batch size?
**A:** One RG or subscription slice per PR for reviewable plans.

**Q:** Communication?
**A:** Tell ops ticket required for any portal change during migration.

---
### S4. Open NSG from Checkov bypass

**Situation:** Checkov skipped in emergency PR; apply opens SSH 0.0.0.0/0 on bastion NSG.

**What they're testing:** Policy gates, emergency process, postconditions.

**How to structure your answer:** Detect → rollback NSG → fix pipeline → add check block.

**Model answer:** Revert NSG via TF or portal temporarily with ticket, restore Checkov gate, add postcondition denying 0.0.0.0/0 on 22. Break-glass PR still runs read-only plan and requires second approver. Incident review: why skip was allowed.

**Common weak answers:** Leave NSG open because prod is down; no ticket.

**Follow-up probes (with answers):**

**Q:** Break-glass?
**A:** Time-boxed skip with mandatory follow-up PR restoring gates.

**Q:** Detect outside CI?
**A:** Azure Policy deny assignment as backstop.

---
### S5. Dual Helm and TF kubernetes fight

**Situation:** Argo CD and TF both manage same Deployment image tag; deploy ping-pongs every sync.

**What they're testing:** Ownership boundaries, GitOps vs TF.

**How to structure your answer:** Map controllers → pick single owner → remove duplicate resource → document.

**Model answer:** Remove Deployment from TF; keep TF for cluster infra. Argo owns image from CI digest. If TF needed bootstrap, one-time create then remove from TF code or use ignore_changes with exit plan. Add linter rule forbidding kubernetes_deployment in app TF dirs.

**Common weak answers:** Add lifecycle ignore_changes on image forever without removing TF resource.

**Follow-up probes (with answers):**

**Q:** Helm provider in TF?
**A:** Platform addons only with documented exceptions.

**Q:** Detect?
**A:** Argo OutOfSync oscillation metric; TF plan every hour changing same field.

---
### S6. Workspace collision in shared CI

**Situation:** Dev and QA CI jobs share workspace name `default` on same backend key—state corruption risk.

**What they're testing:** Workspace vs directory isolation.

**How to structure your answer:** Separate keys → RBAC → pipeline env matrix.

**Model answer:** Move to directory-per-env with distinct backend keys `dev/network.tfstate` and `qa/network.tfstate`. Remove workspace reliance in CI. Add precondition that var.env matches backend key suffix. Test concurrent plans do not lock each other incorrectly.

**Common weak answers:** Use workspaces for prod and non-prod without RBAC separation.

**Follow-up probes (with answers):**

**Q:** When workspaces OK?
**A:** Solo dev or identical low-risk sandboxes—not prod/QA sharing.

**Q:** Lock scope?
**A:** Per state key; separate keys mean separate locks.

---
### S7. SQL firewall opened by drift

**Situation:** Plan cron detects SQL firewall rule added manually allowing 0.0.0.0/0.

**What they're testing:** Drift detection, SQL networking best practice.

**How to structure your answer:** Alert → confirm PE path → remove rule via apply → audit.

**Model answer:** Confirm private endpoint is production path; apply removes rogue firewall rule; investigate who changed portal; enable Policy deny on public SQL access. TF should use private endpoint only in prod module.

**Common weak answers:** Ignore because app works; leave public firewall.

**Follow-up probes (with answers):**

**Q:** PE vs firewall?
**A:** Prod Java services should use PE; firewall for break-glass only with IP allowlist.

**Q:** Detect quickly?
**A:** Daily plan cron exit code 2 to Slack.

---
### S8. count index shuffle destroys QA databases

**Situation:** Adding item at start of counted list reindexes; plan destroys all SQL databases.

**What they're testing:** count vs for_each footgun.

**How to structure your answer:** Refactor to for_each keys → moved block → plan no destroy.

**Model answer:** Stop apply. Refactor to for_each with stable business keys (db name). Use moved blocks from old indices. Plan must show zero destroys. Add code review rule: no new count for named persistent resources.

**Common weak answers:** Proceed because QA can be recreated without checking prod uses same module.

**Follow-up probes (with answers):**

**Q:** Rule?
**A:** Persistent named resources always for_each map keyed by name.

**Q:** moved block?
**A:** Maps old `count.index` address to new for_each key.

---
### S9. OIDC misconfiguration blocks Friday apply

**Situation:** GitHub Actions plan OK; apply fails Azure auth after federated credential subject mismatch.

**What they're testing:** CI IAM, OIDC setup.

**How to structure your answer:** Compare subject claim → fix federated credential → least privilege.

**Model answer:** Apply job uses environment protection; subject must include repo and environment. Fix App Registration federated credential pattern `repo:org/repo:environment:prod`. Scope role to RG not subscription. Re-run apply without bypassing plan artifact.

**Common weak answers:** Use SP secret instead because faster—reintroduces secret sprawl.

**Follow-up probes (with answers):**

**Q:** Least privilege?
**A:** Contributor on target RG plus state storage, not Owner on sub.

**Q:** Plan vs apply identity?
**A:** Same OIDC cred; apply role may be narrower with custom role.

---
### S10. Senior plan review catches `-/+` AKS

**Situation:** Junior attaches plan with `-/+` on AKS default node pool for VM size change.

**What they're testing:** Plan literacy, senior review, blast radius.

**How to structure your answer:** Read symbols → assess downtime → cordon/drain strategy → approve or reject.

**Model answer:** I'd reject immediate apply. `-/+` on node pool evicts all pods—need maintenance window, surge pool, or blue-green node pool strategy. Confirm Kafka/Spring PDBs allow disruption. Alternative: add new pool, migrate, remove old—module design should support.

**Common weak answers:** Approve because plan says update only; miss replace symbol.

**Follow-up probes (with answers):**

**Q:** Symbols?
**A:** `-/+` replace, `~` update, `-` destroy, `+` create.

**Q:** AKS safe resize?
**A:** Often new node pool plus workload shift—not in-place default pool replace.

---
