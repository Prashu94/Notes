# AWS Networking - SAA-C03 Certification Guide

## Table of Contents
1. [Overview](#overview)
2. [Virtual Private Cloud (VPC)](#virtual-private-cloud-vpc)
3. [Subnets](#subnets)
4. [Internet Gateway (IGW)](#internet-gateway-igw)
5. [NAT Gateway and NAT Instance](#nat-gateway-and-nat-instance)
6. [Route Tables](#route-tables)
7. [Security Groups](#security-groups)
8. [Network ACLs (NACLs)](#network-acls-nacls)
9. [VPC Endpoints](#vpc-endpoints)
10. [VPC Peering](#vpc-peering)
11. [Transit Gateway](#transit-gateway)
12. [Direct Connect](#direct-connect)
13. [Site-to-Site VPN](#site-to-site-vpn)
14. [Client VPN](#client-vpn)
15. [Elastic Load Balancer (ELB)](#elastic-load-balancer-elb)
16. [CloudFront](#cloudfront)
17. [Route 53](#route-53)
18. [AWS Global Accelerator](#aws-global-accelerator)
19. [Network Security](#network-security)
20. [AWS CLI Commands Reference](#aws-cli-commands-reference)
21. [Monitoring and Troubleshooting](#monitoring-and-troubleshooting)

## Overview

AWS Networking forms the backbone of cloud infrastructure, providing secure, scalable, and high-performance networking solutions. For the SAA-C03 exam, understanding networking concepts is crucial as they appear in multiple domains.

### Key Networking Services
- **VPC**: Virtual Private Cloud - Your private network in AWS
- **ELB**: Elastic Load Balancing - Distributes traffic
- **Route 53**: DNS web service
- **CloudFront**: Content Delivery Network
- **Direct Connect**: Dedicated network connection
- **Transit Gateway**: Central hub for VPC connectivity

## Virtual Private Cloud (VPC)

### What is VPC?
A VPC is a virtual network dedicated to your AWS account, logically isolated from other virtual networks in AWS.

### Key Features
- **Isolated Environment**: Complete control over your virtual networking environment
- **Customizable**: Configure IP address ranges, subnets, route tables, and gateways
- **Secure**: Multiple layers of security including security groups and NACLs
- **Scalable**: Can span multiple Availability Zones

### VPC Components
```
VPC (10.0.0.0/16)
├── Public Subnet (10.0.1.0/24) - AZ-1a
├── Private Subnet (10.0.2.0/24) - AZ-1a
├── Public Subnet (10.0.3.0/24) - AZ-1b
└── Private Subnet (10.0.4.0/24) - AZ-1b
```

### VPC Limits
- **Default**: 5 VPCs per region (can be increased)
- **CIDR Blocks**: Up to 5 IPv4 CIDR blocks per VPC
- **Size Range**: /16 to /28 netmask
- **Reserved IPs**: 5 IP addresses per subnet are reserved

### Reserved IP Addresses (Example: 10.0.0.0/24)
- `10.0.0.0`: Network address
- `10.0.0.1`: VPC router
- `10.0.0.2`: DNS server
- `10.0.0.3`: Reserved for future use
- `10.0.0.255`: Broadcast address (not supported in VPC)

### Default vs Custom VPC

| Feature | Default VPC | Custom VPC |
|---------|-------------|------------|
| CIDR Block | 172.31.0.0/16 | User-defined |
| Subnets | Public subnets in each AZ | User-configured |
| Internet Gateway | Attached | Must attach manually |
| Route Tables | Main route table with IGW route | Must configure |
| Security Group | Default allows all outbound | Must configure |
| DNS Resolution | Enabled | Must enable |

## Subnets

### Types of Subnets

#### Public Subnet
- Has a route to Internet Gateway (IGW)
- Instances can have public IP addresses
- Direct internet access for inbound/outbound traffic

#### Private Subnet
- No direct route to Internet Gateway
- Uses NAT Gateway/Instance for outbound internet access
- No inbound internet access without load balancer

#### Database Subnet
- Typically private subnets for database tier
- Often in multiple AZs for high availability
- No direct internet access

### Subnet Planning Best Practices

```
Production VPC (10.0.0.0/16)
├── Web Tier
│   ├── Public Subnet AZ-1a (10.0.1.0/24)
│   └── Public Subnet AZ-1b (10.0.2.0/24)
├── Application Tier
│   ├── Private Subnet AZ-1a (10.0.11.0/24)
│   └── Private Subnet AZ-1b (10.0.12.0/24)
└── Database Tier
    ├── Private Subnet AZ-1a (10.0.21.0/24)
    └── Private Subnet AZ-1b (10.0.22.0/24)
```

### Subnet Considerations
- **Availability Zone**: Each subnet exists in one AZ
- **IP Addressing**: Must be subset of VPC CIDR block
- **Auto-assign Public IP**: Configure for public subnets
- **Network ACLs**: Subnet-level security

## Internet Gateway (IGW)

### What is an Internet Gateway?
A horizontally scaled, redundant, and highly available VPC component that allows communication between instances in your VPC and the internet.

### Key Features
- **Highly Available**: Redundant across multiple AZs
- **Scalable**: Automatically scales bandwidth
- **No Bandwidth Constraints**: No limits imposed by IGW
- **One per VPC**: Only one IGW can be attached per VPC

### Requirements for Internet Access
1. **Internet Gateway**: Attached to VPC
2. **Route Table**: Route to IGW (0.0.0.0/0)
3. **Public IP**: Instance must have public IP/Elastic IP
4. **Security Groups**: Allow traffic
5. **NACLs**: Allow traffic

### IGW vs NAT Gateway

| Feature | Internet Gateway | NAT Gateway |
|---------|------------------|-------------|
| Purpose | Bidirectional internet access | Outbound-only internet access |
| Instance Type | Public instances | Private instances |
| IP Address | Public IP required | Private IP only |
| Inbound Traffic | Allowed | Not allowed |
| Cost | Free | Charges apply |

## NAT Gateway and NAT Instance

### NAT Gateway

#### Features
- **Managed Service**: Fully managed by AWS
- **High Availability**: Automatically redundant within AZ
- **Bandwidth**: Up to 45 Gbps
- **No Security Groups**: Cannot apply security groups
- **Automatic Failover**: Within the same AZ

#### Deployment Patterns

**Single AZ NAT Gateway (Not Recommended)**
```
VPC
├── Public Subnet AZ-1a
│   └── NAT Gateway
├── Private Subnet AZ-1a
│   └── EC2 instances → NAT Gateway
└── Private Subnet AZ-1b
    └── EC2 instances → NAT Gateway (Cross-AZ traffic)
```

**Multi-AZ NAT Gateway (Recommended)**
```
VPC
├── Public Subnet AZ-1a
│   └── NAT Gateway A
├── Public Subnet AZ-1b
│   └── NAT Gateway B
├── Private Subnet AZ-1a
│   └── EC2 instances → NAT Gateway A
└── Private Subnet AZ-1b
    └── EC2 instances → NAT Gateway B
```

### NAT Instance

#### Features
- **EC2 Instance**: You manage the instance
- **Customizable**: Can install software, monitoring agents
- **Security Groups**: Can apply security groups
- **Lower Cost**: Potentially cheaper for low traffic
- **Source/Destination Check**: Must disable

#### NAT Gateway vs NAT Instance

| Feature | NAT Gateway | NAT Instance |
|---------|-------------|--------------|
| Availability | Highly available within AZ | Use script for failover |
| Bandwidth | Up to 45 Gbps | Depends on instance type |
| Maintenance | Managed by AWS | Managed by you |
| Cost | Higher | Lower (potentially) |
| Security Groups | Not supported | Supported |
| Bastion Server | Not supported | Can be used as one |

## Route Tables

### What are Route Tables?
A set of rules (routes) that determine where network traffic from your subnet or gateway is directed.

### Types of Route Tables

#### Main Route Table
- **Default**: Created with VPC
- **Association**: Subnets not explicitly associated with custom route table
- **Best Practice**: Keep main route table private

#### Custom Route Table
- **Created**: For specific routing requirements
- **Explicit Association**: Subnets explicitly associated

### Route Priority
Routes are evaluated in this order:
1. **Most Specific**: Longest prefix match
2. **Local Routes**: Always take precedence
3. **Static Routes**: Manually configured routes
4. **Dynamic Routes**: From VGW propagation

### Example Route Table Configurations

#### Public Subnet Route Table
```
Destination     Target
10.0.0.0/16    Local
0.0.0.0/0      IGW-xxxxxxxx
```

#### Private Subnet Route Table
```
Destination     Target
10.0.0.0/16    Local
0.0.0.0/0      NAT-xxxxxxxx
```

#### VPN Route Table
```
Destination     Target
10.0.0.0/16    Local
192.168.0.0/16 VGW-xxxxxxxx
0.0.0.0/0      NAT-xxxxxxxx
```

### Route Table Best Practices
- **Separate Route Tables**: Different tables for public/private subnets
- **Least Privilege**: Only necessary routes
- **Documentation**: Name and tag route tables clearly
- **Regular Review**: Audit routes periodically

## Security Groups

### What are Security Groups?
Virtual firewalls that control inbound and outbound traffic at the instance level.

### Key Characteristics
- **Stateful**: Return traffic is automatically allowed
- **Default Deny**: All inbound traffic denied by default
- **Allow Rules Only**: Cannot create deny rules
- **Instance Level**: Applied to ENI (Elastic Network Interface)
- **Multiple Groups**: Up to 5 security groups per instance

### Security Group Rules

#### Inbound Rules
- **Type**: Protocol (HTTP, HTTPS, SSH, RDP, Custom)
- **Port Range**: Specific port or range
- **Source**: IP address, CIDR block, or another security group

#### Outbound Rules
- **Default**: All outbound traffic allowed (0.0.0.0/0 on all ports)
- **Customizable**: Can restrict outbound traffic

### Common Security Group Patterns

#### Web Server Security Group
```
Inbound Rules:
- HTTP (80) from 0.0.0.0/0
- HTTPS (443) from 0.0.0.0/0
- SSH (22) from Admin-SG

Outbound Rules:
- All traffic to 0.0.0.0/0
```

#### Database Security Group
```
Inbound Rules:
- MySQL (3306) from Web-Server-SG
- SSH (22) from Admin-SG

Outbound Rules:
- HTTPS (443) to 0.0.0.0/0 (for updates)
```

#### Application Load Balancer Security Group
```
Inbound Rules:
- HTTP (80) from 0.0.0.0/0
- HTTPS (443) from 0.0.0.0/0

Outbound Rules:
- HTTP (80) to Web-Server-SG
- HTTPS (443) to Web-Server-SG
```

### Security Group Referencing
Instead of IP addresses, reference other security groups:
```
Database-SG allows MySQL (3306) from Web-Server-SG
```

Benefits:
- **Dynamic**: Automatically includes new instances
- **Secure**: No need to know IP addresses
- **Maintainable**: Easier to manage

## Network ACLs (NACLs)

### What are Network ACLs?
Network Access Control Lists act as a subnet-level firewall, controlling traffic in and out of subnets.

### Key Characteristics
- **Stateless**: Must allow both inbound and outbound traffic
- **Subnet Level**: Applied to entire subnet
- **Rule Numbers**: Rules processed in order (lowest first)
- **Default Allow**: Default NACL allows all traffic
- **Deny Rules**: Support both allow and deny rules

### NACL vs Security Groups

| Feature | Network ACL | Security Group |
|---------|-------------|----------------|
| Level | Subnet | Instance |
| State | Stateless | Stateful |
| Rules | Allow and Deny | Allow only |
| Order | Rule number order | All rules evaluated |
| Default | Allow all | Deny all inbound |

### NACL Rule Structure
```
Rule #  Type        Protocol  Port Range  Source/Destination  Allow/Deny
100     HTTP        TCP       80          0.0.0.0/0          ALLOW
110     HTTPS       TCP       443         0.0.0.0/0          ALLOW
120     SSH         TCP       22          10.0.0.0/16        ALLOW
*       ALL         ALL       ALL         0.0.0.0/0          DENY
```

### NACL Best Practices
- **Default NACL**: Leave default NACL open, use security groups
- **Custom NACLs**: Create for specific security requirements
- **Rule Numbers**: Leave gaps (100, 200, 300) for future rules
- **Ephemeral Ports**: Remember to allow return traffic ports

### Ephemeral Ports
For stateless NACLs, allow ephemeral ports for return traffic:
- **Linux**: 32768-65535
- **Windows**: 1024-65535
- **NAT Gateway**: 1024-65535

## VPC Endpoints

### What are VPC Endpoints?
Private connections between VPC and supported AWS services without requiring internet gateway, NAT device, VPN connection, or AWS Direct Connect.

### Types of VPC Endpoints

#### Interface Endpoints (VPC Endpoint - ENI)
- **Technology**: Elastic Network Interface with private IP
- **Services**: Most AWS services (S3, DynamoDB, EC2, etc.)
- **DNS**: Private DNS names resolve to private IP
- **Cost**: Charged per hour and per GB processed
- **Security Groups**: Can apply security groups

#### Gateway Endpoints
- **Technology**: Gateway that you specify as target in route table
- **Services**: S3 and DynamoDB only
- **Cost**: Free
- **Route Table**: Requires route table entry
- **Security**: Use policies, not security groups

### VPC Endpoint Policies
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::my-bucket/*",
      "Condition": {
        "StringEquals": {
          "aws:PrincipalVpc": "vpc-12345678"
        }
      }
    }
  ]
}
```

### Use Cases
- **Security**: Keep traffic within AWS network
- **Compliance**: Meet data residency requirements
- **Cost**: Reduce NAT Gateway costs for AWS service access
- **Performance**: Lower latency and higher bandwidth

### Interface vs Gateway Endpoints

| Feature | Interface Endpoint | Gateway Endpoint |
|---------|-------------------|------------------|
| Services | Most AWS services | S3, DynamoDB only |
| Implementation | ENI with private IP | Target in route table |
| Cost | Hourly + data charges | Free |
| DNS | Private DNS support | Not applicable |
| Security Groups | Supported | Not supported |
| Cross-Region | Not supported | Not supported |

## VPC Peering

### What is VPC Peering?
A networking connection between two VPCs that enables routing traffic between them using private IPv4 or IPv6 addresses.

### Key Characteristics
- **One-to-One**: Connection between exactly two VPCs
- **Non-Transitive**: A-B and B-C peering doesn't enable A-C communication
- **Cross-Account**: Can peer VPCs across AWS accounts
- **Cross-Region**: Can peer VPCs across regions
- **No Single Point of Failure**: No bandwidth bottleneck

### VPC Peering Limitations
- **Overlapping CIDRs**: Cannot peer VPCs with overlapping IP ranges
- **Transitive Peering**: Not supported
- **Edge-to-Edge Routing**: Not supported through VGW, IGW, etc.

### VPC Peering Scenarios

#### Same Region Peering
```
VPC-A (10.0.0.0/16) ←→ VPC-B (172.31.0.0/16)
```

#### Cross-Region Peering
```
VPC-US-East (10.0.0.0/16) ←→ VPC-EU-West (172.31.0.0/16)
```

#### Cross-Account Peering
```
Account-A: VPC-Prod (10.0.0.0/16) ←→ Account-B: VPC-Dev (172.31.0.0/16)
```

### VPC Peering Route Table Configuration
For VPC-A to communicate with VPC-B:
```
VPC-A Route Table:
Destination     Target
10.0.0.0/16    Local
172.31.0.0/16  pcx-xxxxxxxx

VPC-B Route Table:
Destination     Target
172.31.0.0/16  Local
10.0.0.0/16    pcx-xxxxxxxx
```

### VPC Peering Best Practices
- **CIDR Planning**: Ensure non-overlapping CIDR blocks
- **Security Groups**: Update to allow cross-VPC communication
- **DNS Resolution**: Enable DNS resolution for peered VPCs
- **Monitoring**: Monitor peering connection metrics

## Transit Gateway

### What is Transit Gateway?
A network transit hub that connects VPCs and on-premises networks through a central hub.

### Key Features
- **Central Hub**: Single point of connectivity
- **Scalable**: Up to 5000 VPC attachments
- **Transitive Routing**: Full mesh connectivity
- **Cross-Account**: Share across AWS accounts
- **Cross-Region**: Connect to other regions via peering

### Transit Gateway Components

#### Attachments
- **VPC**: Attach VPCs to Transit Gateway
- **VPN**: Site-to-Site VPN connections
- **Direct Connect**: Direct Connect Gateways
- **Peering**: Other Transit Gateways
- **Connect**: SD-WAN appliances

#### Route Tables
- **Default**: Comes with default route table
- **Custom**: Create multiple route tables for segmentation
- **Propagation**: Automatically learn routes
- **Association**: Associate attachments with route tables

### Transit Gateway Routing

#### Default Route Table Behavior
All attachments can communicate with each other:
```
VPC-A ←→ Transit Gateway ←→ VPC-B
        ←→ VPN Connection
        ←→ Direct Connect
```

#### Segmented Routing
Separate route tables for security:
```
Production Route Table:
- VPC-Prod
- Direct Connect

Development Route Table:
- VPC-Dev
- VPC-Test

Shared Services Route Table:
- VPC-Shared (DNS, AD)
```

### Transit Gateway vs VPC Peering

| Feature | Transit Gateway | VPC Peering |
|---------|-----------------|-------------|
| Scalability | Hub and spoke | Full mesh required |
| Transitive Routing | Supported | Not supported |
| Cross-Region | TGW Peering | Native support |
| Bandwidth | 50 Gbps per VPC | No limit |
| Cost | Per attachment + data | Data processing only |
| Complexity | Centralized | Distributed |

### Use Cases
- **Hub and Spoke**: Central connectivity model
- **Multi-Account**: Connect VPCs across accounts
- **Hybrid Cloud**: Connect on-premises and cloud
- **Network Segmentation**: Isolate traffic with route tables

## Direct Connect

### What is AWS Direct Connect?
A cloud service that links your network directly to AWS to deliver consistent, high-bandwidth, low-latency connection.

### Key Benefits
- **Consistent Performance**: Predictable bandwidth and latency
- **Cost Reduction**: Reduce network costs for large data transfers
- **Security**: Private connection, doesn't traverse internet
- **Bandwidth**: Up to 100 Gbps per connection

### Direct Connect Components

#### Direct Connect Gateway
- **Cross-Region**: Connect to multiple regions
- **Multiple VPCs**: Connect to multiple VPCs
- **Transit Gateway**: Can attach to Transit Gateway

#### Virtual Interfaces (VIFs)
- **Private VIF**: Access VPC using private IP addresses
- **Public VIF**: Access AWS public services
- **Transit VIF**: Connect to Transit Gateway

### Connection Types

#### Dedicated Connection
- **Bandwidth**: 1 Gbps, 10 Gbps, 100 Gbps
- **Port**: Physical ethernet port dedicated to you
- **Timeline**: Typically 2-4 weeks to establish

#### Hosted Connection
- **Bandwidth**: 50 Mbps to 10 Gbps
- **Provider**: Through AWS Direct Connect Partners
- **Timeline**: Faster setup through partner

### Direct Connect Architectures

#### Single Connection (Not Recommended)
```
On-Premises ——— Direct Connect ——— AWS VPC
```

#### Redundant Connections (Recommended)
```
On-Premises ——— Direct Connect 1 ——— AWS VPC
            ——— Direct Connect 2 ——— AWS VPC
```

#### Backup with VPN
```
On-Premises ——— Direct Connect (Primary) ——— AWS VPC
            ——— Site-to-Site VPN (Backup) ——— AWS VPC
```

### Direct Connect Pricing
- **Port Hours**: Hourly charge for dedicated port
- **Data Transfer**: Outbound data transfer charges
- **Cross Connect**: Additional charges at colocation facility

### Direct Connect Best Practices
- **Redundancy**: Multiple connections for high availability
- **BGP**: Use BGP communities for routing control
- **Monitoring**: Monitor connection health and performance
- **Security**: Use MACsec for layer 2 encryption

## Site-to-Site VPN

### What is Site-to-Site VPN?
A secure connection between your on-premises equipment and your VPCs using IPSec VPN tunnels.

### Components

#### Virtual Private Gateway (VGW)
- **VPC Side**: VPN concentrator on AWS side
- **Highly Available**: Redundant across multiple AZs
- **BGP Support**: Dynamic routing with BGP
- **Static Routing**: Static routes configuration

#### Customer Gateway (CGW)
- **On-Premises**: Physical device or software on customer side
- **Public IP**: Must have static public IP address
- **BGP ASN**: Border Gateway Protocol Autonomous System Number

#### VPN Connection
- **Two Tunnels**: Redundant IPSec tunnels for high availability
- **Encryption**: AES 128/256, SHA-1/SHA-256
- **DPD**: Dead Peer Detection for tunnel monitoring

### VPN Routing

#### Static Routing
```
Route Table Entry:
Destination: 192.168.0.0/16
Target: VGW-xxxxxxxx
```

#### Dynamic Routing (BGP)
- **Route Propagation**: Enable route propagation on route table
- **Automatic**: Routes learned dynamically via BGP
- **Failover**: Automatic failover between tunnels

### Site-to-Site VPN Configuration Example
```
Customer Gateway:
- IP Address: 203.0.113.12
- BGP ASN: 65000
- Routing: Dynamic (BGP)

VPN Connection:
- Tunnel 1: 169.254.255.1/30
- Tunnel 2: 169.254.255.5/30
- Pre-shared Key: Generated by AWS
```

### VPN Performance
- **Bandwidth**: Up to 1.25 Gbps per tunnel
- **Latency**: Internet-dependent
- **Throughput**: Can use multiple tunnels for higher bandwidth

### Site-to-Site VPN vs Direct Connect

| Feature | Site-to-Site VPN | Direct Connect |
|---------|------------------|----------------|
| Setup Time | Minutes | Weeks |
| Bandwidth | Up to 1.25 Gbps | Up to 100 Gbps |
| Cost | Lower | Higher |
| Consistency | Internet-dependent | Predictable |
| Security | IPSec encrypted | Private connection |

## Client VPN

### What is AWS Client VPN?
A managed client-based VPN service that enables secure access to AWS resources and on-premises networks.

### Key Features
- **Managed Service**: Fully managed by AWS
- **Scalable**: Automatically scales up/down
- **Secure**: Strong authentication and encryption
- **Split Tunneling**: Route specific traffic through VPN

### Client VPN Components

#### Client VPN Endpoint
- **Entry Point**: VPN connection endpoint for clients
- **Subnet Association**: Associate with VPC subnets
- **Authentication**: Various authentication methods
- **Authorization**: Control client access

#### Authentication Methods
- **Active Directory**: Integration with Microsoft AD
- **Mutual TLS**: Certificate-based authentication
- **SAML**: Single Sign-On with SAML providers
- **Federated**: AWS SSO integration

### Client VPN Architecture
```
Remote Users ——— Internet ——— Client VPN Endpoint ——— VPC Resources
                                    ——— On-Premises (via VPN/DX)
```

### Authorization Rules
Control which clients can access which resources:
```
Rule 1: Allow 10.0.0.0/16 for group "Developers"
Rule 2: Allow 10.0.1.0/24 for group "Admins"
Rule 3: Deny all for everyone else
```

### Client VPN Best Practices
- **Least Privilege**: Grant minimum required access
- **Monitoring**: Enable CloudTrail logging
- **Authentication**: Use strong authentication methods
- **Split Tunneling**: Configure for optimal performance

## Elastic Load Balancer (ELB)

### What is ELB?
A managed load balancing service that automatically distributes incoming application traffic across multiple targets.

### Types of Load Balancers

#### Application Load Balancer (ALB) - Layer 7
- **Protocol**: HTTP/HTTPS
- **Features**: Content-based routing, WebSocket, HTTP/2
- **Target Types**: EC2 instances, IP addresses, Lambda functions
- **Use Cases**: Microservices, container-based applications

#### Network Load Balancer (NLB) - Layer 4
- **Protocol**: TCP/UDP/TLS
- **Performance**: Ultra-high performance (millions of requests/sec)
- **Target Types**: EC2 instances, IP addresses, ALB
- **Use Cases**: High-performance applications, static IP requirements

#### Gateway Load Balancer (GWLB) - Layer 3/4
- **Protocol**: GENEVE protocol
- **Use Cases**: Security appliances, firewalls, intrusion detection
- **Target Types**: EC2 instances, IP addresses
- **Features**: Transparent network gateway

### Load Balancer Features

#### Health Checks
- **Purpose**: Determine target health
- **Protocol**: HTTP/HTTPS/TCP/gRPC
- **Parameters**: Interval, timeout, healthy/unhealthy thresholds
- **Path**: Health check path for HTTP/HTTPS

#### Sticky Sessions (Session Affinity)
- **ALB**: Cookie-based stickiness
- **Duration**: 1 second to 7 days
- **Use Case**: Maintain user sessions

#### Cross-Zone Load Balancing
- **ALB**: Always enabled
- **NLB**: Disabled by default (can enable)
- **Classic**: Disabled by default (can enable)

### ALB Routing Rules

#### Host-Based Routing
```
api.example.com → API Target Group
web.example.com → Web Target Group
```

#### Path-Based Routing
```
example.com/api/* → API Target Group
example.com/images/* → Static Content Target Group
```

#### HTTP Method Routing
```
GET requests → Read Target Group
POST/PUT requests → Write Target Group
```

### Target Groups
- **Purpose**: Route requests to registered targets
- **Health Checks**: Per target group
- **Protocols**: HTTP/HTTPS (ALB), TCP/UDP/TLS (NLB)
- **Targets**: EC2 instances, IP addresses, Lambda functions

### Load Balancer Security
- **Security Groups**: Apply to ALB (not NLB)
- **SSL/TLS**: Terminate SSL at load balancer
- **Certificates**: AWS Certificate Manager integration
- **WAF**: Web Application Firewall integration (ALB only)

### Load Balancer Monitoring
- **CloudWatch Metrics**: Request count, latency, error rates
- **Access Logs**: Detailed request logs to S3
- **AWS X-Ray**: Request tracing for ALB

## CloudFront

### What is Amazon CloudFront?
A fast content delivery network (CDN) service that securely delivers data, videos, applications, and APIs globally with low latency.

### Key Components

#### Distributions
- **Web Distribution**: For websites, APIs, video streaming
- **RTMP Distribution**: For media streaming (deprecated)
- **Origins**: Source of content (S3, ALB, EC2, custom)
- **Behaviors**: How CloudFront handles requests

#### Edge Locations
- **Global Network**: 400+ edge locations worldwide
- **Regional Caches**: Larger caches for less popular content
- **POP**: Points of Presence for content delivery

### CloudFront Origins

#### S3 Origins
- **Static Content**: Images, CSS, JavaScript, videos
- **Origin Access Identity**: Restrict S3 access to CloudFront only
- **S3 Transfer Acceleration**: Use CloudFront edge locations

#### Custom Origins (HTTP/HTTPS)
- **Application Load Balancer**: Dynamic content from ALB
- **EC2 Instance**: Direct connection to EC2
- **On-Premises**: Your own web servers
- **API Gateway**: REST APIs

### Cache Behaviors
Control how CloudFront handles different types of requests:

```
Path Pattern: /api/*
Origin: ALB-API
TTL: 0 (no caching)
Allowed Methods: GET, HEAD, OPTIONS, PUT, PATCH, POST, DELETE

Path Pattern: /images/*
Origin: S3-Bucket
TTL: 86400 (24 hours)
Allowed Methods: GET, HEAD
```

### Caching
- **TTL (Time To Live)**: How long objects stay in cache
- **Cache-Control Headers**: Respect origin cache headers
- **Query String Parameters**: Include in cache key
- **Cookies**: Forward cookies to origin
- **Cache Invalidation**: Manually remove objects from cache

### CloudFront Security

#### Signed URLs and Signed Cookies
- **Signed URLs**: Control access to individual files
- **Signed Cookies**: Control access to multiple files
- **Use Cases**: Premium content, private content

#### Origin Access Identity (OAI)
```
User → CloudFront → S3 (OAI only access)
```
Prevents direct S3 access, forces traffic through CloudFront.

#### AWS WAF Integration
- **Web Application Firewall**: Protect against common exploits
- **Rules**: IP filtering, geo-blocking, SQL injection protection
- **Rate Limiting**: Control request rates

### CloudFront Pricing
- **Data Transfer**: Outbound data transfer charges
- **Requests**: HTTP/HTTPS request charges
- **Regional Pricing**: Different prices per region
- **Price Classes**: All, 100, 200 edge locations

### Use Cases
- **Static Website**: S3 + CloudFront for global delivery
- **Dynamic Content**: ALB + CloudFront for acceleration
- **API Acceleration**: API Gateway + CloudFront
- **Video Streaming**: S3 + CloudFront for video delivery

## Route 53

### What is Amazon Route 53?
A scalable Domain Name System (DNS) web service designed to route end users to internet applications.

### Key Features
- **Domain Registration**: Register new domains
- **DNS Hosting**: Host DNS for your domains
- **Health Checking**: Monitor endpoint health
- **Traffic Routing**: Intelligent traffic routing

### DNS Record Types

#### Common Record Types
- **A Record**: IPv4 address mapping
- **AAAA Record**: IPv6 address mapping
- **CNAME Record**: Canonical name (alias)
- **MX Record**: Mail exchange servers
- **TXT Record**: Text information
- **NS Record**: Name server records
- **SOA Record**: Start of authority

#### AWS-Specific Records
- **Alias Record**: AWS resource mapping (free queries)
- **Route 53 Specific**: Can point to AWS resources directly

### Routing Policies

#### Simple Routing
- **Single Resource**: One IP address per record
- **No Health Checks**: Basic DNS resolution
- **Use Case**: Single web server

#### Weighted Routing
- **Traffic Distribution**: Distribute traffic by weight
- **A/B Testing**: Test new versions with small traffic
- **Blue/Green Deployments**: Gradual traffic shifting

```
Record 1: 70% traffic to Server A
Record 2: 30% traffic to Server B
```

#### Latency-Based Routing
- **Lowest Latency**: Route to lowest latency endpoint
- **Global Applications**: Serve users from nearest region
- **Health Checks**: Failover if endpoint unhealthy

#### Failover Routing
- **Primary/Secondary**: Active-passive failover
- **Health Checks**: Required for failover logic
- **Disaster Recovery**: Automatic failover to backup

#### Geolocation Routing
- **Geographic Location**: Route based on user location
- **Content Localization**: Serve localized content
- **Compliance**: Meet data residency requirements

#### Geoproximity Routing
- **Traffic Flow**: Route based on geographic location and bias
- **Bias Values**: Shift more/less traffic to resources
- **Use Case**: Gradually shift traffic between regions

#### Multivalue Answer Routing
- **Multiple Values**: Return multiple IP addresses
- **Health Checks**: Only return healthy endpoints
- **Load Distribution**: Simple load distribution

### Health Checks
- **HTTP/HTTPS**: Check web server health
- **TCP**: Check port connectivity
- **Calculated**: Combine multiple health checks
- **CloudWatch Alarms**: Based on CloudWatch metrics

#### Health Check Types
```
HTTP Health Check:
- Endpoint: web-server.example.com
- Port: 80
- Path: /health
- Interval: 30 seconds
- Failure Threshold: 3
```

### Route 53 Resolver

#### DNS Resolution
- **Recursive DNS**: Resolve queries for VPC resources
- **Conditional Forwarding**: Forward queries to on-premises DNS
- **Outbound Endpoints**: Forward VPC queries to external DNS
- **Inbound Endpoints**: Resolve on-premises queries for AWS resources

#### Hybrid DNS Architecture
```
On-Premises DNS ←→ Route 53 Resolver ←→ VPC DNS
```

### Private Hosted Zones
- **VPC Association**: Associate with specific VPCs
- **Internal DNS**: Resolve internal domain names
- **Split-Horizon DNS**: Different resolution for internal/external

### Route 53 Pricing
- **Hosted Zones**: Monthly charge per hosted zone
- **Queries**: Charge per DNS query (except Alias queries)
- **Health Checks**: Monthly charge per health check
- **Domain Registration**: Annual domain registration fees

## AWS Global Accelerator

### What is AWS Global Accelerator?
A networking service that improves the performance of your users' traffic by up to 60% using Amazon's global network infrastructure.

### Key Features
- **Static IP Addresses**: 2 static IPv4 addresses
- **Global Network**: Use AWS global network
- **Performance**: Reduce latency and jitter
- **DDoS Protection**: AWS Shield Standard included

### Components

#### Accelerator
- **Static IPs**: 2 anycast IP addresses
- **Listeners**: Listen for connections on specific ports
- **Endpoint Groups**: Route traffic to endpoints in regions

#### Listeners
- **Protocol**: TCP or UDP
- **Port Range**: Single port or port ranges
- **Client Affinity**: Source IP or None

#### Endpoint Groups
- **Region**: AWS region containing endpoints
- **Traffic Dial**: Percentage of traffic to region
- **Health Check**: Monitor endpoint health

#### Endpoints
- **Types**: ALB, NLB, EC2 instances, Elastic IP addresses
- **Weight**: Traffic distribution within endpoint group
- **Health**: Healthy/unhealthy status

### Global Accelerator vs CloudFront

| Feature | Global Accelerator | CloudFront |
|---------|-------------------|------------|
| Use Case | Non-HTTP traffic, gaming, IoT | HTTP/HTTPS, static/dynamic content |
| Caching | No caching | Content caching |
| Protocol | TCP/UDP | HTTP/HTTPS/WebSocket |
| IP Addresses | 2 static anycast IPs | Dynamic IP addresses |
| Performance | Network optimization | Caching + network optimization |

### Traffic Flow
```
User → Edge Location → AWS Global Network → Target Endpoint
```

### Use Cases
- **Gaming Applications**: Low-latency gaming traffic
- **IoT Applications**: IoT device communication
- **VoIP Applications**: Voice over IP applications
- **Non-HTTP Protocols**: Any TCP/UDP applications

### Pricing
- **Fixed Fee**: Per accelerator per month
- **Data Transfer**: Premium tier data transfer pricing
- **DDoS Protection**: AWS Shield Standard included

## Network Security

### Defense in Depth
AWS networking provides multiple layers of security:

```
Internet
    ↓
AWS Shield (DDoS Protection)
    ↓
AWS WAF (Application Firewall)
    ↓
CloudFront (CDN)
    ↓
Application Load Balancer
    ↓
Security Groups (Instance Firewall)
    ↓
Network ACLs (Subnet Firewall)
    ↓
EC2 Instances
```

### AWS Shield
- **Standard**: Free DDoS protection for all AWS customers
- **Advanced**: Enhanced DDoS protection with 24/7 support
- **Attack Mitigation**: Automatic attack detection and mitigation
- **Cost Protection**: DDoS cost protection for Advanced tier

### AWS WAF (Web Application Firewall)
- **Application Layer**: Layer 7 protection
- **Rules**: IP filtering, SQL injection, XSS protection
- **Rate Limiting**: Control request rates
- **Integration**: ALB, CloudFront, API Gateway

#### WAF Rule Examples
```
IP Blacklist Rule:
- Block traffic from specific IP ranges

SQL Injection Rule:
- Block requests with SQL injection patterns

Rate Limiting Rule:
- Allow max 2000 requests per 5 minutes per IP
```

### Network Segmentation

#### Micro-Segmentation with Security Groups
```
Web Tier SG:
- Allow HTTP/HTTPS from Internet
- Allow SSH from Bastion SG

App Tier SG:
- Allow App ports from Web Tier SG
- Allow SSH from Bastion SG

DB Tier SG:
- Allow DB ports from App Tier SG
- Allow SSH from Bastion SG

Bastion SG:
- Allow SSH from Admin IP ranges
```

#### Network Segmentation with Subnets
- **Public Subnets**: Web tier, load balancers
- **Private Subnets**: Application tier, databases
- **Isolated Subnets**: Highly sensitive workloads

### VPC Flow Logs
Monitor network traffic for security analysis:
- **Capture**: All network traffic in/out of VPC
- **Storage**: CloudWatch Logs, S3, Kinesis Data Firehose
- **Analysis**: Detect unusual traffic patterns
- **Compliance**: Meet audit requirements

#### Flow Log Format
```
account-id interface-id srcaddr dstaddr srcport dstport protocol packets bytes windowstart windowend action flowlogstatus
```

### Network Monitoring and Alerting

#### CloudWatch Metrics
- **VPC Flow Logs**: Network traffic analysis
- **Security Group**: Connection tracking
- **Load Balancer**: Request metrics and error rates
- **NAT Gateway**: Data processing metrics

#### AWS Config Rules
- **Compliance**: Monitor network configuration compliance
- **Security Groups**: Detect overly permissive rules
- **NACLs**: Monitor NACL changes
- **Route Tables**: Track routing changes

### Best Practices
- **Least Privilege**: Minimum required network access
- **Defense in Depth**: Multiple security layers
- **Regular Audits**: Review security group rules
- **Monitoring**: Comprehensive network monitoring
- **Automation**: Automated security response

---

## AWS CLI Commands Reference

### VPC Endpoints

#### Create and Manage VPC Endpoints
```bash
# Create Gateway Endpoint for S3
aws ec2 create-vpc-endpoint \
    --vpc-id vpc-0123456789abcdef0 \
    --service-name com.amazonaws.us-east-1.s3 \
    --route-table-ids rtb-12345678 rtb-87654321 \
    --tag-specifications 'ResourceType=vpc-endpoint,Tags=[{Key=Name,Value=S3-Gateway-Endpoint},{Key=Environment,Value=Production}]'

# Create Gateway Endpoint for DynamoDB
aws ec2 create-vpc-endpoint \
    --vpc-id vpc-0123456789abcdef0 \
    --service-name com.amazonaws.us-east-1.dynamodb \
    --route-table-ids rtb-12345678 \
    --policy-document file://dynamodb-endpoint-policy.json

# Create Interface Endpoint for EC2
aws ec2 create-vpc-endpoint \
    --vpc-id vpc-0123456789abcdef0 \
    --vpc-endpoint-type Interface \
    --service-name com.amazonaws.us-east-1.ec2 \
    --subnet-ids subnet-abc123 subnet-def456 \
    --security-group-ids sg-0123456789abcdef0 \
    --private-dns-enabled \
    --tag-specifications 'ResourceType=vpc-endpoint,Tags=[{Key=Name,Value=EC2-Interface-Endpoint}]'

# Create Interface Endpoint for Systems Manager
aws ec2 create-vpc-endpoint \
    --vpc-id vpc-0123456789abcdef0 \
    --vpc-endpoint-type Interface \
    --service-name com.amazonaws.us-east-1.ssm \
    --subnet-ids subnet-abc123 subnet-def456 \
    --security-group-ids sg-0123456789abcdef0 \
    --private-dns-enabled

# Create Interface Endpoint for Secrets Manager
aws ec2 create-vpc-endpoint \
    --vpc-id vpc-0123456789abcdef0 \
    --vpc-endpoint-type Interface \
    --service-name com.amazonaws.us-east-1.secretsmanager \
    --subnet-ids subnet-abc123 subnet-def456 \
    --security-group-ids sg-0123456789abcdef0 \
    --private-dns-enabled
```

#### List and Describe VPC Endpoints
```bash
# List all VPC endpoints
aws ec2 describe-vpc-endpoints

# Describe specific VPC endpoint
aws ec2 describe-vpc-endpoints \
    --vpc-endpoint-ids vpce-0123456789abcdef0

# List VPC endpoints for a specific VPC
aws ec2 describe-vpc-endpoints \
    --filters "Name=vpc-id,Values=vpc-0123456789abcdef0" \
    --query 'VpcEndpoints[*].[VpcEndpointId,ServiceName,State]' \
    --output table

# List all Interface endpoints
aws ec2 describe-vpc-endpoints \
    --filters "Name=vpc-endpoint-type,Values=Interface" \
    --query 'VpcEndpoints[*].[VpcEndpointId,ServiceName,VpcId]' \
    --output table

# List available VPC endpoint services
aws ec2 describe-vpc-endpoint-services

# List VPC endpoint services with filter
aws ec2 describe-vpc-endpoint-services \
    --filters "Name=service-type,Values=Interface" \
    --query 'ServiceNames' \
    --output table
```

#### Modify VPC Endpoints
```bash
# Modify VPC endpoint to add route tables (Gateway endpoint)
aws ec2 modify-vpc-endpoint \
    --vpc-endpoint-id vpce-0123456789abcdef0 \
    --add-route-table-ids rtb-99999999

# Modify VPC endpoint to remove route tables
aws ec2 modify-vpc-endpoint \
    --vpc-endpoint-id vpce-0123456789abcdef0 \
    --remove-route-table-ids rtb-88888888

# Modify Interface endpoint to add subnets
aws ec2 modify-vpc-endpoint \
    --vpc-endpoint-id vpce-0123456789abcdef0 \
    --add-subnet-ids subnet-xyz789

# Modify Interface endpoint security groups
aws ec2 modify-vpc-endpoint \
    --vpc-endpoint-id vpce-0123456789abcdef0 \
    --add-security-group-ids sg-newgroup123 \
    --remove-security-group-ids sg-oldgroup456

# Enable private DNS for Interface endpoint
aws ec2 modify-vpc-endpoint \
    --vpc-endpoint-id vpce-0123456789abcdef0 \
    --private-dns-enabled

# Update endpoint policy
aws ec2 modify-vpc-endpoint \
    --vpc-endpoint-id vpce-0123456789abcdef0 \
    --policy-document file://updated-endpoint-policy.json
```

#### Delete VPC Endpoints
```bash
# Delete VPC endpoint
aws ec2 delete-vpc-endpoints \
    --vpc-endpoint-ids vpce-0123456789abcdef0

# Delete multiple VPC endpoints
aws ec2 delete-vpc-endpoints \
    --vpc-endpoint-ids vpce-0123456789abcdef0 vpce-abcdef0123456789
```

### AWS PrivateLink

#### Create and Manage Endpoint Services
```bash
# Create VPC endpoint service configuration
aws ec2 create-vpc-endpoint-service-configuration \
    --network-load-balancer-arns arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/net/my-nlb/1234567890abcdef \
    --acceptance-required \
    --tag-specifications 'ResourceType=vpc-endpoint-service,Tags=[{Key=Name,Value=MyPrivateLinkService}]'

# Create endpoint service without acceptance required
aws ec2 create-vpc-endpoint-service-configuration \
    --network-load-balancer-arns arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/net/my-nlb/1234567890abcdef \
    --no-acceptance-required

# Describe VPC endpoint service configurations
aws ec2 describe-vpc-endpoint-service-configurations

# Describe specific endpoint service
aws ec2 describe-vpc-endpoint-service-configurations \
    --service-ids vpce-svc-0123456789abcdef0

# Modify endpoint service configuration
aws ec2 modify-vpc-endpoint-service-configuration \
    --service-id vpce-svc-0123456789abcdef0 \
    --acceptance-required

# Add allowed principals to endpoint service
aws ec2 modify-vpc-endpoint-service-permissions \
    --service-id vpce-svc-0123456789abcdef0 \
    --add-allowed-principals arn:aws:iam::123456789012:root

# Remove allowed principals
aws ec2 modify-vpc-endpoint-service-permissions \
    --service-id vpce-svc-0123456789abcdef0 \
    --remove-allowed-principals arn:aws:iam::123456789012:root

# List endpoint service permissions
aws ec2 describe-vpc-endpoint-service-permissions \
    --service-id vpce-svc-0123456789abcdef0
```

#### Manage Endpoint Connections
```bash
# List endpoint connections
aws ec2 describe-vpc-endpoint-connections \
    --filters "Name=service-id,Values=vpce-svc-0123456789abcdef0"

# Accept endpoint connection request
aws ec2 accept-vpc-endpoint-connections \
    --service-id vpce-svc-0123456789abcdef0 \
    --vpc-endpoint-ids vpce-0123456789abcdef0

# Reject endpoint connection request
aws ec2 reject-vpc-endpoint-connections \
    --service-id vpce-svc-0123456789abcdef0 \
    --vpc-endpoint-ids vpce-0123456789abcdef0

# Delete VPC endpoint service configuration
aws ec2 delete-vpc-endpoint-service-configurations \
    --service-ids vpce-svc-0123456789abcdef0
```

### VPC Peering

#### Create and Manage VPC Peering Connections
```bash
# Create VPC peering connection (same account)
aws ec2 create-vpc-peering-connection \
    --vpc-id vpc-0123456789abcdef0 \
    --peer-vpc-id vpc-abcdef0123456789 \
    --tag-specifications 'ResourceType=vpc-peering-connection,Tags=[{Key=Name,Value=VPC-A-to-VPC-B}]'

# Create VPC peering connection (cross-account)
aws ec2 create-vpc-peering-connection \
    --vpc-id vpc-0123456789abcdef0 \
    --peer-vpc-id vpc-abcdef0123456789 \
    --peer-owner-id 123456789012 \
    --peer-region us-west-2 \
    --tag-specifications 'ResourceType=vpc-peering-connection,Tags=[{Key=Name,Value=Cross-Account-Peering}]'

# Accept VPC peering connection
aws ec2 accept-vpc-peering-connection \
    --vpc-peering-connection-id pcx-0123456789abcdef0

# Reject VPC peering connection
aws ec2 reject-vpc-peering-connection \
    --vpc-peering-connection-id pcx-0123456789abcdef0

# Describe VPC peering connections
aws ec2 describe-vpc-peering-connections

# Describe specific peering connection
aws ec2 describe-vpc-peering-connections \
    --vpc-peering-connection-ids pcx-0123456789abcdef0

# List peering connections for a VPC
aws ec2 describe-vpc-peering-connections \
    --filters "Name=requester-vpc-info.vpc-id,Values=vpc-0123456789abcdef0" \
    --query 'VpcPeeringConnections[*].[VpcPeeringConnectionId,Status.Code,AccepterVpcInfo.VpcId]' \
    --output table

# Delete VPC peering connection
aws ec2 delete-vpc-peering-connection \
    --vpc-peering-connection-id pcx-0123456789abcdef0
```

#### Modify VPC Peering Options
```bash
# Modify peering connection options (requester side)
aws ec2 modify-vpc-peering-connection-options \
    --vpc-peering-connection-id pcx-0123456789abcdef0 \
    --requester-peering-connection-options '{"AllowDnsResolutionFromRemoteVpc":true}'

# Modify peering connection options (accepter side)
aws ec2 modify-vpc-peering-connection-options \
    --vpc-peering-connection-id pcx-0123456789abcdef0 \
    --accepter-peering-connection-options '{"AllowDnsResolutionFromRemoteVpc":true}'

# Enable both DNS resolution and allow egress from local Classic link
aws ec2 modify-vpc-peering-connection-options \
    --vpc-peering-connection-id pcx-0123456789abcdef0 \
    --requester-peering-connection-options '{"AllowDnsResolutionFromRemoteVpc":true,"AllowEgressFromLocalClassicLinkToRemoteVpc":true}'
```

### Network Firewall

#### Create and Manage Network Firewall
```bash
# Create firewall policy
aws network-firewall create-firewall-policy \
    --firewall-policy-name MyFirewallPolicy \
    --firewall-policy '{"StatelessDefaultActions": ["aws:forward_to_sfe"], "StatelessFragmentDefaultActions": ["aws:forward_to_sfe"]}' \
    --tags Key=Environment,Value=Production

# Create firewall
aws network-firewall create-firewall \
    --firewall-name MyNetworkFirewall \
    --firewall-policy-arn arn:aws:network-firewall:us-east-1:123456789012:firewall-policy/MyFirewallPolicy \
    --vpc-id vpc-0123456789abcdef0 \
    --subnet-mappings SubnetId=subnet-abc123 SubnetId=subnet-def456 \
    --tags Key=Name,Value=ProductionFirewall

# Describe firewalls
aws network-firewall describe-firewall \
    --firewall-name MyNetworkFirewall

# List firewalls
aws network-firewall list-firewalls

# Update firewall policy
aws network-firewall update-firewall-policy \
    --firewall-policy-name MyFirewallPolicy \
    --firewall-policy-arn arn:aws:network-firewall:us-east-1:123456789012:firewall-policy/MyFirewallPolicy \
    --firewall-policy file://updated-policy.json

# Associate firewall policy with firewall
aws network-firewall associate-firewall-policy \
    --firewall-name MyNetworkFirewall \
    --firewall-policy-arn arn:aws:network-firewall:us-east-1:123456789012:firewall-policy/NewPolicy

# Delete firewall
aws network-firewall delete-firewall \
    --firewall-name MyNetworkFirewall

# Delete firewall policy
aws network-firewall delete-firewall-policy \
    --firewall-policy-name MyFirewallPolicy
```

#### Create Rule Groups
```bash
# Create stateless rule group
aws network-firewall create-rule-group \
    --rule-group-name AllowHTTPSStateless \
    --type STATELESS \
    --rule-group file://stateless-rules.json \
    --capacity 100 \
    --tags Key=Type,Value=Stateless

# Create stateful rule group
aws network-firewall create-rule-group \
    --rule-group-name BlockMaliciousDomains \
    --type STATEFUL \
    --rule-group file://stateful-rules.json \
    --capacity 1000 \
    --tags Key=Type,Value=Stateful

# Describe rule group
aws network-firewall describe-rule-group \
    --rule-group-name AllowHTTPSStateless \
    --type STATELESS

# List rule groups
aws network-firewall list-rule-groups

# Update rule group
aws network-firewall update-rule-group \
    --rule-group-name AllowHTTPSStateless \
    --type STATELESS \
    --rule-group file://updated-rules.json

# Delete rule group
aws network-firewall delete-rule-group \
    --rule-group-name AllowHTTPSStateless \
    --type STATELESS
```

### IPAM (IP Address Manager)

#### Create and Manage IPAM
```bash
# Create IPAM
aws ec2 create-ipam \
    --description "Organization-wide IP address management" \
    --operating-regions RegionName=us-east-1 RegionName=us-west-2 RegionName=eu-west-1 \
    --tag-specifications 'ResourceType=ipam,Tags=[{Key=Name,Value=Corporate-IPAM}]'

# Describe IPAMs
aws ec2 describe-ipams

# Describe specific IPAM
aws ec2 describe-ipams \
    --ipam-ids ipam-0123456789abcdef0

# Create IPAM scope
aws ec2 create-ipam-scope \
    --ipam-id ipam-0123456789abcdef0 \
    --description "Private scope for internal networks" \
    --tag-specifications 'ResourceType=ipam-scope,Tags=[{Key=Name,Value=PrivateScope}]'

# Create IPAM pool (top level)
aws ec2 create-ipam-pool \
    --ipam-scope-id ipam-scope-0123456789abcdef0 \
    --description "Top-level pool for 10.0.0.0/8" \
    --address-family ipv4 \
    --locale us-east-1 \
    --tag-specifications 'ResourceType=ipam-pool,Tags=[{Key=Name,Value=TopLevelPool}]'

# Provision CIDR to IPAM pool
aws ec2 provision-ipam-pool-cidr \
    --ipam-pool-id ipam-pool-0123456789abcdef0 \
    --cidr 10.0.0.0/8

# Create regional IPAM pool (child pool)
aws ec2 create-ipam-pool \
    --ipam-scope-id ipam-scope-0123456789abcdef0 \
    --description "US East regional pool" \
    --address-family ipv4 \
    --source-ipam-pool-id ipam-pool-0123456789abcdef0 \
    --locale us-east-1 \
    --allocation-min-netmask-length 24 \
    --allocation-max-netmask-length 16 \
    --allocation-default-netmask-length 20

# Allocate CIDR from IPAM pool
aws ec2 allocate-ipam-pool-cidr \
    --ipam-pool-id ipam-pool-child123456789 \
    --netmask-length 20

# List IPAM pools
aws ec2 describe-ipam-pools \
    --filters "Name=ipam-scope-id,Values=ipam-scope-0123456789abcdef0"

# Get IPAM pool allocations
aws ec2 get-ipam-pool-allocations \
    --ipam-pool-id ipam-pool-0123456789abcdef0

# Get IPAM pool CIDRs
aws ec2 get-ipam-pool-cidrs \
    --ipam-pool-id ipam-pool-0123456789abcdef0

# Delete IPAM pool
aws ec2 delete-ipam-pool \
    --ipam-pool-id ipam-pool-0123456789abcdef0

# Delete IPAM
aws ec2 delete-ipam \
    --ipam-id ipam-0123456789abcdef0
```

### Reachability Analyzer

#### Analyze Network Paths
```bash
# Create network insights path (EC2 to EC2)
aws ec2 create-network-insights-path \
    --source i-0123456789abcdef0 \
    --destination i-abcdef0123456789 \
    --protocol tcp \
    --destination-port 443 \
    --tag-specifications 'ResourceType=network-insights-path,Tags=[{Key=Name,Value=WebServer-To-Database}]'

# Create network insights path (with VPC endpoints)
aws ec2 create-network-insights-path \
    --source i-0123456789abcdef0 \
    --destination vpce-0123456789abcdef0 \
    --protocol tcp \
    --tag-specifications 'ResourceType=network-insights-path,Tags=[{Key=Name,Value=Instance-To-S3-Endpoint}]'

# Start network insights analysis
aws ec2 start-network-insights-analysis \
    --network-insights-path-id nip-0123456789abcdef0 \
    --tag-specifications 'ResourceType=network-insights-analysis,Tags=[{Key=Date,Value=2026-02-08}]'

# Describe network insights paths
aws ec2 describe-network-insights-paths

# Describe specific path
aws ec2 describe-network-insights-paths \
    --network-insights-path-ids nip-0123456789abcdef0

# Describe network insights analyses
aws ec2 describe-network-insights-analyses \
    --network-insights-path-id nip-0123456789abcdef0

# Get analysis results
aws ec2 describe-network-insights-analyses \
    --network-insights-analysis-ids nia-0123456789abcdef0 \
    --query 'NetworkInsightsAnalyses[0].{Status:Status,NetworkPathFound:NetworkPathFound,Explanations:Explanations}'

# Delete network insights analysis
aws ec2 delete-network-insights-analysis \
    --network-insights-analysis-id nia-0123456789abcdef0

# Delete network insights path
aws ec2 delete-network-insights-path \
    --network-insights-path-id nip-0123456789abcdef0
```

### Network Access Analyzer

#### Create and Manage Network Access Scopes
```bash
# Create network insights access scope
aws ec2 create-network-insights-access-scope \
    --match-paths-source '{"ResourceStatement":{"Resources":["vpc-0123456789abcdef0"]}}' \
    --match-paths-destination '{"ResourceStatement":{"Resources":["*"]}}' \
    --tag-specifications 'ResourceType=network-insights-access-scope,Tags=[{Key=Name,Value=VPC-Internet-Access}]'

# Describe network insights access scopes
aws ec2 describe-network-insights-access-scopes

# Get network insights access scope content
aws ec2 get-network-insights-access-scope-content \
    --network-insights-access-scope-id nis-0123456789abcdef0

# Start network insights access scope analysis
aws ec2 start-network-insights-access-scope-analysis \
    --network-insights-access-scope-id nis-0123456789abcdef0 \
    --tag-specifications 'ResourceType=network-insights-access-scope-analysis,Tags=[{Key=Analysis,Value=Quarterly-Review}]'

# Describe network insights access scope analyses
aws ec2 describe-network-insights-access-scope-analyses \
    --network-insights-access-scope-id nis-0123456789abcdef0

# Get access scope analysis findings
aws ec2 get-network-insights-access-scope-analysis-findings \
    --network-insights-access-scope-analysis-id nisa-0123456789abcdef0

# Delete network insights access scope analysis
aws ec2 delete-network-insights-access-scope-analysis \
    --network-insights-access-scope-analysis-id nisa-0123456789abcdef0

# Delete network insights access scope
aws ec2 delete-network-insights-access-scope \
    --network-insights-access-scope-id nis-0123456789abcdef0
```

### VPC Lattice

#### Create and Manage Service Network
```bash
# Create service network
aws vpc-lattice create-service-network \
    --name my-service-network \
    --auth-type AWS_IAM \
    --tags Key=Environment,Value=Production

# Create service
aws vpc-lattice create-service \
    --name my-application-service \
    --auth-type AWS_IAM \
    --tags Key=Application,Value=WebApp

# Associate service with service network
aws vpc-lattice create-service-network-service-association \
    --service-network-identifier sn-0123456789abcdef0 \
    --service-identifier svc-0123456789abcdef0 \
    --tags Key=Association,Value=WebApp-Network

# Create VPC association with service network
aws vpc-lattice create-service-network-vpc-association \
    --service-network-identifier sn-0123456789abcdef0 \
    --vpc-identifier vpc-0123456789abcdef0 \
    --security-group-ids sg-0123456789abcdef0 \
    --tags Key=VPC,Value=Production

# Create target group
aws vpc-lattice create-target-group \
    --name my-targets \
    --type IP \
    --config '{"Port":80,"Protocol":"HTTP","VpcIdentifier":"vpc-0123456789abcdef0"}' \
    --tags Key=TargetType,Value=WebServers

# Register targets
aws vpc-lattice register-targets \
    --target-group-identifier tg-0123456789abcdef0 \
    --targets Id=10.0.1.100,Port=80 Id=10.0.1.101,Port=80

# Create listener
aws vpc-lattice create-listener \
    --service-identifier svc-0123456789abcdef0 \
    --name default-listener \
    --protocol HTTPS \
    --port 443 \
    --default-action '{"Forward":{"TargetGroups":[{"TargetGroupIdentifier":"tg-0123456789abcdef0","Weight":100}]}}'

# List service networks
aws vpc-lattice list-service-networks

# List services
aws vpc-lattice list-services

# Describe service network
aws vpc-lattice get-service-network \
    --service-network-identifier sn-0123456789abcdef0

# Describe service
aws vpc-lattice get-service \
    --service-identifier svc-0123456789abcdef0

# Delete listener
aws vpc-lattice delete-listener \
    --service-identifier svc-0123456789abcdef0 \
    --listener-identifier listener-0123456789abcdef0

# Deregister targets
aws vpc-lattice deregister-targets \
    --target-group-identifier tg-0123456789abcdef0 \
    --targets Id=10.0.1.100

# Delete target group
aws vpc-lattice delete-target-group \
    --target-group-identifier tg-0123456789abcdef0

# Delete service network VPC association
aws vpc-lattice delete-service-network-vpc-association \
    --service-network-vpc-association-identifier snva-0123456789abcdef0

# Delete service network service association
aws vpc-lattice delete-service-network-service-association \
    --service-network-service-association-identifier snsa-0123456789abcdef0

# Delete service
aws vpc-lattice delete-service \
    --service-identifier svc-0123456789abcdef0

# Delete service network
aws vpc-lattice delete-service-network \
    --service-network-identifier sn-0123456789abcdef0
```

#### Manage Access Policies
```bash
# Put service network policy
aws vpc-lattice put-service-network-access-policy \
    --service-network-identifier sn-0123456789abcdef0 \
    --policy file://service-network-policy.json

# Get service network policy
aws vpc-lattice get-service-network-access-policy \
    --service-network-identifier sn-0123456789abcdef0

# Put service policy
aws vpc-lattice put-service-access-policy \
    --service-identifier svc-0123456789abcdef0 \
    --policy file://service-policy.json

# Get service policy
aws vpc-lattice get-service-access-policy \
    --service-identifier svc-0123456789abcdef0

# Delete service network policy
aws vpc-lattice delete-service-network-access-policy \
    --service-network-identifier sn-0123456789abcdef0

# Delete service policy
aws vpc-lattice delete-service-access-policy \
    --service-identifier svc-0123456789abcdef0
```

### Common Networking Queries

#### VPC and Subnet Information
```bash
# List all VPCs with their CIDR blocks
aws ec2 describe-vpcs \
    --query 'Vpcs[*].[VpcId,CidrBlock,IsDefault,Tags[?Key==`Name`].Value|[0]]' \
    --output table

# Find VPCs with specific CIDR
aws ec2 describe-vpcs \
    --filters "Name=cidr,Values=10.0.0.0/16"

# List all subnets in a VPC
aws ec2 describe-subnets \
    --filters "Name=vpc-id,Values=vpc-0123456789abcdef0" \
    --query 'Subnets[*].[SubnetId,CidrBlock,AvailabilityZone,MapPublicIpOnLaunch,Tags[?Key==`Name`].Value|[0]]' \
    --output table

# Find available IP addresses in subnet
aws ec2 describe-subnets \
    --subnet-ids subnet-abc123 \
    --query 'Subnets[0].AvailableIpAddressCount'

# List route tables for VPC
aws ec2 describe-route-tables \
    --filters "Name=vpc-id,Values=vpc-0123456789abcdef0" \
    --query 'RouteTables[*].[RouteTableId,Associations[0].SubnetId,Routes[0].DestinationCidrBlock]' \
    --output table
```

#### Security Group Analysis
```bash
# List all security groups in VPC
aws ec2 describe-security-groups \
    --filters "Name=vpc-id,Values=vpc-0123456789abcdef0" \
    --query 'SecurityGroups[*].[GroupId,GroupName,Description]' \
    --output table

# Find security groups with specific rule
aws ec2 describe-security-groups \
    --filters "Name=ip-permission.from-port,Values=22" \
    --query 'SecurityGroups[*].[GroupId,GroupName]' \
    --output table

# List all ingress rules for security group
aws ec2 describe-security-groups \
    --group-ids sg-0123456789abcdef0 \
    --query 'SecurityGroups[0].IpPermissions'

# Find unused security groups
for sg in $(aws ec2 describe-security-groups --query 'SecurityGroups[*].GroupId' --output text); do
  instances=$(aws ec2 describe-instances --filters "Name=instance.group-id,Values=$sg" --query 'Reservations[*].Instances[*].InstanceId' --output text)
  enis=$(aws ec2 describe-network-interfaces --filters "Name=group-id,Values=$sg" --query 'NetworkInterfaces[*].NetworkInterfaceId' --output text)
  if [ -z "$instances" ] && [ -z "$enis" ]; then
    echo "Unused SG: $sg"
  fi
done
```

#### Network Interface Information
```bash
# List all network interfaces
aws ec2 describe-network-interfaces

# Find network interfaces in subnet
aws ec2 describe-network-interfaces \
    --filters "Name=subnet-id,Values=subnet-abc123" \
    --query 'NetworkInterfaces[*].[NetworkInterfaceId,PrivateIpAddress,Status,Attachment.InstanceId]' \
    --output table

# Get network interface details
aws ec2 describe-network-interfaces \
    --network-interface-ids eni-0123456789abcdef0

# List elastic IP addresses
aws ec2 describe-addresses \
    --query 'Addresses[*].[PublicIp,InstanceId,AllocationId,AssociationId]' \
    --output table

# Find unattached elastic IPs
aws ec2 describe-addresses \
    --filters "Name=instance-id,Values=" \
    --query 'Addresses[*].[PublicIp,AllocationId]' \
    --output table
```

#### Connectivity Troubleshooting
```bash
# Check NAT Gateway status
aws ec2 describe-nat-gateways \
    --filter "Name=vpc-id,Values=vpc-0123456789abcdef0" \
    --query 'NatGateways[*].[NatGatewayId,State,SubnetId,NatGatewayAddresses[0].PublicIp]' \
    --output table

# Check Internet Gateway attachments
aws ec2 describe-internet-gateways \
    --filters "Name=attachment.vpc-id,Values=vpc-0123456789abcdef0" \
    --query 'InternetGateways[*].[InternetGatewayId,Attachments[0].State]' \
    --output table

# Verify VPC DNS settings
aws ec2 describe-vpc-attribute \
    --vpc-id vpc-0123456789abcdef0 \
    --attribute enableDnsSupport

aws ec2 describe-vpc-attribute \
    --vpc-id vpc-0123456789abcdef0 \
    --attribute enableDnsHostnames

# Check VPC flow logs
aws ec2 describe-flow-logs \
    --filter "Name=resource-id,Values=vpc-0123456789abcdef0" \
    --query 'FlowLogs[*].[FlowLogId,FlowLogStatus,LogDestinationType,LogGroupName]' \
    --output table

# Test reachability to instance
aws ec2 describe-instance-status \
    --instance-ids i-0123456789abcdef0 \
    --include-all-instances \
    --query 'InstanceStatuses[0].{Instance:InstanceId,State:InstanceState.Name,Status:InstanceStatus.Status,Reachability:SystemStatus.Status}'
```

#### Transit Gateway Queries
```bash
# List Transit Gateways
aws ec2 describe-transit-gateways \
    --query 'TransitGateways[*].[TransitGatewayId,State,OwnerId,Tags[?Key==`Name`].Value|[0]]' \
    --output table

# List Transit Gateway attachments
aws ec2 describe-transit-gateway-attachments \
    --filters "Name=transit-gateway-id,Values=tgw-0123456789abcdef0" \
    --query 'TransitGatewayAttachments[*].[TransitGatewayAttachmentId,ResourceType,ResourceId,State]' \
    --output table

# List Transit Gateway route tables
aws ec2 describe-transit-gateway-route-tables \
    --filters "Name=transit-gateway-id,Values=tgw-0123456789abcdef0"

# Search Transit Gateway routes
aws ec2 search-transit-gateway-routes \
    --transit-gateway-route-table-id tgw-rtb-0123456789abcdef0 \
    --filters "Name=type,Values=static"
```

#### Advanced Filtering and Reporting
```bash
# Generate VPC inventory report
echo "VPC_ID,CIDR,Subnets,IGW,NAT_Gateways,Peering_Connections"
for vpc in $(aws ec2 describe-vpcs --query 'Vpcs[*].VpcId' --output text); do
  cidr=$(aws ec2 describe-vpcs --vpc-ids $vpc --query 'Vpcs[0].CidrBlock' --output text)
  subnets=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$vpc" --query 'length(Subnets)')
  igw=$(aws ec2 describe-internet-gateways --filters "Name=attachment.vpc-id,Values=$vpc" --query 'length(InternetGateways)')
  nat=$(aws ec2 describe-nat-gateways --filter "Name=vpc-id,Values=$vpc" "Name=state,Values=available" --query 'length(NatGateways)')
  pcx=$(aws ec2 describe-vpc-peering-connections --filters "Name=requester-vpc-info.vpc-id,Values=$vpc" --query 'length(VpcPeeringConnections)')
  echo "$vpc,$cidr,$subnets,$igw,$nat,$pcx"
done

# Find all resources in a specific subnet
echo "Finding all resources in subnet-abc123..."
echo "\nEC2 Instances:"
aws ec2 describe-instances --filters "Name=subnet-id,Values=subnet-abc123" --query 'Reservations[*].Instances[*].[InstanceId,InstanceType,State.Name]' --output table
echo "\nNetwork Interfaces:"
aws ec2 describe-network-interfaces --filters "Name=subnet-id,Values=subnet-abc123" --query 'NetworkInterfaces[*].[NetworkInterfaceId,Description,Status]' --output table
echo "\nNAT Gateways:"
aws ec2 describe-nat-gateways --filter "Name=subnet-id,Values=subnet-abc123" --query 'NatGateways[*].[NatGatewayId,State]' --output table

# Cost analysis - List expensive resources
echo "Network resources cost analysis:"
echo "\nNAT Gateways (\$0.045/hour + data):"
aws ec2 describe-nat-gateways --filter "Name=state,Values=available" --query 'NatGateways[*].[NatGatewayId,SubnetId,CreateTime]' --output table
echo "\nTransit Gateways (\$0.05/attachment/hour + data):"
aws ec2 describe-transit-gateways --query 'TransitGateways[*].[TransitGatewayId,State,CreationTime]' --output table
echo "\nVPC Endpoints (varies by type):"
aws ec2 describe-vpc-endpoints --query 'VpcEndpoints[*].[VpcEndpointId,ServiceName,VpcEndpointType,State]' --output table
```

---

## Monitoring and Troubleshooting

### CloudWatch Metrics

#### VPC Metrics
- **PacketDropCount**: Packets dropped by security groups
- **NetworkIn/Out**: Network traffic for instances
- **NetworkPacketsIn/Out**: Packet count for instances

#### Load Balancer Metrics
- **RequestCount**: Number of requests
- **TargetResponseTime**: Response time from targets
- **HTTPCode_Target_2XX_Count**: Successful responses
- **UnHealthyHostCount**: Unhealthy targets

#### NAT Gateway Metrics
- **BytesInFromDestination**: Data from internet
- **BytesOutToDestination**: Data to internet
- **PacketsDropCount**: Packets dropped

### VPC Flow Logs Analysis

#### Common Analysis Patterns
```
# Top talkers (source IPs)
SELECT srcaddr, COUNT(*) as request_count 
FROM vpc_flow_logs 
GROUP BY srcaddr 
ORDER BY request_count DESC 
LIMIT 10;

# Rejected connections
SELECT srcaddr, dstaddr, srcport, dstport 
FROM vpc_flow_logs 
WHERE action = 'REJECT';

# Top destination ports
SELECT dstport, COUNT(*) as request_count 
FROM vpc_flow_logs 
GROUP BY dstport 
ORDER BY request_count DESC;
```

### Network Troubleshooting Tools

#### AWS Systems Manager Session Manager
- **Secure Access**: Connect to instances without SSH/RDP
- **No Bastion Host**: Direct connection through Systems Manager
- **Auditing**: Session activity logging

#### VPC Reachability Analyzer
- **Path Analysis**: Analyze network paths between resources
- **Configuration Issues**: Identify misconfigurations
- **Network Verification**: Verify connectivity before deployment

#### AWS X-Ray
- **Request Tracing**: Trace requests through distributed applications
- **Performance Analysis**: Identify performance bottlenecks
- **Service Map**: Visualize service dependencies

### Common Network Issues

#### Connectivity Issues
1. **Security Groups**: Check inbound/outbound rules
2. **NACLs**: Verify subnet-level rules
3. **Route Tables**: Check routing configuration
4. **DNS Resolution**: Verify DNS settings

#### Performance Issues
1. **Instance Type**: Right-size for network performance
2. **Placement Groups**: Use for high-bandwidth applications
3. **Enhanced Networking**: Enable SR-IOV and DPDK
4. **Load Balancer**: Check target group health

#### Security Issues
1. **Overly Permissive**: Security groups allowing 0.0.0.0/0
2. **Missing Encryption**: Unencrypted data in transit
3. **Exposed Resources**: Public instances in private subnets
4. **Weak Authentication**: Weak VPN pre-shared keys

### Troubleshooting Checklist

#### Instance Connectivity
- [ ] Security group allows required ports
- [ ] NACL allows required traffic
- [ ] Route table has correct routes
- [ ] Instance has correct IP configuration
- [ ] DNS resolution is working

#### Load Balancer Issues
- [ ] Target group health checks are passing
- [ ] Security groups allow load balancer traffic
- [ ] Listener configuration is correct
- [ ] SSL certificate is valid (HTTPS)

#### VPN Connectivity
- [ ] Customer gateway configuration is correct
- [ ] Both VPN tunnels are established
- [ ] Route propagation is enabled
- [ ] On-premises firewall allows IPSec traffic

### Performance Optimization

#### Network Performance
- **Enhanced Networking**: Enable for high-bandwidth applications
- **Placement Groups**: Cluster placement for low latency
- **Instance Types**: Choose network-optimized instances
- **Multi-Path**: Use multiple network paths for redundancy

#### Application Performance
- **Connection Pooling**: Reuse database connections
- **Caching**: Use ElastiCache for frequently accessed data
- **CDN**: Use CloudFront for global content delivery
- **Compression**: Enable compression for web content

## Summary

### Key AWS Networking Services

| Service | Use Case | Key Features |
|---------|----------|--------------|
| VPC | Private cloud network | Isolated, customizable networking |
| Security Groups | Instance-level firewall | Stateful, allow rules only |
| NACLs | Subnet-level firewall | Stateless, allow and deny rules |
| VPC Endpoints | Private AWS service access | Interface and Gateway endpoints |
| Transit Gateway | Central connectivity hub | Transitive routing, scalable |
| Direct Connect | Dedicated network connection | Consistent performance, private |
| Site-to-Site VPN | Encrypted connection to on-premises | IPSec tunnels, flexible |
| ELB | Load balancing | ALB (Layer 7), NLB (Layer 4) |
| CloudFront | Content delivery network | Global edge locations, caching |
| Route 53 | DNS service | Multiple routing policies |
| Global Accelerator | Network performance optimization | Static IPs, AWS global network |

### Exam Tips

#### Remember These Key Points
1. **Security Groups are stateful**, NACLs are stateless
2. **VPC Peering is not transitive**
3. **Transit Gateway enables transitive routing**
4. **NAT Gateway is managed**, NAT Instance is not
5. **Direct Connect provides consistent performance**
6. **Route 53 Alias records are free** for AWS resources
7. **CloudFront caches content**, Global Accelerator optimizes network
8. **VPC Endpoints keep traffic within AWS network**

#### Common Scenarios
- **High Availability**: Multi-AZ deployments with redundant connections
- **Security**: Defense in depth with multiple security layers
- **Performance**: Right instance types, enhanced networking, placement groups
- **Cost Optimization**: Reserved capacity, data transfer optimization
- **Compliance**: VPC Flow Logs, encryption in transit

#### Best Practices
- **Network Segmentation**: Separate tiers with subnets and security groups
- **Least Privilege**: Minimum required network access
- **Monitoring**: Comprehensive logging and monitoring
- **Documentation**: Clear naming and tagging conventions
- **Automation**: Infrastructure as Code for consistency

This comprehensive guide covers all the essential AWS networking concepts for the SAA-C03 certification exam. Focus on understanding the use cases, differences between services, and best practices for each networking component.