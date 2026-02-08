# AWS CloudFront - SAA-C03 Certification Guide

## Table of Contents
1. [Introduction to CloudFront](#introduction-to-cloudfront)
2. [CloudFront Architecture](#cloudfront-architecture)
3. [CloudFront Distributions](#cloudfront-distributions)
4. [Origins and Origin Types](#origins-and-origin-types)
5. [Edge Locations and Regional Edge Caches](#edge-locations-and-regional-edge-caches)
6. [CloudFront Behaviors and Caching](#cloudfront-behaviors-and-caching)
7. [CloudFront Security](#cloudfront-security)
8. [CloudFront Performance Optimization](#cloudfront-performance-optimization)
9. [CloudFront Monitoring and Logging](#cloudfront-monitoring-and-logging)
10. [CloudFront Pricing](#cloudfront-pricing)
11. [CloudFront Use Cases](#cloudfront-use-cases)
12. [CloudFront vs Other Services](#cloudfront-vs-other-services)
13. [Common Exam Scenarios](#common-exam-scenarios)
14. [AWS CLI Commands Reference](#aws-cli-commands-reference)
15. [Best Practices](#best-practices)

## Introduction to CloudFront

AWS CloudFront is a fast content delivery network (CDN) service that securely delivers data, videos, applications, and APIs to customers globally with low latency and high transfer speeds.

### Key Features
- **Global Edge Network**: 400+ Points of Presence (PoPs) in 90+ cities across 47 countries
- **Real-time Metrics and Monitoring**: Integration with CloudWatch
- **Security**: Integration with AWS Shield, WAF, and Route 53
- **Programmable**: Lambda@Edge and CloudFront Functions
- **Cost-effective**: Pay-as-you-go pricing model

### Benefits
- **Improved Performance**: Reduced latency through global edge locations
- **Enhanced Security**: DDoS protection, SSL/TLS encryption
- **Scalability**: Automatic scaling to handle traffic spikes
- **Cost Optimization**: Reduced data transfer costs
- **Reliability**: High availability and fault tolerance

## CloudFront Architecture

### Core Components

```
User Request → Route 53 → CloudFront Edge Location → Origin Server
                    ↓
              Edge Cache Check
                    ↓
         Cache Hit: Serve from Edge
         Cache Miss: Fetch from Origin
```

### Request Flow
1. **User Request**: Client makes request to CloudFront domain
2. **DNS Resolution**: Route 53 resolves to nearest edge location
3. **Edge Location Check**: Checks if content is cached
4. **Cache Hit**: Serves content directly from edge
5. **Cache Miss**: Forwards request to origin server
6. **Origin Response**: Content returned and cached at edge
7. **Content Delivery**: Cached content served to user

## CloudFront Distributions

### Distribution Types

#### Web Distribution (Legacy)
- For static and dynamic content
- HTTP/HTTPS protocols
- Custom origins and S3 origins

#### Streaming Distribution (Deprecated)
- For streaming media files using Adobe Flash Media Server's RTMP protocol
- **Note**: Deprecated, use Web Distribution instead

### Distribution Configuration

```yaml
Distribution Settings:
  Origin Domain Name: example.s3.amazonaws.com
  Origin Path: /prod
  Origin ID: S3-example-bucket
  Restrict Bucket Access: Yes
  Origin Access Identity: Create New Identity
  Comment: Production distribution
  Default Root Object: index.html
  Logging: Enabled
  Bucket for Logs: logs.example.com
  Log Prefix: cloudfront/
  Price Class: Use All Edge Locations
  AWS WAF Web ACL: None
  Alternate Domain Names (CNAMEs): www.example.com
  SSL Certificate: Custom SSL Certificate
  Custom SSL Client Support: Only Clients that Support SNI
  Security Policy: TLSv1.2_2021
  Supported HTTP Versions: HTTP/2, HTTP/1.1, HTTP/1.0
  Default Root Object: index.html
  Error Pages: Custom Error Response
  Restrictions: Geo Restriction
```

### Distribution States
- **InProgress**: Deployment in progress (15-20 minutes)
- **Deployed**: Ready to serve content
- **Disabled**: Not accepting requests

## Origins and Origin Types

### S3 Origins

#### Standard S3 Origin
```yaml
Origin Settings:
  Domain Name: mybucket.s3.amazonaws.com
  Origin Path: /production
  Origin Access Control (OAC): Enabled
  Custom Headers:
    - Header Name: X-Custom-Header
      Value: custom-value
```

#### S3 Website Origin
```yaml
Origin Settings:
  Domain Name: mybucket.s3-website-us-east-1.amazonaws.com
  Origin Protocol Policy: HTTP Only
  Origin Path: /
```

### Custom Origins

#### Application Load Balancer
```yaml
Origin Settings:
  Domain Name: my-alb-1234567890.us-east-1.elb.amazonaws.com
  Origin Protocol Policy: HTTPS Only
  HTTP Port: 80
  HTTPS Port: 443
  Origin SSL Protocols: TLSv1.2
  Origin Response Timeout: 30 seconds
  Origin Keep-alive Timeout: 5 seconds
```

#### EC2 Instance
```yaml
Origin Settings:
  Domain Name: ec2-203-0-113-12.compute-1.amazonaws.com
  Origin Protocol Policy: Match Viewer
  Custom Headers:
    - Header Name: X-Forwarded-Host
      Value: ${host}
```

### Origin Groups (Failover)
```yaml
Primary Origin: S3-bucket-primary
Secondary Origin: S3-bucket-secondary
Failover Criteria:
  - HTTP Status Codes: 403, 404, 500, 502, 503, 504
  - Origin Request Timeout: 30 seconds
```

## Edge Locations and Regional Edge Caches

### Edge Location Hierarchy

```
User → Edge Location → Regional Edge Cache → Origin Server
```

### Edge Location Features
- **Cache Duration**: Based on TTL settings
- **Cache Key**: URL path + query strings + headers
- **Compression**: Automatic Gzip compression
- **HTTP/2**: Support for HTTP/2 protocol

### Regional Edge Caches
- **Larger Cache**: More storage than edge locations
- **Longer TTL**: Objects stay cached longer
- **Fewer Locations**: Strategic placement for cost optimization
- **Intermediate Layer**: Between edge locations and origins

### Cache Behavior
```
Cache Hit Ratio Optimization:
1. Edge Location (Highest Hit Ratio)
2. Regional Edge Cache (Medium Hit Ratio)
3. Origin Server (Cache Miss)
```

## CloudFront Behaviors and Caching

### Cache Behaviors

#### Default Cache Behavior
```yaml
Path Pattern: *
Origin: S3-bucket-origin
Viewer Protocol Policy: Redirect HTTP to HTTPS
Allowed HTTP Methods: GET, HEAD, OPTIONS, PUT, POST, PATCH, DELETE
Cached HTTP Methods: GET, HEAD, OPTIONS
Cache Policy: Managed-CachingOptimized
Origin Request Policy: None
Response Headers Policy: None
Compress Objects Automatically: Yes
```

#### Custom Cache Behavior
```yaml
Path Pattern: /api/*
Origin: ALB-origin
Viewer Protocol Policy: HTTPS Only
Allowed HTTP Methods: GET, HEAD, OPTIONS, PUT, POST, PATCH, DELETE
Cache Policy: Managed-CachingDisabled
Origin Request Policy: Managed-CORS-S3Origin
TTL Settings:
  Minimum TTL: 0
  Default TTL: 86400
  Maximum TTL: 31536000
```

### Cache Policies

#### Managed Cache Policies
- **CachingOptimized**: Cache based on query strings and headers
- **CachingDisabled**: No caching, forward all requests to origin
- **CachingOptimizedForUncompressedObjects**: Optimized for uncompressed content
- **Elemental-MediaPackage**: Optimized for media streaming

#### Custom Cache Policy
```yaml
Cache Policy Settings:
  Name: CustomCachePolicy
  Default TTL: 86400
  Maximum TTL: 31536000
  Cache Key Contents:
    Query Strings:
      Include: Specified
      Query Strings: version, locale
    Headers:
      Include: Specified  
      Headers: Authorization, CloudFront-Viewer-Country
    Cookies:
      Include: Specified
      Cookies: session-id, user-pref
```

### Cache Invalidation
```bash
# AWS CLI - Invalidate specific files
aws cloudfront create-invalidation \
  --distribution-id E1234567890123 \
  --paths "/*"

# Invalidate specific paths
aws cloudfront create-invalidation \
  --distribution-id E1234567890123 \
  --paths "/images/*" "/css/style.css"
```

### Versioning Strategy
```
Instead of invalidation, use versioning:
- style-v1.css → style-v2.css
- app-20231001.js → app-20231002.js
- /v1/api/users → /v2/api/users
```

## CloudFront Security

### SSL/TLS Configuration

#### Viewer Certificate Options
```yaml
Default CloudFront Certificate:
  - *.cloudfront.net domain
  - No additional cost
  - Limited to CloudFront domains

Custom SSL Certificate:
  - Your own domain (example.com)
  - Certificate in ACM (us-east-1)
  - SNI or Dedicated IP support
```

#### SSL Certificate Setup
```yaml
Custom SSL Certificate Settings:
  SSL Certificate: Custom SSL Certificate (ACM)
  Custom SSL Client Support: Only Clients that Support SNI
  Security Policy: TLSv1.2_2021
  Minimum Protocol Version: TLSv1.2
```

### Origin Access Control (OAC)

#### S3 Origin Access Control
```yaml
Origin Access Control Settings:
  Name: S3-OAC-example
  Description: OAC for S3 bucket access
  Origin Type: S3
  Signing Behavior: Always sign requests
  Signing Protocol: sigv4
```

#### S3 Bucket Policy for OAC
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowCloudFrontServicePrincipal",
      "Effect": "Allow",
      "Principal": {
        "Service": "cloudfront.amazonaws.com"
      },
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::example-bucket/*",
      "Condition": {
        "StringEquals": {
          "AWS:SourceArn": "arn:aws:cloudfront::123456789012:distribution/E1234567890123"
        }
      }
    }
  ]
}
```

### Geo Restriction

#### Whitelist Configuration
```yaml
Geo Restriction:
  Restriction Type: Whitelist
  Countries: US, CA, GB, DE, FR, JP
```

#### Blacklist Configuration
```yaml
Geo Restriction:
  Restriction Type: Blacklist
  Countries: XX, YY, ZZ
```

### AWS WAF Integration
```yaml
Web ACL Association:
  Web ACL: arn:aws:wafv2:us-east-1:123456789012:global/webacl/ExampleWebACL
  
WAF Rules:
  - SQL Injection Protection
  - XSS Protection
  - Rate Limiting
  - IP Whitelist/Blacklist
  - Geo Blocking
```

### Signed URLs and Signed Cookies

#### Signed URL Example
```python
import boto3
from botocore.signers import CloudFrontSigner
import datetime

def create_signed_url(url, key_id, private_key_string, expiration_date):
    signer = CloudFrontSigner(key_id, rsa_signer)
    
    signed_url = signer.generate_presigned_url(
        url, date_less_than=expiration_date
    )
    return signed_url
```

#### Use Cases for Signed URLs vs Signed Cookies
- **Signed URLs**: Individual file access, temporary access
- **Signed Cookies**: Multiple files, user session-based access

## CloudFront Performance Optimization

### Compression
```yaml
Compress Objects Automatically: Yes
Supported File Types:
  - text/html
  - text/css
  - text/javascript
  - application/javascript
  - application/json
  - application/xml
```

### HTTP/2 Support
```yaml
Supported HTTP Versions:
  - HTTP/2 (Default)
  - HTTP/1.1
  - HTTP/1.0
```

### Origin Shield
```yaml
Origin Shield Settings:
  Enable Origin Shield: Yes
  Origin Shield Region: us-east-1
  
Benefits:
  - Reduced origin load
  - Better cache hit ratio
  - Lower origin costs
  - Improved performance
```

### CloudFront Functions
```javascript
function handler(event) {
    var request = event.request;
    
    // Add security headers
    var response = {
        statusCode: 200,
        statusDescription: 'OK',
        headers: {
            'strict-transport-security': {
                value: 'max-age=31536000'
            },
            'x-content-type-options': {
                value: 'nosniff'
            },
            'x-frame-options': {
                value: 'DENY'
            }
        }
    };
    
    return response;
}
```

### Lambda@Edge
```python
import json

def lambda_handler(event, context):
    request = event['Records'][0]['cf']['request']
    headers = request['headers']
    
    # Modify request headers
    headers['host'] = [{'key': 'Host', 'value': 'example.com'}]
    headers['user-agent'] = [{'key': 'User-Agent', 'value': 'CloudFront-Lambda'}]
    
    return request
```

#### Lambda@Edge vs CloudFront Functions

| Feature | CloudFront Functions | Lambda@Edge |
|---------|---------------------|-------------|
| Runtime | JavaScript | Node.js, Python |
| Execution Location | Edge locations | Regional edge caches |
| Max Duration | Sub-millisecond | 5 seconds (viewer), 30 seconds (origin) |
| Memory | Limited | 128-3008 MB |
| Pricing | Lower cost | Higher cost |
| Use Cases | Simple logic | Complex processing |

## CloudFront Monitoring and Logging

### CloudWatch Metrics

#### Standard Metrics (Free)
```yaml
Available Metrics:
  - Requests: Number of requests
  - BytesDownloaded: Data transferred to viewers
  - BytesUploaded: Data uploaded to origin
  - 4xxErrorRate: Percentage of 4xx errors
  - 5xxErrorRate: Percentage of 5xx errors
  - OriginLatency: Origin response time
```

#### Real-time Metrics (Additional Cost)
```yaml
Real-time Metrics:
  - Requests per second
  - Data transfer rate
  - Error rates
  - Cache hit ratio
  - Origin latency
  
Update Frequency: Every 1 minute
```

### Access Logs
```yaml
Standard Logs:
  Delivery: S3 bucket
  Format: Tab-separated values
  Fields: Date, time, edge location, bytes, IP address, method, host, URI, status, referrer, user-agent, query-string, cookie, edge-result-type, edge-request-id, host-header, protocol, bytes-sent, time-taken, forwarded-for, ssl-protocol, ssl-cipher, edge-response-result-type, protocol-version

Real-time Logs:
  Delivery: Kinesis Data Streams
  Format: JSON
  Latency: Within seconds
```

### CloudTrail Integration
```yaml
API Calls Logged:
  - CreateDistribution
  - UpdateDistribution  
  - DeleteDistribution
  - CreateInvalidation
  - GetDistribution
  - ListDistributions
```

## CloudFront Pricing

### Price Classes

#### Price Class All
- All edge locations worldwide
- Best performance globally
- Highest cost

#### Price Class 200
- North America, Europe, Asia, Middle East, Africa
- Excludes Australia and South America edge locations
- Medium cost

#### Price Class 100
- North America and Europe only
- Lowest cost option
- May have higher latency for other regions

### Cost Components
```yaml
Data Transfer Out:
  - First 10 TB: $0.085 per GB (US/Europe)
  - Next 40 TB: $0.080 per GB
  - Next 100 TB: $0.060 per GB
  - Over 150 TB: $0.040 per GB

HTTP/HTTPS Requests:
  - First 10 million: $0.0075 per 10,000 requests
  - Over 10 million: $0.0075 per 10,000 requests

Dedicated IP SSL: $600 per month per certificate
SNI SSL: No additional charge

Origin Shield: $0.009 per 10,000 requests
```

### Cost Optimization Strategies
- Use appropriate Price Class
- Optimize cache hit ratios
- Use compression
- Implement proper TTL settings
- Use Origin Shield for multiple distributions

## CloudFront Use Cases

### Static Website Hosting
```yaml
Architecture:
  S3 Bucket (Static Files) → CloudFront → Route 53 → Users

Configuration:
  Origin: S3 Static Website
  Default Root Object: index.html
  Error Pages: 404.html
  Compression: Enabled
  SSL Certificate: ACM Certificate
```

### Dynamic Content Acceleration
```yaml
Architecture:
  ALB (Application) → CloudFront → Route 53 → Users

Configuration:
  Origin: Application Load Balancer
  Cache Policy: CachingDisabled for dynamic content
  Origin Request Policy: Forward all headers
  Edge Locations: Improve connection performance
```

### API Acceleration
```yaml
Architecture:
  API Gateway → CloudFront → Route 53 → Users

Configuration:
  Path Pattern: /api/*
  Cache Policy: Custom (short TTL for cacheable responses)
  Origin Request Policy: Forward required headers
  WAF: Rate limiting and security rules
```

### Video Streaming
```yaml
Architecture:
  S3/MediaPackage → CloudFront → Route 53 → Users

Configuration:
  Origin: S3 bucket or MediaPackage
  Cache Policy: Optimized for media files
  Allowed Methods: GET, HEAD, OPTIONS
  Compression: Disabled for video files
```

### Software Distribution
```yaml
Architecture:
  S3 (Software Binaries) → CloudFront → Route 53 → Users

Configuration:
  Origin: S3 bucket
  Signed URLs: For authenticated downloads
  Large Object Caching: Long TTL for software packages
  Origin Shield: Reduce S3 costs
```

## CloudFront vs Other Services

### CloudFront vs S3 Transfer Acceleration
| Feature | CloudFront | S3 Transfer Acceleration |
|---------|------------|-------------------------|
| Use Case | Content delivery | Upload acceleration |
| Direction | Download optimization | Upload optimization |
| Caching | Yes | No |
| Global Network | 400+ locations | AWS backbone |
| Cost | Per GB + requests | Per GB transferred |

### CloudFront vs Global Accelerator
| Feature | CloudFront | Global Accelerator |
|---------|------------|-------------------|
| Layer | Application Layer (L7) | Network Layer (L4) |
| Protocol | HTTP/HTTPS | TCP/UDP |
| Caching | Yes | No |
| Use Case | Web content delivery | Application performance |
| Routing | Content-based | Performance-based |

### CloudFront vs ElastiCache
| Feature | CloudFront | ElastiCache |
|---------|------------|-------------|
| Location | Edge locations | Application-level |
| Content Type | Static/dynamic web content | Application data |
| Management | Fully managed | Managed service |
| Integration | Web applications | Database/application caching |

## Common Exam Scenarios

### Scenario 1: Global Website Performance
**Question**: Company needs to improve website performance for global users accessing static content from S3.

**Solution**: 
- CloudFront distribution with S3 origin
- Origin Access Control (OAC) for security
- Appropriate price class based on user distribution
- Enable compression for text-based content

### Scenario 2: Dynamic Content with Authentication
**Question**: Web application serves both static and dynamic content, requires user authentication for certain paths.

**Solution**:
- Multiple cache behaviors for different path patterns
- Static content: Long TTL, compression enabled  
- Dynamic content: Short TTL or no caching
- Signed URLs/cookies for authenticated content

### Scenario 3: Cost Optimization for Media Delivery
**Question**: Video streaming service needs to reduce bandwidth costs while maintaining performance.

**Solution**:
- CloudFront with appropriate price class
- Origin Shield to reduce origin requests
- Long TTL for video files
- Optimize for cache hit ratio

### Scenario 4: Security Requirements
**Question**: E-commerce site requires DDoS protection, geo-blocking, and SSL encryption.

**Solution**:
- CloudFront with AWS Shield Standard (included)
- WAF integration for application-layer protection
- Geo-restriction for compliance requirements
- Custom SSL certificate from ACM

### Scenario 5: Multi-Region Failover
**Question**: Application needs failover capability between regions for high availability.

**Solution**:
- Origin groups with primary and secondary origins
- Health checks and failover criteria
- Route 53 health checks for DNS-level failover
- CloudFront provides additional layer of availability

## AWS CLI Commands Reference

### Create CloudFront Distribution

```bash
# Create distribution with S3 origin using distribution config file
aws cloudfront create-distribution \
  --distribution-config file://distribution-config.json

# Example distribution-config.json for S3 origin
cat > distribution-config.json <<'EOF'
{
  "CallerReference": "my-distribution-2026-02-08",
  "Comment": "Production S3 Distribution",
  "Enabled": true,
  "Origins": {
    "Quantity": 1,
    "Items": [
      {
        "Id": "S3-my-bucket",
        "DomainName": "my-bucket.s3.amazonaws.com",
        "S3OriginConfig": {
          "OriginAccessIdentity": "origin-access-identity/cloudfront/E1234567890ABC"
        },
        "ConnectionAttempts": 3,
        "ConnectionTimeout": 10
      }
    ]
  },
  "DefaultCacheBehavior": {
    "TargetOriginId": "S3-my-bucket",
    "ViewerProtocolPolicy": "redirect-to-https",
    "AllowedMethods": {
      "Quantity": 2,
      "Items": ["GET", "HEAD"],
      "CachedMethods": {
        "Quantity": 2,
        "Items": ["GET", "HEAD"]
      }
    },
    "Compress": true,
    "MinTTL": 0,
    "DefaultTTL": 86400,
    "MaxTTL": 31536000,
    "ForwardedValues": {
      "QueryString": false,
      "Cookies": {
        "Forward": "none"
      }
    },
    "TrustedSigners": {
      "Enabled": false,
      "Quantity": 0
    }
  },
  "DefaultRootObject": "index.html",
  "PriceClass": "PriceClass_100"
}
EOF

# Create distribution with custom origin (ALB/EC2)
cat > custom-origin-config.json <<'EOF'
{
  "CallerReference": "alb-distribution-2026-02-08",
  "Comment": "ALB Origin Distribution",
  "Enabled": true,
  "Origins": {
    "Quantity": 1,
    "Items": [
      {
        "Id": "ALB-origin",
        "DomainName": "my-alb-123456.us-east-1.elb.amazonaws.com",
        "CustomOriginConfig": {
          "HTTPPort": 80,
          "HTTPSPort": 443,
          "OriginProtocolPolicy": "https-only",
          "OriginSslProtocols": {
            "Quantity": 3,
            "Items": ["TLSv1.2", "TLSv1.1", "TLSv1"]
          },
          "OriginReadTimeout": 30,
          "OriginKeepaliveTimeout": 5
        }
      }
    ]
  },
  "DefaultCacheBehavior": {
    "TargetOriginId": "ALB-origin",
    "ViewerProtocolPolicy": "redirect-to-https",
    "AllowedMethods": {
      "Quantity": 7,
      "Items": ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"],
      "CachedMethods": {
        "Quantity": 2,
        "Items": ["GET", "HEAD"]
      }
    },
    "MinTTL": 0,
    "DefaultTTL": 0,
    "MaxTTL": 0,
    "ForwardedValues": {
      "QueryString": true,
      "Headers": {
        "Quantity": 3,
        "Items": ["Host", "Authorization", "CloudFront-Forwarded-Proto"]
      },
      "Cookies": {
        "Forward": "all"
      }
    }
  },
  "PriceClass": "PriceClass_All"
}
EOF

aws cloudfront create-distribution \
  --distribution-config file://custom-origin-config.json
```

### Update CloudFront Distribution

```bash
# Get current distribution config
aws cloudfront get-distribution-config \
  --id E1234567890ABC \
  --output json > current-config.json

# Extract ETag for update
ETAG=$(aws cloudfront get-distribution-config \
  --id E1234567890ABC \
  --query 'ETag' \
  --output text)

# Edit the configuration (modify current-config.json)
# Then update the distribution
aws cloudfront update-distribution \
  --id E1234567890ABC \
  --distribution-config file://current-config.json \
  --if-match $ETAG

# Enable/disable distribution
aws cloudfront get-distribution-config \
  --id E1234567890ABC > config.json

# Modify Enabled field in config.json to true/false
jq '.DistributionConfig.Enabled = false' config.json > updated-config.json

aws cloudfront update-distribution \
  --id E1234567890ABC \
  --distribution-config file://updated-config.json \
  --if-match $(aws cloudfront get-distribution-config --id E1234567890ABC --query 'ETag' --output text)
```

### Create Cache Invalidation

```bash
# Invalidate all objects
aws cloudfront create-invalidation \
  --distribution-id E1234567890ABC \
  --paths "/*"

# Invalidate specific paths
aws cloudfront create-invalidation \
  --distribution-id E1234567890ABC \
  --paths "/images/*" "/css/*" "/js/app.js"

# Invalidate with caller reference
aws cloudfront create-invalidation \
  --distribution-id E1234567890ABC \
  --invalidation-batch "{\"Paths\":{\"Quantity\":2,\"Items\":[\"/index.html\",\"/about.html\"]},\"CallerReference\":\"invalidation-$(date +%s)\"}"

# Check invalidation status
aws cloudfront get-invalidation \
  --distribution-id E1234567890ABC \
  --id I1234567890ABC

# List invalidations
aws cloudfront list-invalidations \
  --distribution-id E1234567890ABC
```

### Origin Groups and Failover

```bash
# Create distribution with origin group for failover
cat > origin-group-config.json <<'EOF'
{
  "CallerReference": "origin-group-2026-02-08",
  "Comment": "Distribution with Origin Failover",
  "Enabled": true,
  "Origins": {
    "Quantity": 2,
    "Items": [
      {
        "Id": "primary-origin",
        "DomainName": "primary.example.com",
        "CustomOriginConfig": {
          "HTTPPort": 80,
          "HTTPSPort": 443,
          "OriginProtocolPolicy": "https-only"
        }
      },
      {
        "Id": "secondary-origin",
        "DomainName": "secondary.example.com",
        "CustomOriginConfig": {
          "HTTPPort": 80,
          "HTTPSPort": 443,
          "OriginProtocolPolicy": "https-only"
        }
      }
    ]
  },
  "OriginGroups": {
    "Quantity": 1,
    "Items": [
      {
        "Id": "origin-group-1",
        "FailoverCriteria": {
          "StatusCodes": {
            "Quantity": 4,
            "Items": [500, 502, 503, 504]
          }
        },
        "Members": {
          "Quantity": 2,
          "Items": [
            {"OriginId": "primary-origin"},
            {"OriginId": "secondary-origin"}
          ]
        }
      }
    ]
  },
  "DefaultCacheBehavior": {
    "TargetOriginId": "origin-group-1",
    "ViewerProtocolPolicy": "redirect-to-https",
    "AllowedMethods": {
      "Quantity": 2,
      "Items": ["GET", "HEAD"],
      "CachedMethods": {
        "Quantity": 2,
        "Items": ["GET", "HEAD"]
      }
    },
    "MinTTL": 0,
    "ForwardedValues": {
      "QueryString": false,
      "Cookies": {"Forward": "none"}
    }
  },
  "PriceClass": "PriceClass_All"
}
EOF

aws cloudfront create-distribution \
  --distribution-config file://origin-group-config.json
```

### Cache Behaviors

```bash
# Add custom cache behavior for API paths
# First get current config
aws cloudfront get-distribution-config \
  --id E1234567890ABC > current-dist-config.json

# Extract the DistributionConfig and add CacheBehaviors
# Example: Add behavior for /api/* path pattern
cat > cache-behavior.json <<'EOF'
{
  "PathPattern": "/api/*",
  "TargetOriginId": "ALB-origin",
  "ViewerProtocolPolicy": "https-only",
  "AllowedMethods": {
    "Quantity": 7,
    "Items": ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"],
    "CachedMethods": {
      "Quantity": 2,
      "Items": ["GET", "HEAD"]
    }
  },
  "MinTTL": 0,
  "DefaultTTL": 0,
  "MaxTTL": 0,
  "ForwardedValues": {
    "QueryString": true,
    "Headers": {
      "Quantity": 1,
      "Items": ["*"]
    },
    "Cookies": {
      "Forward": "all"
    }
  }
}
EOF

# Manually add this to CacheBehaviors in distribution config and update
```

### Field-Level Encryption

```bash
# Create field-level encryption profile
aws cloudfront create-field-level-encryption-profile \
  --field-level-encryption-profile-config file://fle-profile-config.json

# Example fle-profile-config.json
cat > fle-profile-config.json <<'EOF'
{
  "Name": "CreditCardEncryption",
  "CallerReference": "fle-profile-2026-02-08",
  "Comment": "Encrypt credit card fields",
  "EncryptionEntities": {
    "Quantity": 1,
    "Items": [
      {
        "PublicKeyId": "K1234567890ABC",
        "ProviderId": "MyProvider",
        "FieldPatterns": {
          "Quantity": 2,
          "Items": ["cardNumber", "cvv"]
        }
      }
    ]
  }
}
EOF

# Create field-level encryption config
aws cloudfront create-field-level-encryption-config \
  --field-level-encryption-config file://fle-config.json
```

### Lambda@Edge Functions

```bash
# Create Lambda function for Lambda@Edge
aws lambda create-function \
  --function-name cloudfront-viewer-request \
  --runtime nodejs18.x \
  --role arn:aws:iam::123456789012:role/lambda-edge-role \
  --handler index.handler \
  --zip-file fileb://function.zip \
  --region us-east-1

# Publish Lambda version (required for Lambda@Edge)
VERSION=$(aws lambda publish-version \
  --function-name cloudfront-viewer-request \
  --region us-east-1 \
  --query 'Version' \
  --output text)

echo "Published version: $VERSION"

# Get Lambda function ARN with version
LAMBDA_ARN="arn:aws:lambda:us-east-1:123456789012:function:cloudfront-viewer-request:$VERSION"

# Add Lambda@Edge association to distribution (update distribution config)
# Add this to DefaultCacheBehavior or CacheBehaviors:
# "LambdaFunctionAssociations": {
#   "Quantity": 1,
#   "Items": [
#     {
#       "LambdaFunctionARN": "arn:aws:lambda:us-east-1:123456789012:function:cloudfront-viewer-request:1",
#       "EventType": "viewer-request",
#       "IncludeBody": false
#     }
#   ]
# }

# List Lambda@Edge replicas
aws lambda list-functions \
  --function-version ALL \
  --region us-east-1 \
  --query 'Functions[?starts_with(FunctionName, `us-east-1.cloudfront-viewer-request`)]'
```

### CloudFront Functions

```bash
# Create CloudFront Function
aws cloudfront create-function \
  --name my-viewer-request-function \
  --function-config Comment="Add security headers",Runtime=cloudfront-js-1.0 \
  --function-code fileb://function.js

# Example function.js
cat > function.js <<'EOF'
function handler(event) {
    var response = event.response;
    var headers = response.headers;
    
    // Add security headers
    headers['strict-transport-security'] = { value: 'max-age=31536000; includeSubdomains; preload'};
    headers['x-content-type-options'] = { value: 'nosniff'};
    headers['x-frame-options'] = {value: 'DENY'};
    headers['x-xss-protection'] = {value: '1; mode=block'};
    
    return response;
}
EOF

# Publish function
aws cloudfront publish-function \
  --name my-viewer-request-function \
  --if-match ETAGVALUE

# Test function
aws cloudfront test-function \
  --name my-viewer-request-function \
  --if-match ETAGVALUE \
  --event-object fileb://test-event.json

# Describe function
aws cloudfront describe-function \
  --name my-viewer-request-function

# Associate function with distribution (add to distribution config)
# "FunctionAssociations": {
#   "Quantity": 1,
#   "Items": [
#     {
#       "FunctionARN": "arn:aws:cloudfront::123456789012:function/my-viewer-request-function",
#       "EventType": "viewer-request"
#     }
#   ]
# }
```

### Access Logs Configuration

```bash
# Enable access logs (update distribution config)
cat > logging-config.json <<'EOF'
{
  "Enabled": true,
  "IncludeCookies": false,
  "Bucket": "my-cloudfront-logs.s3.amazonaws.com",
  "Prefix": "cloudfront/production/"
}
EOF

# Add Logging section to distribution config and update
aws cloudfront get-distribution-config --id E1234567890ABC > config.json

# Edit config.json to add Logging configuration
# Then update distribution
ETAG=$(aws cloudfront get-distribution-config --id E1234567890ABC --query 'ETag' --output text)
aws cloudfront update-distribution \
  --id E1234567890ABC \
  --distribution-config file://config.json \
  --if-match $ETAG
```

### Real-Time Logs

```bash
# Create real-time log config
aws cloudfront create-realtime-log-config \
  --name production-realtime-logs \
  --end-points file://endpoints.json \
  --fields timestamp c-ip cs-uri-stem sc-status cs-method cs-protocol cs-host cs-bytes time-taken x-edge-location x-edge-request-id \
  --sampling-rate 100

# Example endpoints.json for Kinesis Data Stream
cat > endpoints.json <<'EOF'
[
  {
    "StreamType": "Kinesis",
    "KinesisStreamConfig": {
      "RoleARN": "arn:aws:iam::123456789012:role/CloudFrontRealtimeLogRole",
      "StreamARN": "arn:aws:kinesis:us-east-1:123456789012:stream/cloudfront-logs"
    }
  }
]
EOF

# Get real-time log config
aws cloudfront get-realtime-log-config \
  --name production-realtime-logs

# Update real-time log config
aws cloudfront update-realtime-log-config \
  --name production-realtime-logs \
  --sampling-rate 50 \
  --end-points file://endpoints.json \
  --fields timestamp c-ip sc-status

# Delete real-time log config
aws cloudfront delete-realtime-log-config \
  --name production-realtime-logs
```

### Origin Request Policies

```bash
# Create origin request policy
aws cloudfront create-origin-request-policy \
  --origin-request-policy-config file://origin-request-policy.json

# Example origin-request-policy.json
cat > origin-request-policy.json <<'EOF'
{
  "Name": "CustomOriginRequestPolicy",
  "Comment": "Forward all headers except Host",
  "HeadersConfig": {
    "HeaderBehavior": "allExcept",
    "Headers": {
      "Quantity": 1,
      "Items": ["Host"]
    }
  },
  "CookiesConfig": {
    "CookieBehavior": "all"
  },
  "QueryStringsConfig": {
    "QueryStringBehavior": "all"
  }
}
EOF

# List origin request policies
aws cloudfront list-origin-request-policies

# Get origin request policy
aws cloudfront get-origin-request-policy \
  --id 12345678-1234-1234-1234-123456789012

# Delete origin request policy
aws cloudfront delete-origin-request-policy \
  --id 12345678-1234-1234-1234-123456789012 \
  --if-match ETAGVALUE
```

### Cache Policies

```bash
# Create cache policy
aws cloudfront create-cache-policy \
  --cache-policy-config file://cache-policy.json

# Example cache-policy.json
cat > cache-policy.json <<'EOF'
{
  "Name": "CustomCachePolicy",
  "Comment": "Cache policy for API responses",
  "DefaultTTL": 86400,
  "MaxTTL": 31536000,
  "MinTTL": 1,
  "ParametersInCacheKeyAndForwardedToOrigin": {
    "EnableAcceptEncodingGzip": true,
    "EnableAcceptEncodingBrotli": true,
    "HeadersConfig": {
      "HeaderBehavior": "whitelist",
      "Headers": {
        "Quantity": 2,
        "Items": ["Authorization", "CloudFront-Viewer-Country"]
      }
    },
    "CookiesConfig": {
      "CookieBehavior": "none"
    },
    "QueryStringsConfig": {
      "QueryStringBehavior": "whitelist",
      "QueryStrings": {
        "Quantity": 2,
        "Items": ["id", "category"]
      }
    }
  }
}
EOF

# List cache policies
aws cloudfront list-cache-policies

# Get cache policy
aws cloudfront get-cache-policy \
  --id 12345678-1234-1234-1234-123456789012

# Update cache policy
ETAG=$(aws cloudfront get-cache-policy --id 12345678-1234-1234-1234-123456789012 --query 'ETag' --output text)
aws cloudfront update-cache-policy \
  --id 12345678-1234-1234-1234-123456789012 \
  --cache-policy-config file://cache-policy.json \
  --if-match $ETAG

# Delete cache policy
aws cloudfront delete-cache-policy \
  --id 12345678-1234-1234-1234-123456789012 \
  --if-match $ETAG
```

### List and Describe Distributions

```bash
# List all distributions
aws cloudfront list-distributions

# List distributions with formatted output
aws cloudfront list-distributions \
  --query 'DistributionList.Items[*].[Id,DomainName,Status,Enabled]' \
  --output table

# Get distribution details
aws cloudfront get-distribution \
  --id E1234567890ABC

# Get distribution configuration
aws cloudfront get-distribution-config \
  --id E1234567890ABC
```

### Origin Access Control (OAC)

```bash
# Create Origin Access Control
aws cloudfront create-origin-access-control \
  --origin-access-control-config file://oac-config.json

# Example oac-config.json
cat > oac-config.json <<'EOF'
{
  "Name": "my-s3-oac",
  "Description": "OAC for S3 bucket access",
  "SigningProtocol": "sigv4",
  "SigningBehavior": "always",
  "OriginAccessControlOriginType": "s3"
}
EOF

# List Origin Access Controls
aws cloudfront list-origin-access-controls

# Get Origin Access Control
aws cloudfront get-origin-access-control \
  --id E1234567890ABC
```

### Delete Distribution

```bash
# Disable distribution first
aws cloudfront get-distribution-config --id E1234567890ABC > config.json
jq '.DistributionConfig.Enabled = false' config.json > disabled-config.json

ETAG=$(aws cloudfront get-distribution-config --id E1234567890ABC --query 'ETag' --output text)
aws cloudfront update-distribution \
  --id E1234567890ABC \
  --distribution-config file://disabled-config.json \
  --if-match $ETAG

# Wait for distribution to be disabled
aws cloudfront wait distribution-deployed --id E1234567890ABC

# Delete distribution
ETAG=$(aws cloudfront get-distribution --id E1234567890ABC --query 'ETag' --output text)
aws cloudfront delete-distribution \
  --id E1234567890ABC \
  --if-match $ETAG
```

### Monitoring with CloudWatch

```bash
# Get CloudFront metrics via CloudWatch
aws cloudwatch get-metric-statistics \
  --namespace AWS/CloudFront \
  --metric-name Requests \
  --dimensions Name=DistributionId,Value=E1234567890ABC \
  --start-time 2026-02-07T00:00:00Z \
  --end-time 2026-02-08T00:00:00Z \
  --period 3600 \
  --statistics Sum

# Get error rate
aws cloudwatch get-metric-statistics \
  --namespace AWS/CloudFront \
  --metric-name ErrorRate \
  --dimensions Name=DistributionId,Value=E1234567890ABC \
  --start-time 2026-02-07T00:00:00Z \
  --end-time 2026-02-08T00:00:00Z \
  --period 300 \
  --statistics Average

# Get bytes downloaded
aws cloudwatch get-metric-statistics \
  --namespace AWS/CloudFront \
  --metric-name BytesDownloaded \
  --dimensions Name=DistributionId,Value=E1234567890ABC \
  --start-time 2026-02-07T00:00:00Z \
  --end-time 2026-02-08T00:00:00Z \
  --period 3600 \
  --statistics Sum
```

---

## Best Practices

### Performance Best Practices
1. **Optimize Cache Hit Ratio**
   - Use consistent URLs
   - Implement proper versioning
   - Configure appropriate TTLs
   - Use query string and header forwarding judiciously

2. **Compression Configuration**
   - Enable automatic compression
   - Serve pre-compressed files from origin when possible
   - Configure appropriate MIME types

3. **HTTP/2 Optimization**
   - Enable HTTP/2 support
   - Optimize for multiplexing
   - Reduce connection overhead

### Security Best Practices
1. **Origin Protection**
   - Use Origin Access Control (OAC) for S3
   - Restrict direct access to origins
   - Configure security groups and NACLs

2. **SSL/TLS Configuration**
   - Use modern TLS versions (1.2+)
   - Implement HSTS headers
   - Configure appropriate cipher suites

3. **Access Control**
   - Implement signed URLs for sensitive content
   - Use WAF for application protection
   - Configure geo-restrictions as needed

### Cost Optimization Best Practices
1. **Price Class Selection**
   - Choose appropriate price class based on user distribution
   - Monitor usage patterns and adjust accordingly

2. **Caching Strategy**
   - Maximize cache hit ratios
   - Use Origin Shield for multiple distributions
   - Implement efficient invalidation strategies

3. **Monitoring and Analytics**
   - Use CloudWatch metrics for optimization
   - Analyze access logs for patterns
   - Implement cost allocation tags

### Operational Best Practices
1. **Deployment Strategy**
   - Use staging and production distributions
   - Implement blue-green deployments
   - Test configuration changes thoroughly

2. **Monitoring and Alerting**
   - Set up CloudWatch alarms for key metrics
   - Monitor error rates and latency
   - Implement real-time monitoring for critical applications

3. **Backup and Recovery**
   - Document distribution configurations
   - Implement infrastructure as code
   - Maintain backup origins and failover procedures

---

This guide covers the essential CloudFront concepts and configurations needed for the AWS Solutions Architect SAA-C03 certification. Focus on understanding the use cases, configuration options, and integration patterns with other AWS services.