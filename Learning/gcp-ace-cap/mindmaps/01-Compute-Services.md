# GCP Compute Services - Detailed Mindmap & Design

## 1. Compute Engine (GCE) - IaaS
*   **Virtual Machine Instances**
    *   **Machine Families**
        *   *General Purpose*: E2 (Day-to-day), N2 (Balanced), N2D (AMD), T2A (Arm).
        *   *Compute Optimized*: C2 (High perf computing, gaming), C2D.
        *   *Memory Optimized*: M1, M2, M3 (Large in-memory DBs like SAP HANA).
        *   *Accelerator Optimized*: A2 (A100 GPUs), G2 (L4 GPUs) - ML/HPC.
    *   **Machine Types**
        *   *Predefined*: Fixed vCPU/RAM ratio (e.g., `n2-standard-4`).
        *   *Custom*: You pick vCPU and RAM (within limits).
        *   *Shared Core*: `e2-micro`, `f1-micro` (Burstable, free tier eligible).
    *   **Lifecycle**
        *   `PROVISIONING` -> `STAGING` -> `RUNNING`.
        *   `STOPPING` -> `STOPPED` (No CPU cost, Disk cost remains).
        *   `TERMINATED` (Deleted).
        *   `SUSPENDED` (Memory saved to disk, cheaper than running).
        *   *Reset*: Hard reboot (OS doesn't shut down gracefully).
    *   **Preemptible / Spot VMs**
        *   Up to 91% discount.
        *   Google can reclaim with 30s notice.
        *   *Spot*: No max duration.
        *   *Preemptible (Legacy)*: Max 24h duration.
        *   *Use Case*: Batch jobs, fault-tolerant workloads.

*   **Storage Options**
    *   **Persistent Disks (PD)** - Network Attached
        *   *Standard (pd-standard)*: HDD. Backup/Archive.
        *   *Balanced (pd-balanced)*: SSD. Best price/perf. Default.
        *   *SSD (pd-ssd)*: High IOPS. Databases.
        *   *Extreme (pd-extreme)*: Max IOPS. SAP HANA.
        *   *Scope*: Zonal (default) or Regional (Synchronous replication for HA).
        *   *Features*: Snapshots (Incremental, Global), Resize (Online), Encrypted (Google or CMEK).
    *   **Local SSD**
        *   Physically attached to server.
        *   Very high IOPS/Throughput.
        *   *Ephemeral*: Data lost on stop/terminate (but survives reboot).
        *   *Use Case*: Cache, Scratch space, NoSQL hot data.
    *   **Cloud Storage Buckets**
        *   Mount using gcsfuse (High latency, infinite capacity).

*   **Images & Snapshots**
    *   **Public Images**: Provided by Google/Vendors (Debian, Ubuntu, Windows, RHEL).
    *   **Custom Images**: Created from disk, snapshot, or other image.
    *   **Snapshots**:
        *   Incremental (pay only for changes).
        *   Stored in GCS (Regional or Multi-regional).
        *   Application Consistent (VSS on Windows, fsfreeze on Linux).
    *   **Machine Images**: Captures all config (VM metadata, permissions) + Disks.

*   **Instance Groups**
    *   **Managed Instance Groups (MIG)**
        *   *Stateless*: Auto-scaling, Auto-healing.
        *   *Stateful*: Preserves disk/metadata on restart (Databases).
        *   *Auto-healing*: Recreates VM if Health Check fails.
        *   *Auto-scaling*: Based on CPU, LB capacity, or Custom Metric (Stackdriver).
        *   *Updates*: Rolling updates (zero downtime), Canary testing.
        *   *Availability*: Zonal (Single zone) or Regional (Multi-zone protection).
    *   **Unmanaged Instance Groups**
        *   Legacy. Group dissimilar VMs.
        *   Used for legacy Load Balancing. No auto-scaling.

## 2. Google Kubernetes Engine (GKE) - CaaS
*   **Cluster Architecture**
    *   **Control Plane** (Master): API Server, Scheduler, Controller Manager, etcd. Managed by Google.
    *   **Nodes** (Workers): GCE VMs running Kubelet, Kube-proxy, Container Runtime.
*   **Operation Modes**
    *   **Standard Mode**
        *   You manage Node Pools (OS, version, machine type).
        *   Pay for underlying GCE instances.
        *   Max flexibility (Custom system configs).
    *   **Autopilot Mode**
        *   Google manages Nodes completely.
        *   Pay for Pod requests (vCPU/RAM).
        *   Security best practices enforced.
        *   SLA covers Pods.
*   **Cluster Types**
    *   **Zonal**: Single control plane. Cheapest. No HA for API.
    *   **Regional**: 3 control planes across zones. HA (99.95%).
    *   **Private Cluster**: Nodes have no public IPs. Control plane can be private or public-access-restricted.
*   **Networking**
    *   **VPC-Native**: Pods get IPs from VPC secondary range (Alias IPs). Better performance.
    *   **Load Balancing**:
        *   *Ingress*: HTTP(S) LB (L7).
        *   *Service (LoadBalancer)*: Network LB (L4).
    *   **Network Policy**: Firewall for Pods (Calico/Cilium).

## 3. Cloud Run - Serverless Containers
*   **Core Features**
    *   Stateless containers (Knative based).
    *   Scale to Zero (No cost when idle).
    *   **Concurrency**: Handle up to 1000 requests per instance (vs 1 for Cloud Functions).
    *   **Timeouts**: Up to 60 mins.
*   **Services vs. Jobs**
    *   **Services**: Listen for HTTP requests. Web apps, APIs.
    *   **Jobs**: Run to completion. Batch processing, DB migrations.
*   **Triggers**
    *   HTTPS (Public or Private).
    *   Eventarc (Pub/Sub, GCS events, Audit Logs).
*   **Security**
    *   **Invoker Role**: `roles/run.invoker` (Control who can call).
    *   **Service Identity**: SA attached to revision.
    *   **Ingress Control**: Allow `All`, `Internal`, or `Internal + LB`.
    *   **VPC Connector**: Access private VPC resources (Cloud SQL, Redis).

## 4. App Engine (GAE) - PaaS
*   **Standard Environment**
    *   *Runtimes*: Python, Java, Node, Go, PHP, Ruby.
    *   *Startup*: Seconds.
    *   *Scaling*: Zero to Infinity.
    *   *Pricing*: Instance hours (F instance classes).
    *   *Constraints*: Sandbox (No local write), specific versions.
*   **Flexible Environment**
    *   *Runtimes*: Docker (Any language).
    *   *Startup*: Minutes.
    *   *Scaling*: Min 1 instance (No scale to zero).
    *   *Pricing*: vCPU + RAM + Disk (GCE pricing).
    *   *Features*: SSH access, Background threads, Local disk.
*   **Traffic Splitting**
    *   IP-based (Sticky).
    *   Cookie-based (Precise).
    *   Random.
    *   *Use*: Canary, A/B Testing, Blue/Green.
*   **Config Files**
    *   `app.yaml`: Service config.
    *   `dispatch.yaml`: Routing rules between services.
    *   `cron.yaml`: Scheduled tasks.

## 5. Cloud Functions - FaaS
*   **Generations**
    *   **1st Gen**:
        *   Google proprietary build.
        *   HTTP or Background triggers.
    *   **2nd Gen** (Recommended):
        *   Built on Cloud Run.
        *   Longer processing (60 min vs 9 min).
        *   Larger instances (16GB vs 8GB).
        *   Traffic splitting support.
*   **Triggers**
    *   **HTTP**: Webhooks, APIs.
    *   **Cloud Storage**: `finalize` (upload), `delete`.
    *   **Pub/Sub**: Message published.
    *   **Firestore**: Document create/update/delete.
*   **Use Cases**
    *   Lightweight ETL.
    *   Glue code between services.
    *   File processing (Thumbnail generation).
    *   Webhook handling.

---

## 🧠 Design Decision Guide: Compute

| Feature | Compute Engine | GKE | App Engine | Cloud Run | Cloud Functions |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Abstraction** | IaaS (VMs) | CaaS (K8s) | PaaS (App) | Serverless Ctnr | FaaS (Code) |
| **Ops Effort** | High | Medium | Low | Low | Lowest |
| **Scale to Zero** | No | No (Autopilot: Yes*) | Std: Yes, Flex: No | Yes | Yes |
| **Stateful?** | Yes | Yes (StatefulSets) | No | No | No |
| **Max Timeout** | Unlimited | Unlimited | Std: 60m, Flex: 60m | 60m | 1st: 9m, 2nd: 60m |
| **Best For** | Legacy, OS control, DBs | Microservices, Complex Apps | Web Apps, Monoliths | Web/Event Containers | Event Snippets |
