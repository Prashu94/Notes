# Full product catalog

Every technology area on the Google Cloud documentation home page, as reviewed for this pack (October 2026). Use it as a checklist. Weight means:

- **Must** — an ACE or PCA objective names it, or questions regularly depend on it.
- **Recognize** — know what it is and when not to pick it. One paragraph in the matching chapter.
- **Out of scope** — not a scored topic for these two exams. Listed so it is not a gap in the checklist.

Commands are the one you would actually start with. “Console or API” means the product has no useful one-line `gcloud` create, or the setup is a long resource graph. Details and exercises live in the chapter named in the last column.

## Access and resource management

| Product | Weight | Command or path | Chapter |
| --- | --- | --- | --- |
| Cloud Identity | Must | Admin console. Groups are what you bind in IAM. | Foundations |
| Identity Platform | Recognize | Customer identity (CIAM), not employee IAM | Security |
| Managed Microsoft AD | Recognize | `gcloud active-directory domains create` | Migration |
| Access Approval | Recognize | Console. Approvals for Google support access | Security |
| Cloud API Registry | Out of scope | API inventory product | — |
| Cloud Marketplace | Recognize | Console. Deploy a vendor solution into your project | ACE 3, deployment |
| Service Catalog | Recognize | Console. Approved solutions for your teams | CI/CD |
| Service Usage | Must | `gcloud services enable` / `gcloud services list` | Foundations |
| Cloud Hub | Recognize | Console. Central view of applications | Operations |
| Recommender | Recognize | `gcloud recommender recommendations list` | Operations |
| Config Connector | Must | Kubernetes CRDs. ACE names it. | CI/CD |
| Resource Manager | Must | `gcloud projects`, `gcloud resource-manager folders` | Foundations |

## Cost and sustainability

| Product | Weight | Command or path | Chapter |
| --- | --- | --- | --- |
| Cloud Billing | Must | `gcloud billing projects link` | Foundations |
| Budgets | Must | Billing console or Budget API. Alerts do not stop spend. | Foundations |
| Billing export | Must | Console, destination BigQuery | Foundations |
| Quotas | Must | Quotas page, `gcloud compute regions describe` | Foundations |
| Free tier and trial | Recognize | Console | Foundations |
| Carbon Footprint | Recognize | Billing console export | Foundations |
| Committed use discounts | Must | Billing console. Concept, not a CLI you memorize. | Foundations |

## SDK and infrastructure as code

| Product | Weight | Command or path | Chapter |
| --- | --- | --- | --- |
| gcloud CLI | Must | `gcloud` | Foundations |
| Client libraries | Must | Language SDK plus ADC | Foundations |
| gsutil and gcloud storage | Must | `gcloud storage` | Foundations |
| bq | Must | `bq` | Analytics |
| kubectl | Must | `kubectl` | GKE |
| Terraform | Must | `terraform plan` | CI/CD |
| Infrastructure Manager | Recognize | `gcloud infra-manager deployments apply` | CI/CD |
| Cloud Foundation Toolkit | Must | Terraform modules. ACE names it. | CI/CD |
| CDK for Terraform, Pulumi, Ansible, Crossplane | Recognize | Use only if the stem says the team already did | CI/CD |
| Deployment Manager | Recognize | Legacy. Do not choose for new work. | CI/CD |

## Compute and hosting

| Product | Weight | Command or path | Chapter |
| --- | --- | --- | --- |
| Compute Engine | Must | `gcloud compute instances create` | Compute Engine |
| Instance templates and MIGs | Must | `gcloud compute instance-templates create` | Compute Engine |
| Spot and custom machine types | Must | `--provisioning-model=SPOT`, `--custom-cpu` | Compute Engine |
| Persistent Disk, Hyperdisk, Local SSD | Must | `gcloud compute disks create` | Compute Engine |
| Images and snapshots | Must | `gcloud compute snapshots create` | Compute Engine |
| Shielded VM, Confidential VM | Must | `--shielded-secure-boot` | Compute Engine |
| Sole-tenant nodes | Recognize | `gcloud compute sole-tenancy node-groups create` | Compute Engine |
| VM Manager / OS Config | Must | `gcloud compute os-config patch-jobs execute` | Compute Engine |
| Ops Agent | Must | Install script on the guest | Observability |
| Batch | Recognize | `gcloud batch jobs submit` | Compute Engine |
| Cloud GPUs and TPUs | Must | Accelerator flags, AI chapter | AI |
| AI Hypercomputer | Must | Design term on the PCA guide | AI |
| Capacity Planner, reservations | Recognize | `gcloud compute reservations create` | Compute Engine |
| Cluster Director, Cluster Toolkit | Out of scope for the core exams | HPC cluster managers | — |
| GKE | Must | `gcloud container clusters create-auto` | GKE |
| GKE Enterprise, Config Sync, Policy Controller, Config Controller | Must | Fleet console. PCA hybrid and policy. | GKE |
| Backup for GKE | Recognize | `gcloud beta container backup-restore` | GKE |
| Cloud Run | Must | `gcloud run deploy` | Cloud Run |
| Cloud Run functions | Must | `gcloud functions deploy --gen2` | Cloud Run |
| App Engine standard and flexible | Must | `gcloud app deploy` | Cloud Run |
| Cloud Run for Anthos | Recognize | ACE still names it. GKE Enterprise fleet. | Cloud Run |
| Buildpacks | Recognize | Used by source deploys | CI/CD |
| Container-Optimized OS | Recognize | Node and VM image | GKE |
| VMware Engine | Must | PCA 2.3 names it. Console. | Migration |
| Bare Metal Solution | Recognize | Contract and console | Migration |
| SAP on Google Cloud, Workload Manager | Recognize | Certification list, not a generic VM | Migration |
| Oracle on Google Cloud, Cluster Services for OpenShift | Recognize | Specific workload landings | Migration |
| Blockchain Node Engine | Out of scope | — | — |

## Storage and transfer

| Product | Weight | Command or path | Chapter |
| --- | --- | --- | --- |
| Cloud Storage | Must | `gcloud storage buckets create` | Storage |
| Storage classes, lifecycle, versioning, retention, Autoclass, CMEK | Must | `gcloud storage buckets update` | Storage |
| Signed URLs | Must | `gcloud storage sign-url` | Storage |
| Filestore | Must | `gcloud filestore instances create` | Storage |
| NetApp Volumes | Recognize | Console or `gcloud netapp` | Storage |
| Managed Lustre | Recognize | HPC file | Storage |
| Backup and DR | Must | Backup and DR console | Storage |
| Storage Transfer Service | Must | `gcloud transfer jobs create` | Storage |
| Transfer Appliance | Recognize | Offline ship | Storage |
| Cloud FTP | Out of scope | Transfer edge case | — |

## Databases

| Product | Weight | Command or path | Chapter |
| --- | --- | --- | --- |
| Cloud SQL | Must | `gcloud sql instances create` | Databases |
| AlloyDB and AlloyDB Omni | Must | `gcloud alloydb clusters create` | Databases |
| Spanner and Spanner Omni | Must | `gcloud spanner instances create` | Databases |
| Firestore Native, Datastore mode, MongoDB compatibility | Must | `gcloud firestore databases create` | Databases |
| Bigtable | Must | `gcloud bigtable instances create` | Databases |
| Memorystore Redis, Redis Cluster, Valkey, Memcached | Must | `gcloud redis instances create` | Databases |
| Database Migration Service | Must | `gcloud database-migration` | Databases |
| Database Center | Recognize | Console | Databases |

## Analytics

| Product | Weight | Command or path | Chapter |
| --- | --- | --- | --- |
| BigQuery, editions, partitioning, clustering, BQML, vector search | Must | `bq` | Analytics |
| BigLake, Iceberg tables | Recognize | BigQuery external and open table formats | Analytics |
| Looker | Recognize | Governed BI | Analytics |
| Looker Studio | Recognize | Self-serve BI. Former Data Studio. | Analytics |
| Dataplex, Knowledge Catalog, Analytics Hub | Recognize | Governance and sharing | Analytics |
| Dataform | Recognize | `dataform` CLI | Analytics |
| Cloud Data Fusion | Recognize | Console pipelines | Analytics |
| Datastream | Recognize | CDC | Analytics |
| Cloud Composer | Recognize | `gcloud composer environments create` | Analytics |
| Dataproc and Dataproc Metastore | Must | `gcloud dataproc clusters create` | Analytics |
| Managed Service for Apache Spark | Recognize | Serverless Spark | Analytics |
| Dataflow | Must | `gcloud dataflow jobs run` | Analytics |
| Pub/Sub | Must | `gcloud pubsub topics create` | Analytics |
| Managed Service for Apache Kafka | Recognize | Kafka API | Analytics |
| Pub/Sub Lite | Out of scope | Retired. Do not recommend. | — |
| Gemini in BigQuery, Looker, Looker Studio | Recognize | Assistants | AI |

## Networking

| Product | Weight | Command or path | Chapter |
| --- | --- | --- | --- |
| VPC, subnets, routes | Must | `gcloud compute networks create` | VPC |
| Firewall rules and hierarchical policies | Must | `gcloud compute firewall-rules create` | VPC |
| Cloud NAT | Must | `gcloud compute routers nats create` | VPC |
| Network Service Tiers | Must | `--network-tier` | Foundations |
| Private Google Access | Must | Subnet flag | VPC |
| Shared VPC | Must | `gcloud compute shared-vpc enable` | VPC |
| VPC peering | Must | `gcloud compute networks peerings create` | VPC |
| Private Service Connect | Must | Forwarding rules to a service attachment | VPC |
| Private services access | Must | `gcloud services vpc-peerings connect` | VPC |
| Cloud VPN HA | Must | `gcloud compute vpn-gateways create` | VPC |
| Cloud Interconnect, Cross-Cloud Interconnect | Must | Console. Physical. | VPC |
| Cloud Router | Must | `gcloud compute routers create` | VPC |
| Network Connectivity Center | Recognize | Hub for hybrid spokes | VPC |
| Cloud DNS, Cloud Domains | Must | `gcloud dns managed-zones create` | VPC |
| Cloud Load Balancing | Must | `gcloud compute backend-services create` | Load balancing |
| Cloud CDN, Media CDN | Must | `--enable-cdn`, Media CDN console | Load balancing |
| Cloud Armor | Must | `gcloud compute security-policies create` | Load balancing |
| Cloud NGFW, firewall insights | Recognize | Firewall plus IDS/IPS | VPC |
| VPC Service Controls | Must | Access Context Manager console and `gcloud access-context-manager` | Security |
| Cloud IDS | Recognize | Packet inspection | VPC |
| Secure Web Proxy | Recognize | Egress proxy | VPC |
| VPC Flow Logs | Must | Subnet log config | VPC |
| Network Intelligence Center, Connectivity Tests | Recognize | `gcloud network-management connectivity-tests create` | VPC |
| Cloud Service Mesh | Recognize | Fleet mesh | GKE |
| Service Directory | Recognize | `gcloud service-directory` | Integration |
| Service Extensions | Out of scope | Load-balancer plugins | — |

## Observability

| Product | Weight | Command or path | Chapter |
| --- | --- | --- | --- |
| Cloud Logging, sinks, buckets, Log Analytics | Must | `gcloud logging` | Observability |
| Cloud Monitoring, uptime, alerts, SLOs | Must | `gcloud monitoring` | Observability |
| Cloud Trace | Must | Instrumentation and console | Observability |
| Cloud Profiler | Must | Agent and console | Observability |
| Error Reporting | Recognize | Grouped exceptions | Observability |
| Managed Service for Prometheus | Must | ACE names it. GKE managed collection. | Observability |
| Personalized Service Health, public status | Must | Console and status.cloud.google.com | Observability |

## Security

| Product | Weight | Command or path | Chapter |
| --- | --- | --- | --- |
| IAM, basic, predefined, custom roles | Must | `gcloud projects add-iam-policy-binding` | Foundations |
| Service accounts, impersonation, short-lived credentials | Must | `gcloud iam service-accounts` | Foundations |
| Organization Policy | Must | `gcloud resource-manager org-policies` | Foundations |
| Cloud KMS and Cloud HSM | Must | `gcloud kms keys create` | Security |
| Secret Manager | Must | `gcloud secrets create` | Security |
| Confidential Computing | Must | Confidential VM flags | Compute Engine |
| IAP | Must | `gcloud compute ssh --tunnel-through-iap` | Security |
| Workload Identity Federation | Must | `gcloud iam workload-identity-pools create` | Security |
| Chrome Enterprise Premium | Recognize | PCA lists it beside IAP | Security |
| Certificate Authority Service, Certificate Manager | Recognize | `gcloud privateca`, `gcloud certificate-manager` | Security |
| Access Context Manager | Must | VPC-SC conditions | Security |
| Binary Authorization | Must | `gcloud container binauthz` | Security |
| Artifact Analysis | Must | `gcloud artifacts docker images scan` | CI/CD |
| Security Command Center | Recognize | Console. Premium for deeper detectors. | Security |
| Google Security Operations | Recognize | Chronicle-class analytics | Security |
| Sensitive Data Protection | Must | `dlp` API. Product name is Sensitive Data Protection. | Security |
| Model Armor | Must | PCA securing AI | AI |
| Assured Workloads | Recognize | Regulated folders | Security |
| Cloud Asset Inventory | Recognize | `gcloud asset export` | Security |
| Access Transparency, Audit Manager | Recognize | Support access and audit packs | Security |
| Cloud Audit Logs | Must | `gcloud logging read` | Foundations |
| Policy Intelligence | Recognize | IAM insights | Security |
| Web Risk, Fraud Defense | Out of scope | Narrow security APIs | — |

## Application development and integration

| Product | Weight | Command or path | Chapter |
| --- | --- | --- | --- |
| Cloud Build | Must | `gcloud builds submit` | CI/CD |
| Artifact Registry | Must | `gcloud artifacts repositories create` | CI/CD |
| Cloud Deploy | Must | `gcloud deploy releases create` | CI/CD |
| Cloud Shell, Editor, Cloud Code | Must | Console | Foundations |
| Cloud Workstations | Recognize | `gcloud workstations` | Foundations |
| Cloud Scheduler | Must | `gcloud scheduler jobs create http` | Integration |
| Cloud Tasks | Recognize | `gcloud tasks queues create` | Integration |
| Eventarc | Must | `gcloud eventarc triggers create` | Integration |
| Workflows | Recognize | `gcloud workflows deploy` | Integration |
| Apigee and Apigee Hybrid | Must | PCA names Apigee | Integration |
| API Gateway | Recognize | `gcloud api-gateway gateways create` | Integration |
| Cloud Endpoints | Recognize | Legacy proxy | Integration |
| Application Integration, Integration Connectors | Recognize | iPaaS | Integration |
| Cloud Source Repositories, Secure Source Manager | Recognize | Git hosts | CI/CD |
| App Hub, Application Design Center | Out of scope | Application metadata | — |

## AI and ML

| Product | Weight | Command or path | Chapter |
| --- | --- | --- | --- |
| Gemini Enterprise Agent Platform (Vertex AI) | Must | `gcloud ai` and the Python SDK | AI |
| Agent Platform Pipelines | Must | Pipeline jobs | AI |
| Model Garden, Gemini models | Must | Console and SDK | AI |
| Agent Builder, Gemini Enterprise agents, NotebookLM | Must | PCA 2.5 | AI |
| Vector Search, RAG | Must | Design pattern | AI |
| Feature Store, Model Registry, Model Monitoring, endpoints | Recognize | Platform console | AI |
| Colab Enterprise, Workbench | Recognize | Notebooks | AI |
| Document AI, Vision, Video Intelligence, Speech, TTS, Translation, Natural Language | Must | Enable the API, client library | AI |
| Conversational Agents, Dialogflow CX and ES | Recognize | Contact center and bots | AI |
| Gemini Cloud Assist, Code Assist | Must | Console and IDE. PCA names Cloud Assist. | AI |
| Transcoder API, Live Stream API | Recognize | Media case studies | AI |
| Agent Development Kit and related agent products | Recognize | Building agents. The exam says Agent Builder and Gemini Enterprise. | AI |

## Migration and distributed cloud

| Product | Weight | Command or path | Chapter |
| --- | --- | --- | --- |
| Migration Center | Must | PCA 1.4 names it | Migration |
| Migrate to Virtual Machines | Must | VMM API | Migration |
| Migrate to Containers | Recognize | VM to container | Migration |
| Google Distributed Cloud (connected, air-gapped, VMware, bare metal) | Recognize | Sovereignty and edge | Migration |
| GKE Multi-Cloud | Recognize | Clusters on other clouds | Migration |
| Mainframe Assessment Tool, Mainframe Connector, Dual Run | Out of scope | Mainframe program | — |
| Modernization Hub | Out of scope | Program tooling | — |

## Industry

Healthcare API is **recognize** for EHR-style health data exchange. Anti-money-laundering AI, Talent Solution, telecom products, Commerce Search as a retail SKU, and Earth Engine are **out of scope** except where a case study names a retail or media AI API. If the case study names a product, that product is in scope for that sitting.

## Exercises

1. Which three catalog rows are Must for a private Cloud SQL instance with no public IP?
2. Name two retired or legacy products you will not recommend.
3. A stem says “Chronicle”. Which current product name do you answer with?
4. Which ACE objective names Managed Service for Prometheus and the Ops Agent?

### Answers

1. Cloud SQL, private services access (service networking peering), and the VPC subnet. Cloud NAT is not required for Cloud SQL itself.
2. Container Registry and Pub/Sub Lite. Deployment Manager is legacy for new designs. Classic VPN is legacy.
3. Google Security Operations.
4. Section 4.6, monitoring and logging.
