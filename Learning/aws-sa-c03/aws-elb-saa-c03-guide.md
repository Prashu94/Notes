# AWS Elastic Load Balancer (ELB) - SAA-C03 Certification Guide

## Table of Contents
1. [Overview](#overview)
2. [Types of Load Balancers](#types-of-load-balancers)
3. [Application Load Balancer (ALB)](#application-load-balancer-alb)
4. [Network Load Balancer (NLB)](#network-load-balancer-nlb)
5. [Classic Load Balancer (CLB)](#classic-load-balancer-clb)
6. [Gateway Load Balancer (GWLB)](#gateway-load-balancer-gwlb)
7. [Load Balancer Components](#load-balancer-components)
8. [Health Checks](#health-checks)
9. [Security Features](#security-features)
10. [Monitoring and Logging](#monitoring-and-logging)
11. [Best Practices](#best-practices)
12. [Common Use Cases](#common-use-cases)
13. [Exam Tips](#exam-tips)

## Overview

AWS Elastic Load Balancer (ELB) automatically distributes incoming application traffic across multiple targets, such as EC2 instances, containers, and IP addresses, across one or more Availability Zones.

### Key Benefits
- **High Availability**: Distributes traffic across multiple AZs
- **Auto Scaling**: Automatically scales to handle traffic changes
- **Security**: Integrates with AWS security services
- **Health Monitoring**: Performs health checks on targets
- **SSL Termination**: Handles SSL/TLS encryption and decryption

### Load Balancer Fundamentals
- **Listeners**: Check for connection requests using configured protocol and port
- **Target Groups**: Route requests to registered targets
- **Rules**: Determine how to route requests to targets
- **Health Checks**: Monitor target health and route traffic only to healthy targets

## Types of Load Balancers

AWS offers four types of load balancers, each designed for specific use cases:

| Feature | ALB | NLB | CLB | GWLB |
|---------|-----|-----|-----|------|
| **Layer** | 7 (Application) | 4 (Transport) | 4 & 7 | 3 (Network) |
| **Protocol** | HTTP, HTTPS, gRPC | TCP, UDP, TLS | TCP, SSL/TLS, HTTP, HTTPS | IP |
| **Target Types** | Instance, IP, Lambda | Instance, IP, ALB | Instance | Instance, IP |
| **Static IP** | No | Yes | No | No |
| **WebSocket** | Yes | Yes | Yes | No |
| **Path-based Routing** | Yes | No | No | No |
| **Host-based Routing** | Yes | No | No | No |

## Application Load Balancer (ALB)

### Overview
ALB operates at Layer 7 (Application layer) and is ideal for HTTP and HTTPS traffic with advanced routing capabilities.

### Key Features

#### Advanced Request Routing
- **Path-based routing**: Route based on URL path
- **Host-based routing**: Route based on hostname
- **Query string routing**: Route based on query parameters
- **Header-based routing**: Route based on HTTP headers
- **HTTP method routing**: Route based on request method

#### Target Types
1. **EC2 instances**
2. **IP addresses** (including on-premises servers)
3. **Lambda functions**
4. **Other ALBs** (for multi-region applications)

#### Security Features
- **WAF Integration**: Web Application Firewall protection
- **SSL Termination**: Handles SSL/TLS encryption
- **Security Groups**: Control traffic at instance level
- **Authentication**: Supports OIDC and SAML

#### Advanced Features
- **HTTP/2 and gRPC support**
- **WebSocket support**
- **Sticky sessions** (session affinity)
- **Request tracing** with X-Amzn-Trace-Id header
- **Slow start mode** for targets

### ALB Routing Rules

```yaml
# Example routing rules priority
Priority 1: Host header = "api.example.com" → API target group
Priority 2: Path = "/images/*" → Images target group  
Priority 3: Query string = "version=v2" → V2 target group
Priority 4: Default → Main target group
```

### ALB Use Cases
- **Microservices architecture**
- **Container-based applications**
- **Web applications requiring Layer 7 routing**
- **Applications needing SSL termination**
- **Lambda function integration**

## Network Load Balancer (NLB)

### Overview
NLB operates at Layer 4 (Transport layer) and is designed for ultra-high performance and low latency applications.

### Key Features

#### Performance Characteristics
- **Ultra-high performance**: Millions of requests per second
- **Low latency**: Sub-millisecond latency
- **Static IP addresses**: One per AZ
- **Elastic IP support**: Assign your own Elastic IPs

#### Protocol Support
- **TCP**: Transmission Control Protocol
- **UDP**: User Datagram Protocol  
- **TLS**: Transport Layer Security

#### Target Types
1. **EC2 instances**
2. **IP addresses** (including on-premises)
3. **Application Load Balancers**

#### Connection Handling
- **Connection multiplexing**: Not performed (each request = new connection)
- **Source IP preservation**: Client IP preserved to targets
- **Cross-zone load balancing**: Optional (disabled by default)

### NLB Features

#### Health Checks
- **TCP health checks**: Check if port is reachable
- **HTTP/HTTPS health checks**: More detailed health verification
- **Customizable intervals**: 10-300 seconds

#### Security
- **Security Groups**: Applied to targets, not NLB
- **TLS termination**: Supports SSL/TLS offloading
- **Client certificate validation**

### NLB Use Cases
- **High-performance applications**
- **Gaming applications**
- **IoT applications**
- **Static IP requirement**
- **Extreme performance requirements**
- **TCP/UDP load balancing**

## Classic Load Balancer (CLB)

### Overview
CLB is the legacy load balancer supporting both Layer 4 and Layer 7 features. AWS recommends migrating to ALB or NLB for new applications.

### Key Features
- **Dual-layer operation**: Layer 4 (TCP/SSL) and Layer 7 (HTTP/HTTPS)
- **Basic load balancing**: Round robin across instances
- **Health checks**: HTTP, HTTPS, TCP, SSL
- **SSL termination**: Basic SSL/TLS support
- **Sticky sessions**: Session affinity support

### Limitations
- **No advanced routing**: Path/host-based routing not supported
- **Single target group**: Cannot route to multiple target groups
- **Limited protocols**: HTTP, HTTPS, TCP, SSL only
- **No Lambda support**: Cannot target Lambda functions

### Migration Considerations
```yaml
CLB → ALB Migration:
  - Better for HTTP/HTTPS applications
  - Advanced routing capabilities
  - Support for Lambda targets
  - Better monitoring and metrics

CLB → NLB Migration:
  - Better for TCP/UDP applications
  - Ultra-high performance requirements
  - Static IP requirements
  - Source IP preservation needs
```

## Gateway Load Balancer (GWLB)

### Overview
GWLB operates at Layer 3 (Network layer) and is designed for deploying, scaling, and managing third-party network virtual appliances.

### Key Features

#### Network Virtual Appliances
- **Firewalls**
- **Intrusion Detection/Prevention Systems (IDS/IPS)**
- **Deep Packet Inspection systems**
- **Payload manipulation applications**

#### GENEVE Protocol
- **Encapsulation**: Uses GENEVE protocol on port 6081
- **Traffic flow**: Transparent to source and destination
- **Scaling**: Auto-scales virtual appliances

#### Target Types
- **EC2 instances** running network virtual appliances
- **IP addresses** of virtual appliances

### GWLB Architecture

```
Internet → IGW → GWLB Endpoint → GWLB → Virtual Appliances → GWLB → GWLB Endpoint → Application Subnets
```

### Use Cases
- **Security inspection**: All traffic inspection
- **Compliance requirements**: Regulatory compliance
- **Network segmentation**: Advanced network controls
- **Third-party integration**: Existing security solutions

## Load Balancer Components

### Listeners
A listener checks for connection requests using the protocol and port you configure.

#### ALB Listeners
- **Protocols**: HTTP (port 80), HTTPS (port 443)
- **Rules**: Conditions and actions for routing
- **Default actions**: Forward, redirect, return fixed response

#### NLB Listeners  
- **Protocols**: TCP, UDP, TLS
- **Port range**: 1-65535
- **Actions**: Forward to target group

#### Listener Rules (ALB Only)
```yaml
Rule Components:
  Conditions:
    - Host header
    - Path pattern
    - HTTP header
    - HTTP method
    - Query string
    - Source IP
  
  Actions:
    - Forward to target group
    - Redirect to URL
    - Return fixed response
    - Authenticate (OIDC/Cognito)
```

### Target Groups
A target group routes requests to one or more registered targets using specified protocol and port.

#### Target Group Settings
- **Protocol**: HTTP, HTTPS (ALB), TCP, UDP, TLS (NLB)
- **Port**: Target port for health checks and traffic
- **Health check settings**: Protocol, path, interval, timeout
- **Target type**: Instance, IP, or Lambda (ALB only)

#### Target Group Algorithms
- **Round robin** (default for ALB)
- **Least outstanding requests** (ALB alternative)
- **Flow hash** (NLB - based on protocol, source/destination IP and port)

### Cross-Zone Load Balancing

#### ALB
- **Always enabled**: Cannot be disabled
- **No additional charges**: Included by default

#### NLB  
- **Disabled by default**: Must be explicitly enabled
- **Additional charges**: Cross-AZ data transfer costs apply
- **Use case dependent**: Enable for even distribution

#### CLB
- **Disabled by default**: Can be enabled
- **Additional charges**: Cross-AZ data transfer costs

## Health Checks

### Health Check Parameters

#### Common Parameters
- **Protocol**: HTTP, HTTPS, TCP (ALB/NLB)
- **Port**: Health check port (can differ from traffic port)
- **Path**: Health check path (HTTP/HTTPS only)
- **Interval**: 15 or 30 seconds (ALB), 10-300 seconds (NLB)
- **Timeout**: 2-120 seconds
- **Healthy threshold**: 2-10 consecutive successes
- **Unhealthy threshold**: 2-10 consecutive failures

#### Health Check Types

##### HTTP/HTTPS Health Checks
```yaml
Configuration:
  Protocol: HTTP or HTTPS
  Port: 80 (HTTP) or 443 (HTTPS)
  Path: /health (example)
  Success codes: 200, 200-299
  Timeout: 5 seconds
  Interval: 30 seconds
  Healthy threshold: 5
  Unhealthy threshold: 2
```

##### TCP Health Check
```yaml
Configuration:
  Protocol: TCP
  Port: Application port
  Timeout: 10 seconds
  Interval: 30 seconds
  Healthy threshold: 10
  Unhealthy threshold: 3
```

### Health Check States
1. **Initial**: Target registration in progress
2. **Healthy**: Target passing health checks  
3. **Unhealthy**: Target failing health checks
4. **Unused**: Target not registered with any load balancer
5. **Draining**: Target deregistration in progress

### Best Practices for Health Checks
- **Lightweight checks**: Avoid resource-intensive operations
- **Dependency checks**: Include critical dependencies
- **Custom health endpoints**: Create dedicated health check endpoints
- **Appropriate timeouts**: Balance responsiveness vs. false positives
- **Graceful degradation**: Handle partial failures appropriately

## Security Features

### SSL/TLS Termination

#### Certificate Management
- **AWS Certificate Manager (ACM)**: Fully managed SSL certificates
- **Custom certificates**: Upload your own certificates
- **Automatic renewal**: ACM certificates auto-renew
- **Wildcard certificates**: Support for *.example.com

#### SSL Policies
```yaml
Predefined SSL Policies:
  - ELBSecurityPolicy-TLS-1-2-2017-01: TLS 1.2 only
  - ELBSecurityPolicy-TLS-1-2-Ext-2018-06: Extended TLS 1.2
  - ELBSecurityPolicy-FS-2018-06: Forward secrecy
  - ELBSecurityPolicy-TLS-1-0-2015-04: Legacy support
```

#### Perfect Forward Secrecy
- **ECDHE ciphers**: Ephemeral key exchange
- **DHE ciphers**: Diffie-Hellman ephemeral
- **Session key protection**: Compromise of private key doesn't affect past sessions

### Web Application Firewall (WAF)

#### Integration with ALB
- **Layer 7 protection**: Application layer security
- **Custom rules**: Block malicious requests
- **Managed rule groups**: Pre-configured protection
- **Rate limiting**: Request rate controls

#### Common WAF Rules
```yaml
Managed Rule Groups:
  - Core Rule Set: OWASP top 10 protection
  - Admin Protection: Admin interface protection  
  - Known Bad Inputs: Known malicious patterns
  - SQL Database: SQL injection protection
  - Linux/Windows OS: OS-specific attacks
```

### Authentication Integration

#### Amazon Cognito
- **User pools**: User directory service
- **Identity pools**: Federated identities
- **Social login**: Facebook, Google, Amazon
- **SAML/OIDC**: Enterprise identity providers

#### OIDC Integration
- **Standards-based**: OpenID Connect protocol
- **Token validation**: Automatic JWT validation
- **Claims routing**: Route based on user attributes
- **Session management**: Handle authentication sessions

### Security Groups and NACLs

#### ALB Security
- **Security groups**: Applied to load balancer
- **Ingress rules**: Allow traffic from internet (0.0.0.0/0)
- **Egress rules**: Allow traffic to targets
- **Target security groups**: Allow traffic from load balancer

#### NLB Security
- **No security groups**: Applied to targets only
- **Source IP preservation**: Client IP reaches targets
- **Target security groups**: Must allow client traffic directly
- **Network ACLs**: Apply at subnet level

## Monitoring and Logging

### CloudWatch Metrics

#### ALB Metrics
```yaml
Key Metrics:
  Request Metrics:
    - RequestCount: Total requests
    - NewConnectionCount: New connections
    - ActiveConnectionCount: Active connections
    
  Response Metrics:
    - HTTPCode_Target_2XX_Count: Successful responses
    - HTTPCode_Target_4XX_Count: Client errors
    - HTTPCode_Target_5XX_Count: Server errors
    - HTTPCode_ELB_5XX_Count: Load balancer errors
    
  Performance Metrics:
    - TargetResponseTime: Response time from targets
    - ResponseTime: Total response time including LB overhead
    
  Target Metrics:
    - HealthyHostCount: Healthy targets
    - UnHealthyHostCount: Unhealthy targets
```

#### NLB Metrics
```yaml
Key Metrics:
  Connection Metrics:
    - ActiveFlowCount_TCP: Active TCP flows
    - ActiveFlowCount_UDP: Active UDP flows
    - NewFlowCount_TCP: New TCP flows
    - NewFlowCount_UDP: New UDP flows
    
  Data Transfer:
    - ProcessedBytes_TCP: TCP bytes processed
    - ProcessedBytes_UDP: UDP bytes processed
    
  Target Health:
    - HealthyHostCount: Healthy targets
    - UnHealthyHostCount: Unhealthy targets
```

### Access Logs

#### ALB Access Logs
```
timestamp elb client:port target:port request_processing_time target_processing_time response_processing_time elb_status_code target_status_code received_bytes sent_bytes "request" "user_agent" ssl_cipher ssl_protocol target_group_arn "trace_id" "domain_name" "chosen_cert_arn" matched_rule_priority request_creation_time "actions_executed" "redirect_url" "error_reason"
```

#### Key Access Log Fields
- **timestamp**: Request timestamp
- **client:port**: Client IP and port
- **target:port**: Target IP and port  
- **request_processing_time**: Time to receive request
- **target_processing_time**: Time for target to respond
- **response_processing_time**: Time to send response
- **elb_status_code**: Load balancer response code
- **target_status_code**: Target response code
- **request**: HTTP request line
- **user_agent**: Client user agent
- **trace_id**: Request tracing ID

### Connection Logs (NLB)
```
version timestamp elb client:port target:port connection_time tls_handshake_time received_bytes sent_bytes incoming_tls_alert chosen_cert_arn chosen_cert_serial tls_cipher tls_protocol_version tls_named_group domain_name alpn_fe_protocol alpn_be_protocol alpn_client_preference_list
```

### Request Tracing
- **X-Amzn-Trace-Id header**: Unique request identifier
- **AWS X-Ray integration**: Distributed tracing
- **Request flow tracking**: End-to-end visibility
- **Performance analysis**: Identify bottlenecks

## Best Practices

### Architecture Design

#### Multi-AZ Deployment
```yaml
Best Practice:
  - Deploy in at least 2 AZs
  - Enable cross-zone load balancing (when appropriate)
  - Distribute targets evenly across AZs
  - Consider regional failover strategies
```

#### Target Group Configuration
- **Appropriate health checks**: Match application requirements
- **Deregistration delay**: Allow in-flight requests to complete
- **Sticky sessions**: Use sparingly, prefer stateless design
- **Target capacity**: Maintain adequate healthy targets

#### Security Configuration
- **Least privilege**: Minimum required security group rules
- **SSL/TLS**: Always use HTTPS for sensitive data
- **WAF integration**: Protect against common attacks
- **Certificate management**: Use ACM for automated renewal

### Performance Optimization

#### ALB Optimization
- **Connection pooling**: Enable keep-alive connections
- **HTTP/2**: Enable for supported clients
- **Compression**: Enable response compression
- **Caching strategies**: Implement appropriate caching

#### NLB Optimization
- **Connection draining**: Configure appropriate deregistration delay
- **Client affinity**: Use source IP hash when needed
- **Preserve source IP**: Ensure security groups accommodate

### Operational Excellence

#### Monitoring Strategy
```yaml
Monitoring Approach:
  CloudWatch Metrics:
    - Set up alarms for key metrics
    - Monitor healthy host count
    - Track response times and error rates
    
  Access Logs:
    - Enable for troubleshooting
    - Analyze traffic patterns
    - Identify security threats
    
  AWS X-Ray:
    - Enable request tracing
    - Identify performance bottlenecks
    - Monitor service dependencies
```

#### Automation
- **Auto Scaling integration**: Scale targets based on metrics
- **Blue/green deployments**: Minimize deployment risk
- **Infrastructure as Code**: Use CloudFormation/CDK/Terraform
- **Automated testing**: Include load balancer in CI/CD pipelines

## Common Use Cases

### Web Applications

#### Traditional Web Architecture
```
Internet → ALB → EC2 Instances (Web Servers) → RDS (Database)
```

**ALB Configuration:**
- HTTP/HTTPS listeners
- Path-based routing for static content
- SSL termination
- WAF protection
- Health checks on /health endpoint

#### Microservices Architecture
```
Internet → ALB → Target Groups:
                   - API Service (api.example.com)
                   - Auth Service (auth.example.com)  
                   - User Service (user.example.com)
```

**Routing Rules:**
- Host-based routing for services
- Path-based routing within services
- Container target groups
- Service discovery integration

### High-Performance Applications

#### Gaming/Real-time Applications
```
Internet → NLB → Game Servers (TCP/UDP)
```

**NLB Configuration:**
- TCP/UDP listeners
- Static IP addresses
- Ultra-low latency
- Source IP preservation
- Minimal health check overhead

#### IoT Applications
```
IoT Devices → NLB → Processing Servers
```

**Requirements:**
- High connection count
- Low latency requirements
- TCP/UDP protocol support
- Scalable architecture

### Hybrid Architectures

#### Multi-Cloud Integration
```
Internet → ALB → Target Groups:
                  - AWS EC2 Instances
                  - On-premises servers (IP targets)
                  - Other cloud providers (IP targets)
```

**Configuration:**
- IP target groups for external resources
- VPN/Direct Connect connectivity
- Health checks across networks
- Weighted routing for migration

#### Container Orchestration

#### ECS Integration
```yaml
ECS Service Configuration:
  Target Group:
    - Type: IP
    - Protocol: HTTP
    - Port: 80
    - Health Check: /health
  
  Load Balancer:
    - Type: ALB  
    - Listener: HTTPS:443
    - Certificate: ACM
```

#### EKS Integration
```yaml
Kubernetes Service:
  apiVersion: v1
  kind: Service
  metadata:
    annotations:
      service.beta.kubernetes.io/aws-load-balancer-type: "nlb"
  spec:
    type: LoadBalancer
    ports:
    - port: 80
```

### Serverless Integration

#### Lambda Functions
```yaml
ALB → Lambda Integration:
  Target Type: Lambda function
  Request Format: Multi-value headers
  Response Format: ALB format
  
  Use Cases:
    - Serverless web applications
    - API backends
    - Event processing
    - Legacy application modernization
```

## Exam Tips

### Key Concepts for SAA-C03

#### Load Balancer Selection
```yaml
Decision Matrix:
  Need Layer 7 routing? → ALB
  Need ultra-high performance? → NLB  
  Need static IP addresses? → NLB
  Legacy application? → Consider CLB migration
  Network appliances? → GWLB
  
  Protocol Requirements:
    - HTTP/HTTPS + advanced routing → ALB
    - TCP/UDP + high performance → NLB
    - Network inspection → GWLB
```

#### Common Exam Scenarios

##### Multi-AZ High Availability
**Question Pattern**: "Design a highly available web application"
**Answer**: ALB with targets in multiple AZs, health checks enabled

##### SSL Termination
**Question Pattern**: "Reduce SSL processing load on web servers"  
**Answer**: Configure SSL termination on ALB with ACM certificates

##### Microservices Routing
**Question Pattern**: "Route requests to different services based on URL"
**Answer**: ALB with path-based or host-based routing rules

##### Gaming Application
**Question Pattern**: "Ultra-low latency TCP application"
**Answer**: NLB with TCP listeners and static IP addresses

##### Security Requirements
**Question Pattern**: "Protect web application from common attacks"
**Answer**: ALB + WAF integration with appropriate rule groups

### Important Service Limits

#### ALB Limits
- **Listeners per load balancer**: 50
- **Rules per listener**: 100
- **Targets per target group**: 1,000
- **Target groups per load balancer**: 50
- **Certificates per load balancer**: 25

#### NLB Limits  
- **Listeners per load balancer**: 50
- **Targets per target group**: 1,000
- **Target groups per load balancer**: 50
- **Flow capacity**: 55 million per minute

### Cost Optimization

#### ALB Pricing Components
- **Load Balancer Hours**: $0.0225 per hour
- **Load Balancer Capacity Units (LCU)**: $0.008 per LCU-hour
- **Data transfer**: Standard AWS data transfer rates

#### NLB Pricing Components
- **Load Balancer Hours**: $0.0225 per hour
- **Load Balancer Capacity Units (NLCU)**: $0.006 per NLCU-hour
- **Data transfer**: Standard AWS data transfer rates

#### Cost Optimization Strategies
- **Right-size load balancer**: Choose appropriate type for workload
- **Monitor LCU/NLCU usage**: Optimize for capacity units
- **Cross-zone load balancing**: Consider data transfer costs
- **Reserved capacity**: For predictable workloads

### Troubleshooting Common Issues

#### Target Registration Issues
```yaml
Common Problems:
  - Security group misconfiguration
  - Health check path returns errors
  - Target not responding on health check port
  - Subnets not associated with load balancer
  
Solutions:
  - Verify security group rules
  - Test health check endpoint manually
  - Check target application logs
  - Ensure proper subnet configuration
```

#### Performance Issues
```yaml
Common Problems:
  - High response times
  - Connection timeouts
  - Uneven target distribution
  - Certificate issues
  
Solutions:
  - Review target response times
  - Check target capacity and auto scaling
  - Enable cross-zone load balancing
  - Verify SSL certificate configuration
```

#### SSL/TLS Issues
```yaml
Common Problems:
  - Certificate not trusted
  - SSL handshake failures
  - Mixed content warnings
  - Protocol version mismatches
  
Solutions:
  - Use ACM for certificate management
  - Configure appropriate SSL policy
  - Ensure HTTPS redirect rules
  - Update SSL policy for compatibility
```

## Summary

AWS Elastic Load Balancer is a critical service for building highly available, scalable, and secure applications on AWS. Understanding the different types of load balancers, their use cases, and configuration options is essential for the SAA-C03 certification.

### Key Takeaways
1. **ALB**: Best for HTTP/HTTPS with advanced Layer 7 routing
2. **NLB**: Optimal for high-performance Layer 4 load balancing  
3. **GWLB**: Specialized for network virtual appliances
4. **Security**: Always implement appropriate security controls
5. **Monitoring**: Use CloudWatch metrics and access logs for visibility
6. **Best Practices**: Follow AWS recommendations for reliability and performance

### Exam Focus Areas
- Load balancer type selection based on requirements
- Security configuration (SSL, WAF, Security Groups)
- Multi-AZ deployment for high availability
- Integration with other AWS services
- Cost optimization strategies
- Troubleshooting common issues

This comprehensive guide covers all the essential ELB concepts needed for the AWS Solutions Architect Associate SAA-C03 certification exam.