# SAA-C03 Concepts Deep Dive

Cross-cutting concepts that appear on multiple exam questions. Each section explains **what it is**, **why it matters**, **how services differ**, and **exam traps** to avoid.

---

## Table of Contents

1. [Multi-AZ vs Multi-Region vs Read Replicas](#multi-az-vs-multi-region-vs-read-replicas)
2. [Security Groups vs Network ACLs](#security-groups-vs-network-acls)
3. [Gateway vs Interface VPC Endpoints](#gateway-vs-interface-vpc-endpoints)
4. [Synchronous vs Asynchronous Integration](#synchronous-vs-asynchronous-integration)
5. [Stateful vs Stateless Applications](#stateful-vs-stateless-applications)
6. [Database Selection Decision Tree](#database-selection-decision-tree)
7. [Storage Type Selection](#storage-type-selection)
8. [Load Balancer Selection](#load-balancer-selection)
9. [CloudFront vs Global Accelerator](#cloudfront-vs-global-accelerator)
10. [IAM Policy Evaluation Logic](#iam-policy-evaluation-logic)
11. [Disaster Recovery Strategies](#disaster-recovery-strategies)
12. [EC2 Pricing Models](#ec2-pricing-models)
13. [S3 Storage Class Selection](#s3-storage-class-selection)
14. [Cost Optimization Decision Framework](#cost-optimization-decision-framework)
15. [NAT Gateway vs NAT Instance](#nat-gateway-vs-nat-instance)
16. [VPC Peering vs Transit Gateway vs PrivateLink](#vpc-peering-vs-transit-gateway-vs-privatelink)
17. [Encryption Options Compared](#encryption-options-compared)
18. [Cognito User Pools vs Identity Pools](#cognito-user-pools-vs-identity-pools)
19. [Secrets Manager vs Parameter Store](#secrets-manager-vs-parameter-store)
20. [SQS Standard vs FIFO](#sqs-standard-vs-fifo)

---

## Multi-AZ vs Multi-Region vs Read Replicas

These three patterns solve **different problems** and are one of the most confused topics on the exam.

### Multi-AZ (High Availability within a Region)

**Purpose:** Survive an Availability Zone failure without manual intervention.

**How it works:**
- AWS maintains a **synchronous standby** in a different AZ
- Automatic failover when primary fails
- Same DNS endpoint — applications don't change connection strings
- Standby is **not readable** (for RDS) — it's a hot spare only

**Services:**
| Service | Multi-AZ behavior |
|---------|-------------------|
| RDS / Aurora | Standby replica in another AZ; auto failover (~60–120 sec) |
| ELB | Automatically spans multiple AZs |
| S3 | Data replicated across ≥3 AZs by default |
| EFS | Standard class replicates across AZs |

**Exam answer when:** "Database must remain available if an AZ fails" → **Multi-AZ**

### Read Replicas (Scale Reads, Not HA for Writes)

**Purpose:** Offload read traffic; optionally promote to primary.

**How it works:**
- **Asynchronous replication** from primary
- Replicas are **readable** — use different endpoint
- Can be in **same region or cross-region**
- Promotion to primary is **manual** (except Aurora, which has faster promotion)
- Does **not** provide automatic write failover by itself

**Exam answer when:** "Read-heavy workload" or "reporting queries shouldn't impact production" → **Read Replicas**

### Multi-Region (Disaster Recovery / Global Presence)

**Purpose:** Survive entire region failure; serve global users.

**How it works:**
- Independent deployments in multiple regions
- Data replicated asynchronously (S3 CRR, DynamoDB Global Tables, Aurora Global Database)
- Route 53 health checks + failover routing
- Higher complexity and cost

**Exam answer when:** "Region-level disaster recovery" or "RTO/RPO in minutes across regions" → **Multi-Region architecture**

### Quick Comparison

| | Multi-AZ | Read Replica | Multi-Region |
|--|----------|--------------|--------------|
| **Protects against** | AZ failure | Read overload | Region failure |
| **Replication** | Synchronous | Asynchronous | Asynchronous |
| **Failover** | Automatic | Manual promotion | Route 53 / manual |
| **Readable standby** | No (RDS) | Yes | Yes (in DR region) |
| **Same endpoint** | Yes | No (separate endpoint) | No |

> **Exam trap:** "High availability for RDS" ≠ Read Replicas. Multi-AZ is for HA; Read Replicas are for read scaling.

---

## Security Groups vs Network ACLs

Both filter network traffic, but they operate at different layers with different rules.

### Security Groups (Instance Level)

- **Stateful:** Return traffic is automatically allowed regardless of outbound rules
- **Allow rules only:** Cannot explicitly deny
- **Evaluates all rules:** If any rule allows, traffic is permitted
- **Applied to:** ENI (network interface) — instance level
- **Default:** Deny all inbound, allow all outbound

**Example:** If you allow inbound TCP 443, the response traffic is automatically allowed back out — you don't need an outbound rule.

### Network ACLs (Subnet Level)

- **Stateless:** Must allow both inbound AND outbound for a connection
- **Allow and deny rules:** Can explicitly block IP ranges
- **Processed in order:** Lowest rule number first; first match wins
- **Applied to:** Subnet — affects all instances in the subnet
- **Default NACL:** Allow all. Custom NACL: Deny all until rules added

**Example:** To allow HTTPS through a custom NACL, you need:
- Inbound: Allow TCP 443
- Outbound: Allow ephemeral ports 1024–65535 (for return traffic)

### When to Use Which

| Scenario | Use |
|----------|-----|
| Application-tier access control | Security Groups |
| Block specific IP at subnet boundary | NACL (deny rule) |
| Reference another security group | Security Group |
| Additional compliance layer | Both (defense in depth) |
| Bastion / ALB access | Security Group |

> **Exam trap:** "Block IP address 203.0.113.50" → NACL deny rule (SGs can't deny). "Allow app servers to talk to database" → Security Group referencing another SG.

---

## Gateway vs Interface VPC Endpoints

VPC endpoints let private subnet resources access AWS services **without going through the internet or NAT Gateway**.

### Gateway Endpoints (Free)

| Property | Value |
|----------|-------|
| **Services** | Amazon S3, DynamoDB only |
| **Type** | Route table entry (prefix list) |
| **Cost** | Free (no hourly or data charges) |
| **Access** | VPC-wide via route tables |
| **Security** | Bucket/table policy + IAM (no SG on endpoint) |

**How it works:** A route is added to your route table pointing S3/DynamoDB traffic to the VPC endpoint instead of the IGW/NAT.

```
Private Subnet → Route Table → Gateway Endpoint → S3 (stays on AWS network)
```

### Interface Endpoints (PrivateLink)

| Property | Value |
|----------|-------|
| **Services** | Most AWS services (EC2, SNS, SQS, Lambda, etc.) |
| **Type** | Elastic Network Interface (ENI) with private IP |
| **Cost** | ~$0.01/hr per AZ + $0.01/GB data processed |
| **Access** | Per-subnet (must add endpoint to subnets) |
| **Security** | Security Group on the endpoint ENI |
| **DNS** | Private DNS enabled by default |

**How it works:** An ENI is placed in your subnet. DNS resolves the AWS service to a private IP within your VPC.

### Decision Guide

| Need | Solution |
|------|----------|
| Private S3 access from VPC | Gateway Endpoint (free) |
| Private DynamoDB access | Gateway Endpoint (free) |
| Private SNS/SQS/Lambda access | Interface Endpoint |
| On-premises access to your VPC service | PrivateLink (you as provider) |
| Reduce NAT Gateway costs for S3 | Gateway Endpoint |

> **Exam trap:** S3 is NOT an Interface endpoint — it's Gateway only. Choosing Interface endpoint for S3 is wrong.

---

## Synchronous vs Asynchronous Integration

### Synchronous (Request-Response)

```
Client ──request──▶ Service A ──request──▶ Service B ──response──▶ Service A ──response──▶ Client
```

- Caller **waits** for response
- Tight coupling — if B is down, A fails
- Examples: REST API calls, ALB → EC2, direct RDS queries

**Use when:** Immediate response required, simple workflows

### Asynchronous (Event-Driven)

```
Producer ──message──▶ Queue/Topic ──▶ Consumer (processes when ready)
```

- Caller **does not wait** — fire and forget
- Loose coupling — consumer can be down temporarily
- Examples: SQS, SNS, EventBridge, Kinesis

**Use when:** Decoupling required, burst traffic, long-running processing, "minimum impact if downstream fails"

### Service Mapping

| Pattern | AWS Services |
|---------|-------------|
| Sync API | API Gateway → Lambda/EC2 |
| Async queue | SQS (competing consumers) |
| Async pub/sub | SNS (fan-out to many) |
| Async event routing | EventBridge (rules, schedules, event buses) |
| Async streaming | Kinesis Data Streams |
| Orchestration | Step Functions (coordinates sync + async) |

> **Exam trap:** "Decouple order processing from inventory update" → SQS or SNS, not direct API call.

---

## Stateful vs Stateless Applications

### Stateless
- No session data stored on the server
- Any instance can handle any request
- **Scale horizontally** easily behind a load balancer
- Session state stored externally: ElastiCache, DynamoDB, client cookies

### Stateful
- Server retains session/context between requests
- Sticky sessions needed (ALB sticky sessions) or dedicated instances
- Harder to scale; instance failure loses state
- Examples: WebSocket servers, gaming sessions, legacy apps

**Exam pattern:** "Scale web tier horizontally" → Design stateless app + store sessions in ElastiCache/DynamoDB + ALB without stickiness.

---

## Database Selection Decision Tree

```
Start: What type of data and access pattern?
│
├── Relational (ACID, joins, complex queries)
│   ├── MySQL/PostgreSQL compatible, AWS-optimized → Aurora
│   ├── Standard relational, managed → RDS
│   ├── Data warehouse / analytics → Redshift
│   └── Lift-and-shift Oracle/SQL Server → RDS with BYOL
│
├── NoSQL
│   ├── Key-value / document, single-digit ms, any scale → DynamoDB
│   ├── In-memory cache / session store → ElastiCache
│   ├── Full-text search / log analytics → OpenSearch
│   └── Graph relationships → Neptune (out of scope but know it exists)
│
├── Ad-hoc SQL on S3 data lake → Athena
├── ETL / data catalog → Glue
└── Time series → Timestream (awareness)
```

### DynamoDB vs RDS — When to Choose

| Factor | Choose DynamoDB | Choose RDS/Aurora |
|--------|----------------|-------------------|
| Access pattern | Known keys, simple queries | Complex joins, ad-hoc SQL |
| Scale | Massive, unpredictable | Moderate, predictable |
| Operations | Fully serverless option | Managed but instance-based |
| Consistency | Eventually or strong per item | Full ACID transactions |
| Cost model | Per request (on-demand) or capacity | Per instance hour |

---

## Storage Type Selection

| Type | AWS Services | Access | Use Case |
|------|-------------|--------|----------|
| **Object** | S3, Glacier | HTTP/API, key-based | Images, backups, data lakes, static websites |
| **Block** | EBS | Attached to single EC2, like a disk | Boot volumes, databases on EC2, low-latency |
| **File** | EFS, FSx | NFS/SMB, multi-attach | Shared files, content management, home directories |

### EBS vs EFS vs S3

| | EBS | EFS | S3 |
|--|-----|-----|-----|
| **Scope** | Single AZ (unless multi-attach io2) | Multi-AZ, multi-EC2 | Regional, global via CloudFront |
| **Max size** | 64 TiB per volume | Petabyte scale | Unlimited |
| **Latency** | Lowest (block) | Low (file) | Higher (object API) |
| **Cost** | Per GB + IOPS | Per GB + throughput | Per GB + requests |

---

## Load Balancer Selection

| | ALB (Layer 7) | NLB (Layer 4) | GLB (Layer 3 Gateway) |
|--|--------------|--------------|----------------------|
| **Protocol** | HTTP/HTTPS/WebSocket | TCP/UDP/TLS | IP packets |
| **Routing** | Path, host, header based | Flow hash | To appliances (firewalls) |
| **Static IP** | No | Yes (one per AZ) | N/A |
| **Use case** | Web apps, microservices | Extreme performance, static IP | Network virtual appliances |
| **WebSockets** | Yes | Yes (TCP) | No |

**Exam shortcuts:**
- Web application with path routing → **ALB**
- Millions of req/sec, static IP, TCP/UDP → **NLB**
- Route traffic to firewall appliances → **Gateway LB**
- "Lowest latency, preserve source IP" → **NLB**

---

## CloudFront vs Global Accelerator

Both improve global performance, but for **different protocols and use cases**.

| | CloudFront | Global Accelerator |
|--|-----------|---------------------|
| **Layer** | Layer 7 (HTTP/HTTPS) | Layer 4 (TCP/UDP) |
| **Edge caching** | Yes — caches content | No — routes traffic |
| **Static IP / Anycast** | No | Yes (2 static IPs) |
| **Protocols** | HTTP, HTTPS, WebSocket | TCP, UDP (any) |
| **Health checks** | Origin health | Endpoint health |
| **Best for** | Static/dynamic web content, APIs | Gaming, IoT, non-HTTP, fixed IP |

> **Exam trap:** Gaming company needs UDP with static IP → Global Accelerator. Media company serving videos → CloudFront.

---

## IAM Policy Evaluation Logic

When AWS evaluates whether a request is allowed:

```
1. Default: DENY all
2. Explicit DENY in any policy? → DENY (cannot be overridden)
3. Organizations SCP allows action? → If SCP denies, DENY
4. Resource-based policy allows? → Continue
5. Identity-based policy allows? → Continue
6. Permissions boundary allows? → If boundary denies, DENY
7. Session policy allows? → Continue
8. Any explicit ALLOW found? → ALLOW
9. No ALLOW found? → DENY (implicit deny)
```

**Key rules:**
- **Explicit Deny always wins** — even over Allow
- **SCPs filter maximum permissions** — they never grant, only restrict
- **Permission boundaries cap** what an identity can receive — intersection, not union
- **Cross-account access:** Need Allow in BOTH identity policy AND resource policy (or role trust)

---

## Disaster Recovery Strategies

| Strategy | Infrastructure in DR | RTO | RPO | Relative Cost |
|----------|---------------------|-----|-----|---------------|
| **Backup & Restore** | None (restore from backup) | Hours | Hours–days | $ |
| **Pilot Light** | Minimal (DB snapshot, AMIs) | 10s of minutes | Minutes | $$ |
| **Warm Standby** | Scaled-down full stack | Minutes | Minutes | $$$ |
| **Active-Active** | Full production both regions | ~Zero | ~Zero | $$$$ |

**How to match business requirements:**
- "Can tolerate hours of downtime" → Backup & Restore
- "Core DB must be ready quickly, app can wait" → Pilot Light
- "Must failover in minutes" → Warm Standby
- "Zero downtime required globally" → Active-Active Multi-Region

---

## EC2 Pricing Models

| Model | Savings | Flexibility | Risk |
|-------|---------|-------------|------|
| **On-Demand** | None | Full | None |
| **Reserved (Standard)** | Up to 72% | Locked to instance family/AZ | Pay even if unused |
| **Reserved (Convertible)** | Up to 66% | Can change instance family | Less savings |
| **Savings Plans** | Up to 72% | Flexible across EC2, Fargate, Lambda | Commitment to $/hr |
| **Spot** | Up to 90% | Can be interrupted with 2-min notice | Interruption |
| **Dedicated Host** | Per-socket licensing | Physical isolation | Highest cost |

**Spot best practices:** Use for batch, CI/CD, stateless, fault-tolerant. Combine with Spot Fleet or Auto Scaling.

---

## S3 Storage Class Selection

```
Access frequency?
│
├── Daily / frequent → S3 Standard
├── Monthly / infrequent, instant retrieval → S3 Standard-IA or One Zone-IA (non-critical)
├── Unknown / changing → S3 Intelligent-Tiering
├── Archive, instant retrieval needed → Glacier Instant Retrieval
├── Archive, retrieval in hours OK → Glacier Flexible Retrieval
├── Long-term (7+ years), retrieval in 12–48 hrs → Glacier Deep Archive
└── Frequently accessed via CloudFront → S3 Standard + CloudFront cache
```

**Minimum storage durations (early deletion fees):**
- Standard-IA / One Zone-IA: 30 days
- Glacier Instant / Flexible: 90 days
- Deep Archive: 180 days

---

## Cost Optimization Decision Framework

When a question asks for "most cost-effective":

1. **Eliminate over-provisioned resources** — Right-size with Compute Optimizer
2. **Match pricing model to usage** — Spot for batch, RI for steady state
3. **Use appropriate storage tier** — Lifecycle policies, Intelligent-Tiering
4. **Reduce data transfer** — VPC endpoints, CloudFront, same-AZ placement
5. **Use serverless for variable load** — Lambda, DynamoDB on-demand, Fargate
6. **Delete unused resources** — EBS snapshots, idle ELBs, unattached EIPs
7. **Consolidate accounts** — Organizations consolidated billing

---

## NAT Gateway vs NAT Instance

| | NAT Gateway | NAT Instance |
|--|------------|--------------|
| **Managed** | Yes (AWS) | No (you manage EC2) |
| **Availability** | Multi-AZ option (one per AZ) | Single point of failure |
| **Bandwidth** | Up to 100 Gbps | Depends on instance type |
| **Cost** | Hourly + per GB processed | EC2 instance cost (can be cheaper at low volume) |
| **Maintenance** | None | Patching, scaling, monitoring |
| **Security Group** | N/A | Must configure SG |

> **Exam default:** Prefer NAT Gateway unless question explicitly asks for cost optimization at very low traffic or custom NAT configuration.

---

## VPC Peering vs Transit Gateway vs PrivateLink

| | VPC Peering | Transit Gateway | PrivateLink |
|--|------------|----------------|-------------|
| **Scope** | Two VPCs | Many VPCs + on-prem | Service consumer → provider |
| **Transitive** | No | Yes | N/A |
| **Overlapping CIDR** | Not allowed | Not allowed (per peering) | N/A |
| **Cost model** | Data processing only | TGW hourly + data processing | Interface endpoint hourly + data |
| **Use case** | Simple two-VPC connection | Hub-and-spoke enterprise | Access SaaS/partner service privately |

> **Exam trap:** VPC A ↔ B ↔ C does NOT mean A can reach C via peering. Need Transit Gateway for transitive routing.

---

## Encryption Options Compared

### At Rest

| Method | Who manages keys | Audit trail | Use case |
|--------|-----------------|-------------|----------|
| SSE-S3 | AWS | No | Default encryption, general data |
| SSE-KMS | AWS KMS (you control policy) | Yes (CloudTrail) | Sensitive data, key rotation |
| SSE-C | You provide key each request | No | Full customer control |
| Client-side | You | Your responsibility | Maximum security |

### In Transit
- **TLS/HTTPS** — Always for data in transit
- **ACM** — Free public SSL/TLS certificates
- **VPN / Direct Connect** — Encrypted tunnels to on-premises

---

## Cognito User Pools vs Identity Pools

| | User Pools | Identity Pools |
|--|-----------|----------------|
| **Purpose** | User directory (sign-up/sign-in) | Exchange identity for AWS credentials |
| **Provides** | JWT tokens (ID, access, refresh) | Temporary AWS credentials (via STS) |
| **Auth methods** | Email/password, social, SAML, OIDC | Federated identities |
| **Use with API Gateway** | Cognito authorizer | IAM authorization |
| **Use case** | Authenticate users to your app | Grant AWS resource access to users |

**Typical pattern:** User Pool for authentication → Identity Pool for AWS resource access (S3 upload, DynamoDB).

---

## Secrets Manager vs Parameter Store

| | Secrets Manager | Parameter Store (Standard) | Parameter Store (Advanced) |
|--|----------------|---------------------------|---------------------------|
| **Cost** | ~$0.40/secret/month | Free | ~$0.05/parameter/month |
| **Rotation** | Automatic (Lambda) | Manual | Manual |
| **Cross-region replication** | Yes | No | No |
| **Max size** | 64 KB | 4 KB | 8 KB |
| **Use case** | DB credentials, API keys with rotation | Config values, non-rotating secrets | Larger secrets, parameter policies |

> **Exam default:** Secrets Manager for credentials needing automatic rotation; Parameter Store for configuration and non-sensitive parameters.

---

## SQS Standard vs FIFO

| | Standard | FIFO |
|--|----------|------|
| **Throughput** | Unlimited | 3,000 msg/sec (with batching: 30,000) |
| **Ordering** | Best-effort (no guarantee) | Strict FIFO order |
| **Delivery** | At-least-once (duplicates possible) | Exactly-once processing |
| **Use case** | High throughput, order doesn't matter | Order processing, financial transactions |
| **Queue name** | Any name | Must end in `.fifo` |

**Related patterns:**
- **Dead Letter Queue (DLQ):** Capture failed messages after max retries
- **Visibility timeout:** Time message is hidden after being read (default 30 sec)
- **Long polling:** Reduces empty responses (WaitTimeSeconds up to 20)

---

## Related Resources

- [Well-Architected Framework Guide](aws-well-architected-framework-saa-c03-guide.md)
- [README — Master Study Guide](README.md)
- Individual service guides for implementation details
