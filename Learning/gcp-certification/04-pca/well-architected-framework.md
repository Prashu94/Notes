# Google Cloud Well-Architected Framework

The Professional Cloud Architect exam requires this framework. The six pillars are woven through every section, and section 6.1 scores operational excellence by name. A product choice that meets the function and violates the pillar the stem is asking about is the wrong answer.

The official write-up lives in the Cloud Architecture Center. This chapter is the exam version: what each pillar demands, which Google Cloud control implements it, and the tradeoff that makes the other option wrong.

## Principles that sit above the pillars

1. **Document the design.** Write the requirement next to the product. An undocumented diagram cannot be operated or audited.
2. **Prefer managed services** when they meet the requirement. A self-managed database on a VM fails operational excellence unless the stem forbids the managed service.
3. **Decouple.** Pub/Sub, Eventarc, or Cloud Tasks so a slow consumer does not fail the producer.
4. **Keep serving tiers stateless.** A zone loss should be a scale event. State belongs in a managed store with a backup.
5. **Automate change.** Terraform, Cloud Build, Cloud Deploy. A production console click is toil.
6. **Design for the printed number.** Do not raise 99.9% to 99.999% because a product can. That spends the cost pillar to buy reliability nobody asked for.
7. **Measure, then change.** Carbon Footprint, billing export, Cloud Profiler, and an SLO. A resize without a metric is a guess.

## How a question uses a pillar

| Words in the stem | Pillar you are scoring |
| --- | --- |
| Manual deploys, missed alerts, no rollback, “operate this” | Operational excellence |
| Keys, tenants, public IP, audit, PHI, PCI, partners | Security |
| 99.9, failover, RPO, RTO, zone, region | Reliability |
| p95, slow query, latency budget, “users in this country” | Performance |
| Bill, idle, night, cheapest that still meets the SLO | Cost |
| Carbon, grid, utilization, “region is otherwise free” | Sustainability |

If two options both work, pick the one that serves the emphasized pillar and adds the least extra architecture.

## Pillar 1 — Operational excellence

Goal: run and change the system with little toil, and know when users are hurt.

### What to recommend

| Practice | Google Cloud control |
| --- | --- |
| Infrastructure defined in reviewable code | Terraform, remote state in a versioned bucket. Infrastructure Manager if they do not want a runner. |
| Application release with promotion | Cloud Deploy stages, or Cloud Run traffic split, or a MIG rolling update with max unavailable 0 |
| Build is not a laptop | Cloud Build trigger on git, Artifact Registry, image digest not `:latest` |
| Only signed artifacts | Binary Authorization enforcement |
| Someone is actually paged | Cloud Monitoring alerting policy on symptoms, channel is Pub/Sub, PagerDuty, or a webhook. Email alone fails this pillar. |
| You can tell a story after the incident | Cloud Logging with a sink if retention exceeds the default bucket. Trace for latency. Admin Activity for who changed it. |
| The goal is numeric | SLO on availability or latency. Error budget is `1 - SLO`. A 99.9% monthly SLO allows about 43 minutes of downtime. Spend the budget on releases. Freeze releases when the budget is gone. |
| Toil is shrinking | Managed service instead of patching VMs. VM Manager only while the workload is still a VM. |
| Change has a backout | Rolling update with surge, Cloud Deploy rollback, Cloud SQL PITR, a tested restore |
| People know what to do at 02:00 | A short runbook linked from the alert: symptom, check, rollback, who to call |

### Error budget arithmetic

A 99.9% SLO over 30 days:

- Allowed bad time = 0.1% of 30 days = 43.2 minutes.
- A 99.95% SLO allows about 21.6 minutes.
- A 99.99% SLO allows about 4.3 minutes.

Do not alert on a single 500 if the SLO is monthly. Alert on burn rate: a fast burn pages, a slow burn opens a ticket. CPU is not the SLO.

### What fails the pillar

- `kubectl apply` from a laptop on Friday
- Alerts that only email a shared inbox
- No rollback
- A resize as the first response to latency, before a trace
- Snowflake console edits that Terraform will overwrite, or the reverse, two owners of one resource

## Pillar 2 — Security

Goal: only the right principal, on the right path, can read or change data, and you can prove it.

### Layers, in order

| Layer | Control | Stem that requires it |
| --- | --- | --- |
| Identity | Groups, predefined or custom roles, no Owner or Editor | Any least-privilege question |
| Workload identity | Attached service account, Workload Identity on GKE, federation from GitHub | “No JSON keys” |
| Who may use the identity | `serviceAccountTokenCreator` or `serviceAccountUser` on the account resource | “Who can deploy as this account” |
| Deny | IAM deny policy | “Even if someone later grants admin” |
| Configuration guardrail | Organization policy | External IP, allowed regions, public buckets, public Cloud SQL |
| Network guardrail | Hierarchical firewall, VPC firewall, IAP | SSH from the internet, a deny the project cannot lift |
| Data plane perimeter | VPC Service Controls plus Access Context Manager | Copy to a personal project must fail even when IAM allows it |
| Encryption | Google-managed by default. CMEK or Cloud HSM when they must control the key. | “Disable the key and the data is unreadable” |
| Secrets | Secret Manager, not metadata and not the image | Passwords, tokens |
| Data in use | Confidential VM or Confidential GKE | Host must not read guest memory |
| Supply chain | Build, scan, attest, Binary Authorization, digest | “How do you know the image was not swapped” |
| Sensitive content | Sensitive Data Protection | PII, PAN, before logs or before a model |
| AI abuse | Model Armor, tenant filter on retrieval | Chatbot, prompt injection, cross-tenant answers |
| Support access | Access Transparency, Access Approval | “Did Google staff open this” |
| Regulated folder | Assured Workloads, resource location constraint | EU data, a named regime |
| Audit | Admin Activity always. Data Access when reads must be recorded. Sink for retention. | Auditor, three years |

Separation of duties: the group that administers KMS is not the group that reads the bucket. The group that sets IAM is not the only group that uses the powerful role. Implement that with two groups, not with a shared Owner.

### What fails the pillar

- `allUsers` on a data bucket
- Cloud SQL public IP and `0.0.0.0/0`
- A key file in git
- Security rules `allow read, write: if true` on Firestore used by mobile clients
- RAG with no tenant predicate
- Logging request bodies that contain card numbers

## Pillar 3 — Reliability

Goal: the stated availability, the stated RPO, and the stated RTO. Nothing stricter unless they asked.

### Match the failure to the product

| They must survive | Pattern |
| --- | --- |
| One process crash | More than one replica, health checks, restart |
| One zone | Regional MIG, regional GKE, Cloud Run, Cloud SQL regional HA, regional PD only if you are stuck on a VM |
| One region, and the RPO can be minutes | Cross-region replica you promote, or a backup in another region. Write the RPO as the replication lag or the backup interval. |
| One region, and writes must continue with strong consistency | Multi-region Spanner. Not a Cloud SQL read replica. |
| Bad deploy an hour ago | Cloud SQL PITR, Cloud Run revision rollback, GKE rollback, a table snapshot |
| Deleted object | Versioning, soft delete, or retention. A lifecycle delete will not undo itself. |
| Expired data-center link | Two HA VPN tunnels with BGP, or two Interconnect attachments. One tunnel is not the 99.99% design. |

### RPO and RTO

- **RPO** is how much data you can lose. Backups set it. A replica’s lag sets it. Spanner multi-region synchronous replication sets it near zero.
- **RTO** is how long until service returns. Automatic failover is seconds to minutes. A restore from a dump is however long the import takes, which you must have tested.
- A snapshot you have never restored is not a plan.

### Quotas and overload

Reliability includes capacity. Reserve GPUs or machine types for a known launch. Set Cloud Run `max-instances` so a spike does not exhaust Cloud SQL connections. Use a queue so the backlog waits instead of falling over. Retry with backoff. Do not retry a 4xx.

### What fails the pillar

- One zone for a 99.9% customer-facing tier
- Spot or Local SSD as the only copy
- Multi-region everything when the PDF says 99.9% in one country (you failed cost, and you did not become more correct)
- A read replica described as failover
- Health-check initial delay shorter than boot, so the group kills healthy new VMs

## Pillar 4 — Performance

Goal: the latency and throughput budget, with evidence.

| Lever | When |
| --- | --- |
| Put compute in the users’ region | Chatty requests. A distant low-carbon region loses if the budget is 5 ms. |
| Global external Application Load Balancer, Premium tier | Users on several continents, HTTP |
| Cloud CDN or Media CDN | Cacheable HTTP or video. Do not cache personalized responses. |
| Memorystore | Hot keys, sessions you can rebuild |
| Partition and cluster BigQuery | The filter is a date or an id. Stop `SELECT *`. |
| Cloud SQL read replica or AlloyDB read pool | Read-heavy, lag is acceptable |
| Spanner or more processing units | The write rate does not fit one Cloud SQL node and the model is relational and global |
| Hyperdisk or pd-ssd, sized for IOPS | A database you are forced to run on a VM |
| Local SSD | Scratch and shuffle only |
| Direct VPC egress, private path | Do not send Cloud SQL traffic through NAT |
| Profile and trace before you buy | Cloud Profiler, Cloud Trace, Query Insights, a load test |
| Connection pooling | Serverless to Cloud SQL. One connection per request will exhaust `max_connections`. |

Performance and cost fight. A CDN is both. A bigger VM with no measurement is neither.

## Pillar 5 — Cost

Goal: meet the other pillars, then stop paying for idle.

| Lever | Pays off when |
| --- | --- |
| Cloud Run or functions scale to zero | Nights are quiet and cold start is acceptable. Min instances if it is not. |
| GKE Autopilot | The cluster would be half empty |
| Spot | The job retries |
| Committed use | The baseline runs all month |
| Reservations | You need stock, not a discount |
| Storage class or Autoclass | Access is rarer than Standard. Respect minimum duration. |
| BigQuery partition, cluster, editions only if steady | On-demand bytes are the spike. Slots are the warehouse that runs all day. |
| Labels and billing export | You cannot optimize a bill you cannot slice |
| Budgets | They notify. They do not stop spend unless you built that. |
| Right region and right tier | Standard network tier for regional cheap egress. Premium when the load balancer is global. |
| Delete stopped disks, idle IPs, old images | Stopped VMs still bill the disk |

The cheapest design that misses 99.9% is not cost-optimized. It is unavailable.

CapEx versus OpEx, which section 4.2 names: buying servers is CapEx. Google Cloud is OpEx. Committed use is a middle. Say so when the finance stakeholder asks. Do not pretend a CUD is the same as an on-demand VM.

## Pillar 6 — Sustainability

Goal: useful work per unit of emissions, after latency, residency, and reliability are met.

- High utilization beats a fleet of idle VMs. Autoscaling and serverless help this pillar and the cost pillar together.
- A managed service is usually better than a poorly used VM because unused capacity is shared.
- Choose a lower-carbon region when the latency budget and the data-residency rule allow it. Carbon-free energy percentage is published per region. Do not move a 5 ms database across a continent to chase it.
- Carbon Footprint exports emissions by project and service into BigQuery. That is the measurement. It is not the architecture.
- Do not add a second continent “for sustainability” if it doubles cross-region traffic.

## Applying all six to one system

A payments API, users in one country, 99.9%, card data, four engineers, quiet nights, last outage was a bad manual deploy.

| Pillar | Decision |
| --- | --- |
| Operational excellence | Cloud Build and Cloud Deploy, SLO on 5xx and latency, page a channel, rollback a revision |
| Security | Private Cloud SQL, no PAN in logs, CMEK if policy says so, Sensitive Data Protection or a tokenizer, group IAM |
| Reliability | Regional Cloud SQL HA, Cloud Run in that region, backups and a tested PITR. Not multi-region Spanner. |
| Performance | Same region as the users, a small Memorystore only if the stem has a hot read, connection pooling |
| Cost | Min instances 0 or 1 based on cold-start budget, max instances capped to the database |
| Sustainability | One region, high utilization, no idle VM fleet |

## Exercises

1. Monthly SLO is 99.95%. How many minutes of downtime is the budget, roughly?
2. Two designs both meet 99.9%. One is multi-region Spanner. One is regional Cloud SQL HA. The stem also says “reduce cost” and the data is SQL Server with no rewrite. Which pillars does Spanner fail?
3. Alerts are email to a list. Two outages were missed. Which pillar, and what do you change without adding a new database?
4. A teammate moves the checkout database to a distant low-carbon region. Latency budget is 5 ms. Which pillar did they misread?
5. Name the control that stops a project Owner from creating a public VM IP.

### Answers

1. About 21.6 minutes in a 30-day month (0.05% of 43,200 minutes).
2. Cost, and also the “no rewrite” constraint. Reliability is already met by regional HA. Spanner does not run SQL Server stored procedures unchanged.
3. Operational excellence. Symptom alerts to an on-call channel, and a pipeline with rollback. CPU email is the thing you delete.
4. Sustainability does not override performance or the written latency number. Keep the database local. Raise utilization instead.
5. Organization policy `constraints/compute.vmExternalIpAccess`. IAM Owner does not beat it.
