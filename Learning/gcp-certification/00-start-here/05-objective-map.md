# Objective map

Every bullet from the October 2026 exam guides, and where this pack teaches it. If you can do the right-hand column, you have covered the bullet.

## Associate Cloud Engineer

| Bullet | Where |
| --- | --- |
| 1.1 Resource hierarchy | `01-foundations/01-resource-hierarchy-iam-billing.md` |
| 1.1 Organization policies | Foundations and `02-services/10-iam-security-compliance.md` |
| 1.1 IAM roles in a project | Foundations |
| 1.1 Cloud Identity users and groups | Foundations |
| 1.1 Enable APIs | Foundations, `02-gcloud` |
| 1.1 Operations suite | `02-services/11-observability-and-operations.md` |
| 1.1 Quotas | `01-foundations/03-regions-zones-quotas-pricing.md` |
| 1.2 Billing accounts, link, budgets, export | Foundations |
| 2.1 Compute choice, Spot, custom machines | `01-compute-engine.md`, `02-gke.md`, `03-cloud-run-and-app-engine.md`, decision trees |
| 2.2 Database and disk and storage class choice | `07-cloud-storage-and-file.md`, `08-databases.md` |
| 2.3 Load balancing, locations, network tiers | `06-load-balancing-cdn-armor.md`, foundations |
| 3.1 Instances, MIG, OS Login, VM Manager | `01-compute-engine.md` |
| 3.2 kubectl, Autopilot, regional, private, GKE Enterprise, deploy | `02-gke.md` |
| 3.3 Cloud Run, functions, events, Anthos choice | `03-cloud-run-and-app-engine.md`, `15-integration` |
| 3.4 Data products including AlloyDB, load, Storage Transfer | `08-databases.md`, `07-storage`, `09-analytics` |
| 3.5 VPC, Shared VPC, firewalls, VPN, peering | `05-vpc-and-hybrid-networking.md` |
| 3.6 Foundation Toolkit, Config Connector, Terraform, Helm | `12-cicd-iac-and-deployment.md` |
| 4.1 SSH, inventory, snapshots, images | `01-compute-engine.md` |
| 4.2 Inventory, Artifact Registry, node pools, Pods, Services, StatefulSets, HPA, VPA | `02-gke.md` |
| 4.3 Revisions, traffic, scaling | `03-cloud-run-and-app-engine.md` |
| 4.4 Objects, lifecycle, queries, cost, backup, job status | Storage, databases, analytics |
| 4.5 Subnet add and expand, static IP, DNS, NAT | `05-vpc` |
| 4.6 Alerts, custom metrics, sinks, buckets, logs, diagnostics, status, Ops Agent, Prometheus, audit logs | `11-observability` |
| 5.1 Policies, basic, predefined, custom roles | Foundations |
| 5.2 Service accounts, least privilege, attach, impersonation, short-lived credentials | Foundations |

## Professional Cloud Architect

| Bullet | Where |
| --- | --- |
| 1.1 Business requirements, KPIs, build/buy/modify/deprecate | `04-pca/design-decisions.md`, case studies |
| 1.2 Well-Architected, HA, scale, latency, Gemini Cloud Assist, backup | `04-pca/well-architected-framework.md`, `13-ai` |
| 1.3 Hybrid, AI, networking, data processing, storage, GKE, Cloud Run, functions, Spot | Service chapters and decision trees |
| 1.4 Migration Center, licenses, waves | `14-migration-hybrid-multicloud.md` |
| 1.5 Future improvements, cloud-first | Migration chapter |
| 2.1 Hybrid, multicloud, firewalls, VPC, load balancing | `05-vpc`, `06-load-balancing` |
| 2.2 Storage allocation, lifecycle, growth, backup | `07-storage`, `08-databases` |
| 2.3 Provisioning, Spot, VMware Engine, orchestration, serverless | Compute, GKE, Cloud Run, migration |
| 2.4 Agent Platform Pipelines, AI Hypercomputer, GPU, TPU | `13-ai-ml-and-gemini.md` |
| 2.5 Prebuilt APIs, Gemini Enterprise, NotebookLM, Model Garden | `13-ai` |
| 3.1 IAM, hierarchy, KMS, secrets, VPC-SC, IAP, WIF, Chrome Enterprise Premium, supply chain, Model Armor, Sensitive Data Protection | `10-iam-security-compliance.md` |
| 3.2 Legislation, PCI, PII, SOC 2, audits | Security chapter, case studies |
| 4.1 SDLC, CI/CD, RCA, testing, service catalog, DR | `12-cicd`, observability, storage backup |
| 4.2 Stakeholders, change, skills, CapEx/OpEx, continuity | `04-pca/design-decisions.md`, well-architected |
| 5.1 Deploy, Apigee, tests, migration tooling, Gemini Cloud Assist | `15-integration`, `12-cicd`, `14-migration`, AI |
| 5.2 Cloud Shell, Cloud Code, gcloud, gsutil, bq, emulators, Terraform, client libraries | `01-foundations/02-gcloud-and-cloud-shell.md` |
| 6.1 Operational excellence pillar | `04-pca/well-architected-framework.md` |
| 6.2 Monitoring, logging, profiling, alerting | `11-observability` |
| 6.3 Release management | `12-cicd` |
| 6.4 Support | Observability, well-architected |
| 6.5 Quality control | CI/CD testing section |
| 6.6 Chaos, penetration, load testing | CI/CD and well-architected |
| Case studies Altostrat, Cymbal, EHR, KnightMotives | `04-pca/case-studies.md` plus the official PDFs |

Products that appear on the documentation home page and are not in a bullet above are still listed, with weight, in `02-services/16-full-product-catalog.md`.

Mechanism that the short chapters only name is in:

| File | Fills |
| --- | --- |
| `17-compute-engine-deep-dive.md` | Lifecycle, disk types, snapshots versus images, MIG updates, scopes, reservations |
| `18-gke-deep-dive.md` | Private clusters, Workload Identity, upgrades, HPA/VPA, fleet policy |
| `19-serverless-deep-dive.md` | Cloud Run CPU, ingress, VPC, jobs, functions gen2, App Engine region lock |
| `20-networking-deep-dive.md` | Routes, firewall fields, HA VPN build, Shared VPC roles, PSC, DNS, LB objects |
| `21-data-deep-dive.md` | Storage class billing, Cloud SQL failover, Spanner keys, Firestore, Bigtable, BigQuery, Pub/Sub |
| `22-security-operations-deep-dive.md` | Conditions, deny, federation, VPC-SC, supply chain, alerting and SLOs |
| `23-ai-deep-dive.md` | Which AI API, RAG filters, endpoints, training versus calling a model |
| `24-cicd-deep-dive.md` | Cloud Build file, Cloud Deploy approval, Terraform state, scan versus block |
| `25-observability-deep-dive.md` | Log router, sinks, SLI/SLO/burn, what to page on |
| `26-cost-migration-deep-dive.md` | Budgets versus quotas versus CUDs, the migration plan headings |
