# Command index

Placeholders: `PROJECT_ID`, `REGION`, `ZONE`, `SA` (service account email), `NETWORK`. Flags change. `gcloud help COMMAND` is the authority if a lab fails.

## Identity and projects

```bash
gcloud auth login
gcloud auth application-default login
gcloud config set project PROJECT_ID
gcloud services enable SERVICE.googleapis.com
gcloud services list --enabled
gcloud projects add-iam-policy-binding PROJECT_ID --member=group:g@example.com --role=ROLE
gcloud projects get-iam-policy PROJECT_ID
gcloud iam roles create NAME --project=PROJECT_ID --permissions=P1,P2 --stage=GA
gcloud iam service-accounts create NAME
gcloud iam service-accounts add-iam-policy-binding SA --member=user:a@example.com --role=roles/iam.serviceAccountTokenCreator
gcloud auth print-access-token --impersonate-service-account=SA
gcloud billing projects link PROJECT_ID --billing-account=BILLING_ACCOUNT
gcloud resource-manager org-policies describe CONSTRAINT --project=PROJECT_ID
```

## Compute Engine

```bash
gcloud compute instances create NAME --zone=ZONE --machine-type=e2-medium
gcloud compute instances list
gcloud compute ssh NAME --zone=ZONE --tunnel-through-iap
gcloud compute disks snapshot DISK --zone=ZONE --snapshot-names=SNAP
gcloud compute snapshots delete SNAP
gcloud compute images create NAME --source-snapshot=SNAP
gcloud compute instance-templates create TPL --machine-type=e2-medium
gcloud compute instance-groups managed create MIG --region=REGION --template=TPL --size=2
gcloud compute instance-groups managed set-autoscaling MIG --region=REGION --max-num-replicas=4 --target-cpu-utilization=0.6
gcloud compute addresses create NAME --region=REGION
gcloud compute addresses create NAME --global
```

## GKE

```bash
gcloud container clusters create-auto NAME --region=REGION
gcloud container clusters get-credentials NAME --region=REGION
gcloud container node-pools create POOL --cluster=NAME --region=REGION
kubectl get pods,svc,statefulset -A
kubectl apply -f manifest.yaml
kubectl autoscale deployment NAME --min=2 --max=10 --cpu-percent=60
```

## Cloud Run and functions

```bash
gcloud run deploy NAME --source=. --region=REGION
gcloud run services update-traffic NAME --region=REGION --to-revisions=REV=10
gcloud run jobs execute NAME --region=REGION
gcloud functions deploy NAME --gen2 --runtime=python312 --region=REGION --trigger-topic=TOPIC
gcloud eventarc triggers create NAME --location=REGION --destination-run-service=SVC
```

## Network

```bash
gcloud compute networks create VPC --subnet-mode=custom
gcloud compute networks subnets create SUB --network=VPC --region=REGION --range=10.0.0.0/20 --enable-private-ip-google-access
gcloud compute networks subnets expand-ip-range SUB --region=REGION --prefix-length=19
gcloud compute firewall-rules create NAME --network=VPC --direction=INGRESS --action=ALLOW --rules=tcp:443
gcloud compute routers create R --network=VPC --region=REGION
gcloud compute routers nats create NAT --router=R --region=REGION --auto-allocate-nat-external-ips --nat-all-subnet-ip-ranges
gcloud compute vpn-gateways create GW --network=VPC --region=REGION
gcloud compute networks peerings create PEER --network=VPC --peer-network=OTHER --peer-project=PROJECT
gcloud compute shared-vpc enable HOST_PROJECT
gcloud dns managed-zones create ZONE --dns-name=example.com. --visibility=private --networks=VPC
gcloud network-management connectivity-tests create NAME --destination-port=443 --protocol=TCP
```

## Load balancer and Armor (global external application, shortened)

```bash
gcloud compute health-checks create http HC --port=80
gcloud compute backend-services create BES --global --health-checks=HC --load-balancing-scheme=EXTERNAL_MANAGED
gcloud compute url-maps create MAP --default-service=BES
gcloud compute target-http-proxies create PROXY --url-map=MAP
gcloud compute forwarding-rules create FR --global --target-http-proxy=PROXY --ports=80
gcloud compute security-policies create POL
gcloud compute backend-services update BES --global --security-policy=POL
```

## Storage and data

```bash
gcloud storage buckets create gs://BUCKET --location=REGION --uniform-bucket-level-access
gcloud storage cp FILE gs://BUCKET/path
gcloud storage buckets update gs://BUCKET --lifecycle-file=life.json --versioning
gsutil cp FILE gs://BUCKET/path
bq mk --dataset --location=REGION PROJECT:DATASET
bq query --use_legacy_sql=false 'SELECT 1'
bq load --source_format=CSV DATASET.TABLE gs://BUCKET/file.csv
bq ls -j -a -n 10
gcloud sql instances create NAME --database-version=POSTGRES_16 --region=REGION --tier=db-custom-2-7680
gcloud sql backups create --instance=NAME
gcloud alloydb clusters create NAME --region=REGION
gcloud spanner instances create NAME --config=regional-REGION --processing-units=100
gcloud firestore databases create --location=REGION --type=firestore-native
gcloud firestore export gs://BUCKET/prefix
gcloud bigtable instances create NAME --cluster=C --cluster-zone=ZONE --instance-type=PRODUCTION
gcloud redis instances create NAME --size=1 --region=REGION --tier=STANDARD
gcloud pubsub topics create TOPIC
gcloud pubsub subscriptions create SUB --topic=TOPIC
gcloud dataflow jobs list --region=REGION --status=active
gcloud dataproc clusters create NAME --region=REGION
gcloud transfer jobs list
```

## Security and operations

```bash
gcloud kms keyrings create RING --location=REGION
gcloud kms keys create KEY --keyring=RING --location=REGION --purpose=encryption
gcloud secrets create NAME --data-file=-
gcloud logging read 'severity>=ERROR' --limit=20 --freshness=1d
gcloud logging sinks create SINK DESTINATION --log-filter=FILTER
gcloud logging metrics create NAME --log-filter=FILTER
gcloud monitoring uptime list
gcloud artifacts repositories create REPO --repository-format=docker --location=REGION
gcloud artifacts docker images scan IMAGE
gcloud builds submit --tag IMAGE
gcloud deploy releases create REL --delivery-pipeline=PIPE --region=REGION
```

## AI

```bash
gcloud services enable aiplatform.googleapis.com
gcloud ai models list --region=REGION
gcloud ai pipelines list --region=REGION
```

Prediction calls are client libraries. Enable each prebuilt API (`vision.googleapis.com`, `documentai.googleapis.com`, and the others in the AI chapter) before you call it.
