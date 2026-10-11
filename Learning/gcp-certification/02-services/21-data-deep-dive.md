# Storage, databases, and analytics deep dive

Read chapters 07, 08, and 09 first. This file is the behavior those chapters named but did not spell out.

## Cloud Storage behavior

Location types:

| Type | Failure it survives | Constraint |
| --- | --- | --- |
| Region | A zone, not the region | Use when compute is in that region and residency is one region |
| Dual-region | One of the two named regions | You pick the pair. Turbo replication is the fast RPO option on dual-region. |
| Multi-region | A region inside that continent area (`us`, `eu`, `asia`) | Not “every region on earth”. Geo-redundant inside the area. |

Storage class is a property of the object, not only of the bucket. The bucket default applies to new objects. Lifecycle moves existing ones.

| Class | Typical access | Minimum storage duration | Retrieval cost |
| --- | --- | --- | --- |
| Standard | Hot | None | None |
| Nearline | ≤ once a month | 30 days | Yes |
| Coldline | ≤ once a quarter | 90 days | Yes |
| Archive | ≤ once a year | 365 days | Yes. First byte is still milliseconds, not hours. |

Deleting or rewriting an object before the minimum duration still bills the rest of that duration. That is the trap in “move yesterday’s logs to Archive”.

Autoclass watches access and moves objects, including back to a hotter class. Use it when you cannot predict. Use a lifecycle rule when you can (logs older than 90 days are Coldline). Autoclass and a hand-written class-change lifecycle on the same objects fight. Pick one.

Other controls questions mix up:

| Control | Stops |
| --- | --- |
| Versioning | Permanent loss on overwrite or delete, by keeping generations |
| Lifecycle on noncurrent versions | Unbounded version cost |
| Retention policy | Delete until the period ends. Lock it so even admins cannot shorten it. |
| Event-based hold and temporary hold | Delete while the hold is on |
| Object versioning is not retention | A user with delete can still delete versions unless retention or a hold applies |
| Public access prevention | `allUsers` and `allAuthenticatedUsers` |
| Uniform bucket-level access | Object ACLs. IAM only. |
| CMEK | Google-managed key control. Does not stop a principal who has decrypt and object get. |
| Signed URL | Lack of an IAM binding for a time-limited caller. The URL is a bearer token. |
| Requester pays | The reader’s project pays egress. The bucket owner still pays storage. |

Soft delete keeps a deleted object for a recovery window you set. It is newer than versioning and easy to confuse with it. Versioning keeps history of overwrites while the object still exists as a live name. Soft delete helps after a delete. Retention forbids the delete. You can want more than one.

```bash
gcloud storage buckets update gs://BUCKET --soft-delete-duration=7d
gcloud storage buckets update gs://BUCKET --retention-period=31557600
# Lock is irreversible. Do it only when the stem says compliance.
gcloud storage buckets update gs://BUCKET --lock-retention-period
```

Parallel composite uploads speed large `cp`. They can break some source-generation preconditions. For a 1 GB object, a normal copy is fine.

Storage Transfer Service jobs have a schedule, a bandwidth cap, and delete behavior (do not delete destination objects unless you mean to mirror). Transfer Appliance is when the network cannot move the bytes in the window you have. A 10 Gbps link and a weekend can move a lot. Do the arithmetic before you ship hardware.

## Cloud SQL behavior

HA is a standby in another zone, same region, same data, automatic failover. The IP (private) stays. Connections drop and must retry. There is a short outage. That is 99.95% class for the regional configuration, which satisfies a 99.9% stem. It is not multi-region.

Read replicas serve reads and can be cross-region. They lag. Promoting a replica is a manual or API failover for disaster recovery, with the lag as your RPO. Do not call a replica “HA”.

| Backup | RPO | What it is for |
| --- | --- | --- |
| Automated backup plus PITR | A point inside the log window (often 7 days, configurable) | A bad deploy an hour ago |
| On-demand backup | The moment you took it | A milestone |
| SQL export to a bucket | Whenever the export finished | A portable dump, a different project |
| Disk snapshot of the data disk | Crash consistent unless you stop the database | The weak answer when Cloud SQL backups exist |

```bash
gcloud sql instances patch app-db \
  --backup-start-time=03:00 \
  --enable-point-in-time-recovery \
  --retained-transaction-log-days=7 \
  --maintenance-window-day=SUN \
  --maintenance-window-hour=4

gcloud sql instances clone app-db app-db-clone
gcloud sql instances promote-replica app-db-read
```

Flags you should recognize: `max_connections`, IAM database authentication, `slow_query` logging, Query Insights. Connection storms from Cloud Run are solved with a pool (a pooler sidecar or managed connection pooling where the engine has it) and with `max-instances` on Cloud Run, not with an infinite `max_connections`.

Private IP requires the service networking peering already in place. Authorized networks apply only to public IP. Adding `10.0.0.0/8` as an authorized network does not enable private IP.

Users: built-in users, or IAM users (`gcloud sql users create ada@example.com --instance=app-db --type=cloud_iam_user`). IAM auth still needs the Cloud SQL client role on the instance plus the database grant.

## AlloyDB and Spanner details

AlloyDB primary is read-write. Read pools scale read and columnar analytical scans. The columnar engine is why “transactions and heavy reports on the same Postgres” lands here instead of a replica you hope can keep up. Backups are cluster-level, with continuous backup for PITR. Private IP only in the serious design.

Spanner:

- Capacity is processing units. 1000 processing units is one node. You can run 100 processing units for a small database. Regional and multi-region configs have a minimum.
- Multi-region uses a witness region for quorums. You pay for that. Writes are strongly consistent across regions. That is the product.
- Hotspot: a monotonic key (`timestamp` first, or an incrementing integer) sends all new writes to one split. Fix the key with a high-cardinality prefix (customer, device) or a hash prefix.
- Interleaved tables put child rows with the parent row so a parent and its children share a split. Use it for a parent that is always read with its children.
- Stale reads (`exact staleness`) are cheaper and faster when the stem allows slightly old data. Strong reads are the default and the payment answer.
- PostgreSQL dialect versus GoogleSQL is a compatibility choice, not a consistency choice.

```bash
gcloud spanner instances create app \
  --config=regional-us-central1 \
  --processing-units=100

gcloud spanner databases ddl update appdb --instance=app --ddl="
CREATE TABLE Users (
  UserId STRING(36) NOT NULL,
  Name STRING(MAX)
) PRIMARY KEY (UserId);

CREATE TABLE Sessions (
  UserId STRING(36) NOT NULL,
  SessionId STRING(36) NOT NULL
) PRIMARY KEY (UserId, SessionId),
  INTERLEAVE IN PARENT Users ON DELETE CASCADE;"
```

## Firestore details

Mode is permanent: Native or Datastore. Native has realtime listeners and mobile security rules. Datastore mode has the older API and no realtime listeners.

A query that is not supported by an automatic single-field index needs a composite index. The error message contains the index to create. Collection-group queries look across all collections of that name and need a collection-group index.

Security rules are for client SDKs. They are not IAM. A backend with a service account uses IAM and bypasses rules. Leaving rules at `allow read, write: if true` is a public database for any client that has the project config.

TTL policies delete old documents. Exports to Cloud Storage are the portable backup. PITR covers a recent window. A scheduled export to another project is the “admin of this project deleted the database” answer.

```bash
gcloud firestore fields ttls update expireAt \
  --collection-group=sessions --enable-ttl
```

## Bigtable details

Data model: row key, column family, column qualifier, timestamped cells. You design column families few and stable. You design the row key first.

| Key | Result |
| --- | --- |
| `device#timestamp` | Writes for one device are ordered. Across devices they spread. Good. |
| `timestamp#device` | Every writer in the same second hits one tablet. Hotspot. Bad. |
| Reverse timestamp | Latest-first scans for one device. Fine if the device id is still first. |

Garbage collection on a column family drops old versions or old age. That is retention inside the row, not a backup.

Replication: multi-cluster instance. Single-cluster routing app profile sends a workload to one cluster (strong for that cluster). Multi-cluster routing fails over and is eventually consistent across clusters. Do not promise strong global reads on multi-cluster routing.

SSD unless the stem is huge, cold, and latency-tolerant (HDD). Production instances have more than one node. Scaling nodes is how you scale throughput. Schema design is how you avoid hotspots that more nodes will not fix.

## Memorystore details

| Tier | Failover |
| --- | --- |
| Basic | No replica. A maintenance event or failure drops the cache. |
| Standard | Replica and automatic failover. Still a cache. Do not be the only copy of orders. |

Redis AUTH and in-transit TLS exist. Turn them on when the stem says the cache holds session tokens. The instance has a private IP in the VPC. Cloud Run reaches it only with VPC egress. There is no public IP to “just enable”.

Valkey is the open-source fork path Memorystore also offers. Treat exam stems that say “Redis API” as Memorystore for Redis or Valkey. Memcached is a simpler cache with no persistence story.

## BigQuery design

On-demand bills bytes scanned. Editions bill slot-hours (Standard, Enterprise, Enterprise Plus) with optional commitments. Autoscaling reservations cover bursts. Baseline slots cover the steady dashboards.

A query scans a column from the rows it must read. Partition pruning stops it reading other days. Clustering sorts inside the partition so a filter on the cluster column reads fewer blocks. You can cluster up to four columns, in the order you filter.

| Partition | Use |
| --- | --- |
| Time-unit column (`DATE`, `TIMESTAMP`) | Events |
| Ingestion time | You do not trust the source timestamp |
| Integer range | A numeric key such as customer id buckets |

```sql
CREATE TABLE ops.events (
  event_date DATE NOT NULL,
  user_id INT64,
  kind STRING,
  payload STRING
)
PARTITION BY event_date
CLUSTER BY user_id, kind
OPTIONS (partition_expiration_days = 400);
```

`require_partition_filter` rejects queries that would scan the whole table. Turn it on for cost safety.

| Feature | Job |
| --- | --- |
| Authorized view | A view in another dataset. The user gets the view, not the base table. |
| Row access policy | Filter rows by IAM principal (`SESSION_USER`, group). |
| Column-level security via policy tags | Taxonomy in Data Catalog / Dataplex. Hide the PAN column. |
| Materialized view | Stored result of a query, maintained by BigQuery. Dashboard speed. |
| BI Engine | In-memory acceleration for Looker Studio and some SQL. |
| External table | File stays in Cloud Storage. You pay scans. No BigQuery storage features. |
| BigLake | Governed external tables, including open formats, with finer security. |
| Iceberg | Open table format so Spark and BigQuery share one table. |
| Time travel | Query the table as of a timestamp, default window measured in days, not years. |
| Table snapshot | A named point-in-time you keep longer than time travel. |
| Fail-safe | Google’s last-resort window after time travel. You cannot query it yourself as a feature you design around. |
| Streaming / Storage Write API | Row shows up quickly. A batch load is cheaper for files. |
| Scheduled query | SQL on a clock. Not a general orchestrator. |
| BigQuery ML | `CREATE MODEL`. Analysts, not a training cluster. |
| Analytics Hub | Share a dataset, including with another org, without a raw copy. |
| Omni | Query data that stays in AWS or Azure. |

Slots do not make a bad `SELECT *` cheap under on-demand, because on-demand is not slots. Under editions you can still waste slot time. Fix the SQL either way.

```sql
CREATE ROW ACCESS POLICY eu_only
ON ops.events
GRANT TO ("group:eu-analysts@example.com")
FILTER USING (STARTS_WITH(region, "eu"));
```

## Pub/Sub behavior

| Fact | Consequence |
| --- | --- |
| At-least-once | Consumers must be idempotent. Store the message id. |
| Ack deadline | If you do not ack in time, the message is redelivered. Extend the deadline for slow work. |
| Ordering key | Order per key, and only if ordering is enabled on the subscription. Head-of-line blocking: one stuck message in a key blocks that key. |
| Exactly-once | A subscription mode. Not the default. Do not design as if every topic has it. |
| Dead letter | After N failed deliveries, publish to another topic. Needs a service account that can publish and ack. |
| Seek / snapshot | Replay or skip a backlog. Not a year-long archive. |
| Retention | Days. Export to Cloud Storage or BigQuery for years. |
| Push | Pub/Sub calls HTTPS. The endpoint must return success quickly. |
| BigQuery subscription | No pull worker. Schema should match. |
| Cloud Storage subscription | Archive the stream as files. |

A fan-out is one topic and N subscriptions. A filter on a subscription drops messages that subscriber does not care about, so you do not need a topic per event type unless the producers must be isolated.

## Dataflow behavior

A streaming job runs until you drain or cancel it. Drain finishes in-flight work. Cancel stops. Update replaces the graph with a compatible job and keeps the state when the update is compatible. An incompatible change needs a new job name and a plan for the subscription backlog.

Windows the exam expects you to recognize:

| Window | Meaning |
| --- | --- |
| Fixed | Tumbling five-minute buckets |
| Sliding | Overlapping windows |
| Session | Gap-based, per key. User activity. |

Watermark is how late data is defined. Allowed lateness keeps late events. Side outputs capture the ones you still drop. You will not write Beam on the ACE exam. You will pick Dataflow over Dataproc when the stem says unified streaming and batch or an existing Beam pipeline.

Templates: `gs://dataflow-templates/...` for the standard ones. Flex templates when the pipeline is yours and must not compile on launch.

## Orchestration choice, restated with constraints

| Constraint | Product |
| --- | --- |
| DAG of Spark, SQL, and SFTP, team knows Airflow | Composer |
| Five Google API calls, retries, a callback | Workflows |
| Cron hit an HTTPS URL | Cloud Scheduler |
| Retry one URL with a rate cap | Cloud Tasks |
| Analysts click together a pipeline | Data Fusion |
| Only SQL, in git | Dataform |
| Database change stream into BigQuery | Datastream |
| Move the database engine | Database Migration Service |

Composer environments are not free. A single nightly SQL does not justify one.

## Exercises

1. An object was rewritten to Archive after 2 days. The lifecycle then deletes it at day 10. What do you still pay?
2. Cloud SQL failover happened. The application did not reconnect. Is the standby broken?
3. Spanner CPU is low on five nodes and one hotspot metric is high. What do you change first?
4. A BigQuery bill dropped after partitioning, then climbed again because Looker Studio queries omit the date. What table option?
5. Two subscribers must both see every order, but fraud only wants amount > 1000. Topics or filters?

### Answers

1. Archive’s remaining minimum duration (365 days from when it became Archive), plus the delete does not refund that. Early delete is the expensive mistake.
2. The standby promoted. Failover drops connections. The app must retry. That is normal, not a failed replica.
3. The row key. More nodes do not fix a single hot split.
4. `require_partition_filter=true`, and fix the dashboard to pass a date.
5. One topic. The billing subscription has no filter. The fraud subscription filters on the attribute. Both subscriptions still exist so both pipelines get a copy. A filter does not remove the message from other subscriptions.
