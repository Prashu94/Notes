# AWS SAA-C03 Practice Test 6: Management & Governance

**Topics Covered:** CloudFormation, CloudWatch, CloudTrail, Config, Systems Manager, Organizations, Trusted Advisor  
**Number of Questions:** 65  
**Time Limit:** 130 minutes

---

## CloudFormation Questions (Questions 1-15)

### Question 1
A company wants to deploy infrastructure as code with templates. What AWS service should be used?

A) AWS CloudFormation  
B) AWS CodeDeploy  
C) AWS Elastic Beanstalk  
D) Terraform only

### Question 2
A CloudFormation template creates EC2, RDS, and VPC. One resource fails. What happens?

A) Successful resources remain, failed resource skipped  
B) Entire stack rolls back by default  
C) Manual cleanup required  
D) Stack partially created

### Question 3
What format can CloudFormation templates use? (Choose TWO)

A) JSON  
B) YAML  
C) XML  
D) CSV  
E) Python

### Question 4
A CloudFormation stack needs to be deployed across multiple regions. What feature enables this?

A) Multi-region templates  
B) CloudFormation StackSets  
C) Copy template manually  
D) Global templates

### Question 5
What is a CloudFormation Change Set?

A) Preview of changes before executing stack update  
B) Automatic stack updates  
C) Version control  
D) Stack backup

### Question 6
A stack creation fails during RDS creation. How can specific resources be skipped on retry?

A) Delete entire stack and recreate  
B) Use continue-update-rollback with resources-to-skip  
C) Cannot skip resources  
D) Modify template only

### Question 7
CloudFormation intrinsic functions include: (Choose TWO)

A) Ref (references parameters/resources)  
B) Fn::GetAtt (get resource attributes)  
C) Fn::Delete  
D) Fn::Connect  
E) Fn::Deploy

### Question 8
What is CloudFormation drift detection used for?

A) Network latency detection  
B) Detecting manual changes to stack resources  
C) Cost calculation  
D) Performance monitoring

### Question 9
A CloudFormation template parameter needs validation. What can be used?

A) Parameter constraints (AllowedValues, AllowedPattern)  
B) Lambda validation  
C) Manual validation only  
D) AWS Config rules

### Question 10
What is CloudFormation nested stack?

A) Stack within another stack's template  
B) Stacks in same region  
C) Related stacks  
D) Stack version

### Question 11
CloudFormation stack policy prevents what?

A) Stack creation  
B) Unintended updates/deletions of stack resources  
C) Parameter changes  
D) Template syntax errors

### Question 12
A template needs to output VPC ID for use in another stack. What feature enables this?

A) CloudFormation Exports and Imports  
B) Parameter Store  
C) S3 bucket  
D) Manual copy

### Question 13
What is CloudFormation Custom Resource?

A) AWS-managed resource type  
B) Lambda or SNS-backed resource for custom provisioning  
C) Third-party template  
D) Nested stack

### Question 14
CloudFormation template has "DeletionPolicy: Retain". What happens on stack deletion?

A) Resource deleted with stack  
B) Resource retained, not deleted  
C) Stack cannot be deleted  
D) Snapshot taken only

### Question 15
A stack update requires replacement of EC2 instance. How can you preview this?

A) Test in separate account  
B) Create Change Set to see replacement indicator  
C) Check CloudWatch  
D) Manual calculation

---

## CloudWatch Questions (Questions 16-30)

### Question 16
CloudWatch default monitoring for EC2 provides metrics every:

A) 1 minute  
B) 5 minutes  
C) 10 minutes  
D) Real-time

### Question 17
What is CloudWatch Logs used for?

A) Storing and monitoring log files from applications and services  
B) API call logging  
C) Configuration changes  
D) Cost tracking

### Question 18
A Lambda function needs custom metrics. How should these be published?

A) Automatic from Lambda  
B) Use PutMetricData API  
C) Enable CloudWatch Integration  
D) Use CloudTrail

### Question 19
CloudWatch Alarms can trigger which actions? (Choose THREE)

A) SNS notification  
B) EC2 action (stop/terminate/reboot)  
C) Auto Scaling action  
D) S3 upload  
E) RDS query

### Question 20
What is CloudWatch Logs Insights?

A) Query and analyze log data using SQL-like syntax  
B) Log storage  
C) Log delivery  
D) Log encryption

### Question 21
A CloudWatch alarm is in "INSUFFICIENT_DATA" state. What does this mean?

A) Alarm error  
B) Not enough data points to determine alarm state  
C) Service down  
D) Metric deleted

### Question 22
What is CloudWatch Events (now EventBridge)?

A) Log aggregation  
B) Event-driven automation responding to AWS resource changes  
C) Metric collection  
D) Performance monitoring

### Question 23
CloudWatch Logs retention can be set to:

A) 1 day minimum  
B) Custom period from 1 day to indefinite  
C) 30 days fixed  
D) 1 year maximum

### Question 24
What is a CloudWatch Dashboard?

A) Customizable display of metrics and alarms  
B) AWS console homepage  
C) Billing dashboard  
D) Resource inventory

### Question 25
CloudWatch Contributor Insights analyzes what?

A) Cost contributors  
B) Top-N contributors to metrics (e.g., top IPs, URLs)  
C) Performance bottlenecks  
D) Security vulnerabilities

### Question 26
A CloudWatch alarm should trigger after 3 consecutive periods of threshold breach. How is this configured?

A) Evaluation periods set to 3  
B) Datapoints to alarm set to 3 out of 3  
C) Period set to 3 minutes  
D) Cannot configure

### Question 27
What is CloudWatch cross-account observability?

A) Sharing metrics across accounts  
B) Monitoring multiple accounts from central account  
C) Account billing  
D) Cross-region monitoring

### Question 28
CloudWatch Logs can export to: (Choose TWO)

A) S3  
B) EC2  
C) Elasticsearch (OpenSearch)  
D) RDS  
E) DynamoDB

### Question 29
What is CloudWatch Anomaly Detection?

A) Manual threshold setting  
B) ML-powered dynamic threshold baselines  
C) Static alarms  
D) Log parsing

### Question 30
CloudWatch ServiceLens provides what capability?

A) Cost analysis  
B) End-to-end view of application with traces, metrics, logs  
C) Service health  
D) Backup status

---

## CloudTrail, Config Questions (Questions 31-45)

### Question 31
What does AWS CloudTrail log?

A) Performance metrics  
B) API calls and AWS account activity  
C) Application logs  
D) Network traffic

### Question 32
CloudTrail logs should be protected from tampering. What should be enabled? (Choose TWO)

A) Log file validation  
B) S3 bucket with restrictive policy  
C) CloudWatch integration  
D) SNS notification  
E) Glacier storage

### Question 33
A security audit requires tracking who created an S3 bucket. What service provides this?

A) CloudWatch  
B) AWS CloudTrail  
C) AWS Config  
D) VPC Flow Logs

### Question 34
What is CloudTrail Event History?

A) 90-day viewable history of management events  
B) 30-day history  
C) Real-time events only  
D) Requires trail configuration

### Question 35
CloudTrail can deliver logs to which destinations? (Choose TWO)

A) S3 bucket  
B) CloudWatch Logs  
C) DynamoDB  
D) RDS  
E) EC2 instance

### Question 36
What is AWS Config used for?

A) Performance monitoring  
B) Recording and evaluating AWS resource configurations  
C) Log aggregation  
D) Cost optimization

### Question 37
AWS Config Rules can automatically remediate non-compliant resources. What is this called?

A) Config automation  
B) Automatic remediation with SSM Automation documents  
C) Config enforcement  
D) Compliance rollback

### Question 38
A Config rule checks if all S3 buckets have encryption enabled. What type of rule is this?

A) Managed rule (AWS provided)  
B) Custom rule  
C) Both could work  
D) Config cannot check encryption

### Question 39
What is AWS Config aggregator?

A) Cost aggregation  
B) Collect Config data from multiple accounts/regions  
C) Log aggregator  
D) Resource grouping

### Question 40
CloudTrail Insights detects what?

A) Cost anomalies  
B) Unusual API activity patterns  
C) Security vulnerabilities  
D) Performance issues

### Question 41
A compliance requirement needs all CloudTrail logs centralized from multiple accounts. What architecture should be used?

A) CloudTrail in each account to same S3 bucket  
B) Centralized logging account with cross-account access  
C) Manual log copying  
D) CloudWatch aggregation

### Question 42
AWS Config conformance packs are:

A) Single Config rules  
B) Collection of Config rules and remediation as single entity  
C) Backup packages  
D) Deployment packages

### Question 43
What is CloudTrail data events?

A) Management API calls (default)  
B) Resource operations like S3 GetObject, Lambda Invoke  
C) Network traffic  
D) Performance metrics

### Question 44
AWS Config timeline shows what?

A) Cost over time  
B) Configuration changes to resource over time  
C) Performance history  
D) API call history

### Question 45
CloudTrail trail can be organization trail. What does this mean?

A) Trail for single account  
B) Trail that logs events for all accounts in AWS Organization  
C) Trail with multiple regions  
D) Paid trail tier

---

## Systems Manager, Organizations, Trusted Advisor (Questions 46-65)

### Question 46
AWS Systems Manager Session Manager provides what capability?

A) SSH key management  
B) Browser-based shell access to EC2 without SSH keys/bastion hosts  
C) Password management  
D) Network sessions

### Question 47
What is Systems Manager Parameter Store used for?

A) EC2 parameters  
B) Centralized configuration and secrets management  
C) Performance parameters  
D) Network parameters

### Question 48
Systems Manager Patch Manager automates what?

A) Code patching  
B) Operating system and application patching for EC2  
C) Network patching  
D) Database patching

### Question 49
What is Systems Manager Run Command?

A) Execute commands on multiple instances remotely  
B) Start instances  
C) Deploy applications  
D) Monitor performance

### Question 50
Systems Manager Automation documents (SSM documents) can:

A) Run commands only  
B) Automate common maintenance and deployment tasks  
C) Store parameters  
D) Monitor logs

### Question 51
What is AWS Organizations?

A) IAM for multiple users  
B) Centrally manage and govern multiple AWS accounts  
C) Resource organization  
D) Cost allocation

### Question 52
Service Control Policies (SCPs) in Organizations provide what?

A) Billing policies  
B) Maximum permissions boundary for accounts  
C) Network policies  
D) Backup policies

### Question 53
What is an Organizational Unit (OU) in AWS Organizations?

A) Single AWS account  
B) Container for accounts to apply policies hierarchically  
C) IAM user group  
D) VPC subnet

### Question 54
Organizations consolidated billing provides: (Choose TWO)

A) Single bill for all accounts  
B) Volume discounts across accounts  
C) Separate billing for each account  
D) Free tier shared  
E) Cost optimization

### Question 55
What happens when an account leaves an AWS Organization?

A) Account deleted  
B) Account becomes standalone, loses organization policies  
C) Cannot leave organization  
D) Resources deleted

### Question 56
AWS Trusted Advisor provides checks in which categories? (Choose THREE)

A) Cost Optimization  
B) Performance  
C) Security  
D) Code quality  
E) Service Limits

### Question 57
Trusted Advisor cost optimization checks are available in which support plans?

A) All plans  
B) Business and Enterprise plans (full checks)  
C) Enterprise only  
D) Paid plans only

### Question 58
A Trusted Advisor check shows "Red" status. What does this indicate?

A) Everything okay  
B) Action recommended (investigation or action required)  
C) Warning  
D) Information only

### Question 59
What is Systems Manager OpsCenter?

A) Operations dashboard  
B) Centralized location to view, investigate, resolve operational issues  
C) Cost center  
D) Data center

### Question 60
Systems Manager Inventory collects what information?

A) Asset billing  
B) Metadata about instances, installed applications, configurations  
C) Network traffic  
D) Performance metrics

### Question 61
What is AWS Control Tower?

A) Network controller  
B) Easiest way to set up and govern multi-account AWS environment  
C) Cost control  
D) Access control

### Question 62
Service Control Policies can: (Choose TWO)

A) Grant permissions  
B) Deny permissions (maximum boundary)  
C) Replace IAM policies  
D) Apply to management account  
E) Override IAM Allow

### Question 63
What is Systems Manager Maintenance Window?

A) Service maintenance notification  
B) Schedule for running tasks on instances at defined times  
C) Instance uptime window  
D) Backup window

### Question 64
Trusted Advisor can automatically refresh checks:

A) Never, manual only  
B) Weekly automatic refresh (some checks)  
C) Real-time continuously  
D) Daily for all checks

### Question 65
AWS Organizations allows what account structure?

A) Flat structure only  
B) Hierarchical with root, OUs, and accounts  
C) Maximum 10 accounts  
D) Single level only

---

## End of Practice Test 6

Check answers in `answers.md`
