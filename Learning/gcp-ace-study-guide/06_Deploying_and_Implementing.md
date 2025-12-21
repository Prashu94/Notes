# 06. Deploying and Implementing (Masterclass Edition)

Implementing cloud solutions involves moving from architecture to execution using Infrastructure as Code (IaC) and automation.

---

## 6.1 Google Cloud Deployment Manager
Google's native, template-driven declarative IaC tool.

### 6.1.1 The Template Hierarchy

| Component | Purpose | Format |
|-----------|---------|--------|
| **Config** | Entry point, defines resources | YAML |
| **Jinja2 Template** | Simple templating | `.jinja` |
| **Python Template** | Complex logic | `.py` |
| **Schema** | Define parameters/validation | `.schema` |

### 6.1.2 Basic Deployment Example

```yaml
# config.yaml
imports:
  - path: vm_template.jinja

resources:
  - name: my-vm
    type: vm_template.jinja
    properties:
      zone: us-central1-a
      machineType: n1-standard-1
      network: default
```

```jinja2
# vm_template.jinja
resources:
- name: {{ env['name'] }}
  type: compute.v1.instance
  properties:
    zone: {{ properties['zone'] }}
    machineType: zones/{{ properties['zone'] }}/machineTypes/{{ properties['machineType'] }}
    disks:
    - boot: true
      autoDelete: true
      initializeParams:
        sourceImage: projects/debian-cloud/global/images/family/debian-11
    networkInterfaces:
    - network: global/networks/{{ properties['network'] }}
      accessConfigs:
      - name: External NAT
        type: ONE_TO_ONE_NAT
```

```bash
# Deploy
gcloud deployment-manager deployments create my-deployment \
    --config=config.yaml

# Update deployment
gcloud deployment-manager deployments update my-deployment \
    --config=config.yaml

# Preview changes before applying
gcloud deployment-manager deployments update my-deployment \
    --config=config.yaml \
    --preview

# Delete deployment (and all resources)
gcloud deployment-manager deployments delete my-deployment
```

### 6.1.3 Advanced Features

#### References and Dependencies

```yaml
resources:
  - name: my-network
    type: compute.v1.network
    properties:
      autoCreateSubnetworks: false
  
  - name: my-subnet
    type: compute.v1.subnetwork
    properties:
      region: us-central1
      network: $(ref.my-network.selfLink)  # Reference to network
      ipCidrRange: 10.0.1.0/24
```

#### Environment Variables

| Variable | Description |
|----------|-------------|
| `env['project']` | Project ID |
| `env['deployment']` | Deployment name |
| `env['name']` | Resource name |
| `env['project_number']` | Project number |
| `env['current_time']` | Timestamp |

#### Schema Files

```yaml
# vm_template.jinja.schema
info:
  title: VM Template
  author: Cloud Team
  version: 1.0

required:
  - zone
  - machineType

properties:
  zone:
    type: string
    description: The zone for the VM
  machineType:
    type: string
    default: n1-standard-1
    description: The machine type
  network:
    type: string
    default: default
```

---

## 6.2 Terraform (Professional Grade)
The most popular multi-cloud IaC tool.

### 6.2.1 Terraform Workflow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  terraform  │ -> │  terraform  │ -> │  terraform  │ -> │  terraform  │
│    init     │    │    plan     │    │    apply    │    │   destroy   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
     │                   │                   │                   │
     v                   v                   v                   v
  Download          Generate           Apply changes       Remove all
  providers         execution          to infrastructure   resources
  & modules         plan
```

### 6.2.2 Basic GCP Configuration

```hcl
# main.tf
terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  
  # Remote backend for team collaboration
  backend "gcs" {
    bucket = "my-tf-state-bucket"
    prefix = "terraform/state"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Create a VPC
resource "google_compute_network" "vpc" {
  name                    = "my-vpc"
  auto_create_subnetworks = false
}

# Create a subnet
resource "google_compute_subnetwork" "subnet" {
  name          = "my-subnet"
  ip_cidr_range = "10.0.1.0/24"
  region        = var.region
  network       = google_compute_network.vpc.id
  
  private_ip_google_access = true
}

# Create a VM
resource "google_compute_instance" "vm" {
  name         = "my-vm"
  machine_type = "e2-medium"
  zone         = "${var.region}-a"

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }

  network_interface {
    subnetwork = google_compute_subnetwork.subnet.id
    access_config {} # Assigns external IP
  }

  service_account {
    email  = google_service_account.vm_sa.email
    scopes = ["cloud-platform"]
  }
}

# Create service account
resource "google_service_account" "vm_sa" {
  account_id   = "vm-service-account"
  display_name = "VM Service Account"
}
```

```hcl
# variables.tf
variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}
```

```hcl
# outputs.tf
output "vm_external_ip" {
  value = google_compute_instance.vm.network_interface[0].access_config[0].nat_ip
}

output "vpc_id" {
  value = google_compute_network.vpc.id
}
```

### 6.2.3 State Management (Critical)

| Backend | Locking | Encryption | Use Case |
|---------|---------|------------|----------|
| **Local** | No | No | Development only |
| **GCS** | Yes (via Firestore) | Yes (Google-managed or CMEK) | Production |
| **Terraform Cloud** | Yes | Yes | Enterprise teams |

```bash
# Initialize with GCS backend
terraform init -backend-config="bucket=my-state-bucket"

# Migrate state to new backend
terraform init -migrate-state

# Import existing resource into state
terraform import google_compute_instance.vm projects/my-project/zones/us-central1-a/instances/my-vm
```

### 6.2.4 Workspaces (Multi-Environment)

```bash
# Create workspaces for environments
terraform workspace new dev
terraform workspace new staging
terraform workspace new prod

# Switch workspace
terraform workspace select prod

# Use workspace in configuration
locals {
  env_config = {
    dev     = { machine_type = "e2-small", min_nodes = 1 }
    staging = { machine_type = "e2-medium", min_nodes = 2 }
    prod    = { machine_type = "e2-standard-4", min_nodes = 3 }
  }
}

resource "google_compute_instance" "vm" {
  machine_type = local.env_config[terraform.workspace].machine_type
  # ...
}
```

### 6.2.5 Modules

```hcl
# Call a module
module "gke_cluster" {
  source = "./modules/gke"
  
  project_id   = var.project_id
  cluster_name = "my-cluster"
  region       = var.region
  node_count   = 3
}

# Use public module from registry
module "vpc" {
  source  = "terraform-google-modules/network/google"
  version = "~> 7.0"

  project_id   = var.project_id
  network_name = "my-vpc"
  
  subnets = [
    {
      subnet_name   = "subnet-01"
      subnet_ip     = "10.0.1.0/24"
      subnet_region = "us-central1"
    }
  ]
}
```

---

## 6.3 Cloud Build (Serverless CI/CD)

### 6.3.1 Cloud Build Architecture

| Component | Description |
|-----------|-------------|
| **Triggers** | Start builds on Git events |
| **Build Steps** | Sequential container executions |
| **Cloud Builders** | Pre-built images for common tasks |
| **Artifacts** | Store outputs (images, packages) |
| **Workers** | Compute for running builds |

### 6.3.2 cloudbuild.yaml Examples

```yaml
# Basic build and push to Artifact Registry
steps:
  # Build the Docker image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', '${_REGION}-docker.pkg.dev/$PROJECT_ID/${_REPO}/${_IMAGE}:$COMMIT_SHA', '.']
  
  # Push to Artifact Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', '${_REGION}-docker.pkg.dev/$PROJECT_ID/${_REPO}/${_IMAGE}:$COMMIT_SHA']
  
  # Deploy to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: 'gcloud'
    args:
      - 'run'
      - 'deploy'
      - '${_SERVICE_NAME}'
      - '--image=${_REGION}-docker.pkg.dev/$PROJECT_ID/${_REPO}/${_IMAGE}:$COMMIT_SHA'
      - '--region=${_REGION}'
      - '--platform=managed'

substitutions:
  _REGION: us-central1
  _REPO: my-repo
  _IMAGE: my-app
  _SERVICE_NAME: my-service

options:
  logging: CLOUD_LOGGING_ONLY
```

```yaml
# Terraform CI/CD pipeline
steps:
  # Terraform init
  - name: 'hashicorp/terraform:1.5'
    entrypoint: 'sh'
    args:
      - '-c'
      - |
        cd infrastructure
        terraform init -backend-config="bucket=$PROJECT_ID-tfstate"

  # Terraform plan
  - name: 'hashicorp/terraform:1.5'
    entrypoint: 'sh'
    args:
      - '-c'
      - |
        cd infrastructure
        terraform plan -out=tfplan

  # Terraform apply (only on main branch)
  - name: 'hashicorp/terraform:1.5'
    entrypoint: 'sh'
    args:
      - '-c'
      - |
        if [ "$BRANCH_NAME" = "main" ]; then
          cd infrastructure
          terraform apply -auto-approve tfplan
        fi
```

### 6.3.3 Substitution Variables

| Variable | Type | Description |
|----------|------|-------------|
| `$PROJECT_ID` | Built-in | Project ID |
| `$BUILD_ID` | Built-in | Build UUID |
| `$COMMIT_SHA` | Built-in | Git commit SHA |
| `$BRANCH_NAME` | Built-in | Git branch |
| `$TAG_NAME` | Built-in | Git tag |
| `$REVISION_ID` | Built-in | Source revision ID |
| `$_CUSTOM_VAR` | User-defined | Your custom variables |

### 6.3.4 Build Triggers

```bash
# Create trigger from GitHub
gcloud builds triggers create github \
    --repo-name=my-repo \
    --repo-owner=my-org \
    --branch-pattern="^main$" \
    --build-config=cloudbuild.yaml

# Create trigger with substitutions
gcloud builds triggers create github \
    --repo-name=my-repo \
    --repo-owner=my-org \
    --tag-pattern="^v.*" \
    --build-config=cloudbuild.yaml \
    --substitutions=_DEPLOY_ENV=prod

# Manual trigger
gcloud builds submit --config=cloudbuild.yaml .
```

### 6.3.5 Private Pools

For accessing private resources (Private GKE, internal VMs).

```bash
# Create private pool
gcloud builds worker-pools create my-private-pool \
    --region=us-central1 \
    --peered-network=projects/my-project/global/networks/my-vpc \
    --peered-network-ip-range=192.168.0.0/24

# Use private pool in cloudbuild.yaml
options:
  pool:
    name: 'projects/my-project/locations/us-central1/workerPools/my-private-pool'
```

### 6.3.6 Service Account Permissions

| Task | Required Role |
|------|---------------|
| Push to Artifact Registry | `roles/artifactregistry.writer` |
| Deploy to Cloud Run | `roles/run.admin` |
| Deploy to GKE | `roles/container.developer` |
| Access Secret Manager | `roles/secretmanager.secretAccessor` |
| Use Private Pool | Network connectivity |

```bash
# Grant Cloud Build SA necessary permissions
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com" \
    --role="roles/run.admin"
```

---

## 6.4 Artifact Registry (Container & Package Management)

Successor to Container Registry. Stores Docker images, Maven, npm, Python packages.

```bash
# Create Docker repository
gcloud artifacts repositories create my-repo \
    --repository-format=docker \
    --location=us-central1 \
    --description="Docker repository"

# Configure Docker to use Artifact Registry
gcloud auth configure-docker us-central1-docker.pkg.dev

# Build and push image
docker build -t us-central1-docker.pkg.dev/my-project/my-repo/my-app:v1 .
docker push us-central1-docker.pkg.dev/my-project/my-repo/my-app:v1

# List images
gcloud artifacts docker images list us-central1-docker.pkg.dev/my-project/my-repo

# Create cleanup policy (delete images older than 90 days)
gcloud artifacts repositories set-cleanup-policies my-repo \
    --location=us-central1 \
    --policy=cleanup-policy.json
```

---

## 6.5 Cloud Marketplace (Click-to-Deploy)

| Feature | Description |
|---------|-------------|
| **Mechanism** | Uses Deployment Manager under the hood |
| **Use Case** | 3rd party software (MongoDB, Jenkins, WordPress) |
| **Pricing** | Infrastructure + Software license fee (if any) |
| **Support** | Varies by vendor |

---

## 6.6 Complete CI/CD Pipeline Example

```yaml
# cloudbuild.yaml - Full pipeline
steps:
  # 1. Run tests
  - name: 'python:3.11'
    entrypoint: 'pip'
    args: ['install', '-r', 'requirements.txt']
  
  - name: 'python:3.11'
    entrypoint: 'pytest'
    args: ['tests/', '-v']

  # 2. Security scan
  - name: 'gcr.io/cloud-builders/gcloud'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        gcloud artifacts docker images scan \
          ${_REGION}-docker.pkg.dev/$PROJECT_ID/${_REPO}/${_IMAGE}:$COMMIT_SHA \
          --format='value(response.scan)'

  # 3. Build container
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', '${_REGION}-docker.pkg.dev/$PROJECT_ID/${_REPO}/${_IMAGE}:$COMMIT_SHA', '.']

  # 4. Push to Artifact Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', '${_REGION}-docker.pkg.dev/$PROJECT_ID/${_REPO}/${_IMAGE}:$COMMIT_SHA']

  # 5. Deploy to staging (Cloud Run)
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: 'gcloud'
    args:
      - 'run'
      - 'deploy'
      - '${_SERVICE_NAME}-staging'
      - '--image=${_REGION}-docker.pkg.dev/$PROJECT_ID/${_REPO}/${_IMAGE}:$COMMIT_SHA'
      - '--region=${_REGION}'
      - '--no-traffic'
      - '--tag=canary'

  # 6. Run integration tests against staging
  - name: 'gcr.io/cloud-builders/curl'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        STAGING_URL=$(gcloud run services describe ${_SERVICE_NAME}-staging \
          --region=${_REGION} --format='value(status.url)')
        curl -f "$STAGING_URL/health" || exit 1

  # 7. Promote to production (main branch only)
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        if [ "$BRANCH_NAME" = "main" ]; then
          gcloud run deploy ${_SERVICE_NAME} \
            --image=${_REGION}-docker.pkg.dev/$PROJECT_ID/${_REPO}/${_IMAGE}:$COMMIT_SHA \
            --region=${_REGION}
        fi

substitutions:
  _REGION: us-central1
  _REPO: my-repo
  _IMAGE: my-app
  _SERVICE_NAME: my-service

options:
  logging: CLOUD_LOGGING_ONLY

images:
  - '${_REGION}-docker.pkg.dev/$PROJECT_ID/${_REPO}/${_IMAGE}:$COMMIT_SHA'
```

### Pipeline Visualization

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Git Push   │ -> │   Trigger    │ -> │  Run Tests   │
│  (main/PR)   │    │ Cloud Build  │    │   (pytest)   │
└──────────────┘    └──────────────┘    └──────┬───────┘
                                               │
                                               v
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Deploy     │ <- │    Push      │ <- │    Build     │
│   Staging    │    │   Image      │    │   Docker     │
└──────┬───────┘    └──────────────┘    └──────────────┘
       │
       v
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Integration │ -> │   Promote    │ -> │   Traffic    │
│    Tests     │    │  to Prod     │    │   Switch     │
└──────────────┘    └──────────────┘    └──────────────┘
```

---

## 6.7 IaC Tool Comparison

| Feature | Deployment Manager | Terraform | Pulumi |
|---------|-------------------|-----------|--------|
| **Language** | YAML/Jinja/Python | HCL | TypeScript/Python/Go |
| **Multi-Cloud** | ❌ GCP only | ✅ All clouds | ✅ All clouds |
| **State** | Google-managed | Self-managed (GCS) | Pulumi Cloud or self |
| **Community** | Limited | Large | Growing |
| **Preview** | `--preview` | `terraform plan` | `pulumi preview` |
| **Best For** | Native GCP | Multi-cloud teams | Developers (code-first) |
