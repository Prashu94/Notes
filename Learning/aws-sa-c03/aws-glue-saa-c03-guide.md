# AWS Glue - SAA-C03 Comprehensive Guide

## Table of Contents
1. [Overview and Introduction](#overview-and-introduction)
2. [AWS Glue Components](#aws-glue-components)
3. [AWS Glue Data Catalog](#aws-glue-data-catalog)
4. [AWS Glue Crawlers](#aws-glue-crawlers)
5. [AWS Glue ETL Jobs](#aws-glue-etl-jobs)
6. [AWS Glue Studio](#aws-glue-studio)
7. [AWS Glue DataBrew](#aws-glue-databrew)
8. [Integration with Other Services](#integration-with-other-services)
9. [Security](#security)
10. [Pricing and Cost Optimization](#pricing-and-cost-optimization)
11. [Best Practices](#best-practices)
12. [SAA-C03 Exam Tips](#saa-c03-exam-tips)
13. [Practice Questions](#practice-questions)

---

## Overview and Introduction

### What is AWS Glue?

AWS Glue is a **fully managed, serverless ETL (Extract, Transform, Load) service** that makes it easy to prepare and transform data for analytics. It provides a central metadata repository (Data Catalog), ETL engine, and flexible scheduling.

### Key Characteristics

- **Serverless**: No infrastructure to provision or manage
- **Fully managed**: AWS handles scaling, provisioning, maintenance
- **Pay-per-use**: Charged for resources consumed during job execution
- **Integrated**: Works with S3, RDS, Redshift, Athena, and more

### Core Capabilities

1. **Data Catalog**: Central metadata repository
2. **ETL Jobs**: Transform data between sources
3. **Crawlers**: Automatic schema discovery
4. **Development**: Visual and code-based job authoring
5. **Scheduling**: Built-in job scheduling and triggers

### AWS Glue at a Glance

```
┌─────────────────────────────────────────────────────────────────┐
│                      AWS Glue Overview                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Data Sources              AWS Glue            Data Targets     │
│   ┌─────────────┐                              ┌─────────────┐  │
│   │    S3       │                              │    S3       │  │
│   │    RDS      │    ┌──────────────────┐     │  Redshift   │  │
│   │  DynamoDB   │───►│  Data Catalog    │────►│   Athena    │  │
│   │   JDBC      │    │  ETL Engine      │     │    EMR      │  │
│   │   Kafka     │    │  Job Scheduler   │     │   Glue DB   │  │
│   └─────────────┘    └──────────────────┘     └─────────────┘  │
│                                                                  │
│   Key Benefits:                                                  │
│   • Automatic schema discovery                                  │
│   • Code generation for ETL jobs                               │
│   • Serverless Spark execution                                  │
│   • Central metadata management                                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## AWS Glue Components

### Component Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                   AWS Glue Architecture                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │                    AWS Glue                               │  │
│   │                                                           │  │
│   │   ┌────────────────────────────────────────────────────┐ │  │
│   │   │              Data Catalog                           │ │  │
│   │   │  • Databases    • Tables    • Connections          │ │  │
│   │   │  • Schemas      • Partitions                       │ │  │
│   │   └────────────────────────────────────────────────────┘ │  │
│   │                                                           │  │
│   │   ┌────────────────────────────────────────────────────┐ │  │
│   │   │                  Crawlers                           │ │  │
│   │   │  • Scan data stores    • Infer schemas             │ │  │
│   │   │  • Populate catalog    • Detect changes            │ │  │
│   │   └────────────────────────────────────────────────────┘ │  │
│   │                                                           │  │
│   │   ┌────────────────────────────────────────────────────┐ │  │
│   │   │                 ETL Jobs                            │ │  │
│   │   │  • Spark-based      • Python/Scala                 │ │  │
│   │   │  • Visual editor    • Serverless                   │ │  │
│   │   └────────────────────────────────────────────────────┘ │  │
│   │                                                           │  │
│   │   ┌────────────────────────────────────────────────────┐ │  │
│   │   │               Triggers & Workflows                  │ │  │
│   │   │  • Scheduled      • On-demand    • Event-based     │ │  │
│   │   └────────────────────────────────────────────────────┘ │  │
│   │                                                           │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Component Summary

| Component | Purpose | Key Features |
|-----------|---------|--------------|
| **Data Catalog** | Metadata repository | Tables, databases, schemas |
| **Crawlers** | Schema discovery | Auto-detect formats, partitions |
| **ETL Jobs** | Data transformation | Spark-based, auto-scaling |
| **Triggers** | Job orchestration | Schedule, event, on-demand |
| **Workflows** | Multi-job pipelines | Dependencies, conditions |
| **Connections** | Data store access | JDBC, S3, Kafka |

---

## AWS Glue Data Catalog

### Overview

The AWS Glue Data Catalog is a **persistent, central metadata repository** that stores structural and operational metadata for all your data assets.

### Catalog Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                  Glue Data Catalog Structure                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   AWS Account (Region-specific)                                  │
│   └── Data Catalog                                               │
│       ├── Database: sales_db                                     │
│       │   ├── Table: orders                                      │
│       │   │   ├── Column: order_id (string)                     │
│       │   │   ├── Column: customer_id (string)                  │
│       │   │   ├── Column: amount (decimal)                      │
│       │   │   ├── Partition: year=2024/month=01                 │
│       │   │   └── Location: s3://bucket/orders/                 │
│       │   │                                                      │
│       │   └── Table: customers                                   │
│       │       ├── Column: id (string)                           │
│       │       ├── Column: name (string)                         │
│       │       └── Location: s3://bucket/customers/              │
│       │                                                          │
│       ├── Database: analytics_db                                 │
│       │   └── Table: aggregated_sales                           │
│       │                                                          │
│       └── Database: logs_db                                      │
│           └── Table: application_logs                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Key Catalog Features

#### 1. Tables
- Store schema definitions (columns, data types)
- Point to data location (S3, RDS, etc.)
- Track partitions
- Support table versioning

#### 2. Databases
- Logical grouping of tables
- Organize by department, project, environment
- Independent permissions possible

#### 3. Partitions
- Physical organization of data
- Enable query optimization
- Hive-style partitioning (key=value)

#### 4. Connections
- Define access to data stores
- Support JDBC, MongoDB, Kafka
- Store credentials securely

### Catalog Integration

```
┌─────────────────────────────────────────────────────────────────┐
│            Services Using Glue Data Catalog                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│                ┌────────────────────────┐                       │
│                │   Glue Data Catalog    │                       │
│                │   (Central Metadata)   │                       │
│                └───────────┬────────────┘                       │
│                            │                                     │
│      ┌─────────────────────┼─────────────────────┐              │
│      │          │          │          │          │              │
│      ▼          ▼          ▼          ▼          ▼              │
│   ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────────┐        │
│   │Athena│  │Glue  │  │ EMR  │  │Redshift│ │Lake      │        │
│   │      │  │Jobs  │  │      │  │Spectrum│ │Formation │        │
│   └──────┘  └──────┘  └──────┘  └──────┘  └──────────┘        │
│                                                                  │
│   Benefit: Single source of truth for all analytics services    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## AWS Glue Crawlers

### What are Crawlers?

Glue Crawlers are programs that **automatically scan data stores, identify data formats, infer schemas, and populate the Data Catalog** with table definitions.

### How Crawlers Work

```
┌─────────────────────────────────────────────────────────────────┐
│                   Crawler Workflow                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Step 1: Configure Crawler                                      │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  • Data store (S3 path, JDBC connection)                 │  │
│   │  • IAM role for access                                   │  │
│   │  • Target database in Data Catalog                       │  │
│   │  • Schedule (on-demand, hourly, daily, etc.)             │  │
│   └──────────────────────────────────────────────────────────┘  │
│                            ↓                                     │
│   Step 2: Crawler Runs                                           │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  • Connects to data store                                │  │
│   │  • Scans files/tables                                    │  │
│   │  • Identifies format (CSV, Parquet, JSON, etc.)          │  │
│   │  • Samples data to infer schema                          │  │
│   │  • Detects partitions                                    │  │
│   └──────────────────────────────────────────────────────────┘  │
│                            ↓                                     │
│   Step 3: Catalog Updated                                        │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  • Creates/updates tables in Data Catalog               │  │
│   │  • Stores column names, data types                       │  │
│   │  • Records partition information                         │  │
│   │  • Tracks schema changes                                 │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Crawler Configuration

#### Supported Data Stores

| Category | Data Stores |
|----------|-------------|
| **Amazon** | S3, DynamoDB, DocumentDB |
| **JDBC** | RDS, Redshift, Aurora, on-premises databases |
| **Streaming** | Kafka, Amazon MSK |

#### Classifiers

Classifiers determine the schema of data:

- **Built-in**: CSV, JSON, Parquet, ORC, Avro, XML
- **Custom**: Regular expressions, JSON patterns, Grok patterns

```
┌─────────────────────────────────────────────────────────────────┐
│              Crawler Classification Process                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Data File                   Classifier                Result   │
│   ┌────────────┐             ┌──────────────┐                   │
│   │ data.csv   │  ─────────► │ CSV Built-in │ ──► Table schema │
│   └────────────┘             └──────────────┘                   │
│                                                                  │
│   ┌────────────┐             ┌──────────────┐                   │
│   │ log.txt    │  ─────────► │ Custom Grok  │ ──► Table schema │
│   └────────────┘             └──────────────┘                   │
│                                                                  │
│   ┌────────────┐             ┌──────────────┐                   │
│   │ data.parquet│ ─────────► │ Parquet      │ ──► Table schema │
│   └────────────┘             └──────────────┘                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Crawler Best Practices

1. **Organize S3 data** in separate folders for different tables
2. **Use consistent formats** within a table's folder
3. **Schedule crawlers** to run after data updates
4. **Use prefixes** to limit what crawler scans
5. **Enable schema change detection** for evolving data

---

## AWS Glue ETL Jobs

### ETL Job Types

```
┌─────────────────────────────────────────────────────────────────┐
│                    Glue ETL Job Types                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  Spark Jobs                                               │  │
│   │  • Apache Spark-based                                    │  │
│   │  • Process large datasets (terabytes to petabytes)       │  │
│   │  • Parallel processing                                    │  │
│   │  • Write in Python (PySpark) or Scala                    │  │
│   │  • Auto-scaling with Glue 2.0+                           │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  Streaming ETL Jobs                                       │  │
│   │  • Process streaming data from Kinesis/Kafka              │  │
│   │  • Continuous processing or micro-batches                 │  │
│   │  • Real-time transformations                              │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  Python Shell Jobs                                        │  │
│   │  • Simple Python scripts                                  │  │
│   │  • Smaller datasets                                       │  │
│   │  • Good for simple transformations                        │  │
│   │  • Lower cost (1 DPU or 0.0625 DPU)                      │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Data Processing Units (DPUs)

| Job Type | Default DPU | DPU Resources |
|----------|-------------|---------------|
| Spark ETL | 10 DPU | 4 vCPUs, 16 GB memory per DPU |
| Streaming ETL | 2 DPU | Same as Spark |
| Python Shell | 1 DPU | 1 vCPU, 4 GB memory |
| Python Shell (fraction) | 0.0625 DPU | Minimal resources |

### ETL Script Components

```python
# Sample Glue ETL Job (PySpark)
import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

# Initialize
args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Extract: Read from Data Catalog
datasource = glueContext.create_dynamic_frame.from_catalog(
    database="sales_db",
    table_name="raw_orders"
)

# Transform: Apply transformations
transformed = ApplyMapping.apply(
    frame=datasource,
    mappings=[
        ("order_id", "string", "order_id", "string"),
        ("amount", "string", "amount", "decimal"),
        ("date", "string", "order_date", "date")
    ]
)

# Filter
filtered = Filter.apply(
    frame=transformed,
    f=lambda x: x["amount"] > 0
)

# Load: Write to S3 as Parquet
glueContext.write_dynamic_frame.from_options(
    frame=filtered,
    connection_type="s3",
    connection_options={
        "path": "s3://bucket/processed/orders/"
    },
    format="parquet"
)

job.commit()
```

### Dynamic Frames vs DataFrames

```
┌─────────────────────────────────────────────────────────────────┐
│           DynamicFrame vs Spark DataFrame                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   DynamicFrame (Glue):                                          │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  • Schema flexibility (handles inconsistent data)        │  │
│   │  • Self-describing records                               │  │
│   │  • Resolves schema ambiguities                          │  │
│   │  • Built-in transformations (ApplyMapping, etc.)        │  │
│   │  • Can convert to/from DataFrame                        │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│   Spark DataFrame:                                               │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  • Fixed schema                                          │  │
│   │  • Full Spark SQL support                               │  │
│   │  • Better for complex transformations                   │  │
│   │  • More familiar to Spark developers                    │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│   Conversion:                                                    │
│   DynamicFrame ──► toDF() ──► DataFrame                         │
│   DataFrame ──► fromDF() ──► DynamicFrame                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Common Transformations

| Transform | Description |
|-----------|-------------|
| **ApplyMapping** | Rename and cast columns |
| **Filter** | Filter rows based on condition |
| **Join** | Join two DynamicFrames |
| **SelectFields** | Select specific columns |
| **DropFields** | Remove columns |
| **ResolveChoice** | Handle data type ambiguities |
| **Relationalize** | Flatten nested structures |

---

## AWS Glue Studio

### Overview

AWS Glue Studio is a **visual interface** for creating, running, and monitoring Glue ETL jobs without writing code.

### Visual Job Editor

```
┌─────────────────────────────────────────────────────────────────┐
│                  Glue Studio Visual Editor                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌────────────────────────────────────────────────────────┐    │
│   │                    Job Canvas                           │    │
│   │                                                         │    │
│   │   ┌─────────────┐                                      │    │
│   │   │   Source    │    Data Catalog Table                │    │
│   │   │  (S3/RDS)   │                                      │    │
│   │   └──────┬──────┘                                      │    │
│   │          │                                              │    │
│   │          ▼                                              │    │
│   │   ┌─────────────┐                                      │    │
│   │   │ Transform 1 │    ApplyMapping                      │    │
│   │   │             │                                      │    │
│   │   └──────┬──────┘                                      │    │
│   │          │                                              │    │
│   │          ▼                                              │    │
│   │   ┌─────────────┐                                      │    │
│   │   │ Transform 2 │    Filter                            │    │
│   │   │             │                                      │    │
│   │   └──────┬──────┘                                      │    │
│   │          │                                              │    │
│   │          ▼                                              │    │
│   │   ┌─────────────┐                                      │    │
│   │   │   Target    │    S3 (Parquet)                      │    │
│   │   │             │                                      │    │
│   │   └─────────────┘                                      │    │
│   │                                                         │    │
│   └────────────────────────────────────────────────────────┘    │
│                                                                  │
│   Features:                                                      │
│   • Drag-and-drop job creation                                  │
│   • Auto-generates PySpark code                                 │
│   • Visual data preview                                         │
│   • One-click job deployment                                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Job Monitoring

Glue Studio provides:
- Real-time job status
- Data lineage visualization
- Execution metrics
- Error tracking
- CloudWatch integration

---

## AWS Glue DataBrew

### Overview

AWS Glue DataBrew is a **visual data preparation tool** for cleaning and normalizing data without writing code.

### Key Features

```
┌─────────────────────────────────────────────────────────────────┐
│                   Glue DataBrew Features                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │                    Projects                               │  │
│   │  • Connect to data source                                │  │
│   │  • Interactive data exploration                          │  │
│   │  • Apply transformations visually                        │  │
│   │  • Create recipes (transformation steps)                 │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │                    Recipes                                │  │
│   │  • Reusable transformation steps                         │  │
│   │  • 250+ built-in transformations                        │  │
│   │  • Version controlled                                    │  │
│   │  • Shareable across projects                            │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │                    Jobs                                   │  │
│   │  • Apply recipes to full datasets                        │  │
│   │  • Scheduled or on-demand                               │  │
│   │  • Output to S3                                         │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │                 Data Quality                              │  │
│   │  • Profile data automatically                            │  │
│   │  • Detect anomalies                                      │  │
│   │  • Validate data quality rules                          │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### DataBrew vs Glue ETL

| Aspect | Glue DataBrew | Glue ETL |
|--------|---------------|----------|
| **Target User** | Data analysts | Data engineers |
| **Interface** | Visual, no code | Code or visual |
| **Scale** | Moderate | Very large |
| **Complexity** | Simple transforms | Complex logic |
| **Data profiling** | Built-in | Manual |

---

## Integration with Other Services

### Athena Integration

```
┌─────────────────────────────────────────────────────────────────┐
│                 Glue + Athena Integration                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   1. Crawler populates Data Catalog                             │
│   ┌─────────────┐      ┌─────────────┐                         │
│   │   S3 Data   │ ───► │   Crawler   │                         │
│   └─────────────┘      └──────┬──────┘                         │
│                               │                                  │
│                               ▼                                  │
│                        ┌─────────────┐                          │
│                        │Data Catalog │                          │
│                        └──────┬──────┘                          │
│                               │                                  │
│   2. Athena uses catalog      │                                  │
│                               ▼                                  │
│                        ┌─────────────┐                          │
│                        │   Athena    │                          │
│                        │   Query     │                          │
│                        └─────────────┘                          │
│                                                                  │
│   Benefits:                                                      │
│   • Single metadata store                                       │
│   • Automatic schema updates                                    │
│   • Query data immediately after catalog update                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Redshift Integration

```
┌─────────────────────────────────────────────────────────────────┐
│                 Glue + Redshift Integration                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Use Cases:                                                     │
│                                                                  │
│   1. ETL to Redshift                                            │
│   ┌──────┐    ┌──────────┐    ┌──────────┐                     │
│   │  S3  │───►│ Glue ETL │───►│ Redshift │                     │
│   └──────┘    └──────────┘    └──────────┘                     │
│                                                                  │
│   2. Redshift Spectrum (query S3 via Glue Catalog)              │
│   ┌──────────┐    ┌─────────────┐    ┌──────┐                  │
│   │ Redshift │───►│Data Catalog │───►│  S3  │                  │
│   │ Spectrum │    │             │    │      │                  │
│   └──────────┘    └─────────────┘    └──────┘                  │
│                                                                  │
│   3. ETL from Redshift                                          │
│   ┌──────────┐    ┌──────────┐    ┌──────┐                     │
│   │ Redshift │───►│ Glue ETL │───►│  S3  │                     │
│   └──────────┘    └──────────┘    └──────┘                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Lake Formation Integration

```
┌─────────────────────────────────────────────────────────────────┐
│              Glue + Lake Formation Integration                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌────────────────────────────────────────────────────────┐    │
│   │               Lake Formation                            │    │
│   │  ┌──────────────────────────────────────────────────┐  │    │
│   │  │  Glue Data Catalog (shared)                      │  │    │
│   │  │  + Fine-grained permissions                      │  │    │
│   │  │  + Column-level security                         │  │    │
│   │  │  + Row-level filtering                          │  │    │
│   │  └──────────────────────────────────────────────────┘  │    │
│   └────────────────────────────────────────────────────────┘    │
│                                                                  │
│   Lake Formation uses Glue Data Catalog as its foundation       │
│   and adds governance, security, and access control features.   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Security

### IAM and Access Control

```
┌─────────────────────────────────────────────────────────────────┐
│                   Glue Security Model                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   IAM Roles:                                                     │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │                                                          │  │
│   │   Glue Service Role:                                     │  │
│   │   • glue:* permissions for Glue operations              │  │
│   │   • s3:GetObject, s3:PutObject for data access          │  │
│   │   • logs:* for CloudWatch Logs                          │  │
│   │                                                          │  │
│   │   Crawler Role:                                          │  │
│   │   • Read access to data stores                          │  │
│   │   • Write access to Data Catalog                        │  │
│   │                                                          │  │
│   │   ETL Job Role:                                          │  │
│   │   • Read/write to source and target data stores         │  │
│   │   • Access to Glue Data Catalog                         │  │
│   │   • CloudWatch Logs access                              │  │
│   │                                                          │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│   Resource Policies:                                             │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  • Data Catalog resource policy (cross-account access)   │  │
│   │  • Database/table permissions                            │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Encryption

| Data Type | Encryption Options |
|-----------|-------------------|
| **Data at rest** | S3 encryption (SSE-S3, SSE-KMS), RDS encryption |
| **Data Catalog** | Encrypted by default (AWS managed or CMK) |
| **Connection passwords** | Encrypted with KMS |
| **Job bookmarks** | Encrypted by default |
| **Development endpoints** | SSL/TLS |
| **Data in transit** | TLS encryption |

### VPC and Network Security

```
┌─────────────────────────────────────────────────────────────────┐
│                Glue in VPC Configuration                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌────────────────────────────────────────────────────────┐    │
│   │                        VPC                              │    │
│   │   ┌──────────────────────────────────────────────────┐ │    │
│   │   │               Private Subnet                      │ │    │
│   │   │                                                   │ │    │
│   │   │   ┌───────────────┐    ┌──────────────────────┐  │ │    │
│   │   │   │   Glue ETL    │    │    RDS Database      │  │ │    │
│   │   │   │   Job (ENI)   │───►│                      │  │ │    │
│   │   │   └───────────────┘    └──────────────────────┘  │ │    │
│   │   │           │                                       │ │    │
│   │   │           │ VPC Endpoint                          │ │    │
│   │   │           ▼                                       │ │    │
│   │   │   ┌───────────────┐                              │ │    │
│   │   │   │ S3 Endpoint   │                              │ │    │
│   │   │   └───────────────┘                              │ │    │
│   │   │                                                   │ │    │
│   │   └──────────────────────────────────────────────────┘ │    │
│   └────────────────────────────────────────────────────────┘    │
│                                                                  │
│   Requirements:                                                  │
│   • Glue connection with VPC/subnet/security group             │
│   • NAT gateway or VPC endpoints for AWS services              │
│   • Security group allowing outbound HTTPS                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Pricing and Cost Optimization

### Pricing Model

#### Glue ETL Jobs

| Component | Pricing |
|-----------|---------|
| **Apache Spark** | $0.44 per DPU-hour |
| **Python Shell** | $0.44 per DPU-hour |
| **Streaming ETL** | $0.44 per DPU-hour |
| **Minimum** | 1 minute, billed per second |

#### Data Catalog

| Component | Pricing |
|-----------|---------|
| **Storage** | First 1 million objects free, then $1 per 100K |
| **Requests** | First 1 million free, then $1 per million |

#### Crawlers

| Component | Pricing |
|-----------|---------|
| **Crawler runtime** | $0.44 per DPU-hour |
| **Minimum** | 10 minutes per run |

#### DataBrew

| Component | Pricing |
|-----------|---------|
| **Interactive sessions** | $1 per session (30 min) |
| **Job nodes** | $0.48 per node-hour |

### Cost Optimization Tips

1. **Right-size DPUs**: Start small, scale as needed
2. **Use auto-scaling** (Glue 2.0+) for dynamic workloads
3. **Enable job bookmarks**: Avoid reprocessing data
4. **Schedule wisely**: Run jobs during off-peak hours
5. **Compress output**: Reduce storage costs
6. **Use columnar formats**: Faster processing, lower costs
7. **Partition data**: Enable efficient querying

---

## Best Practices

### Job Development

1. **Use job bookmarks** to track processed data
2. **Enable continuous logging** for debugging
3. **Test with sample data** before production runs
4. **Use Glue Studio** for rapid prototyping
5. **Implement error handling** in scripts

### Data Organization

1. **Partition data** by commonly queried columns
2. **Use consistent file formats** within tables
3. **Optimize file sizes** (128 MB - 512 MB)
4. **Document table schemas** in catalog

### Performance

1. **Use Glue 3.0+** for latest optimizations
2. **Enable auto-scaling** for variable workloads
3. **Use pushdown predicates** to filter at source
4. **Coalesce small files** to reduce overhead
5. **Monitor and tune DPU allocation**

---

## SAA-C03 Exam Tips

### Key Concepts

1. **Glue = Serverless ETL** service
2. **Data Catalog = Central metadata** repository
3. **Crawlers = Automatic schema** discovery
4. **Shared catalog** with Athena, EMR, Redshift Spectrum

### Common Exam Scenarios

#### Scenario 1: Schema Discovery
**Question**: Need to automatically discover schema of S3 data.
**Answer**: AWS Glue Crawler

#### Scenario 2: ETL without Servers
**Question**: Transform data from S3 to Redshift, serverless.
**Answer**: AWS Glue ETL job

#### Scenario 3: Central Metadata
**Question**: Share table definitions between Athena and EMR.
**Answer**: AWS Glue Data Catalog

#### Scenario 4: Data Preparation
**Question**: Clean and normalize data visually without code.
**Answer**: AWS Glue DataBrew

### Exam Question Keywords

| Keyword | Usually Points To |
|---------|------------------|
| "Serverless ETL" | AWS Glue |
| "Schema discovery" | Glue Crawler |
| "Central metadata" | Glue Data Catalog |
| "Transform S3 data" | Glue ETL Job |
| "No-code data prep" | Glue DataBrew |
| "Share tables with Athena" | Glue Data Catalog |

### Glue vs Other Services

```
┌─────────────────────────────────────────────────────────────────┐
│                Service Comparison Guide                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Glue vs EMR:                                                  │
│   • Glue: Serverless, managed, simpler                         │
│   • EMR: Full control, complex processing, Hadoop ecosystem    │
│                                                                  │
│   Glue vs Data Pipeline:                                        │
│   • Glue: Serverless ETL, Spark-based                          │
│   • Data Pipeline: Orchestration, EC2-based, scheduled tasks   │
│                                                                  │
│   Glue vs Lambda:                                               │
│   • Glue: Large-scale ETL, minutes to hours                    │
│   • Lambda: Small transformations, max 15 minutes              │
│                                                                  │
│   Glue vs Kinesis Data Analytics:                               │
│   • Glue Streaming: Batch-oriented streaming                   │
│   • Kinesis Analytics: Real-time SQL on streams                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Practice Questions

### Question 1
A company has data in S3 in various formats (CSV, JSON, Parquet). They want to automatically discover schemas and make data queryable with Athena. What should they use?

A) AWS Lambda to read files and create schemas  
B) AWS Glue Crawlers to discover schemas and populate Data Catalog  
C) Amazon EMR to process and catalog data  
D) Amazon Redshift Spectrum  

**Answer: B** - Glue Crawlers automatically discover schemas from S3 data and populate the Data Catalog, which Athena uses for queries.

### Question 2
A data engineering team needs to transform terabytes of data from S3 to Parquet format without managing servers. What's the BEST solution?

A) EC2 instances with custom ETL scripts  
B) AWS Glue ETL job  
C) AWS Lambda functions  
D) Amazon EMR cluster  

**Answer: B** - Glue ETL is serverless, scales automatically, and is designed for transforming large datasets.

### Question 3
Which AWS services share the AWS Glue Data Catalog for metadata? (Select THREE)

A) Amazon Athena  
B) Amazon Redshift Spectrum  
C) Amazon EMR  
D) Amazon DynamoDB  
E) Amazon RDS  

**Answer: A, B, C** - Athena, Redshift Spectrum, and EMR can all use the Glue Data Catalog as their metadata store. DynamoDB and RDS are data stores, not catalog consumers.

### Question 4
A company wants to clean and normalize data without writing code. Which AWS service should they use?

A) AWS Glue ETL  
B) AWS Glue DataBrew  
C) AWS Lambda  
D) Amazon EMR  

**Answer: B** - Glue DataBrew provides a visual, no-code interface for data preparation and cleaning.

### Question 5
An organization needs to run Glue ETL jobs that access an RDS database in a private subnet. What must be configured?

A) Public IP for Glue  
B) Glue connection with VPC configuration  
C) Direct Connect  
D) S3 Gateway endpoint  

**Answer: B** - Glue jobs need a connection configured with VPC, subnet, and security group to access resources in private subnets.

---

## Summary

AWS Glue is a fully managed ETL service with these key components:

**Core Components**:
- **Data Catalog**: Central metadata repository (shared with Athena, EMR)
- **Crawlers**: Automatic schema discovery
- **ETL Jobs**: Serverless Spark-based transformations
- **DataBrew**: Visual data preparation

**Key Points for SAA-C03**:
1. Glue = Serverless ETL
2. Data Catalog is shared across services
3. Crawlers auto-discover schemas
4. Use for large-scale transformations
5. Integrates with S3, Redshift, Athena, Lake Formation

**Cost Formula**:
```
Cost = DPU-hours × $0.44
```
