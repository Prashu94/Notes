# Terraform Guide — Deploy Kit Reference

## Module Structure

Every Terraform configuration follows this layout:

```
terraform/
├── main.tf              # Calls reusable modules
├── variables.tf         # All input variables with descriptions + defaults
├── outputs.tf           # Values exposed to other modules
├── versions.tf          # Required providers and version constraints
├── locals.tf            # Computed values (tags, names)
├── backend.tf.example   # Remote state template — never commit real values
└── environments/
    ├── staging.tfvars
    └── production.tfvars
```

---

## versions.tf Pattern

```hcl
terraform {
  required_version = ">= 1.6"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    # GCP:
    # google = {
    #   source  = "hashicorp/google"
    #   version = "~> 5.0"
    # }
    # Azure:
    # azurerm = {
    #   source  = "hashicorp/azurerm"
    #   version = "~> 3.0"
    # }
  }
}
```

---

## Remote State (backend.tf.example)

```hcl
# Copy to backend.tf and replace placeholders before terraform init
terraform {
  backend "s3" {
    bucket         = "# TODO: your-terraform-state-bucket"
    key            = "{{ module_id }}/{{ environment }}/terraform.tfstate"
    region         = "# TODO: your-region"
    encrypt        = true
    dynamodb_table = "# TODO: terraform-state-lock-table"
  }
}

# GCP equivalent:
# backend "gcs" {
#   bucket = "# TODO: your-state-bucket"
#   prefix = "{{ module_id }}/{{ environment }}"
# }
```

---

## Variable Conventions

```hcl
# variables.tf
variable "environment" {
  description = "Deployment environment (staging | production)"
  type        = string
  validation {
    condition     = contains(["staging", "production"], var.environment)
    error_message = "environment must be staging or production."
  }
}

variable "module_id" {
  description = "Module identifier from aikit config.yaml"
  type        = string
}

variable "db_password" {
  description = "Database master password — provide via TF_VAR_db_password env var"
  type        = string
  sensitive   = true
}
```

---

## locals.tf — Common Tags

```hcl
locals {
  common_tags = {
    Module      = var.module_id
    Environment = var.environment
    ManagedBy   = "terraform"
    Project     = var.project_name
  }

  name_prefix = "${var.module_id}-${var.environment}"
}
```

---

## Resource Patterns by Cloud

### AWS — EKS Node Group

```hcl
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.0"

  cluster_name    = "${local.name_prefix}-eks"
  cluster_version = "1.29"
  vpc_id          = module.vpc.vpc_id
  subnet_ids      = module.vpc.private_subnets

  eks_managed_node_groups = {
    default = {
      min_size       = 1
      max_size       = var.environment == "production" ? 5 : 2
      desired_size   = var.environment == "production" ? 2 : 1
      instance_types = [var.node_instance_type]
    }
  }

  tags = local.common_tags
}
```

### GCP — GKE Cluster

```hcl
resource "google_container_cluster" "main" {
  name     = "${local.name_prefix}-gke"
  location = var.region

  remove_default_node_pool = true
  initial_node_count       = 1
  deletion_protection      = var.environment == "production"

  network    = google_compute_network.main.name
  subnetwork = google_compute_subnetwork.main.name
}

resource "google_container_node_pool" "default" {
  name       = "default-pool"
  cluster    = google_container_cluster.main.id
  node_count = var.environment == "production" ? 2 : 1

  node_config {
    machine_type = var.node_machine_type  # "e2-medium"
    disk_size_gb = 50
    oauth_scopes = ["https://www.googleapis.com/auth/cloud-platform"]
  }
}
```

### Azure — AKS Cluster

```hcl
resource "azurerm_kubernetes_cluster" "main" {
  name                = "${local.name_prefix}-aks"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  dns_prefix          = local.name_prefix

  default_node_pool {
    name       = "default"
    node_count = var.environment == "production" ? 2 : 1
    vm_size    = var.node_vm_size  # "Standard_D2_v2"
  }

  identity {
    type = "SystemAssigned"
  }

  tags = local.common_tags
}
```

---

## Security Best Practices

1. **Never** store secrets in `.tfvars` files committed to git — use environment variables: `TF_VAR_db_password`
2. Enable **encryption at rest** for all storage resources
3. Use **private subnets** for databases and compute; public subnets only for load balancers
4. Apply **least-privilege IAM**: each service gets its own role with only the permissions it needs
5. Enable **CloudTrail / Audit Logging** on all cloud providers
6. Set `deletion_protection = true` in production for databases

---

## Apply Order

```bash
# 1. Initialize
terraform init -backend-config=backend.tf

# 2. Plan (review before applying)
terraform plan -var-file=environments/staging.tfvars -out=tfplan

# 3. Apply
terraform apply tfplan

# 4. Output values needed for Helm/app config
terraform output -json > terraform-outputs.json
```
