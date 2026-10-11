# Databases

ACE 2.2, 3.4, 4.4. PCA 1.3 and 2.2. Pick the model first, then the product.

## Decision

| Stem | Product |
| --- | --- |
| MySQL, PostgreSQL, or SQL Server, regional, lift with little rewrite, up to vertical scale and read replicas | Cloud SQL |
| PostgreSQL, needs much higher performance, HTAP (transactions plus analytics), or native vector search on Postgres | AlloyDB for PostgreSQL |
| Relational, horizontal writes, strong consistency, multi-region, 99.999% class | Spanner |
| Document, mobile or web sync, flexible schema | Firestore Native |
| Existing Datastore API | Firestore in Datastore mode |
| MongoDB-compatible | Firestore with MongoDB compatibility, when the stem wants a Google-managed Mongo-compatible API. If they must keep MongoDB server itself, that is a different migration conversation. |
| Huge throughput, time series, IoT, single-row key lookups, HBase | Bigtable |
| Cache, leaderboard in memory, session, sub-millisecond | Memorystore for Redis, Valkey, or Memcached |
| Warehouse, SQL analytics, not the checkout system of record | BigQuery (analytics chapter) |

Do not put analytics scans on Cloud SQL. Do not put the shopping-cart transaction on BigQuery. Do not pick Spanner only because it sounds more enterprise. Spanner costs more and the schema and transactions are not a free lift of SQL Server.

## Cloud SQL

Engines: MySQL, PostgreSQL, SQL Server. HA is a standby in another zone in the same region, automatic failover. That meets 99.9% style regional targets. It is not multi-region active-active. Read replicas scale reads and can sit in another region for read locality. They are not the HA mechanism.

Backups: automated backups and point-in-time recovery. On-demand backups. Export to a SQL dump in Cloud Storage when you need a portable file.

Private IP uses private services access. Public IP plus authorized networks is the weaker option. SSL is required in serious designs. IAM database authentication exists for MySQL and PostgreSQL and avoids shared database passwords.

```bash
gcloud sql instances create app-db \
  --database-version=POSTGRES_16 \
  --tier=db-custom-2-7680 \
  --region="$REGION" \
  --availability-type=REGIONAL \
  --storage-size=20GB \
  --storage-auto-increase \
  --network=projects/$PROJECT_ID/global/networks/prod \
  --no-assign-ip \
  --backup-start-time=03:00 \
  --enable-point-in-time-recovery \
  --database-flags=cloudsql.iam_authentication=on

gcloud sql databases create app --instance=app-db
gcloud sql users create appuser --instance=app-db --password='replace-me'

gcloud sql backups list --instance=app-db
gcloud sql backups create --instance=app-db
gcloud sql backups restore BACKUP_ID --restore-instance=app-db

gcloud sql export sql app-db gs://$PROJECT_ID-lake/sql/app.sql --database=app
gcloud sql import sql app-db gs://$PROJECT_ID-lake/sql/app.sql --database=app

# Read replica
gcloud sql instances create app-db-read \
  --master-instance-name=app-db --region="$REGION"

# Connect through the Auth proxy or from a VM in the peered network
gcloud sql connect app-db --user=appuser --database=app
```

Maintenance windows and deny periods are how you stop a failover-capable update at peak. Query Insights is the slow-query tool.

## AlloyDB

PostgreSQL-compatible, disaggregated storage, a columnar engine for analytical queries on the same data, and stronger performance than Cloud SQL for PostgreSQL on demanding workloads. Read pools scale analytics and read traffic. HA is built in.

Pick AlloyDB when the stem says PostgreSQL and either high throughput, mixed transactional and analytical queries, or vector embeddings in the database. Pick Cloud SQL when the stem says MySQL or SQL Server, or a small Postgres lift where cost matters more than AlloyDB’s performance.

```bash
gcloud alloydb clusters create app \
  --region="$REGION" \
  --password=replace-me \
  --network=projects/$PROJECT_ID/global/networks/prod

gcloud alloydb instances create primary \
  --cluster=app --region="$REGION" \
  --instance-type=PRIMARY --cpu-count=2

gcloud alloydb instances create reads \
  --cluster=app --region="$REGION" \
  --instance-type=READ_POOL --cpu-count=2 --read-pool-node-count=2

# Connect with the AlloyDB Auth Proxy or psql to the private IP
gcloud alloydb instances describe primary --cluster=app --region="$REGION"
```

Backups are cluster backups. Continuous backup supports point-in-time recovery. AlloyDB Omni is the downloadable engine for on-premises or other clouds. Mention it for hybrid Postgres. Do not confuse it with the managed cluster.

## Spanner

Globally distributed relational database. Strong consistency. Scale by adding nodes (processing units). Configurations: regional, dual-region, multi-region. Dialects: GoogleSQL and PostgreSQL.

Interleaved tables and careful primary keys avoid hotspots. You do not get every SQL Server feature. A lift that refuses to change the schema is Cloud SQL, not Spanner.

99.999% is the multi-region story. A regional Spanner is still Spanner, and it is still the wrong pick for a 20 GB MySQL app.

```bash
gcloud spanner instances create app \
  --config=regional-$REGION \
  --processing-units=100 \
  --description=app

gcloud spanner databases create appdb --instance=app \
  --database-dialect=POSTGRESQL

gcloud spanner databases ddl update appdb --instance=app \
  --ddl="CREATE TABLE orders (id bigint PRIMARY KEY, sku varchar(64));"

gcloud spanner databases execute-sql appdb --instance=app \
  --sql="SELECT * FROM orders LIMIT 10"

gcloud spanner backups create b1 --instance=app --database=appdb \
  --retention-period=12h --async
```

The emulator (PCA 5.2):

```bash
gcloud emulators spanner start
```

## Firestore

Native mode: documents in collections, realtime listeners, mobile SDKs. Datastore mode: the older server API. You choose the mode at database creation time. You do not switch it in place.

Queries are not SQL joins. You design indexes for the queries you will run. A missing composite index is a common operational failure.

```bash
gcloud firestore databases create --location="$REGION" --type=firestore-native

gcloud firestore indexes composite create \
  --collection-group=orders \
  --field-config=field-path=customer,order=ASCENDING \
  --field-config=field-path=created,order=DESCENDING

# Export and import are the backup path ACE mentions for Firestore
gcloud firestore export gs://$PROJECT_ID-lake/fs/$(date +%F)
gcloud firestore import gs://$PROJECT_ID-lake/fs/2026-10-11
```

Point-in-time recovery is a database setting on newer Firestore. Scheduled exports still matter for a copy in another project.

Security rules (Native, mobile) are not IAM. IAM controls who administers and who uses the API from a backend. Rules control client SDK access. Do not leave test rules open.

## Bigtable

Wide-column. Row key design is the whole exam. Put the changing part of the key so tablets spread. Time-series keys should not put a raw timestamp first or every write hits one tablet (hotspot).

SSD for most workloads. HDD only for huge cold scans where latency is acceptable. At least one cluster for dev. Production is a replicated instance across zones or regions. Replication is eventually consistent between clusters. Row-level single-cluster consistency is strong.

```bash
gcloud bigtable instances create iot \
  --cluster=iot-a --cluster-zone="${REGION}-a" \
  --cluster-storage-type=SSD --instance-type=PRODUCTION \
  --cluster-num-nodes=3

gcloud bigtable instances tables create events --instance=iot
cbt -instance=iot read events count=5
```

HBase-compatible. Use the emulator for tests. Backup is managed backups or Dataflow export. Bigtable is not a relational join engine.

## Memorystore

Redis and Valkey for data structures, persistence optional, replication. Redis Cluster when you need to shard. Memcached when you want a simple cache and can lose it. All of these are reached on private IP. No public IP is the design.

```bash
gcloud redis instances create cache \
  --size=1 --region="$REGION" --tier=STANDARD \
  --network=projects/$PROJECT_ID/global/networks/prod \
  --redis-version=redis_7_0

gcloud redis instances describe cache --region="$REGION"
```

Standard tier has a replica and failover. Basic tier does not. Sessions you can lose might be Basic. Sessions you cannot lose should be in a database, with Memorystore as a cache in front.

## Database Migration Service

Online or one-time migration into Cloud SQL, AlloyDB, or Spanner from MySQL, PostgreSQL, SQL Server, and Oracle (for the paths the product supports). It is the answer for “minimal downtime database migration”, not a CSV in a bucket.

```bash
gcloud database-migration migration-jobs list --region="$REGION"
```

Connection profiles and a continuous migration job are configured with the API or console because they contain source credentials. Know the product name and that it supports continuous replication then promotion.

## Database Center

Fleet inventory of database instances. Recognition for “what databases do we run”.

## Exercises

1. SQL Server 2019, one region, 2 TB, team will not change stored procedures. Which product?
2. PostgreSQL, both the checkout transactions and heavy analytical reports on the same data, plus pgvector-style embeddings. Which product?
3. Shopping cart must accept writes in the US and Europe with strong consistency. Which product and configuration?
4. Mobile app syncs per-user documents offline. Which product and mode?
5. 2 million vehicles send telemetry, keyed by device and time, huge write rate, rare updates to single keys. Which product, and what key mistake do you avoid?
6. ACE asks you to restore Cloud SQL to a point before a bad deploy. Which feature?

### Answers

1. Cloud SQL for SQL Server. Not Spanner.
2. AlloyDB. Cloud SQL for PostgreSQL if the stem also says “smallest cost, modest QPS”.
3. Spanner, multi-region configuration. Cloud SQL read replicas do not take strongly consistent writes in both regions.
4. Firestore Native mode.
5. Bigtable. Do not prefix the row key with a timestamp that makes every current write land on one tablet. Include the device id (or a hash) first.
6. Point-in-time recovery from automated backups, or a backup restore. A disk snapshot of the data disk is the weaker answer.
