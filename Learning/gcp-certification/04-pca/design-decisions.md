# Design method for architect questions

Use the same order every time. The practice exam and the case studies assume it.

## 1. Write the constraint, not the product

From the stem, extract:

- Users and where they are
- Availability target and whether a whole region failing is in scope
- RPO and RTO if stated
- Data model and consistency
- Compliance and residency
- Team skills and rewrite budget
- Cost pressure and what is idle
- What must stay where it is (legacy interfaces)

If a fact is missing, do not invent a stricter one.

## 2. Reject answers that break a constraint

Throw out any option that:

- Uses a public IP for a database the stem said is private
- Puts the only copy of data on Spot or Local SSD
- Requires a rewrite the stem forbade
- Adds a region the availability target did not ask for
- Uses a basic IAM role
- Uses a retired product (Container Registry, Pub/Sub Lite, classic VPN)
- Logs secrets or card numbers
- Shares one VPC peering transitively (it cannot)

## 3. Pick compute, data, and network with the trees

Compute, in order:

1. VMware must remain → VMware Engine
2. Guest OS or commercial installer → Compute Engine
3. Kubernetes API, StatefulSet, or fleet policy → GKE (Autopilot unless they need nodes)
4. Container, HTTP or job, scale down → Cloud Run
5. One event, one small handler → Cloud Run functions

Data:

1. Object → Cloud Storage
2. Shared filesystem → Filestore or NetApp
3. SQL Server, MySQL, or modest Postgres → Cloud SQL
4. Demanding Postgres or HTAP or vectors in Postgres → AlloyDB
5. Global relational writes → Spanner
6. Documents → Firestore
7. Huge key-value or time series → Bigtable
8. Cache → Memorystore
9. Analytics → BigQuery

Network:

1. Internal only → private IP, no external load balancer
2. Internet HTTP plus WAF or CDN → global external Application Load Balancer
3. UDP or preserve source IP → passthrough Network Load Balancer
4. Many teams, one firewall team → Shared VPC
5. One service, two companies → Private Service Connect
6. Data center, over the internet, 99.99% → HA VPN and Cloud Router
7. Data center, large steady bandwidth → Interconnect
8. Transitive sites → Network Connectivity Center, not a peering mesh

## 4. Add only the security the stem bought

Default private. Add CMEK, VPC-SC, IAP, Binary Authorization, Model Armor, or Assured Workloads only when the stem has a reason. Adding all of them to a marketing site is how you lose the cost and the simplicity comparison.

## 5. Say how it is operated

One sentence: Terraform, Cloud Build, Cloud Deploy, an SLO, logs to BigQuery if they must be retained. Section 6 items are often the tie-break.

## 6. Say what you did not build

“We did not use Spanner because the target is 99.9% in one region and the engine is SQL Server.” That sentence is the whole exam.

## Worked example

Stem: a document-upload API for staff in one country. 99.5% is enough. Files are large. A separate system must virus-scan each file. The team knows containers, not Kubernetes. Auditors want a year of admin audit logs.

Design:

- Cloud Run in one region, private, fronted by an internal or external Application Load Balancer only if staff are outside the VPC. If they are on the corporate network, IAP or an internal load balancer.
- Files in Cloud Storage, Standard, lifecycle later if auditors allow. CMEK only if they asked for customer-managed keys. The stem did not.
- Scan: Eventarc on object finalize to a Cloud Run service that scans and moves the object to a clean bucket. Pub/Sub if several consumers appear later.
- Audit: Admin Activity sink to BigQuery or a locked bucket, retention one year. It is already collected.
- Ops: Cloud Deploy, min instances 0, alert on 5xx.
- Not chosen: GKE, multi-region, Spanner, a VM per upload.

## Exercise

Do the same six steps for this stem before you look.

A game company stores player profiles that change constantly, keyed by player id, at very high write rates in one region. A nightly job aggregates play into a warehouse for analysts. The API is already a container. They want Kubernetes because platform engineering standardized on it. Analysts must not query the live store.

### A solid answer

- GKE Autopilot, regional, because they standardized on Kubernetes. Cloud Run would have been enough for a stateless API, and you can say that, but the skill constraint wins.
- Bigtable for profiles, row key prefixed by player id. Not Cloud SQL.
- Nightly Dataflow or a Dataproc job, or a BigQuery load from an export, into BigQuery. Analysts get BigQuery IAM only. They do not get Bigtable roles.
- VPC-native private cluster, Workload Identity.
- Not Spanner: this is not a relational global ledger. Not Firestore: the write rate and key model fit wide-column better when the stem says very high write rates and a single key.
