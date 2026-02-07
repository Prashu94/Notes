# Google Cloud BigQuery PCA Guide

## 1. Architecture Overview
BigQuery's architecture is based on the separation of storage and compute, connected by a petabit-scale network.

### Components
- **Storage (Colossus):** Distributed storage system. Data is stored in columnar format (Capacitor).
- **Compute (Dremel):** Large multi-tenant cluster that executes SQL queries.
- **Network (Jupiter):** High-speed network connecting storage and compute.

### Execution Model
- **Slots:** The unit of computational capacity (CPU, RAM, I/O).
- **Query Execution:** Queries are broken down into stages and executed in parallel across thousands of slots.

## 2. Capacity Planning & Pricing Models (2026 Updated)

> **2026 Major Update**: BigQuery Editions is now the recommended pricing model, with enhanced features for AI/ML workloads including vector search and Iceberg table support.

### Pricing Models
1.  **On-Demand (Pay-per-Query):**
    - Pay per TB of data processed ($6.25/TB in US multi-region as of 2026).
    - Shared pool of slots (up to 2000 concurrent slots per project by default).
    - First 1 TB/month free.
    - Best for unpredictable workloads, ad-hoc queries, small-scale analytics.

2.  **Capacity-Based (Editions - Recommended for Production):**
    - Pay for reserved slot capacity (continuous availability).
    - **Standard Edition** ($0.04/slot/hour = $29/slot/month):
      - Basic SQL, streaming inserts, standard concurrency
      - 100 slot minimum purchase
      - Best for: Predictable workloads, development/testing
    
    - **Enterprise Edition** ($0.06/slot/hour = $43.20/slot/month):
      - All Standard features +
      - **Autoscaling** (automatically add/remove slots based on demand)
      - Higher concurrency (2x Standard)
      - Machine Learning features (BigQuery ML)
      - 100 slot minimum, scales automatically
      - Best for: Production workloads with variable demand
    
    - **Enterprise Plus Edition** ($0.10/slot/hour = $72/slot/month):
      - All Enterprise features +
      - **Cross-region disaster recovery** (automatic replication)
      - Highest concurrency (5x Standard)
      - **Vector Search (2026)**: Native support for AI/ML embeddings
      - **Iceberg Table Support (2026 GA)**: Open table format compatibility
      - Dedicated technical support
      - 100 slot minimum
      - Best for: Mission-critical workloads, AI/ML pipelines, multi-region apps

### 2026 New Features by Edition

| Feature | Standard | Enterprise | Enterprise Plus |
|---------|----------|------------|------------------|
| **Vector Search (2026)** | ❌ | ✅ Preview | ✅ GA |
| **Iceberg Tables (2026)** | ❌ | ✅ Limited | ✅ Full Support |
| **BigQuery Apache Iceberg (2026)** | ❌ | ✅ Read-only | ✅ Read/Write |
| **Cross-region DR** | ❌ | ❌ | ✅ |
| **Autoscaling** | ❌ | ✅ | ✅ |
| **Gemini in BigQuery (2026)** | Limited | ✅ | ✅ Full |

### Reservations (Enhanced 2026)
- Isolate capacity for specific workloads or departments.
- **Baseline:** Guaranteed slots (always available).
- **Autoscaling** (Enterprise/Enterprise Plus): Automatically add slots during demand spikes.
- **Idle Slot Sharing**: Unused slots from one reservation can be used by others (organization-wide).
- **Flex Slots (2026)**: Commit for 60 seconds minimum (vs 365 days), pay $0.08/slot/hour.
- **Sustainability Credits (2026)**: 5% discount for using carbon-free energy regions.

## 3. Performance Optimization Strategies

### Partitioning vs. Clustering
| Feature | Use Case | Benefit |
| :--- | :--- | :--- |
| **Partitioning** | Filter by time (Day/Month) or Integer Range. | Prunes entire files (partitions). Reduces cost & improves speed. |
| **Clustering** | Filter/Sort by high-cardinality columns (e.g., UserID). | Sorts data within partitions. Reduces data scanned (Block Pruning). |
| **Combined** | Large tables with time + other filters. | Maximum pruning efficiency. |

### Materialized Views
- Precomputed views that periodically cache query results.
- **Smart Tuning:** BigQuery automatically rewrites queries to use MVs if applicable.
- **Zero Maintenance:** Auto-refreshed by BigQuery.
- **Use Case:** Aggregations on large datasets (e.g., Daily Sales Summary).

### BI Engine
- In-memory analysis service.
- Caches frequently used data in memory for sub-second query response.
- **Use Case:** Interactive dashboards (Looker, Tableau) and high-concurrency BI.

## 4. Cost Optimization

- **Avoid `SELECT *`:** Columnar storage means you pay for every column selected.
- **Use Preview:** Previewing data is free; querying `LIMIT 10` is not (it scans full columns).
- **Long-term Storage:** Storage price drops by ~50% if a table is not modified for 90 days.
- **Slot Estimation:** Use `INFORMATION_SCHEMA.JOBS` to analyze slot usage and optimize reservations.

## 5. Security Architecture

### Data Encryption
- **Default:** Google-managed keys.
- **CMEK:** Customer-Managed Encryption Keys (Cloud KMS) for compliance.

### Network Security
- **VPC Service Controls:** Define security perimeters to prevent data exfiltration.
- **Private Google Access:** Access BigQuery from VPC without public IPs.

### Granular Access Control
- **Row-Level Security:** Filter rows based on user identity (e.g., `WHERE region = SESSION_USER()`).
- **Column-Level Security:** Restrict access to specific columns (e.g., PII) using Policy Tags (Data Catalog).

## 6. Decision Matrix: BigQuery vs. Others

| Feature | BigQuery | Cloud SQL | Bigtable | Spanner |
| :--- | :--- | :--- | :--- | :--- |
| **Type** | Data Warehouse (OLAP) | Relational DB (OLTP) | NoSQL Wide-Column | Global Relational (OLTP) |
| **Latency** | Seconds/Minutes | Milliseconds | Milliseconds | Milliseconds |
| **Throughput** | Massive (Petabytes) | Moderate | High (Millions OPS) | High |
| **Use Case** | Analytics, Reporting, ML | Web Apps, CRM, ERP | IoT, Time-series, AdTech | Global Banking, Inventory |

---

## 6.5. BigQuery 2026 New Capabilities

### Apache Iceberg Tables (GA 2026)

**What are Iceberg Tables?**
- Open table format created by Netflix, now Apache project
- Enables interoperability between BigQuery and other analytics engines (Spark, Trino, Flink)
- ACID transactions with snapshot isolation
- Schema evolution and partition evolution
- Time travel and rollback

**Why Use Iceberg in BigQuery?**
```
Use Case 1: Multi-Engine Analytics
┌──────────────────────────────────────────────────────────┐
│  Lakehouse Architecture (2026 Pattern)                   │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  Data Lake (Cloud Storage)                               │
│    │                                                      │
│    ├── Iceberg Tables (Parquet files + metadata)         │
│    │                                                      │
│    ├─► BigQuery (SQL analytics)                          │
│    ├─► Dataproc/Spark (data processing)                  │
│    ├─► Vertex AI (ML training)                           │
│    └─► External tools (Trino, Presto)                    │
│                                                           │
│  Benefit: Single source of truth, no data duplication    │
└──────────────────────────────────────────────────────────┘
```

**Creating Iceberg Tables in BigQuery:**

```sql
-- Method 1: Create BigQuery-managed Iceberg table
CREATE TABLE my_dataset.iceberg_table
WITH CONNECTION `my-project.us.my_connection`
OPTIONS (
  table_format = 'ICEBERG',
  storage_base_uri = 'gs://my-bucket/iceberg/my_table'
)
AS
SELECT * FROM my_dataset.source_table;

-- Method 2: Create external Iceberg table (data in Cloud Storage)
CREATE EXTERNAL TABLE my_dataset.external_iceberg
WITH CONNECTION `my-project.us.my_connection`
OPTIONS (
  table_format = 'ICEBERG',
  uris = ['gs://my-bucket/iceberg/external_table/metadata/*.json']
);

-- Query Iceberg table (same as regular BigQuery table)
SELECT 
  DATE(timestamp) as date,
  COUNT(*) as events,
  AVG(value) as avg_value
FROM my_dataset.iceberg_table
WHERE DATE(timestamp) >= '2026-01-01'
GROUP BY date
ORDER BY date DESC;

-- Time travel with Iceberg
SELECT *
FROM my_dataset.iceberg_table
  FOR SYSTEM_TIME AS OF TIMESTAMP '2026-02-01 00:00:00';

-- Iceberg metadata queries
SELECT *
FROM my_dataset.iceberg_table.SNAPSHOT_METADATA
ORDER BY committed_at DESC
LIMIT 10;
```

**Iceberg Table Management:**

```sql
-- Create new snapshot (manual compaction)
ALTER TABLE my_dataset.iceberg_table
SET OPTIONS (iceberg.auto_compaction = true);

-- Expire old snapshots (data retention)
ALTER TABLE my_dataset.iceberg_table
SET OPTIONS (iceberg.expire_snapshots_older_than_days = 7);

-- Schema evolution (add column)
ALTER TABLE my_dataset.iceberg_table
ADD COLUMN new_field STRING;

-- Partition evolution (change partitioning without rewriting data!)
ALTER TABLE my_dataset.iceberg_table
SET OPTIONS (
  iceberg.partition_fields = ['MONTH(timestamp)', 'region']
);
```

**Iceberg vs Native BigQuery Tables:**

| Feature | Native BigQuery | Iceberg on BigQuery |
|---------|-----------------|---------------------|
| **Query Performance** | Faster (native) | Good (external) |
| **Interoperability** | BigQuery only | All Apache engines |
| **ACID Transactions** | Yes | Yes |
| **Time Travel** | 7 days | Unlimited (configurable) |
| **Schema Evolution** | Limited | Full support |
| **Partition Evolution** | Requires rewrite | No rewrite needed |
| **Storage Cost** | BigQuery pricing | Cloud Storage pricing (cheaper) |
| **Best For** | BigQuery-only | Multi-engine, open standards |

### Vector Search in BigQuery (2026 GA - Enterprise Plus)

**What is Vector Search in BigQuery?**
- Native support for storing and querying high-dimensional vectors (embeddings)
- Enables similarity search for AI/ML applications (RAG, recommendation systems)
- Powered by Google's ScaNN (Scalable Nearest Neighbors) algorithm
- Integrated with Vertex AI for embedding generation

**Use Cases:**
- **Semantic Search**: Find similar documents, images, or products
- **RAG (Retrieval-Augmented Generation)**: Enhance LLM responses with relevant context
- **Recommendation Systems**: Find similar items or users
- **Anomaly Detection**: Identify outliers based on vector distance

**Creating Vector Columns:**

```sql
-- Create table with vector column
CREATE TABLE my_dataset.product_embeddings (
  product_id INT64,
  product_name STRING,
  description STRING,
  -- Vector column (768 dimensions for text-embedding-004)
  embedding ARRAY<FLOAT64>,
  category STRING,
  price FLOAT64
)
PARTITION BY DATE(update_timestamp);

-- Generate embeddings using Vertex AI (through BigQuery ML)
CREATE MODEL my_dataset.embedding_model
  REMOTE WITH CONNECTION `my-project.us.my_vertex_connection`
  OPTIONS (
    endpoint = 'text-embedding-004'  -- Vertex AI embedding model
  );

-- Populate embeddings
INSERT INTO my_dataset.product_embeddings (product_id, product_name, description, embedding)
SELECT 
  product_id,
  product_name,
  description,
  (SELECT ml_generate_embedding_result 
   FROM ML.GENERATE_EMBEDDING(
     MODEL my_dataset.embedding_model,
     (SELECT description as content)
   )
  ) as embedding
FROM my_dataset.products;
```

**Vector Similarity Search:**

```sql
-- Find similar products using cosine similarity
DECLARE query_embedding ARRAY<FLOAT64>;

-- Get embedding for query text
SET query_embedding = (
  SELECT ml_generate_embedding_result
  FROM ML.GENERATE_EMBEDDING(
    MODEL my_dataset.embedding_model,
    (SELECT "wireless headphones with noise cancellation" as content)
  )
);

-- Similarity search (top 10 most similar products)
SELECT
  product_id,
  product_name,
  description,
  -- Cosine similarity
  (
    SELECT SUM(a * b) / (
      SQRT(SUM(a * a)) * SQRT(SUM(b * b))
    )
    FROM UNNEST(embedding) AS a WITH OFFSET pos
    JOIN UNNEST(query_embedding) AS b WITH OFFSET pos2
      ON pos = pos2
  ) AS similarity_score
FROM my_dataset.product_embeddings
WHERE category = 'Electronics'  -- Filter first for performance
ORDER BY similarity_score DESC
LIMIT 10;

-- Alternative: Use VECTOR_SEARCH function (2026 optimized)
SELECT
  base.product_id,
  base.product_name,
  base.description,
  distance
FROM VECTOR_SEARCH(
  TABLE my_dataset.product_embeddings,
  'embedding',
  (
    SELECT ml_generate_embedding_result
    FROM ML.GENERATE_EMBEDDING(
      MODEL my_dataset.embedding_model,
      (SELECT "wireless headphones" as content)
    )
  ),
  distance_type => 'COSINE',
  top_k => 10,
  options => JSON '{"fraction_lists_to_search": 0.01}'  -- HNSW parameter
) AS base;
```

**Building a RAG System with BigQuery:**

```sql
-- Step 1: Store document chunks with embeddings
CREATE TABLE my_dataset.knowledge_base (
  doc_id STRING,
  chunk_id INT64,
  chunk_text STRING,
  embedding ARRAY<FLOAT64>,
  metadata JSON,
  source_url STRING
);

-- Step 2: Query for relevant context
CREATE TEMP FUNCTION get_relevant_context(user_query STRING)
RETURNS ARRAY<STRING>
AS (
  ARRAY(
    SELECT chunk_text
    FROM VECTOR_SEARCH(
      TABLE my_dataset.knowledge_base,
      'embedding',
      (SELECT ml_generate_embedding_result 
       FROM ML.GENERATE_EMBEDDING(
         MODEL my_dataset.embedding_model,
         (SELECT user_query as content)
       )),
      distance_type => 'COSINE',
      top_k => 5
    )
  )
);

-- Step 3: Generate answer with context (use with Vertex AI Gemini)
SELECT
  user_query,
  get_relevant_context(user_query) AS context_chunks,
  -- Send to Gemini via BigQuery ML
  ml_generate_text_result AS generated_answer
FROM ML.GENERATE_TEXT(
  MODEL my_dataset.gemini_model,
  (
    SELECT CONCAT(
      'Context: ', 
      ARRAY_TO_STRING(get_relevant_context("What is BigQuery?"), '\n'),
      '\n\nQuestion: What is BigQuery?',
      '\n\nAnswer based on the context above:'
    ) AS prompt
  ),
  STRUCT(
    0.2 AS temperature,
    1024 AS max_output_tokens
  )
);
```

**Vector Index Optimization (2026):**

```sql
-- Create approximate nearest neighbor (ANN) index for faster queries
CREATE SEARCH INDEX product_vector_index
ON my_dataset.product_embeddings(embedding)
OPTIONS (
  index_type = 'HNSW',  -- Hierarchical Navigable Small World
  distance_type = 'COSINE',
  -- HNSW parameters
  ef_construction = 40,
  m = 16
);

-- Query performance comparison:
-- Without index: 10-30 seconds for 1M vectors
-- With HNSW index: 100-500ms for 1M vectors (20-100x faster!)

-- Monitor index usage
SELECT
  table_name,
  index_name,
  index_type,
  coverage_percentage,
  last_refresh_time
FROM my_dataset.INFORMATION_SCHEMA.SEARCH_INDEXES
WHERE table_name = 'product_embeddings';
```

**Vector Search Cost Optimization:**

```sql
-- Use APPROXIMATE search for cost savings
SELECT product_id, product_name
FROM VECTOR_SEARCH(
  TABLE my_dataset.product_embeddings,
  'embedding',
  query_embedding,
  distance_type => 'COSINE',
  top_k => 10,
  options => JSON '{
    "use_approximate_search": true,
    "fraction_lists_to_search": 0.01  -- Search 1% of data (100x faster, slight accuracy trade-off)
  }'
);

-- Pricing (2026):
-- On-demand: $5 per TB scanned (same as regular queries)
-- Enterprise Plus: Included in base edition pricing
-- Vector index storage: $0.02 per GB/month
```

**Integration with Gemini (2026 Pattern):**

```python
from google.cloud import bigquery
from vertexai.generative_models import GenerativeModel
import vertexai

# Initialize
vertexai.init(project="my-project", location="us-central1")
bq_client = bigquery.Client()

def rag_query(user_question):
    # Step 1: Vector search in BigQuery for relevant context
    query = f"""
    SELECT chunk_text
    FROM VECTOR_SEARCH(
        TABLE my_dataset.knowledge_base,
        'embedding',
        (SELECT ml_generate_embedding_result 
         FROM ML.GENERATE_EMBEDDING(
           MODEL my_dataset.embedding_model,
           (SELECT '{user_question}' as content)
         )),
        distance_type => 'COSINE',
        top_k => 5
    )
    """
    
    results = bq_client.query(query).result()
    context_chunks = [row.chunk_text for row in results]
    
    # Step 2: Generate answer with Gemini
    model = GenerativeModel("gemini-1.5-pro-002")
    prompt = f"""
    Context from knowledge base:
    {chr(10).join(context_chunks)}
    
    Question: {user_question}
    
    Answer based on the context above:
    """
    
    response = model.generate_content(prompt)
    return response.text

# Usage
answer = rag_query("What are BigQuery Editions?")
print(answer)
```

### 2026 Best Practices Summary

**For Iceberg Tables:**
- ✅ Use for multi-engine analytics (Spark + BigQuery)
- ✅ Use for open data lake architectures
- ✅ Enable auto-compaction to maintain performance
- ⚠️ Slightly slower than native BigQuery tables
- ⚠️ Requires BigQuery connection to Cloud Storage

**For Vector Search:**
- ✅ Use Enterprise Plus edition for production (included features)
- ✅ Create HNSW indexes for large datasets (>100K vectors)
- ✅ Use approximate search for cost/performance balance
- ✅ Partition tables by date/category for better filtering
- ⚠️ Vector dimensions should match embedding model (768 for text-embedding-004)
- ⚠️ Index rebuilds can be expensive on frequently updated tables

---

## 7. Data Lake Architecture Patterns

### Multi-Tiered Data Lake

```
┌─────────────────────────────────────────────────────────────┐
│                   DATA INGESTION LAYER                       │
├─────────────────────────────────────────────────────────────┤
│  Cloud Storage (CSV/JSON/Avro/Parquet) ─────────────────►   │
│  Pub/Sub (Streaming) ─────────────────────────────────────►  │
│  Cloud SQL/Firestore (Change Streams) ────────────────────►  │
│  3rd-party APIs (via Cloud Functions) ────────────────────►  │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     RAW DATA ZONE (Bronze)                   │
├─────────────────────────────────────────────────────────────┤
│  - BigQuery External Tables (federated)                      │
│  - Cloud Storage bucket (gs://company-raw/)                  │
│  - Original format, immutable                                │
│  - Retention: 30-90 days                                     │
│  - Partitioned by ingestion date                             │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   CURATED ZONE (Silver)                      │
├─────────────────────────────────────────────────────────────┤
│  - BigQuery Native Tables                                    │
│  - Cleaned, validated, deduplicated                          │
│  - Partitioned + Clustered                                   │
│  - Retention: 1-2 years                                      │
│  - Schema evolution tracked                                  │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   ANALYTICS ZONE (Gold)                      │
├─────────────────────────────────────────────────────────────┤
│  - BigQuery Materialized Views                               │
│  - Aggregated, business-ready                                │
│  - Optimized for BI tools                                    │
│  - SLA: < 5 sec query response                               │
│  - Retention: 3-7 years                                      │
└─────────────────────────────────────────────────────────────┘
```

### Implementation Example

```sql
-- Bronze Layer: External table pointing to Cloud Storage
CREATE EXTERNAL TABLE `project.raw.web_logs`
OPTIONS (
  format = 'NEWLINE_DELIMITED_JSON',
  uris = ['gs://company-raw/logs/*.json'],
  hive_partition_uri_prefix = 'gs://company-raw/logs',
  require_hive_partition_filter = true
);

-- Silver Layer: Cleaned and partitioned
CREATE TABLE `project.curated.web_logs`
PARTITION BY DATE(timestamp)
CLUSTER BY user_id, country AS
SELECT
  PARSE_TIMESTAMP('%Y-%m-%d %H:%M:%S', timestamp_str) as timestamp,
  user_id,
  UPPER(country) as country,  -- Standardize
  page_path,
  duration_ms,
  -- Remove duplicates
  ROW_NUMBER() OVER (PARTITION BY user_id, timestamp_str ORDER BY ingestion_time DESC) as rn
FROM `project.raw.web_logs`
WHERE rn = 1;  -- Keep only latest

-- Gold Layer: Materialized view for dashboards
CREATE MATERIALIZED VIEW `project.analytics.daily_user_activity` AS
SELECT
  DATE(timestamp) as date,
  country,
  COUNT(DISTINCT user_id) as active_users,
  SUM(duration_ms) / 1000 / 60 as total_minutes,
  AVG(duration_ms) as avg_session_ms
FROM `project.curated.web_logs`
GROUP BY date, country;
```

---

## 8. Streaming Data Architecture

### Storage Write API vs Legacy Streaming

| Feature | Storage Write API | Legacy Streaming |
|---------|-------------------|------------------|
| **Cost** | $0.025/GB | $0.05/GB |
| **Latency** | < 1 second | < 1 second |
| **Exactly-once** | Yes (committed stream) | No (best-effort) |
| **At-least-once** | Yes (pending stream) | Yes |
| **Use Case** | Financial transactions | Log aggregation |

### Real-Time Pipeline Architecture

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   IoT Devices│─────►│   Pub/Sub    │─────►│  Dataflow    │
│   Mobile Apps│      │   Topic      │      │  (transform) │
│   Web Events │      └──────────────┘      └──────────────┘
└──────────────┘                                    │
                                                    ▼
                                         ┌──────────────────┐
                                         │   BigQuery       │
                                         │  (Storage Write  │
                                         │      API)        │
                                         └──────────────────┘
                                                    │
                                                    ▼
                                         ┌──────────────────┐
                                         │   Looker         │
                                         │   Dashboard      │
                                         └──────────────────┘
```

### Dataflow Streaming Insert Example (Python)

```python
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions

def parse_event(element):
    import json
    data = json.loads(element)
    return {
        'user_id': data['user_id'],
        'event_type': data['event_type'],
        'timestamp': data['timestamp'],
        'value': float(data.get('value', 0))
    }

options = PipelineOptions(
    streaming=True,
    project='my-project',
    region='us-central1'
)

with beam.Pipeline(options=options) as pipeline:
    (pipeline
     | 'Read from Pub/Sub' >> beam.io.ReadFromPubSub(
         subscription='projects/my-project/subscriptions/events-sub'
     )
     | 'Parse JSON' >> beam.Map(parse_event)
     | 'Write to BigQuery' >> beam.io.WriteToBigQuery(
         table='my_project:dataset.events',
         schema='user_id:STRING,event_type:STRING,timestamp:TIMESTAMP,value:FLOAT',
         write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
         create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
         method='STORAGE_WRITE_API'
     ))
```

---

## 9. Multi-Region and Global Strategies

### Data Locality and Performance

**Regional BigQuery Datasets:**
- Data stored in single region (e.g., `us-central1`, `europe-west1`)
- Best for: Compliance requirements, co-location with compute
- Cannot change region after creation

**Multi-Region BigQuery Datasets:**
- Data replicated across multiple regions (`US`, `EU`)
- Best for: Global analytics, high availability
- Automatic failover

### Global Data Warehouse Pattern

```
┌─────────────────────────────────────────────────────────────┐
│                    GLOBAL ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   US Region              EU Region            APAC Region   │
│   ┌─────────┐           ┌─────────┐         ┌─────────┐    │
│   │ US Data │──────────►│ EU Data │────────►│APAC Data│    │
│   │ BigQuery│   Sync    │BigQuery │  Sync   │BigQuery │    │
│   └─────────┘           └─────────┘         └─────────┘    │
│       │                      │                    │         │
│       ▼                      ▼                    ▼         │
│   ┌─────────────────────────────────────────────────────┐  │
│   │      Global BigQuery (Multi-Region: US + EU)        │  │
│   │       - Aggregated reporting                         │  │
│   │       - Cross-region analytics                       │  │
│   │       - Executive dashboards                         │  │
│   └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Scheduled Queries for Regional Sync

```sql
-- Scheduled query in EU region (runs daily at 02:00 UTC)
INSERT INTO `eu-project.eu_dataset.global_aggregates`
SELECT
  DATE(timestamp) as date,
  'EU' as region,
  COUNT(*) as event_count,
  SUM(revenue) as total_revenue
FROM `eu-project.eu_dataset.events`
WHERE DATE(timestamp) = CURRENT_DATE() - 1
GROUP BY date;

-- Similar query in US region
INSERT INTO `us-project.us_dataset.global_aggregates`
SELECT
  DATE(timestamp) as date,
  'US' as region,
  COUNT(*) as event_count,
  SUM(revenue) as total_revenue
FROM `us-project.us_dataset.events`
WHERE DATE(timestamp) = CURRENT_DATE() - 1
GROUP BY date;

-- Federated query for global view
SELECT
  date,
  SUM(event_count) as global_events,
  SUM(total_revenue) as global_revenue
FROM (
  SELECT * FROM `eu-project.eu_dataset.global_aggregates`
  UNION ALL
  SELECT * FROM `us-project.us_dataset.global_aggregates`
)
GROUP BY date;
```

---

## 10. Disaster Recovery and High Availability

### Backup Strategies

**1. Table Snapshots:**
```bash
# Create snapshot
bq mk --snapshot \
  --destination_table=project.dataset.table_snapshot_20240115 \
  project.dataset.original_table

# Restore from snapshot
bq cp project.dataset.table_snapshot_20240115 project.dataset.restored_table
```

**2. Scheduled Exports to Cloud Storage:**
```bash
# Create scheduled export (runs daily)
bq mk --transfer_config \
  --display_name="Daily Backup" \
  --data_source=scheduled_query \
  --schedule="every day 03:00" \
  --params='{
    "query":"EXPORT DATA OPTIONS(uri=\"gs://backup-bucket/export/table_*.parquet\", format=\"PARQUET\", overwrite=true) AS SELECT * FROM dataset.critical_table",
    "destination_table_name_template":"",
    "write_disposition":"WRITE_TRUNCATE"
  }'
```

**3. Cross-Region Replication:**
- BigQuery multi-region datasets automatically replicate
- Use scheduled queries for regional → multi-region sync
- Recovery Time Objective (RTO): < 1 hour
- Recovery Point Objective (RPO): Based on sync frequency

### High Availability Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    HA ARCHITECTURE                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Production Dataset (US Multi-Region)                        │
│  ┌────────────────────────────────────────┐                 │
│  │  - Automatic replication across zones  │                 │
│  │  - 99.99% SLA (Enterprise Plus)        │                 │
│  │  - Automatic failover                  │                 │
│  └────────────────────────────────────────┘                 │
│                      │                                       │
│                      ▼                                       │
│  ┌─────────────────────────────────────────────┐            │
│  │        Scheduled Snapshot (every 6 hours)   │            │
│  └─────────────────────────────────────────────┘            │
│                      │                                       │
│                      ▼                                       │
│  ┌─────────────────────────────────────────────┐            │
│  │   Export to Cloud Storage (daily)           │            │
│  │   - Multi-region bucket (US + EU)           │            │
│  │   - Object versioning enabled               │            │
│  │   - 30-day retention                        │            │
│  └─────────────────────────────────────────────┘            │
│                      │                                       │
│                      ▼                                       │
│  ┌─────────────────────────────────────────────┐            │
│  │   DR Dataset (EU Region - standby)          │            │
│  │   - Daily sync from Cloud Storage           │            │
│  │   - Read-only replica                       │            │
│  └─────────────────────────────────────────────┘            │
└─────────────────────────────────────────────────────────────┘
```

---

## 11. Cost Optimization at Scale

### Detailed Cost Analysis

**Storage Costs:**
```
Active Storage: $0.020/GB/month
Long-term Storage: $0.010/GB/month (unmodified for 90 days)
```

**Query Costs (On-Demand):**
```
$6.25 per TB processed
First 1 TB/month free
```

**Flat-Rate Pricing (Capacity-Based):**
```
Standard Edition: $0.04/slot-hour ($28.80/100 slots/month)
Enterprise Edition: $0.06/slot-hour ($43.20/100 slots/month)
Enterprise Plus: $0.10/slot-hour ($72/100 slots/month)
```

### Cost Optimization Techniques

**1. Partition Pruning Impact:**
```sql
-- BAD: Scans entire table (100 TB)
SELECT * FROM large_table
WHERE EXTRACT(DATE FROM timestamp) = '2024-01-15';
-- Cost: 100 TB × $6.25/TB = $625

-- GOOD: Scans only one partition (10 GB)
SELECT * FROM large_table
WHERE _PARTITIONDATE = '2024-01-15';
-- Cost: 0.01 TB × $6.25/TB = $0.0625
```

**2. Clustering Optimization:**
```sql
-- Create clustered table
CREATE TABLE dataset.orders
PARTITION BY DATE(order_date)
CLUSTER BY customer_id, product_category AS
SELECT * FROM dataset.raw_orders;

-- Query benefits from clustering
SELECT SUM(amount) FROM dataset.orders
WHERE customer_id = 'C12345'
  AND DATE(order_date) = '2024-01-15';
-- Clustering can reduce scanned data by 80-95%
```

**3. Materialized Views for Cost Reduction:**
```sql
-- Expensive query run 1000x/day
SELECT
  DATE(timestamp) as date,
  country,
  COUNT(*) as events
FROM large_table
GROUP BY date, country;
-- Cost: 50 GB × 1000 runs × $6.25/TB = $312.50/day

-- Materialize it
CREATE MATERIALIZED VIEW dataset.daily_country_stats AS
SELECT
  DATE(timestamp) as date,
  country,
  COUNT(*) as events
FROM large_table
GROUP BY date, country;
-- MV refresh cost: 50 GB × 1 refresh/day × $6.25/TB = $0.31/day
-- Queries against MV: Near-zero cost (already computed)
-- Savings: $312.19/day = $9,365/month
```

**4. Flat-Rate vs On-Demand Decision:**
```
Breakeven Point = Monthly On-Demand Cost / Flat-Rate Cost

Example:
- On-Demand: 500 TB/month × $6.25/TB = $3,125/month
- Flat-Rate: 500 slots × $0.04/hour × 730 hours = $14,600/month

If queries are consistent: Use flat-rate
If queries are spiky: Use on-demand or autoscaling
```

### Cost Monitoring Dashboard (SQL)

```sql
-- Top 10 most expensive queries (last 30 days)
SELECT
  user_email,
  query,
  total_bytes_billed / POW(10,12) as tb_billed,
  total_bytes_billed / POW(10,12) * 6.25 as estimated_cost_usd,
  TIMESTAMP_TRUNC(creation_time, DAY) as date
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE creation_time > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
  AND job_type = 'QUERY'
  AND state = 'DONE'
ORDER BY total_bytes_billed DESC
LIMIT 10;

-- Cost by user (last 30 days)
SELECT
  user_email,
  SUM(total_bytes_billed) / POW(10,12) as total_tb_billed,
  SUM(total_bytes_billed) / POW(10,12) * 6.25 as estimated_cost_usd,
  COUNT(*) as query_count
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE creation_time > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
  AND job_type = 'QUERY'
  AND state = 'DONE'
GROUP BY user_email
ORDER BY total_tb_billed DESC;
```

---

## 12. Advanced Security and Compliance

### Column-Level Security with Policy Tags

```bash
# 1. Create taxonomy in Data Catalog
gcloud data-catalog taxonomies create sensitive_data \
  --location=us \
  --display-name="Sensitive Data Classification"

# 2. Create policy tag
gcloud data-catalog taxonomies policy-tags create pii \
  --taxonomy=sensitive_data \
  --display-name="PII" \
  --location=us

# 3. Apply policy tag to column
bq update --schema_update_option=ALLOW_FIELD_ADDITION \
  dataset.users \
  schema.json

# schema.json:
# [
#   {"name": "user_id", "type": "STRING"},
#   {"name": "email", "type": "STRING", 
#    "policyTags": {"names": ["projects/PROJECT/locations/us/taxonomies/TAXONOMY_ID/policyTags/TAG_ID"]}},
#   {"name": "name", "type": "STRING"}
# ]

# 4. Grant Fine-Grained Reader role
gcloud data-catalog taxonomies policy-tags set-iam-policy TAG_ID policy.json
```

### Row-Level Security (Authorized Views)

```sql
-- Create base table (restricted)
CREATE TABLE dataset.all_sales (
  sale_id INT64,
  region STRING,
  amount FLOAT64,
  salesperson_email STRING
);

-- Create authorized view (filtered by user)
CREATE VIEW dataset.my_sales AS
SELECT sale_id, region, amount
FROM dataset.all_sales
WHERE salesperson_email = SESSION_USER();

-- Grant access to view only (not base table)
GRANT `roles/bigquery.dataViewer` 
  ON dataset.my_sales
  TO 'user:salesperson@example.com';
```

### VPC Service Controls

```bash
# Create service perimeter
gcloud access-context-manager perimeters create bigquery_perimeter \
  --title="BigQuery Perimeter" \
  --resources=projects/PROJECT_NUMBER \
  --restricted-services=bigquery.googleapis.com \
  --access-levels=corp_network

# Prevent data exfiltration
# - Blocks: Copying data to external projects
# - Blocks: Exporting to Cloud Storage outside perimeter
# - Blocks: Querying from unauthorized networks
```

### Audit Logging and Compliance

```sql
-- Query BigQuery audit logs
SELECT
  timestamp,
  principal_email,
  resource.labels.project_id,
  resource.labels.dataset_id,
  protopayload_auditlog.methodName,
  protopayload_auditlog.resourceName,
  protopayload_auditlog.authenticationInfo.principalEmail as authenticated_user
FROM `my_project.logs.cloudaudit_googleapis_com_data_access`
WHERE resource.type = 'bigquery_resource'
  AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
  AND (
    protopayload_auditlog.methodName LIKE '%tabledata.list%'
    OR protopayload_auditlog.methodName LIKE '%jobs.query%'
  )
ORDER BY timestamp DESC
LIMIT 100;
```

**Compliance Frameworks:**
- **HIPAA:** Use CMEK, column-level security, audit logging
- **GDPR:** Implement data retention policies, right-to-be-forgotten (DELETE/UPDATE)
- **SOC 2:** Enable audit logs, restrict access with IAM, VPC-SC
- **PCI DSS:** Column-level security for card data, encrypt with CMEK

---

## 13. Integration Patterns

### BigQuery + Dataflow (ETL/ELT)

```python
# Dataflow pipeline: Transform and load to BigQuery
import apache_beam as beam
from apache_beam.io.gcp.bigquery import WriteToBigQuery

def transform_record(element):
    # Business logic
    return {
        'user_id': element['id'],
        'total_spent': sum(element.get('transactions', [])),
        'processed_at': beam.utils.timestamp.Timestamp.now()
    }

with beam.Pipeline() as pipeline:
    (pipeline
     | 'Read from BigQuery' >> beam.io.ReadFromBigQuery(
         query='SELECT * FROM source_dataset.raw_data WHERE date = CURRENT_DATE()',
         use_standard_sql=True
     )
     | 'Transform' >> beam.Map(transform_record)
     | 'Write to BigQuery' >> WriteToBigQuery(
         table='target_dataset.processed_data',
         schema='user_id:STRING,total_spent:FLOAT,processed_at:TIMESTAMP',
         write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND
     ))
```

### BigQuery + Looker (BI)

```sql
-- Optimized for Looker dashboards
CREATE MATERIALIZED VIEW analytics.looker_sales_metrics
PARTITION BY DATE(order_date)
CLUSTER BY region, product_category AS
SELECT
  DATE(order_date) as order_date,
  region,
  product_category,
  COUNT(DISTINCT order_id) as order_count,
  COUNT(DISTINCT customer_id) as unique_customers,
  SUM(order_amount) as total_revenue,
  AVG(order_amount) as avg_order_value
FROM sales.orders
GROUP BY order_date, region, product_category;

-- Enable BI Engine for fast dashboard queries
ALTER MATERIALIZED VIEW analytics.looker_sales_metrics
SET OPTIONS (enable_refresh = true, refresh_interval_minutes = 30);
```

### BigQuery + Vertex AI (ML Pipeline)

```python
from google.cloud import bigquery, aiplatform

# 1. Feature engineering in BigQuery
client = bigquery.Client()
query = """
CREATE OR REPLACE TABLE ml_dataset.features AS
SELECT
  user_id,
  COUNT(DISTINCT session_id) as session_count,
  SUM(purchase_amount) as total_spent,
  AVG(time_on_site) as avg_time_on_site,
  COUNTIF(event = 'purchase') / COUNT(*) as conversion_rate,
  LABEL  -- Target variable
FROM analytics.user_events
GROUP BY user_id, LABEL
"""
client.query(query).result()

# 2. Train model in Vertex AI
aiplatform.init(project='my-project', location='us-central1')

dataset = aiplatform.TabularDataset.create(
    display_name="user_churn_dataset",
    bigquery_source="bq://my-project.ml_dataset.features"
)

job = aiplatform.AutoMLTabularTrainingJob(
    display_name="churn_prediction",
    optimization_prediction_type="classification",
    optimization_objective="maximize-au-prc"
)

model = job.run(
    dataset=dataset,
    target_column="LABEL",
    training_fraction_split=0.8,
    validation_fraction_split=0.1,
    test_fraction_split=0.1
)

# 3. Batch prediction back to BigQuery
batch_prediction_job = model.batch_predict(
    job_display_name="churn_predictions",
    bigquery_source="bq://my-project.ml_dataset.prediction_input",
    bigquery_destination_prefix="bq://my-project.ml_dataset",
    machine_type="n1-standard-4"
)
```

---

## 14. Performance Tuning at Petabyte Scale

### Query Execution Plan Analysis

```sql
-- Enable query plan explanation
SELECT
  user_id,
  SUM(amount) as total
FROM large_table
WHERE DATE(timestamp) >= '2024-01-01'
GROUP BY user_id;

-- View execution details in INFORMATION_SCHEMA
SELECT
  job_id,
  query,
  total_slot_ms,
  total_bytes_processed,
  (total_slot_ms / 1000) / 3600 as slot_hours,
  timeline
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE job_id = 'YOUR_JOB_ID';
```

### Anti-Patterns and Solutions

**Anti-Pattern 1: Self-JOIN on large tables**
```sql
-- BAD: Cartesian explosion
SELECT a.user_id, COUNT(b.event)
FROM events a
JOIN events b ON a.user_id = b.user_id
GROUP BY a.user_id;

-- GOOD: Use window functions
SELECT DISTINCT
  user_id,
  COUNT(*) OVER (PARTITION BY user_id) as event_count
FROM events;
```

**Anti-Pattern 2: Multiple passes over data**
```sql
-- BAD: Separate queries
SELECT AVG(amount) FROM sales;  -- Pass 1
SELECT MAX(amount) FROM sales;  -- Pass 2
SELECT MIN(amount) FROM sales;  -- Pass 3

-- GOOD: Single pass
SELECT
  AVG(amount) as avg_amount,
  MAX(amount) as max_amount,
  MIN(amount) as min_amount
FROM sales;
```

**Anti-Pattern 3: Unfiltered cross-region queries**
```sql
-- BAD: Query EU dataset from US region
SELECT COUNT(*) FROM `eu-project.eu_dataset.table`;
-- Cross-region data transfer charges apply

-- GOOD: Replicate to US or use scheduled sync
CREATE TABLE `us-project.us_dataset.table_replica` AS
SELECT * FROM `eu-project.eu_dataset.table`;
```

### Slot Utilization Optimization

```sql
-- Monitor slot usage
SELECT
  TIMESTAMP_TRUNC(period_start, HOUR) as hour,
  project_id,
  reservation_name,
  SUM(total_slot_ms) / (1000 * 60 * 60) as slot_hours_used,
  SUM(period_slot_ms) / (1000 * 60 * 60) as slot_hours_available,
  (SUM(total_slot_ms) / SUM(period_slot_ms)) * 100 as utilization_pct
FROM `region-us`.INFORMATION_SCHEMA.JOBS_TIMELINE_BY_PROJECT
WHERE period_start >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
GROUP BY hour, project_id, reservation_name
ORDER BY hour DESC;
```

---

## 15. Real-World Reference Architectures

### E-Commerce Analytics Platform

```
┌────────────────────────────────────────────────────────────┐
│                  E-COMMERCE DATA PLATFORM                   │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐     ┌──────────────┐    ┌─────────────┐ │
│  │ Web/Mobile   │────►│   Pub/Sub    │───►│  Dataflow   │ │
│  │  Clickstream │     │   Topics     │    │(transformation)
│  └──────────────┘     └──────────────┘    └─────────────┘ │
│                                                   │         │
│  ┌──────────────┐                                │         │
│  │  Cloud SQL   │─── Change Streams ─────────────┘         │
│  │  (Orders DB) │                                          │
│  └──────────────┘                                          │
│                              ▼                             │
│                   ┌─────────────────────┐                  │
│                   │    BigQuery         │                  │
│                   │  ┌───────────────┐  │                  │
│                   │  │ Raw Events    │  │                  │
│                   │  │ (partitioned) │  │                  │
│                   │  └───────────────┘  │                  │
│                   │  ┌───────────────┐  │                  │
│                   │  │ Orders (sync) │  │                  │
│                   │  └───────────────┘  │                  │
│                   │  ┌───────────────┐  │                  │
│                   │  │ Customers     │  │                  │
│                   │  │ (clustered)   │  │                  │
│                   │  └───────────────┘  │                  │
│                   └─────────────────────┘                  │
│                              │                             │
│                              ▼                             │
│                   ┌─────────────────────┐                  │
│                   │  Materialized Views │                  │
│                   │  - Daily Revenue    │                  │
│                   │  - User Cohorts     │                  │
│                   │  - Product Rankings │                  │
│                   └─────────────────────┘                  │
│                              │                             │
│                              ▼                             │
│                   ┌─────────────────────┐                  │
│                   │   BI Engine +       │                  │
│                   │   Looker Studio     │                  │
│                   └─────────────────────┘                  │
└────────────────────────────────────────────────────────────┘

Key Features:
- Real-time clickstream (< 1 min latency)
- Daily order sync (consistent with OLTP)
- Customer 360 view (clustered for fast lookup)
- Pre-aggregated metrics (materialized views)
- Interactive dashboards (BI Engine)
```

### Financial Services Risk Analytics

```
┌────────────────────────────────────────────────────────────┐
│             RISK ANALYTICS PLATFORM (PCI-DSS)              │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐     ┌──────────────┐                     │
│  │ Transaction  │────►│  Cloud KMS   │                     │
│  │    API       │     │  (CMEK)      │                     │
│  └──────────────┘     └──────────────┘                     │
│         │                     │                            │
│         ▼                     ▼                            │
│  ┌────────────────────────────────────┐                    │
│  │      BigQuery (US Multi-Region)    │                    │
│  │  ┌──────────────────────────────┐  │                    │
│  │  │ transactions (CMEK encrypted)│  │                    │
│  │  │ - Column-level security      │  │                    │
│  │  │ - Policy tags on PII         │  │                    │
│  │  │ - Partitioned by date        │  │                    │
│  │  └──────────────────────────────┘  │                    │
│  │                                     │                    │
│  │  ┌──────────────────────────────┐  │                    │
│  │  │ fraud_scores (authorized view)│  │                    │
│  │  │ - Row-level security         │  │                    │
│  │  └──────────────────────────────┘  │                    │
│  └────────────────────────────────────┘                    │
│                   │                                        │
│                   ▼                                        │
│  ┌────────────────────────────────────┐                    │
│  │      BigQuery ML Model             │                    │
│  │  - Fraud detection (XGBoost)       │                    │
│  │  - Real-time scoring               │                    │
│  └────────────────────────────────────┘                    │
│                   │                                        │
│                   ▼                                        │
│  ┌────────────────────────────────────┐                    │
│  │   VPC Service Controls Perimeter   │                    │
│  │   - Block external data transfer   │                    │
│  │   - Audit all access               │                    │
│  └────────────────────────────────────┘                    │
└────────────────────────────────────────────────────────────┘

Compliance Features:
- CMEK encryption (PCI-DSS requirement)
- Column-level security for card numbers
- VPC-SC prevents data exfiltration
- Audit logs for all access (SOC 2)
- Multi-region replication (HA requirement)
```

---

## 16. Migration Strategies

### Migrating from On-Premises Data Warehouse

**Assessment Phase:**
```bash
# 1. Analyze current workload
# - Query patterns
# - Data volume
# - Concurrent users
# - Performance requirements

# 2. Estimate BigQuery costs
# Storage: <current_TB> × $0.02/GB/month
# Queries: <monthly_TB_scanned> × $6.25/TB

# 3. Choose migration strategy
```

**Migration Strategies:**

| Strategy | Timeline | Downtime | Use Case |
|----------|----------|----------|----------|
| **Big Bang** | 1-2 weeks | Hours | Small systems |
| **Phased** | 2-6 months | Minutes | Large systems |
| **Hybrid** | 6-12 months | None | Critical systems |

**Phased Migration Example:**

```
Phase 1: Historical Data (Week 1-2)
├── Export from source → Cloud Storage
├── Load into BigQuery
└── Validate data integrity

Phase 2: ETL Pipelines (Week 3-6)
├── Rewrite ETL jobs for BigQuery
├── Deploy Dataflow pipelines
└── Parallel run (validate outputs)

Phase 3: BI Tools (Week 7-8)
├── Update connection strings
├── Optimize dashboards
└── User training

Phase 4: Decommission (Week 9-12)
├── Monitor for 30 days
├── Turn off old system
└── Cost analysis
```

### Oracle to BigQuery Migration

```python
# Python script using Dataflow
import apache_beam as beam
from apache_beam.io.jdbc import ReadFromJdbc
from apache_beam.io.gcp.bigquery import WriteToBigQuery

pipeline_options = PipelineOptions()

with beam.Pipeline(options=pipeline_options) as pipeline:
    (pipeline
     | 'Read from Oracle' >> ReadFromJdbc(
         table_name='HR.EMPLOYEES',
         driver_class_name='oracle.jdbc.OracleDriver',
         jdbc_url='jdbc:oracle:thin:@host:1521:orcl',
         username='user',
         password='pass'
     )
     | 'Transform Data Types' >> beam.Map(lambda row: {
         'employee_id': int(row['EMPLOYEE_ID']),
         'name': str(row['NAME']),
         'hire_date': row['HIRE_DATE'].strftime('%Y-%m-%d'),
         'salary': float(row['SALARY'])
     })
     | 'Write to BigQuery' >> WriteToBigQuery(
         table='project.dataset.employees',
         schema='employee_id:INTEGER,name:STRING,hire_date:DATE,salary:FLOAT',
         write_disposition=beam.io.BigQueryDisposition.WRITE_TRUNCATE
     ))
```

---

## 17. PCA Exam Decision Frameworks

### When to Use BigQuery?

```
Decision Tree:
└── Need to analyze large datasets?
    ├── NO → Use Cloud SQL (< 1 TB, OLTP workload)
    └── YES
        └── Need millisecond latency?
            ├── YES → Use Bigtable (IoT, time-series)
            └── NO
                └── Need global transactions?
                    ├── YES → Use Spanner
                    └── NO → **USE BIGQUERY**
                        ├── Analytics
                        ├── Reporting
                        ├── ML
                        └── Data Warehouse
```

### Partitioning vs Clustering Decision

```
Start: Large table (> 1 GB)?
├── NO → No optimization needed
└── YES
    └── Frequently filter by date/timestamp?
        ├── YES → **PARTITION by date**
        │   └── Also filter by other columns (e.g., user_id)?
        │       ├── YES → **CLUSTER by those columns**
        │       └── NO → Done
        └── NO
            └── Filter by high-cardinality columns?
                ├── YES → **CLUSTER by those columns (up to 4)**
                └── NO → Consider materialized view
```

### On-Demand vs Flat-Rate Pricing

```
Monthly Query Volume?
├── < 10 TB → **On-Demand** ($62.50/month)
├── 10-200 TB → **On-Demand with monitoring**
│   └── Consistent daily usage?
│       ├── YES → Consider flat-rate
│       └── NO → Stay on-demand
└── > 200 TB → **Evaluate Flat-Rate**
    └── Calculate break-even:
        - On-Demand: 200 TB × $6.25 = $1,250/month
        - Flat-Rate: 100 slots × $0.04/hr × 730 hrs = $2,920/month
        - Flat-Rate: 500 slots × $0.04/hr × 730 hrs = $14,600/month
        
    └── If queries spread evenly across 24 hours:
        ├── YES → Flat-rate likely cheaper
        └── NO → Use autoscaling or on-demand
```

---

## 18. PCA Exam Scenarios

### Scenario 1: Real-Time Dashboard with Cost Constraints

**Requirements:**
- Dashboard refreshes every 5 minutes
- Queries scan 100 GB per refresh
- Budget: $500/month

**Solution:**
```sql
-- Bad: Query raw table every 5 minutes
-- Cost: 100 GB × 12 refreshes/hour × 24 hours × 30 days × $6.25/TB
--     = 0.1 TB × 8,640 × $6.25 = $5,400/month ❌

-- Good: Create materialized view
CREATE MATERIALIZED VIEW analytics.dashboard_data
AS
SELECT
  product_id,
  SUM(quantity) as total_quantity,
  SUM(revenue) as total_revenue
FROM sales.transactions
WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
GROUP BY product_id;

-- MV auto-refreshes (smart tuning)
-- Dashboard queries MV (< 1 MB)
-- Cost: ~$10/month ✅
```

### Scenario 2: Multi-Region Compliance

**Requirements:**
- EU customers' data must stay in EU
- US customers' data must stay in US
- Global analytics needed

**Solution:**
```
1. Create regional datasets:
   - EU dataset in europe-west1
   - US dataset in us-central1

2. Use Pub/Sub + Dataflow for data routing:
   - Check user region metadata
   - Route to appropriate BigQuery dataset

3. For global analytics:
   - Use federated queries (cross-region)
   - OR: Schedule aggregated sync to multi-region dataset
```

### Scenario 3: Petabyte-Scale Table Performance

**Requirements:**
- 5 PB table
- Queries take > 10 minutes
- Users need < 30 second response

**Solution:**
```sql
-- 1. Partition by date
CREATE TABLE dataset.large_table
PARTITION BY DATE(timestamp)
CLUSTER BY user_id, event_type
AS SELECT * FROM dataset.original_table;

-- 2. Create clustered materialized view for common queries
CREATE MATERIALIZED VIEW dataset.user_summary
PARTITION BY DATE(date)
CLUSTER BY user_id AS
SELECT
  DATE(timestamp) as date,
  user_id,
  COUNT(*) as event_count,
  SUM(value) as total_value
FROM dataset.large_table
GROUP BY date, user_id;

-- 3. Enable BI Engine (reserve 100 GB)
ALTER TABLE dataset.user_summary
SET OPTIONS (enable_refresh = true);

-- 4. Use flat-rate slots for predictable performance
-- Reserve 2000 slots (Enterprise Edition)

-- Result: Query time reduced from 600s → 15s ✅
```

---

**End of BigQuery PCA Guide**
