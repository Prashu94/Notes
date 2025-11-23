# Google Cloud Certified Associate Cloud Engineer (ACE) - Compute Engine & GKE Guide

## 1. Google Kubernetes Engine (GKE) Fundamentals

### 1.1 GKE Modes of Operation: Deep Dive
Choosing the right mode is the first critical decision.

#### **Autopilot (The "Serverless" K8s Experience)**
*   **Concept**: Google acts as your SRE. You provide the manifests, Google provisions the infrastructure.
*   **Management**:
    *   **Nodes**: Completely hidden. You cannot SSH into them. Google handles OS patching, upgrades, and bin-packing.
    *   **Security**: Enforces best practices by default (e.g., no privileged containers, shielded nodes enabled).
*   **Pricing Model**:
    *   You are billed for the **resources requested** by your Pods (vCPU, Memory, Ephemeral Storage).
    *   *Advantage*: No "bin-packing tax". If your node is 50% empty, you don't pay for the empty space.
*   **Limitations**:
    *   Cannot use custom admission controllers that modify pods.
    *   Cannot use hostPath volumes (security risk).

#### **Standard (The "I Need Control" Experience)**
*   **Concept**: You manage the underlying infrastructure (Compute Engine VMs).
*   **Management**:
    *   **Nodes**: You see them as VMs in GCE. You can SSH, install custom drivers, or run specific OS images (e.g., Windows, Ubuntu).
    *   **Upgrades**: You configure maintenance windows and release channels, but you are responsible for ensuring your apps handle node drains correctly.
*   **Pricing Model**:
    *   You pay for the **underlying Compute Engine instances**, regardless of utilization.
    *   *Risk*: If your nodes are 90% idle, you still pay 100% of the cost.
*   **Use Cases**:
    *   Installing custom agents (e.g., specific security scanners).
    *   Using GPUs/TPUs (though Autopilot now supports some GPUs).
    *   Running legacy apps that need `privileged` mode.

### 1.2 Cluster Architecture & High Availability
Understanding the control plane is vital for the exam.

*   **Zonal Cluster**:
    *   **Structure**: One Control Plane (Zone A) + Nodes (Zone A).
    *   **Risk**: If Zone A goes down, the **Control Plane is unavailable** (cannot deploy new pods, no API access). Existing pods *might* keep running, but self-healing stops.
    *   **SLA**: 99.5%.
*   **Regional Cluster**:
    *   **Structure**: Three Control Planes (Zones A, B, C) + Nodes spread across Zones A, B, C.
    *   **Benefit**: If Zone A fails, the API server fails over to Zone B/C automatically. Zero downtime for management.
    *   **Cost**: You pay a management fee (approx /bin/zsh.10/hr) for the cluster (waived for the first cluster per billing account).
    *   **SLA**: 99.95%.

### 1.3 Creating Clusters (CLI Deep Dive)
The `gcloud` command has many flags. Here are the critical ones for the exam.

**Create a Production-Ready Standard Cluster:**
```bash
gcloud container clusters create prod-cluster \
    --region us-central1 \              # Regional cluster (High Availability)
    --num-nodes 3 \                      # 3 nodes PER ZONE (Total 9 nodes!)
    --machine-type e2-standard-4 \       # Balanced machine type
    --enable-ip-alias \                  # VPC-native (Critical for performance)
    --release-channel regular \          # Auto-upgrade channel
    --scopes "https://www.googleapis.com/auth/cloud-platform" \ # Access to all APIs (controlled by IAM)
    --enable-private-nodes \             # Security: Nodes have no public IPs
    --master-ipv4-cidr 172.16.0.0/28    # Private IP range for Control Plane
```

**Key Flags Explained:**
*   `--enable-ip-alias`: Creates a **VPC-native** cluster. Pods get IPs from a secondary range in the subnet. This is required for Network Policies, Private Clusters, and Alias IPs.
*   `--num-nodes`: In a regional cluster, this is the count **per zone**.
*   `--scopes`: Legacy access method. Modern best practice is to use **Workload Identity**, but for the exam, know that this controls what the *Node* can do.

## 2. GKE Node Management (Standard Mode)

### 2.1 Node Pools: Strategy & Operations
A cluster can have multiple node pools to mix hardware types.

**Scenario**: You have a web app (low CPU) and an ML worker (needs GPU).
*   **Solution**: Create two pools.
    1.  `default-pool`: `e2-medium` for the web app and system pods.
    2.  `gpu-pool`: `n1-standard-4` with `nvidia-tesla-t4` attached.

**Taints and Tolerations**:
*   To ensure *only* ML workloads run on the expensive GPU nodes, you **Taint** the node pool.
*   **Command**:
    ```bash
    gcloud container node-pools create gpu-pool ... --node-taints=dedicated=ml:NoSchedule
    ```
*   **Effect**: No pod will be scheduled there unless it has a matching **Toleration** in its YAML.

### 2.2 Cluster Autoscaler (CA)
*   **How it works**: It checks for **Pending Pods**. If a Pod cannot be scheduled because of insufficient CPU/RAM, CA adds a node.
*   **Scale Down**: If a node is underutilized (e.g., < 50%) for a set time (default 10m), CA drains it and deletes it.
*   **Configuration**:
    ```bash
    gcloud container clusters update my-cluster \
        --enable-autoscaling \
        --min-nodes 1 \
        --max-nodes 100 \
        --node-pool default-pool
    ```
*   **Exam Tip**: CA does NOT scale based on CPU usage percentage. It scales based on *scheduling feasibility*. (HPA scales based on CPU).

## 3. Deploying Workloads: The Kubernetes Objects

### 3.1 Workload Types Explained
1.  **Deployment**:
    *   **What**: The standard for stateless apps (Web servers, APIs).
    *   **Features**: Self-healing (restarts crashed pods), Scaling (replicas), Rolling Updates (zero downtime).
    *   **YAML Key**: `kind: Deployment`.
2.  **StatefulSet**:
    *   **What**: For databases or apps needing persistent identity (Kafka, Zookeeper, MySQL).
    *   **Features**:
        *   **Stable Network ID**: `web-0`, `web-1`. (Deployment pods get random hashes).
        *   **Ordered Deployment**: Starts `web-0`, waits for it to be ready, then starts `web-1`.
        *   **Persistent Storage**: Each pod gets its own PVC that sticks with it if it restarts.
3.  **DaemonSet**:
    *   **What**: Runs exactly **one pod per node**.
    *   **Use Case**: Log collectors (Fluentd), Monitoring agents (Prometheus Node Exporter).
    *   **Behavior**: When a new node is added (by Autoscaler), the DaemonSet automatically spawns a pod on it.
4.  **Job / CronJob**:
    *   **Job**: Runs to completion (exit code 0) then stops. (e.g., Database migration).
    *   **CronJob**: Scheduled Job (e.g., "Run backup every night at 3 AM").

### 3.2 Horizontal Pod Autoscaler (HPA)
Scales the *number of replicas* based on metrics.

**Step 1: Define Resources (Critical)**
HPA *cannot* work if you don't define CPU requests in your Deployment YAML.
```yaml
resources:
  requests:
    cpu: "250m"  # 1/4 of a vCPU
```

**Step 2: Create HPA**
```bash
kubectl autoscale deployment my-app --cpu-percent=60 --min=1 --max=20
```
*   **Logic**: If average CPU usage across all pods > 60% of the *requested* 250m, add more pods.

## 4. Exposing Services (Networking)

### 4.1 Service Types: The Traffic Flow
1.  **ClusterIP (Internal)**:
    *   **Traffic**: Pod A -> Service IP -> Pod B.
    *   **Scope**: Only reachable from *inside* the cluster.
    *   **Use Case**: Backend databases, internal microservices.
2.  **NodePort (External - Primitive)**:
    *   **Traffic**: Client -> Node IP:30000 -> Service -> Pod.
    *   **Scope**: Opens a port (30000-32767) on *every* node.
    *   **Downside**: You have to manage the Node IPs. Not secure for production.
3.  **LoadBalancer (External - Standard)**:
    *   **Traffic**: Client -> Google Cloud Load Balancer (IP) -> NodePort -> Pod.
    *   **Scope**: Provisions a real GCP Load Balancer (L4).
    *   **Cost**: You pay for the Load Balancer resource.

### 4.2 Ingress (L7 HTTP/S Routing)
Ingress is not a Service type, but a router that sits in front of services.

**Architecture**:
*   **Ingress Resource**: A YAML file defining rules (e.g., `example.com/api` -> `api-service`).
*   **Ingress Controller**: The software that reads the YAML and configures the Load Balancer. On GKE, this is the **GKE Ingress Controller**.

**Traffic Flow**:
1.  User hits `https://example.com/api`.
2.  **Global External HTTP(S) Load Balancer** receives request.
3.  LB routes request to a Node in the cluster.
4.  Node routes to the Service (ClusterIP).
5.  Service routes to the Pod.

**Exam Tip**: To use Ingress, your Services must be type `NodePort` or `ClusterIP` (with NEG).

## 5. Compute Engine (GCE) Fundamentals

### 5.1 Machine Families: Choosing the Right VM
*   **E2 (Cost-Optimized)**:
    *   **Tech**: Dynamic resource management. You don't get a dedicated core all the time.
    *   **Use Case**: Web servers, dev environments, small databases.
*   **N2 / N2D (General Purpose)**:
    *   **Tech**: Dedicated cores. Balanced CPU/RAM.
    *   **Use Case**: Production web apps, medium databases, caching.
*   **C2 (Compute Optimized)**:
    *   **Tech**: High clock speed (3.0+ GHz).
    *   **Use Case**: Video encoding, gaming servers, high-performance computing (HPC).
*   **M2 (Memory Optimized)**:
    *   **Tech**: Massive RAM (up to 12TB).
    *   **Use Case**: SAP HANA, huge in-memory SQL databases.

### 5.2 Instance Lifecycle & Availability
*   **Live Migration**:
    *   **Feature**: Google can move your running VM to a different host *without* rebooting it (for maintenance).
    *   **Requirement**: "Availability Policy" -> "On host maintenance" = "Migrate".
    *   **Exception**: GPUs and Spot VMs *cannot* live migrate. They will terminate.
*   **Preemptible / Spot VMs**:
    *   **Rule**: Google can reclaim these at any time with a 30-second warning.
    *   **Handling**: You must have a shutdown script to save state/close connections.
    *   **Cost**: Up to 91% cheaper.

### 5.3 Instance Groups (MIGs)
Managed Instance Groups are the foundation of scalable GCE apps.

**Auto-healing (Health Checks)**:
*   **Concept**: MIG pings your app (e.g., HTTP :80/health).
*   **Action**: If app returns 500 or timeout, MIG **recreates** the VM.
*   **Difference from Load Balancer Health Check**:
    *   LB Health Check: Stops sending traffic to bad VM.
    *   MIG Health Check: *Deletes and replaces* the bad VM.

**Updates (Rolling Replace)**:
*   **Command**:
    ```bash
    gcloud compute instance-groups managed rolling-action start-update my-mig \
        --version template=v2-template \
        --max-unavailable 1
    ```
*   **Logic**: Updates VMs one by one (or in batches) to the new template, ensuring service availability.
