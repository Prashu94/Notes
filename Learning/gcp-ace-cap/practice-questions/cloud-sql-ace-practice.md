# Cloud SQL - ACE Practice Questions

## Question 1
You need to create a Cloud SQL MySQL instance for a production application that requires high availability. What should you configure?

**A)** Create a single instance in us-central1-a

**B)** Create a Cloud SQL instance with high availability (HA) configuration enabled

**C)** Create two separate Cloud SQL instances and set up manual replication

**D)** Use a Compute Engine VM with MySQL installed

**Correct Answer:** B

**Explanation:**
- Option B is correct because:
  - Cloud SQL HA configuration provides automatic failover
  - Creates a primary instance and a standby replica in different zones
  - Synchronous replication (no data loss on failover)
  - Automatic failover in case of zone or instance failure
  - Same regional deployment with zone redundancy

Create HA Cloud SQL instance:
```bash
# Create MySQL instance with HA
gcloud sql instances create prod-mysql \
  --database-version=MYSQL_8_0 \
  --tier=db-n1-standard-2 \
  --region=us-central1 \
  --availability-type=REGIONAL \
  --backup \
  --backup-start-time=03:00

# Verify HA configuration
gcloud sql instances describe prod-mysql \
  --format="value(settings.availabilityType)"
```

HA Configuration details:
- **Primary instance**: Handles all operations
- **Standby replica**: In different zone, same region
- **Failover time**: Typically 60-120 seconds
- **IP address**: Stays the same after failover
- **Automatic backups**: Required for HA

- Option A is incorrect because:
  - Single zone deployment (no HA)
  - Single point of failure
  - Zone outage causes downtime
  - Not suitable for production requiring HA

- Option C is incorrect because:
  - Manual replication requires more management
  - Cloud SQL HA is the managed solution
  - More complex and error-prone
  - Cloud SQL HA is designed for this use case

- Option D is incorrect because:
  - Requires manual management of MySQL
  - No automatic failover
  - More operational overhead
  - Cloud SQL is the managed database service

**HA vs Zonal:**
- **Zonal** (availability-type=ZONAL): Single zone, lower cost
- **Regional** (availability-type=REGIONAL): HA with standby replica

---

## Question 2
Your application needs to connect to Cloud SQL from a Compute Engine instance. The instance should use a private IP connection for security. What should you configure?

**A)** Enable public IP on Cloud SQL and use SSL certificates

**B)** Configure Private IP for Cloud SQL and ensure the instance is in an authorized VPC

**C)** Use Cloud SQL Proxy on the Compute Engine instance

**D)** Create a VPN connection between the instance and Cloud SQL

**Correct Answer:** B

**Explanation:**
- Option B is correct because:
  - Private IP provides secure, internal connectivity
  - No exposure to public internet
  - Lower latency than public IP
  - More secure (no external attack surface)
  - Recommended for GCP-to-Cloud SQL connections

Configure Private IP:
```bash
# 1. Enable Service Networking API
gcloud services enable servicenetworking.googleapis.com

# 2. Create private IP range
gcloud compute addresses create google-managed-services-my-vpc \
  --global \
  --purpose=VPC_PEERING \
  --prefix-length=16 \
  --network=my-vpc

# 3. Create private connection
gcloud services vpc-peerings connect \
  --service=servicenetworking.googleapis.com \
  --ranges=google-managed-services-my-vpc \
  --network=my-vpc

# 4. Create Cloud SQL instance with private IP
gcloud sql instances create private-mysql \
  --database-version=MYSQL_8_0 \
  --tier=db-n1-standard-1 \
  --region=us-central1 \
  --network=projects/PROJECT_ID/global/networks/my-vpc \
  --no-assign-ip

# 5. Get private IP address
gcloud sql instances describe private-mysql \
  --format="value(ipAddresses[0].ipAddress)"

# 6. Connect from Compute Engine instance (in same VPC)
mysql -h PRIVATE_IP -u root -p
```

- Option A is incorrect because:
  - Public IP exposes database to internet
  - Less secure even with SSL
  - Not following security best practice for GCP-internal connections
  - Higher attack surface

- Option C is incorrect because:
  - Cloud SQL Proxy is useful but not necessary for private IP
  - Proxy can work with both public and private IP
  - Private IP is the more direct solution
  - Proxy adds extra component

- Option D is incorrect because:
  - VPN is for external/on-premises connections
  - Not needed for GCP-to-GCP connections
  - Unnecessary complexity
  - Private IP is the native solution

**Connection Methods:**
- **Private IP**: Direct VPC connection (recommended for GCP resources)
- **Public IP + Cloud SQL Proxy**: For external applications
- **Public IP + Authorized Networks**: Less secure, not recommended
- **Private IP + Cloud SQL Proxy**: Extra security layer

---

## Question 3
You need to restore a Cloud SQL database to a specific point in time from 2 days ago. What should you do?

**A)** Create a new instance from the most recent automated backup

**B)** Use point-in-time recovery (PITR) to restore to the exact timestamp

**C)** Restore from a manual snapshot taken 2 days ago

**D)** Export the database and import it to a new instance

**Correct Answer:** B

**Explanation:**
- Option B is correct because:
  - Point-in-time recovery allows restore to any second within retention period
  - Uses binary logs to replay transactions
  - More precise than daily backups
  - Can recover to exact moment before an error

Point-in-time recovery:
```bash
# 1. Verify PITR is enabled (automatic backups required)
gcloud sql instances describe my-instance \
  --format="value(settings.backupConfiguration.enabled)"

# 2. Clone instance to specific point in time
gcloud sql instances clone my-instance my-instance-restored \
  --point-in-time='2024-11-21T14:30:00.000Z'

# OR restore using backup and PITR
gcloud sql backups list --instance=my-instance

# 3. Create instance from backup
gcloud sql instances restore-backup my-instance \
  --backup-id=1234567890

# Alternative: Clone to new instance at specific time
gcloud sql instances clone source-instance clone-instance \
  --point-in-time='2024-11-21T10:00:00.000Z'
```

PITR requirements:
- Automated backups must be enabled
- Binary logging enabled (MySQL) or WAL enabled (PostgreSQL)
- Can restore to any point within retention period (default 7 days)

- Option A is incorrect because:
  - Backups are taken once per day
  - Cannot restore to specific time between backups
  - Less precise than PITR
  - Might lose up to 24 hours of data

- Option C is incorrect because:
  - Manual snapshots are taken at specific times only
  - No guarantee a snapshot was taken exactly 2 days ago
  - Less flexible than PITR

- Option D is incorrect because:
  - Export/import is manual and time-consuming
  - Not designed for point-in-time recovery
  - More complex than using built-in PITR

**Backup vs PITR:**
- **Automated Backups**: Daily snapshots (+ binary logs for PITR)
- **PITR**: Restore to any second (using backups + binary logs)
- **Manual Backups**: On-demand snapshots

---

## Question 4
Your Cloud SQL instance is experiencing high CPU usage. You need to scale it to a larger machine type. What is the impact of this operation?

**A)** No downtime; scaling happens live

**B)** Brief downtime (a few minutes) during the resize

**C)** Instance must be stopped first, then resized

**D)** Data must be exported and re-imported to a new instance

**Correct Answer:** B

**Explanation:**
- Option B is correct because:
  - Changing machine type (tier) requires instance restart
  - Typically 3-5 minutes of downtime
  - HA instances failover to standby (less downtime)
  - Automatic process managed by Google

Scale Cloud SQL instance:
```bash
# Scale up to larger tier
gcloud sql instances patch my-instance \
  --tier=db-n1-standard-4

# The instance will:
# 1. Be marked as PENDING_UPDATE
# 2. Complete current transactions
# 3. Restart with new tier
# 4. Come back online (3-5 minutes)

# For HA instances:
# - Standby is updated first
# - Then failover to standby (updated)
# - Original primary is updated
# - Minimal downtime (~60-120 seconds)

# Check instance state
gcloud sql instances describe my-instance \
  --format="value(state,settings.tier)"

# Scale down (also causes restart)
gcloud sql instances patch my-instance \
  --tier=db-n1-standard-2
```

Scaling considerations:
- **Storage**: Can be increased without restart (no downtime)
- **Machine type**: Requires restart (brief downtime)
- **HA instances**: Automatic failover reduces downtime
- **Read replicas**: Not affected during primary scaling

- Option A is incorrect because:
  - Machine type changes require restart
  - Cannot resize CPU/RAM without restart
  - Storage increases are online, but not tier changes

- Option C is incorrect because:
  - Don't need to manually stop instance
  - Automatic process handles shutdown/restart
  - More disruptive than automatic scaling

- Option D is incorrect because:
  - Export/import not required
  - Scaling happens in place
  - Would take much longer and cause more downtime

**Scale without downtime (alternatives):**
1. Use read replicas for read traffic
2. Scale during maintenance window
3. For HA instances, failover minimizes downtime

---

## Question 5
You need to migrate an on-premises MySQL database to Cloud SQL with minimal downtime. What should you use?

**A)** Export the database using mysqldump and import to Cloud SQL

**B)** Use Database Migration Service (DMS)

**C)** Manually set up replication from on-premises to Cloud SQL

**D)** Take a snapshot and upload to Cloud SQL

**Correct Answer:** B

**Explanation:**
- Option B is correct because:
  - Database Migration Service is designed for minimal-downtime migrations
  - Continuous replication from source to target
  - Automated process with monitoring
  - Can cutover when ready (minimal downtime)
  - Supports MySQL, PostgreSQL, SQL Server

Database Migration Service:
```bash
# 1. Enable DMS API
gcloud services enable datamigration.googleapis.com

# 2. Create connection profile for source (on-premises)
gcloud database-migration connection-profiles create mysql-source \
  --region=us-central1 \
  --host=SOURCE_IP \
  --port=3306 \
  --username=root \
  --password=PASSWORD

# 3. Create connection profile for Cloud SQL destination
gcloud database-migration connection-profiles create mysql-dest \
  --region=us-central1 \
  --cloudsql-instance=projects/PROJECT_ID/instances/INSTANCE_NAME

# 4. Create migration job
gcloud database-migration migration-jobs create my-migration \
  --region=us-central1 \
  --type=CONTINUOUS \
  --source=mysql-source \
  --destination=mysql-dest \
  --display-name="MySQL Migration"

# 5. Start migration
gcloud database-migration migration-jobs start my-migration \
  --region=us-central1

# 6. Monitor migration
gcloud database-migration migration-jobs describe my-migration \
  --region=us-central1

# 7. When ready, promote (cutover)
gcloud database-migration migration-jobs promote my-migration \
  --region=us-central1
```

Migration process:
1. **Initial snapshot**: Full database copy
2. **Continuous replication**: Ongoing changes replicated
3. **Cutover**: Switch applications to Cloud SQL (brief downtime)

- Option A is incorrect because:
  - mysqldump requires downtime during export/import
  - No continuous replication
  - All changes during export/import would be lost
  - High downtime for large databases

- Option C is incorrect because:
  - Manual replication is complex to set up
  - Error-prone
  - DMS is the managed solution
  - More operational overhead

- Option D is incorrect because:
  - Snapshots require downtime
  - No continuous replication
  - Similar to mysqldump approach

**Migration Options:**
- **DMS (Continuous)**: Minimal downtime, recommended
- **DMS (One-time)**: For offline migrations
- **mysqldump**: Simple but requires downtime
- **External replica**: Manual, complex

---

## Question 6
You need to create a read replica of your Cloud SQL instance in a different region for disaster recovery. What command should you use?

**A)**
```bash
gcloud sql instances patch my-instance --enable-read-replica
```

**B)**
```bash
gcloud sql instances create my-replica \
  --master-instance-name=my-instance \
  --region=europe-west1
```

**C)**
```bash
gcloud sql instances clone my-instance my-replica \
  --region=europe-west1
```

**D)**
```bash
gcloud sql replicas create my-replica \
  --instance=my-instance \
  --region=europe-west1
```

**Correct Answer:** B

**Explanation:**
- Option B is correct because:
  - Creates a read replica in specified region
  - `--master-instance-name` links replica to primary
  - Can be in different region (cross-region replica)
  - Asynchronous replication

Create read replica:
```bash
# Create read replica in same region
gcloud sql instances create my-replica \
  --master-instance-name=my-instance \
  --tier=db-n1-standard-1 \
  --region=us-central1

# Create cross-region read replica (DR)
gcloud sql instances create my-dr-replica \
  --master-instance-name=my-instance \
  --tier=db-n1-standard-2 \
  --region=europe-west1

# List replicas
gcloud sql instances list --filter="masterInstanceName:my-instance"

# Promote replica to standalone instance (DR failover)
gcloud sql instances promote-replica my-dr-replica

# Delete replica
gcloud sql instances delete my-replica
```

Read replica use cases:
- **Disaster recovery**: Cross-region replica
- **Read scaling**: Distribute read load
- **Analytics**: Separate analytical queries
- **Reporting**: Offload reporting workload

- Option A is incorrect because:
  - No such parameter exists
  - Replicas are created as separate instances
  - Not how you enable replication

- Option C is incorrect because:
  - `clone` creates an independent copy (not a replica)
  - Clone is a one-time operation
  - No ongoing replication

- Option D is incorrect because:
  - Wrong command structure
  - Should be `sql instances create`, not `sql replicas create`

**Clone vs Replica:**
- **Clone**: Independent instance, point-in-time copy
- **Replica**: Continuously replicating instance, read-only

Replica limitations:
- Read-only (cannot write to replica)
- Asynchronous replication (slight lag)
- Can be promoted to standalone instance

---

## Question 7
Your application requires a managed PostgreSQL database that supports storing and querying geographical data. What should you use?

**A)** Cloud SQL for PostgreSQL with PostGIS extension

**B)** Cloud Spanner

**C)** Firestore

**D)** BigQuery with geography data types

**Correct Answer:** A

**Explanation:**
- Option A is correct because:
  - Cloud SQL for PostgreSQL supports extensions
  - PostGIS is a spatial database extension for PostgreSQL
  - Provides geography/geometry data types
  - Spatial queries and functions
  - Fully managed by Cloud SQL

Enable PostGIS:
```bash
# 1. Create PostgreSQL instance
gcloud sql instances create my-postgres \
  --database-version=POSTGRES_14 \
  --tier=db-custom-2-7680 \
  --region=us-central1

# 2. Create database
gcloud sql databases create mydb \
  --instance=my-postgres

# 3. Connect and enable PostGIS
gcloud sql connect my-postgres --user=postgres

# In psql:
\c mydb
CREATE EXTENSION postgis;

# Verify
SELECT PostGIS_version();

# Create table with geography column
CREATE TABLE locations (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100),
  location GEOGRAPHY(POINT, 4326)
);

# Insert geographical data
INSERT INTO locations (name, location)
VALUES ('Google HQ', ST_GeogFromText('POINT(-122.0840 37.4220)'));

# Query: Find locations within 10km
SELECT name 
FROM locations 
WHERE ST_DWithin(
  location,
  ST_GeogFromText('POINT(-122.0840 37.4220)'),
  10000  -- meters
);
```

- Option B is incorrect because:
  - Cloud Spanner doesn't have built-in geospatial support
  - No PostGIS or geography extensions
  - Different use case (globally distributed SQL)

- Option C is incorrect because:
  - Firestore is a NoSQL document database
  - Limited geospatial query capabilities
  - Not a relational database with SQL

- Option D is incorrect because:
  - BigQuery is for analytics, not transactional workloads
  - While it supports geography types, it's not for application databases
  - Different use case

**Cloud SQL Extensions:**
- **PostgreSQL**: PostGIS, pgaudit, pg_cron, etc.
- **MySQL**: Limited extensions (differs from PostgreSQL)

---

## Question 8
You need to connect to Cloud SQL from Cloud Run. The connection should be secure and efficient. What should you use?

**A)** Public IP with authorized networks

**B)** Cloud SQL Proxy sidecar container

**C)** Direct connection using private IP

**D)** Cloud SQL Auth Proxy via Unix socket

**Correct Answer:** D

**Explanation:**
- Option D is correct because:
  - Cloud SQL Auth Proxy is the recommended way for Cloud Run
  - Uses Unix sockets for local connection
  - Automatic IAM authentication
  - Encrypted connection
  - No need to manage IPs or credentials

Configure Cloud Run with Cloud SQL:
```bash
# Deploy Cloud Run service with Cloud SQL connection
gcloud run deploy my-app \
  --image=gcr.io/PROJECT_ID/my-app \
  --region=us-central1 \
  --add-cloudsql-instances=PROJECT_ID:us-central1:my-instance \
  --set-env-vars=DB_USER=myuser,DB_NAME=mydb \
  --set-secrets=DB_PASS=db-password:latest

# In application code (Python example):
import os
import sqlalchemy

# Create connection pool
db_user = os.environ["DB_USER"]
db_pass = os.environ["DB_PASS"]
db_name = os.environ["DB_NAME"]
db_socket_dir = "/cloudsql"
instance_connection_name = "PROJECT_ID:us-central1:my-instance"

pool = sqlalchemy.create_engine(
    sqlalchemy.engine.url.URL.create(
        drivername="postgresql+pg8000",
        username=db_user,
        password=db_pass,
        database=db_name,
        query={
            "unix_sock": f"{db_socket_dir}/{instance_connection_name}/.s.PGSQL.5432"
        }
    )
)

# Use connection
with pool.connect() as conn:
    result = conn.execute("SELECT * FROM users")
```

Dockerfile with Cloud SQL Proxy:
```dockerfile
FROM python:3.9-slim

# Copy application
COPY . /app
WORKDIR /app

# Install dependencies
RUN pip install -r requirements.txt

# Start application
CMD ["python", "app.py"]
```

- Option A is incorrect because:
  - Public IP with authorized networks is less secure
  - Requires managing IP whitelists
  - Cloud Run IPs can change
  - Not the recommended approach

- Option B is incorrect because:
  - Sidecar containers not needed with Cloud Run
  - Cloud Run has built-in Cloud SQL connector
  - More complex than necessary

- Option C is incorrect because:
  - Cloud Run cannot directly use private IP
  - Serverless VPC Access required (more complex)
  - Cloud SQL Proxy is simpler for Cloud Run

**Cloud SQL Connection from GCP Services:**
- **Cloud Run/Functions**: Cloud SQL Proxy (recommended)
- **GKE**: Cloud SQL Proxy sidecar or Workload Identity
- **Compute Engine**: Private IP (recommended) or Proxy
- **App Engine**: Built-in Cloud SQL connector

---

## Question 9
You need to export data from a Cloud SQL database to Cloud Storage for analysis. What is the correct command?

**A)**
```bash
gcloud sql export csv my-instance gs://my-bucket/export.csv \
  --database=mydb \
  --query="SELECT * FROM users"
```

**B)**
```bash
gcloud sql export sql my-instance gs://my-bucket/export.sql \
  --database=mydb
```

**C)**
```bash
gsutil cp cloudsql://my-instance/mydb gs://my-bucket/export.sql
```

**D)**
```bash
mysqldump my-instance > gs://my-bucket/export.sql
```

**Correct Answer:** B

**Explanation:**
- Option B is correct because:
  - Exports entire database to Cloud Storage
  - SQL format (for re-import)
  - Managed export operation
  - Can export specific databases or tables

Export from Cloud SQL:
```bash
# Export entire database (SQL format)
gcloud sql export sql my-instance gs://my-bucket/backup.sql \
  --database=mydb

# Export specific tables
gcloud sql export sql my-instance gs://my-bucket/users-export.sql \
  --database=mydb \
  --table=users,orders

# Export to CSV
gcloud sql export csv my-instance gs://my-bucket/export.csv \
  --database=mydb \
  --query="SELECT id, name, email FROM users WHERE active = true"

# Export entire instance (all databases)
gcloud sql export sql my-instance gs://my-bucket/full-backup.sql

# Check export operation status
gcloud sql operations list --instance=my-instance
```

Import to Cloud SQL:
```bash
# Import SQL file
gcloud sql import sql my-instance gs://my-bucket/backup.sql \
  --database=mydb

# Import CSV
gcloud sql import csv my-instance gs://my-bucket/data.csv \
  --database=mydb \
  --table=users
```

- Option A is incorrect because:
  - CSV export with query is correct syntax
  - But the question asks for general database export
  - SQL format is more typical for full database export

- Option C is incorrect because:
  - `gsutil` cannot directly access Cloud SQL
  - Wrong command structure
  - `cloudsql://` is not a valid URI scheme

- Option D is incorrect because:
  - `mysqldump` cannot write directly to Cloud Storage
  - Would need to dump to local file first, then upload
  - `gcloud sql export` is the managed approach

**Export formats:**
- **SQL**: Full database with schema and data
- **CSV**: Data only, for specific query results

Requirements:
- Cloud Storage bucket in same project (or granted access)
- Cloud SQL service account needs Storage Object Admin role

---

## Question 10
You need to secure your Cloud SQL instance by limiting which IP addresses can connect. What should you configure?

**A)** VPC firewall rules

**B)** Authorized networks in Cloud SQL

**C)** Cloud Armor security policies

**D)** IAM policies with IP address conditions

**Correct Answer:** B

**Explanation:**
- Option B is correct because:
  - Authorized networks whitelist specific IP ranges
  - Applied at Cloud SQL level
  - Only affects public IP connections
  - Simple and effective for known IP ranges

Configure authorized networks:
```bash
# Add authorized network
gcloud sql instances patch my-instance \
  --authorized-networks=203.0.113.0/24,198.51.100.0/24

# Add single IP
gcloud sql instances patch my-instance \
  --authorized-networks=203.0.113.50/32

# Remove all authorized networks (block all public access)
gcloud sql instances patch my-instance \
  --clear-authorized-networks

# View current authorized networks
gcloud sql instances describe my-instance \
  --format="value(settings.ipConfiguration.authorizedNetworks)"
```

Best practices:
```bash
# Better: Use private IP instead of public
gcloud sql instances create secure-instance \
  --database-version=MYSQL_8_0 \
  --tier=db-n1-standard-1 \
  --region=us-central1 \
  --network=projects/PROJECT_ID/global/networks/my-vpc \
  --no-assign-ip

# If public IP needed, restrict to specific IPs
gcloud sql instances patch my-instance \
  --authorized-networks=OFFICE_IP/32 \
  --require-ssl
```

- Option A is incorrect because:
  - VPC firewall rules don't control Cloud SQL access
  - Cloud SQL is a managed service outside your VPC (unless using private IP)
  - Different security layer

- Option C is incorrect because:
  - Cloud Armor is for HTTP(S) load balancers
  - Not applicable to database connections
  - Wrong service

- Option D is incorrect because:
  - IAM controls who can manage Cloud SQL, not which IPs can connect
  - IAM conditions don't restrict database connection IPs
  - Different purpose

**Security layers:**
- **Authorized Networks**: IP whitelist for public connections
- **Private IP**: No public internet exposure
- **SSL/TLS**: Encrypted connections (always recommended)
- **IAM**: Controls who can manage the instance
- **Cloud SQL Proxy**: Automatic encryption and IAM auth
