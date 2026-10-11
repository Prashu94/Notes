# Lab 08 — Logs, a sink, a log-based metric

## Goal

Read audit logs, create a sink, create a metric. If the BigQuery dataset does not exist yet, create it and grant the sink writer.

## Steps

```bash
gcloud services enable logging.googleapis.com bigquery.googleapis.com
bq mk --dataset --location="$REGION" "${PROJECT_ID}:lablogs" || true

gcloud logging read 'logName:"clou_audit"' --limit=5 --freshness=7d

gcloud logging sinks create lab-to-bq \
  "bigquery.googleapis.com/projects/${PROJECT_ID}/datasets/lablogs" \
  --log-filter='logName:"clou_audit"'

WRITER=$(gcloud logging sinks describe lab-to-bq --format='value(writerIdentity)')
echo "$WRITER"
# Grant that identity roles/bigquery.dataEditor on dataset lablogs in the console
# or with the BigQuery IAM binding you use in your org.

gcloud logging metrics create lab_errors \
  --description="errors" \
  --log-filter='severity>=ERROR'

gcloud logging metrics list
```

## Cleanup

```bash
gcloud logging sinks delete lab-to-bq --quiet
gcloud logging metrics delete lab_errors --quiet
bq rm -r -f -d "${PROJECT_ID}:lablogs"
```
