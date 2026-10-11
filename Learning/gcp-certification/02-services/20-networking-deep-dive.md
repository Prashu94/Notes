# Networking deep dive

Read `05-vpc-and-hybrid-networking.md` and `06-load-balancing-cdn-armor.md` first. This file is routes, firewalls, the full HA VPN build, Private Service Connect, DNS, and load-balancer objects the short chapters only named.

## Routes

A VPC is born with a default route `0.0.0.0/0` whose next hop is the internet gateway. That route does not put a public IP on a VM. It lets a VM that already has outbound (a public IP or Cloud NAT) reach the internet. Delete it only when you understand that you also killed default internet egress.

| Route | How it appears |
| --- | --- |
| Subnet route | Automatic. One per subnet. You cannot override it with a lower-priority custom route in a way that hijacks the subnet’s own range. |
| Default internet | Automatic, priority 1000, next hop internet gateway |
| Peering | Automatic from the peer’s subnet routes. Not transitive. |
| Cloud Router BGP | Learned from VPN or Interconnect |
| Static custom | You create it. Next hop can be an instance, IP, VPN tunnel, or ILB |

Priority: lower number wins. If two routes tie, the more specific prefix wins. That is the whole selection story the exam uses.

```bash
gcloud compute routes create via-appliance \
  --network=prod \
  --destination-range=172.16.0.0/16 \
  --next-hop-instance=fw-1 \
  --next-hop-instance-zone="$ZONE" \
  --priority=100

gcloud compute routes list --filter="network:prod"
```

Policy routing on a VM with two NICs is inside the guest. Google’s route table picks a next hop per NIC network. Do not expect one VPC route to steer traffic that arrived on the other NIC.

## Firewall rules, field by field

A rule matches when all of these match: direction, source or destination, target, protocol and port, and it is the highest priority (lowest number) among matches. First match wins. There is no cumulative “and” across rules.

| Field | Ingress | Egress |
| --- | --- | --- |
| Source | Ranges, tags, or service accounts | Not used the same way |
| Destination | Not the selector | Ranges |
| Target | Tags or service accounts. Empty means all instances. | Tags or service accounts |
| Action | ALLOW or DENY | ALLOW or DENY |
| Priority | 0–65535. Default you set is often 1000. | Same |

Implied rules, priority 65535: deny all ingress, allow all egress. They show up in the console as implied. You cannot delete them. You override them with a higher-priority rule.

Default network also ships allow-internal, allow-ssh, allow-rdp, allow-icmp. Custom networks do not. Do not assume SSH is open.

Google health-check and IAP ranges you will reuse:

| Purpose | Range |
| --- | --- |
| Health checks | `35.191.0.0/16`, `130.211.0.0/22` |
| IAP TCP forward (SSH, RDP) | `35.235.240.0/20` |
| IAP for a different TCP port | Same range, the port you chose |

Service-account targets are better than tags because a tag is a string any instance admin can set. A service account is an identity.

Hierarchical firewall policies attach to an organization or folder. Rules can be delegated or can be forced. A deny in a policy the project cannot override beats a project allow. Use that when the stem says security owns the deny and project teams own the VPC.

```bash
gcloud compute firewall-policies create org-fw --organization="$ORG_ID"
gcloud compute firewall-policies associations create \
  --firewall-policy=org-fw --organization="$ORG_ID"
gcloud compute firewall-policies rules create 900 \
  --firewall-policy=org-fw --organization="$ORG_ID" \
  --action=deny --direction=INGRESS \
  --src-ip-ranges=0.0.0.0/0 --layer4-configs=tcp:22 \
  --enable-logging
```

Firewall Rules Logging and VPC Flow Logs answer different questions. Rules logging says which rule matched. Flow logs say who talked to whom, bytes, and whether it was allowed. Flow logs are configured on the subnet and can sample. They are not a packet capture. Packet Mirroring is the copy of packets, used with Cloud IDS.

## Cloud NAT details

NAT is regional. It covers subnet ranges you list, or all of them. It does not inbound. It does not give a VM a stable public address for callbacks. A VM behind NAT that must receive internet connections needs a load balancer or a public IP, not NAT.

```bash
gcloud compute routers nats create nat-1 \
  --router=nat-rtr --region="$REGION" \
  --nat-custom-subnet-ip-ranges=app \
  --auto-allocate-nat-external-ips \
  --enable-logging --log-filter=ERRORS_ONLY
```

Manual NAT IPs when partners allow-list your egress. Auto-allocate when they do not. Timeouts matter for long database connections through NAT. The default UDP and TCP established timeouts surprise people who NAT a database. Prefer Private Service Connect or private services access so the database never uses NAT.

## HA VPN, the actual build

One tunnel is not HA. The 99.99% design is a VPN gateway with two interfaces, two tunnels, one to each peer interface, and BGP on Cloud Router. Both sides must create their half.

```bash
gcloud compute routers create edge --network=prod --region="$REGION" --asn=64512

gcloud compute vpn-gateways create ha-gw --network=prod --region="$REGION"

# Peer side is either another HA VPN gateway or an external gateway with two IPs
gcloud compute external-vpn-gateways create onprem \
  --interfaces=0=203.0.113.10,1=203.0.113.11

gcloud compute vpn-tunnels create tun-0 \
  --peer-external-gateway=onprem --peer-external-gateway-interface=0 \
  --region="$REGION" --vpn-gateway=ha-gw --interface=0 \
  --ike-version=2 --shared-secret=REPLACE --router=edge

gcloud compute vpn-tunnels create tun-1 \
  --peer-external-gateway=onprem --peer-external-gateway-interface=1 \
  --region="$REGION" --vpn-gateway=ha-gw --interface=1 \
  --ike-version=2 --shared-secret=REPLACE --router=edge

gcloud compute routers add-interface edge \
  --interface-name=if-0 --vpn-tunnel=tun-0 --region="$REGION"
gcloud compute routers add-bgp-peer edge \
  --peer-name=peer-0 --interface=if-0 --peer-asn=64513 \
  --region="$REGION"

gcloud compute routers get-status edge --region="$REGION"
```

Add the second BGP peer the same way on `tun-1`. If BGP is down, the tunnel can be up and still pass no routes. `get-status` is the command that shows sessions.

Classic VPN is a single gateway resource. Do not design it. It exists in old diagrams.

## Interconnect

You do not create a 100 Gbps circuit with one `gcloud` line from a laptop. The exam wants the choice and the objects:

| Object | Role |
| --- | --- |
| Dedicated Interconnect connection | Your cross-connect into Google, 10 or 100 Gbps |
| Partner Interconnect | A provider’s attachment, smaller sizes allowed |
| VLAN attachment | A VLAN that lands on a Cloud Router in a region |
| Cloud Router BGP | Same dynamic routing as VPN |

Redundancy is two attachments in different edge availability domains, or two metros, depending on the SLA you are buying. A single attachment is a single failure. HA VPN as a backup to Interconnect is a normal design when the internet path is acceptable as the degraded mode.

Cross-Cloud Interconnect is the same idea toward another cloud’s edge, so traffic between clouds does not hairpin the public internet.

## Shared VPC roles

| Role | Who | Can |
| --- | --- | --- |
| `compute.xpnAdmin` | Network org admin | Enable Shared VPC, associate service projects |
| `compute.networkAdmin` | On the host | Change routes, peerings, subnets |
| `compute.securityAdmin` | On the host | Firewalls |
| `compute.networkUser` | Service project admins, on a subnet | Use that subnet when creating VMs, and the Google APIs service account needs it too |

A service project admin who is Owner of the service project still cannot create a subnet in the host. That is the control. If the stem says developers keep opening firewalls, move firewall administration to the host and stop granting `securityAdmin` in the service project. Service projects do not own the VPC firewalls.

```bash
gcloud compute shared-vpc enable "$HOST_PROJECT"
gcloud compute shared-vpc associate-projects "$HOST_PROJECT" \
  --project="$SERVICE_PROJECT"

# The Google APIs service agent of the service project must use the subnet
NUM=$(gcloud projects describe "$SERVICE_PROJECT" --format='value(projectNumber)')
gcloud compute networks subnets add-iam-policy-binding app \
  --project="$HOST_PROJECT" --region="$REGION" \
  --member="serviceAccount:${NUM}@cloudservices.gserviceaccount.com" \
  --role="roles/compute.networkUser"
```

## Private Service Connect versus private services access

Private services access is one peering to `servicenetworking.googleapis.com` for a reserved CIDR. Cloud SQL, AlloyDB, Memorystore, and Filestore use it. You do it once per VPC. Overlapping ranges across many VPCs that all peer to producers become your IP-planning problem.

Private Service Connect is an endpoint (a forwarding rule) in your subnet that targets a service attachment, or a producer attachment you publish. Routes of the other VPC are not imported. That is why it is the answer for a partner API.

PSC also publishes Google APIs on an internal IP you choose, so private clients call `storage` without Private Google Access’s default path. Both can be valid. PSC for Google APIs is the answer when you need a controlled IP and a firewall story around that IP.

```bash
# Producer: a service attachment in front of an internal load balancer
# (the ILB must already exist)
gcloud compute service-attachments create inventory-api \
  --region="$REGION" \
  --producer-forwarding-rule=ilb-fr \
  --nat-subnets=psc-nat \
  --connection-preference=ACCEPT_AUTOMATIC

# Consumer, possibly another project
gcloud compute addresses create inventory-ip --region="$REGION" --subnet=app
gcloud compute forwarding-rules create inventory-psc \
  --region="$REGION" \
  --network=prod \
  --address=inventory-ip \
  --target-service-attachment=projects/PROD/regions/$REGION/serviceAttachments/inventory-api
```

The NAT subnet on the producer is not the consumer’s subnet. It is how the producer sources connections. Forgetting it is the usual failed lab.

## Cloud DNS beyond one A record

| Zone type | Answers for | Stem |
| --- | --- | --- |
| Public | The internet | The website name |
| Private | Attached VPCs | `db.internal` |
| Peering | Forwards a private zone’s queries to another VPC’s DNS | Another team owns the names |
| Forwarding | Forwards to on-prem resolvers you list | Names that live in the data center |
| Inbound server policy | Publishes an inbound forwarder IP | On-prem resolves Google Cloud names |
| DNS peering is not VPC peering | Name resolution only | Do not expect routes from a DNS peering |

```bash
gcloud dns policies create inbound-policy \
  --networks=prod --enable-inbound-forwarding

gcloud dns managed-zones create onprem \
  --dns-name=corp.example.com. \
  --visibility=private --networks=prod \
  --forwarding-targets=10.1.0.53
```

Split horizon: a public zone and a private zone with the same DNS name. VMs see the private answers. The internet sees the public answers. That is how `api.example.com` is an internal ILB for VMs and a public load balancer for customers. Do not put the private IP in the public zone.

## Load balancer objects, in order

Global external Application Load Balancer:

1. Health check (not used the same way for serverless NEGs).
2. Backend service (protocol HTTP or HTTPS, EXTERNAL_MANAGED) or a backend bucket for Cloud Storage.
3. Backends: instance group, zonal NEG, hybrid NEG, or serverless NEG.
4. URL map (host and path).
5. Target proxy (HTTP or HTTPS). HTTPS needs a certificate.
6. Global forwarding rule and a global address. Premium tier.
7. Optional: Cloud Armor policy on the backend service. Cloud CDN on the backend service or backend bucket.

Serverless NEG:

```bash
gcloud compute network-endpoint-groups create run-neg \
  --region="$REGION" --network-endpoint-type=serverless \
  --cloud-run-service=api

gcloud compute backend-services add-backend web-bes \
  --global --network-endpoint-group=run-neg --network-endpoint-group-region="$REGION"
```

Internal Application Load Balancer is regional, scheme `INTERNAL_MANAGED`, with a proxy-only subnet in the region. Forgetting the proxy-only subnet is the usual failure. Envoy proxies live there. Your backends do not.

Passthrough Network Load Balancer uses a backend service with scheme `EXTERNAL` and a forwarding rule that lists ports, or all ports. There is no URL map and no Armor. The health check is still required. Session affinity can be client IP.

## CDN cache keys

Default cache keys include host and path. If you also include cookies or headers, you fragment the cache and the hit ratio collapses. Do not cache `Authorization` responses. Set a short TTL on HTML and a long TTL on hashed static files. Invalidation is for emergencies, not for every deploy. A hashed filename does not need invalidation.

## Exercises

1. BGP session is Established on only one of two tunnels. Is the VPN highly available?
2. A project Owner in a service project cannot create a firewall rule on the Shared VPC. Is that a bug?
3. Cloud SQL has a private IP. You also created Cloud NAT. Does the database use the NAT to accept app connections from a VM in the same VPC?
4. Two routes to `10.0.0.0/8`: priority 900 via a VPN, priority 1000 via peering. Which wins?
5. You published a service attachment and the consumer endpoint stays pending. Name the producer object people forget.

### Answers

1. No. HA needs both tunnels and both BGP sessions. One session is a single path.
2. No. Firewalls live in the host project. Owner of the service project does not include them unless you granted a network role on the host.
3. No. VM to private Cloud SQL is internal routing through private services access. NAT is for traffic the VM sends to the public internet.
4. Priority 900. Lower number wins. Specificity would matter only if the prefixes differed.
5. The PSC NAT subnet on the service attachment, and the consumer must be allowed if the attachment is not ACCEPT_AUTOMATIC.
