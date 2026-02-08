# AWS Container Services (ECS, EKS, Fargate) - SAA-C03 Comprehensive Guide

## Table of Contents
1. [Overview and Introduction](#overview-and-introduction)
2. [Amazon ECS Fundamentals](#amazon-ecs-fundamentals)
3. [Amazon EKS Fundamentals](#amazon-eks-fundamentals)
4. [AWS Fargate](#aws-fargate)
5. [Launch Types and Capacity Providers](#launch-types-and-capacity-providers)
6. [Task Definitions and Services](#task-definitions-and-services)
7. [Networking and Load Balancing](#networking-and-load-balancing)
8. [Security and IAM](#security-and-iam)
9. [Storage Options](#storage-options)
10. [Monitoring and Logging](#monitoring-and-logging)
11. [Scaling and Auto Scaling](#scaling-and-auto-scaling)
12. [Service Discovery and Mesh](#service-discovery-and-mesh)
13. [Cost Optimization](#cost-optimization)
14. [Best Practices](#best-practices)
15. [ECS vs EKS vs Fargate Comparison](#ecs-vs-eks-vs-fargate-comparison)
16. [AWS CLI Commands Reference](#aws-cli-commands-reference)
17. [SAA-C03 Exam Tips](#saa-c03-exam-tips)
18. [Practice Questions](#practice-questions)

---

## Overview and Introduction

### What are AWS Container Services?

AWS provides multiple container orchestration services to help you deploy, manage, and scale containerized applications:

- **Amazon ECS (Elastic Container Service)**: AWS-native container orchestration
- **Amazon EKS (Elastic Kubernetes Service)**: Managed Kubernetes service
- **AWS Fargate**: Serverless compute engine for containers

### Why Containers?

Containers provide:
- **Consistency**: Same environment from development to production
- **Portability**: Run anywhere containers are supported
- **Efficiency**: Share OS kernel, lower overhead than VMs
- **Isolation**: Process-level isolation between applications
- **Scalability**: Quickly scale up or down based on demand

### Container Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     AWS Container Services                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │
│  │   Amazon    │    │   Amazon    │    │    AWS      │      │
│  │    ECS      │    │    EKS      │    │   Fargate   │      │
│  │ (AWS Native)│    │ (Kubernetes)│    │ (Serverless)│      │
│  └─────────────┘    └─────────────┘    └─────────────┘      │
│         │                 │                  │                │
│         └─────────────────┼──────────────────┘                │
│                           │                                   │
│                    ┌──────┴──────┐                           │
│                    │   Compute   │                           │
│                    │   Options   │                           │
│                    └──────┬──────┘                           │
│           ┌───────────────┼───────────────┐                  │
│    ┌──────┴──────┐ ┌──────┴──────┐ ┌──────┴──────┐         │
│    │     EC2     │ │   Fargate   │ │  Outposts   │         │
│    │  Instances  │ │  Serverless │ │  On-Prem    │         │
│    └─────────────┘ └─────────────┘ └─────────────┘         │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Amazon ECS Fundamentals

### What is Amazon ECS?

Amazon Elastic Container Service (ECS) is a fully managed container orchestration service that makes it easy to deploy, manage, and scale containerized applications. ECS is deeply integrated with AWS services and uses AWS-native concepts.

### Key Benefits

- **AWS Native**: Deep integration with AWS services (IAM, CloudWatch, VPC, ALB)
- **No Control Plane Cost**: No charge for the ECS control plane
- **Flexible Compute**: Support for EC2 and Fargate launch types
- **Task-based Architecture**: Simple task and service abstractions
- **Windows Support**: Full support for Windows containers

### ECS Architecture Components

#### 1. Clusters
- Logical grouping of tasks or services
- Regional resource
- Can span multiple Availability Zones
- Contains EC2 instances (EC2 launch type) or serverless compute (Fargate)

```json
{
  "clusterName": "production-cluster",
  "clusterSettings": [
    {
      "name": "containerInsights",
      "value": "enabled"
    }
  ],
  "capacityProviders": [
    "FARGATE",
    "FARGATE_SPOT"
  ]
}
```

#### 2. Task Definitions
- Blueprint for your application
- Defines containers, resources, networking, and IAM roles
- Versioned (each revision creates new version)
- JSON format specification

```json
{
  "family": "web-application",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::123456789:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::123456789:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "web-container",
      "image": "123456789.dkr.ecr.us-east-1.amazonaws.com/web-app:latest",
      "portMappings": [
        {
          "containerPort": 80,
          "protocol": "tcp"
        }
      ],
      "essential": true,
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/web-application",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

#### 3. Tasks
- Instantiation of a task definition
- One or more containers running together
- Atomic unit of deployment
- Can run standalone or as part of a service

#### 4. Services
- Maintains desired count of tasks
- Handles task placement and scheduling
- Integrates with load balancers
- Supports rolling deployments

### ECS Launch Types

| Feature | EC2 Launch Type | Fargate Launch Type |
|---------|-----------------|---------------------|
| **Infrastructure** | You manage EC2 instances | AWS manages infrastructure |
| **Pricing** | EC2 instance costs | Per vCPU and memory per second |
| **Scaling** | Cluster capacity + task scaling | Task scaling only |
| **Networking** | Bridge, host, awsvpc | awsvpc only |
| **GPUs** | Supported | Not supported |
| **Persistent Storage** | EBS, EFS | EFS only |
| **Windows Containers** | Supported | Supported |
| **Control** | Full OS access | No OS access |

---

## Amazon EKS Fundamentals

### What is Amazon EKS?

Amazon Elastic Kubernetes Service (EKS) is a managed Kubernetes service that makes it easy to run Kubernetes on AWS without needing to install and operate your own Kubernetes control plane.

### Key Benefits

- **Managed Control Plane**: AWS manages Kubernetes masters
- **Kubernetes Native**: Full Kubernetes API compatibility
- **Integration**: Works with existing Kubernetes tools and add-ons
- **Multi-AZ**: Control plane runs across multiple AZs
- **Security**: Integrated with AWS IAM and VPC

### EKS Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Amazon EKS Cluster                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Managed Control Plane (AWS)               │   │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐        │   │
│  │  │ API Server │ │   etcd     │ │ Scheduler  │        │   │
│  │  └────────────┘ └────────────┘ └────────────┘        │   │
│  │  ┌────────────┐ ┌────────────┐                        │   │
│  │  │ Controller │ │ Cloud      │                        │   │
│  │  │ Manager    │ │ Controller │                        │   │
│  │  └────────────┘ └────────────┘                        │   │
│  └──────────────────────────────────────────────────────┘   │
│                            │                                  │
│                     ┌──────┴──────┐                          │
│                     │             │                          │
│  ┌──────────────────┴───┐  ┌──────┴──────────────────┐     │
│  │    Data Plane (EC2)   │  │  Data Plane (Fargate)   │     │
│  │  ┌─────┐ ┌─────┐     │  │  ┌─────┐ ┌─────┐       │     │
│  │  │Node │ │Node │     │  │  │ Pod │ │ Pod │       │     │
│  │  │(EC2)│ │(EC2)│     │  │  └─────┘ └─────┘       │     │
│  │  └─────┘ └─────┘     │  │                         │     │
│  └───────────────────────┘  └─────────────────────────┘     │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### EKS Components

#### Control Plane
- **API Server**: Front-end for Kubernetes API
- **etcd**: Distributed key-value store for cluster data
- **Scheduler**: Assigns pods to nodes
- **Controller Manager**: Runs controller processes
- **Cloud Controller**: Integrates with AWS services

#### Data Plane Options
1. **Self-Managed Nodes**: EC2 instances you manage
2. **Managed Node Groups**: AWS manages node lifecycle
3. **Fargate**: Serverless compute for pods

### EKS Pricing

| Component | Cost |
|-----------|------|
| Control Plane | $0.10 per hour per cluster |
| Worker Nodes (EC2) | Standard EC2 pricing |
| Worker Nodes (Fargate) | Per vCPU and memory per second |
| EKS Anywhere | License fee required |

### Managed Node Groups

Managed node groups automate the provisioning and lifecycle management of nodes:

- Automatic node provisioning using EC2 Auto Scaling groups
- Automatic node updates and patching
- Integration with Cluster Autoscaler
- Support for Spot instances
- Custom AMIs supported

```yaml
apiVersion: eksctl.io/v1alpha5
kind: ClusterConfig
metadata:
  name: production-cluster
  region: us-east-1
managedNodeGroups:
  - name: managed-ng-1
    instanceType: m5.large
    desiredCapacity: 3
    minSize: 1
    maxSize: 10
    volumeSize: 100
    ssh:
      allow: true
    labels:
      nodegroup-type: managed-workers
```

---

## AWS Fargate

### What is AWS Fargate?

AWS Fargate is a serverless compute engine for containers that works with both Amazon ECS and Amazon EKS. With Fargate, you don't need to provision, configure, or scale clusters of virtual machines to run containers.

### Key Benefits

- **Serverless**: No servers to manage or provision
- **Right-sized**: Pay for exact resources needed
- **Isolation**: Each task/pod runs in its own kernel
- **Scaling**: Automatic scaling with workload
- **Security**: Isolated compute environments

### Fargate Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       AWS Fargate                            │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                    Your Tasks/Pods                     │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │   │
│  │  │   Task 1    │  │   Task 2    │  │   Task 3    │   │   │
│  │  │ ┌─────────┐ │  │ ┌─────────┐ │  │ ┌─────────┐ │   │   │
│  │  │ │Container│ │  │ │Container│ │  │ │Container│ │   │   │
│  │  │ └─────────┘ │  │ └─────────┘ │  │ └─────────┘ │   │   │
│  │  │    ENI      │  │    ENI      │  │    ENI      │   │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘   │   │
│  └──────────────────────────────────────────────────────┘   │
│                            │                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              AWS Managed Infrastructure                │   │
│  │  • Compute • Networking • Security • Scaling          │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Fargate Resource Configuration

#### CPU and Memory Combinations

| CPU (vCPU) | Memory Options (GB) |
|------------|---------------------|
| 0.25 | 0.5, 1, 2 |
| 0.5 | 1, 2, 3, 4 |
| 1 | 2, 3, 4, 5, 6, 7, 8 |
| 2 | 4-16 (1 GB increments) |
| 4 | 8-30 (1 GB increments) |
| 8 | 16-60 (4 GB increments) |
| 16 | 32-120 (8 GB increments) |

#### Ephemeral Storage
- Default: 20 GB
- Maximum: 200 GB
- Configurable per task

### Fargate Spot

Fargate Spot allows you to run fault-tolerant workloads at up to 70% discount:

- **Use Cases**: Batch processing, CI/CD, data analysis
- **Interruption**: 2-minute warning before termination
- **Capacity**: Based on spare AWS capacity
- **Pricing**: Pay Spot price (typically 50-70% off On-Demand)

```json
{
  "capacityProviderStrategy": [
    {
      "capacityProvider": "FARGATE_SPOT",
      "weight": 2,
      "base": 0
    },
    {
      "capacityProvider": "FARGATE",
      "weight": 1,
      "base": 1
    }
  ]
}
```

---

## Launch Types and Capacity Providers

### Capacity Providers

Capacity providers manage the infrastructure for your tasks:

#### ECS Capacity Providers
- **FARGATE**: On-Demand Fargate capacity
- **FARGATE_SPOT**: Spot Fargate capacity
- **Auto Scaling Group**: EC2 instances in ASG

#### Capacity Provider Strategy

```json
{
  "capacityProviderStrategy": [
    {
      "capacityProvider": "FARGATE",
      "weight": 1,
      "base": 2
    },
    {
      "capacityProvider": "FARGATE_SPOT",
      "weight": 4,
      "base": 0
    }
  ]
}
```

- **base**: Minimum tasks on this provider
- **weight**: Relative percentage of remaining tasks

### Choosing Launch Type

| Scenario | Recommended Launch Type |
|----------|------------------------|
| Variable workloads | Fargate |
| GPU requirements | EC2 |
| Persistent storage (EBS) | EC2 |
| Windows containers | EC2 or Fargate |
| Cost optimization (steady state) | EC2 with Reserved Instances |
| Cost optimization (variable) | Fargate Spot |
| Compliance (dedicated hosts) | EC2 |
| Serverless simplicity | Fargate |

---

## Task Definitions and Services

### Task Definition Parameters

#### Required Parameters
- **family**: Name of the task definition
- **containerDefinitions**: List of container configurations

#### Container Definition Parameters

```json
{
  "containerDefinitions": [
    {
      "name": "my-container",
      "image": "my-repo/my-image:tag",
      "cpu": 256,
      "memory": 512,
      "memoryReservation": 256,
      "portMappings": [
        {
          "containerPort": 8080,
          "hostPort": 8080,
          "protocol": "tcp"
        }
      ],
      "essential": true,
      "environment": [
        {
          "name": "ENV_VAR",
          "value": "value"
        }
      ],
      "secrets": [
        {
          "name": "DB_PASSWORD",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:name"
        }
      ],
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8080/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      },
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/my-task",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### ECS Services

#### Service Configuration

```json
{
  "serviceName": "web-service",
  "cluster": "production-cluster",
  "taskDefinition": "web-application:1",
  "desiredCount": 3,
  "launchType": "FARGATE",
  "platformVersion": "LATEST",
  "deploymentConfiguration": {
    "maximumPercent": 200,
    "minimumHealthyPercent": 100,
    "deploymentCircuitBreaker": {
      "enable": true,
      "rollback": true
    }
  },
  "networkConfiguration": {
    "awsvpcConfiguration": {
      "subnets": ["subnet-xxx", "subnet-yyy"],
      "securityGroups": ["sg-xxx"],
      "assignPublicIp": "DISABLED"
    }
  },
  "loadBalancers": [
    {
      "targetGroupArn": "arn:aws:elasticloadbalancing:...",
      "containerName": "web-container",
      "containerPort": 80
    }
  ]
}
```

#### Deployment Strategies

| Strategy | Description | Use Case |
|----------|-------------|----------|
| **Rolling Update** | Replaces tasks gradually | Standard deployments |
| **Blue/Green (CodeDeploy)** | Shifts traffic between task sets | Zero-downtime deployments |
| **External** | Third-party deployment controller | Custom deployment tools |

### Task Placement (EC2 Launch Type)

#### Placement Strategies
- **binpack**: Minimize host count (cost optimization)
- **spread**: Distribute across AZs or instances (high availability)
- **random**: Random placement

#### Placement Constraints
- **distinctInstance**: Each task on different instance
- **memberOf**: Place based on cluster query language

```json
{
  "placementStrategy": [
    {
      "type": "spread",
      "field": "attribute:ecs.availability-zone"
    },
    {
      "type": "binpack",
      "field": "memory"
    }
  ],
  "placementConstraints": [
    {
      "type": "distinctInstance"
    }
  ]
}
```

---

## Networking and Load Balancing

### Network Modes

#### awsvpc Mode (Required for Fargate)
- Each task gets its own ENI
- Task-level networking with security groups
- Full VPC networking capabilities
- Private IP from subnet CIDR

#### Bridge Mode (EC2 Only)
- Docker's built-in bridge network
- Port mapping required
- Dynamic port mapping supported

#### Host Mode (EC2 Only)
- Container uses host's network stack
- Direct port access
- Best network performance

#### None Mode
- No external connectivity
- For batch jobs or internal processing

### Load Balancing Integration

#### Application Load Balancer (ALB)
- Layer 7 load balancing
- Path-based routing
- Host-based routing
- Best for HTTP/HTTPS workloads

#### Network Load Balancer (NLB)
- Layer 4 load balancing
- Ultra-low latency
- Static IP addresses
- Best for TCP/UDP workloads

#### Service Discovery

AWS Cloud Map integration for service discovery:

```json
{
  "serviceRegistries": [
    {
      "registryArn": "arn:aws:servicediscovery:us-east-1:123456789:service/srv-xxx",
      "containerName": "web-container",
      "containerPort": 80
    }
  ]
}
```

---

## Security and IAM

### IAM Roles for Containers

#### Task Execution Role
- Used by ECS agent to pull images and write logs
- Required for Fargate
- Permissions: ECR access, CloudWatch Logs

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
```

#### Task Role
- Used by containers for AWS API calls
- Application-specific permissions
- Each task can have different role

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "dynamodb:Query"
      ],
      "Resource": [
        "arn:aws:s3:::my-bucket/*",
        "arn:aws:dynamodb:us-east-1:123456789:table/my-table"
      ]
    }
  ]
}
```

### Security Best Practices

1. **Use awsvpc Network Mode**: Task-level security groups
2. **Secrets Management**: Use Secrets Manager or Parameter Store
3. **Image Scanning**: Enable ECR image scanning
4. **Least Privilege**: Minimal IAM permissions
5. **Private Subnets**: Run tasks in private subnets
6. **Encryption**: Enable encryption at rest and in transit

### EKS Security

#### IAM Roles for Service Accounts (IRSA)
- Fine-grained IAM permissions for pods
- Uses OIDC identity provider
- No need for instance roles

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-service-account
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::123456789:role/my-role
```

#### Pod Security Standards
- Privileged: Unrestricted
- Baseline: Minimally restrictive
- Restricted: Heavily restricted

---

## Storage Options

### Amazon EFS (Elastic File System)

- Shared file system across tasks
- Supported by both EC2 and Fargate
- Persistent storage
- Multi-AZ availability

```json
{
  "volumes": [
    {
      "name": "efs-volume",
      "efsVolumeConfiguration": {
        "fileSystemId": "fs-xxxxxxxx",
        "transitEncryption": "ENABLED",
        "authorizationConfig": {
          "accessPointId": "fsap-xxxxxxxx",
          "iam": "ENABLED"
        }
      }
    }
  ],
  "containerDefinitions": [
    {
      "mountPoints": [
        {
          "sourceVolume": "efs-volume",
          "containerPath": "/data",
          "readOnly": false
        }
      ]
    }
  ]
}
```

### Amazon EBS (EC2 Launch Type Only)

- Block storage for single task
- High performance
- Snapshot support

### Bind Mounts

- Share data between containers in same task
- Ephemeral (lost when task stops)

### FSx for Windows File Server

- SMB file shares for Windows containers
- Active Directory integration
- High performance

---

## Monitoring and Logging

### CloudWatch Container Insights

Enable enhanced monitoring:
- CPU and memory utilization
- Network metrics
- Storage metrics
- Task and service level metrics

```json
{
  "clusterSettings": [
    {
      "name": "containerInsights",
      "value": "enabled"
    }
  ]
}
```

### Logging Drivers

#### awslogs Driver
```json
{
  "logConfiguration": {
    "logDriver": "awslogs",
    "options": {
      "awslogs-group": "/ecs/my-task",
      "awslogs-region": "us-east-1",
      "awslogs-stream-prefix": "ecs",
      "awslogs-create-group": "true"
    }
  }
}
```

#### FireLens (Fluent Bit/Fluentd)
- Advanced log routing
- Multiple destinations
- Log transformation

### X-Ray Integration

Distributed tracing for microservices:
- Trace requests across services
- Identify performance bottlenecks
- Debug errors

---

## Scaling and Auto Scaling

### ECS Service Auto Scaling

#### Target Tracking Scaling

```json
{
  "targetTrackingScalingPolicyConfiguration": {
    "targetValue": 75.0,
    "predefinedMetricSpecification": {
      "predefinedMetricType": "ECSServiceAverageCPUUtilization"
    },
    "scaleOutCooldown": 60,
    "scaleInCooldown": 60
  }
}
```

#### Step Scaling

```json
{
  "stepScalingPolicyConfiguration": {
    "adjustmentType": "ChangeInCapacity",
    "stepAdjustments": [
      {
        "metricIntervalLowerBound": 0,
        "metricIntervalUpperBound": 10,
        "scalingAdjustment": 1
      },
      {
        "metricIntervalLowerBound": 10,
        "scalingAdjustment": 2
      }
    ],
    "cooldown": 60
  }
}
```

### EKS Auto Scaling

#### Cluster Autoscaler
- Automatically adjusts node count
- Based on pending pods
- Works with managed node groups

#### Horizontal Pod Autoscaler (HPA)
- Scales pods based on metrics
- CPU, memory, or custom metrics

#### Karpenter
- Fast, flexible node provisioning
- Bin-packing optimization
- Spot instance support

---

## Service Discovery and Mesh

### AWS Cloud Map

Service discovery for containers:

```json
{
  "serviceDiscovery": {
    "namespaceId": "ns-xxxxxxxx",
    "service": {
      "name": "my-service",
      "dnsConfig": {
        "dnsRecords": [
          {
            "type": "A",
            "TTL": 60
          }
        ]
      },
      "healthCheckCustomConfig": {
        "failureThreshold": 1
      }
    }
  }
}
```

### AWS App Mesh

Service mesh for microservices:
- Traffic management
- Observability
- Security (mTLS)
- Works with ECS, EKS, EC2

---

## Cost Optimization

### Pricing Models

#### ECS Pricing
- **Control Plane**: Free
- **EC2 Launch Type**: EC2 instance costs
- **Fargate**: Per vCPU and memory per second

#### EKS Pricing
- **Control Plane**: $0.10/hour per cluster
- **EC2 Nodes**: EC2 instance costs
- **Fargate Pods**: Per vCPU and memory per second

### Cost Optimization Strategies

| Strategy | Description | Savings |
|----------|-------------|---------|
| **Fargate Spot** | Use spare capacity | Up to 70% |
| **EC2 Spot** | Spot instances for nodes | Up to 90% |
| **Reserved Instances** | Commit to EC2 capacity | Up to 72% |
| **Savings Plans** | Commit to Fargate usage | Up to 52% |
| **Right-sizing** | Match resources to needs | Variable |
| **Bin-packing** | Maximize instance utilization | 20-40% |

### Cost Comparison

For a workload requiring 4 vCPU and 8 GB memory running 24/7:

| Option | Monthly Cost (approx.) |
|--------|----------------------|
| Fargate On-Demand | ~$150 |
| Fargate Spot | ~$50-75 |
| EC2 On-Demand (t3.xlarge) | ~$120 |
| EC2 Spot | ~$40-60 |
| EC2 Reserved (1 year) | ~$75 |

---

## Best Practices

### Container Best Practices

1. **One Process Per Container**: Single responsibility
2. **Minimal Base Images**: Reduce attack surface
3. **Multi-stage Builds**: Smaller final images
4. **Don't Run as Root**: Use non-root users
5. **Handle Signals**: Graceful shutdown (SIGTERM)
6. **Health Checks**: Define comprehensive health checks

### ECS Best Practices

1. **Use Fargate for Simplicity**: Unless specific EC2 needs
2. **Enable Container Insights**: For monitoring
3. **Use Task Roles**: Not instance roles
4. **Deploy Across AZs**: For high availability
5. **Use Deployment Circuit Breaker**: Automatic rollback
6. **Enable Execute Command**: For debugging

### EKS Best Practices

1. **Use Managed Node Groups**: Simplified management
2. **Implement IRSA**: Pod-level IAM permissions
3. **Enable Control Plane Logging**: For audit
4. **Use Pod Security Standards**: For security
5. **Implement Network Policies**: For network security
6. **Regular Updates**: Keep Kubernetes version current

---

## ECS vs EKS vs Fargate Comparison

### Feature Comparison

| Feature | ECS | EKS | Fargate |
|---------|-----|-----|---------|
| **Orchestrator** | AWS Native | Kubernetes | Compute Engine |
| **Learning Curve** | Low | High | Lowest |
| **Control Plane Cost** | Free | $0.10/hour | N/A |
| **Portability** | AWS only | Multi-cloud | AWS only |
| **Ecosystem** | AWS integrations | K8s ecosystem | Limited |
| **Windows Support** | Yes | Yes | Yes |
| **GPU Support** | Yes (EC2) | Yes (EC2) | No |
| **Serverless** | Via Fargate | Via Fargate | Native |

### When to Use Each

#### Choose ECS When:
- AWS-native environment
- Simpler learning curve needed
- Deep AWS integration required
- Cost-sensitive (no control plane cost)

#### Choose EKS When:
- Kubernetes expertise exists
- Multi-cloud or portability needed
- Kubernetes ecosystem tools required
- Complex networking needs

#### Choose Fargate When:
- Serverless simplicity desired
- Variable workloads
- No infrastructure management wanted
- Rapid scaling required

---

## AWS CLI Commands Reference

This section provides comprehensive AWS CLI commands for managing Amazon ECS, EKS, Fargate, and Amazon ECR.

### Prerequisites

```bash
# Install or update AWS CLI
# macOS/Linux
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Verify installation
aws --version

# Configure AWS CLI
aws configure
# Enter: AWS Access Key ID, Secret Access Key, Default region, Output format (json)

# Install eksctl (for EKS management)
# macOS
brew tap weaveworks/tap
brew install weaveworks/tap/eksctl

# Linux
curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
sudo mv /tmp/eksctl /usr/local/bin

# Verify eksctl installation
eksctl version
```

### ECS Cluster Management

```bash
# Create ECS cluster (default - Fargate/EC2 compatible)
aws ecs create-cluster \
  --cluster-name production-cluster \
  --tags key=Environment,value=Production key=Team,value=Platform

# Create ECS cluster with Container Insights enabled
aws ecs create-cluster \
  --cluster-name production-cluster \
  --settings name=containerInsights,value=enabled \
  --tags key=Environment,value=Production

# Create ECS cluster with capacity providers
aws ecs create-cluster \
  --cluster-name production-cluster \
  --capacity-providers FARGATE FARGATE_SPOT \
  --default-capacity-provider-strategy \
    capacityProvider=FARGATE,weight=1,base=1 \
    capacityProvider=FARGATE_SPOT,weight=4

# List ECS clusters
aws ecs list-clusters

# Describe ECS cluster
aws ecs describe-clusters \
  --clusters production-cluster

# Get cluster details with statistics
aws ecs describe-clusters \
  --clusters production-cluster \
  --include STATISTICS TAGS

# Update cluster settings (enable Container Insights)
aws ecs update-cluster-settings \
  --cluster production-cluster \
  --settings name=containerInsights,value=enabled

# Put cluster capacity providers
aws ecs put-cluster-capacity-providers \
  --cluster production-cluster \
  --capacity-providers FARGATE FARGATE_SPOT my-asg-capacity-provider \
  --default-capacity-provider-strategy \
    capacityProvider=FARGATE,weight=1 \
    capacityProvider=FARGATE_SPOT,weight=2

# Delete ECS cluster
aws ecs delete-cluster \
  --cluster production-cluster
```

### ECS Task Definitions

```bash
# Register task definition (Fargate)
aws ecs register-task-definition \
  --family web-app \
  --network-mode awsvpc \
  --requires-compatibilities FARGATE \
  --cpu 256 \
  --memory 512 \
  --execution-role-arn arn:aws:iam::123456789012:role/ecsTaskExecutionRole \
  --task-role-arn arn:aws:iam::123456789012:role/ecsTaskRole \
  --container-definitions '[
    {
      "name": "web-container",
      "image": "123456789012.dkr.ecr.us-east-1.amazonaws.com/web-app:latest",
      "essential": true,
      "portMappings": [
        {
          "containerPort": 80,
          "protocol": "tcp"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/web-app",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "environment": [
        {
          "name": "ENV",
          "value": "production"
        }
      ]
    }
  ]'

# Register task definition from JSON file
aws ecs register-task-definition \
  --cli-input-json file://task-definition.json

# Register task definition with secrets from Parameter Store
aws ecs register-task-definition \
  --family app-with-secrets \
  --network-mode awsvpc \
  --requires-compatibilities FARGATE \
  --cpu 512 \
  --memory 1024 \
  --execution-role-arn arn:aws:iam::123456789012:role/ecsTaskExecutionRole \
  --container-definitions '[
    {
      "name": "app",
      "image": "myapp:latest",
      "secrets": [
        {
          "name": "DB_PASSWORD",
          "valueFrom": "arn:aws:ssm:us-east-1:123456789012:parameter/prod/db-password"
        }
      ]
    }
  ]'

# Register task definition with EFS volume
aws ecs register-task-definition \
  --family app-with-efs \
  --network-mode awsvpc \
  --requires-compatibilities FARGATE \
  --cpu 512 \
  --memory 1024 \
  --execution-role-arn arn:aws:iam::123456789012:role/ecsTaskExecutionRole \
  --volumes '[
    {
      "name": "efs-storage",
      "efsVolumeConfiguration": {
        "fileSystemId": "fs-0123456789abcdef0",
        "transitEncryption": "ENABLED",
        "authorizationConfig": {
          "accessPointId": "fsap-0123456789abcdef0",
          "iam": "ENABLED"
        }
      }
    }
  ]' \
  --container-definitions '[
    {
      "name": "app",
      "image": "myapp:latest",
      "mountPoints": [
        {
          "sourceVolume": "efs-storage",
          "containerPath": "/data",
          "readOnly": false
        }
      ]
    }
  ]'

# List task definitions
aws ecs list-task-definitions

# List task definition families
aws ecs list-task-definition-families

# Describe task definition
aws ecs describe-task-definition \
  --task-definition web-app:5

# Deregister task definition
aws ecs deregister-task-definition \
  --task-definition web-app:5
```

### ECS Services

```bash
# Create ECS service (Fargate)
aws ecs create-service \
  --cluster production-cluster \
  --service-name web-service \
  --task-definition web-app:1 \
  --desired-count 3 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={
    subnets=[subnet-0123456789abcdef0,subnet-0123456789abcdef1],
    securityGroups=[sg-0123456789abcdef0],
    assignPublicIp=DISABLED
  }" \
  --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/web-tg/50dc6c495c0c9188,containerName=web-container,containerPort=80" \
  --health-check-grace-period-seconds 60 \
  --tags key=Environment,value=Production

# Create service with capacity provider strategy
aws ecs create-service \
  --cluster production-cluster \
  --service-name api-service \
  --task-definition api-app:1 \
  --desired-count 5 \
  --capacity-provider-strategy \
    capacityProvider=FARGATE,weight=1,base=2 \
    capacityProvider=FARGATE_SPOT,weight=3 \
  --network-configuration "awsvpcConfiguration={
    subnets=[subnet-0123456789abcdef0],
    securityGroups=[sg-0123456789abcdef0]
  }"

# Create service with Auto Scaling
aws ecs create-service \
  --cluster production-cluster \
  --service-name worker-service \
  --task-definition worker:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={
    subnets=[subnet-0123456789abcdef0],
    securityGroups=[sg-0123456789abcdef0]
  }" \
  --enable-execute-command

# Create service with service discovery
aws ecs create-service \
  --cluster production-cluster \
  --service-name backend-service \
  --task-definition backend:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={
    subnets=[subnet-0123456789abcdef0],
    securityGroups=[sg-0123456789abcdef0]
  }" \
  --service-registries "registryArn=arn:aws:servicediscovery:us-east-1:123456789012:service/srv-0123456789abcdef0"

# List services in cluster
aws ecs list-services \
  --cluster production-cluster

# Describe services
aws ecs describe-services \
  --cluster production-cluster \
  --services web-service api-service

# Update service (change desired count)
aws ecs update-service \
  --cluster production-cluster \
  --service web-service \
  --desired-count 5

# Update service (deploy new task definition)
aws ecs update-service \
  --cluster production-cluster \
  --service web-service \
  --task-definition web-app:2 \
  --force-new-deployment

# Update service (change capacity provider)
aws ecs update-service \
  --cluster production-cluster \
  --service web-service \
  --capacity-provider-strategy \
    capacityProvider=FARGATE,weight=1 \
    capacityProvider=FARGATE_SPOT,weight=4

# Delete service
aws ecs delete-service \
  --cluster production-cluster \
  --service web-service \
  --force
```

### ECS Tasks (Run Task)

```bash
# Run standalone task (Fargate)
aws ecs run-task \
  --cluster production-cluster \
  --task-definition batch-job:1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={
    subnets=[subnet-0123456789abcdef0],
    securityGroups=[sg-0123456789abcdef0],
    assignPublicIp=ENABLED
  }"

# Run task with environment variable overrides
aws ecs run-task \
  --cluster production-cluster \
  --task-definition data-processor:1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-0123456789abcdef0],securityGroups=[sg-0123456789abcdef0]}" \
  --overrides '{
    "containerOverrides": [
      {
        "name": "processor",
        "environment": [
          {
            "name": "BATCH_SIZE",
            "value": "1000"
          }
        ]
      }
    ]
  }'

# List running tasks
aws ecs list-tasks \
  --cluster production-cluster

# List tasks by service
aws ecs list-tasks \
  --cluster production-cluster \
  --service-name web-service

# Describe tasks
aws ecs describe-tasks \
  --cluster production-cluster \
  --tasks arn:aws:ecs:us-east-1:123456789012:task/production-cluster/1234567890abcdef

# Stop task
aws ecs stop-task \
  --cluster production-cluster \
  --task arn:aws:ecs:us-east-1:123456789012:task/production-cluster/1234567890abcdef \
  --reason "Manual intervention required"

# Execute command in running container (ECS Exec)
aws ecs execute-command \
  --cluster production-cluster \
  --task arn:aws:ecs:us-east-1:123456789012:task/production-cluster/1234567890abcdef \
  --container web-container \
  --interactive \
  --command "/bin/bash"
```

### ECS Auto Scaling

```bash
# Register ECS service with Application Auto Scaling
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --resource-id service/production-cluster/web-service \
  --scalable-dimension ecs:service:DesiredCount \
  --min-capacity 2 \
  --max-capacity 10

# Create target tracking scaling policy (CPU)
aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --resource-id service/production-cluster/web-service \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-name cpu-target-tracking \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration '{
    "TargetValue": 70.0,
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ECSServiceAverageCPUUtilization"
    },
    "ScaleInCooldown": 300,
    "ScaleOutCooldown": 60
  }'

# Create target tracking scaling policy (Memory)
aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --resource-id service/production-cluster/web-service \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-name memory-target-tracking \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration '{
    "TargetValue": 80.0,
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ECSServiceAverageMemoryUtilization"
    }
  }'

# Create step scaling policy
aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --resource-id service/production-cluster/web-service \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-name requests-step-scaling \
  --policy-type StepScaling \
  --step-scaling-policy-configuration '{
    "AdjustmentType": "PercentChangeInCapacity",
    "StepAdjustments": [
      {
        "MetricIntervalLowerBound": 0,
        "MetricIntervalUpperBound": 10,
        "ScalingAdjustment": 10
      },
      {
        "MetricIntervalLowerBound": 10,
        "ScalingAdjustment": 30
      }
    ],
    "Cooldown": 60
  }'

# Describe scaling policies
aws application-autoscaling describe-scaling-policies \
  --service-namespace ecs \
  --resource-id service/production-cluster/web-service

# Deregister scalable target
aws application-autoscaling deregister-scalable-target \
  --service-namespace ecs \
  --resource-id service/production-cluster/web-service \
  --scalable-dimension ecs:service:DesiredCount
```

### Amazon ECR (Elastic Container Registry)

```bash
# Create ECR repository
aws ecr create-repository \
  --repository-name web-app \
  --image-scanning-configuration scanOnPush=true \
  --encryption-configuration encryptionType=AES256 \
  --tags Key=Environment,Value=Production

# Create repository with KMS encryption
aws ecr create-repository \
  --repository-name secure-app \
  --image-scanning-configuration scanOnPush=true \
  --encryption-configuration encryptionType=KMS,kmsKey=arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012

# List repositories
aws ecr describe-repositories

# Get repository details
aws ecr describe-repositories \
  --repository-names web-app

# Get ECR login token and authenticate Docker
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com

# Tag Docker image for ECR
docker tag web-app:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/web-app:latest
docker tag web-app:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/web-app:v1.0.0

# Push image to ECR
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/web-app:latest
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/web-app:v1.0.0

# List images in repository
aws ecr list-images \
  --repository-name web-app

# Describe images (detailed)
aws ecr describe-images \
  --repository-name web-app

# Get specific image details
aws ecr describe-images \
  --repository-name web-app \
  --image-ids imageTag=latest

# Pull image from ECR
docker pull 123456789012.dkr.ecr.us-east-1.amazonaws.com/web-app:latest

# Set lifecycle policy (auto-delete old images)
aws ecr put-lifecycle-policy \
  --repository-name web-app \
  --lifecycle-policy-text '{
    "rules": [
      {
        "rulePriority": 1,
        "description": "Keep last 10 images",
        "selection": {
          "tagStatus": "any",
          "countType": "imageCountMoreThan",
          "countNumber": 10
        },
        "action": {
          "type": "expire"
        }
      }
    ]
  }'

# Get lifecycle policy
aws ecr get-lifecycle-policy \
  --repository-name web-app

# Set repository policy (cross-account access)
aws ecr set-repository-policy \
  --repository-name web-app \
  --policy-text '{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Sid": "AllowPull",
        "Effect": "Allow",
        "Principal": {
          "AWS": "arn:aws:iam::987654321098:root"
        },
        "Action": [
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:BatchCheckLayerAvailability"
        ]
      }
    ]
  }'

# Get repository policy
aws ecr get-repository-policy \
  --repository-name web-app

# Start image scan
aws ecr start-image-scan \
  --repository-name web-app \
  --image-id imageTag=latest

# Get image scan findings
aws ecr describe-image-scan-findings \
  --repository-name web-app \
  --image-id imageTag=latest

# Delete image
aws ecr batch-delete-image \
  --repository-name web-app \
  --image-ids imageTag=v1.0.0

# Delete multiple images
aws ecr batch-delete-image \
  --repository-name web-app \
  --image-ids imageTag=v1.0.0 imageTag=v1.0.1 imageTag=v1.0.2

# Delete repository
aws ecr delete-repository \
  --repository-name web-app \
  --force
```

### Amazon EKS Cluster Management

```bash
# Create EKS cluster using eksctl (recommended)
eksctl create cluster \
  --name production-eks \
  --region us-east-1 \
  --version 1.28 \
  --nodegroup-name standard-workers \
  --node-type t3.medium \
  --nodes 3 \
  --nodes-min 2 \
  --nodes-max 5 \
  --managed \
  --tags Environment=Production,Team=Platform

# Create EKS cluster with Fargate profile
eksctl create cluster \
  --name fargate-eks \
  --region us-east-1 \
  --fargate

# Create EKS cluster using AWS CLI
aws eks create-cluster \
  --name production-eks \
  --role-arn arn:aws:iam::123456789012:role/EKSClusterRole \
  --resources-vpc-config subnetIds=subnet-0123456789abcdef0,subnet-0123456789abcdef1,securityGroupIds=sg-0123456789abcdef0 \
  --kubernetes-version 1.28 \
  --logging '{"clusterLogging":[{"types":["api","audit","authenticator","controllerManager","scheduler"],"enabled":true}]}' \
  --tags Environment=Production

# List EKS clusters
aws eks list-clusters

# Describe EKS cluster
aws eks describe-cluster \
  --name production-eks

# Update cluster version
aws eks update-cluster-version \
  --name production-eks \
  --kubernetes-version 1.29

# Update cluster config (enable logging)
aws eks update-cluster-config \
  --name production-eks \
  --logging '{"clusterLogging":[{"types":["api","audit","authenticator","controllerManager","scheduler"],"enabled":true}]}'

# Get kubeconfig for cluster
aws eks update-kubeconfig \
  --name production-eks \
  --region us-east-1

# Delete EKS cluster (eksctl)
eksctl delete cluster \
  --name production-eks \
  --region us-east-1

# Delete EKS cluster (AWS CLI)
aws eks delete-cluster \
  --name production-eks
```

### EKS Node Groups

```bash
# Create managed node group
aws eks create-nodegroup \
  --cluster-name production-eks \
  --nodegroup-name standard-workers \
  --scaling-config minSize=2,maxSize=5,desiredSize=3 \
  --subnets subnet-0123456789abcdef0 subnet-0123456789abcdef1 \
  --instance-types t3.medium \
  --node-role arn:aws:iam::123456789012:role/EKSNodeRole \
  --tags Environment=Production,NodeType=Standard

# Create node group with spot instances
aws eks create-nodegroup \
  --cluster-name production-eks \
  --nodegroup-name spot-workers \
  --scaling-config minSize=1,maxSize=10,desiredSize=3 \
  --capacity-type SPOT \
  --subnets subnet-0123456789abcdef0 subnet-0123456789abcdef1 \
  --instance-types t3.medium t3.large \
  --node-role arn:aws:iam::123456789012:role/EKSNodeRole

# Create node group using eksctl
eksctl create nodegroup \
  --cluster production-eks \
  --name gpu-workers \
  --node-type g4dn.xlarge \
  --nodes 2 \
  --nodes-min 1 \
  --nodes-max 4 \
  --node-volume-size 100 \
  --node-ami-family AmazonLinux2 \
  --tags Environment=Production,Workload=ML

# List node groups
aws eks list-nodegroups \
  --cluster-name production-eks

# Describe node group
aws eks describe-nodegroup \
  --cluster-name production-eks \
  --nodegroup-name standard-workers

# Update node group configuration
aws eks update-nodegroup-config \
  --cluster-name production-eks \
  --nodegroup-name standard-workers \
  --scaling-config minSize=3,maxSize=10,desiredSize=5

# Update node group version
aws eks update-nodegroup-version \
  --cluster-name production-eks \
  --nodegroup-name standard-workers \
  --kubernetes-version 1.28

# Delete node group
aws eks delete-nodegroup \
  --cluster-name production-eks \
  --nodegroup-name standard-workers

# Delete node group using eksctl
eksctl delete nodegroup \
  --cluster production-eks \
  --name gpu-workers
```

### EKS Fargate Profiles

```bash
# Create Fargate profile
aws eks create-fargate-profile \
  --cluster-name production-eks \
  --fargate-profile-name app-profile \
  --pod-execution-role-arn arn:aws:iam::123456789012:role/EKSFargatePodExecutionRole \
  --subnets subnet-0123456789abcdef0 subnet-0123456789abcdef1 \
  --selectors '[{"namespace":"production","labels":{"app":"web"}}]' \
  --tags Environment=Production

# Create Fargate profile for multiple namespaces
aws eks create-fargate-profile \
  --cluster-name production-eks \
  --fargate-profile-name multi-ns-profile \
  --pod-execution-role-arn arn:aws:iam::123456789012:role/EKSFargatePodExecutionRole \
  --subnets subnet-0123456789abcdef0 subnet-0123456789abcdef1 \
  --selectors '[{"namespace":"backend"},{"namespace":"frontend"}]'

# Create Fargate profile using eksctl
eksctl create fargateprofile \
  --cluster production-eks \
  --name app-profile \
  --namespace production \
  --labels app=web

# List Fargate profiles
aws eks list-fargate-profiles \
  --cluster-name production-eks

# Describe Fargate profile
aws eks describe-fargate-profile \
  --cluster-name production-eks \
  --fargate-profile-name app-profile

# Delete Fargate profile
aws eks delete-fargate-profile \
  --cluster-name production-eks \
  --fargate-profile-name app-profile

# Delete Fargate profile using eksctl
eksctl delete fargateprofile \
  --cluster production-eks \
  --name app-profile
```

### EKS Add-ons

```bash
# List available add-ons
aws eks describe-addon-versions

# List add-ons for cluster
aws eks list-addons \
  --cluster-name production-eks

# Create add-on (VPC CNI)
aws eks create-addon \
  --cluster-name production-eks \
  --addon-name vpc-cni \
  --addon-version v1.15.0-eksbuild.2 \
  --service-account-role-arn arn:aws:iam::123456789012:role/VPCCNIRole \
  --resolve-conflicts OVERWRITE

# Create add-on (CoreDNS)
aws eks create-addon \
  --cluster-name production-eks \
  --addon-name coredns \
  --addon-version v1.10.1-eksbuild.2

# Create add-on (kube-proxy)
aws eks create-addon \
  --cluster-name production-eks \
  --addon-name kube-proxy \
  --addon-version v1.28.2-eksbuild.2

# Describe add-on
aws eks describe-addon \
  --cluster-name production-eks \
  --addon-name vpc-cni

# Update add-on
aws eks update-addon \
  --cluster-name production-eks \
  --addon-name vpc-cni \
  --addon-version v1.15.1-eksbuild.1 \
  --resolve-conflicts OVERWRITE

# Delete add-on
aws eks delete-addon \
  --cluster-name production-eks \
  --addon-name vpc-cni
```

### ECS/EKS Tags and Resource Management

```bash
# Tag ECS cluster
aws ecs tag-resource \
  --resource-arn arn:aws:ecs:us-east-1:123456789012:cluster/production-cluster \
  --tags key=CostCenter,value=Engineering key=Owner,value=PlatformTeam

# List tags for ECS resource
aws ecs list-tags-for-resource \
  --resource-arn arn:aws:ecs:us-east-1:123456789012:cluster/production-cluster

# Untag ECS resource
aws ecs untag-resource \
  --resource-arn arn:aws:ecs:us-east-1:123456789012:cluster/production-cluster \
  --tag-keys CostCenter

# Tag EKS cluster
aws eks tag-resource \
  --resource-arn arn:aws:eks:us-east-1:123456789012:cluster/production-eks \
  --tags CostCenter=Engineering,Owner=PlatformTeam

# List tags for EKS resource
aws eks list-tags-for-resource \
  --resource-arn arn:aws:eks:us-east-1:123456789012:cluster/production-eks

# Untag EKS resource
aws eks untag-resource \
  --resource-arn arn:aws:eks:us-east-1:123456789012:cluster/production-eks \
  --tag-keys CostCenter
```

### Kubernetes Operations on EKS

```bash
# After configuring kubeconfig, use kubectl commands

# Get cluster info
kubectl cluster-info

# Get nodes
kubectl get nodes

# Get all resources
kubectl get all --all-namespaces

# Deploy application
kubectl apply -f deployment.yaml

# Create namespace
kubectl create namespace production

# Deploy to specific namespace
kubectl apply -f deployment.yaml -n production

# Scale deployment
kubectl scale deployment web-app --replicas=5 -n production

# Update deployment image
kubectl set image deployment/web-app web-container=123456789012.dkr.ecr.us-east-1.amazonaws.com/web-app:v2.0.0 -n production

# Rollout status
kubectl rollout status deployment/web-app -n production

# Rollback deployment
kubectl rollout undo deployment/web-app -n production

# Get pods
kubectl get pods -n production

# Get pod logs
kubectl logs -f pod-name -n production

# Execute command in pod
kubectl exec -it pod-name -n production -- /bin/bash

# Port forward
kubectl port-forward pod/pod-name 8080:80 -n production

# Get services
kubectl get services -n production

# Delete resources
kubectl delete -f deployment.yaml -n production
```

### Monitoring and Troubleshooting

```bash
# Get ECS cluster metrics (requires CloudWatch Container Insights)
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ClusterName,Value=production-cluster \
  --start-time 2026-02-08T00:00:00Z \
  --end-time 2026-02-08T23:59:59Z \
  --period 3600 \
  --statistics Average

# Get ECS service events
aws ecs describe-services \
  --cluster production-cluster \
  --services web-service \
  --query 'services[0].events[0:10]'

# List ECS container instances
aws ecs list-container-instances \
  --cluster production-cluster

# Describe container instances
aws ecs describe-container-instances \
  --cluster production-cluster \
  --container-instances arn:aws:ecs:us-east-1:123456789012:container-instance/production-cluster/1234567890abcdef

# Get EKS cluster health
kubectl get componentstatuses

# Get EKS node status
kubectl describe nodes

# View EKS cluster logs (Control Plane)
aws logs tail /aws/eks/production-eks/cluster --follow

# Get ECR image vulnerabilities
aws ecr describe-image-scan-findings \
  --repository-name web-app \
  --image-id imageTag=latest \
  --query 'imageScanFindings.findings[?severity==`CRITICAL` || severity==`HIGH`]'
```

---

## SAA-C03 Exam Tips

### Key Concepts to Remember

1. **ECS Task Definition** = Blueprint, **Task** = Running instance
2. **Fargate** = Serverless compute for both ECS and EKS
3. **awsvpc** = Required network mode for Fargate
4. **Task Execution Role** = Pull images, write logs
5. **Task Role** = Application permissions for AWS services

### Common Exam Scenarios

#### Scenario 1: Microservices with Auto Scaling
**Question**: Company needs to run containerized microservices with automatic scaling based on CPU.
**Answer**: ECS with Fargate + Application Auto Scaling + Target Tracking (CPU)

#### Scenario 2: GPU Machine Learning Workloads
**Question**: Run containerized ML training with GPU support.
**Answer**: ECS or EKS with EC2 launch type (P3 or P4 instances)

#### Scenario 3: Kubernetes Portability
**Question**: Run containers that can move between AWS and on-premises.
**Answer**: Amazon EKS (Kubernetes compatibility)

#### Scenario 4: Serverless Containers
**Question**: Run containers without managing servers, variable workload.
**Answer**: AWS Fargate with ECS or EKS

#### Scenario 5: Cost-Optimized Batch Processing
**Question**: Run fault-tolerant batch jobs at lowest cost.
**Answer**: ECS with Fargate Spot or EC2 Spot instances

### Default Values to Remember

| Setting | Default Value |
|---------|---------------|
| Fargate platform version | LATEST |
| Service desired count | 1 |
| Deployment max percent | 200% |
| Deployment min healthy | 100% |
| EKS control plane HA | Multi-AZ (automatic) |
| Fargate ephemeral storage | 20 GB |

### Exam Question Keywords

- "Serverless containers" → **Fargate**
- "Kubernetes" → **EKS**
- "AWS native containers" → **ECS**
- "GPU support" → **EC2 launch type**
- "No infrastructure management" → **Fargate**
- "Spot pricing for containers" → **Fargate Spot** or **EC2 Spot**
- "Service mesh" → **App Mesh**

---

## Practice Questions

### Question 1
A company wants to run containerized applications without managing servers. The workload varies throughout the day and needs automatic scaling. Which solution provides the MOST operational efficiency?

A) ECS with EC2 launch type and Auto Scaling  
B) ECS with Fargate launch type and Application Auto Scaling  
C) EKS with managed node groups  
D) EC2 instances with Docker installed  

**Answer: B** - Fargate provides serverless container execution with no infrastructure management, and Application Auto Scaling handles the variable workload.

### Question 2
A company runs Kubernetes workloads on-premises and wants to migrate to AWS while maintaining the ability to move back if needed. Which service should they use?

A) Amazon ECS  
B) Amazon EKS  
C) AWS Fargate  
D) AWS Elastic Beanstalk  

**Answer: B** - EKS provides managed Kubernetes, which maintains compatibility with on-premises Kubernetes clusters for portability.

### Question 3
An application running on ECS needs to access objects in S3 and items in DynamoDB. What is the RECOMMENDED way to grant these permissions?

A) Store AWS credentials in environment variables  
B) Use IAM instance role on the EC2 container instances  
C) Use IAM task role attached to the task definition  
D) Use IAM user access keys in the container  

**Answer: C** - Task roles provide fine-grained permissions per task and follow security best practices.

### Question 4
A company wants to run batch processing jobs on containers at the lowest possible cost. The jobs are fault-tolerant and can handle interruptions. Which option is MOST cost-effective?

A) ECS with Fargate On-Demand  
B) ECS with Fargate Spot  
C) EKS with On-Demand EC2 nodes  
D) ECS with Reserved Instances  

**Answer: B** - Fargate Spot provides up to 70% discount for fault-tolerant workloads.

### Question 5
A company needs to run Windows containers with GPU support for video processing. Which combination should they use?

A) ECS with Fargate  
B) EKS with Fargate  
C) ECS with EC2 launch type using GPU instances  
D) Lambda with container image support  

**Answer: C** - GPU support requires EC2 launch type; Fargate does not support GPUs.

---

## Summary

AWS Container Services provide flexible options for running containerized applications:

- **Amazon ECS**: AWS-native, easy to learn, no control plane cost
- **Amazon EKS**: Managed Kubernetes, portable, extensive ecosystem
- **AWS Fargate**: Serverless compute, works with both ECS and EKS

Key decisions for the exam:
1. **Serverless** → Fargate
2. **Kubernetes needed** → EKS
3. **AWS native preferred** → ECS
4. **GPU required** → EC2 launch type
5. **Cost optimization** → Spot instances (Fargate or EC2)

Remember: Fargate is a compute engine, not an orchestrator. It works WITH ECS or EKS, not instead of them.
