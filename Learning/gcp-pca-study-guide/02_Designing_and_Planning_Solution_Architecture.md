# Chapter 02: Solution Architecture Design

In the PCA exam, you are the Architect. You need to translate vague business goals into concrete technical architectures while balancing cost, performance, and reliability.

> **Core Principle**: "Simplicity is crucial for design. If your architecture is too complex to understand, it will be difficult to implement the design and manage it over time. Where feasible, use fully managed services to minimize the risks, time, and effort associated with managing and maintaining baseline systems."
>
> — [Google Cloud Well-Architected Framework](https://cloud.google.com/architecture/framework)

## 📈 The Architectural Process

### 1. Requirements Gathering

#### Business Requirements
| Category | Example Questions |
| :--- | :--- |
| **Cost** | What is the budget? How do we optimize for cost? |
| **Time to Market** | How quickly do we need to launch? |
| **Compliance** | What regulatory requirements apply (HIPAA, PCI-DSS, GDPR)? |
| **User Experience** | What are the latency and availability expectations? |
| **Growth** | What is the expected scale in 1, 3, 5 years? |

#### Technical Requirements
| Category | Example Questions |
| :--- | :--- |
| **Scalability** | How many concurrent users? What's peak traffic? |
| **Availability** | What's the acceptable downtime (99.9%, 99.99%)? |
| **Reliability** | How critical is data durability? |
| **Disaster Recovery** | What are RTO and RPO requirements? |
| **Integration** | What existing systems must be integrated? |

### 2. Design Trade-offs

Architecting is the art of compromise. Every decision involves trade-offs:

| Trade-off | Option A | Option B |
| :--- | :--- | :--- |
| **Consistency vs. Availability** | Cloud Spanner (Strong consistency, global) | Firestore (Eventual consistency, fast reads) |
| **Cost vs. Performance** | Spot VMs (70-90% cheaper, preemptible) | On-demand VMs (Reliable, higher cost) |
| **Operational Effort vs. Customization** | Cloud Run (Low ops, limited control) | GKE Standard (High control, more ops) |
| **Latency vs. Durability** | Regional resources (Lower latency) | Multi-region (Higher durability) |
| **Simplicity vs. Flexibility** | Managed services | Self-managed infrastructure |

## 🧩 Foundational Architecture Patterns

### Microservices vs. Monolith

| Aspect | Monolith | Microservices |
| :--- | :--- | :--- |
| **Development** | Easier initially | Requires more upfront planning |
| **Scaling** | Scale entire application | Scale individual services |
| **Deployment** | Deploy all at once | Independent deployments |
| **Team Structure** | Single team | Multiple autonomous teams |
| **Complexity** | Lower | Higher (networking, observability) |
| **Best For** | Small teams, simple applications | Large teams, complex applications |

**Example: Microservices on Cloud Run**
```yaml
# Cloud Run service definition
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: order-service
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/minScale: "1"
        autoscaling.knative.dev/maxScale: "100"
    spec:
      containerConcurrency: 80
      containers:
      - image: gcr.io/myproject/order-service:v1.2
        ports:
        - containerPort: 8080
        resources:
          limits:
            memory: 512Mi
            cpu: 1000m
```

### Serverless Architecture

> **When to use Serverless**: "Start simple, establish a minimal viable product (MVP), and resist the urge to over-engineer."

| Service | Best Use Case | Max Timeout | Scaling |
| :--- | :--- | :--- | :--- |
| **Cloud Run** | Containerized web apps, APIs | 60 min (gen2) | 0 to 1000+ instances |
| **Cloud Functions** | Event-driven logic, glue code | 9 min (gen1), 60 min (gen2) | 0 to 3000 instances |
| **App Engine Standard** | Web applications | Varies by runtime | Automatic |
| **App Engine Flexible** | Custom runtimes | No limit | Automatic |

**Example: Event-Driven Architecture with Cloud Functions**
```python
# Cloud Function triggered by Cloud Storage
import functions_framework
from google.cloud import bigquery

@functions_framework.cloud_event
def process_file(cloud_event):
    """Triggered when a file is uploaded to Cloud Storage."""
    data = cloud_event.data
    
    bucket = data["bucket"]
    name = data["name"]
    
    # Load data into BigQuery
    client = bigquery.Client()
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        autodetect=True,
    )
    
    uri = f"gs://{bucket}/{name}"
    load_job = client.load_table_from_uri(
        uri, "myproject.mydataset.mytable", job_config=job_config
    )
    load_job.result()  # Wait for job to complete
```

### Three-Tier Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Three-Tier Architecture                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │ PRESENTATION TIER (Frontend)                            │   │
│   │ • Cloud CDN + Global Load Balancer                      │   │
│   │ • Static content in Cloud Storage                       │   │
│   │ • Firebase Hosting for SPAs                             │   │
│   └─────────────────────────────────────────────────────────┘   │
│                            ↓                                     │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │ APPLICATION TIER (Backend)                              │   │
│   │ • Cloud Run / GKE for APIs                              │   │
│   │ • Cloud Functions for event processing                  │   │
│   │ • Memorystore for session caching                       │   │
│   └─────────────────────────────────────────────────────────┘   │
│                            ↓                                     │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │ DATA TIER (Storage)                                     │   │
│   │ • Cloud SQL / AlloyDB for relational data               │   │
│   │ • Firestore for NoSQL                                   │   │
│   │ • BigQuery for analytics                                │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 🏗️ Multi-Cloud & Hybrid Design

Most enterprise customers aren't 100% in the cloud. Understanding hybrid patterns is critical.

### Hybrid Connectivity Options

| Option | Bandwidth | Latency | Setup Time | Best For |
| :--- | :--- | :--- | :--- | :--- |
| **Cloud VPN** | Up to 3 Gbps per tunnel | Variable | Hours | Quick setup, dev/test |
| **Dedicated Interconnect** | 10-200 Gbps | Low, consistent | Weeks | High-throughput production |
| **Partner Interconnect** | 50 Mbps-50 Gbps | Low | Days-Weeks | When colocation not available |
| **Cross-Cloud Interconnect** | 10-100 Gbps | Low | Days | Multi-cloud connections |

**Example: Cloud VPN with HA Configuration**
```bash
# Create HA VPN gateway
gcloud compute vpn-gateways create ha-vpn-gateway \
    --network=my-vpc \
    --region=us-central1

# Create external VPN gateway (representing on-prem)
gcloud compute external-vpn-gateways create on-prem-gateway \
    --interfaces 0=203.0.113.1,1=203.0.113.2

# Create VPN tunnels (2 for HA)
gcloud compute vpn-tunnels create tunnel-0 \
    --vpn-gateway=ha-vpn-gateway \
    --peer-external-gateway=on-prem-gateway \
    --peer-external-gateway-interface=0 \
    --shared-secret=mySharedSecret \
    --router=my-router \
    --ike-version=2 \
    --region=us-central1
```

### Anthos Multi-Cloud Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Anthos Multi-Cloud                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│          ┌─────────────────────────────────┐                    │
│          │      Anthos Control Plane       │                    │
│          │   (Fleet Management, Config)    │                    │
│          └─────────────────────────────────┘                    │
│                          │                                       │
│     ┌────────────────────┼────────────────────┐                 │
│     ↓                    ↓                    ↓                 │
│  ┌──────────┐      ┌──────────┐      ┌──────────────┐          │
│  │   GKE    │      │  Anthos  │      │   Anthos     │          │
│  │ (Google  │      │   on     │      │   on AWS/    │          │
│  │  Cloud)  │      │   VMware │      │   Azure      │          │
│  └──────────┘      └──────────┘      └──────────────┘          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 🧠 Key Decision Frameworks

### High Availability (HA) Design

| Level | Implementation | SLA Target |
| :--- | :--- | :--- |
| **Single Zone** | Single zone deployment | ~99.5% |
| **Multi-Zone (Regional)** | Deploy across zones in one region | ~99.9% |
| **Multi-Region** | Deploy across multiple regions | ~99.99% |

**Example: Regional MIG with Autoscaling**
```bash
# Create an instance template
gcloud compute instance-templates create web-template \
    --machine-type=e2-medium \
    --image-family=debian-12 \
    --image-project=debian-cloud \
    --tags=http-server

# Create a regional managed instance group
gcloud compute instance-groups managed create web-mig \
    --template=web-template \
    --size=3 \
    --region=us-central1

# Configure autoscaling
gcloud compute instance-groups managed set-autoscaling web-mig \
    --region=us-central1 \
    --min-num-replicas=3 \
    --max-num-replicas=10 \
    --target-cpu-utilization=0.7
```

### Disaster Recovery (DR) Patterns

| Pattern | RTO | RPO | Cost | Example |
| :--- | :--- | :--- | :--- | :--- |
| **Cold** | Days | Hours-Days | $ | Backup to GCS, restore when needed |
| **Warm** | Hours | Minutes-Hours | $$ | Standby instances, async replication |
| **Hot** | Minutes | Near-zero | $$$ | Active-active, sync replication |

### Scalability Patterns

| Pattern | Description | Google Cloud Implementation |
| :--- | :--- | :--- |
| **Horizontal Scaling** | Add more instances | MIGs, GKE autoscaling |
| **Vertical Scaling** | Increase instance size | Change machine type |
| **Database Sharding** | Partition data across databases | Cloud Spanner (automatic) |
| **Caching** | Reduce database load | Memorystore (Redis/Memcached) |
| **CDN** | Cache static content at edge | Cloud CDN |

## 📋 Architecture Decision Record Template

When documenting architecture decisions, use this template:

```markdown
## ADR-001: Choice of Container Orchestration Platform

### Status
Accepted

### Context
We need to run containerized microservices with varying scale requirements.

### Decision
Use GKE Autopilot for production workloads.

### Consequences
**Positive:**
- Reduced operational overhead
- Pay per pod, not per node
- Built-in security hardening

**Negative:**
- Less control over node configuration
- Some workloads may not be supported
```

---

📚 **Documentation Links**:
- [Well-Architected Framework](https://cloud.google.com/architecture/framework)
- [Cloud Architecture Center](https://cloud.google.com/architecture)
- [Hybrid and Multi-cloud Patterns](https://cloud.google.com/architecture/hybrid-multicloud-patterns)
- [Microservices Architecture on Google Cloud](https://cloud.google.com/architecture/microservices-architecture-refactoring-monoliths)

---
[Next Chapter: Compute & Networking Infrastructure](03_Compute_and_Networking_Infrastructure.md)
