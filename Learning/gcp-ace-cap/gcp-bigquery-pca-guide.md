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

## 2. Capacity Planning & Pricing Models

### Pricing Models
1.  **On-Demand (Default):**
    - Pay per TB of data processed.
    - Shared pool of slots (up to 2000 concurrent slots per project by default).
    - Best for unpredictable workloads.

2.  **Capacity-Based (Editions):**
    - Pay for slot capacity (measured in slots/hour).
    - **Standard:** Basic SQL, standard concurrency.
    - **Enterprise:** Advanced features, higher concurrency, autoscaling.
    - **Enterprise Plus:** Mission-critical, highest concurrency, disaster recovery.
    - **Autoscaling:** Automatically adds slots to handle load spikes.

### Reservations
- Isolate capacity for specific workloads or departments.
- **Baseline:** Guaranteed slots.
- **Autoscaling:** Additional slots added as needed.
- **Idle Slot Sharing:** Unused slots from one reservation can be used by others.

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
