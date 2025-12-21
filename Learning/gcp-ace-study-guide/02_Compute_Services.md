# 02. Compute Services (Masterclass Edition)

This domain is the largest portion of the exam (~30%). It involves selecting, deploying, and managing various compute resources.

---

## 2.1 Compute Engine (GCE) - Deep Dive
GCE is Google's Infrastructure as a Service (IaaS) offering. It provides Virtual Machines (VMs) running on Google's highly scalable infrastructure powered by the **Andromeda** virtual network stack and **Titanium** custom silicon for offload processing.

### 2.1.1 Machine Families & Selection
Choosing the right machine family is critical for cost and performance. Machine families are organized into **series** and **generations** (e.g., N2 is newer than N1).

#### General-Purpose Machine Family
Best price-performance ratio for a variety of workloads.

| Series | Architecture | vCPUs | Memory | Use Cases |
|--------|-------------|-------|--------|-----------|
| **N4/N4D** | Intel Emerald Rapids / AMD Turin | Up to 80/96 | Up to 640/768 GB DDR5 | Flexible workloads, custom shapes |
| **C4/C4D** | Intel Granite Rapids / AMD Turin | Up to 288/384 | Up to 2.2/3 TB DDR5 | High-traffic apps, databases |
| **N2/N2D** | Intel Ice Lake / AMD Milan | Up to 128/224 | Up to 8 GB/vCPU | Web servers, enterprise apps |
| **E2** | Intel/AMD (dynamic) | Up to 32 | Up to 128 GB | Cost-effective dev/test, low-traffic |
| **Tau T2D/T2A** | AMD Milan / Arm | Up to 60/48 | 4 GB/vCPU | Scale-out workloads, microservices |

*   **E2 Limitations**: Does not support Local SSDs, GPUs, sole-tenant nodes, nested virtualization, or sustained use discounts.
*   **Shared-core Types**: `e2-micro`, `e2-small`, `e2-medium` provide CPU bursting for light workloads.

#### Compute-Optimized Machine Family
Highest performance per core for compute-bound workloads.

| Series | vCPUs | Memory | Special Features |
|--------|-------|--------|------------------|
| **H4D** | Up to 192 | 720 GB DDR5 | Cloud RDMA support, HPC |
| **H3** | 88 | 352 GB DDR5 | Molecular dynamics, CFD |
| **C2/C2D** | Up to 60/112 | 4-8 GB/vCPU | Gaming servers, HPC |

#### Memory-Optimized Machine Family
Highest memory-to-compute ratios for in-memory workloads.

| Series | vCPUs | Memory | Use Cases |
|--------|-------|--------|-----------|
| **X4** | Up to 1,920 | 6-32 TB | SAP HANA, large OLTP |
| **M4** | Up to 224 | Up to 26.5 GB/vCPU | High-performance DBs |
| **M3** | Up to 128 | Up to 30.5 GB/vCPU | SAP, analytics |
| **M2** | N/A | 6/9/12 TB options | Extreme memory needs |

#### Accelerator-Optimized Machine Family
Built for AI/ML and massively parallelized CUDA workloads.

| Series | GPUs | GPU Type | Memory | Network |
|--------|------|----------|--------|---------|
| **A4/A4X** | 8/4 | NVIDIA B200 | Up to 3,968 GB | Up to 3,600 Gbps |
| **A3** | 1-8 | NVIDIA H100/H200 | Up to 2,952 GB | Up to 3,200 Gbps |
| **A2** | 1-16 | NVIDIA A100 | Up to 1,360 GB | Up to 100 Gbps |
| **G4/G2** | 1-8 | RTX PRO 6000 / L4 | Up to 1,440/432 GB | Up to 400/100 Gbps |

#### Storage-Optimized Machine Family (Z3)
For storage-intensive workloads with high IOPS and throughput.
*   Up to 176 vCPUs, 1,408 GB memory, 36 TiB Titanium SSD
*   Use for: SQL/NoSQL databases, data analytics, distributed file systems

#### gcloud Examples: Creating VMs
```bash
# Create a general-purpose VM
gcloud compute instances create my-vm \
    --zone=us-central1-a \
    --machine-type=n2-standard-4 \
    --image-family=debian-12 \
    --image-project=debian-cloud

# Create a compute-optimized VM
gcloud compute instances create hpc-vm \
    --zone=us-central1-a \
    --machine-type=c2-standard-60 \
    --image-family=rocky-linux-9-optimized-gcp \
    --image-project=rocky-linux-cloud

# Create a custom machine type (N2 series)
gcloud compute instances create custom-vm \
    --zone=us-central1-a \
    --custom-cpu=6 \
    --custom-memory=32GB \
    --custom-vm-type=n2

# Create an accelerator-optimized VM with GPU
gcloud compute instances create ml-vm \
    --zone=us-central1-a \
    --machine-type=a2-highgpu-1g \
    --image-family=pytorch-latest-gpu \
    --image-project=deeplearning-platform-release \
    --accelerator=type=nvidia-tesla-a100,count=1 \
    --maintenance-policy=TERMINATE
```

### 2.1.2 Pricing and Cost Optimization (Critical Exam Topic)

Understanding VM pricing is essential for cost optimization and the ACE exam.

#### Pricing Models Comparison

| Model | Discount | Commitment | Best For |
|-------|----------|------------|----------|
| **On-Demand** | 0% | None | Unpredictable, short-term workloads |
| **Sustained Use Discounts (SUD)** | Up to 30% | Automatic | Consistent workloads running >25% month |
| **Committed Use Discounts (CUD)** | Up to 70% | 1 or 3 years | Predictable, steady-state workloads |
| **Spot VMs** | Up to 91% | None | Fault-tolerant batch, CI/CD |

#### Sustained Use Discounts (SUD) - Key Points
*   **Automatic**: No action required; discounts apply automatically.
*   **Inferred Instances**: GCE combines usage across VMs of the same type in the same zone.
*   **Does NOT Apply To**: E2, C3, C4, N4 series, Tau T2D/T2A, or GPUs.
*   **Calculation**: Discount increases incrementally as usage exceeds 25%, 50%, 75% of the month.

#### Committed Use Discounts (CUD) - Key Points
*   **Resource-Based CUDs**: Commit to vCPUs and memory; flexible across machine types.
*   **Machine-Type CUDs**: Commit to specific machine types (e.g., `n2-standard-32`).
*   **Spend-Based CUDs**: For GPUs and Local SSDs based on dollar commitment.
*   **Flex CUD**: Short-term commitments (1-3 months) for predictable needs.
*   **Not Refundable**: Cannot be cancelled once purchased.

#### Spot VMs (formerly Preemptible VMs)
*   **Cost Savings**: Up to 91% discount over on-demand pricing.
*   **Preemption**: Google can reclaim with **30-second warning** (ACPI G2 Soft Off signal).
*   **No Maximum Runtime**: Unlike preemptible VMs (24-hour limit), Spot VMs have no runtime limit.
*   **No SLA**: Availability varies by zone and time.
*   **Best Practices**:
    *   Use shutdown scripts to handle termination gracefully.
    *   Spread across multiple zones to reduce preemption impact.
    *   Ideal for: batch processing, CI/CD pipelines, rendering, distributed computing.

```bash
# Create a Spot VM
gcloud compute instances create spot-worker \
    --zone=us-central1-a \
    --machine-type=n2-standard-4 \
    --provisioning-model=SPOT \
    --instance-termination-action=STOP \
    --metadata=shutdown-script='#!/bin/bash
    echo "Preemption detected, saving state..."
    # Add your cleanup logic here'

# Create a preemptible VM (legacy)
gcloud compute instances create preemptible-worker \
    --zone=us-central1-a \
    --machine-type=e2-medium \
    --preemptible

# View CUD recommendations
gcloud recommender recommendations list \
    --project=my-project \
    --location=us-central1 \
    --recommender=google.compute.commitment.UsageCommitmentRecommender
```

#### Rightsizing Recommendations
GCE automatically analyzes VM resource utilization and provides rightsizing recommendations.
```bash
# List rightsizing recommendations
gcloud recommender recommendations list \
    --project=my-project \
    --location=us-central1-a \
    --recommender=google.compute.instance.MachineTypeRecommender
```

### 2.1.3 Storage for VMs (Block Storage Deep Dive)

Google Cloud offers two types of block storage: **Durable (Persistent)** and **Temporary (Local SSD)**.

#### Durable Block Storage Options

| Disk Type | Performance | Max Size | Use Case |
|-----------|-------------|----------|----------|
| **Hyperdisk Balanced** | Customizable IOPS/throughput | 64 TB | General workloads, boot disks |
| **Hyperdisk Extreme** | Up to 350K IOPS | 64 TB | High-IOPS databases (Oracle, SAP) |
| **Hyperdisk Throughput** | Up to 2,400 MB/s | 32 TB | Big data, streaming |
| **Hyperdisk ML** | Read-optimized | 64 TB | AI/ML model serving |
| **SSD Persistent Disk** | Up to 100K IOPS | 64 TB | Databases, high-performance apps |
| **Balanced Persistent Disk** | Up to 80K IOPS | 64 TB | Default choice, cost-effective |
| **Standard Persistent Disk (HDD)** | Sequential workloads | 64 TB | Backups, bulk storage |

*   **Hyperdisk vs Persistent Disk**: Hyperdisk allows independent provisioning of IOPS, throughput, and capacity. Persistent Disk performance scales with size.
*   **Regional Persistent Disk**: Synchronously replicated across two zones for HA. Doubles cost.

#### Local SSD (Temporary Storage)
*   **Physically Attached**: Directly attached to the host server.
*   **Extreme Performance**: Up to 9 GB/s throughput, 2.4M IOPS.
*   **Data Persistence Rules**:
    | Event | Data Preserved? |
    |-------|-----------------|
    | VM Reset/Reboot | ✅ Yes |
    | VM Stop | ❌ No |
    | VM Suspend | ❌ No |
    | VM Delete | ❌ No |
    | Live Migration | ✅ Yes (if supported) |
    | Host Maintenance (Terminate policy) | ❌ No |
    | Host Failure | ❌ No |

*   **Sizes**: 375 GB per disk, up to 36 TiB per VM (depending on machine type).
*   **Best For**: Temporary scratch space, caches, `tmpdb`, swap, ephemeral data.

```bash
# Create a VM with SSD Persistent Disk
gcloud compute instances create db-vm \
    --zone=us-central1-a \
    --machine-type=n2-standard-8 \
    --boot-disk-type=pd-ssd \
    --boot-disk-size=100GB

# Create a VM with Local SSD
gcloud compute instances create cache-vm \
    --zone=us-central1-a \
    --machine-type=n2-standard-4 \
    --local-ssd=interface=NVME \
    --local-ssd=interface=NVME

# Create a Regional Persistent Disk for HA
gcloud compute disks create ha-disk \
    --region=us-central1 \
    --replica-zones=us-central1-a,us-central1-b \
    --size=500GB \
    --type=pd-ssd

# Attach Hyperdisk Balanced with custom performance
gcloud compute disks create hd-balanced \
    --type=hyperdisk-balanced \
    --size=100GB \
    --provisioned-iops=10000 \
    --provisioned-throughput=500 \
    --zone=us-central1-a
```

#### Disk Snapshots
*   **Incremental**: Only changed blocks are stored after the first snapshot.
*   **Global Resource**: Snapshots can restore disks in any region.
*   **Snapshot Schedules**: Automate backups with retention policies.

```bash
# Create a snapshot
gcloud compute disks snapshot my-disk \
    --zone=us-central1-a \
    --snapshot-names=my-snapshot

# Create a snapshot schedule
gcloud compute resource-policies create snapshot-schedule daily-backup \
    --region=us-central1 \
    --start-time=04:00 \
    --daily-schedule \
    --max-retention-days=14

# Attach schedule to a disk
gcloud compute disks add-resource-policies my-disk \
    --zone=us-central1-a \
    --resource-policies=daily-backup
```

### 2.1.4 Availability Policies

Control VM behavior during infrastructure events:

| Policy | Option | Behavior |
|--------|--------|----------|
| **On Host Maintenance** | `MIGRATE` (Default) | Live migrates VM to another host with minimal downtime |
| | `TERMINATE` | Stops the VM during maintenance |
| **Automatic Restart** | `true` (Default) | Restarts VM after crash/maintenance if terminated |
| | `false` | VM stays stopped |
| **Host Error Timeout** | 30 sec - 2 hours | How long to wait for host recovery before terminating |

**Important Constraints**:
*   VMs with Local SSD: Cannot live migrate (must set `TERMINATE`).
*   GPU-attached VMs: Cannot live migrate (must set `TERMINATE`).
*   Spot VMs: Always `TERMINATE`, no live migration.
*   Sole-Tenant Nodes: Live migration only within the same sole-tenant node group.

```bash
# Create VM with specific availability policies
gcloud compute instances create critical-vm \
    --zone=us-central1-a \
    --machine-type=n2-standard-4 \
    --maintenance-policy=MIGRATE \
    --restart-on-failure

# Create VM that terminates on maintenance (for GPU/Local SSD)
gcloud compute instances create gpu-vm \
    --zone=us-central1-a \
    --machine-type=n1-standard-4 \
    --accelerator=type=nvidia-tesla-t4,count=1 \
    --maintenance-policy=TERMINATE \
    --restart-on-failure
```

### 2.1.5 Managed Instance Groups (MIGs)

MIGs allow you to manage a group of identical VMs as a single entity, created from an **Instance Template**.

#### MIG Types Comparison

| Feature | Zonal MIG | Regional MIG |
|---------|-----------|--------------|
| **Zone Distribution** | Single zone | 2-3 zones in region |
| **Availability** | Zone-level | Region-level (survives zone failure) |
| **Capacity** | Full capacity in one zone | Capacity split across zones |
| **Use Case** | Dev/Test, batch jobs | Production workloads |

#### Autoscaling Signals

| Signal Type | Description | Use Case |
|-------------|-------------|----------|
| **CPU Utilization** | Average CPU across instances | General web servers |
| **Load Balancing Capacity** | % of max requests/connections | Behind load balancer |
| **Cloud Monitoring Metric** | Any custom metric | Custom business logic |
| **Pub/Sub Queue Depth** | Messages waiting | Queue processing |
| **Scheduled Scaling** | Time-based scaling | Predictable traffic patterns |

```bash
# Create an Instance Template
gcloud compute instance-templates create web-template \
    --machine-type=n2-standard-2 \
    --image-family=debian-11 \
    --image-project=debian-cloud \
    --boot-disk-size=20GB \
    --tags=http-server \
    --metadata=startup-script='#!/bin/bash
        apt-get update && apt-get install -y nginx'

# Create a Regional MIG with autoscaling
gcloud compute instance-groups managed create web-mig \
    --region=us-central1 \
    --template=web-template \
    --size=3 \
    --zones=us-central1-a,us-central1-b,us-central1-c

# Configure autoscaling
gcloud compute instance-groups managed set-autoscaling web-mig \
    --region=us-central1 \
    --min-num-replicas=2 \
    --max-num-replicas=10 \
    --target-cpu-utilization=0.6 \
    --cool-down-period=90
```

#### Autohealing
Uses **Health Checks** to detect unhealthy instances and automatically recreate them.

```bash
# Create a health check
gcloud compute health-checks create http my-health-check \
    --port=80 \
    --request-path=/health \
    --check-interval=10s \
    --timeout=5s \
    --healthy-threshold=2 \
    --unhealthy-threshold=3

# Apply autohealing to MIG
gcloud compute instance-groups managed update web-mig \
    --region=us-central1 \
    --health-check=my-health-check \
    --initial-delay=300
```

#### Rolling Updates
Update VMs with minimal disruption using update policies.

| Update Type | Behavior |
|-------------|----------|
| **PROACTIVE** | Immediately starts updating instances |
| **OPPORTUNISTIC** | Updates only when instances are recreated |

```bash
# Perform a rolling update with canary
gcloud compute instance-groups managed rolling-action start-update web-mig \
    --region=us-central1 \
    --version=template=web-template-v2 \
    --max-surge=3 \
    --max-unavailable=0

# Canary deployment: 20% new, 80% old
gcloud compute instance-groups managed rolling-action start-update web-mig \
    --region=us-central1 \
    --version=template=web-template-v1,target-size=80% \
    --version=template=web-template-v2,target-size=20%
```

---

## 2.2 Google Kubernetes Engine (GKE) - Orchestration

### 2.2.1 GKE Architecture
*   **Control Plane (Master)**: Managed by Google. Runs the API server, scheduler, etcd, and controller manager. Regional control planes provide HA.
*   **Nodes (Workers)**: VMs that run your containers (Pods). They belong to **Node Pools**.
*   **Node Pools**: Groups of nodes with the same configuration (machine type, disk, labels). A cluster can have multiple node pools.

```bash
# Create a GKE cluster
gcloud container clusters create my-cluster \
    --zone=us-central1-a \
    --num-nodes=3 \
    --machine-type=e2-medium \
    --enable-ip-alias

# Create a regional cluster (HA control plane)
gcloud container clusters create prod-cluster \
    --region=us-central1 \
    --num-nodes=2 \
    --machine-type=n2-standard-4 \
    --enable-ip-alias
```

### 2.2.2 Operational Modes

| Feature | Standard Mode | Autopilot Mode |
|---------|--------------|----------------|
| **Node Management** | You manage nodes | Google manages nodes |
| **Security** | You configure | Pre-hardened, security best practices enforced |
| **Scaling** | Configure node pools + cluster autoscaler | Automatic node provisioning |
| **Billing** | Pay for VMs + $0.10/hr/cluster | Pay per Pod (CPU/RAM/GPU) |
| **Node Access** | SSH access available | No SSH access |
| **Custom Workloads** | Full flexibility | Some restrictions (no privileged pods) |
| **Best For** | Specialized workloads, customization | Most workloads, operational simplicity |

#### Autopilot Compute Classes
In Autopilot, specify compute requirements using **Compute Classes**:

| Compute Class | Description |
|---------------|-------------|
| `general-purpose` | Default, balanced workloads |
| `scale-out` | Cost-optimized, many small pods |
| `balanced` | Balance of compute and memory |
| `accelerator` | GPU workloads |

```yaml
# Pod spec requesting specific compute class
spec:
  nodeSelector:
    cloud.google.com/compute-class: scale-out
```

```bash
# Create an Autopilot cluster
gcloud container clusters create-auto autopilot-cluster \
    --region=us-central1 \
    --release-channel=regular
```

### 2.2.3 Networking and Scaling

#### Network Modes
*   **VPC-Native (Alias IP)**: Pods get IPs from secondary subnet ranges. Required for: Private Google Access, VPC Flow Logs, Network Policies. **Always use for production.**
*   **Routes-Based (Legacy)**: Pods get IPs via custom routes. Limited scalability.

#### IP Address Planning

| Resource | IP Range | Size Consideration |
|----------|----------|-------------------|
| **Nodes** | Primary subnet | # of nodes |
| **Pods** | Secondary range 1 | 110 pods/node default |
| **Services** | Secondary range 2 | # of ClusterIP services |

```bash
# Create VPC-Native cluster with explicit ranges
gcloud container clusters create vpc-native-cluster \
    --zone=us-central1-a \
    --enable-ip-alias \
    --cluster-ipv4-cidr=/17 \
    --services-ipv4-cidr=/22
```

#### Autoscaling Components

| Autoscaler | What It Scales | Based On |
|------------|----------------|----------|
| **HPA** | Pod replicas | CPU/Memory/Custom metrics |
| **VPA** | Pod resource requests | Historical usage |
| **Cluster Autoscaler** | Nodes in node pool | Pending pods |
| **Node Auto-Provisioning** | Creates new node pools | Pod requirements |
| **Multidimensional Pod Autoscaler** | Horizontal + Vertical | Combined signals |

```bash
# Enable cluster autoscaler on a node pool
gcloud container clusters update my-cluster \
    --zone=us-central1-a \
    --enable-autoscaling \
    --min-nodes=1 \
    --max-nodes=10 \
    --node-pool=default-pool

# Enable Node Auto-Provisioning
gcloud container clusters update my-cluster \
    --zone=us-central1-a \
    --enable-autoprovisioning \
    --min-cpu=1 \
    --max-cpu=100 \
    --min-memory=1 \
    --max-memory=256
```

### 2.2.4 GKE Cluster Security

| Cluster Type | Node IPs | Control Plane Access | Use Case |
|--------------|----------|---------------------|----------|
| **Public** | Public | Public endpoint | Development |
| **Private** | Private only | Private endpoint or authorized networks | Production |
| **Private + PSC** | Private only | Private Service Connect | Enterprise (no peering) |

```bash
# Create a private cluster
gcloud container clusters create private-cluster \
    --zone=us-central1-a \
    --enable-private-nodes \
    --enable-private-endpoint \
    --master-ipv4-cidr=172.16.0.0/28 \
    --enable-ip-alias

# Add authorized network for kubectl access
gcloud container clusters update private-cluster \
    --zone=us-central1-a \
    --enable-master-authorized-networks \
    --master-authorized-networks=203.0.113.0/24
```

### 2.2.5 Workload Identity
The recommended way for GKE workloads to access Google Cloud services. Maps Kubernetes Service Accounts to Google Cloud Service Accounts.

```bash
# Enable Workload Identity on cluster
gcloud container clusters update my-cluster \
    --zone=us-central1-a \
    --workload-pool=PROJECT_ID.svc.id.goog

# Create binding between KSA and GSA
gcloud iam service-accounts add-iam-policy-binding \
    GSA_NAME@PROJECT_ID.iam.gserviceaccount.com \
    --role=roles/iam.workloadIdentityUser \
    --member="serviceAccount:PROJECT_ID.svc.id.goog[NAMESPACE/KSA_NAME]"
```

---

## 2.3 App Engine (PaaS)
A platform for building highly scalable web and mobile backends. No infrastructure management required.

### 2.3.1 Standard vs. Flexible Environments

| Feature | App Engine Standard | App Engine Flexible |
| :--- | :--- | :--- |
| **Scaling** | Scale-to-zero (Cold starts exist) | No scale-to-zero (Min 1 instance) |
| **Runtimes** | Sandboxed (Python, Java, Go, Node.js, PHP, Ruby) | Any (Docker container) |
| **Startup Time** | Seconds (milliseconds for warm) | Minutes |
| **OS Access** | None | SSH Access to VMs allowed |
| **Background Tasks** | Limited via Task Queues | Any background processing |
| **Local Disk** | /tmp only (in-memory) | Ephemeral disk available |
| **Max Request Timeout** | 10 minutes | 60 minutes |
| **WebSockets** | Not supported | Supported |
| **Pricing** | Per instance-hour (can be free) | Per vCPU/memory hour |

#### Standard Environment Generations
*   **Gen 1**: Original sandboxed environment. More restrictions.
*   **Gen 2**: Built on gVisor. Fewer restrictions, better compatibility.

```bash
# Deploy to App Engine Standard
gcloud app deploy app.yaml --version=v1

# View deployed versions
gcloud app versions list

# View services
gcloud app services list
```

### 2.3.2 Traffic Splitting & Versioning
Every `gcloud app deploy` creates a new **Version** under a **Service**.

#### Deployment Strategies

| Strategy | Implementation | Use Case |
|----------|----------------|----------|
| **Blue-Green** | Deploy v2, test, switch 100% | Zero-downtime releases |
| **Canary** | 5-10% to v2, monitor, gradually increase | Risk mitigation |
| **A/B Testing** | Split by cookie/IP for user segments | Feature experiments |

```bash
# Deploy new version without routing traffic
gcloud app deploy --no-promote --version=v2

# Split traffic: 90% v1, 10% v2 (Canary)
gcloud app services set-traffic default \
    --splits=v1=0.9,v2=0.1

# Split by IP (sticky sessions)
gcloud app services set-traffic default \
    --splits=v1=0.9,v2=0.1 \
    --split-by=ip

# Split by cookie
gcloud app services set-traffic default \
    --splits=v1=0.9,v2=0.1 \
    --split-by=cookie

# Migrate all traffic to v2
gcloud app services set-traffic default \
    --splits=v2=1 \
    --migrate
```

### 2.3.3 App Engine Configuration (app.yaml)

```yaml
# Standard Environment example
runtime: python39
instance_class: F2
automatic_scaling:
  min_instances: 0
  max_instances: 10
  target_cpu_utilization: 0.65
  target_throughput_utilization: 0.6
  min_pending_latency: 30ms
  max_pending_latency: automatic

handlers:
- url: /static
  static_dir: static
- url: /.*
  script: auto
  secure: always  # Require HTTPS

env_variables:
  ENV: production
```

---

## 2.4 Cloud Run (Knative-based Serverless)
Managed compute for stateless containers. "Serverless Containers" - bring any container, Google handles the rest.

### 2.4.1 Cloud Run Services vs Jobs

| Feature | Cloud Run Services | Cloud Run Jobs |
|---------|-------------------|----------------|
| **Trigger** | HTTP requests | Manual, scheduled, or Workflows |
| **Lifecycle** | Always listening | Runs to completion, then exits |
| **Scaling** | 0 to 1000 instances | Parallel task execution |
| **Timeout** | Up to 60 min (default 5 min) | Up to 24 hours |
| **Use Case** | APIs, web apps, webhooks | Batch jobs, data processing, migrations |

### 2.4.2 Key Characteristics

| Feature | Details |
|---------|---------|
| **Scale to Zero** | $0 when no requests. Perfect for sporadic workloads |
| **Concurrency** | Up to 1000 concurrent requests per instance |
| **CPU Allocation** | Always-on or request-only (cost optimization) |
| **Min Instances** | Keep instances warm to avoid cold starts |
| **Max Instances** | Limit scaling for cost control or downstream protection |
| **Startup Probes** | Verify container is ready before receiving traffic |

```bash
# Deploy a service
gcloud run deploy my-service \
    --image=gcr.io/PROJECT/my-image:latest \
    --region=us-central1 \
    --platform=managed \
    --allow-unauthenticated \
    --cpu=1 \
    --memory=512Mi \
    --concurrency=80 \
    --min-instances=1 \
    --max-instances=100

# Deploy with CPU always allocated (for background work)
gcloud run deploy my-service \
    --image=gcr.io/PROJECT/my-image:latest \
    --region=us-central1 \
    --cpu-boost \
    --no-cpu-throttling

# Create a job
gcloud run jobs create my-job \
    --image=gcr.io/PROJECT/batch-image:latest \
    --region=us-central1 \
    --tasks=10 \
    --parallelism=5 \
    --max-retries=3

# Execute a job
gcloud run jobs execute my-job --region=us-central1
```

### 2.4.3 Traffic Management & Revisions
Every deployment creates an immutable **Revision**. Traffic can be split across revisions.

```bash
# Deploy new revision without routing traffic
gcloud run deploy my-service \
    --image=gcr.io/PROJECT/my-image:v2 \
    --region=us-central1 \
    --no-traffic

# Split traffic (canary)
gcloud run services update-traffic my-service \
    --region=us-central1 \
    --to-revisions=my-service-00001-abc=90,my-service-00002-def=10

# Rollback to previous revision
gcloud run services update-traffic my-service \
    --region=us-central1 \
    --to-revisions=my-service-00001-abc=100

# Gradual rollout
gcloud run services update-traffic my-service \
    --region=us-central1 \
    --to-latest \
    --to-tags=green=10
```

### 2.4.4 Ingress & Egress Configuration

#### Ingress Settings

| Setting | Traffic Allowed |
|---------|----------------|
| `all` | Internet + Internal |
| `internal` | VPC + Cloud Run internal only |
| `internal-and-cloud-load-balancing` | Internal + External LB |

#### VPC Connectivity (Egress)

| Connector Type | Use Case | Throughput |
|----------------|----------|------------|
| **Serverless VPC Access Connector** | Access VPC resources | Up to 1 Gbps |
| **Direct VPC Egress** | No connector needed, simpler | Better performance |

```bash
# Set ingress to internal only
gcloud run services update my-service \
    --region=us-central1 \
    --ingress=internal

# Connect to VPC using Direct VPC Egress
gcloud run services update my-service \
    --region=us-central1 \
    --network=my-vpc \
    --subnet=my-subnet \
    --vpc-egress=all-traffic

# Using VPC Access Connector
gcloud run services update my-service \
    --region=us-central1 \
    --vpc-connector=my-connector \
    --vpc-egress=private-ranges-only
```

### 2.4.5 Cloud Run Pricing Model

| Component | Cost |
|-----------|------|
| **CPU** | Per vCPU-second (request processing or always-on) |
| **Memory** | Per GiB-second |
| **Requests** | $0.40 per million requests |
| **Networking** | Egress charges apply |

**Cost Optimization Tips**:
*   Use `--cpu-throttling` (CPU only during requests) for request-driven workloads.
*   Use `--no-cpu-throttling` only for background processing.
*   Set appropriate `--concurrency` to maximize instance utilization.

---

## 2.5 Cloud Functions (Event-Driven Serverless)

### 2.5.1 Gen 1 vs Gen 2

| Feature | Cloud Functions Gen 1 | Cloud Functions Gen 2 |
|---------|----------------------|----------------------|
| **Runtime** | Limited languages | More languages, longer support |
| **Timeout** | 9 minutes | 60 minutes |
| **Memory** | Up to 8 GB | Up to 32 GB |
| **Concurrency** | 1 request per instance | Up to 1000 (like Cloud Run) |
| **Traffic Splitting** | Not supported | Supported |
| **Min Instances** | Not supported | Supported |
| **Underlying Platform** | Proprietary | Cloud Run |

```bash
# Deploy Gen 2 function (HTTP trigger)
gcloud functions deploy my-function \
    --gen2 \
    --runtime=python311 \
    --region=us-central1 \
    --source=. \
    --entry-point=hello_http \
    --trigger-http \
    --allow-unauthenticated

# Deploy with Pub/Sub trigger
gcloud functions deploy process-message \
    --gen2 \
    --runtime=nodejs18 \
    --region=us-central1 \
    --source=. \
    --entry-point=processMessage \
    --trigger-topic=my-topic

# Deploy with Cloud Storage trigger
gcloud functions deploy process-upload \
    --gen2 \
    --runtime=python311 \
    --region=us-central1 \
    --source=. \
    --entry-point=process_file \
    --trigger-event-filters="type=google.cloud.storage.object.v1.finalized" \
    --trigger-event-filters="bucket=my-bucket"
```

---

## 2.6 Compute Selection Flowchart (The "Exam Logic")

### Decision Tree

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        COMPUTE SELECTION FLOWCHART                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                    Do you need full OS control?
                    (Custom kernel, Windows, GPUs)
                                    │
                    ┌───────────────┴───────────────┐
                   YES                              NO
                    │                               │
              COMPUTE ENGINE                Is it containerized?
                    │                               │
                    │               ┌───────────────┴───────────────┐
                    │              YES                              NO
                    │               │                               │
                    │     Need complex orchestration?      Is it a simple
                    │     (Service mesh, stateful apps)    web app?
                    │               │                               │
                    │   ┌───────────┴───────────┐       ┌───────────┴───────────┐
                    │  YES                      NO     YES                      NO
                    │   │                       │       │                        │
                    │  GKE              Can scale to    APP ENGINE         Event-driven
                    │   │               zero?           (Standard)         code snippet?
                    │   │                       │                               │
                    │   │           ┌───────────┴───────────┐       ┌───────────┴───────────┐
                    │   │          YES                      NO     YES                      NO
                    │   │           │                       │       │                        │
                    │   │       CLOUD RUN           CLOUD RUN   CLOUD               Consider
                    │   │       (Services)          (min-inst)  FUNCTIONS           external
                    │   │                                                           solutions
```

### Quick Reference Table

| Requirement | Best Service | Why |
|-------------|--------------|-----|
| Windows Server | Compute Engine | Only option for Windows |
| GPU/TPU ML training | Compute Engine / GKE | Direct hardware access |
| Kubernetes orchestration | GKE | Native Kubernetes |
| Stateless container API | Cloud Run | Simplest, scales to zero |
| Batch container jobs | Cloud Run Jobs | Parallel task execution |
| Simple web app (Python/Node) | App Engine Standard | No Docker, scales to zero |
| Custom runtime web app | App Engine Flexible | Docker support, no scale to zero |
| Event-driven (Pub/Sub, GCS) | Cloud Functions Gen 2 | Native triggers |
| Long-running background | Compute Engine / GKE | No timeout limits |
| Legacy application | Compute Engine | Lift and shift |

### Cost Comparison (Simplified)

| Service | Scale to Zero | Pay For | Management Overhead |
|---------|---------------|---------|---------------------|
| Compute Engine | ❌ | VM hours | High |
| GKE Standard | ❌ | VM hours + mgmt fee | Medium-High |
| GKE Autopilot | ❌ | Pod resources | Medium |
| App Engine Standard | ✅ | Instance hours | Low |
| App Engine Flexible | ❌ | vCPU/memory hours | Low |
| Cloud Run | ✅ | Request time + resources | Very Low |
| Cloud Functions | ✅ | Invocations + compute time | Very Low |
