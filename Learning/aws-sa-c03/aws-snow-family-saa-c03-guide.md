# AWS Snow Family - SAA-C03 Comprehensive Guide

## Table of Contents
1. [Overview and Introduction](#overview-and-introduction)
2. [AWS Snowcone](#aws-snowcone)
3. [AWS Snowball Edge](#aws-snowball-edge)
4. [AWS Snowmobile](#aws-snowmobile)
5. [Snow Family Comparison](#snow-family-comparison)
6. [Data Migration Use Cases](#data-migration-use-cases)
7. [Edge Computing Use Cases](#edge-computing-use-cases)
8. [Security](#security)
9. [AWS OpsHub](#aws-opshub)
10. [Pricing and Cost Optimization](#pricing-and-cost-optimization)
11. [Best Practices](#best-practices)
12. [SAA-C03 Exam Tips](#saa-c03-exam-tips)
13. [AWS CLI Commands Reference](#aws-cli-commands-reference)
14. [Practice Questions](#practice-questions)

---

## Overview and Introduction

### What is the AWS Snow Family?

The AWS Snow Family is a collection of physical devices designed to help migrate large amounts of data into and out of AWS, and to run compute workloads in edge locations where connectivity is limited or unavailable.

### Key Use Cases

1. **Data Migration**: Move petabytes of data to AWS
2. **Edge Computing**: Process data locally before sending to cloud
3. **Disconnected Operations**: Work without internet connectivity
4. **Tactical Edge**: Military, maritime, and remote operations

### Snow Family Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     AWS Snow Family                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │                      Snowcone                             │  │
│   │  • Smallest device (4.5 lbs / 2.1 kg)                    │  │
│   │  • 8 TB HDD or 14 TB SSD                                 │  │
│   │  • Edge computing + data transfer                        │  │
│   │  • Fits in a backpack                                    │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │                   Snowball Edge                           │  │
│   │  • Medium device (50 lbs / 22.3 kg)                      │  │
│   │  • Storage Optimized: 80 TB                              │  │
│   │  • Compute Optimized: 42 TB + GPU                        │  │
│   │  • Edge computing + large data transfer                  │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │                     Snowmobile                            │  │
│   │  • Shipping container (45-foot)                          │  │
│   │  • Up to 100 PB capacity                                 │  │
│   │  • Exabyte-scale data migration                         │  │
│   │  • Comes with security personnel                        │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Why Use Snow Family?

#### Challenge: Network Transfer Limitations

| Data Size | 100 Mbps | 1 Gbps | 10 Gbps |
|-----------|----------|--------|---------|
| 10 TB | 12 days | 1.2 days | 3 hours |
| 100 TB | 120 days | 12 days | 1.2 days |
| 1 PB | 3 years | 4 months | 12 days |

**Snow Family Solution**: Physical transfer can be faster for large datasets!

---

## AWS Snowcone

### Overview

AWS Snowcone is the smallest member of the Snow Family, designed for portable edge computing and data transfer in space-constrained environments.

### Specifications

| Feature | Snowcone (HDD) | Snowcone SSD |
|---------|---------------|--------------|
| **Storage** | 8 TB HDD | 14 TB SSD |
| **Compute** | 2 vCPUs, 4 GB RAM | 2 vCPUs, 4 GB RAM |
| **Weight** | 4.5 lbs (2.1 kg) | 4.5 lbs (2.1 kg) |
| **Size** | 9" x 6" x 3" | 9" x 6" x 3" |
| **Power** | USB-C or optional battery | USB-C or optional battery |
| **Network** | 2x 1/10 GbE | 2x 1/10 GbE |
| **Wireless** | Wi-Fi support | Wi-Fi support |

### Key Features

- **Portable**: Fits in a backpack
- **Rugged**: Dust, water, and shock resistant
- **Versatile**: Battery powered option available
- **Edge Computing**: Run EC2 instances and Lambda
- **DataSync Agent**: Pre-installed for easy transfer

### Use Cases

1. **IoT Data Collection**: Remote sensors, industrial equipment
2. **Healthcare**: Medical imaging in field clinics
3. **Military/Tactical**: Battlefield data processing
4. **Content Distribution**: Deliver content to remote locations
5. **Disaster Recovery**: Collect data in emergency situations

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   Snowcone Architecture                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   On-Site/Remote Location                                        │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │                                                          │  │
│   │   ┌────────────┐      ┌────────────────────────────┐    │  │
│   │   │  Sensors   │      │        Snowcone            │    │  │
│   │   │  Cameras   │ ───► │  ┌──────────────────────┐  │    │  │
│   │   │  Devices   │      │  │ Storage (8/14 TB)    │  │    │  │
│   │   └────────────┘      │  ├──────────────────────┤  │    │  │
│   │                       │  │ Compute (EC2/Lambda) │  │    │  │
│   │   ┌────────────┐      │  ├──────────────────────┤  │    │  │
│   │   │  Laptop    │ ◄──► │  │ DataSync Agent       │  │    │  │
│   │   │  (OpsHub)  │      │  └──────────────────────┘  │    │  │
│   │   └────────────┘      └────────────────────────────┘    │  │
│   │                                                          │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│   Data Transfer Options:                                         │
│   • Ship device to AWS                                          │
│   • DataSync over network (when connected)                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## AWS Snowball Edge

### Overview

AWS Snowball Edge is a petabyte-scale data transfer device with on-board storage and compute capabilities, available in two configurations.

### Device Types

#### Snowball Edge Storage Optimized

| Feature | Specification |
|---------|---------------|
| **Storage** | 80 TB usable (210 TB raw) |
| **Compute** | 40 vCPUs, 80 GB RAM |
| **SSD Storage** | 1 TB NVMe SSD |
| **GPU** | Not available |
| **Weight** | 49.7 lbs (22.3 kg) |
| **Network** | 10/25/40/100 GbE |

#### Snowball Edge Compute Optimized

| Feature | Specification |
|---------|---------------|
| **Storage** | 42 TB usable (80 TB raw) |
| **Compute** | 104 vCPUs, 416 GB RAM |
| **SSD Storage** | 28 TB NVMe SSD |
| **GPU** | Optional NVIDIA V100 |
| **Weight** | 49.7 lbs (22.3 kg) |
| **Network** | 10/25/40/100 GbE |

### Key Features

- **Clustering**: Up to 16 devices for increased storage (1+ PB)
- **S3 Compatible**: Local S3 endpoint on device
- **EBS Volumes**: Attach to EC2 instances on device
- **EC2 AMIs**: Run custom AMIs on device
- **Lambda**: Run Lambda functions locally
- **IoT Greengrass**: Edge ML inference

### Storage Clustering

```
┌─────────────────────────────────────────────────────────────────┐
│               Snowball Edge Cluster (Example: 5 Devices)         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐│
│   │Device 1 │  │Device 2 │  │Device 3 │  │Device 4 │  │Device 5 ││
│   │ 80 TB   │  │ 80 TB   │  │ 80 TB   │  │ 80 TB   │  │ 80 TB   ││
│   └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘│
│        │            │            │            │            │     │
│        └────────────┴────────────┴────────────┴────────────┘     │
│                              │                                    │
│                     ┌────────┴────────┐                          │
│                     │  Cluster Storage │                          │
│                     │     400 TB       │                          │
│                     │  (single namespace)                         │
│                     └─────────────────┘                          │
│                                                                  │
│   Benefits:                                                      │
│   • Single S3 endpoint for entire cluster                       │
│   • Automatic data distribution                                  │
│   • Increased durability (data striped across devices)          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Compute Capabilities

```
┌─────────────────────────────────────────────────────────────────┐
│            Snowball Edge Compute Architecture                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌────────────────────────────────────────────────────────┐    │
│   │                 Snowball Edge Device                    │    │
│   │                                                         │    │
│   │   ┌─────────────────────────────────────────────────┐  │    │
│   │   │              Compute Layer                       │  │    │
│   │   │  ┌────────────┐  ┌────────────┐  ┌───────────┐  │  │    │
│   │   │  │    EC2     │  │   Lambda   │  │IoT        │  │  │    │
│   │   │  │ Instances  │  │ Functions  │  │Greengrass │  │  │    │
│   │   │  └────────────┘  └────────────┘  └───────────┘  │  │    │
│   │   └─────────────────────────────────────────────────┘  │    │
│   │                                                         │    │
│   │   ┌─────────────────────────────────────────────────┐  │    │
│   │   │              Storage Layer                       │  │    │
│   │   │  ┌────────────┐  ┌────────────┐  ┌───────────┐  │  │    │
│   │   │  │  S3 API    │  │    NFS     │  │    EBS    │  │  │    │
│   │   │  │ Compatible │  │   Shares   │  │  Volumes  │  │  │    │
│   │   │  └────────────┘  └────────────┘  └───────────┘  │  │    │
│   │   └─────────────────────────────────────────────────┘  │    │
│   │                                                         │    │
│   └────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### EC2 on Snowball Edge

Supported instance types:

| Instance Type | vCPU | Memory | Use Case |
|---------------|------|--------|----------|
| sbe1.small | 1 | 2 GB | Light workloads |
| sbe1.medium | 1 | 4 GB | General purpose |
| sbe1.large | 2 | 8 GB | General purpose |
| sbe1.xlarge | 4 | 16 GB | Compute intensive |
| sbe1.2xlarge | 8 | 32 GB | Memory intensive |
| sbe1.4xlarge | 16 | 64 GB | Heavy workloads |
| sbe-c.medium | 24 | 32 GB | Compute optimized |
| sbe-c.large | 52 | 208 GB | Large compute |
| sbe-g.medium | 24 | 32 GB | GPU workloads |

---

## AWS Snowmobile

### Overview

AWS Snowmobile is an exabyte-scale data transfer service that uses a 45-foot shipping container to move massive amounts of data to AWS.

### Specifications

| Feature | Specification |
|---------|---------------|
| **Storage** | Up to 100 PB per Snowmobile |
| **Container** | 45-foot ruggedized shipping container |
| **Transport** | Semi-trailer truck |
| **Security** | GPS tracking, alarm monitoring, 24/7 video surveillance |
| **Network** | Multiple 40 Gbps connections |
| **Data Transfer** | Can transfer 100 PB in ~10 weeks |

### When to Use Snowmobile

- Data migration > 10 PB
- Datacenter shutdown/migration
- Exabyte-scale transfers
- When network transfer would take years

### Transfer Time Comparison

For 100 PB of data:

| Method | Time |
|--------|------|
| 10 Gbps dedicated line | ~28 years |
| Multiple Snowball Edge | 6+ months |
| Single Snowmobile | ~10 weeks |

### Security Features

```
┌─────────────────────────────────────────────────────────────────┐
│                   Snowmobile Security                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Physical Security:                                             │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  • Tamper-resistant container                            │  │
│   │  • GPS tracking during transit                           │  │
│   │  • 24/7 video surveillance                               │  │
│   │  • Security escort vehicle                               │  │
│   │  • Dedicated security personnel                          │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│   Data Security:                                                 │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  • 256-bit encryption                                    │  │
│   │  • Customer-managed encryption keys                      │  │
│   │  • AWS KMS integration                                   │  │
│   │  • Secure data destruction after transfer                │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│   Network Security:                                              │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  • Dedicated network connection to your datacenter       │  │
│   │  • Optional Direct Connect setup                         │  │
│   │  • Firewall protection                                   │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Snow Family Comparison

### Feature Comparison

| Feature | Snowcone | Snowball Edge SO | Snowball Edge CO | Snowmobile |
|---------|----------|------------------|------------------|------------|
| **Storage** | 8-14 TB | 80 TB | 42 TB | 100 PB |
| **Compute** | 2 vCPU, 4 GB | 40 vCPU, 80 GB | 104 vCPU, 416 GB | None |
| **GPU** | No | No | Optional | No |
| **Weight** | 4.5 lbs | 49.7 lbs | 49.7 lbs | N/A |
| **Portability** | Backpack | Shippable | Shippable | Truck |
| **Clustering** | No | Yes (up to 16) | Yes (up to 16) | No |
| **Use Case** | Portable edge | Large migration | Edge compute | Exabyte migration |

### Decision Matrix

```
┌─────────────────────────────────────────────────────────────────┐
│              Snow Family Selection Guide                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Data Size:                                                     │
│   ┌────────────────────────────────────────────────────────┐    │
│   │  < 8 TB    ──────────►  DataSync/S3 Transfer           │    │
│   │  8-14 TB   ──────────►  Snowcone                       │    │
│   │  14 TB - 10 PB ──────►  Snowball Edge                  │    │
│   │  > 10 PB   ──────────►  Snowmobile                     │    │
│   └────────────────────────────────────────────────────────┘    │
│                                                                  │
│   Use Case:                                                      │
│   ┌────────────────────────────────────────────────────────┐    │
│   │  Portable/Tactical ─────►  Snowcone                    │    │
│   │  Data Migration ────────►  Snowball Edge Storage Opt   │    │
│   │  Edge Compute ──────────►  Snowball Edge Compute Opt   │    │
│   │  Datacenter Shutdown ───►  Snowmobile                  │    │
│   │  ML at Edge ────────────►  Snowball Edge CO + GPU      │    │
│   └────────────────────────────────────────────────────────┘    │
│                                                                  │
│   Environment:                                                   │
│   ┌────────────────────────────────────────────────────────┐    │
│   │  Space Constrained ─────►  Snowcone                    │    │
│   │  Remote/Rugged ─────────►  Snowcone                    │    │
│   │  Standard Facility ─────►  Snowball Edge               │    │
│   │  Large Datacenter ──────►  Snowmobile                  │    │
│   └────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Migration Use Cases

### Typical Migration Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│              Snow Family Migration Workflow                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Step 1: Request Device                                         │
│   ┌────────────────────────────────────────────────────────┐    │
│   │  AWS Console → Snow Family → Create Job → Select Device │    │
│   │  • Choose device type                                   │    │
│   │  • Specify S3 bucket destination                        │    │
│   │  • Configure encryption (KMS)                           │    │
│   │  • Provide shipping address                             │    │
│   └────────────────────────────────────────────────────────┘    │
│                            ↓                                     │
│   Step 2: Receive and Connect Device                             │
│   ┌────────────────────────────────────────────────────────┐    │
│   │  • Receive device (shipped by AWS)                      │    │
│   │  • Connect power and network                            │    │
│   │  • Unlock device using OpsHub or CLI                    │    │
│   └────────────────────────────────────────────────────────┘    │
│                            ↓                                     │
│   Step 3: Transfer Data                                          │
│   ┌────────────────────────────────────────────────────────┐    │
│   │  • Use S3 API, NFS, or DataSync                         │    │
│   │  • Copy data to device                                  │    │
│   │  • Verify transfer completion                           │    │
│   └────────────────────────────────────────────────────────┘    │
│                            ↓                                     │
│   Step 4: Return Device                                          │
│   ┌────────────────────────────────────────────────────────┐    │
│   │  • Power off device                                     │    │
│   │  • Use prepaid shipping label                           │    │
│   │  • Ship back to AWS                                     │    │
│   └────────────────────────────────────────────────────────┘    │
│                            ↓                                     │
│   Step 5: Data Upload                                            │
│   ┌────────────────────────────────────────────────────────┐    │
│   │  • AWS receives device                                  │    │
│   │  • Data uploaded to S3                                  │    │
│   │  • Device securely erased                               │    │
│   │  • Job status updated in console                        │    │
│   └────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Data Transfer Methods

#### S3 Adapter (S3 API Compatible)

```bash
# Configure AWS CLI for Snow device
aws configure --profile snowball

# Copy data using S3 commands
aws s3 cp /data/myfiles s3://mybucket/ \
  --recursive \
  --endpoint http://192.168.1.100:8080 \
  --profile snowball
```

#### NFS File Interface

```bash
# Mount NFS share
mount -t nfs 192.168.1.100:/buckets/mybucket /mnt/snowball

# Copy files
cp -r /data/myfiles/* /mnt/snowball/
```

#### AWS DataSync

```
┌─────────────────────────────────────────────────────────────────┐
│                DataSync with Snowcone                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌──────────────┐        ┌──────────────┐        ┌──────────┐ │
│   │   Source     │        │   Snowcone   │        │   AWS    │ │
│   │   Storage    │ ──────►│   DataSync   │ ──────►│   S3     │ │
│   │   (NAS/NFS)  │  Agent │   Agent      │ Network│          │ │
│   └──────────────┘        └──────────────┘        └──────────┘ │
│                                                                  │
│   • Pre-installed DataSync agent on Snowcone                    │
│   • Transfer data directly to AWS over network                  │
│   • Useful when you have intermittent connectivity              │
│   • Buffer data locally, sync when connected                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Edge Computing Use Cases

### Machine Learning at Edge

```
┌─────────────────────────────────────────────────────────────────┐
│           ML Inference at Edge with Snowball Edge                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Factory Floor                                                  │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │                                                          │  │
│   │   ┌──────────┐      ┌────────────────────────────────┐  │  │
│   │   │  Camera  │      │    Snowball Edge Compute Opt   │  │  │
│   │   │  Stream  │ ───► │    + GPU                       │  │  │
│   │   └──────────┘      │                                │  │  │
│   │                     │  ┌───────────────────────────┐ │  │  │
│   │                     │  │   ML Inference Model      │ │  │  │
│   │                     │  │   (Defect Detection)      │ │  │  │
│   │                     │  └───────────────────────────┘ │  │  │
│   │                     │              │                 │  │  │
│   │                     │              ▼                 │  │  │
│   │                     │  ┌───────────────────────────┐ │  │  │
│   │                     │  │   Alert/Action            │ │  │  │
│   │                     │  │   (Stop production line)  │ │  │  │
│   │                     │  └───────────────────────────┘ │  │  │
│   │                     └────────────────────────────────┘  │  │
│   │                                                          │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│   Benefits:                                                      │
│   • Real-time inference (no network latency)                    │
│   • Works without internet connectivity                         │
│   • Process video streams locally                               │
│   • Sync results to AWS when connected                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### IoT Data Processing

```
┌─────────────────────────────────────────────────────────────────┐
│              IoT Edge Processing with Snowcone                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Remote Oil Field                                               │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │                                                          │  │
│   │   ┌─────────┐  ┌─────────┐  ┌─────────┐                 │  │
│   │   │Sensor 1 │  │Sensor 2 │  │Sensor 3 │                 │  │
│   │   └────┬────┘  └────┬────┘  └────┬────┘                 │  │
│   │        │            │            │                       │  │
│   │        └────────────┼────────────┘                       │  │
│   │                     │                                    │  │
│   │                     ▼                                    │  │
│   │        ┌────────────────────────────────┐               │  │
│   │        │          Snowcone              │               │  │
│   │        │  ┌──────────────────────────┐  │               │  │
│   │        │  │  IoT Greengrass          │  │               │  │
│   │        │  │  - Data aggregation      │  │               │  │
│   │        │  │  - Local processing      │  │               │  │
│   │        │  │  - Anomaly detection     │  │               │  │
│   │        │  └──────────────────────────┘  │               │  │
│   │        │  ┌──────────────────────────┐  │               │  │
│   │        │  │  Local Storage (8-14 TB) │  │               │  │
│   │        │  └──────────────────────────┘  │               │  │
│   │        └────────────────────────────────┘               │  │
│   │                     │                                    │  │
│   │                     │ When connected                     │  │
│   │                     ▼                                    │  │
│   │              ┌─────────────┐                            │  │
│   │              │   AWS IoT   │                            │  │
│   │              │   Cloud     │                            │  │
│   │              └─────────────┘                            │  │
│   │                                                          │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Security

### Encryption

All Snow Family devices use multiple layers of encryption:

```
┌─────────────────────────────────────────────────────────────────┐
│                   Snow Family Encryption                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Encryption at Rest:                                            │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  • 256-bit encryption (AES-256)                          │  │
│   │  • Keys managed by AWS KMS                               │  │
│   │  • Option for customer-managed CMK                       │  │
│   │  • Keys never stored on device                           │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│   Encryption in Transit:                                         │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  • TLS for network transfers                             │  │
│   │  • Encrypted shipping container (Snowmobile)             │  │
│   │  • Tamper-evident enclosure                              │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│   Key Management Flow:                                           │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │                                                          │  │
│   │    ┌─────────┐    ┌─────────┐    ┌─────────────────┐    │  │
│   │    │  AWS    │    │   KMS   │    │     Snow        │    │  │
│   │    │ Console │───►│  Key    │───►│     Device      │    │  │
│   │    └─────────┘    └─────────┘    └─────────────────┘    │  │
│   │         │              │                  │              │  │
│   │         │              │                  │              │  │
│   │    1. Create job   2. Generate      3. Device encrypted │  │
│   │       with KMS       data key          with data key    │  │
│   │       key                                               │  │
│   │                                                          │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Physical Security

| Device | Physical Security Measures |
|--------|---------------------------|
| **Snowcone** | Tamper-evident, ruggedized enclosure |
| **Snowball Edge** | Tamper-evident, GPS tracking, secure boot |
| **Snowmobile** | Armed security, GPS, 24/7 surveillance, escort |

### Secure Erasure

After data is uploaded to AWS:
1. Device is verified received
2. Data is uploaded to S3
3. Device is securely erased (NIST 800-88)
4. Erasure is verified
5. Device is sanitized for next customer

---

## AWS OpsHub

### Overview

AWS OpsHub is a graphical user interface for managing Snow Family devices, available as a free downloadable application.

### Key Features

- **Device Management**: Unlock, configure, monitor devices
- **File Transfer**: GUI-based file copy operations
- **Compute Management**: Launch and manage EC2 instances
- **Monitoring**: View device status and metrics
- **Clustering**: Manage Snowball Edge clusters

### OpsHub Interface

```
┌─────────────────────────────────────────────────────────────────┐
│                     AWS OpsHub Interface                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  Dashboard                                                │  │
│   │  ┌────────────────┐  ┌────────────────┐                  │  │
│   │  │ Device Status  │  │ Storage Used   │                  │  │
│   │  │   Connected ✓  │  │   45 TB / 80 TB│                  │  │
│   │  └────────────────┘  └────────────────┘                  │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  Quick Actions                                            │  │
│   │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │  │
│   │  │  Copy    │  │  Launch  │  │  View    │  │Configure │ │  │
│   │  │  Files   │  │   EC2    │  │   Logs   │  │ Network  │ │  │
│   │  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  Resources                                                │  │
│   │  • S3 Buckets (3)                                        │  │
│   │  • EC2 Instances (2 running)                             │  │
│   │  • NFS Shares (1)                                        │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### OpsHub vs CLI

| Task | OpsHub | CLI |
|------|--------|-----|
| Unlock device | GUI button | `snowballEdge unlock-device` |
| Copy files | Drag and drop | `aws s3 cp` |
| Launch EC2 | Click and configure | `aws ec2 run-instances` |
| View status | Dashboard | `snowballEdge describe-device` |

---

## Pricing and Cost Optimization

### Pricing Model

#### Snowcone

| Component | Cost |
|-----------|------|
| Service fee (per job) | $60 |
| Device usage (per day) | $0 for first 5 days, then $6/day |
| Data transfer out | Standard S3 rates |
| Shipping | Standard shipping rates |

#### Snowball Edge

| Component | Cost |
|-----------|------|
| Service fee (per job) | $300 (Storage Opt) / $440 (Compute Opt) |
| Device usage (per day) | $0 for first 10 days, then $30/day |
| Data transfer IN | Free |
| Data transfer OUT | Standard S3 rates |
| Shipping | Varies by location |

#### Snowmobile

- Custom pricing based on project scope
- Includes setup, security, and transfer services

### Cost Comparison Example

**Scenario**: Migrate 100 TB to AWS

| Method | Estimated Cost | Time |
|--------|---------------|------|
| Direct Connect (1 Gbps) | ~$2,500/month + data | ~10 days |
| Snowball Edge (2 devices) | ~$600 + shipping | ~2 weeks |
| Internet (100 Mbps) | ~$50/month bandwidth | ~120 days |

### Cost Optimization Tips

1. **Maximize device utilization**: Fill device to capacity
2. **Return promptly**: Avoid daily overage charges
3. **Batch jobs**: Combine multiple transfers when possible
4. **Right-size**: Use smallest appropriate device
5. **Plan shipping**: Factor in transit time

---

## Best Practices

### Data Migration Best Practices

1. **Plan thoroughly**: Calculate data size, transfer time
2. **Prepare data**: Organize files, remove unnecessary data
3. **Test first**: Verify setup with small dataset
4. **Parallel transfers**: Use multiple connections when possible
5. **Verify integrity**: Use checksums to verify transfer
6. **Document**: Keep records of what data went where

### Edge Computing Best Practices

1. **Design for disconnected operation**: Assume no connectivity
2. **Local data processing**: Reduce data before transfer
3. **Implement retry logic**: Handle intermittent connectivity
4. **Monitor locally**: Use OpsHub for device monitoring
5. **Plan capacity**: Understand compute and storage limits
6. **Secure access**: Use IAM and security groups

### Security Best Practices

1. **Use customer-managed KMS keys**: For additional control
2. **Verify device**: Check serial numbers match order
3. **Secure network**: Use dedicated network segment
4. **Limit access**: Only authorized personnel
5. **Track chain of custody**: Document who had device when
6. **Verify erasure**: Confirm AWS erased device after job

---

## SAA-C03 Exam Tips

### Key Concepts to Remember

1. **Snowcone** = Smallest, portable, 8-14 TB
2. **Snowball Edge SO** = Large storage, 80 TB
3. **Snowball Edge CO** = Heavy compute, GPU option
4. **Snowmobile** = Exabyte scale, 100 PB
5. **Physical transfer beats network for large data**

### Common Exam Scenarios

#### Scenario 1: Large Data Migration
**Question**: Need to migrate 50 TB to AWS, network would take 60 days.
**Answer**: Snowball Edge Storage Optimized

#### Scenario 2: Edge ML Processing
**Question**: Run ML inference at remote location without internet.
**Answer**: Snowball Edge Compute Optimized with GPU

#### Scenario 3: Tactical/Mobile Data Collection
**Question**: Collect data in remote, space-constrained locations.
**Answer**: Snowcone

#### Scenario 4: Datacenter Shutdown
**Question**: Migrate 50 PB from datacenter before shutdown.
**Answer**: AWS Snowmobile

#### Scenario 5: Edge with Network Sync
**Question**: Process IoT data locally, sync when connected.
**Answer**: Snowcone with DataSync agent

### Decision Guide for Exam

```
┌─────────────────────────────────────────────────────────────────┐
│                  Snow Family Exam Decision Tree                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Q: How much data?                                              │
│   │                                                              │
│   ├── < 8 TB ──────────────► Consider network transfer          │
│   │                                                              │
│   ├── 8 TB - 80 TB ────────► Snowcone or Snowball Edge         │
│   │   │                                                          │
│   │   └── Need portability? ──► Snowcone                        │
│   │   └── Need compute? ──────► Snowball Edge CO                │
│   │   └── Just storage? ──────► Snowball Edge SO                │
│   │                                                              │
│   ├── 80 TB - 10 PB ───────► Multiple Snowball Edge             │
│   │                                                              │
│   └── > 10 PB ─────────────► Snowmobile                         │
│                                                                  │
│   Q: Need edge compute?                                          │
│   │                                                              │
│   ├── Basic compute ───────► Snowcone or Snowball Edge SO       │
│   ├── Heavy compute ───────► Snowball Edge CO                   │
│   └── GPU/ML ──────────────► Snowball Edge CO + GPU             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Exam Question Keywords

- "Petabytes of data" → **Snowball Edge** or **Snowmobile**
- "Exabytes" → **Snowmobile**
- "Portable/tactical" → **Snowcone**
- "Edge computing" → **Snowball Edge**
- "GPU at edge" → **Snowball Edge Compute Optimized**
- "Network too slow" → **Snow Family**
- "Disconnected location" → **Snow Family with edge compute**
- "Datacenter migration" → **Snowball Edge** or **Snowmobile**

### Default Values to Remember

| Device | Storage | Free Usage Days |
|--------|---------|-----------------|
| Snowcone | 8 TB HDD / 14 TB SSD | 5 days |
| Snowball Edge SO | 80 TB | 10 days |
| Snowball Edge CO | 42 TB | 10 days |
| Snowmobile | 100 PB | Custom |

---
## AWS CLI Commands Reference

### Snowball Job Management

#### Create Snowball Job
```bash
# Create import job with Snowball Edge Storage Optimized
aws snowball create-job \
    --job-type IMPORT \
    --resources '{"S3Resources": [{"BucketArn": "arn:aws:s3:::my-import-bucket"}]}' \
    --description "Import 50TB of archive data" \
    --address-id ADID1234567890abc \
    --kms-key-arn arn:aws:kms:us-east-1:123456789012:key/abcd1234-a123-456a-a12b-a123b4cd56ef \
    --role-arn arn:aws:iam::123456789012:role/SnowballRole \
    --snowball-capacity-preference T80 \
    --shipping-option SECOND_DAY

# Create export job from S3 to Snowball
aws snowball create-job \
    --job-type EXPORT \
    --resources '{"S3Resources": [{"BucketArn": "arn:aws:s3:::my-export-bucket", "KeyRange": {"BeginMarker": "data/", "EndMarker": "data/~"}}]}' \
    --description "Export data for offline processing" \
    --address-id ADID1234567890abc \
    --kms-key-arn arn:aws:kms:us-east-1:123456789012:key/abcd1234-a123-456a-a12b-a123b4cd56ef \
    --role-arn arn:aws:iam::123456789012:role/SnowballRole \
    --snowball-capacity-preference T80 \
    --shipping-option NEXT_DAY

# Create local compute and storage job
aws snowball create-job \
    --job-type LOCAL_USE \
    --description "Edge computing for video processing" \
    --address-id ADID1234567890abc \
    --kms-key-arn arn:aws:kms:us-east-1:123456789012:key/abcd1234-a123-456a-a12b-a123b4cd56ef \
    --role-arn arn:aws:iam::123456789012:role/SnowballRole \
    --snowball-capacity-preference T42 \
    --device-configuration '{"SnowconeDeviceConfiguration": {"WirelessConnection": {"IsWifiEnabled": true}}}' \
    --shipping-option SECOND_DAY

# Create Snowball Edge Compute Optimized job with GPU
aws snowball create-job \
    --job-type IMPORT \
    --resources '{"S3Resources": [{"BucketArn": "arn:aws:s3:::ml-training-data"}]}' \
    --description "ML training data import with GPU processing" \
    --address-id ADID1234567890abc \
    --kms-key-arn arn:aws:kms:us-east-1:123456789012:key/abcd1234-a123-456a-a12b-a123b4cd56ef \
    --role-arn arn:aws:iam::123456789012:role/SnowballRole \
    --snowball-capacity-preference T42 \
    --snowball-type EDGE_C \
    --shipping-option SECOND_DAY
```

#### Create Snowcone Job
```bash
# Create Snowcone HDD job for import
aws snowball create-job \
    --job-type IMPORT \
    --resources '{"S3Resources": [{"BucketArn": "arn:aws:s3:::remote-site-data"}]}' \
    --description "Snowcone data collection from remote site" \
    --address-id ADID1234567890abc \
    --kms-key-arn arn:aws:kms:us-east-1:123456789012:key/abcd1234-a123-456a-a12b-a123b4cd56ef \
    --role-arn arn:aws:iam::123456789012:role/SnowballRole \
    --snowball-capacity-preference T8 \
    --snowball-type SNC1_HDD \
    --shipping-option SECOND_DAY

# Create Snowcone SSD job with DataSync
aws snowball create-job \
    --job-type IMPORT \
    --resources '{"S3Resources": [{"BucketArn": "arn:aws:s3:::iot-data-bucket"}]}' \
    --description "IoT edge data collection with Snowcone SSD" \
    --address-id ADID1234567890abc \
    --kms-key-arn arn:aws:kms:us-east-1:123456789012:key/abcd1234-a123-456a-a12b-a123b4cd56ef \
    --role-arn arn:aws:iam::123456789012:role/SnowballRole \
    --snowball-capacity-preference T14 \
    --snowball-type SNC1_SSD \
    --device-configuration '{"SnowconeDeviceConfiguration": {"WirelessConnection": {"IsWifiEnabled": true}}}' \
    --long-term-pricing-id LTP1234567890abc
```

#### Describe and List Jobs
```bash
# List all Snowball jobs
aws snowball list-jobs

# List jobs with specific output format
aws snowball list-jobs \
    --query 'JobListEntries[*].[JobId,JobType,JobState,CreationDate]' \
    --output table

# Describe specific job details
aws snowball describe-job \
    --job-id JID123e4567-e89b-12d3-a456-426655440000

# Get job status
aws snowball describe-job \
    --job-id JID123e4567-e89b-12d3-a456-426655440000 \
    --query 'JobMetadata.JobState' \
    --output text

# List only import jobs
aws snowball list-jobs \
    --query 'JobListEntries[?JobType==`IMPORT`]' \
    --output table

# List jobs in specific state
aws snowball list-jobs \
    --query 'JobListEntries[?JobState==`InProgress`]' \
    --output table
```

#### Cancel and Update Jobs
```bash
# Cancel a job
aws snowball cancel-job \
    --job-id JID123e4567-e89b-12d3-a456-426655440000

# Update job notification settings
aws snowball update-job \
    --job-id JID123e4567-e89b-12d3-a456-426655440000 \
    --notification '{"SnsTopicARN": "arn:aws:sns:us-east-1:123456789012:snowball-notifications", "JobStatesToNotify": ["InProgress", "Complete"]}'

# Update job shipping option
aws snowball update-job \
    --job-id JID123e4567-e89b-12d3-a456-426655440000 \
    --shipping-option NEXT_DAY

# Update job description
aws snowball update-job \
    --job-id JID123e4567-e89b-12d3-a456-426655440000 \
    --description "Updated: Emergency data transfer for disaster recovery"
```

### Cluster Management

#### Create and Manage Clusters
```bash
# Create Snowball Edge cluster for large-scale operations
aws snowball create-cluster \
    --job-type LOCAL_USE \
    --resources '{"S3Resources": [{"BucketArn": "arn:aws:s3:::cluster-storage"}]}' \
    --description "5-node cluster for data processing" \
    --address-id ADID1234567890abc \
    --kms-key-arn arn:aws:kms:us-east-1:123456789012:key/abcd1234-a123-456a-a12b-a123b4cd56ef \
    --role-arn arn:aws:iam::123456789012:role/SnowballRole \
    --snowball-type EDGE \
    --shipping-option SECOND_DAY \
    --cluster-size 5

# List clusters
aws snowball list-clusters

# Describe cluster
aws snowball describe-cluster \
    --cluster-id CID123e4567-e89b-12d3-a456-426655440000

# List jobs in cluster
aws snowball list-cluster-jobs \
    --cluster-id CID123e4567-e89b-12d3-a456-426655440000

# Cancel cluster
aws snowball cancel-cluster \
    --cluster-id CID123e4567-e89b-12d3-a456-426655440000

# Update cluster
aws snowball update-cluster \
    --cluster-id CID123e4567-e89b-12d3-a456-426655440000 \
    --description "Updated cluster configuration" \
    --notification '{"SnsTopicARN": "arn:aws:sns:us-east-1:123456789012:cluster-events"}'
```

### Address Management

#### Create and Manage Shipping Addresses
```bash
# Create shipping address
aws snowball create-address \
    --address '{"Name": "John Doe", "Company": "Example Corp", "Street1": "123 Main Street", "Street2": "Suite 100", "City": "Seattle", "StateOrProvince": "WA", "PostalCode": "98101", "Country": "US", "PhoneNumber": "206-555-0100"}'

# Create address for remote location
aws snowball create-address \
    --address '{"Name": "Remote Site Manager", "Company": "Field Operations", "Street1": "Remote Site Alpha", "City": "Anchorage", "StateOrProvince": "AK", "PostalCode": "99501", "Country": "US", "PhoneNumber": "907-555-0100", "PrefectureOrDistrict": "North"}'

# List all addresses
aws snowball list-addresses

# Describe specific address
aws snowball describe-address \
    --address-id ADID1234567890abc

# Update address (create new address as addresses are immutable)
aws snowball create-address \
    --address '{"Name": "John Doe", "Company": "Example Corp", "Street1": "456 New Street", "City": "Seattle", "StateOrProvince": "WA", "PostalCode": "98102", "Country": "US", "PhoneNumber": "206-555-0200"}'
```

### Job Credentials and Access

#### Get Job Manifest and Unlock Code
```bash
# Get job manifest (required for Snowball Client)
aws snowball get-job-manifest \
    --job-id JID123e4567-e89b-12d3-a456-426655440000

# Get job unlock code
aws snowball get-job-unlock-code \
    --job-id JID123e4567-e89b-12d3-a456-426655440000

# Save manifest to file
aws snowball get-job-manifest \
    --job-id JID123e4567-e89b-12d3-a456-426655440000 \
    --output text > job-manifest.json

# Display unlock code only
aws snowball get-job-unlock-code \
    --job-id JID123e4567-e89b-12d3-a456-426655440000 \
    --query 'UnlockCode' \
    --output text
```

### Device Pickup and Return

#### Manage Device Logistics
```bash
# Get shipping label
aws snowball get-job-manifest \
    --job-id JID123e4567-e89b-12d3-a456-426655440000 \
    --query 'JobMetadata.ShippingDetails'

# Check device status and tracking
aws snowball describe-job \
    --job-id JID123e4567-e89b-12d3-a456-426655440000 \
    --query 'JobMetadata.{State:JobState,ShipDate:ShippingDetails.ShippingOption,Tracking:ShippingDetails.TrackingNumber}' \
    --output table

# List jobs ready for pickup
aws snowball list-jobs \
    --query 'JobListEntries[?JobState==`Pending`].[JobId,JobType,CreationDate]' \
    --output table
```

### Snowmobile Operations

#### Create and Manage Snowmobile Job
```bash
# Note: Snowmobile jobs require direct AWS contact and special arrangements
# These are representative commands - actual Snowmobile operations are coordinated with AWS

# Create Snowmobile job (contact AWS first)
aws snowball create-job \
    --job-type IMPORT \
    --resources '{"S3Resources": [{"BucketArn": "arn:aws:s3:::exabyte-migration"}]}' \
    --description "Exabyte-scale data center migration" \
    --address-id ADID1234567890abc \
    --kms-key-arn arn:aws:kms:us-east-1:123456789012:key/abcd1234-a123-456a-a12b-a123b4cd56ef \
    --role-arn arn:aws:iam::123456789012:role/SnowmobileRole \
    --snowball-type SNOWMOBILE \
    --notification '{"SnsTopicARN": "arn:aws:sns:us-east-1:123456789012:snowmobile-alerts"}'

# Check Snowmobile job status
aws snowball describe-job \
    --job-id JID123e4567-e89b-12d3-a456-426655440000 \
    --query 'JobMetadata.{Type:SnowballType,State:JobState,Description:Description,Resources:Resources}'
```

### Long-Term Pricing

#### Configure Long-Term Pricing
```bash
# Create long-term pricing (1 or 3 years commitment)
aws snowball create-long-term-pricing \
    --long-term-pricing-type OneYear \
    --snowball-type SNC1_SSD \
    --is-long-term-pricing-auto-renew

# List long-term pricing options
aws snowball list-long-term-pricing

# Update long-term pricing
aws snowball update-long-term-pricing \
    --long-term-pricing-id LTP1234567890abc \
    --is-long-term-pricing-auto-renew false
```

### Compatible Storage and Services

#### Work with S3 Compatible Storage
```bash
# List S3 buckets on Snowball Edge (use dedicated endpoint)
export AWS_ENDPOINT=http://192.168.1.100:8080
aws s3 ls --endpoint-url $AWS_ENDPOINT

# Copy data to Snowball Edge S3
aws s3 cp /local/data/ s3://snowball-bucket/data/ \
    --recursive \
    --endpoint-url http://192.168.1.100:8080

# Sync data to Snowball Edge
aws s3 sync /local/data/ s3://snowball-bucket/ \
    --endpoint-url http://192.168.1.100:8080

# List objects on Snowball Edge
aws s3 ls s3://snowball-bucket/ \
    --recursive \
    --endpoint-url http://192.168.1.100:8080
```

### DataSync with Snow Family

#### Configure DataSync for Snowcone
```bash
# Create DataSync agent on Snowcone
aws datasync create-agent \
    --agent-name snowcone-datasync-agent \
    --activation-key ACTIVATION-KEY-FROM-SNOWCONE

# Create NFS location on Snowcone
aws datasync create-location-nfs \
    --server-hostname 192.168.1.50 \
    --subdirectory /export/data \
    --on-prem-config '{"AgentArns": ["arn:aws:datasync:us-east-1:123456789012:agent/agent-0123456789abcdef0"]}'

# Create S3 location for destination
aws datasync create-location-s3 \
    --s3-bucket-arn arn:aws:s3:::my-destination-bucket \
    --s3-config '{"BucketAccessRoleArn": "arn:aws:iam::123456789012:role/DataSyncS3Role"}'

# Create DataSync task
aws datasync create-task \
    --source-location-arn arn:aws:datasync:us-east-1:123456789012:location/loc-source123 \
    --destination-location-arn arn:aws:datasync:us-east-1:123456789012:location/loc-dest456 \
    --name snowcone-to-s3-transfer

# Start DataSync task
aws datasync start-task-execution \
    --task-arn arn:aws:datasync:us-east-1:123456789012:task/task-0123456789abcdef0
```

### Common Monitoring and Troubleshooting

#### Monitor Job Progress
```bash
# Check all jobs status
aws snowball list-jobs \
    --query 'JobListEntries[*].[JobId,JobState,IsMaster,CreationDate]' \
    --output table

# Monitor specific job with watch (Linux/Mac)
watch -n 30 'aws snowball describe-job --job-id JID123e4567-e89b-12d3-a456-426655440000 --query "JobMetadata.JobState" --output text'

# Get detailed job metadata
aws snowball describe-job \
    --job-id JID123e4567-e89b-12d3-a456-426655440000 \
    --query 'JobMetadata.{State:JobState,Progress:JobLogUri,Resources:Resources,KMS:KmsKeyARN}' \
    --output json

# Check for failed jobs
aws snowball list-jobs \
    --query 'JobListEntries[?JobState==`Failed`]' \
    --output table

# Get job logs location
aws snowball describe-job \
    --job-id JID123e4567-e89b-12d3-a456-426655440000 \
    --query 'JobMetadata.JobLogUri' \
    --output text
```

#### Bulk Operations
```bash
# Cancel multiple jobs
for job_id in JID123-001 JID123-002 JID123-003; do
  echo "Cancelling job: $job_id"
  aws snowball cancel-job --job-id $job_id
done

# Check status of multiple jobs
for job_id in $(aws snowball list-jobs --query 'JobListEntries[*].JobId' --output text); do
  status=$(aws snowball describe-job --job-id $job_id --query 'JobMetadata.JobState' --output text)
  echo "Job: $job_id - Status: $status"
done

# Export job details to CSV
aws snowball list-jobs \
    --query 'JobListEntries[*].[JobId,JobType,JobState,CreationDate]' \
    --output text | \
    awk 'BEGIN {print "JobId,Type,State,CreationDate"} {print $1","$2","$3","$4}' > jobs.csv
```

### IAM Policy for Snow Family

#### Example IAM Policies
```bash
# Create IAM role for Snowball
cat > snowball-trust-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "importexport.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

awsiam create-role \
    --role-name SnowballImportExportRole \
    --assume-role-policy-document file://snowball-trust-policy.json

# Attach S3 permissions policy
cat > snowball-s3-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListBucket",
        "s3:GetBucketLocation"
      ],
      "Resource": [
        "arn:aws:s3:::my-snowball-bucket",
        "arn:aws:s3:::my-snowball-bucket/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "kms:Decrypt",
        "kms:Encrypt",
        "kms:GenerateDataKey"
      ],
      "Resource": "arn:aws:kms:us-east-1:123456789012:key/*"
    }
  ]
}
EOF

aws iam put-role-policy \
    --role-name SnowballImportExportRole \
    --policy-name SnowballS3Access \
    --policy-document file://snowball-s3-policy.json
```

### Troubleshooting Commands

#### Common Issues and Solutions
```bash
# Verify KMS key permissions
aws kms describe-key \
    --key-id abcd1234-a123-456a-a12b-a123b4cd56ef \
    --query 'KeyMetadata.{KeyId:KeyId,State:KeyState,Used:KeyUsage}'

# Check IAM role permissions
aws iam get-role-policy \
    --role-name SnowballRole \
    --policy-name SnowballPolicy

# Verify S3 bucket exists and is accessible
aws s3 ls s3://my-import-bucket/

# Check if address is valid
aws snowball describe-address \
    --address-id ADID1234567890abc

# Validate job configuration before creation
aws snowball describe-job \
    --job-id JID123e4567-e89b-12d3-a456-426655440000 \
    --query 'JobMetadata.{Resources:Resources,Role:RoleARN,KMS:KmsKeyARN,Address:ShippingDetails.ShippingAddress}' \
    --output json
```

---
## Practice Questions

### Question 1
A company needs to migrate 60 TB of data to AWS. Their internet connection would take 90 days to complete the transfer. Which is the MOST cost-effective solution?

A) AWS Direct Connect  
B) AWS Snowcone  
C) AWS Snowball Edge Storage Optimized  
D) AWS Snowmobile  

**Answer: C** - Snowball Edge SO can hold 80 TB, sufficient for 60 TB, and is more cost-effective than Snowmobile for this data size.

### Question 2
A research team needs to collect and process sensor data in Antarctica with limited connectivity. They need compute capability and must be able to carry the device. Which solution is BEST?

A) AWS Snowball Edge Compute Optimized  
B) AWS Snowcone  
C) AWS Snowmobile  
D) EC2 instances with EBS  

**Answer: B** - Snowcone is portable (fits in backpack), has compute capability, and works in disconnected environments.

### Question 3
A company is shutting down a datacenter with 40 PB of data. Which AWS service should they use for the migration?

A) Multiple Snowball Edge devices  
B) AWS Snowmobile  
C) AWS Direct Connect  
D) AWS DataSync  

**Answer: B** - For 40 PB, Snowmobile is the most appropriate. While multiple Snowball Edge could work, Snowmobile is designed for exabyte-scale migrations.

### Question 4
Which Snow Family device supports GPU for machine learning inference at the edge?

A) Snowcone  
B) Snowball Edge Storage Optimized  
C) Snowball Edge Compute Optimized  
D) Snowmobile  

**Answer: C** - Only Snowball Edge Compute Optimized has an optional NVIDIA V100 GPU.

### Question 5
A company is using Snowball Edge and wants to ensure the highest level of data security. Which encryption option should they use?

A) No encryption (faster transfer)  
B) AWS managed encryption key  
C) Customer managed KMS key  
D) Client-side encryption only  

**Answer: C** - Customer managed KMS key provides the highest level of control while still using AWS encryption. All Snow devices use encryption by default.

---

## Summary

AWS Snow Family provides physical data transfer and edge computing solutions:

- **Snowcone**: Portable, 8-14 TB, edge compute
- **Snowball Edge SO**: Large storage, 80 TB, clustering
- **Snowball Edge CO**: Heavy compute, GPU option
- **Snowmobile**: Exabyte scale, 100 PB

**Key Decision Points**:
1. Data size determines device type
2. Edge compute needs → Snowball Edge
3. Portability → Snowcone
4. Massive scale → Snowmobile
5. Always encrypted with KMS

Remember: Physical transfer is often faster than network for large datasets!
