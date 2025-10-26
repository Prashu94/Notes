# Google Cloud Professional Architect - Comprehensive Guide

## Table of Contents
1. [Overview](#overview)
2. [Designing Scalable Systems](#designing-scalable-systems)
3. [High Availability & Disaster Recovery](#high-availability--disaster-recovery)
4. [Multi-Region Architecture](#multi-region-architecture)
5. [Security Architecture](#security-architecture)
6. [Performance Optimization](#performance-optimization)
7. [Cost Optimization](#cost-optimization)
8. [Data Architecture](#data-architecture)
9. [Network Architecture](#network-architecture)
10. [Microservices Architecture](#microservices-architecture)
11. [DevOps & CI/CD](#devops--cicd)
12. [Case Studies & Scenarios](#case-studies--scenarios)
13. [Exam Preparation](#exam-preparation)

---

## Overview

### What is Google Cloud Professional Architect?

The Google Cloud Professional Architect certification validates advanced expertise in designing, building, and deploying solutions on Google Cloud Platform. It focuses on enterprise-level architecture, scalability, security, and cost optimization.

**Target Audience:**
- Experienced cloud architects
- Solutions architects
- Senior infrastructure engineers
- Enterprise development leaders

**Exam Focus Areas:**
- 20% - Designing for security and compliance
- 20% - Designing for high availability and disaster recovery
- 18% - Designing for scalability and efficiency
- 16% - Designing for cost optimization
- 13% - Managing and monitoring GCP resources
- 13% - Designing deployments, updates, and migrations

---

## Designing Scalable Systems

### Scalability Principles

**Horizontal Scaling:**
- Add more machines/instances
- Load distribution across servers
- Stateless application design
- Database sharding

**Vertical Scaling:**
- Add more resources to existing machines
- Limited by hardware constraints
- Simple but reaches ceiling quickly

**Best Approach:**
Combine horizontal scaling with load balancing for true scalability.

### Load Balancing Strategy

**Layer 4 (Transport Layer):**
- TCP/UDP level
- Lower latency
- Faster throughput
- Example: Network Load Balancer

**Layer 7 (Application Layer):**
- HTTP/HTTPS level
- Content-based routing
- Better for microservices
- Example: HTTP(S) Load Balancer

```yaml
# HTTP Load Balancer Setup
apiVersion: compute.cnrm.cloud.google.com/v1beta1
kind: ComputeBackendService
metadata:
  name: backend-service
spec:
  healthChecks:
    - name: health-check
  sessionAffinity: "CLIENT_IP"
  affinityCookieTtlSec: 3600
  backends:
    - group: "instance-group-1"
      balancingMode: "RATE"
      maxRatePerEndpoint: 1000
```

### Distributed Caching Architecture

**Multi-Tier Caching:**
```
Client Browser
    ↓ (HTTP Cache)
CDN (Cloud CDN)
    ↓ (Object Cache)
Application Cache (Redis/Memorystore)
    ↓ (Query Cache)
Database Cache
    ↓
Primary Data Store
```

**Implementation:**
```python
from google.cloud import memcache_v1

client = memcache_v1.CloudMemcacheClient()
parent = f"projects/{project_id}/locations/{location}"

instance = memcache_v1.Instance(
    name=f"{parent}/instances/{instance_id}",
    node_count=3,
    node_config={"cpu_count": 2, "memory_size_gb": 32},
    zones=["us-central1-a", "us-central1-b", "us-central1-c"]
)

operation = client.create_instance(parent=parent, instance_id=instance_id, instance=instance)
```

### Database Scaling Patterns

**Read Replicas:**
- Primary database for writes
- Multiple replicas for reads
- Replication lag consideration

**Database Sharding:**
```
User ID 1-1M    → Shard 1
User ID 1M-2M   → Shard 2
User ID 2M-3M   → Shard 3
```

**Example - Cloud Spanner:**
```python
from google.cloud import spanner

client = spanner.Client()
instance = client.instance("my-instance")
database = instance.database("my-database")

with database.batch() as batch:
    batch.insert(
        table="users",
        columns=("user_id", "name", "email"),
        values=[(1, "Alice", "alice@example.com")]
    )
```

---

## High Availability & Disaster Recovery

### HA Architecture Fundamentals

**The Three Pillars:**
1. **Redundancy** - Multiple copies of critical components
2. **Failover** - Automatic switching to backups
3. **Health Checks** - Continuous monitoring

### Designing for 99.99% Uptime (4 Nines)

**Architecture Pattern:**
```
Multi-Zone High Availability
│
├─ Primary Zone (Active)
│  ├─ Instance 1
│  ├─ Instance 2
│  └─ Instance 3
│
├─ Secondary Zone (Standby/Active)
│  ├─ Instance 1
│  ├─ Instance 2
│  └─ Instance 3
│
└─ Load Balancer
   └─ Health Check (10 sec interval)
```

**Configuration:**
```yaml
apiVersion: compute.cnrm.cloud.google.com/v1beta1
kind: ComputeInstanceGroup
metadata:
  name: instance-group-primary
spec:
  zone: us-central1-a
  instances:
    - name: instance-1
    - name: instance-2
    - name: instance-3
---
apiVersion: compute.cnrm.cloud.google.com/v1beta1
kind: ComputeHealthCheck
metadata:
  name: health-check
spec:
  checkIntervalSec: 10
  timeoutSec: 5
  healthyThreshold: 2
  unhealthyThreshold: 2
  httpHealthCheck:
    port: 8080
    requestPath: /health
```

### Disaster Recovery Planning

**RPO vs RTO:**
- **RPO (Recovery Point Objective):** Maximum acceptable data loss
  - Example: 1 hour = lose last hour of data if disaster occurs
  
- **RTO (Recovery Time Objective):** Maximum acceptable downtime
  - Example: 15 minutes = restore within 15 minutes

**DR Strategies:**

**Cold Standby:**
```
RPO: 24 hours
RTO: Hours to days
Cost: Low
Backup stored offline, manual recovery

Best for: Non-critical systems
```

**Warm Standby:**
```
RPO: 1 hour
RTO: 15-30 minutes
Cost: Medium
Replicated data, some instances running

Best for: Important systems
```

**Hot Standby (Active-Active):**
```
RPO: Few minutes
RTO: Few minutes
Cost: High
Real-time replication, both sites active

Best for: Critical systems
```

### Backup & Recovery Implementation

**Cloud Backup and DR Solution:**
```python
from google.cloud import backupdr_v1

client = backupdr_v1.BackupDRClient()

backup = backupdr_v1.Backup(
    name="projects/my-project/locations/us-central1/backups/my-backup",
    description="Daily backup",
    resource_type="compute.instances"
)

parent = "projects/my-project/locations/us-central1"
operation = client.create_backup(parent=parent, backup=backup)
result = operation.result()
```

**Cloud SQL Backups:**
```bash
# Automated backups
gcloud sql backups create \
  --instance=my-instance \
  --description="Daily backup"

# Point-in-time recovery
gcloud sql backups restore BACKUP_ID \
  --backup-instance=my-instance \
  --target-instance=my-instance
```

**Firestore Backup:**
```bash
gcloud firestore backups create \
  --location=us-central1 \
  --retention-days=30
```

---

## Multi-Region Architecture

### Global Application Architecture

**Architecture Pattern:**
```
                          Global Load Balancer
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
    US-Central1              Europe-West1             Asia-Northeast1
    (Primary)                (Secondary)              (Tertiary)
        │                        │                        │
    ┌───┴────┐              ┌────┴────┐             ┌────┴────┐
    │         │              │         │             │         │
  App1      DB1            App2      DB2            App3      DB3
    │         │              │         │             │         │
    └─────────┼──────────────┼─────────┼─────────────┼─────────┘
              │              │         │             │
              └──────────────┴─────────┴─────────────┘
                    Replication (Low Latency)
```

**Implementation:**

1. **Global HTTP(S) Load Balancer:**
```bash
gcloud compute backend-services create global-backend \
  --global \
  --enable-cdn \
  --cache-mode=CACHE_ALL_STATIC

gcloud compute url-maps create global-load-balancer \
  --default-service=global-backend

gcloud compute target-https-proxies create https-proxy \
  --url-map=global-load-balancer \
  --ssl-certificates=my-cert

gcloud compute forwarding-rules create global-https-forwarding \
  --global \
  --target-https-proxy=https-proxy \
  --address=EXTERNAL_IP
```

2. **Cloud Spanner (Multi-Region):**
```python
from google.cloud import spanner_admin_v1

client = spanner_admin_v1.InstanceAdminClient()
config = spanner_admin_v1.InstanceConfig(
    display_name="Multi-region configuration",
    replicas=[
        {"location": "us-central1"},
        {"location": "europe-west1"},
        {"location": "asia-northeast1"}
    ]
)
```

3. **Firestore Global Replication:**
```bash
gcloud firestore databases create \
  --location=eur3 \
  --type=DATASTORE_MODE \
  --enable-delete-protection
```

### Latency Optimization

**Geo-Distributed Content Delivery:**

```
User in London
    ↓
Europe CDN Node (< 10ms)
    ↓
Origin Server (if cache miss)
```

**Cloud CDN Configuration:**
```python
from google.cloud import compute_v1

backend_service = compute_v1.BackendService(
    name="cdn-backend",
    cdn_policy=compute_v1.BackendServiceCdnPolicy(
        cache_mode="CACHE_ALL_STATIC",
        client_ttl=3600,
        default_ttl=3600,
        max_ttl=86400,
        cache_key_policy=compute_v1.CacheKeyPolicy(
            include_host=True,
            include_protocol=True,
            include_query_string=False
        )
    )
)
```

---

## Security Architecture

### Defense in Depth

**Multi-Layer Security Model:**
```
Layer 1: Network Perimeter
├─ Cloud Armor (DDoS Protection)
├─ VPC Firewall Rules
└─ Cloud VPN / Cloud Interconnect

Layer 2: Identity & Access
├─ IAM Policies
├─ Service Accounts
└─ Identity-Aware Proxy (IAP)

Layer 3: Data Protection
├─ Encryption in Transit (TLS)
├─ Encryption at Rest (CMEK)
└─ Key Management Service (KMS)

Layer 4: Application Security
├─ Input Validation
├─ API Authentication
└─ Rate Limiting

Layer 5: Monitoring & Detection
├─ Cloud Audit Logs
├─ Cloud Security Command Center
└─ Security Incident Detection
```

### IAM Architecture

**Service Account Hierarchy:**
```
Project: my-project
│
├─ Service Account: app-sa@my-project.iam.gserviceaccount.com
│  ├─ Role: roles/compute.instanceAdmin
│  ├─ Role: roles/cloudsql.client
│  └─ Role: roles/storage.objectViewer
│
├─ Service Account: batch-sa@my-project.iam.gserviceaccount.com
│  ├─ Role: roles/bigquery.dataEditor
│  └─ Role: roles/storage.admin
│
└─ Service Account: backup-sa@my-project.iam.gserviceaccount.com
   └─ Role: roles/backup.admin
```

**Implementation:**
```bash
# Create service account
gcloud iam service-accounts create app-sa \
  --display-name="Application Service Account"

# Grant roles
gcloud projects add-iam-policy-binding my-project \
  --member="serviceAccount:app-sa@my-project.iam.gserviceaccount.com" \
  --role="roles/compute.instanceAdmin"

# Workload Identity (Kubernetes)
gcloud iam service-accounts add-iam-policy-binding app-sa@my-project.iam.gserviceaccount.com \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:my-project.svc.id.goog[namespace/pod-name]"
```

### Encryption Strategy

**Client-Side Encryption:**
```python
from google.cloud import kms_v1
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

client = kms_v1.KeyManagementServiceClient()
key_path = client.crypto_key_path(
    "my-project", 
    "us-central1", 
    "my-keyring", 
    "my-key"
)

plaintext = b"sensitive data"
encrypt_response = client.encrypt(
    request={"name": key_path, "plaintext": plaintext}
)
ciphertext = encrypt_response.ciphertext
```

**Server-Side Encryption with CMEK (Customer-Managed Keys):**
```bash
# Create key ring
gcloud kms keyrings create my-keyring --location us-central1

# Create key
gcloud kms keys create my-key \
  --location us-central1 \
  --keyring my-keyring \
  --purpose encryption

# Use with Cloud Storage
gsutil -m -e -r cp -C gs://bucket-name gs://bucket-name \
  --kms-key projects/my-project/locations/us-central1/keyRings/my-keyring/cryptoKeys/my-key
```

### VPC Security

**VPC Service Controls:**
```yaml
apiVersion: accesscontextmanager.cnrm.cloud.google.com/v1beta1
kind: AccessContextManagerServicePerimeter
metadata:
  name: my-perimeter
spec:
  parent: accessPolicies/my-policy
  title: "My Service Perimeter"
  description: "Service perimeter for sensitive data"
  perimeterType: PERIMETER_TYPE_REGULAR
  status:
    restrictedServices:
      - storage.googleapis.com
      - bigquery.googleapis.com
    accessLevels:
      - accessLevels/my-level
    resources:
      - projects/my-project
```

### Audit & Compliance

**Enable Cloud Audit Logs:**
```python
from google.cloud import logging_v2

client = logging_v2.Client()
sink = client.sink(
    "security-audit-sink",
    filter_="resource.type=gce_instance AND severity=ERROR"
)

sink.destination = f"bigquery.googleapis.com/projects/{project_id}/datasets/security_logs"
sink.create()
```

---

## Performance Optimization

### Query Performance

**BigQuery Optimization:**

1. **Partitioning:**
```sql
CREATE TABLE project.dataset.events
PARTITION BY DATE(event_timestamp)
CLUSTER BY user_id, event_type AS
SELECT 
  user_id,
  event_type,
  event_timestamp,
  event_data
FROM project.dataset.raw_events;
```

2. **Materialized Views:**
```sql
CREATE MATERIALIZED VIEW project.dataset.daily_summary AS
SELECT
  DATE(event_timestamp) as event_date,
  user_id,
  COUNT(*) as event_count,
  COUNT(DISTINCT event_type) as unique_events
FROM project.dataset.events
GROUP BY event_date, user_id;
```

**Cloud SQL Performance:**

1. **Connection Pooling:**
```python
from google.cloud.sql.connector import Connector

connector = Connector()

def getconn():
    return connector.connect(
        "project:region:instance",
        "pymysql",
        user="user",
        password="password",
        db="database"
    )

engine = create_engine(
    "mysql+pymysql://",
    creator=getconn,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=2,
    pool_pre_ping=True,
)
```

2. **Query Optimization:**
```sql
-- Add indexes
CREATE INDEX idx_user_created ON users(user_id, created_at);

-- Use EXPLAIN to analyze
EXPLAIN SELECT * FROM users 
WHERE user_id = 123 
AND created_at > DATE_SUB(NOW(), INTERVAL 30 DAY);
```

### Application Performance

**Request Optimization:**
```python
# Batch requests to reduce latency
from google.cloud import datastore

client = datastore.Client()

# Instead of individual gets
# results = [client.get(datastore.Key('Kind', id)) for id in ids]

# Use batch get
keys = [datastore.Key('Kind', id) for id in ids]
results = client.get_multi(keys)
```

**Asynchronous Processing:**
```python
import asyncio
from google.cloud import storage

async def upload_files_async(files):
    client = storage.Client()
    bucket = client.bucket('my-bucket')
    
    tasks = []
    for file in files:
        task = asyncio.create_task(
            asyncio.to_thread(
                bucket.blob(file['name']).upload_from_string,
                file['content']
            )
        )
        tasks.append(task)
    
    await asyncio.gather(*tasks)
```

### Network Performance

**Dedicated Interconnect:**
```bash
# Establish private network connection
gcloud compute interconnects attachments create my-attachment \
  --interconnect=my-interconnect \
  --type=PARTNER \
  --router=my-router \
  --vlan=100
```

**Cloud CDN Performance:**
- Cache static assets (images, CSS, JS)
- Reduce origin load by 50-80%
- Serve from edge locations

---

## Cost Optimization

### Cost Analysis Framework

**Cost Categories:**
1. **Compute:** VMs, App Engine, Cloud Run
2. **Storage:** Cloud Storage, Cloud SQL, Firestore
3. **Networking:** Data transfer, Load Balancing
4. **Services:** APIs, Cloud Functions, Pub/Sub

**Monthly Cost Formula:**
```
Total Cost = 
  Compute Costs + 
  Storage Costs + 
  Networking Costs + 
  Service Costs
```

### Compute Cost Optimization

**Reserved Instances (Savings of 25-75%):**
```bash
# Analyze your usage
gcloud compute instances list --format=table

# Create commitment
gcloud compute commitments create my-commitment \
  --plan=one-year \
  --resources=VCPU:16,memory:64 \
  --region=us-central1
```

**Committed Use Discounts:**
```
1-year commitment:  25% discount
3-year commitment:  52% discount
```

**Right-Sizing VMs:**
```python
from google.cloud import recommenders_v1

client = recommenders_v1.RecommendersClient()
parent = f"projects/{project_id}/locations/us-central1"

# Get VM sizing recommendations
operation = client.list_recommendations(
    parent=f"{parent}/recommenders/compute.googleapis.com~instances~sizing"
)

for recommendation in operation.recommendations:
    print(f"VM: {recommendation.name}")
    print(f"Estimated savings: {recommendation.description}")
```

### Storage Cost Optimization

**Storage Classes:**
```
Standard:     $0.020/GB/month (Frequently accessed)
Nearline:     $0.010/GB/month (< 1x/month)
Coldline:     $0.004/GB/month (< 1x/quarter)
Archive:      $0.0025/GB/month (< 1x/year)
```

**Implementation:**
```python
from google.cloud import storage
from google.cloud.storage import transfer_manager

client = storage.Client()
bucket = client.bucket('my-bucket')

# Set lifecycle policy
rule = storage.bucket.LifecycleRuleDelete(
    age_days=90,
    storage_class='STANDARD'
)

bucket.lifecycle_rules = [
    storage.bucket.LifecycleRuleSetStorageClass(
        age_days=30,
        storage_class='NEARLINE'
    ),
    storage.bucket.LifecycleRuleSetStorageClass(
        age_days=90,
        storage_class='COLDLINE'
    ),
    rule
]
bucket.patch()
```

### Networking Cost Optimization

**Egress Cost Reduction:**
```
Zone to Zone (same region):    Free
Zone to Zone (different region): $0.01/GB
Zone to Internet:               $0.12/GB
Cloud CDN:                      $0.085/GB (cheaper than egress)
```

**Cloud CDN Implementation:**
```bash
gcloud compute backend-services create cdn-backend \
  --protocol=HTTP \
  --global \
  --enable-cdn

gcloud compute backend-services update cdn-backend \
  --cache-mode=CACHE_ALL_STATIC \
  --global
```

### Cost Monitoring

**Budget Alerts:**
```bash
gcloud billing budgets create my-budget \
  --billing-account=BILLING_ACCOUNT_ID \
  --display-name="Project Budget" \
  --budget-amount=5000 \
  --threshold-rule=percent=80 \
  --threshold-rule=percent=100

# Get notifications
gcloud billing budgets describe my-budget
```

---

## Data Architecture

### Data Warehouse Architecture

**Modern Data Stack:**
```
Data Sources
├─ SaaS Applications
├─ Databases
├─ APIs
├─ Logs & Events
│
└→ Dataflow (ETL)
    │
    └→ BigQuery (Data Warehouse)
        │
        ├→ Analytics & BI
        ├→ Machine Learning
        └→ Real-time Dashboards
```

**BigQuery Configuration:**
```python
from google.cloud import bigquery

client = bigquery.Client(project="my-project")

# Create dataset
dataset_id = "my_dataset"
dataset = bigquery.Dataset(f"my-project.{dataset_id}")
dataset.location = "us-central1"
dataset = client.create_dataset(dataset, exists_ok=True)

# Create table with schema
schema = [
    bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("event_type", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("event_timestamp", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("event_data", "JSON", mode="NULLABLE"),
]

table_id = f"my-project.{dataset_id}.events"
table = bigquery.Table(table_id, schema=schema)
table.time_partitioning = bigquery.TimePartitioning(
    type_=bigquery.TimePartitioningType.DAY,
    field="event_timestamp"
)
table = client.create_table(table)
```

### Real-Time Data Pipeline

**Pub/Sub → Dataflow → BigQuery:**
```python
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions

class ParseEvent(beam.DoFn):
    def process(self, element):
        import json
        try:
            event = json.loads(element)
            yield event
        except json.JSONDecodeError:
            pass

options = PipelineOptions(
    project="my-project",
    runner="DataflowRunner",
    region="us-central1",
    temp_location="gs://my-bucket/temp"
)

with beam.Pipeline(options=options) as p:
    (p
     | "ReadFromPubSub" >> beam.io.ReadFromPubSub(
         topic="projects/my-project/topics/events"
     )
     | "ParseJSON" >> beam.ParDo(ParseEvent())
     | "WriteToBigQuery" >> beam.io.WriteToBigQuery(
         table="my-project:my_dataset.events",
         schema="user_id:STRING,event_type:STRING,event_timestamp:TIMESTAMP"
     ))
```

### Data Governance

**Data Catalog Setup:**
```bash
# Create entry group
gcloud datacatalog entry-groups create my-entry-group \
  --location=us-central1 \
  --display-name="Data Entry Group"

# Create entry
gcloud datacatalog entries create my-entry \
  --entry-group=my-entry-group \
  --location=us-central1 \
  --display-name="Customer Data" \
  --type=DATASET
```

---

## Network Architecture

### VPC Design

**Multi-Tier VPC Architecture:**
```
┌─────────────────────────────────┐
│         VPC Network             │
│                                 │
│  ┌────────────────────────────┐ │
│  │  Public Subnet             │ │
│  │  (10.0.1.0/24)             │ │
│  │  - Load Balancers          │ │
│  │  - NAT Gateway             │ │
│  └────────────────────────────┘ │
│                                 │
│  ┌────────────────────────────┐ │
│  │  Private Subnet (App)      │ │
│  │  (10.0.2.0/24)             │ │
│  │  - App Servers             │ │
│  │  - Cloud Functions         │ │
│  └────────────────────────────┘ │
│                                 │
│  ┌────────────────────────────┐ │
│  │  Private Subnet (DB)       │ │
│  │  (10.0.3.0/24)             │ │
│  │  - Cloud SQL               │ │
│  │  - Firestore               │ │
│  └────────────────────────────┘ │
└─────────────────────────────────┘
```

**VPC Configuration:**
```bash
# Create custom VPC
gcloud compute networks create my-vpc \
  --subnet-mode=custom \
  --bgp-routing-mode=regional

# Create subnets
gcloud compute networks subnets create public-subnet \
  --network=my-vpc \
  --region=us-central1 \
  --range=10.0.1.0/24

gcloud compute networks subnets create private-app-subnet \
  --network=my-vpc \
  --region=us-central1 \
  --range=10.0.2.0/24 \
  --private-ip-google-access

gcloud compute networks subnets create private-db-subnet \
  --network=my-vpc \
  --region=us-central1 \
  --range=10.0.3.0/24 \
  --private-ip-google-access
```

### Firewall Rules Strategy

**Security Group-Based Approach:**
```bash
# Allow ingress from load balancer
gcloud compute firewall-rules create allow-from-lb \
  --network=my-vpc \
  --allow=tcp:8080 \
  --source-tags=load-balancer \
  --target-tags=app-server

# Allow app to db communication
gcloud compute firewall-rules create allow-app-to-db \
  --network=my-vpc \
  --allow=tcp:3306 \
  --source-tags=app-server \
  --target-tags=database

# Deny by default (implicit)
gcloud compute firewall-rules create deny-all-ingress \
  --network=my-vpc \
  --allow= \
  --priority=65534
```

### Hybrid Connectivity

**Cloud Interconnect Architecture:**
```
┌──────────────────────────┐
│   On-Premises Network    │
│   (192.168.0.0/16)       │
│   - Data Center          │
│   - Edge Router          │
└────────────┬─────────────┘
             │
             │ Dedicated Interconnect
             │ 10Gbps Private Connection
             │
┌────────────┴─────────────┐
│   GCP VPC               │
│   (10.0.0.0/16)         │
│   - Cloud Interconnect  │
│   - Cloud Router        │
└──────────────────────────┘
```

**Implementation:**
```bash
# Create router
gcloud compute routers create my-router \
  --network=my-vpc \
  --region=us-central1

# Create BGP session for on-premises
gcloud compute routers add-bgp-peer my-router \
  --peer-name=on-premises \
  --interface=0 \
  --peer-ip-address=192.168.1.1 \
  --peer-asn=65000 \
  --region=us-central1
```

---

## Microservices Architecture

### Service Mesh Design

**Istio Service Mesh:**
```
┌─────────────────────────────────┐
│      Kubernetes Cluster         │
│                                 │
│  ┌─────────────────────────┐   │
│  │  Istio Control Plane    │   │
│  │  - Pilot (Config)       │   │
│  │  - Citadel (Security)   │   │
│  │  - Galley (Validation)  │   │
│  └─────────────────────────┘   │
│                                 │
│  ┌────────────┐ ┌────────────┐ │
│  │  Service 1 │ │  Service 2 │ │
│  │ ┌────────┐ │ │ ┌────────┐ │ │
│  │ │Envoy   │ │ │ │Envoy   │ │ │
│  │ │Proxy   │ │ │ │Proxy   │ │ │
│  │ └────────┘ │ │ └────────┘ │ │
│  └────────────┘ └────────────┘ │
│                                 │
│  ┌────────────┐ ┌────────────┐ │
│  │  Service 3 │ │  Service 4 │ │
│  │ ┌────────┐ │ │ ┌────────┐ │ │
│  │ │Envoy   │ │ │ │Envoy   │ │ │
│  │ │Proxy   │ │ │ │Proxy   │ │ │
│  │ └────────┘ │ │ └────────┘ │ │
│  └────────────┘ └────────────┘ │
│                                 │
└─────────────────────────────────┘
```

**Istio Configuration:**
```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: user-service
spec:
  hosts:
  - user-service
  http:
  - match:
    - uri:
        prefix: "/api"
    route:
    - destination:
        host: user-service
        port:
          number: 8080
      weight: 80
    - destination:
        host: user-service-v2
        port:
          number: 8080
      weight: 20
---
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: user-service
spec:
  host: user-service
  trafficPolicy:
    connectionPool:
      http:
        http1MaxPendingRequests: 100
        http2MaxRequests: 1000
```

### Service Discovery

**GKE Service Discovery:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: api-service
  labels:
    app: api
spec:
  type: ClusterIP
  selector:
    app: api
  ports:
  - port: 8080
    targetPort: 8080
    name: http
  sessionAffinity: ClientIP
```

### API Gateway Pattern

**Apigee Configuration:**
```xml
<APIProxy name="user-api">
  <Description>User Management API</Description>
  
  <ProxyEndpoint name="default">
    <HTTPProxyConnection>
      <BasePath>/users</BasePath>
    </HTTPProxyConnection>
    
    <Policies>
      <Policy name="VerifyAPIKey-1"/>
      <Policy name="RateLimiting-1"/>
      <Policy name="Authentication-1"/>
    </Policies>
  </ProxyEndpoint>
  
  <TargetEndpoint name="backend">
    <HTTPTargetConnection>
      <URL>https://backend.example.com</URL>
    </HTTPTargetConnection>
  </TargetEndpoint>
</APIProxy>
```

---

## DevOps & CI/CD

### CI/CD Pipeline Architecture

**Multi-Stage Pipeline:**
```
Code Push
  ↓
Source Code Management (Cloud Source Repositories)
  ↓
Cloud Build (Trigger)
  ├─ Build Stage (Compile, Unit Tests)
  ├─ Test Stage (Integration Tests)
  ├─ Security Scan (Container Scan)
  ├─ Build Docker Image
  ├─ Push to Artifact Registry
  │
  ├─ Deploy to Staging
  ├─ Smoke Tests
  │
  └─ Deploy to Production (Canary/Blue-Green)
```

**Cloud Build Configuration:**
```yaml
steps:
  # Step 1: Build
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/my-app:$SHORT_SHA', '.']
  
  # Step 2: Run tests
  - name: 'gcr.io/$PROJECT_ID/my-app:$SHORT_SHA'
    args: ['npm', 'test']
    env:
      - 'NODE_ENV=test'
  
  # Step 3: Push to registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/my-app:$SHORT_SHA']
  
  # Step 4: Deploy to staging
  - name: 'gcr.io/cloud-builders/gke-deploy'
    args:
      - run
      - --filename=k8s/
      - --image=gcr.io/$PROJECT_ID/my-app:$SHORT_SHA
      - --location=us-central1-a
      - --cluster=staging-cluster
      - --namespace=staging
  
  # Step 5: Deploy to production (canary)
  - name: 'gcr.io/cloud-builders/gke-deploy'
    args:
      - run
      - --filename=k8s/
      - --image=gcr.io/$PROJECT_ID/my-app:$SHORT_SHA
      - --location=us-central1-a
      - --cluster=prod-cluster
      - --namespace=production

images:
  - 'gcr.io/$PROJECT_ID/my-app:$SHORT_SHA'

timeout: '3600s'
```

### Infrastructure as Code (IaC)

**Terraform Configuration:**
```hcl
# main.tf
terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
  backend "gcs" {
    bucket = "my-terraform-state"
    prefix = "prod"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# VPC Network
resource "google_compute_network" "main" {
  name                    = "main-vpc"
  auto_create_subnetworks = false
}

# Subnet
resource "google_compute_subnetwork" "app" {
  name          = "app-subnet"
  ip_cidr_range = "10.0.2.0/24"
  region        = var.region
  network       = google_compute_network.main.id

  private_ip_google_access = true
}

# Kubernetes Engine Cluster
resource "google_container_cluster" "primary" {
  name     = "primary-gke-cluster"
  location = var.region

  initial_node_count = 1

  network    = google_compute_network.main.name
  subnetwork = google_compute_subnetwork.app.name

  node_config {
    machine_type = "n1-standard-1"
    
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  }
}

# Cloud SQL
resource "google_sql_database_instance" "main" {
  name             = "main-postgres-instance"
  database_version = "POSTGRES_13"
  region           = var.region

  settings {
    tier = "db-f1-micro"

    backup_configuration {
      enabled                        = true
      point_in_time_recovery_enabled = true
      backup_retention_settings {
        retained_backups = 30
        retention_unit   = "COUNT"
      }
    }
  }

  deletion_protection = true
}
```

### GitOps Implementation

**ArgoCD Configuration:**
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app
  namespace: argocd
spec:
  project: default
  
  source:
    repoURL: https://github.com/my-org/my-app-deploy
    targetRevision: main
    path: k8s/overlays/prod
  
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
    - CreateNamespace=true
  
  ignoreDifferences:
  - group: apps
    kind: Deployment
    jsonPointers:
    - /spec/replicas
```

---

## Case Studies & Scenarios

### Scenario 1: E-Commerce Platform

**Requirements:**
- Handle 10,000+ concurrent users
- Real-time inventory management
- Multi-region deployment
- 99.99% uptime SLA

**Architecture:**
```
Frontend (Cloud CDN)
    ↓
Global HTTP(S) Load Balancer
    ├─ US Region
    │  ├─ GKE Cluster
    │  ├─ Cloud SQL (Primary)
    │  └─ Memorystore
    │
    ├─ Europe Region
    │  ├─ GKE Cluster
    │  ├─ Cloud SQL (Read Replica)
    │  └─ Memorystore
    │
    └─ Asia Region
       ├─ GKE Cluster
       ├─ Cloud SQL (Read Replica)
       └─ Memorystore

Shared Services:
├─ Cloud Pub/Sub (Event Streaming)
├─ BigQuery (Analytics)
├─ Cloud Storage (Product Images/CDN)
└─ Cloud Tasks (Order Processing)
```

**Implementation Points:**
1. Use Spanner for global transactions
2. Cloud CDN for product images
3. Multi-region read replicas with eventual consistency
4. Event-driven architecture for inventory updates
5. Circuit breaker patterns for resilience

### Scenario 2: Real-Time Analytics Platform

**Requirements:**
- Ingest 1M+ events/second
- Sub-second latency for queries
- Cost-effective storage
- Global data access

**Architecture:**
```
Data Sources
├─ Mobile Apps (SDKs)
├─ Web Browsers
├─ Server Logs
└─ Third-party APIs
    │
    ├─ Pub/Sub (High Throughput)
    │  └─ Dataflow (Stream Processing)
    │     └─ BigQuery (Real-time)
    │
    ├─ Storage (Batch Upload)
    │  └─ Dataflow (Batch Processing)
    │     └─ BigQuery (Historical)
    │
    └─ API (Direct Ingestion)
       └─ BigQuery (Insert)

Consumption Layer:
├─ Looker (BI & Analytics)
├─ Data Studio (Dashboards)
├─ Custom Applications
└─ Machine Learning (Vertex AI)
```

**Cost Optimization:**
1. Partition tables by date
2. Cluster by high-cardinality columns
3. Archive cold data to Cloud Storage
4. Use BigQuery Flex Slots for predictable costs
5. Schedule queries during off-peak hours

---

## Exam Preparation

### Key Topics to Master

**1. Scalability & Performance:**
- Horizontal vs vertical scaling
- Load balancing strategies
- Caching architecture
- Database optimization

**2. High Availability & Disaster Recovery:**
- RTO/RPO concepts
- Multi-zone redundancy
- Backup and recovery
- Failover mechanisms

**3. Security:**
- IAM best practices
- Encryption strategies
- Network security
- Audit and compliance

**4. Cost Optimization:**
- Reserved instances
- Committed use discounts
- Resource right-sizing
- Data archival strategies

**5. Data Architecture:**
- Data warehouse design
- ETL/ELT patterns
- Real-time vs batch
- Data governance

### Practice Questions

**Q1:** Design a highly available web application with 99.99% uptime SLA across three regions.

**Model Answer:**
- Use Global HTTP(S) Load Balancer
- Deploy to multiple regions (us-central1, europe-west1, asia-northeast1)
- Each region: GKE cluster with multi-zone setup
- Cloud SQL with automated backups and cross-region replicas
- Cloud CDN for static content
- Implement health checks and automatic failover
- Use managed database replication

**Q2:** A company wants to reduce database costs by 60%. Current infrastructure uses Cloud SQL with 70% idle capacity. How would you optimize?

**Model Answer:**
- Analyze workload patterns → identify peak/off-peak hours
- Right-size instances → use smaller instances with vertical scalability
- Implement read replicas → distribute read traffic
- Enable automatic backup only during off-peak
- Consider switching to BigQuery for analytics queries
- Implement caching layer (Memorystore) to reduce DB load
- Use connection pooling to optimize connections

**Q3:** Design a disaster recovery strategy for a mission-critical application with RPO of 1 hour and RTO of 15 minutes.

**Model Answer:**
- Primary: Active-Active in us-central1
- Standby: Warm standby in europe-west1
- Replication: Continuous binary log replication
- Backup: Automated hourly snapshots
- Failover: Automated DNS switching via Cloud DNS
- Recovery: Automated instance launch in standby region
- Monitoring: Real-time health checks and alerts

### Exam Day Tips

1. **Read Questions Carefully:**
   - Identify constraints (RTO, RPO, budget)
   - Understand business requirements
   - Look for regulatory/compliance needs

2. **Think Multi-Region for HA:**
   - At least 2 regions for high availability
   - Consider latency impact

3. **Cost Optimization Perspective:**
   - Always consider reserved instances
   - Analyze data tiering strategies
   - Evaluate serverless vs provisioned

4. **Security First:**
   - Defense in depth approach
   - Least privilege principle
   - Encryption for sensitive data

5. **Use GCP's Managed Services:**
   - Leverage fully managed solutions
   - Reduces operational burden
   - Better for scalability

---

## Additional Resources

### Official Documentation
- [Google Cloud Architecture Center](https://cloud.google.com/architecture)
- [GCP Best Practices](https://cloud.google.com/docs/cloud-best-practices)
- [Solution Architecture Guide](https://cloud.google.com/solutions)

### Certification Resources
- [Professional Cloud Architect Exam Guide](https://cloud.google.com/certification/guides/professional-cloud-architect)
- [Sample Questions](https://docs.google.com/forms/d/e/1FAIpQLSfexnK-5rREoSv2GaSl3_PZC_H-jzg4fdbqPnGH-1TrOTXZLg/viewform)

### Hands-On Labs
- [Google Cloud Skills Boost](https://www.cloudskillsboost.google/)
- [Qwik Labs](https://www.qwiklabs.com/)

---

## Conclusion

Becoming a Google Cloud Professional Architect requires deep understanding of:
- Scalable system design principles
- High availability and disaster recovery patterns
- Security architecture and best practices
- Cost optimization strategies
- Data architecture and analytics
- Network design and hybrid connectivity
- DevOps and CI/CD practices

Success comes from:
1. Hands-on experience with GCP services
2. Understanding trade-offs between solutions
3. Designing for business requirements
4. Focusing on reliability, security, and cost
5. Continuous learning and practice

Remember: A great architect designs solutions that are not just technically sound but also align with business goals and cost constraints.
