# AWS Global Accelerator Guide for SAA-C03 Certification

## Table of Contents
1. [Overview](#overview)
2. [Key Concepts](#key-concepts)
3. [Architecture and Components](#architecture-and-components)
4. [How Global Accelerator Works](#how-global-accelerator-works)
5. [Configuration and Setup](#configuration-and-setup)
6. [Use Cases](#use-cases)
7. [Benefits](#benefits)
8. [Pricing](#pricing)
9. [Monitoring and Logging](#monitoring-and-logging)
10. [Security](#security)
11. [Best Practices](#best-practices)
12. [Global Accelerator vs CloudFront](#global-accelerator-vs-cloudfront)
13. [Global Accelerator vs Application Load Balancer](#global-accelerator-vs-alb)
14. [Exam Tips for SAA-C03](#exam-tips-for-saa-c03)
15. [Common Exam Scenarios](#common-exam-scenarios)
16. [AWS CLI Commands Reference](#aws-cli-commands-reference)
17. [Hands-On Labs](#hands-on-labs)

---

## Overview

**AWS Global Accelerator** is a networking service that helps you improve the availability and performance of your applications by routing traffic through the AWS global network infrastructure. It provides static IP addresses that act as a fixed entry point to your applications hosted in one or multiple AWS Regions.

### Key Features
- **Static IP Addresses**: Two static anycast IP addresses that serve as entry points
- **Global Network**: Leverages AWS's private global network for faster routing
- **Traffic Routing**: Intelligent traffic routing based on health and performance
- **DDoS Protection**: Built-in DDoS protection at the network and transport layers
- **Health Checks**: Continuous health monitoring of endpoints

---

## Key Concepts

### 1. Accelerator
An accelerator directs traffic to optimal endpoints over the AWS global network to improve availability and performance of your internet applications.

### 2. Listener
A listener processes inbound connections from clients to Global Accelerator, based on the port (or port range) and protocol that you configure.

### 3. Endpoint Group
Each listener has one or more endpoint groups associated with it, and traffic is distributed to endpoints in the group according to configuration options.

### 4. Endpoint
Endpoints can be Network Load Balancers, Application Load Balancers, Amazon EC2 instances, or Elastic IP addresses.

### 5. Anycast IP Address
A network addressing and routing methodology where datagrams from a single sender are routed to the topologically nearest node in a group of potential receivers.

---

## Architecture and Components

```
Internet Users
      ↓
   Anycast IPs (2 static IPs)
      ↓
AWS Global Network Edge Locations
      ↓
   AWS Backbone Network
      ↓
Target Endpoints (ALB, NLB, EC2, EIP)
```

### Components Breakdown

#### 1. Edge Locations
- Global Accelerator uses AWS's network of edge locations
- Traffic enters the AWS network at the closest edge location
- Reduces latency by minimizing the distance traffic travels over the internet

#### 2. Anycast IP Addresses
- Two static IP addresses provided per accelerator
- Same IP addresses announced from multiple edge locations
- Traffic automatically routed to the nearest healthy endpoint

#### 3. Listeners
- Define the port and protocol for connections
- Support TCP and UDP protocols
- Can configure multiple listeners per accelerator

#### 4. Endpoint Groups
- Contain one or more endpoints
- Associated with specific AWS regions
- Traffic distribution controlled by traffic dials and weights

---

## How Global Accelerator Works

### Traffic Flow Process

1. **Client Connection**: Client connects to one of the anycast IP addresses
2. **Edge Location Entry**: Traffic enters AWS network at the nearest edge location
3. **AWS Backbone Routing**: Traffic routed over AWS's private network
4. **Health Check Evaluation**: Global Accelerator evaluates endpoint health
5. **Optimal Routing**: Traffic directed to the best performing healthy endpoint
6. **Response Path**: Response follows the same optimized path back to client

### Traffic Distribution

#### Traffic Dials
- Control the percentage of traffic directed to each endpoint group
- Range from 0 to 100 percent
- Useful for blue/green deployments and gradual traffic shifting

#### Endpoint Weights
- Control traffic distribution within an endpoint group
- Range from 0 to 255
- Higher weights receive more traffic proportionally

---

## Configuration and Setup

### Creating a Global Accelerator

#### Step 1: Create Accelerator
```json
{
  "Name": "MyWebAppAccelerator",
  "IpAddressType": "IPV4",
  "Enabled": true,
  "Attributes": {
    "FlowLogsEnabled": true,
    "FlowLogsS3Bucket": "my-global-accelerator-logs",
    "FlowLogsS3Prefix": "flow-logs/"
  }
}
```

#### Step 2: Configure Listener
```json
{
  "Protocol": "TCP",
  "PortRanges": [
    {
      "FromPort": 80,
      "ToPort": 80
    },
    {
      "FromPort": 443,
      "ToPort": 443
    }
  ]
}
```

#### Step 3: Create Endpoint Group
```json
{
  "Region": "us-west-2",
  "TrafficDialPercentage": 100,
  "HealthCheckIntervalSeconds": 30,
  "HealthCheckPath": "/health",
  "HealthCheckProtocol": "HTTP",
  "HealthyThresholdCount": 3,
  "UnhealthyThresholdCount": 3
}
```

#### Step 4: Add Endpoints
```json
{
  "EndpointConfigurations": [
    {
      "EndpointId": "arn:aws:elasticloadbalancing:us-west-2:123456789012:loadbalancer/app/my-load-balancer/50dc6c495c0c9188",
      "Weight": 100,
      "ClientIPPreservationEnabled": true
    }
  ]
}
```

### AWS CLI Examples

#### Create Accelerator
```bash
aws globalaccelerator create-accelerator \
  --name MyWebAppAccelerator \
  --ip-address-type IPV4 \
  --enabled
```

#### Create Listener
```bash
aws globalaccelerator create-listener \
  --accelerator-arn arn:aws:globalaccelerator::123456789012:accelerator/1234abcd-abcd-1234-abcd-1234abcdefgh \
  --protocol TCP \
  --port-ranges FromPort=80,ToPort=80 FromPort=443,ToPort=443
```

---

## Use Cases

### 1. Global Applications
- Multi-region applications requiring global reach
- Consistent performance across different geographic locations
- Applications with users distributed worldwide

### 2. Gaming Applications
- Real-time multiplayer games
- Low-latency requirements
- UDP traffic optimization

### 3. IoT Applications
- Device connections from various global locations
- Reliable connectivity for IoT devices
- Support for both TCP and UDP protocols

### 4. VoIP and Media Streaming
- Real-time communication applications
- Media streaming services
- Applications requiring consistent jitter and packet loss

### 5. Financial Trading Applications
- High-frequency trading platforms
- Applications requiring minimal latency
- Global financial services

---

## Benefits

### 1. Improved Performance
- **Up to 60% performance improvement** for many applications
- Reduces latency by routing traffic over AWS's optimized network
- Eliminates inconsistent internet routing

### 2. Increased Availability
- **Automatic failover** between healthy endpoints
- Multi-region redundancy
- Continuous health monitoring

### 3. Enhanced Security
- **Built-in DDoS protection** at network and transport layers
- AWS Shield Standard included
- Can integrate with AWS Shield Advanced

### 4. Simplified Management
- **Static IP addresses** eliminate DNS propagation issues
- Easy traffic management with traffic dials
- Simplified endpoint management

### 5. Global Reach
- Leverages AWS's global network of edge locations
- Consistent performance regardless of user location
- Reduced complexity for global deployments

---

## Pricing

### Cost Components

#### 1. Fixed Fee
- **$0.025 per hour** per accelerator
- Charged regardless of traffic volume
- Billed per second with 1-hour minimum

#### 2. Data Transfer Pricing
- **Premium tier**: $0.015 per GB for the first 10 TB per month
- **Standard tier**: Varies by region, typically $0.09-$0.23 per GB
- Additional volume discounts available

#### 3. DRT (DDoS Response Team) Fee
- Only applicable if using AWS Shield Advanced
- $3,000 per month per organization

### Cost Optimization Tips
- Use traffic dials to gradually migrate traffic
- Monitor data transfer costs across regions
- Consider Regional optimization for cost savings

---

## Monitoring and Logging

### CloudWatch Metrics

#### Accelerator-Level Metrics
- `NewFlowCount`: Number of new flows created
- `ProcessedBytesIn`: Bytes processed inbound
- `ProcessedBytesOut`: Bytes processed outbound

#### Endpoint-Level Metrics
- `AwsApiCallCount`: Number of AWS API calls
- `ErrorCount`: Number of errors
- `HealthyEndpointCount`: Number of healthy endpoints

### Flow Logs
```json
{
  "version": "1.0",
  "account_id": "123456789012",
  "accelerator_id": "1234abcd-abcd-1234-abcd-1234abcdefgh",
  "client_ip": "198.51.100.1",
  "client_port": 12345,
  "accelerator_ip": "192.0.2.1",
  "accelerator_port": 80,
  "endpoint_ip": "10.0.1.100",
  "endpoint_port": 80,
  "protocol": "TCP",
  "ip_address_type": "IPv4",
  "packets": 15,
  "bytes": 1500,
  "start_time": "1566848875",
  "end_time": "1566848933"
}
```

### Health Check Monitoring
- Configure health check intervals (10 or 30 seconds)
- Set healthy/unhealthy thresholds
- Monitor endpoint health status in CloudWatch

---

## Security

### Network Security

#### DDoS Protection
- **AWS Shield Standard**: Included automatically
- Protection against common network and transport layer attacks
- Automatic detection and mitigation

#### AWS Shield Advanced Integration
- Advanced DDoS protection for Global Accelerator
- 24/7 access to DDoS Response Team (DRT)
- Cost protection against DDoS-related scaling charges

### Access Control

#### IAM Policies
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "globalaccelerator:Describe*",
        "globalaccelerator:List*"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "globalaccelerator:Create*",
        "globalaccelerator:Update*",
        "globalaccelerator:Delete*"
      ],
      "Resource": "arn:aws:globalaccelerator:*:*:accelerator/*",
      "Condition": {
        "StringEquals": {
          "aws:RequestedRegion": "us-west-2"
        }
      }
    }
  ]
}
```

### Client IP Preservation
- Maintain original client IP addresses
- Important for security logging and analytics
- Supported for Application Load Balancer endpoints

---

## Best Practices

### 1. Architecture Design
- **Use multiple regions** for high availability
- **Implement health checks** for all endpoints
- **Configure appropriate traffic dials** for gradual rollouts

### 2. Performance Optimization
- **Place endpoints close to users** when possible
- **Use appropriate instance types** for your workload
- **Monitor CloudWatch metrics** regularly

### 3. Security Best Practices
- **Enable flow logs** for traffic analysis
- **Use IAM roles** instead of access keys
- **Implement least privilege** access policies

### 4. Cost Management
- **Monitor data transfer costs** across regions
- **Use traffic dials** to optimize traffic distribution
- **Review pricing tiers** regularly

### 5. Operational Excellence
- **Automate deployment** using CloudFormation or Terraform
- **Set up monitoring and alerting**
- **Document configuration changes**

---

## Global Accelerator vs CloudFront

| Aspect | Global Accelerator | CloudFront |
|--------|-------------------|------------|
| **Purpose** | Network acceleration for any TCP/UDP traffic | Content delivery and caching |
| **Protocol Support** | TCP, UDP | HTTP, HTTPS, WebSocket |
| **Caching** | No caching | Edge caching |
| **IP Addresses** | Static anycast IPs | Dynamic IP addresses |
| **Use Cases** | Gaming, IoT, real-time apps | Web content, APIs, video streaming |
| **Performance Gain** | 60% improvement via AWS backbone | Varies based on cache hit ratio |
| **Geographic Distribution** | Global anycast network | Regional edge locations |
| **DDoS Protection** | Network and transport layer | Application layer + network layer |

### When to Use Global Accelerator
- Non-HTTP protocols (TCP/UDP)
- Gaming applications
- IoT applications requiring UDP
- Applications needing static IP addresses
- Real-time applications sensitive to jitter

### When to Use CloudFront
- HTTP/HTTPS traffic
- Static content delivery
- Dynamic content with caching benefits
- APIs that can benefit from edge caching
- Video streaming applications

---

## Global Accelerator vs Application Load Balancer

| Aspect | Global Accelerator | Application Load Balancer |
|--------|-------------------|---------------------------|
| **Scope** | Global traffic routing | Regional load balancing |
| **Layer** | Network Layer (Layer 4) | Application Layer (Layer 7) |
| **Protocol Support** | TCP, UDP | HTTP, HTTPS, gRPC |
| **Routing** | Based on geography and health | Based on content, headers, paths |
| **Static IPs** | Yes (2 anycast IPs) | No (dynamic DNS) |
| **Cross-Region** | Yes | No (single region) |
| **Advanced Routing** | Basic (health, geography) | Advanced (path, host, header-based) |

### Complementary Usage
- Use **Global Accelerator** to route traffic to the optimal region
- Use **ALB as endpoints** within each region for application-level routing
- Common pattern: Global Accelerator → Regional ALBs → Target instances

---

## Exam Tips for SAA-C03

### Key Points to Remember

1. **Static IP Addresses**
   - Global Accelerator provides 2 static anycast IP addresses
   - These IPs don't change even if you modify your backend infrastructure
   - Eliminates DNS propagation delays

2. **Performance Improvement**
   - Can improve performance by up to 60%
   - Uses AWS global network backbone
   - Reduces latency by entering AWS network at nearest edge location

3. **Protocol Support**
   - Supports both TCP and UDP
   - Unlike CloudFront which only supports HTTP/HTTPS
   - Ideal for gaming, IoT, and real-time applications

4. **Health Checks**
   - Automatic failover to healthy endpoints
   - Configurable health check parameters
   - Supports path-based health checks for HTTP endpoints

5. **DDoS Protection**
   - Built-in AWS Shield Standard protection
   - Can integrate with AWS Shield Advanced
   - Protection at network and transport layers

### Common Misconceptions
- ❌ Global Accelerator caches content (it doesn't - that's CloudFront)
- ❌ Only works with HTTP traffic (supports TCP/UDP)
- ❌ Replaces load balancers (complements them)
- ❌ More expensive than CloudFront (pricing depends on use case)

---

## Common Exam Scenarios

### Scenario 1: Global Gaming Application
**Question**: Your company has a real-time multiplayer gaming application with users worldwide. The application uses UDP protocol and requires low latency. What AWS service would best improve performance?

**Answer**: AWS Global Accelerator
- Supports UDP protocol (CloudFront doesn't)
- Provides up to 60% performance improvement
- Uses AWS global network for optimal routing
- Static anycast IPs eliminate DNS propagation delays

### Scenario 2: Multi-Region Failover
**Question**: You need to route traffic between multiple regions based on health status and want to use static IP addresses for your application endpoints. Which service should you use?

**Answer**: AWS Global Accelerator
- Provides automatic failover between regions
- Offers static anycast IP addresses
- Continuous health monitoring of endpoints
- Intelligent traffic routing based on health and performance

### Scenario 3: IoT Application with UDP Traffic
**Question**: Your IoT application receives data from millions of devices worldwide using UDP protocol. You need to improve reliability and reduce latency. What solution would you recommend?

**Answer**: AWS Global Accelerator
- Supports UDP protocol for IoT communications
- Global anycast network improves reliability
- Reduces latency by routing traffic over AWS backbone
- Built-in DDoS protection for device communications

### Scenario 4: Financial Trading Platform
**Question**: A financial trading platform requires the lowest possible latency for global users and needs to maintain consistent IP addresses for firewall configurations. Which AWS service meets these requirements?

**Answer**: AWS Global Accelerator
- Minimizes latency using AWS global network
- Provides static IP addresses for firewall whitelisting
- Optimized routing for performance-critical applications
- Suitable for TCP traffic used in financial applications

### Scenario 5: Blue/Green Deployment
**Question**: You want to perform a blue/green deployment across multiple regions with the ability to gradually shift traffic between environments. What AWS service feature would you use?

**Answer**: Global Accelerator Traffic Dials
- Control traffic percentage to each endpoint group
- Gradual traffic shifting from 0% to 100%
- Instant rollback capability
- Zero-downtime deployments

---

## AWS CLI Commands Reference

### Create Accelerator

```bash
# Create a standard accelerator
aws globalaccelerator create-accelerator \
    --name MyAccelerator \
    --ip-address-type IPV4 \
    --enabled \
    --tags Key=Environment,Value=Production Key=Application,Value=WebApp

# Create accelerator with specific IP addresses (BYOIP)
aws globalaccelerator create-accelerator \
    --name CustomIPAccelerator \
    --ip-addresses 203.0.113.1 203.0.113.2 \
    --enabled

# Create dual-stack accelerator (IPv4 and IPv6)
aws globalaccelerator create-accelerator \
    --name DualStackAccelerator \
    --ip-address-type DUAL_STACK \
    --enabled

# Describe accelerators
aws globalaccelerator list-accelerators

# Describe specific accelerator
aws globalaccelerator describe-accelerator \
    --accelerator-arn arn:aws:globalaccelerator::123456789012:accelerator/abcd1234-abcd-1234-abcd-1234567890ab

# Describe accelerator attributes
aws globalaccelerator describe-accelerator-attributes \
    --accelerator-arn arn:aws:globalaccelerator::123456789012:accelerator/abcd1234-abcd-1234-abcd-1234567890ab
```

### Update Accelerator Attributes

```bash
# Enable flow logs
aws globalaccelerator update-accelerator-attributes \
    --accelerator-arn arn:aws:globalaccelerator::123456789012:accelerator/abcd1234-abcd-1234-abcd-1234567890ab \
    --flow-logs-enabled \
    --flow-logs-s3-bucket my-flow-logs-bucket \
    --flow-logs-s3-prefix globalaccelerator/

# Disable flow logs
aws globalaccelerator update-accelerator-attributes \
    --accelerator-arn arn:aws:globalaccelerator::123456789012:accelerator/abcd1234-abcd-1234-abcd-1234567890ab \
    --no-flow-logs-enabled

# Update accelerator name
aws globalaccelerator update-accelerator \
    --accelerator-arn arn:aws:globalaccelerator::123456789012:accelerator/abcd1234-abcd-1234-abcd-1234567890ab \
    --name UpdatedAcceleratorName

# Disable accelerator
aws globalaccelerator update-accelerator \
    --accelerator-arn arn:aws:globalaccelerator::123456789012:accelerator/abcd1234-abcd-1234-abcd-1234567890ab \
    --no-enabled

# Enable accelerator
aws globalaccelerator update-accelerator \
    --accelerator-arn arn:aws:globalaccelerator::123456789012:accelerator/abcd1234-abcd-1234-abcd-1234567890ab \
    --enabled
```

### Create Listeners

```bash
# Create TCP listener
aws globalaccelerator create-listener \
    --accelerator-arn arn:aws:globalaccelerator::123456789012:accelerator/abcd1234-abcd-1234-abcd-1234567890ab \
    --protocol TCP \
    --port-ranges FromPort=80,ToPort=80 FromPort=443,ToPort=443 \
    --client-affinity SOURCE_IP

# Create UDP listener
aws globalaccelerator create-listener \
    --accelerator-arn arn:aws:globalaccelerator::123456789012:accelerator/abcd1234-abcd-1234-abcd-1234567890ab \
    --protocol UDP \
    --port-ranges FromPort=53,ToPort=53 \
    --client-affinity NONE

# Create listener with port range
aws globalaccelerator create-listener \
    --accelerator-arn arn:aws:globalaccelerator::123456789012:accelerator/abcd1234-abcd-1234-abcd-1234567890ab \
    --protocol TCP \
    --port-ranges FromPort=8000,ToPort=8100 \
    --client-affinity SOURCE_IP

# List listeners
aws globalaccelerator list-listeners \
    --accelerator-arn arn:aws:globalaccelerator::123456789012:accelerator/abcd1234-abcd-1234-abcd-1234567890ab

# Describe listener
aws globalaccelerator describe-listener \
    --listener-arn arn:aws:globalaccelerator::123456789012:accelerator/abcd1234-abcd-1234-abcd-1234567890ab/listener/0123wxyz

# Update listener
aws globalaccelerator update-listener \
    --listener-arn arn:aws:globalaccelerator::123456789012:accelerator/abcd1234-abcd-1234-abcd-1234567890ab/listener/0123wxyz \
    --port-ranges FromPort=80,ToPort=80 FromPort=443,ToPort=443 FromPort=8080,ToPort=8080 \
    --client-affinity SOURCE_IP
```

### Create Endpoint Groups

```bash
# Create endpoint group in us-east-1
aws globalaccelerator create-endpoint-group \
    --listener-arn arn:aws:globalaccelerator::123456789012:accelerator/abcd1234-abcd-1234-abcd-1234567890ab/listener/0123wxyz \
    --endpoint-group-region us-east-1 \
    --traffic-dial-percentage 100 \
    --health-check-interval-seconds 30 \
    --health-check-path "/health" \
    --health-check-protocol HTTP \
    --health-check-port 80 \
    --threshold-count 3

# Create endpoint group with custom health check
aws globalaccelerator create-endpoint-group \
    --listener-arn arn:aws:globalaccelerator::123456789012:accelerator/abcd1234-abcd-1234-abcd-1234567890ab/listener/0123wxyz \
    --endpoint-group-region us-west-2 \
    --traffic-dial-percentage 50 \
    --health-check-interval-seconds 10 \
    --health-check-path "/api/health" \
    --health-check-protocol HTTPS \
    --health-check-port 443 \
    --threshold-count 2

# Create endpoint group with port override
aws globalaccelerator create-endpoint-group \
    --listener-arn arn:aws:globalaccelerator::123456789012:accelerator/abcd1234-abcd-1234-abcd-1234567890ab/listener/0123wxyz \
    --endpoint-group-region eu-west-1 \
    --port-overrides ListenerPort=80,EndpointPort=8080 ListenerPort=443,EndpointPort=8443

# List endpoint groups
aws globalaccelerator list-endpoint-groups \
    --listener-arn arn:aws:globalaccelerator::123456789012:accelerator/abcd1234-abcd-1234-abcd-1234567890ab/listener/0123wxyz

# Describe endpoint group
aws globalaccelerator describe-endpoint-group \
    --endpoint-group-arn arn:aws:globalaccelerator::123456789012:accelerator/abcd1234-abcd-1234-abcd-1234567890ab/listener/0123wxyz/endpoint-group/ab12cd34

# Update endpoint group traffic dial
aws globalaccelerator update-endpoint-group \
    --endpoint-group-arn arn:aws:globalaccelerator::123456789012:accelerator/abcd1234-abcd-1234-abcd-1234567890ab/listener/0123wxyz/endpoint-group/ab12cd34 \
    --traffic-dial-percentage 75
```

### Add Endpoints

```bash
# Add ALB endpoint
aws globalaccelerator update-endpoint-group \
    --endpoint-group-arn arn:aws:globalaccelerator::123456789012:accelerator/abcd1234-abcd-1234-abcd-1234567890ab/listener/0123wxyz/endpoint-group/ab12cd34 \
    --endpoint-configurations \
        EndpointId=arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/my-alb/1234567890abcdef,Weight=128,ClientIPPreservationEnabled=true

# Add NLB endpoint
aws globalaccelerator update-endpoint-group \
    --endpoint-group-arn arn:aws:globalaccelerator::123456789012:accelerator/abcd1234-abcd-1234-abcd-1234567890ab/listener/0123wxyz/endpoint-group/ab12cd34 \
    --endpoint-configurations \
        EndpointId=arn:aws:elasticloadbalancing:us-west-2:123456789012:loadbalancer/net/my-nlb/abcdef1234567890,Weight=128,ClientIPPreservationEnabled=true

# Add EC2 instance endpoint
aws globalaccelerator update-endpoint-group \
    --endpoint-group-arn arn:aws:globalaccelerator::123456789012:accelerator/abcd1234-abcd-1234-abcd-1234567890ab/listener/0123wxyz/endpoint-group/ab12cd34 \
    --endpoint-configurations \
        EndpointId=i-0a1b2c3d4e5f6g7h8,Weight=128,ClientIPPreservationEnabled=false

# Add Elastic IP endpoint
aws globalaccelerator update-endpoint-group \
    --endpoint-group-arn arn:aws:globalaccelerator::123456789012:accelerator/abcd1234-abcd-1234-abcd-1234567890ab/listener/0123wxyz/endpoint-group/ab12cd34 \
    --endpoint-configurations \
        EndpointId=arn:aws:ec2:us-east-1:123456789012:eip-allocation/eipalloc-0a1b2c3d4e5f6g7h8,Weight=128

# Add multiple endpoints with different weights
aws globalaccelerator update-endpoint-group \
    --endpoint-group-arn arn:aws:globalaccelerator::123456789012:accelerator/abcd1234-abcd-1234-abcd-1234567890ab/listener/0123wxyz/endpoint-group/ab12cd34 \
    --endpoint-configurations \
        EndpointId=arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/alb-1/1234567890abcdef,Weight=200,ClientIPPreservationEnabled=true \
        EndpointId=arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/alb-2/abcdef1234567890,Weight=56,ClientIPPreservationEnabled=true
```

### Custom Routing Accelerator

```bash
# Create custom routing accelerator
aws globalaccelerator create-custom-routing-accelerator \
    --name CustomRoutingAccelerator \
    --ip-address-type IPV4 \
    --enabled \
    --tags Key=Type,Value=CustomRouting

# Create custom routing listener
aws globalaccelerator create-custom-routing-listener \
    --accelerator-arn arn:aws:globalaccelerator::123456789012:accelerator/abcd1234-abcd-1234-abcd-1234567890ab \
    --port-ranges FromPort=5000,ToPort=10000

# Create custom routing endpoint group
aws globalaccelerator create-custom-routing-endpoint-group \
    --listener-arn arn:aws:globalaccelerator::123456789012:accelerator/abcd1234-abcd-1234-abcd-1234567890ab/listener/0123wxyz \
    --endpoint-group-region us-east-1 \
    --destination-configurations \
        FromPort=80,ToPort=80,Protocols=TCP \
        FromPort=443,ToPort=443,Protocols=TCP

# Add custom routing endpoints
aws globalaccelerator add-custom-routing-endpoints \
    --endpoint-group-arn arn:aws:globalaccelerator::123456789012:accelerator/abcd1234-abcd-1234-abcd-1234567890ab/listener/0123wxyz/endpoint-group/ab12cd34 \
    --endpoint-configurations EndpointId=subnet-0a1b2c3d4e5f6g7h8

# Allow custom routing traffic
aws globalaccelerator allow-custom-routing-traffic \
    --endpoint-group-arn arn:aws:globalaccelerator::123456789012:accelerator/abcd1234-abcd-1234-abcd-1234567890ab/listener/0123wxyz/endpoint-group/ab12cd34 \
    --endpoint-id subnet-0a1b2c3d4e5f6g7h8 \
    --allow-all-traffic-to-endpoint

# Deny custom routing traffic
aws globalaccelerator deny-custom-routing-traffic \
    --endpoint-group-arn arn:aws:globalaccelerator::123456789012:accelerator/abcd1234-abcd-1234-abcd-1234567890ab/listener/0123wxyz/endpoint-group/ab12cd34 \
    --endpoint-id subnet-0a1b2c3d4e5f6g7h8 \
    --deny-all-traffic-to-endpoint

# List custom routing accelerators
aws globalaccelerator list-custom-routing-accelerators

# Describe custom routing accelerator
aws globalaccelerator describe-custom-routing-accelerator \
    --accelerator-arn arn:aws:globalaccelerator::123456789012:accelerator/abcd1234-abcd-1234-abcd-1234567890ab
```

### Client Affinity

```bash
# Update listener to enable source IP affinity
aws globalaccelerator update-listener \
    --listener-arn arn:aws:globalaccelerator::123456789012:accelerator/abcd1234-abcd-1234-abcd-1234567890ab/listener/0123wxyz \
    --client-affinity SOURCE_IP

# Disable client affinity
aws globalaccelerator update-listener \
    --listener-arn arn:aws:globalaccelerator::123456789012:accelerator/abcd1234-abcd-1234-abcd-1234567890ab/listener/0123wxyz \
    --client-affinity NONE
```

### Health Checks

```bash
# Update endpoint group health check settings
aws globalaccelerator update-endpoint-group \
    --endpoint-group-arn arn:aws:globalaccelerator::123456789012:accelerator/abcd1234-abcd-1234-abcd-1234567890ab/listener/0123wxyz/endpoint-group/ab12cd34 \
    --health-check-interval-seconds 10 \
    --health-check-path "/healthcheck" \
    --health-check-protocol HTTPS \
    --health-check-port 443 \
    --threshold-count 2

# Disable health checks (use for static IP endpoints)
aws globalaccelerator update-endpoint-group \
    --endpoint-group-arn arn:aws:globalaccelerator::123456789012:accelerator/abcd1234-abcd-1234-abcd-1234567890ab/listener/0123wxyz/endpoint-group/ab12cd34 \
    --health-check-interval-seconds 30 \
    --threshold-count 3
```

### Traffic Dials

```bash
# Set traffic dial to 100% (full traffic)
aws globalaccelerator update-endpoint-group \
    --endpoint-group-arn arn:aws:globalaccelerator::123456789012:accelerator/abcd1234-abcd-1234-abcd-1234567890ab/listener/0123wxyz/endpoint-group/ab12cd34 \
    --traffic-dial-percentage 100

# Reduce traffic to 50% (blue/green deployment)
aws globalaccelerator update-endpoint-group \
    --endpoint-group-arn arn:aws:globalaccelerator::123456789012:accelerator/abcd1234-abcd-1234-abcd-1234567890ab/listener/0123wxyz/endpoint-group/ab12cd34 \
    --traffic-dial-percentage 50

# Set traffic to 0% (drain traffic)
aws globalaccelerator update-endpoint-group \
    --endpoint-group-arn arn:aws:globalaccelerator::123456789012:accelerator/abcd1234-abcd-1234-abcd-1234567890ab/listener/0123wxyz/endpoint-group/ab12cd34 \
    --traffic-dial-percentage 0

# Gradually increase traffic (canary deployment)
# Start with 10%
aws globalaccelerator update-endpoint-group \
    --endpoint-group-arn arn:aws:globalaccelerator::123456789012:accelerator/abcd1234-abcd-1234-abcd-1234567890ab/listener/0123wxyz/endpoint-group/ab12cd34 \
    --traffic-dial-percentage 10

# Then increase to 25%
aws globalaccelerator update-endpoint-group \
    --endpoint-group-arn arn:aws:globalaccelerator::123456789012:accelerator/abcd1234-abcd-1234-abcd-1234567890ab/listener/0123wxyz/endpoint-group/ab12cd34 \
    --traffic-dial-percentage 25
```

### Tags Management

```bash
# Tag accelerator
aws globalaccelerator tag-resource \
    --resource-arn arn:aws:globalaccelerator::123456789012:accelerator/abcd1234-abcd-1234-abcd-1234567890ab \
    --tags Key=Environment,Value=Production Key=CostCenter,Value=Engineering Key=Application,Value=WebPortal

# List tags
aws globalaccelerator list-tags-for-resource \
    --resource-arn arn:aws:globalaccelerator::123456789012:accelerator/abcd1234-abcd-1234-abcd-1234567890ab

# Remove tags
aws globalaccelerator untag-resource \
    --resource-arn arn:aws:globalaccelerator::123456789012:accelerator/abcd1234-abcd-1234-abcd-1234567890ab \
    --tag-keys Environment CostCenter
```

### Monitoring and Metrics

```bash
# Get CloudWatch metrics for processed bytes
aws cloudwatch get-metric-statistics \
    --namespace AWS/GlobalAccelerator \
    --metric-name ProcessedBytesIn \
    --dimensions Name=Accelerator,Value=abcd1234-abcd-1234-abcd-1234567890ab \
    --start-time 2026-02-07T00:00:00Z \
    --end-time 2026-02-08T00:00:00Z \
    --period 3600 \
    --statistics Sum \
    --unit Bytes

# Get new connections metric
aws cloudwatch get-metric-statistics \
    --namespace AWS/GlobalAccelerator \
    --metric-name NewFlowCount \
    --dimensions Name=Accelerator,Value=abcd1234-abcd-1234-abcd-1234567890ab \
    --start-time 2026-02-07T00:00:00Z \
    --end-time 2026-02-08T00:00:00Z \
    --period 300 \
    --statistics Sum

# Create alarm for unhealthy endpoints
aws cloudwatch put-metric-alarm \
    --alarm-name global-accelerator-unhealthy-endpoints \
    --alarm-description "Alert when endpoints are unhealthy" \
    --metric-name HealthyEndpointCount \
    --namespace AWS/GlobalAccelerator \
    --statistic Average \
    --period 300 \
    --threshold 1 \
    --comparison-operator LessThanThreshold \
    --evaluation-periods 2 \
    --dimensions Name=Accelerator,Value=abcd1234-abcd-1234-abcd-1234567890ab
```

### IP Address Management

```bash
# List IP sets for accelerator
aws globalaccelerator list-accelerators \
    --query 'Accelerators[?AcceleratorArn==`arn:aws:globalaccelerator::123456789012:accelerator/abcd1234-abcd-1234-abcd-1234567890ab`].IpSets'

# Advertise IP addresses (for BYOIP)
aws globalaccelerator advertise-byoip-cidr \
    --cidr 203.0.113.0/24

# Withdraw IP advertisement
aws globalaccelerator withdraw-byoip-cidr \
    --cidr 203.0.113.0/24

 # Provision BYOIP address range
aws globalaccelerator provision-byoip-cidr \
    --cidr 203.0.113.0/24 \
    --cidr-authorization-context \
        Message="Authorization message",\
        Signature="Signature from ROA"

# Deprovision BYOIP
aws globalaccelerator deprovision-byoip-cidr \
    --cidr 203.0.113.0/24

# List BYOIP CIDRs
aws globalaccelerator list-byoip-cidrs
```

### Delete Resources

```bash
# Remove endpoint from endpoint group
aws globalaccelerator update-endpoint-group \
    --endpoint-group-arn arn:aws:globalaccelerator::123456789012:accelerator/abcd1234-abcd-1234-abcd-1234567890ab/listener/0123wxyz/endpoint-group/ab12cd34 \
    --endpoint-configurations []

# Delete endpoint group
aws globalaccelerator delete-endpoint-group \
    --endpoint-group-arn arn:aws:globalaccelerator::123456789012:accelerator/abcd1234-abcd-1234-abcd-1234567890ab/listener/0123wxyz/endpoint-group/ab12cd34

# Delete listener
aws globalaccelerator delete-listener \
    --listener-arn arn:aws:globalaccelerator::123456789012:accelerator/abcd1234-abcd-1234-abcd-1234567890ab/listener/0123wxyz

# Delete accelerator (must disable first)
aws globalaccelerator update-accelerator \
    --accelerator-arn arn:aws:globalaccelerator::123456789012:accelerator/abcd1234-abcd-1234-abcd-1234567890ab \
    --no-enabled

# Wait for accelerator to be disabled, then delete
aws globalaccelerator delete-accelerator \
    --accelerator-arn arn:aws:globalaccelerator::123456789012:accelerator/abcd1234-abcd-1234-abcd-1234567890ab

# Delete custom routing accelerator
aws globalaccelerator delete-custom-routing-accelerator \
    --accelerator-arn arn:aws:globalaccelerator::123456789012:accelerator/abcd1234-abcd-1234-abcd-1234567890ab
```

---

## Hands-On Labs

### Lab 1: Basic Global Accelerator Setup

#### Prerequisites
- Two Application Load Balancers in different regions
- EC2 instances serving a simple web application
- IAM permissions for Global Accelerator

#### Steps
1. **Create Global Accelerator**
   ```bash
   aws globalaccelerator create-accelerator \
     --name lab-accelerator \
     --ip-address-type IPV4 \
     --enabled
   ```

2. **Create Listener**
   ```bash
   aws globalaccelerator create-listener \
     --accelerator-arn <accelerator-arn> \
     --protocol TCP \
     --port-ranges FromPort=80,ToPort=80
   ```

3. **Create Endpoint Groups**
   ```bash
   # US East endpoint group
   aws globalaccelerator create-endpoint-group \
     --listener-arn <listener-arn> \
     --endpoint-group-region us-east-1 \
     --traffic-dial-percentage 100
   
   # US West endpoint group
   aws globalaccelerator create-endpoint-group \
     --listener-arn <listener-arn> \
     --endpoint-group-region us-west-2 \
     --traffic-dial-percentage 100
   ```

4. **Add Endpoints**
   ```bash
   aws globalaccelerator add-endpoints \
     --endpoint-group-arn <endpoint-group-arn> \
     --endpoint-configurations EndpointId=<alb-arn>,Weight=100
   ```

### Lab 2: Traffic Management with Traffic Dials

#### Scenario
Perform a blue/green deployment using traffic dials

#### Steps
1. **Set up two endpoint groups** (blue and green environments)
2. **Initial traffic distribution**: 100% to blue, 0% to green
3. **Gradual traffic shift**: 
   - 90% blue, 10% green
   - 50% blue, 50% green
   - 0% blue, 100% green
4. **Monitor performance** during the transition

### Lab 3: Health Check Configuration

#### Objective
Configure health checks and observe failover behavior

#### Configuration
```bash
aws globalaccelerator update-endpoint-group \
  --endpoint-group-arn <endpoint-group-arn> \
  --health-check-interval-seconds 30 \
  --health-check-path "/health" \
  --health-check-protocol HTTP \
  --healthy-threshold-count 3 \
  --unhealthy-threshold-count 3
```

#### Testing Failover
1. Monitor endpoint health in CloudWatch
2. Simulate endpoint failure (stop instances/services)
3. Observe automatic traffic redirection
4. Restore endpoints and verify traffic recovery

---

## Advanced Configuration

### Custom Routing Accelerators

#### Use Case
Direct specific users to specific endpoints based on application logic

#### Configuration
```json
{
  "AcceleratorType": "CUSTOM_ROUTING",
  "Subnets": [
    {
      "SubnetId": "subnet-12345678",
      "AllowedPorts": [80, 443, 8080]
    }
  ]
}
```

### Cross-Zone Load Balancing

#### Configuration with ALB Endpoints
- Enable cross-zone load balancing on ALB
- Configure Global Accelerator traffic distribution
- Monitor traffic patterns across availability zones

### Integration with AWS WAF

#### Setup
1. Configure AWS WAF on ALB endpoints
2. Set up Global Accelerator to route to protected ALBs
3. Monitor security metrics in CloudWatch

---

## Troubleshooting Common Issues

### Issue 1: High Latency Despite Global Accelerator

#### Possible Causes
- Endpoints not optimally distributed
- Instance performance issues
- Network congestion at endpoint level

#### Solutions
- Review endpoint placement and performance
- Monitor CloudWatch metrics for bottlenecks
- Consider endpoint scaling or optimization

### Issue 2: Uneven Traffic Distribution

#### Possible Causes
- Incorrect endpoint weights
- Health check failures
- Traffic dial misconfigurations

#### Solutions
- Verify endpoint weights and traffic dials
- Check endpoint health status
- Review CloudWatch metrics for traffic patterns

### Issue 3: Connection Failures

#### Possible Causes
- Firewall or security group restrictions
- Endpoint unavailability
- DNS resolution issues

#### Solutions
- Verify security group and NACL rules
- Check endpoint health and availability
- Test connectivity using anycast IPs directly

---

## Integration Patterns

### Pattern 1: Multi-Tier Architecture
```
Global Accelerator
    ↓
Application Load Balancer (per region)
    ↓
Auto Scaling Group
    ↓
RDS Multi-AZ (per region)
```

### Pattern 2: Microservices Architecture
```
Global Accelerator
    ↓
API Gateway (per region)
    ↓
Microservices (ECS/EKS)
    ↓
Service Discovery
```

### Pattern 3: Hybrid Architecture
```
Global Accelerator
    ↓
Network Load Balancer
    ↓
On-premises endpoints (via Direct Connect)
```

---

## Conclusion

AWS Global Accelerator is a powerful networking service that significantly improves application performance and availability by leveraging AWS's global network infrastructure. For the SAA-C03 exam, focus on understanding:

1. **When to use Global Accelerator** vs. other AWS services
2. **Key benefits**: Static IPs, performance improvement, global reach
3. **Protocol support**: TCP and UDP (unlike CloudFront)
4. **Architecture components**: Accelerators, listeners, endpoint groups, endpoints
5. **Traffic management**: Traffic dials and endpoint weights
6. **Integration patterns** with other AWS services

### Key Takeaways for SAA-C03
- Global Accelerator provides up to 60% performance improvement
- Uses static anycast IP addresses for simplified management
- Supports both TCP and UDP protocols
- Includes built-in DDoS protection with AWS Shield Standard
- Ideal for gaming, IoT, and real-time applications
- Complements rather than replaces other AWS services like CloudFront and ALB

Remember to practice hands-on labs and understand the service's integration with the broader AWS ecosystem for exam success.