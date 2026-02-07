# Google Cloud Event-Driven Services - ACE & PCA Comprehensive Guide

## Table of Contents
1. [Overview](#overview)
2. [Cloud Scheduler](#cloud-scheduler)
3. [Cloud Tasks](#cloud-tasks)
4. [Workflows](#workflows)
5. [Eventarc](#eventarc)
6. [Service Comparison](#service-comparison)
7. [Integration Patterns](#integration-patterns)
8. [Security and IAM](#security-and-iam)
9. [Monitoring and Debugging](#monitoring-and-debugging)
10. [ACE Exam Focus](#ace-exam-focus)
11. [PCA Exam Focus](#pca-exam-focus)

---

## Overview

### Event-Driven Architecture on GCP

```
┌─────────────────────────────────────────────────────────────────────────┐
│                 EVENT-DRIVEN SERVICES LANDSCAPE                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  SCHEDULING & TRIGGERS                                                   │
│  ┌─────────────────┐      ┌─────────────────┐                          │
│  │ Cloud Scheduler │      │    Eventarc     │                          │
│  │ (Cron Jobs)     │      │ (Event Routing) │                          │
│  └────────┬────────┘      └────────┬────────┘                          │
│           │                        │                                     │
│           ▼                        ▼                                     │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    EVENT TARGETS                                 │   │
│  │                                                                   │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │   │
│  │  │Cloud Functions│  │  Cloud Run   │  │    HTTP      │          │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘          │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │   │
│  │  │   Pub/Sub    │  │ Cloud Tasks  │  │  Workflows   │          │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘          │   │
│  │                                                                   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ORCHESTRATION & TASK MANAGEMENT                                         │
│  ┌─────────────────┐      ┌─────────────────┐                          │
│  │   Workflows     │      │   Cloud Tasks   │                          │
│  │ (Orchestration) │      │  (Task Queues)  │                          │
│  └─────────────────┘      └─────────────────┘                          │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Service Summary

| Service | Purpose | Key Use Cases |
|---------|---------|---------------|
| **Cloud Scheduler** | Cron-based job scheduling | Scheduled reports, periodic cleanup |
| **Cloud Tasks** | Asynchronous task queuing | Deferred execution, rate limiting |
| **Workflows** | Service orchestration | Multi-step processes, approvals |
| **Eventarc** | Event routing | React to GCP/custom events |

---

## Cloud Scheduler

### What is Cloud Scheduler?

Cloud Scheduler is a fully managed enterprise-grade cron job scheduler. It allows you to schedule virtually any job including:
- HTTP/HTTPS endpoints
- Pub/Sub topics
- App Engine applications

### Key Features

| Feature | Description |
|---------|-------------|
| **Unix Cron Format** | Standard cron expressions |
| **Multiple Targets** | HTTP, Pub/Sub, App Engine |
| **Retry Policies** | Configurable retries |
| **Time Zones** | Any IANA time zone |
| **OAuth/OIDC** | Secure authenticated requests |

### Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    CLOUD SCHEDULER ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────┐                                                    │
│  │ Cloud Scheduler │                                                    │
│  │    Job          │                                                    │
│  │  ┌───────────┐  │                                                    │
│  │  │  Cron     │  │                                                    │
│  │  │ Schedule  │  │                                                    │
│  │  └───────────┘  │                                                    │
│  └────────┬────────┘                                                    │
│           │                                                              │
│           │ Trigger                                                      │
│           │                                                              │
│  ┌────────┴────────────────────────────────────────────────────────┐   │
│  │                        TARGET OPTIONS                             │   │
│  │                                                                    │   │
│  │  ┌─────────────┐   ┌─────────────┐   ┌─────────────────┐        │   │
│  │  │    HTTP     │   │   Pub/Sub   │   │   App Engine    │        │   │
│  │  │  Endpoint   │   │   Topic     │   │   Handler       │        │   │
│  │  └──────┬──────┘   └──────┬──────┘   └────────┬────────┘        │   │
│  │         │                 │                    │                  │   │
│  └─────────┼─────────────────┼────────────────────┼──────────────────┘   │
│            │                 │                    │                      │
│            ▼                 ▼                    ▼                      │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐                   │
│  │  Cloud Run  │   │  Subscriber │   │ App Engine  │                   │
│  │  Functions  │   │  Services   │   │   Service   │                   │
│  │    API      │   │             │   │             │                   │
│  └─────────────┘   └─────────────┘   └─────────────┘                   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Creating Scheduler Jobs

#### HTTP Target

```bash
# Create HTTP job
gcloud scheduler jobs create http daily-report \
    --location=us-central1 \
    --schedule="0 9 * * *" \
    --uri="https://my-service-xyz.run.app/generate-report" \
    --http-method=POST \
    --message-body='{"type": "daily"}' \
    --headers="Content-Type=application/json" \
    --time-zone="America/New_York" \
    --attempt-deadline=30m

# With OIDC authentication
gcloud scheduler jobs create http secure-job \
    --location=us-central1 \
    --schedule="0 */6 * * *" \
    --uri="https://my-service-xyz.run.app/task" \
    --oidc-service-account-email=scheduler-sa@project.iam.gserviceaccount.com \
    --oidc-token-audience="https://my-service-xyz.run.app"
```

#### Pub/Sub Target

```bash
# Create Pub/Sub job
gcloud scheduler jobs create pubsub hourly-sync \
    --location=us-central1 \
    --schedule="0 * * * *" \
    --topic=data-sync-trigger \
    --message-body='{"action": "sync"}' \
    --attributes="source=scheduler,priority=normal" \
    --time-zone="UTC"
```

#### App Engine Target

```bash
# Create App Engine job
gcloud scheduler jobs create app-engine cleanup-job \
    --location=us-central1 \
    --schedule="0 3 * * *" \
    --service=cleanup-service \
    --relative-uri=/cleanup \
    --http-method=POST
```

### Cron Expression Reference

```
 ┌───────────── minute (0 - 59)
 │ ┌───────────── hour (0 - 23)
 │ │ ┌───────────── day of month (1 - 31)
 │ │ │ ┌───────────── month (1 - 12)
 │ │ │ │ ┌───────────── day of week (0 - 6) (Sunday = 0)
 │ │ │ │ │
 │ │ │ │ │
 * * * * *
```

| Expression | Description |
|------------|-------------|
| `0 9 * * *` | Every day at 9:00 AM |
| `*/15 * * * *` | Every 15 minutes |
| `0 0 1 * *` | First day of every month |
| `0 9 * * 1-5` | Weekdays at 9:00 AM |
| `0 */6 * * *` | Every 6 hours |

### Job Management

```bash
# List jobs
gcloud scheduler jobs list --location=us-central1

# Describe job
gcloud scheduler jobs describe daily-report --location=us-central1

# Update job
gcloud scheduler jobs update http daily-report \
    --location=us-central1 \
    --schedule="0 10 * * *"

# Pause/Resume
gcloud scheduler jobs pause daily-report --location=us-central1
gcloud scheduler jobs resume daily-report --location=us-central1

# Run immediately (manual trigger)
gcloud scheduler jobs run daily-report --location=us-central1

# Delete job
gcloud scheduler jobs delete daily-report --location=us-central1
```

---

## Cloud Tasks

### What is Cloud Tasks?

Cloud Tasks is a fully managed service for asynchronous task execution with:
- **Rate limiting**: Control execution speed
- **Retry policies**: Automatic retries with backoff
- **Delayed execution**: Schedule tasks for later
- **Deduplication**: Prevent duplicate task execution

### Key Features

| Feature | Description |
|---------|-------------|
| **Task Queues** | Organize and manage tasks |
| **Rate Limiting** | Control dispatch rate |
| **Retries** | Configurable retry policies |
| **Delayed Execution** | Schedule tasks in future |
| **Task Deduplication** | Prevent duplicates |

### Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      CLOUD TASKS ARCHITECTURE                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  PRODUCERS                                                               │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐                        │
│  │ App Engine │  │ Cloud Run  │  │   GKE      │                        │
│  └──────┬─────┘  └─────┬──────┘  └─────┬──────┘                        │
│         │              │               │                                 │
│         └──────────────┼───────────────┘                                │
│                        │                                                 │
│                        ▼                                                 │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      CLOUD TASKS                                 │   │
│  │                                                                   │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │   │
│  │  │   Queue 1   │  │   Queue 2   │  │   Queue 3   │             │   │
│  │  │ Rate: 100/s │  │ Rate: 10/s  │  │ Rate: 1/s   │             │   │
│  │  │             │  │             │  │             │             │   │
│  │  │ ┌────────┐  │  │ ┌────────┐  │  │ ┌────────┐  │             │   │
│  │  │ │ Task A │  │  │ │ Task D │  │  │ │ Task F │  │             │   │
│  │  │ │ Task B │  │  │ │ Task E │  │  │ └────────┘  │             │   │
│  │  │ │ Task C │  │  │ └────────┘  │  │             │             │   │
│  │  │ └────────┘  │  │             │  │             │             │   │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │   │
│  │         │               │               │                      │   │
│  └─────────┼───────────────┼───────────────┼──────────────────────┘   │
│            │               │               │                          │
│  CONSUMERS │               │               │                          │
│            ▼               ▼               ▼                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                   │
│  │ Cloud Run   │  │ HTTP API    │  │ App Engine  │                   │
│  └─────────────┘  └─────────────┘  └─────────────┘                   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Creating Queues

```bash
# Create a queue
gcloud tasks queues create my-queue \
    --location=us-central1 \
    --max-dispatches-per-second=100 \
    --max-concurrent-dispatches=500 \
    --max-attempts=5 \
    --min-backoff=1s \
    --max-backoff=3600s \
    --max-doublings=16

# Create with routing override (App Engine)
gcloud tasks queues create app-engine-queue \
    --location=us-central1 \
    --routing-override=service:worker-service,version:v1
```

### Creating Tasks

#### Using gcloud

```bash
# Create HTTP task
gcloud tasks create-http-task \
    --queue=my-queue \
    --location=us-central1 \
    --url="https://my-service.run.app/process" \
    --http-method=POST \
    --body-content='{"id": "123"}' \
    --header="Content-Type: application/json" \
    --oidc-service-account-email=tasks-sa@project.iam.gserviceaccount.com

# Create App Engine task
gcloud tasks create-app-engine-task \
    --queue=app-engine-queue \
    --location=us-central1 \
    --relative-uri=/process \
    --method=POST \
    --body-content='{"id": "123"}'
```

#### Using Python SDK

```python
from google.cloud import tasks_v2
from google.protobuf import timestamp_pb2
import datetime
import json

def create_http_task(project, location, queue, url, payload, delay_seconds=0):
    """Create an HTTP task."""
    client = tasks_v2.CloudTasksClient()
    
    parent = client.queue_path(project, location, queue)
    
    task = {
        'http_request': {
            'http_method': tasks_v2.HttpMethod.POST,
            'url': url,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps(payload).encode()
        }
    }
    
    # Add OIDC token for authentication
    task['http_request']['oidc_token'] = {
        'service_account_email': 'tasks-sa@project.iam.gserviceaccount.com',
        'audience': url
    }
    
    # Schedule for later if delay specified
    if delay_seconds > 0:
        d = datetime.datetime.utcnow() + datetime.timedelta(seconds=delay_seconds)
        timestamp = timestamp_pb2.Timestamp()
        timestamp.FromDatetime(d)
        task['schedule_time'] = timestamp
    
    response = client.create_task(parent=parent, task=task)
    print(f'Created task: {response.name}')
    return response

# Usage
create_http_task(
    project='my-project',
    location='us-central1',
    queue='my-queue',
    url='https://my-service.run.app/process',
    payload={'user_id': '123', 'action': 'send_email'},
    delay_seconds=3600  # Execute in 1 hour
)
```

### Task Deduplication

```python
def create_deduplicated_task(project, location, queue, url, payload, task_id):
    """Create a task with deduplication."""
    client = tasks_v2.CloudTasksClient()
    
    parent = client.queue_path(project, location, queue)
    task_name = f'{parent}/tasks/{task_id}'
    
    task = {
        'name': task_name,  # Explicit task ID for deduplication
        'http_request': {
            'http_method': tasks_v2.HttpMethod.POST,
            'url': url,
            'body': json.dumps(payload).encode()
        }
    }
    
    try:
        response = client.create_task(parent=parent, task=task)
        return response
    except Exception as e:
        if 'ALREADY_EXISTS' in str(e):
            print(f'Task {task_id} already exists')
            return None
        raise
```

### Queue Management

```bash
# List queues
gcloud tasks queues list --location=us-central1

# Describe queue
gcloud tasks queues describe my-queue --location=us-central1

# Update queue
gcloud tasks queues update my-queue \
    --location=us-central1 \
    --max-dispatches-per-second=200

# Pause/Resume queue
gcloud tasks queues pause my-queue --location=us-central1
gcloud tasks queues resume my-queue --location=us-central1

# Purge queue (delete all tasks)
gcloud tasks queues purge my-queue --location=us-central1

# Delete queue
gcloud tasks queues delete my-queue --location=us-central1
```

---

## Workflows

### What is Workflows?

Workflows is a fully managed orchestration service for executing multi-step logic across GCP services and HTTP APIs.

### Key Features

| Feature | Description |
|---------|-------------|
| **YAML/JSON Syntax** | Declarative workflow definition |
| **Built-in Connectors** | Native GCP service integration |
| **Error Handling** | Try-catch-retry patterns |
| **Conditional Logic** | If-else branching |
| **Parallel Execution** | Run steps concurrently |
| **Subworkflows** | Reusable workflow components |

### Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      WORKFLOWS ARCHITECTURE                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  TRIGGERS                                                                │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐       │
│  │  Eventarc  │  │ Scheduler  │  │   Direct   │  │    HTTP    │       │
│  │            │  │            │  │   API Call │  │  Webhook   │       │
│  └──────┬─────┘  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘       │
│         │              │               │               │               │
│         └──────────────┼───────────────┼───────────────┘               │
│                        │               │                                │
│                        ▼               ▼                                │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                       WORKFLOW ENGINE                            │   │
│  │                                                                   │   │
│  │    ┌──────────┐     ┌──────────┐     ┌──────────┐              │   │
│  │    │  Step 1  │────►│  Step 2  │────►│  Step 3  │              │   │
│  │    └──────────┘     └──────────┘     └──────────┘              │   │
│  │         │                                  │                    │   │
│  │         │              ┌───────────────────┘                    │   │
│  │         │              │                                        │   │
│  │         ▼              ▼                                        │   │
│  │    ┌──────────┐  ┌──────────┐                                  │   │
│  │    │Subworkflow│  │ Parallel │                                  │   │
│  │    │  Call    │  │ Branches │                                  │   │
│  │    └──────────┘  └──────────┘                                  │   │
│  │                                                                   │   │
│  └────────────────────────────────────┬────────────────────────────┘   │
│                                       │                                 │
│                         ┌─────────────┼─────────────┐                  │
│                         │             │             │                  │
│                         ▼             ▼             ▼                  │
│                  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│                  │Cloud Run │  │ BigQuery │  │  HTTP    │             │
│                  │Functions │  │ Firestore│  │  APIs    │             │
│                  └──────────┘  └──────────┘  └──────────┘             │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Workflow Definition

#### Basic Workflow

```yaml
# order-processing.yaml
main:
  params: [input]
  steps:
    - init:
        assign:
          - orderId: ${input.orderId}
          - customerId: ${input.customerId}
    
    - validateOrder:
        call: http.post
        args:
          url: https://orders-service.run.app/validate
          body:
            orderId: ${orderId}
            customerId: ${customerId}
        result: validationResult
    
    - checkValidation:
        switch:
          - condition: ${validationResult.body.valid == true}
            next: processPayment
          - condition: ${validationResult.body.valid == false}
            next: rejectOrder
    
    - processPayment:
        call: http.post
        args:
          url: https://payment-service.run.app/charge
          body:
            orderId: ${orderId}
            amount: ${validationResult.body.amount}
        result: paymentResult
        next: fulfillOrder
    
    - fulfillOrder:
        call: http.post
        args:
          url: https://fulfillment-service.run.app/ship
          body:
            orderId: ${orderId}
        result: fulfillmentResult
        next: notifyCustomer
    
    - notifyCustomer:
        call: http.post
        args:
          url: https://notification-service.run.app/email
          body:
            customerId: ${customerId}
            message: "Your order ${orderId} has been shipped!"
        result: notificationResult
        next: returnSuccess
    
    - rejectOrder:
        return:
          status: "rejected"
          orderId: ${orderId}
    
    - returnSuccess:
        return:
          status: "completed"
          orderId: ${orderId}
          trackingNumber: ${fulfillmentResult.body.trackingNumber}
```

#### Error Handling

```yaml
main:
  params: [input]
  steps:
    - processWithRetry:
        try:
          call: http.post
          args:
            url: https://external-api.com/process
            body: ${input}
          result: apiResult
        retry:
          predicate: ${default_retry_predicate}
          max_retries: 3
          backoff:
            initial_delay: 2
            max_delay: 60
            multiplier: 2
        except:
          as: e
          steps:
            - handleError:
                switch:
                  - condition: ${e.code == 404}
                    return:
                      error: "Resource not found"
                  - condition: ${e.code == 500}
                    next: fallbackProcess
            - raiseError:
                raise: ${e}
    
    - fallbackProcess:
        call: http.post
        args:
          url: https://backup-api.com/process
          body: ${input}
        result: fallbackResult
        next: returnResult
    
    - returnResult:
        return: ${apiResult}
```

#### Parallel Execution

```yaml
main:
  params: [input]
  steps:
    - parallelOperations:
        parallel:
          branches:
            - branch1:
                steps:
                  - fetchUserData:
                      call: http.get
                      args:
                        url: https://user-service.run.app/user/${input.userId}
                      result: userData
            - branch2:
                steps:
                  - fetchOrderHistory:
                      call: http.get
                      args:
                        url: https://order-service.run.app/history/${input.userId}
                      result: orderHistory
            - branch3:
                steps:
                  - fetchRecommendations:
                      call: http.get
                      args:
                        url: https://ml-service.run.app/recommend/${input.userId}
                      result: recommendations
    
    - combineResults:
        return:
          user: ${userData.body}
          orders: ${orderHistory.body}
          recommendations: ${recommendations.body}
```

#### GCP Service Connectors

```yaml
main:
  params: [input]
  steps:
    # BigQuery
    - runQuery:
        call: googleapis.bigquery.v2.jobs.query
        args:
          projectId: ${sys.get_env("GOOGLE_CLOUD_PROJECT_ID")}
          body:
            query: "SELECT * FROM dataset.table WHERE id = '${input.id}'"
            useLegacySql: false
        result: queryResult
    
    # Cloud Storage
    - readFromGCS:
        call: googleapis.storage.v1.objects.get
        args:
          bucket: my-bucket
          object: data/file.json
        result: gcsObject
    
    # Firestore
    - getDocument:
        call: googleapis.firestore.v1.projects.databases.documents.get
        args:
          name: projects/my-project/databases/(default)/documents/users/${input.userId}
        result: document
    
    # Pub/Sub
    - publishMessage:
        call: googleapis.pubsub.v1.projects.topics.publish
        args:
          topic: projects/my-project/topics/events
          body:
            messages:
              - data: ${base64.encode(json.encode(input))}
        result: publishResult
```

### Deploying Workflows

```bash
# Deploy workflow
gcloud workflows deploy order-processor \
    --location=us-central1 \
    --source=order-processing.yaml \
    --service-account=workflow-sa@project.iam.gserviceaccount.com

# Execute workflow
gcloud workflows run order-processor \
    --location=us-central1 \
    --data='{"orderId": "ORD-123", "customerId": "CUST-456"}'

# List workflows
gcloud workflows list --location=us-central1

# Describe workflow
gcloud workflows describe order-processor --location=us-central1

# List executions
gcloud workflows executions list order-processor --location=us-central1

# View execution details
gcloud workflows executions describe EXECUTION_ID \
    --workflow=order-processor \
    --location=us-central1
```

---

## Eventarc

### What is Eventarc?

Eventarc is an eventing platform that routes events from GCP services, SaaS applications, and custom sources to targets like Cloud Run, Workflows, and GKE.

### Key Features

| Feature | Description |
|---------|-------------|
| **Event Sources** | GCP audit logs, direct events, Pub/Sub |
| **Event Targets** | Cloud Run, Workflows, GKE |
| **Filtering** | Route events based on criteria |
| **CloudEvents** | Standard event format |

### Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      EVENTARC ARCHITECTURE                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  EVENT SOURCES                                                           │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  GOOGLE CLOUD SOURCES                                            │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │   │
│  │  │ Audit Logs  │  │Cloud Storage│  │  BigQuery   │             │   │
│  │  │ (120+ svcs) │  │   Events    │  │   Events    │             │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘             │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  CUSTOM / THIRD-PARTY                                            │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │   │
│  │  │   Pub/Sub   │  │Custom Events│  │Third-party  │             │   │
│  │  │   Topics    │  │(via Pub/Sub)│  │   SaaS      │             │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘             │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                          │                                               │
│                          ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                     EVENTARC TRIGGERS                            │   │
│  │                                                                   │   │
│  │     ┌───────────────────────────────────────────────────┐      │   │
│  │     │  Filters (Event Type, Source, Attributes)         │      │   │
│  │     └───────────────────────────────────────────────────┘      │   │
│  │                                                                   │   │
│  └───────────────────────────┬─────────────────────────────────────┘   │
│                              │                                          │
│                    ┌─────────┴─────────┐                               │
│                    │                   │                               │
│                    ▼                   ▼                               │
│  ┌─────────────────────┐   ┌─────────────────────┐                    │
│  │      Cloud Run      │   │     Workflows       │                    │
│  │                     │   │                     │                    │
│  └─────────────────────┘   └─────────────────────┘                    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Event Sources

| Source Type | Examples |
|-------------|----------|
| **Direct Events** | Cloud Storage (finalize, delete, archive, metadata update) |
| **Audit Logs** | BigQuery, Compute Engine, Cloud SQL, etc. (120+ services) |
| **Pub/Sub** | Custom events via Pub/Sub topics |
| **Third-party** | Firebase, Stripe, etc. |

### Creating Triggers

#### Cloud Storage Events

```bash
# Trigger on new file upload
gcloud eventarc triggers create storage-trigger \
    --location=us-central1 \
    --destination-run-service=file-processor \
    --destination-run-region=us-central1 \
    --event-filters="type=google.cloud.storage.object.v1.finalized" \
    --event-filters="bucket=my-bucket" \
    --service-account=eventarc-sa@project.iam.gserviceaccount.com

# Trigger on file deletion
gcloud eventarc triggers create delete-trigger \
    --location=us-central1 \
    --destination-run-service=cleanup-handler \
    --destination-run-region=us-central1 \
    --event-filters="type=google.cloud.storage.object.v1.deleted" \
    --event-filters="bucket=my-bucket" \
    --service-account=eventarc-sa@project.iam.gserviceaccount.com
```

#### Audit Log Events

```bash
# Trigger on BigQuery job completion
gcloud eventarc triggers create bq-trigger \
    --location=us-central1 \
    --destination-run-service=bq-handler \
    --destination-run-region=us-central1 \
    --event-filters="type=google.cloud.audit.log.v1.written" \
    --event-filters="serviceName=bigquery.googleapis.com" \
    --event-filters="methodName=google.cloud.bigquery.v2.JobService.InsertJob" \
    --service-account=eventarc-sa@project.iam.gserviceaccount.com

# Trigger on Compute Engine instance creation
gcloud eventarc triggers create vm-trigger \
    --location=us-central1 \
    --destination-run-service=vm-handler \
    --destination-run-region=us-central1 \
    --event-filters="type=google.cloud.audit.log.v1.written" \
    --event-filters="serviceName=compute.googleapis.com" \
    --event-filters="methodName=v1.compute.instances.insert" \
    --service-account=eventarc-sa@project.iam.gserviceaccount.com
```

#### Pub/Sub Events

```bash
# Trigger from Pub/Sub topic
gcloud eventarc triggers create pubsub-trigger \
    --location=us-central1 \
    --destination-run-service=message-processor \
    --destination-run-region=us-central1 \
    --transport-topic=projects/my-project/topics/my-topic \
    --service-account=eventarc-sa@project.iam.gserviceaccount.com
```

#### Workflow as Target

```bash
# Route events to Workflows
gcloud eventarc triggers create workflow-trigger \
    --location=us-central1 \
    --destination-workflow=order-processor \
    --destination-workflow-location=us-central1 \
    --event-filters="type=google.cloud.storage.object.v1.finalized" \
    --event-filters="bucket=orders-bucket" \
    --service-account=eventarc-sa@project.iam.gserviceaccount.com
```

### CloudEvents Format

```json
{
  "specversion": "1.0",
  "type": "google.cloud.storage.object.v1.finalized",
  "source": "//storage.googleapis.com/projects/_/buckets/my-bucket",
  "subject": "objects/my-file.txt",
  "id": "1234567890",
  "time": "2024-01-15T10:30:00.000Z",
  "datacontenttype": "application/json",
  "data": {
    "bucket": "my-bucket",
    "name": "my-file.txt",
    "generation": "1234567890",
    "metageneration": "1",
    "contentType": "text/plain",
    "size": "1024",
    "md5Hash": "abc123...",
    "crc32c": "def456...",
    "etag": "xyz789...",
    "updated": "2024-01-15T10:30:00.000Z",
    "storageClass": "STANDARD"
  }
}
```

### Handling Events in Cloud Run

```python
from flask import Flask, request
import json

app = Flask(__name__)

@app.route('/', methods=['POST'])
def handle_event():
    # Get CloudEvent headers
    ce_type = request.headers.get('ce-type')
    ce_source = request.headers.get('ce-source')
    ce_subject = request.headers.get('ce-subject')
    ce_id = request.headers.get('ce-id')
    
    # Get event data
    event_data = request.get_json()
    
    print(f"Received event: {ce_type}")
    print(f"Source: {ce_source}")
    print(f"Subject: {ce_subject}")
    print(f"Data: {json.dumps(event_data, indent=2)}")
    
    # Process based on event type
    if ce_type == 'google.cloud.storage.object.v1.finalized':
        bucket = event_data.get('bucket')
        name = event_data.get('name')
        process_new_file(bucket, name)
    
    return 'OK', 200

def process_new_file(bucket, name):
    print(f"Processing file: gs://{bucket}/{name}")
    # Add your processing logic here

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
```

### Trigger Management

```bash
# List triggers
gcloud eventarc triggers list --location=us-central1

# Describe trigger
gcloud eventarc triggers describe storage-trigger --location=us-central1

# Update trigger
gcloud eventarc triggers update storage-trigger \
    --location=us-central1 \
    --destination-run-service=new-processor

# Delete trigger
gcloud eventarc triggers delete storage-trigger --location=us-central1
```

---

## Service Comparison

### When to Use Which Service

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    DECISION FLOWCHART                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    WHAT DO YOU NEED?                             │   │
│  └──────────────────────────┬──────────────────────────────────────┘   │
│                              │                                          │
│          ┌───────────────────┼───────────────────┐                     │
│          │                   │                   │                     │
│          ▼                   ▼                   ▼                     │
│  ┌───────────────┐   ┌───────────────┐   ┌───────────────┐            │
│  │  Scheduled    │   │React to Events│   │  Async Task   │            │
│  │  Execution    │   │(GCP/Custom)   │   │  Processing   │            │
│  └───────┬───────┘   └───────┬───────┘   └───────┬───────┘            │
│          │                   │                   │                     │
│          ▼                   ▼                   │                     │
│  ┌───────────────┐   ┌───────────────┐          │                     │
│  │   SCHEDULER   │   │   EVENTARC    │          │                     │
│  │  (Cron Jobs)  │   │(Event Routing)│          │                     │
│  └───────────────┘   └───────────────┘          │                     │
│                                                  │                     │
│          ┌───────────────────────────────────────┘                     │
│          │                                                              │
│          ▼                                                              │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │           TASK COMPLEXITY                                        │   │
│  └──────────────────────────┬──────────────────────────────────────┘   │
│                              │                                          │
│          ┌───────────────────┼───────────────────┐                     │
│          │                   │                   │                     │
│          ▼                   ▼                   ▼                     │
│  ┌───────────────┐   ┌───────────────┐   ┌───────────────┐            │
│  │Simple Dispatch│   │ Multi-Step   │   │ Rate Limited  │            │
│  │ to Service    │   │ Orchestration│   │ Task Queue    │            │
│  └───────┬───────┘   └───────┬───────┘   └───────┬───────┘            │
│          │                   │                   │                     │
│          ▼                   ▼                   ▼                     │
│  ┌───────────────┐   ┌───────────────┐   ┌───────────────┐            │
│  │ Direct HTTP/  │   │   WORKFLOWS   │   │  CLOUD TASKS  │            │
│  │   Pub/Sub     │   │(Orchestration)│   │ (Task Queues) │            │
│  └───────────────┘   └───────────────┘   └───────────────┘            │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Comparison Matrix

| Feature | Scheduler | Tasks | Workflows | Eventarc |
|---------|-----------|-------|-----------|----------|
| **Primary Use** | Cron jobs | Async tasks | Orchestration | Event routing |
| **Trigger** | Time-based | API call | API/Event | GCP events |
| **Targets** | HTTP, Pub/Sub | HTTP, App Engine | HTTP, GCP APIs | Cloud Run, Workflows |
| **Rate Limiting** | ❌ | ✅ | ❌ | ❌ |
| **Multi-step** | ❌ | ❌ | ✅ | ❌ |
| **Retry** | ✅ | ✅ | ✅ | ✅ |
| **Delay** | ✅ (schedule) | ✅ | ✅ (wait) | ❌ |

---

## Integration Patterns

### Pattern 1: Scheduled ETL Pipeline

```
Cloud Scheduler → Cloud Tasks → Cloud Run (ETL) → BigQuery
```

```bash
# Scheduler triggers task queue at 2 AM
gcloud scheduler jobs create http etl-trigger \
    --schedule="0 2 * * *" \
    --uri="https://task-creator.run.app/create-etl-task" \
    --http-method=POST

# Task is queued and dispatched to ETL service
# (with rate limiting to prevent overwhelming sources)
```

### Pattern 2: Event-Driven File Processing

```
GCS Upload → Eventarc → Workflows → (Validate → Transform → Load)
```

```bash
# Eventarc routes file uploads to Workflow
gcloud eventarc triggers create file-processor \
    --destination-workflow=file-pipeline \
    --event-filters="type=google.cloud.storage.object.v1.finalized" \
    --event-filters="bucket=incoming-files"
```

### Pattern 3: Order Processing Pipeline

```yaml
# Complete order processing workflow
main:
  params: [input]
  steps:
    # Validate order
    - validate:
        call: http.post
        args:
          url: ${validation_service}
          body: ${input}
        result: validation
    
    # Parallel: Reserve inventory & Check payment
    - parallelChecks:
        parallel:
          branches:
            - inventory:
                call: http.post
                args:
                  url: ${inventory_service}/reserve
                  body: {orderId: ${input.orderId}, items: ${input.items}}
                result: inventoryResult
            - payment:
                call: http.post
                args:
                  url: ${payment_service}/authorize
                  body: {orderId: ${input.orderId}, amount: ${input.total}}
                result: paymentResult
    
    # Process payment
    - chargePayment:
        call: http.post
        args:
          url: ${payment_service}/charge
          body: {authId: ${paymentResult.body.authId}}
        result: chargeResult
    
    # Queue fulfillment task (rate limited)
    - queueFulfillment:
        call: googleapis.cloudtasks.v2.projects.locations.queues.tasks.create
        args:
          parent: projects/my-project/locations/us-central1/queues/fulfillment
          body:
            task:
              httpRequest:
                url: ${fulfillment_service}/ship
                body: ${base64.encode(json.encode(input))}
        result: taskResult
    
    - returnResult:
        return:
          status: "processing"
          orderId: ${input.orderId}
          fulfillmentTaskId: ${taskResult.name}
```

---

## Security and IAM

### Required Roles

| Service | Role | Description |
|---------|------|-------------|
| **Scheduler** | `roles/cloudscheduler.admin` | Full control |
| **Scheduler** | `roles/cloudscheduler.jobRunner` | Run jobs |
| **Tasks** | `roles/cloudtasks.admin` | Full control |
| **Tasks** | `roles/cloudtasks.enqueuer` | Create tasks |
| **Workflows** | `roles/workflows.admin` | Full control |
| **Workflows** | `roles/workflows.invoker` | Execute workflows |
| **Eventarc** | `roles/eventarc.admin` | Full control |
| **Eventarc** | `roles/eventarc.developer` | Create triggers |

### Service Account Setup

```bash
# Create service account for Scheduler
gcloud iam service-accounts create scheduler-invoker \
    --display-name="Scheduler Invoker"

# Grant Cloud Run invoker role
gcloud run services add-iam-policy-binding my-service \
    --member="serviceAccount:scheduler-invoker@project.iam.gserviceaccount.com" \
    --role="roles/run.invoker"

# Create service account for Eventarc
gcloud iam service-accounts create eventarc-sa \
    --display-name="Eventarc Service Account"

# Grant required roles
gcloud projects add-iam-policy-binding my-project \
    --member="serviceAccount:eventarc-sa@project.iam.gserviceaccount.com" \
    --role="roles/eventarc.eventReceiver"

gcloud projects add-iam-policy-binding my-project \
    --member="serviceAccount:eventarc-sa@project.iam.gserviceaccount.com" \
    --role="roles/run.invoker"
```

---

## Monitoring and Debugging

### Cloud Monitoring

```bash
# View Scheduler job metrics
gcloud monitoring metrics list \
    --filter="metric.type=starts_with(\"cloudscheduler.googleapis.com\")"

# View Tasks metrics
gcloud monitoring metrics list \
    --filter="metric.type=starts_with(\"cloudtasks.googleapis.com\")"

# View Workflows metrics
gcloud monitoring metrics list \
    --filter="metric.type=starts_with(\"workflows.googleapis.com\")"
```

### Key Metrics

| Service | Metric | Description |
|---------|--------|-------------|
| **Scheduler** | `job/attempt_count` | Job execution attempts |
| **Tasks** | `queue/task_attempt_count` | Task execution attempts |
| **Tasks** | `queue/depth` | Tasks waiting in queue |
| **Workflows** | `execution_count` | Workflow executions |
| **Workflows** | `execution_time` | Execution duration |

### Logging

```bash
# Scheduler logs
gcloud logging read 'resource.type="cloud_scheduler_job"' --limit=50

# Tasks logs
gcloud logging read 'resource.type="cloud_tasks_queue"' --limit=50

# Workflows logs
gcloud logging read 'resource.type="workflows.googleapis.com/Workflow"' --limit=50

# Eventarc logs
gcloud logging read 'resource.type="eventarc.googleapis.com/Trigger"' --limit=50
```

---

## ACE Exam Focus

### Key Concepts

1. **Cloud Scheduler**: Cron job service for scheduled tasks
2. **Cloud Tasks**: Async task execution with rate limiting
3. **Workflows**: Multi-step service orchestration
4. **Eventarc**: Event routing from GCP services

### ACE gcloud Commands

```bash
# Scheduler
gcloud scheduler jobs create http JOB_NAME --schedule="CRON" --uri=URL
gcloud scheduler jobs run JOB_NAME --location=REGION
gcloud scheduler jobs list --location=REGION

# Tasks
gcloud tasks queues create QUEUE_NAME --location=REGION
gcloud tasks create-http-task --queue=QUEUE --url=URL

# Workflows
gcloud workflows deploy WORKFLOW_NAME --source=FILE.yaml
gcloud workflows run WORKFLOW_NAME --data='JSON'
gcloud workflows executions list WORKFLOW_NAME

# Eventarc
gcloud eventarc triggers create TRIGGER_NAME \
    --destination-run-service=SERVICE \
    --event-filters="type=EVENT_TYPE"
```

### Sample ACE Questions

**Q1:** You need to run a cleanup job every day at midnight. Which service should you use?
- **A:** Cloud Scheduler with cron schedule `0 0 * * *`

**Q2:** How do you prevent a downstream service from being overwhelmed by too many requests?
- **A:** Use Cloud Tasks with rate limiting configured on the queue

**Q3:** You want to automatically process files when they are uploaded to Cloud Storage. What should you use?
- **A:** Eventarc trigger with Cloud Storage finalize event

---

## PCA Exam Focus

### Architecture Patterns

#### Pattern: Asynchronous Order Processing

```
Web App → Pub/Sub → Cloud Tasks → Order Service → Database
                        ↓
                   Notification Service
```

#### Pattern: Event-Driven Data Pipeline

```
Data Sources → Cloud Storage → Eventarc → Workflows
                                              ↓
                                    ┌─────────┴─────────┐
                                    ↓                   ↓
                              Validate           Transform
                                    ↓                   ↓
                                    └───────┬───────────┘
                                            ↓
                                       BigQuery
```

### Sample PCA Questions

**Q1:** Design a system that processes customer orders with the following requirements:
- Orders must be processed in order per customer
- System should handle 10,000 orders/minute peaks
- Failed orders should be retried with exponential backoff

**A:**
```
Order API → Cloud Tasks (per-customer queues) → Order Processor

Configuration:
- One queue per customer segment for ordering guarantees
- Rate limit: 200 tasks/second per queue
- Max retries: 5 with exponential backoff
- DLQ for persistently failed orders
```

**Q2:** How would you implement a multi-step approval workflow that:
- Validates request
- Gets manager approval
- Provisions resources if approved
- Sends notifications

**A:** Use Workflows with:
```yaml
main:
  steps:
    - validate: # HTTP call to validation service
    - getApproval: # HTTP call with human-in-loop via callback
    - provision: # Call GCP APIs to create resources
    - notify: # Send email/Slack notification
```

**Q3:** Compare using Eventarc vs Pub/Sub for event-driven architecture.

**A:**
| Aspect | Eventarc | Pub/Sub |
|--------|----------|---------|
| **Source** | GCP native events | Any publisher |
| **Filtering** | Event attributes | Subscription filter |
| **Targets** | Cloud Run, Workflows | Any subscriber |
| **Use case** | React to GCP events | General messaging |

---

## Summary

### Quick Reference

| Service | Use When | Key Command |
|---------|----------|-------------|
| **Scheduler** | Need cron-like scheduling | `gcloud scheduler jobs create` |
| **Tasks** | Need rate limiting, retries | `gcloud tasks queues create` |
| **Workflows** | Need multi-step orchestration | `gcloud workflows deploy` |
| **Eventarc** | Need to react to GCP events | `gcloud eventarc triggers create` |

### Integration Matrix

| From/To | Scheduler | Tasks | Workflows | Eventarc |
|---------|-----------|-------|-----------|----------|
| **Scheduler** | - | ✅ | ✅ | ❌ |
| **Tasks** | ❌ | - | ✅ | ❌ |
| **Workflows** | ❌ | ✅ | - | ❌ |
| **Eventarc** | ❌ | ❌ | ✅ | - |
