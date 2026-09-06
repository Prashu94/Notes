# CI/CD — Practical Exercises

Type these. Run them. Break them. A green pipeline on Friday is worthless if rollback is a prayer.

**Structure:** Part A (Basic) · Part B (Intermediate) · Part C (Hard) · Weekend challenge  
**33 exercises** — full solutions with GitHub Actions YAML, pipeline stages, and runbook snippets.

---

# Part A — Basic (10)

---

## Exercise A1 — Minimal GitHub Actions for Spring

**Task:** Create a CI workflow that builds and tests a Maven Spring Boot service on every PR and push to `main`. Add a failing test; prove the PR goes red.

**Solution — pipeline stages:**

| Stage | Purpose |
|-------|---------|
| Checkout | Pin source to commit SHA |
| Setup JDK 21 | Temurin + Maven cache |
| Verify | `mvn -B verify` (compile + unit + integration) |
| (optional) Fail gate | Deliberately break a test to see red |

```yaml
name: ci-order-service
on:
  pull_request:
    paths: ['services/order-service/**', '.github/workflows/order-service.yml']
  push:
    branches: [main]
    paths: ['services/order-service/**']

jobs:
  build-test:
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Java 21
        uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: '21'
          cache: maven

      - name: Build and test
        working-directory: services/order-service
        run: ./mvnw -B verify -DskipITs=false

      - name: Publish test report (on failure)
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: surefire-reports
          path: services/order-service/target/surefire-reports/
```

**Senior takeaway:** Path filters prevent 15 microservices from rebuilding on a README change. `verify` not `package` — integration tests must run in CI.

---

## Exercise A2 — Maven cache and reproducible builds

**Task:** Prove the second CI run is faster. Document what is *not* cached (Docker layers, `~/.m2` local-only deps).

**Solution:**

```yaml
      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: '21'
          cache: maven   # caches ~/.m2/repository keyed by pom hash

      - name: Enforce reproducible build
        run: ./mvnw -B -ntp verify   # -ntp = no transfer progress noise
```

Add `maven-wrapper.properties` and commit `mvnw`. Pin plugin versions in parent POM — floating `LATEST` breaks reproducibility.

**Verify:** Compare job duration run 1 vs run 2 in Actions UI. Cache miss on `pom.xml` change is expected.

---

## Exercise A3 — Unit vs integration test split

**Task:** Run unit tests in every job; integration tests (Testcontainers) only on `main` and nightly — or always, but with a profile. Show the Maven command.

**Solution:**

```yaml
      - name: Unit tests only (fast PR feedback)
        if: github.event_name == 'pull_request'
        run: ./mvnw -B test -Punit

      - name: Full verify including ITs
        if: github.event_name != 'pull_request' || contains(github.event.pull_request.labels.*.name, 'run-its')
        run: ./mvnw -B verify -Pintegration
```

`pom.xml` profiles:

```xml
<profile>
  <id>unit</id>
  <build>
    <plugins>
      <plugin>
        <artifactId>maven-surefire-plugin</artifactId>
        <configuration>
          <excludedGroups>integration</excludedGroups>
        </configuration>
      </plugin>
    </plugins>
  </build>
</profile>
```

**Senior takeaway:** PR speed vs coverage trade-off. Document the `run-its` label in CONTRIBUTING.md.

---

## Exercise A4 — Dockerfile build in CI

**Task:** Multi-stage Dockerfile for Spring Boot. Build image in CI; do not push yet.

**Solution — Dockerfile:**

```dockerfile
# syntax=docker/dockerfile:1
FROM eclipse-temurin:21-jdk-alpine AS build
WORKDIR /app
COPY mvnw pom.xml ./
COPY .mvn .mvn
RUN ./mvnw -B -ntp dependency:go-offline
COPY src ./src
RUN ./mvnw -B -ntp package -DskipTests

FROM eclipse-temurin:21-jre-alpine
RUN addgroup -S app && adduser -S app -G app
USER app
WORKDIR /app
COPY --from=build /app/target/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-XX:+UseContainerSupport", "-jar", "app.jar"]
```

**CI step:**

```yaml
      - name: Build image
        run: |
          docker build -t order-service:ci-${{ github.sha }} \
            -f services/order-service/Dockerfile \
            services/order-service
      - name: Smoke-run container
        run: |
          docker run -d --name order -p 8080:8080 order-service:ci-${{ github.sha }}
          sleep 15
          curl -fsS http://localhost:8080/actuator/health | jq -e '.status=="UP"'
          docker stop order
```

---

## Exercise A5 — Trivy filesystem scan gate

**Task:** Fail CI if CRITICAL vulnerabilities exist in dependencies or base image layers.

**Solution:**

```yaml
      - name: Trivy FS scan (dependencies + Dockerfile)
        uses: aquasecurity/trivy-action@0.28.0
        with:
          scan-type: fs
          scan-ref: services/order-service
          severity: CRITICAL,HIGH
          exit-code: 1
          ignore-unfixed: true

      - name: Trivy image scan (after build)
        uses: aquasecurity/trivy-action@0.28.0
        with:
          image-ref: order-service:ci-${{ github.sha }}
          severity: CRITICAL
          exit-code: 1
```

Maintain `.trivyignore` with ticket references — never silent ignores.

**Senior takeaway:** FS scan catches bad `pom.xml` before image build. Image scan catches base image CVEs.

---

## Exercise A6 — Branch protection mental model

**Task:** Write the branch protection rules for `main` as a checklist (no YAML — this is GitHub settings). Explain what each rule prevents.

**Solution checklist:**

| Rule | Prevents |
|------|----------|
| Require PR before merge | Direct push bypassing review |
| Require 1+ approvals | Single-author mistakes |
| Require status checks: `build-test` | Merging red CI |
| Require linear history | Unreviewable merge-commit soup |
| Do not allow bypass for admins | "I'm senior" hotfix culture |
| Require signed commits (optional) | Impersonation / supply chain |

**Exercise:** Attempt `git push origin main` with failing test — should be rejected if checks required.

---

## Exercise A7 — Semantic versioning of artifacts

**Task:** Tag releases `v1.2.3` from `main`. CI publishes JAR + image with both git SHA and semver tag.

**Solution:**

```yaml
on:
  push:
    tags: ['v*.*.*']

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Extract version
        id: ver
        run: echo "VERSION=${GITHUB_REF_NAME#v}" >> $GITHUB_OUTPUT
      - run: ./mvnw -B verify -Drevision=${{ steps.ver.outputs.VERSION }}
      - run: |
          docker build -t acr.azurecr.io/order-service:${{ steps.ver.outputs.VERSION }} .
          docker build -t acr.azurecr.io/order-service:${{ github.sha }} .
```

**Rule:** Prod deploys reference **digest** or immutable semver — never floating `latest`.

---

## Exercise A8 — Environment variables and secrets in CI

**Task:** Use GitHub Encrypted Secrets for `SONAR_TOKEN`. Never echo secrets. Show correct vs wrong pattern.

**Solution — correct:**

```yaml
      - name: SonarQube scan
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
        run: ./mvnw -B sonar:sonar -Dsonar.login=$SONAR_TOKEN
```

**Wrong:** `run: echo ${{ secrets.SONAR_TOKEN }}` — logs leak.  
**Wrong:** Commit `.env` with real tokens.

**OIDC preview (no long-lived cloud secret):**

```yaml
permissions:
  id-token: write
  contents: read
```

Used fully in Exercise B6.

---

## Exercise A9 — Test report and failure artifacts

**Task:** On failure, upload Surefire XML + JaCoCo HTML. On success, optional coverage comment on PR.

**Solution:**

```yaml
      - name: JaCoCo report
        run: ./mvnw -B verify jacoco:report

      - name: Upload coverage
        uses: actions/upload-artifact@v4
        with:
          name: jacoco-report
          path: target/site/jacoco/

      - name: Coverage comment (optional)
        if: github.event_name == 'pull_request'
        uses: madrapps/jacoco-report@v1.6
        with:
          paths: target/site/jacoco/jacoco.xml
          token: ${{ secrets.GITHUB_TOKEN }}
```

---

## Exercise A10 — Pipeline stages diagram (write on paper)

**Task:** Draw the happy-path CI pipeline for one Spring service. Label inputs, outputs, and gates.

**Solution — stage flow:**

```text
[git push/PR]
    → checkout
    → compile
    → unit test ──────────────┐
    → integration test        │ gate: all green
    → SAST (SpotBugs/Sonar)   │
    → dependency scan (Trivy) ┘
    → build JAR
    → build Docker image
    → scan image
    → push to ACR (main only)
    → update GitOps repo / trigger CD
```

**Output artifact:** `acr.io/order-service@sha256:abc...` + Helm chart version.

---

# Part B — Intermediate (10)

---

## Exercise B1 — Build once, deploy many

**Task:** Two jobs: `build` publishes image with digest. `deploy-qa` and `deploy-prod` consume the **same** digest — only values differ.

**Solution:**

```yaml
name: build-and-promote
on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      image_digest: ${{ steps.push.outputs.digest }}
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: acr.azurecr.io
          username: ${{ secrets.ACR_USERNAME }}
          password: ${{ secrets.ACR_PASSWORD }}
      - id: meta
        run: echo "IMAGE=acr.azurecr.io/order-service" >> $GITHUB_ENV
      - name: Build and push
        id: push
        uses: docker/build-push-action@v6
        with:
          context: services/order-service
          push: true
          tags: ${{ env.IMAGE }}:${{ github.sha }}
      - name: Capture digest
        id: digest
        run: |
          DIGEST=$(docker inspect --format='{{index .RepoDigests 0}}' ${{ env.IMAGE }}:${{ github.sha }} | cut -d@ -f2)
          echo "digest=$DIGEST" >> $GITHUB_OUTPUT

  deploy-qa:
    needs: build
    runs-on: ubuntu-latest
    environment: qa
    steps:
      - uses: actions/checkout@v4
        with:
          repository: org/gitops-qa
          token: ${{ secrets.GITOPS_TOKEN }}
      - name: Patch image digest
        run: |
          yq -i '.image.digest = "${{ needs.build.outputs.image_digest }}"' apps/order/values.yaml
          git commit -am "deploy order ${{ github.sha }} to qa"
          git push

  deploy-prod:
    needs: [build, deploy-qa]
    runs-on: ubuntu-latest
    environment: production   # manual approval gate in GitHub
    steps:
      - uses: actions/checkout@v4
        with:
          repository: org/gitops-prod
          token: ${{ secrets.GITOPS_TOKEN }}
      - run: |
          yq -i '.image.digest = "${{ needs.build.outputs.image_digest }}"' apps/order/values.yaml
          git commit -am "deploy order ${{ github.sha }} to prod"
          git push
```

**Prove:** `docker inspect` digest identical in QA and prod — only `replicas`, `resources`, and `ingress.host` differ.

---

## Exercise B2 — Image digest pinning in Helm

**Task:** Helm values use `image.digest`, not `tag: latest`. Show values snippet + `helm upgrade` command.

**Solution — `values-prod.yaml`:**

```yaml
image:
  repository: acr.azurecr.io/order-service
  digest: sha256:4f53cda18c2baa0c035c4f8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8
  pullPolicy: IfNotPresent

replicas: 6
resources:
  requests: { cpu: 500m, memory: 512Mi }
  limits:   { cpu: 2000m, memory: 1Gi }
```

**Deploy:**

```bash
helm upgrade --install order ./charts/order \
  -f values-prod.yaml \
  --namespace orders \
  --atomic --timeout 10m \
  --wait
```

`--atomic`: if readiness fails, auto-rollback to previous revision.

---

## Exercise B3 — Expand/contract database migrations in pipeline

**Task:** Document a 4-PR Flyway sequence. Explain why one PR with `NOT NULL` + deploy is dangerous.

**Solution — PR sequence:**

| PR | Flyway | App code | Safe? |
|----|--------|----------|-------|
| PR1 | `ADD COLUMN status VARCHAR(20) NULL` | unchanged | ✅ |
| PR2 | App reads/writes `status` (default in code) | new field | ✅ |
| PR3 | Backfill job: `UPDATE orders SET status='PENDING' WHERE status IS NULL` | — | ✅ |
| PR4 | `ALTER COLUMN status SET NOT NULL` | remove default hack | ✅ |

**Dangerous single PR:** `NOT NULL` column + deploy before backfill → insert failures, downtime.

**Pipeline gate:**

```yaml
      - name: Flyway validate (no drift)
        run: ./mvnw -B flyway:validate -Dflyway.url=$DB_URL
```

Prod deploy order: migration job **before** app rollout (init container or separate Job).

---

## Exercise B4 — Deploy concurrency and blast radius

**Task:** Prevent overlapping prod deploys for `order-service`. Two pipelines queued — second waits.

**Solution:**

```yaml
concurrency:
  group: prod-order-service
  cancel-in-progress: false   # never kill an in-flight prod deploy

jobs:
  deploy-prod:
    environment: production
    # ...
```

**Alternative — Argo CD sync waves:** wave 0 = CRDs, wave 1 = migrations Job, wave 2 = Deployment.

**Runbook note:** If deploy hangs, check `kubectl rollout status` before starting manual rollback.

---

## Exercise B5 — OIDC federated login to Azure (no client secret)

**Task:** GitHub Actions authenticates to Azure via OIDC. List setup steps + workflow snippet.

**Solution — setup (one-time):**

1. Azure AD App Registration with federated credential:
   - Issuer: `https://token.actions.githubusercontent.com`
   - Subject: `repo:org/order-service:ref:refs/heads/main`
2. Grant `AcrPush` + `Contributor` on RG (scoped, not subscription-wide).
3. GitHub repo secret: only `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`.

```yaml
permissions:
  id-token: write
  contents: read

jobs:
  push-image:
    runs-on: ubuntu-latest
    steps:
      - uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      - run: az acr login --name myregistry
      - run: docker build -t myregistry.azurecr.io/order:${{ github.sha }} . && docker push ...
```

**Senior takeaway:** Rotating secrets becomes rotating federated credential config — no `AZURE_CLIENT_SECRET` in GitHub.

---

## Exercise B6 — OpenAPI contract gate

**Task:** CI fails if generated OpenAPI spec ≠ committed `openapi.yaml`.

**Solution:**

```yaml
      - name: Generate OpenAPI from Spring
        run: ./mvnw -B spring-boot:run -Dspring-boot.run.arguments="--springdoc.writer-with-order-by-keys=true" &
        sleep 30
        curl -fsS http://localhost:8080/v3/api-docs.yaml -o /tmp/generated.yaml
        kill %1

      - name: Contract drift check
        run: |
          cp src/main/resources/openapi.yaml /tmp/committed.yaml
          diff -u /tmp/committed.yaml /tmp/generated.yaml
          git diff --exit-code src/main/resources/openapi.yaml || \
            (echo "OpenAPI drift — run generator and commit" && exit 1)
```

**Better:** `springdoc-openapi-maven-plugin` in `verify` phase — no sleep hack.

---

## Exercise B7 — Post-deploy smoke test Job

**Task:** Helm post-install Job curls `/actuator/health`. Failure triggers `--atomic` rollback.

**Solution — `templates/smoke-job.yaml`:**

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: order-smoke-{{ .Release.Revision }}
  annotations:
    helm.sh/hook: post-upgrade
    helm.sh/hook-weight: "5"
    helm.sh/hook-delete-policy: before-hook-creation
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: curl
          image: curlimages/curl:8.5.0
          command:
            - sh
            - -c
            - |
              for i in $(seq 1 30); do
                if curl -fsS http://order-service.orders.svc:8080/actuator/health | jq -e '.status=="UP"'; then
                  exit 0
                fi
                sleep 5
              done
              exit 1
```

**CLI verify:**

```bash
curl -fsS https://qa.example.com/actuator/health | jq -e '.status=="UP"'
```

---

## Exercise B8 — Monorepo path filters

**Task:** Changing `services/payment/**` must not trigger `order-service` CI.

**Solution:**

```yaml
# .github/workflows/order-service.yml
on:
  pull_request:
    paths:
      - 'services/order-service/**'
      - '.github/workflows/order-service.yml'
      - 'pom.xml'                    # parent POM change may affect all
  push:
    branches: [main]
    paths:
      - 'services/order-service/**'
```

**Shared library change:** use `paths-filter` action to detect `libs/common/**` and fan out:

```yaml
      - uses: dorny/paths-filter@v3
        id: changes
        with:
          filters: |
            order: services/order-service/**
            payment: services/payment-service/**
            common: libs/common/**
```

---

## Exercise B9 — SonarQube quality gate

**Task:** Fail pipeline on new critical issues or coverage drop below 80% on new code.

**Solution:**

```yaml
      - name: SonarQube scan
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
        run: |
          ./mvnw -B verify sonar:sonar \
            -Dsonar.projectKey=order-service \
            -Dsonar.host.url=https://sonar.example.com \
            -Dsonar.qualitygate.wait=true \
            -Dsonar.coverage.jacoco.xmlReportPaths=target/site/jacoco/jacoco.xml
```

Tune quality gate in Sonar UI: **new code** coverage ≥ 80%, no new blocker/critical.

---

## Exercise B10 — Rollback runbook (one page)

**Task:** Write a production rollback runbook for `order-service`. Store in `docs/runbooks/order-rollback.md`.

**Solution — runbook template:**

```markdown
# order-service — Production Rollback

## Triggers
- Error rate > 5% for 5 min (PagerDuty: OrderAPIBurn)
- p99 latency > 2s sustained
- Smoke test failure post-deploy
- On-call judgment + EM approval

## Roles
- **IC:** on-call backend
- **Comms:** incident channel #inc-order
- **DB:** page DBA if migration involved

## Fast path (no schema change)
1. `helm history order -n orders` — note last GOOD revision
2. `helm rollback order <revision> -n orders --wait --timeout 10m`
3. Verify: `curl /actuator/health`, synthetic checkout test
4. Confirm image digest reverted: `kubectl get deploy order -o jsonpath='{.spec.template.spec.containers[0].image}'`

## GitOps path (Argo CD)
1. `git revert` the values commit that bumped digest
2. Argo sync (or wait auto-sync)
3. Confirm `Healthy` + `Synced`

## Database — CANNOT rollback
- If Flyway migration ran forward-only (column drop, NOT NULL), **do not** `flyway:undo` without DBA script
- Roll back **app only**; feature-flag new code paths off

## Communication
- Status page: "Checkout degraded — workaround: retry in 5 min"
- Post-incident: timeline, root cause, action items within 48h
```

---

# Part C — Hard (8)

---

## Exercise C1 — Full GitOps pipeline (Argo CD)

**Task:** Design CI + GitOps split. CI builds image; separate repo holds Helm values; Argo CD syncs AKS.

**Solution — architecture:**

```text
[order-service repo]          [gitops-prod repo]           [AKS]
  push main ──CI──► ACR         values.yaml ──► Argo CD ──► Deployment
                    digest pin     ▲
                                   └── PR + approval for prod
```

**Argo CD Application:**

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: order-prod
  namespace: argocd
spec:
  project: production
  source:
    repoURL: https://github.com/org/gitops-prod
    targetRevision: main
    path: apps/order
    helm:
      valueFiles: [values-prod.yaml]
  destination:
    server: https://kubernetes.default.svc
    namespace: orders
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

**CI job (image only):**

```yaml
      - name: Update GitOps (bot PR)
        uses: peter-evans/create-pull-request@v6
        with:
          token: ${{ secrets.GITOPS_TOKEN }}
          repository: org/gitops-prod
          branch: deploy/order-${{ github.sha }}
          title: "chore(order): deploy ${{ github.sha }}"
          body: |
            Image digest: ${{ steps.push.outputs.digest }}
            CI run: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}
          commit-message: "deploy order ${{ github.sha }}"
```

**Hard rule:** Never `kubectl set image` in CI **and** Argo auto-sync — fighting controllers.

---

## Exercise C2 — Blue/green or canary with Helm + Argo Rollouts

**Task:** Sketch canary: 10% → 50% → 100% with automatic rollback on 5xx rate.

**Solution — Argo Rollout snippet:**

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: order
spec:
  replicas: 10
  strategy:
    canary:
      steps:
        - setWeight: 10
        - pause: { duration: 5m }
        - setWeight: 50
        - pause: { duration: 5m }
        - setWeight: 100
      analysis:
        templates:
          - templateName: order-5xx-rate
        startingStep: 1
```

**Analysis template:** Prometheus query `rate(http_server_requests_seconds_count{status=~"5.."}[5m])` < threshold.

**Rollback:** `kubectl argo rollouts undo order` or failed analysis auto-reverts.

---

## Exercise C3 — Supply chain: SBOM + image signing

**Task:** Generate SBOM in CI; sign image with Cosign; verify in admission policy.

**Solution:**

```yaml
      - name: Generate SBOM
        uses: anchore/sbom-action@v0
        with:
          image: acr.azurecr.io/order-service:${{ github.sha }}
          format: cyclonedx-json
          output-file: sbom.cdx.json

      - name: Sign image
        env:
          COSIGN_EXPERIMENTAL: "1"
        run: |
          cosign sign --yes acr.azurecr.io/order-service@${{ steps.push.outputs.digest }}

      - name: Attach SBOM attestation
        run: |
          cosign attest --yes --predicate sbom.cdx.json \
            --type cyclonedx \
            acr.azurecr.io/order-service@${{ steps.push.outputs.digest }}
```

**Cluster policy (concept):** Kyverno / Ratify rejects unsigned images from `acr.azurecr.io`.

---

## Exercise C4 — DORA metrics from pipeline data

**Task:** Define how to measure deployment frequency, lead time, change failure rate, MTTR from GitHub + Argo + PagerDuty.

**Solution:**

| Metric | Source | Calculation |
|--------|--------|-------------|
| Deployment frequency | Argo CD sync events / prod deploy workflow | deploys per week |
| Lead time for changes | PR opened → prod deploy timestamp | median hours |
| Change failure rate | deploys causing incident / total deploys | % per month |
| MTTR | PagerDuty resolved − triggered | median minutes |

**Instrumentation:**

```yaml
      - name: Record deploy event
        if: success()
        run: |
          curl -X POST ${{ secrets.DORA_WEBHOOK }} \
            -d "{\"service\":\"order\",\"sha\":\"${{ github.sha }}\",\"env\":\"prod\",\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}"
```

Interview answer: "We moved CFR from 18% to 6% by digest pinning + smoke hooks + mandatory canary."

---

## Exercise C5 — Disaster recovery pipeline drill

**Task:** Primary ACR region down. Failover pulls from geo-replicated registry. Document pipeline changes.

**Solution:**

```text
Primary:   acr-east.azurecr.io/order@sha256:abc
Replica:   acr-west.azurecr.io/order@sha256:abc  (same digest after geo-replication)

Pipeline fallback:
  1. CI still pushes to primary
  2. If primary push fails, retry replica endpoint
  3. GitOps values reference digest — region-agnostic
  4. AKS west cluster pulls from acr-west (firewall rules pre-staged)
```

**Drill script (quarterly):**

1. Block primary ACR in test network
2. Deploy to DR cluster using replica digest
3. Run smoke + synthetic transaction
4. Time the failover — target RTO < 60 min

---

## Exercise C6 — Multi-service coordinated release

**Task:** `order-service` v2 requires `payment-service` v2 (new Kafka schema). Design pipeline coordination.

**Solution:**

```text
Phase 1 — backward compatible
  - payment v2 deploys (consumes old + new events)
  - order v1 still live

Phase 2 — order v2 deploys (publishes new schema)
  - feature flag: dual-write disabled after cutover

Phase 3 — payment v1 decommission
```

**Pipeline:**

```yaml
# orchestrator workflow
jobs:
  deploy-payment:
    # ...
  deploy-order:
    needs: deploy-payment
    # ...
```

**Kafka:** Schema Registry `BACKWARD` compatibility check in CI:

```bash
mvn schema-registry:validate -Dcompatibility=BACKWARD
```

Never deploy producer before consumer can read new schema.

---

## Exercise C7 — Secrets rotation without downtime

**Task:** Rotate `order-service` DB password stored in Azure Key Vault. Zero-downtime steps.

**Solution:**

```text
1. Key Vault: create password-v2 secret version
2. External Secrets Operator syncs to K8s Secret (two keys temporarily)
3. Rolling restart Deployment — new pods pick up v2
4. Azure SQL: alter login to v2 password
5. Revoke v1 secret version
6. CI never holds DB password — only workload identity to Key Vault
```

**ExternalSecret:**

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: order-db
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: azure-kv
    kind: ClusterSecretStore
  target:
    name: order-db-credentials
  data:
    - secretKey: password
      remoteRef:
        key: order-db-password
```

---

## Exercise C8 — Pipeline security: poisoned PR attack

**Task:** A PR modifies `.github/workflows/ci.yml` to exfiltrate secrets. Design protections.

**Solution — defenses:**

| Control | Effect |
|---------|--------|
| Require approval for fork PR workflows | Blocks secret access on first run |
| `pull_request_target` ban in team policy | Prevents privilege escalation pattern |
| CODEOWNERS on `.github/**` | Platform team must approve |
| OIDC scoped to `environment:production` | Stolen token cannot push prod |
| Branch protection: no bypass | Admins cannot merge malicious workflow |

**Detection:**

```yaml
      - name: Workflow lint
        run: |
          actionlint .github/workflows/*.yml
          # reject curl to unknown hosts in workflow files
```

**Incident response:** Rotate all secrets touched since merge; audit `gh api repos/org/repo/actions/runs`.

---

# Weekend challenge

**Goal:** End-to-end mini platform in 4 hours.

1. **Hour 1 — CI:** Spring Boot `order-service` with GitHub Actions: `verify`, Trivy, Docker build, push to local registry (or ACR trial).
2. **Hour 2 — GitOps:** Second repo with Helm chart; pin image digest; install Argo CD locally (minikube/kind) or simulate with `helm upgrade`.
3. **Hour 3 — Gates:** Add Flyway expand/contract exercise on H2; post-deploy smoke Job; break prod intentionally; execute `helm rollback`.
4. **Hour 4 — Runbook:** Write rollback runbook; run OIDC sketch on paper; list 3 ways your pipeline could leak secrets and how you prevented each.

**Deliverables:** Two git repos (or folders), one successful deploy + one successful rollback, runbook in `docs/runbooks/`.

**Self-score checklist:**

- [ ] Image referenced by digest in prod values
- [ ] No `latest` tag in any prod path
- [ ] Migrations run before app pods
- [ ] Rollback tested, not theoretical
- [ ] Can explain CI vs CD vs GitOps in 90 seconds


### Exercise 29 — GitHub Environment protection

**Task:** Add `environment: production` job requiring reviewers (document YAML).

**Solution:**

```yaml
jobs:
  deploy-prod:
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://orders.example.com
    steps:
      - run: echo "deploy with approval gate"
```

**Expected output:** First run waits for configured reviewer approval in repo Settings → Environments.

---

### Exercise 30 — Path filter with dorny/paths-filter

**Task:** Skip CI when only `docs/**` changes.

**Solution:**

```yaml
jobs:
  changes:
    runs-on: ubuntu-latest
    outputs:
      app: ${{ steps.f.outputs.app }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v3
        id: f
        with:
          filters: |
            app:
              - 'services/**'
              - '.github/workflows/**'
  build:
    needs: changes
    if: needs.changes.outputs.app == 'true'
    runs-on: ubuntu-latest
    steps:
      - run: ./mvnw -B verify
```

**Expected output:** Docs-only PR skips build job.

---

### Exercise 31 — SLSA provenance generation (sketch)

**Task:** Add provenance attestation step on release workflow.

**Solution:**

```yaml
      - uses: slsa-framework/slsa-github-generator/.github/workflows/generator_container_slsa3.yml@v2.0.0
        with:
          image-name: ${{ env.IMAGE }}
          digest: ${{ steps.build.outputs.digest }}
```

**Expected output:** Release attaches provenance artifact verifiable with `slsa-verifier`.

---

### Exercise 32 — Deployment freeze workflow rule

**Task:** Block prod deploy Dec 24–26 via workflow condition.

**Solution:**

```yaml
jobs:
  deploy-prod:
    if: |
      !(
        github.event_name == 'push' &&
        contains(fromJSON('["12-24","12-25","12-26"]'), format('{0}-{1}', github.event.repository.updated_at))
      )
    environment: production
```

**Expected output:** Document calendar-based freeze; prefer organization-level freeze window API or manual environment lock for production realism.

---

### Exercise 33 — Pipeline failure taxonomy dashboard

**Task:** Define CSV schema and 5 sample rows classifying CI failures.

**Solution:**

```csv
run_id,repo,stage,failure_class,owner,mttr_minutes,root_cause
991,order-service,integration,flake,team-orders,12,Testcontainers race
992,platform,deploy,infra,team-platform,38,Runner disk full
993,payments,scan,quality_gate,security,144,CVE-2024-xxx triage
994,inventory,unit,test,team-inv,5,Assertion on new API
995,orders,smoke,deploy,team-orders,22,Bad config map post-deploy
```

**Expected output:** Quarterly review reduces flake MTTR with quarantine policy per class.


---

## Stats

| Section | Count |
|---------|------:|
| Part A — Basic | 12 |
| Part B — Intermediate | 12 |
| Part C — Hard | 9 |
| **Total** | **33** |
