# AWS WAF & Shield - SAA-C03 Certification Guide

## Table of Contents

1. [Introduction](#introduction)
2. [AWS WAF Overview](#aws-waf-overview)
3. [AWS Shield Overview](#aws-shield-overview)
4. [AWS WAF Deep Dive](#aws-waf-deep-dive)
5. [AWS Shield Deep Dive](#aws-shield-deep-dive)
6. [Integration with Other AWS Services](#integration-with-other-aws-services)
7. [Monitoring and Logging](#monitoring-and-logging)
8. [Security Best Practices](#security-best-practices)
9. [Common Use Cases and Architectures](#common-use-cases-and-architectures)
10. [Troubleshooting](#troubleshooting)
11. [SAA-C03 Exam Focus Areas](#saa-c03-exam-focus-areas)
12. [AWS CLI Commands Reference](#aws-cli-commands-reference)
13. [Practice Questions](#practice-questions)

---

## Introduction

AWS WAF (Web Application Firewall) and AWS Shield are critical security services for protecting web applications and infrastructure from various types of attacks. For the AWS Solutions Architect Associate (SAA-C03) certification, understanding these services is essential for designing secure, resilient architectures.

### Key Learning Objectives

- Understand the differences between AWS WAF and AWS Shield
- Learn how to configure and manage web ACLs, rules, and rule groups
- Master DDoS protection strategies and implementation
- Integrate WAF and Shield with other AWS services
- Implement monitoring and logging for security events
- Apply best practices for web application security
- Design cost-effective protection strategies

### Service Overview

**AWS WAF**: A web application firewall that helps protect web applications from common web exploits and bots that could affect application availability, compromise security, or consume excessive resources.

**AWS Shield**: A managed DDoS (Distributed Denial of Service) protection service that safeguards applications running on AWS against DDoS attacks.

---

## AWS WAF Overview

### What is AWS WAF?

AWS WAF is a web application firewall that lets you monitor HTTP and HTTPS requests forwarded to your web applications and control access to your content. It operates at the application layer (Layer 7) of the OSI model.

### Key Features

- **Real-time visibility**: Monitor web requests in real-time
- **Customizable rules**: Create custom rules to filter traffic
- **Managed rule groups**: Use pre-configured rule sets
- **Rate limiting**: Control request rates from specific sources
- **IP reputation lists**: Block traffic from known malicious IPs
- **Geo-blocking**: Restrict access based on geographic location
- **Bot control**: Identify and manage bot traffic

### Core Components

1. **Web ACL (Access Control List)**: Main configuration entity that contains rules
2. **Rules**: Define conditions for allowing, blocking, or counting requests
3. **Rule Groups**: Collections of rules that can be reused
4. **Conditions**: Specific criteria used in rules (IP addresses, strings, etc.)
5. **Actions**: What to do when a rule matches (ALLOW, BLOCK, COUNT)

### Supported AWS Services

- Amazon CloudFront
- Application Load Balancer (ALB)
- Amazon API Gateway
- AWS AppSync GraphQL APIs

---

## AWS Shield Overview

### What is AWS Shield?

AWS Shield is a managed DDoS protection service that provides always-on detection and automatic inline mitigations that minimize application downtime and latency.

### Shield Standard vs Shield Advanced

#### Shield Standard
- **Cost**: Free for all AWS customers
- **Protection**: Network layer (Layer 3) and transport layer (Layer 4) DDoS protection
- **Coverage**: Automatic protection for all AWS resources
- **Detection**: Automatic detection and mitigation of common DDoS attacks
- **Services**: CloudFront, Route 53, and ELB (Classic and Application)

#### Shield Advanced
- **Cost**: $3,000 per month per organization (with additional charges for data transfer)
- **Protection**: Enhanced DDoS protection for EC2, ELB, CloudFront, Route 53, and Global Accelerator
- **Features**:
  - 24/7 access to DDoS Response Team (DRT)
  - Advanced attack diagnostics
  - Cost protection against DDoS-related scaling charges
  - Integration with AWS WAF at no additional cost
  - Real-time attack notifications via Amazon SNS
  - Advanced attack analytics and reporting

### DDoS Protection Mechanisms

1. **Always-on detection**: Continuous monitoring of traffic patterns
2. **Inline mitigation**: Automatic mitigation without customer intervention
3. **Attack surface reduction**: Minimize exposed infrastructure
4. **Incident response**: 24/7 support team for advanced tier

---

## AWS WAF Deep Dive

### Web ACLs (Access Control Lists)

Web ACLs are the primary configuration entity in AWS WAF. They define the rules that determine whether to allow, block, or monitor web requests.

#### Web ACL Components
- **Default action**: Action to take for requests that don't match any rules
- **Rules**: Ordered list of rules evaluated sequentially
- **Capacity units**: Each rule consumes capacity units (WCU - Web ACL Capacity Units)
- **Scope**: CloudFront (global) or regional (ALB, API Gateway, AppSync)

#### Web ACL Configuration Steps
1. Choose scope (CloudFront or Regional)
2. Add rules and rule groups
3. Set default action
4. Configure CloudWatch metrics
5. Associate with AWS resources

### Rules and Rule Groups

#### Rule Types
1. **AWS Managed Rules**: Pre-configured rule groups maintained by AWS
2. **Your own rules**: Custom rules you create
3. **Marketplace rules**: Third-party rule groups from AWS Marketplace

#### Common AWS Managed Rule Groups
- **Core Rule Set (CRS)**: Basic OWASP protection
- **Known Bad Inputs**: Blocks requests with patterns associated with vulnerability exploitation
- **SQL Injection**: Protects against SQL injection attacks
- **Cross-Site Scripting (XSS)**: Blocks XSS attacks
- **IP Reputation**: Blocks requests from known malicious IP addresses
- **Amazon IP Reputation**: Amazon-maintained list of malicious IPs
- **Anonymous IP**: Blocks requests from anonymous proxies, VPNs, and Tor nodes

#### Rule Statements
Rules contain statements that define matching criteria:

1. **Geographic match**: Match requests based on country of origin
2. **IP set match**: Match against a set of IP addresses or CIDR blocks
3. **Label match**: Match based on labels applied by other rules
4. **Regex pattern set match**: Match against regular expression patterns
5. **Rule group reference**: Reference to managed or custom rule groups
6. **Size constraint**: Match based on request size
7. **SQLi match**: Detect SQL injection attempts
8. **String match**: Match specific strings in requests
9. **XSS match**: Detect cross-site scripting attempts

#### Rule Actions
- **Allow**: Permit the request to continue
- **Block**: Block the request and return HTTP 403
- **Count**: Count the matching requests but don't affect processing
- **CAPTCHA**: Challenge the request with CAPTCHA
- **Challenge**: Challenge with JavaScript validation

### Rate-Based Rules

Rate-based rules track the rate of requests from individual IP addresses and can automatically block IPs that exceed specified thresholds.

#### Configuration Parameters
- **Rate limit**: Number of requests per 5-minute period
- **Scope of rate limit**: IP address aggregation method
- **Action**: What to do when threshold is exceeded
- **Duration**: How long to block the IP

#### Use Cases for Rate-Based Rules
- DDoS mitigation
- Brute force attack prevention
- API rate limiting
- Bot traffic management

### Custom Rule Creation

#### String Matching Example
```json
{
  "Name": "BlockSQLInjection",
  "Statement": {
    "ByteMatchStatement": {
      "FieldToMatch": {
        "Body": {}
      },
      "PositionalConstraint": "CONTAINS",
      "SearchString": "union select",
      "TextTransformations": [
        {
          "Priority": 0,
          "Type": "LOWERCASE"
        }
      ]
    }
  },
  "Action": {
    "Block": {}
  }
}
```

#### Geographic Blocking Example
```json
{
  "Name": "BlockSpecificCountries",
  "Statement": {
    "GeoMatchStatement": {
      "CountryCodes": ["CN", "RU", "KP"]
    }
  },
  "Action": {
    "Block": {}
  }
}
```

### Field to Match Options

WAF can inspect various parts of web requests:

1. **HTTP method**: GET, POST, PUT, etc.
2. **URI path**: The path portion of the URL
3. **Query string**: URL parameters
4. **Headers**: HTTP headers (including custom headers)
5. **Body**: Request body content
6. **Cookies**: HTTP cookies
7. **Single header**: Specific header value
8. **Single query argument**: Specific query parameter

### Text Transformations

Text transformations normalize request data before evaluation:

- **NONE**: No transformation
- **COMPRESS_WHITE_SPACE**: Replace multiple whitespace characters with single space
- **HTML_ENTITY_DECODE**: Decode HTML entities
- **LOWERCASE**: Convert to lowercase
- **CMD_LINE**: Transform command line arguments
- **URL_DECODE**: URL decode the request
- **BASE64_DECODE**: Base64 decode
- **HEX_DECODE**: Hexadecimal decode
- **MD5**: Generate MD5 hash
- **REPLACE_COMMENTS**: Replace SQL comments with spaces
- **ESCAPE_SEQ_DECODE**: Decode escape sequences
- **SQL_HEX_DECODE**: Decode SQL hex data
- **CSS_DECODE**: Decode CSS escape sequences
- **JS_DECODE**: Decode JavaScript escape sequences
- **NORMALIZE_PATH**: Normalize URL paths
- **NORMALIZE_PATH_WIN**: Normalize Windows file paths
- **REMOVE_NULLS**: Remove null bytes
- **REPLACE_NULLS**: Replace null bytes with spaces
- **BASE64_DECODE_EXT**: Extended base64 decode
- **URL_DECODE_UNI**: Unicode-aware URL decode
- **UTF8_TO_UNICODE**: Convert UTF-8 to Unicode

---

## AWS Shield Deep Dive

### Shield Standard

Shield Standard is automatically enabled for all AWS customers at no additional charge and provides protection against the most common DDoS attacks.

#### Protection Capabilities
- **SYN/UDP floods**: Layer 3 and 4 protection
- **Reflection attacks**: DNS, NTP, SSDP, etc.
- **HTTP flood protection**: Basic application layer protection
- **Automatic mitigation**: No configuration required
- **Always-on monitoring**: 24/7 detection and mitigation

#### Covered Services
- **Amazon CloudFront**: Global edge locations
- **Amazon Route 53**: DNS service
- **Elastic Load Balancing**: Classic and Application Load Balancers
- **AWS Global Accelerator**: Network optimization service

### Shield Advanced

Shield Advanced provides enhanced DDoS protection and additional features for mission-critical applications.

#### Enhanced Protection Features

1. **Expanded DDoS Protection**
   - EC2 instances
   - Network Load Balancers
   - CloudFront distributions
   - Route 53 hosted zones
   - Global Accelerator accelerators

2. **DDoS Response Team (DRT) Access**
   - 24/7 access to AWS experts
   - Incident response support
   - Attack analysis and mitigation guidance
   - Proactive engagement during attacks

3. **Advanced Attack Diagnostics**
   - Real-time attack notifications
   - Detailed attack reports
   - Attack vector analysis
   - Traffic pattern insights

4. **Cost Protection**
   - Protection against DDoS-related scaling charges
   - Covers EC2, ELB, CloudFront, Route 53, and Global Accelerator
   - Request credits for scaling costs during attacks

5. **Global Threat Environment Dashboard**
   - Near real-time threat landscape visibility
   - Attack trends and statistics
   - Threat intelligence reports

#### Shield Advanced Configuration

1. **Subscribe to Shield Advanced**
   - Enable at the account level
   - $3,000/month commitment
   - 1-year minimum commitment

2. **Configure Protected Resources**
   - Select resources to protect
   - Configure health checks
   - Set up proactive monitoring

3. **Configure DRT Access (Optional)**
   - Grant DRT access to WAF and Shield
   - Provide contact information
   - Set escalation procedures

### DDoS Attack Types and Mitigations

#### Layer 3/4 Attacks (Network/Transport)
- **SYN Flood**: Overwhelm server with SYN requests
- **UDP Flood**: Send large volumes of UDP packets
- **ICMP Flood**: Flood with ICMP packets
- **Mitigation**: Shield Standard/Advanced automatic filtering

#### Layer 7 Attacks (Application)
- **HTTP Flood**: Overwhelm with HTTP requests
- **Slowloris**: Slow HTTP attacks
- **DNS Query Flood**: Overwhelm DNS servers
- **Mitigation**: WAF rules, Shield Advanced, CloudFront

#### Reflection/Amplification Attacks
- **DNS Amplification**: Use DNS servers to amplify attack traffic
- **NTP Amplification**: Exploit NTP servers
- **SSDP Amplification**: Exploit UPnP devices
- **Mitigation**: Shield's automatic detection and filtering

### Shield Advanced Integration with WAF

Shield Advanced includes AWS WAF at no additional cost, enabling:
- Custom application-layer protection rules
- Rate-based rule integration
- Enhanced bot detection and mitigation
- Geo-blocking capabilities
- Custom response actions

#### Integration Benefits
1. **Layered Defense**: Network + application layer protection
2. **Automated Response**: DRT can configure WAF rules during attacks
3. **Cost Optimization**: WAF included with Shield Advanced
4. **Enhanced Visibility**: Combined metrics and logging

### Health-Based Detection

Shield Advanced can use Route 53 health checks to detect attacks:
- **Health Check Configuration**: Monitor application availability
- **Automatic Mitigation**: Trigger additional protections when health checks fail
- **Proactive Monitoring**: DRT notification when health degrades
- **Custom Thresholds**: Configure sensitivity levels

### Cost Protection Details

Shield Advanced provides cost protection for:
- **EC2 Auto Scaling**: Scaling due to DDoS attacks
- **ELB Scaling**: Load balancer capacity increases
- **CloudFront Data Transfer**: Increased data transfer costs
- **Route 53 Queries**: DNS query volume increases
- **Global Accelerator**: Data transfer and processing costs

#### Cost Protection Process
1. **Attack Detection**: Shield identifies DDoS attack
2. **Cost Monitoring**: AWS tracks scaling costs during attack
3. **Claim Submission**: Customer submits cost protection claim
4. **Credit Processing**: AWS provides credits for eligible charges

---

## Integration with Other AWS Services

### CloudFront Integration

AWS WAF and Shield integrate seamlessly with Amazon CloudFront for global protection.

#### CloudFront + WAF Benefits
- **Global distribution**: WAF rules applied at edge locations worldwide
- **Reduced latency**: Traffic filtering at the edge
- **Origin protection**: Shield web servers from direct attacks
- **Cost optimization**: Reduce origin server load
- **Enhanced caching**: Cache responses for allowed traffic

#### Configuration Steps
1. Create CloudFront distribution
2. Create WAF Web ACL (CloudFront scope)
3. Associate Web ACL with CloudFront distribution
4. Configure Shield Advanced protection (optional)

#### Edge Security Features
- **Custom error pages**: Display custom pages for blocked requests
- **Geographic restrictions**: CloudFront geo-blocking
- **SSL/TLS termination**: HTTPS enforcement
- **Request/response transformation**: Modify headers and content

### Application Load Balancer (ALB) Integration

ALB integration provides regional application-layer protection.

#### ALB + WAF Capabilities
- **Regional protection**: Protect applications within specific AWS regions
- **Layer 7 routing**: Combine with ALB routing rules
- **WebSocket support**: Protect WebSocket connections
- **HTTP/2 support**: Modern protocol support
- **Target group protection**: Protect backend services

#### Architecture Patterns
1. **Internet-facing ALB**: Direct internet traffic protection
2. **Internal ALB**: Protect internal services from other VPCs
3. **Multi-tier architecture**: Combine with CloudFront for layered protection

### API Gateway Integration

Protect REST and HTTP APIs with WAF integration.

#### API Gateway + WAF Features
- **API-specific rules**: Protect against API-focused attacks
- **Throttling integration**: Combine with API Gateway throttling
- **Authentication support**: Work with API Gateway auth mechanisms
- **Regional deployment**: Protect regional API endpoints

#### Common API Protection Patterns
- **Rate limiting**: Prevent API abuse
- **Payload validation**: Inspect request/response bodies
- **IP allowlisting**: Restrict API access by IP
- **Bot detection**: Identify automated API consumers

### AWS AppSync Integration

GraphQL API protection through WAF integration.

#### AppSync-Specific Protections
- **GraphQL query complexity**: Protect against complex queries
- **Introspection blocking**: Disable schema introspection
- **Depth limiting**: Prevent deeply nested queries
- **Field-level security**: Protect specific GraphQL fields

### Lambda@Edge Integration

Combine WAF with Lambda@Edge for advanced request processing.

#### Use Cases
- **Custom authentication**: Implement custom auth logic
- **Request transformation**: Modify requests before WAF evaluation
- **Dynamic rule generation**: Create rules based on request characteristics
- **Advanced bot detection**: Implement sophisticated bot detection algorithms

### Integration with AWS Config

Monitor WAF and Shield configuration compliance.

#### Config Rules for WAF/Shield
- **WAF Web ACL association**: Ensure resources are protected
- **Shield Advanced subscription**: Verify subscription status
- **Rule group usage**: Monitor managed rule group adoption
- **Configuration drift**: Detect unauthorized changes

### AWS Systems Manager Integration

Automate WAF and Shield management tasks.

#### Automation Opportunities
- **Rule deployment**: Automated rule updates across environments
- **Incident response**: Automated response to security events
- **Configuration management**: Standardized configurations
- **Compliance reporting**: Automated compliance checks

---

## Monitoring and Logging

### CloudWatch Metrics

AWS WAF and Shield provide comprehensive CloudWatch metrics for monitoring.

#### WAF Metrics
- **AllowedRequests**: Number of allowed requests
- **BlockedRequests**: Number of blocked requests
- **CountedRequests**: Number of counted requests (COUNT action)
- **PassedRequests**: Requests that passed through without rule matches
- **CaptchaRequests**: Requests challenged with CAPTCHA
- **ChallengeRequests**: Requests challenged with JavaScript

#### Shield Metrics
- **DDoSDetected**: Binary metric indicating DDoS attack detection
- **DDoSAttackBitsPerSecond**: Attack volume in bits per second
- **DDoSAttackPacketsPerSecond**: Attack volume in packets per second
- **DDoSAttackRequestsPerSecond**: Application layer attack requests per second

#### Custom CloudWatch Dashboards
Create dashboards to visualize:
- Traffic patterns and blocked requests
- Attack detection and mitigation status
- Performance impact during attacks
- Geographic distribution of traffic

### WAF Logging

WAF provides detailed request logs for security analysis and compliance.

#### Log Destinations
1. **Amazon S3**: Long-term storage and analysis
2. **CloudWatch Logs**: Real-time monitoring and alerting
3. **Amazon Kinesis Data Firehose**: Stream processing and analytics

#### Log Content
- **Request details**: Headers, URI, method, body
- **Rule evaluation**: Which rules matched, actions taken
- **Geographic information**: Country and region data
- **Timestamps**: Request and response timing
- **Client information**: IP address, user agent

#### Log Configuration Example
```json
{
  "LogDestinationConfigs": [
    "arn:aws:s3:::waf-logs-bucket/waf-logs/",
    "arn:aws:logs:us-east-1:123456789012:log-group:waf-log-group"
  ],
  "RedactedFields": [
    {
      "SingleHeader": {
        "Name": "authorization"
      }
    }
  ],
  "ManagedByFirewallManager": false
}
```

### Real-time Monitoring

Set up real-time monitoring and alerting for security events.

#### CloudWatch Alarms
1. **High Block Rate Alarm**: Alert on unusual blocking activity
2. **DDoS Attack Alarm**: Immediate notification of attacks
3. **Error Rate Spike**: Monitor for application errors during attacks
4. **Geographic Anomaly**: Alert on traffic from unexpected regions

#### SNS Integration
- **Attack notifications**: Real-time DDoS attack alerts
- **Configuration changes**: Notify on WAF rule modifications
- **Health check failures**: Alert on protected resource health issues
- **Cost protection triggers**: Notify when cost protection activates

### AWS CloudTrail Integration

Monitor WAF and Shield API calls and configuration changes.

#### Auditable Events
- WAF Web ACL creation, modification, deletion
- Rule and rule group changes
- Shield Advanced subscription changes
- Resource association/disassociation
- DRT access grants and modifications

#### Compliance and Governance
- **Change tracking**: Audit all configuration modifications
- **Access monitoring**: Track who made changes and when
- **Compliance reporting**: Generate compliance reports
- **Forensic analysis**: Investigate security incidents

---

## Security Best Practices

### WAF Configuration Best Practices

#### 1. Defense in Depth
- **Layer multiple protections**: Combine WAF, Shield, and CloudFront
- **Network and application layers**: Protect at multiple OSI layers
- **Regional and global**: Use both regional and global WAF deployments
- **Backup mitigations**: Have alternative protection mechanisms

#### 2. Rule Management
- **Start with managed rules**: Use AWS managed rule groups as foundation
- **Custom rules for specific threats**: Add rules for application-specific attacks
- **Regular updates**: Keep managed rules updated
- **Rule testing**: Test rules in COUNT mode before blocking
- **Capacity management**: Monitor and optimize WCU usage

#### 3. Rate Limiting Strategy
- **Appropriate thresholds**: Set realistic rate limits
- **Granular controls**: Different limits for different endpoints
- **Legitimate user consideration**: Avoid blocking normal users
- **Dynamic adjustment**: Adjust limits based on traffic patterns

#### 4. Monitoring and Alerting
- **Comprehensive logging**: Enable full request logging
- **Real-time alerts**: Set up immediate notifications for attacks
- **Regular analysis**: Review logs and metrics regularly
- **Trend monitoring**: Watch for evolving attack patterns

### Shield Configuration Best Practices

#### 1. Shield Standard Optimization
- **Use supported services**: Leverage CloudFront, Route 53, ELB
- **Proper architecture**: Design for DDoS resilience
- **Health monitoring**: Implement robust health checks
- **Capacity planning**: Ensure adequate resource capacity

#### 2. Shield Advanced Implementation
- **Cost-benefit analysis**: Evaluate ROI for your use case
- **Resource coverage**: Protect all critical resources
- **DRT preparation**: Prepare for DRT engagement
- **Health check configuration**: Set up comprehensive monitoring

#### 3. Incident Response Preparation
- **Response procedures**: Document incident response steps
- **Contact information**: Keep DRT contact info updated
- **Escalation paths**: Define clear escalation procedures
- **Communication plans**: Prepare stakeholder communication

### Operational Security

#### 1. Access Control
- **IAM policies**: Use least privilege for WAF/Shield access
- **Cross-account access**: Secure multi-account deployments
- **Service-linked roles**: Use appropriate service roles
- **Regular access reviews**: Audit access permissions

#### 2. Configuration Management
- **Infrastructure as Code**: Use CloudFormation/Terraform
- **Version control**: Track configuration changes
- **Environment consistency**: Maintain consistent configurations
- **Automated deployment**: Use CI/CD for rule deployment

#### 3. Testing and Validation
- **Penetration testing**: Regular security testing
- **Load testing**: Validate performance under load
- **Failover testing**: Test backup protection mechanisms
- **Rule validation**: Verify rule effectiveness

### Cost Optimization

#### 1. WAF Cost Management
- **Optimize WCU usage**: Efficient rule design
- **Request sampling**: Use sampling for analysis
- **Rule group reuse**: Share rule groups across Web ACLs
- **Regular review**: Remove unused rules and conditions

#### 2. Shield Advanced ROI
- **Risk assessment**: Evaluate DDoS risk profile
- **Cost protection value**: Calculate potential savings
- **Alternative solutions**: Compare with third-party options
- **Usage optimization**: Maximize included WAF usage

#### 3. Logging Cost Control
- **Log retention policies**: Set appropriate retention periods
- **Selective logging**: Log only necessary information
- **Storage optimization**: Use appropriate storage classes
- **Analysis tools**: Use cost-effective analysis solutions

---

## Common Use Cases and Architectures

### E-commerce Website Protection

#### Architecture Components
- **CloudFront**: Global content delivery with edge security
- **WAF**: Application-layer protection for dynamic content
- **Shield Advanced**: Enhanced DDoS protection for high-value target
- **ALB**: Regional load balancing with WAF integration
- **Auto Scaling**: Automatic scaling during traffic spikes

#### Protection Strategy
1. **Global Layer**: CloudFront + WAF for global traffic filtering
2. **Regional Layer**: ALB + WAF for application-specific rules
3. **DDoS Protection**: Shield Advanced with DRT access
4. **Rate Limiting**: Protect against scraping and abuse
5. **Bot Management**: Distinguish between good and bad bots

### API Protection Architecture

#### Multi-layered API Security
- **API Gateway**: Managed API service with throttling
- **WAF**: Custom rules for API-specific attacks
- **Cognito**: Authentication and authorization
- **Lambda**: Custom validation and processing

#### API-Specific Rules
```json
{
  "Name": "ProtectAPIEndpoints",
  "Rules": [
    {
      "Name": "RateLimitAPI",
      "Statement": {
        "RateBasedStatement": {
          "Limit": 1000,
          "AggregateKeyType": "IP"
        }
      },
      "Action": {
        "Block": {}
      }
    },
    {
      "Name": "ValidateAPIKey",
      "Statement": {
        "ByteMatchStatement": {
          "FieldToMatch": {
            "SingleHeader": {
              "Name": "x-api-key"
            }
          },
          "PositionalConstraint": "EXACTLY",
          "SearchString": "",
          "TextTransformations": []
        }
      },
      "Action": {
        "Block": {}
      }
    }
  ]
}
```

### Content Delivery Network (CDN) Security

#### CloudFront Security Configuration
- **Origin Access Control**: Restrict direct access to origins
- **Custom Headers**: Add security headers at edge
- **Geographic Restrictions**: Country-level blocking
- **SSL/TLS Configuration**: Enforce HTTPS

#### Edge Security Features
1. **WAF at Edge**: Filter requests before reaching origin
2. **Bot Detection**: Identify and manage bot traffic
3. **DDoS Mitigation**: Absorb attacks at edge locations
4. **Cache Optimization**: Reduce origin load

### Multi-Region Application Protection

#### Architecture Design
- **Global Accelerator**: Intelligent traffic routing
- **Regional WAFs**: Localized protection rules
- **Cross-Region Shield**: Consistent DDoS protection
- **Route 53**: DNS failover and health checks

#### Failover Strategy
1. **Primary Region**: Full WAF and Shield protection
2. **Secondary Region**: Standby with basic protection
3. **Automatic Failover**: Route 53 health check triggers
4. **Consistent Rules**: Synchronized WAF configurations

### Microservices Security

#### Service Mesh Integration
- **ALB per Service**: Granular protection per microservice
- **Service-Specific Rules**: Tailored WAF rules per service
- **Internal Communication**: Protect inter-service communication
- **API Gateway**: Centralized API management and security

#### Container Security
- **ECS/EKS Integration**: Protect containerized applications
- **Service Discovery**: Dynamic service registration
- **Load Balancer Target Groups**: Service-specific protection
- **Health Monitoring**: Container health integration

---

## Troubleshooting

### Common WAF Issues

#### 1. False Positives
**Problem**: Legitimate traffic being blocked by WAF rules
**Symptoms**:
- Users reporting access issues
- Increased blocked request metrics
- Customer complaints about functionality

**Troubleshooting Steps**:
1. Enable WAF logging if not already enabled
2. Analyze logs to identify blocked legitimate requests
3. Review rule configurations and thresholds
4. Use COUNT mode to test rule modifications
5. Implement IP allowlists for known good sources
6. Adjust string matching patterns and transformations

**Resolution**:
- Modify overly restrictive rules
- Add exception conditions for legitimate patterns
- Fine-tune rate limiting thresholds
- Implement CAPTCHA instead of blocking for borderline cases

#### 2. Performance Impact
**Problem**: WAF causing latency or throughput issues
**Symptoms**:
- Increased response times
- CloudWatch metrics showing delays
- User experience degradation

**Troubleshooting Steps**:
1. Monitor CloudWatch metrics for WAF processing time
2. Review rule complexity and WCU usage
3. Analyze rule evaluation order and optimization
4. Check for inefficient regular expressions
5. Monitor origin server performance

**Resolution**:
- Optimize rule order (most specific first)
- Simplify complex regular expressions
- Reduce unnecessary text transformations
- Use managed rule groups where possible
- Consider rule group size limits

#### 3. Configuration Drift
**Problem**: WAF configurations not matching expected settings
**Symptoms**:
- Unexpected blocking behavior
- Rules not triggering as expected
- Compliance violations

**Troubleshooting Steps**:
1. Compare current configuration with baseline
2. Review CloudTrail logs for recent changes
3. Validate rule syntax and conditions
4. Check resource associations
5. Verify IAM permissions

**Resolution**:
- Restore from known good configuration
- Implement infrastructure as code
- Set up configuration monitoring
- Establish change control processes

### Common Shield Issues

#### 1. DDoS Attack Response
**Problem**: Application experiencing DDoS attack
**Symptoms**:
- Unusual traffic patterns
- Application performance degradation
- Shield metrics showing attack indicators

**Immediate Response**:
1. Verify Shield protection is active
2. Check CloudWatch metrics for attack confirmation
3. Contact DRT if Shield Advanced subscriber
4. Enable additional WAF rules if needed
5. Scale infrastructure if possible

**Investigation Steps**:
1. Analyze traffic patterns in logs
2. Identify attack vectors and sources
3. Review Shield Advanced dashboard
4. Examine health check status
5. Assess cost protection eligibility

#### 2. False Attack Detection
**Problem**: Shield detecting normal traffic as DDoS
**Symptoms**:
- DDoS metrics triggering unexpectedly
- Normal traffic patterns flagged as attacks
- Unnecessary DRT engagement

**Troubleshooting**:
1. Analyze traffic patterns during "attack" periods
2. Review application behavior and user patterns
3. Check for legitimate traffic spikes (marketing campaigns, etc.)
4. Validate health check configurations
5. Review historical traffic patterns

**Resolution**:
- Adjust health check thresholds
- Improve baseline traffic understanding
- Work with DRT to refine detection
- Document legitimate traffic patterns

### Integration Issues

#### 1. CloudFront Association Problems
**Problem**: WAF Web ACL not properly associated with CloudFront
**Symptoms**:
- Rules not being applied to CloudFront traffic
- Metrics not reflecting expected traffic
- Association showing as failed

**Troubleshooting**:
1. Verify Web ACL scope (must be CloudFront/Global)
2. Check CloudFront distribution settings
3. Validate IAM permissions for association
4. Review Web ACL capacity limits
5. Check for conflicting configurations

#### 2. ALB Integration Issues
**Problem**: WAF not working with Application Load Balancer
**Symptoms**:
- Traffic bypassing WAF rules
- ALB access logs not showing WAF actions
- Regional Web ACL not filtering traffic

**Troubleshooting**:
1. Verify Web ACL scope (must be Regional)
2. Check ALB listener configurations
3. Validate rule conditions for HTTP/HTTPS traffic
4. Review target group health
5. Examine ALB access logs for WAF headers

### Monitoring and Alerting Issues

#### 1. Missing Metrics
**Problem**: Expected CloudWatch metrics not appearing
**Symptoms**:
- Dashboards showing no data
- Alarms not triggering
- Incomplete monitoring coverage

**Resolution**:
1. Verify metric configuration in Web ACL
2. Check CloudWatch metric filters
3. Validate IAM permissions for metrics
4. Ensure traffic is flowing through protected resources
5. Review metric retention settings

#### 2. Log Analysis Problems
**Problem**: WAF logs not providing useful information
**Symptoms**:
- Incomplete log entries
- Missing request details
- Difficulty analyzing attack patterns

**Resolution**:
1. Review log configuration and destinations
2. Check redacted fields settings
3. Validate log parsing and analysis tools
4. Ensure proper log retention policies
5. Implement structured log analysis

### Performance Optimization

#### 1. High WCU Usage
**Problem**: Approaching Web ACL capacity limits
**Symptoms**:
- Cannot add new rules
- Performance degradation
- Capacity warnings in console

**Optimization Steps**:
1. Audit current rules for efficiency
2. Combine similar conditions where possible
3. Remove unused or redundant rules
4. Use managed rule groups instead of custom rules
5. Optimize regular expressions

#### 2. Cost Management
**Problem**: Unexpected high costs for WAF and Shield
**Symptoms**:
- Higher than expected AWS bills
- Increasing request charges
- Shield Advanced not providing ROI

**Cost Optimization**:
1. Review request volumes and pricing tiers
2. Optimize logging configuration and retention
3. Analyze Shield Advanced cost protection benefits
4. Consider alternative protection strategies
5. Implement usage monitoring and budgets

---

## SAA-C03 Exam Focus Areas

### Key Exam Topics

#### 1. Security and Compliance (Domain 3: Design Secure Architectures)
- **DDoS Protection**: Understanding Shield Standard vs Advanced
- **Web Application Security**: WAF rules and configurations
- **Defense in Depth**: Layered security approaches
- **Compliance Requirements**: Meeting security standards
- **Cost Optimization**: Balancing security and cost

#### 2. High Availability and Fault Tolerance
- **DDoS Resilience**: Designing for attack scenarios
- **Geographic Distribution**: Global vs regional protection
- **Failover Mechanisms**: Backup protection strategies
- **Health Monitoring**: Detecting and responding to attacks

#### 3. Performance and Scalability
- **Edge Protection**: CloudFront integration benefits
- **Load Balancer Integration**: Regional protection strategies
- **Auto Scaling**: Scaling during attacks
- **Caching Strategies**: Reducing origin load

### Important Concepts for Exam

#### WAF Fundamentals
- **Web ACL**: Primary configuration entity
- **Rules vs Rule Groups**: Differences and use cases
- **Managed Rules**: AWS-provided protection
- **Custom Rules**: Application-specific protection
- **Rate-Based Rules**: DDoS and abuse prevention
- **Capacity Units (WCU)**: Resource limits and optimization

#### Shield Protection Levels
- **Standard Features**: Free protection included
- **Advanced Benefits**: Enhanced features and cost
- **DRT Access**: 24/7 expert support
- **Cost Protection**: DDoS-related scaling costs
- **Integration**: WAF included with Shield Advanced

#### Service Integration Patterns
- **CloudFront + WAF**: Global edge protection
- **ALB + WAF**: Regional application protection
- **API Gateway + WAF**: API-specific security
- **Route 53 Health Checks**: Attack detection and failover

### Common Exam Scenarios

#### Scenario 1: E-commerce DDoS Protection
**Requirement**: Protect high-traffic e-commerce site from DDoS attacks
**Solution Components**:
- CloudFront for global distribution
- WAF with managed rule groups
- Shield Advanced for enhanced protection
- ALB for regional load balancing
- Auto Scaling for capacity management

**Key Decision Points**:
- Shield Advanced ROI calculation
- WAF rule optimization
- Cost protection benefits
- Global vs regional deployment

#### Scenario 2: API Security Requirements
**Requirement**: Secure REST API against abuse and attacks
**Solution Components**:
- API Gateway for managed API hosting
- WAF with rate-based rules
- IP allowlisting for trusted clients
- Custom rules for API-specific threats

**Key Decision Points**:
- Rate limiting thresholds
- Authentication integration
- Regional vs global WAF
- Cost optimization strategies

#### Scenario 3: Multi-Region Application Protection
**Requirement**: Protect global application across multiple regions
**Solution Components**:
- Global Accelerator for intelligent routing
- Regional WAFs with synchronized rules
- Route 53 for DNS failover
- Shield protection across regions

**Key Decision Points**:
- Rule synchronization strategies
- Failover mechanisms
- Cost distribution across regions
- Monitoring and alerting setup

### Exam Tips and Strategies

#### 1. Service Selection Criteria
- **Free vs Paid**: Shield Standard is free, Advanced costs $3,000/month
- **Regional vs Global**: CloudFront (global) vs ALB/API Gateway (regional)
- **Protection Level**: Application layer (WAF) vs network layer (Shield)
- **Management Overhead**: Managed rules vs custom configuration

#### 2. Cost Optimization Considerations
- **Shield Advanced ROI**: Calculate based on DDoS risk and potential costs
- **WAF Capacity Units**: Optimize rules to minimize WCU usage
- **Request Volume**: Understand pricing tiers and thresholds
- **Log Management**: Balance logging needs with storage costs

#### 3. Integration Best Practices
- **Layered Defense**: Combine multiple protection mechanisms
- **Performance Impact**: Consider latency implications
- **Monitoring Requirements**: Comprehensive visibility needs
- **Compliance Alignment**: Meet regulatory requirements

### Key Metrics and Monitoring

#### WAF Metrics to Monitor
- **AllowedRequests**: Baseline traffic patterns
- **BlockedRequests**: Security event detection
- **SampledRequests**: Detailed request analysis
- **CountedRequests**: Rule effectiveness testing

#### Shield Metrics to Monitor
- **DDoSDetected**: Attack detection status
- **DDoSAttackBitsPerSecond**: Attack magnitude
- **DDoSAttackPacketsPerSecond**: Attack characteristics
- **VolumetricAttackBitsPerSecond**: Volumetric attack metrics

#### Critical Alarms to Configure
- High block rate indicating active attacks
- DDoS detection triggering immediate response
- Health check failures during attacks
- Unusual geographic traffic patterns
- Cost protection thresholds exceeded

---

## AWS CLI Commands Reference

### 1. Create Web ACLs

#### Create Web ACL for CloudFront (Global)
```bash
# Create a Web ACL for CloudFront distribution
aws wafv2 create-web-acl \
  --name MyCloudFrontWebACL \
  --scope CLOUDFRONT \
  --region us-east-1 \
  --default-action Allow={} \
  --description "Web ACL for CloudFront distributions" \
  --tags Key=Environment,Value=Production Key=Application,Value=WebApp \
  --visibility-config SampledRequestsEnabled=true,CloudWatchMetricsEnabled=true,MetricName=MyCloudFrontWebACL

# Create Web ACL with rules
aws wafv2 create-web-acl \
  --name ProductionWebACL \
  --scope CLOUDFRONT \
  --region us-east-1 \
  --default-action Block={} \
  --description "Production Web ACL with managed rules" \
  --rules file://web-acl-rules.json \
  --visibility-config SampledRequestsEnabled=true,CloudWatchMetricsEnabled=true,MetricName=ProductionWebACL
```

#### Create Web ACL for Regional Resources (ALB/API Gateway)
```bash
# Create regional Web ACL for ALB
aws wafv2 create-web-acl \
  --name MyRegionalWebACL \
  --scope REGIONAL \
  --region us-east-1 \
  --default-action Allow={} \
  --description "Web ACL for Application Load Balancer" \
  --visibility-config SampledRequestsEnabled=true,CloudWatchMetricsEnabled=true,MetricName=MyRegionalWebACL

# Create Web ACL with custom response
aws wafv2 create-web-acl \
  --name APIGatewayACL \
  --scope REGIONAL \
  --region us-west-2 \
  --default-action Block={CustomResponse={ResponseCode=403,CustomResponseBodyKey=blocked}} \
  --custom-response-bodies blocked='{"ContentType":"APPLICATION_JSON","Content":"{\"error\":\"Access denied\"}"}' \
  --visibility-config SampledRequestsEnabled=true,CloudWatchMetricsEnabled=true,MetricName=APIGatewayACL
```

#### List and Describe Web ACLs
```bash
# List all Web ACLs (CloudFront)
aws wafv2 list-web-acls \
  --scope CLOUDFRONT \
  --region us-east-1

# List all Web ACLs (Regional)
aws wafv2 list-web-acls \
  --scope REGIONAL \
  --region us-east-1

# Get Web ACL details
aws wafv2 get-web-acl \
  --scope REGIONAL \
  --region us-east-1 \
  --id <web-acl-id> \
  --name MyRegionalWebACL
```

### 2. Create Rule Groups

#### Create Custom Rule Group
```bash
# Create a custom rule group
aws wafv2 create-rule-group \
  --name MyCustomRuleGroup \
  --scope REGIONAL \
  --region us-east-1 \
  --capacity 100 \
  --description "Custom rules for application protection" \
  --rules file://rule-group-rules.json \
  --visibility-config SampledRequestsEnabled=true,CloudWatchMetricsEnabled=true,MetricName=MyCustomRuleGroup

# Example rule group rules JSON file (rule-group-rules.json)
cat > rule-group-rules.json <<'EOF'
[
  {
    "Name": "BlockSQLInjection",
    "Priority": 1,
    "Statement": {
      "SqliMatchStatement": {
        "FieldToMatch": {
          "AllQueryArguments": {}
        },
        "TextTransformations": [
          {
            "Priority": 0,
            "Type": "URL_DECODE"
          }
        ]
      }
    },
    "Action": {
      "Block": {}
    },
    "VisibilityConfig": {
      "SampledRequestsEnabled": true,
      "CloudWatchMetricsEnabled": true,
      "MetricName": "BlockSQLInjection"
    }
  }
]
EOF
```

#### List and Manage Rule Groups
```bash
# List available rule groups
aws wafv2 list-rule-groups \
  --scope REGIONAL \
  --region us-east-1

# Get rule group details
aws wafv2 get-rule-group \
  --scope REGIONAL \
  --region us-east-1 \
  --id <rule-group-id> \
  --name MyCustomRuleGroup

# Update rule group
aws wafv2 update-rule-group \
  --scope REGIONAL \
  --region us-east-1 \
  --id <rule-group-id> \
  --name MyCustomRuleGroup \
  --lock-token <lock-token> \
  --rules file://updated-rules.json \
  --visibility-config SampledRequestsEnabled=true,CloudWatchMetricsEnabled=true,MetricName=MyCustomRuleGroup

# Delete rule group
aws wafv2 delete-rule-group \
  --scope REGIONAL \
  --region us-east-1 \
  --id <rule-group-id> \
  --name MyCustomRuleGroup \
  --lock-token <lock-token>
```

### 3. IP Sets

#### Create IP Set
```bash
# Create IPv4 IP set for blocking
aws wafv2 create-ip-set \
  --name BlockedIPsV4 \
  --scope REGIONAL \
  --region us-east-1 \
  --description "List of blocked IPv4 addresses" \
  --ip-address-version IPV4 \
  --addresses 203.0.113.0/24 198.51.100.0/24 192.0.2.44/32

# Create IPv6 IP set
aws wafv2 create-ip-set \
  --name BlockedIPsV6 \
  --scope REGIONAL \
  --region us-east-1 \
  --description "List of blocked IPv6 addresses" \
  --ip-address-version IPV6 \
  --addresses 2001:0db8:85a3::/48

# Create trusted IP set (allowlist)
aws wafv2 create-ip-set \
  --name TrustedIPs \
  --scope REGIONAL \
  --region us-east-1 \
  --description "Trusted IP addresses" \
  --ip-address-version IPV4 \
  --addresses 10.0.0.0/8 172.16.0.0/12
```

#### Update and Manage IP Sets
```bash
# List IP sets
aws wafv2 list-ip-sets \
  --scope REGIONAL \
  --region us-east-1

# Get IP set details
aws wafv2 get-ip-set \
  --scope REGIONAL \
  --region us-east-1 \
  --id <ip-set-id> \
  --name BlockedIPsV4

# Update IP set with new addresses
aws wafv2 update-ip-set \
  --scope REGIONAL \
  --region us-east-1 \
  --id <ip-set-id> \
  --name BlockedIPsV4 \
  --lock-token <lock-token> \
  --addresses 203.0.113.0/24 198.51.100.0/24 192.0.2.44/32 192.0.2.99/32

# Delete IP set
aws wafv2 delete-ip-set \
  --scope REGIONAL \
  --region us-east-1 \
  --id <ip-set-id> \
  --name BlockedIPsV4 \
  --lock-token <lock-token>
```

### 4. Regex Pattern Sets

#### Create Regex Pattern Set
```bash
# Create regex pattern set for blocking user agents
aws wafv2 create-regex-pattern-set \
  --name BadUserAgents \
  --scope REGIONAL \
  --region us-east-1 \
  --description "Patterns for malicious user agents" \
  --regular-expression-list '{"RegexString":"badbot"},{"RegexString":"scraper.*"},{"RegexString":".*crawler.*"}'

# Create regex pattern set for email validation
aws wafv2 create-regex-pattern-set \
  --name EmailPatterns \
  --scope REGIONAL \
  --region us-east-1 \
  --description "Email validation patterns" \
  --regular-expression-list '{"RegexString":"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"}'
```

#### Manage Regex Pattern Sets
```bash
# List regex pattern sets
aws wafv2 list-regex-pattern-sets \
  --scope REGIONAL \
  --region us-east-1

# Get regex pattern set details
aws wafv2 get-regex-pattern-set \
  --scope REGIONAL \
  --region us-east-1 \
  --id <regex-pattern-set-id> \
  --name BadUserAgents

# Update regex pattern set
aws wafv2 update-regex-pattern-set \
  --scope REGIONAL \
  --region us-east-1 \
  --id <regex-pattern-set-id> \
  --name BadUserAgents \
  --lock-token <lock-token> \
  --regular-expression-list '{"RegexString":"badbot"},{"RegexString":"scraper.*"},{"RegexString":".*crawler.*"},{"RegexString":"malicious.*"}'

# Delete regex pattern set
aws wafv2 delete-regex-pattern-set \
  --scope REGIONAL \
  --region us-east-1 \
  --id <regex-pattern-set-id> \
  --name BadUserAgents \
  --lock-token <lock-token>
```

### 5. Rate-Based Rules

#### Create Rate-Based Rule in Web ACL
```bash
# Create Web ACL with rate-based rule
cat > rate-based-rules.json <<'EOF'
[
  {
    "Name": "RateLimitRule",
    "Priority": 1,
    "Statement": {
      "RateBasedStatement": {
        "Limit": 2000,
        "AggregateKeyType": "IP"
      }
    },
    "Action": {
      "Block": {
        "CustomResponse": {
          "ResponseCode": 429,
          "CustomResponseBodyKey": "rate-limit-response"
        }
      }
    },
    "VisibilityConfig": {
      "SampledRequestsEnabled": true,
      "CloudWatchMetricsEnabled": true,
      "MetricName": "RateLimitRule"
    }
  }
]
EOF

aws wafv2 create-web-acl \
  --name RateLimitedWebACL \
  --scope REGIONAL \
  --region us-east-1 \
  --default-action Allow={} \
  --rules file://rate-based-rules.json \
  --visibility-config SampledRequestsEnabled=true,CloudWatchMetricsEnabled=true,MetricName=RateLimitedWebACL
```

#### Advanced Rate-Based Rule with Scope-Down Statement
```bash
# Rate limit only for specific URI path
cat > advanced-rate-rule.json <<'EOF'
[
  {
    "Name": "APIRateLimit",
    "Priority": 1,
    "Statement": {
      "RateBasedStatement": {
        "Limit": 100,
        "AggregateKeyType": "IP",
        "ScopeDownStatement": {
          "ByteMatchStatement": {
            "SearchString": "/api/",
            "FieldToMatch": {
              "UriPath": {}
            },
            "TextTransformations": [
              {
                "Priority": 0,
                "Type": "LOWERCASE"
              }
            ],
            "PositionalConstraint": "STARTS_WITH"
          }
        }
      }
    },
    "Action": {
      "Block": {}
    },
    "VisibilityConfig": {
      "SampledRequestsEnabled": true,
      "CloudWatchMetricsEnabled": true,
      "MetricName": "APIRateLimit"
    }
  }
]
EOF
```

### 6. Managed Rule Groups

#### List Available Managed Rule Groups
```bash
# List AWS managed rule groups
aws wafv2 list-available-managed-rule-groups \
  --scope REGIONAL \
  --region us-east-1

# List AWS managed rule groups for CloudFront
aws wafv2 list-available-managed-rule-groups \
  --scope CLOUDFRONT \
  --region us-east-1

# Describe managed rule group
aws wafv2 describe-managed-rule-group \
  --vendor-name AWS \
  --name AWSManagedRulesCommonRuleSet \
  --scope REGIONAL \
  --region us-east-1
```

#### Add Managed Rule Groups to Web ACL
```bash
# Create Web ACL with AWS managed rules
cat > managed-rules-config.json <<'EOF'
[
  {
    "Name": "AWSManagedRulesCommonRuleSet",
    "Priority": 0,
    "Statement": {
      "ManagedRuleGroupStatement": {
        "VendorName": "AWS",
        "Name": "AWSManagedRulesCommonRuleSet"
      }
    },
    "OverrideAction": {
      "None": {}
    },
    "VisibilityConfig": {
      "SampledRequestsEnabled": true,
      "CloudWatchMetricsEnabled": true,
      "MetricName": "AWSManagedRulesCommonRuleSet"
    }
  },
  {
    "Name": "AWSManagedRulesKnownBadInputsRuleSet",
    "Priority": 1,
    "Statement": {
      "ManagedRuleGroupStatement": {
        "VendorName": "AWS",
        "Name": "AWSManagedRulesKnownBadInputsRuleSet"
      }
    },
    "OverrideAction": {
      "None": {}
    },
    "VisibilityConfig": {
      "SampledRequestsEnabled": true,
      "CloudWatchMetricsEnabled": true,
      "MetricName": "AWSManagedRulesKnownBadInputsRuleSet"
    }
  },
  {
    "Name": "AWSManagedRulesSQLiRuleSet",
    "Priority": 2,
    "Statement": {
      "ManagedRuleGroupStatement": {
        "VendorName": "AWS",
        "Name": "AWSManagedRulesSQLiRuleSet"
      }
    },
    "OverrideAction": {
      "None": {}
    },
    "VisibilityConfig": {
      "SampledRequestsEnabled": true,
      "CloudWatchMetricsEnabled": true,
      "MetricName": "AWSManagedRulesSQLiRuleSet"
    }
  }
]
EOF

aws wafv2 create-web-acl \
  --name ManagedRulesWebACL \
  --scope REGIONAL \
  --region us-east-1 \
  --default-action Allow={} \
  --rules file://managed-rules-config.json \
  --visibility-config SampledRequestsEnabled=true,CloudWatchMetricsEnabled=true,MetricName=ManagedRulesWebACL
```

#### Managed Rule Groups with Exclusions
```bash
# Create managed rule with specific rule exclusions
cat > managed-rules-exclusions.json <<'EOF'
[
  {
    "Name": "AWSManagedRulesCommonRuleSet",
    "Priority": 0,
    "Statement": {
      "ManagedRuleGroupStatement": {
        "VendorName": "AWS",
        "Name": "AWSManagedRulesCommonRuleSet",
        "ExcludedRules": [
          {"Name": "SizeRestrictions_BODY"},
          {"Name": "GenericRFI_BODY"}
        ]
      }
    },
    "OverrideAction": {
      "None": {}
    },
    "VisibilityConfig": {
      "SampledRequestsEnabled": true,
      "CloudWatchMetricsEnabled": true,
      "MetricName": "AWSManagedRulesCommonRuleSet"
    }
  }
]
EOF
```

### 7. Associate Web ACL with Resources

#### Associate Web ACL with ALB
```bash
# Associate Web ACL with Application Load Balancer
aws wafv2 associate-web-acl \
  --web-acl-arn arn:aws:wafv2:us-east-1:123456789012:regional/webacl/MyWebACL/<id> \
  --resource-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/my-alb/<id>

# List resources associated with Web ACL
aws wafv2 list-resources-for-web-acl \
  --web-acl-arn arn:aws:wafv2:us-east-1:123456789012:regional/webacl/MyWebACL/<id>
```

#### Associate Web ACL with API Gateway
```bash
# Associate Web ACL with API Gateway REST API
aws wafv2 associate-web-acl \
  --web-acl-arn arn:aws:wafv2:us-east-1:123456789012:regional/webacl/MyWebACL/<id> \
  --resource-arn arn:aws:apigateway:us-east-1::/restapis/<api-id>/stages/<stage-name>

# Associate with API Gateway V2 (HTTP API)
aws wafv2 associate-web-acl \
  --web-acl-arn arn:aws:wafv2:us-east-1:123456789012:regional/webacl/MyWebACL/<id> \
  --resource-arn arn:aws:apigateway:us-east-1::/apis/<api-id>/stages/<stage-name>
```

#### Associate Web ACL with CloudFront
```bash
# Associate Web ACL with CloudFront distribution
aws wafv2 associate-web-acl \
  --web-acl-arn arn:aws:wafv2:us-east-1:123456789012:global/webacl/MyCloudFrontWebACL/<id> \
  --resource-arn arn:aws:cloudfront::123456789012:distribution/<distribution-id>

# Alternative: Update CloudFront distribution with Web ACL
aws cloudfront update-distribution \
  --id <distribution-id> \
  --if-match <etag> \
  --distribution-config file://distribution-config.json
# (Include WebACLId in the distribution-config.json)
```

#### Disassociate Web ACL
```bash
# Disassociate Web ACL from resource
aws wafv2 disassociate-web-acl \
  --resource-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/my-alb/<id>

# Get Web ACL for resource
aws wafv2 get-web-acl-for-resource \
  --resource-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/my-alb/<id>
```

### 8. Logging Configuration

#### Enable WAF Logging to S3
```bash
# Create S3 bucket for WAF logs
BUCKET_NAME="aws-waf-logs-my-app-$(date +%s)"
aws s3 mb s3://$BUCKET_NAME --region us-east-1

# Put logging configuration
aws wafv2 put-logging-configuration \
  --logging-configuration '{
    "ResourceArn": "arn:aws:wafv2:us-east-1:123456789012:regional/webacl/MyWebACL/<id>",
    "LogDestinationConfigs": [
      "arn:aws:s3:::'$BUCKET_NAME'"
    ]
  }'
```

#### Enable WAF Logging to CloudWatch Logs
```bash
# Create CloudWatch Logs log group
LOG_GROUP_NAME="aws-waf-logs-mywebacl"
aws logs create-log-group --log-group-name $LOG_GROUP_NAME

# Put logging configuration for CloudWatch
aws wafv2 put-logging-configuration \
  --logging-configuration '{
    "ResourceArn": "arn:aws:wafv2:us-east-1:123456789012:regional/webacl/MyWebACL/<id>",
    "LogDestinationConfigs": [
      "arn:aws:logs:us-east-1:123456789012:log-group:'$LOG_GROUP_NAME'"
    ]
  }'
```

#### Enable WAF Logging to Kinesis Data Firehose
```bash
# Put logging configuration for Kinesis Firehose
aws wafv2 put-logging-configuration \
  --logging-configuration '{
    "ResourceArn": "arn:aws:wafv2:us-east-1:123456789012:regional/webacl/MyWebACL/<id>",
    "LogDestinationConfigs": [
      "arn:aws:firehose:us-east-1:123456789012:deliverystream/aws-waf-logs-stream"
    ],
    "RedactedFields": [
      {"SingleHeader": {"Name": "authorization"}},
      {"SingleHeader": {"Name": "cookie"}}
    ],
    "LoggingFilter": {
      "DefaultBehavior": "KEEP",
      "Filters": [
        {
          "Behavior": "DROP",
          "Requirement": "MEETS_ALL",
          "Conditions": [
            {
              "ActionCondition": {
                "Action": "ALLOW"
              }
            }
          ]
        }
      ]
    }
  }'

# Get logging configuration
aws wafv2 get-logging-configuration \
  --resource-arn arn:aws:wafv2:us-east-1:123456789012:regional/webacl/MyWebACL/<id>

# Delete logging configuration
aws wafv2 delete-logging-configuration \
  --resource-arn arn:aws:wafv2:us-east-1:123456789012:regional/webacl/MyWebACL/<id>
```

### 9. Shield Advanced Protection

#### Subscribe to Shield Advanced
```bash
# Subscribe to Shield Advanced (creates subscription)
aws shield create-subscription

# Describe subscription
aws shield describe-subscription

# Get subscription state
aws shield get-subscription-state
```

#### Create Shield Advanced Protection
```bash
# Protect CloudFront distribution
aws shield create-protection \
  --name CloudFrontProtection \
  --resource-arn arn:aws:cloudfront::123456789012:distribution/<distribution-id>

# Protect Application Load Balancer
aws shield create-protection \
  --name ALBProtection \
  --resource-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/my-alb/<id>

# Protect Elastic IP
aws shield create-protection \
  --name EIPProtection \
  --resource-arn arn:aws:ec2:us-east-1:123456789012:eip-allocation/<allocation-id>

# Protect Route 53 hosted zone
aws shield create-protection \
  --name Route53Protection \
  --resource-arn arn:aws:route53:::hostedzone/<hosted-zone-id>

# Protect Global Accelerator
aws shield create-protection \
  --name GlobalAcceleratorProtection \
  --resource-arn arn:aws:globalaccelerator::123456789012:accelerator/<accelerator-id>
```

#### List and Describe Protections
```bash
# List all protections
aws shield list-protections

# Describe specific protection
aws shield describe-protection \
  --resource-arn arn:aws:cloudfront::123456789012:distribution/<distribution-id>

# Delete protection
aws shield delete-protection \
  --protection-id <protection-id>
```

#### Shield Protection Groups
```bash
# Create protection group
aws shield create-protection-group \
  --protection-group-id MyAppProtectionGroup \
  --aggregation MAX \
  --pattern ALL \
  --members \
    arn:aws:cloudfront::123456789012:distribution/<dist-id> \
    arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/my-alb/<id>

# Create protection group by resource type
aws shield create-protection-group \
  --protection-group-id ALBProtectionGroup \
  --aggregation SUM \
  --pattern BY_RESOURCE_TYPE \
  --resource-type APPLICATION_LOAD_BALANCER

# List protection groups
aws shield list-protection-groups

# Describe protection group
aws shield describe-protection-group \
  --protection-group-id MyAppProtectionGroup

# Update protection group
aws shield update-protection-group \
  --protection-group-id MyAppProtectionGroup \
  --aggregation MEAN \
  --pattern ALL

# Delete protection group
aws shield delete-protection-group \
  --protection-group-id MyAppProtectionGroup
```

#### Shield Advanced Attack Details
```bash
# List attacks
aws shield list-attacks \
  --start-time FromInclusive=2024-01-01T00:00:00Z \
  --end-time ToExclusive=2024-12-31T23:59:59Z

# List attacks for specific resource
aws shield list-attacks \
  --resource-arns arn:aws:cloudfront::123456789012:distribution/<distribution-id> \
  --start-time FromInclusive=2024-01-01T00:00:00Z \
  --end-time ToExclusive=2024-12-31T23:59:59Z

# Describe attack details
aws shield describe-attack \
  --attack-id <attack-id>

# Describe attack statistics
aws shield describe-attack-statistics
```

### 10. Shield DRT Access

#### Configure DRT Access
```bash
# Associate DRT log bucket
aws shield associate-drt-log-bucket \
  --log-bucket my-shield-logs-bucket

# List DRT log buckets
aws shield list-drt-log-buckets

# Disassociate DRT log bucket
aws shield disassociate-drt-log-bucket \
  --log-bucket my-shield-logs-bucket

# Associate DRT IAM role
aws shield associate-drt-role \
  --role-arn arn:aws:iam::123456789012:role/ShieldDRTAccessRole

# Describe DRT access
aws shield describe-drt-access

# Disassociate DRT role
aws shield disassociate-drt-role
```

#### Emergency Contacts
```bash
# Associate emergency contacts
aws shield associate-health-check \
  --protection-id <protection-id> \
  --health-check-arn arn:aws:route53:::healthcheck/<healthcheck-id>

# Update emergency contact information
aws shield update-emergency-contact-settings \
  --emergency-contact-list '[
    {
      "EmailAddress": "security@example.com",
      "ContactNotes": "Primary security contact",
      "PhoneNumber": "+1-555-0100"
    },
    {
      "EmailAddress": "ops@example.com",
      "ContactNotes": "Operations team",
      "PhoneNumber": "+1-555-0101"
    }
  ]'

# Describe emergency contact settings
aws shield describe-emergency-contact-settings
```

#### Shield Advanced Application Layer DDoS Configuration
```bash
# Enable application layer automatic response
aws shield enable-application-layer-automatic-response \
  --resource-arn arn:aws:cloudfront::123456789012:distribution/<distribution-id> \
  --action Block={}

# Update application layer automatic response
aws shield update-application-layer-automatic-response \
  --resource-arn arn:aws:cloudfront::123456789012:distribution/<distribution-id> \
  --action Count={}

# Describe application layer automatic response
aws shield describe-application-layer-automatic-response \
  --resource-arn arn:aws:cloudfront::123456789012:distribution/<distribution-id>

# Disable application layer automatic response
aws shield disable-application-layer-automatic-response \
  --resource-arn arn:aws:cloudfront::123456789012:distribution/<distribution-id>
```

### 11. Additional Useful Commands

#### Get Sampled Requests
```bash
# Get sampled requests for Web ACL
aws wafv2 get-sampled-requests \
  --web-acl-arn arn:aws:wafv2:us-east-1:123456789012:regional/webacl/MyWebACL/<id> \
  --rule-metric-name MyRuleMetric \
  --scope REGIONAL \
  --time-window StartTime=2024-01-01T00:00:00Z,EndTime=2024-01-01T23:59:59Z \
  --max-items 100
```

#### Check Capacity
```bash
# Check capacity usage for rule group
aws wafv2 check-capacity \
  --scope REGIONAL \
  --rules file://rules.json
```

#### Tags Management
```bash
# Tag Web ACL
aws wafv2 tag-resource \
  --resource-arn arn:aws:wafv2:us-east-1:123456789012:regional/webacl/MyWebACL/<id> \
  --tags Key=Environment,Value=Production Key=Application,Value=WebApp

# List tags
aws wafv2 list-tags-for-resource \
  --resource-arn arn:aws:wafv2:us-east-1:123456789012:regional/webacl/MyWebACL/<id>

# Untag resource
aws wafv2 untag-resource \
  --resource-arn arn:aws:wafv2:us-east-1:123456789012:regional/webacl/MyWebACL/<id> \
  --tag-keys Environment
```

---

## Practice Questions

### Question 1: Basic WAF Configuration
**Scenario**: A company wants to protect their web application hosted on an Application Load Balancer from SQL injection attacks and wants to monitor the effectiveness of their rules before implementing them.

**Question**: What is the BEST approach to test WAF rules before blocking traffic?

A) Deploy rules with BLOCK action and monitor CloudWatch metrics
B) Use COUNT action to monitor rule matches without blocking traffic
C) Deploy rules on a test environment first
D) Enable WAF logging and analyze blocked requests

**Answer**: B) Use COUNT action to monitor rule matches without blocking traffic

**Explanation**: The COUNT action allows you to monitor how many requests would match your rules without actually blocking legitimate traffic. This is the recommended approach for testing rule effectiveness before switching to BLOCK action.

### Question 2: Shield Advanced ROI
**Scenario**: An e-commerce company experiences seasonal traffic spikes and has been hit by DDoS attacks in the past, causing significant revenue loss. They're considering Shield Advanced but are concerned about the cost.

**Question**: Which factors should they consider when evaluating Shield Advanced? (Choose 3)

A) $3,000 monthly cost regardless of usage
B) Cost protection against DDoS-related scaling charges
C) 24/7 access to DDoS Response Team (DRT)
D) Automatic scaling of protected resources
E) Free WAF usage included with Shield Advanced
F) Guaranteed attack prevention

**Answers**: A, B, C, E

**Explanation**: Shield Advanced costs $3,000/month, provides cost protection for DDoS-related scaling, includes 24/7 DRT access, and includes WAF at no additional cost. It doesn't automatically scale resources or guarantee prevention of all attacks.

### Question 3: Global vs Regional Protection
**Scenario**: A company has a web application that serves customers globally and wants to implement WAF protection. They use CloudFront for content delivery and have ALBs in multiple regions.

**Question**: What is the MOST cost-effective approach to implement comprehensive WAF protection?

A) Create separate regional WAF Web ACLs for each ALB
B) Use CloudFront WAF only for global protection
C) Combine CloudFront WAF for global protection with regional WAF for origin protection
D) Use AWS Shield Advanced instead of WAF

**Answer**: C) Combine CloudFront WAF for global protection with regional WAF for origin protection

**Explanation**: This layered approach provides protection at the edge (CloudFront) for global threats and regional protection for any traffic that bypasses CloudFront or targets regional endpoints directly.

### Question 4: Rate-Based Rules
**Scenario**: An API receives legitimate traffic but also experiences bot attacks that make rapid sequential requests from single IP addresses.

**Question**: How should you configure a rate-based rule to protect against this attack while minimizing impact on legitimate users?

A) Set a low rate limit (100 requests/5 minutes) and block immediately
B) Set a reasonable rate limit (2000 requests/5 minutes) and use CAPTCHA action
C) Set a high rate limit (10000 requests/5 minutes) and use COUNT action
D) Use IP reputation lists instead of rate-based rules

**Answer**: B) Set a reasonable rate limit (2000 requests/5 minutes) and use CAPTCHA action

**Explanation**: A reasonable rate limit with CAPTCHA action allows legitimate users to continue accessing the API after solving a CAPTCHA while effectively blocking automated bot attacks.

### Question 5: Shield Cost Protection
**Scenario**: During a DDoS attack, a company's Auto Scaling groups scaled out significantly, incurring substantial EC2 costs. They have Shield Advanced subscription.

**Question**: What steps should they take to receive cost protection credits?

A) Contact AWS Support immediately during the attack
B) Submit a cost protection claim after the attack with evidence
C) File a claim within 30 days of the attack with supporting documentation
D) Both B and C are correct

**Answer**: D) Both B and C are correct

**Explanation**: Shield Advanced cost protection requires submitting a claim with evidence of the attack and its impact on scaling costs. Claims must be filed within a specific timeframe with proper documentation.

### Question 6: WAF Integration
**Scenario**: A company wants to protect both their static website hosted on CloudFront and their API hosted on API Gateway in the same region.

**Question**: What WAF configuration approach should they use?

A) Create one regional Web ACL for both services
B) Create one CloudFront Web ACL for both services
C) Create separate Web ACLs - one CloudFront scope and one regional scope
D) Use Shield Advanced instead of WAF for both services

**Answer**: C) Create separate Web ACLs - one CloudFront scope and one regional scope

**Explanation**: CloudFront requires a global-scoped Web ACL, while API Gateway requires a regional-scoped Web ACL. Different scopes cannot be shared between these service types.

### Question 7: Monitoring and Alerting
**Scenario**: A security team wants to be immediately notified when their WAF starts blocking an unusual number of requests, which might indicate an ongoing attack.

**Question**: What is the BEST approach to implement this alerting?

A) Set up CloudWatch alarm on BlockedRequests metric with SNS notification
B) Enable WAF logging and use CloudWatch Logs insights
C) Monitor AWS Personal Health Dashboard for DDoS notifications
D) Configure Shield Advanced DRT to contact them

**Answer**: A) Set up CloudWatch alarm on BlockedRequests metric with SNS notification

**Explanation**: CloudWatch alarms on WAF metrics provide real-time alerting capabilities. Setting an alarm on BlockedRequests with appropriate thresholds and SNS notification ensures immediate notification of potential attacks.

### Question 8: Rule Optimization
**Scenario**: A Web ACL is approaching its capacity limit (WCU), and the team needs to add more protection rules.

**Question**: Which approach would be MOST effective to optimize capacity usage?

A) Remove all custom rules and use only managed rule groups
B) Combine similar string match conditions into single rules with OR logic
C) Replace custom rules with more efficient managed rule groups where possible
D) Increase the Web ACL capacity limit

**Answer**: C) Replace custom rules with more efficient managed rule groups where possible

**Explanation**: Managed rule groups are optimized by AWS and typically use WCUs more efficiently than custom rules. This approach maintains protection while optimizing capacity usage.

---

## Conclusion

AWS WAF and Shield provide comprehensive protection against web application attacks and DDoS threats. For the SAA-C03 certification, understanding these services is crucial for designing secure, resilient architectures.

### Key Takeaways

1. **Layered Security**: Combine WAF and Shield for comprehensive protection
2. **Service Integration**: Understand how these services integrate with CloudFront, ALB, API Gateway, and other AWS services
3. **Cost Optimization**: Balance security needs with cost considerations
4. **Monitoring**: Implement comprehensive monitoring and alerting
5. **Best Practices**: Follow security best practices for configuration and management

### Exam Preparation Tips

- Focus on understanding service capabilities and limitations
- Practice scenario-based questions involving service selection
- Understand integration patterns and architectural decisions
- Know the differences between Shield Standard and Advanced
- Understand WAF rule types and configuration options
- Practice cost optimization scenarios

### Further Learning

- AWS WAF Developer Guide
- AWS Shield Advanced Guide
- AWS Security Best Practices
- AWS Well-Architected Security Pillar
- Hands-on practice with WAF and Shield configuration

This guide provides a comprehensive foundation for understanding AWS WAF and Shield in the context of the SAA-C03 certification. Regular practice and hands-on experience will help reinforce these concepts for exam success and real-world application.

---

*Last Updated: October 2025*
*Document Version: 1.0*