# Regions, zones, quotas, and pricing

## Geography

- A **region** is a set of zones in one metro, connected with low latency. Subnets, regional managed instance groups, regional Persistent Disks, and Cloud Run services are regional.
- A **zone** is a failure domain inside a region. A single VM and a zonal disk fail with the zone.
- Some products are **multi-regional** or **global**: Cloud Storage multi-region buckets, Spanner multi-region, global external Application Load Balancer, VPC networks (the network is global; subnets are regional), Pub/Sub.

Design rule: one zone is not high availability. Two zones in one region meets a typical 99.9% target for managed services that offer regional HA. Two regions is disaster recovery or a global write requirement, and it costs more. PCA punishes jumping to multi-region when the case study says 99.9%.

Network Service Tiers:

| Tier | Behavior | Pick it when |
| --- | --- | --- |
| Premium | Traffic enters Google’s network at the edge, closest to the user. Required for global load balancers. | Default for production internet apps |
| Standard | Traffic enters near the destination region, more like a regular ISP path. Regional only. Cheaper. | Cost-sensitive regional workloads |

```bash
gcloud compute addresses create web-ip --region="$REGION" --network-tier=PREMIUM
gcloud compute addresses create cheap-ip --region="$REGION" --network-tier=STANDARD
```

## Zonal versus regional resources you must not mix up

| Resource | Scope |
| --- | --- |
| VPC network | Global |
| Subnet | Regional |
| Route | Global on the VPC, next hop can be zonal |
| Firewall rule | VPC-wide, filtered by tags, service accounts, or ranges |
| External static IP for a global load balancer | Global |
| External static IP for a VM or regional load balancer | Regional |
| VM, zonal PD, Local SSD | Zonal |
| Regional PD | Regional (synchronous replica across two zones) |
| Cloud Storage bucket location | Regional, dual-region, or multi-region. The bucket name is global. |
| Filestore instance | Zonal or regional depending on tier |

## Quotas and the flexibility objective

PCA 1.2 scores “flexibility of cloud resources”. That means you design inside quotas and you request increases before launch. Quotas are per project and often per region. They are not a spending cap.

```bash
gcloud compute regions describe "$REGION" \
  --format="yaml(quotas.filter(\"metric:CPUS\"))"

# Generic quota read
gcloud alpha services quota list --service=compute.googleapis.com \
  --consumer="projects/${PROJECT_ID}" 2>/dev/null | head
```

In the console the path is IAM & Admin, or the Quotas page. An increase is a request, not an instant API mutation, for many metrics.

Capacity Planner and reservations matter when the stem is a known launch date and you cannot risk stockouts of GPUs or a machine family. A reservation holds capacity. It is not a discount.

## Pricing ideas the exams use

You are not required to memorize a price list. You are required to know which lever applies.

| Lever | What it changes |
| --- | --- |
| Spot VM | Up to a deep discount. Google can stop it. No fixed 24-hour cap anymore (preemptible VMs had a 24-hour max; Spot does not). Use for fault-tolerant batch, not for the only copy of state. |
| Committed use discount (CUD) | Commit to vCPU/memory, or to a spend amount, for 1 or 3 years. Steady production. |
| Sustained use discount | Automatic for some Compute Engine families as monthly usage grows. Do not “configure” it. |
| Storage class and retrieval | Cold data is cheap to store and costs to read. Minimum storage duration applies. |
| BigQuery editions and slots | On-demand bytes scanned versus slot capacity (Standard, Enterprise, Enterprise Plus). |
| Cloud Run | Pay while the instance is working, including idle time only if you set a minimum instance or always-on CPU. |
| GKE Autopilot | Pay for pod requests. GKE Standard: pay for nodes. |
| Network egress | Cross-region and internet egress cost. Ingress from the internet is not the expensive direction. |
| Labels | Do not change the price. They make the bill explainable. |

```bash
# Pricing calculator is a web tool, not a gcloud product.
# For a quick VM price estimate people still use the console calculator.
# Spot flag:
gcloud compute instances create batch-1 \
  --zone="$ZONE" \
  --machine-type=e2-standard-4 \
  --provisioning-model=SPOT \
  --instance-termination-action=STOP
```

Custom machine types (ACE 2.1) let you pick vCPU and memory inside a family when a predefined shape wastes one of them.

```bash
gcloud compute instances create custom-vm \
  --zone="$ZONE" \
  --custom-cpu=6 \
  --custom-memory=22
```

## Carbon and sustainability (PCA pillar)

Carbon Footprint exports estimated emissions by project and service. Region choice matters: some regions have a lower carbon grid. The exam will not ask you to fake a number. It will ask which pillar a “pick the lower-carbon region when latency allows” decision serves. That pillar is sustainability. Do not move a latency-sensitive database to a distant low-carbon region if the requirement is milliseconds.

```bash
# Carbon Footprint is enabled from the console (Billing). Data lands in BigQuery.
# There is no single create command that replaces the console setup.
```

## Free tier and trials

New billing accounts can receive trial credit. A set of products has an always-free monthly allotment (small VM shapes in specific regions, BigQuery query allowance, Cloud Storage allowance, and others). Free tier is not an architecture. Do not design production HA on the free-tier VM.

## Exercises

1. The requirement is 99.9% for a web tier in one country. A colleague proposes multi-region Spanner and a global load balancer with two continents. What do you propose instead, and which pillar did they overspend?
2. A batch render farm can lose a machine at any time. Which provisioning model?
3. Traffic from users in one region only, and the company wants the cheaper ingress path to the VM’s region. Which network tier, and which load balancer scope is then impossible?
4. A launch fails with `QUOTA_EXCEEDED` on CPUs in `us-central1`. Is that a billing budget?

### Answers

1. Regional managed services in two zones (regional MIG or Cloud Run or regional GKE, regional Cloud SQL HA). They overspent cost and possibly sustainability for a reliability target the business did not set. Multi-region is for a region-loss requirement or global writes.
2. Spot VMs, or GKE Spot pods, with the job retried by the queue.
3. Standard tier. Global anycast load balancers require Premium tier.
4. No. Quotas cap resource counts. Budgets notify on spend. Fix is a quota increase or a smaller shape in another region that has quota.
