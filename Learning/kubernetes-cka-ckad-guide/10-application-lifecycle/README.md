# Module 10: Application Lifecycle Management

## 📚 Overview

Manage application deployments, updates, scaling, and rollbacks in Kubernetes.

**Exam Weight**: CKA (8%), CKAD (20%)

---

## Deployment Strategies

### Rolling Update (Default)

Gradually replaces old pods with new ones.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rolling-app
spec:
  replicas: 4
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1        # Max pods above desired count
      maxUnavailable: 1   # Max pods unavailable during update
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
        - name: app
          image: nginx:1.21
```

**maxSurge**: How many extra pods can be created (1 or 25%)
**maxUnavailable**: How many pods can be unavailable (1 or 25%)

### Recreate Strategy

Terminates all existing pods before creating new ones.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: recreate-app
spec:
  replicas: 3
  strategy:
    type: Recreate  # All pods terminated, then new ones created
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
        - name: app
          image: nginx:1.22
```

**Use case**: When running multiple versions simultaneously causes issues.

---

## Updating Deployments

### Update Image

```bash
# Update image
kubectl set image deployment/nginx nginx=nginx:1.22

# Update with record (saves rollout history)
kubectl set image deployment/nginx nginx=nginx:1.22 --record

# Edit deployment
kubectl edit deployment nginx

# Apply updated YAML
kubectl apply -f deployment.yaml
```

### Check Rollout Status

```bash
# Watch rollout
kubectl rollout status deployment/nginx

# Check rollout history
kubectl rollout history deployment/nginx

# Check specific revision
kubectl rollout history deployment/nginx --revision=2
```

### Pause and Resume Rollout

```bash
# Pause (useful for making multiple changes)
kubectl rollout pause deployment/nginx

# Make changes
kubectl set image deployment/nginx nginx=nginx:1.22
kubectl set resources deployment/nginx -c=nginx --limits=cpu=200m,memory=512Mi

# Resume
kubectl rollout resume deployment/nginx
```

---

## Rollbacks

### Undo Rollout

```bash
# Rollback to previous revision
kubectl rollout undo deployment/nginx

# Rollback to specific revision
kubectl rollout undo deployment/nginx --to-revision=2

# Check status
kubectl rollout status deployment/nginx
```

### Rollback Strategy

1. **Check current status**:
   ```bash
   kubectl rollout status deployment/nginx
   kubectl get pods
   ```

2. **View history**:
   ```bash
   kubectl rollout history deployment/nginx
   ```

3. **Rollback**:
   ```bash
   kubectl rollout undo deployment/nginx
   ```

4. **Verify**:
   ```bash
   kubectl get pods
   kubectl rollout status deployment/nginx
   ```

---

## Scaling

### Manual Scaling

```bash
# Scale deployment
kubectl scale deployment nginx --replicas=5

# Scale multiple deployments
kubectl scale deployment nginx redis --replicas=3

# Scale based on current count
kubectl scale deployment nginx --current-replicas=3 --replicas=5
```

### Horizontal Pod Autoscaler (HPA)

Automatically scales based on CPU/memory/custom metrics.

**Prerequisites**: Metrics Server must be installed

```bash
# Install Metrics Server
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

**Create HPA**:
```bash
# Autoscale based on CPU
kubectl autoscale deployment nginx --cpu-percent=50 --min=2 --max=10

# Check HPA
kubectl get hpa
kubectl describe hpa nginx
```

**HPA YAML**:
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

**Test HPA**:
```bash
# Generate load
kubectl run -i --tty load-generator --rm --image=busybox --restart=Never -- /bin/sh -c "while sleep 0.01; do wget -q -O- http://nginx; done"

# Watch scaling
kubectl get hpa nginx --watch
kubectl get deployment nginx --watch
```

**Delete HPA**:
```bash
kubectl delete hpa nginx
```

---

## Resource Management

### Resource Requests and Limits

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: resource-pod
spec:
  containers:
    - name: app
      image: nginx
      resources:
        requests:
          memory: "64Mi"
          cpu: "250m"
        limits:
          memory: "128Mi"
          cpu: "500m"
```

**requests**: Minimum guaranteed resources
**limits**: Maximum allowed resources

**CPU Units**:
- 1 CPU = 1000m (millicores)
- 500m = 0.5 CPU = half a core

**Memory Units**:
- Mi = Mebibyte (1024²)
- Gi = Gibibyte (1024³)

### LimitRange

Set default limits for namespace:

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: resource-limits
  namespace: default
spec:
  limits:
    - max:
        cpu: "2"
        memory: "2Gi"
      min:
        cpu: "100m"
        memory: "64Mi"
      default:
        cpu: "500m"
        memory: "512Mi"
      defaultRequest:
        cpu: "250m"
        memory: "256Mi"
      type: Container
```

### ResourceQuota

Limit total resources in namespace:

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: namespace-quota
  namespace: development
spec:
  hard:
    requests.cpu: "4"
    requests.memory: "8Gi"
    limits.cpu: "8"
    limits.memory: "16Gi"
    pods: "20"
    services: "10"
    persistentvolumeclaims: "10"
```

**Check quota**:
```bash
kubectl get resourcequota -n development
kubectl describe resourcequota namespace-quota -n development
```

---

## Jobs and CronJobs

### Jobs

Run pods to completion:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: batch-job
spec:
  completions: 3         # Number of successful completions
  parallelism: 2         # Number of pods running in parallel
  backoffLimit: 4        # Number of retries before marking failed
  template:
    spec:
      restartPolicy: OnFailure
      containers:
        - name: worker
          image: busybox
          command: ["sh", "-c", "echo Processing...; sleep 30; echo Done"]
```

**Create job**:
```bash
# From YAML
kubectl apply -f job.yaml

# Imperative
kubectl create job test --image=busybox -- echo "Hello"

# Check job
kubectl get jobs
kubectl describe job batch-job

# View pods
kubectl get pods

# View logs
kubectl logs job/batch-job
```

**Delete job**:
```bash
kubectl delete job batch-job

# Delete with pods
kubectl delete job batch-job --cascade=foreground
```

### CronJobs

Schedule jobs:

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: scheduled-job
spec:
  schedule: "*/5 * * * *"     # Every 5 minutes
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: OnFailure
          containers:
            - name: worker
              image: busybox
              command: ["sh", "-c", "date; echo Scheduled task completed"]
```

**Cron syntax**:
```
# ┌───────────── minute (0 - 59)
# │ ┌───────────── hour (0 - 23)
# │ │ ┌───────────── day of month (1 - 31)
# │ │ │ ┌───────────── month (1 - 12)
# │ │ │ │ ┌───────────── day of week (0 - 6) (Sunday=0)
# │ │ │ │ │
# * * * * *

Examples:
0 * * * *     # Every hour
*/30 * * * *  # Every 30 minutes
0 9 * * *     # Every day at 9 AM
0 0 * * 0     # Every Sunday at midnight
```

**Create CronJob**:
```bash
# From YAML
kubectl apply -f cronjob.yaml

# Imperative
kubectl create cronjob test --image=busybox --schedule="*/1 * * * *" -- echo "Hello"

# Check CronJob
kubectl get cronjobs
kubectl describe cronjob scheduled-job

# View jobs created
kubectl get jobs

# Manually trigger
kubectl create job manual-run --from=cronjob/scheduled-job
```

**CronJob Options**:
```yaml
spec:
  schedule: "0 * * * *"
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 1
  concurrencyPolicy: Allow  # Allow, Forbid, Replace
  startingDeadlineSeconds: 60
  suspend: false  # Pause cron job
```

---

## Application Self-Healing

### Restart Policies

```yaml
spec:
  restartPolicy: Always  # Always, OnFailure, Never
```

- **Always**: Default for Deployments/StatefulSets
- **OnFailure**: For Jobs
- **Never**: For one-time tasks

### Liveness and Readiness Probes

See [Module 08: Health Probes](../08-observability-debugging/README.md#health-probes)

### Pod Disruption Budgets (PDB)

Ensure minimum pods available during voluntary disruptions:

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: app-pdb
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: myapp
```

Or with percentage:

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: app-pdb
spec:
  maxUnavailable: "25%"
  selector:
    matchLabels:
      app: myapp
```

**Check PDB**:
```bash
kubectl get pdb
kubectl describe pdb app-pdb
```

---

## Init Containers

Run before main containers:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: init-pod
spec:
  initContainers:
    - name: init-db
      image: busybox
      command: ['sh', '-c', 'until nslookup mydb; do echo waiting for mydb; sleep 2; done']
    - name: init-config
      image: busybox
      command: ['sh', '-c', 'echo "Config setup"; sleep 10']
  containers:
    - name: app
      image: nginx
```

**Use cases**:
- Wait for services
- Setup configuration
- Clone git repos
- Register with external services

---

## Exam Tips

**Quick Commands**:
```bash
# Deployments
kubectl create deployment nginx --image=nginx:1.21 --replicas=3
kubectl scale deployment nginx --replicas=5
kubectl set image deployment/nginx nginx=nginx:1.22
kubectl rollout status deployment/nginx
kubectl rollout history deployment/nginx
kubectl rollout undo deployment/nginx

# HPA
kubectl autoscale deployment nginx --cpu-percent=50 --min=2 --max=10
kubectl get hpa

# Jobs
kubectl create job test --image=busybox -- echo "Hello"
kubectl get jobs

# CronJobs
kubectl create cronjob test --image=busybox --schedule="*/5 * * * *" -- date
kubectl get cronjobs

# Resources
kubectl top nodes
kubectl top pods
```

**Common Tasks**:
1. Create deployment and scale it
2. Update deployment image
3. Rollback deployment
4. Create HPA for autoscaling
5. Create Job for batch processing
6. Create CronJob for scheduled tasks
7. Set resource requests and limits
8. Create PodDisruptionBudget

**Deployment Template**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
        - name: app
          image: nginx:1.21
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 200m
              memory: 256Mi
```

---

## Summary

**Deployment Strategies**:
- **RollingUpdate**: Gradual replacement (default)
- **Recreate**: Terminate all, then create

**Updates & Rollbacks**:
- `kubectl set image`: Update image
- `kubectl rollout undo`: Rollback
- `kubectl rollout status`: Check progress

**Scaling**:
- Manual: `kubectl scale`
- Automatic: HorizontalPodAutoscaler (HPA)

**Resource Management**:
- **Requests**: Minimum guaranteed
- **Limits**: Maximum allowed
- **LimitRange**: Namespace defaults
- **ResourceQuota**: Namespace limits

**Jobs**:
- One-time tasks
- Batch processing
- Scheduled with CronJobs

**Self-Healing**:
- Restart policies
- Health probes
- Pod Disruption Budgets

**Next Module**: [Module 11: Advanced Topics →](../11-advanced-topics/README.md)
