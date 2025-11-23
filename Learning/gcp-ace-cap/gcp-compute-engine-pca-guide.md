# Google Compute Engine - Professional Cloud Architect (PCA) Comprehensive Guide

## Table of Contents
1. [Architectural Overview](#architectural-overview)
2. [Design Decisions & Trade-offs](#design-decisions--trade-offs)
3. [High Availability & Disaster Recovery](#high-availability--disaster-recovery)
4. [Performance Optimization](#performance-optimization)
5. [Cost Optimization Strategies](#cost-optimization-strategies)
6. [Security Architecture](#security-architecture)
7. [Migration Strategies](#migration-strategies)
8. [Enterprise Patterns](#enterprise-patterns)
9. [PCA Exam Tips](#pca-exam-tips)

---

## Architectural Overview

For the Professional Cloud Architect exam, Compute Engine represents the foundation of IaaS solutions. You must design architectures that balance cost, performance, availability, and security while meeting business requirements.

### When to Choose Compute Engine

**Best For:**
- Full control over OS and software stack
- Legacy applications requiring specific configurations
- Applications with consistent, predictable workloads
- GPU/TPU intensive workloads
- Hybrid cloud scenarios

**Consider Alternatives:**
- **App Engine/Cloud Run:** For fully managed containerized apps
- **GKE:** For container orchestration at scale
- **Cloud Functions:** For event-driven, short-lived tasks

---

## Design Decisions & Trade-offs

### Machine Type Selection

| Workload | Recommended Family | Rationale |
|----------|-------------------|-----------|
| **Web/App Servers** | N-series (N4, N2, N2D) | Balanced CPU/memory, good all-around |
| **Databases (OLTP)** | C-series (C4, C3) | High single-thread performance |
| **In-Memory Databases** | M-series (M3, M2) | High memory-to-CPU ratio |
| **Batch Processing** | E2 or Spot VMs | Cost-effective for fault-tolerant |
| **Analytics/Data Warehouses** | Z3 | High local SSD throughput |
| **ML Training** | A-series (A3, A2) | GPU-accelerated |
| **ML Inference** | G2 or T4 GPUs | Cost-effective GPU inference |

### Preemptible vs Spot vs On-Demand

**Preemptible VMs:**
- 60-80% discount
- Can be terminated anytime
- Max 24 hours runtime
- Best for: Batch jobs, fault-tolerant workloads

**Spot VMs:**
- 60-91% discount
- Can be terminated anytime
- No maximum runtime
- Best for: Modern containerized workloads with checkpointing

**On-Demand:**
- No discount (unless committed use)
- Guaranteed availability
- Best for: Production services requiring high availability

**Design Pattern:**
```
Load Balancer
├── On-Demand VMs (minimum capacity)
└── Spot VMs (burst capacity, 70%+ of fleet)
```

### Regional vs Zonal Resources

**Zonal Resources:**
- Instances, persistent disks (standard)
- Lower latency within zone
- Cheaper

**Regional Resources:**
- Regional persistent disks (synchronously replicated)
- Higher availability
- Higher cost (+50%)

**Architecture Decision:**
```
Single Zone: Lower cost, lower availability
Multi-Zone (same region): HA within region, moderate cost
Multi-Region: Global HA, highest cost
```

---

## High Availability & Disaster Recovery

### Multi-Zone Deployment

**Managed Instance Group with Regional Distribution:**
```bash
gcloud compute instance-groups managed create web-mig \
  --template=web-template \
  --size=6 \
  --region=us-central1 \
  --distribution-policy-zones=us-central1-a,us-central1-b,us-central1-c
```

**Benefits:**
- Survives zone failures
- Automatic VM redistribution
- Integrated with load balancing

### Health Checks & Autohealing

**Configure Health Check:**
```bash
gcloud compute health-checks create http web-health-check \
  --port=80 \
  --request-path=/health \
  --check-interval=10s \
  --timeout=5s \
  --unhealthy-threshold=3 \
  --healthy-threshold=2
```

**Apply to MIG:**
```bash
gcloud compute instance-groups managed set-autohealing web-mig \
  --health-check=web-health-check \
  --initial-delay=300 \
  --region=us-central1
```

### Disaster Recovery Strategies

**1. Backup Strategy:**
- **Snapshots:** Point-in-time disk backups
  - Schedule daily snapshots
  - Retain snapshots per policy (7 daily, 4 weekly)
  - Cross-region snapshot replication

**2. RPO (Recovery Point Objective):**
- Snapshot-based: RPO = snapshot frequency (e.g., 1 hour)
- Continuous replication: RPO near zero (use regional disks)

**3. RTO (Recovery Time Objective):**
- Active-Active: RTO < 1 minute (multi-region)
- Active-Passive: RTO 5-30 minutes (standby region)
- Backup/Restore: RTO 1-4 hours (restore from snapshots)

**Multi-Region DR Pattern:**
```
Region A (Active)
├── Load Balancer (Global)
├── MIG (serving traffic)
└── Snapshots (replicated to Region B)

Region B (Standby)
├── Warm standby MIG (minimal size)
└── Snapshots (ready for quick scale-up)
```

---

## Performance Optimization

### Right-Sizing Instances

**Use Rightsizing Recommendations:**
- Cloud Console > Compute Engine > Recommendations
- Based on actual usage patterns
- Can reduce costs by 30-50%

**Custom Machine Types:**
```bash
# Instead of n2-standard-8 (8 vCPU, 32 GB)
# Use custom if you only need 20 GB RAM
gcloud compute instances create optimized-vm \
  --custom-cpu=8 \
  --custom-memory=20GB
```

**Savings:** 5% premium but saves 30% on unused RAM

### Storage Performance

**Disk IOPS/Throughput Limits:**
- Depends on machine type vCPU count
- More vCPUs = higher disk throughput

| Machine Type | Max Read IOPS | Max Write IOPS |
|--------------|---------------|----------------|
| 1-2 vCPUs | 15,000 | 15,000 |
| 3-4 vCPUs | 15,000 | 15,000 |
| 8+ vCPUs | 60,000 | 30,000 |
| 32+ vCPUs | 100,000 | 50,000 |

**Optimize for I/O:**
1. Use SSD persistent disks for high IOPS
2. Increase machine type vCPUs (if disk-bound)
3. Use local SSDs for highest performance (400K+ IOPS)
4. Stripe multiple disks for aggregated throughput

### Network Performance

**Tier 1 Networking:**
- Available for C3, N2, C2 series with 16+ vCPUs
- Up to 100 Gbps bandwidth
- Use for high-throughput applications

**Optimize Network:**
1. Use VPC-native networks
2. Enable IP aliasing for GKE workloads
3. Use internal load balancing for internal traffic
4. Enable Cloud CDN for static content

---

## Cost Optimization Strategies

### Committed Use Discounts (CUDs)

**Resource-Based CUDs:**
- 1-year: 37% discount
- 3-year: 55% discount
- Commit to specific machine types in specific regions

```bash
gcloud compute commitments create my-commitment \
  --resources=vcpu=100,memory=200GB \
  --plan=twelve-month \
  --region=us-central1
```

**Spend-Based CUDs:**
- 1-year: 25% discount
- 3-year: 52% discount
- Flexible across machine types and regions

### Sustained Use Discounts (SUDs)

- Automatic for N1, N2, N2D, E2 instances
- Up to 30% discount for usage over 25% of month
- No commitment required

### Cost Optimization Patterns

**1. Right-Size + Committed Use:**
```
Original: 10x n2-standard-16 on-demand = $5,840/month
Optimized: 10x n2-standard-8 with 1-year CUD = $2,317/month
Savings: 60%
```

**2. Hybrid On-Demand + Spot:**
```
4x on-demand (baseline) + 16x Spot (burst) = 70% savings
```

**3. Schedule-Based Scaling:**
```bash
# Stop dev/test VMs during non-business hours
# Save 60% (12 hours/day * 5 days/week)
```

**4. Use Smaller, More Efficient Machine Types:**
- E2 series: Best price-performance for general workloads
- T2D/T2A: Optimized for scale-out workloads
- 20-30% cheaper than equivalent N-series

### Cost Monitoring

**Set Budgets:**
```bash
gcloud billing budgets create \
  --billing-account=BILLING_ACCOUNT_ID \
  --display-name="Compute Engine Budget" \
  --budget-amount=5000
```

**Use Cost Allocation Labels:**
```bash
gcloud compute instances add-labels INSTANCE \
  --labels=environment=production,team=backend,cost-center=engineering
```

---

## Security Architecture

### Defense in Depth

**Layer 1: Network Security**
- VPC firewall rules (default deny)
- Private Google Access (no external IPs)
- Cloud NAT for egress
- VPC Service Controls (perimeter security)

**Layer 2: Identity & Access**
- Service accounts with minimal permissions
- OS Login for SSH access management
- IAM policies at project/folder level

**Layer 3: Data Protection**
- Encryption at rest (automatic)
- Customer-managed encryption keys (CMEK)
- Shielded VMs (UEFI, Secure Boot, vTPM)

### Secure Architecture Pattern

```
Internet
    ↓
Cloud Armor (DDoS protection)
    ↓
Global Load Balancer (HTTPS)
    ↓
Cloud IAP (Identity-Aware Proxy)
    ↓
Web Tier (Public subnet, minimal access)
    ↓
Internal Load Balancer
    ↓
App Tier (Private subnet, no external IP)
    ↓
Database (Private subnet, Private Service Connect)
```

### Shielded VMs

Enable for security-critical workloads:
```bash
gcloud compute instances create secure-vm \
  --shielded-secure-boot \
  --shielded-vtpm \
  --shielded-integrity-monitoring
```

**Benefits:**
- Verifiable boot integrity
- Protection against rootkits/bootkits
- Compliance requirements (PCI-DSS, HIPAA)

### Confidential Computing

For sensitive data processing:
```bash
gcloud compute instances create confidential-vm \
  --machine-type=n2d-standard-4 \
  --confidential-compute \
  --maintenance-policy=TERMINATE
```

**Use Cases:**
- Healthcare (HIPAA)
- Financial services (PCI-DSS)
- Government (FedRAMP)

---

## Migration Strategies

### Lift-and-Shift (Rehost)

**VM Migration Service:**
- Migrate VMs from on-premises, AWS, Azure
- Minimal downtime (replication-based)
- Automated conversion

**Steps:**
1. Install Migrate for Compute Engine connector
2. Discover source VMs
3. Create test clones in GCP
4. Validate and cut over

### Refactor & Modernize

**Containerization Path:**
```
Physical/VM → Container → GKE → Cloud Run (fully managed)
```

**Database Modernization:**
```
Self-managed DB → Cloud SQL (managed) → Cloud Spanner (global scale)
```

### Hybrid Cloud Architecture

**Use Cases:**
- Data residency requirements
- Gradual migration
- Burst to cloud

**Components:**
- **Cloud VPN/Interconnect:** Secure connectivity
- **Shared VPC:** Centralized network management
- **Workload Identity:** Secure service-to-service auth

---

## Enterprise Patterns

### Multi-Tenancy

**Approach 1: Project-Based Isolation**
```
Organization
├── Production Folder
│   ├── App1 Project (Team A)
│   └── App2 Project (Team B)
└── Development Folder
    ├── Dev1 Project
    └── Dev2 Project
```

**Approach 2: Network-Based Isolation**
```
Shared VPC Host Project
├── Subnet A (Team A, 10.1.0.0/16)
├── Subnet B (Team B, 10.2.0.0/16)
└── Shared Services (10.0.0.0/16)
```

### Auto-Scaling Strategies

**CPU-Based:**
```bash
gcloud compute instance-groups managed set-autoscaling web-mig \
  --target-cpu-utilization=0.6 \
  --min-num-replicas=2 \
  --max-num-replicas=20
```

**Load Balancer-Based:**
```bash
gcloud compute instance-groups managed set-autoscaling web-mig \
  --target-load-balancing-utilization=0.8 \
  --min-num-replicas=2 \
  --max-num-replicas=50
```

**Custom Metrics:**
```bash
gcloud compute instance-groups managed set-autoscaling web-mig \
  --custom-metric-utilization metric=custom.googleapis.com/queue_depth,target=100
```

### Blue-Green Deployments

**Using Managed Instance Groups:**
1. Create new instance template with updated code (Green)
2. Create new MIG from Green template
3. Update load balancer backend to include Green MIG
4. Gradually shift traffic from Blue to Green
5. Delete Blue MIG after validation

---

## PCA Exam Tips

1. **Cost Optimization:** Know all discount types (CUDs, SUDs, Spot, Preemptible). Combine them for maximum savings.

2. **HA Design:** Multi-zone MIGs with regional load balancers. Understand RPO vs RTO trade-offs.

3. **Machine Type Selection:** Match workload to machine family. Don't use memory-optimized for CPU-bound workloads.

4. **Security Layering:** Network (firewall) + Identity (IAM) + Data (encryption). Know when to use Shielded VMs and Confidential Computing.

5. **Migration Patterns:** Lift-and-shift (quick), refactor (optimize), rebuild (modernize). Choose based on business constraints.

6. **Multi-Region Design:** Requires global load balancer. Consider latency vs redundancy trade-offs.

7. **Managed Instance Groups:** Core of scalable architecture. Know health checks, autohealing, autoscaling.

8. **Persistent Disks:** Understand zonal vs regional. Regional disks have synchronous replication (higher availability, higher cost).

9. **Sole-Tenant Nodes:** For compliance (licensing, isolation). Higher cost, use only when required.

10. **Rightsizing:** Use recommendations. Custom machine types save money but add 5% premium.
