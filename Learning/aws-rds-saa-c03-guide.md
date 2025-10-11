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
18. [SAA-C03 Exam Tips](#saa-c03-exam-tips)

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