# Module 01: Exercises - Kubernetes Architecture & Fundamentals

## 📝 Exercise Overview

These exercises will test your understanding of Kubernetes architecture and core components.

**Time Allocation**: 45-60 minutes
**Difficulty Levels**: ⭐ Easy | ⭐⭐ Medium | ⭐⭐⭐ Hard

---

## Exercise 1: Cluster Component Inspection ⭐

**Objective**: Identify and verify all control plane components in your cluster.

**Tasks**:
1. List all pods in the `kube-system` namespace
2. Identify which pods are control plane components
3. Check the status of all control plane components
4. Find the version of Kubernetes running on your cluster
5. List all nodes in the cluster with their roles

**Expected Output**: A report showing all components and their health status.

**Hints**:
```bash
kubectl get pods -n kube-system
kubectl get componentstatuses
kubectl version
kubectl get nodes
```

---

## Exercise 2: API Resource Discovery ⭐

**Objective**: Explore Kubernetes API resources and their structure.

**Tasks**:
1. List all API resources available in your cluster
2. Find all resources in the `apps` API group
3. Get the full API documentation for a `Deployment` object
4. List all available API versions
5. Show the detailed structure of `Pod.spec.containers`

**Commands to Use**:
```bash
kubectl api-resources
kubectl api-versions
kubectl explain <resource>
```

---

## Exercise 3: Component Log Analysis ⭐⭐

**Objective**: Learn to inspect component logs for troubleshooting.

**Tasks**:
1. View the logs of the API server
2. View the logs of the scheduler
3. View the logs of the controller manager
4. View the logs of CoreDNS
5. Check for any error messages in the logs

**Questions**:
- What port is the API server listening on?
- How many leader election attempts do you see in the controller manager logs?
- Are there any failed scheduling attempts in the scheduler logs?

---

## Exercise 4: etcd Inspection ⭐⭐

**Objective**: Interact with etcd and understand cluster state storage.

**Tasks**:
1. Check etcd pod health
2. List all keys stored in etcd (just the keys, not values)
3. Find where pod information is stored in etcd
4. Count how many keys exist in etcd
5. Identify the etcd data directory

**Prerequisites**: 
- etcd client tools installed
- Access to etcd certificates

**Sample Command**:
```bash
ETCDCTL_API=3 etcdctl \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  endpoint health
```

---

## Exercise 5: Node Component Analysis ⭐⭐

**Objective**: Understand worker node components and their configuration.

**Tasks**:
1. Find the kubelet configuration file location
2. Check kubelet service status
3. Identify which container runtime is being used
4. Check kube-proxy mode (iptables or ipvs)
5. List all containers running on a node

**For systemd-based systems**:
```bash
systemctl status kubelet
journalctl -u kubelet -n 50
cat /var/lib/kubelet/config.yaml
```

---

## Exercise 6: Static Pod Creation ⭐⭐

**Objective**: Understand how control plane components run as static pods.

**Tasks**:
1. Find the static pod manifest directory
2. List all static pod manifests
3. Identify which components run as static pods
4. Create a custom static pod that runs nginx
5. Verify the static pod is running

**Steps**:
1. Determine static pod path: `cat /var/lib/kubelet/config.yaml | grep staticPodPath`
2. Create a pod manifest in that directory
3. Kubelet will automatically create the pod

**Static Pod Characteristics**:
- Pod name has node name appended (e.g., `nginx-node01`)
- Cannot be managed by controllers
- Managed directly by kubelet

---

## Exercise 7: Scheduler Behavior ⭐⭐⭐

**Objective**: Understand how the scheduler assigns pods to nodes.

**Tasks**:
1. Create a pod without specifying a nodeName
2. Observe the pod being scheduled
3. Create a pod that requires more resources than available
4. Observe that it stays in Pending state
5. Describe the pending pod to see scheduler events

**Pod Manifest** (large-resources-pod.yaml):
```yaml
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
```

**Questions**:
- What scheduler events do you see?
- Why is the pod not scheduled?
- How can you fix this?

---

## Exercise 8: Controller Manager Deep Dive ⭐⭐⭐

**Objective**: Observe controller reconciliation loops in action.

**Tasks**:
1. Create a deployment with 3 replicas
2. Delete one of the pods manually
3. Observe how quickly a new pod is created
4. Scale the deployment to 5 replicas
5. Watch the controller manager logs during these operations

**Commands**:
```bash
kubectl create deployment nginx --image=nginx --replicas=3
kubectl get pods -w
kubectl delete pod <pod-name>
kubectl scale deployment nginx --replicas=5
kubectl logs -n kube-system kube-controller-manager-<node> --tail=50
```

**Questions**:
- Which controller created the new pod?
- How long did it take to detect and fix the drift?
- What happens if you delete multiple pods simultaneously?

---

## Exercise 9: API Server Authentication Flow ⭐⭐⭐

**Objective**: Understand how API requests are authenticated and authorized.

**Tasks**:
1. View your kubeconfig file
2. Identify the client certificate and key
3. Make a raw API request using curl
4. Try to access the API without authentication
5. Create a service account and get its token

**Sample curl command**:
```bash
# Get cluster endpoint
kubectl config view --minify -o jsonpath='{.clusters[0].cluster.server}'

# Get client certificate
kubectl config view --raw -o jsonpath='{.users[0].user.client-certificate-data}' | base64 -d > client.crt

# Get client key
kubectl config view --raw -o jsonpath='{.users[0].user.client-key-data}' | base64 -d > client.key

# Get CA certificate
kubectl config view --raw -o jsonpath='{.clusters[0].cluster.certificate-authority-data}' | base64 -d > ca.crt

# Make API request
curl --cert client.crt --key client.key --cacert ca.crt https://<api-server>:6443/api/v1/namespaces
```

---

## Exercise 10: Component Failure Simulation ⭐⭐⭐

**Objective**: Understand cluster behavior when components fail.

**Tasks**:
1. Stop the scheduler temporarily
2. Create a new pod and observe it stays unscheduled
3. Restart the scheduler
4. Observe the pod gets scheduled
5. Document your findings

**For kubeadm clusters**:
```bash
# Move scheduler manifest
sudo mv /etc/kubernetes/manifests/kube-scheduler.yaml /tmp/

# Create a pod
kubectl run test-pod --image=nginx

# Check pod status
kubectl get pods

# Restore scheduler
sudo mv /tmp/kube-scheduler.yaml /etc/kubernetes/manifests/

# Watch pod get scheduled
kubectl get pods -w
```

**Questions**:
- What happens to existing pods when scheduler is down?
- How long does it take for the scheduler to restart?
- What would happen if controller manager failed?

---

## Exercise 11: Namespace Isolation ⭐⭐

**Objective**: Understand namespace-based organization.

**Tasks**:
1. Create three namespaces: `dev`, `staging`, `prod`
2. Create a pod with the same name in each namespace
3. List pods across all namespaces
4. Delete all pods in the `dev` namespace
5. Verify pods in other namespaces are unaffected

**Commands**:
```bash
kubectl create namespace dev
kubectl create namespace staging
kubectl create namespace prod

kubectl run nginx --image=nginx -n dev
kubectl run nginx --image=nginx -n staging
kubectl run nginx --image=nginx -n prod

kubectl get pods --all-namespaces
kubectl delete pods --all -n dev
```

---

## Exercise 12: Label Selection Practice ⭐⭐

**Objective**: Master label selectors for resource management.

**Tasks**:
1. Create 5 pods with different labels:
   - app=frontend, env=dev
   - app=frontend, env=prod
   - app=backend, env=dev
   - app=backend, env=prod
   - app=database, env=prod
   
2. Select all frontend pods
3. Select all dev environment pods
4. Select all prod backend pods
5. Select pods that are NOT in prod

**Example**:
```bash
kubectl run frontend-dev --image=nginx --labels="app=frontend,env=dev"
kubectl run frontend-prod --image=nginx --labels="app=frontend,env=prod"
# ... create others

# Selectors
kubectl get pods -l app=frontend
kubectl get pods -l env=dev
kubectl get pods -l app=backend,env=prod
kubectl get pods -l 'env!=prod'
```

---

## Exercise 13: API Object Inspection ⭐⭐

**Objective**: Understand Kubernetes object structure.

**Tasks**:
1. Create a simple pod
2. Get the pod definition in YAML format
3. Identify the `spec` section (desired state)
4. Identify the `status` section (current state)
5. Explain the difference between `metadata` and `spec`

**Commands**:
```bash
kubectl run test-pod --image=nginx
kubectl get pod test-pod -o yaml
kubectl get pod test-pod -o json | jq .status
```

**Questions**:
- What fields are in `metadata`?
- What fields are in `spec`?
- Who manages the `status` field?
- Can you modify the `status` field directly?

---

## Exercise 14: Event Monitoring ⭐⭐

**Objective**: Use events to understand cluster activities.

**Tasks**:
1. Get all events in the default namespace
2. Create a pod with an invalid image
3. Check events related to that pod
4. Sort events by timestamp
5. Filter events by type (Warning, Normal)

**Commands**:
```bash
kubectl get events
kubectl run bad-pod --image=nonexistent:latest
kubectl get events --field-selector involvedObject.name=bad-pod
kubectl get events --sort-by=.metadata.creationTimestamp
kubectl get events --field-selector type=Warning
```

---

## Exercise 15: Multi-Node Cluster Analysis ⭐⭐⭐

**Objective**: Understand multi-node cluster topology.

**Tasks**:
1. List all nodes in your cluster
2. Identify which node is the control plane
3. List all pods running on each node
4. Identify node roles and labels
5. Check resource usage on each node

**Commands**:
```bash
kubectl get nodes
kubectl get nodes --show-labels
kubectl get pods --all-namespaces -o wide
kubectl describe node <node-name>
kubectl top nodes
```

**Questions**:
- How many control plane nodes do you have?
- How many worker nodes?
- What labels identify control plane nodes?
- How is pod distribution across nodes?

---

## 🎯 Challenge Exercise: Complete Cluster Audit ⭐⭐⭐

**Objective**: Perform a comprehensive cluster health check.

**Tasks**:
Create a shell script that performs the following:

1. **Component Health**:
   - Check all control plane pods are running
   - Verify component statuses
   - Check etcd health

2. **Node Health**:
   - List all nodes and their status
   - Check node resource usage
   - Verify kubelet is running on all nodes

3. **Networking**:
   - Verify CoreDNS is running
   - Check kube-proxy is running on all nodes
   - Test DNS resolution

4. **API Server**:
   - Verify API server is accessible
   - Check certificate validity
   - Test API authentication

5. **Generate Report**:
   - Create a summary report with all findings
   - Highlight any issues found
   - Suggest remediation steps

**Deliverable**: Shell script named `cluster-health-check.sh` and a sample report.

---

## 💡 Tips for Success

1. **Use kubectl explain**: Before creating resources, use `kubectl explain` to understand object structure
2. **Read the events**: Events often contain clues about what's happening in the cluster
3. **Check logs frequently**: Component logs provide detailed information about operations
4. **Practice label selectors**: They're crucial for managing resources at scale
5. **Understand the flow**: Know how components interact when you perform an action

## 🔗 Solution Files

Solutions for all exercises can be found in the [solutions](./solutions.md) file.

---

**Next Steps**: After completing these exercises, proceed to [Module 02 - Cluster Installation & Configuration](../../02-cluster-installation/README.md)
