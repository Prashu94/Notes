# Google Cloud Spanner - Associate Cloud Engineer (ACE) Comprehensive Guide

## Table of Contents
1. [Overview](#overview)
2. [Core Concepts](#core-concepts)
3. [Instance Configuration](#instance-configuration)
4. [Database Creation & Management](#database-creation--management)
5. [Schema Design Basics](#schema-design-basics)
6. [Data Operations](#data-operations)
7. [Access Control & Security](#access-control--security)
8. [Backup & Recovery](#backup--recovery)
9. [Monitoring & Troubleshooting](#monitoring--troubleshooting)
10. [ACE Exam Tips](#ace-exam-tips)

---

## Overview

**Cloud Spanner** is Google's globally-distributed, horizontally scalable, relational database service that provides:
- **Strong consistency** across regions
- **High availability** (99.999% SLA)
- **Automatic sharding** and replication
- **SQL support** (GoogleSQL and PostgreSQL dialects)
- **Horizontal scalability** without re-architecture

### Key Characteristics

| Feature | Description |
|---------|-------------|
| **Consistency** | Strongconsistency with external consistency guarantees |
| **Availability** | Up to 99.999% (five 9s) for multi-region configurations |
| **Scalability** | Horizontal scale from gigabytes to petabytes |
| **Global Distribution** | Multi-region replication with TrueTime technology |
| **ACID Transactions** | Full ACID compliance for relational data |

### When to Use Cloud Spanner

**Best For:**
- Global applications requiring strong consistency
- Financial services (banking, trading, payments)
- Gaming (player profiles, leaderboards, inventory)
- Retail (omni-channel inventory, order management)
- Applications that outgrow traditional RDBMS

**Consider Alternatives:**
- **Cloud SQL:** For regional applications, lower cost (<500GB)
- **Cloud Firestore:** For document-based NoSQL workloads
- **BigQuery:** For analytics and data warehousing
- **Bigtable:** For high-throughput NoSQL (eventual consistency okay)

---

## Core Concepts

### Architecture Components

```
Organization
└── Project
    └── Spanner Instance (compute resources)
        └── Database (schema + data)
            ├── Tables
            ├── Indexes
            └── Schemas
```

### Instance

A Spanner **instance** provides compute and storage resources:
- Allocated in **processing units** or **nodes**
  - 1 node = 1000 processing units
  - 1 node provides: 2 TiB storage, 10,000 QPS reads, 2,000 QPS writes
- Regional or multi-regional configuration
- Scales dynamically without downtime

### Database

A **database** contains your schema and data:
- Multiple databases per instance
- Each database has tables, indexes, views
- Supports both GoogleSQL and PostgreSQL dialects

### Splits

Spanner automatically partitions data into **splits**:
- Each split ≈ 8 GiB of data or less
- Distributed across multiple servers
- Load-based splitting for hotspot prevention
- Transparent to applications

---

## Instance Configuration

### Instance Configuration Types

| Configuration | Regions | Availability | Use Case |
|---------------|---------|--------------|----------|
| **Regional** | 1 region (3 zones) | 99.99% | Regional apps, cost-sensitive |
| **Dual-Region** | 2 regions | 99.99% | Regional redundancy |
| **Multi-Region** | 3+ regions | 99.999% | Global apps, highest availability |

**Popular Configurations:**
- `us-central1` - Single region (Iowa)
- `nam3` - Multi-region (US East, Central, West)
- `eur3` - Multi-region (Belgium, Netherlands, Germany)
- `asia1` - Multi-region (Tokyo, Osaka, Taiwan)

### Creating an Instance

**Console:**
1. Navigate to **Spanner** > **Create Instance**
2. Enter instance ID (e.g., `my-spanner-instance`)
3. Choose instance name
4. Select configuration (regional/multi-region)
5. Set processing units/nodes
6. Click **Create**

**gcloud:**
```bash
# Create regional instance with 1000 processing units (1 node)
gcloud spanner instances create my-instance \
    --config=regional-us-central1 \
    --description="My Spanner Instance" \
    --processing-units=1000

# Create multi-region instance with 3 nodes
gcloud spanner instances create my-global-instance \
    --config=nam3 \
    --description="Global Instance" \
    --nodes=3
```

### Scaling Instances

**Manual Scaling:**
```bash
# Scale up to 2000 processing units
gcloud spanner instances update my-instance \
    --processing-units=2000

# Scale down to 500 processing units
gcloud spanner instances update my-instance \
    --processing-units=500
```

**Autoscaling (Recommended):**
```bash
# Enable autoscaling with min/max processing units
gcloud spanner instances update my-instance \
    --autoscaling-min-processing-units=1000 \
    --autoscaling-max-processing-units=5000 \
    --autoscaling-high-priority-cpu-target=65 \
    --autoscaling-storage-target=95
```

---

## Database Creation & Management

### Creating a Database

**gcloud:**
```bash
# Create database with GoogleSQL dialect
gcloud spanner databases create my-database \
    --instance=my-instance

# Create database with PostgreSQL dialect
gcloud spanner databases create my-pg-database \
    --instance=my-instance \
    --database-dialect=POSTGRESQL
```

**Console:**
1. Select instance
2. Click **Create Database**
3. Enter database name
4. Choose dialect (GoogleSQL or PostgreSQL)
5. Optionally add DDL statements
6. Click **Create**

### Database Dialects

| Dialect | Description | Use Case |
|---------|-------------|----------|
| **GoogleSQL** | Google's SQL dialect, Spanner-optimized | New applications, Google ecosystem |
| **PostgreSQL** | PostgreSQL-compatible interface | Migrating from PostgreSQL |

### Executing SQL Queries

**Console (Spanner Studio):**
1. Navigate to **Database** > **Spanner Studio**
2. Write SQL query
3. Click **Run**

**gcloud:**
```bash
# Execute query
gcloud spanner databases execute-sql my-database \
    --instance=my-instance \
    --sql="SELECT * FROM Users LIMIT 10"

# Execute DML
gcloud spanner databases execute-sql my-database \
    --instance=my-instance \
    --sql="INSERT INTO Users (UserId, Name, Email) VALUES (1, 'John Doe', 'john@example.com')"
```

---

## Schema Design Basics

### Creating Tables

**GoogleSQL:**
```sql
CREATE TABLE Users (
    UserId INT64 NOT NULL,
    Name STRING(100),
    Email STRING(255),
    CreatedAt TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp=true),
    LastLogin TIMESTAMP
) PRIMARY KEY (UserId);
```

**PostgreSQL:**
```sql
CREATE TABLE users (
    user_id BIGINT NOT NULL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMPTZ
);
```

### Primary Key Best Practices

**❌ Avoid Monotonic Keys (Hotspots):**
```sql
-- Bad: Sequential timestamps create hotspots
CREATE TABLE UserAccessLogs (
    Timestamp TIMESTAMP NOT NULL,
    UserId INT64,
    Action STRING(50)
) PRIMARY KEY (Timestamp, UserId);
```

**✅ Use UUIDs or Composite Keys:**
```sql
-- Good: UUID prevents hotspots
CREATE TABLE UserAccessLogs (
    LogId STRING(36) NOT NULL DEFAULT (GENERATE_UUID()),
    Timestamp TIMESTAMP NOT NULL,
    UserId INT64,
    Action STRING(50)
) PRIMARY KEY (LogId);

-- Good: Swap key order (UserId first)
CREATE TABLE UserAccessLogs (
    UserId INT64 NOT NULL,
    Timestamp TIMESTAMP NOT NULL,
    Action STRING(50)
) PRIMARY KEY (UserId, Timestamp);
```

### Secondary Indexes

```sql
-- Create index for faster lookups by Email
CREATE INDEX UsersByEmail ON Users(Email);

-- Create unique index
CREATE UNIQUE INDEX UsersByEmail ON Users(Email);

-- Interleaved index (stored with parent table)
CREATE INDEX UsersByName ON Users(Name) INTERLEAVE IN Users;

-- Covering index (includes additional columns)
CREATE INDEX UsersByEmailWithName ON Users(Email) STORING (Name);
```

### Interleaved Tables (Parent-Child Relationships)

```sql
-- Parent table
CREATE TABLE Albums (
    SingerId INT64 NOT NULL,
    AlbumId INT64 NOT NULL,
    AlbumTitle STRING(100),
) PRIMARY KEY (SingerId, AlbumId);

-- Child table interleaved in parent
CREATE TABLE Songs (
    SingerId INT64 NOT NULL,
    AlbumId INT64 NOT NULL,
    SongId INT64 NOT NULL,
    SongTitle STRING(100),
    Duration INT64,
) PRIMARY KEY (SingerId, AlbumId, SongId),
  INTERLEAVE IN PARENT Albums ON DELETE CASCADE;
```

**Benefits:**
- Co-locates related rows
- Faster reads for parent-child queries
- Cascading deletes

---

## Data Operations

### Inserting Data

**Single Insert:**
```sql
INSERT INTO Users (UserId, Name, Email)
VALUES (1, 'Alice', 'alice@example.com');
```

**Bulk Insert:**
```sql
INSERT INTO Users (UserId, Name, Email) VALUES
    (1, 'Alice', 'alice@example.com'),
    (2, 'Bob', 'bob@example.com'),
    (3, 'Charlie', 'charlie@example.com');
```

**gcloud:**
```bash
gcloud spanner databases execute-sql my-database \
    --instance=my-instance \
    --sql="INSERT INTO Users (UserId, Name, Email) VALUES (1, 'Alice', 'alice@example.com')"
```

### Updating Data

```sql
-- Update single row
UPDATE Users SET Name = 'Alice Smith' WHERE UserId = 1;

-- Update multiple rows
UPDATE Users SET LastLogin = CURRENT_TIMESTAMP() WHERE Email LIKE '%@example.com';
```

### Deleting Data

```sql
-- Delete single row
DELETE FROM Users WHERE UserId = 1;

-- Delete multiple rows
DELETE FROM Users WHERE CreatedAt < TIMESTAMP('2020-01-01T00:00:00Z');
```

### Querying Data

```sql
-- Simple SELECT
SELECT * FROM Users WHERE UserId = 1;

-- JOIN
SELECT u.Name, a.AlbumTitle, s.SongTitle
FROM Users u
JOIN Albums a ON u.UserId = a.SingerId
JOIN Songs s ON a.SingerId = s.SingerId AND a.AlbumId = s.AlbumId
WHERE u.UserId = 1;

-- Aggregation
SELECT COUNT(*) as TotalUsers FROM Users;

-- Ordering and Limiting
SELECT * FROM Users ORDER BY CreatedAt DESC LIMIT 10;
```

### Transactions

**Read-Write Transaction:**
```sql
BEGIN TRANSACTION;
UPDATE Accounts SET Balance = Balance - 100 WHERE AccountId = 1;
UPDATE Accounts SET Balance = Balance + 100 WHERE AccountId = 2;
COMMIT TRANSACTION;
```

**Read-Only Transaction (Strongly Consistent):**
```sql
-- Use read-only transaction for consistency across multiple reads
SELECT * FROM Users WHERE UserId IN (1, 2, 3);
```

---

## Access Control & Security

### IAM Roles

| Role | Permissions | Use Case |
|------|-------------|----------|
| **roles/spanner.admin** | Full access to instances and databases | Administrators |
| **roles/spanner.databaseAdmin** | Manage databases, schemas, data | Database admins |
| **roles/spanner.databaseUser** | Read/write data (no schema changes) | Application services |
| **roles/spanner.databaseReader** | Read-only access | Reporting, analytics |
| **roles/spanner.viewer** | View metadata (no data access) | Auditors |

### Granting Access

**Console:**
1. Navigate to **IAM & Admin** > **IAM**
2. Click **Grant Access**
3. Enter principal (user/service account)
4. Select role (e.g., `Spanner Database User`)
5. Click **Save**

**gcloud:**
```bash
# Grant database user role to service account
gcloud spanner databases add-iam-policy-binding my-database \
    --instance=my-instance \
    --member=serviceAccount:app@project.iam.gserviceaccount.com \
    --role=roles/spanner.databaseUser

# Grant database reader role to user
gcloud spanner databases add-iam-policy-binding my-database \
    --instance=my-instance \
    --member=user:analyst@example.com \
    --role=roles/spanner.databaseReader
```

### Fine-Grained Access Control

**Row-Level Security (PostgreSQL):**
```sql
-- Create policy for row-level security
CREATE POLICY user_isolation ON users
    FOR ALL
    TO app_user
    USING (user_id = current_user_id());

ALTER TABLE users ENABLE ROW LEVEL SECURITY;
```

### Encryption

- **At Rest:** Automatic encryption with Google-managed keys
- **In Transit:** Automatic TLS encryption
- **CMEK (Customer-Managed Encryption Keys):**
  ```bash
  gcloud spanner databases create my-encrypted-db \
      --instance=my-instance \
      --kms-key=projects/PROJECT/locations/LOCATION/keyRings/RING/cryptoKeys/KEY
  ```

---

## Backup & Recovery

### Creating Backups

**Console:**
1. Navigate to **Database** > **Backups**
2. Click **Create Backup**
3. Enter backup ID and retention period
4. Click **Create**

**gcloud:**
```bash
# Create backup
gcloud spanner backups create my-backup \
    --instance=my-instance \
    --database=my-database \
    --retention-period=30d

# List backups
gcloud spanner backups list --instance=my-instance
```

### Restoring from Backup

**gcloud:**
```bash
# Restore to new database
gcloud spanner databases create my-restored-db \
    --instance=my-instance \
    --source-backup=projects/PROJECT/instances/INSTANCE/backups/my-backup
```

### Scheduled Backups

**gcloud (using Cloud Scheduler):**
```bash
# Create Cloud Scheduler job for daily backups
gcloud scheduler jobs create http daily-spanner-backup \
    --schedule="0 2 * * *" \
    --uri="https://spanner.googleapis.com/v1/projects/PROJECT/instances/INSTANCE/databases/DATABASE/backups" \
    --message-body='{"backupId": "daily-backup-'$(date +%Y%m%d)'", "retentionPeriod": "2592000s"}' \
    --oauth-service-account-email=scheduler@PROJECT.iam.gserviceaccount.com
```

### Point-in-Time Recovery (PITR)

```bash
# Enable PITR (retention: 1-7 days)
gcloud spanner databases ddl update my-database \
    --instance=my-instance \
    --enable-pitr \
    --pitr-retention-period=7d

# Restore to specific timestamp
gcloud spanner databases create my-restored-db \
    --instance=my-instance \
    --source-database=projects/PROJECT/instances/INSTANCE/databases/my-database \
    --version-time="2024-11-20T10:30:00Z"
```

---

## Monitoring & Troubleshooting

### Key Metrics

**Cloud Monitoring Metrics:**
- `instance/cpu/utilization` - CPU usage (target <65%)
- `instance/storage/used_bytes` - Storage utilization
- `instance/node_count` - Number of nodes
- `database/query_count` - Query volume
- `database/query_latency` - Query performance

### Viewing Metrics

**Console:**
1. Navigate to **Spanner** > **Instance** > **Monitoring**
2. View CPU, storage, and query metrics

**gcloud:**
```bash
# View instance CPU utilization
gcloud monitoring time-series list \
    --filter='metric.type="spanner.googleapis.com/instance/cpu/utilization"' \
    --format=json
```

### Query Insights

**Spanner Studio:**
1. Navigate to **Database** > **Spanner Studio**
2. Click **Query Insights**
3. View top queries by latency, CPU, and execution count

### Common Issues & Solutions

| Issue | Symptom | Solution |
|-------|---------|----------|
| **Hotspots** | High latency, uneven CPU usage | Redesign primary key (avoid monotonic keys) |
| **High CPU** | CPU utilization >65% | Scale up processing units or optimize queries |
| **Storage Full** | Storage nearing capacity | Scale up or delete old data |
| **Slow Queries** | High query latency | Add indexes, optimize SQL, use query hints |

### Troubleshooting Commands

```bash
# Check instance details
gcloud spanner instances describe my-instance

# List databases
gcloud spanner databases list --instance=my-instance

# View database schema
gcloud spanner databases ddl describe my-database --instance=my-instance

# Export schema
gcloud spanner databases ddl describe my-database \
    --instance=my-instance \
    --format="value(DDL)"
```

---

## ACE Exam Tips

### Key Concepts to Remember

1. **Spanner vs Other Databases:**
   - Use Spanner for global, strongly consistent, horizontally scalable relational workloads
   - Use Cloud SQL for regional, traditional RDBMS workloads
   - Use Firestore for document-based NoSQL
   - Use Bigtable for high-throughput NoSQL (eventual consistency)

2. **Instance Scaling:**
   - 1 node = 1000 processing units
   - Can scale up/down without downtime
   - Autoscaling recommended for production

3. **Primary Key Design:**
   - Avoid monotonic keys (timestamps, auto-increments)
   - Use UUIDs with `GENERATE_UUID()`
   - Swap key order (e.g., UserId first, then Timestamp)

4. **Configuration Types:**
   - Regional: 99.99% SLA
   - Multi-region: 99.999% SLA
   - Multi-region costs ~3x regional

5. **IAM Roles:**
   - `spanner.admin` - Full access
   - `spanner.databaseAdmin` - Manage schema and data
   - `spanner.databaseUser` - Read/write data
   - `spanner.databaseReader` - Read-only

6. **Backups:**
   - Manual backups with retention up to 366 days
   - PITR (Point-in-Time Recovery) for 1-7 days
   - Backups stored in same region/multi-region as database

7. **Transactions:**
   - Full ACID compliance
   - Strongly consistent reads
   - External consistency with TrueTime

8. **Performance:**
   - Target CPU <65% for optimal performance
   - Use indexes for frequently queried columns
   - Use interleaved tables for parent-child relationships

### Common Exam Scenarios

**Scenario 1:** Need global database with strong consistency
- **Answer:** Cloud Spanner (multi-region configuration)

**Scenario 2:** High write throughput causing hotspots
- **Answer:** Redesign primary key (use UUID or swap key order)

**Scenario 3:** Need 99.999% availability
- **Answer:** Use multi-region Spanner configuration

**Scenario 4:** Application needs read-only access to Spanner
- **Answer:** Grant `roles/spanner.databaseReader` role

**Scenario 5:** Need to restore database to specific point in time
- **Answer:** Enable PITR and restore using `--version-time`

### Hands-On Practice

**Essential gcloud Commands:**
```bash
# Create instance
gcloud spanner instances create my-instance --config=regional-us-central1 --processing-units=1000

# Create database
gcloud spanner databases create my-db --instance=my-instance

# Execute SQL
gcloud spanner databases execute-sql my-db --instance=my-instance --sql="SELECT 1"

# Create backup
gcloud spanner backups create my-backup --instance=my-instance --database=my-db --retention-period=7d

# Grant access
gcloud spanner databases add-iam-policy-binding my-db --instance=my-instance --member=user:user@example.com --role=roles/spanner.databaseUser
```

---

## Additional Resources

- [Spanner Documentation](https://cloud.google.com/spanner/docs)
- [Schema Design Best Practices](https://cloud.google.com/spanner/docs/schema-design)
- [SQL Best Practices](https://cloud.google.com/spanner/docs/sql-best-practices)
- [Pricing Calculator](https://cloud.google.com/products/calculator)
- [Spanner Proof of Concept Playbook](https://cloud.google.com/spanner/docs/proof-of-concept-playbook)

---

**Last Updated:** November 2025  
**Exam:** Google Associate Cloud Engineer (ACE)
