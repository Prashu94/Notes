# Observability deep dive

Read `11-observability-and-operations.md` and the alerting section of `22-security-operations-deep-dive.md`. This file is the logging path, the metric types, and the SLO math.

## Where a log line goes

1. The product or the Ops Agent writes an entry.
2. The log router sees it. The `_Required` sink keeps Admin Activity and System Event. You cannot disable that sink.
3. The `_Default` sink keeps the rest, minus exclusions.
4. Your sinks copy matching entries to BigQuery, Cloud Storage, Pub/Sub, or another project.
5. A log bucket stores the entry for its retention. Log Analytics can query a bucket that has analytics on.
6. A log-based metric counts or samples matching lines and becomes a Monitoring metric.

```bash
gcloud logging read \
  'resource.type="cloud_run_revision"
   AND severity>=ERROR
   AND resource.labels.service_name="api"' \
  --freshness=1d --limit=20 --format='value(timestamp,textPayload,jsonPayload.message)'

gcloud logging sinks create to-bq \
  "bigquery.googleapis.com/projects/${PROJECT_ID}/datasets/logs" \
  --log-filter='logName:"clou_audit" OR resource.type="cloud_run_revision"'

WRITER=$(gcloud logging sinks describe to-bq --format='value(writerIdentity)')
# Grant WRITER roles/bigquery.dataEditor on the dataset, or the partitioned tables are never created.

gcloud logging sinks update _Default \
  --add-exclusion='name=health,filter=httpRequest.requestUrl:"/healthz"'
```

Exclusions drop volume and cost. Do not exclude audit logs. Do not exclude the error you will need during an incident. Exclude health checks and noisy debug.

| Destination | Pick it when |
| --- | --- |
| Log Analytics on the bucket | You want SQL on recent logs without a copy |
| BigQuery sink | Analysts, long retention, joins to billing export |
| Cloud Storage sink | Cheap years, compliance lock, not interactive SQL |
| Pub/Sub sink | Another system must react to each entry |
| Another project | The security team owns the archive and app teams must not delete it |

Retention on `_Default` is configurable. `_Required` is not, and it is already long. A locked user-defined bucket cannot have its retention shortened. That is the same idea as a bucket lock on Cloud Storage.

Data Access logs are off for most services. Turn them on only for the services where a read is an audit event. BigQuery data access is already on. A Storage object-read audit is a choice, and it can be larger than the application logs.

## Metrics

| Kind | Example | Alert on it? |
| --- | --- | --- |
| Built-in workload | Cloud Run request count, latency, CPU | Yes for errors and latency. CPU as a chart. |
| Guest, via Ops Agent | Memory percent, disk percent, process | Disk full, yes. Memory if the app dies at a known level. |
| Log-based counter | Count of `severity>=ERROR` | Yes, with a duration so one line does not page |
| Log-based distribution | Latency parsed from a log | When the platform metric does not exist |
| Custom, from the API | Queue depth inside the app | When nothing else exposes it |
| Prometheus, managed collection | A scrape on GKE | ACE names Managed Service for Prometheus |
| Absence | The metric stopped | Yes. A dead agent looks “fine” on a threshold alert. |

```bash
gcloud logging metrics create api_errors \
  --description="Cloud Run errors" \
  --log-filter='resource.type="cloud_run_revision" AND severity>=ERROR'
```

Uptime checks hit a URL from outside Google, or from a private checker if the service is internal. They answer “can a user reach it”, which CPU does not.

```bash
gcloud monitoring uptime create api \
  --resource-type=uptime-url \
  --resource-labels=host=api.example.com,project_id="$PROJECT_ID" \
  --protocol=https --path=/healthz --period=60 --timeout=10
```

## An alert that is safe to page

Parts:

- Filter to one service
- Alignment window (for example 5 minutes) so a single spike is not the value
- Threshold
- Duration the threshold must hold (for example 5 minutes)
- A channel that wakes a person
- Documentation: the dashboard link and the rollback command

Page on:

- Uptime check failing
- Error ratio above the SLO burn
- p95 latency above the budget for a sustained window
- Replication lag or backup age too old
- Disk will fill
- Certificate expires in a few days
- Dataflow streaming job failed
- Cloud SQL failover happened, as a ticket at least

Do not page on:

- CPU at 70% with happy users
- A single log line
- Email to a list nobody reads

```bash
gcloud monitoring channels list
gcloud monitoring policies list
gcloud monitoring dashboards list
```

The policy body is JSON in the API. You should be able to describe it. You do not have to memorize the schema. The console is an acceptable way to create it. The exam tests the shape: symptom, duration, channel, not a 200-line JSON document.

## SLI, SLO, SLA, burn

| Term | Meaning |
| --- | --- |
| SLI | The measurement. Good requests / all requests. Or requests faster than 300 ms / all requests. |
| SLO | The target. 99.9% of requests are good over 28 days. |
| SLA | The contract that pays out. Looser than the SLO. Never tighter. |
| Error budget | `1 - SLO`. 99.9% over 30 days is about 43 minutes, or 0.1% of requests. |
| Burn rate | How fast you are spending the budget. A burn of 1 spends it exactly on time. A burn of 14.4 spends a 30-day budget in about 2 days. |

Multi-window alerts: page if the last hour is burning fast and the last 5 minutes agrees. Ticket if the last day is slightly over. That pairing is the operational-excellence answer when the stem says “we get paged for noise and we still miss real outages.”

Release policy: if the budget remains, ship. If it is gone, stop feature releases and pay down reliability. That is the point of the number.

## Trace, Profiler, Error Reporting

| Tool | You open it when |
| --- | --- |
| Cloud Trace | A request is slow and you need the hop. Cloud Run and instrumented GKE emit spans. You still add spans in your own code for the database call. |
| Cloud Profiler | One process is hot. CPU or heap. It is sampling, so it is safe enough for production. |
| Error Reporting | Exceptions should be grouped. It reads logs that look like stack traces. Fix the top group, not the latest unique message. |
| Connectivity Tests | You think a firewall or a route is why a packet fails |
| Query Insights | Cloud SQL is the slow hop |
| Personalized Service Health | You need to know if Google’s side is the incident, for your project, not the global status homepage only |

Order during an incident: user symptom, recent change, SLO chart, trace of a slow request, logs of that span, then saturation (CPU, connections, quota). Resizing is after that list, unless the chart already shows saturation and the remedy is known.

## Ops Agent

Install on Compute Engine when you need memory, disk, or a file log. GKE and Cloud Run do not need it for platform logs. The agent uses the VM service account. That account needs `roles/logging.logWriter` and `roles/monitoring.metricWriter`. A default compute service account with Editor works and is the wrong IAM. Grant the two writer roles on a dedicated account.

Managed Service for Prometheus on GKE collects Prometheus metrics without you running a Prometheus server to operate. The ACE guide names it next to the Ops Agent. Do not install a pet Prometheus VM as the first answer.

## Diagnostics the ACE guide names

“Use cloud diagnostics” means this set, not a single product: Logging, Monitoring, Trace, Profiler, Error Reporting, and the product’s own tool (Connectivity Tests, Query Insights). “View Google Cloud status” means the public dashboard plus Personalized Service Health. Your uptime check still wins if status is green and users are failing.

## Exercises

1. Admin Activity must be kept for three years and queried with SQL. Which sink, and do you have to enable the log?
2. Health-check lines are half the log bill. How do you drop them without dropping errors?
3. The Ops Agent was stopped. The CPU alert did not fire. What kind of alert would have fired?
4. 99.9% of requests under 300 ms. Write the SLI in one sentence.
5. A deploy at 14:00 matches the start of 5xx. What is the first remediation if Cloud Run has the previous revision?

### Answers

1. Admin Activity is already on, in `_Required`. Add a BigQuery sink of `logName:"clou_audit"` and keep the dataset. Grant the sink writer. You do not enable Admin Activity.
2. An exclusion on the `_Default` sink for the health path. Do not exclude `severity>=ERROR`.
3. An absence alert on the agent’s own metric, or an uptime check on the service. A threshold needs data.
4. The fraction of requests whose latency is under 300 ms, measured at the load balancer or the Cloud Run request metric.
5. Send 100% of traffic back to the previous revision. Then read traces. Do not start by adding CPUs.
