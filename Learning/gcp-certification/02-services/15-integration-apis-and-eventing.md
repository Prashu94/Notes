# Integration, APIs, events, and messaging edges

PCA 5.1 names Apigee. ACE 3.3 names events. This chapter is the glue products.

## API management

| Product | When |
| --- | --- |
| Apigee | Full API platform: products, developers, API keys or OAuth, quotas, analytics, monetization, hybrid gateway if the stem needs a runtime outside Google Cloud. PCA’s named answer for API management. |
| Apigee Hybrid | Gateway runtime in your cluster, control plane managed. |
| API Gateway | A simpler gateway in front of Cloud Run, functions, or App Engine. OpenAPI. Use it when the stem does not need Apigee’s portal and monetization. |
| Cloud Endpoints | Older proxy (ESPv2) in front of a service. Recognition. New designs pick API Gateway or Apigee. |
| Service Directory | Registry of service endpoints. Not a gateway. |

Put a gateway in front when there are external developers, partner quotas, or several backends behind one API hostname. Do not put Apigee in front of an internal cron job.

```bash
gcloud services enable apigee.googleapis.com apigateway.googleapis.com
# Apigee organizations are a project-level setup with a paid runtime.
# Know why you recommend it. The console holds the proxy editor.

gcloud api-gateway apis create orders --project="$PROJECT_ID"
gcloud api-gateway api-configs create v1 \
  --api=orders --openapi-spec=openapi.yaml --project="$PROJECT_ID"
gcloud api-gateway gateways create orders-gw \
  --api=orders --api-config=v1 --location="$REGION"
```

## Events and async work

| Product | Job |
| --- | --- |
| Eventarc | Route events to Cloud Run, functions, GKE, Workflows |
| Pub/Sub | Bus and buffer |
| Cloud Tasks | Targeted HTTP tasks with retry and rate limits, from an app. Not a fan-out bus. |
| Cloud Scheduler | Cron |
| Workflows | Orchestrate steps and wait for callbacks |
| Application Integration | Integration Platform as a Service, connectors, visual. When the team is integration developers, not Beam authors. |
| Integration Connectors | The connector catalog behind Application Integration and similar tools |
| Eventarc + Audit Logs | React to almost any API call. Remember to enable Data Access logs or the event never fires. |

```bash
gcloud tasks queues create orders --location="$REGION"
gcloud tasks create-http-task \
  --queue=orders --location="$REGION" \
  --url="https://example.com/worker" \
  --method=POST

gcloud scheduler jobs list --location="$REGION"
```

Choose Cloud Tasks when one producer calls one URL with retry control (send this email, call this webhook). Choose Pub/Sub when many consumers each need a copy. Choose Workflows when the next step depends on the previous step’s body.

## Service mesh and discovery

Cloud Service Mesh: mTLS, retries, traffic split inside the cluster. Service Directory: publish and resolve endpoints. These are not API management.

## Source and developer tools

| Tool | Role |
| --- | --- |
| Cloud Shell, Cloud Shell Editor, Cloud Code | PCA 5.2 |
| Cloud Workstations | Admin-managed dev environments |
| Cloud Source Repositories | Hosted git |
| Secure Source Manager | Hardened git |
| Developer Connect | Link external SCM |
| App Hub and Application Design Center | Describe an application’s components. Recognition for operations, not a runtime. |

## Domain and certificates at the edge

Cloud Domains registers domains. Cloud DNS serves them. Certificate Manager proves TLS. They sit with the load balancer chapter.

## Exercises

1. Partners need API keys, a quota, and a developer portal. API Gateway or Apigee?
2. An app must retry a single webhook at a controlled rate. Pub/Sub or Cloud Tasks?
3. You need a workflow that waits for a human approval callback, then deploys. Which product?
4. A Cloud Storage upload must start a Cloud Run service. Which router?

### Answers

1. Apigee.
2. Cloud Tasks.
3. Workflows, with an approval step. Cloud Deploy also has approvals for releases. Use Cloud Deploy if the thing being approved is a GKE or Cloud Run release. Use Workflows if the steps are arbitrary APIs.
4. Eventarc (Storage finalized), or a bucket notification into Pub/Sub that pushes to Cloud Run.
