# Module 01: Exercise Solutions - Kubernetes Architecture & Fundamentals

## Exercise 1: Cluster Component Inspection ⭐

### Solution:

```bash
# 1. List all pods in kube-system namespace
kubectl get pods -n kube-system

# Expected output: Control plane pods and add-ons
# - kube-apiserver-*
# - etcd-*
# - kube-scheduler-*
# - kube-controller-manager-*
# - kube-proxy-*
# - coredns-*

# 2. Identify control plane components
kubectl get pods -n kube-system -l tier=control-plane

# 3. Check component status
kubectl get componentstatuses
# or
kubectl get cs

# Expected output:
# NAME                 STATUS    MESSAGE             ERROR
# scheduler            Healthy   ok                  
# controller-manager   Healthy   ok                  
# etcd-0               Healthy   {"health":"true"}

# 4. Find Kubernetes version
kubectl version --short

# Alternative:
kubectl get nodes -o wide

# 5. List all nodes with roles
kubectl get nodes

# More detailed:
kubectl get nodes -o wide
```

### Report Template:
```
Cluster Health Report
===================
Date: [Current Date]

Control Plane Components:
- API Server: Running (Pod: kube-apiserver-node1)
- etcd: Running (Pod: etcd-node1)
- Scheduler: Running (Pod: kube-scheduler-node1)
- Controller Manager: Running (Pod: kube-controller-manager-node1)

Kubernetes Version: v1.31.0

Nodes:
- node1 (control-plane): Ready
- node2 (worker): Ready
- node3 (worker): Ready

All components healthy ✓
```

---

## Exercise 2: API Resource Discovery ⭐

### Solution:

```bash
# 1. List all API resources
kubectl api-resources

# 2. Find resources in 'apps' API group
kubectl api-resources --api-group=apps

# Expected output:
# NAME                  SHORTNAMES   APIVERSION   NAMESPACED   KIND
# controllerrevisions                apps/v1      true         ControllerRevision
# daemonsets            ds           apps/v1      true         DaemonSet
# deployments           deploy       apps/v1      true         Deployment
# replicasets           rs           apps/v1      true         ReplicaSet
# statefulsets          sts          apps/v1      true         StatefulSet

# 3. Get full API documentation for Deployment
kubectl explain deployment
kubectl explain deployment --recursive

# Get specific field
kubectl explain deployment.spec

# 4. List all API versions
kubectl api-versions

# 5. Show detailed structure of Pod.spec.containers
kubectl explain pod.spec.containers
kubectl explain pod.spec.containers.resources
kubectl explain pod.spec.containers.env
```

### Key Findings:
```yaml
API Groups and Resources:
- Core API (v1): pods, services, configmaps, secrets
- apps/v1: deployments, statefulsets, daemonsets
- batch/v1: jobs, cronjobs
- networking.k8s.io/v1: networkpolicies, ingresses
- storage.k8s.io/v1: storageclasses
- rbac.authorization.k8s.io/v1: roles, rolebindings
```

---

## Exercise 3: Component Log Analysis ⭐⭐

### Solution:

```bash
# 1. View API server logs
kubectl logs -n kube-system kube-apiserver-$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}')

# Alternative for systems with static pods:
sudo cat /var/log/pods/kube-system_kube-apiserver-*/kube-apiserver/*.log

# 2. View scheduler logs
kubectl logs -n kube-system kube-scheduler-$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}')

# 3. View controller manager logs
kubectl logs -n kube-system kube-controller-manager-$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}')

# 4. View CoreDNS logs
kubectl logs -n kube-system -l k8s-app=kube-dns

# 5. Check for errors
kubectl logs -n kube-system kube-apiserver-$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}') | grep -i error

# Get logs from all control plane components
for component in kube-apiserver kube-scheduler kube-controller-manager; do
    echo "=== $component logs ==="
    kubectl logs -n kube-system ${component}-$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}') --tail=20
done
```

### Answers to Questions:

**Q: What port is the API server listening on?**
```bash
kubectl logs -n kube-system kube-apiserver-* | grep "Serving securely"
# Answer: Port 6443 (HTTPS)
```

**Q: How many leader election attempts?**
```bash
kubectl logs -n kube-system kube-controller-manager-* | grep "leader election"
# Look for messages about acquiring or renewing leader lease
```

**Q: Failed scheduling attempts?**
```bash
kubectl logs -n kube-system kube-scheduler-* | grep -i "failed\|error"
# Check for "Failed to schedule pod" or "no nodes available"
```

---

## Exercise 4: etcd Inspection ⭐⭐

### Solution:

```bash
# 1. Check etcd pod health
kubectl get pods -n kube-system -l component=etcd

# Using etcdctl
ETCDCTL_API=3 etcdctl \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  endpoint health

# 2. List all keys in etcd
ETCDCTL_API=3 etcdctl \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  get / --prefix --keys-only

# 3. Find pod information
ETCDCTL_API=3 etcdctl \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  get /registry/pods --prefix --keys-only

# 4. Count keys
ETCDCTL_API=3 etcdctl \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  get / --prefix --keys-only | wc -l

# 5. Identify etcd data directory
kubectl describe pod -n kube-system etcd-* | grep data-dir
# Default: /var/lib/etcd
```

### Key Structure in etcd:
```
/registry/
  /pods/{namespace}/{pod-name}
  /services/{namespace}/{service-name}
  /deployments/{namespace}/{deployment-name}
  /configmaps/{namespace}/{configmap-name}
  /secrets/{namespace}/{secret-name}
  /namespaces/{namespace-name}
```

---

## Exercise 5: Node Component Analysis ⭐⭐

### Solution:

```bash
# 1. Find kubelet configuration file
# Check kubelet process for config location
ps aux | grep kubelet | grep config

# Common locations:
cat /var/lib/kubelet/config.yaml

# 2. Check kubelet service status
systemctl status kubelet

# View kubelet service file
systemctl cat kubelet

# 3. Identify container runtime
kubectl get nodes -o wide
# Check CONTAINER-RUNTIME column

# Or check kubelet config
cat /var/lib/kubelet/config.yaml | grep containerRuntime

# Using crictl
sudo crictl info | grep runtimeType

# 4. Check kube-proxy mode
kubectl logs -n kube-system kube-proxy-<pod-name> | grep "Using"
# or
kubectl describe cm -n kube-system kube-proxy | grep mode

# 5. List all containers on node
# Using containerd
sudo ctr -n k8s.io containers list

# Using crictl (recommended)
sudo crictl ps

# Using docker (if available)
sudo docker ps
```

### Example Output:
```yaml
Kubelet Configuration:
  Config File: /var/lib/kubelet/config.yaml
  Status: Active (running)
  Container Runtime: containerd://1.7.2
  
Kube-proxy Mode: iptables

Running Containers: 15
  - System pods: 10
  - Application pods: 5
```

---

## Exercise 6: Static Pod Creation ⭐⭐

### Solution:

```bash
# 1. Find static pod manifest directory
cat /var/lib/kubelet/config.yaml | grep staticPodPath
# Default: /etc/kubernetes/manifests/

# 2. List all static pod manifests
ls -la /etc/kubernetes/manifests/

# Expected files:
# - kube-apiserver.yaml
# - etcd.yaml
# - kube-scheduler.yaml
# - kube-controller-manager.yaml

# 3. Identify static pod components
kubectl get pods -n kube-system -o wide | grep $(hostname)

# 4. Create custom static pod
sudo vi /etc/kubernetes/manifests/nginx-static.yaml
```

### Static Pod Manifest (nginx-static.yaml):
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-static
  namespace: default
spec:
  containers:
  - name: nginx
    image: nginx:1.21
    ports:
    - containerPort: 80
```

```bash
# 5. Verify static pod is running
kubectl get pods

# Pod name will be: nginx-static-<node-name>

# Try to delete it
kubectl delete pod nginx-static-<node-name>
# It will be recreated automatically by kubelet!

# To permanently delete, remove the manifest file
sudo rm /etc/kubernetes/manifests/nginx-static.yaml
```

### Key Points:
- Static pods are created by kubelet from manifests in `staticPodPath`
- Cannot be managed by API server directly
- Useful for running system components
- Pod name includes node name as suffix
- Mirror pod appears in API server (read-only)

---

## Exercise 7: Scheduler Behavior ⭐⭐⭐

### Solution:

```bash
# 1. Create a normal pod
kubectl run test-pod --image=nginx

# 2. Watch it being scheduled
kubectl get pods -w

# Check scheduling event
kubectl describe pod test-pod | grep -A 5 Events

# 3. Create pod with excessive resources
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: large-resources-pod
spec:
  containers:
  - name: stress
    image: polinux/stress
    resources:
      requests:
        memory: "100Gi"
        cpu: "50"
EOF

# 4. Observe Pending state
kubectl get pods large-resources-pod
# STATUS: Pending

# 5. Describe to see scheduler events
kubectl describe pod large-resources-pod
```

### Expected Events:
```
Events:
  Type     Reason            Message
  ----     ------            -------
  Warning  FailedScheduling  0/3 nodes are available: 
                             3 Insufficient cpu, 3 Insufficient memory.
```

### Answers to Questions:

**Q: What scheduler events do you see?**
```
FailedScheduling events showing:
- No nodes with sufficient CPU
- No nodes with sufficient memory
- Predicate failed for all nodes
```

**Q: Why is the pod not scheduled?**
```
The pod requests:
- 100Gi memory
- 50 CPUs

But cluster nodes have much less capacity.
Scheduler cannot find a feasible node.
```

**Q: How to fix?**
```bash
# Option 1: Reduce resource requests
kubectl edit pod large-resources-pod
# Modify resources.requests to reasonable values

# Option 2: Delete and recreate
kubectl delete pod large-resources-pod

kubectl run test-pod --image=nginx \
  --requests='cpu=100m,memory=128Mi' \
  --limits='cpu=200m,memory=256Mi'
```

---

## Exercise 8: Controller Manager Deep Dive ⭐⭐⭐

### Solution:

```bash
# 1. Create deployment with 3 replicas
kubectl create deployment nginx --image=nginx --replicas=3

# Verify pods
kubectl get pods -l app=nginx
kubectl get rs

# 2. Delete one pod manually
POD_NAME=$(kubectl get pods -l app=nginx -o jsonpath='{.items[0].metadata.name}')
kubectl delete pod $POD_NAME

# 3. Watch new pod creation
kubectl get pods -l app=nginx -w

# 4. Scale deployment
kubectl scale deployment nginx --replicas=5

# Watch scaling
kubectl get pods -l app=nginx -w

# 5. Check controller manager logs
kubectl logs -n kube-system kube-controller-manager-* --tail=50 | grep -i replica

# Alternative: Watch ReplicaSet controller
kubectl get events --sort-by='.lastTimestamp' | grep -i scaled
```

### Detailed Analysis:

```bash
# Create a script to measure reconciliation time
cat <<'EOF' > test-reconciliation.sh
#!/bin/bash

echo "Creating deployment..."
kubectl create deployment nginx --image=nginx --replicas=3
sleep 5

echo "Deleting one pod at $(date +%T)"
POD=$(kubectl get pods -l app=nginx -o jsonpath='{.items[0].metadata.name}')
kubectl delete pod $POD

echo "Monitoring pod recreation..."
while true; do
    COUNT=$(kubectl get pods -l app=nginx --field-selector=status.phase=Running | grep -c nginx)
    echo "$(date +%T): Running pods: $COUNT"
    if [ $COUNT -eq 3 ]; then
        echo "All pods back to desired state!"
        break
    fi
    sleep 1
done

kubectl delete deployment nginx
EOF

chmod +x test-reconciliation.sh
./test-reconciliation.sh
```

### Answers to Questions:

**Q: Which controller created the new pod?**
```
The ReplicaSet Controller (part of controller manager)
- Monitors ReplicaSet objects
- Ensures desired replica count matches actual count
- Creates/deletes pods as needed
```

**Q: How long to detect and fix?**
```bash
# Typically 1-2 seconds
# Factors affecting speed:
# - Controller sync period (default: 30s)
# - API watch latency
# - Pod creation time

# Check events for timing
kubectl get events --sort-by='.lastTimestamp' | grep -i scaled
```

**Q: What happens with multiple deletions?**
```bash
# Test it:
kubectl create deployment nginx --image=nginx --replicas=5

# Delete multiple pods simultaneously
kubectl get pods -l app=nginx -o name | head -3 | xargs kubectl delete

# Result: Controller detects all deletions and creates 3 new pods
# Usually happens within 1-2 seconds
```

---

## Exercise 9: API Server Authentication Flow ⭐⭐⭐

### Solution:

```bash
# 1. View kubeconfig
cat ~/.kube/config

# Or formatted:
kubectl config view

# 2. Identify certificates
kubectl config view --raw

# Extract specific fields:
kubectl config view --raw -o jsonpath='{.users[0].user.client-certificate-data}'

# 3. Make raw API request

# Get cluster info
API_SERVER=$(kubectl config view --minify -o jsonpath='{.clusters[0].cluster.server}')

# Extract certificates
kubectl config view --raw -o jsonpath='{.users[0].user.client-certificate-data}' | base64 -d > /tmp/client.crt
kubectl config view --raw -o jsonpath='{.users[0].user.client-key-data}' | base64 -d > /tmp/client.key
kubectl config view --raw -o jsonpath='{.clusters[0].cluster.certificate-authority-data}' | base64 -d > /tmp/ca.crt

# Make authenticated request
curl --cert /tmp/client.crt \
     --key /tmp/client.key \
     --cacert /tmp/ca.crt \
     $API_SERVER/api/v1/namespaces

# 4. Try without authentication
curl -k $API_SERVER/api/v1/namespaces
# Expected: 403 Forbidden or authentication required

# 5. Create service account and get token
kubectl create serviceaccount demo-sa

# Get token (Kubernetes 1.24+)
kubectl create token demo-sa

# Or create token secret manually
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Secret
metadata:
  name: demo-sa-token
  annotations:
    kubernetes.io/service-account.name: demo-sa
type: kubernetes.io/service-account-token
EOF

# Get token
TOKEN=$(kubectl get secret demo-sa-token -o jsonpath='{.data.token}' | base64 -d)

# Use token to access API
curl -k -H "Authorization: Bearer $TOKEN" $API_SERVER/api/v1/namespaces
```

### Understanding the Flow:

```
Client Request Flow:
1. Client sends request with credentials (cert or token)
2. API Server receives request
3. Authentication: Verify credentials
   - X509 certificates
   - Bearer tokens
   - Basic auth (deprecated)
4. Authorization: Check permissions (RBAC)
5. Admission Control: Validate/mutate request
6. Process request and update etcd
7. Return response
```

---

## Exercise 10: Component Failure Simulation ⭐⭐⭐

### Solution:

```bash
# IMPORTANT: Do this on a test cluster only!

# 1. Check scheduler is running
kubectl get pods -n kube-system | grep scheduler

# 2. Stop scheduler (move manifest)
sudo mv /etc/kubernetes/manifests/kube-scheduler.yaml /tmp/

# Wait for pod to stop (30-60 seconds)
kubectl get pods -n kube-system | grep scheduler
# Should show no scheduler pod

# 3. Create a new pod
kubectl run test-pod --image=nginx

# 4. Check pod status
kubectl get pods test-pod
# STATUS: Pending

# Describe to see why
kubectl describe pod test-pod
# Events will show: "0/X nodes are available: persistentvolumeclaim not found"
# or simply no scheduling events

# 5. Restore scheduler
sudo mv /tmp/kube-scheduler.yaml /etc/kubernetes/manifests/

# 6. Watch pod get scheduled
kubectl get pods test-pod -w
# Should transition from Pending to Running

# Cleanup
kubectl delete pod test-pod
```

### Alternative Test - Controller Manager:

```bash
# Stop controller manager
sudo mv /etc/kubernetes/manifests/kube-controller-manager.yaml /tmp/

# Create a deployment
kubectl create deployment test-deploy --image=nginx --replicas=3

# Check what happens
kubectl get deployment test-deploy
kubectl get rs
kubectl get pods

# Result: Deployment created but no ReplicaSet or Pods
# Because controllers aren't running!

# Restore controller manager
sudo mv /tmp/kube-controller-manager.yaml /etc/kubernetes/manifests/

# Watch resources get created
kubectl get pods -w
```

### Answers to Questions:

**Q: What happens to existing pods when scheduler is down?**
```
- Existing pods continue running normally
- Kubelet manages running pods independently
- Only NEW pods cannot be scheduled
- Pending pods stay pending until scheduler returns
```

**Q: How long for scheduler to restart?**
```
- Kubelet check interval: 20 seconds (default)
- Pod startup time: 10-30 seconds
- Total: Usually 30-60 seconds
```

**Q: What if controller manager failed?**
```
- No replica management (pods won't be recreated)
- No namespace cleanup
- No service account token generation
- No node lifecycle management
- Deployments won't update/scale
- Jobs won't create pods

But existing pods keep running!
```

---

## Exercise 11: Namespace Isolation ⭐⭐

### Solution:

```bash
# 1. Create namespaces
kubectl create namespace dev
kubectl create namespace staging
kubectl create namespace prod

# Verify
kubectl get namespaces

# 2. Create pods with same name in each namespace
kubectl run nginx --image=nginx -n dev
kubectl run nginx --image=nginx -n staging
kubectl run nginx --image=nginx -n prod

# 3. List pods across all namespaces
kubectl get pods --all-namespaces | grep nginx

# Or specific namespaces
kubectl get pods -n dev
kubectl get pods -n staging
kubectl get pods -n prod

# 4. Delete all pods in dev namespace
kubectl delete pods --all -n dev

# 5. Verify other namespaces unaffected
kubectl get pods -n staging
kubectl get pods -n prod
# Should still show running pods

# Additional operations:

# Set default namespace for context
kubectl config set-context --current --namespace=staging

# Now commands use staging by default
kubectl get pods  # Shows pods in staging

# List all resources in a namespace
kubectl get all -n prod

# Delete a namespace (removes all resources)
kubectl delete namespace dev

# Cleanup
kubectl delete namespace staging prod
```

### Namespace Use Cases:
```yaml
Development Teams:
  - team-a
  - team-b
  - team-c

Environments:
  - development
  - staging
  - production

Applications:
  - app1
  - app2
  - monitoring
```

---

## Exercise 12: Label Selection Practice ⭐⭐

### Solution:

```bash
# 1. Create pods with labels
kubectl run frontend-dev --image=nginx --labels="app=frontend,env=dev"
kubectl run frontend-prod --image=nginx --labels="app=frontend,env=prod"
kubectl run backend-dev --image=nginx --labels="app=backend,env=dev"
kubectl run backend-prod --image=nginx --labels="app=backend,env=prod"
kubectl run database-prod --image=nginx --labels="app=database,env=prod"

# Verify labels
kubectl get pods --show-labels

# 2. Select all frontend pods
kubectl get pods -l app=frontend

# 3. Select all dev environment pods
kubectl get pods -l env=dev

# 4. Select prod backend pods (AND operation)
kubectl get pods -l app=backend,env=prod

# 5. Select pods NOT in prod (inequality)
kubectl get pods -l 'env!=prod'

# Additional selector examples:

# Set-based selectors
kubectl get pods -l 'env in (dev,staging)'
kubectl get pods -l 'env notin (prod)'
kubectl get pods -l 'app,env'  # Has both labels
kubectl get pods -l '!version'  # Doesn't have version label

# Update labels
kubectl label pod frontend-dev version=v1
kubectl label pod frontend-dev version=v2 --overwrite
kubectl label pod frontend-dev version-  # Remove label

# Delete pods by label
kubectl delete pods -l env=dev

# Cleanup
kubectl delete pods -l app
```

### Label Best Practices:

```yaml
Recommended Labels:
  app.kubernetes.io/name: nginx
  app.kubernetes.io/instance: nginx-prod
  app.kubernetes.io/version: "1.21"
  app.kubernetes.io/component: frontend
  app.kubernetes.io/part-of: ecommerce
  app.kubernetes.io/managed-by: helm
  environment: production
  tier: frontend
```

---

## Exercise 13: API Object Inspection ⭐⭐

### Solution:

```bash
# 1. Create a simple pod
kubectl run test-pod --image=nginx --labels="app=test" --port=80

# 2. Get pod definition in YAML
kubectl get pod test-pod -o yaml

# Save to file
kubectl get pod test-pod -o yaml > pod-definition.yaml

# 3. Identify spec section
kubectl get pod test-pod -o yaml | grep -A 20 "spec:"

# Or using jsonpath
kubectl get pod test-pod -o jsonpath='{.spec}' | jq .

# 4. Identify status section
kubectl get pod test-pod -o yaml | grep -A 20 "status:"

# Or
kubectl get pod test-pod -o jsonpath='{.status}' | jq .

# 5. Compare metadata, spec, and status

# Metadata (who/what/where)
kubectl get pod test-pod -o jsonpath='{.metadata}' | jq .

# Spec (desired state - what you defined)
kubectl get pod test-pod -o jsonpath='{.spec}' | jq .

# Status (current state - what Kubernetes reports)
kubectl get pod test-pod -o jsonpath='{.status}' | jq .
```

### Object Structure Breakdown:

```yaml
apiVersion: v1              # Which API version
kind: Pod                   # What type of object
metadata:                   # Data about the object
  name: test-pod           # Required: Object name
  namespace: default       # Namespace (default if not specified)
  labels:                  # Key-value pairs for organization
    app: test
  annotations:             # Non-identifying metadata
    description: "Test pod"
  uid: "abc-123"          # Unique identifier (generated)
  creationTimestamp: "..." # When created (generated)
  
spec:                      # Desired state (YOU define)
  containers:
  - name: nginx
    image: nginx:1.21
    ports:
    - containerPort: 80
  restartPolicy: Always
  
status:                    # Current state (KUBERNETES manages)
  phase: Running
  conditions:
  - type: Ready
    status: "True"
  containerStatuses:
  - name: nginx
    state:
      running:
        startedAt: "..."
  podIP: "10.244.1.5"
  hostIP: "192.168.1.10"
```

### Answers to Questions:

**Q: What fields are in metadata?**
```
- name (required)
- namespace
- labels
- annotations
- uid (generated)
- resourceVersion (generated)
- creationTimestamp (generated)
- deletionTimestamp (when deleting)
- ownerReferences (if owned by another resource)
```

**Q: What fields are in spec?**
```
- containers (required for pods)
- volumes
- restartPolicy
- nodeSelector
- affinity
- tolerations
- serviceAccountName
- securityContext
- All user-defined desired state
```

**Q: Who manages the status field?**
```
Kubernetes controllers manage the status field:
- Kubelet updates pod status
- Controllers update resource status
- Users cannot directly modify status
- Status is reconciled automatically
```

**Q: Can you modify status directly?**
```
No! The status field is read-only for users.
It's managed entirely by Kubernetes controllers.

If you try:
kubectl edit pod test-pod
# Modify status and save
# Changes will be ignored/reverted
```

---

## Exercise 14: Event Monitoring ⭐⭐

### Solution:

```bash
# 1. Get all events in default namespace
kubectl get events

# 2. Create pod with invalid image
kubectl run bad-pod --image=nonexistent-image:latest

# 3. Check events related to that pod
kubectl get events --field-selector involvedObject.name=bad-pod

# More specific
kubectl describe pod bad-pod | grep -A 10 Events

# 4. Sort events by timestamp
kubectl get events --sort-by=.metadata.creationTimestamp

# Most recent last
kubectl get events --sort-by='.lastTimestamp'

# 5. Filter by type
kubectl get events --field-selector type=Warning
kubectl get events --field-selector type=Normal

# Additional useful event queries:

# Events in all namespaces
kubectl get events --all-namespaces

# Events for specific reason
kubectl get events --field-selector reason=FailedScheduling

# Events in last hour
kubectl get events --field-selector type=Warning \
  --sort-by='.lastTimestamp' | \
  awk -v date="$(date -u -v-1H '+%Y-%m-%dT%H:%M:%S')" '$1 > date'

# Watch events in real-time
kubectl get events -w

# Events for a namespace
kubectl get events -n kube-system

# Clean format
kubectl get events --sort-by='.lastTimestamp' \
  -o custom-columns=TIME:.lastTimestamp,TYPE:.type,REASON:.reason,OBJECT:.involvedObject.name,MESSAGE:.message

# Cleanup
kubectl delete pod bad-pod
```

### Common Event Reasons:

```yaml
Scheduling:
  - Scheduled: Pod assigned to node
  - FailedScheduling: Cannot find suitable node
  
Container:
  - Pulling: Pulling container image
  - Pulled: Successfully pulled image
  - Failed: Failed to pull image
  - Created: Container created
  - Started: Container started
  - Killing: Killing container
  - BackOff: Back-off restarting failed container
  
Node:
  - NodeReady: Node is ready
  - NodeNotReady: Node is not ready
  - RegisteredNode: Node registered
  
Volume:
  - FailedMount: Failed to mount volume
  - SuccessfulAttachVolume: Volume attached
```

---

## Exercise 15: Multi-Node Cluster Analysis ⭐⭐⭐

### Solution:

```bash
# 1. List all nodes
kubectl get nodes

# Detailed view
kubectl get nodes -o wide

# 2. Identify control plane node
kubectl get nodes --selector='node-role.kubernetes.io/control-plane'

# Or
kubectl get nodes --show-labels | grep control-plane

# 3. List pods on each node
# For each node:
NODE_NAME="node1"  # Replace with actual node name
kubectl get pods --all-namespaces --field-selector spec.nodeName=$NODE_NAME

# Or create a script
for node in $(kubectl get nodes -o jsonpath='{.items[*].metadata.name}'); do
    echo "=== Pods on $node ==="
    kubectl get pods --all-namespaces --field-selector spec.nodeName=$node
    echo ""
done

# 4. Identify node roles and labels
kubectl get nodes --show-labels

# Get specific label
kubectl get nodes -o custom-columns=NAME:.metadata.name,ROLES:.metadata.labels

# 5. Check resource usage
kubectl top nodes

# Detailed node info
kubectl describe node <node-name>

# See capacity and allocatable resources
kubectl get nodes -o custom-columns=\
NAME:.metadata.name,\
CPU-CAPACITY:.status.capacity.cpu,\
MEMORY-CAPACITY:.status.capacity.memory,\
CPU-ALLOCATABLE:.status.allocatable.cpu,\
MEMORY-ALLOCATABLE:.status.allocatable.memory
```

### Comprehensive Node Analysis Script:

```bash
#!/bin/bash

echo "=== KUBERNETES CLUSTER ANALYSIS ==="
echo ""

# Cluster info
echo "Cluster Information:"
kubectl cluster-info
echo ""

# Node summary
echo "Node Summary:"
kubectl get nodes -o wide
echo ""

# Control plane nodes
echo "Control Plane Nodes:"
kubectl get nodes -l node-role.kubernetes.io/control-plane --no-headers | wc -l
echo ""

# Worker nodes
echo "Worker Nodes:"
TOTAL=$(kubectl get nodes --no-headers | wc -l)
CONTROL=$(kubectl get nodes -l node-role.kubernetes.io/control-plane --no-headers | wc -l)
echo "$((TOTAL - CONTROL))"
echo ""

# Pod distribution
echo "Pod Distribution Across Nodes:"
for node in $(kubectl get nodes -o jsonpath='{.items[*].metadata.name}'); do
    COUNT=$(kubectl get pods --all-namespaces --field-selector spec.nodeName=$node --no-headers | wc -l)
    echo "  $node: $COUNT pods"
done
echo ""

# Resource usage
echo "Node Resource Usage:"
kubectl top nodes
echo ""

# Node conditions
echo "Node Conditions:"
kubectl get nodes -o custom-columns=\
NAME:.metadata.name,\
READY:.status.conditions[?(@.type==\"Ready\")].status,\
DISK-PRESSURE:.status.conditions[?(@.type==\"DiskPressure\")].status,\
MEMORY-PRESSURE:.status.conditions[?(@.type==\"MemoryPressure\")].status,\
PID-PRESSURE:.status.conditions[?(@.type==\"PIDPressure\")].status
```

Save as `cluster-analysis.sh` and run:
```bash
chmod +x cluster-analysis.sh
./cluster-analysis.sh
```

### Answers to Questions:

**Q: How many control plane nodes?**
```bash
kubectl get nodes -l node-role.kubernetes.io/control-plane --no-headers | wc -l

# In production: Usually 3 for HA
# In test: Usually 1
```

**Q: How many worker nodes?**
```bash
TOTAL=$(kubectl get nodes --no-headers | wc -l)
CONTROL=$(kubectl get nodes -l node-role.kubernetes.io/control-plane --no-headers | wc -l)
echo "Worker nodes: $((TOTAL - CONTROL))"
```

**Q: What labels identify control plane nodes?**
```
Labels:
- node-role.kubernetes.io/control-plane="" (1.20+)
- node-role.kubernetes.io/master="" (deprecated)

Taints:
- node-role.kubernetes.io/control-plane:NoSchedule
```

**Q: How is pod distribution?**
```bash
# Check if pods are evenly distributed
for node in $(kubectl get nodes -o jsonpath='{.items[*].metadata.name}'); do
    COUNT=$(kubectl get pods --all-namespaces --field-selector spec.nodeName=$node --no-headers | wc -l)
    echo "$node: $COUNT pods"
done

# Factors affecting distribution:
# - DaemonSets (run on all nodes)
# - Node selectors
# - Taints and tolerations
# - Resource requests
# - Pod anti-affinity rules
```

---

## 🎯 Challenge Exercise Solution: Complete Cluster Audit

### cluster-health-check.sh

```bash
#!/bin/bash

# Cluster Health Check Script
# For CKA/CKAD Practice

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "╔════════════════════════════════════════╗"
echo "║   KUBERNETES CLUSTER HEALTH CHECK     ║"
echo "╚════════════════════════════════════════╝"
echo ""
echo "Date: $(date)"
echo "Cluster: $(kubectl config current-context)"
echo ""

# Track issues
ISSUES=0

# 1. Component Health
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. CONTROL PLANE COMPONENTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

components=("kube-apiserver" "etcd" "kube-scheduler" "kube-controller-manager")
for comp in "${components[@]}"; do
    STATUS=$(kubectl get pods -n kube-system -l component=$comp -o jsonpath='{.items[0].status.phase}' 2>/dev/null)
    if [ "$STATUS" == "Running" ]; then
        echo -e "✓ $comp: ${GREEN}Running${NC}"
    else
        echo -e "✗ $comp: ${RED}Not Running${NC}"
        ((ISSUES++))
    fi
done

echo ""
kubectl get componentstatuses 2>/dev/null || echo "Component status API deprecated"
echo ""

# 2. Node Health
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2. NODE HEALTH"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

kubectl get nodes -o custom-columns=\
NAME:.metadata.name,\
STATUS:.status.conditions[?(@.type==\"Ready\")].status,\
ROLES:.metadata.labels.node-role\\.kubernetes\\.io/control-plane,\
VERSION:.status.nodeInfo.kubeletVersion

NOT_READY=$(kubectl get nodes --no-headers | grep -v " Ready" | wc -l)
if [ "$NOT_READY" -gt 0 ]; then
    echo -e "${RED}Warning: $NOT_READY node(s) not ready${NC}"
    ((ISSUES++))
fi

echo ""
echo "Node Resource Usage:"
kubectl top nodes 2>/dev/null || echo "Metrics server not available"
echo ""

# 3. Networking
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3. NETWORKING COMPONENTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# CoreDNS
COREDNS_READY=$(kubectl get deployment -n kube-system coredns -o jsonpath='{.status.readyReplicas}' 2>/dev/null)
COREDNS_DESIRED=$(kubectl get deployment -n kube-system coredns -o jsonpath='{.spec.replicas}' 2>/dev/null)
if [ "$COREDNS_READY" == "$COREDNS_DESIRED" ]; then
    echo -e "✓ CoreDNS: ${GREEN}$COREDNS_READY/$COREDNS_DESIRED ready${NC}"
else
    echo -e "✗ CoreDNS: ${RED}$COREDNS_READY/$COREDNS_DESIRED ready${NC}"
    ((ISSUES++))
fi

# kube-proxy
PROXY_COUNT=$(kubectl get daemonset -n kube-system kube-proxy -o jsonpath='{.status.numberReady}' 2>/dev/null)
PROXY_DESIRED=$(kubectl get daemonset -n kube-system kube-proxy -o jsonpath='{.status.desiredNumberScheduled}' 2>/dev/null)
if [ "$PROXY_COUNT" == "$PROXY_DESIRED" ]; then
    echo -e "✓ kube-proxy: ${GREEN}$PROXY_COUNT/$PROXY_DESIRED ready${NC}"
else
    echo -e "✗ kube-proxy: ${RED}$PROXY_COUNT/$PROXY_DESIRED ready${NC}"
    ((ISSUES++))
fi

# DNS Test
echo ""
echo "Testing DNS resolution:"
kubectl run --rm -it dns-test --image=busybox:1.28 --restart=Never -- nslookup kubernetes.default >/dev/null 2>&1 && \
    echo -e "${GREEN}✓ DNS resolution working${NC}" || \
    echo -e "${RED}✗ DNS resolution failed${NC}"
echo ""

# 4. etcd Health
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4. ETCD HEALTH"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

ETCD_POD=$(kubectl get pods -n kube-system -l component=etcd -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
if [ -n "$ETCD_POD" ]; then
    echo "etcd pod: $ETCD_POD"
    
    # Try to check etcd health (requires exec permissions)
    kubectl exec -n kube-system $ETCD_POD -- etcdctl \
        --endpoints=https://127.0.0.1:2379 \
        --cacert=/etc/kubernetes/pki/etcd/ca.crt \
        --cert=/etc/kubernetes/pki/etcd/server.crt \
        --key=/etc/kubernetes/pki/etcd/server.key \
        endpoint health 2>/dev/null && \
        echo -e "${GREEN}✓ etcd is healthy${NC}" || \
        echo -e "${YELLOW}⚠ Could not check etcd health (permissions?)${NC}"
else
    echo -e "${YELLOW}⚠ etcd pod not found (external etcd?)${NC}"
fi
echo ""

# 5. Certificates
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5. CERTIFICATE VALIDITY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check API server certificate expiry (if accessible)
echo "Checking API server certificate:"
API_SERVER=$(kubectl config view --minify -o jsonpath='{.clusters[0].cluster.server}' | sed 's/https:\/\///')
echo | openssl s_client -showcerts -connect $API_SERVER 2>/dev/null | \
    openssl x509 -noout -dates 2>/dev/null && \
    echo -e "${GREEN}✓ Certificate information retrieved${NC}" || \
    echo -e "${YELLOW}⚠ Could not check certificate${NC}"
echo ""

# 6. System Pods
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "6. SYSTEM PODS STATUS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

NOT_RUNNING=$(kubectl get pods -n kube-system --no-headers | grep -v "Running\|Completed" | wc -l)
if [ "$NOT_RUNNING" -eq 0 ]; then
    echo -e "${GREEN}✓ All system pods running${NC}"
else
    echo -e "${RED}✗ $NOT_RUNNING system pod(s) not running:${NC}"
    kubectl get pods -n kube-system | grep -v "Running\|Completed"
    ((ISSUES++))
fi
echo ""

# 7. Recent Events
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "7. RECENT WARNING EVENTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

WARNINGS=$(kubectl get events --all-namespaces --field-selector type=Warning --sort-by='.lastTimestamp' 2>/dev/null | tail -n 10)
if [ -z "$WARNINGS" ]; then
    echo -e "${GREEN}✓ No recent warnings${NC}"
else
    echo "$WARNINGS"
    ((ISSUES++))
fi
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ $ISSUES -eq 0 ]; then
    echo -e "${GREEN}✓ Cluster is healthy! No issues detected.${NC}"
else
    echo -e "${YELLOW}⚠ Found $ISSUES issue(s) that need attention.${NC}"
fi

echo ""
echo "Health check completed at $(date)"

exit $ISSUES
```

### Usage:

```bash
# Make executable
chmod +x cluster-health-check.sh

# Run health check
./cluster-health-check.sh

# Schedule as cron job (optional)
crontab -e
# Add: 0 */6 * * * /path/to/cluster-health-check.sh > /var/log/k8s-health-check.log 2>&1
```

---

This comprehensive set of solutions covers all exercises with detailed explanations, expected outputs, and additional insights. Practice these regularly to build muscle memory for the CKA/CKAD exams!

