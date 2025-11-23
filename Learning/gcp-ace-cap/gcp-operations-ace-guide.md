# Google Cloud Certified Associate Cloud Engineer (ACE) - Operations Deep Dive

## 1. Cloud Logging (The Central Nervous System)

### 1.1 Advanced Log Queries
The Log Explorer uses a specific query language. You **must** know how to filter effectively.
*   **Basic Filter**: `resource.type="gce_instance" AND severity="ERROR"`
*   **JSON Payload**: `jsonPayload.status_code >= 500`
*   **Substring**: `textPayload:"Connection refused"` (Case-insensitive search).
*   **Regex**: `textPayload =~ "^Error.*[0-9]+$"`

### 1.2 Audit Logs (Exam Critical)
Not all logs are created equal.
1.  **Admin Activity Logs**:
    *   **What**: "Who changed the configuration?" (e.g., `v1.compute.instances.delete`).
    *   **Cost**: **Free**.
    *   **Retention**: 400 days.
    *   **Default**: **Always On**.
2.  **Data Access Logs**:
    *   **What**: "Who read the data?" (e.g., `s3.objects.get`).
    *   **Cost**: **Paid** (High volume).
    *   **Retention**: 30 days.
    *   **Default**: **Off** (except for BigQuery). You must enable them explicitly.

### 1.3 Log-Based Metrics
*   **Scenario**: You want to alert when your app logs "Payment Failed". There is no CPU metric for this.
*   **Solution**: Create a **Counter Metric** based on the log filter `textPayload="Payment Failed"`.
*   **Result**: Now you have a metric `logging/user/payment_failed_count` that you can graph and alert on.

### 1.4 Log Sinks (Exporting)
*   **Aggregated Sinks**: Export logs from an entire Organization or Folder to a central project.
*   **Destinations**:
    *   **BigQuery**: For SQL analysis ("How many errors last month?").
    *   **Pub/Sub**: For Splunk/Datadog integration.
    *   **Cloud Storage**: For long-term compliance (cheapest).

## 2. Cloud Monitoring (Observability)

### 2.1 Metric Kinds & Types
*   **Gauge**: A value at a point in time (e.g., CPU Temperature, Queue Depth). Can go up or down.
*   **Delta**: The change over a time interval (e.g., Request Count per minute).
*   **Cumulative**: A value that strictly increases (e.g., Total Bytes Sent since startup).

### 2.2 Alerting Policies
*   **Resource Grouping**: **Never** alert on a specific Instance ID (VMs are ephemeral). Alert on the **Instance Group** or **Service**.
*   **MQL (Monitoring Query Language)**: Powerful text-based query language for complex math (e.g., "Rate of 500 errors / Rate of Total Requests > 1%").
*   **Notification Channels**:
    *   Email/SMS (Basic).
    *   PagerDuty/Slack (Ops teams).
    *   **Pub/Sub** (Auto-remediation - e.g., trigger a Cloud Function to restart the server).

### 2.3 Uptime Checks
*   **Public**: Google probes your URL from around the world.
    *   **Firewall**: You must whitelist Google's Uptime Check IP ranges.
*   **Private**: Probes internal IPs (RFC 1918).
    *   **Requirement**: Uses a "Private Uptime Check" agent.

## 3. Application Performance Management (APM)

### 3.1 Cloud Trace
*   **Purpose**: Latency analysis.
*   **Visualization**: Waterfall chart showing how long each microservice took.
*   **Header**: Propagates the `X-Cloud-Trace-Context` header across HTTP calls to link spans.

### 3.2 Cloud Profiler
*   **Purpose**: Resource usage analysis (CPU/RAM).
*   **Visualization**: Flame Graph.
*   **Use Case**: "Why is my function using 2GB of RAM?" (Finds memory leaks).
*   **Overhead**: Low impact (runs statistically on a subset of requests).

### 3.3 Error Reporting
*   **Purpose**: Aggregates crash logs.
*   **Feature**: Groups similar stack traces (e.g., "NullPointerException at line 50" happened 1000 times).

---

## 4. Cloud Logging Deep Dive

### 4.1 Log Router Architecture

```
┌──────────────────────────────────────────────────────────┐
│                  LOG ROUTER FLOW                          │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  Services → Logs → Log Router → Sinks → Destinations     │
│                         │                                 │
│                         ├─► _Required sink (400 days)    │
│                         ├─► _Default sink (30 days)      │
│                         └─► Custom sinks                  │
└──────────────────────────────────────────────────────────┘
```

### 4.2 Creating Custom Sinks

```bash
# Export ERROR logs to BigQuery
gcloud logging sinks create error-sink \
    bigquery.googleapis.com/projects/my-project/datasets/logs_dataset \
    --log-filter='severity >= ERROR'

# Export audit logs to Cloud Storage
gcloud logging sinks create audit-sink \
    storage.googleapis.com/audit-logs-bucket \
    --log-filter='logName:"cloudaudit.googleapis.com"'

# Export application logs to Pub/Sub
gcloud logging sinks create app-logs-sink \
    pubsub.googleapis.com/projects/my-project/topics/app-logs \
    --log-filter='resource.type="gce_instance" AND labels.app="backend"'
```

### 4.3 Advanced Log Filtering

```bash
# Filter by specific VM instance
resource.type="gce_instance" AND resource.labels.instance_id="1234567890"

# Filter HTTP 5xx errors from Load Balancer
resource.type="http_load_balancer" AND httpRequest.status >= 500

# Filter by custom log entry
jsonPayload.user_id="user-123" AND jsonPayload.action="purchase"

# Time range filter
timestamp >= "2024-01-15T00:00:00Z" AND timestamp < "2024-01-16T00:00:00Z"

# Combine multiple conditions
resource.type="cloud_function" AND
severity >= WARNING AND
NOT textPayload:"expected error"
```

### 4.4 Structured Logging Best Practices

```python
# Python example with structured logging
import logging
import json
from google.cloud import logging as cloud_logging

# Setup Cloud Logging
logging_client = cloud_logging.Client()
logging_client.setup_logging()

# Use structured logging
def process_order(order_id, user_id, amount):
    logging.info(json.dumps({
        "message": "Processing order",
        "order_id": order_id,
        "user_id": user_id,
        "amount": amount,
        "event_type": "order_processing"
    }))
    
    try:
        # Process order
        result = complete_order(order_id)
        
        logging.info(json.dumps({
            "message": "Order completed",
            "order_id": order_id,
            "result": result,
            "event_type": "order_completed"
        }))
    except Exception as e:
        logging.error(json.dumps({
            "message": "Order failed",
            "order_id": order_id,
            "error": str(e),
            "event_type": "order_failed"
        }))
        raise

# Query structured logs
# jsonPayload.event_type="order_failed" AND jsonPayload.order_id="ORD-123"
```

### 4.5 Log-Based Metrics

```bash
# Create counter metric for failed payments
gcloud logging metrics create payment_failures \
    --description="Count of payment failures" \
    --log-filter='jsonPayload.event_type="payment_failed"'

# Create distribution metric for request latency
gcloud logging metrics create request_latency \
    --description="Request latency distribution" \
    --value-extractor='EXTRACT(jsonPayload.latency_ms)' \
    --metric-kind=DELTA \
    --value-type=DISTRIBUTION

# List metrics
gcloud logging metrics list

# View metric data
gcloud logging metrics describe payment_failures
```

---

## 5. Cloud Monitoring Advanced

### 5.1 Creating Dashboards

```bash
# Create dashboard via gcloud (JSON config)
cat > dashboard.json << 'EOF'
{
  "displayName": "Application Performance Dashboard",
  "mosaicLayout": {
    "columns": 12,
    "tiles": [
      {
        "width": 6,
        "height": 4,
        "widget": {
          "title": "CPU Utilization",
          "xyChart": {
            "dataSets": [{
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "resource.type=\"gce_instance\" metric.type=\"compute.googleapis.com/instance/cpu/utilization\"",
                  "aggregation": {
                    "alignmentPeriod": "60s",
                    "perSeriesAligner": "ALIGN_MEAN"
                  }
                }
              }
            }]
          }
        }
      }
    ]
  }
}
EOF

gcloud monitoring dashboards create --config-from-file=dashboard.json
```

### 5.2 Alert Policy Configuration

```bash
# Create alert for high CPU
cat > cpu-alert.json << 'EOF'
{
  "displayName": "High CPU Alert",
  "conditions": [{
    "displayName": "CPU > 80%",
    "conditionThreshold": {
      "filter": "resource.type=\"gce_instance\" AND metric.type=\"compute.googleapis.com/instance/cpu/utilization\"",
      "comparison": "COMPARISON_GT",
      "thresholdValue": 0.8,
      "duration": "300s",
      "aggregations": [{
        "alignmentPeriod": "60s",
        "perSeriesAligner": "ALIGN_MEAN"
      }]
    }
  }],
  "alertStrategy": {
    "autoClose": "1800s"
  },
  "notificationChannels": ["projects/my-project/notificationChannels/CHANNEL_ID"],
  "enabled": true
}
EOF

gcloud alpha monitoring policies create --policy-from-file=cpu-alert.json
```

### 5.3 Multi-Condition Alerts

```bash
# Alert if BOTH CPU > 80% AND Memory > 90%
cat > multi-condition-alert.json << 'EOF'
{
  "displayName": "Resource Exhaustion Alert",
  "combiner": "AND",
  "conditions": [
    {
      "displayName": "CPU > 80%",
      "conditionThreshold": {
        "filter": "metric.type=\"compute.googleapis.com/instance/cpu/utilization\"",
        "comparison": "COMPARISON_GT",
        "thresholdValue": 0.8,
        "duration": "300s"
      }
    },
    {
      "displayName": "Memory > 90%",
      "conditionThreshold": {
        "filter": "metric.type=\"agent.googleapis.com/memory/percent_used\"",
        "comparison": "COMPARISON_GT",
        "thresholdValue": 90,
        "duration": "300s"
      }
    }
  ],
  "notificationChannels": ["projects/my-project/notificationChannels/CHANNEL_ID"]
}
EOF
```

### 5.4 MQL (Monitoring Query Language) Examples

```python
# Error rate percentage
fetch gce_instance
| metric 'compute.googleapis.com/instance/network/received_packets_count'
| group_by 1m, [value_received_packets_count_mean: mean(value.received_packets_count)]
| every 1m

# HTTP 5xx error rate
fetch k8s_container
| metric 'custom.googleapis.com/http_requests'
| filter metric.status_code >= 500
| group_by 1m, [error_count: sum(value.http_requests)]
| ratio_by 1m, [total_count: sum(value.http_requests)]
```

---

## 6. Cloud Trace

### 6.1 Enabling Trace in Applications

```python
# Python Flask with Cloud Trace
from flask import Flask
from google.cloud import trace_v1
import google.cloud.trace_v1.gapic.trace_service_client as trace_service

app = Flask(__name__)
tracer = trace_v1.TraceServiceClient()

@app.route('/api/order')
def create_order():
    # Start a trace span
    with tracer.span(name='create_order'):
        # Call database
        with tracer.span(name='db_query'):
            user = get_user_from_db()
        
        # Call external API
        with tracer.span(name='payment_api'):
            payment_result = charge_payment()
        
        # Complete order
        with tracer.span(name='complete_order'):
            order = save_order(user, payment_result)
    
    return {"order_id": order.id}
```

### 6.2 Viewing Traces

```bash
# List traces
gcloud trace list --filter="2024-01-15T00:00:00Z" --limit=10

# Get specific trace
gcloud trace describe TRACE_ID

# Analyze trace latency
# In Cloud Console: Trace → Trace List → Analysis Reports
# - Latency distribution
# - Request density
# - Most time-consuming operations
```

---

## 7. Cloud Profiler

### 7.1 Enabling Profiler

```python
# Python application
import googlecloudprofiler

try:
    googlecloudprofiler.start(
        service='backend-service',
        service_version='1.0.0',
        verbose=3
    )
except Exception as e:
    print(f"Failed to start profiler: {e}")
```

```go
// Go application
import (
    "cloud.google.com/go/profiler"
)

func main() {
    if err := profiler.Start(profiler.Config{
        Service:        "backend-service",
        ServiceVersion: "1.0.0",
    }); err != nil {
        log.Fatalf("Failed to start profiler: %v", err)
    }
    
    // Your application code
}
```

### 7.2 Analyzing Profiles

```
Profile Types:
- CPU Time: Where is CPU being spent?
- Heap Memory: Which objects are using memory?
- Allocated Memory: Where are allocations happening?
- Contention: Where are threads waiting?

Example Analysis:
1. Select service: backend-service
2. Select profile type: CPU Time
3. Time range: Last 1 hour
4. Result: Flame graph showing function call hierarchy
   - 60% in database queries
   - 25% in JSON serialization
   - 15% in business logic
```

---

## 8. Error Reporting

### 8.1 Integration

```python
# Python with Error Reporting
from google.cloud import error_reporting

error_client = error_reporting.Client()

try:
    risky_operation()
except Exception as e:
    error_client.report_exception()
    # Also log to Cloud Logging
    logging.error(f"Operation failed: {e}")
    raise
```

### 8.2 Grouping and Notifications

```bash
# View error groups
gcloud beta error-reporting events list \
    --service=backend-service \
    --time-range=1d

# Error groups are automatically created based on:
# - Exception type
# - Stack trace similarity
# - Error message pattern

# Configure notifications
# Console → Error Reporting → Settings
# - Email notifications for new errors
# - Daily error summary
```

---

## 9. Uptime Checks

### 9.1 Creating Uptime Checks

```bash
# Create HTTP uptime check
gcloud monitoring uptime-checks create my-app-check \
    --display-name="My App Uptime" \
    --resource-type=uptime-url \
    --host=myapp.example.com \
    --path=/health \
    --period=60 \
    --timeout=10s

# Create with authentication
gcloud monitoring uptime-checks create authenticated-check \
    --display-name="Authenticated API Check" \
    --resource-type=uptime-url \
    --host=api.example.com \
    --path=/v1/status \
    --custom-headers="Authorization: Bearer TOKEN"
```

### 9.2 Alert on Uptime Check Failures

```bash
# Create alert policy for uptime check
cat > uptime-alert.json << 'EOF'
{
  "displayName": "App Down Alert",
  "conditions": [{
    "displayName": "Uptime check failed",
    "conditionThreshold": {
      "filter": "metric.type=\"monitoring.googleapis.com/uptime_check/check_passed\" AND resource.type=\"uptime_url\"",
      "comparison": "COMPARISON_LT",
      "thresholdValue": 1,
      "duration": "60s",
      "aggregations": [{
        "alignmentPeriod": "60s",
        "perSeriesAligner": "ALIGN_FRACTION_TRUE"
      }]
    }
  }],
  "notificationChannels": ["projects/my-project/notificationChannels/CHANNEL_ID"]
}
EOF

gcloud alpha monitoring policies create --policy-from-file=uptime-alert.json
```

---

## 10. Cloud Debugger

### 10.1 Setting Snapshots

```bash
# Enable Cloud Debugger in code
# Python
import googleclouddebugger
googleclouddebugger.enable(breakpoint_enable_canary=True)

# Java (add agent to JVM args)
# -agentpath:/opt/cdbg/cdbg_java_agent.so
```

```
Using Cloud Debugger:
1. Open Cloud Console → Debugger
2. Select service and version
3. Open source file
4. Click line number to set snapshot
5. Condition (optional): user_id == "123"
6. When code reaches that line:
   - Captures local variables
   - Call stack
   - Logs without stopping execution
```

---

## 11. Service Monitoring

### 11.1 Creating SLIs

```bash
# Define SLI: Request latency < 500ms
cat > sli-latency.json << 'EOF'
{
  "displayName": "Request Latency SLI",
  "serviceLevelIndicator": {
    "requestBased": {
      "goodTotalRatio": {
        "goodServiceFilter": "metric.type=\"loadbalancing.googleapis.com/https/request_count\" AND metric.latency < 500",
        "totalServiceFilter": "metric.type=\"loadbalancing.googleapis.com/https/request_count\""
      }
    }
  }
}
EOF
```

### 11.2 Defining SLOs

```bash
# SLO: 99% of requests complete in < 500ms
cat > slo.json << 'EOF'
{
  "displayName": "Latency SLO",
  "goal": 0.99,
  "rollingPeriod": "2592000s",  # 30 days
  "serviceLevelIndicator": {
    "requestBased": {
      "goodTotalRatio": {
        "goodServiceFilter": "metric.type=\"loadbalancing.googleapis.com/https/request_count\" AND metric.latency < 500",
        "totalServiceFilter": "metric.type=\"loadbalancing.googleapis.com/https/request_count\""
      }
    }
  }
}
EOF

gcloud alpha monitoring slos create --config-from-file=slo.json --service=SERVICE_ID
```

---

## 12. Integration with Third-Party Tools

### 12.1 Export to Splunk

```bash
# Create Pub/Sub topic
gcloud pubsub topics create logs-to-splunk

# Create log sink
gcloud logging sinks create splunk-sink \
    pubsub.googleapis.com/projects/my-project/topics/logs-to-splunk \
    --log-filter='resource.type="gce_instance"'

# Configure Splunk Add-on for Google Cloud Platform
# - Subscribe to logs-to-splunk topic
# - Parse JSON log entries
```

### 12.2 Export to Datadog

```bash
# Install Datadog agent on VMs
curl -L https://raw.githubusercontent.com/DataDog/dd-agent/master/packaging/datadog-agent/source/install_agent.sh | DD_API_KEY=YOUR_KEY bash

# Configure Ops Agent for metrics collection
sudo systemctl enable google-cloud-ops-agent
sudo systemctl start google-cloud-ops-agent

# Datadog automatically collects Cloud Monitoring metrics
```

---

## 13. Cost Optimization for Operations

### 13.1 Log Ingestion Costs

```
Pricing:
- First 50 GiB/month: Free
- Beyond 50 GiB: $0.50 per GiB

Example:
- Application generates 200 GiB logs/month
- Cost: (200 - 50) × $0.50 = $75/month
```

### 13.2 Cost Reduction Strategies

```bash
# 1. Exclude unnecessary logs
gcloud logging sinks create _Default \
    logging.googleapis.com/projects/my-project/locations/global/buckets/_Default \
    --log-filter='NOT resource.type="gce_instance" OR severity >= WARNING'

# 2. Set log retention
gcloud logging buckets update _Default \
    --location=global \
    --retention-days=7

# 3. Sample high-volume logs
gcloud logging sinks create sampled-logs \
    bigquery.googleapis.com/projects/my-project/datasets/logs \
    --log-filter='resource.type="cloud_function" AND sample(insertId, 0.1)'  # 10% sample

# 4. Export to Cloud Storage for long-term retention (cheaper)
gcloud logging sinks create archive-sink \
    storage.googleapis.com/archive-logs-bucket \
    --log-filter='timestamp < "2023-01-01T00:00:00Z"'
```

---

## 14. Troubleshooting Common Issues

### Issue 1: Logs Not Appearing

```bash
# Check service account permissions
gcloud projects get-iam-policy PROJECT_ID \
    --flatten="bindings[].members" \
    --filter="bindings.members:serviceAccount:SERVICE_ACCOUNT"

# Required role: roles/logging.logWriter

# Verify logging enabled
gcloud services list --enabled | grep logging

# Check log router
gcloud logging sinks list
```

### Issue 2: Alerts Not Firing

```bash
# Check alert policy status
gcloud alpha monitoring policies list

# Verify notification channels
gcloud alpha monitoring channels list

# Test notification channel
gcloud alpha monitoring channels verify CHANNEL_ID

# Check alert history
# Console → Monitoring → Alerting → Policies → View Incidents
```

### Issue 3: High Logging Costs

```bash
# Identify top log sources
# Run in BigQuery (if logs exported):
SELECT
  resource.type,
  COUNT(*) as log_count,
  SUM(LENGTH(textPayload)) / 1024 / 1024 as size_mb
FROM `project.dataset.cloudaudit_googleapis_com_activity_*`
WHERE _TABLE_SUFFIX BETWEEN '20240101' AND '20240131'
GROUP BY resource.type
ORDER BY size_mb DESC
LIMIT 10;

# Exclude verbose logs
gcloud logging exclusions create exclude-debug-logs \
    --log-filter='severity < WARNING'
```

---

## 15. ACE Exam Tips

### Key Concepts

1. **Audit logs**: Admin Activity (free, always on), Data Access (paid, opt-in)
2. **Log retention**: _Required (400 days), _Default (30 days)
3. **Log sinks**: Export to BigQuery (analysis), Pub/Sub (SIEM), GCS (archive)
4. **Metrics**: Gauge (point-in-time), Delta (change), Cumulative (increasing)
5. **Alerting**: Alert on groups/services, not individual instances
6. **Trace**: Latency analysis, requires header propagation
7. **Profiler**: CPU/memory profiling, flame graphs
8. **Uptime checks**: Public (whitelist IPs), Private (needs agent)
9. **Error Reporting**: Groups similar errors automatically
10. **SLI/SLO**: Service Level Indicator + Objective for reliability

### Common Commands

```bash
# View logs
gcloud logging read "resource.type=gce_instance" --limit=10

# Create sink
gcloud logging sinks create SINK_NAME DESTINATION --log-filter='FILTER'

# Create metric
gcloud logging metrics create METRIC_NAME --log-filter='FILTER'

# Create alert
gcloud alpha monitoring policies create --policy-from-file=policy.json

# Create uptime check
gcloud monitoring uptime-checks create CHECK_NAME \
    --resource-type=uptime-url \
    --host=HOSTNAME \
    --path=PATH
```

### Decision Matrix

| Scenario | Solution |
|----------|----------|
| **Store logs 1+ year** | Export to Cloud Storage |
| **Analyze logs with SQL** | Export to BigQuery |
| **Send logs to Splunk** | Export to Pub/Sub |
| **Alert on log pattern** | Create log-based metric + alert policy |
| **Find slow API calls** | Cloud Trace |
| **Find memory leaks** | Cloud Profiler |
| **Group crash reports** | Error Reporting |
| **Monitor website uptime** | Uptime Checks |

### Best Practices

1. **Use structured logging** (JSON) for better querying
2. **Set appropriate log retention** (balance cost vs compliance)
3. **Export audit logs** to separate project for security
4. **Create log-based metrics** for business KPIs
5. **Alert on SLOs**, not individual metrics
6. **Use MQL** for complex alert conditions
7. **Enable Error Reporting** for production apps
8. **Profile production** traffic (low overhead)
9. **Trace distributed** requests across services
10. **Monitor from outside** your network (Uptime Checks)

---

**End of Operations ACE Guide**
