# Google Cloud Run - ACE & PCA Certification Guide

## Table of Contents
1. [Overview](#overview)
2. [Core Concepts](#core-concepts)
3. [Architecture & Components](#architecture--components)
4. [Container Requirements](#container-requirements)
5. [Service Configuration](#service-configuration)
6. [Traffic Management & Revisions](#traffic-management--revisions)
7. [Networking](#networking)
8. [Security & IAM](#security--iam)
9. [Scaling & Performance](#scaling--performance)
10. [Observability & Monitoring](#observability--monitoring)
11. [CI/CD Integration](#cicd-integration)
12. [Cost Optimization](#cost-optimization)
13. [Best Practices](#best-practices)
14. [Common Use Cases](#common-use-cases)
15. [Troubleshooting](#troubleshooting)
16. [Exam Tips](#exam-tips)

---

## Overview

### What is Cloud Run?

**Cloud Run** is a fully managed serverless compute platform that automatically scales stateless containers. It abstracts away infrastructure management and allows you to run containers that respond to web requests or events.

### Key Features

- **Fully Managed**: No infrastructure to manage
- **Serverless**: Automatic scaling to zero
- **Container-Based**: Run any language, library, or binary
- **Pay-per-Use**: Billed only for actual usage (request time)
- **Built on Knative**: Open-source Kubernetes-based platform
- **Fast Autoscaling**: Scale from 0 to N instances in seconds
- **HTTPS Endpoints**: Automatic HTTPS URLs for services

### Cloud Run vs Other Compute Options

| Feature | Cloud Run | App Engine | GKE | Cloud Functions |
|---------|-----------|------------|-----|-----------------|
| **Unit** | Container | Application | Pod/Container | Function |
| **Languages** | Any (containerized) | Specific runtimes | Any | Specific runtimes |
| **Scale to Zero** | Yes | Standard: No, Flex: No | Manual | Yes |
| **Cold Start** | Low | Medium | N/A | Low-Medium |
| **Customization** | Medium | Low | High | Low |
| **Management** | Fully managed | Fully managed | Managed/Self-managed | Fully managed |
| **Pricing Model** | Request-based | Instance hours | Node hours | Invocation-based |

---

## Core Concepts

### Service Types

#### 1. **Cloud Run Services**
- Continuously running services that respond to HTTP requests
- Unique HTTPS endpoint
- Support traffic splitting and gradual rollouts
- Best for: Web apps, APIs, microservices

#### 2. **Cloud Run Jobs**
- Execute tasks that run to completion
- No HTTP endpoint
- Ideal for batch processing, data transformations
- Can be scheduled or triggered
- Best for: ETL jobs, batch processing, scheduled tasks

### Revisions

- **Immutable**: Each deployment creates a new revision
- **Versioning**: Automatic version tracking
- **Rollback**: Easy rollback to previous revisions
- **Traffic Splitting**: Distribute traffic across revisions
- **Naming**: Auto-generated or custom names

### Execution Environment

> **2026 Update**: Generation 2 (Gen2) is now the **default execution environment** for all new Cloud Run services. Gen1 is deprecated and scheduled for removal in Q4 2026.

#### Generation 1 (First Generation - DEPRECATED)
- **Status**: ⚠️ Deprecated since January 2026, removal planned Q4 2026
- Based on gVisor container runtime
- Fast cold starts (~100-200ms)
- Limited CPU availability (only during request processing)
- 32 GB memory limit
- **Migration Required**: All Gen1 services must migrate to Gen2 by Q4 2026

#### Generation 2 (Second Generation - DEFAULT as of 2026)
- **Status**: ✅ Default for all new services since February 2026
- Based on standard Linux container runtime
- Full Linux compatibility (all syscalls supported)
- CPU always allocated (even outside requests) - better for background tasks
- **Enhanced Limits (2026)**:
  - Memory: Up to **32 GB** (increased from 8 GB in 2024)
  - vCPUs: Up to **8 vCPUs** per instance
  - Startup timeout: **600 seconds** (10 minutes)
- **GPU Support (2026)**: ✅ GA for NVIDIA L4 GPUs for AI/ML inference
- Network file systems support (Cloud Storage FUSE, NFS)
- **WebSockets**: Full support for long-lived connections
- **gRPC**: Native support with HTTP/2
- **Startup CPU Boost (2026)**: Automatic 2x CPU during container startup for faster cold starts
- **Multi-container support (2026 Preview)**: Run sidecars (proxies, agents) alongside main container

**Why Gen2 is Now Default:**
- 40% faster request processing for CPU-intensive workloads
- Better compatibility with existing applications (full Linux)
- Support for modern AI/ML inference with GPUs
- Enhanced observability and debugging capabilities

---

## Architecture & Components

### Cloud Run Architecture

```
┌─────────────────────────────────────────────────┐
│                  Client Request                  │
└────────────────────┬────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────┐
│         Cloud Load Balancer (Optional)          │
│              (For Multi-Region)                  │
└────────────────────┬────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────┐
│              Cloud Run Service                   │
│  ┌──────────────────────────────────────────┐  │
│  │           Revision A (80%)               │  │
│  │  ┌──────────┐  ┌──────────┐            │  │
│  │  │Container │  │Container │  ...        │  │
│  │  └──────────┘  └──────────┘            │  │
│  └──────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────┐  │
│  │           Revision B (20%)               │  │
│  │  ┌──────────┐                           │  │
│  │  │Container │                           │  │
│  │  └──────────┘                           │  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│Cloud SQL │  │ Firestore│  │Cloud     │
│          │  │          │  │Storage   │
└──────────┘  └──────────┘  └──────────┘
```

### Request Flow

1. **Request Reception**: HTTPS request hits Cloud Run endpoint
2. **Authentication**: Cloud Run validates authentication (if required)
3. **Scaling Decision**: Determine if new instance needed
4. **Cold Start** (if needed): Start new container instance
5. **Request Routing**: Route to appropriate revision/instance
6. **Request Processing**: Container processes request
7. **Response**: Return response to client
8. **Scale Down**: Idle instances eventually terminated

---

## Container Requirements

### Basic Requirements

1. **HTTP Server**: Must listen on port defined by `PORT` environment variable
   ```dockerfile
   # Example: Listening on $PORT
   CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 app:app
   ```

2. **Stateless**: Containers should be stateless
   - No reliance on local filesystem for persistent data
   - Use external storage (Cloud Storage, Cloud SQL, etc.)

3. **Container Registry**: Image must be in:
   - Artifact Registry (recommended)
   - Container Registry
   - Docker Hub (public images)

4. **Response Time**: Must respond to requests within timeout period (default 5 min, max 60 min)

### Dockerfile Best Practices

```dockerfile
# Use specific versions for reproducibility
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy dependency files first (better caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser /app
USER appuser

# Use environment variable for port
ENV PORT=8080

# Expose port (documentation only)
EXPOSE 8080

# Start application
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
```

### Multi-Stage Builds (Optimization)

```dockerfile
# Build stage
FROM node:18 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

# Production stage
FROM node:18-slim
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY package*.json ./

# Security: non-root user
USER node

# Use PORT environment variable
ENV PORT=8080
EXPOSE 8080

CMD ["node", "dist/server.js"]
```

---

## Service Configuration

### Resource Limits

```yaml
# Example Cloud Run service YAML
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: my-service
spec:
  template:
    metadata:
      annotations:
        # Execution environment
        run.googleapis.com/execution-environment: gen2
        # Scaling settings
        autoscaling.knative.dev/minScale: "0"
        autoscaling.knative.dev/maxScale: "100"
        # Startup CPU boost
        run.googleapis.com/startup-cpu-boost: "true"
    spec:
      # Container timeout (max 3600s)
      timeoutSeconds: 300
      # Service account
      serviceAccountName: my-service-account@project.iam.gserviceaccount.com
      containers:
      - image: gcr.io/project/image:tag
        # Resource allocation
        resources:
          limits:
            cpu: "2"
            memory: "2Gi"
        # Environment variables
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        # Port configuration
        ports:
        - containerPort: 8080
```

### CPU Allocation

#### CPU Always Allocated (Gen2)
```bash
gcloud run deploy SERVICE_NAME \
  --image IMAGE_URL \
  --cpu-throttling \
  --execution-environment=gen2
```

#### CPU Only During Request Processing (Gen1)
```bash
gcloud run deploy SERVICE_NAME \
  --image IMAGE_URL \
  --no-cpu-throttling \
  --execution-environment=gen1
```

### Memory and CPU Options

| CPU | Memory Options |
|-----|----------------|
| 1 | 128Mi - 4Gi |
| 2 | 256Mi - 8Gi |
| 4 | 512Mi - 16Gi |
| 6 | 1Gi - 24Gi |
| 8 | 2Gi - 32Gi |

### Environment Variables

```bash
# Set environment variables
gcloud run deploy SERVICE_NAME \
  --image IMAGE_URL \
  --set-env-vars "ENV=production,DEBUG=false" \
  --set-env-vars "API_KEY=abc123"

# Update environment variables
gcloud run services update SERVICE_NAME \
  --update-env-vars "NEW_VAR=value"

# Remove environment variables
gcloud run services update SERVICE_NAME \
  --remove-env-vars "OLD_VAR"
```

### Secrets Management

```bash
# Mount secret as environment variable
gcloud run deploy SERVICE_NAME \
  --image IMAGE_URL \
  --set-secrets "DATABASE_URL=db-connection-string:latest"

# Mount secret as volume
gcloud run deploy SERVICE_NAME \
  --image IMAGE_URL \
  --set-secrets "/secrets/api-key=api-key-secret:latest"
```

---

## Traffic Management & Revisions

### Revision Management

```bash
# Deploy new revision (automatically gets 100% traffic)
gcloud run deploy SERVICE_NAME \
  --image IMAGE_URL:v2

# Deploy without routing traffic
gcloud run deploy SERVICE_NAME \
  --image IMAGE_URL:v2 \
  --no-traffic

# List revisions
gcloud run revisions list --service SERVICE_NAME
```

### Traffic Splitting

#### Blue/Green Deployment
```bash
# Route all traffic to new revision
gcloud run services update-traffic SERVICE_NAME \
  --to-revisions REVISION_2=100
```

#### Canary Deployment
```bash
# Gradual rollout: 90% old, 10% new
gcloud run services update-traffic SERVICE_NAME \
  --to-revisions REVISION_1=90,REVISION_2=10

# Increase canary traffic: 50/50
gcloud run services update-traffic SERVICE_NAME \
  --to-revisions REVISION_1=50,REVISION_2=50

# Complete rollout: 100% new
gcloud run services update-traffic SERVICE_NAME \
  --to-revisions REVISION_2=100
```

#### Tag-Based Routing

```bash
# Assign tag to revision
gcloud run services update-traffic SERVICE_NAME \
  --update-tags staging=REVISION_NAME

# Access via tagged URL
# https://staging---SERVICE_NAME-PROJECT_ID.REGION.run.app
```

### Rollback Strategy

```bash
# Rollback to previous revision
gcloud run services update-traffic SERVICE_NAME \
  --to-revisions PREVIOUS_REVISION=100

# Rollback using latest tag
gcloud run services update-traffic SERVICE_NAME \
  --to-latest
```

---

## Networking

### Ingress Settings

#### Allow All Traffic (Default)
```bash
gcloud run deploy SERVICE_NAME \
  --image IMAGE_URL \
  --ingress all
```

#### Internal Traffic Only (VPC)
```bash
gcloud run deploy SERVICE_NAME \
  --image IMAGE_URL \
  --ingress internal
```

#### Internal and Cloud Load Balancing
```bash
gcloud run deploy SERVICE_NAME \
  --image IMAGE_URL \
  --ingress internal-and-cloud-load-balancing
```

### VPC Connector (Accessing VPC Resources)

```bash
# Create VPC connector
gcloud compute networks vpc-access connectors create CONNECTOR_NAME \
  --region REGION \
  --network VPC_NETWORK \
  --range 10.8.0.0/28 \
  --min-instances 2 \
  --max-instances 10

# Deploy with VPC connector
gcloud run deploy SERVICE_NAME \
  --image IMAGE_URL \
  --vpc-connector CONNECTOR_NAME \
  --vpc-egress all-traffic
```

### VPC Egress Settings

| Setting | Description | Use Case |
|---------|-------------|----------|
| `all-traffic` | Route all egress through VPC | Access private resources, specific routing |
| `private-ranges-only` | Only private IPs through VPC | Hybrid connectivity, reduce data costs |

### Direct VPC Egress (Serverless VPC Access Alternative)

```bash
# Deploy with Direct VPC egress (Preview)
gcloud run deploy SERVICE_NAME \
  --image IMAGE_URL \
  --network VPC_NETWORK \
  --subnet SUBNET_NAME
```

### Custom Domains

```bash
# Map custom domain
gcloud run domain-mappings create \
  --service SERVICE_NAME \
  --domain api.example.com \
  --region REGION

# Verify domain mapping
gcloud run domain-mappings describe \
  --domain api.example.com \
  --region REGION
```

### Load Balancing (Multi-Region)

#### Setup External Application Load Balancer

```bash
# 1. Create NEG (Network Endpoint Group)
gcloud compute network-endpoint-groups create NEG_NAME \
  --region REGION \
  --network-endpoint-type serverless \
  --cloud-run-service SERVICE_NAME

# 2. Create backend service
gcloud compute backend-services create BACKEND_NAME \
  --global

# 3. Add NEG to backend
gcloud compute backend-services add-backend BACKEND_NAME \
  --global \
  --network-endpoint-group NEG_NAME \
  --network-endpoint-group-region REGION

# 4. Create URL map
gcloud compute url-maps create URL_MAP_NAME \
  --default-service BACKEND_NAME

# 5. Create HTTPS proxy
gcloud compute target-https-proxies create PROXY_NAME \
  --url-map URL_MAP_NAME \
  --ssl-certificates CERT_NAME

# 6. Create forwarding rule
gcloud compute forwarding-rules create RULE_NAME \
  --global \
  --target-https-proxy PROXY_NAME \
  --ports 443
```

---

## Security & IAM

### Authentication & Authorization

#### Public Access (Unauthenticated)
```bash
# Allow unauthenticated access
gcloud run deploy SERVICE_NAME \
  --image IMAGE_URL \
  --allow-unauthenticated

# Or update existing service
gcloud run services add-iam-policy-binding SERVICE_NAME \
  --member="allUsers" \
  --role="roles/run.invoker"
```

#### Private Access (Authenticated)
```bash
# Require authentication
gcloud run deploy SERVICE_NAME \
  --image IMAGE_URL \
  --no-allow-unauthenticated

# Grant specific user access
gcloud run services add-iam-policy-binding SERVICE_NAME \
  --member="user:alice@example.com" \
  --role="roles/run.invoker"

# Grant service account access
gcloud run services add-iam-policy-binding SERVICE_NAME \
  --member="serviceAccount:SA_EMAIL" \
  --role="roles/run.invoker"
```

### IAM Roles

| Role | Description | Use Case |
|------|-------------|----------|
| `roles/run.admin` | Full control over Cloud Run resources | DevOps engineers, admins |
| `roles/run.developer` | Create and update services, cannot set IAM | Developers |
| `roles/run.viewer` | Read-only access to services | Monitoring, auditing |
| `roles/run.invoker` | Invoke services | Service-to-service calls |
| `roles/run.serviceAgent` | Cloud Run service agent | Automatic, GCP-managed |

### Service-to-Service Authentication

#### Using Service Account

```python
import google.auth
from google.auth.transport.requests import AuthorizedSession

# Get default credentials
credentials, project = google.auth.default()

# Create authenticated session
authed_session = AuthorizedSession(credentials)

# Make request to Cloud Run service
response = authed_session.get('https://SERVICE_URL')
```

```bash
# Using gcloud to invoke authenticated service
gcloud run services proxy SERVICE_NAME --port=8080
```

#### Using Identity Token

```bash
# Get identity token
TOKEN=$(gcloud auth print-identity-token)

# Call authenticated service
curl -H "Authorization: Bearer $TOKEN" \
  https://SERVICE_URL
```

### Service Account Best Practices

```bash
# Create dedicated service account
gcloud iam service-accounts create cloud-run-sa \
  --display-name "Cloud Run Service Account"

# Grant minimal permissions
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:cloud-run-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/cloudsql.client"

# Deploy with service account
gcloud run deploy SERVICE_NAME \
  --image IMAGE_URL \
  --service-account cloud-run-sa@PROJECT_ID.iam.gserviceaccount.com
```

### Binary Authorization

```bash
# Enable Binary Authorization
gcloud run deploy SERVICE_NAME \
  --image IMAGE_URL \
  --binary-authorization=default

# Use specific policy
gcloud run deploy SERVICE_NAME \
  --image IMAGE_URL \
  --binary-authorization=POLICY_NAME
```

### Container Security

#### Vulnerability Scanning
```bash
# Enable vulnerability scanning in Artifact Registry
gcloud artifacts repositories create REPO_NAME \
  --repository-format=docker \
  --location=REGION \
  --enable-scanning
```

#### Run as Non-Root User
```dockerfile
# In Dockerfile
RUN useradd -m -u 1000 appuser
USER appuser
```

---

## Scaling & Performance

### Autoscaling Configuration

```bash
# Set minimum instances (prevent cold starts)
gcloud run deploy SERVICE_NAME \
  --image IMAGE_URL \
  --min-instances 1

# Set maximum instances (cost control)
gcloud run deploy SERVICE_NAME \
  --image IMAGE_URL \
  --max-instances 100

# Configure both
gcloud run deploy SERVICE_NAME \
  --image IMAGE_URL \
  --min-instances 2 \
  --max-instances 50
```

### Concurrency

```bash
# Set maximum concurrent requests per instance
gcloud run deploy SERVICE_NAME \
  --image IMAGE_URL \
  --concurrency 80

# Default: 80 (Gen1), 250 (Gen2)
# Maximum: 1000
```

### Cold Start Optimization

#### 1. Minimum Instances
```bash
# Keep 1+ instances warm
gcloud run deploy SERVICE_NAME \
  --image IMAGE_URL \
  --min-instances 3
```

#### 2. Startup CPU Boost
```bash
# Allocate extra CPU during startup
gcloud run deploy SERVICE_NAME \
  --image IMAGE_URL \
  --cpu-boost \
  --execution-environment gen2
```

#### 3. Optimize Container Image
- Use smaller base images (alpine, distroless)
- Multi-stage builds to reduce image size
- Minimize dependencies
- Layer caching optimization

```dockerfile
# Example: Distroless image
FROM gcr.io/distroless/python3
COPY --from=builder /app /app
WORKDIR /app
CMD ["main.py"]
```

#### 4. Application Optimization
- Lazy loading of dependencies
- Reduce startup initialization
- Use connection pooling
- Precompile or cache resources

### Request Timeout

```bash
# Set request timeout (default: 300s, max: 3600s)
gcloud run deploy SERVICE_NAME \
  --image IMAGE_URL \
  --timeout 600
```

### Performance Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| **Cold Start Time** | Time to start container | < 1s (optimized) |
| **Request Latency** | Time to process request | < 100ms (p50) |
| **Instance Utilization** | Concurrent requests/instance | 60-80% of max concurrency |
| **Scale-up Time** | Time to provision new instances | < 10s |

---

## Observability & Monitoring

### Cloud Logging

```bash
# View logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=SERVICE_NAME" \
  --limit 50 \
  --format json

# Filter by severity
gcloud logging read "resource.type=cloud_run_revision AND severity>=ERROR" \
  --limit 20
```

### Structured Logging (Best Practice)

```python
# Python example
import json
import logging
import sys

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    stream=sys.stdout
)

def log_message(message, severity='INFO', **kwargs):
    log_entry = {
        'severity': severity,
        'message': message,
        **kwargs
    }
    print(json.dumps(log_entry))

# Usage
log_message('Request processed', 
            severity='INFO',
            request_id='abc123',
            duration_ms=45)
```

### Cloud Monitoring

#### Key Metrics

```bash
# Create alert policy
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="High Error Rate" \
  --condition-display-name="Error rate > 5%" \
  --condition-threshold-value=0.05 \
  --condition-threshold-duration=300s
```

#### Important Metrics to Monitor

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| `request_count` | Total requests | N/A (trending) |
| `request_latencies` | Request duration | p95 > 1s |
| `container/cpu/utilizations` | CPU usage | > 80% |
| `container/memory/utilizations` | Memory usage | > 85% |
| `container/instance_count` | Active instances | Approaching max |
| `request_count` (5xx) | Server errors | > 1% of total |
| `request_count` (4xx) | Client errors | > 5% of total |

### Cloud Trace

```bash
# Enable Cloud Trace (automatic for Cloud Run)
# View in console or use API

# Python example with OpenTelemetry
from opentelemetry import trace
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Setup
tracer_provider = TracerProvider()
cloud_trace_exporter = CloudTraceSpanExporter()
tracer_provider.add_span_processor(
    BatchSpanProcessor(cloud_trace_exporter)
)
trace.set_tracer_provider(tracer_provider)
```

### Error Reporting

- Automatically enabled for Cloud Run
- Aggregates and displays errors in Cloud Console
- Supports error grouping and notifications

```python
# Python: Report errors to Error Reporting
from google.cloud import error_reporting

client = error_reporting.Client()

try:
    # Your code
    process_request()
except Exception as e:
    client.report_exception()
    raise
```

### Health Checks

```python
# Example health check endpoint
@app.route('/health')
def health_check():
    # Check database connection
    db_healthy = check_database()
    
    # Check external dependencies
    api_healthy = check_external_api()
    
    if db_healthy and api_healthy:
        return {'status': 'healthy'}, 200
    else:
        return {'status': 'unhealthy'}, 503
```

---

## CI/CD Integration

### Cloud Build

#### cloudbuild.yaml Example

```yaml
steps:
  # Build container image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/$_SERVICE_NAME:$COMMIT_SHA', '.']
  
  # Push to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/$_SERVICE_NAME:$COMMIT_SHA']
  
  # Deploy to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - '$_SERVICE_NAME'
      - '--image'
      - 'gcr.io/$PROJECT_ID/$_SERVICE_NAME:$COMMIT_SHA'
      - '--region'
      - '$_REGION'
      - '--platform'
      - 'managed'
      - '--allow-unauthenticated'

images:
  - 'gcr.io/$PROJECT_ID/$_SERVICE_NAME:$COMMIT_SHA'

substitutions:
  _SERVICE_NAME: my-service
  _REGION: us-central1
```

#### Trigger Cloud Build

```bash
# Create trigger from GitHub
gcloud builds triggers create github \
  --repo-name=REPO_NAME \
  --repo-owner=OWNER \
  --branch-pattern="^main$" \
  --build-config=cloudbuild.yaml

# Manual trigger
gcloud builds submit --config cloudbuild.yaml
```

### GitHub Actions

```yaml
name: Deploy to Cloud Run

on:
  push:
    branches:
      - main

env:
  PROJECT_ID: ${{ secrets.GCP_PROJECT_ID }}
  SERVICE_NAME: my-service
  REGION: us-central1

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Authenticate to Google Cloud
      uses: google-github-actions/auth@v1
      with:
        credentials_json: ${{ secrets.GCP_SA_KEY }}
    
    - name: Set up Cloud SDK
      uses: google-github-actions/setup-gcloud@v1
    
    - name: Configure Docker
      run: gcloud auth configure-docker
    
    - name: Build container
      run: |
        docker build -t gcr.io/$PROJECT_ID/$SERVICE_NAME:$GITHUB_SHA .
    
    - name: Push container
      run: |
        docker push gcr.io/$PROJECT_ID/$SERVICE_NAME:$GITHUB_SHA
    
    - name: Deploy to Cloud Run
      run: |
        gcloud run deploy $SERVICE_NAME \
          --image gcr.io/$PROJECT_ID/$SERVICE_NAME:$GITHUB_SHA \
          --region $REGION \
          --platform managed \
          --allow-unauthenticated
```

### GitLab CI/CD

```yaml
# .gitlab-ci.yml
stages:
  - build
  - deploy

variables:
  GCP_PROJECT_ID: "my-project"
  SERVICE_NAME: "my-service"
  REGION: "us-central1"

build:
  stage: build
  image: google/cloud-sdk:alpine
  script:
    - echo $GCP_SERVICE_KEY | base64 -d > ${HOME}/gcp-key.json
    - gcloud auth activate-service-account --key-file ${HOME}/gcp-key.json
    - gcloud config set project $GCP_PROJECT_ID
    - gcloud builds submit --tag gcr.io/$GCP_PROJECT_ID/$SERVICE_NAME:$CI_COMMIT_SHA

deploy:
  stage: deploy
  image: google/cloud-sdk:alpine
  script:
    - echo $GCP_SERVICE_KEY | base64 -d > ${HOME}/gcp-key.json
    - gcloud auth activate-service-account --key-file ${HOME}/gcp-key.json
    - gcloud config set project $GCP_PROJECT_ID
    - gcloud run deploy $SERVICE_NAME
        --image gcr.io/$GCP_PROJECT_ID/$SERVICE_NAME:$CI_COMMIT_SHA
        --region $REGION
        --platform managed
        --allow-unauthenticated
  only:
    - main
```

---

## Cost Optimization

### Pricing Model

Cloud Run charges for:
1. **CPU**: vCPU-seconds (billed to nearest 100ms)
2. **Memory**: GB-seconds (billed to nearest 100ms)
3. **Requests**: Per million requests
4. **Networking**: Egress traffic (ingress free)

### Cost Optimization Strategies

#### 1. Right-Size Resources

```bash
# Monitor actual usage and adjust
gcloud run deploy SERVICE_NAME \
  --image IMAGE_URL \
  --cpu 1 \
  --memory 512Mi
```

#### 2. Optimize Concurrency

```bash
# Higher concurrency = fewer instances
gcloud run deploy SERVICE_NAME \
  --image IMAGE_URL \
  --concurrency 250
```

#### 3. Use CPU Allocation Wisely

```bash
# For Gen1: CPU only during requests (cheaper for request-driven workloads)
gcloud run deploy SERVICE_NAME \
  --image IMAGE_URL \
  --no-cpu-throttling \
  --execution-environment gen1
```

#### 4. Minimize Instance Count

```bash
# Avoid min-instances unless needed for SLA
gcloud run deploy SERVICE_NAME \
  --image IMAGE_URL \
  --min-instances 0 \
  --max-instances 10
```

#### 5. Optimize Request Duration

- Reduce processing time
- Use async processing for long tasks
- Implement request timeout appropriately

#### 6. Network Optimization

- Use VPC connector efficiently
- Minimize external API calls
- Cache responses when possible
- Use Cloud CDN for static content

#### 7. Use Cloud Run Jobs for Batch Processing

```bash
# Jobs are more cost-effective for batch work
gcloud run jobs create JOB_NAME \
  --image IMAGE_URL \
  --task-timeout 3600
```

### Cost Monitoring

```bash
# Export billing data to BigQuery
# Query Cloud Run costs
SELECT
  service.description,
  SUM(cost) as total_cost
FROM
  `project.dataset.gcp_billing_export_v1_XXXXXX`
WHERE
  service.description LIKE '%Cloud Run%'
  AND DATE(usage_start_time) >= '2024-01-01'
GROUP BY
  service.description
ORDER BY
  total_cost DESC
```

### Free Tier (as of 2025)

- **Requests**: 2 million requests/month
- **CPU**: 360,000 vCPU-seconds/month
- **Memory**: 180,000 GiB-seconds/month
- **Networking**: 1 GB egress/month (North America)

---

## Best Practices

### Development Best Practices

1. **Use Environment Variables for Configuration**
   - Never hardcode credentials
   - Use Secret Manager for sensitive data
   - Configure via environment variables

2. **Implement Health Checks**
   ```python
   @app.route('/health')
   def health():
       return {'status': 'ok'}, 200
   ```

3. **Graceful Shutdown**
   ```python
   import signal
   import sys
   
   def signal_handler(sig, frame):
       print('Shutting down gracefully...')
       # Close connections, cleanup
       sys.exit(0)
   
   signal.signal(signal.SIGTERM, signal_handler)
   ```

4. **Use Structured Logging**
   - JSON format for better parsing
   - Include request context
   - Use appropriate severity levels

5. **Optimize Container Size**
   - Use minimal base images
   - Multi-stage builds
   - Remove unnecessary files

### Operational Best Practices

1. **Use Separate Environments**
   ```bash
   # Dev environment
   gcloud run deploy my-service-dev \
     --image IMAGE_URL \
     --region us-central1
   
   # Prod environment
   gcloud run deploy my-service-prod \
     --image IMAGE_URL \
     --region us-central1
   ```

2. **Implement Circuit Breakers**
   - Handle downstream failures gracefully
   - Use retry with exponential backoff
   - Set appropriate timeouts

3. **Use Connection Pooling**
   ```python
   # Example for Cloud SQL
   import sqlalchemy
   
   db = sqlalchemy.create_engine(
       DATABASE_URL,
       pool_size=5,
       max_overflow=2,
       pool_timeout=30,
       pool_recycle=1800
   )
   ```

4. **Tag Revisions for Testing**
   ```bash
   gcloud run services update-traffic SERVICE_NAME \
     --update-tags beta=REVISION_NAME
   ```

5. **Monitor and Alert**
   - Set up error rate alerts
   - Monitor latency percentiles
   - Track cold start frequency
   - Alert on cost anomalies

### Security Best Practices

1. **Principle of Least Privilege**
   - Dedicated service accounts per service
   - Minimal IAM permissions
   - Regular permission audits

2. **Use Private Services When Possible**
   ```bash
   gcloud run deploy SERVICE_NAME \
     --image IMAGE_URL \
     --ingress internal \
     --no-allow-unauthenticated
   ```

3. **Enable Binary Authorization**
   - Enforce image signing
   - Validate image provenance

4. **Regular Security Scanning**
   - Enable vulnerability scanning
   - Review and patch CVEs
   - Update base images regularly

5. **Network Security**
   - Use VPC for private resources
   - Implement Cloud Armor for DDoS protection
   - Use Identity-Aware Proxy for authentication

---

## Common Use Cases

### 1. RESTful API Backend

```python
# app.py
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/api/users', methods=['GET'])
def get_users():
    # Fetch from database
    return jsonify([{'id': 1, 'name': 'Alice'}])

@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.json
    # Save to database
    return jsonify({'id': 2, **data}), 201

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
```

```bash
gcloud run deploy api-service \
  --image gcr.io/project/api:latest \
  --allow-unauthenticated \
  --max-instances 100
```

### 2. Webhook Handler

```python
# webhook.py
from flask import Flask, request
import os

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    payload = request.json
    
    # Process webhook asynchronously
    # Push to Pub/Sub for processing
    publish_to_pubsub(payload)
    
    return '', 204

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
```

### 3. Microservice Architecture

```yaml
# Multiple Cloud Run services
Frontend Service (React/Next.js)
  ↓
API Gateway (Cloud Run)
  ↓
  ├── User Service (Cloud Run)
  ├── Product Service (Cloud Run)
  ├── Order Service (Cloud Run)
  └── Payment Service (Cloud Run)
       ↓
    Third-party API
```

### 4. Scheduled Jobs

```bash
# Create Cloud Run Job
gcloud run jobs create nightly-report \
  --image gcr.io/project/report-generator \
  --task-timeout 3600

# Create Cloud Scheduler job to trigger
gcloud scheduler jobs create http nightly-trigger \
  --schedule "0 2 * * *" \
  --uri "https://REGION-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/PROJECT_ID/jobs/nightly-report:run" \
  --http-method POST \
  --oauth-service-account-email ACCOUNT@PROJECT.iam.gserviceaccount.com
```

### 5. Event-Driven Processing

```bash
# Deploy Cloud Run service for Pub/Sub
gcloud run deploy pubsub-handler \
  --image gcr.io/project/handler \
  --no-allow-unauthenticated

# Create Pub/Sub subscription
gcloud pubsub subscriptions create cloud-run-sub \
  --topic TOPIC_NAME \
  --push-endpoint https://SERVICE_URL \
  --push-auth-service-account SERVICE_ACCOUNT
```

### 6. Static Website with API

```dockerfile
# Multi-purpose container
FROM node:18 AS builder
WORKDIR /app
COPY . .
RUN npm install && npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Cold Start Latency

**Problem**: Service slow to respond after idle period

**Solutions**:
```bash
# Set minimum instances
gcloud run services update SERVICE_NAME \
  --min-instances 1

# Enable startup CPU boost
gcloud run services update SERVICE_NAME \
  --cpu-boost

# Optimize container
# - Reduce image size
# - Lazy load dependencies
# - Use distroless images
```

#### 2. Container Exits Before Ready

**Problem**: Container crashes on startup

**Troubleshooting**:
```bash
# Check logs
gcloud logging read "resource.type=cloud_run_revision" \
  --limit 50 --format json

# Common causes:
# - Not listening on $PORT
# - Startup timeout exceeded
# - Missing dependencies
```

**Solution**:
```dockerfile
# Ensure listening on PORT
ENV PORT=8080
CMD exec gunicorn --bind :$PORT app:app
```

#### 3. 503 Service Unavailable

**Problem**: All instances at max capacity

**Solutions**:
```bash
# Increase max instances
gcloud run services update SERVICE_NAME \
  --max-instances 200

# Increase concurrency
gcloud run services update SERVICE_NAME \
  --concurrency 250

# Add more CPU/memory if bottleneck
gcloud run services update SERVICE_NAME \
  --cpu 2 --memory 2Gi
```

#### 4. High Memory Usage / OOM

**Problem**: Container killed due to memory

**Solutions**:
```bash
# Increase memory allocation
gcloud run services update SERVICE_NAME \
  --memory 2Gi

# Optimize application
# - Fix memory leaks
# - Implement pagination
# - Use streaming for large payloads
```

#### 5. Database Connection Issues

**Problem**: Cannot connect to Cloud SQL

**Solutions**:
```bash
# Ensure Cloud SQL connector configured
gcloud run services update SERVICE_NAME \
  --add-cloudsql-instances PROJECT:REGION:INSTANCE

# Or use VPC connector
gcloud run services update SERVICE_NAME \
  --vpc-connector CONNECTOR_NAME

# Verify service account has cloudsql.client role
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:SA@PROJECT.iam.gserviceaccount.com" \
  --role="roles/cloudsql.client"
```

#### 6. Authentication Errors (403)

**Problem**: Permission denied when calling service

**Solutions**:
```bash
# Check IAM policy
gcloud run services get-iam-policy SERVICE_NAME

# Grant invoker role
gcloud run services add-iam-policy-binding SERVICE_NAME \
  --member="user:EMAIL" \
  --role="roles/run.invoker"

# For service account
gcloud run services add-iam-policy-binding SERVICE_NAME \
  --member="serviceAccount:SA_EMAIL" \
  --role="roles/run.invoker"
```

#### 7. Timeout Errors

**Problem**: Request timeout (504)

**Solutions**:
```bash
# Increase timeout (max 3600s)
gcloud run services update SERVICE_NAME \
  --timeout 900

# For long-running tasks, consider:
# - Cloud Run Jobs
# - Push to Pub/Sub for async processing
# - Cloud Tasks for deferred execution
```

#### 8. VPC Connector Issues

**Problem**: Cannot access resources in VPC

**Solutions**:
```bash
# Verify connector status
gcloud compute networks vpc-access connectors describe CONNECTOR \
  --region REGION

# Check egress settings
gcloud run services update SERVICE_NAME \
  --vpc-egress all-traffic

# Verify firewall rules allow traffic
```

### Debugging Commands

```bash
# Get service details
gcloud run services describe SERVICE_NAME --region REGION

# List all revisions
gcloud run revisions list --service SERVICE_NAME

# Get revision details
gcloud run revisions describe REVISION_NAME

# Stream logs
gcloud logging tail "resource.type=cloud_run_revision" --format=json

# Check metrics
gcloud monitoring time-series list \
  --filter='metric.type="run.googleapis.com/request_count"'
```

---

## Exam Tips

### ACE (Associate Cloud Engineer) Focus Areas

1. **Deployment Basics**
   - Deploy services using gcloud and Console
   - Understand basic configuration (CPU, memory, timeout)
   - Know how to make services public vs private
   - Basic traffic management and rollback

2. **IAM and Security**
   - Roles: run.admin, run.developer, run.invoker
   - Service account assignment
   - Allow/deny unauthenticated access

3. **Integration**
   - Deploy from Container Registry/Artifact Registry
   - Connect to Cloud SQL
   - Use environment variables and secrets
   - Basic Cloud Build integration

4. **Monitoring**
   - View logs in Cloud Logging
   - Basic metrics in Cloud Monitoring
   - Understand error reporting

5. **Key Commands**
   ```bash
   # Deploy
   gcloud run deploy SERVICE --image IMAGE
   
   # Update traffic
   gcloud run services update-traffic SERVICE --to-revisions REV=100
   
   # Grant access
   gcloud run services add-iam-policy-binding SERVICE \
     --member=USER --role=roles/run.invoker
   ```

### PCA (Professional Cloud Architect) Focus Areas

1. **Architecture Design**
   - When to use Cloud Run vs App Engine vs GKE vs Functions
   - Multi-region deployments with Load Balancer
   - Microservices architecture patterns
   - Event-driven architectures with Pub/Sub and Eventarc

2. **Advanced Networking**
   - VPC connectivity options (connector, direct VPC egress)
   - Ingress controls (internal, internal-and-cloud-load-balancing)
   - Custom domain mapping with Cloud Load Balancing
   - Shared VPC and private access patterns

3. **Performance & Scalability**
   - Cold start optimization strategies
   - Concurrency tuning
   - Traffic splitting for canary/blue-green deployments
   - Connection pooling and resource optimization

4. **Security Architecture**
   - Binary Authorization for container security
   - Service mesh integration (Anthos Service Mesh)
   - Identity-Aware Proxy integration
   - Secret management best practices

5. **Cost Optimization**
   - Right-sizing resources
   - CPU allocation strategies (gen1 vs gen2)
   - Min/max instances tradeoffs
   - Alternative architectures for cost reduction

6. **Disaster Recovery**
   - Multi-region failover strategies
   - Backup and restore for stateless services
   - Database connectivity patterns (Cloud SQL, Firestore)
   - Data residency and compliance

7. **Integration Patterns**
   - Service-to-service authentication
   - Pub/Sub push subscriptions
   - Cloud Tasks for asynchronous processing
   - Eventarc for event-driven architectures

### Common Exam Scenarios

#### Scenario 1: High-Traffic API
**Question**: Need to serve millions of requests per day with low latency

**Answer**:
- Cloud Run with high max-instances
- Min-instances to avoid cold starts
- Use Cloud CDN for cacheable responses
- Multi-region with Load Balancer for global availability
- Gen2 execution environment for better performance

#### Scenario 2: Internal Microservices
**Question**: Multiple services that should only communicate internally

**Answer**:
- Deploy with `--ingress internal`
- Use `--no-allow-unauthenticated`
- Service accounts with run.invoker role
- VPC connector for database access
- Shared VPC for network connectivity

#### Scenario 3: Cost Optimization
**Question**: Reduce costs for unpredictable workload

**Answer**:
- Set min-instances to 0 (scale to zero)
- Use appropriate CPU/memory sizing
- Gen1 with CPU-only-during-requests for request-driven workloads
- Optimize concurrency to reduce instance count
- Implement caching to reduce compute

#### Scenario 4: Legacy Application Migration
**Question**: Migrate stateless web app to serverless

**Answer**:
- Containerize application
- Use VPC connector for on-prem database access
- Gradual migration with traffic splitting
- Use Cloud SQL or managed databases
- Implement health checks and graceful shutdown

#### Scenario 5: Batch Processing
**Question**: Run nightly data processing job

**Answer**:
- Use Cloud Run Jobs (not services)
- Trigger with Cloud Scheduler
- Set appropriate task timeout
- Scale with max-instances for parallel processing
- Use Cloud Storage for input/output

### Key Differentiators (Know These Cold)

| Cloud Run | App Engine | Cloud Functions | GKE |
|-----------|------------|-----------------|-----|
| Container-based | Runtime-based | Function-based | Container orchestration |
| Stateless HTTP/Events | Web apps | Event triggers | Any workload |
| Request-based billing | Instance-based | Invocation-based | Node-based |
| Scale to zero | Standard: No | Yes | Manual |
| Full control over container | Limited | Very limited | Full control |
| Knative-compatible | Proprietary | Proprietary | Kubernetes |

### Must-Know Limits

- Max timeout: 60 minutes (3600s)
- Max memory: 32 GB
- Max CPU: 8 vCPU
- Max concurrency: 1000
- Max request size: 32 MB
- Max response size: 32 MB
- Max instances: 1000 (can request increase)

### Common Gotchas

1. **Port Configuration**: Must use `$PORT` environment variable
2. **Stateless Requirement**: No persistent local storage
3. **Cold Starts**: First request after idle can be slow
4. **VPC Access**: Requires VPC connector for private resources
5. **Binary Authorization**: Must be explicitly enabled
6. **Service Accounts**: Need explicit IAM permissions
7. **Regional**: Services are regional, not global
8. **HTTPS Only**: No HTTP-only endpoints

---

## Quick Reference Commands

### Deployment

```bash
# Basic deploy
gcloud run deploy SERVICE --image IMAGE --region REGION

# Deploy with options
gcloud run deploy SERVICE \
  --image IMAGE \
  --region REGION \
  --platform managed \
  --allow-unauthenticated \
  --cpu 2 \
  --memory 2Gi \
  --concurrency 80 \
  --timeout 300 \
  --min-instances 1 \
  --max-instances 100 \
  --set-env-vars "KEY=VALUE" \
  --service-account SA@PROJECT.iam.gserviceaccount.com

# Deploy without traffic
gcloud run deploy SERVICE --image IMAGE --no-traffic
```

### Service Management

```bash
# List services
gcloud run services list

# Describe service
gcloud run services describe SERVICE --region REGION

# Update service
gcloud run services update SERVICE --region REGION --memory 4Gi

# Delete service
gcloud run services delete SERVICE --region REGION
```

### Traffic Management

```bash
# Update traffic split
gcloud run services update-traffic SERVICE \
  --to-revisions REVISION1=80,REVISION2=20

# Tag revision
gcloud run services update-traffic SERVICE \
  --update-tags staging=REVISION

# Route to latest
gcloud run services update-traffic SERVICE --to-latest
```

### IAM

```bash
# Allow unauthenticated
gcloud run services add-iam-policy-binding SERVICE \
  --member="allUsers" \
  --role="roles/run.invoker"

# Grant user access
gcloud run services add-iam-policy-binding SERVICE \
  --member="user:EMAIL" \
  --role="roles/run.invoker"

# Get IAM policy
gcloud run services get-iam-policy SERVICE
```

### Logs & Monitoring

```bash
# View logs
gcloud logging read "resource.type=cloud_run_revision" --limit 50

# Stream logs
gcloud logging tail "resource.type=cloud_run_revision"

# Filter by service
gcloud logging read "resource.labels.service_name=SERVICE" --limit 20
```

---

## Conclusion

Cloud Run is a powerful serverless platform that combines the flexibility of containers with the simplicity of fully managed infrastructure. For both ACE and PCA certifications:

### ACE Focus
- Master basic deployment and configuration
- Understand IAM and access control
- Know how to integrate with other GCP services
- Practice common troubleshooting scenarios

### PCA Focus
- Design multi-region, highly available architectures
- Optimize for performance and cost
- Implement sophisticated security patterns
- Choose appropriate compute options for different scenarios
- Understand advanced networking and integration patterns

### Study Strategy
1. Hands-on practice with sample applications
2. Deploy services using different configuration options
3. Implement traffic splitting and rollback scenarios
4. Practice troubleshooting common issues
5. Understand cost implications of different configurations
6. Review integration with other GCP services

Good luck with your certification! 🚀
