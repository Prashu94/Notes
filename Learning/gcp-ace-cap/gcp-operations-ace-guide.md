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
