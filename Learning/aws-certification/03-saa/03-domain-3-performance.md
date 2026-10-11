# SAA-C03 Domain 3 — Design high-performing architectures (24%)

About 12 of the 50 scored items. The stem has a number or a word that stands in for one: milliseconds, millions of requests, 20,000 IOPS, a shared POSIX tree, UDP, replay the last six hours. Pick the option that meets the number. The fastest option loses when a cheaper one also meets the number and the stem said "most cost-effective," but that item is Domain 4. Here the constraint is the number. Do not under-build it.

Tasks 3.1 through 3.5. Storage, compute, database, network, and ingestion are separate tasks and they show up as separate chapters in `02-services/`. This file is the choice.

## Task 3.1 — Storage

Name the access before you name the product. Object, block, or file. Then durability and the performance number.

| Access | Service | Configuration that matters |
| --- | --- | --- |
| Put and get by key, any size, durable, many readers | S3 Standard | Multipart upload above a few hundred megabytes, and required as you approach 5 GB. Parallel GETs. Prefixes scale. Transfer Acceleration when the upload crosses a long internet path and speed matters more than the per-GB price |
| One instance, a database or a filesystem on one machine | EBS | gp3: you set IOPS and throughput without growing the disk. io2 or io2 Block Express when the IOPS number is high and they name durability of the volume. gp2 makes you grow capacity to buy IOPS. That is the old trap |
| Scratch, high IOPS, the data can vanish with the instance | Instance store | The durable copy is in S3 or on EBS. Instance store does not survive stop, and it does not survive every restart story. Do not put the only copy there |
| Many Linux instances, one POSIX tree, a mount | EFS | General Purpose for latency. One mount target per AZ. Elastic throughput unless they have a known baseline. Max I/O mode is the old "high parallel, higher latency" knob. Do not put a database on EFS |
| SMB, Windows ACLs, Active Directory | FSx for Windows File Server | Multi-AZ when the share itself must survive an AZ. SSD versus HDD is a performance versus cost choice |
| HPC, training jobs reading the same dataset very fast | FSx for Lustre, usually linked to S3 | The dataset lives in S3. Lustre is the scratch performance in front of it |
| NetApp features, SnapMirror, multi-protocol | FSx for NetApp ONTAP | The team already speaks NetApp. It is not the default file share |
| OpenZFS | FSx for OpenZFS | When they name ZFS. Otherwise EFS or ONTAP |
| On-premises NFS or SMB that should land in S3 | Storage Gateway, File Gateway | DataSync when the job is a copy, not an ongoing mount. Transfer Family when the protocol is SFTP, FTPS, or FTP |
| Petabytes, the link would take more than about a week | Snow Family | Snowcone for the small ship, Snowball for the usual ship, Snowmobile is the truck and almost never the answer. DataSync if the network is actually fast enough |

S3 does not become faster because you bought a bigger bucket. It becomes faster because the clients request in parallel. A single-threaded 200 GB upload is the slow design. Multipart fixes the upload. CloudFront fixes the repeated download when the bytes are cacheable.

EBS is one AZ. "High performance Multi-AZ disk" is not a feature you check on a volume. You snapshot and restore in another AZ, or you stop using a single volume as the sharing mechanism and move to a database or to S3.

EFS burstable throughput surprises people the same way T-instance CPU credits do. A workload that is hot all day exhausts burst credits and then looks "randomly slow." Provisioned or elastic throughput is the fix. The exam's current default recommendation for unknown throughput is elastic.

## Task 3.2 — Compute

Scale the tier that is saturated. A bigger load balancer does nothing for a database that is out of connections. A bigger database does nothing for an app that is waiting on one unindexed query, but that second sentence is harder to see on this exam. They will tell you the metric.

### Families

| Family | You recognize it as | The incident |
| --- | --- | --- |
| M | General, balanced | The default when they did not name a bottleneck |
| C | Compute | High CPU, not a memory footprint |
| R | Memory | A cache, an in-memory database, a JVM that needs the heap |
| T | Burstable | Fine for a dev box and a spiky low-duty app. A T instance that runs hot all day exhausts CPU credits and becomes the performance incident. Move it to M or C |
| I, D | Storage local to the host | When they name local NVMe or dense disk and accept the instance-store story |
| G, P, Inf, Trn | GPU and machine learning accelerators | The training or graphics stem. Not a web fleet |
| Mac | macOS builds | When they name macOS. Rare |

Graviton (g suffix, such as `m7g`) is the price-performance move when the software runs on ARM. It is not a different architecture decision. A Standard Reserved Instance bought for `m5` does not discount `m7g`. That fact is Domain 4, and it shows up here when someone "upgraded" and the performance changed because they also changed architecture without testing.

### Scaling

| Tier | Metric |
| --- | --- |
| Web behind an ALB | `ALBRequestCountPerTarget`, or target response time. CPU only if you have seen CPU saturate |
| Queue consumer | SQS `ApproximateNumberOfMessagesVisible`, often with a target per task. CPU of an idle long-poller stays low while the queue grows |
| Lambda | Memory is the CPU dial. More memory adds CPU until the duration stops falling. Then stop. Timeout is a separate setting and does not make the function faster. Reserved concurrency protects a downstream. Provisioned concurrency removes cold start when the SLO applies to the first request |
| A mixed fleet | A mixed-instances policy. On-Demand or a Savings Plan for the base. Spot for the interruptible share. The app must tolerate interruption |

| Signal | Choice |
| --- | --- |
| Short request, under 15 minutes, scales to zero | Lambda. If it needs a full web server, a long connection, or a GPU, it is the wrong box |
| Container, you do not want to run nodes | ECS on Fargate |
| Kubernetes is a requirement, not a preference you invented | EKS |
| You must control the host | EC2, or ECS and EKS on EC2 |
| Hours-long batch, a queue | AWS Batch |
| Spark | EMR |
| First request after idle must be fast | Provisioned concurrency, or a minimum task count above zero |
| The work is a platform the team will not cluster | Elastic Beanstalk |

Lambda's 15-minute limit and API Gateway's 29-second integration limit are performance designs, not just quotas. A two-minute report cannot be a synchronous API call. It is a queue, a 202, and a worker. Raising Lambda memory does not stretch the 29-second front door.

Placement groups: cluster for the lowest latency between instances in one AZ, spread for a small number of critical instances that must not share hardware, partition for a large distributed system such as HDFS. These are rare Associate items. The common item is "put the instances in more than one AZ," which is the opposite of a cluster placement group. Do not pick a cluster placement group for a highly available web tier.

## Task 3.3 — Databases

Pick from the access pattern, not from the product you like.

| Access | Engine | The feature that answers the number |
| --- | --- | --- |
| SQL, joins, one Region, moderate rate | RDS Multi-AZ | The right instance family. R for memory. Provisioned IOPS (io1 or gp3 on the storage) when they name an IOPS figure the baseline disk will not deliver |
| SQL, higher rate, fast failover, readers, MySQL or PostgreSQL compatible | Aurora | Add readers. The reader endpoint load-balances reads. Aurora Serverless v2 when the load moves during the day and they want ACUs instead of a size they must guess |
| SQL reads are the bottleneck and the writes are fine | A read replica, or Aurora readers | The replica is asynchronous. A read-after-write bug is not fixed by sending the user to a replica. Send that read to the writer, or use a consistent read where the engine has one |
| Key lookup, no joins, extreme rate, single-digit milliseconds | DynamoDB | A key that matches the query. On-demand while the traffic is unknown. Provisioned plus auto scaling when it is flat. DAX when the same GetItem is hot enough that even DynamoDB latency or cost is the complaint |
| The hot SQL rows, sessions, leaderboards | ElastiCache | Redis OSS or Valkey when you need replication, structures, or pub/sub. Memcached when you need a simple cache that can add nodes and you accept the simpler availability story |
| Documents, MongoDB-compatible | DocumentDB | When they name that model. Not a default for "JSON in a column" |
| Graph | Neptune | When the query is a relationship, not a join they could write in SQL |
| Cassandra-compatible | Keyspaces | When they name Cassandra or a wide-column access pattern |
| Columnar scans, a warehouse | Redshift | Not Aurora. Aurora is the operational database. Redshift is the scan |
| Search, logs, full text | OpenSearch Service | Not a DynamoDB scan, and not CloudWatch Logs Insights if they asked for a product search feature |
| Time series | Timestream when the stem offers it. The SAA in-scope list does not feature it the way SAP does | DynamoDB or a purpose-built option that is actually in the stem. Do not invent Timestream as the only right answer if it is not offered |

### DynamoDB, because the performance item is usually the key

A query uses the partition key and, optionally, a condition on the sort key. A scan reads items and then applies a filter. The filter does not reduce read capacity. A "we added a filter so the scan is cheap" design is the wrong answer on this domain and on the developer exam.

A partition is on the order of 3,000 read capacity units and 1,000 write capacity units. A table can be enormous and still throttle if every write uses `TENANT#acme`. Put a high-cardinality value in the partition key. If you must query by tenant, that value can be a GSI key, and you then have to watch whether that GSI key is also hot.

DAX is an item cache in front of DynamoDB. It is not ElastiCache, and it does not help a query pattern DAX does not serve. ElastiCache is the cache in front of RDS or in front of anything you write the cache logic for.

### RDS performance moves that are not a new engine

- A reader for read-heavy SQL, before a larger writer, when the reads can be slightly stale.
- gp3 or provisioned IOPS when the disk queue is the metric, not the CPU.
- RDS Proxy when the symptom is too many connections, especially from Lambda. The proxy does not make a slow query fast.
- An index. The exam rarely shows SQL. When it says the query scans the whole table, the answer is the access pattern or a cache, not a bigger class.
- Parameter groups and a reboot are the operational version of "the setting did not apply." Know that some parameters are static.

Homogeneous migration stays on the same engine and is the smaller project. Heterogeneous migration needs schema conversion. DMS copies data. The AWS Schema Conversion Tool is the schema tool, and it is emphasized more on Professional. On SAA, DMS is the data mover, and a heterogeneous move is the bigger project. Neither is a performance feature of the database you already have.

## Task 3.4 — Network

### Load balancers

| Balancer | You pick it when |
| --- | --- |
| ALB | HTTP, HTTPS, gRPC, WebSocket, path and host rules, Lambda targets, authenticate the user at the listener with Cognito, one balancer for many applications |
| NLB | TCP or UDP, a static IP, PrivateLink in front of your own service, very high packet rates, TLS passthrough |
| Gateway Load Balancer | You are inserting a fleet of firewall appliances. GENEVE. Not application routing |

An ALB needs at least two subnets in two AZs. That is a resilience fact that shows up in performance questions as "the balancer cannot be created in one subnet." Cross-zone load balancing changes whether an AZ with more targets gets more traffic. Turn it on unless you have a reason to keep traffic inside the AZ to avoid cross-AZ charges. That reason is a cost stem.

### CloudFront and Global Accelerator

| | CloudFront | Global Accelerator |
| --- | --- | --- |
| Protocol | HTTP and HTTPS | TCP and UDP, and HTTP |
| Cache | Yes. This is why a global news site's images belong here | No. It does not store your objects |
| Addresses | The distribution's DNS name | Two static anycast IP addresses |
| Failover | Origin groups, for HTTP origins | Shifts traffic between Regional endpoints in seconds |
| Typical stem | Static assets, video, an API whose GET is cacheable, WAF at the edge | Gaming, IoT, UDP, non-cacheable traffic, static IPs, fast Regional failover |
| Certificate | ACM in `us-east-1` | The Regional endpoints keep their own certificates |

If the stem says the body is unique per user and caching is useless, CloudFront is only a network path and WAF attachment, and Global Accelerator is the product built for the non-cached failover story. If the stem says the same image is fetched all day worldwide, CloudFront. People swap them because both are "global."

### Topology

| Topology | When |
| --- | --- |
| Two VPCs, no plan to grow, CIDRs do not overlap | VPC peering. Not transitive |
| Many VPCs, or a need to grow, or on-premises as well | Transit Gateway. Attachments have a cost, which Domain 4 will ask about |
| Overlapping CIDRs | Peering will not form. Private NAT, or renumber. Renumbering is the clean design and the one they often cannot do during an acquisition |
| S3 or DynamoDB from a VPC, and the path is the bottleneck or the NAT is the cost | Gateway endpoint |
| One service published to other VPCs | PrivateLink |
| Users close to a Region | Put the workload in that Region |
| A millisecond target the Region cannot meet because the users are in one city | Local Zone, or Wavelength for the 5G edge story. These are not the default. The default is the nearest Region |
| Data must stay in a country | The Region or Local Zone that satisfies the residency rule, even if another Region is closer. Residency beats latency |

Direct Connect is the performance and stability answer for a large, steady flow to a data center. A VPN is encrypted internet and is what you use until the circuit exists, and as the backup after it exists. VPN over Direct Connect is the encryption-on-the-circuit design. Do not answer Direct Connect for a team of ten people who need access next week.

Route 53 latency routing sends the user to the lowest-latency healthy Region. It is not a cache. Failover routing is the active-passive switch. Geolocation is for content that must differ by country, which is often a residency or a licensing rule, not a performance rule. Geoproximity is the version you bias with a number.

## Task 3.5 — Ingestion and transformation

| Shape | Service | The limit that decides it |
| --- | --- | --- |
| Many small events, your own consumers, you must replay | Kinesis Data Streams | Retention is the replay window. Shards are the throughput unit. A poison record blocks a shard unless you isolate it |
| Land a stream in S3, Redshift, OpenSearch, or HTTP, little code | Data Firehose | It buffers and delivers. It is not the log you re-read yourself. Lambda transform inside Firehose is for small conversions |
| Kafka API, the client is already a Kafka client | MSK | Do not rewrite them onto Kinesis unless the stem allows it |
| Crawl, convert, catalog | Glue | CSV to Parquet or ORC, partition by date or another filter column. The crawler fills the catalog. The job does the conversion |
| SQL on the lake | Athena | Columnar formats and partitions, or you pay to scan the world. A bigger workgroup is the expensive way to avoid the format change |
| Permissions on tables, columns, not just the bucket | Lake Formation | On top of the Glue catalog. A bucket policy is the coarse door. Lake Formation is the catalog door |
| Charts for business users | QuickSight | Not CloudWatch dashboards, which are the operations view |
| Spark at cluster scale | EMR | Glue for Spark is the serverless ETL alternative when they do not want a cluster to run |
| Copy a filesystem or an object store in | DataSync | Online. Agents at the source |
| Ongoing file share in front of S3 | Storage Gateway File Gateway | Different from a one-time DataSync task |
| Petabytes and a slow link | Snow | Then DataSync or a direct load once the device arrives |
| A database, continuously, into AWS | DMS | Performance of the source and the replication instance matters. It is not a file copy |

Secure the bucket the data lands in. A fast public bucket fails Domain 1. KMS, a bucket policy, Block Public Access, and a VPC endpoint for the collectors that live in a VPC.

Partitioning is the performance feature of a data lake. `s3://lake/orders/year=2026/month=10/` lets Athena skip other months. A single prefix with every file named by a GUID makes every query a full scan. Glue can write that layout. You can also write it yourself. The exam wants the layout, not a brand name.

Kinesis versus SQS: Kinesis keeps an ordered stream per shard and many consumers can read it. SQS is a queue where a message is consumed by one worker. If the stem says replay and multiple independent consumers on the same ordered log, Kinesis. If the stem says a buffer of work, SQS. Firehose is the delivery stream. People pick Firehose when they needed replay, because the names are adjacent.

## Worked scenarios

**1.** A global news site serves the same images all day. CloudFront, S3 origin, a cache policy with a long TTL, origin access control so the bucket is not public. Global Accelerator does not cache. A bigger EC2 origin does not help once the cache is warm, and it is the wrong place to serve the bytes from.

**2.** A game server uses UDP and must fail over between Regions quickly. Global Accelerator in front of NLBs. CloudFront does not do UDP. An ALB does not do UDP.

**3.** Athena scans 40 TB of CSV every morning. Convert to Parquet with Glue, partition by the column the query filters on, compress. Then set the workgroup. A bigger workgroup without the format change keeps the scan expensive and slow.

**4.** The API is 40 ms except the product page, which hits RDS with the same query all day. ElastiCache in front of that query. A read replica helps if the SQL varies and is not cacheable. A bigger writer helps if the writer CPU is the graph you were shown. The stem usually says the query is repeated. That is the cache.

**5.** Lambda duration falls from 128 MB to 1024 MB and stops falling after that. Set 1024 MB. You were buying CPU. Leaving it at 2048 MB buys nothing on this function and shows up as a cost item.

**6.** A T3 web tier is slow every afternoon and fine in the morning. CPU credit balance is exhausted. Move the fleet to M or C, or spread the load so the burst is real. Buying a bigger T instance postpones the same incident.

**7.** gp2, 200 GB, the database needs 12,000 IOPS. gp2 gives 3 IOPS per GB, so 200 GB is 600 IOPS, and you would have to grow the disk to buy the IOPS. gp3 lets you set 12,000 IOPS on the 200 GB volume. io2 is the answer if they also named the highest durability and a sustained IOPS figure gp3 will not sign up for.

**8.** One DynamoDB partition key, `STATUS#OPEN`, every order. The table metric looks fine and one partition throttles. Write a high-cardinality key. Query open orders through a design that does not put every writer on one key, or accept a GSI and shard that key if you truly must list them all.

**9.** A video job can be rewritten. Today it reads a shared EFS tree with one thread. S3 and parallel GET will go faster. EFS remains the answer if they cannot change the job and need the POSIX mount.

**10.** Users in one city need under 10 ms to a workload the nearest Region cannot deliver. A Local Zone in that city, if one exists, or Outposts if the workload must sit in their building. Do not add a CloudFront cache for a dynamic non-cacheable protocol and call it the same thing.

## Exercise set

1. gp2 versus gp3 for 12,000 IOPS and 200 GB.
2. CloudFront versus Global Accelerator for a REST API with a unique body per user and fast failover to another Region. Caching is useless.
3. Kinesis Data Streams versus Data Firehose when custom code must reprocess the last six hours.
4. The partition key `TENANT#acme` takes every order for the largest customer. What symptom, and what key change?
5. EFS or S3 for a video job that can GET objects in parallel.
6. Memcached or Redis (Valkey) for a leaderboard that must survive a node failure.
7. ALB or NLB in front of a service you will publish with PrivateLink.
8. Why does a cluster placement group fight a Multi-AZ web tier?
9. Athena is slow and the files are JSON, one prefix, no partitions. Name two changes that are not "a bigger workgroup."
10. A Lambda function behind API Gateway must generate a PDF that takes two minutes. What do you change in the architecture, not in the memory setting?
11. Read replica or Multi-AZ: the dashboard team runs heavy SELECT statements and must not slow the checkout writes.
12. DAX or ElastiCache: the hot operation is DynamoDB `GetItem` on the same keys.
13. DataSync or Snowball: 80 TB, a 100 Mbps link that is free at night, and a two-day deadline.
14. Transfer Acceleration or a Direct Connect: users around the world upload large objects to S3 once a day, and there is no data center circuit.
15. RDS Proxy or a larger RDS instance: Lambda concurrency was raised and the database is failing with "too many connections," CPU is low.

## Answers

1. gp3. You set the IOPS independently of size. gp2 would force you to buy capacity you do not need so that the included IOPS rise.
2. Global Accelerator. The stem removed the cache and asked for fast Regional failover. CloudFront is still an HTTP edge, and it is the wrong primary answer once caching is useless and the failover speed is the point. If both appear, prefer Accelerator for that sentence.
3. Kinesis Data Streams, with retention of at least six hours. Firehose delivers onward. It is not the stream you rewind and consume again with your own code.
4. That partition throttles while the table still has unused capacity. Include a high-cardinality value, such as the order id, in the partition key. Put the tenant where you can still query it, often a GSI, and do not make the GSI key a single hot value either.
5. S3. Parallel GET is the point of object storage. EFS is the answer when they need a shared POSIX mount and will not change the job.
6. Redis or Valkey, with replication. Memcached's sharding model is a simple cache. A leaderboard that must survive a node is the replication and data-structure case.
7. NLB. PrivateLink uses a Network Load Balancer as the service's front end. An ALB is not the PrivateLink producer.
8. A cluster placement group packs instances into one AZ for low latency between them. A Multi-AZ web tier must be in at least two AZs. You cannot have both for the same instances. Low-latency mesh inside one AZ is a different system, often a data or HPC tier, and it needs its own AZ-failure story.
9. Convert to Parquet or ORC, and partition by the column the WHERE clause uses. Both cut the bytes Athena scans. Compression helps. A bigger workgroup does not fix the layout.
10. Accept the request, put the job on a queue or start a Step Functions execution, return 202, and let a worker build the PDF. API Gateway will not wait two minutes. The Lambda timeout is not the limit that fires first.
11. A read replica, or an Aurora reader. Multi-AZ is a standby for failover, not a place to send the dashboard.
12. DAX. It is the DynamoDB item cache. ElastiCache is what you use when the data is not a DynamoDB item cache, or when DAX does not fit the API you are calling.
13. Snowball, or another Snow device that can hold 80 TB. 80 TB on 100 Mbps is on the order of weeks even if you ignore overhead (80 terabytes is hundreds of terabits; at 100 megabits per second you are past a week). The two-day deadline makes the network path impossible. DataSync is the answer when the link can finish inside the deadline.
14. Transfer Acceleration. It uses the CloudFront edge network for the upload to S3. Direct Connect needs a circuit from a data center you were not given.
15. RDS Proxy. The symptom is connection count, not CPU. A larger instance may raise `max_connections` and still fall over the next time concurrency doubles. The proxy pools them. Also cap the Lambda reserved concurrency so it cannot outrun the pool you sized.
