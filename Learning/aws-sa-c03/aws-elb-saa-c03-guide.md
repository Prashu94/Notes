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
13. [AWS CLI Commands Reference](#aws-cli-commands-reference)
14. [Exam Tips](#exam-tips)

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

## AWS CLI Commands Reference

This section provides comprehensive AWS CLI commands for managing Elastic Load Balancers. All commands use AWS CLI v2 syntax.

### Application Load Balancer (ALB) Management

#### Create Application Load Balancer

```bash
# Create an internet-facing ALB
aws elbv2 create-load-balancer \
  --name my-application-load-balancer \
  --subnets subnet-12345678 subnet-87654321 \
  --security-groups sg-12345678 \
  --scheme internet-facing \
  --type application \
  --ip-address-type ipv4 \
  --tags Key=Environment,Value=Production Key=Application,Value=WebApp

# Create an internal ALB
aws elbv2 create-load-balancer \
  --name my-internal-alb \
  --subnets subnet-12345678 subnet-87654321 \
  --security-groups sg-12345678 \
  --scheme internal \
  --type application

# Create ALB with dual-stack (IPv4 and IPv6)
aws elbv2 create-load-balancer \
  --name my-dualstack-alb \
  --subnets subnet-12345678 subnet-87654321 \
  --security-groups sg-12345678 \
  --ip-address-type dualstack
```

#### Describe and List ALBs

```bash
# List all load balancers
aws elbv2 describe-load-balancers

# Describe specific load balancer
aws elbv2 describe-load-balancers \
  --load-balancer-arns arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/my-alb/1234567890abcdef

# Describe load balancers by name
aws elbv2 describe-load-balancers \
  --names my-application-load-balancer

# Filter load balancers with JMESPath query
aws elbv2 describe-load-balancers \
  --query 'LoadBalancers[?Type==`application`].[LoadBalancerName,DNSName,State.Code]' \
  --output table
```

#### Modify ALB Attributes

```bash
# Enable access logs
aws elbv2 modify-load-balancer-attributes \
  --load-balancer-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/my-alb/1234567890abcdef \
  --attributes \
    Key=access_logs.s3.enabled,Value=true \
    Key=access_logs.s3.bucket,Value=my-alb-logs \
    Key=access_logs.s3.prefix,Value=my-app

# Enable deletion protection
aws elbv2 modify-load-balancer-attributes \
  --load-balancer-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/my-alb/1234567890abcdef \
  --attributes Key=deletion_protection.enabled,Value=true

# Configure idle timeout (default is 60 seconds)
aws elbv2 modify-load-balancer-attributes \
  --load-balancer-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/my-alb/1234567890abcdef \
  --attributes Key=idle_timeout.timeout_seconds,Value=120

# Enable HTTP/2
aws elbv2 modify-load-balancer-attributes \
  --load-balancer-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/my-alb/1234567890abcdef \
  --attributes Key=routing.http2.enabled,Value=true

# Enable drop invalid header fields
aws elbv2 modify-load-balancer-attributes \
  --load-balancer-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/my-alb/1234567890abcdef \
  --attributes Key=routing.http.drop_invalid_header_fields.enabled,Value=true
```

#### Delete ALB

```bash
# Delete load balancer
aws elbv2 delete-load-balancer \
  --load-balancer-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/my-alb/1234567890abcdef
```

### Network Load Balancer (NLB) Management

#### Create Network Load Balancer

```bash
# Create internet-facing NLB
aws elbv2 create-load-balancer \
  --name my-network-load-balancer \
  --subnets subnet-12345678 subnet-87654321 \
  --type network \
  --scheme internet-facing \
  --tags Key=Environment,Value=Production

# Create NLB with static IP addresses (Elastic IPs)
aws elbv2 create-load-balancer \
  --name my-nlb-with-eip \
  --type network \
  --subnet-mappings SubnetId=subnet-12345678,AllocationId=eipalloc-12345678 \
                    SubnetId=subnet-87654321,AllocationId=eipalloc-87654321

# Create internal NLB
aws elbv2 create-load-balancer \
  --name my-internal-nlb \
  --subnets subnet-12345678 subnet-87654321 \
  --scheme internal \
  --type network
```

#### Modify NLB Attributes

```bash
# Enable cross-zone load balancing (disabled by default for NLB)
aws elbv2 modify-load-balancer-attributes \
  --load-balancer-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/net/my-nlb/1234567890abcdef \
  --attributes Key=load_balancing.cross_zone.enabled,Value=true

# Enable access logs for NLB
aws elbv2 modify-load-balancer-attributes \
  --load-balancer-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/net/my-nlb/1234567890abcdef \
  --attributes \
    Key=access_logs.s3.enabled,Value=true \
    Key=access_logs.s3.bucket,Value=my-nlb-logs \
    Key=access_logs.s3.prefix,Value=my-app

# Enable deletion protection
aws elbv2 modify-load-balancer-attributes \
  --load-balancer-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/net/my-nlb/1234567890abcdef \
  --attributes Key=deletion_protection.enabled,Value=true
```

### Classic Load Balancer (CLB) Operations

#### Create Classic Load Balancer

```bash
# Create Classic Load Balancer (using older elb command)
aws elb create-load-balancer \
  --load-balancer-name my-classic-load-balancer \
  --listeners "Protocol=HTTP,LoadBalancerPort=80,InstanceProtocol=HTTP,InstancePort=80" \
             "Protocol=HTTPS,LoadBalancerPort=443,InstanceProtocol=HTTP,InstancePort=80,SSLCertificateId=arn:aws:acm:us-east-1:123456789012:certificate/12345678-1234-1234-1234-123456789012" \
  --subnets subnet-12345678 subnet-87654321 \
  --security-groups sg-12345678
```

#### Configure CLB Health Checks

```bash
# Configure health check for CLB
aws elb configure-health-check \
  --load-balancer-name my-classic-load-balancer \
  --health-check \
    Target=HTTP:80/health,\
    Interval=30,\
    Timeout=5,\
    UnhealthyThreshold=2,\
    HealthyThreshold=2
```

#### Manage CLB Instances

```bash
# Register instances with CLB
aws elb register-instances-with-load-balancer \
  --load-balancer-name my-classic-load-balancer \
  --instances i-12345678 i-87654321

# Deregister instances from CLB
aws elb deregister-instances-from-load-balancer \
  --load-balancer-name my-classic-load-balancer \
  --instances i-12345678

# Describe instance health
aws elb describe-instance-health \
  --load-balancer-name my-classic-load-balancer
```

#### Delete CLB

```bash
# Delete Classic Load Balancer
aws elb delete-load-balancer \
  --load-balancer-name my-classic-load-balancer
```

### Target Groups Management

#### Create Target Groups

```bash
# Create target group for EC2 instances (ALB/NLB)
aws elbv2 create-target-group \
  --name my-targets \
  --protocol HTTP \
  --port 80 \
  --vpc-id vpc-12345678 \
  --health-check-protocol HTTP \
  --health-check-path /health \
  --health-check-interval-seconds 30 \
  --health-check-timeout-seconds 5 \
  --healthy-threshold-count 2 \
  --unhealthy-threshold-count 2 \
  --matcher HttpCode=200

# Create target group with IP address targets
aws elbv2 create-target-group \
  --name my-ip-targets \
  --protocol HTTP \
  --port 80 \
  --vpc-id vpc-12345678 \
  --target-type ip

# Create target group for Lambda functions
aws elbv2 create-target-group \
  --name my-lambda-targets \
  --target-type lambda

# Create target group for NLB with TCP protocol
aws elbv2 create-target-group \
  --name my-tcp-targets \
  --protocol TCP \
  --port 3306 \
  --vpc-id vpc-12345678 \
  --health-check-protocol TCP

# Create target group with advanced health check settings
aws elbv2 create-target-group \
  --name my-advanced-targets \
  --protocol HTTPS \
  --port 443 \
  --vpc-id vpc-12345678 \
  --health-check-protocol HTTPS \
  --health-check-path /api/health \
  --health-check-interval-seconds 10 \
  --health-check-timeout-seconds 5 \
  --healthy-threshold-count 3 \
  --unhealthy-threshold-count 3 \
  --matcher HttpCode=200-299
```

#### Describe Target Groups

```bash
# List all target groups
aws elbv2 describe-target-groups

# Describe specific target group
aws elbv2 describe-target-groups \
  --target-group-arns arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-targets/1234567890abcdef

# Describe target groups by name
aws elbv2 describe-target-groups \
  --names my-targets

# List target groups for a load balancer
aws elbv2 describe-target-groups \
  --load-balancer-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/my-alb/1234567890abcdef
```

#### Register and Deregister Targets

```bash
# Register EC2 instances with target group
aws elbv2 register-targets \
  --target-group-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-targets/1234567890abcdef \
  --targets Id=i-12345678 Id=i-87654321

# Register targets with specific ports
aws elbv2 register-targets \
  --target-group-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-targets/1234567890abcdef \
  --targets Id=i-12345678,Port=8080 Id=i-87654321,Port=8081

# Register IP address targets
aws elbv2 register-targets \
  --target-group-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-ip-targets/1234567890abcdef \
  --targets Id=10.0.1.10 Id=10.0.2.20

# Register IP targets with availability zone
aws elbv2 register-targets \
  --target-group-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-ip-targets/1234567890abcdef \
  --targets Id=10.0.1.10,AvailabilityZone=us-east-1a Id=10.0.2.20,AvailabilityZone=us-east-1b

# Register Lambda function as target
aws elbv2 register-targets \
  --target-group-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-lambda-targets/1234567890abcdef \
  --targets Id=arn:aws:lambda:us-east-1:123456789012:function:my-function

# Deregister targets from target group
aws elbv2 deregister-targets \
  --target-group-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-targets/1234567890abcdef \
  --targets Id=i-12345678 Id=i-87654321
```

#### Modify Target Group Attributes

```bash
# Configure deregistration delay (connection draining)
aws elbv2 modify-target-group-attributes \
  --target-group-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-targets/1234567890abcdef \
  --attributes Key=deregistration_delay.timeout_seconds,Value=30

# Enable stickiness (session affinity) for ALB
aws elbv2 modify-target-group-attributes \
  --target-group-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-targets/1234567890abcdef \
  --attributes \
    Key=stickiness.enabled,Value=true \
    Key=stickiness.type,Value=lb_cookie \
    Key=stickiness.lb_cookie.duration_seconds,Value=86400

# Enable application-based stickiness
aws elbv2 modify-target-group-attributes \
  --target-group-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-targets/1234567890abcdef \
  --attributes \
    Key=stickiness.enabled,Value=true \
    Key=stickiness.type,Value=app_cookie \
    Key=stickiness.app_cookie.cookie_name,Value=MyCookie \
    Key=stickiness.app_cookie.duration_seconds,Value=86400

# Enable slow start mode
aws elbv2 modify-target-group-attributes \
  --target-group-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-targets/1234567890abcdef \
  --attributes Key=slow_start.duration_seconds,Value=30

# Configure load balancing algorithm (for ALB)
aws elbv2 modify-target-group-attributes \
  --target-group-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-targets/1234567890abcdef \
  --attributes Key=load_balancing.algorithm.type,Value=least_outstanding_requests

# Enable cross-zone load balancing for target group
aws elbv2 modify-target-group-attributes \
  --target-group-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-targets/1234567890abcdef \
  --attributes Key=load_balancing.cross_zone.enabled,Value=true

# Configure Lambda multi-value headers
aws elbv2 modify-target-group-attributes \
  --target-group-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-lambda-targets/1234567890abcdef \
  --attributes Key=lambda.multi_value_headers.enabled,Value=true
```

#### Delete Target Group

```bash
# Delete target group
aws elbv2 delete-target-group \
  --target-group-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-targets/1234567890abcdef
```

### Health Checks Configuration

#### Check Target Health

```bash
# Describe target health for a target group
aws elbv2 describe-target-health \
  --target-group-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-targets/1234567890abcdef

# Check health of specific targets
aws elbv2 describe-target-health \
  --target-group-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-targets/1234567890abcdef \
  --targets Id=i-12345678 Id=i-87654321

# Get health status with detailed output
aws elbv2 describe-target-health \
  --target-group-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-targets/1234567890abcdef \
  --query 'TargetHealthDescriptions[*].[Target.Id,TargetHealth.State,TargetHealth.Reason]' \
  --output table
```

#### Modify Health Check Settings

```bash
# Modify target group health check settings
aws elbv2 modify-target-group \
  --target-group-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-targets/1234567890abcdef \
  --health-check-protocol HTTP \
  --health-check-path /health \
  --health-check-interval-seconds 15 \
  --health-check-timeout-seconds 5 \
  --healthy-threshold-count 2 \
  --unhealthy-threshold-count 2

# Configure advanced health check with custom port
aws elbv2 modify-target-group \
  --target-group-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-targets/1234567890abcdef \
  --health-check-port 8080 \
  --health-check-protocol HTTP \
  --health-check-path /api/health \
  --matcher HttpCode=200,202

# Enable health check for NLB with TCP
aws elbv2 modify-target-group \
  --target-group-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-tcp-targets/1234567890abcdef \
  --health-check-protocol TCP \
  --health-check-interval-seconds 30
```

### Listeners Management

#### Create Listeners

```bash
# Create HTTP listener for ALB
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/my-alb/1234567890abcdef \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-targets/1234567890abcdef

# Create HTTPS listener with SSL certificate
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/my-alb/1234567890abcdef \
  --protocol HTTPS \
  --port 443 \
  --certificates CertificateArn=arn:aws:acm:us-east-1:123456789012:certificate/12345678-1234-1234-1234-123456789012 \
  --ssl-policy ELBSecurityPolicy-TLS-1-2-2017-01 \
  --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-targets/1234567890abcdef

# Create HTTP listener with redirect to HTTPS
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/my-alb/1234567890abcdef \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=redirect,RedirectConfig="{Protocol=HTTPS,Port=443,StatusCode=HTTP_301}"

# Create listener with fixed response
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/my-alb/1234567890abcdef \
  --protocol HTTP \
  --port 8080 \
  --default-actions Type=fixed-response,FixedResponseConfig="{StatusCode=200,ContentType=text/plain,MessageBody='Hello World'}"

# Create TCP listener for NLB
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/net/my-nlb/1234567890abcdef \
  --protocol TCP \
  --port 3306 \
  --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-tcp-targets/1234567890abcdef

# Create TLS listener for NLB
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/net/my-nlb/1234567890abcdef \
  --protocol TLS \
  --port 443 \
  --certificates CertificateArn=arn:aws:acm:us-east-1:123456789012:certificate/12345678-1234-1234-1234-123456789012 \
  --ssl-policy ELBSecurityPolicy-TLS-1-2-2017-01 \
  --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-targets/1234567890abcdef
```

#### Describe Listeners

```bash
# List all listeners for a load balancer
aws elbv2 describe-listeners \
  --load-balancer-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/my-alb/1234567890abcdef

# Describe specific listener
aws elbv2 describe-listeners \
  --listener-arns arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/my-alb/1234567890abcdef/1234567890abcdef
```

#### Modify Listeners

```bash
# Modify listener default action
aws elbv2 modify-listener \
  --listener-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/my-alb/1234567890abcdef/1234567890abcdef \
  --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-new-targets/1234567890abcdef

# Update SSL certificate
aws elbv2 modify-listener \
  --listener-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/my-alb/1234567890abcdef/1234567890abcdef \
  --certificates CertificateArn=arn:aws:acm:us-east-1:123456789012:certificate/new-cert-id

# Update SSL policy
aws elbv2 modify-listener \
  --listener-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/my-alb/1234567890abcdef/1234567890abcdef \
  --ssl-policy ELBSecurityPolicy-TLS-1-3-2021-06
```

#### Delete Listener

```bash
# Delete listener
aws elbv2 delete-listener \
  --listener-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/my-alb/1234567890abcdef/1234567890abcdef
```

### Listener Rules Management

#### Create Listener Rules

```bash
# Create path-based routing rule
aws elbv2 create-rule \
  --listener-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/my-alb/1234567890abcdef/1234567890abcdef \
  --priority 10 \
  --conditions Field=path-pattern,Values='/api/*' \
  --actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/api-targets/1234567890abcdef

# Create host-based routing rule
aws elbv2 create-rule \
  --listener-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/my-alb/1234567890abcdef/1234567890abcdef \
  --priority 20 \
  --conditions Field=host-header,Values='api.example.com' \
  --actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/api-targets/1234567890abcdef

# Create rule with multiple conditions
aws elbv2 create-rule \
  --listener-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/my-alb/1234567890abcdef/1234567890abcdef \
  --priority 30 \
  --conditions \
    Field=host-header,Values='admin.example.com' \
    Field=path-pattern,Values='/admin/*' \
  --actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/admin-targets/1234567890abcdef

# Create rule based on HTTP headers
aws elbv2 create-rule \
  --listener-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/my-alb/1234567890abcdef/1234567890abcdef \
  --priority 40 \
  --conditions Field=http-header,HttpHeaderName=User-Agent,Values='*Mobile*' \
  --actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/mobile-targets/1234567890abcdef

# Create rule based on query strings
aws elbv2 create-rule \
  --listener-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/my-alb/1234567890abcdef/1234567890abcdef \
  --priority 50 \
  --conditions Field=query-string,Values='Key=version,Value=v2' \
  --actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/v2-targets/1234567890abcdef

# Create rule based on source IP
aws elbv2 create-rule \
  --listener-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/my-alb/1234567890abcdef/1234567890abcdef \
  --priority 60 \
  --conditions Field=source-ip,Values='192.0.2.0/24','198.51.100.0/24' \
  --actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/internal-targets/1234567890abcdef

# Create rule based on HTTP request method
aws elbv2 create-rule \
  --listener-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/my-alb/1234567890abcdef/1234567890abcdef \
  --priority 70 \
  --conditions Field=http-request-method,Values='POST','PUT' \
  --actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/write-targets/1234567890abcdef

# Create rule with redirect action
aws elbv2 create-rule \
  --listener-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/my-alb/1234567890abcdef/1234567890abcdef \
  --priority 80 \
  --conditions Field=path-pattern,Values='/old-path/*' \
  --actions Type=redirect,RedirectConfig="{Protocol=HTTPS,Port=443,Path='/new-path/#{path}',StatusCode=HTTP_301}"

# Create rule with fixed response
aws elbv2 create-rule \
  --listener-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/my-alb/1234567890abcdef/1234567890abcdef \
  --priority 90 \
  --conditions Field=path-pattern,Values='/maintenance' \
  --actions Type=fixed-response,FixedResponseConfig="{StatusCode=503,ContentType=text/html,MessageBody='<html>Service Unavailable</html>'}"

# Create rule with weighted target groups
aws elbv2 create-rule \
  --listener-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/my-alb/1234567890abcdef/1234567890abcdef \
  --priority 100 \
  --conditions Field=path-pattern,Values='/canary/*' \
  --actions Type=forward,ForwardConfig="{TargetGroups=[{TargetGroupArn=arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/stable/1234567890abcdef,Weight=90},{TargetGroupArn=arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/canary/1234567890abcdef,Weight=10}],TargetGroupStickinessConfig={Enabled=true,DurationSeconds=3600}}"
```

#### Describe Rules

```bash
# List all rules for a listener
aws elbv2 describe-rules \
  --listener-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/my-alb/1234567890abcdef/1234567890abcdef

# Describe specific rule
aws elbv2 describe-rules \
  --rule-arns arn:aws:elasticloadbalancing:us-east-1:123456789012:listener-rule/app/my-alb/1234567890abcdef/1234567890abcdef/1234567890abcdef

# Get rules in priority order
aws elbv2 describe-rules \
  --listener-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/my-alb/1234567890abcdef/1234567890abcdef \
  --query 'Rules | sort_by(@, &Priority)' \
  --output table
```

#### Modify Rules

```bash
# Modify rule conditions
aws elbv2 modify-rule \
  --rule-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:listener-rule/app/my-alb/1234567890abcdef/1234567890abcdef/1234567890abcdef \
  --conditions Field=path-pattern,Values='/api/v2/*'

# Modify rule actions
aws elbv2 modify-rule \
  --rule-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:listener-rule/app/my-alb/1234567890abcdef/1234567890abcdef/1234567890abcdef \
  --actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/new-targets/1234567890abcdef
```

#### Change Rule Priority

```bash
# Set rule priority
aws elbv2 set-rule-priorities \
  --rule-priorities \
    RuleArn=arn:aws:elasticloadbalancing:us-east-1:123456789012:listener-rule/app/my-alb/1234567890abcdef/1234567890abcdef/rule1,Priority=5 \
    RuleArn=arn:aws:elasticloadbalancing:us-east-1:123456789012:listener-rule/app/my-alb/1234567890abcdef/1234567890abcdef/rule2,Priority=10
```

#### Delete Rule

```bash
# Delete listener rule
aws elbv2 delete-rule \
  --rule-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:listener-rule/app/my-alb/1234567890abcdef/1234567890abcdef/1234567890abcdef
```

### SSL/TLS Certificates Management

#### Add Certificates to Listener

```bash
# Add additional certificates to HTTPS listener
aws elbv2 add-listener-certificates \
  --listener-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/my-alb/1234567890abcdef/1234567890abcdef \
  --certificates \
    CertificateArn=arn:aws:acm:us-east-1:123456789012:certificate/cert1 \
    CertificateArn=arn:aws:acm:us-east-1:123456789012:certificate/cert2
```

#### Describe Listener Certificates

```bash
# List certificates attached to listener
aws elbv2 describe-listener-certificates \
  --listener-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/my-alb/1234567890abcdef/1234567890abcdef
```

#### Remove Certificates from Listener

```bash
# Remove certificates from listener
aws elbv2 remove-listener-certificates \
  --listener-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/my-alb/1234567890abcdef/1234567890abcdef \
  --certificates CertificateArn=arn:aws:acm:us-east-1:123456789012:certificate/cert1
```

#### Describe SSL Policies

```bash
# List all SSL policies
aws elbv2 describe-ssl-policies

# Describe specific SSL policy
aws elbv2 describe-ssl-policies \
  --names ELBSecurityPolicy-TLS-1-2-2017-01

# List recommended SSL policies
aws elbv2 describe-ssl-policies \
  --query 'SslPolicies[?contains(Name, `Recommended`)].Name'
```

### Access Logs Configuration

```bash
# Enable access logs for ALB
aws elbv2 modify-load-balancer-attributes \
  --load-balancer-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/my-alb/1234567890abcdef \
  --attributes \
    Key=access_logs.s3.enabled,Value=true \
    Key=access_logs.s3.bucket,Value=my-loadbalancer-logs \
    Key=access_logs.s3.prefix,Value=my-app/production

# Disable access logs
aws elbv2 modify-load-balancer-attributes \
  --load-balancer-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/my-alb/1234567890abcdef \
  --attributes Key=access_logs.s3.enabled,Value=false

# Get access logs configuration
aws elbv2 describe-load-balancer-attributes \
  --load-balancer-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/my-alb/1234567890abcdef \
  --query 'Attributes[?contains(Key, `access_logs`)]'
```

### Tags Management

```bash
# Add tags to load balancer
aws elbv2 add-tags \
  --resource-arns arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/my-alb/1234567890abcdef \
  --tags Key=Environment,Value=Production Key=Owner,Value=TeamA Key=CostCenter,Value=12345

# Add tags to multiple resources
aws elbv2 add-tags \
  --resource-arns \
    arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/my-alb/1234567890abcdef \
    arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-targets/1234567890abcdef \
  --tags Key=Project,Value=WebApp Key=Version,Value=2.0

# Describe tags
aws elbv2 describe-tags \
  --resource-arns arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/my-alb/1234567890abcdef

# Remove tags from load balancer
aws elbv2 remove-tags \
  --resource-arns arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/my-alb/1234567890abcdef \
  --tag-keys Environment Owner
```

### Load Balancer Attributes

```bash
# Get all load balancer attributes
aws elbv2 describe-load-balancer-attributes \
  --load-balancer-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/my-alb/1234567890abcdef

# Get target group attributes
aws elbv2 describe-target-group-attributes \
  --target-group-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-targets/1234567890abcdef

# Enable HTTP/2 and HTTP desync mitigation
aws elbv2 modify-load-balancer-attributes \
  --load-balancer-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/my-alb/1234567890abcdef \
  --attributes \
    Key=routing.http2.enabled,Value=true \
    Key=routing.http.desync_mitigation_mode,Value=defensive

# Configure timeout and keep-alive settings
aws elbv2 modify-load-balancer-attributes \
  --load-balancer-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/my-alb/1234567890abcdef \
  --attributes \
    Key=idle_timeout.timeout_seconds,Value=120 \
    Key=routing.http.x_amzn_tls_version_and_cipher_suite.enabled,Value=true
```

### Cross-Zone Load Balancing

```bash
# Enable cross-zone load balancing for NLB (disabled by default)
aws elbv2 modify-load-balancer-attributes \
  --load-balancer-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/net/my-nlb/1234567890abcdef \
  --attributes Key=load_balancing.cross_zone.enabled,Value=true

# Disable cross-zone load balancing
aws elbv2 modify-load-balancer-attributes \
  --load-balancer-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/net/my-nlb/1234567890abcdef \
  --attributes Key=load_balancing.cross_zone.enabled,Value=false

# Enable cross-zone for target group (ALB)
aws elbv2 modify-target-group-attributes \
  --target-group-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-targets/1234567890abcdef \
  --attributes Key=load_balancing.cross_zone.enabled,Value=use_load_balancer_configuration
```

### Connection Draining / Deregistration Delay

```bash
# Set deregistration delay to 30 seconds
aws elbv2 modify-target-group-attributes \
  --target-group-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-targets/1234567890abcdef \
  --attributes Key=deregistration_delay.timeout_seconds,Value=30

# Set longer deregistration delay for long-running connections
aws elbv2 modify-target-group-attributes \
  --target-group-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-targets/1234567890abcdef \
  --attributes Key=deregistration_delay.timeout_seconds,Value=300

# Configure connection termination for NLB
aws elbv2 modify-target-group-attributes \
  --target-group-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-tcp-targets/1234567890abcdef \
  --attributes \
    Key=deregistration_delay.timeout_seconds,Value=120 \
    Key=deregistration_delay.connection_termination.enabled,Value=true
```

### Monitoring and Metrics

```bash
# Get CloudWatch metrics for load balancer
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApplicationELB \
  --metric-name RequestCount \
  --dimensions Name=LoadBalancer,Value=app/my-alb/1234567890abcdef \
  --start-time 2026-02-08T00:00:00Z \
  --end-time 2026-02-08T23:59:59Z \
  --period 3600 \
  --statistics Sum

# Get target response time metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApplicationELB \
  --metric-name TargetResponseTime \
  --dimensions Name=LoadBalancer,Value=app/my-alb/1234567890abcdef \
  --start-time 2026-02-08T00:00:00Z \
  --end-time 2026-02-08T23:59:59Z \
  --period 300 \
  --statistics Average,Maximum

# Get unhealthy target count
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApplicationELB \
  --metric-name UnHealthyHostCount \
  --dimensions \
    Name=LoadBalancer,Value=app/my-alb/1234567890abcdef \
    Name=TargetGroup,Value=targetgroup/my-targets/1234567890abcdef \
  --start-time 2026-02-08T00:00:00Z \
  --end-time 2026-02-08T23:59:59Z \
  --period 300 \
  --statistics Maximum
```

### Useful Query and Filter Examples

```bash
# List all ALBs with their DNS names
aws elbv2 describe-load-balancers \
  --query 'LoadBalancers[?Type==`application`].[LoadBalancerName,DNSName,State.Code]' \
  --output table

# List all NLBs
aws elbv2 describe-load-balancers \
  --query 'LoadBalancers[?Type==`network`].[LoadBalancerName,DNSName]' \
  --output table

# Get load balancers by tag
aws elbv2 describe-load-balancers \
  --query 'LoadBalancers[*].LoadBalancerArn' \
  --output text | xargs -I {} aws elbv2 describe-tags --resource-arns {} \
  --query 'TagDescriptions[?Tags[?Key==`Environment`&&Value==`Production`]].ResourceArn' \
  --output text

# List all target groups with health check settings
aws elbv2 describe-target-groups \
  --query 'TargetGroups[*].[TargetGroupName,Protocol,Port,HealthCheckPath,HealthCheckIntervalSeconds]' \
  --output table

# Find unhealthy targets across all target groups
aws elbv2 describe-target-groups \
  --query 'TargetGroups[*].TargetGroupArn' \
  --output text | xargs -n1 aws elbv2 describe-target-health --target-group-arn | \
  jq '.TargetHealthDescriptions[] | select(.TargetHealth.State != "healthy")'

# Get all listeners for a load balancer with their rules count
aws elbv2 describe-listeners \
  --load-balancer-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/my-alb/1234567890abcdef \
  --query 'Listeners[*].[Protocol,Port,ListenerArn]' \
  --output table

# Export load balancer configuration to JSON
aws elbv2 describe-load-balancers \
  --load-balancer-arns arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/my-alb/1234567890abcdef \
  > my-alb-config.json

# Get all target groups and their stickiness settings
aws elbv2 describe-target-group-attributes \
  --target-group-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-targets/1234567890abcdef \
  --query 'Attributes[?contains(Key, `stickiness`)]' \
  --output table
```

### Batch Operations and Automation

```bash
# Create complete ALB setup with target group and listener
# Step 1: Create target group
TARGET_GROUP_ARN=$(aws elbv2 create-target-group \
  --name my-web-targets \
  --protocol HTTP \
  --port 80 \
  --vpc-id vpc-12345678 \
  --health-check-path /health \
  --query 'TargetGroups[0].TargetGroupArn' \
  --output text)

# Step 2: Create load balancer
LOAD_BALANCER_ARN=$(aws elbv2 create-load-balancer \
  --name my-web-alb \
  --subnets subnet-12345678 subnet-87654321 \
  --security-groups sg-12345678 \
  --tags Key=Environment,Value=Production \
  --query 'LoadBalancers[0].LoadBalancerArn' \
  --output text)

# Step 3: Create HTTP listener with redirect to HTTPS
aws elbv2 create-listener \
  --load-balancer-arn $LOAD_BALANCER_ARN \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=redirect,RedirectConfig="{Protocol=HTTPS,Port=443,StatusCode=HTTP_301}"

# Step 4: Create HTTPS listener
LISTENER_ARN=$(aws elbv2 create-listener \
  --load-balancer-arn $LOAD_BALANCER_ARN \
  --protocol HTTPS \
  --port 443 \
  --certificates CertificateArn=arn:aws:acm:us-east-1:123456789012:certificate/12345678 \
  --ssl-policy ELBSecurityPolicy-TLS-1-2-2017-01 \
  --default-actions Type=forward,TargetGroupArn=$TARGET_GROUP_ARN \
  --query 'Listeners[0].ListenerArn' \
  --output text)

# Step 5: Register targets
aws elbv2 register-targets \
  --target-group-arn $TARGET_GROUP_ARN \
  --targets Id=i-12345678 Id=i-87654321

# Step 6: Enable access logs
aws elbv2 modify-load-balancer-attributes \
  --load-balancer-arn $LOAD_BALANCER_ARN \
  --attributes \
    Key=access_logs.s3.enabled,Value=true \
    Key=access_logs.s3.bucket,Value=my-logs \
    Key=deletion_protection.enabled,Value=true

echo "ALB Setup Complete!"
echo "Load Balancer ARN: $LOAD_BALANCER_ARN"
echo "Target Group ARN: $TARGET_GROUP_ARN"
echo "Listener ARN: $LISTENER_ARN"

# Delete complete ALB setup (cleanup)
# Note: Delete in reverse order
aws elbv2 delete-listener --listener-arn $LISTENER_ARN
aws elbv2 delete-load-balancer --load-balancer-arn $LOAD_BALANCER_ARN
aws elbv2 delete-target-group --target-group-arn $TARGET_GROUP_ARN
```

### Advanced Scenarios

```bash
# Blue-Green Deployment with weighted target groups
# Create blue target group
BLUE_TG=$(aws elbv2 create-target-group \
  --name blue-targets \
  --protocol HTTP \
  --port 80 \
  --vpc-id vpc-12345678 \
  --query 'TargetGroups[0].TargetGroupArn' \
  --output text)

# Create green target group
GREEN_TG=$(aws elbv2 create-target-group \
  --name green-targets \
  --protocol HTTP \
  --port 80 \
  --vpc-id vpc-12345678 \
  --query 'TargetGroups[0].TargetGroupArn' \
  --output text)

# Create listener with 90/10 traffic split
aws elbv2 create-listener \
  --load-balancer-arn $LOAD_BALANCER_ARN \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=forward,ForwardConfig="{TargetGroups=[{TargetGroupArn=$BLUE_TG,Weight=90},{TargetGroupArn=$GREEN_TG,Weight=10}]}"

# Gradually shift traffic to green (canary deployment)
# Update to 50/50
aws elbv2 modify-listener \
  --listener-arn $LISTENER_ARN \
  --default-actions Type=forward,ForwardConfig="{TargetGroups=[{TargetGroupArn=$BLUE_TG,Weight=50},{TargetGroupArn=$GREEN_TG,Weight=50}]}"

# Complete migration to green
aws elbv2 modify-listener \
  --listener-arn $LISTENER_ARN \
  --default-actions Type=forward,ForwardConfig="{TargetGroups=[{TargetGroupArn=$GREEN_TG,Weight=100}]}"

# Multi-region failover with Route 53 health checks
# Create health check for ALB
aws route53 create-health-check \
  --caller-reference $(date +%s) \
  --health-check-config \
    Type=HTTPS_STR_MATCH,\
    ResourcePath=/health,\
    FullyQualifiedDomainName=my-alb-123456.us-east-1.elb.amazonaws.com,\
    Port=443,\
    RequestInterval=30,\
    FailureThreshold=3,\
    SearchString=healthy
```

These CLI commands provide comprehensive coverage for managing AWS Elastic Load Balancers. Remember to replace placeholder ARNs, IDs, and names with your actual values.

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