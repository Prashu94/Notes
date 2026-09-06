# Helm & Kubernetes Basics — 55 Senior Interview Questions

**Bar:** Charts, values, releases, rollback, and enough K8s to debug a Spring pod. You are not applying for SRE, but JDs list Helm.

---

### 1. What Helm actually is.

**Short answer:** Helm is Kubernetes' package manager: charts templatize manifests and releases track deployed state. Senior interviews expect production trade-offs, failure modes, and Spring API integration—not isolated trivia.

#### What it is
Helm packages Kubernetes YAML into versioned charts with parameterized templates. A release is a named deployment instance of a chart in a cluster namespace. Helm renders templates with values, applies resources via the Kubernetes API, and stores release metadata in Secrets (Helm 3) for upgrade/rollback history. It is not a runtime controller—it is a client-side deploy tool often wrapped by CI/CD or GitOps.

#### How it works (internals)
Author a Chart.yaml, values.yaml, and templates/*.yaml using Go templating. Install with `helm install <release> <chart> -f values-prod.yaml`. Upgrade with `helm upgrade --install` for idempotent deploys. Use `helm template` locally to inspect rendered manifests before apply.

#### When to use / when NOT to use
Use Helm when you need repeatable, parameterized deployments across dev/stage/prod, shared library charts (umbrella patterns), or standardized Spring Boot service packaging on AKS. Prefer plain manifests or Kustomize when templating complexity is low and GitOps diff clarity matters more.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Production example
Pin chart version and image digest in values; store secrets outside chart (External Secrets, Key Vault). Run `helm template` and policy checks in CI. Use `--atomic` and reasonable timeouts on AKS upgrades. Separate values per environment; never commit production credentials. Document release naming conventions and namespace strategy for multi-team AKS clusters.

#### Common mistakes
- Treating Helm as source of truth instead of Git
- Embedding secrets in values.yaml committed to Git
- Using `latest` image tags in production values
- Skipping `helm diff` before upgrades
- Installing multiple releases that fight over the same cluster-scoped resources

#### Interview follow-ups (with model answers)

**Q:** How does Helm 3 differ from Helm 2 regarding Tiller?
**A:** Helm 2 relied on Tiller, a cluster-side gRPC server with elevated RBAC that applied manifests on behalf of users. That design created security and multi-tenant headaches on shared clusters. Helm 3 removed Tiller entirely: the CLI talks directly to the Kubernetes API using the caller's kubeconfig identity. Release state moved to Secrets in the release namespace (or ConfigMaps if configured). Three-way merge and hooks still exist, but permissions follow standard RBAC. On AKS, this means Helm operations audit like kubectl, and you no longer maintain a Tiller service account with cluster-admin.

**Q:** Where is release history stored and why does it matter?
**A:** Helm 3 stores each revision as a Secret (label `owner=helm`) in the namespace of the release, encoded with the rendered manifest and chart metadata. `helm history` reads these revisions; `helm rollback` re-applies a prior manifest snapshot. This matters because rollback is not a Git revert—it restores whatever was rendered at that revision, including values overrides used then. If someone hand-patched live resources, rollback can produce surprising merges. For Spring services on AKS, treat Helm history as operational backup, not your configuration catalog.

#### Scenario probe
**Situation:** Interviewer: 'We deploy Spring Boot to AKS with kubectl apply from CI. Why add Helm?'

**Model answer:** Acknowledge kubectl works for single services. Helm adds parameterized charts so 30 microservices share the same Deployment/Service/Ingress patterns with per-service values. Upgrades become revisioned releases with rollback, and umbrella charts compose platform dependencies (ingress, monitoring). On AKS, pair Helm with GitOps (Argo CD) so Git remains truth while Helm packages complexity. Offer a concrete example: one chart, values for CPU/memory/probes per service, no copy-paste YAML.

---

### 2. Chart structure.

**Short answer:** A chart is Chart.yaml + values + templates + optional charts/ dependencies and hooks. Senior interviews expect production trade-offs, failure modes, and Spring API integration—not isolated trivia.

#### What it is
Standard layout: Chart.yaml (metadata, version, appVersion), values.yaml (defaults), templates/ (Kubernetes manifests with Go template syntax), charts/ (subchart dependencies), and optional crds/, README, tests/. Templates render to standard Kubernetes resources. Named templates live in _helpers.tpl. .helmignore excludes files from packaging.

#### How it works (internals)
Run `helm create my-spring-service` for scaffolding, then replace generic templates with Deployment, Service, ConfigMap, ServiceAccount, Ingress, and PodDisruptionBudget suited for Spring Boot. Extract labels and selectors into `_helpers.tpl`. Keep environment-specific config in values, not templates.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### When to use / when NOT to use
Structure matters when multiple teams consume your chart or when you publish to OCI/ChartMuseum. Strict layout enables `helm lint`, chart-testing, and dependency version pinning via Chart.lock.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Production example
Version Chart.yaml on every publish; use semantic versioning. Pin subchart versions in Chart.yaml and commit Chart.lock. Keep templates readable—complex logic belongs in values or external tooling. Add NOTES.txt for post-install hints (health URL, swagger path).

#### Common mistakes
- Hardcoding namespace in templates instead of `.Release.Namespace`
- Putting business logic in templates with deeply nested conditionals
- Forgetting to bump chart version when only templates change
- Shipping default values unsuitable for production (replicaCount: 1, no resources)
- Omitting standard labels (app.kubernetes.io/*)

#### Interview follow-ups (with model answers)

**Q:** What belongs in _helpers.tpl versus values.yaml?
**A:** _helpers.tpl defines reusable template fragments: fullname, chart labels, selector labels, and common annotations. These are structural and stable across environments—they encode naming conventions and Kubernetes recommended labels. values.yaml holds data that changes per environment: replica counts, image repository, JVM flags, ingress hostnames, and Spring profiles. Blurring the line leads to duplicated helper logic per env and harder chart reviews. For Spring on AKS, helpers enforce consistent label selectors across Deployment, Service, and HPA so you never break immutable selectors during a values-only change.

**Q:** How do chart dependencies work?
**A:** Declare dependencies in Chart.yaml under dependencies with name, version, and repository URL or OCI registry. Run helm dependency update to vendor tarballs into charts/ and generate Chart.lock for reproducible builds. Parent values override subchart values via the dependency name or alias prefix at the top level of values.yaml. Umbrella charts bundle ingress controllers, cert-manager, or observability agents alongside your Spring application. Pin versions explicitly on AKS—floating semver ranges have caused production outages when a subchart major version changed defaults for probes or security contexts.

#### Scenario probe
**Situation:** Interviewer: 'Walk me through your Spring Boot chart layout.'

**Model answer:** Chart.yaml names the chart and versions. values.yaml defaults replicas, image, probes, resources, and Spring profile. templates/ has deployment with env from ConfigMap/Secret refs, Service, optional Ingress, HPA, PDB, and ServiceAccount. _helpers.tpl centralizes labels matching app.kubernetes.io conventions. tests/ might curl the actuator health endpoint. Dependencies pull shared platform charts if needed.

---

### 3. `helm install` vs `upgrade` vs `rollback` vs `uninstall`.

**Short answer:** install creates a release; upgrade revises it; rollback restores a revision; uninstall removes it. Senior interviews expect production trade-offs, failure modes, and Spring API integration—not isolated trivia.

#### What it is
helm install creates release revision 1 from a chart and values. helm upgrade creates a new revision with updated chart/values; --install makes it idempotent. helm rollback re-applies a prior revision's manifest. helm uninstall deletes release-tracked resources (with hooks) and removes history unless --keep-history.

#### How it works (internals)
CI/CD: `helm upgrade --install myapp ./chart -f values-prod.yaml --namespace prod --atomic --timeout 10m`. Rollback: `helm rollback myapp 3`. Uninstall: `helm uninstall myapp`. Always check `helm history` and `helm status` before and after.

#### When to use / when NOT to use
Install for first deploy; upgrade for every subsequent change; rollback for fast mitigation when a bad revision is live; uninstall when decommissioning a service or namespace cleanup.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Production example
Use --atomic on AKS so failed upgrades auto-rollback. Set --wait and probe-aware timeouts for Spring startup. Never rollback as a substitute for fixing forward in Git. Keep revision history limit reasonable.

#### Common mistakes
- Running install when release already exists (use upgrade --install)
- Rollback without understanding values at that revision
- Uninstalling without checking shared resources or PVCs
- Skipping --wait and assuming pods are healthy
- Concurrent upgrades from two pipelines

#### Interview follow-ups (with model answers)

**Q:** What does --atomic do?
**A:** --atomic wraps upgrade in transaction-like behavior: if the upgrade fails due to timeout, failed hooks, or resource errors, Helm automatically rolls back to the previous revision without leaving the cluster in a half-updated state. On AKS Spring deploys, this prevents Deployments pointing at a new ConfigMap while old pods still run, or vice versa. Combine with --wait so Helm waits for readiness probes before declaring success. Trade-off: longer pipeline times and possible false rollbacks if startup probes are too aggressive for slow JVM warm-up or Flyway migrations.

**Q:** Does rollback change the chart version in Git?
**A:** No. Helm rollback only changes cluster state to match a stored revision snapshot in the release Secret. Your Git repository still points at the bad commit unless developers revert there too. In GitOps with Argo CD on AKS, prefer reverting Git and letting the controller sync rather than manual helm rollback alone. Manual rollback causes drift between Git desired state and live cluster until reconciled. Best practice: emergency helm rollback for user impact, then immediate Git revert and Argo sync to restore single source of truth.

#### Scenario probe
**Situation:** Interviewer: 'Production deploy failed mid-upgrade. What do you run first?'

**Model answer:** Check `helm history` and `kubectl get pods` for the failed revision. If user impact is high and the prior revision was healthy, `helm rollback <release> <good-rev>` for immediate relief. Then diagnose root cause (bad image, config, probe). Fix forward in Git and redeploy. On Spring services, verify actuator health and recent ConfigMap changes before re-attempting upgrade.

---

### 4. Three-way strategic merge.

**Short answer:** Helm three-way merge compares old manifest, new manifest, and live cluster state on upgrade. Senior interviews expect production trade-offs, failure modes, and Spring API integration—not isolated trivia.

#### What it is
On upgrade, Helm loads the previous release manifest, renders the new manifest, and fetches live resources. It merges to preserve fields changed out-of-band (kubectl edit) where possible. This differs from plain kubectl apply three-way merge but solves similar drift problems.

#### How it works (internals)
Understand that manual kubectl patches may survive upgrades—or conflict unexpectedly. Use `helm get manifest` and `helm diff upgrade` to preview. For GitOps, avoid hand-editing live resources.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### When to use / when NOT to use
Relevant when operators hot-fix production without updating Helm values, or when admission controllers mutate resources (sidecar injection, defaults on AKS).  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Production example
Discipline: all changes through values/Git. Use drift detection in Argo CD. Document that HPA-owned replica counts should use Helm hooks or omit replicas in templates when HPA enabled.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Common mistakes
- kubectl editing Deployments then blaming Helm for 'random' reversions
- Expecting merge to fix invalid immutable field changes
- Not knowing HPA scales replicas outside Helm's last rendered value
- Ignoring admission webhook mutations in diff previews

#### Interview follow-ups (with model answers)

**Q:** What happens if someone changed replicas with kubectl?
**A:** If the Deployment template still sets replicas explicitly, the next Helm upgrade may reset replicas to the chart value, overriding the manual kubectl scale unless your chart omits replicas when HPA is enabled. Three-way merge tries to reconcile live changes but spec fields from the new manifest generally win. HPA-owned replica counts are a special case—Helm should not fight the autoscaler. Best practice for Spring services on AKS: scale via HPA or values changes, not kubectl patch, and document that in the operations runbook.

**Q:** What is the first command or dashboard you check when this misbehaves on AKS?
**A:** I start with `helm status <release> -n <ns>` and `helm history` to see if a recent upgrade correlates with the incident. Then `kubectl get pods -l app.kubernetes.io/instance=<release>` and `kubectl describe` the failing pod for events—ImagePullBackOff, OOMKilled, probe failures. Spring-specific: `kubectl logs` for datasource or Flyway errors; compare `helm get values` against expected profile. If JVM OOM, check limits vs requests and whether HPA scaled beyond node capacity. For config issues, `helm template` locally with prod values (redacted) and diff against live manifest. Document findings with revision number before rollback so postmortem can reference exact chart+image combo.

#### Scenario probe
**Situation:** Interviewer: 'After helm upgrade, our manual resource limit change disappeared.'

**Model answer:** Explain Helm reapplied the chart template, overwriting the kubectl patch. Show how to put limits in values.yaml or use post-renderer/Kustomize overlay in GitOps. Recommend helm diff before upgrade and banning emergency kubectl edits without a follow-up values change.

---

### 5. Values override order.

**Short answer:** Values merge: chart defaults < -f files < --set/--set-file, later overrides win. Senior interviews expect production trade-offs, failure modes, and Spring API integration—not isolated trivia.

#### What it is
Helm merges values from the chart's values.yaml, then each -f/--values file in order, then --set/--set-string/--set-file flags. Subchart values nest under the dependency alias/name. Parent chart can pass values to children via the dependencies section or prefixed keys.

#### How it works (internals)
Layer: values.yaml (defaults) < values-aks.yaml (cluster) < values-prod.yaml (env) < CI --set image.tag=$SHA. Use `helm get values -a` to see effective values on a live release.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### When to use / when NOT to use
Every multi-environment Spring deployment. Override order disputes are a common source of 'wrong profile in prod' bugs.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Production example
Document override order in README. Never rely on --set for secrets in CI logs. Use structured values: spring.profiles.active, jvm.opts, datasource.url from ExternalSecret.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Common mistakes
- Passing -f files in wrong order so staging overrides prod
- Using --set for complex nested structures and typos
- Forgetting subchart values need correct prefix
- Assuming empty string in later file clears a key (merge semantics)

#### Interview follow-ups (with model answers)

**Q:** How do you verify effective values on a running release?
**A:** Run helm get values release -n namespace for user-supplied values, or add -a for computed values including chart defaults. Compare output with helm template locally using the identical -f file chain and --set flags your pipeline uses. In Argo CD, inspect live manifests and Helm parameters on the Application resource. For Spring Boot, confirm spring.profiles.active, datasource URLs, and JVM options match intent before approving a prod sync. When prod diverges from staging, diff effective values first—it is the fastest way to explain wrong-profile bugs.

**Q:** What is the first command or dashboard you check when this misbehaves on AKS?
**A:** I start with `helm status <release> -n <ns>` and `helm history` to see if a recent upgrade correlates with the incident. Then `kubectl get pods -l app.kubernetes.io/instance=<release>` and `kubectl describe` the failing pod for events—ImagePullBackOff, OOMKilled, probe failures. Spring-specific: `kubectl logs` for datasource or Flyway errors; compare `helm get values` against expected profile. If JVM OOM, check limits vs requests and whether HPA scaled beyond node capacity. For config issues, `helm template` locally with prod values (redacted) and diff against live manifest. Document findings with revision number before rollback so postmortem can reference exact chart+image combo.

#### Scenario probe
**Situation:** Interviewer: 'Prod used staging DB URL after deploy. How?'

**Model answer:** Walk through values file order: likely prod pipeline passed values-staging.yaml after values-prod.yaml, or --set overwrote spring.datasource.url. Show helm get values on the release and CI logs for -f order. Fix: explicit file naming, environment guards in pipeline, and required review for prod value files.

---

### 6. Templating: `{{ .Values.x }}`, `include`, `required`.

**Short answer:** Use include and required in templates to compose snippets and fail fast on missing values. Senior interviews expect production trade-offs, failure modes, and Spring API integration—not isolated trivia.

#### What it is
`include` renders named templates from _helpers.tpl and returns strings for piping. `required` aborts render with an error if a value is empty—prevents silent bad deploys. `define`/`template` blocks build reusable label, name, and annotation fragments.

#### How it works (internals)
Example: `{{ include \"mychart.labels\" . | nindent 4 }}` and `{{ required \"image.repository is required\" .Values.image.repository }}`. Use `tpl` to render values that themselves contain template snippets sparingly.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### When to use / when NOT to use
Any chart consumed by others or deployed to prod without human review of every rendered field.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Production example
Required fields for image.repository, image.tag, ingress.host in prod profiles. Lint templates in CI with `helm template` against minimal and prod fixture values.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Common mistakes
- Using template instead of include and losing whitespace control
- Required on values that are legitimately empty in some envs
- Duplicating label logic instead of central helpers
- tpl on untrusted values (injection risk)

#### Interview follow-ups (with model answers)

**Q:** include vs template?
**A:** The template action renders a named template inline at the call site. The include function renders a named template and returns the result as a string you can pipe to nindent, indent, or quote. For YAML blocks in Kubernetes manifests, include is preferred because you control indentation precisely. Both access the same root context dot. Senior charts use include almost exclusively for labels, fullname, and selector helpers. Choosing template where include is needed often produces YAML indentation errors that only appear at apply time on AKS.

**Q:** What is the first command or dashboard you check when this misbehaves on AKS?
**A:** I start with `helm status <release> -n <ns>` and `helm history` to see if a recent upgrade correlates with the incident. Then `kubectl get pods -l app.kubernetes.io/instance=<release>` and `kubectl describe` the failing pod for events—ImagePullBackOff, OOMKilled, probe failures. Spring-specific: `kubectl logs` for datasource or Flyway errors; compare `helm get values` against expected profile. If JVM OOM, check limits vs requests and whether HPA scaled beyond node capacity. For config issues, `helm template` locally with prod values (redacted) and diff against live manifest. Document findings with revision number before rollback so postmortem can reference exact chart+image combo.

#### Scenario probe
**Situation:** Interviewer: 'Deploy succeeded but Service had empty selector labels.'

**Model answer:** Likely missing required validation on critical values and empty default label values. Add required for app name, use shared selector helper included in both Deployment and Service. Add CI test that helm template fails when required values omitted.

---

### 7. `lookup` and why it's dangerous.

**Short answer:** lookup queries live cluster during template render—non-deterministic and dangerous in CI/GitOps. Senior interviews expect production trade-offs, failure modes, and Spring API integration—not isolated trivia.

#### What it is
The `lookup` function reads existing Secrets, ConfigMaps, or other resources at render time to inject data into templates. Output depends on cluster state at render moment, not just values files.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### How it works (internals)
Avoid lookup for passwords and release-critical config. Prefer External Secrets Operator, Sealed Secrets, or CSI Secret Store to mount Key Vault secrets. If unavoidable, document cluster dependency.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### When to use / when NOT to use
Rarely in production charts. Sometimes for advanced cluster discovery patterns—not for Spring credentials.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Production example
helm template in CI must not call lookup without cluster or it returns empty. Argo CD renders may differ from local renders. Use deterministic values and operators instead.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Common mistakes
- Generating DB passwords with lookup and random on every upgrade
- Relying on lookup in helm template CI checks
- Non-idempotent renders causing Secret churn
- Using lookup for cross-release coordination

#### Interview follow-ups (with model answers)

**Q:** Why does helm template show empty Secret data with lookup?
**A:** The lookup function requires a live Kubernetes API server during template render. Offline helm template has no cluster, so lookup returns nil and Secret data blocks render empty. The same chart rendered in CI, Argo CD, and helm upgrade can therefore produce different manifests. That breaks GitOps review and can rotate secrets unintentionally on every upgrade if templates generate new values. Replace lookup with pre-provisioned secrets, External Secrets Operator pulling from Azure Key Vault, or Sealed Secrets instead. Validate on AKS staging with the same values chain, Helm version, and admission policies as production. Store rendered manifests per release revision for incident review, and add helm template plus policy checks in CI. Senior interviews expect trade-offs, failure modes, and how

**Q:** What is the first command or dashboard you check when this misbehaves on AKS?
**A:** I start with `helm status <release> -n <ns>` and `helm history` to see if a recent upgrade correlates with the incident. Then `kubectl get pods -l app.kubernetes.io/instance=<release>` and `kubectl describe` the failing pod for events—ImagePullBackOff, OOMKilled, probe failures. Spring-specific: `kubectl logs` for datasource or Flyway errors; compare `helm get values` against expected profile. If JVM OOM, check limits vs requests and whether HPA scaled beyond node capacity. For config issues, `helm template` locally with prod values (redacted) and diff against live manifest. Document findings with revision number before rollback so postmortem can reference exact chart+image combo.

#### Scenario probe
**Situation:** Interviewer: 'Chart uses lookup to read existing Secret on upgrade. Concerns?'

**Model answer:** Non-deterministic renders, broken CI validation, accidental secret regeneration, and GitOps drift. Propose External Secrets pulling from Azure Key Vault, with Deployment referencing secretRef. Helm only deploys the ExternalSecret CR and Deployment wiring, not secret content at render time.

---

### 8. Hooks.

**Short answer:** Hooks run Jobs or resources at defined lifecycle points: pre/post install, upgrade, delete. Senior interviews expect production trade-offs, failure modes, and Spring API integration—not isolated trivia.

#### What it is
Resources annotated with helm.sh/hook and hook-weight run outside the normal release ordering. Hook types include pre-install, post-install, pre-upgrade, post-upgrade, pre-delete, post-delete, and test hooks. Hook-delete-policy controls retention after success/failure.

#### How it works (internals)
Define a Job manifest with hook annotations for migrations or cache warm-up. Set hook-weight for ordering among hooks. Use `helm test` for test hooks hitting Spring actuator.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### When to use / when NOT to use
One-off setup, post-deploy smoke tests, or coordinated tasks—not long-running controllers.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Production example
Keep hooks short-lived with backoff limits. Failed hooks block --wait and --atomic rollbacks. Monitor hook Job logs in AKS. Prefer running DB migrations outside Helm for critical systems.

#### Common mistakes
- Hooks without resource limits causing node pressure
- Forgotten hook resources cluttering namespace
- Wrong hook-delete-policy leaving failed Jobs
- Heavy work in pre-upgrade without timeout strategy

#### Interview follow-ups (with model answers)

**Q:** What is hook-weight?
**A:** Hook-weight is an integer that orders hooks of the same type; lower values run first. Use it when a pre-upgrade hook needs namespace preparation before a migration Job, or when multiple post-install hooks must run sequentially. Combine with hook-delete-policy hook-succeeded to clean up completed Jobs and avoid clutter. Document weights when platform teams add hooks alongside application hooks in umbrella charts on AKS. Without weights, hook execution order is undefined and can cause race conditions during Spring service upgrades. Validate on AKS staging with the same values chain, Helm version, and admission policies as production. Store rendered manifests per release revision for incident review, and add helm template plus policy checks in CI. Senior interviews expect trade-offs, failure modes, and

**Q:** What is the first command or dashboard you check when this misbehaves on AKS?
**A:** I start with `helm status <release> -n <ns>` and `helm history` to see if a recent upgrade correlates with the incident. Then `kubectl get pods -l app.kubernetes.io/instance=<release>` and `kubectl describe` the failing pod for events—ImagePullBackOff, OOMKilled, probe failures. Spring-specific: `kubectl logs` for datasource or Flyway errors; compare `helm get values` against expected profile. If JVM OOM, check limits vs requests and whether HPA scaled beyond node capacity. For config issues, `helm template` locally with prod values (redacted) and diff against live manifest. Document findings with revision number before rollback so postmortem can reference exact chart+image combo.

#### Scenario probe
**Situation:** Interviewer: 'When would you use a post-install hook?'

**Model answer:** Post-install after resources exist: smoke test Job curling /actuator/health, register with service discovery, or notify Slack. Not for schema migrations in prod. Mention hook-delete-policy and --wait interaction.

---

### 9. Why DB migrate-in-Helm-hook is risky.

**Short answer:** Running DB migrations in Helm hooks is risky: partial failure, locking, and rollback mismatch. Senior interviews expect production trade-offs, failure modes, and Spring API integration—not isolated trivia.

#### What it is
Schema migrations mutate persistent state while Helm tracks stateless Kubernetes resources. If upgrade fails after migration, app rollback may not match DB schema. Concurrent replicas during hook windows can race. Long migrations exceed upgrade timeouts.

#### How it works (internals)
Run Flyway/Liquibase in CI/CD pipeline before helm upgrade, or as separate Kubernetes Job with manual approval and backup. Use backward-compatible migrations for roll-forward-only strategy.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### When to use / when NOT to use
Small dev clusters only for hook-based migrate. Production Spring services on AKS: pipeline-gated migrations.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Production example
Backup before migrate, expand-contract pattern, feature flags for code/schema coupling. Never rely on helm rollback to undo DDL.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Common mistakes
- Non-backward-compatible migration before new pods
- Hook migration without single-flight locking
- Assuming helm rollback reverts Liquibase changes
- No timeout on migration Job

#### Interview follow-ups (with model answers)

**Q:** How would you order migration and app deploy for zero downtime?
**A:** Use expand-contract migrations: first deploy DDL that is backward compatible, then roll out application code that reads both old and new schema, then remove obsolete columns in a later release. Run the migration Job once with a pipeline mutex or leader election before rolling new images via Helm. Validate on AKS staging with production-like data volume and connection pool settings. Spring Flyway baseline and validate-on-migrate settings should be explicit in values, not hidden in Helm hooks. Never assume helm rollback will undo DDL—plan roll-forward fixes instead.

**Q:** What is the first command or dashboard you check when this misbehaves on AKS?
**A:** I start with `helm status <release> -n <ns>` and `helm history` to see if a recent upgrade correlates with the incident. Then `kubectl get pods -l app.kubernetes.io/instance=<release>` and `kubectl describe` the failing pod for events—ImagePullBackOff, OOMKilled, probe failures. Spring-specific: `kubectl logs` for datasource or Flyway errors; compare `helm get values` against expected profile. If JVM OOM, check limits vs requests and whether HPA scaled beyond node capacity. For config issues, `helm template` locally with prod values (redacted) and diff against live manifest. Document findings with revision number before rollback so postmortem can reference exact chart+image combo.

#### Scenario probe
**Situation:** Interviewer: 'Team runs Flyway in pre-upgrade hook. Your review?'

**Model answer:** Flag rollback/schema mismatch risk and timeout issues on AKS. Recommend pipeline Job with backup gate, then helm upgrade. Mention backward-compatible migrations and that Helm atomic rollback won't undo DDL.

---

### 10. Chart version vs appVersion.

**Short answer:** chart version tracks chart package; appVersion documents the application release (often image). Senior interviews expect production trade-offs, failure modes, and Spring API integration—not isolated trivia.

#### What it is
Chart.yaml `version` is the chart semver (template/values changes). `appVersion` is informational—typically the Spring Boot app or container tag you ship. They version independently: chart 2.1.0 might package app 3.4.5.

#### How it works (internals)
Bump chart version on any chart change for publishing. Set appVersion in CI from build metadata. Image tag usually comes from values.image.tag, not automatically from appVersion unless templated.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### When to use / when NOT to use
Publishing to OCI/artifact registry or tracking compatibility between chart API and app releases.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Production example
Pin chart version in Argo CD Application. Align appVersion with image for traceability in helm list output.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Common mistakes
- Bumping only appVersion without chart version when templates changed
- Assuming appVersion drives deployment image automatically
- Using same version for unrelated chart and app changes
- No changelog between chart versions

#### Interview follow-ups (with model answers)

**Q:** What do consumers see in helm search?
**A:** Repository indexes and OCI registries show chart version and appVersion columns for each published package. Consumers pin chart version for reproducible deploys; appVersion helps quick identification of which Spring Boot release the chart intends to run. Operational truth is still image.tag in values at deploy time—verify chart version, appVersion, and image digest all align in production. On ACR OCI Helm repos, semver tags are immutable artifacts; document breaking chart changes in CHANGELOG for downstream teams consuming your platform chart. Validate on AKS staging with the same values chain, Helm version, and admission policies as production. Store rendered manifests per release revision for incident review, and add helm template plus policy checks in CI. Senior interviews expect trade-offs, failure modes, and

**Q:** What is the first command or dashboard you check when this misbehaves on AKS?
**A:** I start with `helm status <release> -n <ns>` and `helm history` to see if a recent upgrade correlates with the incident. Then `kubectl get pods -l app.kubernetes.io/instance=<release>` and `kubectl describe` the failing pod for events—ImagePullBackOff, OOMKilled, probe failures. Spring-specific: `kubectl logs` for datasource or Flyway errors; compare `helm get values` against expected profile. If JVM OOM, check limits vs requests and whether HPA scaled beyond node capacity. For config issues, `helm template` locally with prod values (redacted) and diff against live manifest. Document findings with revision number before rollback so postmortem can reference exact chart+image combo.

#### Scenario probe
**Situation:** Interviewer: 'We changed only values.yaml defaults. Bump chart version?'

**Model answer:** Yes if publishing the chart artifact; consumers need semver signal. appVersion unchanged if application bits unchanged. For internal monorepo charts used only by GitOps path, some teams bump on any merge to main.

---

### 11. Umbrella charts vs many releases.

**Short answer:** Umbrella chart bundles subcharts; many releases deploy components independently with looser coupling. Senior interviews expect production trade-offs, failure modes, and Spring API integration—not isolated trivia.

#### What it is
Umbrella (parent) chart lists dependencies in Chart.yaml—one helm install deploys app plus ingress, redis, etc. Many releases means separate helm installs per component, linked by values and conventions, not one atomic unit.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### How it works (internals)
Umbrella for tightly versioned stacks (demo env, single-tenant). Separate releases for platform (ingress-controller) vs apps (spring-order-service) on shared AKS.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### When to use / when NOT to use
Umbrella when upgrade cadence and ownership are unified. Many releases when teams or lifecycles differ—typical enterprise AKS.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Production example
Platform team owns cluster add-ons as separate releases. App teams own microservice releases. Document cross-release dependencies (e.g., cert-manager must exist before app Ingress).  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Common mistakes
- Monolithic umbrella blocking independent team deploys
- Subchart version drift without Chart.lock
- Duplicate cluster-scoped resources from umbrella and standalone install
- Parent values typos breaking silent subchart defaults

#### Interview follow-ups (with model answers)

**Q:** How do you pass values to a subchart?
**A:** Use the subchart name or alias as a top-level key in parent values.yaml—for example postgresql.auth.password under the dependency name. Alternatively configure an alias in Chart.yaml when the chart name differs from the values prefix you want. Parent charts can also expose a global: stanza if subcharts implement the global values pattern for shared settings like imagePullSecrets. Always validate with helm template and inspect rendered subchart sections before a production umbrella upgrade on AKS. Undocumented prefix typos silently leave subcharts at insecure defaults, which is a common multi-team incident pattern.

**Q:** What is the first command or dashboard you check when this misbehaves on AKS?
**A:** I start with `helm status <release> -n <ns>` and `helm history` to see if a recent upgrade correlates with the incident. Then `kubectl get pods -l app.kubernetes.io/instance=<release>` and `kubectl describe` the failing pod for events—ImagePullBackOff, OOMKilled, probe failures. Spring-specific: `kubectl logs` for datasource or Flyway errors; compare `helm get values` against expected profile. If JVM OOM, check limits vs requests and whether HPA scaled beyond node capacity. For config issues, `helm template` locally with prod values (redacted) and diff against live manifest. Document findings with revision number before rollback so postmortem can reference exact chart+image combo.

#### Scenario probe
**Situation:** Interviewer: 'One helm release for entire platform or per microservice?'

**Model answer:** Per microservice for independent CI/CD and blast radius. Shared infra (ingress, cert-manager, monitoring) as separate platform releases. Optional umbrella only for ephemeral environments. Mention Chart.lock and team ownership on AKS.

---

### 12. `helm template` in CI.

**Short answer:** helm template renders manifests offline—ideal for CI diff, policy checks, and review without cluster. Senior interviews expect production trade-offs, failure modes, and Spring API integration—not isolated trivia.

#### What it is
`helm template <release> <chart> -f values.yaml` outputs rendered YAML to stdout. No cluster required unless templates use lookup. Used for validation, kubeconform, OPA/Kyverno dry-run.

#### How it works (internals)
CI job: template with prod values fixture, pipe to kubeconform, conftest, or kyverno apply --dry-run. Fail build on invalid API versions or missing required values.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### When to use / when NOT to use
Every PR touching charts. Pre-promotion gate before Argo CD sync or helm upgrade.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Production example
Use same -f order as deploy pipeline. Store golden files for regression diff. Validate against target AKS Kubernetes version schema.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Common mistakes
- CI templates with dev values while prod deploy uses different files
- Skipping validation because 'we use Argo CD'
- lookup making CI output misleading
- Not pinning helm version in CI vs local

#### Interview follow-ups (with model answers)

**Q:** helm template vs helm install --dry-run?
**A:** helm template is a client-only render to stdout—fast, deterministic, and ideal for CI without cluster credentials. helm install --dry-run sends rendered manifests to the API server for validation; behavior varies with server-side dry-run settings. For CI pipelines on AKS, template plus kubeconform or kyverno CLI is the standard gate. To exercise admission webhooks and mutating controllers, use kubectl apply --dry-run=server against a staging cluster. Senior teams never treat dry-run success as proof Spring actuator health will pass—only that Kubernetes accepted the schema.

**Q:** What is the first command or dashboard you check when this misbehaves on AKS?
**A:** I start with `helm status <release> -n <ns>` and `helm history` to see if a recent upgrade correlates with the incident. Then `kubectl get pods -l app.kubernetes.io/instance=<release>` and `kubectl describe` the failing pod for events—ImagePullBackOff, OOMKilled, probe failures. Spring-specific: `kubectl logs` for datasource or Flyway errors; compare `helm get values` against expected profile. If JVM OOM, check limits vs requests and whether HPA scaled beyond node capacity. For config issues, `helm template` locally with prod values (redacted) and diff against live manifest. Document findings with revision number before rollback so postmortem can reference exact chart+image combo.

#### Scenario probe
**Situation:** Interviewer: 'How do you catch bad Ingress before prod?'

**Model answer:** helm template with prod values, kubeconform against AKS version, policy check for required labels and TLS. Optional PR comment with diff vs main branch golden manifest.

---

### 13. Secrets in Helm.

**Short answer:** Never commit plaintext secrets in charts; use External Secrets, Sealed Secrets, or CSI with Key Vault. Senior interviews expect production trade-offs, failure modes, and Spring API integration—not isolated trivia.

#### What it is
Helm values often need DB passwords and API keys. Charts should reference Kubernetes Secret names, not secret values. Azure Key Vault + External Secrets Operator syncs to K8s Secrets on AKS.

#### How it works (internals)
Template ExternalSecret or SecretProviderClass; Deployment envFrom secretRef. Sealed Secrets for Git-stored encrypted blobs. SOPS-encrypted values decrypted in CI only.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### When to use / when NOT to use
Always in production. Spring Boot: spring.datasource.password from env sourced from Secret.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Production example
RBAC limit Secret read to namespace SA. Rotate via Key Vault. Audit helm get values does not leak secrets. Avoid printing --set passwords in CI logs.

#### Common mistakes
- secrets.yaml in Git with base64 'encoding' (still visible)
- helm get values exposing --set secrets in release metadata
- Shared Secret across envs
- lookup generating passwords into Helm release Secret

#### Interview follow-ups (with model answers)

**Q:** Are Helm release Secrets a security concern?
**A:** Helm 3 stores each release revision in a Secret labeled owner=helm, including the rendered manifest snapshot. If you templated plaintext secrets into manifests, they are recoverable via helm get manifest and helm get values. Treat release Secrets as sensitive: restrict RBAC to namespace admins and break-glass roles. Better pattern: manifests contain only secretRef or env valueFrom references; secret bytes live in Key Vault synced by External Secrets. Audit CI to ensure --set passwords never appear in build logs or release metadata on shared AKS clusters.

**Q:** What is the first command or dashboard you check when this misbehaves on AKS?
**A:** I start with `helm status <release> -n <ns>` and `helm history` to see if a recent upgrade correlates with the incident. Then `kubectl get pods -l app.kubernetes.io/instance=<release>` and `kubectl describe` the failing pod for events—ImagePullBackOff, OOMKilled, probe failures. Spring-specific: `kubectl logs` for datasource or Flyway errors; compare `helm get values` against expected profile. If JVM OOM, check limits vs requests and whether HPA scaled beyond node capacity. For config issues, `helm template` locally with prod values (redacted) and diff against live manifest. Document findings with revision number before rollback so postmortem can reference exact chart+image combo.

#### Scenario probe
**Situation:** Interviewer: 'How do Spring apps get DB password on AKS?'

**Model answer:** External Secrets Operator pulls from Azure Key Vault into K8s Secret; chart templates secretRef on Deployment; Spring reads SPRING_DATASOURCE_PASSWORD from env. Helm never contains plaintext password.

---

### 14. Deployment vs StatefulSet vs DaemonSet vs Job vs CronJob.

**Short answer:** Workload types: Deployment (stateless), StatefulSet (stable identity/storage), DaemonSet (per-node), Job/CronJob (batch). Senior interviews expect production trade-offs, failure modes, and Spring API integration—not isolated trivia.

#### What it is
Deployment manages ReplicaSets for stateless Spring Boot APIs with rolling updates. StatefulSet gives stable network IDs and PVCs for databases—not typical for Spring app pods. DaemonSet runs one pod per node (log agents). Job runs to completion; CronJob schedules Jobs.

#### How it works (internals)
Default Spring microservice: Deployment + Service. Choose StatefulSet only if app requires stable hostname or local PVC per pod (rare for Spring).  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### When to use / when NOT to use
Deployment for 99% of Spring REST services on AKS. CronJob for scheduled batch; separate from main HTTP Deployment.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Production example
Match workload to data semantics. Don't run Postgres inside Deployment without understanding data loss. Use Azure managed services instead of StatefulSet databases when possible.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Common mistakes
- StatefulSet for stateless Spring 'because prod'
- Deployment for workload needing stable per-pod storage
- CronJob without concurrencyPolicy and backoff limits
- DaemonSet for app that should scale with load

#### Interview follow-ups (with model answers)

**Q:** When would Spring use a Job instead of Deployment?
**A:** Use a Job for one-shot tasks that must run to completion: Flyway migration runner, search reindex, batch export, or data backfill. Jobs support parallelism, backoff limits, and ttlSecondsAfterFinished for cleanup. They are inappropriate for long-running HTTP APIs—that is a Deployment with probes and HPA. Production Spring teams usually run migrations in CI/CD or approved pipeline Jobs rather than Helm hooks for auditability. Helm can template the Job manifest, but orchestration and approval gates belong in the deployment pipeline on AKS.

**Q:** What is the first command or dashboard you check when this misbehaves on AKS?
**A:** I start with `helm status <release> -n <ns>` and `helm history` to see if a recent upgrade correlates with the incident. Then `kubectl get pods -l app.kubernetes.io/instance=<release>` and `kubectl describe` the failing pod for events—ImagePullBackOff, OOMKilled, probe failures. Spring-specific: `kubectl logs` for datasource or Flyway errors; compare `helm get values` against expected profile. If JVM OOM, check limits vs requests and whether HPA scaled beyond node capacity. For config issues, `helm template` locally with prod values (redacted) and diff against live manifest. Document findings with revision number before rollback so postmortem can reference exact chart+image combo.

#### Scenario probe
**Situation:** Interviewer: 'Why Deployment not StatefulSet for our API?'

**Model answer:** API is stateless; any pod handles traffic; PVCs and stable ordinals unnecessary. Deployment enables rolling updates and simpler HPA. State lives in Azure SQL/Cosmos, not pod disks.

---

### 15. Pod, ReplicaSet, Deployment.

**Short answer:** Pod is the unit; ReplicaSet maintains pod count; Deployment manages ReplicaSets and rollout strategy. Senior interviews expect production trade-offs, failure modes, and Spring API integration—not isolated trivia.

#### What it is
Pods are ephemeral. ReplicaSet ensures desired replica count with a label selector. Deployment owns ReplicaSets and handles rolling updates by creating new RS and scaling down old.

#### How it works (internals)
Helm templates Deployment spec.replicas, selector, template labels. HPA can own replicas field when enabled—omit static replicas in chart or use conditional.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### When to use / when NOT to use
Understanding rollbacks at pod vs deployment level during incidents and immutable selector errors.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Production example
PodDisruptionBudget protects Deployment during node drains on AKS. Match selector labels exactly between Deployment and Service.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Common mistakes
- Changing immutable selector labels on live Deployment
- Editing ReplicaSet directly instead of Deployment
- Label mismatch between Service and Deployment
- Ignoring maxSurge/maxUnavailable during peak traffic

#### Interview follow-ups (with model answers)

**Q:** What happens during a rolling update?
**A:** The Deployment controller creates a new ReplicaSet with the updated pod template and scales it up according to maxSurge and maxUnavailable. It simultaneously scales down the old ReplicaSet once new pods pass readiness probes and join Service endpoints. Kubernetes removes not-ready pods from load balancing automatically. Spring Boot must expose accurate readiness—often /actuator/health/readiness—so traffic shifts only to JVMs that finished startup and critical checks. Misconfigured maxUnavailable during peak hours can drop capacity below SLO on AKS node pools without autoscaling headroom.

**Q:** What is the first command or dashboard you check when this misbehaves on AKS?
**A:** I start with `helm status <release> -n <ns>` and `helm history` to see if a recent upgrade correlates with the incident. Then `kubectl get pods -l app.kubernetes.io/instance=<release>` and `kubectl describe` the failing pod for events—ImagePullBackOff, OOMKilled, probe failures. Spring-specific: `kubectl logs` for datasource or Flyway errors; compare `helm get values` against expected profile. If JVM OOM, check limits vs requests and whether HPA scaled beyond node capacity. For config issues, `helm template` locally with prod values (redacted) and diff against live manifest. Document findings with revision number before rollback so postmortem can reference exact chart+image combo.

#### Scenario probe
**Situation:** Interviewer: 'Pods restart but Deployment shows old image.'

**Model answer:** Check if editing ReplicaSet directly—Deployment reconciles back. Verify image tag in Deployment spec, not just pod env cache. Check for multiple ReplicaSets and rollout status.

---

### 16. Probes: liveness vs readiness vs startup.

**Short answer:** Startup probe delays liveness/readiness until JVM up; readiness gates traffic; liveness restarts stuck containers. Senior interviews expect production trade-offs, failure modes, and Spring API integration—not isolated trivia.

#### What it is
startupProbe: for slow Spring Boot start, prevents liveness killing during warm-up. readinessProbe: fails remove pod from Service endpoints—use /actuator/health/readiness. livenessProbe: fails restart container—use lightweight check, not full dependency graph.

#### How it works (internals)
Helm values: probes enabled, paths, initialDelaySeconds, periodSeconds, failureThreshold. Spring Boot 2.3+ separate liveness/readiness groups in application.yml.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### When to use / when NOT to use
Always for production Spring on AKS. Startup probe when start > 30s (large classpath, Flyway).  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Production example
Liveness should not call external DB if that causes false restarts. Align probe timeouts with Istio/linkerd if mesh enabled.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Common mistakes
- Same heavy /actuator/health for liveness and readiness
- No startup probe on slow JVM causing restart loop
- Readiness includes downstream failures killing all pods
- Probe port wrong when management.server.port separate

#### Interview follow-ups (with model answers)

**Q:** What should Spring liveness check?
**A:** Liveness should verify the JVM process is responsive, not that every downstream dependency is healthy. Use Spring Boot 2.3+ health groups: liveness state or a lightweight ping endpoint separate from readiness. If the database is temporarily unavailable, you typically want the pod not ready but not restart-looping. Configure management.endpoint.health.group.liveness and keep liveness cheap to avoid GC pauses triggering kills. On AKS, align probe timeouts with Istio sidecars if mesh injection adds proxy startup latency. Validate on AKS staging with the same values chain, Helm version, and admission policies as production. Store rendered manifests per release revision for incident review, and add helm template plus policy checks in CI. Senior interviews expect trade-offs, failure modes, and how GitOps, Helm history, and

**Q:** What is the first command or dashboard you check when this misbehaves on AKS?
**A:** I start with `helm status <release> -n <ns>` and `helm history` to see if a recent upgrade correlates with the incident. Then `kubectl get pods -l app.kubernetes.io/instance=<release>` and `kubectl describe` the failing pod for events—ImagePullBackOff, OOMKilled, probe failures. Spring-specific: `kubectl logs` for datasource or Flyway errors; compare `helm get values` against expected profile. If JVM OOM, check limits vs requests and whether HPA scaled beyond node capacity. For config issues, `helm template` locally with prod values (redacted) and diff against live manifest. Document findings with revision number before rollback so postmortem can reference exact chart+image combo.

#### Scenario probe
**Situation:** Interviewer: 'All pods Not Ready during deploy but process is up.'

**Model answer:** Check readiness probe path and Spring health groups—likely DB check failing readiness. Review startup vs readiness timing. Suggest splitting liveness/readiness and temporary lenient readiness during migration windows.

---

### 17. Wrong liveness = restart loop.

**Short answer:** Aggressive liveness on slow or blocking health endpoint causes CrashLoopBackOff restart storm. Senior interviews expect production trade-offs, failure modes, and Spring API integration—not isolated trivia.

#### What it is
Liveness failure triggers kubelet restart. If Spring health blocks on DB or GC pause exceeds timeout, kubelet kills pod repeatedly. Looks like app bug but is probe misconfiguration.

#### How it works (internals)
Add startupProbe with generous failureThreshold. Use dedicated liveness group excluding external deps. Increase timeoutSeconds for JVM pauses.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### When to use / when NOT to use
Incident: CrashLoopBackOff with logs showing mid-startup kill or healthy then restart.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Production example
Load test probes under GC pressure. Document probe settings in Helm values per service size.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Common mistakes
- initialDelaySeconds only without startupProbe on large apps
- Liveness hitting /actuator/health with all indicators
- periodSeconds too low for JVM
- Copy-paste probe values from tiny service to heap-heavy service

#### Interview follow-ups (with model answers)

**Q:** How do you debug probe-induced restarts?
**A:** kubectl describe pod shows Liveness probe failed events and Last State with exit codes. Compare logs from the current container and kubectl logs --previous for the crash before restart. Temporarily widen probe thresholds or add a startupProbe in a staging namespace—never leave prod probes disabled. Exec or kubectl debug with curl against the management port to hit the exact probe path and port. Distinguish OOMKilled (memory limit) from liveness failures; they present similarly in CrashLoopBackOff but require different Helm values fixes.

**Q:** What is the first command or dashboard you check when this misbehaves on AKS?
**A:** I start with `helm status <release> -n <ns>` and `helm history` to see if a recent upgrade correlates with the incident. Then `kubectl get pods -l app.kubernetes.io/instance=<release>` and `kubectl describe` the failing pod for events—ImagePullBackOff, OOMKilled, probe failures. Spring-specific: `kubectl logs` for datasource or Flyway errors; compare `helm get values` against expected profile. If JVM OOM, check limits vs requests and whether HPA scaled beyond node capacity. For config issues, `helm template` locally with prod values (redacted) and diff against live manifest. Document findings with revision number before rollback so postmortem can reference exact chart+image combo.

#### Scenario probe
**Situation:** Interviewer: 'Service CrashLoopBackOff after Helm change—only probes changed.'

**Model answer:** Identify liveness too aggressive or now hitting readiness-only endpoint. Recommend startupProbe, separate liveness group, and verify actuator exposure in chart values.

---

### 18. Resources: requests vs limits.

**Short answer:** Requests schedule pods and drive HPA; limits cap usage—OOMKill when memory limit exceeded. Senior interviews expect production trade-offs, failure modes, and Spring API integration—not isolated trivia.

#### What it is
requests: guaranteed resources for scheduling on AKS nodes. limits: maximum CPU throttle and memory kill threshold. CPU is compressible; memory is not—exceed limit → OOMKilled.

#### How it works (internals)
Helm values resources.requests/limits for Spring container. Size requests from load test; limits often memory = heap + metaspace + native + headroom.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### When to use / when NOT to use
Always set requests in prod for reliable scheduling and HPA. Limits mandatory on multi-tenant AKS with ResourceQuota.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Production example
Monitor JVM heap vs container memory with Micrometer/Prometheus. Align -Xmx leaving ~25-30% for non-heap in container limit.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Common mistakes
- Limits without requests
- request == limit for Java (no burst, still OOM risk)
- Ignoring sidecar memory in pod total
- HPA on CPU when app is memory-bound

#### Interview follow-ups (with model answers)

**Q:** Should Java requests equal limits?
**A:** Equal requests and limits give Guaranteed QoS class, reducing eviction likelihood on congested AKS nodes. Burstable QoS (request lower than limit) is common for Java when you monitor heap and accept some burst headroom. Guaranteed can waste capacity if you size for peak heap that rarely occurs. Pick per tier: critical payment services may prefer Guaranteed; internal tools may use Burstable with tight alerting. Either way, set requests so HPA and cluster autoscaler see honest scheduling demand—missing requests break autoscaling math entirely.

**Q:** What is the first command or dashboard you check when this misbehaves on AKS?
**A:** I start with `helm status <release> -n <ns>` and `helm history` to see if a recent upgrade correlates with the incident. Then `kubectl get pods -l app.kubernetes.io/instance=<release>` and `kubectl describe` the failing pod for events—ImagePullBackOff, OOMKilled, probe failures. Spring-specific: `kubectl logs` for datasource or Flyway errors; compare `helm get values` against expected profile. If JVM OOM, check limits vs requests and whether HPA scaled beyond node capacity. For config issues, `helm template` locally with prod values (redacted) and diff against live manifest. Document findings with revision number before rollback so postmortem can reference exact chart+image combo.

#### Scenario probe
**Situation:** Interviewer: 'Pods pending after increasing replicas.'

**Model answer:** Insufficient cluster capacity for sum of requests. Check kubectl describe pod events, AKS node pool autoscaling, and whether requests were raised in Helm values.

---

### 19. OOMKilled Java.

**Short answer:** Java OOMKilled when container memory limit < heap + metaspace + threads + direct buffers + JVM overhead. Senior interviews expect production trade-offs, failure modes, and Spring API integration—not isolated trivia.

#### What it is
Kubernetes kills container on memory limit breach, exit 137. JVM -Xmx does not include native memory, metaspace, thread stacks, GC overhead, or off-heap buffers.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### How it works (internals)
Set container memory limit with headroom above -Xmx. Use CONTAINER_SUPPORT or JDK ergonomics for cgroup awareness. Helm values: jvmOpts and resources.limits.memory coordinated.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### When to use / when NOT to use
OOMKilled in describe pod, works locally with same Xmx but no cgroup limit.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Production example
Track container_memory_working_set_bytes vs limit. Consider Vertical Pod Autoscaler recommendations for Java heap tuning on AKS.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Common mistakes
- Xmx equals memory limit
- No monitoring of non-heap growth
- Ignoring Spring Boot 3 native image different profile
- Raising only heap without limit

#### Interview follow-ups (with model answers)

**Q:** How do you pick memory limit for Spring Boot?
**A:** Load test representative traffic until heap and metaspace stabilize, then set container memory limit to heap peak plus non-heap overhead plus twenty to thirty percent headroom. Set -Xmx or MaxRAMPercentage to roughly seventy to seventy-five percent of the limit so the kernel OOM killer does not strike first. Include sidecar proxies in the pod limit when Istio or Linkerd injects containers. Validate under Flyway migration, warm caches, and peak concurrency on AKS staging before promoting values changes. Revisit after major dependency upgrades—Netty, gRPC, and native buffers change off-heap footprint silently.

**Q:** What is the first command or dashboard you check when this misbehaves on AKS?
**A:** I start with `helm status <release> -n <ns>` and `helm history` to see if a recent upgrade correlates with the incident. Then `kubectl get pods -l app.kubernetes.io/instance=<release>` and `kubectl describe` the failing pod for events—ImagePullBackOff, OOMKilled, probe failures. Spring-specific: `kubectl logs` for datasource or Flyway errors; compare `helm get values` against expected profile. If JVM OOM, check limits vs requests and whether HPA scaled beyond node capacity. For config issues, `helm template` locally with prod values (redacted) and diff against live manifest. Document findings with revision number before rollback so postmortem can reference exact chart+image combo.

#### Scenario probe
**Situation:** Interviewer: 'Java pod OOMKilled but heap dump shows plenty of free heap.'

**Model answer:** Explain native/metaspace/direct memory outside heap. Raise limit or reduce Xmx, enable native memory tracking, review Netty/direct buffers and class loaders.

---

### 20. Service types.

**Short answer:** Service types: ClusterIP (internal), NodePort, LoadBalancer (AKS public/internal LB), ExternalName. Senior interviews expect production trade-offs, failure modes, and Spring API integration—not isolated trivia.

#### What it is
ClusterIP default—stable VIP for in-cluster access to Spring pods. LoadBalancer provisions Azure LB on AKS for external traffic. NodePort exposes on node IPs—usually avoided in favor of Ingress/Gateway.

#### How it works (internals)
Helm Service type ClusterIP for east-west; Ingress or Gateway API for HTTP north-south. annotations for internal LB on AKS: service.beta.kubernetes.io/azure-load-balancer-internal.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### When to use / when NOT to use
ClusterIP + Ingress for public HTTP APIs. LoadBalancer for TCP services or when Ingress not used.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Production example
Prefer private ingress on internal LB for corporate APIs. Document sessionAffinity if sticky sessions required (prefer stateless JWT).  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Common mistakes
- LoadBalancer per microservice (cost and IP sprawl)
- Wrong targetPort vs Spring server.port
- Forgetting named port for Istio
- Public LB for admin actuator

#### Interview follow-ups (with model answers)

**Q:** ClusterIP vs headless Service?
**A:** A standard ClusterIP Service provides a virtual IP and kube-proxy or dataplane load balancing to ready pod endpoints. A headless Service sets clusterIP: None and returns DNS A records pointing directly to pod IPs—used for StatefulSet peer discovery. Typical stateless Spring Boot Deployments use ClusterIP; clients resolve the Service name and connect to any ready pod. Headless is wrong for ordinary REST microservices unless you need per-pod DNS for debugging or custom client-side selection. Helm charts should default to ClusterIP and expose ingress or Gateway API for north-south HTTP on AKS.

**Q:** What is the first command or dashboard you check when this misbehaves on AKS?
**A:** I start with `helm status <release> -n <ns>` and `helm history` to see if a recent upgrade correlates with the incident. Then `kubectl get pods -l app.kubernetes.io/instance=<release>` and `kubectl describe` the failing pod for events—ImagePullBackOff, OOMKilled, probe failures. Spring-specific: `kubectl logs` for datasource or Flyway errors; compare `helm get values` against expected profile. If JVM OOM, check limits vs requests and whether HPA scaled beyond node capacity. For config issues, `helm template` locally with prod values (redacted) and diff against live manifest. Document findings with revision number before rollback so postmortem can reference exact chart+image combo.

#### Scenario probe
**Situation:** Interviewer: 'How does traffic reach Spring pods from internet on AKS?'

**Model answer:** Ingress or Application Gateway Ingress Controller terminates TLS, routes to Service ClusterIP, kube-proxy/CNI forwards to pod IPs on containerPort. Mention readiness removes unhealthy endpoints.

---

### 21. Ingress vs Gateway API vs Service mesh.

**Short answer:** Ingress is L7 routing; Gateway API is successor model; mesh adds L7 policy, mTLS, observability between services. Senior interviews expect production trade-offs, failure modes, and Spring API integration—not isolated trivia.

#### What it is
Ingress (nginx, AGIC) routes external HTTP to Services via rules and TLS. Gateway API separates Gateway and HTTPRoute resources with better role separation. Service mesh (Istio/Linkerd) injects sidecars for traffic management, security, and telemetry.

#### How it works (internals)
Helm chart templates Ingress or HTTPRoute referencing Service. Mesh via namespace labels and sidecar injection annotations in pod template.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### When to use / when NOT to use
Ingress/Gateway for north-south. Mesh when you need mTLS, fine-grained retries, or unified observability east-west.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Production example
AGIC on AKS integrates with Azure Application Gateway. Mesh adds CPU/memory—justify for regulated mTLS, not hello-world APIs.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Common mistakes
- Ingress + mesh retries doubling timeout chaos
- Wrong Ingress class on AKS
- Mesh on without tuning Java connection pools
- Gateway API CRDs not installed before chart deploy

#### Interview follow-ups (with model answers)

**Q:** Do you need a mesh for Spring on AKS?
**A:** Many Spring platforms on AKS start without a mesh: Ingress or Gateway API for north-south, Micrometer tracing, and mTLS at the edge suffice. A mesh adds uniform east-west mTLS, retries, and traffic shifting without changing application code—valuable in regulated industries. Cost is sidecar CPU and memory on every pod, operational complexity, and tuning Spring connection pools for proxy latency. Adopt when compliance mandates service-to-service encryption or you need canary traffic management beyond Ingress weights. Pilot on non-critical services, measure overhead, then standardize namespace labels and Helm resource bumps.

**Q:** What is the first command or dashboard you check when this misbehaves on AKS?
**A:** I start with `helm status <release> -n <ns>` and `helm history` to see if a recent upgrade correlates with the incident. Then `kubectl get pods -l app.kubernetes.io/instance=<release>` and `kubectl describe` the failing pod for events—ImagePullBackOff, OOMKilled, probe failures. Spring-specific: `kubectl logs` for datasource or Flyway errors; compare `helm get values` against expected profile. If JVM OOM, check limits vs requests and whether HPA scaled beyond node capacity. For config issues, `helm template` locally with prod values (redacted) and diff against live manifest. Document findings with revision number before rollback so postmortem can reference exact chart+image combo.

#### Scenario probe
**Situation:** Interviewer: 'Ingress vs service mesh for new Spring platform?'

**Model answer:** Start with Ingress/Gateway for external traffic and Spring observability libraries. Add mesh when mTLS east-west or canary at L7 without app changes is a hard requirement.

---

### 22. ConfigMap / Secret vs Spring config.

**Short answer:** ConfigMap/Secret inject env or files; Spring Cloud Kubernetes or config server can layer over static mounts. Senior interviews expect production trade-offs, failure modes, and Spring API integration—not isolated trivia.

#### What it is
Helm renders ConfigMap with application.yml snippets; Secret for credentials. Mount via envFrom, volumeMount, or spring.config.import=kubernetes:. Spring Cloud Config centralizes dynamic config; K8s native suits GitOps Helm values.

#### How it works (internals)
Chart templates ConfigMap data from values; Deployment env SPRING_CONFIG_ADDITIONAL_LOCATION. Reloader operator restarts on ConfigMap change if needed.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### When to use / when NOT to use
Static per-env config in Helm values → ConfigMap. Frequent dynamic toggles → config server or feature flag service.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Production example
Don't put secrets in ConfigMap. Version config with chart; hot reload via Spring @RefreshScope only if architected.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Common mistakes
- Huge ConfigMap over 1MB limit
- Secret in ConfigMap for 'convenience'
- Config change without rollout strategy
- Duplicating same property in env and file

#### Interview follow-ups (with model answers)

**Q:** How does Spring pick up Helm-rendered ConfigMap?
**A:** Mount application-env.yaml into /config and set SPRING_CONFIG_ADDITIONAL_LOCATION=/config/ so Spring merges file properties over jar defaults. Alternatively use spring.config.import=kubernetes: when running Spring Cloud Kubernetes on AKS. Helm values drive ConfigMap keys per environment; changing ConfigMap does not always reload beans unless @RefreshScope or Reloader triggers rollout. Keep secrets out of ConfigMaps—use Secret references for credentials. Document which properties are image-baked versus Helm-supplied so developers know where to change datasource URLs. Validate on AKS staging with the same values chain, Helm version, and admission policies as production. Store rendered manifests per release revision for incident review, and add helm template plus policy checks in CI. Senior interviews expect trade-offs, failure modes, and how GitOps, Helm history, and Spring observability connect.

**Q:** What is the first command or dashboard you check when this misbehaves on AKS?
**A:** I start with `helm status <release> -n <ns>` and `helm history` to see if a recent upgrade correlates with the incident. Then `kubectl get pods -l app.kubernetes.io/instance=<release>` and `kubectl describe` the failing pod for events—ImagePullBackOff, OOMKilled, probe failures. Spring-specific: `kubectl logs` for datasource or Flyway errors; compare `helm get values` against expected profile. If JVM OOM, check limits vs requests and whether HPA scaled beyond node capacity. For config issues, `helm template` locally with prod values (redacted) and diff against live manifest. Document findings with revision number before rollback so postmortem can reference exact chart+image combo.

#### Scenario probe
**Situation:** Interviewer: 'Move properties from JAR to Helm—how?'

**Model answer:** Externalize environment-specific keys to values.yaml → ConfigMap template; keep defaults in application.yml inside image; mount additional location; secrets via Secret ref only.

---

### 23. Rolling update vs recreate vs blue/green vs canary.

**Short answer:** Rolling update default; recreate downtime; blue/green and canary reduce risk with traffic switching. Senior interviews expect production trade-offs, failure modes, and Spring API integration—not isolated trivia.

#### What it is
RollingUpdate gradually replaces pods (Deployment strategy). Recreate kills all then starts new—brief outage. Blue/green runs two full stacks, switches traffic. Canary sends small % to new version via Ingress/mesh/Argo Rollouts.

#### How it works (internals)
Helm values: strategy type, maxSurge, maxUnavailable. Advanced: Argo Rollouts chart or Flagger with Istio/Contour on AKS.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### When to use / when NOT to use
Rolling for backward-compatible Spring releases. Canary when schema/API risk needs measured exposure.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Production example
Combine with PDB and readiness. Database migrations must support old and new code during roll.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Common mistakes
- maxUnavailable 100% during peak
- Canary without metric rollback automation
- Recreate on stateful session apps without planning
- Two Helm releases same labels (blue/green collision)

#### Interview follow-ups (with model answers)

**Q:** How do you canary a Helm-deployed Spring service?
**A:** Option A: deploy two Helm releases with weighted Ingress or Gateway API HTTPRoute rules splitting traffic by percentage. Option B: replace Deployment with Argo Rollouts, using Helm to install the Rollout manifest and analysis templates on Prometheus error rates. Helm deploys stable chart versions; the rollout controller steps canary weight and auto-aborts on SLO breach. Ensure Spring metrics and health checks align with analysis queries—5xx rate and latency percentiles need consistent labels. Database migrations must remain backward compatible throughout the canary window on AKS.

**Q:** What is the first command or dashboard you check when this misbehaves on AKS?
**A:** I start with `helm status <release> -n <ns>` and `helm history` to see if a recent upgrade correlates with the incident. Then `kubectl get pods -l app.kubernetes.io/instance=<release>` and `kubectl describe` the failing pod for events—ImagePullBackOff, OOMKilled, probe failures. Spring-specific: `kubectl logs` for datasource or Flyway errors; compare `helm get values` against expected profile. If JVM OOM, check limits vs requests and whether HPA scaled beyond node capacity. For config issues, `helm template` locally with prod values (redacted) and diff against live manifest. Document findings with revision number before rollback so postmortem can reference exact chart+image combo.

#### Scenario probe
**Situation:** Interviewer: 'Zero-downtime deploy requirements for payments API?'

**Model answer:** Rolling update with readiness, PDB minAvailable 1+, backward-compatible migrations, optional canary with automated rollback on 5xx rate. Mention probe and connection draining.

---

### 24. PDB (PodDisruptionBudget).

**Short answer:** PDB limits voluntary disruptions so node drains/upgrades don't take all pods offline. Senior interviews expect production trade-offs, failure modes, and Spring API integration—not isolated trivia.

#### What it is
PodDisruptionBudget specifies minAvailable or maxUnavailable during voluntary evictions (node drain, cluster upgrade). Does not stop involuntary failures or Deployment rollouts the same way.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### How it works (internals)
Helm template PDB with minAvailable: 1 or maxUnavailable: 1 for N-replica Spring service. Match selector labels to Deployment.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### When to use / when NOT to use
Any production service with >1 replica on AKS node pool maintenance windows.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Production example
Coordinate PDB with HPA min replicas. AKS upgrades respect PDB but can block drain if misconfigured.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Common mistakes
- PDB minAvailable equal replicas blocks all drains
- No PDB on critical service
- Selector mismatch makes PDB ineffective
- Ignoring PDB during forced node pool rotation

#### Interview follow-ups (with model answers)

**Q:** PDB vs rolling update interaction?
**A:** Rolling updates are Deployment-controller driven and generally proceed even when PDB exists, subject to maxUnavailable on the Deployment strategy. PDB primarily blocks voluntary evictions during node drain, cluster upgrade, or kubectl drain on AKS. If PDB minAvailable equals desired replicas and a drain is attempted, the operation stalls until pods reschedule—often mistaken for a broken rollout. Align PDB minAvailable, replica count, and HPA minReplicas so maintenance and autoscaling do not deadlock. Test node pool upgrades on staging with identical PDB settings before production maintenance windows.

**Q:** What is the first command or dashboard you check when this misbehaves on AKS?
**A:** I start with `helm status <release> -n <ns>` and `helm history` to see if a recent upgrade correlates with the incident. Then `kubectl get pods -l app.kubernetes.io/instance=<release>` and `kubectl describe` the failing pod for events—ImagePullBackOff, OOMKilled, probe failures. Spring-specific: `kubectl logs` for datasource or Flyway errors; compare `helm get values` against expected profile. If JVM OOM, check limits vs requests and whether HPA scaled beyond node capacity. For config issues, `helm template` locally with prod values (redacted) and diff against live manifest. Document findings with revision number before rollback so postmortem can reference exact chart+image combo.

#### Scenario probe
**Situation:** Interviewer: 'Node drain stuck on Spring pods.'

**Model answer:** Check PDB minAvailable vs ready replicas, pod readiness, and PodDisruptionConditions. May need temporary PDB adjustment or scale up replicas before drain.

---

### 25. HPA.

**Short answer:** HPA scales Deployment replicas based on CPU, memory, or custom metrics from metrics-server/Prometheus. Senior interviews expect production trade-offs, failure modes, and Spring API integration—not isolated trivia.

#### What it is
HorizontalPodAutoscaler watches metrics and adjusts spec.replicas within min/max. Requires requests on containers for resource metrics. Custom metrics need Prometheus adapter or similar on AKS.

#### How it works (internals)
Helm values autoscaling.enabled, minReplicas, maxReplicas, targetCPUUtilization. Omit static replicas when HPA enabled.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### When to use / when NOT to use
Variable load Spring APIs—business hours spikes, flash sales.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Production example
Set sensible min for HA. Cooldown/stabilization prevents flapping. Memory HPA for Java needs careful JVM warmup behavior.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Common mistakes
- HPA without resource requests
- Fixed replicas in Deployment fighting HPA
- CPU target on I/O bound service
- maxReplicas below PDB minAvailable math error

#### Interview follow-ups (with model answers)

**Q:** HPA on memory for Java—gotchas?
**A:** JVM heap grows gradually toward steady state, so memory-based HPA reacts slower than CPU for bursty Java workloads. Without accurate memory requests, HPA cannot compute utilization percentages and appears broken. Combine memory HPA with VPA recommendations or periodic rightsizing PRs updating Helm values. Prefer custom metrics—request latency, queue depth, or Tomcat thread pool—when CPU and memory misrepresent saturation. Cold starts during scale-out can trigger false scale events if startup probes and stabilization windows are not tuned on AKS. Validate on AKS staging with the same values chain, Helm version, and admission policies as production. Store rendered manifests per release revision for incident review, and add helm template plus policy checks in CI. Senior interviews expect trade-offs, failure modes, and how

**Q:** What is the first command or dashboard you check when this misbehaves on AKS?
**A:** I start with `helm status <release> -n <ns>` and `helm history` to see if a recent upgrade correlates with the incident. Then `kubectl get pods -l app.kubernetes.io/instance=<release>` and `kubectl describe` the failing pod for events—ImagePullBackOff, OOMKilled, probe failures. Spring-specific: `kubectl logs` for datasource or Flyway errors; compare `helm get values` against expected profile. If JVM OOM, check limits vs requests and whether HPA scaled beyond node capacity. For config issues, `helm template` locally with prod values (redacted) and diff against live manifest. Document findings with revision number before rollback so postmortem can reference exact chart+image combo.

#### Scenario probe
**Situation:** Interviewer: 'HPA not scaling despite high CPU.'

**Model answer:** Check metrics-server, missing requests, wrong scaleTargetRef, or replicas already at max. Describe HPA for conditions. Verify AKS monitor metrics pipeline if using custom metrics.

---

### 26. NetworkPolicy.

**Short answer:** NetworkPolicy restricts pod ingress/egress—default allow becomes deny-by-policy for zero trust. Senior interviews expect production trade-offs, failure modes, and Spring API integration—not isolated trivia.

#### What it is
L4 rules select pods by labels and allow/deny traffic to namespaces, CIDRs, or ports. Requires CNI supporting NetworkPolicy on AKS (Azure CNI with policy addon or Calico).  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### How it works (internals)
Helm optional NetworkPolicy template: allow ingress from ingress namespace and same app; egress to kube-dns, Azure SQL IP range, Key Vault if needed.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### When to use / when NOT to use
Regulated environments, multi-tenant namespaces, limiting lateral movement.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Production example
Enable policy addon at AKS create or upgrade. Test DNS and APM egress before enforcing deny-all default.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Common mistakes
- Deny-all without allowing DNS (53/udp)
- Blocking Azure Monitor or ACR pulls incorrectly
- Policies not applied because CNI lacks support
- Forgetting health probe paths from kubelet (host network nuances)

#### Interview follow-ups (with model answers)

**Q:** How does NetworkPolicy affect Spring calling Azure SQL?
**A:** NetworkPolicy egress rules must allow TCP 1433 to your SQL subnet, private endpoint IP range, or approved CIDR. Azure SQL with private link changes target addresses—policies hardcoded to public IPs fail silently after migration. Allow DNS egress to kube-system on UDP port 53 or CoreDNS resolution breaks before SQL is reached. Validate from an app pod using kubectl debug and netshoot before enforcing deny-by-default policies. Document required egress in Helm values comments so application teams know constraints when onboarding to shared AKS namespaces.

**Q:** What is the first command or dashboard you check when this misbehaves on AKS?
**A:** I start with `helm status <release> -n <ns>` and `helm history` to see if a recent upgrade correlates with the incident. Then `kubectl get pods -l app.kubernetes.io/instance=<release>` and `kubectl describe` the failing pod for events—ImagePullBackOff, OOMKilled, probe failures. Spring-specific: `kubectl logs` for datasource or Flyway errors; compare `helm get values` against expected profile. If JVM OOM, check limits vs requests and whether HPA scaled beyond node capacity. For config issues, `helm template` locally with prod values (redacted) and diff against live manifest. Document findings with revision number before rollback so postmortem can reference exact chart+image combo.

#### Scenario probe
**Situation:** Interviewer: 'After NetworkPolicy, app cannot reach database.'

**Model answer:** Audit egress rules, namespace labels on policy peers, DNS resolution path, and private link CIDRs. Iteratively widen with logging (Azure NSG flow logs) then tighten.

---

### 27. SA and RBAC.

**Short answer:** ServiceAccount identities pods; RBAC Role/ClusterRole binds permissions via RoleBinding. Senior interviews expect production trade-offs, failure modes, and Spring API integration—not isolated trivia.

#### What it is
Each pod runs with a ServiceAccount (default or chart-created). RBAC grants least privilege for API access—Spring rarely needs K8s API unless using K8s config operator.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### How it works (internals)
Helm templates ServiceAccount, optional Role for metrics or lease leader election. pod.spec.serviceAccountName reference. On AKS, use Azure Workload Identity linking SA to Entra ID app.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### When to use / when NOT to use
Apps accessing Azure Key Vault, Storage, or Service Bus via workload identity instead of secrets.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Production example
Disable automount default SA token if unused. Separate SA per microservice. Audit ClusterRoleBindings carefully.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Common mistakes
- cluster-admin for app SA
- Sharing SA across unrelated services
- Workload identity annotation missing on SA/pod
- Helm creating ClusterRole when Role suffices

#### Interview follow-ups (with model answers)

**Q:** Spring on AKS accessing Key Vault without password in Helm?
**A:** Enable workload identity on the AKS cluster and create a federated credential mapping the pod ServiceAccount to an Entra application. Grant that identity Key Vault secret get permission on the vault housing database passwords. Spring Azure SDK uses DefaultAzureCredential, which picks up workload identity in cluster. Helm templates only the ServiceAccount annotations and pod labels—no secret bytes in values.yaml or release Secrets. Rotate secrets in Key Vault; External Secrets or SDK refresh policies propagate without chart republish. Validate on AKS staging with the same values chain, Helm version, and admission policies as production. Store rendered manifests per release revision for incident review, and add helm template plus policy checks in CI. Senior interviews expect trade-offs, failure modes, and how GitOps,

**Q:** What is the first command or dashboard you check when this misbehaves on AKS?
**A:** I start with `helm status <release> -n <ns>` and `helm history` to see if a recent upgrade correlates with the incident. Then `kubectl get pods -l app.kubernetes.io/instance=<release>` and `kubectl describe` the failing pod for events—ImagePullBackOff, OOMKilled, probe failures. Spring-specific: `kubectl logs` for datasource or Flyway errors; compare `helm get values` against expected profile. If JVM OOM, check limits vs requests and whether HPA scaled beyond node capacity. For config issues, `helm template` locally with prod values (redacted) and diff against live manifest. Document findings with revision number before rollback so postmortem can reference exact chart+image combo.

#### Scenario probe
**Situation:** Interviewer: 'Pod gets 403 calling Kubernetes API.'

**Model answer:** Check SA on pod, RoleBinding scope, and whether app should use API at all. Prefer workload identity for Azure resources over broad K8s RBAC.

---

### 28. SecurityContext.

**Short answer:** SecurityContext sets pod/container privileges: runAsNonRoot, readOnlyRootFilesystem, capabilities. Senior interviews expect production trade-offs, failure modes, and Spring API integration—not isolated trivia.

#### What it is
Pod securityContext: fsGroup, seccomp. Container securityContext: runAsUser, allowPrivilegeEscalation, capabilities drop. AKS Pod Security Standards/Admission enforce baseline or restricted.

#### How it works (internals)
Helm values securityContext aligned with Spring image (non-root user in Dockerfile). readOnlyRootFilesystem with emptyDir for tmp if needed.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### When to use / when NOT to use
Compliance, restricted PSS namespaces, reducing container escape blast radius.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Production example
Test Spring with readOnly FS—logging to stdout avoids file writes. Align with distroless/eclipse-temurin non-root images.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Common mistakes
- runAsRoot required because image poorly built
- Writable root FS without reason
- Missing fsGroup for volume permissions
- Privileged sidecar for 'debugging' left on

#### Interview follow-ups (with model answers)

**Q:** How make Spring Boot work readOnlyRootFilesystem?
**A:** Log to stdout and stderr only so the container needs no writable log directory under /. Mount an emptyDir volume at /tmp and set JAVA_TOOL_OPTIONS=-Djava.io.tmpdir=/tmp for libraries that insist on temp files. Build images with a non-root USER matching securityContext runAsUser in the Helm chart. Verify Flyway, actuator, and embedded Tomcat do not require writes under /app. AKS Pod Security Standards restricted profile expects readOnlyRootFilesystem true—test in CI with the same securityContext before prod. Validate on AKS staging with the same values chain, Helm version, and admission policies as production. Store rendered manifests per release revision for incident review, and add helm template plus policy checks in CI. Senior interviews expect trade-offs, failure modes, and how GitOps, Helm history, and

**Q:** What is the first command or dashboard you check when this misbehaves on AKS?
**A:** I start with `helm status <release> -n <ns>` and `helm history` to see if a recent upgrade correlates with the incident. Then `kubectl get pods -l app.kubernetes.io/instance=<release>` and `kubectl describe` the failing pod for events—ImagePullBackOff, OOMKilled, probe failures. Spring-specific: `kubectl logs` for datasource or Flyway errors; compare `helm get values` against expected profile. If JVM OOM, check limits vs requests and whether HPA scaled beyond node capacity. For config issues, `helm template` locally with prod values (redacted) and diff against live manifest. Document findings with revision number before rollback so postmortem can reference exact chart+image combo.

#### Scenario probe
**Situation:** Interviewer: 'PSS restricted blocks our Helm deploy.'

**Model answer:** Identify violating fields—usually runAsNonRoot or capabilities. Fix container image and securityContext in chart values; avoid privileged escalation.

---

### 29. `imagePullPolicy`.

**Short answer:** imagePullPolicy IfNotPresent/Always/Never controls kubelet image cache behavior. Senior interviews expect production trade-offs, failure modes, and Spring API integration—not isolated trivia.

#### What it is
IfNotPresent pulls only if not cached locally—risky with mutable tags like latest. Always pulls every pod start—good for mutable tags, more registry load. Never uses local only.

#### How it works (internals)
Helm values image.pullPolicy: IfNotPresent with immutable tags (git SHA). Or Always with digest-pinned references.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### When to use / when NOT to use
Prod: immutable tags + IfNotPresent or digest pin. Dev: Always on latest for convenience.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Production example
ACR geo-replication and pull secrets via AKS-ACR attachment. Avoid latest tag entirely in values-prod.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Common mistakes
- latest + IfNotPresent = stale pods on different nodes
- Changing tag without rollout restart
- Missing pull secret on new node pool
- Always on high-churn fleet hammering ACR

#### Interview follow-ups (with model answers)

**Q:** Deployed new image tag but some nodes run old code?
**A:** If imagePullPolicy is IfNotPresent and you reused a mutable tag like latest, nodes with cached layers never pull the new bits. Unique immutable tags per CI build—or digest pinning—force correct artifacts. Helm upgrade must change the Deployment pod template spec or Kubernetes will not recreate pods. Run kubectl rollout restart only as a temporary fix; fix the pipeline to promote SHA or digest tags. Verify pod status.containerStatuses.imageID on multiple nodes after deploy on AKS. Validate on AKS staging with the same values chain, Helm version, and admission policies as production. Store rendered manifests per release revision for incident review, and add helm template plus policy checks in CI. Senior interviews expect trade-offs, failure modes, and how GitOps, Helm history, and

**Q:** What is the first command or dashboard you check when this misbehaves on AKS?
**A:** I start with `helm status <release> -n <ns>` and `helm history` to see if a recent upgrade correlates with the incident. Then `kubectl get pods -l app.kubernetes.io/instance=<release>` and `kubectl describe` the failing pod for events—ImagePullBackOff, OOMKilled, probe failures. Spring-specific: `kubectl logs` for datasource or Flyway errors; compare `helm get values` against expected profile. If JVM OOM, check limits vs requests and whether HPA scaled beyond node capacity. For config issues, `helm template` locally with prod values (redacted) and diff against live manifest. Document findings with revision number before rollback so postmortem can reference exact chart+image combo.

#### Scenario probe
**Situation:** Interviewer: 'Helm upgraded but pod still old jar.'

**Model answer:** Check image ID in pod spec vs ACR, pullPolicy, and whether ReplicaSet updated. Recommend SHA tags and rollout status verification in pipeline.

---

### 30. Helm + digest pinning.

**Short answer:** Pin image by digest (@sha256:...) for immutable deploys regardless of tag mutation. Senior interviews expect production trade-offs, failure modes, and Spring API integration—not isolated trivia.

#### What it is
image: myacr.azurecr.io/app@sha256:abc... uniquely identifies artifact. Tags are mutable; digests are content-addressed.

#### How it works (internals)
CI builds image, captures digest, passes to helm --set image.digest or full image string. Chart template: `{{ .Values.image.repository }}@{{ .Values.image.digest }}` when digest set.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### When to use / when NOT to use
Production promotions, compliance, reproducible rollbacks on AKS.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Production example
Store digest in deployment manifest from CI, not human-chosen tags alone. Document mapping digest → git commit in release notes.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Common mistakes
- Digest pin in values but template still uses :tag
- Rollback to revision with wrong digest unknowingly
- Not updating digest in GitOps repo on promote
- Mixing tag and digest incorrectly in image string

#### Interview follow-ups (with model answers)

**Q:** Digest pinning with Helm rollback?
**A:** Helm rollback reapplies the manifest stored in the target revision, including whatever image reference was rendered then. If that revision used an immutable digest, rollback restores exact container bits—high confidence for incident recovery. If revisions used mutable tags, rollback ambiguity remains because the tag may now point elsewhere in ACR. Best practice: CI injects digest into values on every build so each revision history entry is content-addressed. Document digest-to-git-commit mapping in release notes for auditors and on-call engineers. Validate on AKS staging with the same values chain, Helm version, and admission policies as production. Store rendered manifests per release revision for incident review, and add helm template plus policy checks in CI. Senior interviews expect trade-offs, failure modes, and how

**Q:** What is the first command or dashboard you check when this misbehaves on AKS?
**A:** I start with `helm status <release> -n <ns>` and `helm history` to see if a recent upgrade correlates with the incident. Then `kubectl get pods -l app.kubernetes.io/instance=<release>` and `kubectl describe` the failing pod for events—ImagePullBackOff, OOMKilled, probe failures. Spring-specific: `kubectl logs` for datasource or Flyway errors; compare `helm get values` against expected profile. If JVM OOM, check limits vs requests and whether HPA scaled beyond node capacity. For config issues, `helm template` locally with prod values (redacted) and diff against live manifest. Document findings with revision number before rollback so postmortem can reference exact chart+image combo.

#### Scenario probe
**Situation:** Interviewer: 'How guarantee prod runs exact tested image?'

**Model answer:** Promote by digest from staging sign-off, helm upgrade with digest in values, verify pod imageID matches. No retag of same tag for different content.

---

### 31. `kubectl` debug flow.

**Short answer:** kubectl debug creates ephemeral debug container or copy pod for live troubleshooting. Senior interviews expect production trade-offs, failure modes, and Spring API integration—not isolated trivia.

#### What it is
kubectl debug pod/name -it --image=netshoot --target=myapp attaches troubleshoot container. Or --copy-to for node debugging. Useful when distroless Spring image lacks shell.

#### How it works (internals)
Debug CrashLoop: kubectl logs previous, debug with curl against localhost management port. Share process namespace options for advanced cases.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### When to use / when NOT to use
Network/DNS issues, missing tools in app image, probe failures in running pod.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Production example
Restrict debug RBAC on prod AKS. Prefer observability over ad-hoc debug. Audit ephemeral debug containers.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Common mistakes
- Installing packages into running app container permanently
- Debug in prod without change control
- Forgetting ephemeral container disappears on restart
- Using privileged debug images routinely

#### Interview follow-ups (with model answers)

**Q:** Debug Spring Boot in distroless image?
**A:** Use kubectl debug to attach an ephemeral container such as netshoot with --target sharing the app container network namespace. From the debug container, curl localhost on the Spring management port to hit actuator endpoints the probes use. For deeper JVM insight, maintain a separate debug image tag with async-profiler or jcmd used only during incidents. Do not kubectl exec package installs into distroless app containers—they are ephemeral and non-persistent. Restrict debug RBAC on production AKS namespaces and audit ephemeral container creation.

**Q:** What is the first command or dashboard you check when this misbehaves on AKS?
**A:** I start with `helm status <release> -n <ns>` and `helm history` to see if a recent upgrade correlates with the incident. Then `kubectl get pods -l app.kubernetes.io/instance=<release>` and `kubectl describe` the failing pod for events—ImagePullBackOff, OOMKilled, probe failures. Spring-specific: `kubectl logs` for datasource or Flyway errors; compare `helm get values` against expected profile. If JVM OOM, check limits vs requests and whether HPA scaled beyond node capacity. For config issues, `helm template` locally with prod values (redacted) and diff against live manifest. Document findings with revision number before rollback so postmortem can reference exact chart+image combo.

#### Scenario probe
**Situation:** Interviewer: 'Pod has no shell—how investigate connectivity?'

**Model answer:** kubectl debug with netshoot, same network namespace, test DNS and TCP to SQL. Correlate with NetworkPolicy and private endpoint config.

---

### 32. CrashLoopBackOff Spring.

**Short answer:** CrashLoopBackOff: container exits repeatedly—check logs, probes, config, memory, and missing deps. Senior interviews expect production trade-offs, failure modes, and Spring API integration—not isolated trivia.

#### What it is
Kubelet backs off restarting after crashes. Spring causes: bad config, Flyway failure, port bind, OOM, liveness kill, missing env/Secret.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### How it works (internals)
kubectl logs pod --previous, describe pod events, check helm get manifest for env, exec/debug if possible, compare working revision with helm diff.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### When to use / when NOT to use
Post helm upgrade incident triage on AKS Spring services.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Production example
Structured logging to Azure Monitor, alert on restart count, staged rollout catches most issues.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Common mistakes
- Only checking current logs not --previous
- Ignoring ConfigMap mount errors at startup
- Assuming image pull success means app healthy
- Scaling replicas instead of fixing crash

#### Interview follow-ups (with model answers)

**Q:** CrashLoop only in prod not staging?
**A:** Compare helm get values -a between environments: Spring profile, datasource URLs, feature flags, and resource limits often differ. Production may enforce NetworkPolicy, Pod Security Standards, or workload identity that staging lacks. Key Vault RBAC or private endpoint DNS may work in staging public networking but fail in prod VNet integration. Secrets referenced in prod ExternalSecret may be missing or wrong version. Reproduce with prod values on a staging namespace before changing production Helm revisions again. Validate on AKS staging with the same values chain, Helm version, and admission policies as production. Store rendered manifests per release revision for incident review, and add helm template plus policy checks in CI. Senior interviews expect trade-offs, failure modes, and how GitOps, Helm history,

**Q:** What is the first command or dashboard you check when this misbehaves on AKS?
**A:** I start with `helm status <release> -n <ns>` and `helm history` to see if a recent upgrade correlates with the incident. Then `kubectl get pods -l app.kubernetes.io/instance=<release>` and `kubectl describe` the failing pod for events—ImagePullBackOff, OOMKilled, probe failures. Spring-specific: `kubectl logs` for datasource or Flyway errors; compare `helm get values` against expected profile. If JVM OOM, check limits vs requests and whether HPA scaled beyond node capacity. For config issues, `helm template` locally with prod values (redacted) and diff against live manifest. Document findings with revision number before rollback so postmortem can reference exact chart+image combo.

#### Scenario probe
**Situation:** Interviewer: 'Spring service CrashLoop after helm upgrade—steps?'

**Model answer:** Previous logs, describe events, rollback if needed, diff manifest env and secrets, verify datasource URL and Flyway, check probes and memory limits.

---

### 33. `helm get manifest` / `history` / `diff`.

**Short answer:** helm get manifest/history shows deployed state; helm diff plugin previews upgrade changes. Senior interviews expect production trade-offs, failure modes, and Spring API integration—not isolated trivia.

#### What it is
helm get manifest <rev> outputs rendered resources for a revision. helm history lists revisions with status. helm diff upgrade compares live cluster or last release to new render.

#### How it works (internals)
Pre-upgrade: `helm diff upgrade rel chart -f prod.yaml`. Post-incident: compare manifest rev N vs N-1 for Deployment, ConfigMap, probes.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### When to use / when NOT to use
Change review, incident analysis, GitOps drift investigation.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Production example
Integrate diff in CI approval gates. Store rendered manifests as artifacts per release.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Common mistakes
- Upgrading without diff on prod
- Diff only chart not values files used in CI
- Ignoring Secret data changes in diff output
- Not specifying revision in get manifest

#### Interview follow-ups (with model answers)

**Q:** helm diff vs argocd app diff?
**A:** helm diff compares the currently deployed Helm release manifest to a newly rendered upgrade, surfacing Deployment, ConfigMap, and probe changes. argocd app diff compares Git-declared desired state to live cluster resources, including drift from manual kubectl edits. In GitOps-first AKS platforms, Argo diff is authoritative for reconciliation health. helm diff remains valuable for local chart development and Jenkins-style pipelines that call helm upgrade directly. Use both lenses during incidents: Argo shows Git drift; helm history shows revision-to-revision manifest evolution. Validate on AKS staging with the same values chain, Helm version, and admission policies as production. Store rendered manifests per release revision for incident review, and add helm template plus policy checks in CI. Senior interviews expect trade-offs, failure modes, and

**Q:** What is the first command or dashboard you check when this misbehaves on AKS?
**A:** I start with `helm status <release> -n <ns>` and `helm history` to see if a recent upgrade correlates with the incident. Then `kubectl get pods -l app.kubernetes.io/instance=<release>` and `kubectl describe` the failing pod for events—ImagePullBackOff, OOMKilled, probe failures. Spring-specific: `kubectl logs` for datasource or Flyway errors; compare `helm get values` against expected profile. If JVM OOM, check limits vs requests and whether HPA scaled beyond node capacity. For config issues, `helm template` locally with prod values (redacted) and diff against live manifest. Document findings with revision number before rollback so postmortem can reference exact chart+image combo.

#### Scenario probe
**Situation:** Interviewer: 'How know what changed in last prod deploy?'

**Model answer:** helm history, get manifest for rev, diff revisions or CI artifact, cross-check git commit and image digest in deployment record.

---

### 34. `helm rollback` vs GitOps revert.

**Short answer:** helm rollback restores cluster revision fast; GitOps revert fixes source of truth and prevents re-drift. Senior interviews expect production trade-offs, failure modes, and Spring API integration—not isolated trivia.

#### What it is
Rollback is operational, cluster-local, immediate. Git revert changes desired state in Git; Argo CD syncs back to good config permanently.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### How it works (internals)
Incident: helm rollback for speed, then git revert bad commit, Argo sync, verify auto-sync won't redeploy bad.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### When to use / when NOT to use
Any GitOps-managed AKS environment—always pair emergency rollback with Git fix.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Production example
Disable auto-sync during incident if needed. Document runbook: rollback then revert within SLA.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Common mistakes
- Rollback only—Argo resyncs bad commit
- Git revert without checking DB migrations
- Assuming rollback fixes forward bug in chart template in Git
- No communication between ops helm rollback and dev Git revert

#### Interview follow-ups (with model answers)

**Q:** Argo CD OutOfSync after helm rollback?
**A:** After manual helm rollback, live cluster matches an older revision while Git still contains the bad commit—Argo reports OutOfSync. Either revert Git to the rolled-back configuration or deploy a forward fix and sync intentionally. Temporary sync windows or application overrides may be needed during incidents but must be time-boxed. Goal is converging Git, Helm release history, and cluster state so auto-sync does not redeploy the failure. Communicate between on-call doing helm rollback and developers reverting pull requests on the AKS GitOps repo.

**Q:** What is the first command or dashboard you check when this misbehaves on AKS?
**A:** I start with `helm status <release> -n <ns>` and `helm history` to see if a recent upgrade correlates with the incident. Then `kubectl get pods -l app.kubernetes.io/instance=<release>` and `kubectl describe` the failing pod for events—ImagePullBackOff, OOMKilled, probe failures. Spring-specific: `kubectl logs` for datasource or Flyway errors; compare `helm get values` against expected profile. If JVM OOM, check limits vs requests and whether HPA scaled beyond node capacity. For config issues, `helm template` locally with prod values (redacted) and diff against live manifest. Document findings with revision number before rollback so postmortem can reference exact chart+image combo.

#### Scenario probe
**Situation:** Interviewer: 'Bad deploy via Argo—rollback strategy?'

**Model answer:** Revert Git commit or pin previous image digest in values, sync Argo. Optional helm rollback if manual helm involved. Ensure migrations compatible with rolled-back app.

---

### 35. Chart testing.

**Short answer:** Chart testing: helm lint, chart-testing (ct), helm test hooks, and policy validation in CI. Senior interviews expect production trade-offs, failure modes, and Spring API integration—not isolated trivia.

#### What it is
helm lint checks chart structure and syntax. chart-testing installs chart on kind cluster, runs tests, checks version bump. helm test runs test pods defined in chart.

#### How it works (internals)
ct lint-and-install with kind on PR. Spring chart test pod curls /actuator/health. kubeconform + conftest policies on rendered YAML.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### When to use / when NOT to use
Shared platform charts and any service chart with multiple consumers.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Production example
Version bump enforcement, maintain chart-test values for minimal install, smoke test against staging AKS before prod promote.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Common mistakes
- Lint only, never install test
- Tests requiring prod secrets
- Flaky helm test without retries
- No test for required values failure

#### Interview follow-ups (with model answers)

**Q:** What does chart-testing ct install do?
**A:** chart-testing spins up an ephemeral kind cluster, installs the chart with test values, waits for workloads to become ready, runs helm test, then uninstalls. It catches RBAC mistakes, probe misconfiguration, and broken dependencies that helm lint alone misses. ct also enforces chart version bumps on changed charts in pull requests. Pipeline runtime is minutes—acceptable for shared platform charts consumed by dozens of Spring services on AKS. Pair ct with kubeconform against the target Kubernetes version schema for API deprecation safety.

**Q:** What is the first command or dashboard you check when this misbehaves on AKS?
**A:** I start with `helm status <release> -n <ns>` and `helm history` to see if a recent upgrade correlates with the incident. Then `kubectl get pods -l app.kubernetes.io/instance=<release>` and `kubectl describe` the failing pod for events—ImagePullBackOff, OOMKilled, probe failures. Spring-specific: `kubectl logs` for datasource or Flyway errors; compare `helm get values` against expected profile. If JVM OOM, check limits vs requests and whether HPA scaled beyond node capacity. For config issues, `helm template` locally with prod values (redacted) and diff against live manifest. Document findings with revision number before rollback so postmortem can reference exact chart+image combo.

#### Scenario probe
**Situation:** Interviewer: 'How test Helm charts before prod?'

**Model answer:** Pipeline: lint, template with prod fixture, policy check, ct install on kind, optional staging AKS deploy with synthetic traffic on actuator.

---

### 36. Named templates and labels.

**Short answer:** Named templates in _helpers.tpl standardize names and recommended labels across all resources. Senior interviews expect production trade-offs, failure modes, and Spring API integration—not isolated trivia.

#### What it is
Templates like `fullname`, `labels`, `selectorLabels` ensure Deployment, Service, HPA share app.kubernetes.io/name, instance, version labels per Helm best practices.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### How it works (internals)
Define in _helpers.tpl; include in every resource metadata and spec.selector. Use `helm.sh/chart` label with chart version escaped.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### When to use / when NOT to use
Any chart with more than one resource—prevents selector mismatches and aids Prometheus/Grafana queries.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Production example
Consistent labels enable network policies, cost allocation, and AKS monitor service maps.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Common mistakes
- Different selector labels on Service vs Deployment
- Changing selector labels on upgrade (immutable)
- Omitting version label for tracking releases
- Overlong names exceeding DNS limits

#### Interview follow-ups (with model answers)

**Q:** Why is selector immutability important?
**A:** Deployment spec.selector is immutable after creation—Kubernetes rejects changes to matchLabels keys or values. If a chart refactor changes selectorLabels helpers, helm upgrade fails or leaves orphaned ReplicaSets with no endpoints. Treat selector keys as permanent API contracts when naming charts for Spring microservices. You may add new labels in metadata without touching spec.selector.matchLabels. Recovery requires a new Deployment identity or blue/green release name—plan selector design on day one of the Helm chart. Validate on AKS staging with the same values chain, Helm version, and admission policies as production. Store rendered manifests per release revision for incident review, and add helm template plus policy checks in CI. Senior interviews expect trade-offs, failure modes, and how GitOps, Helm history, and Spring observability

**Q:** What is the first command or dashboard you check when this misbehaves on AKS?
**A:** I start with `helm status <release> -n <ns>` and `helm history` to see if a recent upgrade correlates with the incident. Then `kubectl get pods -l app.kubernetes.io/instance=<release>` and `kubectl describe` the failing pod for events—ImagePullBackOff, OOMKilled, probe failures. Spring-specific: `kubectl logs` for datasource or Flyway errors; compare `helm get values` against expected profile. If JVM OOM, check limits vs requests and whether HPA scaled beyond node capacity. For config issues, `helm template` locally with prod values (redacted) and diff against live manifest. Document findings with revision number before rollback so postmortem can reference exact chart+image combo.

#### Scenario probe
**Situation:** Interviewer: 'Service has no endpoints after chart refactor.'

**Model answer:** Selector label mismatch—compare Service selector to pod labels from helper templates. Likely refactor changed selectorLabels but not all resources consistently.

---

### 37. Immutable selectors incident.

**Short answer:** Changing Deployment selector labels is immutable—causes failed upgrades or orphaned ReplicaSets. Senior interviews expect production trade-offs, failure modes, and Spring API integration—not isolated trivia.

#### What it is
Kubernetes rejects selector changes on existing Deployments. Helm upgrade attempting new selector leaves old RS orphaned, Service endpoints empty.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### How it works (internals)
Prevention: stable selectorLabels in helpers from day one. Recovery: new Deployment name (fullname bump) or delete/recreate with downtime planning.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### When to use / when NOT to use
Chart refactor incidents, rebranding label keys in production.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Production example
Blue/green new release name if selector must change. Communicate downtime window if recreate required.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Common mistakes
- Renaming app.kubernetes.io/name in selector
- Thinking helm rollback fixes selector change
- Manual label edits on pods not owned by template
- Not testing upgrade on staging clone

#### Interview follow-ups (with model answers)

**Q:** How recover without downtime?
**A:** Deploy a parallel Helm release with a new fullname suffix and corrected selector labels, then shift Ingress or Gateway traffic to the new Service. Validate Spring health and metrics on the green release before decommissioning the blue release. You cannot mutate selector in place on an existing Deployment—Kubernetes forbids it. This pattern also works when renaming release tracks during major chart breaking changes on AKS. Document DNS and TLS cutover steps so rollback means shifting traffic back, not editing immutable fields.

**Q:** What is the first command or dashboard you check when this misbehaves on AKS?
**A:** I start with `helm status <release> -n <ns>` and `helm history` to see if a recent upgrade correlates with the incident. Then `kubectl get pods -l app.kubernetes.io/instance=<release>` and `kubectl describe` the failing pod for events—ImagePullBackOff, OOMKilled, probe failures. Spring-specific: `kubectl logs` for datasource or Flyway errors; compare `helm get values` against expected profile. If JVM OOM, check limits vs requests and whether HPA scaled beyond node capacity. For config issues, `helm template` locally with prod values (redacted) and diff against live manifest. Document findings with revision number before rollback so postmortem can reference exact chart+image combo.

#### Scenario probe
**Situation:** Interviewer: 'helm upgrade failed: field is immutable selector.'

**Model answer:** Explain immutable selector, identify label change in diff, propose new release name or planned recreate, fix helpers to prevent recurrence.

---

### 38. Init containers.

**Short answer:** Init containers run to completion before app containers start—ordering setup tasks. Senior interviews expect production trade-offs, failure modes, and Spring API integration—not isolated trivia.

#### What it is
Init containers sequential; all must succeed before main Spring container starts. Use for wait-for-db, download config, or permissions fix—not long-running work.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### How it works (internals)
Helm template initContainers array from values: busybox wait-for TCP 1433, or custom image.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### When to use / when NOT to use
Dependency ordering when readiness alone insufficient; legacy apps needing file prep.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Production example
Prefer Spring retries and health checks over init wait loops when possible. Set init container resources and timeout.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Common mistakes
- Infinite wait init container blocking rollout
- Heavy logic duplicated in init and app
- Init requiring secrets not yet mounted
- Using init for DB migrations in prod

#### Interview follow-ups (with model answers)

**Q:** Init container vs readiness probe waiting for DB?
**A:** Readiness probe failure removes the pod from Service endpoints but the Deployment continues rolling other replicas—useful when DB is briefly down. Init containers block the main Spring container from starting until all init steps succeed—useful if the app crashes hard without DB at boot. Spring Boot often tolerates Hikari retry and Flyway retry loops; readiness reflecting partial health is more flexible than init wait loops. Infinite init wait scripts are a common stuck Pod Init:0/1 incident—always cap retries and surface logs. Prefer connection retry in application.yml plus readiness over brittle busybox wait-for-it in Helm templates.

**Q:** What is the first command or dashboard you check when this misbehaves on AKS?
**A:** I start with `helm status <release> -n <ns>` and `helm history` to see if a recent upgrade correlates with the incident. Then `kubectl get pods -l app.kubernetes.io/instance=<release>` and `kubectl describe` the failing pod for events—ImagePullBackOff, OOMKilled, probe failures. Spring-specific: `kubectl logs` for datasource or Flyway errors; compare `helm get values` against expected profile. If JVM OOM, check limits vs requests and whether HPA scaled beyond node capacity. For config issues, `helm template` locally with prod values (redacted) and diff against live manifest. Document findings with revision number before rollback so postmortem can reference exact chart+image combo.

#### Scenario probe
**Situation:** Interviewer: 'Pod stuck Init:0/1.'

**Model answer:** kubectl logs pod -c init-container-name, check command, network to dependency, image pull, and RBAC.

---

### 39. Sidecars.

**Short answer:** Sidecars share pod network/volumes—logging agents, mesh proxies, config sync—not second app servers. Senior interviews expect production trade-offs, failure modes, and Spring API integration—not isolated trivia.

#### What it is
Additional containers in pod.spec.containers alongside Spring app. Service mesh injects istio-proxy/linkerd-proxy via admission webhook or manual template.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### How it works (internals)
Helm values sidecar.enabled or rely on namespace injection labels on AKS. Account sidecar CPU/memory in pod resources.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### When to use / when NOT to use
mTLS, traffic capture, log forwarding (Fluent Bit), or secret rotation agents.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Production example
Size node pools for sidecar overhead. Configure Spring connection idle timeouts with proxy.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Common mistakes
- Ignoring sidecar memory in Java pod limit
- Two main HTTP servers in one pod anti-pattern
- Sidecar without lifecycle order on shutdown
- Manual sidecar fighting webhook injection duplicate

#### Interview follow-ups (with model answers)

**Q:** How sidecar injection interact with Helm?
**A:** Mutating admission webhooks add sidecar containers not present in helm template output—helm diff under-reports final pod spec. Platform teams enable injection via namespace labels; app Helm charts document required labels in values and README. Resource requests and limits in values must budget for proxy CPU and memory or HPA and VPA mis-size pods. Duplicate manual sidecar containers in templates plus webhook injection creates double proxies—choose one mechanism. On AKS with Istio, coordinate holdApplicationUntilProxyStarts with Spring startup probes in chart values.

**Q:** What is the first command or dashboard you check when this misbehaves on AKS?
**A:** I start with `helm status <release> -n <ns>` and `helm history` to see if a recent upgrade correlates with the incident. Then `kubectl get pods -l app.kubernetes.io/instance=<release>` and `kubectl describe` the failing pod for events—ImagePullBackOff, OOMKilled, probe failures. Spring-specific: `kubectl logs` for datasource or Flyway errors; compare `helm get values` against expected profile. If JVM OOM, check limits vs requests and whether HPA scaled beyond node capacity. For config issues, `helm template` locally with prod values (redacted) and diff against live manifest. Document findings with revision number before rollback so postmortem can reference exact chart+image combo.

#### Scenario probe
**Situation:** Interviewer: 'OOM after enabling Istio on Spring pods.'

**Model answer:** Sidecar adds ~64-128Mi+; raise pod memory limit and adjust JVM MaxRAMPercentage. Verify proxy resource annotations.

---

### 40. Graceful shutdown in K8s.

**Short answer:** Graceful shutdown: preStop hook + terminationGracePeriodSeconds + Spring graceful endpoint shutdown. Senior interviews expect production trade-offs, failure modes, and Spring API integration—not isolated trivia.

#### What it is
On pod delete, kubelet sends SIGTERM, runs preStop, waits grace period, then SIGKILL. Spring Boot handles SIGTERM to complete in-flight requests if server.shutdown=graceful.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### How it works (internals)
Helm values: terminationGracePeriodSeconds 60+, lifecycle.preStop sleep or actuator shutdown, readiness removed from endpoints before SIGTERM during roll.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### When to use / when NOT to use
Long-running HTTP requests, Kafka consumers, connection draining on AKS node drain.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Production example
Align grace with load balancer idle timeout and Ingress drain. Test rolling deploy under load.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Common mistakes
- terminationGracePeriodSeconds too short for JVM shutdown
- No preStop causing immediate endpoint removal race
- Liveness killing during slow shutdown
- Ignoring Kafka max.poll interval during roll

#### Interview follow-ups (with model answers)

**Q:** Why add preStop sleep?
**A:** When Kubernetes deletes a pod, endpoint removal propagates asynchronously through kube-proxy, CNI, and cloud load balancers. A short preStop sleep gives the Ingress or Application Gateway time to stop sending new connections before SIGTERM reaches Spring. Combine with server.shutdown=graceful so in-flight HTTP requests complete within terminationGracePeriodSeconds. Tune sleep duration to your AKS ingress controller propagation latency—often five to fifteen seconds. Without preStop, users see 502 errors during rolling deploys even when readiness checks are correct. Validate on AKS staging with the same values chain, Helm version, and admission policies as production. Store rendered manifests per release revision for incident review, and add helm template plus policy checks in CI. Senior interviews expect trade-offs, failure modes, and how GitOps, Helm history,

**Q:** What is the first command or dashboard you check when this misbehaves on AKS?
**A:** I start with `helm status <release> -n <ns>` and `helm history` to see if a recent upgrade correlates with the incident. Then `kubectl get pods -l app.kubernetes.io/instance=<release>` and `kubectl describe` the failing pod for events—ImagePullBackOff, OOMKilled, probe failures. Spring-specific: `kubectl logs` for datasource or Flyway errors; compare `helm get values` against expected profile. If JVM OOM, check limits vs requests and whether HPA scaled beyond node capacity. For config issues, `helm template` locally with prod values (redacted) and diff against live manifest. Document findings with revision number before rollback so postmortem can reference exact chart+image combo.

#### Scenario probe
**Situation:** Interviewer: '502 errors during deploy spikes.'

**Model answer:** Insufficient graceful shutdown—add preStop, increase grace period, enable Spring graceful, verify readiness fails before termination and PDB allows orderly roll.

---

### 41. Topology spread / AZ.

**Short answer:** Topology spread constraints distribute pods across zones/nodes for HA on multi-zone AKS. Senior interviews expect production trade-offs, failure modes, and Spring API integration—not isolated trivia.

#### What it is
topologySpreadConstraints with topologyKey topology.kubernetes.io/zone spread replicas across AZs. maxSkew and whenUnsatisfiable control strictness.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### How it works (internals)
Helm template spreadConstraints when values.highAvailability.enabled on regional AKS.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### When to use / when NOT to use
Production Spring services requiring zone failure tolerance.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Production example
Requires node pools across zones, PDB, and enough replicas (>=3 for 3 zones ideal).  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Common mistakes
- Spread with replicaCount 2 in 3 zones
- DoNotSchedule blocking all scheduling
- Ignoring zone-specific storage latency
- No pod anti-affinity complement

#### Interview follow-ups (with model answers)

**Q:** Spread constraints vs podAntiAffinity?
**A:** topologySpreadConstraints distribute pods across domains such as topology.kubernetes.io/zone for zone-level HA on regional AKS clusters. podAntiAffinity discourages co-location on the same node—complementary, not redundant. Use spread for AZ balance when replicaCount is at least three; use anti-affinity to reduce noisy neighbor stacking on large nodes. whenUnsatisfiable: DoNotSchedule can block scheduling if zones lack capacity—monitor pending pods during scale events. Helm values should toggle spread constraints only when highAvailability.enabled and node pools span multiple zones. Validate on AKS staging with the same values chain, Helm version, and admission policies as production. Store rendered manifests per release revision for incident review, and add helm template plus policy checks in CI. Senior interviews expect trade-offs, failure modes, and how GitOps, Helm history, and

**Q:** What is the first command or dashboard you check when this misbehaves on AKS?
**A:** I start with `helm status <release> -n <ns>` and `helm history` to see if a recent upgrade correlates with the incident. Then `kubectl get pods -l app.kubernetes.io/instance=<release>` and `kubectl describe` the failing pod for events—ImagePullBackOff, OOMKilled, probe failures. Spring-specific: `kubectl logs` for datasource or Flyway errors; compare `helm get values` against expected profile. If JVM OOM, check limits vs requests and whether HPA scaled beyond node capacity. For config issues, `helm template` locally with prod values (redacted) and diff against live manifest. Document findings with revision number before rollback so postmortem can reference exact chart+image combo.

#### Scenario probe
**Situation:** Interviewer: 'All pods on same node after scale-up.'

**Model answer:** Add topology spread or anti-affinity in chart, increase replicas, verify AKS node pool multi-AZ.

---

### 42. ResourceQuota / LimitRange.

**Short answer:** ResourceQuota caps namespace totals; LimitRange sets defaults/min/max per pod/container. Senior interviews expect production trade-offs, failure modes, and Spring API integration—not isolated trivia.

#### What it is
ResourceQuota limits aggregate CPU/memory/object counts per namespace on shared AKS. LimitRange injects default requests/limits when containers specify none.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### How it works (internals)
Platform team sets Quota per team namespace; chart always sets explicit resources to avoid surprises.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### When to use / when NOT to use
Multi-tenant clusters, chargeback, preventing noisy neighbor Spring services.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Production example
Request quota increases via governance. Document minimum requests for scheduling success.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Common mistakes
- Deploy failing 'exceeded quota' with no chart resources
- Quota too low for HPA maxReplicas sum
- LimitRange default limits breaking JVM sizing assumptions
- Forgetting ObjectCount quotas on ConfigMaps

#### Interview follow-ups (with model answers)

**Q:** Pod pending due to quota—debug?
**A:** kubectl describe quota -n namespace shows hard limits versus current usage for CPU, memory, and object counts. Sum container requests across all pods plus the new Deployment replica count you are trying to schedule. HPA maxReplicas times per-pod CPU request must fit within remaining quota headroom. LimitRange defaults may inflate requests if your chart omits resources entirely. Resolve by rightsizing Helm values, scaling down lower-priority workloads, or requesting a quota increase through platform governance on AKS. Validate on AKS staging with the same values chain, Helm version, and admission policies as production. Store rendered manifests per release revision for incident review, and add helm template plus policy checks in CI. Senior interviews expect trade-offs, failure modes, and how GitOps, Helm

**Q:** What is the first command or dashboard you check when this misbehaves on AKS?
**A:** I start with `helm status <release> -n <ns>` and `helm history` to see if a recent upgrade correlates with the incident. Then `kubectl get pods -l app.kubernetes.io/instance=<release>` and `kubectl describe` the failing pod for events—ImagePullBackOff, OOMKilled, probe failures. Spring-specific: `kubectl logs` for datasource or Flyway errors; compare `helm get values` against expected profile. If JVM OOM, check limits vs requests and whether HPA scaled beyond node capacity. For config issues, `helm template` locally with prod values (redacted) and diff against live manifest. Document findings with revision number before rollback so postmortem can reference exact chart+image combo.

#### Scenario probe
**Situation:** Interviewer: 'Helm install fails forbidden exceeded quota.'

**Model answer:** Check namespace ResourceQuota usage, HPA max, and whether new Deployment requests push over CPU/memory limits.

---

### 43. Helm `lookup` alternative for generated passwords.

**Short answer:** Replace Helm lookup for passwords with External Secrets, SOPS, or CSI Secret Store drivers. Senior interviews expect production trade-offs, failure modes, and Spring API integration—not isolated trivia.

#### What it is
Deterministic secret wiring: chart references Secret name; operator syncs from Key Vault. No cluster state read at template render time.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### How it works (internals)
Template ExternalSecret CR with Key Vault secret name from values. Deployment envFrom secretKeyRef. CI never renders secret values.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### When to use / when NOT to use
Any production Spring datasource or API key on AKS.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Production example
Rotation via Key Vault version; ESO refresh interval; audit access logs.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Common mistakes
- lookup + randAlphaNum password pattern from blog posts
- Storing generated password only in Helm release Secret
- ExternalSecret misconfigured tenant on AKS workload identity
- Secret name drift between chart versions

#### Interview follow-ups (with model answers)

**Q:** SOPS vs External Secrets?
**A:** SOPS encrypts values files stored in Git; CI or Argo CD decrypts at deploy time using KMS or Key Vault keys. External Secrets Operator keeps plaintext secrets only in Azure Key Vault and syncs Kubernetes Secrets on an interval. SOPS suits GitOps teams wanting encrypted secrets in the same repo as charts; ESO suits rotation, audit, and avoiding CI decryption keys. Many AKS enterprises standardize on ESO plus workload identity for Spring datasource passwords. Helm charts reference secret names only—never embed ciphertext or lookup-generated passwords in templates.

**Q:** What is the first command or dashboard you check when this misbehaves on AKS?
**A:** I start with `helm status <release> -n <ns>` and `helm history` to see if a recent upgrade correlates with the incident. Then `kubectl get pods -l app.kubernetes.io/instance=<release>` and `kubectl describe` the failing pod for events—ImagePullBackOff, OOMKilled, probe failures. Spring-specific: `kubectl logs` for datasource or Flyway errors; compare `helm get values` against expected profile. If JVM OOM, check limits vs requests and whether HPA scaled beyond node capacity. For config issues, `helm template` locally with prod values (redacted) and diff against live manifest. Document findings with revision number before rollback so postmortem can reference exact chart+image combo.

#### Scenario probe
**Situation:** Interviewer: 'Chart generates random DB password with lookup—replace how?'

**Model answer:** Provision password in Azure SQL + Key Vault, ExternalSecret to K8s Secret, Helm Deployment reference only. Spring uses env injection; idempotent upgrades.

---

### 44. `helm create` default chart vs production.

**Short answer:** helm create scaffolds dev-friendly defaults; production charts need probes, resources, PDB, security. Senior interviews expect production trade-offs, failure modes, and Spring API integration—not isolated trivia.

#### What it is
`helm create` yields generic nginx-like Deployment with no resources, single replica, no PDB, ClusterIP only—unsuitable for prod Spring without heavy customization.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### How it works (internals)
Start scaffold, replace with Spring patterns: actuator probes, resources, SA, optional HPA/Ingress, external secrets, topology spread for AKS.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### When to use / when NOT to use
Bootstrapping new microservice chart—never copy defaults to prod values.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Production example
Maintain values-prod.yaml checklist: replicas>=2, PDB, resources, non-root, network policy optional.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Common mistakes
- Shipping helm create defaults to AKS prod
- No differentiation between values-dev and values-prod
- Missing management port split for probes
- No chart version discipline

#### Interview follow-ups (with model answers)

**Q:** Minimum prod checklist for Spring Helm chart?
**A:** At minimum: two replicas, PodDisruptionBudget, CPU and memory requests and limits sized for JVM, startup/readiness/liveness on actuator paths, immutable image tag or digest, dedicated ServiceAccount with workload identity, externalized secrets, Ingress or HTTPRoute with TLS, optional HPA, graceful shutdown with preStop, standard app.kubernetes.io labels, and CI running helm lint, template, and policy validation. Add NetworkPolicy and topology spread when the AKS cluster enforces zero-trust or multi-AZ SLOs. Publish the checklist in the golden chart README so service teams self-serve compliant deploys.

**Q:** What is the first command or dashboard you check when this misbehaves on AKS?
**A:** I start with `helm status <release> -n <ns>` and `helm history` to see if a recent upgrade correlates with the incident. Then `kubectl get pods -l app.kubernetes.io/instance=<release>` and `kubectl describe` the failing pod for events—ImagePullBackOff, OOMKilled, probe failures. Spring-specific: `kubectl logs` for datasource or Flyway errors; compare `helm get values` against expected profile. If JVM OOM, check limits vs requests and whether HPA scaled beyond node capacity. For config issues, `helm template` locally with prod values (redacted) and diff against live manifest. Document findings with revision number before rollback so postmortem can reference exact chart+image combo.

#### Scenario probe
**Situation:** Interviewer: 'Review junior's helm create chart for prod.'

**Model answer:** Call out missing probes, resources, PDB, securityContext, secret handling, and env-specific values structure.

---

### 45. Multi-env.

**Short answer:** Multi-env via layered values files, Git branches, or Argo CD ApplicationSet—not one values.yaml for all. Senior interviews expect production trade-offs, failure modes, and Spring API integration—not isolated trivia.

#### What it is
Pattern: chart stable, values-dev/stage/prod override image, ingress host, replicas, Spring profile. Argo CD Application per env pointing same chart path different values.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### How it works (internals)
helm upgrade -f values.yaml -f values-prod.yaml. ApplicationSet generators for AKS clusters/environments.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### When to use / when NOT to use
Every team running Spring on dev/stage/prod AKS subscriptions or namespaces.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Production example
Separate AKS namespaces or clusters per env; prevent prod secrets in dev files. Promotion pipeline updates image digest in stage then prod Git.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Common mistakes
- Single values file with if env prod scattered in templates
- Prod hostnames in default values.yaml
- Wrong cluster kubecontext in CI
- Shared namespace dev+prod

#### Interview follow-ups (with model answers)

**Q:** ApplicationSet for multi-env Helm?
**A:** ApplicationSet generators list clusters, git directories, or SCM providers and instantiate Argo CD Applications from a template. Each Application points at the same chart path but uses environment-specific helm.valueFiles such as values-staging.yaml versus values-prod.yaml. Destination server and namespace differ per generator element—staging AKS versus production AKS. Promotion becomes a pull request updating image digest in prod values after staging verification. This DRY pattern scales to dozens of Spring microservices without copy-pasting Application YAML. Validate on AKS staging with the same values chain, Helm version, and admission policies as production. Store rendered manifests per release revision for incident review, and add helm template plus policy checks in CI. Senior interviews expect trade-offs, failure modes, and how GitOps, Helm history, and Spring

**Q:** What is the first command or dashboard you check when this misbehaves on AKS?
**A:** I start with `helm status <release> -n <ns>` and `helm history` to see if a recent upgrade correlates with the incident. Then `kubectl get pods -l app.kubernetes.io/instance=<release>` and `kubectl describe` the failing pod for events—ImagePullBackOff, OOMKilled, probe failures. Spring-specific: `kubectl logs` for datasource or Flyway errors; compare `helm get values` against expected profile. If JVM OOM, check limits vs requests and whether HPA scaled beyond node capacity. For config issues, `helm template` locally with prod values (redacted) and diff against live manifest. Document findings with revision number before rollback so postmortem can reference exact chart+image combo.

#### Scenario probe
**Situation:** Interviewer: 'How structure repos for 3 envs on AKS?'

**Model answer:** Monorepo chart + values-{env}.yaml or overlay dirs; Argo CD apps per env; CI promotes digest; secrets from Key Vault per subscription.

---

### 46. OCI Helm charts.

**Short answer:** OCI registries (ACR) store Helm charts as artifacts—helm push/pull like container images. Senior interviews expect production trade-offs, failure modes, and Spring API integration—not isolated trivia.

#### What it is
Helm 3 supports OCI protocol for chart storage in Azure Container Registry alongside images. helm package && helm push chart.tgz oci://myacr.azurecr.io/helm. Consumers: helm install oci://myacr.azurecr.io/helm/myapp --version 1.2.3.

#### How it works (internals)
CI publishes chart on merge with semver tag. Argo CD or helm upgrade references OCI chart version. Authenticate with az acr login or workload identity in pipeline.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### When to use / when NOT to use
Central artifact governance on AKS shops already using ACR; replaces ChartMuseum HTTP repos.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Production example
RBAC on ACR repos, sign charts (cosign), retain versions, replicate ACR for DR.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Common mistakes
- Mixing chart and image repos without naming convention
- Not pinning OCI chart version in Argo
- Assuming latest tag exists for charts
- Forgotten helm registry login in CI

#### Interview follow-ups (with model answers)

**Q:** OCI charts vs git-sourced charts in Argo?
**A:** Git-sourced charts live beside values in the repo—every template change gets a pull request review and full diff visibility. OCI charts are packaged artifacts in ACR versioned by semver—ideal for published platform charts consumed by many teams. Hybrid is common: application chart in Git, dependencies pulled from oci://myacr.azurecr.io/helm. Pin OCI chart versions explicitly in Argo Application spec—floating versions defeat reproducibility on AKS. Choose based on who publishes, how often the chart changes, and whether consumers need source-level review. Validate on AKS staging with the same values chain, Helm version, and admission policies as production. Store rendered manifests per release revision for incident review, and add helm template plus policy checks in CI. Senior interviews expect trade-offs, failure modes, and how

**Q:** What is the first command or dashboard you check when this misbehaves on AKS?
**A:** I start with `helm status <release> -n <ns>` and `helm history` to see if a recent upgrade correlates with the incident. Then `kubectl get pods -l app.kubernetes.io/instance=<release>` and `kubectl describe` the failing pod for events—ImagePullBackOff, OOMKilled, probe failures. Spring-specific: `kubectl logs` for datasource or Flyway errors; compare `helm get values` against expected profile. If JVM OOM, check limits vs requests and whether HPA scaled beyond node capacity. For config issues, `helm template` locally with prod values (redacted) and diff against live manifest. Document findings with revision number before rollback so postmortem can reference exact chart+image combo.

#### Scenario probe
**Situation:** Interviewer: 'Publish internal Helm charts on Azure?'

**Model answer:** Use ACR OCI helm push from CI, semver versions, Argo or helm pull by version, integrate with Azure AD for pull RBAC.

---

### 47. Kustomize vs Helm.

**Short answer:** Kustomize patches/overlays without templating; Helm parameterizes via Go templates—often combined. Senior interviews expect production trade-offs, failure modes, and Spring API integration—not isolated trivia.

#### What it is
Kustomize: base + overlays for env deltas, no logic language. Helm: charts with values and functions. Helm post-renderer kustomize or Argo CD kustomize plugins merge both.

#### How it works (internals)
Choose Helm when many services share parameterized chart. Kustomize when Kubernetes YAML mostly static with patch per env.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### When to use / when NOT to use
Helm for Spring microservice factory; Kustomize for platform teams preferring pure YAML.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Production example
Avoid two sources of truth fighting—pick primary tool per repo. Argo CD supports both natively.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Common mistakes
- Helm + Kustomize duplicate label changes
- Team split with no convention
- Over-templating in Helm what Kustomize patches handle cleaner
- Using Helm for single Deployment

#### Interview follow-ups (with model answers)

**Q:** When combine Helm and Kustomize?
**A:** Use Helm for parameterizing the Spring service chart across microservices; use Kustomize post-render patches for cluster-specific tweaks like tolerations, node selectors, or AKS agent pool labels. Document render order: helm template then kustomize build so reviewers know final YAML source. Avoid duplicating the same label or annotation change in both layers—pick one owner per field. Argo CD supports Helm plugins with kustomize post-rendering natively on some setups. Combine when platform mandates cluster patches app teams should not fork into every chart.

**Q:** What is the first command or dashboard you check when this misbehaves on AKS?
**A:** I start with `helm status <release> -n <ns>` and `helm history` to see if a recent upgrade correlates with the incident. Then `kubectl get pods -l app.kubernetes.io/instance=<release>` and `kubectl describe` the failing pod for events—ImagePullBackOff, OOMKilled, probe failures. Spring-specific: `kubectl logs` for datasource or Flyway errors; compare `helm get values` against expected profile. If JVM OOM, check limits vs requests and whether HPA scaled beyond node capacity. For config issues, `helm template` locally with prod values (redacted) and diff against live manifest. Document findings with revision number before rollback so postmortem can reference exact chart+image combo.

#### Scenario probe
**Situation:** Interviewer: 'Helm or Kustomize for 40 Spring services?'

**Model answer:** Helm chart template once, values per service—DRY wins. Kustomize overlays per service duplicate structure. Optional kustomize post-render for cluster-specific tweaks.

---

### 48. Argo CD + Helm.

**Short answer:** Argo CD syncs Git desired state to cluster; native Helm support with values files and parameters. Senior interviews expect production trade-offs, failure modes, and Spring API integration—not isolated trivia.

#### What it is
Application CR specifies repo path or OCI chart, helm.valueFiles, releaseName, version. Argo renders Helm and applies with tracking labels, supports sync waves, hooks respect.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### How it works (internals)
Git repo: charts/myapp + values-prod.yaml; Application destination AKS namespace; syncPolicy automated with selfHeal prune options cautiously.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### When to use / when NOT to use
GitOps standard for AKS Spring platforms—audit trail and PR-based promote.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Production example
Use AppProjects RBAC, ignore differences on HPA replicas if needed, sync hooks ordering for CRDs, avoid auto-prune on stateful mistakes.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Common mistakes
- Auto-sync bad commit to prod
- Helm values secret in Git plaintext
- Not using ignoreDifferences for webhook mutations
- Multiple Applications same release name

#### Interview follow-ups (with model answers)

**Q:** Argo CD vs helm upgrade in CI?
**A:** Argo CD continuously reconciles Git desired state to the cluster—drift is visible and self-heal can correct manual edits. CI helm upgrade is push-based: the pipeline applies changes when it runs, with no ongoing reconciliation. GitOps on AKS favors Argo for audit trails, PR promotions, and multi-cluster consistency. CI helm upgrade remains valid for Jenkins/GitLab deploy jobs or break-glass operations without Argo installed. Senior platforms often block direct helm upgrade to prod kubeconfig, forcing Argo sync from merged Git. Validate on AKS staging with the same values chain, Helm version, and admission policies as production. Store rendered manifests per release revision for incident review, and add helm template plus policy checks in CI. Senior interviews expect trade-offs, failure modes, and how

**Q:** What is the first command or dashboard you check when this misbehaves on AKS?
**A:** I start with `helm status <release> -n <ns>` and `helm history` to see if a recent upgrade correlates with the incident. Then `kubectl get pods -l app.kubernetes.io/instance=<release>` and `kubectl describe` the failing pod for events—ImagePullBackOff, OOMKilled, probe failures. Spring-specific: `kubectl logs` for datasource or Flyway errors; compare `helm get values` against expected profile. If JVM OOM, check limits vs requests and whether HPA scaled beyond node capacity. For config issues, `helm template` locally with prod values (redacted) and diff against live manifest. Document findings with revision number before rollback so postmortem can reference exact chart+image combo.

#### Scenario probe
**Situation:** Interviewer: 'Design GitOps for Helm on AKS.'

**Model answer:** Argo CD per env Application, PR promotes values change, ESO for secrets, helm template in CI on PR, Argo sync with manual prod approval or progressive sync.

---

### 49. Debugging a bad release.

**Short answer:** Debug bad release: history, status, pods, logs, manifest diff, rollback, then root-cause in Git. Senior interviews expect production trade-offs, failure modes, and Spring API integration—not isolated trivia.

#### What it is
Systematic triage: helm status/history, kubectl get/describe/logs, helm get manifest, helm diff, compare image/config with last good rev, check events and metrics.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### How it works (internals)
Runbook: identify revision → assess blast radius → rollback if needed → fix values/chart in Git → redeploy with atomic/wait.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### When to use / when NOT to use
Failed upgrade, partial sync, regression after promote on AKS Spring service.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Production example
Post-incident: add CI check that failed, update probes/resources, improve staging parity.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Common mistakes
- Random chart edits without diffing revisions
- Skipping --previous logs
- Multiple concurrent fixes obscuring cause
- Not capturing helm get manifest before rollback

#### Interview follow-ups (with model answers)

**Q:** helm status shows deployed but app broken?
**A:** Helm deployed means Kubernetes accepted resource creates and updates—not that Spring Boot passed business health checks. Investigate pod readiness, actuator health components, recent ConfigMap changes, and dependency outages separately from helm status. helm history revision may show deployed while pods CrashLoop due to probes or config. Use kubectl logs, metrics, and distributed traces to close the gap between control plane success and user-visible SLOs. Improve staging parity so helm success correlates with application health before prod promotion on AKS. Validate on AKS staging with the same values chain, Helm version, and admission policies as production. Store rendered manifests per release revision for incident review, and add helm template plus policy checks in CI. Senior interviews expect trade-offs, failure modes, and

**Q:** What is the first command or dashboard you check when this misbehaves on AKS?
**A:** I start with `helm status <release> -n <ns>` and `helm history` to see if a recent upgrade correlates with the incident. Then `kubectl get pods -l app.kubernetes.io/instance=<release>` and `kubectl describe` the failing pod for events—ImagePullBackOff, OOMKilled, probe failures. Spring-specific: `kubectl logs` for datasource or Flyway errors; compare `helm get values` against expected profile. If JVM OOM, check limits vs requests and whether HPA scaled beyond node capacity. For config issues, `helm template` locally with prod values (redacted) and diff against live manifest. Document findings with revision number before rollback so postmortem can reference exact chart+image combo.

#### Scenario probe
**Situation:** Interviewer: 'Walk through debugging failed prod Helm release.'

**Model answer:** History for rev, describe failing pods, logs --previous, get manifest diff rev-1, rollback if urgent, fix Git, postmortem on missing CI guard.

---

### 50. Senior Helm for a Spring service.

**Short answer:** Senior Helm for Spring: idempotent upgrades, externalized config/secrets, probes, resources, GitOps, observability. Senior interviews expect production trade-offs, failure modes, and Spring API integration—not isolated trivia.

#### What it is
Holistic chart: Deployment with graceful shutdown, actuator probes, JVM-sized resources, HPA/PDB, Ingress/Gateway, SA+workload identity, ExternalSecrets, standard labels, CI template/lint/policy, Argo CD promotion, digest pinning, multi-env values.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### How it works (internals)
Own platform chart library; services only supply values for image, ingress host, feature flags. Document override order and runbooks.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### When to use / when NOT to use
Leading platform engineering for Spring Boot fleet on AKS.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Production example
SLO-driven rollouts, migration discipline, cost-aware autoscaling, security baselines enforced by policy.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Common mistakes
- Treating Helm as afterthought bolted on kubectl YAML
- No shared chart standards across teams
- Ignoring JVM/container coupling in resources
- Operational rollback without Git discipline

#### Interview follow-ups (with model answers)

**Q:** What metrics prove Helm/Spring deploy health?
**A:** Kubernetes signals: rollout status conditions, container restart rate, probe failure events, HPA current versus desired replicas, and PDB allowed disruptions. Spring signals: actuator health, HTTP 5xx ratio, latency p99, JVM heap usage, and GC pause time from Micrometer exporting to Azure Monitor or Prometheus. Annotate Deployments with helm revision or git commit for correlation dashboards during canary analysis. Alert on sustained readiness failures after sync—not only on pipeline green. Senior SRE reviews combine helm history timeline with application SLO dashboards for post-deploy validation.

**Q:** How mentor teams on Helm standards?
**A:** Provide a golden Spring chart, jsonschema validation for values.yaml, pull request checklist, and recorded chart review office hours. Enforce gradually: start with CI helm lint and template policy warnings, then Kyverno audit mode, then admission enforce. Document AKS-specific annotations for internal load balancers, workload identity, and AGIC. Celebrate good examples in internal tech talks—reduces tribal knowledge. Measure adoption via policy violation rates and mean time to onboard a new microservice chart. Validate on AKS staging with the same values chain, Helm version, and admission policies as production. Store rendered manifests per release revision for incident review, and add helm template plus policy checks in CI. Senior interviews expect trade-offs, failure modes, and how GitOps, Helm history, and Spring observability connect.

#### Scenario probe
**Situation:** Interviewer: 'You own Helm standards for 50 Spring services on AKS—priorities?'

**Model answer:** Golden chart, ESO+Key Vault, CI render/policy, Argo GitOps, digest promote, probe/resource baselines, PDB/HPA patterns, runbooks for rollback, OCI chart registry, Kyverno guardrails.

---

### 51. Gateway API vs Ingress — Helm chart implications

**Short answer:** Gateway API changes Helm chart outputs from Ingress to Gateway+HTTPRoute with separate CRD lifecycle. Senior interviews expect production trade-offs, failure modes, and Spring API integration—not isolated trivia.

#### What it is
Gateway API introduces GatewayClass, Gateway, HTTPRoute resources replacing monolithic Ingress. Helm charts must template HTTPRoute parentRefs to shared Gateway installed by platform team. TLS and listener config move to Gateway resource—apps only route rules.

#### How it works (internals)
Platform Helm release installs Gateway API CRDs and shared Gateway on AKS (AGIC v2 or Envoy Gateway). App chart templates HTTPRoute with hostnames and backend Service refs from values.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### When to use / when NOT to use
Greenfield AKS platforms or migrating from Ingress when needing role separation (infra vs app teams).  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Production example
Install CRDs once per cluster version; chart dependencies pin gateway-api version. Coordinate listener ports and certificates on Gateway—not per-app Ingress annotations.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Common mistakes
- App chart templates Ingress while cluster only supports Gateway API
- HTTPRoute parentRef wrong Gateway name/namespace
- CRD version skew between controller and chart
- Duplicating TLS certs on every app chart

#### Interview follow-ups (with model answers)

**Q:** Migrate Ingress Helm templates to Gateway API?
**A:** Phase one: platform installs shared Gateway with TLS listeners matching current Ingress hosts on AKS. Phase two: dual-publish Ingress and HTTPRoute during cutover, verifying traffic on both paths in staging. Phase three: remove Ingress templates from app charts once HTTPRoute is stable. Rename values keys from ingress.host to httpRoute.hostnames and parentRefs.gatewayName pointing at the shared Gateway. Run gateway API conformance tests and update CI kubeconform schemas for gateway.networking.k8s.io API versions. Validate on AKS staging with the same values chain, Helm version, and admission policies as production. Store rendered manifests per release revision for incident review, and add helm template plus policy checks in CI. Senior interviews expect trade-offs, failure modes, and how GitOps, Helm history, and Spring observability connect.

**Q:** What is the first command or dashboard you check when this misbehaves on AKS?
**A:** I start with `helm status <release> -n <ns>` and `helm history` to see if a recent upgrade correlates with the incident. Then `kubectl get pods -l app.kubernetes.io/instance=<release>` and `kubectl describe` the failing pod for events—ImagePullBackOff, OOMKilled, probe failures. Spring-specific: `kubectl logs` for datasource or Flyway errors; compare `helm get values` against expected profile. If JVM OOM, check limits vs requests and whether HPA scaled beyond node capacity. For config issues, `helm template` locally with prod values (redacted) and diff against live manifest. Document findings with revision number before rollback so postmortem can reference exact chart+image combo.

#### Scenario probe
**Situation:** Interviewer: 'Platform moving to Gateway API—impact on app Helm charts?'

**Model answer:** Replace Ingress template with HTTPRoute, stop managing cluster-wide Gateway in app chart, reference shared Gateway via values parentRefs, update CI kubeconform schemas for new API group.

---

### 52. Service mesh (Istio/Linkerd) with Helm — sidecar injection

**Short answer:** Mesh sidecar injection via namespace labels or pod annotations—Helm must account for extra containers/resources. Senior interviews expect production trade-offs, failure modes, and Spring API integration—not isolated trivia.

#### What it is
Istio: label namespace istio-injection=enabled or pod annotation sidecar.istio.io/inject. Linkerd: linkerd.io/inject enabled. Admission webhook mutates pods at create—Helm-rendered Deployment triggers injection.

#### How it works (internals)
Platform sets namespace labels; app Helm chart documents required labels in values. Add pod annotations template optional for per-service opt-out. Increase resources.limits.memory for JVM after injection.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### When to use / when NOT to use
mTLS east-west, traffic policies, or unified telemetry on AKS Spring mesh.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Production example
Install istio/linkerd control plane via separate Helm releases. Configure holdApplicationUntilProxyStarts for Spring startup ordering if needed.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Common mistakes
- Helm chart hardcodes sidecar container conflicting with webhook
- OOM from unchanged memory after injection
- Probe ports ignoring redirect to sidecar
- Not setting outbound port exclusions for Azure SQL

#### Interview follow-ups (with model answers)

**Q:** holdApplicationUntilProxyStarts for Spring?
**A:** The Istio annotation holdApplicationUntilProxyStarts delays the Spring container until the envoy sidecar is ready to accept outbound traffic. This prevents startup failures when the app calls Azure SQL, Redis, or Key Vault before the proxy can intercept connections. Trade-off: longer rollouts and tighter coupling between sidecar readiness and Spring startup probes. Tune startupProbe failureThreshold accordingly and verify SQL outbound port exclusions if using explicit port lists. Linkerd offers similar ordering via proxy wait init behavior—consult mesh docs when standardizing Helm values.

**Q:** What is the first command or dashboard you check when this misbehaves on AKS?
**A:** I start with `helm status <release> -n <ns>` and `helm history` to see if a recent upgrade correlates with the incident. Then `kubectl get pods -l app.kubernetes.io/instance=<release>` and `kubectl describe` the failing pod for events—ImagePullBackOff, OOMKilled, probe failures. Spring-specific: `kubectl logs` for datasource or Flyway errors; compare `helm get values` against expected profile. If JVM OOM, check limits vs requests and whether HPA scaled beyond node capacity. For config issues, `helm template` locally with prod values (redacted) and diff against live manifest. Document findings with revision number before rollback so postmortem can reference exact chart+image combo.

#### Scenario probe
**Situation:** Interviewer: 'Enable Istio injection for Helm-deployed Spring apps.'

**Model answer:** Namespace label, bump pod memory in values, verify mTLS, configure SQL port outbound rules, test rollout with holdApplicationUntilProxyStarts and actuator health.

---

### 53. Vertical Pod Autoscaler vs HPA for Java memory

**Short answer:** VPA recommends/adjusts requests; HPA scales replica count—complementary for Java memory right-sizing. Senior interviews expect production trade-offs, failure modes, and Spring API integration—not isolated trivia.

#### What it is
Vertical Pod Autoscaler observes usage and suggests or auto-updates CPU/memory requests. HPA changes replicas based on metrics. Java memory benefits from VPA recommendations for requests; HPA handles traffic spikes.

#### How it works (internals)
Install VPA on AKS (often custom or preview). Set VPA mode Off or Initial for recommendations only before auto. Helm values resources from VPA recommendation pipeline updated periodically.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### When to use / when NOT to use
Java services with uncertain heap after launch; reduce OOM and wasted capacity.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Production example
Avoid VPA auto on JVM during active HPA scale events without coordination. Use recommendation mode, human review, update values Git.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Common mistakes
- VPA auto + HPA on same metric causing thrash
- Applying VPA recommendation without adjusting -Xmx
- VPA updating limits unexpectedly killing pods
- Ignoring sidecar memory in VPA target

#### Interview follow-ups (with model answers)

**Q:** VPA vs manually setting Java container memory?
**A:** Manual sizing after load testing establishes a baseline Helm values contract trusted by finance and SRE. VPA recommendation mode observes actual usage and suggests updated requests without auto-mutating pods—safe for JVM workloads. Translate VPA memory recommendations into MaxRAMPercentage and limits via periodic Git pull requests, not silent auto-apply. Full VPA auto on Java remains risky during traffic shifts because heap ramps lag demand spikes. Pair VPA insights with HPA on custom latency metrics for holistic scaling on AKS. Validate on AKS staging with the same values chain, Helm version, and admission policies as production. Store rendered manifests per release revision for incident review, and add helm template plus policy checks in CI. Senior interviews expect trade-offs, failure modes, and how

**Q:** What is the first command or dashboard you check when this misbehaves on AKS?
**A:** I start with `helm status <release> -n <ns>` and `helm history` to see if a recent upgrade correlates with the incident. Then `kubectl get pods -l app.kubernetes.io/instance=<release>` and `kubectl describe` the failing pod for events—ImagePullBackOff, OOMKilled, probe failures. Spring-specific: `kubectl logs` for datasource or Flyway errors; compare `helm get values` against expected profile. If JVM OOM, check limits vs requests and whether HPA scaled beyond node capacity. For config issues, `helm template` locally with prod values (redacted) and diff against live manifest. Document findings with revision number before rollback so postmortem can reference exact chart+image combo.

#### Scenario probe
**Situation:** Interviewer: 'Java pods over-provisioned—HPA or VPA?'

**Model answer:** VPA (recommendation mode) for right-size requests/limits; HPA if traffic variable. Update Helm values from VPA reports; align JVM flags; don't rely on CPU HPA alone for memory-bound Java.

---

### 54. cert-manager + Let's Encrypt in Helm

**Short answer:** cert-manager Helm release automates TLS Certificates via Let's Encrypt ClusterIssuer and Ingress/Gateway integration. Senior interviews expect production trade-offs, failure modes, and Spring API integration—not isolated trivia.

#### What it is
cert-manager CRDs: ClusterIssuer (Let's Encrypt ACME), Certificate, CertificateRequest. Helm installs cert-manager; annotations on Ingress or cert-manager Certificate CR reference issuer. HTTP-01 or DNS-01 challenge on AKS.

#### How it works (internals)
Platform chart: cert-manager dependency, ClusterIssuer letsencrypt-prod with DNS-01 for Azure DNS. App Ingress template annotation cert-manager.io/cluster-issuer or separate Certificate manifest.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### When to use / when NOT to use
Automated TLS for Spring public APIs without manual cert import to Application Gateway.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Production example
Use staging issuer for tests, rate limits awareness, secure ACME account key in Secret, monitor cert expiry alerts despite auto-renew.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Common mistakes
- HTTP-01 blocked by NetworkPolicy
- Issuer in wrong namespace scope
- cert-manager CRDs not installed before app chart
- Wildcard cert per app instead of shared pattern

#### Interview follow-ups (with model answers)

**Q:** DNS-01 vs HTTP-01 on AKS?
**A:** HTTP-01 requires Let's Encrypt to reach your Ingress challenge URL from the public internet—simple for public Spring APIs behind AGIC. DNS-01 creates TXT records via Azure DNS solver—required for wildcard certs and internal-only hostnames without public endpoints. Helm values choose cert-manager solver type per environment; platform charts install ClusterIssuer once. NetworkPolicy must allow cert-manager solver pods to reach ACME endpoints and DNS APIs. Test with letsencrypt-staging issuer before prod to avoid rate limit lockouts during chart iteration. Validate on AKS staging with the same values chain, Helm version, and admission policies as production. Store rendered manifests per release revision for incident review, and add helm template plus policy checks in CI. Senior interviews expect trade-offs, failure modes, and how GitOps,

**Q:** What is the first command or dashboard you check when this misbehaves on AKS?
**A:** I start with `helm status <release> -n <ns>` and `helm history` to see if a recent upgrade correlates with the incident. Then `kubectl get pods -l app.kubernetes.io/instance=<release>` and `kubectl describe` the failing pod for events—ImagePullBackOff, OOMKilled, probe failures. Spring-specific: `kubectl logs` for datasource or Flyway errors; compare `helm get values` against expected profile. If JVM OOM, check limits vs requests and whether HPA scaled beyond node capacity. For config issues, `helm template` locally with prod values (redacted) and diff against live manifest. Document findings with revision number before rollback so postmortem can reference exact chart+image combo.

#### Scenario probe
**Situation:** Interviewer: 'Automate TLS for Helm Ingress on AKS.'

**Model answer:** Install cert-manager via Helm, ClusterIssuer LE prod, annotate Ingress or Certificate CR, DNS-01 if private AGIC, verify secret mounted and renew before 30d expiry.

---

### 55. Kyverno/OPA policy with Helm releases

**Short answer:** Kyverno/OPA policies validate or mutate Helm-deployed resources—enforce standards beyond helm lint. Senior interviews expect production trade-offs, failure modes, and Spring API integration—not isolated trivia.

#### What it is
Admission policies: require labels, ban latest tag, enforce resources requests, disallow privileged containers. Validate helm-rendered manifests at apply time in Argo CD or API server.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### How it works (internals)
Install Kyverno via Helm on AKS. Policies: mutate imagePullPolicy, validate PDB present for prod namespaces, require non-root. CI: conftest test against policies before merge.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### When to use / when NOT to use
Multi-team clusters needing guardrails when Helm chart quality varies.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Production example
Start audit mode, then enforce. Exceptions via policy exceptions CR for break-glass. Sync policy updates before enforcing on existing workloads.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Common mistakes
- Enforce without notifying teams—deploy wall of failures
- Policies conflicting with mesh injection mutations
- Blocking Helm hooks needed Jobs
- No CI pre-check duplicating cluster policy

#### Interview follow-ups (with model answers)

**Q:** Kyverno vs OPA Gatekeeper with Helm?
**A:** Both are admission controllers validating resources at apply time regardless of whether Helm or Argo CD created them. Kyverno uses Kubernetes-native YAML policies approachable for platform teams; Gatekeeper uses Rego for expressive custom logic. Policies can require labels, ban latest image tags, enforce resource requests, and demand PDBs in prod namespaces. Combine helm template CI checks with cluster admission for defense in depth—CI catches developer mistakes early, admission catches bypass attempts. Start Kyverno in audit mode on AKS, then enforce with documented exceptions for break-glass namespaces.

**Q:** What is the first command or dashboard you check when this misbehaves on AKS?
**A:** I start with `helm status <release> -n <ns>` and `helm history` to see if a recent upgrade correlates with the incident. Then `kubectl get pods -l app.kubernetes.io/instance=<release>` and `kubectl describe` the failing pod for events—ImagePullBackOff, OOMKilled, probe failures. Spring-specific: `kubectl logs` for datasource or Flyway errors; compare `helm get values` against expected profile. If JVM OOM, check limits vs requests and whether HPA scaled beyond node capacity. For config issues, `helm template` locally with prod values (redacted) and diff against live manifest. Document findings with revision number before rollback so postmortem can reference exact chart+image combo.

#### Scenario probe
**Situation:** Interviewer: 'Enforce Helm chart standards cluster-wide.'

**Model answer:** Golden chart plus Kyverno validate policies (resources, probes, labels), CI conftest on template output, gradual enforce, Argo CD pre-sync validation hooks optional.

---

## Scenario-based interview drills

### S1. Readiness probe kills pod during slow Spring startup

**Situation:** Spring Boot 3 service with Flyway migrations and Redis cache warm-up takes 90 seconds to accept traffic on cold start. Helm chart sets `readinessProbe.httpGet.path: /actuator/health` with `initialDelaySeconds: 10`, `periodSeconds: 5`, `failureThreshold: 3`. Pods never become Ready; Deployment rollout stalls at 0/N; Argo CD sync hangs.

**What they're testing:** Startup vs readiness vs liveness probes, Spring Boot 3 actuator health groups, and Helm values for JVM services.

**How to structure your answer:**
- Calculate failure window: 10 + 3×5 = 25s < 90s startup
- Introduce `startupProbe` (K8s 1.16+) or tune readiness
- Split actuator health groups: `readinessState` vs `livenessState`
- Helm chart values documentation for team overrides

**Model answer:** Readiness fails three times by 25s while Flyway still runs—kubelet marks pod unready forever but doesn't restart (liveness not failed). Rollout can't complete because new ReplicaSet pods never pass Ready. Fix: add `startupProbe` hitting same `/actuator/health/readiness` with `failureThreshold: 30`, `periodSeconds: 5` (150s budget); readiness probe runs only after startup succeeds. Alternatively increase readiness `initialDelaySeconds` to 120 for this chart profile—less flexible across services. Spring: `management.endpoint.health.group.readiness.include=readinessState,db,redis` so Flyway completion reflects in readiness; keep liveness lightweight ping only. Helm values: `probes.startup.enabled`, document JVM+Flyway services use `slow` profile. Don't point liveness at same heavy health check—DB blip restarts pod unnecessarily. Test `helm template` + kind cluster with intentional `spring.main.lazy-initialization=false`. Argo CD: sync wave with Job migration before Deployment if migrations moved out. Senior signal: quote probe timing math and Spring Boot 3 probe port `management.server.port`.

**Common weak answers:** Disable readiness; set liveness identical to readiness; `failureThreshold: 100` on readiness without startupProbe; use `/actuator/health` including disk space causing flaky readiness.

**Follow-up probes (with answers):**

**Q:** Flyway in init container vs main container startup?
**A:** Init container Job ensures migrations complete before app starts—readiness simpler but schema migrate blocks pod schedule; choose based on multi-replica migration locking strategy.

---

### S2. Java pod OOMKilled after Helm memory limit change

**Situation:** Platform team applied golden Helm chart bump `resources.limits.memory` from 1Gi to 768Mi to save cost. Spring Boot service using `-Xmx512m` and container-aware flags starts fine then OOMKilled under load during month-end batch. `kubectl describe pod` shows exit 137, `OOMKilled`.

**What they're testing:** JVM heap vs container limit, `-XX:MaxRAMPercentage`, native memory overhead, and Helm resource templates.

**How to structure your answer:**
- Container limit must exceed heap + metaspace + thread stacks + direct buffers
- Use `MaxRAMPercentage` not fixed `-Xmx` when limits change
- Helm values: requests vs limits, JVM env from downward API
- Right-size with metrics not spreadsheet

**Model answer:** 768Mi limit with `-Xmx512m` leaves only 256Mi for off-heap—insufficient for 200 threads, Netty, metaspace, and GC overhead under batch load. JVM doesn't know cgroup limit if running older JDK without `UseContainerSupport` (Java 17 has it). Fix: set `JAVA_TOOL_OPTIONS=-XX:MaxRAMPercentage=70.0 -XX:+UseContainerSupport` so heap scales with limit, or restore 1Gi limit with measured usage from Prometheus `container_memory_working_set_bytes`. Requests should reflect steady state; limits headroom for spikes. Helm chart: `resources.java.memory.default` ties `limits.memory` and `MaxRAMPercentage` formula in `_helpers.tpl`. Month-end batch: temporarily raise limits via values overlay or HPA doesn't help memory-bound—vertical scale. Investigate native memory leak if OOM persists at generous limit. Document cost trade-off: saved $50/month vs incident. Flyway/hibernate second-level cache sizing review. Never copy non-Java chart memory defaults onto Spring.

**Common weak answers:** Disable limits; set `-Xmx768m` equal to limit; ignore 137 exit code; scale replicas to fix memory per pod.

**Follow-up probes (with answers):**

**Q:** Why not set `-Xmx` to limit minus 128Mi rule of thumb?
**A:** Rule breaks with varying thread counts and native libs; `MaxRAMPercentage` adapts to limit changes—one Helm value update propagates correctly.

---

### S3. Helm rollback cannot undo Flyway migration

**Situation:** Release `order-service` revision 47 deployed new Helm chart with image tag `2.4.0` including Flyway `V47__add_column.sql`. Production issue forces `helm rollback order-service 46` within 10 minutes. Pods run `2.3.0` but crash: `Validate failed: migration checksum mismatch` or missing column errors.

**What they're testing:** Helm rollback limits, database migration forward-only discipline, GitOps revert vs helm rollback, and Spring Flyway repair strategy.

**How to structure your answer:**
- Helm restores K8s manifest snapshot, not DB schema
- Migrations must be backward compatible expand-contract
- Rollforward fix vs restore DB snapshot
- Pipeline: migrate before deploy or feature flags

**Model answer:** `helm rollback` re-applies revision 46 manifests—image 2.3.0—but database already applied V47 irreversible DDL unless migration was additive nullable column only. If V47 added `NOT NULL` column without default, 2.3.0 ORM fails. Correct incident response: roll forward—deploy 2.4.1 fixing bug while keeping schema, or hotfix 2.3.1 if migration was backward compatible (rare). If truly broken migration, restore SQL PITR to pre-deploy timestamp—coordinated outage—and block rollback fantasy. Prevention: expand-contract migrations (add nullable column → dual write → backfill → enforce → remove old); Flyway `validateOnMigrate` in CI against staging clone. GitOps: revert Git commit and sync, same DB constraint applies—Helm isn't special. Store rendered manifest per revision for audit but educate teams: **rollback is compute rollback, not data rollback**. Optional: Helm pre-upgrade hook Job running Flyway separately with version gate requiring app version ≥ migration version. Runbook documents when helm rollback safe (config-only change) vs forbidden (schema).

**Common weak answers:** `flyway repair` to silence errors without schema fix; delete flyway_schema_history row; rollback DB manually in prod without backup; assume `--atomic` rollbacks database.

**Follow-up probes (with answers):**

**Q:** Separate migration Job from app Deployment in Helm?
**A:** `pre-upgrade` hook Job runs Flyway once per release—app image assumes schema ready; rollback still can't un-migrate; enables smaller app pods and clearer failure surface.

---

### S4. External Secrets Operator lag after Key Vault rotation

**Situation:** Platform uses External Secrets Operator (ESO) with `ClusterSecretStore` pointing to Azure Key Vault. Security rotates `spring.datasource.password` in vault. ESO `refreshInterval: 1h`. Within 20 minutes of rotation, Spring pods still use old password—intermittent auth failures until hour passes.

**What they're testing:** Secret rotation, ESO refresh, pod restart on secret change, Helm chart secret refs, and Spring config reload limits.

**How to structure your answer:**
- ESO async refresh vs app mount reload
- Reduce interval or trigger refresh on rotation event
- Reloader sidecar/stakater reload on Secret change
- Spring doesn't hot-reload JDBC password by default

**Model answer:** Kubernetes Secret updated by ESO doesn't restart pods—Spring reads password at startup from env `SPRING_DATASOURCE_PASSWORD` injected via `secretKeyRef`. After Key Vault rotation, ESO updates K8s Secret on next refresh (1h)—until then pods hold old value; DB may reject old password immediately if dual-password window not configured. Fixes: (1) Stakater Reloader annotation on Deployment `secret.reloader.stakater.com/reload: db-secret` rolling restart on Secret change; (2) Lower `refreshInterval` to 5m for creds; (3) Azure Event Grid on Key Vault secret near-expiry triggering ESO force reconcile; (4) SQL Entra auth eliminates password rotation class. Helm: ExternalSecret manifest in chart or platform layer; document that `helm upgrade` doesn't restart pods if secret data changes—need Reloader or `kubectl rollout restart`. Coordinate rotation: enable dual active passwords on SQL before vault swap. Test: rotate in staging, measure time to pod cred update. Senior: secrets lifecycle is app+platform joint ownership.

**Common weak answers:** `helm upgrade` with same chart version expecting secret push; embed password in values.yaml; manual pod delete without Reloader automation; ignore intermittent errors as transient network.

**Follow-up probes (with answers):**

**Q:** Mount secrets as files vs env for rotation?
**A:** Files allow inotify reload with Spring Cloud Kubernetes reload feature—still needs app support; env always requires restart unless custom watcher; most Java shops restart on secret change via Reloader.

---

### S5. Argo CD OutOfSync from manual kubectl edit

**Situation:** On-call `kubectl edit deployment order-service` raised CPU limits during incident. Incident resolved but Argo CD shows `OutOfSync` and next automated sync reverts limits, causing recurrence. Developer insists Helm chart values are correct; cluster differs.

**What they're testing:** GitOps drift, imperative vs declarative, Argo CD sync policies, and Helm as packaging not source of truth.

**How to structure your answer:**
- Argo compares Git desired vs live
- Manual edit creates drift
- Fix Git values, sync, disable ad-hoc kubectl
- Self-heal implications

**Model answer:** GitOps principle: Git (or Helm values repo) is desired state; Argo CD reconciles. `kubectl edit` patches live Deployment directly—Argo detects diff on `spec.template.spec.containers[0].resources.limits.cpu`. If `selfHeal: true`, Argo reverts on next sync interval—on-call fix disappears. Correct path: commit CPU limit bump to `values-prod.yaml`, MR review, `helm upgrade` via pipeline, Argo sync. For incident temporary scale, use Argo CD `kubectl patch` with sync override annotation pause or document `argocd app sync --force` after Git update. Enable `ignoreDifferences` only for legitimate fields (replicas if HPA)—not resources. RBAC: restrict kubectl edit in prod to break-glass with audit. Helm release metadata still shows chart version but live spec drifted—`helm get values` won't show kubectl edit. Prevention: Kyverno deny UPDATE deployment from humans except Argo SA. Post-incident: export live yaml, diff against Git, merge learnings. Senior quote: **Helm rollback doesn't fix GitOps drift if Git wasn't updated.**

Argo CD `Application` `syncPolicy.

**Common weak answers:** Disable Argo; `--force` sync without Git fix; edit Helm release Secret directly; expect Helm to own live drift.

**Follow-up probes (with answers):**

**Q:** `helm upgrade` vs Argo CD Application sync?
**A:** Argo wraps helm template + apply; standalone `helm upgrade` bypasses Git causing Argo OutOfSync—pick one deploy mechanism per cluster.

---

### S6. preStop hook race loses in-flight HTTP requests

**Situation:** Spring service on AKS receives SIGTERM during rolling deploy. Helm chart adds `preStop: sleep 15` but customers report 502s from Application Gateway during deploy windows. Ingress removes pod from backend before sleep completes—or vice versa depending on config.

**What they're testing:** Pod termination lifecycle, ingress connection draining, preStop ordering, and Spring graceful shutdown alignment.

**How to structure your answer:**
- Sequence: delete pod → endpoint removal → SIGTERM → grace period
- preStop sleep purpose: wait for LB drain
- Spring graceful + sufficient `terminationGracePeriodSeconds`
- AGIC/App Gateway drain timeout settings

**Model answer:** On SIGTERM, kubelet runs `preStop` then sends SIGTERM to container. Endpoints controller removes pod IP from Service when pod marked Terminating—but timing varies; AGIC may still send traffic briefly. Pattern: `preStop: exec sleep 15` allows load balancer to stop new connections before Spring shutdown begins; must exceed LB drain interval (AGIC `connection-draining-timeout`). Spring `server.shutdown=graceful` with `spring.lifecycle.timeout-per-shutdown-phase=30s` completes in-flight requests. Total need: `terminationGracePeriodSeconds` ≥ preStop sleep + graceful shutdown (e.g., 60s). If 502 persists, increase AGIC draining, verify readiness removed pod from pool before Terminating (readinessProbe fails on shutdown). Helm values expose `lifecycle.preStop.sleepSeconds` and `terminationGracePeriodSeconds` linked. Avoid `preStop` calling `/shutdown` endpoint unless custom. Test: `kubectl delete pod` with active long request load test. Document deploy window SLO impact; consider blue-green or Flagger canary.

**Common weak answers:** preStop without graceful shutdown; zero grace period; only increase replicas without drain tuning; disable rolling update.

**Follow-up probes (with answers):**

**Q:** Why sleep in preStop instead of immediate graceful shutdown?
**A:** LB and K8s endpoints propagation lag; sleep lets dataplane stop routing new connections before app begins rejecting—graceful shutdown handles existing connections.

---

### S7. Helm post-upgrade hook migration Job blocks all deploys

**Situation:** Chart adds `post-upgrade` hook Job running Flyway against shared Azure SQL. Job fails on migration conflict; hook failure leaves release in `pending-upgrade` state; subsequent `helm upgrade` errors; 15 microservices queue behind failed release.

**What they're testing:** Helm hooks failure modes, hook weights, backoff limits, and migration isolation.

**How to structure your answer:**
- Hook failure blocks release status
- `helm rollback` or delete failed hook Job
- Hook design: idempotent, timeout, separate migration pipeline
- `hook-delete-policy` cleanup

**Model answer:** Failed post-upgrade hook prevents marking release successful—Argo CD sync stuck `Progressing`. `kubectl get jobs -l helm.sh/hook` shows failed migration; logs reveal Flyway validation error (checksum, locked migration). Immediate: fix SQL script forward in Git, delete failed hook Job and associated pods, `helm upgrade` again with `--no-hooks` only if emergency and migrations run manually—document exception. Structural fix: move Flyway to CI pipeline against staging clone before image build; hook only for smoke test or remove hooks for migrations entirely. Hook config: `hook-weight` order, `hook-delete-policy: before-hook-creation,hook-succeeded`, `backoffLimit: 1`, activeDeadlineSeconds. Never share one migration Job across services writing same schema. For shared DB, platform team owns migration repo decoupled from app chart. Alert on `helm status` pending-upgrade. Senior: hooks are sharp knives—justify vs pipeline Jobs.

**Common weak answers:** Delete release Secret blindly; rerun hook without fixing SQL; infinite `backoffLimit`; run migrations in every replica pod.

**Follow-up probes (with answers):**

**Q:** `helm upgrade --no-hooks` when acceptable?
**A:** Break-glass only when migrations applied manually and verified; requires change ticket, platform approval, and immediate Git fix so next normal deploy isn't inconsistent.

---

### S8. ConfigMap change does not update Spring `@Value` properties

**Situation:** Ops updates Helm values `application.yaml` ConfigMap feature flags; `helm upgrade` succeeds; pods running but new `feature.newCheckout=true` not active until manual pod restart. Team expected Spring Cloud Kubernetes reload.

**What they're testing:** ConfigMap updates vs pod restart, Spring Cloud Kubernetes config reload, Helm chart checksum annotation pattern.

**How to structure your answer:**
- ConfigMap mount propagation delay
- Spring Boot doesn't auto-reload `@Value` without refresh scope
- Helm `checksum/config` pod template annotation
- Reloader or rollout restart

**Model answer:** Updating ConfigMap doesn't restart pods—kubelet syncs files within ~60s but Spring reads properties at startup unless `spring-cloud-kubernetes` config reload enabled with `spring.cloud.kubernetes.reload.enabled=true` and `monitoring-config-maps=true`—still limited for `@Value` vs `@ConfigurationProperties` refresh. Helm best practice: template annotation `checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}` on Deployment pod spec—ConfigMap content change changes checksum, triggers rolling update. Alternative: Stakater Reloader on ConfigMap. For feature flags, prefer external config service or Query refetch interval over ConfigMap hot reload complexity. Document in chart README: **config changes cause rolling restart** by design. Verify `kubectl rollout status` after upgrade. Spring Boot 3: `spring.config.import=optional:configtree:/etc/config/` for mounted files. Test: change flag, helm upgrade, assert new pod env without manual delete.

**Common weak answers:** Expect ConfigMap alone to restart pods; use `kubectl apply` without checksum trick; enable reload without testing `@Value` beans; store feature flags only in ConfigMap without app support.

**Follow-up probes (with answers):**

**Q:** Secret vs ConfigMap for non-sensitive feature flags?
**A:** ConfigMap appropriate; same restart semantics; don't use Secret to force reload—that obscures sensitivity classification.

---

### S9. PDB blocks node drain during cluster upgrade

**Situation:** AKS cluster upgrade needs node drain. `order-service` Helm chart sets `PodDisruptionBudget minAvailable: 100%` with `replicaCount: 2`. Platform cannot evict pods; upgrade blocked; management deadline missed.

**What they're testing:** PDB semantics, availability vs operability, Helm values for HA, and platform negotiation.

**How to structure your answer:**
- PDB minAvailable 100% with 2 replicas = zero voluntary disruption
- Fix: `maxUnavailable: 1` or temporarily relax PDB
- Surge upgrade strategy
- Business hours maintenance window

**Model answer:** `minAvailable: 100%` on two replicas forbids any voluntary eviction—Kubernetes blocks drain. Chart likely copied production banking template without tailoring. Fix chart: `maxUnavailable: 1` (or `minAvailable: 1`) allowing one pod down during rolling work while maintaining single-instance service. For true zero-downtime during infra upgrade, need ≥3 replicas across zones with PDB `minAvailable: 2` and surge node pool. Coordinate temporary PDB patch via Git for maintenance window—platform PR lowering minAvailable with approval. AKS upgrade settings: surge nodes accept new pods before old drain. Educate app team: PDB protects users but blocks cluster ops—balance SLO. Helm: environment-specific values `pdb.enabled`, stricter prod. Test drain in staging: `kubectl drain --ignore-daemonsets`. Incident comms: misconfigured PDB is app chart bug, not platform malice.

**Common weak answers:** Delete PDB in prod permanently; set replicas 1 with minAvailable 100%; force drain `--force` without understanding PDB; disable cluster upgrades.

**Follow-up probes (with answers):**

**Q:** `minAvailable` vs `maxUnavailable` for odd replica counts?
**A:** `maxUnavailable: 34%` on 3 replicas allows one down; express policy clearly in values docs—prefer maxUnavailable for rolling deploy mental model.

---

### S10. Image digest pin in values breaks emergency hotfix path

**Situation:** GitOps policy requires `image.tag` replaced with `image.digest: sha256:abc...` in Helm values for supply-chain security. Security patch needs urgent deploy; CI builds `2.3.1-patch` but values file still pins old digest; Argo sync deploys vulnerable image; team confused why tag change ignored.

**What they're testing:** Image reference immutability, digest vs tag in Helm, GitOps promotion flow, and emergency change process.

**How to structure your answer:**
- Digest pins immutable manifest; tag variable ignored if digest set
- Hotfix pipeline updates digest in Git
- OCI signing and ACR retention
- Break-glass tag-only override policy

**Model answer:** When both tag and digest specified, kubelet uses digest—updating tag alone in values without new digest deploys nothing new. CI must push image, capture digest from `docker buildx imagetools inspect`, commit to `values-prod.yaml` or Argo Image Updater writes digest. Emergency hotfix: build patch image, pipeline opens automated PR updating digest field, fast-track merge, Argo sync. Document that `helm upgrade --set image.tag=2.3.1` fails policy if template prefers digest from values. ACR: enable retention policy so old digests aren't garbage-collected before rollback need. For rollback, Git revert digest to previous sha256 recorded in changelog. Optional: use tags only in dev; prod digest-only. Cosign verify in admission matches digest. Senior supply-chain narrative: digest pin is correct; process must update pin atomically with build. Test: change tag only, confirm Argo diff shows no pod change—expected.

**Common weak answers:** Remove digest pinning under pressure without review; use `latest` tag; manually retag old digest to new code; skip CI updating Git.

**Follow-up probes (with answers):**

**Q:** Argo CD Image Updater vs pipeline digest commit?
**A:** Image Updater watches ACR semver tags and writes digest to Git—good for continuous deploy; pipeline commit better for audited promotion gates—pick one to avoid fighting.

---
