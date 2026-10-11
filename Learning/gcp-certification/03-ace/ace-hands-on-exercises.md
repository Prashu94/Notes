# ACE section drills

Do these after the service chapters. Write the command or the product before you read the answer. Assume `PROJECT_ID`, `REGION=us-central1`, `ZONE=us-central1-a`, and a custom-mode VPC named `prod` where a network is required.

## Section 1 — environment

1. Enable Cloud Run, Artifact Registry, and Cloud SQL in the current project.
2. Grant `roles/logging.viewer` to `group:auditors@example.com` on the project.
3. Link the project to a billing account.
4. Show CPU quota in the region.
5. A budget email fired. Did Google stop the VMs?

### Answers

```bash
gcloud services enable run.googleapis.com artifactregistry.googleapis.com sqladmin.googleapis.com
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="group:auditors@example.com" --role="roles/logging.viewer"
gcloud billing projects link "$PROJECT_ID" --billing-account="$BILLING_ACCOUNT"
gcloud compute regions describe "$REGION" --format="yaml(quotas)"
```

5. No. Budgets alert. They do not stop resources unless you built automation.

## Section 3 — deploy

6. Create a Spot e2-standard-2 VM named `batch` with OS Login, no public IP story yet (omit access config only if you also have IAP; for this drill a normal VM is fine). Use Debian 12.
7. Create a regional MIG `web` of size 2 from template `web-tpl` in zones a and b.
8. Create an Autopilot cluster `app` in the region.
9. Deploy Cloud Run service `web` from an image, private, max 10 instances.
10. Create a gen2 function `on_obj` on topic `uploads`.
11. Create a Postgres 16 Cloud SQL instance `app-db`, regional HA, private network `prod`, no public IP.
12. Create a bucket with uniform access in the region.
13. Create a custom-mode VPC and one subnet `10.10.0.0/20` with Private Google Access.
14. Allow ingress tcp/443 to service account `SA_EMAIL` from `10.0.0.0/8`.

### Answers

```bash
gcloud compute instances create batch --zone="$ZONE" \
  --machine-type=e2-standard-2 --provisioning-model=SPOT \
  --instance-termination-action=STOP \
  --image-family=debian-12 --image-project=debian-cloud \
  --metadata=enable-oslogin=TRUE

gcloud compute instance-groups managed create web --region="$REGION" \
  --template=web-tpl --size=2 --zones="${REGION}-a,${REGION}-b"

gcloud container clusters create-auto app --region="$REGION"

gcloud run deploy web --image=IMAGE --region="$REGION" \
  --no-allow-unauthenticated --max-instances=10

gcloud functions deploy on_obj --gen2 --runtime=python312 --region="$REGION" \
  --source=. --entry-point=handle --trigger-topic=uploads

gcloud sql instances create app-db --database-version=POSTGRES_16 \
  --tier=db-custom-2-7680 --region="$REGION" --availability-type=REGIONAL \
  --network=projects/$PROJECT_ID/global/networks/prod --no-assign-ip

gcloud storage buckets create gs://$PROJECT_ID-lab --location="$REGION" \
  --uniform-bucket-level-access

gcloud compute networks create prod --subnet-mode=custom
gcloud compute networks subnets create app --network=prod --region="$REGION" \
  --range=10.10.0.0/20 --enable-private-ip-google-access

gcloud compute firewall-rules create allow-https --network=prod \
  --direction=INGRESS --action=ALLOW --rules=tcp:443 \
  --source-ranges=10.0.0.0/8 --target-service-accounts="$SA_EMAIL"
```

## Section 4 — operate

15. SSH to `batch` using IAP.
16. Snapshot disk `batch` (boot disk name defaults to the instance name).
17. Add a subnet `batchnet` `10.30.0.0/24` and expand `app` from /20 to /19.
18. Reserve a regional static address `web-ip`.
19. Create Cloud NAT on router `nat-rtr` for all subnets.
20. Move 25% of Cloud Run traffic to revision `web-00008` and leave the rest on `web-00007`.
21. List running Dataflow jobs and recent BigQuery jobs.
22. Read Cloud Run errors from the last day.
23. Create a log sink of audit logs to BigQuery dataset `logs`.

### Answers

```bash
gcloud compute ssh batch --zone="$ZONE" --tunnel-through-iap
gcloud compute disks snapshot batch --zone="$ZONE" --snapshot-names=batch-snap
gcloud compute networks subnets create batchnet --network=prod --region="$REGION" --range=10.30.0.0/24
gcloud compute networks subnets expand-ip-range app --region="$REGION" --prefix-length=19
gcloud compute addresses create web-ip --region="$REGION"
gcloud compute routers nats create nat-1 --router=nat-rtr --region="$REGION" \
  --auto-allocate-nat-external-ips --nat-all-subnet-ip-ranges
gcloud run services update-traffic web --region="$REGION" \
  --to-revisions=web-00008=25,web-00007=75
gcloud dataflow jobs list --region="$REGION" --status=active
bq ls -j -a -n 5
gcloud logging read 'resource.type="cloud_run_revision" AND severity>=ERROR' --freshness=1d --limit=20
gcloud logging sinks create to-bq \
  bigquery.googleapis.com/projects/$PROJECT_ID/datasets/logs \
  --log-filter='logName:"clou_audit"'
```

Remember to grant the sink’s writer identity access to the dataset.

## Section 5 — access

24. Create service account `jobs` and let `user:ada@example.com` impersonate it.
25. Create a custom role `restarter` with `compute.instances.get` and `compute.instances.reset`.

### Answers

```bash
gcloud iam service-accounts create jobs --display-name=jobs
gcloud iam service-accounts add-iam-policy-binding jobs@${PROJECT_ID}.iam.gserviceaccount.com \
  --member="user:ada@example.com" --role="roles/iam.serviceAccountTokenCreator"
gcloud iam roles create restarter --project="$PROJECT_ID" \
  --title=Restarter \
  --permissions=compute.instances.get,compute.instances.reset --stage=GA
```

## Mixed choices

26. Object read about once a month. Storage class?
27. Global users, HTTPS, WAF. Load balancer?
28. Pods, no node patching. GKE mode?
29. SQL Server, no schema change, one region. Database?
30. Fan-out of one event to three workers. Pub/Sub shape?

### Answers

26. Nearline.
27. Global external Application Load Balancer plus Cloud Armor. Premium tier.
28. Autopilot, regional if it is production.
29. Cloud SQL for SQL Server.
30. One topic, three subscriptions.
