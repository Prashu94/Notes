# GCP Associate Cloud Engineer Practice Test 03

## Exam Instructions
- **Total Questions**: 50
- **Time Limit**: 2 hours
- **Passing Score**: 70%
- **Focus**: Networking, VPC, Security, and Firewalls

---

## Questions

### Question 1
You need to create a custom VPC network with two subnets in different regions. Which subnet mode should you use?

**A)** Auto mode
**B)** Custom mode
**C)** Default mode
**D)** Legacy mode

**Answer**: B

---

### Question 2
Your application requires a firewall rule that denies traffic to a specific destination IP. What priority should you assign (assuming default allow rules exist)?

**A)** 65535 (lowest priority)
**B)** 0 (highest priority)
**C)** Lower number than allow rules (e.g., 900)
**D)** Same as allow rules

**Answer**: C

---

### Question 3
You need to ensure developers can create VMs but cannot delete them. Which roles should you assign?

**A)** roles/compute.instanceAdmin
**B)** Custom role with compute.instances.create, no delete permission
**C)** roles/compute.viewer
**D)** roles/editor

**Answer**: B

---

### Question 4
Your Cloud SQL instance needs high availability across zones. What should you enable?

**A)** Multi-region deployment
**B)** Regional (high availability) configuration
**C)** Read replicas in multiple zones
**D)** Automatic backups

**Answer**: B

---

### Question 5
You need to allow HTTP traffic (port 80) to instances tagged "web-server" from anywhere. Which firewall rule should you create?

**A)** Allow TCP:80, source 0.0.0.0/0, target tag "web-server"
**B)** Allow HTTP, source any, target all instances
**C)** Allow all traffic to web-server tag
**D)** No rule needed, HTTP is allowed by default

**Answer**: A

---

### Question 6###
Your organization prohibits service account keys for security reasons. How should GKE pods authenticate to Google APIs?

**A)** Download keys and mount as secrets
**B)** Use Workload Identity
**C)** Use default service account
**D)** Embed credentials in Pod spec

**Answer**: B

---

### Question 7
You need to connect your on-premises network to GCP with encrypted traffic over the internet. Which option should you use?

**A)** Dedicated Interconnect
**B)** Partner Interconnect
**C)** Cloud VPN
**D)** Direct Peering

**Answer**: C

---

### Question 8
Your VPC has a subnet 10.1.0.0/24. You need to add another subnet in the same region. Which range is valid?

**A)** 10.1.0.0/20 (overlaps)
**B)** 10.2.0.0/24
**C)** 192.168.1.0/24
**D)** Both B and C

**Answer**: D

---

### Question 9
You need to grant a user permission to view but not modify IAM policies. Which role should you assign?

**A)** roles/iam.securityReviewer
**B)** roles/iam.securityAdmin
**C)** roles/viewer
**D)** roles/iam.roleViewer

**Answer**: A

---

### Question 10
Your application requires end-to-end encryption including at rest and in transit. What should you implement?

**A)** HTTPS only
**B)** CMEK for at-rest, TLS for in-transit
**C)** VPN only
**D)** Default encryption

**Answer**: B

---

### Question 11
You need to share a Cloud Storage bucket with a partner company. What is the most secure method?

**A)** Make bucket public
**B)** Grant IAM roles to partner's Google accounts/groups
**C)** Share signed URLs
**D)** Create service account keys

**Answer**: B

---

### Question 12
Your firewall rules are not working as expected. How can you debug which rule is being applied?

**A)** Enable Firewall Rules Logging
**B)** Check VPC Flow Logs
**C)** Use Packet Mirroring
**D)** Review Cloud Audit Logs

**Answer**: A

---

### Question 13
You need to ensure a service account can only be used from specific IP addresses. What should you use?

**A)** Firewall rules
**B)** IAM Conditions with IP address constraints
**C)** VPC Service Controls
**D)** Organization Policy

**Answer**: B

---

### Question 14
Your Cloud SQL instance should only be accessible via private IP. What configuration is required?

**A)** Disable public IP, enable private IP with VPC peering
**B)** Use authorized networks
**C** Use Cloud SQL Proxy only
**D)** Create VPN tunnel

**Answer**: A

---

### Question 15
You need to peer two VPCs in different organizations. What permissions are required?

**A)** Compute Network Admin in both organizations
**B)** Compute Network Admin in one, permission to accept peering in other
**C)** Organization Admin
**D)** VPC peering not possible across organizations

**Answer**: B

---

### Question 16
Your application needs to verify it's running on a legitimate Google Cloud VM. What should you check?

**A)** Instance metadata server signature
**B)** Serial number
**C)** IP address
**D)** Hostname

**Answer**: A

---

### Question 17
You need to deny all traffic to 0.0.0.0/0 except Google APIs. Which firewall rules should you create?

**A)** Single deny rule to 0.0.0.0/0
**B)** Allow rule to Google API ranges (priority 1000), deny 0.0.0.0/0 (priority 2000)
**C)** No rules needed
**D)** Block specific IPs only

**Answer**: B

---

### Question 18
Your organization requires all VM disks to be encrypted with customer-managed keys. What should you implement?

**A)** Organization Policy requiring CMEK
**B)** Manual encryption configuration
**C)** Default encryption is sufficient
**D)** Application-level encryption

**Answer**: A

---

### Question 19
You need to load balance HTTPS traffic globally with SSL termination. Which load balancer should you use?

**A)** Network Load Balancer
**B)** Internal HTTP(S) Load Balancer
**C)** External HTTP(S) Load Balancer (global)
**D)** TCP Proxy Load Balancer

**Answer**: C

---

### Question 20
Your service account needs temporary elevated permissions for a migration. What is the best practice?

**A)** Grant permanent elevated permissions
**B)** Grant temporary permissions, remove after migration
**C)** Create new service account
**D)** Use personal account instead

**Answer**: B

---

### Question 21
You need to resolve custom DNS names within your VPC. What should you create?

**A)** Cloud DNS private zone
**B)** External DNS server
**C)** /etc/hosts on each VM
**D)** Public Cloud DNS zone

**Answer**: A

---

### Question 22
Your Cloud Storage bucket should only be accessible from within your VPC. What should you use?

**A)** Firewall rules
**B)** VPC Service Controls perimeter
**C)** IAM conditions
**D)** Signed URLs only

**Answer**: B

---

### Question 23
You need to monitor all Cloud SQL connection attempts including denied ones. What should you enable?

**A)** Cloud Audit Logs - Data Access
**B)** Cloud SQL flags
**C)** VPC Flow Logs
**D)** Cloud Monitoring alerts

**Answer**: A

---

### Question 24
Your application requires a static internal IP address that persists even if you recreate the VM. What should you configure?

**A)** Ephemeral internal IP
**B)** Reserve static internal IP address and assign to VM
**C)** External IP address
**D)** Automatic IP assignment

**Answer**: B

---

### Question 25
You need to allow Cloud Functions to access a private Cloud SQL instance. What should you configure?

**A)** Serverless VPC Access connector
**B)** Public IP on Cloud SQL
**C)** VPN connection
**D)** Cloud Functions cannot access private SQL

**Answer**: A

---

### Question 26
Your organization requires role separation. Who should be able to grant IAM roles?

**A)** Anyone with Editor role
**B)** Only users with Security Admin or Owner roles
**C)** Project creators
**D)** All project members

**Answer**: B

---

### Question 27
You need to ensure two GKE clusters in different regions can communicate privately. What should you configure?

**A)** VPC Peering if clusters are in different VPCs
**B)** Same VPC for both clusters
**C)** Public IPs
**D)** Cloud VPN

**Answer**: B

---

### Question 28
Your firewall rule allows TCP:22 from source tag "bastion". What does this mean?

**A)** Traffic from instances with tag "bastion"
**B)** Traffic to instances with tag "bastion"
**C)** Traffic from IP addresses tagged bastion
**D)** Invalid configuration

**Answer**: A

---

### Question 29
You need to audit all permission changes across your organization. What should you enable?

**A)** Cloud Audit Logs - Admin Activity (enabled by default)
**B)** Cloud Audit Logs - Data Access
**C)** Cloud Monitoring alerts
**D)** Custom logging

**Answer**: A

---

### Question 30
Your application uses a service account but you don't know which resources it accesses. How can you find out?

**A)** Service Account Insights
**B)** Cloud Audit Logs
**C)** IAM Policy Analyzer
**D)** All of the above

**Answer**: D

---

### Question 31
You need to create a load balancer that preserves client source IP addresses. Which type should you use?

**A)** HTTP(S) Load Balancer
**B)** Network Load Balancer (passthrough)
**C)** Internal TCP/UDP Load Balancer
**D)** SSL Proxy

**Answer**: B

---

### Question 32
Your VPC spans multiple regions. Subnets in us-central1 need to communicate with europe-west1. What configuration is needed?

**A)** VPC Peering
**B)** No configuration needed, subnets in same VPC can communicate
**C)** Cloud VPN
**D)** Firewall rules allowing cross-region traffic

**Answer**: B

---

### Question 33
You need to prevent data exfiltration from your VPC to the internet. What should you implement?

**A)** Deny all egress firewall rules
**B)** VPC Service Controls and egress controls
**C)** Remove all external IPs
**D)** Cloud NAT only

**Answer**: B

---

### Question 34
Your application requires bidirectional firewall rules (ingress and egress). How many rules do you need?

**A)** 1 rule (bidirectional)
**B)** 2 rules (one ingress, one egress)
**C)** Firewall rules are automatically bidirectional
**D)** 4 rules for redundancy

**Answer**: B

---

### Question 35
You need to grant a developer access to create VMs but only in us-central1. How can you enforce this?

**A)** IAM conditions with resource.location constraint
**B)** Organization Policy constraint
**C)** Firewall rules
**D)** VPC configuration

**Answer**: A

---

### Question 36
Your Cloud SQL instance is using public IP. You want to restrict access to specific client IPs. What should you configure?

**A)** Authorized networks
**B)** Firewall rules (Cloud SQL is not controlled by VPC firewalls)
**C)** VPC peering
**D)** Cloud Armor

**Answer**: A

---

### Question 37
You need to inspect all traffic entering your VPC for threats. What GCP service should you use?

**A)** Cloud Armor
**B)** Cloud IDS (Intrusion Detection System)
**C)** Firewall rules
**D)** VPC Flow Logs

**Answer**: B

---

### Question 38
Your organization requires MFA for all privileged operations. What should you enable?

**A)** 2-Step Verification for all users
**B)** Context-Aware Access policies
**C)** IAM conditions
**D)** All of the above for comprehensive security

**Answer**: D

---

### Question 39
You need to route traffic from your VPC to on-premises based on destination IP. What should you configure?

**A)** Static routes or Cloud Router for dynamic routing
**B)** Firewall rules
**C)** Load balancer
**D)** VPC peering

**Answer**: A

---

### Question 40
Your application logs sensitive data. You need to ensure logs are encrypted and access is audited. What should you implement?

**A)** Default logging is sufficient
**B)** CMEK for logs, enable Data Access audit logs for Cloud Logging
**C)** Disable logging
**D)** Application-level encryption only

**Answer**: B

---

### Question 41
You need to test firewall rules without affecting production traffic. What should you use?

**A)** Firewall Insights
**B)** Create test VPC
**C)** Logging-only mode
**D)** VPC Flow Logs

**Answer**: A

---

### Question 42
Your VPN tunnel keeps going down. Where should you check for issues?

**A)** Cloud Logging for VPN logs
**B)** VPN tunnel status in console
**C)** Cloud Monitoring metrics
**D)** All of the above

**Answer**: D

---

### Question 43
You need to implement network segmentation for different application tiers. What architecture should you use?

**A)** Single VPC with multiple subnets
**B)** Multiple VPCs with VPC peering
**C)** Shared VPC
**D)** Any of the above depending on requirements

**Answer**: D

---

### Question 44
Your application requires end-to-end private connectivity to Google APIs without internet exposure. What should you enable?

**A)** Private Google Access
**B)** Cloud NAT
**C)** VPN tunnel
**D)** Public IPs with firewall rules

**Answer**: A

---

### Question 45
You need to grant temporary access to a resource for 2 hours. What IAM feature should you use?

**A)** Temporary account
**B)** IAM conditions with time-based constraints
**C)** Grant and manually revoked
**D)** Service account key with expiration

**Answer**: B

---

### Question 46
Your load balancer needs to route traffic based on URL path (/api to API servers, / to web servers). Which type should you use?

**A)** Network Load Balancer
**B)** HTTP(S) Load Balancer with URL maps
**C)** TCP Proxy
**D)** Internal Load Balancer

**Answer**: B

---

### Question 47
You need to ensure Cloud Run services can only be invoked by authenticated users. What should you configure?

**A)** Allow unauthenticated invocations
**B)** Require authentication, grant invoker role to specific principals
**C)** API Gateway
**D)** Cloud Armor

**Answer**: B

---

### Question 48
Your VPC needs to reject connections from known malicious IPs. What is the most scalable solution?

**A)** Manual firewall deny rules
**B)** Cloud Armor security policies
**C)** Reject at application level
**D)** VPN filtering

**Answer**: B

---

### Question 49
You need to monitor unauthorized access attempts to Cloud Storage resources. What should you enable?

**A)** Cloud Audit Logs - Data Access logs
**B)** Access Transparency logs
**C)** Cloud Monitoring metrics
**D)** Bucket logging

**Answer**: A

---

### Question 50
Your organization has a zero-trust security model. Which GCP product helps implement this?

**A)** VPC Service Controls
**B)** BeyondCorp Enterprise
**C)** Identity-Aware Proxy (IAP)
**D)** All of the above

**Answer**: D

---

## Answer Key

| Q# | Answer | Q# | Answer | Q# | Answer | Q# | Answer | Q# | Answer |
|----|--------|----|----|----|----|----|----|----|----|
| 1  | B | 11 | B | 21 | A | 31 | B | 41 | A |
| 2  | C | 12 | A | 22 | B | 32 | B | 42 | D |
| 3  | B | 13 | B | 23 | A | 33 | B | 43 | D |
| 4  | B | 14 | A | 24 | B | 34 | B | 44 | A |
| 5  | A | 15 | B | 25 | A | 35 | A | 45 | B |
| 6  | B | 16 | A | 26 | B | 36 | A | 46 | B |
| 7  | C | 17 | B | 27 | B | 37 | B | 47 | B |
| 8  | D | 18 | A | 28 | A | 38 | D | 48 | B |
| 9  | A | 19 | C | 29 | A | 39 | A | 49 | A |
| 10 | B | 20 | B | 30 | D | 40 | B | 50 | D |

**Score: ___/50**

---

## Topic Distribution
- **VPC Networking**: 15 questions
- **Security & IAM**: 20 questions
- **Firewalls**: 10 questions
- **Cloud SQL**: 3 questions
- **Load Balancing**: 2 questions

**Test completed on**: __________
**Time taken**: __________ minutes
