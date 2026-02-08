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
13. [AWS CLI Commands Reference](#aws-cli-commands-reference)
14. [Practice Questions](#practice-questions)

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

## AWS CLI Commands Reference

### Prerequisites

```bash
# Install AWS CLI
# Visit: https://aws.amazon.com/cli/

# Configure AWS CLI
aws configure

# Verify configuration
aws sts get-caller-identity
```

### Database Operations

#### Create Database

```bash
# Create a database in Glue Data Catalog
aws glue create-database \
    --database-input '{
        "Name": "sales_database",
        "Description": "Database for sales data"
    }'

# Create database with location
aws glue create-database \
    --database-input '{
        "Name": "analytics_db",
        "Description": "Analytics database",
        "LocationUri": "s3://my-data-bucket/analytics/"
    }'

# Create database with parameters
aws glue create-database \
    --database-input '{
        "Name": "logs_db",
        "Description": "Application logs database",
        "Parameters": {
            "classification": "json",
            "compressionType": "gzip"
        }
    }'
```

#### List and Get Databases

```bash
# List all databases
aws glue get-databases

# List databases with pagination
aws glue get-databases --max-results 50

# Get specific database
aws glue get-database --name sales_database

# Search databases
aws glue get-databases \
    --query "DatabaseList[?contains(Name, 'prod')]"
```

#### Update Database

```bash
# Update database description
aws glue update-database \
    --name sales_database \
    --database-input '{
        "Name": "sales_database",
        "Description": "Updated sales data database"
    }'
```

#### Delete Database

```bash
# Delete a database (must be empty)
aws glue delete-database --name old_database
```

### Table Operations

#### Create Table

```bash
# Create table for CSV data
aws glue create-table \
    --database-name sales_database \
    --table-input '{
        "Name": "orders",
        "StorageDescriptor": {
            "Columns": [
                {"Name": "order_id", "Type": "bigint"},
                {"Name": "customer_id", "Type": "int"},
                {"Name": "order_date", "Type": "date"},
                {"Name": "amount", "Type": "decimal(10,2)"},
                {"Name": "status", "Type": "string"}
            ],
            "Location": "s3://my-data-bucket/orders/",
            "InputFormat": "org.apache.hadoop.mapred.TextInputFormat",
            "OutputFormat": "org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat",
            "SerdeInfo": {
                "SerializationLibrary": "org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe",
                "Parameters": {
                    "field.delim": ",",
                    "skip.header.line.count": "1"
                }
            }
        }
    }'

# Create table for Parquet data
aws glue create-table \
    --database-name sales_database \
    --table-input '{
        "Name": "transactions",
        "StorageDescriptor": {
            "Columns": [
                {"Name": "transaction_id", "Type": "bigint"},
                {"Name": "user_id", "Type": "int"},
                {"Name": "amount", "Type": "decimal(10,2)"},
                {"Name": "timestamp", "Type": "timestamp"}
            ],
            "Location": "s3://my-data-bucket/transactions/",
            "InputFormat": "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat",
            "OutputFormat": "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat",
            "SerdeInfo": {
                "SerializationLibrary": "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
            },
            "Compressed": true
        }
    }'

# Create partitioned table
aws glue create-table \
    --database-name sales_database \
    --table-input '{
        "Name": "sales",
        "StorageDescriptor": {
            "Columns": [
                {"Name": "sale_id", "Type": "bigint"},
                {"Name": "product_id", "Type": "int"},
                {"Name": "quantity", "Type": "int"},
                {"Name": "amount", "Type": "decimal(10,2)"}
            ],
            "Location": "s3://my-data-bucket/sales/",
            "InputFormat": "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat",
            "OutputFormat": "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat",
            "SerdeInfo": {
                "SerializationLibrary": "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
            }
        },
        "PartitionKeys": [
            {"Name": "year", "Type": "int"},
            {"Name": "month", "Type": "int"},
            {"Name": "day", "Type": "int"}
        ]
    }'
```

#### List and Get Tables

```bash
# List all tables in a database
aws glue get-tables --database-name sales_database

# Get specific table
aws glue get-table \
    --database-name sales_database \
    --name orders

# Get multiple tables
aws glue batch-get-table \
    --database-name sales_database \
    --tables-to-get orders transactions sales

# Search tables with filter
aws glue search-tables \
    --filters "[{\"Key\":\"TABLE_NAME\",\"Value\":\"order*\"}]"
```

#### Update Table

```bash
# Update table schema
aws glue update-table \
    --database-name sales_database \
    --table-input '{
        "Name": "orders",
        "StorageDescriptor": {
            "Columns": [
                {"Name": "order_id", "Type": "bigint"},
                {"Name": "customer_id", "Type": "int"},
                {"Name": "order_date", "Type": "date"},
                {"Name": "amount", "Type": "decimal(10,2)"},
                {"Name": "status", "Type": "string"},
                {"Name": "created_at", "Type": "timestamp"}
            ],
            "Location": "s3://my-data-bucket/orders/"
        }
    }'
```

#### Delete Table

```bash
# Delete table
aws glue delete-table \
    --database-name sales_database \
    --name old_orders

# Batch delete tables
aws glue batch-delete-table \
    --database-name sales_database \
    --tables-to-delete old_table1 old_table2 old_table3
```

#### Partition Operations

```bash
# Create partition
aws glue create-partition \
    --database-name sales_database \
    --table-name sales \
    --partition-input '{
        "Values": ["2024", "1", "15"],
        "StorageDescriptor": {
            "Location": "s3://my-data-bucket/sales/year=2024/month=1/day=15/",
            "InputFormat": "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat",
            "OutputFormat": "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat",
            "SerdeInfo": {
                "SerializationLibrary": "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
            }
        }
    }'

# Get partitions
aws glue get-partitions \
    --database-name sales_database \
    --table-name sales

# Get specific partition
aws glue get-partition \
    --database-name sales_database \
    --table-name sales \
    --partition-values 2024 1 15

# Batch create partitions
aws glue batch-create-partition \
    --database-name sales_database \
    --table-name sales \
    --partition-input-list file://partitions.json

# Delete partition
aws glue delete-partition \
    --database-name sales_database \
    --table-name sales \
    --partition-values 2023 12 31
```

### Crawler Operations

#### Create Crawler

```bash
# Create basic crawler for S3
aws glue create-crawler \
    --name "s3-sales-crawler" \
    --role "arn:aws:iam::123456789012:role/AWSGlueServiceRole" \
    --database-name "sales_database" \
    --targets '{
        "S3Targets": [
            {"Path": "s3://my-data-bucket/sales/"}
        ]
    }'

# Create crawler with multiple S3 paths
aws glue create-crawler \
    --name "multi-path-crawler" \
    --role "arn:aws:iam::123456789012:role/AWSGlueServiceRole" \
    --database-name "sales_database" \
    --targets '{
        "S3Targets": [
            {"Path": "s3://my-data-bucket/orders/"},
            {"Path": "s3://my-data-bucket/customers/"},
            {"Path": "s3://my-data-bucket/products/"}
        ]
    }'

# Create crawler with classifier
aws glue create-crawler \
    --name "custom-format-crawler" \
    --role "arn:aws:iam::123456789012:role/AWSGlueServiceRole" \
    --database-name "sales_database" \
    --targets '{"S3Targets": [{"Path": "s3://my-data-bucket/custom/"}]}' \
    --classifiers "custom-csv-classifier"

# Create crawler with schedule
aws glue create-crawler \
    --name "scheduled-crawler" \
    --role "arn:aws:iam::123456789012:role/AWSGlueServiceRole" \
    --database-name "sales_database" \
    --targets '{"S3Targets": [{"Path": "s3://my-data-bucket/sales/"}]}' \
    --schedule "cron(0 2 * * ? *)"  # Daily at 2 AM UTC

# Create crawler for JDBC database
aws glue create-crawler \
    --name "rds-crawler" \
    --role "arn:aws:iam::123456789012:role/AWSGlueServiceRole" \
    --database-name "rds_catalog" \
    --targets '{
        "JdbcTargets": [
            {
                "ConnectionName": "rds-connection",
                "Path": "mydb/%"
            }
        ]
    }'

# Create crawler with schema change policy
aws glue create-crawler \
    --name "schema-aware-crawler" \
    --role "arn:aws:iam::123456789012:role/AWSGlueServiceRole" \
    --database-name "sales_database" \
    --targets '{"S3Targets": [{"Path": "s3://my-data-bucket/sales/"}]}' \
    --schema-change-policy '{
        "UpdateBehavior": "UPDATE_IN_DATABASE",
        "DeleteBehavior": "LOG"
    }'
```

#### Start and Stop Crawler

```bash
# Start crawler
aws glue start-crawler --name "s3-sales-crawler"

# Stop crawler
aws glue stop-crawler --name "s3-sales-crawler"

# Check crawler status
aws glue get-crawler --name "s3-sales-crawler"
```

#### List and Get Crawlers

```bash
# List all crawlers
aws glue list-crawlers

# Get crawler details
aws glue get-crawler --name "s3-sales-crawler"

# Get multiple crawlers
aws glue batch-get-crawlers --crawler-names s3-sales-crawler rds-crawler

# List crawler metrics
aws glue get-crawler-metrics --crawler-name-list s3-sales-crawler
```

#### Update Crawler

```bash
# Update crawler targets
aws glue update-crawler \
    --name "s3-sales-crawler" \
    --targets '{
        "S3Targets": [
            {"Path": "s3://my-data-bucket/sales/"},
            {"Path": "s3://my-data-bucket/returns/"}
        ]
    }'

# Update crawler schedule
aws glue update-crawler \
    --name "s3-sales-crawler" \
    --schedule "cron(0 4 * * ? *)"  # Daily at 4 AM UTC
```

#### Delete Crawler

```bash
# Delete crawler
aws glue delete-crawler --name "old-crawler"
```

### ETL Job Operations

#### Create ETL Job

```bash
# Create Spark ETL job
aws glue create-job \
    --name "sales-etl-job" \
    --role "arn:aws:iam::123456789012:role/AWSGlueServiceRole" \
    --command '{
        "Name": "glueetl",
        "ScriptLocation": "s3://my-scripts-bucket/sales-transform.py",
        "PythonVersion": "3"
    }' \
    --default-arguments '{
        "--TempDir": "s3://my-temp-bucket/temp/",
        "--job-bookmark-option": "job-bookmark-enable",
        "--enable-metrics": "true",
        "--enable-continuous-cloudwatch-log": "true"
    }' \
    --max-retries 1 \
    --timeout 60 \
    --glue-version "4.0" \
    --number-of-workers 10 \
    --worker-type "G.1X"

# Create Python Shell job
aws glue create-job \
    --name "data-validation-job" \
    --role "arn:aws:iam::123456789012:role/AWSGlueServiceRole" \
    --command '{
        "Name": "pythonshell",
        "ScriptLocation": "s3://my-scripts-bucket/validate.py",
        "PythonVersion": "3.9"
    }' \
    --max-capacity 1.0

# Create streaming job
aws glue create-job \
    --name "kinesis-streaming-job" \
    --role "arn:aws:iam::123456789012:role/AWSGlueServiceRole" \
    --command '{
        "Name": "gluestreaming",
        "ScriptLocation": "s3://my-scripts-bucket/stream-processing.py",
        "PythonVersion": "3"
    }' \
    --default-arguments '{
        "--TempDir": "s3://my-temp-bucket/temp/",
        "--job-bookmark-option": "job-bookmark-disable"
    }' \
    --glue-version "4.0" \
    --number-of-workers 5 \
    --worker-type "G.1X"

# Create job with connections
aws glue create-job \
    --name "rds-etl-job" \
    --role "arn:aws:iam::123456789012:role/AWSGlueServiceRole" \
    --command '{
        "Name": "glueetl",
        "ScriptLocation": "s3://my-scripts-bucket/rds-transform.py"
    }' \
    --connections '{"Connections": ["rds-connection"]}' \
    --glue-version "4.0" \
    --number-of-workers 5 \
    --worker-type "G.1X"
```

#### Start and Monitor Jobs

```bash
# Start job run
aws glue start-job-run --job-name "sales-etl-job"

# Start job with arguments
aws glue start-job-run \
    --job-name "sales-etl-job" \
    --arguments '{
        "--input_path": "s3://my-data-bucket/input/2024-01-15/",
        "--output_path": "s3://my-data-bucket/output/2024-01-15/"
    }'

# Start job with custom worker configuration
aws glue start-job-run \
    --job-name "sales-etl-job" \
    --number-of-workers 20 \
    --worker-type "G.2X"

# Get job run status
aws glue get-job-run \
    --job-name "sales-etl-job" \
    --run-id "jr_abc123"

# List job runs
aws glue get-job-runs \
    --job-name "sales-etl-job" \
    --max-results 50

# Get job runs by status
aws glue get-job-runs \
    --job-name "sales-etl-job" \
    --query "JobRuns[?JobRunState=='SUCCEEDED']"
```

#### List and Get Jobs

```bash
# List all jobs
aws glue list-jobs

# Get job details
aws glue get-job --job-name "sales-etl-job"

# Batch get jobs
aws glue batch-get-jobs --job-names sales-etl-job data-validation-job
```

#### Update Job

```bash
# Update job configuration
aws glue update-job \
    --job-name "sales-etl-job" \
    --job-update '{
        "Role": "arn:aws:iam::123456789012:role/AWSGlueServiceRole",
        "Command": {
            "Name": "glueetl",
            "ScriptLocation": "s3://my-scripts-bucket/sales-transform-v2.py"
        },
        "NumberOfWorkers": 15,
        "WorkerType": "G.2X"
    }'
```

#### Delete Job

```bash
# Delete job
aws glue delete-job --job-name "old-etl-job"

# Batch delete jobs
aws glue batch-delete-job --job-names old-job1 old-job2 old-job3
```

#### Stop Job Run

```bash
# Stop a running job
aws glue batch-stop-job-run \
    --job-name "sales-etl-job" \
    --job-run-ids "jr_abc123" "jr_def456"
```

### Connection Operations

#### Create Connection

```bash
# Create JDBC connection for RDS
aws glue create-connection \
    --connection-input '{
        "Name": "rds-postgres-connection",
        "Description": "Connection to RDS PostgreSQL",
        "ConnectionType": "JDBC",
        "ConnectionProperties": {
            "JDBC_CONNECTION_URL": "jdbc:postgresql://mydb.us-east-1.rds.amazonaws.com:5432/mydb",
            "USERNAME": "admin",
            "PASSWORD": "MySecurePassword123"
        },
        "PhysicalConnectionRequirements": {
            "SubnetId": "subnet-12345678",
            "SecurityGroupIdList": ["sg-12345678"],
            "AvailabilityZone": "us-east-1a"
        }
    }'

# Create connection for Redshift
aws glue create-connection \
    --connection-input '{
        "Name": "redshift-connection",
        "ConnectionType": "JDBC",
        "ConnectionProperties": {
            "JDBC_CONNECTION_URL": "jdbc:redshift://my-cluster.us-east-1.redshift.amazonaws.com:5439/dev",
            "USERNAME": "admin",
            "PASSWORD": "MySecurePassword123"
        },
        "PhysicalConnectionRequirements": {
            "SubnetId": "subnet-12345678",
            "SecurityGroupIdList": ["sg-12345678"]
        }
    }'

# Create MongoDB connection
aws glue create-connection \
    --connection-input '{
        "Name": "mongodb-connection",
        "ConnectionType": "MONGODB",
        "ConnectionProperties": {
            "CONNECTION_URL": "mongodb://username:password@mongodb-server:27017/",
            "DATABASE": "myapp"
        }
    }'

# Create Kafka connection
aws glue create-connection \
    --connection-input '{
        "Name": "kafka-connection",
        "ConnectionType": "KAFKA",
        "ConnectionProperties": {
            "KAFKA_BOOTSTRAP_SERVERS": "broker1:9092,broker2:9092"
        }
    }'
```

#### List and Get Connections

```bash
# List all connections
aws glue get-connections

# Get specific connection
aws glue get-connection --name "rds-postgres-connection"

# Get connection with credentials hidden
aws glue get-connection \
    --name "rds-postgres-connection" \
    --hide-password
```

#### Update Connection

```bash
# Update connection properties
aws glue update-connection \
    --name "rds-postgres-connection" \
    --connection-input '{
        "Name": "rds-postgres-connection",
        "ConnectionType": "JDBC",
        "ConnectionProperties": {
            "JDBC_CONNECTION_URL": "jdbc:postgresql://new-db.us-east-1.rds.amazonaws.com:5432/mydb",
            "USERNAME": "admin",
            "PASSWORD": "NewPassword123"
        }
    }'
```

#### Delete Connection

```bash
# Delete connection
aws glue delete-connection --connection-name "old-connection"

# Batch delete connections
aws glue batch-delete-connection \
    --connection-name-list old-conn1 old-conn2
```

### Trigger Operations

#### Create Triggers

```bash
# Create scheduled trigger
aws glue create-trigger \
    --name "daily-etl-trigger" \
    --type "SCHEDULED" \
    --schedule "cron(0 3 * * ? *)" \
    --actions '[{"JobName": "sales-etl-job"}]' \
    --start-on-creation

# Create on-demand trigger
aws glue create-trigger \
    --name "manual-trigger" \
    --type "ON_DEMAND" \
    --actions '[{"JobName": "sales-etl-job"}]'

# Create conditional trigger (job dependency)
aws glue create-trigger \
    --name "chained-etl-trigger" \
    --type "CONDITIONAL" \
    --actions '[{"JobName": "transform-job"}]' \
    --predicate '{
        "Logical": "AND",
        "Conditions": [
            {
                "LogicalOperator": "EQUALS",
                "JobName": "extract-job",
                "State": "SUCCEEDED"
            }
        ]
    }' \
    --start-on-creation

# Create trigger with multiple actions
aws glue create-trigger \
    --name "multi-job-trigger" \
    --type "SCHEDULED" \
    --schedule "cron(0 2 * * ? *)" \
    --actions '[
        {"JobName": "job1"},
        {"JobName": "job2"},
        {"JobName": "job3"}
    ]' \
    --start-on-creation

# Create event-based trigger
aws glue create-trigger \
    --name "event-trigger" \
    --type "EVENT" \
    --actions '[{"JobName": "process-new-data"}]' \
    --event-batching-condition '{
        "BatchSize": 5,
        "BatchWindow": 900
    }'
```

#### Start and Stop Triggers

```bash
# Start trigger
aws glue start-trigger --name "daily-etl-trigger"

# Stop trigger
aws glue stop-trigger --name "daily-etl-trigger"
```

#### List and Get Triggers

```bash
# List all triggers
aws glue list-triggers

# Get trigger details
aws glue get-trigger --name "daily-etl-trigger"

# Get multiple triggers
aws glue batch-get-triggers \
    --trigger-names daily-etl-trigger manual-trigger
```

#### Update Trigger

```bash
# Update trigger schedule
aws glue update-trigger \
    --name "daily-etl-trigger" \
    --trigger-update '{
        "Schedule": "cron(0 4 * * ? *)",
        "Actions": [{"JobName": "sales-etl-job"}]
    }'
```

#### Delete Trigger

```bash
# Delete trigger
aws glue delete-trigger --name "old-trigger"
```

### Data Catalog Operations

#### Add Metadata Tags

```bash
# Tag database
aws glue tag-resource \
    --resource-arn "arn:aws:glue:us-east-1:123456789012:database/sales_database" \
    --tags-to-add '{"Environment": "Production", "Team": "Analytics"}'

# Tag table
aws glue tag-resource \
    --resource-arn "arn:aws:glue:us-east-1:123456789012:table/sales_database/orders" \
    --tags-to-add '{"Classification": "PII", "Owner": "DataTeam"}'

# List tags
aws glue get-tags \
    --resource-arn "arn:aws:glue:us-east-1:123456789012:database/sales_database"

# Remove tags
aws glue untag-resource \
    --resource-arn "arn:aws:glue:us-east-1:123456789012:database/sales_database" \
    --tags-to-remove "OldTag"
```

#### Import and Export Catalog

```bash
# Import catalog from file
aws glue import-catalog-to-glue \
    --catalog-id "123456789012"

# Get catalog import status
aws glue get-catalog-import-status \
    --catalog-id "123456789012"
```

### Development Endpoint Operations

#### Create Development Endpoint

```bash
# Create development endpoint
aws glue create-dev-endpoint \
    --endpoint-name "dev-endpoint-1" \
    --role-arn "arn:aws:iam::123456789012:role/AWSGlueServiceRole" \
    --security-group-ids "sg-12345678" \
    --subnet-id "subnet-12345678" \
    --number-of-nodes 2 \
    --glue-version "4.0"

# Create endpoint with public key
aws glue create-dev-endpoint \
    --endpoint-name "dev-endpoint-2" \
    --role-arn "arn:aws:iam::123456789012:role/AWSGlueServiceRole" \
    --public-key "ssh-rsa AAAAB3NzaC1yc2E..." \
    --number-of-nodes 2
```

#### List and Get Development Endpoints

```bash
# List all development endpoints
aws glue get-dev-endpoints

# Get specific endpoint
aws glue get-dev-endpoint --endpoint-name "dev-endpoint-1"

# Batch get endpoints
aws glue batch-get-dev-endpoints \
    --dev-endpoint-names dev-endpoint-1 dev-endpoint-2
```

#### Update Development Endpoint

```bash
# Update endpoint
aws glue update-dev-endpoint \
    --endpoint-name "dev-endpoint-1" \
    --public-key "ssh-rsa NEW_PUBLIC_KEY..."
```

#### Delete Development Endpoint

```bash
# Delete endpoint
aws glue delete-dev-endpoint --endpoint-name "dev-endpoint-1"
```

### ML Transform Operations

#### Create ML Transform

```bash
# Create ML transform for deduplication
aws glue create-ml-transform \
    --name "customer-dedup-transform" \
    --role "arn:aws:iam::123456789012:role/AWSGlueServiceRole" \
    --input-record-tables '[{
        "DatabaseName": "sales_database",
        "TableName": "customers"
    }]' \
    --parameters '{
        "TransformType": "FIND_MATCHES",
        "FindMatchesParameters": {
            "PrimaryKeyColumnName": "customer_id",
            "PrecisionRecallTradeoff": 0.5,
            "AccuracyCostTradeoff": 0.5
        }
    }' \
    --max-capacity 5.0
```

#### Start ML Transform

```bash
# Start ML transform
aws glue start-ml-evaluation-task-run \
    --transform-id "tfm-abc123"

# Start ML labeling task
aws glue start-ml-labeling-set-generation-task-run \
    --transform-id "tfm-abc123" \
    --output-s3-path "s3://my-ml-bucket/labeling/"
```

#### List and Get ML Transforms

```bash
# List ML transforms
aws glue list-ml-transforms

# Get ML transform
aws glue get-ml-transform --transform-id "tfm-abc123"

# Get ML task runs
aws glue get-ml-task-runs --transform-id "tfm-abc123"
```

#### Delete ML Transform

```bash
# Delete ML transform
aws glue delete-ml-transform --transform-id "tfm-abc123"
```

### Security Configuration Operations

#### Create Security Configuration

```bash
# Create security configuration with S3 encryption
aws glue create-security-configuration \
    --name "s3-encryption-config" \
    --encryption-configuration '{
        "S3Encryption": [
            {
                "S3EncryptionMode": "SSE-KMS",
                "KmsKeyArn": "arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789abc"
            }
        ],
        "CloudWatchEncryption": {
            "CloudWatchEncryptionMode": "SSE-KMS",
            "KmsKeyArn": "arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789abc"
        },
        "JobBookmarksEncryption": {
            "JobBookmarksEncryptionMode": "CSE-KMS",
            "KmsKeyArn": "arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789abc"
        }
    }'
```

#### List and Get Security Configurations

```bash
# List security configurations
aws glue get-security-configurations

# Get specific security configuration
aws glue get-security-configuration \
    --name "s3-encryption-config"
```

#### Delete Security Configuration

```bash
# Delete security configuration
aws glue delete-security-configuration \
    --name "old-security-config"
```

### Workflow Operations

```bash
# Create workflow
aws glue create-workflow \
    --name "sales-data-pipeline" \
    --description "Complete sales data processing pipeline"

# Get workflow
aws glue get-workflow --name "sales-data-pipeline"

# Start workflow run
aws glue start-workflow-run --name "sales-data-pipeline"

# Get workflow run
aws glue get-workflow-run \
    --name "sales-data-pipeline" \
    --run-id "wr_abc123"

# Get workflow runs
aws glue get-workflow-runs \
    --name "sales-data-pipeline" \
    --max-results 50

# Delete workflow
aws glue delete-workflow --name "old-workflow"
```

### Advanced Operations

#### Batch Operations Script

```bash
#!/bin/bash
# Batch create multiple tables

DATABASE="sales_database"
TABLES=("orders" "customers" "products" "transactions")

for table in "${TABLES[@]}"; do
    echo "Creating table: $table"
    aws glue create-table \
        --database-name "$DATABASE" \
        --table-input file://"table-definitions/${table}.json"
done

# Start multiple crawlers
CRAWLERS=("s3-orders-crawler" "s3-customers-crawler" "s3-products-crawler")

for crawler in "${CRAWLERS[@]}"; do
    echo "Starting crawler: $crawler"
    aws glue start-crawler --name "$crawler"
done

# Wait for crawlers to complete
for crawler in "${CRAWLERS[@]}"; do
    while true; do
        STATE=$(aws glue get-crawler --name "$crawler" --query 'Crawler.State' --output text)
        if [ "$STATE" = "READY" ]; then
            echo "Crawler $crawler completed"
            break
        fi
        echo "Crawler $crawler is $STATE, waiting..."
        sleep 30
    done
done
```

#### Monitoring and Logging

```bash
# Get job run metrics
aws glue get-job-run \
    --job-name "sales-etl-job" \
    --run-id "jr_abc123" \
    --query 'JobRun.{Status:JobRunState,Duration:ExecutionTime,DPUs:MaxCapacity}'

# Get crawler metrics for all crawlers
aws glue get-crawler-metrics \
    --query 'CrawlerMetricsList[*].{Name:CrawlerName,TablesCreated:TablesCreated,TablesUpdated:TablesUpdated}'

# Enable CloudWatch logging for job
aws glue update-job \
    --job-name "sales-etl-job" \
    --job-update '{
        "DefaultArguments": {
            "--enable-continuous-cloudwatch-log": "true",
            "--enable-metrics": "true",
            "--enable-spark-ui": "true"
        }
    }'
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
