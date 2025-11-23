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
