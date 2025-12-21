# AWS Athena - SAA-C03 Comprehensive Guide

## Table of Contents
1. [Overview and Introduction](#overview-and-introduction)
2. [Architecture and Components](#architecture-and-components)
3. [Data Sources and Formats](#data-sources-and-formats)
4. [Querying Data](#querying-data)
5. [Performance Optimization](#performance-optimization)
6. [Federated Queries](#federated-queries)
7. [Integration with Other Services](#integration-with-other-services)
8. [Security](#security)
9. [Cost Management](#cost-management)
10. [Best Practices](#best-practices)
11. [SAA-C03 Exam Tips](#saa-c03-exam-tips)
12. [Practice Questions](#practice-questions)

---

## Overview and Introduction

### What is Amazon Athena?

Amazon Athena is a **serverless, interactive query service** that makes it easy to analyze data directly in Amazon S3 using standard SQL. There are no clusters to manage, no infrastructure to set up, and you pay only for the queries you run.

### Key Characteristics

- **Serverless**: No infrastructure to manage
- **Pay-per-query**: Charged based on data scanned
- **Standard SQL**: Uses Presto SQL engine
- **Fast**: Results in seconds
- **Integrated**: Works with AWS Glue Data Catalog

### Common Use Cases

1. **Ad-hoc Analysis**: Quick queries on S3 data
2. **Log Analysis**: Query application/access logs
3. **Business Intelligence**: Connect to visualization tools
4. **Data Lake Queries**: Query data lake without ETL
5. **Security Analysis**: Analyze CloudTrail, VPC Flow Logs

### Athena at a Glance

```
┌─────────────────────────────────────────────────────────────────┐
│                    Amazon Athena Overview                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Data Sources (S3)                        Query & Results       │
│   ┌─────────────────┐                                           │
│   │    CSV Files    │                      ┌─────────────────┐  │
│   │    JSON Files   │                      │   AWS Console   │  │
│   │  Parquet Files  │ ◄─── Athena ───────► │   JDBC/ODBC     │  │
│   │    ORC Files    │     Queries          │   API/CLI       │  │
│   │     Avro        │                      │   QuickSight    │  │
│   └─────────────────┘                      └─────────────────┘  │
│                                                                  │
│   Key Benefits:                                                  │
│   • No data movement - query data where it lives               │
│   • No servers to manage                                        │
│   • Pay only for data scanned ($5 per TB)                      │
│   • Standard SQL syntax                                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Architecture and Components

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   Athena Architecture                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │                    Client Layer                           │  │
│   │  ┌────────────┐  ┌────────────┐  ┌──────────────────┐   │  │
│   │  │  Console   │  │  JDBC/ODBC │  │  API/SDK/CLI     │   │  │
│   │  └─────┬──────┘  └──────┬─────┘  └────────┬─────────┘   │  │
│   └────────┼────────────────┼─────────────────┼─────────────┘  │
│            │                │                 │                  │
│            └────────────────┼─────────────────┘                  │
│                             ▼                                    │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │                 Athena Query Engine                       │  │
│   │  ┌────────────────────────────────────────────────────┐  │  │
│   │  │  SQL Parser → Query Planner → Execution Engine     │  │  │
│   │  │              (Presto-based)                         │  │  │
│   │  └────────────────────────────────────────────────────┘  │  │
│   └──────────────────────────────────────────────────────────┘  │
│                             │                                    │
│            ┌────────────────┼────────────────┐                  │
│            ▼                ▼                ▼                  │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐     │
│   │  AWS Glue    │  │   Amazon     │  │  Query Results   │     │
│   │  Data Catalog│  │     S3       │  │   (S3 Bucket)    │     │
│   │  (Metadata)  │  │   (Data)     │  │                  │     │
│   └──────────────┘  └──────────────┘  └──────────────────┘     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Core Components

#### 1. Query Engine
- Based on Presto (open-source distributed SQL engine)
- Handles SQL parsing, planning, and execution
- Scales automatically based on query complexity

#### 2. AWS Glue Data Catalog
- Central metadata repository
- Stores table definitions, schemas
- Shared with other services (EMR, Redshift Spectrum)

#### 3. Data Storage (S3)
- Source data remains in S3
- No data movement or transformation required
- Supports various file formats

#### 4. Query Results
- Stored in S3 bucket (configurable)
- Results cached for 45 minutes by default
- Can be encrypted

### Workgroups

Workgroups help organize users and queries:

```
┌─────────────────────────────────────────────────────────────────┐
│                     Athena Workgroups                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │                    Organization                          │  │
│   │                                                          │  │
│   │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │  │
│   │   │  Analytics   │  │    Data      │  │   Finance    │  │  │
│   │   │  Workgroup   │  │  Engineering │  │  Workgroup   │  │  │
│   │   │              │  │   Workgroup  │  │              │  │  │
│   │   │ • Query limit│  │ • Unlimited  │  │ • Query limit│  │  │
│   │   │ • Own results│  │ • Own results│  │ • Own results│  │  │
│   │   │ • Metrics    │  │ • Metrics    │  │ • Metrics    │  │  │
│   │   └──────────────┘  └──────────────┘  └──────────────┘  │  │
│   │                                                          │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│   Workgroup Features:                                            │
│   • Separate query history per workgroup                        │
│   • Data usage controls (per-query and per-workgroup limits)    │
│   • Different result locations                                   │
│   • CloudWatch metrics per workgroup                            │
│   • IAM policies to control access                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Sources and Formats

### Supported File Formats

| Format | Description | Best For |
|--------|-------------|----------|
| **CSV** | Comma-separated values | Simple tabular data |
| **TSV** | Tab-separated values | Tab-delimited data |
| **JSON** | JavaScript Object Notation | Semi-structured data |
| **Parquet** | Columnar format | Analytics workloads |
| **ORC** | Optimized Row Columnar | Hive-compatible data |
| **Avro** | Row-based format | Schema evolution |
| **Text** | Plain text files | Log files |

### Format Comparison

```
┌─────────────────────────────────────────────────────────────────┐
│              Data Format Comparison for Athena                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Row-Based Formats (CSV, JSON, Avro):                          │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  Row 1: │ Col1 │ Col2 │ Col3 │ Col4 │ Col5 │            │  │
│   │  Row 2: │ Col1 │ Col2 │ Col3 │ Col4 │ Col5 │            │  │
│   │  Row 3: │ Col1 │ Col2 │ Col3 │ Col4 │ Col5 │            │  │
│   │                                                          │  │
│   │  ✓ Good for: INSERT, full row retrieval                 │  │
│   │  ✗ Bad for: Analytical queries on specific columns      │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│   Columnar Formats (Parquet, ORC):                              │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  Col1: │ R1 │ R2 │ R3 │                                 │  │
│   │  Col2: │ R1 │ R2 │ R3 │                                 │  │
│   │  Col3: │ R1 │ R2 │ R3 │    ◄── Only read needed columns │  │
│   │  Col4: │ R1 │ R2 │ R3 │                                 │  │
│   │  Col5: │ R1 │ R2 │ R3 │                                 │  │
│   │                                                          │  │
│   │  ✓ Good for: Analytics, aggregations, specific columns  │  │
│   │  ✓ Better compression                                   │  │
│   │  ✓ Up to 90% less data scanned                         │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Data Sources

#### Primary: Amazon S3
```
┌─────────────────────────────────────────────────────────────────┐
│                   S3 as Athena Data Source                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   s3://my-data-lake/                                            │
│   ├── raw/                                                       │
│   │   ├── logs/                                                  │
│   │   │   ├── 2024/01/01/                                       │
│   │   │   └── 2024/01/02/                                       │
│   │   └── events/                                                │
│   │                                                              │
│   ├── processed/                                                 │
│   │   ├── year=2024/                                            │
│   │   │   ├── month=01/                                         │
│   │   │   │   └── day=01/                                       │
│   │   │   │       └── data.parquet  ◄── Hive-style partitioning │
│   │   │   └── month=02/                                         │
│   │   └── year=2023/                                            │
│   │                                                              │
│   └── athena-results/    ◄── Query results storage              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### Federated Query Sources
- Amazon DynamoDB
- Amazon Redshift
- Amazon RDS (MySQL, PostgreSQL)
- Amazon OpenSearch
- Amazon CloudWatch Logs
- Custom sources via Lambda connectors

---

## Querying Data

### Creating Tables

#### Using AWS Glue Data Catalog (Recommended)

```sql
-- Create a database
CREATE DATABASE my_database;

-- Create external table pointing to S3
CREATE EXTERNAL TABLE my_database.web_logs (
    request_timestamp string,
    client_ip string,
    request_method string,
    request_uri string,
    http_status int,
    response_size int
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
LOCATION 's3://my-bucket/logs/'
TBLPROPERTIES ('skip.header.line.count'='1');
```

#### Partitioned Table

```sql
-- Create partitioned table
CREATE EXTERNAL TABLE my_database.sales_data (
    order_id string,
    product_id string,
    quantity int,
    price decimal(10,2)
)
PARTITIONED BY (year int, month int, day int)
STORED AS PARQUET
LOCATION 's3://my-bucket/sales/';

-- Add partitions
ALTER TABLE my_database.sales_data ADD
PARTITION (year=2024, month=1, day=1) 
LOCATION 's3://my-bucket/sales/year=2024/month=1/day=1/';

-- Or use MSCK REPAIR to automatically discover partitions
MSCK REPAIR TABLE my_database.sales_data;
```

### Query Examples

```sql
-- Simple SELECT
SELECT * FROM my_database.web_logs
WHERE http_status = 404
LIMIT 100;

-- Aggregation
SELECT 
    DATE(request_timestamp) as date,
    COUNT(*) as request_count,
    SUM(response_size) as total_bytes
FROM my_database.web_logs
GROUP BY DATE(request_timestamp)
ORDER BY date DESC;

-- Join tables
SELECT 
    w.client_ip,
    u.username,
    COUNT(*) as visits
FROM my_database.web_logs w
JOIN my_database.users u ON w.user_id = u.id
GROUP BY w.client_ip, u.username;
```

### CTAS (Create Table As Select)

Convert data formats and create new tables:

```sql
-- Convert CSV to Parquet with partitioning
CREATE TABLE my_database.logs_parquet
WITH (
    format = 'PARQUET',
    external_location = 's3://my-bucket/logs-parquet/',
    partitioned_by = ARRAY['year', 'month']
) AS
SELECT 
    request_timestamp,
    client_ip,
    request_method,
    YEAR(DATE(request_timestamp)) as year,
    MONTH(DATE(request_timestamp)) as month
FROM my_database.web_logs;
```

---

## Performance Optimization

### Partitioning

```
┌─────────────────────────────────────────────────────────────────┐
│                   Partitioning Benefits                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Without Partitioning:                                         │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  Query: SELECT * FROM logs WHERE date = '2024-01-15'     │  │
│   │                                                          │  │
│   │  s3://bucket/logs/                                       │  │
│   │  ├── file1.parquet  ◄── SCANNED                         │  │
│   │  ├── file2.parquet  ◄── SCANNED                         │  │
│   │  ├── file3.parquet  ◄── SCANNED                         │  │
│   │  └── ... (all files) ◄── SCANNED                        │  │
│   │                                                          │  │
│   │  Result: Scans ALL data = High cost + Slow               │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│   With Partitioning:                                            │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  Query: SELECT * FROM logs WHERE date = '2024-01-15'     │  │
│   │                                                          │  │
│   │  s3://bucket/logs/                                       │  │
│   │  ├── date=2024-01-14/  (skipped)                        │  │
│   │  ├── date=2024-01-15/  ◄── ONLY THIS SCANNED            │  │
│   │  │   └── data.parquet                                    │  │
│   │  └── date=2024-01-16/  (skipped)                        │  │
│   │                                                          │  │
│   │  Result: Scans ONLY relevant partition = Low cost + Fast │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Columnar Formats

| Optimization | CSV | Parquet |
|-------------|-----|---------|
| Data scanned for 3 columns out of 100 | 100% | ~3% |
| Compression | None/minimal | Excellent |
| Query cost | $5/TB scanned | ~$0.50/TB or less |
| Query speed | Slow | Fast |

### Compression

Supported compression codecs:

| Format | Supported Compression |
|--------|----------------------|
| CSV/JSON | GZIP, LZO, SNAPPY, ZSTD |
| Parquet | SNAPPY (default), GZIP, LZO, ZSTD |
| ORC | SNAPPY, ZLIB, LZ4, ZSTD |

### File Size Optimization

```
┌─────────────────────────────────────────────────────────────────┐
│                   Optimal File Sizes                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Too Many Small Files:                                          │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  ├── file1.parquet (1 KB)                                │  │
│   │  ├── file2.parquet (2 KB)                                │  │
│   │  ├── file3.parquet (1 KB)                                │  │
│   │  └── ... (thousands of files)                            │  │
│   │                                                          │  │
│   │  Problem: Overhead for opening each file                 │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│   Too Large Files:                                               │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  └── giant_file.parquet (100 GB)                         │  │
│   │                                                          │  │
│   │  Problem: Cannot parallelize, no partition pruning       │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│   Optimal (128 MB - 512 MB per file):                           │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  ├── file1.parquet (256 MB)                              │  │
│   │  ├── file2.parquet (256 MB)                              │  │
│   │  ├── file3.parquet (256 MB)                              │  │
│   │  └── file4.parquet (256 MB)                              │  │
│   │                                                          │  │
│   │  Benefit: Good parallelism + efficient reading           │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Performance Best Practices Summary

1. **Use columnar formats** (Parquet, ORC) - up to 90% cost savings
2. **Partition data** by commonly filtered columns (date, region)
3. **Compress data** (SNAPPY for Parquet is default)
4. **Optimize file sizes** (128 MB - 512 MB per file)
5. **Use LIMIT** to reduce scanned data
6. **Select only needed columns** (avoid SELECT *)

---

## Federated Queries

### What are Federated Queries?

Federated queries allow Athena to query data from sources beyond S3 using Lambda-based data source connectors.

```
┌─────────────────────────────────────────────────────────────────┐
│                  Athena Federated Query                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌────────────────────────────────────────────────────────┐    │
│   │                     Athena Query                        │    │
│   │  SELECT * FROM s3_table t1                             │    │
│   │  JOIN dynamodb_table t2 ON t1.id = t2.id              │    │
│   │  JOIN rds_table t3 ON t1.user = t3.user               │    │
│   └────────────────────────────────────────────────────────┘    │
│                             │                                    │
│            ┌────────────────┼────────────────┐                  │
│            ▼                ▼                ▼                  │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│   │    S3        │  │   Lambda     │  │   Lambda     │         │
│   │   Direct     │  │  Connector   │  │  Connector   │         │
│   │   Access     │  │  (DynamoDB)  │  │    (RDS)     │         │
│   └──────────────┘  └──────┬───────┘  └──────┬───────┘         │
│                            ▼                 ▼                  │
│                    ┌──────────────┐  ┌──────────────┐          │
│                    │  DynamoDB    │  │   RDS        │          │
│                    │    Table     │  │  Database    │          │
│                    └──────────────┘  └──────────────┘          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Available Data Source Connectors

| Connector | Source |
|-----------|--------|
| Amazon DynamoDB | NoSQL tables |
| Amazon Redshift | Data warehouse |
| Amazon RDS | MySQL, PostgreSQL |
| Amazon OpenSearch | Search/log analytics |
| Amazon CloudWatch Logs | Log data |
| Amazon CloudWatch Metrics | Metrics data |
| HBase | Apache HBase |
| Redis | Redis cache |
| Custom | Any source via Lambda |

### Setting Up Federated Query

1. **Deploy connector** from AWS Serverless Application Repository
2. **Configure data source** in Athena console
3. **Create catalog** reference in Athena
4. **Query** using catalog.database.table syntax

```sql
-- Query DynamoDB table through federated connector
SELECT * 
FROM dynamodb_catalog.default.my_dynamodb_table
WHERE user_id = '12345';

-- Join S3 and DynamoDB data
SELECT s3.*, ddb.user_name
FROM awsdatacatalog.mydb.s3_table s3
JOIN dynamodb_catalog.default.users ddb 
ON s3.user_id = ddb.id;
```

---

## Integration with Other Services

### AWS Glue Integration

```
┌─────────────────────────────────────────────────────────────────┐
│               Athena + AWS Glue Integration                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌────────────────────────────────────────────────────────┐    │
│   │                 AWS Glue Data Catalog                   │    │
│   │  ┌──────────────────────────────────────────────────┐  │    │
│   │  │  Database: sales_db                              │  │    │
│   │  │  ├── Table: orders (schema, location, format)    │  │    │
│   │  │  ├── Table: customers                            │  │    │
│   │  │  └── Table: products                             │  │    │
│   │  └──────────────────────────────────────────────────┘  │    │
│   └────────────────────────────────────────────────────────┘    │
│                             │                                    │
│                Shared Metadata                                   │
│            ┌────────────────┼────────────────┐                  │
│            ▼                ▼                ▼                  │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│   │   Athena     │  │  AWS Glue    │  │   Redshift   │         │
│   │   Queries    │  │    ETL       │  │   Spectrum   │         │
│   └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                  │
│   Benefits:                                                      │
│   • Single source of truth for metadata                         │
│   • Automatic schema discovery with Glue Crawlers              │
│   • Shared tables across services                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Amazon QuickSight Integration

```
┌─────────────────────────────────────────────────────────────────┐
│              Athena + QuickSight BI Integration                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌────────────┐      ┌────────────┐      ┌────────────────┐   │
│   │    S3      │      │   Athena   │      │  QuickSight    │   │
│   │   Data     │ ───► │   Query    │ ───► │  Dashboards    │   │
│   │   Lake     │      │   Engine   │      │  & Reports     │   │
│   └────────────┘      └────────────┘      └────────────────┘   │
│                                                                  │
│   Use Cases:                                                     │
│   • Interactive dashboards on S3 data                           │
│   • Ad-hoc analysis without ETL                                 │
│   • Scheduled report generation                                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### CloudWatch Logs Integration

Query CloudWatch Logs directly from Athena:

```sql
-- Query VPC Flow Logs
SELECT 
    srcaddr,
    dstaddr,
    srcport,
    dstport,
    protocol,
    SUM(bytes) as total_bytes
FROM vpc_flow_logs
WHERE action = 'REJECT'
GROUP BY srcaddr, dstaddr, srcport, dstport, protocol
ORDER BY total_bytes DESC
LIMIT 10;
```

### CloudTrail Integration

```sql
-- Analyze CloudTrail logs with Athena
SELECT 
    eventTime,
    eventName,
    userIdentity.userName,
    sourceIPAddress,
    errorCode
FROM cloudtrail_logs
WHERE eventSource = 's3.amazonaws.com'
AND eventTime > DATE_ADD('day', -7, CURRENT_DATE)
ORDER BY eventTime DESC;
```

---

## Security

### Authentication and Access Control

```
┌─────────────────────────────────────────────────────────────────┐
│                   Athena Security Model                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   IAM Permissions Required:                                      │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │                                                          │  │
│   │   Athena Operations:                                     │  │
│   │   • athena:StartQueryExecution                          │  │
│   │   • athena:GetQueryExecution                            │  │
│   │   • athena:GetQueryResults                              │  │
│   │                                                          │  │
│   │   S3 Data Access:                                        │  │
│   │   • s3:GetObject (source data)                          │  │
│   │   • s3:GetBucketLocation                                │  │
│   │   • s3:ListBucket                                       │  │
│   │                                                          │  │
│   │   S3 Results:                                            │  │
│   │   • s3:PutObject (results bucket)                       │  │
│   │   • s3:GetObject (results bucket)                       │  │
│   │                                                          │  │
│   │   Glue Catalog:                                          │  │
│   │   • glue:GetDatabase                                    │  │
│   │   • glue:GetTable                                       │  │
│   │   • glue:GetPartitions                                  │  │
│   │                                                          │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Encryption

| Data | Encryption Options |
|------|-------------------|
| **Data at rest (S3)** | SSE-S3, SSE-KMS, CSE-KMS |
| **Query results** | SSE-S3, SSE-KMS, CSE-KMS |
| **Data in transit** | TLS encryption |
| **Metadata (Glue)** | Encrypted by default |

### Lake Formation Integration

```
┌─────────────────────────────────────────────────────────────────┐
│            Athena + Lake Formation Security                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌────────────────────────────────────────────────────────┐    │
│   │               Lake Formation                            │    │
│   │  ┌──────────────────────────────────────────────────┐  │    │
│   │  │  Fine-Grained Access Control                     │  │    │
│   │  │  • Table-level permissions                       │  │    │
│   │  │  • Column-level permissions                      │  │    │
│   │  │  • Row-level filtering                          │  │    │
│   │  │  • Cell-level security                          │  │    │
│   │  └──────────────────────────────────────────────────┘  │    │
│   └────────────────────────────────────────────────────────┘    │
│                             │                                    │
│                             ▼                                    │
│   ┌────────────────────────────────────────────────────────┐    │
│   │                     Athena                              │    │
│   │   Queries respect Lake Formation permissions           │    │
│   └────────────────────────────────────────────────────────┘    │
│                                                                  │
│   Example: User A can see columns 1,2,3                         │
│            User B can only see columns 1,2                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Cost Management

### Pricing Model

- **$5 per TB of data scanned**
- Minimum 10 MB per query
- No charges for failed queries
- DDL statements (CREATE, ALTER, DROP) are free

### Cost Optimization Strategies

```
┌─────────────────────────────────────────────────────────────────┐
│                Cost Optimization Strategies                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Strategy              │ Savings │ Effort │ Impact             │
│   ─────────────────────────────────────────────────────────     │
│   Use columnar formats  │  ~90%   │  Med   │  Significant       │
│   Partition data        │  ~80%   │  Med   │  Significant       │
│   Compress data         │  ~50%   │  Low   │  Moderate          │
│   Optimize file sizes   │  ~30%   │  Med   │  Moderate          │
│   SELECT specific cols  │  Varies │  Low   │  Varies            │
│   Use LIMIT clause      │  Varies │  Low   │  For exploration   │
│   Cache query results   │   100%  │  None  │  Repeated queries  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Cost Calculation Example

```
Scenario: Query 1 TB of log data daily

CSV (uncompressed, all columns):
• Data scanned: 1 TB × 30 days = 30 TB
• Cost: 30 TB × $5 = $150/month

Parquet (compressed, 3 of 50 columns):
• Compression: ~80% reduction = 200 GB
• Columnar: 3/50 cols = 6% of data
• Data scanned: 200 GB × 6% × 30 = ~360 GB
• Cost: 0.36 TB × $5 = $1.80/month

Savings: $150 - $1.80 = $148.20/month (~99%)
```

### Workgroup Data Usage Controls

```sql
-- Set query data limit (per query)
-- Maximum 100 GB per query

-- Set workgroup data limit (total)
-- Maximum 1 TB per day for workgroup
```

---

## Best Practices

### Data Organization

1. **Partition by frequently filtered columns** (date, region)
2. **Use Hive-style partitioning** (key=value folder structure)
3. **Keep partition count reasonable** (< 1 million partitions)
4. **Avoid over-partitioning** (not every column needs partitioning)

### Query Optimization

1. **Always filter on partition columns**
2. **Select only needed columns**
3. **Use LIMIT for exploration**
4. **Avoid SELECT \* in production**
5. **Use CTAS to create optimized tables**

### Schema Management

1. **Use AWS Glue crawlers** for schema discovery
2. **Version your schemas** for evolution
3. **Document table schemas** and purpose
4. **Use meaningful database/table names**

---

## SAA-C03 Exam Tips

### Key Concepts for Exam

1. **Serverless** = No infrastructure management
2. **Pay per query** = $5 per TB scanned
3. **S3 data source** = Data stays in S3
4. **Glue Data Catalog** = Metadata store
5. **Columnar formats** = Cost and performance optimization

### Common Exam Scenarios

#### Scenario 1: Ad-hoc S3 Queries
**Question**: Need to run SQL queries on S3 data without managing servers.
**Answer**: Amazon Athena

#### Scenario 2: Cost Optimization
**Question**: How to reduce Athena query costs?
**Answer**: Use columnar formats (Parquet/ORC), partition data, compress

#### Scenario 3: Log Analysis
**Question**: Analyze CloudTrail/VPC Flow Logs with SQL.
**Answer**: Athena (query logs directly in S3)

#### Scenario 4: BI Integration
**Question**: Build dashboards on S3 data lake.
**Answer**: Athena + QuickSight

### Exam Question Keywords

| Keyword | Usually Points To |
|---------|------------------|
| "Query S3 directly" | Athena |
| "Serverless SQL" | Athena |
| "Pay per query" | Athena |
| "Analyze logs with SQL" | Athena |
| "Data lake queries" | Athena |
| "Ad-hoc analysis" | Athena |
| "No ETL required" | Athena |

### Athena vs Other Services

```
┌─────────────────────────────────────────────────────────────────┐
│                Service Selection Guide                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Athena vs Redshift:                                           │
│   • Athena: Ad-hoc queries, pay per query, serverless          │
│   • Redshift: Data warehouse, complex analytics, provisioned   │
│                                                                  │
│   Athena vs EMR:                                                │
│   • Athena: Simple SQL queries, no cluster management          │
│   • EMR: Complex processing, Spark/Hadoop, more control        │
│                                                                  │
│   Athena vs Redshift Spectrum:                                  │
│   • Athena: Standalone S3 queries                               │
│   • Spectrum: Query S3 from Redshift (requires Redshift)       │
│                                                                  │
│   Decision: Choose Athena for:                                  │
│   • Ad-hoc queries                                              │
│   • Infrequent queries                                          │
│   • When you want to avoid infrastructure management            │
│   • Log analysis                                                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Practice Questions

### Question 1
A company stores log files in S3 in CSV format. They run daily queries that only need 5 columns out of 50. Query costs are too high. What should they do?

A) Move data to Amazon RDS  
B) Convert CSV to Parquet format  
C) Use Amazon Redshift instead  
D) Increase the number of S3 buckets  

**Answer: B** - Converting to Parquet (columnar format) reduces data scanned by only reading the 5 needed columns, reducing costs by up to 90%.

### Question 2
A data analyst needs to query CloudTrail logs stored in S3 to investigate a security incident. What's the FASTEST way to analyze this data?

A) Download logs and analyze locally  
B) Use Amazon Athena with SQL queries  
C) Import data into Amazon Redshift  
D) Process with AWS Lambda  

**Answer: B** - Athena allows immediate SQL queries on S3 data without any data movement or cluster setup.

### Question 3
A company wants to reduce Athena query costs. Their data is partitioned by date, but queries scan all partitions. What should they check?

A) Increase the query timeout  
B) Ensure queries include partition column in WHERE clause  
C) Move to a different AWS region  
D) Use smaller S3 storage class  

**Answer: B** - Queries must filter on partition columns (WHERE date = '2024-01-01') for Athena to use partition pruning.

### Question 4
Which combination provides the LOWEST cost for Athena queries?

A) CSV format, no compression, no partitioning  
B) JSON format, GZIP compression, partitioning  
C) Parquet format, SNAPPY compression, partitioning  
D) CSV format, GZIP compression, partitioning  

**Answer: C** - Parquet (columnar) + SNAPPY compression + partitioning provides the lowest data scanned and thus lowest cost.

### Question 5
A company needs to query data from both S3 and DynamoDB in a single SQL query. What Athena feature should they use?

A) Athena workgroups  
B) Athena federated queries  
C) Athena CTAS  
D) Athena views  

**Answer: B** - Federated queries allow Athena to query external data sources like DynamoDB using Lambda connectors.

---

## Summary

Amazon Athena is a serverless interactive query service for S3 data:

**Key Points**:
- **Serverless**: No infrastructure to manage
- **Pricing**: $5 per TB scanned
- **Integration**: Glue Data Catalog, QuickSight, Lake Formation
- **Performance**: Columnar formats, partitioning, compression
- **Federated**: Query multiple data sources

**Cost Optimization Formula**:
```
Columnar Format + Partitioning + Compression = Lowest Cost
```

**Best For**:
- Ad-hoc S3 queries
- Log analysis
- Data lake exploration
- Infrequent query patterns
