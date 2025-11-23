# Google Cloud DNS — ACE + Professional Cloud Architect Guide

This guide gives you the depth and practical patterns you need for Google Cloud DNS on the Associate Cloud Engineer (ACE) and Professional Cloud Architect (PCA) exams. It blends fundamentals, hands-on commands, design trade-offs, hybrid connectivity patterns, security, operations, and exam-style scenarios.


## 1) What Cloud DNS is (and isn’t)

- Cloud DNS is Google Cloud’s scalable, managed, authoritative DNS service.
- It hosts DNS zones (public and private) and records (A/AAAA, CNAME, TXT, MX, SRV, PTR, NS, SOA, etc.).
- It’s not a recursive cache you manage directly; VMs and GKE use Google’s built-in resolver which can query Cloud DNS. For hybrid, use Cloud DNS policies with inbound/outbound endpoints.
- Key sub-features:
  - Public zones: Internet-facing authoritative DNS for your domains.
  - Private zones: VPC-scoped authoritative DNS used by workloads inside one or more VPCs.
  - Peering zones: Resolve private zones across VPC network peering without duplicating zones.
  - Forwarding zones: Forward queries for specific domains to on-prem or third-party name servers.
  - DNS policies and resolver endpoints: Inbound/outbound endpoints, logging, and response policies for VPCs.


## 2) Core building blocks and terminology

- Managed zone: A container for DNS records for a domain suffix (example.com., corp.local.).
  - Public zone: Visible on the Internet (delegate NS at the registrar).
  - Private zone: Visible only inside attached VPC networks (can attach multiple VPCs across projects).
  - Forwarding zone: Forwards queries for a domain to target name servers (commonly on-prem).
  - Peering zone: Allows a “consumer” VPC to resolve records from a private zone in a “producer” VPC over VPC Network Peering.
- Record sets: DNS records within a zone. Specify name, type, TTL, and data.
- DNS policy:
  - Attach to one or more VPCs to control query behavior (e.g., enable inbound/outbound forwarding, enable logging, set alternative name servers, define response policies).
  - Inbound endpoint: Lets on-prem/other networks send queries into a VPC’s Cloud DNS over hybrid connectivity.
  - Outbound endpoint: Lets a VPC forward unresolved queries to on-prem name servers.
- Split-horizon DNS: Same domain name with different answers depending on client location (e.g., public vs private zone with same apex).


## 3) Resolution order and name matching inside a VPC

Within a VPC, Google’s resolver follows these rules (memorize for exams):

- Longest suffix match wins (most specific domain suffix takes precedence).
- Priority order for resolutions typically follows:
  1) Cache (client or resolver)
  2) Private zones attached to the VPC (most-specific suffix first)
  3) Peering zones (from peered VPCs)
  4) Forwarding zones
  5) Google Public DNS (public Internet)
- Split-horizon: If both a public and a private zone exist for the same name, VPC-internal clients resolve using the private zone; external clients see the public zone.


## 4) When to use which zone type

- Public zone
  - Host Internet-facing services; delegate NS at the domain registrar.
  - Pair with Global external HTTP(S) Load Balancer and managed SSL/TLS.
- Private zone
  - Name resolution for internal microservices, VMs, GKE, and PSC endpoints.
  - Attach to multiple VPCs (same project or cross-project) for shared services.
- Peering zone
  - Consumer VPC resolves records in a producer VPC’s private zone over VPC peering.
  - No record duplication; producer retains control.
- Forwarding zone
  - VPC forwards queries for specific suffixes to on-prem/3rd-party DNS (e.g., corp.example.com.).
  - Use for hybrid split-horizon, Active Directory domains, or Azure/AWS private zones.


## 5) Hybrid connectivity patterns (ACE + PCA favorite)

- Site-to-site Cloud VPN or Cloud Interconnect provides IP reachability for DNS traffic (UDP/TCP 53) between on-prem and VPCs.
- Inbound endpoints (DNS policy) let on-prem resolvers query into Cloud DNS for private zones via VPN/Interconnect.
- Outbound endpoints (DNS policy) let VPC-resident resolvers forward to on-prem DNS for corporate zones.
- Common designs:
  - Hub-and-spoke: Central VPC hosts private zones. Spokes resolve via peering zones. On-prem queries ingress via inbound endpoint in hub.
  - Bi-directional hybrid: Outbound endpoint in VPC forwards corp.local to on-prem; inbound endpoint allows on-prem to resolve private.cloud.
  - Multi-cloud: Forwarding zones between GCP and AWS Route 53 Private Hosted Zones or Azure Private DNS.


## 6) Private Google Access and restricted Google APIs DNS

- Private Google Access (PGA) for on-prem and VPC uses special DNS names to route Google APIs over private IP paths:
  - private.googleapis.com → 199.36.153.4/30
  - restricted.googleapis.com → 199.36.153.8/30 (egress-restricted services)
- Implement via private zone or DNS policy/response policy to map these names to the correct VIPs; ensure routes and firewall rules allow traffic.
- For PCA scenarios, justify restricted.googleapis.com when you must block consumer Google APIs while allowing required enterprise APIs.


## 7) Security and IAM

- IAM roles (common):
  - roles/dns.admin — Full admin for Cloud DNS resources in a project.
  - roles/dns.reader — Read-only access to Cloud DNS resources.
  - Use principle of least privilege; consider per-environment projects (dev/stage/prod).
- DNSSEC (public zones):
  - Cloud DNS can sign zones; publish DS at your registrar to enable validation by resolvers.
  - Protects against spoofing; understand KSK/ZSK rotation basics for PCA.
- Network security:
  - Allow UDP/TCP 53 between on-prem resolvers and Cloud DNS inbound endpoints over VPN/Interconnect.
  - Use Cloud Logging to audit DNS queries; consider sampling and retention policies.
- Response policies:
  - Override/blackhole malicious domains or direct specific names to internal sinks.


## 8) Logging, monitoring, and SRE operations

- DNS query logging via DNS policies (per VPC). Choose sampling rate to control cost.
- Cloud Monitoring metrics: query counts, response codes, latency. Create SLOs for resolution success and P95 latency.
- Incident playbook:
  - Validate VPC attachment and zone visibility.
  - Check suffix specificity and conflicts.
  - Review forwarding targets reachability and firewall rules.
  - Use dig/nslookup from VM in target VPC and from on-prem resolver.


## 9) Quotas and limits (watch for exam traps)

- Categories to know:
  - Managed zones per project
  - Record sets per managed zone
  - Requests per second (QPS) per project/zone
  - Forwarding targets per forwarding zone
  - Policies per project and endpoints per policy
- Exact numbers can change; always check the latest quotas. Design for shard-by-subdomain if needed.


## 10) Pricing — what drives cost

- Managed zone monthly charge (public and private)
- Query volume (public queries billed per million; private query pricing can vary by SKU)
- Logging/Monitoring ingestion (Cloud Logging/Monitoring pricing)
- Hybrid resolver endpoints may have associated costs
- Optimization:
  - Reduce query volume with sensible TTLs and client-side caching
  - Consolidate zones where appropriate, but avoid over-large blast radius


## 11) Hands-on: gcloud examples

- Create a public managed zone

```bash
# Create public zone
gcloud dns managed-zones create public-example \
  --dns-name="example.com." \
  --description="Public zone for example.com"

# Add an A record
gcloud dns record-sets transaction start --zone=public-example

gcloud dns record-sets transaction add \
  --zone=public-example \
  --name="www.example.com." \
  --ttl=300 \
  --type=A \
  "203.0.113.10"

gcloud dns record-sets transaction execute --zone=public-example

# Retrieve NS to delegate at the registrar
gcloud dns record-sets list --zone=public-example --type=NS
```

- Create a private zone and attach to VPC

```bash
# Create private zone attached to a VPC
VPC="projects/PROJECT_ID/global/networks/MAIN_VPC"

gcloud dns managed-zones create private-corp \
  --dns-name="corp.internal." \
  --visibility=private \
  --networks="$VPC" \
  --description="Private zone for internal services"

# Add a record
gcloud dns record-sets transaction start --zone=private-corp

gcloud dns record-sets transaction add \
  --zone=private-corp \
  --name="api.corp.internal." \
  --ttl=60 \
  --type=A \
  "10.20.30.40"

gcloud dns record-sets transaction execute --zone=private-corp
```

- Create a forwarding zone to on-prem DNS

```bash
# Forwards queries for corp.example.com to on-prem DNS
# Replace with your on-prem name servers
ONPREM_DNS1="192.0.2.53"
ONPREM_DNS2="198.51.100.53"

gcloud dns managed-zones create fwd-corp-example \
  --description="Forward corp.example.com to on-prem" \
  --dns-name="corp.example.com." \
  --visibility=private \
  --forwarding-targets=$ONPREM_DNS1,$ONPREM_DNS2 \
  --networks="$VPC"
```

- Create a peering zone to resolve from a producer VPC

```bash
# Consumer VPC peers with producer; resolve private zone from producer
PRODUCER_VPC="projects/PRODUCER_PROJ/global/networks/PRODUCER_VPC"

gcloud dns managed-zones create peer-prod \
  --dns-name="svc.prod.internal." \
  --visibility=private \
  --peer-network="$PRODUCER_VPC" \
  --networks="$VPC"
```

- Enable query logging via DNS policy (example)

```bash
# Create a policy with logging enabled and attach to VPC
gcloud dns policies create vpc-dns-policy \
  --networks="$VPC" \
  --enable-logging

# Describe policy
gcloud dns policies describe vpc-dns-policy
```

- Inbound/outbound forwarding (high level)

```bash
# Inbound: allow on-prem to query Cloud DNS in this VPC
# Outbound: forward queries for non-matching names to on-prem
# Note: Commands and capabilities evolve; consult current docs for exact flags.

gcloud dns policies create hybrid-policy \
  --networks="$VPC" \
  --enable-inbound-forwarding \
  --enable-outbound-forwarding

# Then configure alternative name servers or endpoints per policy as required.
```


## 12) Terraform examples

- Public zone with records

```hcl
resource "google_dns_managed_zone" "public_example" {
  name     = "public-example"
  dns_name = "example.com."
}

resource "google_dns_record_set" "www_a" {
  name         = "www.example.com."
  type         = "A"
  ttl          = 300
  managed_zone = google_dns_managed_zone.public_example.name
  rrdatas      = ["203.0.113.10"]
}
```

- Private zone attached to a VPC

```hcl
resource "google_dns_managed_zone" "private_corp" {
  name        = "private-corp"
  dns_name    = "corp.internal."
  visibility  = "private"
  private_visibility_config {
    networks {
      network_url = google_compute_network.main.self_link
    }
  }
}
```

- Forwarding zone to on-prem

```hcl
resource "google_dns_managed_zone" "fwd_corp" {
  name       = "fwd-corp-example"
  dns_name   = "corp.example.com."
  visibility = "private"
  forwarding_config {
    target_name_servers {
      ipv4_address = "192.0.2.53"
    }
    target_name_servers {
      ipv4_address = "198.51.100.53"
    }
  }
  private_visibility_config {
    networks { network_url = google_compute_network.main.self_link }
  }
}
```

- Peering zone

```hcl
resource "google_dns_managed_zone" "peer_prod" {
  name       = "peer-prod"
  dns_name   = "svc.prod.internal."
  visibility = "private"
  peering_config {
    target_network {
      network_url = google_compute_network.producer.self_link
    }
  }
  private_visibility_config {
    networks { network_url = google_compute_network.consumer.self_link }
  }
}
```


## 13) GKE and Cloud DNS

- GKE CoreDNS/kube-dns forwards external queries to Google’s resolver which reaches Cloud DNS zones.
- NodeLocal DNSCache reduces latency and improves resiliency for pods.
- ExternalDNS controller can manage Cloud DNS records for Kubernetes Services/Ingress.
- For internal-only Services, prefer private zones; for Internet-facing Ingress with a Global external LB, use public zones.


## 14) Migrations and cutovers

- From another provider (e.g., Route 53):
  1) Export existing records; import/create them in a Cloud DNS public zone.
  2) Lower TTLs ahead of cutover (e.g., to 60s) to reduce propagation time.
  3) At cutover, update NS at the registrar to Cloud DNS NS set.
  4) Monitor; after stabilization, raise TTLs as appropriate.
- For private DNS migrations (on-prem → Cloud DNS):
  - Start with forwarding zones and test resolution.
  - Gradually replace with native private zones and deprecate on-prem hosting.


## 15) Troubleshooting checklist

- Query path:
  - dig from a VM in the target VPC: `dig +trace name.corp.internal.`
  - dig from on-prem resolver to inbound endpoint IP (ensure UDP/TCP 53 permitted).
- Visibility:
  - Confirm zone visibility and VPC attachments.
  - Check that no more-specific private zone is shadowing your records.
- Forwarding/peering:
  - Validate target name servers’ reachability; ensure routes and firewall rules exist.
  - Confirm VPC Network Peering is ACTIVE and DNS export/import is configured when needed.
- Conflicts:
  - Avoid creating the same name in multiple private zones attached to the same VPC unless intentional split-horizon is designed.
- Logging:
  - Enable DNS query logging temporarily to inspect resolution behavior.


## 16) Design best practices and patterns

- Use private zones per environment (dev/stage/prod) to isolate blast radius.
- Prefer short TTLs for rapidly changing records (failover), longer TTLs for stable entries.
- For hybrid, keep forwarding suffixes narrow to reduce on-prem dependency and latency.
- Centralize shared service discovery (e.g., `svc.shared.internal.`) and expose via peering zones.
- For compliance, enable DNSSEC on public zones and monitor DS correctness at the registrar.


## 17) Exam focus: ACE vs PCA

- ACE (Associate Cloud Engineer):
  - Create/modify public and private zones, add records, attach to VPCs.
  - Configure forwarding and peering zones for hybrid/basic multi-VPC.
  - Enable/verify logging, basic troubleshooting with gcloud and dig.
- PCA (Professional Cloud Architect):
  - Design hybrid DNS with inbound/outbound endpoints, hub-and-spoke, and multi-project multi-VPC.
  - Choose split-horizon strategies, justify DNSSEC, and logging/monitoring trade-offs.
  - Address org-level multi-tenancy (shared VPC + cross-project zone attachments).
  - Align with security requirements (restricted.googleapis.com, response policies).


## 18) Scenario-style practice (condensed)

1) You must allow on-prem clients to resolve `*.svc.prod.internal` hosted in a GCP private zone.
   - Use Cloud VPN/Interconnect + DNS policy with inbound endpoint on the prod VPC; point on-prem resolvers to inbound endpoint IPs.

2) A consumer VPC needs read-only name resolution to a producer VPC’s internal services.
   - Use a peering zone in consumer VPC targeting producer VPC. Keep records only in producer.

3) Resolve `corp.example.com` to on-prem domain controllers from GCP workloads.
   - Use a forwarding zone in your VPC to on-prem DNS servers (ensure connectivity and firewall rules).

4) Same apex `example.com` used publicly and internally with different answers.
   - Create public zone and private zone. Internal clients see private answers; Internet sees public.

5) Lock down Google API egress but allow necessary enterprise APIs.
   - Use restricted.googleapis.com mapping and firewall egress rules; document justification for PCA.


## 19) Quick FAQs

- Can I attach a private zone to multiple VPCs across projects? Yes.
- Can I use Cloud DNS across regions? Yes; Cloud DNS is global.
- Do I need to open TCP 53? Yes; for large responses and reliability, allow both UDP and TCP 53.
- Does Cloud DNS support DNSSEC? Yes, for public zones; publish DS at the registrar.
- What about geo/latency-based routing? Cloud DNS supports advanced routing policies; confirm current GA status and constraints for your exam version.


## 20) Reference checklists

- Before creating zones
  - Confirm domain suffix plan and split-horizon needs
  - Identify VPC attachments and cross-project needs
  - Define TTLs and change management

- For hybrid
  - Choose VPN vs Interconnect, confirm IP ranges, routes, firewall (UDP/TCP 53)
  - Decide inbound, outbound, or both
  - Keep forwarding scopes minimal; monitor latency and failure modes

- Security/Compliance
  - Enable query logging with appropriate sampling
  - DNSSEC for public zones; rotate keys on schedule
  - Response policies for known-bad domains


## 21) Glossary

- Authoritative DNS: Answers for domains it hosts.
- Recursive resolver: Follows referrals to find answers (Google’s internal resolver does this for VMs).
- Managed zone: Container for records for a domain suffix.
- Private/Peering/Forwarding zone: VPC-scoped DNS mechanisms for internal and hybrid resolution.
- Split-horizon DNS: Different answers depending on client network.


---

Notes:
- CLI flags and product capabilities evolve. For exam prep, focus on concepts, design choices, and typical commands; verify exact flags against current docs when implementing in production.
