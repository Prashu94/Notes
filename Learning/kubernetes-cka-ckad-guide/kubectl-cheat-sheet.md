# Kubernetes CKA/CKAD Quick Reference & Cheat Sheet

## 🚀 Essential kubectl Commands

### Context and Cluster Management

```bash
# View current context
kubectl config current-context

# List all contexts
kubectl config get-contexts

# Switch context
kubectl config use-context <context-name>

# Set default namespace for current context
kubectl config set-context --current --namespace=<namespace>

# View cluster info
kubectl cluster-info
kubectl cluster-info dump

# Get API resources
kubectl api-resources
kubectl api-versions
```

### Namespace Operations

```bash
# List namespaces
kubectl get namespaces
kubectl get ns

# Create namespace
kubectl create namespace <name>
kubectl create ns <name>

# Delete namespace
kubectl delete namespace <name>

# Set default namespace
kubectl config set-context --current --namespace=<namespace>
```

---

## 📦 Pod Operations

### Create Pods

```bash
# Imperative - run a pod
kubectl run <pod-name> --image=<image>

# With labels
kubectl run <pod-name> --image=<image> --labels="app=web,env=prod"

# With port
kubectl run <pod-name> --image=<image> --port=80

# With environment variables
kubectl run <pod-name> --image=<image> --env="KEY=value"

# With resource limits
kubectl run <pod-name> --image=<image> \
  --requests='cpu=100m,memory=128Mi' \
  --limits='cpu=200m,memory=256Mi'

# With command
kubectl run <pod-name> --image=<image> -- <command> <args>

# Dry run (generate YAML without creating)
kubectl run <pod-name> --image=<image> --dry-run=client -o yaml

# Save to file
kubectl run <pod-name> --image=<image> --dry-run=client -o yaml > pod.yaml
```

### Get Pods

```bash
# List pods
kubectl get pods
kubectl get po

# All namespaces
kubectl get pods --all-namespaces
kubectl get pods -A

# With labels
kubectl get pods --show-labels
kubectl get pods -l app=web
kubectl get pods -l 'env in (prod,staging)'

# Wide output
kubectl get pods -o wide

# YAML output
kubectl get pod <pod-name> -o yaml

# JSON output
kubectl get pod <pod-name> -o json

# Custom columns
kubectl get pods -o custom-columns=NAME:.metadata.name,STATUS:.status.phase

# Watch pods
kubectl get pods -w
```

### Describe and Debug

```bash
# Describe pod
kubectl describe pod <pod-name>

# Get logs
kubectl logs <pod-name>
kubectl logs <pod-name> -c <container-name>  # Multi-container
kubectl logs <pod-name> --previous  # Previous instance
kubectl logs <pod-name> -f  # Follow
kubectl logs <pod-name> --tail=50  # Last 50 lines

# Execute command in pod
kubectl exec <pod-name> -- <command>
kubectl exec -it <pod-name> -- /bin/sh

# For multi-container pods
kubectl exec -it <pod-name> -c <container-name> -- /bin/bash

# Port forward
kubectl port-forward <pod-name> <local-port>:<pod-port>

# Copy files
kubectl cp <pod-name>:<path> <local-path>
kubectl cp <local-path> <pod-name>:<path>
```

### Delete Pods

```bash
# Delete pod
kubectl delete pod <pod-name>

# Force delete
kubectl delete pod <pod-name> --force --grace-period=0

# Delete all pods in namespace
kubectl delete pods --all

# Delete by label
kubectl delete pods -l app=web
```

---

## 🚀 Deployment Operations

### Create Deployments

```bash
# Create deployment
kubectl create deployment <name> --image=<image>

# With replicas
kubectl create deployment <name> --image=<image> --replicas=3

# With port
kubectl create deployment <name> --image=<image> --port=80

# Generate YAML
kubectl create deployment <name> --image=<image> --dry-run=client -o yaml > deploy.yaml
```

### Manage Deployments

```bash
# Get deployments
kubectl get deployments
kubectl get deploy

# Describe deployment
kubectl describe deployment <name>

# Scale deployment
kubectl scale deployment <name> --replicas=5

# Autoscale
kubectl autoscale deployment <name> --min=2 --max=10 --cpu-percent=80

# Update image
kubectl set image deployment/<name> <container>=<new-image>

# Edit deployment
kubectl edit deployment <name>

# Rollout status
kubectl rollout status deployment/<name>

# Rollout history
kubectl rollout history deployment/<name>

# Rollback
kubectl rollout undo deployment/<name>
kubectl rollout undo deployment/<name> --to-revision=2

# Restart deployment
kubectl rollout restart deployment/<name>
```

---

## 🌐 Service Operations

### Create Services

```bash
# Expose deployment
kubectl expose deployment <name> --port=80 --target-port=8080

# ClusterIP (default)
kubectl expose deployment <name> --port=80 --type=ClusterIP

# NodePort
kubectl expose deployment <name> --port=80 --type=NodePort

# LoadBalancer
kubectl expose deployment <name> --port=80 --type=LoadBalancer

# With specific NodePort
kubectl expose deployment <name> --port=80 --type=NodePort --dry-run=client -o yaml > svc.yaml
# Edit YAML to add nodePort: 30080

# Create service from YAML
kubectl create -f service.yaml
```

### Manage Services

```bash
# Get services
kubectl get services
kubectl get svc

# Describe service
kubectl describe svc <name>

# Get endpoints
kubectl get endpoints
kubectl get ep

# Delete service
kubectl delete svc <name>
```

---

## 📝 ConfigMap and Secret

### ConfigMap

```bash
# Create from literals
kubectl create configmap <name> --from-literal=key1=value1 --from-literal=key2=value2

# Create from file
kubectl create configmap <name> --from-file=<file-path>

# Create from directory
kubectl create configmap <name> --from-file=<directory>

# Get ConfigMap
kubectl get configmap
kubectl get cm

# Describe
kubectl describe cm <name>

# Edit
kubectl edit cm <name>

# Delete
kubectl delete cm <name>
```

### Secret

```bash
# Create generic secret
kubectl create secret generic <name> --from-literal=username=admin --from-literal=password=secret

# Create from file
kubectl create secret generic <name> --from-file=<file>

# Create TLS secret
kubectl create secret tls <name> --cert=<cert-file> --key=<key-file>

# Create Docker registry secret
kubectl create secret docker-registry <name> \
  --docker-server=<server> \
  --docker-username=<username> \
  --docker-password=<password> \
  --docker-email=<email>

# Get secrets
kubectl get secrets

# Describe (values are hidden)
kubectl describe secret <name>

# Get secret value
kubectl get secret <name> -o jsonpath='{.data.password}' | base64 -d

# Edit secret
kubectl edit secret <name>
```

---

## 💾 Persistent Volume Operations

### PersistentVolume

```bash
# Get PV
kubectl get pv
kubectl get persistentvolume

# Describe PV
kubectl describe pv <name>

# Delete PV
kubectl delete pv <name>
```

### PersistentVolumeClaim

```bash
# Get PVC
kubectl get pvc
kubectl get persistentvolumeclaim

# Describe PVC
kubectl describe pvc <name>

# Delete PVC
kubectl delete pvc <name>
```

---

## 👥 RBAC (Role-Based Access Control)

### ServiceAccount

```bash
# Create service account
kubectl create serviceaccount <name>
kubectl create sa <name>

# Get service accounts
kubectl get sa

# Get token (Kubernetes 1.24+)
kubectl create token <sa-name>

# Describe
kubectl describe sa <name>
```

### Role and RoleBinding

```bash
# Create Role
kubectl create role <name> --verb=get,list --resource=pods

# Create Role with multiple resources
kubectl create role <name> --verb=get,list,watch --resource=pods,deployments

# Create RoleBinding
kubectl create rolebinding <name> --role=<role-name> --user=<username>

# Bind to ServiceAccount
kubectl create rolebinding <name> --role=<role-name> --serviceaccount=<namespace>:<sa-name>

# Get roles
kubectl get roles

# Get role bindings
kubectl get rolebindings

# Describe
kubectl describe role <name>
kubectl describe rolebinding <name>
```

### ClusterRole and ClusterRoleBinding

```bash
# Create ClusterRole
kubectl create clusterrole <name> --verb=get,list --resource=pods

# Create ClusterRoleBinding
kubectl create clusterrolebinding <name> --clusterrole=<role-name> --user=<username>

# Get cluster roles
kubectl get clusterroles

# Get cluster role bindings
kubectl get clusterrolebindings
```

### Check Permissions

```bash
# Check if you can perform an action
kubectl auth can-i create pods
kubectl auth can-i delete deployments --namespace=production

# Check as another user
kubectl auth can-i get pods --as=<username>

# Check as service account
kubectl auth can-i list pods --as=system:serviceaccount:<namespace>:<sa-name>
```

---

## 🔧 Node Operations

### Node Management

```bash
# Get nodes
kubectl get nodes
kubectl get nodes -o wide

# Describe node
kubectl describe node <node-name>

# Label node
kubectl label node <node-name> <key>=<value>

# Remove label
kubectl label node <node-name> <key>-

# Cordon node (mark unschedulable)
kubectl cordon <node-name>

# Drain node (evict pods)
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data

# Uncordon node (mark schedulable)
kubectl uncordon <node-name>

# Taint node
kubectl taint node <node-name> <key>=<value>:<effect>
# Effects: NoSchedule, PreferNoSchedule, NoExecute

# Remove taint
kubectl taint node <node-name> <key>:<effect>-

# Top nodes (requires metrics-server)
kubectl top nodes
```

---

## 📊 Resource Management

### Resource Quotas

```bash
# Create resource quota
kubectl create quota <name> --hard=pods=10,cpu=1000m,memory=1Gi

# Get quotas
kubectl get resourcequota
kubectl get quota

# Describe quota
kubectl describe quota <name>
```

### LimitRange

```bash
# Get limit ranges
kubectl get limitrange
kubectl get limits

# Describe
kubectl describe limitrange <name>
```

---

## 🔍 Troubleshooting Commands

### Events

```bash
# Get events
kubectl get events

# Sort by time
kubectl get events --sort-by=.metadata.creationTimestamp
kubectl get events --sort-by='.lastTimestamp'

# Filter by type
kubectl get events --field-selector type=Warning

# All namespaces
kubectl get events --all-namespaces

# For specific object
kubectl get events --field-selector involvedObject.name=<pod-name>
```

### Debugging

```bash
# Check pod status
kubectl get pods
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name>
kubectl logs <pod-name> --previous

# Check events
kubectl get events | grep <pod-name>

# Check service endpoints
kubectl get endpoints <service-name>

# Check DNS
kubectl run -it --rm debug --image=busybox:1.28 --restart=Never -- nslookup <service-name>

# Network debugging pod
kubectl run -it --rm debug --image=nicolaka/netshoot --restart=Never -- /bin/bash

# Check node conditions
kubectl describe node <node-name> | grep -A5 Conditions

# Check component status
kubectl get componentstatuses
kubectl get cs

# Check API server
kubectl get --raw /healthz
kubectl get --raw /readyz
```

---

## 📋 YAML Quick Reference

### Pod Template

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
  namespace: default
  labels:
    app: web
  annotations:
    description: "My pod"
spec:
  containers:
  - name: nginx
    image: nginx:1.21
    ports:
    - containerPort: 80
    env:
    - name: ENV_VAR
      value: "value"
    resources:
      requests:
        memory: "128Mi"
        cpu: "100m"
      limits:
        memory: "256Mi"
        cpu: "200m"
    volumeMounts:
    - name: data
      mountPath: /data
  volumes:
  - name: data
    emptyDir: {}
  restartPolicy: Always
  nodeSelector:
    disktype: ssd
```

### Deployment Template

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-deployment
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
      - name: nginx
        image: nginx:1.21
        ports:
        - containerPort: 80
```

### Service Template

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  type: ClusterIP  # ClusterIP, NodePort, LoadBalancer
  selector:
    app: web
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
    # nodePort: 30080  # Only for NodePort type
```

---

## ⏱️ Exam Time-Saving Tips

### Set Aliases

```bash
# Add to ~/.bashrc or run at exam start
alias k=kubectl
alias kn='kubectl config set-context --current --namespace'
alias kgp='kubectl get pods'
alias kgs='kubectl get svc'
alias kgd='kubectl get deployments'
alias kd='kubectl describe'
alias kl='kubectl logs'
alias ke='kubectl exec -it'
alias kap='kubectl apply -f'
alias kdel='kubectl delete'

# Auto-completion
source <(kubectl completion bash)
complete -F __start_kubectl k
```

### Quick YAML Generation

```bash
# Pod
kubectl run <name> --image=<image> --dry-run=client -o yaml > pod.yaml

# Deployment
kubectl create deployment <name> --image=<image> --dry-run=client -o yaml > deploy.yaml

# Service
kubectl expose deployment <name> --port=80 --dry-run=client -o yaml > svc.yaml

# ConfigMap
kubectl create configmap <name> --from-literal=key=value --dry-run=client -o yaml > cm.yaml

# Secret
kubectl create secret generic <name> --from-literal=key=value --dry-run=client -o yaml > secret.yaml

# Job
kubectl create job <name> --image=<image> --dry-run=client -o yaml > job.yaml

# CronJob
kubectl create cronjob <name> --image=<image> --schedule="*/5 * * * *" --dry-run=client -o yaml > cronjob.yaml
```

### Quick Edits

```bash
# Use kubectl explain for field reference
kubectl explain pod.spec
kubectl explain deployment.spec.template.spec.containers

# Edit running resource
kubectl edit <resource> <name>

# Replace resource
kubectl replace -f <file> --force

# Patch resource
kubectl patch <resource> <name> -p '{"spec":{"replicas":3}}'
```

---

## 🎯 Common Exam Scenarios

### Create a Pod Quickly

```bash
# Basic pod
kubectl run nginx --image=nginx

# With environment variable
kubectl run nginx --image=nginx --env="ENV=prod"

# With labels
kubectl run nginx --image=nginx --labels="app=web,tier=frontend"

# With resource limits
kubectl run nginx --image=nginx --requests='cpu=100m,memory=128Mi' --limits='cpu=200m,memory=256Mi'

# With command
kubectl run busybox --image=busybox --command -- sleep 3600

# Interactive
kubectl run -it busybox --image=busybox --restart=Never -- sh
```

### Expose a Deployment

```bash
# ClusterIP
kubectl expose deployment nginx --port=80 --target-port=8080

# NodePort with specific port
kubectl expose deployment nginx --port=80 --type=NodePort --name=nginx-service --dry-run=client -o yaml > svc.yaml
# Edit to add nodePort: 30080
kubectl apply -f svc.yaml
```

### Scale Deployment

```bash
kubectl scale deployment nginx --replicas=5
```

### Update Image

```bash
kubectl set image deployment/nginx nginx=nginx:1.22
```

### Rollback Deployment

```bash
kubectl rollout undo deployment/nginx
```

### Create ConfigMap from File

```bash
echo "key1=value1" > config.txt
kubectl create configmap app-config --from-file=config.txt
```

### Create Secret

```bash
kubectl create secret generic db-secret --from-literal=username=admin --from-literal=password=secret
```

### Drain Node for Maintenance

```bash
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data
# Perform maintenance
kubectl uncordon <node-name>
```

### Backup etcd

```bash
ETCDCTL_API=3 etcdctl snapshot save /tmp/backup.db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key
```

---

## 📖 kubectl explain - Your Best Friend

```bash
# Get field documentation
kubectl explain pod
kubectl explain pod.spec
kubectl explain pod.spec.containers
kubectl explain pod.spec.containers.resources
kubectl explain deployment.spec.template.spec

# Show all fields recursively
kubectl explain pod --recursive

# Specific field
kubectl explain pod.spec.restartPolicy
```

---

## 🔗 Useful Jsonpath Queries

```bash
# Get pod IPs
kubectl get pods -o jsonpath='{.items[*].status.podIP}'

# Get node names
kubectl get nodes -o jsonpath='{.items[*].metadata.name}'

# Get image names
kubectl get pods -o jsonpath='{.items[*].spec.containers[*].image}'

# Custom output
kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.phase}{"\n"}{end}'

# Get secret value
kubectl get secret <name> -o jsonpath='{.data.password}' | base64 -d
```

---

## 📚 Remember

✅ **Always verify context and namespace**
✅ **Use --dry-run=client -o yaml for templates**
✅ **kubectl explain is your documentation**
✅ **Kubernetes.io docs are allowed in exam**
✅ **Practice speed over perfection**
✅ **Skip and come back to difficult questions**

**Good luck with your certification!** 🎉
