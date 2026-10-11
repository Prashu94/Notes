# Lab 06 — Bucket lifecycle and BigQuery

## Goal

Uniform bucket, a lifecycle file, a partitioned table, a load job, a query that prunes the partition.

## Steps

```bash
gcloud services enable bigquery.googleapis.com
BUCKET="${PROJECT_ID}-lab-lake"
gcloud storage buckets create "gs://${BUCKET}" --location="$REGION" \
  --uniform-bucket-level-access

cat > /tmp/life.json << 'EOF'
{"rule":[{"action":{"type":"Delete"},"condition":{"age":30}}]}
EOF
gcloud storage buckets update "gs://${BUCKET}" --lifecycle-file=/tmp/life.json
gcloud storage buckets describe "gs://${BUCKET}" --format="yaml(lifecycle)"

printf 'event_date,user_id,kind\n2026-10-01,1,click\n2026-10-02,2,view\n' > /tmp/events.csv
gcloud storage cp /tmp/events.csv "gs://${BUCKET}/in/events.csv"

bq mk --dataset --location="$REGION" "${PROJECT_ID}:lab"
bq query --use_legacy_sql=false \
  "CREATE TABLE lab.events (
     event_date DATE,
     user_id INT64,
     kind STRING
   ) PARTITION BY event_date"

bq load --source_format=CSV --skip_leading_rows=1 \
  lab.events "gs://${BUCKET}/in/events.csv" \
  event_date:DATE,user_id:INT64,kind:STRING

bq query --use_legacy_sql=false \
  'SELECT kind, COUNT(*) c FROM `'"${PROJECT_ID}"'.lab.events`
   WHERE event_date = "2026-10-01" GROUP BY kind'

bq ls -j -a -n 3
```

## Cleanup

```bash
bq rm -r -f -d "${PROJECT_ID}:lab"
gcloud storage rm --recursive "gs://${BUCKET}"
gcloud storage buckets delete "gs://${BUCKET}"
```
