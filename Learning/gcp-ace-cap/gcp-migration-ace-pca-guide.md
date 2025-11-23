# Google Cloud Migration Services - ACE & PCA Comprehensive Guide

## Table of Contents
1. [Overview](#overview)
2. [Migration Strategies](#migration-strategies)
3. [Migration Planning](#migration-planning)
4. [Compute Migration Services](#compute-migration-services)
5. [Database Migration Services](#database-migration-services)
6. [Data Transfer Services](#data-transfer-services)
7. [Application Migration](#application-migration)
8. [Migration Best Practices](#migration-best-practices)
9. [Post-Migration Optimization](#post-migration-optimization)
10. [Exam Tips](#exam-tips)

---

## Overview

Google Cloud provides multiple services to migrate workloads from on-premises or other clouds to GCP. Understanding which service to use is critical for both ACE and PCA exams.

**Migration Services Overview:**

| Service | Use Case | Source | Destination |
|---------|----------|--------|-------------|
| **Migrate for Compute Engine** | VM migration | VMware, AWS EC2, Azure VMs | Compute Engine |
| **Database Migration Service** | Database migration | MySQL, PostgreSQL, SQL Server | Cloud SQL, AlloyDB |
| **Storage Transfer Service** | Online data transfer | AWS S3, Azure Blob, HTTP(S) | Cloud Storage |
| **Transfer Appliance** | Offline data transfer | On-premises | Cloud Storage |
| **BigQuery Data Transfer** | SaaS data import | YouTube, Google Ads, S3 | BigQuery |
| **Migrate for Anthos** | Containerization | VMs | GKE/Anthos |

---

## Migration Strategies

### The 6 R's of Migration

**1. Rehost ("Lift and Shift")**
- Move VMs as-is to cloud
- Minimal changes
- Fast migration
- **Tool:** Migrate for Compute Engine

**Use Case:**
- Quick cloud migration
- Legacy apps that can't be modified
- Time-sensitive migrations

**2. Replatform ("Lift, Tinker, and Shift")**
- Minor optimizations during migration
- Switch to managed services
- **Example:** On-prem MySQL → Cloud SQL

**Use Case:**
- Reduce operational overhead
- Take advantage of managed services
- Minimal code changes

**3. Repurchase ("Drop and Shop")**
- Switch to SaaS product
- **Example:** Exchange → Google Workspace

**Use Case:**
- Outdated software
- SaaS alternative available

**4. Refactor/Re-architect**
- Redesign application for cloud
- Containerize, use microservices
- **Tool:** Migrate for Anthos

**Use Case:**
- Maximize cloud benefits
- Application modernization
- Long-term strategy

**5. Retire**
- Decommission unused applications
- **No migration needed**

**Use Case:**
- Reduce costs
- Technical debt cleanup

**6. Retain**
- Keep on-premises
- **No migration**

**Use Case:**
- Compliance requirements
- Not cloud-ready

---

## Migration Planning

### Phase 1: Assess

**Discover your infrastructure:**
```bash
# Use StratoZone or manual assessment
# Inventory:
- VMs and physical servers
- Databases
- Applications
- Dependencies
- Network topology
- Storage requirements
```

**Key Questions:**
- What applications do we have?
- What are dependencies?
- What's our data volume?
- What are compliance requirements?

### Phase 2: Plan

**Create Migration Plan:**
1. Categorize workloads (by migration strategy)
2. Prioritize migrations (quick wins first)
3. Define success criteria
4. Estimate costs
5. Plan network connectivity

**Example Prioritization:**
```
Wave 1 (Quick Wins):
  - Dev/Test environments
  - Stateless web apps
  
Wave 2 (Low Risk):
  - Non-critical databases
  - Batch processing systems

Wave 3 (Complex):
  - Production databases
  - Mission-critical applications
```

### Phase 3: Deploy

**Execute Migration:**
1. Set up networking (VPN/Interconnect)
2. Migrate workloads
3. Test thoroughly
4. Cutover

### Phase 4: Optimize

**Post-Migration:**
1. Right-size resources
2. Implement autoscaling
3. Use managed services
4. Apply cost optimization

---

## Compute Migration Services

### Migrate for Compute Engine

**What it does:**
Migrates VMs from VMware, AWS, Azure, or physical servers to Compute Engine.

**Key Features:**
- Minimal downtime
- Continuous replication
- Automated testing
- Rollback capability

### Architecture

```
Source Environment (VMware/AWS/Azure)
    ↓
Migrate for Compute Engine Manager (in GCP)
    ↓
Replication to Cloud Storage
    ↓
Test Clone VMs
    ↓
Final Cutover to Compute Engine
```

### Migration Process

**1. Install Migration Manager:**
```bash
# Deploy Migrate for Compute Engine backend
# (Done via GCP Console or Terraform)
```

**2. Add Source Environment:**
```bash
# Add VMware vCenter
# Console: Migrate for Compute Engine → Sources → Add Source
# Credentials: vCenter URL, username, password
```

**3. Create Migration Waves:**
```
Wave 1: Dev VMs (test migration)
Wave 2: UAT VMs
Wave 3: Production VMs
```

**4. Runbook Creation:**
```yaml
# Define migration steps
- name: "Web Server Migration"
  source: "vm-web-01"
  target:
    machine_type: "n2-standard-4"
    zone: "us-central1-a"
    network: "default"
```

**5. Execute Migration:**
```
1. Replication: Continuous sync from source to GCP
2. Test Clone: Create test VM, validate
3. Cutover: 
   - Shutdown source VM
   - Final sync
   - Start target VM
   - Update DNS
```

### Migration Types

**Full Migration:**
- Complete VM migration
- VM runs on Compute Engine
- Source VM decommissioned

**Migration with Modernization:**
- Migrate to Compute Engine
- Then containerize with Migrate for Anthos

### Supported Sources

**VMware:**
- vSphere 5.5+
- VMs with VMDK disks

**AWS:**
- EC2 instances
- Most instance types

**Azure:**
- Azure VMs
- Most VM sizes

**Physical Servers:**
- Linux/Windows servers
- Via agent installation

---

## Database Migration Services

### Database Migration Service (DMS)

**What it does:**
Migrates databases to Cloud SQL, AlloyDB, or Spanner with minimal downtime.

**Supported Sources:**
- MySQL
- PostgreSQL
- SQL Server
- Oracle (via third-party tools)

### Create Migration Job

**Via Console:**
1. **Database Migration** → **Create Migration Job**
2. Configure:
   - **Source:** Connection details
   - **Destination:** Cloud SQL instance
   - **Migration type:** Continuous or one-time
3. **Test Connection**
4. **Start Migration**

**Via gcloud:**
```bash
# Create connection profile for source
gcloud database-migration connection-profiles create mysql source-mysql \
  --region=us-central1 \
  --host=10.0.0.5 \
  --port=3306 \
  --username=root \
  --password=PASSWORD

# Create connection profile for destination (Cloud SQL)
gcloud database-migration connection-profiles create mysql dest-cloudsql \
  --region=us-central1 \
  --cloudsql-instance=my-cloudsql-instance

# Create migration job
gcloud database-migration migration-jobs create my-migration \
  --region=us-central1 \
  --type=CONTINUOUS \
  --source=source-mysql \
  --destination=dest-cloudsql \
  --display-name="MySQL Migration"
```

### Migration Types

**1. Continuous (Minimal Downtime):**
```
1. Initial snapshot
2. Continuous replication (CDC)
3. Cutover when ready
```

**Downtime:** Minutes (during cutover)

**2. One-Time (Full Dump):**
```
1. Full backup
2. Restore to Cloud SQL
3. Application cutover
```

**Downtime:** Hours (depending on size)

### Migration Process

**Phase 1: Setup**
```bash
# Create destination Cloud SQL instance
gcloud sql instances create my-cloudsql \
  --database-version=MYSQL_8_0 \
  --tier=db-n1-standard-4 \
  --region=us-central1 \
  --network=projects/PROJECT_ID/global/networks/default
```

**Phase 2: Full Dump**
```bash
# Create initial snapshot
# DMS automatically handles this
```

**Phase 3: CDC (Change Data Capture)**
```
# Continuous replication of changes
# Keeps destination in sync with source
```

**Phase 4: Promote**
```bash
# Verify data integrity
# Stop application
# Promote replica to primary
gcloud database-migration migration-jobs promote my-migration --region=us-central1

# Update application connection strings
# Start application
```

### Monitoring Migration

```bash
# Check migration status
gcloud database-migration migration-jobs describe my-migration \
  --region=us-central1

# View migration progress
# Console shows:
- Replication lag
- Data transferred
- Tables migrated
```

---

## Data Transfer Services

### Storage Transfer Service

**What it does:**
Transfers data from online sources (AWS S3, Azure, HTTP) to Cloud Storage.

**Use Cases:**
- Migrate from AWS S3 to GCS
- Backup from Azure Blob to GCS
- Periodic data sync

**Create Transfer Job:**

**Via Console:**
1. **Storage Transfer Service** → **Create Transfer Job**
2. **Source:**
   - AWS S3, Azure, HTTP, or another GCS bucket
3. **Destination:** GCS bucket
4. **Schedule:** One-time or recurring
5. **Options:**
   - Delete from source
   - Overwrite destination
6. **Create Job**

**Transfer from AWS S3:**
```bash
# Create transfer job
gcloud transfer jobs create gs://my-destination-bucket \
  --source-creds-file=aws-credentials.json \
  --source-bucket=s3://my-source-bucket \
  --schedule-starts=2024-01-01T00:00:00Z \
  --schedule-repeats-every=24h
```

**aws-credentials.json:**
```json
{
  "type": "aws",
  "accessKeyId": "AKIAIOSFODNN7EXAMPLE",
  "secretAccessKey": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
}
```

**Transfer from Azure:**
```bash
gcloud transfer jobs create gs://my-destination-bucket \
  --source-creds-file=azure-credentials.json \
  --source-container=my-azure-container \
  --schedule-starts=2024-01-01T00:00:00Z
```

**Transfer Options:**
```bash
# Delete source files after transfer
--delete-from-source

# Overwrite destination files
--overwrite-when=DIFFERENT

# Transfer only new/modified files
--overwrite-when=NEVER
```

**Monitor Transfer:**
```bash
# List jobs
gcloud transfer jobs list

# Describe job
gcloud transfer jobs describe JOB_NAME

# Monitor via console for detailed stats
```

### Transfer Appliance

**What it does:**
Physical device shipped to you for offline data transfer.

**Use Cases:**
- Large datasets (>20 TB)
- Limited bandwidth
- Faster than network transfer

**Capacity:**
- TA40: 40 TB usable (~60 TB raw)
- TA300: 300 TB usable (~480 TB raw)

**Process:**
```
1. Order appliance (Console)
2. Google ships appliance to you
3. Connect to your network
4. Copy data to appliance
5. Ship back to Google
6. Google uploads data to GCS
7. Google securely wipes appliance
```

**Ordering:**
```bash
# Order via Console only
# Go to: Transfer Appliance → Create Order
# Fill out:
- Shipping address
- Network configuration
- Destination bucket
- Import schedule
```

**Cost:**
- Appliance rental: ~$300/day
- Shipping costs
- Ingress to GCP: Free

### BigQuery Data Transfer Service

**What it does:**
Automatically loads data from SaaS apps and other sources into BigQuery.

**Data Sources:**
- Google Ads
- Google Analytics 360
- YouTube
- AWS S3
- Cloud Storage
- Teradata
- Amazon Redshift

**Create Transfer:**
```bash
# Transfer from Cloud Storage to BigQuery
bq mk --transfer_config \
  --project_id=my-project \
  --data_source=google_cloud_storage \
  --display_name="Daily CSV Load" \
  --schedule="every day 01:00" \
  --params='{
    "destination_table_name_template":"my_table",
    "data_path_template":"gs://my-bucket/data/*.csv",
    "write_disposition":"APPEND",
    "file_format":"CSV"
  }'
```

**Transfer from AWS S3:**
```bash
bq mk --transfer_config \
  --project_id=my-project \
  --data_source=amazon_s3 \
  --display_name="S3 to BigQuery" \
  --params='{
    "destination_table_name_template":"imported_data",
    "data_path":"s3://my-bucket/data/*.parquet",
    "access_key_id":"AKIAIOSFODNN7EXAMPLE",
    "secret_access_key":"SECRET",
    "file_format":"PARQUET"
  }'
```

---

## Application Migration

### Migrate for Anthos

**What it does:**
Migrates VMs to containers running on GKE/Anthos.

**Process:**
```
Source VM (VMware/AWS/Azure/Compute Engine)
    ↓
Automated Analysis & Containerization
    ↓
Container Image
    ↓
Deploy to GKE
```

**Benefits:**
- Automated containerization
- No code changes required
- Modernize legacy apps

**Migration Flow:**
```bash
# 1. Analyze VM
migctl migration create my-migration --source vm-source

# 2. Generate artifacts
# - Dockerfile
# - Deployment YAML
# - ConfigMaps

# 3. Review and customize

# 4. Deploy to GKE
kubectl apply -f deployment.yaml
```

### Migrate to Cloud Run

**Manual Migration:**
```bash
# 1. Containerize application
cat > Dockerfile <<EOF
FROM node:16
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
CMD ["npm", "start"]
EOF

# 2. Build container
gcloud builds submit --tag gcr.io/my-project/my-app

# 3. Deploy to Cloud Run
gcloud run deploy my-app \
  --image gcr.io/my-project/my-app \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

## Migration Best Practices

### 1. Start Small

**Pilot Migration:**
- Choose non-critical workload
- Validate process
- Learn lessons
- Apply to larger migrations

### 2. Network Connectivity

**Establish Before Migration:**
```bash
# Cloud VPN
gcloud compute vpn-tunnels create my-vpn-tunnel \
  --peer-address=ON_PREM_IP \
  --shared-secret=SECRET \
  --target-vpn-gateway=my-gateway

# OR Cloud Interconnect (for large data)
# Higher bandwidth, lower latency
```

### 3. Data Validation

**Verify Data Integrity:**
```bash
# Compare row counts
# Source
mysql> SELECT COUNT(*) FROM users;

# Destination
gcloud sql connect my-cloudsql --user=root
mysql> SELECT COUNT(*) FROM users;

# Compare checksums
# Use data validation tools
```

### 4. Cutover Planning

**Minimize Downtime:**
```
Friday 10 PM: Stop writes to source
Friday 10:05 PM: Final sync
Friday 10:15 PM: Promote destination
Friday 10:20 PM: Update DNS/load balancer
Friday 10:30 PM: Verify application
Friday 10:45 PM: Monitor
Saturday 8 AM: Declare success
```

### 5. Rollback Plan

**Always Have Backup:**
```
If migration fails:
1. Revert DNS to source
2. Re-enable source systems
3. Investigate issues
4. Plan retry
```

### 6. Testing

**Test Everything:**
- Application functionality
- Performance benchmarks
- Disaster recovery
- Monitoring/alerting

### 7. Documentation

**Document:**
- Architecture diagrams
- Migration runbooks
- Cutover procedures
- Rollback plans
- Post-migration tasks

---

## Post-Migration Optimization

### 1. Right-Sizing

**Analyze Utilization:**
```bash
# View rightsizing recommendations
gcloud compute instances list --format=table

# Cloud Console: Compute Engine → Recommendations
```

**Resize VMs:**
```bash
gcloud compute instances set-machine-type my-vm \
  --zone=us-central1-a \
  --machine-type=n2-standard-4
```

### 2. Managed Services

**Replace DIY with Managed:**
- Self-managed MySQL → Cloud SQL
- Self-managed Redis → Memorystore
- Self-managed Kafka → Pub/Sub

### 3. Auto-Scaling

**Implement MIGs:**
```bash
# Create instance template
gcloud compute instance-templates create my-template \
  --machine-type=n2-standard-2 \
  --image-family=debian-11 \
  --boot-disk-size=20GB

# Create autoscaling MIG
gcloud compute instance-groups managed create my-mig \
  --base-instance-name=my-vm \
  --template=my-template \
  --size=3 \
  --zone=us-central1-a

# Configure autoscaling
gcloud compute instance-groups managed set-autoscaling my-mig \
  --zone=us-central1-a \
  --min-num-replicas=2 \
  --max-num-replicas=10 \
  --target-cpu-utilization=0.7
```

### 4. Cost Optimization

**Apply Cost-Saving Strategies:**
- Committed Use Discounts
- Spot VMs for batch workloads
- Storage lifecycle policies
- Idle resource cleanup

### 5. Security Hardening

**Implement Cloud Security:**
```bash
# Enable VPC Service Controls
# Implement Cloud Armor
# Use managed SSL certificates
# Enable Cloud Audit Logs
```

---

## Exam Tips

### ACE Exam Focus

**1. Service Selection:**

| Scenario | Service |
|----------|---------|
| Migrate VMs from VMware | Migrate for Compute Engine |
| Migrate MySQL database | Database Migration Service |
| Transfer files from AWS S3 | Storage Transfer Service |
| Transfer 100 TB offline | Transfer Appliance |

**2. Migration Strategies:**
- **Rehost:** Lift and shift (fastest)
- **Replatform:** Minor changes (managed services)
- **Refactor:** Containerize (long-term)

**3. Data Transfer:**
- **< 1 TB + good bandwidth:** gsutil or Storage Transfer
- **1-20 TB:** Storage Transfer Service
- **> 20 TB + limited bandwidth:** Transfer Appliance

### PCA Exam Focus

**1. Migration Strategy Selection:**

**Choose Rehost When:**
- Time-sensitive migration
- Legacy app that can't change
- Compliance requires exact replication

**Choose Replatform When:**
- Want managed services
- Minor modernization acceptable
- Reduce operational overhead

**Choose Refactor When:**
- Long-term cloud strategy
- Application modernization goal
- Maximize cloud benefits

**2. Network Planning:**

**VPN vs Interconnect:**
- **VPN:** < 3 Gbps, encryption required, quick setup
- **Interconnect:** > 10 Gbps, low latency, enterprise

**3. Database Migration:**

**Minimal Downtime:**
- Use Database Migration Service (continuous mode)
- CDC replication
- Cutover during maintenance window

**Acceptable Downtime:**
- One-time migration (dump/restore)
- Simpler, less complex

**4. Hybrid Migration:**

**Gradual Migration:**
```
Phase 1: Non-production (dev/test)
Phase 2: Non-critical production
Phase 3: Critical production
```

**Hybrid Operation:**
- Some workloads on-prem
- Some in cloud
- Connected via Interconnect

### Exam Scenarios

**Scenario:** "Migrate 50 TB from on-premises to Cloud Storage with limited bandwidth"
**Solution:** Transfer Appliance

**Scenario:** "Migrate MySQL database to Cloud SQL with < 5 minutes downtime"
**Solution:** Database Migration Service (continuous mode)

**Scenario:** "Migrate 500 VMs from VMware to Compute Engine"
**Solution:** Migrate for Compute Engine

**Scenario:** "Daily import of data from AWS S3 to Cloud Storage"
**Solution:** Storage Transfer Service with schedule

**Scenario:** "Modernize legacy app by containerizing and moving to GKE"
**Solution:** Migrate for Anthos

**Scenario:** "Migrate PostgreSQL from AWS RDS to Cloud SQL"
**Solution:** Database Migration Service

---

## Quick Reference

```bash
# Database Migration Service
gcloud database-migration migration-jobs create JOB_NAME --region=REGION
gcloud database-migration migration-jobs promote JOB_NAME --region=REGION

# Storage Transfer Service
gcloud transfer jobs create DESTINATION --source-bucket=SOURCE
gcloud transfer jobs list

# Migrate for Compute Engine
# (Managed via Console)

# Data Transfer to BigQuery
bq mk --transfer_config --data_source=SOURCE

# Compute Engine VM Creation (after migration)
gcloud compute instances create VM_NAME --source-machine-image=IMAGE
```

---

**End of Guide** - Successfully migrate workloads to GCP! 🚀
