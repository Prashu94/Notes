# Google Cloud Run - Associate Cloud Engineer (ACE) Comprehensive Guide

## Table of Contents
1. [Overview](#overview)
2. [Core Concepts](#core-concepts)
3. [Container Requirements](#container-requirements)
4. [Service Deployment & Configuration](#service-deployment--configuration)
5. [Traffic Management & Revisions](#traffic-management--revisions)
6. [Networking Configuration](#networking-configuration)
7. [Security & IAM](#security--iam)
8. [Environment Variables & Secrets](#environment-variables--secrets)
9. [Cloud SQL Integration](#cloud-sql-integration)
10. [Observability & Monitoring](#observability--monitoring)
11. [CI/CD Integration](#cicd-integration)
12. [Troubleshooting](#troubleshooting)
13. [Best Practices](#best-practices)
14. [ACE Exam Tips](#ace-exam-tips)

---

## Overview

### What is Cloud Run?

**Cloud Run** is a fully managed serverless compute platform that automatically scales stateless containers. It abstracts away infrastructure management, allowing you to deploy containerized applications that respond to HTTP requests or events without managing servers.

### Key Features

- **Fully Managed Serverless**: No infrastructure provisioning or management
- **Container-Based**: Run any language, library, or binary in a container
- **Automatic Scaling**: Scale from 0 to N instances based on traffic
- **Pay-per-Use**: Billed only for actual request processing time (to nearest 100ms)
- **Built on Knative**: Open-source Kubernetes-based platform
- **Fast Deployment**: Deploy new revisions in seconds
- **HTTPS Endpoints**: Automatic HTTPS URLs with managed SSL certificates

### When to Use Cloud Run

**Good Use Cases:**
- Web applications and APIs
- Microservices architectures
- Event-driven processing (with Eventarc)
- Webhooks and callback handlers
- Backend services for mobile/web apps
- Batch processing (Cloud Run Jobs)

**Not Ideal For:**
- Stateful applications requiring persistent connections
- Applications requiring sustained CPU/GPU usage
- WebSocket connections with long durations (15-60 min limit)
- Applications requiring custom kernel modules

### Cloud Run vs Other Compute Options

| Feature | Cloud Run | App Engine | Cloud Functions | GKE |
|---------|-----------|------------|-----------------|-----|
| **Unit** | Container | Application | Function | Pod/Container |
| **Languages** | Any (containerized) | Specific runtimes | Specific runtimes | Any |
| **Scale to Zero** | Yes | Standard: No | Yes | Manual config |
| **Cold Start** | ~500ms | ~1-2s | ~200-500ms | N/A |
| **Max Timeout** | 60 min (3600s) | 60 min | 9 min (540s) | Unlimited |
| **Management** | Fully managed | Fully managed | Fully managed | Managed nodes |
| **Pricing** | Request-based | Instance hours | Invocations | Node hours |
| **Customization** | Medium | Low | Low | High |

---

## Core Concepts

### 1. Services vs Jobs

#### Cloud Run Services
- **Purpose**: Continuously running services that respond to HTTP/HTTPS requests
- **Endpoint**: Unique HTTPS URL provided automatically
- **Scaling**: Automatic based on incoming traffic
- **Use Cases**: Web apps, APIs, microservices, webhooks

```bash
# Deploy a service
gcloud run deploy my-web-app \
  --image gcr.io/my-project/app:latest \
  --region us-central1
```

#### Cloud Run Jobs
- **Purpose**: Execute tasks that run to completion and then stop
- **Endpoint**: No HTTP endpoint
- **Execution**: Manual, scheduled (Cloud Scheduler), or event-driven
- **Use Cases**: Batch processing, ETL, data transformations, scheduled tasks

```bash
# Create a job
gcloud run jobs create my-batch-job \
  --image gcr.io/my-project/job:latest \
  --region us-central1 \
  --task-timeout 3600s

# Execute job
gcloud run jobs execute my-batch-job
```

### 2. Revisions

Every deployment creates a new **revision** - an immutable snapshot of your service configuration:

- **Immutable**: Once created, a revision cannot be changed
- **Auto-Versioned**: Automatically named (e.g., `my-service-00001-abc`)
- **Traffic Splitting**: Route traffic across multiple revisions
- **Rollback**: Instantly revert to previous revisions
- **Retention**: Previous revisions retained for rollback (not billed when not serving traffic)

```bash
# List revisions
gcloud run revisions list --service my-service

# Describe specific revision
gcloud run revisions describe my-service-00005-xyz
```

### 3. Execution Environments

#### Generation 1 (First Generation)
- Based on gVisor container runtime
- CPU available only during request processing
- 32 GB memory limit
- Faster cold starts (~300-500ms)
- **Default for existing services**

#### Generation 2 (Second Generation) - **Recommended**
- Based on standard Linux container runtime
- CPU always allocated (even outside requests)
- Better support for CPU-intensive workloads
- Full Linux compatibility (all syscalls)
- Support for network file systems
- 32 GB memory limit
- GPU support (Preview)
- **Default for new services**

```bash
# Deploy with Gen2
gcloud run deploy my-service \
  --image gcr.io/my-project/app:latest \
  --execution-environment gen2

# Deploy with Gen1
gcloud run deploy my-service \
  --image gcr.io/my-project/app:latest \
  --execution-environment gen1
```

### 4. Request Processing Model

```
Internet → Cloud Run Service → Container Instance
                              → Container Instance
                              → Container Instance
```

- **Container Instance**: Single container running your image
- **Concurrency**: Number of requests one instance can handle simultaneously
- **Autoscaling**: Instances created/destroyed based on request load
- **Scale to Zero**: All instances terminated when no requests (after ~15 min idle)

---

## Container Requirements

### Container Image Requirements

Your container must meet these requirements:

1. **Listen on Port**: Must listen on `$PORT` environment variable (default: 8080)
2. **HTTP Server**: Must respond to HTTP requests
3. **Stateless**: Should not rely on local disk storage (ephemeral)
4. **Fast Startup**: Should start quickly to minimize cold starts
5. **Size Limit**: Container image up to 10 GB (32 GB uncompressed)

### Dockerfile Example (Node.js)

```dockerfile
# Use official Node.js runtime
FROM node:18-slim

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy application code
COPY . .

# Expose port (documentation only)
EXPOSE 8080

# Start application
CMD ["node", "server.js"]
```

**server.js:**
```javascript
const express = require('express');
const app = express();

// Cloud Run sets PORT environment variable
const PORT = process.env.PORT || 8080;

app.get('/', (req, res) => {
  res.send('Hello from Cloud Run!');
});

app.listen(PORT, () => {
  console.log(`Server listening on port ${PORT}`);
});
```

### Dockerfile Example (Python)

```dockerfile
# Use official Python runtime
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (documentation only)
EXPOSE 8080

# Start application with gunicorn
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
```

**main.py:**
```python
from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello from Cloud Run!'

if __name__ == '__main__':
    # Cloud Run sets PORT environment variable
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
```

### Building Container Images

#### Using Cloud Build

```bash
# Build and push to Artifact Registry
gcloud builds submit --tag us-central1-docker.pkg.dev/PROJECT_ID/REPO/IMAGE:TAG

# Build and push to Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/IMAGE:TAG
```

#### Using Docker Locally

```bash
# Build image
docker build -t us-central1-docker.pkg.dev/PROJECT_ID/REPO/IMAGE:TAG .

# Test locally
docker run -p 8080:8080 -e PORT=8080 IMAGE:TAG

# Push to Artifact Registry
gcloud auth configure-docker us-central1-docker.pkg.dev
docker push us-central1-docker.pkg.dev/PROJECT_ID/REPO/IMAGE:TAG
```

### Container Best Practices

1. **Use Slim Base Images**: `alpine`, `slim`, or `distroless` images
2. **Multi-Stage Builds**: Reduce final image size
3. **Layer Caching**: Order Dockerfile commands for better caching
4. **Health Checks**: Implement `/health` or `/ready` endpoints
5. **Graceful Shutdown**: Handle SIGTERM signal for graceful termination

---

## Service Deployment & Configuration

### Basic Deployment

```bash
# Minimal deployment
gcloud run deploy my-service \
  --image gcr.io/PROJECT_ID/IMAGE:TAG \
  --region us-central1

# Interactive deployment (prompts for options)
gcloud run deploy
```

### Comprehensive Deployment

```bash
gcloud run deploy my-service \
  --image us-central1-docker.pkg.dev/PROJECT_ID/REPO/IMAGE:TAG \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --cpu 2 \
  --memory 2Gi \
  --concurrency 80 \
  --timeout 300 \
  --max-instances 100 \
  --min-instances 1 \
  --execution-environment gen2 \
  --service-account SA_NAME@PROJECT_ID.iam.gserviceaccount.com \
  --set-env-vars "ENV=production,DEBUG=false" \
  --set-secrets "API_KEY=my-secret:latest" \
  --ingress all \
  --vpc-connector my-connector \
  --vpc-egress private-ranges-only \
  --no-cpu-throttling
```

### Configuration Options

#### CPU & Memory

```bash
# CPU options: 1, 2, 4, 6, 8
# Memory options: 128Mi, 256Mi, 512Mi, 1Gi, 2Gi, 4Gi, 8Gi, 16Gi, 32Gi

gcloud run deploy my-service \
  --image IMAGE \
  --cpu 2 \
  --memory 4Gi
```

**Relationship:**
- 1 CPU: 128Mi - 4Gi memory
- 2 CPU: 128Mi - 8Gi memory
- 4 CPU: 512Mi - 16Gi memory
- 8 CPU: 2Gi - 32Gi memory

#### Concurrency

Maximum number of requests a single container instance can handle simultaneously:

```bash
# Default: 80 (Gen2), 250 max
gcloud run deploy my-service \
  --image IMAGE \
  --concurrency 100
```

**Guidelines:**
- **CPU-Bound Apps**: Lower concurrency (10-50)
- **I/O-Bound Apps**: Higher concurrency (80-250)
- **Start with defaults**: Adjust based on monitoring

#### Timeout

Maximum time a request can take before being terminated:

```bash
# Default: 300s (5 min), Max: 3600s (60 min)
gcloud run deploy my-service \
  --image IMAGE \
  --timeout 600
```

#### Autoscaling

```bash
# Min instances: 0-1000 (default: 0)
# Max instances: 1-1000 (default: 100)
gcloud run deploy my-service \
  --image IMAGE \
  --min-instances 2 \
  --max-instances 50
```

**Cost Considerations:**
- `min-instances=0`: Scale to zero when idle (cheapest)
- `min-instances>0`: Always-on instances (eliminates cold starts, costs more)

### Deployment Strategies

#### 1. Direct Deployment (Default)

```bash
# New revision receives 100% traffic immediately
gcloud run deploy my-service --image IMAGE:v2
```

#### 2. Gradual Rollout

```bash
# Deploy without traffic
gcloud run deploy my-service \
  --image IMAGE:v2 \
  --no-traffic

# Gradually shift traffic
gcloud run services update-traffic my-service \
  --to-revisions LATEST=10

# After validation, shift remaining traffic
gcloud run services update-traffic my-service \
  --to-revisions LATEST=100
```

#### 3. Blue-Green Deployment

```bash
# Deploy new version (green)
gcloud run deploy my-service \
  --image IMAGE:v2 \
  --no-traffic \
  --tag green

# Test green deployment
curl https://green---my-service-abc123-uc.a.run.app

# Switch traffic instantly
gcloud run services update-traffic my-service \
  --to-tags green=100
```

### Service Management

```bash
# List services
gcloud run services list --region us-central1

# Describe service
gcloud run services describe my-service --region us-central1

# Get service URL
gcloud run services describe my-service --format='value(status.url)'

# Update service configuration
gcloud run services update my-service \
  --region us-central1 \
  --memory 4Gi \
  --max-instances 200

# Delete service
gcloud run services delete my-service --region us-central1
```

---

## Traffic Management & Revisions

### Understanding Revisions

Each deployment creates a new immutable revision:

```bash
# List all revisions
gcloud run revisions list --service my-service --region us-central1

# Output example:
# REVISION                ACTIVE  SERVICE      CREATED              CREATOR
# my-service-00005-abc    yes     my-service   2024-01-15 10:30:00  user@example.com
# my-service-00004-def    no      my-service   2024-01-14 09:15:00  user@example.com
```

### Traffic Splitting

#### Percentage-Based Split

```bash
# Split traffic between revisions
gcloud run services update-traffic my-service \
  --to-revisions my-service-00005-abc=80,my-service-00004-def=20

# Split to latest + previous
gcloud run services update-traffic my-service \
  --to-revisions LATEST=90,my-service-00004-def=10
```

#### Tag-Based Routing

Tags create stable URLs for specific revisions:

```bash
# Assign tags
gcloud run services update-traffic my-service \
  --update-tags staging=my-service-00005-abc,prod=my-service-00004-def

# Tagged URLs created:
# https://staging---my-service-abc123-uc.a.run.app
# https://prod---my-service-abc123-uc.a.run.app

# Route traffic by tags
gcloud run services update-traffic my-service \
  --to-tags prod=100
```

### Rollback Strategies

#### Instant Rollback

```bash
# Route all traffic to previous revision
gcloud run services update-traffic my-service \
  --to-revisions my-service-00004-def=100
```

#### Gradual Rollback

```bash
# Gradually shift traffic back to previous version
gcloud run services update-traffic my-service \
  --to-revisions my-service-00005-abc=50,my-service-00004-def=50

# Complete rollback after verification
gcloud run services update-traffic my-service \
  --to-revisions my-service-00004-def=100
```

### Revision Lifecycle Management

```bash
# Delete old unused revisions
gcloud run revisions delete my-service-00001-xyz --region us-central1

# Delete multiple revisions
for rev in $(gcloud run revisions list --service my-service --format="value(name)" | tail -n +6); do
  gcloud run revisions delete $rev --region us-central1 --quiet
done
```

---

## Networking Configuration

### 1. Ingress Settings

Control where requests can originate:

#### Allow All Traffic (Default)

```bash
# Accept requests from internet
gcloud run deploy my-service \
  --image IMAGE \
  --ingress all
```

#### Internal Only (VPC)

```bash
# Only from VPC network or VPC Service Controls perimeter
gcloud run deploy my-service \
  --image IMAGE \
  --ingress internal
```

#### Internal + Cloud Load Balancing

```bash
# From VPC + Google Cloud Load Balancer
gcloud run deploy my-service \
  --image IMAGE \
  --ingress internal-and-cloud-load-balancing
```

### 2. VPC Access (Serverless VPC Access)

Access resources in your VPC (Cloud SQL, Memorystore, GCE VMs):

#### Create VPC Connector

```bash
# Create connector (one per region)
gcloud compute networks vpc-access connectors create my-connector \
  --region us-central1 \
  --network default \
  --range 10.8.0.0/28 \
  --min-instances 2 \
  --max-instances 10

# List connectors
gcloud compute networks vpc-access connectors list --region us-central1
```

**Connector Requirements:**
- `/28` CIDR block (16 IP addresses)
- Not overlapping with existing subnets
- 2-10 connector instances (autoscales)

#### Attach to Cloud Run Service

```bash
gcloud run deploy my-service \
  --image IMAGE \
  --vpc-connector my-connector \
  --vpc-egress all-traffic
```

#### VPC Egress Options

| Option | Description | Use Case |
|--------|-------------|----------|
| `all-traffic` | Route all egress through VPC | Strict network controls, Cloud NAT |
| `private-ranges-only` | Only private IPs (10.x, 172.x, 192.168.x) through VPC | Hybrid connectivity, cost optimization |

### 3. Direct VPC Egress (Preview)

Newer alternative to Serverless VPC Access:

```bash
gcloud run deploy my-service \
  --image IMAGE \
  --network default \
  --subnet my-subnet
```

**Benefits:**
- Lower latency
- No connector management
- Better scalability

### 4. Custom Domains

#### Map Custom Domain

```bash
# Map domain to service
gcloud run domain-mappings create \
  --service my-service \
  --domain api.example.com \
  --region us-central1

# Get DNS records to configure
gcloud run domain-mappings describe \
  --domain api.example.com \
  --region us-central1
```

**DNS Configuration:**
Add the provided DNS records to your domain:
- Type: `CNAME` or `A`
- Value: `ghs.googlehosted.com.` (Cloud Run managed)

#### Verify Domain Mapping

```bash
# Check status
gcloud run domain-mappings describe \
  --domain api.example.com \
  --region us-central1

# SSL certificate provisioned automatically (Let's Encrypt)
```

### 5. Load Balancing (Multi-Region)

For global load balancing across multiple regions:

#### Create Network Endpoint Groups (NEGs)

```bash
# Create NEG for each region
gcloud compute network-endpoint-groups create my-neg-us \
  --region us-central1 \
  --network-endpoint-type serverless \
  --cloud-run-service my-service

gcloud compute network-endpoint-groups create my-neg-eu \
  --region europe-west1 \
  --network-endpoint-type serverless \
  --cloud-run-service my-service
```

#### Create Backend Service

```bash
# Create backend service
gcloud compute backend-services create my-backend \
  --global \
  --enable-cdn

# Add NEGs to backend
gcloud compute backend-services add-backend my-backend \
  --global \
  --network-endpoint-group my-neg-us \
  --network-endpoint-group-region us-central1

gcloud compute backend-services add-backend my-backend \
  --global \
  --network-endpoint-group my-neg-eu \
  --network-endpoint-group-region europe-west1
```

#### Create URL Map and Forwarding Rule

```bash
# Create URL map
gcloud compute url-maps create my-lb \
  --default-service my-backend

# Create SSL certificate
gcloud compute ssl-certificates create my-cert \
  --domains api.example.com

# Create HTTPS proxy
gcloud compute target-https-proxies create my-https-proxy \
  --url-map my-lb \
  --ssl-certificates my-cert

# Create global forwarding rule
gcloud compute forwarding-rules create my-https-rule \
  --global \
  --target-https-proxy my-https-proxy \
  --ports 443
```

---

## Security & IAM

### Authentication & Authorization

#### Public Access (Unauthenticated)

```bash
# Allow unauthenticated access during deployment
gcloud run deploy my-service \
  --image IMAGE \
  --allow-unauthenticated

# Grant unauthenticated access to existing service
gcloud run services add-iam-policy-binding my-service \
  --region us-central1 \
  --member="allUsers" \
  --role="roles/run.invoker"
```

#### Private Access (Authenticated)

```bash
# Require authentication during deployment
gcloud run deploy my-service \
  --image IMAGE \
  --no-allow-unauthenticated

# Grant specific user access
gcloud run services add-iam-policy-binding my-service \
  --region us-central1 \
  --member="user:alice@example.com" \
  --role="roles/run.invoker"

# Grant service account access
gcloud run services add-iam-policy-binding my-service \
  --region us-central1 \
  --member="serviceAccount:caller@project.iam.gserviceaccount.com" \
  --role="roles/run.invoker"

# Grant to all authenticated users in project
gcloud run services add-iam-policy-binding my-service \
  --region us-central1 \
  --member="allAuthenticatedUsers" \
  --role="roles/run.invoker"
```

### IAM Roles for Cloud Run

| Role | Permissions | Use Case |
|------|-------------|----------|
| `roles/run.admin` | Full control (create, update, delete, IAM) | Platform administrators |
| `roles/run.developer` | Create/update services, cannot set IAM | Application developers |
| `roles/run.viewer` | Read-only access | Monitoring, auditing |
| `roles/run.invoker` | Invoke/call services | Service-to-service communication |
| `roles/run.serviceAgent` | Cloud Run service agent (automatic) | GCP-managed service account |

```bash
# Grant developer role to user
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="user:developer@example.com" \
  --role="roles/run.developer"

# Grant invoker role to service account
gcloud run services add-iam-policy-binding my-service \
  --region us-central1 \
  --member="serviceAccount:caller@project.iam.gserviceaccount.com" \
  --role="roles/run.invoker"
```

### Service-to-Service Authentication

#### Using Service Account Token

**Caller Application (Python):**
```python
import google.auth
from google.auth.transport.requests import AuthorizedSession

# Get default credentials (from service account)
credentials, project = google.auth.default()

# Create authenticated session
authed_session = AuthorizedSession(credentials)

# Call authenticated Cloud Run service
service_url = 'https://my-service-abc123-uc.a.run.app'
response = authed_session.get(service_url)
print(response.text)
```

**Caller Application (Node.js):**
```javascript
const {GoogleAuth} = require('google-auth-library');

async function callService() {
  const auth = new GoogleAuth();
  const client = await auth.getIdTokenClient('https://my-service-abc123-uc.a.run.app');
  
  const response = await client.request({
    url: 'https://my-service-abc123-uc.a.run.app'
  });
  
  console.log(response.data);
}
```

#### Using gcloud for Testing

```bash
# Get identity token
TOKEN=$(gcloud auth print-identity-token)

# Call authenticated service
curl -H "Authorization: Bearer $TOKEN" \
  https://my-service-abc123-uc.a.run.app
```

### Service Account Configuration

#### Default Service Account

Cloud Run uses the default compute service account:
```
PROJECT_NUMBER-compute@developer.gserviceaccount.com
```

**Not recommended for production** (too many permissions).

#### Custom Service Account (Best Practice)

```bash
# Create custom service account
gcloud iam service-accounts create my-service-sa \
  --display-name "My Service SA"

# Grant minimal permissions
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:my-service-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/cloudsql.client"

# Deploy with custom service account
gcloud run deploy my-service \
  --image IMAGE \
  --service-account my-service-sa@PROJECT_ID.iam.gserviceaccount.com
```

### Binary Authorization

Ensure only verified container images are deployed:

```bash
# Enable Binary Authorization
gcloud run services update my-service \
  --binary-authorization=default \
  --region us-central1

# Images must be signed by Cloud Build or Attestor
```

---

## Environment Variables & Secrets

### Environment Variables

#### Set During Deployment

```bash
# Set single variable
gcloud run deploy my-service \
  --image IMAGE \
  --set-env-vars "ENV=production"

# Set multiple variables
gcloud run deploy my-service \
  --image IMAGE \
  --set-env-vars "ENV=production,DEBUG=false,LOG_LEVEL=info"

# Update existing service
gcloud run services update my-service \
  --update-env-vars "API_URL=https://api.example.com"
```

#### Using YAML Configuration

**service.yaml:**
```yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: my-service
spec:
  template:
    spec:
      containers:
      - image: gcr.io/project/image:tag
        env:
        - name: ENV
          value: "production"
        - name: DATABASE_URL
          value: "postgres://host/db"
```

```bash
gcloud run services replace service.yaml
```

### Secrets (Secret Manager)

#### Create Secret

```bash
# Create secret
echo -n "my-api-key-value" | gcloud secrets create my-api-key --data-file=-

# Add secret version
echo -n "new-api-key-value" | gcloud secrets versions add my-api-key --data-file=-
```

#### Grant Access to Service Account

```bash
# Grant Secret Manager Secret Accessor role
gcloud secrets add-iam-policy-binding my-api-key \
  --member="serviceAccount:my-service-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

#### Mount Secret as Environment Variable

```bash
# Mount latest version
gcloud run deploy my-service \
  --image IMAGE \
  --set-secrets "API_KEY=my-api-key:latest"

# Mount specific version
gcloud run deploy my-service \
  --image IMAGE \
  --set-secrets "API_KEY=my-api-key:2"

# Mount multiple secrets
gcloud run deploy my-service \
  --image IMAGE \
  --set-secrets "API_KEY=my-api-key:latest,DB_PASSWORD=db-password:latest"
```

#### Access in Application Code

**Python:**
```python
import os

api_key = os.environ.get('API_KEY')
print(f"Using API key: {api_key[:4]}...")
```

**Node.js:**
```javascript
const apiKey = process.env.API_KEY;
console.log(`Using API key: ${apiKey.substring(0, 4)}...`);
```

#### Mount Secret as Volume (File)

```bash
# Mount secret to /secrets/api-key
gcloud run deploy my-service \
  --image IMAGE \
  --set-secrets "/secrets/api-key=my-api-key:latest"
```

**Access in code:**
```python
# Read from file
with open('/secrets/api-key', 'r') as f:
    api_key = f.read().strip()
```

---

## Cloud SQL Integration

### Setup Cloud SQL Connection

#### 1. Enable Cloud SQL Admin API

```bash
gcloud services enable sqladmin.googleapis.com
```

#### 2. Create Cloud SQL Instance

```bash
gcloud sql instances create my-postgres \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1
```

#### 3. Grant Service Account Access

```bash
# Grant Cloud SQL Client role to service account
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:my-service-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/cloudsql.client"
```

#### 4. Deploy Cloud Run with Cloud SQL Connection

```bash
gcloud run deploy my-service \
  --image IMAGE \
  --add-cloudsql-instances PROJECT_ID:REGION:INSTANCE_NAME \
  --service-account my-service-sa@PROJECT_ID.iam.gserviceaccount.com \
  --set-env-vars "DB_USER=myuser,DB_NAME=mydb" \
  --set-secrets "DB_PASSWORD=db-password:latest"
```

### Connection Patterns

#### Using Unix Socket (Recommended)

**Python (psycopg2):**
```python
import os
import psycopg2

def get_db_connection():
    conn = psycopg2.connect(
        host=f"/cloudsql/{os.environ['INSTANCE_CONNECTION_NAME']}",
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'],
        database=os.environ['DB_NAME']
    )
    return conn

# Environment variables:
# INSTANCE_CONNECTION_NAME=project:region:instance
# DB_USER=myuser
# DB_PASSWORD=mypassword (from Secret Manager)
# DB_NAME=mydb
```

**Node.js (pg):**
```javascript
const { Pool } = require('pg');

const pool = new Pool({
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
  host: `/cloudsql/${process.env.INSTANCE_CONNECTION_NAME}`
});

module.exports = pool;
```

#### Using TCP Connection

```bash
# Enable Private IP on Cloud SQL instance
gcloud sql instances patch my-postgres \
  --network=default \
  --no-assign-ip

# Get private IP
gcloud sql instances describe my-postgres --format="value(ipAddresses[0].ipAddress)"
```

**Python:**
```python
conn = psycopg2.connect(
    host="10.1.2.3",  # Private IP
    port=5432,
    user=os.environ['DB_USER'],
    password=os.environ['DB_PASSWORD'],
    database=os.environ['DB_NAME']
)
```

### Connection Pooling

**Python (SQLAlchemy with connection pooling):**
```python
from sqlalchemy import create_engine
import os

def get_engine():
    db_user = os.environ['DB_USER']
    db_pass = os.environ['DB_PASSWORD']
    db_name = os.environ['DB_NAME']
    instance_conn = os.environ['INSTANCE_CONNECTION_NAME']
    
    db_url = f"postgresql+psycopg2://{db_user}:{db_pass}@/{db_name}?host=/cloudsql/{instance_conn}"
    
    engine = create_engine(
        db_url,
        pool_size=5,           # Max 5 connections in pool
        max_overflow=2,        # Max 2 overflow connections
        pool_timeout=30,       # 30s timeout
        pool_recycle=1800      # Recycle connections after 30 min
    )
    return engine

engine = get_engine()

# Use in application
with engine.connect() as conn:
    result = conn.execute("SELECT * FROM users")
```

---

## Observability & Monitoring

### Cloud Logging

#### View Logs

```bash
# View recent logs
gcloud logging read "resource.type=cloud_run_revision" --limit 50

# Filter by service
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=my-service" --limit 20

# Stream logs (tail -f)
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=my-service"

# Filter by severity
gcloud logging read "resource.type=cloud_run_revision AND severity>=ERROR" --limit 20
```

#### Structured Logging in Application

**Python:**
```python
import json
import sys

def log_message(message, severity='INFO', **kwargs):
    log_entry = {
        'severity': severity,
        'message': message,
        **kwargs
    }
    print(json.dumps(log_entry), file=sys.stderr)

# Usage
log_message("User logged in", user_id="12345", action="login")
log_message("Database error", severity="ERROR", error="Connection timeout")
```

**Node.js:**
```javascript
function log(message, severity = 'INFO', metadata = {}) {
  const logEntry = {
    severity,
    message,
    ...metadata
  };
  console.error(JSON.stringify(logEntry));
}

// Usage
log("User logged in", "INFO", { userId: "12345", action: "login" });
log("Database error", "ERROR", { error: "Connection timeout" });
```

### Cloud Monitoring

#### Key Metrics

| Metric | Description | Threshold |
|--------|-------------|-----------|
| **request_count** | Total requests | Monitor trends |
| **request_latencies** | Request duration | p99 < 1000ms |
| **billable_instance_time** | Container runtime | Cost tracking |
| **instance_count** | Active instances | Capacity planning |
| **container/cpu/utilizations** | CPU usage | < 80% |
| **container/memory/utilizations** | Memory usage | < 80% |

#### Create Alert Policy

```bash
# Using gcloud (complex, use Console for easier setup)
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="High Error Rate" \
  --condition-display-name="Error rate > 5%" \
  --condition-threshold-value=0.05 \
  --condition-threshold-duration=60s
```

**Console (Recommended):**
1. Go to Cloud Monitoring → Alerting
2. Create Policy → Add Condition
3. Select Resource: Cloud Run Revision
4. Metric: `request_count` with filter `response_code_class="5xx"`
5. Set threshold: Rate > 10 per minute
6. Configure notification channels

### Health Checks

Implement health check endpoints:

**Python (Flask):**
```python
@app.route('/health')
def health():
    # Check database connection
    try:
        engine.connect()
        db_status = "ok"
    except Exception as e:
        db_status = "error"
    
    return {
        "status": "healthy" if db_status == "ok" else "unhealthy",
        "database": db_status
    }, 200 if db_status == "ok" else 503

@app.route('/ready')
def ready():
    # Check if service is ready to receive traffic
    return {"status": "ready"}, 200
```

### Tracing with Cloud Trace

Enable automatic trace collection:

**Python:**
```python
from opentelemetry import trace
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Setup
tracer_provider = TracerProvider()
cloud_trace_exporter = CloudTraceSpanExporter()
tracer_provider.add_span_processor(BatchSpanProcessor(cloud_trace_exporter))
trace.set_tracer_provider(tracer_provider)

# Use in code
tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("process_request"):
    # Your code here
    result = process_data()
```

---

## CI/CD Integration

### Cloud Build

#### cloudbuild.yaml

```yaml
steps:
  # Build container image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/$_SERVICE_NAME:$SHORT_SHA', '.']
  
  # Push to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/$_SERVICE_NAME:$SHORT_SHA']
  
  # Deploy to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - '$_SERVICE_NAME'
      - '--image'
      - 'gcr.io/$PROJECT_ID/$_SERVICE_NAME:$SHORT_SHA'
      - '--region'
      - '$_REGION'
      - '--platform'
      - 'managed'
      - '--allow-unauthenticated'

images:
  - 'gcr.io/$PROJECT_ID/$_SERVICE_NAME:$SHORT_SHA'

substitutions:
  _SERVICE_NAME: my-service
  _REGION: us-central1

options:
  logging: CLOUD_LOGGING_ONLY
```

#### Create Build Trigger

```bash
# From GitHub
gcloud builds triggers create github \
  --repo-name=my-repo \
  --repo-owner=my-org \
  --branch-pattern="^main$" \
  --build-config=cloudbuild.yaml \
  --substitutions=_SERVICE_NAME=my-service,_REGION=us-central1

# Manual build
gcloud builds submit --config cloudbuild.yaml
```

### GitHub Actions

**.github/workflows/deploy.yml:**
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
      run: docker build -t gcr.io/$PROJECT_ID/$SERVICE_NAME:$GITHUB_SHA .
    
    - name: Push container
      run: docker push gcr.io/$PROJECT_ID/$SERVICE_NAME:$GITHUB_SHA
    
    - name: Deploy to Cloud Run
      run: |
        gcloud run deploy $SERVICE_NAME \
          --image gcr.io/$PROJECT_ID/$SERVICE_NAME:$GITHUB_SHA \
          --region $REGION \
          --platform managed \
          --allow-unauthenticated \
          --max-instances 100 \
          --memory 1Gi
```

**Setup Secrets in GitHub:**
1. Create service account with Cloud Run Admin role
2. Generate JSON key
3. Add to GitHub Secrets:
   - `GCP_PROJECT_ID`: Your project ID
   - `GCP_SA_KEY`: Service account JSON key (base64 encoded)

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Service Won't Start / Container Crashes

**Symptoms:**
- Deployment fails
- Service restarts continuously
- "Container failed to start" error

**Diagnosis:**
```bash
# View logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=my-service" --limit 50

# Check revision status
gcloud run revisions describe REVISION --region us-central1
```

**Common Causes:**
- **Not listening on $PORT**: Container must listen on port specified by `PORT` environment variable
- **Slow startup**: Container takes too long to start (>4 min timeout)
- **Application crashes**: Error in application code

**Solutions:**
```bash
# Verify port configuration
gcloud run services describe my-service --format="value(spec.template.spec.containers[0].ports[0].containerPort)"

# Increase startup timeout (via Cloud Console)
# Check application logs for errors
```

#### 2. High Latency / Slow Response Times

**Symptoms:**
- Requests taking longer than expected
- Timeout errors (504)
- High p99 latency

**Diagnosis:**
```bash
# Check latency metrics
gcloud monitoring time-series list \
  --filter='metric.type="run.googleapis.com/request_latencies"' \
  --format=json

# View slow requests in logs
gcloud logging read "resource.type=cloud_run_revision AND httpRequest.latency>\"1s\"" --limit 20
```

**Common Causes:**
- **Cold starts**: First request to new instance is slow
- **CPU throttling**: Gen1 only allocates CPU during requests
- **Insufficient resources**: Under-provisioned CPU/memory
- **Database connection delays**: Establishing new connections

**Solutions:**
```bash
# Use Gen2 for CPU-intensive workloads
gcloud run deploy my-service --execution-environment gen2

# Set min instances to avoid cold starts
gcloud run deploy my-service --min-instances 1

# Increase CPU and memory
gcloud run deploy my-service --cpu 2 --memory 2Gi

# Implement connection pooling for databases
```

#### 3. 403 Forbidden Errors

**Symptoms:**
- "Your client does not have permission" error
- 403 status code

**Diagnosis:**
```bash
# Check IAM policy
gcloud run services get-iam-policy my-service --region us-central1
```

**Common Causes:**
- Service requires authentication
- Caller lacks `roles/run.invoker` permission

**Solutions:**
```bash
# Allow unauthenticated access
gcloud run services add-iam-policy-binding my-service \
  --member="allUsers" \
  --role="roles/run.invoker"

# Grant specific user access
gcloud run services add-iam-policy-binding my-service \
  --member="user:caller@example.com" \
  --role="roles/run.invoker"
```

#### 4. Cannot Connect to Cloud SQL

**Symptoms:**
- "Connection refused" or "Connection timeout"
- "Could not connect to database"

**Diagnosis:**
```bash
# Check Cloud SQL connections
gcloud run services describe my-service \
  --format="value(spec.template.metadata.annotations['run.googleapis.com/cloudsql-instances'])"

# Verify service account permissions
gcloud projects get-iam-policy PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:my-service-sa@PROJECT_ID.iam.gserviceaccount.com"
```

**Common Causes:**
- Cloud SQL instance not connected
- Service account lacks Cloud SQL Client role
- Incorrect connection string
- VPC connector not configured (for Private IP)

**Solutions:**
```bash
# Add Cloud SQL connection
gcloud run services update my-service \
  --add-cloudsql-instances PROJECT_ID:REGION:INSTANCE

# Grant Cloud SQL Client role
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:my-service-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/cloudsql.client"

# For Private IP: Add VPC connector
gcloud run services update my-service \
  --vpc-connector my-connector \
  --vpc-egress private-ranges-only
```

#### 5. Out of Memory (OOM) Errors

**Symptoms:**
- Container terminated with exit code 137
- "Memory limit exceeded"

**Diagnosis:**
```bash
# Check memory usage metrics
gcloud monitoring time-series list \
  --filter='metric.type="run.googleapis.com/container/memory/utilizations"' \
  --format=json

# View OOM logs
gcloud logging read "resource.type=cloud_run_revision AND textPayload=~\"Memory\"" --limit 20
```

**Solutions:**
```bash
# Increase memory allocation
gcloud run services update my-service --memory 2Gi

# Optimize application code (memory leaks, caching)
# Reduce concurrency to use less memory per instance
gcloud run services update my-service --concurrency 40
```

#### 6. Too Many Instances / Unexpected Scaling

**Symptoms:**
- More instances than expected
- High costs
- Instance count not scaling down

**Diagnosis:**
```bash
# Check instance count metrics
gcloud monitoring time-series list \
  --filter='metric.type="run.googleapis.com/container/instance_count"' \
  --format=json

# View autoscaling configuration
gcloud run services describe my-service \
  --format="value(spec.template.metadata.annotations['autoscaling.knative.dev/maxScale'])"
```

**Common Causes:**
- High concurrency setting with many requests
- Min instances set too high
- Requests taking too long (creates more instances)

**Solutions:**
```bash
# Set max instances limit
gcloud run services update my-service --max-instances 50

# Optimize request processing time
# Adjust concurrency based on workload
gcloud run services update my-service --concurrency 100

# Set min-instances to 0 if cold starts are acceptable
gcloud run services update my-service --min-instances 0
```

---

## Best Practices

### 1. Container Design

✅ **Do:**
- Use official base images (python:3.11-slim, node:18-slim)
- Implement graceful shutdown (handle SIGTERM)
- Make containers stateless
- Use multi-stage builds to reduce image size
- Cache dependencies in separate layer

❌ **Don't:**
- Store state locally (use databases/Cloud Storage)
- Use latest tag (use specific versions)
- Run as root user
- Include build tools in final image

### 2. Configuration Management

✅ **Do:**
- Use Secret Manager for sensitive data
- Use environment variables for configuration
- Implement health check endpoints
- Version your configuration

❌ **Don't:**
- Hard-code secrets in code or Dockerfile
- Use .env files in production
- Store configuration in container image

### 3. Security

✅ **Do:**
- Use custom service accounts with minimal permissions
- Enable Binary Authorization in production
- Implement authentication for sensitive services
- Use private container registries
- Enable VPC Service Controls for compliance

❌ **Don't:**
- Use default compute service account
- Allow unauthenticated access to sensitive endpoints
- Store credentials in code or logs
- Expose internal services to internet

### 4. Performance Optimization

✅ **Do:**
- Use Gen2 for CPU-intensive workloads
- Implement connection pooling for databases
- Set appropriate concurrency based on workload type
- Use min-instances for latency-sensitive applications
- Enable Cloud CDN for static content

❌ **Don't:**
- Over-provision resources (costs more)
- Under-provision resources (performance issues)
- Use synchronous processing for long tasks
- Create new database connections per request

### 5. Cost Optimization

✅ **Do:**
- Set max-instances to prevent runaway costs
- Use min-instances=0 when cold starts are acceptable
- Right-size CPU and memory based on monitoring
- Optimize request duration
- Use Cloud Run Jobs for batch processing

❌ **Don't:**
- Use min-instances unnecessarily
- Over-allocate resources "just in case"
- Process long-running tasks synchronously
- Ignore monitoring and optimization opportunities

### 6. Monitoring & Observability

✅ **Do:**
- Implement structured logging
- Use Cloud Trace for distributed tracing
- Set up alert policies for critical metrics
- Monitor error rates and latencies
- Log meaningful context (request IDs, user IDs)

❌ **Don't:**
- Log sensitive data (passwords, tokens)
- Over-log (creates noise and costs)
- Ignore error rate spikes
- Skip health check endpoints

### 7. Deployment Strategies

✅ **Do:**
- Use gradual rollouts for risky changes
- Implement blue-green deployments for zero-downtime
- Tag revisions for easy rollback
- Automate deployments with CI/CD
- Test in staging environment first

❌ **Don't:**
- Deploy directly to production without testing
- Delete old revisions immediately
- Skip rollback planning
- Make manual configuration changes

---

## ACE Exam Tips

### Key Concepts to Remember

1. **Cloud Run is serverless and container-based** - scales automatically, no infrastructure management

2. **Revisions are immutable** - each deployment creates new revision, easy rollback

3. **Three ingress settings:**
   - `all`: Internet access (default)
   - `internal`: VPC only
   - `internal-and-cloud-load-balancing`: VPC + Load Balancer

4. **Two execution environments:**
   - Gen1: CPU only during requests, gVisor runtime
   - Gen2: Always-on CPU, better compatibility (recommended)

5. **Authentication patterns:**
   - `--allow-unauthenticated`: Public access
   - `--no-allow-unauthenticated`: Requires IAM role `roles/run.invoker`

6. **VPC Access requires Serverless VPC Access Connector** - create connector in same region

7. **Cloud SQL connection** - use Unix socket `/cloudsql/PROJECT:REGION:INSTANCE`

8. **Container must listen on $PORT** - dynamically assigned by Cloud Run

9. **Secrets via Secret Manager** - `--set-secrets "KEY=secret-name:version"`

10. **Scaling parameters:**
    - `--min-instances`: Always-on instances (costs more, no cold starts)
    - `--max-instances`: Limit maximum scale
    - `--concurrency`: Requests per instance (default 80, max 250)

### Exam Scenarios

#### Scenario 1: Deploy Simple Web Application

**Question:** Deploy a containerized Node.js application to Cloud Run, accessible from internet.

**Solution:**
```bash
gcloud run deploy my-app \
  --image gcr.io/my-project/app:v1 \
  --region us-central1 \
  --allow-unauthenticated
```

#### Scenario 2: Connect to Cloud SQL

**Question:** Cloud Run service needs to connect to Cloud SQL PostgreSQL instance.

**Solution:**
```bash
# 1. Grant Cloud SQL Client role to service account
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:my-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/cloudsql.client"

# 2. Deploy with Cloud SQL connection
gcloud run deploy my-service \
  --image IMAGE \
  --add-cloudsql-instances PROJECT_ID:REGION:INSTANCE \
  --service-account my-sa@PROJECT_ID.iam.gserviceaccount.com
```

#### Scenario 3: Access VPC Resources

**Question:** Cloud Run service needs to access Memorystore Redis instance in VPC.

**Solution:**
```bash
# 1. Create VPC connector
gcloud compute networks vpc-access connectors create my-connector \
  --region us-central1 \
  --network default \
  --range 10.8.0.0/28

# 2. Deploy with VPC connector
gcloud run deploy my-service \
  --image IMAGE \
  --vpc-connector my-connector \
  --vpc-egress private-ranges-only
```

#### Scenario 4: Use Secrets

**Question:** Store database password securely and use in Cloud Run.

**Solution:**
```bash
# 1. Create secret
echo -n "my-db-password" | gcloud secrets create db-password --data-file=-

# 2. Grant access to service account
gcloud secrets add-iam-policy-binding db-password \
  --member="serviceAccount:my-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# 3. Deploy with secret
gcloud run deploy my-service \
  --image IMAGE \
  --set-secrets "DB_PASSWORD=db-password:latest"
```

#### Scenario 5: Gradual Rollout

**Question:** Deploy new version with gradual traffic migration (canary deployment).

**Solution:**
```bash
# 1. Deploy new version without traffic
gcloud run deploy my-service \
  --image IMAGE:v2 \
  --no-traffic

# 2. Shift 10% traffic to new version
gcloud run services update-traffic my-service \
  --to-revisions LATEST=10

# 3. After validation, shift remaining traffic
gcloud run services update-traffic my-service \
  --to-latest
```

#### Scenario 6: Internal-Only Service

**Question:** Deploy service accessible only from within VPC, not from internet.

**Solution:**
```bash
gcloud run deploy my-internal-service \
  --image IMAGE \
  --ingress internal \
  --no-allow-unauthenticated
```

#### Scenario 7: Custom Domain

**Question:** Map custom domain api.example.com to Cloud Run service.

**Solution:**
```bash
# 1. Map domain
gcloud run domain-mappings create \
  --service my-service \
  --domain api.example.com \
  --region us-central1

# 2. Get DNS records
gcloud run domain-mappings describe \
  --domain api.example.com \
  --region us-central1

# 3. Add CNAME record to DNS:
# Name: api.example.com
# Type: CNAME
# Value: ghs.googlehosted.com.
```

#### Scenario 8: Minimize Cold Starts

**Question:** Reduce cold start latency for latency-sensitive API.

**Solution:**
```bash
gcloud run deploy my-api \
  --image IMAGE \
  --min-instances 1 \
  --execution-environment gen2
```

**Note:** `min-instances=1` keeps at least one instance warm (costs more but eliminates cold starts).

### Command Cheat Sheet

```bash
# Deploy service
gcloud run deploy SERVICE --image IMAGE --region REGION

# Update service
gcloud run services update SERVICE --memory 2Gi --region REGION

# List services
gcloud run services list

# Describe service
gcloud run services describe SERVICE --region REGION

# Delete service
gcloud run services delete SERVICE --region REGION

# List revisions
gcloud run revisions list --service SERVICE

# Update traffic
gcloud run services update-traffic SERVICE --to-revisions REV1=80,REV2=20

# Add IAM binding (public)
gcloud run services add-iam-policy-binding SERVICE \
  --member="allUsers" --role="roles/run.invoker"

# View logs
gcloud logging read "resource.type=cloud_run_revision" --limit 50

# Get service URL
gcloud run services describe SERVICE --format='value(status.url)'
```

### Exam Strategy

1. **Identify requirement type:**
   - Public vs private access
   - VPC connectivity needed
   - Database connection required
   - Secret management

2. **Choose appropriate configuration:**
   - Ingress setting based on access pattern
   - VPC connector for private resources
   - Cloud SQL connection for databases
   - Secret Manager for sensitive data

3. **Remember defaults:**
   - Default: Gen2, allow-unauthenticated=false, concurrency=80, min-instances=0

4. **Common gotchas:**
   - Container must listen on $PORT
   - Service account needs Cloud SQL Client role
   - VPC connector required for VPC resources
   - Secret Manager requires secretAccessor role

---

## Quick Reference

### Essential Commands

```bash
# Deploy
gcloud run deploy my-service --image gcr.io/project/image:tag --region us-central1

# Update
gcloud run services update my-service --memory 2Gi

# View URL
gcloud run services describe my-service --format='value(status.url)'

# View logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=my-service" --limit 20

# Scale
gcloud run services update my-service --min-instances 1 --max-instances 100

# Connect Cloud SQL
gcloud run deploy my-service --add-cloudsql-instances project:region:instance

# Add VPC connector
gcloud run deploy my-service --vpc-connector my-connector

# Use secrets
gcloud run deploy my-service --set-secrets "API_KEY=my-secret:latest"

# Traffic split
gcloud run services update-traffic my-service --to-revisions rev1=80,rev2=20
```

---

## Conclusion

Cloud Run provides a powerful serverless platform for deploying containerized applications. For ACE certification:

### Focus Areas:
- Service deployment and configuration
- IAM and authentication patterns
- VPC connectivity and networking
- Cloud SQL integration
- Environment variables and secrets
- Basic troubleshooting
- Monitoring and logging

### Hands-On Practice:
1. Deploy sample applications with different configurations
2. Connect to Cloud SQL and Memorystore
3. Implement traffic splitting and rollback
4. Configure custom domains
5. Use secrets from Secret Manager
6. Set up CI/CD pipelines
7. Practice common troubleshooting scenarios

Good luck with your ACE exam! 🚀
