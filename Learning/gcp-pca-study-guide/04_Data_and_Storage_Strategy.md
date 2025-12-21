# Chapter 04: Data & Storage Strategy

Choosing the right database is often the most important decision an architect makes. Once data is in a system, it's hard (and expensive) to move.

> **Key Principle**: "A properly documented cloud architecture establishes a common language and standards, which enable cross-functional teams to communicate and collaborate effectively."
>
> — [Google Cloud Well-Architected Framework](https://cloud.google.com/architecture/framework)

## 🗄️ Database Selection Decision Tree

```
┌─────────────────────────────────────────────────────────────────┐
│                 Database Selection Decision Tree                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Need SQL/relational queries?                                    │
│       │                                                          │
│       ├── Yes ──► Need global distribution & horizontal scale?  │
│       │               │                                          │
│       │               ├── Yes ──► Cloud Spanner                 │
│       │               │                                          │
│       │               └── No ──► Need high-performance OLTP?    │
│       │                             │                            │
│       │                             ├── Yes ──► AlloyDB         │
│       │                             │                            │
│       │                             └── No ──► Cloud SQL        │
│       │                                                          │
│       └── No ──► What type of data?                             │
│                    │                                             │
│                    ├── Documents ──► Firestore                  │
│                    │                                             │
│                    ├── Wide-column/Time-series ──► Bigtable     │
│                    │                                             │
│                    ├── Key-value cache ──► Memorystore         │
│                    │                                             │
│                    └── Graph ──► Neo4j (Marketplace)           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 📊 Relational Databases (SQL)

### Comparison Matrix

| Feature | Cloud SQL | AlloyDB | Cloud Spanner |
| :--- | :--- | :--- | :--- |
| **Engines** | MySQL, PostgreSQL, SQL Server | PostgreSQL-compatible | Proprietary (SQL + NoSQL) |
| **Scaling** | Vertical (read replicas) | Vertical + Horizontal reads | Horizontal (both) |
| **Availability** | Regional (HA optional) | Regional (HA built-in) | Regional or Multi-regional |
| **Consistency** | Strong (single region) | Strong (single region) | Strong (global) |
| **Max Storage** | 64 TB | 64 TB per instance | Unlimited |
| **Use Case** | Traditional apps | High-performance PostgreSQL | Global mission-critical |
| **Price Point** | $ | $$ | $$$ |

### Cloud SQL

Best for: Traditional web applications, CMS, e-commerce with regional users.

**Example: Create Cloud SQL with High Availability**
```bash
# Create a Cloud SQL PostgreSQL instance with HA
gcloud sql instances create my-postgres-instance \
    --database-version=POSTGRES_15 \
    --tier=db-custom-4-16384 \
    --region=us-central1 \
    --availability-type=REGIONAL \
    --storage-type=SSD \
    --storage-size=100GB \
    --storage-auto-increase \
    --backup-start-time=02:00 \
    --enable-point-in-time-recovery \
    --retained-backups-count=7 \
    --network=projects/my-project/global/networks/my-vpc \
    --no-assign-ip

# Create a read replica
gcloud sql instances create my-postgres-replica \
    --master-instance-name=my-postgres-instance \
    --region=us-east1
```

### AlloyDB

Best for: High-performance OLTP, existing PostgreSQL applications needing 4x performance.

**Key Features**:
- 4x faster than standard PostgreSQL
- 100x faster analytical queries (columnar engine)
- PostgreSQL 14+ compatible
- Automatic scaling of read pools

**Example: AlloyDB Cluster**
```bash
# Create AlloyDB cluster
gcloud alloydb clusters create my-alloydb-cluster \
    --region=us-central1 \
    --network=my-vpc \
    --password=my-secure-password

# Create primary instance
gcloud alloydb instances create my-primary \
    --cluster=my-alloydb-cluster \
    --region=us-central1 \
    --instance-type=PRIMARY \
    --cpu-count=4

# Create read pool
gcloud alloydb instances create my-read-pool \
    --cluster=my-alloydb-cluster \
    --region=us-central1 \
    --instance-type=READ_POOL \
    --read-pool-node-count=2 \
    --cpu-count=2
```

### Cloud Spanner

Best for: Global applications requiring strong consistency, financial systems, gaming.

**Key Features**:
- Unlimited horizontal scaling
- 99.999% availability (multi-regional)
- Strong consistency globally
- SQL support with NoSQL scale

**Example: Cloud Spanner Configuration**
```bash
# Create a multi-regional Spanner instance
gcloud spanner instances create my-spanner-instance \
    --config=nam-eur-asia1 \
    --description="Global Financial Database" \
    --processing-units=1000

# Create a database with schema
gcloud spanner databases create financial_db \
    --instance=my-spanner-instance \
    --ddl='CREATE TABLE Accounts (
        AccountId INT64 NOT NULL,
        CustomerId INT64 NOT NULL,
        Balance NUMERIC NOT NULL,
        CreatedAt TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp=true),
        UpdatedAt TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp=true)
    ) PRIMARY KEY (AccountId)'
```

**Spanner Schema Best Practices**:
```sql
-- Use interleaved tables for parent-child relationships
CREATE TABLE Orders (
    CustomerId INT64 NOT NULL,
    OrderId INT64 NOT NULL,
    OrderDate TIMESTAMP NOT NULL,
    TotalAmount NUMERIC
) PRIMARY KEY (CustomerId, OrderId);

CREATE TABLE OrderItems (
    CustomerId INT64 NOT NULL,
    OrderId INT64 NOT NULL,
    ItemId INT64 NOT NULL,
    ProductId INT64 NOT NULL,
    Quantity INT64 NOT NULL
) PRIMARY KEY (CustomerId, OrderId, ItemId),
INTERLEAVE IN PARENT Orders ON DELETE CASCADE;

-- Use commit timestamps for automatic time tracking
CREATE TABLE AuditLog (
    LogId STRING(36) NOT NULL,
    EventType STRING(50) NOT NULL,
    EventData JSON,
    CreatedAt TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp=true)
) PRIMARY KEY (LogId);
```

## 🔄 Non-Relational Databases (NoSQL)

### Firestore

Best for: Mobile/web apps, real-time sync, serverless applications.

| Mode | Description | Use Case |
| :--- | :--- | :--- |
| **Native Mode** | Real-time listeners, offline support | Mobile apps, web apps |
| **Datastore Mode** | Server-side only, higher throughput | Backend services |

**Example: Firestore with Security Rules**
```javascript
// Firestore Security Rules
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can only read/write their own data
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Orders: users can read their own, admins can read all
    match /orders/{orderId} {
      allow read: if request.auth != null && 
        (resource.data.userId == request.auth.uid || 
         request.auth.token.admin == true);
      allow create: if request.auth != null && 
        request.resource.data.userId == request.auth.uid;
    }
  }
}
```

### Cloud Bigtable

Best for: IoT, time-series, AdTech, massive analytical workloads (petabyte scale).

**Key Characteristics**:
- Single-digit millisecond latency
- Petabyte scale
- HBase API compatible
- Wide-column store (not relational)

**Example: Bigtable with Row Key Design**
```bash
# Create Bigtable instance
gcloud bigtable instances create my-bigtable \
    --cluster=my-cluster \
    --cluster-zone=us-central1-a \
    --cluster-num-nodes=3 \
    --cluster-storage-type=SSD

# Create a table using cbt
cbt createtable iot-data
cbt createfamily iot-data sensor_readings
cbt createfamily iot-data device_info
```

**Row Key Design Pattern (Time Series)**:
```
# Good: Reversed timestamp prevents hotspotting
Row Key: device_id#reverse_timestamp
Example: sensor_001#9223370449315775807

# Bad: Sequential timestamps cause hotspots
Row Key: timestamp#device_id
Example: 2024-01-15T10:30:00#sensor_001

# Alternative: Salted keys for high-write scenarios
Row Key: hash(device_id)#device_id#reverse_timestamp
```

## 📦 Object Storage (Cloud Storage)

### Storage Classes

| Class | Min Duration | Use Case | Price (us-central1) |
| :--- | :--- | :--- | :--- |
| **Standard** | None | Hot data, frequently accessed | $0.020/GB/month |
| **Nearline** | 30 days | Monthly access (backups) | $0.010/GB/month |
| **Coldline** | 90 days | Quarterly access (archives) | $0.004/GB/month |
| **Archive** | 365 days | Yearly access (compliance) | $0.0012/GB/month |

**Example: Lifecycle Management**
```json
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
        "action": {"type": "SetStorageClass", "storageClass": "ARCHIVE"},
        "condition": {"age": 365, "matchesStorageClass": ["COLDLINE"]}
      },
      {
        "action": {"type": "Delete"},
        "condition": {"age": 2555}
      }
    ]
  }
}
```

```bash
# Apply lifecycle policy
gsutil lifecycle set lifecycle.json gs://my-bucket

# Enable versioning for data protection
gsutil versioning set on gs://my-bucket

# Configure retention policy (for compliance)
gsutil retention set 7y gs://my-bucket
```

### Storage Location Types

| Type | Description | Use Case |
| :--- | :--- | :--- |
| **Region** | Single region | Low latency, regional compliance |
| **Dual-region** | Two specific regions | HA with data residency control |
| **Multi-region** | US, EU, or ASIA | Global access, highest availability |

## 📊 Data Warehousing & Analytics

### BigQuery

Serverless, highly scalable data warehouse separating compute from storage.

**Architecture**:
```
┌─────────────────────────────────────────────────────────────────┐
│                    BigQuery Architecture                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                  Dremel Query Engine                     │    │
│  │            (Serverless, Auto-scaling)                    │    │
│  └─────────────────────────────────────────────────────────┘    │
│                            ↓                                     │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                  Colossus Storage                        │    │
│  │         (Columnar format, Capacitor)                     │    │
│  └─────────────────────────────────────────────────────────┘    │
│                            ↓                                     │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │               Jupiter Network                            │    │
│  │        (1 Petabit/sec bisection bandwidth)              │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Example: BigQuery with Partitioning and Clustering**
```sql
-- Create a partitioned and clustered table
CREATE TABLE `myproject.mydataset.sales`
(
  transaction_id STRING NOT NULL,
  customer_id STRING NOT NULL,
  product_id STRING NOT NULL,
  amount NUMERIC NOT NULL,
  transaction_date DATE NOT NULL,
  region STRING NOT NULL
)
PARTITION BY transaction_date
CLUSTER BY region, customer_id
OPTIONS (
  partition_expiration_days = 365,
  description = "Sales transactions partitioned by date"
);

-- Query with partition and cluster pruning
SELECT customer_id, SUM(amount) as total_spend
FROM `myproject.mydataset.sales`
WHERE transaction_date BETWEEN '2024-01-01' AND '2024-03-31'
  AND region = 'US-WEST'
GROUP BY customer_id
ORDER BY total_spend DESC
LIMIT 100;
```

### BigLake

Unified storage for data lakes and warehouses, supporting open formats.

**Features**:
- Query data in Cloud Storage (Parquet, ORC, Avro, JSON)
- Fine-grained row/column level security
- Cross-cloud analytics (AWS S3, Azure Storage)

```sql
-- Create external table with BigLake
CREATE EXTERNAL TABLE `myproject.mydataset.external_sales`
WITH CONNECTION `projects/myproject/locations/us/connections/my-connection`
OPTIONS (
  format = 'PARQUET',
  uris = ['gs://my-bucket/sales/*.parquet']
);
```

## 🔄 Data Migration Strategies

### Migration Decision Matrix

| Scenario | Tool | Description |
| :--- | :--- | :--- |
| **Database to Cloud SQL/AlloyDB** | Database Migration Service (DMS) | Continuous replication, minimal downtime |
| **Large local data to GCS** | Storage Transfer Service | Scheduled transfers, bandwidth management |
| **Petabyte-scale offline** | Transfer Appliance | Physical device shipped to Google |
| **Existing cloud to GCS** | Storage Transfer Service | Cross-cloud transfers |
| **BigQuery from other DW** | BigQuery Data Transfer Service | Scheduled from SaaS sources |

**Example: Database Migration Service**
```bash
# Create a connection profile for source (on-prem MySQL)
gcloud database-migration connection-profiles create source-mysql \
    --region=us-central1 \
    --display-name="On-prem MySQL" \
    --mysql-host=192.168.1.100 \
    --mysql-port=3306 \
    --mysql-username=migration_user \
    --mysql-password-secret=projects/myproject/secrets/mysql-password/versions/latest

# Create a connection profile for destination (Cloud SQL)
gcloud database-migration connection-profiles create dest-cloudsql \
    --region=us-central1 \
    --display-name="Cloud SQL MySQL" \
    --cloudsql-instance=myproject:us-central1:my-instance

# Create and start migration job
gcloud database-migration migration-jobs create my-migration \
    --region=us-central1 \
    --type=CONTINUOUS \
    --source=source-mysql \
    --destination=dest-cloudsql

gcloud database-migration migration-jobs start my-migration \
    --region=us-central1
```

## 🔐 Data Security Patterns

### Encryption Options

| Type | Description | Key Management |
| :--- | :--- | :--- |
| **Google-managed** | Default, transparent | Google manages |
| **CMEK** | Customer-managed encryption keys | You manage in Cloud KMS |
| **CSEK** | Customer-supplied encryption keys | You supply keys per request |

**Example: CMEK for Cloud Storage**
```bash
# Create a key ring
gcloud kms keyrings create my-keyring --location=us-central1

# Create a key
gcloud kms keys create my-key \
    --location=us-central1 \
    --keyring=my-keyring \
    --purpose=encryption

# Grant Cloud Storage service account access to key
gsutil kms authorize -k projects/myproject/locations/us-central1/keyRings/my-keyring/cryptoKeys/my-key

# Create bucket with CMEK
gsutil mb -l us-central1 \
    -k projects/myproject/locations/us-central1/keyRings/my-keyring/cryptoKeys/my-key \
    gs://my-encrypted-bucket
```

---

📚 **Documentation Links**:
- [Cloud SQL Documentation](https://cloud.google.com/sql/docs)
- [AlloyDB Documentation](https://cloud.google.com/alloydb/docs)
- [Cloud Spanner Documentation](https://cloud.google.com/spanner/docs)
- [Firestore Documentation](https://cloud.google.com/firestore/docs)
- [Bigtable Documentation](https://cloud.google.com/bigtable/docs)
- [BigQuery Documentation](https://cloud.google.com/bigquery/docs)
- [Cloud Storage Documentation](https://cloud.google.com/storage/docs)
- [Database Migration Service](https://cloud.google.com/database-migration/docs)

---
[Next Chapter: Security & Compliance](05_Security_and_Compliance_by_Design.md)
