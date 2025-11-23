# AWS SAA-C03 Practice Test 5: Security & Identity Services

**Topics Covered:** IAM, Cognito, KMS, Secrets Manager, Certificate Manager, GuardDuty, Inspector, WAF & Shield  
**Number of Questions:** 65  
**Time Limit:** 130 minutes

---

## IAM Questions (Questions 1-25)

### Question 1
What is the AWS recommended best practice for the root account?

A) Use for daily tasks  
B) Enable MFA and use only for initial setup  
C) Share credentials with team  
D) Disable after account creation

### Question 2
A developer needs programmatic access to AWS. What should be created?

A) IAM user with access keys  
B) Root account credentials  
C) IAM role  
D) Security token

### Question 3
An EC2 instance needs to access S3 buckets. What is the MOST secure way?

A) Store access keys on instance  
B) Attach IAM role to instance  
C) Use root account credentials  
D) Store credentials in code

### Question 4
A policy allows s3:GetObject for bucket "example-bucket/*". What does this allow?

A) Read all objects in bucket  
B) List bucket contents  
C) Download objects but not list  
D) Both read and list

### Question 5
What is the permission boundary effect in IAM?

A) Expands permissions  
B) Sets maximum permissions a user can have  
C) Denies all permissions  
D) Duplicates inline policies

### Question 6
Cross-account access is needed. What is the BEST approach?

A) Share credentials  
B) Create IAM role with trust policy for external account  
C) Use root accounts  
D) Create duplicate users

### Question 7
An IAM policy has both Allow and Deny for same action. What happens?

A) Allow takes precedence  
B) Deny takes precedence  
C) Policy error  
D) Depends on order

### Question 8
What is an IAM policy condition?

A) Mandatory policy field  
B) Optional constraints (IP, time, MFA) for when policy applies  
C) Policy version  
D) Resource tag

### Question 9
How many IAM users can be created in an AWS account?

A) 100  
B) 500  
C) 5,000 (default limit)  
D) Unlimited

### Question 10
A policy grants "s3:*" on "arn:aws:s3:::mybucket". What is missing for full bucket access?

A) Nothing, this is complete  
B) Need "mybucket/*" for objects  
C) Need GetBucketLocation  
D) Need encryption permissions

### Question 11
What is AWS STS (Security Token Service)?

A) Permanent credentials  
B) Temporary security credentials for IAM roles  
C) Multi-factor authentication  
D) Password policy service

### Question 12
An IAM group has 10 users. A policy is attached to the group. What happens?

A) Only first user gets permissions  
B) All users in group inherit permissions  
C) Must attach to each user individually  
D) Group policies don't work

### Question 13
What is IAM Access Analyzer used for?

A) Generating policies  
B) Finding resources shared with external entities  
C) Password auditing  
D) MFA enforcement

### Question 14
A user has AdministratorAccess managed policy. They cannot delete S3 bucket. Why?

A) S3 deletion requires additional permissions  
B) Bucket has deletion protection  
C) Service control policy (SCP) may deny  
D) Both B and C possible

### Question 15
What is the IAM policy evaluation logic order?

A) Explicit Allow → Implicit Deny → Explicit Deny  
B) Explicit Deny → Explicit Allow → Implicit Deny  
C) Implicit Deny → Explicit Allow → Explicit Deny  
D) Random order

### Question 16
How can you enforce MFA for AWS CLI access?

A) MFA automatically required  
B) Policy condition requiring aws:MultiFactorAuthPresent  
C) Cannot enforce MFA for CLI  
D) Use root account

### Question 17
What is an IAM instance profile?

A) EC2 instance type configuration  
B) Container for IAM role used by EC2  
C) Instance metadata  
D) Security group

### Question 18
A Lambda function needs temporary elevated permissions. What should be used?

A) IAM user credentials  
B) STS AssumeRole to get temporary credentials  
C) Root account  
D) Hard-coded keys

### Question 19
How many managed policies can be attached to an IAM user?

A) 1  
B) 5  
C) 10  
D) 20

### Question 20
What is AWS Organizations SCP (Service Control Policy)?

A) Billing policy  
B) Maximum permissions boundary for accounts in organization  
C) Network policy  
D) Backup policy

### Question 21
A policy uses "NotPrincipal" in resource policy. What does this mean?

A) Apply to all principals  
B) Apply to all EXCEPT specified principals  
C) Invalid syntax  
D) Same as "Principal"

### Question 22
What is IAM credential report used for?

A) Listing all IAM users and credential status  
B) Billing information  
C) Resource usage  
D) Network traffic

### Question 23
Can IAM policies be attached to AWS account root user?

A) Yes  
B) No, root has all permissions by default  
C) Only deny policies  
D) With SCP only

### Question 24
What is aws:PrincipalOrgID condition used for?

A) Checking user ID  
B) Restricting access to specific AWS Organization  
C) Checking account number  
D) Validating MFA

### Question 25
How do you grant permissions to an AWS service to perform actions on your behalf?

A) IAM user for service  
B) Service role with trust policy for that service  
C) Root account  
D) Access keys for service

---

## Cognito, KMS, Secrets Manager (Questions 26-45)

### Question 26
A mobile app needs user authentication with social logins (Google, Facebook). What AWS service should be used?

A) IAM users  
B) Amazon Cognito User Pools  
C) AWS SSO  
D) Active Directory

### Question 27
A mobile app users need temporary AWS credentials to access S3. What Cognito feature provides this?

A) Cognito User Pools  
B) Cognito Identity Pools (Federated Identities)  
C) Cognito Sync  
D) IAM users

### Question 28
What is the difference between Cognito User Pools and Identity Pools?

A) User Pools = Authentication, Identity Pools = AWS credentials  
B) Same functionality  
C) Identity Pools = Authentication only  
D) User Pools = AWS credentials only

### Question 29
An application stores database passwords that need automatic rotation. What AWS service provides this?

A) Parameter Store  
B) AWS Secrets Manager with rotation  
C) KMS  
D) IAM

### Question 30
AWS KMS Customer Managed Keys (CMK) are used for encryption. Who manages key material?

A) Customer manages key material  
B) AWS manages key material, customer controls usage  
C) Fully customer managed  
D) AWS controls everything

### Question 31
A company needs to import their own encryption keys to AWS. What KMS feature enables this?

A) Customer Managed Keys  
B) AWS Managed Keys  
C) Import key material (BYOK)  
D) Not possible

### Question 32
What is envelope encryption in KMS?

A) Encrypting email  
B) Using data key to encrypt data, KMS CMK to encrypt data key  
C) Double encryption  
D) Physical envelope for keys

### Question 33
A Lambda function needs to decrypt data encrypted with KMS. What permission is needed?

A) kms:Decrypt on CMK  
B) kms:Encrypt only  
C) kms:GetKey  
D) No specific permission

### Question 34
What is the maximum size of data that can be encrypted directly with KMS?

A) 1 KB  
B) 4 KB  
C) 64 KB  
D) 1 MB

### Question 35
Secrets Manager vs Parameter Store. When should Secrets Manager be used?

A) Always use Secrets Manager  
B) When automatic rotation and RDS integration needed  
C) For configuration values  
D) No difference

### Question 36
A KMS key is accidentally deleted. What is the minimum waiting period before deletion?

A) Immediate deletion  
B) 7 to 30 days waiting period  
C) 90 days  
D) Cannot delete KMS keys

### Question 37
What is AWS Certificate Manager (ACM) used for?

A) Provisioning and managing SSL/TLS certificates  
B) Managing IAM certificates  
C) KMS key management  
D) Password certificates

### Question 38
ACM certificates can be used with which services? (Choose THREE)

A) CloudFront  
B) Application Load Balancer  
C) EC2 instances directly  
D) API Gateway  
E) S3 buckets

### Question 39
A Cognito User Pool requires MFA for all users. What MFA options are available? (Choose TWO)

A) SMS text message  
B) Time-based One-Time Password (TOTP)  
C) Email verification  
D) Push notifications  
E) Voice call

### Question 40
What happens when a KMS CMK is disabled?

A) All encrypted data becomes inaccessible  
B) Encryption/decryption operations fail temporarily  
C) Data automatically decrypted  
D) Key permanently deleted

### Question 41
A multi-region application needs to encrypt data with same key material in different regions. What KMS feature provides this?

A) Copy key to regions  
B) Multi-Region Keys  
C) Global keys  
D) Not possible

### Question 42
Parameter Store SecureString vs Secrets Manager. What is a key difference?

A) SecureString cannot encrypt  
B) Secrets Manager has automatic rotation, SecureString doesn't  
C) Same functionality  
D) SecureString more expensive

### Question 43
A web application uses Cognito User Pools for authentication. Where are user credentials stored?

A) In your database  
B) In Cognito User Pool managed by AWS  
C) In IAM  
D) In Active Directory

### Question 44
What is a KMS grant?

A) Permission in key policy  
B) Temporary, programmatic permission delegation  
C) IAM policy  
D) User group

### Question 45
ACM certificates are free for use with AWS services. What is the limitation?

A) Limited to 10 certificates  
B) Cannot export private keys for use outside AWS services  
C) Only 1-year validity  
D) Only for CloudFront

---

## GuardDuty, Inspector, WAF & Shield (Questions 46-65)

### Question 46
What is AWS GuardDuty?

A) Firewall service  
B) Threat detection service analyzing logs (VPC Flow, CloudTrail, DNS)  
C) Backup service  
D) Compliance service

### Question 47
GuardDuty findings show cryptocurrency mining. What data source detected this?

A) VPC Flow Logs  
B) CloudTrail logs  
C) DNS logs  
D) All of the above could detect it

### Question 48
AWS Inspector assesses what aspects? (Choose TWO)

A) EC2 instance vulnerabilities  
B) Network accessibility  
C) S3 bucket policies  
D) DynamoDB performance  
E) CloudWatch metrics

### Question 49
What is AWS Shield Standard?

A) Paid DDoS protection  
B) Free automatic DDoS protection for all AWS customers  
C) Requires activation  
D) Only for CloudFront

### Question 50
AWS Shield Advanced provides what additional features? (Choose THREE)

A) 24/7 DDoS Response Team (DRT)  
B) Cost protection during DDoS attacks  
C) Advanced DDoS detection  
D) Free service  
E) Automatic snapshots

### Question 51
AWS WAF can be deployed with which services? (Choose THREE)

A) CloudFront  
B) Application Load Balancer  
C) EC2 instances  
D) API Gateway  
E) S3 buckets

### Question 52
A WAF Web ACL has rate-based rule limiting requests to 2,000 per 5 minutes. What happens at 2,001 requests?

A) All requests blocked  
B) Additional requests blocked until rate drops  
C) Warning logged only  
D) No action

### Question 53
GuardDuty is enabled. When are findings generated?

A) Only during business hours  
B) Continuously, automatically analyzes logs  
C) On-demand scans only  
D) Weekly reports

### Question 54
AWS Inspector requires what to scan EC2 instances?

A) Inspector agent installed on instances  
B) No agent required  
C) VPC Flow Logs enabled  
D) GuardDuty enabled

### Question 55
WAF rule matches SQL injection pattern. What action can be configured?

A) Allow, Block, or Count  
B) Block only  
C) Log only  
D) Redirect

### Question 56
What is AWS Macie used for?

A) DDoS protection  
B) Discovering and protecting sensitive data (PII) in S3  
C) Network scanning  
D) Log analysis

### Question 57
A company wants to block requests from specific countries to their CloudFront distribution. What service should be used?

A) Security groups  
B) AWS WAF with geo-match condition  
C) CloudFront geo-restriction  
D) Both B and C work

### Question 58
GuardDuty finding severity levels are High, Medium, Low. What should be done for High severity?

A) Ignore  
B) Investigate immediately, potential security incident  
C) Review monthly  
D) Automatic remediation

### Question 59
AWS Inspector assessment templates can assess: (Choose TWO)

A) Common Vulnerabilities and Exposures (CVEs)  
B) CIS Operating System Security Configuration Benchmarks  
C) Database performance  
D) S3 object encryption  
E) Lambda function code

### Question 60
WAF managed rules are available. What are these?

A) AWS and third-party pre-configured rule sets  
B) Custom rules only  
C) Free rules  
D) Auto-generated rules

### Question 61
A WAF rule should block requests with specific user-agent header. What rule type should be used?

A) IP match condition  
B) String match condition on header  
C) Geo match condition  
D) Size constraint

### Question 62
GuardDuty finding shows "UnauthorizedAccess:EC2/SSHBruteForce". What does this indicate?

A) Successful SSH login  
B) Multiple failed SSH authentication attempts  
C) SSH service down  
D) Port 22 open

### Question 63
What is AWS Security Hub?

A) Firewall hub  
B) Centralized security findings aggregator from multiple services  
C) VPN hub  
D) Network hub

### Question 64
Shield Advanced provides DDoS cost protection. What does this mean?

A) Refund for DDoS mitigation costs  
B) Credits for scaled-up resources during DDoS attack  
C) Free bandwidth  
D) Discount on services

### Question 65
A WAF Web ACL should allow traffic from specific IP addresses only. What rule type?

A) IP set match condition  
B) Geo match  
C) String match  
D) Rate limit

---

## End of Practice Test 5

Check answers in `answers.md`
