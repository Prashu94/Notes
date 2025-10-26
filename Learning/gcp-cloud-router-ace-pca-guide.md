# Google Cloud Router - Comprehensive Guide for ACE and PCA Certifications

## Table of Contents
1. [Overview and Core Concepts](#overview-and-core-concepts)
2. [Architecture and Components](#architecture-and-components)
3. [Router Configuration and Setup](#router-configuration-and-setup)
4. [BGP and Dynamic Routing](#bgp-and-dynamic-routing)
5. [Hybrid Connectivity Integration](#hybrid-connectivity-integration)
6. [Cloud NAT Integration](#cloud-nat-integration)
7. [Security and Access Control](#security-and-access-control)
8. [Monitoring and Troubleshooting](#monitoring-and-troubleshooting)
9. [Best Practices and Design Patterns](#best-practices-and-design-patterns)
10. [Cost Optimization](#cost-optimization)
11. [Exam-Focused Scenarios](#exam-focused-scenarios)
12. [Hands-On Labs and Examples](#hands-on-labs-and-examples)

---

## Overview and Core Concepts

### What is Google Cloud Router?

Google Cloud Router is a fully managed service that uses the Border Gateway Protocol (BGP) to advertise IP prefixes and exchange routing information between your Virtual Private Cloud (VPC) networks and on-premises networks. It enables dynamic routing for hybrid cloud connectivity.

### Key Features

- **Dynamic Route Advertisement**: Automatically advertises subnet routes to on-premises networks
- **Custom Route Advertisement**: Advertise custom IP ranges beyond your VPC subnets
- **BGP Session Management**: Establishes and maintains BGP peering sessions
- **Multi-path Routing**: Supports ECMP (Equal Cost Multi-Path) routing
- **Regional Resource**: Operates within a specific Google Cloud region
- **High Availability**: Built-in redundancy for reliable connectivity

### Use Cases

1. **Hybrid Cloud Connectivity**: Connect on-premises networks to GCP
2. **Multi-cloud Integration**: Route traffic between different cloud providers
3. **Site-to-Site VPN**: Dynamic routing for VPN connections
4. **Dedicated Interconnect**: BGP routing for private dedicated connections
5. **Partner Interconnect**: Routing through service provider connections
6. **Cloud NAT**: Provide outbound internet access for private instances

---

## Architecture and Components

### Cloud Router Architecture

```
┌─────────────────────┐    ┌─────────────────────┐
│   On-Premises       │    │   Google Cloud      │
│   Network           │    │   VPC Network       │
│                     │    │                     │
│  ┌──────────────┐   │    │  ┌──────────────┐   │
│  │  BGP Router  │◄──┼────┼──►│ Cloud Router │   │
│  │              │   │    │  │              │   │
│  └──────────────┘   │    │  └──────────────┘   │
│                     │    │         │           │
└─────────────────────┘    │         ▼           │
                           │  ┌──────────────┐   │
                           │  │   Subnets    │   │
                           │  │              │   │
                           │  └──────────────┘   │
                           └─────────────────────┘
```

### Core Components

#### 1. **Cloud Router Instance**
- Regional resource tied to a specific VPC network
- Manages BGP sessions and route advertisements
- Maintains routing tables and policies

#### 2. **BGP Sessions**
- Established between Cloud Router and peer routers
- Exchange routing information bidirectionally
- Support for MD5 authentication

#### 3. **Route Advertisements**
- **Default Mode**: Advertises all subnet routes in the region
- **Custom Mode**: Advertises only specified custom IP ranges
- **Selective Advertisement**: Fine-grained control over advertised routes

#### 4. **Interface Types**
- **VPN Tunnel Interface**: For Cloud VPN connections
- **VLAN Attachment Interface**: For Cloud Interconnect connections

### Integration Points

```
Cloud Router Integration Architecture

┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Cloud VPN     │────►│  Cloud Router   │◄────│ Cloud Interconnect │
└─────────────────┘     │                 │     └─────────────────┘
                        │                 │
┌─────────────────┐     │                 │     ┌─────────────────┐
│   Cloud NAT     │◄────│                 │────►│ VPC Networks    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

---

## Router Configuration and Setup

### Creating a Cloud Router

#### Using gcloud CLI

```bash
# Create a basic Cloud Router
gcloud compute routers create my-router \
    --network=my-vpc \
    --region=us-central1 \
    --description="Router for hybrid connectivity"

# Create router with specific ASN
gcloud compute routers create my-router \
    --network=my-vpc \
    --region=us-central1 \
    --asn=64512 \
    --advertisement-mode=custom
```

#### Using Terraform

```hcl
resource "google_compute_router" "main" {
  name    = "my-router"
  region  = "us-central1"
  network = google_compute_network.vpc.id

  bgp {
    asn            = 64512
    advertise_mode = "CUSTOM"
    
    advertised_groups = [
      "ALL_SUBNETS"
    ]
    
    advertised_ip_ranges {
      range = "192.168.100.0/24"
      description = "Custom range for on-premises"
    }
  }
}
```

### Router Configuration Parameters

#### 1. **Basic Configuration**
- **Name**: Unique identifier for the router
- **Network**: Target VPC network
- **Region**: Geographic region for the router
- **Description**: Optional documentation

#### 2. **BGP Configuration**
- **ASN (Autonomous System Number)**: 16-bit or 32-bit ASN
  - Private ASN ranges: 64512-65534, 4200000000-4294967294
  - Must be unique within your network topology
- **Advertisement Mode**: DEFAULT or CUSTOM
- **Keepalive Interval**: BGP keepalive timer (default: 20 seconds)
- **Hold Time**: BGP hold timer (default: 60 seconds)

#### 3. **Route Advertisement Settings**

```bash
# Configure custom advertisement
gcloud compute routers update my-router \
    --region=us-central1 \
    --advertisement-mode=custom \
    --set-advertisement-groups=ALL_SUBNETS \
    --add-advertisement-ranges=192.168.100.0/24
```

### Interface Configuration

#### VPN Tunnel Interface

```bash
# Add VPN tunnel interface
gcloud compute routers add-interface my-router \
    --interface-name=vpn-interface-1 \
    --vpn-tunnel=my-vpn-tunnel \
    --ip-address=169.254.1.1 \
    --mask-length=30 \
    --region=us-central1
```

#### VLAN Attachment Interface

```bash
# Add Interconnect VLAN interface
gcloud compute routers add-interface my-router \
    --interface-name=interconnect-interface-1 \
    --interconnect-attachment=my-vlan-attachment \
    --ip-address=169.254.2.1 \
    --mask-length=30 \
    --region=us-central1
```

---

## BGP and Dynamic Routing

### BGP Fundamentals in Cloud Router

#### BGP Session Establishment

```
BGP Session Lifecycle

1. Idle State
   ↓
2. Connect State
   ↓
3. Active State
   ↓
4. OpenSent State
   ↓
5. OpenConfirm State
   ↓
6. Established State (Route Exchange)
```

#### BGP Peer Configuration

```bash
# Add BGP peer for VPN tunnel
gcloud compute routers add-bgp-peer my-router \
    --peer-name=on-premises-peer \
    --interface=vpn-interface-1 \
    --peer-ip-address=169.254.1.2 \
    --peer-asn=65001 \
    --region=us-central1 \
    --md5-authentication-key="shared-secret"
```

### Route Advertisement Strategies

#### 1. **Default Advertisement Mode**
- Automatically advertises all subnet routes in the router's region
- Simplest configuration for basic connectivity
- Limited control over advertised routes

```bash
# Set default advertisement mode
gcloud compute routers update my-router \
    --region=us-central1 \
    --advertisement-mode=default
```

#### 2. **Custom Advertisement Mode**
- Granular control over advertised routes
- Can advertise specific IP ranges
- Supports route filtering and manipulation

```bash
# Configure custom advertisements
gcloud compute routers update my-router \
    --region=us-central1 \
    --advertisement-mode=custom \
    --set-advertisement-groups=ALL_SUBNETS \
    --add-advertisement-ranges=10.1.0.0/16,10.2.0.0/16
```

#### 3. **Advertisement Groups**
- **ALL_SUBNETS**: All subnet routes in the VPC
- **ALL_VPC_SUBNETS**: All subnets across all regions in VPC
- **ALL_PEER_VPC_SUBNETS**: Subnets from peered VPCs

### Route Priority and Selection

#### MED (Multi-Exit Discriminator)
```bash
# Set route priority using MED
gcloud compute routers update-bgp-peer my-router \
    --peer-name=on-premises-peer \
    --region=us-central1 \
    --advertised-route-priority=100
```

#### Route Maps and Filters
```bash
# Create route policy for filtering
gcloud compute route-policies create my-policy \
    --type=ROUTE_POLICY_TYPE_IMPORT \
    --next-hop-other-routes=DEFAULT_ROUTING \
    --terms="[{
        'priority': 100,
        'match': {
            'prefix-set': 'internal-prefixes'
        },
        'actions': {
            'route-action': 'ACCEPT'
        }
    }]"
```

### ECMP (Equal Cost Multi-Path) Routing

#### Configuration for Load Balancing
```bash
# Configure multiple BGP peers for ECMP
gcloud compute routers add-bgp-peer my-router \
    --peer-name=peer-1 \
    --interface=interface-1 \
    --peer-ip-address=169.254.1.2 \
    --peer-asn=65001 \
    --region=us-central1

gcloud compute routers add-bgp-peer my-router \
    --peer-name=peer-2 \
    --interface=interface-2 \
    --peer-ip-address=169.254.2.2 \
    --peer-asn=65001 \
    --region=us-central1
```

---

## Hybrid Connectivity Integration

### Cloud VPN Integration

#### HA VPN with Cloud Router

```hcl
# Terraform configuration for HA VPN with Cloud Router
resource "google_compute_ha_vpn_gateway" "ha_gateway" {
  name   = "ha-vpn-gateway"
  region = "us-central1"
  
  vpn_interfaces {
    id                  = 0
    interconnect_attachment = null
  }
  
  vpn_interfaces {
    id                  = 1
    interconnect_attachment = null
  }
}

resource "google_compute_vpn_tunnel" "tunnel1" {
  name               = "ha-vpn-tunnel-1"
  region             = "us-central1"
  vpn_gateway        = google_compute_ha_vpn_gateway.ha_gateway.id
  vpn_gateway_interface = 0
  peer_external_gateway = google_compute_external_vpn_gateway.peer_gateway.id
  peer_external_gateway_interface = 0
  router             = google_compute_router.main.name
  ike_version        = 2
  shared_secret      = var.shared_secret_1
}

resource "google_compute_router_interface" "interface1" {
  name       = "interface-1"
  router     = google_compute_router.main.name
  region     = "us-central1"
  ip_range   = "169.254.1.1/30"
  vpn_tunnel = google_compute_vpn_tunnel.tunnel1.name
}

resource "google_compute_router_peer" "peer1" {
  name            = "peer-1"
  router          = google_compute_router.main.name
  region          = "us-central1"
  peer_ip_address = "169.254.1.2"
  peer_asn        = 65001
  interface       = google_compute_router_interface.interface1.name
}
```

#### Classic VPN Configuration
```bash
# Create Classic VPN tunnel with static routing fallback
gcloud compute vpn-tunnels create vpn-tunnel-1 \
    --peer-address=203.0.113.12 \
    --shared-secret="shared-secret" \
    --target-vpn-gateway=vpn-gateway-1 \
    --region=us-central1 \
    --ike-version=2

# Add BGP configuration to existing tunnel
gcloud compute routers add-interface my-router \
    --interface-name=vpn-interface \
    --vpn-tunnel=vpn-tunnel-1 \
    --ip-address=169.254.1.1 \
    --mask-length=30 \
    --region=us-central1
```

### Cloud Interconnect Integration

#### Dedicated Interconnect with BGP

```bash
# Create VLAN attachment for Dedicated Interconnect
gcloud compute interconnects attachments dedicated create my-attachment \
    --interconnect=my-interconnect \
    --router=my-router \
    --region=us-central1 \
    --vlan=100

# Configure BGP for the attachment
gcloud compute routers add-interface my-router \
    --interface-name=interconnect-interface \
    --interconnect-attachment=my-attachment \
    --ip-address=169.254.100.1 \
    --mask-length=30 \
    --region=us-central1

gcloud compute routers add-bgp-peer my-router \
    --peer-name=interconnect-peer \
    --interface=interconnect-interface \
    --peer-ip-address=169.254.100.2 \
    --peer-asn=65002 \
    --region=us-central1
```

#### Partner Interconnect Configuration

```bash
# Create Partner Interconnect VLAN attachment
gcloud compute interconnects attachments partner create partner-attachment \
    --router=my-router \
    --region=us-central1 \
    --edge-availability-domain=AVAILABILITY_DOMAIN_1 \
    --bandwidth=BPS_1G

# Configure BGP session
gcloud compute routers add-interface my-router \
    --interface-name=partner-interface \
    --interconnect-attachment=partner-attachment \
    --region=us-central1

gcloud compute routers add-bgp-peer my-router \
    --peer-name=partner-peer \
    --interface=partner-interface \
    --peer-ip-address=169.254.200.2 \
    --peer-asn=65003 \
    --region=us-central1
```

### Multi-Region Connectivity

#### Hub-and-Spoke Architecture

```yaml
# Architecture Design
Hub Region (us-central1):
  - Primary Cloud Router
  - VPN/Interconnect connections
  - Route aggregation

Spoke Regions:
  - Regional Cloud Routers
  - VPC peering connections
  - Local subnet advertisements
```

```bash
# Configure hub router with global route advertisement
gcloud compute routers create hub-router \
    --network=hub-vpc \
    --region=us-central1 \
    --asn=64512 \
    --advertisement-mode=custom \
    --set-advertisement-groups=ALL_VPC_SUBNETS

# Configure spoke router
gcloud compute routers create spoke-router \
    --network=spoke-vpc \
    --region=us-east1 \
    --asn=64513 \
    --advertisement-mode=custom \
    --set-advertisement-groups=ALL_SUBNETS
```

---

## Cloud NAT Integration

### Cloud NAT with Cloud Router

#### Basic NAT Configuration

```hcl
resource "google_compute_router_nat" "main" {
  name   = "main-nat"
  router = google_compute_router.main.name
  region = google_compute_router.main.region

  nat_ip_allocate_option = "MANUAL_ONLY"
  nat_ips                = [google_compute_address.nat_ip.self_link]

  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}

resource "google_compute_address" "nat_ip" {
  name   = "nat-ip"
  region = "us-central1"
}
```

#### Advanced NAT Configuration

```bash
# Create NAT with custom subnet selection
gcloud compute routers nats create advanced-nat \
    --router=my-router \
    --region=us-central1 \
    --nat-custom-subnet-ip-ranges=subnet-1:ALL_IP_RANGES,subnet-2:PRIMARY_IP_RANGE \
    --nat-external-ip-pool=nat-ip-1,nat-ip-2 \
    --enable-logging \
    --log-filter=ALL
```

#### NAT Rules and Port Management

```bash
# Configure NAT rules for specific source ranges
gcloud compute routers nats rules create rule-1 \
    --router=my-router \
    --nat=advanced-nat \
    --region=us-central1 \
    --source-nat-active-ranges=10.1.0.0/24 \
    --source-nat-drain-ranges=10.2.0.0/24
```

### NAT Monitoring and Logging

#### Cloud Logging Configuration
```json
{
  "insertId": "example-insert-id",
  "jsonPayload": {
    "connection": {
      "dest_ip": "8.8.8.8",
      "dest_port": 53,
      "protocol": 17,
      "src_ip": "10.1.0.5",
      "src_port": 35662
    },
    "endpoint": {
      "project_id": "my-project",
      "region": "us-central1",
      "vm_name": "instance-1",
      "zone": "us-central1-a"
    },
    "allocation_status": "OK",
    "nat_gateway_name": "advanced-nat",
    "router_name": "my-router"
  },
  "logName": "projects/my-project/logs/compute.googleapis.com%2Fnat_flows",
  "severity": "INFO",
  "timestamp": "2024-01-01T10:00:00Z"
}
```

---

## Security and Access Control

### IAM Roles and Permissions

#### Required IAM Roles

```bash
# Grant Compute Network Admin role
gcloud projects add-iam-policy-binding PROJECT_ID \
    --member="user:admin@example.com" \
    --role="roles/compute.networkAdmin"

# Grant Compute Security Admin role
gcloud projects add-iam-policy-binding PROJECT_ID \
    --member="serviceAccount:router-sa@PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/compute.securityAdmin"
```

#### Custom IAM Role for Cloud Router Management

```json
{
  "title": "Cloud Router Operator",
  "description": "Custom role for Cloud Router operations",
  "stage": "GA",
  "includedPermissions": [
    "compute.routers.create",
    "compute.routers.delete",
    "compute.routers.get",
    "compute.routers.list",
    "compute.routers.update",
    "compute.routers.use",
    "compute.networks.get",
    "compute.subnetworks.get",
    "compute.addresses.get",
    "compute.vpnTunnels.get",
    "compute.interconnectAttachments.get"
  ]
}
```

### BGP Security Best Practices

#### MD5 Authentication
```bash
# Configure BGP peer with MD5 authentication
gcloud compute routers add-bgp-peer my-router \
    --peer-name=secure-peer \
    --interface=vpn-interface \
    --peer-ip-address=169.254.1.2 \
    --peer-asn=65001 \
    --region=us-central1 \
    --md5-authentication-key="$(cat /path/to/secret-key)"
```

#### Route Filtering and Policies
```bash
# Implement route filtering
gcloud compute routers update-bgp-peer my-router \
    --peer-name=secure-peer \
    --region=us-central1 \
    --advertisement-mode=custom \
    --set-advertisement-ranges=10.0.0.0/16
```

### Network Security Integration

#### Firewall Rules for BGP Traffic
```bash
# Allow BGP traffic (TCP 179)
gcloud compute firewall-rules create allow-bgp \
    --network=my-vpc \
    --allow=tcp:179 \
    --source-ranges=169.254.0.0/16 \
    --description="Allow BGP traffic for Cloud Router"

# Allow IPSec traffic for VPN
gcloud compute firewall-rules create allow-ipsec \
    --network=my-vpc \
    --allow=esp,ah,udp:500,udp:4500 \
    --source-ranges=203.0.113.0/24 \
    --description="Allow IPSec traffic for VPN"
```

---

## Monitoring and Troubleshooting

### Cloud Monitoring Metrics

#### Key Metrics to Monitor

```bash
# BGP session state metrics
- router/bgp_session_up: BGP session status
- router/bgp_sessions_up: Number of active BGP sessions
- router/best_received_routes_count: Number of best routes received
- router/sent_routes_count: Number of routes sent to peers

# NAT metrics
- nat/allocated_ports: Number of allocated NAT ports
- nat/port_usage: NAT port utilization
- nat/sent_packets_count: Packets sent through NAT
- nat/received_packets_count: Packets received through NAT
```

#### Cloud Monitoring Query Examples

```sql
-- Monitor BGP session health
fetch gce_router
| filter resource.router_id == "my-router"
| metric 'compute.googleapis.com/router/bgp_session_up'
| group_by 1m, [mean]

-- Monitor NAT port utilization
fetch gce_nat
| filter resource.nat_gateway_name == "main-nat"
| metric 'compute.googleapis.com/nat/port_usage'
| group_by 1m, [max]
```

### Logging and Diagnostics

#### Enable Comprehensive Logging
```bash
# Enable VPC Flow Logs
gcloud compute networks subnets update my-subnet \
    --region=us-central1 \
    --enable-flow-logs \
    --logging-aggregation-interval=INTERVAL_5_SEC \
    --logging-flow-sampling=1.0 \
    --logging-metadata=INCLUDE_ALL_METADATA

# Enable Cloud NAT Logging
gcloud compute routers nats update main-nat \
    --router=my-router \
    --region=us-central1 \
    --enable-logging \
    --log-filter=ALL
```

#### BGP Session Diagnostics
```bash
# Check BGP session status
gcloud compute routers get-status my-router \
    --region=us-central1 \
    --format="table(
        result.bgpPeerStatus[].name:label='PEER_NAME',
        result.bgpPeerStatus[].state:label='STATE',
        result.bgpPeerStatus[].uptime:label='UPTIME',
        result.bgpPeerStatus[].numLearnedRoutes:label='LEARNED_ROUTES'
    )"

# Get detailed BGP session information
gcloud compute routers get-status my-router \
    --region=us-central1 \
    --format="json" | jq '.result.bgpPeerStatus[0]'
```

### Troubleshooting Common Issues

#### 1. BGP Session Not Establishing

**Symptoms:**
- BGP session state shows "Idle" or "Active"
- Routes not being exchanged

**Troubleshooting Steps:**
```bash
# Check router configuration
gcloud compute routers describe my-router --region=us-central1

# Verify interface IP addresses
gcloud compute routers get-status my-router --region=us-central1

# Check firewall rules
gcloud compute firewall-rules list --filter="network:(my-vpc)"

# Verify VPN tunnel or Interconnect status
gcloud compute vpn-tunnels describe my-tunnel --region=us-central1
```

**Common Solutions:**
- Verify peer ASN and IP addresses
- Check MD5 authentication key if configured
- Ensure firewall rules allow BGP traffic (TCP 179)
- Verify underlying connectivity (VPN/Interconnect)

#### 2. Route Advertisement Issues

**Symptoms:**
- Routes not appearing on-premises
- Incorrect routes being advertised

**Troubleshooting:**
```bash
# Check advertised routes
gcloud compute routers get-status my-router \
    --region=us-central1 \
    --format="table(result.bgpPeerStatus[].advertisedRoutes[].destPrefix)"

# Verify advertisement mode
gcloud compute routers describe my-router \
    --region=us-central1 \
    --format="value(bgp.advertiseMode)"
```

#### 3. NAT Connectivity Problems

**Symptoms:**
- Outbound connections failing
- NAT port exhaustion

**Troubleshooting:**
```bash
# Check NAT status
gcloud compute routers nats describe main-nat \
    --router=my-router \
    --region=us-central1

# Monitor NAT metrics
gcloud logging read 'resource.type="nat_gateway"' \
    --limit=10 \
    --format=json
```

---

## Best Practices and Design Patterns

### High Availability Design

#### Multi-Path Redundancy
```yaml
Design Pattern: Redundant Connectivity
┌─────────────────────┐
│   On-Premises       │
│                     │
│  ┌─────┐   ┌─────┐  │
│  │ RTR1│   │ RTR2│  │
│  └──┬──┘   └──┬──┘  │
└─────┼─────────┼─────┘
      │         │
   ┌──▼──┐   ┌──▼──┐
   │VPN-1│   │VPN-2│
   └──┬──┘   └──┬──┘
      │         │
   ┌──▼─────────▼──┐
   │ Cloud Router  │
   │   (Primary)   │
   └───────────────┘
```

#### Multi-Region Deployment
```bash
# Primary region router
gcloud compute routers create primary-router \
    --network=global-vpc \
    --region=us-central1 \
    --asn=64512

# Secondary region router  
gcloud compute routers create secondary-router \
    --network=global-vpc \
    --region=us-east1 \
    --asn=64513

# Configure route priorities for failover
gcloud compute routers update-bgp-peer primary-router \
    --peer-name=primary-peer \
    --region=us-central1 \
    --advertised-route-priority=100

gcloud compute routers update-bgp-peer secondary-router \
    --peer-name=secondary-peer \
    --region=us-east1 \
    --advertised-route-priority=200
```

### Performance Optimization

#### ECMP Load Balancing Configuration
```bash
# Configure multiple equal-cost paths
for i in {1..4}; do
  gcloud compute routers add-bgp-peer my-router \
    --peer-name=peer-$i \
    --interface=interface-$i \
    --peer-ip-address=169.254.$i.2 \
    --peer-asn=65001 \
    --region=us-central1 \
    --advertised-route-priority=100
done
```

#### Route Aggregation
```bash
# Advertise summary routes instead of individual subnets
gcloud compute routers update my-router \
    --region=us-central1 \
    --advertisement-mode=custom \
    --add-advertisement-ranges=10.0.0.0/8:summary-route
```

### Security Hardening

#### Principle of Least Privilege
```bash
# Advertise only necessary routes
gcloud compute routers update my-router \
    --region=us-central1 \
    --advertisement-mode=custom \
    --set-advertisement-ranges=10.1.0.0/24,10.2.0.0/24

# Use route filtering on BGP peers
gcloud compute routers update-bgp-peer my-router \
    --peer-name=external-peer \
    --region=us-central1 \
    --advertisement-mode=custom \
    --set-advertisement-ranges=10.1.0.0/16
```

#### Authentication and Encryption
```bash
# Always use MD5 authentication for BGP
gcloud compute routers add-bgp-peer my-router \
    --peer-name=authenticated-peer \
    --interface=vpn-interface \
    --peer-ip-address=169.254.1.2 \
    --peer-asn=65001 \
    --region=us-central1 \
    --md5-authentication-key-file=/path/to/key

# Use strong IPSec parameters for VPN tunnels
gcloud compute vpn-tunnels create secure-tunnel \
    --peer-address=203.0.113.12 \
    --shared-secret-file=/path/to/strong-secret \
    --ike-version=2 \
    --target-vpn-gateway=vpn-gateway \
    --region=us-central1
```

### Scalability Patterns

#### Hub-and-Spoke with Regional Hubs
```yaml
Global Architecture:
├── Americas Hub (us-central1)
│   ├── Cloud Router (ASN: 64512)
│   ├── Regional VPN Gateways
│   └── Spoke VPCs
├── EMEA Hub (europe-west1)
│   ├── Cloud Router (ASN: 64513)
│   ├── Regional VPN Gateways
│   └── Spoke VPCs
└── APAC Hub (asia-southeast1)
    ├── Cloud Router (ASN: 64514)
    ├── Regional VPN Gateways
    └── Spoke VPCs
```

---

## Cost Optimization

### Cost Components

#### 1. **Cloud Router Charges**
- No charge for the Cloud Router itself
- Charges for data processing through the router
- BGP session maintenance (minimal cost)

#### 2. **Data Transfer Costs**
- Ingress traffic: Generally free
- Egress traffic: Charged based on destination
- Cross-region traffic: Higher rates

#### 3. **Associated Resource Costs**
- VPN Gateway charges
- Interconnect attachment fees
- NAT Gateway processing fees
- External IP address reservations

### Cost Optimization Strategies

#### 1. **Route Optimization**
```bash
# Use route summarization to reduce routing table size
gcloud compute routers update my-router \
    --region=us-central1 \
    --advertisement-mode=custom \
    --set-advertisement-ranges=10.0.0.0/8  # Summary instead of /24s
```

#### 2. **Regional Optimization**
```bash
# Place routers in regions close to resources
gcloud compute routers create optimized-router \
    --network=my-vpc \
    --region=us-central1  # Same region as compute resources
```

#### 3. **NAT Optimization**
```bash
# Use selective NAT for cost control
gcloud compute routers nats create selective-nat \
    --router=my-router \
    --region=us-central1 \
    --nat-custom-subnet-ip-ranges=private-subnet:ALL_IP_RANGES \
    --auto-allocate-nat-external-ips
```

### Cost Monitoring

#### Budget Alerts for Network Costs
```json
{
  "displayName": "Network Egress Budget",
  "budgetFilter": {
    "services": ["services/95FF2355-6827-4240-A88C-3E3B220C90F0"],
    "subAccounts": []
  },
  "amount": {
    "specifiedAmount": {
      "currencyCode": "USD",
      "units": "100"
    }
  },
  "thresholdRules": [
    {
      "thresholdPercent": 0.8,
      "spendBasis": "CURRENT_SPEND"
    }
  ]
}
```

---

## Exam-Focused Scenarios

### ACE Certification Scenarios

#### Scenario 1: Basic Hybrid Connectivity
**Question:** Your company needs to connect their on-premises network to GCP using VPN with dynamic routing. What components are required?

**Answer:**
1. Create VPC network and subnets
2. Set up Cloud VPN Gateway (HA VPN recommended)
3. Configure Cloud Router for BGP
4. Establish VPN tunnels
5. Configure BGP sessions between Cloud Router and on-premises router

```bash
# Complete setup commands
gcloud compute networks create hybrid-vpc --subnet-mode=regional
gcloud compute routers create hybrid-router --network=hybrid-vpc --region=us-central1 --asn=64512
gcloud compute ha-vpn-gateways create ha-vpn --network=hybrid-vpc --region=us-central1
# ... additional VPN and BGP configuration
```

#### Scenario 2: NAT Configuration for Private Instances
**Question:** Private VM instances need internet access for software updates. Configure Cloud NAT.

**Answer:**
```bash
# Create NAT with Cloud Router
gcloud compute addresses create nat-ip --region=us-central1
gcloud compute routers nats create internet-nat \
    --router=hybrid-router \
    --region=us-central1 \
    --nat-external-ip-pool=nat-ip \
    --nat-all-subnet-ip-ranges
```

### PCA Certification Scenarios

#### Scenario 1: Multi-Region High Availability
**Question:** Design a highly available hybrid connectivity solution spanning multiple GCP regions with automatic failover.

**Solution Architecture:**
```yaml
Primary Region (us-central1):
  - Primary Cloud Router (ASN: 64512)
  - HA VPN Gateway with dual tunnels
  - BGP priority: 100 (preferred)

Secondary Region (us-east1):
  - Secondary Cloud Router (ASN: 64513)  
  - HA VPN Gateway with dual tunnels
  - BGP priority: 200 (backup)

Route Advertisement:
  - Primary: ALL_VPC_SUBNETS with MED 100
  - Secondary: ALL_VPC_SUBNETS with MED 200
```

#### Scenario 2: Complex Route Policy Design
**Question:** Implement route filtering to advertise only production subnets to partners while advertising all subnets to corporate headquarters.

**Solution:**
```bash
# Corporate connection - advertise all subnets
gcloud compute routers add-bgp-peer corporate-router \
    --peer-name=hq-peer \
    --interface=hq-interface \
    --peer-asn=65000 \
    --advertisement-mode=custom \
    --set-advertisement-groups=ALL_VPC_SUBNETS

# Partner connection - advertise only production subnets
gcloud compute routers add-bgp-peer partner-router \
    --peer-name=partner-peer \
    --interface=partner-interface \
    --peer-asn=65100 \
    --advertisement-mode=custom \
    --set-advertisement-ranges=10.1.0.0/16,10.2.0.0/16
```

#### Scenario 3: Bandwidth and Performance Optimization
**Question:** Optimize network performance for a latency-sensitive application requiring 10Gbps throughput.

**Solution Design:**
```yaml
Implementation:
1. Dedicated Interconnect (10Gbps)
   - Direct physical connection
   - Lower latency than VPN
   
2. Multiple VLAN Attachments:
   - ECMP across 4 x 2.5Gbps attachments
   - Load balancing and redundancy
   
3. BGP Optimization:
   - Shorter AS paths
   - Optimized route advertisements
   - Connection-specific routing policies
```

---

## Hands-On Labs and Examples

### Lab 1: Basic Cloud Router Setup with VPN

#### Objective
Set up Cloud Router with HA VPN for hybrid connectivity.

#### Prerequisites
- GCP project with billing enabled
- On-premises router simulator or actual router
- Basic networking knowledge

#### Step-by-Step Implementation

```bash
# Step 1: Create VPC network
gcloud compute networks create lab-vpc \
    --subnet-mode=custom \
    --description="Lab VPC for Cloud Router"

# Step 2: Create subnet
gcloud compute networks subnets create lab-subnet \
    --network=lab-vpc \
    --range=10.1.0.0/24 \
    --region=us-central1

# Step 3: Create Cloud Router
gcloud compute routers create lab-router \
    --network=lab-vpc \
    --region=us-central1 \
    --asn=64512 \
    --advertisement-mode=default

# Step 4: Create HA VPN Gateway
gcloud compute ha-vpn-gateways create lab-ha-vpn \
    --network=lab-vpc \
    --region=us-central1

# Step 5: Create external VPN gateway (represents on-premises)
gcloud compute external-vpn-gateways create on-prem-gateway \
    --interfaces=0=203.0.113.12

# Step 6: Create VPN tunnels
gcloud compute vpn-tunnels create tunnel-1 \
    --peer-external-gateway=on-prem-gateway \
    --peer-external-gateway-interface=0 \
    --region=us-central1 \
    --ike-version=2 \
    --shared-secret="lab-shared-secret-1" \
    --router=lab-router \
    --vpn-gateway=lab-ha-vpn \
    --vpn-gateway-interface=0

gcloud compute vpn-tunnels create tunnel-2 \
    --peer-external-gateway=on-prem-gateway \
    --peer-external-gateway-interface=0 \
    --region=us-central1 \
    --ike-version=2 \
    --shared-secret="lab-shared-secret-2" \
    --router=lab-router \
    --vpn-gateway=lab-ha-vpn \
    --vpn-gateway-interface=1

# Step 7: Configure router interfaces
gcloud compute routers add-interface lab-router \
    --interface-name=tunnel-1-interface \
    --ip-range=169.254.1.1/30 \
    --vpn-tunnel=tunnel-1 \
    --region=us-central1

gcloud compute routers add-interface lab-router \
    --interface-name=tunnel-2-interface \
    --ip-range=169.254.2.1/30 \
    --vpn-tunnel=tunnel-2 \
    --region=us-central1

# Step 8: Add BGP peers
gcloud compute routers add-bgp-peer lab-router \
    --peer-name=on-prem-peer-1 \
    --interface=tunnel-1-interface \
    --peer-ip-address=169.254.1.2 \
    --peer-asn=65001 \
    --region=us-central1

gcloud compute routers add-bgp-peer lab-router \
    --peer-name=on-prem-peer-2 \
    --interface=tunnel-2-interface \
    --peer-ip-address=169.254.2.2 \
    --peer-asn=65001 \
    --region=us-central1
```

#### Verification Steps
```bash
# Check router status
gcloud compute routers get-status lab-router --region=us-central1

# Verify BGP sessions
gcloud compute routers get-status lab-router \
    --region=us-central1 \
    --format="table(result.bgpPeerStatus[].name,result.bgpPeerStatus[].state)"

# Check routes
gcloud compute routes list --filter="network:(lab-vpc)"
```

### Lab 2: Advanced Route Advertisement

#### Objective
Configure custom route advertisements for different peer types.

#### Implementation
```bash
# Create router with custom advertisement
gcloud compute routers create advanced-router \
    --network=lab-vpc \
    --region=us-central1 \
    --asn=64512 \
    --advertisement-mode=custom

# Add corporate peer (advertise all subnets)
gcloud compute routers add-bgp-peer advanced-router \
    --peer-name=corporate-peer \
    --interface=corporate-interface \
    --peer-ip-address=169.254.10.2 \
    --peer-asn=65000 \
    --region=us-central1

# Configure corporate peer advertisements
gcloud compute routers update-bgp-peer advanced-router \
    --peer-name=corporate-peer \
    --region=us-central1 \
    --advertisement-mode=custom \
    --set-advertisement-groups=ALL_VPC_SUBNETS

# Add partner peer (advertise only specific ranges)
gcloud compute routers add-bgp-peer advanced-router \
    --peer-name=partner-peer \
    --interface=partner-interface \
    --peer-ip-address=169.254.20.2 \
    --peer-asn=65100 \
    --region=us-central1

# Configure partner peer advertisements (production networks only)
gcloud compute routers update-bgp-peer advanced-router \
    --peer-name=partner-peer \
    --region=us-central1 \
    --advertisement-mode=custom \
    --set-advertisement-ranges=10.100.0.0/16,10.101.0.0/16
```

### Lab 3: Cloud NAT with Monitoring

#### Objective
Set up Cloud NAT with comprehensive monitoring and logging.

#### Implementation
```bash
# Create static IP for NAT
gcloud compute addresses create nat-external-ip \
    --region=us-central1

# Create NAT with logging
gcloud compute routers nats create production-nat \
    --router=lab-router \
    --region=us-central1 \
    --nat-external-ip-pool=nat-external-ip \
    --nat-all-subnet-ip-ranges \
    --enable-logging \
    --log-filter=ALL

# Create monitoring dashboard
cat << 'EOF' > nat-dashboard.json
{
  "displayName": "Cloud NAT Monitoring",
  "mosaicLayout": {
    "tiles": [
      {
        "width": 6,
        "height": 4,
        "widget": {
          "title": "NAT Port Utilization",
          "xyChart": {
            "dataSets": [{
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "metric.type=\"compute.googleapis.com/nat/port_usage\"",
                  "aggregation": {
                    "alignmentPeriod": "60s",
                    "perSeriesAligner": "ALIGN_MEAN"
                  }
                }
              }
            }]
          }
        }
      }
    ]
  }
}
EOF

gcloud monitoring dashboards create --config-from-file=nat-dashboard.json
```

### Lab 4: Interconnect with BGP

#### Objective
Configure Dedicated Interconnect with Cloud Router and BGP.

#### Implementation
```bash
# Note: This requires actual Interconnect setup
# Create VLAN attachment (assuming Interconnect exists)
gcloud compute interconnects attachments dedicated create prod-attachment \
    --interconnect=my-interconnect \
    --router=lab-router \
    --region=us-central1 \
    --vlan=100 \
    --description="Production Interconnect attachment"

# Add router interface for Interconnect
gcloud compute routers add-interface lab-router \
    --interface-name=interconnect-interface \
    --interconnect-attachment=prod-attachment \
    --ip-range=169.254.100.1/30 \
    --region=us-central1

# Configure BGP peer for Interconnect
gcloud compute routers add-bgp-peer lab-router \
    --peer-name=interconnect-peer \
    --interface=interconnect-interface \
    --peer-ip-address=169.254.100.2 \
    --peer-asn=65200 \
    --region=us-central1 \
    --advertised-route-priority=100
```

---

## Conclusion

Google Cloud Router is a critical component for hybrid and multi-cloud connectivity in Google Cloud Platform. This comprehensive guide covers all aspects needed for both ACE and PCA certifications:

### Key Takeaways for ACE Certification:
- Understand basic Cloud Router configuration with VPN
- Know how to set up Cloud NAT for private instance internet access
- Be familiar with BGP fundamentals and route advertisement
- Understand integration with Cloud VPN and basic Interconnect

### Key Takeaways for PCA Certification:
- Design complex multi-region, highly available network architectures
- Implement advanced route policies and filtering
- Optimize for performance, security, and cost
- Integrate with enterprise-grade connectivity solutions
- Troubleshoot complex networking scenarios

### Best Practices Summary:
1. **Always use HA VPN** for production workloads
2. **Implement redundancy** across multiple tunnels/attachments
3. **Use custom route advertisement** for security and control
4. **Monitor BGP sessions** and NAT utilization continuously
5. **Apply principle of least privilege** for route advertisements
6. **Optimize for cost** through regional placement and route summarization

This guide provides the foundation needed to successfully implement Cloud Router solutions and pass both Google Cloud certification exams. Regular hands-on practice with the provided labs will reinforce the theoretical knowledge and prepare you for real-world implementations.