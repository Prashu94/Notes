# Google Cloud Dataflow - ACE & PCA Comprehensive Guide

## Table of Contents
1. [Overview](#overview)
2. [Apache Beam Programming Model](#apache-beam-programming-model)
3. [Dataflow Architecture](#dataflow-architecture)
4. [Pipeline Development](#pipeline-development)
5. [Batch Processing](#batch-processing)
6. [Stream Processing](#stream-processing)
7. [Windowing and Triggers](#windowing-and-triggers)
8. [Templates](#templates)
9. [Performance Optimization](#performance-optimization)
10. [Monitoring and Debugging](#monitoring-and-debugging)
11. [Security and Networking](#security-and-networking)
12. [Cost Management](#cost-management)
13. [ACE Exam Focus](#ace-exam-focus)
14. [PCA Exam Focus](#pca-exam-focus)

---

## Overview

### What is Dataflow?

Cloud Dataflow is a fully managed service for executing Apache Beam pipelines for batch and stream data processing. It provides:
- **Unified batch and streaming**: Same code for both processing modes
- **Autoscaling**: Automatically adjusts workers based on workload
- **Serverless**: No infrastructure management
- **Integration**: Native connectors for GCP services

### Key Features

| Feature | Description |
|---------|-------------|
| **Unified Model** | Same API for batch and streaming |
| **Autoscaling** | Dynamic worker allocation |
| **Horizontal Scaling** | Massive parallelism |
| **Exactly-once Processing** | Guaranteed delivery for streaming |
| **Flexible Execution** | Run on-prem or in cloud |
| **Managed Service** | No cluster management |

### Dataflow vs Other Processing Services

| Service | Best For | Processing Type |
|---------|----------|-----------------|
| **Dataflow** | Complex transformations, streaming | Batch & Stream |
| **Dataproc** | Spark/Hadoop workloads | Batch |
| **BigQuery** | SQL-based analysis | Batch & Stream (limited) |
| **Pub/Sub** | Message routing (no processing) | Stream |
| **Cloud Functions** | Simple event-driven tasks | Event-based |

---

## Apache Beam Programming Model

### Core Concepts

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     APACHE BEAM PIPELINE MODEL                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐        │
│   │  SOURCE  │───►│TRANSFORM │───►│TRANSFORM │───►│   SINK   │        │
│   │ (Read)   │    │ (Map)    │    │ (Group)  │    │ (Write)  │        │
│   └──────────┘    └──────────┘    └──────────┘    └──────────┘        │
│        │               │               │               │               │
│        ▼               ▼               ▼               ▼               │
│   PCollection    PCollection    PCollection    PCollection            │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Pipeline Components

| Component | Description |
|-----------|-------------|
| **Pipeline** | Encapsulates the entire data processing task |
| **PCollection** | Distributed dataset (potentially unbounded) |
| **Transform** | Data processing operation |
| **PTransform** | Reusable transformation |
| **Runner** | Execution engine (DataflowRunner, DirectRunner) |

### Basic Pipeline Structure

```python
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions

# Define pipeline options
options = PipelineOptions(
    project='my-project',
    region='us-central1',
    runner='DataflowRunner',
    temp_location='gs://my-bucket/temp',
    staging_location='gs://my-bucket/staging'
)

# Create pipeline
with beam.Pipeline(options=options) as pipeline:
    # Read -> Transform -> Write
    (
        pipeline
        | 'Read' >> beam.io.ReadFromText('gs://input/data.txt')
        | 'Transform' >> beam.Map(lambda x: x.upper())
        | 'Write' >> beam.io.WriteToText('gs://output/results')
    )
```

### Core Transforms

#### ParDo (Parallel Do)

```python
class ProcessElement(beam.DoFn):
    def process(self, element):
        # Process each element
        words = element.split()
        for word in words:
            yield word.lower()

# Usage
result = input_pcollection | beam.ParDo(ProcessElement())
```

#### Map (1:1 transformation)

```python
# Simple transformation
result = input | beam.Map(lambda x: x.upper())

# With side inputs
def multiply(element, factor):
    return element * factor

factor = pipeline | beam.Create([10])
result = input | beam.Map(multiply, factor=beam.pvalue.AsSingleton(factor))
```

#### FlatMap (1:many transformation)

```python
# Split into multiple elements
result = input | beam.FlatMap(lambda x: x.split())
```

#### Filter

```python
# Keep elements matching condition
result = input | beam.Filter(lambda x: x > 100)
```

#### GroupByKey

```python
# Group by key
# Input: [('a', 1), ('b', 2), ('a', 3)]
# Output: [('a', [1, 3]), ('b', [2])]
result = input | beam.GroupByKey()
```

#### CoGroupByKey (Join)

```python
# Join multiple PCollections
emails = p | beam.Create([('user1', 'a@email.com'), ('user2', 'b@email.com')])
phones = p | beam.Create([('user1', '555-1234'), ('user2', '555-5678')])

joined = {'emails': emails, 'phones': phones} | beam.CoGroupByKey()
# Output: [('user1', {'emails': ['a@email.com'], 'phones': ['555-1234']}), ...]
```

#### Combine

```python
# Global combine
total = input | beam.CombineGlobally(sum)

# Per-key combine
totals_by_key = input | beam.CombinePerKey(sum)

# Custom combiner
class AverageFn(beam.CombineFn):
    def create_accumulator(self):
        return (0, 0)  # (sum, count)
    
    def add_input(self, accumulator, input):
        sum_val, count = accumulator
        return (sum_val + input, count + 1)
    
    def merge_accumulators(self, accumulators):
        sums, counts = zip(*accumulators)
        return (sum(sums), sum(counts))
    
    def extract_output(self, accumulator):
        sum_val, count = accumulator
        return sum_val / count if count else 0

average = input | beam.CombineGlobally(AverageFn())
```

---

## Dataflow Architecture

### Execution Model

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      DATAFLOW EXECUTION                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                     DATAFLOW SERVICE                             │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │   │
│  │  │   Graph     │  │  Resource   │  │   Worker    │             │   │
│  │  │ Optimizer   │  │  Manager    │  │  Scheduler  │             │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘             │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                │                                         │
│                                ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      WORKER POOL                                 │   │
│  │                                                                   │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │   │
│  │  │ Worker 1 │  │ Worker 2 │  │ Worker 3 │  │ Worker N │        │   │
│  │  │  ┌────┐  │  │  ┌────┐  │  │  ┌────┐  │  │  ┌────┐  │        │   │
│  │  │  │Task│  │  │  │Task│  │  │  │Task│  │  │  │Task│  │        │   │
│  │  │  └────┘  │  │  └────┘  │  │  └────┘  │  │  └────┘  │        │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │   │
│  │                                                                   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Worker Configuration

```python
from apache_beam.options.pipeline_options import (
    PipelineOptions,
    GoogleCloudOptions,
    WorkerOptions
)

options = PipelineOptions()

# Google Cloud options
google_options = options.view_as(GoogleCloudOptions)
google_options.project = 'my-project'
google_options.region = 'us-central1'
google_options.temp_location = 'gs://bucket/temp'
google_options.staging_location = 'gs://bucket/staging'

# Worker options
worker_options = options.view_as(WorkerOptions)
worker_options.machine_type = 'n1-standard-4'
worker_options.num_workers = 5
worker_options.max_num_workers = 100
worker_options.disk_size_gb = 100
worker_options.disk_type = 'pd-ssd'
worker_options.network = 'my-vpc'
worker_options.subnetwork = 'regions/us-central1/subnetworks/my-subnet'
worker_options.use_public_ips = False
```

### Shuffle Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| **Default Shuffle** | Worker-based shuffle | Small to medium data |
| **Dataflow Shuffle** | Service-based shuffle | Large-scale processing |

```python
# Enable Dataflow Shuffle
options = PipelineOptions([
    '--experiments=shuffle_mode=service'
])
```

---

## Pipeline Development

### Pipeline Options

```python
from apache_beam.options.pipeline_options import PipelineOptions

# Command-line style options
options = PipelineOptions([
    '--project=my-project',
    '--region=us-central1',
    '--runner=DataflowRunner',
    '--temp_location=gs://bucket/temp',
    '--staging_location=gs://bucket/staging',
    '--job_name=my-job',
    '--max_num_workers=50',
    '--machine_type=n1-standard-4',
    '--experiments=shuffle_mode=service'
])

# Or programmatic style
options = PipelineOptions()
options.view_as(GoogleCloudOptions).project = 'my-project'
```

### Custom Pipeline Options

```python
from apache_beam.options.pipeline_options import PipelineOptions

class MyOptions(PipelineOptions):
    @classmethod
    def _add_argparse_args(cls, parser):
        parser.add_argument('--input', required=True, help='Input path')
        parser.add_argument('--output', required=True, help='Output path')
        parser.add_argument('--threshold', type=int, default=100)

# Usage
options = PipelineOptions()
my_options = options.view_as(MyOptions)
print(f"Input: {my_options.input}")
```

### I/O Connectors

#### Cloud Storage

```python
# Read text files
lines = p | beam.io.ReadFromText('gs://bucket/input/*.txt')

# Read with pattern
lines = p | beam.io.ReadFromText(
    'gs://bucket/input/*.txt',
    skip_header_lines=1
)

# Write text files
output | beam.io.WriteToText(
    'gs://bucket/output/results',
    file_name_suffix='.txt',
    num_shards=10
)
```

#### BigQuery

```python
# Read from BigQuery
rows = p | beam.io.ReadFromBigQuery(
    query='SELECT * FROM `project.dataset.table` WHERE date > "2024-01-01"',
    use_standard_sql=True
)

# Or from table directly
rows = p | beam.io.ReadFromBigQuery(
    table='project:dataset.table'
)

# Write to BigQuery
rows | beam.io.WriteToBigQuery(
    table='project:dataset.table',
    schema='name:STRING,count:INTEGER',
    create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
    write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND
)

# Write with dynamic destinations
def get_table(element):
    return f'project:dataset.table_{element["region"]}'

rows | beam.io.WriteToBigQuery(
    table=get_table,
    schema='name:STRING,count:INTEGER'
)
```

#### Pub/Sub

```python
# Read from Pub/Sub
messages = p | beam.io.ReadFromPubSub(
    subscription='projects/my-project/subscriptions/my-sub'
)

# Or from topic
messages = p | beam.io.ReadFromPubSub(
    topic='projects/my-project/topics/my-topic'
)

# Write to Pub/Sub
messages | beam.io.WriteToPubSub(
    topic='projects/my-project/topics/output-topic'
)
```

#### Avro/Parquet

```python
# Read Avro
records = p | beam.io.ReadFromAvro('gs://bucket/data/*.avro')

# Write Parquet
records | beam.io.WriteToParquet(
    'gs://bucket/output/data',
    schema=pyarrow_schema,
    file_name_suffix='.parquet'
)
```

---

## Batch Processing

### Word Count Example

```python
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions

def run():
    options = PipelineOptions([
        '--runner=DataflowRunner',
        '--project=my-project',
        '--region=us-central1',
        '--temp_location=gs://my-bucket/temp'
    ])
    
    with beam.Pipeline(options=options) as p:
        (
            p
            | 'Read' >> beam.io.ReadFromText('gs://dataflow-samples/shakespeare/*')
            | 'Split' >> beam.FlatMap(lambda line: line.split())
            | 'FilterEmpty' >> beam.Filter(lambda word: len(word) > 0)
            | 'PairWithOne' >> beam.Map(lambda word: (word.lower(), 1))
            | 'GroupAndSum' >> beam.CombinePerKey(sum)
            | 'Format' >> beam.Map(lambda kv: f'{kv[0]}: {kv[1]}')
            | 'Write' >> beam.io.WriteToText('gs://my-bucket/output/counts')
        )

if __name__ == '__main__':
    run()
```

### ETL Pipeline Example

```python
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions

class ParseCSV(beam.DoFn):
    def process(self, line):
        import csv
        from io import StringIO
        
        reader = csv.reader(StringIO(line))
        for row in reader:
            yield {
                'user_id': row[0],
                'timestamp': row[1],
                'event_type': row[2],
                'value': float(row[3])
            }

class FilterAndEnrich(beam.DoFn):
    def __init__(self, min_value):
        self.min_value = min_value
    
    def process(self, element):
        if element['value'] >= self.min_value:
            element['processed_at'] = datetime.now().isoformat()
            element['category'] = 'high' if element['value'] > 100 else 'medium'
            yield element

def run():
    options = PipelineOptions()
    
    with beam.Pipeline(options=options) as p:
        # Read raw data
        raw_data = p | 'Read CSV' >> beam.io.ReadFromText(
            'gs://input/events/*.csv',
            skip_header_lines=1
        )
        
        # Parse and transform
        parsed = raw_data | 'Parse' >> beam.ParDo(ParseCSV())
        
        # Filter and enrich
        enriched = parsed | 'FilterEnrich' >> beam.ParDo(FilterAndEnrich(10))
        
        # Aggregate by user
        aggregated = (
            enriched
            | 'ExtractUserValue' >> beam.Map(lambda x: (x['user_id'], x['value']))
            | 'SumByUser' >> beam.CombinePerKey(sum)
        )
        
        # Write to BigQuery
        enriched | 'WriteEvents' >> beam.io.WriteToBigQuery(
            'project:dataset.events',
            schema='user_id:STRING,timestamp:STRING,event_type:STRING,value:FLOAT,processed_at:STRING,category:STRING',
            create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
            write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND
        )
        
        aggregated | 'WriteAggregated' >> beam.io.WriteToBigQuery(
            'project:dataset.user_totals',
            schema='user_id:STRING,total_value:FLOAT',
            create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
            write_disposition=beam.io.BigQueryDisposition.WRITE_TRUNCATE
        )

if __name__ == '__main__':
    run()
```

---

## Stream Processing

### Streaming Pipeline Basics

```python
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions

def run():
    options = PipelineOptions()
    options.view_as(StandardOptions).streaming = True
    
    with beam.Pipeline(options=options) as p:
        (
            p
            | 'Read from Pub/Sub' >> beam.io.ReadFromPubSub(
                subscription='projects/my-project/subscriptions/input-sub'
            )
            | 'Decode' >> beam.Map(lambda x: x.decode('utf-8'))
            | 'Parse JSON' >> beam.Map(json.loads)
            | 'Process' >> beam.Map(process_event)
            | 'Format' >> beam.Map(json.dumps)
            | 'Encode' >> beam.Map(lambda x: x.encode('utf-8'))
            | 'Write to Pub/Sub' >> beam.io.WriteToPubSub(
                topic='projects/my-project/topics/output-topic'
            )
        )
```

### Streaming with BigQuery

```python
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions

def run():
    options = PipelineOptions()
    options.view_as(StandardOptions).streaming = True
    
    with beam.Pipeline(options=options) as p:
        events = (
            p
            | 'Read' >> beam.io.ReadFromPubSub(
                subscription='projects/my-project/subscriptions/events'
            )
            | 'Parse' >> beam.Map(json.loads)
        )
        
        # Write streaming inserts to BigQuery
        events | 'WriteStreaming' >> beam.io.WriteToBigQuery(
            'project:dataset.events',
            schema='timestamp:TIMESTAMP,user_id:STRING,event:STRING',
            method=beam.io.WriteToBigQuery.Method.STREAMING_INSERTS
        )
```

---

## Windowing and Triggers

### Window Types

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         WINDOW TYPES                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  FIXED WINDOWS (Tumbling)                                               │
│  ┌────────┐┌────────┐┌────────┐┌────────┐                              │
│  │ 0-10s  ││ 10-20s ││ 20-30s ││ 30-40s │                              │
│  └────────┘└────────┘└────────┘└────────┘                              │
│                                                                          │
│  SLIDING WINDOWS                                                        │
│  ┌──────────────┐                                                       │
│  │ 0-10s        │                                                       │
│  └──────────────┘                                                       │
│       ┌──────────────┐                                                  │
│       │ 5-15s        │                                                  │
│       └──────────────┘                                                  │
│            ┌──────────────┐                                             │
│            │ 10-20s       │                                             │
│            └──────────────┘                                             │
│                                                                          │
│  SESSION WINDOWS (Gap-based)                                            │
│  ┌─────────┐    ┌──────────────────┐   ┌────┐                          │
│  │Session 1│    │    Session 2     │   │ S3 │                          │
│  └─────────┘    └──────────────────┘   └────┘                          │
│                                                                          │
│  GLOBAL WINDOW (No windowing)                                           │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │                    Single Global Window                         │    │
│  └────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Implementing Windows

```python
import apache_beam as beam
from apache_beam import window

# Fixed windows (10-minute windows)
windowed = (
    events
    | 'FixedWindow' >> beam.WindowInto(window.FixedWindows(600))  # 600 seconds
    | 'CountPerWindow' >> beam.combiners.Count.Globally()
)

# Sliding windows (10-minute window, 5-minute slide)
windowed = (
    events
    | 'SlidingWindow' >> beam.WindowInto(
        window.SlidingWindows(size=600, period=300)
    )
    | 'CountPerWindow' >> beam.combiners.Count.Globally()
)

# Session windows (30-minute gap)
windowed = (
    events
    | 'SessionWindow' >> beam.WindowInto(
        window.Sessions(gap_size=1800)  # 1800 seconds
    )
    | 'CountPerSession' >> beam.combiners.Count.Globally()
)
```

### Triggers

```python
from apache_beam import trigger

# Default trigger (at watermark)
events | beam.WindowInto(
    window.FixedWindows(60),
    trigger=trigger.AfterWatermark()
)

# Early and late firings
events | beam.WindowInto(
    window.FixedWindows(60),
    trigger=trigger.AfterWatermark(
        early=trigger.AfterProcessingTime(30),  # Fire every 30s before watermark
        late=trigger.AfterCount(1)  # Fire on each late element
    ),
    accumulation_mode=trigger.AccumulationMode.ACCUMULATING
)

# Repeated trigger (every 10 elements)
events | beam.WindowInto(
    window.FixedWindows(60),
    trigger=trigger.Repeatedly(trigger.AfterCount(10))
)
```

### Watermarks and Late Data

```python
# Handle late data with allowed lateness
events | beam.WindowInto(
    window.FixedWindows(60),
    trigger=trigger.AfterWatermark(late=trigger.AfterCount(1)),
    allowed_lateness=3600,  # Accept data up to 1 hour late
    accumulation_mode=trigger.AccumulationMode.ACCUMULATING
)
```

### Accumulation Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| **DISCARDING** | Each pane has only new elements | Incremental updates |
| **ACCUMULATING** | Each pane has all elements | Full aggregations |

---

## Templates

### Classic Templates

Create reusable pipeline templates:

```python
from apache_beam.options.pipeline_options import PipelineOptions

class MyOptions(PipelineOptions):
    @classmethod
    def _add_argparse_args(cls, parser):
        parser.add_value_provider_argument(
            '--input',
            help='Input path'
        )
        parser.add_value_provider_argument(
            '--output',
            help='Output path'
        )

def run():
    options = PipelineOptions()
    my_options = options.view_as(MyOptions)
    
    with beam.Pipeline(options=options) as p:
        (
            p
            | beam.io.ReadFromText(my_options.input)
            | beam.Map(str.upper)
            | beam.io.WriteToText(my_options.output)
        )
```

```bash
# Create template
python my_pipeline.py \
    --runner=DataflowRunner \
    --project=my-project \
    --region=us-central1 \
    --staging_location=gs://bucket/staging \
    --temp_location=gs://bucket/temp \
    --template_location=gs://bucket/templates/my-template

# Run template
gcloud dataflow jobs run my-job \
    --gcs-location=gs://bucket/templates/my-template \
    --parameters input=gs://input/data.txt,output=gs://output/results
```

### Flex Templates

More flexible templates using Docker containers:

```python
# pipeline.py
import argparse
import apache_beam as beam

def run(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    args, pipeline_args = parser.parse_known_args(argv)
    
    with beam.Pipeline(argv=pipeline_args) as p:
        (
            p
            | beam.io.ReadFromText(args.input)
            | beam.Map(str.upper)
            | beam.io.WriteToText(args.output)
        )

if __name__ == '__main__':
    run()
```

```dockerfile
# Dockerfile
FROM gcr.io/dataflow-templates-base/python39-template-launcher-base

ENV FLEX_TEMPLATE_PYTHON_PY_FILE="/template/pipeline.py"
COPY pipeline.py /template/
COPY requirements.txt /template/

RUN pip install -r /template/requirements.txt
```

```bash
# Build and push container
docker build -t gcr.io/my-project/my-template:latest .
docker push gcr.io/my-project/my-template:latest

# Create Flex Template
gcloud dataflow flex-template build gs://bucket/templates/my-flex-template.json \
    --image=gcr.io/my-project/my-template:latest \
    --sdk-language=PYTHON \
    --metadata-file=metadata.json

# Run Flex Template
gcloud dataflow flex-template run my-job \
    --template-file-gcs-location=gs://bucket/templates/my-flex-template.json \
    --parameters input=gs://input/data.txt,output=gs://output/results \
    --region=us-central1
```

### Google-Provided Templates

```bash
# List available templates
gcloud dataflow jobs list --status=JOB_STATE_RUNNING

# Common templates:
# - Word_Count
# - Cloud_PubSub_to_BigQuery
# - Cloud_Storage_Text_to_BigQuery
# - Cloud_Spanner_to_GCS_Avro
# - Bulk_Compress_GCS_Files
# - Stream_Pub/Sub_to_BigQuery

# Run a Google template
gcloud dataflow jobs run pubsub-to-bq \
    --gcs-location=gs://dataflow-templates/latest/PubSub_to_BigQuery \
    --parameters \
        inputTopic=projects/my-project/topics/my-topic,\
        outputTableSpec=my-project:dataset.table
```

---

## Performance Optimization

### Key Optimization Techniques

#### 1. Efficient I/O

```python
# Use batch reads where possible
p | beam.io.ReadFromBigQuery(
    query='SELECT * FROM table',
    use_standard_sql=True,
    method=beam.io.ReadFromBigQuery.Method.DIRECT_READ  # Faster
)

# Use streaming inserts for real-time
output | beam.io.WriteToBigQuery(
    table='project:dataset.table',
    method=beam.io.WriteToBigQuery.Method.STREAMING_INSERTS
)

# Or use file loads for batch (cheaper)
output | beam.io.WriteToBigQuery(
    table='project:dataset.table',
    method=beam.io.WriteToBigQuery.Method.FILE_LOADS
)
```

#### 2. Combiner Optimization

```python
# Bad: GroupByKey + reduce
(
    input
    | beam.GroupByKey()
    | beam.Map(lambda kv: (kv[0], sum(kv[1])))  # All values in memory
)

# Good: CombinePerKey (incremental)
input | beam.CombinePerKey(sum)
```

#### 3. Fusion Prevention

```python
# Force a shuffle to enable parallelism
(
    input
    | 'Reshuffle' >> beam.Reshuffle()  # Break fusion
    | 'HeavyProcess' >> beam.ParDo(ExpensiveDoFn())
)
```

#### 4. Side Inputs

```python
# Small side input (in-memory)
lookup_data = p | beam.io.ReadFromText('gs://bucket/lookup.txt')
lookup_dict = beam.pvalue.AsDict(
    lookup_data | beam.Map(lambda x: (x.split(',')[0], x.split(',')[1]))
)

main_data | beam.Map(
    lambda element, lookup: lookup.get(element['key'], 'unknown'),
    lookup=lookup_dict
)
```

### Worker Configuration

```python
options = PipelineOptions([
    # Machine type
    '--machine_type=n1-standard-4',  # or n1-highmem-4 for memory-intensive
    
    # Worker count
    '--num_workers=10',
    '--max_num_workers=100',
    
    # Autoscaling
    '--autoscaling_algorithm=THROUGHPUT_BASED',
    
    # Disk
    '--disk_size_gb=100',
    '--disk_type=pd-ssd',  # SSD for I/O intensive
    
    # Shuffle service
    '--experiments=shuffle_mode=service',
    
    # Streaming engine
    '--enable_streaming_engine'  # For streaming pipelines
])
```

---

## Monitoring and Debugging

### Cloud Console Monitoring

```bash
# View job details
gcloud dataflow jobs describe JOB_ID --region=us-central1

# List jobs
gcloud dataflow jobs list --region=us-central1 --status=JOB_STATE_RUNNING

# Cancel job
gcloud dataflow jobs cancel JOB_ID --region=us-central1

# Drain streaming job (graceful shutdown)
gcloud dataflow jobs drain JOB_ID --region=us-central1
```

### Key Metrics

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| `system_lag` | Time behind real-time | > 5 minutes |
| `data_watermark_age` | Watermark delay | > 10 minutes |
| `backlog_bytes` | Unprocessed data | Increasing trend |
| `cpu_utilization` | Worker CPU usage | > 80% sustained |
| `memory_utilization` | Worker memory usage | > 80% |

### Logging

```python
import logging

class MyDoFn(beam.DoFn):
    def process(self, element):
        logging.info(f'Processing: {element}')
        try:
            result = transform(element)
            logging.debug(f'Result: {result}')
            yield result
        except Exception as e:
            logging.error(f'Error processing {element}: {e}')
            # Optionally output to dead-letter queue
```

```bash
# View logs
gcloud logging read 'resource.type="dataflow_step" AND resource.labels.job_id="JOB_ID"' \
    --limit=100
```

### Debugging Techniques

```python
# Use DirectRunner for local testing
options = PipelineOptions(['--runner=DirectRunner'])

# Add assertions
class ValidateDoFn(beam.DoFn):
    def process(self, element):
        assert element['count'] >= 0, f"Invalid count: {element}"
        yield element

# Sample data for testing
sampled = input | beam.combiners.Sample.FixedSizeGlobally(100)
```

---

## Security and Networking

### VPC Network Configuration

```python
options = PipelineOptions([
    '--network=my-vpc',
    '--subnetwork=regions/us-central1/subnetworks/my-subnet',
    '--use_public_ips=false',  # No public IPs (requires Cloud NAT)
    '--service_account_email=dataflow-sa@my-project.iam.gserviceaccount.com'
])
```

### IAM Roles

| Role | Description |
|------|-------------|
| `roles/dataflow.developer` | Create and manage jobs |
| `roles/dataflow.worker` | Worker service account |
| `roles/dataflow.viewer` | View jobs and metrics |
| `roles/dataflow.admin` | Full control |

### Service Account Configuration

```bash
# Create service account
gcloud iam service-accounts create dataflow-worker \
    --display-name="Dataflow Worker"

# Grant worker role
gcloud projects add-iam-policy-binding my-project \
    --member="serviceAccount:dataflow-worker@my-project.iam.gserviceaccount.com" \
    --role="roles/dataflow.worker"

# Grant data access
gcloud projects add-iam-policy-binding my-project \
    --member="serviceAccount:dataflow-worker@my-project.iam.gserviceaccount.com" \
    --role="roles/bigquery.dataEditor"

gcloud projects add-iam-policy-binding my-project \
    --member="serviceAccount:dataflow-worker@my-project.iam.gserviceaccount.com" \
    --role="roles/storage.objectAdmin"
```

### CMEK Encryption

```python
options = PipelineOptions([
    '--dataflow_kms_key=projects/my-project/locations/us-central1/keyRings/my-ring/cryptoKeys/my-key'
])
```

---

## Cost Management

### Pricing Factors

| Factor | Impact |
|--------|--------|
| **Worker vCPUs** | Per vCPU/hour |
| **Worker Memory** | Per GB/hour |
| **Worker Disk** | Per GB/month |
| **Shuffle Service** | Per GB shuffled |
| **Streaming Engine** | Per GB processed |

### Cost Optimization Strategies

```python
# 1. Right-size workers
options = PipelineOptions([
    '--machine_type=n1-standard-2',  # Start small
    '--autoscaling_algorithm=THROUGHPUT_BASED',
    '--max_num_workers=50'  # Cap maximum
])

# 2. Use Dataflow Shuffle for large jobs
options = PipelineOptions([
    '--experiments=shuffle_mode=service'
])

# 3. Use Streaming Engine for streaming
options = PipelineOptions([
    '--enable_streaming_engine'
])

# 4. Use Flex RS (Flexible Resource Scheduling) for batch
options = PipelineOptions([
    '--flexrs_goal=COST_OPTIMIZED'
])
```

### Flex RS (Flexible Resource Scheduling)

```python
# For non-time-sensitive batch jobs
options = PipelineOptions([
    '--flexrs_goal=COST_OPTIMIZED',  # Use preemptible VMs, cheaper shuffle
    # Or
    '--flexrs_goal=SPEED_OPTIMIZED'  # Faster execution
])
```

---

## ACE Exam Focus

### Key Concepts for ACE

1. **Pipeline basics**: Read → Transform → Write
2. **Runners**: DataflowRunner vs DirectRunner
3. **I/O connectors**: GCS, BigQuery, Pub/Sub
4. **Basic transforms**: Map, Filter, GroupByKey
5. **Job management**: Start, cancel, drain

### Sample ACE Questions

**Q1:** You need to process data from Cloud Storage, transform it, and load it into BigQuery. What service should you use?
- **A:** Cloud Dataflow with Apache Beam

**Q2:** How do you gracefully stop a streaming Dataflow job while ensuring all in-flight data is processed?
- **A:** Use `gcloud dataflow jobs drain JOB_ID`

**Q3:** What is the difference between batch and streaming pipelines in Dataflow?
- **A:** 
  - Batch: Processes bounded data, finite execution
  - Streaming: Processes unbounded data, continuous execution, requires `--streaming` flag

### ACE gcloud Commands

```bash
# Run a job
gcloud dataflow jobs run my-job \
    --gcs-location=gs://bucket/template \
    --region=us-central1

# List jobs
gcloud dataflow jobs list --region=us-central1

# Describe job
gcloud dataflow jobs describe JOB_ID --region=us-central1

# Cancel job
gcloud dataflow jobs cancel JOB_ID --region=us-central1

# Drain streaming job
gcloud dataflow jobs drain JOB_ID --region=us-central1
```

---

## PCA Exam Focus

### Architecture Decisions

#### When to Use Dataflow

| Scenario | Dataflow | Alternative |
|----------|----------|-------------|
| Complex ETL | ✅ | BigQuery (simple SQL) |
| Real-time streaming | ✅ | Pub/Sub + Functions (simple) |
| ML preprocessing | ✅ | Dataproc (Spark ML) |
| Hadoop migration | Consider | Dataproc |
| SQL transformations | Consider | BigQuery |

### Sample PCA Questions

**Q1:** Design a real-time analytics pipeline that processes 100,000 events/second from IoT devices, enriches data with device metadata, aggregates metrics per minute, and stores results in BigQuery.

**A:**
```
IoT Devices → Pub/Sub → Dataflow Streaming Pipeline → BigQuery

Pipeline design:
1. Read from Pub/Sub subscription
2. Parse JSON messages
3. Window: Fixed 1-minute windows
4. Side input: Device metadata from Cloud Storage
5. Enrich: Join with device metadata
6. Aggregate: Count, sum, avg per device type
7. Write: Streaming inserts to BigQuery

Key configurations:
- --enable_streaming_engine
- --max_num_workers=50
- --experiments=shuffle_mode=service
- Autoscaling for traffic spikes
```

**Q2:** A data lake needs to process 10TB of daily log files, parse them, filter invalid records, and partition by date into BigQuery.

**A:**
```
GCS (logs) → Dataflow Batch → BigQuery (partitioned)

Pipeline:
1. Read: Glob pattern gs://logs/*/access.log.gz
2. Decompress: Automatic with Beam
3. Parse: Custom DoFn for log format
4. Filter: Remove invalid/test records
5. Transform: Extract fields, normalize
6. Write: BigQuery with date partitioning

Optimizations:
- --flexrs_goal=COST_OPTIMIZED (non-urgent)
- --experiments=shuffle_mode=service
- --machine_type=n1-highmem-4 (memory for parsing)
```

**Q3:** How would you implement exactly-once processing for a payment processing pipeline?

**A:**
- Dataflow provides exactly-once for Pub/Sub sources
- Use idempotent writes to BigQuery
- Enable checkpointing
- Use deterministic processing
- For external systems: implement deduplication or use transactions

### Streaming Architecture Pattern

```
┌─────────────────────────────────────────────────────────────┐
│                 STREAMING ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌─────────────┐                                           │
│   │   Sources   │                                           │
│   │  (Pub/Sub)  │                                           │
│   └──────┬──────┘                                           │
│          │                                                   │
│          ▼                                                   │
│   ┌─────────────────────────────────────────────────────┐  │
│   │              DATAFLOW STREAMING                      │  │
│   │  ┌─────────┐  ┌─────────┐  ┌─────────┐            │  │
│   │  │ Parse   │─►│ Enrich  │─►│ Window  │            │  │
│   │  └─────────┘  └─────────┘  └────┬────┘            │  │
│   │                                  │                  │  │
│   │                    ┌─────────────┴─────────────┐   │  │
│   │                    │                           │   │  │
│   │               ┌────▼────┐               ┌─────▼───┐│  │
│   │               │Aggregate│               │  Route  ││  │
│   │               └────┬────┘               └────┬────┘│  │
│   │                    │                         │     │  │
│   └────────────────────┼─────────────────────────┼─────┘  │
│                        │                         │         │
│          ┌─────────────┼─────────────┬───────────┘        │
│          ▼             ▼             ▼                     │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐               │
│   │ BigQuery │  │ Bigtable │  │ Pub/Sub  │               │
│   │(Analytics)│  │(Real-time)│  │(Alerts)  │               │
│   └──────────┘  └──────────┘  └──────────┘               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Summary

### Dataflow Capabilities

| Feature | ACE Focus | PCA Focus |
|---------|-----------|-----------|
| Batch processing | Basic pipelines | Complex ETL design |
| Stream processing | Awareness | Windowing, triggers, exactly-once |
| I/O connectors | GCS, BigQuery | All connectors, custom |
| Templates | Run Google templates | Create Flex templates |
| Performance | Basic | Optimization strategies |
| Monitoring | View jobs | Metrics, alerting, debugging |

### Key Decision Points

| Question | Answer |
|----------|--------|
| SQL-based transforms? | Use BigQuery |
| Existing Spark jobs? | Consider Dataproc |
| Complex transforms + streaming? | Use Dataflow |
| Simple event-driven? | Consider Cloud Functions |
| Need exactly-once? | Use Dataflow streaming |
