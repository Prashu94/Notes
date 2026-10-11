# Lab 09 — Private Cloud SQL

**This bills until you delete the instance.** Skip it if you are conserving credit. A `db-f1-micro` or `db-custom-1-3840` still costs money every hour.

## Goal

Reserve a private services range, peer it, create PostgreSQL with no public IP, list backups settings.

## Steps

```bash
gcloud services enable sqladmin.googleapis.com servicenetworking.googleapis.com

gcloud compute networks describe lab-vpc >/dev/null || \
  gcloud compute networks create lab-vpc --subnet-mode=custom

gcloud compute addresses create lab-google-managed \
  --global --purpose=VPC_PEERING --prefix-length=20 \
  --network=lab-vpc --addresses=10.90.0.0

gcloud services vpc-peerings connect \
  --service=servicenetworking.googleapis.com \
  --ranges=lab-google-managed --network=lab-vpc

gcloud sql instances create lab-db \
  --database-version=POSTGRES_16 \
  --tier=db-custom-1-3840 \
  --region="$REGION" \
  --availability-type=ZONAL \
  --network=projects/$PROJECT_ID/global/networks/lab-vpc \
  --no-assign-ip \
  --backup-start-time=04:00

gcloud sql instances describe lab-db --format="yaml(ipAddresses,settings.backupConfiguration)"
```

Use zonal here only to keep the lab smaller. The exam’s production answer is `--availability-type=REGIONAL`.

## Cleanup

```bash
gcloud sql instances delete lab-db --quiet
gcloud services vpc-peerings delete --network=lab-vpc \
  --service=servicenetworking.googleapis.com --quiet
gcloud compute addresses delete lab-google-managed --global --quiet
```

Do not delete `lab-vpc` if lab 02 still uses it. If this lab created it and nothing else uses it, delete it too.
