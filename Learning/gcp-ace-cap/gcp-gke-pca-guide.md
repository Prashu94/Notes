# Google Kubernetes Engine (GKE) - Professional Cloud Architect (PCA) Comprehensive Guide

## Table of Contents
1. [Architectural Overview](#architectural-overview)
2. [Design Decisions & Trade-offs](#design-decisions--trade-offs)
3. [Networking Architecture](#networking-architecture)
4. [Security Architecture](#security-architecture)
5. [High Availability & Disaster Recovery](#high-availability--disaster-recovery)
6. [Scalability Patterns](#scalability-patterns)
7. [Storage Architecture](#storage-architecture)
8. [Cost Optimization](#cost-optimization)
9. [Multi-Cluster & Hybrid Patterns](#multi-cluster--hybrid-patterns)
10. [Migration Strategies](#migration-strategies)
11. [PCA Exam Tips](#pca-exam-tips)

---

## GKE Architecture Design

### Control Plane Availability

**Zonal Clusters:**
- **Architecture**: Single control plane in one zone. Nodes can be in one zone (Single-Zone) or multiple zones (Multi-Zonal).
- **SLA**: 99.5% for zonal clusters.
- **Use Case**: Dev/Test environments, batch processing, non-critical workloads.
- **Risk**: If the zone fails, the control plane is inaccessible (cannot manage cluster), though workloads may continue running.

**Regional Clusters:**
- **Architecture**: Control plane replicated across 3 zones in a region. Nodes are also distributed across 3 zones by default.
- **SLA**: 99.95% for regional clusters.
- **Use Case**: Production workloads, high availability requirements.
- **Benefit**: Zero downtime during upgrades (control plane replicas upgraded one by one). Resilient to single zone failure.

### GKE Modes: Autopilot vs Standard (Architectural View)

| Feature | Autopilot | Standard |
|---------|-----------|----------|
| **Responsibility** | Google manages nodes, security, scaling. | User manages nodes, system pods, OS config. |
| **SLA** | Covers Pods and Control Plane. | Covers Control Plane (and Nodes if Regional). |
| **Security** | Hardened by default (no SSH, Workload Identity). | Configurable (can be insecure if misconfigured). |
| **Cost Model** | Pay per Pod (vCPU/RAM). Higher unit cost, zero waste. | Pay per Node (VM). Lower unit cost, potential bin-packing waste. |
| **Best For** | Most production workloads, variable traffic, low ops teams. | Specific hardware needs, custom kernel modules, legacy apps requiring node access. |

### Version Management

**Release Channels:**
- **Rapid**: Newest features, less stability. For testing new features.
- **Regular**: Default. Balance of features and stability. For most production apps.
- **Stable**: High stability, older features. For critical, slow-changing apps.

**Maintenance Windows & Exclusions:**
- Configure windows for upgrades to occur during off-peak hours.
- Use exclusions to prevent upgrades during critical business events (e.g., Black Friday).

---

## Networking Architecture

### VPC-Native Clusters (Alias IPs)

**Architecture:**
- Pods get IP addresses from a secondary range in the VPC subnet.
- Pod IPs are natively routable within the VPC and across VPC Peering/VPN/Interconnect.
- No NAT required for Pod-to-Pod communication across nodes.
- **Requirement**: Must be enabled for GKE Autopilot and recommended for Standard.

**Benefits:**
- **Performance**: No route lookup penalty or encapsulation overhead.
- **Scalability**: Supports more Pods per node and cluster.
- **Security**: Firewall rules can target Pod IP ranges directly.
- **Anti-Spoofing**: VPC checks source IPs.

### Private Clusters

**Architecture:**
- **Private Nodes**: Nodes have only internal IP addresses. No public internet access.
- **Private Endpoint**: Control plane has a private internal IP.
- **Public Endpoint (Optional)**: Control plane can also have a public IP (restricted by Authorized Networks).

**Outbound Internet Access:**
- Since nodes have no public IPs, use **Cloud NAT** for outbound internet access (e.g., pulling images from Docker Hub, calling external APIs).
- **Private Google Access**: Enabled on subnet to allow nodes to reach Google APIs (GCR, Cloud Logging) without internet.

### Master Authorized Networks

- Restricts access to the cluster's public endpoint (control plane).
- Whitelist specific CIDR ranges (e.g., corporate VPN, bastion host).
- **Best Practice**: Always enable for public endpoints to prevent unauthorized internet access to the API server.

### Shared VPC (Hub-and-Spoke)

**Architecture:**
- **Host Project**: Contains the VPC network, subnets, and Shared VPC configuration.
- **Service Project**: Contains the GKE cluster.
- **Roles**:
  - Host Project Admin manages network (subnets, firewalls).
  - Service Project Admin manages GKE cluster.
  - GKE Service Account in Service Project needs `Compute Network User` role on the Host Project subnet.

**Use Case:**
- Centralized network management (SecOps/NetOps team).
- Distributed cluster ownership (DevOps teams).
- Separation of duties.

### Ingress and Load Balancing

**1. GKE Ingress Controller (GCE):**
- Creates Google Cloud Load Balancers (GCLB) automatically.
- **External HTTP(S) Load Balancer**: Global, Anycast IP, managed certificates, Cloud Armor integration.
- **Internal HTTP(S) Load Balancer**: Regional, private access within VPC.

**2. Container Native Load Balancing (NEG):**
- Uses **Network Endpoint Groups (NEGs)**.
- Load balancer sends traffic directly to Pod IPs (bypassing kube-proxy/node iptables).
- **Benefits**: Lower latency, better visibility, supports Pod readiness gates.

**3. Multi-Cluster Ingress (MCI):**
- Single global load balancer fronting multiple GKE clusters across regions.
- **Use Case**: Global high availability, low latency (closest cluster routing), blue-green clusters.

---

## Security Architecture

### Workload Identity

**Concept:**
- Maps Kubernetes Service Accounts (KSA) to Google IAM Service Accounts (GSA).
- Pods authenticate to Google Cloud APIs (Storage, Spanner, BigQuery) using the GSA identity.
- **Mechanism**: Uses OIDC federation. No secrets/keys stored in the cluster.

**Architecture:**
1. Create GSA with IAM roles (e.g., `roles/storage.objectViewer`).
2. Create KSA in Kubernetes.
3. Bind KSA to GSA: `gcloud iam service-accounts add-iam-policy-binding ... --role roles/iam.workloadIdentityUser`
4. Annotate KSA: `iam.gke.io/gcp-service-account=...`

**Best Practice**: NEVER use Node Service Account for workload permissions. Always use Workload Identity.

### Network Policies

**Concept:**
- Acts as a firewall for Pod-to-Pod communication inside the cluster.
- Default behavior: All Pods can talk to all Pods (Allow All).
- **Implementation**: Uses Dataplane V2 (Cilium) or Calico.

**Patterns:**
- **Deny-All Default**: Block all traffic, then allow specific paths.
- **Namespace Isolation**: Allow traffic only within the same namespace.
- **Frontend-Backend**: Allow Frontend Pods to talk to Backend Pods on specific ports only.

### Binary Authorization

**Concept:**
- Supply chain security. Ensures only trusted/verified images are deployed.
- **Attestors**: Sign images after passing CI/CD checks (vulnerability scan, unit tests).
- **Policy**: GKE enforces policy at admission time. If image is not signed by required attestors, deployment is blocked.

**Modes:**
- **Audit Only**: Log violations but allow deployment (Dry Run).
- **Enforce**: Block deployment of non-compliant images.

### Security Hardening

1. **Shielded GKE Nodes**: Verifies node integrity (Secure Boot, Integrity Monitoring). Enabled by default.
2. **Private Clusters**: Remove public IPs from nodes.
3. **RBAC (Role-Based Access Control)**: Least privilege for users accessing the cluster (via Cloud IAM + Kubernetes RBAC).
4. **Pod Security Standards (PSS)**:
   - **Privileged**: Unrestricted (avoid).
   - **Baseline**: Minimal restrictions, prevents known privilege escalations.
   - **Restricted**: Heavily restricted (no root, dropped capabilities). Best for security-critical apps.
5. **Secret Encryption**: Enable Application-layer Secrets Encryption (envelope encryption) using Cloud KMS keys to encrypt secrets in etcd.

---

## Scalability and Reliability

### Autoscaling Dimensions

**1. Horizontal Pod Autoscaler (HPA):**
- Scales **Pods** based on CPU/Memory or Custom Metrics (Cloud Monitoring).
- **Best For**: Stateless apps, handling traffic spikes.

**2. Vertical Pod Autoscaler (VPA):**
- Adjusts **Pod resource requests/limits** based on historical usage.
- **Best For**: Stateful apps, monolithic apps, "rightsizing" initial requests.
- **Modes**: Off (recommendations only), Initial (apply at start), Auto (restart to apply).

**3. Cluster Autoscaler (CA):**
- Scales **Nodes** (Node Pools) when Pods cannot be scheduled (pending state) or nodes are underutilized.
- **Best For**: Cost optimization, handling aggregate cluster load.
- **Interaction**: HPA adds Pods -> Cluster fills up -> CA adds Nodes.

**4. Node Auto-Provisioning (NAP):**
- Extension of Cluster Autoscaler.
- Automatically creates **new Node Pools** with optimal machine types for pending Pods.
- **Best For**: Diverse workloads requiring different machine types (e.g., GPU, High-Mem) without manual pool management.

### High Availability Patterns

**1. Regional Clusters**:
- Protects against zonal failures.
- Distribute nodes across 3 zones.
- Use **Pod Topology Spread Constraints** to ensure Pods are spread across zones.

**2. Pod Disruption Budgets (PDB):**
- Limits the number of Pods that can be down simultaneously during voluntary disruptions (upgrades, scaling).
- Ensures service availability during maintenance.

**3. Liveness and Readiness Probes:**
- **Liveness**: Restarts dead containers.
- **Readiness**: Removes unready containers from Service endpoints (load balancer).
- **Startup**: Delays other probes for slow-starting apps.

---

## Storage Patterns

### Container Storage Interface (CSI)

GKE uses the Compute Engine PD CSI driver by default.

**Storage Types:**
- **Standard Persistent Disk (pd-standard)**: HDD. Cheap, lower IOPS.
- **Balanced Persistent Disk (pd-balanced)**: SSD. Balance of cost/performance. Default.
- **SSD Persistent Disk (pd-ssd)**: High performance SSD.
- **Local SSD**: Ephemeral, attached physically to node. High IOPS, low latency. Data lost if node fails. Use for cache/scratch.
- **Filestore (NFS)**: Shared file storage (ReadWriteMany). Accessible by multiple Pods across zones.

### StatefulSets and Regional PD

**Regional Persistent Disks:**
- Replicated across two zones in the same region.
- **Use Case**: High availability for stateful databases (MySQL, Postgres).
- If primary zone fails, GKE can force-attach the disk to a node in the secondary zone.

**Access Modes:**
- **ReadWriteOnce (RWO)**: Mounted by single node (Block storage).
- **ReadWriteMany (RWX)**: Mounted by multiple nodes (File storage - Filestore).
- **ReadOnlyMany (ROX)**: Read-only by multiple nodes (Config/Secrets).

---

## Cost Optimization Strategies

### 1. Spot VMs (Preemptible)
- **Concept**: Excess Compute Engine capacity at 60-91% discount.
- **Risk**: Can be preempted with 30-second warning.
- **Use Case**: Batch jobs, stateless services, fault-tolerant workloads.
- **Strategy**: Use mixed node pools (On-demand for base load, Spot for bursts).
- **Graceful Termination**: Handle `SIGTERM` in application to finish requests before shutdown.

### 2. GKE Autopilot
- **Optimization**: Eliminates "bin-packing" waste. You don't pay for unused space on nodes.
- **Scenario**: If your Standard clusters have low utilization (<60-70%), Autopilot is often cheaper.

### 3. Rightsizing
- Use **VPA** in recommendation mode to find actual usage.
- Adjust resource requests to match reality.
- **Impact**: HPA scales based on utilization relative to requests. Accurate requests = efficient scaling.

### 4. GKE Cost Allocation
- Enable **GKE Cost Allocation** in Cloud Billing.
- Break down costs by **Namespace** and **Label**.
- **Use Case**: Chargeback/Showback to different teams/departments sharing a cluster.

### 5. Image Streaming
- Enables faster Pod startup by streaming image data.
- Reduces time nodes are running while initializing.

---

## Multi-Cluster and Hybrid Patterns

### Multi-Cluster Services (MCS)
- Allows Services to be exported and imported across clusters.
- **Concept**: "ClusterSet" groups clusters.
- **Service Discovery**: `<service>.<ns>.svc.clusterset.local`.
- **Use Case**: High availability, data locality, migration.

### GKE Enterprise (formerly Anthos)
- **Fleet**: Logical grouping of clusters.
- **Config Sync**: GitOps for multi-cluster configuration management. Enforce consistent policies across all clusters.
- **Policy Controller**: Enforce OPA Gatekeeper policies (e.g., "All images must come from gcr.io").
- **Service Mesh (ASM)**: Managed Istio. mTLS, observability, traffic splitting across clusters.

---

## Migration Strategies

### Migrate to Containers (formerly Migrate for Anthos)
- Tool to lift-and-shift VMs to GKE containers.
- **Source**: Compute Engine, VMware, AWS EC2, Azure VMs.
- **Process**:
  1. Replicates VM disk.
  2. Analyzes OS and app.
  3. Generates Dockerfile and Kubernetes artifacts.
  4. Deploys to GKE.
- **Benefit**: Quick modernization without code rewrite.

---

## Decision Matrices

### Network Endpoint Groups (NEG) vs Instance Groups
| Feature | NEG (Container-Native) | Instance Groups (Legacy) |
|---------|------------------------|--------------------------|
| **Traffic Routing** | LB -> Pod IP | LB -> Node IP -> iptables -> Pod IP |
| **Hops** | 1 Hop (Direct) | 2 Hops (Node + NAT) |
| **Latency** | Lower | Higher |
| **Visibility** | LB sees Pod health | LB sees Node health only |
| **Recommendation** | **Preferred** for Ingress | Legacy / NodePort |

### Ingress vs Service (LoadBalancer)
| Feature | Ingress (L7 HTTP/S) | Service LoadBalancer (L4 TCP/UDP) |
|---------|---------------------|-----------------------------------|
| **Protocol** | HTTP, HTTPS, HTTP/2 | TCP, UDP |
| **Routing** | Path/Host-based (/api, foo.com) | Port-based only |
| **SSL Termination** | Yes (Managed Certs) | No (Pass-through) |
| **Cost** | 1 LB for many services | 1 LB per service ($$$) |
| **WAF** | Cloud Armor supported | Not supported |

### Workload Identity vs Node Service Account
| Feature | Workload Identity | Node Service Account |
|---------|-------------------|----------------------|
| **Granularity** | Per Pod/Deployment | Per Node (All pods on node) |
| **Security** | Least Privilege | Broad Privilege (Risk) |
| **Credential** | Short-lived Token | Metadata Server |
| **Recommendation** | **Always Use** | Avoid for app permissions |

---

## High Availability & Disaster Recovery

### Multi-Region Architecture Patterns

**Pattern 1: Active-Active Multi-Region**
```
                      Global Load Balancer (GCLB)
                              |
          +-------------------+-------------------+
          |                                       |
    Region US-CENTRAL1                     Region EUROPE-WEST1
    GKE Regional Cluster                   GKE Regional Cluster
    (us-central1-a/b/c)                    (europe-west1-b/c/d)
          |                                       |
    Cloud SQL (HA)                          Cloud SQL (HA)
          |                                       |
    Cloud Storage (Multi-region)           Cloud Storage (Multi-region)
```

**Design Considerations:**
- **Data Replication**: Use Cloud Spanner for globally consistent data, or Cloud SQL with cross-region read replicas
- **Session Affinity**: Use cookie-based affinity to keep users on same region during session
- **Latency**: Route users to nearest region using global load balancing
- **Cost**: 2x infrastructure costs but maximum availability

**Pattern 2: Active-Passive (DR)**
- Primary cluster serves all traffic
- Secondary cluster on standby (can be smaller/scaled down)
- **RTO**: Time to detect failure + DNS/LB switch + scale up secondary
- **RPO**: Depends on data replication lag (Cloud SQL async replication: minutes)

**Pattern 3: Multi-Cluster Mesh (Advanced)**
- Use Anthos Service Mesh (ASM) with multi-cluster services
- Pods in Cluster A can call services in Cluster B transparently
- **Traffic Splitting**: 90% to primary, 10% to secondary for testing
- **Failover**: Automatic if ASM detects cluster health issues

### Backup and Recovery Strategies

**1. Cluster State Backup:**
- **Backup for GKE**: Managed service for backing up workloads and PVs
  - Backup Plans: Schedule backups (hourly, daily, weekly)
  - Backup Scope: Entire cluster, specific namespaces, or label selectors
  - Restore: To same cluster, different cluster, or different project
  - **RPO**: Based on schedule (hourly = 1hr max data loss)
  - **RTO**: Minutes to tens of minutes for restore

**2. GitOps Approach:**
- Store all Kubernetes manifests in Git (source of truth)
- Use Config Sync or Flux/ArgoCD
- **Recovery**: Provision new cluster + apply manifests from Git
- **Benefit**: Infrastructure as Code, audit trail, rollback capability

**3. Data Layer Backup:**
- **Persistent Volumes**: Use VolumeSnapshot CRD with CSI driver
- **Databases**: Use native backup tools (Cloud SQL automated backups, pg_dump, etc.)
- **Stateful Applications**: Use application-aware backup tools (e.g., Velero with plugins)

### SLO/SLA Design

**Google's SLA for GKE:**
- **Regional Clusters**: 99.95% uptime SLA (21.6 min/month downtime)
- **Zonal Clusters**: 99.5% uptime SLA (3.6 hrs/month downtime)
- **Autopilot**: 99.9% uptime SLA for Pod availability

**Designing Your SLOs:**

**SLI (Service Level Indicator) Examples:**
- **Availability**: Percentage of successful requests (non-5xx)
- **Latency**: 95th percentile response time < 200ms
- **Throughput**: Requests per second handled

**SLO Targets:**
```
Service: Frontend API
- SLI: HTTP success rate
- SLO: 99.9% (3 nines) = 43 min downtime/month
- Error Budget: 0.1% = 43 min/month

Actions:
- If error budget > 50% remaining: Safe to deploy, experiment
- If error budget < 10%: Freeze deployments, focus on reliability
```

**Implementation:**
- Use Cloud Monitoring SLOs
- Alert when burn rate is too high (consuming budget too fast)
- Dashboard showing current SLO status and error budget

---

## Advanced Networking Patterns

### Service Mesh Architecture (Anthos Service Mesh / Istio)

**Components:**
- **Control Plane**: Istiod (Pilot, Citadel, Galley merged)
- **Data Plane**: Envoy sidecar proxies injected into each Pod

**Key Capabilities:**

**1. Traffic Management:**
```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: reviews
spec:
  hosts:
  - reviews
  http:
  - match:
    - headers:
        end-user:
          exact: jason
    route:
    - destination:
        host: reviews
        subset: v2
  - route:
    - destination:
        host: reviews
        subset: v1
      weight: 80
    - destination:
        host: reviews
        subset: v2
      weight: 20
```
- **Use Cases**: Canary deployments, A/B testing, header-based routing

**2. Security (mTLS):**
- Automatic mutual TLS between services
- Service-to-service authentication
- No code changes required
- **Modes**: PERMISSIVE (both mTLS and plain), STRICT (mTLS only)

**3. Observability:**
- Distributed tracing (Jaeger, Cloud Trace)
- Service topology graph
- Metrics: Request rate, error rate, latency percentiles
- **Golden Signals**: Latency, Traffic, Errors, Saturation

**4. Multi-Cluster Service Discovery:**
- Deploy service in Cluster A, accessible from Cluster B
- DNS: `<service>.<namespace>.svc.cluster.local` resolves across clusters
- **Use Case**: Shared services (auth, billing) in one cluster, consumed by many

### Egress Gateway Pattern

**Problem**: Pods have ephemeral IPs, making firewall whitelisting difficult.

**Solution**: Force all egress traffic through dedicated gateway with stable IPs.
```
Pod -> Istio Egress Gateway (Static External IP) -> External Service
```

**Benefits:**
- External services can whitelist the gateway IP
- Centralized egress policy (allow/deny domains)
- Audit all outbound traffic

### DNS Architecture

**Default (kube-dns or Cloud DNS for GKE):**
- Cluster DNS resolves `<service>.<namespace>.svc.cluster.local`
- Upstream DNS for external domains

**Custom DNS:**
- Use **NodeLocal DNSCache**: DaemonSet caching layer
  - **Benefit**: Reduces DNS query latency, lowers kube-dns load
  - **Pattern**: Pod -> NodeLocal Cache (127.0.0.1) -> kube-dns -> Upstream

**Cloud DNS Integration:**
- Map cluster services to Cloud DNS zones
- **Use Case**: Private cluster services accessible from Compute Engine VMs using DNS names

---

## Observability and Monitoring Architecture

### Logging Strategy

**Default GKE Logging:**
- Container stdout/stderr -> Cloud Logging
- **Log Types**:
  - **System Logs**: kubelet, kube-proxy, docker
  - **Application Logs**: Container stdout/stderr
  - **Audit Logs**: API server actions (who did what, when)

**Structured Logging:**
```json
{
  "severity": "ERROR",
  "message": "Failed to connect to database",
  "trace": "projects/PROJECT_ID/traces/TRACE_ID",
  "component": "backend-service"
}
```
- **Benefit**: Queryable fields, correlation with traces, better alerting

**Log Aggregation Patterns:**

**Pattern 1: Native Cloud Logging**
- Pros: Zero setup, integrated with Cloud Monitoring
- Cons: Cost scales with log volume

**Pattern 2: Self-Hosted (Elasticsearch, Loki)**
- Deploy logging stack in GKE cluster
- Use **Fluentd DaemonSet** to collect logs from nodes
- Pros: Full control, potentially cheaper at scale
- Cons: Operational overhead (HA, backups, upgrades)

**Pattern 3: Hybrid**
- Send application logs to Cloud Logging
- Send high-volume debug logs to self-hosted system
- Retention: Short-term in Cloud Logging (30 days), long-term in GCS

### Monitoring and Alerting

**GKE Metrics in Cloud Monitoring:**
- **Infrastructure**: CPU, Memory, Disk I/O per node/pod
- **Kubernetes**: Pod restarts, deployments, HPA events
- **Custom Metrics**: Application-specific (via OpenTelemetry or Prometheus)

**Critical Alerts for Production:**

```yaml
1. High Pod Restart Rate
   - Condition: restart_count > 3 in 5 minutes
   - Action: Check liveness probe, application logs

2. Persistent Volume Near Full
   - Condition: disk_utilization > 85%
   - Action: Scale PV, investigate disk usage

3. HPA Max Replicas Reached
   - Condition: current_replicas == max_replicas for > 10 min
   - Action: Increase max replicas or investigate load

4. Node NotReady
   - Condition: Node status != Ready
   - Action: Check kubelet logs, node resource exhaustion

5. Certificate Expiry
   - Condition: TLS cert expires in < 30 days
   - Action: Renew certificate
```

**Prometheus Integration:**
- **Google Cloud Managed Service for Prometheus**: Fully managed, compatible with Prometheus APIs
- **Self-Managed Prometheus**: Deploy in GKE with persistent storage
- **Federation**: Scrape metrics from multiple clusters into central Prometheus

---

## CI/CD Integration Patterns

### GitOps with Config Sync

**Architecture:**
```
Git Repository (Source of Truth)
      |
      | webhook / poll
      |
   Config Sync (GKE Cluster)
      |
      | apply manifests
      |
   Kubernetes API Server
```

**Directory Structure:**
```
manifests/
├── cluster/          # Cluster-scoped resources (Namespaces, CRDs)
├── namespaces/
│   ├── production/   # Prod manifests
│   └── staging/      # Staging manifests
└── policies/         # Network Policies, RBAC
```

**Benefits:**
- **Declarative**: Desired state in Git
- **Audit Trail**: Every change is a Git commit
- **Rollback**: `git revert` to undo changes
- **Multi-Cluster**: One repo, multiple clusters sync

### Blue-Green Deployments

**Pattern:**
```
Initial State: Blue (v1) = 100% traffic
1. Deploy Green (v2) environment (0% traffic)
2. Test Green (smoke tests, manual QA)
3. Switch traffic: Blue = 0%, Green = 100%
4. Monitor Green
5. If OK: Delete Blue. If issues: Rollback to Blue
```

**Implementation with Ingress:**
- Use two Services: `app-blue`, `app-green`
- Update Ingress to point to `app-green`
- **Benefit**: Instant rollback (change Ingress back to blue)

### Canary Deployments with Progressive Delivery

**Pattern:**
```
v1: 100% traffic
v2: Deploy, route 5% traffic -> Monitor metrics
If OK: Increase to 10%, 25%, 50%, 100%
If Error Rate > SLO: Rollback to v1
```

**Tools:**
- **Flagger**: Automated canary analysis using metrics
- **Argo Rollouts**: Advanced deployment strategies
- **Istio**: Traffic splitting at service mesh layer

**Example with Istio:**
```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
spec:
  http:
  - route:
    - destination:
        host: my-app
        subset: v1
      weight: 90
    - destination:
        host: my-app
        subset: v2
      weight: 10  # Canary: 10% traffic
```

**Analysis Metrics:**
- **Success Rate**: >99.5% for canary
- **Latency (p95)**: < 200ms
- **Custom**: Business metrics (conversion rate, signup rate)

---

## Performance Optimization

### Resource Management Best Practices

**Requests vs Limits:**
```yaml
resources:
  requests:
    cpu: "500m"      # Scheduling: Node must have 0.5 CPU available
    memory: "512Mi"  # OOMKill threshold
  limits:
    cpu: "1000m"     # Throttling: Max 1 CPU
    memory: "1Gi"    # OOMKill if exceeded
```

**QoS Classes:**
1. **Guaranteed**: requests == limits (both CPU and Memory)
   - **Priority**: Highest (last to be evicted)
   - **Use Case**: Latency-sensitive, critical services
2. **Burstable**: requests < limits
   - **Priority**: Medium
   - **Use Case**: Most applications (allow bursts, save cost)
3. **BestEffort**: No requests/limits
   - **Priority**: Lowest (first to be evicted)
   - **Use Case**: Batch jobs, non-critical workloads

**Eviction Order under Node Pressure:**
BestEffort → Burstable (exceeding requests) → Guaranteed

### Pod Scheduling Optimization

**Node Affinity:**
```yaml
affinity:
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:
      - matchExpressions:
        - key: cloud.google.com/gke-nodepool
          operator: In
          values:
          - high-memory-pool
```
**Use Case**: Schedule database pods on high-memory nodes

**Pod Anti-Affinity:**
```yaml
affinity:
  podAntiAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
    - labelSelector:
        matchExpressions:
        - key: app
          operator: In
          values:
          - frontend
      topologyKey: topology.kubernetes.io/zone
```
**Use Case**: Spread frontend pods across zones (HA)

**Taints and Tolerations:**
```yaml
# Node Taint (Applied to Node Pool)
taints:
- key: "workload-type"
  value: "gpu"
  effect: "NoSchedule"

# Pod Toleration
tolerations:
- key: "workload-type"
  operator: "Equal"
  value: "gpu"
  effect: "NoSchedule"
```
**Use Case**: Reserve expensive GPU nodes for ML workloads only

### Image Optimization

**1. Multi-Stage Builds:**
```dockerfile
# Build stage
FROM golang:1.21 AS builder
COPY . .
RUN go build -o app

# Runtime stage
FROM gcr.io/distroless/base
COPY --from=builder /app /app
CMD ["/app"]
```
**Benefit**: Smaller image (no build tools in runtime), faster pulls

**2. Image Streaming:**
- Enable on GKE: Pulls image layers on-demand
- **Benefit**: Faster pod startup (seconds vs minutes for large images)
- **Best For**: Large images (ML models, heavy dependencies)

**3. Artifact Registry:**
- Use Artifact Registry instead of Docker Hub
- **Benefits**: Faster pulls (same region), vulnerability scanning, access control

---

## Security Architecture Deep Dive

### Least Privilege Access Model

**Layer 1: GCP IAM (Who can access the cluster)**
```
User/Group -> Cloud IAM Role -> GKE Cluster
Roles:
- container.viewer: Read-only (view clusters, not workloads)
- container.developer: Full CRUD on workloads
- container.admin: Full cluster management
```

**Layer 2: Kubernetes RBAC (What can users do in cluster)**
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: production
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: production
subjects:
- kind: User
  name: "dev@example.com"
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

**Best Practice:**
- Use ClusterRole for cluster-wide resources (Nodes, PV)
- Use Role for namespaced resources (Pods, Services)
- Bind via RoleBinding (namespace-scoped) or ClusterRoleBinding (cluster-scoped)

### Pod Security Standards (PSS)

**Enforcement Modes:**
- **enforce**: Block pods that violate the standard
- **audit**: Allow but log violations
- **warn**: Allow and show warning to user

**Namespace-level Policy:**
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

**Restricted Standard Requirements:**
- No privileged containers
- No host namespaces (hostNetwork, hostPID, hostIPC)
- No host ports
- Run as non-root
- Drop all capabilities, can add back only NET_BIND_SERVICE

### Supply Chain Security

**1. Vulnerability Scanning:**
- **Artifact Registry**: Automatic CVE scanning on push
- **Binary Authorization**: Block images with HIGH/CRITICAL vulnerabilities
- **Policy**: `gcr.io/my-project/* must have CVSS < 7.0`

**2. Image Signing:**
```bash
# CI/CD Pipeline
1. Build image -> Push to Artifact Registry
2. Scan for vulnerabilities -> If pass, sign with KMS key
3. Create attestation (proof of signature)
4. Deploy to GKE -> Binary Authorization verifies signature
```

**3. SBOM (Software Bill of Materials):**
- Generate SBOM during build (lists all dependencies)
- Store in Artifact Registry
- **Use Case**: Quickly identify if your apps use a vulnerable library (e.g., log4j)

---

## Cost Optimization Advanced Strategies

### Right-Sizing with VPA and HPA Together

**Scenario**: Application with variable load and unknown resource needs.

**Strategy:**
1. Deploy with conservative requests (e.g., 1 CPU, 2Gi RAM)
2. Enable VPA in recommendation mode
3. After 1 week, check VPA recommendations
4. Adjust requests to VPA recommendations (e.g., actual usage is 300m CPU, 512Mi RAM)
5. Enable HPA to scale replicas based on new (accurate) requests
6. **Result**: Efficient scaling (HPA) without over-provisioning (VPA rightsizing)

### Committed Use Discounts (CUDs) for GKE

**Concept**: Commit to use a certain amount of resources (CPU/RAM) for 1 or 3 years.
- **Discount**: Up to 57% for 3-year, 37% for 1-year
- **Applies to**: Compute Engine (node pools), even if workload changes

**Strategy:**
- Identify baseline workload (minimum resources always running)
- Purchase CUD for baseline
- Use Spot VMs or on-demand for bursts above baseline
- **Example**: Baseline 100 vCPUs (CUD), peak 200 vCPUs (50 Spot, 50 on-demand)

### GKE Cost Allocation to Teams

**Setup:**
```bash
gcloud container clusters update CLUSTER_NAME \
  --enable-cost-allocation
```

**Label Workloads:**
```yaml
metadata:
  labels:
    team: backend-team
    env: production
    cost-center: "12345"
```

**Billing Analysis:**
- Cloud Billing exports to BigQuery
- Query costs by label: `SUM(cost) GROUP BY labels.key.team`
- **Chargeback**: Invoice teams based on their usage

---

## Migration and Modernization Patterns

### Strangler Fig Pattern (Monolith to Microservices)

**Pattern:**
1. Run monolith in GKE (containerized)
2. Identify a feature/module to extract (e.g., user authentication)
3. Build new microservice for that feature
4. Use Ingress to route specific paths to new microservice:
   ```
   /auth/* -> auth-microservice
   /* -> monolith
   ```
5. Gradually extract more features
6. Eventually, monolith is fully replaced

**Benefits:**
- No "big bang" rewrite
- Incremental value delivery
- Rollback individual services

### Lift and Shift with Migrate to Containers

**Process:**
```
VM (On-Prem / AWS / GCE) 
  -> Migrate to Containers Tool
  -> Dockerfile + K8s Manifests
  -> GKE
```

**Post-Migration Optimization:**
1. **Phase 1**: Run as-is (stateful container, host path volumes)
2. **Phase 2**: Refactor storage (use Cloud SQL, Filestore)
3. **Phase 3**: Refactor app (stateless, 12-factor)
4. **Phase 4**: Re-architect (microservices, event-driven)

### Database Migration Strategies

**Pattern 1: Dual-Write During Transition**
```
Application
  -> Write to Old DB (VM)
  -> Write to New DB (Cloud SQL)
  -> Read from New DB (verify consistency)
  -> Stop writing to Old DB
```

**Pattern 2: CDC (Change Data Capture)**
- Use Datastream to replicate MySQL/PostgreSQL to Cloud SQL
- **Cutover**: Switch connection string, minimal downtime

**Pattern 3: Blue-Green Database**
- Replicate Old DB to New DB (Cloud SQL)
- Test application with New DB
- **Cutover**: DNS/connection string switch
- **Rollback**: Switch back to Old DB

---

## Advanced GKE Features

### GKE Dataplane V2 (eBPF)

**Architecture:**
- Uses **Cilium** and **eBPF** (kernel-level networking)
- Replaces iptables-based kube-proxy and Calico

**Benefits:**
- **Performance**: 2-3x faster than iptables (packet processing in kernel)
- **Scalability**: Handle 10,000+ services (iptables degrades at scale)
- **Security**: Network Policies with L7 (HTTP) filtering, not just L4
- **Observability**: Built-in flow logs (Hubble)

**When to Use:**
- Large clusters (>500 nodes)
- Latency-sensitive applications
- Advanced network policies (L7)

### GKE Sandbox (gVisor)

**Concept:**
- Additional isolation layer between containers and kernel
- Uses **gVisor**: User-space kernel for containers
- **Security**: Even if container is compromised, attacker is in gVisor, not host kernel

**Use Case:**
- Multi-tenant clusters (different customers/teams)
- Untrusted workloads (user-submitted code, CI/CD runners)

**Trade-off:**
- **Performance**: 10-20% overhead (extra layer)
- **Compatibility**: Some syscalls not supported (exotic kernel features)

### GKE Backup for Applications

**Features:**
- Schedule-based backups (RPO: hourly, daily, weekly)
- Backup scope: Namespace, label selector, entire cluster
- **Cross-region restore**: Backup in us-central1, restore in europe-west1
- **Encryption**: Backups encrypted at rest

**Advanced: Application-Consistent Backups:**
- Use pre-backup and post-backup hooks
- **Example**: Flush database to disk before backup, unfreeze after
- **Ensures**: Consistent state (no partial writes)

---

## Enterprise Patterns and Governance

### Policy as Code with Policy Controller

**Concept:**
- **OPA Gatekeeper**: Admission controller enforcing custom policies
- Policies written in **Rego** language

**Example Policies:**
```rego
# Policy: All images must come from Artifact Registry
package k8srequiredregistry

violation[{"msg": msg}] {
  container := input.review.object.spec.containers[_]
  not startswith(container.image, "us-docker.pkg.dev/my-project/")
  msg := sprintf("Image '%v' not from approved registry", [container.image])
}
```

**Common Policies:**
- No `latest` tag (enforce versioned images)
- All Pods must have resource requests/limits
- No privileged containers
- Services must have PodDisruptionBudget

### Hierarchy and Organization

**Fleet-based Management:**
```
Organization (GCP Org)
├── Folder: Production
│   ├── Project: prod-us
│   │   └── GKE Cluster: prod-us-central1
│   └── Project: prod-eu
│       └── GKE Cluster: prod-europe-west1
└── Folder: Development
    └── Project: dev-sandbox
        └── GKE Cluster: dev-cluster
```

**Fleet Features:**
- **Unified Dashboard**: View all clusters in one place
- **Config Management**: Apply policies to all clusters in fleet
- **Service Mesh**: Multi-cluster mesh across fleet

### Compliance and Audit

**GKE Compliance Controls:**
1. **Audit Logging**: Log all API requests (who, what, when)
   - Enable Data Access logs for read operations
   - Retention: 400 days (configurable)
2. **Config Connector**: Manage GCP resources via Kubernetes (GitOps)
   - **Benefit**: All infra changes in Git (audit trail)
3. **Binary Authorization**: Enforce deployment policies
4. **Shielded GKE Nodes**: Secure boot, integrity monitoring

**Compliance Frameworks:**
- **PCI-DSS**: Use private clusters, encryption at rest, network policies
- **HIPAA**: Use CMEK (customer-managed encryption keys), audit logs
- **SOC 2**: GKE is SOC 2 compliant (Google's responsibility)
  - **Your responsibility**: Access controls (IAM, RBAC), logging, incident response

---

## Disaster Recovery Test Scenarios

### Scenario 1: Regional Cluster Zone Failure

**Setup**: Regional cluster in `us-central1` (zones a, b, c)

**Simulation:**
```bash
# Cordon all nodes in one zone (simulate zone failure)
kubectl cordon -l topology.kubernetes.io/zone=us-central1-a
```

**Expected Behavior:**
- Pods on failed zone's nodes become Terminating
- Kubernetes reschedules Pods to nodes in zones b and c
- Control plane remains available (replicas in 3 zones)
- **RTO**: <5 minutes (pod reschedule time)

**Validation:**
- Check pod distribution: `kubectl get pods -o wide`
- Verify application availability: `curl http://app-endpoint`

### Scenario 2: Full Cluster Failure

**Simulation**: Delete entire cluster

**Recovery:**
1. Provision new GKE cluster (via Terraform or gcloud)
2. Restore from Backup for GKE (or apply manifests from Git)
3. Restore PV data from snapshots
4. Update DNS/load balancer to point to new cluster

**RTO**: 15-30 minutes (cluster provision + restore)  
**RPO**: Depends on backup schedule (e.g., hourly backups = <1hr data loss)

### Scenario 3: Data Corruption

**Simulation**: Accidental deployment deletes data

**Recovery:**
1. Identify last good backup (before corruption)
2. Restore from Backup for GKE to a temporary namespace
3. Export data from temporary namespace
4. Import data to production namespace
5. Verify data integrity
6. Delete temporary namespace

**Best Practice**: Test restores quarterly (verify backups are usable)

---

## PCA Exam Tips and Common Scenarios

### Design Decision Framework

When presented with a scenario, evaluate:
1. **Availability**: Regional cluster? Multi-region? ASM?
2. **Scalability**: Autopilot or Standard? HPA? Cluster Autoscaler?
3. **Security**: Private cluster? Workload Identity? Binary Authorization?
4. **Cost**: Spot VMs? Autopilot? Rightsizing?
5. **Compliance**: Audit logs? Encryption? GKE Sandbox?

### Common Exam Scenarios

**Scenario 1: "Need to deploy 1000s of microservices, minimize ops overhead"**
- **Answer**: GKE Autopilot + Config Sync (GitOps)
- **Why**: Autopilot = No node management, Config Sync = Declarative at scale

**Scenario 2: "Multi-tenant SaaS, isolate customer workloads"**
- **Answer**: Separate namespaces + Network Policies + GKE Sandbox
- **Advanced**: Separate clusters per customer (extreme isolation, higher cost)

**Scenario 3: "Global app, low latency worldwide"**
- **Answer**: Multi-region GKE + Multi-Cluster Ingress + Cloud Spanner (global DB)
- **Why**: MCI routes to nearest cluster, Spanner for consistent global data

**Scenario 4: "Migrate legacy app (stateful, runs on VM) to GKE"**
- **Answer**: Migrate to Containers tool -> Initial StatefulSet with local storage -> Refactor to Cloud SQL/Filestore
- **Why**: Incremental migration (lift-and-shift -> optimize)

**Scenario 5: "Enforce compliance: No privileged containers, all images signed"**
- **Answer**: Policy Controller (OPA) + Binary Authorization
- **Why**: Policy Controller enforces Pod Security, Binary Authorization verifies image signatures

**Scenario 6: "Reduce costs for batch processing workload"**
- **Answer**: Spot VMs (preemptible) + Job-based workloads + SIGTERM handling
- **Why**: Up to 91% discount, batch jobs tolerate interruptions

**Scenario 7: "Service A (Frontend) should only call Service B (Backend), deny all other traffic"**
- **Answer**: Network Policies (default deny all -> allow A to B on specific port)
- **Why**: Zero-trust networking, limit blast radius of compromise

**Scenario 8: "Need to debug production issue, but developers shouldn't access production cluster directly"**
- **Answer**: Bastion host with IAM conditions + Cloud IAM + Audit logs
- **Alternative**: Ephemeral clusters for debugging (clone prod config, load test data)

### Key Architectural Trade-offs

| Decision | Option A | Option B | Trade-off |
|----------|----------|----------|-----------|
| **Cluster Type** | Zonal (99.5%) | Regional (99.95%) | Cost vs Availability |
| **GKE Mode** | Standard | Autopilot | Control vs Simplicity |
| **Networking** | VPC-Native | Routes-based | Scalability vs Legacy |
| **Cluster Access** | Private | Public (Auth Nets) | Security vs Convenience |
| **Service Mesh** | Yes (ASM) | No | Observability/Security vs Complexity |
| **Workload Type** | Stateless (Deployment) | Stateful (StatefulSet) | Scalability vs Data Persistence |
| **Node VMs** | On-demand | Spot | Reliability vs Cost |

---

## Real-World Reference Architectures

### E-commerce Platform on GKE

```
                    Cloud CDN
                        |
                Global Load Balancer
                        |
        +---------------+---------------+
        |                               |
   Region US                       Region EU
   GKE Autopilot                   GKE Autopilot
        |                               |
   +---------+                     +---------+
   |Frontend |                     |Frontend |
   +---------+                     +---------+
        |                               |
   +---------+                     +---------+
   |Checkout |                     |Checkout |
   +---------+                     +---------+
        |                               |
        +---------------+---------------+
                        |
                 Cloud Spanner (Global)
                        |
                 Cloud Storage (Product images)
```

**Key Design Choices:**
- **Autopilot**: Variable traffic (Black Friday spikes)
- **Multi-region**: Low latency globally, HA
- **Cloud Spanner**: Strong consistency for inventory
- **Cloud CDN**: Cache product pages, images

### ML Training Pipeline on GKE

```
GKE Standard Cluster
├── GPU Node Pool (NVIDIA A100)
│   └── TensorFlow Training Jobs (Batch)
├── CPU Node Pool (Spot VMs)
│   └── Data Preprocessing (Apache Beam)
└── High-Memory Node Pool
    └── Feature Engineering (Pandas/Dask)
```

**Key Design Choices:**
- **Standard Mode**: Need GPUs (not available in Autopilot)
- **Spot VMs**: Training can checkpoint and resume (tolerate preemption)
- **Node Pools**: Different workloads need different hardware
- **Persistent Volumes**: Store model checkpoints (Regional PD for HA)

---

## Conclusion and Next Steps

### Professional Cloud Architect Mindset

**Remember:**
- **No Single Right Answer**: PCA scenarios have trade-offs, not absolutes
- **Business Context Matters**: Cost-sensitive startup vs regulated enterprise
- **Iterate**: Start simple, add complexity as needed (don't over-engineer)

### Hands-On Practice

**Essential Labs:**
1. Deploy Regional GKE cluster with private nodes
2. Implement Workload Identity for Cloud Storage access
3. Set up Multi-Cluster Ingress across 2 regions
4. Configure Network Policies (deny-all -> selective allow)
5. Deploy Anthos Service Mesh and implement traffic splitting
6. Automate deployments with Config Sync (GitOps)
7. Simulate zone failure and measure RTO
8. Set up GKE Backup and perform restore to different cluster

### Additional Resources

- **GKE Best Practices**: https://cloud.google.com/kubernetes-engine/docs/best-practices
- **GKE Security Hardening Guide**: https://cloud.google.com/kubernetes-engine/docs/how-to/hardening-your-cluster
- **Anthos Service Mesh Docs**: https://cloud.google.com/service-mesh/docs
- **Kubernetes Patterns (Book)**: Design patterns for cloud-native apps

---

**End of GKE Professional Cloud Architect Guide**
