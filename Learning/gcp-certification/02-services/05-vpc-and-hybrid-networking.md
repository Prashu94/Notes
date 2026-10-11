# VPC, firewalls, hybrid, and private access

ACE 2.3, 3.5, 4.5. PCA 1.3, 2.1. The network is global. Subnets are regional. That single fact explains Shared VPC, peering limits, and why a VM in `europe-west1` can share a VPC with a VM in `us-central1`.

## Custom-mode VPC

Auto-mode VPCs create a subnet in every region from a fixed range. They collide when you peer. Production is **custom mode**. Delete the default network in new projects (organization policy can stop it being created).

```bash
gcloud compute networks create prod \
  --subnet-mode=custom \
  --bgp-routing-mode=regional

gcloud compute networks subnets create app \
  --network=prod \
  --region="$REGION" \
  --range=10.10.0.0/20 \
  --enable-private-ip-google-access

# Add a subnet later (ACE 4.5)
gcloud compute networks subnets create data \
  --network=prod --region="$REGION" --range=10.20.0.0/24

# Expand the prefix. You can grow a subnet. You cannot shrink it.
gcloud compute networks subnets expand-ip-range app \
  --region="$REGION" --prefix-length=19

gcloud compute networks list
gcloud compute networks subnets list --network=prod
```

Secondary ranges on a subnet are for GKE pod and service IPs (alias IP).

Private Google Access lets VMs with only internal IPs reach Google APIs (`*.googleapis.com`, Artifact Registry). Turn it on per subnet. It is not Cloud NAT. Cloud NAT is for the public internet (apt, external SaaS).

```bash
gcloud compute routers create nat-rtr --network=prod --region="$REGION"
gcloud compute routers nats create nat-1 \
  --router=nat-rtr --region="$REGION" \
  --auto-allocate-nat-external-ips \
  --nat-all-subnet-ip-ranges
```

## IP addresses

```bash
# Regional external (VM or regional LB)
gcloud compute addresses create vm-ip --region="$REGION"

# Regional internal
gcloud compute addresses create app-ip --region="$REGION" \
  --subnet=app --purpose=GCE_ENDPOINT

# Global external (global load balancer)
gcloud compute addresses create lb-ip --global

gcloud compute addresses list
gcloud compute instances delete-access-config web-1 --zone="$ZONE" --access-config-name=external-nat
gcloud compute instances add-access-config web-1 --zone="$ZONE" --address=vm-ip
```

## Firewalls and Cloud NGFW

VPC firewall rules are **stateful**. A rule has direction (ingress or egress), allow or deny, priority (lower number wins), and a target.

Targets and sources:

- IP ranges (`--source-ranges`, `--destination-ranges`)
- Network tags (`--target-tags`, `--source-tags`)
- Service accounts (`--target-service-accounts`, `--source-service-accounts`) — preferred, because tags are just strings a project editor can set

Implied rules: deny all ingress, allow all egress. Both are overridable. IAP’s SSH range is `35.235.240.0/20`. Health checks come from Google ranges you must allow if you use network load balancers.

```bash
# Allow HTTP only from the load balancer / health check ranges, to VMs tagged web
gcloud compute firewall-rules create allow-hc \
  --network=prod --direction=INGRESS --action=ALLOW \
  --rules=tcp:80,tcp:443 \
  --source-ranges=130.211.0.0/22,35.191.0.0/16 \
  --target-tags=web

# SSH only through IAP, to a service account
gcloud compute firewall-rules create allow-iap-ssh \
  --network=prod --direction=INGRESS --action=ALLOW \
  --rules=tcp:22 \
  --source-ranges=35.235.240.0/20 \
  --target-service-accounts="$SA_EMAIL"

# Egress deny to the internet for a tier, while still allowing Private Google Access paths carefully
gcloud compute firewall-rules create deny-egress-internet \
  --network=prod --direction=EGRESS --action=DENY \
  --rules=all --destination-ranges=0.0.0.0/0 \
  --target-tags=locked --priority=1000
```

**Hierarchical firewall policies** attach at organization or folder. A deny there beats a project admin’s allow. PCA security stems about a central security team use these, not a wiki page.

**Cloud NGFW** adds threat detection and intrusion prevention on firewall endpoints. Pick it when the stem says IDS/IPS inside the VPC, not just allow/deny. **Cloud IDS** is the inspection product for mirrored traffic. **Firewall Insights** (Network Intelligence Center) finds shadowed rules and overly open rules.

**Secure Web Proxy** is the controlled egress proxy when you need identity-aware outbound policy. **VPC Flow Logs** are the packet metadata for forensics. They are not a firewall.

## Shared VPC

One **host project** owns the VPC. **Service projects** attach and place VMs, GKE, and Cloud Run into the host’s subnets. IAM in the service project does not let a team admin change firewalls if you do not grant them network admin on the host.

Pick Shared VPC when many teams need the same network and IP plan, with central firewall control. This is the enterprise default inside one organization.

```bash
gcloud compute shared-vpc enable HOST_PROJECT
gcloud compute shared-vpc associate-projects HOST_PROJECT --project=SERVICE_PROJECT
gcloud compute networks subnets add-iam-policy-binding app \
  --region="$REGION" --project=HOST_PROJECT \
  --member="serviceAccount:SERVICE_PROJECT_NUMBER@cloudservices.gserviceaccount.com" \
  --role="roles/compute.networkUser"
```

## VPC Network Peering

Connects two VPC networks so they route to each other’s private IPs. **Not transitive.** A peered to B and B peered to C does not let A reach C. Subnet ranges must not overlap. Peering is inside Google Cloud, not a path to a data center.

```bash
gcloud compute networks peerings create a-to-b \
  --network=prod --peer-network=OTHER_VPC \
  --peer-project=OTHER_PROJECT
# The other side must create the reverse peering.
```

## Private Service Connect and private services access

Two different “private” features. The exam uses both.

| Feature | What it does |
| --- | --- |
| Private services access | VPC peering to Google’s service producer network. Used by Cloud SQL, Memorystore, AlloyDB, Filestore so they get an IP in a reserved range. |
| Private Service Connect (PSC) | An endpoint in your VPC (or a service attachment you publish) for Google APIs or for another team’s service, without peering your whole VPC to theirs. The producer and consumer do not exchange full route tables. |

PSC is the PCA answer for “consume a partner API or a Shared VPC service without VPC peering and without public IPs”, and for “expose one service to many consumer VPCs”. It is also how you reach Google APIs with a private IP you control.

```bash
# Reserve a range and peer it for managed services (private services access)
gcloud compute addresses create google-managed \
  --global --purpose=VPC_PEERING --prefix-length=16 \
  --network=prod --addresses=10.80.0.0
gcloud services vpc-peerings connect \
  --service=servicenetworking.googleapis.com \
  --ranges=google-managed --network=prod

# PSC endpoint for a published service (consumer side)
gcloud compute addresses create psc-ip --region="$REGION" --subnet=app
gcloud compute forwarding-rules create psc-endpoint \
  --region="$REGION" --network=prod --address=psc-ip \
  --target-service-attachment=ATTACHMENT_URI \
  --load-balancing-scheme=
```

The exact PSC flags depend on whether the target is a service attachment or the Google APIs bundle. Know the concept cold. Check the flag page before a lab.

## Hybrid: VPN, Interconnect, Router, NCC

| Path | Use | SLA idea |
| --- | --- | --- |
| HA VPN | Encrypted tunnels over the internet, BGP, 99.99% when built as HA (two tunnels, two interfaces) | Default hybrid when you do not have a physical cross-connect |
| Classic VPN | Legacy. Do not design it. | |
| Dedicated Interconnect | Your own 10 or 100 Gbps circuit into Google | High volume, steady, you can meet Google at a colocation |
| Partner Interconnect | A service provider’s connection, smaller bandwidths | You cannot get to a Google point of presence yourself |
| Cross-Cloud Interconnect | Google Cloud to another cloud over a dedicated path | Multicloud private, PCA 2.1 |

Cloud Router speaks BGP. HA VPN and Interconnect both need it for dynamic routes. Static routes do not failover cleanly.

```bash
gcloud compute routers create edge --network=prod --region="$REGION" --asn=64512

gcloud compute vpn-gateways create ha-gw --network=prod --region="$REGION"
gcloud compute vpn-gateways describe ha-gw --region="$REGION"

# You then create a peer gateway, two tunnels, and BGP sessions on the router.
# A single tunnel is not the 99.99% HA VPN design.
gcloud compute vpn-tunnels list --region="$REGION"
gcloud compute routers get-status edge --region="$REGION"
```

**Network Connectivity Center** is the hub for hybrid spokes (VPN, Interconnect, and VPC spokes) so sites can talk through a hub instead of a mesh of peerings. Pick NCC when the stem is many sites or transitive hybrid connectivity. Peering will not give you transitivity.

**Google Cloud to Google Cloud** across organizations is peering, PSC, or NCC, depending on whether you need full subnet routing or one service. Do not hairpin that traffic through the internet.

## Cloud DNS

DNS zones are global. Private zones answer inside VPCs you attach. Public zones answer on the internet. Peering zones and forwarding zones handle hybrid DNS (on-prem names, or another VPC’s names).

```bash
gcloud dns managed-zones create private-example \
  --dns-name=internal.example.com. \
  --visibility=private \
  --networks=prod

gcloud dns record-sets create app.internal.example.com. \
  --zone=private-example --type=A --ttl=300 \
  --rrdatas=10.10.0.5

# Inbound server policy: on-prem can resolve Cloud DNS
# Outbound forwarding: Cloud VMs resolve on-prem names via a forwarder
gcloud dns policies create inbound \
  --networks=prod --enable-inbound-forwarding
```

Split horizon means a public zone and a private zone share a name and return different answers. That is intentional.

## Packet mirroring, flow logs, Network Intelligence Center

- VPC Flow Logs: who talked to whom. Enable on the subnet. Export to BigQuery for analysis.
- Firewall Rules Logging: which rule matched.
- Network Intelligence Center: Topology, Connectivity Tests, Performance Dashboard, Firewall Insights. Connectivity Tests are the “will this flow work” answer, better than guessing.
- Packet Mirroring: copy traffic to an IDS appliance. Used with Cloud IDS.

```bash
gcloud network-management connectivity-tests create ssh-test \
  --source-instance=projects/$PROJECT_ID/zones/$ZONE/instances/web-1 \
  --destination-instance=projects/$PROJECT_ID/zones/$ZONE/instances/db-1 \
  --destination-port=3306 --protocol=TCP
```

## Exercises

1. Two teams, one IP plan, one firewall team. Peering or Shared VPC?
2. A partner must call one internal API. You must not learn their other subnets, and they must not learn yours. Which technology?
3. On-prem to cloud, encrypted, over the internet, dynamic routing, 99.99%. What do you build?
4. A private VM cannot `apt-get` but can reach `storage.googleapis.com`. Which feature is missing?
5. Subnet `10.10.0.0/20` is full. What command, and what can you not do?

### Answers

1. Shared VPC. Peering does not centralize firewall administration the way a host project does, and it is not transitive.
2. Private Service Connect with a service attachment and a consumer endpoint.
3. HA VPN: VPN gateway with two interfaces, two tunnels, Cloud Router, BGP. Not a single classic VPN tunnel.
4. Cloud NAT. Private Google Access is already working, which is why Cloud Storage succeeds.
5. `gcloud compute networks subnets expand-ip-range` to a shorter prefix (larger range). You cannot shrink, and the new range must not overlap.
