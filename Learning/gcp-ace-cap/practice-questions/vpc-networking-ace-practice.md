# VPC Networking - ACE Practice Questions

## Question 1
You need to create a custom VPC network with two subnets: one in us-central1 (10.1.0.0/24) and one in europe-west1 (10.2.0.0/24). Which commands should you use?

**A)**
```bash
gcloud compute networks create my-vpc --subnet-mode=custom
gcloud compute networks subnets create subnet-us --network=my-vpc --region=us-central1 --range=10.1.0.0/24
gcloud compute networks subnets create subnet-eu --network=my-vpc --region=europe-west1 --range=10.2.0.0/24
```

**B)**
```bash
gcloud compute networks create my-vpc --subnet-mode=auto
gcloud compute networks subnets create subnet-us --network=my-vpc --region=us-central1 --range=10.1.0.0/24
```

**C)**
```bash
gcloud compute vpcs create my-vpc
gcloud compute subnets create subnet-us --vpc=my-vpc --region=us-central1 --cidr=10.1.0.0/24
```

**D)**
```bash
gcloud network create my-vpc --mode=custom --subnets=us-central1:10.1.0.0/24,europe-west1:10.2.0.0/24
```

**Correct Answer:** A

**Explanation:**
- Option A is correct because:
  - Creates custom mode VPC (subnets must be explicitly created)
  - Correctly creates subnets with proper syntax
  - `--subnet-mode=custom` allows manual subnet management
  - Each subnet specifies network, region, and IP range

Create VPC and subnets:
```bash
# Step 1: Create custom VPC
gcloud compute networks create my-vpc \
  --subnet-mode=custom \
  --bgp-routing-mode=regional

# Step 2: Create subnet in us-central1
gcloud compute networks subnets create subnet-us \
  --network=my-vpc \
  --region=us-central1 \
  --range=10.1.0.0/24

# Step 3: Create subnet in europe-west1
gcloud compute networks subnets create subnet-eu \
  --network=my-vpc \
  --region=europe-west1 \
  --range=10.2.0.0/24 \
  --enable-private-ip-google-access

# Verify
gcloud compute networks subnets list --network=my-vpc
```

With secondary ranges:
```bash
gcloud compute networks subnets create subnet-gke \
  --network=my-vpc \
  --region=us-central1 \
  --range=10.3.0.0/24 \
  --secondary-range=pods=10.4.0.0/14,services=10.8.0.0/20
```

- Option B is incorrect because:
  - Auto mode VPCs automatically create subnets in all regions
  - Cannot manually create subnets in auto mode initially
  - Contradicts custom subnet creation

- Option C is incorrect because:
  - Wrong command: `gcloud compute vpcs` doesn't exist
  - Should be `gcloud compute networks`
  - Wrong parameter: `--cidr` should be `--range`

- Option D is incorrect because:
  - Wrong command structure
  - `gcloud network` should be `gcloud compute networks`
  - Cannot create subnets in the same command as VPC

**VPC Modes:**
- **Auto mode**: Automatically creates subnets in all regions (10.128.0.0/9)
- **Custom mode**: You create subnets manually (recommended for production)

---

## Question 2
You need to allow SSH (port 22) access to VM instances tagged with "ssh-enabled" from your office IP (203.0.113.0). What firewall rule should you create?

**A)**
```bash
gcloud compute firewall-rules create allow-ssh \
  --network=default \
  --allow=tcp:22 \
  --source-ranges=203.0.113.0/32 \
  --target-tags=ssh-enabled
```

**B)**
```bash
gcloud compute firewall-rules create allow-ssh \
  --network=default \
  --allow=ssh \
  --source-ranges=203.0.113.0 \
  --target-tags=ssh-enabled
```

**C)**
```bash
gcloud compute firewall-rules create allow-ssh \
  --allow=tcp:22 \
  --source-ranges=203.0.113.0/32 \
  --destination-tags=ssh-enabled
```

**D)**
```bash
gcloud compute instances add-firewall-rule ssh-enabled \
  --allow=tcp:22 \
  --source-ranges=203.0.113.0/32
```

**Correct Answer:** A

**Explanation:**
- Option A is correct because:
  - Specifies protocol and port correctly (`tcp:22`)
  - Uses `/32` notation for single IP (best practice)
  - `--target-tags` applies rule to tagged instances
  - Specifies network explicitly

Create firewall rules:
```bash
# Allow SSH from specific IP
gcloud compute firewall-rules create allow-ssh-office \
  --network=default \
  --allow=tcp:22 \
  --source-ranges=203.0.113.0/32 \
  --target-tags=ssh-enabled \
  --description="Allow SSH from office"

# Allow HTTP/HTTPS to web servers
gcloud compute firewall-rules create allow-web \
  --network=default \
  --allow=tcp:80,tcp:443 \
  --source-ranges=0.0.0.0/0 \
  --target-tags=web-server

# Allow internal traffic between VMs
gcloud compute firewall-rules create allow-internal \
  --network=my-vpc \
  --allow=tcp:1-65535,udp:1-65535,icmp \
  --source-ranges=10.1.0.0/24,10.2.0.0/24

# Deny all egress to internet (high priority)
gcloud compute firewall-rules create deny-internet-egress \
  --network=my-vpc \
  --direction=EGRESS \
  --action=DENY \
  --rules=all \
  --destination-ranges=0.0.0.0/0 \
  --priority=1000 \
  --target-tags=isolated

# List firewall rules
gcloud compute firewall-rules list --filter="network:default"

# View specific rule
gcloud compute firewall-rules describe allow-ssh-office
```

- Option B is incorrect because:
  - `--allow=ssh` is not valid (must specify protocol:port)
  - Missing `/32` (works but not best practice for single IP)
  - Should be `tcp:22`, not `ssh`

- Option C is incorrect because:
  - Missing `--network` parameter (required)
  - `--destination-tags` doesn't exist (should be `--target-tags`)
  - Firewall rules use target-tags for ingress

- Option D is incorrect because:
  - Wrong command structure
  - Firewall rules are network-level, not instance-level
  - `add-firewall-rule` is not a valid gcloud command

**Firewall Rule Components:**
- **network**: Which VPC the rule applies to
- **allow/deny**: Action and protocols
- **source-ranges**: Source IP ranges (ingress)
- **destination-ranges**: Destination IPs (egress)
- **target-tags**: Apply to instances with specific tags
- **priority**: Lower number = higher priority (default: 1000)

---

## Question 3
Your VM instances in a private subnet need to download updates from the internet but should not have external IP addresses. What should you configure?

**A)** Create a Cloud NAT gateway

**B)** Enable Private Google Access

**C)** Create a VPN tunnel

**D)** Assign ephemeral external IPs

**Correct Answer:** A

**Explanation:**
- Option A is correct because:
  - Cloud NAT allows instances without external IPs to access the internet
  - Instances can download updates, patches, etc.
  - Outbound connections only (more secure)
  - No inbound connections from internet
  - Does NOT provide access to Google APIs (that's Private Google Access)

Setup Cloud NAT:
```bash
# 1. Create Cloud Router
gcloud compute routers create my-router \
  --network=my-vpc \
  --region=us-central1

# 2. Create Cloud NAT
gcloud compute routers nats create my-nat \
  --router=my-router \
  --region=us-central1 \
  --nat-all-subnet-ip-ranges \
  --auto-allocate-nat-external-ips

# Alternative: Specify subnets and IP addresses
gcloud compute routers nats create my-nat \
  --router=my-router \
  --region=us-central1 \
  --nat-custom-subnet-ip-ranges=subnet-priv \
  --nat-external-ip-pool=nat-ip-1,nat-ip-2

# Verify
gcloud compute routers nats describe my-nat \
  --router=my-router \
  --region=us-central1

# Create VM without external IP (will use Cloud NAT)
gcloud compute instances create private-vm \
  --subnet=subnet-priv \
  --no-address \
  --zone=us-central1-a

# Test internet access from VM
gcloud compute ssh private-vm --zone=us-central1-a
# Inside VM:
curl http://www.google.com  # Works via Cloud NAT
```

- Option B is incorrect because:
  - Private Google Access is for accessing Google APIs (not general internet)
  - Allows access to Cloud Storage, BigQuery, etc.
  - Does NOT allow downloading from arbitrary internet sites
  - Different use case

- Option C is incorrect because:
  - VPN is for connecting to on-premises or other networks
  - Doesn't provide internet access
  - More complex and not designed for this use case

- Option D is incorrect because:
  - Question specifically requires NO external IPs
  - Contradicts the requirement
  - Less secure (instances are internet-accessible)

**Cloud NAT vs Private Google Access:**
- **Cloud NAT**: Access to internet (e.g., apt-get, yum, wget from external sites)
- **Private Google Access**: Access to Google APIs (GCS, BigQuery, etc.)
- Often used together: Private Google Access for GCP services, Cloud NAT for internet

Enable Private Google Access:
```bash
gcloud compute networks subnets update subnet-priv \
  --region=us-central1 \
  --enable-private-ip-google-access
```

---

## Question 4
You need to connect your on-premises data center to Google Cloud with a dedicated, high-bandwidth connection (10 Gbps). What should you use?

**A)** Cloud VPN

**B)** Dedicated Interconnect

**C)** Partner Interconnect

**D)** Direct Peering

**Correct Answer:** B (or C depending on requirements)

**Explanation:**
- Option B is correct if you can meet colocation requirements:
  - Dedicated Interconnect provides 10 Gbps or 100 Gbps dedicated connections
  - Direct physical connection to Google network
  - Lowest latency and highest bandwidth
  - Requires colocation in a supported facility
  - SLA-backed

Setup Dedicated Interconnect:
```bash
# 1. Create Interconnect attachment
gcloud compute interconnects attachments dedicated create my-attachment \
  --router=my-router \
  --region=us-central1 \
  --interconnect=my-interconnect \
  --candidate-subnets=169.254.0.0/29

# 2. Configure Cloud Router for BGP
gcloud compute routers create my-router \
  --network=my-vpc \
  --region=us-central1 \
  --asn=65001

# 3. Add BGP peer
gcloud compute routers add-bgp-peer my-router \
  --peer-name=on-prem \
  --peer-asn=65002 \
  --interface=attachment-interface \
  --peer-ip-address=169.254.0.2 \
  --region=us-central1

# Verify
gcloud compute interconnects attachments describe my-attachment \
  --region=us-central1
```

- Option C is also often correct:
  - Partner Interconnect if you can't meet colocation requirements
  - Works through a supported service provider
  - Lower commitment (50 Mbps - 10 Gbps increments)
  - More flexible
  - Slightly higher latency than Dedicated

- Option A is incorrect because:
  - Cloud VPN max bandwidth is ~3 Gbps per tunnel
  - Goes over public internet (encrypted)
  - Higher latency than Interconnect
  - Doesn't meet "dedicated" requirement

- Option D is incorrect because:
  - Direct Peering is for accessing Google services (not VPC)
  - Different use case (Google Workspace, YouTube, etc.)
  - Not for private VPC connectivity

**Connection Options Comparison:**

| Option | Bandwidth | Latency | Cost | Use Case |
|--------|-----------|---------|------|----------|
| **Cloud VPN** | 3 Gbps/tunnel | Higher | Low | Small to medium, encrypted |
| **Dedicated Interconnect** | 10/100 Gbps | Lowest | High | Enterprise, dedicated |
| **Partner Interconnect** | 50 Mbps - 10 Gbps | Low | Medium | Enterprise, flexible |
| **Direct Peering** | 10+ Gbps | Low | Free* | Google services only |

*Direct Peering: No GCP charges but ISP costs apply

---

## Question 5
You have two VPCs (vpc-1 and vpc-2) and need to allow instances in both VPCs to communicate privately. What should you configure?

**A)** VPC Peering

**B)** External IP addresses on all instances

**C)** Shared VPC

**D)** Cloud VPN between VPCs

**Correct Answer:** A

**Explanation:**
- Option A is correct because:
  - VPC Peering connects two VPCs for private communication
  - Uses internal IP addresses
  - Low latency (Google's network)
  - No bandwidth costs between peered VPCs in same region
  - Can peer VPCs in different projects

Setup VPC Peering:
```bash
# Create peering from vpc-1 to vpc-2
gcloud compute networks peerings create peer-1-to-2 \
  --network=vpc-1 \
  --peer-project=project-2 \
  --peer-network=vpc-2 \
  --auto-create-routes

# Create peering from vpc-2 to vpc-1 (must be bidirectional)
gcloud compute networks peerings create peer-2-to-1 \
  --network=vpc-2 \
  --peer-project=project-1 \
  --peer-network=vpc-1 \
  --auto-create-routes

# Verify peering
gcloud compute networks peerings list --network=vpc-1

# Check peering status
gcloud compute networks peerings describe peer-1-to-2 \
  --network=vpc-1
```

VPC Peering Example:
```
vpc-1 (10.1.0.0/16) <----Peering----> vpc-2 (10.2.0.0/16)
     |                                        |
  Instance A                              Instance B
  10.1.0.5                                10.2.0.10

# Instance A can ping Instance B using 10.2.0.10
# No external IPs needed!
```

- Option B is incorrect because:
  - Uses public internet (slower, less secure)
  - Incurs egress charges
  - Requires firewall rules for external IPs
  - Not a "private" solution

- Option C is incorrect because:
  - Shared VPC is for sharing a VPC across multiple projects
  - Different use case (not for connecting separate VPCs)
  - Both VMs would be in the SAME VPC

- Option D is incorrect because:
  - Cloud VPN is for on-premises or cross-cloud connections
  - More complex setup
  - VPC Peering is the native GCP solution for VPC-to-VPC communication

**VPC Peering Limitations:**
- No transitive peering (if A peers with B, and B peers with C, A cannot reach C)
- IP ranges cannot overlap
- Peering must be bidirectional (both sides must create peering)
- Max 25 peering connections per VPC

**Transitive Peering Example (NOT ALLOWED):**
```
VPC-A <--peer--> VPC-B <--peer--> VPC-C
         ✓                 ✓

VPC-A -?-> VPC-C ✗ (No connectivity without direct peering)
```

---

## Question 6
You need to create a load balancer that distributes HTTP traffic across Compute Engine instances in multiple regions. What type of load balancer should you create?

**A)** Internal HTTP(S) Load Balancer

**B)** External HTTP(S) Load Balancer

**C)** Network Load Balancer

**D)** Internal TCP/UDP Load Balancer

**Correct Answer:** B

**Explanation:**
- Option B is correct because:
  - External HTTP(S) Load Balancer is global (multi-region)
  - Layer 7 load balancing (HTTP/HTTPS)
  - Single global anycast IP
  - SSL termination
  - URL-based routing
  - Cloud CDN integration

Create External HTTP(S) Load Balancer:
```bash
# 1. Create instance template
gcloud compute instance-templates create web-template \
  --machine-type=n1-standard-1 \
  --image-family=debian-11 \
  --image-project=debian-cloud \
  --tags=web-server \
  --metadata=startup-script='#! /bin/bash
    apt-get update
    apt-get install -y apache2
    echo "Hello from $(hostname)" > /var/www/html/index.html'

# 2. Create managed instance groups in multiple regions
gcloud compute instance-groups managed create web-mig-us \
  --template=web-template \
  --size=2 \
  --region=us-central1

gcloud compute instance-groups managed create web-mig-eu \
  --template=web-template \
  --size=2 \
  --region=europe-west1

# Set named ports
gcloud compute instance-groups managed set-named-ports web-mig-us \
  --named-ports=http:80 \
  --region=us-central1

gcloud compute instance-groups managed set-named-ports web-mig-eu \
  --named-ports=http:80 \
  --region=europe-west1

# 3. Create health check
gcloud compute health-checks create http web-health-check \
  --port=80 \
  --request-path=/

# 4. Create backend service
gcloud compute backend-services create web-backend \
  --protocol=HTTP \
  --health-checks=web-health-check \
  --global

# Add backends
gcloud compute backend-services add-backend web-backend \
  --instance-group=web-mig-us \
  --instance-group-region=us-central1 \
  --global

gcloud compute backend-services add-backend web-backend \
  --instance-group=web-mig-eu \
  --instance-group-region=europe-west1 \
  --global

# 5. Create URL map
gcloud compute url-maps create web-map \
  --default-service=web-backend

# 6. Create target HTTP proxy
gcloud compute target-http-proxies create web-proxy \
  --url-map=web-map

# 7. Create forwarding rule
gcloud compute forwarding-rules create web-lb-rule \
  --global \
  --target-http-proxy=web-proxy \
  --ports=80

# Get load balancer IP
gcloud compute forwarding-rules describe web-lb-rule --global
```

- Option A is incorrect because:
  - Internal load balancers are for internal traffic only (not internet-facing)
  - Regional, not global
  - Cannot distribute traffic from the internet

- Option C is incorrect because:
  - Network Load Balancer is Layer 4 (TCP/UDP)
  - Regional, not global
  - No HTTP-specific features (no URL routing, no SSL termination)

- Option D is incorrect because:
  - Internal load balancer (not external)
  - Layer 4 only
  - Internal traffic only

**Load Balancer Types:**

| Type | Layer | Scope | Use Case |
|------|-------|-------|----------|
| **External HTTP(S)** | 7 | Global | Web applications, global traffic |
| **Internal HTTP(S)** | 7 | Regional | Internal microservices |
| **External Network** | 4 | Regional | TCP/UDP applications |
| **Internal TCP/UDP** | 4 | Regional | Internal databases, apps |

---

## Question 7
You need to allow egress traffic to only specific external IP addresses (198.51.100.0/24) from VMs in your VPC. What should you create?

**A)** Egress firewall rule with allow action for destination-ranges=198.51.100.0/24

**B)** Egress firewall rule with deny action for destination-ranges=0.0.0.0/0, and priority higher than default

**C)** Create two egress rules: one to allow 198.51.100.0/24 (priority 1000) and one to deny all (priority 2000)

**D)** You cannot control egress traffic with firewall rules

**Correct Answer:** C

**Explanation:**
- Option C is correct because:
  - First rule allows specific destination (priority 1000 - higher priority)
  - Second rule denies all other egress (priority 2000 - lower priority)
  - Lower priority number = higher priority (evaluated first)
  - Allows only desired destination

Create egress firewall rules:
```bash
# 1. Allow egress to specific IP range (high priority)
gcloud compute firewall-rules create allow-specific-egress \
  --network=my-vpc \
  --direction=EGRESS \
  --action=ALLOW \
  --rules=all \
  --destination-ranges=198.51.100.0/24 \
  --priority=1000 \
  --target-tags=restricted-egress

# 2. Deny all other egress (low priority)
gcloud compute firewall-rules create deny-all-egress \
  --network=my-vpc \
  --direction=EGRESS \
  --action=DENY \
  --rules=all \
  --destination-ranges=0.0.0.0/0 \
  --priority=2000 \
  --target-tags=restricted-egress

# Verify firewalls
gcloud compute firewall-rules list \
  --filter="direction:EGRESS" \
  --sort-by=priority
```

How priority works:
```
Priority 1000: ALLOW to 198.51.100.0/24  (evaluated first)
Priority 2000: DENY to 0.0.0.0/0         (evaluated second)

Traffic to 198.51.100.5 → Matches priority 1000 → ALLOWED ✓
Traffic to 8.8.8.8      → Skips priority 1000, matches priority 2000 → DENIED ✗
```

- Option A is incorrect because:
  - Only allowing specific destination doesn't block other destinations
  - Default egress rule allows all (priority 65535)
  - Need to explicitly deny other destinations

- Option B is incorrect because:
  - Would block ALL egress including the allowed range
  - No exception for 198.51.100.0/24
  - Need allow rule with higher priority

- Option D is incorrect because:
  - You CAN control egress with firewall rules
  - Both allow and deny rules support egress direction

**Firewall Rule Priority:**
- Range: 0-65535
- Lower number = higher priority
- Default allow ingress: 65534
- Default deny ingress: 65535
- Default allow egress: 65535

---

## Question 8
Your application needs to resolve private DNS names for VMs in your VPC (e.g., my-vm.internal). What should you use?

**A)** Cloud DNS private zones

**B)** Automatic internal DNS (default)

**C)** External DNS server

**D)** /etc/hosts file on each VM

**Correct Answer:** B (for automatic VM name resolution) or A (for custom domains)

**Explanation:**
For the basic use case (my-vm.internal):

**Option B is correct because:**
- GCP automatically provides internal DNS for VMs
- Resolves [instance-name].[zone].c.[project-id].internal
- Also resolves [instance-name].internal if unique in project
- No configuration needed

Automatic DNS resolution:
```bash
# Create VMs
gcloud compute instances create vm-1 --zone=us-central1-a
gcloud compute instances create vm-2 --zone=us-central1-a

# SSH to vm-1
gcloud compute ssh vm-1 --zone=us-central1-a

# Inside vm-1, ping vm-2 by name
ping vm-2.internal  # Works automatically!
ping vm-2.us-central1-a.c.my-project.internal  # FQDN also works

# Resolve hostname
nslookup vm-2.internal
# Returns internal IP of vm-2
```

**Option A is also correct for custom domains:**
- Cloud DNS private zones for custom domains
- More flexible than automatic DNS
- Can create custom records

Create private DNS zone:
```bash
# 1. Create private zone
gcloud dns managed-zones create my-private-zone \
  --description="Private zone for my VPC" \
  --dns-name=example.internal. \
  --networks=my-vpc \
  --visibility=private

# 2. Add A record
gcloud dns record-sets create db.example.internal. \
  --zone=my-private-zone \
  --type=A \
  --ttl=300 \
  --rrdatas=10.1.0.10

# 3. Add CNAME record
gcloud dns record-sets create www.example.internal. \
  --zone=my-private-zone \
  --type=CNAME \
  --ttl=300 \
  --rrdatas=db.example.internal.

# Verify
gcloud dns record-sets list --zone=my-private-zone

# Test from VM
ping db.example.internal  # Resolves to 10.1.0.10
```

- Option C is incorrect because:
  - External DNS cannot resolve internal IPs
  - More complex to configure
  - Not necessary for internal names

- Option D is incorrect because:
  - Manual management
  - Doesn't scale
  - No dynamic updates
  - Built-in DNS is better

**DNS Resolution in VPC:**
- **Metadata server** (169.254.169.254) handles DNS queries
- Resolves internal names using Cloud DNS
- Also resolves external names (forwards to 8.8.8.8/8.8.4.4)

---

## Question 9
You need to monitor and log all network traffic (accepted and denied) to your VMs for security auditing. What should you enable?

**A)** Cloud Logging

**B)** VPC Flow Logs

**C)** Firewall Rules Logging

**D)** Packet Mirroring

**Correct Answer:** C (for firewall decisions) or B (for traffic analysis)

**Explanation:**
For the specific requirement "accepted and denied" traffic:

**Option C is correct:**
- Firewall Rules Logging logs every firewall allow/deny decision
- Shows which firewall rule was applied
- Includes source, destination, protocol, port
- Essential for security auditing

Enable Firewall Logging:
```bash
# Enable logging on existing firewall rule
gcloud compute firewall-rules update allow-ssh \
  --enable-logging \
  --logging-metadata=include-all

# Create new rule with logging enabled
gcloud compute firewall-rules create allow-web-logged \
  --network=my-vpc \
  --allow=tcp:80,tcp:443 \
  --source-ranges=0.0.0.0/0 \
  --enable-logging \
  --logging-metadata=include-all

# View logs in Cloud Logging
gcloud logging read "resource.type=gce_subnetwork AND jsonPayload.rule_details.reference!=NULL" \
  --limit=50 \
  --format=json
```

View in Cloud Console:
```
Logging > Logs Explorer > Query:
resource.type="gce_subnetwork"
jsonPayload.disposition=("ALLOWED" OR "DENIED")
```

**Option B is also valuable:**
- VPC Flow Logs captures network flows (sampled)
- Shows connections between VM pairs
- Useful for traffic analysis and troubleshooting

Enable VPC Flow Logs:
```bash
# Enable on subnet
gcloud compute networks subnets update subnet-us \
  --region=us-central1 \
  --enable-flow-logs \
  --logging-aggregation-interval=interval-5-sec \
  --logging-flow-sampling=0.5 \
  --logging-metadata=include-all

# View flow logs
gcloud logging read "resource.type=gce_subnetwork AND logName:compute.googleapis.com/vpc_flows" \
  --limit=10
```

- Option A is incorrect because:
  - Cloud Logging is the platform, not a specific feature
  - Need to enable VPC Flow Logs or Firewall Logging specifically

- Option D is incorrect because:
  - Packet Mirroring clones packets for deep inspection
  - Used with IDS/IPS solutions
  - Overkill for basic auditing
  - More expensive

**Comparison:**

| Feature | Use Case | Detail Level | Cost |
|---------|----------|--------------|------|
| **Firewall Logging** | Security auditing | Firewall decisions | Low |
| **VPC Flow Logs** | Traffic analysis | Connection metadata | Medium |
| **Packet Mirroring** | Deep inspection | Full packet capture | High |

---

## Question 10
You need to ensure that traffic between two Compute Engine instances in the same VPC subnet is automatically allowed. What should you check?

**A)** VPC peering is configured

**B)** Default allow ingress rule from 10.128.0.0/9

**C)** Implied allow ingress for same subnet

**D)** External IP addresses are configured

**Correct Answer:** C

**Explanation:**
- Option C is correct because:
  - VPC has implied allow rules for internal traffic
  - Instances in same VPC can communicate unless explicitly blocked
  - No firewall rule creation needed for same-subnet communication
  - Automatic and cannot be removed

Implied VPC Rules:
```
1. Implied allow egress (all traffic can leave)
   - Destination: 0.0.0.0/0
   - Action: ALLOW
   - Priority: 65535

2. Implied deny ingress (all incoming traffic is blocked by default)
   - Source: 0.0.0.0/0
   - Action: DENY
   - Priority: 65535 (lowest)

3. Implied allow ingress from same VPC
   - Source: VPC internal IP ranges
   - Action: ALLOW (for same VPC)
   - Cannot be seen or deleted
```

Test connectivity:
```bash
# Create two VMs in same subnet
gcloud compute instances create vm-1 --subnet=subnet-us --zone=us-central1-a
gcloud compute instances create vm-2 --subnet=subnet-us --zone=us-central1-a

# SSH to vm-1
gcloud compute ssh vm-1 --zone=us-central1-a

# Inside vm-1
ping [vm-2-internal-ip]  # Works automatically!
```

- Option A is incorrect because:
  - VPC peering is for connecting DIFFERENT VPCs
  - Not needed for same VPC communication

- Option B is incorrect because:
  - 10.128.0.0/9 is the auto-mode subnet range
  - Doesn't explain same-subnet communication
  - Implied rules are broader

- Option D is incorrect because:
  - External IPs not needed for internal communication
  - Internal IPs are sufficient
  - External IPs are for internet connectivity

**VPC Firewall Hierarchy:**
```
Priority 0-65534: Custom rules
↓
Priority 65535: Implied allow egress
↓
Priority 65535: Implied deny ingress

Evaluation order:
1. Check custom rules (0-65534)
2. If no match, apply implied rules (65535)
```

**Best Practice:** Always create explicit allow rules for production, don't rely solely on implied rules for documentation.
