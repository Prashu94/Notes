# Module 01: Kubernetes Architecture & Fundamentals

## 📋 Learning Objectives

By the end of this module, you will understand:
- Kubernetes architecture and core components
- Control plane and worker node components
- Kubernetes API and object model
- etcd and cluster state management
- How components communicate with each other

## 🏗️ Kubernetes Architecture Overview

Kubernetes follows a **master-worker architecture** with a declarative model where you describe the desired state and Kubernetes works to maintain that state.

```
┌─────────────────────────────────────────────────────────────┐
│                      CONTROL PLANE                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  API Server  │  │  Scheduler   │  │   Controller │     │
│  │              │  │              │  │    Manager   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│         │                 │                  │              │
│         └─────────────────┼──────────────────┘              │
│                           │                                 │
│                  ┌────────┴────────┐                       │
│                  │      etcd       │                       │
│                  │  (Key-Value DB) │                       │
│                  └─────────────────┘                       │
└─────────────────────────────────────────────────────────────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
    ┌─────────▼─────┐  ┌───▼──────┐  ┌▼──────────┐
    │  WORKER NODE  │  │  WORKER  │  │  WORKER   │
    │               │  │   NODE   │  │   NODE    │
    │  ┌─────────┐  │  │          │  │           │
    │  │ kubelet │  │  │  ...     │  │  ...      │
    │  └─────────┘  │  │          │  │           │
    │  ┌─────────┐  │  │          │  │           │
    │  │kube-proxy│ │  │          │  │           │
    │  └─────────┘  │  │          │  │           │
    │  ┌─────────┐  │  │          │  │           │
    │  │Container│  │  │          │  │           │
    │  │ Runtime │  │  │          │  │           │
    │  └─────────┘  │  │          │  │           │
    └───────────────┘  └──────────┘  └───────────┘
```

## 🎯 Control Plane Components

### 1. API Server (kube-apiserver)

**Purpose**: The front-end for the Kubernetes control plane. All communications go through the API server.

**Key Functions**:
- Exposes the Kubernetes API (RESTful interface)
- Authenticates and authorizes requests
- Validates and processes API requests
- Updates etcd with the cluster state
- Only component that talks directly to etcd

**Important Details**:
- Runs on port 6443 (HTTPS)
- Horizontally scalable (can run multiple instances)
- Stateless component

```bash
# Check API server status
kubectl get componentstatuses

# View API server logs
kubectl logs -n kube-system kube-apiserver-<node-name>

# API server configuration
cat /etc/kubernetes/manifests/kube-apiserver.yaml
```

### 2. etcd

**Purpose**: Consistent and highly-available key-value store for all cluster data.

**Key Functions**:
- Stores entire cluster state
- Stores configuration data
- Service discovery information
- Implements distributed consensus (Raft algorithm)

**Important Details**:
- Runs on port 2379 (client) and 2380 (peer)
- Only API server communicates with etcd
- Critical for cluster - MUST be backed up regularly
- Can run as external cluster or stacked with control plane

```bash
# Check etcd health
ETCDCTL_API=3 etcdctl --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  endpoint health

# List all keys in etcd
ETCDCTL_API=3 etcdctl --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  get / --prefix --keys-only
```

### 3. Scheduler (kube-scheduler)

**Purpose**: Watches for newly created Pods and assigns them to nodes.

**Key Functions**:
- Selects optimal node for pod placement
- Considers resource requirements, constraints, and policies
- Implements scheduling algorithms (filtering and scoring)

**Scheduling Process**:
1. **Filtering**: Find feasible nodes (predicates)
   - NodeResourcesFit
   - NodeName
   - NodeSelector
   - PodFitsHostPorts
   
2. **Scoring**: Rank feasible nodes (priorities)
   - LeastRequestedPriority
   - BalancedResourceAllocation
   - ImageLocalityPriority

**Important Details**:
- Only schedules pods, doesn't run them
- Can be customized with scheduler policies
- Considers taints, tolerations, affinity rules

```bash
# View scheduler logs
kubectl logs -n kube-system kube-scheduler-<node-name>

# Check pending pods waiting for scheduling
kubectl get pods --field-selector=status.phase=Pending
```

### 4. Controller Manager (kube-controller-manager)

**Purpose**: Runs controller processes that regulate cluster state.

**Key Controllers**:
- **Node Controller**: Monitors node health
- **Replication Controller**: Maintains correct number of pods
- **Endpoints Controller**: Populates Endpoints objects (joins Services & Pods)
- **Service Account & Token Controllers**: Create default accounts and API access tokens
- **Deployment Controller**: Manages deployments
- **StatefulSet Controller**: Manages stateful applications
- **DaemonSet Controller**: Ensures pods run on all/some nodes
- **Job Controller**: Creates pods for Jobs
- **CronJob Controller**: Manages time-based jobs

**Control Loop Pattern**:
```
1. Observe: Watch current state
2. Diff: Compare current state with desired state
3. Act: Take action to reconcile
4. Repeat
```

```bash
# View controller manager logs
kubectl logs -n kube-system kube-controller-manager-<node-name>

# Check which controllers are running
ps aux | grep kube-controller-manager
```

### 5. Cloud Controller Manager (optional)

**Purpose**: Embeds cloud-specific control logic (AWS, GCP, Azure).

**Key Controllers**:
- Node Controller: Check cloud provider for node deletion
- Route Controller: Set up routes in cloud infrastructure
- Service Controller: Create/delete cloud load balancers

## 🖥️ Worker Node Components

### 1. kubelet

**Purpose**: Agent running on each node that ensures containers are running in pods.

**Key Functions**:
- Registers node with API server
- Receives PodSpecs from API server
- Ensures containers described in PodSpecs are running and healthy
- Reports node and pod status to API server
- Executes liveness/readiness probes
- Mounts volumes

**Important Details**:
- Runs as systemd service (not as a pod)
- Communicates with container runtime via CRI
- Monitors pod health and restarts failed containers
- Port 10250 (API), 10255 (read-only)

```bash
# Check kubelet status
systemctl status kubelet

# View kubelet logs
journalctl -u kubelet -f

# Kubelet configuration
cat /var/lib/kubelet/config.yaml
```

### 2. kube-proxy

**Purpose**: Network proxy running on each node, maintains network rules.

**Key Functions**:
- Implements Kubernetes Service concept
- Maintains network rules for pod communication
- Forwards traffic to appropriate pods
- Implements load balancing for Services

**Proxy Modes**:
- **iptables** (default): Uses iptables rules, no additional latency
- **IPVS**: Better performance for large clusters, requires IPVS kernel modules
- **userspace**: Legacy mode, adds latency

```bash
# Check kube-proxy mode
kubectl logs -n kube-system kube-proxy-<pod-name> | grep "Using"

# View iptables rules created by kube-proxy
sudo iptables -t nat -L -n -v | grep KUBE
```

### 3. Container Runtime

**Purpose**: Software responsible for running containers.

**Supported Runtimes**:
- **containerd** (most common)
- **CRI-O**
- **Docker Engine** (via containerd)

**Container Runtime Interface (CRI)**:
- Standard interface between kubelet and container runtime
- Allows pluggable container runtimes

```bash
# Check container runtime
kubectl get nodes -o wide

# List containers with containerd
sudo ctr -n k8s.io containers list

# List containers with crictl
sudo crictl ps
```

## 🔌 Add-ons

Essential cluster features implemented as pods:

### DNS (CoreDNS)
- Provides DNS-based service discovery
- Resolves service names to cluster IPs

### Dashboard
- Web-based UI for cluster management

### Container Resource Monitoring
- Collects and stores container metrics

### Cluster-level Logging
- Saves container logs to central location

## 📦 Kubernetes Objects

### Object Structure

Every Kubernetes object includes:

```yaml
apiVersion: v1              # API version
kind: Pod                   # Object type
metadata:                   # Metadata about the object
  name: my-pod
  namespace: default
  labels:
    app: nginx
  annotations:
    description: "Example pod"
spec:                       # Desired state
  containers:
  - name: nginx
    image: nginx:1.14.2
status:                     # Current state (managed by K8s)
  phase: Running
```

### Object Categories

1. **Workloads**: Pod, ReplicaSet, Deployment, StatefulSet, DaemonSet, Job, CronJob
2. **Service & Discovery**: Service, Ingress, EndpointSlice
3. **Config & Storage**: ConfigMap, Secret, Volume, PersistentVolume, PersistentVolumeClaim
4. **Cluster**: Namespace, Node, ServiceAccount, ResourceQuota, LimitRange
5. **Metadata**: HorizontalPodAutoscaler, PodDisruptionBudget

## 🔐 Kubernetes API

### API Structure

```
/api/v1/
    /namespaces/{namespace}/
        /pods
        /services
        /configmaps
        /secrets
        
/apis/{group}/{version}/
    /namespaces/{namespace}/
        /{resource}
```

### API Groups

- **Core (legacy)**: `/api/v1` - Pod, Service, ConfigMap, etc.
- **apps**: `/apis/apps/v1` - Deployment, StatefulSet, DaemonSet
- **batch**: `/apis/batch/v1` - Job, CronJob
- **networking.k8s.io**: `/apis/networking.k8s.io/v1` - NetworkPolicy, Ingress
- **storage.k8s.io**: `/apis/storage.k8s.io/v1` - StorageClass
- **rbac.authorization.k8s.io**: `/apis/rbac.authorization.k8s.io/v1` - Role, RoleBinding

```bash
# List all API resources
kubectl api-resources

# List API versions
kubectl api-versions

# Get specific resource API details
kubectl explain pod
kubectl explain pod.spec
kubectl explain pod.spec.containers
```

## 🔄 How Kubernetes Works: Pod Creation Flow

```
1. User runs: kubectl create -f pod.yaml
   └─> kubectl sends request to API Server

2. API Server:
   ├─> Authenticates user
   ├─> Authorizes request (RBAC)
   ├─> Validates pod spec
   ├─> Persists pod object to etcd
   └─> Returns response to user

3. Scheduler watches API Server:
   ├─> Detects new pod with no nodeName
   ├─> Filters feasible nodes
   ├─> Scores nodes
   ├─> Selects best node
   └─> Updates pod object with nodeName (via API Server)

4. kubelet on selected node watches API Server:
   ├─> Detects new pod assigned to its node
   ├─> Instructs container runtime to pull image
   ├─> Creates and starts container
   └─> Reports pod status back to API Server

5. Controllers watch API Server:
   └─> Continuously monitor and reconcile state
```

## 🎓 Key Concepts

### Desired State Management
- You declare desired state in YAML/JSON
- Kubernetes constantly works to maintain that state
- Controllers implement reconciliation loops

### Labels and Selectors
- Labels: Key-value pairs attached to objects
- Selectors: Query objects by labels
- Used for grouping and selecting objects

### Namespaces
- Virtual clusters within physical cluster
- Provides scope for names (name must be unique within namespace)
- Resource quotas and limits can be applied per namespace

### Default Namespaces
```bash
default          # Default namespace for objects
kube-system      # Objects created by Kubernetes system
kube-public      # Readable by all users
kube-node-lease  # Node heartbeat data
```

## 📊 Component Communication

### Communication Patterns

1. **kubectl → API Server**: HTTPS (port 6443)
2. **API Server → etcd**: HTTPS (port 2379)
3. **API Server → kubelet**: HTTPS (port 10250)
4. **API Server → Scheduler**: In-cluster
5. **API Server → Controller Manager**: In-cluster
6. **kubelet → API Server**: HTTPS (port 6443)
7. **Scheduler → API Server**: In-cluster
8. **Controller Manager → API Server**: In-cluster

### Security
- All communication is encrypted (TLS)
- Mutual TLS authentication
- Certificates managed in `/etc/kubernetes/pki/`

## 🔍 Inspection Commands

```bash
# Cluster information
kubectl cluster-info
kubectl get nodes
kubectl describe node <node-name>

# Component status
kubectl get componentstatuses
kubectl get pods -n kube-system

# API server
kubectl get --raw /healthz
kubectl get --raw /api/v1

# Node information
kubectl get nodes -o wide
kubectl top nodes

# Cluster events
kubectl get events --all-namespaces --sort-by='.lastTimestamp'
```

## 🎯 Exam Tips

### CKA Focus
- Know all control plane components and their functions
- Understand etcd backup and restore procedures
- Know where component logs are located
- Understand static pod manifests location
- Know certificate locations and renewal

### CKAD Focus
- Understand basic architecture
- Focus on application-level concepts
- Know how to interact with API
- Understand pod lifecycle

### Must-Know Locations
```
/etc/kubernetes/manifests/       # Static pod manifests
/etc/kubernetes/pki/             # Certificates
/var/lib/kubelet/                # kubelet data
/var/lib/etcd/                   # etcd data
/var/log/pods/                   # Pod logs
```

## 📝 Quick Reference

### Component Ports
```
API Server:        6443
etcd:              2379, 2380
Scheduler:         10259
Controller Mgr:    10257
kubelet:           10250
kube-proxy:        10256
```

### Component Locations (kubeadm)
```
Static Pods:       /etc/kubernetes/manifests/
Kubelet Config:    /var/lib/kubelet/config.yaml
Systemd Service:   /etc/systemd/system/kubelet.service.d/
```

## 🔗 Additional Resources

- [Official Architecture Documentation](https://kubernetes.io/docs/concepts/architecture/)
- [Components Overview](https://kubernetes.io/docs/concepts/overview/components/)
- [API Conventions](https://github.com/kubernetes/community/blob/master/contributors/devel/sig-architecture/api-conventions.md)

---

**Next Module**: [02 - Cluster Installation & Configuration](../02-cluster-installation/README.md)
