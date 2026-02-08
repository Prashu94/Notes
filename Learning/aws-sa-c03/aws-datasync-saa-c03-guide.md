# AWS DataSync - SAA-C03 Comprehensive Guide

## Table of Contents
1. [Overview and Introduction](#overview-and-introduction)
2. [Architecture and Components](#architecture-and-components)
3. [Supported Storage Locations](#supported-storage-locations)
4. [DataSync Agents](#datasync-agents)
5. [Task Configuration](#task-configuration)
6. [Data Transfer and Filtering](#data-transfer-and-filtering)
7. [Security](#security)
8. [Monitoring and Logging](#monitoring-and-logging)
9. [Pricing and Cost Optimization](#pricing-and-cost-optimization)
10. [Common Use Cases](#common-use-cases)
11. [Best Practices](#best-practices)
12. [SAA-C03 Exam Tips](#saa-c03-exam-tips)
13. [AWS CLI Commands Reference](#aws-cli-commands-reference)
14. [Practice Questions](#practice-questions)

---

## Overview and Introduction

### What is AWS DataSync?

AWS DataSync is a **secure, online data transfer service** that simplifies, automates, and accelerates moving data between on-premises storage systems, edge locations, other clouds, and AWS storage services.

### Key Characteristics

- **High-speed transfer**: Up to 10 Gbps per task
- **Automated**: Handles scripting, scheduling, monitoring
- **Secure**: Encryption in-transit and at-rest
- **Fully managed**: No infrastructure to manage
- **Incremental**: Transfers only changed data

### Primary Use Cases

1. **Data migration**: Move data to AWS
2. **Data replication**: Replicate data for disaster recovery
3. **Cold data archiving**: Move infrequently accessed data to S3 Glacier
4. **Hybrid workflows**: Continuous sync between on-premises and cloud

### DataSync at a Glance

```
┌─────────────────────────────────────────────────────────────────┐
│                    AWS DataSync Overview                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Source                      DataSync               Target      │
│   Locations                   Service                Locations   │
│                                                                  │
│   ┌─────────────┐         ┌───────────────┐       ┌───────────┐│
│   │On-premises  │         │               │       │ Amazon S3 ││
│   │NFS/SMB/HDFS │────────►│   AWS         │──────►│ Amazon EFS││
│   │             │         │   DataSync    │       │ Amazon FSx││
│   └─────────────┘         │               │       │           ││
│                           │  • Automated  │       └───────────┘│
│   ┌─────────────┐         │  • Encrypted  │                     │
│   │ Amazon S3   │────────►│  • Fast       │       ┌───────────┐│
│   │ Amazon EFS  │         │  • Monitored  │──────►│On-premises││
│   │ Amazon FSx  │         │               │       │NFS/SMB    ││
│   └─────────────┘         └───────────────┘       └───────────┘│
│                                                                  │
│   ┌─────────────┐                                               │
│   │Other Clouds │                                               │
│   │(Azure, GCP) │─────────────────────────────────────────────►│
│   └─────────────┘                                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Architecture and Components

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                  DataSync Architecture                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   On-Premises / Edge                    AWS Cloud                │
│   ┌──────────────────────┐             ┌──────────────────────┐ │
│   │                      │             │                      │ │
│   │  ┌────────────────┐  │             │  ┌────────────────┐  │ │
│   │  │ Source Storage │  │             │  │    DataSync    │  │ │
│   │  │ (NFS/SMB/HDFS) │  │             │  │    Service     │  │ │
│   │  └───────┬────────┘  │             │  └───────┬────────┘  │ │
│   │          │           │             │          │           │ │
│   │          ▼           │             │          ▼           │ │
│   │  ┌────────────────┐  │  Internet/  │  ┌────────────────┐  │ │
│   │  │   DataSync     │  │   Direct    │  │ Target Storage │  │ │
│   │  │    Agent       │──┼─ Connect ──►│  │  (S3/EFS/FSx)  │  │ │
│   │  │   (VM)         │  │   VPN       │  │                │  │ │
│   │  └────────────────┘  │             │  └────────────────┘  │ │
│   │                      │             │                      │ │
│   └──────────────────────┘             └──────────────────────┘ │
│                                                                  │
│   Key Components:                                                │
│   • Agent: Software on-premises that reads/writes data          │
│   • Task: Transfer configuration (source, target, settings)     │
│   • Location: Source or destination storage endpoint            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Core Components

| Component | Description |
|-----------|-------------|
| **Agent** | VM deployed on-premises to read/write data |
| **Location** | Source or destination storage endpoint |
| **Task** | Transfer job configuration |
| **Task Execution** | Individual run of a task |

### Cloud-to-Cloud Transfer (No Agent)

```
┌─────────────────────────────────────────────────────────────────┐
│            DataSync Cloud-to-Cloud (Agentless)                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   AWS Cloud                                                      │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │                                                          │  │
│   │   ┌────────────┐       ┌────────────┐       ┌──────────┐│  │
│   │   │  Amazon S3 │       │  DataSync  │       │ Amazon   ││  │
│   │   │  (Source)  │──────►│  Service   │──────►│ EFS      ││  │
│   │   └────────────┘       └────────────┘       │ (Target) ││  │
│   │                                             └──────────┘│  │
│   │                                                          │  │
│   │   • No agent required for AWS-to-AWS transfers          │  │
│   │   • Direct service-to-service communication             │  │
│   │                                                          │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Supported Storage Locations

### Source and Destination Options

```
┌─────────────────────────────────────────────────────────────────┐
│              DataSync Supported Locations                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   On-Premises / Edge (Requires Agent):                          │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  • NFS (Network File System) v3, v4, v4.1               │  │
│   │  • SMB (Server Message Block) 2.1, 3.0, 3.1.1           │  │
│   │  • HDFS (Hadoop Distributed File System)                 │  │
│   │  • Self-managed object storage (S3-compatible API)       │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│   AWS Storage (No Agent Required):                               │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  • Amazon S3 (all storage classes)                       │  │
│   │  • Amazon EFS (Elastic File System)                      │  │
│   │  • Amazon FSx for Windows File Server                    │  │
│   │  • Amazon FSx for Lustre                                 │  │
│   │  • Amazon FSx for OpenZFS                                │  │
│   │  • Amazon FSx for NetApp ONTAP                           │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│   Other Clouds (Requires Agent):                                 │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  • Microsoft Azure Blob Storage                          │  │
│   │  • Microsoft Azure Files                                 │  │
│   │  • Google Cloud Storage                                  │  │
│   │  • Wasabi (S3-compatible)                                │  │
│   │  • Other S3-compatible object storage                    │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│   Edge Locations:                                                │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  • AWS Snowcone (built-in DataSync agent)               │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Transfer Direction Matrix

| Source | Target | Agent Required |
|--------|--------|----------------|
| On-premises NFS/SMB | S3/EFS/FSx | Yes |
| S3 | EFS/FSx | No |
| EFS | S3/FSx | No |
| FSx | S3/EFS | No |
| S3 | S3 (cross-region/account) | No |
| Azure Blob | S3/EFS/FSx | Yes (on Azure) |
| Google Cloud Storage | S3/EFS/FSx | Yes (on GCP) |

---

## DataSync Agents

### Agent Overview

The DataSync agent is a **VM deployed in your environment** that connects your storage to the DataSync service.

### Deployment Options

```
┌─────────────────────────────────────────────────────────────────┐
│               DataSync Agent Deployment                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   VMware ESXi:                                                   │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  • Download OVA from AWS console                         │  │
│   │  • Deploy on ESXi 6.5+                                   │  │
│   │  • Minimum: 4 vCPU, 32 GB RAM, 80 GB disk               │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│   Microsoft Hyper-V:                                             │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  • Download VHD from AWS console                         │  │
│   │  • Deploy on Hyper-V 2012 R2+                           │  │
│   │  • Same resource requirements as VMware                  │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│   KVM (Linux):                                                   │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  • Download QCOW2 image                                  │  │
│   │  • Deploy on KVM hypervisor                             │  │
│   │  • Same resource requirements                            │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│   Amazon EC2:                                                    │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  • Use AMI provided by AWS                               │  │
│   │  • Deploy in VPC for accessing EFS/FSx                   │  │
│   │  • Useful for cloud-to-cloud via VPC peering            │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│   AWS Snowcone:                                                  │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  • Built-in DataSync agent                               │  │
│   │  • No separate deployment needed                        │  │
│   │  • Edge computing + data transfer                       │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Agent Activation

```
┌─────────────────────────────────────────────────────────────────┐
│               Agent Activation Process                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   1. Deploy agent VM                                            │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  Deploy OVA/VHD/QCOW2 in your environment               │  │
│   └──────────────────────────────────────────────────────────┘  │
│                            ↓                                     │
│   2. Configure network                                          │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  • Agent needs outbound HTTPS (443) to AWS              │  │
│   │  • Activate via public or VPC endpoint                  │  │
│   └──────────────────────────────────────────────────────────┘  │
│                            ↓                                     │
│   3. Get activation key                                         │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  • Access agent on port 80 (HTTP)                       │  │
│   │  • Choose activation region                              │  │
│   │  • Get activation key or use redirect URL               │  │
│   └──────────────────────────────────────────────────────────┘  │
│                            ↓                                     │
│   4. Activate in AWS Console                                    │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  • Enter activation key in DataSync console             │  │
│   │  • Agent appears in console as "Online"                 │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Agent Network Requirements

| Direction | Port | Protocol | Purpose |
|-----------|------|----------|---------|
| Outbound | 443 | HTTPS | Control traffic to AWS |
| Outbound | 443 | TLS | Data transfer to AWS |
| Local | 80 | HTTP | Agent activation (temporary) |
| Local | 2049 | NFS | Connect to NFS storage |
| Local | 445 | SMB | Connect to SMB storage |

---

## Task Configuration

### Creating a DataSync Task

```
┌─────────────────────────────────────────────────────────────────┐
│                    Task Configuration                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Step 1: Configure Source Location                             │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  • Select agent (for on-premises)                        │  │
│   │  • Specify server/path (NFS: nfs://server/export)       │  │
│   │  • Configure mount options                               │  │
│   └──────────────────────────────────────────────────────────┘  │
│                            ↓                                     │
│   Step 2: Configure Destination Location                        │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  • Select S3 bucket / EFS / FSx                         │  │
│   │  • Configure S3 storage class                           │  │
│   │  • Specify IAM role for access                          │  │
│   └──────────────────────────────────────────────────────────┘  │
│                            ↓                                     │
│   Step 3: Configure Task Settings                               │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  • Verify options (checksums, timestamps)                │  │
│   │  • Copy options (metadata, permissions)                  │  │
│   │  • Bandwidth throttling                                  │  │
│   │  • Filtering (include/exclude patterns)                  │  │
│   │  • Scheduling                                            │  │
│   └──────────────────────────────────────────────────────────┘  │
│                            ↓                                     │
│   Step 4: Review and Create                                     │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  • Review configuration                                  │  │
│   │  • Add tags                                             │  │
│   │  • Create task                                          │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Task Options

| Option | Description |
|--------|-------------|
| **Verify mode** | Check data integrity (checksum comparison) |
| **Overwrite mode** | Always, never, or only if different |
| **Preserve metadata** | Timestamps, permissions, ownership |
| **Bandwidth limit** | Throttle transfer speed (bytes/sec) |
| **Task queueing** | Queue executions when task is running |

### Scheduling Options

- **On-demand**: Manual start
- **Scheduled**: Cron-like expressions
- **Hourly/Daily/Weekly**: Preset schedules

```
# Schedule Examples
Rate(1 hour)           # Every hour
Rate(1 day)            # Every day
Cron(0 12 * * ? *)     # Daily at noon UTC
Cron(0 0 ? * SUN *)    # Every Sunday at midnight
```

---

## Data Transfer and Filtering

### Transfer Process

```
┌─────────────────────────────────────────────────────────────────┐
│                  DataSync Transfer Process                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Phase 1: PREPARING                                             │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  • Scans source and destination                          │  │
│   │  • Compares files (size, timestamps, checksums)          │  │
│   │  • Identifies what needs to be transferred               │  │
│   └──────────────────────────────────────────────────────────┘  │
│                            ↓                                     │
│   Phase 2: TRANSFERRING                                          │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  • Transfers new/changed files                          │  │
│   │  • Uses multiple parallel streams                       │  │
│   │  • Compresses data in-transit                           │  │
│   │  • Encrypts with TLS                                    │  │
│   └──────────────────────────────────────────────────────────┘  │
│                            ↓                                     │
│   Phase 3: VERIFYING                                             │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  • Verifies transferred data (based on verify mode)     │  │
│   │  • Compares checksums                                   │  │
│   │  • Reports any discrepancies                            │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│   Transfer Optimizations:                                        │
│   • Only changed data is transferred (incremental)              │
│   • Parallel streams for high throughput                        │
│   • In-transit compression                                      │
│   • Protocol optimization                                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Filtering

Include and exclude files using patterns:

```
┌─────────────────────────────────────────────────────────────────┐
│                    DataSync Filtering                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Include Patterns:                                              │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  /data/*          # Everything in /data/                 │  │
│   │  *.csv            # All CSV files                        │  │
│   │  /logs/2024*      # Files starting with 2024 in logs/   │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│   Exclude Patterns:                                              │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  *.tmp            # Exclude temp files                   │  │
│   │  /cache/*         # Exclude cache directory             │  │
│   │  *.log            # Exclude log files                   │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│   Evaluation Order:                                              │
│   1. Include patterns evaluated first                           │
│   2. Exclude patterns applied to included files                 │
│   3. Result: Transfer = Include - Exclude                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### S3 Storage Class Selection

Transfer directly to any S3 storage class:

| Storage Class | Use Case |
|---------------|----------|
| **S3 Standard** | Frequently accessed data |
| **S3 Standard-IA** | Infrequently accessed |
| **S3 One Zone-IA** | Infrequent, single AZ |
| **S3 Glacier Instant** | Archive with instant retrieval |
| **S3 Glacier Flexible** | Archive (minutes to hours) |
| **S3 Glacier Deep Archive** | Long-term archive |
| **S3 Intelligent-Tiering** | Unknown access patterns |

---

## Security

### Encryption

```
┌─────────────────────────────────────────────────────────────────┐
│                   DataSync Security                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Encryption In-Transit:                                         │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  • TLS 1.2 encryption for all data transfers            │  │
│   │  • Agent to AWS communication encrypted                 │  │
│   │  • Cannot be disabled                                   │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│   Encryption At-Rest (Destination):                              │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  S3:                                                     │  │
│   │  • SSE-S3 (AES-256)                                     │  │
│   │  • SSE-KMS (customer managed key)                       │  │
│   │                                                          │  │
│   │  EFS:                                                    │  │
│   │  • Encryption at rest using KMS                         │  │
│   │                                                          │  │
│   │  FSx:                                                    │  │
│   │  • Encryption at rest using KMS                         │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│   Network Security:                                              │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  • VPC endpoints (PrivateLink) for private transfer     │  │
│   │  • No public internet exposure required                 │  │
│   │  • Security groups for agent access control             │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### IAM Permissions

DataSync requires IAM roles for:
- Reading from source (S3/EFS/FSx)
- Writing to destination
- CloudWatch logging

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetBucketLocation",
                "s3:ListBucket",
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject"
            ],
            "Resource": [
                "arn:aws:s3:::destination-bucket",
                "arn:aws:s3:::destination-bucket/*"
            ]
        }
    ]
}
```

### VPC Endpoint (PrivateLink)

```
┌─────────────────────────────────────────────────────────────────┐
│              DataSync with VPC Endpoint                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   On-Premises                               AWS Cloud            │
│   ┌──────────────┐                         ┌──────────────────┐ │
│   │              │                         │      VPC         │ │
│   │  ┌────────┐  │    Direct Connect/VPN   │  ┌────────────┐  │ │
│   │  │ Agent  │──┼─────────────────────────┼─►│ VPC        │  │ │
│   │  └────────┘  │                         │  │ Endpoint   │  │ │
│   │              │                         │  │ (DataSync) │  │ │
│   └──────────────┘                         │  └─────┬──────┘  │ │
│                                            │        │         │ │
│                                            │        ▼         │ │
│                                            │  ┌────────────┐  │ │
│                                            │  │  DataSync  │  │ │
│                                            │  │  Service   │  │ │
│                                            │  └────────────┘  │ │
│                                            └──────────────────┘ │
│                                                                  │
│   Benefits:                                                      │
│   • Data stays on private network                               │
│   • No internet exposure                                        │
│   • Lower latency                                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Monitoring and Logging

### CloudWatch Metrics

| Metric | Description |
|--------|-------------|
| **BytesTransferred** | Total bytes transferred |
| **FilesTransferred** | Number of files transferred |
| **BytesVerifiedSource** | Bytes verified at source |
| **BytesVerifiedDestination** | Bytes verified at destination |

### CloudWatch Logs

Enable detailed logging for:
- Transfer progress
- File-level details
- Errors and warnings
- Performance metrics

```
┌─────────────────────────────────────────────────────────────────┐
│               DataSync Monitoring Options                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   CloudWatch Metrics (Automatic):                                │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  • Transfer throughput                                   │  │
│   │  • Files/bytes transferred                              │  │
│   │  • Verification status                                   │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│   CloudWatch Logs (Optional):                                    │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  Log Levels:                                             │  │
│   │  • OFF: No logging                                      │  │
│   │  • BASIC: Task status only                              │  │
│   │  • TRANSFER: File transfer details                      │  │
│   │                                                          │  │
│   │  Log Content:                                            │  │
│   │  • Individual file transfer status                      │  │
│   │  • Verification results                                  │  │
│   │  • Error details                                        │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│   EventBridge (Events):                                          │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  • Task state changes                                   │  │
│   │  • Task execution completion                            │  │
│   │  • Use for automation/notifications                     │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Pricing and Cost Optimization

### Pricing Model

| Component | Price |
|-----------|-------|
| **Data transferred** | $0.0125 per GB (varies by region) |
| **Agent** | No charge for agent software |
| **Scheduling** | No additional charge |

### Cost Factors

- Data transferred (GB)
- Number of transfers
- Data transfer out fees (if cross-region)
- S3/EFS/FSx storage costs

### Cost Optimization Tips

1. **Incremental transfers**: Only changed data is charged
2. **Compression**: Data is compressed in-transit automatically
3. **Filtering**: Exclude unnecessary files
4. **Scheduling**: Optimize transfer frequency
5. **Direct transfer to Glacier**: Lower storage costs

### Cost Comparison Example

```
┌─────────────────────────────────────────────────────────────────┐
│                    Cost Comparison                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Scenario: Transfer 10 TB from on-premises to S3               │
│                                                                  │
│   DataSync:                                                      │
│   • Transfer cost: 10,000 GB × $0.0125 = $125                   │
│   • S3 storage: Variable based on class                         │
│   • Total: ~$125 for transfer                                   │
│                                                                  │
│   DIY (EC2 + scripts):                                          │
│   • EC2 instance: ~$50-200/month                                │
│   • Data transfer: Similar                                      │
│   • Development time: Significant                               │
│   • Maintenance: Ongoing                                        │
│                                                                  │
│   Snowball (for comparison):                                     │
│   • Service fee: $300                                           │
│   • Useful for: > 50 TB or limited bandwidth                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Common Use Cases

### Use Case 1: Data Migration

```
┌─────────────────────────────────────────────────────────────────┐
│              Data Migration to AWS                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   On-Premises NAS                          Amazon S3             │
│   ┌──────────────────┐                    ┌──────────────────┐  │
│   │                  │                    │                  │  │
│   │  ┌────────────┐  │    DataSync        │  Data Lake       │  │
│   │  │ File Data  │──┼───────────────────►│  ┌────────────┐  │  │
│   │  │ 100 TB     │  │   (incremental)    │  │ S3 Buckets │  │  │
│   │  └────────────┘  │                    │  └────────────┘  │  │
│   │                  │                    │                  │  │
│   └──────────────────┘                    └──────────────────┘  │
│                                                                  │
│   Workflow:                                                      │
│   1. Deploy DataSync agent on-premises                          │
│   2. Initial full transfer (bulk migration)                     │
│   3. Schedule incremental syncs (catch changes)                 │
│   4. Final sync before cutover                                  │
│   5. Cutover applications to use S3                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Use Case 2: Hybrid Cloud Workflows

```
┌─────────────────────────────────────────────────────────────────┐
│              Hybrid Cloud Data Processing                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌────────────────────────────────────────────────────────┐    │
│   │                                                        │    │
│   │   On-Premises               AWS Cloud                  │    │
│   │   ┌──────────┐             ┌──────────────────────┐   │    │
│   │   │ Data     │  DataSync   │       S3             │   │    │
│   │   │ Creation │────────────►│                      │   │    │
│   │   └──────────┘  (nightly)  │        │             │   │    │
│   │                            │        ▼             │   │    │
│   │                            │   ┌──────────┐       │   │    │
│   │                            │   │ Analytics│       │   │    │
│   │                            │   │ (EMR/    │       │   │    │
│   │                            │   │  Athena) │       │   │    │
│   │                            │   └──────────┘       │   │    │
│   │                            │        │             │   │    │
│   │   ┌──────────┐  DataSync   │        ▼             │   │    │
│   │   │ Consume  │◄────────────│   ┌──────────┐       │   │    │
│   │   │ Results  │  (results)  │   │ Results  │       │   │    │
│   │   └──────────┘             │   └──────────┘       │   │    │
│   │                            └──────────────────────┘   │    │
│   │                                                        │    │
│   └────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Use Case 3: Disaster Recovery

```
┌─────────────────────────────────────────────────────────────────┐
│              Disaster Recovery Replication                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Primary Site                          DR Site (AWS)            │
│   ┌──────────────────┐                 ┌──────────────────┐     │
│   │                  │                 │                  │     │
│   │  ┌────────────┐  │    DataSync     │  ┌────────────┐  │     │
│   │  │ Production │  │    (hourly)     │  │  DR Copy   │  │     │
│   │  │    Data    │──┼────────────────►│  │ (S3/EFS)  │  │     │
│   │  └────────────┘  │                 │  └────────────┘  │     │
│   │                  │                 │                  │     │
│   └──────────────────┘                 └──────────────────┘     │
│                                                                  │
│   RPO (Recovery Point Objective):                               │
│   • Depends on sync frequency                                   │
│   • Hourly sync = up to 1 hour data loss                       │
│                                                                  │
│   RTO (Recovery Time Objective):                                │
│   • Fast recovery with data already in AWS                     │
│   • Spin up compute as needed                                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Use Case 4: Cold Data Archival

Transfer infrequently accessed data directly to S3 Glacier:

```
On-Premises ──► DataSync ──► S3 Glacier Deep Archive
  (NAS)           (Task)      (Long-term storage)
```

---

## Best Practices

### Performance Optimization

1. **Use multiple agents** for parallel transfers
2. **Position agent close to data** (same datacenter/rack)
3. **Ensure adequate network bandwidth**
4. **Use Direct Connect** for consistent performance
5. **Enable compression** (default)

### Security

1. **Use VPC endpoints** for private transfers
2. **Enable encryption** at destination (KMS)
3. **Least privilege IAM roles**
4. **Monitor with CloudWatch**
5. **Enable CloudWatch Logs** for auditing

### Cost Management

1. **Use filtering** to exclude unnecessary files
2. **Schedule during off-peak** hours
3. **Leverage incremental** transfers
4. **Transfer directly to** appropriate S3 storage class
5. **Monitor transfer** metrics

---

## SAA-C03 Exam Tips

### Key Concepts

1. **DataSync = Online data transfer** service
2. **Agent required** for on-premises/other clouds
3. **No agent** for AWS-to-AWS transfers
4. **Incremental** transfers (only changed data)
5. **Up to 10 Gbps** throughput per task

### Common Exam Scenarios

#### Scenario 1: Migrate NFS to S3
**Question**: Move large NFS file share to S3.
**Answer**: AWS DataSync with agent on-premises

#### Scenario 2: Continuous Replication
**Question**: Replicate on-premises data to AWS for DR.
**Answer**: DataSync with scheduled tasks

#### Scenario 3: S3 to EFS Transfer
**Question**: Move data from S3 to EFS.
**Answer**: DataSync (no agent required)

#### Scenario 4: Azure to AWS
**Question**: Migrate data from Azure Blob to S3.
**Answer**: DataSync with agent deployed on Azure VM

### Exam Question Keywords

| Keyword | Usually Points To |
|---------|------------------|
| "Transfer data to AWS" | DataSync or Snow Family |
| "NFS to S3" | DataSync |
| "Replicate on-premises to cloud" | DataSync |
| "Automated data migration" | DataSync |
| "Incremental sync" | DataSync |
| "Online data transfer" | DataSync |

### DataSync vs Other Services

```
┌─────────────────────────────────────────────────────────────────┐
│              Service Selection Guide                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   DataSync vs Snow Family:                                      │
│   • DataSync: Online, network-based, continuous                 │
│   • Snow: Offline, physical devices, large/disconnected        │
│                                                                  │
│   DataSync vs S3 Transfer Acceleration:                         │
│   • DataSync: Bulk transfer, scheduled, NFS/SMB support        │
│   • Transfer Acceleration: S3 uploads, edge locations          │
│                                                                  │
│   DataSync vs Storage Gateway:                                  │
│   • DataSync: Migration, replication, one-way transfers        │
│   • Storage Gateway: Hybrid storage, ongoing access            │
│                                                                  │
│   DataSync vs AWS Transfer Family:                              │
│   • DataSync: Bulk file transfer, scheduled                    │
│   • Transfer Family: SFTP/FTPS/FTP access to S3               │
│                                                                  │
│   Decision Matrix:                                               │
│   • Online migration → DataSync                                 │
│   • Offline/large migration → Snowball                         │
│   • Hybrid storage access → Storage Gateway                    │
│   • SFTP to S3 → Transfer Family                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## AWS CLI Commands Reference

### Creating DataSync Locations

#### Amazon S3 Location
```bash
# Create an S3 location
aws datasync create-location-s3 \
  --s3-bucket-arn arn:aws:s3:::my-datasync-bucket \
  --s3-storage-class STANDARD \
  --s3-config BucketAccessRoleArn=arn:aws:iam::123456789012:role/DataSyncS3Role \
  --subdirectory /data/migration \
  --tags Key=Environment,Value=Production Key=Project,Value=Migration

# Create S3 location with specific storage class
aws datasync create-location-s3 \
  --s3-bucket-arn arn:aws:s3:::archive-bucket \
  --s3-storage-class GLACIER_INSTANT_RETRIEVAL \
  --s3-config BucketAccessRoleArn=arn:aws:iam::123456789012:role/DataSyncS3Role
```

#### Amazon EFS Location
```bash
# Create an EFS location
aws datasync create-location-efs \
  --efs-filesystem-arn arn:aws:elasticfilesystem:us-east-1:123456789012:file-system/fs-1234567 \
  --ec2-config SubnetArn=arn:aws:ec2:us-east-1:123456789012:subnet/subnet-12345678,SecurityGroupArns=arn:aws:ec2:us-east-1:123456789012:security-group/sg-12345678 \
  --subdirectory /mount-path \
  --tags Key=Environment,Value=Production

# Create EFS location with in-transit encryption
aws datasync create-location-efs \
  --efs-filesystem-arn arn:aws:elasticfilesystem:us-east-1:123456789012:file-system/fs-1234567 \
  --ec2-config SubnetArn=arn:aws:ec2:us-east-1:123456789012:subnet/subnet-12345678,SecurityGroupArns=arn:aws:ec2:us-east-1:123456789012:security-group/sg-12345678 \
  --in-transit-encryption TLS1_2
```

#### Amazon FSx for Windows File Server Location
```bash
# Create FSx for Windows location
aws datasync create-location-fsx-windows \
  --fsx-filesystem-arn arn:aws:fsx:us-east-1:123456789012:file-system/fs-0123456789abcdef0 \
  --security-group-arns arn:aws:ec2:us-east-1:123456789012:security-group/sg-12345678 \
  --user administrator \
  --password "YourSecurePassword" \
  --domain example.com \
  --subdirectory /share/data
```

#### Amazon FSx for Lustre Location
```bash
# Create FSx for Lustre location
aws datasync create-location-fsx-lustre \
  --fsx-filesystem-arn arn:aws:fsx:us-east-1:123456789012:file-system/fs-0123456789abcdef0 \
  --security-group-arns arn:aws:ec2:us-east-1:123456789012:security-group/sg-12345678 \
  --subdirectory /mount \
  --tags Key=Project,Value=HPC
```

#### NFS Location
```bash
# Create on-premises NFS location
aws datasync create-location-nfs \
  --server-hostname nfs-server.example.com \
  --subdirectory /exports/data \
  --on-prem-config AgentArns=arn:aws:datasync:us-east-1:123456789012:agent/agent-01234567890abcdef \
  --mount-options Version=NFS3,RSize=65536,WSize=65536 \
  --tags Key=Environment,Value=OnPremises

# Create NFS location with NFS4 and specific mount options
aws datasync create-location-nfs \
  --server-hostname 10.0.1.50 \
  --subdirectory /data/shared \
  --on-prem-config AgentArns=arn:aws:datasync:us-east-1:123456789012:agent/agent-01234567890abcdef \
  --mount-options Version=NFS4_1,RSize=1048576,WSize=1048576,HardMount=true
```

#### SMB Location
```bash
# Create SMB location
aws datasync create-location-smb \
  --server-hostname smb-server.example.com \
  --subdirectory /share/data \
  --user "DOMAIN\\username" \
  --password "YourSecurePassword" \
  --agent-arns arn:aws:datasync:us-east-1:123456789012:agent/agent-01234567890abcdef \
  --mount-options Version=SMB3,RSize=65536,WSize=65536 \
  --domain example.com
```

#### HDFS Location
```bash
# Create HDFS location
aws datasync create-location-hdfs \
  --name-nodes NameNode=hdfs-namenode.example.com,Port=8020 \
  --subdirectory /data/warehouse \
  --agent-arns arn:aws:datasync:us-east-1:123456789012:agent/agent-01234567890abcdef \
  --authentication-type SIMPLE \
  --simple-user hadoop \
  --block-size 134217728 \
  --replication-factor 3

# Create HDFS location with Kerberos authentication
aws datasync create-location-hdfs \
  --name-nodes NameNode=hdfs-namenode.example.com,Port=8020 \
  --subdirectory /user/data \
  --agent-arns arn:aws:datasync:us-east-1:123456789012:agent/agent-01234567890abcdef \
  --authentication-type KERBEROS \
  --kerberos-principal datasync/datasync.example.com@EXAMPLE.COM \
  --kerberos-keytab file://path/to/keytab \
  --kerberos-krb5-conf file://path/to/krb5.conf
```

#### Object Storage Location
```bash
# Create object storage location (S3-compatible)
aws datasync create-location-object-storage \
  --server-hostname s3-compatible.example.com \
  --server-port 443 \
  --server-protocol HTTPS \
  --subdirectory /bucket/prefix \
  --bucket-name my-bucket \
  --access-key AKIAIOSFODNN7EXAMPLE \
  --secret-key "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY" \
  --agent-arns arn:aws:datasync:us-east-1:123456789012:agent/agent-01234567890abcdef
```

### Managing DataSync Agents

#### Create and Activate Agent
```bash
# Get agent activation key (after deploying agent VM/appliance)
# Agent provides activation key via web interface at http://agent-ip/?gatewayType=SYNC

# Activate agent
aws datasync create-agent \
  --activation-key ABCDE-12345-FGHIJ-67890-KLMNO \
  --agent-name "Production-DataSync-Agent" \
  --vpc-endpoint-id vpce-1234567890abcdef0 \
  --subnet-arns arn:aws:ec2:us-east-1:123456789012:subnet/subnet-12345678 \
  --security-group-arns arn:aws:ec2:us-east-1:123456789012:security-group/sg-12345678 \
  --tags Key=Environment,Value=Production

# List all agents
aws datasync list-agents

# Describe specific agent
aws datasync describe-agent \
  --agent-arn arn:aws:datasync:us-east-1:123456789012:agent/agent-01234567890abcdef

# Update agent name
aws datasync update-agent \
  --agent-arn arn:aws:datasync:us-east-1:123456789012:agent/agent-01234567890abcdef \
  --name "Production-Agent-Updated"

# Delete agent
aws datasync delete-agent \
  --agent-arn arn:aws:datasync:us-east-1:123456789012:agent/agent-01234567890abcdef
```

### Creating and Managing Tasks

#### Create Basic Task
```bash
# Create a simple sync task from NFS to S3
aws datasync create-task \
  --source-location-arn arn:aws:datasync:us-east-1:123456789012:location/loc-0123456789abcdef0 \
  --destination-location-arn arn:aws:datasync:us-east-1:123456789012:location/loc-0123456789abcdef1 \
  --name "NFS-to-S3-Migration" \
  --cloud-watch-log-group-arn arn:aws:logs:us-east-1:123456789012:log-group:/aws/datasync \
  --tags Key=Project,Value=Migration Key=Environment,Value=Production
```

#### Create Task with Options
```bash
# Create task with comprehensive options
aws datasync create-task \
  --source-location-arn arn:aws:datasync:us-east-1:123456789012:location/loc-0123456789abcdef0 \
  --destination-location-arn arn:aws:datasync:us-east-1:123456789012:location/loc-0123456789abcdef1 \
  --name "Advanced-Sync-Task" \
  --options '{
    "VerifyMode": "POINT_IN_TIME_CONSISTENT",
    "OverwriteMode": "ALWAYS",
    "Atime": "BEST_EFFORT",
    "Mtime": "PRESERVE",
    "Uid": "INT_VALUE",
    "Gid": "INT_VALUE",
    "PreserveDeletedFiles": "PRESERVE",
    "PreserveDevices": "NONE",
    "PosixPermissions": "PRESERVE",
    "BytesPerSecond": 104857600,
    "TaskQueueing": "ENABLED",
    "LogLevel": "TRANSFER",
    "TransferMode": "CHANGED",
    "SecurityDescriptorCopyFlags": "OWNER_DACL",
    "ObjectTags": "PRESERVE"
  }' \
  --cloud-watch-log-group-arn arn:aws:logs:us-east-1:123456789012:log-group:/aws/datasync
```

#### Create Task with File Filters
```bash
# Create task with include/exclude filters
aws datasync create-task \
  --source-location-arn arn:aws:datasync:us-east-1:123456789012:location/loc-0123456789abcdef0 \
  --destination-location-arn arn:aws:datasync:us-east-1:123456789012:location/loc-0123456789abcdef1 \
  --name "Filtered-Sync-Task" \
  --excludes FilterType=SIMPLE_PATTERN,Value="*.tmp" FilterType=SIMPLE_PATTERN,Value=".git/*" \
  --includes FilterType=SIMPLE_PATTERN,Value="*.jpg" FilterType=SIMPLE_PATTERN,Value="*.png"

# Create task excluding specific directories and file types
aws datasync create-task \
  --source-location-arn arn:aws:datasync:us-east-1:123456789012:location/loc-0123456789abcdef0 \
  --destination-location-arn arn:aws:datasync:us-east-1:123456789012:location/loc-0123456789abcdef1 \
  --name "Production-Backup" \
  --excludes \
    FilterType=SIMPLE_PATTERN,Value="/temp/*" \
    FilterType=SIMPLE_PATTERN,Value="/cache/*" \
    FilterType=SIMPLE_PATTERN,Value="*.log" \
    FilterType=SIMPLE_PATTERN,Value="*.tmp"
```

#### Create Task with Schedule
```bash
# Create task with hourly schedule
aws datasync create-task \
  --source-location-arn arn:aws:datasync:us-east-1:123456789012:location/loc-0123456789abcdef0 \
  --destination-location-arn arn:aws:datasync:us-east-1:123456789012:location/loc-0123456789abcdef1 \
  --name "Scheduled-Hourly-Sync" \
  --schedule ScheduleExpression="cron(0 * * * ? *)" \
  --cloud-watch-log-group-arn arn:aws:logs:us-east-1:123456789012:log-group:/aws/datasync

# Create task with daily schedule at 2 AM
aws datasync create-task \
  --source-location-arn arn:aws:datasync:us-east-1:123456789012:location/loc-0123456789abcdef0 \
  --destination-location-arn arn:aws:datasync:us-east-1:123456789012:location/loc-0123456789abcdef1 \
  --name "Daily-Backup" \
  --schedule ScheduleExpression="cron(0 2 * * ? *)"

# Create task with weekly schedule (every Sunday at 3 AM)
aws datasync create-task \
  --source-location-arn arn:aws:datasync:us-east-1:123456789012:location/loc-0123456789abcdef0 \
  --destination-location-arn arn:aws:datasync:us-east-1:123456789012:location/loc-0123456789abcdef1 \
  --name "Weekly-Archive" \
  --schedule ScheduleExpression="cron(0 3 ? * SUN *)"
```

#### List and Describe Tasks
```bash
# List all tasks
aws datasync list-tasks

# List tasks with filters
aws datasync list-tasks \
  --filters Name=LocationId,Values=loc-0123456789abcdef0,Operator=Equals

# Describe specific task
aws datasync describe-task \
  --task-arn arn:aws:datasync:us-east-1:123456789012:task/task-0123456789abcdef0

# Update task options
aws datasync update-task \
  --task-arn arn:aws:datasync:us-east-1:123456789012:task/task-0123456789abcdef0 \
  --name "Updated-Task-Name" \
  --options VerifyMode=ONLY_FILES_TRANSFERRED,TransferMode=CHANGED,LogLevel=TRANSFER

# Update task schedule
aws datasync update-task \
  --task-arn arn:aws:datasync:us-east-1:123456789012:task/task-0123456789abcdef0 \
  --schedule ScheduleExpression="cron(0 4 * * ? *)"

# Delete task
aws datasync delete-task \
  --task-arn arn:aws:datasync:us-east-1:123456789012:task/task-0123456789abcdef0
```

### Task Execution

#### Start Task Execution
```bash
# Start immediate task execution
aws datasync start-task-execution \
  --task-arn arn:aws:datasync:us-east-1:123456789012:task/task-0123456789abcdef0

# Start task execution with specific options override
aws datasync start-task-execution \
  --task-arn arn:aws:datasync:us-east-1:123456789012:task/task-0123456789abcdef0 \
  --override-options VerifyMode=NONE,LogLevel=BASIC,TransferMode=ALL

# Start task execution with includes/excludes override
aws datasync start-task-execution \
  --task-arn arn:aws:datasync:us-east-1:123456789012:task/task-0123456789abcdef0 \
  --includes FilterType=SIMPLE_PATTERN,Value="*.pdf" \
  --excludes FilterType=SIMPLE_PATTERN,Value="*.tmp"
```

#### Monitor Task Executions
```bash
# List task executions for a specific task
aws datasync list-task-executions \
  --task-arn arn:aws:datasync:us-east-1:123456789012:task/task-0123456789abcdef0

# List task executions with max results
aws datasync list-task-executions \
  --task-arn arn:aws:datasync:us-east-1:123456789012:task/task-0123456789abcdef0 \
  --max-results 10

# Describe specific task execution
aws datasync describe-task-execution \
  --task-execution-arn arn:aws:datasync:us-east-1:123456789012:task/task-0123456789abcdef0/execution/exec-0123456789abcdef0

# Get detailed status of running execution
aws datasync describe-task-execution \
  --task-execution-arn arn:aws:datasync:us-east-1:123456789012:task/task-0123456789abcdef0/execution/exec-0123456789abcdef0 \
  --query '{Status:Status,BytesTransferred:BytesTransferred,FilesTransferred:FilesTransferred,Result:Result}'
```

#### Cancel Task Execution
```bash
# Cancel running task execution
aws datasync cancel-task-execution \
  --task-execution-arn arn:aws:datasync:us-east-1:123456789012:task/task-0123456789abcdef0/execution/exec-0123456789abcdef0
```

### Schedule Expressions Reference

```bash
# Common schedule expressions (cron format)

# Every hour
cron(0 * * * ? *)

# Every 6 hours
cron(0 */6 * * ? *)

# Every day at 2:00 AM
cron(0 2 * * ? *)

# Every weekday at 6:00 AM
cron(0 6 ? * MON-FRI *)

# Every Sunday at 3:00 AM
cron(0 3 ? * SUN *)

# First day of every month at midnight
cron(0 0 1 * ? *)

# Every 15 minutes
cron(0/15 * * * ? *)

# Twice daily (6 AM and 6 PM)
cron(0 6,18 * * ? *)
```

### Managing Tags

```bash
# Add tags to a task
aws datasync tag-resource \
  --resource-arn arn:aws:datasync:us-east-1:123456789012:task/task-0123456789abcdef0 \
  --tags Key=CostCenter,Value=Engineering Key=Owner,Value=DataTeam

# List tags for a resource
aws datasync list-tags-for-resource \
  --resource-arn arn:aws:datasync:us-east-1:123456789012:task/task-0123456789abcdef0

# Remove tags from a resource
aws datasync untag-resource \
  --resource-arn arn:aws:datasync:us-east-1:123456789012:task/task-0123456789abcdef0 \
  --tag-keys CostCenter Owner
```

### CloudWatch Logging

```bash
# Create CloudWatch log group for DataSync
aws logs create-log-group \
  --log-group-name /aws/datasync

# Set retention policy (7 days)
aws logs put-retention-policy \
  --log-group-name /aws/datasync \
  --retention-in-days 7

# Update task with CloudWatch logging
aws datasync update-task \
  --task-arn arn:aws:datasync:us-east-1:123456789012:task/task-0123456789abcdef0 \
  --cloud-watch-log-group-arn arn:aws:logs:us-east-1:123456789012:log-group:/aws/datasync

# Query CloudWatch logs for task execution
aws logs filter-log-events \
  --log-group-name /aws/datasync \
  --filter-pattern "task-0123456789abcdef0" \
  --start-time 1640000000000

# Get log streams for DataSync
aws logs describe-log-streams \
  --log-group-name /aws/datasync \
  --order-by LastEventTime \
  --descending \
  --max-items 10
```

### Advanced Task Options

```bash
# Task with bandwidth throttling (100 MB/s)
aws datasync create-task \
  --source-location-arn arn:aws:datasync:us-east-1:123456789012:location/loc-source \
  --destination-location-arn arn:aws:datasync:us-east-1:123456789012:location/loc-dest \
  --name "Throttled-Task" \
  --options BytesPerSecond=104857600

# Task with verification disabled for speed
aws datasync create-task \
  --source-location-arn arn:aws:datasync:us-east-1:123456789012:location/loc-source \
  --destination-location-arn arn:aws:datasync:us-east-1:123456789012:location/loc-dest \
  --name "Fast-Transfer" \
  --options VerifyMode=NONE,TransferMode=CHANGED

# Task that preserves deleted files
aws datasync create-task \
  --source-location-arn arn:aws:datasync:us-east-1:123456789012:location/loc-source \
  --destination-location-arn arn:aws:datasync:us-east-1:123456789012:location/loc-dest \
  --name "Preserve-Deletes" \
  --options PreserveDeletedFiles=PRESERVE,TransferMode=CHANGED

# Task with full metadata preservation
aws datasync create-task \
  --source-location-arn arn:aws:datasync:us-east-1:123456789012:location/loc-source \
  --destination-location-arn arn:aws:datasync:us-east-1:123456789012:location/loc-dest \
  --name "Full-Metadata-Sync" \
  --options '
  {
    "Atime": "BEST_EFFORT",
    "Mtime": "PRESERVE",
    "Uid": "INT_VALUE",
    "Gid": "INT_VALUE",
    "PosixPermissions": "PRESERVE",
    "PreserveDeletedFiles": "PRESERVE",
    "PreserveDevices": "PRESERVE",
    "SecurityDescriptorCopyFlags": "OWNER_DACL_SACL",
    "ObjectTags": "PRESERVE"
  }'
```

### Listing Locations

```bash
# List all locations
aws datasync list-locations

# List locations with pagination
aws datasync list-locations --max-results 20

# Describe S3 location
aws datasync describe-location-s3 \
  --location-arn arn:aws:datasync:us-east-1:123456789012:location/loc-0123456789abcdef0

# Describe EFS location
aws datasync describe-location-efs \
  --location-arn arn:aws:datasync:us-east-1:123456789012:location/loc-0123456789abcdef0

# Describe NFS location
aws datasync describe-location-nfs \
  --location-arn arn:aws:datasync:us-east-1:123456789012:location/loc-0123456789abcdef0

# Update S3 location storage class
aws datasync update-location-s3 \
  --location-arn arn:aws:datasync:us-east-1:123456789012:location/loc-0123456789abcdef0 \
  --s3-storage-class INTELLIGENT_TIERING

# Delete location
aws datasync delete-location \
  --location-arn arn:aws:datasync:us-east-1:123456789012:location/loc-0123456789abcdef0
```

### Monitoring and Metrics

```bash
# Get CloudWatch metrics for DataSync task
aws cloudwatch get-metric-statistics \
  --namespace AWS/DataSync \
  --metric-name BytesTransferred \
  --dimensions Name=TaskId,Value=task-0123456789abcdef0 \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 3600 \
  --statistics Sum

# Get files transferred metric
aws cloudwatch get-metric-statistics \
  --namespace AWS/DataSync \
  --metric-name FilesTransferred \
  --dimensions Name=TaskId,Value=task-0123456789abcdef0 \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 3600 \
  --statistics Sum

# Create CloudWatch alarm for task failures
aws cloudwatch put-metric-alarm \
  --alarm-name datasync-task-failure \
  --alarm-description "Alert when DataSync task fails" \
  --metric-name TaskExecutionStatus \
  --namespace AWS/DataSync \
  --statistic Sum \
  --period 300 \
  --evaluation-periods 1 \
  --threshold 1 \
  --comparison-operator GreaterThanOrEqualToThreshold \
  --dimensions Name=TaskId,Value=task-0123456789abcdef0 \
  --alarm-actions arn:aws:sns:us-east-1:123456789012:datasync-alerts
```

---

## Practice Questions

### Question 1
A company wants to migrate 50 TB of data from their on-premises NFS server to Amazon S3. They have a 1 Gbps Direct Connect connection. Which service should they use?

A) AWS Snowball  
B) AWS DataSync  
C) AWS Storage Gateway  
D) AWS Transfer Family  

**Answer: B** - DataSync is ideal for online migration over network connections. With 1 Gbps, 50 TB can be transferred in about a week.

### Question 2
Which component is required when using DataSync to transfer data from an on-premises SMB file share to Amazon EFS?

A) AWS Direct Connect  
B) DataSync agent  
C) VPC peering  
D) NAT gateway  

**Answer: B** - DataSync agent must be deployed on-premises to access SMB file shares.

### Question 3
A company needs to replicate data from Amazon S3 in one region to Amazon EFS in another region. What does this require?

A) DataSync agent in both regions  
B) DataSync agent in source region only  
C) DataSync agent in destination region only  
D) No DataSync agent required  

**Answer: D** - AWS-to-AWS transfers don't require an agent. DataSync accesses S3 and EFS directly.

### Question 4
Which DataSync feature helps reduce the amount of data transferred on subsequent task executions?

A) Compression  
B) Filtering  
C) Incremental transfer  
D) Bandwidth throttling  

**Answer: C** - DataSync performs incremental transfers by comparing source and destination, only transferring new or changed files.

### Question 5
A company wants to transfer data to S3 without going over the public internet. What should they configure?

A) S3 Transfer Acceleration  
B) VPC endpoint for DataSync  
C) CloudFront distribution  
D) Public DataSync endpoint  

**Answer: B** - Using VPC endpoints (PrivateLink) keeps DataSync traffic on private network, not the public internet.

---

## Summary

AWS DataSync is an online data transfer service:

**Key Points**:
- **Purpose**: Move data between on-premises, other clouds, and AWS
- **Speed**: Up to 10 Gbps per task
- **Agent**: Required for on-premises/other clouds, not for AWS-to-AWS
- **Incremental**: Only transfers changed data
- **Integrated**: Works with S3, EFS, FSx

**Core Components**:
1. Agent (on-premises/edge)
2. Location (source/destination)
3. Task (transfer configuration)
4. Task Execution (individual run)

**Use Cases**:
- Data migration
- Disaster recovery replication
- Hybrid workflows
- Cold data archival

**SAA-C03 Focus**:
- DataSync for online transfers
- Snow Family for offline/large transfers
- Agent vs agentless scenarios
- Transfer to any S3 storage class
