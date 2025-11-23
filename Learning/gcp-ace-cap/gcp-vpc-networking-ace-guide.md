# Google Cloud VPC & Networking - Associate Cloud Engineer (ACE) Comprehensive Guide

## Table of Contents
1. [VPC Networks Overview](#vpc-networks-overview)
2. [Subnets & IP Addressing](#subnets--ip-addressing)
3. [Routes](#routes)
4. [Firewall Rules](#firewall-rules)
5. [Cloud VPN](#cloud-vpn)
6. [Cloud Interconnect](#cloud-interconnect)
7. [Shared VPC](#shared-vpc)
8. [VPC Peering](#vpc-peering)
9. [Common Networking Tasks](#common-networking-tasks)
10. [ACE Exam Tips](#ace-exam-tips)

---

## VPC Networks Overview

### What is VPC?

A Virtual Private Cloud (VPC) network is a virtualized network within Google Cloud. VPCs are **global resources** — they span all regions.

**Key Characteristics:**
- **Global scope:** VPC networks are not tied to any single region or zone
- **Subnets are regional:** While VPC is global, subnets exist in specific regions
- **Private networking:** Resources communicate using internal IP addresses
- **Scalable:** Support thousands of instances

### VPC Network Types

**1. Default Network:**
- Automatically created when you create a new project
- Auto mode VPC with one subnet per region
- Pre-configured firewall rules (allow SSH, RDP, ICMP, internal)
- Subnets use 10.128.0.0/9 CIDR range

```bash
# View default network
gcloud compute networks describe default
```

**2. Auto Mode VPC:**
- One subnet automatically created in each region
- Subnets use predefined IP ranges from 10.128.0.0/9
- New subnets added automatically as new regions launch
- Good for getting started, but limited for production

```bash
# Create auto mode VPC
gcloud compute networks create my-auto-network \
  --subnet-mode=auto
```

**3. Custom Mode VPC:**
- Full control over subnet creation and IP ranges
- You manually create subnets in chosen regions
- **Recommended for production**
- Can use any RFC 1918 private IP ranges

```bash
# Create custom mode VPC
gcloud compute networks create my-custom-network \
  --subnet-mode=custom
```

### View Networks

```bash
# List all VPC networks
gcloud compute networks list

# Describe specific network
gcloud compute networks describe NETWORK_NAME

# View subnets in a network
gcloud compute networks subnets list \
  --network=NETWORK_NAME
```

### Convert Auto to Custom Mode

```bash
# One-way conversion (cannot reverse!)
gcloud compute networks update my-auto-network \
  --switch-to-custom-subnet-mode
```

### Delete a VPC Network

```bash
# Must delete all resources first (instances, load balancers, etc.)
gcloud compute networks delete NETWORK_NAME
```

---

## Subnets & IP Addressing

### Understanding Subnets

**Subnets are regional resources** that define IP address ranges within a VPC network.

**Key Points:**
- Each subnet has a **primary IPv4 range**
- Can add **secondary ranges** for alias IPs (GKE pods, etc.)
- Subnets cannot overlap within the same VPC
- Instances must be in a zone within the subnet's region

### Create Subnets

```bash
# Create subnet in custom VPC
gcloud compute networks subnets create my-subnet \
  --network=my-custom-network \
  --region=us-central1 \
  --range=10.0.1.0/24

# Create subnet with secondary ranges (for GKE)
gcloud compute networks subnets create gke-subnet \
  --network=my-custom-network \
  --region=us-west1 \
  --range=10.1.0.0/24 \
  --secondary-range pods=10.10.0.0/16,services=10.20.0.0/16
```

### View Subnets

```bash
# List all subnets
gcloud compute networks subnets list

# Describe specific subnet
gcloud compute networks subnets describe my-subnet \
  --region=us-central1

# List subnets in specific network
gcloud compute networks subnets list \
  --network=my-custom-network
```

### Expand Subnet Range

```bash
# Expand subnet (can only expand, not shrink)
gcloud compute networks subnets expand-ip-range my-subnet \
  --region=us-central1 \
  --prefix-length=20
```

### IP Address Ranges

**Valid Private IP Ranges (RFC 1918):**
- `10.0.0.0/8` (10.0.0.0 to 10.255.255.255)
- `172.16.0.0/12` (172.16.0.0 to 172.31.255.255)
- `192.168.0.0/16` (192.168.0.0 to 192.168.255.255)

**Reserved IPs in Each Subnet:**
- **Network address:** First IP (e.g., 10.0.1.0 in 10.0.1.0/24)
- **Gateway address:** Second IP (e.g., 10.0.1.1)
- **Second-to-last IP:** Reserved by Google (e.g., 10.0.1.254)
- **Broadcast address:** Last IP (e.g., 10.0.1.255)

**Example:** In 10.0.1.0/24:
- Total IPs: 256
- Usable IPs: 252 (256 - 4 reserved)

### Internal IP Addresses

**Assign internal IP to instance:**

```bash
# Ephemeral internal IP (automatic)
gcloud compute instances create my-instance \
  --zone=us-central1-a \
  --subnet=my-subnet

# Static internal IP
# First, reserve the address
gcloud compute addresses create my-static-ip \
  --region=us-central1 \
  --subnet=my-subnet \
  --addresses=10.0.1.10

# Then assign to instance
gcloud compute instances create my-instance \
  --zone=us-central1-a \
  --subnet=my-subnet \
  --private-network-ip=10.0.1.10
```

### External IP Addresses

```bash
# Reserve static external IP
gcloud compute addresses create my-external-ip \
  --region=us-central1

# List external IPs
gcloud compute addresses list

# Create instance with external IP
gcloud compute instances create my-instance \
  --zone=us-central1-a \
  --subnet=my-subnet \
  --address=my-external-ip

# Create instance without external IP
gcloud compute instances create my-instance \
  --zone=us-central1-a \
  --subnet=my-subnet \
  --no-address
```

### IPv6 Support

```bash
# Enable IPv6 on subnet (dual-stack)
gcloud compute networks subnets update my-subnet \
  --region=us-central1 \
  --stack-type=IPV4_IPV6 \
  --ipv6-access-type=EXTERNAL

# Create IPv6-only subnet
gcloud compute networks subnets create ipv6-subnet \
  --network=my-custom-network \
  --region=us-west1 \
  --stack-type=IPV6_ONLY \
  --ipv6-access-type=INTERNAL
```

---

## Routes

### Understanding Routes

Routes define paths for packets leaving instances (egress traffic).

**Types of Routes:**

1. **System-Generated Routes:**
   - **Default route:** 0.0.0.0/0 to internet gateway (if external IP exists)
   - **Subnet routes:** Automatically created for each subnet

2. **Custom Routes:**
   - **Static routes:** Manually defined
   - **Dynamic routes:** Learned via Cloud Router (BGP)

### View Routes

```bash
# List all routes in network
gcloud compute routes list \
  --filter="network:my-custom-network"

# Describe specific route
gcloud compute routes describe ROUTE_NAME
```

### Create Custom Static Route

```bash
# Route to on-premises network via VPN
gcloud compute routes create on-prem-route \
  --network=my-custom-network \
  --destination-range=192.168.0.0/16 \
  --next-hop-gateway=my-vpn-gateway \
  --priority=1000

# Route to specific instance
gcloud compute routes create to-nat-instance \
  --network=my-custom-network \
  --destination-range=0.0.0.0/0 \
  --next-hop-instance=nat-gateway \
  --next-hop-instance-zone=us-central1-a \
  --priority=800 \
  --tags=no-external-ip
```

### Delete Route

```bash
gcloud compute routes delete ROUTE_NAME
```

### Route Priority

- Lower number = higher priority
- Range: 0-65535
- Default routes have priority 1000
- Most specific route wins if same priority

---

## Firewall Rules

### Understanding Firewall Rules

VPC firewall rules control traffic to and from VM instances.

**Key Concepts:**
- **Stateful:** Return traffic for allowed connections is automatically permitted
- **Implied rules:** 
  - **Deny all ingress** (priority 65535)
  - **Allow all egress** (priority 65535)
- **Direction:** Ingress (inbound) or Egress (outbound)
- **Priority:** 0-65535 (lower = higher priority)
- **Action:** Allow or Deny

### View Firewall Rules

```bash
# List all firewall rules
gcloud compute firewall-rules list

# List rules for specific network
gcloud compute firewall-rules list \
  --filter="network:my-custom-network"

# Describe specific rule
gcloud compute firewall-rules describe RULE_NAME
```

### Create Firewall Rules

**Allow SSH from anywhere:**

```bash
gcloud compute firewall-rules create allow-ssh \
  --network=my-custom-network \
  --allow=tcp:22 \
  --source-ranges=0.0.0.0/0 \
  --description="Allow SSH from anywhere"
```

**Allow HTTP/HTTPS to web servers:**

```bash
gcloud compute firewall-rules create allow-http-https \
  --network=my-custom-network \
  --allow=tcp:80,tcp:443 \
  --source-ranges=0.0.0.0/0 \
  --target-tags=web-server
```

**Allow internal communication:**

```bash
gcloud compute firewall-rules create allow-internal \
  --network=my-custom-network \
  --allow=tcp:0-65535,udp:0-65535,icmp \
  --source-ranges=10.0.0.0/8
```

**Deny specific traffic:**

```bash
gcloud compute firewall-rules create deny-telnet \
  --network=my-custom-network \
  --action=DENY \
  --rules=tcp:23 \
  --source-ranges=0.0.0.0/0 \
  --priority=900
```

**Allow from specific service account:**

```bash
gcloud compute firewall-rules create allow-from-backend \
  --network=my-custom-network \
  --allow=tcp:3306 \
  --source-service-accounts=backend-sa@project.iam.gserviceaccount.com \
  --target-tags=database
```

### Firewall Rule Components

**Source/Destination Filters:**
- **IP ranges:** CIDR notation (e.g., 10.0.1.0/24)
- **Network tags:** Instance tags (e.g., web-server)
- **Service accounts:** IAM service accounts

**Protocols and Ports:**
```bash
# Single port
--allow=tcp:80

# Multiple ports
--allow=tcp:80,tcp:443

# Port range
--allow=tcp:8000-8100

# All ports for protocol
--allow=tcp

# Multiple protocols
--allow=tcp:80,udp:53,icmp
```

### Update Firewall Rules

```bash
# Update allowed protocols/ports
gcloud compute firewall-rules update allow-ssh \
  --allow=tcp:22,tcp:3389

# Change priority
gcloud compute firewall-rules update allow-ssh \
  --priority=500

# Disable rule (for troubleshooting)
gcloud compute firewall-rules update allow-ssh \
  --disabled

# Enable rule
gcloud compute firewall-rules update allow-ssh \
  --no-disabled
```

### Delete Firewall Rule

```bash
gcloud compute firewall-rules delete RULE_NAME
```

### Firewall Rule Logging

```bash
# Enable logging on rule
gcloud compute firewall-rules update allow-ssh \
  --enable-logging

# View firewall logs in Cloud Logging
gcloud logging read "resource.type=gce_subnetwork AND logName=projects/PROJECT_ID/logs/compute.googleapis.com%2Ffirewall"
```

---

## Cloud VPN

### Understanding Cloud VPN

Cloud VPN securely connects your on-premises network to your VPC network through an IPsec VPN tunnel over the internet.

**Types:**
- **HA VPN:** 99.99% SLA, two interfaces, dynamic routing (BGP)
- **Classic VPN:** 99.9% SLA, one interface, static routing

**Use HA VPN for production!**

### HA VPN Components

1. **HA VPN Gateway:** Google Cloud side (2 external IPs)
2. **External VPN Gateway:** On-premises side or peer cloud
3. **VPN Tunnels:** IPsec tunnels (2+ for HA)
4. **Cloud Router:** Manages BGP sessions for dynamic routing

### Create HA VPN Gateway

```bash
# Create HA VPN gateway
gcloud compute vpn-gateways create my-ha-vpn-gateway \
  --network=my-custom-network \
  --region=us-central1

# View gateway (note the 2 IP addresses)
gcloud compute vpn-gateways describe my-ha-vpn-gateway \
  --region=us-central1
```

### Create External VPN Gateway Resource

```bash
# For on-prem gateway with 2 interfaces
gcloud compute external-vpn-gateways create on-prem-gateway \
  --interfaces \
    0=ON_PREM_IP_0,\
    1=ON_PREM_IP_1
```

### Create Cloud Router

```bash
# Create Cloud Router for BGP
gcloud compute routers create my-router \
  --network=my-custom-network \
  --region=us-central1 \
  --asn=65001
```

### Create VPN Tunnels

```bash
# Tunnel from interface 0 to peer interface 0
gcloud compute vpn-tunnels create tunnel-0 \
  --peer-external-gateway=on-prem-gateway \
  --peer-external-gateway-interface=0 \
  --region=us-central1 \
  --ike-version=2 \
  --shared-secret=SHARED_SECRET \
  --router=my-router \
  --vpn-gateway=my-ha-vpn-gateway \
  --interface=0

# Tunnel from interface 1 to peer interface 1
gcloud compute vpn-tunnels create tunnel-1 \
  --peer-external-gateway=on-prem-gateway \
  --peer-external-gateway-interface=1 \
  --region=us-central1 \
  --ike-version=2 \
  --shared-secret=SHARED_SECRET \
  --router=my-router \
  --vpn-gateway=my-ha-vpn-gateway \
  --interface=1
```

### Configure BGP Sessions

```bash
# BGP session for tunnel-0
gcloud compute routers add-interface my-router \
  --interface-name=if-tunnel-0 \
  --ip-address=169.254.0.1 \
  --mask-length=30 \
  --vpn-tunnel=tunnel-0 \
  --region=us-central1

gcloud compute routers add-bgp-peer my-router \
  --peer-name=bgp-peer-0 \
  --interface=if-tunnel-0 \
  --peer-ip-address=169.254.0.2 \
  --peer-asn=65002 \
  --region=us-central1

# BGP session for tunnel-1
gcloud compute routers add-interface my-router \
  --interface-name=if-tunnel-1 \
  --ip-address=169.254.1.1 \
  --mask-length=30 \
  --vpn-tunnel=tunnel-1 \
  --region=us-central1

gcloud compute routers add-bgp-peer my-router \
  --peer-name=bgp-peer-1 \
  --interface=if-tunnel-1 \
  --peer-ip-address=169.254.1.2 \
  --peer-asn=65002 \
  --region=us-central1
```

### Check VPN Status

```bash
# Check tunnel status
gcloud compute vpn-tunnels describe tunnel-0 \
  --region=us-central1

# View BGP session status
gcloud compute routers get-status my-router \
  --region=us-central1

# View learned routes
gcloud compute routes list \
  --filter="nextHopVpnTunnel:tunnel-0"
```

---

## Cloud Interconnect

### Understanding Cloud Interconnect

Cloud Interconnect provides **private, high-speed connectivity** between on-premises and Google Cloud (does not traverse the internet).

**Types:**

1. **Dedicated Interconnect:** 10 Gbps or 100 Gbps direct connection
2. **Partner Interconnect:** 50 Mbps to 50 Gbps via service provider

**When to Use:**
- High bandwidth requirements (multi-Gbps)
- Low latency requirements
- Predictable network performance
- Reduce egress costs

### Dedicated Interconnect Overview

**Requires:**
- Physical connection to Google colocation facility
- BGP routing configuration
- VLAN attachments (multiple VLANs over single connection)

### Partner Interconnect Overview

**Benefits:**
- No need for physical connection to Google facility
- Service provider handles physical connectivity
- Flexible bandwidth (50 Mbps - 50 Gbps)

### Create VLAN Attachment

```bash
# Create VLAN attachment for Dedicated Interconnect
gcloud compute interconnects attachments dedicated create my-vlan-attachment \
  --region=us-central1 \
  --router=my-router \
  --interconnect=my-interconnect \
  --vlan=100

# Create VLAN attachment for Partner Interconnect
gcloud compute interconnects attachments partner create my-partner-attachment \
  --region=us-central1 \
  --router=my-router \
  --edge-availability-domain=AVAILABILITY_DOMAIN_1
```

### View Interconnect Details

```bash
# List interconnects
gcloud compute interconnects list

# List VLAN attachments
gcloud compute interconnects attachments list

# Describe VLAN attachment
gcloud compute interconnects attachments describe my-vlan-attachment \
  --region=us-central1
```

---

## Shared VPC

### Understanding Shared VPC

Shared VPC allows multiple projects to share a common VPC network.

**Key Concepts:**
- **Host Project:** Contains the Shared VPC network
- **Service Projects:** Attach to host project, use its networks
- **Centralized network administration**
- **Decentralized resource management**

### Roles

- **Shared VPC Admin:** Enables host project, attaches service projects
- **Network Admin:** Manages network resources in host project
- **Service Project Admin:** Creates resources in service project

### Enable Shared VPC

```bash
# Enable host project
gcloud compute shared-vpc enable HOST_PROJECT_ID

# Attach service project
gcloud compute shared-vpc associated-projects add SERVICE_PROJECT_ID \
  --host-project=HOST_PROJECT_ID
```

### Grant Permissions

```bash
# Grant Network User role to service project admin (whole project)
gcloud projects add-iam-policy-binding HOST_PROJECT_ID \
  --member=user:admin@example.com \
  --role=roles/compute.networkUser

# Grant Network User role for specific subnet
gcloud compute networks subnets add-iam-policy-binding my-subnet \
  --region=us-central1 \
  --member=user:admin@example.com \
  --role=roles/compute.networkUser
```

### View Shared VPC Configuration

```bash
# List host projects
gcloud compute shared-vpc list-associated-resources HOST_PROJECT_ID

# Get host project for service project
gcloud compute shared-vpc get-host-project SERVICE_PROJECT_ID
```

### Create Instance in Shared VPC

```bash
# From service project, use host project subnet
gcloud compute instances create my-instance \
  --zone=us-central1-a \
  --subnet=projects/HOST_PROJECT_ID/regions/us-central1/subnetworks/my-subnet
```

---

## VPC Peering

### Understanding VPC Peering

VPC Network Peering connects two VPC networks (same or different projects/organizations) allowing private communication.

**Key Features:**
- **Private connectivity:** No external IPs needed
- **Low latency:** Direct connection
- **No single point of failure**
- **Works across organizations**

**Limitations:**
- Subnet IP ranges cannot overlap
- Peering is not transitive (A-B, B-C does NOT mean A-C)
- Max 25 peered networks per VPC

### Create VPC Peering

```bash
# From Network A side
gcloud compute networks peerings create peer-a-to-b \
  --network=network-a \
  --peer-project=PROJECT_B_ID \
  --peer-network=network-b \
  --auto-create-routes

# From Network B side (must create from both sides)
gcloud compute networks peerings create peer-b-to-a \
  --network=network-b \
  --peer-project=PROJECT_A_ID \
  --peer-network=network-a \
  --auto-create-routes
```

### View VPC Peering

```bash
# List peerings for network
gcloud compute networks peerings list \
  --network=network-a

# Describe specific peering
gcloud compute networks peerings describe peer-a-to-b \
  --network=network-a
```

### Delete VPC Peering

```bash
gcloud compute networks peerings delete peer-a-to-b \
  --network=network-a
```

---

## Common Networking Tasks

### Configure Private Google Access

**Allows instances without external IPs to access Google APIs.**

```bash
# Enable on subnet
gcloud compute networks subnets update my-subnet \
  --region=us-central1 \
  --enable-private-ip-google-access

# Verify
gcloud compute networks subnets describe my-subnet \
  --region=us-central1 \
  --format="get(privateIpGoogleAccess)"
```

### Configure Cloud NAT

**Allows instances without external IPs to access the internet.**

```bash
# Create Cloud Router first
gcloud compute routers create nat-router \
  --network=my-custom-network \
  --region=us-central1

# Create Cloud NAT
gcloud compute routers nats create my-nat \
  --router=nat-router \
  --region=us-central1 \
  --nat-all-subnet-ip-ranges \
  --auto-allocate-nat-external-ips
```

### Test Connectivity

```bash
# SSH to instance
gcloud compute ssh my-instance --zone=us-central1-a

# Test internal connectivity
ping 10.0.2.5

# Test external connectivity
ping google.com

# Check route table
ip route

# Check DNS
nslookup google.com
```

### Troubleshoot Network Issues

```bash
# Check firewall rules blocking traffic
gcloud compute firewall-rules list \
  --filter="network:my-custom-network AND denied.IPProtocol=tcp"

# Test connectivity with Connectivity Test (Network Intelligence)
gcloud network-management connectivity-tests create my-test \
  --source-instance=instance-a \
  --source-instance-zone=us-central1-a \
  --destination-instance=instance-b \
  --destination-instance-zone=us-west1-a \
  --protocol=tcp \
  --destination-port=443
```

---

## ACE Exam Tips

### 1. VPC Network Concepts
- **VPC networks are global**, subnets are regional
- **Auto mode** = automatic subnets per region
- **Custom mode** = full control (recommended for production)
- Conversion: Auto → Custom (one-way, irreversible)

### 2. IP Addressing
- **4 reserved IPs** in every subnet (network, gateway, penultimate, broadcast)
- **Private IP ranges:** 10.x.x.x, 172.16.x.x-172.31.x.x, 192.168.x.x
- **Ephemeral** (temporary) vs **Static** (reserved) IPs
- External IP costs money; use Cloud NAT for instances without external IP

### 3. Firewall Rules
- **Implied deny ingress**, **implied allow egress**
- **Stateful:** Return traffic automatically allowed
- **Priority:** 0-65535 (lower number = higher priority)
- **Tags** identify instances
- **Deny rules** override allow rules at same priority

### 4. Routes
- **System routes:** Default (0.0.0.0/0) and subnet routes (automatic)
- **Custom routes:** Static or dynamic (BGP via Cloud Router)
- **Priority:** Lower number wins
- **Most specific route** wins if same priority

### 5. Cloud VPN
- **HA VPN:** 99.99% SLA, 2 interfaces, BGP required
- **Classic VPN:** 99.9% SLA, 1 interface, static routing
- **IPsec tunnel** over internet
- **3 Gbps per tunnel** max bandwidth

### 6. Cloud Interconnect
- **Dedicated:** 10/100 Gbps, physical connection
- **Partner:** 50 Mbps - 50 Gbps, via provider
- **Private connection** (does not use internet)
- **Lower latency**, **higher bandwidth** than VPN

### 7. Shared VPC
- **Host project:** Contains VPC network
- **Service projects:** Use host project network
- **Centralized network admin**, decentralized resource admin
- **Billing:** Attributed to service project

### 8. VPC Peering
- **Private connectivity** between VPCs
- **No overlapping subnets**
- **Not transitive:** A↔B, B↔C ≠ A↔C
- **Max 25 peers** per VPC

### 9. Private Google Access
- Enables instances **without external IPs** to reach Google APIs
- Configured **per subnet**
- Requires route to 199.36.153.8/30 (usually automatic)

### 10. Cloud NAT
- Allows instances **without external IPs** to access internet
- **Regional resource**
- Requires **Cloud Router**
- **No inbound connections** (outbound only)

### 11. Common Exam Scenarios

**Scenario:** "Instances can't reach Google Cloud Storage"
- **Check:** Private Google Access enabled on subnet

**Scenario:** "Instance without external IP can't update packages"
- **Solution:** Configure Cloud NAT

**Scenario:** "Need to connect two VPCs"
- **Options:** VPC Peering (private) or VPN (encrypted over internet)

**Scenario:** "On-premises needs to access GCP with high bandwidth"
- **Solution:** Cloud Interconnect (Dedicated or Partner)

**Scenario:** "Multiple projects need to share one network"
- **Solution:** Shared VPC

**Scenario:** "Firewall rule not working"
- **Check:** Priority, direction (ingress/egress), targets (tags/service accounts), source/destination

### 12. Important gcloud Commands

```bash
# Networks
gcloud compute networks list
gcloud compute networks create
gcloud compute networks describe

# Subnets
gcloud compute networks subnets list
gcloud compute networks subnets create
gcloud compute networks subnets expand-ip-range

# Firewall
gcloud compute firewall-rules list
gcloud compute firewall-rules create
gcloud compute firewall-rules update
gcloud compute firewall-rules delete

# Routes
gcloud compute routes list
gcloud compute routes create

# VPN
gcloud compute vpn-gateways create
gcloud compute vpn-tunnels create
gcloud compute routers create

# Shared VPC
gcloud compute shared-vpc enable
gcloud compute shared-vpc associated-projects add

# VPC Peering
gcloud compute networks peerings create
```

### 13. Troubleshooting Checklist
1. **Can't SSH/RDP to instance:**
   - Check firewall rules (allow tcp:22 or tcp:3389)
   - Check external IP exists (or use Cloud IAP)
   - Check subnet has default route to internet

2. **Instance can't reach other instances:**
   - Check firewall rules (allow internal)
   - Check instances are in same VPC or peered VPCs
   - Check routes exist

3. **Instance can't reach internet:**
   - Check external IP exists OR Cloud NAT configured
   - Check firewall egress rules (usually allowed by default)
   - Check default route exists (0.0.0.0/0)

4. **High latency to on-premises:**
   - Consider Cloud Interconnect instead of VPN
   - Check VPN tunnel bandwidth limits

### 14. Best Practices
- Use **custom mode VPC** for production
- Use **network tags** for firewall rules
- Enable **VPC Flow Logs** for troubleshooting
- Use **Private Google Access** for instances without external IPs
- Use **Cloud NAT** for internet access without external IPs
- Design **non-overlapping subnet ranges** for future peering/VPN
