# AWS SAA-C03 Practice Test 7: Application Integration Services

**Topics Covered:** API Gateway, SQS, SNS, EventBridge, Directory Services  
**Number of Questions:** 65  
**Time Limit:** 130 minutes

---

## API Gateway Questions (Questions 1-20)

### Question 1
A company needs to create RESTful APIs for their microservices. What AWS service should be used?

A) Application Load Balancer  
B) Amazon API Gateway  
C) Route53  
D) CloudFront

### Question 2
API Gateway can integrate with which backend services? (Choose THREE)

A) Lambda functions  
B) HTTP endpoints  
C) AWS services (DynamoDB, S3, etc.)  
D) RDS directly  
E) VPC resources via VPC Link

### Question 3
What are API Gateway deployment stages used for?

A) Different environments (dev, test, prod)  
B) API versions  
C) Load balancing  
D) Both A and B

### Question 4
API Gateway has default throttle limit per account per region of:

A) 5,000 requests per second  
B) 10,000 requests per second  
C) 20,000 requests per second  
D) Unlimited

### Question 5
A REST API in API Gateway should require API key authentication. How is this configured?

A) Enable API key required on method  
B) IAM authentication only  
C) Cognito User Pools only  
D) Cannot use API keys

### Question 6
What is API Gateway Lambda authorizer (custom authorizer)?

A) AWS-managed authorization  
B) Lambda function to implement custom authorization logic  
C) Cognito integration  
D) API key validation

### Question 7
API Gateway supports which authentication methods? (Choose THREE)

A) IAM authentication  
B) Cognito User Pools  
C) Lambda authorizers  
D) Active Directory  
E) OAuth 2.0 only

### Question 8
What is API Gateway usage plan?

A) API design plan  
B) Throttling and quota limits for API keys  
C) Deployment plan  
D) Backup plan

### Question 9
API Gateway REST API vs HTTP API. What is a key difference?

A) REST API has more features but higher cost, HTTP API simpler and cheaper  
B) Same functionality and cost  
C) HTTP API deprecated  
D) REST API for HTTP only

### Question 10
What is API Gateway caching used for?

A) Backend caching  
B) Cache endpoint responses to reduce backend calls and latency  
C) Database caching  
D) Static content caching

### Question 11
API Gateway can transform request/response. What feature enables this?

A) Lambda transformation  
B) Mapping templates with VTL (Velocity Template Language)  
C) CloudFront transformation  
D) Automatic transformation

### Question 12
A WebSocket API is needed for real-time bidirectional communication. Does API Gateway support this?

A) No, REST only  
B) Yes, API Gateway supports WebSocket APIs  
C) Use Lambda only  
D) Use EC2 with WebSocket library

### Question 13
What is API Gateway stage variable?

A) Environment variable available in stage configuration  
B) API version  
C) Lambda alias  
D) Backend URL

### Question 14
API Gateway has maximum timeout of:

A) 30 seconds  
B) 29 seconds  
C) 5 minutes  
D) 15 minutes

### Question 15
What is API Gateway private API?

A) Internal API without public endpoint  
B) API accessible only from VPC via VPC endpoint  
C) API with authentication  
D) Local API

### Question 16
API Gateway can generate SDK for API consumers. For which languages? (Choose THREE)

A) JavaScript  
B) iOS (Swift)  
C) Android (Java)  
D) Rust  
E) Assembly

### Question 17
What is API Gateway request validator?

A) Validates request before invoking backend  
B) Load balancer  
C) Authentication service  
D) Rate limiter

### Question 18
API Gateway logs can be sent to:

A) S3 only  
B) CloudWatch Logs  
C) DynamoDB  
D) RDS

### Question 19
What is API Gateway canary deployment?

A) Beta testing  
B) Route percentage of traffic to new deployment for testing  
C) Blue-green deployment  
D) A/B testing

### Question 20
API Gateway CORS (Cross-Origin Resource Sharing) must be enabled when:

A) Always required  
B) API called from browser on different domain  
C) Never required  
D) Only for public APIs

---

## SQS Questions (Questions 21-35)

### Question 21
What is Amazon SQS?

A) Real-time messaging  
B) Fully managed message queuing service for decoupling applications  
C) Database queue  
D) Email service

### Question 22
SQS Standard Queue provides:

A) Guaranteed order  
B) At-least-once delivery, best-effort ordering  
C) Exactly-once delivery  
D) Real-time delivery

### Question 23
SQS FIFO Queue provides:

A) Best-effort ordering  
B) Guaranteed order and exactly-once processing  
C) At-least-once delivery only  
D) No ordering

### Question 24
What is SQS visibility timeout?

A) Message expiration  
B) Time message is hidden from other consumers after being received  
C) Queue creation time  
D) Delay before message available

### Question 25
Maximum SQS message size is:

A) 64 KB  
B) 128 KB  
C) 256 KB  
D) 1 MB (with extended client library to S3)

### Question 26
SQS Dead Letter Queue (DLQ) is used for:

A) Deleted messages  
B) Messages that failed processing after max retries  
C) Spam messages  
D) Expired messages

### Question 27
SQS Long Polling vs Short Polling. What is the benefit of long polling?

A) Faster response  
B) Reduces empty responses and costs by waiting for messages  
C) More expensive  
D) No difference

### Question 28
What is SQS delay queue?

A) Slow queue  
B) Postpone message delivery for specified time  
C) Queue with delay in creation  
D) Backup queue

### Question 29
SQS FIFO queue naming must:

A) Start with "sqs-"  
B) End with ".fifo" suffix  
C) Be numeric only  
D) No naming requirements

### Question 30
Maximum message retention period in SQS is:

A) 1 day  
B) 4 days (default)  
C) 14 days  
D) 30 days

### Question 31
SQS supports which protocols? (Choose TWO)

A) HTTP/HTTPS  
B) AWS SDK  
C) FTP  
D) SMTP  
E) Telnet

### Question 32
What is SQS message attribute?

A) Message body  
B) Optional metadata attached to message  
C) Queue configuration  
D) Visibility timeout

### Question 33
Can SQS messages be encrypted?

A) No encryption support  
B) Yes, with SSE using KMS  
C) Manual encryption only  
D) Base64 encoding only

### Question 34
SQS FIFO queue maximum throughput is:

A) Unlimited  
B) 300 TPS (transactions per second) per action without batching  
C) 1,000 TPS  
D) 10,000 TPS

### Question 35
A consumer processes SQS message but crashes before deleting. What happens?

A) Message lost  
B) Message becomes visible again after visibility timeout  
C) Message duplicated  
D) Queue stopped

---

## SNS Questions (Questions 36-50)

### Question 36
What is Amazon SNS?

A) Queue service  
B) Fully managed pub/sub messaging service  
C) Database notification  
D) Email marketing

### Question 37
SNS Topic is:

A) Message queue  
B) Logical access point for publishers and subscribers  
C) Database table  
D) API endpoint

### Question 38
SNS supports which subscription protocols? (Choose FOUR)

A) HTTP/HTTPS  
B) Email/Email-JSON  
C) SQS  
D) Lambda  
E) RDS

### Question 39
What is SNS message filtering?

A) Spam filtering  
B) Subscribers receive only messages matching filter policy  
C) Message encryption  
D) Message ordering

### Question 40
Can SNS deliver message to multiple protocols simultaneously?

A) No, one protocol per topic  
B) Yes, fanout to multiple subscriptions with different protocols  
C) Requires multiple topics  
D) Manual delivery required

### Question 41
What is SNS FIFO topic?

A) Standard topic  
B) Ordered message delivery with deduplication  
C) Fast topic  
D) Filtered topic

### Question 42
SNS message size limit is:

A) 64 KB  
B) 128 KB  
C) 256 KB  
D) 1 MB

### Question 43
How can SNS trigger Lambda function?

A) Cannot integrate  
B) Lambda subscribes to SNS topic  
C) Manual invocation  
D) Through SQS only

### Question 44
What is SNS Dead Letter Queue?

A) Standard SNS feature  
B) Not native to SNS, configured at subscription level using SQS DLQ  
C) Automatic for all topics  
D) Premium feature

### Question 45
SNS supports message encryption at rest and in transit?

A) No encryption  
B) Yes, with KMS for at-rest, TLS for in-transit  
C) In-transit only  
D) Manual encryption required

### Question 46
What is SNS Mobile Push?

A) Email to mobile  
B) Send push notifications to mobile devices (iOS, Android, etc.)  
C) SMS only  
D) Mobile web notifications

### Question 47
Can SNS be used for application-to-application (A2A) messaging?

A) No, only notifications to users  
B) Yes, SNS to SQS, Lambda, HTTP endpoints  
C) Through SQS only  
D) Requires API Gateway

### Question 48
SNS message delivery retry policy:

A) No retries  
B) Automatic retries with exponential backoff  
C) Single retry  
D) Manual retry

### Question 49
What is SNS message attribute?

A) Message body  
B) Optional metadata sent with message  
C) Topic name  
D) Subscription filter

### Question 50
SNS Standard Topic vs FIFO Topic delivery?

A) Both guarantee ordering  
B) Standard: best-effort ordering, FIFO: guaranteed ordering  
C) Same delivery  
D) FIFO faster

---

## EventBridge and Directory Services (Questions 51-65)

### Question 51
What is Amazon EventBridge (formerly CloudWatch Events)?

A) Log service  
B) Serverless event bus for application event routing  
C) Monitoring service  
D) Database events

### Question 52
EventBridge receives events from:

A) AWS services only  
B) AWS services, custom applications, SaaS partners  
C) Custom applications only  
D) Manual input

### Question 53
What is EventBridge rule?

A) Security rule  
B) Routes events to targets based on event patterns or schedules  
C) Backup rule  
D) Firewall rule

### Question 54
EventBridge can route events to which targets? (Choose FOUR)

A) Lambda functions  
B) SNS topics  
C) SQS queues  
D) Step Functions  
E) RDS databases

### Question 55
What is EventBridge schema registry?

A) Database schema  
B) Discover, create, manage event schemas  
C) API schema  
D) JSON validator

### Question 56
EventBridge Event Bus types include: (Choose THREE)

A) Default event bus (AWS services)  
B) Custom event bus (custom applications)  
C) Partner event bus (SaaS providers)  
D) Global event bus  
E) Private event bus

### Question 57
A scheduled task needs to run every hour. What EventBridge feature enables this?

A) Event pattern rule  
B) Schedule expression (cron/rate)  
C) Lambda trigger  
D) CloudWatch alarm

### Question 58
What is AWS Directory Service?

A) File directory  
B) Managed Microsoft Active Directory in AWS  
C) S3 directory structure  
D) LDAP only

### Question 59
AWS Directory Service options include: (Choose THREE)

A) AWS Managed Microsoft AD  
B) AD Connector  
C) Simple AD  
D) Oracle Directory  
E) Custom LDAP

### Question 60
AD Connector is used for:

A) Creating new directory  
B) Proxy to redirect directory requests to on-premises AD  
C) Standalone directory  
D) File connector

### Question 61
Simple AD is:

A) Full Microsoft AD  
B) Samba-based, AD-compatible directory for basic needs  
C) AD Connector  
D) LDAP only

### Question 62
AWS Managed Microsoft AD provides:

A) Basic directory only  
B) Full Microsoft AD with trust relationships, multi-AZ deployment  
C) Read-only AD  
D) Proxy only

### Question 63
EventBridge vs CloudWatch Events:

A) Completely different services  
B) EventBridge is enhanced version with additional features  
C) CloudWatch Events is newer  
D) No relationship

### Question 64
EventBridge Archive and Replay feature allows:

A) Event backup  
B) Archive events and replay them later for testing/debugging  
C) Event deletion  
D) Event modification

### Question 65
Can EventBridge work with cross-account events?

A) No, same account only  
B) Yes, with resource-based policies allowing cross-account access  
C) Requires VPC peering  
D) Manual event forwarding only

---

## End of Practice Test 7

Check answers in `answers.md`

---

# Congratulations!

You've completed all 7 AWS SAA-C03 practice tests covering:
1. **Compute Services** - EC2, Lambda, Auto Scaling
2. **Storage Services** - S3, EBS, EFS, FSx, Storage Gateway, Backup
3. **Database Services** - RDS, Aurora, DynamoDB, Redshift
4. **Networking Services** - VPC, Route53, CloudFront, ELB, Direct Connect, Transit Gateway
5. **Security & Identity** - IAM, Cognito, KMS, Secrets Manager, GuardDuty, Inspector, WAF, Shield
6. **Management & Governance** - CloudFormation, CloudWatch, CloudTrail, Config, Systems Manager, Organizations
7. **Application Integration** - API Gateway, SQS, SNS, EventBridge, Directory Services

**Total Questions:** 455 (65 questions × 7 tests)

Review your answers, identify weak areas, and continue studying AWS documentation. Good luck with your SAA-C03 certification! 🚀
