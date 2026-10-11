# Cost, billing, and migration deep dive

Read foundations chapter 03 and `14-migration-hybrid-multicloud.md`. This file is the bill, the estimate, and the migration plan PCA section 1.4 expects you to write.

## How money is attached

A billing account pays for projects. One project has one open billing link. IAM on the billing account is separate from IAM on the project. `roles/billing.admin` can link projects and see invoices. `roles/billing.viewer` can see cost and cannot change the link. A project Owner cannot see the company invoice unless they also have a billing role.

```bash
gcloud billing accounts list
gcloud billing projects describe "$PROJECT_ID"
gcloud billing projects link "$PROJECT_ID" --billing-account="$BILLING_ACCOUNT"
gcloud billing projects unlink "$PROJECT_ID"
```

Unlink stops new spend only in the sense that resources that require billing may be shut off or blocked. It is a blunt instrument. It is not what a budget does.

## Budgets

A budget has an amount, a scope (billing account, project, or labels), and thresholds (50%, 90%, 100%, or a forecast). At a threshold it notifies email and, if you configure it, Pub/Sub. The notification does not delete VMs.

If the stem says “stop spend at the cap”, you must add a subscriber that shuts the project down or removes the billing link, and you must accept that this causes an outage. Say that tradeoff. If the stem says “warn finance”, the budget alone is the answer.

Labels are how a budget or a report slices by team. Agree `env`, `app`, and `owner` before the bill is large. Labels are not permissions.

## Exports

| Export | Use |
| --- | --- |
| Standard usage to BigQuery | Cost by service, SKU, project, label. The default analysis answer. |
| Detailed usage | Resource-level rows. Larger. Use when standard is too coarse. |
| Pricing export | The rate card, so you can recompute. |
| File export to Cloud Storage | A dump, not SQL |

```sql
SELECT
  service.description AS service,
  SUM(cost) AS cost
FROM `PROJECT.billing.gcp_billing_export_v1_ACCOUNT`
WHERE invoice.month = "202610"
GROUP BY service
ORDER BY cost DESC
```

The table name includes the billing account id. The query is the skill. The exact table suffix is in the export setup screen.

## Discounts and commitments

| Mechanism | You configure it? | Interruption? | Best for |
| --- | --- | --- | --- |
| Spot VM or Spot pod | Yes | Yes | Batch, CI, fault-tolerant workers |
| Sustained use | No, automatic on families that still have it | No | Long-running VMs in that family |
| Resource-based CUD | Yes, 1 or 3 years, vCPU and memory | No | Steady Compute Engine or GKE node baseline |
| Spend-based CUD | Yes, a dollar commit | No | A basket of services |
| Reservation | Yes | No | Capacity, not a discount by itself |

Do not put Spot under a CUD story. Do not buy a three-year commit for a workload you will shut down next quarter. Flex or a short commit is the answer when the stem says the footprint will change.

## Network and storage cost traps

- Ingress from the internet is cheap or free. Egress to the internet and cross-region egress are not.
- Premium tier uses Google’s backbone and is required for global load balancers. Standard tier is regional and cheaper.
- A multi-region bucket replicates and you pay for that. A regional bucket next to the VM is cheaper when users are not global.
- Nearline, Coldline, and Archive bill a retrieval fee and a minimum duration. Reading Archive every day costs more than Standard.
- BigQuery on-demand bills bytes scanned. A `SELECT *` on 20 TB is the bill. Partitioning is the fix. Editions bill slots whether or not the query is wise, but a wise query uses fewer slots.
- Cloud NAT is an hourly gateway plus data. Private Google Access avoids NAT for Google APIs.
- Stopped VMs bill disks and reserved IPs. Delete what you snapshot.

## Quotas are not cost

A quota failure is `QUOTA_EXCEEDED`. A budget alert is an email. A CUD is a contract. A reservation is stock. The stem’s verb tells you which. “Cannot create more CPUs” is a quota increase or a different region. “The invoice doubled” is labels, export, and a design change.

## Pricing calculator

The calculator is a web tool, not a `gcloud` command. Use it to compare two designs before you build. The exam will not ask you to click it. It will ask which design is cheaper given idle time, egress, or a storage class. You should be able to explain the comparison without a dollar figure.

## Migration plan, the document PCA wants

Section 1.4 is a plan, not a product logo. Write these headings.

1. **Disposition of each workload.** Build, buy, modify, or deprecate. A server with no users is deprecate. A SaaS you already pay for is buy. An unchanged VM is rehost (modify the location, not the software). A container is replatform. A new data model is build.
2. **Inventory and dependencies.** Migration Center discovers servers, connections, and groups. A spreadsheet of hostnames misses “this app calls that database every night.”
3. **Waves.** Small first wave as a pilot. Then batches that share a dependency. The thing the case study says must stay is not in a wave. It is an integration.
4. **Network.** Addressing that does not overlap, DNS forwarding both ways, bandwidth, HA VPN or Interconnect sized to the measured traffic, a rollback path if cutover fails.
5. **Data.** Storage Transfer, Transfer Appliance if the math says the network loses, Database Migration Service for the engine, Datastream if the destination is analytics, a freeze window, a checksum.
6. **Identity.** Cloud Identity, groups already matching job function, federation from the existing IdP, no new shared passwords.
7. **Licenses.** What the vendor allows on Google Cloud, whether sole-tenant or VMware Engine is required, bring-your-own-license versus pay-as-you-go images. This is the “financial impact” bullet.
8. **Landing zone.** Folders, projects, Shared VPC, org policies, a billing export, an audit sink. Do this before wave 1, or wave 1 invents it badly.
9. **Test.** Functional test, a performance test against the SLO, a failover test, a backout test.
10. **Cutover.** Who decides, how you move the DNS or the connection string, how you stop writes to the source, how you confirm the new primary.
11. **Rollback.** The source is still there until the soak period ends. Write the soak length.
12. **Next improvement.** Phase 2 is Cloud SQL or Cloud Run. Do not block the lease expiry on phase 2.

```bash
gcloud services enable migrationcenter.googleapis.com vmmigration.googleapis.com \
  datamigration.googleapis.com storagetransfer.googleapis.com
```

Migration Center collectors run on-premises and report in. The console is where you group waves. Migrate to Virtual Machines replicates disks and cuts over to Compute Engine. Test a clone before you cut DNS. Database Migration Service does continuous replication and then promotion. Those are different teams and different weekends. Do not schedule them as one button.

## Hybrid choices during migration

| Situation | Path |
| --- | --- |
| Lease ends in a few months, no rewrite skill | Rehost VMs, connect with HA VPN or Interconnect |
| Team will only use vCenter | VMware Engine |
| Oracle or a certified appliance | Bare Metal Solution, after the current certification list |
| One partner API, no full network merge | Private Service Connect or Apigee, not peering |
| Many sites that must reach each other | Network Connectivity Center as a hub |
| Files people mount | Filestore or NetApp, not a bucket, until the app changes |
| The PDF says the insurer link stays | Integrate it. Do not migrate it. |

## After the move

Section 1.5 is the next architecture, not a new project. Typical sequence: managed database, autoscaling, IaC, one observability stack, then retire the VM agents you no longer need. Cloud-first means you stop adding features to the pet VM. It does not mean a rewrite the week the lease ends.

## Exercises

1. A budget at 100% fired. Are the VMs stopped?
2. The invoice should be sliced by team. The export exists and every row says the same project. What is missing?
3. 80 TB must move this weekend. The circuit is 200 Mbps. Is Transfer Appliance in the conversation?
4. A cross-region read replica is promoted during a region loss. What is the RPO?
5. Name three headings that must be in the plan besides the list of VMs.

### Answers

1. No. Not unless you also automated a shutdown. The budget notified.
2. Resource labels, and the export query has to group by them. The export does not invent a team name.
3. Yes. 200 Mbps moves on the order of a couple of terabytes a day. 80 TB will not finish over a weekend on that link. Do the arithmetic in the plan.
4. The replication lag at the moment of promotion. It is not zero. Synchronous multi-region Spanner is the near-zero RPO, and it is a different design.
5. Dependencies (Migration Center), network and DNS, data movement and checksums, license impact, test and rollback, and the workloads you will not move. Any three of those.
