# Module 11: Advanced Topics

## 📚 Overview

Explore advanced Kubernetes concepts including Custom Resource Definitions, Operators, Admission Controllers, and Helm.

**Exam Weight**: CKA (Optional), CKAD (Optional - beyond core exam scope)

---

## Custom Resource Definitions (CRDs)

CRDs extend Kubernetes API with custom resources.

### Create CRD

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: websites.extensions.example.com
spec:
  group: extensions.example.com
  versions:
    - name: v1
      served: true
      storage: true
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              properties:
                domain:
                  type: string
                replicas:
                  type: integer
                  minimum: 1
                  maximum: 10
  scope: Namespaced
  names:
    plural: websites
    singular: website
    kind: Website
    shortNames:
      - ws
```

**Apply CRD**:
```bash
kubectl apply -f website-crd.yaml

# Verify
kubectl get crds
kubectl api-resources | grep website
```

### Use Custom Resource

```yaml
apiVersion: extensions.example.com/v1
kind: Website
metadata:
  name: my-website
spec:
  domain: example.com
  replicas: 3
```

```bash
# Create custom resource
kubectl apply -f website.yaml

# View custom resources
kubectl get websites
kubectl get ws  # Using shortname

# Describe
kubectl describe website my-website
```

---

## Operators

Operators are software extensions that use CRDs to manage applications.

**What operators do**:
- Deploy applications
- Take backups
- Perform upgrades
- Handle failovers
- Scale automatically

### Popular Operators

- **Prometheus Operator**: Manages Prometheus monitoring
- **Cert-Manager**: Manages TLS certificates
- **MySQL Operator**: Manages MySQL databases
- **Elasticsearch Operator**: Manages Elasticsearch clusters

### Install Operator Example (Prometheus)

```bash
# Add Prometheus Operator
kubectl apply -f https://raw.githubusercontent.com/prometheus-operator/prometheus-operator/main/bundle.yaml

# Verify
kubectl get pods -n default

# Create ServiceMonitor (custom resource)
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: my-app-monitor
spec:
  selector:
    matchLabels:
      app: my-app
  endpoints:
    - port: metrics
```

---

## Admission Controllers

Admission controllers intercept requests to the Kubernetes API before object persistence.

### Types

1. **Validating**: Validate requests
2. **Mutating**: Modify requests

### Common Admission Controllers

| Controller | Type | Purpose |
|------------|------|---------|
| NamespaceLifecycle | Validating | Prevents operations in terminating namespaces |
| LimitRanger | Validating | Enforces resource limits |
| ServiceAccount | Mutating | Adds default ServiceAccount |
| MutatingAdmissionWebhook | Mutating | Calls external webhooks |
| ValidatingAdmissionWebhook | Validating | Calls external webhooks |
| PodSecurityPolicy (deprecated) | Validating | Enforced security policies |

### Check Enabled Admission Controllers

```bash
kubectl exec -n kube-system kube-apiserver-<node> -- kube-apiserver -h | grep enable-admission-plugins
```

### Admission Webhooks

**Validating Webhook**:
```yaml
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingWebhookConfiguration
metadata:
  name: pod-validator
webhooks:
  - name: validate.example.com
    clientConfig:
      service:
        name: validation-service
        namespace: default
        path: /validate
      caBundle: <base64-ca-cert>
    rules:
      - operations: ["CREATE", "UPDATE"]
        apiGroups: [""]
        apiVersions: ["v1"]
        resources: ["pods"]
    admissionReviewVersions: ["v1"]
    sideEffects: None
```

**Mutating Webhook**:
```yaml
apiVersion: admissionregistration.k8s.io/v1
kind: MutatingWebhookConfiguration
metadata:
  name: pod-mutator
webhooks:
  - name: mutate.example.com
    clientConfig:
      service:
        name: mutation-service
        namespace: default
        path: /mutate
      caBundle: <base64-ca-cert>
    rules:
      - operations: ["CREATE"]
        apiGroups: [""]
        apiVersions: ["v1"]
        resources: ["pods"]
    admissionReviewVersions: ["v1"]
    sideEffects: None
```

**Use cases**:
- Inject sidecar containers
- Enforce naming conventions
- Add labels automatically
- Validate resource configurations

---

## Helm

Helm is a package manager for Kubernetes.

### Helm Concepts

- **Chart**: Package containing Kubernetes manifests
- **Release**: Instance of a chart running in cluster
- **Repository**: Collection of charts

### Install Helm

```bash
# macOS
brew install helm

# Linux
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Verify
helm version
```

### Using Helm

**Add Repository**:
```bash
# Add official Helm stable repo
helm repo add stable https://charts.helm.sh/stable

# Add bitnami repo
helm repo add bitnami https://charts.bitnami.com/bitnami

# Update repos
helm repo update

# Search charts
helm search repo nginx
helm search hub nginx
```

**Install Chart**:
```bash
# Install chart
helm install my-nginx bitnami/nginx

# Install with custom values
helm install my-nginx bitnami/nginx --set service.type=NodePort

# Install from values file
helm install my-nginx bitnami/nginx -f values.yaml

# Install in specific namespace
helm install my-nginx bitnami/nginx -n production --create-namespace
```

**Manage Releases**:
```bash
# List releases
helm list
helm list --all-namespaces

# Get release status
helm status my-nginx

# Get release values
helm get values my-nginx

# Get release manifest
helm get manifest my-nginx

# Upgrade release
helm upgrade my-nginx bitnami/nginx --set replicaCount=3

# Rollback release
helm rollback my-nginx 1

# Uninstall release
helm uninstall my-nginx
```

### Create Helm Chart

```bash
# Create new chart
helm create my-chart

# Chart structure:
my-chart/
  Chart.yaml          # Chart metadata
  values.yaml         # Default values
  templates/          # Kubernetes manifests
    deployment.yaml
    service.yaml
    ingress.yaml
    _helpers.tpl      # Template helpers
  charts/             # Dependent charts
  .helmignore        # Files to ignore
```

**Chart.yaml**:
```yaml
apiVersion: v2
name: my-chart
description: A Helm chart for my application
type: application
version: 1.0.0
appVersion: "1.0"
```

**values.yaml**:
```yaml
replicaCount: 3

image:
  repository: nginx
  tag: "1.21"
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 80

resources:
  limits:
    cpu: 200m
    memory: 256Mi
  requests:
    cpu: 100m
    memory: 128Mi
```

**Template (deployment.yaml)**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}-deployment
  labels:
    app: {{ .Chart.Name }}
    version: {{ .Chart.Version }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app: {{ .Chart.Name }}
  template:
    metadata:
      labels:
        app: {{ .Chart.Name }}
    spec:
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - containerPort: 80
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
```

**Install custom chart**:
```bash
# Validate chart
helm lint my-chart

# Dry run (show generated manifests)
helm install my-app ./my-chart --dry-run --debug

# Install chart
helm install my-app ./my-chart

# Package chart
helm package my-chart
```

---

## Service Mesh (Istio)

Service mesh provides observability, traffic management, and security for microservices.

### Istio Features

- Traffic management (routing, load balancing)
- Security (mTLS, authentication)
- Observability (metrics, tracing)
- Policy enforcement

### Install Istio

```bash
# Download Istio
curl -L https://istio.io/downloadIstio | sh -

# Install Istio
istioctl install --set profile=demo -y

# Enable sidecar injection
kubectl label namespace default istio-injection=enabled

# Verify
kubectl get pods -n istio-system
```

### Virtual Service Example

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: reviews-route
spec:
  hosts:
    - reviews
  http:
    - match:
        - headers:
            end-user:
              exact: jason
      route:
        - destination:
            host: reviews
            subset: v2
    - route:
        - destination:
            host: reviews
            subset: v1
```

---

## DaemonSets

Ensures a pod runs on all (or some) nodes.

**Use cases**:
- Log collectors (Fluentd)
- Monitoring agents (Prometheus Node Exporter)
- Network plugins (CNI)

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: node-exporter
spec:
  selector:
    matchLabels:
      app: node-exporter
  template:
    metadata:
      labels:
        app: node-exporter
    spec:
      containers:
        - name: node-exporter
          image: prom/node-exporter:latest
          ports:
            - containerPort: 9100
```

```bash
kubectl apply -f daemonset.yaml
kubectl get daemonsets
kubectl get pods -o wide  # Shows one pod per node
```

---

## Taints and Tolerations

Control which pods can be scheduled on which nodes.

### Taints

**Add taint to node**:
```bash
# NoSchedule: Don't schedule new pods
kubectl taint nodes node1 key=value:NoSchedule

# PreferNoSchedule: Try not to schedule
kubectl taint nodes node1 key=value:PreferNoSchedule

# NoExecute: Evict existing pods
kubectl taint nodes node1 key=value:NoExecute

# Remove taint
kubectl taint nodes node1 key=value:NoSchedule-
```

### Tolerations

**Add toleration to pod**:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: tolerant-pod
spec:
  tolerations:
    - key: "key"
      operator: "Equal"
      value: "value"
      effect: "NoSchedule"
  containers:
    - name: nginx
      image: nginx
```

---

## Node Affinity

Constrain pods to specific nodes.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: affinity-pod
spec:
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
          - matchExpressions:
              - key: disktype
                operator: In
                values:
                  - ssd
      preferredDuringSchedulingIgnoredDuringExecution:
        - weight: 1
          preference:
            matchExpressions:
              - key: zone
                operator: In
                values:
                  - us-east-1a
  containers:
    - name: nginx
      image: nginx
```

---

## Summary

**CRDs**: Extend Kubernetes with custom resources
**Operators**: Automate application management using CRDs
**Admission Controllers**: Validate and mutate API requests
**Helm**: Package manager for Kubernetes
**Service Mesh**: Advanced traffic management and security
**DaemonSets**: Run pod on every node
**Taints & Tolerations**: Control pod scheduling
**Node Affinity**: Constrain pods to nodes

These topics are beyond core CKA/CKAD requirements but useful for advanced Kubernetes usage.

---

**Congratulations! You've completed all 11 modules!** 🎉

**Next**: Take practice exams in [Module 12](../12-practice-exams/README.md)
