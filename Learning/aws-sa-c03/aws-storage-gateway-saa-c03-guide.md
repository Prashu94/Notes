# AWS Storage Gateway - SAA-C03 Comprehensive Guide

## Table of Contents
1. [Overview](#overview)
2. [Storage Gateway Types](#storage-gateway-types)
3. [File Gateway](#file-gateway)
4. [Volume Gateway](#volume-gateway)
5. [Tape Gateway](#tape-gateway)
6. [Deployment Models](#deployment-models)
7. [Performance and Optimization](#performance-and-optimization)
8. [Security and Access Control](#security-and-access-control)
9. [Monitoring and Troubleshooting](#monitoring-and-troubleshooting)
10. [Integration with Other AWS Services](#integration-with-other-aws-services)
11. [Cost Optimization](#cost-optimization)
12. [Exam Tips and Common Scenarios](#exam-tips-and-common-scenarios)
13. [Hands-on Labs](#hands-on-labs)
14. [AWS CLI Commands Reference](#aws-cli-commands-reference)
15. [FAQ](#faq)

---

## Overview

### What is AWS Storage Gateway?

AWS Storage Gateway is a hybrid cloud storage service that connects on-premises environments to AWS cloud storage services (Amazon S3, Amazon S3 Glacier, Amazon EBS, and Amazon Glacier Deep Archive). It provides seamless integration between on-premises and cloud storage infrastructure.

### Key Benefits

- **Hybrid Cloud Integration**: Seamlessly connect on-premises to AWS cloud storage
- **Cost Optimization**: Move infrequently accessed data to cost-effective cloud storage
- **Scalability**: Virtually unlimited cloud storage capacity
- **Data Protection**: Built-in encryption and backup capabilities
- **Low Latency**: Local cache for frequently accessed data

### Use Cases

1. **File Shares**: Replace traditional file servers with cloud-backed file storage
2. **Backup and Archive**: Move backup data to cloud for long-term retention
3. **Data Lakes**: Ingest on-premises data into cloud data lakes
4. **Disaster Recovery**: Replicate critical data to cloud for DR scenarios
5. **Content Distribution**: Distribute content from cloud to edge locations

---

## Storage Gateway Types

AWS Storage Gateway offers three types of gateways:

### 1. File Gateway
- **Protocol**: NFS and SMB
- **Storage Backend**: Amazon S3
- **Use Case**: File shares and content distribution

### 2. Volume Gateway
- **Stored Volumes**: Primary data on-premises, async backup to S3
- **Cached Volumes**: Primary data in S3, cache frequently accessed data locally
- **Protocol**: iSCSI
- **Use Case**: Block storage and backup

### 3. Tape Gateway (VTL)
- **Protocol**: Virtual Tape Library (VTL)
- **Storage Backend**: S3 and S3 Glacier/Glacier Deep Archive
- **Use Case**: Replace physical tape infrastructure

---

## File Gateway

### Architecture

```
[On-Premises Applications] 
         ↓ (NFS/SMB)
[File Gateway VM/Hardware]
         ↓ (HTTPS)
[Amazon S3 Buckets]
```

### Key Features

- **Protocol Support**: NFS v3, v4.1 and SMB v2, v3
- **File Access**: Files stored as objects in S3 buckets
- **Local Cache**: Frequently accessed data cached locally for low latency
- **File Shares**: Multiple file shares per gateway
- **POSIX Compliance**: Full POSIX file system semantics

### Configuration Steps

1. **Deploy Gateway**
   - Download and deploy VM or use hardware appliance
   - Allocate resources (CPU, memory, storage)

2. **Activate Gateway**
   - Configure network settings
   - Activate through AWS console

3. **Create File Share**
   - Choose S3 bucket
   - Configure access permissions
   - Set up NFS/SMB settings

4. **Mount File Share**
   - Mount on client systems using standard protocols

### Best Practices

- **Local Cache Sizing**: Allocate sufficient cache for working set
- **Network Bandwidth**: Ensure adequate bandwidth for data transfer
- **S3 Bucket Policies**: Configure appropriate access policies
- **Monitoring**: Set up CloudWatch metrics and alarms

### Storage Classes Integration

File Gateway integrates with S3 storage classes:
- **S3 Standard**: For frequently accessed data
- **S3 Standard-IA**: For infrequently accessed data
- **S3 One Zone-IA**: For recreatable, infrequently accessed data
- **S3 Intelligent-Tiering**: Automatic cost optimization
- **S3 Glacier**: For archival with retrieval times in minutes to hours
- **S3 Glacier Deep Archive**: For long-term archival

---

## Volume Gateway

### Stored Volumes

#### Architecture
```
[Applications] 
    ↓ (iSCSI)
[Volume Gateway] → [Local Primary Storage] → [S3 (Snapshots)]
```

#### Key Features
- **Primary Storage**: Data stored locally on-premises
- **Asynchronous Backup**: Point-in-time snapshots to S3
- **Low Latency**: Local access to all data
- **Snapshot-based Recovery**: Restore volumes from S3 snapshots
- **Volume Size**: 1 GB to 16 TB per volume

#### Use Cases
- Applications requiring low-latency access to entire dataset
- Backup of on-premises volumes to cloud
- Disaster recovery scenarios

### Cached Volumes

#### Architecture
```
[Applications] 
    ↓ (iSCSI)
[Volume Gateway] → [Local Cache] ← [S3 (Primary Storage)]
```

#### Key Features
- **Primary Storage**: Data stored in S3
- **Local Cache**: Frequently accessed data cached locally
- **Scalable**: Up to 32 volumes per gateway, 32 TB each
- **Cost-Effective**: Only pay for storage used in S3
- **Instant Access**: Recently accessed data available locally

#### Use Cases
- Applications with large datasets where only subset is frequently accessed
- Expanding storage capacity beyond on-premises constraints
- Cost optimization for storage-heavy workloads

### Volume Gateway Best Practices

1. **Cache Sizing**
   - For Stored Volumes: Size for snapshot overhead
   - For Cached Volumes: Size for working set (20-30% of total data)

2. **Performance Optimization**
   - Use multiple volumes for better IOPS distribution
   - Implement proper MPIO configuration
   - Monitor cache hit ratios

3. **Backup Strategy**
   - Schedule regular snapshots
   - Implement retention policies
   - Test restore procedures

---

## Tape Gateway (VTL)

### Architecture

```
[Backup Applications] 
      ↓ (VTL)
[Tape Gateway] → [Virtual Tapes] → [S3/Glacier]
```

### Key Components

#### Virtual Tape Library (VTL)
- **Virtual Tapes**: Up to 1,500 virtual tapes in VTL
- **Tape Size**: 100 GB to 5 TB per tape
- **Media Changer**: Automated tape management
- **Barcode Labels**: Standard barcode support

#### Virtual Tape Shelf (VTS)
- **Archive Storage**: Unlimited virtual tapes in VTS
- **Storage Classes**: S3 Glacier and Glacier Deep Archive
- **Retrieval**: Tapes retrieved from VTS to VTL when needed

### Supported Backup Applications

- **Veeam Backup & Replication**
- **NetBackup (Symantec)**
- **Backup Exec (Symantec)**
- **CommVault**
- **Dell EMC NetWorker**
- **IBM Spectrum Protect**
- **Microsoft System Center Data Protection Manager**

### Migration Process

1. **Assessment**
   - Inventory existing tape infrastructure
   - Identify backup applications and workflows

2. **Gateway Deployment**
   - Deploy Tape Gateway
   - Configure VTL settings

3. **Backup Application Configuration**
   - Update backup jobs to use VTL
   - Configure tape policies

4. **Data Migration**
   - Migrate existing tape data (if needed)
   - Validate backup and restore processes

### Cost Benefits

- **Eliminate Physical Tapes**: No more tape procurement and management
- **Reduce Facilities Costs**: No need for tape storage facilities
- **Durability**: 99.999999999% (11 9's) durability in S3
- **Offsite Storage**: Automatic offsite storage in AWS

---

## Deployment Models

### 1. VM-based Deployment

#### Supported Platforms
- **VMware ESXi**: 5.0 or later
- **Microsoft Hyper-V**: 2012 R2 or later
- **Linux KVM**: Kernel-based Virtual Machine
- **Amazon EC2**: For cloud-based deployment

#### Resource Requirements
- **CPU**: Minimum 4 vCPUs (8 vCPUs recommended)
- **Memory**: Minimum 8 GB (16 GB recommended)
- **Network**: Gigabit Ethernet connection
- **Storage**: 
  - Root disk: 80 GB
  - Cache disk: Based on working set size
  - Upload buffer: For data staging

### 2. Hardware Appliance

#### Dell EMC PowerEdge R640
- **Pre-configured**: Ready-to-deploy hardware
- **Performance**: Optimized for Storage Gateway workloads
- **Support**: Single point of contact for hardware and software

#### Use Cases
- Organizations preferring hardware solutions
- Environments with specific compliance requirements
- Simplified procurement and support

### 3. Amazon EC2 Deployment

#### Benefits
- **Cloud-native**: Fully managed in AWS
- **Scalability**: Easy to scale resources up/down
- **Integration**: Native integration with VPC and security groups
- **Cost**: Pay only for what you use

#### Considerations
- **Data Transfer Costs**: Charges for data transfer between regions
- **Latency**: Network latency between on-premises and EC2
- **Bandwidth**: Ensure sufficient bandwidth for operations

---

## Performance and Optimization

### Network Optimization

#### Bandwidth Planning
- **Initial Sync**: Plan for full data transfer bandwidth requirements
- **Ongoing Operations**: Consider daily change rate and RPO requirements
- **Burst Capacity**: Account for peak usage periods

#### Network Configuration
- **Dedicated Connection**: Use AWS Direct Connect for consistent performance
- **Internet Connection**: Minimum 100 Mbps, recommended 1 Gbps+
- **QoS**: Implement Quality of Service policies
- **Multiple NICs**: Use multiple network interfaces for bandwidth aggregation

### Cache Optimization

#### Cache Sizing Guidelines
- **File Gateway**: 20-30% of frequently accessed data
- **Volume Gateway (Cached)**: 30-40% of working set
- **Tape Gateway**: Size based on concurrent backup jobs

#### Cache Performance
- **SSD Storage**: Use SSD for cache storage for better performance
- **RAID Configuration**: Implement RAID 0 for multiple cache disks
- **Monitoring**: Monitor cache hit ratios and adjust sizing

### Storage Optimization

#### Disk Configuration
- **Separate Disks**: Use separate disks for cache and upload buffer
- **RAID Levels**: 
  - RAID 0 for performance
  - RAID 1/10 for redundancy
- **Alignment**: Ensure proper disk alignment for optimal performance

### Performance Monitoring

#### Key Metrics
- **Cache Hit Ratio**: Percentage of reads served from cache
- **Throughput**: Data transfer rates to/from AWS
- **IOPS**: Input/Output operations per second
- **Latency**: Response times for operations

#### CloudWatch Metrics
- `CacheHitPercent`
- `CloudBytesUploaded`
- `CloudBytesDownloaded`
- `CachePercentDirty`
- `CachePercentUsed`

---

## Security and Access Control

### Data Encryption

#### Encryption in Transit
- **HTTPS/TLS**: All data encrypted during transfer to AWS
- **Protocol Security**: NFS and SMB traffic secured locally
- **VPN/Direct Connect**: Additional network-level encryption

#### Encryption at Rest
- **S3 Server-Side Encryption**: 
  - SSE-S3 (AES-256)
  - SSE-KMS (AWS Key Management Service)
  - SSE-C (Customer-provided keys)
- **Local Cache**: Cache data encrypted on gateway

### Access Control

#### AWS IAM Integration
- **Service Roles**: IAM roles for Storage Gateway service
- **User Permissions**: Granular permissions for gateway operations
- **Cross-Account Access**: Support for cross-account scenarios

#### File-Level Security
- **POSIX Permissions**: Standard UNIX file permissions
- **SMB Access Control**: Windows-style access control lists
- **Active Directory Integration**: Integration with on-premises AD

### Network Security

#### VPC Integration
- **VPC Endpoints**: Private connectivity to AWS services
- **Security Groups**: Control network access to EC2-based gateways
- **NACLs**: Additional network-level access control

#### Firewall Requirements
- **Outbound HTTPS (443)**: For AWS API communication
- **NTP (123)**: For time synchronization
- **DNS (53)**: For name resolution
- **Activation Port (80)**: For initial activation only

---

## Monitoring and Troubleshooting

### CloudWatch Integration

#### Standard Metrics
- **Gateway Metrics**: Overall gateway health and performance
- **Volume Metrics**: Volume-specific performance data
- **Cache Metrics**: Cache utilization and performance

#### Custom Alarms
```json
{
  "AlarmName": "StorageGateway-HighCacheUtilization",
  "MetricName": "CachePercentUsed",
  "Namespace": "AWS/StorageGateway",
  "Statistic": "Average",
  "Period": 300,
  "EvaluationPeriods": 2,
  "Threshold": 80,
  "ComparisonOperator": "GreaterThanThreshold"
}
```

### Logging and Auditing

#### CloudTrail Integration
- **API Calls**: All Storage Gateway API calls logged
- **Configuration Changes**: Track gateway and volume modifications
- **Access Patterns**: Monitor who accessed what resources

#### Local Gateway Logs
- **System Logs**: Gateway system and application logs
- **Performance Logs**: Detailed performance metrics
- **Error Logs**: Troubleshooting information

### Common Issues and Solutions

#### Performance Issues
1. **Slow Upload Speed**
   - Check bandwidth utilization
   - Verify cache configuration
   - Monitor upload buffer usage

2. **High Latency**
   - Verify network connectivity
   - Check cache hit ratios
   - Optimize cache sizing

#### Connectivity Issues
1. **Activation Failures**
   - Verify network connectivity to AWS
   - Check firewall rules
   - Validate time synchronization

2. **Ongoing Connection Issues**
   - Monitor CloudWatch metrics
   - Check gateway status
   - Verify security group rules

### Troubleshooting Tools

#### AWS Support Tools
- **Storage Gateway Console**: Real-time status and metrics
- **CloudWatch Dashboards**: Custom monitoring dashboards
- **AWS Support Center**: Access to technical support

#### Local Tools
- **Gateway Local Console**: Direct access to gateway configuration
- **Network Diagnostics**: Built-in network testing tools
- **Log Collection**: Automated log collection for support cases

---

## Integration with Other AWS Services

### Amazon S3 Integration

#### Direct Integration
- **File Gateway**: Files stored as S3 objects
- **Lifecycle Policies**: Automatic transition to lower-cost storage classes
- **Cross-Region Replication**: Replicate data across regions
- **Event Notifications**: Trigger actions based on S3 events

#### S3 Features Support
- **Versioning**: Object versioning for data protection
- **MFA Delete**: Additional protection for object deletion
- **Transfer Acceleration**: Faster uploads using CloudFront edge locations
- **Inventory Reports**: Detailed reports on stored objects

### AWS Backup Integration

#### Centralized Backup Management
- **Backup Plans**: Centralized backup scheduling
- **Cross-Service Backups**: Backup across multiple AWS services
- **Compliance Reporting**: Backup compliance monitoring

### Amazon CloudWatch Integration

#### Monitoring and Alerting
- **Metrics Collection**: Automatic metrics collection
- **Custom Dashboards**: Create custom monitoring dashboards
- **Alarm Actions**: Automated responses to threshold breaches
- **Log Aggregation**: Centralized log management

### AWS Lambda Integration

#### Event-Driven Processing
```python
import json
import boto3

def lambda_handler(event, context):
    """
    Process S3 events from Storage Gateway uploads
    """
    s3_client = boto3.client('s3')
    
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        
        # Process the uploaded file
        process_uploaded_file(bucket, key)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Successfully processed files')
    }

def process_uploaded_file(bucket, key):
    """
    Custom processing logic for uploaded files
    """
    # Add your processing logic here
    pass
```

### Amazon VPC Integration

#### Network Isolation
- **VPC Endpoints**: Private connectivity without internet gateway
- **Security Groups**: Fine-grained network access control
- **Private Subnets**: Deploy gateways in private subnets
- **Direct Connect**: Dedicated network connection to AWS

---

## Cost Optimization

### Storage Cost Management

#### S3 Storage Classes
1. **Standard**: Frequently accessed data
2. **Standard-IA**: Infrequently accessed data (30+ day minimum)
3. **One Zone-IA**: Recreatable, infrequently accessed data
4. **Intelligent-Tiering**: Automatic cost optimization
5. **Glacier**: Archive data (90+ day minimum)
6. **Glacier Deep Archive**: Long-term archive (180+ day minimum)

#### Lifecycle Policies
```json
{
  "Rules": [
    {
      "ID": "StorageGatewayLifecycle",
      "Status": "Enabled",
      "Transitions": [
        {
          "Days": 30,
          "StorageClass": "STANDARD_IA"
        },
        {
          "Days": 90,
          "StorageClass": "GLACIER"
        },
        {
          "Days": 365,
          "StorageClass": "DEEP_ARCHIVE"
        }
      ]
    }
  ]
}
```

### Data Transfer Optimization

#### Minimize Transfer Costs
- **Compression**: Enable compression for data transfers
- **Deduplication**: Reduce redundant data transfer
- **Scheduling**: Transfer large datasets during off-peak hours
- **Direct Connect**: Use dedicated connection for large volumes

### Gateway Sizing Optimization

#### Right-sizing Guidelines
- **Start Small**: Begin with minimum recommended resources
- **Monitor Performance**: Use CloudWatch metrics to identify bottlenecks
- **Scale Incrementally**: Add resources based on actual usage patterns
- **Regular Review**: Periodically review and optimize configurations

### Cost Monitoring

#### AWS Cost Explorer
- **Usage Patterns**: Analyze Storage Gateway usage over time
- **Cost Allocation Tags**: Tag resources for detailed cost tracking
- **Reserved Capacity**: Consider reserved capacity for predictable workloads

#### Budget Alerts
```json
{
  "BudgetName": "StorageGateway-Monthly-Budget",
  "BudgetLimit": {
    "Amount": "1000",
    "Unit": "USD"
  },
  "TimeUnit": "MONTHLY",
  "CostFilters": {
    "Service": ["Amazon Simple Storage Service"]
  },
  "Notifications": [
    {
      "NotificationType": "ACTUAL",
      "ComparisonOperator": "GREATER_THAN",
      "Threshold": 80
    }
  ]
}
```

---

## Exam Tips and Common Scenarios

### Key Exam Concepts

#### Storage Gateway Types
- **Remember the protocols**: 
  - File Gateway: NFS/SMB
  - Volume Gateway: iSCSI
  - Tape Gateway: VTL

#### Volume Gateway Subtypes
- **Stored Volumes**: Primary data on-premises, backup to S3
- **Cached Volumes**: Primary data in S3, cache on-premises

### Common Exam Scenarios

#### Scenario 1: File Server Migration
**Question**: Company wants to migrate file servers to cloud while maintaining on-premises access.
**Answer**: File Gateway with NFS/SMB protocols, S3 backend storage.

#### Scenario 2: Backup Modernization
**Question**: Replace aging tape backup infrastructure with cloud solution.
**Answer**: Tape Gateway (VTL) with existing backup applications.

#### Scenario 3: Hybrid Storage Expansion
**Question**: Need to expand on-premises storage without additional hardware.
**Answer**: Volume Gateway (Cached Volumes) for scalable cloud storage.

#### Scenario 4: Disaster Recovery
**Question**: Implement cost-effective disaster recovery solution.
**Answer**: Volume Gateway (Stored Volumes) with S3 snapshots for DR.

### Decision Matrix

| Requirement | File Gateway | Stored Volumes | Cached Volumes | Tape Gateway |
|------------|--------------|----------------|----------------|--------------|
| File-based access | ✅ | ❌ | ❌ | ❌ |
| Block-based access | ❌ | ✅ | ✅ | ❌ |
| Low latency for all data | ❌ | ✅ | ❌ | ❌ |
| Cloud-first storage | ✅ | ❌ | ✅ | ✅ |
| Backup application compatibility | ❌ | Partial | Partial | ✅ |
| Unlimited capacity | ✅ | ❌ | ✅ | ✅ |

### Study Tips

1. **Understand Use Cases**: Focus on when to use each gateway type
2. **Know Protocols**: Remember which protocols each gateway supports
3. **Performance Characteristics**: Understand latency and throughput implications
4. **Integration Points**: Know how gateways integrate with other AWS services
5. **Cost Implications**: Understand pricing models and optimization strategies

---

## Hands-on Labs

### Lab 1: File Gateway Setup

#### Objectives
- Deploy File Gateway
- Create NFS file share
- Mount share on Linux client
- Upload and access files through S3

#### Prerequisites
- AWS Account with appropriate permissions
- Linux system for client testing
- VMware vSphere or other supported hypervisor

#### Step-by-Step Instructions

1. **Deploy Gateway VM**
   ```bash
   # Download OVA file from AWS console
   # Deploy to VMware vSphere
   # Allocate minimum resources:
   # - 4 vCPUs
   # - 8 GB RAM  
   # - 80 GB root disk
   # - Additional disk for cache
   ```

2. **Activate Gateway**
   ```bash
   # Access gateway local console
   # Configure network settings
   # Obtain activation key from AWS console
   # Complete activation process
   ```

3. **Create File Share**
   ```bash
   # AWS CLI commands
   aws storagegateway create-nfs-file-share \
     --client-token $(uuidgen) \
     --gateway-arn arn:aws:storagegateway:region:account:gateway/sgw-12345678 \
     --location-arn arn:aws:s3:::my-bucket/prefix \
     --role arn:aws:iam::account:role/StorageGatewayRole \
     --client-list "0.0.0.0/0"
   ```

4. **Mount File Share**
   ```bash
   # On Linux client
   sudo mkdir /mnt/gateway-share
   sudo mount -t nfs -o nfsvers=4.1,rsize=1048576,wsize=1048576 \
     gateway-ip:/bucket-name /mnt/gateway-share
   ```

5. **Test File Operations**
   ```bash
   # Create test file
   echo "Hello from Storage Gateway" > /mnt/gateway-share/test.txt
   
   # Verify in S3
   aws s3 ls s3://my-bucket/prefix/
   aws s3 cp s3://my-bucket/prefix/test.txt -
   ```

### Lab 2: Volume Gateway Implementation

#### Objectives
- Deploy Volume Gateway
- Create stored volumes
- Configure iSCSI initiator
- Perform backup operations

#### Step-by-Step Instructions

1. **Deploy Volume Gateway**
   ```bash
   # Similar to File Gateway deployment
   # Ensure adequate storage for volumes
   ```

2. **Create Stored Volume**
   ```bash
   aws storagegateway create-stored-iscsi-volume \
     --gateway-arn arn:aws:storagegateway:region:account:gateway/sgw-12345678 \
     --disk-id disk-id \
     --preserve-existing-data false \
     --target-name my-volume \
     --network-interface-id 192.168.1.100
   ```

3. **Configure iSCSI Initiator**
   ```bash
   # On Windows
   # Use iSCSI Initiator tool
   
   # On Linux
   sudo iscsiadm --mode discovery --type sendtargets --portal gateway-ip
   sudo iscsiadm --mode node --targetname iqn.target.name --portal gateway-ip --login
   ```

4. **Format and Mount Volume**
   ```bash
   # Linux example
   sudo fdisk /dev/sdb
   sudo mkfs.ext4 /dev/sdb1
   sudo mkdir /mnt/gateway-volume
   sudo mount /dev/sdb1 /mnt/gateway-volume
   ```

### Lab 3: Tape Gateway Configuration

#### Objectives
- Deploy Tape Gateway
- Configure VTL
- Integrate with backup application
- Perform backup and restore operations

#### Prerequisites
- Backup application (Veeam, NetBackup, etc.)
- Understanding of tape backup concepts

#### Implementation Steps

1. **Deploy Tape Gateway**
   ```bash
   # Deploy similar to other gateways
   # Ensure adequate cache storage
   ```

2. **Create Virtual Tapes**
   ```bash
   aws storagegateway create-tapes \
     --gateway-arn arn:aws:storagegateway:region:account:gateway/sgw-12345678 \
     --tape-size-in-bytes 107374182400 \
     --client-token $(uuidgen) \
     --num-tapes-to-create 10 \
     --tape-barcode-prefix "TAPE"
   ```

3. **Configure Backup Application**
   ```bash
   # Configure backup software to recognize VTL
   # Update media server configuration
   # Create backup policies using virtual tapes
   ```

---

## AWS CLI Commands Reference

### Gateway Activation and Setup

#### Activate Gateway
```bash
# First, deploy the gateway VM or hardware appliance and obtain activation key
# Activation key is obtained from gateway's web interface at http://gateway-ip/?activationRegion=us-east-1

# Activate File Gateway
aws storagegateway activate-gateway \
  --activation-key ABCDE-12345-FGHIJ-67890-KLMNO \
  --gateway-name "Production-File-Gateway" \
  --gateway-timezone "GMT-5:00" \
  --gateway-region us-east-1 \
  --gateway-type FILE_S3 \
  --tags Key=Environment,Value=Production Key=Department,Value=IT

# Activate Volume Gateway (Cached mode)
aws storagegateway activate-gateway \
  --activation-key ABCDE-12345-FGHIJ-67890-KLMNO \
  --gateway-name "Production-Volume-Gateway" \
  --gateway-timezone "GMT-5:00" \
  --gateway-region us-east-1 \
  --gateway-type CACHED \
  --tags Key=Environment,Value=Production

# Activate Volume Gateway (Stored mode)
aws storagegateway activate-gateway \
  --activation-key ABCDE-12345-FGHIJ-67890-KLMNO \
  --gateway-name "Backup-Volume-Gateway" \
  --gateway-timezone "GMT-5:00" \
  --gateway-region us-east-1 \
  --gateway-type STORED

# Activate Tape Gateway
aws storagegateway activate-gateway \
  --activation-key ABCDE-12345-FGHIJ-67890-KLMNO \
  --gateway-name "Archive-Tape-Gateway" \
  --gateway-timezone "GMT-5:00" \
  --gateway-region us-east-1 \
  --gateway-type VTL \
  --medium-changer-type STK-L700 \
  --tape-drive-type IBM-ULT3580-TD5
```

#### List and Describe Gateways
```bash
# List all gateways
aws storagegateway list-gateways

# List gateways with pagination
aws storagegateway list-gateways --limit 10

# Describe specific gateway
aws storagegateway describe-gateway-information \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678

# Get gateway metrics
aws storagegateway list-local-disks \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678
```

### Local Disks Management

#### Add and Configure Cache
```bash
# List available local disks
aws storagegateway list-local-disks \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678

# Add cache disk (for File Gateway or Cached Volume Gateway)
aws storagegateway add-cache \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678 \
  --disk-ids "disk-1234abcd"

# Add upload buffer (for Volume Gateway)
aws storagegateway add-upload-buffer \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678 \
  --disk-ids "disk-5678efgh"

# Add working storage (for Stored Volume Gateway)
aws storagegateway add-working-storage \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678 \
  --disk-ids "disk-9012ijkl"

# Describe cache status
aws storagegateway describe-cache \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678

# Describe upload buffer
aws storagegateway describe-upload-buffer \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678

# Describe working storage
aws storagegateway describe-working-storage \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678
```

### File Gateway Operations

#### Create NFS File Share
```bash
# Create NFS file share with default settings
aws storagegateway create-nfs-file-share \
  --client-token $(uuidgen) \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678 \
  --location-arn arn:aws:s3:::my-file-gateway-bucket/prefix \
  --role arn:aws:iam::123456789012:role/StorageGatewayFileShareRole \
  --default-storage-class S3_STANDARD \
  --tags Key=Project,Value=FileSharing

# Create NFS file share with specific client access
aws storagegateway create-nfs-file-share \
  --client-token $(uuidgen) \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678 \
  --location-arn arn:aws:s3:::my-bucket/data \
  --role arn:aws:iam::123456789012:role/StorageGatewayRole \
  --client-list "10.0.1.0/24" "10.0.2.50" \
  --squash "RootSquash" \
  --read-only false \
  --default-storage-class S3_INTELLIGENT_TIERING \
  --object-acl bucket-owner-full-control

# Create NFS file share with guessed MIME types
aws storagegateway create-nfs-file-share \
  --client-token $(uuidgen) \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678 \
  --location-arn arn:aws:s3:::media-bucket \
  --role arn:aws:iam::123456789012:role/StorageGatewayRole \
  --guess-mime-type-enabled \
  --requester-pays false \
  --file-share-name "MediaShare"

# Create NFS file share with cache refresh settings
aws storagegateway create-nfs-file-share \
  --client-token $(uuidgen) \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678 \
  --location-arn arn:aws:s3:::shared-data \
  --role arn:aws:iam::123456789012:role/StorageGatewayRole \
  --cache-attributes CacheStaleTimeoutInSeconds=300 \
  --notification-policy '{"UploadNotificationPolicy":"{\"UploadComplete\":{\"Enabled\":true}}"}'
```

#### Create SMB File Share
```bash
# Create SMB file share with Active Directory authentication
aws storagegateway create-smb-file-share \
  --client-token $(uuidgen) \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678 \
  --location-arn arn:aws:s3:::smb-bucket \
  --role arn:aws:iam::123456789012:role/StorageGatewayRole \
  --authentication ActiveDirectory \
  --default-storage-class S3_STANDARD \
  --object-acl bucket-owner-full-control \
  --valid-user-list "DOMAIN\\user1" "DOMAIN\\user2" \
  --tags Key=Protocol,Value=SMB

# Create SMB file share with guest access
aws storagegateway create-smb-file-share \
  --client-token $(uuidgen) \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678 \
  --location-arn arn:aws:s3:::guest-bucket \
  --role arn:aws:iam::123456789012:role/StorageGatewayRole \
  --authentication GuestAccess \
  --guess-mime-type-enabled

# Create SMB file share with file share visibility disabled
aws storagegateway create-smb-file-share \
  --client-token $(uuidgen) \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678 \
  --location-arn arn:aws:s3:::hidden-share \
  --role arn:aws:iam::123456789012:role/StorageGatewayRole \
  --authentication ActiveDirectory \
  --smb-acl-enabled \
  --access-based-enumeration \
  --admin-user-list "DOMAIN\\admin"

# Create SMB file share with case sensitivity
aws storagegateway create-smb-file-share \
  --client-token $(uuidgen) \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678 \
  --location-arn arn:aws:s3:::case-sensitive-share \
  --role arn:aws:iam::123456789012:role/StorageGatewayRole \
  --authentication ActiveDirectory \
  --case-sensitivity CaseSensitive
```

#### Manage File Shares
```bash
# List file shares
aws storagegateway list-file-shares \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678

# Describe NFS file share
aws storagegateway describe-nfs-file-shares \
  --file-share-arn-list arn:aws:storagegateway:us-east-1:123456789012:share/share-12345678

# Describe SMB file share
aws storagegateway describe-smb-file-shares \
  --file-share-arn-list arn:aws:storagegateway:us-east-1:123456789012:share/share-87654321

# Update NFS file share
aws storagegateway update-nfs-file-share \
  --file-share-arn arn:aws:storagegateway:us-east-1:123456789012:share/share-12345678 \
  --default-storage-class S3_INTELLIGENT_TIERING \
  --client-list "10.0.0.0/16"

# Update SMB file share
aws storagegateway update-smb-file-share \
  --file-share-arn arn:aws:storagegateway:us-east-1:123456789012:share/share-87654321 \
  --valid-user-list "DOMAIN\\newuser" \
  --admin-user-list "DOMAIN\\admin"

# Delete file share
aws storagegateway delete-file-share \
  --file-share-arn arn:aws:storagegateway:us-east-1:123456789012:share/share-12345678 \
  --force-delete

# Refresh cache for file share
aws storagegateway refresh-cache \
  --file-share-arn arn:aws:storagegateway:us-east-1:123456789012:share/share-12345678 \
  --folder-list "/" \
  --recursive

# Notify when upload complete
aws storagegateway notify-when-uploaded \
  --file-share-arn arn:aws:storagegateway:us-east-1:123456789012:share/share-12345678
```

### Volume Gateway Operations

#### Create Cached Volumes
```bash
# Create cached volume
aws storagegateway create-cached-iscsi-volume \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678 \
  --volume-size-in-bytes 107374182400 \
  --snapshot-id snap-1234567890abcdef0 \
  --target-name "cached-volume-1" \
  --network-interface-id "10.0.1.100" \
  --client-token $(uuidgen) \
  --tags Key=VolumeType,Value=Cached

# Create cached volume without source snapshot
aws storagegateway create-cached-iscsi-volume \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678 \
  --volume-size-in-bytes 536870912000 \
  --target-name "data-volume-01" \
  --network-interface-id "10.0.1.100" \
  --client-token $(uuidgen) \
  --kms-encrypted \
  --kms-key arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012
```

#### Create Stored Volumes
```bash
# Create stored volume
aws storagegateway create-stored-iscsi-volume \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678 \
  --disk-id "disk-1234abcd" \
  --preserve-existing-data false \
  --target-name "stored-volume-1" \
  --network-interface-id "10.0.1.100" \
  --tags Key=VolumeType,Value=Stored

# Create stored volume from snapshot
aws storagegateway create-stored-iscsi-volume \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678 \
  --disk-id "disk-5678efgh" \
  --snapshot-id snap-0987654321fedcba0 \
  --preserve-existing-data false \
  --target-name "restored-volume" \
  --network-interface-id "10.0.1.100" \
  --kms-encrypted
```

#### Manage Volumes
```bash
# List volumes
aws storagegateway list-volumes \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678

# Describe cached iSCSI volumes
aws storagegateway describe-cached-iscsi-volumes \
  --volume-arns arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678/volume/vol-12345678

# Describe stored iSCSI volumes
aws storagegateway describe-stored-iscsi-volumes \
  --volume-arns arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678/volume/vol-87654321

# Update volume information
aws storagegateway update-vtl-device-type \
  --vtl-device-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678/device/vtl-device-12345678 \
  --device-type "Medium Changer"

# Delete volume
aws storagegateway delete-volume \
  --volume-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678/volume/vol-12345678
```

#### Volume Snapshots
```bash
# Create snapshot from volume
aws storagegateway create-snapshot \
  --volume-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678/volume/vol-12345678 \
  --snapshot-description "Daily backup $(date +%Y-%m-%d)" \
  --tags Key=BackupType,Value=Daily

# Create snapshot from cached volume
aws storagegateway create-snapshot-from-volume-recovery-point \
  --volume-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678/volume/vol-12345678 \
  --snapshot-description "Recovery point snapshot" \
  --tags Key=SnapshotType,Value=RecoveryPoint

# List volume recovery points
aws storagegateway list-volume-recovery-points \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678

# Describe snapshot schedule
aws storagegateway describe-snapshot-schedule \
  --volume-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678/volume/vol-12345678

# Update snapshot schedule
aws storagegateway update-snapshot-schedule \
  --volume-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678/volume/vol-12345678 \
  --start-at 2 \
  --recurrence-in-hours 24 \
  --description "Daily snapshot at 2 AM"

# Delete snapshot schedule
aws storagegateway delete-snapshot-schedule \
  --volume-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678/volume/vol-12345678
```

### Tape Gateway (VTL) Operations

#### Create Virtual Tapes
```bash
# Create single virtual tape
aws storagegateway create-tapes \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678 \
  --tape-size-in-bytes 107374182400 \
  --client-token $(uuidgen) \
  --num-tapes-to-create 1 \
  --tape-barcode-prefix "TAPE" \
  --tags Key=TapePool,Value=Production

# Create multiple virtual tapes
aws storagegateway create-tapes \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678 \
  --tape-size-in-bytes 2199023255552 \
  --client-token $(uuidgen) \
  --num-tapes-to-create 10 \
  --tape-barcode-prefix "PROD" \
  --kms-encrypted \
  --kms-key arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012 \
  --pool-id GLACIER

# Create tapes with WORM protection
aws storagegateway create-tapes \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678 \
  --tape-size-in-bytes 1099511627776 \
  --client-token $(uuidgen) \
  --num-tapes-to-create 5 \
  --tape-barcode-prefix "WORM" \
  --worm true \
  --tags Key=Compliance,Value=Required
```

#### Manage Virtual Tapes
```bash
# List tapes
aws storagegateway list-tapes

# List tapes for specific gateway
aws storagegateway list-tapes \
  --tape-arns arn:aws:storagegateway:us-east-1:123456789012:tape/TAPE12345

# Describe tapes
aws storagegateway describe-tapes \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678

# Describe tape with specific ARN
aws storagegateway describe-tapes \
  --tape-arns arn:aws:storagegateway:us-east-1:123456789012:tape/TAPE12345

# Describe tape archive
aws storagegateway describe-tape-archives \
  --tape-arns arn:aws:storagegateway:us-east-1:123456789012:tape/TAPE12345

# List tape archives
aws storagegateway list-tape-archives

# Retrieve tape archive
aws storagegateway retrieve-tape-archive \
  --tape-arn arn:aws:storagegateway:us-east-1:123456789012:tape/TAPE12345 \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678

# Retrieve tape recovery point
aws storagegateway retrieve-tape-recovery-point \
  --tape-arn arn:aws:storagegateway:us-east-1:123456789012:tape/TAPE12345 \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678

# Delete tape
aws storagegateway delete-tape \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678 \
  --tape-arn arn:aws:storagegateway:us-east-1:123456789012:tape/TAPE12345 \
  --bypass-governance-retention

# Delete tape archive
aws storagegateway delete-tape-archive \
  --tape-arn arn:aws:storagegateway:us-east-1:123456789012:tape/TAPE12345 \
  --bypass-governance-retention
```

#### Tape Pools
```bash
# List tape pools
aws storagegateway list-tape-pools

# Describe tape recovery points
aws storagegateway describe-tape-recovery-points \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678

# Assign tape pool
aws storagegateway assign-tape-pool \
  --tape-arn arn:aws:storagegateway:us-east-1:123456789012:tape/TAPE12345 \
  --pool-id GLACIER \
  --bypass-governance-retention

# Create custom tape pool
aws storagegateway create-tape-pool \
  --pool-name "CustomArchive" \
  --storage-class GLACIER \
  --retention-lock-type GOVERNANCE \
  --retention-lock-time-in-days 365 \
  --tags Key=PoolType,Value=LongTermArchive
```

### Gateway Maintenance

#### Software Updates
```bash
# Start gateway software update
aws storagegateway update-gateway-software-now \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678

# Update maintenance start time
aws storagegateway update-maintenance-start-time \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678 \
  --hour-of-day 2 \
  --minute-of-hour 0 \
  --day-of-week 0 \
  --day-of-month 15

# Describe maintenance start time
aws storagegateway describe-maintenance-start-time \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678
```

#### Gateway Operations
```bash
# Shutdown gateway
aws storagegateway shutdown-gateway \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678

# Start gateway (after shutdown)
aws storagegateway start-gateway \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678

# Disable gateway
aws storagegateway disable-gateway \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678

# Delete gateway
aws storagegateway delete-gateway \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678

# Update gateway information
aws storagegateway update-gateway-information \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678 \
  --gateway-name "Updated-Gateway-Name" \
  --gateway-timezone "GMT-8:00"
```

### Bandwidth Management

#### Configure Bandwidth Throttling
```bash
# Set bandwidth rate limit (in KB/s)
aws storagegateway update-bandwidth-rate-limit \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678 \
  --average-upload-rate-limit-in-bits-per-sec 102400000 \
  --average-download-rate-limit-in-bits-per-sec 204800000

# Set upload limit only
aws storagegateway update-bandwidth-rate-limit \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678 \
  --average-upload-rate-limit-in-bits-per-sec 51200000

# Describe bandwidth rate limit
aws storagegateway describe-bandwidth-rate-limit \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678

# Delete bandwidth rate limit
aws storagegateway delete-bandwidth-rate-limit \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678 \
  --bandwidth-type UPLOAD

# Update bandwidth rate limit schedule
aws storagegateway update-bandwidth-rate-limit-schedule \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678 \
  --bandwidth-rate-limit-intervals '
  [
    {
      "StartHourOfDay": 8,
      "StartMinuteOfHour": 0,
      "EndHourOfDay": 17,
      "EndMinuteOfHour": 0,
      "DaysOfWeek": [1,2,3,4,5],
      "AverageUploadRateLimitInBitsPerSec": 51200000
    },
    {
      "StartHourOfDay": 18,
      "StartMinuteOfHour": 0,
      "EndHourOfDay": 6,
      "EndMinuteOfHour": 0,
      "DaysOfWeek": [0,1,2,3,4,5,6],
      "AverageUploadRateLimitInBitsPerSec": 204800000
    }
  ]'

# Describe bandwidth rate limit schedule
aws storagegateway describe-bandwidth-rate-limit-schedule \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678
```

### SMB Settings and Active Directory

#### Join Active Directory Domain
```bash
# Join gateway to Active Directory
aws storagegateway join-domain \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678 \
  --domain-name "corp.example.com" \
  --organizational-unit "OU=Gateways,DC=corp,DC=example,DC=com" \
  --domain-controllers "dc1.corp.example.com" "dc2.corp.example.com" \
  --user-name "admin" \
  --password "SecurePassword123" \
  --timeout-in-seconds 60

# Describe SMB settings
aws storagegateway describe-smb-settings \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678

# Update SMB security strategy
aws storagegateway update-smb-security-strategy \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678 \
  --smb-security-strategy MandatoryEncryption

# Update SMB file share visibility
aws storagegateway update-smb-file-share-visibility \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678 \
  --file-shares-visible false

# Set SMB guest password
aws storagegateway set-smb-guest-password \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678 \
  --password "GuestPassword123"

# Set local console password
aws storagegateway set-local-console-password \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678 \
  --local-console-password "ConsolePassword123"
```

### CHAP Authentication (iSCSI)

```bash
# Update CHAP credentials for volume
aws storagegateway update-chap-credentials \
  --target-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678/target/iqn.1997-05.com.amazon:myvolume \
  --secret-to-authenticate-initiator "InitiatorSecret123" \
  --initiator-name "iqn.1991-05.com.microsoft:client1" \
  --secret-to-authenticate-target "TargetSecret123"

# Describe CHAP credentials
aws storagegateway describe-chap-credentials \
  --target-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678/target/iqn.1997-05.com.amazon:myvolume

# Delete CHAP credentials
aws storagegateway delete-chap-credentials \
  --target-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678/target/iqn.1997-05.com.amazon:myvolume \
  --initiator-name "iqn.1991-05.com.microsoft:client1"
```

### Monitoring and Metrics

```bash
# Get CloudWatch metrics for cache hit percentage
aws cloudwatch get-metric-statistics \
  --namespace AWS/StorageGateway \
  --metric-name CacheHitPercent \
  --dimensions Name=GatewayId,Value=sgw-12345678 Name=GatewayName,Value=Production-Gateway \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 3600 \
  --statistics Average

# Get cache used metric
aws cloudwatch get-metric-statistics \
  --namespace AWS/StorageGateway \
  --metric-name CacheUsed \
  --dimensions Name=GatewayId,Value=sgw-12345678 \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 3600 \
  --statistics Average

# Get upload buffer used
aws cloudwatch get-metric-statistics \
  --namespace AWS/StorageGateway \
  --metric-name UploadBufferUsed \
  --dimensions Name=GatewayId,Value=sgw-12345678 \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 3600 \
  --statistics Average

# Create CloudWatch alarm for cache hit percentage
aws cloudwatch put-metric-alarm \
  --alarm-name storage-gateway-low-cache-hit \
  --alarm-description "Alert when cache hit is below 80%" \
  --metric-name CacheHitPercent \
  --namespace AWS/StorageGateway \
  --statistic Average \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 80 \
  --comparison-operator LessThanThreshold \
  --dimensions Name=GatewayId,Value=sgw-12345678 \
  --alarm-actions arn:aws:sns:us-east-1:123456789012:storage-alerts

# Create alarm for file uploads
aws cloudwatch put-metric-alarm \
  --alarm-name storage-gateway-file-upload-failures \
  --alarm-description "Alert on file upload failures" \
  --metric-name FileUploadsFailed \
  --namespace AWS/StorageGateway \
  --statistic Sum \
  --period 300 \
  --evaluation-periods 1 \
  --threshold 1 \
  --comparison-operator GreaterThanOrEqualToThreshold \
  --dimensions Name=GatewayId,Value=sgw-12345678 \
  --alarm-actions arn:aws:sns:us-east-1:123456789012:storage-alerts
```

### Audit and Logging

```bash
# Enable CloudWatch log group
aws storagegateway update-gateway-information \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678 \
  --cloud-watch-log-group-arn arn:aws:logs:us-east-1:123456789012:log-group:/aws/storagegateway

# List file system associations (for audit trails)
aws storagegateway list-file-system-associations \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678

# Describe availability monitor test
aws storagegateway describe-availability-monitor-test \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678

# Start availability monitor test
aws storagegateway start-availability-monitor-test \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678
```

### Tags Management

```bash
# Add tags to gateway
aws storagegateway add-tags-to-resource \
  --resource-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678 \
  --tags Key=Environment,Value=Production Key=CostCenter,Value=IT Key=Backup,Value=Daily

# List tags for resource
aws storagegateway list-tags-for-resource \
  --resource-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678

# Remove tags from resource
aws storagegateway remove-tags-from-resource \
  --resource-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678 \
  --tag-keys Environment CostCenter

# Add tags to file share
aws storagegateway add-tags-to-resource \
  --resource-arn arn:aws:storagegateway:us-east-1:123456789012:share/share-12345678 \
  --tags Key=Department,Value=Finance Key=DataClassification,Value=Sensitive

# Add tags to volume
aws storagegateway add-tags-to-resource \
  --resource-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678/volume/vol-12345678 \
  --tags Key=Application,Value=Database Key=BackupSchedule,Value=Daily
```

### Automatic Tape Creation

```bash
# Create automatic tape creation policy
aws storagegateway update-automatic-tape-creation-policy \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678 \
  --automatic-tape-creation-rules '
  [
    {
      "TapeBarcodePrefix": "AUTO",
      "PoolId": "GLACIER",
      "TapeSizeInBytes": 2199023255552,
      "MinimumNumTapes": 5,
      "Worm": false
    }
  ]'

# List automatic tape creation policies
aws storagegateway list-automatic-tape-creation-policies \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678

# Delete automatic tape creation policy
aws storagegateway delete-automatic-tape-creation-policy \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678
```

### VPC Endpoint Configuration

```bash
# Attach VPC endpoint to gateway
aws storagegateway attach-volume \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678 \
  --network-interface-id "10.0.1.100" \
  --volume-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678/volume/vol-12345678

# Detach volume
aws storagegateway detach-volume \
  --volume-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-12345678/volume/vol-12345678
```

---

## FAQ

### General Questions

**Q: What is the difference between Storage Gateway and AWS DataSync?**
A: Storage Gateway provides ongoing hybrid access to data, while DataSync is for one-time or scheduled data transfers. Storage Gateway is for operational workloads, DataSync for migration and backup.

**Q: Can I use Storage Gateway with existing applications?**
A: Yes, Storage Gateway uses standard protocols (NFS, SMB, iSCSI, VTL) that work with existing applications without modification.

**Q: How much local storage do I need for cache?**
A: It depends on your access patterns. Generally, allocate 20-30% of your frequently accessed data size for cache. Monitor cache hit ratios and adjust as needed.

### Technical Questions

**Q: What happens if my gateway loses internet connectivity?**
A: File and Volume Gateways continue to serve data from local cache. New writes are queued for upload when connectivity is restored. Tape Gateway requires connectivity for most operations.

**Q: Can I migrate between gateway types?**
A: No, you cannot directly migrate between gateway types. You would need to migrate data and reconfigure applications.

**Q: How do I monitor gateway performance?**
A: Use Amazon CloudWatch metrics, set up custom dashboards, and configure alarms for key performance indicators like cache hit ratio and throughput.

### Security Questions

**Q: Is my data encrypted in transit and at rest?**
A: Yes, all data is encrypted in transit using HTTPS/TLS. Data at rest in S3 can be encrypted using SSE-S3, SSE-KMS, or SSE-C.

**Q: Can I use Storage Gateway with VPC?**
A: Yes, you can deploy Storage Gateway in Amazon VPC and use VPC endpoints for private connectivity to AWS services.

### Cost Questions

**Q: How is Storage Gateway priced?**
A: Pricing includes gateway usage charges, S3 storage costs, and data transfer charges. Cached Volumes and File Gateway also have request charges.

**Q: How can I optimize Storage Gateway costs?**
A: Use S3 lifecycle policies, implement compression, right-size your cache, and consider using Direct Connect for high-volume data transfers.

### Troubleshooting Questions

**Q: My gateway activation is failing. What should I check?**
A: Verify network connectivity, check firewall rules (port 80 for activation, 443 for ongoing operations), ensure NTP synchronization, and validate security group rules if using EC2.

**Q: Why is my upload speed slow?**
A: Check available bandwidth, monitor upload buffer utilization, verify cache configuration, and ensure your network isn't the bottleneck.

---

## Summary and Key Takeaways

### Critical Points for SAA-C03

1. **Gateway Types**: Understand the three types and their specific use cases
2. **Protocols**: Know which protocols each gateway type supports
3. **Storage Integration**: Understand how each gateway integrates with S3 and other AWS services
4. **Performance**: Know the factors that affect performance and how to optimize
5. **Security**: Understand encryption options and access control mechanisms
6. **Cost Optimization**: Know strategies for minimizing storage and transfer costs

### Best Practices Summary

- **Right-size cache**: Allocate appropriate cache based on access patterns
- **Monitor performance**: Use CloudWatch for ongoing monitoring and optimization
- **Implement security**: Use encryption, proper IAM roles, and network security
- **Plan for scale**: Design for growth in data volume and performance requirements
- **Test disaster recovery**: Regularly test backup and restore procedures

### Common Pitfalls to Avoid

- **Insufficient cache sizing**: Leading to poor performance
- **Inadequate bandwidth planning**: Causing slow data transfers
- **Missing security configurations**: Potential data exposure
- **Lack of monitoring**: Missing performance issues and optimization opportunities
- **Poor lifecycle management**: Unnecessary storage costs

This comprehensive guide covers all aspects of AWS Storage Gateway relevant to the SAA-C03 certification. Focus on understanding the use cases, architectural patterns, and integration points with other AWS services for exam success.