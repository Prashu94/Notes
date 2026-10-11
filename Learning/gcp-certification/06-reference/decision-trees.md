# Decision trees

Read the constraint. Walk top to bottom. Stop at the first row that matches.

## Compute

| If the stem says | Choose |
| --- | --- |
| vSphere / vCenter must stay | Google Cloud VMware Engine |
| Certified bare metal, Oracle or similar | Bare Metal Solution, after you check the current program |
| Guest OS, kernel, or a non-container installer | Compute Engine |
| Batch or HPC jobs, no cluster to operate | Batch |
| Kubernetes API, StatefulSet, mesh, or fleet policy | GKE |
| GKE and they do not want to patch nodes | Autopilot |
| GKE and they need DaemonSets, SSH, or special nodes | Standard |
| Container HTTP or a batch container, no Kubernetes | Cloud Run service or Cloud Run job |
| One function, one event | Cloud Run functions |
| Existing `app.yaml` and App Engine versions | App Engine, then plan a move |

## Database and storage

| If the stem says | Choose |
| --- | --- |
| Bytes, files, lake, backup dumps, static web | Cloud Storage |
| `open()` on a shared path, NFS | Filestore |
| SMB or NetApp features | NetApp Volumes |
| MySQL, SQL Server, or modest Postgres, one region | Cloud SQL |
| Postgres, heavy performance, HTAP, or vectors | AlloyDB |
| Relational, multi-region strong writes | Spanner |
| Documents, mobile sync | Firestore Native |
| Old Datastore client | Firestore in Datastore mode |
| Huge writes, one key, time series, IoT | Bigtable |
| Cache or session you can rebuild | Memorystore |
| SQL analytics | BigQuery |
| Disk on a VM | Persistent Disk or Hyperdisk. Local SSD only for scratch |

## Availability

| Printed target or failure | Minimum shape |
| --- | --- |
| One zone is acceptable (lab, batch) | Zonal VM or zonal Cloud SQL |
| Zone loss, about 99.9%, one region | Regional MIG, regional GKE, Cloud Run, Cloud SQL HA, or regional Spanner |
| Region loss, or active writes on two continents | Multi-region Spanner or a designed active-passive with a written RPO |
| 99.99% hybrid over the internet | HA VPN, two tunnels, Cloud Router, not one tunnel |

## Network path

| If the stem says | Choose |
| --- | --- |
| Internet HTTPS, WAF, CDN, serverless | Global external Application Load Balancer |
| UDP or original client IP | Passthrough Network Load Balancer |
| Only inside the VPC | Internal load balancer or private IP. No public Armor story. |
| Many teams, one network team | Shared VPC |
| One API, two companies, no full routing | Private Service Connect |
| Full private routing between two VPCs | Peering. Remember it is not transitive. |
| Site-to-site over the internet | HA VPN |
| Large steady bandwidth, a real circuit | Dedicated or Partner Interconnect |
| Many sites that must talk | Network Connectivity Center |

## Security add-on

Add a row only when the stem asks for the problem it solves.

| Problem | Add |
| --- | --- |
| Customer must control key destruction | CMEK |
| Password or token | Secret Manager |
| No public SSH | IAP and OS Login |
| No keys in GitHub | Workload Identity Federation |
| Data must not be copied to a personal project | VPC Service Controls |
| Project admins must not open a firewall you deny | Hierarchical firewall policy |
| Unsigned images must not deploy | Binary Authorization |
| PII in text or images | Sensitive Data Protection |
| User prompts to a model | Model Armor |
| Regulated folder and residency | Assured Workloads and resource-location policy |

## Pipeline

| If the stem says | Choose |
| --- | --- |
| Fan-out messages | Pub/Sub, one topic, many subscriptions |
| Beam, batch or stream, windows | Dataflow |
| Existing Spark | Dataproc or serverless Spark |
| Airflow | Cloud Composer |
| A few API steps and retries | Workflows |
| Cron | Cloud Scheduler |
| One HTTP retry queue | Cloud Tasks |
| GUI ETL | Cloud Data Fusion |
| SQL models in git | Dataform |
| CDC into analytics | Datastream |
| Move the database | Database Migration Service |
| Move files from S3 or a bucket | Storage Transfer Service |
