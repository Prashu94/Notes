# AlloyDB for PostgreSQL - Comprehensive Guide for ACE & PCA Certifications

## Table of Contents
- [Overview](#overview)
- [Key Concepts](#key-concepts)
- [Architecture](#architecture)
- [AlloyDB vs Cloud SQL](#alloydb-vs-cloud-sql)
- [High Availability & Disaster Recovery](#high-availability--disaster-recovery)
- [Performance Features](#performance-features)
- [AI/ML Integration](#aiml-integration)
- [Security](#security)
- [Migration Strategies](#migration-strategies)
- [Pricing & Cost Comparison](#pricing--cost-comparison)
- [Exam Focus Areas](#exam-focus-areas)
- [Practice Scenarios](#practice-scenarios)
- [CLI Examples](#cli-examples)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Overview

### What is AlloyDB?

**AlloyDB for PostgreSQL** is a fully managed, PostgreSQL-compatible database service designed for demanding enterprise workloads. It combines the best of Google's infrastructure with PostgreSQL compatibility.

> **Key Differentiator**: AlloyDB provides **4x faster transactional workloads** and **100x faster analytical queries** compared to standard PostgreSQL.

### Key Characteristics
- **PostgreSQL Compatible**: 100% compatible with PostgreSQL (versions 14, 15)
- **High Performance**: Purpose-built for OLTP and hybrid OLTP + OLAP workloads
- **Fully Managed**: Automated backups, patching, and maintenance
- **AI-Optimized**: Native support for vector embeddings and vector search
- **Enterprise-Grade**: 99.99% availability SLA, encryption, and audit logging
- **Scalable**: Separate compute and storage, read pool autoscaling

### When to Use AlloyDB

| Scenario | Use AlloyDB | Use Cloud SQL PostgreSQL |
|----------|-------------|-------------------------|
| **High-performance OLTP** | ✅ Yes | ❌ No |
| **Large databases (>10TB)** | ✅ Yes | ⚠️ Limited |
| **Analytical queries on OLTP data** | ✅ Yes | ❌ No |
| **AI/ML with vector search** | ✅ Yes | ❌ No |
| **Small-medium databases (<100GB)** | ⚠️ Overkill | ✅ Yes |
| **Cost-sensitive workloads** | ❌ No | ✅ Yes |
| **Simple PostgreSQL migration** | ✅ Yes | ✅ Yes |

---

## Key Concepts

### AlloyDB Architecture Components

```
┌─────────────────────────────────────────────────────────────────┐
│                      AlloyDB Cluster                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐     │
│  │               Primary Instance                         │     │
│  │  • Read-Write operations                               │     │
│  │  • Transaction processing                              │     │
│  │  • WAL (Write-Ahead Log) generation                    │     │
│  └────────────────────────────────────────────────────────┘     │
│                              │                                   │
│                              ├──> Replication                    │
│                              │                                   │
│  ┌────────────────────────────────────────────────────────┐     │
│  │               Read Pool (Optional)                     │     │
│  │  • Read-only replicas                                  │     │
│  │  • Analytical queries                                  │     │
│  │  • Autoscaling (2-20 replicas)                         │     │
│  │  • Query result caching                                │     │
│  └────────────────────────────────────────────────────────┘     │
│                              │                                   │
│                              ↓                                   │
│  ┌────────────────────────────────────────────────────────┐     │
│  │          Intelligent Storage Layer                     │     │
│  │  • Automatically expands                               │     │
│  │  • Transactionally consistent backups                  │     │
│  │  • Multi-region replication                            │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Instance Types

| Type | Purpose | Read-Write | Use Case |
|------|---------|------------|----------|
| **Primary** | Main instance | ✅ Yes | Transaction processing, writes |
| **Read Pool** | Read replicas | ❌ No (read-only) | Analytics, reporting, read scaling |

### Storage Architecture

**Separation of Compute and Storage**:
- **Compute**: Primary and read pool instances (CPU, RAM)
- **Storage**: Intelligent distributed storage layer
- **Benefit**: Scale compute and storage independently

```
Traditional DB:
┌──────────────────┐
│  Instance        │
│  ├─ Compute      │
│  └─ Storage      │  ← Tightly coupled
└──────────────────┘

AlloyDB:
┌──────────────────┐     ┌──────────────────┐
│  Primary         │     │  Storage Layer   │
│  Instance        │────▶│  (Shared)        │
│  (Compute)       │     │  - Distributed   │
└──────────────────┘     │  - Fault-tolerant│
                         │  - Auto-scaling  │
┌──────────────────┐     │                  │
│  Read Pool       │────▶│                  │
│  (Compute)       │     │                  │
└──────────────────┘     └──────────────────┘
```

---

## Architecture

### Cluster Configuration

```yaml
# AlloyDB Cluster Configuration Example
apiVersion: alloydb.cnrm.cloud.google.com/v1beta1
kind: AlloyDBCluster
metadata:
  name: production-cluster
spec:
  location: us-central1
  network: projects/my-project/global/networks/my-vpc
  
  # Primary instance configuration
  primaryConfig:
    nodeCount: 1  # Always 1 for primary
    machineConfig:
      cpuCount: 16
      memoryGb: 64
    databaseFlags:
      max_connections: "500"
      shared_buffers: "8GB"
  
  # Optional: Read pool configuration
  readPoolConfig:
    nodeCount: 4  # Initial replicas
    autoscaling:
      enabled: true
      minNodeCount: 2
      maxNodeCount: 20
    machineConfig:
      cpuCount: 8
      memoryGb: 32
  
  # Backup configuration
  continuousBackup:
    enabled: true
    retentionDays: 35
  
  # Encryption
  encryptionConfig:
    kmsKeyName: projects/my-project/locations/us-central1/keyRings/my-ring/cryptoKeys/my-key
```

### Network Architecture

**Private IP Only** (Required):
- AlloyDB instances do NOT have public IPs
- Access via Private Service Connect or VPC peering
- Requires VPC with allocated IP range

```
┌─────────────────────────────────────────────────────────────────┐
│                          VPC Network                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐        Private IP        ┌──────────────┐  │
│  │  Application    │───────────────────────────▶│  AlloyDB   │  │
│  │  (GKE/GCE)      │      10.0.0.0/8           │  Cluster   │  │
│  └─────────────────┘                           └──────────────┘  │
│                                                                  │
│  ┌─────────────────┐                                            │
│  │  Private        │                                            │
│  │  Service        │                                            │
│  │  Connect        │                                            │
│  └─────────────────┘                                            │
│         │                                                        │
└─────────┼────────────────────────────────────────────────────────┘
          │
          ↓
    ┌─────────────┐
    │  On-Premises│
    │  (via VPN)  │
    └─────────────┘
```

### High Availability Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│               AlloyDB HA Configuration                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Primary Zone (us-central1-a):                                  │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Primary Instance                                      │     │
│  │  • Active: Serving read-write traffic                 │     │
│  └────────────────────────────────────────────────────────┘     │
│                              │                                   │
│                              │ Synchronous Replication           │
│                              │                                   │
│  Secondary Zone (us-central1-b):                                │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Standby Instance (Hidden)                            │     │
│  │  • Passive: Ready for automatic failover              │     │
│  │  • RPO: < 1 second                                     │     │
│  │  • RTO: < 1 minute                                     │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  Storage Layer (Multi-zone):                                    │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  • Automatically replicated across zones               │     │
│  │  • Transactionally consistent backups                  │     │
│  │  • Point-in-time recovery (PITR)                       │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

SLA: 99.99% availability (4 nines)
```

---

## AlloyDB vs Cloud SQL

### Comparison Matrix

| Feature | AlloyDB | Cloud SQL PostgreSQL |
|---------|---------|---------------------|
| **Performance (OLTP)** | 4x faster | Baseline |
| **Analytical Queries** | 100x faster | Slow on large datasets |
| **Max Storage** | 64 TB+ | 64 TB |
| **Read Replicas** | Up to 20 (autoscaling) | Up to 10 (manual) |
| **Vector Search** | ✅ Native support | ❌ Extension only |
| **Pricing** | $$$$ | $$ |
| **Minimum Cost** | ~$730/month | ~$25/month |
| **Public IP** | ❌ No (Private only) | ✅ Yes (optional) |
| **Cross-Region Replicas** | ✅ Yes | ✅ Yes |
| **HA SLA** | 99.99% | 99.95% |
| **Backup Retention** | Up to 35 days | Up to 365 days |
| **AI/ML Integration** | ✅ Optimized | ⚠️ Limited |

### Performance Comparison

**Transactional Workload (OLTP)**:
```
Benchmark: pgbench (10M rows, 100 concurrent connections)

Cloud SQL PostgreSQL:     10,000 TPS
AlloyDB:                  40,000 TPS    (4x faster)
```

**Analytical Workload (OLAP)**:
```
Benchmark: Complex JOIN query across 100M rows

Cloud SQL PostgreSQL:     120 seconds
AlloyDB (Read Pool):      1.2 seconds   (100x faster)
```

### Cost Comparison Example

**Scenario**: Medium database (500 GB, 4 vCPUs, 16 GB RAM)

**Cloud SQL PostgreSQL (HA)**:
```
Instance cost:  $280/month  (db-custom-4-16384)
Storage:        $85/month   (500 GB SSD)
Backup:         $50/month   (500 GB backup)
Total:          ~$415/month
```

**AlloyDB**:
```
Primary (4 vCPU, 16GB):  $730/month  (base configuration)
Storage:                 $100/month  (500 GB)
Backups:                 Included
Total:                   ~$830/month  (2x cost for 4x-100x performance)
```

### Decision Tree: AlloyDB vs Cloud SQL

```
Start: Need PostgreSQL database
│
├─ Budget < $1000/month? 
│  └─ YES ──> Cloud SQL PostgreSQL
│
├─ Database < 100 GB?
│  └─ YES ──> Cloud SQL PostgreSQL
│
├─ Need high analytical query performance?
│  └─ YES ──> AlloyDB
│
├─ Need AI/ML vector search?
│  └─ YES ──> AlloyDB
│
├─ Database > 10 TB?
│  └─ YES ──> AlloyDB
│
├─ Mission-critical, need 99.99% SLA?
│  └─ YES ──> AlloyDB
│
└─ Default ──> Cloud SQL PostgreSQL (start here, migrate later)
```

---

## High Availability & Disaster Recovery

### Built-in HA Configuration

**Automatic Failover**:
- Hidden standby instance in different zone
- Automatic failover on primary failure
- Client connections seamlessly redirected
- RPO < 1 second, RTO < 1 minute

```bash
# Create HA cluster
gcloud alloydb clusters create prod-cluster \
    --region=us-central1 \
    --network=my-vpc \
    --availability-type=REGIONAL  # HA enabled

# HA is automatic, no additional configuration needed
```

### Cross-Region Disaster Recovery

```
Primary Region (us-central1):
┌────────────────────────────────────┐
│  AlloyDB Cluster (Primary)         │
│  • Active read-write                │
│  • Continuous backup                │
└────────────────────────────────────┘
         │
         │ Cross-region replication
         │
         ↓
Secondary Region (us-east1):
┌────────────────────────────────────┐
│  AlloyDB Cluster (Secondary)       │
│  • Created from backup              │
│  • Async replication                │
│  • Promoted on DR event             │
└────────────────────────────────────┘
```

**Cross-Region Setup**:
```bash
# 1. Enable continuous backup in primary
gcloud alloydb clusters update prod-cluster \
    --region=us-central1 \
    --enable-continuous-backup

# 2. Create secondary cluster from backup
gcloud alloydb clusters create dr-cluster \
    --region=us-east1 \
    --network=my-vpc-global \
    --source-cluster=projects/my-project/locations/us-central1/clusters/prod-cluster
```

### Backup & Recovery Options

#### 1. Continuous Backup (Recommended)
- Enabled by default
- Point-in-time recovery (PITR) to any second
- Retention: 1-35 days
- Automatic, no performance impact

```bash
# Enable continuous backup
gcloud alloydb clusters update prod-cluster \
    --region=us-central1 \
    --enable-continuous-backup \
    --continuous-backup-retention-days=35
```

#### 2. On-Demand Backups
- Manual backups
- Retention: Up to 365 days
- Useful for pre-upgrade snapshots

```bash
# Create on-demand backup
gcloud alloydb backups create my-backup \
    --region=us-central1 \
    --cluster=prod-cluster

# List backups
gcloud alloydb backups list --region=us-central1

# Restore from backup
gcloud alloydb clusters restore prod-cluster \
    --region=us-central1 \
    --backup=my-backup \
    --network=my-vpc
```

#### 3. Export to Cloud Storage
- Export data for long-term retention or analytics
- Use `pg_dump` or Cloud SQL Admin API

```bash
# Export database
gcloud alloydb operations wait \
  $(gcloud alloydb instances export sales-instance \
    --region=us-central1 \
    --database=sales_db \
    --uri=gs://my-bucket/exports/sales_db_$(date +%Y%m%d).sql \
    --format=json | jq -r '.name')
```

---

## Performance Features

### 1. Columnar Engine

**What it is**: AlloyDB automatically creates a columnar representation of your data for analytical queries.

**Benefits**:
- 100x faster analytical queries
- No ETL pipeline needed
- Real-time analytics on operational data
- Automatic maintenance

```sql
-- Same query runs on both row-store and column-store
-- AlloyDB automatically chooses optimal execution

-- Analytical query (uses columnar engine)
SELECT 
  region,
  product_category,
  SUM(revenue) as total_revenue,
  AVG(order_value) as avg_order
FROM sales
WHERE order_date >= '2025-01-01'
GROUP BY region, product_category
ORDER BY total_revenue DESC;

-- Result: 100x faster than row-based execution
```

**How it works**:
```
Write Operation:
User INSERT ──> Row Store (Primary) ──> Columnar Engine (Async)
                   │                          │
                   ↓                          ↓
              OLTP Queries              Analytical Queries

Unified View: Single SQL interface, optimal execution plan automatically chosen
```

### 2. Read Pool Autoscaling

**Configuration**:
```bash
# Create cluster with read pool
gcloud alloydb clusters create prod-cluster \
    --region=us-central1 \
    --read-pool-node-count=4 \
    --enable-read-pool-autoscaling \
    --min-read-pool-node-count=2 \
    --max-read-pool-node-count=20
```

**Scaling Behavior**:
- Scales based on CPU utilization and query queue length
- Scale-up: Within 1 minute
- Scale-down: Gradual (5+ minutes of low load)
- Each replica: Identical configuration to primary

**Use Cases**:
- Variable analytical workloads
- Reporting dashboards
- Read-heavy applications
- Cost optimization (scale down when idle)

### 3. Query Result Caching

**Automatic caching**:
- Results cached in read pool instances
- Cache hit = instant response (microseconds)
- Cache invalidation on data changes
- No configuration needed

```sql
-- First execution: 5 seconds
SELECT * FROM large_table WHERE category = 'electronics';

-- Subsequent executions: < 1ms (cached)
SELECT * FROM large_table WHERE category = 'electronics';

-- Cache invalidated after:
INSERT INTO large_table VALUES (...);  -- or UPDATE or DELETE
```

### 4. Database Connection Pooling

**Cloud SQL Auth Proxy with AlloyDB**:
```bash
# Run Cloud SQL Auth Proxy
./cloud-sql-proxy \
  --alloydb-instance=projects/my-project/locations/us-central1/clusters/my-cluster/instances/primary \
  --alloydb-read-pool \  # Load balance across read pool
  --max-connections=100

# Application connects to localhost:5432
```

**PgBouncer Integration**:
```ini
# pgbouncer.ini
[databases]
mydb = host=alloydb-private-ip port=5432 dbname=mydb

[pgbouncer]
pool_mode = transaction
max_client_conn = 10000
default_pool_size = 25
reserve_pool_size = 10
reserve_pool_timeout = 5
```

---

## AI/ML Integration

### Vector Embeddings Support

**AlloyDB + Vertex AI Integration**:
AlloyDB includes the `pgvector` extension with optimizations.

```sql
-- Enable vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create table with vector column
CREATE TABLE product_embeddings (
  product_id INT PRIMARY KEY,
  product_name TEXT,
  embedding vector(768)  -- 768-dimensional vector
);

-- Create vector index (HNSW algorithm)
CREATE INDEX ON product_embeddings 
USING hnsw (embedding vector_cosine_ops);

-- Insert embeddings (generated by Vertex AI)
INSERT INTO product_embeddings VALUES 
  (1, 'Laptop', '[0.1, 0.2, ..., 0.9]'::vector);

-- Semantic search query
SELECT 
  product_id,
  product_name,
  1 - (embedding <=> '[0.15, 0.25, ..., 0.85]'::vector) AS similarity
FROM product_embeddings
ORDER BY embedding <=> '[0.15, 0.25, ..., 0.85]'::vector
LIMIT 10;
```

### RAG (Retrieval Augmented Generation) Pattern

```
┌─────────────────────────────────────────────────────────────────┐
│                    RAG with AlloyDB                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  User Query ──> Vertex AI (Gemini)                              │
│                   │                                              │
│                   ├──> Generate Embedding                        │
│                   │                                              │
│                   ├──> AlloyDB Vector Search                     │
│                   │     (semantic similarity)                    │
│                   │                                              │
│                   ├──> Retrieve Relevant Documents               │
│                   │                                              │
│                   └──> Generate Response (with context)          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Implementation**:
```python
from google.cloud import aiplatform
from google.cloud.sql.connector import Connector
import sqlalchemy

# Initialize Vertex AI
aiplatform.init(project='my-project', location='us-central1')

# Generate embedding for query
from vertexai.language_models import TextEmbeddingModel
model = TextEmbeddingModel.from_pretrained("textembedding-gecko@003")
query = "best laptop for programming"
query_embedding = model.get_embeddings([query])[0].values

# Connect to AlloyDB
connector = Connector()

def getconn():
    return connector.connect(
        "my-project:us-central1:my-cluster:primary",
        "pg8000",
        user="postgres",
        password="secret",
        db="mydb"
    )

engine = sqlalchemy.create_engine(
    "postgresql+pg8000://",
    creator=getconn,
)

# Vector search
with engine.connect() as conn:
    result = conn.execute(
        sqlalchemy.text("""
            SELECT product_id, product_name, description
            FROM product_embeddings
            ORDER BY embedding <=> :query_embedding
            LIMIT 5
        """),
        {"query_embedding": str(query_embedding)}
    )
    
    products = result.fetchall()

# Use retrieved context with Gemini
from vertexai.generative_models import GenerativeModel
model = GenerativeModel("gemini-pro")
context = "\n".join([f"{p.product_name}: {p.description}" for p in products])
prompt = f"Based on these products:\n{context}\n\nRecommend the best laptop for programming."
response = model.generate_content(prompt)
print(response.text)
```

### BigQuery Integration

**Federated Queries**:
```sql
-- Query AlloyDB from BigQuery
SELECT 
  bq.customer_id,
  bq.total_orders,
  alloydb.customer_tier,
  alloydb.lifetime_value
FROM 
  `my-project.analytics.customer_metrics` bq
JOIN 
  EXTERNAL_QUERY(
    'projects/my-project/locations/us-central1/connections/alloydb-conn',
    'SELECT customer_id, customer_tier, lifetime_value FROM customers'
  ) alloydb
ON bq.customer_id = alloydb.customer_id
WHERE bq.total_orders > 10;
```

---

## Security

### Encryption

**At Rest** (Automatic):
- Default: Google-managed encryption keys
- Optional: Customer-Managed Encryption Keys (CMEK) via Cloud KMS

```bash
# Create cluster with CMEK
gcloud alloydb clusters create secure-cluster \
    --region=us-central1 \
    --network=my-vpc \
    --kms-key=projects/my-project/locations/us-central1/keyRings/my-ring/cryptoKeys/db-key
```

**In Transit** (Automatic):
- TLS 1.2+ for all client connections
- TLS certificate verification

```bash
# Connect with SSL verification
psql "host=alloydb-ip port=5432 dbname=mydb user=postgres sslmode=verify-ca sslrootcert=server-ca.pem"
```

### IAM Integration

**IAM Database Authentication**:
```bash
# Grant IAM role
gcloud projects add-iam-policy-binding my-project \
    --member="user:alice@example.com" \
    --role="roles/alloydb.client"

# Connect using IAM
gcloud alloydb instances connect primary \
    --cluster=my-cluster \
    --region=us-central1 \
    --database=mydb \
    --user=alice@example.com
```

**Service Account Access**:
```python
# Python client with service account
from google.cloud.sql.connector import Connector
import google.auth

credentials, project = google.auth.default()

connector = Connector()

def getconn():
    return connector.connect(
        "project:region:cluster:instance",
        "pg8000",
        user="service-account@project.iam",  # IAM user
        enable_iam_auth=True,  # Use IAM
        db="mydb"
    )
```

### Audit Logging

**Enable Cloud Audit Logs**:
```bash
# Log all data access
gcloud logging read "resource.type=alloydb.googleapis.com/Instance" \
    --limit 50 \
    --format json

# Monitor specific operations
gcloud logging read '
  resource.type="alloydb.googleapis.com/Instance"
  AND protoPayload.methodName="CreateCluster"
' --limit 10
```

**Audit Log Sink to BigQuery**:
```bash
# Export logs to BigQuery for analysis
gcloud logging sinks create alloydb-audit-sink \
    bigquery.googleapis.com/projects/my-project/datasets/audit_logs \
    --log-filter='resource.type="alloydb.googleapis.com/Instance"'
```

---

## Migration Strategies

### From Cloud SQL PostgreSQL to AlloyDB

**Migration Approaches**:

#### 1. Database Migration Service (DMS) - Recommended
```
Cloud SQL ──> DMS ──> AlloyDB
  (Source)    (Replication)  (Target)
  
Benefits:
- Minimal downtime
- Continuous replication
- Automatic schema conversion
- Rollback capability
```

**Steps**:
```bash
# 1. Create DMS connection profile (source)
gcloud database-migration connection-profiles create \
    cloudsql-source \
    --type=CLOUDSQL \
    --connection-profile-type=SOURCE \
    --cloudsql-instance=projects/my-project/instances/my-cloudsql

# 2. Create DMS connection profile (destination)
gcloud database-migration connection-profiles create \
    alloydb-dest \
    --type=ALLOYDB \
    --connection-profile-type=DESTINATION \
    --alloydb-cluster=projects/my-project/locations/us-central1/clusters/my-alloydb

# 3. Create migration job
gcloud database-migration migration-jobs create my-migration \
    --source=cloudsql-source \
    --destination=alloydb-dest \
    --type=CONTINUOUS

# 4. Start migration
gcloud database-migration migration-jobs start my-migration

# 5. Monitor progress
gcloud database-migration migration-jobs describe my-migration

# 6. Promote AlloyDB (cutover)
gcloud database-migration migration-jobs promote my-migration
```

#### 2. pg_dump and pg_restore (Small Databases)
```bash
# 1. Dump from Cloud SQL
gcloud sql export sql my-cloudsql-instance \
    gs://my-bucket/dump.sql \
    --database=mydb

# 2. Import to AlloyDB
gsutil cat gs://my-bucket/dump.sql | \
  psql "host=alloydb-ip dbname=mydb user=postgres"

# Or restore from pg_dump
pg_dump -h cloudsql-ip -U postgres mydb > dump.sql
psql -h alloydb-ip -U postgres mydb < dump.sql
```

### From On-Premises PostgreSQL

**Approach**: Database Migration Service
```bash
# 1. Set up VPN/Interconnect to GCP
# 2. Configure Cloud SQL Auth Proxy for on-prem database
./cloud-sql-proxy --address 0.0.0.0 --port 5432 --dir /cloudsql \
    --instances=my-project:us-central1:on-prem-proxy

# 3. Use DMS with on-prem source
gcloud database-migration connection-profiles create \
    onprem-source \
    --type=POSTGRESQL \
    --connection-profile-type=SOURCE \
    --postgresql-host=on-prem-ip \
    --postgresql-port=5432 \
    --postgresql-username=postgres \
    --postgresql-password-file=password.txt

# 4. Create and start migration (same as Cloud SQL steps)
```

### Migration Checklist

**Pre-Migration**:
- ✅ Test application compatibility with PostgreSQL 14/15
- ✅ Identify and resolve unsupported features (if any)
- ✅ Estimate storage requirements
- ✅ Plan downtime window (or zero-downtime with DMS)
- ✅ Set up AlloyDB cluster in same region as source
- ✅ Configure VPC connectivity

**During Migration**:
- ✅ Monitor replication lag (for DMS)
- ✅ Test read queries on AlloyDB
- ✅ Prepare rollback plan
- ✅ Update application connection strings

**Post-Migration**:
- ✅ Verify data integrity (row counts, checksums)
- ✅ Test application functionality
- ✅ Monitor performance metrics
- ✅ Update documentation
- ✅ Decommission source database (after validation period)

---

## Pricing & Cost Comparison

### AlloyDB Pricing Components (February 2026)

#### 1. Instance (Compute) Pricing
**Per vCPU per hour**:
- Primary instance: $0.114/vCPU/hour
- Read pool instance: $0.07/vCPU/hour (cheaper!)

**Per GB memory per hour**:
- Primary instance: $0.019/GB/hour
- Read pool instance: $0.012/GB/hour

**Example Primary Instance (4 vCPU, 16 GB)**:
```
Compute:  (4 × $0.114) + (16 × $0.019) = $0.456 + $0.304 = $0.76/hour
Monthly:  $0.76 × 730 hours = $554.80/month
```

#### 2. Storage Pricing
- **Active storage**: $0.20/GB/month
- **Backup storage**: $0.08/GB/month
- **No charge** for first backup equal to database size

**Example (500 GB database)**:
```
Active storage:  500 GB × $0.20 = $100/month
Backup storage:  500 GB × $0 (first backup free)
```

#### 3. Data Transfer
- **Ingress**: Free
- **Egress to same region**: Free
- **Egress to internet**: $0.12/GB (after 1 GB free)

### Sample Monthly Costs

**Small Production Cluster**:
```
Primary (4 vCPU, 16 GB):     $555/month
Storage (500 GB):            $100/month
Backups:                     $0 (included)
─────────────────────────────────────────
Total:                       ~$655/month
```

**Medium Production Cluster with Read Pool**:
```
Primary (8 vCPU, 32 GB):     $1,130/month
Read Pool 2 replicas:        $720/month
Storage (2 TB):              $400/month
Backups:                     $160/month (extra backups)
─────────────────────────────────────────
Total:                       ~$2,410/month
```

**Large Enterprise Cluster**:
```
Primary (32 vCPU, 128 GB):   $4,520/month
Read Pool (8 replicas):      $2,880/month
Storage (10 TB):             $2,000/month
Backups:                     $800/month
Cross-region replication:    +30%
─────────────────────────────────────────
Total:                       ~$13,260/month
```

### Cost Optimization Tips

**1. Right-size Instances**:
```bash
# Monitor CPU/memory utilization
gcloud monitoring time-series list \
    --filter='metric.type="alloydb.googleapis.com/database/cpu/utilization"' \
    --interval-start=$(date -u -d '7 days ago' +%Y-%m-%dT%H:%M:%SZ) \
    --interval-end=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# Resize if consistently <50% utilized
gcloud alloydb instances update primary \
    --cluster=my-cluster \
    --region=us-central1 \
    --cpu-count=4 \  # Down from 8
    --memory-gb=16   # Down from 32
```

**2. Use Read Pool Autoscaling**:
```bash
# Scale down read pool during off-hours
gcloud alloydb clusters update my-cluster \
    --region=us-central1 \
    --min-read-pool-node-count=1 \  # Was 2
    --max-read-pool-node-count=10   # Was 20
```

**3. Optimize Storage**:
```sql
-- Identify large tables
SELECT 
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 20;

-- Archive old data to Cloud Storage
COPY (SELECT * FROM orders WHERE order_date < '2023-01-01') 
TO PROGRAM 'gsutil cp - gs://my-bucket/archive/orders_2022.csv.gz | gzip' 
WITH CSV HEADER;

DELETE FROM orders WHERE order_date < '2023-01-01';
VACUUM FULL orders;
```

**4. Cleanup Old Backups**:
```bash
# List backups
gcloud alloydb backups list --region=us-central1

# Delete old manual backups
gcloud alloydb backups delete old-backup --region=us-central1
```

---

## Exam Focus Areas

### For Associate Cloud Engineer (ACE)

**Exam Weight**: Low-Medium (emerging topic)

**Key Learning Points**:
1. **What AlloyDB is**:
   - PostgreSQL-compatible managed database
   - High-performance for OLTP and analytics
   - More expensive than Cloud SQL

2. **When to use AlloyDB vs Cloud SQL**:
   - AlloyDB: High-performance, large databases, AI/ML
   - Cloud SQL: Cost-sensitive, smaller databases

3. **Basic Operations**:
   - Creating clusters and instances
   - Connecting to AlloyDB (private IP only)
   - Backup and restore basics

**Sample ACE Question**:
```
Q: Your company has a 5 TB PostgreSQL database with heavy analytical queries 
that are slowing down operations. The database needs 99.99% availability. 
Which solution should you recommend?

A) Migrate to Cloud SQL PostgreSQL with read replicas
B) Migrate to AlloyDB with read pool
C) Keep current PostgreSQL and add BigQuery for analytics
D) Migrate to Cloud Spanner

Answer: B - Migrate to AlloyDB with read pool
Explanation:
- Large database (5 TB) = AlloyDB better suited
- Analytical queries = Read pool provides 100x faster analytics
- 99.99% SLA = AlloyDB provides this, Cloud SQL is 99.95%
- Option A: Cloud SQL read replicas wouldn't provide same performance
- Option C: Requires ETL pipeline (more complexity)
- Option D: Spanner for horizontal scaling, not analytics performance
```

### For Professional Cloud Architect (PCA)

**Exam Weight**: Medium-High

**Key Learning Points**:
1. **Architecture Decisions**:
   - AlloyDB vs Cloud SQL vs Spanner decision tree
   - Cost-benefit analysis
   - Performance vs cost trade-offs
   - When to use read pools
   - AI/ML integration patterns

2. **Design Patterns**:
   - Hybrid OLTP + OLAP architectures
   - RAG (Retrieval Augmented Generation) with vector search
   - Multi-region DR strategies
   - Migration patterns from on-prem/Cloud SQL

3. **Case Study Integration**:
   - EHR Healthcare: Patient records with analytics, vector search for similar cases
   - Cymbal Retail: Product catalog with recommendation engine
   - TerramEarth: Equipment telemetry data with real-time analytics

4. **Well-Architected Framework**:
   - **Performance**: Columnar engine, read pools
   - **Reliability**: 99.99% SLA, automated backups
   - **Security**: CMEK, private IP, IAM integration
   - **Cost Optimization**: Right-sizing, autoscaling read pools
   - **Operational Excellence**: Managed service, automated maintenance

**Sample PCA Question**:
```
Q: A financial services company needs to:
- Store 20 TB of transactional data with millisecond latency
- Run complex analytical queries for fraud detection in real-time
- Maintain audit trails for 7 years
- Ensure data never leaves eu-west1 region
- Minimize operational overhead

Which database solution and architecture should you recommend?

A) Cloud SQL PostgreSQL (HA) with BigQuery export for analytics
B) AlloyDB with read pool and long-term backup export to Cloud Storage
C) Cloud Spanner with BigQuery federation
D) Cloud SQL PostgreSQL with read replicas in multiple zones

Answer: B - AlloyDB with read pool
Explanation:
- Large database (20 TB) = AlloyDB optimal
- Real-time analytics = Read pool with columnar engine
- Regional constraint = AlloyDB deployed in eu-west1 only
- Audit trails = Export old backups to regional Cloud Storage bucket
- Low ops overhead = Fully managed AlloyDB

Option A: BigQuery export adds latency (not real-time)
Option C: Spanner = higher cost, overkill for regional requirement
Option D: Cloud SQL read replicas won't provide same analytical performance
```

---

## Practice Scenarios

### Scenario 1: E-commerce Platform

**Requirements**:
- 10 TB product catalog and order history
- 50,000 transactions per second (peak)
- Real-time inventory analytics
- Product recommendations using vector search
- 99.99% availability

**Solution**:
```bash
# Create AlloyDB cluster
gcloud alloydb clusters create ecommerce-cluster \
    --region=us-central1 \
    --network=projects/my-project/global/networks/prod-vpc \
    --availability-type=REGIONAL

# Primary instance (high CPU for transactions)
gcloud alloydb instances create primary \
    --cluster=ecommerce-cluster \
    --region=us-central1 \
    --instance-type=PRIMARY \
    --cpu-count=32 \
    --memory-size=128GB \
    --database-flags=max_connections=5000

# Read pool for analytics and recommendations
gcloud alloydb clusters update ecommerce-cluster \
    --region=us-central1 \
    --read-pool-node-count=8 \
    --enable-read-pool-autoscaling \
    --max-read-pool-node-count=20 \
    --read-pool-cpu-count=16 \
    --read-pool-memory-size=64GB
```

**Database Schema**:
```sql
-- Products with vector embeddings
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    description TEXT,
    price DECIMAL(10,2),
    inventory_count INT,
    embedding vector(768)  -- For recommendations
);

CREATE INDEX ON products USING hnsw (embedding vector_cosine_ops);

-- Orders (high write volume)
CREATE TABLE orders (
    order_id BIGSERIAL PRIMARY KEY,
    customer_id INT,
    product_id INT,
    quantity INT,
    order_date TIMESTAMP DEFAULT NOW(),
    status VARCHAR(50)
) PARTITION BY RANGE (order_date);

-- Analytics view (uses columnar engine)
CREATE MATERIALIZED VIEW product_analytics AS
SELECT 
    product_id,
    COUNT(*) as order_count,
    SUM(quantity) as units_sold,
    AVG(quantity) as avg_quantity
FROM orders
WHERE order_date >= NOW() - INTERVAL '30 days'
GROUP BY product_id;
```

### Scenario 2: Healthcare Records System

**Requirements**:
- HIPAA compliant
- 5 TB patient records
- AI-powered diagnostic suggestions (vector search)
- Read-heavy (analytics and research)
- Data residency in us-east4

**Solution**:
```bash
# Create HIPAA-compliant cluster with CMEK
gcloud kms keyrings create healthcare-keyring \
    --location=us-east4

gcloud kms keys create healthcare-db-key \
    --location=us-east4 \
    --keyring=healthcare-keyring \
    --purpose=encryption

gcloud alloydb clusters create healthcare-cluster \
    --region=us-east4 \
    --network=projects/my-project/global/networks/healthcare-vpc \
    --availability-type=REGIONAL \
    --kms-key=projects/my-project/locations/us-east4/keyRings/healthcare-keyring/cryptoKeys/healthcare-db-key

# Enable audit logs
gcloud logging sinks create healthcare-audit \
    bigquery.googleapis.com/projects/my-project/datasets/healthcare_audit \
    --log-filter='resource.type="alloydb.googleapis.com/Instance" AND resource.labels.cluster_id="healthcare-cluster"'
```

### Scenario 3: Migration from Cloud SQL

**Current State**:
- Cloud SQL PostgreSQL (db-highmem-16): 2 TB database
- 200 concurrent connections
- Slow analytical queries (30+ seconds)

**Migration Plan**:
```bash
# 1. Create AlloyDB cluster
gcloud alloydb clusters create migrated-cluster \
    --region=us-central1 \
    --network=default

# 2. Set up Database Migration Service
gcloud database-migration connection-profiles create cloudsql-source \
    --type=CLOUDSQL \
    --connection-profile-type=SOURCE \
    --cloudsql-instance=projects/my-project/instances/old-cloudsql

gcloud database-migration connection-profiles create alloydb-dest \
    --type=ALLOYDB \
    --connection-profile-type=DESTINATION \
    --alloydb-cluster=projects/my-project/locations/us-central1/clusters/migrated-cluster

# 3. Create and start migration
gcloud database-migration migration-jobs create migration-job \
    --source=cloudsql-source \
    --destination=alloydb-dest \
    --type=CONTINUOUS \
    --region=us-central1

gcloud database-migration migration-jobs start migration-job

# 4. Wait for full replication
# Monitor: gcloud database-migration migration-jobs describe migration-job

# 5. Update application connection strings (test in dev first)
# Old: host=cloudsql-ip
# New: host=alloydb-private-ip

# 6. Promote AlloyDB (cutover during low-traffic window)
gcloud database-migration migration-jobs promote migration-job
```

---

## CLI Examples

### Cluster Management

```bash
# Create cluster
gcloud alloydb clusters create my-cluster \
    --region=us-central1 \
    --network=projects/my-project/global/networks/my-vpc \
    --availability-type=REGIONAL \
    --async

# List clusters
gcloud alloydb clusters list --region=us-central1

# Describe cluster
gcloud alloydb clusters describe my-cluster --region=us-central1

# Update cluster (enable continuous backup)
gcloud alloydb clusters update my-cluster \
    --region=us-central1 \
    --enable-continuous-backup \
    --continuous-backup-retention-days=35

# Delete cluster
gcloud alloydb clusters delete my-cluster --region=us-central1
```

### Instance Management

```bash
# Create primary instance
gcloud alloydb instances create primary \
    --cluster=my-cluster \
    --region=us-central1 \
    --instance-type=PRIMARY \
    --cpu-count=4 \
    --memory-size=16GB \
    --database-flags=max_connections=500,shared_buffers='2GB'

# Create read pool instances
gcloud alloydb clusters update my-cluster \
    --region=us-central1 \
    --read-pool-node-count=2 \
    --read-pool-cpu-count=4 \
    --read-pool-memory-size=16GB

# Update instance
gcloud alloydb instances update primary \
    --cluster=my-cluster \
    --region=us-central1 \
    --cpu-count=8 \
    --memory-size=32GB

# Restart instance
gcloud alloydb instances restart primary \
    --cluster=my-cluster \
    --region=us-central1
```

### Backup Operations

```bash
# Create backup
gcloud alloydb backups create my-backup \
    --region=us-central1 \
    --cluster=my-cluster

# List backups
gcloud alloydb backups list --region=us-central1

# Restore from backup
gcloud alloydb clusters restore restored-cluster \
    --region=us-central1 \
    --backup=my-backup \
    --network=projects/my-project/global/networks/my-vpc

# Delete backup
gcloud alloydb backups delete my-backup --region=us-central1
```

### Connection

```bash
# Connect to primary via Cloud SQL Auth Proxy
gcloud alloydb instances connect primary \
    --cluster=my-cluster \
    --region=us-central1 \
    --database=postgres

# Get connection details
gcloud alloydb instances describe primary \
    --cluster=my-cluster \
    --region=us-central1 \
    --format="get(ipAddress)"
```

---

## Best Practices

### 1. Instance Sizing

**Start conservatively, scale up**:
- Begin with smallest instance that meets requirements
- Monitor CPU/memory utilization for 1-2 weeks
- Resize based on actual usage patterns

**Guidelines**:
- **CPU**: Target 50-70% average utilization
- **Memory**: Allocate 25% of database size (minimum 16 GB)
- **Connections**: Max connections = (Memory GB × 25)

### 2. Read Pool Configuration

**When to use read pools**:
- ✅ Reporting and analytics queries
- ✅ Dashboard data feeds
- ✅ Read-heavy microservices
- ❌ Real-time transactional writes

**Application routing**:
```python
# Route reads to read pool, writes to primary
import psycopg2

# Primary connection (writes)
primary_conn = psycopg2.connect(
    host="10.0.0.5",  # Primary IP
    database="mydb",
    user="postgres",
    password="secret"
)

# Read pool connection (reads)
read_conn = psycopg2.connect(
    host="10.0.0.6",  # Read pool IP
    database="mydb",
    user="postgres",
    password="secret"
)

# Use primary for writes
with primary_conn.cursor() as cur:
    cur.execute("INSERT INTO orders VALUES (...)")
    primary_conn.commit()

# Use read pool for analytics
with read_conn.cursor() as cur:
    cur.execute("SELECT COUNT(*) FROM orders WHERE ...")
    result = cur.fetchone()
```

### 3. Backup Strategy

**Recommended configuration**:
```bash
# Continuous backup (PITR) - ESSENTIAL
--enable-continuous-backup
--continuous-backup-retention-days=35  # Max retention

# Automated on-demand backups (weekly)
# Use Cloud Scheduler + Cloud Functions to create weekly snapshots
```

**Backup retention**:
- Operational recovery: 7-14 days (continuous backup)
- Compliance: Export to Cloud Storage for long-term retention

### 4. Security Hardening

```bash
# 1. Private IP only (default, good!)
# 2. CMEK for encryption
# 3. IAM database authentication
# 4. Network policies

# Create secure cluster
gcloud alloydb clusters create secure-cluster \
    --region=us-central1 \
    --network=projects/my-project/global/networks/private-vpc \
    --kms-key=projects/my-project/locations/us-central1/keyRings/my-ring/cryptoKeys/db-key \
    --enable-private-service-connect

# Configure firewall (VPC level)
gcloud compute firewall-rules create allow-alloydb-from-app \
    --network=private-vpc \
    --allow=tcp:5432 \
    --source-tags=app-servers \
    --target-tags=alloydb-instances \
    --description="Allow app servers to connect to AlloyDB"
```

### 5. Monitoring & Alerting

```bash
# Key metrics to monitor
- CPU utilization (target: 50-70%)
- Memory utilization (alert > 85%)
- Replication lag (alert > 1 second)
- Connection count (alert > 80% of max)
- Disk write latency (alert > 10ms)
- Backup success rate (alert < 100%)

# Create alert policy
gcloud alpha monitoring policies create \
    --notification-channels=CHANNEL_ID \
    --display-name="AlloyDB CPU High" \
    --condition-display-name="CPU > 80%" \
    --condition-threshold-value=0.8 \
    --condition-threshold-duration=300s \
    --condition-filter='
        resource.type="alloydb.googleapis.com/Instance"
        AND metric.type="alloydb.googleapis.com/database/cpu/utilization"
    '
```

---

## Troubleshooting

### Connection Issues

**Problem**: Cannot connect to AlloyDB instance

**Diagnosis**:
```bash
# 1. Check instance status
gcloud alloydb instances describe primary \
    --cluster=my-cluster \
    --region=us-central1

# 2. Verify network connectivity
gcloud compute networks describe my-vpc

# 3. Check firewall rules
gcloud compute firewall-rules list \
    --filter="network:my-vpc"

# 4. Test from GCE instance in same VPC
gcloud compute ssh test-vm -- \
    psql -h alloydb-ip -U postgres -d mydb
```

**Solutions**:
- Ensure VPC is correctly configured
- Verify Private Service Connect is enabled
- Check IAM permissions (roles/alloydb.client)
- Use Cloud SQL Auth Proxy for secure connections

### Performance Issues

**Problem**: Slow query performance

**Diagnosis**:
```sql
-- Check active queries
SELECT 
    pid,
    now() - query_start AS duration,
    state,
    query
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY duration DESC;

-- Identify long-running transactions
SELECT 
    pid,
    now() - xact_start AS transaction_duration,
    state,
    query
FROM pg_stat_activity
WHERE xact_start IS NOT NULL
ORDER BY transaction_duration DESC;

-- Check for missing indexes
SELECT 
    schemaname,
    tablename,
    idx_scan,
    seq_scan,
    seq_scan / NULLIF(idx_scan, 0) AS seq_idx_ratio
FROM pg_stat_user_tables
WHERE seq_scan > 1000
  AND idx_scan > 0  
ORDER BY seq_scan / NULLIF(idx_scan, 0) DESC;
```

**Solutions**:
- Add indexes for frequently filtered columns
- Use EXPLAIN ANALYZE to optimize queries
- Consider read pool for analytical queries
- Increase instance size if CPU/memory constrained

### Replication Lag

**Problem**: Read pool lag behind primary

**Diagnosis**:
```bash
# Check replication lag
gcloud monitoring time-series list \
    --filter='metric.type="alloydb.googleapis.com/database/replication/replica_lag"' \
    --interval-start=$(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ) \
    --interval-end=$(date -u +%Y-%m-%dT%H:%M:%SZ)
```

**Solutions**:
- If consistently high: Increase read pool instance size
- Check for long-running transactions on primary
- Consider write batching to reduce replication overhead

---

## Summary

### Key Takeaways

**For ACE Exam**:
- Know what AlloyDB is and basic differences from Cloud SQL
- Understand when to choose AlloyDB (performance, scale, AI/ML)
- Be familiar with creating clusters and instances
- Know that AlloyDB uses private IP only

**For PCA Exam**:
- Master AlloyDB vs Cloud SQL vs Spanner decision criteria
- Understand performance benefits (4x OLTP, 100x analytics)
- Know AI/ML integration patterns (vector search, Vertex AI)
- Understand cost implications and optimization strategies
- Apply Well-Architected Framework to AlloyDB solutions
- Migration strategies and considerations

**Critical Distinctions**:
| Feature | AlloyDB | Cloud SQL PostgreSQL | Cloud Spanner |
|---------|---------|---------------------|---------------|
| **Use Case** | High-perf OLTP + Analytics | General PostgreSQL | Global, horizontally scalable |
| **Performance** | 4x-100x faster | Baseline | Scalable but complex |
| **Cost** | $$$ (High) | $ (Low) | $$$$ (Very High) |
| **Max Size** | 64 TB+ | 64 TB | Unlimited |
| **HA SLA** | 99.99% | 99.95% | 99.999% |

### Next Steps

1. **Hands-on Practice**:
   - Create an AlloyDB cluster in your project
   - Migrate a small database from Cloud SQL
   - Test vector search with sample embeddings
   - Benchmark query performance

2. **Study Resources**:
   - [AlloyDB Documentation](https://cloud.google.com/alloydb/docs)
   - [Migration Guide](https://cloud.google.com/alloydb/docs/migration-overview)
   - [Best Practices](https://cloud.google.com/alloydb/docs/best-practices)

3. **Practice Scenarios**:
   - Design database architecture for case studies
   - Compare costs: AlloyDB vs alternatives
   - Plan migration strategies
   - Configure HA and DR

---

*Last Updated: February 7, 2026*  
*Aligned with: GCP ACE & PCA 2025/2026 Exam Blueprints*
