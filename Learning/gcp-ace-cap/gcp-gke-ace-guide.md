# Google Kubernetes Engine (GKE) - Associate Cloud Engineer Guide

## Table of Contents
1. [GKE Overview](#gke-overview)
2. [GKE Cluster Architecture](#gke-cluster-architecture)
3. [Autopilot vs Standard Mode](#autopilot-vs-standard-mode)
4. [Creating and Managing Clusters](#creating-and-managing-clusters)
5. [Node Pools Management](#node-pools-management)
6. [Deploying Workloads](#deploying-workloads)
7. [Kubernetes Services](#kubernetes-services)
8. [ConfigMaps and Secrets](#configmaps-and-secrets)
9. [Storage in GKE](#storage-in-gke)
10. [Monitoring and Logging](#monitoring-and-logging)
11. [Troubleshooting](#troubleshooting)
12. [Best Practices](#best-practices)

---

## GKE Overview

### What is Google Kubernetes Engine?

Google Kubernetes Engine (GKE) is a managed Kubernetes service that automates the deployment, scaling, and management of containerized applications using Kubernetes orchestration.

**Key Features:**
- **Managed Control Plane**: Google manages the Kubernetes master (API server, scheduler, controllers)
- **Automatic Upgrades**: Control plane and nodes can auto-upgrade to latest Kubernetes versions
- **Auto-Scaling**: Horizontal Pod Autoscaler (HPA) and Cluster Autoscaler
- **Integrated Monitoring**: Built-in Cloud Logging and Cloud Monitoring
- **Security**: Workload Identity, Binary Authorization, Pod Security Standards
- **Networking**: VPC-native networking with alias IP ranges, Network Policies

**GKE Cluster Types:**
- **Zonal Cluster**: Single control plane in one zone (lower cost, single point of failure)
- **Regional Cluster**: Replicated control plane across 3 zones (99.95% SLA, high availability)

---

## GKE Cluster Architecture

### Control Plane Components

The control plane runs the Kubernetes master components (managed by Google):

**1. API Server (kube-apiserver)**
- Entry point for all REST commands to manipulate Kubernetes resources
- Validates and processes API requests
- Provides frontend for cluster's shared state

**2. Scheduler (kube-scheduler)**
- Watches for newly created Pods without assigned nodes
- Selects optimal node based on resource requirements, affinity rules
- Considers CPU, memory, storage, and custom constraints

**3. Controller Manager**
- Runs controller processes (node controller, replication controller, endpoints controller)
- Maintains desired state (e.g., ensures correct number of Pods are running)
- Responds to node failures and manages service endpoints

**4. etcd / Cloud Spanner**
- Distributed key-value store for cluster state
- Stores all API objects (Deployments, Services, ConfigMaps, Secrets)
- Regional clusters use Cloud Spanner for higher availability

### Node Components

Nodes are Compute Engine VMs that run containerized workloads:

**1. Kubelet**
- Agent running on each node
- Communicates with control plane API server
- Ensures containers are running in Pods as specified
- Reports node and Pod status

**2. Container Runtime (containerd)**
- Runs containers on the node
- Pulls container images from registries
- Manages container lifecycle (start, stop, monitor)

**3. Kube-proxy**
- Network proxy running on each node
- Maintains network rules for Pod communication
- Implements Kubernetes Service abstraction

**4. DaemonSets**
- System Pods running on every node (logging agents, monitoring, networking)
- Examples: Fluentd (logs), node-problem-detector, kube-proxy

---

## Autopilot vs Standard Mode

### GKE Autopilot

**Fully Managed Infrastructure:**
- Google manages nodes, scaling, upgrades, repairs, health checks
- No SSH access to nodes
- Automatic node provisioning based on Pod resource requests
- Security hardened by default (Shielded GKE nodes, Workload Identity enabled)

**Benefits:**
- **Reduced Operational Overhead**: No node pool management
- **Automatic Scaling**: Nodes scale automatically with workload demands
- **Cost Optimization**: Pay only for Pod resources (vCPU, memory, storage), not idle nodes
- **Security**: Hardened configuration with many security settings enabled by default
- **SLA**: Covers both control plane and compute capacity

**Pricing Model:**
- **General-Purpose Pods**: Pod-based billing (pay for vCPU, memory, ephemeral storage)
- **Specific Hardware Pods** (GPUs, specific machine types): Node-based billing with management premium

**Create Autopilot Cluster:**
```bash
# Regional Autopilot cluster
gcloud container clusters create-auto my-autopilot-cluster \
    --region=us-central1 \
    --project=my-project

# With custom network
gcloud container clusters create-auto my-autopilot-cluster \
    --region=us-central1 \
    --network=my-vpc \
    --subnetwork=my-subnet \
    --cluster-secondary-range-name=pods \
    --services-secondary-range-name=services
```

### GKE Standard

**User-Managed Infrastructure:**
- User creates and manages node pools
- Choose machine types, sizes, disk types
- Manual or automatic scaling configuration
- SSH access to nodes for debugging

**Benefits:**
- **Full Control**: Custom node configurations, SSH access, OS customization
- **Flexibility**: DaemonSets, node-level agents, specific machine types
- **Legacy Workloads**: Support for workloads requiring node-level access

**Node Pool Management:**
- Users manage lifecycle (creation, upgrades, deletion)
- Configure autoscaling per node pool
- Choose Compute Engine machine types

**Create Standard Cluster:**
```bash
# Zonal Standard cluster
gcloud container clusters create my-standard-cluster \
    --zone=us-central1-a \
    --machine-type=e2-medium \
    --num-nodes=3 \
    --enable-autorepair \
    --enable-autoupgrade

# Regional Standard cluster
gcloud container clusters create my-standard-cluster \
    --region=us-central1 \
    --machine-type=e2-medium \
    --num-nodes=1 \
    --node-locations=us-central1-a,us-central1-b,us-central1-c
```

**Decision Matrix:**

| Feature | Autopilot | Standard |
|---------|-----------|----------|
| Node Management | Fully managed by Google | User-managed |
| SSH Access | No | Yes |
| Cost Model | Pay per Pod resources | Pay per node |
| Scaling | Automatic | Manual or auto-configured |
| Machine Types | Auto-selected or ComputeClasses | User-selected |
| Security Hardening | Enabled by default | User-configured |
| Use Case | Production apps, minimal ops | Custom configs, legacy apps |

---

## Creating and Managing Clusters

### Create Clusters

**Autopilot Cluster (Regional):**
```bash
# Basic Autopilot cluster
gcloud container clusters create-auto my-autopilot \
    --region=us-central1

# With VPC and IP ranges
gcloud container clusters create-auto my-autopilot \
    --region=us-central1 \
    --network=my-vpc \
    --subnetwork=my-subnet \
    --cluster-secondary-range-name=pods \
    --services-secondary-range-name=services \
    --enable-private-nodes \
    --enable-private-endpoint \
    --master-ipv4-cidr=172.16.0.0/28
```

**Standard Cluster (Zonal):**
```bash
# Basic Standard cluster
gcloud container clusters create my-standard \
    --zone=us-central1-a \
    --machine-type=e2-medium \
    --num-nodes=3 \
    --disk-size=50 \
    --disk-type=pd-standard

# With advanced options
gcloud container clusters create my-standard \
    --zone=us-central1-a \
    --machine-type=n1-standard-2 \
    --num-nodes=3 \
    --enable-autoscaling \
    --min-nodes=2 \
    --max-nodes=10 \
    --enable-autorepair \
    --enable-autoupgrade \
    --maintenance-window-start=2024-01-01T00:00:00Z \
    --maintenance-window-duration=4h \
    --maintenance-window-recurrence="FREQ=WEEKLY;BYDAY=SU"
```

**Standard Cluster (Regional):**
```bash
# Regional cluster with HA
gcloud container clusters create my-regional \
    --region=us-central1 \
    --machine-type=e2-medium \
    --num-nodes=1 \
    --node-locations=us-central1-a,us-central1-b,us-central1-c
```

### Get Cluster Credentials

After creating a cluster, configure kubectl to use it:

```bash
# Get credentials for zonal cluster
gcloud container clusters get-credentials my-cluster \
    --zone=us-central1-a

# Get credentials for regional cluster
gcloud container clusters get-credentials my-cluster \
    --region=us-central1

# Verify connection
kubectl cluster-info
kubectl get nodes
```

### List Clusters

```bash
# List all clusters
gcloud container clusters list

# List clusters in specific location
gcloud container clusters list --region=us-central1

# Describe cluster details
gcloud container clusters describe my-cluster \
    --region=us-central1
```

### Resize Cluster (Standard Mode)

```bash
# Resize node pool
gcloud container clusters resize my-cluster \
    --num-nodes=5 \
    --zone=us-central1-a

# Resize specific node pool
gcloud container clusters resize my-cluster \
    --node-pool=my-node-pool \
    --num-nodes=5 \
    --zone=us-central1-a
```

### Upgrade Cluster

**Control Plane Upgrade:**
```bash
# List available versions
gcloud container get-server-config --region=us-central1

# Upgrade control plane
gcloud container clusters upgrade my-cluster \
    --master \
    --cluster-version=1.29.1-gke.1425000 \
    --region=us-central1
```

**Node Pool Upgrade:**
```bash
# Upgrade all nodes
gcloud container clusters upgrade my-cluster \
    --region=us-central1

# Upgrade specific node pool
gcloud container clusters upgrade my-cluster \
    --node-pool=my-node-pool \
    --region=us-central1
```

### Delete Cluster

```bash
# Delete cluster
gcloud container clusters delete my-cluster \
    --region=us-central1 \
    --quiet

# Delete without confirmation
gcloud container clusters delete my-cluster \
    --zone=us-central1-a \
    --async
```

---

## Node Pools Management

### What is a Node Pool?

A node pool is a group of nodes within a cluster that all have the same configuration (machine type, disk, service account).

**Node Pool Features:**
- Different machine types per pool (e.g., CPU-optimized, memory-optimized, GPU)
- Independent scaling policies
- Different disk sizes and types
- Separate upgrade schedules

### Create Node Pool

```bash
# Basic node pool
gcloud container node-pools create my-node-pool \
    --cluster=my-cluster \
    --zone=us-central1-a \
    --machine-type=n1-standard-2 \
    --num-nodes=3

# Node pool with autoscaling
gcloud container node-pools create my-scalable-pool \
    --cluster=my-cluster \
    --zone=us-central1-a \
    --machine-type=n1-standard-4 \
    --enable-autoscaling \
    --min-nodes=2 \
    --max-nodes=10 \
    --num-nodes=3

# Node pool with specific disk
gcloud container node-pools create my-pool \
    --cluster=my-cluster \
    --zone=us-central1-a \
    --machine-type=n1-standard-2 \
    --disk-size=100 \
    --disk-type=pd-ssd \
    --num-nodes=3

# Node pool with preemptible VMs
gcloud container node-pools create preemptible-pool \
    --cluster=my-cluster \
    --zone=us-central1-a \
    --machine-type=n1-standard-4 \
    --preemptible \
    --num-nodes=5
```

### List Node Pools

```bash
# List all node pools
gcloud container node-pools list \
    --cluster=my-cluster \
    --zone=us-central1-a

# Describe node pool
gcloud container node-pools describe my-node-pool \
    --cluster=my-cluster \
    --zone=us-central1-a
```

### Update Node Pool

```bash
# Enable autoscaling
gcloud container node-pools update my-node-pool \
    --cluster=my-cluster \
    --zone=us-central1-a \
    --enable-autoscaling \
    --min-nodes=2 \
    --max-nodes=10

# Enable auto-repair and auto-upgrade
gcloud container node-pools update my-node-pool \
    --cluster=my-cluster \
    --zone=us-central1-a \
    --enable-autorepair \
    --enable-autoupgrade
```

### Delete Node Pool

```bash
# Delete node pool
gcloud container node-pools delete my-node-pool \
    --cluster=my-cluster \
    --zone=us-central1-a \
    --quiet
```

---

## Deploying Workloads

### Pods

The smallest deployable unit in Kubernetes. A Pod represents a single instance of a running process.

**Create Pod (Imperative):**
```bash
# Run a simple pod
kubectl run nginx --image=nginx:latest

# Run with port exposed
kubectl run nginx --image=nginx:latest --port=80

# Run with environment variables
kubectl run nginx --image=nginx:latest --env="ENV=production"

# Run interactive pod
kubectl run -it ubuntu --image=ubuntu:latest --restart=Never -- bash
```

**Pod YAML (Declarative):**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
  labels:
    app: nginx
spec:
  containers:
  - name: nginx
    image: nginx:latest
    ports:
    - containerPort: 80
    resources:
      requests:
        cpu: 250m
        memory: 512Mi
      limits:
        cpu: 500m
        memory: 1Gi
```

```bash
# Apply Pod manifest
kubectl apply -f pod.yaml

# Get Pod details
kubectl get pods
kubectl get pod nginx-pod -o wide
kubectl describe pod nginx-pod

# Delete Pod
kubectl delete pod nginx-pod
```

### Deployments

A Deployment manages a replicated application, ensuring a specified number of Pods are running.

**Create Deployment (Imperative):**
```bash
# Create deployment
kubectl create deployment nginx --image=nginx:latest

# Create with replicas
kubectl create deployment nginx --image=nginx:latest --replicas=3

# Create and expose
kubectl create deployment nginx --image=nginx:latest --port=80
kubectl expose deployment nginx --port=80 --target-port=80 --type=LoadBalancer
```

**Deployment YAML (Declarative):**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.21
        ports:
        - containerPort: 80
        resources:
          requests:
            cpu: 250m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 512Mi
```

```bash
# Apply Deployment
kubectl apply -f deployment.yaml

# Get Deployments
kubectl get deployments
kubectl get deployment nginx-deployment -o wide
kubectl describe deployment nginx-deployment

# Scale Deployment
kubectl scale deployment nginx-deployment --replicas=5

# Update image
kubectl set image deployment/nginx-deployment nginx=nginx:1.22

# Rollout status
kubectl rollout status deployment/nginx-deployment

# Rollback
kubectl rollout undo deployment/nginx-deployment

# View rollout history
kubectl rollout history deployment/nginx-deployment
```

### ReplicaSets

A ReplicaSet ensures a specified number of Pod replicas are running at any time. Usually created by Deployments.

```bash
# Get ReplicaSets
kubectl get replicasets
kubectl get rs

# Describe ReplicaSet
kubectl describe replicaset nginx-deployment-5d59d67564
```

### StatefulSets

For stateful applications requiring stable network identities and persistent storage.

**StatefulSet YAML:**
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
        env:
        - name: MYSQL_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mysql-secret
              key: password
        volumeMounts:
        - name: data
          mountPath: /var/lib/mysql
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 10Gi
```

```bash
# Apply StatefulSet
kubectl apply -f statefulset.yaml

# Get StatefulSets
kubectl get statefulsets
kubectl get sts

# Scale StatefulSet
kubectl scale statefulset mysql --replicas=5
```

### DaemonSets

Ensures a copy of a Pod runs on all (or some) nodes in the cluster.

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluentd
spec:
  selector:
    matchLabels:
      name: fluentd
  template:
    metadata:
      labels:
        name: fluentd
    spec:
      containers:
      - name: fluentd
        image: fluent/fluentd:latest
        resources:
          limits:
            memory: 200Mi
          requests:
            cpu: 100m
            memory: 200Mi
```

```bash
# Apply DaemonSet
kubectl apply -f daemonset.yaml

# Get DaemonSets
kubectl get daemonsets
kubectl get ds
```

### Jobs and CronJobs

**Job** - Runs Pods to completion (batch processing):
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: pi-calculation
spec:
  template:
    spec:
      containers:
      - name: pi
        image: perl:5.34
        command: ["perl", "-Mbignum=bpi", "-wle", "print bpi(2000)"]
      restartPolicy: Never
  backoffLimit: 4
```

**CronJob** - Runs Jobs on a schedule:
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: backup-job
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: backup-image:latest
            command: ["/bin/sh", "-c", "backup-script.sh"]
          restartPolicy: OnFailure
```

```bash
# Get Jobs
kubectl get jobs

# Get CronJobs
kubectl get cronjobs

# Manually trigger CronJob
kubectl create job --from=cronjob/backup-job backup-manual
```

---

## Kubernetes Services

### Service Types

**1. ClusterIP (Default)**

Exposes Service on cluster-internal IP. Only accessible within cluster.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-clusterip
spec:
  type: ClusterIP
  selector:
    app: nginx
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
```

```bash
# Create ClusterIP Service
kubectl expose deployment nginx --port=80 --type=ClusterIP

# Test from within cluster
kubectl run test-pod --image=curlimages/curl -it --rm -- curl http://nginx-clusterip
```

**2. NodePort**

Exposes Service on each node's IP at a static port (30000-32767).

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-nodeport
spec:
  type: NodePort
  selector:
    app: nginx
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
    nodePort: 30080  # Optional, let Kubernetes assign if omitted
```

```bash
# Create NodePort Service
kubectl expose deployment nginx --port=80 --type=NodePort

# Get NodePort
kubectl get service nginx-nodeport

# Access via node IP
curl http://<NODE_EXTERNAL_IP>:30080
```

**3. LoadBalancer**

Exposes Service externally using cloud provider's load balancer. Creates external IP.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-loadbalancer
spec:
  type: LoadBalancer
  selector:
    app: nginx
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
```

```bash
# Create LoadBalancer Service
kubectl expose deployment nginx --port=80 --type=LoadBalancer

# Get external IP (may take a few minutes)
kubectl get service nginx-loadbalancer

# Access via external IP
curl http://<EXTERNAL_IP>
```

**4. Headless Service**

For direct Pod-to-Pod communication without load balancing. Used with StatefulSets.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: mysql-headless
spec:
  clusterIP: None
  selector:
    app: mysql
  ports:
  - protocol: TCP
    port: 3306
    targetPort: 3306
```

### Create and Manage Services

```bash
# Create Service from Deployment
kubectl expose deployment nginx --port=80 --type=LoadBalancer

# Create Service from file
kubectl apply -f service.yaml

# Get Services
kubectl get services
kubectl get svc

# Describe Service
kubectl describe service nginx

# Delete Service
kubectl delete service nginx
```

### Ingress

Ingress manages external HTTP/HTTPS access to Services.

**Ingress YAML:**
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nginx-ingress
  annotations:
    kubernetes.io/ingress.class: "gce"
spec:
  rules:
  - host: example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: nginx
            port:
              number: 80
```

```bash
# Apply Ingress
kubectl apply -f ingress.yaml

# Get Ingress
kubectl get ingress

# Describe Ingress
kubectl describe ingress nginx-ingress
```

---

## ConfigMaps and Secrets

### ConfigMaps

Store non-confidential configuration data as key-value pairs.

**Create ConfigMap (Imperative):**
```bash
# From literal values
kubectl create configmap app-config \
    --from-literal=DATABASE_HOST=mysql.example.com \
    --from-literal=DATABASE_PORT=3306

# From file
kubectl create configmap nginx-config --from-file=nginx.conf

# From directory
kubectl create configmap app-configs --from-file=config-dir/
```

**ConfigMap YAML:**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  DATABASE_HOST: "mysql.example.com"
  DATABASE_PORT: "3306"
  APP_ENV: "production"
  config.json: |
    {
      "debug": false,
      "timeout": 30
    }
```

**Use ConfigMap in Pod:**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-pod
spec:
  containers:
  - name: app
    image: myapp:latest
    env:
    # Single environment variable from ConfigMap
    - name: DATABASE_HOST
      valueFrom:
        configMapKeyRef:
          name: app-config
          key: DATABASE_HOST
    # All keys from ConfigMap as environment variables
    envFrom:
    - configMapRef:
        name: app-config
    # Mount ConfigMap as volume
    volumeMounts:
    - name: config-volume
      mountPath: /etc/config
  volumes:
  - name: config-volume
    configMap:
      name: app-config
```

```bash
# Get ConfigMaps
kubectl get configmaps
kubectl get cm

# Describe ConfigMap
kubectl describe configmap app-config

# View ConfigMap data
kubectl get configmap app-config -o yaml

# Delete ConfigMap
kubectl delete configmap app-config
```

### Secrets

Store sensitive data like passwords, tokens, SSH keys.

**Create Secret (Imperative):**
```bash
# Generic secret from literal
kubectl create secret generic db-secret \
    --from-literal=username=admin \
    --from-literal=password=mypassword123

# From file
kubectl create secret generic tls-secret \
    --from-file=tls.crt=server.crt \
    --from-file=tls.key=server.key

# Docker registry secret
kubectl create secret docker-registry gcr-secret \
    --docker-server=gcr.io \
    --docker-username=_json_key \
    --docker-password="$(cat key.json)" \
    --docker-email=user@example.com
```

**Secret YAML:**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
data:
  username: YWRtaW4=       # base64 encoded "admin"
  password: bXlwYXNzd29yZDEyMw==  # base64 encoded "mypassword123"
```

**Encode/Decode Base64:**
```bash
# Encode
echo -n "mypassword123" | base64

# Decode
echo "bXlwYXNzd29yZDEyMw==" | base64 -d
```

**Use Secret in Pod:**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-pod
spec:
  containers:
  - name: app
    image: myapp:latest
    env:
    # Single environment variable from Secret
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: db-secret
          key: password
    # Mount Secret as volume
    volumeMounts:
    - name: secret-volume
      mountPath: /etc/secrets
      readOnly: true
  volumes:
  - name: secret-volume
    secret:
      secretName: db-secret
```

```bash
# Get Secrets
kubectl get secrets

# Describe Secret (won't show data)
kubectl describe secret db-secret

# View Secret data
kubectl get secret db-secret -o yaml

# Delete Secret
kubectl delete secret db-secret
```

---

## Storage in GKE

### Persistent Volumes (PV) and Persistent Volume Claims (PVC)

**PersistentVolumeClaim (PVC):**
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mysql-pvc
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
  storageClassName: standard-rwo
```

**Use PVC in Pod:**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: mysql-pod
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

```bash
# Get PVCs
kubectl get pvc

# Get PVs
kubectl get pv

# Describe PVC
kubectl describe pvc mysql-pvc

# Delete PVC
kubectl delete pvc mysql-pvc
```

### Storage Classes

GKE provides default storage classes for dynamic provisioning:

- **standard-rwo**: Standard persistent disk (HDD), ReadWriteOnce
- **premium-rwo**: SSD persistent disk, ReadWriteOnce
- **standard**: Deprecated, use standard-rwo
- **premium**: Deprecated, use premium-rwo

```bash
# List storage classes
kubectl get storageclass
kubectl get sc

# Describe storage class
kubectl describe storageclass standard-rwo
```

**Custom StorageClass:**
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: kubernetes.io/gce-pd
parameters:
  type: pd-ssd
  replication-type: regional-pd
allowVolumeExpansion: true
```

---

## Monitoring and Logging

### Cloud Logging

GKE automatically collects logs from containers, system components, and audit logs.

**View Logs:**
```bash
# View Pod logs
kubectl logs nginx-pod

# View logs from specific container in multi-container Pod
kubectl logs nginx-pod -c nginx

# Follow logs (stream)
kubectl logs -f nginx-pod

# View previous container logs (if crashed)
kubectl logs nginx-pod --previous

# View logs from all Pods with label
kubectl logs -l app=nginx

# View logs with timestamps
kubectl logs nginx-pod --timestamps

# View last N lines
kubectl logs nginx-pod --tail=100
```

**Cloud Logging (gcloud):**
```bash
# View logs in Cloud Logging
gcloud logging read "resource.type=k8s_container AND resource.labels.pod_name=nginx-pod" \
    --limit=50 \
    --format=json

# Filter by severity
gcloud logging read "resource.type=k8s_container AND severity=ERROR" \
    --limit=20
```

### Cloud Monitoring

GKE integrates with Cloud Monitoring for metrics and alerts.

**View Cluster Metrics:**
```bash
# Get node resource usage
kubectl top nodes

# Get Pod resource usage
kubectl top pods

# Get Pod resource usage in specific namespace
kubectl top pods -n kube-system

# Sort by CPU
kubectl top pods --sort-by=cpu

# Sort by memory
kubectl top pods --sort-by=memory
```

**Metrics Server** (required for `kubectl top`):
```bash
# Check if metrics-server is running
kubectl get deployment metrics-server -n kube-system

# If not available in Standard clusters, install it
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

### Horizontal Pod Autoscaler (HPA)

Automatically scales number of Pods based on CPU/memory utilization or custom metrics.

**Create HPA:**
```bash
# Autoscale based on CPU (target 50%)
kubectl autoscale deployment nginx --cpu-percent=50 --min=2 --max=10

# Autoscale based on memory
kubectl autoscale deployment nginx --memory-percent=70 --min=2 --max=10
```

**HPA YAML:**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: nginx-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: nginx
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 50
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 70
```

```bash
# Get HPA status
kubectl get hpa

# Describe HPA
kubectl describe hpa nginx-hpa

# Delete HPA
kubectl delete hpa nginx-hpa
```

### Cluster Autoscaler (Standard Mode)

Automatically adjusts the number of nodes in a node pool based on Pod resource requests.

```bash
# Enable cluster autoscaler on existing node pool
gcloud container node-pools update my-node-pool \
    --cluster=my-cluster \
    --zone=us-central1-a \
    --enable-autoscaling \
    --min-nodes=2 \
    --max-nodes=10
```

---

## Troubleshooting

### Pod Troubleshooting

**Get Pod Status:**
```bash
# Get all Pods
kubectl get pods
kubectl get pods -o wide

# Get Pods in all namespaces
kubectl get pods --all-namespaces
kubectl get pods -A

# Get Pods with specific label
kubectl get pods -l app=nginx

# Watch Pods (real-time updates)
kubectl get pods -w
```

**Describe Pod:**
```bash
# Detailed Pod information (events, status, containers)
kubectl describe pod nginx-pod

# Check Pod events
kubectl get events --sort-by='.lastTimestamp' | grep nginx-pod
```

**Pod Logs:**
```bash
# View logs
kubectl logs nginx-pod

# Follow logs
kubectl logs -f nginx-pod

# Previous container logs (if crashed)
kubectl logs nginx-pod --previous

# Logs from specific container
kubectl logs nginx-pod -c nginx
```

**Execute Commands in Pod:**
```bash
# Execute command
kubectl exec nginx-pod -- ls /usr/share/nginx/html

# Interactive shell
kubectl exec -it nginx-pod -- /bin/bash
kubectl exec -it nginx-pod -- /bin/sh

# Specific container in multi-container Pod
kubectl exec -it nginx-pod -c nginx -- /bin/bash
```

**Common Pod Issues:**

1. **ImagePullBackOff / ErrImagePull**
   - Image doesn't exist or wrong tag
   - No access to private registry
   - Check: `kubectl describe pod <pod-name>`

2. **CrashLoopBackOff**
   - Application crashes immediately after starting
   - Check logs: `kubectl logs <pod-name> --previous`

3. **Pending**
   - Insufficient resources (CPU, memory)
   - No node available matching constraints
   - Check: `kubectl describe pod <pod-name>`

4. **OOMKilled (Out of Memory)**
   - Container exceeded memory limit
   - Increase memory limits or optimize application

**Debug with Ephemeral Containers:**
```bash
# Add debug container to running Pod (Kubernetes 1.23+)
kubectl debug nginx-pod -it --image=busybox --target=nginx
```

### Service Troubleshooting

**Check Service:**
```bash
# Get Services
kubectl get services

# Describe Service
kubectl describe service nginx

# Check endpoints
kubectl get endpoints nginx
```

**Test Service Connectivity:**
```bash
# From within cluster
kubectl run test-pod --image=curlimages/curl -it --rm -- curl http://nginx.default.svc.cluster.local

# Port-forward to local machine
kubectl port-forward service/nginx 8080:80
# Access via http://localhost:8080
```

### Node Troubleshooting

**Get Node Status:**
```bash
# Get nodes
kubectl get nodes
kubectl get nodes -o wide

# Describe node
kubectl describe node <node-name>

# Check node conditions
kubectl get nodes -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.conditions[?(@.type=="Ready")].status}{"\n"}{end}'
```

**Drain Node (for maintenance):**
```bash
# Drain node (evict all Pods)
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data

# Uncordon node (make schedulable again)
kubectl uncordon <node-name>

# Cordon node (mark unschedulable)
kubectl cordon <node-name>
```

### Cluster Troubleshooting

**Cluster Info:**
```bash
# Cluster information
kubectl cluster-info

# Cluster components
kubectl get componentstatuses
kubectl get cs

# Cluster events
kubectl get events --sort-by='.lastTimestamp'
```

**Namespace Issues:**
```bash
# Get all resources in namespace
kubectl get all -n my-namespace

# Describe namespace
kubectl describe namespace my-namespace

# Delete stuck namespace
kubectl get namespace my-namespace -o json > namespace.json
# Edit namespace.json and remove finalizers
kubectl replace --raw "/api/v1/namespaces/my-namespace/finalize" -f namespace.json
```

---

## Best Practices

### Resource Management

1. **Always Set Resource Requests and Limits**
   ```yaml
   resources:
     requests:
       cpu: 250m
       memory: 512Mi
     limits:
       cpu: 500m
       memory: 1Gi
   ```

2. **Use Namespaces for Isolation**
   ```bash
   kubectl create namespace development
   kubectl create namespace staging
   kubectl create namespace production
   ```

3. **Use Labels and Selectors**
   ```yaml
   metadata:
     labels:
       app: nginx
       environment: production
       tier: frontend
   ```

### Security Best Practices

1. **Use Workload Identity**
   - Avoid storing service account keys in Secrets
   - Bind Kubernetes ServiceAccounts to Google service accounts

2. **Enable Binary Authorization**
   - Only deploy verified container images

3. **Use Network Policies**
   ```yaml
   apiVersion: networking.k8s.io/v1
   kind: NetworkPolicy
   metadata:
     name: deny-all-ingress
   spec:
     podSelector: {}
     policyTypes:
     - Ingress
   ```

4. **Use Pod Security Standards**
   - Apply pod security policies to restrict privileged containers

5. **Regularly Update Clusters**
   - Enable auto-upgrades for control plane and nodes

### High Availability

1. **Use Regional Clusters for Production**
   - 99.95% SLA with replicated control plane

2. **Use Multiple Replicas**
   ```yaml
   spec:
     replicas: 3
   ```

3. **Configure Pod Disruption Budgets**
   ```yaml
   apiVersion: policy/v1
   kind: PodDisruptionBudget
   metadata:
     name: nginx-pdb
   spec:
     minAvailable: 2
     selector:
       matchLabels:
         app: nginx
   ```

4. **Use Anti-Affinity for Pod Distribution**
   ```yaml
   affinity:
     podAntiAffinity:
       requiredDuringSchedulingIgnoredDuringExecution:
       - labelSelector:
           matchExpressions:
           - key: app
             operator: In
             values:
             - nginx
         topologyKey: kubernetes.io/hostname
   ```

### Deployment Strategies

1. **Use Rolling Updates (Default)**
   ```yaml
   spec:
     strategy:
       type: RollingUpdate
       rollingUpdate:
         maxSurge: 1
         maxUnavailable: 1
   ```

2. **Use Readiness and Liveness Probes**
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

3. **Use ConfigMaps and Secrets for Configuration**
   - Don't hardcode configuration in container images

4. **Tag Container Images Properly**
   - Use specific tags, not `latest`
   - Example: `myapp:v1.2.3` instead of `myapp:latest`

### Cost Optimization

1. **Use Autopilot for Variable Workloads**
   - Pay only for Pod resources, not idle nodes

2. **Use Preemptible/Spot VMs for Fault-Tolerant Workloads**
   ```bash
   gcloud container node-pools create preemptible-pool \
       --cluster=my-cluster \
       --preemptible \
       --num-nodes=5
   ```

3. **Enable Cluster Autoscaler**
   - Automatically scale node pools based on demand

4. **Right-Size Resources**
   - Use VPA (Vertical Pod Autoscaler) to recommend resource requests

5. **Use Resource Quotas**
   ```yaml
   apiVersion: v1
   kind: ResourceQuota
   metadata:
     name: compute-quota
     namespace: development
   spec:
     hard:
       requests.cpu: "10"
       requests.memory: 20Gi
       limits.cpu: "20"
       limits.memory: 40Gi
   ```

---

## Common kubectl Commands Reference

### Cluster Management
```bash
# Get cluster info
kubectl cluster-info
kubectl version

# Get credentials
gcloud container clusters get-credentials CLUSTER --region REGION

# View contexts
kubectl config get-contexts
kubectl config use-context CONTEXT
```

### Resource Management
```bash
# Get resources
kubectl get pods|deployments|services|nodes|pv|pvc
kubectl get all
kubectl get all -A

# Describe resource
kubectl describe pod|deployment|service POD_NAME

# Create resource
kubectl create -f file.yaml
kubectl apply -f file.yaml

# Delete resource
kubectl delete pod|deployment|service NAME
kubectl delete -f file.yaml

# Edit resource
kubectl edit pod|deployment|service NAME
```

### Pod Operations
```bash
# Run Pod
kubectl run nginx --image=nginx

# Execute command
kubectl exec POD -- COMMAND
kubectl exec -it POD -- /bin/bash

# View logs
kubectl logs POD
kubectl logs -f POD
kubectl logs POD --previous

# Port forward
kubectl port-forward POD LOCAL_PORT:REMOTE_PORT
kubectl port-forward service/SERVICE LOCAL_PORT:REMOTE_PORT
```

### Scaling
```bash
# Scale deployment
kubectl scale deployment DEPLOYMENT --replicas=5

# Autoscale
kubectl autoscale deployment DEPLOYMENT --min=2 --max=10 --cpu-percent=80
```

### Rollouts
```bash
# Update image
kubectl set image deployment/DEPLOYMENT CONTAINER=IMAGE

# Rollout status
kubectl rollout status deployment/DEPLOYMENT

# Rollout history
kubectl rollout history deployment/DEPLOYMENT

# Rollback
kubectl rollout undo deployment/DEPLOYMENT
```

### Debugging
```bash
# Get events
kubectl get events --sort-by='.lastTimestamp'

# Resource usage
kubectl top nodes
kubectl top pods

# Debug
kubectl debug POD -it --image=busybox
```

---

## Summary

This guide covers essential GKE operations for the Associate Cloud Engineer exam:

✅ **GKE Fundamentals**: Cluster architecture, control plane, nodes, Autopilot vs Standard
✅ **Cluster Management**: Creating, upgrading, resizing, and deleting clusters
✅ **Node Pool Operations**: Creating, scaling, and managing node pools
✅ **Workload Deployment**: Pods, Deployments, ReplicaSets, StatefulSets, DaemonSets, Jobs
✅ **Services & Networking**: ClusterIP, NodePort, LoadBalancer, Headless, Ingress
✅ **Configuration Management**: ConfigMaps, Secrets, environment variables, volumes
✅ **Storage**: PersistentVolumes, PersistentVolumeClaims, StorageClasses
✅ **Monitoring & Logging**: Cloud Logging, Cloud Monitoring, kubectl logs, kubectl top
✅ **Autoscaling**: HPA (Horizontal Pod Autoscaler), Cluster Autoscaler
✅ **Troubleshooting**: Pod debugging, Service connectivity, node issues, logs analysis

**Key Takeaways:**
- Use **Autopilot** for fully managed clusters with automatic scaling and security
- Use **Standard** for custom configurations, node access, and legacy workloads
- Always set **resource requests and limits** for Pods
- Use **regional clusters** for production workloads (99.95% SLA)
- Enable **auto-repair and auto-upgrade** for automated maintenance
- Leverage **kubectl** for all cluster interactions and troubleshooting
- Use **Cloud Logging and Monitoring** for observability
- Implement **HPA and Cluster Autoscaler** for automatic scaling
