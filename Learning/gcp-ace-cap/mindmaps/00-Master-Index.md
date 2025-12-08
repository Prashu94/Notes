# GCP Associate Cloud Engineer (ACE) - Master Mindmap & Design Guide

This guide provides a structured mindmap of GCP services and design patterns to help you visualize and remember key concepts for the ACE exam.

## 📂 Detailed Mindmaps
For deep-dives into specific domains, refer to the detailed guides:
*   [01-Compute-Services.md](./01-Compute-Services.md)
*   [02-Storage-Database-Services.md](./02-Storage-Database-Services.md)
*   [03-Networking-Services.md](./03-Networking-Services.md)
*   [04-Security-IAM.md](./04-Security-IAM.md)
*   [05-Operations-Management.md](./05-Operations-Management.md)

## 🧠 Master Mindmap (Summary)

### 1. Compute Services
*   **Compute Engine (GCE)** - *IaaS (Virtual Machines)*
    *   **Machine Types**
        *   *General Purpose*: E2, N2 (Balanced)
        *   *Compute Optimized*: C2 (High CPU)
        *   *Memory Optimized*: M2 (High RAM)
        *   *Shared Core*: f1-micro, g1-small (Burstable, cheap)
    *   **Disks**
        *   *Persistent Disk (PD)*: Network storage, durable.
            *   Standard (HDD), Balanced (SSD), SSD (High IOPS).
            *   Zonal vs. Regional (HA).
        *   *Local SSD*: Physically attached, ephemeral, super fast, lost on stop.
    *   **Lifecycle**: Provisioning -> Staging -> Running -> Stopping -> Terminated.
    *   **Images**: Public (OS) vs. Custom (Your config).
    *   **Snapshots**: Incremental backups of PDs. Global access.
    *   **Preemptible/Spot VMs**: Cheap (up to 91% off), short-lived (24h max for Preemptible), can be stopped anytime.
    *   **Instance Groups**
        *   *Managed (MIG)*: Auto-scaling, Auto-healing, Multi-zone (Regional).
        *   *Unmanaged*: Group dissimilar VMs (legacy).

*   **Google Kubernetes Engine (GKE)** - *CaaS (Managed Kubernetes)*
    *   **Modes**
        *   *Standard*: You manage nodes (OS, upgrades). Pay for nodes.
        *   *Autopilot*: Google manages nodes. Pay for Pods (CPU/RAM). Best for ops-light.
    *   **Cluster Types**
        *   *Zonal*: Single zone control plane (No HA).
        *   *Regional*: Multi-zone control plane (HA).
    *   **Node Pools**: Groups of nodes with same config.
    *   **Networking**: VPC-native (Alias IPs), Load Balancing (Ingress/Service).

*   **App Engine (GAE)** - *PaaS (Web Apps)*
    *   **Standard Environment**
        *   Scale to zero (Free).
        *   Specific runtimes (Python, Java, Go, etc.).
        *   Sandbox (No local file write).
        *   Fast startup.
    *   **Flexible Environment**
        *   Docker containers.
        *   Min 1 instance (Always paying).
        *   Access to background processes/disk.
        *   Longer startup.
    *   **Traffic Splitting**: Canary deployments, A/B testing.
    *   **Config**: `app.yaml`.

*   **Cloud Run** - *Serverless Containers*
    *   **Unit**: Stateless Container.
    *   **Trigger**: HTTP (Web) or Eventarc (Events).
    *   **Scaling**: 0 to N. Fast.
    *   **Concurrency**: Multiple requests per container instance.
    *   **Services** (Web) vs. **Jobs** (Batch).

*   **Cloud Functions** - *FaaS (Event-driven snippets)*
    *   **Unit**: Single function (Code snippet).
    *   **Triggers**: HTTP, Cloud Storage, Pub/Sub, Firestore.
    *   **Generations**:
        *   *1st Gen*: Specific runtimes.
        *   *2nd Gen*: Built on Cloud Run, longer timeouts, larger instances.

### 2. Storage Services
*   **Object Storage**
    *   **Cloud Storage (GCS)** - *Unstructured (Files, Blobs)*
        *   *Classes*:
            *   Standard (Hot, freq access).
            *   Nearline (Once/mo).
            *   Coldline (Once/qtr).
            *   Archive (Once/yr).
        *   *Versioning*: Protect against overwrites/deletes.
        *   *Lifecycle Policies*: Auto-move to cheaper class or delete (TTL).
        *   *Access*: IAM (Bucket level) vs. ACL (Object level - legacy). Signed URLs (Temp access).

*   **Relational Databases (SQL)**
    *   **Cloud SQL** - *Regional RDBMS*
        *   Engines: MySQL, PostgreSQL, SQL Server.
        *   Capacity: Up to ~64TB.
        *   Scaling: Vertical (Machine type). Read Replicas (Horizontal Read).
        *   HA: Regional failover (Active/Standby).
    *   **Cloud Spanner** - *Global RDBMS*
        *   Scale: Horizontal (Unlimited).
        *   Consistency: Strong (Global).
        *   Use case: Global scale, >64TB, high transaction rate, 99.999% SLA.

*   **NoSQL Databases**
    *   **Firestore** - *Document Store*
        *   Mode: Native (Mobile/Web, Real-time) vs. Datastore (Server).
        *   Structure: Collection -> Document -> Subcollection.
        *   Queries: Shallow (can't join).
    *   **Cloud Bigtable** - *Wide-Column Store*
        *   Use case: High throughput writes (IoT, AdTech, FinTech).
        *   Interface: HBase compatible.
        *   Key Design: Row Key is critical for performance (avoid hotspots).
        *   Storage: HDD vs. SSD.

*   **Analytical**
    *   **BigQuery** - *Data Warehouse*
        *   Serverless SQL.
        *   Storage/Compute separated.
        *   *Partitioning*: Split by time/integer (Cost/Perf optimization).
        *   *Clustering*: Sort within partitions.

### 3. Networking Services
*   **VPC (Virtual Private Cloud)**
    *   Global resource.
    *   **Subnets**: Regional.
    *   **Firewall Rules**: Stateful. Allow/Deny. Tags/Service Accounts.
    *   **Routes**: Direct traffic.
    *   **Peering**: Connect two VPCs (Non-transitive).
    *   **Shared VPC**: Centralized network control (Host project), decentralized usage (Service projects).

*   **Load Balancing**
    *   **Global HTTP(S)**: Layer 7. Web traffic. Anycast IP.
    *   **Global SSL Proxy / TCP Proxy**: Layer 4. Non-HTTP.
    *   **Regional Network (External)**: Layer 4. UDP/TCP. Passthrough. Preserves Client IP.
    *   **Internal HTTP(S)**: Layer 7 internal.
    *   **Internal TCP/UDP**: Layer 4 internal.

*   **Hybrid Connectivity**
    *   **Cloud VPN**: IPsec tunnel over internet.
        *   *HA VPN*: 99.99% SLA. Dynamic routing (BGP).
    *   **Cloud Interconnect**: Physical link.
        *   *Dedicated*: Direct to Google. High bandwidth (10/100G).
        *   *Partner*: Via service provider. Variable bandwidth.
    *   **Cloud Router**: Dynamic routing (BGP) for VPN/Interconnect.

### 4. Identity & Security
*   **IAM (Identity & Access Management)**
    *   **Principals**: User, Group (Best practice), Service Account.
    *   **Roles**:
        *   *Primitive*: Owner, Editor, Viewer (Avoid).
        *   *Predefined*: Granular (e.g., Storage Object Viewer).
        *   *Custom*: User-defined.
    *   **Policy**: Hierarchy (Org -> Folder -> Project -> Resource). Inheritance.

*   **Service Accounts (SA)**
    *   Identity for machines/apps.
    *   Keys: Managed (Google) vs. User-managed (JSON - Avoid).
    *   Scopes: Legacy access control (Use IAM instead).

*   **Security Tools**
    *   **Cloud Armor**: WAF, DDoS protection (Global LB).
    *   **IAP (Identity-Aware Proxy)**: Zero-trust access to VMs (SSH/RDP) and Web Apps without VPN.
    *   **KMS (Key Management Service)**: Manage encryption keys (CMEK).
    *   **Secret Manager**: Store API keys, passwords.

### 5. Operations & Management
*   **Cloud Operations (Stackdriver)**
    *   **Logging**: Centralized logs. Sinks (Export to BQ, GCS, Pub/Sub).
    *   **Monitoring**: Metrics, Dashboards, Uptime Checks, Alerts.
    *   **Trace**: Latency analysis.
    *   **Profiler**: CPU/RAM profiling.

*   **Billing**
    *   **Account**: Who pays.
    *   **Budget**: Alerts (doesn't stop spending).
    *   **Export**: To BigQuery for analysis.

### 6. Data & Analytics Services
*   **Data Integration**
    *   **Pub/Sub** - *Global Messaging*
        *   Decouples services (Async).
        *   *Push* vs. *Pull* subscriptions.
        *   Global by default.
    *   **Dataflow** - *ETL / Processing*
        *   Apache Beam based.
        *   Unified Batch and Stream processing.
        *   Fully managed, auto-scaling.
    *   **Dataproc** - *Managed Hadoop/Spark*
        *   Lift & shift existing Hadoop/Spark clusters.
        *   Ephemeral clusters (create, process, delete) for cost saving.

### 7. DevOps & Tools
*   **CI/CD**
    *   **Cloud Build** - *Serverless CI/CD*
        *   Builds containers, artifacts.
        *   `cloudbuild.yaml`.
    *   **Artifact Registry** - *Container/Package Store*
        *   Replaces Container Registry (GCR).
        *   Stores Docker images, Maven, npm, etc.
    *   **Source Repositories** - *Private Git*
        *   Mirror GitHub/Bitbucket or host private repos.

*   **Management**
    *   **Cloud Shell** - *Admin Machine*
        *   Browser-based terminal.
        *   Pre-installed tools (gcloud, kubectl, terraform).
        *   5GB persistent home directory.
    *   **Deployment Manager** - *IaC (Legacy)*
        *   YAML/Python based infrastructure as code.
        *   (Note: Terraform is often preferred in real world, but DM is Google native).

---

## 📐 Design Patterns & Decision Guides

### 1. Compute Decision Tree
*   **Need OS control / Legacy App?** -> **Compute Engine**
*   **Containerized?**
    *   *Need Orchestration / Complex / Stateful?* -> **GKE**
    *   *Stateless / Web / Event-driven?* -> **Cloud Run**
*   **Code Snippet / Event-driven?** -> **Cloud Functions**
*   **Web App (Standard languages)?** -> **App Engine**

### 2. Storage Decision Tree
*   **Structured (SQL)?**
    *   *Global / Massive Scale?* -> **Spanner**
    *   *Regional / Standard Scale?* -> **Cloud SQL**
*   **Unstructured (Files)?** -> **Cloud Storage**
*   **Semi-Structured (NoSQL)?**
    *   *Mobile / Web / Hierarchical?* -> **Firestore**
    *   *High Throughput / Flat / IoT?* -> **Bigtable**
*   **Analytical (OLAP)?** -> **BigQuery**

### 3. Load Balancer Decision Tree
*   **Traffic Type?**
    *   *HTTP(S)?*
        *   Global? -> **Global HTTP(S) LB**
        *   Regional/Internal? -> **Internal HTTP(S) LB**
    *   *TCP/UDP?*
        *   Global / SSL Offload? -> **SSL/TCP Proxy**
        *   Regional / Passthrough / UDP? -> **Network LB**

### 4. Common Architectures

#### A. Scalable Web Application
*   **Frontend**: Global HTTP(S) Load Balancer (Anycast IP).
*   **Compute**: Managed Instance Group (MIG) with Auto-scaling across zones.
*   **Database**: Cloud SQL (Regional HA) or Spanner.
*   **Static Assets**: Cloud Storage + Cloud CDN.
*   **Caching**: Cloud Memorystore (Redis).

#### B. Serverless Event Processing
*   **Ingest**: Pub/Sub (Decoupling).
*   **Process**: Cloud Functions or Cloud Run (Triggered by Pub/Sub).
*   **Store**: Firestore (Result data) or BigQuery (Analytics).
*   **Archive**: Cloud Storage (Raw data).

#### C. Hybrid Networking
*   **Connectivity**: HA VPN (Backup/Low volume) or Interconnect (Primary/High volume).
*   **Routing**: Cloud Router (BGP) to exchange routes dynamically.
*   **DNS**: Cloud DNS (Forwarding zones) to resolve on-prem names.
*   **Access**: Private Google Access to reach GCP APIs from private IPs.

#### D. Secure VM Access
*   **No Public IPs**: VMs have only internal IPs.
*   **Outbound Internet**: Cloud NAT (for updates/patching).
*   **Inbound Admin**: IAP (Identity-Aware Proxy) for SSH/RDP tunneling.
*   **Firewall**: Deny all ingress except IAP range (`35.235.240.0/20`).

---

## 📝 Exam Memorization Tips (The "Rule of Thumb")

1.  **"Global SQL"** = Spanner.
2.  **"Hadoop/Spark"** = Dataproc.
3.  **"Kafka"** = Pub/Sub (mostly).
4.  **"Mobile Sync"** = Firestore.
5.  **"IoT / High Write"** = Bigtable.
6.  **"Warehouse / SQL Analytics"** = BigQuery.
7.  **"Lift and Shift"** = Compute Engine.
8.  **"Docker without Ops"** = Cloud Run.
9.  **"Private Access to APIs"** = Private Google Access.
10. **"Private Access to Services"** = Private Service Connect.
11. **"Cost Control"** = Preemptible/Spot VMs + CUDs (Committed Use Discounts).
12. **"Encryption Key Control"** = CMEK (Customer Managed Encryption Keys) with Cloud KMS.
