# Google Cloud BigQuery ACE Guide

## 1. Overview
BigQuery is a fully managed, serverless, highly scalable enterprise data warehouse. It separates storage and compute, allowing them to scale independently.

### Key Features
- **Serverless:** No infrastructure to manage.
- **SQL Interface:** Supports ANSI-standard SQL (GoogleSQL).
- **Storage & Compute Separation:** Cost-effective and scalable.
- **Real-time Analytics:** Supports streaming ingestion.
- **Built-in ML:** BigQuery ML for machine learning models using SQL.

## 2. Managing Resources (Datasets & Tables)

### Creating a Dataset
Datasets are top-level containers for tables and views.
```bash
# Create a dataset in a specific location
bq mk --location=US --dataset my_project:my_dataset
```

### Creating a Table
Tables contain the actual data.
```bash
# Create a table with a schema
bq mk --table my_dataset.my_table name:STRING,age:INTEGER,joined:DATE

# Create a table from a file (CSV)
bq load --source_format=CSV --skip_leading_rows=1 \
  my_dataset.my_table ./data.csv \
  name:STRING,age:INTEGER,joined:DATE
```

### Managing Tables
```bash
# List tables in a dataset
bq ls my_dataset

# Show table schema and details
bq show my_dataset.my_table

# Delete a table
bq rm -t my_dataset.my_table
```

## 3. Loading Data

### Batch Loading
Load data from Cloud Storage or local files. Supported formats: Avro, Parquet, ORC, CSV, JSON.
```bash
# Load from GCS (Autodetect schema)
bq load --autodetect --source_format=CSV \
  my_dataset.my_table \
  gs://my-bucket/data.csv
```

### Streaming Inserts
Insert data row-by-row for real-time availability.
- **API:** `tabledata.insertAll`
- **Storage Write API:** High-throughput streaming.

### External Tables (Federated Queries)
Query data directly in Cloud Storage, Bigtable, or Cloud SQL without loading it.
```sql
-- Create an external table definition
CREATE EXTERNAL TABLE my_dataset.external_table
OPTIONS (
  format = 'CSV',
  uris = ['gs://my-bucket/data.csv']
);
```

## 4. Querying Data

### Using `bq` CLI
```bash
# Run a query
bq query --use_legacy_sql=false \
  'SELECT name FROM my_dataset.my_table WHERE age > 30'

# Run a dry run to estimate costs
bq query --dry_run --use_legacy_sql=false \
  'SELECT * FROM my_dataset.my_table'
```

### Interactive vs. Batch Queries
- **Interactive:** Executed immediately (default).
- **Batch:** Queued and executed when resources are available (use `--batch` flag).

## 5. Partitioning & Clustering (Operational)

### Partitioned Tables
Divides a table into segments (partitions) to improve query performance and reduce costs.
- **Ingestion Time:** Partitioned by load time (`_PARTITIONTIME`).
- **Time-unit Column:** Partitioned by a `DATE`, `TIMESTAMP`, or `DATETIME` column.
- **Integer Range:** Partitioned by an integer column.

```bash
# Create a partitioned table
bq mk --table \
  --time_partitioning_type=DAY \
  --time_partitioning_field=joined \
  my_dataset.partitioned_table \
  name:STRING,joined:DATE
```

### Clustered Tables
Sorts data within partitions based on one or more columns (up to 4).
```bash
# Create a clustered table
bq mk --table \
  --clustering_fields=category,status \
  my_dataset.clustered_table \
  category:STRING,status:STRING,amount:FLOAT
```

## 6. Security & IAM

### Roles
- **BigQuery Admin:** Full access.
- **BigQuery Data Editor:** Edit tables/datasets.
- **BigQuery Data Viewer:** Read-only access.
- **BigQuery User:** Run queries (needs read access to data).

### Authorized Views
Share query results without giving access to the underlying tables.
1. Create a view.
2. Authorize the view in the source dataset's access controls.

```sql
CREATE VIEW my_dataset.my_view AS
SELECT name, age FROM my_dataset.sensitive_table;
```

## 7. Best Practices (ACE Focus)
- **Use `SELECT *` sparingly:** Only select needed columns to reduce costs.
- **Use Dry Runs:** Estimate query costs before execution.
- **Use Partitioning/Clustering:** Optimize large tables.
- **Expiration:** Set table/partition expiration for temporary data.
