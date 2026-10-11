# Databases: RDS, Aurora, DynamoDB, and the purpose-built engines

SAA 2.2, 3.3, 4.3. SAP 2.4, 2.5, 4.3, 4.4. DVA task 1.3. DynamoDB code is in `05-dva/06-dynamodb-for-developers.md`. This file is the choice and the operations.

Official:

- https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Welcome.html
- https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/CHAP_AuroraOverview.html
- https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Introduction.html
- https://aws.amazon.com/getting-started/decision-guides/ (Choosing an AWS database)

## Pick from the access pattern

| Pattern | Engine |
| --- | --- |
| Joins, transactions, a known SQL engine, moderate scale | RDS for MySQL, PostgreSQL, MariaDB, Oracle, or SQL Server |
| SQL, MySQL or PostgreSQL compatible, higher throughput, fast failover, many readers | Aurora |
| SQL, spiky, scale down when idle | Aurora Serverless v2 |
| Key-value or a known query on a partition key, extreme scale, single-digit milliseconds | DynamoDB |
| Documents, MongoDB API | DocumentDB. Test the API. Not every Mongo feature exists |
| Graph traversals | Neptune |
| Wide column, Cassandra API | Keyspaces |
| In-memory cache | ElastiCache. See the cache chapter |
| In-memory and durable, Redis API | MemoryDB |
| Warehouse scans, columnar | Redshift |
| Full text and log search | OpenSearch Service |
| Time series | Timestream when it is offered. Otherwise DynamoDB with a time sort key |
| Ledger, immutable history | QLDB. Recognize it. It is not on every in-scope list. Do not pick it for a normal orders table |
| Global multi-Region writes, key-value | DynamoDB global tables |
| Global SQL reads, one write Region, sub-second replica lag | Aurora Global Database |

"We might need joins later" is not a reason to avoid DynamoDB if the current access is a key lookup at a rate RDS will not survive. "We have a stored procedure estate" is a reason to stay on RDS or Aurora until they refactor.

Homogeneous migration stays on the engine (Oracle to RDS Oracle) and is simpler. Heterogeneous (Oracle to Aurora PostgreSQL) needs SCT plus DMS. SAP owns that detail. SAA needs to know the words.

## RDS

Multi-AZ instance: a synchronous standby in another AZ, one endpoint, automatic failover, the standby is not a read endpoint. Multi-AZ cluster (MySQL and PostgreSQL): a writer and two readable standbys. Read replicas: asynchronous, readable, you can promote them, they can be cross-Region, they are not automatic failover.

Backups: automated backups enable PITR inside the retention window. A snapshot is manual or copied. Encryption at create only. Parameter groups and option groups are the configuration. Enhanced Monitoring is the OS. Performance Insights is the SQL.

```bash
aws rds create-db-instance --db-instance-identifier orders --engine postgres \
  --db-instance-class db.m7g.large --allocated-storage 100 --storage-type gp3 \
  --master-username app --manage-master-user-password \
  --multi-az --backup-retention-period 7 \
  --vpc-security-group-ids "$SG" --db-subnet-group-name data \
  --no-publicly-accessible --storage-encrypted
aws rds create-db-instance-read-replica --db-instance-identifier orders-rr \
  --source-db-instance-identifier orders
```

`--manage-master-user-password` puts the master password in Secrets Manager. That is the current default you want.

RDS Proxy pools connections, makes failover less visible to the app, and supports IAM auth. Use it in front of Lambda. Do not put it in a diagram that has five long-lived EC2 connections and no pain.

IAM database authentication issues a short-lived token instead of a password for MySQL and PostgreSQL. The application still needs a database user mapped to the IAM role.

## Aurora

Storage is six copies across three AZs. The writer and the readers share that volume. Readers are for scale-out of reads and for failover targets. Failover is typically well under a minute. A cluster endpoint points at the writer. A reader endpoint load-balances readers. Custom endpoints split a reporting reader away from the interactive ones.

Aurora Serverless v2 scales in ACUs. It is the variable-load SQL answer. It is not DynamoDB. You still have connections, SQL, and a minimum ACU you pay for.

Aurora Global Database: one primary Region, up to five secondaries, typical lag under a second. Failover can be managed. Write forwarding lets a secondary send writes to the primary with extra latency. It is not DynamoDB-style multi-Region active writes.

Aurora multi-master is not the answer you reach for. Global Database or DynamoDB covers the stems people used to force into multi-master.

Backtrack rewinds a cluster to a time without a restore. Cloning is copy-on-write and is the fast way to get a test database. Zero-ETL to Redshift is the analytics path when the stem refuses a nightly DMS job.

## DynamoDB

| Concept | Fact |
| --- | --- |
| Partition key | High cardinality. A hot key throttles |
| Sort key | Range queries inside one partition |
| GSI | Different partition key. Its own capacity. Eventually consistent |
| LSI | Same partition key, different sort. Created with the table. Shares capacity |
| On-demand | Pay per request. Unknown or spiky traffic |
| Provisioned | Cheaper when steady. Auto scaling follows consumed capacity. It is not instant |
| Burst | Unused provisioned capacity is saved briefly and spent on spikes |
| DAX | Microsecond cache, API-compatible. Item cache and query cache. Not for strongly consistent reads you just wrote unless you design for it |
| TTL | Deletes expired items. Usually within days, not at the second of expiry. Not a backup |
| Streams | A change log. Lambda consumes it. The trigger for "when a row changes" |
| PITR | Continuous backup, 35 days |
| Global tables | Multi-Region, active-active, last-writer-wins. Not a transaction across Regions |
| Transactions | ACID across items in one Region, up to 100 items. More expensive |
| Conditional writes | Optimistic locking. The idempotency tool |

```bash
aws dynamodb create-table --table-name orders \
  --attribute-definitions AttributeName=pk,AttributeType=S AttributeName=sk,AttributeType=S \
  --key-schema AttributeName=pk,KeyType=HASH AttributeName=sk,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST
aws dynamodb update-continuous-backups --table-name orders \
  --point-in-time-recovery-specification PointInTimeRecoveryEnabled=true
```

A filter expression is applied after the read. It does not reduce RCUs. A `Query` with a key condition does. A `Scan` reads the table.

DynamoDB Accelerator versus ElastiCache: DAX speaks the DynamoDB API and is only a cache for DynamoDB. ElastiCache is a general cache and a place to put data structures DynamoDB does not have.

## The others, one paragraph each

DocumentDB is the Mongo-compatible managed service. Compatibility is not identity. A stem that says "MongoDB with a feature DocumentDB does not support" lands on MongoDB on EC2 or Amazon's current compatibility note. Check the docs before you promise aggregation features.

Neptune is the graph. Keyspaces is Cassandra without the nodes. OpenSearch is search and log analytics, and it is also the vector-search option some RAG designs use. Redshift is the warehouse. Redshift Serverless is the warehouse that should not run all night. Redshift RA3 with managed storage separates compute and data. Spectrum queries S3. Zero-ETL and streaming ingestion have reduced the number of stems whose answer is "DMS into Redshift," but DMS is still the heterogeneous migration tool.

Timestream is purpose-built time series. If it is not in the options, DynamoDB or a columnar store is the fallback you justify from the access pattern.

## Exercises

1. A catalog is 95% reads, needs SQL, and the writer is fine. Users are in one Region. What do you add?
2. The same catalog must survive a Region failure with RPO under 1 second and RTO under a minute, and the team will stay on PostgreSQL. What is the Aurora feature?
3. Shopping-cart lookups by cart id at a million requests per minute, no joins. RDS or DynamoDB?
4. A DynamoDB table uses `status` as the partition key. `OPEN` is hot. What do you change?
5. Lambda opens a new RDS connection per invoke and the database hits `max_connections`. What do you put in front, and what secret change do you make?
6. A global table and a strongly consistent read in the second Region immediately after a write in the first. Will the read see the write?

## Answers

1. An Aurora or RDS read replica, or an ElastiCache in front if the hot queries are cacheable. Multi-AZ does not add read capacity on a classic Multi-AZ instance.
2. Aurora Global Database. Promote the secondary on a Regional failure. Practice it.
3. DynamoDB on-demand or provisioned with a high-cardinality cart id key. RDS will become the connection and IOPS bottleneck first.
4. A partition key that includes a high-cardinality attribute (user id or cart id). Status can be a GSI if you truly must query all open carts, and that GSI may still be hot. A sparse index or a queue of open work is often the real design.
5. RDS Proxy, and store the password in Secrets Manager (or use IAM auth) so Lambda is not holding a static superuser password.
6. No. Global tables replicate asynchronously. A strongly consistent read is a same-Region DynamoDB read. Cross-Region is eventually consistent.

## RDS, the operations

Engines you will see: MySQL, PostgreSQL, MariaDB, Oracle, SQL Server. The engine is the one the team runs, unless a license or a feature forces a move. Oracle and SQL Server carry license-included or bring-your-own-license choices. A per-socket license that they already own can push the database onto EC2 on a Dedicated Host instead of RDS, when RDS cannot honor the license or a feature. That is a cost and a constraint answer, not a preference.

A DB subnet group in at least two AZs is required for Multi-AZ. `PubliclyAccessible` should be false. The security group allows the database port from the application security group only. The master password belongs in Secrets Manager, which RDS can rotate, or you use IAM database authentication for MySQL and PostgreSQL. A password in a Lambda environment variable is the developer bug.

| Deployment | Failover | Reads |
| --- | --- | --- |
| Single-AZ | You restore a snapshot. This is dev, or a stem that accepted downtime | The one instance |
| Multi-AZ instance | Synchronous standby in another AZ. Automatic. The endpoint does not change. The standby is not a read endpoint | Scale reads with a replica, not with the standby |
| Multi-AZ cluster (the newer cluster deployments) | A writer and readable standbys | Read the current docs if a stem offers readable standbys. Do not describe classic Multi-AZ as a reader |
| Read replica | You promote it yourself. It can be cross-Region. Replication is asynchronous, so there is lag | Yes. This is the read-scale and the manual DR copy |
| Snapshot restore | A new instance. RPO is the snapshot time. RTO is the restore time | You are down until it finishes |

Encryption is chosen when the instance is created. You cannot flip it on later. Snapshot, copy the snapshot with a KMS key, restore, cut over. Automated backups and snapshots inherit the encryption of the instance. Sharing an encrypted snapshot means sharing the key.

Parameter groups hold engine settings. Some parameters are static and wait for a reboot. Option groups attach engine options, more relevant on Oracle and SQL Server. A change that "did not apply" is often a static parameter and an instance that was never rebooted.

Storage autoscaling grows the disk. It does not shrink it. gp3 sets IOPS without growing the disk. A gp2 volume grown to 2 TB to buy IOPS is the cost item from the storage chapter, applied to the database.

RDS Proxy sits in front and holds a pool. Use it when Lambda or a large fleet opens too many connections, and when failover should be less visible to the app. It is not a query accelerator. It costs money. IAM auth through the proxy is a normal pattern. The Data API for Aurora is the HTTP alternative that does not use a persistent connection at all.

Maintenance windows and backup windows matter because a Multi-AZ failover during a patch is still a short blip, and a single-AZ patch is downtime. Automated backup retention of 0 disables point-in-time recovery. Retention longer than the policy is a bill.

## Aurora

The storage volume is replicated across three AZs in the Region. That is already in the product. You do not "turn on Multi-AZ" as a separate checkbox to get storage durability. Compute is separate. A writer instance and zero readers still has the storage. Failover is faster if a reader already exists, because Aurora promotes a reader. Add readers for read scale. The cluster endpoint goes to the writer. The reader endpoint load-balances readers. An instance endpoint pins one instance, which you use when you need a specific replica or the writer.

Aurora Serverless v2 scales in ACUs. It is the spiky or idle-at-night SQL database. A flat, high load is often cheaper on provisioned Aurora. Serverless is not a durability feature. It is a capacity feature.

Aurora Global Database is one writer Region and secondary Regions with typical lag under a second. You fail over by promoting a secondary. It is not multi-master. Write forwarding exists and has limits. Do not describe Global Database as DynamoDB global tables. A cross-Region RDS read replica is the non-Aurora version: more lag, you promote by hand, the endpoint changes.

Clones are copy-on-write. A test clone is fast and does not double the storage bill until the test writes. That is the "give me a production-sized test database without copying 10 TB" answer. Backtrack rewinds the cluster to a point in time without a full restore, within the backtrack window, for Aurora MySQL. It is not a second Region.

Aurora PostgreSQL and Aurora MySQL are compatible, not identical, to the community engines. An extension or a version the stem requires can force RDS or EC2. Read the constraint. "Aurora is faster" does not install an extension Aurora does not ship.

## DynamoDB

A table has a partition key and an optional sort key. The partition key decides the physical partition. A single partition is on the order of 3,000 read capacity units, 1,000 write capacity units, and about 10 GB. A table can be huge and still throttle if every write uses one key value. On-demand raises the table's ability to absorb bursts. It does not fix a hot key. Contributor Insights shows the hot key. The fix is a high-cardinality partition key.

Query uses the partition key and a condition on the sort key (`=`, `<`, `begins_with`). Scan reads items and then filters. The filter does not reduce RCUs. `begins_with` on the partition key is illegal.

A GSI is another partition-and-sort key, projected attributes, and its own throughput. Every write to the base item writes the index if the attributes are present. A sparse index omits items that lack the attribute, which is how "only OPEN orders" stays small. A GSI whose partition key is `STATUS#OPEN` is a second hot key. An LSI shares the base partition key and must be created with the table. LSIs are the rare answer. GSIs are the usual one.

Capacity. On-demand for unknown and spiky. Provisioned with auto scaling for flat and high. A transaction consumes more capacity than a plain write. `BatchWriteItem` is 25 items and is not atomic. `TransactWriteItems` is atomic, up to 100 actions, and is how you update two items or fail both. It is not a join and not a place to put a 10,000-row workflow.

Item size max is 400 KB. Larger attributes go to S3 and the item stores the key. TTL deletes expired items so you stop paying. It is not a compliance delete at a precise second.

Streams are an ordered log of changes, consumed by Lambda. They are how you replicate, search-index, or react. Iterator age means you are behind. Global tables use replication on top of this idea so other Regions can read and write. Replication is asynchronous. A strongly consistent read is same-Region only. Design for conflicts if both Regions write the same key, or do not use global tables.

DAX is a DynamoDB item cache. It speaks the DynamoDB API. It does not cache RDS. ElastiCache is the general cache. Point-in-time recovery is a DynamoDB feature you turn on. It is not on by default. On-demand backups are the manual snapshot.

Single-table design shows up as `pk` and `sk` values like `CUSTOMER#12` and `ORDER#99`. You should be able to point at an access pattern and name the key. You should not invent a join.

## Purpose-built, when the name is the answer

| Stem names | Engine | Refuse |
| --- | --- | --- |
| MongoDB API, documents | DocumentDB | DynamoDB, unless they will change the access pattern and the driver. DocumentDB is not a perfect MongoDB. A feature it does not support lands on MongoDB on EC2 or a compatibility check |
| Graph, traversals, relationships | Neptune | A pile of SQL self-joins at a depth the stem says is the problem |
| Cassandra, wide column | Keyspaces | Running Cassandra on EC2 unless they need a feature Keyspaces does not have |
| Search, logs, full text, a vector store for RAG | OpenSearch | A DynamoDB scan |
| Warehouse, columnar scans, BI | Redshift. Serverless if it should not run all night. RA3 if compute and storage should scale apart. Spectrum or Redshift queries on S3 for the lake | Aurora, which is the operational database |
| Time series at a scale they named | Timestream if it is in the options | DynamoDB with a time sort key if Timestream is not offered |
| Immutable ledger, cryptographically verifiable history | QLDB | An orders table. QLDB is not the default operational store |
| Cache | ElastiCache or MemoryDB | MemoryDB when the data must survive a node and still look like Redis. ElastiCache when it is a cache and loss of the cache is acceptable |
| Ledger plus a normal relational app | The relational app stays on Aurora. Do not move it to QLDB because the word "audit" appeared | |

DMS moves data. It is not a database. SCT converts schema. Homogeneous stays on the engine. Heterogeneous needs SCT and a test. Zero-ETL integrations have reduced some "DMS into Redshift" stems. DMS is still the answer for a one-time or ongoing heterogeneous copy the integration does not cover.

## Commands

```bash
aws rds create-db-instance \
  --db-instance-identifier app \
  --engine postgres \
  --db-instance-class db.m7g.large \
  --allocated-storage 100 \
  --storage-type gp3 --iops 12000 \
  --multi-az \
  --manage-master-user-password \
  --backup-retention-period 7 \
  --no-publicly-accessible \
  --vpc-security-group-ids "$SG"

aws rds create-db-snapshot --db-instance-identifier app --db-snapshot-identifier app-before
aws rds copy-db-snapshot --source-db-snapshot-identifier app-before \
  --target-db-snapshot-identifier app-encrypted --kms-key-id "$KEY"
aws rds create-db-instance-read-replica --db-instance-identifier app-ro \
  --source-db-instance-identifier app

aws rds create-db-proxy --db-proxy-name app --engine-family POSTGRESQL \
  --auth SecretArn="$SECRET",IAMAuth=REQUIRED --role-arn "$ROLE" \
  --vpc-subnet-ids "$A" "$B" --vpc-security-group-ids "$SG"

aws dynamodb update-continuous-backups --table-name orders \
  --point-in-time-recovery-specification PointInTimeRecoveryEnabled=true
aws dynamodb update-table --table-name orders \
  --global-secondary-index-updates file://gsi.json
```

Promoting a replica: `aws rds promote-read-replica`. It is irreversible in the sense that the replica becomes its own instance and stops replicating. You do this in a Regional failure, then repoint the application. Multi-AZ failover does not use this command.

## More exercises

7. Classic RDS Multi-AZ, CPU on the writer is high because of SELECT. Will sending reads to the standby work? What do you add?
8. Aurora with one writer and no readers. Storage is across three AZs. What fails when the writer instance dies, and what do you add so failover has a target?
9. A team wants an Aurora clone of production for a test that writes 10 GB. Why is a snapshot restore the slower and more expensive first move?
10. DynamoDB `TransactWriteItems` versus `BatchWriteItem` for two items that represent a payment and an order and must both land.
11. PITR was never enabled on the table. A bad job deleted items an hour ago. What can you restore to?
12. Oracle features SCT cannot convert, and the license is per socket and already owned. Which landing zone is honest?
13. The application reads its own write immediately after PUT, from a different AZ in the same Region, on DynamoDB. Which read consistency do you ask for?

## Answers

7. No. The classic standby is not a read endpoint. Add a read replica, or an Aurora reader, or a cache if the SELECT is the same query all day.
8. The storage is fine and the compute is gone until Aurora replaces the writer, which takes longer if there is no reader to promote. Add at least one reader in another AZ. This is still one Region. A Region failure needs Global Database or a backup strategy.
9. A clone is copy-on-write and is available quickly, and you pay for the 10 GB the test changes rather than a full stored copy from the start. A snapshot restore builds a new full copy. Clones are the test-environment answer. They are not the DR copy in another Region.
10. `TransactWriteItems`. The transaction commits both or neither. `BatchWriteItem` is a batch of independent writes. A partial failure can leave the payment without the order.
11. Only an on-demand backup you actually took, if you took one. PITR cannot be enabled after the fact for the hour you already lost. This is why PITR is part of the table creation checklist and not a restore-day decision.
12. RDS Oracle or Oracle on EC2 on a Dedicated Host, after you check which features RDS blocks. Aurora PostgreSQL is the answer only after the gap list is accepted. "Managed" does not compile a feature the conversion tool rejected.
13. `ConsistentRead=true` on the GetItem or Query, in that Region. The default is eventually consistent. A global table in another Region will not honor "I just wrote in this Region" as a strongly consistent cross-Region read.
