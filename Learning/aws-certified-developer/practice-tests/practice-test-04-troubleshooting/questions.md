# Practice Test 04 — Troubleshooting & Optimization (DVA-C02)

**15 questions** · Domain 4 (18%) · Recommended time: 25 minutes

---

## Questions

### 1
A Lambda function shows high `Duration` metrics but low `Errors`. What is the BEST first step to identify the bottleneck?

A) Increase memory to maximum  
B) Enable AWS X-Ray tracing and analyze the service map  
C) Delete and recreate the function  
D) Disable CloudWatch Logs  

### 2
CloudWatch Logs Insights is used to:

A) Deploy Lambda functions  
B) Query and analyze log data using a SQL-like syntax  
C) Encrypt log data  
D) Create IAM policies  

### 3
A Lambda function is throttled frequently (`TooManyRequestsException`). The account has available concurrency. What may be causing this?

A) Function has reserved concurrency set to 0 or a low limit  
B) DynamoDB on-demand mode  
C) API Gateway caching enabled  
D) X-Ray tracing enabled  

### 4
Which CloudWatch Lambda metric indicates messages are backing up in a Kinesis or DynamoDB Stream?

A) Errors  
B) IteratorAge  
C) Invocations  
D) Duration  

### 5
A developer wants custom business metrics without calling PutMetricData API for each event. Which approach should be used?

A) Embedded Metric Format (EMF) in log output  
B) Manual spreadsheet tracking  
C) Disable metrics  
D) S3 access logs  

### 6
What is the recommended way to eliminate Lambda cold starts for a latency-sensitive production API?

A) Reduce memory to 128 MB  
B) Provisioned Concurrency  
C) Disable logging  
D) Use asynchronous invocation  

### 7
A Lambda function's memory is increased from 512 MB to 1024 MB and execution time drops by 60%. Total cost per invocation may:

A) Always increase  
B) Decrease, because shorter duration can offset higher memory cost  
C) Stay exactly the same  
D) Become zero  

### 8
An application logs unstructured plain text. Debugging production issues is difficult. What should the developer implement?

A) Disable logging to reduce costs  
B) Structured JSON logging with correlation IDs  
C) Log only error messages without timestamps  
D) Email logs to developers  

### 9
X-Ray "fault" vs "error" — which statement is correct?

A) They are identical  
B) Fault = client-side 4xx; Error = server-side unhandled exception (5xx)  
C) Fault = server error; Error = client error  
D) X-Ray does not distinguish between them  

### 10
A developer needs to alert the team when Lambda errors exceed 5 in 5 minutes. Which services should be used?

A) CloudWatch Alarm → SNS notification  
B) CloudTrail → S3  
C) AWS Config → remediation  
D) IAM Access Analyzer  

### 11
API Gateway caching reduces load on backend services. Cache hits are determined by:

A) Random selection  
B) Cache key based on configured query strings, headers, and path  
C) User identity only  
D) Lambda memory size  

### 12
A DynamoDB read-heavy application has high latency. Which caching service provides microsecond read latency in front of DynamoDB?

A) CloudFront  
B) DynamoDB Accelerator (DAX)  
C) S3 Transfer Acceleration  
D) API Gateway throttling  

### 13
SNS subscription filter policies optimize messaging by:

A) Encrypting messages  
B) Delivering only messages matching the filter to each subscriber  
C) Increasing message size  
D) Deleting old messages  

### 14
A Lambda in VPC cannot reach the public internet or AWS APIs. What is likely missing?

A) Increase timeout  
B) NAT Gateway or VPC endpoints in the subnet route tables  
C) Enable Provisioned Concurrency  
D) Add more memory  

### 15
After deploying new code, CloudFormation stack enters ROLLBACK_COMPLETE state. Where should the developer look first?

A) CloudWatch Logs for Lambda  
B) CloudFormation stack events for the failure reason  
C) Route 53 health checks  
D) S3 bucket policy  

---

See [answers.md](answers.md)
