# Cloud Run, Cloud Run functions, and App Engine

Serverless compute. ACE 2.1, 3.3, 4.3. PCA 1.3 and 2.3.

## How to choose

| Need | Product |
| --- | --- |
| HTTP service or a container that should scale to zero | Cloud Run service |
| Container that runs and exits (batch, migration step) | Cloud Run job |
| One function, one event, minimal code | Cloud Run functions |
| Legacy PaaS with `app.yaml`, versions, and services already there | App Engine |
| Kubernetes API | GKE, not this chapter |
| Guest OS | Compute Engine |

Cloud Run for Anthos is the older name for Cloud Run on a GKE Enterprise cluster. The ACE guide still says it. Fully managed Cloud Run is the default. Use the GKE-backed form only when the stem requires the cluster’s network, GPU layout, or on-premises Anthos/GKE Enterprise.

## Cloud Run

A **service** listens for HTTP (and gRPC, WebSockets). A **job** runs tasks to completion. Concurrency is many requests per instance, which is why it is cheaper than one-request-per-instance functions for web traffic.

Generation 2 is the execution environment to know: stronger sandbox, network file systems, and the current default. Do not design new work on gen1.

Notable limits you should be able to talk about without memorizing a table: request timeout (long, but not infinite), memory and CPU you set per instance, scale to zero unless `min-instances` is set, pay for allocated CPU while a request is in flight unless you choose always-allocated CPU.

```bash
# From source (buildpacks) or from an image
gcloud run deploy web \
  --source=. \
  --region="$REGION" \
  --service-account="$SA_EMAIL" \
  --allow-unauthenticated \
  --min-instances=0 \
  --max-instances=20 \
  --concurrency=80 \
  --cpu=1 --memory=512Mi \
  --port=8080 \
  --set-env-vars=ENV=prod

# Private service. Callers need roles/run.invoker.
gcloud run deploy internal \
  --image="${REGION}-docker.pkg.dev/${PROJECT_ID}/apps/api:1" \
  --region="$REGION" \
  --no-allow-unauthenticated \
  --ingress=internal

# New revision and traffic split (ACE 4.3)
gcloud run deploy web --image="${REGION}-docker.pkg.dev/${PROJECT_ID}/apps/web:2" \
  --region="$REGION" --no-traffic
gcloud run services update-traffic web \
  --region="$REGION" \
  --to-revisions=web-00002=10,web-00001=90

gcloud run revisions list --service=web --region="$REGION"
gcloud run services describe web --region="$REGION"

# Job
gcloud run jobs create nightly \
  --image="${REGION}-docker.pkg.dev/${PROJECT_ID}/apps/batch:1" \
  --region="$REGION" \
  --tasks=10 --parallelism=5 \
  --service-account="$SA_EMAIL"
gcloud run jobs execute nightly --region="$REGION"
```

Ingress settings: `all`, `internal`, `internal-and-cloud-load-balancing`. Put an external Application Load Balancer in front when you need Cloud Armor, CDN, or serverless NEGs across regions.

Cloud Run can mount Cloud Storage via Cloud Storage FUSE and NFS (Filestore) on gen2. That does not make it a POSIX server. It makes a read path possible.

GPU on Cloud Run is for inference when the stem wants scale-to-zero or simple deploys and a supported GPU. Large training is AI Hypercomputer or GKE, not a Cloud Run request.

## Events: Eventarc and Cloud Run functions

ACE 3.3: receive Pub/Sub events, Cloud Storage object notifications, and other Eventarc events.

Eventarc is the routing layer. It delivers Cloud Audit Logs events, Pub/Sub messages, and direct events to Cloud Run, Cloud Run functions, GKE, or Workflows.

```bash
# Deploy a function (2nd gen / Cloud Run functions) on a bucket finalize event
gcloud functions deploy on_upload \
  --gen2 \
  --runtime=python312 \
  --region="$REGION" \
  --source=. \
  --entry-point=handle \
  --trigger-event-filters="type=google.cloud.storage.object.v1.finalized" \
  --trigger-event-filters="bucket=BUCKET" \
  --service-account="$SA_EMAIL"

# Pub/Sub triggered function
gcloud functions deploy on_message \
  --gen2 \
  --runtime=python312 \
  --region="$REGION" \
  --source=. \
  --entry-point=handle \
  --trigger-topic=orders \
  --service-account="$SA_EMAIL"

# The same idea as a Cloud Run service plus an Eventarc trigger
gcloud eventarc triggers create bucket-to-run \
  --location="$REGION" \
  --destination-run-service=worker \
  --destination-run-region="$REGION" \
  --event-filters="type=google.cloud.storage.object.v1.finalized" \
  --event-filters="bucket=BUCKET" \
  --service-account="$SA_EMAIL"
```

1st gen Cloud Functions is the legacy product: different event model, shorter timeouts, no concurrency like Cloud Run. If an old stem says Cloud Functions and the new stem says Cloud Run functions, they mean the same job: a small handler. Prefer gen2 flags.

Direct events versus audit-log events: object finalize is a direct Storage event. “Any API call” is often an audit-log Eventarc trigger, which means Data Access logs must be on or you only see Admin Activity.

## App Engine

App Engine is PaaS. Two environments:

| | Standard | Flexible |
| --- | --- | --- |
| Scale to zero | Yes | No. At least one instance |
| Runtimes | Specific language versions in a sandbox | Custom container |
| Local disk writes | Sandbox limits | Yes |
| Startup | Fast | Slower |
| Network | App Engine-specific, serverless VPC access for private resources | Closer to Compute Engine |

Versions and traffic splitting are built in. Services are components inside one app. `app.yaml` is the config. Cron, task queues, and datastore coupling are why old apps stay here. New apps should be Cloud Run unless the stem is an existing App Engine app.

```bash
gcloud app create --region="$REGION"
gcloud app deploy app.yaml
gcloud app versions list
gcloud app services set-traffic default --splits=v2=0.1,v1=0.9
gcloud app browse
```

Standard cannot open arbitrary outbound sockets in the oldest sandboxes. If the stem says WebSocket or a custom binary, Flexible or Cloud Run is the answer. Today Cloud Run is the better default even for WebSockets.

## Related products

| Product | Role |
| --- | --- |
| Artifact Registry | Images and language packages the service pulls |
| Serverless VPC Access / Direct VPC egress | Reach private IPs (Cloud SQL, Memorystore) without a public IP |
| Cloud SQL connector | Preferred path to Cloud SQL from Cloud Run |
| Secret Manager | Environment secrets, mounted as env or volumes |
| Cloud Build | Builds the source deploy |
| API Gateway or Apigee | In front, when the stem is API keys, quotas, and an API product. Cloud Run’s URL is not an API management layer. |
| Buildpacks | Source-to-image used by `gcloud run deploy --source` |

```bash
gcloud compute networks vpc-access connectors create run-conn \
  --region="$REGION" --network=NETWORK --range=10.8.0.0/28

gcloud run deploy web --region="$REGION" \
  --image=IMAGE \
  --vpc-connector=run-conn \
  --vpc-egress=private-ranges-only
```

Direct VPC egress is the newer attachment and is preferred when the exam stem is current. The connector still appears in older material.

## Exercises

1. A stateless API, container already built, traffic at night is zero, no Kubernetes. Which product?
2. Ten thousand independent thumbnail jobs from a bucket upload. Which trigger and which runtime?
3. You must shift 10% of users to a new revision and keep 90% on the old one. Which command family?
4. The service must read Memorystore, which has only a private IP. What do you add?
5. An existing `app.yaml` Python 2 app must keep its current versioning model through a migration quarter. Where does it stay for that quarter?

### Answers

1. Cloud Run service.
2. Cloud Run functions gen2, or a Cloud Run service, with an Eventarc or Storage finalize trigger. A GKE cluster per upload is the trap.
3. `gcloud run services update-traffic` with revision splits. App Engine’s equivalent is `gcloud app services set-traffic` if it is App Engine.
4. Direct VPC egress or a Serverless VPC Access connector, plus the Serverless VPC Access user role and a firewall path. Do not give Memorystore a public IP.
5. App Engine, until they containerize. The target after that quarter is Cloud Run.
