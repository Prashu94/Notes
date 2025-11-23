# GCP Professional Cloud Architect - Practice Questions

## Architecture Design & Case Studies - PCA Practice

### Overview
Professional Cloud Architect (PCA) exam focuses on:
- **Designing solutions** that meet business requirements
- **Multi-service architectures** and trade-offs
- **Cost optimization** and technical constraints
- **Migration strategies** and hybrid architectures
- **Security and compliance** at scale
- **HA, DR, and business continuity**

**Question Style**: Scenario-based, requiring architectural decisions

---

## Question 1
A global e-commerce company needs to migrate their on-premises application to GCP. The application has:
- Web tier (stateless)
- Application tier (requires session affinity)
- Database tier (PostgreSQL, 2TB, requires <10ms latency)
- Expected: 50,000 concurrent users, 99.95% availability SLA

Which architecture should you recommend?

**A)** 
- Web: Cloud Run globally
- App: GKE with session affinity
- DB: Cloud SQL PostgreSQL (single region, HA)

**B)**
- Web: Compute Engine MIG globally with HTTP(S) LB
- App: Compute Engine MIG with session affinity cookies
- DB: Cloud Spanner multi-region

**C)**
- Web: App Engine Standard
- App: App Engine Flexible with session affinity
- DB: Cloud SQL PostgreSQL multi-region

**D)**
- Web: GKE with Ingress (global)
- App: GKE with StatefulSet for session affinity
- DB: Cloud Spanner or Cloud SQL HA

**Correct Answer**: D

**Explanation**:
- **Option D is best** because:
  - GKE provides flexibility and session affinity via service configuration
  - StatefulSet not required for session affinity (use session affinity in Service)
  - Cloud Spanner for global distribution OR Cloud SQL HA for regional (depending on global vs regional requirement)
  - Ingress with global load balancing for web tier
  - Meets 99.95% SLA with proper HA configuration

Architecture:
```yaml
# Web Tier - Global HTTP(S) Load Balancer + GKE
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web-ingress
  annotations:
    kubernetes.io/ingress.class: "gce"
    kubernetes.io/ingress.global-static-ip-name: "web-global-ip"
spec:
  rules:
  - http:
      paths:
      - path: /*
        pathType: ImplementationSpecific
        backend:
          service:
            name: web-service
            port:
              number: 80

---
# Application Tier - Session Affinity
apiVersion: v1
kind: Service
metadata:
  name: app-service
spec:
  sessionAffinity: ClientIP  # Session affinity
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 10800  # 3 hours
  selector:
    app: application
  ports:
  - port: 8080
    targetPort: 8080
```

Database options:
```bash
# Option 1: Cloud SQL HA (regional, <10ms latency guaranteed)
gcloud sql instances create ecommerce-db \
  --database-version=POSTGRES_14 \
  --tier=db-custom-16-65536 \
  --region=us-central1 \
  --availability-type=REGIONAL \
  --backup

# Option 2: Cloud Spanner (global, if multi-region needed)
gcloud spanner instances create ecommerce-spanner \
  --config=nam-eur-asia1 \
  --nodes=3 \
  --description="Global e-commerce database"
```

- **Option A is partially correct** but:
  - Cloud Run for web is good but session affinity in GKE is more robust
  - Single region DB limits global performance
  
- **Option B is incorrect** because:
  - Cloud Spanner might be over-engineered for 2TB PostgreSQL workload
  - Higher cost than Cloud SQL HA
  - Migration from PostgreSQL to Spanner requires schema changes

- **Option C is incorrect** because:
  - App Engine Flexible is deprecated in favor of Cloud Run
  - Cloud SQL multi-region not available (only regional HA)
  - Session affinity in App Engine less granular

**Key Architectural Decisions**:
1. **Global distribution**: GKE + Ingress for multi-region deployment
2. **Session affinity**: ClientIP-based session affinity in Kubernetes Service
3. **Database**: Cloud SQL HA for regional or Spanner for global
4. **HA**: Regional MIGs across zones, Cloud SQL HA configuration
5. **Cost**: Cloud SQL cheaper than Spanner for this use case

---

## Question 2
A financial services company requires:
- Data residency in EU only
- Encryption with customer-managed keys
- Audit all data access
- 99.99% availability for transaction processing
- Real-time fraud detection (ML)

Which architecture meets ALL requirements?

**A)**
- Compute: GKE in europe-west regions
- Storage: Multi-region EU Cloud Storage with CMEK
- Database: Cloud Spanner EUR3 configuration
- ML: Vertex AI in EU region
- Auditing: Cloud Audit Logs - Data Access enabled

**B)**
- Compute: Cloud Run in europe-west1
- Storage: Regional Cloud Storage
- Database: Cloud SQL PostgreSQL HA
- ML: On-premises ML
- Auditing: Enabled

**C)**
- Compute: Global GKE
- Storage: Multi-region (global)
- Database: Cloud Spanner global
- ML: Vertex AI global
- Auditing: Admin Activity only

**D)**
- Compute: Compute Engine in EU
- Storage: EU Cloud Storage
- Database: Firestore
- ML: BigQuery ML in EU
- Auditing: Cloud Logging only

**Correct Answer**: A

**Explanation**:
- **Option A is correct** because it meets ALL requirements:

**1. Data Residency (EU only)**:
```bash
# GKE in EU regions only
gcloud container clusters create financial-cluster \
  --region=europe-west1 \
  --num-nodes=3 \
  --resource-usage-export-bucket-name=eu-usage-bucket \
  --addons=ResourceUsageExportConfig

# Cloud Storage - EU multi-region
gsutil mb -c STANDARD -l EU gs://financial-data-eu

# Cloud Spanner - EUR3 configuration (EU only)
gcloud spanner instances create financial-spanner \
  --config=eur3 \
  --nodes=5 \
  --description="EU-only financial data"

# Vertex AI in EU region
gcloud ai models deploy MODEL_ID \
  --region=europe-west4 \
  --endpoint-display-name=fraud-detection-eu
```

**2. Customer-Managed Encryption Keys (CMEK)**:
```bash
# Create KMS key ring in EU
gcloud kms keyrings create financial-keyring \
  --location=europe-west1

# Create encryption key
gcloud kms keys create financial-key \
  --location=europe-west1 \
  --keyring=financial-keyring \
  --purpose=encryption

# Apply CMEK to Cloud Storage
gsutil kms encryption \
  -k projects/PROJECT/locations/europe-west1/keyRings/financial-keyring/cryptoKeys/financial-key \
  gs://financial-data-eu

# Cloud Spanner with CMEK
gcloud spanner instances update financial-spanner \
  --kms-key=projects/PROJECT/locations/europe-west1/keyRings/financial-keyring/cryptoKeys/financial-key

# GKE with CMEK for secrets and disks
gcloud container clusters create financial-cluster \
  --region=europe-west1 \
  --database-encryption-key=projects/PROJECT/locations/europe-west1/keyRings/financial-keyring/cryptoKeys/financial-key \
  --disk-encryption-key=projects/PROJECT/locations/europe-west1/keyRings/financial-keyring/cryptoKeys/financial-key
```

**3. Audit All Data Access**:
```bash
# Enable Data Access audit logs (billable)
cat > audit-policy.yaml <<EOF
auditConfigs:
- service: allServices
  auditLogConfigs:
  - logType: ADMIN_READ
  - logType: DATA_READ
  - logType: DATA_WRITE
EOF

gcloud organizations set-iam-policy ORGANIZATION_ID audit-policy.yaml

# Export audit logs to BigQuery in EU
gcloud logging sinks create financial-audit-sink \
  bigquery.googleapis.com/projects/PROJECT/datasets/audit_logs_eu \
  --log-filter='protoPayload.serviceName="spanner.googleapis.com" OR protoPayload.serviceName="storage.googleapis.com"'
```

**4. 99.99% Availability**:
```yaml
# Cloud Spanner EUR3 provides 99.99% availability SLA
# GKE regional cluster with 3 zones
# Auto-scaling and PodDisruptionBudgets

apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: transaction-pdb
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: transaction-processor
```

**5. Real-time Fraud Detection**:
```python
# Vertex AI for real-time predictions
from google.cloud import aiplatform

aiplatform.init(
    project='financial-project',
    location='europe-west4'  # EU region
)

endpoint = aiplatform.Endpoint('fraud-detection-endpoint')

# Real-time prediction
prediction = endpoint.predict(instances=[transaction_data])
```

- **Option B is incorrect** because:
  - Regional storage doesn't meet 99.99% availability
  - Cloud SQL HA provides 99.95%, not 99.99%
  - On-premises ML breaks cloud-native architecture

- **Option C is incorrect** because:
  - Global GKE/Storage/Spanner violates EU data residency
  - Admin Activity logs don't audit data access
  - Fails compliance requirements

- **Option D is incorrect** because:
  - Firestore doesn't meet 99.99% for transactional workloads
  - BigQuery ML not suitable for real-time predictions
  - Cloud Logging only doesn't provide Data Access auditing

**Cost Optimization**:
```bash
# Use committed use discounts for Spanner
gcloud spanner instances create financial-spanner \
  --config=eur3 \
  --processing-units=1000 \
  --commit-term=1-YEAR  # Significant discount

# Use preemptible nodes for batch ML training
gcloud container node-pools create ml-training-pool \
  --cluster=financial-cluster \
  --preemptible \
  --num-nodes=0 \
  --enable-autoscaling \
  --min-nodes=0 \
  --max-nodes=20
```

**Architecture Diagram**:
```
[Users in EU] 
     ↓
[Global HTTP(S) LB - anycast IP]
     ↓
[GKE Cluster - europe-west1 (3 zones)]
     ├─ Transaction Service (CMEK encrypted)
     ├─ Fraud Detection Service → Vertex AI (EU)
     └─ API Gateway
           ↓
     [Cloud Spanner EUR3] (CMEK, 99.99% SLA)
           ↓
     [Cloud Storage EU] (CMEK, archive/backup)
           ↓
     [Audit Logs] → BigQuery EU

[Cloud KMS - europe-west1] → All encrypted resources
```

---

## Question 3
A healthcare company is migrating a HIPAA-compliant application. Current setup:
- 500TB medical imaging data
- 10,000 concurrent users
- <100ms latency for image retrieval
- Must maintain audit trail for 7 years
- Disaster recovery: RPO=1hr, RTO=4hr

Design the migration strategy and GCP architecture.

**A)** Lift-and-shift to Compute Engine, Cloud Storage Standard, manual DR

**B)** Re-architect to Cloud Run + Cloud Storage with signed URLs + regional DR

**C)**
- Migration: Storage Transfer Service + Database Migration Service
- Architecture: GKE + Cloud Storage + Cloud SQL + Cloud CDN
- DR: Cross-region replication + automated failover

**D)**
- Migration: Transfer Appliance for imaging data
- Architecture: Compute Engine MIG + Cloud Storage Nearline + Filestore
- DR: Scheduled snapshots only

**Correct Answer**: C

**Explanation**:
**Option C provides comprehensive solution**:

**Migration Strategy**:
```bash
# 1. Data Migration - Storage Transfer Service for 500TB
gcloud transfer jobs create gs://on-prem-sync gs://gcp-medical-images \
  --source-creds-file=credentials.json \
  --schedule-starts=2024-01-01T00:00:00Z \
  --schedule-repeats-every=24h

# 2. Database Migration - Database Migration Service
gcloud database-migration migration-jobs create medical-db-migration \
  --source=SOURCE_PROFILE \
  --destination=CLOUD_SQL_PROFILE \
  --type=CONTINUOUS \
  --region=us-central1

# 3. Application Migration - Containerize and deploy to GKE
docker build -t gcr.io/PROJECT/medical-app:v1 .
docker push gcr.io/PROJECT/medical-app:v1

gcloud container clusters create medical-cluster \
  --region=us-central1 \
  --num-nodes=3 \
  --enable-autoscaling \
  --min-nodes=3 \
  --max-nodes=20 \
  --enable-ip-alias \
  --enable-network-policy

kubectl apply -f deployment.yaml
```

**Production Architecture**:
```yaml
# GKE Deployment with autoscaling
apiVersion: apps/v1
kind: Deployment
metadata:
name: medical-imaging-app
spec:
  replicas: 10
  selector:
    matchLabels:
      app: medical-app
  template:
    metadata:
      labels:
        app: medical-app
    spec:
      containers:
      - name: app
        image: gcr.io/PROJECT/medical-app:v1
        resources:
          requests:
            memory: "4Gi"
            cpu: "2"
          limits:
            memory: "8Gi"
            cpu: "4"
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: medical-app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: medical-imaging-app
  minReplicas: 10
  maxReplicas: 100
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

**Storage Architecture** (< 100ms latency):
```bash
# Cloud Storage Standard for frequently accessed images
gsutil mb -c STANDARD -l us-central1 gs://medical-images-hot

# Cloud CDN for global low-latency access
gcloud compute backend-buckets create medical-images-backend \
  --gcs-bucket-name=medical-images-hot \
  --enable-cdn

# Lifecycle policy for older images
cat > lifecycle.json <<EOF
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "SetStorageClass", "storageClass": "NEARLINE"},
        "condition": {"age": 90, "matchesPrefix": ["archive/"]}
      },
      {
        "action": {"type": "SetStorageClass", "storageClass": "COLDLINE"},
        "condition": {"age": 365}
      }
    ]
  }
}
EOF

gsutil lifecycle set lifecycle.json gs://medical-images-hot
```

**HIPAA Compliance**:
```bash
# 1. Enable Cloud Audit Logs - Data Access
gcloud projects get-iam-policy PROJECT_ID > policy.yaml
# Edit to enable DATA_READ, DATA_WRITE logs
gcloud projects set-iam-policy PROJECT_ID policy.yaml

# 2. Create audit log sink (7-year retention)
bq mk --dataset --location=US audit_logs

gcloud logging sinks create hipaa-audit-sink \
  bigquery.googleapis.com/projects/PROJECT/datasets/audit_logs \
  --log-filter='protoPayload.serviceName="healthcare.googleapis.com" OR protoPayload.serviceName="storage.googleapis.com"'

# Set BigQuery table expiration to 7 years
bq update --expiration=220752000 audit_logs.cloudaudit_googleapis_com_data_access

# 3. CMEK encryption
gcloud kms keyrings create hipaa-keyring --location=us-central1
gcloud kms keys create hipaa-key \
  --location=us-central1 \
  --keyring=hipaa-keyring \
  --purpose=encryption

gsutil kms encryption -k projects/PROJECT/locations/us-central1/keyRings/hipaa-keyring/cryptoKeys/hipaa-key gs://medical-images-hot

# 4. VPC Service Controls perimeter
gcloud access-context-manager perimeters create medical_perimeter \
  --title="Medical Application Perimeter" \
  --resources=projects/PROJECT_NUMBER \
  --restricted-services=storage.googleapis.com,healthcare.googleapis.com \
  --policy=POLICY_ID
```

**Disaster Recovery** (RPO=1hr, RTO=4hr):
```bash
# 1. Cross-region replication for Cloud Storage
gsutil rsync -r -d gs://medical-images-hot gs://medical-images-dr-us-east1

# 2. Cloud SQL HA + Cross-region read replica
gcloud sql instances create medical-db-primary \
  --region=us-central1 \
  --availability-type=REGIONAL \
  --backup \
  --backup-start-time=02:00

# Read replica in DR region
gcloud sql instances create medical-db-dr-replica \
  --master-instance-name=medical-db-primary \
  --region=us-east1

# 3. GKE cluster in DR region (standby)
gcloud container clusters create medical-cluster-dr \
  --region=us-east1 \
  --num-nodes=3

# 4. Automated DR failover script
cat > dr-failover.sh <<'EOF'
#!/bin/bash
# Promote DR database
gcloud sql instances promote-replica medical-db-dr-replica

# Update DNS to point to DR region
gcloud dns record-sets transaction start --zone=medical-zone
gcloud dns record-sets transaction add DR_IP \
  --name=app.medical.com \
  --ttl=300 \
  --type=A \
  --zone=medical-zone
gcloud dns record-sets transaction execute --zone=medical-zone

# Scale up DR GKE cluster
gcloud container clusters resize medical-cluster-dr --num-nodes=10 --region=us-east1
EOF

# Scheduled DR tests
gcloud scheduler jobs create http dr-test-job \
  --schedule="0 0 1 * *" \
  --uri="https://us-central1-PROJECT.cloudfunctions.net/dr-test" \
  --http-method=POST
```

- **Option A incorrect**: Lift-and-shift doesn't optimize for cloud, manual DR doesn't meet RTO
- **Option B incorrect**: Cloud Storage doesn't meet <100ms for large images globally, no database mentioned
- **Option D incorrect**: Filestore expensive for 500TB, snapshots don't meet RPO=1hr

**Cost Estimate** (monthly):
- GKE: ~$3,000 (10-100 pods autoscaling)
-Cloud Storage: ~$10,000 (500TB Standard)
- Cloud SQL: ~$800 (HA configuration)
- Cloud CDN: ~$1,000 (egress + cache)
- Audit Logs: ~$500 (Data Access logs)
- **Total**: ~$15,300/month

---

## Question 4
Design a real-time analytics platform for an IoT company:
- 1 million devices sending metrics every 10 seconds
- Real-time dashboards (<1 second latency)
- Historical analysis (1 year retention)
- ML-based anomaly detection
- Cost-optimized

**A)** Devices → Cloud Pub/Sub → Dataflow → BigQuery + Bigtable

**B)** Devices → HTTP endpoints → Cloud Run → BigQuery

**C)** Devices → IoT Core → Pub/Sub → Dataflow → BigQuery (streaming) + Cloud Storage (batch)

**D)** Devices → Load Balancer → Compute Engine → Cloud SQL

**Correct Answer**: C

**Explanation**:
**Option C is the optimal architecture**:

```
[1M IoT Devices]
      ↓
[Cloud IoT Core] - Device authentication, per-device config
      ↓
[Cloud Pub/Sub] - Message ingestion, buffering
      ↓
    ┌─────┴─────┐
    ↓           ↓
[Dataflow]  [Dataflow]
(Stream)    (Batch)
    ↓           ↓
[BigQuery]  [Cloud Storage]
(Real-time) (Long-term/archive)
    ↓
[Looker/Data Studio] - Dashboards
    ↓
[Vertex AI] - Anomaly detection
```

**Implementation**:

```bash
# 1. IoT Core Setup
gcloud iot registries create device-registry \
  --project=PROJECT_ID \
  --region=us-central1 \
  --event-notification-config=topic=projects/PROJECT_ID/topics/iot-metrics

# 2. Pub/Sub Topic
gcloud pubsub topics create iot-metrics
gcloud pubsub subscriptions create iot-metrics-sub \
  --topic=iot-metrics \
  --ack-deadline=60

# 3. Dataflow Streaming Pipeline
# Apache Beam pipeline
```

```python
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions

class ParseIoTMessage(beam.DoFn):
    def process(self, element):
        import json
        data = json.loads(element)
        yield {
            'device_id': data['device_id'],
            'timestamp': data['timestamp'],
            'temperature': data['temperature'],
            'humidity': data['humidity'],
            'pressure': data['pressure']
        }

# Streaming to BigQuery
def run():
    options = PipelineOptions(
        streaming=True,
        project='PROJECT_ID',
        region='us-central1',
        temp_location='gs://temp-bucket/temp',
        staging_location='gs://temp-bucket/staging'
    )
    
    with beam.Pipeline(options=options) as pipeline:
        (pipeline
         | 'Read from Pub/Sub' >> beam.io.ReadFromPubSub(
             subscription='projects/PROJECT_ID/subscriptions/iot-metrics-sub')
         | 'Parse JSON' >> beam.ParDo(ParseIoTMessage())
         | 'Write to BigQuery' >> beam.io.WriteToBigQuery(
             'PROJECT_ID:iot_dataset.metrics',
             schema='device_id:STRING,timestamp:TIMESTAMP,temperature:FLOAT,humidity:FLOAT,pressure:FLOAT',
             write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND)
        )
```

```bash
# Run Dataflow job
python dataflow_pipeline.py \
  --runner=DataflowRunner \
  --project=PROJECT_ID \
  --region=us-central1 \
  --streaming

# 4. BigQuery Tables
# Real-time table (partitioned)
bq mk --table \
  --time_partitioning_field=timestamp \
  --time_partitioning_type=DAY \
  --clustering_fields=device_id \
  iot_dataset.metrics \
  schema.json

# 5. ML Anomaly Detection
bq query --use_legacy_sql=false '
CREATE OR REPLACE MODEL iot_dataset.anomaly_model
OPTIONS(
  model_type="AUTOML_REGRESSOR",
  input_label_cols=["temperature"]
) AS
SELECT
  device_id,
  timestamp,
  temperature,
  humidity,
  pressure
FROM
  iot_dataset.metrics
WHERE
  timestamp > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
'

# 6. Cost Optimization - Lifecycle Management
cat > bq_lifecycle.json <<EOF
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "SetStorageClass", "storageClass": "ARCHIVE"},
        "condition": {"age": 365}
      }
    ]
  }
}
EOF

# 7. Real-time Dashboard
# Data Studio connected to BigQuery with caching
```

**Scaling Math**:
- 1M devices × 1 message/10s = 100,000 msg/sec
- Message size: ~1KB
- Data rate: 100 MB/sec = 8.64 TB/day
- Monthly: ~260 TB

**Cost Optimization**:
```sql
-- BigQuery partitioning and clustering
CREATE TABLE iot_dataset.metrics_optimized
PARTITION BY DATE(timestamp)
CLUSTER BY device_id
AS SELECT * FROM iot_dataset.metrics;

-- Materialized view for common queries
CREATE MATERIALIZED VIEW iot_dataset.hourly_avg AS
SELECT
  device_id,
  TIMESTAMP_TRUNC(timestamp, HOUR) as hour,
  AVG(temperature) as avg_temp,
  AVG(humidity) as avg_humidity
FROM iot_dataset.metrics
GROUP BY device_id, hour;
```

**Monthly Cost Estimate**:
- IoT Core: ~$5,000 (1M devices, ~260M messages/month)
- Pub/Sub: ~$4,000 (260TB data)
- Dataflow: ~$3,000 (streaming workers)
- BigQuery: ~$5,200 (storage) + $1,000 (queries)
- Cloud Storage: ~$500 (archive)
- **Total**: ~$18,700/month

- **Option A**: Missing IoT Core for device management
- **Option B**: HTTP endpoints can't scale to 100K msg/sec reliably
- **Option D**: Cloud SQL can't handle this write throughput

---

## Question 5
A media company needs to transcode 10,000 hours of video daily. Requirements:
- Multiple output formats (1080p, 720p, 480p)
- Cost-effective
- Process within 12 hours
- Store results for 30 days

Design the architecture.

**A)** Compute Engine with manual scaling + Cloud Storage

**B)** Cloud Tasks + Cloud Run + Cloud Storage + Transcode API

**C)** GKE with batch jobs + Preemptible nodes + Cloud Storage + Lifecycle management

**D)** Dataflow + Cloud Functions + Cloud Storage

**Correct Answer**: C

**Explanation**:
**Option C provides optimal cost/performance**:

```bash
# 1. GKE Cluster with batch processing pool
gcloud container clusters create video-transcode \
  --region=us-central1 \
  --num-nodes=1  # Default pool for control plane

# 2. Preemptible node pool for batch jobs (70% cost savings)
gcloud container node-pools create batch-pool \
  --cluster=video-transcode \
  --region=us-central1 \
  --machine-type=n1-highcpu-16 \
  --preemptible \
  --num-nodes=0 \
  --enable-autoscaling \
  --min-nodes=0 \
  --max-nodes=100 \
  --node-labels=workload=batch

# 3. Kubernetes CronJob for daily processing
```

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: video-transcode-job
spec:
  schedule: "0 0 * * *"  # Daily at midnight
  jobTemplate:
    spec:
      parallelism: 50  # 50 pods in parallel
      completions: 500  # Total 500 jobs
      template:
        spec:
          nodeSelector:
            workload: batch
          tolerations:
          - key: preemptible
            operator: Equal
            value: "true"
            effect: NoSchedule
          containers:
          - name: transcoder
            image: gcr.io/PROJECT/video-transcoder:latest
            env:
            - name: INPUT_BUCKET
              value: "gs://raw-videos"
            - name: OUTPUT_BUCKET
              value: "gs://transcoded-videos"
            resources:
              requests:
                cpu: "8"
                memory: "16Gi"
              limits:
                cpu: "16"
                memory: "32Gi"
          restartPolicy: OnFailure
```

```python
# Transcoder application
from google.cloud import storage
import ffmpeg
import os

def transcode_video(input_path, output_bucket):
    """Transcode video to multiple formats"""
    formats = [
        {'resolution': '1920x1080', 'suffix': '1080p'},
        {'resolution': '1280x720', 'suffix': '720p'},
        {'resolution': '854x480', 'suffix': '480p'}
    ]
    
    for fmt in formats:
        output_path = f"/tmp/output_{fmt['suffix']}.mp4"
        
        # Transcode with ffmpeg
        (
            ffmpeg
            .input(input_path)
            .output(output_path, 
                   vf=f"scale={fmt['resolution']}", 
                   video_bitrate='2M',
                   audio_bitrate='128k')
            .run()
        )
        
        # Upload to Cloud Storage
        client = storage.Client()
        bucket = client.bucket(output_bucket)
        blob = bucket.blob(f"transcoded/{fmt['suffix']}/{os.path.basename(output_path)}")
        blob.upload_from_filename(output_path)
        
        os.remove(output_path)

if __name__ == '__main__':
    input_video = os.getenv('INPUT_VIDEO')
    output_bucket = os.getenv('OUTPUT_BUCKET')
    transcode_video(input_video, output_bucket)
```

```bash
# 4. Cloud Storage lifecycle for 30-day retention
cat > lifecycle.json <<EOF
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {
          "age": 30,
          "matchesPrefix": ["transcoded/"]
        }
      }
    ]
  }
}
EOF

gsutil lifecycle set lifecycle.json gs://transcoded-videos

# 5. Monitoring and alerts
gcloud monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="Transcode Job Failures" \
  --condition-display-name="Job failure rate > 5%" \
  --condition-threshold-value=0.05 \
  --condition-threshold>
  --condition-filter='resource.type="k8s_pod" AND resource.labels.namespace_name="default"'
```

**Scaling Calculation**:
- 10,000 hours of video/day
- 3 output formats = 30,000 transcode operations
- Assuming 1 hour video = 30 min transcode on n1-highcpu-16
- Need: 30,000 ops × 0.5 hr / 12 hrs = 1,250 concurrent node-hours
- With preemptible n1-highcpu-16: ~80 nodes peak

**Cost Estimate** (daily):
- Preemptible n1-highcpu-16: $0.142/hr × 16 vCPUs = $2.27/hr
- 1,250 node-hours × $2.27 = $2,837/day
- Monthly: ~$85,000
- **vs Standard VMs would be $285,000/month** (70% savings)

- **Option A**: Manual scaling doesn't optimize costs
- **Option B**: Cloud Run 15-min timeout insufficient for video transcoding
- **Option D**: Dataflow not designed for video processing

---

I'll continue creating more PCA questions. Would you like me to:
1. Continue with more architecture scenarios
2. Create topic-specific PCA tests (GKE, Networking, Security, Data, etc.)
3. Create full 50-question PCA practice exams

Let me know your preference!
