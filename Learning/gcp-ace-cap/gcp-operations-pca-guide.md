# Google Cloud Professional Cloud Architect (PCA) - Operations & SRE Architecture

## 1. Site Reliability Engineering (SRE) in Practice

### 1.1 The SRE Hierarchy
1.  **Monitoring**: "Something is broken."
2.  **Incident Response**: "Page the on-call engineer."
3.  **Post-Mortem**: "Why did it break? How do we fix the process?"
4.  **Testing & Release**: "Prevent breakage before it ships."
5.  **Capacity Planning**: "Will it break next Black Friday?"
6.  **Development**: "Building reliable systems."
7.  **Product**: "Feature velocity vs. Reliability."

### 1.2 Error Budgets & Burn Rates
*   **Concept**: 100% reliability is impossible and expensive.
*   **Error Budget**: `1 - SLO`. If SLO is 99.9%, you have 43 minutes of downtime per month.
*   **Burn Rate Alerting**:
    *   **Don't** alert if you have 1 error.
    *   **Do** alert if you are burning your budget at a rate that will exhaust it in 2 hours (Burn Rate = 14.4x).
    *   **Benefit**: Reduces pager fatigue.

### 1.3 Toil Reduction
*   **Toil**: Manual, repetitive, automatable, tactical work (e.g., manually restarting a server, manually resizing a disk).
*   **Goal**: Cap toil at 50% of engineering time. The rest goes to engineering (automation).

## 2. Enterprise Logging Architecture

### 2.1 The "Log Factory" Pattern
*   **Requirement**: Centralize logs for security, but allow teams to see their own logs.
*   **Design**:
    1.  **Organization Sink**: Exports *all* audit logs to a **Central Log Bucket** in a Security Project.
    2.  **Log Views**: Create a "Log View" on the Central Bucket that filters for `resource.project_id="app-project"`.
    3.  **IAM**: Grant the App Team `roles/logging.viewAccessor` on that specific Log View.
    4.  **Result**: Security sees everything. App Team sees only their project's logs, but cannot delete them.

### 2.2 Cost Optimization (Exclusion Filters)
*   **Problem**: Cloud Logging is expensive (/bin/zsh.50/GB).
*   **Solution**: Exclude high-volume, low-value logs at the **Sink** level.
    *   *Example*: Exclude HTTP 200 OK logs from the Load Balancer (keep only 4xx/5xx).
    *   *Example*: Exclude `k8s_container` debug logs.
    *   **Note**: Excluded logs are discarded *before* ingestion (you pay nothing).

## 3. Managed Service for Prometheus (GMP)

### 3.1 Architecture Choices
*   **Managed Collection (Recommended)**:
    *   You deploy a `PodMonitoring` Custom Resource (CR).
    *   Google manages the Prometheus server, scraper, and scaling.
    *   **Pros**: Zero ops, easy setup.
*   **Self-Deployed Collection**:
    *   You run your own Prometheus server.
    *   You add a sidecar to write data to Google Monarch.
    *   **Pros**: Drop-in replacement for existing complex Prometheus setups.

### 3.2 PromQL & Grafana
*   GMP is **100% compatible** with PromQL.
*   You can use **Grafana** as the visualization layer, pointing to GMP as the datasource.
*   **Global View**: Query metrics across 100 clusters in 10 regions in a single query without setting up Thanos Federation.

## 4. Compliance & Transparency

### 4.1 Access Transparency (AxT)
*   **What**: Logs generated when **Google Support** accesses your content.
*   **Why**: Verify that Google is only accessing data for valid support tickets.
*   **Requirement**: You must have an Enterprise Support plan.

### 4.2 Access Approval
*   **What**: Requires your **explicit approval** (via email/console) *before* Google Support can access your data.
*   **Workflow**:
    1.  Google Engineer requests access.
    2.  You get an email.
    3.  You click "Approve".
    4.  Access is granted for a limited time.

---

## 5. Observability Architecture Patterns

### 5.1 Three Pillars of Observability

```
┌──────────────────────────────────────────────────────────┐
│           OBSERVABILITY ARCHITECTURE                      │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  ┌────────────┐    ┌────────────┐    ┌────────────┐     │
│  │   Metrics  │    │    Logs    │    │   Traces   │     │
│  │  (What)    │    │   (Why)    │    │  (Where)   │     │
│  └────────────┘    └────────────┘    └────────────┘     │
│       │                  │                  │            │
│       ├─ CPU, Memory     ├─ Errors          ├─ Latency  │
│       ├─ Request rate    ├─ Context         ├─ Spans    │
│       └─ Error rate      └─ Events          └─ Deps     │
│                                                           │
│  Integration Layer:                                       │
│  ┌────────────────────────────────────────────────────┐  │
│  │     Cloud Monitoring + Logging + Trace             │  │
│  │     → Unified dashboard & correlation              │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

### 5.2 Multi-Cloud Observability

```
┌──────────────────────────────────────────────────────────┐
│          MULTI-CLOUD OBSERVABILITY                        │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  GCP Workloads       AWS Workloads      On-Prem          │
│  ┌────────────┐     ┌────────────┐     ┌────────────┐   │
│  │ Cloud      │     │ CloudWatch │     │ Prometheus │   │
│  │ Monitoring │     │  Agent     │     │            │   │
│  └────────────┘     └────────────┘     └────────────┘   │
│        │                  │                  │           │
│        └──────────────────┼──────────────────┘           │
│                           ▼                              │
│              ┌────────────────────────┐                  │
│              │   OpenTelemetry        │                  │
│              │   Collector            │                  │
│              └────────────────────────┘                  │
│                           │                              │
│        ┌──────────────────┼──────────────────┐           │
│        ▼                  ▼                  ▼           │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐       │
│  │  Cloud   │      │  Datadog │      │  Splunk  │       │
│  │Operations│      │          │      │          │       │
│  └──────────┘      └──────────┘      └──────────┘       │
│                                                           │
│  Unified Query & Analysis Layer                           │
└──────────────────────────────────────────────────────────┘
```

### 5.3 Distributed Tracing Architecture

```
┌──────────────────────────────────────────────────────────┐
│         DISTRIBUTED TRACING FLOW                          │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  User Request → API Gateway                               │
│                     │                                     │
│                     ├─ Trace ID: abc123                   │
│                     ├─ Parent Span: gateway               │
│                     │                                     │
│                     ▼                                     │
│              ┌────────────┐                               │
│              │ Service A  │ (span_id: A1)                 │
│              └────────────┘                               │
│                     │                                     │
│        ┌────────────┴────────────┐                        │
│        ▼                         ▼                        │
│  ┌────────────┐           ┌────────────┐                 │
│  │ Service B  │           │ Service C  │                 │
│  │(span_id:B1)│           │(span_id:C1)│                 │
│  └────────────┘           └────────────┘                 │
│        │                         │                        │
│        ▼                         ▼                        │
│  ┌────────────┐           ┌────────────┐                 │
│  │  Database  │           │  Cache     │                 │
│  │(span_id:D1)│           │(span_id:C2)│                 │
│  └────────────┘           └────────────┘                 │
│                                                           │
│  All spans share: trace_id=abc123                         │
│  Visualization: Waterfall showing latency breakdown       │
└──────────────────────────────────────────────────────────┘
```

---

## 6. SLI/SLO/SLA Design Framework

### 6.1 SLI (Service Level Indicator) Design

**Request-Based SLIs:**
```yaml
SLI: Availability
Definition: Percentage of successful requests
Formula: (count of 2xx responses) / (count of all responses)
Target: 99.9%

SLI: Latency
Definition: Percentage of requests under threshold
Formula: (count of requests < 500ms) / (count of all requests)
Target: 99% (p99 < 500ms)

SLI: Quality
Definition: Percentage of correct responses
Formula: (count of valid responses) / (count of all responses)
Target: 99.99%
```

**Windows-Based SLIs:**
```yaml
SLI: Uptime
Definition: Percentage of time system is available
Formula: (total uptime seconds) / (total period seconds)
Target: 99.95%

SLI: Data freshness
Definition: Percentage of time data is fresh
Formula: (time when data_age < 5min) / (total time)
Target: 99%
```

### 6.2 Error Budget Calculation

```python
# Example: E-commerce platform
slo = 0.999  # 99.9% availability
monthly_requests = 100_000_000  # 100M requests/month

# Error budget
error_budget = 1 - slo  # 0.001 = 0.1%
allowed_failures = monthly_requests * error_budget  # 100,000 failures/month

# Burn rate monitoring
current_failures = 5000  # in last hour
hours_in_month = 730

hourly_budget = allowed_failures / hours_in_month  # 137 failures/hour
burn_rate = current_failures / hourly_budget  # 36.5x

if burn_rate > 14.4:  # Will exhaust budget in 2 days
    alert("Critical: High error budget burn rate")
elif burn_rate > 2:  # Will exhaust budget in 15 days
    alert("Warning: Elevated error budget burn")
```

### 6.3 Multi-Window Burn Rate Alerting

```yaml
Alerting Policy:

Fast Burn (Page immediately):
  Window: 1 hour
  Burn Rate: > 14.4x (exhausts budget in 2 days)
  Long Window: 6 hours
  Action: Page on-call engineer

Medium Burn (Page in business hours):
  Window: 6 hours  
  Burn Rate: > 6x (exhausts budget in 5 days)
  Long Window: 24 hours
  Action: Create ticket

Slow Burn (Review weekly):
  Window: 24 hours
  Burn Rate: > 3x (exhausts budget in 10 days)
  Long Window: 3 days
  Action: Add to weekly review
```

---

## 7. Large-Scale Log Management

### 7.1 Log Aggregation Patterns

```
┌──────────────────────────────────────────────────────────┐
│        CENTRALIZED LOG AGGREGATION                        │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  Organization Level                                       │
│  ┌────────────────────────────────────────────────┐      │
│  │  Organization Aggregated Sink                  │      │
│  │  - Includes all projects                       │      │
│  │  - Filter: logName:cloudaudit                  │      │
│  │  - Destination: Central Log Bucket             │      │
│  └────────────────────────────────────────────────┘      │
│                          │                               │
│                          ▼                               │
│  ┌────────────────────────────────────────────────────┐  │
│  │     Security Project: central-logs-project        │  │
│  │  ┌──────────────────────────────────────────────┐ │  │
│  │  │  Log Bucket: audit-logs (7 year retention)  │ │  │
│  │  └──────────────────────────────────────────────┘ │  │
│  │                                                    │  │
│  │  ┌──────────────────────────────────────────────┐ │  │
│  │  │  Log Views (filtered access):                │ │  │
│  │  │  - prod-app-view (project="prod-app")        │ │  │
│  │  │  - dev-app-view (project="dev-app")          │ │  │
│  │  │  - security-view (all audit logs)            │ │  │
│  │  └──────────────────────────────────────────────┘ │  │
│  └────────────────────────────────────────────────────┘  │
│                          │                               │
│                          ▼                               │
│  ┌────────────────────────────────────────────────────┐  │
│  │     BigQuery: audit_logs_dataset                  │  │
│  │     - SQL analysis                                │  │
│  │     - Compliance reporting                        │  │
│  │     - Cost attribution                            │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

### 7.2 Log Retention Strategy

```yaml
Log Types and Retention:

Audit Logs (Compliance):
  Source: Cloud Audit Logs
  Retention: 7 years (regulatory requirement)
  Storage: Central log bucket → Cloud Storage (Nearline)
  Cost: ~$0.01/GB/month (Nearline)

Application Logs (Operational):
  Source: Cloud Run, GKE, Compute Engine
  Retention: 90 days (hot), 1 year (archive)
  Storage: Log bucket (90d) → BigQuery (analysis) → GCS (archive)
  Cost: $0.50/GB ingestion, $0.01/GB archive

Security Logs (Incident Response):
  Source: VPC Flow Logs, Firewall Logs
  Retention: 1 year
  Storage: Log bucket → SIEM (real-time) → GCS (archive)
  Cost: High volume, use sampling (10-50%)

Debug Logs (Development):
  Source: Application debug output
  Retention: 7 days
  Storage: Log bucket only (excluded from exports)
  Cost: Minimize with exclusion filters
```

### 7.3 Cost Optimization at Scale

```python
# Example: 10 TB/month of logs

# Scenario 1: No optimization
ingestion_cost = 10_000 * 0.50  # $5,000/month

# Scenario 2: With exclusions (50% reduction)
# Exclude: Debug logs, HTTP 200, Kubernetes system logs
ingestion_cost = 5_000 * 0.50  # $2,500/month
savings = $2,500/month

# Scenario 3: Sampling high-volume logs
# Sample VPC Flow Logs at 10%
vpc_flow_volume = 7_000  # GB/month (70% of total)
sampled_volume = vpc_flow_volume * 0.1
app_logs = 3_000
total_volume = sampled_volume + app_logs  # 3,700 GB
ingestion_cost = 3_700 * 0.50  # $1,850/month
savings = $3,150/month (63% reduction)

# Scenario 4: Tiered storage
ingestion_cost = 5_000 * 0.50  # $2,500
hot_storage = 5_000 * 0.01 * 3  # 90 days = $150
archive_storage = 5_000 * 0.004 * 12  # 1 year in Nearline = $240
total_cost = $2,890/month
vs_default_retention = 5_000 * 0.01 * 12  # $600/month storage saved
```

---

## 8. Prometheus and GMP Architecture

### 8.1 GMP Managed Collection

```yaml
# PodMonitoring Custom Resource
apiVersion: monitoring.googleapis.com/v1
kind: PodMonitoring
metadata:
  name: backend-monitoring
  namespace: production
spec:
  selector:
    matchLabels:
      app: backend
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
  targetLabels:
    metadata:
    - pod
    - namespace
```

### 8.2 Global Query Architecture

```
┌──────────────────────────────────────────────────────────┐
│         GLOBAL PROMETHEUS ARCHITECTURE                    │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  Region: us-central1        Region: europe-west1         │
│  ┌──────────────────┐      ┌──────────────────┐         │
│  │  GKE Cluster 1   │      │  GKE Cluster 2   │         │
│  │  ┌────────────┐  │      │  ┌────────────┐  │         │
│  │  │ Pods +     │  │      │  │ Pods +     │  │         │
│  │  │ /metrics   │  │      │  │ /metrics   │  │         │
│  │  └────────────┘  │      │  └────────────┘  │         │
│  │         │        │      │         │        │         │
│  │         ▼        │      │         ▼        │         │
│  │  ┌────────────┐  │      │  ┌────────────┐  │         │
│  │  │ GMP        │  │      │  │ GMP        │  │         │
│  │  │ Collector  │  │      │  │ Collector  │  │         │
│  │  └────────────┘  │      │  └────────────┘  │         │
│  └──────────────────┘      └──────────────────┘         │
│           │                         │                    │
│           └─────────────┬───────────┘                    │
│                         ▼                                │
│              ┌────────────────────┐                      │
│              │   Google Monarch   │                      │
│              │  (Global Datastore)│                      │
│              └────────────────────┘                      │
│                         │                                │
│        ┌────────────────┼────────────────┐               │
│        ▼                ▼                ▼               │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐           │
│  │ Grafana  │    │  Cloud   │    │  Alert   │           │
│  │          │    │ Monitoring│    │ Manager  │           │
│  └──────────┘    └──────────┘    └──────────┘           │
│                                                           │
│  Global PromQL Query:                                     │
│  sum(rate(http_requests_total[5m])) by (region)          │
│  → Aggregates across ALL clusters automatically          │
└──────────────────────────────────────────────────────────┘
```

### 8.3 Recording Rules for Performance

```yaml
# PromQL recording rules (pre-compute expensive queries)
apiVersion: monitoring.googleapis.com/v1
kind: Rules
metadata:
  name: recording-rules
spec:
  groups:
  - name: api_performance
    interval: 30s
    rules:
    # Record: Request rate per service
    - record: service:http_requests:rate5m
      expr: sum(rate(http_requests_total[5m])) by (service)
    
    # Record: Error rate per service
    - record: service:http_errors:rate5m
      expr: sum(rate(http_requests_total{status=~"5.."}[5m])) by (service)
    
    # Record: Error percentage
    - record: service:error_rate:percentage
      expr: |
        (service:http_errors:rate5m / service:http_requests:rate5m) * 100

# Benefits:
# - Query service:error_rate:percentage instead of complex calculation
# - Faster dashboards
# - Lower query costs
```

---

## 9. Compliance and Security Monitoring

### 9.1 Access Transparency Implementation

```bash
# Enable Access Transparency
gcloud organizations add-iam-policy-binding ORGANIZATION_ID \
    --member="domain:example.com" \
    --role="roles/accesstransparency.viewer"

# Create alert for Access Transparency events
cat > access-transparency-alert.json << 'EOF'
{
  "displayName": "Google Access Alert",
  "conditions": [{
    "displayName": "Access Transparency Event Detected",
    "conditionThreshold": {
      "filter": "logName:\"cloudaudit.googleapis.com/access_transparency\"",
      "comparison": "COMPARISON_GT",
      "thresholdValue": 0,
      "duration": "60s"
    }
  }],
  "notificationChannels": ["SECURITY_TEAM_CHANNEL"],
  "alertStrategy": {
    "notificationRateLimit": {
      "period": "300s"
    }
  }
}
EOF

gcloud alpha monitoring policies create --policy-from-file=access-transparency-alert.json
```

### 9.2 Compliance Audit Dashboard

```sql
-- BigQuery SQL for compliance reporting

-- 1. Who accessed PII data?
SELECT
  timestamp,
  principal_email,
  resource.labels.dataset_id,
  resource.labels.table_id,
  protopayload_auditlog.resourceName
FROM `security-project.audit_logs.cloudaudit_googleapis_com_data_access_*`
WHERE resource.type = 'bigquery_resource'
  AND protopayload_auditlog.resourceName LIKE '%pii_data%'
  AND _TABLE_SUFFIX BETWEEN '20240101' AND '20240131'
ORDER BY timestamp DESC;

-- 2. Configuration changes by admin
SELECT
  timestamp,
  principal_email,
  protopayload_auditlog.methodName,
  resource.type,
  severity
FROM `security-project.audit_logs.cloudaudit_googleapis_com_activity_*`
WHERE severity = 'NOTICE'
  AND _TABLE_SUFFIX BETWEEN '20240101' AND '20240131'
  AND protopayload_auditlog.methodName IN (
    'v1.compute.instances.delete',
    'v1.compute.firewalls.insert',
    'storage.buckets.delete'
  )
ORDER BY timestamp DESC;

-- 3. Failed authentication attempts
SELECT
  timestamp,
  principal_email,
  resource.labels.project_id,
  protopayload_auditlog.status.code,
  protopayload_auditlog.status.message
FROM `security-project.audit_logs.cloudaudit_googleapis_com_activity_*`
WHERE protopayload_auditlog.status.code = 16  -- UNAUTHENTICATED
  AND _TABLE_SUFFIX BETWEEN FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY))
      AND FORMAT_DATE('%Y%m%d', CURRENT_DATE())
GROUP BY 1, 2, 3, 4, 5
ORDER BY timestamp DESC;
```

---

## 10. Incident Response Architecture

### 10.1 Automated Remediation Pattern

```
┌──────────────────────────────────────────────────────────┐
│         AUTOMATED INCIDENT RESPONSE                       │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  Incident Detected                                        │
│  ┌────────────────┐                                       │
│  │ Alert Policy   │                                       │
│  │ (CPU > 90%)    │                                       │
│  └────────────────┘                                       │
│         │                                                 │
│         ▼                                                 │
│  ┌────────────────┐                                       │
│  │ Pub/Sub Topic  │                                       │
│  │ "alerts"       │                                       │
│  └────────────────┘                                       │
│         │                                                 │
│    ┌────┴─────┬──────────┬──────────┐                    │
│    ▼          ▼          ▼          ▼                    │
│  ┌─────┐  ┌───────┐  ┌────────┐  ┌──────┐               │
│  │Page │  │Ticket │  │Auto    │  │Log to│               │
│  │Duty │  │(Jira) │  │Remediate  │BigQuery              │
│  └─────┘  └───────┘  └────────┘  └──────┘               │
│                         │                                │
│                         ▼                                │
│              ┌────────────────────┐                       │
│              │ Cloud Function     │                       │
│              │ "auto-scale-up"    │                       │
│              └────────────────────┘                       │
│                         │                                │
│                         ▼                                │
│              ┌────────────────────┐                       │
│              │ Increase MIG size  │                       │
│              │ OR                 │                       │
│              │ Restart pods       │                       │
│              └────────────────────┘                       │
└──────────────────────────────────────────────────────────┘
```

### 10.2 Runbook Automation (Cloud Function)

```python
# Cloud Function triggered by Pub/Sub alert
import base64
import json
from google.cloud import compute_v1

compute_client = compute_v1.InstanceGroupManagersClient()

def auto_remediate(event, context):
    """Triggered by Pub/Sub alert."""
    
    # Parse alert
    message = base64.b64decode(event['data']).decode('utf-8')
    alert = json.loads(message)
    
    incident = alert.get('incident', {})
    condition = incident.get('condition_name', '')
    resource = incident.get('resource', {})
    
    # Identify remediation action
    if 'High CPU' in condition:
        project_id = resource.get('project_id')
        zone = resource.get('zone')
        instance_group = resource.get('instance_group')
        
        # Get current size
        igm = compute_client.get(
            project=project_id,
            zone=zone,
            instance_group_manager=instance_group
        )
        current_size = igm.target_size
        
        # Increase by 50%
        new_size = int(current_size * 1.5)
        
        # Apply resize
        operation = compute_client.resize(
            project=project_id,
            zone=zone,
            instance_group_manager=instance_group,
            size=new_size
        )
        
        print(f"Scaled {instance_group} from {current_size} to {new_size}")
        
        # Log to BigQuery for audit
        log_remediation(incident, 'scale_up', current_size, new_size)
    
    elif 'High Memory' in condition:
        # Trigger pod restart via GKE API
        restart_pods(resource)
    
    else:
        # Unknown condition - just log
        print(f"No remediation for: {condition}")

def log_remediation(incident, action, old_value, new_value):
    """Log remediation action for audit."""
    from google.cloud import bigquery
    
    client = bigquery.Client()
    table_id = "my-project.operations.remediation_log"
    
    rows_to_insert = [{
        "timestamp": datetime.datetime.now().isoformat(),
        "incident_id": incident.get('incident_id'),
        "action": action,
        "old_value": old_value,
        "new_value": new_value,
        "resource": json.dumps(incident.get('resource'))
    }]
    
    errors = client.insert_rows_json(table_id, rows_to_insert)
    if errors:
        print(f"Errors logging: {errors}")
```

---

## 11. Capacity Planning and Forecasting

### 11.1 Trend Analysis with MQL

```python
# Monitoring Query Language (MQL) for capacity planning

# Forecast CPU usage growth
fetch gce_instance
| metric 'compute.googleapis.com/instance/cpu/utilization'
| group_by 1h, [value_mean: mean(value.utilization)]
| every 1h
| forecast 30d  # Predict next 30 days

# Analyze storage growth rate
fetch gcs_bucket
| metric 'storage.googleapis.com/storage/total_bytes'
| group_by 1d, [value_sum: sum(value.total_bytes)]
| every 1d
| delta 1d  # Daily growth rate
```

### 11.2 Capacity Planning Dashboard (BigQuery)

```sql
-- Historical growth analysis
WITH daily_metrics AS (
  SELECT
    DATE(timestamp) as date,
    AVG(value.double_value) as avg_cpu,
    MAX(value.double_value) as max_cpu
  FROM `project.monitoring.compute_metrics`
  WHERE metric.type = 'compute.googleapis.com/instance/cpu/utilization'
    AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
  GROUP BY date
),
growth_analysis AS (
  SELECT
    date,
    avg_cpu,
    max_cpu,
    AVG(avg_cpu) OVER (ORDER BY date ROWS BETWEEN 7 PRECEDING AND CURRENT ROW) as moving_avg_7d,
    AVG(avg_cpu) OVER (ORDER BY date ROWS BETWEEN 30 PRECEDING AND CURRENT ROW) as moving_avg_30d
  FROM daily_metrics
)
SELECT
  date,
  avg_cpu,
  moving_avg_7d,
  moving_avg_30d,
  -- Linear regression for forecast
  (moving_avg_30d - LAG(moving_avg_30d, 30) OVER (ORDER BY date)) / 30 as daily_growth_rate,
  -- Project 90 days forward
  moving_avg_30d + ((moving_avg_30d - LAG(moving_avg_30d, 30) OVER (ORDER BY date)) / 30 * 90) as projected_90d
FROM growth_analysis
ORDER BY date DESC
LIMIT 100;
```

---

## 12. Integration with External SIEM

### 12.1 Splunk Integration

```bash
# Export logs to Pub/Sub
gcloud logging sinks create splunk-sink \
    pubsub.googleapis.com/projects/my-project/topics/logs-to-splunk \
    --log-filter='resource.type="gce_instance" OR logName:"cloudaudit"'

# Install Splunk Add-on for GCP
# Configure:
# - Project ID
# - Pub/Sub Subscription
# - Service Account with pubsub.subscriber role

# Splunk Search Examples:
# index=gcp source=cloudaudit | stats count by protoPayload.methodName
# index=gcp severity=ERROR | timechart count
```

### 12.2 Datadog Integration

```bash
# Install Datadog agent
DD_AGENT_MAJOR_VERSION=7 \
DD_API_KEY=YOUR_KEY \
DD_SITE="datadoghq.com" \
bash -c "$(curl -L https://s3.amazonaws.com/dd-agent/scripts/install_script.sh)"

# Configure GCP integration in Datadog UI
# - Enable Cloud Monitoring metric collection
# - Enable log collection (via Pub/Sub)
# - Install GKE integration for Kubernetes metrics

# Custom metrics from Cloud Monitoring
gcloud projects add-iam-policy-binding PROJECT_ID \
    --member="serviceAccount:datadog@PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/monitoring.viewer"
```

---

## 13. Real-World Reference Architectures

### 13.1 E-Commerce Platform Observability

```
┌──────────────────────────────────────────────────────────┐
│       E-COMMERCE OBSERVABILITY STACK                      │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  Application Tier (GKE)                                   │
│  ┌────────────────────────────────────────────────┐      │
│  │ Microservices (15 services)                    │      │
│  │ - Instrumented with OpenTelemetry              │      │
│  │ - Structured JSON logging                      │      │
│  │ - Prometheus /metrics endpoint                 │      │
│  └────────────────────────────────────────────────┘      │
│           │              │              │                │
│           ▼              ▼              ▼                │
│  ┌─────────────┐ ┌─────────────┐ ┌──────────────┐       │
│  │Cloud Logging│ │Cloud Trace  │ │GMP(Prometheus)       │
│  └─────────────┘ └─────────────┘ └──────────────┘       │
│           │              │              │                │
│           └──────────────┼──────────────┘                │
│                          ▼                               │
│           ┌──────────────────────────────┐               │
│           │   Cloud Monitoring           │               │
│           │   - Unified dashboards       │               │
│           │   - SLO tracking             │               │
│           │   - Error budget alerts      │               │
│           └──────────────────────────────┘               │
│                          │                               │
│        ┌─────────────────┼─────────────────┐             │
│        ▼                 ▼                 ▼             │
│  ┌──────────┐     ┌──────────┐     ┌──────────┐         │
│  │PagerDuty │     │BigQuery  │     │Grafana   │         │
│  │(Incidents)     │(Analysis)│     │(Custom   │         │
│  └──────────┘     └──────────┘     │Dashboards)         │
│                                     └──────────┘         │
│                                                           │
│  SLOs:                                                    │
│  - Availability: 99.9% (43 min downtime/month)            │
│  - Latency: p99 < 500ms                                   │
│  - Error rate: < 0.1%                                     │
│                                                           │
│  Cost: ~$2,000/month (100M requests/day)                  │
└──────────────────────────────────────────────────────────┘
```

### 13.2 Financial Services Compliance Architecture

```
┌──────────────────────────────────────────────────────────┐
│     FINANCIAL SERVICES COMPLIANCE OBSERVABILITY           │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  Production Workloads                                     │
│  ┌────────────────────────────────────────────────────┐  │
│  │ Trading Platform (GKE)                             │  │
│  │ Payment Gateway (Cloud Run)                        │  │
│  │ Risk Analytics (Compute Engine)                    │  │
│  └────────────────────────────────────────────────────┘  │
│                          │                               │
│                          ▼                               │
│  ┌────────────────────────────────────────────────────┐  │
│  │      Organization Aggregated Sink                  │  │
│  │      (ALL audit logs + application logs)           │  │
│  └────────────────────────────────────────────────────┘  │
│                          │                               │
│        ┌─────────────────┼─────────────────┐             │
│        ▼                 ▼                 ▼             │
│  ┌──────────┐     ┌──────────┐     ┌──────────┐         │
│  │Security  │     │BigQuery  │     │Cloud     │         │
│  │Project   │     │(7 years) │     │Storage   │         │
│  │Log Bucket│     │          │     │(Archive) │         │
│  │(immutable)     │          │     │          │         │
│  └──────────┘     └──────────┘     └──────────┘         │
│       │                 │                 │              │
│       ▼                 ▼                 ▼              │
│  ┌──────────────────────────────────────────────┐        │
│  │         Compliance Dashboards                │        │
│  │  - SOC 2 audit trail                         │        │
│  │  - PCI DSS transaction logs                  │        │
│  │  - GDPR data access reports                  │        │
│  │  - Access Transparency (Google access)       │        │
│  └──────────────────────────────────────────────┘        │
│                                                           │
│  Security Features:                                       │
│  - VPC-SC perimeter (no data exfiltration)                │
│  - CMEK encryption (customer keys)                        │
│  - Access Approval (explicit approval for Google access)  │
│  - Immutable log buckets (tamper-proof)                   │
│  - Real-time alerting (suspicious activity)               │
│                                                           │
│  Compliance: SOC 2, PCI DSS, GDPR, ISO 27001             │
└──────────────────────────────────────────────────────────┘
```

---

## 14. PCA Exam Decision Frameworks

### 14.1 Observability Tool Selection

```
Decision Tree:

Need to analyze application latency?
├── YES → **Cloud Trace**
│   └── Distributed tracing across microservices
└── NO
    └── Need to find performance bottlenecks?
        ├── YES → **Cloud Profiler**
        │   └── CPU/memory flame graphs
        └── NO
            └── Need to aggregate error logs?
                ├── YES → **Error Reporting**
                │   └── Automatic grouping of similar errors
                └── NO
                    └── Need custom metrics from logs?
                        ├── YES → **Log-based metrics**
                        └── NO
                            └── Standard metrics → **Cloud Monitoring**
```

### 14.2 Log Export Decision Matrix

| Requirement | Destination | Reasoning |
|-------------|-------------|-----------|
| **SQL analysis** | BigQuery | Query with SQL, create reports |
| **Long-term archive (7+ years)** | Cloud Storage | Cheapest ($0.01/GB/month) |
| **Real-time SIEM** | Pub/Sub → Splunk/Datadog | Stream to external tools |
| **Compliance audit** | Immutable log bucket | Tamper-proof, fixed retention |
| **Cost-sensitive** | Exclude + sample + GCS | Reduce ingestion + archive |

### 14.3 SLO Framework Selection

| Service Type | SLI | SLO Target | Example |
|--------------|-----|------------|---------|
| **User-facing API** | Availability + Latency | 99.9% availability, p99 < 500ms | REST API |
| **Batch processing** | Success rate | 99% successful jobs | ETL pipeline |
| **Data pipeline** | Freshness | 99% of data < 5 min old | Real-time analytics |
| **Storage** | Durability + Availability | 99.999999999% durability | Object storage |

---

## 15. PCA Exam Scenarios

### Scenario 1: Multi-Region SLO Enforcement

**Requirements:**
- Global application in 5 regions
- Overall SLO: 99.9% availability
- Regional failures shouldn't breach global SLO

**Solution:**
```yaml
Global SLO Design:

SLI: Weighted availability across regions
Formula: 
  (us_requests × us_availability + 
   eu_requests × eu_availability + ...) 
  / total_requests

Implementation:
1. Create regional SLIs in Cloud Monitoring
2. Use MQL to aggregate with request-weighted average
3. Set alert if global SLO at risk (error budget 50% consumed)
4. Regional degradation isolated (doesn't fail global SLO)

MQL Query:
fetch global_http_lb_rule
| metric 'loadbalancing.googleapis.com/https/request_count'
| group_by [region], [value_request_count_sum: sum(value.request_count)]
| join (
    fetch global_http_lb_rule
    | metric 'loadbalancing.googleapis.com/https/request_count'
    | filter response_code_class != '2xx'
    | group_by [region], [value_error_count_sum: sum(value.request_count)]
  )
| value [availability: 1 - (value_error_count_sum / value_request_count_sum)]
| group_by [], [global_availability: weighted_mean(availability, value_request_count_sum)]
```

### Scenario 2: Cost-Optimized Logging for Startup

**Requirements:**
- Startup with $500/month budget
- 1 TB/month of logs
- Need 30-day retention for debugging
- 1-year retention for compliance

**Solution:**
```bash
# Calculate costs without optimization:
# 1 TB × $0.50/GB = $500/month (at budget limit)

# Optimized approach:

# 1. Exclude debug logs (60% reduction)
gcloud logging exclusions create exclude-debug \
    --log-filter='severity < INFO'
# New volume: 400 GB/month

# 2. Sample high-volume logs (e.g., HTTP 200)
gcloud logging exclusions create sample-success \
    --log-filter='httpRequest.status = 200 AND NOT sample(insertId, 0.1)'
# Further reduction: 400 GB → 250 GB

# 3. Short retention in log bucket (30 days)
gcloud logging buckets update _Default \
    --retention-days=30

# 4. Export to Cloud Storage for 1-year compliance
gcloud logging sinks create archive-sink \
    storage.googleapis.com/compliance-logs-bucket \
    --log-filter='severity >= INFO'

# Final cost:
# Ingestion: 250 GB × $0.50 = $125/month
# Storage (30d): 250 GB × $0.01 = $2.50/month
# Archive (GCS): 250 GB × 12 months × $0.02/GB = $60/year = $5/month
# Total: $132.50/month (73% savings)
```

### Scenario 3: Financial Trading Platform with Sub-Second SLO

**Requirements:**
- p99 latency < 100ms
- 99.99% availability
- Real-time alerting (< 10 seconds)
- Full traceability for regulatory compliance

**Solution:**
```yaml
Architecture:

1. Instrumentation:
   - OpenTelemetry for distributed tracing
   - Custom metrics: trade_latency_ms, trade_success_rate
   - Structured logging with trade_id for correlation

2. Monitoring:
   - GMP for metrics (30s scrape interval)
   - Cloud Trace for latency analysis
   - Log-based metrics for error tracking

3. SLI/SLO:
   SLI: trade_latency_ms < 100 (p99)
   SLO: 99.99% of trades under 100ms
   Error Budget: 0.01% = 43 seconds downtime/month

4. Alerting:
   - Fast burn (1 min window, burn rate > 14.4x) → Page
   - Medium burn (10 min window, burn rate > 6x) → Ticket
   - Notification latency: < 10 seconds (Pub/Sub → Cloud Functions)

5. Compliance:
   - All trades logged to immutable log bucket
   - Exported to BigQuery for audit queries
   - Retention: 7 years
   - Access Transparency enabled

Cost: ~$5,000/month (1M trades/day)
```

---

**End of Operations PCA Guide**
