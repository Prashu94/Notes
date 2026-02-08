# AWS Simple Notification Service (SNS) - SAA-C03 Study Guide

## Table of Contents
1. [Overview](#overview)
2. [Core Concepts](#core-concepts)
3. [SNS Components](#sns-components)
4. [Message Types and Protocols](#message-types-and-protocols)
5. [SNS Integrations](#sns-integrations)
6. [Security and Access Control](#security-and-access-control)
7. [Monitoring and Troubleshooting](#monitoring-and-troubleshooting)
8. [Best Practices](#best-practices)
9. [Pricing](#pricing)
10. [Common Exam Scenarios](#common-exam-scenarios)
11. [AWS CLI Commands Reference](#aws-cli-commands-reference)
12. [Hands-on Labs](#hands-on-labs)

---

## Overview

Amazon Simple Notification Service (SNS) is a fully managed messaging service that enables you to decouple microservices, distributed systems, and serverless applications. SNS provides topics for high-throughput, push-based, many-to-many messaging.

### Key Features
- **Pub/Sub Messaging**: Publisher sends messages to topics, subscribers receive messages
- **Multiple Protocol Support**: SMS, Email, HTTP/HTTPS, SQS, Lambda, Platform Applications
- **Message Filtering**: Route messages to specific subscribers based on message attributes
- **Message Delivery Status**: Track delivery success/failure for supported endpoints
- **Dead Letter Queues**: Handle failed message deliveries
- **FIFO Topics**: Maintain message ordering and exactly-once delivery
- **Server-Side Encryption**: Encrypt messages at rest and in transit

---

## Core Concepts

### Topics
A communication channel where publishers send messages and subscribers receive notifications.

**Standard Topics:**
- Best-effort ordering
- At-least-once delivery
- High throughput (unlimited)
- Duplicate messages possible

**FIFO Topics:**
- First-in-first-out delivery
- Exactly-once processing
- Limited throughput (3,000 messages/second with batching, 300/second without)
- No duplicate messages
- Message deduplication
- Content-based deduplication available

### Publishers
Applications that send messages to SNS topics:
- AWS services (CloudWatch, S3, etc.)
- Applications using AWS SDK
- AWS CLI
- AWS Management Console

### Subscribers
Endpoints that receive messages from topics:
- Email addresses
- SMS phone numbers
- HTTP/HTTPS endpoints
- SQS queues
- Lambda functions
- Platform applications (mobile push)

---

## SNS Components

### Message Structure
```json
{
  "Type": "Notification",
  "MessageId": "22b80b92-fdea-4c2c-8f9d-bdfb0c7bf324",
  "TopicArn": "arn:aws:sns:us-west-2:123456789012:MyTopic",
  "Subject": "My First Message",
  "Message": "Hello world!",
  "Timestamp": "2012-05-02T00:54:06.655Z",
  "SignatureVersion": "1",
  "Signature": "...",
  "SigningCertURL": "...",
  "UnsubscribeURL": "..."
}
```

### Message Attributes
Key-value pairs that provide metadata about the message:
- Up to 10 attributes per message
- Used for message filtering
- Data types: String, Number, Binary, String.Array, Number.Array

### Message Filtering
Filter messages using message attributes:

```json
{
  "store": ["example_corp"],
  "price_usd": [{"numeric": [">=", 100]}],
  "event_type": ["order-placed"]
}
```

---

## Message Types and Protocols

### Email
- **Email**: Plain text notifications
- **Email-JSON**: Full SNS message payload in JSON format
- Confirmation required for new subscriptions
- Unsubscribe link included in emails

### SMS
- Text messages to mobile phones
- Character limit: 160 characters (140 for some countries)
- Delivery status tracking available
- Opt-out compliance built-in

### HTTP/HTTPS
- POST requests to web endpoints
- Must return 200 status code for successful delivery
- Confirmation and unsubscribe URLs provided
- Custom headers supported

### SQS Integration
- Decouple SNS from downstream processing
- Fan-out pattern: One message to multiple queues
- Cross-account delivery supported
- Dead letter queue integration

### Lambda Integration
- Trigger Lambda functions directly
- Automatic retry with exponential backoff
- Error handling and DLQ support
- Parallel execution for multiple functions

### Platform Applications
- iOS: Apple Push Notification Service (APNS)
- Android: Firebase Cloud Messaging (FCM)
- Windows: Windows Push Notification Service (WNS)
- Amazon: Amazon Device Messaging (ADM)

---

## SNS Integrations

### AWS Service Integrations

#### CloudWatch Alarms
```bash
# Create CloudWatch alarm that publishes to SNS
aws cloudwatch put-metric-alarm \
  --alarm-name "HighCPUUtilization" \
  --alarm-description "Alarm when CPU exceeds 70%" \
  --metric-name CPUUtilization \
  --namespace AWS/EC2 \
  --statistic Average \
  --period 300 \
  --threshold 70 \
  --comparison-operator GreaterThanThreshold \
  --alarm-actions arn:aws:sns:us-east-1:123456789012:my-topic
```

#### S3 Event Notifications
- Object creation/deletion events
- Replication events
- Restore events
- Configure in bucket properties or via CloudFormation

#### Auto Scaling
- Scale-out/scale-in notifications
- Instance launch/terminate notifications
- Health check failures

#### RDS Events
- DB instance events
- DB cluster events
- DB parameter group events
- DB security group events

### Cross-Service Patterns

#### SNS + SQS Fan-out
```yaml
# CloudFormation template
Resources:
  MyTopic:
    Type: AWS::SNS::Topic
    Properties:
      TopicName: OrderProcessing
      
  OrderQueue:
    Type: AWS::SQS::Queue
    Properties:
      QueueName: OrderProcessingQueue
      
  InventoryQueue:
    Type: AWS::SQS::Queue
    Properties:
      QueueName: InventoryUpdateQueue
      
  OrderSubscription:
    Type: AWS::SNS::Subscription
    Properties:
      TopicArn: !Ref MyTopic
      Protocol: sqs
      Endpoint: !GetAtt OrderQueue.Arn
      
  InventorySubscription:
    Type: AWS::SNS::Subscription
    Properties:
      TopicArn: !Ref MyTopic
      Protocol: sqs
      Endpoint: !GetAtt InventoryQueue.Arn
```

#### SNS + Lambda Processing
- Real-time event processing
- Serverless microservices
- Error handling with DLQ

---

## Security and Access Control

### IAM Policies

#### Topic Policy Example
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "s3.amazonaws.com"
      },
      "Action": "sns:Publish",
      "Resource": "arn:aws:sns:us-east-1:123456789012:my-topic",
      "Condition": {
        "StringEquals": {
          "aws:SourceAccount": "123456789012"
        }
      }
    }
  ]
}
```

#### Cross-Account Access
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::111122223333:root"
      },
      "Action": [
        "sns:Subscribe",
        "sns:Receive"
      ],
      "Resource": "arn:aws:sns:us-east-1:123456789012:my-topic"
    }
  ]
}
```

### Encryption

#### Server-Side Encryption (SSE)
- **SSE-KMS**: Customer managed or AWS managed keys
- **SSE-SQS**: For SQS queue subscriptions
- In-transit encryption for HTTPS endpoints

#### KMS Key Policy
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "sns.amazonaws.com"
      },
      "Action": [
        "kms:Encrypt",
        "kms:Decrypt",
        "kms:ReEncrypt*",
        "kms:GenerateDataKey*",
        "kms:DescribeKey"
      ],
      "Resource": "*"
    }
  ]
}
```

### VPC Endpoints
- Private connectivity to SNS from VPC
- No internet gateway required
- Enhanced security for VPC-based applications

---

## Monitoring and Troubleshooting

### CloudWatch Metrics

#### Topic Metrics
- `NumberOfMessagesPublished`: Messages sent to topic
- `NumberOfNotificationsDelivered`: Successfully delivered messages
- `NumberOfNotificationsFailed`: Failed deliveries
- `PublishSize`: Size of published messages

#### Subscription Metrics
- `NumberOfMessagesPublished`: Per subscription
- `NumberOfNotificationsDelivered`: Per subscription
- `NumberOfNotificationsFailed`: Per subscription

### CloudWatch Logs
Enable logging for message delivery status:
```json
{
  "DeliveryStatusLogging": [
    {
      "Protocol": "lambda",
      "SuccessFeedbackRoleArn": "arn:aws:iam::123456789012:role/SNSSuccessRole",
      "SuccessFeedbackSampleRate": 100,
      "FailureFeedbackRoleArn": "arn:aws:iam::123456789012:role/SNSFailureRole"
    }
  ]
}
```

### X-Ray Tracing
- Trace message flow through distributed systems
- Identify bottlenecks and latency issues
- Integration with Lambda and other AWS services

### Common Issues and Solutions

#### Message Delivery Failures
- **HTTP/HTTPS**: Check endpoint availability, return codes
- **Email**: Verify email addresses, check spam folders
- **SMS**: Verify phone numbers, check opt-out status
- **SQS**: Check queue permissions, queue existence

#### FIFO Topic Issues
- Message deduplication errors
- Content-based deduplication conflicts
- Throughput limitations

#### Permission Errors
- Check IAM policies and topic policies
- Verify cross-account permissions
- KMS key permissions for encrypted topics

---

## Best Practices

### Message Design
1. **Keep Messages Small**: Under 256 KB limit
2. **Use Message Attributes**: For filtering and routing
3. **Include Correlation IDs**: For tracking and debugging
4. **Design for Idempotency**: Handle duplicate messages gracefully

### Topic Design
1. **Use Descriptive Names**: Clear naming conventions
2. **Separate Concerns**: Different topics for different event types
3. **Consider Message Volume**: Standard vs FIFO based on requirements
4. **Plan for Growth**: Consider scaling implications

### Subscription Management
1. **Confirm Subscriptions**: Ensure all subscriptions are confirmed
2. **Monitor Health**: Use CloudWatch metrics
3. **Handle Unsubscribes**: Respect opt-out requests
4. **Use Dead Letter Queues**: Handle failed deliveries

### Security Best Practices
1. **Principle of Least Privilege**: Minimal required permissions
2. **Enable Encryption**: Use KMS for sensitive data
3. **Use VPC Endpoints**: For VPC-based applications
4. **Monitor Access**: CloudTrail logging for API calls

### Cost Optimization
1. **Message Filtering**: Reduce unnecessary deliveries
2. **Batch Operations**: Use batch APIs where available
3. **Monitor Usage**: Track costs with CloudWatch
4. **Choose Appropriate Protocols**: Consider costs of different delivery methods

---

## Pricing

### Standard Topics
- **Requests**: $0.50 per 1 million SNS requests
- **HTTP/HTTPS**: $0.60 per 1 million notifications
- **Email**: $2.00 per 100,000 notifications
- **SMS**: Variable by destination (US: $0.00645 per SMS)
- **Mobile Push**: $0.50 per 1 million notifications

### FIFO Topics
- **Requests**: $0.50 per 1 million SNS requests
- **Deliveries**: Same as standard topics

### Additional Costs
- **Data Transfer**: Standard AWS data transfer rates
- **KMS Encryption**: KMS key usage charges
- **CloudWatch Logs**: If delivery status logging enabled

### Free Tier
- 1 million SNS requests per month
- 100,000 HTTP/HTTPS notifications
- 100,000 email notifications
- 1,000 SMS notifications

---

## Common Exam Scenarios

### Scenario 1: Application Decoupling
**Question**: A company needs to decouple microservices and ensure messages are processed by multiple services.

**Solution**: Use SNS with SQS fan-out pattern. Create SNS topic and subscribe multiple SQS queues to it.

### Scenario 2: Real-time Notifications
**Question**: Send immediate notifications to mobile apps and email when critical events occur.

**Solution**: Use SNS with platform applications for mobile push and email subscriptions for email notifications.

### Scenario 3: Event-Driven Processing
**Question**: Trigger multiple Lambda functions when S3 objects are uploaded.

**Solution**: Configure S3 event notifications to publish to SNS topic, subscribe Lambda functions to the topic.

### Scenario 4: Ordered Message Processing
**Question**: Ensure messages are processed in order with exactly-once delivery.

**Solution**: Use SNS FIFO topics with SQS FIFO queues for ordered, exactly-once processing.

### Scenario 5: Cross-Account Notifications
**Question**: Send notifications from one AWS account to resources in another account.

**Solution**: Configure cross-account SNS topic policy and IAM roles for proper permissions.

### Key Decision Factors
1. **Message Ordering**: Standard vs FIFO topics
2. **Delivery Guarantees**: At-least-once vs exactly-once
3. **Throughput Requirements**: Standard (unlimited) vs FIFO (limited)
4. **Protocol Requirements**: Email, SMS, HTTP, SQS, Lambda, Mobile
5. **Security Requirements**: Encryption, VPC endpoints, cross-account access

---

## AWS CLI Commands Reference

### Create and Manage Topics

#### Create Standard Topic
```bash
# Create a standard SNS topic
aws sns create-topic --name MyStandardTopic

# Create topic with display name
aws sns create-topic \
  --name MyTopic \
  --attributes DisplayName="My Production Topic"

# Create topic with tags
aws sns create-topic \
  --name MyTaggedTopic \
  --tags Key=Environment,Value=Production Key=Application,Value=WebApp
```

#### Create FIFO Topic
```bash
# Create FIFO topic with content-based deduplication
aws sns create-topic \
  --name MyFIFOTopic.fifo \
  --attributes FifoTopic=true,ContentBasedDeduplication=true

# Create FIFO topic without content-based deduplication
aws sns create-topic \
  --name MyFIFOTopic.fifo \
  --attributes FifoTopic=true,ContentBasedDeduplication=false
```

#### List and Get Topics
```bash
# List all topics
aws sns list-topics

# List topics with pagination
aws sns list-topics --max-items 10

# Get topic attributes
aws sns get-topic-attributes \
  --topic-arn arn:aws:sns:us-east-1:123456789012:MyTopic
```

#### Configure Topic Attributes
```bash
# Set topic display name
aws sns set-topic-attributes \
  --topic-arn arn:aws:sns:us-east-1:123456789012:MyTopic \
  --attribute-name DisplayName \
  --attribute-value "Production Alerts"

# Enable server-side encryption with AWS managed key
aws sns set-topic-attributes \
  --topic-arn arn:aws:sns:us-east-1:123456789012:MyTopic \
  --attribute-name KmsMasterKeyId \
  --attribute-value alias/aws/sns

# Enable server-side encryption with customer managed key
aws sns set-topic-attributes \
  --topic-arn arn:aws:sns:us-east-1:123456789012:MyTopic \
  --attribute-name KmsMasterKeyId \
  --attribute-value arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012

# Set delivery status logging for Lambda
aws sns set-topic-attributes \
  --topic-arn arn:aws:sns:us-east-1:123456789012:MyTopic \
  --attribute-name LambdaSuccessFeedbackRoleArn \
  --attribute-value arn:aws:iam::123456789012:role/SNSSuccessFeedback

# Set delivery policy for retries
aws sns set-topic-attributes \
  --topic-arn arn:aws:sns:us-east-1:123456789012:MyTopic \
  --attribute-name DeliveryPolicy \
  --attribute-value '{"http":{"defaultHealthyRetryPolicy":{"minDelayTarget":20,"maxDelayTarget":20,"numRetries":3}}}'
```

#### Delete Topic
```bash
# Delete SNS topic (also deletes all subscriptions)
aws sns delete-topic \
  --topic-arn arn:aws:sns:us-east-1:123456789012:MyTopic
```

### Manage Subscriptions

#### Email Subscriptions
```bash
# Subscribe email address to topic
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:123456789012:MyTopic \
  --protocol email \
  --notification-endpoint user@example.com

# Subscribe with return subscription ARN
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:123456789012:MyTopic \
  --protocol email \
  --notification-endpoint user@example.com \
  --return-subscription-arn

# Subscribe email-json (receives full JSON message)
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:123456789012:MyTopic \
  --protocol email-json \
  --notification-endpoint admin@example.com
```

#### SMS Subscriptions
```bash
# Subscribe phone number to topic
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:123456789012:MyTopic \
  --protocol sms \
  --notification-endpoint +1234567890

# Set SMS attributes for account
aws sns set-sms-attributes \
  --attributes DefaultSMSType=Transactional

# Get SMS attributes
aws sns get-sms-attributes
```

#### HTTP/HTTPS Subscriptions
```bash
# Subscribe HTTP endpoint
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:123456789012:MyTopic \
  --protocol http \
  --notification-endpoint http://example.com/sns-endpoint

# Subscribe HTTPS endpoint
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:123456789012:MyTopic \
  --protocol https \
  --notification-endpoint https://example.com/sns-endpoint
```

#### Lambda Subscriptions
```bash
# Subscribe Lambda function to topic
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:123456789012:MyTopic \
  --protocol lambda \
  --notification-endpoint arn:aws:lambda:us-east-1:123456789012:function:MyFunction

# Add Lambda permission for SNS to invoke
aws lambda add-permission \
  --function-name MyFunction \
  --statement-id sns-invoke \
  --action lambda:InvokeFunction \
  --principal sns.amazonaws.com \
  --source-arn arn:aws:sns:us-east-1:123456789012:MyTopic
```

#### SQS Subscriptions
```bash
# Subscribe SQS queue to topic
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:123456789012:MyTopic \
  --protocol sqs \
  --notification-endpoint arn:aws:sqs:us-east-1:123456789012:MyQueue

# Subscribe SQS FIFO queue to SNS FIFO topic
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:123456789012:MyFIFOTopic.fifo \
  --protocol sqs \
  --notification-endpoint arn:aws:sqs:us-east-1:123456789012:MyQueue.fifo
```

#### List and Manage Subscriptions
```bash
# List all subscriptions
aws sns list-subscriptions

# List subscriptions for a specific topic
aws sns list-subscriptions-by-topic \
  --topic-arn arn:aws:sns:us-east-1:123456789012:MyTopic

# Get subscription attributes
aws sns get-subscription-attributes \
  --subscription-arn arn:aws:sns:us-east-1:123456789012:MyTopic:12345678-1234-1234-1234-123456789012

# Confirm pending subscription (for HTTP/HTTPS/Email)
aws sns confirm-subscription \
  --topic-arn arn:aws:sns:us-east-1:123456789012:MyTopic \
  --token <token-from-confirmation-message>

# Unsubscribe from topic
aws sns unsubscribe \
  --subscription-arn arn:aws:sns:us-east-1:123456789012:MyTopic:12345678-1234-1234-1234-123456789012
```

### Publish Messages

#### Publish to Standard Topic
```bash
# Publish simple message
aws sns publish \
  --topic-arn arn:aws:sns:us-east-1:123456789012:MyTopic \
  --message "Hello from SNS!"

# Publish message with subject
aws sns publish \
  --topic-arn arn:aws:sns:us-east-1:123456789012:MyTopic \
  --message "Important notification" \
  --subject "Alert: System Status"

# Publish message from file
aws sns publish \
  --topic-arn arn:aws:sns:us-east-1:123456789012:MyTopic \
  --message file://message.txt

# Publish JSON message
aws sns publish \
  --topic-arn arn:aws:sns:us-east-1:123456789012:MyTopic \
  --message '{"status":"active","count":42}'
```

#### Publish to FIFO Topic
```bash
# Publish to FIFO topic with message group ID
aws sns publish \
  --topic-arn arn:aws:sns:us-east-1:123456789012:MyFIFOTopic.fifo \
  --message "Ordered message 1" \
  --message-group-id "order-group-1" \
  --message-deduplication-id "unique-id-1"

# Publish to FIFO topic with content-based deduplication
aws sns publish \
  --topic-arn arn:aws:sns:us-east-1:123456789012:MyFIFOTopic.fifo \
  --message "This message will be deduplicated based on content" \
  --message-group-id "order-group-1"
```

#### Publish to Phone Number (Direct SMS)
```bash
# Send SMS directly to phone number (no topic needed)
aws sns publish \
  --phone-number +1234567890 \
  --message "Your verification code is 123456"

# Send SMS with sender ID
aws sns publish \
  --phone-number +1234567890 \
  --message "Your order has shipped!" \
  --message-attributes '{"AWS.SNS.SMS.SenderID":{"DataType":"String","StringValue":"MyCompany"}}'
```

### Message Attributes

#### Publish with Message Attributes
```bash
# Publish message with string attributes
aws sns publish \
  --topic-arn arn:aws:sns:us-east-1:123456789012:MyTopic \
  --message "Order placed" \
  --message-attributes '{
    "store": {"DataType":"String", "StringValue":"example_store"},
    "customer_type": {"DataType":"String", "StringValue":"premium"}
  }'

# Publish message with numeric attributes
aws sns publish \
  --topic-arn arn:aws:sns:us-east-1:123456789012:MyTopic \
  --message "Price alert" \
  --message-attributes '{
    "price": {"DataType":"Number", "StringValue":"99.99"},
    "quantity": {"DataType":"Number", "StringValue":"5"}
  }'

# Publish message with binary attributes
aws sns publish \
  --topic-arn arn:aws:sns:us-east-1:123456789012:MyTopic \
  --message "Binary data notification" \
  --message-attributes '{
    "data": {"DataType":"Binary", "BinaryValue":"base64-encoded-data"}
  }'

# Publish message with string array
aws sns publish \
  --topic-arn arn:aws:sns:us-east-1:123456789012:MyTopic \
  --message "Multi-region deployment" \
  --message-attributes '{
    "regions": {"DataType":"String.Array", "StringValue":"[\"us-east-1\",\"us-west-2\",\"eu-west-1\"]"}
  }'
```

### Message Filtering

#### Set Filter Policy on Subscription
```bash
# Set filter policy for exact string match
aws sns set-subscription-attributes \
  --subscription-arn arn:aws:sns:us-east-1:123456789012:MyTopic:12345678-1234-1234-1234-123456789012 \
  --attribute-name FilterPolicy \
  --attribute-value '{"store":["example_store"]}'

# Set filter policy for multiple values (OR condition)
aws sns set-subscription-attributes \
  --subscription-arn arn:aws:sns:us-east-1:123456789012:MyTopic:12345678-1234-1234-1234-123456789012 \
  --attribute-name FilterPolicy \
  --attribute-value '{"customer_type":["premium","gold"]}'

# Set filter policy with numeric range
aws sns set-subscription-attributes \
  --subscription-arn arn:aws:sns:us-east-1:123456789012:MyTopic:12345678-1234-1234-1234-123456789012 \
  --attribute-name FilterPolicy \
  --attribute-value '{"price":[{"numeric":[">",100]}]}'

# Set complex filter policy (AND conditions)
aws sns set-subscription-attributes \
  --subscription-arn arn:aws:sns:us-east-1:123456789012:MyTopic:12345678-1234-1234-1234-123456789012 \
  --attribute-name FilterPolicy \
  --attribute-value '{
    "store": ["example_store"],
    "event_type": ["order"],
    "price": [{"numeric":[">=",100]}]
  }'

# Set filter policy with exists check
aws sns set-subscription-attributes \
  --subscription-arn arn:aws:sns:us-east-1:123456789012:MyTopic:12345678-1234-1234-1234-123456789012 \
  --attribute-name FilterPolicy \
  --attribute-value '{"urgent":[{"exists":true}]}'

# Remove filter policy
aws sns set-subscription-attributes \
  --subscription-arn arn:aws:sns:us-east-1:123456789012:MyTopic:12345678-1234-1234-1234-123456789012 \
  --attribute-name FilterPolicy \
  --attribute-value '{}'
```

#### Set Filter Policy Scope
```bash
# Set filter policy scope to MessageAttributes (default)
aws sns set-subscription-attributes \
  --subscription-arn arn:aws:sns:us-east-1:123456789012:MyTopic:12345678-1234-1234-1234-123456789012 \
  --attribute-name FilterPolicyScope \
  --attribute-value MessageAttributes

# Set filter policy scope to MessageBody
aws sns set-subscription-attributes \
  --subscription-arn arn:aws:sns:us-east-1:123456789012:MyTopic:12345678-1234-1234-1234-123456789012 \
  --attribute-name FilterPolicyScope \
  --attribute-value MessageBody
```

### Advanced Subscription Configuration

#### Configure Raw Message Delivery
```bash
# Enable raw message delivery (for SQS/HTTP/S)
aws sns set-subscription-attributes \
  --subscription-arn arn:aws:sns:us-east-1:123456789012:MyTopic:12345678-1234-1234-1234-123456789012 \
  --attribute-name RawMessageDelivery \
  --attribute-value true

# Disable raw message delivery
aws sns set-subscription-attributes \
  --subscription-arn arn:aws:sns:us-east-1:123456789012:MyTopic:12345678-1234-1234-1234-123456789012 \
  --attribute-name RawMessageDelivery \
  --attribute-value false
```

#### Configure Dead Letter Queue
```bash
# Set DLQ for subscription
aws sns set-subscription-attributes \
  --subscription-arn arn:aws:sns:us-east-1:123456789012:MyTopic:12345678-1234-1234-1234-123456789012 \
  --attribute-name RedrivePolicy \
  --attribute-value '{"deadLetterTargetArn":"arn:aws:sqs:us-east-1:123456789012:MyDLQ"}'

# Remove DLQ configuration
aws sns set-subscription-attributes \
  --subscription-arn arn:aws:sns:us-east-1:123456789012:MyTopic:12345678-1234-1234-1234-123456789012 \
  --attribute-name RedrivePolicy \
  --attribute-value ''
```

#### Configure Delivery Status
```bash
# Enable delivery status logging for HTTP
aws sns set-subscription-attributes \
  --subscription-arn arn:aws:sns:us-east-1:123456789012:MyTopic:12345678-1234-1234-1234-123456789012 \
  --attribute-name DeliveryPolicy \
  --attribute-value '{"healthyRetryPolicy":{"numRetries":3,"minDelayTarget":10,"maxDelayTarget":30}}'
```

### Topic Policies

#### Set Topic Policy
```bash
# Allow all AWS accounts to subscribe
aws sns set-topic-attributes \
  --topic-arn arn:aws:sns:us-east-1:123456789012:MyTopic \
  --attribute-name Policy \
  --attribute-value '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"AWS": "*"},
      "Action": "SNS:Subscribe",
      "Resource": "arn:aws:sns:us-east-1:123456789012:MyTopic"
    }]
  }'

# Allow specific AWS service to publish
aws sns set-topic-attributes \
  --topic-arn arn:aws:sns:us-east-1:123456789012:MyTopic \
  --attribute-name Policy \
  --attribute-value '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "cloudwatch.amazonaws.com"},
      "Action": "SNS:Publish",
      "Resource": "arn:aws:sns:us-east-1:123456789012:MyTopic"
    }]
  }'

# Cross-account topic access
aws sns set-topic-attributes \
  --topic-arn arn:aws:sns:us-east-1:123456789012:MyTopic \
  --attribute-name Policy \
  --attribute-value '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"AWS": "arn:aws:iam::999999999999:root"},
      "Action": ["SNS:Subscribe", "SNS:Receive"],
      "Resource": "arn:aws:sns:us-east-1:123456789012:MyTopic"
    }]
  }'
```

### Tags Management

```bash
# Add tags to topic
aws sns tag-resource \
  --resource-arn arn:aws:sns:us-east-1:123456789012:MyTopic \
  --tags Key=Environment,Value=Production Key=CostCenter,Value=Engineering

# List tags for topic
aws sns list-tags-for-resource \
  --resource-arn arn:aws:sns:us-east-1:123456789012:MyTopic

# Remove tags from topic
aws sns untag-resource \
  --resource-arn arn:aws:sns:us-east-1:123456789012:MyTopic \
  --tag-keys Environment CostCenter
```

### Platform Applications (Mobile Push)

#### Create Platform Application
```bash
# Create platform application for iOS (APNS)
aws sns create-platform-application \
  --name MyiOSApp \
  --platform APNS \
  --attributes PlatformCredential=<certificate>,PlatformPrincipal=<private-key>

# Create platform application for Android (FCM)
aws sns create-platform-application \
  --name MyAndroidApp \
  --platform GCM \
  --attributes PlatformCredential=<api-key>

# List platform applications
aws sns list-platform-applications

# Get platform application attributes
aws sns get-platform-application-attributes \
  --platform-application-arn arn:aws:sns:us-east-1:123456789012:app/APNS/MyiOSApp
```

#### Manage Platform Endpoints
```bash
# Create platform endpoint (register device)
aws sns create-platform-endpoint \
  --platform-application-arn arn:aws:sns:us-east-1:123456789012:app/APNS/MyiOSApp \
  --token <device-token>

# List endpoints for platform application
aws sns list-endpoints-by-platform-application \
  --platform-application-arn arn:aws:sns:us-east-1:123456789012:app/APNS/MyiOSApp

# Publish to mobile device
aws sns publish \
  --target-arn arn:aws:sns:us-east-1:123456789012:endpoint/APNS/MyiOSApp/12345678-1234-1234-1234-123456789012 \
  --message '{"APNS":"{\\"aps\\":{\\"alert\\":\\"Hello from SNS!\\"}}"}'   --message-structure json

# Delete platform endpoint
aws sns delete-endpoint \
  --endpoint-arn arn:aws:sns:us-east-1:123456789012:endpoint/APNS/MyiOSApp/12345678-1234-1234-1234-123456789012

# Delete platform application
aws sns delete-platform-application \
  --platform-application-arn arn:aws:sns:us-east-1:123456789012:app/APNS/MyiOSApp
```

### Monitoring and Troubleshooting

```bash
# Check if phone number is opted out
aws sns check-if-phone-number-is-opted-out \
  --phone-number +1234567890

# List opted out phone numbers
aws sns list-phone-numbers-opted-out

# Opt in phone number
aws sns opt-in-phone-number \
  --phone-number +1234567890

# Get SMS sandbox account status
aws sns get-sms-sandbox-account-status

# List SMS sandbox phone numbers
aws sns list-sms-sandbox-phone-numbers
```

### Batch Operations

```bash
# Publish batch messages to FIFO topic
aws sns publish-batch \
  --topic-arn arn:aws:sns:us-east-1:123456789012:MyFIFOTopic.fifo \
  --publish-batch-request-entries file://batch-messages.json

# Example batch-messages.json:
# [
#   {
#     "Id": "1",
#     "Message": "First message",
#     "MessageGroupId": "group1",
#     "MessageDeduplicationId": "dedup1"
#   },
#   {
#     "Id": "2",
#     "Message": "Second message", 
#     "MessageGroupId": "group1",
#     "MessageDeduplicationId": "dedup2"
#   }
# ]
```

---

## Hands-on Labs

### Lab 1: Basic SNS Topic Setup

#### Step 1: Create Topic
```bash
# Create standard topic
aws sns create-topic --name MyFirstTopic

# Create FIFO topic
aws sns create-topic \
  --name MyFIFOTopic.fifo \
  --attributes FifoTopic=true,ContentBasedDeduplication=true
```

#### Step 2: Subscribe to Topic
```bash
# Email subscription
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:123456789012:MyFirstTopic \
  --protocol email \
  --notification-endpoint your-email@example.com

# SQS subscription
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:123456789012:MyFirstTopic \
  --protocol sqs \
  --notification-endpoint arn:aws:sqs:us-east-1:123456789012:MyQueue
```

#### Step 3: Publish Message
```bash
# Publish to standard topic
aws sns publish \
  --topic-arn arn:aws:sns:us-east-1:123456789012:MyFirstTopic \
  --message "Hello from SNS!" \
  --subject "Test Message"

# Publish to FIFO topic
aws sns publish \
  --topic-arn arn:aws:sns:us-east-1:123456789012:MyFIFOTopic.fifo \
  --message "Hello from FIFO!" \
  --message-group-id "group1" \
  --message-deduplication-id "unique-id-1"
```

### Lab 2: SNS with Message Filtering

#### Step 1: Create Subscription with Filter
```bash
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:123456789012:MyTopic \
  --protocol email \
  --notification-endpoint filtered@example.com \
  --attributes FilterPolicy='{"event_type":["order"],"amount":[{"numeric":[">=",100]}]}'
```

#### Step 2: Publish Filtered Message
```bash
aws sns publish \
  --topic-arn arn:aws:sns:us-east-1:123456789012:MyTopic \
  --message "Large order received!" \
  --message-attributes '{"event_type":{"DataType":"String","StringValue":"order"},"amount":{"DataType":"Number","StringValue":"150"}}'
```

### Lab 3: SNS + Lambda Integration

#### Step 1: Create Lambda Function
```python
import json

def lambda_handler(event, context):
    for record in event['Records']:
        # Parse SNS message
        sns_message = json.loads(record['Sns']['Message'])
        print(f"Received message: {sns_message}")
        
        # Process message here
        
    return {
        'statusCode': 200,
        'body': json.dumps('Messages processed successfully')
    }
```

#### Step 2: Subscribe Lambda to SNS
```bash
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:123456789012:MyTopic \
  --protocol lambda \
  --notification-endpoint arn:aws:lambda:us-east-1:123456789012:function:MyFunction
```

#### Step 3: Grant SNS Permission to Invoke Lambda
```bash
aws lambda add-permission \
  --function-name MyFunction \
  --statement-id sns-invoke \
  --action lambda:InvokeFunction \
  --principal sns.amazonaws.com \
  --source-arn arn:aws:sns:us-east-1:123456789012:MyTopic
```

---

## Summary

Amazon SNS is a powerful messaging service that enables building decoupled, scalable applications. Key points for SAA-C03:

1. **Choose appropriate topic type**: Standard for high throughput, FIFO for ordered processing
2. **Understand protocol capabilities**: Each has different use cases and limitations
3. **Implement proper security**: IAM policies, encryption, VPC endpoints
4. **Design for scale**: Consider message filtering and fan-out patterns
5. **Monitor and troubleshoot**: Use CloudWatch metrics and logs
6. **Follow best practices**: Security, cost optimization, and reliability

SNS integrates seamlessly with other AWS services and is essential for building event-driven architectures in AWS.