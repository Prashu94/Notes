# Chapter 06: Operations, Reliability, and SRE

Modern cloud operations are based on Google's Site Reliability Engineering (SRE) principles. You must design for operational excellence.

> **SRE Definition**: "SRE is what happens when you ask a software engineer to design an operations team." — Ben Treynor, VP Engineering at Google

## 📈 Google Cloud Operations Suite

### Cloud Monitoring

**Core Components**:
- **Metrics**: Time-series data from resources
- **Dashboards**: Custom visualizations
- **Alerting Policies**: Notifications based on conditions
- **Uptime Checks**: External availability monitoring
- **Service Monitoring**: SLO tracking

**Example: Create Custom Dashboard and Alert**
```bash
# Create a dashboard (using gcloud with JSON config)
gcloud monitoring dashboards create --config-from-file=dashboard.json

# dashboard.json example:
# {
#   "displayName": "Application Performance",
#   "gridLayout": {
#     "columns": 2,
#     "widgets": [
#       {
#         "title": "CPU Utilization",
#         "xyChart": {
#           "dataSets": [{
#             "timeSeriesQuery": {
#               "timeSeriesFilter": {
#                 "filter": "metric.type=\"compute.googleapis.com/instance/cpu/utilization\"",
#                 "aggregation": {"perSeriesAligner": "ALIGN_MEAN"}
#               }
#             }
#           }]
#         }
#       }
#     ]
#   }
# }

# Create an alerting policy
gcloud alpha monitoring policies create \
    --policy-from-file=alert-policy.yaml
```

**Alert Policy YAML**:
```yaml
displayName: "High CPU Alert"
combiner: OR
conditions:
  - displayName: "CPU > 80%"
    conditionThreshold:
      filter: 'metric.type="compute.googleapis.com/instance/cpu/utilization" AND resource.type="gce_instance"'
      comparison: COMPARISON_GT
      thresholdValue: 0.8
      duration: "300s"
      aggregations:
        - alignmentPeriod: "60s"
          perSeriesAligner: ALIGN_MEAN
notificationChannels:
  - projects/my-project/notificationChannels/12345
alertStrategy:
  autoClose: "604800s"
```

### Cloud Logging

**Architecture**:
```
┌─────────────────────────────────────────────────────────────────┐
│                    Cloud Logging Flow                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [Log Sources]                                                   │
│       ↓                                                          │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              Cloud Logging Router                        │    │
│  │   (Inclusion/Exclusion filters applied here)            │    │
│  └─────────────────────────────────────────────────────────┘    │
│       ↓                          ↓                    ↓         │
│  [_Required]              [Log Sinks]           [_Default]      │
│  (Admin Activity,         (Export to:)          (Retained       │
│   System Events)          • Cloud Storage       30 days)        │
│                           • BigQuery                             │
│                           • Pub/Sub                              │
│                           • Splunk/Other                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Example: Log Sink to BigQuery**
```bash
# Create a dataset for logs
bq mk --dataset --location=US my-project:logs_dataset

# Create a log sink to BigQuery
gcloud logging sinks create bigquery-sink \
    bigquery.googleapis.com/projects/my-project/datasets/logs_dataset \
    --log-filter='resource.type="gce_instance" OR resource.type="k8s_container"' \
    --use-partitioned-tables

# Grant sink service account access to BigQuery
gcloud projects add-iam-policy-binding my-project \
    --member="serviceAccount:serviceAccount-12345@gcp-sa-logging.iam.gserviceaccount.com" \
    --role="roles/bigquery.dataEditor"
```

**Example: Log-based Metric**
```bash
# Create a log-based metric for error counting
gcloud logging metrics create error-count \
    --description="Count of application errors" \
    --log-filter='resource.type="k8s_container" AND severity>=ERROR' \
    --bucket-name=_Default
```

### Error Reporting

Automatically aggregates and de-duplicates errors from your applications.

**Supported Languages**: Java, Python, Go, Node.js, Ruby, PHP, .NET

**Example: Error Reporting Integration (Python)**
```python
from google.cloud import error_reporting

# Initialize client
client = error_reporting.Client()

try:
    # Your application code
    process_request()
except Exception:
    # Report exception to Error Reporting
    client.report_exception()
```

## 🤝 SRE Fundamentals

### SLI/SLO/SLA Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│                   SLI → SLO → SLA → Error Budget               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  SLI (Service Level Indicator)                                   │
│  ├─ The METRIC you measure                                      │
│  ├─ Example: "Latency of 95th percentile requests"             │
│  └─ Example: "Error rate of API requests"                       │
│                                                                  │
│  SLO (Service Level Objective)                                   │
│  ├─ The TARGET for your SLI                                     │
│  ├─ Example: "99.9% of requests < 200ms"                        │
│  └─ Example: "Error rate < 0.1%"                                │
│                                                                  │
│  SLA (Service Level Agreement)                                   │
│  ├─ The PROMISE to customers (with consequences)               │
│  └─ Example: "99.9% uptime or service credits"                  │
│                                                                  │
│  Error Budget = 1 - SLO                                         │
│  ├─ If SLO = 99.9%, Error Budget = 0.1%                        │
│  ├─ ~43 minutes downtime per month                              │
│  └─ Use budget for: deployments, experiments, incidents        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Common SLIs by Service Type

| Service Type | Availability SLI | Latency SLI | Quality SLI |
| :--- | :--- | :--- | :--- |
| **Web Service** | % successful requests | p50, p95, p99 latency | Error rate |
| **Data Pipeline** | % records processed | End-to-end duration | Data freshness |
| **Storage** | % successful operations | Operation latency | Durability |
| **Batch Job** | % successful completions | Job duration | Output quality |

### Defining SLOs in Cloud Monitoring

**Example: Create SLO for Cloud Run Service**
```bash
# Create an availability SLO
gcloud monitoring slo create \
    --service=my-cloud-run-service \
    --slo-id=availability-slo \
    --display-name="Availability SLO" \
    --goal=0.999 \
    --rolling-period-days=28 \
    --request-based-sli='{"goodTotalRatioThreshold":{"threshold":0.99,"basicSliPerformance":{"availability":{}}}}'

# Create a latency SLO
gcloud monitoring slo create \
    --service=my-cloud-run-service \
    --slo-id=latency-slo \
    --display-name="Latency SLO (p99 < 500ms)" \
    --goal=0.99 \
    --rolling-period-days=28 \
    --request-based-sli='{"goodTotalRatioThreshold":{"threshold":0.99,"basicSliPerformance":{"latency":{"threshold":"500ms"}}}}'
```

### Error Budget Policy

```yaml
# Example Error Budget Policy (Document)
error_budget_policy:
  service: "payment-service"
  slo_target: 99.9%
  
  actions:
    - condition: "budget_remaining > 50%"
      allowed:
        - "Feature deployments"
        - "Infrastructure changes"
        - "Experiments"
    
    - condition: "budget_remaining > 25%"
      allowed:
        - "Critical bug fixes"
        - "Security patches"
      not_allowed:
        - "New feature deployments"
    
    - condition: "budget_remaining < 25%"
      allowed:
        - "Reliability improvements only"
      escalation:
        - "All hands on reliability"
        - "Halt feature development"
```

## 🚀 Deployment Strategies

### Comparison Matrix

| Strategy | Zero Downtime | Rollback Speed | Risk Level | Cost | Best For |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Recreate** | No | Slow | High | Low | Non-critical, dev |
| **Rolling Update** | Yes | Medium | Medium | Low | Standard updates |
| **Blue/Green** | Yes | Fast | Low | High (2x resources) | Critical services |
| **Canary** | Yes | Fast | Very Low | Medium | Production testing |
| **A/B Testing** | Yes | Fast | Low | Medium | Feature experiments |

### Blue/Green Deployment

```
┌─────────────────────────────────────────────────────────────────┐
│                    Blue/Green Deployment                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  STEP 1: Initial State                                           │
│  ┌─────────────┐                                                │
│  │ Load        │──────────► [Blue Environment v1.0]            │
│  │ Balancer    │            (100% traffic)                      │
│  └─────────────┘                                                │
│                                                                  │
│  STEP 2: Deploy New Version                                      │
│  ┌─────────────┐                                                │
│  │ Load        │──────────► [Blue Environment v1.0]            │
│  │ Balancer    │            (100% traffic)                      │
│  └─────────────┘            [Green Environment v2.0]           │
│                              (0% traffic - testing)             │
│                                                                  │
│  STEP 3: Switch Traffic                                          │
│  ┌─────────────┐                                                │
│  │ Load        │──────────► [Green Environment v2.0]           │
│  │ Balancer    │            (100% traffic)                      │
│  └─────────────┘            [Blue Environment v1.0]            │
│                              (standby for rollback)             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Example: Blue/Green with Cloud Run**
```bash
# Deploy new revision without traffic
gcloud run deploy my-service \
    --image=gcr.io/my-project/my-service:v2 \
    --region=us-central1 \
    --no-traffic \
    --tag=green

# Test the new revision
curl https://green---my-service-abc123.run.app

# Gradually shift traffic
gcloud run services update-traffic my-service \
    --region=us-central1 \
    --to-tags=green=10

# If successful, shift all traffic
gcloud run services update-traffic my-service \
    --region=us-central1 \
    --to-latest

# Rollback if needed
gcloud run services update-traffic my-service \
    --region=us-central1 \
    --to-revisions=my-service-00001-abc=100
```

### Canary Deployment

```bash
# GKE with Istio/Anthos Service Mesh
# VirtualService for canary routing
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: my-service
spec:
  hosts:
    - my-service
  http:
    - match:
        - headers:
            x-canary:
              exact: "true"
      route:
        - destination:
            host: my-service
            subset: canary
    - route:
        - destination:
            host: my-service
            subset: stable
          weight: 95
        - destination:
            host: my-service
            subset: canary
          weight: 5
```

## 🛠️ Performance & Observability

### Cloud Trace

Distributed tracing for microservices to identify bottlenecks.

**Example: Custom Trace Span (Python)**
```python
from opentelemetry import trace
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Configure tracing
trace.set_tracer_provider(TracerProvider())
cloud_trace_exporter = CloudTraceSpanExporter()
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(cloud_trace_exporter)
)

tracer = trace.get_tracer(__name__)

@tracer.start_as_current_span("process_order")
def process_order(order_id):
    with tracer.start_as_current_span("validate_order"):
        validate_order(order_id)
    
    with tracer.start_as_current_span("charge_payment"):
        charge_payment(order_id)
    
    with tracer.start_as_current_span("update_inventory"):
        update_inventory(order_id)
```

### Cloud Profiler

Continuous CPU and memory profiling with minimal overhead.

**Example: Enable Profiler (Python)**
```python
import googlecloudprofiler

def main():
    # Start profiler
    try:
        googlecloudprofiler.start(
            service='my-service',
            service_version='1.0.0',
            verbose=3,
            project_id='my-project'
        )
    except (ValueError, NotImplementedError) as e:
        print(f"Could not start profiler: {e}")
    
    # Your application code
    run_application()

if __name__ == '__main__':
    main()
```

## 🆘 Disaster Recovery (DR)

### RTO and RPO Definitions

| Metric | Definition | Question Answered |
| :--- | :--- | :--- |
| **RTO** (Recovery Time Objective) | Max acceptable downtime | "How fast do we need to be back up?" |
| **RPO** (Recovery Point Objective) | Max acceptable data loss | "How much data can we lose?" |

### DR Patterns

| Pattern | RTO | RPO | Cost | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Backup & Restore** | Hours-Days | Hours | $ | Restore from backups |
| **Pilot Light** | Hours | Minutes | $$ | Minimal always-on infra |
| **Warm Standby** | Minutes-Hours | Minutes | $$$ | Scaled-down replica |
| **Hot Standby (Active-Active)** | Near-zero | Near-zero | $$$$ | Full replica, traffic split |

### DR Architecture Example

```
┌─────────────────────────────────────────────────────────────────┐
│                Multi-Region DR Architecture                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [Global Load Balancer]                                          │
│       ├────────────────────────────────────────┐                │
│       ↓                                        ↓                │
│  ┌─────────────────────┐        ┌─────────────────────┐        │
│  │   PRIMARY REGION    │        │   DR REGION         │        │
│  │   (us-central1)     │        │   (us-east1)        │        │
│  ├─────────────────────┤        ├─────────────────────┤        │
│  │ • Cloud Run (Active)│        │ • Cloud Run (Warm)  │        │
│  │ • Cloud SQL (Primary│◄──────►│ • Cloud SQL (Replica│        │
│  │ • GCS (Primary)     │  Sync  │ • GCS (Replica)     │        │
│  └─────────────────────┘        └─────────────────────┘        │
│                                                                  │
│  Failover: Automatic via Health Checks + DNS                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Example: Cloud SQL Cross-Region Replica**
```bash
# Create primary instance
gcloud sql instances create primary-db \
    --database-version=POSTGRES_15 \
    --tier=db-custom-4-16384 \
    --region=us-central1 \
    --availability-type=REGIONAL

# Create cross-region read replica
gcloud sql instances create dr-replica \
    --master-instance-name=primary-db \
    --region=us-east1 \
    --tier=db-custom-4-16384

# In disaster scenario, promote replica
gcloud sql instances promote-replica dr-replica
```

### Backup Strategies

```bash
# Cloud SQL automated backups
gcloud sql instances patch my-instance \
    --backup-start-time=02:00 \
    --enable-point-in-time-recovery \
    --retained-backups-count=14 \
    --transaction-log-retention-days=7

# GCS bucket versioning and lifecycle
gsutil versioning set on gs://critical-data-bucket
gsutil lifecycle set lifecycle.json gs://critical-data-bucket

# lifecycle.json for versioned objects:
# {
#   "rule": [
#     {
#       "action": {"type": "Delete"},
#       "condition": {"isLive": false, "numNewerVersions": 3}
#     }
#   ]
# }

# GKE backup with Backup for GKE
gcloud container backup-restore backup-plans create my-backup-plan \
    --cluster=projects/my-project/locations/us-central1/clusters/my-cluster \
    --location=us-central1 \
    --all-namespaces \
    --cron-schedule="0 2 * * *" \
    --backup-retain-days=30
```

## 📊 Incident Management

### Incident Response Framework

```
┌─────────────────────────────────────────────────────────────────┐
│                   Incident Response Lifecycle                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. DETECT ──► 2. TRIAGE ──► 3. RESPOND ──► 4. RESOLVE         │
│       │            │             │              │                │
│       ↓            ↓             ↓              ↓                │
│  Monitoring    Severity      Mitigation    Root Cause           │
│  Alerts        Assessment    Actions       Analysis             │
│                                                                  │
│  5. LEARN (Post-mortem)                                         │
│       │                                                          │
│       ↓                                                          │
│  Blameless     Action Items    Prevention                       │
│  Review        Created         Measures                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Post-Mortem Template

```markdown
## Incident Report: [Title]

### Summary
- **Date**: YYYY-MM-DD
- **Duration**: X hours Y minutes
- **Impact**: [Description of user/business impact]
- **Severity**: P1/P2/P3/P4

### Timeline
| Time (UTC) | Event |
|------------|-------|
| 14:00 | Alert triggered for high error rate |
| 14:05 | On-call engineer acknowledged |
| 14:15 | Root cause identified |
| 14:30 | Mitigation applied |
| 15:00 | Service restored |

### Root Cause
[Technical explanation of what caused the incident]

### Impact
- X users affected
- Y transactions failed
- $Z revenue impact

### Action Items
| Action | Owner | Due Date | Priority |
|--------|-------|----------|----------|
| Add monitoring for X | @engineer | 2024-01-30 | P1 |
| Update runbook | @oncall | 2024-02-05 | P2 |

### Lessons Learned
- What went well
- What didn't go well
- Where we got lucky
```

---

📚 **Documentation Links**:
- [Cloud Monitoring Documentation](https://cloud.google.com/monitoring/docs)
- [Cloud Logging Documentation](https://cloud.google.com/logging/docs)
- [Cloud Trace Documentation](https://cloud.google.com/trace/docs)
- [Site Reliability Engineering Book](https://sre.google/sre-book/table-of-contents/)
- [Disaster Recovery Planning Guide](https://cloud.google.com/architecture/dr-scenarios-planning-guide)
- [Error Reporting Documentation](https://cloud.google.com/error-reporting/docs)

---
[Next Chapter: Google Cloud Well-Architected Framework](07_Google_Cloud_Well_Architected_Framework.md)
