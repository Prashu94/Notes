# Google Cloud Professional Cloud Architect (PCA) - Compute & GKE Architecture Guide

## 1. GKE Architecture & Design Patterns

### 1.1 Multi-Cluster Architecture (Fleets)
A **Fleet** (formerly Anthos) is a logical grouping of Kubernetes clusters to normalize management, identity, and networking.

#### **Architecture Components**
*   **Fleet Host Project**: The central project where the Fleet is defined.
*   **Member Clusters**:
    *   **GKE (Google Cloud)**: Registered automatically or manually.
    *   **GKE Multi-Cloud**: GKE on AWS / GKE on Azure.
    *   **GKE on Bare Metal / VMWare**: On-premises clusters.
*   **Connect Agent**: A deployment running in the member cluster that establishes a reverse tunnel to Google Cloud. This allows the Google Cloud Console to manage the cluster even if it's behind a firewall (no inbound ports needed).

#### **Key Fleet Features (Deep Dive)**
1.  **Config Sync (GitOps)**:
    *   **Problem**: How to keep 50 clusters in sync?
    *   **Solution**: Store YAML manifests (Policies, Quotas, RBAC) in a Git Repo.
    *   **Mechanism**: An agent on *every* cluster pulls from Git and applies the state. If someone manually changes a setting on the cluster, Config Sync reverts it (Drift Correction).
2.  **Policy Controller (Governance)**:
    *   **Problem**: Developers deploying insecure pods (e.g., running as root).
    *   **Solution**: Enforce policies using OPA Gatekeeper (Rego language).
    *   **Example**: "All images must come from `gcr.io/my-company`".
3.  **Cloud Service Mesh (Managed Istio)**:
    *   **Problem**: Service A in Cluster 1 needs to call Service B in Cluster 2 securely.
    *   **Solution**: mTLS, Traffic Splitting, and Global Observability.
    *   **East-West Traffic**: Traffic between services across clusters flows over the private network (VPC/Interconnect), not the public internet.

### 1.2 Private Clusters: The Security Standard
For PCA, you must understand the network isolation.

*   **Private Nodes**:
    *   Nodes have **only RFC 1918 private IPs**.
    *   They cannot be reached from the internet.
    *   **Outbound Access**: They use **Cloud NAT** to reach the internet (e.g., to pull Docker images from Docker Hub).
*   **Control Plane (Master)**:
    *   In a private cluster, the master has a private IP (VPC Peering) and a public IP (optional).
    *   **Authorized Networks**: You *must* whitelist CIDR ranges that can access the Master's public endpoint (e.g., your corporate VPN IP).
    *   **Private Endpoint Only**: You can disable the public endpoint entirely. Then, you can only access `kubectl` from a VM inside the VPC or via VPN/Interconnect.

## 2. Advanced GKE Networking

### 2.1 VPC-Native Clusters (Alias IPs)
This is the default and recommended mode.

*   **Architecture**:
    *   **Node IP**: Primary CIDR of the Subnet.
    *   **Pod IP**: **Secondary CIDR** range of the Subnet.
*   **Packet Flow**:
    *   Because Pod IPs are real VPC IPs, traffic from a VM to a Pod does **not** need encapsulation (VXLAN/Calico). It is natively routed by the VPC software-defined network.
*   **Benefits**:
    *   **High Performance**: No overlay overhead.
    *   **Direct Visibility**: On-prem firewalls see the Pod IP, not the Node IP.
    *   **Scalability**: Not limited by the Route Quota (Routes-based clusters use static routes, which have a hard limit per VPC).

### 2.2 IP Masquerading (The "Gotcha")
*   **Scenario**: You connect GKE to On-Prem via VPN. On-Prem firewall sees traffic coming from the *Node IP*, not the *Pod IP*. Why?
*   **Reason**: By default, GKE **Masquerades (SNAT)** traffic destined for non-RFC 1918 ranges. If your on-prem uses public IPs (rare but possible) or if the logic is flawed, SNAT hides the Pod IP.
*   **Solution**: **ip-masq-agent**.
    *   ConfigMap lists CIDRs that should *NOT* be masqueraded.
    *   Add your On-Prem CIDR to this list to preserve the Pod IP source.

### 2.3 Gateway API (Multi-Cluster Ingress)
*   **Old Way (MCI)**: `MultiClusterIngress` resource.
*   **New Way (Gateway API)**:
    *   **Gateway**: Represents the Load Balancer (Global External LB).
    *   **HTTPRoute**: Defines the logic (`host: store.com` -> `service: store-frontend`).
    *   **ServiceExport / ServiceImport**: The magic that makes a Service in Cluster A visible to the Gateway in the Config Cluster.

## 3. GKE Security Architecture

### 3.1 Workload Identity (The "No Keys" Rule)
**Never** download a JSON Service Account key for a Pod.

**The Flow (Step-by-Step)**:
1.  **Create GSA**: Create a Google Service Account (`app-gsa@project.iam...`).
2.  **Create KSA**: Create a Kubernetes Service Account (`app-ksa`).
3.  **Bind**: Allow KSA to impersonate GSA.
    ```bash
    gcloud iam service-accounts add-iam-policy-binding app-gsa...         --role roles/iam.workloadIdentityUser         --member "serviceAccount:my-project.svc.id.goog[default/app-ksa]"
    ```
4.  **Annotate**: Tell KSA which GSA to use.
    ```bash
    kubectl annotate sa app-ksa iam.gke.io/gcp-service-account=app-gsa@...
    ```
5.  **Result**: When the Pod starts, the GKE Metadata Server intercepts requests to `metadata.google.internal`. It validates the KSA signature and exchanges it for a short-lived OAuth2 token for the GSA.

### 3.2 Binary Authorization (Supply Chain)
*   **Concept**: Prevent "rogue" containers from running.
*   **Attestor**: A person or system that verifies an image.
*   **Workflow**:
    1.  CI/CD Pipeline builds image.
    2.  Vulnerability Scanner checks image. **Pass**.
    3.  **Attestor** signs the image digest using Cloud KMS Asymmetric Key.
    4.  GKE Admission Controller checks: "Does this image have a valid signature from the QA Attestor?"
    5.  If yes -> Allow. If no -> Block.

## 4. Compute Engine Advanced Design

### 4.1 Sole-Tenant Nodes
*   **What**: You rent the *entire physical server*.
*   **Why?**:
    1.  **Compliance**: "No shared hardware" requirements (Gov/Fin).
    2.  **Licensing**: BYOL (Bring Your Own License) for Windows/Oracle often requires counting physical cores.
    3.  **Performance**: Ensure no "noisy neighbor" steals your L3 cache.

### 4.2 Migration Strategies
*   **Migrate to Virtual Machines (M4CE)**:
    *   **Agentless**: Uses snapshots (for VMWare).
    *   **Testing**: You can clone a VM to the cloud, test it, and then sync the delta before cutover.
*   **Migrate to Containers (m2c)**:
    *   **Discovery**: Scans the VM to find running apps (Tomcat, Apache, WordPress).
    *   **Extraction**: Copies the binaries and config files.
    *   **Containerization**: Generates a `Dockerfile` and Kubernetes YAML.
    *   **Best For**: Linux web servers, App servers.
    *   **Avoid For**: Complex stateful apps (Oracle DB), proprietary kernels.

## 5. Decision Tree: Compute Selection

| Requirement | Recommended Service | Reason |
| :--- | :--- | :--- |
| **Stateless HTTP, Scale-to-Zero** | **Cloud Run** | Lowest ops, pay-per-use. |
| **Microservices, Custom Protocols (gRPC, WebSockets)** | **GKE Autopilot** | Industry standard, rich ecosystem. |
| **Legacy App, Specific OS Kernel, GPU** | **GKE Standard** | Full control over nodes. |
| **COTS App, Windows, Persistent State** | **Compute Engine** | Replicates on-prem environment. |
| **VMware Lift-and-Shift** | **GCVE (VMware Engine)** | Keep same tools (vCenter), no refactoring. |
