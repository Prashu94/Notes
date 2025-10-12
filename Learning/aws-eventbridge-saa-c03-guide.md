# AWS EventBridge - SAA-C03 Certification Guide

## Table of Contents
1. [Overview](#overview)
2. [Core Concepts](#core-concepts)
3. [Key Features](#key-features)
4. [EventBridge Components](#eventbridge-components)
5. [Event Sources](#event-sources)
6. [Event Targets](#event-targets)
7. [Event Patterns and Rules](#event-patterns-and-rules)
8. [Custom Event Buses](#custom-event-buses)
9. [Schema Registry](#schema-registry)
10. [Integration Patterns](#integration-patterns)
11. [Security and Access Control](#security-and-access-control)
12. [Monitoring and Troubleshooting](#monitoring-and-troubleshooting)
13. [Cost Optimization](#cost-optimization)
14. [Best Practices](#best-practices)
15. [Common Exam Scenarios](#common-exam-scenarios)
16. [Hands-on Examples](#hands-on-examples)

---

## Overview

### What is AWS EventBridge?
AWS EventBridge is a serverless event bus service that makes it easier to build event-driven applications at scale using events generated from your applications, integrated Software-as-a-Service (SaaS) applications, and AWS services.

### Key Benefits
- **Serverless**: No infrastructure to manage
- **Scalable**: Automatically scales to handle millions of events
- **Reliable**: Built-in retry and dead letter queue support
- **Flexible**: Support for multiple event sources and targets
- **Cost-effective**: Pay only for what you use

### Use Cases
- Application integration
- Real-time data processing
- Workflow orchestration
- Monitoring and alerting
- Cross-account event routing
- SaaS application integration

---

## Core Concepts

### Event-Driven Architecture
```
Event Source → EventBridge → Event Target
    ↓             ↓              ↓
  Producer    Event Router   Consumer
```

### Event Structure
```json
{
  "version": "0",
  "id": "6a7e8feb-b491-4cf7-a9f1-bf3703467718",
  "detail-type": "EC2 Instance State-change Notification",
  "source": "aws.ec2",
  "account": "111122223333",
  "time": "2017-12-22T18:43:48Z",
  "region": "us-west-1",
  "detail": {
    "instance-id": "i-1234567890abcdef0",
    "state": "terminated"
  }
}
```

### Event Components
- **Version**: Event format version
- **ID**: Unique event identifier
- **Detail-type**: High-level description of the event
- **Source**: Event source identifier
- **Account**: AWS account ID
- **Time**: Event timestamp
- **Region**: AWS region
- **Detail**: Event-specific information

---

## Key Features

### 1. Multiple Event Buses
- **Default Event Bus**: Pre-created for AWS service events
- **Custom Event Buses**: For application and SaaS events
- **Partner Event Buses**: For third-party SaaS integrations

### 2. Event Replay
- Replay events from a specific time range
- Useful for testing and disaster recovery
- Events stored for up to 24 hours by default

### 3. Archive and Replay
```bash
# Create an archive
aws events put-archive \
    --archive-name my-archive \
    --event-source-arn arn:aws:events:region:account:event-bus/my-bus \
    --retention-days 30

# Replay events
aws events start-replay \
    --replay-name my-replay \
    --event-source-arn arn:aws:events:region:account:archive/my-archive \
    --event-start-time 2023-01-01T00:00:00Z \
    --event-end-time 2023-01-02T00:00:00Z \
    --destination arn:aws:events:region:account:event-bus/target-bus
```

### 4. Content-Based Filtering
- Filter events based on event content
- Reduce unnecessary invocations
- Cost optimization through selective processing

---

## EventBridge Components

### 1. Event Buses
```yaml
# Custom Event Bus
Type: AWS::Events::EventBus
Properties:
  Name: MyCustomEventBus
  EventSourceName: myapp.orders
```

### 2. Rules
```yaml
# Event Rule
Type: AWS::Events::Rule
Properties:
  Name: OrderProcessingRule
  EventBusName: !Ref MyCustomEventBus
  EventPattern:
    source: ["myapp.orders"]
    detail-type: ["Order Placed"]
  Targets:
    - Arn: !GetAtt OrderProcessingFunction.Arn
      Id: "OrderProcessingTarget"
```

### 3. Targets
- AWS Lambda functions
- Amazon SQS queues
- Amazon SNS topics
- Amazon Kinesis streams
- AWS Step Functions
- Amazon ECS tasks
- HTTP endpoints
- And many more...

---

## Event Sources

### AWS Service Events
```json
{
  "source": ["aws.ec2"],
  "detail-type": ["EC2 Instance State-change Notification"],
  "detail": {
    "state": ["running", "stopped"]
  }
}
```

### Custom Application Events
```python
import boto3
import json
from datetime import datetime

eventbridge = boto3.client('events')

# Send custom event
response = eventbridge.put_events(
    Entries=[
        {
            'Source': 'myapp.orders',
            'DetailType': 'Order Placed',
            'Detail': json.dumps({
                'orderId': '12345',
                'customerId': 'cust-67890',
                'amount': 99.99,
                'timestamp': datetime.now().isoformat()
            }),
            'EventBusName': 'MyCustomEventBus'
        }
    ]
)
```

### SaaS Partner Events
- Shopify
- Zendesk
- Auth0
- Datadog
- PagerDuty
- And many more...

---

## Event Targets

### Lambda Function Target
```yaml
LambdaInvokePermission:
  Type: AWS::Lambda::Permission
  Properties:
    FunctionName: !Ref ProcessOrderFunction
    Action: lambda:InvokeFunction
    Principal: events.amazonaws.com
    SourceArn: !GetAtt OrderRule.Arn
```

### SQS Queue Target
```yaml
SQSTarget:
  Type: AWS::Events::Rule
  Properties:
    Targets:
      - Arn: !GetAtt OrderQueue.Arn
        Id: "OrderQueueTarget"
        SqsParameters:
          MessageGroupId: "order-processing"
```

### Step Functions Target
```yaml
StepFunctionsTarget:
  Type: AWS::Events::Rule
  Properties:
    Targets:
      - Arn: !GetAtt OrderWorkflow.Arn
        Id: "OrderWorkflowTarget"
        RoleArn: !GetAtt EventBridgeRole.Arn
        StepFunctionsParameters:
          StateMachineParameters:
            orderId: "$.detail.orderId"
```

### Cross-Account Targets
```json
{
  "Rules": [
    {
      "Name": "CrossAccountRule",
      "EventPattern": {
        "source": ["myapp.orders"]
      },
      "Targets": [
        {
          "Id": "CrossAccountTarget",
          "Arn": "arn:aws:events:us-east-1:222222222222:event-bus/target-bus",
          "RoleArn": "arn:aws:iam::111111111111:role/EventBridgeRole"
        }
      ]
    }
  ]
}
```

---

## Event Patterns and Rules

### Basic Event Pattern
```json
{
  "source": ["aws.ec2"],
  "detail-type": ["EC2 Instance State-change Notification"]
}
```

### Advanced Filtering
```json
{
  "source": ["myapp.orders"],
  "detail-type": ["Order Placed"],
  "detail": {
    "state": ["confirmed"],
    "amount": [{"numeric": [">", 100]}],
    "region": ["us-east-1", "us-west-2"],
    "customerId": [{"exists": true}]
  }
}
```

### Prefix Matching
```json
{
  "detail": {
    "eventName": [{"prefix": "Delete"}]
  }
}
```

### Array Matching
```json
{
  "detail": {
    "tags": {
      "Environment": ["Production", "Staging"]
    }
  }
}
```

---

## Custom Event Buses

### Creating Custom Event Bus
```bash
# CLI command
aws events create-event-bus --name MyApplicationBus
```

### Cross-Account Access
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowCrossAccountAccess",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::222222222222:root"
      },
      "Action": "events:PutEvents",
      "Resource": "arn:aws:events:us-east-1:111111111111:event-bus/MyApplicationBus"
    }
  ]
}
```

### Resource-Based Policy
```bash
aws events put-permission \
    --principal 222222222222 \
    --action events:PutEvents \
    --statement-id "CrossAccountAccess" \
    --event-bus-name MyApplicationBus
```

---

## Schema Registry

### Benefits
- Event schema discovery
- Code generation
- Version management
- Documentation

### Creating Schema Registry
```bash
aws schemas create-registry \
    --registry-name MyAppRegistry \
    --description "Schema registry for my application events"
```

### Schema Discovery
```bash
aws schemas start-discoverer \
    --discoverer-id MyAppDiscoverer \
    --source-arn arn:aws:events:us-east-1:123456789012:event-bus/MyApplicationBus
```

### Schema Example
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://myapp.com/order-placed.json",
  "title": "Order Placed Event",
  "type": "object",
  "properties": {
    "orderId": {
      "type": "string",
      "description": "Unique order identifier"
    },
    "customerId": {
      "type": "string",
      "description": "Customer identifier"
    },
    "amount": {
      "type": "number",
      "minimum": 0,
      "description": "Order amount"
    }
  },
  "required": ["orderId", "customerId", "amount"]
}
```

---

## Integration Patterns

### 1. Fan-out Pattern
```yaml
# One event triggers multiple targets
OrderRule:
  Type: AWS::Events::Rule
  Properties:
    EventPattern:
      source: ["myapp.orders"]
      detail-type: ["Order Placed"]
    Targets:
      - Arn: !GetAtt InventoryFunction.Arn
        Id: "InventoryUpdate"
      - Arn: !GetAtt PaymentFunction.Arn
        Id: "PaymentProcessing"
      - Arn: !GetAtt NotificationFunction.Arn
        Id: "CustomerNotification"
```

### 2. Content-Based Routing
```yaml
# Route based on event content
HighValueOrderRule:
  Type: AWS::Events::Rule
  Properties:
    EventPattern:
      source: ["myapp.orders"]
      detail:
        amount: [{"numeric": [">", 1000]}]
    Targets:
      - Arn: !GetAtt HighValueOrderFunction.Arn
        Id: "HighValueProcessing"

RegularOrderRule:
  Type: AWS::Events::Rule
  Properties:
    EventPattern:
      source: ["myapp.orders"]
      detail:
        amount: [{"numeric": ["<=", 1000]}]
    Targets:
      - Arn: !GetAtt RegularOrderFunction.Arn
        Id: "RegularProcessing"
```

### 3. Aggregation Pattern
```python
# Lambda function for event aggregation
import json
import boto3
from datetime import datetime, timedelta

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('EventAggregation')

def lambda_handler(event, context):
    # Aggregate events in DynamoDB
    current_time = datetime.now()
    window_key = current_time.strftime('%Y-%m-%d-%H')  # Hourly window
    
    table.update_item(
        Key={'window': window_key},
        UpdateExpression='ADD event_count :val SET last_updated = :time',
        ExpressionAttributeValues={
            ':val': 1,
            ':time': current_time.isoformat()
        }
    )
```

### 4. Error Handling Pattern
```yaml
# Dead Letter Queue configuration
OrderProcessingRule:
  Type: AWS::Events::Rule
  Properties:
    Targets:
      - Arn: !GetAtt OrderFunction.Arn
        Id: "OrderTarget"
        RetryPolicy:
          MaximumRetryAttempts: 3
          MaximumEventAge: 3600
        DeadLetterConfig:
          Arn: !GetAtt DeadLetterQueue.Arn
```

---

## Security and Access Control

### IAM Policies for EventBridge

#### EventBridge Service Role
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "events:PutEvents",
        "events:PutRule",
        "events:PutTargets"
      ],
      "Resource": "*"
    }
  ]
}
```

#### Lambda Execution Policy
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "events:PutEvents"
      ],
      "Resource": "arn:aws:events:*:*:event-bus/MyApplicationBus"
    }
  ]
}
```

### Resource-Based Policies
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowSpecificSource",
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "events:PutEvents",
      "Resource": "arn:aws:events:*:*:event-bus/MyApplicationBus",
      "Condition": {
        "StringEquals": {
          "events:source": "myapp.orders"
        }
      }
    }
  ]
}
```

### Encryption
```yaml
# KMS encryption for event bus
EncryptedEventBus:
  Type: AWS::Events::EventBus
  Properties:
    Name: SecureEventBus
    KmsKeyId: !Ref EventBusKMSKey
```

---

## Monitoring and Troubleshooting

### CloudWatch Metrics
```bash
# Key metrics to monitor
- InvocationsCount: Number of rule invocations
- SuccessfulInvocations: Successful invocations
- FailedInvocations: Failed invocations
- MatchedEvents: Events that matched rules
- ThrottledRules: Throttled rule invocations
```

### CloudWatch Dashboards
```json
{
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/Events", "SuccessfulInvocations", "RuleName", "OrderProcessingRule"],
          [".", "FailedInvocations", ".", "."]
        ],
        "period": 300,
        "stat": "Sum",
        "region": "us-east-1",
        "title": "EventBridge Rule Performance"
      }
    }
  ]
}
```

### CloudWatch Alarms
```yaml
HighFailureRate:
  Type: AWS::CloudWatch::Alarm
  Properties:
    AlarmDescription: "High EventBridge failure rate"
    MetricName: FailedInvocations
    Namespace: AWS/Events
    Statistic: Sum
    Period: 300
    EvaluationPeriods: 2
    Threshold: 10
    ComparisonOperator: GreaterThanThreshold
    Dimensions:
      - Name: RuleName
        Value: !Ref OrderProcessingRule
```

### AWS X-Ray Integration
```python
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

# Patch AWS SDK calls
patch_all()

@xray_recorder.capture('process_order_event')
def lambda_handler(event, context):
    # Process event with X-Ray tracing
    order_id = event['detail']['orderId']
    
    with xray_recorder.in_subsegment('validate_order'):
        validate_order(order_id)
    
    with xray_recorder.in_subsegment('process_payment'):
        process_payment(order_id)
```

### Troubleshooting Common Issues

#### 1. Events Not Matching Rules
```bash
# Check event pattern syntax
aws events test-event-pattern \
    --event-pattern file://pattern.json \
    --event file://event.json
```

#### 2. Target Invocation Failures
```bash
# Check CloudWatch Logs for Lambda errors
aws logs describe-log-groups \
    --log-group-name-prefix /aws/lambda/my-function

# Check dead letter queues
aws sqs receive-message \
    --queue-url https://sqs.region.amazonaws.com/account/dlq
```

#### 3. Permission Issues
```bash
# Verify IAM policies
aws iam simulate-principal-policy \
    --policy-source-arn arn:aws:iam::account:role/EventBridgeRole \
    --action-names events:PutEvents \
    --resource-arns arn:aws:events:region:account:event-bus/bus-name
```

---

## Cost Optimization

### Pricing Model
- **Custom Events**: $1.00 per million custom events
- **Replayed Events**: $0.10 per million replayed events
- **Cross-Region Replication**: $0.01 per GB transferred
- **Schema Discovery**: $0.10 per million ingested events

### Cost Optimization Strategies

#### 1. Event Filtering
```json
{
  "detail": {
    "state": ["RUNNING", "STOPPED"],
    "instance-type": [{"prefix": "m5"}]
  }
}
```

#### 2. Batch Processing
```python
import boto3

eventbridge = boto3.client('events')

# Batch multiple events
events = []
for i in range(10):  # Max 10 events per batch
    events.append({
        'Source': 'myapp.batch',
        'DetailType': 'Batch Event',
        'Detail': json.dumps({'id': i})
    })

eventbridge.put_events(Entries=events)
```

#### 3. Archive Lifecycle Management
```bash
# Set appropriate retention periods
aws events put-archive \
    --archive-name cost-optimized-archive \
    --retention-days 7 \
    --event-source-arn arn:aws:events:region:account:event-bus/my-bus
```

#### 4. Regional Optimization
- Keep event sources and targets in the same region
- Use cross-region replication only when necessary
- Consider data transfer costs

---

## Best Practices

### 1. Event Design
- Use consistent event structure
- Include correlation IDs
- Add timestamp information
- Use meaningful source and detail-type values

```json
{
  "source": "myapp.orders",
  "detail-type": "Order Status Changed",
  "detail": {
    "orderId": "12345",
    "correlationId": "corr-67890",
    "previousStatus": "pending",
    "newStatus": "confirmed",
    "timestamp": "2023-10-12T10:30:00Z",
    "metadata": {
      "userId": "user-123",
      "version": "1.0"
    }
  }
}
```

### 2. Rule Organization
- Use descriptive rule names
- Group related rules logically
- Implement proper error handling
- Use appropriate retry policies

### 3. Target Configuration
- Configure dead letter queues
- Set appropriate batch sizes
- Use input transformation when needed
- Monitor target performance

### 4. Security
- Use least privilege IAM policies
- Enable CloudTrail logging
- Encrypt sensitive data
- Implement resource-based policies

### 5. Testing
- Test event patterns before deployment
- Use EventBridge test features
- Implement integration tests
- Monitor rule performance

---

## Common Exam Scenarios

### Scenario 1: Decoupling Microservices
**Question**: How to decouple microservices communication?
**Answer**: Use EventBridge with custom event buses for async communication

```yaml
# Solution Architecture
OrderService → EventBridge → [InventoryService, PaymentService, NotificationService]
```

### Scenario 2: Cross-Account Event Routing
**Question**: Route events between AWS accounts
**Answer**: Use resource-based policies and cross-account targets

### Scenario 3: SaaS Integration
**Question**: Integrate with third-party SaaS applications
**Answer**: Use EventBridge partner integrations and schema registry

### Scenario 4: Disaster Recovery
**Question**: Replay events after system failure
**Answer**: Use EventBridge archive and replay capabilities

### Scenario 5: Cost Optimization
**Question**: Reduce EventBridge costs
**Answer**: Implement event filtering, batching, and appropriate retention

---

## Hands-on Examples

### Example 1: Order Processing System
```python
# Order service sending events
import boto3
import json
from datetime import datetime

def place_order(order_data):
    eventbridge = boto3.client('events')
    
    # Send order placed event
    eventbridge.put_events(
        Entries=[
            {
                'Source': 'ecommerce.orders',
                'DetailType': 'Order Placed',
                'Detail': json.dumps({
                    'orderId': order_data['id'],
                    'customerId': order_data['customer_id'],
                    'amount': order_data['amount'],
                    'items': order_data['items'],
                    'timestamp': datetime.now().isoformat()
                }),
                'EventBusName': 'EcommerceEventBus'
            }
        ]
    )
```

### Example 2: Infrastructure Monitoring
```yaml
# CloudFormation template for EC2 monitoring
EC2StateChangeRule:
  Type: AWS::Events::Rule
  Properties:
    Description: "Monitor EC2 state changes"
    EventPattern:
      source: ["aws.ec2"]
      detail-type: ["EC2 Instance State-change Notification"]
      detail:
        state: ["terminated", "stopped"]
    Targets:
      - Arn: !GetAtt AlertingFunction.Arn
        Id: "EC2AlertTarget"
      - Arn: !Ref CleanupQueue.Arn
        Id: "CleanupTarget"
```

### Example 3: Multi-Region Event Replication
```bash
# Create replication rule
aws events put-replication-configuration \
    --replication-config '{
        "ReplicationConfig": {
            "State": "ENABLED"
        }
    }' \
    --region us-east-1

# Target region receives events automatically
```

---

## Summary

AWS EventBridge is a powerful serverless event bus service that enables:

1. **Scalable Event-Driven Architecture**: Build loosely coupled, scalable applications
2. **Multi-Source Integration**: Connect AWS services, SaaS applications, and custom applications
3. **Flexible Event Routing**: Content-based filtering and routing
4. **Built-in Reliability**: Retry mechanisms and dead letter queues
5. **Cost-Effective**: Pay-per-use pricing model
6. **Security**: IAM integration and encryption support
7. **Monitoring**: CloudWatch integration for observability

### Key Takeaways for SAA-C03
- Understand event-driven architecture patterns
- Know when to use EventBridge vs other messaging services
- Master event filtering and routing concepts
- Understand cross-account and cross-region capabilities
- Know cost optimization strategies
- Practice with real-world integration scenarios

EventBridge is essential for modern serverless and microservices architectures, making it a critical service for the SAA-C03 certification.