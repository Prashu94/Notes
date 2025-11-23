# Google Cloud Professional Cloud Architect (PCA) - Serverless Architecture Guide

## 1. Advanced Architecture Patterns

### 1.1 Choreography vs. Orchestration (Critical Concept)
*   **Choreography (Event-Driven)**:
    *   **Mechanism**: Services emit events (Pub/Sub, Eventarc) and other services react.
    *   **Pros**: Loose coupling, high scalability.
    *   **Cons**: "Distributed Monolith" risk. Hard to debug (who triggered what?).
    *   **Tool**: **Eventarc** / **Pub/Sub**.
*   **Orchestration (Workflow-Driven)**:
    *   **Mechanism**: A central coordinator tells services what to do.
    *   **Pros**: Clear state visibility, error handling, retries, timeouts.
    *   **Cons**: Tighter coupling to the orchestrator.
    *   **Tool**: **Cloud Workflows** / **Cloud Composer (Airflow)**.

### 1.2 Cloud Workflows (The Orchestrator)
Serverless workflow engine for linking HTTP-based services.
*   **Key Features**:
    *   **Zero Maintenance**: No infrastructure (unlike Composer/Airflow).
    *   **Low Latency**: Fast execution, suitable for user-facing flows.
    *   **Connectors**: Native integration with GCP APIs (Compute, Firestore, BigQuery) without writing HTTP calls.
*   **Syntax Example (YAML)**:
    ```yaml
    - init:
        assign:
          - project: ${sys.get_env("GOOGLE_CLOUD_PROJECT_ID")}
    - call_cloud_run:
        call: http.post
        args:
          url: https://my-service-xyz.a.run.app
          auth:
            type: OIDC
        result: api_response
    - check_result:
        switch:
          - condition: ${api_response.code == 200}
            next: success_step
    ```

### 1.3 Asynchronous Task Queues (Cloud Tasks)
*   **Problem**: You have a Cloud Run service that processes images. If 10,000 users upload at once, the service crashes or scales too fast (cost spike).
*   **Solution**: **Cloud Tasks**.
    *   **Rate Limiting**: "Process max 50 images per second".
    *   **Retries**: "If it fails, wait 10s, then 20s, then 40s (Exponential Backoff)".
    *   **Deduplication**: Ensure a task is added only once.
    *   **Architecture**: User -> Frontend -> **Cloud Tasks Queue** -> **Cloud Run Worker**.

## 2. Serverless Networking & Security

### 2.1 Global Serverless Load Balancing
Put a **Global External Application Load Balancer** in front of Cloud Run/Functions.
*   **Why?**:
    1.  **Single Anycast IP**: One IP for the whole world.
    2.  **Cloud Armor**: WAF protection (SQLi, XSS, Geo-blocking).
    3.  **Cloud CDN**: Cache static assets at the edge.
    4.  **Multi-Region Failover**: If `us-central1` is down, route to `us-east1`.
*   **Setup**:
    *   Create a **Serverless NEG (Network Endpoint Group)** for each region.
    *   Add NEGs to the Backend Service of the Load Balancer.

### 2.2 Private Service Connect (PSC)
*   **Scenario**: You have a Cloud Run service in Project A (Producer). You want a VM in Project B (Consumer) to access it privately, *without* VPC Peering.
*   **Solution**:
    *   **Producer**: Expose Cloud Run via a Load Balancer with a Service Attachment.
    *   **Consumer**: Create a PSC Endpoint (Internal IP) in their VPC.
    *   **Traffic**: Flows privately across Google's backbone.

## 3. State Management in Serverless

### 3.1 Database Connections (The "Connection Limit" Problem)
*   **Problem**: Serverless scales to thousands of instances. If each instance opens a connection to Cloud SQL (Postgres/MySQL), the database runs out of connections.
*   **Solution**:
    1.  **Cloud SQL Auth Proxy**: Handles secure connection, but doesn't pool well.
    2.  **PgBouncer (Sidecar/Proxy)**: Connection pooling middleware.
    3.  **Cloud SQL Connector for Java/Python/Go**: Libraries that manage connections efficiently.
    4.  **Firestore / Spanner**: Built for massive concurrency (HTTP-based, no connection limits).

### 3.2 Shared State
*   **Do NOT** store state in the container memory or local disk (it's ephemeral).
*   **Use**:
    *   **Memorystore (Redis)**: For high-speed caching (Session store).
    *   **Firestore**: For user profiles, metadata.
    *   **Cloud Storage**: For large files (Images, PDFs).

## 4. Migration Strategy: "Strangler Fig"
*   **Concept**: Slowly replace a monolithic app with microservices.
*   **Implementation**:
    1.  Deploy the Monolith on App Engine / Compute Engine.
    2.  Build a new feature (e.g., "Search") on Cloud Run.
    3.  Use the **Load Balancer** to route `/search` to Cloud Run and `/*` to the Monolith.
    4.  Repeat until the Monolith is gone.
