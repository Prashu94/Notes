# Google Cloud Build & CI/CD - ACE & PCA Comprehensive Guide

## Table of Contents
1. [Overview](#overview)
2. [Core Concepts](#core-concepts)
3. [Cloud Build Basics](#cloud-build-basics)
4. [Build Configuration](#build-configuration)
5. [Triggers](#triggers)
6. [Artifact Registry](#artifact-registry)
7. [Cloud Deploy](#cloud-deploy)
8. [CI/CD Pipelines](#cicd-pipelines)
9. [Advanced Patterns](#advanced-patterns)
10. [Security](#security)
11. [Best Practices](#best-practices)
12. [Exam Tips](#exam-tips)

---

## Overview

Cloud Build is Google Cloud's fully managed CI/CD platform that executes builds and deployments in a serverless environment.

**Key Services:**
- **Cloud Build:** Build, test, and deploy
- **Artifact Registry:** Store build artifacts (containers, packages)
- **Cloud Deploy:** Continuous delivery pipeline
- **Cloud Source Repositories:** Git repositories
- **Binary Authorization:** Container deployment policy

**Benefits:**
- Serverless (no infrastructure management)
- Fast builds (cached layers, parallel steps)
- Integrated with GCP services
- Pay per minute of build time

---

## Core Concepts

### Build

A Build is a series of build steps executed in sequence.

**Build Lifecycle:**
```
1. Source Code (GitHub, GitLab, Cloud Source Repositories)
    ↓
2. Cloud Build Trigger
    ↓
3. Execute Build Steps
    ↓
4. Store Artifacts (Artifact Registry, Cloud Storage)
    ↓
5. Deploy (Cloud Run, GKE, Compute Engine)
```

### Build Steps

Each step runs in a Docker container and executes a command.

**Example Steps:**
1. Clone repository
2. Install dependencies
3. Run tests
4. Build Docker image
5. Push to Artifact Registry
6. Deploy to Cloud Run

### Builders

Pre-built Docker images used as build steps.

**Common Builders:**
- `gcr.io/cloud-builders/docker` - Docker operations
- `gcr.io/cloud-builders/gcloud` - gcloud commands
- `gcr.io/cloud-builders/kubectl` - Kubernetes operations
- `gcr.io/cloud-builders/npm` - Node.js builds
- `gcr.io/cloud-builders/mvn` - Maven builds
- `gcr.io/cloud-builders/gsutil` - Cloud Storage operations

---

## Cloud Build Basics

### Manual Build

**Build from Source:**
```bash
# Build from local directory
gcloud builds submit --tag gcr.io/PROJECT_ID/my-app

# Build with custom Dockerfile
gcloud builds submit --tag gcr.io/PROJECT_ID/my-app --dockerfile=Dockerfile.prod

# Build from Cloud Storage
gcloud builds submit gs://my-bucket/source.tar.gz --tag gcr.io/PROJECT_ID/my-app
```

**Build from Repository:**
```bash
# Build from GitHub
gcloud builds submit --git=https://github.com/user/repo --tag gcr.io/PROJECT_ID/my-app

# Build from Cloud Source Repositories
gcloud builds submit --git=https://source.developers.google.com/p/PROJECT_ID/r/my-repo
```

### View Build Status

**List Builds:**
```bash
gcloud builds list --limit=10

# Filter by status
gcloud builds list --filter="status=SUCCESS"
gcloud builds list --filter="status=FAILURE"
```

**View Build Details:**
```bash
gcloud builds describe BUILD_ID

# View logs
gcloud builds log BUILD_ID

# Stream logs in real-time
gcloud builds log BUILD_ID --stream
```

---

## Build Configuration

### cloudbuild.yaml

The `cloudbuild.yaml` file defines build steps and configuration.

**Basic Structure:**
```yaml
steps:
  # Build step 1
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/my-app', '.']
  
  # Build step 2
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/my-app']

# Images to push to registry
images:
  - 'gcr.io/$PROJECT_ID/my-app'
```

### Complete Example: Node.js Application

**cloudbuild.yaml:**
```yaml
steps:
  # Step 1: Install dependencies
  - name: 'gcr.io/cloud-builders/npm'
    args: ['install']
  
  # Step 2: Run tests
  - name: 'gcr.io/cloud-builders/npm'
    args: ['test']
  
  # Step 3: Build Docker image
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'build'
      - '-t'
      - 'gcr.io/$PROJECT_ID/my-app:$COMMIT_SHA'
      - '-t'
      - 'gcr.io/$PROJECT_ID/my-app:latest'
      - '.'
  
  # Step 4: Push to Artifact Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/my-app:$COMMIT_SHA']
  
  # Step 5: Deploy to Cloud Run
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'my-app'
      - '--image=gcr.io/$PROJECT_ID/my-app:$COMMIT_SHA'
      - '--region=us-central1'
      - '--platform=managed'

# Images to store
images:
  - 'gcr.io/$PROJECT_ID/my-app:$COMMIT_SHA'
  - 'gcr.io/$PROJECT_ID/my-app:latest'

# Options
options:
  machineType: 'N1_HIGHCPU_8'
  logging: CLOUD_LOGGING_ONLY

# Timeout
timeout: '600s'
```

### Substitution Variables

**Built-in Variables:**
- `$PROJECT_ID` - GCP project ID
- `$BUILD_ID` - Unique build ID
- `$COMMIT_SHA` - Git commit SHA
- `$BRANCH_NAME` - Git branch name
- `$TAG_NAME` - Git tag name
- `$SHORT_SHA` - First 7 chars of commit SHA

**Custom Variables:**
```yaml
substitutions:
  _ENV: 'production'
  _REGION: 'us-central1'
  _SERVICE_NAME: 'my-app'

steps:
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'run'
      - 'deploy'
      - '${_SERVICE_NAME}'
      - '--image=gcr.io/$PROJECT_ID/${_SERVICE_NAME}'
      - '--region=${_REGION}'
```

**Override at Build Time:**
```bash
gcloud builds submit \
  --substitutions=_ENV=staging,_REGION=us-east1
```

### Parallel Steps

**Run steps in parallel:**
```yaml
steps:
  # Run tests in parallel
  - name: 'gcr.io/cloud-builders/npm'
    id: 'unit-tests'
    args: ['run', 'test:unit']
  
  - name: 'gcr.io/cloud-builders/npm'
    id: 'integration-tests'
    args: ['run', 'test:integration']
  
  - name: 'gcr.io/cloud-builders/npm'
    id: 'lint'
    args: ['run', 'lint']
  
  # This step waits for all tests to complete
  - name: 'gcr.io/cloud-builders/docker'
    waitFor: ['unit-tests', 'integration-tests', 'lint']
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/my-app', '.']
```

### Conditional Steps

**Skip steps based on branch:**
```yaml
steps:
  # Always run tests
  - name: 'gcr.io/cloud-builders/npm'
    args: ['test']
  
  # Deploy only on main branch
  - name: 'gcr.io/cloud-builders/gcloud'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        if [ "$BRANCH_NAME" == "main" ]; then
          gcloud run deploy my-app --image gcr.io/$PROJECT_ID/my-app
        else
          echo "Skipping deployment for branch $BRANCH_NAME"
        fi
```

---

## Triggers

### What are Triggers?

Triggers automatically start builds when code changes.

**Trigger Sources:**
- GitHub
- GitLab
- Bitbucket
- Cloud Source Repositories
- Pub/Sub messages
- Manual invocation

### Create Trigger

**Via Console:**
1. **Cloud Build** → **Triggers** → **Create Trigger**
2. **Name:** `deploy-to-production`
3. **Event:**
   - Push to branch
   - Push new tag
   - Pull request
4. **Source:** Select repository
5. **Configuration:** `cloudbuild.yaml`
6. **Create**

**Via gcloud:**
```bash
# Create trigger for GitHub repo
gcloud builds triggers create github \
  --name="deploy-production" \
  --repo-name="my-app" \
  --repo-owner="myusername" \
  --branch-pattern="^main$" \
  --build-config="cloudbuild.yaml"

# Create trigger for Cloud Source Repositories
gcloud builds triggers create cloud-source-repositories \
  --name="deploy-staging" \
  --repo="my-repo" \
  --branch-pattern="^develop$" \
  --build-config="cloudbuild.yaml"

# Create trigger for tags
gcloud builds triggers create github \
  --name="release" \
  --repo-name="my-app" \
  --repo-owner="myusername" \
  --tag-pattern="^v[0-9]+\.[0-9]+\.[0-9]+$" \
  --build-config="cloudbuild.yaml"
```

### Trigger with Filters

**File Path Filters:**
```yaml
# Only trigger if certain files changed
includedFiles:
  - 'src/**'
  - 'package.json'

# Don't trigger for certain files
ignoredFiles:
  - 'README.md'
  - 'docs/**'
  - '**.md'
```

**Branch Filters:**
```bash
# Trigger on main or release/* branches
gcloud builds triggers create github \
  --name="deploy-prod-and-release" \
  --repo-name="my-app" \
  --repo-owner="myusername" \
  --branch-pattern="^(main|release/.*)$" \
  --build-config="cloudbuild.yaml"
```

### Manual Trigger

**Run trigger manually:**
```bash
gcloud builds triggers run TRIGGER_NAME \
  --branch=main

# With custom substitutions
gcloud builds triggers run TRIGGER_NAME \
  --branch=main \
  --substitutions=_ENV=staging
```

---

## Artifact Registry

### What is Artifact Registry?

Universal artifact repository for containers, packages, and language-specific artifacts.

**Supported Formats:**
- **Docker:** Container images
- **Maven:** Java packages
- **npm:** Node.js packages
- **Python:** Python packages (PyPI)
- **APT:** Debian packages
- **YUM:** RPM packages

### Create Repository

**Via Console:**
1. **Artifact Registry** → **Create Repository**
2. **Format:** Docker, Maven, npm, Python
3. **Location:** Region or multi-region
4. **Encryption:** Google-managed or CMEK
5. **Create**

**Via gcloud:**
```bash
# Create Docker repository
gcloud artifacts repositories create my-docker-repo \
  --repository-format=docker \
  --location=us-central1 \
  --description="Docker repository"

# Create npm repository
gcloud artifacts repositories create my-npm-repo \
  --repository-format=npm \
  --location=us-central1
```

### Configure Docker

**Authenticate Docker:**
```bash
# Configure Docker to use Artifact Registry
gcloud auth configure-docker us-central1-docker.pkg.dev
```

### Push Images

**Tag and Push:**
```bash
# Tag image
docker tag my-app us-central1-docker.pkg.dev/PROJECT_ID/my-docker-repo/my-app:v1.0

# Push image
docker push us-central1-docker.pkg.dev/PROJECT_ID/my-docker-repo/my-app:v1.0
```

**Via Cloud Build:**
```yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'build'
      - '-t'
      - 'us-central1-docker.pkg.dev/$PROJECT_ID/my-docker-repo/my-app:$SHORT_SHA'
      - '.'
  
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'push'
      - 'us-central1-docker.pkg.dev/$PROJECT_ID/my-docker-repo/my-app:$SHORT_SHA'

images:
  - 'us-central1-docker.pkg.dev/$PROJECT_ID/my-docker-repo/my-app:$SHORT_SHA'
```

### List Artifacts

**List Repositories:**
```bash
gcloud artifacts repositories list --location=us-central1
```

**List Images:**
```bash
gcloud artifacts docker images list \
  us-central1-docker.pkg.dev/PROJECT_ID/my-docker-repo
```

**List Tags:**
```bash
gcloud artifacts docker tags list \
  us-central1-docker.pkg.dev/PROJECT_ID/my-docker-repo/my-app
```

### Cleanup Policies

**Auto-delete old images:**
```bash
# Keep only last 10 versions
gcloud artifacts repositories set-cleanup-policies my-docker-repo \
  --location=us-central1 \
  --policy='{"name":"keep-latest-10","action":{"type":"Delete"},"condition":{"tagState":"tagged","newerThan":"10"}}'
```

---

## Cloud Deploy

### What is Cloud Deploy?

Managed continuous delivery service for deploying to GKE and Cloud Run.

**Features:**
- Multi-stage delivery (dev → staging → prod)
- Progressive rollouts (canary, blue/green)
- Approval gates
- Rollback support

### Delivery Pipeline

**Create Pipeline:**

**clouddeploy.yaml:**
```yaml
apiVersion: deploy.cloud.google.com/v1
kind: DeliveryPipeline
metadata:
  name: my-app-pipeline
description: Deploy my app to dev, staging, prod
serialPipeline:
  stages:
    - targetId: dev
      profiles: []
    - targetId: staging
      profiles: []
    - targetId: prod
      profiles: []
      strategy:
        canary:
          runtimeConfig:
            cloudRun:
              automaticTrafficControl: true
          canaryDeployment:
            percentages: [25, 50, 75]
            verify: false
---
apiVersion: deploy.cloud.google.com/v1
kind: Target
metadata:
  name: dev
description: Development environment
run:
  location: projects/PROJECT_ID/locations/us-central1
---
apiVersion: deploy.cloud.google.com/v1
kind: Target
metadata:
  name: staging
description: Staging environment
run:
  location: projects/PROJECT_ID/locations/us-central1
requireApproval: false
---
apiVersion: deploy.cloud.google.com/v1
kind: Target
metadata:
  name: prod
description: Production environment
run:
  location: projects/PROJECT_ID/locations/us-central1
requireApproval: true
```

**Apply Pipeline:**
```bash
gcloud deploy apply --file=clouddeploy.yaml --region=us-central1
```

### Create Release

**Trigger Release:**
```bash
gcloud deploy releases create release-001 \
  --delivery-pipeline=my-app-pipeline \
  --region=us-central1 \
  --images=my-app=us-central1-docker.pkg.dev/PROJECT_ID/my-repo/my-app:v1.0
```

### Promote Release

**Promote to Next Stage:**
```bash
# Promote from dev to staging
gcloud deploy releases promote \
  --delivery-pipeline=my-app-pipeline \
  --release=release-001 \
  --region=us-central1

# Approve production deployment
gcloud deploy rollouts approve ROLLOUT_ID \
  --delivery-pipeline=my-app-pipeline \
  --release=release-001 \
  --region=us-central1
```

---

## CI/CD Pipelines

### Complete CI/CD Pipeline

**End-to-End Pipeline:**
```
Code Commit (GitHub)
    ↓
Cloud Build Trigger
    ↓
Build & Test
    ↓
Build Docker Image
    ↓
Push to Artifact Registry
    ↓
Cloud Deploy Release
    ↓
Deploy to Dev
    ↓
Automated Tests
    ↓
Promote to Staging
    ↓
Integration Tests
    ↓
Manual Approval
    ↓
Deploy to Production (Canary)
```

**cloudbuild.yaml (Build & Deploy):**
```yaml
steps:
  # Run tests
  - name: 'gcr.io/cloud-builders/npm'
    args: ['install']
  
  - name: 'gcr.io/cloud-builders/npm'
    args: ['test']
  
  # Build image
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'build'
      - '-t'
      - 'us-central1-docker.pkg.dev/$PROJECT_ID/my-repo/my-app:$SHORT_SHA'
      - '.'
  
  # Push image
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'push'
      - 'us-central1-docker.pkg.dev/$PROJECT_ID/my-repo/my-app:$SHORT_SHA'
  
  # Create Cloud Deploy release
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'deploy'
      - 'releases'
      - 'create'
      - 'release-$SHORT_SHA'
      - '--delivery-pipeline=my-app-pipeline'
      - '--region=us-central1'
      - '--images=my-app=us-central1-docker.pkg.dev/$PROJECT_ID/my-repo/my-app:$SHORT_SHA'

images:
  - 'us-central1-docker.pkg.dev/$PROJECT_ID/my-repo/my-app:$SHORT_SHA'
```

### Multi-Environment Pipeline

**Different Envs with Different Configs:**
```yaml
steps:
  # Build once
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/my-app:$SHORT_SHA', '.']
  
  # Push
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/my-app:$SHORT_SHA']
  
  # Deploy to dev
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'my-app-dev'
      - '--image=gcr.io/$PROJECT_ID/my-app:$SHORT_SHA'
      - '--region=us-central1'
      - '--set-env-vars=ENV=dev,LOG_LEVEL=debug'
  
  # Deploy to staging (only on develop branch)
  - name: 'gcr.io/cloud-builders/gcloud'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        if [ "$BRANCH_NAME" == "develop" ]; then
          gcloud run deploy my-app-staging \
            --image gcr.io/$PROJECT_ID/my-app:$SHORT_SHA \
            --region us-central1 \
            --set-env-vars ENV=staging,LOG_LEVEL=info
        fi
  
  # Deploy to prod (only on main branch)
  - name: 'gcr.io/cloud-builders/gcloud'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        if [ "$BRANCH_NAME" == "main" ]; then
          gcloud run deploy my-app-prod \
            --image gcr.io/$PROJECT_ID/my-app:$SHORT_SHA \
            --region us-central1 \
            --set-env-vars ENV=production,LOG_LEVEL=error
        fi
```

---

## Advanced Patterns

### Build Caching

**Use Kaniko for Layer Caching:**
```yaml
steps:
  - name: 'gcr.io/kaniko-project/executor:latest'
    args:
      - '--destination=gcr.io/$PROJECT_ID/my-app:$SHORT_SHA'
      - '--cache=true'
      - '--cache-ttl=24h'
```

### Secrets Management

**Use Secret Manager:**
```yaml
availableSecrets:
  secretManager:
    - versionName: projects/$PROJECT_ID/secrets/db-password/versions/latest
      env: 'DB_PASSWORD'

steps:
  - name: 'gcr.io/cloud-builders/gcloud'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        echo "DB Password: $$DB_PASSWORD"
    secretEnv: ['DB_PASSWORD']
```

### Build Notifications

**Send Notifications:**
```yaml
# Configure via Console or API
# Notifications go to:
- Cloud Pub/Sub
- Slack (via webhook)
- Email
```

### Custom Builders

**Create Custom Builder:**
```dockerfile
# custom-builder/Dockerfile
FROM golang:1.20
RUN go install github.com/my-tool/cli@latest
ENTRYPOINT ["/go/bin/cli"]
```

**Build and Use:**
```bash
# Build custom builder
cd custom-builder
gcloud builds submit --tag gcr.io/$PROJECT_ID/my-custom-builder

# Use in cloudbuild.yaml
```

```yaml
steps:
  - name: 'gcr.io/$PROJECT_ID/my-custom-builder'
    args: ['do-something']
```

---

## Security

### IAM for Cloud Build

**Service Account:**
```bash
# Create dedicated service account
gcloud iam service-accounts create cloud-build-sa \
  --display-name="Cloud Build Service Account"

# Grant necessary roles
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member=serviceAccount:cloud-build-sa@PROJECT_ID.iam.gserviceaccount.com \
  --role=roles/run.admin

gcloud projects add-iam-policy-binding PROJECT_ID \
  --member=serviceAccount:cloud-build-sa@PROJECT_ID.iam.gserviceaccount.com \
  --role=roles/storage.admin
```

**Use in Build:**
```yaml
options:
  serviceAccount: 'cloud-build-sa@PROJECT_ID.iam.gserviceaccount.com'
```

### Binary Authorization

**Enforce Trusted Images:**
```bash
# Enable Binary Authorization
gcloud services enable binaryauthorization.googleapis.com

# Create policy (require attestation)
cat > policy.yaml <<EOF
admissionWhitelistPatterns:
  - namePattern: gcr.io/PROJECT_ID/*
defaultAdmissionRule:
  requireAttestationsBy:
    - projects/PROJECT_ID/attestors/my-attestor
  enforcementMode: ENFORCED_BLOCK_AND_AUDIT_LOG
EOF

gcloud container binauthz policy import policy.yaml
```

---

## Best Practices

### 1. Use Substitution Variables

**Avoid hardcoding:**
```yaml
# Good
substitutions:
  _REGION: 'us-central1'
  _SERVICE: 'my-app'

steps:
  - name: 'gcr.io/cloud-builders/gcloud'
    args: ['run', 'deploy', '${_SERVICE}', '--region=${_REGION}']

# Bad
steps:
  - name: 'gcr.io/cloud-builders/gcloud'
    args: ['run', 'deploy', 'my-app', '--region=us-central1']
```

### 2. Optimize Build Time

**Parallelize steps:**
- Run tests in parallel
- Use cached layers (Kaniko)
- Use appropriate machine types

### 3. Version Everything

**Tag images with:**
- Git commit SHA
- Semantic version
- Latest (carefully!)

### 4. Use Least Privilege

**Service Account:**
- Create dedicated SA for Cloud Build
- Grant only required permissions
- Avoid project Editor role

### 5. Implement Approval Gates

**Production Deployments:**
- Require manual approval
- Use Cloud Deploy
- Notify stakeholders

---

## Exam Tips

### ACE Exam Focus

**1. Basic Commands:**
```bash
# Submit build
gcloud builds submit --tag gcr.io/PROJECT/APP

# Create trigger
gcloud builds triggers create github --repo-name=REPO --branch-pattern=BRANCH

# List builds
gcloud builds list
```

**2. cloudbuild.yaml:**
- Understand basic structure
- Steps run sequentially
- Each step is a Docker container

**3. Triggers:**
- Automatically start builds
- Sources: GitHub, Cloud Source Repos, Pub/Sub
- Can filter by branch, tag, files

**4. Artifact Registry:**
- Stores Docker images, packages
- Replaces Container Registry (GCR)
- Regional or multi-regional

### PCA Exam Focus

**1. CI/CD Architecture:**

**Choose Cloud Build When:**
- Serverless CI/CD needed
- Integrated with GCP services
- Docker-based builds

 **Alternative:**
- Jenkins on GKE (more control)
- GitLab CI (if using GitLab)

**2. Multi-Stage Pipelines:**
- Dev → Staging → Prod
- Approval gates for prod
- Use Cloud Deploy

**3. Security:**
- Service Account per environment
- Binary Authorization for GKE
- Secret Manager for secrets
- Vulnerability scanning in Artifact Registry

**4. Optimization:**
- Build caching (Kaniko)
- Parallel steps
- Right machine type

### Exam Scenarios

**Scenario:** "Automatically deploy to Cloud Run when code is pushed to main branch"
**Solution:** Create Cloud Build trigger on main branch with Cloud Run deployment step

**Scenario:** "Store built container images securely"
**Solution:** Use Artifact Registry with IAM controls and vulnerability scanning

**Scenario:** "Require manual approval before production deployment"
**Solution:** Use Cloud Deploy with requireApproval on prod target

**Scenario:** "Build Docker images without Docker daemon"
**Solution:** Use Kaniko builder in Cloud Build

---

## Quick Reference

```bash
# Cloud Build
gcloud builds submit --tag gcr.io/PROJECT/APP
gcloud builds list
gcloud builds log BUILD_ID

# Triggers
gcloud builds triggers create github --repo-name=REPO --branch-pattern=BRANCH
gcloud builds triggers run TRIGGER_NAME

# Artifact Registry
gcloud artifacts repositories create REPO --repository-format=docker
gcloud artifacts docker images list REPO_PATH

# Cloud Deploy
gcloud deploy apply --file=clouddeploy.yaml
gcloud deploy releases create RELEASE --delivery-pipeline=PIPELINE
```

---

**End of Guide** - Build and deploy with confidence! 🚀
