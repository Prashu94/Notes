# AWS RDS (Relational Database Service) - SAA-C03 Study Guide

## Table of Contents
1. [Overview](#overview)
2. [Key Concepts](#key-concepts)
3. [Database Engines](#database-engines)
4. [DB Instance Classes](#db-instance-classes)
5. [Storage Types](#storage-types)
6. [Multi-AZ Deployments](#multi-az-deployments)
7. [Read Replicas](#read-replicas)
8. [Security](#security)
9. [Backup and Recovery](#backup-and-recovery)
10. [Monitoring and Performance](#monitoring-and-performance)
11. [Parameter Groups](#parameter-groups)
12. [Option Groups](#option-groups)
13. [Subnet Groups](#subnet-groups)
14. [Cost Optimization](#cost-optimization)
15. [Best Practices](#best-practices)
16. [Common Use Cases](#common-use-cases)
17. [Troubleshooting](#troubleshooting)
18. [AWS CLI Commands Reference](#aws-cli-commands-reference)
19. [SAA-C03 Exam Tips](#saa-c03-exam-tips)

## Overview

Amazon RDS is a managed relational database service that makes it easy to set up, operate, and scale relational databases in the cloud. RDS handles routine database tasks such as provisioning, patching, backup, recovery, failure detection, and repair.

### Key Benefits
- **Managed Service**: AWS handles maintenance, patching, and backups
- **Scalability**: Easy vertical and horizontal scaling
- **High Availability**: Multi-AZ deployments for failover
- **Performance**: Read replicas for improved read performance
- **Security**: Encryption at rest and in transit, VPC support
- **Cost-Effective**: Pay-as-you-use model with Reserved Instances

## Key Concepts

### RDS vs Self-Managed Databases
| Feature | RDS | Self-Managed EC2 |
|---------|-----|------------------|
| Management | Fully managed | Manual management |
| Patching | Automatic | Manual |
| Backups | Automatic | Manual setup |
| Monitoring | CloudWatch integration | Manual setup |
| Scaling | Easy vertical/horizontal | Manual |
| Cost | Service charges | EC2 + storage + management |

### Database Instance
- Virtual database environment in the cloud
- Can contain multiple databases
- Identified by DB instance identifier
- Runs on DB instance class (compute and memory)

## Database Engines

### Supported Engines
1. **MySQL**
   - Versions: 5.7, 8.0
   - Use cases: Web applications, e-commerce
   - Features: InnoDB engine, replication

2. **PostgreSQL**
   - Versions: 11, 12, 13, 14, 15
   - Use cases: Complex queries, analytics
   - Features: Advanced SQL, JSON support

3. **MariaDB**
   - Versions: 10.4, 10.5, 10.6
   - Use cases: MySQL replacement
   - Features: Enhanced performance, security

4. **Oracle Database**
   - Versions: 19c, 21c
   - Licensing: BYOL or License Included
   - Use cases: Enterprise applications

5. **Microsoft SQL Server**
   - Versions: 2017, 2019, 2022
   - Editions: Express, Web, Standard, Enterprise
   - Use cases: .NET applications, Windows environments

6. **Amazon Aurora**
   - MySQL and PostgreSQL compatible
   - Cloud-native, high performance
   - Serverless option available

### Engine Selection Criteria
- **Application compatibility**
- **Performance requirements**
- **Licensing costs**
- **Feature requirements**
- **Existing expertise**

## DB Instance Classes

### Categories

#### General Purpose (T3, T4g)
- **T3**: Burstable performance
- **T4g**: ARM-based Graviton2 processors
- **Use cases**: Development, testing, light workloads
- **CPU Credits**: Performance baseline with burst capability

#### Memory Optimized (R5, R6i, X1e, Z1d)
- **R5/R6i**: High memory-to-vCPU ratio
- **X1e**: Extremely high memory (up to 3,904 GiB)
- **Z1d**: High frequency processors + NVMe SSD
- **Use cases**: In-memory databases, real-time analytics

#### Compute Optimized (C5, C6i)
- **C5/C6i**: High-performance processors
- **Use cases**: CPU-intensive applications
- **Features**: Enhanced networking, NVMe SSD

### Sizing Considerations
- **CPU requirements**
- **Memory requirements**
- **Network performance**
- **Storage performance**
- **Cost constraints**

## Storage Types

### General Purpose SSD (gp2/gp3)
- **gp2**: 
  - 3 IOPS per GB (min 100, max 16,000)
  - Burst to 3,000 IOPS for volumes under 1 TiB
  - Storage: 20 GiB to 65 TiB

- **gp3**:
  - Baseline 3,000 IOPS regardless of size
  - Provision up to 16,000 IOPS
  - Provision up to 1,000 MiB/s throughput
  - Storage: 20 GiB to 65 TiB

### Provisioned IOPS SSD (io1/io2)
- **io1**:
  - Up to 64,000 IOPS
  - 50:1 IOPS to GiB ratio
  - Storage: 100 GiB to 65 TiB

- **io2**:
  - Up to 256,000 IOPS
  - 1000:1 IOPS to GiB ratio
  - Better durability than io1
  - Storage: 100 GiB to 65 TiB

### Magnetic Storage (Standard)
- **Legacy option**
- **Use cases**: Infrequent access
- **Performance**: Up to 1,000 IOPS
- **Storage**: 20 GiB to 3 TiB

### Storage Selection Guidelines
```
Low IOPS requirements (< 10,000) → gp2/gp3
Consistent high IOPS → io1/io2
Cost-sensitive, predictable workloads → gp3
Legacy applications → Magnetic (not recommended)
```

## Multi-AZ Deployments

### Purpose
- **High Availability**: Automatic failover
- **Data Durability**: Synchronous replication
- **Maintenance**: Zero-downtime maintenance

### How It Works
1. Primary DB instance in one AZ
2. Standby replica in different AZ
3. Synchronous replication
4. Automatic failover (1-2 minutes)

### Failover Scenarios
- Primary DB instance failure
- AZ outage
- Instance type change
- Software patching
- Manual failover

### Multi-AZ vs Single-AZ
| Feature | Multi-AZ | Single-AZ |
|---------|----------|-----------|
| Availability | 99.95% | 99.9% |
| Failover | Automatic | Manual recovery |
| Maintenance | Zero downtime | Planned downtime |
| Cost | ~2x | Standard |
| Read traffic | Primary only | Single instance |

### Configuration
```bash
# Enable Multi-AZ
aws rds modify-db-instance \
    --db-instance-identifier mydb \
    --multi-az \
    --apply-immediately
```

## Read Replicas

### Purpose
- **Read Scaling**: Distribute read traffic
- **Performance**: Reduce load on primary
- **Disaster Recovery**: Cross-region copies
- **Analytics**: Separate reporting workloads

### Types
1. **Same Region Read Replicas**
   - Up to 15 replicas per DB instance
   - Asynchronous replication
   - Same region as primary

2. **Cross-Region Read Replicas**
   - Different AWS region
   - Higher latency
   - Disaster recovery
   - Data locality

### Supported Engines
- MySQL: Up to 15 read replicas
- PostgreSQL: Up to 15 read replicas
- MariaDB: Up to 15 read replicas
- Aurora: Up to 15 Aurora replicas
- SQL Server: Not supported
- Oracle: Not supported

### Read Replica Lag
- **Monitoring**: CloudWatch ReplicaLag metric
- **Factors affecting lag**:
  - Network latency
  - Write load on primary
  - Instance class of replica
  - Storage type performance

### Promotion to Primary
- Manual process
- Breaks replication link
- Used for disaster recovery
- Applications need DNS update

### Configuration
```bash
# Create read replica
aws rds create-db-instance-read-replica \
    --db-instance-identifier mydb-replica \
    --source-db-instance-identifier mydb \
    --db-instance-class db.t3.medium
```

## Security

### Network Security

#### VPC Security Groups
- **Inbound rules**: Control database access
- **Outbound rules**: Usually allow all
- **Port configuration**: Engine-specific ports
- **Source**: Specific IPs, security groups, or CIDR blocks

#### DB Subnet Groups
- **Requirement**: Minimum 2 subnets in different AZs
- **Private subnets**: Recommended for security
- **Public accessibility**: Can be disabled

### Encryption

#### Encryption at Rest
- **AES-256 encryption**
- **AWS KMS integration**
- **Customer managed keys** or AWS managed keys
- **Cannot be disabled** once enabled
- **Snapshots**: Automatically encrypted

#### Encryption in Transit
- **SSL/TLS certificates**
- **Force SSL**: Parameter group setting
- **Certificate rotation**: Automatic
- **Engine-specific**: Implementation varies

### Access Control

#### IAM Database Authentication
- **Supported engines**: MySQL, PostgreSQL, Aurora
- **Token-based**: 15-minute validity
- **Benefits**: No password management, IAM integration
- **Use cases**: Applications with IAM roles

#### Database Users and Privileges
- **Engine-native**: Traditional username/password
- **Principle of least privilege**
- **Regular rotation**: Security best practice
- **Centralized management**: Consider external tools

### Compliance and Auditing

#### Database Activity Streams (Aurora)
- **Real-time monitoring**
- **Immutable audit logs**
- **Kinesis Data Streams integration**
- **Compliance**: SOX, PCI DSS

#### Performance Insights
- **Database performance monitoring**
- **SQL statement analysis**
- **Wait event analysis**
- **7-day free tier**, extended with paid option

## Backup and Recovery

### Automated Backups

#### Point-in-Time Recovery (PITR)
- **Retention period**: 0-35 days (default 7 days)
- **Recovery window**: Any point within retention period
- **Transaction logs**: Stored every 5 minutes
- **Granularity**: Second-level recovery
- **Storage**: No additional charge for backup storage equal to DB size

#### Backup Window
- **Duration**: User-defined maintenance window
- **Performance impact**: Minimal for Multi-AZ
- **Single-AZ**: Brief I/O suspension during snapshot

### Manual Snapshots
- **User-initiated**: Taken on-demand
- **Retention**: Until manually deleted
- **Sharing**: Can be shared across accounts
- **Cross-region**: Can be copied to other regions
- **Restoration**: Creates new DB instance

### Recovery Scenarios

#### Point-in-Time Recovery Process
1. Select recovery time
2. AWS creates new DB instance
3. Restores from automated backup
4. Applies transaction logs
5. Update application connection strings

#### Snapshot Restoration
1. Select snapshot
2. Specify new DB instance details
3. AWS creates new instance from snapshot
4. Update application configuration

### Backup Best Practices
- **Multi-AZ**: Enable for zero-downtime backups
- **Snapshot frequency**: Regular manual snapshots before major changes
- **Cross-region**: Copy snapshots for disaster recovery
- **Testing**: Regularly test restore procedures
- **Retention**: Balance between recovery needs and cost

## Monitoring and Performance

### Amazon CloudWatch Metrics

#### Basic Monitoring (Free)
- **DatabaseConnections**: Current connections
- **CPUUtilization**: Instance CPU usage
- **FreeableMemory**: Available memory
- **DatabaseConnections**: Active connections
- **DiskQueueDepth**: Outstanding I/O requests

#### Enhanced Monitoring (Paid)
- **Granularity**: Up to 1-second intervals
- **OS metrics**: Process and thread information
- **Real-time**: More frequent updates
- **Cost**: Additional charges apply

### Performance Insights
- **Query performance**: Top SQL statements
- **Wait events**: What's slowing down queries
- **Database load**: Average active sessions
- **Filtering**: By user, host, database
- **Free tier**: 7 days of history
- **Long-term**: Up to 2 years (paid)

### Common Performance Metrics
```
CPU Utilization > 80% → Consider scaling up
Free Memory < 15% → Memory pressure
Read/Write IOPS → Storage performance
Database Connections → Connection pooling
Replica Lag > 30 seconds → Investigate replication
```

### Performance Optimization

#### Query Optimization
- **Slow query logs**: Identify problematic queries
- **EXPLAIN plans**: Analyze query execution
- **Indexing strategy**: Proper index design
- **Query tuning**: Optimize SQL statements

#### Parameter Tuning
- **Buffer pool size**: Memory allocation
- **Connection limits**: Max connections
- **Query cache**: MySQL query caching
- **Work memory**: PostgreSQL work_mem

#### Connection Management
- **Connection pooling**: Reduce connection overhead
- **Persistent connections**: Reduce connection setup time
- **Connection limits**: Monitor and adjust
- **Idle connections**: Clean up unused connections

## Parameter Groups

### Purpose
- **Database configuration**: Engine-specific settings
- **Performance tuning**: Optimize for workload
- **Security settings**: Configure security parameters
- **Compliance**: Meet regulatory requirements

### Types
- **Default parameter groups**: Cannot be modified
- **Custom parameter groups**: User-created and modifiable
- **Engine-specific**: Different for each database engine

### Common Parameters

#### MySQL Parameters
```
innodb_buffer_pool_size → Memory for InnoDB
max_connections → Maximum concurrent connections
query_cache_size → Query result caching
slow_query_log → Enable slow query logging
```

#### PostgreSQL Parameters
```
shared_buffers → Shared memory buffers
work_mem → Memory for sorting operations
max_connections → Connection limit
log_statement → SQL statement logging
```

### Parameter Management
```bash
# Create parameter group
aws rds create-db-parameter-group \
    --db-parameter-group-name custom-mysql8 \
    --db-parameter-group-family mysql8.0 \
    --description "Custom MySQL 8.0 parameters"

# Modify parameter
aws rds modify-db-parameter-group \
    --db-parameter-group-name custom-mysql8 \
    --parameters "ParameterName=max_connections,ParameterValue=200,ApplyMethod=pending-reboot"
```

### Parameter Types
- **Static parameters**: Require instance reboot
- **Dynamic parameters**: Applied immediately
- **Apply method**: immediate or pending-reboot

## Option Groups

### Purpose
- **Additional features**: Enable optional database features
- **Engine-specific**: Different options for each engine
- **Plugin management**: Database plugins and extensions

### Common Options

#### MySQL Options
- **Memcached**: In-memory caching
- **MariaDB Audit Plugin**: Auditing capabilities

#### Oracle Options
- **Oracle Enterprise Manager**: Database management
- **Oracle APEX**: Application development
- **Oracle Label Security**: Row-level security

#### SQL Server Options
- **SQL Server Audit**: Auditing features
- **SQL Server Agent**: Job scheduling
- **SSIS, SSAS, SSRS**: Business intelligence tools

### Option Group Management
```bash
# Create option group
aws rds create-option-group \
    --option-group-name mysql-memcached \
    --engine-name mysql \
    --major-engine-version 8.0 \
    --option-group-description "MySQL with Memcached"

# Add option
aws rds add-option-to-option-group \
    --option-group-name mysql-memcached \
    --options OptionName=MEMCACHED
```

## Subnet Groups

### Purpose
- **Network placement**: Define which subnets DB can use
- **Multi-AZ requirement**: Must span multiple AZs
- **Security**: Control network access

### Requirements
- **Minimum 2 subnets**: In different Availability Zones
- **Same VPC**: All subnets must be in same VPC
- **Sufficient IP addresses**: For DB instances and replicas

### Best Practices
- **Private subnets**: Use for better security
- **Multiple AZs**: Ensure high availability
- **CIDR planning**: Adequate IP address space
- **Route tables**: Proper routing configuration

### Configuration
```bash
# Create DB subnet group
aws rds create-db-subnet-group \
    --db-subnet-group-name my-db-subnet-group \
    --db-subnet-group-description "DB subnet group for RDS" \
    --subnet-ids subnet-12345678 subnet-87654321
```

## Cost Optimization

### Instance Optimization

#### Right-Sizing
- **Monitor utilization**: Use CloudWatch metrics
- **T3 instances**: For variable workloads
- **Reserved Instances**: 1-3 year commitments
- **Spot instances**: Not available for RDS

#### Reserved Instances
- **1 or 3 year terms**
- **Payment options**: All upfront, partial upfront, no upfront
- **Instance flexibility**: Size flexibility within instance family
- **Savings**: Up to 69% compared to On-Demand

### Storage Optimization

#### Storage Types
- **gp3 vs gp2**: Better price/performance with gp3
- **Provisioned IOPS**: Only when needed
- **Storage autoscaling**: Automatic storage increases

#### Backup Optimization
- **Retention period**: Balance recovery needs with cost
- **Manual snapshots**: Delete when no longer needed
- **Cross-region**: Only when required for DR

### Multi-AZ and Read Replicas
- **Multi-AZ**: Use only for production workloads
- **Read replicas**: Scale appropriately for read load
- **Cross-region replicas**: Consider data transfer costs

### Cost Monitoring
```bash
# Set up billing alerts
aws cloudwatch put-metric-alarm \
    --alarm-name "RDS-High-Cost" \
    --alarm-description "Alert when RDS costs are high" \
    --metric-name EstimatedCharges \
    --namespace AWS/Billing \
    --statistic Maximum \
    --period 86400 \
    --threshold 1000 \
    --comparison-operator GreaterThanThreshold
```

## Best Practices

### Security Best Practices
1. **Use VPC**: Deploy in private subnets
2. **Security Groups**: Restrict access to necessary sources
3. **Encryption**: Enable encryption at rest and in transit
4. **IAM**: Use IAM database authentication when possible
5. **Regular updates**: Keep engine versions current
6. **Strong passwords**: Complex database passwords
7. **Principle of least privilege**: Minimal required permissions

### Performance Best Practices
1. **Right-sizing**: Match instance class to workload
2. **Storage type**: Choose appropriate storage for IOPS needs
3. **Parameter tuning**: Optimize database parameters
4. **Connection pooling**: Implement at application level
5. **Monitoring**: Use Performance Insights and CloudWatch
6. **Query optimization**: Regular query performance review
7. **Indexing strategy**: Proper index design and maintenance

### Availability Best Practices
1. **Multi-AZ**: Enable for production workloads
2. **Read replicas**: Use for read scaling and DR
3. **Automated backups**: Enable with appropriate retention
4. **Manual snapshots**: Before major changes
5. **Cross-region**: For disaster recovery
6. **Health checks**: Application-level database health monitoring
7. **Failover testing**: Regular DR testing procedures

### Operational Best Practices
1. **Maintenance windows**: Schedule during low-usage periods
2. **Parameter groups**: Use custom parameter groups
3. **Version management**: Plan for major version upgrades
4. **Capacity planning**: Monitor growth trends
5. **Documentation**: Maintain runbooks and procedures
6. **Alerting**: Set up appropriate CloudWatch alarms
7. **Change management**: Proper change control processes

## Common Use Cases

### Web Applications
- **Requirements**: High availability, read scaling
- **Solution**: Multi-AZ with read replicas
- **Database**: MySQL or PostgreSQL
- **Instance class**: T3 or R5 family
- **Storage**: gp3 for cost-effective performance

### Data Warehousing
- **Requirements**: Large data sets, complex queries
- **Solution**: Large instance classes, provisioned IOPS
- **Database**: PostgreSQL or Oracle
- **Instance class**: R5 or X1e family
- **Storage**: io1/io2 for consistent performance

### Development/Testing
- **Requirements**: Cost optimization, flexibility
- **Solution**: Single-AZ, smaller instances
- **Database**: Match production engine
- **Instance class**: T3 burstable instances
- **Storage**: gp2 for basic performance

### Microservices
- **Requirements**: Multiple small databases
- **Solution**: Aurora Serverless or small RDS instances
- **Database**: Engine per service requirements
- **Instance class**: T3 micro/small
- **Storage**: gp3 with autoscaling

### Analytics and Reporting
- **Requirements**: Read-heavy workloads
- **Solution**: Read replicas for reporting
- **Database**: PostgreSQL or MySQL
- **Instance class**: R5 for memory-intensive queries
- **Storage**: gp3 or io1 based on query patterns

## Troubleshooting

### Common Issues and Solutions

#### High CPU Utilization
**Symptoms**: CPU > 80% consistently
**Causes**: 
- Inefficient queries
- Missing indexes
- Insufficient instance size
**Solutions**:
- Identify slow queries using Performance Insights
- Add appropriate indexes
- Scale up instance class
- Optimize query performance

#### High Database Connections
**Symptoms**: Connection count near maximum
**Causes**:
- Poor connection management
- Connection leaks
- Insufficient max_connections
**Solutions**:
- Implement connection pooling
- Fix application connection leaks
- Increase max_connections parameter
- Monitor connection patterns

#### Storage Performance Issues
**Symptoms**: High disk queue depth, slow queries
**Causes**:
- Insufficient IOPS provisioning
- Wrong storage type
- I/O intensive workload
**Solutions**:
- Upgrade to higher IOPS storage (gp3, io1/io2)
- Optimize queries to reduce I/O
- Consider read replicas to distribute load
- Monitor IOPS CloudWatch metrics

#### Replication Lag
**Symptoms**: Read replica lag > acceptable threshold
**Causes**:
- High write load on primary
- Network issues
- Replica instance undersized
**Solutions**:
- Scale up read replica instance
- Reduce write load during peak times
- Check network connectivity
- Consider multiple smaller replicas

#### Connectivity Issues
**Symptoms**: Cannot connect to database
**Causes**:
- Security group rules
- Network ACLs
- DNS resolution
- Authentication failures
**Solutions**:
- Verify security group inbound rules
- Check VPC route tables and NACLs
- Confirm endpoint DNS resolution
- Validate credentials and IAM permissions

### Diagnostic Tools

#### Performance Insights
- Query performance analysis
- Wait event identification
- Database load trending
- Top SQL statements

#### CloudWatch Logs
- Error logs analysis
- Slow query logs
- General query logs
- Audit logs (where supported)

#### Enhanced Monitoring
- OS-level metrics
- Process monitoring
- Real-time performance data
- Resource utilization details

## AWS CLI Commands Reference

### DB Instance Management

#### Create DB Instances
```bash
# Create a MySQL DB instance
aws rds create-db-instance \
    --db-instance-identifier mydb-instance \
    --db-instance-class db.t3.medium \
    --engine mysql \
    --engine-version 8.0.35 \
    --master-username admin \
    --master-user-password MyPassword123! \
    --allocated-storage 100 \
    --storage-type gp3 \
    --vpc-security-group-ids sg-0123456789abcdef0 \
    --db-subnet-group-name my-db-subnet-group \
    --backup-retention-period 7 \
    --preferred-backup-window "03:00-04:00" \
    --preferred-maintenance-window "mon:04:00-mon:05:00" \
    --storage-encrypted \
    --kms-key-id arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012

# Create a PostgreSQL DB instance with Multi-AZ
aws rds create-db-instance \
    --db-instance-identifier postgres-prod \
    --db-instance-class db.r5.xlarge \
    --engine postgres \
    --engine-version 15.4 \
    --master-username postgres \
    --master-user-password SecurePass123! \
    --allocated-storage 500 \
    --storage-type io1 \
    --iops 3000 \
    --multi-az \
    --db-subnet-group-name prod-db-subnet-group \
    --vpc-security-group-ids sg-0987654321fedcba0 \
    --backup-retention-period 14 \
    --enable-cloudwatch-logs-exports '["postgresql"]' \
    --storage-encrypted

# Create SQL Server DB instance
aws rds create-db-instance \
    --db-instance-identifier sqlserver-prod \
    --db-instance-class db.m5.2xlarge \
    --engine sqlserver-se \
    --engine-version 15.00.4335.1.v1 \
    --master-username admin \
    --master-user-password Password123! \
    --allocated-storage 400 \
    --storage-type gp3 \
    --iops 12000 \
    --license-model license-included \
    --multi-az \
    --storage-encrypted

# Create Oracle DB instance with BYOL
aws rds create-db-instance \
    --db-instance-identifier oracle-prod \
    --db-instance-class db.m5.4xlarge \
    --engine oracle-ee \
    --engine-version 19.0.0.0.ru-2023-10.rur-2023-10.r1 \
    --master-username admin \
    --master-user-password OraclePass123! \
    --allocated-storage 1000 \
    --storage-type io2 \
    --iops 10000 \
    --license-model bring-your-own-license \
    --multi-az \
    --storage-encrypted
```

#### List and Describe DB Instances
```bash
# List all DB instances
aws rds describe-db-instances

# List specific DB instance
aws rds describe-db-instances \
    --db-instance-identifier mydb-instance

# List DB instances with specific engine
aws rds describe-db-instances \
    --query 'DBInstances[?Engine==`mysql`].[DBInstanceIdentifier,DBInstanceClass,EngineVersion]' \
    --output table

# List Multi-AZ instances
aws rds describe-db-instances \
    --query 'DBInstances[?MultiAZ==`true`].[DBInstanceIdentifier,Engine,MultiAZ]' \
    --output table

# Get DB instance endpoint
aws rds describe-db-instances \
    --db-instance-identifier mydb-instance \
    --query 'DBInstances[0].Endpoint.[Address,Port]' \
    --output text
```

#### Modify DB Instances
```bash
# Modify DB instance class (scale up)
aws rds modify-db-instance \
    --db-instance-identifier mydb-instance \
    --db-instance-class db.r5.2xlarge \
    --apply-immediately

# Modify storage (increase size and IOPS)
aws rds modify-db-instance \
    --db-instance-identifier mydb-instance \
    --allocated-storage 200 \
    --storage-type gp3 \
    --iops 6000 \
    --apply-immediately

# Enable Multi-AZ
aws rds modify-db-instance \
    --db-instance-identifier mydb-instance \
    --multi-az \
    --apply-immediately

# Disable Multi-AZ
aws rds modify-db-instance \
    --db-instance-identifier mydb-instance \
    --no-multi-az \
    --apply-immediately

# Change backup retention period
aws rds modify-db-instance \
    --db-instance-identifier mydb-instance \
    --backup-retention-period 14 \
    --preferred-backup-window "02:00-03:00"

# Enable Performance Insights
aws rds modify-db-instance \
    --db-instance-identifier mydb-instance \
    --enable-performance-insights \
    --performance-insights-retention-period 7 \
    --apply-immediately

# Enable Enhanced Monitoring
aws rds modify-db-instance \
    --db-instance-identifier mydb-instance \
    --monitoring-interval 60 \
    --monitoring-role-arn arn:aws:iam::123456789012:role/rds-monitoring-role \
    --apply-immediately

# Enable deletion protection
aws rds modify-db-instance \
    --db-instance-identifier mydb-instance \
    --deletion-protection \
    --apply-immediately

# Disable deletion protection
aws rds modify-db-instance \
    --db-instance-identifier mydb-instance \
    --no-deletion-protection \
    --apply-immediately
```

#### Start, Stop, and Reboot Instances
```bash
# Stop a DB instance
aws rds stop-db-instance \
    --db-instance-identifier mydb-instance

# Start a stopped DB instance
aws rds start-db-instance \
    --db-instance-identifier mydb-instance

# Reboot a DB instance
aws rds reboot-db-instance \
    --db-instance-identifier mydb-instance

# Reboot with failover (Multi-AZ)
aws rds reboot-db-instance \
    --db-instance-identifier mydb-instance \
    --force-failover
```

#### Delete DB Instances
```bash
# Delete DB instance without final snapshot
aws rds delete-db-instance \
    --db-instance-identifier mydb-instance \
    --skip-final-snapshot

# Delete DB instance with final snapshot
aws rds delete-db-instance \
    --db-instance-identifier mydb-instance \
    --final-db-snapshot-identifier mydb-final-snapshot-2024

# Delete DB instance and delete automated backups
aws rds delete-db-instance \
    --db-instance-identifier mydb-instance \
    --skip-final-snapshot \
    --delete-automated-backups
```

### Snapshot Management

#### Create DB Snapshots
```bash
# Create manual DB snapshot
aws rds create-db-snapshot \
    --db-instance-identifier mydb-instance \
    --db-snapshot-identifier mydb-snapshot-20240208

# Create snapshot with tags
aws rds create-db-snapshot \
    --db-instance-identifier mydb-instance \
    --db-snapshot-identifier mydb-snapshot-prod \
    --tags Key=Environment,Value=Production Key=Backup,Value=Manual
```

#### List and Describe Snapshots
```bash
# List all DB snapshots
aws rds describe-db-snapshots

# List snapshots for specific DB instance
aws rds describe-db-snapshots \
    --db-instance-identifier mydb-instance

# List manual snapshots
aws rds describe-db-snapshots \
    --snapshot-type manual

# List automated snapshots
aws rds describe-db-snapshots \
    --snapshot-type automated

# Describe specific snapshot
aws rds describe-db-snapshots \
    --db-snapshot-identifier mydb-snapshot-20240208

# List snapshots with specific tag
aws rds describe-db-snapshots \
    --query 'DBSnapshots[?contains(Tags[?Key==`Environment`].Value, `Production`)].[DBSnapshotIdentifier,SnapshotCreateTime]' \
    --output table
```

#### Restore from Snapshot
```bash
# Restore DB instance from snapshot
aws rds restore-db-instance-from-db-snapshot \
    --db-instance-identifier mydb-restored \
    --db-snapshot-identifier mydb-snapshot-20240208 \
    --db-instance-class db.t3.medium \
    --vpc-security-group-ids sg-0123456789abcdef0 \
    --db-subnet-group-name my-db-subnet-group

# Restore with different storage type
aws rds restore-db-instance-from-db-snapshot \
    --db-instance-identifier mydb-restored \
    --db-snapshot-identifier mydb-snapshot-20240208 \
    --db-instance-class db.r5.xlarge \
    --storage-type gp3 \
    --iops 4000 \
    --multi-az

# Restore to specific availability zone
aws rds restore-db-instance-from-db-snapshot \
    --db-instance-identifier mydb-restored \
    --db-snapshot-identifier mydb-snapshot-20240208 \
    --availability-zone us-east-1a
```

#### Copy Snapshots
```bash
# Copy snapshot within same region
aws rds copy-db-snapshot \
    --source-db-snapshot-identifier mydb-snapshot-20240208 \
    --target-db-snapshot-identifier mydb-snapshot-copy-20240208

# Copy snapshot to another region (cross-region)
aws rds copy-db-snapshot \
    --source-db-snapshot-identifier arn:aws:rds:us-east-1:123456789012:snapshot:mydb-snapshot-20240208 \
    --target-db-snapshot-identifier mydb-snapshot-dr \
    --region us-west-2

# Copy encrypted snapshot
aws rds copy-db-snapshot \
    --source-db-snapshot-identifier mydb-snapshot-20240208 \
    --target-db-snapshot-identifier mydb-snapshot-encrypted \
    --kms-key-id arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012

# Copy snapshot with option to share
aws rds copy-db-snapshot \
    --source-db-snapshot-identifier mydb-snapshot-20240208 \
    --target-db-snapshot-identifier mydb-snapshot-shared \
    --copy-tags
```

#### Share and Modify Snapshots
```bash
# Share snapshot with another AWS account
aws rds modify-db-snapshot-attribute \
    --db-snapshot-identifier mydb-snapshot-20240208 \
    --attribute-name restore \
    --values-to-add 987654321098

# Make snapshot public (use with caution)
aws rds modify-db-snapshot-attribute \
    --db-snapshot-identifier mydb-snapshot-20240208 \
    --attribute-name restore \
    --values-to-add all

# Remove account access from snapshot
aws rds modify-db-snapshot-attribute \
    --db-snapshot-identifier mydb-snapshot-20240208 \
    --attribute-name restore \
    --values-to-remove 987654321098

# Describe snapshot attributes
aws rds describe-db-snapshot-attributes \
    --db-snapshot-identifier mydb-snapshot-20240208
```

#### Delete Snapshots
```bash
# Delete manual snapshot
aws rds delete-db-snapshot \
    --db-snapshot-identifier mydb-snapshot-20240208
```

### Read Replicas

#### Create Read Replicas
```bash
# Create read replica in same region
aws rds create-db-instance-read-replica \
    --db-instance-identifier mydb-replica-1 \
    --source-db-instance-identifier mydb-instance \
    --db-instance-class db.t3.medium \
    --availability-zone us-east-1b

# Create read replica in different AZ
aws rds create-db-instance-read-replica \
    --db-instance-identifier mydb-replica-2 \
    --source-db-instance-identifier mydb-instance \
    --db-instance-class db.r5.large \
    --availability-zone us-east-1c \
    --storage-type gp3 \
    --iops 4000

# Create cross-region read replica
aws rds create-db-instance-read-replica \
    --db-instance-identifier mydb-replica-west \
    --source-db-instance-identifier arn:aws:rds:us-east-1:123456789012:db:mydb-instance \
    --db-instance-class db.t3.large \
    --region us-west-2 \
    --vpc-security-group-ids sg-0987654321fedcba0 \
    --db-subnet-group-name west-db-subnet-group

# Create read replica with encryption
aws rds create-db-instance-read-replica \
    --db-instance-identifier mydb-replica-encrypted \
    --source-db-instance-identifier mydb-instance \
    --storage-encrypted \
    --kms-key-id arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012

# Create read replica with auto minor version upgrade
aws rds create-db-instance-read-replica \
    --db-instance-identifier mydb-replica-auto \
    --source-db-instance-identifier mydb-instance \
    --db-instance-class db.t3.medium \
    --auto-minor-version-upgrade
```

#### Promote Read Replica
```bash
# Promote read replica to standalone instance
aws rds promote-read-replica \
    --db-instance-identifier mydb-replica-1

# Promote with custom backup retention
aws rds promote-read-replica \
    --db-instance-identifier mydb-replica-1 \
    --backup-retention-period 7 \
    --preferred-backup-window "03:00-04:00"
```

### Point-in-Time Recovery

```bash
# Restore DB instance to specific point in time
aws rds restore-db-instance-to-point-in-time \
    --source-db-instance-identifier mydb-instance \
    --target-db-instance-identifier mydb-restored-pitr \
    --restore-time 2024-02-08T10:30:00Z

# Restore to latest restorable time
aws rds restore-db-instance-to-point-in-time \
    --source-db-instance-identifier mydb-instance \
    --target-db-instance-identifier mydb-restored-latest \
    --use-latest-restorable-time

# Restore PITR with different configuration
aws rds restore-db-instance-to-point-in-time \
    --source-db-instance-identifier mydb-instance \
    --target-db-instance-identifier mydb-restored-pitr \
    --restore-time 2024-02-08T10:30:00Z \
    --db-instance-class db.r5.xlarge \
    --multi-az \
    --vpc-security-group-ids sg-0123456789abcdef0

# Get latest restorable time
aws rds describe-db-instances \
    --db-instance-identifier mydb-instance \
    --query 'DBInstances[0].LatestRestorableTime'
```

### Parameter Groups

#### Create and Manage Parameter Groups
```bash
# Create DB parameter group
aws rds create-db-parameter-group \
    --db-parameter-group-name mysql-custom-params \
    --db-parameter-group-family mysql8.0 \
    --description "Custom MySQL 8.0 parameters"

# List parameter groups
aws rds describe-db-parameter-groups

# List specific parameter group
aws rds describe-db-parameter-groups \
    --db-parameter-group-name mysql-custom-params

# Describe parameters in a group
aws rds describe-db-parameters \
    --db-parameter-group-name mysql-custom-params

# Describe specific parameter
aws rds describe-db-parameters \
    --db-parameter-group-name mysql-custom-params \
    --query 'Parameters[?ParameterName==`max_connections`]'
```

#### Modify Parameter Groups
```bash
# Modify single parameter
aws rds modify-db-parameter-group \
    --db-parameter-group-name mysql-custom-params \
    --parameters "ParameterName=max_connections,ParameterValue=200,ApplyMethod=immediate"

# Modify multiple parameters
aws rds modify-db-parameter-group \
    --db-parameter-group-name mysql-custom-params \
    --parameters \
        "ParameterName=max_connections,ParameterValue=200,ApplyMethod=immediate" \
        "ParameterName=innodb_buffer_pool_size,ParameterValue={DBInstanceClassMemory*3/4},ApplyMethod=pending-reboot"

# Reset parameter group to defaults
aws rds reset-db-parameter-group \
    --db-parameter-group-name mysql-custom-params \
    --reset-all-parameters

# Reset specific parameters
aws rds reset-db-parameter-group \
    --db-parameter-group-name mysql-custom-params \
    --parameters "ParameterName=max_connections,ApplyMethod=immediate"
```

#### Copy Parameter Groups
```bash
# Copy parameter group
aws rds copy-db-parameter-group \
    --source-db-parameter-group-identifier mysql-custom-params \
    --target-db-parameter-group-identifier mysql-custom-params-copy \
    --target-db-parameter-group-description "Copy of custom MySQL parameters"
```

#### Delete Parameter Groups
```bash
# Delete parameter group
aws rds delete-db-parameter-group \
    --db-parameter-group-name mysql-custom-params
```

### Option Groups

#### Create and Manage Option Groups
```bash
# Create option group
aws rds create-option-group \
    --option-group-name mysql-audit-group \
    --engine-name mysql \
    --major-engine-version 8.0 \
    --option-group-description "MySQL audit plugin options"

# List option groups
aws rds describe-option-groups

# Describe specific option group
aws rds describe-option-groups \
    --option-group-name mysql-audit-group

# List available options for engine
aws rds describe-option-group-options \
    --engine-name mysql \
    --major-engine-version 8.0
```

#### Modify Option Groups
```bash
# Add option to option group
aws rds modify-option-group \
    --option-group-name mysql-audit-group \
    --options-to-include \
        "OptionName=MARIADB_AUDIT_PLUGIN,OptionSettings=[{Name=SERVER_AUDIT_EVENTS,Value=CONNECT}]"

# Remove option from option group
aws rds modify-option-group \
    --option-group-name mysql-audit-group \
    --options-to-remove MARIADB_AUDIT_PLUGIN \
    --apply-immediately
```

#### Copy and Delete Option Groups
```bash
# Copy option group
aws rds copy-option-group \
    --source-option-group-identifier mysql-audit-group \
    --target-option-group-identifier mysql-audit-group-copy \
    --target-option-group-description "Copy of MySQL audit options"

# Delete option group
aws rds delete-option-group \
    --option-group-name mysql-audit-group
```

### Subnet Groups

#### Create and Manage DB Subnet Groups
```bash
# Create DB subnet group
aws rds create-db-subnet-group \
    --db-subnet-group-name my-db-subnet-group \
    --db-subnet-group-description "Database subnet group for VPC" \
    --subnet-ids subnet-12345678 subnet-87654321 subnet-11223344

# List DB subnet groups
aws rds describe-db-subnet-groups

# Describe specific subnet group
aws rds describe-db-subnet-groups \
    --db-subnet-group-name my-db-subnet-group
```

#### Modify Subnet Groups
```bash
# Modify DB subnet group (add/remove subnets)
aws rds modify-db-subnet-group \
    --db-subnet-group-name my-db-subnet-group \
    --subnet-ids subnet-12345678 subnet-87654321 subnet-99887766
```

#### Delete Subnet Groups
```bash
# Delete DB subnet group
aws rds delete-db-subnet-group \
    --db-subnet-group-name my-db-subnet-group
```

### Security Groups

#### Manage DB Security Groups (EC2-Classic)
```bash
# Note: DB Security Groups are for EC2-Classic only
# For VPC, use VPC Security Groups instead

# Create DB security group (EC2-Classic)
aws rds create-db-security-group \
    --db-security-group-name mydb-secgroup \
    --db-security-group-description "Database security group"

# Authorize CIDR range
aws rds authorize-db-security-group-ingress \
    --db-security-group-name mydb-secgroup \
    --cidrip 10.0.0.0/24

# Authorize EC2 security group
aws rds authorize-db-security-group-ingress \
    --db-security-group-name mydb-secgroup \
    --ec2-security-group-name app-secgroup \
    --ec2-security-group-owner-id 123456789012

# Revoke access
aws rds revoke-db-security-group-ingress \
    --db-security-group-name mydb-secgroup \
    --cidrip 10.0.0.0/24

# List DB security groups
aws rds describe-db-security-groups

# Delete DB security group
aws rds delete-db-security-group \
    --db-security-group-name mydb-secgroup
```

### Automated Backups

#### Manage Automated Backups
```bash
# Describe automated backups
aws rds describe-db-instance-automated-backups

# Describe automated backups for specific instance
aws rds describe-db-instance-automated-backups \
    --db-instance-identifier mydb-instance

# Describe retained automated backups
aws rds describe-db-instance-automated-backups \
    --db-instance-automated-backups-arn arn:aws:rds:us-east-1:123456789012:auto-backup:ab-abcdefgh12345678

# Delete automated backup
aws rds delete-db-instance-automated-backup \
    --dbi-resource-id db-ABCDEFGHIJKLMNOP

# Start backup retention (retain automated backups after deletion)
aws rds stop-db-instance \
    --db-instance-identifier mydb-instance
```

### Aurora Clusters

#### Create Aurora Clusters
```bash
# Create Aurora MySQL cluster
aws rds create-db-cluster \
    --db-cluster-identifier aurora-mysql-cluster \
    --engine aurora-mysql \
    --engine-version 8.0.mysql_aurora.3.04.0 \
    --master-username admin \
    --master-user-password AuroraPass123! \
    --database-name mydb \
    --vpc-security-group-ids sg-0123456789abcdef0 \
    --db-subnet-group-name my-db-subnet-group \
    --backup-retention-period 7 \
    --storage-encrypted

# Create Aurora PostgreSQL cluster
aws rds create-db-cluster \
    --db-cluster-identifier aurora-postgres-cluster \
    --engine aurora-postgresql \
    --engine-version 15.4 \
    --master-username postgres \
    --master-user-password PostgresPass123! \
    --database-name mydb \
    --vpc-security-group-ids sg-0123456789abcdef0 \
    --db-subnet-group-name my-db-subnet-group \
    --backup-retention-period 14 \
    --storage-encrypted \
    --enable-cloudwatch-logs-exports '["postgresql"]'

# Create Aurora Serverless v2 cluster
aws rds create-db-cluster \
    --db-cluster-identifier aurora-serverless-cluster \
    --engine aurora-mysql \
    --engine-version 8.0.mysql_aurora.3.04.0 \
    --master-username admin \
    --master-user-password ServerlessPass123! \
    --database-name mydb \
    --vpc-security-group-ids sg-0123456789abcdef0 \
    --db-subnet-group-name my-db-subnet-group \
    --serverless-v2-scaling-configuration MinCapacity=0.5,MaxCapacity=2 \
    --storage-encrypted
```

#### Create Aurora Cluster Instances
```bash
# Create Aurora cluster writer instance
aws rds create-db-instance \
    --db-instance-identifier aurora-mysql-instance-1 \
    --db-cluster-identifier aurora-mysql-cluster \
    --db-instance-class db.r5.large \
    --engine aurora-mysql

# Create Aurora cluster reader instance
aws rds create-db-instance \
    --db-instance-identifier aurora-mysql-instance-2 \
    --db-cluster-identifier aurora-mysql-cluster \
    --db-instance-class db.r5.large \
    --engine aurora-mysql

# Create Aurora Serverless v2 instance
aws rds create-db-instance \
    --db-instance-identifier aurora-serverless-instance-1 \
    --db-cluster-identifier aurora-serverless-cluster \
    --db-instance-class db.serverless \
    --engine aurora-mysql
```

#### Manage Aurora Clusters
```bash
# List DB clusters
aws rds describe-db-clusters

# Describe specific cluster
aws rds describe-db-clusters \
    --db-cluster-identifier aurora-mysql-cluster

# Modify Aurora cluster
aws rds modify-db-cluster \
    --db-cluster-identifier aurora-mysql-cluster \
    --backup-retention-period 14 \
    --preferred-backup-window "03:00-04:00" \
    --apply-immediately

# Enable backtrack for Aurora MySQL
aws rds modify-db-cluster \
    --db-cluster-identifier aurora-mysql-cluster \
    --backtrack-window 72 \
    --apply-immediately

# Stop Aurora cluster
aws rds stop-db-cluster \
    --db-cluster-identifier aurora-mysql-cluster

# Start Aurora cluster
aws rds start-db-cluster \
    --db-cluster-identifier aurora-mysql-cluster

# Delete Aurora cluster
aws rds delete-db-cluster \
    --db-cluster-identifier aurora-mysql-cluster \
    --skip-final-snapshot

# Delete Aurora cluster with final snapshot
aws rds delete-db-cluster \
    --db-cluster-identifier aurora-mysql-cluster \
    --final-db-snapshot-identifier aurora-final-snapshot-2024
```

#### Aurora Cluster Snapshots
```bash
# Create cluster snapshot
aws rds create-db-cluster-snapshot \
    --db-cluster-identifier aurora-mysql-cluster \
    --db-cluster-snapshot-identifier aurora-snapshot-20240208

# List cluster snapshots
aws rds describe-db-cluster-snapshots

# Restore cluster from snapshot
aws rds restore-db-cluster-from-snapshot \
    --db-cluster-identifier aurora-restored \
    --snapshot-identifier aurora-snapshot-20240208 \
    --engine aurora-mysql \
    --vpc-security-group-ids sg-0123456789abcdef0 \
    --db-subnet-group-name my-db-subnet-group

# Copy cluster snapshot
aws rds copy-db-cluster-snapshot \
    --source-db-cluster-snapshot-identifier aurora-snapshot-20240208 \
    --target-db-cluster-snapshot-identifier aurora-snapshot-copy

# Delete cluster snapshot
aws rds delete-db-cluster-snapshot \
    --db-cluster-snapshot-identifier aurora-snapshot-20240208
```

### Aurora Global Database

#### Create and Manage Global Database
```bash
# Create Aurora global database cluster
aws rds create-global-cluster \
    --global-cluster-identifier my-global-cluster \
    --engine aurora-mysql \
    --engine-version 8.0.mysql_aurora.3.04.0

# Add primary cluster to global database
aws rds modify-db-cluster \
    --db-cluster-identifier aurora-mysql-cluster \
    --global-cluster-identifier my-global-cluster \
    --apply-immediately

# Create secondary cluster in another region
aws rds create-db-cluster \
    --db-cluster-identifier aurora-secondary-cluster \
    --engine aurora-mysql \
    --engine-version 8.0.mysql_aurora.3.04.0 \
    --global-cluster-identifier my-global-cluster \
    --vpc-security-group-ids sg-0987654321fedcba0 \
    --db-subnet-group-name secondary-db-subnet-group \
    --region us-west-2

# List global clusters
aws rds describe-global-clusters

# Describe specific global cluster
aws rds describe-global-clusters \
    --global-cluster-identifier my-global-cluster

# Remove cluster from global database
aws rds remove-from-global-cluster \
    --global-cluster-identifier my-global-cluster \
    --db-cluster-identifier aurora-secondary-cluster \
    --region us-west-2

# Delete global cluster
aws rds delete-global-cluster \
    --global-cluster-identifier my-global-cluster

# Failover global cluster (promote secondary to primary)
aws rds failover-global-cluster \
    --global-cluster-identifier my-global-cluster \
    --target-db-cluster-identifier aurora-secondary-cluster \
    --region us-west-2
```

### Performance Insights

#### Enable and Query Performance Insights
```bash
# Enable Performance Insights (done via modify-db-instance, shown earlier)

# Get Performance Insights metrics
aws pi get-resource-metrics \
    --service-type RDS \
    --identifier db-ABCDEFGHIJKLMNOP \
    --start-time 2024-02-08T00:00:00Z \
    --end-time 2024-02-08T12:00:00Z \
    --period-in-seconds 300 \
    --metric-queries '[{"Metric":"db.load.avg"}]'

# Get dimension keys (top SQL queries)
aws pi describe-dimension-keys \
    --service-type RDS \
    --identifier db-ABCDEFGHIJKLMNOP \
    --start-time 2024-02-08T00:00:00Z \
    --end-time 2024-02-08T12:00:00Z \
    --metric db.load.avg \
    --group-by '{"Group":"db.sql"}'
```

### Enhanced Monitoring

```bash
# Enhanced Monitoring is enabled via modify-db-instance (shown earlier)
# Metrics are available in CloudWatch Logs

# List CloudWatch log streams for RDS Enhanced Monitoring
aws logs describe-log-streams \
    --log-group-name /aws/rds/instance/mydb-instance/enhanced-monitoring

# Get Enhanced Monitoring logs
aws logs get-log-events \
    --log-group-name /aws/rds/instance/mydb-instance/enhanced-monitoring \
    --log-stream-name db-ABCDEFGHIJKLMNOP
```

### Tags Management

#### Add and Manage Tags
```bash
# Add tags to DB instance
aws rds add-tags-to-resource \
    --resource-name arn:aws:rds:us-east-1:123456789012:db:mydb-instance \
    --tags Key=Environment,Value=Production Key=Application,Value=WebApp Key=Owner,Value=TeamA

# List tags for resource
aws rds list-tags-for-resource \
    --resource-name arn:aws:rds:us-east-1:123456789012:db:mydb-instance

# Remove tags from resource
aws rds remove-tags-from-resource \
    --resource-name arn:aws:rds:us-east-1:123456789012:db:mydb-instance \
    --tag-keys Environment Owner

# Add tags to snapshot
aws rds add-tags-to-resource \
    --resource-name arn:aws:rds:us-east-1:123456789012:snapshot:mydb-snapshot-20240208 \
    --tags Key=Backup,Value=Daily Key=Retention,Value=30days

# Add tags to parameter group
aws rds add-tags-to-resource \
    --resource-name arn:aws:rds:us-east-1:123456789012:pg:mysql-custom-params \
    --tags Key=Team,Value=Database Key=Purpose,Value=CustomConfig
```

### CloudWatch Logs Export

```bash
# Enable CloudWatch Logs export for MySQL
aws rds modify-db-instance \
    --db-instance-identifier mydb-instance \
    --cloudwatch-logs-export-configuration '{"LogTypesToEnable":["error","general","slowquery"]}' \
    --apply-immediately

# Enable CloudWatch Logs export for PostgreSQL
aws rds modify-db-instance \
    --db-instance-identifier postgres-instance \
    --cloudwatch-logs-export-configuration '{"LogTypesToEnable":["postgresql"]}' \
    --apply-immediately

# Disable specific log exports
aws rds modify-db-instance \
    --db-instance-identifier mydb-instance \
    --cloudwatch-logs-export-configuration '{"LogTypesToDisable":["general"]}' \
    --apply-immediately
```

### Database Activity Streams

```bash
# Start database activity stream
aws rds start-activity-stream \
    --resource-arn arn:aws:rds:us-east-1:123456789012:db:mydb-instance \
    --mode async \
    --kms-key-id arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012

# Describe database activity stream
aws rds describe-db-instances \
    --db-instance-identifier mydb-instance \
    --query 'DBInstances[0].ActivityStreamStatus'

# Stop database activity stream
aws rds stop-activity-stream \
    --resource-arn arn:aws:rds:us-east-1:123456789012:db:mydb-instance
```

### IAM Database Authentication

```bash
# Enable IAM database authentication
aws rds modify-db-instance \
    --db-instance-identifier mydb-instance \
    --enable-iam-database-authentication \
    --apply-immediately

# Generate authentication token
aws rds generate-db-auth-token \
    --hostname mydb-instance.abcdefg.us-east-1.rds.amazonaws.com \
    --port 3306 \
    --username iamuser \
    --region us-east-1
```

### Events and Notifications

#### Event Subscriptions
```bash
# Create event subscription
aws rds create-event-subscription \
    --subscription-name my-db-events \
    --sns-topic-arn arn:aws:sns:us-east-1:123456789012:rds-notifications \
    --source-type db-instance \
    --event-categories availability backup failure configuration

# List event subscriptions
aws rds describe-event-subscriptions

# Modify event subscription
aws rds modify-event-subscription \
    --subscription-name my-db-events \
    --enabled

# Delete event subscription
aws rds delete-event-subscription \
    --subscription-name my-db-events
```

#### Describe Events
```bash
# Describe recent events
aws rds describe-events \
    --duration 10080 \
    --max-records 100

# Describe events for specific instance
aws rds describe-events \
    --source-identifier mydb-instance \
    --source-type db-instance

# Describe events by category
aws rds describe-events \
    --source-type db-instance \
    --event-categories availability failure

# List event categories
aws rds describe-event-categories
```

### Reserved Instances

```bash
# List available reserved instance offerings
aws rds describe-reserved-db-instances-offerings \
    --db-instance-class db.r5.xlarge \
    --duration 31536000 \
    --product-description mysql

# Purchase reserved instance
aws rds purchase-reserved-db-instances-offering \
    --reserved-db-instances-offering-id 01234567-89ab-cdef-0123-456789abcdef \
    --reserved-db-instance-id my-reserved-instance \
    --db-instance-count 2

# List purchased reserved instances
aws rds describe-reserved-db-instances

# Describe specific reserved instance
aws rds describe-reserved-db-instances \
    --reserved-db-instance-id my-reserved-instance
```

### Engine Version Management

```bash
# List available engine versions
aws rds describe-db-engine-versions \
    --engine mysql

# List specific engine version details
aws rds describe-db-engine-versions \
    --engine mysql \
    --engine-version 8.0.35

# List upgradeable engine versions
aws rds describe-db-engine-versions \
    --engine mysql \
    --engine-version 8.0.32 \
    --query 'DBEngineVersions[0].ValidUpgradeTarget[*].[EngineVersion,Description]' \
    --output table
```

### Maintenance and Upgrades

```bash
# Describe pending maintenance actions
aws rds describe-pending-maintenance-actions

# Apply pending maintenance immediately
aws rds apply-pending-maintenance-action \
    --resource-identifier arn:aws:rds:us-east-1:123456789012:db:mydb-instance \
    --apply-action system-update \
    --opt-in-type immediate

# Modify maintenance window
aws rds modify-db-instance \
    --db-instance-identifier mydb-instance \
    --preferred-maintenance-window sun:03:00-sun:04:00 \
    --apply-immediately
```

## SAA-C03 Exam Tips

### Key Concepts for Exam

#### High Availability Scenarios
- **Multi-AZ**: Automatic failover, synchronous replication
- **Read Replicas**: Asynchronous, up to 15 replicas
- **Cross-region**: Disaster recovery, different region
- **Aurora**: Global database, cross-region automated failover

#### Performance Questions
- **Instance classes**: T3 (burstable), R5 (memory), C5 (compute)
- **Storage types**: gp2/gp3 (general), io1/io2 (provisioned IOPS)
- **Read replicas**: Scale read traffic, reduce primary load
- **Parameter groups**: Database configuration optimization

#### Security Requirements
- **Encryption**: At rest (KMS), in transit (SSL/TLS)
- **Network**: VPC, security groups, private subnets
- **IAM**: Database authentication, policy-based access
- **Compliance**: Audit trails, activity monitoring

#### Cost Optimization
- **Reserved Instances**: Long-term cost savings
- **Right-sizing**: Match instance to workload
- **Storage optimization**: Choose appropriate storage type
- **Backup retention**: Balance cost and recovery needs

### Exam Question Patterns

#### Scenario-Based Questions
1. **High Availability**: "Application needs zero downtime" → Multi-AZ
2. **Read Performance**: "Read-heavy workload" → Read replicas
3. **Disaster Recovery**: "Cross-region backup" → Cross-region snapshots
4. **Cost Optimization**: "Reduce database costs" → Reserved Instances, right-sizing
5. **Security**: "Encrypt sensitive data" → Encryption at rest and in transit

#### Common Distractors
- **Aurora vs RDS**: Know when to use each
- **Multi-AZ vs Read Replicas**: Different purposes
- **Storage types**: Performance and cost differences
- **Backup vs Snapshots**: Automated vs manual

### Study Focus Areas

#### Must Know for Exam
1. **Multi-AZ deployments**: Automatic failover, synchronous replication
2. **Read replicas**: Asynchronous, read scaling, cross-region
3. **Security**: Encryption options, network security, IAM integration
4. **Backup and recovery**: PITR, snapshots, cross-region copying
5. **Performance**: Instance classes, storage types, monitoring tools
6. **Cost optimization**: Reserved Instances, storage optimization

#### Common Exam Topics
- RDS vs Aurora comparison
- Multi-AZ vs Read Replica differences
- Security group configuration for databases
- Parameter group usage and benefits
- Backup and recovery strategies
- Performance monitoring and optimization
- Cost optimization techniques

### Quick Reference for Exam

#### Decision Trees
```
Need high availability? → Multi-AZ
Need read scaling? → Read Replicas  
Need cross-region DR? → Cross-region snapshots or replicas
Need consistent IOPS? → Provisioned IOPS (io1/io2)
Cost-sensitive workload? → gp3 storage, T3 instances
Memory-intensive queries? → R5 instance family
CPU-intensive workload? → C5 instance family
Variable workload? → T3 burstable instances
```

#### Key Numbers to Remember
- **Read replicas**: Up to 15 per DB instance
- **Multi-AZ failover**: 1-2 minutes
- **Backup retention**: 0-35 days (default 7)
- **Performance Insights**: 7 days free, up to 2 years paid
- **Reserved Instance terms**: 1 or 3 years
- **gp3 baseline**: 3,000 IOPS regardless of size

---

This comprehensive guide covers all essential RDS topics for the AWS Solutions Architect Associate (SAA-C03) certification exam. Focus on understanding the differences between Multi-AZ and Read Replicas, security options, and performance optimization strategies, as these are frequently tested areas.