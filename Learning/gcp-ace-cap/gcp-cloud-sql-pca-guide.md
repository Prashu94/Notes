# Cloud SQL - Professional Cloud Architect Guide

## Table of Contents
1. [High Availability Architecture](#high-availability-architecture)
2. [Disaster Recovery Strategies](#disaster-recovery-strategies)
3. [Replication Patterns](#replication-patterns)
4. [Security Architecture](#security-architecture)
5. [Migration Strategies](#migration-strategies)
6. [Performance Optimization](#performance-optimization)
7. [Decision Matrices](#decision-matrices)

---

## High Availability Architecture

### Regional Availability (HA)

**Architecture:**
- **Primary Instance**: Located in Primary Zone (e.g., `us-central1-a`).
- **Standby Instance**: Located in Secondary Zone (e.g., `us-central1-b`).
- **Synchronous Replication**: Writes are committed to Regional Persistent Disk (replicated across zones) before acknowledged.
- **Shared IP**: Both instances share a single Static IP.

**Failover Process:**
1. **Detection**: Heartbeat failure (approx. 60s).
2. **Switch**: Standby instance becomes Primary.
3. **Re-routing**: Shared IP points to new Primary.
4. **Impact**: Brief downtime (typically < 60s). Existing connections dropped; app must reconnect.

**Requirements:**
- Automated backups must be enabled.
- Point-in-Time Recovery (PITR) must be enabled (requires binary logging).
- **SLA**: 99.95% availability for HA instances (General Purpose).

**Zonal vs Regional:**
- **Zonal**: Single zone. No failover. 99.5% SLA. Good for dev/test.
- **Regional (HA)**: Multi-zone. Automatic failover. 99.95% SLA. Required for production.

---

## Disaster Recovery Strategies

### Cross-Region Read Replicas

**Architecture:**
- Primary in Region A (e.g., `us-central1`).
- Read Replica in Region B (e.g., `us-east1`).
- **Asynchronous Replication**: Potential replication lag.

**DR Workflow (Promote Replica):**
1. **Region A Failure**: Primary becomes unavailable.
2. **Decision**: Promote Cross-Region Replica in Region B.
3. **Action**: `gcloud sql instances promote-replica my-replica`.
4. **Result**: Replica becomes standalone Primary.
5. **Post-Recovery**: Update application connection strings to new Primary IP.

**RTO/RPO Considerations:**
- **RPO (Recovery Point Objective)**: Depends on replication lag. Data not yet replicated is lost.
- **RTO (Recovery Time Objective)**: Time to promote replica + update app config.

### Database Migration Service (DMS) for DR

- Can be used to set up continuous replication from Cloud SQL to another Cloud SQL instance for DR purposes, often with easier switchover workflows.

---

## Replication Patterns

### 1. Read Replicas (In-Region)
- **Purpose**: Scale read traffic.
- **Load Balancing**: Cloud SQL does **not** provide a load balancer endpoint for replicas. You must implement client-side load balancing or use an internal L4 LB (ProxySQL/HAProxy).
- **Limit**: Up to 10 direct replicas.

### 2. Cross-Region Replicas
- **Purpose**: Disaster Recovery (DR) and Data Locality (serving users in another region).
- **Cost**: Incurs cross-region network egress charges.

### 3. Cascading Replicas
- **Architecture**: Primary -> Replica A -> Replica B.
- **Purpose**:
  - Offload replication log overhead from Primary.
  - Distribute reads in a multi-region topology (Primary -> Region B Replica -> Region B Local Replicas).
- **Limit**: Max 4 levels deep.

### 4. External Replicas
- **Purpose**: Hybrid cloud or multi-cloud scenarios.
- **External Read Replica**: Cloud SQL Primary -> On-prem MySQL Replica.
- **External Primary**: On-prem MySQL Primary -> Cloud SQL Replica (Migration path).

---

## Security Architecture

### Encryption
- **At Rest**: Encrypted by default (AES-256).
- **CMEK (Customer-Managed Encryption Keys)**: Use Cloud KMS keys to manage encryption.
  - **Key Revocation**: Revoking key renders database inaccessible (Crypto-shredding).
- **In Transit**: SSL/TLS. Enforce SSL with `require_ssl` flag.

### Network Security
- **Private Service Access**: VPC Peering. Private IP only.
- **Authorized Networks**: Public IP allowlist (Less secure, avoid for production).
- **Cloud SQL Auth Proxy**:
  - Authenticates via IAM (no static passwords in config).
  - Encrypts traffic.
  - Works with Private IP.

### IAM Integration
- **IAM Database Authentication**: Log in to DB using IAM users/service accounts instead of database passwords.
- **Roles**:
  - `roles/cloudsql.client`: Connect to instance.
  - `roles/cloudsql.admin`: Full control.
  - `roles/cloudsql.editor`: Manage instance (no delete/permission changes).

---

## Migration Strategies

### Database Migration Service (DMS)
- **Serverless**: Fully managed migration service.
- **Homogeneous**: MySQL to Cloud SQL for MySQL, PostgreSQL to Cloud SQL for PostgreSQL.
- **Continuous Replication**: Minimal downtime.
  1. Initial snapshot.
  2. Continuous replication (CDC).
  3. Cutover (Promote).

### External Master (Legacy)
- Configure Cloud SQL as a replica of an external master.
- Manual setup of VPN/Interconnect and replication user.

### Import/Export
- **Offline Migration**: Dump SQL -> Upload to GCS -> Import.
- **Downtime**: High (Time to dump + transfer + import).

---

## Performance Optimization

### Maintenance Windows
- **Deny Maintenance Period**: Block maintenance during peak business events (up to 90 days).
- **Order of Update**: Replicas updated first, then Primary.

### Query Insights
- Built-in observability tool.
- Identifies:
  - Top queries by load.
  - Long-running queries.
  - Lock contention.
- **Action**: Add indexes, optimize SQL, resize instance.

### Storage
- **SSD vs HDD**: Always use SSD for production (better IOPS).
- **IOPS**: Linked to disk size. Increase disk size to increase IOPS (up to 64TB).

---

## Decision Matrices

### Cloud SQL vs Cloud Spanner vs Bigtable

| Feature | Cloud SQL | Cloud Spanner | Bigtable |
|---------|-----------|---------------|----------|
| **Type** | Relational (OLTP) | Relational (OLTP) | NoSQL (Wide-column) |
| **Scale** | Vertical (up to ~64TB) | Horizontal (Petabytes) | Horizontal (Petabytes) |
| **Consistency** | Strong (Single Region) | Strong (Global) | Eventual (Multi-cluster) |
| **Availability** | 99.95% (Regional) | 99.999% (Global) | 99.99% |
| **Use Case** | ERP, CRM, Web Apps (MySQL/PG) | Global Supply Chain, Banking, High Scale | IoT, Time-series, AdTech |

### Cloud SQL Editions

| Feature | Enterprise | Enterprise Plus |
|---------|------------|-----------------|
| **Performance** | Standard | High (Data Cache, improved IO path) |
| **SLA** | 99.95% | 99.99% |
| **Maintenance** | < 60s downtime | < 10s downtime |
| **Replication** | Standard | Accelerated |
| **Use Case** | General workloads | High-performance, mission-critical |

---

## Cost Optimization Strategies

### Pricing Model

**Compute Costs:**
```
Per-hour cost = (vCPUs × $0.0413) + (GB RAM × $0.00698)

Example (db-n1-standard-4, us-central1):
- 4 vCPUs × $0.0413 = $0.1652/hour
- 15 GB RAM × $0.00698 = $0.1047/hour
Total: $0.27/hour = $194/month
```

**Storage Costs:**
- SSD: $0.17/GB/month
- Backups: $0.08/GB/month (beyond instance size)

**Network Costs:**
- Ingress: Free
- Egress (same region): Free
- Cross-region replication: $0.08-0.12/GB

### Right-Sizing Strategy

**Before:**
- db-n1-standard-16: 16 vCPU, 60 GB RAM = $784/month
- CPU utilization: 20%, Memory: 30%

**After:**
- db-n1-standard-4: 4 vCPU, 15 GB RAM = $194/month
- **Savings: $590/month (75%)**

**Implementation:**
```bash
# Monitor resource usage
gcloud monitoring time-series list \
  --filter='metric.type="cloudsql.googleapis.com/database/cpu/utilization"'

# Apply sizing recommendation
gcloud sql instances patch prod-db --tier=db-n1-standard-4
```

### Scheduled Scaling

**Pattern: Business hours only**
```bash
# Scale up (9 AM): db-n1-standard-8
# Scale down (6 PM): db-n1-standard-2

# Cost calculation:
# 9 hours × $388/month + 15 hours × $97/month = $165/month
# vs Always-on: $388/month
# Savings: $223/month (57%)
```

### Development Environment Optimization

**Anti-Pattern:**
- 10 developers × separate Cloud SQL instance = $1,940/month

**Optimized:**
- 1 shared instance with separate databases = $194/month
- **Savings: $1,746/month (90%)**

### Committed Use Discounts

**3-year CUD:**
- Standard: $194/month
- With CUD: $83/month (57% discount)
- **Savings: $111/month × 36 months = $3,996**

---

## Integration Architecture Patterns

### Cloud SQL + GKE (Kubernetes)

**Architecture with Cloud SQL Proxy:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  replicas: 3
  template:
    spec:
      serviceAccountName: cloudsql-sa
      containers:
      - name: app
        image: gcr.io/project/app
        env:
        - name: DB_HOST
          value: "127.0.0.1"
        - name: DB_USER
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: username
      - name: cloud-sql-proxy
        image: gcr.io/cloud-sql-connectors/cloud-sql-proxy:latest
        args:
        - "--private-ip"
        - "PROJECT:REGION:INSTANCE"
        resources:
          requests:
            memory: "64Mi"
            cpu: "50m"
```

**Best Practices:**
- ✅ Use Workload Identity (no service account keys)
- ✅ Private IP connections
- ✅ Connection pooling in application
- ✅ Separate secrets per environment

### Cloud SQL + Cloud Functions

**Serverless Connection Pattern:**
```python
from google.cloud.sql.connector import Connector
import sqlalchemy

connector = Connector()

def getconn():
    return connector.connect(
        "PROJECT:REGION:INSTANCE",
        "pg8000",
        user="postgres",
        db="mydb",
        enable_iam_auth=True
    )

pool = sqlalchemy.create_engine(
    "postgresql+pg8000://",
    creator=getconn,
    pool_size=5,
    max_overflow=2,
    pool_timeout=30,
)

def handler(request):
    with pool.connect() as conn:
        result = conn.execute("SELECT * FROM users")
        return str(result.fetchall())
```

### Cloud SQL + BigQuery Analytics

**Federated Query Pattern:**
```sql
-- Query Cloud SQL from BigQuery
SELECT 
  DATE(order_date) as date,
  COUNT(*) as orders,
  SUM(amount) as revenue
FROM 
  EXTERNAL_QUERY(
    "us-central1.cloudsql-connection",
    "SELECT order_date, amount FROM orders WHERE order_date >= CURRENT_DATE - 30"
  )
GROUP BY date
ORDER BY date;
```

**ETL Pipeline (Better for large-scale):**
```
Cloud SQL → Cloud Scheduler → Dataflow → BigQuery
(nightly export of aggregated data)
```

---

## Advanced Security Patterns

### Zero-Trust Architecture

**Layered Security:**
```
Layer 1: Network Isolation
├── Private IP only (VPC peering)
├── No public internet access
└── VPC Service Controls perimeter

Layer 2: Authentication
├── IAM database authentication
├── Cloud SQL Auth Proxy
└── Short-lived credentials

Layer 3: Encryption
├── CMEK (customer-managed keys)
├── SSL/TLS in transit
└── Application-layer encryption

Layer 4: Monitoring
├── Audit logs (all queries)
├── Cloud Monitoring alerts
└── Security Command Center
```

### Compliance Implementation

**HIPAA Requirements:**
```bash
# 1. Enable CMEK
gcloud kms keys create hipaa-key --location=us-central1 --keyring=healthcare

# 2. Create instance with CMEK
gcloud sql instances create patient-db \
  --tier=db-n1-standard-4 \
  --region=us-central1 \
  --availability-type=REGIONAL \
  --kms-key=projects/PROJECT/locations/us-central1/keyRings/healthcare/cryptoKeys/hipaa-key \
  --no-assign-ip \
  --network=projects/PROJECT/global/networks/default

# 3. Enable audit logs
gcloud logging sinks create hipaa-audit \
  storage.googleapis.com/hipaa-audit-logs \
  --log-filter='resource.type="cloudsql_database"'

# 4. Require SSL
gcloud sql instances patch patient-db \
  --database-flags=require_secure_transport=on
```

**PCI-DSS Implementation:**
- Private IP only (no public access)
- VPC Service Controls perimeter
- CMEK encryption with 90-day rotation
- Quarterly vulnerability scans
- Regular access reviews

---

## Monitoring and SLO Design

### Critical Metrics

**Database Health:**
```yaml
CPU Utilization:
  Metric: cloudsql.googleapis.com/database/cpu/utilization
  Alert: > 80% for 5 minutes
  Action: Scale up or optimize queries

Memory Usage:
  Metric: cloudsql.googleapis.com/database/memory/utilization
  Alert: > 85%
  Action: Increase memory tier

Connections:
  Metric: cloudsql.googleapis.com/database/network/connections
  Alert: > 80% of max_connections
  Action: Enable connection pooling

Disk Utilization:
  Metric: cloudsql.googleapis.com/database/disk/utilization
  Alert: > 85%
  Action: Increase storage
```

**Replication Health:**
```yaml
Replica Lag:
  Metric: cloudsql.googleapis.com/database/replication/replica_lag
  Alert: > 10 seconds
  Action: Check primary load

Replication Status:
  Metric: cloudsql.googleapis.com/database/replication/network_lag
  Alert: Any errors
  Action: Investigate connectivity
```

### SLI/SLO Definition

**Availability SLO:**
```yaml
SLI: Successful connection rate
Calculation: (successful_connects / total_attempts) × 100
Target: 99.95% (Regional HA)
Error Budget: 21.6 minutes/month
```

**Latency SLO:**
```yaml
SLI: p95 query latency
Target: < 100ms
Measurement: Query Insights
Action: Optimize slow queries
```

**Alerting Policy:**
```bash
gcloud alpha monitoring policies create \
  --notification-channels=email-channel \
  --display-name="Cloud SQL High CPU" \
  --condition-threshold-value=0.8 \
  --condition-threshold-duration=300s \
  --condition-filter='metric.type="cloudsql.googleapis.com/database/cpu/utilization"'
```

---

## Multi-Region and Global Patterns

### Active-Passive DR Pattern

**Architecture:**
```
Primary Region (us-central1)
├── Regional HA Instance (active)
│   ├── Primary (zone-a)
│   └── Standby (zone-b)
└── Applications (read/write)

DR Region (europe-west1)
├── Cross-Region Read Replica
│   └── Async replication (~5s lag)
└── Applications (scaled to 0)

Failover Process:
1. Detect primary failure
2. Promote replica: gcloud sql instances promote-replica dr-replica
3. Update DNS/connection strings
4. Scale up DR applications
RTO: 5-15 minutes, RPO: ~5 seconds
```

### Read-Heavy Global Pattern

**Architecture:**
```
                Global Load Balancer
                        |
        +---------------+---------------+
        |               |               |
   US Region       EU Region       ASIA Region
   (Primary)       (Replica)       (Replica)
   Read/Write      Read-Only       Read-Only
```

**Implementation:**
```bash
# Primary
gcloud sql instances create global-primary \
  --region=us-central1 \
  --tier=db-n1-standard-8 \
  --availability-type=REGIONAL

# EU Replica
gcloud sql instances create eu-replica \
  --master-instance-name=global-primary \
  --region=europe-west1 \
  --tier=db-n1-standard-4

# Asia Replica
gcloud sql instances create asia-replica \
  --master-instance-name=global-primary \
  --region=asia-southeast1 \
  --tier=db-n1-standard-4
```

### When to Use Cloud Spanner Instead

**Cloud Spanner is better when:**
- Need global write consistency (Cloud SQL = single-region writes)
- Need > 64 TB (Cloud SQL limit)
- Need < 10ms latency globally
- Budget allows (3-5x more expensive)

**Cloud SQL is better when:**
- Regional application (99% of cases)
- Budget-conscious
- Need MySQL/PostgreSQL compatibility
- Database size < 10 TB

---

## Performance Tuning Best Practices

### Connection Pooling Architecture

**Problem:** Each connection = ~256 KB memory

**Solution: PgBouncer (PostgreSQL)**
```
Application (1000 requests/sec)
    ↓
PgBouncer (10 connections to DB)
    ↓
Cloud SQL (low connection count)
```

**Configuration:**
```ini
[databases]
mydb = host=10.0.0.3 port=5432

[pgbouncer]
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 10
```

### Storage IOPS Optimization

**IOPS Formula:**
```
IOPS = 3 × Storage Size (GB)
Maximum: 60,000 IOPS

Examples:
100 GB = 300 IOPS
1 TB = 3,000 IOPS
20 TB+ = 60,000 IOPS (capped)
```

**When storage is bottleneck:**
```bash
# Increase storage to increase IOPS
gcloud sql instances patch prod-db --storage-size=2000GB
# Result: 2000 × 3 = 6,000 IOPS
```

### Query Optimization Workflow

**1. Enable Query Insights:**
```bash
gcloud sql instances patch prod-db \
  --insights-config-query-insights-enabled \
  --insights-config-query-string-length=1024
```

**2. Identify slow queries:**
- Top queries by total time
- Queries with high rows examined
- Lock wait times

**3. Optimize:**
```sql
-- Before: Full table scan (5 seconds)
SELECT * FROM orders WHERE customer_id = 123 AND status = 'pending';

-- Add compound index
CREATE INDEX idx_customer_status ON orders(customer_id, status);

-- After: Index scan (50ms)
```

---

## Migration Best Practices

### Database Migration Service (DMS) Workflow

**Phase 1: Planning**
- Assess source database compatibility
- Test connectivity (VPN/Interconnect)
- Calculate migration time (1 TB ≈ 4 hours)

**Phase 2: Setup**
```bash
# Create connection profiles
gcloud database-migration connection-profiles create mysql SOURCE_PROFILE \
  --host=SOURCE_IP --port=3306

gcloud database-migration connection-profiles create cloudsql DEST_PROFILE \
  --cloudsql-instance=PROJECT:REGION:INSTANCE

# Create migration job
gcloud database-migration migration-jobs create my-migration \
  --source=SOURCE_PROFILE \
  --destination=DEST_PROFILE \
  --type=CONTINUOUS
```

**Phase 3: Validation**
- Compare row counts
- Verify data integrity
- Test application connectivity
- Monitor replication lag

**Phase 4: Cutover**
```bash
# Stop writes to source
# Wait for lag = 0
gcloud database-migration migration-jobs promote my-migration
# Update application config
```

---

## PCA Exam Scenarios

### Scenario 1: "Minimize maintenance downtime"

**Answer:** Enterprise Plus edition (< 10s vs 30-60s standard)

### Scenario 2: "Global app, strong consistency"

**Answer:** Cloud Spanner (Cloud SQL is regional for writes)

### Scenario 3: "500 GB MySQL migration, < 5 min downtime"

**Answer:** Database Migration Service with continuous replication

### Scenario 4: "Reduce dev database costs"

**Answer:** 
- Smaller tier (db-n1-standard-1)
- Zonal (no HA)
- Scheduled scaling (stop at night)

### Scenario 5: "HIPAA compliance"

**Answer:**
- CMEK encryption
- Private IP only
- IAM authentication
- Audit logging
- BAA with Google

### Scenario 6: "CPU 90%, Memory 60%"

**Answer:** Scale up vCPUs (CPU is bottleneck)

### Scenario 7: "Replication lag > 30 seconds"

**Answer:**
- Check primary load (optimize queries)
- Check network connectivity
- Consider larger replica tier
- Check for long transactions

---

## Decision Framework

### Cloud SQL vs Alternatives

```
Question Flow:

1. Need managed database?
   No → Compute Engine + self-managed
   Yes → Continue

2. Need relational database?
   No → Firestore/Bigtable
   Yes → Continue

3. Need global writes?
   Yes → Cloud Spanner
   No → Continue

4. Need > 64 TB?
   Yes → Cloud Spanner or sharding
   No → Cloud SQL

5. Need < 10s maintenance windows?
   Yes → Enterprise Plus
   No → Enterprise

6. Need HA?
   Yes → Regional HA (99.95%)
   No → Zonal (99.5%)
```

### Key Trade-offs

| Decision | Option A | Option B | Choose When |
|----------|----------|----------|-------------|
| **Edition** | Enterprise | Enterprise Plus | Need < 10s maintenance |
| **Availability** | Zonal | Regional HA | Need 99.95% uptime |
| **DR** | Backups | Cross-region replica | RTO < 15 min required |
| **Network** | Public IP | Private IP | Security is priority |
| **Scaling** | Vertical | Cloud Spanner | Need > 64 TB |

---

## Production Checklist

### High Availability
- ✅ Regional HA enabled (99.95% SLA)
- ✅ Automated backups (30-day retention)
- ✅ Point-in-Time Recovery enabled
- ✅ Cross-region replica for DR
- ✅ Deny maintenance periods configured

### Security
- ✅ Private IP only (no public access)
- ✅ Cloud SQL Auth Proxy deployed
- ✅ IAM database authentication enabled
- ✅ CMEK for sensitive data
- ✅ SSL/TLS enforced
- ✅ Audit logging enabled

### Performance
- ✅ Right-sized instance tier
- ✅ Storage sized for IOPS needs
- ✅ Automatic storage increase enabled
- ✅ Connection pooling configured
- ✅ Query Insights enabled
- ✅ Read replicas for read-heavy workloads

### Monitoring
- ✅ CPU/Memory alerts configured
- ✅ Disk utilization alerts
- ✅ Connection count monitoring
- ✅ Replication lag alerts
- ✅ Backup success monitoring

### Cost Optimization
- ✅ Right-sized based on metrics
- ✅ Committed use discounts applied
- ✅ Backup retention optimized
- ✅ Dev environments scaled appropriately

---

**End of Cloud SQL PCA Guide**
