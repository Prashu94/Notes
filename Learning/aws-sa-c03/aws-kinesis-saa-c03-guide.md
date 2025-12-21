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
16. [Practice Questions](#practice-questions)

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
