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
17. [AWS CLI Commands Reference](#aws-cli-commands-reference)
18. [Hands-on Examples](#hands-on-examples)

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

## AWS CLI Commands Reference

### Event Rules

#### Create Rules

```bash
# Create a simple rule that triggers on all EC2 state changes
aws events put-rule \
    --name ec2-state-change-rule \
    --description "Trigger on EC2 instance state changes" \
    --event-pattern '{"source":["aws.ec2"],"detail-type":["EC2 Instance State-change Notification"]}'

# Create rule with specific state filter
aws events put-rule \
    --name ec2-terminated-rule \
    --description "Trigger when EC2 instances are terminated" \
    --event-pattern file://ec2-terminated-pattern.json

cat > ec2-terminated-pattern.json << 'EOF'
{
  "source": ["aws.ec2"],
  "detail-type": ["EC2 Instance State-change Notification"],
  "detail": {
    "state": ["terminated"]
  }
}
EOF

# Create scheduled rule (cron expression)
aws events put-rule \
    --name daily-backup-rule \
    --description "Trigger backup every day at 2 AM UTC" \
    --schedule-expression "cron(0 2 * * ? *)"

# Create scheduled rule (rate expression)
aws events put-rule \
    --name every-5-minutes-rule \
    --description "Trigger every 5 minutes" \
    --schedule-expression "rate(5 minutes)"

# Create rule on custom event bus
aws events put-rule \
    --name custom-app-rule \
    --event-bus-name custom-app-bus \
    --description "Rule on custom event bus" \
    --event-pattern '{"source":["custom.app"],"detail-type":["order.placed"]}'

# Create rule with specific state (enabled/disabled)
aws events put-rule \
    --name test-rule \
    --description "Test rule - initially disabled" \
    --event-pattern '{"source":["aws.s3"]}' \
    --state DISABLED
```

#### Describe and List Rules

```bash
# List all rules on default event bus
aws events list-rules

# List rules with name prefix
aws events list-rules --name-prefix "ec2-"

# List rules on custom event bus
aws events list-rules --event-bus-name custom-app-bus

# Describe specific rule
aws events describe-rule --name ec2-state-change-rule

# Describe rule on custom event bus
aws events describe-rule \
    --name custom-app-rule \
    --event-bus-name custom-app-bus
```

#### Enable and Disable Rules

```bash
# Enable a rule
aws events enable-rule --name ec2-state-change-rule

# Disable a rule
aws events disable-rule --name ec2-state-change-rule

# Enable rule on custom event bus
aws events enable-rule \
    --name custom-app-rule \
    --event-bus-name custom-app-bus
```

#### Delete Rules

```bash
# Delete a rule (must remove targets first)
aws events delete-rule --name ec2-state-change-rule

# Force delete (removes targets automatically)
aws events delete-rule \
    --name ec2-state-change-rule \
    --force

# Delete rule on custom event bus
aws events delete-rule \
    --name custom-app-rule \
    --event-bus-name custom-app-bus
```

---

### Event Patterns

#### Complex Event Patterns

```bash
# Multiple sources and detail types
aws events put-rule \
    --name multi-service-rule \
    --event-pattern file://multi-service-pattern.json

cat > multi-service-pattern.json << 'EOF'
{
  "source": ["aws.ec2", "aws.autoscaling"],
  "detail-type": [
    "EC2 Instance State-change Notification",
    "EC2 Instance Launch Successful",
    "EC2 Instance Terminate Successful"
  ]
}
EOF

# Pattern with specific field matching
aws events put-rule \
    --name critical-errors-rule \
    --event-pattern file://critical-errors-pattern.json

cat > critical-errors-pattern.json << 'EOF'
{
  "source": ["custom.myapp"],
  "detail-type": ["application.error"],
  "detail": {
    "severity": ["CRITICAL", "ERROR"],
    "component": ["payment-processor", "auth-service"]
  }
}
EOF

# Pattern with prefix matching
aws events put-rule \
    --name s3-uploads-rule \
    --event-pattern file://s3-prefix-pattern.json

cat > s3-prefix-pattern.json << 'EOF'
{
  "source": ["aws.s3"],
  "detail-type": ["Object Created"],
  "detail": {
    "bucket": {
      "name": ["my-upload-bucket"]
    },
    "object": {
      "key": [{"prefix": "uploads/images/"}]
    }
  }
}
EOF

# Pattern with numeric matching
aws events put-rule \
    --name high-cpu-rule \
    --event-pattern file://high-cpu-pattern.json

cat > high-cpu-pattern.json << 'EOF'
{
  "source": ["aws.cloudwatch"],
  "detail-type": ["CloudWatch Alarm State Change"],
  "detail": {
    "alarmName": [{"prefix": "CPU-"}],
    "state": {
      "value": ["ALARM"]
    },
    "configuration": {
      "metrics": [{
        "metricStat": {
          "metric": {
            "name": ["CPUUtilization"]
          },
          "stat": ["Average"]
        }
      }]
    }
  }
}
EOF

# Pattern with anything-but matching
aws events put-rule \
    --name non-production-events-rule \
    --event-pattern file://non-production-pattern.json

cat > non-production-pattern.json << 'EOF'
{
  "source": ["custom.myapp"],
  "detail": {
    "environment": [{"anything-but": "production"}]
  }
}
EOF
```

---

### Event Targets

#### Add Targets to Rules

##### Lambda Function Target

```bash
# Add Lambda function as target
aws events put-targets \
    --rule ec2-state-change-rule \
    --targets file://lambda-target.json

cat > lambda-target.json << 'EOF'
[
  {
    "Id": "1",
    "Arn": "arn:aws:lambda:us-east-1:123456789012:function:ProcessEC2Events"
  }
]
EOF

# Add Lambda with input transformation
aws events put-targets \
    --rule ec2-state-change-rule \
    --targets file://lambda-transform-target.json

cat > lambda-transform-target.json << 'EOF'
[
  {
    "Id": "1",
    "Arn": "arn:aws:lambda:us-east-1:123456789012:function:ProcessEC2Events",
    "InputTransformer": {
      "InputPathsMap": {
        "instance": "$.detail.instance-id",
        "state": "$.detail.state"
      },
      "InputTemplate": "{\"instanceId\": <instance>, \"newState\": <state>}"
    }
  }
]
EOF
```

##### SQS Queue Target

```bash
# Add SQS queue as target
aws events put-targets \
    --rule ec2-state-change-rule \
    --targets file://sqs-target.json

cat > sqs-target.json << 'EOF'
[
  {
    "Id": "1",
    "Arn": "arn:aws:sqs:us-east-1:123456789012:ec2-events-queue",
    "MessageGroupId": "ec2-events"
  }
]
EOF

# Add SQS queue for FIFO queue
aws events put-targets \
    --rule order-events-rule \
    --targets file://sqs-fifo-target.json

cat > sqs-fifo-target.json << 'EOF'
[
  {
    "Id": "1",
    "Arn": "arn:aws:sqs:us-east-1:123456789012:orders.fifo",
    "SqsParameters": {
      "MessageGroupId": "$.detail.orderId"
    }
  }
]
EOF
```

##### SNS Topic Target

```bash
# Add SNS topic as target
aws events put-targets \
    --rule ec2-state-change-rule \
    --targets file://sns-target.json

cat > sns-target.json << 'EOF'
[
  {
    "Id": "1",
    "Arn": "arn:aws:sns:us-east-1:123456789012:EC2Notifications",
    "InputTransformer": {
      "InputPathsMap": {
        "instance": "$.detail.instance-id",
        "state": "$.detail.state",
        "time": "$.time"
      },
      "InputTemplate": "\"Instance <instance> has changed state to <state> at <time>\""
    }
  }
]
EOF
```

##### Step Functions Target

```bash
# Add Step Functions state machine as target
aws events put-targets \
    --rule order-placed-rule \
    --targets file://stepfunctions-target.json

cat > stepfunctions-target.json << 'EOF'
[
  {
    "Id": "1",
    "Arn": "arn:aws:states:us-east-1:123456789012:stateMachine:OrderProcessing",
    "RoleArn": "arn:aws:iam::123456789012:role/EventBridgeToStepFunctionsRole",
    "Input": "{\"orderId\": \"$.detail.orderId\", \"customerId\": \"$.detail.customerId\"}"
  }
]
EOF
```

##### EC2 Actions Target

```bash
# Add EC2 instance action as target (stop instance)
aws events put-targets \
    --rule after-hours-rule \
    --targets file://ec2-stop-target.json

cat > ec2-stop-target.json << 'EOF'
[
  {
    "Id": "1",
    "Arn": "arn:aws:events:us-east-1:123456789012:target/aws.ec2.stopInstances",
    "RoleArn": "arn:aws:iam::123456789012:role/EventBridgeEC2Role",
    "Input": "{\"InstanceIds\": [\"i-1234567890abcdef0\"]}"
  }
]
EOF

# Start instances
aws events put-targets \
    --rule business-hours-rule \
    --targets file://ec2-start-target.json

cat > ec2-start-target.json << 'EOF'
[
  {
    "Id": "1",
    "Arn": "arn:aws:events:us-east-1:123456789012:target/aws.ec2.startInstances",
    "RoleArn": "arn:aws:iam::123456789012:role/EventBridgeEC2Role",
    "Input": "{\"InstanceIds\": [\"i-1234567890abcdef0\", \"i-0987654321fedcba0\"]}"
  }
]
EOF
```

##### ECS Task Target

```bash
# Add ECS task as target
aws events put-targets \
    --rule scheduled-job-rule \
    --targets file://ecs-target.json

cat > ecs-target.json << 'EOF'
[
  {
    "Id": "1",
    "Arn": "arn:aws:ecs:us-east-1:123456789012:cluster/my-cluster",
    "RoleArn": "arn:aws:iam::123456789012:role/EventBridgeECSRole",
    "EcsParameters": {
      "TaskDefinitionArn": "arn:aws:ecs:us-east-1:123456789012:task-definition/my-task:1",
      "TaskCount": 1,
      "LaunchType": "FARGATE",
      "NetworkConfiguration": {
        "awsvpcConfiguration": {
          "Subnets": ["subnet-12345678", "subnet-87654321"],
          "SecurityGroups": ["sg-0123456789abcdef0"],
          "AssignPublicIp": "ENABLED"
        }
      },
      "PlatformVersion": "LATEST"
    }
  }
]
EOF
```

##### Multiple Targets

```bash
# Add multiple targets to a single rule
aws events put-targets \
    --rule critical-error-rule \
    --targets file://multiple-targets.json

cat > multiple-targets.json << 'EOF'
[
  {
    "Id": "1",
    "Arn": "arn:aws:lambda:us-east-1:123456789012:function:LogError"
  },
  {
    "Id": "2",
    "Arn": "arn:aws:sns:us-east-1:123456789012:CriticalAlerts"
  },
  {
    "Id": "3",
    "Arn": "arn:aws:sqs:us-east-1:123456789012:error-queue"
  }
]
EOF
```

#### List and Remove Targets

```bash
# List targets for a rule
aws events list-targets-by-rule --rule ec2-state-change-rule

# List targets on custom event bus
aws events list-targets-by-rule \
    --rule custom-app-rule \
    --event-bus-name custom-app-bus

# Remove specific targets
aws events remove-targets \
    --rule ec2-state-change-rule \
    --ids "1" "2"

# Remove targets on custom event bus
aws events remove-targets \
    --rule custom-app-rule \
    --event-bus-name custom-app-bus \
    --ids "1"
```

---

### Custom Event Buses

#### Create and Manage Event Buses

```bash
# Create a custom event bus
aws events create-event-bus \
    --name custom-app-bus

# Create event bus with tags
aws events create-event-bus \
    --name production-bus \
    --tags Key=Environment,Value=Production Key=Application,Value=OrderService

# Describe event bus
aws events describe-event-bus --name custom-app-bus

# List all event buses
aws events list-event-buses

# List event buses with name prefix
aws events list-event-buses --name-prefix "custom"

# Delete event bus
aws events delete-event-bus --name custom-app-bus
```

#### Event Bus Permissions

```bash
# Add permission for another account to send events
aws events put-permission \
    --event-bus-name custom-app-bus \
    --statement-id AllowAccountToPutEvents \
    --action events:PutEvents \
    --principal 123456789012

# Add permission with condition
aws events put-permission \
    --event-bus-name custom-app-bus \
    --statement-id AllowSpecificSource \
    --action events:PutEvents \
    --principal 123456789012 \
    --condition '{"Type":"StringEquals","Key":"events:source","Value":"custom.orders"}'

# Add permission for organization
aws events put-permission \
    --event-bus-name custom-app-bus \
    --statement-id AllowOrganization \
    --action events:PutEvents \
    --principal '*' \
    --condition '{"Type":"StringEquals","Key":"aws:PrincipalOrgID","Value":"o-1234567890"}'

# Describe event bus policy
aws events describe-event-bus \
    --name custom-app-bus \
    --query 'Policy'

# Remove permission
aws events remove-permission \
    --event-bus-name custom-app-bus \
    --statement-id AllowAccountToPutEvents
```

---

### Put Events

#### Send Custom Events

```bash
# Put a single event to default event bus
aws events put-events \
    --entries file://single-event.json

cat > single-event.json << 'EOF'
[
  {
    "Source": "custom.myapp",
    "DetailType": "user.signup",
    "Detail": "{\"userId\": \"user123\", \"email\": \"user@example.com\", \"timestamp\": \"2026-02-08T10:00:00Z\"}"
  }
]
EOF

# Put event to custom event bus
aws events put-events \
    --entries file://custom-bus-event.json

cat > custom-bus-event.json << 'EOF'
[
  {
    "Source": "custom.orders",
    "DetailType": "order.placed",
    "Detail": "{\"orderId\": \"ord-789\", \"customerId\": \"cust-456\", \"total\": 99.99}",
    "EventBusName": "custom-app-bus"
  }
]
EOF

# Put multiple events in batch (up to 10 events)
aws events put-events \
    --entries file://batch-events.json

cat > batch-events.json << 'EOF'
[
  {
    "Source": "custom.myapp",
    "DetailType": "user.login",
    "Detail": "{\"userId\": \"user123\", \"timestamp\": \"2026-02-08T10:00:00Z\"}"
  },
  {
    "Source": "custom.myapp",
    "DetailType": "user.logout",
    "Detail": "{\"userId\": \"user456\", \"timestamp\": \"2026-02-08T10:05:00Z\"}"
  },
  {
    "Source": "custom.myapp",
    "DetailType": "order.created",
    "Detail": "{\"orderId\": \"ord-001\", \"amount\": 150.00}",
    "Resources": ["arn:aws:myapp:us-east-1:123456789012:order/ord-001"]
  }
]
EOF

# Put event with resources and trace header
aws events put-events \
    --entries file://traced-event.json

cat > traced-event.json << 'EOF'
[
  {
    "Source": "custom.orders",
    "DetailType": "order.shipped",
    "Detail": "{\"orderId\": \"ord-123\", \"trackingNumber\": \"TRACK123\"}",
    "Resources": [
      "arn:aws:orders:us-east-1:123456789012:order/ord-123",
      "arn:aws:shipping:us-east-1:123456789012:shipment/ship-456"
    ],
    "TraceHeader": "Root=1-67891234-abcdef012345678901234567"
  }
]
EOF
```

---

### Archive and Replay

#### Create and Manage Archives

```bash
# Create an archive for all events
aws events create-archive \
    --archive-name all-events-archive \
    --event-source-arn arn:aws:events:us-east-1:123456789012:event-bus/default \
    --retention-days 30

# Create archive with event pattern filter
aws events create-archive \
    --archive-name ec2-events-archive \
    --event-source-arn arn:aws:events:us-east-1:123456789012:event-bus/default \
    --description "Archive of EC2 state change events" \
    --event-pattern file://archive-pattern.json \
    --retention-days 90

cat > archive-pattern.json << 'EOF'
{
  "source": ["aws.ec2"],
  "detail-type": ["EC2 Instance State-change Notification"]
}
EOF

# Create archive for custom event bus
aws events create-archive \
    --archive-name custom-bus-archive \
    --event-source-arn arn:aws:events:us-east-1:123456789012:event-bus/custom-app-bus \
    --retention-days 365

# Describe archive
aws events describe-archive --archive-name all-events-archive

# List archives
aws events list-archives

# List archives for specific event bus
aws events list-archives \
    --event-source-arn arn:aws:events:us-east-1:123456789012:event-bus/custom-app-bus

# Update archive
aws events update-archive \
    --archive-name all-events-archive \
    --retention-days 60 \
    --description "Updated retention period"

# Delete archive
aws events delete-archive --archive-name all-events-archive
```

#### Replay Events

```bash
# Start replay from archive
aws events start-replay \
    --replay-name my-replay-001 \
    --event-source-arn arn:aws:events:us-east-1:123456789012:event-bus/default \
    --event-start-time "2026-02-01T00:00:00Z" \
    --event-end-time "2026-02-08T00:00:00Z" \
    --destination file://replay-destination.json

cat > replay-destination.json << 'EOF'
{
  "Arn": "arn:aws:events:us-east-1:123456789012:event-bus/replay-bus"
}
EOF

# Start replay with event pattern filter
aws events start-replay \
    --replay-name filtered-replay \
    --event-source-arn arn:aws:events:us-east-1:123456789012:event-bus/default \
    --event-start-time "2026-02-07T00:00:00Z" \
    --event-end-time "2026-02-08T00:00:00Z" \
    --destination Arn=arn:aws:events:us-east-1:123456789012:event-bus/default \
    --description "Replay EC2 events for testing"

# Describe replay
aws events describe-replay --replay-name my-replay-001

# List replays
aws events list-replays

# List replays for specific event bus
aws events list-replays \
    --event-source-arn arn:aws:events:us-east-1:123456789012:event-bus/custom-app-bus

# Cancel replay
aws events cancel-replay --replay-name my-replay-001
```

---

### API Destinations

#### Create and Manage Connections

```bash
# Create connection with API key authentication
aws events create-connection \
    --name webhook-connection \
    --description "Connection for webhook API" \
    --authorization-type API_KEY \
    --auth-parameters file://api-key-auth.json

cat > api-key-auth.json << 'EOF'
{
  "ApiKeyAuthParameters": {
    "ApiKeyName": "X-API-Key",
    "ApiKeyValue": "your-api-key-here"
  }
}
EOF

# Create connection with basic authentication
aws events create-connection \
    --name basic-auth-connection \
    --authorization-type BASIC \
    --auth-parameters file://basic-auth.json

cat > basic-auth.json << 'EOF'
{
  "BasicAuthParameters": {
    "Username": "apiuser",
    "Password": "apipassword"
  }
}
EOF

# Create connection with OAuth authentication
aws events create-connection \
    --name oauth-connection \
    --authorization-type OAUTH_CLIENT_CREDENTIALS \
    --auth-parameters file://oauth-auth.json

cat > oauth-auth.json << 'EOF'
{
  "OAuthParameters": {
    "ClientParameters": {
      "ClientID": "your-client-id"
    },
    "AuthorizationEndpoint": "https://oauth.example.com/authorize",
    "HttpMethod": "POST",
    "OAuthHttpParameters": {
      "HeaderParameters": [
        {
          "Key": "Content-Type",
          "Value": "application/x-www-form-urlencoded"
        }
      ]
    }
  }
}
EOF

# Describe connection
aws events describe-connection --name webhook-connection

# List connections
aws events list-connections

# List connections with specific state
aws events list-connections --connection-state AUTHORIZED

# Update connection
aws events update-connection \
    --name webhook-connection \
    --description "Updated webhook connection" \
    --authorization-type API_KEY \
    --auth-parameters file://updated-api-key-auth.json

# Deauthorize connection
aws events deauthorize-connection --name webhook-connection

# Delete connection
aws events delete-connection --name webhook-connection
```

#### Create and Manage API Destinations

```bash
# Create API destination
aws events create-api-destination \
    --name webhook-destination \
    --description "Webhook API destination" \
    --connection-arn arn:aws:events:us-east-1:123456789012:connection/webhook-connection/12345678-1234-1234-1234-123456789012 \
    --invocation-endpoint https://webhook.example.com/events \
    --http-method POST \
    --invocation-rate-limit-per-second 10

# Create API destination with specific headers
aws events create-api-destination \
    --name api-with-headers \
    --connection-arn arn:aws:events:us-east-1:123456789012:connection/webhook-connection/12345678-1234-1234-1234-123456789012 \
    --invocation-endpoint https://api.example.com/webhook \
    --http-method POST \
    --invocation-rate-limit-per-second 100

# Describe API destination
aws events describe-api-destination --name webhook-destination

# List API destinations
aws events list-api-destinations

# List API destinations by connection
aws events list-api-destinations \
    --connection-arn arn:aws:events:us-east-1:123456789012:connection/webhook-connection/12345678-1234-1234-1234-123456789012

# Update API destination
aws events update-api-destination \
    --name webhook-destination \
    --description "Updated webhook destination" \
    --invocation-endpoint https://new-webhook.example.com/events \
    --invocation-rate-limit-per-second 50

# Delete API destination
aws events delete-api-destination --name webhook-destination
```

#### Add API Destination as Target

```bash
# Add API destination as rule target
aws events put-targets \
    --rule my-api-rule \
    --targets file://api-destination-target.json

cat > api-destination-target.json << 'EOF'
[
  {
    "Id": "1",
    "Arn": "arn:aws:events:us-east-1:123456789012:api-destination/webhook-destination/12345678-1234-1234-1234-123456789012",
    "RoleArn": "arn:aws:iam::123456789012:role/EventBridgeAPIDestinationRole",
    "HttpParameters": {
      "HeaderParameters": {
        "X-Custom-Header": "CustomValue"
      },
      "QueryStringParameters": {
        "source": "eventbridge"
      }
    },
    "InputTransformer": {
      "InputPathsMap": {
        "time": "$.time",
        "detail": "$.detail"
      },
      "InputTemplate": "{\"timestamp\": <time>, \"data\": <detail>}"
    },
    "RetryPolicy": {
      "MaximumRetryAttempts": 2,
      "MaximumEventAge": 3600
    },
    "DeadLetterConfig": {
      "Arn": "arn:aws:sqs:us-east-1:123456789012:eventbridge-dlq"
    }
  }
]
EOF
```

---

### Schema Registry

#### Create and Manage Registries

```bash
# Create custom schema registry
aws schemas create-registry \
    --registry-name custom-app-registry \
    --description "Registry for custom application schemas"

# Describe registry
aws schemas describe-registry --registry-name custom-app-registry

# List registries
aws schemas list-registries

# Update registry
aws schemas update-registry \
    --registry-name custom-app-registry \
    --description "Updated description"

# Delete registry (must delete schemas first)
aws schemas delete-registry --registry-name custom-app-registry
```

#### Create and Manage Schemas

```bash
# Create schema
aws schemas create-schema \
    --registry-name custom-app-registry \
    --schema-name OrderPlaced \
    --type OpenApi3 \
    --description "Schema for order placed events" \
    --content file://order-schema.json

cat > order-schema.json << 'EOF'
{
  "openapi": "3.0.0",
  "info": {
    "version": "1.0.0",
    "title": "OrderPlaced"
  },
  "paths": {},
  "components": {
    "schemas": {
      "OrderPlaced": {
        "type": "object",
        "properties": {
          "orderId": {
            "type": "string"
          },
          "customerId": {
            "type": "string"
          },
          "items": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "productId": {"type": "string"},
                "quantity": {"type": "integer"},
                "price": {"type": "number"}
              }
            }
          },
          "totalAmount": {
            "type": "number"
          },
          "timestamp": {
            "type": "string",
            "format": "date-time"
          }
        },
        "required": ["orderId", "customerId", "totalAmount"]
      }
    }
  }
}
EOF

# Describe schema
aws schemas describe-schema \
    --registry-name custom-app-registry \
    --schema-name OrderPlaced

# Get schema content
aws schemas describe-schema \
    --registry-name custom-app-registry \
    --schema-name OrderPlaced \
    --query 'Content' \
    --output text

# List schemas in registry
aws schemas list-schemas --registry-name custom-app-registry

# List schema versions
aws schemas list-schema-versions \
    --registry-name custom-app-registry \
    --schema-name OrderPlaced

# Update schema (creates new version)
aws schemas update-schema \
    --registry-name custom-app-registry \
    --schema-name OrderPlaced \
    --description "Updated schema" \
    --content file://order-schema-v2.json

# Delete schema version
aws schemas delete-schema-version \
    --registry-name custom-app-registry \
    --schema-name OrderPlaced \
    --schema-version 2

# Delete schema
aws schemas delete-schema \
    --registry-name custom-app-registry \
    --schema-name OrderPlaced
```

#### Search and Discover Schemas

```bash
# Search schemas by keyword
aws schemas search-schemas \
    --registry-name custom-app-registry \
    --keywords "order"

# Search schemas across all registries
aws schemas search-schemas --keywords "ec2 state"

# Get code binding for schema (generate code)
aws schemas get-code-binding-source \
    --registry-name aws.events \
    --schema-name aws.ec2@EC2InstanceStateChangeNotification \
    --language Java8

# Export schema
aws schemas export-schema \
    --registry-name custom-app-registry \
    --schema-name OrderPlaced \
    --type OpenApi3 \
    --output text > exported-schema.json
```

#### Schema Discovery

```bash
# Start schema discovery for event bus
aws schemas put-resource-policy \
    --registry-name discovered-schemas \
    --policy file://discovery-policy.json

cat > discovery-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowEventBridgeToCreateSchema",
      "Effect": "Allow",
      "Principal": {
        "Service": "events.amazonaws.com"
      },
      "Action": [
        "schemas:CreateSchema",
        "schemas:UpdateSchema"
      ],
      "Resource": "*"
    }
  ]
}
EOF

# Enable schema discovery (via EventBridge console or API)
# List discovered schemas
aws schemas list-schemas --registry-name discovered-schemas
```

---

### Tags and Resource Management

#### Tag EventBridge Resources

```bash
# Tag a rule
aws events tag-resource \
    --resource-arn arn:aws:events:us-east-1:123456789012:rule/my-rule \
    --tags Key=Environment,Value=Production Key=Application,Value=OrderService Key=CostCenter,Value=Engineering

# Tag an event bus
aws events tag-resource \
    --resource-arn arn:aws:events:us-east-1:123456789012:event-bus/custom-app-bus \
    --tags Key=Environment,Value=Staging Key=Team,Value=DevOps

# List tags for resource
aws events list-tags-for-resource \
    --resource-arn arn:aws:events:us-east-1:123456789012:rule/my-rule

# Untag resource
aws events untag-resource \
    --resource-arn arn:aws:events:us-east-1:123456789012:rule/my-rule \
    --tag-keys Environment CostCenter
```

---

### Testing and Validation

#### Test Event Pattern

```bash
# Test if event matches pattern
aws events test-event-pattern \
    --event-pattern file://test-pattern.json \
    --event file://test-event.json

cat > test-pattern.json << 'EOF'
{
  "source": ["aws.ec2"],
  "detail-type": ["EC2 Instance State-change Notification"],
  "detail": {
    "state": ["terminated", "stopped"]
  }
}
EOF

cat > test-event.json << 'EOF'
{
  "version": "0",
  "id": "12345678-1234-1234-1234-123456789012",
  "detail-type": "EC2 Instance State-change Notification",
  "source": "aws.ec2",
  "account": "123456789012",
  "time": "2026-02-08T10:00:00Z",
  "region": "us-east-1",
  "resources": [
    "arn:aws:ec2:us-east-1:123456789012:instance/i-1234567890abcdef0"
  ],
  "detail": {
    "instance-id": "i-1234567890abcdef0",
    "state": "terminated"
  }
}
EOF

# Returns true or false whether event matches pattern
```

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