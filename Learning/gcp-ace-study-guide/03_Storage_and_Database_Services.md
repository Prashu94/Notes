# 03. Storage and Database Services (Masterclass Edition)

Selecting the right storage or database is essentially a trade-off between **Latency, Consistency, Scaling, and Cost.**

---

## 3.1 Cloud Storage (GCS) - Architectural Detail
GCS is an object store (not a file system) designed for binary large objects (blobs). Globally available, 11 nines durability.

### 3.1.1 Consistency Model
*   **Strong Consistency**: Read-after-write, read-after-update, and read-after-delete are all strongly consistent for **objects**.
*   **Eventual Consistency**: List operations (listing files in a bucket) can be eventually consistent due to the distributed nature of the metadata catalog.
*   **Atomic Updates**: You cannot partially update an object. You upload the entire object again.

### 3.1.2 Storage Classes & Minimums

| Storage Class | Min Duration | Access Frequency | Retrieval Cost | Use Case |
|---------------|--------------|------------------|----------------|----------|
| **Standard** | None | High-frequency | None | Hot data, websites, streaming |
| **Nearline** | 30 days | < 1x/month | $0.01/GB | Backups, long-tail content |
| **Coldline** | 90 days | < 1x/quarter | $0.02/GB | Disaster recovery |
| **Archive** | 365 days | < 1x/year | $0.05/GB | Compliance, legal holds |

**Key Exam Points**:
*   Early deletion: Billed for remaining minimum duration
*   All classes have same latency (milliseconds)
*   All classes have same durability (11 nines)
*   All classes have same availability SLA (varies by location type)

#### Autoclass (Intelligent Tiering)
Automatically transitions objects between classes based on access patterns. No lifecycle rules needed.

```bash
# Create bucket with Autoclass enabled
gcloud storage buckets create gs://my-autoclass-bucket \
    --location=us-central1 \
    --autoclass \
    --autoclass-terminal-storage-class=ARCHIVE

# Enable Autoclass on existing bucket
gcloud storage buckets update gs://my-bucket --enable-autoclass
```

#### Lifecycle Management
Automate object management based on conditions:

| Action | Description |
|--------|-------------|
| `Delete` | Remove objects matching conditions |
| `SetStorageClass` | Change storage class (only to colder) |
| `AbortIncompleteMultipartUpload` | Clean up failed uploads |

```bash
# Create lifecycle configuration (lifecycle.json)
cat > lifecycle.json << EOF
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "SetStorageClass", "storageClass": "NEARLINE"},
        "condition": {"age": 30, "matchesStorageClass": ["STANDARD"]}
      },
      {
        "action": {"type": "SetStorageClass", "storageClass": "COLDLINE"},
        "condition": {"age": 90, "matchesStorageClass": ["NEARLINE"]}
      },
      {
        "action": {"type": "Delete"},
        "condition": {"age": 365}
      }
    ]
  }
}
EOF

# Apply lifecycle policy
gcloud storage buckets update gs://my-bucket --lifecycle-file=lifecycle.json
```

### 3.1.3 Security & Access Control

#### Access Control Models

| Model | Scope | Use Case |
|-------|-------|----------|
| **Uniform** | Bucket-level IAM only | Recommended for most cases |
| **Fine-grained** | Bucket IAM + Object ACLs | Legacy, per-object sharing |

```bash
# Enable uniform bucket-level access (recommended)
gcloud storage buckets update gs://my-bucket --uniform-bucket-level-access

# Grant bucket-level access
gcloud storage buckets add-iam-policy-binding gs://my-bucket \
    --member=user:analyst@example.com \
    --role=roles/storage.objectViewer
```

#### Common IAM Roles

| Role | Permissions |
|------|-------------|
| `storage.objectViewer` | Read objects |
| `storage.objectCreator` | Write objects (no read/delete) |
| `storage.objectAdmin` | Full object CRUD |
| `storage.admin` | Full bucket + object control |

#### Signed URLs & Signed Policy Documents

| Method | Use Case | How It Works |
|--------|----------|--------------|
| **Signed URL** | Temporary access to specific object | URL includes cryptographic signature |
| **Signed Policy Document** | Control uploads (size, type limits) | JSON policy embedded in form |

```bash
# Generate a signed URL (requires service account key)
gcloud storage sign-url gs://my-bucket/my-file.pdf \
    --duration=1h \
    --private-key-file=key.json

# Using Python client library (recommended)
from google.cloud import storage
from datetime import timedelta

client = storage.Client()
bucket = client.bucket('my-bucket')
blob = bucket.blob('my-file.pdf')

url = blob.generate_signed_url(
    version='v4',
    expiration=timedelta(hours=1),
    method='GET'
)
```

### 3.1.4 Data Transfer Options

| Method | Best For | Speed |
|--------|----------|-------|
| `gcloud storage cp` | < 1 TB | Network dependent |
| **Storage Transfer Service** | Cloud-to-cloud, scheduled | Managed, parallelized |
| **Transfer Appliance** | > 20 TB, poor network | Physical device shipped |
| **Transfer Service for on-prem** | On-prem to GCS | Agent-based, high performance |

```bash
# Copy files to GCS
gcloud storage cp -r ./local-folder gs://my-bucket/

# Parallel upload for large files
gcloud storage cp large-file.zip gs://my-bucket/ --parallel-composite-upload-threshold=150M

# Rsync for incremental syncs
gcloud storage rsync -r ./local-folder gs://my-bucket/folder/
```

---

## 3.2 Relational Databases (OLTP)

### 3.2.1 Cloud SQL
Managed instances for MySQL, PostgreSQL, and SQL Server.

#### Instance Configuration

| Setting | Options | Impact |
|---------|---------|--------|
| **Machine Type** | Shared-core to 96 vCPUs | Performance, cost |
| **Storage** | SSD or HDD, 10GB-64TB | IOPS, durability |
| **Storage Auto-resize** | Up to specified limit | Prevents outages |
| **Maintenance Window** | Day/time | When updates occur |

```bash
# Create a Cloud SQL instance
gcloud sql instances create my-postgres \
    --database-version=POSTGRES_15 \
    --tier=db-custom-4-15360 \
    --region=us-central1 \
    --storage-type=SSD \
    --storage-size=100GB \
    --storage-auto-increase \
    --backup-start-time=04:00 \
    --availability-type=REGIONAL

# Create a database
gcloud sql databases create mydb --instance=my-postgres

# Create a user
gcloud sql users create appuser \
    --instance=my-postgres \
    --password=securepassword
```

#### High Availability Architecture

| Configuration | Zones | Failover | Cost |
|--------------|-------|----------|------|
| **Single Zone** | 1 | None (manual restore from backup) | 1x |
| **High Availability** | 2 (Primary + Standby) | Automatic (~1-2 min) | ~2x |

*   **Synchronous Replication**: Data written to both primary and standby before commit.
*   **Same Static IP**: Failover preserves the instance IP address.
*   **Standby Not Readable**: Cannot read from standby; use read replicas for read scaling.

#### Read Replicas

| Feature | Details |
|---------|---------|
| **Replication** | Asynchronous |
| **Lag** | Seconds to minutes |
| **Cross-Region** | Supported (for DR or latency) |
| **Promotion** | Manual (becomes standalone) |
| **Use Cases** | Read scaling, analytics, geo-distribution |

```bash
# Create a read replica
gcloud sql instances create my-postgres-replica \
    --master-instance-name=my-postgres \
    --region=us-east1

# Promote replica to standalone (disaster recovery)
gcloud sql instances promote-replica my-postgres-replica
```

#### Connectivity Options

| Method | Use Case | Configuration |
|--------|----------|---------------|
| **Public IP** | Quick dev/test | Authorized networks |
| **Private IP** | Production (VPC) | VPC peering, no internet |
| **Cloud SQL Auth Proxy** | Secure connection | IAM-based, encrypted |
| **Private Service Connect** | Enterprise | No VPC peering needed |

```bash
# Connect via Cloud SQL Auth Proxy
cloud_sql_proxy -instances=PROJECT:REGION:INSTANCE=tcp:5432

# Connect using gcloud
gcloud sql connect my-postgres --user=appuser --database=mydb
```

### 3.2.2 Cloud Spanner (The Relational Giant)
Google's proprietary, horizontally scalable relational database with global consistency.

#### Architecture Deep Dive

| Component | Function |
|-----------|----------|
| **Splits** | Shards of table data distributed across nodes |
| **TrueTime** | GPS + atomic clocks for global ordering |
| **Paxos** | Consensus protocol for replication |

#### Configuration Types

| Type | Nodes | Availability SLA | Use Case |
|------|-------|------------------|----------|
| **Regional** | 1+ | 99.99% | Single-region apps |
| **Multi-Regional** | 3+ | 99.999% | Global apps, disaster recovery |

#### Capacity Planning

| Node Count | Read QPS | Write QPS | Storage |
|------------|----------|-----------|---------|
| 1 node | ~10,000 | ~2,000 | 4 TB |
| 3 nodes | ~30,000 | ~6,000 | 12 TB |
| N nodes | N × 10,000 | N × 2,000 | N × 4 TB |

```bash
# Create a regional Spanner instance
gcloud spanner instances create my-spanner \
    --config=regional-us-central1 \
    --nodes=3 \
    --description="Production Spanner"

# Create a multi-regional instance
gcloud spanner instances create global-spanner \
    --config=nam-eur-asia1 \
    --nodes=3 \
    --description="Global multi-region"

# Create a database with schema
gcloud spanner databases create mydb \
    --instance=my-spanner \
    --ddl='CREATE TABLE Users (
        UserId INT64 NOT NULL,
        Name STRING(100),
        Email STRING(100),
    ) PRIMARY KEY (UserId)'
```

#### When to Choose Spanner vs Cloud SQL

| Requirement | Choose |
|-------------|--------|
| Standard MySQL/PostgreSQL compatibility | Cloud SQL |
| Global strong consistency | Spanner |
| Horizontal write scaling | Spanner |
| Cost-sensitive, regional workload | Cloud SQL |
| 99.999% availability requirement | Spanner (multi-regional) |

---

## 3.3 NoSQL Databases

### 3.3.1 Firestore (Document Store)
Serverless, fully managed document database. Successor to Datastore.

#### Data Model

| Concept | Description | Limit |
|---------|-------------|-------|
| **Document** | JSON-like data with fields | 1 MB max |
| **Collection** | Container of documents | Unlimited |
| **Subcollection** | Nested collection within document | 100 levels deep |
| **Field** | Key-value pair within document | 20,000 fields/doc |

#### Modes

| Mode | Use Case | Limitations |
|------|----------|-------------|
| **Native** | Mobile/Web apps, real-time | 1 database per project |
| **Datastore** | Server-side apps, batch | No real-time listeners |

```bash
# Create Firestore database (Native mode)
gcloud firestore databases create \
    --location=us-central \
    --type=firestore-native

# Export data (for backup)
gcloud firestore export gs://my-bucket/firestore-backup

# Import data
gcloud firestore import gs://my-bucket/firestore-backup
```

#### Indexing

| Index Type | Created | Use Case |
|------------|---------|----------|
| **Single-field** | Automatic | Equality, range on one field |
| **Composite** | Manual | Queries on multiple fields |
| **Exemptions** | Manual | Disable indexing for large fields |

```bash
# Create composite index
gcloud firestore indexes composite create \
    --collection-group=orders \
    --field-config=field-path=customerId,order=ASCENDING \
    --field-config=field-path=orderDate,order=DESCENDING
```

#### Pricing Model

| Operation | Cost (per 100K) |
|-----------|-----------------|
| Document reads | $0.06 |
| Document writes | $0.18 |
| Document deletes | $0.02 |
| Storage | $0.18/GB/month |

### 3.3.2 Cloud Bigtable (High-Throughput Key-Value)
Designed for massive analytical and operational workloads. Powers Google Search, Maps, Gmail.

#### Architecture

| Component | Function |
|-----------|----------|
| **Row** | Single entity, identified by row key |
| **Column Family** | Group of related columns |
| **Column Qualifier** | Individual column within family |
| **Cell** | Intersection of row and column (versioned) |
| **Tablet** | Contiguous range of rows (shard) |

#### Cluster Sizing

| Nodes | Read Throughput | Write Throughput | Storage |
|-------|-----------------|------------------|---------|
| 1 | ~10,000 QPS | ~10,000 QPS | 8 TB HDD / 5 TB SSD |
| 3 | ~30,000 QPS | ~30,000 QPS | 24 TB HDD / 15 TB SSD |
| N | N × 10,000 | N × 10,000 | N × storage |

```bash
# Create a Bigtable instance
gcloud bigtable instances create my-bigtable \
    --display-name="Production Bigtable" \
    --cluster-config=id=my-cluster,zone=us-central1-a,nodes=3,storage-type=SSD

# Create a table with column families
cbt createtable my-table
cbt createfamily my-table cf1
cbt createfamily my-table cf2

# Set column family GC policy (keep last 2 versions)
cbt setgcpolicy my-table cf1 maxversions=2
```

#### Row Key Design (Critical for Performance)

| Pattern | Example | Result |
|---------|---------|--------|
| ❌ **Sequential** | `2024-01-15#event1` | Hotspotting |
| ❌ **Monotonic** | `1, 2, 3, 4...` | Hotspotting |
| ✅ **Reversed** | `51-10-4202#event1` | Distributed |
| ✅ **Salted** | `hash(userId)#userId#timestamp` | Distributed |
| ✅ **Field Promotion** | `userId#timestamp` | Efficient scans |

**Design Principles**:
*   Row key is the ONLY indexed field
*   Design for your most common query pattern
*   Avoid sequential or timestamp-leading keys
*   Keep row keys short (affects storage and network)

#### Replication for HA

| Configuration | Clusters | Use Case |
|---------------|----------|----------|
| **Single Cluster** | 1 | Dev/Test |
| **Multi-Cluster** | 2-4 | Production, global |

```bash
# Add a cluster to existing instance
gcloud bigtable clusters create my-cluster-2 \
    --instance=my-bigtable \
    --zone=us-east1-b \
    --num-nodes=3

# Configure app profile for routing
gcloud bigtable app-profiles create multi-cluster-profile \
    --instance=my-bigtable \
    --route-any \
    --transactional-writes
```

---

## 3.4 BigQuery (Analytical Data Warehouse)

### 3.4.1 Architecture

| Component | Function |
|-----------|----------|
| **Colossus** | Distributed storage (columnar Capacitor format) |
| **Dremel** | Distributed query engine |
| **Jupiter** | Petabit network connecting storage and compute |
| **Borg** | Cluster management |

#### Storage vs Compute Separation
*   Storage and compute scale independently
*   Pay for storage at rest, pay for compute when querying
*   Data automatically replicated and encrypted

### 3.4.2 Pricing Models

| Model | How It Works | Best For |
|-------|--------------|----------|
| **On-Demand** | $5-$8 per TB scanned | Variable workloads, exploration |
| **Capacity (Slots)** | Reserved compute slots | Predictable, heavy workloads |
| **Flex Slots** | Hourly slot commitments | Burst workloads |

#### Storage Pricing

| Type | Cost |
|------|------|
| **Active** | $0.02/GB/month |
| **Long-term** (90+ days untouched) | $0.01/GB/month |
| **Streaming Inserts** | $0.01/200 MB |

```bash
# Check query cost before running
bq query --dry_run --use_legacy_sql=false \
    'SELECT * FROM `project.dataset.table` WHERE date > "2024-01-01"'

# Run query with maximum bytes billed limit
bq query --maximum_bytes_billed=10000000000 --use_legacy_sql=false \
    'SELECT COUNT(*) FROM `project.dataset.large_table`'
```

### 3.4.3 Cost Optimization Patterns

#### Partitioning
Divide tables into segments for targeted queries.

| Partition Type | Use Case | Example |
|----------------|----------|---------|
| **Time-unit (Ingestion)** | Auto-partition on load time | `_PARTITIONTIME` |
| **Time-unit (Column)** | Partition on date/timestamp column | `PARTITION BY DATE(created_at)` |
| **Integer Range** | Partition on numeric column | `PARTITION BY RANGE_BUCKET(customer_id, ...)` |

```sql
-- Create partitioned table
CREATE TABLE `project.dataset.events`
(
  event_id STRING,
  event_type STRING,
  event_timestamp TIMESTAMP,
  user_id STRING,
  payload STRING
)
PARTITION BY DATE(event_timestamp)
OPTIONS(
  partition_expiration_days=365,
  require_partition_filter=true  -- Prevent full table scans
);
```

#### Clustering
Sort data within partitions for efficient filtering.

```sql
-- Create partitioned and clustered table
CREATE TABLE `project.dataset.events`
(
  event_id STRING,
  event_type STRING,
  event_timestamp TIMESTAMP,
  user_id STRING,
  region STRING
)
PARTITION BY DATE(event_timestamp)
CLUSTER BY user_id, region;  -- Up to 4 columns
```

| Feature | Partitioning | Clustering |
|---------|--------------|------------|
| **Columns** | 1 | Up to 4 |
| **Data Type** | DATE, TIMESTAMP, INT | Any |
| **Pruning** | Before query | During query |
| **Maintenance** | None | Auto-reclustering |

### 3.4.4 Data Loading Options

| Method | Latency | Cost | Use Case |
|--------|---------|------|----------|
| **Batch Load** | Minutes | Free | Bulk ETL, migrations |
| **Streaming Insert** | Seconds | $0.01/200MB | Real-time dashboards |
| **Storage Write API** | Seconds | Free (with commit) | High-volume streaming |
| **BigQuery Data Transfer** | Scheduled | Free | SaaS data (GA, Ads) |

```bash
# Load from GCS
bq load --source_format=CSV --autodetect \
    project:dataset.table gs://bucket/data.csv

# Load from GCS with schema
bq load --source_format=NEWLINE_DELIMITED_JSON \
    project:dataset.table gs://bucket/data.json schema.json

# Export to GCS
bq extract --destination_format=PARQUET \
    project:dataset.table gs://bucket/export/data-*.parquet
```

### 3.4.5 External Tables & Federated Queries

Query data without loading it into BigQuery.

| Source | Supported Formats |
|--------|-------------------|
| Cloud Storage | CSV, JSON, Avro, Parquet, ORC |
| Cloud SQL | MySQL, PostgreSQL, SQL Server |
| Cloud Spanner | Native |
| Bigtable | Native |

```sql
-- Create external table pointing to GCS
CREATE EXTERNAL TABLE `project.dataset.external_logs`
OPTIONS (
  format = 'PARQUET',
  uris = ['gs://bucket/logs/*.parquet']
);

-- Federated query to Cloud SQL
SELECT * FROM EXTERNAL_QUERY(
  'projects/my-project/locations/us/connections/my-connection',
  'SELECT * FROM users WHERE created_at > NOW() - INTERVAL 7 DAY'
);
```

---

## 3.5 Memorystore (In-Memory Cache)

Fully managed Redis and Memcached service.

### 3.5.1 Redis vs Memcached

| Feature | Memorystore for Redis | Memorystore for Memcached |
|---------|----------------------|---------------------------|
| **Data Structures** | Strings, Lists, Sets, Hashes, Sorted Sets | Key-Value only |
| **Persistence** | RDB snapshots | None |
| **HA** | Automatic failover | None (add more nodes) |
| **Replication** | Read replicas | None |
| **Max Size** | 300 GB | 5 TB (distributed) |
| **Use Case** | Session cache, leaderboards, pub/sub | Simple caching, large cache pools |

```bash
# Create Redis instance
gcloud redis instances create my-redis \
    --size=5 \
    --region=us-central1 \
    --tier=standard \
    --redis-version=redis_7_0

# Create Memcached instance
gcloud memcache instances create my-memcached \
    --region=us-central1 \
    --node-count=3 \
    --node-cpu=1 \
    --node-memory=1024MB
```

### 3.5.2 Redis Tiers

| Tier | Features | Use Case |
|------|----------|----------|
| **Basic** | Single node, no SLA | Dev/Test |
| **Standard** | Automatic failover, 99.9% SLA | Production |

---

## 3.6 Database Selection Decision Matrix

| Requirement | Recommended Service | Why |
| :--- | :--- | :--- |
| **Relational, Standard SQL, Regional** | Cloud SQL | Managed MySQL/PostgreSQL/SQL Server |
| **Relational, Global, Massive Scale** | Cloud Spanner | Horizontal scaling with consistency |
| **NoSQL, Document-based, Mobile Sync** | Firestore | Real-time sync, offline support |
| **NoSQL, IoT/Time-series, Extreme Throughput** | Bigtable | Millions of QPS, < 10ms latency |
| **Analytics, SQL-based, Petabytes** | BigQuery | Serverless, columnar warehouse |
| **Binary Files, Images, Logs, Backups** | Cloud Storage | Object storage, lifecycle management |
| **In-memory Cache, Session Store** | Memorystore Redis | Sub-millisecond latency |
| **Simple Key-Value Cache** | Memorystore Memcached | Large distributed cache |

### 3.6.1 Quick Decision Flowchart

```
┌─────────────────────────────────────────────────────────────┐
│                 DATABASE SELECTION FLOWCHART                │
└─────────────────────────────────────────────────────────────┘
                              │
                    Is it analytical (OLAP)?
                              │
              ┌───────────────┴───────────────┐
             YES                              NO
              │                               │
         BIGQUERY                    Is it relational (SQL)?
              │                               │
              │               ┌───────────────┴───────────────┐
              │              YES                              NO
              │               │                               │
              │     Need global scale/            Is it documents/
              │     99.999% SLA?                  mobile/real-time?
              │               │                               │
              │   ┌───────────┴───────────┐       ┌───────────┴───────────┐
              │  YES                      NO     YES                      NO
              │   │                       │       │                        │
              │ SPANNER              CLOUD SQL  FIRESTORE           High throughput
              │                                                     time-series?
              │                                                           │
              │                                             ┌─────────────┴─────────────┐
              │                                            YES                          NO
              │                                             │                            │
              │                                          BIGTABLE                 Binary files?
              │                                                                         │
              │                                                         ┌───────────────┴───────────────┐
              │                                                        YES                              NO
              │                                                         │                               │
              │                                                   CLOUD STORAGE              MEMORYSTORE (Cache)
```

### 3.6.2 Cost Comparison Tips

| Service | Free Tier | Cost Driver |
|---------|-----------|-------------|
| Cloud Storage | 5 GB Standard | Storage + Operations + Egress |
| Cloud SQL | None | Instance hours + Storage |
| Spanner | $0.90/hr/node (free trial) | Nodes + Storage |
| Firestore | 1 GB storage, 50K reads/day | Operations + Storage |
| Bigtable | None | Nodes + Storage |
| BigQuery | 1 TB queries/month, 10 GB storage | Queries (bytes scanned) or Slots |
| Memorystore | None | GB-hours |
