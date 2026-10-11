# Analytics: Kinesis, Firehose, Glue, Athena, Lake Formation, Redshift, MSK

SAA 3.5. SAP 2.5 and 4.4. SAP-C03 adds the lakehouse (Iceberg), real-time plus batch, and Clean Rooms. DVA uses Kinesis and OpenSearch and, on C03, Firehose.

Official:

- https://docs.aws.amazon.com/streams/latest/dev/introduction.html
- https://docs.aws.amazon.com/firehose/latest/dev/what-is-this-service.html
- https://docs.aws.amazon.com/glue/latest/dg/what-is-glue.html
- https://docs.aws.amazon.com/athena/latest/ug/what-is.html
- https://docs.aws.amazon.com/lake-formation/latest/dg/what-is-lake-formation.html
- https://docs.aws.amazon.com/redshift/latest/mgmt/welcome.html
- https://docs.aws.amazon.com/msk/latest/developerguide/what-is-msk.html

## Pick the pipe

| Job | Service |
| --- | --- |
| Your code consumes, you need replay, you scale by shard | Kinesis Data Streams |
| Land a stream in S3, Redshift, OpenSearch, or HTTP, little code | Data Firehose |
| Kafka API, you already have producers | MSK or MSK Serverless |
| Crawl, ETL, catalog, jobs | Glue. Spark underneath |
| SQL on S3 | Athena |
| Who may query which column of the lake | Lake Formation on the Glue catalog |
| Dashboards | QuickSight. Out of scope for DVA. In scope for SAA and SAP |
| Warehouse | Redshift. RA3 separates compute and storage. Serverless when it should not run all night |
| Hadoop or Spark at cluster scale | EMR |
| Flink | Managed Service for Apache Flink |
| Video | Kinesis Video Streams. Recognize it |
| Two companies, joint query, no raw exchange | Clean Rooms |
| Open table format, updates, time travel | Apache Iceberg on S3, Glue catalog, Athena or EMR or Redshift Spectrum |

A shard has a write ceiling. When producers throttle, you add shards or you are on the wrong service. Iterator age means consumers are behind. Lambda event-source mapping plus `ReportBatchItemFailures` is the DVA half of this.

Firehose buffers and delivers. It is not a log you re-read for 24 hours. If you need both delivery and replay, put Streams in front and let Firehose read the stream, or retain the stream and also deliver.

## The lake

```text
Producers -> Kinesis or MSK -> Firehose -> S3 (raw)
  Glue job: CSV to Parquet or Iceberg, partitioned by date
  Glue Data Catalog
  Lake Formation permissions
  Athena for ad hoc, Redshift for the warehouse, QuickSight for the chart
```

Partition the prefix (`dt=2026-10-11`). Athena cost follows bytes scanned. CSV scans more than Parquet. A query without the partition column scans the world.

Lake Formation cross-account grants are the SAP-C03 "share the table, not a copy of the bucket" answer. A bucket policy that allows another account to `s3:GetObject` on the whole lake is the coarse version and fails a column-level stem.

## Commands

```bash
aws kinesis create-stream --stream-name orders --shard-count 2
aws firehose create-delivery-stream --delivery-stream-name orders-to-s3 --s3-destination-configuration file://dest.json
aws glue start-crawler --name orders
aws athena start-query-execution --query-string "SELECT count(*) FROM orders WHERE dt='2026-10-11'" --result-configuration OutputLocation=s3://results-BUCKET/
aws redshift-serverless create-workgroup --workgroup-name analytics --namespace-name analytics
```

## Exercises

1. Custom consumers, replay for six hours, then a copy in S3 for Athena. Which two services, in which order?
2. Athena bills jumped. The files are CSV and the queries do not filter a date. What do you change in the data, not in the workgroup size?
3. The stem says Kafka. Kinesis or MSK?
4. A partner must aggregate totals with you and must not receive your rows. Clean Rooms or a shared bucket?

## Answers

1. Kinesis Data Streams, consumed by your code, with Firehose or a consumer writing S3. Streams give the replay. S3 plus Athena is the query.
2. Convert to Parquet or ORC, partition by date, and make the query use the partition. A bigger workgroup hides the scan.
3. MSK. Kinesis is the answer when they do not need the Kafka API.
4. Clean Rooms. A shared bucket gives them the rows.

## Streams

Kinesis Data Streams is a durable ordered log per shard. Producers put records. Consumers read at their own pace. Retention is the replay window, from the default of a day up to a long retention you pay for. A shard has a write ceiling and a read ceiling. If producers are throttled, you need more shards or a better partition key. A hot partition key lands on one shard the way a hot DynamoDB key lands on one partition.

Enhanced fan-out gives each consumer its own read throughput. Without it, consumers share the shard's read budget. A poison record blocks a shard until you skip it, bisect the batch, or the retention expires. Iterator age is the "consumers are behind" metric. Lambda event-source mappings are the usual consumer on these exams. A Kinesis Data Analytics or Managed Flink application is the stream processor when the stem wants SQL or Flink on the stream rather than a Lambda.

Data Firehose delivers to S3, Redshift, OpenSearch, or HTTP. It buffers by size or time. It can run a Lambda transform. It is not a log you rewind and consume with your own code. If the stem says replay and a custom consumer, the answer is Data Streams, and Firehose can still be one consumer that lands a copy in S3.

MSK is Kafka. Use it when the client is already a Kafka client. Do not migrate them to Kinesis for taste, and do not stand up MSK when they have no Kafka requirement. MSK Connect and MSK Serverless show up as the "less cluster work" versions. The decision is still the API.

## Lake, query, warehouse

Glue crawlers fill the Data Catalog. Glue jobs transform. Bookmarks stop a job from reprocessing old files. Convert CSV and JSON to Parquet or ORC, partition by the column queries filter on (`dt=2026-10-11`), and compress. That layout is the Athena performance feature. A bigger workgroup is how you pay to scan the world again.

Athena is SQL on S3, charged by bytes scanned. Partition projection or a catalog that matches the layout lets the query skip files. Workgroups isolate query results and limits. Lake Formation sits on the catalog and grants table and column permissions, including cross-account, which a bucket policy cannot express cleanly. The bucket policy is still the door to the objects. Both exist.

EMR is Spark and Hadoop when the job needs a cluster. Glue is the serverless ETL alternative when they do not want nodes. Do not answer EMR for a daily partition compaction Glue can run, or Glue for a workload that needs a long-lived cluster and a specific Hadoop tool.

Redshift is the columnar warehouse. RA3 separates compute and managed storage. Serverless is the warehouse that should not run all night. A sort key matches the filter. A distribution key matches the join. Spectrum and Redshift reading S3 query the lake without loading every file. Concurrency scaling and materialized views are the "the dashboard is slow at 9 a.m." tools. Zero-ETL and streaming ingestion have reduced some DMS-into-Redshift stems. DMS remains the heterogeneous copy.

QuickSight is the business dashboard. CloudWatch dashboards are the operations view. OpenSearch is search and log analytics, not the warehouse.

Clean Rooms is two parties computing on combined data without exchanging raw rows. A shared bucket is the opposite. Data Exchange is a catalog of third-party data sets. It is not your lake.

## More exercises

5. Producers are throttled. One shard shows all the writes. What do you change besides "add ten shards"?
6. Firehose is landing objects, and a developer wants to rewind six hours and reprocess in a Lambda. Why is that the wrong tool?
7. A Glue job reprocesses every file every night and the bill tripled. What feature stops that?
8. Analysts query `WHERE dt = '2026-10-11'` and Athena still scans the whole bucket. The files are Parquet. What is wrong with the layout?
9. Two companies need a joint aggregate. One of them proposes cross-account read on the raw bucket. What do you propose instead, and when would the bucket share be right?

## Answers

5. The partition key. Extra shards do not help if every record hashes to the same shard. Spread the key, then add shards if the aggregate write rate still exceeds one shard.
6. Firehose has already delivered and does not keep a consumer cursor you rewind. Put Data Streams in front with six hours of retention, and let Firehose be the S3 delivery if you still want the files.
7. Job bookmarks, and a source layout that can express "already processed." Without bookmarks, every run is a full scan of the prefix.
8. The path is not actually partitioned by `dt`, or the table is not partitioned and Athena has no way to skip files. Parquet helps inside a file. Partitioning decides which files are opened. Both are required for that query.
9. Clean Rooms for the joint aggregate. Share the bucket only when the other company is allowed to see the rows. "Aggregate" and "must not receive the rows" are the Clean Rooms sentence.
