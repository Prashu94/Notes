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
16. [SAA-C03 Exam Tips](#saa-c03-exam-tips)
17. [Practice Questions](#practice-questions)

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
