# AWS Route 53 - SAA-C03 Certification Guide

## Table of Contents
1. [Overview](#overview)
2. [Key Concepts](#key-concepts)
3. [DNS Record Types](#dns-record-types)
4. [Routing Policies](#routing-policies)
5. [Health Checks](#health-checks)
6. [Resolver](#resolver)
7. [Domain Registration](#domain-registration)
8. [Route 53 Application Recovery Controller](#route-53-application-recovery-controller)
9. [Pricing](#pricing)
10. [Best Practices](#best-practices)
11. [Common Use Cases](#common-use-cases)
12. [Exam Tips](#exam-tips)
13. [Hands-On Labs](#hands-on-labs)

## Overview

Amazon Route 53 is a highly available and scalable Domain Name System (DNS) web service designed to give developers and businesses an extremely reliable and cost-effective way to route end users to Internet applications.

### Key Features
- **Domain Name System (DNS)**: Translates human-readable domain names to IP addresses
- **Domain Registration**: Register and manage domain names
- **Health Checking**: Monitor application health and route traffic accordingly
- **Traffic Flow**: Visual editor for complex routing configurations
- **Resolver**: Hybrid DNS resolution between AWS and on-premises

### Service Components
- **Hosted Zones**: DNS namespace for a domain
- **Record Sets**: DNS records within hosted zones
- **Health Checks**: Monitor endpoint availability
- **Traffic Policies**: Complex routing configurations
- **Resolver Rules**: Hybrid DNS resolution rules

## Key Concepts

### DNS Fundamentals

#### Domain Name System (DNS)
```
User Request: www.example.com
    ↓
DNS Resolver
    ↓
Root Name Server (.com)
    ↓
TLD Name Server (example.com)
    ↓
Authoritative Name Server
    ↓
IP Address: 192.0.2.1
```

#### DNS Hierarchy
- **Root Domain**: `.` (managed by IANA)
- **Top-Level Domain (TLD)**: `.com`, `.org`, `.net`
- **Second-Level Domain**: `example.com`
- **Subdomain**: `www.example.com`

### Hosted Zones

#### Public Hosted Zone
```yaml
Type: Public
Domain: example.com
Records:
  - Name: www.example.com
    Type: A
    Value: 192.0.2.1
  - Name: mail.example.com
    Type: MX
    Value: 10 mail.example.com
```

#### Private Hosted Zone
```yaml
Type: Private
Domain: internal.company.com
VPC Association:
  - VPC ID: vpc-12345678
    Region: us-east-1
Records:
  - Name: db.internal.company.com
    Type: A
    Value: 10.0.1.100
```

### Time To Live (TTL)
```yaml
Record Configuration:
  Name: www.example.com
  Type: A
  Value: 192.0.2.1
  TTL: 300  # 5 minutes
```

**TTL Impact:**
- **Short TTL (60-300s)**: Faster failover, more DNS queries
- **Long TTL (3600s+)**: Fewer DNS queries, slower failover

## DNS Record Types

### A Record
Maps domain name to IPv4 address:
```yaml
Name: www.example.com
Type: A
Value: 192.0.2.1
TTL: 300
```

### AAAA Record
Maps domain name to IPv6 address:
```yaml
Name: www.example.com
Type: AAAA
Value: 2001:db8::1
TTL: 300
```

### CNAME Record
Maps alias to canonical name:
```yaml
Name: blog.example.com
Type: CNAME
Value: www.example.com
TTL: 300
```

**Important**: CNAME cannot coexist with other record types for the same name.

### MX Record
Mail exchange record:
```yaml
Name: example.com
Type: MX
Value:
  - Priority: 10, Value: mail1.example.com
  - Priority: 20, Value: mail2.example.com
TTL: 3600
```

### NS Record
Name server record:
```yaml
Name: subdomain.example.com
Type: NS
Value:
  - ns1.subdomain-provider.com
  - ns2.subdomain-provider.com
TTL: 3600
```

### PTR Record
Reverse DNS lookup:
```yaml
Name: 1.2.0.192.in-addr.arpa
Type: PTR
Value: www.example.com
TTL: 300
```

### SOA Record
Start of Authority (automatically created):
```yaml
Name: example.com
Type: SOA
Value: ns1.route53.amazonaws.com admin.example.com 2023100201 7200 3600 604800 86400
```

### SRV Record
Service record:
```yaml
Name: _sip._tcp.example.com
Type: SRV
Value: 10 5 5060 sip.example.com
TTL: 300
```

### TXT Record
Text record for verification:
```yaml
Name: example.com
Type: TXT
Value: "v=spf1 include:_spf.google.com ~all"
TTL: 300
```

### CAA Record
Certificate Authority Authorization:
```yaml
Name: example.com
Type: CAA
Value: 0 issue "letsencrypt.org"
TTL: 300
```

## Routing Policies

### Simple Routing
Single resource with one or more IP addresses:
```yaml
Policy: Simple
Record:
  Name: www.example.com
  Type: A
  Values:
    - 192.0.2.1
    - 192.0.2.2
    - 192.0.2.3
```

### Weighted Routing
Traffic distribution based on weights:
```yaml
Record Set 1:
  Name: www.example.com
  Type: A
  Value: 192.0.2.1
  Weight: 70
  Set ID: Primary

Record Set 2:
  Name: www.example.com
  Type: A
  Value: 192.0.2.2
  Weight: 30
  Set ID: Secondary
```

### Latency-Based Routing
Route to lowest latency endpoint:
```yaml
Record Set 1:
  Name: www.example.com
  Type: A
  Value: 192.0.2.1
  Region: us-east-1
  Set ID: US-East

Record Set 2:
  Name: www.example.com
  Type: A
  Value: 203.0.113.1
  Region: ap-southeast-1
  Set ID: Asia-Pacific
```

### Failover Routing
Active-passive failover:
```yaml
Primary Record:
  Name: www.example.com
  Type: A
  Value: 192.0.2.1
  Failover: PRIMARY
  Health Check: check-primary
  Set ID: Primary

Secondary Record:
  Name: www.example.com
  Type: A
  Value: 192.0.2.2
  Failover: SECONDARY
  Set ID: Secondary
```

### Geolocation Routing
Route based on user location:
```yaml
Default Record:
  Name: www.example.com
  Type: A
  Value: 192.0.2.1
  Geolocation: Default
  Set ID: Default

US Record:
  Name: www.example.com
  Type: A
  Value: 192.0.2.2
  Geolocation: Country=US
  Set ID: United-States

Europe Record:
  Name: www.example.com
  Type: A
  Value: 203.0.113.1
  Geolocation: Continent=EU
  Set ID: Europe
```

### Geoproximity Routing
Route based on geographic location with bias:
```yaml
Record Set 1:
  Name: www.example.com
  Type: A
  Value: 192.0.2.1
  Coordinates: 40.7128, -74.0060  # New York
  Bias: +50
  Set ID: East-Coast

Record Set 2:
  Name: www.example.com
  Type: A
  Value: 203.0.113.1
  Coordinates: 37.7749, -122.4194  # San Francisco
  Bias: -25
  Set ID: West-Coast
```

### Multivalue Answer Routing
Return multiple healthy IP addresses:
```yaml
Record Set 1:
  Name: www.example.com
  Type: A
  Value: 192.0.2.1
  Health Check: check-1
  Set ID: Server-1

Record Set 2:
  Name: www.example.com
  Type: A
  Value: 192.0.2.2
  Health Check: check-2
  Set ID: Server-2

Record Set 3:
  Name: www.example.com
  Type: A
  Value: 192.0.2.3
  Health Check: check-3
  Set ID: Server-3
```

## Health Checks

### Health Check Types

#### HTTP/HTTPS Health Checks
```yaml
Health Check Configuration:
  Type: HTTP
  Resource Path: /health
  Port: 80
  Request Interval: 30 seconds
  Failure Threshold: 3
  Success Codes: 200-299
  Regions: Global (15+ regions)
```

#### TCP Health Check
```yaml
Health Check Configuration:
  Type: TCP
  Port: 443
  Request Interval: 30 seconds
  Failure Threshold: 3
```

#### Calculated Health Check
```yaml
Health Check Configuration:
  Type: Calculated
  Child Health Checks:
    - web-server-1-health
    - web-server-2-health
    - database-health
  Healthy Threshold: 2 of 3
```

#### CloudWatch Alarm Health Check
```yaml
Health Check Configuration:
  Type: CloudWatch Alarm
  CloudWatch Alarm: high-cpu-alarm
  Region: us-east-1
  Insufficient Data: Healthy
```

### Health Check Features

#### String Matching
```yaml
Health Check:
  Type: HTTP
  Path: /status
  String Matching: "Server is healthy"
  Search First: 5120 bytes
```

#### SNS Notifications
```yaml
Health Check:
  Name: web-server-health
  Notification:
    Topic: arn:aws:sns:us-east-1:123456789012:health-alerts
    When: Alarm (health check fails)
```

## Resolver

### Route 53 Resolver Overview
Provides recursive DNS resolution between AWS VPC and on-premises networks.

### Resolver Endpoints

#### Inbound Endpoint
Allows on-premises DNS queries to resolve AWS resources:
```yaml
Inbound Endpoint:
  VPC: vpc-12345678
  Subnets:
    - subnet-abcdef01 (AZ-1a)
    - subnet-abcdef02 (AZ-1b)
  IP Addresses:
    - 10.0.1.10
    - 10.0.2.10
```

#### Outbound Endpoint
Allows AWS resources to query on-premises DNS:
```yaml
Outbound Endpoint:
  VPC: vpc-12345678
  Subnets:
    - subnet-abcdef01
    - subnet-abcdef02
  IP Addresses:
    - 10.0.1.11
    - 10.0.2.11
```

### Resolver Rules

#### Forward Rule
```yaml
Rule Configuration:
  Name: on-premises-forward
  Type: Forward
  Domain: corp.company.com
  VPC Associations:
    - vpc-12345678
  Target IPs:
    - 192.168.1.10:53
    - 192.168.1.11:53
```

#### System Rule
```yaml
Rule Configuration:
  Type: System
  Domain: amazonaws.com
  Action: Default AWS DNS resolution
```

### DNS Resolution Flow
```
AWS VPC Query (app.corp.company.com)
    ↓
Route 53 Resolver
    ↓
Resolver Rule (Forward to on-premises)
    ↓
Outbound Endpoint
    ↓
On-premises DNS Server
    ↓
Response: 192.168.100.50
```

## Domain Registration

### Domain Registration Process
1. **Check Availability**: Verify domain name availability
2. **Register Domain**: Complete registration with registrar information
3. **Configure DNS**: Set up hosted zone and name servers
4. **Manage Domain**: Renew, transfer, or update domain settings

### Supported TLDs
- **Generic TLDs**: .com, .net, .org, .info, .biz
- **Country Code TLDs**: .us, .uk, .ca, .au, .de
- **New TLDs**: .tech, .online, .store, .app

### Domain Transfer
```yaml
Transfer Process:
  1. Unlock domain at current registrar
  2. Obtain authorization code
  3. Initiate transfer in Route 53
  4. Confirm transfer via email
  5. Complete transfer (5-7 days)
```

### Auto-Renewal
```yaml
Domain Configuration:
  Domain: example.com
  Auto-Renew: Enabled
  Renewal Period: 1 year
  Notification: 30 days before expiry
```

## Route 53 Application Recovery Controller

### Overview
Provides application-level routing controls for disaster recovery scenarios.

### Control Panels
```yaml
Control Panel:
  Name: webapp-controls
  Cluster: recovery-cluster
  Routing Controls:
    - primary-datacenter
    - secondary-datacenter
    - maintenance-mode
```

### Routing Controls
```yaml
Routing Control:
  Name: primary-datacenter
  State: On/Off
  Associated Health Checks:
    - primary-elb-health
    - primary-rds-health
```

### Safety Rules

#### Assertion Rule
```yaml
Assertion Rule:
  Name: at-least-one-datacenter
  Rule Logic: primary-datacenter OR secondary-datacenter
  Wait Period: 5 minutes
```

#### Gating Rule
```yaml
Gating Rule:
  Name: prevent-simultaneous-failover
  Gating Controls:
    - maintenance-mode
  Target Controls:
    - primary-datacenter
    - secondary-datacenter
```

## Pricing

### Hosted Zone Pricing
- **Public Hosted Zone**: $0.50 per hosted zone per month
- **Private Hosted Zone**: $0.50 per hosted zone per month
- **First 25 hosted zones**: $0.50 each
- **Additional hosted zones**: Discounted pricing

### Query Pricing (per million queries)
- **Standard Queries**: $0.40
- **Latency-Based Routing**: $0.60
- **Geolocation/Geoproximity**: $0.70
- **Weighted/Failover**: $0.60

### Health Check Pricing
- **Basic Health Checks**: $0.50 per health check per month
- **Optional Features**: Additional costs for string matching, HTTPS, fast interval

### Domain Registration
- **Varies by TLD**: $9-$50+ per year depending on domain extension
- **Premium Domains**: Higher pricing for premium domain names

## Best Practices

### Performance Optimization

#### TTL Configuration
```yaml
Best Practices:
  Static Content: TTL 3600-86400 seconds
  Dynamic Content: TTL 60-300 seconds
  Failover Scenarios: TTL 60 seconds
  Development/Testing: TTL 30-60 seconds
```

#### Geographic Optimization
```yaml
Strategy:
  - Use latency-based routing for global applications
  - Implement geolocation routing for compliance requirements
  - Configure geoproximity routing for traffic shifting
  - Monitor resolver performance by region
```

### High Availability

#### Multi-Region Setup
```yaml
Architecture:
  Primary Region: us-east-1
  Secondary Region: us-west-2
  Routing Policy: Failover
  Health Checks: Both regions
  RPO: < 1 hour
  RTO: < 5 minutes
```

#### Health Check Strategy
```yaml
Implementation:
  - Monitor application endpoints, not just servers
  - Use calculated health checks for complex dependencies
  - Configure appropriate failure thresholds
  - Set up CloudWatch alarms integration
```

### Security

#### Access Control
```yaml
IAM Policy Example:
  Version: '2012-10-17'
  Statement:
    - Effect: Allow
      Action:
        - route53:GetHostedZone
        - route53:ListResourceRecordSets
      Resource: "arn:aws:route53:::hostedzone/Z123456789"
    - Effect: Allow
      Action:
        - route53:ChangeResourceRecordSets
      Resource: "arn:aws:route53:::hostedzone/Z123456789"
      Condition:
        StringEquals:
          'route53:RRType': ['A', 'CNAME']
```

#### DNS Security
- Enable DNS query logging
- Use private hosted zones for internal resources
- Implement DNSSEC where supported
- Monitor for DNS hijacking attempts

### Cost Optimization

#### Query Optimization
```yaml
Strategies:
  - Use appropriate TTL values to reduce query volume
  - Consolidate similar records where possible
  - Monitor query patterns with CloudWatch
  - Use alias records for AWS resources (free queries)
```

#### Health Check Optimization
```yaml
Best Practices:
  - Use calculated health checks instead of multiple individual checks
  - Optimize health check intervals based on requirements
  - Use CloudWatch alarms for cost-effective monitoring
  - Remove unused health checks regularly
```

## Common Use Cases

### 1. Simple Web Application
```yaml
Scenario: Static website with CDN
Setup:
  - A record: www.example.com → CloudFront distribution
  - CNAME: example.com → www.example.com
  - MX record: Mail service configuration
```

### 2. Multi-Region Application
```yaml
Scenario: Global application with regional endpoints
Setup:
  Primary: us-east-1 (Weighted 70%)
  Secondary: eu-west-1 (Weighted 30%)
  Routing: Weighted with health checks
  Failover: Automatic to secondary region
```

### 3. Blue-Green Deployment
```yaml
Scenario: Zero-downtime deployment strategy
Setup:
  Blue Environment: Current production (Weight 100%)
  Green Environment: New version (Weight 0%)
  Deployment: Gradually shift weight to green
  Rollback: Instant weight shift back to blue
```

### 4. Disaster Recovery
```yaml
Scenario: Active-passive DR setup
Primary Site:
  - Route: Primary (Active)
  - Health Check: Application endpoint
  - Failover Record: Primary
DR Site:
  - Route: Secondary (Standby)
  - Failover Record: Secondary
  - Activation: Automatic on primary failure
```

### 5. Hybrid Cloud DNS
```yaml
Scenario: On-premises and AWS integration
Components:
  - Route 53 Resolver endpoints
  - Conditional forwarding rules
  - Private hosted zones for AWS resources
  - Integration with on-premises DNS servers
```

### 6. Microservices Architecture
```yaml
Scenario: Service discovery for microservices
Setup:
  - Private hosted zone: services.internal
  - Service records: user-service.services.internal
  - Health checks: Per service endpoint
  - Load balancing: Multivalue answer routing
```

## Exam Tips

### Key Concepts to Remember

#### DNS Fundamentals
- Understand DNS hierarchy and resolution process
- Know the difference between authoritative and recursive DNS
- Understand TTL impact on DNS caching and failover speed
- Remember that Route 53 is a global service (not region-specific)

#### Record Types
- **A**: IPv4 address mapping
- **AAAA**: IPv6 address mapping
- **CNAME**: Alias (cannot coexist with other record types)
- **ALIAS**: AWS-specific, can coexist with other records
- **MX**: Mail exchange with priority
- **NS**: Delegation to other name servers

#### Routing Policies
- **Simple**: Single resource, multiple IP addresses returned randomly
- **Weighted**: Traffic distribution based on assigned weights
- **Latency-based**: Route to lowest latency endpoint
- **Failover**: Active-passive configuration with health checks
- **Geolocation**: Route based on user's geographic location
- **Geoproximity**: Geographic routing with bias adjustments
- **Multivalue**: Multiple healthy records returned

#### Health Checks
- Health checks can monitor HTTP/HTTPS endpoints, TCP ports, or other health checks
- Calculated health checks combine multiple health checks
- Health checks can trigger CloudWatch alarms
- Health checks are performed from multiple AWS regions

### Common Exam Scenarios

#### Scenario 1: Global Application Performance
**Question**: How to route users to the closest AWS region for better performance?
**Answer**: Use latency-based routing policy with health checks

#### Scenario 2: Disaster Recovery
**Question**: Automatic failover when primary region becomes unavailable?
**Answer**: Use failover routing policy with health checks monitoring primary region

#### Scenario 3: Gradual Deployment
**Question**: Gradually shift traffic from old to new version of application?
**Answer**: Use weighted routing policy, gradually increasing weight for new version

#### Scenario 4: Compliance Requirements
**Question**: Route users to specific regions based on data residency laws?
**Answer**: Use geolocation routing policy to ensure users stay within required regions

#### Scenario 5: Hybrid DNS Resolution
**Question**: AWS resources need to resolve on-premises domain names?
**Answer**: Configure Route 53 Resolver with outbound endpoints and forwarding rules

### DNS Resolution Order
1. Check local DNS cache
2. Query recursive resolver
3. Query root name servers
4. Query TLD name servers
5. Query authoritative name servers
6. Return IP address to client

### Route 53 vs Other Services
- **Route 53 vs CloudFront**: Route 53 provides DNS, CloudFront provides content delivery
- **Route 53 vs ELB**: Route 53 routes to resources, ELB distributes traffic among instances
- **Route 53 vs API Gateway**: Route 53 provides DNS routing, API Gateway manages API traffic

### Troubleshooting Tips
- Use `dig` or `nslookup` commands to test DNS resolution
- Check TTL values when DNS changes aren't propagating
- Verify health check configuration for failover issues
- Monitor CloudWatch metrics for DNS query patterns
- Use Route 53 query logging for detailed analysis

## Hands-On Labs

### Lab 1: Basic DNS Setup

#### Prerequisites
- AWS Account with appropriate permissions
- Domain name (or use Route 53 domain registration)
- Basic understanding of DNS concepts

#### Steps
1. **Create Hosted Zone**
   ```bash
   aws route53 create-hosted-zone \
     --name example.com \
     --caller-reference $(date +%s)
   ```

2. **Create A Record**
   ```json
   {
     "Comment": "Creating A record",
     "Changes": [{
       "Action": "CREATE",
       "ResourceRecordSet": {
         "Name": "www.example.com",
         "Type": "A",
         "TTL": 300,
         "ResourceRecords": [{"Value": "192.0.2.1"}]
       }
     }]
   }
   ```

3. **Test DNS Resolution**
   ```bash
   dig www.example.com
   nslookup www.example.com
   ```

### Lab 2: Weighted Routing

#### Scenario
Set up weighted routing to distribute traffic between two web servers.

#### Configuration
```yaml
Record Set 1:
  Name: api.example.com
  Type: A
  Value: 192.0.2.1
  Routing Policy: Weighted
  Weight: 70
  Set Identifier: Primary-Server

Record Set 2:
  Name: api.example.com
  Type: A
  Value: 192.0.2.2
  Routing Policy: Weighted
  Weight: 30
  Set Identifier: Secondary-Server
```

#### Testing
```bash
# Multiple DNS queries to see weight distribution
for i in {1..10}; do
  dig +short api.example.com
done
```

### Lab 3: Health Check and Failover

#### Setup Primary Record with Health Check
```json
{
  "Type": "A",
  "Name": "app.example.com",
  "ResourceRecords": [{"Value": "192.0.2.1"}],
  "TTL": 60,
  "SetIdentifier": "Primary",
  "Failover": "PRIMARY",
  "HealthCheckId": "health-check-id"
}
```

#### Setup Secondary Record
```json
{
  "Type": "A",
  "Name": "app.example.com",
  "ResourceRecords": [{"Value": "192.0.2.2"}],
  "TTL": 60,
  "SetIdentifier": "Secondary",
  "Failover": "SECONDARY"
}
```

#### Create Health Check
```bash
aws route53 create-health-check \
  --caller-reference $(date +%s) \
  --health-check-config \
    Type=HTTP,ResourcePath=/health,FullyQualifiedDomainName=192.0.2.1,Port=80,RequestInterval=30,FailureThreshold=3
```

### Lab 4: Private Hosted Zone

#### Create Private Hosted Zone
```bash
aws route53 create-hosted-zone \
  --name internal.company.com \
  --caller-reference $(date +%s) \
  --vpc VPCRegion=us-east-1,VPCId=vpc-12345678 \
  --hosted-zone-config PrivateZone=true
```

#### Add Internal Records
```json
{
  "Comment": "Internal service records",
  "Changes": [{
    "Action": "CREATE",
    "ResourceRecordSet": {
      "Name": "database.internal.company.com",
      "Type": "A",
      "TTL": 300,
      "ResourceRecords": [{"Value": "10.0.1.100"}]
    }
  }]
}
```

### Lab 5: Route 53 Resolver Setup

#### Create Inbound Endpoint
```bash
aws route53resolver create-resolver-endpoint \
  --creator-request-id $(date +%s) \
  --direction INBOUND \
  --security-group-ids sg-12345678 \
  --ip-addresses SubnetId=subnet-abcdef01,Ip=10.0.1.10 SubnetId=subnet-abcdef02,Ip=10.0.2.10
```

#### Create Forwarding Rule
```bash
aws route53resolver create-resolver-rule \
  --creator-request-id $(date +%s) \
  --domain-name corp.company.com \
  --rule-type FORWARD \
  --resolver-endpoint-id rslvr-in-12345678 \
  --target-ips Ip=192.168.1.10,Port=53
```

#### Associate Rule with VPC
```bash
aws route53resolver associate-resolver-rule \
  --resolver-rule-id rslvr-rr-12345678 \
  --vpc-id vpc-12345678
```

This comprehensive guide covers all aspects of AWS Route 53 relevant to the SAA-C03 certification exam, including practical examples, best practices, and hands-on labs to reinforce learning.