# Disaster recovery design

SAP tasks 1.3 and 2.2. SAA task 2.2 uses the same four patterns with less design around them.

Official: https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/disaster-recovery-workloads-on-aws.html

## Definitions

RTO is how long you may be down. RPO is how much data you may lose. They are independent. A one-minute RPO with a 12-hour RTO is a real requirement (replicate continuously, rebuild compute slowly). A 24-hour RPO with a 15-minute RTO is also real (last night's backup is acceptable, the replacement stack must already be warm).

Multi-AZ is not DR for a Region failure. It is HA for an AZ failure.

## The four patterns

| Pattern | Compute in the recovery Region | Data | Typical RTO | Cost |
| --- | --- | --- | --- | --- |
| Backup and restore | Built at failover time | Backups, snapshots, CRR | Hours | Lowest |
| Pilot light | Off or minimal | Live replication | Tens of minutes | Low |
| Warm standby | Scaled-down full stack | Live replication | Minutes | Medium |
| Multi-site active/active | Serving traffic | Multi-Region writes or careful read-local design | Near zero | Highest |

Match the pattern to the numbers. Do not buy active-active for a 24-hour RTO.

## Data services

| Data | AZ failure | Region failure |
| --- | --- | --- |
| RDS | Multi-AZ, automatic | Cross-Region replica, you promote it. Or AWS Backup copy, you restore it |
| Aurora | Storage across 3 AZs, failover to a reader | Aurora Global Database. Typical lag under a second. Promote the secondary |
| DynamoDB | Built in | Global tables. Active-active. Last writer wins. Not a cross-Region transaction |
| S3 Standard | Built in | CRR. Versioning required. RTC for a 15-minute commitment. Does not replace a database transaction |
| EBS | Snapshot and recreate in another AZ | Copy the snapshot to the other Region, or DRS block replication |
| EFS | Multi-AZ file system if you chose it | AWS Backup copy |

## Compute and DNS

Elastic Disaster Recovery: continuous block replication of servers into a staging area, then a failover launch. Use it when the workload is still servers and will not be refactored before the RTO is due. Run a drill. A drill is not a failover.

Route 53 failover plus health checks for active-passive. Latency routing for active-active. Weighted records to shift a migration. Low TTL on records you must move. ARC routing controls when the failure is gray: the Region answers health checks and is still not serving correctly. You flip a control. You do not wait for DNS health to notice.

An Auto Scaling group in the recovery Region at desired 0 is pilot light only if the data is already there and the launch will succeed. Check the AMI, the KMS key, the quota, and the secrets replica.

## Backup

AWS Backup plan across services, copy to a second Region, vault in a second account, vault lock so an attacker with admin in the source account cannot delete the recovery points. A snapshot in the same account as the workload is not a ransomware design.

PITR on RDS and DynamoDB beats a nightly snapshot when the RPO is minutes. Say the number.

## What "automatic" excludes

A runbook that says the architect edits a DNS record is not automatic. A health check, a routing policy, and a database that fails over without a ticket is automatic. Promoting an Aurora secondary can be automated. It is still a decision you should test, because failovers have a write-freeze moment.

## Scenario answers you should be able to say

1. RPO 5 minutes, RTO 4 hours, SQL, lowest cost. Automated backups or PITR with cross-Region copy. Not Global Database unless the RTO shrinks.
2. RPO 1 second, RTO 10 minutes, PostgreSQL. Aurora Global, pilot light or warm standby for the app, Route 53 failover, a practiced promote.
3. RPO near zero, both Regions write, key-value. DynamoDB global tables. Not Aurora multi-master.
4. Two hundred servers, no refactor this year, RTO 2 hours. Elastic Disaster Recovery, plus a drill.
5. The health check stays green during a partial Region failure. ARC routing control, not another Route 53 health check on the same endpoint.

## Commands

```bash
aws backup create-backup-plan --backup-plan file://plan.json
aws backup start-restore-job --recovery-point-arn "$RP" --metadata file://meta.json --iam-role-arn "$ROLE"
aws drs describe-source-servers
aws route53 list-health-checks
```

Direct Connect and Transit Gateway in the recovery Region are part of the design when the users are on-premises. A DR Region with no network path back to the office is a design that fails the failover test even if the compute comes up.

## Pick the pattern from the numbers

RPO is data loss. RTO is downtime. Multi-AZ is not a Region failure. Get both numbers before you name a product.

| Pattern | Already running in the other Region | Typical fit |
| --- | --- | --- |
| Backup and restore | Backups only. You build the stack at failover | RTO of many hours, lowest cost |
| Pilot light | The data is live. Compute is small or off | RTO of tens of minutes if you have timed the scale-up |
| Warm standby | A scaled-down full stack | RTO of minutes. You pay for the small stack every day |
| Active-active | Both Regions serve | Near-zero RTO. Writes in both places need a conflict story |

Aurora Global Database is one writer Region, sub-second storage lag, and a promote you must practice. DynamoDB global tables accept writes in each Region and replicate asynchronously. A strongly consistent read does not cross Regions. S3 CRR is not a database strategy. Replication Time Control is the 15-minute object RPO, and delete replication can delete the replica too. AWS Backup with a vault lock in another account is the ransomware copy. A snapshot in the same account is what the attacker deletes.

Route 53 failover needs a health check and a TTL the RTO can afford. Latency routing is active-active. ARC routing controls are for a gray failure where the health check stays green. Quotas in the standby Region are part of the design. An AMI, a KMS key, and a secrets replica that were never copied are why the launch at desired 0 does not save you.

Elastic Disaster Recovery is the server product when they will not refactor. It is not the database product when Aurora or DMS already replicates the log.

## More exercises

6. S3 CRR with delete-marker replication, and a backup vault in the same account. An attacker deletes objects and recovery points. What still exists?
7. RPO of 30 seconds, RTO of 8 hours, SQL, lowest cost. Global Database or PITR with a cross-Region copy?
8. The promote runbook has never been timed. The RTO is 10 minutes. What claim can you not make?
9. Both Regions write the same DynamoDB key. What did you accept when you chose global tables?
10. A NAT and a Direct Connect exist only in the primary Region. The compute fails over. What do office users still lack?

## Answers

6. Nothing you can restore, if the replica honored the delete and the vault was in the account they controlled. You needed Object Lock or a vault lock in another account, and replication that does not propagate deletes to the locked copy.
7. PITR or backups copied to the other Region. Eight hours is enough to restore. Global Database meets a much tighter RTO and costs more than this stem asked for. Thirty seconds of RPO is the part that rejects a nightly snapshot. PITR can meet it. A daily copy cannot.
8. The 10-minute RTO. You have a document. You do not have a measurement. Drill it and write down the actual time.
9. Concurrent writes and a conflict. Last-writer-wins is not a business rule. If both Regions must write, the application has to tolerate that. If it cannot, use one writer.
10. A path. The recovery Region needs its own egress and its own hybrid connection or a VPN, or the office cannot reach the recovered app. Compute in isolation is not a failover.
