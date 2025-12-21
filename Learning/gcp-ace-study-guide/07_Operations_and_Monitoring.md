# 07. Operations and Monitoring (Masterclass Edition)

Maintaining a cloud solution isn't just about logs; it's about observing the health of the system and reacting before users notice a failure.

---

## 7.1 Cloud Monitoring (Observability)

### 7.1.1 Google Cloud Operations Suite Components

| Service | Purpose | Data Type |
|---------|---------|-----------|
| **Cloud Monitoring** | Metrics, dashboards, alerts | Time-series metrics |
| **Cloud Logging** | Centralized log management | Log entries |
| **Cloud Trace** | Distributed tracing | Request traces |
| **Cloud Profiler** | Continuous profiling | CPU/Memory profiles |
| **Error Reporting** | Error aggregation | Exceptions/crashes |

### 7.1.2 Metrics Collection

| Source | Collection Method | Built-in Metrics |
|--------|-------------------|------------------|
| **Compute Engine** | Ops Agent | CPU, disk (basic without agent) |
| **GKE** | Managed Prometheus | Pod, node, container |
| **Cloud Run** | Native | Requests, latency, CPU |
| **Cloud SQL** | Native | Queries, connections, replication |
| **Custom Apps** | OpenTelemetry / Client Library | Your metrics |

```bash
# Install Ops Agent on VM
curl -sSO https://dl.google.com/cloudagents/add-google-cloud-ops-agent-repo.sh
sudo bash add-google-cloud-ops-agent-repo.sh --also-install

# Check agent status
sudo systemctl status google-cloud-ops-agent

# Agent configuration (/etc/google-cloud-ops-agent/config.yaml)
```

```yaml
# /etc/google-cloud-ops-agent/config.yaml
logging:
  receivers:
    myapp_logs:
      type: files
      include_paths:
        - /var/log/myapp/*.log
  service:
    pipelines:
      default_pipeline:
        receivers: [myapp_logs]

metrics:
  receivers:
    hostmetrics:
      type: hostmetrics
      collection_interval: 60s
  processors:
    metrics_filter:
      type: exclude_metrics
      metrics_pattern:
        - agent.googleapis.com/agent/*
  service:
    pipelines:
      default_pipeline:
        receivers: [hostmetrics]
        processors: [metrics_filter]
```

### 7.1.3 Alerting Policies

| Alert Type | Use Case | Example |
|------------|----------|---------|
| **Metric Threshold** | Resource limits | CPU > 80% for 5 min |
| **Metric Absence** | Heartbeat/batch jobs | No logs in 1 hour |
| **Log-based** | Error patterns | "ERROR" in logs |
| **Uptime Check** | External monitoring | HTTP 200 response |
| **Forecasted** | Predictive | Disk full in 24 hours |

```bash
# Create alerting policy via gcloud
gcloud alpha monitoring policies create \
    --display-name="High CPU Alert" \
    --condition-display-name="CPU > 80%" \
    --condition-filter='resource.type="gce_instance" AND metric.type="compute.googleapis.com/instance/cpu/utilization"' \
    --condition-threshold-value=0.8 \
    --condition-threshold-comparison=COMPARISON_GT \
    --condition-threshold-duration=300s \
    --notification-channels=projects/my-project/notificationChannels/1234567

# Create uptime check
gcloud monitoring uptime-check-configs create my-uptime-check \
    --display-name="Website Health" \
    --monitored-resource-type=uptime-url \
    --resource-labels=host=www.example.com,project_id=my-project \
    --http-check-request-method=GET \
    --http-check-path=/health \
    --period=60s
```

### 7.1.4 Monitoring Query Language (MQL)

```python
# Calculate error rate
fetch gae_app
| metric 'appengine.googleapis.com/http/server/response_count'
| filter response_code >= 500
| group_by [module_id], sum(value)
| every 1m

# Compare CPU across instances
fetch gce_instance
| metric 'compute.googleapis.com/instance/cpu/utilization'
| group_by [instance_name], mean(value)
| top 5

# Calculate percentiles
fetch https_lb_rule
| metric 'loadbalancing.googleapis.com/https/backend_latencies'
| align delta(1m)
| group_by [], [p50: percentile(value, 50), p95: percentile(value, 95), p99: percentile(value, 99)]
```

---

## 7.2 Reliability Engineering (SLI/SLO)

### 7.2.1 Definitions

| Term | Definition | Example |
|------|------------|---------|
| **SLI** | Quantitative measure of service performance | Request latency, error rate |
| **SLO** | Target value for an SLI | 99.9% availability |
| **SLA** | Business agreement with consequences | 99.9% uptime or credits |
| **Error Budget** | Allowed failure (100% - SLO) | 0.1% downtime/month |

### 7.2.2 Common SLI Types

| SLI Category | Metric | Good For |
|--------------|--------|----------|
| **Availability** | Successful requests / Total requests | APIs, web services |
| **Latency** | % requests < threshold | User-facing apps |
| **Throughput** | Requests per second | Data pipelines |
| **Freshness** | Time since last update | Dashboards, caches |
| **Durability** | Data loss events | Storage systems |

### 7.2.3 Creating SLOs in Cloud Monitoring

```bash
# Create SLO for Cloud Run service (99.5% availability)
gcloud monitoring slos create my-slo \
    --service=my-service \
    --display-name="Availability SLO" \
    --sli-type=request-based \
    --goal=0.995 \
    --rolling-period=28d

# Create latency SLO (99% of requests < 500ms)
gcloud monitoring slos create latency-slo \
    --service=my-service \
    --display-name="Latency SLO" \
    --sli-type=windows-based \
    --good-total-ratio-threshold=0.99 \
    --rolling-period=7d
```

### 7.2.4 Error Budget Policy

```
┌─────────────────────────────────────────────────────────────┐
│                    ERROR BUDGET WORKFLOW                    │
└─────────────────────────────────────────────────────────────┘

Budget Remaining > 20%          Budget < 20%           Budget Exhausted
        │                            │                        │
        v                            v                        v
   Ship features              Slow down releases      Stop feature work
   Normal velocity            Focus on stability      Only reliability fixes
```

---

## 7.3 Cloud Logging (Management)

### 7.3.1 Log Types

| Log Type | Source | Retention | Cost |
|----------|--------|-----------|------|
| **Platform Logs** | GCP services (automatic) | 30 days | Included (up to limit) |
| **User Logs** | Your applications | 30 days | Charged |
| **Audit Logs** | Admin Activity, Data Access | 400 days / 30 days | Admin free, Data charged |
| **VPC Flow Logs** | Network traffic | 30 days | Charged |

### 7.3.2 Log Queries

```bash
# Basic query in Logs Explorer
resource.type="gce_instance"
severity>=ERROR
timestamp>="2024-01-01T00:00:00Z"

# JSON payload query
jsonPayload.message:"connection refused"
jsonPayload.user_id="12345"

# Combine with AND/OR
(resource.type="cloud_run_revision" OR resource.type="gae_app")
severity=ERROR
httpRequest.status>=500

# Regex matching
textPayload=~"error.*timeout"
```

```bash
# Query logs via gcloud
gcloud logging read 'resource.type="gce_instance" AND severity>=ERROR' \
    --limit=50 \
    --format=json

# Tail logs in real-time
gcloud logging tail 'resource.type="cloud_run_revision"' --format=json
```

### 7.3.3 Log-Based Metrics

| Metric Type | Description | Use Case |
|-------------|-------------|----------|
| **Counter** | Count occurrences | Error count, request count |
| **Distribution** | Extract numeric values | Latency distribution |
| **Boolean** | True/false based on log presence | Health indicators |

```bash
# Create counter metric for errors
gcloud logging metrics create error_count \
    --description="Count of ERROR logs" \
    --log-filter='severity=ERROR'

# Create distribution metric for latency
gcloud logging metrics create request_latency \
    --description="Request latency distribution" \
    --log-filter='resource.type="cloud_run_revision"' \
    --value-extractor='EXTRACT(jsonPayload.latency_ms)'
```

### 7.3.4 Log Sinks (Export)

| Destination | Use Case | Query Support |
|-------------|----------|---------------|
| **Cloud Storage** | Long-term archive, compliance | Limited |
| **BigQuery** | Analytics, investigations | Full SQL |
| **Pub/Sub** | Real-time processing, SIEM | Streaming |
| **Splunk/other** | Third-party integration | Via Pub/Sub |

```bash
# Create sink to BigQuery
gcloud logging sinks create bq-sink \
    bigquery.googleapis.com/projects/my-project/datasets/logs \
    --log-filter='resource.type="gce_instance"'

# Create aggregated sink at org level
gcloud logging sinks create org-sink \
    bigquery.googleapis.com/projects/security-project/datasets/all_logs \
    --organization=123456789 \
    --include-children \
    --log-filter='logName:"cloudaudit.googleapis.com"'

# Grant sink service account access to BigQuery
gcloud projects add-iam-policy-binding my-project \
    --member="serviceAccount:p123456789-123456@gcp-sa-logging.iam.gserviceaccount.com" \
    --role="roles/bigquery.dataEditor"
```

### 7.3.5 Log Exclusion (Cost Optimization)

```bash
# Exclude verbose GKE system logs
gcloud logging sinks create exclude-kube-system \
    --log-filter='resource.type="k8s_container" AND resource.labels.namespace_name="kube-system"' \
    --exclusion

# Exclude INFO logs from specific service
gcloud logging sinks update _Default \
    --add-exclusion=name=exclude-info,filter='severity=INFO AND resource.labels.service_name="my-service"'
```

---

## 7.4 Performance Analysis Tools

### 7.4.1 Cloud Trace (Distributed Tracing)

Visualize request flow across microservices.

| Feature | Description |
|---------|-------------|
| **Waterfall View** | Request breakdown by service |
| **Auto-instrumentation** | Automatic for App Engine, Cloud Run, Cloud Functions |
| **Custom Spans** | Add using OpenTelemetry SDK |
| **Sampling** | Configurable trace sampling rate |
| **Analysis** | Latency breakdown, bottleneck identification |

```python
# Python example with OpenTelemetry
from opentelemetry import trace
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Setup
tracer_provider = TracerProvider()
cloud_trace_exporter = CloudTraceSpanExporter()
tracer_provider.add_span_processor(BatchSpanProcessor(cloud_trace_exporter))
trace.set_tracer_provider(tracer_provider)

# Create spans
tracer = trace.get_tracer(__name__)
with tracer.start_as_current_span("my-operation") as span:
    span.set_attribute("user.id", "12345")
    # ... your code
```

### 7.4.2 Cloud Profiler (Continuous Profiling)

| Profile Type | Measures | Use Case |
|--------------|----------|----------|
| **CPU Time** | Function CPU consumption | Optimize hot paths |
| **Heap** | Memory allocation | Find memory leaks |
| **Threads** | Thread blocking | Concurrency issues |
| **Contention** | Lock contention | Thread synchronization |
| **Wall Time** | Real elapsed time | Overall latency |

```bash
# Enable profiler in Python
pip install google-cloud-profiler

# In your application
import googlecloudprofiler

googlecloudprofiler.start(
    service='my-service',
    service_version='1.0.0',
    verbose=3
)
```

### 7.4.3 Error Reporting

Automatic error grouping and notification.

```bash
# View errors
gcloud beta error-reporting events list

# Create notification for new errors (via alerting policy)
gcloud monitoring channels list  # Get notification channel ID

gcloud alpha monitoring policies create \
    --display-name="New Errors Alert" \
    --condition-display-name="New error group" \
    --condition-filter='resource.type="cloud_run_revision"' \
    --notification-channels=projects/my-project/notificationChannels/123
```

---

## 7.5 Operations Agent (Deep Dive)

### 7.5.1 What the Agent Provides

| Without Agent | With Ops Agent |
|---------------|----------------|
| Basic CPU utilization | Detailed CPU (per-core, steal, wait) |
| ❌ No memory metrics | Memory usage, cache, buffers |
| ❌ No disk space | Disk usage, inodes |
| ❌ No custom logs | Application log collection |
| ❌ No process metrics | Per-process CPU/memory |

### 7.5.2 Installation Methods

```bash
# Interactive installation (single VM)
curl -sSO https://dl.google.com/cloudagents/add-google-cloud-ops-agent-repo.sh
sudo bash add-google-cloud-ops-agent-repo.sh --also-install

# Policy-based installation (fleet management)
gcloud compute instances ops-agents policies create ops-agent-policy \
    --project=my-project \
    --zone=us-central1-a \
    --agent-rules="type=ops-agent,version=current-major,packageState=installed" \
    --os-types="short-name=debian,version=11"

# Via startup script (for MIG/instance template)
startup-script: |
  #!/bin/bash
  curl -sSO https://dl.google.com/cloudagents/add-google-cloud-ops-agent-repo.sh
  bash add-google-cloud-ops-agent-repo.sh --also-install
```

### 7.5.3 Custom Configuration

```yaml
# /etc/google-cloud-ops-agent/config.yaml

# Collect nginx access logs
logging:
  receivers:
    nginx_access:
      type: nginx_access
    nginx_error:
      type: nginx_error
  service:
    pipelines:
      nginx:
        receivers: [nginx_access, nginx_error]

# Collect MySQL metrics
metrics:
  receivers:
    mysql:
      type: mysql
      endpoint: localhost:3306
      username: monitoring
      password: ${MYSQL_PASSWORD}
  service:
    pipelines:
      mysql:
        receivers: [mysql]
```

---

## 7.6 Incident Management

### 7.6.1 Incident Response Flow

```
Alert Fired -> Incident Created -> Page On-Call -> Acknowledge -> Investigate -> Resolve -> Postmortem
     │               │                  │              │              │            │           │
     v               v                  v              v              v            v           v
  Monitoring     Auto-create      PagerDuty/       Silence       Dashboards    Change      Blameless
   Policy        or manual        Slack/etc        alerts        & Logs        status      review
```

### 7.6.2 Best Practices

| Practice | Implementation |
|----------|----------------|
| **Alert on symptoms** | User-facing impact, not causes |
| **Reduce noise** | Tune thresholds, use alert grouping |
| **Multiple channels** | Email + Slack + PagerDuty |
| **Runbooks** | Link documentation in alerts |
| **Postmortems** | Blameless review after incidents |

```bash
# Create notification channel (email)
gcloud beta monitoring channels create \
    --display-name="Ops Team Email" \
    --type=email \
    --channel-labels=email_address=ops@example.com

# Create notification channel (Slack)
gcloud beta monitoring channels create \
    --display-name="Alerts Slack" \
    --type=slack \
    --channel-labels=auth_token=xoxb-xxx,channel_name=alerts
```

---

## 7.7 Operations Quick Reference

### Key gcloud Commands

```bash
# Monitoring
gcloud monitoring dashboards list
gcloud monitoring policies list
gcloud monitoring channels list

# Logging
gcloud logging read "severity>=ERROR" --limit=100
gcloud logging sinks list
gcloud logging metrics list

# Uptime checks
gcloud monitoring uptime list-configs

# Error reporting
gcloud beta error-reporting events list
```

### Metrics to Monitor by Service

| Service | Key Metrics |
|---------|-------------|
| **Compute Engine** | CPU, memory, disk, network |
| **Cloud SQL** | CPU, memory, connections, replication lag |
| **Cloud Run** | Request count, latency, container instances |
| **GKE** | Node CPU/memory, pod restarts, pending pods |
| **Cloud Storage** | Request count, object count, bucket size |
| **Load Balancer** | Request count, latency, error rate |
