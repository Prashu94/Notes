# Cloud Run, functions, and App Engine deep dive

Read `03-cloud-run-and-app-engine.md` first. This file is the settings those questions turn on.

## Cloud Run service settings

| Setting | What it actually does | Wrong assumption |
| --- | --- | --- |
| CPU and memory | Sized per instance, not per request | “1 vCPU means one request” |
| Concurrency | How many requests share one instance | Default is many, not 1. Set 1 only when the app is not thread-safe. |
| Min instances | Keep this many warm. You pay while they are idle. | Scale-to-zero is gone for that floor |
| Max instances | Cap. Extra requests wait or fail. Protects a database. | It is not a quota increase |
| Request timeout | Max time for one request. Jobs have their own task timeout. | It is not infinite |
| CPU is only allocated during request processing | You pay for CPU while a request runs. Background threads die between requests. | A background poller will stall |
| CPU always allocated | CPU stays on for the life of the instance. Needed for some background work. Costs more. | Not the cheap default |
| Startup CPU boost | Extra CPU during cold start | Does not change steady-state price much |
| Session affinity | Best-effort stickiness to an instance | Not a session store. Use Memorystore or a database. |
| Ingress all | Internet and internal | Default public pattern |
| Ingress internal | Only from the VPC and other Google Cloud services you allow | Partners on the internet cannot call it |
| Ingress internal and cloud load balancing | VPC plus the load balancer, not the raw `run.app` URL from the internet | The way you put Armor in front |
| Authentication | IAM `roles/run.invoker`. `--allow-unauthenticated` binds `allUsers`. | “Internal ingress” is not IAM |
| Service account | The identity of the running code | Not the identity of the caller |
| Execution environment gen2 | Current default. NFS, more CPU and memory, the sandbox you design for. | Gen1 is the legacy sandbox |

```bash
gcloud run deploy api \
  --image="${REGION}-docker.pkg.dev/${PROJECT_ID}/apps/api:1" \
  --region="$REGION" \
  --service-account="$SA_EMAIL" \
  --no-allow-unauthenticated \
  --ingress=internal-and-cloud-load-balancing \
  --concurrency=40 \
  --cpu=2 --memory=1Gi \
  --min-instances=1 --max-instances=50 \
  --timeout=300 \
  --cpu-boost \
  --port=8080

# Caller, which is a different service account, gets invoker
gcloud run services add-iam-policy-binding api \
  --region="$REGION" \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/run.invoker"
```

Service-to-service calls use an identity token for the target URL, minted from the caller’s service account. A raw URL with no token gets 403 when the service is private.

## VPC and Cloud SQL from Cloud Run

Direct VPC egress is the current attachment. The connector is the older one. Both put the instance on a subnet so it can reach private IPs.

```bash
gcloud run deploy api --region="$REGION" --image=IMAGE \
  --network=prod --subnet=app \
  --vpc-egress=private-ranges-only
```

`private-ranges-only` sends RFC 1918 to the VPC and public traffic to the internet directly. `all-traffic` forces every packet through the VPC, which is what you want if a Secure Web Proxy or a firewall must see egress.

Cloud SQL: use the built-in Cloud SQL connection (Auth Proxy style) rather than opening a public IP.

```bash
gcloud run deploy api --region="$REGION" --image=IMAGE \
  --add-cloudsql-instances="${PROJECT_ID}:${REGION}:app-db" \
  --set-secrets=DB_PASSWORD=db-password:latest
```

The runtime service account needs `roles/cloudsql.client` and `roles/secretmanager.secretAccessor`.

Volumes: Cloud Storage FUSE and NFS (Filestore) need gen2. They are a read or shared-file path. They do not turn Cloud Run into a POSIX server with a durable local disk. The instance disk is ephemeral.

## Jobs

A job is not a service. Nothing listens. Tasks run, then the execution ends. Use task count and parallelism. Retries are per task. Trigger it from Cloud Scheduler, Workflows, or an Eventarc schedule.

```bash
gcloud run jobs create nightly \
  --image=IMAGE --region="$REGION" \
  --tasks=100 --parallelism=10 \
  --task-timeout=3600 \
  --max-retries=3 \
  --service-account="$SA_EMAIL" \
  --set-env-vars=BUCKET=gs://example

gcloud scheduler jobs create http nightly \
  --location="$REGION" \
  --schedule="0 2 * * *" \
  --uri="https://${REGION}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${PROJECT_ID}/jobs/nightly:run" \
  --http-method=POST \
  --oauth-service-account-email="$SA_EMAIL"
```

If the work is one container and it must scale to zero, a job beats a GKE CronJob you have to patch. If the work is a Beam pipeline, Dataflow still wins.

## Cloud Run functions, gen2 versus gen1

| | Gen2 (Cloud Run functions) | Gen1 (Cloud Functions) |
| --- | --- | --- |
| Built on | Cloud Run and Eventarc | The original functions stack |
| Concurrency | Yes | One request per instance |
| Timeout and instance size | The larger Cloud Run limits | Smaller |
| Traffic splitting, revisions | Yes | Limited |
| Triggers | Eventarc, including Storage, Pub/Sub, Audit Logs | Original trigger types |
| Exam name | Cloud Run functions, and still “Cloud Functions” on some ACE text | Legacy |

```bash
gcloud functions deploy on_finalize --gen2 \
  --runtime=python312 --region="$REGION" \
  --source=. --entry-point=handle \
  --trigger-event-filters=type=google.cloud.storage.object.v1.finalized \
  --trigger-event-filters=bucket=BUCKET \
  --trigger-location="$REGION" \
  --service-account="$SA_EMAIL" \
  --memory=512Mi --timeout=120
```

Audit-log triggers only see events that are logged. Data Access logs are off by default. A trigger on `storage.objects.get` never fires until those logs are enabled. Object-finalize is a direct event and does not need Data Access logs.

Cold starts: min instances, smaller dependencies, and CPU boost. They do not remove a cold start when you scale from zero to a spike above the minimum.

## App Engine, the parts that still show up

One project has one App Engine app, in one region, chosen at `gcloud app create`. You cannot move that region. That constraint alone pushes new work to Cloud Run.

`app.yaml` defines runtime, instance class, scaling, env vars, and handlers.

Standard scaling:

- **Automatic**: scale on request rate, latency, and errors. Can go to zero on standard.
- **Basic**: turns instances on when requests arrive. Simple apps.
- **Manual**: a fixed instance count.

Flexible scaling is automatic with a minimum of 1. You always pay for at least one instance.

Versions are immutable deployments. Traffic split is by version, including cookie or IP splits for sticky canaries. Services are components (`default`, `api`, `worker`) inside the one app. `dispatch.yaml` routes host and path to services.

```bash
gcloud app deploy app.yaml --version=v2 --no-promote
gcloud app services set-traffic default --splits=v2=0.1,v1=0.9
gcloud app versions stop v1
```

`cron.yaml` is Scheduler-like inside App Engine. `queue.yaml` is the older task-queue config. New work uses Cloud Scheduler and Cloud Tasks even if the app stays on App Engine for a quarter.

Standard sandbox limits are why a stem about WebSockets, background threads, or writing local files in the old standard runtime becomes Flexible or Cloud Run. Do not fight the sandbox.

Connecting to Cloud SQL from App Engine uses the Cloud SQL connection on the app, plus the App Engine service account as `cloudsql.client`. Serverless VPC Access if the database is only a private IP and you are not using the built-in connector path.

## Choosing again, with the settings

| Stem detail | Not just the product, the setting |
| --- | --- |
| No cold start on the first morning request | Cloud Run min instances ≥ 1, or App Engine with a resident instance |
| Must not accept internet traffic on the default URL | Ingress internal-and-cloud-load-balancing, plus a load balancer |
| Partner calls it with no Google identity | `--allow-unauthenticated` only if that is intended, or Apigee / IAP in front. Do not confuse those. |
| Protect Cloud SQL from a traffic spike | `max-instances` sized to the connection pool |
| 10% canary | Revision traffic split, not a second project |
| Batch of 100 tasks | Cloud Run job, not a service with a 60-minute HTTP call |

## Exercises

1. The service is private. Another Cloud Run service gets 403. Ingress is `all`. What is missing?
2. A cache warmer thread works in local Docker and dies on Cloud Run between requests. Which CPU setting?
3. You need Cloud Armor on a Cloud Run URL. What sits in front, and what ingress do you set?
4. Object-finalize trigger never runs. The function deployed. Name two checks.
5. Why is “move this App Engine app to `europe-west1`” not a config change?

### Answers

1. `roles/run.invoker` on the caller’s service account, and the caller must send an identity token. Ingress `all` only means the network path exists.
2. CPU always allocated. Request-only CPU freezes the process when no request is active.
3. External Application Load Balancer with a serverless NEG, Armor on that backend service, ingress `internal-and-cloud-load-balancing` so people cannot bypass the load balancer.
4. The trigger region matches the bucket, the function’s service account can be invoked by Eventarc, and the bucket is the one in the filter. Then read the function logs.
5. The App Engine region is fixed at app create. A move is a new app in another project, or a rewrite onto Cloud Run.
