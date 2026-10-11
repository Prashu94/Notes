# Well-Architected Framework

PCA requires this. The six pillars are operational excellence, security, reliability, performance optimization, cost optimization, and sustainability. Section 6.1 scores the operational excellence pillar by name. The others show up as the reason an answer is better.

Official overview: the Cloud Architecture Center page for the Well-Architected Framework. This chapter is a study sheet of decisions, not a copy of that guide.

## Core habits

- Write the architecture down, including the requirement that forced each product.
- Prefer fully managed services when they meet the requirement.
- Decouple with Pub/Sub, events, or a queue so a slow consumer does not fall over the producer.
- Keep tiers stateless so a zone loss is a scale event, not a data loss.
- Change through automation. A console click in production is toil.

## Pillar 1 — Operational excellence

What the exam wants you to recommend:

- Infrastructure as code (Terraform) and a pipeline (Cloud Build, Cloud Deploy).
- Small releases, canary or traffic split, a tested rollback.
- SLOs and alerts on symptoms (error rate, latency), sent to an on-call channel. Email alone is a known failure mode.
- Logs exported to a place you can query. Trace and Profiler before you resize.
- Incident review that produces a ticket, not a blame paragraph.
- Reduced toil: VM Manager or, better, a managed runtime so you stop patching pets.

A design that “works” but ships from a laptop fails this pillar.

## Pillar 2 — Security

- Least privilege IAM, groups, no basic roles, no JSON keys.
- Hierarchy: org policies and hierarchical firewalls for the rules that must win.
- CMEK when key control is a requirement. Secret Manager for secrets.
- Private nodes, IAP, no public database IPs.
- VPC Service Controls when data must not leave a perimeter.
- Software supply chain: Artifact Registry, scanning, Binary Authorization.
- For AI: Model Armor, Sensitive Data Protection, private endpoints, and a retrieval filter so tenants do not see each other’s documents.

## Pillar 3 — Reliability

- Map the target. 99.9% is multi-zone in one region for most managed services. 99.99% and 99.999% are specific products (HA VPN built correctly, Spanner multi-region, global load balancing). Do not upgrade the target on your own.
- Health checks, autoscaling, and a regional MIG or a regional GKE control plane or Cloud Run’s multi-zone serving.
- Backups and a tested restore. RPO and RTO written down. A snapshot schedule you have never restored is a hope.
- Multi-region only when a region loss is in the requirement, or writes must be global.
- Graceful degradation: a cache can fail open or fail closed. Say which.

## Pillar 4 — Performance optimization

- Put the data next to the compute. Cross-region chatty SQL is a design bug.
- CDN for cacheable HTTP. Memorystore for hot keys. Partition and cluster BigQuery tables.
- Load test, then read Monitoring and Profiler. Buy a bigger machine after the evidence, not before.
- Connection pooling in front of Cloud SQL. A serverless platform that opens a connection per request will exhaust the database.
- Right storage class and right disk. Local SSD for scratch, not for the ledger.

## Pillar 5 — Cost optimization

- Serverless or Autopilot when utilization would be low.
- Spot for fault-tolerant batch.
- Committed use for the steady baseline, on-demand or Spot for the spike.
- Lifecycle and Autoclass for objects. Editions and slots only when BigQuery spend is steady enough to justify them.
- Labels and billing export so a conversation about cost has data.
- The cheapest design that misses the availability target is not optimized. It is wrong. Meet the requirement, then reduce waste.

## Pillar 6 — Sustainability

- Managed services and high utilization waste less capacity than a fleet of idle VMs.
- Region choice can follow the lower-carbon grid when latency and residency allow.
- Do not add a second continent “for sustainability” if it doubles cross-region traffic and the users are in one country.
- Carbon Footprint is how you measure. It is not itself the architecture.

## How a question uses a pillar

The stem will not always name the pillar. You name it.

| If the stem emphasizes | You bias toward |
| --- | --- |
| “Prove we can operate this”, “too many manual steps”, “alerts were missed” | Operational excellence: pipeline, SLO, on-call channel |
| “Only this team may see the data”, “keys”, “partners” | Security: IAM, CMEK, VPC-SC, IAP |
| “99.9%”, “zone maintenance” | Reliability: regional HA, not a second continent |
| “p95 latency”, “dashboard is slow” | Performance: CDN, cache, partition, colocation, profile first |
| “bill doubled”, “idle at night” | Cost: scale to zero, Spot, lifecycle, CUDs |
| “carbon goals”, “region choice is free given latency” | Sustainability: region and utilization |

When two answers both meet the functional need, pick the one that serves the pillar the stem emphasized and that adds the least extra architecture.

## Exercise

A payments API has these facts: users in one country, 99.9% target, card numbers in the payload, a team of four with no Kubernetes experience, nights are quiet, and last quarter’s outage was a bad manual deploy.

Write one product choice for compute, one for the database, one control for card data, and one change for the outage. Name the pillar for each.

### A solid answer

- Cloud Run in one region (cost and operational excellence: no cluster, scales down).
- Cloud SQL regional HA, private IP (reliability matches 99.9%, not Spanner).
- Tokenize or de-identify with a vault or Sensitive Data Protection, do not log PANs, CMEK on the database if policy requires customer-managed keys (security).
- Cloud Deploy or at least Cloud Build with a reviewed rollout and a rollback, plus an SLO alert to a real channel (operational excellence).
