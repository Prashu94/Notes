# Cloud Operations (Monitoring & Logging) - ACE Practice Questions

## Question 1
You need to monitor CPU utilization of all Compute Engine instances and receive an email alert when it exceeds 80% for 5 minutes. What should you create?

**A)** Cloud Monitoring alert policy with email notification channel

**B)** Cloud Logging sink to BigQuery

**C)** Custom dashboard in Cloud Monitoring

**D)** Uptime check for each instance

**Correct Answer:** A

**Explanation:**
- Option A is correct because:
  - Alert policies monitor metrics and trigger notifications
  - Can specify threshold conditions (80% CPU)
  - Duration requirement (5 minutes)
  - Email notification channels for alerts
  - Designed exactly for this use case

Create alert policy:
```bash
# Create notification channel (email)
gcloud alpha monitoring channels create \
  --display-name="Ops Team Email" \
  --type=email \
  --channel-labels=email_address=ops@example.com

# Get channel ID
CHANNEL_ID=$(gcloud alpha monitoring channels list \
  --filter="displayName='Ops Team Email'" \
  --format="value(name)")

# Create alert policy via YAML
cat > alert-policy.yaml <<EOF
displayName: "High CPU Alert"
conditions:
  - displayName: "CPU usage above 80%"
    conditionThreshold:
      filter: 'resource.type="gce_instance" AND metric.type="compute.googleapis.com/instance/cpu/utilization"'
      comparison: COMPARISON_GT
      thresholdValue: 0.80
      duration: 300s  # 5 minutes
      aggregations:
        - alignmentPeriod: 60s
          perSeriesAligner: ALIGN_MEAN
notificationChannels:
  - ${CHANNEL_ID}
alertStrategy:
  autoClose: 604800s  # 7 days
EOF

gcloud alpha monitoring policies create --policy-from-file=alert-policy.yaml
```

Via Console UI:
```
1. Cloud Monitoring > Alerting > Create Policy
2. Add Condition:
   - Resource: VM Instance
   - Metric: CPU utilization
   - Threshold: > 80%
   - For: 5 minutes
3. Notifications: ops@example.com
4. Documentation: "High CPU usage detected"
5. Save
```

Common alert conditions:
```yaml
# Memory utilization
filter: 'resource.type="gce_instance" AND metric.type="compute.googleapis.com/instance/memory/utilization"'
thresholdValue: 0.90

# Disk utilization
filter: 'resource.type="gce_instance" AND metric.type="compute.googleapis.com/instance/disk/utilization"'
thresholdValue: 0.85

# HTTP 5xx errors
filter: 'resource.type="http_load_balancer" AND metric.type="loadbalancing.googleapis.com/https/request_count" AND metric.label.response_code_class="500"'

# Cloud SQL connections
filter: 'resource.type="cloudsql_database" AND metric.type="cloudsql.googleapis.com/database/network/connections"'
thresholdValue: 100
```

- Option B is incorrect because:
  - Logging sinks export logs, don't create alerts
  - No threshold monitoring or notifications
  - Different use case (log analysis)

- Option C is incorrect because:
  - Dashboards visualize metrics, don't send alerts
  - No notification capability
  - Monitoring only, no alerting

- Option D is incorrect because:
  - Uptime checks monitor endpoint availability
  - Don't monitor CPU or resource metrics
  - Different purpose (HTTP/HTTPS endpoint monitoring)

**Alert Policy Components:**
- **Conditions**: What to monitor (metrics, thresholds)
- **Notification Channels**: Where to send alerts (email, SMS, PagerDuty, Slack)
- **Documentation**: Context for responders
- **Auto-close**: When to auto-resolve alerts

---

## Question 2
You need to view all error logs from your Cloud Run service in the last 24 hours. What query should you use in Cloud Logging?

**A)**
```
resource.type="cloud_run_revision"
severity>=ERROR
timestamp>="2024-01-20T00:00:00Z"
```

**B)**
```
resource.type="cloud_run_revision"
logName:"stderr"
```

**C)**
```
resource.type="cloud_run_revision"
severity>=ERROR
timestamp>"-24h"
```

**D)**
```
resource.type="gce_instance"
textPayload:"ERROR"
```

**Correct Answer:** C

**Explanation:**
- Option C is correct because:
  - Filters for Cloud Run resources
  - Severity >= ERROR captures ERROR, CRITICAL, ALERT, EMERGENCY
  - Relative timestamp `-24h` is simpler than absolute time
  - Returns last 24 hours of error logs

Cloud Logging queries:
```bash
# View Cloud Run errors (last 24 hours)
gcloud logging read \
  'resource.type="cloud_run_revision" AND
   severity>=ERROR AND
   timestamp>="-24h"' \
  --limit=50 \
  --format=json

# Specific Cloud Run service
gcloud logging read \
  'resource.type="cloud_run_revision" AND
   resource.labels.service_name="my-service" AND
   severity>=ERROR' \
  --limit=100

# Filter by specific error message
gcloud logging read \
  'resource.type="cloud_run_revision" AND
   textPayload=~"Database connection failed"' \
  --limit=20

# JSON payload filtering
gcloud logging read \
  'resource.type="cloud_run_revision" AND
   jsonPayload.error_code="500"'
```

In Cloud Console Logs Explorer:
```
resource.type="cloud_run_revision"
resource.labels.service_name="my-service"
severity>=ERROR
timestamp>="-24h"
```

Common severity levels:
```
DEFAULT   (0) - Default log level
DEBUG     (100) - Debug messages
INFO      (200) - Informational messages
NOTICE    (300) - Normal but significant
WARNING   (400) - Warning conditions
ERROR     (500) - Error conditions
CRITICAL  (600) - Critical conditions
ALERT     (700) - Action must be taken immediately
EMERGENCY (800) - System is unusable
```

Resource types:
```bash
# Compute Engine
resource.type="gce_instance"

# GKE
resource.type="k8s_container"
resource.labels.cluster_name="my-cluster"

# Cloud Functions
resource.type="cloud_function"

# App Engine
resource.type="gae_app"

# Cloud SQL
resource.type="cloudsql_database"

# Load Balancer
resource.type="http_load_balancer"
```

- Option A is incorrect because:
  - Absolute timestamp requires exact date
  - Less flexible than relative time
  - Works but not as convenient

- Option B is incorrect because:
  - Filtering by logName doesn't guarantee severity filtering
  - stderr might have non-error logs
  - Not the standard way to filter by severity

- Option D is incorrect because:
  - Wrong resource type (gce_instance vs cloud_run_revision)
  - textPayload search is substring match, less precise than severity
  - Not querying Cloud Run logs

**Log Query Operators:**
- `AND`, `OR`, `NOT` - Boolean operators
- `=`, `!=` - Equality
- `=~`, `!~` - Regex match
- `>`, `>=`, `<`, `<=` - Comparison
- `:` - Has (field exists)

---

## Question 3
Your application logs need to be retained for 90 days for compliance, but Cloud Logging only retains logs for 30 days. What should you do?

**A)** Increase Cloud Logging retention to 90 days

**B)** Create a log sink to export logs to Cloud Storage

**C)** Download logs daily and store locally

**D)** Use Cloud Monitoring to store logs

**Correct Answer:** B

**Explanation:**
- Option B is correct because:
  - Log sinks export logs to long-term storage
  - Cloud Storage retention can be configured
  - Automatic, continuous export
  - Cost-effective for long-term retention
  - Can export to BigQuery or Cloud Storage

Create log sink:
```bash
# Create Cloud Storage bucket for logs
gsutil mb gs://my-logs-archive

# Create log sink to Cloud Storage
gcloud logging sinks create my-log-sink \
  storage.googleapis.com/my-logs-archive \
  --log-filter='resource.type="cloud_run_revision" OR resource.type="gce_instance"'

# Grant sink permission to write to bucket
PROJECT_NUMBER=$(gcloud projects describe PROJECT_ID --format="value(projectNumber)")
SINK_SA="serviceAccount:cloud-logs@system.gserviceaccount.com"

gsutil iam ch ${SINK_SA}:roles/storage.objectCreator gs://my-logs-archive

# Verify sink
gcloud logging sinks describe my-log-sink
```

Export to BigQuery (for analysis):
```bash
# Create BigQuery dataset
bq mk --dataset logs_archive

# Create log sink to BigQuery
gcloud logging sinks create bigquery-sink \
  bigquery.googleapis.com/projects/PROJECT_ID/datasets/logs_archive \
  --log-filter='severity>=ERROR'

# Grant permissions
bq add-iam-policy-binding logs_archive \
  --member='serviceAccount:cloud-logs@system.gserviceaccount.com' \
  --role='roles/bigquery.dataEditor'
```

Set bucket lifecycle policy for compliance:
```json
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {"age": 90}
      }
    ]
  }
}
```

```bash
gsutil lifecycle set lifecycle-policy.json gs://my-logs-archive
```

Export to Pub/Sub (for real-time processing):
```bash
# Create Pub/Sub topic
gcloud pubsub topics create log-events

# Create log sink to Pub/Sub
gcloud logging sinks create pubsub-sink \
  pubsub.googleapis.com/projects/PROJECT_ID/topics/log-events \
  --log-filter='severity>=WARNING'
```

- Option A is incorrect because:
  - Cloud Logging retention is fixed at 30 days (cannot increase)
  - No option to extend beyond 30 days in Cloud Logging
  - Must use log sinks for longer retention

- Option C is incorrect because:
  - Manual process, not scalable
  - Risk of data loss
  - Operational overhead
  - Log sinks are automated

- Option D is incorrect because:
  - Cloud Monitoring is for metrics, not log storage
  - Doesn't provide long-term log retention
  - Wrong service

**Log Sink Destinations:**
- **Cloud Storage**: Long-term archival
- **BigQuery**: Log analysis and queries
- **Pub/Sub**: Real-time log processing
- **Another Cloud Logging bucket**: Cross-project aggregation

---

## Question 4
You need to create a custom metric that tracks the number of failed login attempts from your application logs. What should you do?

**A)** Use a log-based metric in Cloud Logging

**B)** Write a Cloud Function to count logs and push to Monitoring

**C)** Export logs to BigQuery and run queries

**D)** Create a Cloud Monitoring dashboard with manual data entry

**Correct Answer:** A

**Explanation:**
- Option A is correct because:
  - Log-based metrics automatically count log entries matching a filter
  - Appears as a metric in Cloud Monitoring
  - Can create alerts on log-based metrics
  - No custom code needed
  - Real-time metric updates

Create log-based metric:
```bash
# Create counter metric for failed logins
gcloud logging metrics create failed_logins \
  --description="Count of failed login attempts" \
  --log-filter='jsonPayload.event_type="login_failed"'

# Create distribution metric (with value extraction)
gcloud logging metrics create response_time_distribution \
  --description="Distribution of response times" \
  --log-filter='jsonPayload.response_time_ms>0' \
  --value-extractor='EXTRACT(jsonPayload.response_time_ms)' \
  --metric-kind=DELTA \
  --value-type=DISTRIBUTION \
  --bucket-options='exponential-buckets: {num-finite-buckets: 64, growth-factor: 2, scale: 1}'

# List metrics
gcloud logging metrics list

# View metric details
gcloud logging metrics describe failed_logins

# Update metric
gcloud logging metrics update failed_logins \
  --description="Updated description"
```

Via Console:
```
1. Cloud Logging > Logs-based Metrics
2. Create Metric
3. Metric Type: Counter
4. Filter: jsonPayload.event_type="login_failed"
5. Name: failed_logins
6. Create
```

Use log-based metric in alert:
```yaml
# Alert when failed logins > 10 in 5 minutes
displayName: "Too Many Failed Logins"
conditions:
  - displayName: "Failed login threshold"
    conditionThreshold:
      filter: 'metric.type="logging.googleapis.com/user/failed_logins"'
      comparison: COMPARISON_GT
      thresholdValue: 10
      duration: 300s
```

Application logging (Python example):
```python
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log structured data for easy filtering
def log_failed_login(username, ip_address):
    logger.warning(json.dumps({
        "event_type": "login_failed",
        "username": username,
        "ip_address": ip_address,
        "timestamp": datetime.now().isoformat()
    }))

# This log entry will be counted by the log-based metric
log_failed_login("user123", "203.0.113.50")
```

- Option B is incorrect because:
  - Requires custom code and maintenance
  - More complex than log-based metrics
  - Log-based metrics are the native solution

- Option C is incorrect because:
  - Export to BigQuery is for analysis, not real-time metrics
  - No automatic metric creation
  - Cannot create alerts directly

- Option D is incorrect because:
  - Manual data entry is not automated
  - Not scalable
  - Prone to errors

**Log-based Metric Types:**
- **Counter**: Count log entries (e.g., error count)
- **Distribution**: Statistical distribution of values
- **Custom with labels**: Group by extracted fields

---

## Question 5
You need to check if your website is accessible from different locations globally. What Cloud Monitoring feature should you use?

**A)** Alert policies

**B)** Uptime checks

**C)** Service monitoring

**D)** Log-based metrics

**Correct Answer:** B

**Explanation:**
- Option B is correct because:
  - Uptime checks monitor endpoint availability from multiple locations
  - HTTP/HTTPS support
  - Global monitoring points
  - Automatic alerts on downtime
  - Latency measurements

Create uptime check:
```bash
# Create HTTP uptime check
gcloud monitoring uptime create web-check \
  --display-name="Website Uptime" \
  --resource-type=uptime-url \
  --host=www.example.com \ --path=/ \
  --port=443 \
  --protocol=HTTPS \
  --timeout=10s \
  --period=60s

# List uptime checks
gcloud monitoring uptime list

# View uptime check details
gcloud monitoring uptime describe web-check
```

Via Console:
```
1. Cloud Monitoring > Uptime checks
2. Create Uptime Check
3. Protocol: HTTPS
4. Resource Type: URL
5. Hostname: www.example.com
6. Path: /
7. Check frequency: 1 minute
8. Regions: Multiple locations (US, Europe, Asia)
9. Alert (optional): Email on failure
10. Create
```

Advanced uptime check:
```yaml
displayName: "API Health Check"
monitoredResource:
  type: uptime_url
  labels:
    host: api.example.com
    project_id: my-project
httpCheck:
  path: /health
  port: 443
  useSsl: true
  requestMethod: GET
  validateSsl: true
  headers:
    User-Agent: GoogleStackdriverMonitoring
period: 60s
timeout: 10s
selectedRegions:
  - USA
  - EUROPE
  - ASIA_PACIFIC
contentMatchers:
  - content: "\"status\":\"healthy\""
    matcher: CONTAINS_STRING
```

Uptime check with authentication:
```bash
# Create uptime check with custom headers
gcloud monitoring uptime create api-check \
  --display-name="API Uptime" \
  --resource-type=uptime-url \
  --host=api.example.com \
  --path=/v1/status \
  --port=443 \
  --protocol=HTTPS \
  --custom-headers='{"Authorization":"Bearer TOKEN"}'
```

Alert on uptime check failure:
```yaml
displayName: "Website Down Alert"
conditions:
  - displayName: "Uptime check failed"
    conditionThreshold:
      filter: 'metric.type="monitoring.googleapis.com/uptime_check/check_passed" AND metric.labels.check_id="web-check"'
      comparison: COMPARISON_GT
      thresholdValue: 1  # Alert if ANY check fails
      aggregations:
        - alignmentPeriod: 600s
          crossSeriesReducer: REDUCE_COUNT_FALSE
          perSeriesAligner: ALIGN_NEXT_OLDER
```

- Option A is incorrect because:
  - Alert policies notify on metric conditions
  - Don't perform actual uptime checking
  - Need uptime checks as the source

- Option C is incorrect because:
  - Service monitoring is for SLI/SLO tracking
  - Different purpose (reliability engineering)
  - Uptime checks are simpler for basic availability

- Option D is incorrect because:
  - Log-based metrics count log entries
  - Don't actively check endpoint availability
  - Different use case

**Uptime Check Capabilities:**
- Global monitoring (6 regions)
- HTTP/HTTPS/TCP protocols
- Custom headers and authentication
- Content validation (response body)
- SSL certificate validation
- Latency measurement

---

## Question 6
You need to install the Cloud Monitoring agent on a Compute Engine instance to collect memory and disk metrics. What should you do?

**A)** The agent is pre-installed; enable it via metadata

**B)** Install the Ops Agent using a startup script

**C)** Enable Cloud Monitoring API; agent installs automatically

**D)** Agents are not needed; metrics are collected automatically

**Correct Answer:** B

**Explanation:**
- Option B is correct because:
  - Ops Agent must be manually installed
  - Startup script ensures installation on boot
  - Collects advanced metrics (memory, disk, processes)
  - Recommended by Google (replaces legacy agents)

Install Ops Agent:
```bash
# SSH to instance and install
gcloud compute ssh my-instance --zone=us-central1-a

# On the instance:
curl -sSO https://dl.google.com/cloudagents/add-google-cloud-ops-agent-repo.sh
sudo bash add-google-cloud-ops-agent-repo.sh --also-install

# Verify installation
sudo systemctl status google-cloud-ops-agent

# Configure logging and monitoring
sudo nano /etc/google-cloud-ops-agent/config.yaml
```

Via startup script:
```bash
# Create instance with Ops Agent installation
gcloud compute instances create my-instance \
  --zone=us-central1-a \
  --metadata=startup-script='#! /bin/bash
    curl -sSO https://dl.google.com/cloudagents/add-google-cloud-ops-agent-repo.sh
    sudo bash add-google-cloud-ops-agent-repo.sh --also-install
  '
```

Ops Agent configuration (`/etc/google-cloud-ops-agent/config.yaml`):
```yaml
logging:
  receivers:
    syslog:
      type: files
      include_paths:
        - /var/log/syslog
        - /var/log/messages
  service:
    pipelines:
      default_pipeline:
        receivers: [syslog]

metrics:
  receivers:
    hostmetrics:
      type: hostmetrics
      collection_interval: 60s
  processors:
    metrics_filter:
      type: exclude_metrics
      metrics_pattern:
        - system.cpu.utilization
  service:
    pipelines:
      default_pipeline:
        receivers: [hostmetrics]
        processors: [metrics_filter]
```

Install on multiple instances:
```bash
# Create instance template with Ops Agent
gcloud compute instance-templates create ops-agent-template \
  --machine-type=n1-standard-1 \
  --metadata=startup-script='#! /bin/bash
    curl -sSO https://dl.google.com/cloudagents/add-google-cloud-ops-agent-repo.sh
    sudo bash add-google-cloud-ops-agent-repo.sh --also-install
  '

# Use in managed instance group
gcloud compute instance-groups managed create web-mig \
  --template=ops-agent-template \
  --size=3 \
  --zone=us-central1-a
```

- Option A is incorrect because:
  - Ops Agent is NOT pre-installed
  - Must be explicitly installed
  - No metadata flag to enable it

- Option C is incorrect because:
  - Enabling API doesn't install agents
  - Manual installation required
  - API is needed but doesn't trigger installation

- Option D is incorrect because:
  - Basic metrics (CPU, network) are automatic
  - Advanced metrics (memory, disk) require Ops Agent
  - Agent is necessary for complete monitoring

**Metrics Collected:**
- **Without Agent**: CPU, network, disk I/O
- **With Ops Agent**: Memory, disk usage, processes, custom application metrics

---

## Question 7
You need to export all audit logs to BigQuery for compliance analysis. What type of log sink should you create?

**A)** Log sink with filter for Admin Activity logs

**B)** Log sink with filter for Data Access logs

**C)** Log sink with filter for all audit logs (Admin Activity + Data Access)

**D)** Create separate sinks for each audit log type

**Correct Answer:** C

**Explanation:**
- Option C is correct because:
  - Compliance typically requires all audit logs
  - Admin Activity AND Data Access logs
  - Single sink can capture both
  - More efficient than multiple sinks

Create comprehensive audit log sink:
```bash
# Create BigQuery dataset
bq mk --dataset audit_logs

# Create log sink for all audit logs
gcloud logging sinks create audit-logs-sink \
  bigquery.googleapis.com/projects/PROJECT_ID/datasets/audit_logs \
  --log-filter='protoPayload.@type="type.googleapis.com/google.cloud.audit.AuditLog"'

# Grant BigQuery permissions
bq add-iam-policy-binding audit_logs \
  --member='serviceAccount:cloud-logs@system.gserviceaccount.com' \
  --role='roles/bigquery.dataEditor'

# Verify sink
gcloud logging sinks describe audit-logs-sink
```

Specific audit log filters:
```bash
# Admin Activity logs only
--log-filter='logName:"cloudaudit.googleapis.com%2Factivity"'

# Data Access logs only
--log-filter='logName:"cloudaudit.googleapis.com%2Fdata_access"'

# System Event logs
--log-filter='logName:"cloudaudit.googleapis.com%2Fsystem_event"'

# Policy Denied logs
--log-filter='logName:"cloudaudit.googleapis.com%2Fpolicy"'

# Specific service (e.g., Compute Engine)
--log-filter='protoPayload.serviceName="compute.googleapis.com" AND logName:"cloudaudit.googleapis.com"'

# IAM changes only
--log-filter='protoPayload.methodName="SetIamPolicy"'
```

Query audit logs in BigQuery:
```sql
-- Count IAM changes by user
SELECT
  protopayload_auditlog.authenticationInfo.principalEmail as user,
  COUNT(*) as iam_changes
FROM `PROJECT_ID.audit_logs.cloudaudit_googleapis_com_activity_*`
WHERE protopayload_auditlog.methodName = "SetIamPolicy"
  AND _TABLE_SUFFIX BETWEEN '20240101' AND '20240131'
GROUP BY user
ORDER BY iam_changes DESC

-- Failed authentication attempts
SELECT
  timestamp,
  protopayload_auditlog.authenticationInfo.principalEmail,
  protopayload_auditlog.methodName,
  protopayload_auditlog.status.message
FROM `PROJECT_ID.audit_logs.cloudaudit_googleapis_com_activity_*`
WHERE protopayload_auditlog.status.code != 0
  AND _TABLE_SUFFIX = FORMAT_DATE('%Y%m%d', CURRENT_DATE())
```

- Option A is incorrect because:
  - Admin Activity logs are only part of audit logs
  - Missing Data Access logs
  - Incomplete for compliance

- Option B is incorrect because:
  - Data Access logs only (missing Admin Activity)
  - Incomplete audit trail

- Option D is incorrect because:
  - Single sink can handle all audit logs
  - Multiple sinks add complexity
  - Not necessary

**Audit Log Types:**
- **Admin Activity**: Resource modifications (always enabled, free)
- **Data Access**: Data reads/writes (must enable, charges apply)
- **System Event**: Google system actions
- **Policy Denied**: Permission denied events

---

## Question 8
Your Cloud Monitoring dashboard shows high latency, but you need to correlate it with application logs. What should you do?

**A)** Use Cloud Trace to view distributed traces

**B)** Use Logs Explorer with metric time range filter

**C)** Export metrics to BigQuery and join with logs

**D)** Create a log-based metric for latency

**Correct Answer:** A (for distributed tracing) or B (for log correlation)

**Explanation:**
For the specific requirement of correlating latency with logs:

- Option A is best for understanding latency:
  - Cloud Trace shows end-to-end request latency
  - Distributed tracing across services
  - Can link to logs for specific requests
  - Visual representation of request flow

Enable Cloud Trace:
```python
# Python example with Cloud Trace
from google.cloud import trace_v1
from opencensus.ext.stackdriver import trace_exporter
from opencensus.trace import tracer as tracer_module

# Configure exporter
exporter = trace_exporter.StackdriverExporter(
    project_id="my-project"
)
tracer = tracer_module.Tracer(exporter=exporter)

# Trace a function
with tracer.span(name='process_request'):
    # Your application code
    process_request()
    
    # Log with trace context
    import logging
    import json_logging
    
    logger = logging.getLogger()
    logger.info("Processing completed", extra={
        "trace_id": tracer.span_context.trace_id
    })
```

- Option B is also practical:
  - View logs during high latency period
  - Time-based correlation in Logs Explorer
  - Filter logs by timestamp when latency spiked

Correlate logs with metrics:
```bash
# View logs during specific time range (when latency was high)
gcloud logging read \
  'resource.type="cloud_run_revision" AND
   severity>=WARNING AND
   timestamp>="2024-01-20T14:30:00Z" AND
   timestamp<="2024-01-20T14:35:00Z"' \
  --format=json

# In Logs Explorer, use time picker to match metric spike
```

- Option C is incorrect because:
  - Too complex for simple correlation
  - Real-time correlation is lost
  - Cloud Trace and Logs Explorer are simpler

- Option D is incorrect because:
  - Log-based latency metric is possible but doesn't correlateexisting latency metrics with logs
  - Doesn't help with correlation

**Observability Tools:**
- **Cloud Monitoring**: Metrics (CPU, latency, errors)
- **Cloud Logging**: Application and system logs
- **Cloud Trace**: Distributed tracing
- **Cloud Profiler**: CPU/Memory profiling

---

## Question 9
You need to aggregate logs from multiple projects into a single location for centralized analysis. What should you do?

**A)** Create a log sink in each project pointing to a central project's Cloud Storage bucket

**B)** Manually copy logs from each project daily

**C)** Use a single GCP project for all resources

**D)** Create organization-level log sink

**Correct Answer:** D (best) or A (also works)

**Explanation:**
- Option D is best (if you have an organization):
  - Organization-level sink aggregates all project logs
  - Single configuration for all projects
  - Automatic inclusion of new projects
  - Centralized compliance and security

Create organization-level sink:
```bash
# Create organization log sink
gcloud logging sinks create org-audit-sink \
  bigquery.googleapis.com/projects/central-logging-project/datasets/all_logs \
  --organization=ORGANIZATION_ID \
  --include-children \
  --log-filter='logName:"cloudaudit.googleapis.com"'

# Grant permissions (get service account from sink creation output)
bq add-iam-policy-binding all_logs \
  --member='serviceAccount:o123456789-987654@gcp-sa-logging.iam.gserviceaccount.com' \
  --role='roles/bigquery.dataEditor'
```

- Option A also works (project-level approach): 
  - Create log sink in each project
  - All point to same destination
  - More management overhead

Per-project sinks to central location:
```bash
# In each project, create sink to central bucket
gcloud logging sinks create project-logs \
  storage.googleapis.com/central-logs-bucket \
  --project=project-1 \
  --log-filter='resource.type!="audited_resource"'

gcloud logging sinks create project-logs \
  storage.googleapis.com/central-logs-bucket \
  --project=project-2 \
  --log-filter='resource.type!="audited_resource"'

# Grant write permission to bucket (from each project's log service account)
gsutil iam ch serviceAccount:cloud-logs@system.gserviceaccount.com:roles/storage.objectCreator \
  gs://central-logs-bucket
```

- Option B is incorrect because:
  - Manual process is not scalable
  - Risk of data loss
  - Operational overhead

- Option C is incorrect because:
  - Single project doesn't scale
  - Poor organization and isolation
  - Not best practice for multi-team environments

**Log Aggregation Strategies:**
1. **Organization-level sink**: Best for organizations
2. **Folder-level sink**: For specific business units
3. **Project-level sinks**: Manual but flexible
4. **Aggregated logging bucket**: New feature for multi-project logs

---

## Question 10
You need to create a Service Level Objective (SLO) to ensure your API has 99.9% availability. What should you use?

**A)** Create an alert policy for uptime check failures

**B)** Create a custom SLO in Cloud Monitoring

**C)** Use log-based metrics to calculate availability

**D)** Monitor manually and track in a spreadsheet

**Correct Answer:** B

**Explanation:**
- Option B is correct because:
  - Cloud Monitoring has native SLO support
  - Tracks compliance against SLO targets
  - Alert on burn rate
  - Error budget tracking
  - Industry-standard SLI/SLO framework

Create SLO:
```yaml
# Via Console: Cloud Monitoring > Services > Create SLO
# 1. Select service (or create custom service)
# 2. Define SLI type:
#    - Availability (request-based or windows-based)
#    - Latency (percentage of requests below threshold)
# 3. Set SLO target: 99.9%
# 4. Compliance period: 30 days

# Example SLO configuration
displayName: "API Availability SLO"
serviceLevelIndicator:
  requestBased:
    goodTotalRatio:
      goodServiceFilter: |
        metric.type="serviceruntime.googleapis.com/api/request_count"
        resource.type="api"
        metric.labels.response_code!="5xx"
      totalServiceFilter: |
        metric.type="serviceruntime.googleapis.com/api/request_count"
        resource.type="api"
goal: 0.999  # 99.9%
rollingPeriodDays: 30
```

Create alerting on SLO burn rate:
```yaml
# Alert when error budget is burning too fast
displayName: "SLO Burn Rate Alert"
conditions:
  - displayName: "Fast burn rate"
    conditionThreshold:
      filter: |
        select_slo_burn_rate("projects/my-project/services/my-api/serviceLevelObjectives/availability-slo", 3600s)
      comparison: COMPARISON_GT
      thresholdValue: 10  # 10x burn rate
notificationChannels: ["projects/my-project/notificationChannels/email-ops"]
```

Query SLO compliance:
```bash
# View SLO status
gcloud monitoring services list

#Describe SLO
gcloud monitoring services slos describe availability-slo \
  --service=my-api
```

- Option A is incorrect because:
  - Alert policies notify on issues but don't track SLOs
  - No error budget concept
  - Not designed for SLO tracking

- Option C is incorrect because:
  - Log-based metrics can calculate availability
  - But Cloud Monitoring SLO is the native solution
  - More manual work

- Option D is incorrect because:
  - Manual tracking is not scalable
  - No automation or alerting
  - Spreadsheets are error-prone

**SLO Components:**
- **SLI (Service Level Indicator)**: Measurement (e.g., % of successful requests)
- **SLO (Service Level Objective)**: Target (e.g., 99.9% availability)
- **Error Budget**: Allowed failures (100% - SLO = 0.1%)
- **Burn Rate**: Rate at which error budget is consumed
