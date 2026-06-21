# Practice Test 01 — Answers and Explanations

---

### 1 — **C) Send order messages to an SQS queue consumed by the inventory Lambda**

SQS provides durable message buffering. If the inventory Lambda is down, messages remain in the queue (up to 14 days retention) and are processed when the consumer recovers. Synchronous invocation (A) fails when the downstream service is unavailable. SNS direct Lambda (B) has limited retry and no persistent buffer. DynamoDB Streams (D) is for table change events, not general decoupling.

---

### 2 — **B) Increase the SQS visibility timeout to exceed the Lambda timeout**

When a message is received, it becomes invisible for the visibility timeout duration. If processing exceeds this timeout, the message reappears and may be processed twice. Set visibility timeout ≥ Lambda timeout (AWS recommends 6× Lambda timeout for event source mappings). DLQ (D) captures failed messages but doesn't fix the reprocessing issue.

---

### 3 — **C) Lambda function throwing an unhandled exception or timing out**

API Gateway returns 502 when Lambda fails synchronously — unhandled exceptions or timeouts. Incorrect response format (B) can also cause 502, but exceptions/timeouts are the most common intermittent cause. Throttling (A) returns 429. CORS (D) causes browser errors, not 502.

---

### 4 — **B) Use Cognito Identity Pool to exchange authenticated identity for temporary AWS credentials**

Cognito Identity Pools (Federated Identities) exchange authenticated user identity for temporary AWS credentials via STS — the standard pattern for mobile direct-to-S3 uploads. Never embed IAM user keys (A). Pre-signed URLs (C) work but require a backend to generate them.

---

### 5 — **B) Create a Global Secondary Index with email as the partition key**

When you need to query by an attribute that isn't the table's primary key, create a GSI. Scan (A) reads the entire table — expensive and slow. LSI (C) requires the same partition key as the table. Streams (D) is over-engineered for this use case.

---

### 6 — **B) S3 → SNS → multiple SQS queues (each with its own Lambda consumer)**

The fan-out pattern: SNS delivers to multiple subscribers independently. Using SQS between SNS and Lambda adds buffering and per-consumer retry/DLQ. Single Lambda (A) creates tight coupling. Single SQS (C) gives competing consumers, not independent fan-out.

---

### 7 — **A) Attach the Lambda function to the same VPC and private subnets as RDS** and **B) Assign a security group to the Lambda that allows outbound traffic to RDS**

Lambda must be in the VPC to reach private RDS (A). Security groups must allow Lambda → RDS traffic (B). NAT/endpoints (D) are needed for AWS API calls from VPC Lambda, but aren't the primary fix for RDS connectivity. Timeout (C) doesn't fix network issues.

---

### 8 — **A) CloudWatch Events / EventBridge scheduled rule**

EventBridge (formerly CloudWatch Events) supports cron and rate expressions for scheduled Lambda invocations. SQS delay (B) is per-message, not recurring schedule. Destinations (C) route async results. Step Functions Wait (D) is for workflow delays.

---

### 9 — **B) FIFO queues guarantee exactly-once processing and strict message ordering**

FIFO queues enforce strict ordering and exactly-once processing (with deduplication). Throughput is limited to 3,000 msg/sec (A is wrong). FIFO supports DLQ (C is wrong). Names must end in `.fifo` (D is wrong).

---

### 10 — **C) The SDK cannot reuse connections when initialized inside the handler**

While global scope persists on warm starts, initializing inside the handler creates a new client every invocation — missing connection reuse optimization. The best practice is initializing boto3 clients **outside** the handler in global scope. Lambda does reuse execution environments on warm starts (D is wrong).

---

### 11 — **B) Exponential backoff with jitter and a maximum retry count**

Standard resilience pattern for transient failures (503). Infinite retry (A) can cause cascading failures. Manual S3 storage (C) is not automated retry. Step Functions (D) is overkill for simple HTTP retry logic.

---

### 12 — **A) Return a `batchItemFailures` list from the Lambda handler**

For Kinesis and DynamoDB Streams event source mappings, returning `batchItemFailures` with failed record IDs allows partial batch failure — only failed records are retried. DLQ on DynamoDB table (C) doesn't exist as a concept.

---

### 13 — **B) `event.requestContext.authorizer.claims`**

When API Gateway validates a Cognito JWT, it passes decoded claims to Lambda in `event.requestContext.authorizer.claims`. The raw token is in headers (A) but claims are the parsed user info.

---

### 14 — **B) Amazon Kinesis Data Streams**

Kinesis Data Streams is designed for real-time streaming data ingestion with custom processing (Lambda or Kinesis Analytics). SQS (A) is message queuing, not streaming. SNS (C) is pub/sub notifications. DataSync (D) is file transfer.

---

### 15 — **B) Configure an EventBridge rule with event pattern matching on the amount field**

EventBridge rules support content-based filtering including numeric comparisons. Filtering in Lambda (A) wastes invocations. SNS filtering (C) could work but EventBridge is the designated event routing service for application events with complex patterns.

---

**Score guide:** 13–15 = strong · 10–12 = review weak areas · Below 10 = revisit Domain 1 guides
