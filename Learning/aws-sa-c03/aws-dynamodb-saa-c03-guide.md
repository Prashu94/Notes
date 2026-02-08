# AWS DynamoDB - SAA-C03 Study Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Core Concepts](#core-concepts)
3. [DynamoDB Architecture](#dynamodb-architecture)
4. [Data Types and Attributes](#data-types-and-attributes)
5. [Primary Keys](#primary-keys)
6. [Read and Write Operations](#read-and-write-operations)
7. [Consistency Models](#consistency-models)
8. [Capacity Management](#capacity-management)
9. [Global Secondary Indexes (GSI)](#global-secondary-indexes-gsi)
10. [Local Secondary Indexes (LSI)](#local-secondary-indexes-lsi)
11. [DynamoDB Streams](#dynamodb-streams)
12. [Global Tables](#global-tables)
13. [Security and Access Control](#security-and-access-control)
14. [Backup and Restore](#backup-and-restore)
15. [Performance Optimization](#performance-optimization)
16. [Monitoring and Troubleshooting](#monitoring-and-troubleshooting)
17. [Integration with Other AWS Services](#integration-with-other-aws-services)
18. [Best Practices](#best-practices)
19. [Common Use Cases](#common-use-cases)
20. [AWS CLI Commands Reference](#aws-cli-commands-reference)
21. [Exam Tips](#exam-tips)

## Introduction

Amazon DynamoDB is a fully managed NoSQL database service that provides fast and predictable performance with seamless scalability. It's a key service for the AWS Solutions Architect Associate (SAA-C03) certification.

### Key Features
- **Fully Managed**: No server management, patching, or maintenance
- **Fast Performance**: Single-digit millisecond latency at any scale
- **Seamless Scalability**: Scales up or down based on demand
- **Built-in Security**: Encryption at rest and in transit, fine-grained access control
- **Global Distribution**: Multi-region replication with Global Tables
- **Event-Driven Programming**: DynamoDB Streams for real-time data processing

## Core Concepts

### NoSQL Database
- **Schema-less**: No predefined schema required
- **Document or Key-Value**: Stores data as items (documents) with attributes
- **Horizontal Scaling**: Scales across multiple servers
- **ACID Transactions**: Supports ACID transactions for multiple items

### Tables, Items, and Attributes
- **Table**: Collection of items (similar to rows in relational databases)
- **Item**: Collection of attributes (similar to a row)
- **Attribute**: Name-value pair (similar to a column)

```json
{
  "CustomerID": "12345",
  "Name": "John Doe",
  "Email": "john@example.com",
  "Orders": [
    {
      "OrderID": "ORD-001",
      "Amount": 99.99,
      "Date": "2023-10-15"
    }
  ]
}
```

## DynamoDB Architecture

### Distributed Architecture
- **Partitions**: Data is distributed across multiple partitions
- **Partition Key**: Determines which partition an item is stored in
- **Hash Function**: Uses partition key to distribute data evenly

### Storage Engine
- **SSD Storage**: All data stored on solid-state drives
- **Automatic Replication**: Data replicated across multiple Availability Zones
- **Consistent Hashing**: Ensures even data distribution

## Data Types and Attributes

### Scalar Types
- **String (S)**: Text data, UTF-8 encoded
- **Number (N)**: Numeric data, up to 38 digits precision
- **Binary (B)**: Binary data, images, compressed objects
- **Boolean (BOOL)**: True or false values
- **Null (NULL)**: Represents unknown or undefined state

### Document Types
- **List (L)**: Ordered collection of values
- **Map (M)**: Unordered collection of name-value pairs

### Set Types
- **String Set (SS)**: Set of strings
- **Number Set (NS)**: Set of numbers
- **Binary Set (BS)**: Set of binary values

### Attribute Examples
```json
{
  "ProductID": "PROD-001",              // String
  "Price": 29.99,                       // Number
  "InStock": true,                      // Boolean
  "Description": null,                  // Null
  "Tags": ["electronics", "gadget"],    // String Set
  "Metadata": {                         // Map
    "manufacturer": "TechCorp",
    "warranty": "2 years"
  }
}
```

## Primary Keys

### Simple Primary Key (Partition Key)
- Single attribute that uniquely identifies each item
- Must be unique across all items in the table
- Used for hash-based data distribution

```json
{
  "UserID": "user123",  // Partition Key
  "Name": "Alice Smith",
  "Email": "alice@example.com"
}
```

### Composite Primary Key (Partition Key + Sort Key)
- Combination of partition key and sort key
- Partition key groups related items
- Sort key orders items within the same partition
- Combination must be unique

```json
{
  "UserID": "user123",        // Partition Key
  "Timestamp": "2023-10-15T10:30:00Z", // Sort Key
  "Action": "login",
  "IPAddress": "192.168.1.1"
}
```

### Key Design Considerations
- **Uniform Distribution**: Choose partition keys that distribute data evenly
- **Access Patterns**: Design keys based on how you'll query the data
- **Avoid Hot Partitions**: Prevent all requests going to the same partition

## Read and Write Operations

### Read Operations

#### GetItem
- Retrieves a single item by primary key
- Eventually consistent reads by default
- Strongly consistent reads available

```python
# Eventually Consistent Read
response = dynamodb.get_item(
    TableName='Users',
    Key={'UserID': {'S': 'user123'}}
)

# Strongly Consistent Read
response = dynamodb.get_item(
    TableName='Users',
    Key={'UserID': {'S': 'user123'}},
    ConsistentRead=True
)
```

#### Query
- Retrieves items with the same partition key
- Can filter by sort key using comparison operators
- More efficient than Scan for targeted retrieval

```python
response = dynamodb.query(
    TableName='UserSessions',
    KeyConditionExpression='UserID = :uid AND #ts BETWEEN :start AND :end',
    ExpressionAttributeNames={'#ts': 'Timestamp'},
    ExpressionAttributeValues={
        ':uid': {'S': 'user123'},
        ':start': {'S': '2023-10-01'},
        ':end': {'S': '2023-10-31'}
    }
)
```

#### Scan
- Examines every item in the table
- Can apply filters after scanning
- Less efficient than Query, use sparingly

```python
response = dynamodb.scan(
    TableName='Users',
    FilterExpression='#status = :status',
    ExpressionAttributeNames={'#status': 'Status'},
    ExpressionAttributeValues={':status': {'S': 'Active'}}
)
```

### Write Operations

#### PutItem
- Creates new item or replaces existing item
- Overwrites all attributes if item exists

```python
response = dynamodb.put_item(
    TableName='Users',
    Item={
        'UserID': {'S': 'user123'},
        'Name': {'S': 'John Doe'},
        'Email': {'S': 'john@example.com'},
        'CreatedAt': {'S': '2023-10-15T10:30:00Z'}
    }
)
```

#### UpdateItem
- Modifies attributes of existing item
- Creates item if it doesn't exist (unless using conditional expressions)

```python
response = dynamodb.update_item(
    TableName='Users',
    Key={'UserID': {'S': 'user123'}},
    UpdateExpression='SET #email = :email, #modified = :modified',
    ExpressionAttributeNames={
        '#email': 'Email',
        '#modified': 'ModifiedAt'
    },
    ExpressionAttributeValues={
        ':email': {'S': 'newemail@example.com'},
        ':modified': {'S': '2023-10-15T11:00:00Z'}
    }
)
```

#### DeleteItem
- Removes item from table
- Idempotent operation (no error if item doesn't exist)

```python
response = dynamodb.delete_item(
    TableName='Users',
    Key={'UserID': {'S': 'user123'}}
)
```

### Batch Operations

#### BatchGetItem
- Retrieves multiple items across multiple tables
- Up to 100 items per request
- 16 MB data limit per request

#### BatchWriteItem
- Puts or deletes multiple items across multiple tables
- Up to 25 operations per request
- 16 MB data limit per request

## Consistency Models

### Eventually Consistent Reads (Default)
- **Faster**: Lower latency
- **Cost Effective**: Consumes fewer read capacity units
- **Availability**: Works during network partitions
- **Trade-off**: May not reflect recent writes immediately

### Strongly Consistent Reads
- **Accuracy**: Always returns most recent data
- **Cost**: Consumes more read capacity units (2x)
- **Latency**: Slightly higher latency
- **Availability**: May not be available during network issues

### When to Use Each
- **Eventually Consistent**: Analytics, reporting, non-critical reads
- **Strongly Consistent**: Financial transactions, inventory management, critical operations

## Capacity Management

### Read Capacity Units (RCUs)
- **1 RCU**: One strongly consistent read per second for items up to 4 KB
- **Eventually Consistent**: 1 RCU = 2 eventually consistent reads per second
- **Larger Items**: Items > 4 KB consume additional RCUs

### Write Capacity Units (WCUs)
- **1 WCU**: One write per second for items up to 1 KB
- **Larger Items**: Items > 1 KB consume additional WCUs

### Provisioned Mode
- **Predictable Workloads**: When you can forecast capacity needs
- **Cost Control**: Pay for provisioned capacity whether used or not
- **Auto Scaling**: Automatically adjusts capacity based on utilization

```json
{
  "TableName": "Users",
  "BillingMode": "PROVISIONED",
  "ProvisionedThroughput": {
    "ReadCapacityUnits": 100,
    "WriteCapacityUnits": 50
  }
}
```

### On-Demand Mode
- **Unpredictable Workloads**: Traffic spikes and unknown patterns
- **Pay-per-Use**: Pay only for actual reads and writes
- **Automatic Scaling**: No capacity planning required

```json
{
  "TableName": "Users",
  "BillingMode": "PAY_PER_REQUEST"
}
```

### Capacity Calculation Examples

#### Read Capacity
```
Item size: 6 KB
Strongly consistent reads: 10 per second

RCUs needed = (6 KB / 4 KB) × 10 = 2 × 10 = 20 RCUs

Eventually consistent reads: 10 per second
RCUs needed = (6 KB / 4 KB) × 10 / 2 = 2 × 5 = 10 RCUs
```

#### Write Capacity
```
Item size: 3 KB
Writes: 15 per second

WCUs needed = (3 KB / 1 KB) × 15 = 3 × 15 = 45 WCUs
```

## Global Secondary Indexes (GSI)

### Overview
- **Alternative Access Patterns**: Query data using different attributes
- **Independent Scaling**: Own read/write capacity settings
- **Eventual Consistency**: Updates propagated asynchronously
- **Flexible Schema**: Can include different attributes from base table

### GSI Structure
- **Partition Key**: Required, can be different from table's partition key
- **Sort Key**: Optional, enables range queries
- **Projected Attributes**: Controls which attributes are copied to index

### Projection Types
1. **KEYS_ONLY**: Only key attributes
2. **INCLUDE**: Key attributes plus specified non-key attributes
3. **ALL**: All table attributes

### GSI Example
```json
{
  "IndexName": "UsersByEmail",
  "Keys": {
    "PartitionKey": "Email",
    "SortKey": "CreatedAt"
  },
  "Projection": {
    "ProjectionType": "INCLUDE",
    "NonKeyAttributes": ["Name", "Status"]
  },
  "ProvisionedThroughput": {
    "ReadCapacityUnits": 50,
    "WriteCapacityUnits": 25
  }
}
```

### GSI Best Practices
- **Sparse Indexes**: Not all items need to have GSI key attributes
- **Capacity Planning**: Monitor GSI capacity separately
- **Query Efficiency**: Design GSI keys for efficient access patterns
- **Cost Optimization**: Use appropriate projection types

## Local Secondary Indexes (LSI)

### Overview
- **Same Partition Key**: Uses table's partition key
- **Alternative Sort Key**: Different sort key for varied sorting
- **Strong Consistency**: Supports strongly consistent reads
- **Size Limit**: 10 GB per partition key value

### LSI vs GSI Comparison
| Feature | LSI | GSI |
|---------|-----|-----|
| Partition Key | Same as table | Can be different |
| Sort Key | Different from table | Can be different |
| Consistency | Strong + Eventual | Eventual only |
| Capacity | Shares with table | Independent |
| Size Limit | 10 GB per partition | No limit |
| Creation Time | Table creation only | Anytime |

### LSI Example
```json
{
  "IndexName": "UserSessionsByDuration",
  "Keys": {
    "PartitionKey": "UserID",  // Same as table
    "SortKey": "Duration"      // Different from table's Timestamp
  },
  "Projection": {
    "ProjectionType": "ALL"
  }
}
```

## DynamoDB Streams

### Overview
- **Change Data Capture**: Real-time stream of data modifications
- **Event-Driven Architecture**: Trigger functions on data changes
- **Ordered**: Events ordered by modification time
- **Retention**: 24-hour retention period

### Stream Record Contents
- **KEYS_ONLY**: Only key attributes of modified item
- **NEW_IMAGE**: Entire item after modification
- **OLD_IMAGE**: Entire item before modification
- **NEW_AND_OLD_IMAGES**: Both before and after images

### Stream Processing
```python
# Lambda function triggered by DynamoDB Stream
import json

def lambda_handler(event, context):
    for record in event['Records']:
        event_name = record['eventName']
        
        if event_name == 'INSERT':
            # Handle new item
            new_image = record['dynamodb']['NewImage']
            
        elif event_name == 'MODIFY':
            # Handle updated item
            old_image = record['dynamodb']['OldImage']
            new_image = record['dynamodb']['NewImage']
            
        elif event_name == 'REMOVE':
            # Handle deleted item
            old_image = record['dynamodb']['OldImage']
    
    return {'statusCode': 200}
```

### Use Cases
- **Real-time Analytics**: Stream changes to analytics systems
- **Audit Logging**: Track all data modifications
- **Data Synchronization**: Sync with other databases or search engines
- **Notifications**: Send alerts on specific changes

## Global Tables

### Overview
- **Multi-Region Replication**: Automatically replicated across AWS regions
- **Multi-Master**: Read and write from any region
- **Conflict Resolution**: Last-writer-wins conflict resolution
- **Eventual Consistency**: Cross-region replication is eventually consistent

### Benefits
- **Low Latency**: Users access nearest region
- **Disaster Recovery**: Built-in DR across regions
- **Global Scale**: Serve global user base efficiently
- **High Availability**: Continues operating if region fails

### Global Tables Setup
```json
{
  "GlobalTableName": "Users",
  "ReplicationGroup": [
    {
      "RegionName": "us-east-1",
      "Replica": {
        "TableClass": "STANDARD",
        "BillingMode": "PAY_PER_REQUEST"
      }
    },
    {
      "RegionName": "eu-west-1",
      "Replica": {
        "TableClass": "STANDARD",
        "BillingMode": "PAY_PER_REQUEST"
      }
    },
    {
      "RegionName": "ap-southeast-1",
      "Replica": {
        "TableClass": "STANDARD",
        "BillingMode": "PAY_PER_REQUEST"
      }
    }
  ]
}
```

### Considerations
- **Consistency**: Eventually consistent across regions
- **Conflicts**: Handle potential write conflicts
- **Cost**: Data transfer charges between regions
- **Latency**: Cross-region replication latency

## Security and Access Control

### IAM Policies
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem"
      ],
      "Resource": "arn:aws:dynamodb:region:account:table/Users"
    }
  ]
}
```

### Fine-Grained Access Control
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:UpdateItem"
      ],
      "Resource": "arn:aws:dynamodb:region:account:table/Users",
      "Condition": {
        "ForAllValues:StringEquals": {
          "dynamodb:Attributes": [
            "UserID",
            "Name",
            "Email"
          ]
        },
        "StringEquals": {
          "dynamodb:LeadingKeys": "${aws:username}"
        }
      }
    }
  ]
}
```

### Encryption

#### Encryption at Rest
- **AWS Managed**: Default encryption using AWS managed keys
- **Customer Managed**: Customer managed KMS keys for full control
- **Client-Side**: Encrypt data before sending to DynamoDB

#### Encryption in Transit
- **HTTPS/TLS**: All API calls encrypted in transit
- **VPC Endpoints**: Private connectivity without internet gateway

### VPC Endpoints
- **Gateway Endpoint**: Route traffic through VPC without internet
- **Interface Endpoint**: ENI-based endpoint with private IP
- **Cost**: No data transfer charges for VPC traffic

## Backup and Restore

### Point-in-Time Recovery (PITR)
- **Continuous Backups**: Automatic incremental backups
- **35-Day Retention**: Restore to any point within 35 days
- **Per-Second Granularity**: Restore to exact timestamp
- **Cross-Region**: Restore to different region

### On-Demand Backup
- **Manual Snapshots**: Create backups on demand
- **Long-Term Retention**: Keep backups as long as needed
- **Cross-Account**: Share backups across AWS accounts
- **Full Backup**: Complete table backup including data and settings

### Backup Best Practices
- **Regular Backups**: Schedule regular on-demand backups
- **Test Restores**: Regularly test backup restoration
- **Cross-Region**: Store critical backups in multiple regions
- **Lifecycle**: Implement backup lifecycle policies

## Performance Optimization

### Hot Partition Avoidance
```python
# Bad: Sequential partition keys
user_id = f"USER_{timestamp}"  # Creates hot partition

# Good: Distributed partition keys
user_id = f"{hash(email) % 1000}_{timestamp}"  # Better distribution
```

### Efficient Access Patterns
```python
# Efficient: Query with partition key
response = dynamodb.query(
    TableName='Orders',
    KeyConditionExpression='CustomerID = :customer_id',
    ExpressionAttributeValues={':customer_id': {'S': 'CUST123'}}
)

# Inefficient: Scan entire table
response = dynamodb.scan(
    TableName='Orders',
    FilterExpression='CustomerID = :customer_id',
    ExpressionAttributeValues={':customer_id': {'S': 'CUST123'}}
)
```

### Pagination
```python
def paginated_scan(table_name, filter_expression=None):
    params = {'TableName': table_name}
    if filter_expression:
        params['FilterExpression'] = filter_expression
    
    items = []
    last_evaluated_key = None
    
    while True:
        if last_evaluated_key:
            params['ExclusiveStartKey'] = last_evaluated_key
        
        response = dynamodb.scan(**params)
        items.extend(response.get('Items', []))
        
        last_evaluated_key = response.get('LastEvaluatedKey')
        if not last_evaluated_key:
            break
    
    return items
```

### Batch Operations
```python
# Efficient batch write
def batch_write_items(table_name, items):
    with table.batch_writer() as batch:
        for item in items:
            batch.put_item(Item=item)
```

## Monitoring and Troubleshooting

### CloudWatch Metrics
- **ConsumedReadCapacityUnits**: RCUs consumed
- **ConsumedWriteCapacityUnits**: WCUs consumed
- **ProvisionedReadCapacityUnits**: Provisioned RCUs
- **ProvisionedWriteCapacityUnits**: Provisioned WCUs
- **ReadThrottledRequests**: Throttled read operations
- **WriteThrottledRequests**: Throttled write operations
- **SuccessfulRequestLatency**: Request latency
- **SystemErrors**: DynamoDB system errors

### CloudWatch Alarms
```json
{
  "AlarmName": "DynamoDB-ReadThrottling",
  "MetricName": "ReadThrottledRequests",
  "Namespace": "AWS/DynamoDB",
  "Statistic": "Sum",
  "Period": 300,
  "Threshold": 0,
  "ComparisonOperator": "GreaterThanThreshold",
  "Dimensions": [
    {
      "Name": "TableName",
      "Value": "Users"
    }
  ]
}
```

### AWS X-Ray Integration
- **Request Tracing**: Trace requests through DynamoDB
- **Performance Analysis**: Identify bottlenecks
- **Error Analysis**: Debug failed requests

### Common Issues and Solutions

#### Throttling
**Causes**: Exceeding provisioned capacity, hot partitions
**Solutions**: Increase capacity, improve key design, use exponential backoff

#### Hot Partitions
**Causes**: Uneven data distribution, sequential access patterns
**Solutions**: Better partition key design, add randomness, use composite keys

#### Large Items
**Causes**: Items exceeding 400 KB limit
**Solutions**: Break into smaller items, use S3 for large data, normalize data

## Integration with Other AWS Services

### Lambda Integration
```python
# DynamoDB trigger function
import boto3

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('ProcessingQueue')
    
    for record in event['Records']:
        if record['eventName'] == 'INSERT':
            # Process new item
            item = record['dynamodb']['NewImage']
            process_item(item)
```

### API Gateway Integration
```yaml
# API Gateway with DynamoDB integration
Resources:
  DynamoDBIntegration:
    Type: AWS::ApiGateway::Method
    Properties:
      HttpMethod: GET
      Integration:
        Type: AWS
        IntegrationHttpMethod: POST
        Uri: !Sub 'arn:aws:apigateway:${AWS::Region}:dynamodb:action/GetItem'
        Credentials: !GetAtt ApiGatewayRole.Arn
```

### Step Functions Integration
```json
{
  "Comment": "DynamoDB workflow",
  "StartAt": "GetUser",
  "States": {
    "GetUser": {
      "Type": "Task",
      "Resource": "arn:aws:states:::dynamodb:getItem",
      "Parameters": {
        "TableName": "Users",
        "Key": {
          "UserID": {"S.$": "$.userId"}
        }
      },
      "Next": "ProcessUser"
    }
  }
}
```

### Kinesis Integration
- **DynamoDB Streams**: Stream changes to Kinesis Data Streams
- **Kinesis Analytics**: Real-time analytics on DynamoDB data
- **Kinesis Firehose**: Load DynamoDB data to S3, Redshift

### ElasticSearch Integration
```python
# Sync DynamoDB changes to Elasticsearch
def sync_to_elasticsearch(event, context):
    es_client = boto3.client('es')
    
    for record in event['Records']:
        if record['eventName'] == 'INSERT':
            doc = record['dynamodb']['NewImage']
            es_client.index(
                index='users',
                id=doc['UserID']['S'],
                body=convert_dynamodb_to_json(doc)
            )
```

## Best Practices

### Table Design
1. **Understand Access Patterns**: Design based on query requirements
2. **Minimize Tables**: Use single table design when possible
3. **Optimize for Queries**: Avoid scans, use queries instead
4. **Plan for Growth**: Consider future scaling needs

### Key Design
1. **Uniform Distribution**: Choose keys that spread data evenly
2. **Avoid Sequential Keys**: Prevent hot partitions
3. **Composite Keys**: Use sort keys for range queries
4. **Hierarchical Data**: Model relationships using sort keys

### Performance
1. **Right-Size Capacity**: Monitor and adjust capacity settings
2. **Use Batch Operations**: Reduce API calls with batch operations
3. **Implement Caching**: Use DAX or ElastiCache for frequently accessed data
4. **Optimize Projections**: Choose appropriate GSI projections

### Security
1. **Least Privilege**: Grant minimum required permissions
2. **Use IAM Roles**: Avoid hardcoded credentials
3. **Enable Encryption**: Use encryption at rest and in transit
4. **Monitor Access**: Use CloudTrail and CloudWatch

### Cost Optimization
1. **Choose Right Billing Mode**: Provisioned vs On-Demand
2. **Monitor Capacity Usage**: Avoid over-provisioning
3. **Use Reserved Capacity**: For predictable workloads
4. **Optimize Storage**: Use appropriate table classes

## Common Use Cases

### Session Store
```python
# Session management with DynamoDB
def store_session(session_id, user_data, ttl_seconds=3600):
    ttl_timestamp = int(time.time()) + ttl_seconds
    
    table.put_item(
        Item={
            'SessionID': session_id,
            'UserData': user_data,
            'TTL': ttl_timestamp
        }
    )
```

### Real-time Gaming
```python
# Gaming leaderboard
def update_score(player_id, score):
    table.update_item(
        Key={'PlayerID': player_id},
        UpdateExpression='SET Score = :score, LastUpdated = :timestamp',
        ExpressionAttributeValues={
            ':score': score,
            ':timestamp': int(time.time())
        }
    )
```

### IoT Data Storage
```python
# IoT sensor data
def store_sensor_data(device_id, timestamp, measurements):
    table.put_item(
        Item={
            'DeviceID': device_id,
            'Timestamp': timestamp,
            'Temperature': measurements['temperature'],
            'Humidity': measurements['humidity'],
            'Pressure': measurements['pressure']
        }
    )
```

### Content Management
```python
# Content versioning
def create_content_version(content_id, version, content_data):
    table.put_item(
        Item={
            'ContentID': content_id,
            'Version': version,
            'Data': content_data,
            'CreatedAt': datetime.utcnow().isoformat(),
            'Status': 'draft'
        }
    )
```

## AWS CLI Commands Reference

This section provides comprehensive AWS CLI commands for managing DynamoDB tables, items, and related operations.

### Create and Manage Tables

```bash
# Create a table with simple primary key (partition key only)
aws dynamodb create-table \
    --table-name Users \
    --attribute-definitions \
        AttributeName=UserID,AttributeType=S \
    --key-schema \
        AttributeName=UserID,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST

# Create a table with composite primary key (partition key + sort key)
aws dynamodb create-table \
    --table-name Orders \
    --attribute-definitions \
        AttributeName=CustomerID,AttributeType=S \
        AttributeName=OrderDate,AttributeType=S \
    --key-schema \
        AttributeName=CustomerID,KeyType=HASH \
        AttributeName=OrderDate,KeyType=RANGE \
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5

# Create a table with GSI and LSI
aws dynamodb create-table \
    --table-name Products \
    --attribute-definitions \
        AttributeName=ProductID,AttributeType=S \
        AttributeName=Category,AttributeType=S \
        AttributeName=Price,AttributeType=N \
        AttributeName=CreatedDate,AttributeType=S \
    --key-schema \
        AttributeName=ProductID,KeyType=HASH \
        AttributeName=CreatedDate,KeyType=RANGE \
    --global-secondary-indexes \
        "[
            {
                \"IndexName\": \"CategoryIndex\",
                \"KeySchema\": [
                    {\"AttributeName\":\"Category\",\"KeyType\":\"HASH\"},
                    {\"AttributeName\":\"Price\",\"KeyType\":\"RANGE\"}
                ],
                \"Projection\": {\"ProjectionType\":\"ALL\"},
                \"ProvisionedThroughput\": {
                    \"ReadCapacityUnits\": 5,
                    \"WriteCapacityUnits\": 5
                }
            }
        ]" \
    --local-secondary-indexes \
        "[
            {
                \"IndexName\": \"PriceIndex\",
                \"KeySchema\": [
                    {\"AttributeName\":\"ProductID\",\"KeyType\":\"HASH\"},
                    {\"AttributeName\":\"Price\",\"KeyType\":\"RANGE\"}
                ],
                \"Projection\": {\"ProjectionType\":\"ALL\"}
            }
        ]" \
    --billing-mode PROVISIONED \
    --provisioned-throughput ReadCapacityUnits=10,WriteCapacityUnits=10

# Describe a table
aws dynamodb describe-table --table-name Users

# List all tables
aws dynamodb list-tables

# Update table billing mode
aws dynamodb update-table \
    --table-name Users \
    --billing-mode PAY_PER_REQUEST

# Update table provisioned throughput
aws dynamodb update-table \
    --table-name Orders \
    --provisioned-throughput ReadCapacityUnits=10,WriteCapacityUnits=10

# Delete a table
aws dynamodb delete-table --table-name Users

# Wait for table to be active
aws dynamodb wait table-exists --table-name Users
```

### Put, Get, Update, Delete Items

```bash
# Put an item
aws dynamodb put-item \
    --table-name Users \
    --item '{
        "UserID": {"S": "user-123"},
        "Name": {"S": "John Doe"},
        "Email": {"S": "john@example.com"},
        "Age": {"N": "30"},
        "Active": {"BOOL": true}
    }'

# Put item with condition (only if not exists)
aws dynamodb put-item \
    --table-name Users \
    --item '{
        "UserID": {"S": "user-456"},
        "Name": {"S": "Jane Smith"},
        "Email": {"S": "jane@example.com"}
    }' \
    --condition-expression "attribute_not_exists(UserID)"

# Get an item
aws dynamodb get-item \
    --table-name Users \
    --key '{"UserID": {"S": "user-123"}}'

# Get item with specific attributes
aws dynamodb get-item \
    --table-name Users \
    --key '{"UserID": {"S": "user-123"}}' \
    --projection-expression "Name, Email"

# Get item with consistent read
aws dynamodb get-item \
    --table-name Users \
    --key '{"UserID": {"S": "user-123"}}' \
    --consistent-read

# Update an item
aws dynamodb update-item \
    --table-name Users \
    --key '{"UserID": {"S": "user-123"}}' \
    --update-expression "SET Age = :age, #n = :name" \
    --expression-attribute-names '{"#n": "Name"}' \
    --expression-attribute-values '{
        ":age": {"N": "31"},
        ":name": {"S": "John Updated"}
    }'

# Update item with atomic counter
aws dynamodb update-item \
    --table-name Users \
    --key '{"UserID": {"S": "user-123"}}' \
    --update-expression "SET LoginCount = LoginCount + :inc" \
    --expression-attribute-values '{":inc": {"N": "1"}}' \
    --return-values UPDATED_NEW

# Update item with condition
aws dynamodb update-item \
    --table-name Users \
    --key '{"UserID": {"S": "user-123"}}' \
    --update-expression "SET Active = :active" \
    --condition-expression "Age > :min_age" \
    --expression-attribute-values '{
        ":active": {"BOOL": false},
        ":min_age": {"N": "18"}
    }'

# Delete an item
aws dynamodb delete-item \
    --table-name Users \
    --key '{"UserID": {"S": "user-123"}}'

# Delete item with condition and return old values
aws dynamodb delete-item \
    --table-name Users \
    --key '{"UserID": {"S": "user-123"}}' \
    --condition-expression "Active = :inactive" \
    --expression-attribute-values '{":inactive": {"BOOL": false}}' \
    --return-values ALL_OLD
```

### Batch Operations

```bash
# Batch write items (put and delete)
aws dynamodb batch-write-item \
    --request-items '{
        "Users": [
            {
                "PutRequest": {
                    "Item": {
                        "UserID": {"S": "user-001"},
                        "Name": {"S": "Alice"},
                        "Email": {"S": "alice@example.com"}
                    }
                }
            },
            {
                "PutRequest": {
                    "Item": {
                        "UserID": {"S": "user-002"},
                        "Name": {"S": "Bob"},
                        "Email": {"S": "bob@example.com"}
                    }
                }
            },
            {
                "DeleteRequest": {
                    "Key": {
                        "UserID": {"S": "user-999"}
                    }
                }
            }
        ]
    }'

# Batch get items (up to 100 items, 16 MB)
aws dynamodb batch-get-item \
    --request-items '{
        "Users": {
            "Keys": [
                {"UserID": {"S": "user-001"}},
                {"UserID": {"S": "user-002"}},
                {"UserID": {"S": "user-003"}}
            ],
            "ProjectionExpression": "UserID, Name, Email"
        },
        "Orders": {
            "Keys": [
                {
                    "CustomerID": {"S": "cust-001"},
                    "OrderDate": {"S": "2024-01-15"}
                }
            ]
        }
    }'

# Batch get with consistent read
aws dynamodb batch-get-item \
    --request-items '{
        "Users": {
            "Keys": [
                {"UserID": {"S": "user-001"}},
                {"UserID": {"S": "user-002"}}
            ],
            "ConsistentRead": true
        }
    }'
```

### Query Operations

```bash
# Query with partition key only
aws dynamodb query \
    --table-name Orders \
    --key-condition-expression "CustomerID = :cust_id" \
    --expression-attribute-values '{
        ":cust_id": {"S": "customer-123"}
    }'

# Query with partition key and sort key range
aws dynamodb query \
    --table-name Orders \
    --key-condition-expression "CustomerID = :cust_id AND OrderDate BETWEEN :start_date AND :end_date" \
    --expression-attribute-values '{
        ":cust_id": {"S": "customer-123"},
        ":start_date": {"S": "2024-01-01"},
        ":end_date": {"S": "2024-12-31"}
    }'

# Query with filter expression
aws dynamodb query \
    --table-name Orders \
    --key-condition-expression "CustomerID = :cust_id" \
    --filter-expression "TotalAmount > :min_amount" \
    --expression-attribute-values '{
        ":cust_id": {"S": "customer-123"},
        ":min_amount": {"N": "100"}
    }'

# Query on GSI
aws dynamodb query \
    --table-name Products \
    --index-name CategoryIndex \
    --key-condition-expression "Category = :cat AND Price < :max_price" \
    --expression-attribute-values '{
        ":cat": {"S": "Electronics"},
        ":max_price": {"N": "500"}
    }'

# Query with projection
aws dynamodb query \
    --table-name Orders \
    --key-condition-expression "CustomerID = :cust_id" \
    --projection-expression "OrderID, OrderDate, TotalAmount" \
    --expression-attribute-values '{":cust_id": {"S": "customer-123"}}'

# Query with limit and pagination
aws dynamodb query \
    --table-name Orders \
    --key-condition-expression "CustomerID = :cust_id" \
    --expression-attribute-values '{":cust_id": {"S": "customer-123"}}' \
    --limit 10

# Query in reverse order (descending)
aws dynamodb query \
    --table-name Orders \
    --key-condition-expression "CustomerID = :cust_id" \
    --expression-attribute-values '{":cust_id": {"S": "customer-123"}}' \
    --scan-index-forward false

# Query with consistent read
aws dynamodb query \
    --table-name Orders \
    --key-condition-expression "CustomerID = :cust_id" \
    --expression-attribute-values '{":cust_id": {"S": "customer-123"}}' \
    --consistent-read
```

### Scan Operations

```bash
# Scan entire table
aws dynamodb scan --table-name Users

# Scan with filter expression
aws dynamodb scan \
    --table-name Users \
    --filter-expression "Age > :min_age AND Active = :active" \
    --expression-attribute-values '{
        ":min_age": {"N": "25"},
        ":active": {"BOOL": true}
    }'

# Scan with projection
aws dynamodb scan \
    --table-name Users \
    --projection-expression "UserID, Name, Email"

# Parallel scan (segment 0 of 4)
aws dynamodb scan \
    --table-name Users \
    --total-segments 4 \
    --segment 0

# Scan with limit
aws dynamodb scan \
    --table-name Users \
    --limit 50

# Scan on GSI
aws dynamodb scan \
    --table-name Products \
    --index-name CategoryIndex

# Scan with consistent read (only for base table, not GSI)
aws dynamodb scan \
    --table-name Users \
    --consistent-read
```

### Global Tables

```bash
# Create a global table (v2019.11.21)
aws dynamodb create-global-table \
    --global-table-name GlobalUsers \
    --replication-group RegionName=us-east-1 RegionName=eu-west-1 RegionName=ap-southeast-1

# Update global table (add new region)
aws dynamodb update-global-table \
    --global-table-name GlobalUsers \
    --replica-updates Create={RegionName=us-west-2}

# Describe global table
aws dynamodb describe-global-table \
    --global-table-name GlobalUsers

# List global tables
aws dynamodb list-global-tables

# Update global table settings
aws dynamodb update-global-table-settings \
    --global-table-name GlobalUsers \
    --global-table-billing-mode PAY_PER_REQUEST

# Describe global table settings
aws dynamodb describe-global-table-settings \
    --global-table-name GlobalUsers
```

### DynamoDB Streams

```bash
# Enable streams on a table
aws dynamodb update-table \
    --table-name Users \
    --stream-specification \
        StreamEnabled=true,StreamViewType=NEW_AND_OLD_IMAGES

# List streams
aws dynamodbstreams list-streams \
    --table-name Users

# Describe a stream
aws dynamodbstreams describe-stream \
    --stream-arn "arn:aws:dynamodb:us-east-1:123456789012:table/Users/stream/2024-01-15T00:00:00.000"

# Get shard iterator
aws dynamodbstreams get-shard-iterator \
    --stream-arn "arn:aws:dynamodb:us-east-1:123456789012:table/Users/stream/2024-01-15T00:00:00.000" \
    --shard-id "shardId-00000001234567890123-abcdefgh" \
    --shard-iterator-type LATEST

# Get stream records
aws dynamodbstreams get-records \
    --shard-iterator "AAAAAAAAAAGx1...=="

# Disable streams
aws dynamodb update-table \
    --table-name Users \
    --stream-specification StreamEnabled=false
```

### Backup and Restore

```bash
# Create on-demand backup
aws dynamodb create-backup \
    --table-name Users \
    --backup-name users-backup-2024-01-15

# List backups
aws dynamodb list-backups \
    --table-name Users

# List all backups
aws dynamodb list-backups

# Describe backup
aws dynamodb describe-backup \
    --backup-arn "arn:aws:dynamodb:us-east-1:123456789012:table/Users/backup/01234567890123-abcdefgh"

# Restore from backup
aws dynamodb restore-table-from-backup \
    --target-table-name UsersRestored \
    --backup-arn "arn:aws:dynamodb:us-east-1:123456789012:table/Users/backup/01234567890123-abcdefgh"

# Delete backup
aws dynamodb delete-backup \
    --backup-arn "arn:aws:dynamodb:us-east-1:123456789012:table/Users/backup/01234567890123-abcdefgh"

# Enable point-in-time recovery (PITR)
aws dynamodb update-continuous-backups \
    --table-name Users \
    --point-in-time-recovery-specification PointInTimeRecoveryEnabled=true

# Describe continuous backups
aws dynamodb describe-continuous-backups \
    --table-name Users

# Restore to a point in time
aws dynamodb restore-table-to-point-in-time \
    --source-table-name Users \
    --target-table-name UsersRestored \
    --restore-date-time "2024-01-15T12:00:00Z"

# Restore to latest restorable time
aws dynamodb restore-table-to-point-in-time \
    --source-table-name Users \
    --target-table-name UsersRestored \
    --use-latest-restorable-time
```

### DynamoDB Accelerator (DAX)

```bash
# Create DAX cluster
aws dax create-cluster \
    --cluster-name my-dax-cluster \
    --node-type dax.r5.large \
    --replication-factor 3 \
    --iam-role-arn "arn:aws:iam::123456789012:role/DAXServiceRole" \
    --subnet-group my-dax-subnet-group \
    --security-group-ids sg-12345678

# Describe DAX cluster
aws dax describe-clusters \
    --cluster-names my-dax-cluster

# List DAX clusters
aws dax describe-clusters

# Update DAX cluster
aws dax update-cluster \
    --cluster-name my-dax-cluster \
    --preferred-maintenance-window "sun:05:00-sun:06:00"

# Increase DAX cluster nodes
aws dax increase-replication-factor \
    --cluster-name my-dax-cluster \
    --new-replication-factor 5

# Decrease DAX cluster nodes
aws dax decrease-replication-factor \
    --cluster-name my-dax-cluster \
    --new-replication-factor 3

# Delete DAX cluster
aws dax delete-cluster \
    --cluster-name my-dax-cluster

# Create DAX subnet group
aws dax create-subnet-group \
    --subnet-group-name my-dax-subnet-group \
    --subnet-ids subnet-12345678 subnet-87654321

# Create DAX parameter group
aws dax create-parameter-group \
    --parameter-group-name my-dax-params \
    --description "Custom DAX parameters"

# Describe DAX parameter groups
aws dax describe-parameter-groups
```

### Auto Scaling Configuration

```bash
# Register scalable target for table
aws application-autoscaling register-scalable-target \
    --service-namespace dynamodb \
    --resource-id "table/Users" \
    --scalable-dimension "dynamodb:table:ReadCapacityUnits" \
    --min-capacity 5 \
    --max-capacity 100

# Register scalable target for write capacity
aws application-autoscaling register-scalable-target \
    --service-namespace dynamodb \
    --resource-id "table/Users" \
    --scalable-dimension "dynamodb:table:WriteCapacityUnits" \
    --min-capacity 5 \
    --max-capacity 100

# Create scaling policy for read capacity
aws application-autoscaling put-scaling-policy \
    --service-namespace dynamodb \
    --resource-id "table/Users" \
    --scalable-dimension "dynamodb:table:ReadCapacityUnits" \
    --policy-name "MyReadScalingPolicy" \
    --policy-type TargetTrackingScaling \
    --target-tracking-scaling-policy-configuration '{
        "TargetValue": 70.0,
        "PredefinedMetricSpecification": {
            "PredefinedMetricType": "DynamoDBReadCapacityUtilization"
        },
        "ScaleInCooldown": 60,
        "ScaleOutCooldown": 60
    }'

# Create scaling policy for write capacity
aws application-autoscaling put-scaling-policy \
    --service-namespace dynamodb \
    --resource-id "table/Users" \
    --scalable-dimension "dynamodb:table:WriteCapacityUnits" \
    --policy-name "MyWriteScalingPolicy" \
    --policy-type TargetTrackingScaling \
    --target-tracking-scaling-policy-configuration '{
        "TargetValue": 70.0,
        "PredefinedMetricSpecification": {
            "PredefinedMetricType": "DynamoDBWriteCapacityUtilization"
        },
        "ScaleInCooldown": 60,
        "ScaleOutCooldown": 60
    }'

# Register GSI for auto scaling
aws application-autoscaling register-scalable-target \
    --service-namespace dynamodb \
    --resource-id "table/Products/index/CategoryIndex" \
    --scalable-dimension "dynamodb:index:ReadCapacityUnits" \
    --min-capacity 5 \
    --max-capacity 50

# Describe scaling policies
aws application-autoscaling describe-scaling-policies \
    --service-namespace dynamodb

# Deregister scalable target
aws application-autoscaling deregister-scalable-target \
    --service-namespace dynamodb \
    --resource-id "table/Users" \
    --scalable-dimension "dynamodb:table:ReadCapacityUnits"
```

### Tags Management

```bash
# Add tags to a table
aws dynamodb tag-resource \
    --resource-arn "arn:aws:dynamodb:us-east-1:123456789012:table/Users" \
    --tags Key=Environment,Value=Production Key=Owner,Value=TeamA Key=CostCenter,Value=Engineering

# List tags for a table
aws dynamodb list-tags-of-resource \
    --resource-arn "arn:aws:dynamodb:us-east-1:123456789012:table/Users"

# Remove tags from a table
aws dynamodb untag-resource \
    --resource-arn "arn:aws:dynamodb:us-east-1:123456789012:table/Users" \
    --tag-keys Environment Owner
```

### Time to Live (TTL) Configuration

```bash
# Enable TTL on a table
aws dynamodb update-time-to-live \
    --table-name Users \
    --time-to-live-specification "Enabled=true,AttributeName=ExpirationTime"

# Describe TTL settings
aws dynamodb describe-time-to-live \
    --table-name Users

# Disable TTL
aws dynamodb update-time-to-live \
    --table-name Users \
    --time-to-live-specification "Enabled=false,AttributeName=ExpirationTime"
```

### Global Secondary Indexes (GSI) Management

```bash
# Create a GSI on existing table
aws dynamodb update-table \
    --table-name Users \
    --attribute-definitions AttributeName=Email,AttributeType=S \
    --global-secondary-index-updates '[
        {
            "Create": {
                "IndexName": "EmailIndex",
                "KeySchema": [
                    {"AttributeName": "Email", "KeyType": "HASH"}
                ],
                "Projection": {
                    "ProjectionType": "ALL"
                },
                "ProvisionedThroughput": {
                    "ReadCapacityUnits": 5,
                    "WriteCapacityUnits": 5
                }
            }
        }
    ]'

# Update GSI provisioned throughput
aws dynamodb update-table \
    --table-name Users \
    --global-secondary-index-updates '[
        {
            "Update": {
                "IndexName": "EmailIndex",
                "ProvisionedThroughput": {
                    "ReadCapacityUnits": 10,
                    "WriteCapacityUnits": 10
                }
            }
        }
    ]'

# Delete a GSI
aws dynamodb update-table \
    --table-name Users \
    --global-secondary-index-updates '[
        {
            "Delete": {
                "IndexName": "EmailIndex"
            }
        }
    ]'

# Create GSI with projection (only specific attributes)
aws dynamodb update-table \
    --table-name Users \
    --attribute-definitions AttributeName=Country,AttributeType=S \
    --global-secondary-index-updates '[
        {
            "Create": {
                "IndexName": "CountryIndex",
                "KeySchema": [
                    {"AttributeName": "Country", "KeyType": "HASH"}
                ],
                "Projection": {
                    "ProjectionType": "INCLUDE",
                    "NonKeyAttributes": ["Name", "Email"]
                },
                "ProvisionedThroughput": {
                    "ReadCapacityUnits": 5,
                    "WriteCapacityUnits": 5
                }
            }
        }
    ]'
```

### Local Secondary Indexes (LSI) Management

```bash
# Note: LSI can only be created at table creation time
# Create table with LSI
aws dynamodb create-table \
    --table-name Orders \
    --attribute-definitions \
        AttributeName=CustomerID,AttributeType=S \
        AttributeName=OrderDate,AttributeType=S \
        AttributeName=OrderStatus,AttributeType=S \
    --key-schema \
        AttributeName=CustomerID,KeyType=HASH \
        AttributeName=OrderDate,KeyType=RANGE \
    --local-secondary-indexes '[
        {
            "IndexName": "StatusIndex",
            "KeySchema": [
                {"AttributeName": "CustomerID", "KeyType": "HASH"},
                {"AttributeName": "OrderStatus", "KeyType": "RANGE"}
            ],
            "Projection": {
                "ProjectionType": "ALL"
            }
        }
    ]' \
    --billing-mode PAY_PER_REQUEST

# Query using LSI
aws dynamodb query \
    --table-name Orders \
    --index-name StatusIndex \
    --key-condition-expression "CustomerID = :cust_id AND OrderStatus = :status" \
    --expression-attribute-values '{
        ":cust_id": {"S": "customer-123"},
        ":status": {"S": "SHIPPED"}
    }'
```

### Transactions

```bash
# TransactWriteItems - atomic write across multiple items
aws dynamodb transact-write-items \
    --transact-items '[
        {
            "Put": {
                "TableName": "Users",
                "Item": {
                    "UserID": {"S": "user-123"},
                    "Balance": {"N": "100"}
                },
                "ConditionExpression": "attribute_not_exists(UserID)"
            }
        },
        {
            "Update": {
                "TableName": "Accounts",
                "Key": {
                    "AccountID": {"S": "acc-456"}
                },
                "UpdateExpression": "SET Balance = Balance - :amount",
                "ExpressionAttributeValues": {
                    ":amount": {"N": "100"},
                    ":min_balance": {"N": "0"}
                },
                "ConditionExpression": "Balance >= :min_balance"
            }
        },
        {
            "Delete": {
                "TableName": "PendingTransactions",
                "Key": {
                    "TransactionID": {"S": "txn-789"}
                }
            }
        }
    ]'

# TransactGetItems - atomic read across multiple items
aws dynamodb transact-get-items \
    --transact-items '[
        {
            "Get": {
                "TableName": "Users",
                "Key": {
                    "UserID": {"S": "user-123"}
                },
                "ProjectionExpression": "UserID, Balance"
            }
        },
        {
            "Get": {
                "TableName": "Accounts",
                "Key": {
                    "AccountID": {"S": "acc-456"}
                }
            }
        }
    ]'

# Transaction with condition check
aws dynamodb transact-write-items \
    --transact-items '[
        {
            "ConditionCheck": {
                "TableName": "Users",
                "Key": {
                    "UserID": {"S": "user-123"}
                },
                "ConditionExpression": "Active = :true",
                "ExpressionAttributeValues": {
                    ":true": {"BOOL": true}
                }
            }
        },
        {
            "Put": {
                "TableName": "Orders",
                "Item": {
                    "OrderID": {"S": "order-001"},
                    "CustomerID": {"S": "user-123"},
                    "Amount": {"N": "99.99"}
                }
            }
        }
    ]'
```

### Export to S3

```bash
# Export table to S3
aws dynamodb export-table-to-point-in-time \
    --table-arn "arn:aws:dynamodb:us-east-1:123456789012:table/Users" \
    --s3-bucket "my-exports-bucket" \
    --s3-prefix "dynamodb-exports/" \
    --export-format DYNAMODB_JSON

# Export to S3 with specific time
aws dynamodb export-table-to-point-in-time \
    --table-arn "arn:aws:dynamodb:us-east-1:123456789012:table/Users" \
    --s3-bucket "my-exports-bucket" \
    --s3-prefix "dynamodb-exports/users/" \
    --export-time "2024-01-15T12:00:00Z" \
    --export-format ION

# Export with SSE encryption
aws dynamodb export-table-to-point-in-time \
    --table-arn "arn:aws:dynamodb:us-east-1:123456789012:table/Users" \
    --s3-bucket "my-exports-bucket" \
    --s3-prefix "dynamodb-exports/" \
    --s3-sse-algorithm AES256

# Describe export
aws dynamodb describe-export \
    --export-arn "arn:aws:dynamodb:us-east-1:123456789012:table/Users/export/01234567890123-abcdefgh"

# List exports
aws dynamodb list-exports \
    --table-arn "arn:aws:dynamodb:us-east-1:123456789012:table/Users"
```

### Import from S3

```bash
# Import table from S3
aws dynamodb import-table \
    --s3-bucket-source S3Bucket=my-imports-bucket,S3KeyPrefix=dynamodb-imports/ \
    --input-format DYNAMODB_JSON \
    --table-creation-parameters '{
        "TableName": "ImportedUsers",
        "AttributeDefinitions": [
            {"AttributeName": "UserID", "AttributeType": "S"}
        ],
        "KeySchema": [
            {"AttributeName": "UserID", "KeyType": "HASH"}
        ],
        "BillingMode": "PAY_PER_REQUEST"
    }'

# Import with provisioned capacity
aws dynamodb import-table \
    --s3-bucket-source S3Bucket=my-imports-bucket,S3KeyPrefix=data/ \
    --input-format ION \
    --table-creation-parameters '{
        "TableName": "ImportedOrders",
        "AttributeDefinitions": [
            {"AttributeName": "OrderID", "AttributeType": "S"},
            {"AttributeName": "OrderDate", "AttributeType": "S"}
        ],
        "KeySchema": [
            {"AttributeName": "OrderID", "KeyType": "HASH"},
            {"AttributeName": "OrderDate", "KeyType": "RANGE"}
        ],
        "BillingMode": "PROVISIONED",
        "ProvisionedThroughput": {
            "ReadCapacityUnits": 10,
            "WriteCapacityUnits": 10
        }
    }'

# Import with compression
aws dynamodb import-table \
    --s3-bucket-source S3Bucket=my-imports-bucket,S3KeyPrefix=compressed/,InputCompressionType=GZIP \
    --input-format CSV \
    --input-format-options Csv={Delimiter=",",HeaderList=["UserID","Name","Email"]} \
    --table-creation-parameters '{
        "TableName": "ImportedUsersCSV",
        "AttributeDefinitions": [
            {"AttributeName": "UserID", "AttributeType": "S"}
        ],
        "KeySchema": [
            {"AttributeName": "UserID", "KeyType": "HASH"}
        ],
        "BillingMode": "PAY_PER_REQUEST"
    }'

# Describe import
aws dynamodb describe-import \
    --import-arn "arn:aws:dynamodb:us-east-1:123456789012:table/Users/import/01234567890123-abcdefgh"

# List imports
aws dynamodb list-imports \
    --table-arn "arn:aws:dynamodb:us-east-1:123456789012:table/Users"
```

### Additional Useful Commands

```bash
# Describe table limits
aws dynamodb describe-limits

# Get table contributor insights status
aws dynamodb describe-contributor-insights \
    --table-name Users

# Update contributor insights
aws dynamodb update-contributor-insights \
    --table-name Users \
    --contributor-insights-action ENABLE

# Describe kinesis streaming destination
aws dynamodb describe-kinesis-streaming-destination \
    --table-name Users

# Enable kinesis streaming
aws dynamodb enable-kinesis-streaming-destination \
    --table-name Users \
    --stream-arn "arn:aws:kinesis:us-east-1:123456789012:stream/my-stream"

# Disable kinesis streaming
aws dynamodb disable-kinesis-streaming-destination \
    --table-name Users \
    --stream-arn "arn:aws:kinesis:us-east-1:123456789012:stream/my-stream"

# Describe table replica auto scaling
aws dynamodb describe-table-replica-auto-scaling \
    --table-name GlobalUsers

# Update table replica auto scaling
aws dynamodb update-table-replica-auto-scaling \
    --table-name GlobalUsers \
    --replica-updates '[
        {
            "RegionName": "us-west-2",
            "ReplicaGlobalSecondaryIndexUpdates": [
                {
                    "IndexName": "EmailIndex",
                    "ProvisionedReadCapacityAutoScalingUpdate": {
                        "MinimumUnits": 5,
                        "MaximumUnits": 100,
                        "AutoScalingRoleArn": "arn:aws:iam::123456789012:role/DynamoDBAutoscaleRole",
                        "ScalingPolicyUpdate": {
                            "TargetTrackingScalingPolicyConfiguration": {
                                "TargetValue": 70.0
                            }
                        }
                    }
                }
            ]
        }
    ]'
```

## Exam Tips

### Key Points for SAA-C03
1. **NoSQL Use Cases**: When to choose DynamoDB over RDS
2. **Scalability**: Horizontal scaling capabilities
3. **Performance**: Single-digit millisecond latency
4. **Global Distribution**: Multi-region replication
5. **Serverless**: Fully managed, no server management

### Common Exam Scenarios
1. **High-Traffic Web Applications**: Session storage, user profiles
2. **Real-time Analytics**: Clickstream data, IoT sensors
3. **Gaming Applications**: Player data, leaderboards
4. **Mobile Applications**: Offline sync, user preferences
5. **Content Management**: Metadata storage, content delivery

### Decision Factors
- **Predictable vs Unpredictable Traffic**: Provisioned vs On-Demand
- **Consistency Requirements**: Strong vs Eventual consistency
- **Global Access**: Global Tables for multi-region
- **Real-time Processing**: DynamoDB Streams
- **Cost Sensitivity**: Reserved capacity, table classes

### Performance Considerations
- **Hot Partitions**: Even data distribution
- **Access Patterns**: Query vs Scan operations
- **Capacity Planning**: RCU/WCU calculations
- **Index Design**: GSI vs LSI trade-offs

### Integration Patterns
- **Serverless Applications**: Lambda + DynamoDB
- **API Backends**: API Gateway + DynamoDB
- **Real-time Processing**: DynamoDB Streams + Lambda
- **Analytics**: DynamoDB + Kinesis + S3

Remember: DynamoDB is often the right choice for applications requiring:
- Fast, predictable performance
- Seamless scalability
- Flexible data models
- Serverless architecture
- Global distribution
- Real-time applications

Understanding these concepts and being able to identify appropriate use cases will help you succeed in the SAA-C03 exam questions related to DynamoDB.