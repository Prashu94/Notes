# GCP Storage & Database Services - Detailed Mindmap & Design

## 1. Object Storage
*   **Cloud Storage (GCS)** - *Unstructured Data*
    *   **Storage Classes**
        *   **Standard**: Hot data. Frequent access. No retrieval fee. Web content, streaming.
        *   **Nearline**: Once/month access. 30-day min storage duration. Backups, long-tail content.
        *   **Coldline**: Once/quarter access. 90-day min storage duration. DR, older backups.
        *   **Archive**: Once/year access. 365-day min storage duration. Compliance, tape replacement.
        *   *Autoclass*: Automatically moves objects between classes based on access pattern.
    *   **Location Types**
        *   *Region*: Lowest latency, single region availability.
        *   *Dual-region*: High availability (99.99%), geo-redundancy (2 specific regions).
        *   *Multi-region*: Highest availability (99.995%), geo-redundancy (large area like US, EU).
    *   **Features**
        *   **Versioning**: Protects against overwrites/deletes. Keeps history.
        *   **Lifecycle Management**: Rules to Delete or Downgrade class (e.g., "Move to Coldline after 30 days").
        *   **Object Lock (Retention Policy)**: WORM (Write Once Read Many). Compliance.
        *   **Encryption**: Google-managed (default), CMEK (Cloud KMS), CSEK (Customer supplied).
    *   **Access Control**
        *   **IAM**: Bucket-level permissions (Recommended). `roles/storage.objectViewer`.
        *   **ACLs**: Object-level permissions (Legacy, fine-grained).
        *   **Signed URLs**: Temporary access for users without Google account.
    *   **Transfer Services**
        *   *Storage Transfer Service*: Batch transfer from AWS S3, Azure, HTTP, or On-prem.
        *   *Transfer Appliance*: Hardware for petabyte-scale offline transfer.

## 2. Relational Databases (SQL)
*   **Cloud SQL** - *Regional RDBMS*
    *   **Engines**: MySQL, PostgreSQL, SQL Server.
    *   **Capacity**: Up to ~64 TB storage. Vertical scaling (Machine type).
    *   **Architecture**:
        *   *Primary*: Read/Write.
        *   *Read Replicas*: Read-only. Horizontal scaling for reads. Cross-region supported.
        *   *High Availability (HA)*: Active/Standby in different zones. Synchronous replication. Auto-failover.
    *   **Backups**: Automated (daily) + On-demand. Point-in-time recovery (PITR) via binary logs.
    *   **Connectivity**: Public IP (Authorized networks) or Private IP (VPC Peering/PSA). Cloud SQL Auth Proxy (Secure).

*   **Cloud Spanner** - *Global RDBMS*
    *   **Key Features**:
        *   Global scale (Horizontal).
        *   Strong Consistency (External Consistency via TrueTime).
        *   99.999% SLA (Multi-region).
        *   SQL (GoogleSQL & PostgreSQL dialects).
    *   **Architecture**:
        *   *Instance*: Regional or Multi-regional config.
        *   *Nodes/Processing Units*: Compute capacity.
        *   *Splits*: Data automatically sharded by Primary Key.
    *   **Use Cases**: Global inventory, Financial ledgers, Gaming, High-scale relational data (>64TB).

## 3. NoSQL Databases
*   **Cloud Firestore** - *Document Store*
    *   **Modes**:
        *   *Native Mode*: Real-time sync, Offline support, Mobile/Web SDKs.
        *   *Datastore Mode*: Server-side focus, High throughput, No real-time.
    *   **Data Model**: Collection -> Document -> Subcollection. Schemaless.
    *   **Querying**:
        *   Shallow queries (no joins).
        *   Requires Composite Indexes for multi-field filters.
        *   Strong consistency.
    *   **Scaling**: Automatic. Zero to millions of QPS.

*   **Cloud Bigtable** - *Wide-Column Store*
    *   **Key Features**:
        *   HBase compatible.
        *   High throughput (Millions of QPS).
        *   Low latency (<10ms).
        *   Petabyte scale.
    *   **Data Model**:
        *   *Row Key*: Critical design choice. Sorted lexicographically. Avoid hotspots (e.g., don't use sequential IDs or timestamps at start).
        *   *Column Families*: Group columns for locality.
    *   **Architecture**:
        *   Separation of Compute (Nodes) and Storage (Colossus).
        *   *Replication*: Multi-cluster routing (HA).
    *   **Use Cases**: IoT, AdTech, FinTech, Time-series, Personalization.

*   **Cloud Memorystore** - *In-Memory Store*
    *   **Engines**: Redis, Memcached.
    *   **Use Cases**: Caching, Session store, Gaming leaderboards.
    *   **Tiers**: Basic (No HA), Standard (HA with replica).

## 4. Analytical Databases
*   **BigQuery** - *Data Warehouse*
    *   **Architecture**: Serverless. Separation of Storage and Compute (Slots).
    *   **Storage**:
        *   *Active*: Modified in last 90 days.
        *   *Long-term*: No mod for 90 days (50% cheaper).
    *   **Optimization**:
        *   **Partitioning**: Divide table by Date/Time or Integer Range. Reduces cost (scans less data).
        *   **Clustering**: Sort data within partitions. Improves filter/agg performance.
    *   **Ingestion**:
        *   *Batch*: Load jobs (Free).
        *   *Streaming*: Insert API (Paid).
    *   **Features**: BigQuery ML, BI Engine (In-memory), Omni (Multi-cloud).

---

## 🧠 Design Decision Guide: Storage

| Feature | Cloud Storage | Cloud SQL | Spanner | Firestore | Bigtable | BigQuery |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Type** | Object (Blob) | Relational (SQL) | Relational (SQL) | NoSQL (Doc) | NoSQL (Wide) | Warehouse (SQL) |
| **Scale** | Infinite | ~64 TB | Petabytes | Petabytes | Petabytes | Petabytes |
| **Consistency** | Strong | Strong | Strong (Global) | Strong | Eventual/Strong | Strong |
| **Transaction** | No | ACID | ACID | ACID | Row-atomicity | ACID |
| **Workload** | Unstructured | OLTP (Regional) | OLTP (Global) | Mobile/Web | High Write/Read | OLAP (Analytics) |
| **Key Use** | Images, Backups | CMS, ERP, CRM | Global Ledger | User Profiles | IoT, AdTech | BI, Reporting |

### 🔑 Key Exam Rules
1.  **"Global SQL"** or **"Horizontal Scale SQL"** -> **Spanner**.
2.  **"Mobile App"** or **"Offline Sync"** -> **Firestore**.
3.  **"High Throughput Writes"** or **"IoT"** or **"HBase"** -> **Bigtable**.
4.  **"Analytics"** or **"SQL Warehouse"** -> **BigQuery**.
5.  **"Lift & Shift MySQL/Postgres"** -> **Cloud SQL**.
6.  **"Files"** or **"Images"** -> **Cloud Storage**.
