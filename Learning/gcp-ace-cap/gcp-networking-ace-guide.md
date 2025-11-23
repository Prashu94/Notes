# Google Cloud Networking Guide for ACE Certification

This guide covers the essential networking concepts and operational tasks required for the **Associate Cloud Engineer (ACE)** exam. It focuses on VPCs, subnets, firewalls, routes, and connectivity.

## 1. Virtual Private Cloud (VPC)

A VPC is a global virtual network that spans all Google Cloud regions. It is logically isolated from other virtual networks.

### 1.1 VPC Modes
*   **Auto Mode**:
    *   Automatically creates one subnet in *every* region.
    *   Uses a predefined IP range (`10.128.0.0/9`).
    *   **Pros**: Easy to set up.
    *   **Cons**: Can't overlap with on-prem ranges; inflexible IP addressing.
    *   **Use Case**: Proof of concepts, simple standalone projects.
*   **Custom Mode**:
    *   No subnets created automatically.
    *   You define subnets and IP ranges explicitly.
    *   **Pros**: Full control over IP space; avoids overlap with on-prem.
    *   **Cons**: More manual setup.
    *   **Use Case**: Production environments, hybrid clouds.

### 1.2 Creating VPCs and Subnets

**Create a Custom VPC:**
```bash
gcloud compute networks create my-custom-vpc \
    --subnet-mode=custom \
    --bgp-routing-mode=regional  # or global
```

**Create a Subnet:**
```bash
gcloud compute networks subnets create my-subnet-us-east1 \
    --network=my-custom-vpc \
    --region=us-east1 \
    --range=10.0.1.0/24 \
    --enable-private-ip-google-access
```

**Expand a Subnet:**
*   You can expand a subnet's primary IP range without downtime.
*   You *cannot* shrink a subnet.
```bash
gcloud compute networks subnets expand-ip-range my-subnet-us-east1 \
    --region=us-east1 \
    --prefix-length=20
```

## 2. Firewall Rules

Firewall rules control traffic to and from VM instances. They are stateful (return traffic is automatically allowed).

### 2.1 Key Concepts
*   **Direction**: `INGRESS` (incoming) or `EGRESS` (outgoing).
*   **Action**: `ALLOW` or `DENY`.
*   **Priority**: Integer from `0` to `65535`. Lower number = higher priority. Default is `1000`.
*   **Targets**:
    *   **All instances in the network**.
    *   **Target Tags**: Applies to VMs with specific network tags.
    *   **Service Accounts**: Applies to VMs running as a specific service account (more secure than tags).
*   **Implied Rules**:
    *   **Deny All Ingress**: Blocks all incoming traffic by default (lowest priority).
    *   **Allow All Egress**: Allows all outgoing traffic by default (lowest priority).

### 2.2 Creating Firewall Rules

**Allow SSH (Port 22) from specific IPs:**
```bash
gcloud compute firewall-rules create allow-ssh-ingress \
    --network=my-custom-vpc \
    --action=ALLOW \
    --direction=INGRESS \
    --rules=tcp:22 \
    --source-ranges=203.0.113.0/24 \
    --target-tags=ssh-enabled
```

**Deny Egress to a specific IP:**
```bash
gcloud compute firewall-rules create deny-bad-ip-egress \
    --network=my-custom-vpc \
    --action=DENY \
    --direction=EGRESS \
    --rules=all \
    --destination-ranges=1.2.3.4/32
```

## 3. Routes

Routes define how traffic leaves a VM.

### 3.1 Route Types
*   **System-Generated**:
    *   **Default Route**: `0.0.0.0/0` -> Default Internet Gateway.
    *   **Subnet Routes**: Created automatically for each subnet range.
*   **Custom Routes**:
    *   **Static Routes**: Manually defined (e.g., route traffic to a VPN gateway or a NAT instance).
    *   **Dynamic Routes**: Learned via Cloud Router (BGP) from VPN or Interconnect.

### 3.2 Creating a Static Route
Route traffic destined for `192.168.0.0/16` through a specific VPN gateway instance.

```bash
gcloud compute routes create route-to-on-prem \
    --network=my-custom-vpc \
    --destination-range=192.168.0.0/16 \
    --next-hop-instance=vpn-gateway-vm \
    --next-hop-instance-zone=us-east1-b
```

## 4. VPC Peering

Connects two VPC networks so that resources can communicate using internal IP addresses.

*   **Non-Transitive**: If A peers with B, and B peers with C, A *cannot* talk to C.
*   **No Overlapping IPs**: Subnet ranges must not overlap.
*   **Route Exchange**: You can choose to export/import custom routes.

**Create Peering (Side A):**
```bash
gcloud compute networks peer create peer-to-vpc-b \
    --network=vpc-a \
    --peer-network=vpc-b
```

**Create Peering (Side B):**
*   Peering must be established from *both* sides to be active.
```bash
gcloud compute networks peer create peer-to-vpc-a \
    --network=vpc-b \
    --peer-network=vpc-a
```

## 5. Shared VPC

Allows multiple projects (Service Projects) to share a common VPC network defined in a central project (Host Project).

*   **Host Project**: Owns the VPC network, subnets, firewall rules, and routes.
*   **Service Project**: Attaches to the Host Project. Can use shared subnets to create VMs.
*   **Roles**:
    *   **Shared VPC Admin**: Enables Shared VPC, attaches projects.
    *   **Service Project Admin**: Creates resources (VMs) in the shared subnets.

**Enable Host Project:**
```bash
gcloud compute shared-vpc enable my-host-project
```

**Attach Service Project:**
```bash
gcloud compute shared-vpc associated-projects add my-service-project \
    --host-project=my-host-project
```

## 6. Private Google Access

Allows VMs with **only internal IP addresses** (no external IP) to reach Google APIs (like Cloud Storage, BigQuery) and services.

*   **Enabled per Subnet**.
*   Traffic stays within Google's network.
*   Requires a route to `0.0.0.0/0` (default internet gateway) but *does not* require the VM to have an external IP.

**Enable on Subnet:**
```bash
gcloud compute networks subnets update my-subnet \
    --region=us-east1 \
    --enable-private-ip-google-access
```

## 7. Cloud NAT

Provides internet access to VMs without external IP addresses.

*   **Outbound only**: Allows VMs to initiate connections to the internet.
*   **No Inbound**: Does not allow the internet to initiate connections to VMs.
*   **Regional**: A Cloud NAT gateway serves a specific region.

**Create Cloud Router (Prerequisite):**
```bash
gcloud compute routers create my-router \
    --network=my-custom-vpc \
    --region=us-east1
```

**Create NAT Gateway:**
```bash
gcloud compute routers nats create my-nat-config \
    --router=my-router \
    --region=us-east1 \
    --auto-allocate-nat-external-ips \
    --nat-all-subnet-ip-ranges
```
