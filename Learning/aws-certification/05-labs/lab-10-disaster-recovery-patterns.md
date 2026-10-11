# Lab 10 — Disaster recovery patterns

SAA task 2.2 and SAP tasks 1.3 and 2.2. This is a design lab. Building a second-Region Aurora Global Database, a Pilot Light fleet, or Elastic Disaster Recovery "to see" is how a weekend lab becomes a bill. You will write the four patterns, name the service that implements each, and optionally create one Route 53 health check against a public endpoint you already have.

Read `04-sap/06-disaster-recovery-design.md` alongside this file.

## The four patterns

RPO is how much data you can lose. RTO is how long you can be down. Multi-AZ is not a Region failure. A second AZ in the same Region does not answer "the Region is unavailable."

| Pattern | RPO / RTO shape | What is already running in the second Region | Service the exam wants |
| --- | --- | --- | --- |
| Backup and restore | Hours. You accept a long restore | Backups, nothing else | AWS Backup, S3 cross-Region replication, RDS snapshot copy |
| Pilot light | Minutes to an hour. Data is live, compute is small or off | The database replica. A tiny core. You scale the rest on the day | Aurora Global Database or a cross-Region read replica, AMIs copied, a pipeline that can scale |
| Warm standby | Minutes. A scaled-down copy is serving | A smaller full stack | The same services as production, smaller. Route 53 failover |
| Active/active | Near zero. Both Regions take traffic | A full stack, and the data layer can take writes in both places | Aurora Global Database write forwarding, or DynamoDB global tables. Route 53 latency or weighted records |

DynamoDB global tables are active/active by default: both Regions accept writes, and you must design for conflict. Aurora Global Database is one writer Region plus readers, unless you turn on write forwarding and accept its limits. Those two sentences separate a lot of "multi-Region database" items.

## What fails over by itself

| Failure | Fails over without you | Does not |
| --- | --- | --- |
| One AZ, RDS Multi-AZ | The database endpoint moves to the standby | A read replica. You promote that yourself |
| One AZ, Auto Scaling across subnets | New instances in the healthy subnet, if the group spans them | An instance that was not in an Auto Scaling group |
| One Region | Nothing, unless you built one of the four patterns and a DNS or Global Accelerator failover | Multi-AZ |

Elastic Disaster Recovery (DRS) is the lift-and-shift pilot light: continuous block replication of servers, and you drill a failover. Resilience Hub measures an application against a resilience policy. Fault Injection Service runs the experiment that shows the runbook is a lie. Application Recovery Controller decides whether the Region is healthy enough to take traffic, which is stricter than a single Route 53 health check. Those four are the SAP-C03 resilience additions and they are already the right nouns on SAP-C02 items about drills and routing control.

## A health check you may create

Only if you have a public HTTPS URL that is yours. A health check against `https://example.com` is rude and it does not teach you anything about your stack.

```bash
export AWS_PROFILE=sandbox
# Replace with your own URL.
aws route53 create-health-check --caller-reference "lab10-$(date +%s)" \
  --health-check-config '{
    "FullyQualifiedDomainName": "status.example.com",
    "Port": 443,
    "Type": "HTTPS",
    "ResourcePath": "/health",
    "RequestInterval": 30,
    "FailureThreshold": 3
  }'
```

A failover record has two records with the same name, `PRIMARY` and `SECONDARY`, and the primary is associated with this health check. When the check fails, Route 53 answers with the secondary. You did not create the records. The item is the association: a weighted or failover policy without a health check does not move traffic when the origin dies.

Global Accelerator is the answer when they want static anycast IPs and fast failover of non-HTTP as well as HTTP. CloudFront is the answer when they want cache, TLS at the edge, and WAF. Do not swap them because both are "global."

## The drill, on paper

1. Write the RPO and RTO as numbers before you pick a pattern. "Highly available" is not a number.
2. Name the data copy. Snapshots are backup-and-restore. A replica that is open is pilot light or better.
3. Name the DNS or routing change. Route 53 failover, Global Accelerator, or ARC routing control.
4. Name who is allowed to run the failover, and where the runbook lives. Systems Manager runbooks are the SAP-C03 operational answer.
5. Say what you will not do in the drill: you will not fail over production to prove you read this page.

## Cleanup

```bash
aws route53 list-health-checks \
  --query "HealthChecks[?CallerReference.contains(@, 'lab10')].Id" --output text
# Delete only the id you just created.
aws route53 delete-health-check --health-check-id "$HC_ID"
```

If you skipped the health check, there is nothing to delete. That is the correct outcome for this lab.
