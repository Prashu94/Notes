# BigQuery - ACE Practice Questions

## Question 1
You need to load a 50GB CSV file from Cloud Storage into BigQuery. What is the most efficient method?

**A)** Use the BigQuery web UI to upload the file

**B)** Use `bq load` command to load from Cloud Storage

**C)** Stream the data using API insert requests

**D)** Download the file and use `bq load` from local machine

**Correct Answer:** B

**Explanation:**
- Option B is correct because:
  - `bq load` is designed for batch loading from Cloud Storage
  - Efficient for large files
  - Free batch loading (no streaming costs)
  - Automatic schema detection available
  - Can load multiple files in parallel

Load data into BigQuery:
```bash
# Load CSV from Cloud Storage
bq load \
  --source_format=CSV \
  --skip_leading_rows=1 \
  --autodetect \
  mydataset.mytable \
  gs://my-bucket/data.csv

# Load with explicit schema
bq load \
  --source_format=CSV \
  --skip_leading_rows=1 \
  mydataset.users \
  gs://my-bucket/users.csv \
  user_id:INTEGER,name:STRING,email:STRING,created_at:TIMESTAMP

# Load multiple files (wildcard)
bq load \
  --source_format=CSV \
  --autodetect \
  mydataset.logs \
  gs://my-bucket/logs/*.csv

# Load JSON
bq load \
  --source_format=NEWLINE_DELIMITED_JSON \
  --autodetect \
  mydataset.events \
  gs://my-bucket/events.json

# Load Parquet (most efficient)
bq load \
  --source_format=PARQUET \
  mydataset.analytics \
  gs://my-bucket/data.parquet

# Load Avro
bq load \
  --source_format=AVRO \
  mydataset.records \
  gs://my-bucket/data.avro
```

Load job options:
```bash
# Overwrite existing table
bq load --replace \
  mydataset.mytable \
  gs://my-bucket/data.csv

# Append to existing table
bq load --noreplace \
  mydataset.mytable \
  gs://my-bucket/new-data.csv

# Set partitioning while loading
bq load \
  --time_partitioning_field=event_date \
  --time_partitioning_type=DAY \
  mydataset.events \
  gs://my-bucket/events.csv \
  event_date:DATE,user_id:INTEGER,event_type:STRING
```

- Option A is incorrect because:
  - Web UI has file size limits (typically 100 MB)
  - 50GB exceeds web UI capabilities
  - Command-line is required for large files

- Option C is incorrect because:
  - Streaming is for real-time, row-by-row inserts
  - Expensive for large batch loads
  - Much slower than batch loading
  - Streaming costs apply ($0.01/200MB)

- Option D is incorrect because:
  - Downloading 50GB is wasteful
  - Slower (download + upload)
  - Loading from Cloud Storage is direct and faster
  - Unnecessary data transfer

**Loading methods comparison:**
- **Batch load (bq load)**: Large files, free, efficient
- **Streaming inserts**: Real-time, small batches, costs apply
- **BigQuery Data Transfer Service**: Scheduled, automated imports
- **BigQuery Storage Write API**: High-throughput streaming

---

## Question 2
You're running a BigQuery query that processes 5TB of data. You want to estimate the cost before running it. What should you do?

**A)** Run the query with `--dry_run` flag

**B)** Run the query normally and check the bill later

**C)** Use the BigQuery pricing calculator

**D)** Query the INFORMATION_SCHEMA

**Correct Answer:** A

**Explanation:**
- Option A is correct because:
  - `--dry_run` validates query and estimates bytes processed
  - No data is actually queried (no cost)
  - Shows exact bytes that will be scanned
  - Can calculate cost from bytes

Estimate query cost:
```bash
# Dry run to estimate bytes
bq query --dry_run \
  'SELECT * FROM `mydataset.large_table` WHERE date >= "2024-01-01"'

# Output shows:
# Query successfully validated. Assuming the tables are not modified,
# running this query will process 5497558138880 bytes of data.

# Calculate cost:
# On-demand pricing: $5 per TB
# 5.5 TB × $5 = $27.50

# Dry run with more details
bq query --dry_run --format=prettyjson \
  'SELECT user_id, COUNT(*) FROM `mydataset.events` GROUP BY user_id'

# In BigQuery console, see estimated bytes in bottom right before running

# Python example:
from google.cloud import bigquery

client = bigquery.Client()
job_config = bigquery.QueryJobConfig(dry_run=True)

query = """
    SELECT name, COUNT(*) as count
    FROM `bigquery-public-data.usa_names.usa_1910_current`
    GROUP BY name
"""

job = client.query(query, job_config=job_config)
print(f"This query will process {job.total_bytes_processed} bytes")
cost = (job.total_bytes_processed / 1024**4) * 5  # Cost in USD
print(f"Estimated cost: ${cost:.2f}")
```

Cost optimization tips:
```sql
-- Bad: SELECT * scans all columns
SELECT * FROM `mydataset.events` WHERE date = '2024-01-01'

-- Good: SELECT only needed columns
SELECT event_id, user_id, event_type 
FROM `mydataset.events` 
WHERE date = '2024-01-01'

-- Better: Use partitioned tables
SELECT event_id FROM `mydataset.events` 
WHERE _PARTITIONDATE = '2024-01-01'  -- Partition filter

-- Best: Partitioned + clustered
-- Queries only scan relevant partitions and clusters
```

- Option B is incorrect because:
  - No cost preview
  - Could result in unexpected charges
  - No ability to optimize before running

- Option C is incorrect because:
  - Pricing calculator gives general estimates
  - Cannot estimate specific query costs
  - Doesn't analyze your actual query

- Option D is incorrect because:
  - INFORMATION_SCHEMA provides metadata
  - Doesn't estimate query costs
  - Different purpose

**BigQuery Pricing (On-Demand):**
- **Query**: $5 per TB scanned
- **Storage**: $0.02 per GB/month (active), $0.01 per GB/month (long-term)
- **Streaming inserts**: $0.01 per 200 MB
- **Free tier**: 1 TB query/month, 10 GB storage

---

## Question 3
You need to partition a BigQuery table by date to improve query performance and reduce costs. What partitioning strategy should you use for a table with an `event_timestamp` column?

**A)** Partition by integer range on event_id

**B)** Partition by ingestion time (_PARTITIONTIME)

**C)** Partition by DAY on event_timestamp column

**D)** Create separate tables for each day

**Correct Answer:** C

**Explanation:**
- Option C is correct because:
  - Partitioning on date/timestamp column allows time-based filtering
  - Queries with date filters only scan relevant partitions
  - Significantly reduces data scanned = lower cost
  - Better performance for time-range queries

Create partitioned table:
```bash
# Create table partitioned by date column
bq mk --table \
  --schema=event_id:INTEGER,user_id:STRING,event_type:STRING,event_timestamp:TIMESTAMP \
  --time_partitioning_field=event_timestamp \
  --time_partitioning_type=DAY \
  mydataset.events

# With expiration (auto-delete old partitions)
bq mk --table \
  --time_partitioning_field=event_timestamp \
  --time_partitioning_type=DAY \
  --time_partitioning_expiration=7776000 \
  mydataset.events \
  schema.json
# 7776000 seconds = 90 days

# Create partitioned table via SQL
CREATE TABLE mydataset.events (
  event_id INT64,
  user_id STRING,
  event_type STRING,
  event_timestamp TIMESTAMP
)
PARTITION BY DATE(event_timestamp)
OPTIONS(
  partition_expiration_days=90,
  description="User events partitioned by event date"
)

# Query partitioned table (efficient)
SELECT event_type, COUNT(*) as count
FROM `mydataset.events`
WHERE DATE(event_timestamp) BETWEEN '2024-01-01' AND '2024-01-31'
GROUP BY event_type

# Check partition info
SELECT
  partition_id,
  total_rows,
  total_logical_bytes
FROM `mydataset.INFORMATION_SCHEMA.PARTITIONS`
WHERE table_name = 'events'
ORDER BY partition_id DESC
LIMIT 10
```

Partitioning types:
```sql
-- Daily partitioning (most common)
PARTITION BY DATE(event_timestamp)

-- Hourly partitioning
PARTITION BY TIMESTAMP_TRUNC(event_timestamp, HOUR)

-- Monthly partitioning
PARTITION BY DATE_TRUNC(event_date, MONTH)

-- Yearly partitioning
PARTITION BY DATE_TRUNC(event_date, YEAR)

-- Integer range partitioning
PARTITION BY RANGE_BUCKET(customer_id, GENERATE_ARRAY(0, 100000, 10000))
```

- Option A is incorrect because:
  - Integer range partitioning is for  numeric columns (IDs, scores)
  - Doesn't help with time-based queries
  - Not appropriate for timestamp data

- Option B is incorrect because:
  - Ingestion time partitioning uses when data was loaded, not event time
  - Less precise for analytical queries
  - Event timestamp is more accurate for event data

- Option D is incorrect because:
  - Managing separate tables is complex
  - Queries across dates require UNION
  - Partitioned tables are the native solution
  - More operational overhead

**Partitioning Benefits:**
- Reduces data scanned (lower cost)
- Faster queries (less data to process)
- Can set partition expiration (auto-cleanup)
- Easier data management

---

## Question 4
You need to allow users to query BigQuery data but prevent them from exporting or downloading results. What IAM role should you grant?

**A)** `roles/bigquery.dataViewer`

**B)** `roles/bigquery.user`

**C)** `roles/bigquery.jobUser`

**D)** Custom role with only `bigquery.tables.getData` permission

**Correct Answer:** A

**Explanation:**
- Option A is correct because:
  - `bigquery.dataViewer` allows reading table data
  - Does NOT include job creation (cannot export)
  - Cannot create query jobs or export jobs
  - Read-only access to data

BigQuery IAM roles:
```bash
# Grant dataViewer (read-only, no queries)
gcloud projects add-iam-policy-binding my-project \
  --member=user:analyst@example.com \
  --role=roles/bigquery.dataViewer

# Grant at dataset level (more restricted)
bq add-iam-policy-binding \
  --member=user:analyst@example.com \
  --role=roles/bigquery.dataViewer \
  mydataset

# Grant table-level access
bq add-iam-policy-binding \
  --member=user:analyst@example.com \
  --role=roles/bigquery.dataViewer \
  mydataset.sensitive_table
```

Common BigQuery roles:
```bash
# bigquery.admin - Full control
gcloud projects add-iam-policy-binding my-project \
  --member=user:admin@example.com \
  --role=roles/bigquery.admin

# bigquery.dataEditor - Read and modify data
gcloud projects add-iam-policy-binding my-project \
  --member=user:editor@example.com \
  --role=roles/bigquery.dataEditor

# bigquery.dataOwner - Full control of datasets
gcloud projects add-iam-policy-binding my-project \
  --member=user:owner@example.com \
  --role=roles/bigquery.dataOwner

# bigquery.user - Create jobs, query, export
gcloud projects add-iam-policy-binding my-project \
  --member=user:analyst@example.com \
  --role=roles/bigquery.user

# bigquery.jobUser - Submit jobs only
gcloud projects add-iam-policy-binding my-project \
  --member=user:jobuser@example.com \
  --role=roles/bigquery.jobUser
```

- Option B is incorrect because:
  - `bigquery.user` can create query jobs
  - Can run queries and export results
  - Has more permissions than needed

- Option C is incorrect because:
  - `bigquery.jobUser` allows submitting jobs
  - Combined with dataset access, could export data
  - More permissions than dataViewer

- Option D is incorrect because:
  - `bigquery.tables.getData` alone might not be sufficient
  - Need additional permissions to view schemas, metadata
  - dataViewer is the standard role for this use case

**Permission levels:**
- **dataViewer**: Read only, no job execution
- **dataEditor**: Read/write data, no dataset management
- **dataOwner**: Full dataset control
- **user**: Can query and export
- **admin**: Full BigQuery access

---

## Question 5
You need to optimize a BigQuery table for queries that filter by `country` and `product_category`. What should you do?

**A)** Create an index on country and product_category columns

**B)** Cluster the table by country and product_category

**C)** Partition the table by country

**D)** Create separate tables for each country and category

**Correct Answer:** B

**Explanation:**
- Option B is correct because:
  - Clustering organizes data by specified columns
  - Queries filtering on clustered columns scan less data
  - Can have up to 4 clustering columns
  - Works with partitioned tables
  - Automatic organization by BigQuery

Create clustered table:
```sql
-- Create partitioned and clustered table
CREATE TABLE mydataset.sales (
  sale_id INT64,
  sale_date DATE,
  country STRING,
  product_category STRING,
  amount NUMERIC
)
PARTITION BY sale_date
CLUSTER BY country, product_category
OPTIONS(
  description="Sales data partitioned by date, clustered by country and category"
)

-- Insert data
INSERT INTO mydataset.sales VALUES
  (1, '2024-01-15', 'US', 'Electronics', 1000.00),
  (2, '2024-01-15', 'UK', 'Clothing', 500.00),
  (3, '2024-01-16', 'US', 'Electronics', 1500.00)
```

Query optimization with clustering:
```sql
-- Efficient: Uses clustering
SELECT SUM(amount) 
FROM `mydataset.sales`
WHERE country = 'US' AND product_category = 'Electronics'
  AND sale_date BETWEEN '2024-01-01' AND '2024-01-31'
-- Scans minimal data due to partition + clustering

-- Less efficient: Doesn't use clustering
SELECT SUM(amount)
FROM `mydataset.sales`
WHERE amount > 1000
-- Scans more data, clustering doesn't help
```

Modify existing table:
```bash
# Add clustering to existing table
bq update --clustering_fields=country,product_category \
  mydataset.sales

# Remove clustering
bq update --clustering_fields= \
  mydataset.sales
```

Clustering vs Partitioning:
```sql
-- PARTITIONING: Good for time-based filtering
-- Reduces data scanned significantly
-- Max 4,000 partitions

-- CLUSTERING: Good for high-cardinality columns
-- Further reduces data within partitions
-- Up to 4 clustering columns
-- Order matters (most filtered column first)

-- Best practice: Use both!
CREATE TABLE combined (
  event_timestamp TIMESTAMP,
  user_country STRING,
  device_type STRING,
  event_category STRING,
  event_value NUMERIC
)
PARTITION BY DATE(event_timestamp)
CLUSTER BY user_country, device_type, event_category
```

- Option A is incorrect because:
  - BigQuery doesn't support traditional indexes
  - Clustering is the BigQuery equivalent
  - Indexing is not how BigQuery optimizes queries

- Option C is incorrect because:
  - Partitioning by string column (country) is not supported
  - Partitioning is for date/timestamp/integer range columns
  - Wrong optimization strategy

- Option D is incorrect because:
  - Managing multiple tables is complex
  - Queries require UNION across tables
  - Clustering is the native solution

**When to use Clustering:**
- High-cardinality columns (countries, product IDs, categories)
- Frequently used in WHERE clauses
- Combined with partitioning for best results

---

## Question 6
You receive an error "Query exceeded resource limits" in BigQuery. What is the most likely cause and solution?

**A)** Query is too large; break it into smaller queries or use destination table

**B)** Insufficient IAM permissions; grant bigquery.admin role

**C)** Table is too large; delete old data

**D)** Network connectivity issue; retry the query

**Correct Answer:** A

**Explanation:**
- Option A is correct because:
  - Large result sets can exceed memory limits
  - Breaking into smaller chunks helps
  - Writing to destination table bypasses result size limits
  - Can use pagination for large results

Handle large query results:
```bash
# Write results to destination table (no size limit)
bq query \
  --destination_table=mydataset.results \
  --use_legacy_sql=false \
  --replace \
  'SELECT * FROM `mydataset.large_table` WHERE date >= "2024-01-01"'

# Query with pagination (for API/programmatic access)
from google.cloud import bigquery

client = bigquery.Client()
query = "SELECT * FROM `bigquery-public-data.usa_names.usa_1910_current`"

query_job = client.query(query)

# Paginate results
for page in query_job.result().pages:
    for row in page:
        print(row)

# Or store in table
job_config = bigquery.QueryJobConfig(
    destination="mydataset.temp_results",
    write_disposition="WRITE_TRUNCATE"
)
query_job = client.query(query, job_config=job_config)
query_job.result()  # Wait for completion
```

Query optimization:
```sql
-- Bad: Returns huge result set
SELECT * FROM `mydataset.events` 

-- Better: Aggregate to reduce rows
SELECT 
  DATE(event_timestamp) as event_date,
  event_type,
  COUNT(*) as count
FROM `mydataset.events`
GROUP BY event_date, event_type

-- Good: Use LIMIT for testing
SELECT * FROM `mydataset.events` LIMIT 1000

-- Best: Write to destination table
CREATE OR REPLACE TABLE mydataset.filtered_events AS
SELECT * FROM `mydataset.events`
WHERE DATE(event_timestamp) >= '2024-01-01'
```

Other resource limit solutions:
```bash
# For complex queries, use temporary tables
CREATE TEMP TABLE daily_stats AS
SELECT DATE(timestamp) as date, COUNT(*) as count
FROM `mydataset.events` GROUP BY date;

CREATE TEMP TABLE monthly_stats AS
SELECT DATE_TRUNC(date, MONTH) as month, SUM(count) as total
FROM daily_stats GROUP BY month;

SELECT * FROM monthly_stats;

# Use reservation for guaranteed resources
bq mk --reservation \
  --project_id=my-project \
  --location=us \
  --slots=500 \
  my_reservation
```

- Option B is incorrect because:
  - Resource limits are not related to IAM permissions
  - Different error message for permission issues
  - Admin role wouldn't solve resource constraints

- Option C is incorrect because:
  - Table size doesn't cause "resource limits" error
  - Deleting data is drastic and unnecessary
  - Query optimization is the solution

- Option D is incorrect because:
  - Network issues cause different errors
  - Resource limits are server-side BigQuery constraints
  - Retrying won't help

**Common Resource Limits:**
- Result size limits (interactive queries)
- Query complexity (too many JOINs, subqueries)
- Temporary table size
- Solution: Use destination tables, simplify queries

---

## Question 7
You need to grant access to specific columns in a BigQuery table while hiding sensitive columns. What should you use?

**A)** Create a view with only the allowed columns

**B)** Grant column-level permissions using IAM

**C)** Create a separate table with only non-sensitive columns

**D)** Use row-level security policies

**Correct Answer:** A

**Explanation:**
- Option A is correct because:
  - Views can select specific columns
  - Grant access to view, not underlying table
  - Simple and effective column-level security
  - Can add WHERE clauses for additional filtering

Create view for column security:
```sql
-- Original table with sensitive data
CREATE TABLE mydataset.users (
  user_id INT64,
  username STRING,
  email STRING,
  phone STRING,           -- Sensitive
  ssn STRING,             -- Sensitive
  credit_card STRING,     -- Sensitive
  address STRING,
  created_at TIMESTAMP
);

-- Create view with only non-sensitive columns
CREATE VIEW mydataset.users_public AS
SELECT 
  user_id,
  username,
  email,
  address,
  created_at
FROM mydataset.users;

-- Grant access to view only
bq add-iam-policy-binding mydataset.users_public \
  --member=user:analyst@example.com \
  --role=roles/bigquery.dataViewer

-- Analysts can query the view
SELECT * FROM `mydataset.users_public`;
-- Cannot access phone, ssn, credit_card columns
```

Advanced: Authorized views:
```sql
-- Create view in different dataset
CREATE VIEW reporting_dataset.user_summary AS
SELECT 
  user_id,
  username,
  CONCAT(SUBSTR(email, 1, 3), '***@***') as masked_email,
  created_at
FROM source_dataset.users;

-- Authorize view to access source dataset
bq update \
  --source_dataset=reporting_dataset.user_summary \
  source_dataset

-- Users with access to reporting_dataset can query view
-- but cannot directly access source_dataset
```

Combine with row-level security:
```sql
-- View with column AND row filtering
CREATE VIEW mydataset.regional_users AS
SELECT 
  user_id,
  username,
  email,
  created_at
FROM mydataset.users
WHERE region = SESSION_USER();  -- Row-level filtering
-- Plus column filtering (no sensitive fields)
```

- Option B is incorrect because:
  - BigQuery doesn't have column-level IAM permissions
  - Permissions are at table/dataset/project level
  - Views are the standard solution

- Option C is incorrect because:
  - Maintaining duplicate tables is complex
  - Data synchronization issues
  - Views are simpler and automatically up-to-date

- Option D is incorrect because:
  - Row-level security filters rows, not columns
  - Different security mechanism
  - Both can be used together, though

**Column-level Security Options:**
1. **Views**: Select specific columns (recommended)
2. **Authorized Views**: Views in separate dataset
3. **Data Catalog Policy Tags**: Column-level access control (advanced)

---

## Question 8
You need to query data from multiple BigQuery datasets across different projects. What should you use?

**A)** Export data from all datasets to one project

**B)** Use fully-qualified table names in queries

**C)** Create federated queries

**D)** Set up BigQuery Data Transfer Service

**Correct Answer:** B

**Explanation:**
- Option B is correct because:
  - Fully-qualified names allow cross-project queries
  - Format: `project.dataset.table`
  - No data movement needed
  - Simple and efficient

Cross-project queries:
```sql
-- Query table in different project
SELECT * 
FROM `other-project.other_dataset.other_table`
WHERE date >= '2024-01-01'

-- JOIN tables from multiple projects
SELECT 
  a.user_id,
  a.username,
  b.order_count
FROM `project-a.dataset-a.users` a
JOIN `project-b.dataset-b.orders` b
  ON a.user_id = b.user_id

-- UNION data from multiple projects
SELECT event_id, event_type FROM `project-1.events.user_events`
UNION ALL
SELECT event_id, event_type FROM `project-2.events.user_events`
UNION ALL
SELECT event_id, event_type FROM `project-3.events.user_events`

-- Create view combining multiple projects
CREATE VIEW mydataset.all_sales AS
SELECT * FROM `us-project.sales.transactions`
UNION ALL
SELECT * FROM `eu-project.sales.transactions`
UNION ALL
SELECT * FROM `asia-project.sales.transactions`
```

Run cross-project query via bq:
```bash
# Query uses fully-qualified table names
bq query --use_legacy_sql=false \
  'SELECT COUNT(*) FROM `other-project.dataset.table`'

# Save results to local project
bq query --use_legacy_sql=false \
  --destination_table=my-project:mydataset.results \
  'SELECT * FROM `other-project.dataset.table`'
```

Required permissions:
```bash
# Grant access to dataset in other project
# In other-project:
bq add-iam-policy-binding \
  --member=user:analyst@example.com \
  --role=roles/bigquery.dataViewer \
  other_dataset

# Or grant at project level
gcloud projects add-iam-policy-binding other-project \
  --member=user:analyst@example.com \
  --role=roles/bigquery.user
```

- Option A is incorrect because:
  - Unnecessary data duplication
  - Storage costs increase
  - Data staleness issues
  - Can query directly across projects

- Option C is incorrect because:
  - Federated queries are for external data sources (Cloud Storage, Bigtable, etc.)
  - Not for other BigQuery datasets
  - Different use case

- Option D is incorrect because:
  - Data Transfer Service is for scheduled imports
  - Creates copies of data
  - Unnecessary for ad-hoc queries

**Cross-Project Querying:**
- Uses fully-qualified names: `project.dataset.table`
- Requires IAM permissions in source project
- No data movement
- Billed to the project running the query

---

## Question 9
You need to share a BigQuery dataset with external partners while maintaining security. What should you do?

**A)** Export data to Cloud Storage and share the bucket

**B)** Grant partners IAM access to the dataset

**C)** Use Analytics Hub to publish the dataset

**D)** Create a public dataset

**Correct Answer:** C (or B depending on context)

**Explanation:**
- Option C is correct for modern sharing:
  - Analytics Hub is designed for data sharing
  - Can publish datasets to partners
  - Centralized data exchange
  - Usage tracking and analytics
  - More control than direct IAM

Analytics Hub (preferred for external sharing):
```bash
# Create data exchange (publisher)
bq mk --data_exchange \
  --display_name="Partner Data Exchange" \
  --location=us \
  my_exchange

# Create listing in exchange
bq mk --listing \
  --display_name="Sales Data" \
  --description="Q1 2024 sales data" \
  --data_exchange=my_exchange \
  --dataset=mydataset \
  --location=us \
  sales_listing

# Share with specific organizations
# Partners can subscribe via Analytics Hub UI
```

- Option B is also correct for simple sharing:
  - Grant specific IAM roles to external users
  - More direct than Analytics Hub
  - Works for Google accounts

Grant dataset access:
```bash
# Grant dataset access to external user
bq add-iam-policy-binding \
  --member=user:partner@external-company.com \
  --role=roles/bigquery.dataViewer \
  mydataset

# Grant to external group
bq add-iam-policy-binding \
  --member=group:partners@external-company.com \
  --role=roles/bigquery.dataViewer \
  mydataset

# Grant with authorized view (more control)
# Create view in partner-accessible dataset
CREATE VIEW shared_dataset.sales_summary AS
SELECT 
  DATE_TRUNC(date, MONTH) as month,
  SUM(amount) as total_sales
FROM private_dataset.sales
GROUP BY month;

# Authorize view
bq update --source shared_dataset.sales_summary private_dataset

# Grant access only to shared_dataset
bq add-iam-policy-binding \
  --member=user:partner@external-company.com \
  --role=roles/bigquery.dataViewer \
  shared_dataset
```

- Option A is incorrect because:
  - Loses BigQuery query capabilities
  - Partners need to import to their own BigQuery
  - Less efficient than native sharing

- Option D is incorrect because:
  - Public datasets are accessible to everyone
  - Not appropriate for partner-specific sharing
  - No access control

**Data Sharing Options:**
1. **Analytics Hub**: Best for external/marketplace sharing
2. **Direct IAM**: Simple partner access
3. **Authorized Views**: Share subsets with computed logic
4. **Authorized Datasets**: Cross-project view access

---

## Question 10
You need to automate daily data loads from Cloud Storage to BigQuery. What should you use?

**A)** Schedule a Cloud Function to run bq load daily

**B)** Use BigQuery Data Transfer Service

**C)** Create a cron job on Compute Engine

**D)** Manually load data each day

**Correct Answer:** B

**Explanation:**
- Option B is correct because:
  - Data Transfer Service is designed for scheduled data loads
  - Native BigQuery integration
  - Automatic retry on failures
  - Monitoring and logging built-in
  - Supports various sources (Cloud Storage, SaaS applications)

Configure scheduled transfer:
```bash
# Enable Data Transfer Service API
gcloud services enable bigquerydatatransfer.googleapis.com

# Create scheduled transfer from Cloud Storage
bq mk --transfer_config \
  --display_name="Daily Sales Load" \
  --target_dataset=mydataset \
  --data_source=google_cloud_storage \
  --schedule="every day 02:00" \
  --params='{
    "data_path_template":"gs://my-bucket/sales/daily/*.csv",
    "destination_table_name_template":"sales",
    "write_disposition":"WRITE_APPEND",
    "skip_leading_rows":"1",
    "field_delimiter":","
  }'

# List transfers
bq ls --transfer_config --transfer_location=us

# Get transfer details
bq show --transfer_config projects/PROJECT_ID/locations/us/transferConfigs/CONFIG_ID

# Run transfer manually (for testing)
bq mk --transfer_run \
  --run_time="2024-01-15T00:00:00Z" \
  projects/PROJECT_ID/locations/us/transferConfigs/CONFIG_ID
```

Schedule options:
```bash
# Daily at 3 AM
--schedule="every day 03:00"

# Every 6 hours
--schedule="every 6 hours"

# Weekly on Monday
--schedule="every monday 00:00"

# Monthly on 1st
--schedule="first day of month 00:00"

# Custom cron format
--schedule="0 2 * * *"  # 2 AM daily
```

Other data sources (Data Transfer Service):
```bash
# From Google Ads
bq mk --transfer_config \
  --data_source=google_ads \
  --display_name="Google Ads Transfer" \
  --target_dataset=ads_data \
  --params='{...}'

# From Google Analytics 360
bq mk --transfer_config \
  --data_source=google_analytics_360 \
  --display_name="GA360 Transfer" \
  --target_dataset=analytics \
  --params='{...}'

# From Amazon S3
bq mk --transfer_config \
  --data_source=amazon_s3 \
  --display_name="S3 Transfer" \
  --target_dataset=imports \
  --params='{...}'
```

- Option A is incorrect because:
  - Cloud Functions works but is more complex
  - Need to manage function code
  - Data Transfer Service is the native solution
  - More operational overhead

- Option C is incorrect because:
  - Requires managing Compute Engine VM
  - More infrastructure to maintain
  - Higher costs
  - Data Transfer Service is serverless

- Option D is incorrect because:
  - Manual process is error-prone
  - Not scalable
  - No automation

**Data Transfer Service Features:**
- Scheduled or on-demand runs
- Automatic retries
- Email notifications on failure
- Support for multiple data sources
- Backfill historical data
- Monitoring via Cloud Console/Logging
