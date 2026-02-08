# AWS SQS (Simple Queue Service) - SAA-C03 Guide

## Table of Contents
- [Overview](#overview)
- [Key Concepts](#key-concepts)
- [Queue Types](#queue-types)
- [Message Lifecycle](#message-lifecycle)
- [Queue Configuration](#queue-configuration)
- [Security and Access Control](#security-and-access-control)
- [Monitoring and Troubleshooting](#monitoring-and-troubleshooting)
- [Best Practices](#best-practices)
- [Integration Patterns](#integration-patterns)
- [Cost Optimization](#cost-optimization)
- [AWS CLI Commands Reference](#aws-cli-commands-reference)
- [Exam Tips](#exam-tips)

---

## Overview

Amazon Simple Queue Service (SQS) is a fully managed message queuing service that enables you to decouple and scale microservices, distributed systems, and serverless applications. SQS eliminates the complexity and overhead associated with managing and operating message-oriented middleware.

### Key Benefits
- **Fully Managed**: No infrastructure to manage
- **Scalable**: Handles message volumes from a few to millions
- **Reliable**: Messages stored redundantly across multiple AZs
- **Secure**: Encryption in transit and at rest
- **Cost-Effective**: Pay only for what you use

### Use Cases
- **Application Decoupling**: Separate components for better fault tolerance
- **Batch Processing**: Queue work items for processing
- **Auto Scaling**: Buffer between varying loads
- **Microservices Communication**: Asynchronous communication between services

---

## Key Concepts

### Messages
- **Message Body**: Up to 256 KB of text data
- **Message Attributes**: Optional metadata (up to 10 attributes)
- **Message ID**: Unique identifier assigned by SQS
- **Receipt Handle**: Temporary identifier for message processing

### Visibility Timeout
- Time during which a message is invisible to other consumers after being received
- Default: 30 seconds (configurable 0 seconds to 12 hours)
- Prevents multiple consumers from processing the same message

### Long Polling vs Short Polling
- **Short Polling**: Returns immediately, even if queue is empty
- **Long Polling**: Waits for messages to arrive (up to 20 seconds)
- Long polling reduces empty responses and costs

---

## Queue Types

### Standard Queues
- **Throughput**: Nearly unlimited transactions per second
- **Delivery**: At-least-once delivery (messages may be delivered more than once)
- **Ordering**: Best-effort ordering (messages might arrive out of order)
- **Use Cases**: High throughput applications where occasional duplicates are acceptable

#### Characteristics
- Default queue type
- Distributed architecture for high availability
- Occasional duplicate messages
- Message ordering not guaranteed

### FIFO Queues
- **Throughput**: Up to 3,000 messages per second (with batching: 30,000)
- **Delivery**: Exactly-once delivery
- **Ordering**: Strict message ordering maintained
- **Queue Name**: Must end with `.fifo` suffix

#### Key Features
- **Message Groups**: Messages within same group processed in order
- **Deduplication**: Prevents duplicate messages
- **Content-Based Deduplication**: Uses SHA-256 hash of message body
- **Message Deduplication ID**: Custom deduplication identifier

#### FIFO Queue Configuration
```json
{
    "FifoQueue": true,
    "ContentBasedDeduplication": true,
    "DeduplicationScope": "messageGroup",
    "FifoThroughputLimit": "perQueue"
}
```

---

## Message Lifecycle

### 1. Message Production
```python
import boto3

sqs = boto3.client('sqs')

# Send message to standard queue
response = sqs.send_message(
    QueueUrl='https://sqs.region.amazonaws.com/account/queue-name',
    MessageBody='Hello World',
    MessageAttributes={
        'Priority': {
            'StringValue': 'High',
            'DataType': 'String'
        }
    }
)
```

### 2. Message Consumption
```python
# Receive messages
messages = sqs.receive_message(
    QueueUrl=queue_url,
    MaxNumberOfMessages=10,
    WaitTimeSeconds=20,  # Long polling
    MessageAttributeNames=['All']
)

for message in messages.get('Messages', []):
    # Process message
    print(f"Message: {message['Body']}")
    
    # Delete message after processing
    sqs.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=message['ReceiptHandle']
    )
```

### 3. Message States
1. **Sent**: Message added to queue
2. **Received**: Message retrieved by consumer
3. **Invisible**: During visibility timeout period
4. **Deleted**: Message removed from queue

---

## Queue Configuration

### Basic Settings
```yaml
Queue Configuration:
  Name: my-application-queue
  Type: Standard | FIFO
  VisibilityTimeout: 30 seconds
  MessageRetentionPeriod: 4 days (default, max 14 days)
  MaxReceiveCount: 3 (for DLQ)
  ReceiveMessageWaitTimeSeconds: 0 (short polling)
```

### Advanced Settings
- **DelaySeconds**: Delay message delivery (0-900 seconds)
- **KmsMasterKeyId**: Customer managed KMS key for encryption
- **KmsDataKeyReusePeriodSeconds**: Data key reuse period (60-86400 seconds)

### Dead Letter Queues (DLQ)
- Queue for messages that can't be processed successfully
- Configured with `maxReceiveCount` parameter
- Helps identify problematic messages
- Should be same type as source queue (Standard/FIFO)

#### DLQ Configuration
```json
{
    "RedrivePolicy": {
        "deadLetterTargetArn": "arn:aws:sqs:region:account:dlq-name",
        "maxReceiveCount": 3
    }
}
```

---

## Security and Access Control

### IAM Policies
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "sqs:SendMessage",
                "sqs:ReceiveMessage",
                "sqs:DeleteMessage"
            ],
            "Resource": "arn:aws:sqs:region:account:queue-name"
        }
    ]
}
```

### Resource-Based Policies
- SQS queue policies for cross-account access
- Grant permissions to AWS services
- Control access based on conditions

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowS3ToSendMessages",
            "Effect": "Allow",
            "Principal": {
                "Service": "s3.amazonaws.com"
            },
            "Action": "sqs:SendMessage",
            "Resource": "arn:aws:sqs:region:account:queue-name"
        }
    ]
}
```

### Encryption
#### Server-Side Encryption (SSE)
- **SSE-SQS**: AWS managed encryption keys
- **SSE-KMS**: Customer managed KMS keys
- **In Transit**: HTTPS encryption for API calls

#### Key Management
- Automatic key rotation with AWS managed keys
- Custom key policies with customer managed keys
- Data key caching for performance optimization

---

## Monitoring and Troubleshooting

### CloudWatch Metrics
- **ApproximateNumberOfMessages**: Messages available for retrieval
- **ApproximateNumberOfMessagesVisible**: Messages not being processed
- **ApproximateNumberOfMessagesNotVisible**: Messages being processed
- **NumberOfMessagesSent**: Messages added to queue
- **NumberOfMessagesReceived**: Messages retrieved from queue
- **NumberOfMessagesDeleted**: Messages deleted from queue

### Key Metrics to Monitor
```yaml
Primary Metrics:
  - Queue Depth (ApproximateNumberOfMessages)
  - Message Age (ApproximateAgeOfOldestMessage)
  - Empty Receives (NumberOfEmptyReceives)
  - Processing Time (custom metric)

Alerts:
  - Queue depth > threshold
  - Message age > acceptable limit
  - High number of empty receives
  - DLQ message count > 0
```

### CloudTrail Integration
- API call logging
- Queue creation/deletion events
- Permission changes tracking

### Troubleshooting Common Issues
1. **Messages Not Being Processed**
   - Check consumer application health
   - Verify IAM permissions
   - Review visibility timeout settings

2. **Duplicate Messages** (Standard Queues)
   - Implement idempotent processing
   - Use FIFO queues if exactly-once delivery required

3. **Message Loss**
   - Ensure proper message deletion after processing
   - Check DLQ for failed messages
   - Verify retention period settings

---

## Best Practices

### Performance Optimization
1. **Use Batching**
   ```python
   # Send messages in batches (up to 10 messages)
   sqs.send_message_batch(
       QueueUrl=queue_url,
       Entries=[
           {
               'Id': '1',
               'MessageBody': 'Message 1'
           },
           {
               'Id': '2',
               'MessageBody': 'Message 2'
           }
       ]
   )
   ```

2. **Enable Long Polling**
   - Reduces empty responses
   - Lowers costs
   - Improves efficiency

3. **Optimize Visibility Timeout**
   - Set based on processing time
   - Too short: duplicate processing
   - Too long: delayed retry processing

### Scaling Considerations
- **Horizontal Scaling**: Multiple consumers per queue
- **Message Distribution**: Use message groups in FIFO queues
- **Auto Scaling**: Scale consumers based on queue depth

### Error Handling
```python
import boto3
from botocore.exceptions import ClientError

def process_messages_with_retry():
    try:
        # Receive and process messages
        messages = sqs.receive_message(QueueUrl=queue_url)
        
        for message in messages.get('Messages', []):
            try:
                # Process message
                process_message(message['Body'])
                
                # Delete on success
                sqs.delete_message(
                    QueueUrl=queue_url,
                    ReceiptHandle=message['ReceiptHandle']
                )
            except Exception as e:
                # Log error, message will become visible again
                print(f"Processing failed: {e}")
                
    except ClientError as e:
        print(f"SQS error: {e}")
```

### Security Best Practices
1. **Principle of Least Privilege**: Grant minimum required permissions
2. **Use IAM Roles**: For EC2 instances and Lambda functions
3. **Enable Encryption**: For sensitive data
4. **Monitor Access**: Use CloudTrail for auditing
5. **Validate Input**: Sanitize message content

---

## Integration Patterns

### Lambda Integration
```python
import json
import boto3

def lambda_handler(event, context):
    # Lambda automatically handles SQS message processing
    for record in event['Records']:
        message_body = record['body']
        
        # Process message
        result = process_message(message_body)
        
        # Lambda automatically deletes message on success
        # Sends to DLQ on repeated failures
    
    return {
        'statusCode': 200,
        'body': json.dumps('Messages processed successfully')
    }
```

### S3 Event Integration
```json
{
    "Rules": [
        {
            "Name": "S3ToSQS",
            "EventPattern": {
                "source": ["aws.s3"],
                "detail-type": ["Object Created"]
            },
            "Targets": [
                {
                    "Id": "SQSTarget",
                    "Arn": "arn:aws:sqs:region:account:queue-name"
                }
            ]
        }
    ]
}
```

### SNS Fan-Out Pattern
```yaml
Architecture:
  SNS Topic -> Multiple SQS Queues
  Benefits:
    - Message filtering
    - Multiple processing paths
    - Decoupled consumers
```

### API Gateway Integration
```python
# API Gateway can send messages directly to SQS
{
    "Action": "SendMessage",
    "MessageBody": "$input.body",
    "QueueUrl": "https://sqs.region.amazonaws.com/account/queue"
}
```

---

## Cost Optimization

### Pricing Model
- **Request Charges**: Per API call (send, receive, delete)
- **Data Transfer**: Standard AWS data transfer rates
- **KMS**: Additional charges for customer managed keys

### Cost Optimization Strategies
1. **Use Batching**: Reduce number of API calls
2. **Enable Long Polling**: Reduce empty receive calls
3. **Right-Size Message Retention**: Don't keep messages longer than needed
4. **Monitor Usage**: Use Cost Explorer and billing alerts
5. **Choose Appropriate Queue Type**: Standard vs FIFO based on requirements

### Free Tier
- 1 million requests per month
- Applies to both Standard and FIFO queues

---

## AWS CLI Commands Reference

### Create Queues

#### Create Standard Queue
```bash
# Create a basic standard queue
aws sqs create-queue --queue-name MyStandardQueue

# Create standard queue with attributes
aws sqs create-queue \
  --queue-name MyConfiguredQueue \
  --attributes '{
    "DelaySeconds": "5",
    "MaximumMessageSize": "262144",
    "MessageRetentionPeriod": "345600",
    "ReceiveMessageWaitTimeSeconds": "20",
    "VisibilityTimeout": "30"
  }'

# Create queue with tags
aws sqs create-queue \
  --queue-name MyTaggedQueue \
  --tags Environment=Production,Application=WebApp,CostCenter=Engineering
```

#### Create FIFO Queue
```bash
# Create basic FIFO queue
aws sqs create-queue \
  --queue-name MyFIFOQueue.fifo \
  --attributes FifoQueue=true

# Create FIFO queue with content-based deduplication
aws sqs create-queue \
  --queue-name MyDedupQueue.fifo \
  --attributes '{
    "FifoQueue": "true",
    "ContentBasedDeduplication": "true"
  }'

# Create high-throughput FIFO queue
aws sqs create-queue \
  --queue-name MyHighThroughputQueue.fifo \
  --attributes '{
    "FifoQueue": "true",
    "DeduplicationScope": "messageGroup",
    "FifoThroughputLimit": "perMessageGroupId"
  }'
```

### List and Get Queue Information

```bash
# List all queues
aws sqs list-queues

# List queues with name prefix
aws sqs list-queues --queue-name-prefix MyApp

# Get queue URL by name
aws sqs get-queue-url --queue-name MyStandardQueue

# Get queue attributes
aws sqs get-queue-attributes \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/MyStandardQueue \
  --attribute-names All

# Get specific queue attributes
aws sqs get-queue-attributes \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/MyStandardQueue \
  --attribute-names ApproximateNumberOfMessages VisibilityTimeout
```

### Send Messages

#### Send to Standard Queue
```bash
# Send simple message
aws sqs send-message \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/MyStandardQueue \
  --message-body "Hello from SQS!"

# Send message with delay
aws sqs send-message \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/MyStandardQueue \
  --message-body "Delayed message" \
  --delay-seconds 60

# Send message with attributes
aws sqs send-message \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/MyStandardQueue \
  --message-body "Order notification" \
  --message-attributes '{
    "OrderId": {"DataType":"String","StringValue":"12345"},
    "Amount": {"DataType":"Number","StringValue":"99.99"},
    "Priority": {"DataType":"String","StringValue":"high"}
  }'

# Send message from file
aws sqs send-message \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/MyStandardQueue \
  --message-body file://message.txt
```

#### Send to FIFO Queue
```bash
# Send message to FIFO queue with message group
aws sqs send-message \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/MyFIFOQueue.fifo \
  --message-body "First FIFO message" \
  --message-group-id "order-group-1" \
  --message-deduplication-id "unique-id-1"

# Send with content-based deduplication enabled
aws sqs send-message \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/MyDedupQueue.fifo \
  --message-body "This message uses content-based dedup" \
  --message-group-id "order-group-1"
```

#### Batch Send Messages
```bash
# Send batch of messages to standard queue
aws sqs send-message-batch \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/MyStandardQueue \
  --entries '[
    {"Id":"1","MessageBody":"First message"},
    {"Id":"2","MessageBody":"Second message","DelaySeconds":10},
    {"Id":"3","MessageBody":"Third message"}
  ]'

# Send batch to FIFO queue
aws sqs send-message-batch \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/MyFIFOQueue.fifo \
  --entries file://batch-messages.json

# Example batch-messages.json for FIFO:
# [
#   {
#     "Id": "1",
#     "MessageBody": "First ordered message",
#     "MessageGroupId": "group1",
#     "MessageDeduplicationId": "dedup1"
#   },
#   {
#     "Id": "2",
#     "MessageBody": "Second ordered message",
#     "MessageGroupId": "group1",
#     "MessageDeduplicationId": "dedup2"
#   }
# ]
```

### Receive Messages

#### Short Polling (Default)
```bash
# Receive one message
aws sqs receive-message \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/MyStandardQueue

# Receive multiple messages (up to 10)
aws sqs receive-message \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/MyStandardQueue \
  --max-number-of-messages 10

# Receive with message attributes
aws sqs receive-message \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/MyStandardQueue \
  --attribute-names All \
  --message-attribute-names All
```

#### Long Polling
```bash
# Enable long polling for this receive request (up to 20 seconds)
aws sqs receive-message \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/MyStandardQueue \
  --wait-time-seconds 20 \
  --max-number-of-messages 10

# Long polling helps reduce empty responses and costs
```

#### Receive with Visibility Timeout Override
```bash
# Change visibility timeout for received messages
aws sqs receive-message \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/MyStandardQueue \
  --visibility-timeout 300 \
  --max-number-of-messages 5
```

### Delete Messages

```bash
# Delete single message (requires receipt handle from receive-message)
aws sqs delete-message \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/MyStandardQueue \
  --receipt-handle "AQEBzWwaKH...ReceiptHandleFromReceiveMessage"

# Delete batch of messages
aws sqs delete-message-batch \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/MyStandardQueue \
  --entries '[
    {"Id":"1","ReceiptHandle":"AQEBzWwaKH..."},
    {"Id":"2","ReceiptHandle":"AQEBwXuKL..."}
  ]'
```

### Change Message Visibility

```bash
# Extend visibility timeout for a message being processed
aws sqs change-message-visibility \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/MyStandardQueue \
  --receipt-handle "AQEBzWwaKH..." \
  --visibility-timeout 600

# Change visibility for multiple messages
aws sqs change-message-visibility-batch \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/MyStandardQueue \
  --entries '[
    {"Id":"1","ReceiptHandle":"AQEBzWwaKH...","VisibilityTimeout":300},
    {"Id":"2","ReceiptHandle":"AQEBwXuKL...","VisibilityTimeout":300}
  ]'
```

### Purge Queue

```bash
# Delete all messages in queue (cannot be undone)
aws sqs purge-queue \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/MyStandardQueue

# Note: Can only purge once every 60 seconds
```

### Configure Queue Attributes

#### Visibility Timeout
```bash
# Set visibility timeout (0 seconds to 12 hours)
aws sqs set-queue-attributes \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/MyStandardQueue \
  --attributes VisibilityTimeout=300
```

#### Message Retention Period
```bash
# Set retention period (60 seconds to 14 days)
aws sqs set-queue-attributes \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/MyStandardQueue \
  --attributes MessageRetentionPeriod=1209600
```

#### Delivery Delay
```bash
# Set default delay for all messages (0 to 900 seconds)
aws sqs set-queue-attributes \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/MyStandardQueue \
  --attributes DelaySeconds=30
```

#### Maximum Message Size
```bash
# Set max message size (1,024 bytes to 262,144 bytes)
aws sqs set-queue-attributes \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/MyStandardQueue \
  --attributes MaximumMessageSize=131072
```

#### Enable Long Polling
```bash
# Set receive message wait time for long polling
aws sqs set-queue-attributes \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/MyStandardQueue \
  --attributes ReceiveMessageWaitTimeSeconds=20
```

### Dead Letter Queue (DLQ) Configuration

```bash
# Configure DLQ for a queue
aws sqs set-queue-attributes \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/MyStandardQueue \
  --attributes '{
    "RedrivePolicy": "{
      \"deadLetterTargetArn\":\"arn:aws:sqs:us-east-1:123456789012:MyDLQ\",
      \"maxReceiveCount\":\"3\"
    }"
  }'

# Remove DLQ configuration
aws sqs set-queue-attributes \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/MyStandardQueue \
  --attributes RedrivePolicy=""

# Configure redrive allow policy on DLQ (specify which queues can use this DLQ)
aws sqs set-queue-attributes \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/MyDLQ \
  --attributes '{
    "RedriveAllowPolicy": "{
      \"redrivePermission\":\"byQueue\",
      \"sourceQueueArns\":[
        \"arn:aws:sqs:us-east-1:123456789012:MyStandardQueue\",
        \"arn:aws:sqs:us-east-1:123456789012:MyOtherQueue\"
      ]
    }"
  }'
```

### Server-Side Encryption (SSE)

```bash
# Enable SSE with AWS managed key (SSE-SQS)
aws sqs set-queue-attributes \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/MyStandardQueue \
  --attributes SqsManagedSseEnabled=true

# Enable SSE with customer managed KMS key (SSE-KMS)
aws sqs set-queue-attributes \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/MyStandardQueue \
  --attributes '{
    "KmsMasterKeyId": "arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012",
    "KmsDataKeyReusePeriodSeconds": "300"
  }'

# Disable SSE
aws sqs set-queue-attributes \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/MyStandardQueue \
  --attributes SqsManagedSseEnabled=false
```

### Queue Policies

```bash
# Set queue policy for cross-account access
aws sqs set-queue-attributes \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/MyStandardQueue \
  --attributes Policy='{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"AWS":"arn:aws:iam::999999999999:root"},"Action":"sqs:SendMessage","Resource":"arn:aws:sqs:us-east-1:123456789012:MyStandardQueue"}]}'

# Allow SNS topic to send messages to queue
aws sqs set-queue-attributes \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/MyStandardQueue \
  --attributes Policy='{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"sns.amazonaws.com"},"Action":"sqs:SendMessage","Resource":"arn:aws:sqs:us-east-1:123456789012:MyStandardQueue","Condition":{"ArnEquals":{"aws:SourceArn":"arn:aws:sns:us-east-1:123456789012:MyTopic"}}}]}'

# Allow S3 to send event notifications
aws sqs set-queue-attributes \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/MyStandardQueue \
  --attributes Policy='{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"s3.amazonaws.com"},"Action":"sqs:SendMessage","Resource":"arn:aws:sqs:us-east-1:123456789012:MyStandardQueue","Condition":{"ArnLike":{"aws:SourceArn":"arn:aws:s3:::my-bucket"}}}]}'
```

### FIFO Queue Specific Operations

#### Deduplication Configuration
```bash
# Enable content-based deduplication
aws sqs set-queue-attributes \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/MyFIFOQueue.fifo \
  --attributes ContentBasedDeduplication=true

# Configure deduplication scope and throughput
aws sqs set-queue-attributes \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/MyFIFOQueue.fifo \
  --attributes '{
    "DeduplicationScope": "messageGroup",
    "FifoThroughputLimit": "perMessageGroupId"
  }'
```

### Tags Management

```bash
# Add tags to queue
aws sqs tag-queue \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/MyStandardQueue \
  --tags Environment=Production CostCenter=Engineering Application=OrderProcessing

# List tags for queue
aws sqs list-queue-tags \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/MyStandardQueue

# Remove tags from queue
aws sqs untag-queue \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/MyStandardQueue \
  --tag-keys Environment CostCenter
```

### Delete Queue

```bash
# Delete queue (cannot be undone, deletes all messages)
aws sqs delete-queue \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/MyStandardQueue
```

### Advanced Operations

#### List Dead Letter Source Queues
```bash
# Find queues using this queue as DLQ
aws sqs list-dead-letter-source-queues \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/MyDLQ
```

#### Start Message Move Task
```bash
# Move messages from DLQ back to source queue
aws sqs start-message-move-task \
  --source-arn arn:aws:sqs:us-east-1:123456789012:MyDLQ \
  --destination-arn arn:aws:sqs:us-east-1:123456789012:MyStandardQueue \
  --max-number-of-messages-per-second 10

# List message move tasks
aws sqs list-message-move-tasks \
  --source-arn arn:aws:sqs:us-east-1:123456789012:MyDLQ

# Cancel message move task
aws sqs cancel-message-move-task \
  --task-handle <task-handle-from-start>
```

### Monitoring Commands

```bash
# Get approximate number of messages
aws sqs get-queue-attributes \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/MyStandardQueue \
  --attribute-names ApproximateNumberOfMessages ApproximateNumberOfMessagesNotVisible ApproximateNumberOfMessagesDelayed

# Get queue creation and modification timestamps
aws sqs get-queue-attributes \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/MyStandardQueue \
  --attribute-names CreatedTimestamp LastModifiedTimestamp
```

### Useful Query Examples

```bash
# Get all queue URLs and format as list
aws sqs list-queues --output text

# Get queue URL by name and store in variable
QUEUE_URL=$(aws sqs get-queue-url --queue-name MyStandardQueue --output text)

# Count approximate messages in queue
aws sqs get-queue-attributes \
  --queue-url $QUEUE_URL \
  --attribute-names ApproximateNumberOfMessages \
  --query 'Attributes.ApproximateNumberOfMessages' \
  --output text

# Send and receive in a script
#!/bin/bash
QUEUE_URL="https://sqs.us-east-1.amazonaws.com/123456789012/MyQueue"

# Send message
aws sqs send-message --queue-url $QUEUE_URL --message-body "Test message"

# Receive message
MESSAGE=$(aws sqs receive-message --queue-url $QUEUE_URL)
RECEIPT_HANDLE=$(echo $MESSAGE | jq -r '.Messages[0].ReceiptHandle')

# Process message (your logic here)
echo "Processing message..."

# Delete message after processing
aws sqs delete-message --queue-url $QUEUE_URL --receipt-handle $RECEIPT_HANDLE
```

---

## Exam Tips

### Key Points for SAA-C03
1. **Queue Types**: Understand Standard vs FIFO differences
2. **Visibility Timeout**: How it prevents duplicate processing
3. **Dead Letter Queues**: For handling failed messages
4. **Polling Types**: Long vs short polling implications
5. **Security**: IAM policies vs resource-based policies
6. **Integration**: With Lambda, S3, SNS, API Gateway

### Common Exam Scenarios
1. **Decoupling Application Components**
   - Use SQS between web tier and processing tier
   - Handle traffic spikes with queue buffering

2. **Batch Processing**
   - Queue jobs for background processing
   - Scale workers based on queue depth

3. **Event-Driven Architecture**
   - S3 → SQS → Lambda processing pipeline
   - SNS fan-out to multiple SQS queues

4. **Error Handling**
   - DLQ for failed message processing
   - Retry mechanisms with visibility timeout

### Sample Questions Focus Areas
- **Choosing queue type** based on requirements
- **Configuring visibility timeout** for processing time
- **Setting up DLQ** for error handling
- **Integration patterns** with other AWS services
- **Security configurations** for cross-account access
- **Cost optimization** strategies

### Key Differentiators
| Feature | Standard Queue | FIFO Queue |
|---------|---------------|------------|
| Throughput | Nearly unlimited | 3,000 msgs/sec (30K with batching) |
| Delivery | At-least-once | Exactly-once |
| Ordering | Best-effort | Strict FIFO |
| Duplicates | Possible | No duplicates |
| Naming | Any valid name | Must end with .fifo |

---

## Conclusion

Amazon SQS is a fundamental service for building scalable, decoupled applications in AWS. Understanding its queue types, configuration options, and integration patterns is crucial for the SAA-C03 exam. Focus on practical scenarios involving application decoupling, error handling, and cost optimization when preparing for exam questions.

Remember to consider SQS as a solution for:
- **Application decoupling** requirements
- **Asynchronous processing** needs
- **Buffer management** for varying loads
- **Error handling** with DLQ patterns
- **Event-driven architectures** with other AWS services