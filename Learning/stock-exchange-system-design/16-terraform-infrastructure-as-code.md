# Infrastructure as Code - Terraform for AWS EKS & Spring Boot

## Overview

This guide provides complete Terraform configurations for deploying Spring Boot microservices on AWS EKS, including VPC, RDS, ElastiCache, MSK, and all supporting infrastructure.

## Project Structure

```
terraform/
├── main.tf                      # Main configuration
├── variables.tf                 # Input variables
├── outputs.tf                   # Output values
├── versions.tf                  # Provider versions
├── modules/
│   ├── vpc/                     # VPC module
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── eks/                     # EKS cluster module
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── rds/                     # RDS PostgreSQL module
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── elasticache/             # ElastiCache Redis module
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── msk/                     # Amazon MSK module
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
├── environments/
│   ├── dev/
│   │   └── terraform.tfvars
│   ├── staging/
│   │   └── terraform.tfvars
│   └── prod/
│       └── terraform.tfvars
└── kubernetes/
    ├── order-service/
    │   ├── deployment.yaml
    │   ├── service.yaml
    │   ├── hpa.yaml
    │   └── ingress.yaml
    └── trade-service/
        ├── deployment.yaml
        ├── service.yaml
        ├── hpa.yaml
        └── ingress.yaml
```

## Main Terraform Configuration

### versions.tf

```hcl
terraform {
  required_version = ">= 1.6.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.11"
    }
  }
  
  backend "s3" {
    bucket         = "trading-platform-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
    kms_key_id     = "arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012"
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Environment = var.environment
      Project     = "trading-platform"
      ManagedBy   = "terraform"
      CostCenter  = "trading"
    }
  }
}

provider "kubernetes" {
  host                   = module.eks.cluster_endpoint
  cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
  
  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    args = [
      "eks",
      "get-token",
      "--cluster-name",
      module.eks.cluster_name
    ]
  }
}

provider "helm" {
  kubernetes {
    host                   = module.eks.cluster_endpoint
    cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
    
    exec {
      api_version = "client.authentication.k8s.io/v1beta1"
      command     = "aws"
      args = [
        "eks",
        "get-token",
        "--cluster-name",
        module.eks.cluster_name
      ]
    }
  }
}
```

### main.tf

```hcl
# Data sources
data "aws_caller_identity" "current" {}
data "aws_availability_zones" "available" {
  state = "available"
}

locals {
  cluster_name = "${var.environment}-trading-cluster"
  common_tags = {
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "terraform"
  }
}

# VPC Module
module "vpc" {
  source = "./modules/vpc"
  
  environment         = var.environment
  vpc_cidr            = var.vpc_cidr
  availability_zones  = slice(data.aws_availability_zones.available.names, 0, 3)
  
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_app_cidrs    = var.private_app_subnet_cidrs
  private_data_cidrs   = var.private_data_subnet_cidrs
  
  enable_nat_gateway   = true
  single_nat_gateway   = var.environment != "prod"
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = local.common_tags
}

# EKS Cluster Module
module "eks" {
  source = "./modules/eks"
  
  cluster_name    = local.cluster_name
  cluster_version = var.eks_cluster_version
  
  vpc_id          = module.vpc.vpc_id
  subnet_ids      = module.vpc.private_app_subnet_ids
  
  cluster_endpoint_private_access = true
  cluster_endpoint_public_access  = var.environment == "dev"
  
  cluster_addons = {
    coredns = {
      most_recent = true
    }
    kube-proxy = {
      most_recent = true
    }
    vpc-cni = {
      most_recent = true
    }
    aws-ebs-csi-driver = {
      most_recent = true
    }
  }
  
  # Node groups
  node_groups = {
    trading_services = {
      name           = "trading-services-ng"
      instance_types = ["c6i.4xlarge"]
      capacity_type  = "ON_DEMAND"
      
      min_size     = 3
      max_size     = 20
      desired_size = 5
      
      labels = {
        workload    = "trading"
        criticality = "high"
      }
      
      taints = [{
        key    = "trading"
        value  = "true"
        effect = "NO_SCHEDULE"
      }]
      
      tags = merge(local.common_tags, {
        "k8s.io/cluster-autoscaler/enabled"               = "true"
        "k8s.io/cluster-autoscaler/${local.cluster_name}" = "owned"
      })
    }
    
    support_services = {
      name           = "support-services-ng"
      instance_types = ["m6i.2xlarge"]
      capacity_type  = "ON_DEMAND"
      
      min_size     = 2
      max_size     = 10
      desired_size = 3
      
      labels = {
        workload    = "support"
        criticality = "medium"
      }
      
      tags = merge(local.common_tags, {
        "k8s.io/cluster-autoscaler/enabled"               = "true"
        "k8s.io/cluster-autoscaler/${local.cluster_name}" = "owned"
      })
    }
    
    market_data = {
      name           = "market-data-ng"
      instance_types = ["c6gn.4xlarge"]
      capacity_type  = "ON_DEMAND"
      
      min_size     = 2
      max_size     = 15
      desired_size = 3
      
      labels = {
        workload    = "market-data"
        criticality = "high"
        network     = "enhanced"
      }
      
      taints = [{
        key    = "market-data"
        value  = "true"
        effect = "NO_SCHEDULE"
      }]
      
      tags = merge(local.common_tags, {
        "k8s.io/cluster-autoscaler/enabled"               = "true"
        "k8s.io/cluster-autoscaler/${local.cluster_name}" = "owned"
      })
    }
  }
  
  tags = local.common_tags
}

# RDS PostgreSQL Module
module "rds" {
  source = "./modules/rds"
  
  identifier        = "${var.environment}-trading-db"
  engine_version    = "15.4"
  instance_class    = var.rds_instance_class
  allocated_storage = var.rds_allocated_storage
  storage_type      = "io2"
  iops              = var.rds_iops
  
  db_name  = "trading"
  username = "postgres"
  port     = 5432
  
  multi_az               = var.environment == "prod"
  db_subnet_group_name   = module.vpc.database_subnet_group_name
  vpc_security_group_ids = [module.rds_security_group.security_group_id]
  
  backup_retention_period = var.environment == "prod" ? 35 : 7
  backup_window           = "03:00-04:00"
  maintenance_window      = "sun:04:00-sun:05:00"
  
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
  
  performance_insights_enabled    = true
  performance_insights_kms_key_id = aws_kms_key.rds.arn
  
  deletion_protection = var.environment == "prod"
  skip_final_snapshot = var.environment != "prod"
  
  tags = local.common_tags
}

# ElastiCache Redis Module
module "elasticache" {
  source = "./modules/elasticache"
  
  cluster_id           = "${var.environment}-trading-cache"
  engine_version       = "7.0"
  node_type            = var.elasticache_node_type
  num_cache_clusters   = var.elasticache_num_nodes
  
  parameter_group_name = aws_elasticache_parameter_group.redis.name
  subnet_group_name    = module.vpc.elasticache_subnet_group_name
  security_group_ids   = [module.elasticache_security_group.security_group_id]
  
  automatic_failover_enabled = true
  multi_az_enabled           = var.environment == "prod"
  
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  auth_token_enabled         = true
  
  maintenance_window         = "sun:05:00-sun:06:00"
  snapshot_retention_limit   = var.environment == "prod" ? 7 : 1
  snapshot_window            = "04:00-05:00"
  
  tags = local.common_tags
}

# Amazon MSK (Kafka) Module
module "msk" {
  source = "./modules/msk"
  
  cluster_name    = "${var.environment}-trading-kafka"
  kafka_version   = "3.5.1"
  number_of_nodes = 9  # 3 per AZ
  
  broker_node_group_info = {
    instance_type   = var.msk_instance_type
    client_subnets  = module.vpc.private_data_subnet_ids
    security_groups = [module.msk_security_group.security_group_id]
    
    storage_info = {
      ebs_storage_info = {
        volume_size = var.msk_volume_size
        provisioned_throughput = {
          enabled           = true
          volume_throughput = 250
        }
      }
    }
  }
  
  encryption_info = {
    encryption_at_rest_kms_key_arn = aws_kms_key.msk.arn
    encryption_in_transit = {
      client_broker = "TLS"
      in_cluster    = true
    }
  }
  
  client_authentication = {
    sasl = {
      iam   = true
      scram = true
    }
  }
  
  configuration_info = {
    arn      = aws_msk_configuration.kafka_config.arn
    revision = aws_msk_configuration.kafka_config.latest_revision
  }
  
  logging_info = {
    broker_logs = {
      cloudwatch_logs = {
        enabled   = true
        log_group = aws_cloudwatch_log_group.msk.name
      }
      s3 = {
        enabled = true
        bucket  = aws_s3_bucket.msk_logs.id
        prefix  = "kafka-logs/"
      }
    }
  }
  
  tags = local.common_tags
}

# Security Groups
module "eks_security_group" {
  source = "terraform-aws-modules/security-group/aws"
  
  name        = "${local.cluster_name}-eks-sg"
  description = "Security group for EKS cluster"
  vpc_id      = module.vpc.vpc_id
  
  ingress_with_cidr_blocks = [
    {
      from_port   = 443
      to_port     = 443
      protocol    = "tcp"
      cidr_blocks = module.vpc.vpc_cidr_block
      description = "Allow HTTPS from VPC"
    }
  ]
  
  egress_with_cidr_blocks = [
    {
      from_port   = 0
      to_port     = 0
      protocol    = "-1"
      cidr_blocks = "0.0.0.0/0"
      description = "Allow all outbound"
    }
  ]
  
  tags = local.common_tags
}

module "rds_security_group" {
  source = "terraform-aws-modules/security-group/aws"
  
  name        = "${var.environment}-rds-sg"
  description = "Security group for RDS PostgreSQL"
  vpc_id      = module.vpc.vpc_id
  
  ingress_with_source_security_group_id = [
    {
      from_port                = 5432
      to_port                  = 5432
      protocol                 = "tcp"
      source_security_group_id = module.eks.node_security_group_id
      description              = "Allow PostgreSQL from EKS nodes"
    }
  ]
  
  tags = local.common_tags
}

module "elasticache_security_group" {
  source = "terraform-aws-modules/security-group/aws"
  
  name        = "${var.environment}-elasticache-sg"
  description = "Security group for ElastiCache Redis"
  vpc_id      = module.vpc.vpc_id
  
  ingress_with_source_security_group_id = [
    {
      from_port                = 6379
      to_port                  = 6379
      protocol                 = "tcp"
      source_security_group_id = module.eks.node_security_group_id
      description              = "Allow Redis from EKS nodes"
    }
  ]
  
  tags = local.common_tags
}

module "msk_security_group" {
  source = "terraform-aws-modules/security-group/aws"
  
  name        = "${var.environment}-msk-sg"
  description = "Security group for Amazon MSK"
  vpc_id      = module.vpc.vpc_id
  
  ingress_with_source_security_group_id = [
    {
      from_port                = 9092
      to_port                  = 9092
      protocol                 = "tcp"
      source_security_group_id = module.eks.node_security_group_id
      description              = "Allow Kafka from EKS nodes"
    },
    {
      from_port                = 9094
      to_port                  = 9094
      protocol                 = "tcp"
      source_security_group_id = module.eks.node_security_group_id
      description              = "Allow Kafka TLS from EKS nodes"
    }
  ]
  
  ingress_with_self = [
    {
      from_port   = 0
      to_port     = 0
      protocol    = "-1"
      description = "Allow all traffic between brokers"
    }
  ]
  
  tags = local.common_tags
}

# KMS Keys
resource "aws_kms_key" "rds" {
  description             = "KMS key for RDS encryption"
  deletion_window_in_days = 30
  enable_key_rotation     = true
  
  tags = merge(local.common_tags, {
    Name = "${var.environment}-rds-kms"
  })
}

resource "aws_kms_key" "msk" {
  description             = "KMS key for MSK encryption"
  deletion_window_in_days = 30
  enable_key_rotation     = true
  
  tags = merge(local.common_tags, {
    Name = "${var.environment}-msk-kms"
  })
}

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "msk" {
  name              = "/aws/msk/${var.environment}-trading-kafka"
  retention_in_days = var.environment == "prod" ? 90 : 30
  
  tags = local.common_tags
}

# S3 Bucket for MSK Logs
resource "aws_s3_bucket" "msk_logs" {
  bucket = "${var.environment}-trading-msk-logs-${data.aws_caller_identity.current.account_id}"
  
  tags = local.common_tags
}

resource "aws_s3_bucket_versioning" "msk_logs" {
  bucket = aws_s3_bucket.msk_logs.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "msk_logs" {
  bucket = aws_s3_bucket.msk_logs.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# MSK Configuration
resource "aws_msk_configuration" "kafka_config" {
  name              = "${var.environment}-kafka-config"
  kafka_versions    = ["3.5.1"]
  server_properties = <<PROPERTIES
auto.create.topics.enable=false
default.replication.factor=3
min.insync.replicas=2
num.io.threads=8
num.network.threads=5
num.replica.fetchers=2
replica.lag.time.max.ms=30000
socket.receive.buffer.bytes=102400
socket.request.max.bytes=104857600
socket.send.buffer.bytes=102400
unclean.leader.election.enable=false
zookeeper.session.timeout.ms=18000
log.retention.hours=168
log.segment.bytes=1073741824
compression.type=lz4
PROPERTIES
}

# Helm Releases for Kubernetes Add-ons
resource "helm_release" "aws_load_balancer_controller" {
  name       = "aws-load-balancer-controller"
  repository = "https://aws.github.io/eks-charts"
  chart      = "aws-load-balancer-controller"
  namespace  = "kube-system"
  version    = "1.6.2"
  
  set {
    name  = "clusterName"
    value = module.eks.cluster_name
  }
  
  set {
    name  = "serviceAccount.create"
    value = "true"
  }
  
  set {
    name  = "serviceAccount.annotations.eks\\.amazonaws\\.com/role-arn"
    value = module.eks_lb_controller_irsa.iam_role_arn
  }
  
  depends_on = [module.eks]
}

resource "helm_release" "cluster_autoscaler" {
  name       = "cluster-autoscaler"
  repository = "https://kubernetes.github.io/autoscaler"
  chart      = "cluster-autoscaler"
  namespace  = "kube-system"
  version    = "9.29.3"
  
  set {
    name  = "autoDiscovery.clusterName"
    value = module.eks.cluster_name
  }
  
  set {
    name  = "awsRegion"
    value = var.aws_region
  }
  
  set {
    name  = "rbac.serviceAccount.annotations.eks\\.amazonaws\\.com/role-arn"
    value = module.cluster_autoscaler_irsa.iam_role_arn
  }
  
  depends_on = [module.eks]
}

resource "helm_release" "metrics_server" {
  name       = "metrics-server"
  repository = "https://kubernetes-sigs.github.io/metrics-server/"
  chart      = "metrics-server"
  namespace  = "kube-system"
  version    = "3.11.0"
  
  depends_on = [module.eks]
}
```

### variables.tf

```hcl
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "trading-platform"
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "Public subnet CIDR blocks"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}

variable "private_app_subnet_cidrs" {
  description = "Private application subnet CIDR blocks"
  type        = list(string)
  default     = ["10.0.11.0/24", "10.0.12.0/24", "10.0.13.0/24"]
}

variable "private_data_subnet_cidrs" {
  description = "Private data subnet CIDR blocks"
  type        = list(string)
  default     = ["10.0.21.0/24", "10.0.22.0/24", "10.0.23.0/24"]
}

variable "eks_cluster_version" {
  description = "EKS cluster version"
  type        = string
  default     = "1.28"
}

variable "rds_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.r6i.4xlarge"
}

variable "rds_allocated_storage" {
  description = "RDS allocated storage in GB"
  type        = number
  default     = 2048
}

variable "rds_iops" {
  description = "RDS provisioned IOPS"
  type        = number
  default     = 64000
}

variable "elasticache_node_type" {
  description = "ElastiCache node type"
  type        = string
  default     = "cache.r6g.2xlarge"
}

variable "elasticache_num_nodes" {
  description = "Number of ElastiCache nodes"
  type        = number
  default     = 6
}

variable "msk_instance_type" {
  description = "MSK broker instance type"
  type        = string
  default     = "kafka.m5.4xlarge"
}

variable "msk_volume_size" {
  description = "MSK EBS volume size in GB"
  type        = number
  default     = 2000
}
```

### outputs.tf

```hcl
output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "eks_cluster_name" {
  description = "EKS cluster name"
  value       = module.eks.cluster_name
}

output "eks_cluster_endpoint" {
  description = "EKS cluster endpoint"
  value       = module.eks.cluster_endpoint
}

output "rds_endpoint" {
  description = "RDS endpoint"
  value       = module.rds.db_instance_endpoint
  sensitive   = true
}

output "elasticache_endpoint" {
  description = "ElastiCache endpoint"
  value       = module.elasticache.configuration_endpoint
  sensitive   = true
}

output "msk_bootstrap_brokers" {
  description = "MSK bootstrap brokers"
  value       = module.msk.bootstrap_brokers_tls
  sensitive   = true
}

output "configure_kubectl" {
  description = "Command to configure kubectl"
  value       = "aws eks update-kubeconfig --region ${var.aws_region} --name ${module.eks.cluster_name}"
}
```

### Production Environment (environments/prod/terraform.tfvars)

```hcl
environment = "prod"
aws_region  = "us-east-1"

# VPC Configuration
vpc_cidr                  = "10.0.0.0/16"
public_subnet_cidrs       = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
private_app_subnet_cidrs  = ["10.0.11.0/24", "10.0.12.0/24", "10.0.13.0/24"]
private_data_subnet_cidrs = ["10.0.21.0/24", "10.0.22.0/24", "10.0.23.0/24"]

# EKS Configuration
eks_cluster_version = "1.28"

# RDS Configuration
rds_instance_class    = "db.r6i.4xlarge"
rds_allocated_storage = 2048
rds_iops              = 64000

# ElastiCache Configuration
elasticache_node_type  = "cache.r6g.2xlarge"
elasticache_num_nodes  = 6

# MSK Configuration
msk_instance_type = "kafka.m5.4xlarge"
msk_volume_size   = 2000
```

## Deployment Commands

```bash
# Initialize Terraform
terraform init

# Select workspace/environment
terraform workspace select prod || terraform workspace new prod

# Plan infrastructure changes
terraform plan -var-file=environments/prod/terraform.tfvars

# Apply infrastructure changes
terraform apply -var-file=environments/prod/terraform.tfvars -auto-approve

# Get outputs
terraform output eks_cluster_name
terraform output -raw configure_kubectl | bash

# Verify EKS cluster
kubectl get nodes
kubectl get pods --all-namespaces

# Destroy infrastructure (BE CAREFUL!)
terraform destroy -var-file=environments/prod/terraform.tfvars
```

---

**Document Version**: 1.0  
**Last Updated**: January 17, 2026  
**Status**: Complete
