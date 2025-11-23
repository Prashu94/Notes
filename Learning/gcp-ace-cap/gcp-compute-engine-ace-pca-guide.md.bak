# Google Cloud Compute Engine - ACE & PCA Certification Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Compute Engine Fundamentals](#compute-engine-fundamentals)
3. [Instance Types and Machine Families](#instance-types-and-machine-families)
4. [Instance Management](#instance-management)
5. [Storage Options](#storage-options)
6. [Networking](#networking)
7. [Security](#security)
8. [High Availability and Scaling](#high-availability-and-scaling)
9. [Monitoring and Logging](#monitoring-and-logging)
10. [Cost Optimization](#cost-optimization)
11. [Best Practices](#best-practices)
12. [ACE-Specific Topics](#ace-specific-topics)
13. [PCA-Specific Topics](#pca-specific-topics)
14. [Hands-On Labs](#hands-on-labs)
15. [Common Exam Scenarios](#common-exam-scenarios)

---

## Introduction

Google Cloud Compute Engine is Infrastructure as a Service (IaaS) that lets you run virtual machines on Google's infrastructure. This guide covers essential concepts for both Associate Cloud Engineer (ACE) and Professional Cloud Architect (PCA) certifications.

### Key Benefits
- **Performance**: Custom machine types and high-performance computing
- **Flexibility**: Multiple operating systems and configurations
- **Scalability**: Auto-scaling and load balancing capabilities
- **Security**: Identity and Access Management (IAM) integration
- **Cost-effectiveness**: Sustained use discounts and preemptible instances

---

## Compute Engine Fundamentals

### Core Concepts

#### Virtual Machine Instances
```bash
# Create a basic VM instance
gcloud compute instances create my-instance \
    --zone=us-central1-a \
    --machine-type=e2-medium \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud
```

#### Key Components
- **Instance**: Virtual machine running on Google's infrastructure
- **Machine Type**: Predefined or custom hardware configuration
- **Image**: Operating system and root filesystem
- **Disk**: Persistent storage attached to instances
- **Network**: VPC networks for instance communication

### Instance Lifecycle
1. **PROVISIONING**: Resources being allocated
2. **STAGING**: Resources acquired, instance being prepared
3. **RUNNING**: Instance is running and ready to use
4. **STOPPING**: Instance is being stopped
5. **STOPPED**: Instance is shut down and not running
6. **TERMINATED**: Instance has been permanently deleted

---

## Instance Types and Machine Families

### General-Purpose Machine Families

#### E2 Series (Cost-Optimized)
- **Use Cases**: Web servers, small databases, development environments
- **Features**: Balanced CPU and memory, burstable performance
- **Options**: e2-micro to e2-highmem-16

```bash
# Create E2 instance
gcloud compute instances create e2-instance \
    --machine-type=e2-standard-4 \
    --zone=us-central1-a
```

#### N2 Series (Balanced)
- **Use Cases**: General workloads, enterprise applications
- **Features**: Intel Cascade Lake processors
- **Options**: n2-standard-2 to n2-highmem-128

#### N2D Series (AMD-based)
- **Use Cases**: Scale-out workloads, high-performance computing
- **Features**: AMD EPYC processors
- **Cost**: Up to 20% lower cost than Intel equivalents

### Compute-Optimized Machine Families

#### C2 Series (High-Performance)
- **Use Cases**: Gaming, HPC, scientific computing
- **Features**: High CPU performance, Intel Cascade Lake
- **Options**: c2-standard-4 to c2-standard-60

### Memory-Optimized Machine Families

#### M2 Series (Ultra High-Memory)
- **Use Cases**: In-memory databases, real-time analytics
- **Features**: Up to 12TB of memory per instance
- **Options**: m2-ultramem-208 to m2-megamem-416

### Custom Machine Types
```bash
# Create custom machine type
gcloud compute instances create custom-instance \
    --custom-cpu=4 \
    --custom-memory=8GB \
    --zone=us-central1-a
```

### Accelerator-Optimized Instances
- **GPUs**: NVIDIA Tesla K80, P4, P100, V100, T4, A100
- **TPUs**: Tensor Processing Units for machine learning

```bash
# Create GPU instance
gcloud compute instances create gpu-instance \
    --accelerator=type=nvidia-tesla-t4,count=1 \
    --machine-type=n1-standard-4 \
    --maintenance-policy=TERMINATE \
    --zone=us-central1-a
```

---

## Instance Management

### Creating Instances

#### Console Method
1. Navigate to Compute Engine > VM instances
2. Click "Create Instance"
3. Configure machine type, boot disk, and network
4. Set firewall rules and access scopes

#### gcloud CLI Method
```bash
# Comprehensive instance creation
gcloud compute instances create web-server \
    --zone=us-central1-a \
    --machine-type=e2-standard-2 \
    --network-interface=network-tier=PREMIUM,subnet=default \
    --maintenance-policy=MIGRATE \
    --provisioning-model=STANDARD \
    --service-account=compute-sa@project.iam.gserviceaccount.com \
    --scopes=https://www.googleapis.com/auth/cloud-platform \
    --tags=http-server,https-server \
    --create-disk=auto-delete=yes,boot=yes,device-name=web-server,image=projects/ubuntu-os-cloud/global/images/ubuntu-2004-focal-v20231213,mode=rw,size=10,type=projects/PROJECT_ID/zones/us-central1-a/diskTypes/pd-balanced \
    --no-shielded-secure-boot \
    --shielded-vtpm \
    --shielded-integrity-monitoring \
    --labels=environment=production,team=webdev \
    --reservation-affinity=any
```

### Managing Instances

#### Start/Stop/Restart Operations
```bash
# Stop instance
gcloud compute instances stop INSTANCE_NAME --zone=ZONE

# Start instance
gcloud compute instances start INSTANCE_NAME --zone=ZONE

# Restart instance
gcloud compute instances reset INSTANCE_NAME --zone=ZONE

# Delete instance
gcloud compute instances delete INSTANCE_NAME --zone=ZONE
```

#### Resizing Instances
```bash
# Stop instance first
gcloud compute instances stop my-instance --zone=us-central1-a

# Change machine type
gcloud compute instances set-machine-type my-instance \
    --machine-type=e2-standard-4 \
    --zone=us-central1-a

# Start instance
gcloud compute instances start my-instance --zone=us-central1-a
```

### Instance Templates
```bash
# Create instance template
gcloud compute instance-templates create web-template \
    --machine-type=e2-medium \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud \
    --boot-disk-size=20GB \
    --boot-disk-type=pd-ssd \
    --tags=web-server \
    --metadata=startup-script='#!/bin/bash
apt-get update
apt-get install -y apache2
systemctl start apache2
systemctl enable apache2'
```

---

## Storage Options

### Persistent Disks

#### Standard Persistent Disk (pd-standard)
- **Performance**: Lower IOPS, cost-effective
- **Use Cases**: Sequential workloads, backup storage
- **IOPS**: Up to 15,000 read IOPS, 15,000 write IOPS

#### Balanced Persistent Disk (pd-balanced)
- **Performance**: Balance of performance and cost
- **Use Cases**: General workloads, boot disks
- **IOPS**: Up to 80,000 read IOPS, 30,000 write IOPS

#### SSD Persistent Disk (pd-ssd)
- **Performance**: High IOPS and throughput
- **Use Cases**: Databases, high-performance applications
- **IOPS**: Up to 100,000 read IOPS, 100,000 write IOPS

#### Extreme Persistent Disk (pd-extreme)
- **Performance**: Highest performance option
- **Use Cases**: Mission-critical applications
- **IOPS**: Up to 100,000 IOPS with configurable performance

```bash
# Create and attach persistent disk
gcloud compute disks create my-disk \
    --size=100GB \
    --type=pd-ssd \
    --zone=us-central1-a

gcloud compute instances attach-disk my-instance \
    --disk=my-disk \
    --zone=us-central1-a
```

### Local SSDs
- **Performance**: Very high IOPS and low latency
- **Limitations**: Data doesn't persist across instance stops
- **Use Cases**: Temporary storage, caching, scratch disks

```bash
# Create instance with local SSD
gcloud compute instances create ssd-instance \
    --local-ssd=interface=SCSI \
    --zone=us-central1-a
```

### Regional Persistent Disks
- **Availability**: Synchronous replication across zones
- **Use Cases**: High availability applications
- **Performance**: Same as zonal disks but with higher availability

```bash
# Create regional persistent disk
gcloud compute disks create regional-disk \
    --size=500GB \
    --region=us-central1 \
    --type=pd-ssd
```

### Storage Performance Optimization

#### Disk Performance Factors
1. **Disk Type**: SSD > Balanced > Standard
2. **Disk Size**: Larger disks have higher performance limits
3. **Instance Type**: More vCPUs allow higher IOPS
4. **File System**: ext4, xfs optimization

#### Performance Monitoring
```bash
# Monitor disk performance
gcloud compute operations list --filter="operationType:compute.disks"
```

---

## Networking

### VPC Networks

#### Default Network
- Automatically created for each project
- One subnet per region with predefined firewall rules
- Suitable for simple deployments

#### Custom Networks
```bash
# Create custom VPC
gcloud compute networks create custom-vpc \
    --subnet-mode=custom \
    --bgp-routing-mode=global

# Create subnet
gcloud compute networks subnets create web-subnet \
    --network=custom-vpc \
    --range=10.1.0.0/24 \
    --region=us-central1
```

### Firewall Rules
```bash
# Allow HTTP traffic
gcloud compute firewall-rules create allow-http \
    --allow=tcp:80 \
    --source-ranges=0.0.0.0/0 \
    --target-tags=http-server

# Allow SSH from specific source
gcloud compute firewall-rules create allow-ssh-from-office \
    --allow=tcp:22 \
    --source-ranges=203.0.113.0/24 \
    --target-tags=ssh-server
```

### Load Balancing

#### HTTP(S) Load Balancer
```bash
# Create instance group
gcloud compute instance-groups managed create web-group \
    --base-instance-name=web \
    --size=3 \
    --template=web-template \
    --zone=us-central1-a

# Create health check
gcloud compute health-checks create http web-health-check \
    --port=80 \
    --request-path=/health

# Create backend service
gcloud compute backend-services create web-backend \
    --protocol=HTTP \
    --health-checks=web-health-check \
    --global

# Add instance group to backend
gcloud compute backend-services add-backend web-backend \
    --instance-group=web-group \
    --instance-group-zone=us-central1-a \
    --global
```

### External IP Addresses

#### Ephemeral IP
- Automatically assigned when instance is created
- Changes when instance is stopped and started
- No additional cost

#### Static IP
```bash
# Reserve static IP
gcloud compute addresses create web-ip \
    --global

# Assign to instance
gcloud compute instances add-access-config my-instance \
    --access-config-name="external-nat" \
    --address=web-ip \
    --zone=us-central1-a
```

---

## Security

### Identity and Access Management (IAM)

#### Service Accounts
```bash
# Create service account
gcloud iam service-accounts create compute-sa \
    --display-name="Compute Service Account"

# Grant roles
gcloud projects add-iam-policy-binding PROJECT_ID \
    --member="serviceAccount:compute-sa@PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/compute.instanceAdmin.v1"
```

#### Access Scopes
- Define permissions for service account on instance
- Can be set during instance creation or modification

```bash
# Create instance with specific scopes
gcloud compute instances create secure-instance \
    --scopes=storage-ro,logging-write,monitoring-write
```

### Shielded VMs
- **Secure Boot**: Ensures authentic operating system
- **Virtual Trusted Platform Module (vTPM)**: Hardware-based security
- **Integrity Monitoring**: Detects unauthorized changes

```bash
# Create Shielded VM
gcloud compute instances create shielded-vm \
    --shielded-secure-boot \
    --shielded-vtpm \
    --shielded-integrity-monitoring
```

### OS Login
- Manages SSH keys through IAM
- Two-factor authentication support
- Audit logging for SSH access

```bash
# Enable OS Login on instance
gcloud compute instances add-metadata my-instance \
    --metadata enable-oslogin=TRUE \
    --zone=us-central1-a
```

### Network Security

#### Private Google Access
- Allows instances without external IP to access Google services
- Configured at subnet level

```bash
# Enable Private Google Access
gcloud compute networks subnets update web-subnet \
    --enable-private-ip-google-access \
    --region=us-central1
```

#### VPC Service Controls
- Create security perimeters around Google Cloud resources
- Prevent data exfiltration

---

## High Availability and Scaling

### Managed Instance Groups (MIGs)

#### Creating MIGs
```bash
# Create managed instance group
gcloud compute instance-groups managed create web-mig \
    --base-instance-name=web \
    --template=web-template \
    --size=3 \
    --zone=us-central1-a
```

#### Auto Scaling
```bash
# Create autoscaling policy
gcloud compute instance-groups managed set-autoscaling web-mig \
    --max-num-replicas=10 \
    --min-num-replicas=2 \
    --target-cpu-utilization=0.75 \
    --zone=us-central1-a
```

#### Update Strategies
```bash
# Rolling update
gcloud compute instance-groups managed rolling-action start-update web-mig \
    --version=template=new-web-template \
    --zone=us-central1-a
```

### Regional MIGs
- Distribute instances across multiple zones
- Automatic failover and load distribution

```bash
# Create regional MIG
gcloud compute instance-groups managed create regional-web-mig \
    --base-instance-name=web \
    --template=web-template \
    --size=6 \
    --region=us-central1 \
    --target-distribution-shape=BALANCED
```

### Health Checks
```bash
# Create TCP health check
gcloud compute health-checks create tcp tcp-health-check \
    --port=80 \
    --check-interval=10s \
    --timeout=5s \
    --healthy-threshold=2 \
    --unhealthy-threshold=3
```

### Sole-Tenant Nodes
- Dedicated physical servers for compliance requirements
- Isolation from other customers' workloads

```bash
# Create node template
gcloud compute sole-tenancy node-templates create my-template \
    --node-type=n1-node-96-624 \
    --region=us-central1

# Create node group
gcloud compute sole-tenancy node-groups create my-group \
    --node-template=my-template \
    --target-size=2 \
    --zone=us-central1-a
```

---

## Monitoring and Logging

### Cloud Monitoring

#### Predefined Metrics
- CPU utilization
- Disk I/O
- Network traffic
- Memory usage (with Monitoring agent)

#### Custom Metrics
```bash
# Install monitoring agent
curl -sSO https://dl.google.com/cloudagents/add-monitoring-agent-repo.sh
sudo bash add-monitoring-agent-repo.sh --also-install
```

#### Alerting Policies
```bash
# Create alerting policy via CLI (complex - usually done via console)
gcloud alpha monitoring policies create --policy-from-file=policy.yaml
```

### Cloud Logging

#### Log Types
- **System logs**: Operating system events
- **Application logs**: Application-generated logs
- **Security logs**: Authentication and authorization events

#### Log Export
```bash
# Create log sink
gcloud logging sinks create my-sink \
    bigquery.googleapis.com/projects/PROJECT_ID/datasets/logs_dataset \
    --log-filter='resource.type="gce_instance"'
```

### Performance Monitoring

#### Cloud Profiler
- Continuous profiling for production applications
- CPU and memory usage analysis

#### Cloud Trace
- Distributed tracing for applications
- Latency analysis and bottleneck identification

---

## Cost Optimization

### Pricing Models

#### Sustained Use Discounts
- Automatic discounts for running instances
- Up to 30% discount for continuous usage
- Applied automatically, no configuration needed

#### Committed Use Discounts
```bash
# Purchase 1-year commitment
gcloud compute commitments create my-commitment \
    --plan=12-month \
    --region=us-central1 \
    --resources=type=VCPU,amount=100
```

#### Preemptible Instances
- Up to 80% cost savings
- Can be terminated with 30-second notice
- Ideal for batch processing and fault-tolerant workloads

```bash
# Create preemptible instance
gcloud compute instances create preemptible-instance \
    --preemptible \
    --machine-type=e2-standard-4 \
    --zone=us-central1-a
```

#### Spot VMs
- Even higher savings than preemptible instances
- Similar termination behavior
- No maximum runtime limit

```bash
# Create Spot VM
gcloud compute instances create spot-instance \
    --provisioning-model=SPOT \
    --machine-type=e2-standard-4 \
    --zone=us-central1-a
```

### Right-Sizing Recommendations
- Analyze usage patterns and recommend optimal machine types
- Available in Cloud Console and via Recommender API

### Storage Optimization
- Use appropriate disk types for workloads
- Regular snapshots with retention policies
- Delete unused persistent disks

```bash
# Create snapshot schedule
gcloud compute resource-policies create snapshot-schedule daily-backup \
    --max-retention-days=7 \
    --start-time=02:00 \
    --daily-schedule \
    --region=us-central1
```

---

## Best Practices

### Instance Management Best Practices

#### 1. Use Instance Templates
- Standardize configurations
- Enable consistent deployments
- Simplify scaling operations

#### 2. Implement Proper Tagging
```bash
# Add labels for organization
gcloud compute instances add-labels my-instance \
    --labels=environment=prod,team=backend,cost-center=engineering \
    --zone=us-central1-a
```

#### 3. Regular Updates and Patching
```bash
# Automate updates with startup scripts
#!/bin/bash
apt-get update
apt-get upgrade -y
```

### Security Best Practices

#### 1. Principle of Least Privilege
- Use specific IAM roles instead of broad permissions
- Regular access reviews and cleanup

#### 2. Network Security
- Use custom VPCs with specific subnets
- Implement proper firewall rules
- Enable Private Google Access where appropriate

#### 3. Enable Security Features
- Use Shielded VMs for sensitive workloads
- Enable OS Login for centralized access management
- Implement proper service account management

### Performance Best Practices

#### 1. Choose Appropriate Machine Types
- Match CPU and memory requirements to workload
- Use custom machine types for specific needs
- Consider accelerators for specialized workloads

#### 2. Storage Optimization
- Use SSD persistent disks for high-performance needs
- Implement proper disk sizing
- Consider local SSDs for temporary high-performance storage

#### 3. Network Optimization
- Use appropriate network tier (Premium vs Standard)
- Implement proper load balancing
- Consider proximity to users and services

---

## ACE-Specific Topics

### Core ACE Skills for Compute Engine

#### 1. Basic Instance Operations
- Creating, starting, stopping, and deleting instances
- Understanding machine types and their use cases
- Basic networking configuration

#### 2. Storage Management
- Attaching and detaching persistent disks
- Creating and managing snapshots
- Understanding storage types and their performance characteristics

#### 3. Basic Security
- Configuring firewall rules
- Using service accounts with instances
- Understanding SSH key management

#### 4. Monitoring Basics
- Setting up basic monitoring and alerting
- Understanding Cloud Logging for instances
- Basic troubleshooting techniques

### ACE Exam Focus Areas

#### Instance Lifecycle Management
```bash
# Common ACE tasks
# 1. Create instance with specific configuration
gcloud compute instances create ace-instance \
    --machine-type=e2-medium \
    --boot-disk-size=20GB \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud \
    --zone=us-central1-a

# 2. Resize instance
gcloud compute instances stop ace-instance --zone=us-central1-a
gcloud compute instances set-machine-type ace-instance \
    --machine-type=e2-standard-2 --zone=us-central1-a
gcloud compute instances start ace-instance --zone=us-central1-a

# 3. Add persistent disk
gcloud compute disks create ace-disk \
    --size=100GB --zone=us-central1-a
gcloud compute instances attach-disk ace-instance \
    --disk=ace-disk --zone=us-central1-a
```

#### Basic Auto Scaling
```bash
# Create simple managed instance group
gcloud compute instance-groups managed create ace-mig \
    --base-instance-name=ace-web \
    --template=web-template \
    --size=2 \
    --zone=us-central1-a

# Enable autoscaling
gcloud compute instance-groups managed set-autoscaling ace-mig \
    --max-num-replicas=5 \
    --min-num-replicas=2 \
    --target-cpu-utilization=0.8 \
    --zone=us-central1-a
```

---

## PCA-Specific Topics

### Advanced Architecture Patterns

#### 1. Multi-Region Deployments
```bash
# Regional MIG for high availability
gcloud compute instance-groups managed create pca-regional-mig \
    --base-instance-name=pca-app \
    --template=app-template \
    --size=6 \
    --region=us-central1 \
    --target-distribution-shape=BALANCED
```

#### 2. Hybrid Connectivity
- VPN connections for hybrid cloud scenarios
- Dedicated Interconnect for high-bandwidth requirements
- Partner Interconnect for third-party connectivity

#### 3. Advanced Security Architectures
```bash
# VPC Service Controls perimeter
gcloud access-context-manager perimeters create production-perimeter \
    --policy=POLICY_ID \
    --title="Production Environment" \
    --resources=projects/PROJECT_ID \
    --restricted-services=compute.googleapis.com
```

### Enterprise-Grade Solutions

#### 1. Disaster Recovery Strategies
- **RTO/RPO Planning**: Recovery Time/Point Objectives
- **Cross-region backups**: Automated snapshot replication
- **Failover procedures**: Automated and manual processes

#### 2. Compliance and Governance
```bash
# Organization policies for Compute Engine
gcloud resource-manager org-policies set-policy compute-policy.yaml \
    --organization=ORGANIZATION_ID
```

#### 3. Cost Management at Scale
- **Billing budgets**: Automated cost controls
- **Resource quotas**: Prevent runaway spending
- **Rightsizing at scale**: Organization-wide optimization

### Migration Strategies

#### 1. Lift and Shift Migration
- **Assessment**: Current infrastructure analysis
- **Planning**: Migration timeline and dependencies
- **Execution**: Systematic workload migration

#### 2. Cloud-Native Refactoring
- **Microservices architecture**: Breaking monoliths
- **Containerization**: Docker and Kubernetes integration
- **Serverless integration**: Cloud Functions and Cloud Run

### Advanced Monitoring and Operations

#### 1. SRE Practices
```bash
# Custom metrics for SLI/SLO monitoring
gcloud monitoring metrics create \
    --descriptor-from-file=sli-descriptor.yaml
```

#### 2. Advanced Logging Architecture
```bash
# Centralized logging with multiple sinks
gcloud logging sinks create audit-sink \
    storage.googleapis.com/audit-logs-bucket \
    --log-filter='protoPayload.methodName:("compute.instances.insert" OR "compute.instances.delete")'
```

---

## Hands-On Labs

### Lab 1: Basic Instance Management (ACE Level)

#### Objective
Create and manage a web server instance with proper configuration.

#### Steps
```bash
# 1. Create instance with web server
gcloud compute instances create web-server \
    --zone=us-central1-a \
    --machine-type=e2-small \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud \
    --tags=http-server \
    --metadata=startup-script='#!/bin/bash
apt-get update
apt-get install -y apache2
systemctl start apache2
echo "<h1>Hello from $(hostname)</h1>" > /var/www/html/index.html'

# 2. Create firewall rule
gcloud compute firewall-rules create allow-http \
    --allow=tcp:80 \
    --source-ranges=0.0.0.0/0 \
    --target-tags=http-server

# 3. Get external IP and test
gcloud compute instances describe web-server \
    --zone=us-central1-a \
    --format='get(networkInterfaces[0].accessConfigs[0].natIP)'
```

### Lab 2: Auto-Scaling Web Application (PCA Level)

#### Objective
Deploy a scalable web application with load balancing and auto-scaling.

#### Steps
```bash
# 1. Create instance template
gcloud compute instance-templates create web-template \
    --machine-type=e2-medium \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud \
    --boot-disk-size=20GB \
    --boot-disk-type=pd-standard \
    --tags=web-server,http-server \
    --metadata=startup-script-url=gs://YOUR_BUCKET/startup.sh

# 2. Create managed instance group
gcloud compute instance-groups managed create web-mig \
    --base-instance-name=web \
    --template=web-template \
    --size=2 \
    --zone=us-central1-a

# 3. Configure autoscaling
gcloud compute instance-groups managed set-autoscaling web-mig \
    --max-num-replicas=10 \
    --min-num-replicas=2 \
    --target-cpu-utilization=0.75 \
    --zone=us-central1-a

# 4. Create health check
gcloud compute health-checks create http web-health-check \
    --port=80 \
    --request-path=/health \
    --check-interval=10s \
    --timeout=5s \
    --healthy-threshold=2 \
    --unhealthy-threshold=3

# 5. Create load balancer backend service
gcloud compute backend-services create web-backend \
    --protocol=HTTP \
    --health-checks=web-health-check \
    --global

# 6. Add instance group to backend
gcloud compute backend-services add-backend web-backend \
    --instance-group=web-mig \
    --instance-group-zone=us-central1-a \
    --global

# 7. Create URL map
gcloud compute url-maps create web-map \
    --default-service=web-backend

# 8. Create HTTP proxy
gcloud compute target-http-proxies create web-proxy \
    --url-map=web-map

# 9. Create forwarding rule
gcloud compute forwarding-rules create web-rule \
    --global \
    --target-http-proxy=web-proxy \
    --ports=80
```

### Lab 3: Multi-Region Deployment (PCA Level)

#### Objective
Deploy an application across multiple regions for high availability.

#### Implementation Details
1. **Regional MIGs**: Deploy in us-central1 and europe-west1
2. **Global Load Balancer**: Route traffic based on proximity
3. **Health Monitoring**: Implement comprehensive health checks
4. **Disaster Recovery**: Automated failover procedures

---

## Common Exam Scenarios

### ACE Exam Scenarios

#### Scenario 1: Instance Performance Issues
**Problem**: Web server responding slowly
**Solution Steps**:
1. Check CPU and memory utilization
2. Analyze disk I/O performance
3. Review network connectivity
4. Consider machine type upgrade
5. Implement monitoring alerts

#### Scenario 2: Storage Management
**Problem**: Running out of disk space
**Solution Steps**:
```bash
# 1. Check current disk usage
df -h

# 2. Create and attach new disk
gcloud compute disks create additional-storage \
    --size=200GB \
    --zone=us-central1-a

gcloud compute instances attach-disk my-instance \
    --disk=additional-storage \
    --zone=us-central1-a

# 3. Format and mount the disk
sudo mkfs.ext4 /dev/sdb
sudo mkdir /mnt/additional-storage
sudo mount /dev/sdb /mnt/additional-storage
```

#### Scenario 3: Security Compliance
**Problem**: Instance needs restricted access
**Solution Steps**:
1. Remove external IP address
2. Configure Private Google Access
3. Implement bastion host for SSH access
4. Set up VPN connection

### PCA Exam Scenarios

#### Scenario 1: Multi-Region Architecture Design
**Requirements**:
- Global user base
- 99.99% availability
- Disaster recovery capability
- Cost optimization

**Solution Architecture**:
1. Regional MIGs in multiple regions
2. Global HTTP(S) Load Balancer
3. Regional persistent disks with snapshots
4. Cloud CDN for static content
5. Cloud Armor for security

#### Scenario 2: Migration Strategy
**Current State**: On-premises data center
**Target State**: Google Cloud
**Approach**:
1. **Assessment Phase**: Inventory and dependencies
2. **Pilot Migration**: Non-critical workloads first
3. **Phased Migration**: Systematic workload movement
4. **Optimization**: Post-migration improvements

#### Scenario 3: Cost Optimization Strategy
**Problem**: High Compute Engine costs
**Solution Approach**:
1. **Right-sizing analysis**: Match resources to workload
2. **Committed use discounts**: Long-term commitments
3. **Preemptible instances**: Fault-tolerant workloads
4. **Automated scaling**: Match capacity to demand
5. **Storage optimization**: Appropriate disk types

### Troubleshooting Common Issues

#### SSH Connection Problems
```bash
# Check firewall rules
gcloud compute firewall-rules list --filter="name~ssh"

# Verify instance is running
gcloud compute instances describe INSTANCE_NAME --zone=ZONE

# Check SSH keys
gcloud compute os-login ssh-keys list

# Use serial console for access
gcloud compute instances get-serial-port-output INSTANCE_NAME --zone=ZONE
```

#### Performance Issues
```bash
# Monitor instance metrics
gcloud compute instances get-serial-port-output INSTANCE_NAME --zone=ZONE

# Check resource utilization
# (On the instance)
top
iostat -x 1
netstat -i
```

#### Startup Script Failures
```bash
# Check startup script logs
sudo journalctl -u google-startup-scripts.service

# View metadata server logs
curl -H "Metadata-Flavor: Google" \
  http://metadata.google.internal/computeMetadata/v1/instance/attributes/startup-script
```

---

## Conclusion

This comprehensive guide covers all essential aspects of Google Cloud Compute Engine for both ACE and PCA certifications. Key takeaways:

### For ACE Certification:
- Focus on fundamental operations and basic configurations
- Understand instance lifecycle and basic scaling
- Master firewall rules and basic security concepts
- Practice common troubleshooting scenarios

### For PCA Certification:
- Design multi-region, highly available architectures
- Understand enterprise security and compliance requirements
- Master cost optimization strategies at scale
- Plan and execute complex migration scenarios

### Next Steps:
1. **Hands-on Practice**: Complete the provided labs
2. **Official Documentation**: Study Google Cloud documentation
3. **Practice Exams**: Use official Google Cloud practice tests
4. **Real-world Experience**: Apply concepts in actual projects

Remember that both certifications require not just theoretical knowledge but practical experience with the Google Cloud Console, gcloud CLI, and real-world problem-solving scenarios.