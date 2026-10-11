# Migration, hybrid, and multicloud

PCA 1.4 and 1.5. ACE needs the product names when a task says “move this VM” or “load this data”.

## Disposition first

For every workload, say one of: **build**, **buy**, **modify**, **deprecate**. The exam lists those four. A lift of a server nobody uses fails the deprecate test. A SaaS the business already pays for fails the build test.

Then pick a movement pattern:

| Pattern | Meaning | Typical landing zone |
| --- | --- | --- |
| Retire | Turn it off | None |
| Replace / buy | Adopt SaaS or a managed API | The product, plus integration |
| Rehost | Same VM, new place | Compute Engine, or VMware Engine if vSphere must remain |
| Replatform | Same app, managed platform | Cloud SQL, Cloud Run, GKE |
| Refactor | Change the app | Cloud Run, GKE, Pub/Sub, Spanner, as the design needs |

## Migration Center

PCA 1.4 names **Google Cloud Migration Center**. It discovers servers, builds dependency maps, and groups waves. Use it before you argue about products. A migration plan the exam will respect includes:

- Inventory and dependencies (Migration Center)
- Network plan (addressing, DNS, Interconnect or HA VPN, bandwidth)
- Data move (Storage Transfer, Database Migration Service, Datastream, Transfer Appliance)
- License map (what the vendor allows in Google Cloud, sole tenant or not, pay-as-you-go images)
- Pilot or proof of concept
- Wave plan and a rollback
- Test plan (functional, performance, failover)
- Cost comparison, CapEx to OpEx
- Who owns the cutover (change management)

```bash
gcloud services enable migrationcenter.googleapis.com
# Discovery often uses collectors you install on-premises.
# The console is the working UI. Know the product’s job.
```

## Move virtual machines

**Migrate to Virtual Machines** (the product that followed Migrate for Compute Engine) replicates disks and cuts over into Compute Engine. Use it for rehost. Test clones before cutover. Replication is not a backup policy after you land.

**Migrate to Containers** extracts a VM into a container workload when the app can live that way. It is not magic for a kernel module.

```bash
gcloud services enable vmmigration.googleapis.com
gcloud alpha migration vms list --location="$REGION" 2>/dev/null | head
```

## Move databases and files

Covered in earlier chapters. The mapping:

| Source | Tool |
| --- | --- |
| MySQL, PostgreSQL, SQL Server, Oracle into Cloud SQL, AlloyDB, or Spanner | Database Migration Service |
| Ongoing CDC into analytics | Datastream |
| Files, S3, Azure, another bucket | Storage Transfer Service |
| Many terabytes, weak network | Transfer Appliance |
| Hadoop | Dataproc, then consider BigQuery or Bigtable as the destination you refactor toward |

## VMware, bare metal, and other clouds

| Product | Answer it gives |
| --- | --- |
| Google Cloud VMware Engine | Keep vCenter, vSphere, and NSX. The private cloud runs on Google’s hardware. Use it when the stem says VMware tools, existing operational model, or a license that is tied to vSphere. It is not the cheapest long-term home for a cloud-native rewrite. |
| Bare Metal Solution | Certified hardware for Oracle or similar, adjacent to the VPC. |
| SAP on Google Cloud | Certified shapes and Workload Manager checks. |
| GKE Multi-Cloud | GKE attached to AWS or Azure clusters, one fleet. |
| Google Distributed Cloud | Run Google Cloud control on your site, including connected, air-gapped, VMware, and bare metal software. Sovereignty and edge. |
| Cross-Cloud Interconnect | Private bandwidth to another cloud. |
| BigQuery Omni | Query data that stays in AWS or Azure. |

Hybrid network for all of these is still HA VPN or Interconnect plus Cloud Router, or NCC as the hub. DNS forwarding so both sides resolve names. Identity: Cloud Identity as the IdP, or federation with Active Directory (Managed Microsoft AD if you must host AD domain controllers as a managed service).

## Strangler and waves

Do not big-bang a hospital or a retailer. Put a facade (load balancer, Apigee, or a routing layer) in front. Move one capability. Keep the legacy interface the case study says you must keep (EHR’s insurer links are the classic “do not migrate this yet”).

Each wave has an owner, a test, a backout, and a metric that says it worked (KPI). That is section 1.1’s success measurement, not a nice-to-have.

## Future improvements (PCA 1.5)

After the first landing, the cloud-first move is usually:

- Managed database instead of a VM database
- Cloud Run or GKE instead of a pet VM
- Autoscaling instead of a sized-for-peak VM
- IaC and CI/CD instead of a runbook
- A data platform (Pub/Sub, Dataflow, BigQuery) instead of a nightly file drop

Say that as a phase. Do not block the migration on the end state if the data center lease is expiring. The exam likes a sequenced plan.

## Exercises

1. 150 unchanged VMs, a lease expiring in four months, no container skill. First move?
2. The team lives in vCenter and will not retool this year. Which product?
3. Oracle licenses are tied to specific hardware the vendor certified. Which adjacent product do you evaluate?
4. What does Migration Center give you that a spreadsheet of hostnames does not?
5. A case study says insurer links stay on-premises. Do you include them in wave 1?

### Answers

1. Rehost with Migrate to Virtual Machines onto Compute Engine, after Migration Center grouping and a network path. Refactor is a later phase.
2. Google Cloud VMware Engine.
3. Bare Metal Solution, with the vendor’s current certification list. Do not promise a normal n2 VM until you have checked.
4. Dependency mapping and wave planning, not only a list of names.
5. No. You integrate them (hybrid connectivity, Apigee or the existing interface). You do not force a migration the business forbade.
