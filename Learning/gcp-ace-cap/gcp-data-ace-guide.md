# Google Cloud Certified Associate Cloud Engineer (ACE) - Big Data & AI Guide

## 1. BigQuery (Serverless Data Warehouse)

### 1.1 Core Concepts
*   **Dataset**: Top-level container for tables and views. Controls access (IAM).
*   **Table**: Contains the data. Schema-defined.
*   **View**: Virtual table defined by a SQL query.
*   **Job**: Any action (Query, Load, Export, Copy).

### 1.2 Loading Data
*   **Formats**: CSV, JSON (Newline Delimited), Avro (Preferred for speed), Parquet, ORC.
*   **Sources**: Cloud Storage, Local file, Google Drive, Bigtable.
*   **CLI Command**:
    ```bash
    bq load \
        --source_format=CSV \
        --autodetect \
        my_dataset.my_table \
        gs://my-bucket/data.csv
    ```

### 1.3 Querying
*   **Standard SQL**: The default SQL dialect (ANSI compliant).
*   **CLI Command**:
    ```bash
    bq query --use_legacy_sql=false \
        'SELECT name, count(*) FROM `my_dataset.my_table` GROUP BY name'
    ```
*   **External Tables (Federated Queries)**: Query data directly in GCS/Bigtable/Cloud SQL without loading it.

## 2. Pub/Sub (Messaging)

### 2.1 Concepts
*   **Topic**: A named resource to which messages are sent by publishers.
*   **Subscription**: A named resource representing the stream of messages from a single, specific topic, to be delivered to the subscribing application.
*   **Message**: The data moving through the service.

### 2.2 Subscription Types
1.  **Pull**: Subscriber requests messages. Best for high throughput, batch processing.
2.  **Push**: Pub/Sub sends messages to an HTTP endpoint (e.g., Cloud Run, App Engine). Best for real-time, serverless.
3.  **BigQuery Subscription**: Writes directly to a BigQuery table.
4.  **Cloud Storage Subscription**: Writes directly to a GCS bucket.

**Create Topic & Subscription:**
```bash
gcloud pubsub topics create my-topic
gcloud pubsub subscriptions create my-sub --topic=my-topic
```

## 3. Dataflow (Stream & Batch Processing)

### 3.1 Concepts
*   **Apache Beam**: The SDK used to write pipelines (Java, Python, Go).
*   **Unified Model**: Same code for Batch (Bounded) and Streaming (Unbounded) data.
*   **Fully Managed**: Auto-scaling (Horizontal), Dynamic Work Rebalancing.

### 3.2 Templates
*   **Classic Templates**: Staged on GCS.
*   **Flex Templates**: Packaged as a Docker container.
*   **Use Case**: Run standard jobs without writing code (e.g., "Pub/Sub to BigQuery", "GCS to BigQuery").

**Run a Template:**
```bash
gcloud dataflow jobs run my-job \
    --gcs-location gs://dataflow-templates/latest/PubSub_to_BigQuery \
    --region us-central1 \
    --parameters \
        inputTopic=projects/my-project/topics/my-topic,\
        outputTableSpec=my-project:dataset.table
```

## 4. Dataproc (Managed Hadoop/Spark)
*   **Concept**: Lift-and-shift Hadoop/Spark clusters to GCP.
*   **Ephemeral Clusters**: Create cluster -> Run Job -> Delete Cluster. (Cost effective).
*   **Integration**: Uses GCS instead of HDFS (Connector) for storage separation.

**Create Cluster:**
```bash
gcloud dataproc clusters create my-cluster \
    --region us-central1 \
    --master-machine-type n1-standard-2 \
    --worker-machine-type n1-standard-2 \
    --num-workers 2
```
