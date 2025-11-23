# Google Cloud SQL - Associate Cloud Engineer (ACE) Comprehensive Guide

## Table of Contents
1. [Overview](#overview)
2. [Database Engine Selection](#database-engine-selection)
3. [Instance Creation & Configuration](#instance-creation--configuration)
4. [Connection Methods](#connection-methods)
5. [Database & User Management](#database--user-management)
6. [Backup & Recovery](#backup--recovery)
7. [High Availability](#high-availability)
8. [Replication](#replication)
9. [Storage Management](#storage-management)
10. [Security](#security)
11. [Import & Export](#import--export)
12. [Maintenance & Updates](#maintenance--updates)
13. [Monitoring & Logging](#monitoring--logging)
14. [Performance Optimization](#performance-optimization)
15. [Troubleshooting](#troubleshooting)
16. [ACE Exam Tips](#ace-exam-tips)

---

## Overview

### What is Cloud SQL?

**Cloud SQL** is Google Cloud's fully managed relational database service that makes it easy to set up, maintain, manage, and administer MySQL, PostgreSQL, and SQL Server databases in the cloud.

### Key Features

- **Fully Managed:** Google handles backups, replication, patches, updates, and infrastructure
- **High Availability:** 99.95% SLA with regional instances and automatic failover
- **Automatic Backups:** Daily automated backups and point-in-time recovery
- **Read Replicas:** Scale read operations and improve performance
- **Security:** Encryption at rest and in transit, VPC support, IAM integration
- **Easy Migration:** Database Migration Service for seamless migration
- **Integration:** Works with App Engine, Compute Engine, GKE, Cloud Functions

### Supported Database Engines

| Engine | Latest Versions | Use Cases |
|--------|----------------|-----------|
| **MySQL** | 5.7, 8.0 | Web applications, WordPress, e-commerce |
| **PostgreSQL** | 12, 13, 14, 15 | Analytics, geospatial, complex queries |
| **SQL Server** | 2017, 2019, 2022 | Enterprise apps, Windows environments |

---

## Database Engine Selection

### MySQL

**Best For:**
- Web applications (WordPress, Drupal)
- E-commerce platforms
- Content management systems
- Applications requiring simple queries

**Key Features:**
- InnoDB storage engine
- Full-text search
- JSON support (MySQL 5.7+)
- Replication support

### PostgreSQL

**Best For:**
- Data analytics and warehousing
- Geospatial applications (PostGIS)
- Complex queries and transactions
- Applications requiring advanced data types

**Key Features:**
- ACID compliance
- JSON/JSONB support
- Full-text search
- Arrays and custom types
- PostGIS extension for geospatial data

### SQL Server

**Best For:**
- Enterprise Windows applications
- .NET applications
- Microsoft ecosystem integration
- Business intelligence workloads

**Key Features:**
- T-SQL support
- Always On availability groups
- Integration with Active Directory
- SQL Server Reporting Services (SSRS)

---

## Instance Creation & Configuration

### Creating a MySQL Instance

**Console Method:**
1. Go to Cloud SQL in Console
2. Click "Create Instance"
3. Choose MySQL
4. Configure instance ID, password, region, zone
5. Choose machine type and storage
6. Click "Create"

**gcloud Command:**
```bash
# Basic MySQL instance
gcloud sql instances create mysql-instance \
    --database-version=MYSQL_8_0 \
    --tier=db-n1-standard-2 \
    --region=us-central1 \
    --root-password=SecureP@ssw0rd \
    --backup \
    --backup-start-time=03:00

# Production MySQL instance with HA
gcloud sql instances create mysql-prod \
    --database-version=MYSQL_8_0 \
    --tier=db-n1-standard-4 \
    --region=us-central1 \
    --availability-type=REGIONAL \
    --storage-type=SSD \
    --storage-size=100GB \
    --storage-auto-increase \
    --storage-auto-increase-limit=500 \
    --backup \
    --backup-start-time=03:00 \
    --enable-bin-log \
    --maintenance-window-day=SUN \
    --maintenance-window-hour=4 \
    --root-password=SecureP@ssw0rd
```

### Creating a PostgreSQL Instance

```bash
# Basic PostgreSQL instance
gcloud sql instances create postgres-instance \
    --database-version=POSTGRES_15 \
    --tier=db-custom-2-7680 \
    --region=us-central1 \
    --root-password=SecureP@ssw0rd

# Production PostgreSQL with HA
gcloud sql instances create postgres-prod \
    --database-version=POSTGRES_15 \
    --tier=db-custom-4-15360 \
    --region=us-central1 \
    --availability-type=REGIONAL \
    --storage-type=SSD \
    --storage-size=100GB \
    --storage-auto-increase \
    --backup \
    --enable-bin-log \
    --root-password=SecureP@ssw0rd
```

### Creating a SQL Server Instance

```bash
# SQL Server Standard
gcloud sql instances create sqlserver-instance \
    --database-version=SQLSERVER_2019_STANDARD \
    --tier=db-custom-2-7680 \
    --region=us-central1 \
    --root-password=SecureP@ssw0rd123

# SQL Server Enterprise with HA
gcloud sql instances create sqlserver-prod \
    --database-version=SQLSERVER_2019_ENTERPRISE \
    --tier=db-custom-4-15360 \
    --region=us-central1 \
    --availability-type=REGIONAL \
    --storage-type=SSD \
    --storage-size=100GB \
    --root-password=SecureP@ssw0rd123
```

### Machine Types (Tiers)

**Shared Core (Dev/Test only):**
```bash
--tier=db-f1-micro    # 0.6 GB RAM (shared CPU)
--tier=db-g1-small    # 1.7 GB RAM (shared CPU)
```

**Standard Machine Types:**
```bash
--tier=db-n1-standard-1    # 1 vCPU, 3.75 GB RAM
--tier=db-n1-standard-2    # 2 vCPU, 7.5 GB RAM
--tier=db-n1-standard-4    # 4 vCPU, 15 GB RAM
--tier=db-n1-standard-8    # 8 vCPU, 30 GB RAM
--tier=db-n1-standard-16   # 16 vCPU, 60 GB RAM
```

**Custom Machine Types:**
```bash
--tier=db-custom-2-7680    # 2 vCPU, 7.5 GB RAM
--tier=db-custom-4-15360   # 4 vCPU, 15 GB RAM
--tier=db-custom-8-30720   # 8 vCPU, 30 GB RAM
```

**Memory format:** `--tier=db-custom-<CPU>-<MEMORY_MB>`

### Storage Configuration

**Storage Types:**
- **SSD (Solid State Drive):** Better performance, recommended for production
- **HDD (Hard Disk Drive):** Lower cost, suitable for dev/test

```bash
# Configure storage
--storage-type=SSD \
--storage-size=100GB \
--storage-auto-increase \
--storage-auto-increase-limit=500GB
```

**Storage Auto-Increase:**
- Automatically expands storage when 90% full
- Prevents downtime due to storage exhaustion
- Set a limit to control costs

### Listing and Describing Instances

```bash
# List all instances
gcloud sql instances list

# Describe specific instance
gcloud sql instances describe mysql-instance

# Get connection name
gcloud sql instances describe mysql-instance \
    --format="value(connectionName)"
```

---

## Connection Methods

### 1. Cloud SQL Auth Proxy (Recommended)

**What is it?**
A secure way to connect to Cloud SQL without configuring firewall rules or SSL certificates. The proxy provides IAM-based authentication and encryption.

**Benefits:**
- Secure encrypted connections
- No need to manage SSL certificates
- Works from anywhere (local machine, Cloud Functions, App Engine)
- Automatic IAM authentication
- Supports multiple instances

**Installation:**
```bash
# Download Cloud SQL Proxy (Linux)
curl -o cloud-sql-proxy https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v2.6.0/cloud-sql-proxy.linux.amd64

# Make executable
chmod +x cloud-sql-proxy

# Start proxy for MySQL
./cloud-sql-proxy my-project:us-central1:mysql-instance

# Start with custom port
./cloud-sql-proxy my-project:us-central1:mysql-instance --port 3307

# Start for multiple instances
./cloud-sql-proxy \
    my-project:us-central1:mysql-instance \
    my-project:us-east1:postgres-instance
```

**Connect via Proxy:**
```bash
# MySQL connection
mysql -h 127.0.0.1 -u root -p

# PostgreSQL connection
psql "host=127.0.0.1 user=postgres dbname=mydb"
```

**Using in Application (Python):**
```python
import pymysql
import os

connection = pymysql.connect(
    host='127.0.0.1',
    user='root',
    password=os.environ['DB_PASSWORD'],
    database='mydb',
    port=3306
)
```

### 2. Private IP Connection

**Best for:** Applications running in the same VPC (Compute Engine, GKE)

**Setup Private Services Access:**
```bash
# 1. Enable Service Networking API
gcloud services enable servicenetworking.googleapis.com

# 2. Allocate IP range for private services
gcloud compute addresses create google-managed-services-default \
    --global \
    --purpose=VPC_PEERING \
    --prefix-length=16 \
    --network=default

# 3. Create private connection
gcloud services vpc-peerings connect \
    --service=servicenetworking.googleapis.com \
    --ranges=google-managed-services-default \
    --network=default
```

**Create Instance with Private IP:**
```bash
gcloud sql instances create mysql-private \
    --database-version=MYSQL_8_0 \
    --tier=db-n1-standard-2 \
    --region=us-central1 \
    --network=projects/PROJECT_ID/global/networks/default \
    --no-assign-ip \
    --root-password=SecureP@ssw0rd
```

**Add Private IP to Existing Instance:**
```bash
gcloud sql instances patch mysql-instance \
    --network=projects/PROJECT_ID/global/networks/default
```

**Connect from Compute Engine VM:**
```bash
# Get private IP
gcloud sql instances describe mysql-private \
    --format="value(ipAddresses.ipAddress)"

# Connect directly
mysql -h 10.X.X.X -u root -p
```

### 3. Public IP with Authorized Networks

**Best for:** Connecting from known static IP addresses

```bash
# Add authorized network
gcloud sql instances patch mysql-instance \
    --authorized-networks=203.0.113.0/24

# Add multiple networks
gcloud sql instances patch mysql-instance \
    --authorized-networks=203.0.113.0/24,198.51.100.0/24

# Clear authorized networks
gcloud sql instances patch mysql-instance \
    --clear-authorized-networks
```

### 4. SSL/TLS Connections

**Create Server Certificate:**
```bash
# Server certificate is auto-created

# Download server CA certificate
gcloud sql ssl server-ca-certs list --instance=mysql-instance

gcloud sql ssl server-ca-certs get --instance=mysql-instance \
    --output-file=server-ca.pem
```

**Create Client Certificate:**
```bash
gcloud sql ssl-certs create my-client-cert \
    --instance=mysql-instance

gcloud sql ssl-certs describe my-client-cert \
    --instance=mysql-instance \
    --format="value(cert)" > client-cert.pem

# Get client key (only available at creation)
```

**Connect with SSL:**
```bash
mysql -h PUBLIC_IP -u root -p \
    --ssl-ca=server-ca.pem \
    --ssl-cert=client-cert.pem \
    --ssl-key=client-key.pem
```

---

## Database & User Management

### Creating Databases

**MySQL:**
```bash
# Create database
gcloud sql databases create myapp_db \
    --instance=mysql-instance \
    --charset=utf8mb4 \
    --collation=utf8mb4_unicode_ci

# List databases
gcloud sql databases list --instance=mysql-instance

# Delete database
gcloud sql databases delete myapp_db --instance=mysql-instance
```

**PostgreSQL:**
```bash
# Create database
gcloud sql databases create myapp_db \
    --instance=postgres-instance

# Connect and create manually
psql "host=127.0.0.1 user=postgres" -c "CREATE DATABASE myapp_db;"
```

### Managing Users

**Create User:**
```bash
# MySQL user
gcloud sql users create appuser \
    --instance=mysql-instance \
    --password=UserP@ssw0rd

# PostgreSQL user
gcloud sql users create appuser \
    --instance=postgres-instance \
    --password=UserP@ssw0rd

# SQL Server user
gcloud sql users create appuser \
    --instance=sqlserver-instance \
    --password=UserP@ssw0rd
```

**List Users:**
```bash
gcloud sql users list --instance=mysql-instance
```

**Change User Password:**
```bash
gcloud sql users set-password appuser \
    --instance=mysql-instance \
    --password=NewP@ssw0rd
```

**Change Root Password:**
```bash
# MySQL/PostgreSQL
gcloud sql users set-password root \
    --host=% \
    --instance=mysql-instance \
    --password=NewRootP@ssw0rd
```

**Delete User:**
```bash
gcloud sql users delete appuser --instance=mysql-instance
```

**Grant Permissions (via SQL):**
```sql
-- MySQL: Grant all privileges on database
GRANT ALL PRIVILEGES ON myapp_db.* TO 'appuser'@'%';
FLUSH PRIVILEGES;

-- PostgreSQL: Grant privileges
GRANT ALL PRIVILEGES ON DATABASE myapp_db TO appuser;
```

---

## Backup & Recovery

### Automated Backups

**Configure Automated Backups:**
```bash
# Enable automated backups
gcloud sql instances patch mysql-instance \
    --backup-start-time=03:00 \
    --retained-backups-count=7

# Configure backup location
gcloud sql instances patch mysql-instance \
    --backup-location=us
```

**Backup Settings:**
- **Backup Window:** 4-hour window starting at specified time
- **Retention:** Default 7 days (configurable up to 365 days)
- **Backup Location:** Region or multi-region (us, eu, asia)
- **Cost:** Included up to instance storage size

**Disable Automated Backups:**
```bash
gcloud sql instances patch mysql-instance --no-backup
```

### On-Demand Backups

**Create On-Demand Backup:**
```bash
# Create backup
gcloud sql backups create \
    --instance=mysql-instance \
    --description="Pre-migration backup"

# Backups persist until manually deleted
```

**List Backups:**
```bash
gcloud sql backups list --instance=mysql-instance

# Output:
# ID                       WINDOW_START_TIME          STATUS
# 1234567890123            2024-01-15T03:00:00.000Z   SUCCESSFUL
```

**Describe Backup:**
```bash
gcloud sql backups describe 1234567890123 \
    --instance=mysql-instance
```

**Delete Backup:**
```bash
gcloud sql backups delete 1234567890123 \
    --instance=mysql-instance
```

### Restore from Backup

**Restore to Same Instance (Overwrites Data):**
```bash
gcloud sql backups restore 1234567890123 \
    --backup-instance=mysql-instance \
    --restore-instance=mysql-instance
```

**Restore to New Instance (Recommended):**
```bash
# Create new instance from backup
gcloud sql instances create mysql-restored \
    --backup=1234567890123 \
    --source-instance=mysql-instance \
    --tier=db-n1-standard-2 \
    --region=us-central1
```

### Point-in-Time Recovery (PITR)

**Prerequisites:**
- Automated backups enabled
- Binary logging enabled (MySQL) or WAL archiving (PostgreSQL)

**Enable Binary Logging:**
```bash
gcloud sql instances patch mysql-instance --enable-bin-log
```

**Perform PITR:**
```bash
# Clone instance to specific timestamp
gcloud sql instances clone mysql-instance mysql-pitr-clone \
    --point-in-time='2024-01-15T14:30:00.000Z'

# PITR window: Last 7 days (or backup retention period)
```

**Use Cases:**
- Recover from accidental data deletion
- Restore to time before schema change
- Create test environment from specific time

---

## High Availability

### Regional (HA) Configuration

**What is HA?**
- Primary instance in one zone
- Standby instance in another zone (same region)
- Synchronous replication via regional persistent disk
- Automatic failover (< 60 seconds)
- 99.95% SLA

**Create HA Instance:**
```bash
gcloud sql instances create mysql-ha \
    --database-version=MYSQL_8_0 \
    --tier=db-n1-standard-2 \
    --region=us-central1 \
    --availability-type=REGIONAL \
    --backup \
    --enable-bin-log \
    --root-password=SecureP@ssw0rd
```

**Enable HA on Existing Instance:**
```bash
gcloud sql instances patch mysql-instance \
    --availability-type=REGIONAL \
    --enable-bin-log
```

**Disable HA:**
```bash
gcloud sql instances patch mysql-instance \
    --availability-type=ZONAL
```

### Failover Testing

**Initiate Manual Failover:**
```bash
gcloud sql instances failover mysql-ha
```

**What Happens During Failover:**
1. Primary instance becomes unavailable
2. Standby promoted to primary (< 60 seconds)
3. New standby created in original primary zone
4. Existing connections dropped (application must reconnect)
5. Same IP address maintained (no DNS changes needed)

**Requirements:**
- Automated backups enabled
- Binary logging/WAL archiving enabled
- Instance must be healthy

---

## Replication

### Read Replicas

**Purpose:**
- Offload read traffic from primary instance
- Improve read performance
- Data locality (replicas in different regions)

**Create Read Replica:**
```bash
# In-region replica
gcloud sql instances create mysql-replica-1 \
    --master-instance-name=mysql-instance \
    --tier=db-n1-standard-2 \
    --region=us-central1

# Cross-region replica (disaster recovery)
gcloud sql instances create mysql-replica-us-east \
    --master-instance-name=mysql-instance \
    --tier=db-n1-standard-2 \
    --region=us-east1

# Replica with higher machine type
gcloud sql instances create mysql-replica-large \
    --master-instance-name=mysql-instance \
    --tier=db-n1-standard-4 \
    --region=us-central1
```

**List Replicas:**
```bash
gcloud sql instances list --filter="masterInstanceName:mysql-instance"
```

**Replica Lag Monitoring:**
```bash
# Check replication status
gcloud sql operations list \
    --instance=mysql-replica-1 \
    --filter="operationType:REPLICA_LAG"
```

**Promote Replica to Standalone:**
```bash
# Breaks replication link, makes replica independent
gcloud sql instances promote-replica mysql-replica-1

# Use case: Disaster recovery or migration
```

**Delete Replica:**
```bash
gcloud sql instances delete mysql-replica-1
```

### Cascading Replicas

**Create Replica of Replica:**
```bash
# Level 1 replica
gcloud sql instances create mysql-replica-1 \
    --master-instance-name=mysql-instance \
    --region=us-central1

# Level 2 replica (cascading)
gcloud sql instances create mysql-replica-2 \
    --master-instance-name=mysql-replica-1 \
    --region=us-central1
```

**Use Case:** Reduce replication load on primary instance

---

## Storage Management

### Check Storage Usage

```bash
# Get storage info
gcloud sql instances describe mysql-instance \
    --format="value(settings.dataDiskSizeGb,settings.dataDiskType)"

# Monitor storage with Cloud Monitoring
# Metric: cloudsql.googleapis.com/database/disk/bytes_used
```

### Increase Storage Size

```bash
# Increase storage manually
gcloud sql instances patch mysql-instance \
    --storage-size=200GB

# Note: Storage can only be increased, never decreased
```

### Auto-Increase Storage

```bash
# Enable auto-increase
gcloud sql instances patch mysql-instance \
    --storage-auto-increase \
    --storage-auto-increase-limit=500GB

# Triggers when storage is 90% full
# Increases by 25% or 25 GB (whichever is larger)
```

### Change Storage Type

**Note:** Cannot change storage type (SSD/HDD) after creation

```bash
# Must create new instance and migrate data
```

---

## Security

### IAM Integration

**Cloud SQL Roles:**
- `roles/cloudsql.admin`: Full control
- `roles/cloudsql.client`: Connect to instances
- `roles/cloudsql.editor`: Manage instances (no data access)
- `roles/cloudsql.viewer`: View instances (read-only)

**Grant IAM Permissions:**
```bash
# Grant admin role
gcloud projects add-iam-policy-binding PROJECT_ID \
    --member=user:alice@example.com \
    --role=roles/cloudsql.admin

# Grant client role (for Cloud SQL Proxy)
gcloud projects add-iam-policy-binding PROJECT_ID \
    --member=serviceAccount:myapp@PROJECT_ID.iam.gserviceaccount.com \
    --role=roles/cloudsql.client
```

### Database Authentication

**MySQL:**
```bash
# Create user with password
gcloud sql users create appuser \
    --instance=mysql-instance \
    --password=SecureP@ssw0rd

# Create IAM user (Cloud SQL IAM Authentication)
gcloud sql users create alice@example.com \
    --instance=mysql-instance \
    --type=CLOUD_IAM_USER

# Connect with IAM
gcloud sql connect mysql-instance --user=alice@example.com
```

**PostgreSQL:**
```bash
# Cloud SQL IAM Authentication
gcloud sql users create alice@example.com \
    --instance=postgres-instance \
    --type=CLOUD_IAM_USER
```

### Encryption

**At Rest:**
- Default: Google-managed encryption keys
- CMEK: Customer-managed encryption keys (Cloud KMS)

```bash
# Create instance with CMEK
gcloud sql instances create mysql-cmek \
    --database-version=MYSQL_8_0 \
    --tier=db-n1-standard-2 \
    --region=us-central1 \
    --disk-encryption-key=projects/PROJECT_ID/locations/us-central1/keyRings/my-keyring/cryptoKeys/my-key \
    --root-password=SecureP@ssw0rd
```

**In Transit:**
- Cloud SQL Proxy: Automatic encryption
- SSL/TLS: Configure certificates

**Require SSL:**
```bash
gcloud sql instances patch mysql-instance \
    --require-ssl
```

---

## Import & Export

### Export Data

**Export to SQL Dump:**
```bash
# Export entire database
gcloud sql export sql mysql-instance \
    gs://my-bucket/database-dump.sql \
    --database=myapp_db

# Export specific tables
gcloud sql export sql mysql-instance \
    gs://my-bucket/users-dump.sql \
    --database=myapp_db \
    --table=users,profiles

# Compressed export
gcloud sql export sql mysql-instance \
    gs://my-bucket/database-dump.sql.gz \
    --database=myapp_db
```

**Export to CSV:**
```bash
# Export query results to CSV
gcloud sql export csv mysql-instance \
    gs://my-bucket/users.csv \
    --database=myapp_db \
    --query="SELECT id, name, email FROM users WHERE active=1"

# Specify delimiter
gcloud sql export csv mysql-instance \
    gs://my-bucket/users.tsv \
    --database=myapp_db \
    --query="SELECT * FROM users" \
    --offload \
    --quote='"' \
    --escape='\' \
    --fields-terminated-by='\t'
```

**Export PostgreSQL:**
```bash
# PostgreSQL export
gcloud sql export sql postgres-instance \
    gs://my-bucket/postgres-dump.sql \
    --database=myapp_db
```

### Import Data

**Import SQL Dump:**
```bash
# Import database
gcloud sql import sql mysql-instance \
    gs://my-bucket/database-dump.sql \
    --database=myapp_db

# Import compressed file
gcloud sql import sql mysql-instance \
    gs://my-bucket/database-dump.sql.gz \
    --database=myapp_db
```

**Import CSV:**
```bash
# Import CSV into table
gcloud sql import csv mysql-instance \
    gs://my-bucket/users.csv \
    --database=myapp_db \
    --table=users

# Import with custom delimiter
gcloud sql import csv mysql-instance \
    gs://my-bucket/users.tsv \
    --database=myapp_db \
    --table=users \
    --fields-terminated-by='\t'
```

**Import Best Practices:**
1. **Test on non-production first**
2. **Use serverless export/import** (`--offload`) for large datasets
3. **Compress large files** (`.gz` compression)
4. **Create database before import** (doesn't auto-create)
5. **Grant Storage Object Viewer role** to Cloud SQL service account

---

## Maintenance & Updates

### Maintenance Windows

**Set Maintenance Window:**
```bash
gcloud sql instances patch mysql-instance \
    --maintenance-window-day=SUN \
    --maintenance-window-hour=3 \
    --maintenance-window-duration=1

# Days: MON, TUE, WED, THU, FRI, SAT, SUN
# Hour: 0-23 (UTC)
# Duration: 1-24 hours
```

**Maintenance Release Channel:**
```bash
# Production (default): Stable, tested updates
gcloud sql instances patch mysql-instance \
    --maintenance-release-channel=production

# Preview: Earlier access to features
gcloud sql instances patch mysql-instance \
    --maintenance-release-channel=preview
```

### Deny Maintenance Period

**Prevent maintenance during critical periods:**
```bash
# Deny maintenance for 90 days
gcloud sql instances patch mysql-instance \
    --deny-maintenance-period-start-date=2024-11-15 \
    --deny-maintenance-period-end-date=2025-02-15

# Use case: Holiday season, tax season, etc.
```

### Instance Operations

**Start Instance:**
```bash
gcloud sql instances start mysql-instance
```

**Stop Instance:**
```bash
gcloud sql instances stop mysql-instance

# Billing continues for storage and IP addresses
# No charges for compute
```

**Restart Instance:**
```bash
gcloud sql instances restart mysql-instance

# Causes brief downtime
```

**Delete Instance:**
```bash
gcloud sql instances delete mysql-instance

# With deletion protection disabled first:
gcloud sql instances patch mysql-instance --no-deletion-protection
gcloud sql instances delete mysql-instance
```

### Database Flags

**Set Database Flags:**
```bash
# MySQL: Enable slow query log
gcloud sql instances patch mysql-instance \
    --database-flags=slow_query_log=on,long_query_time=2

# PostgreSQL: Set max connections
gcloud sql instances patch postgres-instance \
    --database-flags=max_connections=200

# Clear all flags
gcloud sql instances patch mysql-instance --clear-database-flags
```

**Common MySQL Flags:**
- `max_connections`: Maximum concurrent connections
- `slow_query_log`: Enable slow query logging
- `long_query_time`: Slow query threshold
- `max_allowed_packet`: Maximum packet size
- `innodb_buffer_pool_size`: InnoDB buffer pool size

**Common PostgreSQL Flags:**
- `max_connections`: Maximum concurrent connections
- `shared_buffers`: Shared buffer size
- `work_mem`: Memory for operations
- `maintenance_work_mem`: Memory for maintenance operations

---

## Monitoring & Logging

### Cloud Monitoring Metrics

**Key Metrics:**
```
# CPU Utilization
cloudsql.googleapis.com/database/cpu/utilization

# Memory Utilization
cloudsql.googleapis.com/database/memory/utilization

# Disk Utilization
cloudsql.googleapis.com/database/disk/bytes_used
cloudsql.googleapis.com/database/disk/utilization

# Network
cloudsql.googleapis.com/database/network/sent_bytes_count
cloudsql.googleapis.com/database/network/received_bytes_count

# Connections
cloudsql.googleapis.com/database/network/connections

# Replication Lag
cloudsql.googleapis.com/database/replication/replica_lag
```

**Create Alert Policy:**
```bash
# High CPU alert
gcloud alpha monitoring policies create \
    --notification-channels=CHANNEL_ID \
    --display-name="High CPU on Cloud SQL" \
    --condition-threshold-value=0.8 \
    --condition-threshold-duration=300s \
    --condition-filter='resource.type="cloudsql_database" AND metric.type="cloudsql.googleapis.com/database/cpu/utilization"'
```

### Cloud Logging

**Log Types:**
- **Error Logs:** `cloudsql.googleapis.com/mysql.err`
- **General Logs:** `cloudsql.googleapis.com/mysql-general.log`
- **Slow Query Logs:** `cloudsql.googleapis.com/mysql-slow.log`
- **PostgreSQL Logs:** `cloudsql.googleapis.com/postgres.log`

**View Logs:**
```bash
# View error logs
gcloud logging read "resource.type=cloudsql_database AND logName=projects/PROJECT_ID/logs/cloudsql.googleapis.com%2Fmysql.err" --limit=50

# View slow query logs
gcloud logging read "resource.type=cloudsql_database AND logName=projects/PROJECT_ID/logs/cloudsql.googleapis.com%2Fmysql-slow.log" --limit=20

# Filter by instance
gcloud logging read "resource.type=cloudsql_database AND resource.labels.database_id=PROJECT_ID:mysql-instance" --limit=50
```

**Enable Slow Query Log:**
```bash
gcloud sql instances patch mysql-instance \
    --database-flags=slow_query_log=on,long_query_time=2
```

---

## Performance Optimization

### Query Insights

**Enable Query Insights:**
```bash
gcloud sql instances patch mysql-instance \
    --insights-config-query-insights-enabled \
    --insights-config-query-string-length=1024 \
    --insights-config-record-application-tags \
    --insights-config-record-client-address
```

**View in Console:**
- Go to Cloud SQL instance
- Click "Query Insights" tab
- Analyze slow queries, CPU time, execution counts

### Connection Pooling

**Use Connection Poolers:**
- **PgBouncer** (PostgreSQL)
- **ProxySQL** (MySQL)
- **Cloud SQL Python Connector**

**Python Example with Connection Pooling:**
```python
from google.cloud.sql.connector import Connector
import sqlalchemy

connector = Connector()

def getconn():
    conn = connector.connect(
        "project:region:instance",
        "pymysql",
        user="appuser",
        password="password",
        db="mydb"
    )
    return conn

pool = sqlalchemy.create_engine(
    "mysql+pymysql://",
    creator=getconn,
    pool_size=5,
    max_overflow=2,
    pool_timeout=30,
    pool_recycle=1800
)
```

### Caching

**Implement Application-Level Caching:**
- Use Memorystore (Redis/Memcached)
- Cache frequent queries
- Cache session data

### Indexing

**Create Indexes:**
```sql
-- MySQL
CREATE INDEX idx_user_email ON users(email);
CREATE INDEX idx_orders_date ON orders(order_date);

-- PostgreSQL
CREATE INDEX idx_user_email ON users USING btree(email);
CREATE INDEX idx_orders_date ON orders(order_date);
```

**Check Missing Indexes:**
```sql
-- MySQL: Check slow queries
SELECT * FROM mysql.slow_log ORDER BY query_time DESC LIMIT 10;

-- Use EXPLAIN to analyze queries
EXPLAIN SELECT * FROM users WHERE email = 'alice@example.com';
```

---

## Troubleshooting

### Common Issues

#### 1. Connection Timeouts

**Symptoms:**
- Cannot connect to instance
- Connection refused errors
- Timeout errors

**Troubleshooting:**
```bash
# Check instance is running
gcloud sql instances describe mysql-instance --format="value(state)"

# Check authorized networks (public IP)
gcloud sql instances describe mysql-instance --format="value(settings.ipConfiguration.authorizedNetworks)"

# Test Cloud SQL Proxy
./cloud-sql-proxy my-project:us-central1:mysql-instance --verbose

# Check firewall rules (private IP)
gcloud compute firewall-rules list --filter="network:default"
```

**Solutions:**
- Add IP to authorized networks
- Use Cloud SQL Proxy
- Configure private IP correctly
- Check VPC firewall rules

#### 2. Storage Full

**Symptoms:**
- Instance stops responding
- Write operations fail
- Database in read-only mode

**Troubleshooting:**
```bash
# Check storage usage
gcloud sql instances describe mysql-instance \
    --format="value(settings.dataDiskSizeGb,currentDiskSize)"
```

**Solutions:**
```bash
# Increase storage
gcloud sql instances patch mysql-instance --storage-size=200GB

# Enable auto-increase
gcloud sql instances patch mysql-instance \
    --storage-auto-increase \
    --storage-auto-increase-limit=500GB

# Clean up data (archive old records)
```

#### 3. High Memory Usage

**Symptoms:**
- OOM (Out of Memory) errors
- Instance restarts automatically
- Slow query performance

**Troubleshooting:**
```bash
# Check memory metrics in Cloud Monitoring
# Metric: cloudsql.googleapis.com/database/memory/utilization

# Check connections
gcloud sql operations list --instance=mysql-instance \
    --filter="operationType:CONNECTIONS"
```

**Solutions:**
```bash
# Upgrade machine type
gcloud sql instances patch mysql-instance --tier=db-n1-standard-4

# Optimize queries
# Reduce max_connections
gcloud sql instances patch mysql-instance \
    --database-flags=max_connections=100

# Implement connection pooling
```

#### 4. Replication Lag

**Symptoms:**
- Read replicas showing stale data
- High replica lag metrics

**Troubleshooting:**
```bash
# Check replica lag
# View in Cloud Console: Instance > Replicas

# Check replica instance resources
gcloud sql instances describe mysql-replica-1
```

**Solutions:**
```bash
# Upgrade replica machine type
gcloud sql instances patch mysql-replica-1 --tier=db-n1-standard-4

# Reduce write load on primary
# Use multiple read replicas
# Check network between regions (cross-region replicas)
```

#### 5. Failed Backups

**Symptoms:**
- Backup operations fail
- No recent backups listed

**Troubleshooting:**
```bash
# Check backup configuration
gcloud sql instances describe mysql-instance \
    --format="value(settings.backupConfiguration)"

# Check operations log
gcloud sql operations list --instance=mysql-instance \
    --filter="operationType:BACKUP"

# View operation details
gcloud sql operations describe OPERATION_ID
```

**Solutions:**
- Ensure instance is running during backup window
- Check IAM permissions for service account
- Ensure sufficient storage space
- Enable binary logging for PITR

### Diagnostic Commands

```bash
# Check instance status
gcloud sql instances describe mysql-instance

# List recent operations
gcloud sql operations list --instance=mysql-instance --limit=20

# Get operation details
gcloud sql operations describe OPERATION_ID

# Wait for operation to complete
gcloud sql operations wait OPERATION_ID

# Check service account
gcloud sql instances describe mysql-instance \
    --format="value(serviceAccountEmailAddress)"

# Test connectivity
gcloud sql connect mysql-instance --user=root

# Check database flags
gcloud sql instances describe mysql-instance \
    --format="value(settings.databaseFlags)"
```

---

## ACE Exam Tips

### Key Concepts to Remember

1. **Instance Types:**
   - **Zonal:** Single zone, 99.5% SLA, lower cost
   - **Regional (HA):** Multi-zone, 99.95% SLA, automatic failover, synchronous replication

2. **Connection Methods:**
   - **Cloud SQL Auth Proxy:** Recommended, secure, no firewall config needed
   - **Private IP:** Best for same VPC, requires Private Services Access
   - **Public IP + Authorized Networks:** Static IPs only
   - **SSL/TLS:** Additional security layer

3. **Backup Types:**
   - **Automated:** Daily, 7-day retention, required for HA/PITR
   - **On-Demand:** Manual, persist until deleted
   - **PITR:** Requires binary logging, 7-day window

4. **Read Replicas:**
   - Asynchronous replication
   - Can be promoted to standalone
   - Support cross-region (DR) and cascading
   - No automatic load balancing

5. **Storage:**
   - Can only increase, never decrease
   - Auto-increase at 90% full
   - SSD recommended for production

### Common Exam Scenarios

**Scenario 1:** Need to connect Cloud Functions to Cloud SQL
- **Answer:** Use Cloud SQL Proxy (serverless connector) or Private IP

**Scenario 2:** Disaster recovery for Cloud SQL instance
- **Answer:** Create cross-region read replica, promote if primary region fails

**Scenario 3:** Minimize downtime for Cloud SQL maintenance
- **Answer:** Use regional (HA) instance for automatic failover during maintenance

**Scenario 4:** Accidentally deleted data, need to recover
- **Answer:** Use Point-in-Time Recovery (PITR) to restore to timestamp before deletion

**Scenario 5:** Read-heavy workload causing performance issues
- **Answer:** Create read replicas to offload read traffic from primary

**Scenario 6:** Need to migrate MySQL database from on-premises
- **Answer:** Use Database Migration Service or export/import via Cloud Storage

**Scenario 7:** Instance storage full, database read-only
- **Answer:** Increase storage size or enable auto-increase

**Scenario 8:** Need to prevent maintenance during Black Friday
- **Answer:** Configure deny maintenance period

### Command Cheat Sheet

```bash
# Create instance
gcloud sql instances create INSTANCE --database-version=MYSQL_8_0 --tier=db-n1-standard-2 --region=us-central1

# Enable HA
gcloud sql instances patch INSTANCE --availability-type=REGIONAL

# Create database
gcloud sql databases create DATABASE --instance=INSTANCE

# Create user
gcloud sql users create USER --instance=INSTANCE --password=PASSWORD

# Create backup
gcloud sql backups create --instance=INSTANCE

# Restore backup
gcloud sql backups restore BACKUP_ID --backup-instance=INSTANCE --restore-instance=INSTANCE

# PITR
gcloud sql instances clone SOURCE TARGET --point-in-time='TIMESTAMP'

# Create replica
gcloud sql instances create REPLICA --master-instance-name=INSTANCE --region=REGION

# Promote replica
gcloud sql instances promote-replica REPLICA

# Export
gcloud sql export sql INSTANCE gs://BUCKET/file.sql --database=DATABASE

# Import
gcloud sql import sql INSTANCE gs://BUCKET/file.sql --database=DATABASE

# Connect
gcloud sql connect INSTANCE --user=USER

# Failover
gcloud sql instances failover INSTANCE
```

---

## Additional Resources

- [Cloud SQL Documentation](https://cloud.google.com/sql/docs)
- [MySQL Documentation](https://dev.mysql.com/doc/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Database Migration Service](https://cloud.google.com/database-migration)
- [Cloud SQL Pricing](https://cloud.google.com/sql/pricing)

---

**Last Updated:** November 2025  
**Exam:** Google Associate Cloud Engineer (ACE)
