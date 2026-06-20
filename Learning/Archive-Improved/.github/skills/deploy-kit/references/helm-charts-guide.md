# Helm Charts Guide — Deploy Kit Reference

## Helm 3 Best Practices

- One chart per microservice
- All configurable values in `values.yaml` — nothing hardcoded in templates
- Override per environment with `values-staging.yaml` / `values-production.yaml`
- Use named templates in `_helpers.tpl` for labels and name generation
- Pin chart versions in `Chart.yaml`; bump `appVersion` with each release

---

## _helpers.tpl Pattern

```yaml
{{/*
Expand the name of the chart.
*/}}
{{- define "<service>.name" -}}
{{- .Chart.Name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "<service>.fullname" -}}
{{- $name := .Chart.Name }}
{{- printf "%s" $name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "<service>.labels" -}}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "<service>.selectorLabels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
```

---

## Resource Limits Reference

| Service Size | CPU Request | CPU Limit | Memory Request | Memory Limit |
|---|---|---|---|---|
| Extra Small (cron, sidecar) | 50m | 100m | 64Mi | 128Mi |
| Small (lightweight API) | 100m | 300m | 128Mi | 256Mi |
| Medium (standard service) | 250m | 500m | 256Mi | 512Mi |
| Large (high-traffic, ML) | 500m | 1000m | 512Mi | 1Gi |
| Extra Large (data processing) | 1000m | 2000m | 1Gi | 2Gi |

---

## Health Probe Patterns by Technology

### Spring Boot (Actuator)
```yaml
livenessProbe:
  httpGet:
    path: /actuator/health/liveness
    port: 8080
  initialDelaySeconds: 45
  periodSeconds: 10
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /actuator/health/readiness
    port: 8080
  initialDelaySeconds: 15
  periodSeconds: 5
  failureThreshold: 3
```

### FastAPI / Flask
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 15
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /health/ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
```

### NestJS / Express
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 3000
  initialDelaySeconds: 20
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /health
    port: 3000
  initialDelaySeconds: 5
  periodSeconds: 5
```

---

## HPA Configuration

```yaml
# templates/hpa.yaml
{{- if .Values.autoscaling.enabled }}
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {{ include "<service>.fullname" . }}
  labels:
    {{- include "<service>.labels" . | nindent 4 }}
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {{ include "<service>.fullname" . }}
  minReplicas: {{ .Values.autoscaling.minReplicas }}
  maxReplicas: {{ .Values.autoscaling.maxReplicas }}
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: {{ .Values.autoscaling.targetCPUUtilizationPercentage }}
{{- end }}
```

---

## Secret Handling Pattern

**Never** put secret values in `values.yaml`. Reference a pre-created Kubernetes Secret:

```yaml
# templates/secret.yaml — shows the expected keys, values must be injected externally
apiVersion: v1
kind: Secret
metadata:
  name: {{ .Values.secretName }}
  annotations:
    helm.sh/hook: pre-install,pre-upgrade
    helm.sh/hook-weight: "-5"
    helm.sh/resource-policy: keep   # don't delete secret on helm uninstall
type: Opaque
data:
  # Keys are documented here but values must be set by CI/CD pipeline
  # kubectl create secret generic <name> --from-env-file=.env.production --dry-run=client -o yaml | kubectl apply -f -
  DB_PASSWORD: ""         # TODO: inject via CI/CD
  JWT_SECRET: ""          # TODO: inject via CI/CD
  API_KEY: ""             # TODO: inject via CI/CD
```

---

## Ingress with TLS

```yaml
# templates/ingress.yaml
{{- if .Values.ingress.enabled }}
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {{ include "<service>.fullname" . }}
  labels:
    {{- include "<service>.labels" . | nindent 4 }}
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    {{- with .Values.ingress.annotations }}
    {{- toYaml . | nindent 4 }}
    {{- end }}
spec:
  ingressClassName: {{ .Values.ingress.className }}
  {{- if .Values.ingress.tls }}
  tls:
    {{- toYaml .Values.ingress.tls | nindent 4 }}
  {{- end }}
  rules:
    {{- range .Values.ingress.hosts }}
    - host: {{ .host }}
      http:
        paths:
          {{- range .paths }}
          - path: {{ .path }}
            pathType: {{ .pathType }}
            backend:
              service:
                name: {{ include "<service>.fullname" $ }}
                port:
                  number: {{ $.Values.service.port }}
          {{- end }}
    {{- end }}
{{- end }}
```

---

## Install / Upgrade Commands

```bash
# Staging
helm upgrade --install <service> ./helm/<service> \
  -f ./helm/<service>/values-staging.yaml \
  --namespace <namespace> \
  --set image.tag=<git-sha>

# Production
helm upgrade --install <service> ./helm/<service> \
  -f ./helm/<service>/values-production.yaml \
  --namespace <namespace> \
  --set image.tag=<release-tag> \
  --atomic \
  --timeout 5m

# Rollback
helm rollback <service> --namespace <namespace>
```
