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

---

## 8. Data Export

### Export to Cloud Storage

```bash
# Export table to CSV
bq extract \
  --destination_format=CSV \
  my_dataset.my_table \
  gs://my-bucket/export/*.csv

# Export to Parquet (compressed)
bq extract \
  --destination_format=PARQUET \
  --compression=SNAPPY \
  my_dataset.my_table \
  gs://my-bucket/export/*.parquet

# Export to JSON
bq extract \
  --destination_format=NEWLINE_DELIMITED_JSON \
  my_dataset.my_table \
  gs://my-bucket/export/*.json
```

**Limitations:**
- Max 1 GB per file (use wildcards for larger exports)
- Nested/repeated fields require Avro or JSON format

### Export Query Results

```bash
# Export query results
bq query --destination_table=my_dataset.results \
  --use_legacy_sql=false \
  'SELECT * FROM my_dataset.my_table WHERE status = "active"'

bq extract my_dataset.results gs://my-bucket/results/*.csv
```

---

## 9. Jobs and Job Management

### Understanding Jobs

Every operation in BigQuery (load, query, extract, copy) creates a job.

```bash
# List recent jobs
bq ls -j -a -n 10

# Show job details
bq show -j JOB_ID

# Cancel a running job
bq cancel JOB_ID
```

### Job States
- **PENDING**: Queued
- **RUNNING**: Executing
- **DONE**: Completed successfully
- **FAILED**: Failed with errors

### Query Job Example

```bash
# Submit a query job
bq query --use_legacy_sql=false \
  --destination_table=my_dataset.results \
  --batch \
  'SELECT COUNT(*) FROM my_dataset.large_table'

# Check job status
bq wait JOB_ID
```

---

## 10. Cost Management

### Understanding Pricing

**Storage Costs:**
- Active storage: $0.02/GB/month (first 90 days)
- Long-term storage: $0.01/GB/month (after 90 days no modification)

**Query Costs:**
- On-demand: $6.25 per TB processed
- Flat-rate pricing: Reserved slots (e.g., 500 slots = $20,000/month)

**Streaming Inserts:**
- $0.01 per 200 MB

### Cost Optimization Tips

```bash
# Estimate query cost (dry run)
bq query --dry_run --use_legacy_sql=false \
  'SELECT * FROM my_dataset.large_table'
# Output: "This query will process 10.5 GB when run."
# Cost: 10.5 GB / 1024 GB/TB × $6.25 = $0.064

# Use partition filters to reduce scanned data
SELECT * FROM my_dataset.partitioned_table
WHERE date = '2024-01-15'  -- Scans only one partition

# Use clustering for additional optimization
SELECT * FROM my_dataset.clustered_table
WHERE category = 'electronics'  -- Scans only relevant clusters
```

### Query Result Caching

- Results cached for 24 hours (free)
- Cached results returned instantly (no charge)
- Cache invalidated if table changes

```bash
# Disable cache for a query
bq query --nouse_cache --use_legacy_sql=false \
  'SELECT * FROM my_dataset.my_table'
```

---

## 11. Data Transfer and Integration

### Data Transfer Service

Schedule automatic imports from external sources:

```bash
# Create transfer configuration (from GCS)
bq mk --transfer_config \
  --display_name="Daily Import" \
  --data_source=google_cloud_storage \
  --target_dataset=my_dataset \
  --params='{"data_path_template":"gs://my-bucket/daily/*.csv","destination_table_name_template":"daily_data","file_format":"CSV","write_disposition":"WRITE_APPEND"}'
```

**Supported Sources:**
- Cloud Storage
- Google Ads
- Google Ad Manager
- YouTube
- Google Play
- Amazon S3 (via connector)
- Teradata
- Amazon Redshift

### BigQuery Connector for Spark/Hadoop

```python
# PySpark example
df = spark.read \
  .format("bigquery") \
  .option("table", "my_project.my_dataset.my_table") \
  .load()
```

---

## 12. Views and Materialized Views

### Standard Views

Logical views (no data storage):

```sql
CREATE VIEW my_dataset.active_users AS
SELECT user_id, name, email
FROM my_dataset.users
WHERE status = 'active';
```

### Materialized Views

Pre-computed results (stored, periodically refreshed):

```sql
CREATE MATERIALIZED VIEW my_dataset.daily_summary AS
SELECT 
  DATE(timestamp) as date,
  COUNT(*) as event_count,
  SUM(amount) as total_amount
FROM my_dataset.events
GROUP BY date;
```

**Benefits:**
- Faster query performance
- Automatic refresh
- Smart tuning (only changed data recomputed)

**Limitations:**
- Additional storage costs
- Refresh lag (not real-time)
- Limited SQL features (no UDFs, some JOINs restrictions)

---

## 13. Working with Arrays and Structs

### Arrays

```sql
-- Create table with array
CREATE TABLE my_dataset.products (
  product_id INT64,
  tags ARRAY<STRING>
);

-- Insert data
INSERT INTO my_dataset.products VALUES
  (1, ['electronics', 'mobile', 'featured']),
  (2, ['clothing', 'sale']);

-- Query arrays
SELECT product_id, tag
FROM my_dataset.products
CROSS JOIN UNNEST(tags) AS tag
WHERE tag = 'electronics';
```

### Structs (Records)

```sql
-- Create table with struct
CREATE TABLE my_dataset.orders (
  order_id INT64,
  customer STRUCT<
    name STRING,
    email STRING,
    address STRUCT<
      street STRING,
      city STRING
    >
  >
);

-- Query structs
SELECT 
  order_id,
  customer.name,
  customer.address.city
FROM my_dataset.orders
WHERE customer.address.city = 'New York';
```

---

## 14. User-Defined Functions (UDFs)

### JavaScript UDF

```sql
CREATE TEMP FUNCTION multiplyByTwo(x FLOAT64)
RETURNS FLOAT64
LANGUAGE js AS r"""
  return x * 2;
""";

SELECT 
  value,
  multiplyByTwo(value) as doubled
FROM UNNEST([1.5, 2.5, 3.5]) as value;
```

### SQL UDF

```sql
CREATE TEMP FUNCTION isPrime(num INT64)
RETURNS BOOL AS (
  num > 1 AND NOT EXISTS (
    SELECT 1
    FROM UNNEST(GENERATE_ARRAY(2, CAST(SQRT(num) AS INT64))) AS divisor
    WHERE MOD(num, divisor) = 0
  )
);

SELECT number, isPrime(number) as is_prime
FROM UNNEST(GENERATE_ARRAY(1, 20)) AS number;
```

---

## 15. Scheduled Queries

Automate recurring queries:

```bash
# Create scheduled query (runs daily at 9 AM)
bq mk --transfer_config \
  --display_name="Daily Aggregation" \
  --data_source=scheduled_query \
  --target_dataset=my_dataset \
  --schedule="every day 09:00" \
  --params='{
    "query":"INSERT INTO my_dataset.daily_stats SELECT DATE(timestamp) as date, COUNT(*) as count FROM my_dataset.events WHERE DATE(timestamp) = CURRENT_DATE() - 1 GROUP BY date",
    "destination_table_name_template":"daily_stats",
    "write_disposition":"WRITE_APPEND"
  }'
```

**Use Cases:**
- Daily/weekly aggregations
- Data pipeline automation
- Report generation
- Data archival

---

## 16. BigQuery ML (Basics for ACE)

Create ML models using SQL:

```sql
-- Create a linear regression model
CREATE MODEL my_dataset.price_model
OPTIONS(model_type='linear_reg', input_label_cols=['price']) AS
SELECT
  size,
  bedrooms,
  location,
  price
FROM my_dataset.housing_data;

-- Make predictions
SELECT *
FROM ML.PREDICT(MODEL my_dataset.price_model,
  (SELECT 1500 as size, 3 as bedrooms, 'downtown' as location));

-- Evaluate model
SELECT *
FROM ML.EVALUATE(MODEL my_dataset.price_model);
```

---

## 17. Data Quality and Validation

### Table Constraints (Beta)

```sql
-- Create table with primary key
CREATE TABLE my_dataset.users (
  user_id INT64 NOT NULL,
  email STRING NOT NULL,
  PRIMARY KEY (user_id) NOT ENFORCED
);

-- Foreign key constraint
CREATE TABLE my_dataset.orders (
  order_id INT64 NOT NULL,
  user_id INT64 NOT NULL,
  PRIMARY KEY (order_id) NOT ENFORCED,
  FOREIGN KEY (user_id) REFERENCES my_dataset.users(user_id) NOT ENFORCED
);
```

**Note:** Constraints are NOT ENFORCED (documentation only)

### Data Validation Queries

```sql
-- Check for duplicates
SELECT user_id, COUNT(*) as count
FROM my_dataset.users
GROUP BY user_id
HAVING count > 1;

-- Check for nulls in required fields
SELECT COUNT(*) as null_count
FROM my_dataset.users
WHERE email IS NULL;

-- Validate date ranges
SELECT MIN(order_date) as earliest, MAX(order_date) as latest
FROM my_dataset.orders;
```

---

## 18. Monitoring and Logging

### View Query History

```bash
# List recent queries
bq ls -j -a --max_results=50

# Query audit logs
bq query --use_legacy_sql=false '
SELECT
  timestamp,
  principal_email,
  resource.labels.project_id,
  protopayload_auditlog.methodName,
  protopayload_auditlog.resourceName
FROM `my_project.logs.cloudaudit_googleapis_com_data_access`
WHERE resource.type = "bigquery_resource"
  AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
ORDER BY timestamp DESC
LIMIT 100'
```

### Information Schema

```sql
-- View all tables in a dataset
SELECT * FROM my_dataset.INFORMATION_SCHEMA.TABLES;

-- View column information
SELECT * FROM my_dataset.INFORMATION_SCHEMA.COLUMNS
WHERE table_name = 'my_table';

-- View table size and row count
SELECT
  table_name,
  row_count,
  size_bytes / POW(10,9) as size_gb
FROM my_dataset.__TABLES__;
```

---

## 19. Common Operations

### Copy Table

```bash
# Copy table within project
bq cp my_dataset.source_table my_dataset.dest_table

# Copy across projects
bq cp source_project:dataset.table dest_project:dataset.table

# Copy with overwrite
bq cp -f my_dataset.source_table my_dataset.dest_table
```

### Update Table Schema

```bash
# Add a column
bq update my_dataset.my_table schema.json

# schema.json:
# [
#   {"name": "name", "type": "STRING", "mode": "REQUIRED"},
#   {"name": "age", "type": "INTEGER", "mode": "NULLABLE"},
#   {"name": "new_column", "type": "STRING", "mode": "NULLABLE"}
# ]
```

### Table Expiration

```bash
# Set table to expire in 7 days
bq update --expiration 604800 my_dataset.my_table

# Set default expiration for all tables in dataset
bq update --default_table_expiration 604800 my_dataset
```

---

## 20. Troubleshooting Common Issues

### Issue 1: "Quota exceeded" error

**Solution:**
- Use flat-rate pricing for predictable costs
- Optimize queries to scan less data
- Use partitioned/clustered tables
- Schedule batch queries during off-peak

### Issue 2: Slow query performance

**Solution:**
```bash
# Get query execution plan
bq query --use_legacy_sql=false --dry_run 'YOUR_QUERY'

# Check Query Explanation in Console
# Look for:
# - Full table scans (add WHERE filters)
# - Large shuffles (optimize JOINs)
# - Skewed data (use approximate aggregation)
```

### Issue 3: "Resources exceeded" error

**Solution:**
- Break large query into smaller chunks
- Use approximate aggregation functions (APPROX_COUNT_DISTINCT)
- Reduce result size with LIMIT
- Use materialized views for complex aggregations

### Issue 4: Access denied errors

**Solution:**
```bash
# Check dataset permissions
bq show --format=prettyjson my_dataset

# Grant access
bq update --source my_dataset \
  --add_access_entry "role=READER,userByEmail:user@example.com"
```

---

## 21. ACE Exam Tips

### Key Concepts to Remember

1. **BigQuery is serverless**: No infrastructure management
2. **Separation of storage and compute**: Scale independently
3. **Pricing model**: Pay for storage + queries (data processed)
4. **Partitioning reduces costs**: Scan less data
5. **Clustering improves performance**: Within partitions
6. **Slots**: Units of computational capacity
7. **Datasets are regional**: Cannot change after creation
8. **Jobs are atomic**: Load, query, extract, copy
9. **Views don't store data**: Logical only
10. **Materialized views do store data**: Pre-computed

### Common Commands

```bash
# Create dataset
bq mk --location=US my_dataset

# Load data
bq load --autodetect my_dataset.table gs://bucket/file.csv

# Query
bq query --use_legacy_sql=false 'SELECT * FROM dataset.table'

# Export
bq extract dataset.table gs://bucket/output*.csv

# Copy
bq cp dataset.source dataset.dest

# Show schema
bq show dataset.table

# Delete
bq rm -t dataset.table
bq rm -r -f dataset  # Delete dataset and all tables
```

### Cost Optimization Strategies

1. **Use SELECT specific columns** instead of SELECT *
2. **Filter early** with WHERE clauses
3. **Use partition filters**: `WHERE _PARTITIONDATE = '2024-01-15'`
4. **Enable query result caching** (default)
5. **Use approximate functions**: APPROX_COUNT_DISTINCT, APPROX_QUANTILES
6. **Materialize frequently used aggregations**
7. **Use flat-rate pricing for predictable workloads**
8. **Set table expiration for temporary data**

### Security Best Practices

1. **Use IAM roles** for access control
2. **Enable authorized views** for row-level security
3. **Use VPC Service Controls** for data exfiltration prevention
4. **Enable audit logging** for compliance
5. **Encrypt with CMEK** for sensitive data
6. **Use column-level security** for PII data
7. **Implement data retention policies**

---

**End of BigQuery ACE Guide**
