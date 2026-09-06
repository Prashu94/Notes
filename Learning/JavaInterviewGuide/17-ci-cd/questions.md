# CI/CD — 55 Senior Interview Questions

**Bar:** Quality gates, artifacts, GitOps, secrets, rollback. JDs list CI-CD and AI-assisted tools together — you still own the pipeline.

---

### 1. CI vs CD vs GitOps

**Short answer:** CI validates every commit (build, test, scan). CD promotes a tested artifact through environments. GitOps makes Git the desired-state source for the cluster—Argo CD or Flux reconcile manifests, not humans clicking `kubectl`. In a mature Spring-on-AKS shop, CI builds and signs the image; CD or GitOps applies the Helm chart revision that references that digest.

#### What it is
Continuous Integration is the feedback loop on the developer's change: compile, unit tests, static analysis, security scans, and packaging into an immutable artifact. Continuous Delivery/Deployment is the promotion path from artifact registry to QA, staging, and production with gates between stages. GitOps is an operational model where cluster state is declared in Git and a controller continuously syncs live state to match.

#### How it works (internals)
CI triggers on push/PR via webhooks. The pipeline runs on ephemeral agents, publishes images to ACR, and records the git SHA as metadata. CD can be push-based (`helm upgrade`) or pull-based (GitOps). Argo CD sync policies control automated, selfHeal, and prune behavior.

#### When to use / when NOT to use
Use CI on every team. Use CD for all non-prod; for prod use automated CD with strong gates or GitOps with manual sync—pick based on compliance. GitOps shines on AKS with many microservices.

#### Production example
A `order-service` Spring Boot app: PR triggers GitHub Actions—Maven test, SpotBugs, Trivy, build/push `acr.io/orders:abc1234`. Merge updates `values-prod.yaml`; Argo CD syncs; rollback is `git revert`.

#### Common mistakes
- Manual prod deploy bypassing pipeline
- No path filters in monorepo—wasted CI minutes
- Secrets in workflow YAML or logs
- Treating green CI as optional before merge

#### Interview follow-ups (with model answers)

**Q:** How does CI vs CD vs GitOps affect rollback and MTTR?
**A:** Rollback is fast only when artifacts are immutable and cluster desired state lives in Git. I revert the GitOps PR or Helm revision, re-run smoke tests against the same image digest, and verify database migration compatibility. MTTR improves when prod promotion is reproducible and not a manual kubectl hotfix. I measure time from failed deploy to restored SLO and track failure class in a dashboard.

**Q:** What gate would you add after a failure involving CI vs CD vs GitOps?
**A:** I classify the failure (flake, infra, quality, security, deploy) and add an automated guard in the right stage. Examples: quarantine flaky integration tests, ephemeral runners with disk cleanup, required Trivy/Sonar on main, or environment approval for production. Track recurrence quarterly and tie to DORA change failure rate separately from PR red builds.

**Q:** How do you explain CI vs CD vs GitOps to a team new to CI/CD on Spring and AKS?
**A:** I walk a concrete path: PR runs Maven verify and scans; merge publishes a signed image to ACR; a GitOps PR updates Helm values; Argo CD syncs to AKS; smoke tests hit `/actuator/health`. I emphasize CI validates change, CD/GitOps promotes immutable artifacts, and main stays green with feature flags for incomplete work.

#### Scenario probe

**Situation:** Production deploy failed after a green PR; the panel asks how CI vs CD vs GitOps fits your response.

**Model answer:** I timeline the pipeline: which stage failed, which digest was promoted, whether Argo drifted from Git. I roll forward or revert Git, verify smoke tests and Flyway order, communicate MTTR, and add a gate so this failure class is caught pre-prod next time.

#### Code / config (when useful)
```yaml
# See repo workflow — pin actions to SHA; use environments for prod
```

---
### 2. Pipeline as code

**Short answer:** The pipeline definition lives in version control—`.github/workflows/`, `azure-pipelines.yml`, or `Jenkinsfile`—reviewed in PRs like application code. The UI is for observability, not the source of truth. Seniors reject snowflake jobs that only exist in someone's Jenkins clicks.

#### What it is
Pipeline-as-code means build, test, scan, and deploy steps are declarative files committed beside the application—auditable, diffable, branchable.

#### How it works (internals)
GitHub Actions parses workflow YAML on webhooks; Azure DevOps expands templates at queue time; Jenkins loads Jenkinsfile from SCM. Shared libraries or reusable workflows deduplicate boilerplate.

#### When to use / when NOT to use
Adopt when team size or compliance requires repeatable delivery. Skip heavyweight gates for throwaway prototypes. For Pipeline as code, enforce on main and prod paths; allow faster feedback loops on feature branches where safe. Never bypass prod gates without break-glass documentation and post-incident restore of controls.

#### Production example
On `order-service`, we applied pipeline as code in the pipeline: PR blocked on failure, main published digest `sha256:abc…`, GitOps PR updated `values-prod.yaml`, smoke tests passed, and rollback was a Git revert tested in staging first. Change failure rate dropped after we classified flakes and added quarantine policy.

#### Common mistakes
- Manual prod deploy bypassing pipeline
- No path filters in monorepo—wasted CI minutes
- Secrets in workflow YAML or logs
- Treating green CI as optional before merge

#### Interview follow-ups (with model answers)

**Q:** How does Pipeline as code affect rollback and MTTR?
**A:** Rollback is fast only when artifacts are immutable and cluster desired state lives in Git. I revert the GitOps PR or Helm revision, re-run smoke tests against the same image digest, and verify database migration compatibility. MTTR improves when prod promotion is reproducible and not a manual kubectl hotfix. I measure time from failed deploy to restored SLO and track failure class in a dashboard.

**Q:** What gate would you add after a failure involving Pipeline as code?
**A:** I classify the failure (flake, infra, quality, security, deploy) and add an automated guard in the right stage. Examples: quarantine flaky integration tests, ephemeral runners with disk cleanup, required Trivy/Sonar on main, or environment approval for production. Track recurrence quarterly and tie to DORA change failure rate separately from PR red builds.

**Q:** How do you explain Pipeline as code to a team new to CI/CD on Spring and AKS?
**A:** I walk a concrete path: PR runs Maven verify and scans; merge publishes a signed image to ACR; a GitOps PR updates Helm values; Argo CD syncs to AKS; smoke tests hit `/actuator/health`. I emphasize CI validates change, CD/GitOps promotes immutable artifacts, and main stays green with feature flags for incomplete work.

#### Scenario probe

**Situation:** Production deploy failed after a green PR; the panel asks how Pipeline as code fits your response.

**Model answer:** I timeline the pipeline: which stage failed, which digest was promoted, whether Argo drifted from Git. I roll forward or revert Git, verify smoke tests and Flyway order, communicate MTTR, and add a gate so this failure class is caught pre-prod next time.

---
### 3. Trunk-based vs GitFlow

**Short answer:** Trunk-based development keeps `main` always releasable with short-lived feature branches and feature flags for incomplete work. GitFlow's long-lived `develop`/`release` branches slow integration and inflate merge pain. Most high-performing teams lean trunk plus small PRs plus protected main.

#### What it is
Trunk-based: short-lived branches merge to `main` via PR with CI required. GitFlow uses long-lived develop/release branches—a model from shrink-wrap era.

#### How it works (internals)
Protected branch rules enforce reviews and status checks. Feature flags decouple deploy from release. Release trains tag `main` weekly.

#### When to use / when NOT to use
Adopt when team size or compliance requires repeatable delivery. Skip heavyweight gates for throwaway prototypes. For Trunk-based vs GitFlow, enforce on main and prod paths; allow faster feedback loops on feature branches where safe. Never bypass prod gates without break-glass documentation and post-incident restore of controls.

#### Production example
On `order-service`, we applied trunk-based vs gitflow in the pipeline: PR blocked on failure, main published digest `sha256:abc…`, GitOps PR updated `values-prod.yaml`, smoke tests passed, and rollback was a Git revert tested in staging first. Change failure rate dropped after we classified flakes and added quarantine policy.

#### Common mistakes
- Manual prod deploy bypassing pipeline
- No path filters in monorepo—wasted CI minutes
- Secrets in workflow YAML or logs
- Treating green CI as optional before merge

#### Interview follow-ups (with model answers)

**Q:** How does Trunk-based vs GitFlow affect rollback and MTTR?
**A:** Rollback is fast only when artifacts are immutable and cluster desired state lives in Git. I revert the GitOps PR or Helm revision, re-run smoke tests against the same image digest, and verify database migration compatibility. MTTR improves when prod promotion is reproducible and not a manual kubectl hotfix. I measure time from failed deploy to restored SLO and track failure class in a dashboard.

**Q:** What gate would you add after a failure involving Trunk-based vs GitFlow?
**A:** I classify the failure (flake, infra, quality, security, deploy) and add an automated guard in the right stage. Examples: quarantine flaky integration tests, ephemeral runners with disk cleanup, required Trivy/Sonar on main, or environment approval for production. Track recurrence quarterly and tie to DORA change failure rate separately from PR red builds.

**Q:** How do you explain Trunk-based vs GitFlow to a team new to CI/CD on Spring and AKS?
**A:** I walk a concrete path: PR runs Maven verify and scans; merge publishes a signed image to ACR; a GitOps PR updates Helm values; Argo CD syncs to AKS; smoke tests hit `/actuator/health`. I emphasize CI validates change, CD/GitOps promotes immutable artifacts, and main stays green with feature flags for incomplete work.

#### Scenario probe

**Situation:** Production deploy failed after a green PR; the panel asks how Trunk-based vs GitFlow fits your response.

**Model answer:** I timeline the pipeline: which stage failed, which digest was promoted, whether Argo drifted from Git. I roll forward or revert Git, verify smoke tests and Flyway order, communicate MTTR, and add a gate so this failure class is caught pre-prod next time.

---
### 4. Quality gates

**Short answer:** Quality gates are automated checks that block promotion when thresholds fail—unit coverage, Sonar quality gate, Trivy CVE severity, contract tests. They turn 'hope someone reviewed' into enforced policy. Tune gates to fail fast on PR, not only on main.

#### What it is
Quality gates is a core practice in modern delivery for Spring microservices on AKS. It connects developer workflow to production safety—artifacts, gates, GitOps, and observability—not just running Jenkins jobs. Interviewers want trade-offs, failure modes, and how you measured improvement with DORA metrics.

#### How it works (internals)
Pipelines trigger on git events, run on ephemeral agents, publish immutable artifacts, and promote through environments with approvals. For quality gates, wire the check into the earliest stage that has enough context—usually PR for tests and main for deploy. Integrate with ACR, Key Vault or OIDC, and Argo CD for cluster sync. Failed stages should emit structured logs and failure class tags for MTTR tracking.

#### When to use / when NOT to use
Adopt when team size or compliance requires repeatable delivery. Skip heavyweight gates for throwaway prototypes. For Quality gates, enforce on main and prod paths; allow faster feedback loops on feature branches where safe. Never bypass prod gates without break-glass documentation and post-incident restore of controls.

#### Production example
On `order-service`, we applied quality gates in the pipeline: PR blocked on failure, main published digest `sha256:abc…`, GitOps PR updated `values-prod.yaml`, smoke tests passed, and rollback was a Git revert tested in staging first. Change failure rate dropped after we classified flakes and added quarantine policy.

#### Common mistakes
- Manual prod deploy bypassing pipeline
- No path filters in monorepo—wasted CI minutes
- Secrets in workflow YAML or logs
- Treating green CI as optional before merge

#### Interview follow-ups (with model answers)

**Q:** How does Quality gates affect rollback and MTTR?
**A:** Rollback is fast only when artifacts are immutable and cluster desired state lives in Git. I revert the GitOps PR or Helm revision, re-run smoke tests against the same image digest, and verify database migration compatibility. MTTR improves when prod promotion is reproducible and not a manual kubectl hotfix. I measure time from failed deploy to restored SLO and track failure class in a dashboard.

**Q:** What gate would you add after a failure involving Quality gates?
**A:** I classify the failure (flake, infra, quality, security, deploy) and add an automated guard in the right stage. Examples: quarantine flaky integration tests, ephemeral runners with disk cleanup, required Trivy/Sonar on main, or environment approval for production. Track recurrence quarterly and tie to DORA change failure rate separately from PR red builds.

**Q:** How do you explain Quality gates to a team new to CI/CD on Spring and AKS?
**A:** I walk a concrete path: PR runs Maven verify and scans; merge publishes a signed image to ACR; a GitOps PR updates Helm values; Argo CD syncs to AKS; smoke tests hit `/actuator/health`. I emphasize CI validates change, CD/GitOps promotes immutable artifacts, and main stays green with feature flags for incomplete work.

#### Scenario probe

**Situation:** Production deploy failed after a green PR; the panel asks how Quality gates fits your response.

**Model answer:** I timeline the pipeline: which stage failed, which digest was promoted, whether Argo drifted from Git. I roll forward or revert Git, verify smoke tests and Flyway order, communicate MTTR, and add a gate so this failure class is caught pre-prod next time.

---
### 5. Artifact immutability

**Short answer:** Build once, store immutable artifacts (JAR, container image by digest) in a registry; promote the same bits through environments. Never rebuild on deploy—that introduces non-reproducible drift. Tags like `:main` are pointers; digests are truth.

#### What it is
Artifact immutability is a core practice in modern delivery for Spring microservices on AKS. It connects developer workflow to production safety—artifacts, gates, GitOps, and observability—not just running Jenkins jobs. Interviewers want trade-offs, failure modes, and how you measured improvement with DORA metrics.

#### How it works (internals)
Pipelines trigger on git events, run on ephemeral agents, publish immutable artifacts, and promote through environments with approvals. For artifact immutability, wire the check into the earliest stage that has enough context—usually PR for tests and main for deploy. Integrate with ACR, Key Vault or OIDC, and Argo CD for cluster sync. Failed stages should emit structured logs and failure class tags for MTTR tracking.

#### When to use / when NOT to use
Adopt when team size or compliance requires repeatable delivery. Skip heavyweight gates for throwaway prototypes. For Artifact immutability, enforce on main and prod paths; allow faster feedback loops on feature branches where safe. Never bypass prod gates without break-glass documentation and post-incident restore of controls.

#### Production example
On `order-service`, we applied artifact immutability in the pipeline: PR blocked on failure, main published digest `sha256:abc…`, GitOps PR updated `values-prod.yaml`, smoke tests passed, and rollback was a Git revert tested in staging first. Change failure rate dropped after we classified flakes and added quarantine policy.

#### Common mistakes
- Manual prod deploy bypassing pipeline
- No path filters in monorepo—wasted CI minutes
- Secrets in workflow YAML or logs
- Treating green CI as optional before merge

#### Interview follow-ups (with model answers)

**Q:** How does Artifact immutability affect rollback and MTTR?
**A:** Rollback is fast only when artifacts are immutable and cluster desired state lives in Git. I revert the GitOps PR or Helm revision, re-run smoke tests against the same image digest, and verify database migration compatibility. MTTR improves when prod promotion is reproducible and not a manual kubectl hotfix. I measure time from failed deploy to restored SLO and track failure class in a dashboard.

**Q:** What gate would you add after a failure involving Artifact immutability?
**A:** I classify the failure (flake, infra, quality, security, deploy) and add an automated guard in the right stage. Examples: quarantine flaky integration tests, ephemeral runners with disk cleanup, required Trivy/Sonar on main, or environment approval for production. Track recurrence quarterly and tie to DORA change failure rate separately from PR red builds.

**Q:** How do you explain Artifact immutability to a team new to CI/CD on Spring and AKS?
**A:** I walk a concrete path: PR runs Maven verify and scans; merge publishes a signed image to ACR; a GitOps PR updates Helm values; Argo CD syncs to AKS; smoke tests hit `/actuator/health`. I emphasize CI validates change, CD/GitOps promotes immutable artifacts, and main stays green with feature flags for incomplete work.

#### Scenario probe

**Situation:** Production deploy failed after a green PR; the panel asks how Artifact immutability fits your response.

**Model answer:** I timeline the pipeline: which stage failed, which digest was promoted, whether Argo drifted from Git. I roll forward or revert Git, verify smoke tests and Flyway order, communicate MTTR, and add a gate so this failure class is caught pre-prod next time.

---
### 6. Build once, deploy many

**Short answer:** A single CI build produces artifacts consumed by dev, QA, staging, and prod deploy jobs. Each environment changes configuration only—Helm values, env vars—not the compiled binary. This is how you prove prod ran what QA tested.

#### What it is
Build once, deploy many is a core practice in modern delivery for Spring microservices on AKS. It connects developer workflow to production safety—artifacts, gates, GitOps, and observability—not just running Jenkins jobs. Interviewers want trade-offs, failure modes, and how you measured improvement with DORA metrics.

#### How it works (internals)
Pipelines trigger on git events, run on ephemeral agents, publish immutable artifacts, and promote through environments with approvals. For build once, deploy many, wire the check into the earliest stage that has enough context—usually PR for tests and main for deploy. Integrate with ACR, Key Vault or OIDC, and Argo CD for cluster sync. Failed stages should emit structured logs and failure class tags for MTTR tracking.

#### When to use / when NOT to use
Adopt when team size or compliance requires repeatable delivery. Skip heavyweight gates for throwaway prototypes. For Build once, deploy many, enforce on main and prod paths; allow faster feedback loops on feature branches where safe. Never bypass prod gates without break-glass documentation and post-incident restore of controls.

#### Production example
On `order-service`, we applied build once, deploy many in the pipeline: PR blocked on failure, main published digest `sha256:abc…`, GitOps PR updated `values-prod.yaml`, smoke tests passed, and rollback was a Git revert tested in staging first. Change failure rate dropped after we classified flakes and added quarantine policy.

#### Common mistakes
- Manual prod deploy bypassing pipeline
- No path filters in monorepo—wasted CI minutes
- Secrets in workflow YAML or logs
- Treating green CI as optional before merge

#### Interview follow-ups (with model answers)

**Q:** How does Build once, deploy many affect rollback and MTTR?
**A:** Rollback is fast only when artifacts are immutable and cluster desired state lives in Git. I revert the GitOps PR or Helm revision, re-run smoke tests against the same image digest, and verify database migration compatibility. MTTR improves when prod promotion is reproducible and not a manual kubectl hotfix. I measure time from failed deploy to restored SLO and track failure class in a dashboard.

**Q:** What gate would you add after a failure involving Build once, deploy many?
**A:** I classify the failure (flake, infra, quality, security, deploy) and add an automated guard in the right stage. Examples: quarantine flaky integration tests, ephemeral runners with disk cleanup, required Trivy/Sonar on main, or environment approval for production. Track recurrence quarterly and tie to DORA change failure rate separately from PR red builds.

**Q:** How do you explain Build once, deploy many to a team new to CI/CD on Spring and AKS?
**A:** I walk a concrete path: PR runs Maven verify and scans; merge publishes a signed image to ACR; a GitOps PR updates Helm values; Argo CD syncs to AKS; smoke tests hit `/actuator/health`. I emphasize CI validates change, CD/GitOps promotes immutable artifacts, and main stays green with feature flags for incomplete work.

#### Scenario probe

**Situation:** Production deploy failed after a green PR; the panel asks how Build once, deploy many fits your response.

**Model answer:** I timeline the pipeline: which stage failed, which digest was promoted, whether Argo drifted from Git. I roll forward or revert Git, verify smoke tests and Flyway order, communicate MTTR, and add a gate so this failure class is caught pre-prod next time.

---
### 7. Reproducible builds

**Short answer:** Same commit SHA plus locked dependencies yields the same artifact hash every time. Pin Maven/Gradle lockfiles, base image digests, and JDK version in CI. Reproducibility is prerequisite for credible rollback and security audits.

#### What it is
Reproducible builds is a core practice in modern delivery for Spring microservices on AKS. It connects developer workflow to production safety—artifacts, gates, GitOps, and observability—not just running Jenkins jobs. Interviewers want trade-offs, failure modes, and how you measured improvement with DORA metrics.

#### How it works (internals)
Pipelines trigger on git events, run on ephemeral agents, publish immutable artifacts, and promote through environments with approvals. For reproducible builds, wire the check into the earliest stage that has enough context—usually PR for tests and main for deploy. Integrate with ACR, Key Vault or OIDC, and Argo CD for cluster sync. Failed stages should emit structured logs and failure class tags for MTTR tracking.

#### When to use / when NOT to use
Adopt when team size or compliance requires repeatable delivery. Skip heavyweight gates for throwaway prototypes. For Reproducible builds, enforce on main and prod paths; allow faster feedback loops on feature branches where safe. Never bypass prod gates without break-glass documentation and post-incident restore of controls.

#### Production example
On `order-service`, we applied reproducible builds in the pipeline: PR blocked on failure, main published digest `sha256:abc…`, GitOps PR updated `values-prod.yaml`, smoke tests passed, and rollback was a Git revert tested in staging first. Change failure rate dropped after we classified flakes and added quarantine policy.

#### Common mistakes
- Manual prod deploy bypassing pipeline
- No path filters in monorepo—wasted CI minutes
- Secrets in workflow YAML or logs
- Treating green CI as optional before merge

#### Interview follow-ups (with model answers)

**Q:** How does Reproducible builds affect rollback and MTTR?
**A:** Rollback is fast only when artifacts are immutable and cluster desired state lives in Git. I revert the GitOps PR or Helm revision, re-run smoke tests against the same image digest, and verify database migration compatibility. MTTR improves when prod promotion is reproducible and not a manual kubectl hotfix. I measure time from failed deploy to restored SLO and track failure class in a dashboard.

**Q:** What gate would you add after a failure involving Reproducible builds?
**A:** I classify the failure (flake, infra, quality, security, deploy) and add an automated guard in the right stage. Examples: quarantine flaky integration tests, ephemeral runners with disk cleanup, required Trivy/Sonar on main, or environment approval for production. Track recurrence quarterly and tie to DORA change failure rate separately from PR red builds.

**Q:** How do you explain Reproducible builds to a team new to CI/CD on Spring and AKS?
**A:** I walk a concrete path: PR runs Maven verify and scans; merge publishes a signed image to ACR; a GitOps PR updates Helm values; Argo CD syncs to AKS; smoke tests hit `/actuator/health`. I emphasize CI validates change, CD/GitOps promotes immutable artifacts, and main stays green with feature flags for incomplete work.

#### Scenario probe

**Situation:** Production deploy failed after a green PR; the panel asks how Reproducible builds fits your response.

**Model answer:** I timeline the pipeline: which stage failed, which digest was promoted, whether Argo drifted from Git. I roll forward or revert Git, verify smoke tests and Flyway order, communicate MTTR, and add a gate so this failure class is caught pre-prod next time.

---
### 8. Caching CI

**Short answer:** Cache dependencies (`~/.m2`, Gradle, Docker layers) to keep feedback under ten minutes—but invalidate on lockfile change. Remote cache for monorepos; beware cache poisoning on fork PRs with self-hosted runners.

#### What it is
Caching CI is a core practice in modern delivery for Spring microservices on AKS. It connects developer workflow to production safety—artifacts, gates, GitOps, and observability—not just running Jenkins jobs. Interviewers want trade-offs, failure modes, and how you measured improvement with DORA metrics.

#### How it works (internals)
Pipelines trigger on git events, run on ephemeral agents, publish immutable artifacts, and promote through environments with approvals. For caching ci, wire the check into the earliest stage that has enough context—usually PR for tests and main for deploy. Integrate with ACR, Key Vault or OIDC, and Argo CD for cluster sync. Failed stages should emit structured logs and failure class tags for MTTR tracking.

#### When to use / when NOT to use
Adopt when team size or compliance requires repeatable delivery. Skip heavyweight gates for throwaway prototypes. For Caching CI, enforce on main and prod paths; allow faster feedback loops on feature branches where safe. Never bypass prod gates without break-glass documentation and post-incident restore of controls.

#### Production example
On `order-service`, we applied caching ci in the pipeline: PR blocked on failure, main published digest `sha256:abc…`, GitOps PR updated `values-prod.yaml`, smoke tests passed, and rollback was a Git revert tested in staging first. Change failure rate dropped after we classified flakes and added quarantine policy.

#### Common mistakes
- Manual prod deploy bypassing pipeline
- No path filters in monorepo—wasted CI minutes
- Secrets in workflow YAML or logs
- Treating green CI as optional before merge

#### Interview follow-ups (with model answers)

**Q:** How does Caching CI affect rollback and MTTR?
**A:** Rollback is fast only when artifacts are immutable and cluster desired state lives in Git. I revert the GitOps PR or Helm revision, re-run smoke tests against the same image digest, and verify database migration compatibility. MTTR improves when prod promotion is reproducible and not a manual kubectl hotfix. I measure time from failed deploy to restored SLO and track failure class in a dashboard.

**Q:** What gate would you add after a failure involving Caching CI?
**A:** I classify the failure (flake, infra, quality, security, deploy) and add an automated guard in the right stage. Examples: quarantine flaky integration tests, ephemeral runners with disk cleanup, required Trivy/Sonar on main, or environment approval for production. Track recurrence quarterly and tie to DORA change failure rate separately from PR red builds.

**Q:** How do you explain Caching CI to a team new to CI/CD on Spring and AKS?
**A:** I walk a concrete path: PR runs Maven verify and scans; merge publishes a signed image to ACR; a GitOps PR updates Helm values; Argo CD syncs to AKS; smoke tests hit `/actuator/health`. I emphasize CI validates change, CD/GitOps promotes immutable artifacts, and main stays green with feature flags for incomplete work.

#### Scenario probe

**Situation:** Production deploy failed after a green PR; the panel asks how Caching CI fits your response.

**Model answer:** I timeline the pipeline: which stage failed, which digest was promoted, whether Argo drifted from Git. I roll forward or revert Git, verify smoke tests and Flyway order, communicate MTTR, and add a gate so this failure class is caught pre-prod next time.

---
### 9. Matrix and parallelism

**Short answer:** Matrix builds test multiple JDK versions or modules in parallel; parallelism caps wall-clock time. Balance cost versus coverage—do not matrix every microservice on every PR without path filters. Measure impact with DORA metrics and document rollback paths before changing prod gates.

#### What it is
Matrix and parallelism is a core practice in modern delivery for Spring microservices on AKS. It connects developer workflow to production safety—artifacts, gates, GitOps, and observability—not just running Jenkins jobs. Interviewers want trade-offs, failure modes, and how you measured improvement with DORA metrics.

#### How it works (internals)
Pipelines trigger on git events, run on ephemeral agents, publish immutable artifacts, and promote through environments with approvals. For matrix and parallelism, wire the check into the earliest stage that has enough context—usually PR for tests and main for deploy. Integrate with ACR, Key Vault or OIDC, and Argo CD for cluster sync. Failed stages should emit structured logs and failure class tags for MTTR tracking.

#### When to use / when NOT to use
Adopt when team size or compliance requires repeatable delivery. Skip heavyweight gates for throwaway prototypes. For Matrix and parallelism, enforce on main and prod paths; allow faster feedback loops on feature branches where safe. Never bypass prod gates without break-glass documentation and post-incident restore of controls.

#### Production example
On `order-service`, we applied matrix and parallelism in the pipeline: PR blocked on failure, main published digest `sha256:abc…`, GitOps PR updated `values-prod.yaml`, smoke tests passed, and rollback was a Git revert tested in staging first. Change failure rate dropped after we classified flakes and added quarantine policy.

#### Common mistakes
- Manual prod deploy bypassing pipeline
- No path filters in monorepo—wasted CI minutes
- Secrets in workflow YAML or logs
- Treating green CI as optional before merge

#### Interview follow-ups (with model answers)

**Q:** How does Matrix and parallelism affect rollback and MTTR?
**A:** Rollback is fast only when artifacts are immutable and cluster desired state lives in Git. I revert the GitOps PR or Helm revision, re-run smoke tests against the same image digest, and verify database migration compatibility. MTTR improves when prod promotion is reproducible and not a manual kubectl hotfix. I measure time from failed deploy to restored SLO and track failure class in a dashboard.

**Q:** What gate would you add after a failure involving Matrix and parallelism?
**A:** I classify the failure (flake, infra, quality, security, deploy) and add an automated guard in the right stage. Examples: quarantine flaky integration tests, ephemeral runners with disk cleanup, required Trivy/Sonar on main, or environment approval for production. Track recurrence quarterly and tie to DORA change failure rate separately from PR red builds.

**Q:** How do you explain Matrix and parallelism to a team new to CI/CD on Spring and AKS?
**A:** I walk a concrete path: PR runs Maven verify and scans; merge publishes a signed image to ACR; a GitOps PR updates Helm values; Argo CD syncs to AKS; smoke tests hit `/actuator/health`. I emphasize CI validates change, CD/GitOps promotes immutable artifacts, and main stays green with feature flags for incomplete work.

#### Scenario probe

**Situation:** Production deploy failed after a green PR; the panel asks how Matrix and parallelism fits your response.

**Model answer:** I timeline the pipeline: which stage failed, which digest was promoted, whether Argo drifted from Git. I roll forward or revert Git, verify smoke tests and Flyway order, communicate MTTR, and add a gate so this failure class is caught pre-prod next time.

---
### 10. Testcontainers in CI

**Short answer:** Integration tests spin real Postgres, Kafka, or Redis in Docker during CI. Requires privileged runners or Docker-in-Docker; slower but catches wiring bugs unit tests miss. Ryuk cleanup and resource limits prevent orphaned containers.

#### What it is
Testcontainers in CI is a core practice in modern delivery for Spring microservices on AKS. It connects developer workflow to production safety—artifacts, gates, GitOps, and observability—not just running Jenkins jobs. Interviewers want trade-offs, failure modes, and how you measured improvement with DORA metrics.

#### How it works (internals)
Pipelines trigger on git events, run on ephemeral agents, publish immutable artifacts, and promote through environments with approvals. For testcontainers in ci, wire the check into the earliest stage that has enough context—usually PR for tests and main for deploy. Integrate with ACR, Key Vault or OIDC, and Argo CD for cluster sync. Failed stages should emit structured logs and failure class tags for MTTR tracking.

#### When to use / when NOT to use
Adopt when team size or compliance requires repeatable delivery. Skip heavyweight gates for throwaway prototypes. For Testcontainers in CI, enforce on main and prod paths; allow faster feedback loops on feature branches where safe. Never bypass prod gates without break-glass documentation and post-incident restore of controls.

#### Production example
On `order-service`, we applied testcontainers in ci in the pipeline: PR blocked on failure, main published digest `sha256:abc…`, GitOps PR updated `values-prod.yaml`, smoke tests passed, and rollback was a Git revert tested in staging first. Change failure rate dropped after we classified flakes and added quarantine policy.

#### Common mistakes
- Manual prod deploy bypassing pipeline
- No path filters in monorepo—wasted CI minutes
- Secrets in workflow YAML or logs
- Treating green CI as optional before merge

#### Interview follow-ups (with model answers)

**Q:** How does Testcontainers in CI affect rollback and MTTR?
**A:** Rollback is fast only when artifacts are immutable and cluster desired state lives in Git. I revert the GitOps PR or Helm revision, re-run smoke tests against the same image digest, and verify database migration compatibility. MTTR improves when prod promotion is reproducible and not a manual kubectl hotfix. I measure time from failed deploy to restored SLO and track failure class in a dashboard.

**Q:** What gate would you add after a failure involving Testcontainers in CI?
**A:** I classify the failure (flake, infra, quality, security, deploy) and add an automated guard in the right stage. Examples: quarantine flaky integration tests, ephemeral runners with disk cleanup, required Trivy/Sonar on main, or environment approval for production. Track recurrence quarterly and tie to DORA change failure rate separately from PR red builds.

**Q:** How do you explain Testcontainers in CI to a team new to CI/CD on Spring and AKS?
**A:** I walk a concrete path: PR runs Maven verify and scans; merge publishes a signed image to ACR; a GitOps PR updates Helm values; Argo CD syncs to AKS; smoke tests hit `/actuator/health`. I emphasize CI validates change, CD/GitOps promotes immutable artifacts, and main stays green with feature flags for incomplete work.

#### Scenario probe

**Situation:** Production deploy failed after a green PR; the panel asks how Testcontainers in CI fits your response.

**Model answer:** I timeline the pipeline: which stage failed, which digest was promoted, whether Argo drifted from Git. I roll forward or revert Git, verify smoke tests and Flyway order, communicate MTTR, and add a gate so this failure class is caught pre-prod next time.

---
### 11. Flaky tests

**Short answer:** Flaky tests erode trust in CI—quarantine with owner SLA, fix or delete. Do not 're-run until green' on main without classification. Measure impact with DORA metrics and document rollback paths before changing prod gates.

#### What it is
Flaky tests is a core practice in modern delivery for Spring microservices on AKS. It connects developer workflow to production safety—artifacts, gates, GitOps, and observability—not just running Jenkins jobs. Interviewers want trade-offs, failure modes, and how you measured improvement with DORA metrics.

#### How it works (internals)
Pipelines trigger on git events, run on ephemeral agents, publish immutable artifacts, and promote through environments with approvals. For flaky tests, wire the check into the earliest stage that has enough context—usually PR for tests and main for deploy. Integrate with ACR, Key Vault or OIDC, and Argo CD for cluster sync. Failed stages should emit structured logs and failure class tags for MTTR tracking.

#### When to use / when NOT to use
Adopt when team size or compliance requires repeatable delivery. Skip heavyweight gates for throwaway prototypes. For Flaky tests, enforce on main and prod paths; allow faster feedback loops on feature branches where safe. Never bypass prod gates without break-glass documentation and post-incident restore of controls.

#### Production example
On `order-service`, we applied flaky tests in the pipeline: PR blocked on failure, main published digest `sha256:abc…`, GitOps PR updated `values-prod.yaml`, smoke tests passed, and rollback was a Git revert tested in staging first. Change failure rate dropped after we classified flakes and added quarantine policy.

#### Common mistakes
- Manual prod deploy bypassing pipeline
- No path filters in monorepo—wasted CI minutes
- Secrets in workflow YAML or logs
- Treating green CI as optional before merge

#### Interview follow-ups (with model answers)

**Q:** How does Flaky tests affect rollback and MTTR?
**A:** Rollback is fast only when artifacts are immutable and cluster desired state lives in Git. I revert the GitOps PR or Helm revision, re-run smoke tests against the same image digest, and verify database migration compatibility. MTTR improves when prod promotion is reproducible and not a manual kubectl hotfix. I measure time from failed deploy to restored SLO and track failure class in a dashboard.

**Q:** What gate would you add after a failure involving Flaky tests?
**A:** I classify the failure (flake, infra, quality, security, deploy) and add an automated guard in the right stage. Examples: quarantine flaky integration tests, ephemeral runners with disk cleanup, required Trivy/Sonar on main, or environment approval for production. Track recurrence quarterly and tie to DORA change failure rate separately from PR red builds.

**Q:** How do you explain Flaky tests to a team new to CI/CD on Spring and AKS?
**A:** I walk a concrete path: PR runs Maven verify and scans; merge publishes a signed image to ACR; a GitOps PR updates Helm values; Argo CD syncs to AKS; smoke tests hit `/actuator/health`. I emphasize CI validates change, CD/GitOps promotes immutable artifacts, and main stays green with feature flags for incomplete work.

#### Scenario probe

**Situation:** Production deploy failed after a green PR; the panel asks how Flaky tests fits your response.

**Model answer:** I timeline the pipeline: which stage failed, which digest was promoted, whether Argo drifted from Git. I roll forward or revert Git, verify smoke tests and Flyway order, communicate MTTR, and add a gate so this failure class is caught pre-prod next time.

---
### 12. Security scanning

**Short answer:** Shift-left SAST, dependency scan, container scan in CI. Block on critical CVEs with waiver process; scan the image you deploy, not just the repo. Measure impact with DORA metrics and document rollback paths before changing prod gates.

#### What it is
Security scanning is a core practice in modern delivery for Spring microservices on AKS. It connects developer workflow to production safety—artifacts, gates, GitOps, and observability—not just running Jenkins jobs. Interviewers want trade-offs, failure modes, and how you measured improvement with DORA metrics.

#### How it works (internals)
Pipelines trigger on git events, run on ephemeral agents, publish immutable artifacts, and promote through environments with approvals. For security scanning, wire the check into the earliest stage that has enough context—usually PR for tests and main for deploy. Integrate with ACR, Key Vault or OIDC, and Argo CD for cluster sync. Failed stages should emit structured logs and failure class tags for MTTR tracking.

#### When to use / when NOT to use
Adopt when team size or compliance requires repeatable delivery. Skip heavyweight gates for throwaway prototypes. For Security scanning, enforce on main and prod paths; allow faster feedback loops on feature branches where safe. Never bypass prod gates without break-glass documentation and post-incident restore of controls.

#### Production example
On `order-service`, we applied security scanning in the pipeline: PR blocked on failure, main published digest `sha256:abc…`, GitOps PR updated `values-prod.yaml`, smoke tests passed, and rollback was a Git revert tested in staging first. Change failure rate dropped after we classified flakes and added quarantine policy.

#### Common mistakes
- Manual prod deploy bypassing pipeline
- No path filters in monorepo—wasted CI minutes
- Secrets in workflow YAML or logs
- Treating green CI as optional before merge

#### Interview follow-ups (with model answers)

**Q:** How does Security scanning affect rollback and MTTR?
**A:** Rollback is fast only when artifacts are immutable and cluster desired state lives in Git. I revert the GitOps PR or Helm revision, re-run smoke tests against the same image digest, and verify database migration compatibility. MTTR improves when prod promotion is reproducible and not a manual kubectl hotfix. I measure time from failed deploy to restored SLO and track failure class in a dashboard.

**Q:** What gate would you add after a failure involving Security scanning?
**A:** I classify the failure (flake, infra, quality, security, deploy) and add an automated guard in the right stage. Examples: quarantine flaky integration tests, ephemeral runners with disk cleanup, required Trivy/Sonar on main, or environment approval for production. Track recurrence quarterly and tie to DORA change failure rate separately from PR red builds.

**Q:** How do you explain Security scanning to a team new to CI/CD on Spring and AKS?
**A:** I walk a concrete path: PR runs Maven verify and scans; merge publishes a signed image to ACR; a GitOps PR updates Helm values; Argo CD syncs to AKS; smoke tests hit `/actuator/health`. I emphasize CI validates change, CD/GitOps promotes immutable artifacts, and main stays green with feature flags for incomplete work.

#### Scenario probe

**Situation:** Production deploy failed after a green PR; the panel asks how Security scanning fits your response.

**Model answer:** I timeline the pipeline: which stage failed, which digest was promoted, whether Argo drifted from Git. I roll forward or revert Git, verify smoke tests and Flyway order, communicate MTTR, and add a gate so this failure class is caught pre-prod next time.

---
### 13. SBOM

**Short answer:** Software Bill of Materials lists dependencies for incident response. Generate CycloneDX/SPDX in CI; store beside image in registry. Measure impact with DORA metrics and document rollback paths before changing prod gates.

#### What it is
SBOM is a core practice in modern delivery for Spring microservices on AKS. It connects developer workflow to production safety—artifacts, gates, GitOps, and observability—not just running Jenkins jobs. Interviewers want trade-offs, failure modes, and how you measured improvement with DORA metrics.

#### How it works (internals)
Pipelines trigger on git events, run on ephemeral agents, publish immutable artifacts, and promote through environments with approvals. For sbom, wire the check into the earliest stage that has enough context—usually PR for tests and main for deploy. Integrate with ACR, Key Vault or OIDC, and Argo CD for cluster sync. Failed stages should emit structured logs and failure class tags for MTTR tracking.

#### When to use / when NOT to use
Adopt when team size or compliance requires repeatable delivery. Skip heavyweight gates for throwaway prototypes. For SBOM, enforce on main and prod paths; allow faster feedback loops on feature branches where safe. Never bypass prod gates without break-glass documentation and post-incident restore of controls.

#### Production example
On `order-service`, we applied sbom in the pipeline: PR blocked on failure, main published digest `sha256:abc…`, GitOps PR updated `values-prod.yaml`, smoke tests passed, and rollback was a Git revert tested in staging first. Change failure rate dropped after we classified flakes and added quarantine policy.

#### Common mistakes
- Manual prod deploy bypassing pipeline
- No path filters in monorepo—wasted CI minutes
- Secrets in workflow YAML or logs
- Treating green CI as optional before merge

#### Interview follow-ups (with model answers)

**Q:** How does SBOM affect rollback and MTTR?
**A:** Rollback is fast only when artifacts are immutable and cluster desired state lives in Git. I revert the GitOps PR or Helm revision, re-run smoke tests against the same image digest, and verify database migration compatibility. MTTR improves when prod promotion is reproducible and not a manual kubectl hotfix. I measure time from failed deploy to restored SLO and track failure class in a dashboard.

**Q:** What gate would you add after a failure involving SBOM?
**A:** I classify the failure (flake, infra, quality, security, deploy) and add an automated guard in the right stage. Examples: quarantine flaky integration tests, ephemeral runners with disk cleanup, required Trivy/Sonar on main, or environment approval for production. Track recurrence quarterly and tie to DORA change failure rate separately from PR red builds.

**Q:** How do you explain SBOM to a team new to CI/CD on Spring and AKS?
**A:** I walk a concrete path: PR runs Maven verify and scans; merge publishes a signed image to ACR; a GitOps PR updates Helm values; Argo CD syncs to AKS; smoke tests hit `/actuator/health`. I emphasize CI validates change, CD/GitOps promotes immutable artifacts, and main stays green with feature flags for incomplete work.

#### Scenario probe

**Situation:** Production deploy failed after a green PR; the panel asks how SBOM fits your response.

**Model answer:** I timeline the pipeline: which stage failed, which digest was promoted, whether Argo drifted from Git. I roll forward or revert Git, verify smoke tests and Flyway order, communicate MTTR, and add a gate so this failure class is caught pre-prod next time.

---
### 14. Signing

**Short answer:** Sign container images with cosign; verify at deploy admission. Pairs with provenance for supply-chain compliance. Measure impact with DORA metrics and document rollback paths before changing prod gates.

#### What it is
Signing is a core practice in modern delivery for Spring microservices on AKS. It connects developer workflow to production safety—artifacts, gates, GitOps, and observability—not just running Jenkins jobs. Interviewers want trade-offs, failure modes, and how you measured improvement with DORA metrics.

#### How it works (internals)
Pipelines trigger on git events, run on ephemeral agents, publish immutable artifacts, and promote through environments with approvals. For signing, wire the check into the earliest stage that has enough context—usually PR for tests and main for deploy. Integrate with ACR, Key Vault or OIDC, and Argo CD for cluster sync. Failed stages should emit structured logs and failure class tags for MTTR tracking.

#### When to use / when NOT to use
Adopt when team size or compliance requires repeatable delivery. Skip heavyweight gates for throwaway prototypes. For Signing, enforce on main and prod paths; allow faster feedback loops on feature branches where safe. Never bypass prod gates without break-glass documentation and post-incident restore of controls.

#### Production example
On `order-service`, we applied signing in the pipeline: PR blocked on failure, main published digest `sha256:abc…`, GitOps PR updated `values-prod.yaml`, smoke tests passed, and rollback was a Git revert tested in staging first. Change failure rate dropped after we classified flakes and added quarantine policy.

#### Common mistakes
- Manual prod deploy bypassing pipeline
- No path filters in monorepo—wasted CI minutes
- Secrets in workflow YAML or logs
- Treating green CI as optional before merge

#### Interview follow-ups (with model answers)

**Q:** How does Signing affect rollback and MTTR?
**A:** Rollback is fast only when artifacts are immutable and cluster desired state lives in Git. I revert the GitOps PR or Helm revision, re-run smoke tests against the same image digest, and verify database migration compatibility. MTTR improves when prod promotion is reproducible and not a manual kubectl hotfix. I measure time from failed deploy to restored SLO and track failure class in a dashboard.

**Q:** What gate would you add after a failure involving Signing?
**A:** I classify the failure (flake, infra, quality, security, deploy) and add an automated guard in the right stage. Examples: quarantine flaky integration tests, ephemeral runners with disk cleanup, required Trivy/Sonar on main, or environment approval for production. Track recurrence quarterly and tie to DORA change failure rate separately from PR red builds.

**Q:** How do you explain Signing to a team new to CI/CD on Spring and AKS?
**A:** I walk a concrete path: PR runs Maven verify and scans; merge publishes a signed image to ACR; a GitOps PR updates Helm values; Argo CD syncs to AKS; smoke tests hit `/actuator/health`. I emphasize CI validates change, CD/GitOps promotes immutable artifacts, and main stays green with feature flags for incomplete work.

#### Scenario probe

**Situation:** Production deploy failed after a green PR; the panel asks how Signing fits your response.

**Model answer:** I timeline the pipeline: which stage failed, which digest was promoted, whether Argo drifted from Git. I roll forward or revert Git, verify smoke tests and Flyway order, communicate MTTR, and add a gate so this failure class is caught pre-prod next time.

---
### 15. Secrets in CI

**Short answer:** Secrets from vault or OIDC—never echo, never in logs. GitHub/Azure secret scopes per environment; rotate on leak. Measure impact with DORA metrics and document rollback paths before changing prod gates.

#### What it is
Secrets in CI is a core practice in modern delivery for Spring microservices on AKS. It connects developer workflow to production safety—artifacts, gates, GitOps, and observability—not just running Jenkins jobs. Interviewers want trade-offs, failure modes, and how you measured improvement with DORA metrics.

#### How it works (internals)
Pipelines trigger on git events, run on ephemeral agents, publish immutable artifacts, and promote through environments with approvals. For secrets in ci, wire the check into the earliest stage that has enough context—usually PR for tests and main for deploy. Integrate with ACR, Key Vault or OIDC, and Argo CD for cluster sync. Failed stages should emit structured logs and failure class tags for MTTR tracking.

#### When to use / when NOT to use
Adopt when team size or compliance requires repeatable delivery. Skip heavyweight gates for throwaway prototypes. For Secrets in CI, enforce on main and prod paths; allow faster feedback loops on feature branches where safe. Never bypass prod gates without break-glass documentation and post-incident restore of controls.

#### Production example
On `order-service`, we applied secrets in ci in the pipeline: PR blocked on failure, main published digest `sha256:abc…`, GitOps PR updated `values-prod.yaml`, smoke tests passed, and rollback was a Git revert tested in staging first. Change failure rate dropped after we classified flakes and added quarantine policy.

#### Common mistakes
- Manual prod deploy bypassing pipeline
- No path filters in monorepo—wasted CI minutes
- Secrets in workflow YAML or logs
- Treating green CI as optional before merge

#### Interview follow-ups (with model answers)

**Q:** How does Secrets in CI affect rollback and MTTR?
**A:** Rollback is fast only when artifacts are immutable and cluster desired state lives in Git. I revert the GitOps PR or Helm revision, re-run smoke tests against the same image digest, and verify database migration compatibility. MTTR improves when prod promotion is reproducible and not a manual kubectl hotfix. I measure time from failed deploy to restored SLO and track failure class in a dashboard.

**Q:** What gate would you add after a failure involving Secrets in CI?
**A:** I classify the failure (flake, infra, quality, security, deploy) and add an automated guard in the right stage. Examples: quarantine flaky integration tests, ephemeral runners with disk cleanup, required Trivy/Sonar on main, or environment approval for production. Track recurrence quarterly and tie to DORA change failure rate separately from PR red builds.

**Q:** How do you explain Secrets in CI to a team new to CI/CD on Spring and AKS?
**A:** I walk a concrete path: PR runs Maven verify and scans; merge publishes a signed image to ACR; a GitOps PR updates Helm values; Argo CD syncs to AKS; smoke tests hit `/actuator/health`. I emphasize CI validates change, CD/GitOps promotes immutable artifacts, and main stays green with feature flags for incomplete work.

#### Scenario probe

**Situation:** Production deploy failed after a green PR; the panel asks how Secrets in CI fits your response.

**Model answer:** I timeline the pipeline: which stage failed, which digest was promoted, whether Argo drifted from Git. I roll forward or revert Git, verify smoke tests and Flyway order, communicate MTTR, and add a gate so this failure class is caught pre-prod next time.

---
### 16. Environments and approvals

**Short answer:** GitHub Environments / ADO environments add required reviewers for prod. Map to SoD: builder cannot approve own prod deploy. Measure impact with DORA metrics and document rollback paths before changing prod gates.

#### What it is
Environments and approvals is a core practice in modern delivery for Spring microservices on AKS. It connects developer workflow to production safety—artifacts, gates, GitOps, and observability—not just running Jenkins jobs. Interviewers want trade-offs, failure modes, and how you measured improvement with DORA metrics.

#### How it works (internals)
Pipelines trigger on git events, run on ephemeral agents, publish immutable artifacts, and promote through environments with approvals. For environments and approvals, wire the check into the earliest stage that has enough context—usually PR for tests and main for deploy. Integrate with ACR, Key Vault or OIDC, and Argo CD for cluster sync. Failed stages should emit structured logs and failure class tags for MTTR tracking.

#### When to use / when NOT to use
Adopt when team size or compliance requires repeatable delivery. Skip heavyweight gates for throwaway prototypes. For Environments and approvals, enforce on main and prod paths; allow faster feedback loops on feature branches where safe. Never bypass prod gates without break-glass documentation and post-incident restore of controls.

#### Production example
On `order-service`, we applied environments and approvals in the pipeline: PR blocked on failure, main published digest `sha256:abc…`, GitOps PR updated `values-prod.yaml`, smoke tests passed, and rollback was a Git revert tested in staging first. Change failure rate dropped after we classified flakes and added quarantine policy.

#### Common mistakes
- Manual prod deploy bypassing pipeline
- No path filters in monorepo—wasted CI minutes
- Secrets in workflow YAML or logs
- Treating green CI as optional before merge

#### Interview follow-ups (with model answers)

**Q:** How does Environments and approvals affect rollback and MTTR?
**A:** Rollback is fast only when artifacts are immutable and cluster desired state lives in Git. I revert the GitOps PR or Helm revision, re-run smoke tests against the same image digest, and verify database migration compatibility. MTTR improves when prod promotion is reproducible and not a manual kubectl hotfix. I measure time from failed deploy to restored SLO and track failure class in a dashboard.

**Q:** What gate would you add after a failure involving Environments and approvals?
**A:** I classify the failure (flake, infra, quality, security, deploy) and add an automated guard in the right stage. Examples: quarantine flaky integration tests, ephemeral runners with disk cleanup, required Trivy/Sonar on main, or environment approval for production. Track recurrence quarterly and tie to DORA change failure rate separately from PR red builds.

**Q:** How do you explain Environments and approvals to a team new to CI/CD on Spring and AKS?
**A:** I walk a concrete path: PR runs Maven verify and scans; merge publishes a signed image to ACR; a GitOps PR updates Helm values; Argo CD syncs to AKS; smoke tests hit `/actuator/health`. I emphasize CI validates change, CD/GitOps promotes immutable artifacts, and main stays green with feature flags for incomplete work.

#### Scenario probe

**Situation:** Production deploy failed after a green PR; the panel asks how Environments and approvals fits your response.

**Model answer:** I timeline the pipeline: which stage failed, which digest was promoted, whether Argo drifted from Git. I roll forward or revert Git, verify smoke tests and Flyway order, communicate MTTR, and add a gate so this failure class is caught pre-prod next time.

---
### 17. Deployment strategies

**Short answer:** Rolling, blue/green, canary—pick based on blast radius and observability. Spring on K8s often rolling with PDB; canary needs metrics analysis. Measure impact with DORA metrics and document rollback paths before changing prod gates.

#### What it is
Deployment strategies is a core practice in modern delivery for Spring microservices on AKS. It connects developer workflow to production safety—artifacts, gates, GitOps, and observability—not just running Jenkins jobs. Interviewers want trade-offs, failure modes, and how you measured improvement with DORA metrics.

#### How it works (internals)
Pipelines trigger on git events, run on ephemeral agents, publish immutable artifacts, and promote through environments with approvals. For deployment strategies, wire the check into the earliest stage that has enough context—usually PR for tests and main for deploy. Integrate with ACR, Key Vault or OIDC, and Argo CD for cluster sync. Failed stages should emit structured logs and failure class tags for MTTR tracking.

#### When to use / when NOT to use
Adopt when team size or compliance requires repeatable delivery. Skip heavyweight gates for throwaway prototypes. For Deployment strategies, enforce on main and prod paths; allow faster feedback loops on feature branches where safe. Never bypass prod gates without break-glass documentation and post-incident restore of controls.

#### Production example
On `order-service`, we applied deployment strategies in the pipeline: PR blocked on failure, main published digest `sha256:abc…`, GitOps PR updated `values-prod.yaml`, smoke tests passed, and rollback was a Git revert tested in staging first. Change failure rate dropped after we classified flakes and added quarantine policy.

#### Common mistakes
- Manual prod deploy bypassing pipeline
- No path filters in monorepo—wasted CI minutes
- Secrets in workflow YAML or logs
- Treating green CI as optional before merge

#### Interview follow-ups (with model answers)

**Q:** How does Deployment strategies affect rollback and MTTR?
**A:** Rollback is fast only when artifacts are immutable and cluster desired state lives in Git. I revert the GitOps PR or Helm revision, re-run smoke tests against the same image digest, and verify database migration compatibility. MTTR improves when prod promotion is reproducible and not a manual kubectl hotfix. I measure time from failed deploy to restored SLO and track failure class in a dashboard.

**Q:** What gate would you add after a failure involving Deployment strategies?
**A:** I classify the failure (flake, infra, quality, security, deploy) and add an automated guard in the right stage. Examples: quarantine flaky integration tests, ephemeral runners with disk cleanup, required Trivy/Sonar on main, or environment approval for production. Track recurrence quarterly and tie to DORA change failure rate separately from PR red builds.

**Q:** How do you explain Deployment strategies to a team new to CI/CD on Spring and AKS?
**A:** I walk a concrete path: PR runs Maven verify and scans; merge publishes a signed image to ACR; a GitOps PR updates Helm values; Argo CD syncs to AKS; smoke tests hit `/actuator/health`. I emphasize CI validates change, CD/GitOps promotes immutable artifacts, and main stays green with feature flags for incomplete work.

#### Scenario probe

**Situation:** Production deploy failed after a green PR; the panel asks how Deployment strategies fits your response.

**Model answer:** I timeline the pipeline: which stage failed, which digest was promoted, whether Argo drifted from Git. I roll forward or revert Git, verify smoke tests and Flyway order, communicate MTTR, and add a gate so this failure class is caught pre-prod next time.

---
### 18. Migration order

**Short answer:** Run Flyway/Liquibase before scaling new app pods—Job or Helm pre-hook. Expand/contract for zero-downtime schema. Measure impact with DORA metrics and document rollback paths before changing prod gates.

#### What it is
Migration order is a core practice in modern delivery for Spring microservices on AKS. It connects developer workflow to production safety—artifacts, gates, GitOps, and observability—not just running Jenkins jobs. Interviewers want trade-offs, failure modes, and how you measured improvement with DORA metrics.

#### How it works (internals)
Pipelines trigger on git events, run on ephemeral agents, publish immutable artifacts, and promote through environments with approvals. For migration order, wire the check into the earliest stage that has enough context—usually PR for tests and main for deploy. Integrate with ACR, Key Vault or OIDC, and Argo CD for cluster sync. Failed stages should emit structured logs and failure class tags for MTTR tracking.

#### When to use / when NOT to use
Adopt when team size or compliance requires repeatable delivery. Skip heavyweight gates for throwaway prototypes. For Migration order, enforce on main and prod paths; allow faster feedback loops on feature branches where safe. Never bypass prod gates without break-glass documentation and post-incident restore of controls.

#### Production example
On `order-service`, we applied migration order in the pipeline: PR blocked on failure, main published digest `sha256:abc…`, GitOps PR updated `values-prod.yaml`, smoke tests passed, and rollback was a Git revert tested in staging first. Change failure rate dropped after we classified flakes and added quarantine policy.

#### Common mistakes
- Manual prod deploy bypassing pipeline
- No path filters in monorepo—wasted CI minutes
- Secrets in workflow YAML or logs
- Treating green CI as optional before merge

#### Interview follow-ups (with model answers)

**Q:** How does Migration order affect rollback and MTTR?
**A:** Rollback is fast only when artifacts are immutable and cluster desired state lives in Git. I revert the GitOps PR or Helm revision, re-run smoke tests against the same image digest, and verify database migration compatibility. MTTR improves when prod promotion is reproducible and not a manual kubectl hotfix. I measure time from failed deploy to restored SLO and track failure class in a dashboard.

**Q:** What gate would you add after a failure involving Migration order?
**A:** I classify the failure (flake, infra, quality, security, deploy) and add an automated guard in the right stage. Examples: quarantine flaky integration tests, ephemeral runners with disk cleanup, required Trivy/Sonar on main, or environment approval for production. Track recurrence quarterly and tie to DORA change failure rate separately from PR red builds.

**Q:** How do you explain Migration order to a team new to CI/CD on Spring and AKS?
**A:** I walk a concrete path: PR runs Maven verify and scans; merge publishes a signed image to ACR; a GitOps PR updates Helm values; Argo CD syncs to AKS; smoke tests hit `/actuator/health`. I emphasize CI validates change, CD/GitOps promotes immutable artifacts, and main stays green with feature flags for incomplete work.

#### Scenario probe

**Situation:** Production deploy failed after a green PR; the panel asks how Migration order fits your response.

**Model answer:** I timeline the pipeline: which stage failed, which digest was promoted, whether Argo drifted from Git. I roll forward or revert Git, verify smoke tests and Flyway order, communicate MTTR, and add a gate so this failure class is caught pre-prod next time.

---
### 19. Rollback of app vs DB

**Short answer:** App rollback is Git revert; DB rollback is hard—forward-fix preferred. Never auto-downgrade Flyway in prod without playbook. Measure impact with DORA metrics and document rollback paths before changing prod gates.

#### What it is
Rollback of app vs DB is a core practice in modern delivery for Spring microservices on AKS. It connects developer workflow to production safety—artifacts, gates, GitOps, and observability—not just running Jenkins jobs. Interviewers want trade-offs, failure modes, and how you measured improvement with DORA metrics.

#### How it works (internals)
Pipelines trigger on git events, run on ephemeral agents, publish immutable artifacts, and promote through environments with approvals. For rollback of app vs db, wire the check into the earliest stage that has enough context—usually PR for tests and main for deploy. Integrate with ACR, Key Vault or OIDC, and Argo CD for cluster sync. Failed stages should emit structured logs and failure class tags for MTTR tracking.

#### When to use / when NOT to use
Adopt when team size or compliance requires repeatable delivery. Skip heavyweight gates for throwaway prototypes. For Rollback of app vs DB, enforce on main and prod paths; allow faster feedback loops on feature branches where safe. Never bypass prod gates without break-glass documentation and post-incident restore of controls.

#### Production example
On `order-service`, we applied rollback of app vs db in the pipeline: PR blocked on failure, main published digest `sha256:abc…`, GitOps PR updated `values-prod.yaml`, smoke tests passed, and rollback was a Git revert tested in staging first. Change failure rate dropped after we classified flakes and added quarantine policy.

#### Common mistakes
- Manual prod deploy bypassing pipeline
- No path filters in monorepo—wasted CI minutes
- Secrets in workflow YAML or logs
- Treating green CI as optional before merge

#### Interview follow-ups (with model answers)

**Q:** How does Rollback of app vs DB affect rollback and MTTR?
**A:** Rollback is fast only when artifacts are immutable and cluster desired state lives in Git. I revert the GitOps PR or Helm revision, re-run smoke tests against the same image digest, and verify database migration compatibility. MTTR improves when prod promotion is reproducible and not a manual kubectl hotfix. I measure time from failed deploy to restored SLO and track failure class in a dashboard.

**Q:** What gate would you add after a failure involving Rollback of app vs DB?
**A:** I classify the failure (flake, infra, quality, security, deploy) and add an automated guard in the right stage. Examples: quarantine flaky integration tests, ephemeral runners with disk cleanup, required Trivy/Sonar on main, or environment approval for production. Track recurrence quarterly and tie to DORA change failure rate separately from PR red builds.

**Q:** How do you explain Rollback of app vs DB to a team new to CI/CD on Spring and AKS?
**A:** I walk a concrete path: PR runs Maven verify and scans; merge publishes a signed image to ACR; a GitOps PR updates Helm values; Argo CD syncs to AKS; smoke tests hit `/actuator/health`. I emphasize CI validates change, CD/GitOps promotes immutable artifacts, and main stays green with feature flags for incomplete work.

#### Scenario probe

**Situation:** Production deploy failed after a green PR; the panel asks how Rollback of app vs DB fits your response.

**Model answer:** I timeline the pipeline: which stage failed, which digest was promoted, whether Argo drifted from Git. I roll forward or revert Git, verify smoke tests and Flyway order, communicate MTTR, and add a gate so this failure class is caught pre-prod next time.

---
### 20. Helm in CD

**Short answer:** Helm packages K8s manifests; CD updates chart version or values with image digest. Use `helm upgrade --atomic` in automation or GitOps equivalent. Measure impact with DORA metrics and document rollback paths before changing prod gates.

#### What it is
Helm in CD is a core practice in modern delivery for Spring microservices on AKS. It connects developer workflow to production safety—artifacts, gates, GitOps, and observability—not just running Jenkins jobs. Interviewers want trade-offs, failure modes, and how you measured improvement with DORA metrics.

#### How it works (internals)
Pipelines trigger on git events, run on ephemeral agents, publish immutable artifacts, and promote through environments with approvals. For helm in cd, wire the check into the earliest stage that has enough context—usually PR for tests and main for deploy. Integrate with ACR, Key Vault or OIDC, and Argo CD for cluster sync. Failed stages should emit structured logs and failure class tags for MTTR tracking.

#### When to use / when NOT to use
Adopt when team size or compliance requires repeatable delivery. Skip heavyweight gates for throwaway prototypes. For Helm in CD, enforce on main and prod paths; allow faster feedback loops on feature branches where safe. Never bypass prod gates without break-glass documentation and post-incident restore of controls.

#### Production example
On `order-service`, we applied helm in cd in the pipeline: PR blocked on failure, main published digest `sha256:abc…`, GitOps PR updated `values-prod.yaml`, smoke tests passed, and rollback was a Git revert tested in staging first. Change failure rate dropped after we classified flakes and added quarantine policy.

#### Common mistakes
- Manual prod deploy bypassing pipeline
- No path filters in monorepo—wasted CI minutes
- Secrets in workflow YAML or logs
- Treating green CI as optional before merge

#### Interview follow-ups (with model answers)

**Q:** How does Helm in CD affect rollback and MTTR?
**A:** Rollback is fast only when artifacts are immutable and cluster desired state lives in Git. I revert the GitOps PR or Helm revision, re-run smoke tests against the same image digest, and verify database migration compatibility. MTTR improves when prod promotion is reproducible and not a manual kubectl hotfix. I measure time from failed deploy to restored SLO and track failure class in a dashboard.

**Q:** What gate would you add after a failure involving Helm in CD?
**A:** I classify the failure (flake, infra, quality, security, deploy) and add an automated guard in the right stage. Examples: quarantine flaky integration tests, ephemeral runners with disk cleanup, required Trivy/Sonar on main, or environment approval for production. Track recurrence quarterly and tie to DORA change failure rate separately from PR red builds.

**Q:** How do you explain Helm in CD to a team new to CI/CD on Spring and AKS?
**A:** I walk a concrete path: PR runs Maven verify and scans; merge publishes a signed image to ACR; a GitOps PR updates Helm values; Argo CD syncs to AKS; smoke tests hit `/actuator/health`. I emphasize CI validates change, CD/GitOps promotes immutable artifacts, and main stays green with feature flags for incomplete work.

#### Scenario probe

**Situation:** Production deploy failed after a green PR; the panel asks how Helm in CD fits your response.

**Model answer:** I timeline the pipeline: which stage failed, which digest was promoted, whether Argo drifted from Git. I roll forward or revert Git, verify smoke tests and Flyway order, communicate MTTR, and add a gate so this failure class is caught pre-prod next time.

---
### 21. Argo CD sync waves

**Short answer:** Sync waves order CRDs, namespaces, Jobs, Deployments. Migrations as wave -1 or Job before app. Measure impact with DORA metrics and document rollback paths before changing prod gates.

#### What it is
Argo CD sync waves is a core practice in modern delivery for Spring microservices on AKS. It connects developer workflow to production safety—artifacts, gates, GitOps, and observability—not just running Jenkins jobs. Interviewers want trade-offs, failure modes, and how you measured improvement with DORA metrics.

#### How it works (internals)
Pipelines trigger on git events, run on ephemeral agents, publish immutable artifacts, and promote through environments with approvals. For argo cd sync waves, wire the check into the earliest stage that has enough context—usually PR for tests and main for deploy. Integrate with ACR, Key Vault or OIDC, and Argo CD for cluster sync. Failed stages should emit structured logs and failure class tags for MTTR tracking.

#### When to use / when NOT to use
Adopt when team size or compliance requires repeatable delivery. Skip heavyweight gates for throwaway prototypes. For Argo CD sync waves, enforce on main and prod paths; allow faster feedback loops on feature branches where safe. Never bypass prod gates without break-glass documentation and post-incident restore of controls.

#### Production example
On `order-service`, we applied argo cd sync waves in the pipeline: PR blocked on failure, main published digest `sha256:abc…`, GitOps PR updated `values-prod.yaml`, smoke tests passed, and rollback was a Git revert tested in staging first. Change failure rate dropped after we classified flakes and added quarantine policy.

#### Common mistakes
- Manual prod deploy bypassing pipeline
- No path filters in monorepo—wasted CI minutes
- Secrets in workflow YAML or logs
- Treating green CI as optional before merge

#### Interview follow-ups (with model answers)

**Q:** How does Argo CD sync waves affect rollback and MTTR?
**A:** Rollback is fast only when artifacts are immutable and cluster desired state lives in Git. I revert the GitOps PR or Helm revision, re-run smoke tests against the same image digest, and verify database migration compatibility. MTTR improves when prod promotion is reproducible and not a manual kubectl hotfix. I measure time from failed deploy to restored SLO and track failure class in a dashboard.

**Q:** What gate would you add after a failure involving Argo CD sync waves?
**A:** I classify the failure (flake, infra, quality, security, deploy) and add an automated guard in the right stage. Examples: quarantine flaky integration tests, ephemeral runners with disk cleanup, required Trivy/Sonar on main, or environment approval for production. Track recurrence quarterly and tie to DORA change failure rate separately from PR red builds.

**Q:** How do you explain Argo CD sync waves to a team new to CI/CD on Spring and AKS?
**A:** I walk a concrete path: PR runs Maven verify and scans; merge publishes a signed image to ACR; a GitOps PR updates Helm values; Argo CD syncs to AKS; smoke tests hit `/actuator/health`. I emphasize CI validates change, CD/GitOps promotes immutable artifacts, and main stays green with feature flags for incomplete work.

#### Scenario probe

**Situation:** Production deploy failed after a green PR; the panel asks how Argo CD sync waves fits your response.

**Model answer:** I timeline the pipeline: which stage failed, which digest was promoted, whether Argo drifted from Git. I roll forward or revert Git, verify smoke tests and Flyway order, communicate MTTR, and add a gate so this failure class is caught pre-prod next time.

---
### 22. Progressive delivery

**Short answer:** Flagger, Argo Rollouts, or manual canary with Prometheus analysis. Automated rollback on SLO burn. Measure impact with DORA metrics and document rollback paths before changing prod gates.

#### What it is
Progressive delivery is a core practice in modern delivery for Spring microservices on AKS. It connects developer workflow to production safety—artifacts, gates, GitOps, and observability—not just running Jenkins jobs. Interviewers want trade-offs, failure modes, and how you measured improvement with DORA metrics.

#### How it works (internals)
Pipelines trigger on git events, run on ephemeral agents, publish immutable artifacts, and promote through environments with approvals. For progressive delivery, wire the check into the earliest stage that has enough context—usually PR for tests and main for deploy. Integrate with ACR, Key Vault or OIDC, and Argo CD for cluster sync. Failed stages should emit structured logs and failure class tags for MTTR tracking.

#### When to use / when NOT to use
Adopt when team size or compliance requires repeatable delivery. Skip heavyweight gates for throwaway prototypes. For Progressive delivery, enforce on main and prod paths; allow faster feedback loops on feature branches where safe. Never bypass prod gates without break-glass documentation and post-incident restore of controls.

#### Production example
On `order-service`, we applied progressive delivery in the pipeline: PR blocked on failure, main published digest `sha256:abc…`, GitOps PR updated `values-prod.yaml`, smoke tests passed, and rollback was a Git revert tested in staging first. Change failure rate dropped after we classified flakes and added quarantine policy.

#### Common mistakes
- Manual prod deploy bypassing pipeline
- No path filters in monorepo—wasted CI minutes
- Secrets in workflow YAML or logs
- Treating green CI as optional before merge

#### Interview follow-ups (with model answers)

**Q:** How does Progressive delivery affect rollback and MTTR?
**A:** Rollback is fast only when artifacts are immutable and cluster desired state lives in Git. I revert the GitOps PR or Helm revision, re-run smoke tests against the same image digest, and verify database migration compatibility. MTTR improves when prod promotion is reproducible and not a manual kubectl hotfix. I measure time from failed deploy to restored SLO and track failure class in a dashboard.

**Q:** What gate would you add after a failure involving Progressive delivery?
**A:** I classify the failure (flake, infra, quality, security, deploy) and add an automated guard in the right stage. Examples: quarantine flaky integration tests, ephemeral runners with disk cleanup, required Trivy/Sonar on main, or environment approval for production. Track recurrence quarterly and tie to DORA change failure rate separately from PR red builds.

**Q:** How do you explain Progressive delivery to a team new to CI/CD on Spring and AKS?
**A:** I walk a concrete path: PR runs Maven verify and scans; merge publishes a signed image to ACR; a GitOps PR updates Helm values; Argo CD syncs to AKS; smoke tests hit `/actuator/health`. I emphasize CI validates change, CD/GitOps promotes immutable artifacts, and main stays green with feature flags for incomplete work.

#### Scenario probe

**Situation:** Production deploy failed after a green PR; the panel asks how Progressive delivery fits your response.

**Model answer:** I timeline the pipeline: which stage failed, which digest was promoted, whether Argo drifted from Git. I roll forward or revert Git, verify smoke tests and Flyway order, communicate MTTR, and add a gate so this failure class is caught pre-prod next time.

---
### 23. Infra vs app pipelines

**Short answer:** Terraform pipeline separate from app CI; app consumes outputs via remote state or service endpoints. Different cadence and approvers. Measure impact with DORA metrics and document rollback paths before changing prod gates.

#### What it is
Infra vs app pipelines is a core practice in modern delivery for Spring microservices on AKS. It connects developer workflow to production safety—artifacts, gates, GitOps, and observability—not just running Jenkins jobs. Interviewers want trade-offs, failure modes, and how you measured improvement with DORA metrics.

#### How it works (internals)
Pipelines trigger on git events, run on ephemeral agents, publish immutable artifacts, and promote through environments with approvals. For infra vs app pipelines, wire the check into the earliest stage that has enough context—usually PR for tests and main for deploy. Integrate with ACR, Key Vault or OIDC, and Argo CD for cluster sync. Failed stages should emit structured logs and failure class tags for MTTR tracking.

#### When to use / when NOT to use
Adopt when team size or compliance requires repeatable delivery. Skip heavyweight gates for throwaway prototypes. For Infra vs app pipelines, enforce on main and prod paths; allow faster feedback loops on feature branches where safe. Never bypass prod gates without break-glass documentation and post-incident restore of controls.

#### Production example
On `order-service`, we applied infra vs app pipelines in the pipeline: PR blocked on failure, main published digest `sha256:abc…`, GitOps PR updated `values-prod.yaml`, smoke tests passed, and rollback was a Git revert tested in staging first. Change failure rate dropped after we classified flakes and added quarantine policy.

#### Common mistakes
- Manual prod deploy bypassing pipeline
- No path filters in monorepo—wasted CI minutes
- Secrets in workflow YAML or logs
- Treating green CI as optional before merge

#### Interview follow-ups (with model answers)

**Q:** How does Infra vs app pipelines affect rollback and MTTR?
**A:** Rollback is fast only when artifacts are immutable and cluster desired state lives in Git. I revert the GitOps PR or Helm revision, re-run smoke tests against the same image digest, and verify database migration compatibility. MTTR improves when prod promotion is reproducible and not a manual kubectl hotfix. I measure time from failed deploy to restored SLO and track failure class in a dashboard.

**Q:** What gate would you add after a failure involving Infra vs app pipelines?
**A:** I classify the failure (flake, infra, quality, security, deploy) and add an automated guard in the right stage. Examples: quarantine flaky integration tests, ephemeral runners with disk cleanup, required Trivy/Sonar on main, or environment approval for production. Track recurrence quarterly and tie to DORA change failure rate separately from PR red builds.

**Q:** How do you explain Infra vs app pipelines to a team new to CI/CD on Spring and AKS?
**A:** I walk a concrete path: PR runs Maven verify and scans; merge publishes a signed image to ACR; a GitOps PR updates Helm values; Argo CD syncs to AKS; smoke tests hit `/actuator/health`. I emphasize CI validates change, CD/GitOps promotes immutable artifacts, and main stays green with feature flags for incomplete work.

#### Scenario probe

**Situation:** Production deploy failed after a green PR; the panel asks how Infra vs app pipelines fits your response.

**Model answer:** I timeline the pipeline: which stage failed, which digest was promoted, whether Argo drifted from Git. I roll forward or revert Git, verify smoke tests and Flyway order, communicate MTTR, and add a gate so this failure class is caught pre-prod next time.

---
### 24. Monorepo pipelines

**Short answer:** Path filters and change detection build only affected services. Shared workflow templates reduce YAML drift. Measure impact with DORA metrics and document rollback paths before changing prod gates.

#### What it is
Monorepo pipelines is a core practice in modern delivery for Spring microservices on AKS. It connects developer workflow to production safety—artifacts, gates, GitOps, and observability—not just running Jenkins jobs. Interviewers want trade-offs, failure modes, and how you measured improvement with DORA metrics.

#### How it works (internals)
Pipelines trigger on git events, run on ephemeral agents, publish immutable artifacts, and promote through environments with approvals. For monorepo pipelines, wire the check into the earliest stage that has enough context—usually PR for tests and main for deploy. Integrate with ACR, Key Vault or OIDC, and Argo CD for cluster sync. Failed stages should emit structured logs and failure class tags for MTTR tracking.

#### When to use / when NOT to use
Adopt when team size or compliance requires repeatable delivery. Skip heavyweight gates for throwaway prototypes. For Monorepo pipelines, enforce on main and prod paths; allow faster feedback loops on feature branches where safe. Never bypass prod gates without break-glass documentation and post-incident restore of controls.

#### Production example
On `order-service`, we applied monorepo pipelines in the pipeline: PR blocked on failure, main published digest `sha256:abc…`, GitOps PR updated `values-prod.yaml`, smoke tests passed, and rollback was a Git revert tested in staging first. Change failure rate dropped after we classified flakes and added quarantine policy.

#### Common mistakes
- Manual prod deploy bypassing pipeline
- No path filters in monorepo—wasted CI minutes
- Secrets in workflow YAML or logs
- Treating green CI as optional before merge

#### Interview follow-ups (with model answers)

**Q:** How does Monorepo pipelines affect rollback and MTTR?
**A:** Rollback is fast only when artifacts are immutable and cluster desired state lives in Git. I revert the GitOps PR or Helm revision, re-run smoke tests against the same image digest, and verify database migration compatibility. MTTR improves when prod promotion is reproducible and not a manual kubectl hotfix. I measure time from failed deploy to restored SLO and track failure class in a dashboard.

**Q:** What gate would you add after a failure involving Monorepo pipelines?
**A:** I classify the failure (flake, infra, quality, security, deploy) and add an automated guard in the right stage. Examples: quarantine flaky integration tests, ephemeral runners with disk cleanup, required Trivy/Sonar on main, or environment approval for production. Track recurrence quarterly and tie to DORA change failure rate separately from PR red builds.

**Q:** How do you explain Monorepo pipelines to a team new to CI/CD on Spring and AKS?
**A:** I walk a concrete path: PR runs Maven verify and scans; merge publishes a signed image to ACR; a GitOps PR updates Helm values; Argo CD syncs to AKS; smoke tests hit `/actuator/health`. I emphasize CI validates change, CD/GitOps promotes immutable artifacts, and main stays green with feature flags for incomplete work.

#### Scenario probe

**Situation:** Production deploy failed after a green PR; the panel asks how Monorepo pipelines fits your response.

**Model answer:** I timeline the pipeline: which stage failed, which digest was promoted, whether Argo drifted from Git. I roll forward or revert Git, verify smoke tests and Flyway order, communicate MTTR, and add a gate so this failure class is caught pre-prod next time.

---
### 25. Multi-module Maven/Gradle

**Short answer:** Build changed modules with `-pl` and dependents `-am`. Cache keyed on parent POM hash. Measure impact with DORA metrics and document rollback paths before changing prod gates.

#### What it is
Multi-module Maven/Gradle is a core practice in modern delivery for Spring microservices on AKS. It connects developer workflow to production safety—artifacts, gates, GitOps, and observability—not just running Jenkins jobs. Interviewers want trade-offs, failure modes, and how you measured improvement with DORA metrics.

#### How it works (internals)
Pipelines trigger on git events, run on ephemeral agents, publish immutable artifacts, and promote through environments with approvals. For multi-module maven/gradle, wire the check into the earliest stage that has enough context—usually PR for tests and main for deploy. Integrate with ACR, Key Vault or OIDC, and Argo CD for cluster sync. Failed stages should emit structured logs and failure class tags for MTTR tracking.

#### When to use / when NOT to use
Adopt when team size or compliance requires repeatable delivery. Skip heavyweight gates for throwaway prototypes. For Multi-module Maven/Gradle, enforce on main and prod paths; allow faster feedback loops on feature branches where safe. Never bypass prod gates without break-glass documentation and post-incident restore of controls.

#### Production example
On `order-service`, we applied multi-module maven/gradle in the pipeline: PR blocked on failure, main published digest `sha256:abc…`, GitOps PR updated `values-prod.yaml`, smoke tests passed, and rollback was a Git revert tested in staging first. Change failure rate dropped after we classified flakes and added quarantine policy.

#### Common mistakes
- Manual prod deploy bypassing pipeline
- No path filters in monorepo—wasted CI minutes
- Secrets in workflow YAML or logs
- Treating green CI as optional before merge

#### Interview follow-ups (with model answers)

**Q:** How does Multi-module Maven/Gradle affect rollback and MTTR?
**A:** Rollback is fast only when artifacts are immutable and cluster desired state lives in Git. I revert the GitOps PR or Helm revision, re-run smoke tests against the same image digest, and verify database migration compatibility. MTTR improves when prod promotion is reproducible and not a manual kubectl hotfix. I measure time from failed deploy to restored SLO and track failure class in a dashboard.

**Q:** What gate would you add after a failure involving Multi-module Maven/Gradle?
**A:** I classify the failure (flake, infra, quality, security, deploy) and add an automated guard in the right stage. Examples: quarantine flaky integration tests, ephemeral runners with disk cleanup, required Trivy/Sonar on main, or environment approval for production. Track recurrence quarterly and tie to DORA change failure rate separately from PR red builds.

**Q:** How do you explain Multi-module Maven/Gradle to a team new to CI/CD on Spring and AKS?
**A:** I walk a concrete path: PR runs Maven verify and scans; merge publishes a signed image to ACR; a GitOps PR updates Helm values; Argo CD syncs to AKS; smoke tests hit `/actuator/health`. I emphasize CI validates change, CD/GitOps promotes immutable artifacts, and main stays green with feature flags for incomplete work.

#### Scenario probe

**Situation:** Production deploy failed after a green PR; the panel asks how Multi-module Maven/Gradle fits your response.

**Model answer:** I timeline the pipeline: which stage failed, which digest was promoted, whether Argo drifted from Git. I roll forward or revert Git, verify smoke tests and Flyway order, communicate MTTR, and add a gate so this failure class is caught pre-prod next time.

---
### 26. Frontend + backend

**Short answer:** Coordinate API contract tests; deploy order may be backend first or parallel with feature flags. Single pipeline or orchestrated workflows. Measure impact with DORA metrics and document rollback paths before changing prod gates.

#### What it is
Frontend + backend is a core practice in modern delivery for Spring microservices on AKS. It connects developer workflow to production safety—artifacts, gates, GitOps, and observability—not just running Jenkins jobs. Interviewers want trade-offs, failure modes, and how you measured improvement with DORA metrics.

#### How it works (internals)
Pipelines trigger on git events, run on ephemeral agents, publish immutable artifacts, and promote through environments with approvals. For frontend + backend, wire the check into the earliest stage that has enough context—usually PR for tests and main for deploy. Integrate with ACR, Key Vault or OIDC, and Argo CD for cluster sync. Failed stages should emit structured logs and failure class tags for MTTR tracking.

#### When to use / when NOT to use
Adopt when team size or compliance requires repeatable delivery. Skip heavyweight gates for throwaway prototypes. For Frontend + backend, enforce on main and prod paths; allow faster feedback loops on feature branches where safe. Never bypass prod gates without break-glass documentation and post-incident restore of controls.

#### Production example
On `order-service`, we applied frontend + backend in the pipeline: PR blocked on failure, main published digest `sha256:abc…`, GitOps PR updated `values-prod.yaml`, smoke tests passed, and rollback was a Git revert tested in staging first. Change failure rate dropped after we classified flakes and added quarantine policy.

#### Common mistakes
- Manual prod deploy bypassing pipeline
- No path filters in monorepo—wasted CI minutes
- Secrets in workflow YAML or logs
- Treating green CI as optional before merge

#### Interview follow-ups (with model answers)

**Q:** How does Frontend + backend affect rollback and MTTR?
**A:** Rollback is fast only when artifacts are immutable and cluster desired state lives in Git. I revert the GitOps PR or Helm revision, re-run smoke tests against the same image digest, and verify database migration compatibility. MTTR improves when prod promotion is reproducible and not a manual kubectl hotfix. I measure time from failed deploy to restored SLO and track failure class in a dashboard.

**Q:** What gate would you add after a failure involving Frontend + backend?
**A:** I classify the failure (flake, infra, quality, security, deploy) and add an automated guard in the right stage. Examples: quarantine flaky integration tests, ephemeral runners with disk cleanup, required Trivy/Sonar on main, or environment approval for production. Track recurrence quarterly and tie to DORA change failure rate separately from PR red builds.

**Q:** How do you explain Frontend + backend to a team new to CI/CD on Spring and AKS?
**A:** I walk a concrete path: PR runs Maven verify and scans; merge publishes a signed image to ACR; a GitOps PR updates Helm values; Argo CD syncs to AKS; smoke tests hit `/actuator/health`. I emphasize CI validates change, CD/GitOps promotes immutable artifacts, and main stays green with feature flags for incomplete work.

#### Scenario probe

**Situation:** Production deploy failed after a green PR; the panel asks how Frontend + backend fits your response.

**Model answer:** I timeline the pipeline: which stage failed, which digest was promoted, whether Argo drifted from Git. I roll forward or revert Git, verify smoke tests and Flyway order, communicate MTTR, and add a gate so this failure class is caught pre-prod next time.

---
### 27. Versioning

**Short answer:** Semver for libraries; calendar or semver for services. Git SHA on images always; marketing version optional tag. Measure impact with DORA metrics and document rollback paths before changing prod gates.

#### What it is
Versioning is a core practice in modern delivery for Spring microservices on AKS. It connects developer workflow to production safety—artifacts, gates, GitOps, and observability—not just running Jenkins jobs. Interviewers want trade-offs, failure modes, and how you measured improvement with DORA metrics.

#### How it works (internals)
Pipelines trigger on git events, run on ephemeral agents, publish immutable artifacts, and promote through environments with approvals. For versioning, wire the check into the earliest stage that has enough context—usually PR for tests and main for deploy. Integrate with ACR, Key Vault or OIDC, and Argo CD for cluster sync. Failed stages should emit structured logs and failure class tags for MTTR tracking.

#### When to use / when NOT to use
Adopt when team size or compliance requires repeatable delivery. Skip heavyweight gates for throwaway prototypes. For Versioning, enforce on main and prod paths; allow faster feedback loops on feature branches where safe. Never bypass prod gates without break-glass documentation and post-incident restore of controls.

#### Production example
On `order-service`, we applied versioning in the pipeline: PR blocked on failure, main published digest `sha256:abc…`, GitOps PR updated `values-prod.yaml`, smoke tests passed, and rollback was a Git revert tested in staging first. Change failure rate dropped after we classified flakes and added quarantine policy.

#### Common mistakes
- Manual prod deploy bypassing pipeline
- No path filters in monorepo—wasted CI minutes
- Secrets in workflow YAML or logs
- Treating green CI as optional before merge

#### Interview follow-ups (with model answers)

**Q:** How does Versioning affect rollback and MTTR?
**A:** Rollback is fast only when artifacts are immutable and cluster desired state lives in Git. I revert the GitOps PR or Helm revision, re-run smoke tests against the same image digest, and verify database migration compatibility. MTTR improves when prod promotion is reproducible and not a manual kubectl hotfix. I measure time from failed deploy to restored SLO and track failure class in a dashboard.

**Q:** What gate would you add after a failure involving Versioning?
**A:** I classify the failure (flake, infra, quality, security, deploy) and add an automated guard in the right stage. Examples: quarantine flaky integration tests, ephemeral runners with disk cleanup, required Trivy/Sonar on main, or environment approval for production. Track recurrence quarterly and tie to DORA change failure rate separately from PR red builds.

**Q:** How do you explain Versioning to a team new to CI/CD on Spring and AKS?
**A:** I walk a concrete path: PR runs Maven verify and scans; merge publishes a signed image to ACR; a GitOps PR updates Helm values; Argo CD syncs to AKS; smoke tests hit `/actuator/health`. I emphasize CI validates change, CD/GitOps promotes immutable artifacts, and main stays green with feature flags for incomplete work.

#### Scenario probe

**Situation:** Production deploy failed after a green PR; the panel asks how Versioning fits your response.

**Model answer:** I timeline the pipeline: which stage failed, which digest was promoted, whether Argo drifted from Git. I roll forward or revert Git, verify smoke tests and Flyway order, communicate MTTR, and add a gate so this failure class is caught pre-prod next time.

---
### 28. Changelog / release notes

**Short answer:** Generate from conventional commits or PR labels in CI. Attach to GitHub Release and deployment ticket. Measure impact with DORA metrics and document rollback paths before changing prod gates.

#### What it is
Changelog / release notes is a core practice in modern delivery for Spring microservices on AKS. It connects developer workflow to production safety—artifacts, gates, GitOps, and observability—not just running Jenkins jobs. Interviewers want trade-offs, failure modes, and how you measured improvement with DORA metrics.

#### How it works (internals)
Pipelines trigger on git events, run on ephemeral agents, publish immutable artifacts, and promote through environments with approvals. For changelog / release notes, wire the check into the earliest stage that has enough context—usually PR for tests and main for deploy. Integrate with ACR, Key Vault or OIDC, and Argo CD for cluster sync. Failed stages should emit structured logs and failure class tags for MTTR tracking.

#### When to use / when NOT to use
Adopt when team size or compliance requires repeatable delivery. Skip heavyweight gates for throwaway prototypes. For Changelog / release notes, enforce on main and prod paths; allow faster feedback loops on feature branches where safe. Never bypass prod gates without break-glass documentation and post-incident restore of controls.

#### Production example
On `order-service`, we applied changelog / release notes in the pipeline: PR blocked on failure, main published digest `sha256:abc…`, GitOps PR updated `values-prod.yaml`, smoke tests passed, and rollback was a Git revert tested in staging first. Change failure rate dropped after we classified flakes and added quarantine policy.

#### Common mistakes
- Manual prod deploy bypassing pipeline
- No path filters in monorepo—wasted CI minutes
- Secrets in workflow YAML or logs
- Treating green CI as optional before merge

#### Interview follow-ups (with model answers)

**Q:** How does Changelog / release notes affect rollback and MTTR?
**A:** Rollback is fast only when artifacts are immutable and cluster desired state lives in Git. I revert the GitOps PR or Helm revision, re-run smoke tests against the same image digest, and verify database migration compatibility. MTTR improves when prod promotion is reproducible and not a manual kubectl hotfix. I measure time from failed deploy to restored SLO and track failure class in a dashboard.

**Q:** What gate would you add after a failure involving Changelog / release notes?
**A:** I classify the failure (flake, infra, quality, security, deploy) and add an automated guard in the right stage. Examples: quarantine flaky integration tests, ephemeral runners with disk cleanup, required Trivy/Sonar on main, or environment approval for production. Track recurrence quarterly and tie to DORA change failure rate separately from PR red builds.

**Q:** How do you explain Changelog / release notes to a team new to CI/CD on Spring and AKS?
**A:** I walk a concrete path: PR runs Maven verify and scans; merge publishes a signed image to ACR; a GitOps PR updates Helm values; Argo CD syncs to AKS; smoke tests hit `/actuator/health`. I emphasize CI validates change, CD/GitOps promotes immutable artifacts, and main stays green with feature flags for incomplete work.

#### Scenario probe

**Situation:** Production deploy failed after a green PR; the panel asks how Changelog / release notes fits your response.

**Model answer:** I timeline the pipeline: which stage failed, which digest was promoted, whether Argo drifted from Git. I roll forward or revert Git, verify smoke tests and Flyway order, communicate MTTR, and add a gate so this failure class is caught pre-prod next time.

---
### 29. Hotfix process

**Short answer:** Branch from prod tag, CI, fast-track review, deploy, cherry-pick to main. Same gates, smaller scope. Measure impact with DORA metrics and document rollback paths before changing prod gates.

#### What it is
Hotfix process is a core practice in modern delivery for Spring microservices on AKS. It connects developer workflow to production safety—artifacts, gates, GitOps, and observability—not just running Jenkins jobs. Interviewers want trade-offs, failure modes, and how you measured improvement with DORA metrics.

#### How it works (internals)
Pipelines trigger on git events, run on ephemeral agents, publish immutable artifacts, and promote through environments with approvals. For hotfix process, wire the check into the earliest stage that has enough context—usually PR for tests and main for deploy. Integrate with ACR, Key Vault or OIDC, and Argo CD for cluster sync. Failed stages should emit structured logs and failure class tags for MTTR tracking.

#### When to use / when NOT to use
Adopt when team size or compliance requires repeatable delivery. Skip heavyweight gates for throwaway prototypes. For Hotfix process, enforce on main and prod paths; allow faster feedback loops on feature branches where safe. Never bypass prod gates without break-glass documentation and post-incident restore of controls.

#### Production example
On `order-service`, we applied hotfix process in the pipeline: PR blocked on failure, main published digest `sha256:abc…`, GitOps PR updated `values-prod.yaml`, smoke tests passed, and rollback was a Git revert tested in staging first. Change failure rate dropped after we classified flakes and added quarantine policy.

#### Common mistakes
- Manual prod deploy bypassing pipeline
- No path filters in monorepo—wasted CI minutes
- Secrets in workflow YAML or logs
- Treating green CI as optional before merge

#### Interview follow-ups (with model answers)

**Q:** How does Hotfix process affect rollback and MTTR?
**A:** Rollback is fast only when artifacts are immutable and cluster desired state lives in Git. I revert the GitOps PR or Helm revision, re-run smoke tests against the same image digest, and verify database migration compatibility. MTTR improves when prod promotion is reproducible and not a manual kubectl hotfix. I measure time from failed deploy to restored SLO and track failure class in a dashboard.

**Q:** What gate would you add after a failure involving Hotfix process?
**A:** I classify the failure (flake, infra, quality, security, deploy) and add an automated guard in the right stage. Examples: quarantine flaky integration tests, ephemeral runners with disk cleanup, required Trivy/Sonar on main, or environment approval for production. Track recurrence quarterly and tie to DORA change failure rate separately from PR red builds.

**Q:** How do you explain Hotfix process to a team new to CI/CD on Spring and AKS?
**A:** I walk a concrete path: PR runs Maven verify and scans; merge publishes a signed image to ACR; a GitOps PR updates Helm values; Argo CD syncs to AKS; smoke tests hit `/actuator/health`. I emphasize CI validates change, CD/GitOps promotes immutable artifacts, and main stays green with feature flags for incomplete work.

#### Scenario probe

**Situation:** Production deploy failed after a green PR; the panel asks how Hotfix process fits your response.

**Model answer:** I timeline the pipeline: which stage failed, which digest was promoted, whether Argo drifted from Git. I roll forward or revert Git, verify smoke tests and Flyway order, communicate MTTR, and add a gate so this failure class is caught pre-prod next time.

---
### 30. Feature flags vs incomplete main

**Short answer:** Trunk stays green; flags hide incomplete features. Pipeline deploys complete code paths only. Measure impact with DORA metrics and document rollback paths before changing prod gates.

#### What it is
Feature flags vs incomplete main is a core practice in modern delivery for Spring microservices on AKS. It connects developer workflow to production safety—artifacts, gates, GitOps, and observability—not just running Jenkins jobs. Interviewers want trade-offs, failure modes, and how you measured improvement with DORA metrics.

#### How it works (internals)
Pipelines trigger on git events, run on ephemeral agents, publish immutable artifacts, and promote through environments with approvals. For feature flags vs incomplete main, wire the check into the earliest stage that has enough context—usually PR for tests and main for deploy. Integrate with ACR, Key Vault or OIDC, and Argo CD for cluster sync. Failed stages should emit structured logs and failure class tags for MTTR tracking.

#### When to use / when NOT to use
Adopt when team size or compliance requires repeatable delivery. Skip heavyweight gates for throwaway prototypes. For Feature flags vs incomplete main, enforce on main and prod paths; allow faster feedback loops on feature branches where safe. Never bypass prod gates without break-glass documentation and post-incident restore of controls.

#### Production example
On `order-service`, we applied feature flags vs incomplete main in the pipeline: PR blocked on failure, main published digest `sha256:abc…`, GitOps PR updated `values-prod.yaml`, smoke tests passed, and rollback was a Git revert tested in staging first. Change failure rate dropped after we classified flakes and added quarantine policy.

#### Common mistakes
- Manual prod deploy bypassing pipeline
- No path filters in monorepo—wasted CI minutes
- Secrets in workflow YAML or logs
- Treating green CI as optional before merge

#### Interview follow-ups (with model answers)

**Q:** How does Feature flags vs incomplete main affect rollback and MTTR?
**A:** Rollback is fast only when artifacts are immutable and cluster desired state lives in Git. I revert the GitOps PR or Helm revision, re-run smoke tests against the same image digest, and verify database migration compatibility. MTTR improves when prod promotion is reproducible and not a manual kubectl hotfix. I measure time from failed deploy to restored SLO and track failure class in a dashboard.

**Q:** What gate would you add after a failure involving Feature flags vs incomplete main?
**A:** I classify the failure (flake, infra, quality, security, deploy) and add an automated guard in the right stage. Examples: quarantine flaky integration tests, ephemeral runners with disk cleanup, required Trivy/Sonar on main, or environment approval for production. Track recurrence quarterly and tie to DORA change failure rate separately from PR red builds.

**Q:** How do you explain Feature flags vs incomplete main to a team new to CI/CD on Spring and AKS?
**A:** I walk a concrete path: PR runs Maven verify and scans; merge publishes a signed image to ACR; a GitOps PR updates Helm values; Argo CD syncs to AKS; smoke tests hit `/actuator/health`. I emphasize CI validates change, CD/GitOps promotes immutable artifacts, and main stays green with feature flags for incomplete work.

#### Scenario probe

**Situation:** Production deploy failed after a green PR; the panel asks how Feature flags vs incomplete main fits your response.

**Model answer:** I timeline the pipeline: which stage failed, which digest was promoted, whether Argo drifted from Git. I roll forward or revert Git, verify smoke tests and Flyway order, communicate MTTR, and add a gate so this failure class is caught pre-prod next time.

---
### 31. DORA metrics

**Short answer:** Lead time, deployment frequency, change failure rate, MTTR—measure before/after pipeline investment. Measure impact with DORA metrics and document rollback paths before changing prod gates.

#### What it is
DORA metrics is a core practice in modern delivery for Spring microservices on AKS. It connects developer workflow to production safety—artifacts, gates, GitOps, and observability—not just running Jenkins jobs. Interviewers want trade-offs, failure modes, and how you measured improvement with DORA metrics.

#### How it works (internals)
Pipelines trigger on git events, run on ephemeral agents, publish immutable artifacts, and promote through environments with approvals. For dora metrics, wire the check into the earliest stage that has enough context—usually PR for tests and main for deploy. Integrate with ACR, Key Vault or OIDC, and Argo CD for cluster sync. Failed stages should emit structured logs and failure class tags for MTTR tracking.

#### When to use / when NOT to use
Adopt when team size or compliance requires repeatable delivery. Skip heavyweight gates for throwaway prototypes. For DORA metrics, enforce on main and prod paths; allow faster feedback loops on feature branches where safe. Never bypass prod gates without break-glass documentation and post-incident restore of controls.

#### Production example
On `order-service`, we applied dora metrics in the pipeline: PR blocked on failure, main published digest `sha256:abc…`, GitOps PR updated `values-prod.yaml`, smoke tests passed, and rollback was a Git revert tested in staging first. Change failure rate dropped after we classified flakes and added quarantine policy.

#### Common mistakes
- Manual prod deploy bypassing pipeline
- No path filters in monorepo—wasted CI minutes
- Secrets in workflow YAML or logs
- Treating green CI as optional before merge

#### Interview follow-ups (with model answers)

**Q:** How does DORA metrics affect rollback and MTTR?
**A:** Rollback is fast only when artifacts are immutable and cluster desired state lives in Git. I revert the GitOps PR or Helm revision, re-run smoke tests against the same image digest, and verify database migration compatibility. MTTR improves when prod promotion is reproducible and not a manual kubectl hotfix. I measure time from failed deploy to restored SLO and track failure class in a dashboard.

**Q:** What gate would you add after a failure involving DORA metrics?
**A:** I classify the failure (flake, infra, quality, security, deploy) and add an automated guard in the right stage. Examples: quarantine flaky integration tests, ephemeral runners with disk cleanup, required Trivy/Sonar on main, or environment approval for production. Track recurrence quarterly and tie to DORA change failure rate separately from PR red builds.

**Q:** How do you explain DORA metrics to a team new to CI/CD on Spring and AKS?
**A:** I walk a concrete path: PR runs Maven verify and scans; merge publishes a signed image to ACR; a GitOps PR updates Helm values; Argo CD syncs to AKS; smoke tests hit `/actuator/health`. I emphasize CI validates change, CD/GitOps promotes immutable artifacts, and main stays green with feature flags for incomplete work.

#### Scenario probe

**Situation:** Production deploy failed after a green PR; the panel asks how DORA metrics fits your response.

**Model answer:** I timeline the pipeline: which stage failed, which digest was promoted, whether Argo drifted from Git. I roll forward or revert Git, verify smoke tests and Flyway order, communicate MTTR, and add a gate so this failure class is caught pre-prod next time.

---
### 32. Nightly vs every commit

**Short answer:** Heavy e2e nightly; fast checks every commit. Schedule cost versus risk trade-off. Measure impact with DORA metrics and document rollback paths before changing prod gates.

#### What it is
Nightly vs every commit is a core practice in modern delivery for Spring microservices on AKS. It connects developer workflow to production safety—artifacts, gates, GitOps, and observability—not just running Jenkins jobs. Interviewers want trade-offs, failure modes, and how you measured improvement with DORA metrics.

#### How it works (internals)
Pipelines trigger on git events, run on ephemeral agents, publish immutable artifacts, and promote through environments with approvals. For nightly vs every commit, wire the check into the earliest stage that has enough context—usually PR for tests and main for deploy. Integrate with ACR, Key Vault or OIDC, and Argo CD for cluster sync. Failed stages should emit structured logs and failure class tags for MTTR tracking.

#### When to use / when NOT to use
Adopt when team size or compliance requires repeatable delivery. Skip heavyweight gates for throwaway prototypes. For Nightly vs every commit, enforce on main and prod paths; allow faster feedback loops on feature branches where safe. Never bypass prod gates without break-glass documentation and post-incident restore of controls.

#### Production example
On `order-service`, we applied nightly vs every commit in the pipeline: PR blocked on failure, main published digest `sha256:abc…`, GitOps PR updated `values-prod.yaml`, smoke tests passed, and rollback was a Git revert tested in staging first. Change failure rate dropped after we classified flakes and added quarantine policy.

#### Common mistakes
- Manual prod deploy bypassing pipeline
- No path filters in monorepo—wasted CI minutes
- Secrets in workflow YAML or logs
- Treating green CI as optional before merge

#### Interview follow-ups (with model answers)

**Q:** How does Nightly vs every commit affect rollback and MTTR?
**A:** Rollback is fast only when artifacts are immutable and cluster desired state lives in Git. I revert the GitOps PR or Helm revision, re-run smoke tests against the same image digest, and verify database migration compatibility. MTTR improves when prod promotion is reproducible and not a manual kubectl hotfix. I measure time from failed deploy to restored SLO and track failure class in a dashboard.

**Q:** What gate would you add after a failure involving Nightly vs every commit?
**A:** I classify the failure (flake, infra, quality, security, deploy) and add an automated guard in the right stage. Examples: quarantine flaky integration tests, ephemeral runners with disk cleanup, required Trivy/Sonar on main, or environment approval for production. Track recurrence quarterly and tie to DORA change failure rate separately from PR red builds.

**Q:** How do you explain Nightly vs every commit to a team new to CI/CD on Spring and AKS?
**A:** I walk a concrete path: PR runs Maven verify and scans; merge publishes a signed image to ACR; a GitOps PR updates Helm values; Argo CD syncs to AKS; smoke tests hit `/actuator/health`. I emphasize CI validates change, CD/GitOps promotes immutable artifacts, and main stays green with feature flags for incomplete work.

#### Scenario probe

**Situation:** Production deploy failed after a green PR; the panel asks how Nightly vs every commit fits your response.

**Model answer:** I timeline the pipeline: which stage failed, which digest was promoted, whether Argo drifted from Git. I roll forward or revert Git, verify smoke tests and Flyway order, communicate MTTR, and add a gate so this failure class is caught pre-prod next time.

---
### 33. Self-hosted runners

**Short answer:** Needed for private network, larger machines, or compliance. Isolate prod deploy runners; ephemeral preferred. Measure impact with DORA metrics and document rollback paths before changing prod gates.

#### What it is
Self-hosted runners is a core practice in modern delivery for Spring microservices on AKS. It connects developer workflow to production safety—artifacts, gates, GitOps, and observability—not just running Jenkins jobs. Interviewers want trade-offs, failure modes, and how you measured improvement with DORA metrics.

#### How it works (internals)
Pipelines trigger on git events, run on ephemeral agents, publish immutable artifacts, and promote through environments with approvals. For self-hosted runners, wire the check into the earliest stage that has enough context—usually PR for tests and main for deploy. Integrate with ACR, Key Vault or OIDC, and Argo CD for cluster sync. Failed stages should emit structured logs and failure class tags for MTTR tracking.

#### When to use / when NOT to use
Adopt when team size or compliance requires repeatable delivery. Skip heavyweight gates for throwaway prototypes. For Self-hosted runners, enforce on main and prod paths; allow faster feedback loops on feature branches where safe. Never bypass prod gates without break-glass documentation and post-incident restore of controls.

#### Production example
On `order-service`, we applied self-hosted runners in the pipeline: PR blocked on failure, main published digest `sha256:abc…`, GitOps PR updated `values-prod.yaml`, smoke tests passed, and rollback was a Git revert tested in staging first. Change failure rate dropped after we classified flakes and added quarantine policy.

#### Common mistakes
- Manual prod deploy bypassing pipeline
- No path filters in monorepo—wasted CI minutes
- Secrets in workflow YAML or logs
- Treating green CI as optional before merge

#### Interview follow-ups (with model answers)

**Q:** How does Self-hosted runners affect rollback and MTTR?
**A:** Rollback is fast only when artifacts are immutable and cluster desired state lives in Git. I revert the GitOps PR or Helm revision, re-run smoke tests against the same image digest, and verify database migration compatibility. MTTR improves when prod promotion is reproducible and not a manual kubectl hotfix. I measure time from failed deploy to restored SLO and track failure class in a dashboard.

**Q:** What gate would you add after a failure involving Self-hosted runners?
**A:** I classify the failure (flake, infra, quality, security, deploy) and add an automated guard in the right stage. Examples: quarantine flaky integration tests, ephemeral runners with disk cleanup, required Trivy/Sonar on main, or environment approval for production. Track recurrence quarterly and tie to DORA change failure rate separately from PR red builds.

**Q:** How do you explain Self-hosted runners to a team new to CI/CD on Spring and AKS?
**A:** I walk a concrete path: PR runs Maven verify and scans; merge publishes a signed image to ACR; a GitOps PR updates Helm values; Argo CD syncs to AKS; smoke tests hit `/actuator/health`. I emphasize CI validates change, CD/GitOps promotes immutable artifacts, and main stays green with feature flags for incomplete work.

#### Scenario probe

**Situation:** Production deploy failed after a green PR; the panel asks how Self-hosted runners fits your response.

**Model answer:** I timeline the pipeline: which stage failed, which digest was promoted, whether Argo drifted from Git. I roll forward or revert Git, verify smoke tests and Flyway order, communicate MTTR, and add a gate so this failure class is caught pre-prod next time.

---
### 34. Cache poisoning / untrusted PRs

**Short answer:** Do not run untrusted fork workflows with secrets; limit PR permissions; use `pull_request_target` carefully. Measure impact with DORA metrics and document rollback paths before changing prod gates.

#### What it is
Cache poisoning / untrusted PRs is a core practice in modern delivery for Spring microservices on AKS. It connects developer workflow to production safety—artifacts, gates, GitOps, and observability—not just running Jenkins jobs. Interviewers want trade-offs, failure modes, and how you measured improvement with DORA metrics.

#### How it works (internals)
Pipelines trigger on git events, run on ephemeral agents, publish immutable artifacts, and promote through environments with approvals. For cache poisoning / untrusted prs, wire the check into the earliest stage that has enough context—usually PR for tests and main for deploy. Integrate with ACR, Key Vault or OIDC, and Argo CD for cluster sync. Failed stages should emit structured logs and failure class tags for MTTR tracking.

#### When to use / when NOT to use
Adopt when team size or compliance requires repeatable delivery. Skip heavyweight gates for throwaway prototypes. For Cache poisoning / untrusted PRs, enforce on main and prod paths; allow faster feedback loops on feature branches where safe. Never bypass prod gates without break-glass documentation and post-incident restore of controls.

#### Production example
On `order-service`, we applied cache poisoning / untrusted prs in the pipeline: PR blocked on failure, main published digest `sha256:abc…`, GitOps PR updated `values-prod.yaml`, smoke tests passed, and rollback was a Git revert tested in staging first. Change failure rate dropped after we classified flakes and added quarantine policy.

#### Common mistakes
- Manual prod deploy bypassing pipeline
- No path filters in monorepo—wasted CI minutes
- Secrets in workflow YAML or logs
- Treating green CI as optional before merge

#### Interview follow-ups (with model answers)

**Q:** How does Cache poisoning / untrusted PRs affect rollback and MTTR?
**A:** Rollback is fast only when artifacts are immutable and cluster desired state lives in Git. I revert the GitOps PR or Helm revision, re-run smoke tests against the same image digest, and verify database migration compatibility. MTTR improves when prod promotion is reproducible and not a manual kubectl hotfix. I measure time from failed deploy to restored SLO and track failure class in a dashboard.

**Q:** What gate would you add after a failure involving Cache poisoning / untrusted PRs?
**A:** I classify the failure (flake, infra, quality, security, deploy) and add an automated guard in the right stage. Examples: quarantine flaky integration tests, ephemeral runners with disk cleanup, required Trivy/Sonar on main, or environment approval for production. Track recurrence quarterly and tie to DORA change failure rate separately from PR red builds.

**Q:** How do you explain Cache poisoning / untrusted PRs to a team new to CI/CD on Spring and AKS?
**A:** I walk a concrete path: PR runs Maven verify and scans; merge publishes a signed image to ACR; a GitOps PR updates Helm values; Argo CD syncs to AKS; smoke tests hit `/actuator/health`. I emphasize CI validates change, CD/GitOps promotes immutable artifacts, and main stays green with feature flags for incomplete work.

#### Scenario probe

**Situation:** Production deploy failed after a green PR; the panel asks how Cache poisoning / untrusted PRs fits your response.

**Model answer:** I timeline the pipeline: which stage failed, which digest was promoted, whether Argo drifted from Git. I roll forward or revert Git, verify smoke tests and Flyway order, communicate MTTR, and add a gate so this failure class is caught pre-prod next time.

---
### 35. Jenkins specifics (still around)

**Short answer:** Multibranch, shared libraries, credential binding. Migrate to Actions/ADO with template parity. Measure impact with DORA metrics and document rollback paths before changing prod gates.

#### What it is
Jenkins specifics (still around) is a core practice in modern delivery for Spring microservices on AKS. It connects developer workflow to production safety—artifacts, gates, GitOps, and observability—not just running Jenkins jobs. Interviewers want trade-offs, failure modes, and how you measured improvement with DORA metrics.

#### How it works (internals)
Pipelines trigger on git events, run on ephemeral agents, publish immutable artifacts, and promote through environments with approvals. For jenkins specifics (still around), wire the check into the earliest stage that has enough context—usually PR for tests and main for deploy. Integrate with ACR, Key Vault or OIDC, and Argo CD for cluster sync. Failed stages should emit structured logs and failure class tags for MTTR tracking.

#### When to use / when NOT to use
Adopt when team size or compliance requires repeatable delivery. Skip heavyweight gates for throwaway prototypes. For Jenkins specifics (still around), enforce on main and prod paths; allow faster feedback loops on feature branches where safe. Never bypass prod gates without break-glass documentation and post-incident restore of controls.

#### Production example
On `order-service`, we applied jenkins specifics (still around) in the pipeline: PR blocked on failure, main published digest `sha256:abc…`, GitOps PR updated `values-prod.yaml`, smoke tests passed, and rollback was a Git revert tested in staging first. Change failure rate dropped after we classified flakes and added quarantine policy.

#### Common mistakes
- Manual prod deploy bypassing pipeline
- No path filters in monorepo—wasted CI minutes
- Secrets in workflow YAML or logs
- Treating green CI as optional before merge

#### Interview follow-ups (with model answers)

**Q:** How does Jenkins specifics (still around) affect rollback and MTTR?
**A:** Rollback is fast only when artifacts are immutable and cluster desired state lives in Git. I revert the GitOps PR or Helm revision, re-run smoke tests against the same image digest, and verify database migration compatibility. MTTR improves when prod promotion is reproducible and not a manual kubectl hotfix. I measure time from failed deploy to restored SLO and track failure class in a dashboard.

**Q:** What gate would you add after a failure involving Jenkins specifics (still around)?
**A:** I classify the failure (flake, infra, quality, security, deploy) and add an automated guard in the right stage. Examples: quarantine flaky integration tests, ephemeral runners with disk cleanup, required Trivy/Sonar on main, or environment approval for production. Track recurrence quarterly and tie to DORA change failure rate separately from PR red builds.

**Q:** How do you explain Jenkins specifics (still around) to a team new to CI/CD on Spring and AKS?
**A:** I walk a concrete path: PR runs Maven verify and scans; merge publishes a signed image to ACR; a GitOps PR updates Helm values; Argo CD syncs to AKS; smoke tests hit `/actuator/health`. I emphasize CI validates change, CD/GitOps promotes immutable artifacts, and main stays green with feature flags for incomplete work.

#### Scenario probe

**Situation:** Production deploy failed after a green PR; the panel asks how Jenkins specifics (still around) fits your response.

**Model answer:** I timeline the pipeline: which stage failed, which digest was promoted, whether Argo drifted from Git. I roll forward or revert Git, verify smoke tests and Flyway order, communicate MTTR, and add a gate so this failure class is caught pre-prod next time.

---
### 36. Azure DevOps YAML

**Short answer:** Templates, environments, service connections, artifact feeds. OIDC to Azure over long-lived secrets. Measure impact with DORA metrics and document rollback paths before changing prod gates.

#### What it is
Azure DevOps YAML is a core practice in modern delivery for Spring microservices on AKS. It connects developer workflow to production safety—artifacts, gates, GitOps, and observability—not just running Jenkins jobs. Interviewers want trade-offs, failure modes, and how you measured improvement with DORA metrics.

#### How it works (internals)
Pipelines trigger on git events, run on ephemeral agents, publish immutable artifacts, and promote through environments with approvals. For azure devops yaml, wire the check into the earliest stage that has enough context—usually PR for tests and main for deploy. Integrate with ACR, Key Vault or OIDC, and Argo CD for cluster sync. Failed stages should emit structured logs and failure class tags for MTTR tracking.

#### When to use / when NOT to use
Adopt when team size or compliance requires repeatable delivery. Skip heavyweight gates for throwaway prototypes. For Azure DevOps YAML, enforce on main and prod paths; allow faster feedback loops on feature branches where safe. Never bypass prod gates without break-glass documentation and post-incident restore of controls.

#### Production example
On `order-service`, we applied azure devops yaml in the pipeline: PR blocked on failure, main published digest `sha256:abc…`, GitOps PR updated `values-prod.yaml`, smoke tests passed, and rollback was a Git revert tested in staging first. Change failure rate dropped after we classified flakes and added quarantine policy.

#### Common mistakes
- Manual prod deploy bypassing pipeline
- No path filters in monorepo—wasted CI minutes
- Secrets in workflow YAML or logs
- Treating green CI as optional before merge

#### Interview follow-ups (with model answers)

**Q:** How does Azure DevOps YAML affect rollback and MTTR?
**A:** Rollback is fast only when artifacts are immutable and cluster desired state lives in Git. I revert the GitOps PR or Helm revision, re-run smoke tests against the same image digest, and verify database migration compatibility. MTTR improves when prod promotion is reproducible and not a manual kubectl hotfix. I measure time from failed deploy to restored SLO and track failure class in a dashboard.

**Q:** What gate would you add after a failure involving Azure DevOps YAML?
**A:** I classify the failure (flake, infra, quality, security, deploy) and add an automated guard in the right stage. Examples: quarantine flaky integration tests, ephemeral runners with disk cleanup, required Trivy/Sonar on main, or environment approval for production. Track recurrence quarterly and tie to DORA change failure rate separately from PR red builds.

**Q:** How do you explain Azure DevOps YAML to a team new to CI/CD on Spring and AKS?
**A:** I walk a concrete path: PR runs Maven verify and scans; merge publishes a signed image to ACR; a GitOps PR updates Helm values; Argo CD syncs to AKS; smoke tests hit `/actuator/health`. I emphasize CI validates change, CD/GitOps promotes immutable artifacts, and main stays green with feature flags for incomplete work.

#### Scenario probe

**Situation:** Production deploy failed after a green PR; the panel asks how Azure DevOps YAML fits your response.

**Model answer:** I timeline the pipeline: which stage failed, which digest was promoted, whether Argo drifted from Git. I roll forward or revert Git, verify smoke tests and Flyway order, communicate MTTR, and add a gate so this failure class is caught pre-prod next time.

---
### 37. GitHub Actions

**Short answer:** Reusable workflows, environments, concurrency groups, OIDC to ACR/AKS. Marketplace actions pin to SHA. Measure impact with DORA metrics and document rollback paths before changing prod gates.

#### What it is
GitHub Actions is a core practice in modern delivery for Spring microservices on AKS. It connects developer workflow to production safety—artifacts, gates, GitOps, and observability—not just running Jenkins jobs. Interviewers want trade-offs, failure modes, and how you measured improvement with DORA metrics.

#### How it works (internals)
Pipelines trigger on git events, run on ephemeral agents, publish immutable artifacts, and promote through environments with approvals. For github actions, wire the check into the earliest stage that has enough context—usually PR for tests and main for deploy. Integrate with ACR, Key Vault or OIDC, and Argo CD for cluster sync. Failed stages should emit structured logs and failure class tags for MTTR tracking.

#### When to use / when NOT to use
Adopt when team size or compliance requires repeatable delivery. Skip heavyweight gates for throwaway prototypes. For GitHub Actions, enforce on main and prod paths; allow faster feedback loops on feature branches where safe. Never bypass prod gates without break-glass documentation and post-incident restore of controls.

#### Production example
On `order-service`, we applied github actions in the pipeline: PR blocked on failure, main published digest `sha256:abc…`, GitOps PR updated `values-prod.yaml`, smoke tests passed, and rollback was a Git revert tested in staging first. Change failure rate dropped after we classified flakes and added quarantine policy.

#### Common mistakes
- Manual prod deploy bypassing pipeline
- No path filters in monorepo—wasted CI minutes
- Secrets in workflow YAML or logs
- Treating green CI as optional before merge

#### Interview follow-ups (with model answers)

**Q:** How does GitHub Actions affect rollback and MTTR?
**A:** Rollback is fast only when artifacts are immutable and cluster desired state lives in Git. I revert the GitOps PR or Helm revision, re-run smoke tests against the same image digest, and verify database migration compatibility. MTTR improves when prod promotion is reproducible and not a manual kubectl hotfix. I measure time from failed deploy to restored SLO and track failure class in a dashboard.

**Q:** What gate would you add after a failure involving GitHub Actions?
**A:** I classify the failure (flake, infra, quality, security, deploy) and add an automated guard in the right stage. Examples: quarantine flaky integration tests, ephemeral runners with disk cleanup, required Trivy/Sonar on main, or environment approval for production. Track recurrence quarterly and tie to DORA change failure rate separately from PR red builds.

**Q:** How do you explain GitHub Actions to a team new to CI/CD on Spring and AKS?
**A:** I walk a concrete path: PR runs Maven verify and scans; merge publishes a signed image to ACR; a GitOps PR updates Helm values; Argo CD syncs to AKS; smoke tests hit `/actuator/health`. I emphasize CI validates change, CD/GitOps promotes immutable artifacts, and main stays green with feature flags for incomplete work.

#### Scenario probe

**Situation:** Production deploy failed after a green PR; the panel asks how GitHub Actions fits your response.

**Model answer:** I timeline the pipeline: which stage failed, which digest was promoted, whether Argo drifted from Git. I roll forward or revert Git, verify smoke tests and Flyway order, communicate MTTR, and add a gate so this failure class is caught pre-prod next time.

---
### 38. Concurrency and locking deploys

**Short answer:** `concurrency: group` prevents overlapping prod deploys. Queue or cancel in-flight per policy. Measure impact with DORA metrics and document rollback paths before changing prod gates.

#### What it is
Concurrency and locking deploys is a core practice in modern delivery for Spring microservices on AKS. It connects developer workflow to production safety—artifacts, gates, GitOps, and observability—not just running Jenkins jobs. Interviewers want trade-offs, failure modes, and how you measured improvement with DORA metrics.

#### How it works (internals)
Pipelines trigger on git events, run on ephemeral agents, publish immutable artifacts, and promote through environments with approvals. For concurrency and locking deploys, wire the check into the earliest stage that has enough context—usually PR for tests and main for deploy. Integrate with ACR, Key Vault or OIDC, and Argo CD for cluster sync. Failed stages should emit structured logs and failure class tags for MTTR tracking.

#### When to use / when NOT to use
Adopt when team size or compliance requires repeatable delivery. Skip heavyweight gates for throwaway prototypes. For Concurrency and locking deploys, enforce on main and prod paths; allow faster feedback loops on feature branches where safe. Never bypass prod gates without break-glass documentation and post-incident restore of controls.

#### Production example
On `order-service`, we applied concurrency and locking deploys in the pipeline: PR blocked on failure, main published digest `sha256:abc…`, GitOps PR updated `values-prod.yaml`, smoke tests passed, and rollback was a Git revert tested in staging first. Change failure rate dropped after we classified flakes and added quarantine policy.

#### Common mistakes
- Manual prod deploy bypassing pipeline
- No path filters in monorepo—wasted CI minutes
- Secrets in workflow YAML or logs
- Treating green CI as optional before merge

#### Interview follow-ups (with model answers)

**Q:** How does Concurrency and locking deploys affect rollback and MTTR?
**A:** Rollback is fast only when artifacts are immutable and cluster desired state lives in Git. I revert the GitOps PR or Helm revision, re-run smoke tests against the same image digest, and verify database migration compatibility. MTTR improves when prod promotion is reproducible and not a manual kubectl hotfix. I measure time from failed deploy to restored SLO and track failure class in a dashboard.

**Q:** What gate would you add after a failure involving Concurrency and locking deploys?
**A:** I classify the failure (flake, infra, quality, security, deploy) and add an automated guard in the right stage. Examples: quarantine flaky integration tests, ephemeral runners with disk cleanup, required Trivy/Sonar on main, or environment approval for production. Track recurrence quarterly and tie to DORA change failure rate separately from PR red builds.

**Q:** How do you explain Concurrency and locking deploys to a team new to CI/CD on Spring and AKS?
**A:** I walk a concrete path: PR runs Maven verify and scans; merge publishes a signed image to ACR; a GitOps PR updates Helm values; Argo CD syncs to AKS; smoke tests hit `/actuator/health`. I emphasize CI validates change, CD/GitOps promotes immutable artifacts, and main stays green with feature flags for incomplete work.

#### Scenario probe

**Situation:** Production deploy failed after a green PR; the panel asks how Concurrency and locking deploys fits your response.

**Model answer:** I timeline the pipeline: which stage failed, which digest was promoted, whether Argo drifted from Git. I roll forward or revert Git, verify smoke tests and Flyway order, communicate MTTR, and add a gate so this failure class is caught pre-prod next time.

---
### 39. Observability of the pipeline

**Short answer:** Metrics on duration, queue time, failure class. Alert on main red > 30 minutes. Measure impact with DORA metrics and document rollback paths before changing prod gates.

#### What it is
Observability of the pipeline is a core practice in modern delivery for Spring microservices on AKS. It connects developer workflow to production safety—artifacts, gates, GitOps, and observability—not just running Jenkins jobs. Interviewers want trade-offs, failure modes, and how you measured improvement with DORA metrics.

#### How it works (internals)
Pipelines trigger on git events, run on ephemeral agents, publish immutable artifacts, and promote through environments with approvals. For observability of the pipeline, wire the check into the earliest stage that has enough context—usually PR for tests and main for deploy. Integrate with ACR, Key Vault or OIDC, and Argo CD for cluster sync. Failed stages should emit structured logs and failure class tags for MTTR tracking.

#### When to use / when NOT to use
Adopt when team size or compliance requires repeatable delivery. Skip heavyweight gates for throwaway prototypes. For Observability of the pipeline, enforce on main and prod paths; allow faster feedback loops on feature branches where safe. Never bypass prod gates without break-glass documentation and post-incident restore of controls.

#### Production example
On `order-service`, we applied observability of the pipeline in the pipeline: PR blocked on failure, main published digest `sha256:abc…`, GitOps PR updated `values-prod.yaml`, smoke tests passed, and rollback was a Git revert tested in staging first. Change failure rate dropped after we classified flakes and added quarantine policy.

#### Common mistakes
- Manual prod deploy bypassing pipeline
- No path filters in monorepo—wasted CI minutes
- Secrets in workflow YAML or logs
- Treating green CI as optional before merge

#### Interview follow-ups (with model answers)

**Q:** How does Observability of the pipeline affect rollback and MTTR?
**A:** Rollback is fast only when artifacts are immutable and cluster desired state lives in Git. I revert the GitOps PR or Helm revision, re-run smoke tests against the same image digest, and verify database migration compatibility. MTTR improves when prod promotion is reproducible and not a manual kubectl hotfix. I measure time from failed deploy to restored SLO and track failure class in a dashboard.

**Q:** What gate would you add after a failure involving Observability of the pipeline?
**A:** I classify the failure (flake, infra, quality, security, deploy) and add an automated guard in the right stage. Examples: quarantine flaky integration tests, ephemeral runners with disk cleanup, required Trivy/Sonar on main, or environment approval for production. Track recurrence quarterly and tie to DORA change failure rate separately from PR red builds.

**Q:** How do you explain Observability of the pipeline to a team new to CI/CD on Spring and AKS?
**A:** I walk a concrete path: PR runs Maven verify and scans; merge publishes a signed image to ACR; a GitOps PR updates Helm values; Argo CD syncs to AKS; smoke tests hit `/actuator/health`. I emphasize CI validates change, CD/GitOps promotes immutable artifacts, and main stays green with feature flags for incomplete work.

#### Scenario probe

**Situation:** Production deploy failed after a green PR; the panel asks how Observability of the pipeline fits your response.

**Model answer:** I timeline the pipeline: which stage failed, which digest was promoted, whether Argo drifted from Git. I roll forward or revert Git, verify smoke tests and Flyway order, communicate MTTR, and add a gate so this failure class is caught pre-prod next time.

---
### 40. Config promotion

**Short answer:** Promote same Helm chart; only values change per env. No manual kubectl set env in prod. Measure impact with DORA metrics and document rollback paths before changing prod gates.

#### What it is
Config promotion is a core practice in modern delivery for Spring microservices on AKS. It connects developer workflow to production safety—artifacts, gates, GitOps, and observability—not just running Jenkins jobs. Interviewers want trade-offs, failure modes, and how you measured improvement with DORA metrics.

#### How it works (internals)
Pipelines trigger on git events, run on ephemeral agents, publish immutable artifacts, and promote through environments with approvals. For config promotion, wire the check into the earliest stage that has enough context—usually PR for tests and main for deploy. Integrate with ACR, Key Vault or OIDC, and Argo CD for cluster sync. Failed stages should emit structured logs and failure class tags for MTTR tracking.

#### When to use / when NOT to use
Adopt when team size or compliance requires repeatable delivery. Skip heavyweight gates for throwaway prototypes. For Config promotion, enforce on main and prod paths; allow faster feedback loops on feature branches where safe. Never bypass prod gates without break-glass documentation and post-incident restore of controls.

#### Production example
On `order-service`, we applied config promotion in the pipeline: PR blocked on failure, main published digest `sha256:abc…`, GitOps PR updated `values-prod.yaml`, smoke tests passed, and rollback was a Git revert tested in staging first. Change failure rate dropped after we classified flakes and added quarantine policy.

#### Common mistakes
- Manual prod deploy bypassing pipeline
- No path filters in monorepo—wasted CI minutes
- Secrets in workflow YAML or logs
- Treating green CI as optional before merge

#### Interview follow-ups (with model answers)

**Q:** How does Config promotion affect rollback and MTTR?
**A:** Rollback is fast only when artifacts are immutable and cluster desired state lives in Git. I revert the GitOps PR or Helm revision, re-run smoke tests against the same image digest, and verify database migration compatibility. MTTR improves when prod promotion is reproducible and not a manual kubectl hotfix. I measure time from failed deploy to restored SLO and track failure class in a dashboard.

**Q:** What gate would you add after a failure involving Config promotion?
**A:** I classify the failure (flake, infra, quality, security, deploy) and add an automated guard in the right stage. Examples: quarantine flaky integration tests, ephemeral runners with disk cleanup, required Trivy/Sonar on main, or environment approval for production. Track recurrence quarterly and tie to DORA change failure rate separately from PR red builds.

**Q:** How do you explain Config promotion to a team new to CI/CD on Spring and AKS?
**A:** I walk a concrete path: PR runs Maven verify and scans; merge publishes a signed image to ACR; a GitOps PR updates Helm values; Argo CD syncs to AKS; smoke tests hit `/actuator/health`. I emphasize CI validates change, CD/GitOps promotes immutable artifacts, and main stays green with feature flags for incomplete work.

#### Scenario probe

**Situation:** Production deploy failed after a green PR; the panel asks how Config promotion fits your response.

**Model answer:** I timeline the pipeline: which stage failed, which digest was promoted, whether Argo drifted from Git. I roll forward or revert Git, verify smoke tests and Flyway order, communicate MTTR, and add a gate so this failure class is caught pre-prod next time.

---
### 41. Smoke tests post-deploy

**Short answer:** Hit `/actuator/health`, critical API paths, Kafka consume one message. Fail deploy on smoke red. Measure impact with DORA metrics and document rollback paths before changing prod gates.

#### What it is
Smoke tests post-deploy is a core practice in modern delivery for Spring microservices on AKS. It connects developer workflow to production safety—artifacts, gates, GitOps, and observability—not just running Jenkins jobs. Interviewers want trade-offs, failure modes, and how you measured improvement with DORA metrics.

#### How it works (internals)
Pipelines trigger on git events, run on ephemeral agents, publish immutable artifacts, and promote through environments with approvals. For smoke tests post-deploy, wire the check into the earliest stage that has enough context—usually PR for tests and main for deploy. Integrate with ACR, Key Vault or OIDC, and Argo CD for cluster sync. Failed stages should emit structured logs and failure class tags for MTTR tracking.

#### When to use / when NOT to use
Adopt when team size or compliance requires repeatable delivery. Skip heavyweight gates for throwaway prototypes. For Smoke tests post-deploy, enforce on main and prod paths; allow faster feedback loops on feature branches where safe. Never bypass prod gates without break-glass documentation and post-incident restore of controls.

#### Production example
On `order-service`, we applied smoke tests post-deploy in the pipeline: PR blocked on failure, main published digest `sha256:abc…`, GitOps PR updated `values-prod.yaml`, smoke tests passed, and rollback was a Git revert tested in staging first. Change failure rate dropped after we classified flakes and added quarantine policy.

#### Common mistakes
- Manual prod deploy bypassing pipeline
- No path filters in monorepo—wasted CI minutes
- Secrets in workflow YAML or logs
- Treating green CI as optional before merge

#### Interview follow-ups (with model answers)

**Q:** How does Smoke tests post-deploy affect rollback and MTTR?
**A:** Rollback is fast only when artifacts are immutable and cluster desired state lives in Git. I revert the GitOps PR or Helm revision, re-run smoke tests against the same image digest, and verify database migration compatibility. MTTR improves when prod promotion is reproducible and not a manual kubectl hotfix. I measure time from failed deploy to restored SLO and track failure class in a dashboard.

**Q:** What gate would you add after a failure involving Smoke tests post-deploy?
**A:** I classify the failure (flake, infra, quality, security, deploy) and add an automated guard in the right stage. Examples: quarantine flaky integration tests, ephemeral runners with disk cleanup, required Trivy/Sonar on main, or environment approval for production. Track recurrence quarterly and tie to DORA change failure rate separately from PR red builds.

**Q:** How do you explain Smoke tests post-deploy to a team new to CI/CD on Spring and AKS?
**A:** I walk a concrete path: PR runs Maven verify and scans; merge publishes a signed image to ACR; a GitOps PR updates Helm values; Argo CD syncs to AKS; smoke tests hit `/actuator/health`. I emphasize CI validates change, CD/GitOps promotes immutable artifacts, and main stays green with feature flags for incomplete work.

#### Scenario probe

**Situation:** Production deploy failed after a green PR; the panel asks how Smoke tests post-deploy fits your response.

**Model answer:** I timeline the pipeline: which stage failed, which digest was promoted, whether Argo drifted from Git. I roll forward or revert Git, verify smoke tests and Flyway order, communicate MTTR, and add a gate so this failure class is caught pre-prod next time.

---
### 42. Database in pipeline

**Short answer:** Testcontainers or ephemeral schema for integration; prod migrations gated and backward compatible. Measure impact with DORA metrics and document rollback paths before changing prod gates.

#### What it is
Database in pipeline is a core practice in modern delivery for Spring microservices on AKS. It connects developer workflow to production safety—artifacts, gates, GitOps, and observability—not just running Jenkins jobs. Interviewers want trade-offs, failure modes, and how you measured improvement with DORA metrics.

#### How it works (internals)
Pipelines trigger on git events, run on ephemeral agents, publish immutable artifacts, and promote through environments with approvals. For database in pipeline, wire the check into the earliest stage that has enough context—usually PR for tests and main for deploy. Integrate with ACR, Key Vault or OIDC, and Argo CD for cluster sync. Failed stages should emit structured logs and failure class tags for MTTR tracking.

#### When to use / when NOT to use
Adopt when team size or compliance requires repeatable delivery. Skip heavyweight gates for throwaway prototypes. For Database in pipeline, enforce on main and prod paths; allow faster feedback loops on feature branches where safe. Never bypass prod gates without break-glass documentation and post-incident restore of controls.

#### Production example
On `order-service`, we applied database in pipeline in the pipeline: PR blocked on failure, main published digest `sha256:abc…`, GitOps PR updated `values-prod.yaml`, smoke tests passed, and rollback was a Git revert tested in staging first. Change failure rate dropped after we classified flakes and added quarantine policy.

#### Common mistakes
- Manual prod deploy bypassing pipeline
- No path filters in monorepo—wasted CI minutes
- Secrets in workflow YAML or logs
- Treating green CI as optional before merge

#### Interview follow-ups (with model answers)

**Q:** How does Database in pipeline affect rollback and MTTR?
**A:** Rollback is fast only when artifacts are immutable and cluster desired state lives in Git. I revert the GitOps PR or Helm revision, re-run smoke tests against the same image digest, and verify database migration compatibility. MTTR improves when prod promotion is reproducible and not a manual kubectl hotfix. I measure time from failed deploy to restored SLO and track failure class in a dashboard.

**Q:** What gate would you add after a failure involving Database in pipeline?
**A:** I classify the failure (flake, infra, quality, security, deploy) and add an automated guard in the right stage. Examples: quarantine flaky integration tests, ephemeral runners with disk cleanup, required Trivy/Sonar on main, or environment approval for production. Track recurrence quarterly and tie to DORA change failure rate separately from PR red builds.

**Q:** How do you explain Database in pipeline to a team new to CI/CD on Spring and AKS?
**A:** I walk a concrete path: PR runs Maven verify and scans; merge publishes a signed image to ACR; a GitOps PR updates Helm values; Argo CD syncs to AKS; smoke tests hit `/actuator/health`. I emphasize CI validates change, CD/GitOps promotes immutable artifacts, and main stays green with feature flags for incomplete work.

#### Scenario probe

**Situation:** Production deploy failed after a green PR; the panel asks how Database in pipeline fits your response.

**Model answer:** I timeline the pipeline: which stage failed, which digest was promoted, whether Argo drifted from Git. I roll forward or revert Git, verify smoke tests and Flyway order, communicate MTTR, and add a gate so this failure class is caught pre-prod next time.

---
### 43. Kafka topics as code

**Short answer:** Topic CRs or Terraform; pipeline validates ACLs and retention. App pipeline does not create topics ad hoc. Measure impact with DORA metrics and document rollback paths before changing prod gates.

#### What it is
Kafka topics as code is a core practice in modern delivery for Spring microservices on AKS. It connects developer workflow to production safety—artifacts, gates, GitOps, and observability—not just running Jenkins jobs. Interviewers want trade-offs, failure modes, and how you measured improvement with DORA metrics.

#### How it works (internals)
Pipelines trigger on git events, run on ephemeral agents, publish immutable artifacts, and promote through environments with approvals. For kafka topics as code, wire the check into the earliest stage that has enough context—usually PR for tests and main for deploy. Integrate with ACR, Key Vault or OIDC, and Argo CD for cluster sync. Failed stages should emit structured logs and failure class tags for MTTR tracking.

#### When to use / when NOT to use
Adopt when team size or compliance requires repeatable delivery. Skip heavyweight gates for throwaway prototypes. For Kafka topics as code, enforce on main and prod paths; allow faster feedback loops on feature branches where safe. Never bypass prod gates without break-glass documentation and post-incident restore of controls.

#### Production example
On `order-service`, we applied kafka topics as code in the pipeline: PR blocked on failure, main published digest `sha256:abc…`, GitOps PR updated `values-prod.yaml`, smoke tests passed, and rollback was a Git revert tested in staging first. Change failure rate dropped after we classified flakes and added quarantine policy.

#### Common mistakes
- Manual prod deploy bypassing pipeline
- No path filters in monorepo—wasted CI minutes
- Secrets in workflow YAML or logs
- Treating green CI as optional before merge

#### Interview follow-ups (with model answers)

**Q:** How does Kafka topics as code affect rollback and MTTR?
**A:** Rollback is fast only when artifacts are immutable and cluster desired state lives in Git. I revert the GitOps PR or Helm revision, re-run smoke tests against the same image digest, and verify database migration compatibility. MTTR improves when prod promotion is reproducible and not a manual kubectl hotfix. I measure time from failed deploy to restored SLO and track failure class in a dashboard.

**Q:** What gate would you add after a failure involving Kafka topics as code?
**A:** I classify the failure (flake, infra, quality, security, deploy) and add an automated guard in the right stage. Examples: quarantine flaky integration tests, ephemeral runners with disk cleanup, required Trivy/Sonar on main, or environment approval for production. Track recurrence quarterly and tie to DORA change failure rate separately from PR red builds.

**Q:** How do you explain Kafka topics as code to a team new to CI/CD on Spring and AKS?
**A:** I walk a concrete path: PR runs Maven verify and scans; merge publishes a signed image to ACR; a GitOps PR updates Helm values; Argo CD syncs to AKS; smoke tests hit `/actuator/health`. I emphasize CI validates change, CD/GitOps promotes immutable artifacts, and main stays green with feature flags for incomplete work.

#### Scenario probe

**Situation:** Production deploy failed after a green PR; the panel asks how Kafka topics as code fits your response.

**Model answer:** I timeline the pipeline: which stage failed, which digest was promoted, whether Argo drifted from Git. I roll forward or revert Git, verify smoke tests and Flyway order, communicate MTTR, and add a gate so this failure class is caught pre-prod next time.

---
### 44. Documentation generated in CI

**Short answer:** OpenAPI, AsciiDoc site, ADR index published on merge. Docs PR triggers lighter workflow. Measure impact with DORA metrics and document rollback paths before changing prod gates.

#### What it is
Documentation generated in CI is a core practice in modern delivery for Spring microservices on AKS. It connects developer workflow to production safety—artifacts, gates, GitOps, and observability—not just running Jenkins jobs. Interviewers want trade-offs, failure modes, and how you measured improvement with DORA metrics.

#### How it works (internals)
Pipelines trigger on git events, run on ephemeral agents, publish immutable artifacts, and promote through environments with approvals. For documentation generated in ci, wire the check into the earliest stage that has enough context—usually PR for tests and main for deploy. Integrate with ACR, Key Vault or OIDC, and Argo CD for cluster sync. Failed stages should emit structured logs and failure class tags for MTTR tracking.

#### When to use / when NOT to use
Adopt when team size or compliance requires repeatable delivery. Skip heavyweight gates for throwaway prototypes. For Documentation generated in CI, enforce on main and prod paths; allow faster feedback loops on feature branches where safe. Never bypass prod gates without break-glass documentation and post-incident restore of controls.

#### Production example
On `order-service`, we applied documentation generated in ci in the pipeline: PR blocked on failure, main published digest `sha256:abc…`, GitOps PR updated `values-prod.yaml`, smoke tests passed, and rollback was a Git revert tested in staging first. Change failure rate dropped after we classified flakes and added quarantine policy.

#### Common mistakes
- Manual prod deploy bypassing pipeline
- No path filters in monorepo—wasted CI minutes
- Secrets in workflow YAML or logs
- Treating green CI as optional before merge

#### Interview follow-ups (with model answers)

**Q:** How does Documentation generated in CI affect rollback and MTTR?
**A:** Rollback is fast only when artifacts are immutable and cluster desired state lives in Git. I revert the GitOps PR or Helm revision, re-run smoke tests against the same image digest, and verify database migration compatibility. MTTR improves when prod promotion is reproducible and not a manual kubectl hotfix. I measure time from failed deploy to restored SLO and track failure class in a dashboard.

**Q:** What gate would you add after a failure involving Documentation generated in CI?
**A:** I classify the failure (flake, infra, quality, security, deploy) and add an automated guard in the right stage. Examples: quarantine flaky integration tests, ephemeral runners with disk cleanup, required Trivy/Sonar on main, or environment approval for production. Track recurrence quarterly and tie to DORA change failure rate separately from PR red builds.

**Q:** How do you explain Documentation generated in CI to a team new to CI/CD on Spring and AKS?
**A:** I walk a concrete path: PR runs Maven verify and scans; merge publishes a signed image to ACR; a GitOps PR updates Helm values; Argo CD syncs to AKS; smoke tests hit `/actuator/health`. I emphasize CI validates change, CD/GitOps promotes immutable artifacts, and main stays green with feature flags for incomplete work.

#### Scenario probe

**Situation:** Production deploy failed after a green PR; the panel asks how Documentation generated in CI fits your response.

**Model answer:** I timeline the pipeline: which stage failed, which digest was promoted, whether Argo drifted from Git. I roll forward or revert Git, verify smoke tests and Flyway order, communicate MTTR, and add a gate so this failure class is caught pre-prod next time.

---
### 45. AI in CI

**Short answer:** AI assists code review and test generation; human owns gates and prod promotion. No auto-merge on AI alone. Measure impact with DORA metrics and document rollback paths before changing prod gates.

#### What it is
AI in CI is a core practice in modern delivery for Spring microservices on AKS. It connects developer workflow to production safety—artifacts, gates, GitOps, and observability—not just running Jenkins jobs. Interviewers want trade-offs, failure modes, and how you measured improvement with DORA metrics.

#### How it works (internals)
Pipelines trigger on git events, run on ephemeral agents, publish immutable artifacts, and promote through environments with approvals. For ai in ci, wire the check into the earliest stage that has enough context—usually PR for tests and main for deploy. Integrate with ACR, Key Vault or OIDC, and Argo CD for cluster sync. Failed stages should emit structured logs and failure class tags for MTTR tracking.

#### When to use / when NOT to use
Adopt when team size or compliance requires repeatable delivery. Skip heavyweight gates for throwaway prototypes. For AI in CI, enforce on main and prod paths; allow faster feedback loops on feature branches where safe. Never bypass prod gates without break-glass documentation and post-incident restore of controls.

#### Production example
On `order-service`, we applied ai in ci in the pipeline: PR blocked on failure, main published digest `sha256:abc…`, GitOps PR updated `values-prod.yaml`, smoke tests passed, and rollback was a Git revert tested in staging first. Change failure rate dropped after we classified flakes and added quarantine policy.

#### Common mistakes
- Manual prod deploy bypassing pipeline
- No path filters in monorepo—wasted CI minutes
- Secrets in workflow YAML or logs
- Treating green CI as optional before merge

#### Interview follow-ups (with model answers)

**Q:** How does AI in CI affect rollback and MTTR?
**A:** Rollback is fast only when artifacts are immutable and cluster desired state lives in Git. I revert the GitOps PR or Helm revision, re-run smoke tests against the same image digest, and verify database migration compatibility. MTTR improves when prod promotion is reproducible and not a manual kubectl hotfix. I measure time from failed deploy to restored SLO and track failure class in a dashboard.

**Q:** What gate would you add after a failure involving AI in CI?
**A:** I classify the failure (flake, infra, quality, security, deploy) and add an automated guard in the right stage. Examples: quarantine flaky integration tests, ephemeral runners with disk cleanup, required Trivy/Sonar on main, or environment approval for production. Track recurrence quarterly and tie to DORA change failure rate separately from PR red builds.

**Q:** How do you explain AI in CI to a team new to CI/CD on Spring and AKS?
**A:** I walk a concrete path: PR runs Maven verify and scans; merge publishes a signed image to ACR; a GitOps PR updates Helm values; Argo CD syncs to AKS; smoke tests hit `/actuator/health`. I emphasize CI validates change, CD/GitOps promotes immutable artifacts, and main stays green with feature flags for incomplete work.

#### Scenario probe

**Situation:** Production deploy failed after a green PR; the panel asks how AI in CI fits your response.

**Model answer:** I timeline the pipeline: which stage failed, which digest was promoted, whether Argo drifted from Git. I roll forward or revert Git, verify smoke tests and Flyway order, communicate MTTR, and add a gate so this failure class is caught pre-prod next time.

---
### 46. Compliance: SoD

**Short answer:** Separate roles: dev merges, platform approves prod, security owns scan waivers. Audit log retention. Measure impact with DORA metrics and document rollback paths before changing prod gates.

#### What it is
Compliance: SoD is a core practice in modern delivery for Spring microservices on AKS. It connects developer workflow to production safety—artifacts, gates, GitOps, and observability—not just running Jenkins jobs. Interviewers want trade-offs, failure modes, and how you measured improvement with DORA metrics.

#### How it works (internals)
Pipelines trigger on git events, run on ephemeral agents, publish immutable artifacts, and promote through environments with approvals. For compliance: sod, wire the check into the earliest stage that has enough context—usually PR for tests and main for deploy. Integrate with ACR, Key Vault or OIDC, and Argo CD for cluster sync. Failed stages should emit structured logs and failure class tags for MTTR tracking.

#### When to use / when NOT to use
Adopt when team size or compliance requires repeatable delivery. Skip heavyweight gates for throwaway prototypes. For Compliance: SoD, enforce on main and prod paths; allow faster feedback loops on feature branches where safe. Never bypass prod gates without break-glass documentation and post-incident restore of controls.

#### Production example
On `order-service`, we applied compliance: sod in the pipeline: PR blocked on failure, main published digest `sha256:abc…`, GitOps PR updated `values-prod.yaml`, smoke tests passed, and rollback was a Git revert tested in staging first. Change failure rate dropped after we classified flakes and added quarantine policy.

#### Common mistakes
- Manual prod deploy bypassing pipeline
- No path filters in monorepo—wasted CI minutes
- Secrets in workflow YAML or logs
- Treating green CI as optional before merge

#### Interview follow-ups (with model answers)

**Q:** How does Compliance: SoD affect rollback and MTTR?
**A:** Rollback is fast only when artifacts are immutable and cluster desired state lives in Git. I revert the GitOps PR or Helm revision, re-run smoke tests against the same image digest, and verify database migration compatibility. MTTR improves when prod promotion is reproducible and not a manual kubectl hotfix. I measure time from failed deploy to restored SLO and track failure class in a dashboard.

**Q:** What gate would you add after a failure involving Compliance: SoD?
**A:** I classify the failure (flake, infra, quality, security, deploy) and add an automated guard in the right stage. Examples: quarantine flaky integration tests, ephemeral runners with disk cleanup, required Trivy/Sonar on main, or environment approval for production. Track recurrence quarterly and tie to DORA change failure rate separately from PR red builds.

**Q:** How do you explain Compliance: SoD to a team new to CI/CD on Spring and AKS?
**A:** I walk a concrete path: PR runs Maven verify and scans; merge publishes a signed image to ACR; a GitOps PR updates Helm values; Argo CD syncs to AKS; smoke tests hit `/actuator/health`. I emphasize CI validates change, CD/GitOps promotes immutable artifacts, and main stays green with feature flags for incomplete work.

#### Scenario probe

**Situation:** Production deploy failed after a green PR; the panel asks how Compliance: SoD fits your response.

**Model answer:** I timeline the pipeline: which stage failed, which digest was promoted, whether Argo drifted from Git. I roll forward or revert Git, verify smoke tests and Flyway order, communicate MTTR, and add a gate so this failure class is caught pre-prod next time.

---
### 47. Break-glass

**Short answer:** Documented emergency bypass with time box, extra approvers, mandatory post-incident PR restoring gates. Measure impact with DORA metrics and document rollback paths before changing prod gates.

#### What it is
Break-glass is a core practice in modern delivery for Spring microservices on AKS. It connects developer workflow to production safety—artifacts, gates, GitOps, and observability—not just running Jenkins jobs. Interviewers want trade-offs, failure modes, and how you measured improvement with DORA metrics.

#### How it works (internals)
Pipelines trigger on git events, run on ephemeral agents, publish immutable artifacts, and promote through environments with approvals. For break-glass, wire the check into the earliest stage that has enough context—usually PR for tests and main for deploy. Integrate with ACR, Key Vault or OIDC, and Argo CD for cluster sync. Failed stages should emit structured logs and failure class tags for MTTR tracking.

#### When to use / when NOT to use
Adopt when team size or compliance requires repeatable delivery. Skip heavyweight gates for throwaway prototypes. For Break-glass, enforce on main and prod paths; allow faster feedback loops on feature branches where safe. Never bypass prod gates without break-glass documentation and post-incident restore of controls.

#### Production example
On `order-service`, we applied break-glass in the pipeline: PR blocked on failure, main published digest `sha256:abc…`, GitOps PR updated `values-prod.yaml`, smoke tests passed, and rollback was a Git revert tested in staging first. Change failure rate dropped after we classified flakes and added quarantine policy.

#### Common mistakes
- Manual prod deploy bypassing pipeline
- No path filters in monorepo—wasted CI minutes
- Secrets in workflow YAML or logs
- Treating green CI as optional before merge

#### Interview follow-ups (with model answers)

**Q:** How does Break-glass affect rollback and MTTR?
**A:** Rollback is fast only when artifacts are immutable and cluster desired state lives in Git. I revert the GitOps PR or Helm revision, re-run smoke tests against the same image digest, and verify database migration compatibility. MTTR improves when prod promotion is reproducible and not a manual kubectl hotfix. I measure time from failed deploy to restored SLO and track failure class in a dashboard.

**Q:** What gate would you add after a failure involving Break-glass?
**A:** I classify the failure (flake, infra, quality, security, deploy) and add an automated guard in the right stage. Examples: quarantine flaky integration tests, ephemeral runners with disk cleanup, required Trivy/Sonar on main, or environment approval for production. Track recurrence quarterly and tie to DORA change failure rate separately from PR red builds.

**Q:** How do you explain Break-glass to a team new to CI/CD on Spring and AKS?
**A:** I walk a concrete path: PR runs Maven verify and scans; merge publishes a signed image to ACR; a GitOps PR updates Helm values; Argo CD syncs to AKS; smoke tests hit `/actuator/health`. I emphasize CI validates change, CD/GitOps promotes immutable artifacts, and main stays green with feature flags for incomplete work.

#### Scenario probe

**Situation:** Production deploy failed after a green PR; the panel asks how Break-glass fits your response.

**Model answer:** I timeline the pipeline: which stage failed, which digest was promoted, whether Argo drifted from Git. I roll forward or revert Git, verify smoke tests and Flyway order, communicate MTTR, and add a gate so this failure class is caught pre-prod next time.

---
### 48. Cost of CI

**Short answer:** Right-size runners, path filters, cache, spot instances for non-prod. Chargeback tags per team. Measure impact with DORA metrics and document rollback paths before changing prod gates.

#### What it is
Cost of CI is a core practice in modern delivery for Spring microservices on AKS. It connects developer workflow to production safety—artifacts, gates, GitOps, and observability—not just running Jenkins jobs. Interviewers want trade-offs, failure modes, and how you measured improvement with DORA metrics.

#### How it works (internals)
Pipelines trigger on git events, run on ephemeral agents, publish immutable artifacts, and promote through environments with approvals. For cost of ci, wire the check into the earliest stage that has enough context—usually PR for tests and main for deploy. Integrate with ACR, Key Vault or OIDC, and Argo CD for cluster sync. Failed stages should emit structured logs and failure class tags for MTTR tracking.

#### When to use / when NOT to use
Adopt when team size or compliance requires repeatable delivery. Skip heavyweight gates for throwaway prototypes. For Cost of CI, enforce on main and prod paths; allow faster feedback loops on feature branches where safe. Never bypass prod gates without break-glass documentation and post-incident restore of controls.

#### Production example
On `order-service`, we applied cost of ci in the pipeline: PR blocked on failure, main published digest `sha256:abc…`, GitOps PR updated `values-prod.yaml`, smoke tests passed, and rollback was a Git revert tested in staging first. Change failure rate dropped after we classified flakes and added quarantine policy.

#### Common mistakes
- Manual prod deploy bypassing pipeline
- No path filters in monorepo—wasted CI minutes
- Secrets in workflow YAML or logs
- Treating green CI as optional before merge

#### Interview follow-ups (with model answers)

**Q:** How does Cost of CI affect rollback and MTTR?
**A:** Rollback is fast only when artifacts are immutable and cluster desired state lives in Git. I revert the GitOps PR or Helm revision, re-run smoke tests against the same image digest, and verify database migration compatibility. MTTR improves when prod promotion is reproducible and not a manual kubectl hotfix. I measure time from failed deploy to restored SLO and track failure class in a dashboard.

**Q:** What gate would you add after a failure involving Cost of CI?
**A:** I classify the failure (flake, infra, quality, security, deploy) and add an automated guard in the right stage. Examples: quarantine flaky integration tests, ephemeral runners with disk cleanup, required Trivy/Sonar on main, or environment approval for production. Track recurrence quarterly and tie to DORA change failure rate separately from PR red builds.

**Q:** How do you explain Cost of CI to a team new to CI/CD on Spring and AKS?
**A:** I walk a concrete path: PR runs Maven verify and scans; merge publishes a signed image to ACR; a GitOps PR updates Helm values; Argo CD syncs to AKS; smoke tests hit `/actuator/health`. I emphasize CI validates change, CD/GitOps promotes immutable artifacts, and main stays green with feature flags for incomplete work.

#### Scenario probe

**Situation:** Production deploy failed after a green PR; the panel asks how Cost of CI fits your response.

**Model answer:** I timeline the pipeline: which stage failed, which digest was promoted, whether Argo drifted from Git. I roll forward or revert Git, verify smoke tests and Flyway order, communicate MTTR, and add a gate so this failure class is caught pre-prod next time.

---
### 49. Definition of done includes pipeline

**Short answer:** No feature done without green CI, scan, and deploy path to dev. DoD in team working agreement. Measure impact with DORA metrics and document rollback paths before changing prod gates.

#### What it is
Definition of done includes pipeline is a core practice in modern delivery for Spring microservices on AKS. It connects developer workflow to production safety—artifacts, gates, GitOps, and observability—not just running Jenkins jobs. Interviewers want trade-offs, failure modes, and how you measured improvement with DORA metrics.

#### How it works (internals)
Pipelines trigger on git events, run on ephemeral agents, publish immutable artifacts, and promote through environments with approvals. For definition of done includes pipeline, wire the check into the earliest stage that has enough context—usually PR for tests and main for deploy. Integrate with ACR, Key Vault or OIDC, and Argo CD for cluster sync. Failed stages should emit structured logs and failure class tags for MTTR tracking.

#### When to use / when NOT to use
Adopt when team size or compliance requires repeatable delivery. Skip heavyweight gates for throwaway prototypes. For Definition of done includes pipeline, enforce on main and prod paths; allow faster feedback loops on feature branches where safe. Never bypass prod gates without break-glass documentation and post-incident restore of controls.

#### Production example
On `order-service`, we applied definition of done includes pipeline in the pipeline: PR blocked on failure, main published digest `sha256:abc…`, GitOps PR updated `values-prod.yaml`, smoke tests passed, and rollback was a Git revert tested in staging first. Change failure rate dropped after we classified flakes and added quarantine policy.

#### Common mistakes
- Manual prod deploy bypassing pipeline
- No path filters in monorepo—wasted CI minutes
- Secrets in workflow YAML or logs
- Treating green CI as optional before merge

#### Interview follow-ups (with model answers)

**Q:** How does Definition of done includes pipeline affect rollback and MTTR?
**A:** Rollback is fast only when artifacts are immutable and cluster desired state lives in Git. I revert the GitOps PR or Helm revision, re-run smoke tests against the same image digest, and verify database migration compatibility. MTTR improves when prod promotion is reproducible and not a manual kubectl hotfix. I measure time from failed deploy to restored SLO and track failure class in a dashboard.

**Q:** What gate would you add after a failure involving Definition of done includes pipeline?
**A:** I classify the failure (flake, infra, quality, security, deploy) and add an automated guard in the right stage. Examples: quarantine flaky integration tests, ephemeral runners with disk cleanup, required Trivy/Sonar on main, or environment approval for production. Track recurrence quarterly and tie to DORA change failure rate separately from PR red builds.

**Q:** How do you explain Definition of done includes pipeline to a team new to CI/CD on Spring and AKS?
**A:** I walk a concrete path: PR runs Maven verify and scans; merge publishes a signed image to ACR; a GitOps PR updates Helm values; Argo CD syncs to AKS; smoke tests hit `/actuator/health`. I emphasize CI validates change, CD/GitOps promotes immutable artifacts, and main stays green with feature flags for incomplete work.

#### Scenario probe

**Situation:** Production deploy failed after a green PR; the panel asks how Definition of done includes pipeline fits your response.

**Model answer:** I timeline the pipeline: which stage failed, which digest was promoted, whether Argo drifted from Git. I roll forward or revert Git, verify smoke tests and Flyway order, communicate MTTR, and add a gate so this failure class is caught pre-prod next time.

---
### 50. Senior CD story

**Short answer:** Narrate end-to-end: PR gates, signed digest, GitOps prod, canary analysis, rollback drill, DORA improvement with numbers. Measure impact with DORA metrics and document rollback paths before changing prod gates.

#### What it is
Senior CD story is a core practice in modern delivery for Spring microservices on AKS. It connects developer workflow to production safety—artifacts, gates, GitOps, and observability—not just running Jenkins jobs. Interviewers want trade-offs, failure modes, and how you measured improvement with DORA metrics.

#### How it works (internals)
Pipelines trigger on git events, run on ephemeral agents, publish immutable artifacts, and promote through environments with approvals. For senior cd story, wire the check into the earliest stage that has enough context—usually PR for tests and main for deploy. Integrate with ACR, Key Vault or OIDC, and Argo CD for cluster sync. Failed stages should emit structured logs and failure class tags for MTTR tracking.

#### When to use / when NOT to use
Adopt when team size or compliance requires repeatable delivery. Skip heavyweight gates for throwaway prototypes. For Senior CD story, enforce on main and prod paths; allow faster feedback loops on feature branches where safe. Never bypass prod gates without break-glass documentation and post-incident restore of controls.

#### Production example
On `order-service`, we applied senior cd story in the pipeline: PR blocked on failure, main published digest `sha256:abc…`, GitOps PR updated `values-prod.yaml`, smoke tests passed, and rollback was a Git revert tested in staging first. Change failure rate dropped after we classified flakes and added quarantine policy.

#### Common mistakes
- Manual prod deploy bypassing pipeline
- No path filters in monorepo—wasted CI minutes
- Secrets in workflow YAML or logs
- Treating green CI as optional before merge

#### Interview follow-ups (with model answers)

**Q:** How does Senior CD story affect rollback and MTTR?
**A:** Rollback is fast only when artifacts are immutable and cluster desired state lives in Git. I revert the GitOps PR or Helm revision, re-run smoke tests against the same image digest, and verify database migration compatibility. MTTR improves when prod promotion is reproducible and not a manual kubectl hotfix. I measure time from failed deploy to restored SLO and track failure class in a dashboard.

**Q:** What gate would you add after a failure involving Senior CD story?
**A:** I classify the failure (flake, infra, quality, security, deploy) and add an automated guard in the right stage. Examples: quarantine flaky integration tests, ephemeral runners with disk cleanup, required Trivy/Sonar on main, or environment approval for production. Track recurrence quarterly and tie to DORA change failure rate separately from PR red builds.

**Q:** How do you explain Senior CD story to a team new to CI/CD on Spring and AKS?
**A:** I walk a concrete path: PR runs Maven verify and scans; merge publishes a signed image to ACR; a GitOps PR updates Helm values; Argo CD syncs to AKS; smoke tests hit `/actuator/health`. I emphasize CI validates change, CD/GitOps promotes immutable artifacts, and main stays green with feature flags for incomplete work.

#### Scenario probe

**Situation:** Production deploy failed after a green PR; the panel asks how Senior CD story fits your response.

**Model answer:** I timeline the pipeline: which stage failed, which digest was promoted, whether Argo drifted from Git. I roll forward or revert Git, verify smoke tests and Flyway order, communicate MTTR, and add a gate so this failure class is caught pre-prod next time.

---
### 51. GitLab CI vs GitHub Actions — senior comparison.

**Short answer:** Both run pipeline-as-code on git events. GitLab integrates SCM+CI+registry in one product; GitHub Actions leverages marketplace and GitHub-native UX with tighter OIDC to Azure. Pick based on org standard, runner strategy, and compliance logging—not feature checklists alone.

#### What it is
GitLab `.gitlab-ci.yml` with runners and environments; GitHub Actions YAML with reusable workflows and environments requiring reviewers.

#### How it works (internals)
GitLab has built-in container registry and deploy boards; GitHub uses Actions + ACR + Environments + branch protection. Both support OIDC to cloud.

#### When to use / when NOT to use
Enterprise on GitHub.com often Actions; GitLab self-managed for air-gap. Hybrid monorepos need path filters either way.

#### Production example
Migrated 40 Spring services from Jenkins to Actions with reusable workflow; kept GitLab only for legacy mobile team.

#### Common mistakes
- Duplicating CI on both platforms
- Fork PR secret exposure on either

#### Interview follow-ups (with model answers)

**Q:** Self-hosted runners?
**A:** Both support; isolate prod deploy runners; ephemeral preferred.

**Q:** Compliance logs?
**A:** GitLab audit events vs GitHub audit log API—map to SOX retention.

#### Scenario probe

CTO asks GitLab vs Actions for greenfield Java platform.

Compare existing enterprise contracts, runner ops cost, OIDC to Azure maturity, developer familiarity. Pilot one service with plan/scan/deploy parity before mandate.

---
### 52. Tekton / Argo Workflows for K8s-native CI.

**Short answer:** Tekton and Argo Workflows run CI steps as Kubernetes CRDs—CI lives in cluster beside apps. Good when platform is K8s-first; heavier ops than managed SaaS CI.

#### What it is
Tekton Pipelines/PipelineRuns; Argo Workflows with DAG templates. Tasks run as pods; artifacts via PVC or object storage.

#### How it works (internals)
Kaniko builds images without Docker daemon; Workspaces cache Maven `.m2` between PipelineRuns; Argo DAG coordinates integration test fan-out.

#### When to use / when NOT to use
Use when compliance requires CI inside tenant cluster. Avoid for small teams without platform SRE.

#### Production example
Platform runs Tekton in `ci` namespace; builds Spring images with Kaniko; pushes to internal registry.

#### Common mistakes
- Shared cluster CI without isolation
- No resource quotas on build pods

#### Interview follow-ups (with model answers)

**Q:** vs Actions?
**A:** K8s-native when CI must not leave cluster; Actions simpler for GitHub-centric.

**Q:** Caching?
**A:** PVC layer cache or remote cache server; slower than SaaS unless tuned.

#### Scenario probe

Bank requires builds never leave K8s tenant.

Tekton with NetworkPolicy egress only to registry and Maven mirror; scan with Trivy task; sign with cosign task; no Docker daemon.

---
### 53. Supply chain: SLSA levels and provenance attestations.

**Short answer:** SLSA defines increasing supply-chain integrity levels—from scripted build to hermetic reproducible with provenance. Attestations (in-toto, Sigstore) prove who built what from which commit.

#### What it is
SLSA Level 1 requires versioned build script; Level 2 hosted builders; Level 3 non-falsifiable provenance. Java shops often start at L2 with GitHub Actions + SLSA generator.

#### How it works (internals)
Generate provenance on release; verify digest and predicate in deploy pipeline or Kyverno admission policy.

#### When to use / when NOT to use
Do not claim L3 without hermetic builds; be honest about gap and roadmap.

#### Production example
Order service release attaches SLSA provenance to ACR image; deploy policy verifies signature.

#### Common mistakes
- Signing without verification at deploy
- Provenance stored but never validated

#### Interview follow-ups (with model answers)

**Q:** Cosign?
**A:** Signs image digest; pairs with provenance predicate.

**Q:** Maven?
**A:** Gradle provenance emerging; at minimum lock dependencies and SBOM.

#### Scenario probe

Security asks SLSA level for prod images.

Document current level 2: GitHub hosted build, pinned actions, SBOM+sign. Roadmap: hermetic cache, isolated builders for L3.

---
### 54. Deployment freeze and change advisory board integration.

**Short answer:** Deployment freezes block prod promotes during peak events (Black Friday, fiscal close). CAB integrates pipeline approvals with change tickets—idempotent link between ServiceNow change and GitHub Environment.

#### What it is
Freeze via pipeline rule, GitHub Environment lock, or Argo CD sync pause. CAB validates change number via API before prod job starts.

#### How it works (internals)
Automate freeze calendar in pipeline; manual override with break-glass role and post-freeze review.

#### When to use / when NOT to use
Use freezes for peak retail and fiscal close; integrate CAB ticket ID as required env var on prod deploy job.

#### Production example
Retail org disables prod environment Dec 20-Jan 2 except P1 break-glass with VP approval.

#### Common mistakes
- Shadow deploys bypassing freeze via kubectl
- Freeze without comms to product teams

#### Interview follow-ups (with model answers)

**Q:** GitOps during freeze?
**A:** Argo sync paused or promotion workflow disabled; dev continues.

**Q:** Hotfix?
**A:** Break-glass path with smaller blast radius and extra approvers.

#### Scenario probe

P1 bug during freeze—product demands deploy.

Invoke break-glass: pre-approved CAB emergency template, deploy canary only, extra smoke, rollback rehearsed, post-freeze RCA.

---
### 55. Pipeline failure taxonomy and MTTR reduction.

**Short answer:** Classify failures: infra (runner, network), test (unit, flake), quality gate (scan), deploy (helm, smoke), external (registry, Azure). MTTR drops when alerts route to owner and runbooks match category.

#### What it is
Tag CI jobs with failure class in analytics dashboards. Track MTTR per class quarterly and tie to DORA change failure rate separately.

#### How it works (internals)
Flake quarantine with owner SLA; infra failures page platform; scan failures route security triage with SLA.

#### When to use / when NOT to use
Use taxonomy in weekly platform review; do not treat all red builds as equal urgency.

#### Production example
Dashboard: 40% flakes → quarantine sprint; infra MTTR 45m → ephemeral runners fix.

#### Common mistakes
- Untagged red builds
- Re-run until green culture

#### Interview follow-ups (with model answers)

**Q:** DORA CFR?
**A:** Only count deploy failures that reach prod; CI red != CFR but erodes trust.

**Q:** MTTR measure?
**A:** Time from failed prod deploy to restored SLO or rollback complete.

#### Scenario probe

Red main for three days; developers ignore CI.

Freeze merges, classify last 50 failures, fix top flake and infra bucket, restore required checks, communicate SLA.

---

## Scenario-based interview drills

### S1. Bad image promoted despite red scan

**Situation:** Trivy critical CVE merged; prod deployed.

**What they're testing:** Gate enforcement

**How to structure your answer:** How bypass happened; fix policy

**Model answer:** Disable bypass; immutable tag promotion only on green scan job artifact.

**Common weak answers:** Blame developer only

**Follow-up probes (with answers):**

**Q:** Deeper probe?
**A:** Owner, metric, prevention.

---
### S2. Argo CD auto-sync fights pipeline

**Situation:** Pipeline helm upgrade; Argo reverts.

**What they're testing:** GitOps source of truth

**How to structure your answer:** Single writer rule

**Model answer:** Remove imperative deploy; Git PR only.

**Common weak answers:** Disable Argo

**Follow-up probes (with answers):**

**Q:** Deeper probe?
**A:** Owner, metric, prevention.

---
### S3. Flyway migrate after app scaled

**Situation:** New pods hit old schema.

**What they're testing:** Migration ordering

**How to structure your answer:** Job before Deployment

**Model answer:** Sync wave or helm pre-hook Job.

**Common weak answers:** Manual sql

**Follow-up probes (with answers):**

**Q:** Deeper probe?
**A:** Owner, metric, prevention.

---
### S4. Secret leaked in workflow log

**Situation:** echo debug printed token.

**What they're testing:** Secret hygiene

**How to structure your answer:** Rotate, mask, audit

**Model answer:** Revoke secret; grep logs; gitleaks history.

**Common weak answers:** Delete log only

**Follow-up probes (with answers):**

**Q:** Deeper probe?
**A:** Owner, metric, prevention.

---
### S5. Canary passed; prod SLO burned

**Situation:** Error rate lagging metric.

**What they're testing:** Analysis window

**How to structure your answer:** Prometheus rules

**Model answer:** Longer analysis; customer SLO not just 5xx.

**Common weak answers:** Ship faster

**Follow-up probes (with answers):**

**Q:** Deeper probe?
**A:** Owner, metric, prevention.

---
### S6. Monorepo path filter miss

**Situation:** Docs PR rebuilt all images.

**What they're testing:** Path filters

**How to structure your answer:** change detection

**Model answer:** paths-ignore and dorny paths-filter.

**Common weak answers:** Accept cost

**Follow-up probes (with answers):**

**Q:** Deeper probe?
**A:** Owner, metric, prevention.

---
### S7. OIDC deploy works plan fails

**Situation:** Different permissions.

**What they're testing:** IAM least privilege

**How to structure your answer:** Role diff

**Model answer:** Align federated cred scopes.

**Common weak answers:** Owner subscription

**Follow-up probes (with answers):**

**Q:** Deeper probe?
**A:** Owner, metric, prevention.

---
### S8. Rollback blocked by schema

**Situation:** App rollback; DB forward only.

**What they're testing:** Expand/contract

**How to structure your answer:** Compatibility matrix

**Model answer:** Forward-fix app; never down Flyway prod.

**Common weak answers:** Restore DB backup

**Follow-up probes (with answers):**

**Q:** Deeper probe?
**A:** Owner, metric, prevention.

---
### S9. Self-hosted runner compromised

**Situation:** Malicious workflow on fork.

**What they're testing:** Fork PR policy

**How to structure your answer:** Approval, isolation

**Model answer:** Require approval; ephemeral runners; rotate.

**Common weak answers:** Trust all forks

**Follow-up probes (with answers):**

**Q:** Deeper probe?
**A:** Owner, metric, prevention.

---
### S10. Senior pipeline story under pressure

**Situation:** Board asks why CI investment.

**What they're testing:** DORA narrative

**How to structure your answer:** STAR with metrics

**Model answer:** Lead time, CFR, MTTR before/after; one incident recovered.

**Common weak answers:** Buzzwords without numbers

**Follow-up probes (with answers):**

**Q:** Deeper probe?
**A:** Owner, metric, prevention.

---
