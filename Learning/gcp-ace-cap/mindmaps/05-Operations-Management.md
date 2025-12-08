# GCP Operations & Management - Detailed Mindmap & Design

## 1. Cloud Operations (formerly Stackdriver)
*   **Cloud Logging**
    *   **Log Types**:
        *   *Admin Activity*: "Who did what". Always on. Free. 400-day retention.
        *   *Data Access*: "Who accessed data". Disabled by default (except BigQuery). Paid.
        *   *System/App Logs*: From agents/services.
    *   **Log Router (Sinks)**:
        *   Export logs to other services for long-term storage or analysis.
        *   *Destinations*:
            *   **Cloud Storage**: Long-term retention, Compliance, Cheapest.
            *   **BigQuery**: Analytics, SQL queries.
            *   **Pub/Sub**: Streaming to external tools (Splunk, Datadog).
    *   **Exclusion Filters**: Drop noisy logs to save money.
    *   **Log-based Metrics**: Create metrics from log entries (e.g., count "Error 500").

*   **Cloud Monitoring**
    *   **Metrics**:
        *   *System*: CPU, RAM, Disk (from Agent).
        *   *Custom*: App-specific metrics.
    *   **Uptime Checks**:
        *   Check endpoint availability from around the world.
        *   Public (URL) or Private (Internal IP).
    *   **Alerting Policies**:
        *   Trigger when metric crosses threshold.
        *   *Notification Channels*: Email, SMS, Slack, PagerDuty, Pub/Sub (Auto-healing).
    *   **Dashboards**: Visualize metrics.

*   **APM (Application Performance Management)**
    *   **Cloud Trace**: Distributed tracing. Latency analysis. Find bottlenecks in microservices.
    *   **Cloud Profiler**: Continuous profiling. CPU/Memory usage. Find expensive code.
    *   **Cloud Debugger**: (Deprecated/Retired) Snapshot state of running app.
    *   **Error Reporting**: Aggregates and groups crash logs/stack traces.

## 2. Billing & Cost Management
*   **Billing Account**
    *   Linked to Projects.
    *   One Billing Account -> Many Projects.
    *   One Project -> One Billing Account.
*   **Budgets & Alerts**
    *   Set threshold (Amount or % of last month).
    *   Send email/Pub/Sub when threshold reached.
    *   **Does NOT stop spending** automatically (requires Pub/Sub + Cloud Function to stop resources).
*   **Exports**
    *   **BigQuery Export**: Detailed billing data. Essential for custom analysis/visualization (Data Studio/Looker).
*   **Cost Optimization**
    *   **Committed Use Discounts (CUDs)**: 1 or 3 year commitment. No upfront or Partial upfront.
    *   **Sustained Use Discounts (SUDs)**: Automatic discount for running VMs >25% of month (GCE only).
    *   **Preemptible/Spot VMs**: Fault-tolerant workloads.
    *   **Recommendations AI**: Suggests resizing/idle VM cleanup.

## 3. Deployment & Infrastructure as Code
*   **Cloud Build**
    *   Serverless CI/CD.
    *   Build steps (Docker containers).
    *   Triggers (Git push).
*   **Artifact Registry**
    *   Store Docker images, Maven/npm/Python packages.
    *   Replaces Container Registry (GCR).
    *   Vulnerability scanning.
*   **Google Cloud Deployment Manager**
    *   Native IaC tool.
    *   YAML/Python templates.
    *   *Note*: Terraform is widely used and supported, but DM is the native tool.

---

## 🧠 Design Decision Guide: Operations

### Logging Export Strategy
1.  **Compliance / Long-term Archive** -> **Cloud Storage**.
2.  **Analytics / SQL Querying** -> **BigQuery**.
3.  **External SIEM / Real-time processing** -> **Pub/Sub**.

### Monitoring Strategy
1.  **"Is it up?"** -> **Uptime Checks**.
2.  **"Is it slow?"** -> **Cloud Trace**.
3.  **"Is it expensive (CPU/RAM)?"** -> **Cloud Profiler**.
4.  **"Did it crash?"** -> **Error Reporting**.
5.  **"Alert me"** -> **Monitoring Alerting Policy**.

### 🔑 Key Exam Rules
1.  **"Stop spending"** -> **Budget + Pub/Sub + Cloud Function** (Budget alone only alerts).
2.  **"Analyze Billing"** -> **Export to BigQuery**.
3.  **"Retain Logs > 400 days"** -> **Log Sink to Storage**.
4.  **"Custom Metric"** -> **Log-based Metric** (if data is in logs) or **Monitoring API**.
