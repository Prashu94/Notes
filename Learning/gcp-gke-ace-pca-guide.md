# Google Kubernetes Engine (GKE) - ACE & PCA Certification Guide

## Table of Contents
1. [Overview](#overview)
2. [Core Concepts](#core-concepts)
3. [GKE Cluster Types](#gke-cluster-types)
4. [Cluster Management](#cluster-management)
5. [Workload Management](#workload-management)
6. [Networking](#networking)
7. [Security](#security)
8. [Storage](#storage)
9. [Monitoring and Logging](#monitoring-and-logging)
10. [Auto-scaling](#auto-scaling)
11. [Updates and Upgrades](#updates-and-upgrades)
12. [Multi-cluster and Hybrid](#multi-cluster-and-hybrid)
13. [Cost Optimization](#cost-optimization)
14. [Best Practices](#best-practices)
15. [Common Exam Scenarios](#common-exam-scenarios)

---

## Overview

### What is GKE?
**Google Kubernetes Engine (GKE)** is a managed Kubernetes service that provides a platform for deploying, managing, and scaling containerized applications using Google's infrastructure.

### Key Features
- **Fully Managed Control Plane**: Google manages the Kubernetes master nodes
- **Auto-upgrade**: Automatic version updates for nodes and control plane
- **Auto-repair**: Automatic node health monitoring and repair
- **Integrated Logging and Monitoring**: Built-in Cloud Logging and Cloud Monitoring
- **Load Balancing**: Automatic load balancer provisioning
- **Auto-scaling**: Pod and node auto-scaling capabilities
- **Security**: Integrated security features including Workload Identity and Binary Authorization
- **Multi-cloud Support**: Anthos for hybrid and multi-cloud deployments

### Service Model
- **Control Plane**: Managed by Google (no charge for Standard mode)
- **Worker Nodes**: Run on Compute Engine VMs (customer pays for VM resources)
- **Autopilot Mode**: Google manages both control plane and nodes

---

## Core Concepts

### Kubernetes Fundamentals

#### Cluster Architecture
```
GKE Cluster
├── Control Plane (Master)
│   ├── API Server
│   ├── Scheduler
│   ├── Controller Manager
│   └── etcd
└── Node Pool(s)
    ├── Node 1 (Compute Engine VM)
    ├── Node 2 (Compute Engine VM)
    └── Node N (Compute Engine VM)
```

#### Key Kubernetes Objects
- **Pod**: Smallest deployable unit, one or more containers
- **Deployment**: Manages replica sets and rolling updates
- **Service**: Exposes pods as a network service
- **ConfigMap**: Configuration data for applications
- **Secret**: Sensitive data (passwords, tokens)
- **PersistentVolume (PV)**: Storage resource
- **PersistentVolumeClaim (PVC)**: Request for storage
- **Namespace**: Virtual clusters within a physical cluster
- **Ingress**: HTTP(S) load balancing and routing
- **StatefulSet**: Manages stateful applications
- **DaemonSet**: Runs a pod on all (or selected) nodes
- **Job/CronJob**: Batch processing tasks

### GKE-Specific Concepts

#### Node Pools
- Group of nodes within a cluster with the same configuration
- Can have different machine types, disk types, and settings
- Enables workload isolation and optimization

#### Workload Identity
- Recommended way for applications to access Google Cloud services
- Maps Kubernetes Service Accounts to Google Service Accounts
- More secure than using service account keys

---

## GKE Cluster Types

### 1. Standard Mode (Traditional GKE)

**Characteristics:**
- Full control over cluster configuration
- Manage node pools manually
- Configure networking, security, and scaling
- Pay for control plane in regional clusters (free for zonal)

**Use Cases:**
- Need fine-grained control
- Specific compliance requirements
- Custom node configurations
- Predictable workloads

**Configuration Example:**
```bash
gcloud container clusters create standard-cluster \
    --zone us-central1-a \
    --num-nodes 3 \
    --machine-type n1-standard-2 \
    --disk-size 100 \
    --disk-type pd-standard \
    --enable-autoscaling \
    --min-nodes 1 \
    --max-nodes 10
```

### 2. Autopilot Mode

**Characteristics:**
- Google manages infrastructure (nodes, scaling, security)
- Pay only for pod resources (CPU, memory, storage)
- Automatic node provisioning and scaling
- Built-in security best practices
- No node access (no SSH)

**Use Cases:**
- Hands-off management
- Variable workloads
- Cost optimization
- Focus on application development

**Configuration Example:**
```bash
gcloud container clusters create-auto autopilot-cluster \
    --region us-central1
```

**Key Differences:**

| Feature | Standard | Autopilot |
|---------|----------|-----------|
| Node Management | Manual | Automatic |
| Pricing | Per node (VM) | Per pod resource |
| Configuration Control | Full | Limited |
| Security Baseline | Manual setup | Enforced |
| Node Access | SSH available | No SSH |
| Scaling | Manual/Auto | Fully automatic |
| Control Plane Cost | Charged (regional) | Included |

### 3. Private Clusters

**Features:**
- Nodes have only private IP addresses
- Control plane endpoint can be private or public
- Enhanced security for sensitive workloads
- Requires Cloud NAT for internet access

**Configuration:**
```bash
gcloud container clusters create private-cluster \
    --enable-private-nodes \
    --enable-private-endpoint \
    --master-ipv4-cidr 172.16.0.0/28 \
    --region us-central1
```

### 4. Regional vs Zonal Clusters

#### Zonal Cluster
- Control plane in single zone
- Nodes can span multiple zones in same region
- Lower availability
- Lower cost

#### Regional Cluster
- Control plane replicated across 3 zones
- 99.95% SLA for control plane
- Higher availability
- Higher cost (control plane charged in Standard mode)

**Best Practice**: Use regional clusters for production workloads

---

## Cluster Management

### Creating a Cluster

#### Basic Cluster
```bash
gcloud container clusters create my-cluster \
    --zone us-central1-a \
    --num-nodes 3
```

#### Production-Grade Cluster
```bash
gcloud container clusters create production-cluster \
    --region us-central1 \
    --num-nodes 1 \
    --node-locations us-central1-a,us-central1-b,us-central1-c \
    --machine-type n1-standard-4 \
    --disk-size 100 \
    --disk-type pd-ssd \
    --enable-stackdriver-kubernetes \
    --enable-ip-alias \
    --network my-vpc \
    --subnetwork my-subnet \
    --enable-autoscaling \
    --min-nodes 1 \
    --max-nodes 10 \
    --enable-autorepair \
    --enable-autoupgrade \
    --maintenance-window-start 2023-01-01T00:00:00Z \
    --maintenance-window-duration 4h \
    --addons HorizontalPodAutoscaling,HttpLoadBalancing,GcePersistentDiskCsiDriver \
    --workload-pool=PROJECT_ID.svc.id.goog \
    --enable-shielded-nodes
```

### Connecting to a Cluster

```bash
# Get cluster credentials
gcloud container clusters get-credentials CLUSTER_NAME \
    --zone ZONE \
    --project PROJECT_ID

# Verify connection
kubectl cluster-info
kubectl get nodes
```

### Managing Node Pools

#### Create Node Pool
```bash
gcloud container node-pools create high-mem-pool \
    --cluster my-cluster \
    --zone us-central1-a \
    --machine-type n1-highmem-4 \
    --num-nodes 3 \
    --enable-autoscaling \
    --min-nodes 1 \
    --max-nodes 5
```

#### Update Node Pool
```bash
# Enable autoscaling
gcloud container node-pools update high-mem-pool \
    --cluster my-cluster \
    --zone us-central1-a \
    --enable-autoscaling \
    --min-nodes 1 \
    --max-nodes 10
```

#### Delete Node Pool
```bash
gcloud container node-pools delete high-mem-pool \
    --cluster my-cluster \
    --zone us-central1-a
```

### Resizing Clusters

```bash
# Resize node pool
gcloud container clusters resize my-cluster \
    --node-pool default-pool \
    --num-nodes 5 \
    --zone us-central1-a
```

### Deleting a Cluster

```bash
gcloud container clusters delete my-cluster \
    --zone us-central1-a
```

---

## Workload Management

### Deploying Applications

#### Using kubectl
```bash
# Create deployment from image
kubectl create deployment nginx --image=nginx:latest

# Apply from YAML
kubectl apply -f deployment.yaml

# Scale deployment
kubectl scale deployment nginx --replicas=5
```

#### Sample Deployment YAML
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
  labels:
    app: web
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: web
        image: gcr.io/PROJECT_ID/web-app:v1
        ports:
        - containerPort: 8080
        resources:
          requests:
            memory: "128Mi"
            cpu: "250m"
          limits:
            memory: "256Mi"
            cpu: "500m"
        env:
        - name: DATABASE_HOST
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: db_host
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: password
```

### Services

#### ClusterIP (Internal)
```yaml
apiVersion: v1
kind: Service
metadata:
  name: web-service
spec:
  type: ClusterIP
  selector:
    app: web
  ports:
  - port: 80
    targetPort: 8080
```

#### LoadBalancer (External)
```yaml
apiVersion: v1
kind: Service
metadata:
  name: web-service-external
spec:
  type: LoadBalancer
  selector:
    app: web
  ports:
  - port: 80
    targetPort: 8080
```

#### NodePort
```yaml
apiVersion: v1
kind: Service
metadata:
  name: web-service-nodeport
spec:
  type: NodePort
  selector:
    app: web
  ports:
  - port: 80
    targetPort: 8080
    nodePort: 30080
```

### Ingress

#### HTTP(S) Load Balancer
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web-ingress
  annotations:
    kubernetes.io/ingress.class: "gce"
    kubernetes.io/ingress.global-static-ip-name: "web-static-ip"
spec:
  rules:
  - host: example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-service
            port:
              number: 80
  - host: api.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 80
```

#### HTTPS with Managed Certificates
```yaml
apiVersion: networking.gke.io/v1
kind: ManagedCertificate
metadata:
  name: web-cert
spec:
  domains:
  - example.com
  - www.example.com
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web-ingress-https
  annotations:
    kubernetes.io/ingress.class: "gce"
    networking.gke.io/managed-certificates: "web-cert"
spec:
  rules:
  - host: example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-service
            port:
              number: 80
```

### ConfigMaps and Secrets

#### ConfigMap
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  db_host: "mysql.default.svc.cluster.local"
  app_mode: "production"
  config.json: |
    {
      "setting1": "value1",
      "setting2": "value2"
    }
```

```bash
# Create from literal
kubectl create configmap app-config \
    --from-literal=db_host=mysql.default.svc.cluster.local

# Create from file
kubectl create configmap app-config \
    --from-file=config.json
```

#### Secrets
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque
data:
  password: cGFzc3dvcmQxMjM=  # base64 encoded
  api_key: YXBpa2V5MTIz
```

```bash
# Create secret
kubectl create secret generic app-secrets \
    --from-literal=password=password123 \
    --from-literal=api_key=apikey123

# Use with Workload Identity (recommended)
kubectl create secret generic db-secret \
    --from-literal=password=password123
```

---

## Networking

### VPC-Native Clusters (Alias IP)

**Benefits:**
- Pods get IPs from VPC subnet ranges
- Direct communication with other GCP services
- Supports VPC-native features (firewall rules, VPC peering)
- Better IP management

**Configuration:**
```bash
gcloud container clusters create vpc-native-cluster \
    --enable-ip-alias \
    --network my-vpc \
    --subnetwork my-subnet \
    --cluster-ipv4-cidr=/16 \
    --services-ipv4-cidr=/22 \
    --zone us-central1-a
```

**IP Address Planning:**
```
Node Subnet:      10.0.0.0/24    (256 IPs)
Pod CIDR:         10.4.0.0/16    (65,536 IPs)
Service CIDR:     10.8.0.0/22    (1,024 IPs)
```

### Network Policies

Enable network policy enforcement:
```bash
gcloud container clusters update my-cluster \
    --enable-network-policy \
    --zone us-central1-a
```

**Example Network Policy:**
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all-ingress
  namespace: production
spec:
  podSelector: {}
  policyTypes:
  - Ingress
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-to-backend
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 8080
```

### Service Mesh (Anthos Service Mesh / Istio)

**Benefits:**
- Advanced traffic management
- Service-to-service authentication
- Observability (metrics, logs, traces)
- Circuit breaking and retries

**Enable Anthos Service Mesh:**
```bash
gcloud container clusters update my-cluster \
    --update-addons=ConfigManagement=ENABLED \
    --zone us-central1-a
```

### Load Balancing Options

| Type | Layer | Use Case | Implementation |
|------|-------|----------|----------------|
| Internal TCP/UDP | L4 | Internal services | Service type: LoadBalancer with annotation |
| External TCP/UDP | L4 | External TCP/UDP services | Service type: LoadBalancer |
| HTTP(S) | L7 | Web applications | Ingress |
| Internal HTTP(S) | L7 | Internal web apps | Ingress with annotation |
| NEG (Network Endpoint Groups) | L7 | Container-native load balancing | Enabled via annotation |

**Container-Native Load Balancing (NEG):**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: web-service
  annotations:
    cloud.google.com/neg: '{"ingress": true}'
spec:
  type: ClusterIP
  selector:
    app: web
  ports:
  - port: 80
    targetPort: 8080
```

### Multi-Cluster Networking

**GKE Multi-cluster Services (MCS):**
- Service discovery across clusters
- Cross-cluster load balancing
- Requires GKE Enterprise (formerly Anthos)

---

## Security

### Workload Identity (Recommended)

**Setup:**
```bash
# 1. Enable Workload Identity on cluster
gcloud container clusters update my-cluster \
    --workload-pool=PROJECT_ID.svc.id.goog \
    --zone us-central1-a

# 2. Create Kubernetes Service Account
kubectl create serviceaccount my-ksa \
    --namespace default

# 3. Create Google Service Account
gcloud iam service-accounts create my-gsa \
    --project=PROJECT_ID

# 4. Grant permissions to GSA
gcloud projects add-iam-policy-binding PROJECT_ID \
    --member="serviceAccount:my-gsa@PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.objectViewer"

# 5. Bind KSA to GSA
gcloud iam service-accounts add-iam-policy-binding \
    my-gsa@PROJECT_ID.iam.gserviceaccount.com \
    --role roles/iam.workloadIdentityUser \
    --member "serviceAccount:PROJECT_ID.svc.id.goog[default/my-ksa]"

# 6. Annotate KSA
kubectl annotate serviceaccount my-ksa \
    iam.gke.io/gcp-service-account=my-gsa@PROJECT_ID.iam.gserviceaccount.com \
    --namespace default
```

**Use in Pod:**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  serviceAccountName: my-ksa
  containers:
  - name: app
    image: gcr.io/PROJECT_ID/my-app
```

### Binary Authorization

**Purpose:** Enforce deployment policies (only deploy signed/verified images)

**Enable:**
```bash
gcloud container clusters update my-cluster \
    --enable-binauthz \
    --zone us-central1-a
```

### Shielded GKE Nodes

**Features:**
- Secure Boot
- vTPM (virtual Trusted Platform Module)
- Integrity Monitoring

**Enable:**
```bash
gcloud container clusters create secure-cluster \
    --enable-shielded-nodes \
    --zone us-central1-a
```

### Pod Security Standards

**Pod Security Policies (PSP) - Deprecated**
- Being replaced by Pod Security Admission

**Pod Security Admission (PSA):**
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

### Security Context

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-pod
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 2000
  containers:
  - name: app
    image: my-app
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:
        - ALL
```

### RBAC (Role-Based Access Control)

**Role and RoleBinding (Namespace-scoped):**
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: production
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: production
subjects:
- kind: User
  name: jane@example.com
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

**ClusterRole and ClusterRoleBinding (Cluster-scoped):**
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: node-reader
rules:
- apiGroups: [""]
  resources: ["nodes"]
  verbs: ["get", "watch", "list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: read-nodes-global
subjects:
- kind: User
  name: admin@example.com
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: node-reader
  apiGroup: rbac.authorization.k8s.io
```

### GKE Security Best Practices

1. **Use Workload Identity** instead of service account keys
2. **Enable Binary Authorization** for production
3. **Use Private Clusters** for sensitive workloads
4. **Enable Shielded Nodes**
5. **Implement Network Policies**
6. **Use least privilege RBAC**
7. **Scan container images** for vulnerabilities
8. **Enable GKE Security Posture**
9. **Use Secrets management** (Secret Manager)
10. **Regularly update clusters**

---

## Storage

### Storage Classes

**Standard Persistent Disk:**
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: standard-storage
provisioner: kubernetes.io/gce-pd
parameters:
  type: pd-standard
  replication-type: none
```

**SSD Persistent Disk:**
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: ssd-storage
provisioner: kubernetes.io/gce-pd
parameters:
  type: pd-ssd
  replication-type: none
```

**Regional Persistent Disk (HA):**
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: regional-storage
provisioner: kubernetes.io/gce-pd
parameters:
  type: pd-standard
  replication-type: regional-pd
volumeBindingMode: WaitForFirstConsumer
```

### Persistent Volumes

**PersistentVolumeClaim:**
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mysql-pvc
spec:
  accessModes:
  - ReadWriteOnce
  storageClassName: ssd-storage
  resources:
    requests:
      storage: 10Gi
```

**Using PVC in Pod:**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: mysql
spec:
  containers:
  - name: mysql
    image: mysql:8.0
    volumeMounts:
    - name: mysql-storage
      mountPath: /var/lib/mysql
  volumes:
  - name: mysql-storage
    persistentVolumeClaim:
      claimName: mysql-pvc
```

### StatefulSets

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql
spec:
  serviceName: mysql
  replicas: 3
  selector:
    matchLabels:
      app: mysql
  template:
    metadata:
      labels:
        app: mysql
    spec:
      containers:
      - name: mysql
        image: mysql:8.0
        ports:
        - containerPort: 3306
        volumeMounts:
        - name: data
          mountPath: /var/lib/mysql
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: ssd-storage
      resources:
        requests:
          storage: 10Gi
```

### Filestore (NFS)

**Create Filestore Instance:**
```bash
gcloud filestore instances create nfs-server \
    --zone=us-central1-a \
    --tier=STANDARD \
    --file-share=name="vol1",capacity=1TB \
    --network=name="default"
```

**PersistentVolume for Filestore:**
```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: filestore-pv
spec:
  capacity:
    storage: 1Ti
  accessModes:
  - ReadWriteMany
  nfs:
    path: /vol1
    server: 10.0.0.2  # Filestore IP
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: filestore-pvc
spec:
  accessModes:
  - ReadWriteMany
  storageClassName: ""
  volumeName: filestore-pv
  resources:
    requests:
      storage: 1Ti
```

### Storage Comparison

| Storage Type | Access Mode | Use Case | Performance |
|--------------|-------------|----------|-------------|
| pd-standard | RWO | General purpose | Standard |
| pd-ssd | RWO | Databases, high IOPS | High |
| pd-balanced | RWO | Balance cost/performance | Medium-High |
| Regional PD | RWO | High availability | Standard/High |
| Filestore | RWX | Shared storage | High |
| Cloud Storage FUSE | RWX | Object storage | Variable |

---

## Monitoring and Logging

### Cloud Monitoring (Stackdriver)

**Enable:**
```bash
gcloud container clusters create my-cluster \
    --enable-cloud-monitoring \
    --zone us-central1-a
```

**Key Metrics:**
- Node CPU/Memory utilization
- Pod CPU/Memory utilization
- Disk I/O
- Network throughput
- Container restart count
- API server latency

### Cloud Logging

**Enable:**
```bash
gcloud container clusters create my-cluster \
    --enable-cloud-logging \
    --zone us-central1-a
```

**Log Types:**
- Container logs (stdout/stderr)
- System logs (kubelet, docker)
- Audit logs (control plane activities)
- Events (Kubernetes events)

**View Logs:**
```bash
# GKE cluster logs
gcloud logging read "resource.type=k8s_cluster" \
    --limit 50 \
    --format json

# Container logs
gcloud logging read "resource.type=k8s_container" \
    --limit 50 \
    --format json
```

### Application Performance Monitoring

**Cloud Trace:**
- Distributed tracing
- Latency analysis
- Performance insights

**Cloud Profiler:**
- CPU and memory profiling
- Application optimization

### Prometheus and Grafana

**Install Prometheus Operator:**
```bash
kubectl create namespace monitoring

kubectl apply -f https://raw.githubusercontent.com/prometheus-operator/prometheus-operator/main/bundle.yaml
```

**Install Grafana:**
```bash
kubectl apply -f grafana-deployment.yaml
```

---

## Auto-scaling

### Horizontal Pod Autoscaler (HPA)

**Based on CPU:**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: web-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

**Based on Memory:**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: web-hpa-memory
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

**Custom Metrics:**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: web-hpa-custom
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "1000"
```

**Using kubectl:**
```bash
kubectl autoscale deployment web-app \
    --cpu-percent=70 \
    --min=2 \
    --max=10
```

### Vertical Pod Autoscaler (VPA)

**Install VPA:**
```bash
git clone https://github.com/kubernetes/autoscaler.git
cd autoscaler/vertical-pod-autoscaler
./hack/vpa-up.sh
```

**VPA Configuration:**
```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: web-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web-app
  updatePolicy:
    updateMode: "Auto"  # or "Off", "Initial", "Recreate"
  resourcePolicy:
    containerPolicies:
    - containerName: web
      minAllowed:
        cpu: 100m
        memory: 128Mi
      maxAllowed:
        cpu: 2
        memory: 2Gi
```

### Cluster Autoscaler (Node Autoscaling)

**Enable during cluster creation:**
```bash
gcloud container clusters create my-cluster \
    --enable-autoscaling \
    --min-nodes 1 \
    --max-nodes 10 \
    --zone us-central1-a
```

**Enable on existing cluster:**
```bash
gcloud container clusters update my-cluster \
    --enable-autoscaling \
    --min-nodes 1 \
    --max-nodes 10 \
    --zone us-central1-a
```

**Per Node Pool:**
```bash
gcloud container node-pools update default-pool \
    --cluster my-cluster \
    --enable-autoscaling \
    --min-nodes 1 \
    --max-nodes 5 \
    --zone us-central1-a
```

**How it works:**
1. Monitors pod scheduling failures
2. Adds nodes when pods can't be scheduled
3. Removes nodes when underutilized (10 minutes)
4. Respects PodDisruptionBudgets

### Node Auto-provisioning (NAP)

**Automatically creates node pools based on pending pod requirements**

**Enable:**
```bash
gcloud container clusters update my-cluster \
    --enable-autoprovisioning \
    --min-cpu 1 \
    --max-cpu 100 \
    --min-memory 1 \
    --max-memory 1000 \
    --zone us-central1-a
```

### Autoscaling Best Practices

1. **Set appropriate resource requests and limits**
2. **Use HPA for stateless applications**
3. **Use VPA for right-sizing (not with HPA on same metric)**
4. **Configure PodDisruptionBudgets**
5. **Monitor scaling behavior**
6. **Set realistic min/max values**
7. **Test autoscaling before production**

---

## Updates and Upgrades

### Release Channels

**Rapid:**
- Latest features
- Frequent updates
- Higher risk

**Regular (Default):**
- Balanced approach
- Tested features
- Moderate update frequency

**Stable:**
- Most stable
- Proven in production
- Slower updates

**Configure Channel:**
```bash
gcloud container clusters create my-cluster \
    --release-channel regular \
    --zone us-central1-a

# Update existing cluster
gcloud container clusters update my-cluster \
    --release-channel stable \
    --zone us-central1-a
```

### Auto-upgrade

**Enable:**
```bash
gcloud container clusters create my-cluster \
    --enable-autoupgrade \
    --zone us-central1-a
```

**Maintenance Window:**
```bash
gcloud container clusters update my-cluster \
    --maintenance-window-start 2023-01-01T00:00:00Z \
    --maintenance-window-duration 4h \
    --maintenance-window-recurrence "FREQ=WEEKLY;BYDAY=SU" \
    --zone us-central1-a
```

### Manual Upgrades

**Upgrade Control Plane:**
```bash
gcloud container clusters upgrade my-cluster \
    --master \
    --cluster-version 1.27.3-gke.100 \
    --zone us-central1-a
```

**Upgrade Nodes:**
```bash
gcloud container clusters upgrade my-cluster \
    --node-pool default-pool \
    --zone us-central1-a
```

**Check Available Versions:**
```bash
gcloud container get-server-config \
    --zone us-central1-a
```

### Surge Upgrades

**Control upgrade speed:**
```bash
gcloud container node-pools update default-pool \
    --cluster my-cluster \
    --max-surge-upgrade 2 \
    --max-unavailable-upgrade 1 \
    --zone us-central1-a
```

### Blue/Green Node Pool Strategy

```bash
# 1. Create new node pool with new version
gcloud container node-pools create new-pool \
    --cluster my-cluster \
    --machine-type n1-standard-4 \
    --num-nodes 3 \
    --zone us-central1-a

# 2. Cordon old nodes
kubectl cordon -l cloud.google.com/gke-nodepool=default-pool

# 3. Drain old nodes
kubectl drain NODE_NAME --ignore-daemonsets --delete-emptydir-data

# 4. Delete old node pool
gcloud container node-pools delete default-pool \
    --cluster my-cluster \
    --zone us-central1-a
```

---

## Multi-cluster and Hybrid

### GKE Enterprise (formerly Anthos)

**Components:**
- **GKE on Google Cloud**
- **GKE on VMware**
- **GKE on AWS**
- **GKE on bare metal**
- **Anthos Config Management**
- **Anthos Service Mesh**
- **Cloud Run for Anthos**

### Multi-cluster Ingress

**Route traffic across clusters:**
```yaml
apiVersion: networking.gke.io/v1
kind: MultiClusterIngress
metadata:
  name: multi-cluster-ingress
  namespace: default
spec:
  template:
    spec:
      backend:
        serviceName: backend
        servicePort: 8080
```

### Config Management

**Centralized configuration across clusters:**
```bash
# Install Config Management Operator
kubectl apply -f config-management-operator.yaml

# Configure
kubectl apply -f config-management.yaml
```

**Config Management YAML:**
```yaml
apiVersion: configmanagement.gke.io/v1
kind: ConfigManagement
metadata:
  name: config-management
spec:
  sourceFormat: unstructured
  git:
    syncRepo: https://github.com/example/configs
    syncBranch: main
    secretType: ssh
    policyDir: "configs"
```

### Fleet (Multi-cluster Management)

**Register Cluster to Fleet:**
```bash
gcloud container fleet memberships register my-cluster \
    --gke-cluster us-central1-a/my-cluster \
    --enable-workload-identity
```

**Benefits:**
- Unified management
- Cross-cluster service discovery
- Multi-cluster ingress
- Centralized policy management

---

## Cost Optimization

### Strategies

#### 1. Use Autopilot
- Pay only for pods
- No idle node costs
- Automatic bin-packing

#### 2. Right-size Resources
```yaml
resources:
  requests:
    cpu: "100m"      # Start small
    memory: "128Mi"
  limits:
    cpu: "500m"
    memory: "512Mi"
```

#### 3. Use Preemptible/Spot Nodes
```bash
gcloud container node-pools create spot-pool \
    --cluster my-cluster \
    --spot \
    --machine-type n1-standard-4 \
    --num-nodes 3 \
    --zone us-central1-a
```

**Handle evictions:**
```yaml
spec:
  tolerations:
  - key: cloud.google.com/gke-preemptible
    operator: Equal
    value: "true"
    effect: NoSchedule
```

#### 4. Use Appropriate Machine Types
```bash
# E2 (cost-optimized)
--machine-type e2-medium

# N1 (balanced)
--machine-type n1-standard-2

# N2 (higher performance)
--machine-type n2-standard-4

# Custom
--custom-cpu 2 --custom-memory 7680
```

#### 5. Enable Cluster Autoscaling
```bash
gcloud container clusters update my-cluster \
    --enable-autoscaling \
    --min-nodes 1 \
    --max-nodes 10 \
    --zone us-central1-a
```

#### 6. Use Zonal Clusters for Dev/Test
- Lower control plane costs
- Acceptable for non-production

#### 7. Schedule Batch Jobs Efficiently
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: batch-job
spec:
  schedule: "0 2 * * *"  # Run during off-peak hours
  jobTemplate:
    spec:
      template:
        spec:
          nodeSelector:
            cloud.google.com/gke-spot: "true"
          containers:
          - name: job
            image: my-batch-job
```

#### 8. Use Storage Wisely
- Use `pd-standard` instead of `pd-ssd` when possible
- Delete unused PVs
- Use appropriate storage class

#### 9. Minimize Data Transfer
- Use regional resources
- Enable VPC-native clusters
- Use Private Google Access

#### 10. Monitor and Analyze Costs
```bash
# Enable billing export
gcloud beta billing accounts set-iam-policy BILLING_ACCOUNT_ID policy.yaml
```

### Cost Monitoring

**GKE Cost Allocation:**
```bash
gcloud container clusters update my-cluster \
    --enable-cost-allocation \
    --zone us-central1-a
```

**Labels for Cost Tracking:**
```yaml
metadata:
  labels:
    team: platform
    environment: production
    cost-center: engineering
```

---

## Best Practices

### Cluster Design

1. **Use Regional Clusters for Production**
   - Higher availability (99.95% SLA)
   - Control plane redundancy

2. **Use VPC-Native Clusters**
   - Better IP management
   - Native GCP integration

3. **Enable Workload Identity**
   - Secure service account access
   - No key management

4. **Use Private Clusters for Sensitive Workloads**
   - Enhanced security
   - No public IPs for nodes

5. **Separate Node Pools by Workload**
   - Different machine types
   - Different scaling policies
   - Workload isolation

### Application Design

1. **Set Resource Requests and Limits**
   ```yaml
   resources:
     requests:
       cpu: "250m"
       memory: "256Mi"
     limits:
       cpu: "500m"
       memory: "512Mi"
   ```

2. **Use Health Checks**
   ```yaml
   livenessProbe:
     httpGet:
       path: /healthz
       port: 8080
     initialDelaySeconds: 30
     periodSeconds: 10
   
   readinessProbe:
     httpGet:
       path: /ready
       port: 8080
     initialDelaySeconds: 5
     periodSeconds: 5
   ```

3. **Implement Graceful Shutdown**
   ```yaml
   lifecycle:
     preStop:
       exec:
         command: ["/bin/sh", "-c", "sleep 15"]
   ```

4. **Use ConfigMaps and Secrets**
   - Separate configuration from code
   - Environment-specific settings

5. **Implement PodDisruptionBudgets**
   ```yaml
   apiVersion: policy/v1
   kind: PodDisruptionBudget
   metadata:
     name: web-pdb
   spec:
     minAvailable: 2
     selector:
       matchLabels:
         app: web
   ```

### Security Best Practices

1. **Enable Shielded Nodes**
2. **Use Workload Identity**
3. **Enable Binary Authorization**
4. **Implement Network Policies**
5. **Use Private Clusters**
6. **Enable GKE Security Posture**
7. **Scan Container Images**
8. **Use Least Privilege RBAC**
9. **Rotate Credentials Regularly**
10. **Enable Audit Logging**

### Networking Best Practices

1. **Use VPC-Native Clusters**
2. **Plan IP Address Ranges Carefully**
3. **Implement Network Policies**
4. **Use Private Google Access**
5. **Enable Container-Native Load Balancing**
6. **Use Cloud Armor for DDoS Protection**

### Monitoring and Logging

1. **Enable Cloud Monitoring and Logging**
2. **Set Up Alerts**
3. **Use Structured Logging**
4. **Monitor Resource Utilization**
5. **Track Application Metrics**
6. **Review Audit Logs**

### Operational Best Practices

1. **Use GitOps for Configuration Management**
2. **Automate Deployments (CI/CD)**
3. **Test in Non-Production First**
4. **Use Release Channels**
5. **Enable Auto-upgrade with Maintenance Windows**
6. **Regular Backup Strategy**
7. **Document Runbooks**
8. **Conduct Disaster Recovery Drills**

---

## Common Exam Scenarios

### Scenario 1: High Availability Web Application

**Requirements:**
- 99.95% availability
- Auto-scaling based on traffic
- HTTPS with managed certificates
- Global load balancing

**Solution:**
```bash
# 1. Create regional GKE cluster
gcloud container clusters create web-cluster \
    --region us-central1 \
    --num-nodes 1 \
    --node-locations us-central1-a,us-central1-b,us-central1-c \
    --enable-autoscaling \
    --min-nodes 1 \
    --max-nodes 10 \
    --enable-autorepair \
    --enable-autoupgrade \
    --enable-ip-alias \
    --workload-pool=PROJECT_ID.svc.id.goog

# 2. Deploy application with HPA
kubectl apply -f deployment.yaml
kubectl apply -f hpa.yaml

# 3. Create managed certificate
kubectl apply -f managed-cert.yaml

# 4. Create Ingress with HTTPS
kubectl apply -f ingress.yaml
```

### Scenario 2: Microservices with Service Mesh

**Requirements:**
- Multiple microservices
- Service-to-service authentication
- Traffic management
- Observability

**Solution:**
1. Enable Anthos Service Mesh
2. Deploy microservices with sidecar injection
3. Configure VirtualServices and DestinationRules
4. Implement mTLS
5. Set up monitoring with Cloud Trace

### Scenario 3: Batch Processing Jobs

**Requirements:**
- Cost-effective
- Run during off-peak hours
- Handle failures gracefully

**Solution:**
```yaml
# Use Spot VMs
apiVersion: batch/v1
kind: CronJob
metadata:
  name: batch-processor
spec:
  schedule: "0 2 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          nodeSelector:
            cloud.google.com/gke-spot: "true"
          restartPolicy: OnFailure
          containers:
          - name: processor
            image: gcr.io/PROJECT_ID/batch-processor
            resources:
              requests:
                cpu: "1"
                memory: "2Gi"
```

### Scenario 4: Stateful Database

**Requirements:**
- Persistent storage
- High availability
- Automatic failover

**Solution:**
```yaml
# StatefulSet with regional persistent disk
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
spec:
  serviceName: postgres
  replicas: 3
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:14
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: data
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: regional-storage
      resources:
        requests:
          storage: 100Gi
```

### Scenario 5: Multi-tenant Application

**Requirements:**
- Workload isolation
- Resource quotas per tenant
- Network isolation

**Solution:**
```bash
# 1. Create namespace per tenant
kubectl create namespace tenant-a
kubectl create namespace tenant-b

# 2. Set resource quotas
kubectl apply -f resource-quota.yaml -n tenant-a

# 3. Apply network policies
kubectl apply -f network-policy.yaml -n tenant-a

# 4. Use separate node pools (optional)
gcloud container node-pools create tenant-a-pool \
    --cluster multi-tenant-cluster \
    --machine-type n1-standard-4 \
    --num-nodes 3

# 5. Use taints and tolerations for pod placement
```

### Scenario 6: Hybrid Cloud Deployment

**Requirements:**
- On-premises integration
- Consistent management
- Unified service mesh

**Solution:**
1. Deploy GKE Enterprise (Anthos)
2. Register on-premises clusters to Fleet
3. Enable Anthos Config Management
4. Set up Anthos Service Mesh
5. Configure Multi-cluster Ingress

### Scenario 7: CI/CD Pipeline

**Requirements:**
- Automated deployments
- Rollback capability
- Progressive delivery

**Solution:**
```yaml
# Cloud Build configuration
steps:
- name: 'gcr.io/cloud-builders/docker'
  args: ['build', '-t', 'gcr.io/$PROJECT_ID/app:$SHORT_SHA', '.']

- name: 'gcr.io/cloud-builders/docker'
  args: ['push', 'gcr.io/$PROJECT_ID/app:$SHORT_SHA']

- name: 'gcr.io/cloud-builders/gke-deploy'
  args:
  - run
  - --filename=k8s/
  - --image=gcr.io/$PROJECT_ID/app:$SHORT_SHA
  - --location=us-central1
  - --cluster=production-cluster
```

### Scenario 8: Data Processing Pipeline

**Requirements:**
- Process large datasets
- Autoscaling based on queue depth
- Cost optimization

**Solution:**
1. Use Spot VMs for worker nodes
2. Deploy Kubernetes Jobs
3. Use HPA with custom metrics (queue length)
4. Implement pod priority and preemption
5. Use node auto-provisioning

---

## Quick Command Reference

### Cluster Management
```bash
# Create cluster
gcloud container clusters create CLUSTER_NAME --zone ZONE

# Get credentials
gcloud container clusters get-credentials CLUSTER_NAME --zone ZONE

# List clusters
gcloud container clusters list

# Describe cluster
gcloud container clusters describe CLUSTER_NAME --zone ZONE

# Delete cluster
gcloud container clusters delete CLUSTER_NAME --zone ZONE
```

### Node Pool Management
```bash
# Create node pool
gcloud container node-pools create POOL_NAME --cluster CLUSTER_NAME

# List node pools
gcloud container node-pools list --cluster CLUSTER_NAME

# Delete node pool
gcloud container node-pools delete POOL_NAME --cluster CLUSTER_NAME
```

### kubectl Basics
```bash
# Get resources
kubectl get pods
kubectl get deployments
kubectl get services
kubectl get nodes

# Describe resources
kubectl describe pod POD_NAME
kubectl describe service SERVICE_NAME

# Create from file
kubectl apply -f FILE.yaml

# Delete resources
kubectl delete pod POD_NAME
kubectl delete -f FILE.yaml

# Logs
kubectl logs POD_NAME
kubectl logs -f POD_NAME  # Follow

# Execute commands
kubectl exec -it POD_NAME -- /bin/bash

# Port forwarding
kubectl port-forward POD_NAME 8080:80

# Scale
kubectl scale deployment DEPLOYMENT_NAME --replicas=5
```

### Workload Identity
```bash
# Enable on cluster
gcloud container clusters update CLUSTER_NAME \
    --workload-pool=PROJECT_ID.svc.id.goog

# Bind KSA to GSA
gcloud iam service-accounts add-iam-policy-binding GSA@PROJECT_ID.iam.gserviceaccount.com \
    --role roles/iam.workloadIdentityUser \
    --member "serviceAccount:PROJECT_ID.svc.id.goog[NAMESPACE/KSA]"

# Annotate KSA
kubectl annotate serviceaccount KSA \
    iam.gke.io/gcp-service-account=GSA@PROJECT_ID.iam.gserviceaccount.com
```

---

## Exam Tips

### For ACE (Associate Cloud Engineer)

**Focus Areas:**
1. **Basic cluster creation and management**
2. **Deploying applications** (kubectl apply, create)
3. **Services and Ingress** (LoadBalancer, Ingress)
4. **Basic scaling** (manual scaling, HPA)
5. **Monitoring and logging** (Cloud Monitoring/Logging)
6. **Node pool management**
7. **Workload Identity basics**
8. **Storage** (PV, PVC, StorageClass)

**Common Tasks:**
- Create a GKE cluster with specific configurations
- Deploy a containerized application
- Expose an application with a LoadBalancer
- Scale a deployment
- View logs and metrics
- Update cluster or node pool settings

### For PCA (Professional Cloud Architect)

**Focus Areas:**
1. **High availability architecture** (regional clusters, multi-zone)
2. **Security best practices** (Workload Identity, Binary Authorization, Private clusters)
3. **Advanced networking** (VPC-native, Network Policies, Service Mesh)
4. **Multi-cluster management** (GKE Enterprise, Fleet)
5. **Cost optimization strategies**
6. **Disaster recovery and backup**
7. **Advanced autoscaling** (HPA, VPA, NAP)
8. **CI/CD integration**
9. **Compliance and governance**
10. **Hybrid and multi-cloud** scenarios

**Common Scenarios:**
- Design a highly available microservices architecture
- Implement zero-downtime deployments
- Secure inter-service communication
- Optimize costs for variable workloads
- Design disaster recovery strategy
- Implement multi-region failover
- Integrate with existing on-premises infrastructure

### General Tips

1. **Understand the differences** between Standard and Autopilot modes
2. **Know when to use** different service types (ClusterIP, LoadBalancer, Ingress)
3. **Be familiar with** gcloud and kubectl commands
4. **Understand pricing model** (node costs vs pod costs)
5. **Know security best practices** (Workload Identity, Private clusters)
6. **Understand autoscaling options** (HPA, VPA, Cluster Autoscaler)
7. **Be familiar with** storage options (PD, Filestore)
8. **Know monitoring and logging** capabilities
9. **Understand upgrade strategies** (surge upgrades, blue/green)
10. **Practice hands-on** in GCP Console and CLI

---

## Additional Resources

### Official Documentation
- [GKE Documentation](https://cloud.google.com/kubernetes-engine/docs)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [GKE Best Practices](https://cloud.google.com/kubernetes-engine/docs/best-practices)

### Training
- [Google Cloud Skills Boost](https://www.cloudskillsboost.google/)
- [Kubernetes Learning Path](https://kubernetes.io/training/)

### Tools
- **gcloud CLI**: Google Cloud command-line tool
- **kubectl**: Kubernetes command-line tool
- **Cloud Console**: Web-based management interface
- **Cloud Shell**: Browser-based shell with pre-installed tools

### Practice
- Create multiple clusters with different configurations
- Deploy sample applications
- Test autoscaling scenarios
- Practice disaster recovery procedures
- Implement security best practices
- Set up monitoring and alerting

---

## Glossary

- **ACE**: Associate Cloud Engineer
- **PCA**: Professional Cloud Architect
- **GKE**: Google Kubernetes Engine
- **HPA**: Horizontal Pod Autoscaler
- **VPA**: Vertical Pod Autoscaler
- **NAP**: Node Auto-provisioning
- **RBAC**: Role-Based Access Control
- **PSP**: Pod Security Policy (deprecated)
- **PSA**: Pod Security Admission
- **NEG**: Network Endpoint Group
- **MCS**: Multi-cluster Services
- **VPC**: Virtual Private Cloud
- **PV**: Persistent Volume
- **PVC**: Persistent Volume Claim
- **PDB**: Pod Disruption Budget
- **KSA**: Kubernetes Service Account
- **GSA**: Google Service Account

---

**Last Updated**: October 2025
**Version**: 1.0
**Target Certifications**: Google Cloud ACE, Google Cloud Professional Cloud Architect

**Good luck with your certification! 🚀**
