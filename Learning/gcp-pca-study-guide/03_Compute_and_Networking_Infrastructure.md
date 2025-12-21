# Chapter 03: Compute & Networking Infrastructure

Networking is the backbone of any cloud architecture. Compute provides the muscle. Understanding how to connect and run your workloads is critical.

> **Key Concept**: "Google Cloud consists of a set of physical assets, such as computers and hard disk drives, and virtual resources, such as virtual machines (VMs), that are contained in data centers around the globe."
>
> — [Google Cloud Documentation](https://cloud.google.com/docs/overview)

## 🌐 Networking Deep Dive

### VPC Fundamentals

A Virtual Private Cloud (VPC) network is a global resource with regional subnets.

```
┌─────────────────────────────────────────────────────────────────┐
│                    VPC Network (Global)                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────────────────┐     ┌─────────────────────┐           │
│   │ Subnet us-central1  │     │ Subnet europe-west1 │           │
│   │   10.0.1.0/24       │     │   10.0.2.0/24       │           │
│   │ ┌─────┐  ┌─────┐    │     │ ┌─────┐  ┌─────┐   │           │
│   │ │ VM  │  │ VM  │    │     │ │ VM  │  │ VM  │   │           │
│   │ └─────┘  └─────┘    │     │ └─────┘  └─────┘   │           │
│   └─────────────────────┘     └─────────────────────┘           │
│                                                                  │
│   Firewall Rules (Applied to VMs via network tags/SA)           │
│   Routes (Automatic or custom)                                   │
└─────────────────────────────────────────────────────────────────┘
```

### VPC Topologies

| Topology | Description | Use Case |
| :--- | :--- | :--- |
| **Shared VPC** | Host project manages VPC, service projects use it | Centralized network management across projects |
| **VPC Peering** | Direct connection between two VPCs (non-transitive) | Connecting separate workloads, cross-organization |
| **Private Service Connect** | Private access to Google APIs or third-party services | Secure access without public IPs |

#### Shared VPC Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                       Organization                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │             HOST PROJECT (Network Admin)                │   │
│   │  ┌──────────────────────────────────────────────────┐  │   │
│   │  │                 Shared VPC                        │  │   │
│   │  │  ┌───────────┐  ┌───────────┐  ┌───────────┐    │  │   │
│   │  │  │ Subnet-A  │  │ Subnet-B  │  │ Subnet-C  │    │  │   │
│   │  │  │(Dev Team) │  │(QA Team)  │  │(Prod Team)│    │  │   │
│   │  │  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘    │  │   │
│   │  └────────┼──────────────┼──────────────┼──────────┘  │   │
│   └───────────┼──────────────┼──────────────┼─────────────┘   │
│               │              │              │                  │
│   ┌───────────▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐         │
│   │ Service Project  │ │Service Proj│ │Service Proj│         │
│   │     (Dev)        │ │   (QA)     │ │  (Prod)    │         │
│   │   VMs/GKE        │ │  VMs/GKE   │ │  VMs/GKE   │         │
│   └──────────────────┘ └────────────┘ └────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

**Example: Create Shared VPC**
```bash
# Enable Shared VPC in host project
gcloud compute shared-vpc enable host-project-id

# Associate a service project
gcloud compute shared-vpc associated-projects add service-project-id \
    --host-project=host-project-id

# Grant IAM role to use specific subnet
gcloud projects add-iam-policy-binding host-project-id \
    --member="serviceAccount:service-account@service-project-id.iam.gserviceaccount.com" \
    --role="roles/compute.networkUser" \
    --condition='expression=resource.name.endsWith("subnet-a"),title=subnet-a-only'
```

### Hybrid Connectivity

| Option | Bandwidth | SLA | Setup Time | Use Case |
| :--- | :--- | :--- | :--- | :--- |
| **Cloud VPN (HA)** | 3 Gbps per tunnel | 99.99% | Hours | Development, small workloads |
| **Dedicated Interconnect** | 10-200 Gbps | 99.99% | Weeks | High-bandwidth production |
| **Partner Interconnect** | 50 Mbps-50 Gbps | 99.9-99.99% | Days | When not colocated with Google |

**Example: HA VPN Configuration**
```bash
# Create Cloud Router (required for dynamic routing)
gcloud compute routers create my-router \
    --network=my-vpc \
    --region=us-central1 \
    --asn=65001

# Create HA VPN Gateway
gcloud compute vpn-gateways create ha-vpn-gw \
    --network=my-vpc \
    --region=us-central1

# View external IPs (to configure on-prem gateway)
gcloud compute vpn-gateways describe ha-vpn-gw \
    --region=us-central1 \
    --format='value(vpnInterfaces[0].ipAddress,vpnInterfaces[1].ipAddress)'
```

### Load Balancing Selection Guide

| Load Balancer | Layer | Scope | Use Case |
| :--- | :--- | :--- | :--- |
| **Global External HTTP(S)** | L7 | Global | Web apps with global users |
| **Global External TCP/SSL Proxy** | L4 | Global | Non-HTTP TCP traffic globally |
| **Regional External HTTP(S)** | L7 | Regional | Data residency requirements |
| **Regional External TCP/UDP** | L4 | Regional | Regional network load balancing |
| **Internal HTTP(S)** | L7 | Regional | Internal microservices |
| **Internal TCP/UDP** | L4 | Regional | Database access, internal services |
| **Cross-region Internal** | L4/L7 | Global | Multi-region internal traffic |

**Example: Global HTTP(S) Load Balancer with Cloud Run**
```bash
# Create a serverless NEG for Cloud Run
gcloud compute network-endpoint-groups create cloud-run-neg \
    --region=us-central1 \
    --network-endpoint-type=serverless \
    --cloud-run-service=my-service

# Create backend service
gcloud compute backend-services create my-backend \
    --load-balancing-scheme=EXTERNAL_MANAGED \
    --global

# Add NEG to backend service
gcloud compute backend-services add-backend my-backend \
    --network-endpoint-group=cloud-run-neg \
    --network-endpoint-group-region=us-central1 \
    --global

# Create URL map
gcloud compute url-maps create my-url-map \
    --default-service=my-backend

# Create target HTTPS proxy (requires SSL certificate)
gcloud compute target-https-proxies create my-https-proxy \
    --url-map=my-url-map \
    --ssl-certificates=my-ssl-cert

# Create forwarding rule
gcloud compute forwarding-rules create my-forwarding-rule \
    --load-balancing-scheme=EXTERNAL_MANAGED \
    --network-tier=PREMIUM \
    --target-https-proxy=my-https-proxy \
    --ports=443 \
    --global
```

## 💻 Compute Selection Strategy

### Decision Matrix

| Service | Best Use Case | Operational Effort | Scaling | Cost Model |
| :--- | :--- | :--- | :--- | :--- |
| **Compute Engine** | Legacy apps, GPUs, specific OS | High | MIGs, Autoscaling | Per-second (min 1 min) |
| **GKE Autopilot** | Containerized apps, K8s ecosystem | Low | Per-pod autoscaling | Per-pod resources |
| **GKE Standard** | Complex containerized apps, node control | Medium | Node + Pod autoscaling | Per-node |
| **Cloud Run** | Stateless containers, APIs | Very Low | 0-1000+ instances | Per-request |
| **Cloud Functions** | Event-driven, glue code | Very Low | 0-3000 instances | Per-invocation |
| **App Engine Standard** | Web apps (specific runtimes) | Low | Automatic | Per-instance-hour |
| **App Engine Flexible** | Web apps (custom containers) | Low | Automatic | Per-VM-hour |

### When to Use Which?

```
┌─────────────────────────────────────────────────────────────────┐
│                    Compute Decision Tree                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Need containers?                                                │
│       │                                                          │
│       ├── Yes ──► Need Kubernetes features?                     │
│       │               │                                          │
│       │               ├── Yes ──► Need node control? ──► GKE    │
│       │               │                  │             Standard  │
│       │               │                  └── No ──► GKE Autopilot│
│       │               │                                          │
│       │               └── No ──► Stateless? ──► Cloud Run       │
│       │                              │                           │
│       │                              └── No ──► GKE              │
│       │                                                          │
│       └── No ──► Event-driven/small? ──► Cloud Functions        │
│                          │                                       │
│                          └── No ──► Compute Engine              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## ☸️ GKE Architectural Patterns

### Autopilot vs. Standard Mode

> **Best Practice**: "Use the fully managed Autopilot mode, in which Google Cloud manages your nodes for you and provides a workload-focused, cost-optimized, production-ready experience. Only use Standard mode if you have a specific need to manually manage the node pools and clusters."
>
> — [GKE Documentation](https://cloud.google.com/kubernetes-engine/docs/concepts/autopilot-overview)

| Feature | GKE Autopilot | GKE Standard |
| :--- | :--- | :--- |
| **Node Management** | Google-managed | Self-managed |
| **Pricing** | Per-pod CPU/memory | Per-node |
| **SLA** | Pod-level | Node-level |
| **Node Access** | No SSH access | Full node access |
| **GPU Support** | Limited | Full support |
| **Windows Containers** | Not supported | Supported |
| **Best For** | Most workloads | Specialized needs |

**Example: Create GKE Autopilot Cluster**
```bash
# Create an Autopilot cluster
gcloud container clusters create-auto my-autopilot-cluster \
    --region=us-central1 \
    --release-channel=regular

# Deploy an application
kubectl create deployment nginx --image=nginx:latest
kubectl expose deployment nginx --port=80 --type=LoadBalancer

# Enable autoscaling (automatic in Autopilot)
kubectl autoscale deployment nginx --min=1 --max=10 --cpu-percent=50
```

### GKE Security Features

| Feature | Description |
| :--- | :--- |
| **Workload Identity** | Map K8s service accounts to GCP service accounts |
| **Binary Authorization** | Only deploy trusted container images |
| **Shielded GKE Nodes** | Verified boot and integrity monitoring |
| **Private Clusters** | Nodes without public IPs |
| **GKE Security Posture** | Dashboard for security insights |

**Example: Enable Workload Identity**
```bash
# Create a GCP service account
gcloud iam service-accounts create my-app-sa

# Grant permissions to the service account
gcloud projects add-iam-policy-binding my-project \
    --member="serviceAccount:my-app-sa@my-project.iam.gserviceaccount.com" \
    --role="roles/storage.objectViewer"

# Create Kubernetes service account
kubectl create serviceaccount my-k8s-sa --namespace=default

# Bind the K8s SA to the GCP SA
gcloud iam service-accounts add-iam-policy-binding \
    my-app-sa@my-project.iam.gserviceaccount.com \
    --role="roles/iam.workloadIdentityUser" \
    --member="serviceAccount:my-project.svc.id.goog[default/my-k8s-sa]"

# Annotate the K8s service account
kubectl annotate serviceaccount my-k8s-sa \
    iam.gke.io/gcp-service-account=my-app-sa@my-project.iam.gserviceaccount.com
```

## 🛡️ Network Security

### Defense in Depth

```
┌─────────────────────────────────────────────────────────────────┐
│                    Network Security Layers                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Layer 1: EDGE SECURITY                                   │    │
│  │ • Cloud Armor (WAF, DDoS protection)                    │    │
│  │ • Cloud CDN (caching, edge termination)                 │    │
│  └─────────────────────────────────────────────────────────┘    │
│                            ↓                                     │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Layer 2: PERIMETER SECURITY                             │    │
│  │ • VPC Service Controls (data exfiltration prevention)   │    │
│  │ • Cloud NAT (outbound without public IPs)               │    │
│  └─────────────────────────────────────────────────────────┘    │
│                            ↓                                     │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Layer 3: NETWORK SECURITY                               │    │
│  │ • Firewall rules (ingress/egress)                       │    │
│  │ • Hierarchical firewall policies                        │    │
│  │ • Private Google Access                                 │    │
│  └─────────────────────────────────────────────────────────┘    │
│                            ↓                                     │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Layer 4: APPLICATION SECURITY                           │    │
│  │ • Identity-Aware Proxy (IAP)                            │    │
│  │ • Service mesh (Anthos Service Mesh)                    │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Key Security Services

| Service | Purpose | Example Use Case |
| :--- | :--- | :--- |
| **Cloud Armor** | WAF, DDoS protection | Block SQL injection, rate limiting |
| **Cloud IAP** | Context-aware access | Secure internal apps without VPN |
| **Private Google Access** | Access Google APIs privately | VMs without public IPs accessing GCS |
| **VPC Service Controls** | Data exfiltration prevention | Prevent BigQuery data from leaving perimeter |

**Example: Cloud Armor Security Policy**
```bash
# Create a security policy
gcloud compute security-policies create my-policy

# Add a rule to block SQL injection
gcloud compute security-policies rules create 1000 \
    --security-policy=my-policy \
    --expression="evaluatePreconfiguredExpr('sqli-stable')" \
    --action=deny-403

# Add rate limiting rule
gcloud compute security-policies rules create 2000 \
    --security-policy=my-policy \
    --src-ip-ranges="*" \
    --action=rate-based-ban \
    --rate-limit-threshold-count=100 \
    --rate-limit-threshold-interval-sec=60 \
    --ban-duration-sec=600

# Attach to backend service
gcloud compute backend-services update my-backend \
    --security-policy=my-policy \
    --global
```

---

📚 **Documentation Links**:
- [VPC Documentation](https://cloud.google.com/vpc/docs)
- [GKE Documentation](https://cloud.google.com/kubernetes-engine/docs)
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Load Balancing Documentation](https://cloud.google.com/load-balancing/docs)
- [Cloud Armor Documentation](https://cloud.google.com/armor/docs)
- [Compute Engine Documentation](https://cloud.google.com/compute/docs)

---
[Next Chapter: Data & Storage Strategy](04_Data_and_Storage_Strategy.md)
