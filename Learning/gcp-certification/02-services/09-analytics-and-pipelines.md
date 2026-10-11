# Analytics, streaming, and pipelines

ACE 3.4 and 4.4 (BigQuery, Pub/Sub, Dataflow, job status). PCA 1.3 data-processing choice and section 2.2.

## Pick a pipeline

| Stem | Product |
| --- | --- |
| Messaging between services, at-least-once, fan-out | Pub/Sub |
| Kafka API specifically | Managed Service for Apache Kafka |
| Unified batch and stream processing, Apache Beam | Dataflow |
| Existing Spark or Hadoop jobs, lift the cluster | Dataproc, or Managed Service for Apache Spark when you want serverless Spark |
| Orchestrate tasks on a schedule with dependencies | Cloud Composer (Managed Service for Apache Airflow), or Workflows if the steps are Google Cloud APIs and the team is not an Airflow shop |
| Visual ETL, non-developer pipeline | Cloud Data Fusion |
| SQL transforms in BigQuery, versioned in git | Dataform |
| Change data capture from a database into BigQuery or Cloud Storage | Datastream |
| Warehouse SQL | BigQuery |
| Dashboards for business users | Looker or Looker Studio |

Pub/Sub Lite was a cheaper zonal product and has been shut down. Do not recommend it. Use Pub/Sub.

## Pub/Sub

A **topic** receives messages. One or more **subscriptions** receive a copy. Pull subscriptions are workers calling the API. Push subscriptions deliver HTTP to Cloud Run or an endpoint. There is also an export subscription toward BigQuery or Cloud Storage.

- At-least-once delivery. Make the consumer idempotent.
- Ordering keys give order per key, not global order.
- Exactly-once delivery is a subscription setting with a narrower API. Do not assume every subscription has it.
- Seek and snapshot rewind a subscription. Dead-letter topics catch poison messages after N deliveries.
- Retention is not a database. Default is days, not years. Long archive is an export to Cloud Storage or BigQuery.

```bash
gcloud pubsub topics create orders
gcloud pubsub subscriptions create orders-workers \
  --topic=orders \
  --ack-deadline=60 \
  --dead-letter-topic=orders-dlq \
  --max-delivery-attempts=5 \
  --enable-message-ordering

gcloud pubsub topics publish orders --message='{"id":1}'
gcloud pubsub subscriptions pull orders-workers --auto-ack --limit=5

# BigQuery subscription: stream messages into a table without a pull worker
gcloud pubsub subscriptions create orders-bq \
  --topic=orders \
  --bigquery-table="${PROJECT_ID}:ops.orders_raw" \
  --use-topic-schema
```

Schemas (Avro or Protobuf) live on the topic. Consumers should not parse an undocumented string if the stem mentions a contract.

## Dataflow

Managed Apache Beam. The same pipeline can run batch or streaming. Autoscaling workers. Streaming Engine. Shuffle is managed.

Use it for windowed aggregations, sessionization, and ETL that is code. Do not use it to move a file from A to B with no transform. Storage Transfer or a BigQuery load is simpler.

Templates exist for common jobs (Pub/Sub to BigQuery, Cloud Storage to BigQuery). A custom job is a JAR or a Python pipeline launched with the runner.

```bash
# Example: official template, Pub/Sub to BigQuery
gcloud dataflow jobs run orders-stream \
  --gcs-location=gs://dataflow-templates/latest/PubSub_to_BigQuery \
  --region="$REGION" \
  --staging-location=gs://$PROJECT_ID-lake/df/staging \
  --parameters inputTopic=projects/$PROJECT_ID/topics/orders,outputTableSpec=${PROJECT_ID}:ops.orders

gcloud dataflow jobs list --region="$REGION" --status=active
gcloud dataflow jobs show JOB_ID --region="$REGION"
gcloud dataflow jobs cancel JOB_ID --region="$REGION"
```

ACE 4.4: you must be able to say whether a job is running, failed, or queued. Streaming jobs stay running. Batch jobs end. A failed streaming job is an incident. Update it with a replacement job and drain, rather than killing it and dropping the subscription backlog without a plan.

Flex templates package the pipeline in a container so the runner does not compile at launch. That is the production packaging answer.

## Dataproc

Managed Hadoop and Spark clusters. Ephemeral clusters save money: create, submit, delete. Use it when the code is already Spark, Hive, or Pig. Use Dataflow when you can write Beam or the workload is streaming-first. Serverless Spark (batches and sessions) removes the cluster for Spark jobs that fit it.

```bash
gcloud dataproc clusters create etl \
  --region="$REGION" --single-node \
  --master-machine-type=e2-standard-4

gcloud dataproc jobs submit pyspark wordcount.py --cluster=etl --region="$REGION"
gcloud dataproc clusters delete etl --region="$REGION"
```

Dataproc Metastore is the managed Hive metastore. Recognize it when several Spark engines must share table metadata.

## BigQuery

Serverless warehouse. Storage and compute are separate. You pay on-demand for bytes scanned, or you buy slot capacity with **editions** (Standard, Enterprise, Enterprise Plus) and reservations. Editions are the capacity model. On-demand is the default for small and spiky work.

Design habits the exam cares about:

- **Partition** large tables (time or integer range) so queries prune.
- **Cluster** on filter columns inside partitions.
- Do not `SELECT *` on a fact table in production SQL.
- External tables over Cloud Storage (and BigLake, Iceberg) when you want the file to stay in the lake.
- Materialized views and BI Engine for repeated aggregates and dashboards.
- Authorized views and column-level security and row-level security for governance.
- Time travel (days) is not a backup forever. Table snapshots and copies are the longer recovery. Dataset copy across regions is a DR pattern.
- Streaming inserts and the Storage Write API land rows quickly. Batch load from Cloud Storage is cheaper for files.
- **BigQuery ML** trains models with SQL. Use it when the team is analysts, not a separate training platform.
- **Vector search** and remote models connect warehouse retrieval to Gemini. PCA AI stems.
- Gemini in BigQuery helps write SQL. It does not replace access control.

```bash
bq mk --dataset --location="$REGION" ${PROJECT_ID}:ops

bq query --use_legacy_sql=false \
  "CREATE TABLE ops.events (
     event_date DATE,
     user_id INT64,
     kind STRING
   )
   PARTITION BY event_date
   CLUSTER BY user_id"

bq load --source_format=CSV --skip_leading_rows=1 \
  ops.events gs://$PROJECT_ID-lake/in/events.csv \
  event_date:DATE,user_id:INT64,kind:STRING

bq query --use_legacy_sql=false \
  'SELECT kind, COUNT(*) c FROM `'"$PROJECT_ID"'.ops.events`
   WHERE event_date = "2026-10-01" GROUP BY kind'

# Job status (ACE 4.4)
bq ls -j -a -n 10
bq show -j JOB_ID
bq cancel JOB_ID

# Scheduled query
bq query --use_legacy_sql=false --schedule='every 24 hours' \
  --display_name='daily rollup' \
  --destination_table=ops.daily \
  --replace \
  'SELECT event_date, COUNT(*) n FROM `'"$PROJECT_ID"'.ops.events` GROUP BY event_date'
```

Slots and reservations:

```bash
bq ls --reservation --project_id="$PROJECT_ID" --location="$REGION"
```

Pick on-demand when the stem is unpredictable small SQL. Pick an edition reservation when the stem is a steady dashboard estate or a need for features that sit in Enterprise (some security and ML features). Do not memorize a price. Know the lever.

**Analytics Hub** shares datasets across orgs without copying. **BigQuery Omni** queries data that stays in another cloud. **Dataplex** is the governance layer: zones, data quality, catalog. Pick Dataplex or a catalog when the stem is “who owns this table and is it trustworthy”, not when the stem is “run this SQL”.

## Orchestration

**Cloud Composer** is Airflow. DAGs, operators, a GKE-backed environment (Composer 2 and 3). Use it when the pipeline is a graph of heterogeneous tasks and the team already speaks Airflow.

**Workflows** is a YAML or JSON state machine for HTTP and Google Cloud APIs, with retries. Lighter than Composer. Use it to chain Cloud Run, functions, and callbacks.

**Cloud Scheduler** is cron that hits HTTP, Pub/Sub, or App Engine. It does not transform data.

**Dataform** compiles SQLX into BigQuery jobs. The analytics engineering answer.

**Cloud Data Fusion** is CDAP, UI pipelines, and connectors. The “analysts build the pipeline in a GUI” answer.

```bash
gcloud composer environments list --locations="$REGION"
gcloud workflows deploy nightly --source=nightly.yaml --location="$REGION"
gcloud workflows run nightly --location="$REGION"
gcloud scheduler jobs create http nightly \
  --location="$REGION" \
  --schedule="0 3 * * *" \
  --uri="https://REGION-run.googleapis.com/..." \
  --oidc-service-account-email="$SA_EMAIL"
```

## Datastream

CDC from MySQL, PostgreSQL, Oracle, SQL Server, and similar into BigQuery, Cloud Storage, or Spanner paths the product supports. Use it for continuous replication with low downtime. Database Migration Service is for migrating the database itself. Datastream is for the data pipeline. They overlap in conversation. The stem’s destination tells you which.

## Looker and Looker Studio

Looker is the semantic model (LookML) and governed BI. Looker Studio is the self-serve dashboard tool (formerly Data Studio). Both query BigQuery. Pick Looker when the stem says governed metrics and embedded analytics. Pick Looker Studio when the stem says a quick dashboard. Gemini in Looker and Gemini in Looker Studio are assistants. They are not the warehouse.

## Exercises

1. Services must fan out an order event to billing, fraud, and email, independently. Which Pub/Sub layout?
2. A Spark jar already runs on-premises. The team will not rewrite it in Beam this quarter. Which product?
3. Analysts scan a 10 TB table daily but always filter on `event_date`. What do you change?
4. A streaming job shows `Failed` in Dataflow and the subscription backlog is growing. What do you look at first?
5. Nightly “run SQL, then call Cloud Run, then send email” with retries, no Airflow skill. Composer or Workflows?

### Answers

1. One topic, three subscriptions. Not three topics the publisher must know about.
2. Dataproc (ephemeral cluster) or serverless Spark if the jar fits. Not Dataflow until they rewrite.
3. Partition by `event_date`. Cluster on the next most common filter. Stop selecting unused columns.
4. The job’s logs in Cloud Logging, then the error on `gcloud dataflow jobs show`. Fix and drain or replace. Do not ack the backlog away.
5. Workflows, triggered by Cloud Scheduler. Composer if they already operate Airflow or the graph is large and heterogeneous.
