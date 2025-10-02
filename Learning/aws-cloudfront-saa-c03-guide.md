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
14. [Best Practices](#best-practices)

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