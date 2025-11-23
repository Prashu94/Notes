# Google Cloud Storage & Databases Guide (ACE - Associate Cloud Engineer)

## 1. Cloud Storage (Object Storage)

### 1.1. Storage Classes
*   **Standard**: Hot data, frequently accessed. Best for serving web content, streaming videos.
*   **Nearline**: Accessed < once/month. 30-day minimum storage duration. Best for backups.
*   **Coldline**: Accessed < once/quarter. 90-day minimum. Best for DR.
*   **Archive**: Accessed < once/year. 365-day minimum. Best for regulatory compliance.
*   **Autoclass**: Automatically transitions objects to colder classes based on access patterns. Useful when access patterns are unpredictable.

### 1.2. Operations & Lifecycle Management
*   **Versioning**: Protects against accidental overwrites/deletes.
*   **Lifecycle Rules**: Automate transitions (e.g., "Move to Coldline after 30 days", "Delete after 365 days").
*   **Soft Delete**: Enabled by default (7 days). Protects against accidental bucket/object deletion.

```bash
# Create a bucket (Standard class, us-central1)
gcloud storage buckets create gs://my-bucket --location=us-central1 --default-storage-class=STANDARD

# Enable Versioning
gcloud storage buckets update gs://my-bucket --versioning

# Copy files (Parallel upload)
gcloud storage cp -r ./local-folder gs://my-bucket
```

---

## 2. Cloud SQL (Relational Database)

### 2.1. Engines & Editions
*   **Engines**: MySQL, PostgreSQL, SQL Server.
*   **Editions**:
    *   **Enterprise**: General purpose.
    *   **Enterprise Plus**: High performance (Data Cache), 99.99% SLA, sub-second maintenance downtime.

### 2.2. Operations
*   **Connecting**:
    *   **Public IP**: Requires authorized networks (allowlisting IPs).
    *   **Private IP**: Requires Private Service Access (VPC Peering).
    *   **Cloud SQL Auth Proxy**: Secure connection without allowlisting IPs. Recommended for development/production.

```bash
# Create a MySQL instance
gcloud sql instances create my-instance \
    --database-version=MYSQL_8_0 \
    --tier=db-f1-micro \
    --region=us-central1

# Connect using the Auth Proxy (Download binary first)
./cloud-sql-proxy my-project:us-central1:my-instance
```

---

## 3. Cloud Spanner (Global Relational)

### 3.1. Key Features
*   **Global Scale**: Horizontal scaling for relational data.
*   **Strong Consistency**: External consistency (TrueTime).
*   **Schema**: Relational (SQL).

### 3.2. Operations
*   **Instance Config**: Regional (e.g., `regional-us-central1`) or Multi-Regional (e.g., `nam3`).
*   **Processing Units (PU)**: Granular scaling (100 PUs = 1/10th of a node).

```bash
# Create a Spanner instance
gcloud spanner instances create my-spanner \
    --config=regional-us-central1 \
    --description="My Spanner Instance" \
    --nodes=1
```

---

## 4. Firestore (NoSQL Document)

### 4.1. Modes
*   **Native Mode**: For mobile/web apps. Supports real-time updates, offline sync.
*   **Datastore Mode**: For server-side apps. High throughput, no real-time.

### 4.2. Data Model
*   **Collections** contain **Documents**. Documents contain **Fields** (and sub-collections).
*   **Indexing**: Automatic for single fields. Composite indexes required for complex queries.

---

## 5. Cloud Bigtable (NoSQL Wide-Column)

### 5.1. Key Features
*   **High Throughput**: Millions of reads/writes per second.
*   **Low Latency**: Sub-millisecond.
*   **Use Case**: IoT data, AdTech, FinTech, Time-series.

### 5.2. Storage Types
*   **SSD**: High performance, higher cost.
*   **HDD**: Lower cost, higher latency. Good for batch analytics.

```bash
# Create a Bigtable instance
gcloud bigtable instances create my-bigtable \
    --cluster=my-cluster \
    --cluster-zone=us-central1-a \
    --display-name="My Bigtable" \
    --instance-type=PRODUCTION
```

---

## 6. ACE Exam Cheat Sheet

| Service | Use Case | Key Command/Flag |
| :--- | :--- | :--- |
| **Cloud Storage** | Unstructured data (Images, Logs). | `gcloud storage` (New CLI), `gsutil` (Legacy). |
| **Cloud SQL** | Relational, Regional (< 30TB). | `--availability-type=REGIONAL` (for HA). |
| **Spanner** | Relational, Global, Horizontal Scale (> 30TB). | `gcloud spanner instances update --nodes=5` |
| **Firestore** | NoSQL, Mobile/Web, Real-time. | `gcloud firestore databases create` |
| **Bigtable** | NoSQL, High Throughput, Flat schema. | `cbt` (CLI tool for data operations). |
| **Memorystore** | In-memory cache (Redis/Memcached). | `gcloud redis instances create` |
