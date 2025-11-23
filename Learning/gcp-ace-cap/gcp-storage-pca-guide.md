# Google Cloud Storage & Databases Guide (PCA - Professional Cloud Architect)

## 1. Database Decision Tree (The "Flowchart")

### 1.1. The Primary Questions
1.  **Is the data structured?**
    *   **No (Files, Blobs)** -> **Cloud Storage**.
    *   **Yes** -> Go to 2.
2.  **Is the workload Analytics (OLAP) or Transactional (OLTP)?**
    *   **Analytics** -> **BigQuery** (Data Warehouse).
    *   **Transactional** -> Go to 3.
3.  **Is the data Relational (SQL)?**
    *   **Yes** -> Go to 4.
    *   **No** -> Go to 5.
4.  **Relational Needs:**
    *   **Global Scale / Horizontal Scaling?** -> **Cloud Spanner**.
    *   **Regional / Vertical Scaling (< 30TB)?** -> **Cloud SQL**.
    *   **Legacy Oracle/SQL Server (Lift & Shift)?** -> **Bare Metal Solution** (if strict hardware reqs) or **Cloud SQL**.
5.  **NoSQL Needs:**
    *   **Mobile/Web App / Real-time Sync?** -> **Firestore**.
    *   **High Throughput / Low Latency (IoT, AdTech)?** -> **Cloud Bigtable**.
    *   **In-memory Cache?** -> **Memorystore**.

---

## 2. Relational Database Architecture

### 2.1. Cloud SQL Architecture
*   **High Availability (HA)**:
    *   **Regional HA**: Primary in Zone A, Standby in Zone B. Synchronous replication.
    *   **Failover**: Automatic. IP address remains the same.
*   **Read Replicas**:
    *   **Purpose**: Offload read traffic. Asynchronous replication.
    *   **Cross-Region**: Can be used for Disaster Recovery (promote replica to primary).
*   **Maintenance**:
    *   **Enterprise Plus**: Sub-second downtime (uses proxy layer to hold connections).

### 2.2. Cloud Spanner Architecture
*   **TrueTime**: Uses atomic clocks/GPS to guarantee external consistency globally.
*   **Replication**:
    *   **Regional**: 3 replicas in 3 zones (RW/RW/RW).
    *   **Multi-Region**: 5 replicas (2 RW regions, 1 Witness region). 99.999% SLA.
*   **Sharding**: Automatic. No manual sharding required.

---

## 3. NoSQL Database Architecture

### 3.1. Cloud Bigtable Schema Design
*   **Row Key**: The *most critical* design decision. Determines data distribution.
    *   **Anti-Pattern**: Sequential IDs (Timestamp, 1, 2, 3) -> Causes "Hotspotting" (all writes go to one node).
    *   **Best Practice**: Reverse Timestamp, Hashed ID, or `TenantID#Timestamp`.
*   **Storage**: Separation of compute (Nodes) and storage (Colossus). Resizing cluster is instant (no data movement).

### 3.2. Firestore
*   **Consistency**: Strong consistency (unlike eventual consistency in many NoSQL DBs).
*   **Limits**: 1 write/sec per document. (Design implication: Don't use a single document for a global counter).

---

## 4. Data Migration & Lifecycle

### 4.1. Migration Tools
*   **Database Migration Service (DMS)**:
    *   **Use Case**: Homogeneous migrations (MySQL -> Cloud SQL MySQL, PG -> PG).
    *   **Method**: Serverless, continuous replication.
*   **Datastream**:
    *   **Use Case**: Change Data Capture (CDC). Replicate data from Oracle/MySQL to BigQuery/Spanner.
    *   **Method**: Serverless, reads transaction logs.

### 4.2. Cloud Storage Lifecycle Design
*   **Cost Optimization**:
    *   Use **Autoclass** for unpredictable workloads.
    *   Use **Lifecycle Rules** for predictable logs (e.g., "Logs -> Coldline after 30 days -> Delete after 1 year").
*   **Compliance**:
    *   **Object Versioning**: Protect against ransomware/accidental delete.
    *   **Retention Policy (Bucket Lock)**: WORM (Write Once Read Many). "Compliance Mode" prevents deletion even by admins.

---

## 5. PCA Scenarios

### Scenario 1: Global Gaming Leaderboard
*   **Requirement**: Global scale, strong consistency, relational data.
*   **Solution**: **Cloud Spanner**. (Cloud SQL cannot scale writes globally).

### Scenario 2: IoT Sensor Data
*   **Requirement**: Millions of writes/sec, time-series data, analytics later.
*   **Solution**: **Cloud Bigtable**. (Firestore is too expensive/slow for this volume; SQL cannot handle the throughput).

### Scenario 3: E-commerce Product Catalog
*   **Requirement**: Flexible schema, high read availability, product attributes vary.
*   **Solution**: **Firestore** (Document model fits product catalogs well).

### Scenario 4: Financial Transaction History
*   **Requirement**: Immutable logs, 7-year retention, strict regulatory compliance.
*   **Solution**: **Cloud Storage (Archive Class)** with **Bucket Lock** (Retention Policy).
