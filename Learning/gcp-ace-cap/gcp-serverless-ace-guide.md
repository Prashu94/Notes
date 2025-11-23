# Google Cloud Certified Associate Cloud Engineer (ACE) - Serverless Deep Dive

## 1. Cloud Run (The Gold Standard)

### 1.1 Architecture & Lifecycle
Cloud Run is a managed compute platform that runs stateless containers.
*   **Knative-based**: Built on the open-source Knative standard (portability).
*   **Revisions**: Every time you deploy, a new **Revision** is created.
    *   Revisions are immutable (you can't change a running revision, you must deploy a new one).
    *   **Traffic Splitting**: You can route 10% of traffic to `v2-green` and 90% to `v1-blue` for canary testing.
    *   **Rollbacks**: Instant rollback by changing the traffic split to 100% on the old revision.

### 1.2 Services vs. Jobs
| Feature | **Cloud Run Services** | **Cloud Run Jobs** |
| :--- | :--- | :--- |
| **Trigger** | HTTP Request, gRPC, Eventarc. | Manual, Scheduled (Cloud Scheduler), Workflow. |
| **Scaling Metric** | **Concurrency** (Requests per instance). | **Parallelism** (Number of tasks). |
| **Timeout** | Max 60 mins (default 5 mins). | Max 24 hours. |
| **Use Case** | APIs, Webhooks, Websites. | DB Migrations, Video Rendering, Batch Scripts. |

### 1.3 Networking & Security (Exam Critical)
*   **Ingress Control**:
    *   `--ingress all`: Public internet access.
    *   `--ingress internal`: Only from VPC, other Cloud Run services, or Eventarc.
    *   `--ingress internal-and-cloud-load-balancing`: Allows Global LB to front the service (for WAF/CDN).
*   **VPC Access (Egress)**:
    *   **Direct VPC Egress (New)**: Sends traffic directly to VPC without a connector. Faster, cheaper.
    *   **Serverless VPC Access Connector (Old)**: A VM-based bridge. Required for Shared VPCs in some older setups.
*   **Authentication**:
    *   **Public**: `--allow-unauthenticated` (assigns `roles/run.invoker` to `allUsers`).
    *   **Private**: Requires an OIDC Token in the `Authorization: Bearer <token>` header.

### 1.4 Essential CLI Commands
```bash
# Deploy a new revision with traffic splitting
gcloud run deploy my-app --image gcr.io/proj/img:v2 --no-traffic
gcloud run services update-traffic my-app --to-tags v2=10

# Set environment variables and secrets
gcloud run deploy my-app     --set-env-vars DB_HOST=10.0.0.5     --set-secrets DB_PASS=projects/my-proj/secrets/db-pass:latest

# Create a job with 50 parallel tasks
gcloud run jobs create data-processor     --image gcr.io/proj/processor     --tasks 50     --max-retries 3
```

## 2. Cloud Functions (FaaS)

### 2.1 Gen 1 vs. Gen 2 (Must Know)
*   **Gen 1**:
    *   Google-proprietary architecture.
    *   **Slow Cold Starts**.
    *   **Concurrency = 1**: One instance handles ONE request at a time. If you get 100 requests, you spin up 100 instances.
*   **Gen 2 (Exam Standard)**:
    *   **Built on Cloud Run**: It's literally a Cloud Run service with a function signature.
    *   **Concurrency > 1**: One instance can handle up to 1000 concurrent requests (cheaper).
    *   **Longer Timeouts**: Up to 60 mins for HTTP.
    *   **Eventarc Integration**: Native support for 90+ Google Cloud events (e.g., "BigQuery Job Completed").

### 2.2 Triggers
1.  **HTTP**: A public or private URL.
2.  **Cloud Storage**: Trigger on `google.storage.object.finalize` (File Upload).
3.  **Pub/Sub**: Trigger on message publish.
4.  **Firestore**: Trigger on document create/update/delete.

## 3. App Engine (PaaS)

### 3.1 Standard vs. Flexible
| Feature | **App Engine Standard** | **App Engine Flexible** |
| :--- | :--- | :--- |
| **Runtime** | Specific versions (Python 3.10, Java 17, Node 16). | **Docker Containers** (Any language/library). |
| **Startup** | Milliseconds (Scale to Zero). | Minutes (Minimum 1 instance running). |
| **OS Access** | Sandbox (No writing to local disk, no background threads). | VM Access (SSH allowed, background processes allowed). |
| **Network** | Uses App Engine specific network. | Runs on Compute Engine VMs in your VPC. |

### 3.2 Configuration (app.yaml)
The `app.yaml` file controls scaling and resources.
```yaml
runtime: python310
instance_class: F2  # Vertical Scaling (More CPU/RAM)
automatic_scaling:
  target_cpu_utilization: 0.65
  min_instances: 1
  max_instances: 100
```

### 3.3 Traffic Splitting
App Engine has built-in traffic splitting (A/B Testing).
*   **IP Address**: Sticky session based on client IP.
*   **Cookie**: Sticky session based on a cookie (better for users behind NAT).
*   **Random**: Purely random distribution.

```bash
gcloud app services set-traffic my-service --splits v1=.5,v2=.5 --split-by cookie
```
