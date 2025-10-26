# Module 03: Workloads & Scheduling

## 📋 Learning Objectives

By the end of this module, you will understand:
- Pods and their lifecycle
- Deployments and replica management
- StatefulSets for stateful applications
- DaemonSets for node-level services
- Jobs and CronJobs for batch processing
- Pod scheduling mechanisms
- Resource management and Quality of Service

## 🎯 Exam Relevance

**CKA**: 15% of exam
- Pod lifecycle and scheduling
- Workload controllers
- Resource management

**CKAD**: 40% of exam (Critical!)
- Application deployment
- Multi-container patterns
- Resource configuration

---

## 📦 Pods

### What is a Pod?

A **Pod** is the smallest deployable unit in Kubernetes. It represents a single instance of a running process in your cluster.

**Key Characteristics**:
- One or more containers
- Shared network namespace (single IP)
- Shared storage volumes
- Atomic unit of scheduling
- Ephemeral (disposable and replaceable)

### Pod Lifecycle

```
┌─────────────┐
│   Pending   │ ← Pod created, waiting for scheduling
└─────┬───────┘
      │
      ▼
┌─────────────┐
│  Running    │ ← At least one container running
└─────┬───────┘
      │
      ├─────────────────┐
      │                 │
      ▼                 ▼
┌─────────────┐   ┌─────────────┐
│  Succeeded  │   │   Failed    │
└─────────────┘   └─────────────┘
```

**Pod Phases**:
- **Pending**: Accepted but not yet running
- **Running**: Pod bound to node, containers created
- **Succeeded**: All containers terminated successfully
- **Failed**: All containers terminated, at least one failed
- **Unknown**: Pod state cannot be determined

### Creating Pods

**Method 1: Imperative (Quick)**
```bash
# Basic pod
kubectl run nginx --image=nginx

# With port
kubectl run nginx --image=nginx --port=80

# With environment variables
kubectl run nginx --image=nginx --env="DB_HOST=mysql" --env="DB_PORT=3306"

# With labels
kubectl run nginx --image=nginx --labels="app=web,env=prod"

# With resource limits
kubectl run nginx --image=nginx \
  --requests='cpu=100m,memory=128Mi' \
  --limits='cpu=200m,memory=256Mi'

# With command override
kubectl run busybox --image=busybox --command -- sleep 3600

# Restart policy
kubectl run nginx --image=nginx --restart=Never  # Creates a Pod
kubectl run nginx --image=nginx --restart=OnFailure  # Creates a Job
kubectl run nginx --image=nginx --restart=Always  # Creates a Deployment
```

**Method 2: Declarative (Production)**

```yaml
# simple-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
  namespace: default
  labels:
    app: nginx
    tier: frontend
  annotations:
    description: "Simple nginx pod"
spec:
  containers:
  - name: nginx
    image: nginx:1.21
    ports:
    - containerPort: 80
      name: http
      protocol: TCP
    env:
    - name: ENVIRONMENT
      value: "production"
    resources:
      requests:
        memory: "128Mi"
        cpu: "100m"
      limits:
        memory: "256Mi"
        cpu: "200m"
  restartPolicy: Always
```

```bash
kubectl apply -f simple-pod.yaml
kubectl get pod nginx-pod
kubectl describe pod nginx-pod
kubectl logs nginx-pod
kubectl delete pod nginx-pod
```

### Multi-Container Pods

**Use Cases**:
- **Sidecar**: Helper container (logging, monitoring)
- **Ambassador**: Proxy container for external services
- **Adapter**: Transform output from main container

```yaml
# multi-container-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: multi-container-pod
spec:
  containers:
  # Main application container
  - name: app
    image: nginx:1.21
    ports:
    - containerPort: 80
    volumeMounts:
    - name: shared-logs
      mountPath: /var/log/nginx
  
  # Sidecar: Log processor
  - name: log-processor
    image: busybox:1.28
    command: ['sh', '-c', 'tail -f /var/log/nginx/access.log']
    volumeMounts:
    - name: shared-logs
      mountPath: /var/log/nginx
  
  # Sidecar: Metrics exporter
  - name: metrics-exporter
    image: nginx/nginx-prometheus-exporter:0.9.0
    args:
    - '-nginx.scrape-uri=http://localhost:80/stub_status'
    ports:
    - containerPort: 9113
  
  volumes:
  - name: shared-logs
    emptyDir: {}
```

### Init Containers

Run before main containers, sequentially. Useful for setup tasks.

```yaml
# init-container-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: init-demo
spec:
  # Init containers run first, in order
  initContainers:
  - name: install-dependencies
    image: busybox:1.28
    command: ['sh', '-c', 'echo Installing dependencies && sleep 5']
  
  - name: check-database
    image: busybox:1.28
    command: ['sh', '-c', 'until nslookup mysql-service; do sleep 2; done']
  
  # Main container runs after all init containers succeed
  containers:
  - name: app
    image: nginx:1.21
```

---

## 🚀 Deployments

### What is a Deployment?

A **Deployment** provides declarative updates for Pods and ReplicaSets.

**Benefits**:
- Automated rollouts and rollbacks
- Replica management
- Self-healing
- Scaling
- Update strategies

### Deployment Architecture

```
Deployment
    │
    └─── ReplicaSet (current)
    │        └─── Pod 1
    │        └─── Pod 2
    │        └─── Pod 3
    │
    └─── ReplicaSet (old - being terminated)
             └─── Pod 4 (Terminating)
```

### Creating Deployments

**Imperative**:
```bash
# Create deployment
kubectl create deployment nginx --image=nginx

# With replicas
kubectl create deployment nginx --image=nginx --replicas=3

# With port
kubectl create deployment nginx --image=nginx --port=80 --replicas=3

# Generate YAML
kubectl create deployment nginx --image=nginx --replicas=3 --dry-run=client -o yaml > deployment.yaml
```

**Declarative**:
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
spec:
  replicas: 3
  
  # Selector must match template labels
  selector:
    matchLabels:
      app: nginx
  
  # Update strategy
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1        # Max pods above desired count
      maxUnavailable: 1  # Max pods below desired count
  
  # Pod template
  template:
    metadata:
      labels:
        app: nginx
        version: v1
    spec:
      containers:
      - name: nginx
        image: nginx:1.21
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Managing Deployments

```bash
# Create deployment
kubectl apply -f deployment.yaml

# Get deployments
kubectl get deployments
kubectl get deploy

# Get detailed info
kubectl describe deployment nginx-deployment

# Get ReplicaSets
kubectl get replicasets
kubectl get rs

# Scale deployment
kubectl scale deployment nginx-deployment --replicas=5

# Autoscale
kubectl autoscale deployment nginx-deployment --min=2 --max=10 --cpu-percent=80

# Update image
kubectl set image deployment/nginx-deployment nginx=nginx:1.22

# Edit deployment
kubectl edit deployment nginx-deployment

# Check rollout status
kubectl rollout status deployment/nginx-deployment

# Pause rollout
kubectl rollout pause deployment/nginx-deployment

# Resume rollout
kubectl rollout resume deployment/nginx-deployment

# View rollout history
kubectl rollout history deployment/nginx-deployment

# Rollback to previous version
kubectl rollout undo deployment/nginx-deployment

# Rollback to specific revision
kubectl rollout undo deployment/nginx-deployment --to-revision=2

# Restart deployment (recreate pods)
kubectl rollout restart deployment/nginx-deployment

# Delete deployment
kubectl delete deployment nginx-deployment
```

### Update Strategies

**1. Rolling Update (Default)**
```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 25%        # Max 25% extra pods during update
    maxUnavailable: 25%  # Max 25% unavailable during update
```

**Benefits**:
- Zero downtime
- Gradual rollout
- Easy rollback

**2. Recreate**
```yaml
strategy:
  type: Recreate
```

**Process**:
- Terminate all existing pods
- Create new pods

**Use Case**:
- Application cannot run multiple versions simultaneously
- Downtime is acceptable

---

## 📊 StatefulSets

### What is a StatefulSet?

A **StatefulSet** manages stateful applications with:
- Stable network identities
- Stable persistent storage
- Ordered deployment and scaling
- Ordered rolling updates

### When to Use StatefulSets

✅ **Use StatefulSet for**:
- Databases (MySQL, PostgreSQL, MongoDB)
- Distributed systems (Kafka, Cassandra, ZooKeeper)
- Applications requiring stable network IDs
- Applications needing persistent storage per pod

❌ **Don't use StatefulSet for**:
- Stateless applications (use Deployment)
- Temporary data processing

### StatefulSet Characteristics

```
StatefulSet: web (replicas: 3)
    │
    ├─── web-0 (DNS: web-0.web-service.default.svc.cluster.local)
    │        └─── PVC: data-web-0 (1Gi)
    │
    ├─── web-1 (DNS: web-1.web-service.default.svc.cluster.local)
    │        └─── PVC: data-web-1 (1Gi)
    │
    └─── web-2 (DNS: web-2.web-service.default.svc.cluster.local)
             └─── PVC: data-web-2 (1Gi)
```

**Key Features**:
- Pod names: `<statefulset-name>-<ordinal>` (web-0, web-1, web-2)
- Stable DNS: `<pod-name>.<service-name>.<namespace>.svc.cluster.local`
- Ordered creation: web-0 → web-1 → web-2
- Ordered deletion: web-2 → web-1 → web-0
- Persistent storage: Each pod gets dedicated PVC

### Creating StatefulSets

```yaml
# statefulset.yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
  labels:
    app: nginx
spec:
  ports:
  - port: 80
    name: web
  clusterIP: None  # Headless service
  selector:
    app: nginx
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web
spec:
  serviceName: "nginx-service"  # Governs network identity
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
          name: web
        volumeMounts:
        - name: www
          mountPath: /usr/share/nginx/html
  
  # Volume claim template
  volumeClaimTemplates:
  - metadata:
      name: www
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: "standard"
      resources:
        requests:
          storage: 1Gi
```

### Managing StatefulSets

```bash
# Create StatefulSet
kubectl apply -f statefulset.yaml

# Watch pod creation (ordered)
kubectl get pods -w

# Get StatefulSets
kubectl get statefulsets
kubectl get sts

# Describe
kubectl describe sts web

# Scale
kubectl scale statefulset web --replicas=5

# Update (rolling update)
kubectl set image statefulset/web nginx=nginx:1.22

# Delete (cascading delete)
kubectl delete statefulset web

# Delete without deleting pods
kubectl delete statefulset web --cascade=orphan

# Access specific pod
kubectl exec -it web-0 -- /bin/bash

# Test DNS resolution
kubectl run -it --rm dns-test --image=busybox:1.28 --restart=Never -- nslookup web-0.nginx-service
```

---

## 👿 DaemonSets

### What is a DaemonSet?

A **DaemonSet** ensures that all (or some) nodes run a copy of a Pod.

**Common Use Cases**:
- Node monitoring (Prometheus Node Exporter)
- Log collection (Fluentd, Logstash)
- Storage daemons (Ceph, GlusterFS)
- Network plugins (Calico, Flannel)

### Creating DaemonSets

```yaml
# daemonset.yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: node-exporter
  namespace: monitoring
  labels:
    app: node-exporter
spec:
  selector:
    matchLabels:
      app: node-exporter
  template:
    metadata:
      labels:
        app: node-exporter
    spec:
      # Tolerate control plane taint to run on all nodes
      tolerations:
      - key: node-role.kubernetes.io/control-plane
        effect: NoSchedule
      
      # Use host network
      hostNetwork: true
      hostPID: true
      
      containers:
      - name: node-exporter
        image: prom/node-exporter:latest
        ports:
        - containerPort: 9100
          name: metrics
        securityContext:
          privileged: true
        volumeMounts:
        - name: proc
          mountPath: /host/proc
          readOnly: true
        - name: sys
          mountPath: /host/sys
          readOnly: true
      
      volumes:
      - name: proc
        hostPath:
          path: /proc
      - name: sys
        hostPath:
          path: /sys
```

### Managing DaemonSets

```bash
# Create DaemonSet
kubectl apply -f daemonset.yaml

# Get DaemonSets
kubectl get daemonsets -n monitoring
kubectl get ds -n monitoring

# Describe
kubectl describe ds node-exporter -n monitoring

# Update
kubectl set image daemonset/node-exporter node-exporter=prom/node-exporter:v1.2.0 -n monitoring

# Delete
kubectl delete daemonset node-exporter -n monitoring

# Check which nodes have the DaemonSet pods
kubectl get pods -n monitoring -o wide -l app=node-exporter
```

---

## ⏰ Jobs

### What is a Job?

A **Job** creates one or more Pods and ensures a specified number complete successfully.

**Use Cases**:
- Batch processing
- Data migrations
- One-time tasks
- Backup operations

### Job Types

**1. Single Job (One completion)**
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: single-job
spec:
  template:
    spec:
      containers:
      - name: processor
        image: busybox:1.28
        command: ['sh', '-c', 'echo Processing data && sleep 30 && echo Done']
      restartPolicy: Never
```

**2. Job with Fixed Completions**
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: multiple-completions
spec:
  completions: 5      # Run 5 times successfully
  parallelism: 2      # Run 2 at a time
  template:
    spec:
      containers:
      - name: processor
        image: busybox:1.28
        command: ['sh', '-c', 'echo Processing && sleep 20']
      restartPolicy: Never
```

**3. Work Queue Job**
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: work-queue
spec:
  parallelism: 3      # 3 workers
  # No completions specified - pods continue until queue is empty
  template:
    spec:
      containers:
      - name: worker
        image: gcr.io/my-project/work-queue-processor:v1
      restartPolicy: Never
```

### Managing Jobs

```bash
# Create job
kubectl apply -f job.yaml

# Get jobs
kubectl get jobs

# Watch job progress
kubectl get jobs -w

# Get pods created by job
kubectl get pods -l job-name=single-job

# Check job logs
kubectl logs job/single-job

# Describe job
kubectl describe job single-job

# Delete job (also deletes pods)
kubectl delete job single-job

# Delete job but keep pods
kubectl delete job single-job --cascade=orphan
```

---

## 🔄 CronJobs

### What is a CronJob?

A **CronJob** creates Jobs on a time-based schedule (like cron in Linux).

**Use Cases**:
- Scheduled backups
- Report generation
- Data synchronization
- Cleanup tasks

### CronJob Schedule Format

```
# ┌───────────── minute (0 - 59)
# │ ┌───────────── hour (0 - 23)
# │ │ ┌───────────── day of month (1 - 31)
# │ │ │ ┌───────────── month (1 - 12)
# │ │ │ │ ┌───────────── day of week (0 - 6) (Sunday=0)
# │ │ │ │ │
# * * * * *

# Examples:
0 2 * * *        # Daily at 2 AM
*/15 * * * *     # Every 15 minutes
0 */6 * * *      # Every 6 hours
0 0 * * 0        # Every Sunday at midnight
0 0 1 * *        # First day of every month
```

### Creating CronJobs

```yaml
# cronjob.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: backup-job
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  
  # Job history limits
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 1
  
  # Concurrency policy
  concurrencyPolicy: Forbid  # Forbid, Allow, or Replace
  
  # If job didn't run at scheduled time (node down)
  startingDeadlineSeconds: 300
  
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: backup-image:latest
            command:
            - /bin/sh
            - -c
            - |
              echo "Starting backup at $(date)"
              # Backup commands here
              tar -czf /backup/data-$(date +%Y%m%d).tar.gz /data
              echo "Backup completed at $(date)"
          restartPolicy: OnFailure
```

### Managing CronJobs

```bash
# Create CronJob
kubectl apply -f cronjob.yaml

# Get CronJobs
kubectl get cronjobs
kubectl get cj

# Describe
kubectl describe cronjob backup-job

# Manually trigger (create job from cronjob)
kubectl create job backup-manual --from=cronjob/backup-job

# Suspend CronJob (pause scheduling)
kubectl patch cronjob backup-job -p '{"spec":{"suspend":true}}'

# Resume CronJob
kubectl patch cronjob backup-job -p '{"spec":{"suspend":false}}'

# Edit schedule
kubectl edit cronjob backup-job

# View jobs created by CronJob
kubectl get jobs -l parent-cron=backup-job

# Delete CronJob
kubectl delete cronjob backup-job
```

---

## 📅 Pod Scheduling

### How Scheduling Works

```
1. User creates Pod
2. API Server validates and stores in etcd
3. Scheduler watches for unscheduled pods
4. Scheduler:
   - Filters nodes (predicates)
   - Scores feasible nodes (priorities)
   - Selects best node
5. Binds pod to node
6. kubelet on node creates containers
```

### Node Selection

**1. nodeName (Manual Scheduling)**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx
spec:
  nodeName: worker-node-1  # Directly assign to node
  containers:
  - name: nginx
    image: nginx
```

**2. nodeSelector (Simple Constraint)**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx
spec:
  nodeSelector:
    disktype: ssd        # Node must have this label
    environment: production
  containers:
  - name: nginx
    image: nginx
```

```bash
# Label node first
kubectl label node worker-1 disktype=ssd environment=production
```

**3. Node Affinity (Advanced)**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx
spec:
  affinity:
    nodeAffinity:
      # MUST match (hard requirement)
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: disktype
            operator: In
            values:
            - ssd
      
      # PREFER to match (soft requirement)
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 1
        preference:
          matchExpressions:
          - key: location
            operator: In
            values:
            - us-west
  containers:
  - name: nginx
    image: nginx
```

**4. Pod Affinity/Anti-Affinity**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: web-server
spec:
  affinity:
    # Run on same node as cache pods
    podAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
      - labelSelector:
          matchExpressions:
          - key: app
            operator: In
            values:
            - cache
        topologyKey: kubernetes.io/hostname
    
    # Don't run on same node as other web-server pods
    podAntiAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        podAffinityTerm:
          labelSelector:
            matchExpressions:
            - key: app
              operator: In
              values:
              - web-server
          topologyKey: kubernetes.io/hostname
  containers:
  - name: web
    image: nginx
```

### Taints and Tolerations

**Taints** (on nodes): Repel pods
**Tolerations** (on pods): Allow pods to schedule on tainted nodes

```bash
# Add taint to node
kubectl taint node node1 key=value:NoSchedule

# Taint effects:
# NoSchedule - Don't schedule new pods
# PreferNoSchedule - Try not to schedule
# NoExecute - Evict running pods

# Remove taint
kubectl taint node node1 key:NoSchedule-
```

**Pod with Toleration**:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx
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

## 📊 Resource Management

### Resource Types

**CPU**:
- Measured in cores
- 1 CPU = 1000 millicores (m)
- Example: 500m = 0.5 CPU

**Memory**:
- Measured in bytes
- Units: Ki, Mi, Gi (1024-based)
- Example: 128Mi = 128 Mebibytes

### Requests and Limits

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: resource-demo
spec:
  containers:
  - name: app
    image: nginx
    resources:
      requests:        # Minimum guaranteed
        memory: "128Mi"
        cpu: "100m"
      limits:          # Maximum allowed
        memory: "256Mi"
        cpu: "200m"
```

**What Happens**:
- **Requests**: Scheduler ensures node has this much available
- **Limits**: Container throttled (CPU) or killed (memory) if exceeded

### Quality of Service (QoS) Classes

**1. Guaranteed** (Highest priority)
```yaml
# All containers have requests = limits
resources:
  requests:
    memory: "200Mi"
    cpu: "100m"
  limits:
    memory: "200Mi"
    cpu: "100m"
```

**2. Burstable** (Medium priority)
```yaml
# Has requests, but limits > requests (or no limits)
resources:
  requests:
    memory: "100Mi"
    cpu: "100m"
  limits:
    memory: "200Mi"
    cpu: "200m"
```

**3. BestEffort** (Lowest priority)
```yaml
# No requests or limits specified
# First to be evicted under resource pressure
```

---

## 🎯 Exam Tips

### Speed Commands

```bash
# Quick pod
k run nginx --image=nginx

# Quick deployment
k create deploy nginx --image=nginx --replicas=3

# Quick job
k create job test --image=busybox -- echo "Hello"

# Quick cronjob
k create cronjob test --image=busybox --schedule="*/5 * * * *" -- echo "Hello"

# Scale
k scale deploy nginx --replicas=5

# Update image
k set image deploy/nginx nginx=nginx:1.22

# Rollback
k rollout undo deploy/nginx
```

### Common Patterns

**Multi-container pod**:
```bash
k run multi --image=nginx --dry-run=client -o yaml > pod.yaml
# Edit to add second container
k apply -f pod.yaml
```

**Resource limits**:
```bash
k run nginx --image=nginx --requests='cpu=100m,memory=128Mi' --limits='cpu=200m,memory=256Mi'
```

**Node selector**:
```bash
kubectl label node <node> disktype=ssd
# Add nodeSelector to pod spec
```

---

## 📝 Practice Exercises

Complete exercises in [exercises/exercises.md](./exercises/exercises.md)

---

**Next Module**: [04 - Services & Networking](../04-services-networking/README.md)
