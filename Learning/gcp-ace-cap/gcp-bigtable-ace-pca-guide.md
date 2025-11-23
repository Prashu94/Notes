# Google Cloud Bigtable - ACE & PCA Comprehensive Guide

## Table of Contents
1. [Overview](#overview)
2. [Core Concepts](#core-concepts)
3. [Architecture](#architecture)
4. [Data Model](#data-model)
5. [When to Use Bigtable](#when-to-use-bigtable)
6. [Instance Configuration](#instance-configuration)
7. [Schema Design](#schema-design)
8. [Performance Optimization](#performance-optimization)
9. [Operations](#operations)
10. [Security](#security)
11. [Monitoring](#monitoring)
12. [Cost Optimization](#cost-optimization)
13. [Migration](#migration)
14. [Best Practices](#best-practices)
15. [Exam Tips](#exam-tips)

---

## Overview

Cloud Bigtable is Google's **NoSQL wide-column database** service, based on the original Bigtable paper that inspired HBase and Cassandra. It's designed for **massive-scale** analytical and operational workloads.

**Key Characteristics:**
- **Petabyte-scale:** Single table can store petabytes of data
- **Low latency:** Sub-10ms reads/writes at scale
- **High throughput:** Millions of operations per second
- **Fully managed:** No ops overhead
- **HBase compatible:** Easy migration from HBase

**Use Cases:**
- Time-series data (IoT sensors, financial tickers)
- Marketing data (user events, clickstreams)
- Financial data (transaction histories)
- IoT data (sensor readings)
- Graph data (social networks)

---

## Core Concepts

### Instance

A Bigtable instance is a container for your data with compute and storage resources.

**Components:**
- **Clusters:** One or more clusters in different zones/regions
- **Nodes:** Compute resources (each node provides ~10K QPS)
- **Tables:** Actual data containers
- **Storage:** SSD or HDD

### Table

A table contains rows identified by row keys.

**Properties:**
- **Row key:** Unique identifier (like primary key)
- **Column families:** Groups of columns
- **Columns:** Individual fields
- **Cells:** Timestamped values

### Row Key

The most important design decision! Row key determines:
- Data distribution
- Query performance
- Hotspotting

**Format:** Any string (up to 4KB)

### Column Family

Logical grouping of columns with same access patterns.

**Characteristics:**
- Defined at table creation
- Cannot be changed easily
- Has garbage collection policy
- Up to ~100 column families (but typically 1-10)

### Cell

A cell contains a value at a specific timestamp.

**Properties:**
- Multiple versions (timestamps)
- Configurable retention
- Immutable (can only add/delete, not update)

---

## Architecture

### High-Level Architecture

```
Client Application
    ↓
Cloud Bigtable API
    ↓
Bigtable Instance
    ├── Cluster 1 (us-central1-a)
    │   ├── Node 1
    │   ├── Node 2
    │   └── Node 3
    └── Cluster 2 (us-east1-b) [Optional, for replication]
        ├── Node 1
        ├── Node 2
        └── Node 3
    ↓
Google Colossus (Storage)
    ├── SSDs (low latency)
    └── HDDs (cost-effective)
```

### Storage and Compute Separation

**Key Design:**
- **Compute (Nodes):** Handle requests, manage tablets
- **Storage (Colossus):** Durably store data
- **Separation Benefit:** Scale them independently

### Tablets

Data is divided into **tablets** (contiguous row ranges):
```
Tablet 1: Rows A-F
Tablet 2: Rows G-M
Tablet 3: Rows N-Z
```

**Automatic Balancing:**
- Bigtable automatically redistributes tablets across nodes
- Ensures even load distribution

---

## Data Model

### Wide-Column Model

```
Row Key: "user123#2024-01-15"
│
├── Column Family: "info"
│   ├── Column: "name" → Value: "John Doe"
│   ├── Column: "email" → Value: "john@example.com"
│   └── Column: "age" → Value: "30"
│
└── Column Family: "metrics"
    ├── Column: "pageviews" → Value: "150"
    ├── Column: "clicks" → Value: "25"
    └── Column: "purchases" → Value: "3"
```

### Logical View

| Row Key | info:name | info:email | metrics:pageviews | metrics:clicks |
|---------|-----------|------------|-------------------|----------------|
| user123#2024-01-15 | John Doe | john@example.com | 150 | 25 |
| user123#2024-01-16 | John Doe | john@example.com | 200 | 30 |
| user456#2024-01-15 | Jane Smith | jane@example.com | 75 | 10 |

### Multi-Version Cells

Each cell can store multiple timestamped versions:

```
Row: "user123#2024-01-15"
Column: "info:status"
│
├── Timestamp: 1642262400 → Value: "active"
├── Timestamp: 1642348800 → Value: "inactive"
└── Timestamp: 1642435200 → Value: "active"
```

**Garbage Collection:**
- Keep last N versions
- Keep versions newer than X days
- Combination of both

---

## When to Use Bigtable

### ✅ Good Fit

**1. Large Scale:**
- >= 1 TB of data
- >= 300 GB with high-throughput needs

**2. High Throughput:**
- Millions of operations per second
- Low latency requirements (< 10ms)

**3. Time-Series Data:**
- IoT sensor data
- Financial market data
- Application metrics

**4. Time-Series Queries:**
- Recent data queries
- Range scans
- Sequential reads

**5. Append-Heavy Workloads:**
- Logs
- Event streams
- Clickstream data

### ❌ Not a Good Fit

**1. Small Data (<1 TB):**
Use Cloud SQL or Firestore instead

**2. Complex Transactions:**
No multi-row transactions
Use Cloud SQL or Spanner instead

**3. Complex Queries:**
No JOINs, GROUP BY, or aggregations
Use BigQuery instead

**4. Full Table Scans:**
Very expensive in Bigtable
Use BigQuery for analytics

**5. Frequently Changing Schema:**
Column families are relatively static
Use Firestore for flexible schema

---

## Instance Configuration

### Instance Types

**1. Production Instance:**
- Minimum 3 nodes
- SLA-backed
- Replication available
- For production workloads

**2. Development Instance:**
- Single node
- No SLA
- No replication
- For testing/development

### Create Instance

**Via Console:**
1. Go to **Bigtable** → **Create Instance**
2. Choose instance type
3. Configure:
   - Instance ID
   - Storage type (SSD/HDD)
   - Region/zones
   - Number of nodes
4. Click **Create**

**Via gcloud:**
```bash
# Create production instance with SSD
gcloud bigtable instances create my-instance \
  --display-name="My Bigtable Instance" \
  --cluster=my-cluster \
  --cluster-zone=us-central1-a \
  --cluster-num-nodes=3 \
  --cluster-storage-type=SSD

# Create development instance
gcloud bigtable instances create dev-instance \
  --display-name="Dev Instance" \
  --instance-type=DEVELOPMENT \
  --cluster=dev-cluster \
  --cluster-zone=us-central1-a \
  --cluster-storage-type=HDD
```

### Storage Types

**SSD (Default):**
- **Latency:** < 10ms (p99)
- **Cost:** $0.17/GB/month
- **Use Case:** Production, low-latency workloads

**HDD:**
- **Latency:** ~200ms (p99)
- **Cost:** $0.026/GB/month
- **Use Case:** Large batch processing, less latency-sensitive

### Replication

**Multi-Cluster Replication:**
```bash
# Add second cluster for replication
gcloud bigtable clusters create my-cluster-backup \
  --instance=my-instance \
  --zone=us-east1-b \
  --num-nodes=3 \
  --storage-type=SSD
```

**Benefits:**
- **High availability:** Automatic failover
- **Low latency:** Read from nearest cluster
- **Disaster recovery:** Data in multiple regions

**Consistency:** Eventual consistency across clusters

### Scaling

**Add Nodes (Linear Scaling):**
```bash
# Scale cluster to 6 nodes
gcloud bigtable clusters update my-cluster \
  --instance=my-instance \
  --num-nodes=6
```

**Performance:**
- Each node: ~10,000 QPS
- 3 nodes: ~30,000 QPS
- 10 nodes: ~100,000 QPS

**Autoscaling:**
```bash
# Enable autoscaling (3-10 nodes)
gcloud bigtable clusters update my-cluster \
  --instance=my-instance \
  --autoscaling-min-nodes=3 \
  --autoscaling-max-nodes=10 \
  --autoscaling-cpu-target=70
```

---

## Schema Design

### Row Key Design (Most Critical!)

**Goal:** Evenly distribute data and queries across nodes

#### Anti-Pattern: Sequential Keys

**❌ Bad:**
```
timestamp#user123
timestamp#user456
timestamp#user789
```

**Problem:** All new data goes to same tablet → **hotspot**

#### Pattern 1: Reverse Timestamp

**✅ Better:**
```
user123#reverse_timestamp
user456#reverse_timestamp
```

**Reverse Timestamp:**
```python
import time
reverse_timestamp = str(sys.maxsize - int(time.time() * 1000))
```

**Benefit:** Recent data spreads across tablets

#### Pattern 2: Field Promotion

**✅ Good:**
```
user_id#timestamp#event_type
```

**Benefit:**
- Queries by user are efficient
- Time-based queries within user are efficient

#### Pattern 3: Salting

**✅ Good for hot keys:**
```
{hash(user_id) % num_buckets}#{user_id}#timestamp
```

**Example:**
```
0#user123#1642262400
3#user123#1642348800
7#user456#1642262400
```

**Benefit:** Distributes hot keys across tablets

### Column Family Design

**Keep It Simple:**
- 1-10 column families (rarely more)
- Group by access pattern
- Same retention policy

**Example:**
```python
column_families = {
    "metadata": {},  # User profile info
    "events": {},    # User events
    "aggregates": {} # Pre-computed metrics
}
```

**Create Table with Column Families:**
```bash
cbt createtable my-table \
  families="metadata:maxversions=1,events:maxage=30d,aggregates:maxversions=5"
```

### Garbage Collection Policies

**Max Versions:**
```bash
# Keep only latest version
cbt createfamily my-table metadata maxversions=1

# Keep last 5 versions
cbt createfamily my-table events maxversions=5
```

**Max Age:**
```bash
# Keep data for 30 days
cbt createfamily my-table events maxage=30d

# Keep data for 1 year
cbt createfamily my-table historical maxage=365d
```

**Combine Both:**
```bash
# Keep last 3 versions AND max 90 days
cbt setgcpolicy my-table events maxversions=3 or maxage=90d
```

---

## Performance Optimization

### 1. Avoid Hotspotting

**Causes:**
- Sequential row keys
- Single-row high traffic
- Monotonically increasing timestamps

**Solutions:**
- Use reversed timestamps
- Salt hot keys
- Promote high-cardinality fields

### 2. Optimize Row Key for Queries

**Query Pattern:** Get user events from last 7 days
**Row Key:** `user_id#reverse_timestamp`

**Query:**
```python
# Efficient range scan
start_key = f"user123#{reverse_timestamp(now)}"
end_key = f"user123#{reverse_timestamp(7_days_ago)}"
rows = table.read_rows(start_key=start_key, end_key=end_key)
```

### 3. Use Appropriate Filters

**Row Filter:**
```python
from google.cloud import bigtable
from google.cloud.bigtable import row_filters

# Only rows matching regex
row_filter = row_filters.RowKeyRegexFilter(b'user123#.*')
rows = table.read_rows(filter_=row_filter)
```

**Column Filter:**
```python
# Only specific columns
column_filter = row_filters.ColumnQualifierRegexFilter(b'status|name')
rows = table.read_rows(filter_=column_filter)
```

**Value Filter:**
```python
# Only cells with specific value
value_filter = row_filters.ValueRegexFilter(b'active')
rows = table.read_rows(filter_=value_filter)
```

### 4. Batch Operations

**Batch Writes:**
```python
rows = []
for i in range(1000):
    row = table.direct_row(f"user{i}#timestamp")
    row.set_cell("cf1", "column1", "value1")
    rows.append(row)

# Write in batch
table.mutate_rows(rows)
```

**Benefit:** Reduces round trips, increases throughput

### 5. Connection Pooling

**Use Connection Pools:**
```python
from google.cloud.bigtable import Client

# Create client with connection pool
client = Client(project="my-project", admin=True)
instance = client.instance("my-instance")
table = instance.table("my-table")
```

---

## Operations

### Create Table

**Via cbt CLI:**
```bash
# Install cbt
gcloud components install cbt

# Configure cbt
echo "project = my-project" > ~/.cbtrc
echo "instance = my-instance" >> ~/.cbtrc

# Create table
cbt createtable my-table

# Create column families
cbt createfamily my-table cf1
cbt createfamily my-table cf2 maxversions=5
```

### Insert Data

**Via cbt:**
```bash
# Set cell value
cbt set my-table user123 cf1:name="John Doe"
cbt set my-table user123 cf1:email="john@example.com"
cbt set my-table user123 cf2:score=100
```

**Via Python:**
```python
from google.cloud import bigtable

client = bigtable.Client(project="my-project", admin=True)
instance = client.instance("my-instance")
table = instance.table("my-table")

row_key = "user123"
row = table.direct_row(row_key)
row.set_cell("cf1", "name", "John Doe")
row.set_cell("cf1", "email", "john@example.com")
row.set_cell("cf2", "score", "100")
row.commit()
```

### Read Data

**Via cbt:**
```bash
# Read single row
cbt read my-table prefix="user123"

# Read with count limit
cbt read my-table count=10

# Read specific columns
cbt read my-table columns="cf1:name,cf1:email"
```

**Via Python:**
```python
# Read single row
row = table.read_row("user123")
print(row.cells["cf1"][b"name"][0].value)

# Read multiple rows
rows = table.read_rows()
for row_key, row in rows:
    print(f"Row: {row_key}")
    for cf, columns in row.cells.items():
        for col, cells in columns.items():
            print(f"  {cf}:{col} = {cells[0].value}")
```

### Delete Data

**Delete Row:**
```bash
cbt deleterow my-table user123
```

**Delete Column:**
```bash
cbt deletecells my-table user123 cf1:name
```

**Delete Entire Table:**
```bash
cbt deletetable my-table
```

### Import/Export

**Export to Cloud Storage:**
```bash
# Create Dataflow job for export
gcloud dataflow jobs run bigtable-export \
  --gcs-location gs://dataflow-templates/latest/Cloud_Bigtable_to_GCS_Avro \
  --region us-central1 \
  --parameters \
bigtableProjectId=my-project,\
bigtableInstanceId=my-instance,\
bigtableTableId=my-table,\
destinationPath=gs://my-bucket/exports/,\
filenamePrefix=export-
```

**Import from Cloud Storage:**
```bash
gcloud dataflow jobs run bigtable-import \
  --gcs-location gs://dataflow-templates/latest/GCS_Avro_to_Cloud_Bigtable \
  --region us-central1 \
  --parameters \
bigtableProjectId=my-project,\
bigtableInstanceId=my-instance,\
bigtableTableId=my-table,\
inputFilePattern=gs://my-bucket/exports/*.avro
```

---

## Security

### IAM Roles

| Role | Permissions | Use Case |
|------|------------|----------|
| `roles/bigtable.admin` | Full control | Database administrators |
| `roles/bigtable.user` | Read/write data | Applications |
| `roles/bigtable.reader` | Read-only access | Analytics, reporting |
| `roles/bigtable.viewer` | View metadata | Auditors |

**Grant Access:**
```bash
gcloud bigtable instances add-iam-policy-binding my-instance \
  --member=user:developer@example.com \
  --role=roles/bigtable.user
```

### Encryption

**At Rest:**
- Automatic encryption (Google-managed keys)
- Optional: Customer-managed encryption keys (CMEK)

**Enable CMEK:**
```bash
gcloud bigtable instances update my-instance \
  --cluster=my-cluster \
  --kms-key=projects/my-project/locations/us-central1/keyRings/my-ring/cryptoKeys/my-key
```

**In Transit:**
- All data encrypted via TLS

### VPC Service Controls

**Protect Bigtable from exfiltration:**
```bash
# Must use VPC Service Controls in Console
# Create perimeter around Bigtable instances
```

---

## Monitoring

### Key Metrics

**CPU Utilization:**
- **Target:** < 70% for autoscaling
- **Alert:** > 90%

**Storage Utilization:**
- **Target:** < 70% of capacity
- **SSD:** Cost increases, consider HDD or cleanup

**Latency:**
- **SSD:** < 10ms (p99)
- **HDD:** < 200ms (p99)

### View Metrics

**Via Console:**
1. **Bigtable** → **Instances** → **[Instance]** → **Monitoring**
2. View:
   - CPU usage
   - Storage usage
   - Request rates
   - Error rates

**Via Cloud Monitoring:**
```bash
# Install monitoring agent (if needed)
# Metrics automatically exported to Cloud Monitoring

# Create alert
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="Bigtable High CPU" \
  --condition-display-name="CPU > 90%" \
  --condition-threshold-value=0.9 \
  --condition-threshold-duration=300s
```

### Enable Key Visualizer

**What is Key Visualizer?**
Visual tool to analyze Bigtable usage patterns and identify hotspots.

**Enable:**
1. **Bigtable** → **Instances** → **[Instance]** → **Tables** → **[Table]**
2. Click **Key Visualizer** tab
3. View heatmap showing:
   - Hot keys (red areas)
   - Balanced distribution (green)

---

## Cost Optimization

### 1. Right-Size Nodes

**Monitor CPU:**
- < 50% CPU: Over-provisioned, reduce nodes
- > 90% CPU: Under-provisioned, add nodes

**Autoscaling:**
```bash
gcloud bigtable clusters update my-cluster \
  --instance=my-instance \
  --autoscaling-min-nodes=3 \
  --autoscaling-max-nodes=10 \
  --autoscaling-cpu-target=70
```

### 2. Use HDD for Cold Data

**Storage Costs:**
- SSD: $0.17/GB/month
- HDD: $0.026/GB/month (6.5x cheaper)

**Use HDD When:**
- Batch processing
- Less latency-sensitive
- Large datasets (>10 TB)

### 3. Implement Data Retention

**Automatic Cleanup:**
```bash
# Delete data older than 30 days
cbt setgcpolicy my-table events maxage=30d
```

### 4. Use Development Instances for Testing

**Development Instance:**
- Single node
- Much cheaper
- No SLA (acceptable for dev/test)

---

## Migration

### From HBase to Bigtable

**Compatibility:**
- Bigtable supports HBase API
- Most HBase applications work with minimal changes

**Migration Steps:**

**1. Export HBase Data:**
```bash
# Use HBase snapshot
hbase snapshot create mySnapshot myTable

# Export to Cloud Storage
hadoop distcp \
  hbase.rootdir/archive/data/default/myTable/.hbase-snapshot/mySnapshot \
  gs://my-bucket/hbase-export/
```

**2. Import to Bigtable:**
```bash
gcloud dataflow jobs run hbase-import \
  --gcs-location gs://dataflow-templates/latest/GCS_SequenceFile_to_Cloud_Bigtable \
  --region us-central1 \
  --parameters \
bigtableProject=my-project,\
bigtableInstanceId=my-instance,\
bigtableTableId=my-table,\
sourcePattern=gs://my-bucket/hbase-export/*
```

**3. Update Application:**
```java
// Change HBase connection to Bigtable
Configuration config = BigtableConfiguration.configure(projectId, instanceId);
Connection connection = ConnectionFactory.createConnection(config);
```

### From Cassandra to Bigtable

**Differences:**
- No CQL support
- Different data model
- Schema redesign needed

**Migration:**
1. Export Cassandra to CSV/Avro
2. Transform data for Bigtable schema
3. Import using Dataflow

---

## Best Practices

### 1. Row Key Design

**✅ Do:**
- Distribute writes evenly
- Optimize for read patterns
- Use field promotion for common queries
- Salt hot keys

**❌ Don't:**
- Use sequential keys (timestamps first)
- Use monotonically increasing IDs
- Create hot keys

### 2. Column Families

**✅ Do:**
- Keep to minimum (typically 1-10)
- Group by access patterns
- Set appropriate GC policies

**❌ Don't:**
- Create hundreds of column families
- Mix different retention needs

### 3. Sizing

**✅ Do:**
- Start with >= 1 TB data or high throughput
- Use 3+ nodes for production
- Enable autoscaling

**❌ Don't:**
- Use for small datasets (< 300 GB)
- Under-provision nodes (causes latency)

### 4. Operations

**✅ Do:**
- Use batch operations
- Implement connection pooling
- Monitor Key Visualizer
- Set up alerting

**❌ Don't:**
- Do full table scans
- Use single-row operations in loops
- Ignore hotspots

---

## Exam Tips

### ACE Exam Focus

**1. When to Use Bigtable:**
- Large-scale time-series data
- IoT sensor data
- High-throughput requirements (> 10K QPS)
- Low latency needs (< 10ms)

**2. Common Commands:**
```bash
# Create instance
gcloud bigtable instances create INSTANCE_ID --cluster=CLUSTER_ID

# Create table
cbt createtable TABLE_NAME

# Insert data
cbt set TABLE ROW FAMILY:COLUMN=VALUE

# Read data
cbt read TABLE
```

**3. Instance Types:**
- **Production:** 3+ nodes, SLA-backed
- **Development:** 1 node, no SLA, cheaper

**4. Storage:**
- **SSD:** Low latency (< 10ms)
- **HDD:** Cost-effective, higher latency

### PCA Exam Focus

**1. Architecture Decisions:**

**Use Bigtable When:**
- Time-series data at massive scale
- High write throughput
- Low latency reads/writes
- HBase migration

**Don't Use Bigtable When:**
- Small dataset (< 1 TB)
- Complex queries/JOINs
- Strong ACID transactions

**2. Schema Design:**
- Row key design critical for performance
- Avoid hotspotting with proper key design
- Use field promotion for query optimization

**3. Scaling:**
- Linear scaling with nodes
- Each node ~10K QPS
- Autoscaling for variable load

**4. Replication:**
- Multi-cluster replication for HA
- Eventual consistency
- Read from nearest cluster

**5. Cost Optimization:**
- Use HDD for cold storage
- Right-size nodes (autoscaling)
- Implement data retention policies

### Exam Scenarios

**Scenario:** "Store IoT sensor data from millions of devices with sub-10ms query latency"
**Solution:** Cloud Bigtable with SSD storage

**Scenario:** "Migrate existing HBase cluster to GCP"
**Solution:** Cloud Bigtable (HBase API compatible)

**Scenario:** "500 GB database with complex analytical queries"
**Solution:** Cloud SQL or BigQuery (NOT Bigtable)

**Scenario:** "Prevent hotspotting in time-series data"
**Solution:** Use reverse timestamp or field promotion in row key

**Scenario:** "High availability across regions"
**Solution:** Multi-cluster replication in different regions

---

## Quick Reference

```bash
# Instance Management
gcloud bigtable instances create my-instance --cluster=my-cluster --cluster-zone=us-central1-a
gcloud bigtable instances list
gcloud bigtable instances delete my-instance

# Cluster Management
gcloud bigtable clusters create my-cluster --instance=my-instance --zone=us-central1-a
gcloud bigtable clusters update my-cluster --instance=my-instance --num-nodes=6

# Table Operations (cbt)
cbt createtable my-table
cbt createfamily my-table cf1
cbt ls                         # List tables
cbt set TABLE ROW CF:COL=VAL  # Insert
cbt read TABLE                 # Read
cbt deletetable my-table       # Delete table
```

---

**End of Guide** - Master Bigtable for massive-scale NoSQL workloads! 🚀
