# Google Cloud Certification Study Roadmap

This repository contains a comprehensive set of study guides for the **Associate Cloud Engineer (ACE)** and **Professional Cloud Architect (PCA)** certifications.

## 📚 Study Path

### Phase 1: Core Infrastructure (ACE Focus)
Start here to build the foundation.
1.  **IAM & Security**:
    *   [ACE Guide](gcp-iam-ace-guide.md): Users, Roles, Service Accounts.
    *   [Security Operations](gcp-security-ace-guide.md): Key Management, IAP.
2.  **Networking**:
    *   [VPC Fundamentals](gcp-networking-ace-guide.md): VPCs, Subnets, Firewalls.
    *   [Load Balancing](gcp-load-balancing-ace-guide.md): HTTP(S), TCP/UDP LBs.
3.  **Compute**:
    *   [Compute Engine & GKE](gcp-compute-ace-guide.md): VMs, Clusters, Pods.
    *   [Serverless](gcp-serverless-ace-guide.md): Cloud Run, Functions, App Engine.
4.  **Storage & Data**:
    *   [Storage](gcp-storage-ace-guide.md): GCS, Cloud SQL.
    *   [Big Data](gcp-data-ace-guide.md): BigQuery, Pub/Sub.
5.  **Operations**:
    *   [Ops Guide](gcp-operations-ace-guide.md): Monitoring, Logging.

### Phase 2: Advanced Architecture (PCA Focus)
Move to design patterns, decision trees, and complex scenarios.
1.  **Advanced Design**:
    *   [Compute Architecture](gcp-compute-pca-guide.md): High Availability, Migration, Fleets.
    *   [Serverless Architecture](gcp-serverless-pca-guide.md): Event-driven patterns.
2.  **Advanced Networking**:
    *   [Networking Architecture](gcp-networking-pca-guide.md): Shared VPC, Hybrid Connectivity.
    *   [Load Balancing Design](gcp-load-balancing-pca-guide.md): Global vs Regional, mTLS.
3.  **Security Architecture**:
    *   [Security Design](gcp-security-pca-guide.md): Compliance, DLP, WIF.
    *   [IAM Design](gcp-iam-pca-guide.md): Org Policies, Hierarchy.
4.  **Data Architecture**:
    *   [Data & AI Design](gcp-data-pca-guide.md): Pipelines, MLOps, Storage Selection.
    *   [Storage Architecture](gcp-storage-pca-guide.md): Database Decision Tree.
5.  **SRE & Operations**:
    *   [SRE Guide](gcp-operations-pca-guide.md): SLO/SLA, Cost Management.

## 🎯 Key Decision Trees (PCA)
*   **Compute**: Cloud Run vs GKE vs GCE vs App Engine.
*   **Storage**: SQL vs NoSQL (Bigtable/Firestore) vs Object.
*   **Load Balancing**: Global vs Regional, External vs Internal.
*   **Data**: ETL vs ELT, Batch vs Streaming.

## 🛠 CLI Cheatsheet
Each ACE guide contains relevant `gcloud` commands. Practice them in the Cloud Shell!
