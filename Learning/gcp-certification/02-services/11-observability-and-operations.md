# Observability and operations excellence

ACE 1.1 and 4.6. PCA section 6. The suite is **Google Cloud Observability**: Cloud Logging, Cloud Monitoring, Cloud Trace, Cloud Profiler, Error Reporting.

## Ops Agent

The Ops Agent collects logs and metrics from Compute Engine and bare VM workloads. Install it when the stem says guest metrics (memory, process) or application logs from a file. GKE and Cloud Run export without it. Managed Service for Prometheus scrapes Prometheus metrics. The ACE guide names both.

```bash
# Ops Agent on a Debian VM
curl -sSO https://dl.google.com/cloudagents/add-google-cloud-ops-agent-repo.sh
sudo bash add-google-cloud-ops-agent-repo.sh --also-install

gcloud logging read "resource.type=gce_instance" --limit=5 --freshness=1h
```

## Logging

Every entry sits in a **log bucket**. The **log router** sends entries to buckets and to **sinks**. Sinks export to another bucket, BigQuery, Cloud Storage, Pub/Sub, or another project.

- `_Required` bucket: Admin Activity, System Event, and some security logs. You cannot turn these off. Retention is long.
- `_Default` bucket: everything else that is not excluded. Retention is configurable.
- Data Access logs are off for most services until you enable them. BigQuery is the exception.

Log Analytics lets you SQL-query logs in a bucket that has analytics enabled. That is different from a BigQuery sink, which is a copy you own.

```bash
# Sink to BigQuery (ACE: export logs)
bq mk --dataset --location="$REGION" ${PROJECT_ID}:logs

gcloud logging sinks create to-bq \
  bigquery.googleapis.com/projects/$PROJECT_ID/datasets/logs \
  --log-filter='resource.type="cloud_run_revision" OR logName:"clou_audit"'

# The sink creates a writer identity. Grant it BigQuery data editor on the dataset.
gcloud logging sinks describe to-bq --format='value(writerIdentity)'

# Read and filter
gcloud logging read \
  'resource.type="cloud_run_revision" AND severity>=ERROR' \
  --limit=20 --freshness=1d --format='value(textPayload)'

# Exclusion on the default sink to drop noisy logs
gcloud logging sinks update _Default \
  --add-exclusion='name=health,filter=httpRequest.requestUrl:"/healthz"'
```

A log-based metric turns a count or a distribution of log lines into a Monitoring metric, which an alert can use.

```bash
gcloud logging metrics create error_count \
  --description="errors" \
  --log-filter='severity>=ERROR'
```

## Monitoring

- Built-in metrics per product (CPU, request count, replication lag).
- Custom metrics from the Monitoring API or from log-based metrics.
- Dashboards.
- Alerting policies: condition, duration, notification channel.
- Uptime checks: public or private probe of a URL.
- SLOs: you define a service-level objective on a service. Error budget is the room left. PCA operational excellence uses this language.
- Notification channels: email, SMS, Pub/Sub, Slack, PagerDuty, webhook. Email alone is how EHR-style case studies say alerts were missed. Send to an on-call channel.

```bash
# Notification channel is often created in the console. The API exists.
gcloud monitoring channels list

# Uptime check
gcloud monitoring uptime create web \
  --resource-type=uptime-url \
  --resource-labels=host=example.com,project_id=$PROJECT_ID \
  --protocol=https --path=/healthz --period=60

gcloud monitoring policies list
```

An alert policy in YAML (concept): a condition on `metric.type`, a threshold, a duration so one spike does not page, and a channel. Alerting on a symptom the user feels (availability, latency, error rate) beats alerting only on CPU.

Custom metrics: the application writes to the Monitoring API, or you define a log-based metric. The ACE bullet “from applications or logs” is exactly those two paths.

## Trace, Profiler, Error Reporting

| Product | Question it answers |
| --- | --- |
| Cloud Trace | Where did the latency go across services? Needs instrumentation or the platform’s automatic traces (Cloud Run, GKE with the right setup). |
| Cloud Profiler | Which function uses CPU or heap in production? Low overhead. PCA says profiling and benchmarking. |
| Error Reporting | Grouped exceptions. It reads logs that look like stack traces. |
| Personalized Service Health | Incidents and maintenance that affect your project. |
| Google Cloud status dashboard | Public status of products. ACE names “viewing Google Cloud status”. Not a substitute for your own uptime check. |

Benchmarking is a test you run (load test), not a checkbox in Monitoring. Profiler plus a load test is the performance-optimization evidence PCA wants before you buy a bigger machine.

## SRE ideas the architect exam uses

- **SLI**: a measured ratio (successful requests / all requests, or requests under 300 ms).
- **SLO**: the target (99.9% over 28 days).
- **SLA**: the contract with a penalty. Do not set an SLA tighter than the SLO you actually run.
- **Error budget**: 100% minus the SLO. Spend it on releases. Freeze releases when it is gone.
- **Multi-window burn alerts**: page on fast burn, ticket on slow burn.
- **Golden signals**: latency, traffic, errors, saturation.

Operational excellence pillar, in exam sentences:

- Automate deploys and infrastructure.
- Observe symptoms, not only causes.
- Practice incident response. Write a short blameless review.
- Reduce toil. If a human repeats it, script it or delete it.
- Change in small steps with a rollback.

## Diagnostics

ACE “cloud diagnostics”: Logging, Monitoring, Trace, Profiler, and the product’s own troubleshooter (Connectivity Tests, Query Insights, GKE recommendations). Start with the user symptom, then the trace, then the logs of the slow span, then saturation metrics. Do not start by resizing the VM.

## Exercises

1. You need memory-used-percent from a Debian VM. What do you install?
2. Security wants Admin Activity kept 3 years in SQL. Where do the logs go, and which bucket already has them?
3. One error line should page only after it happens 20 times in 5 minutes. Metric path?
4. The public status page is green and your users are failing. What do you trust?
5. Name the PCA section 6 observability trio in the exam’s words.

### Answers

1. Ops Agent.
2. They are already in the `_Required` log bucket as Admin Activity. For SQL and a retention you control, add a sink to BigQuery. The required bucket is not your reporting warehouse.
3. A log-based metric counting that line, then an alerting policy with a threshold and alignment window. A single-entry email alert is the wrong shape.
4. Your uptime check and your service’s error metric. Public status is necessary and not sufficient.
5. Monitoring and logging, profiling and benchmarking, alerting strategies.
