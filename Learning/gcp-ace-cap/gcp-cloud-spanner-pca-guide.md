# Google Cloud Spanner - Professional Cloud Architect (PCA) Comprehensive Guide

## Table of Contents
1. [Architectural Overview](#architectural-overview)
2. [Design Decisions & Trade-offs](#design-decisions--trade-offs)
3. [Advanced Schema Design](#advanced-schema-design)
4. [Performance Optimization](#performance-optimization)
5. [High Availability & Disaster Recovery](#high-availability--disaster-recovery)
6. [Cost Optimization](#cost-optimization)
7. [Security Architecture](#security-architecture)
8. [Migration Strategies](#migration-strategies)
9. [Multi-Tenancy Patterns](#multi-tenancy-patterns)
10. [Enterprise Integration Patterns](#enterprise-integration-patterns)
11. [PCA Exam Tips](#pca-exam-tips)

---

## Architectural Overview

Cloud Spanner is a globally distributed, strongly consistent, horizontally scalable relational database built on Google's TrueTime technology. For the Professional Cloud Architect exam, you must design Spanner architectures that balance consistency, availability, performance, and cost while meeting complex business requirements.

### TrueTime Architecture

**TrueTime** provides global time synchronization with bounded uncertainty:
- Time API returns interval: `[earliest, latest]`
- Typical uncertainty: 1-7 milliseconds
- Enables **external consistency** (transactions ordered globally)
- Foundation for Spanner's strong consistency guarantees

**How it Works:**
```
Transaction T1 commits at time t1
Transaction T2 starts at time t2 > t1
→ T2 always sees T1's writes (external consistency)
```

### Distributed Architecture

```
Global Deployment
├── Region A (Read-Write Replica)
│   ├── Zone A1 (Split 1, Split 2, ...)
│   ├── Zone A2 (Split 1, Split 2, ...)
│   └── Zone A3 (Split 1, Split 2, ...)
├── Region B (Read-Write Replica)
│   └── Zones (3x with splits)
└── Region C (Read-Only/Witness Replica)
    └── Zones (3x with splits)
```

**Paxos Replication:**
- Each split replicated across zones using Paxos
- Write requires majority (quorum) acknowledgment
- Read-write replicas participate in writes
- Witness replicas only vote (no data storage)
- Read-only replicas serve stale-read requests

---

## Design Decisions & Trade-offs

### Regional vs Multi-Region

| Aspect | Regional | Multi-Region |
|--------|----------|--------------|
| **Availability** | 99.99% (3 zones in 1 region) | 99.999% (3+ regions) |
| **Latency** | <5ms within region | <10ms within continent, 50-300ms cross-continent |
| **Cost** | Baseline | 3x regional for storage, 1x for compute |
| **Replication** | 3 replicas within region | 3+ replicas across regions |
| **Use Case** | Regional apps, cost-sensitive | Global apps, highest availability |

**Architecture Decision Matrix:**
```
Regional: 
- Single-region user base
- Latency-critical (<5ms)
- Budget constraints
- 99.99% acceptable

Dual-Region:
- Two primary regions
- Regional redundancy
- Balance cost/availability
- Synchronous replication within continent

Multi-Region:
- Global user base
- Highest availability (99.999%)
- Multi-continent presence
- Business-critical workloads
```

### Consistency vs Latency Trade-offs

**Strong Reads (Default):**
- Latest committed data
- Higher latency (cross-region coordination)
- Use for: Financial transactions, inventory management

**Stale Reads (Bounded Staleness):**
```sql
-- Read data up to 15 seconds old
SELECT * FROM Users
WHERE UserId = @userId
OPTIONS (max_staleness = '15s');
```
- Lower latency (local replica)
- Slightly stale data
- Use for: Reporting, analytics, non-critical reads

**Exact Staleness:**
```sql
-- Read data exactly 10 seconds old
SELECT * FROM Users
WHERE UserId = @userId
OPTIONS (exact_staleness = '10s');
```

### Spanner vs Other Google Databases

| Database | Consistency | Scalability | Latency | Cost | Use Case |
|----------|-------------|-------------|---------|------|----------|
| **Spanner** | Strong | Horizontal (petabytes) | 5-300ms | High | Global, mission-critical RDBMS |
| **Cloud SQL** | Strong | Vertical (64 TB) | 1-10ms | Medium | Regional RDBMS, <10TB |
| **Firestore** | Strong (eventual) | Horizontal | 1-100ms | Low | Document NoSQL, mobile/web |
| **Bigtable** | Eventual | Horizontal (petabytes) | <10ms | Medium | High-throughput NoSQL, analytics |
| **AlloyDB** | Strong | Vertical (64 TB) | <5ms | High | PostgreSQL-compatible, analytical |

---

## Advanced Schema Design

### Hotspot Prevention Strategies

**Problem: Monotonic Keys**
```sql
-- ❌ BAD: Creates hotspot (all writes go to same split)
CREATE TABLE UserEvents (
    EventTime TIMESTAMP NOT NULL,
    UserId INT64,
    EventType STRING(50)
) PRIMARY KEY (EventTime, UserId);
```

**Solution 1: UUID Primary Key**
```sql
-- ✅ GOOD: Random UUIDs distribute writes
CREATE TABLE UserEvents (
    EventId STRING(36) NOT NULL DEFAULT (GENERATE_UUID()),
    EventTime TIMESTAMP NOT NULL,
    UserId INT64,
    EventType STRING(50)
) PRIMARY KEY (EventId);

-- Secondary index for time-based queries
CREATE INDEX EventsByTime ON UserEvents(EventTime);
```

**Solution 2: Swap Key Order**
```sql
-- ✅ GOOD: UserId first distributes writes across users
CREATE TABLE UserEvents (
    UserId INT64 NOT NULL,
    EventTime TIMESTAMP NOT NULL,
    EventType STRING(50)
) PRIMARY KEY (UserId, EventTime);
```

**Solution 3: Bit-Reversed Sequences**
```sql
-- ✅ GOOD: Bit-reversed sequences avoid hotspots
CREATE SEQUENCE user_seq OPTIONS (
    sequence_kind="bit_reversed_positive"
);

CREATE TABLE Users (
    UserId INT64 DEFAULT (GET_NEXT_SEQUENCE_VALUE(SEQUENCE user_seq)),
    Name STRING(100),
    Email STRING(255)
) PRIMARY KEY (UserId);
```

**Solution 4: Hash-Based Sharding**
```sql
-- ✅ GOOD: Hash-based logical sharding
CREATE TABLE UserEvents (
    ShardId INT64 NOT NULL AS (MOD(FARM_FINGERPRINT(CAST(EventTime AS STRING)), 100)) STORED,
    EventTime TIMESTAMP NOT NULL,
    UserId INT64,
    EventType STRING(50)
) PRIMARY KEY (ShardId, EventTime, UserId);
```

### Interleaving for Performance

**Parent-Child Co-location:**
```sql
-- Parent: Albums
CREATE TABLE Albums (
    SingerId INT64 NOT NULL,
    AlbumId INT64 NOT NULL,
    AlbumTitle STRING(100),
    ReleaseDate DATE
) PRIMARY KEY (SingerId, AlbumId);

-- Child: Songs (interleaved under Albums)
CREATE TABLE Songs (
    SingerId INT64 NOT NULL,
    AlbumId INT64 NOT NULL,
    SongId INT64 NOT NULL,
    SongTitle STRING(100),
    Duration INT64,
    TrackNumber INT64
) PRIMARY KEY (SingerId, AlbumId, SongId),
  INTERLEAVE IN PARENT Albums ON DELETE CASCADE;

-- Grandchild: SongMetadata (interleaved under Songs)
CREATE TABLE SongMetadata (
    SingerId INT64 NOT NULL,
    AlbumId INT64 NOT NULL,
    SongId INT64 NOT NULL,
    MetadataType STRING(50) NOT NULL,
    MetadataValue STRING(1000)
) PRIMARY KEY (SingerId, AlbumId, SongId, MetadataType),
  INTERLEAVE IN PARENT Songs ON DELETE CASCADE;
```

**Benefits:**
- **Co-location:** Parent and child rows stored together (same split)
- **Performance:** Single read for parent + children
- **Cascading Deletes:** Automatic cleanup
- **Consistency:** Atomic operations across hierarchy

**When to Interleave:**
- Frequently read parent + children together
- 1-to-many relationships with bounded children
- Delete parent should delete children
- Strong consistency required

**When NOT to Interleave:**
- Many-to-many relationships
- Children queried independently of parent
- Unbounded children (could exceed split size)

### Index Design Strategies

**Covering Indexes:**
```sql
-- Index includes all columns needed for query (no table lookup)
CREATE INDEX UsersByEmailWithName ON Users(Email) STORING (Name, CreatedAt);

-- Query uses index only (no table access)
SELECT Name, CreatedAt FROM Users WHERE Email = 'alice@example.com';
```

**Interleaved Indexes:**
```sql
-- Non-interleaved index (separate table, can create hotspots)
CREATE INDEX SongsByDuration ON Songs(Duration);

-- Interleaved index (stored with parent, better performance)
CREATE INDEX SongsByDuration ON Songs(SingerId, AlbumId, Duration),
    INTERLEAVE IN Albums;
```

**Partial Indexes (NULL-Filtered):**
```sql
-- Index only non-NULL values
CREATE NULL_FILTERED INDEX ActiveUsersByEmail ON Users(Email);
```

**Composite Indexes:**
```sql
-- Multi-column index for complex queries
CREATE INDEX UsersByCountryAndCity ON Users(Country, City, LastLogin DESC);

-- Efficient query
SELECT * FROM Users 
WHERE Country = 'US' AND City = 'New York' 
ORDER BY LastLogin DESC 
LIMIT 100;
```

### Generated Columns

```sql
CREATE TABLE Products (
    ProductId INT64 NOT NULL,
    Name STRING(255),
    Price NUMERIC,
    Discount NUMERIC,
    -- Generated column (computed automatically)
    FinalPrice NUMERIC AS (Price * (1 - Discount)) STORED
) PRIMARY KEY (ProductId);

-- Index on generated column
CREATE INDEX ProductsByFinalPrice ON Products(FinalPrice);
```

### Foreign Keys

```sql
-- Parent table
CREATE TABLE Singers (
    SingerId INT64 NOT NULL,
    Name STRING(100)
) PRIMARY KEY (SingerId);

-- Child table with foreign key
CREATE TABLE Albums (
    AlbumId INT64 NOT NULL,
    SingerId INT64 NOT NULL,
    Title STRING(255),
    CONSTRAINT FK_Albums_Singers FOREIGN KEY (SingerId) 
        REFERENCES Singers(SingerId)
) PRIMARY KEY (AlbumId);
```

**Trade-offs:**
- **Pros:** Data integrity, referential consistency
- **Cons:** Performance overhead, write amplification

---

## Performance Optimization

### Query Optimization Techniques

**1. Use Query Hints:**
```sql
-- Force index usage
SELECT * FROM Users @{FORCE_INDEX=UsersByEmail}
WHERE Email = 'alice@example.com';

-- Join hints
SELECT * FROM Orders o
JOIN @{JOIN_METHOD=HASH_JOIN} Customers c ON o.CustomerId = c.CustomerId;

-- Batch hints (parallel execution)
SELECT * FROM Users @{USE_ADDITIONAL_PARALLELISM=TRUE}
WHERE Country = 'US';
```

**2. Batch Operations:**
```sql
-- Batch mutations (up to 20,000 mutations per transaction)
BEGIN TRANSACTION;
  INSERT INTO Users (UserId, Name) VALUES (1, 'Alice');
  INSERT INTO Users (UserId, Name) VALUES (2, 'Bob');
  INSERT INTO Users (UserId, Name) VALUES (3, 'Charlie');
  -- ... up to 20,000 rows
COMMIT TRANSACTION;
```

**3. Partitioned DML:**
```sql
-- Update millions of rows efficiently
PARTITIONED DML UPDATE Users SET LastLogin = CURRENT_TIMESTAMP()
WHERE LastLogin < TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY);
```

**4. Use Mutations API (not DML) for High Throughput:**
```python
# Mutations API bypasses SQL parsing (10x faster for bulk operations)
with database.batch() as batch:
    batch.insert(
        table='Users',
        columns=['UserId', 'Name', 'Email'],
        values=[
            (1, 'Alice', 'alice@example.com'),
            (2, 'Bob', 'bob@example.com'),
            # ... thousands of rows
        ]
    )
```

### Data Boost for Analytics

**Isolate analytical workloads:**
```bash
# Enable Data Boost (separate compute for analytics)
gcloud spanner databases execute-sql my-database \
    --instance=my-instance \
    --sql="SELECT * FROM Users" \
    --data-boost-enabled
```

**Benefits:**
- No impact on OLTP workloads
- Elastic compute (pay only when used)
- Faster analytical queries

### Read-Only Replicas

**Architecture:**
```
Multi-Region Configuration
├── us-central1 (Read-Write)
├── us-east1 (Read-Write)
├── us-west1 (Read-Write)
└── asia-southeast1 (Read-Only Replica)
```

**Configuration:**
```bash
# Add read-only replica
gcloud spanner instances update my-instance \
    --add-read-only-replicas=asia-southeast1
```

**Use Case:**
- Serve low-latency reads in additional regions
- Offload read traffic from read-write replicas
- Regional compliance (data residency)

### CPU Utilization Targets

| Workload Type | Target CPU | Recommendation |
|---------------|------------|----------------|
| **OLTP (Priority)** | <65% | Scale up at 65% |
| **Mixed (OLTP + Analytical)** | <50% | Use Data Boost for analytics |
| **Batch Processing** | <75% | Monitor closely, scale up |

---

## High Availability & Disaster Recovery

### Multi-Region HA Architecture

**Configuration:**
```
nam3 (North America Multi-Region)
├── us-central1 (Iowa) - Read-Write
├── us-east1 (Virginia) - Read-Write
└── us-west1 (Oregon) - Read-Write
```

**Availability SLA:**
- 99.999% (five 9s) = 5.26 minutes downtime/year
- Automatic failover across regions
- No single point of failure

### Leader Region (Default Leader)

**Concept:**
- One region acts as default leader for write transactions
- Reduces commit latency for writes originating in that region

**Configuration:**
```bash
# Set default leader region
gcloud spanner instances update my-instance \
    --instance-config=nam3 \
    --default-leader=us-central1
```

**Multi-Region Leader Configuration:**
```sql
-- Set per-database default leader
ALTER DATABASE my-database
SET OPTIONS (default_leader = 'us-central1');
```

### Backup & Recovery Strategies

**1. Regular Backups:**
```bash
# Create backup with 90-day retention
gcloud spanner backups create production-backup-$(date +%Y%m%d) \
    --instance=production-instance \
    --database=production-db \
    --retention-period=90d \
    --version-time="2024-11-20T10:00:00Z"
```

**2. Point-in-Time Recovery (PITR):**
```bash
# Enable PITR (1-7 day retention)
gcloud spanner databases ddl update my-database \
    --instance=my-instance \
    --enable-pitr \
    --pitr-retention-period=7d

# Restore to specific point in time
gcloud spanner databases create restored-db \
    --instance=my-instance \
    --source-database=projects/PROJECT/instances/INSTANCE/databases/my-database \
    --version-time="2024-11-20T14:30:00Z"
```

**3. Cross-Region Backup Replication:**
```bash
# Copy backup to another region
gcloud spanner backups copy source-backup \
    --source-instance=us-instance \
    --source-backup=my-backup \
    --destination-instance=eu-instance \
    --destination-backup=my-backup-eu
```

### Disaster Recovery Patterns

**Pattern 1: Multi-Region Active-Active**
```
Global Application
├── Region A (Read-Write, Serves North America)
├── Region B (Read-Write, Serves Europe)
└── Region C (Read-Write, Serves Asia)
```
- **RPO:** Near 0 (continuous replication)
- **RTO:** <1 minute (automatic failover)
- **Cost:** Highest

**Pattern 2: Regional with Cross-Region Backups**
```
Primary: us-central1 (Regional)
DR: Backups replicated to europe-west1
```
- **RPO:** Backup frequency (e.g., 1 hour)
- **RTO:** 30-60 minutes (restore time)
- **Cost:** Lower

**Pattern 3: Dual-Region**
```
nam-eur-asia1 (Dual-Region)
├── us-central1 (Read-Write)
└── europe-west1 (Read-Write)
```
- **RPO:** Near 0
- **RTO:** <5 minutes
- **Cost:** Medium

---

## Cost Optimization

### Cost Model

**Compute:**
- Processing units: $0.09 per 100 units/hour (regional)
- Nodes: $0.90/hour (regional), ~$3/hour (multi-region)

**Storage:**
- Regional: $0.30/GB/month
- Multi-region: $0.50/GB/month

**Network:**
- Cross-region replication: $0.01-$0.02/GB

**Backups:**
- Regional: $0.11/GB/month
- Multi-region: $0.17/GB/month

### Optimization Strategies

**1. Right-Size Processing Units:**
```bash
# Monitor CPU utilization
gcloud monitoring time-series list \
    --filter='metric.type="spanner.googleapis.com/instance/cpu/utilization"'

# Scale down if consistently <40%
gcloud spanner instances update my-instance \
    --processing-units=1000  # Down from 2000
```

**2. Use Autoscaling:**
```bash
# Enable autoscaling (recommended)
gcloud spanner instances update my-instance \
    --autoscaling-min-processing-units=1000 \
    --autoscaling-max-processing-units=5000 \
    --autoscaling-high-priority-cpu-target=65
```

**3. Choose Regional for Non-Global Workloads:**
- Regional: $0.90/node/hour
- Multi-region: ~$3.00/node/hour
- **Savings:** 67% by using regional

**4. Optimize Storage:**
```sql
-- Delete old data
DELETE FROM UserEvents 
WHERE EventTime < TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 365 DAY);

-- Use TTL policies (requires scheduled job)
DELETE FROM Logs WHERE CreatedAt < @retention_date;
```

**5. Use Read-Only Replicas Strategically:**
- Only add read-only replicas if needed for latency/compliance
- Each replica adds storage cost

**6. Backup Optimization:**
```bash
# Set appropriate retention (not too long)
gcloud spanner backups create monthly-backup \
    --instance=my-instance \
    --database=my-database \
    --retention-period=30d  # Not 365d

# Delete old backups
gcloud spanner backups delete old-backup --instance=my-instance
```

**7. Use Data Boost for Analytics:**
- Separate billing for analytical queries
- Prevents overprovisioning for peak analytical loads

### Cost Comparison Example

**Scenario:** 2 TB database, 1M QPS reads, 100K QPS writes

| Configuration | Nodes | Monthly Cost | Notes |
|---------------|-------|--------------|-------|
| Regional (us-central1) | 5 | ~$3,240 | 5 nodes × $0.90/hr × 720 hrs + storage |
| Multi-region (nam3) | 5 | ~$10,800 | 5 nodes × $3/hr × 720 hrs + storage |
| **Savings (Regional)** | | **$7,560/month** | **70% less** |

---

## Security Architecture

### Defense-in-Depth Strategy

**Layer 1: Network Security**
```
VPC Service Controls Perimeter
├── Private Service Connect
├── VPC Peering
└── IAP (Identity-Aware Proxy)
```

**Configuration:**
```bash
# Create VPC Service Controls perimeter
gcloud access-context-manager perimeters create spanner-perimeter \
    --resources=projects/PROJECT_NUMBER \
    --restricted-services=spanner.googleapis.com \
    --policy=POLICY_ID
```

**Layer 2: Identity & Access Management**
```
IAM Hierarchy
├── Organization-Level: Viewer
├── Folder-Level: DatabaseReader (for analytics team)
└── Project-Level: DatabaseUser (for apps)
    └── Database-Level: Fine-grained roles
```

**Layer 3: Encryption**
- At-rest: Customer-Managed Encryption Keys (CMEK)
- In-transit: TLS 1.2+
- Application-level: Field-level encryption for sensitive data

### Customer-Managed Encryption Keys (CMEK)

**Setup:**
```bash
# Create KMS key ring
gcloud kms keyrings create spanner-keyring --location=us-central1

# Create key
gcloud kms keys create spanner-key \
    --location=us-central1 \
    --keyring=spanner-keyring \
    --purpose=encryption

# Grant Spanner access to key
gcloud kms keys add-iam-policy-binding spanner-key \
    --location=us-central1 \
    --keyring=spanner-keyring \
    --member=serviceAccount:service-PROJECT_NUMBER@gcp-sa-cloud-spanner.iam.gserviceaccount.com \
    --role=roles/cloudkms.cryptoKeyEncrypterDecrypter

# Create CMEK-encrypted database
gcloud spanner databases create encrypted-db \
    --instance=my-instance \
    --kms-key=projects/PROJECT/locations/us-central1/keyRings/spanner-keyring/cryptoKeys/spanner-key
```

### Audit Logging

**Enable Data Access Logs:**
```yaml
# IAM policy with audit config
auditConfigs:
  - service: spanner.googleapis.com
    auditLogConfigs:
      - logType: ADMIN_READ
      - logType: DATA_READ
      - logType: DATA_WRITE
```

**Query Audit Logs:**
```bash
gcloud logging read "resource.type=spanner_instance" \
    --limit=100 \
    --format=json
```

### Compliance & Data Residency

**Data Residency:**
```bash
# Use region-specific configuration
gcloud spanner instances create eu-instance \
    --config=regional-europe-west1 \
    --processing-units=1000

# Multi-region with geographic control
gcloud spanner instances create eu-multi-instance \
    --config=eur3  # Belgium, Netherlands, Germany only
    --processing-units=3000
```

**Compliance Certifications:**
- SOC 2/3, ISO 27001, PCI-DSS, HIPAA, GDPR
- FedRAMP (government workloads)

---

## Migration Strategies

### Migrating from MySQL/PostgreSQL

**1. Schema Conversion:**
```bash
# Use Spanner Migration Tool (Harbourbridge)
git clone https://github.com/GoogleCloudPlatform/spanner-migration-tool.git
cd spanner-migration-tool

# Generate schema from MySQL dump
./spanner-migration-tool schema \
    --source=mysql \
    --source-profile="host=localhost,port=3306,user=root,password=pass,dbname=mydb" \
    --target-profile="project=my-project,instance=my-instance" \
    --target=my-spanner-db
```

**2. Data Migration:**
```bash
# Bulk load using Dataflow
./spanner-migration-tool data \
    --source=mysql \
    --source-profile="..." \
    --target-profile="..." \
    --target=my-spanner-db
```

**3. Schema Modifications:**
```sql
-- Convert auto-increment to sequences
-- MySQL:
-- CREATE TABLE users (id INT AUTO_INCREMENT PRIMARY KEY, ...);

-- Spanner (GoogleSQL):
CREATE SEQUENCE user_seq OPTIONS (sequence_kind="bit_reversed_positive");
CREATE TABLE users (
    id INT64 DEFAULT (GET_NEXT_SEQUENCE_VALUE(SEQUENCE user_seq)),
    ...
) PRIMARY KEY (id);
```

### Migrating from Sharded MySQL

**Scenario:** 16 MySQL shards → Single Spanner instance

**Challenges:**
- Application logic includes sharding
- Cross-shard queries impossible
- Manual rebalancing required

**Solution:**
1. **Unified Schema:** Merge shard schemas into single Spanner schema
2. **Add Shard Key:** Include original shard ID in primary key (optional)
3. **Bulk Load:** Parallel load from all shards using Dataflow
4. **Application Changes:** Remove sharding logic, use Spanner client

**Example:**
```sql
-- Original sharded schema (16 shards)
CREATE TABLE users_shard_0 (id INT, name VARCHAR(100), ...);
CREATE TABLE users_shard_1 (id INT, name VARCHAR(100), ...);
-- ...

-- Unified Spanner schema
CREATE TABLE users (
    id INT64 NOT NULL,
    name STRING(100),
    ...
) PRIMARY KEY (id);  -- Spanner handles distribution automatically
```

---

## Multi-Tenancy Patterns

### Pattern 1: Database-Per-Tenant

```
Instance: my-multi-tenant-instance
├── Database: tenant-1
├── Database: tenant-2
└── Database: tenant-3
```

**Pros:**
- Strong isolation (data, schema, performance)
- Easy backups/restore per tenant
- Simple to implement

**Cons:**
- Higher cost (overhead per database)
- Complex multi-tenant queries
- Management overhead (100s of databases)

**Use Case:** B2B SaaS with large tenants, strict isolation required

### Pattern 2: Shared Database with Tenant Column

```sql
CREATE TABLE Users (
    TenantId STRING(36) NOT NULL,
    UserId INT64 NOT NULL,
    Name STRING(100),
    Email STRING(255)
) PRIMARY KEY (TenantId, UserId);

-- All queries include TenantId
SELECT * FROM Users WHERE TenantId = @tenantId AND UserId = @userId;
```

**Pros:**
- Cost-effective (single database)
- Easy to add tenants
- Simple management

**Cons:**
- No data isolation (security risk)
- Cross-tenant queries possible (data leak risk)
- Noisy neighbor (tenant A impacts tenant B performance)

**Use Case:** B2C SaaS with many small tenants

### Pattern 3: Hybrid (Sharded Tenants)

```sql
-- Tenant shard assignment table
CREATE TABLE TenantShards (
    TenantId STRING(36) NOT NULL,
    ShardId INT64 NOT NULL,
    CreatedAt TIMESTAMP
) PRIMARY KEY (TenantId);

-- User table with shard key
CREATE TABLE Users (
    ShardId INT64 NOT NULL,
    TenantId STRING(36) NOT NULL,
    UserId INT64 NOT NULL,
    Name STRING(100)
) PRIMARY KEY (ShardId, TenantId, UserId);
```

**Pros:**
- Balance isolation and cost
- Can isolate large tenants
- Better performance isolation

**Cons:**
- More complex application logic
- Rebalancing required as tenants grow

**Use Case:** Mix of small and large tenants

---

## Enterprise Integration Patterns

### Event-Driven Architecture with Change Streams

**Change Streams** capture row-level changes in near real-time:

```sql
-- Create change stream
CREATE CHANGE STREAM UsersChangeStream
FOR Users;

-- Query change stream
SELECT * FROM READ_UsersChangeStream(
    start_timestamp => @start_time,
    end_timestamp => @end_time
);
```

**Integration with Pub/Sub:**
```bash
# Stream changes to Pub/Sub
gcloud spanner databases change-streams create user-stream \
    --instance=my-instance \
    --database=my-database \
    --change-stream=UsersChangeStream \
    --target-topic=projects/PROJECT/topics/user-changes
```

**Use Cases:**
- Real-time data pipelines
- Event sourcing
- Cache invalidation
- Cross-system synchronization

### Integration with BigQuery (Analytics)

**Federated Queries:**
```sql
-- Query Spanner from BigQuery
SELECT u.UserId, u.Name, o.TotalAmount
FROM `project.dataset.external_spanner_table` u
JOIN `project.dataset.orders` o ON u.UserId = o.UserId
WHERE u.Country = 'US';
```

**Scheduled ETL with Dataflow:**
```bash
# Export Spanner data to BigQuery daily
gcloud dataflow jobs run spanner-to-bq \
    --gcs-location=gs://dataflow-templates/latest/Spanner_to_BigQuery \
    --region=us-central1 \
    --parameters \
        spannerInstanceId=my-instance,\
        spannerDatabaseId=my-database,\
        spannerTable=Users,\
        bigQueryDataset=analytics,\
        bigQueryTable=users
```

### API Gateway Integration

**Architecture:**
```
Client → API Gateway (Apigee) → Cloud Run → Spanner
```

**Benefits:**
- Rate limiting (protect Spanner from overload)
- Authentication/authorization
- Request transformation
- API versioning

---

## PCA Exam Tips

### Key Architectural Patterns

1. **Global Strong Consistency:**
   - Use Spanner for financial transactions, inventory management
   - TrueTime enables external consistency globally
   - No "eventual consistency" issues

2. **Multi-Region Selection:**
   - Use multi-region (nam3, eur3, asia1) for global apps, 99.999% SLA
   - Use regional for cost savings when users are regional
   - Dual-region for balance of cost and redundancy

3. **Schema Design:**
   - **Hotspot avoidance:** Never use monotonic keys (timestamps, auto-increments)
   - **Use UUIDs, bit-reversed sequences, or hash-based sharding**
   - **Interleaving:** For parent-child relationships frequently queried together

4. **Performance:**
   - Target CPU <65% for OLTP
   - Use Data Boost for analytics (separate compute)
   - Use read-only replicas for low-latency regional reads
   - Batch operations for bulk inserts/updates

5. **Cost Optimization:**
   - Regional is 67% cheaper than multi-region
   - Autoscaling prevents overprovisioning
   - Delete old data to reduce storage costs
   - Use appropriate backup retention (not 365 days by default)

6. **HA & DR:**
   - Multi-region: RPO near 0, RTO <1 minute
   - Regional + backups: RPO = backup frequency, RTO = restore time
   - PITR for 1-7 days (accidental data changes)

7. **Security:**
   - CMEK for compliance (customer-managed keys)
   - VPC Service Controls for network isolation
   - IAM roles at database level (fine-grained access)
   - Audit logging for compliance

### Common Exam Scenarios

**Scenario 1:** Global e-commerce app needs 99.999% availability
- **Answer:** Multi-region Spanner (nam3, eur3, or asia1)

**Scenario 2:** High write throughput causing hotspots
- **Answer:** Redesign primary key (use UUID or bit-reversed sequence)

**Scenario 3:** Need to run analytics without impacting OLTP
- **Answer:** Use Data Boost for analytical queries

**Scenario 4:** Migrating from 16-shard MySQL to single database
- **Answer:** Use Spanner (horizontal scaling), migrate with Dataflow, remove sharding logic

**Scenario 5:** Comply with GDPR (data residency in EU)
- **Answer:** Use regional Spanner in europe-west1 or multi-region eur3

**Scenario 6:** Need to sync Spanner changes to external system in real-time
- **Answer:** Use Change Streams with Pub/Sub integration

**Scenario 7:** Balance cost and availability for regional app
- **Answer:** Use dual-region Spanner (2 regions, 99.99% SLA, lower cost than multi-region)

### Decision Trees

**Database Selection:**
```
Need strong consistency? → Yes
Need horizontal scale (>10TB)? → Yes
Global distribution? → Yes → Multi-region Spanner
               → No → Regional Spanner or Cloud SQL
```

**Primary Key Design:**
```
High write rate? → Yes
Monotonic key (timestamp, auto-increment)? → Yes → Use UUID or swap key order
                                             → No → Okay to use
```

**Cost Optimization:**
```
Global users? → No → Use regional Spanner (67% cheaper)
             → Yes → Use multi-region Spanner
Autoscaling enabled? → No → Enable autoscaling
                     → Yes → Monitor and adjust min/max
```

---

## Additional Resources

- [Spanner Documentation](https://cloud.google.com/spanner/docs)
- [Schema Design Best Practices](https://cloud.google.com/spanner/docs/schema-design)
- [SQL Best Practices](https://cloud.google.com/spanner/docs/sql-best-practices)
- [Spanner Proof of Concept Playbook](https://cloud.google.com/spanner/docs/proof-of-concept-playbook)
- [TrueTime Paper](https://research.google/pubs/pub39966/)
- [Migration Tool (Harbourbridge)](https://github.com/GoogleCloudPlatform/spanner-migration-tool)
- [Spanner Architecture Whitepaper](https://static.googleusercontent.com/media/research.google.com/en//archive/spanner-osdi2012.pdf)

---

**Last Updated:** November 2025  
**Exam:** Google Professional Cloud Architect (PCA)
