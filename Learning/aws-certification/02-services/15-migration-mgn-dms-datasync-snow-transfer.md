# Migration: MGN, DMS, DataSync, Snow, Transfer Family

SAP domain 4. SAA task 3.5 and 4.1. DVA lists Application Migration Service as out of scope. You still recognize the name so you do not pick it in a developer question about an SDK.

Official:

- https://docs.aws.amazon.com/mgn/latest/ug/what-is-application-migration-service.html
- https://docs.aws.amazon.com/dms/latest/userguide/Welcome.html
- https://docs.aws.amazon.com/datasync/latest/userguide/what-is-datasync.html
- https://docs.aws.amazon.com/snowball/latest/developer-guide/what-is-snowball.html
- https://docs.aws.amazon.com/transfer/latest/userguide/what-is-aws-transfer-family.html
- https://docs.aws.amazon.com/migrationhub/latest/ug/whatishub.html

## The table you memorize

| You have | You use |
| --- | --- |
| Virtual machines, a cutover window, little change | Application Migration Service. Replication agents, a staging area, a cutover |
| Servers you are already replicating for DR and you will fail over as the migration | Elastic Disaster Recovery |
| A database that must stay online, then a short cutover | DMS. Full load plus CDC. Endpoints for source and target |
| A different engine (Oracle to PostgreSQL) | SCT for schema and code, DMS for data |
| NFS, SMB, HDFS, object stores, on a schedule, with verification | DataSync |
| People and scripts that speak SFTP, FTPS, FTP, or AS2 | Transfer Family into S3, EFS, or FSx |
| More data than the link can carry in the window | Snowball Edge. Snowcone-class for smaller edge jobs. Check the current device names. The exam still says Snow Family |
| A long-distance upload of large objects and the link is good enough | Multipart upload, or Transfer Acceleration if the distance is the problem. DataSync if you want a schedule and a report |
| An inventory before any of this | Application Discovery Service, agent or agentless |
| A board slide of progress | Migration Hub |

Bandwidth rule of thumb: a saturated 1 Gbps link moves on the order of 10 TB a day if you are lucky and nobody else uses it. If the math misses the change window, look at Snow. Do not "just use DataSync" because it is the newer word.

## How you keep the cutover short

DMS CDC replicates changes after the full load. You cut over when the lag is small. You do not stop the source for the whole copy. MGN continuous replication does the same for disks. Snow is offline. You still need a delta tool (often DataSync) for files that changed while the device was on a truck.

## Security on the tool

Replication instances in a private subnet. Security groups open only to the source. KMS on the target. No public snapshots. IAM roles, not keys in the agent config you commit to git. A DMS task does not need `AdministratorAccess`.

## Identity and DNS during the move

Managed Microsoft AD if Windows auth must survive. Identity Center if humans are ready to federate. Route 53 weighted records to shift a percentage of users. A big-bang DNS change with a day-long TTL is how you extend an incident.

## Commands

```bash
aws dms create-replication-task --replication-task-identifier orders --migration-type full-load-and-cdc \
  --replication-instance-arn "$RI" --source-endpoint-arn "$SRC" --target-endpoint-arn "$TGT" \
  --table-mappings file://tables.json
aws dms describe-replication-tasks --filters Name=replication-task-id,Values=orders
aws datasync create-task --source-location-arn "$SRC" --destination-location-arn "$DST"
aws transfer create-server --protocols SFTP --identity-provider-type SERVICE_MANAGED
```

MGN and Snow are console-and-ops workflows. Know the sequence: install agent, replicate, test instance, cutover, finalize. The exam asks which tool, not the click path.

## Exercises

1. 40 TB, 100 Mbps, this weekend. Which tool?
2. Oracle to Aurora PostgreSQL, downtime under ten minutes. Which two tools, in which order?
3. A partner will keep uploading CSVs with SFTP after the migration. DataSync or Transfer Family?
4. Two hundred VMs, no code changes, cut over application by application. MGN or DMS?

## Answers

1. Snow Family. 100 Mbps cannot move 40 TB in a weekend. DataSync after the device arrives only if a delta remains.
2. SCT to convert, DMS full load plus CDC to move, cut over when CDC lag is inside the window.
3. Transfer Family. DataSync is your copy. It is not their ongoing SFTP endpoint.
4. MGN. DMS moves databases, not the VM estate. You might use both: MGN for the servers that stay servers, DMS for the database you are replatforming.

## Which R, then which tool

Retire what nobody uses. Retain what must stay on-premises this wave. Relocate is VMware to VMware on AWS, not a lift of a VM onto EC2. Rehost is Application Migration Service onto EC2. Replatform is one managed-service change, such as the database onto RDS. Repurchase is SaaS. Refactor is a new design and does not fit a lease that ends in a quarter.

Discovery Service collects dependencies. Migration Hub tracks tools. Migration Evaluator is the cost comparison against the data center. The exam will not ask you to compute the dollars. It will ask which fact changes the tool: the protocol, the downtime window, the size of the link, whether the engine can change.

## MGN

Install the agent, replicate block changes continuously, launch a test instance, cut over, finalize. The cutover is minutes when replication is healthy. It is crash-consistent at the disk. It is the wrong tool for a database whose RPO is a transaction log you can reason about. Use MGN for the servers and DMS for the database. Do not start with a refactor of the estate in the same weekend.

## DMS and schema conversion

Full load copies existing data. CDC keeps up with changes. Full load plus CDC is the minimal-downtime path. The replication instance needs CPU, memory, and a security group path to the source and the target. A tiny instance is why CDC lag blows the maintenance window. Validate row counts or checksums before you let writers back on the source.

Homogeneous (Oracle to RDS Oracle) does not need schema conversion. Heterogeneous (Oracle to Aurora PostgreSQL) needs the Schema Conversion Tool first, then a human for what SCT could not convert, then DMS. SCT does not move rows. DMS does not rewrite procedures. LOB columns and unsupported types are why a task looks "almost done" and is not. Multi-AZ on the replication instance is the resilience of the migration itself.

Cutover: stop writers, let CDC catch up, verify, repoint, do not start the old writers. Two writers without a design is split brain.

## Files

DataSync copies and verifies, on a schedule, with an agent at the source when the source is on-premises. It is the online file move. Storage Gateway is the ongoing protocol endpoint you leave behind, not the one-time copy. Transfer Family is SFTP, FTPS, or FTP into S3 or EFS, for a partner who will keep uploading. Transfer Acceleration is an S3 feature for long-distance uploads. It is not DataSync and it is not Snow.

Snow is the device you ship when the link cannot finish. A rough check: if the transfer on the available bandwidth takes more than about a week, price Snow. After the device imports into S3, DataSync or a final sync takes the delta if the source is still changing. Snowcone is the small device. Snowball is the usual one. Snowmobile is the truck and almost never the answer.

## The weekend

Lower DNS TTL days before the cutover. Weighted Route 53 records move a percentage. A day-long TTL makes Sunday's cutover invisible until Monday night. The network path (VPN now, Direct Connect when the circuit exists) and identity (Identity Center, plus Managed AD if Windows must join) land before the VMs. Encrypt the replication path. Do not open the database to `0.0.0.0/0` to make the replication instance "easier."

## More exercises

5. CDC lag grows every afternoon and the replication instance CPU is pegged. The source is fine. What do you change before the cutover date?
6. SCT reports 40 procedures it could not convert. The team plans to cut over to Aurora PostgreSQL on Saturday. What is the honest landing zone if those procedures are required?
7. Users must keep `\\fileserver\share` and NTFS permissions. DataSync into S3, or something else?
8. 5 TB on a 10 Gbps link, this weekend. Snow or DataSync?
9. The migration window is four hours for the VMs and under a minute of data loss for PostgreSQL. Which tool for which?

## Answers

5. A larger replication instance, and a look at LOB and parallel load settings. Lag that tracks CPU means the task cannot keep up with the change rate. Cutting over anyway exceeds the RPO.
6. Stay on the source engine, on RDS or on EC2, until those procedures are rewritten or accepted as gaps. Aurora is the target only after the gap list is signed. A conversion report with failures is not a green cutover.
7. FSx for Windows File Server joined to AD. DataSync can copy into it. S3 does not preserve NTFS ACLs for users who still open the share. File Gateway is the SMB-in-front-of-S3 option when ACLs can soften.
8. DataSync. 5 TB on 10 Gbps is hours, not a week. Snow adds shipping time you do not need.
9. MGN for the VMs. DMS CDC for PostgreSQL, with writers stopped only for the final catch-up. Do not use a crash-consistent MGN cutover as the database RPO plan.
