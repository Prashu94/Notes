# Google Compute Engine - Associate Cloud Engineer (ACE) Comprehensive Guide

## Table of Contents
1. [Overview](#overview)
2. [Core Concepts](#core-concepts)
3. [Machine Types & Families](#machine-types--families)
4. [Creating & Managing Instances](#creating--managing-instances)
5. [Storage Options](#storage-options)
6. [Networking](#networking)
7. [Instance Templates & Groups](#instance-templates--groups)
8. [Access & Security](#access--security)
9. [Monitoring & Maintenance](#monitoring--maintenance)
10. [ACE Exam Tips](#ace-exam-tips)

---

## Overview

Google Compute Engine is an Infrastructure as a Service (IaaS) offering that provides virtual machines (VMs) running on Google's infrastructure. As an ACE candidate, you need to understand how to create, configure, manage, and troubleshoot Compute Engine instances.

**Key Characteristics:**
- **IaaS:** Full control over VM configuration
- **Scalable:** From single instance to thousands
- **Flexible:** Custom machine types and configurations
- **Global:** Deploy in any GCP region/zone

---

## Core Concepts

### What is a Compute Engine Instance?

A Compute Engine instance can be:
- **VM Instance:** Virtual machine with a hypervisor
- **Bare Metal Instance:** Physical server without hypervisor (machine type ends in `-metal`)

### Projects & Organization

- Each instance belongs to one GCP project
- Instances are zonal resources (tied to a specific zone)
- Projects can have many instances across multiple zones/regions

### Instance Lifecycle

```
PROVISIONING → STAGING → RUNNING ⇄ STOPPING → STOPPED → TERMINATED
```

**States:**
- **PROVISIONING:** Resources being allocated
- **STAGING:** Starting up
- **RUNNING:** Instance is active
- **STOPPING:** Shutting down
- **STOPPED:** Instance is stopped (no charges for CPU/RAM, only disk)
- **TERMINATED:** Instance deleted

---

## Machine Types & Families

### Machine Families

| Family | Use Case | Example Series |
|--------|----------|----------------|
| **General-Purpose** | Balanced CPU/memory for most workloads | N4, N2, N2D, N1, E2, T2D, T2A |
| **Compute-Optimized** | High performance per core | C4, C3, C2, C2D, H3 |
| **Memory-Optimized** | High memory-to-CPU ratio | M4, M3, M2, M1 |
| **Storage-Optimized** | High local storage throughput | Z3 |
| **Accelerator-Optimized** | GPU/TPU workloads | A3, A2, G2 |

### Predefined Machine Types

Format: `[SERIES]-[TYPE]-[CPUs]`

- **highcpu:** 1-3 GB RAM per vCPU
- **standard:** 3-7 GB RAM per vCPU
- **highmem:** 7-12 GB RAM per vCPU

**Examples:**
```bash
n2-standard-4    # 4 vCPUs, 16 GB RAM
n2-highcpu-8     # 8 vCPUs, 16 GB RAM
n2-highmem-2     # 2 vCPUs, 16 GB RAM
```

### Custom Machine Types

Create VMs with specific vCPU and memory combinations:

```bash
gcloud compute instances create custom-vm \
  --custom-cpu=6 \
  --custom-memory=30GB \
  --zone=us-central1-a
```

**Limitations:**
- Only available for N1, N2, N2D, E2 series
- Memory must be between 0.9 GB and 6.5 GB per vCPU (N1)
- 5% premium over predefined types

### Shared-Core Machine Types

For lightweight, burstable workloads:
- **f1-micro:** 0.2 vCPU, 600 MB RAM (Always Free tier eligible)
- **g1-small:** 0.5 vCPU, 1.7 GB RAM
- **e2-micro, e2-small, e2-medium:** Newer shared-core options

---

## Creating & Managing Instances

### Creating an Instance (Console)

1. Navigate to **Compute Engine > VM instances**
2. Click **Create Instance**
3. Configure:
   - **Name:** Unique within project-zone
   - **Region/Zone:** Geographic location
   - **Machine type:** Select family/series/size
   - **Boot disk:** OS image and disk size
   - **Firewall:** Allow HTTP/HTTPS traffic (optional)
4. Click **Create**

### Creating an Instance (gcloud)

**Basic Command:**
```bash
gcloud compute instances create INSTANCE_NAME \
  --zone=us-central1-a \
  --machine-type=n2-standard-2 \
  --image-family=debian-11 \
  --image-project=debian-cloud
```

**With Additional Options:**
```bash
gcloud compute instances create web-server \
  --zone=us-east1-b \
  --machine-type=e2-medium \
  --boot-disk-size=20GB \
  --boot-disk-type=pd-standard \
  --tags=http-server,https-server \
  --metadata=startup-script='#! /bin/bash
    apt-get update
    apt-get install -y apache2'
```

### Managing Instance State

**Start an instance:**
```bash
gcloud compute instances start INSTANCE_NAME --zone=ZONE
```

**Stop an instance:**
```bash
gcloud compute instances stop INSTANCE_NAME --zone=ZONE
```

**Reset (hard restart):**
```bash
gcloud compute instances reset INSTANCE_NAME --zone=ZONE
```

**Delete an instance:**
```bash
gcloud compute instances delete INSTANCE_NAME --zone=ZONE
```

### Viewing Instance Details

```bash
# List all instances
gcloud compute instances list

# Describe specific instance
gcloud compute instances describe INSTANCE_NAME --zone=ZONE

# View serial port output (useful for debugging)
gcloud compute instances get-serial-port-output INSTANCE_NAME --zone=ZONE
```

---

## Storage Options

### Boot Disks

Every instance has a boot disk containing the OS.

**Disk Types:**
- **Standard Persistent Disk (pd-standard):** HDD, lower cost
- **Balanced Persistent Disk (pd-balanced):** SSD, good balance (default)
- **SSD Persistent Disk (pd-ssd):** SSD, high performance
- **Extreme Persistent Disk (pd-extreme):** Highest performance

**Create with Specific Boot Disk:**
```bash
gcloud compute instances create my-instance \
  --boot-disk-size=50GB \
  --boot-disk-type=pd-ssd \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud
```

### Additional Persistent Disks

Attach extra disks to instances:

**Create a disk:**
```bash
gcloud compute disks create my-data-disk \
  --size=100GB \
  --type=pd-standard \
  --zone=us-central1-a
```

**Attach to running instance:**
```bash
gcloud compute instances attach-disk INSTANCE_NAME \
  --disk=my-data-disk \
  --zone=us-central1-a
```

**Detach disk:**
```bash
gcloud compute instances detach-disk INSTANCE_NAME \
  --disk=my-data-disk \
  --zone=us-central1-a
```

### Local SSDs

Temporary, high-performance local storage:

```bash
gcloud compute instances create my-instance \
  --local-ssd=interface=NVME \
  --zone=us-central1-a
```

**Important:** Data is lost when instance stops!

### Snapshots

Backup persistent disks:

**Create snapshot:**
```bash
gcloud compute disks snapshot DISK_NAME \
  --snapshot-names=my-snapshot \
  --zone=ZONE
```

**Create disk from snapshot:**
```bash
gcloud compute disks create restored-disk \
  --source-snapshot=my-snapshot \
  --zone=us-central1-a
```

---

## Networking

### VPC Networks

Every instance must be in a VPC network and subnet.

**Create instance in specific network:**
```bash
gcloud compute instances create my-instance \
  --network=my-vpc \
  --subnet=my-subnet \
  --zone=us-central1-a
```

### IP Addresses

**Internal IP:**
- Automatically assigned from subnet range
- Used for communication within VPC

**External IP:**
- Optional
- Can be ephemeral (changes on restart) or static

**Reserve static external IP:**
```bash
gcloud compute addresses create my-static-ip --region=us-central1
```

**Create instance with static IP:**
```bash
gcloud compute instances create my-instance \
  --address=my-static-ip \
  --zone=us-central1-a
```

### Firewall Rules

Control traffic to/from instances using network tags:

**Create firewall rule:**
```bash
gcloud compute firewall-rules create allow-http \
  --network=default \
  --allow=tcp:80 \
  --source-ranges=0.0.0.0/0 \
  --target-tags=http-server
```

**Apply tag to instance:**
```bash
gcloud compute instances add-tags INSTANCE_NAME \
  --tags=http-server \
  --zone=ZONE
```

---

## Instance Templates & Groups

### Instance Templates

Reusable configuration for creating instances:

```bash
gcloud compute instance-templates create web-template \
  --machine-type=e2-medium \
  --boot-disk-size=20GB \
  --image-family=debian-11 \
  --image-project=debian-cloud \
  --tags=http-server \
  --metadata=startup-script='#!/bin/bash
    apt-get update
    apt-get install -y apache2'
```

### Managed Instance Groups (MIGs)

Group of identical instances created from a template:

**Create MIG:**
```bash
gcloud compute instance-groups managed create web-mig \
  --base-instance-name=web \
  --template=web-template \
  --size=3 \
  --zone=us-central1-a
```

**Autoscaling:**
```bash
gcloud compute instance-groups managed set-autoscaling web-mig \
  --max-num-replicas=10 \
  --min-num-replicas=2 \
  --target-cpu-utilization=0.6 \
  --cool-down-period=90 \
  --zone=us-central1-a
```

---

## Access & Security

### SSH Access (Linux)

**Via Console:** Click **SSH** button next to instance

**Via gcloud:**
```bash
gcloud compute ssh INSTANCE_NAME --zone=ZONE
```

**Via SSH client:**
```bash
ssh -i ~/.ssh/my-key USER@EXTERNAL_IP
```

### OS Login

Manage SSH access using IAM:

**Enable OS Login:**
```bash
gcloud compute instances add-metadata INSTANCE_NAME \
  --metadata=enable-oslogin=TRUE \
  --zone=ZONE
```

**Grant SSH access:**
```bash
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member=user:EMAIL \
  --role=roles/compute.osLogin
```

### Service Accounts

Instances use service accounts for API access:

```bash
gcloud compute instances create my-instance \
  --service-account=SA_EMAIL \
  --scopes=cloud-platform \
  --zone=ZONE
```

---

## Monitoring & Maintenance

### Cloud Monitoring

View CPU, disk, network metrics in Console or via API.

### Startup Scripts

Run scripts when instance boots:

```bash
gcloud compute instances create my-instance \
  --metadata-from-file=startup-script=startup.sh \
  --zone=ZONE
```

### Metadata

Store custom key-value pairs:

```bash
gcloud compute instances add-metadata INSTANCE_NAME \
  --metadata=KEY=VALUE \
  --zone=ZONE
```

**Access metadata from within instance:**
```bash
curl "http://metadata.google.internal/computeMetadata/v1/instance/name" \
  -H "Metadata-Flavor: Google"
```

---

## ACE Exam Tips

1. **Machine Types:** Know the difference between predefined, custom, and shared-core types. Remember f1-micro is Always Free tier eligible.

2. **Disk Types:** Understand when to use standard vs. SSD vs. local SSD. Remember local SSDs are ephemeral!

3. **Snapshots vs Images:** Snapshots backup disks; images are for creating instances.

4. **Instance Groups:** Managed groups use templates and support autoscaling. Unmanaged groups are just collections.

5. **Preemptible VMs:** 60-80% cheaper but can be terminated anytime. Max 24 hours. Use for fault-tolerant batch workloads.

6. **Spot VMs:** Similar to preemptible but no 24-hour limit. Use for modern workloads.

7. **gcloud Commands:** Memorize:
   - `gcloud compute instances create`
   - `gcloud compute instances start/stop/delete`
   - `gcloud compute disks snapshot`
   - `gcloud compute instance-templates create`

8. **Zones vs Regions:** Instances are zonal. Some resources (like disks) can't move zones easily.

9. **Static IPs:** Reserve external IPs if you need persistent addresses across restarts.

10. **Metadata Server:** Instances can query `metadata.google.internal` for configuration and credentials.
