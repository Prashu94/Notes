# Amazon S3 and Glacier - AWS SAA-C03 Study Guide

## Table of Contents
1. [S3 Fundamentals](#s3-fundamentals)
2. [S3 Storage Classes](#s3-storage-classes)
3. [S3 Security](#s3-security)
4. [S3 Performance](#s3-performance)
5. [Amazon Glacier](#amazon-glacier)
6. [Lifecycle Management](#lifecycle-management)
7. [Advanced Features](#advanced-features)
8. [AWS CLI Commands Reference](#aws-cli-commands-reference)
9. [SAA-C03 Exam Scenarios](#saa-c03-exam-scenarios)

## S3 Fundamentals

### What is Amazon S3?
Amazon Simple Storage Service (S3) is an object storage service that offers industry-leading scalability, data availability, security, and performance. It's designed for 99.999999999% (11 9's) of durability.

### Key Concepts

#### Buckets
- **Definition**: A container for objects stored in S3
- **Global Namespace**: Bucket names must be globally unique across all AWS accounts
- **Regional Resource**: Buckets are created in a specific AWS region
- **Naming Rules**:
  - 3-63 characters long
  - Lowercase letters, numbers, and hyphens only
  - Cannot start or end with hyphen
  - Cannot have consecutive hyphens
  - Cannot be formatted as IP addresses

#### Objects
- **Definition**: Files stored in S3 buckets
- **Components**:
  - **Key**: The object name/path (up to 1024 bytes)
  - **Value**: The object data (0 bytes to 5TB)
  - **Version ID**: For versioned objects
  - **Metadata**: Key-value pairs describing the object
- **Object URL Format**: `https://bucket-name.s3.region.amazonaws.com/key`

#### Regions
- Data never leaves the region unless explicitly configured
- Choose regions based on:
  - **Latency**: Proximity to users
  - **Compliance**: Data sovereignty requirements
  - **Cost**: Regional pricing differences
  - **Feature Availability**: Some features may not be available in all regions

### Core Features

#### Scalability
- **Storage**: Virtually unlimited capacity
- **Objects**: No limit on number of objects per bucket
- **Request Performance**: Scales to handle high request rates

#### Durability and Availability
- **Durability**: 99.999999999% (11 9's) for Standard storage
- **Availability**: 99.99% availability SLA for Standard storage
- **Data Protection**: Automatically stored across multiple devices in multiple facilities

#### Access Methods
1. **AWS Management Console**: Web-based interface
2. **AWS CLI**: Command-line interface
3. **AWS SDKs**: Programming language-specific libraries
4. **REST APIs**: HTTP-based programmatic access
5. **Third-party tools**: Various backup and sync tools

## S3 Storage Classes

### Overview
S3 offers multiple storage classes designed for different use cases, with varying levels of availability, durability, and cost.

### Standard Storage Classes

#### S3 Standard
- **Use Case**: Frequently accessed data
- **Durability**: 99.999999999% (11 9's)
- **Availability**: 99.99%
- **AZ Resilience**: ≥3 AZs
- **Minimum Storage Duration**: None
- **Retrieval**: Immediate
- **Cost**: Highest storage cost, no retrieval fees

#### S3 Standard-Infrequent Access (S3 Standard-IA)
- **Use Case**: Infrequently accessed data that needs rapid access
- **Durability**: 99.999999999% (11 9's)
- **Availability**: 99.9%
- **AZ Resilience**: ≥3 AZs
- **Minimum Storage Duration**: 30 days
- **Retrieval**: Immediate
- **Cost**: Lower storage cost, retrieval fees apply

#### S3 One Zone-Infrequent Access (S3 One Zone-IA)
- **Use Case**: Infrequently accessed, non-critical data
- **Durability**: 99.999999999% (11 9's) within single AZ
- **Availability**: 99.5%
- **AZ Resilience**: Single AZ (data lost if AZ destroyed)
- **Minimum Storage Duration**: 30 days
- **Retrieval**: Immediate
- **Cost**: 20% lower than Standard-IA

### Intelligent Storage Classes

#### S3 Intelligent-Tiering
- **Use Case**: Data with unknown or changing access patterns
- **How it works**: Automatically moves objects between tiers based on access patterns
- **Tiers**:
  - **Frequent Access**: Same as S3 Standard
  - **Infrequent Access**: Same as S3 Standard-IA
  - **Archive Instant Access**: Same as Glacier Instant Retrieval
  - **Archive Access**: Same as Glacier Flexible Retrieval (optional)
  - **Deep Archive Access**: Same as Glacier Deep Archive (optional)
- **Monitoring Fee**: Small monthly fee per 1,000 objects
- **No Retrieval Fees**: Within Frequent and Infrequent tiers

### Archive Storage Classes

#### S3 Glacier Instant Retrieval
- **Use Case**: Archive data requiring immediate access
- **Durability**: 99.999999999% (11 9's)
- **Availability**: 99.9%
- **AZ Resilience**: ≥3 AZs
- **Minimum Storage Duration**: 90 days
- **Retrieval**: Milliseconds
- **Cost**: Lower storage cost than Standard-IA, higher retrieval costs

#### S3 Glacier Flexible Retrieval (formerly Glacier)
- **Use Case**: Archive data accessed 1-2 times per year
- **Durability**: 99.999999999% (11 9's)
- **Availability**: 99.99% after restoration
- **AZ Resilience**: ≥3 AZs
- **Minimum Storage Duration**: 90 days
- **Retrieval Options**:
  - **Expedited**: 1-5 minutes (additional cost)
  - **Standard**: 3-5 hours
  - **Bulk**: 5-12 hours (lowest cost)

#### S3 Glacier Deep Archive
- **Use Case**: Long-term backup and archive (7-10 years)
- **Durability**: 99.999999999% (11 9's)
- **Availability**: 99.99% after restoration
- **AZ Resilience**: ≥3 AZs
- **Minimum Storage Duration**: 180 days
- **Retrieval Options**:
  - **Standard**: 12 hours
  - **Bulk**: 48 hours (lowest cost)
- **Lowest Cost**: Among all storage classes

### Storage Class Comparison

| Storage Class | Durability | Availability | Min Duration | Retrieval Time | Use Case |
|---------------|------------|--------------|--------------|----------------|----------|
| Standard | 11 9's | 99.99% | None | Immediate | Frequently accessed |
| Standard-IA | 11 9's | 99.9% | 30 days | Immediate | Infrequently accessed |
| One Zone-IA | 11 9's* | 99.5% | 30 days | Immediate | Non-critical, infrequent |
| Intelligent-Tiering | 11 9's | 99.9% | None | Immediate** | Unknown patterns |
| Glacier Instant | 11 9's | 99.9% | 90 days | Milliseconds | Archive w/ instant access |
| Glacier Flexible | 11 9's | 99.99%*** | 90 days | Minutes-Hours | Archive, 1-2x/year |
| Glacier Deep Archive | 11 9's | 99.99%*** | 180 days | 12-48 hours | Long-term archive |

*Within single AZ  
**For Frequent/Infrequent tiers  
***After restoration

## S3 Security

### Access Control Overview
S3 provides multiple layers of security controls to protect your data:

### Identity-Based Policies

#### IAM Policies
- **Scope**: Control access for IAM users, groups, and roles
- **Granularity**: Can specify actions, resources, and conditions
- **Best Practice**: Use least privilege principle
- **Example Actions**:
  - `s3:GetObject`: Read objects
  - `s3:PutObject`: Write objects
  - `s3:DeleteObject`: Delete objects
  - `s3:ListBucket`: List bucket contents

### Resource-Based Policies

#### Bucket Policies
- **JSON-based**: Similar to IAM policies but attached to buckets
- **Cross-account Access**: Primary method for cross-account access
- **Public Access**: Can make buckets/objects public (use cautiously)
- **Key Elements**:
  - **Principal**: Who the policy applies to
  - **Action**: What actions are allowed/denied
  - **Resource**: Which bucket/objects
  - **Condition**: When the policy applies

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::my-bucket/*"
    }
  ]
}
```

#### Access Control Lists (ACLs)
- **Legacy Method**: Older access control mechanism
- **Limited Granularity**: Less flexible than bucket policies
- **Common Use**: Simple cross-account access scenarios
- **Recommendation**: Use bucket policies instead when possible

### Encryption

#### Encryption in Transit
- **HTTPS/SSL**: Always use encrypted connections
- **Bucket Policy Enforcement**: Can require HTTPS-only access
- **Client-Side**: Additional encryption before upload

#### Encryption at Rest

##### Server-Side Encryption (SSE)

###### SSE-S3 (Server-Side Encryption with S3-Managed Keys)
- **Default**: Now the default for all new objects
- **Key Management**: AWS manages all encryption keys
- **Algorithm**: AES-256
- **Cost**: No additional charge
- **Use Case**: Basic encryption needs

###### SSE-KMS (Server-Side Encryption with KMS-Managed Keys)
- **Key Management**: AWS Key Management Service (KMS)
- **Benefits**:
  - Audit trail of key usage
  - Key rotation
  - Fine-grained access control
- **Cost**: KMS charges apply
- **Envelope Encryption**: Uses both data keys and customer master keys (CMKs)

###### SSE-C (Server-Side Encryption with Customer-Provided Keys)
- **Key Management**: Customer provides and manages keys
- **Requirements**: 
  - Must provide key with every request
  - Use HTTPS
- **Use Case**: When you need full control over encryption keys

##### Client-Side Encryption
- **Process**: Encrypt data before uploading to S3
- **Key Management**: Customer responsibility
- **Use Case**: Maximum security control

### Advanced Security Features

#### S3 Block Public Access
- **Purpose**: Prevent accidental public exposure
- **Settings**:
  - Block public ACLs
  - Ignore public ACLs
  - Block public bucket policies
  - Block public and cross-account access
- **Best Practice**: Enable by default, disable only when needed

#### Access Points
- **Purpose**: Simplify access management for shared datasets
- **Features**:
  - Unique hostname and access policy
  - Can restrict access to VPC
  - Support for internet and VPC access
- **Use Case**: When multiple applications need different access patterns

#### Object Lock
- **Purpose**: Write Once Read Many (WORM) compliance
- **Modes**:
  - **Governance**: Can be overridden by privileged users
  - **Compliance**: Cannot be overridden by anyone, including root
- **Retention Periods**: Can set fixed retention periods
- **Legal Hold**: Indefinite protection

#### Access Logging
- **Server Access Logging**: Log requests made to your bucket
- **CloudTrail Integration**: API-level logging
- **Use Case**: Security auditing and compliance

### Security Best Practices

#### Access Management
1. **Enable Block Public Access** by default
2. **Use IAM roles** instead of long-term access keys
3. **Implement least privilege** access
4. **Regular access reviews** and cleanup
5. **Use bucket policies** for cross-account access

#### Encryption
1. **Enable default encryption** on all buckets
2. **Use KMS keys** for sensitive data
3. **Implement bucket key** for cost optimization with KMS
4. **Enforce HTTPS-only** access

#### Monitoring and Auditing
1. **Enable CloudTrail** for API logging
2. **Use Access Analyzer** to identify public access
3. **Set up CloudWatch alarms** for unusual activity
4. **Regular security assessments**

### Common Security Scenarios for SAA-C03

#### Scenario 1: Cross-Account Access
- **Solution**: Bucket policies with specific account principals
- **Consideration**: Ensure proper IAM permissions in target account

#### Scenario 2: Temporary Access
- **Solution**: Pre-signed URLs or STS temporary credentials
- **Use Case**: Allow users to upload/download without AWS credentials

#### Scenario 3: Compliance Requirements
- **Solution**: Object Lock + KMS encryption + detailed logging
- **Components**: WORM storage, audit trails, encryption

#### Scenario 4: Public Website Hosting
- **Solution**: Static website hosting with proper bucket policies
- **Security**: Only allow public read access, not write

## S3 Performance

### Performance Fundamentals

#### Request Performance
- **Baseline Performance**: 3,500 PUT/COPY/POST/DELETE and 5,500 GET/HEAD requests per second per prefix
- **Auto-scaling**: Performance scales automatically with higher request rates
- **No Pre-warming**: No need to gradually ramp up request rates

#### Prefixes and Performance
- **Prefix Definition**: Everything between bucket name and object name
  - `my-bucket/folder1/subfolder1/file.txt` → prefix: `/folder1/subfolder1/`
- **Spread Requests**: Distribute requests across multiple prefixes for higher aggregate performance
- **Avoid Sequential Naming**: Don't use timestamps or alphabetical sequences as prefixes

### Performance Optimization Techniques

#### Multipart Upload
- **Definition**: Split large objects into parts for parallel upload
- **Benefits**:
  - Faster uploads through parallelism
  - Resume failed uploads
  - Better network utilization
- **Recommendations**:
  - **Required**: Objects larger than 5 GB
  - **Recommended**: Objects larger than 100 MB
  - **Part Size**: 5 MB to 5 GB (except last part)
  - **Maximum Parts**: 10,000 per object

#### Transfer Acceleration
- **How it Works**: Uses CloudFront edge locations for faster uploads
- **Benefits**:
  - Faster uploads from distant locations
  - Automatic routing optimization
- **Cost**: Additional charges apply
- **Use Cases**:
  - Global user base
  - Large file uploads
  - Frequent uploads from remote locations
- **URL Format**: `bucket-name.s3-accelerate.amazonaws.com`

#### Byte-Range Fetches
- **Definition**: Download specific byte ranges of an object
- **Benefits**:
  - Parallelize downloads
  - Resume failed downloads
  - Download only needed portions
- **Use Cases**:
  - Large file downloads
  - Streaming applications
  - Partial file processing

### Request Patterns

#### Hot-Spotting
- **Problem**: Concentrated requests on specific prefixes
- **Solutions**:
  - Use random prefixes
  - Implement hexadecimal prefixes
  - Avoid sequential naming patterns

#### Mixed Workloads
- **GET-Heavy Workloads**: 
  - Use CloudFront for caching
  - Consider Cross-Region Replication for global access
- **PUT-Heavy Workloads**:
  - Distribute across multiple prefixes
  - Use multipart uploads
  - Consider Transfer Acceleration

### Performance Monitoring

#### CloudWatch Metrics
- **AllRequests**: Total number of requests
- **GetRequests**: Number of GET requests
- **PutRequests**: Number of PUT requests
- **DeleteRequests**: Number of DELETE requests
- **ListRequests**: Number of LIST requests
- **HeadRequests**: Number of HEAD requests
- **PostRequests**: Number of POST requests
- **SelectRequests**: Number of SELECT requests
- **BytesDownloaded**: Total bytes downloaded
- **BytesUploaded**: Total bytes uploaded
- **4xxErrors**: Client-side errors
- **5xxErrors**: Server-side errors
- **FirstByteLatency**: Time to first byte
- **TotalRequestLatency**: Total request time

#### Request Metrics
- **Enable**: Provides detailed request metrics
- **Granularity**: Per-prefix or per-object metrics
- **Cost**: Additional charges apply
- **Use Case**: Identify performance bottlenecks

### Performance Best Practices

#### Upload Optimization
1. **Use Multipart Upload** for files > 100 MB
2. **Enable Transfer Acceleration** for global uploads
3. **Distribute requests** across multiple prefixes
4. **Use appropriate part sizes** (5-100 MB typically optimal)
5. **Implement retry logic** with exponential backoff

#### Download Optimization
1. **Use CloudFront** for frequently accessed content
2. **Implement byte-range fetches** for large files
3. **Use appropriate client configurations** (connection pooling, timeouts)
4. **Consider S3 Select** for querying data without downloading entire objects

#### General Optimization
1. **Choose the right region** (closest to users/applications)
2. **Use appropriate storage class** based on access patterns
3. **Monitor performance metrics** regularly
4. **Implement proper error handling** and retries
5. **Use VPC endpoints** for private network access

### S3 Select and Glacier Select
- **Purpose**: Retrieve subsets of data without downloading entire objects
- **Benefits**:
  - Reduced data transfer costs
  - Improved application performance
  - Lower bandwidth requirements
- **Supported Formats**: CSV, JSON, Parquet (S3 Select)
- **Query Language**: SQL-like syntax
- **Use Cases**:
  - Data analytics
  - Log processing
  - Serverless applications

### Integration with Other Services

#### Amazon ElastiCache
- **Use Case**: Cache frequently accessed S3 objects
- **Benefits**: Microsecond latency for cached data

#### AWS Lambda
- **Event-driven Processing**: Process S3 objects as they're uploaded
- **Performance Considerations**: 
  - Lambda timeout limits
  - Memory allocation impacts performance

#### Amazon CloudFront
- **Global Content Delivery**: Cache S3 objects at edge locations
- **Performance Benefits**:
  - Reduced latency
  - Decreased load on S3
  - Cost optimization for frequent access

## Amazon Glacier

### Glacier Overview
Amazon Glacier is a secure, durable, and extremely low-cost cloud storage service for data archiving and long-term backup. It's designed for data that is accessed infrequently and for which retrieval times of several hours are acceptable.

### Glacier Storage Classes (within S3)

#### S3 Glacier Instant Retrieval
- **Target Use Case**: Archive data that needs immediate access
- **Access Pattern**: Accessed once per quarter
- **Retrieval Time**: Milliseconds (same as S3 Standard)
- **Minimum Storage Duration**: 90 days
- **Durability**: 99.999999999% (11 9's)
- **Availability**: 99.9%
- **Cost**: Lower storage cost than S3 Standard-IA, higher retrieval costs
- **Exam Tip**: Choose when you need archive pricing but immediate access

#### S3 Glacier Flexible Retrieval (formerly S3 Glacier)
- **Target Use Case**: Archive data accessed 1-2 times per year
- **Retrieval Options**:
  - **Expedited**: 1-5 minutes
    - Most expensive retrieval option
    - On-demand or provisioned capacity
    - Up to 250 MB archives
  - **Standard**: 3-5 hours
    - Default retrieval option
    - Balanced cost and speed
  - **Bulk**: 5-12 hours
    - Lowest cost retrieval option
    - Large amounts of data
- **Minimum Storage Duration**: 90 days
- **Durability**: 99.999999999% (11 9's)
- **Availability**: 99.99% (after restoration)

#### S3 Glacier Deep Archive
- **Target Use Case**: Long-term retention (7-10 years)
- **Lowest Cost**: Storage class in S3
- **Retrieval Options**:
  - **Standard**: 12 hours
  - **Bulk**: 48 hours (lowest cost)
- **Minimum Storage Duration**: 180 days
- **Durability**: 99.999999999% (11 9's)
- **Availability**: 99.99% (after restoration)
- **Use Cases**: Compliance, regulatory archives, digital preservation

### Glacier Retrieval Process

#### Archive Retrieval Job
1. **Initiate Retrieval**: Submit a retrieval job
2. **Job Processing**: Glacier processes the request
3. **Notification**: Receive notification when complete (optional)
4. **Download**: Download the restored data
5. **Expiration**: Restored copy expires after specified time (1-365 days)

#### Retrieval Notifications
- **SNS Topics**: Get notified when retrieval jobs complete
- **SQS Queues**: Alternative notification method
- **No Notification**: Poll for job completion status

### Provisioned Capacity

#### Expedited Retrievals
- **On-Demand**: May be throttled during high demand
- **Provisioned**: Guaranteed retrieval capacity
- **Purchase**: Buy capacity units in advance
- **Cost**: Additional cost for guaranteed performance
- **Use Case**: When you need guaranteed fast access to archived data

### Glacier Vault Lock

#### Purpose
- **Compliance**: Meet regulatory requirements
- **WORM**: Write Once Read Many compliance
- **Immutable**: Cannot be changed once locked

#### Process
1. **Initiate**: Start vault lock process
2. **Test**: 24-hour window to test the policy
3. **Complete**: Finalize the lock (irreversible)
4. **Locked**: Policy cannot be changed

#### Use Cases
- Financial records retention
- Healthcare data compliance
- Legal document preservation
- Regulatory compliance (SEC, HIPAA, etc.)

### Cost Optimization Strategies

#### Lifecycle Policies
- **Automatic Transition**: Move data through storage classes automatically
- **Cost-Effective**: Optimize costs without manual intervention
- **Examples**:
  - S3 Standard → S3 Standard-IA (30 days)
  - S3 Standard-IA → Glacier Flexible Retrieval (60 days)
  - Glacier Flexible Retrieval → Deep Archive (365 days)

#### Retrieval Cost Management
- **Plan Retrievals**: Understand retrieval patterns and costs
- **Bulk Retrievals**: Use for large amounts of data
- **Free Tier**: S3 Glacier provides free retrieval allowance
- **Data Retrieval Pricing**: 
  - Expedited: $0.03 per GB + $0.01 per request
  - Standard: $0.01 per GB + $0.00004 per request
  - Bulk: $0.0025 per GB + $0.00004 per request

### Monitoring and Management

#### CloudWatch Metrics
- **Vault Metrics**:
  - SizeInBytes
  - NumberOfArchives
- **Retrieval Metrics**:
  - DataRetrievalBytes
  - StandardRetrievalBytes
  - BulkRetrievalBytes
  - ExpeditedRetrievalBytes

#### Management Tools
- **AWS CLI**: Command-line management
- **AWS Console**: Web-based management
- **SDKs**: Programmatic access
- **Third-party Tools**: Backup and archive solutions

### Integration Patterns

#### Backup Solutions
- **AWS Backup**: Centralized backup service
- **Third-party**: Veeam, Commvault, etc.
- **Custom Solutions**: Using AWS SDKs and APIs

#### Data Lakes
- **Archive Tier**: Long-term storage of infrequently accessed data
- **Cost Optimization**: Move old data to cheaper storage
- **Compliance**: Meet retention requirements

### Glacier vs. Tape Storage

#### Advantages of Glacier
- **No Infrastructure**: No physical tape management
- **Durability**: 11 9's durability vs. tape degradation
- **Accessibility**: Programmatic access vs. physical retrieval
- **Scalability**: Unlimited capacity vs. physical constraints
- **Security**: Built-in encryption vs. physical security concerns

#### Migration from Tape
- **AWS Storage Gateway**: Virtual Tape Library (VTL) interface
- **Hybrid Approach**: Gradual migration strategy
- **Cost Analysis**: Compare total cost of ownership

### Common Glacier Scenarios for SAA-C03

#### Scenario 1: Compliance Archive
- **Requirement**: 7-year retention with WORM compliance
- **Solution**: S3 Glacier Deep Archive with Vault Lock
- **Considerations**: Vault Lock policy, retrieval planning

#### Scenario 2: Backup Strategy
- **Requirement**: Cost-effective long-term backup
- **Solution**: Lifecycle policies transitioning to Glacier classes
- **Considerations**: Retention periods, retrieval requirements

#### Scenario 3: Data Lake Archive
- **Requirement**: Archive old analytics data
- **Solution**: S3 Intelligent-Tiering or custom lifecycle policies
- **Considerations**: Access patterns, query requirements

#### Scenario 4: Disaster Recovery
- **Requirement**: Secondary backup for disaster recovery
- **Solution**: Cross-region replication to Glacier classes
- **Considerations**: RTO/RPO requirements, retrieval times

## Lifecycle Management

### Lifecycle Policies Overview
S3 Lifecycle management enables you to define rules that automatically transition objects between storage classes or delete objects based on their age or other criteria.

### Lifecycle Configuration Components

#### Rules
- **Rule ID**: Unique identifier for the rule
- **Status**: Enabled or Disabled
- **Filter**: Defines which objects the rule applies to
- **Actions**: What happens to matching objects

#### Filters
- **Prefix Filter**: Apply to objects with specific prefix
- **Tag Filter**: Apply to objects with specific tags
- **Object Size Filter**: Apply based on object size
- **Combination**: Use multiple filters together (AND logic)

#### Actions
- **Transition Actions**: Move objects between storage classes
- **Expiration Actions**: Delete objects or versions
- **Abort Incomplete Multipart Uploads**: Clean up incomplete uploads

### Transition Rules

#### Supported Transitions
```
S3 Standard
    ↓ (30 days min)
S3 Standard-IA
    ↓ (30 days min)
S3 One Zone-IA
    ↓ (Same day)
S3 Glacier Instant Retrieval
    ↓ (90 days min)
S3 Glacier Flexible Retrieval
    ↓ (90 days min)
S3 Glacier Deep Archive
```

#### Transition Constraints
- **Minimum Storage Duration**: Must respect minimum durations
- **Object Size**: Objects < 128KB not cost-effective for IA classes
- **One-Way Transitions**: Cannot transition back to warmer storage classes
- **Skip Classes**: Can skip intermediate classes if timing allows

#### Cost Considerations
- **Transition Costs**: Per-request charges for transitions
- **Minimum Durations**: Early deletion charges if removed before minimum
- **Object Overhead**: Additional metadata storage costs
- **Request Charges**: Different pricing for different storage classes

### Expiration Rules

#### Object Expiration
- **Delete Objects**: Remove objects after specified time
- **Permanent Deletion**: Cannot be recovered unless versioning is enabled
- **Cost Savings**: Eliminate storage costs for unnecessary data

#### Version Expiration (with Versioning)
- **Current Version Expiration**: Converts current version to delete marker
- **Noncurrent Version Expiration**: Permanently deletes noncurrent versions
- **Delete Marker Expiration**: Removes unnecessary delete markers

#### Incomplete Multipart Upload Cleanup
- **Automatic Cleanup**: Remove parts from failed multipart uploads
- **Cost Optimization**: Prevent accumulation of orphaned parts
- **Timing**: Typically set to 7 days

### Example Lifecycle Policies

#### Basic Transition Policy
```json
{
  "Rules": [
    {
      "ID": "BasicTransition",
      "Status": "Enabled",
      "Filter": {
        "Prefix": "documents/"
      },
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

#### Version Management Policy
```json
{
  "Rules": [
    {
      "ID": "VersionManagement",
      "Status": "Enabled",
      "Filter": {},
      "NoncurrentVersionTransitions": [
        {
          "NoncurrentDays": 30,
          "StorageClass": "STANDARD_IA"
        },
        {
          "NoncurrentDays": 60,
          "StorageClass": "GLACIER"
        }
      ],
      "NoncurrentVersionExpiration": {
        "NoncurrentDays": 365
      },
      "AbortIncompleteMultipartUpload": {
        "DaysAfterInitiation": 7
      }
    }
  ]
}
```

### Cost Optimization Strategies

#### Intelligent-Tiering vs. Lifecycle Policies
- **Intelligent-Tiering**: Automatic based on access patterns
  - Best for: Unknown or changing access patterns
  - Cost: Small monitoring fee per object
  - Benefit: No retrieval fees between frequent/infrequent tiers
- **Lifecycle Policies**: Time-based transitions
  - Best for: Predictable access patterns
  - Cost: No monitoring fees, but potential early deletion charges
  - Benefit: More predictable costs

#### Policy Design Best Practices
1. **Analyze Access Patterns**: Understand how data is accessed over time
2. **Start Conservative**: Begin with longer transition periods
3. **Monitor Costs**: Use Cost Explorer to track storage class costs
4. **Consider Object Size**: Small objects may not benefit from IA classes
5. **Use Filters Effectively**: Apply policies only where beneficial

### Lifecycle with Versioning

#### Version-Specific Rules
- **Current Versions**: Apply standard lifecycle rules
- **Noncurrent Versions**: Separate rules for previous versions
- **Delete Markers**: Can be automatically cleaned up

#### Best Practices with Versioning
1. **Separate Policies**: Different rules for current vs. noncurrent versions
2. **Faster Transitions**: Noncurrent versions can transition more aggressively
3. **Version Limits**: Consider limiting number of versions retained
4. **MFA Delete**: Protect against accidental policy changes

### Monitoring Lifecycle Policies

#### CloudWatch Metrics
- **Storage Class Metrics**: Track distribution across storage classes
- **Lifecycle Rule Metrics**: Monitor rule effectiveness
- **Cost Metrics**: Track cost savings from transitions

#### Cost Analysis
- **Storage Costs**: Compare costs across storage classes
- **Transition Costs**: Factor in transition request charges
- **Retrieval Costs**: Consider future access needs
- **Total Cost**: Analyze total cost of ownership

### Advanced Lifecycle Scenarios

#### Multi-Tier Architecture
```
Hot Data (0-30 days): S3 Standard
Warm Data (30-90 days): S3 Standard-IA
Cold Data (90-365 days): S3 Glacier Flexible Retrieval
Archive Data (365+ days): S3 Glacier Deep Archive
```

#### Compliance-Driven Lifecycle
```
Active Records (0-2 years): S3 Standard/Standard-IA
Inactive Records (2-7 years): S3 Glacier Flexible Retrieval
Long-term Archive (7+ years): S3 Glacier Deep Archive
Legal Hold: S3 Object Lock + appropriate storage class
```

#### Data Lake Lifecycle
```
Recent Data (0-90 days): S3 Standard (frequent analysis)
Historical Data (90-365 days): S3 Standard-IA (occasional analysis)
Archive Data (1+ years): S3 Glacier Flexible Retrieval
Compliance Archive (7+ years): S3 Glacier Deep Archive
```

### Common Lifecycle Pitfalls

#### Minimum Duration Violations
- **Problem**: Transitioning or deleting before minimum storage duration
- **Result**: Early deletion charges
- **Solution**: Respect minimum duration requirements

#### Small Object Overhead
- **Problem**: Transitioning small objects to IA classes
- **Result**: Higher costs due to minimum billable size (128KB)
- **Solution**: Use size filters in lifecycle policies

#### Frequent Access After Transition
- **Problem**: Objects transitioned to archive but frequently accessed
- **Result**: High retrieval costs
- **Solution**: Better access pattern analysis before policy creation

#### Over-Aggressive Policies
- **Problem**: Transitioning too quickly without understanding usage
- **Result**: Unexpected costs and performance issues
- **Solution**: Start conservative and adjust based on monitoring

## Advanced Features

### Versioning

#### Overview
S3 Versioning allows you to keep multiple variants of an object in the same bucket, providing protection against accidental deletion and modification.

#### Versioning States
- **Unversioned**: Default state, no versioning
- **Enabled**: Versioning is active
- **Suspended**: Versioning was enabled but is now suspended

#### Key Concepts
- **Version ID**: Unique identifier for each object version
- **Current Version**: The latest version of an object
- **Noncurrent Versions**: Previous versions of an object
- **Delete Marker**: Special marker when current version is deleted

#### Benefits
- **Data Protection**: Recover from accidental deletion or modification
- **Change Tracking**: Maintain history of object changes
- **Rollback Capability**: Easily revert to previous versions

#### Considerations
- **Storage Costs**: Each version is billed separately
- **Performance**: LIST operations return all versions by default
- **Management**: Need lifecycle policies to manage versions

### Cross-Region Replication (CRR)

#### Purpose
Automatically replicate objects across different AWS regions for disaster recovery, compliance, and latency reduction.

#### Prerequisites
- **Versioning**: Must be enabled on both source and destination buckets
- **IAM Role**: S3 needs permissions to replicate objects
- **Different Regions**: Source and destination must be in different regions

#### Configuration Options
- **Entire Bucket**: Replicate all objects
- **Prefix Filter**: Replicate objects with specific prefix
- **Tag Filter**: Replicate objects with specific tags
- **Storage Class**: Choose destination storage class

#### Replication Features
- **Metadata Replication**: Object metadata is preserved
- **Access Control**: ACLs and object ownership replicated
- **Encryption**: Supports replication of encrypted objects
- **Delete Replication**: Can replicate delete markers and versions

#### Use Cases
- **Disaster Recovery**: Maintain copies in multiple regions
- **Compliance**: Meet data locality requirements
- **Performance**: Reduce latency for global users
- **Analytics**: Aggregate data from multiple regions

### Same-Region Replication (SRR)

#### Purpose
Replicate objects within the same AWS region for data redundancy, compliance, or processing workflows.

#### Use Cases
- **Log Aggregation**: Centralize logs from multiple sources
- **Live Replication**: Maintain real-time copies
- **Production/Test**: Replicate production data to test environments
- **Compliance**: Meet specific backup requirements

### Event Notifications

#### Overview
S3 can publish events to other AWS services when specific actions occur, enabling event-driven architectures.

#### Supported Events
- **Object Created**: PUT, POST, COPY, Multipart Upload
- **Object Deleted**: Delete operations
- **Object Restore**: Glacier restore operations
- **Reduced Redundancy Storage (RRS)**: Object lost events
- **Replication**: Replication events

#### Destination Services
- **Amazon SQS**: Send messages to SQS queues
- **Amazon SNS**: Publish to SNS topics  
- **AWS Lambda**: Trigger Lambda functions
- **Amazon EventBridge**: Route to EventBridge rules

#### Configuration
- **Event Types**: Select which events to monitor
- **Filters**: Prefix and suffix filters to limit scope
- **Destinations**: Configure target services
- **Permissions**: Ensure proper IAM permissions

#### Common Patterns
- **Image Processing**: Trigger Lambda for image resize/optimization
- **Log Processing**: Process logs as they arrive
- **Data Pipeline**: Trigger downstream processing
- **Monitoring**: Alert on specific object operations

### Static Website Hosting

#### Overview
S3 can host static websites directly, providing a cost-effective solution for web content delivery.

#### Configuration
- **Enable Hosting**: Turn on static website hosting for bucket
- **Index Document**: Default page (e.g., index.html)
- **Error Document**: Custom error page (e.g., error.html)
- **Redirection**: Redirect requests to another host

#### Requirements
- **Public Access**: Objects must be publicly readable
- **Bucket Policy**: Allow public access to website content
- **DNS**: Configure DNS to point to S3 website endpoint

#### Website Endpoints
- **Format**: `bucket-name.s3-website-region.amazonaws.com`
- **Regional**: Each region has specific endpoint format
- **HTTPS**: Not supported natively (use CloudFront)

#### Use Cases
- **Marketing Sites**: Simple websites with static content
- **Documentation**: Host documentation and guides
- **SPAs**: Single Page Applications (React, Angular, Vue)
- **Landing Pages**: Campaign and product pages

### S3 Transfer Acceleration

#### How It Works
Uses Amazon CloudFront's globally distributed edge locations to accelerate uploads to S3.

#### Benefits
- **Global Acceleration**: Faster uploads from worldwide locations
- **Automatic Routing**: Intelligent routing through optimal paths
- **No Changes Required**: Compatible with existing applications
- **Speed Comparison**: Tool to test speed improvements

#### Configuration
- **Enable**: Turn on Transfer Acceleration for bucket
- **Endpoint**: Use accelerated endpoint for uploads
- **Testing**: Use speed comparison tool to verify benefits

#### Cost
- **Additional Charges**: Per GB transferred through edge locations
- **Regional Variation**: Different pricing in different regions
- **ROI Analysis**: Compare cost vs. time savings

### Multipart Upload

#### Overview
Allows uploading large objects in parts, providing better performance and reliability for large files.

#### Benefits
- **Parallel Uploads**: Upload parts simultaneously
- **Resume Capability**: Resume failed uploads
- **Early Completion**: Start upload before knowing total size
- **Improved Performance**: Better throughput for large files

#### Process
1. **Initiate**: Start multipart upload
2. **Upload Parts**: Upload individual parts (5MB - 5GB each)
3. **Complete**: Combine parts into single object
4. **Abort**: Cancel and clean up if needed

#### Best Practices
- **Part Size**: 5-100 MB typically optimal
- **Parallelism**: Upload multiple parts concurrently
- **Error Handling**: Retry failed parts individually
- **Cleanup**: Use lifecycle policies to clean up incomplete uploads

### S3 Inventory

#### Purpose
Provides scheduled reports about objects in your buckets, enabling large-scale analysis and management.

#### Report Contents
- **Object Metadata**: Size, last modified, storage class, etc.
- **Encryption Status**: Encryption type and key information
- **Replication Status**: Cross-region replication status
- **Custom Fields**: Select specific metadata to include

#### Output Formats
- **CSV**: Comma-separated values
- **ORC**: Optimized Row Columnar (for big data tools)
- **Parquet**: Columnar storage format

#### Use Cases
- **Compliance Auditing**: Verify encryption and retention policies
- **Cost Analysis**: Analyze storage class distribution
- **Lifecycle Planning**: Understand object age and access patterns
- **Security Assessment**: Identify unencrypted objects

### S3 Analytics

#### Storage Class Analysis
- **Purpose**: Understand access patterns to optimize storage classes
- **Recommendations**: Suggests optimal lifecycle policies
- **Filters**: Analyze specific prefixes or tags
- **Export**: Results can be exported for further analysis

#### Usage Reports
- **Access Patterns**: Frequency of object access
- **Cost Optimization**: Identify opportunities for savings
- **Lifecycle Tuning**: Optimize transition timing

### Integration with AWS Services

#### AWS CloudFormation
- **Infrastructure as Code**: Define S3 resources in templates
- **Automation**: Automated bucket and policy creation
- **Version Control**: Track infrastructure changes

#### AWS Config
- **Compliance Monitoring**: Track S3 configuration changes
- **Rules**: Automated compliance checking
- **Remediation**: Automatic fixing of configuration drift

#### AWS CloudTrail
- **API Logging**: Log all S3 API calls
- **Security Auditing**: Track access and modifications
- **Compliance**: Meet audit and regulatory requirements

#### Amazon Macie
- **Data Discovery**: Automatically discover sensitive data
- **Classification**: Classify data based on content
- **Security**: Identify potential security risks

## SAA-C03 Exam Scenarios

### Common Exam Question Patterns

#### Storage Class Selection
**Scenario**: A company needs to store financial records that are accessed frequently for the first month, occasionally for the next 11 months, and rarely thereafter for compliance purposes (7 years total retention).

**Analysis**:
- First month: S3 Standard (frequent access)
- Months 2-12: S3 Standard-IA (occasional access)
- Years 2-7: S3 Glacier Deep Archive (compliance, lowest cost)

**Solution**: Lifecycle policy with transitions at 30 days and 365 days

**Key Exam Tips**:
- Consider access patterns over time
- Factor in minimum storage durations
- Choose based on retrieval requirements

#### Cross-Region Replication Scenario
**Scenario**: A global company needs to ensure data is available in multiple regions for disaster recovery and compliance, with automatic failover capabilities.

**Requirements**:
- Data in multiple regions
- Automatic replication
- Different storage classes for cost optimization

**Solution**:
- Enable versioning on all buckets
- Configure CRR with appropriate IAM roles
- Use different storage classes in destination (e.g., Standard-IA)
- Implement Route 53 for failover routing

**Key Exam Tips**:
- CRR requires versioning
- Different regions for disaster recovery
- Consider storage class in destination

#### Security and Compliance Scenario
**Scenario**: A healthcare company needs to store patient records with strict access controls, encryption, and audit trails.

**Requirements**:
- Encryption at rest and in transit
- Fine-grained access control
- Audit logging
- Compliance with regulations

**Solution**:
- Enable S3 default encryption (SSE-KMS)
- Implement bucket policies with condition keys
- Enable CloudTrail for API logging
- Use S3 Object Lock for WORM compliance
- Configure VPC endpoints for private access

**Key Exam Tips**:
- Layer security controls
- Use KMS for sensitive data
- CloudTrail for audit requirements
- Object Lock for compliance

#### Performance Optimization Scenario
**Scenario**: A media company uploads thousands of large video files daily from global locations and needs optimal performance.

**Requirements**:
- Fast uploads globally
- Handle large files efficiently
- Cost-effective solution

**Solution**:
- Enable S3 Transfer Acceleration
- Use multipart uploads for files >100MB
- Implement random prefixes to avoid hot-spotting
- Use CloudFront for global distribution of completed content

**Key Exam Tips**:
- Transfer Acceleration for global uploads
- Multipart uploads for large files
- Avoid sequential prefixes
- CloudFront for distribution

#### Cost Optimization Scenario
**Scenario**: A company has unpredictable access patterns for their data and wants to minimize storage costs without impacting performance.

**Analysis**:
- Unknown access patterns = Intelligent-Tiering
- Automatic optimization without operational overhead
- No retrieval fees for frequent/infrequent tiers

**Solution**: S3 Intelligent-Tiering with optional archive tiers enabled

**Key Exam Tips**:
- Intelligent-Tiering for unknown patterns
- No retrieval fees between frequent/infrequent
- Consider monitoring fees vs. potential savings

### Exam-Focused Best Practices

#### Storage Class Decision Matrix
```
Frequent Access (daily) → S3 Standard
Infrequent Access (monthly) → S3 Standard-IA
Infrequent + Cost Sensitive → S3 One Zone-IA
Archive + Instant Access → S3 Glacier Instant Retrieval
Archive + Hours OK → S3 Glacier Flexible Retrieval
Long-term Archive → S3 Glacier Deep Archive
Unknown Patterns → S3 Intelligent-Tiering
```

---

## AWS CLI Commands Reference

### Bucket Operations

#### Create and Manage Buckets
```bash
# Create a bucket
aws s3 mb s3://my-bucket-name --region us-east-1

# Create a bucket with specific configuration
aws s3api create-bucket \
    --bucket my-bucket-name \
    --region us-west-2 \
    --create-bucket-configuration LocationConstraint=us-west-2

# List all buckets
aws s3 ls

# List contents of a bucket
aws s3 ls s3://my-bucket-name

# List with details
aws s3 ls s3://my-bucket-name --recursive --human-readable --summarize

# Delete an empty bucket
aws s3 rb s3://my-bucket-name

# Delete bucket and all contents (force)
aws s3 rb s3://my-bucket-name --force
```

#### Bucket Configuration
```bash
# Enable versioning
aws s3api put-bucket-versioning \
    --bucket my-bucket-name \
    --versioning-configuration Status=Enabled

# Get versioning status
aws s3api get-bucket-versioning --bucket my-bucket-name

# Enable server access logging
aws s3api put-bucket-logging \
    --bucket my-bucket-name \
    --bucket-logging-status file://logging.json

# Enable bucket encryption
aws s3api put-bucket-encryption \
    --bucket my-bucket-name \
    --server-side-encryption-configuration file://encryption.json

# Get bucket encryption
aws s3api get-bucket-encryption --bucket my-bucket-name

# Enable Transfer Acceleration
aws s3api put-bucket-accelerate-configuration \
    --bucket my-bucket-name \
    --accelerate-configuration Status=Enabled
```

### Object Operations

#### Upload and Download Objects
```bash
# Upload a file
aws s3 cp myfile.txt s3://my-bucket-name/

# Upload with storage class
aws s3 cp myfile.txt s3://my-bucket-name/ \
    --storage-class STANDARD_IA

# Upload directory recursively
aws s3 cp mydir/ s3://my-bucket-name/mydir/ --recursive

# Upload with server-side encryption
aws s3 cp myfile.txt s3://my-bucket-name/ \
    --server-side-encryption AES256

# Upload with KMS encryption
aws s3 cp myfile.txt s3://my-bucket-name/ \
    --server-side-encryption aws:kms \
    --ssekms-key-id alias/my-key

# Download a file
aws s3 cp s3://my-bucket-name/myfile.txt ./

# Download directory recursively
aws s3 cp s3://my-bucket-name/mydir/ ./mydir/ --recursive

# Sync local directory to S3
aws s3 sync ./local-dir s3://my-bucket-name/remote-dir/

# Sync S3 to local directory
aws s3 sync s3://my-bucket-name/remote-dir/ ./local-dir

# Sync with delete (remove files not in source)
aws s3 sync ./local-dir s3://my-bucket-name/remote-dir/ --delete
```

#### Move and Delete Objects
```bash
# Move/rename object
aws s3 mv s3://my-bucket-name/oldfile.txt s3://my-bucket-name/newfile.txt

# Move local file to S3
aws s3 mv myfile.txt s3://my-bucket-name/

# Delete an object
aws s3 rm s3://my-bucket-name/myfile.txt

# Delete all objects in a directory
aws s3 rm s3://my-bucket-name/mydir/ --recursive

# Delete specific version of object
aws s3api delete-object \
    --bucket my-bucket-name \
    --key myfile.txt \
    --version-id versionId123
```

#### Object Metadata and Properties
```bash
# Get object metadata
aws s3api head-object \
    --bucket my-bucket-name \
    --key myfile.txt

# Copy object with new metadata
aws s3api copy-object \
    --bucket my-bucket-name \
    --copy-source my-bucket-name/myfile.txt \
    --key myfile.txt \
    --metadata Key1=Value1,Key2=Value2 \
    --metadata-directive REPLACE

# Change storage class of existing object
aws s3api copy-object \
    --bucket my-bucket-name \
    --copy-source my-bucket-name/myfile.txt \
    --key myfile.txt \
    --storage-class GLACIER \
    --metadata-directive COPY

# Set object ACL
aws s3api put-object-acl \
    --bucket my-bucket-name \
    --key myfile.txt \
    --acl public-read

# Get object ACL
aws s3api get-object-acl \
    --bucket my-bucket-name \
    --key myfile.txt
```

### Multipart Upload

```bash
# Initiate multipart upload
aws s3api create-multipart-upload \
    --bucket my-bucket-name \
    --key large-file.zip

# Upload parts (example for part 1)
aws s3api upload-part \
    --bucket my-bucket-name \
    --key large-file.zip \
    --part-number 1 \
    --body part1.zip \
    --upload-id <upload-id>

# Complete multipart upload
aws s3api complete-multipart-upload \
    --bucket my-bucket-name \
    --key large-file.zip \
    --upload-id <upload-id> \
    --multipart-upload file://parts.json

# Abort multipart upload
aws s3api abort-multipart-upload \
    --bucket my-bucket-name \
    --key large-file.zip \
    --upload-id <upload-id>

# List multipart uploads
aws s3api list-multipart-uploads \
    --bucket my-bucket-name
```

### Versioning

```bash
# List object versions
aws s3api list-object-versions \
    --bucket my-bucket-name \
    --prefix myfile.txt

# Get specific version of object
aws s3api get-object \
    --bucket my-bucket-name \
    --key myfile.txt \
    --version-id versionId123 \
    myfile-version.txt

# Restore deleted object (remove delete marker)
aws s3api delete-object \
    --bucket my-bucket-name \
    --key myfile.txt \
    --version-id <delete-marker-id>
```

### Bucket Policies and ACLs

```bash
# Get bucket policy
aws s3api get-bucket-policy \
    --bucket my-bucket-name

# Set bucket policy
aws s3api put-bucket-policy \
    --bucket my-bucket-name \
    --policy file://policy.json

# Delete bucket policy
aws s3api delete-bucket-policy \
    --bucket my-bucket-name

# Get bucket ACL
aws s3api get-bucket-acl \
    --bucket my-bucket-name

# Set bucket ACL
aws s3api put-bucket-acl \
    --bucket my-bucket-name \
    --acl private

# Block public access
aws s3api put-public-access-block \
    --bucket my-bucket-name \
    --public-access-block-configuration \
    "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

# Get public access block configuration
aws s3api get-public-access-block-configuration \
    --bucket my-bucket-name
```

### Lifecycle Policies

```bash
# Set lifecycle policy
aws s3api put-bucket-lifecycle-configuration \
    --bucket my-bucket-name \
    --lifecycle-configuration file://lifecycle.json

# Get lifecycle policy
aws s3api get-bucket-lifecycle-configuration \
    --bucket my-bucket-name

# Delete lifecycle policy
aws s3api delete-bucket-lifecycle \
    --bucket my-bucket-name

# Example lifecycle.json
# {
#   "Rules": [
#     {
#       "Id": "MoveToIA",
#       "Status": "Enabled",
#       "Transitions": [
#         {
#           "Days": 30,
#           "StorageClass": "STANDARD_IA"
#         },
#         {
#           "Days": 90,
#           "StorageClass": "GLACIER"
#         }
#       ],
#       "Filter": {
#         "Prefix": "documents/"
#       }
#     }
#   ]
# }
```

### Replication

```bash
# Configure replication
aws s3api put-bucket-replication \
    --bucket my-bucket-name \
    --replication-configuration file://replication.json

# Get replication configuration
aws s3api get-bucket-replication \
    --bucket my-bucket-name

# Delete replication configuration
aws s3api delete-bucket-replication \
    --bucket my-bucket-name
```

### Static Website Hosting

```bash
# Enable static website hosting
aws s3api put-bucket-website \
    --bucket my-bucket-name \
    --website-configuration file://website.json

# Get website configuration
aws s3api get-bucket-website \
    --bucket my-bucket-name

# Delete website configuration
aws s3api delete-bucket-website \
    --bucket my-bucket-name

# Example website.json
# {
#   "IndexDocument": {
#     "Suffix": "index.html"
#   },
#   "ErrorDocument": {
#     "Key": "error.html"
#   }
# }
```

### Pre-signed URLs

```bash
# Generate pre-signed URL (valid for 1 hour)
aws s3 presign s3://my-bucket-name/myfile.txt \
    --expires-in 3600

# Generate pre-signed URL for upload
aws s3 presign s3://my-bucket-name/upload-file.txt \
    --expires-in 3600
```

### Bucket Notifications

```bash
# Configure bucket notifications
aws s3api put-bucket-notification-configuration \
    --bucket my-bucket-name \
    --notification-configuration file://notification.json

# Get notification configuration
aws s3api get-bucket-notification-configuration \
    --bucket my-bucket-name

# Example notification.json for Lambda
# {
#   "LambdaFunctionConfigurations": [
#     {
#       "Id": "ObjectCreated",
#       "LambdaFunctionArn": "arn:aws:lambda:us-east-1:123456789012:function:MyFunction",
#       "Events": ["s3:ObjectCreated:*"]
#     }
#   ]
# }
```

### Glacier Operations

```bash
# Initiate restore from Glacier
aws s3api restore-object \
    --bucket my-bucket-name \
    --key myfile.txt \
    --restore-request '{"Days":7,"GlacierJobParameters":{"Tier":"Standard"}}'

# Check restore status
aws s3api head-object \
    --bucket my-bucket-name \
    --key myfile.txt

# Expedited retrieval
aws s3api restore-object \
    --bucket my-bucket-name \
    --key myfile.txt \
    --restore-request '{"Days":1,"GlacierJobParameters":{"Tier":"Expedited"}}'

# Bulk retrieval
aws s3api restore-object \
    --bucket my-bucket-name \
    --key myfile.txt \
    --restore-request '{"Days":7,"GlacierJobParameters":{"Tier":"Bulk"}}'
```

### Glacier Vault Operations

```bash
# Create a vault
aws glacier create-vault \
    --account-id - \
    --vault-name my-vault

# List vaults
aws glacier list-vaults --account-id -

# Describe vault
aws glacier describe-vault \
    --account-id - \
    --vault-name my-vault

# Delete vault
aws glacier delete-vault \
    --account-id - \
    --vault-name my-vault

# Initiate archive retrieval
aws glacier initiate-job \
    --account-id - \
    --vault-name my-vault \
    --job-parameters '{"Type":"archive-retrieval","ArchiveId":"archive-id","Tier":"Standard"}'

# List jobs
aws glacier list-jobs \
    --account-id - \
    --vault-name my-vault

# Get job output
aws glacier get-job-output \
    --account-id - \
    --vault-name my-vault \
    --job-id job-id \
    output-file.txt
```

### S3 Analytics and Inventory

```bash
# Configure S3 analytics
aws s3api put-bucket-analytics-configuration \
    --bucket my-bucket-name \
    --id analytics-id \
    --analytics-configuration file://analytics.json

# Get analytics configuration
aws s3api get-bucket-analytics-configuration \
    --bucket my-bucket-name \
    --id analytics-id

# Configure S3 inventory
aws s3api put-bucket-inventory-configuration \
    --bucket my-bucket-name \
    --id inventory-id \
    --inventory-configuration file://inventory.json

# Get inventory configuration
aws s3api get-bucket-inventory-configuration \
    --bucket my-bucket-name \
    --id inventory-id
```

### Tagging

```bash
# Add tags to bucket
aws s3api put-bucket-tagging \
    --bucket my-bucket-name \
    --tagging 'TagSet=[{Key=Environment,Value=Production},{Key=Owner,Value=TeamA}]'

# Get bucket tags
aws s3api get-bucket-tagging \
    --bucket my-bucket-name

# Delete bucket tags
aws s3api delete-bucket-tagging \
    --bucket my-bucket-name

# Add tags to object
aws s3api put-object-tagging \
    --bucket my-bucket-name \
    --key myfile.txt \
    --tagging 'TagSet=[{Key=Category,Value=Documents}]'

# Get object tags
aws s3api get-object-tagging \
    --bucket my-bucket-name \
    --key myfile.txt
```

### CORS Configuration

```bash
# Set CORS configuration
aws s3api put-bucket-cors \
    --bucket my-bucket-name \
    --cors-configuration file://cors.json

# Get CORS configuration
aws s3api get-bucket-cors \
    --bucket my-bucket-name

# Delete CORS configuration
aws s3api delete-bucket-cors \
    --bucket my-bucket-name

# Example cors.json
# {
#   "CORSRules": [
#     {
#       "AllowedOrigins": ["https://example.com"],
#       "AllowedMethods": ["GET", "PUT", "POST"],
#       "AllowedHeaders": ["*"],
#       "MaxAgeSeconds": 3000
#     }
#   ]
# }
```

### Requester Pays and Other Features

```bash
# Enable Requester Pays
aws s3api put-bucket-request-payment \
    --bucket my-bucket-name \
    --request-payment-configuration Payer=Requester

# Get request payment configuration
aws s3api get-bucket-request-payment \
    --bucket my-bucket-name

# Enable Object Lock
aws s3api put-object-lock-configuration \
    --bucket my-bucket-name \
    --object-lock-configuration file://object-lock.json

# Get Object Lock configuration
aws s3api get-object-lock-configuration \
    --bucket my-bucket-name
```

---

## SAA-C03 Exam Scenarios

#### Security Decision Framework
1. **Encryption**: Always encrypt sensitive data
2. **Access Control**: Use IAM policies + bucket policies
3. **Network**: VPC endpoints for private access
4. **Auditing**: CloudTrail for compliance
5. **Public Access**: Block unless specifically needed

#### Performance Optimization Checklist
- [ ] Use Transfer Acceleration for global access
- [ ] Implement multipart uploads for large files
- [ ] Avoid sequential naming patterns
- [ ] Use CloudFront for content distribution
- [ ] Monitor request patterns and optimize

#### Cost Optimization Strategies
1. **Analyze Access Patterns**: Use S3 Analytics
2. **Implement Lifecycle Policies**: Automate transitions
3. **Choose Right Storage Class**: Match to access pattern
4. **Clean Up**: Remove incomplete uploads and unused versions
5. **Monitor Costs**: Use Cost Explorer and billing alerts

### Key Exam Formulas and Limits

#### Storage Limits
- **Object Size**: 0 bytes to 5 TB
- **Bucket Name**: 3-63 characters, globally unique
- **Multipart Parts**: 10,000 maximum per object
- **Part Size**: 5 MB to 5 GB (except last part)

#### Performance Baselines
- **Request Rate**: 3,500 PUT/COPY/POST/DELETE per prefix per second
- **Request Rate**: 5,500 GET/HEAD per prefix per second
- **Prefixes**: Unlimited number of prefixes

#### Minimum Storage Durations
- **Standard-IA**: 30 days
- **One Zone-IA**: 30 days
- **Glacier Instant Retrieval**: 90 days
- **Glacier Flexible Retrieval**: 90 days
- **Glacier Deep Archive**: 180 days

#### Retrieval Times
- **Standard/IA**: Immediate
- **Glacier Instant**: Milliseconds
- **Glacier Flexible Expedited**: 1-5 minutes
- **Glacier Flexible Standard**: 3-5 hours
- **Glacier Flexible Bulk**: 5-12 hours
- **Deep Archive Standard**: 12 hours
- **Deep Archive Bulk**: 48 hours

### Common Exam Traps

#### Trap 1: Storage Class Transitions
**Wrong**: Direct transition from Standard to Glacier Deep Archive
**Right**: Must follow transition waterfall (or use lifecycle policy with appropriate timing)

#### Trap 2: Cross-Region Replication Requirements
**Wrong**: Assuming CRR works without versioning
**Right**: Versioning must be enabled on both source and destination

#### Trap 3: Glacier Retrieval Costs
**Wrong**: Choosing Glacier for frequently accessed data
**Right**: Consider total cost including retrieval fees

#### Trap 4: Public Access Settings
**Wrong**: Making bucket public when only specific objects need public access
**Right**: Use object-level permissions or pre-signed URLs

#### Trap 5: Performance Assumptions
**Wrong**: Assuming sequential naming is optimal
**Right**: Random prefixes provide better performance distribution

### Study Tips for SAA-C03

#### Focus Areas
1. **Storage Classes**: Understand use cases and constraints
2. **Security**: Master IAM, bucket policies, and encryption
3. **Performance**: Know optimization techniques
4. **Cost**: Understand pricing models and optimization
5. **Integration**: How S3 works with other AWS services

#### Hands-On Practice
1. Create buckets with different storage classes
2. Configure lifecycle policies
3. Set up cross-region replication
4. Test multipart uploads
5. Configure static website hosting
6. Practice with AWS CLI and SDKs

#### Additional Resources
- AWS S3 User Guide
- AWS Well-Architected Framework
- AWS Pricing Calculator
- AWS Training and Certification
- AWS Whitepapers on storage best practices

---

## Summary

This comprehensive guide covers all essential aspects of Amazon S3 and Glacier for the AWS Solutions Architect Associate (SAA-C03) certification exam. Key takeaways include:

1. **Storage Classes**: Choose the right class based on access patterns and cost requirements
2. **Security**: Implement layered security with encryption, access controls, and monitoring
3. **Performance**: Optimize for your specific use case with appropriate techniques
4. **Cost Management**: Use lifecycle policies and analytics to minimize costs
5. **Advanced Features**: Leverage versioning, replication, and event notifications for robust architectures
6. **Exam Success**: Understand common scenarios and avoid typical traps

Remember to practice hands-on with these services and understand how they integrate with other AWS services for a complete solution architecture approach.