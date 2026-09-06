# Helm / Kubernetes — Practical Exercises

Use a local cluster (kind/minikube) or AKS dev. Type the commands; read the events when things break.

**Structure:** Part A (Basic) · Part B (Intermediate) · Part C (Hard) — 33 exercises total.

---

## Part A — Basic (10)

### Exercise A1 — Create a chart scaffold

**Task:** `helm create order-service` and inspect generated templates.

**Solution:**

```bash
helm create order-service
tree order-service/templates
```

**Expected output:**

```
order-service/templates/
├── NOTES.txt
├── deployment.yaml
├── hpa.yaml
├── ingress.yaml
├── service.yaml
├── serviceaccount.yaml
└── tests/test-connection.yaml
```

---

### Exercise A2 — Install a release

**Task:** Install `order-service` release v0.1.0 into namespace `orders`.

**Solution:**

```bash
kubectl create namespace orders
helm install order-svc ./order-service -n orders \
  --set image.repository=ghcr.io/demo/order-service \
  --set image.tag=0.1.0
```

**Expected output:**

```
NAME: order-svc
LAST DEPLOYED: Sat Sep  5 14:00:00 2026
NAMESPACE: orders
STATUS: deployed
REVISION: 1
```

---

### Exercise A3 — List releases and status

**Task:** Show all releases and detailed status for `order-svc`.

**Solution:**

```bash
helm list -A
helm status order-svc -n orders
```

**Expected output:**

```
NAME       NAMESPACE  REVISION  STATUS   CHART
order-svc  orders     1         deployed order-service-0.1.0
```

```
RESOURCES:
==> v1/Deployment
NAME         READY   UP-TO-DATE   AVAILABLE
order-svc    1/1     1            1
```

---

### Exercise A4 — kubectl pod basics

**Task:** After install, get pods, describe one, read logs.

**Solution:**

```bash
kubectl get pods -n orders -o wide
kubectl describe pod -n orders -l app.kubernetes.io/instance=order-svc
kubectl logs -n orders -l app.kubernetes.io/instance=order-svc --tail=50
```

**Expected output:**

```
NAME                         READY   STATUS    RESTARTS   AGE   IP           NODE
order-svc-6f9c8d7b5d-abcde   1/1     Running   0          2m    10.244.1.5   kind-worker
```

```
Started container order-service
Tomcat started on port 8080
```

---

### Exercise A5 — Override values on install

**Task:** Set `replicaCount: 3` and `service.port: 8080` via CLI.

**Solution:**

```bash
helm upgrade --install order-svc ./order-service -n orders \
  --set replicaCount=3 \
  --set service.port=8080
kubectl get deploy order-svc -n orders -o jsonpath='{.spec.replicas}{"\n"}'
```

**Expected output:**

```
3
```

---

### Exercise A6 — Liveness probe

**Task:** Add HTTP liveness on `/actuator/health/liveness`.

**Solution:**

```yaml
# values.yaml
livenessProbe:
  httpGet:
    path: /actuator/health/liveness
    port: http
  initialDelaySeconds: 30
  periodSeconds: 10
```

```bash
helm upgrade order-svc ./order-service -n orders
kubectl describe pod -n orders -l app.kubernetes.io/instance=order-svc | grep -A6 Liveness
```

**Expected output:**

```
Liveness:   http-get http://:8080/actuator/health/liveness delay=30s timeout=1s period=10s
```

---

### Exercise A7 — Readiness probe

**Task:** Readiness on `/actuator/health/readiness` so Service skips not-ready pods.

**Solution:**

```yaml
readinessProbe:
  httpGet:
    path: /actuator/health/readiness
    port: http
  initialDelaySeconds: 20
  periodSeconds: 5
```

```bash
helm upgrade order-svc ./order-service -n orders
kubectl get endpoints -n orders order-svc -o yaml
```

**Expected output:** Endpoints list only pod IPs that pass readiness (empty during slow Spring start).

---

### Exercise A8 — Service + port-forward smoke test

**Task:** Expose port 80 → 8080; curl via port-forward.

**Solution:**

```bash
kubectl port-forward -n orders svc/order-svc 8080:80 &
sleep 2
curl -s http://localhost:8080/actuator/health | jq .
```

**Expected output:**

```json
{
  "status": "UP"
}
```

---

### Exercise A9 — ConfigMap from values

**Task:** Mount `application.yaml` snippet from ConfigMap template.

**Solution:**

```yaml
# templates/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ include "order-service.fullname" . }}-config
data:
  application.yaml: |
    server:
      port: {{ .Values.service.port }}
    logging:
      level:
        root: {{ .Values.logLevel }}
```

```yaml
# deployment volumeMount
volumeMounts:
  - name: config
    mountPath: /config
    readOnly: true
volumes:
  - name: config
    configMap:
      name: {{ include "order-service.fullname" . }}-config
```

```bash
helm template order-svc ./order-service --set logLevel=DEBUG | grep -A3 "logLevel"
```

**Expected output:**

```
level:
  root: DEBUG
```

---

### Exercise A10 — Uninstall a release

**Task:** Remove release but keep namespace.

**Solution:**

```bash
helm uninstall order-svc -n orders
kubectl get all -n orders
```

**Expected output:**

```
release "order-svc" uninstalled
```

```
No resources found in orders namespace.
```

---

## Part B — Intermediate (10)

### Exercise B1 — Render and validate a Spring chart

**Task:** Template with prod values; validate with kubeconform. Add `values.schema.json` requiring `image.tag`.

**Solution:**

```bash
helm template order-svc ./order-service -f values-prod.yaml > /tmp/out.yaml
kubeconform -summary /tmp/out.yaml
```

```json
// values.schema.json
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "required": ["image"],
  "properties": {
    "image": {
      "type": "object",
      "required": ["repository", "tag"],
      "properties": {
        "repository": { "type": "string" },
        "tag": { "type": "string", "minLength": 1 }
      }
    }
  }
}
```

```bash
helm install test ./order-service --set image.tag= -n orders  # should fail schema
```

**Expected output:**

```
Error: values don't meet the specifications of the schema(s) ...
```

---

### Exercise B2 — Checksum annotation forces rollout

**Task:** Pod template annotation hashes ConfigMap; changing CM rolls pods.

**Solution:**

```yaml
# templates/deployment.yaml
metadata:
  annotations:
    checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
```

```bash
kubectl get rs -n orders -o wide
helm upgrade order-svc ./order-service -n orders --set logLevel=INFO
kubectl get rs -n orders -o wide   # new ReplicaSet
```

**Expected output:** New ReplicaSet with revision; old pods terminated; only one RS has `DESIRED > 0`.

---

### Exercise B3 — Startup probe for slow JVM

**Task:** JVM takes 90 s to start. Use startupProbe so liveness does not kill the pod.

**Solution:**

```yaml
startupProbe:
  httpGet:
    path: /actuator/health/liveness
    port: http
  failureThreshold: 30
  periodSeconds: 5
livenessProbe:
  httpGet:
    path: /actuator/health/liveness
    port: http
  periodSeconds: 10
```

```bash
# Simulate slow start in Spring:
# @Bean ApplicationRunner r = args -> Thread.sleep(120_000);
kubectl describe pod -n orders -l app.kubernetes.io/instance=order-svc | grep -E 'Startup|Liveness'
```

**Expected output:** Pod stays `Running`; events show startup probe failures but **no** liveness kill before app is up.

---

### Exercise B4 — Memory limits and JVM MaxRAMPercentage

**Task:** Pod limit 1 Gi; set `JAVA_TOOL_OPTIONS`; explain non-heap headroom.

**Solution:**

```yaml
resources:
  limits:
    memory: 1Gi
  requests:
    memory: 512Mi
env:
  - name: JAVA_TOOL_OPTIONS
    value: "-XX:MaxRAMPercentage=75.0"
```

```bash
kubectl exec -n orders deploy/order-svc -- printenv JAVA_TOOL_OPTIONS
kubectl top pod -n orders
```

**Expected output:**

```
-XX:MaxRAMPercentage=75.0
```

Heap ~750 Mi; remaining ~250 Mi for metaspace, threads, direct buffers, native libs.

**OOM drill:**

```java
byte[] leak = new byte[900 * 1024 * 1024]; // force OOMKilled
```

```bash
kubectl describe pod -n orders ... | grep -i oom
```

```
Last State: Terminated
Reason: OOMKilled
```

---

### Exercise B5 — Helm rollback

**Task:** Upgrade to bad image tag; rollback to revision 1.

**Solution:**

```bash
helm upgrade --install order-svc ./order-service -n orders --set image.tag=1.0.0-good
helm upgrade order-svc ./order-service -n orders --set image.tag=9.9.9-bad
kubectl get pods -n orders   # ImagePullBackOff or CrashLoop
helm history order-svc -n orders
helm rollback order-svc 1 -n orders
kubectl rollout status deployment/order-svc -n orders
```

**Expected output:**

```
REVISION  STATUS     CHART              DESCRIPTION
1         superseded order-service-0.1.0 Install complete
2         superseded order-service-0.1.0 Upgrade complete
3         deployed   order-service-0.1.0 Rollback to 1
```

Pods return to `1.0.0-good` image.

---

### Exercise B6 — Pre-upgrade Helm hook Job

**Task:** Run `echo migrate` as pre-upgrade hook; argue CI migration is safer.

**Solution:**

```yaml
# templates/migrate-job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ include "order-service.fullname" . }}-migrate
  annotations:
    "helm.sh/hook": pre-upgrade
    "helm.sh/hook-delete-policy": before-hook-creation,hook-succeeded
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: migrate
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          command: ["sh", "-c", "echo migrate && flyway migrate"]
```

```bash
helm upgrade order-svc ./order-service -n orders
kubectl get jobs -n orders
```

**Expected output:**

```
order-svc-migrate   Complete   1/1   10s
```

**Interview comment:** CI pipeline Job with pinned Flyway image + reviewed SQL is safer than cluster hook sharing app image — hooks run with prod credentials on every `helm upgrade`, including `helm rollback` surprises.

---

### Exercise B7 — Debug CrashLoopBackOff (wrong JDBC URL)

**Task:** Pod crashes on bad `SPRING_DATASOURCE_URL`. RCA with kubectl only.

**Solution:**

```bash
kubectl get pods -n orders
kubectl describe pod -n orders order-svc-xxx
kubectl logs -n orders order-svc-xxx --previous
kubectl logs -n orders order-svc-xxx
kubectl get secret -n orders -o yaml
```

**Expected output (logs):**

```
Caused by: org.postgresql.util.PSQLException: Connection to wrong-host:5432 refused
```

**RCA:** Typo `wrong-host` in Secret `order-svc-db` mounted as env. Fix Secret + `helm upgrade` or `kubectl rollout restart`.

---

### Exercise B8 — PDB blocks node drain

**Task:** 2 replicas, PDB `minAvailable: 2`. Observe drain blocked; fix to `minAvailable: 1`.

**Solution:**

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: order-svc-pdb
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app.kubernetes.io/instance: order-svc
```

```bash
kubectl drain kind-worker --ignore-daemonsets --delete-emptydir-data
```

**Expected output:**

```
error when evicting pods/"order-svc-..." - cannot evict as it would violate PDB
```

After `minAvailable: 1`:

```bash
kubectl drain kind-worker --ignore-daemonsets --delete-emptydir-data
```

```
evicting pod order-svc-...
node/kind-worker drained
```

---

### Exercise B9 — Non-root container + securityContext

**Task:** Dockerfile `USER 65532`; match Helm `securityContext`.

**Solution:**

```dockerfile
FROM eclipse-temurin:21-jre
USER 65532
COPY --chown=65532:65532 app.jar /app.jar
ENTRYPOINT ["java","-jar","/app.jar"]
```

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 65532
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
```

```bash
kubectl exec -n orders deploy/order-svc -- id
```

**Expected output:**

```
uid=65532 gid=65532 groups=65532
```

---

### Exercise B10 — helm diff before upgrade

**Task:** Install diff plugin; preview changes in fake PR.

**Solution:**

```bash
helm plugin install https://github.com/databahn/helm-diff
helm diff upgrade order-svc ./order-service -n orders \
  --set image.tag=1.1.0 \
  --set replicaCount=3
```

**Expected output:**

```
orders, order-svc, Deployment (apps) has changed:
  spec.replicas: 1 -> 3
  spec.template.spec.containers[0].image: ...:1.0.0 -> ...:1.1.0
```

Paste into PR: "Bumps image to 1.1.0, scales to 3 replicas."

---

## Part C — Hard (8)

### Exercise C1 — Subchart dependency (PostgreSQL)

**Task:** Add Bitnami PostgreSQL as chart dependency; wire JDBC URL via values.

**Solution:**

```yaml
# Chart.yaml
dependencies:
  - name: postgresql
    version: 15.x.x
    repository: https://charts.bitnami.com/bitnami
```

```bash
helm dependency update ./order-service
```

```yaml
# values.yaml
postgresql:
  auth:
    username: order
    password: devonly
    database: orders
spring:
  datasource:
    url: jdbc:postgresql://{{ .Release.Name }}-postgresql:5432/orders
```

```bash
helm upgrade --install order-svc ./order-service -n orders
kubectl get pods -n orders
```

**Expected output:**

```
order-svc-postgresql-0   1/1   Running
order-svc-...            1/1   Running
```

---

### Exercise C2 — HPA on CPU

**Task:** HPA scales 1–5 on CPU 70%; load test with `hey`.

**Solution:**

```yaml
autoscaling:
  enabled: true
  minReplicas: 1
  maxReplicas: 5
  targetCPUUtilizationPercentage: 70
```

```bash
helm upgrade order-svc ./order-service -n orders
kubectl get hpa -n orders -w
hey -z 60s -c 50 http://localhost:8080/api/orders   # via port-forward
```

**Expected output:**

```
NAME        REFERENCE              TARGETS   MINPODS   MAXPODS   REPLICAS
order-svc   Deployment/order-svc   85%/70%   1         5         4
```

---

### Exercise C3 — Canary with two releases

**Task:** `order-svc-stable` 90%, `order-svc-canary` 10% via separate releases + Ingress weights (nginx).

**Solution:**

```bash
helm upgrade --install order-svc-stable ./order-service -n orders \
  --set fullnameOverride=order-stable --set image.tag=2.0.0
helm upgrade --install order-svc-canary ./order-service -n orders \
  --set fullnameOverride=order-canary --set image.tag=2.1.0-canary \
  --set replicaCount=1
```

```yaml
# ingress annotations
nginx.ingress.kubernetes.io/canary: "true"
nginx.ingress.kubernetes.io/canary-weight: "10"
```

**Expected output:** ~10% of requests hit canary (`X-Version: 2.1.0` header); 90% stable.

---

### Exercise C4 — values.schema.json + required prod keys

**Task:** Reject prod install without `resources.limits` and `image.tag`.

**Solution:**

```json
{
  "allOf": [
    {
      "if": { "properties": { "environment": { "const": "prod" } } },
      "then": {
        "required": ["resources"],
        "properties": {
          "resources": {
            "required": ["limits"],
            "properties": {
              "limits": { "required": ["memory", "cpu"] }
            }
          }
        }
      }
    }
  ]
}
```

```bash
helm install order-svc ./order-service -f values-prod.yaml -n orders
# missing limits → fail
```

**Expected output:**

```
Error: values don't meet the specifications of the schema
```

---

### Exercise C5 — Secret rotation without downtime

**Task:** Rolling restart after External Secrets Operator syncs new DB password.

**Solution:**

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: order-svc-db
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: azure-kv
    kind: ClusterSecretStore
  target:
    name: order-svc-db
    creationPolicy: Owner
  data:
    - secretKey: password
      remoteRef:
        key: db-password
```

```bash
# After KV secret version bumped:
kubectl annotate externalsecret order-svc-db force-sync=$(date +%s) -n orders
kubectl rollout restart deployment/order-svc -n orders
kubectl rollout status deployment/order-svc -n orders
```

**Expected output:** `Successfully rolled out`; zero `FailedMount` events; old pods terminate only after new ones Ready.

---

### Exercise C6 — NetworkPolicy deny-all egress except DNS + DB

**Task:** Default deny egress; allow DNS and PostgreSQL 5432.

**Solution:**

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: order-svc-egress
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/instance: order-svc
  policyTypes: [Egress]
  egress:
    - to:
        - namespaceSelector: {}
          podSelector:
            matchLabels:
              k8s-app: kube-dns
      ports:
        - protocol: UDP
          port: 53
    - to:
        - podSelector:
            matchLabels:
              app.kubernetes.io/name: postgresql
      ports:
        - protocol: TCP
          port: 5432
```

```bash
kubectl exec -n orders deploy/order-svc -- curl -m 3 https://google.com
```

**Expected output:**

```
curl: (28) Connection timed out
```

App still connects to DB; external HTTP blocked.

---

### Exercise C7 — OOMKilled + limits tuning RCA

**Task:** Pod restarted with `OOMKilled`. Read events, adjust heap or limits.

**Solution:**

```bash
kubectl get pod -n orders -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.containerStatuses[0].lastState.terminated.reason}{"\n"}{end}'
kubectl describe pod -n orders order-svc-xxx | grep -A3 "Last State"
```

**Expected output:**

```
Reason: OOMKilled
Exit Code: 137
```

**Fix:** Raise limit to `1536Mi` OR lower `MaxRAMPercentage` to `65.0` OR fix direct-memory leak.

```bash
helm upgrade order-svc ./order-service -n orders --set resources.limits.memory=1536Mi
```

---

### Exercise C8 — Multi-env values layering

**Task:** Base `values.yaml` + `values-qa.yaml` + `values-prod.yaml`; single command per env.

**Solution:**

```bash
# dev
helm upgrade --install order-svc ./order-service -n orders-dev \
  -f values.yaml

# qa
helm upgrade --install order-svc ./order-service -n orders-qa \
  -f values.yaml -f values-qa.yaml

# prod
helm upgrade --install order-svc ./order-service -n orders-prod \
  -f values.yaml -f values-qa.yaml -f values-prod.yaml \
  --atomic --timeout 10m
```

```yaml
# values-prod.yaml
replicaCount: 3
environment: prod
image:
  tag: 2.0.0
resources:
  limits:
    cpu: "2"
    memory: 2Gi
```

**Expected output:**

```bash
helm get values order-svc -n orders-prod
```

```
USER-SUPPLIED VALUES:
environment: prod
replicaCount: 3
```

Prod deploy rolls back automatically on failed readiness (`--atomic`).

---


### Exercise A29 — Gateway API HTTPRoute via Helm

**Task:** Install Gateway API CRDs and an `HTTPRoute` chart that routes `orders.example.com/cancel` to `order-svc` ClusterIP on port 8080.

**Solution:**

```bash
helm install gateway-api-crds oci://ghcr.io/kubernetes-sigs/gateway-api/charts/gateway-api-crds --version v1.2.0
```

```yaml
# charts/order-gateway/templates/gateway.yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: {{ include "order-gateway.fullname" . }}
spec:
  gatewayClassName: {{ .Values.gatewayClassName }}
  listeners:
    - name: https
      protocol: HTTP
      port: 80
      hostname: {{ .Values.hostname }}
---
# charts/order-gateway/templates/httproute.yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: order-cancel
spec:
  parentRefs:
    - name: {{ include "order-gateway.fullname" . }}
  hostnames:
    - {{ .Values.hostname | quote }}
  rules:
    - matches:
        - path:
            type: PathPrefix
            value: /cancel
      backendRefs:
        - name: order-svc
          port: {{ .Values.service.port }}
```

```yaml
# values.yaml
gatewayClassName: nginx
hostname: orders.example.com
service:
  port: 8080
```

```bash
helm upgrade --install order-gateway ./charts/order-gateway -n orders
kubectl get httproute,gateway -n orders
curl -H "Host: orders.example.com" http://<gateway-ip>/cancel/ORD-1
```

**Expected output:**

```
NAME          HOSTNAMES               AGE
order-cancel  ["orders.example.com"]  1m
```

```
HTTP/1.1 200 OK
```

**Senior takeaway:** Gateway API separates **route** (HTTPRoute) from **implementation** (GatewayClass) — Helm charts should not hard-code Ingress annotations per cloud.

---

### Exercise A30 — cert-manager TLS for Gateway

**Task:** Helm-install cert-manager; issue a Let's Encrypt certificate via `ClusterIssuer` and attach to Gateway listener using `certificateRefs`.

**Solution:**

```bash
helm repo add jetstack https://charts.jetstack.io
helm upgrade --install cert-manager jetstack/cert-manager -n cert-manager --create-namespace   --set crds.enabled=true
```

```yaml
# charts/platform/templates/cluster-issuer.yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: {{ .Values.acme.email }}
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
      - http01:
          gatewayHTTPRoute:
            parentRefs:
              - name: order-gateway
                namespace: orders
```

```yaml
# charts/platform/templates/certificate.yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: orders-tls
  namespace: orders
spec:
  secretName: orders-tls
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
  dnsNames:
    - orders.example.com
---
# Patch Gateway listener
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: order-gateway
spec:
  listeners:
    - name: https
      protocol: HTTPS
      port: 443
      hostname: orders.example.com
      tls:
        mode: Terminate
        certificateRefs:
          - name: orders-tls
```

```bash
helm upgrade --install platform ./charts/platform -n cert-manager
kubectl describe certificate orders-tls -n orders
```

**Expected output:**

```
Events:
  Normal  Issuing    certificate issued successfully
  Normal  Ready      Certificate is up to date and has not expired
```

```bash
curl -v https://orders.example.com/cancel/ORD-1
# SSL certificate verify ok; issuer Let's Encrypt
```

**Senior takeaway:** cert-manager owns renewal — reference `Secret` from Gateway via `certificateRefs`, not manual Ingress TLS blocks.

---

### Exercise B29 — VPA vs HPA in Helm values

**Task:** Document when to use **Vertical Pod Autoscaler (VPA)** vs **Horizontal Pod Autoscaler (HPA)**. Helm-chart `order-svc` with HPA on CPU; optional VPA in `Auto` mode for right-sizing recommendations only.

**Solution:**

```yaml
# charts/order-svc/templates/hpa.yaml — scale OUT under load
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: order-svc
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: order-svc
  minReplicas: {{ .Values.autoscaling.minReplicas }}
  maxReplicas: {{ .Values.autoscaling.maxReplicas }}
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: {{ .Values.autoscaling.targetCPUUtilizationPercentage }}
```

```yaml
# charts/order-svc/templates/vpa.yaml — scale UP/DOWN per pod (do NOT run both on same metric)
{{- if .Values.vpa.enabled }}
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: order-svc
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: order-svc
  updatePolicy:
    updateMode: {{ .Values.vpa.updateMode }}  # "Off" = recommendations only
  resourcePolicy:
    containerPolicies:
      - containerName: order-svc
        minAllowed:
          cpu: 100m
          memory: 256Mi
        maxAllowed:
          cpu: "2"
          memory: 2Gi
{{- end }}
```

```yaml
# values.yaml
autoscaling:
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
vpa:
  enabled: true
  updateMode: "Off"   # interview-safe: recommend only; apply manually
```

| Concern | HPA | VPA |
|---------|-----|-----|
| Traffic spike, stateless | ✅ add replicas | ❌ slow (restart pods) |
| JVM heap mis-sized | ❌ same pod CPU | ✅ raises memory request |
| Cost baseline tuning | over-provisioned replicas | `updateMode: Off` → read recommendations |
| Same deployment, CPU metric | ✅ | ⚠️ conflict — pick one controller per resource |

```bash
helm upgrade order-svc ./charts/order-svc -n orders -f values.yaml
kubectl get hpa,vpa -n orders
kubectl describe vpa order-svc -n orders | grep -A5 Recommendation
```

**Expected output:**

```
NAME        REFERENCE              TARGETS   MINPODS   MAXPODS
order-svc   Deployment/order-svc   45%/70%   2         10

Recommendation:
  Container order-svc:
    Target:  cpu: 450m  memory: 768Mi  (was 500m / 512Mi)
```

**Senior takeaway:** HPA handles **request rate**; VPA handles **per-pod sizing** — never let both auto-scale CPU on the same Deployment without `updateMode: Off` on VPA.

---

### Exercise B30 — Kyverno policy packaged in Helm

**Task:** Ship a Kyverno `ClusterPolicy` in a Helm subchart: require `runAsNonRoot`, drop `ALL` capabilities, and label `app.kubernetes.io/part-of: orders` on every Deployment in namespace `orders`.

**Solution:**

```bash
helm repo add kyverno https://kyverno.github.io/kyverno/
helm upgrade --install kyverno kyverno/kyverno -n kyverno --create-namespace
```

```yaml
# charts/policy/templates/require-security-context.yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: orders-baseline
  annotations:
    policies.kyverno.io/title: Orders namespace baseline
spec:
  validationFailureAction: Enforce
  background: true
  rules:
    - name: require-non-root-and-drop-caps
      match:
        any:
          - resources:
              kinds: [Deployment]
              namespaces: [orders]
      validate:
        message: "Containers must runAsNonRoot and drop ALL capabilities"
        pattern:
          spec:
            template:
              spec:
                containers:
                  - securityContext:
                      runAsNonRoot: true
                      capabilities:
                        drop: ["ALL"]
    - name: require-part-of-label
      match:
        any:
          - resources:
              kinds: [Deployment]
              namespaces: [orders]
      validate:
        message: "Deployment must have label app.kubernetes.io/part-of=orders"
        pattern:
          metadata:
            labels:
              app.kubernetes.io/part-of: orders
```

```yaml
# OPA Gatekeeper equivalent (ConstraintTemplate) — Kyverno chosen for YAML-only policies
# gatekeeper.sh/require-labels — use when org standardizes on OPA Rego
```

```bash
helm upgrade --install orders-policy ./charts/policy
kubectl apply -f bad-deployment.yaml   # missing runAsNonRoot
```

**Expected output:**

```
Error from server: admission webhook "validate.kyverno.svc" denied:
  Containers must runAsNonRoot and drop ALL capabilities
```

Fix deployment → `kubectl apply` succeeds. `kubectl get cpol orders-baseline -o yaml` shows `Ready: true`.

**Senior takeaway:** Kyverno policies-as-YAML ship in Helm like app charts — version policy with app releases; use `validationFailureAction: Audit` first, then `Enforce`.

---

### Exercise C29 — Service mesh sidecar injection via Helm

**Task:** Install Istio (or Linkerd) with Helm; label namespace `orders` for sidecar injection; verify mTLS between `order-svc` and `payment-svc` and observe retry/timeout headers.

**Solution:**

```bash
# Istio base + istiod
helm repo add istio https://istio-release.storage.googleapis.com/charts
helm upgrade --install istio-base istio/base -n istio-system --create-namespace
helm upgrade --install istiod istio/istiod -n istio-system --wait

# Namespace injection label
kubectl create namespace orders --dry-run=client -o yaml | kubectl apply -f -
kubectl label namespace orders istio-injection=enabled --overwrite
```

```yaml
# charts/order-svc/templates/deployment.yaml (excerpt)
metadata:
  labels:
    app: order-svc
spec:
  template:
    metadata:
      labels:
        app: order-svc
        sidecar.istio.io/inject: "true"
    spec:
      containers:
        - name: order-svc
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
```

```yaml
# charts/order-svc/templates/virtual-service.yaml — mesh traffic policy
apiVersion: networking.istio.io/v1
kind: VirtualService
metadata:
  name: payment-svc
spec:
  hosts: [payment-svc.orders.svc.cluster.local]
  http:
    - timeout: 2s
      retries:
        attempts: 3
        perTryTimeout: 800ms
      route:
        - destination:
            host: payment-svc
```

```bash
helm upgrade --install order-svc ./charts/order-svc -n orders
helm upgrade --install payment-svc ./charts/payment-svc -n orders

# Verify two containers per pod
kubectl get pod -n orders -l app=order-svc -o jsonpath='{.items[0].spec.containers[*].name}'
# order-svc istio-proxy

# mTLS STRICT for namespace
kubectl apply -f - <<EOF
apiVersion: security.istio.io/v1
kind: PeerAuthentication
metadata:
  name: default
  namespace: orders
spec:
  mtls:
    mode: STRICT
EOF

istioctl authn tls-check order-svc.orders.svc.cluster.local payment-svc.orders.svc.cluster.local
```

**Expected output:**

```
order-svc istio-proxy
```

```
HOST:PORT                                    STATUS     SERVER     CLIENT
payment-svc.orders.svc.cluster.local:8080  OK         STRICT     STRICT
```

Simulate payment 503 → sidecar retries 3× within 2 s; `kubectl logs` on `istio-proxy` shows `upstream_rq_retry`.

**Senior takeaway:** Sidecars intercept east-west traffic — Helm charts must set **requests/limits for the proxy container** too; mesh gives mTLS + retries without app code changes, at cost of latency and operational complexity.

---

---

## Stats

| Section | Count |
|---------|------:|
| Part A — Basic | 12 |
| Part B — Intermediate | 12 |
| Part C — Hard | 9 |
| **Total** | **33** |
