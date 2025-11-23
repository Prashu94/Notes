# Google Cloud Professional Cloud Architect (PCA) - Data & AI Architecture Guide

## 1. Data Pipeline Architecture

### 1.1 Processing Patterns
*   **ETL (Extract, Transform, Load)**:
    *   Data is transformed *before* loading into the warehouse.
    *   **Tool**: Dataflow.
    *   **Use Case**: Cleaning PII, complex aggregations, format conversion.
*   **ELT (Extract, Load, Transform)**:
    *   Raw data is loaded immediately, then transformed using SQL.
    *   **Tool**: BigQuery (Scheduled Queries, DBT).
    *   **Use Case**: Fast ingestion, analysts prefer SQL over Java/Python.

### 1.2 Streaming Architecture (Kappa)
*   **Ingest**: Pub/Sub (Global, durable buffer).
*   **Process**: Dataflow (Windowing, Watermarks, Late data handling).
*   **Store**: BigQuery (Analytics) or Bigtable (High-throughput writes).
*   **Visualize**: Looker Studio.

## 2. BigQuery Optimization & Architecture

### 2.1 Partitioning
Divides a table into segments to reduce the amount of data scanned (Cost & Performance).
*   **Time-Unit Partitioning**: By Day/Hour/Month (e.g., `transaction_date`).
*   **Ingestion Time Partitioning**: By when the data arrived (`_PARTITIONDATE`).
*   **Integer Range Partitioning**: By a number ID (e.g., `customer_id`).
*   **Best Practice**: Always partition large tables by date.

### 2.2 Clustering
Sorts data within a partition based on one or more columns.
*   **Use Case**: High cardinality filters (e.g., `WHERE user_id = '123'`).
*   **Benefit**: Eliminates scanning unrelated blocks (Block Pruning).
*   **Order Matters**: Cluster by most frequently filtered columns first.

### 2.3 Materialized Views
Pre-computed views that periodically cache results of a query.
*   **Smart Tuning**: BigQuery automatically uses the MV if it can satisfy a query (Query Rewrite).
*   **Real-time**: Can combine cached data with the latest streaming buffer data.

## 3. Vertex AI & MLOps

### 3.1 Model Training Options
| Feature | **AutoML** | **Custom Training** |
| :--- | :--- | :--- |
| **Skill Level** | No code / Low code. | Data Scientists / ML Engineers. |
| **Flexibility** | Limited to standard tasks (Vision, NLP). | Unlimited (TensorFlow, PyTorch, Scikit-learn). |
| **Speed** | Slower to train (searches architectures). | Faster (if you know the architecture). |
| **Use Case** | "I need a good model fast." | "I need state-of-the-art performance." |

### 3.2 MLOps Components
*   **Vertex AI Pipelines**: Orchestrate the ML workflow (Data prep -> Train -> Eval -> Deploy). Based on Kubeflow.
*   **Feature Store**: Centralized repository for serving features to models (Training & Serving consistency).
*   **Model Registry**: Version control for models.

## 4. Data Storage Decision Matrix

| Requirement | Recommended Service |
| :--- | :--- |
| **SQL + Analytics (OLAP) + Petabytes** | **BigQuery** |
| **SQL + Transactional (OLTP) + Global Scale** | **Spanner** |
| **SQL + Transactional (OLTP) + Regional** | **Cloud SQL** |
| **NoSQL + High Throughput (IoT/AdTech) + <10ms** | **Bigtable** |
| **NoSQL + Mobile/Web App + Real-time Sync** | **Firestore** |
| **In-Memory + Sub-millisecond (Cache)** | **Memorystore** |

## 5. Data Governance
*   **Data Catalog**: Discovery and metadata management.
*   **DLP (Data Loss Prevention)**: Scan and redact sensitive data (PII, Credit Cards) before it enters BigQuery.
*   **IAM**:
    *   **BigQuery**: Dataset-level, Table-level, and Row-level security.
    *   **Authorized Views**: Allow users to query a view without giving access to the underlying table.
