# Google Cloud Load Balancing - ACE & PCA Certification Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Load Balancing Overview](#load-balancing-overview)
3. [Types of Load Balancers](#types-of-load-balancers)
4. [Global vs Regional Load Balancers](#global-vs-regional-load-balancers)
5. [HTTP(S) Load Balancing](#https-load-balancing)
6. [TCP/SSL Proxy Load Balancing](#tcpssl-proxy-load-balancing)
7. [Network Load Balancing](#network-load-balancing)
8. [Internal Load Balancing](#internal-load-balancing)
9. [Load Balancer Components](#load-balancer-components)
10. [Health Checks](#health-checks)
11. [Session Affinity](#session-affinity)
12. [SSL Certificates and Security](#ssl-certificates-and-security)
13. [CDN Integration](#cdn-integration)
14. [Autoscaling with Load Balancers](#autoscaling-with-load-balancers)
15. [Monitoring and Logging](#monitoring-and-logging)
16. [Cost Optimization](#cost-optimization)
17. [Best Practices](#best-practices)
18. [Troubleshooting](#troubleshooting)
19. [Exam Tips](#exam-tips)
20. [Hands-on Labs](#hands-on-labs)

## Introduction

Google Cloud Load Balancing is a fully managed service that distributes incoming traffic across multiple instances of your application. It provides high availability, scalability, and performance for your applications while reducing latency and ensuring optimal user experience.

**Key Benefits:**
- **High Availability**: Distributes traffic across healthy instances
- **Scalability**: Handles millions of requests per second
- **Global Reach**: Serves users from the nearest location
- **Security**: Built-in DDoS protection and SSL termination
- **Cost-Effective**: Pay only for what you use

## Load Balancing Overview

### What is Load Balancing?
Load balancing is the process of distributing network traffic across multiple servers to ensure no single server is overwhelmed. This improves:
- **Performance**: Reduces response times
- **Reliability**: Prevents single points of failure
- **Scalability**: Handles increased traffic loads

### Google Cloud Load Balancing Architecture
```
Internet → Global Load Balancer → Regional Backends → Instance Groups
```

### Key Concepts
- **Frontend**: Receives traffic from clients
- **Backend**: Pool of servers handling requests
- **Health Checks**: Monitor backend health
- **Forwarding Rules**: Route traffic to backends

## Types of Load Balancers

Google Cloud offers several types of load balancers based on:
- **Traffic Type**: HTTP(S), TCP, UDP
- **Scope**: Global or Regional
- **Load Balancer Type**: External or Internal

### 1. HTTP(S) Load Balancer
- **Type**: Layer 7 (Application Layer)
- **Scope**: Global
- **Traffic**: HTTP and HTTPS
- **Use Cases**: Web applications, APIs, microservices

### 2. SSL Proxy Load Balancer
- **Type**: Layer 4 (Transport Layer)
- **Scope**: Global
- **Traffic**: SSL/TLS traffic (non-HTTP)
- **Use Cases**: SSL-terminated applications

### 3. TCP Proxy Load Balancer
- **Type**: Layer 4 (Transport Layer)
- **Scope**: Global
- **Traffic**: TCP traffic
- **Use Cases**: Gaming, IoT, custom protocols

### 4. Network Load Balancer
- **Type**: Layer 4 (Transport Layer)
- **Scope**: Regional
- **Traffic**: TCP, UDP, ESP, ICMP
- **Use Cases**: High-performance, low-latency applications

### 5. Internal Load Balancer
- **Type**: Layer 4 (Transport Layer)
- **Scope**: Regional
- **Traffic**: Internal traffic within VPC
- **Use Cases**: Multi-tier architectures, internal services

### 6. Internal HTTP(S) Load Balancer
- **Type**: Layer 7 (Application Layer)
- **Scope**: Regional or Global
- **Traffic**: Internal HTTP(S) traffic
- **Use Cases**: Internal web services, microservices

## Global vs Regional Load Balancers

### Global Load Balancers
- **Geographic Distribution**: Multiple regions
- **Anycast IP**: Single IP address globally
- **Automatic Failover**: Cross-region redundancy
- **Types**: HTTP(S), SSL Proxy, TCP Proxy

**Benefits:**
- Lower latency for global users
- Automatic disaster recovery
- Simplified DNS management

### Regional Load Balancers
- **Geographic Scope**: Single region
- **Regional IP**: IP address within specific region
- **Lower Cost**: Reduced data transfer costs
- **Types**: Network Load Balancer, Internal Load Balancer

**Benefits:**
- Lower latency for regional users
- Cost-effective for regional applications
- Compliance with data locality requirements

## HTTP(S) Load Balancing

### Architecture Overview
```
Internet → Global HTTP(S) LB → Backend Services → Instance Groups
```

### Key Features
- **Global Anycast IP**: Single IP for worldwide access
- **SSL Termination**: Handles SSL/TLS encryption
- **Content-Based Routing**: Route based on URL, headers
- **Auto Scaling**: Integrates with managed instance groups
- **CDN Integration**: Works with Cloud CDN

### Configuration Components

#### 1. Forwarding Rules
```yaml
# Example forwarding rule configuration
name: my-forwarding-rule
IPProtocol: TCP
portRange: 80-80
target: my-target-proxy
```

#### 2. Target Proxy
- **HTTP Target Proxy**: For HTTP traffic
- **HTTPS Target Proxy**: For HTTPS traffic with SSL certificates

#### 3. URL Maps
Route requests to appropriate backend services based on:
- **Host**: Different domains
- **Path**: URL paths (/api, /images)
- **Headers**: Custom routing logic

```yaml
# Example URL map
defaultService: backend-service-1
hostRules:
  - hosts: ['example.com']
    pathMatcher: matcher-1
pathMatchers:
  - name: matcher-1
    defaultService: backend-service-1
    pathRules:
      - paths: ['/api/*']
        service: api-backend-service
```

#### 4. Backend Services
Define how traffic is distributed to backends:
```yaml
# Backend service configuration
name: my-backend-service
protocol: HTTP
timeoutSec: 30
backends:
  - group: instance-group-1
    balancingMode: UTILIZATION
    maxUtilization: 0.8
healthChecks:
  - my-health-check
```

### Load Balancing Algorithms
1. **Round Robin**: Sequential distribution
2. **Least Connections**: Route to least busy server
3. **IP Hash**: Based on client IP
4. **Weighted Round Robin**: Based on server capacity

## TCP/SSL Proxy Load Balancing

### TCP Proxy Load Balancer
- **Global**: Anycast IP addresses
- **Protocol**: TCP traffic (non-HTTP)
- **Termination**: TCP connection termination
- **Use Cases**: Gaming, databases, custom protocols

### SSL Proxy Load Balancer
- **Global**: Anycast IP addresses
- **Protocol**: SSL/TLS traffic (non-HTTP)
- **Termination**: SSL connection termination
- **Certificate Management**: Google-managed or self-managed certificates

### Configuration
```yaml
# TCP Proxy configuration
name: tcp-proxy-lb
service: tcp-backend-service
proxyHeader: PROXY_V1

# SSL Proxy configuration
name: ssl-proxy-lb
service: ssl-backend-service
sslCertificates:
  - my-ssl-certificate
```

## Network Load Balancing

### Overview
- **Regional**: Operates within a single region
- **Pass-through**: Preserves source IP addresses
- **High Performance**: Low latency, high throughput
- **Protocol Support**: TCP, UDP, ESP, ICMP

### Use Cases
- **Gaming**: Real-time multiplayer games
- **IoT**: Device communication protocols
- **VPN**: Site-to-site VPN connections
- **Database**: Direct database connections

### Configuration
```yaml
# Network Load Balancer
name: network-lb
region: us-central1
loadBalancingScheme: EXTERNAL
backends:
  - group: instance-group
    balancingMode: CONNECTION
```

### Session Affinity Options
1. **None**: No affinity (default)
2. **Client IP**: Based on client IP
3. **Generated Cookie**: Server-generated session cookie
4. **Client IP and Protocol**: IP + protocol combination

## Internal Load Balancing

### Internal TCP/UDP Load Balancer
- **Private**: Internal to VPC network
- **Regional**: Single region deployment
- **Andromeda**: Google's network virtualization stack
- **Source IP Preservation**: Maintains original client IP

### Internal HTTP(S) Load Balancer
- **Layer 7**: Application-layer load balancing
- **Envoy-based**: Uses Envoy proxy technology
- **Advanced Routing**: Content-based routing capabilities
- **Regional or Global**: Flexible deployment scope

### Use Cases
- **Multi-tier Applications**: Frontend to backend communication
- **Microservices**: Service-to-service communication
- **Database Clustering**: Database load distribution
- **Internal APIs**: Private API gateways

### Configuration Example
```yaml
# Internal Load Balancer
name: internal-lb
loadBalancingScheme: INTERNAL
network: my-vpc-network
subnetwork: my-subnet
backends:
  - group: internal-instance-group
```

## Load Balancer Components

### 1. Frontend Configuration
- **IP Address**: External or internal IP
- **Port**: Listening port (80, 443, custom)
- **Protocol**: HTTP, HTTPS, TCP, UDP

### 2. Backend Configuration
- **Instance Groups**: Managed or unmanaged
- **Network Endpoint Groups (NEGs)**:
  - Zonal NEGs: VM instances
  - Internet NEGs: External endpoints
  - Serverless NEGs: Cloud Run, App Engine, Cloud Functions

### 3. Health Checks
Monitor backend health and availability:
```yaml
# Health check configuration
name: http-health-check
type: HTTP
requestPath: /health
port: 80
checkIntervalSec: 10
timeoutSec: 5
unhealthyThreshold: 3
healthyThreshold: 2
```

### 4. Firewall Rules
Allow traffic for load balancers:
```bash
# Allow health check traffic
gcloud compute firewall-rules create allow-health-checks \
    --allow tcp:80,tcp:443 \
    --source-ranges 130.211.0.0/22,35.191.0.0/16 \
    --description "Allow health checks"

# Allow load balancer traffic
gcloud compute firewall-rules create allow-lb-traffic \
    --allow tcp:80,tcp:443 \
    --target-tags lb-backend
```

## Health Checks

### Types of Health Checks
1. **HTTP Health Check**: HTTP GET requests
2. **HTTPS Health Check**: HTTPS GET requests
3. **TCP Health Check**: TCP connection attempts
4. **SSL Health Check**: SSL handshake verification

### Health Check Parameters
- **Check Interval**: Time between checks (default: 10s)
- **Timeout**: Request timeout (default: 5s)
- **Healthy Threshold**: Consecutive successes (default: 2)
- **Unhealthy Threshold**: Consecutive failures (default: 3)

### Best Practices
- **Dedicated Endpoint**: Create specific health check endpoints
- **Lightweight Checks**: Fast, minimal resource usage
- **Dependency Checks**: Verify critical dependencies
- **Logging**: Monitor health check results

### Example Health Check Endpoint
```python
# Flask example
@app.route('/health')
def health_check():
    # Check database connection
    if not database.is_healthy():
        return 'Database unhealthy', 503
    
    # Check external dependencies
    if not external_service.is_reachable():
        return 'External service unavailable', 503
    
    return 'OK', 200
```

## Session Affinity

### Overview
Session affinity (sticky sessions) ensures requests from the same client are routed to the same backend instance.

### Types of Session Affinity

#### 1. Client IP Affinity
- **Mechanism**: Hash of client IP address
- **Persistence**: Until IP changes
- **Use Case**: Simple session management

#### 2. Generated Cookie Affinity
- **Mechanism**: Load balancer-generated cookie
- **Persistence**: Cookie lifetime
- **Control**: TTL and path settings

#### 3. Client IP and Protocol Affinity
- **Mechanism**: Hash of IP + protocol
- **Use Case**: Multi-protocol applications

### Configuration
```yaml
# Backend service with session affinity
sessionAffinity: CLIENT_IP
affinityCookieTtlSec: 3600  # 1 hour
```

### Considerations
- **Scalability Impact**: May cause uneven distribution
- **Failover**: Sessions lost if backend fails
- **Stateless Design**: Prefer stateless applications

## SSL Certificates and Security

### SSL Certificate Types

#### 1. Google-Managed Certificates
- **Automatic**: Provisioning and renewal
- **Domain Validation**: Requires domain ownership
- **Free**: No additional cost
- **Limitations**: Domain validation only

```bash
# Create Google-managed certificate
gcloud compute ssl-certificates create my-ssl-cert \
    --domains example.com,www.example.com \
    --global
```

#### 2. Self-Managed Certificates
- **Control**: Full certificate management
- **Validation Types**: DV, OV, EV certificates
- **Flexibility**: Custom certificate authorities

```bash
# Upload self-managed certificate
gcloud compute ssl-certificates create my-ssl-cert \
    --certificate=cert.pem \
    --private-key=private-key.pem \
    --global
```

### SSL Policies
Control SSL/TLS versions and cipher suites:
```yaml
# SSL policy configuration
name: modern-ssl-policy
profile: MODERN  # COMPATIBLE, MODERN, RESTRICTED
minTlsVersion: TLS_1_2
```

### Security Features
- **DDoS Protection**: Built-in protection against attacks
- **Cloud Armor**: Web application firewall integration
- **Identity-Aware Proxy**: Zero-trust access control
- **Certificate Transparency**: Automatic CT log submission

## CDN Integration

### Cloud CDN Overview
- **Global Network**: 100+ edge locations
- **Cache Control**: HTTP headers and cache keys
- **Origin Shield**: Additional caching layer
- **Compression**: Automatic content compression

### Integration with Load Balancers
```yaml
# Backend service with CDN
name: cdn-backend-service
enableCDN: true
cdnPolicy:
  cacheKeyPolicy:
    includeHost: true
    includeProtocol: true
    includeQueryString: false
  defaultTtl: 3600
  maxTtl: 86400
```

### Cache Configuration
- **Cache Keys**: Customize caching behavior
- **TTL Settings**: Control cache duration
- **Cache Modes**: Cache all, cache static, use origin headers
- **Signed URLs**: Secure content delivery

### Best Practices
- **Cache-Control Headers**: Set appropriate headers
- **Versioning**: Use versioned URLs for updates
- **Compression**: Enable gzip compression
- **Monitoring**: Track cache hit ratios

## Autoscaling with Load Balancers

### Managed Instance Groups (MIGs)
Automatically scale based on:
- **CPU Utilization**: Scale on CPU usage
- **Load Balancer Utilization**: Scale on LB metrics
- **Custom Metrics**: Scale on custom metrics
- **Queue-based Scaling**: Scale on queue depth

### Autoscaling Configuration
```yaml
# Autoscaling policy
name: autoscaler-policy
target: managed-instance-group
autoscalingPolicy:
  minNumReplicas: 1
  maxNumReplicas: 10
  cpuUtilization:
    utilizationTarget: 0.6
  loadBalancingUtilization:
    utilizationTarget: 0.8
```

### Scaling Best Practices
- **Graceful Startup**: Use startup scripts
- **Health Checks**: Ensure healthy scaling
- **Cool-down Periods**: Prevent thrashing
- **Pre-scaling**: Scale proactively for known events

## Monitoring and Logging

### Monitoring Metrics
Key metrics to monitor:
- **Request Count**: Total requests per second
- **Latency**: Response time percentiles
- **Error Rate**: 4xx and 5xx error rates
- **Backend Utilization**: Instance utilization
- **Health Check Status**: Backend health

### Cloud Monitoring Integration
```yaml
# Alerting policy example
displayName: "High Error Rate"
conditions:
  - displayName: "Error rate > 5%"
    conditionThreshold:
      filter: 'resource.type="gce_instance"'
      comparison: COMPARISON_GREATER_THAN
      thresholdValue: 0.05
```

### Access Logs
Enable and configure access logs:
```yaml
# Backend service logging
logConfig:
  enable: true
  sampleRate: 1.0  # 100% sampling
```

### Log Analysis
Use Cloud Logging to analyze:
- **Request patterns**: Identify traffic trends
- **Error analysis**: Debug application issues
- **Performance insights**: Optimize response times
- **Security events**: Detect suspicious activity

## Cost Optimization

### Cost Factors
- **Data Processing**: Charge per GB processed
- **Forwarding Rules**: Fixed cost per rule
- **Global vs Regional**: Different pricing tiers
- **SSL Certificates**: Google-managed vs self-managed

### Optimization Strategies

#### 1. Choose Appropriate Load Balancer Type
- **Regional for Regional Traffic**: Use regional LBs for local traffic
- **Global for Global Traffic**: Use global LBs for worldwide users
- **Internal for Private Traffic**: Use internal LBs for VPC traffic

#### 2. Optimize Data Processing
- **CDN Integration**: Reduce origin traffic
- **Compression**: Enable content compression
- **Caching**: Implement effective caching strategies
- **Connection Pooling**: Reuse connections

#### 3. Right-size Resources
- **Instance Types**: Use appropriate machine types
- **Autoscaling**: Scale based on demand
- **Preemptible Instances**: Use for fault-tolerant workloads

### Cost Monitoring
```bash
# View load balancer costs
gcloud billing budgets list
gcloud logging read "resource.type=http_load_balancer"
```

## Best Practices

### 1. Architecture Design
- **High Availability**: Deploy across multiple zones
- **Fault Tolerance**: Design for component failures
- **Scalability**: Plan for traffic growth
- **Security**: Implement defense in depth

### 2. Performance Optimization
- **Connection Pooling**: Reuse connections when possible
- **Keep-Alive**: Enable HTTP keep-alive
- **Compression**: Use gzip compression
- **CDN**: Cache static content

### 3. Security Best Practices
- **SSL/TLS**: Always use HTTPS for sensitive data
- **Certificate Management**: Automate certificate renewal
- **Access Control**: Implement proper IAM policies
- **DDoS Protection**: Enable Cloud Armor when needed

### 4. Monitoring and Alerting
- **Comprehensive Monitoring**: Monitor all key metrics
- **Alerting**: Set up proactive alerts
- **Dashboards**: Create operational dashboards
- **Runbooks**: Document incident response procedures

### 5. Disaster Recovery
- **Multi-region Deployment**: Deploy across regions
- **Backup Strategies**: Implement data backup
- **Failover Testing**: Regular DR testing
- **RTO/RPO Goals**: Define recovery objectives

## Troubleshooting

### Common Issues and Solutions

#### 1. High Latency
**Symptoms:**
- Slow response times
- Poor user experience

**Troubleshooting Steps:**
```bash
# Check backend health
gcloud compute backend-services get-health BACKEND_SERVICE_NAME

# Review monitoring metrics
gcloud logging read "resource.type=http_load_balancer" \
    --format="table(timestamp, httpRequest.latency)"

# Check for geographic distribution issues
```

**Solutions:**
- Add backends in user-proximity regions
- Enable Cloud CDN
- Optimize application performance
- Review health check configuration

#### 2. 502/503 Errors
**Symptoms:**
- Bad Gateway or Service Unavailable errors

**Troubleshooting Steps:**
```bash
# Check backend health status
gcloud compute backend-services get-health BACKEND_SERVICE_NAME

# Review health check logs
gcloud logging read "resource.type=gce_instance AND severity>=ERROR"

# Check firewall rules
gcloud compute firewall-rules list --filter="name~health-check"
```

**Solutions:**
- Fix unhealthy backends
- Adjust health check parameters
- Scale up backend capacity
- Review firewall rules

#### 3. SSL Certificate Issues
**Symptoms:**
- SSL handshake failures
- Certificate warnings

**Troubleshooting Steps:**
```bash
# Check certificate status
gcloud compute ssl-certificates list

# Verify domain ownership
gcloud compute ssl-certificates describe CERT_NAME

# Test SSL configuration
openssl s_client -connect example.com:443
```

**Solutions:**
- Verify domain ownership
- Update DNS records
- Check certificate expiration
- Review SSL policy configuration

#### 4. Traffic Distribution Issues
**Symptoms:**
- Uneven load distribution
- Some backends overloaded

**Troubleshooting Steps:**
```bash
# Check backend utilization
gcloud monitoring metrics list --filter="metric.type~load_balancing"

# Review session affinity settings
gcloud compute backend-services describe BACKEND_SERVICE_NAME
```

**Solutions:**
- Adjust balancing mode
- Review session affinity settings
- Check backend capacity
- Update autoscaling policies

### Debugging Commands
```bash
# List all load balancers
gcloud compute forwarding-rules list
gcloud compute target-proxies list
gcloud compute backend-services list

# Check specific configuration
gcloud compute url-maps describe URL_MAP_NAME
gcloud compute backend-services describe BACKEND_SERVICE_NAME

# View logs
gcloud logging read "resource.type=http_load_balancer" \
    --limit=50 --format=json
```

## Exam Tips

### Associate Cloud Engineer (ACE) Focus Areas
1. **Basic Configuration**: Create and configure load balancers
2. **Health Checks**: Implement and troubleshoot health checks
3. **Instance Groups**: Configure managed instance groups
4. **Firewall Rules**: Set up appropriate firewall rules
5. **Monitoring**: Basic monitoring and alerting

### Professional Cloud Architect (PCA) Focus Areas
1. **Architecture Design**: Design scalable, resilient architectures
2. **Multi-region Deployment**: Global load balancing strategies
3. **Security**: Advanced security configurations
4. **Cost Optimization**: Design cost-effective solutions
5. **Integration**: Integration with other GCP services

### Key Exam Topics

#### ACE Exam Topics
- **Load Balancer Types**: Understand when to use each type
- **Backend Services**: Configure backend services and instance groups
- **Health Checks**: Create and configure health checks
- **Basic Troubleshooting**: Diagnose common issues
- **gcloud Commands**: Know essential gcloud commands

#### PCA Exam Topics
- **Architectural Patterns**: Design patterns with load balancers
- **Global Architecture**: Multi-region, multi-zone deployments
- **Advanced Features**: SSL policies, Cloud Armor integration
- **Migration Strategies**: Migrate existing applications
- **Performance Optimization**: Design for high performance

### Common Exam Questions Patterns

#### Scenario-Based Questions
1. **Traffic Distribution**: "How to distribute traffic globally?"
2. **High Availability**: "Design for 99.99% availability"
3. **Cost Optimization**: "Reduce load balancing costs"
4. **Security Requirements**: "Secure web application traffic"

#### Technical Implementation
1. **Configuration Steps**: Step-by-step setup procedures
2. **Troubleshooting**: Identify and fix issues
3. **Monitoring Setup**: Configure monitoring and alerting
4. **Integration**: Combine with other GCP services

### Study Tips
1. **Hands-on Practice**: Set up different load balancer types
2. **Documentation**: Read official Google Cloud documentation
3. **Case Studies**: Review real-world implementation examples
4. **Practice Exams**: Take practice tests to identify gaps
5. **Community Resources**: Participate in forums and study groups

## Hands-on Labs

### Lab 1: HTTP(S) Load Balancer Setup

#### Prerequisites
- GCP Account with billing enabled
- Basic knowledge of gcloud CLI

#### Step 1: Create Instance Template
```bash
# Create instance template
gcloud compute instance-templates create web-server-template \
    --machine-type=e2-medium \
    --image-family=debian-11 \
    --image-project=debian-cloud \
    --tags=web-server \
    --metadata=startup-script='#!/bin/bash
    apt-get update
    apt-get install -y apache2
    echo "Hello from $(hostname)" > /var/www/html/index.html
    systemctl start apache2
    systemctl enable apache2'
```

#### Step 2: Create Managed Instance Group
```bash
# Create managed instance group
gcloud compute instance-groups managed create web-server-group \
    --template=web-server-template \
    --size=3 \
    --zone=us-central1-a

# Set up autoscaling
gcloud compute instance-groups managed set-autoscaling web-server-group \
    --zone=us-central1-a \
    --max-num-replicas=5 \
    --min-num-replicas=1 \
    --target-cpu-utilization=0.6
```

#### Step 3: Create Health Check
```bash
# Create HTTP health check
gcloud compute health-checks create http web-server-health-check \
    --port=80 \
    --request-path=/ \
    --check-interval=10s \
    --timeout=5s \
    --unhealthy-threshold=3 \
    --healthy-threshold=2
```

#### Step 4: Create Backend Service
```bash
# Create backend service
gcloud compute backend-services create web-server-backend \
    --protocol=HTTP \
    --health-checks=web-server-health-check \
    --global

# Add instance group to backend service
gcloud compute backend-services add-backend web-server-backend \
    --instance-group=web-server-group \
    --instance-group-zone=us-central1-a \
    --global
```

#### Step 5: Create URL Map and Target Proxy
```bash
# Create URL map
gcloud compute url-maps create web-server-map \
    --default-service=web-server-backend

# Create target HTTP proxy
gcloud compute target-http-proxies create web-server-proxy \
    --url-map=web-server-map
```

#### Step 6: Create Forwarding Rule
```bash
# Create global forwarding rule
gcloud compute forwarding-rules create web-server-rule \
    --global \
    --target-http-proxy=web-server-proxy \
    --ports=80
```

#### Step 7: Configure Firewall
```bash
# Allow health check traffic
gcloud compute firewall-rules create allow-health-checks \
    --allow tcp:80 \
    --source-ranges 130.211.0.0/22,35.191.0.0/16 \
    --target-tags web-server

# Allow load balancer traffic
gcloud compute firewall-rules create allow-web-traffic \
    --allow tcp:80 \
    --source-ranges 0.0.0.0/0 \
    --target-tags web-server
```

#### Step 8: Test the Load Balancer
```bash
# Get the load balancer IP
LB_IP=$(gcloud compute forwarding-rules describe web-server-rule \
    --global --format="value(IPAddress)")

# Test the load balancer
curl http://$LB_IP
```

### Lab 2: Internal Load Balancer

#### Step 1: Create VPC Network
```bash
# Create VPC network
gcloud compute networks create internal-lb-network \
    --subnet-mode=custom

# Create subnet
gcloud compute networks subnets create internal-lb-subnet \
    --network=internal-lb-network \
    --range=10.1.0.0/24 \
    --region=us-central1
```

#### Step 2: Create Backend Instances
```bash
# Create instance template for internal services
gcloud compute instance-templates create internal-service-template \
    --machine-type=e2-small \
    --subnet=internal-lb-subnet \
    --no-address \
    --image-family=debian-11 \
    --image-project=debian-cloud \
    --tags=internal-service \
    --metadata=startup-script='#!/bin/bash
    apt-get update
    apt-get install -y nginx
    echo "Internal service on $(hostname)" > /var/www/html/index.html
    systemctl start nginx
    systemctl enable nginx'

# Create managed instance group
gcloud compute instance-groups managed create internal-service-group \
    --template=internal-service-template \
    --size=2 \
    --zone=us-central1-a
```

#### Step 3: Create Internal Load Balancer
```bash
# Create health check
gcloud compute health-checks create tcp internal-health-check \
    --port=80 \
    --region=us-central1

# Create backend service
gcloud compute backend-services create internal-backend-service \
    --load-balancing-scheme=INTERNAL \
    --protocol=TCP \
    --health-checks=internal-health-check \
    --health-checks-region=us-central1 \
    --region=us-central1

# Add backend to service
gcloud compute backend-services add-backend internal-backend-service \
    --instance-group=internal-service-group \
    --instance-group-zone=us-central1-a \
    --region=us-central1

# Create forwarding rule
gcloud compute forwarding-rules create internal-lb-rule \
    --load-balancing-scheme=INTERNAL \
    --backend-service=internal-backend-service \
    --subnet=internal-lb-subnet \
    --region=us-central1 \
    --ports=80
```

### Lab 3: SSL Load Balancer with Google-Managed Certificate

#### Step 1: Create HTTPS Load Balancer
```bash
# Create Google-managed SSL certificate
gcloud compute ssl-certificates create my-ssl-cert \
    --domains=example.com \
    --global

# Create HTTPS target proxy
gcloud compute target-https-proxies create https-lb-proxy \
    --url-map=web-server-map \
    --ssl-certificates=my-ssl-cert

# Create HTTPS forwarding rule
gcloud compute forwarding-rules create https-lb-rule \
    --global \
    --target-https-proxy=https-lb-proxy \
    --ports=443
```

#### Step 2: Update DNS
```bash
# Get the load balancer IP
LB_IP=$(gcloud compute forwarding-rules describe https-lb-rule \
    --global --format="value(IPAddress)")

echo "Update your DNS A record for example.com to point to: $LB_IP"
```

### Lab 4: Load Balancer with Cloud CDN

#### Step 1: Enable CDN on Backend Service
```bash
# Update backend service to enable CDN
gcloud compute backend-services update web-server-backend \
    --enable-cdn \
    --global

# Configure CDN settings
gcloud compute backend-services update web-server-backend \
    --cache-key-include-host \
    --cache-key-include-protocol \
    --cache-key-query-string-whitelist="" \
    --global
```

#### Step 2: Test CDN Caching
```bash
# Test cache headers
curl -I http://$LB_IP/

# Check for cache hit/miss headers
curl -H "Cache-Control: no-cache" http://$LB_IP/
```

### Lab 5: Advanced Traffic Management

#### Step 1: Create Multiple Backend Services
```bash
# Create different instance groups for A/B testing
gcloud compute instance-groups managed create web-server-group-v1 \
    --template=web-server-template \
    --size=2 \
    --zone=us-central1-a

gcloud compute instance-groups managed create web-server-group-v2 \
    --template=web-server-template-v2 \
    --size=1 \
    --zone=us-central1-b

# Create separate backend services
gcloud compute backend-services create web-backend-v1 \
    --protocol=HTTP \
    --health-checks=web-server-health-check \
    --global

gcloud compute backend-services create web-backend-v2 \
    --protocol=HTTP \
    --health-checks=web-server-health-check \
    --global
```

#### Step 2: Configure Advanced URL Mapping
```bash
# Create URL map with path-based routing
cat > url-map.yaml << 'EOF'
name: advanced-web-map
defaultService: projects/PROJECT_ID/global/backendServices/web-backend-v1
hostRules:
- hosts:
  - example.com
  pathMatcher: matcher1
pathMatchers:
- name: matcher1
  defaultService: projects/PROJECT_ID/global/backendServices/web-backend-v1
  pathRules:
  - paths:
    - /v2/*
    service: projects/PROJECT_ID/global/backendServices/web-backend-v2
  - paths:
    - /api/*
    service: projects/PROJECT_ID/global/backendServices/api-backend-service
EOF

# Import URL map
gcloud compute url-maps import advanced-web-map \
    --source=url-map.yaml \
    --global
```

### Cleanup Commands
```bash
# Clean up resources to avoid charges
gcloud compute forwarding-rules delete web-server-rule --global --quiet
gcloud compute forwarding-rules delete https-lb-rule --global --quiet
gcloud compute target-http-proxies delete web-server-proxy --quiet
gcloud compute target-https-proxies delete https-lb-proxy --quiet
gcloud compute ssl-certificates delete my-ssl-cert --global --quiet
gcloud compute url-maps delete web-server-map --quiet
gcloud compute backend-services delete web-server-backend --global --quiet
gcloud compute health-checks delete web-server-health-check --quiet
gcloud compute instance-groups managed delete web-server-group --zone=us-central1-a --quiet
gcloud compute instance-templates delete web-server-template --quiet
gcloud compute firewall-rules delete allow-health-checks --quiet
gcloud compute firewall-rules delete allow-web-traffic --quiet
```

## Additional Resources

### Official Documentation
- [Google Cloud Load Balancing Overview](https://cloud.google.com/load-balancing/docs)
- [HTTP(S) Load Balancing](https://cloud.google.com/load-balancing/docs/https)
- [Network Load Balancing](https://cloud.google.com/load-balancing/docs/network)
- [Internal Load Balancing](https://cloud.google.com/load-balancing/docs/internal)

### Training and Certification
- [Google Cloud Skills Boost](https://www.cloudskillsboost.google/)
- [Coursera Google Cloud Courses](https://www.coursera.org/googlecloud)
- [Linux Academy/A Cloud Guru](https://acloudguru.com/)

### Community Resources
- [Google Cloud Community](https://cloud.google.com/community)
- [Stack Overflow - Google Cloud Platform](https://stackoverflow.com/questions/tagged/google-cloud-platform)
- [Reddit - r/googlecloud](https://www.reddit.com/r/googlecloud/)

### Tools and Utilities
- [gcloud CLI Reference](https://cloud.google.com/sdk/gcloud/reference)
- [Terraform Google Provider](https://registry.terraform.io/providers/hashicorp/google/latest)
- [Cloud Foundation Toolkit](https://cloud.google.com/foundation-toolkit)

---

This comprehensive guide covers all aspects of Google Cloud Load Balancing relevant to both ACE and PCA certifications. Practice the hands-on labs and focus on understanding the architectural patterns and best practices for successful certification and real-world implementation.