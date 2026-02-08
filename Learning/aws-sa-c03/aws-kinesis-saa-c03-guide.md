# Amazon Kinesis - SAA-C03 Comprehensive Guide

## Table of Contents
1. [Overview and Introduction](#overview-and-introduction)
2. [Kinesis Data Streams](#kinesis-data-streams)
3. [Kinesis Data Firehose](#kinesis-data-firehose)
4. [Kinesis Data Analytics](#kinesis-data-analytics)
5. [Kinesis Video Streams](#kinesis-video-streams)
6. [Kinesis Services Comparison](#kinesis-services-comparison)
7. [Data Producers](#data-producers)
8. [Data Consumers](#data-consumers)
9. [Security](#security)
10. [Monitoring and Performance](#monitoring-and-performance)
11. [Scaling and Capacity](#scaling-and-capacity)
12. [Cost Optimization](#cost-optimization)
13. [Best Practices](#best-practices)
14. [Common Architectures](#common-architectures)
15. [SAA-C03 Exam Tips](#saa-c03-exam-tips)
16. [AWS CLI Commands Reference](#aws-cli-commands-reference)
17. [Practice Questions](#practice-questions)

---

## Overview and Introduction

### What is Amazon Kinesis?

Amazon Kinesis is a platform for streaming data on AWS, offering powerful services to collect, process, and analyze real-time, streaming data. Kinesis enables you to build applications that can react to data as it arrives.

### Kinesis Services Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Amazon Kinesis Platform                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐    ┌──────────────────┐                   │
│  │  Kinesis Data    │    │  Kinesis Data    │                   │
│  │    Streams       │    │    Firehose      │                   │
│  │                  │    │                  │                   │
│  │ Real-time data   │    │ Load streaming   │                   │
│  │ streaming        │    │ data to          │                   │
│  │ & processing     │    │ destinations     │                   │
│  └──────────────────┘    └──────────────────┘                   │
│                                                                  │
│  ┌──────────────────┐    ┌──────────────────┐                   │
│  │  Kinesis Data    │    │  Kinesis Video   │                   │
│  │   Analytics      │    │    Streams       │                   │
│  │                  │    │                  │                   │
│  │ Real-time        │    │ Stream and       │                   │
│  │ analytics with   │    │ process video    │                   │
│  │ SQL/Flink        │    │ streams          │                   │
│  └──────────────────┘    └──────────────────┘                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Key Use Cases

1. **Real-time Analytics**: Dashboards, metrics, monitoring
2. **Log and Event Processing**: Application logs, clickstreams
3. **IoT Data Ingestion**: Sensor data, telemetry
4. **Video Processing**: Live video analytics, ML inference
5. **ETL Pipelines**: Transform and load streaming data

---

## Kinesis Data Streams

### What is Kinesis Data Streams?

Kinesis Data Streams (KDS) is a real-time data streaming service that can continuously capture gigabytes of data per second from hundreds of thousands of sources.

### Key Features

- **Real-time**: Sub-second data latency
- **Scalable**: Throughput scales with shards
- **Durable**: Data replicated across 3 AZs
- **Flexible Retention**: 24 hours to 365 days
- **Multiple Consumers**: Parallel processing

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                  Kinesis Data Streams Architecture               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Producers                Stream                   Consumers    │
│   ─────────                ────────                 ─────────    │
│                                                                  │
│   ┌──────────┐         ┌─────────────────┐      ┌──────────┐   │
│   │  App 1   │         │                 │      │ Lambda   │   │
│   └────┬─────┘         │   ┌─────────┐   │      └──────────┘   │
│        │               │   │ Shard 1 │   │                      │
│   ┌────┴─────┐    ───► │   ├─────────┤   │ ───► ┌──────────┐   │
│   │  App 2   │         │   │ Shard 2 │   │      │   EC2    │   │
│   └────┬─────┘         │   ├─────────┤   │      └──────────┘   │
│        │               │   │ Shard 3 │   │                      │
│   ┌────┴─────┐         │   └─────────┘   │      ┌──────────┐   │
│   │ IoT/SDK  │         │                 │ ───► │ Firehose │   │
│   └──────────┘         └─────────────────┘      └──────────┘   │
│                                                                  │
│   Data Flow:                                                     │
│   1. Producers send records with partition key                  │
│   2. Records distributed to shards by partition key hash        │
│   3. Consumers read and process records                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Shards

Shards are the base throughput unit of a Kinesis data stream:

| Metric | Per Shard Capacity |
|--------|-------------------|
| **Write** | 1 MB/sec or 1,000 records/sec |
| **Read** | 2 MB/sec (shared) or 2 MB/sec per consumer (enhanced) |
| **Data Records** | Up to 1 MB each |

### Partition Keys

- Determine which shard receives the record
- MD5 hash maps key to shard
- Same key = same shard (ordering guaranteed)
- Use unique keys for even distribution

```python
# Producer sending records
import boto3

kinesis = boto3.client('kinesis')

# Records with same partition key go to same shard
kinesis.put_record(
    StreamName='my-stream',
    Data=b'{"event": "click", "user": "123"}',
    PartitionKey='user-123'  # All user-123 events in order
)
```

### Data Retention

| Retention Period | Use Case | Cost Impact |
|-----------------|----------|-------------|
| **24 hours** (default) | Real-time processing | Base cost |
| **7 days** | Reprocessing, debugging | Higher cost |
| **365 days** | Compliance, audit | Highest cost |

### Capacity Modes

#### On-Demand Mode
- Automatic scaling
- No capacity planning required
- Pay per GB ingested/retrieved
- Best for: Variable/unpredictable workloads

#### Provisioned Mode
- Manual shard management
- Fixed capacity (add/remove shards)
- Pay per shard-hour
- Best for: Predictable workloads, cost optimization

### Consumer Types

#### Shared Throughput (Standard)
- 2 MB/sec per shard shared across all consumers
- Lower cost
- Use GetRecords API
- 200 ms latency

#### Enhanced Fan-Out (EFO)
- 2 MB/sec per shard PER consumer
- Higher cost
- Use SubscribeToShard API
- ~70 ms latency
- Dedicated throughput

```
┌──────────────────────────────────────────────────────────────┐
│           Standard vs Enhanced Fan-Out Consumers              │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Standard (Shared):              Enhanced Fan-Out:           │
│  ┌───────────┐                   ┌───────────┐               │
│  │   Shard   │ 2 MB/s            │   Shard   │               │
│  └─────┬─────┘ total             └─────┬─────┘               │
│        │                               │                      │
│   ┌────┴────┬────────┐          ┌─────┼─────┬─────┐         │
│   ▼         ▼        ▼          ▼     ▼     ▼     ▼         │
│ ┌───┐    ┌───┐    ┌───┐      ┌───┐ ┌───┐ ┌───┐ ┌───┐      │
│ │C1 │    │C2 │    │C3 │      │C1 │ │C2 │ │C3 │ │C4 │      │
│ └───┘    └───┘    └───┘      └───┘ └───┘ └───┘ └───┘      │
│                                2MB/s 2MB/s 2MB/s 2MB/s      │
│  Share 2 MB/s                  each   each  each  each      │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

---

## Kinesis Data Firehose

### What is Kinesis Data Firehose?

Kinesis Data Firehose is the easiest way to reliably load streaming data into data lakes, data stores, and analytics services. It can capture, transform, and deliver streaming data.

### Key Features

- **Fully Managed**: No administration required
- **Auto Scaling**: Scales automatically
- **Near Real-time**: 60 seconds minimum buffer
- **Data Transformation**: Lambda integration
- **Format Conversion**: Parquet, ORC
- **Compression**: GZIP, Snappy, ZIP

### Supported Destinations

| Destination | Description |
|-------------|-------------|
| **Amazon S3** | Data lake storage |
| **Amazon Redshift** | Data warehouse (via S3) |
| **Amazon OpenSearch** | Search and analytics |
| **Splunk** | SIEM and monitoring |
| **HTTP Endpoint** | Custom destinations |
| **Third-party** | Datadog, MongoDB, etc. |

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                  Kinesis Data Firehose Architecture              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Sources              Firehose               Destinations       │
│                                                                  │
│   ┌──────────┐      ┌─────────────────┐      ┌──────────┐       │
│   │ Direct   │      │                 │      │    S3    │       │
│   │ PUT      │ ───► │  ┌───────────┐  │ ───► └──────────┘       │
│   └──────────┘      │  │ Buffer    │  │                         │
│                     │  │ (size or  │  │      ┌──────────┐       │
│   ┌──────────┐      │  │  time)    │  │ ───► │ Redshift │       │
│   │ Kinesis  │ ───► │  └───────────┘  │      └──────────┘       │
│   │ Streams  │      │        │        │                         │
│   └──────────┘      │        ▼        │      ┌──────────┐       │
│                     │  ┌───────────┐  │ ───► │OpenSearch│       │
│   ┌──────────┐      │  │ Transform │  │      └──────────┘       │
│   │ CloudWatch│ ───► │  │ (Lambda) │  │                         │
│   │ Logs     │      │  └───────────┘  │      ┌──────────┐       │
│   └──────────┘      │        │        │ ───► │  Splunk  │       │
│                     │        ▼        │      └──────────┘       │
│   ┌──────────┐      │  ┌───────────┐  │                         │
│   │  AWS     │ ───► │  │ Convert   │  │      ┌──────────┐       │
│   │  IoT     │      │  │ (Parquet) │  │ ───► │  HTTP    │       │
│   └──────────┘      │  └───────────┘  │      │ Endpoint │       │
│                     │                 │      └──────────┘       │
│                     └─────────────────┘                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Buffer Configuration

Firehose buffers incoming data before delivery:

| Setting | Minimum | Maximum | Default |
|---------|---------|---------|---------|
| **Buffer Size** | 1 MB | 128 MB | 5 MB |
| **Buffer Interval** | 60 seconds | 900 seconds | 300 seconds |

- Delivers when EITHER condition is met first
- Smaller buffers = faster delivery, more requests
- Larger buffers = higher latency, fewer requests

### Data Transformation

Transform data with Lambda before delivery:

```python
# Lambda transformation function
import base64
import json

def lambda_handler(event, context):
    output = []
    
    for record in event['records']:
        # Decode incoming data
        payload = base64.b64decode(record['data']).decode('utf-8')
        data = json.loads(payload)
        
        # Transform data
        data['processed_at'] = '2024-01-15T10:30:00Z'
        data['source'] = 'firehose'
        
        # Encode output
        output_data = json.dumps(data) + '\n'
        
        output.append({
            'recordId': record['recordId'],
            'result': 'Ok',
            'data': base64.b64encode(output_data.encode('utf-8')).decode('utf-8')
        })
    
    return {'records': output}
```

### Format Conversion

Convert JSON to columnar formats:

- **Apache Parquet**: Columnar, great for analytics
- **Apache ORC**: Columnar, optimized for Hive

```json
{
  "DataFormatConversionConfiguration": {
    "Enabled": true,
    "InputFormatConfiguration": {
      "Deserializer": {
        "OpenXJsonSerDe": {}
      }
    },
    "OutputFormatConfiguration": {
      "Serializer": {
        "ParquetSerDe": {
          "Compression": "SNAPPY"
        }
      }
    },
    "SchemaConfiguration": {
      "DatabaseName": "my_database",
      "TableName": "my_table",
      "RoleARN": "arn:aws:iam::123456789:role/firehose-role"
    }
  }
}
```

### Firehose vs Data Streams

| Feature | Data Streams | Firehose |
|---------|--------------|----------|
| **Management** | Manual sharding | Fully managed |
| **Latency** | Real-time (~200 ms) | Near real-time (~60 sec) |
| **Scaling** | Add/remove shards | Automatic |
| **Custom Code** | Required (consumers) | Optional (Lambda) |
| **Replay** | Yes (retention period) | No |
| **Destinations** | Custom consumers | Pre-built (S3, Redshift, etc.) |
| **Pricing** | Per shard-hour | Per GB ingested |

---

## Kinesis Data Analytics

### What is Kinesis Data Analytics?

Kinesis Data Analytics enables you to process and analyze streaming data using SQL or Apache Flink.

### Two Versions

#### 1. SQL Applications (Legacy)
- Write SQL queries against streaming data
- Simpler for SQL-familiar users
- Limited to SQL operations

#### 2. Apache Flink Applications
- Use Java, Scala, or Python
- More powerful processing
- Complex event processing
- Exactly-once semantics

### SQL Application Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│               Kinesis Data Analytics (SQL)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌──────────────┐                        ┌──────────────┐      │
│   │   Input      │                        │   Output     │      │
│   │   Stream     │                        │   Stream     │      │
│   │  (Kinesis    │      ┌──────────┐      │  (Kinesis    │      │
│   │   or         │ ───► │   SQL    │ ───► │   Data       │      │
│   │   Firehose)  │      │  Query   │      │   Streams    │      │
│   └──────────────┘      └──────────┘      │   or         │      │
│                                           │   Firehose)  │      │
│   Reference Data                          └──────────────┘      │
│   (S3)                                                           │
│   ┌──────────────┐                                              │
│   │  Lookup      │                                              │
│   │  Tables      │ ──────────────────────►                      │
│   │  (S3)        │       JOIN                                   │
│   └──────────────┘                                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### SQL Examples

```sql
-- Real-time aggregation (tumbling window)
CREATE OR REPLACE STREAM "DESTINATION_SQL_STREAM" (
    ticker_symbol VARCHAR(4),
    avg_price DOUBLE,
    record_count INTEGER
);

CREATE OR REPLACE PUMP "STREAM_PUMP" AS
INSERT INTO "DESTINATION_SQL_STREAM"
SELECT STREAM
    ticker_symbol,
    AVG(price) AS avg_price,
    COUNT(*) AS record_count
FROM "SOURCE_SQL_STREAM_001"
GROUP BY
    ticker_symbol,
    STEP("SOURCE_SQL_STREAM_001".ROWTIME BY INTERVAL '60' SECOND);

-- Anomaly detection
CREATE OR REPLACE STREAM "ANOMALY_STREAM" (
    ticker_symbol VARCHAR(4),
    price DOUBLE,
    anomaly_score DOUBLE
);

CREATE OR REPLACE PUMP "ANOMALY_PUMP" AS
INSERT INTO "ANOMALY_STREAM"
SELECT STREAM
    ticker_symbol,
    price,
    ANOMALY_SCORE
FROM TABLE(
    RANDOM_CUT_FOREST(
        CURSOR(SELECT STREAM * FROM "SOURCE_SQL_STREAM_001")
    )
);
```

### Apache Flink Applications

```java
// Flink application example
public class StreamingJob {
    public static void main(String[] args) throws Exception {
        StreamExecutionEnvironment env = 
            StreamExecutionEnvironment.getExecutionEnvironment();
        
        // Read from Kinesis
        FlinkKinesisConsumer<String> consumer = new FlinkKinesisConsumer<>(
            "input-stream",
            new SimpleStringSchema(),
            consumerConfig
        );
        
        DataStream<String> stream = env.addSource(consumer);
        
        // Process data
        DataStream<Result> processed = stream
            .map(new ParseFunction())
            .keyBy(event -> event.getKey())
            .window(TumblingEventTimeWindows.of(Time.minutes(1)))
            .aggregate(new MyAggregator());
        
        // Write to Kinesis
        FlinkKinesisProducer<String> producer = new FlinkKinesisProducer<>(
            new SimpleStringSchema(),
            producerConfig
        );
        producer.setDefaultStream("output-stream");
        
        processed.map(Object::toString).addSink(producer);
        
        env.execute("Streaming Job");
    }
}
```

---

## Kinesis Video Streams

### What is Kinesis Video Streams?

Kinesis Video Streams makes it easy to securely stream video from connected devices to AWS for analytics, machine learning, playback, and processing.

### Key Features

- **Secure Streaming**: TLS encryption
- **Durable Storage**: Up to 10 years retention
- **SDK Support**: C/C++, Java producers
- **Playback**: HLS and DASH streaming
- **ML Integration**: Rekognition, SageMaker

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│               Kinesis Video Streams Architecture                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Producers                                    Consumers         │
│                                                                  │
│   ┌──────────┐         ┌───────────────┐      ┌──────────┐     │
│   │  Camera  │         │   Kinesis     │      │ HLS/DASH │     │
│   │          │ ──────► │   Video       │ ───► │ Playback │     │
│   └──────────┘         │   Stream      │      └──────────┘     │
│                        │               │                        │
│   ┌──────────┐         │  ┌─────────┐  │      ┌──────────┐     │
│   │  Drone   │ ──────► │  │  Stored │  │ ───► │Rekognition│    │
│   │          │         │  │  Video  │  │      │  Video   │     │
│   └──────────┘         │  └─────────┘  │      └──────────┘     │
│                        │               │                        │
│   ┌──────────┐         │               │      ┌──────────┐     │
│   │  RTSP    │ ──────► │               │ ───► │SageMaker │     │
│   │  Camera  │         │               │      │          │     │
│   └──────────┘         └───────────────┘      └──────────┘     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Use Cases

1. **Smart Home**: Video doorbells, security cameras
2. **Smart City**: Traffic monitoring, public safety
3. **Industrial**: Quality inspection, safety monitoring
4. **Retail**: Customer analytics, loss prevention

---

## Kinesis Services Comparison

### Decision Matrix

| Requirement | Service |
|-------------|---------|
| Real-time processing with custom code | **Kinesis Data Streams** |
| Load data to S3/Redshift/OpenSearch | **Kinesis Data Firehose** |
| SQL-based stream analytics | **Kinesis Data Analytics** |
| Video streaming and analysis | **Kinesis Video Streams** |
| Replay/reprocess data | **Kinesis Data Streams** |
| Fully managed, no code | **Kinesis Data Firehose** |
| Sub-second latency | **Kinesis Data Streams** |
| Complex event processing | **Kinesis Data Analytics (Flink)** |

### Feature Comparison

| Feature | Data Streams | Firehose | Data Analytics |
|---------|--------------|----------|----------------|
| **Latency** | ~200 ms | ~60 seconds | ~1 second |
| **Scaling** | Manual shards | Automatic | Automatic |
| **Data Retention** | 24h-365d | None | None |
| **Custom Code** | Required | Optional | SQL/Flink |
| **Management** | Semi-managed | Fully managed | Fully managed |
| **Replay** | Yes | No | No |

### Common Patterns

```
┌─────────────────────────────────────────────────────────────────┐
│                    Common Kinesis Patterns                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Pattern 1: Direct to S3                                         │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐              │
│  │ Producer │ ───► │ Firehose │ ───► │    S3    │              │
│  └──────────┘      └──────────┘      └──────────┘              │
│                                                                  │
│  Pattern 2: Real-time Processing                                 │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐              │
│  │ Producer │ ───► │  Streams │ ───► │  Lambda  │              │
│  └──────────┘      └──────────┘      └──────────┘              │
│                                                                  │
│  Pattern 3: Analytics + Storage                                  │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐    │
│  │ Producer │ ─►│ Streams  │ ─►│ Analytics│ ─►│ Firehose │ ─► S3│
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘    │
│                                                                  │
│  Pattern 4: Fan-out                                              │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐              │
│  │ Producer │ ───► │  Streams │ ───► │ Lambda 1 │              │
│  └──────────┘      └────┬─────┘      ├──────────┤              │
│                         ├──────────► │ Lambda 2 │              │
│                         └──────────► │ Firehose │              │
│                                      └──────────┘              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Producers

### Producer SDK

```python
import boto3

kinesis = boto3.client('kinesis')

# Put single record
response = kinesis.put_record(
    StreamName='my-stream',
    Data=b'{"event": "page_view", "page": "/home"}',
    PartitionKey='user-123'
)

# Put multiple records (batch)
response = kinesis.put_records(
    StreamName='my-stream',
    Records=[
        {
            'Data': b'{"event": "click"}',
            'PartitionKey': 'user-123'
        },
        {
            'Data': b'{"event": "purchase"}',
            'PartitionKey': 'user-456'
        }
    ]
)
```

### Kinesis Producer Library (KPL)

High-performance producer with:
- Automatic batching
- Retry logic
- Aggregation (multiple records per API call)
- Async operations

```java
KinesisProducer producer = new KinesisProducer(config);

// Async put with callback
ListenableFuture<UserRecordResult> future = producer.addUserRecord(
    "my-stream",
    "partition-key",
    ByteBuffer.wrap("data".getBytes())
);

Futures.addCallback(future, new FutureCallback<UserRecordResult>() {
    @Override
    public void onSuccess(UserRecordResult result) {
        // Handle success
    }
    
    @Override
    public void onFailure(Throwable t) {
        // Handle failure
    }
});
```

### Kinesis Agent

Pre-built Java agent for log files:

```json
{
  "cloudwatch.endpoint": "monitoring.us-east-1.amazonaws.com",
  "kinesis.endpoint": "kinesis.us-east-1.amazonaws.com",
  "flows": [
    {
      "filePattern": "/var/log/app/*.log",
      "kinesisStream": "my-stream",
      "partitionKeyOption": "RANDOM"
    }
  ]
}
```

---

## Data Consumers

### Consumer SDK

```python
import boto3

kinesis = boto3.client('kinesis')

# Get shard iterator
response = kinesis.get_shard_iterator(
    StreamName='my-stream',
    ShardId='shardId-000000000000',
    ShardIteratorType='LATEST'  # or TRIM_HORIZON, AT_TIMESTAMP
)
shard_iterator = response['ShardIterator']

# Read records
while True:
    response = kinesis.get_records(
        ShardIterator=shard_iterator,
        Limit=100
    )
    
    for record in response['Records']:
        data = record['Data']
        # Process record
    
    shard_iterator = response['NextShardIterator']
```

### Kinesis Client Library (KCL)

Managed consumer with:
- Automatic load balancing across workers
- Checkpointing
- Shard distribution
- Lease management (DynamoDB)

```java
public class RecordProcessor implements IRecordProcessor {
    
    @Override
    public void processRecords(ProcessRecordsInput input) {
        for (Record record : input.getRecords()) {
            // Process record
            byte[] data = record.getData().array();
            String partitionKey = record.getPartitionKey();
            
            // Your processing logic
            processData(data);
        }
        
        // Checkpoint after processing
        input.getCheckpointer().checkpoint();
    }
}
```

### Lambda Consumer

Event source mapping for Lambda:

```yaml
# SAM Template
MyFunction:
  Type: AWS::Serverless::Function
  Properties:
    Handler: index.handler
    Events:
      KinesisEvent:
        Type: Kinesis
        Properties:
          Stream: !GetAtt MyStream.Arn
          StartingPosition: LATEST
          BatchSize: 100
          ParallelizationFactor: 10
          MaximumRetryAttempts: 3
          MaximumBatchingWindowInSeconds: 5
```

```python
# Lambda handler
def handler(event, context):
    for record in event['Records']:
        # Decode base64 data
        data = base64.b64decode(record['kinesis']['data'])
        
        # Process record
        print(f"Data: {data}")
        print(f"Partition Key: {record['kinesis']['partitionKey']}")
        print(f"Sequence Number: {record['kinesis']['sequenceNumber']}")
```

---

## Security

### Encryption

#### In-Transit Encryption
- TLS 1.2 for all API calls
- Automatic, no configuration needed

#### At-Rest Encryption (Server-Side)
- AWS managed key (aws/kinesis)
- Customer managed KMS key
- Automatic encryption/decryption

```python
# Create encrypted stream
kinesis.create_stream(
    StreamName='encrypted-stream',
    ShardCount=2,
    StreamModeDetails={'StreamMode': 'PROVISIONED'},
    # Encryption enabled by default with AWS managed key
)

# Or specify customer managed key
kinesis.start_stream_encryption(
    StreamName='my-stream',
    EncryptionType='KMS',
    KeyId='arn:aws:kms:us-east-1:123456789:key/12345678-1234-1234-1234-123456789012'
)
```

### IAM Policies

#### Producer Policy
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "kinesis:PutRecord",
        "kinesis:PutRecords",
        "kinesis:DescribeStream"
      ],
      "Resource": "arn:aws:kinesis:us-east-1:123456789:stream/my-stream"
    }
  ]
}
```

#### Consumer Policy
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "kinesis:GetRecords",
        "kinesis:GetShardIterator",
        "kinesis:DescribeStream",
        "kinesis:DescribeStreamSummary",
        "kinesis:ListShards"
      ],
      "Resource": "arn:aws:kinesis:us-east-1:123456789:stream/my-stream"
    }
  ]
}
```

### VPC Endpoints

Access Kinesis without internet:

```
┌──────────────────────────────────────────────────────────────┐
│                          VPC                                  │
│   ┌──────────────────────────────────────────────────────┐  │
│   │                 Private Subnet                        │  │
│   │   ┌──────────┐      ┌────────────────────┐           │  │
│   │   │   EC2    │ ───► │  VPC Endpoint      │           │  │
│   │   │ Producer │      │  (Interface)       │           │  │
│   │   └──────────┘      └─────────┬──────────┘           │  │
│   └───────────────────────────────│───────────────────────┘  │
│                                   │                           │
└───────────────────────────────────│───────────────────────────┘
                                    │
                                    ▼
                            ┌──────────────┐
                            │   Kinesis    │
                            │   Service    │
                            └──────────────┘
```

---

## Monitoring and Performance

### CloudWatch Metrics

#### Stream-Level Metrics

| Metric | Description |
|--------|-------------|
| **IncomingBytes** | Bytes put to stream |
| **IncomingRecords** | Records put to stream |
| **GetRecords.Bytes** | Bytes retrieved |
| **GetRecords.Records** | Records retrieved |
| **WriteProvisionedThroughputExceeded** | Throttled writes |
| **ReadProvisionedThroughputExceeded** | Throttled reads |
| **IteratorAgeMilliseconds** | Consumer lag |

#### Shard-Level Metrics
- Must be enabled separately
- Per-shard granularity
- Additional cost

### Key Alarms

```yaml
# Alarm for write throttling
WriteThrottleAlarm:
  Type: AWS::CloudWatch::Alarm
  Properties:
    MetricName: WriteProvisionedThroughputExceeded
    Namespace: AWS/Kinesis
    Statistic: Sum
    Period: 60
    EvaluationPeriods: 1
    Threshold: 0
    ComparisonOperator: GreaterThanThreshold
    Dimensions:
      - Name: StreamName
        Value: my-stream

# Alarm for consumer lag
ConsumerLagAlarm:
  Type: AWS::CloudWatch::Alarm
  Properties:
    MetricName: GetRecords.IteratorAgeMilliseconds
    Namespace: AWS/Kinesis
    Statistic: Maximum
    Period: 60
    EvaluationPeriods: 5
    Threshold: 60000  # 1 minute lag
    ComparisonOperator: GreaterThanThreshold
```

### Performance Optimization

1. **Batch Records**: Use PutRecords instead of PutRecord
2. **Use KPL**: Automatic aggregation and batching
3. **Partition Key Design**: Even distribution across shards
4. **Right-size Shards**: Monitor and adjust capacity
5. **Enhanced Fan-Out**: For multiple high-throughput consumers

---

## Scaling and Capacity

### Shard Management

#### Scaling Up (Split Shard)
- Split one shard into two
- Doubles throughput for that data
- Parent shard becomes read-only

#### Scaling Down (Merge Shards)
- Merge two adjacent shards
- Reduces throughput
- Both parent shards become read-only

### Scaling Strategies

| Strategy | Description | Use Case |
|----------|-------------|----------|
| **On-Demand** | Automatic scaling | Variable workloads |
| **Manual** | Add/remove shards | Predictable changes |
| **Auto Scaling** | CloudWatch + Lambda | Automated response |

### Auto Scaling with Lambda

```python
import boto3

def scale_kinesis_stream(event, context):
    cloudwatch = boto3.client('cloudwatch')
    kinesis = boto3.client('kinesis')
    
    # Get current metrics
    response = cloudwatch.get_metric_statistics(
        Namespace='AWS/Kinesis',
        MetricName='IncomingBytes',
        Dimensions=[{'Name': 'StreamName', 'Value': 'my-stream'}],
        StartTime=datetime.utcnow() - timedelta(minutes=5),
        EndTime=datetime.utcnow(),
        Period=300,
        Statistics=['Sum']
    )
    
    # Calculate if scaling needed
    incoming_bytes = response['Datapoints'][0]['Sum'] if response['Datapoints'] else 0
    
    # Get current shard count
    stream_info = kinesis.describe_stream(StreamName='my-stream')
    shard_count = len([s for s in stream_info['StreamDescription']['Shards'] 
                       if not s.get('SequenceNumberRange', {}).get('EndingSequenceNumber')])
    
    # Scale if needed
    max_throughput = shard_count * 1024 * 1024 * 300  # 1 MB/s per shard for 5 min
    
    if incoming_bytes > max_throughput * 0.8:  # 80% threshold
        kinesis.update_shard_count(
            StreamName='my-stream',
            TargetShardCount=shard_count * 2,
            ScalingType='UNIFORM_SCALING'
        )
```

---

## Cost Optimization

### Pricing Components

#### Kinesis Data Streams

| Component | Provisioned | On-Demand |
|-----------|-------------|-----------|
| **Shard Hour** | $0.015/shard/hour | N/A |
| **PUT Payload Units** | $0.014/million | $0.08/GB ingested |
| **Extended Retention** | $0.020/shard/hour | $0.02/GB-month |
| **Enhanced Fan-Out** | $0.015/consumer-shard/hour + $0.013/GB |

#### Kinesis Data Firehose

| Component | Price |
|-----------|-------|
| **Data Ingested** | $0.029/GB (first 500 TB) |
| **Format Conversion** | $0.018/GB |
| **VPC Delivery** | $0.01/hour + $0.01/GB |

### Cost Optimization Tips

1. **Use On-Demand**: For variable workloads
2. **Right-size Retention**: Don't retain longer than needed
3. **Batch Records**: Reduce PUT unit charges
4. **Use KPL Aggregation**: More records per PUT
5. **Compress Data**: Reduce data volume
6. **Firehose for Delivery**: Simpler than custom consumers

### Cost Comparison Example

**Scenario**: 100 GB/day ingestion, 7-day retention

| Option | Monthly Cost (approx.) |
|--------|----------------------|
| Data Streams (2 shards) | ~$22 + PUT units |
| Data Streams On-Demand | ~$240 |
| Firehose to S3 | ~$87 |

---

## Best Practices

### Producer Best Practices

1. **Use Partition Keys Wisely**: Even distribution
2. **Batch with PutRecords**: Up to 500 records per call
3. **Implement Retries**: Handle throttling
4. **Use KPL**: For high-throughput producers
5. **Compress Large Records**: Before sending

### Consumer Best Practices

1. **Use KCL**: For managed checkpointing
2. **Handle Duplicates**: At-least-once delivery
3. **Monitor Iterator Age**: Detect lag
4. **Use Enhanced Fan-Out**: For multiple consumers
5. **Process in Batches**: Efficient processing

### General Best Practices

1. **Enable Encryption**: At-rest and in-transit
2. **Use VPC Endpoints**: For private access
3. **Monitor Metrics**: Proactive scaling
4. **Set Up Alarms**: Throttling, lag detection
5. **Plan Retention**: Based on replay needs

---

## Common Architectures

### Real-time Analytics Dashboard

```
┌─────────────────────────────────────────────────────────────────┐
│              Real-time Analytics Architecture                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   │
│   │   Web    │   │ Kinesis  │   │ Kinesis  │   │  Kinesis │   │
│   │   App    │──►│  Data    │──►│   Data   │──►│   Data   │   │
│   │          │   │ Streams  │   │ Analytics│   │ Firehose │   │
│   └──────────┘   └──────────┘   └──────────┘   └────┬─────┘   │
│                                                      │         │
│                                        ┌─────────────┴────┐    │
│                                        │                  │    │
│                                        ▼                  ▼    │
│                                   ┌──────────┐     ┌─────────┐ │
│                                   │OpenSearch│     │   S3    │ │
│                                   │Dashboard │     │ Archive │ │
│                                   └──────────┘     └─────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### IoT Data Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    IoT Data Pipeline                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   │
│   │   IoT    │   │  AWS     │   │ Kinesis  │   │  Lambda  │   │
│   │ Sensors  │──►│  IoT     │──►│   Data   │──►│ (Process)│   │
│   │          │   │  Core    │   │ Streams  │   └────┬─────┘   │
│   └──────────┘   └──────────┘   └──────────┘        │         │
│                                                      │         │
│                       ┌──────────────────────────────┼────┐    │
│                       │                              │    │    │
│                       ▼                              ▼    ▼    │
│                  ┌──────────┐              ┌─────┐┌──────────┐ │
│                  │ DynamoDB │              │ SNS ││   S3     │ │
│                  │ (Alerts) │              │Alerts│ (Archive)│ │
│                  └──────────┘              └─────┘└──────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Log Aggregation

```
┌─────────────────────────────────────────────────────────────────┐
│                    Log Aggregation Pipeline                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌──────────┐                                                  │
│   │  EC2     │ ──┐                                              │
│   │  Logs    │   │                                              │
│   └──────────┘   │     ┌──────────┐     ┌──────────┐           │
│                  │     │          │     │          │           │
│   ┌──────────┐   ├────►│ Kinesis  │────►│  Kinesis │───► S3    │
│   │Container │   │     │   Data   │     │   Data   │           │
│   │  Logs    │ ──┤     │ Streams  │     │ Firehose │           │
│   └──────────┘   │     │          │     │(transform│           │
│                  │     └──────────┘     │  + S3)   │           │
│   ┌──────────┐   │                      └──────────┘           │
│   │ Lambda   │ ──┘                                              │
│   │  Logs    │                                                  │
│   └──────────┘                                                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## SAA-C03 Exam Tips

### Key Concepts to Remember

1. **Data Streams** = Real-time, custom consumers, replay capability
2. **Firehose** = Near real-time, managed delivery, no replay
3. **Data Analytics** = SQL/Flink on streaming data
4. **Shard** = 1 MB/s write, 2 MB/s read
5. **Partition Key** = Determines shard, enables ordering

### Common Exam Scenarios

#### Scenario 1: Real-time Processing with Lambda
**Question**: Process streaming data in real-time with Lambda.
**Answer**: Kinesis Data Streams with Lambda event source mapping

#### Scenario 2: Load Streaming Data to S3
**Question**: Continuously load streaming data to S3 with minimal management.
**Answer**: Kinesis Data Firehose (automatic batching, delivery)

#### Scenario 3: Multiple Consumers with High Throughput
**Question**: Multiple applications need to consume same stream independently.
**Answer**: Kinesis Data Streams with Enhanced Fan-Out

#### Scenario 4: Replay Historical Data
**Question**: Need to reprocess data from 3 days ago.
**Answer**: Kinesis Data Streams with extended retention

#### Scenario 5: Real-time Aggregations
**Question**: Calculate rolling averages on streaming data.
**Answer**: Kinesis Data Analytics (SQL or Flink)

### Default Values to Remember

| Setting | Default |
|---------|---------|
| Data Streams Retention | 24 hours |
| Maximum Retention | 365 days |
| Record Size | 1 MB maximum |
| Firehose Buffer Interval | 300 seconds (5 min) |
| Firehose Buffer Size | 5 MB |
| Shards per Stream | No limit (soft limits apply) |

### Exam Question Keywords

- "Real-time streaming" → **Kinesis Data Streams**
- "Load to S3/Redshift" → **Kinesis Data Firehose**
- "SQL on streaming data" → **Kinesis Data Analytics**
- "Video streaming" → **Kinesis Video Streams**
- "Replay data" → **Kinesis Data Streams**
- "No management/serverless delivery" → **Firehose**
- "Multiple consumers" → **Enhanced Fan-Out**
- "Ordering guarantee" → **Same partition key**

---

## AWS CLI Commands Reference

### Kinesis Data Streams

#### Create and Manage Streams

```bash
# Create a stream with specified shard count
aws kinesis create-stream \
    --stream-name my-data-stream \
    --shard-count 3

# Create stream with on-demand capacity mode
aws kinesis create-stream \
    --stream-name my-ondemand-stream \
    --stream-mode-details StreamMode=ON_DEMAND

# Create stream with provisioned capacity mode
aws kinesis create-stream \
    --stream-name my-provisioned-stream \
    --stream-mode-details StreamMode=PROVISIONED \
    --shard-count 5

# Describe stream details
aws kinesis describe-stream \
    --stream-name my-data-stream

# Describe stream summary (faster)
aws kinesis describe-stream-summary \
    --stream-name my-data-stream

# List all streams
aws kinesis list-streams

# List streams with limit
aws kinesis list-streams --limit 10

# Delete stream
aws kinesis delete-stream \
    --stream-name my-data-stream

# Delete stream and disable enforcement of minimum retention period
aws kinesis delete-stream \
    --stream-name my-data-stream \
    --enforce-consumer-deletion
```

#### Update Stream Configuration

```bash
# Update shard count (scale up)
aws kinesis update-shard-count \
    --stream-name my-data-stream \
    --target-shard-count 6 \
    --scaling-type UNIFORM_SCALING

# Update stream mode to on-demand
aws kinesis update-stream-mode \
    --stream-arn arn:aws:kinesis:us-east-1:123456789012:stream/my-data-stream \
    --stream-mode-details StreamMode=ON_DEMAND

# Increase retention period (1-365 days)
aws kinesis increase-stream-retention-period \
    --stream-name my-data-stream \
    --retention-period-hours 168

# Decrease retention period
aws kinesis decrease-stream-retention-period \
    --stream-name my-data-stream \
    --retention-period-hours 24
```

---

### Put Records (Producer Operations)

#### Put Single Record

```bash
# Put a single record
aws kinesis put-record \
    --stream-name my-data-stream \
    --partition-key user123 \
    --data '{"temperature": 72, "humidity": 45}'

# Put record with base64 encoded data
echo -n '{"user":"john","action":"login"}' | base64 | xargs -I {} aws kinesis put-record \
    --stream-name my-data-stream \
    --partition-key user_john \
    --data {}

# Put record with explicit hash key
aws kinesis put-record \
    --stream-name my-data-stream \
    --partition-key sensor001 \
    --explicit-hash-key 12345678901234567890123456789012 \
    --data '{"reading": 98.6}'

# Put record with sequence number ordering
aws kinesis put-record \
    --stream-name my-data-stream \
    --partition-key order123 \
    --data '{"item":"laptop","price":999}' \
    --sequence-number-for-ordering 49590338271490256608559692538361571095921575989136588898
```

#### Put Multiple Records (Batch)

```bash
# Put records in batch (up to 500 records or 5 MB)
aws kinesis put-records \
    --stream-name my-data-stream \
    --records file://records.json

cat > records.json << 'EOF'
[
  {
    "Data": "eyJ1c2VyIjoiYWxpY2UiLCJhY3Rpb24iOiJsb2dpbiJ9",
    "PartitionKey": "user_alice"
  },
  {
    "Data": "eyJ1c2VyIjoiYm9iIiwiYWN0aW9uIjoicHVyY2hhc2UifQ==",
    "PartitionKey": "user_bob"
  },
  {
    "Data": "eyJ1c2VyIjoiY2hhcmxpZSIsImFjdGlvbiI6ImxvZ291dCJ9",
    "PartitionKey": "user_charlie"
  }
]
EOF

# Put records with inline JSON
aws kinesis put-records \
    --stream-name my-data-stream \
    --records \
        Data='{"event":"click","user":"user1"}',PartitionKey=user1 \
        Data='{"event":"view","user":"user2"}',PartitionKey=user2
```

---

### Get Records (Consumer Operations)

#### Get Shard Iterator

```bash
# List shards first
aws kinesis list-shards \
    --stream-name my-data-stream

# Get shard iterator - start from beginning
aws kinesis get-shard-iterator \
    --stream-name my-data-stream \
    --shard-id shardId-000000000000 \
    --shard-iterator-type TRIM_HORIZON

# Get shard iterator - start from latest
aws kinesis get-shard-iterator \
    --stream-name my-data-stream \
    --shard-id shardId-000000000000 \
    --shard-iterator-type LATEST

# Get shard iterator - start at specific sequence number
aws kinesis get-shard-iterator \
    --stream-name my-data-stream \
    --shard-id shardId-000000000000 \
    --shard-iterator-type AT_SEQUENCE_NUMBER \
    --starting-sequence-number 49590338271490256608559692538361571095921575989136588898

# Get shard iterator - start after specific sequence number
aws kinesis get-shard-iterator \
    --stream-name my-data-stream \
    --shard-id shardId-000000000000 \
    --shard-iterator-type AFTER_SEQUENCE_NUMBER \
    --starting-sequence-number 49590338271490256608559692538361571095921575989136588898

# Get shard iterator - start at timestamp
aws kinesis get-shard-iterator \
    --stream-name my-data-stream \
    --shard-id shardId-000000000000 \
    --shard-iterator-type AT_TIMESTAMP \
    --timestamp 1612137600
```

#### Get Records from Stream

```bash
# Get records using shard iterator
SHARD_ITERATOR=$(aws kinesis get-shard-iterator \
    --stream-name my-data-stream \
    --shard-id shardId-000000000000 \
    --shard-iterator-type TRIM_HORIZON \
    --query 'ShardIterator' --output text)

aws kinesis get-records \
    --shard-iterator $SHARD_ITERATOR

# Get records with limit
aws kinesis get-records \
    --shard-iterator $SHARD_ITERATOR \
    --limit 100

# Continuous polling example
SHARD_ITERATOR=$(aws kinesis get-shard-iterator \
    --stream-name my-data-stream \
    --shard-id shardId-000000000000 \
    --shard-iterator-type LATEST \
    --query 'ShardIterator' --output text)

while true; do
    RESULT=$(aws kinesis get-records --shard-iterator $SHARD_ITERATOR)
    echo "$RESULT" | jq -r '.Records[].Data' | base64 -d
    SHARD_ITERATOR=$(echo "$RESULT" | jq -r '.NextShardIterator')
    sleep 1
done
```

---

### Shard Management

#### List and Describe Shards

```bash
# List all shards in a stream
aws kinesis list-shards \
    --stream-name my-data-stream

# List shards starting from specific shard
aws kinesis list-shards \
    --stream-name my-data-stream \
    --exclusive-start-shard-id shardId-000000000002

# List shards with max results
aws kinesis list-shards \
    --stream-name my-data-stream \
    --max-results 10

# List shards at specific timestamp
aws kinesis list-shards \
    --stream-name my-data-stream \
    --stream-creation-timestamp 1612137600

# List shards using stream ARN
aws kinesis list-shards \
    --stream-arn arn:aws:kinesis:us-east-1:123456789012:stream/my-data-stream
```

#### Split Shards

```bash
# Split a shard to increase capacity
# First, get the shard information
aws kinesis describe-stream \
    --stream-name my-data-stream

# Split shard at the middle of hash key range
aws kinesis split-shard \
    --stream-name my-data-stream \
    --shard-to-split shardId-000000000000 \
    --new-starting-hash-key 170141183460469231731687303715884105728

# Split shard with calculated hash key
# For a shard with range 0 to 340282366920938463463374607431768211455
# Split in the middle: 170141183460469231731687303715884105728
aws kinesis split-shard \
    --stream-name my-data-stream \
    --shard-to-split shardId-000000000001 \
    --new-starting-hash-key 85070591730234615865843651857942052864
```

#### Merge Shards

```bash
# Merge two adjacent shards to reduce capacity and costs
aws kinesis merge-shards \
    --stream-name my-data-stream \
    --shard-to-merge shardId-000000000001 \
    --adjacent-shard-to-merge shardId-000000000002

# Example: Merge after splitting
# List shards to identify adjacent shards
aws kinesis list-shards --stream-name my-data-stream

# Merge the shards
aws kinesis merge-shards \
    --stream-name my-data-stream \
    --shard-to-merge shardId-000000000003 \
    --adjacent-shard-to-merge shardId-000000000004
```

---

### Enhanced Fan-Out Consumers

#### Register Stream Consumer

```bash
# Register enhanced fan-out consumer
aws kinesis register-stream-consumer \
    --stream-arn arn:aws:kinesis:us-east-1:123456789012:stream/my-data-stream \
    --consumer-name my-consumer-app

# Describe stream consumer
aws kinesis describe-stream-consumer \
    --stream-arn arn:aws:kinesis:us-east-1:123456789012:stream/my-data-stream \
    --consumer-name my-consumer-app

# Describe consumer by ARN
aws kinesis describe-stream-consumer \
    --consumer-arn arn:aws:kinesis:us-east-1:123456789012:stream/my-data-stream/consumer/my-consumer-app:1612137600

# List stream consumers
aws kinesis list-stream-consumers \
    --stream-arn arn:aws:kinesis:us-east-1:123456789012:stream/my-data-stream

# List consumers with pagination
aws kinesis list-stream-consumers \
    --stream-arn arn:aws:kinesis:us-east-1:123456789012:stream/my-data-stream \
    --max-results 10
```

#### Deregister Stream Consumer

```bash
# Deregister consumer by name
aws kinesis deregister-stream-consumer \
    --stream-arn arn:aws:kinesis:us-east-1:123456789012:stream/my-data-stream \
    --consumer-name my-consumer-app

# Deregister consumer by ARN
aws kinesis deregister-stream-consumer \
    --consumer-arn arn:aws:kinesis:us-east-1:123456789012:stream/my-data-stream/consumer/my-consumer-app:1612137600
```

---

### Stream Encryption

#### Enable and Manage Encryption

```bash
# Enable encryption with AWS managed CMK
aws kinesis start-stream-encryption \
    --stream-name my-data-stream \
    --encryption-type KMS \
    --key-id alias/aws/kinesis

# Enable encryption with customer managed CMK
aws kinesis start-stream-encryption \
    --stream-name my-data-stream \
    --encryption-type KMS \
    --key-id arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012

# Disable encryption
aws kinesis stop-stream-encryption \
    --stream-name my-data-stream \
    --encryption-type KMS \
    --key-id alias/aws/kinesis

# Check encryption status
aws kinesis describe-stream \
    --stream-name my-data-stream \
    --query 'StreamDescription.EncryptionType'
```

---

### Tags and Resource Management

#### Manage Stream Tags

```bash
# Add tags to stream
aws kinesis add-tags-to-stream \
    --stream-name my-data-stream \
    --tags Environment=Production,Application=Analytics,CostCenter=Engineering

# List stream tags
aws kinesis list-tags-for-stream \
    --stream-name my-data-stream

# Remove tags from stream
aws kinesis remove-tags-from-stream \
    --stream-name my-data-stream \
    --tag-keys Environment Application
```

---

## Kinesis Data Firehose

### Create Delivery Streams

#### Create Firehose to S3

```bash
# Create Firehose delivery stream to S3
aws firehose create-delivery-stream \
    --delivery-stream-name my-s3-delivery-stream \
    --delivery-stream-type DirectPut \
    --s3-destination-configuration file://s3-config.json

cat > s3-config.json << 'EOF'
{
  "RoleARN": "arn:aws:iam::123456789012:role/FirehoseDeliveryRole",
  "BucketARN": "arn:aws:s3:::my-firehose-bucket",
  "Prefix": "data/year=!{timestamp:yyyy}/month=!{timestamp:MM}/day=!{timestamp:dd}/",
  "ErrorOutputPrefix": "errors/year=!{timestamp:yyyy}/month=!{timestamp:MM}/day=!{timestamp:dd}/!{firehose:error-output-type}",
  "BufferingHints": {
    "SizeInMBs": 5,
    "IntervalInSeconds": 300
  },
  "CompressionFormat": "GZIP",
  "EncryptionConfiguration": {
    "NoEncryptionConfig": "NoEncryption"
  },
  "CloudWatchLoggingOptions": {
    "Enabled": true,
    "LogGroupName": "/aws/kinesisfirehose/my-s3-delivery-stream",
    "LogStreamName": "S3Delivery"
  }
}
EOF
```

#### Create Firehose from Kinesis Stream

```bash
# Create Firehose with Kinesis Stream as source
aws firehose create-delivery-stream \
    --delivery-stream-name kinesis-to-s3-stream \
    --delivery-stream-type KinesisStreamAsSource \
    --kinesis-stream-source-configuration file://kinesis-source.json \
    --extended-s3-destination-configuration file://extended-s3-config.json

cat > kinesis-source.json << 'EOF'
{
  "KinesisStreamARN": "arn:aws:kinesis:us-east-1:123456789012:stream/my-data-stream",
  "RoleARN": "arn:aws:iam::123456789012:role/FirehoseKinesisRole"
}
EOF
```

#### Create Firehose to Redshift

```bash
# Create Firehose delivery stream to Redshift
aws firehose create-delivery-stream \
    --delivery-stream-name redshift-delivery-stream \
    --redshift-destination-configuration file://redshift-config.json

cat > redshift-config.json << 'EOF'
{
  "RoleARN": "arn:aws:iam::123456789012:role/FirehoseDeliveryRole",
  "ClusterJDBCURL": "jdbc:redshift://redshift-cluster.us-east-1.redshift.amazonaws.com:5439/dev",
  "CopyCommand": {
    "DataTableName": "events",
    "CopyOptions": "JSON 'auto' GZIP"
  },
  "Username": "admin",
  "Password": "MyPassword123!",
  "S3Configuration": {
    "RoleARN": "arn:aws:iam::123456789012:role/FirehoseDeliveryRole",
    "BucketARN": "arn:aws:s3:::my-firehose-redshift-bucket",
    "Prefix": "redshift-data/",
    "BufferingHints": {
      "SizeInMBs": 5,
      "IntervalInSeconds": 300
    },
    "CompressionFormat": "GZIP"
  }
}
EOF
```

#### Create Firehose to Elasticsearch/OpenSearch

```bash
# Create Firehose delivery stream to OpenSearch
aws firehose create-delivery-stream \
    --delivery-stream-name opensearch-delivery-stream \
    --elasticsearch-destination-configuration file://opensearch-config.json

cat > opensearch-config.json << 'EOF'
{
  "RoleARN": "arn:aws:iam::123456789012:role/FirehoseDeliveryRole",
  "DomainARN": "arn:aws:es:us-east-1:123456789012:domain/my-domain",
  "IndexName": "events",
  "TypeName": "_doc",
  "IndexRotationPeriod": "OneDay",
  "BufferingHints": {
    "IntervalInSeconds": 60,
    "SizeInMBs": 5
  },
  "RetryOptions": {
    "DurationInSeconds": 300
  },
  "S3BackupMode": "FailedDocumentsOnly",
  "S3Configuration": {
    "RoleARN": "arn:aws:iam::123456789012:role/FirehoseDeliveryRole",
    "BucketARN": "arn:aws:s3:::my-firehose-backup-bucket",
    "Prefix": "backup/",
    "BufferingHints": {
      "SizeInMBs": 5,
      "IntervalInSeconds": 300
    }
  }
}
EOF
```

### Manage Delivery Streams

```bash
# Describe delivery stream
aws firehose describe-delivery-stream \
    --delivery-stream-name my-s3-delivery-stream

# List delivery streams
aws firehose list-delivery-streams

# List delivery streams with limit
aws firehose list-delivery-streams --limit 10

# Update delivery stream
aws firehose update-destination \
    --delivery-stream-name my-s3-delivery-stream \
    --current-delivery-stream-version-id 1 \
    --destination-id destinationId-000000000001 \
    --s3-destination-update file://s3-update.json

cat > s3-update.json << 'EOF'
{
  "BufferingHints": {
    "SizeInMBs": 10,
    "IntervalInSeconds": 600
  },
  "CompressionFormat": "SNAPPY"
}
EOF

# Delete delivery stream
aws firehose delete-delivery-stream \
    --delivery-stream-name my-s3-delivery-stream
```

### Put Records to Firehose

```bash
# Put single record
aws firehose put-record \
    --delivery-stream-name my-s3-delivery-stream \
    --record '{"Data":"eyJ1c2VyIjoiam9obiIsImFjdGlvbiI6ImxvZ2luIn0="}'

# Put record with inline data
echo -n '{"user":"alice","event":"purchase"}' | base64 | \
    xargs -I {} aws firehose put-record \
    --delivery-stream-name my-s3-delivery-stream \
    --record Data={}

# Put records in batch
aws firehose put-record-batch \
    --delivery-stream-name my-s3-delivery-stream \
    --records file://firehose-records.json

cat > firehose-records.json << 'EOF'
[
  {"Data": "eyJ1c2VyIjoiYWxpY2UifQ=="},
  {"Data": "eyJ1c2VyIjoiYm9iIn0="},
  {"Data": "eyJ1c2VyIjoiY2hhcmxpZSJ9"}
]
EOF
```

### Firehose Tags

```bash
# Tag delivery stream
aws firehose tag-delivery-stream \
    --delivery-stream-name my-s3-delivery-stream \
    --tags Key=Environment,Value=Production Key=Application,Value=Analytics

# List tags
aws firehose list-tags-for-delivery-stream \
    --delivery-stream-name my-s3-delivery-stream

# Untag delivery stream
aws firehose untag-delivery-stream \
    --delivery-stream-name my-s3-delivery-stream \
    --tag-keys Environment
```

---

## Kinesis Data Analytics

### Create Analytics Applications

#### Create SQL Application

```bash
# Create Kinesis Data Analytics SQL application
aws kinesisanalyticsv2 create-application \
    --application-name my-analytics-app \
    --runtime-environment SQL-1_0 \
    --service-execution-role arn:aws:iam::123456789012:role/KinesisAnalyticsRole \
    --application-configuration file://analytics-config.json

cat > analytics-config.json << 'EOF'
{
  "SqlApplicationConfiguration": {
    "Inputs": [
      {
        "NamePrefix": "SOURCE_SQL_STREAM",
        "KinesisStreamsInput": {
          "ResourceARN": "arn:aws:kinesis:us-east-1:123456789012:stream/my-data-stream"
        },
        "InputSchema": {
          "RecordFormat": {
            "RecordFormatType": "JSON",
            "MappingParameters": {
              "JSONMappingParameters": {
                "RecordRowPath": "$"
              }
            }
          },
          "RecordColumns": [
            {
              "Name": "user_id",
              "Mapping": "$.user_id",
              "SqlType": "VARCHAR(64)"
            },
            {
              "Name": "event_time",
              "Mapping": "$.event_time",
              "SqlType": "TIMESTAMP"
            },
            {
              "Name": "value",
              "Mapping": "$.value",
              "SqlType": "DOUBLE"
            }
          ]
        }
      }
    ]
  },
  "ApplicationCodeConfiguration": {
    "CodeContent": {
      "TextContent": "CREATE OR REPLACE STREAM \"DESTINATION_SQL_STREAM\" (user_id VARCHAR(64), event_count BIGINT); CREATE OR REPLACE PUMP \"STREAM_PUMP\" AS INSERT INTO \"DESTINATION_SQL_STREAM\" SELECT STREAM user_id, COUNT(*) AS event_count FROM \"SOURCE_SQL_STREAM_001\" GROUP BY user_id, STEP(\"SOURCE_SQL_STREAM_001\".ROWTIME BY INTERVAL '60' SECOND);"
    },
    "CodeContentType": "PLAINTEXT"
  }
}
EOF
```

#### Create Flink Application

```bash
# Create Kinesis Data Analytics Flink application
aws kinesisanalyticsv2 create-application \
    --application-name my-flink-app \
    --runtime-environment FLINK-1_15 \
    --service-execution-role arn:aws:iam::123456789012:role/KinesisAnalyticsRole \
    --application-configuration file://flink-config.json

cat > flink-config.json << 'EOF'
{
  "FlinkApplicationConfiguration": {
    "CheckpointConfiguration": {
      "ConfigurationType": "CUSTOM",
      "CheckpointingEnabled": true,
      "CheckpointInterval": 60000,
      "MinPauseBetweenCheckpoints": 5000
    },
    "MonitoringConfiguration": {
      "ConfigurationType": "CUSTOM",
      "MetricsLevel": "APPLICATION",
      "LogLevel": "INFO"
    },
    "ParallelismConfiguration": {
      "ConfigurationType": "CUSTOM",
      "Parallelism": 2,
      "ParallelismPerKPU": 1,
      "AutoScalingEnabled": true
    }
  },
  "ApplicationCodeConfiguration": {
    "CodeContent": {
      "S3ContentLocation": {
        "BucketARN": "arn:aws:s3:::my-flink-code-bucket",
        "FileKey": "flink-app.jar"
      }
    },
    "CodeContentType": "ZIPFILE"
  }
}
EOF
```

### Manage Analytics Applications

```bash
# Describe application
aws kinesisanalyticsv2 describe-application \
    --application-name my-analytics-app

# List applications
aws kinesisanalyticsv2 list-applications

# Start application
aws kinesisanalyticsv2 start-application \
    --application-name my-analytics-app \
    --run-configuration '{"SqlRunConfigurations":[]}'

# Start Flink application
aws kinesisanalyticsv2 start-application \
    --application-name my-flink-app \
    --run-configuration '{"FlinkRunConfiguration":{"AllowNonRestoredState":false}}'

# Stop application
aws kinesisanalyticsv2 stop-application \
    --application-name my-analytics-app

# Update application
aws kinesisanalyticsv2 update-application \
    --application-name my-analytics-app \
    --current-application-version-id 1 \
    --application-configuration-update file://app-update.json

# Delete application
aws kinesisanalyticsv2 delete-application \
    --application-name my-analytics-app \
    --create-timestamp "2026-02-08T12:00:00Z"
```

### Add Application Outputs

```bash
# Add output to Kinesis Stream
aws kinesisanalyticsv2 add-application-output \
    --application-name my-analytics-app \
    --current-application-version-id 1 \
    --output file://output-config.json

cat > output-config.json << 'EOF'
{
  "Name": "DESTINATION_STREAM",
  "KinesisStreamsOutput": {
    "ResourceARN": "arn:aws:kinesis:us-east-1:123456789012:stream/output-stream"
  },
  "DestinationSchema": {
    "RecordFormatType": "JSON"
  }
}
EOF

# Add Lambda output
aws kinesisanalyticsv2 add-application-output \
    --application-name my-analytics-app \
    --current-application-version-id 1 \
    --output file://lambda-output.json

cat > lambda-output.json << 'EOF'
{
  "Name": "LAMBDA_OUTPUT",
  "LambdaOutput": {
    "ResourceARN": "arn:aws:lambda:us-east-1:123456789012:function:ProcessAnalyticsOutput"
  },
  "DestinationSchema": {
    "RecordFormatType": "JSON"
  }
}
EOF
```

### Application Snapshots

```bash
# Create application snapshot
aws kinesisanalyticsv2 create-application-snapshot \
    --application-name my-flink-app \
    --snapshot-name my-snapshot-001

# List snapshots
aws kinesisanalyticsv2 list-application-snapshots \
    --application-name my-flink-app

# Describe snapshot
aws kinesisanalyticsv2 describe-application-snapshot \
    --application-name my-flink-app \
    --snapshot-name my-snapshot-001

# Delete snapshot
aws kinesisanalyticsv2 delete-application-snapshot \
    --application-name my-flink-app \
    --snapshot-name my-snapshot-001 \
    --snapshot-creation-timestamp "2026-02-08T12:00:00Z"
```

### Application Tags

```bash
# Tag application
aws kinesisanalyticsv2 tag-resource \
    --resource-arn arn:aws:kinesisanalytics:us-east-1:123456789012:application/my-analytics-app \
    --tags Key=Environment,Value=Production,Key=Team,Value=DataEngineering

# List tags
aws kinesisanalyticsv2 list-tags-for-resource \
    --resource-arn arn:aws:kinesisanalytics:us-east-1:123456789012:application/my-analytics-app

# Untag application
aws kinesisanalyticsv2 untag-resource \
    --resource-arn arn:aws:kinesisanalytics:us-east-1:123456789012:application/my-analytics-app \
    --tag-keys Environment
```

---

## Practice Questions

### Question 1
A company needs to collect clickstream data from their website and store it in S3 for analysis. The solution should require minimal operational overhead. Which service should they use?

A) Kinesis Data Streams with Lambda to S3  
B) Kinesis Data Firehose to S3  
C) Amazon SQS to Lambda to S3  
D) Direct PUT to S3 from website  

**Answer: B** - Firehose provides fully managed delivery to S3 with minimal operational overhead.

### Question 2
An application needs to process streaming data with multiple consumer applications, each requiring dedicated throughput. Which feature should be used?

A) Kinesis Data Streams Standard consumers  
B) Kinesis Data Firehose  
C) Kinesis Data Streams Enhanced Fan-Out  
D) Amazon SQS with multiple queues  

**Answer: C** - Enhanced Fan-Out provides dedicated 2 MB/s throughput per consumer.

### Question 3
A company needs to analyze streaming data using SQL queries to detect anomalies in real-time. Which service is MOST appropriate?

A) Amazon Athena  
B) Kinesis Data Analytics  
C) Amazon Redshift  
D) Amazon EMR  

**Answer: B** - Kinesis Data Analytics supports SQL queries on streaming data with built-in anomaly detection.

### Question 4
A Kinesis Data Stream has 4 shards. What is the maximum read throughput for standard consumers?

A) 2 MB/s  
B) 4 MB/s  
C) 8 MB/s  
D) 16 MB/s  

**Answer: C** - Each shard provides 2 MB/s read throughput, so 4 shards = 8 MB/s total (shared among all standard consumers).

### Question 5
A company needs to load streaming data into Amazon Redshift with data transformation. Which is the BEST approach?

A) Kinesis Data Streams to Lambda to Redshift  
B) Kinesis Data Firehose with Lambda transformation to Redshift  
C) Kinesis Data Streams directly to Redshift  
D) Amazon SQS to Lambda to Redshift  

**Answer: B** - Firehose supports Lambda transformation and native Redshift destination (via S3 staging).

---

## Summary

Amazon Kinesis provides a comprehensive platform for streaming data:

- **Data Streams**: Real-time, custom consumers, data replay
- **Firehose**: Managed delivery to destinations
- **Data Analytics**: SQL/Flink processing
- **Video Streams**: Video ingestion and processing

**Key Decision Points**:
1. Need custom processing → Data Streams
2. Need managed delivery → Firehose
3. Need SQL analytics → Data Analytics
4. Need data replay → Data Streams
5. Multiple high-throughput consumers → Enhanced Fan-Out

Remember: Firehose can source FROM Data Streams, creating powerful pipelines that combine real-time processing with managed delivery.
