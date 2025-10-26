# Module 12: Practice Exams & Mock Scenarios

## 🎯 Overview

This module contains realistic practice exams for both CKA and CKAD certifications. Each exam simulates the actual certification environment with:
- Time-bound scenarios
- Real-world problems
- Command-line only solutions
- Performance-based tasks

---

## 📊 Exam Structure

### CKA Exam (2 hours)
- **Duration**: 120 minutes
- **Questions**: ~15-20 tasks
- **Passing Score**: 66%
- **Environment**: Multiple clusters
- **Focus**: Cluster administration and troubleshooting

### CKAD Exam (2 hours)
- **Duration**: 120 minutes  
- **Questions**: ~15-20 tasks
- **Passing Score**: 66%
- **Environment**: Multiple clusters
- **Focus**: Application deployment and configuration

---

## 🔧 Practice Environment Setup

### Prerequisites

```bash
# Install required tools
brew install kubectl
brew install kind  # or minikube

# Create practice clusters
kind create cluster --name cka-cluster1 --config cluster1-config.yaml
kind create cluster --name cka-cluster2 --config cluster2-config.yaml

# Set up kubectl contexts
kubectl config use-context kind-cka-cluster1
kubectl config rename-context kind-cka-cluster1 cluster1
kubectl config use-context kind-cka-cluster2
kubectl config rename-context kind-cka-cluster2 cluster2
```

### Cluster Configuration Files

**cluster1-config.yaml**:
```yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: cka-cluster1
nodes:
- role: control-plane
- role: worker
- role: worker
networking:
  podSubnet: "10.244.0.0/16"
  serviceSubnet: "10.96.0.0/12"
```

**cluster2-config.yaml**:
```yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: cka-cluster2
nodes:
- role: control-plane
- role: worker
networking:
  podSubnet: "10.245.0.0/16"
  serviceSubnet: "10.97.0.0/12"
```

---

## 📝 CKA Practice Exam 1

**Duration**: 120 minutes
**Passing Score**: 66% (14/20 questions)
**Total Weight**: 100%

### Setup

```bash
# Switch to cluster1
kubectl config use-context cluster1

# Set up aliases (provided in real exam)
alias k=kubectl
alias kn='kubectl config set-context --current --namespace'
```

---

### Question 1: Create a Multi-Container Pod (5%)
**Context**: cluster1
**Namespace**: default

Create a pod named `multi-app` with the following specifications:
- Container 1: `nginx-container` using image `nginx:1.21`
- Container 2: `busybox-container` using image `busybox:1.28`
  - Command: `sleep 3600`
- Labels: `app=multi`, `tier=frontend`
- Both containers should share the same process namespace

**Solution**:
```bash
kubectl run multi-app --image=nginx:1.21 --dry-run=client -o yaml > pod.yaml
```

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: multi-app
  labels:
    app: multi
    tier: frontend
spec:
  shareProcessNamespace: true
  containers:
  - name: nginx-container
    image: nginx:1.21
  - name: busybox-container
    image: busybox:1.28
    command: ['sleep', '3600']
```

```bash
kubectl apply -f pod.yaml
kubectl get pod multi-app
```

---

### Question 2: Create Deployment with Resource Limits (5%)
**Context**: cluster1
**Namespace**: production

Create a namespace called `production` and deploy an nginx application with:
- Deployment name: `web-server`
- Replicas: 3
- Image: `nginx:1.21`
- Container resources:
  - CPU request: 100m
  - CPU limit: 200m
  - Memory request: 128Mi
  - Memory limit: 256Mi
- Environment variable: `ENV=production`

**Solution**:
```bash
kubectl create namespace production
kubectl create deployment web-server --image=nginx:1.21 --replicas=3 -n production --dry-run=client -o yaml > deployment.yaml
```

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-server
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web-server
  template:
    metadata:
      labels:
        app: web-server
    spec:
      containers:
      - name: nginx
        image: nginx:1.21
        env:
        - name: ENV
          value: production
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 200m
            memory: 256Mi
```

```bash
kubectl apply -f deployment.yaml
kubectl get deployment -n production
```

---

### Question 3: Expose Service (4%)
**Context**: cluster1
**Namespace**: production

Expose the `web-server` deployment created in Question 2:
- Service name: `web-service`
- Type: NodePort
- Port: 80
- NodePort: 30080

**Solution**:
```bash
kubectl expose deployment web-server --name=web-service --port=80 --type=NodePort -n production --dry-run=client -o yaml > service.yaml
```

Edit to add nodePort:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: web-service
  namespace: production
spec:
  type: NodePort
  ports:
  - port: 80
    targetPort: 80
    nodePort: 30080
  selector:
    app: web-server
```

```bash
kubectl apply -f service.yaml
kubectl get svc -n production
```

---

### Question 4: Create PersistentVolume and PersistentVolumeClaim (6%)
**Context**: cluster1
**Namespace**: default

Create a PersistentVolume and PersistentVolumeClaim:

**PersistentVolume**:
- Name: `task-pv`
- Capacity: 1Gi
- Access Mode: ReadWriteOnce
- hostPath: `/mnt/data`

**PersistentVolumeClaim**:
- Name: `task-pvc`
- Request: 500Mi
- Access Mode: ReadWriteOnce

**Solution**:
```yaml
# pv.yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: task-pv
spec:
  capacity:
    storage: 1Gi
  accessModes:
  - ReadWriteOnce
  hostPath:
    path: /mnt/data
---
# pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: task-pvc
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 500Mi
```

```bash
kubectl apply -f pv.yaml
kubectl apply -f pvc.yaml
kubectl get pv,pvc
```

---

### Question 5: Troubleshoot Failed Pod (5%)
**Context**: cluster1
**Namespace**: default

A pod named `broken-pod` has been created but is not running. Identify and fix the issue.

**Scenario Setup** (already done):
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: broken-pod
spec:
  containers:
  - name: nginx
    image: nginxxx:latest  # Wrong image name
    resources:
      requests:
        memory: "10000Gi"   # Impossible memory request
```

**Solution**:
```bash
# Check pod status
kubectl get pod broken-pod
kubectl describe pod broken-pod

# Identify issues:
# 1. Image pull error (nginxxx doesn't exist)
# 2. Impossible memory request

# Fix the pod
kubectl delete pod broken-pod
```

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: broken-pod
spec:
  containers:
  - name: nginx
    image: nginx:latest
    resources:
      requests:
        memory: "128Mi"
      limits:
        memory: "256Mi"
```

```bash
kubectl apply -f fixed-pod.yaml
kubectl get pod broken-pod
```

---

### Question 6: Create ConfigMap and Use in Pod (5%)
**Context**: cluster1
**Namespace**: default

Create a ConfigMap named `app-config` with the following data:
- `database_url=postgres://db:5432`
- `cache_enabled=true`
- `log_level=info`

Create a pod named `config-pod` that:
- Uses image `busybox:1.28`
- Mounts the ConfigMap as environment variables
- Runs command: `env` to display environment variables

**Solution**:
```bash
# Create ConfigMap
kubectl create configmap app-config \
  --from-literal=database_url=postgres://db:5432 \
  --from-literal=cache_enabled=true \
  --from-literal=log_level=info

# Verify
kubectl get configmap app-config -o yaml
```

```yaml
# config-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: config-pod
spec:
  containers:
  - name: busybox
    image: busybox:1.28
    command: ['sh', '-c', 'env && sleep 3600']
    envFrom:
    - configMapRef:
        name: app-config
  restartPolicy: Never
```

```bash
kubectl apply -f config-pod.yaml
kubectl logs config-pod | grep -E '(database_url|cache_enabled|log_level)'
```

---

### Question 7: Scale Deployment (3%)
**Context**: cluster1
**Namespace**: production

Scale the `web-server` deployment to 5 replicas and verify all replicas are running.

**Solution**:
```bash
kubectl scale deployment web-server --replicas=5 -n production
kubectl get deployment web-server -n production
kubectl get pods -n production -l app=web-server
```

---

### Question 8: Create NetworkPolicy (6%)
**Context**: cluster1
**Namespace**: production

Create a NetworkPolicy named `deny-all` in the `production` namespace that:
- Denies all ingress traffic to pods with label `app=web-server`
- Allows ingress traffic only from pods with label `role=frontend` on port 80

**Solution**:
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: web-server
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          role: frontend
    ports:
    - protocol: TCP
      port: 80
```

```bash
kubectl apply -f networkpolicy.yaml
kubectl get networkpolicy -n production
```

---

### Question 9: Create ServiceAccount and RBAC (7%)
**Context**: cluster1
**Namespace**: default

Create the following:
1. ServiceAccount named `app-sa`
2. Role named `pod-reader` that can `get`, `list`, and `watch` pods
3. RoleBinding named `read-pods` that binds `pod-reader` role to `app-sa`

**Solution**:
```bash
# Create ServiceAccount
kubectl create serviceaccount app-sa

# Create Role
kubectl create role pod-reader --verb=get,list,watch --resource=pods

# Create RoleBinding
kubectl create rolebinding read-pods --role=pod-reader --serviceaccount=default:app-sa

# Verify
kubectl get sa app-sa
kubectl get role pod-reader
kubectl get rolebinding read-pods
kubectl describe rolebinding read-pods
```

---

### Question 10: Create DaemonSet (5%)
**Context**: cluster1
**Namespace**: kube-system

Create a DaemonSet named `node-monitor` that:
- Runs on all nodes (including control plane if possible)
- Uses image `busybox:1.28`
- Runs command: `sh -c "while true; do date; sleep 60; done"`
- Has label: `app=node-monitor`

**Solution**:
```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: node-monitor
  namespace: kube-system
  labels:
    app: node-monitor
spec:
  selector:
    matchLabels:
      app: node-monitor
  template:
    metadata:
      labels:
        app: node-monitor
    spec:
      tolerations:
      - key: node-role.kubernetes.io/control-plane
        effect: NoSchedule
      containers:
      - name: monitor
        image: busybox:1.28
        command: ['sh', '-c', 'while true; do date; sleep 60; done']
```

```bash
kubectl apply -f daemonset.yaml
kubectl get daemonset -n kube-system node-monitor
kubectl get pods -n kube-system -l app=node-monitor
```

---

### Question 11: Create Job (4%)
**Context**: cluster1
**Namespace**: default

Create a Job named `data-processor` that:
- Uses image `busybox:1.28`
- Runs command: `echo "Processing data..." && sleep 30`
- Completions: 3
- Parallelism: 2
- Restart policy: Never

**Solution**:
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: data-processor
spec:
  completions: 3
  parallelism: 2
  template:
    spec:
      containers:
      - name: processor
        image: busybox:1.28
        command: ['sh', '-c', 'echo "Processing data..." && sleep 30']
      restartPolicy: Never
```

```bash
kubectl apply -f job.yaml
kubectl get jobs
kubectl get pods -l job-name=data-processor
```

---

### Question 12: Create CronJob (4%)
**Context**: cluster1
**Namespace**: default

Create a CronJob named `backup-job` that:
- Runs every day at 2 AM (cron: `0 2 * * *`)
- Uses image `busybox:1.28`
- Runs command: `echo "Backup completed"`
- Keep last 3 successful jobs
- Keep last 1 failed job

**Solution**:
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: backup-job
spec:
  schedule: "0 2 * * *"
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 1
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: busybox:1.28
            command: ['sh', '-c', 'echo "Backup completed"']
          restartPolicy: OnFailure
```

```bash
kubectl apply -f cronjob.yaml
kubectl get cronjob backup-job
# Manually trigger for testing
kubectl create job backup-test --from=cronjob/backup-job
```

---

### Question 13: Node Maintenance - Drain and Cordon (5%)
**Context**: cluster1

Perform maintenance on one of the worker nodes:
1. Identify a worker node
2. Mark it as unschedulable (cordon)
3. Safely evict all pods (drain)
4. Verify no new pods are scheduled on it

**Solution**:
```bash
# List nodes
kubectl get nodes

# Cordon the node
kubectl cordon <worker-node-name>

# Drain the node
kubectl drain <worker-node-name> --ignore-daemonsets --delete-emptydir-data

# Verify
kubectl get nodes
# The node should show SchedulingDisabled

# To bring it back online:
# kubectl uncordon <worker-node-name>
```

---

### Question 14: Create Ingress Resource (6%)
**Context**: cluster1
**Namespace**: production

Assuming an Ingress controller is installed, create an Ingress resource named `web-ingress` that:
- Routes traffic from `app.example.com` to the `web-service` on port 80
- Uses path `/`

**Solution**:
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web-ingress
  namespace: production
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: app.example.com
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

```bash
kubectl apply -f ingress.yaml
kubectl get ingress -n production
kubectl describe ingress web-ingress -n production
```

---

### Question 15: Backup etcd (7%)
**Context**: cluster1

Create a backup of the etcd database and save it to `/tmp/etcd-backup.db`.

**Solution**:
```bash
# Find etcd pod
kubectl get pods -n kube-system -l component=etcd

# Create backup
ETCDCTL_API=3 etcdctl snapshot save /tmp/etcd-backup.db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key

# Verify backup
ETCDCTL_API=3 etcdctl snapshot status /tmp/etcd-backup.db --write-out=table
```

---

### Question 16: Create Secret and Mount in Pod (5%)
**Context**: cluster1
**Namespace**: default

Create a Secret named `db-secret` with:
- `username=admin`
- `password=secret123`

Create a pod named `secret-pod` that:
- Uses image `nginx:1.21`
- Mounts the secret as volume at `/etc/secrets`

**Solution**:
```bash
# Create Secret
kubectl create secret generic db-secret \
  --from-literal=username=admin \
  --from-literal=password=secret123
```

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secret-pod
spec:
  containers:
  - name: nginx
    image: nginx:1.21
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
kubectl apply -f secret-pod.yaml
kubectl exec secret-pod -- ls /etc/secrets
kubectl exec secret-pod -- cat /etc/secrets/username
```

---

### Question 17: Pod Scheduling - Node Affinity (6%)
**Context**: cluster1
**Namespace**: default

Create a pod named `affinity-pod` that:
- Uses image `nginx:1.21`
- Must be scheduled on a node with label `disktype=ssd`
- Label a worker node first with `disktype=ssd`

**Solution**:
```bash
# Label a node
kubectl label node <worker-node-name> disktype=ssd

# Verify label
kubectl get nodes --show-labels | grep disktype
```

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
  containers:
  - name: nginx
    image: nginx:1.21
```

```bash
kubectl apply -f affinity-pod.yaml
kubectl get pod affinity-pod -o wide
```

---

### Question 18: Troubleshoot Service Connectivity (6%)
**Context**: cluster1
**Namespace**: production

A deployment `app-deployment` exists with 3 replicas, but the service `app-service` is not routing traffic correctly. Identify and fix the issue.

**Scenario Setup** (already done):
```yaml
# Deployment has label: app=myapp
# Service selector is: app=wrongapp
```

**Solution**:
```bash
# Check deployment labels
kubectl get deployment app-deployment -n production -o yaml | grep -A5 labels

# Check service selector
kubectl get svc app-service -n production -o yaml | grep -A3 selector

# Identify mismatch
kubectl describe svc app-service -n production
# Look at Endpoints - should be empty or wrong

# Fix the service
kubectl edit svc app-service -n production
# Change selector from app=wrongapp to app=myapp

# Verify endpoints
kubectl get endpoints app-service -n production
kubectl describe svc app-service -n production
```

---

### Question 19: Create StatefulSet (6%)
**Context**: cluster1
**Namespace**: default

Create a StatefulSet named `web-stateful` with:
- Replicas: 3
- Image: `nginx:1.21`
- Service name: `nginx-service`
- Each pod should have a PersistentVolumeClaim requesting 1Gi storage

**Solution**:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  clusterIP: None
  selector:
    app: nginx-stateful
  ports:
  - port: 80
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web-stateful
spec:
  serviceName: nginx-service
  replicas: 3
  selector:
    matchLabels:
      app: nginx-stateful
  template:
    metadata:
      labels:
        app: nginx-stateful
    spec:
      containers:
      - name: nginx
        image: nginx:1.21
        ports:
        - containerPort: 80
        volumeMounts:
        - name: www
          mountPath: /usr/share/nginx/html
  volumeClaimTemplates:
  - metadata:
      name: www
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 1Gi
```

```bash
kubectl apply -f statefulset.yaml
kubectl get statefulset web-stateful
kubectl get pods -l app=nginx-stateful
kubectl get pvc
```

---

### Question 20: Upgrade Cluster (10%)
**Context**: cluster1

Upgrade the cluster from version 1.30.0 to 1.31.0:
1. Upgrade control plane node
2. Upgrade one worker node
3. Verify the upgrade

**Solution**:
```bash
# On control plane node:

# 1. Upgrade kubeadm
sudo apt-mark unhold kubeadm
sudo apt-get update
sudo apt-get install -y kubeadm=1.31.0-00
sudo apt-mark hold kubeadm

# 2. Check upgrade plan
sudo kubeadm upgrade plan

# 3. Apply upgrade
sudo kubeadm upgrade apply v1.31.0 -y

# 4. Drain control plane
kubectl drain <control-plane-node> --ignore-daemonsets

# 5. Upgrade kubelet and kubectl
sudo apt-mark unhold kubelet kubectl
sudo apt-get install -y kubelet=1.31.0-00 kubectl=1.31.0-00
sudo apt-mark hold kubelet kubectl

# 6. Restart kubelet
sudo systemctl daemon-reload
sudo systemctl restart kubelet

# 7. Uncordon node
kubectl uncordon <control-plane-node>

# On worker node:

# 1. Drain from control plane
kubectl drain <worker-node> --ignore-daemonsets --delete-emptydir-data

# 2. On worker node, upgrade kubeadm
sudo apt-mark unhold kubeadm
sudo apt-get update
sudo apt-get install -y kubeadm=1.31.0-00
sudo apt-mark hold kubeadm

# 3. Upgrade node
sudo kubeadm upgrade node

# 4. Upgrade kubelet and kubectl
sudo apt-mark unhold kubelet kubectl
sudo apt-get install -y kubelet=1.31.0-00 kubectl=1.31.0-00
sudo apt-mark hold kubelet kubectl

# 5. Restart kubelet
sudo systemctl daemon-reload
sudo systemctl restart kubelet

# 6. From control plane, uncordon worker
kubectl uncordon <worker-node>

# Verify
kubectl get nodes
```

---

## 📊 Scoring Summary

| Question | Topic | Weight | Time Est. |
|----------|-------|--------|-----------|
| 1 | Multi-container Pod | 5% | 5 min |
| 2 | Deployment with Resources | 5% | 6 min |
| 3 | Service Exposure | 4% | 4 min |
| 4 | Persistent Storage | 6% | 7 min |
| 5 | Troubleshooting | 5% | 6 min |
| 6 | ConfigMap | 5% | 6 min |
| 7 | Scaling | 3% | 3 min |
| 8 | NetworkPolicy | 6% | 7 min |
| 9 | RBAC | 7% | 8 min |
| 10 | DaemonSet | 5% | 6 min |
| 11 | Job | 4% | 5 min |
| 12 | CronJob | 4% | 5 min |
| 13 | Node Maintenance | 5% | 6 min |
| 14 | Ingress | 6% | 7 min |
| 15 | etcd Backup | 7% | 8 min |
| 16 | Secrets | 5% | 6 min |
| 17 | Node Affinity | 6% | 7 min |
| 18 | Service Troubleshooting | 6% | 7 min |
| 19 | StatefulSet | 6% | 8 min |
| 20 | Cluster Upgrade | 10% | 12 min |

**Total**: 100% in 120 minutes

---

## 🎯 Exam Tips

### Time Management
- Spend no more than 7 minutes per question average
- Skip difficult questions and return later
- Always verify your work if time permits

### Command Efficiency
```bash
# Set aliases at start
alias k=kubectl
alias kn='kubectl config set-context --current --namespace'
alias kgp='kubectl get pods'
alias kgs='kubectl get svc'

# Use imperative commands when possible
kubectl run/create/expose --dry-run=client -o yaml

# Use kubectl explain
kubectl explain pod.spec.containers

# Quick debugging
kubectl describe <resource> <name>
kubectl logs <pod>
kubectl get events --sort-by='.lastTimestamp'
```

### Common Pitfalls
1. ❌ Not switching contexts
2. ❌ Wrong namespace
3. ❌ Typos in YAML indentation
4. ❌ Forgetting to apply changes
5. ❌ Not verifying the solution

### Verification Checklist
```bash
✓ Switched to correct context
✓ In correct namespace
✓ Resource created successfully
✓ Resource is in desired state (Running/Ready)
✓ Labels/selectors match
✓ Saved configuration if required
```

---

## 📚 Additional Practice Resources

- **killer.sh**: Official CKA/CKAD simulator (2 sessions included with exam)
- **CKA Practice Exam 2**: [cka-exam-2.md](./cka-exam-2.md)
- **CKA Practice Exam 3**: [cka-exam-3.md](./cka-exam-3.md)
- **CKAD Practice Exam 1**: [ckad-exam-1.md](./ckad-exam-1.md)
- **CKAD Practice Exam 2**: [ckad-exam-2.md](./ckad-exam-2.md)

---

## 🔗 Next Steps

After completing practice exams:
1. Review incorrect answers
2. Practice weak areas
3. Time yourself strictly
4. Simulate exam pressure
5. Book your certification!

**Good luck!** 🍀
