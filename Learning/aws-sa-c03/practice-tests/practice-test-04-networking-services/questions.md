# AWS SAA-C03 Practice Test 4: Networking Services

**Topics Covered:** VPC, Route53, CloudFront, ELB, Direct Connect, Transit Gateway, VPN Gateway, Global Accelerator  
**Number of Questions:** 65  
**Time Limit:** 130 minutes

---

## VPC Questions (Questions 1-25)

### Question 1
A company needs to create isolated network environments for development, staging, and production. What AWS service provides this?

A) Multiple AWS accounts  
B) Amazon VPC with separate VPCs  
C) EC2 placement groups  
D) AWS Organizations

### Question 2
A web application requires instances in public subnets to access the internet while instances in private subnets should only make outbound connections. What components are needed? (Choose TWO)

A) Internet Gateway attached to VPC  
B) NAT Gateway in public subnet  
C) VPN Gateway  
D) Virtual Private Gateway  
E) Direct Connect Gateway

### Question 3
A security group allows inbound SSH (port 22) from 203.0.113.0/24. An instance cannot be accessed. What could be the issue?

A) Network ACL is blocking traffic  
B) Route table doesn't have route to Internet Gateway  
C) Instance doesn't have public IP  
D) All of the above could cause the issue

### Question 4
A company wants to connect their on-premises data center to AWS VPC over the internet with encryption. What solution should be used?

A) AWS Direct Connect  
B) Site-to-Site VPN  
C) VPC Peering  
D) Transit Gateway

### Question 5
Two VPCs in the same region need to communicate privately. What is the MOST cost-effective solution?

A) VPN connection between VPCs  
B) VPC Peering  
C) Transit Gateway  
D) Internet Gateway with encryption

### Question 6
A Network ACL has the following rules: Inbound allow HTTP (80) from 0.0.0.0/0, Deny 10.0.1.0/24. An instance at 10.0.1.50 tries to access. What happens?

A) Access allowed if allow rule has lower number  
B) Access denied if deny rule has lower number  
C) Security group overrides NACL  
D) Both rules apply, access partially allowed

### Question 7
A company needs to restrict access to S3 and DynamoDB from their VPC without internet traversal. What should be configured?

A) NAT Gateway  
B) VPC Gateway Endpoints for S3 and DynamoDB  
C) VPC Interface Endpoints  
D) Direct Connect

### Question 8
An application requires low latency communication between instances in different AZs within the same VPC. What automatically enables this?

A) VPC Peering  
B) Transit Gateway  
C) Default VPC routing  
D) Enhanced networking

### Question 9
A company wants to monitor VPC network traffic for security analysis. What service captures this information?

A) CloudWatch Logs  
B) VPC Flow Logs  
C) AWS CloudTrail  
D) AWS Config

### Question 10
A VPC has CIDR block 10.0.0.0/16. What is the maximum number of /24 subnets that can be created?

A) 16  
B) 64  
C) 256  
D) Unlimited

### Question 11
An EC2 instance in a private subnet needs to access AWS services (S3, DynamoDB) and internet. What is the MOST secure architecture?

A) Attach Internet Gateway, use public IPs  
B) Use NAT Gateway for internet, VPC endpoints for AWS services  
C) Move instance to public subnet  
D) Use VPN connection

### Question 12
A Network ACL is stateless. What does this mean?

A) Rules are evaluated in order  
B) Return traffic must be explicitly allowed  
C) Cannot use CIDR notation  
D) Only applies to specific protocols

### Question 13
A company connects 10 VPCs across multiple regions. What service simplifies this hub-and-spoke connectivity?

A) VPC Peering (10 peering connections)  
B) AWS Transit Gateway with peering  
C) Site-to-Site VPN mesh  
D) Direct Connect Gateway

### Question 14
A VPC security group allows outbound HTTPS (443) to 0.0.0.0/0. Does return traffic need explicit inbound rule?

A) Yes, security groups are stateless  
B) No, security groups are stateful  
C) Only for TCP traffic  
D) Depends on NACL configuration

### Question 15
A company needs dedicated bandwidth and consistent network performance between on-premises and AWS. What should be used?

A) Site-to-Site VPN  
B) AWS Direct Connect  
C) VPN over Direct Connect  
D) Internet with VPN

### Question 16
A VPC has default NACL. What is the default behavior?

A) Allow all inbound and outbound traffic  
B) Deny all traffic  
C) Allow outbound, deny inbound  
D) Allow inbound, deny outbound

### Question 17
An application requires multiple EC2 instances to share the same elastic network interface. Is this possible?

A) Yes, ENIs can be attached to multiple instances  
B) No, ENI can only attach to one instance at a time  
C) Yes, but only in the same AZ  
D) Yes, using placement groups

### Question 18
A company wants to advertise custom IP ranges they own in AWS. What service enables this?

A) Elastic IP addresses  
B) Bring Your Own IP (BYOIP)  
C) VPC CIDR extension  
D) Direct Connect

### Question 19
A VPC has instances in public and private subnets. What defines a public subnet?

A) Has Internet Gateway attached  
B) Has route to Internet Gateway in route table  
C) Has public IP addresses assigned  
D) Has no Network ACL restrictions

### Question 20
An application requires network isolation between tiers (web, app, database). What VPC feature provides this?

A) Multiple VPCs  
B) Subnets with security groups and NACLs  
C) Placement groups  
D) Elastic Network Interfaces

### Question 21
A company needs to route traffic from multiple VPCs through a single egress point for inspection. What architecture should be used?

A) NAT Gateway in each VPC  
B) Transit Gateway with centralized inspection VPC  
C) VPC Peering with inspection instances  
D) Multiple Internet Gateways

### Question 22
A VPC CIDR block is running out of IP addresses. What can be done?

A) Modify existing CIDR block  
B) Add secondary CIDR blocks (up to 5)  
C) Recreate VPC with larger CIDR  
D) Use elastic network interfaces

### Question 23
An EC2 instance needs a fixed private IP address that persists across restarts. How should this be configured?

A) Allocate Elastic IP  
B) Assign static private IP in subnet range  
C) Use Elastic Network Interface with static IP  
D) Both B and C work

### Question 24
A company wants to prevent traffic between certain subnets in the same VPC. What is the BEST approach?

A) Use security groups  
B) Use Network ACLs with deny rules  
C) Use separate VPCs  
D) Use route table restrictions

### Question 25
An application uses UDP protocol. Can security groups filter UDP traffic?

A) No, only TCP supported  
B) Yes, security groups support TCP, UDP, and ICMP  
C) Only with custom rules  
D) Only outbound UDP

---

## Route53, CloudFront, ELB Questions (Questions 26-50)

### Question 26
A company needs to route traffic to multiple regions based on geographic location. What Route53 routing policy should be used?

A) Simple routing  
B) Geolocation routing  
C) Latency-based routing  
D) Weighted routing

### Question 27
A web application requires automatic DNS failover to standby region if primary fails. What Route53 feature enables this?

A) Weighted routing  
B) Failover routing with health checks  
C) Multivalue answer routing  
D) Simple routing

### Question 28
A static website on S3 needs global content delivery with custom domain and HTTPS. What combination is needed?

A) S3 static hosting with Route53  
B) CloudFront with S3 origin, ACM certificate, Route53  
C) S3 with load balancer  
D) EC2 with web server

### Question 29
An Application Load Balancer should distribute traffic to EC2 instances based on URL path (/api → API servers, /web → Web servers). What feature enables this?

A) Listener rules with path-based routing  
B) Target group attributes  
C) Security group rules  
D) Route53 routing policy

### Question 30
A company needs to distribute traffic across multiple target groups with 70% to new version and 30% to old version. What ALB feature enables this?

A) Path-based routing  
B) Host-based routing  
C) Weighted target groups  
D) Sticky sessions

### Question 31
A CloudFront distribution serves content from S3. Users report stale content. What should be done?

A) Increase CloudFront TTL  
B) Create CloudFront invalidation  
C) Delete and recreate distribution  
D) Disable caching

### Question 32
A Route53 hosted zone is authoritative for example.com. What does authoritative mean?

A) Route53 owns the domain  
B) Route53 has definitive DNS records for the domain  
C) Route53 automatically renews domain  
D) Route53 provides DDoS protection

### Question 33
An Application Load Balancer should perform SSL/TLS termination. Where is the certificate configured?

A) On EC2 instances  
B) On ALB listener with ACM certificate  
C) On target groups  
D) On Route53

### Question 34
A global application needs to route users to the AWS region with lowest latency. What Route53 routing policy should be used?

A) Geolocation routing  
B) Latency-based routing  
C) Geoproximity routing  
D) Failover routing

### Question 35
A Network Load Balancer is needed for ultra-low latency and high throughput TCP traffic. What are NLB characteristics? (Choose TWO)

A) Operates at Layer 4 (Transport)  
B) Supports path-based routing  
C) Provides static IP addresses  
D) SSL/TLS termination required  
E) Sticky sessions required

### Question 36
CloudFront serves dynamic content from ALB origin. What feature improves performance for dynamic content?

A) Increase CloudFront TTL  
B) Use CloudFront with no caching  
C) Enable compression  
D) Use S3 origin instead

### Question 37
A company wants to protect CloudFront distribution from DDoS attacks. What services provide protection? (Choose TWO)

A) AWS Shield Standard (automatic)  
B) AWS WAF with rate limiting  
C) Security groups  
D) Network ACLs  
E) VPC Flow Logs

### Question 38
A Route53 Alias record can point to which AWS resources? (Choose THREE)

A) Elastic Load Balancers  
B) CloudFront distributions  
C) S3 website endpoints  
D) EC2 instances  
E) RDS databases

### Question 39
An Application Load Balancer needs to route traffic based on HTTP headers (User-Agent). What type of rule should be configured?

A) Path-based routing rule  
B) Host-based routing rule  
C) HTTP header-based routing rule  
D) Query string-based routing rule

### Question 40
A Classic Load Balancer is being used. Why should it be migrated to ALB or NLB?

A) CLB is deprecated  
B) ALB/NLB provide advanced features (path routing, WebSocket, better performance)  
C) CLB more expensive  
D) CLB doesn't support SSL

### Question 41
CloudFront distribution uses custom origin (EC2). How can origin be protected from direct access?

A) Configure security group allowing only CloudFront IPs  
B) Use custom header verified by origin  
C) Use Signed URLs  
D) All of the above

### Question 42
A company needs to register a new domain name. Can this be done through Route53?

A) No, use external registrar  
B) Yes, Route53 is a domain registrar  
C) Only for .com domains  
D) Only with AWS support

### Question 43
An ALB health check is failing. Instances are healthy but marked unhealthy. What could be the issue?

A) Health check path returns non-200 status code  
B) Health check interval too short  
C) Security group doesn't allow health check traffic from ALB  
D) Both A and C could cause failure

### Question 44
CloudFront can cache content based on which factors? (Choose THREE)

A) Query string parameters  
B) HTTP headers  
C) Cookies  
D) Client IP address  
E) Request method (GET/POST)

### Question 45
A Route53 health check monitors an endpoint. Health check fails but endpoint is accessible. What could be the reason?

A) Health checker IPs blocked by firewall  
B) Health check protocol mismatch  
C) Health check interval too frequent  
D) Both A and B

### Question 46
An NLB should preserve client IP addresses for backend instances. What feature enables this?

A) Proxy Protocol  
B) X-Forwarded-For header  
C) Cross-Zone Load Balancing  
D) Client IP preservation is default for NLB

### Question 47
A CloudFront distribution should serve different content based on device type (mobile/desktop). What feature enables this?

A) Lambda@Edge to detect device  
B) Multiple origins  
C) Geo-targeting  
D) Path patterns

### Question 48
A company uses Route53 private hosted zone. What is required to resolve these DNS names?

A) VPC with enableDnsHostnames and enableDnsSupport  
B) Internet Gateway  
C) Public hosted zone  
D) Route53 Resolver endpoints

### Question 49
An ALB should authenticate users before routing to backend. What feature provides this?

A) Cognito User Pool integration  
B) OIDC-compliant IdP integration  
C) Both A and B  
D) IAM authentication

### Question 50
CloudFront signed URLs vs signed cookies. When should signed URLs be used?

A) Restrict access to individual files  
B) Restrict access to multiple files  
C) Always use signed cookies  
D) No difference

---

## Direct Connect, Transit Gateway, Global Accelerator (Questions 51-65)

### Question 51
A company needs dedicated 10 Gbps connection between on-premises and AWS. What Direct Connect option should be used?

A) Hosted Connection  
B) Dedicated Connection  
C) VPN over Direct Connect  
D) Site-to-Site VPN

### Question 52
A Direct Connect connection requires redundancy. What architecture provides this?

A) Single Direct Connect with VPN backup  
B) Two Direct Connect connections at same location  
C) Two Direct Connect connections at different locations  
D) Both A and C provide redundancy

### Question 53
A company has 20 VPCs that need to connect to on-premises via Direct Connect. What simplifies this architecture?

A) Direct Connect connection to each VPC  
B) Transit Gateway with Direct Connect Gateway  
C) VPN connections to each VPC  
D) VPC Peering mesh

### Question 54
A Transit Gateway connects VPCs in hub-and-spoke model. What are the benefits? (Choose TWO)

A) Simplified network architecture  
B) Centralized routing  
C) Lower cost than VPC Peering  
D) Automatic load balancing  
E) Built-in DDoS protection

### Question 55
A global application needs static anycast IP addresses with automatic failover and DDoS protection. What service provides this?

A) Elastic IP addresses  
B) AWS Global Accelerator  
C) CloudFront  
D) Route53

### Question 56
A Direct Connect connection is established. Traffic still goes over internet. What is missing?

A) Virtual Private Gateway attached to VPC  
B) BGP session configured  
C) Route propagation enabled  
D) All of the above could be missing

### Question 57
A Transit Gateway needs to route traffic between VPCs and on-premises, but one VPC should be isolated. How should this be configured?

A) Use separate Transit Gateways  
B) Use Transit Gateway route tables with association/propagation  
C) Use Network ACLs  
D) Use security groups

### Question 58
A Global Accelerator endpoint should route traffic to multiple ALBs across regions with health-based failover. What feature enables this?

A) Weighted routing  
B) Endpoint groups with health checks  
C) Route53 health checks  
D) CloudWatch alarms

### Question 59
A company needs to access AWS services privately over Direct Connect without internet. What should be configured?

A) Public Virtual Interface (VIF)  
B) Private Virtual Interface (VIF) with VPC  
C) Transit Virtual Interface  
D) VPN over Direct Connect

### Question 60
A Transit Gateway connects VPCs in multiple AWS accounts. What feature enables cross-account attachment?

A) Resource Access Manager (RAM)  
B) AWS Organizations  
C) IAM cross-account roles  
D) VPC Peering

### Question 61
Global Accelerator vs CloudFront. When should Global Accelerator be used?

A) Static content caching  
B) Non-HTTP workloads (TCP/UDP) or static IP requirements  
C) Always use CloudFront  
D) Dynamic content only

### Question 62
A Direct Connect connection provides access to AWS public services (S3, DynamoDB) and VPC resources. How many virtual interfaces are needed?

A) One VIF for both  
B) Public VIF for AWS services, Private VIF for VPC  
C) Transit VIF  
D) No VIFs needed

### Question 63
A Transit Gateway attachment to VPC incurs costs. What affects Transit Gateway costs? (Choose TWO)

A) Number of attachments  
B) Data processed through Transit Gateway  
C) Number of route tables  
D) Number of VPCs  
E) BGP sessions

### Question 64
A Global Accelerator provides two static IP addresses. Can custom IP addresses be used?

A) No, must use provided IPs  
B) Yes, with BYOIP (Bring Your Own IP)  
C) Only with Enterprise Support  
D) Only for specific regions

### Question 65
A company uses Direct Connect. They want to access public AWS services without traversing internet. What should be configured?

A) Private VIF only  
B) Public VIF to access AWS public endpoints  
C) VPN over Direct Connect  
D) Internet Gateway

---

## End of Practice Test 4

Check answers in `answers.md`
