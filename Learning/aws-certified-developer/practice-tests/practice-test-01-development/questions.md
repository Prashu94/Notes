# Practice Test 01 — Development with AWS Services (DVA-C02)

**15 questions** · Domain 1 (32%) · Recommended time: 25 minutes

---

## Questions

### 1
A developer needs to decouple an order-processing Lambda function from an inventory-update Lambda function. The inventory service may be temporarily unavailable, and orders must not be lost.

Which solution meets these requirements?

A) Invoke the inventory Lambda synchronously from the order Lambda  
B) Publish order events to an SNS topic with a direct Lambda subscription  
C) Send order messages to an SQS queue consumed by the inventory Lambda  
D) Store orders in DynamoDB and use DynamoDB Streams to trigger the inventory Lambda  

---

### 2
A Lambda function processes messages from an SQS queue. Occasionally, processing takes longer than expected, and messages reappear in the queue while still being processed.

What should the developer configure?

A) Increase the Lambda memory allocation  
B) Increase the SQS visibility timeout to exceed the Lambda timeout  
C) Enable SQS long polling  
D) Configure a dead letter queue  

---

### 3
A serverless application uses API Gateway with Lambda proxy integration. Users report receiving HTTP 502 errors intermittently.

What is the MOST likely cause?

A) API Gateway throttling limit exceeded  
B) Lambda function returning an incorrect response format  
C) Lambda function throwing an unhandled exception or timing out  
D) Missing CORS configuration  

---

### 4
A developer needs to grant a mobile application temporary credentials to upload files directly to S3 without embedding AWS access keys in the app.

Which approach should be used?

A) Create an IAM user and embed access keys in the app  
B) Use Cognito Identity Pool to exchange authenticated identity for temporary AWS credentials  
C) Generate S3 pre-signed URLs from a hardcoded IAM role ARN  
D) Store IAM credentials in AWS Systems Manager Parameter Store  

---

### 5
A DynamoDB table uses `userId` as the partition key. The application also needs to query users by email address, which is not the partition key.

What should the developer implement?

A) Scan the table filtering by email  
B) Create a Global Secondary Index with email as the partition key  
C) Create a Local Secondary Index with email as the sort key  
D) Use DynamoDB Streams to maintain a separate email lookup table  

---

### 6
A developer is implementing an event-driven architecture where multiple downstream services must react independently to the same S3 upload event.

Which pattern is MOST appropriate?

A) S3 → Lambda (single function calls all services)  
B) S3 → SNS → multiple SQS queues (each with its own Lambda consumer)  
C) S3 → SQS → Lambda (single queue, single consumer)  
D) S3 → EventBridge → Step Functions (sequential processing)  

---

### 7
A Lambda function needs to access an RDS database in a private subnet. The function currently cannot connect to the database.

Which configuration is required? (Select TWO.)

A) Attach the Lambda function to the same VPC and private subnets as RDS  
B) Assign a security group to the Lambda that allows outbound traffic to RDS  
C) Increase the Lambda timeout to 15 minutes  
D) Configure a NAT Gateway or VPC endpoint for the Lambda to reach AWS APIs  
E) Enable DynamoDB Streams on the RDS instance  

---

### 8
A developer wants to schedule a Lambda function to run every day at midnight UTC.

Which service should be used?

A) CloudWatch Events / EventBridge scheduled rule  
B) SQS delay queue  
C) Lambda Destinations  
D) Step Functions Wait state  

---

### 9
An application uses SQS FIFO queues for order processing. Which statement about FIFO queues is correct?

A) FIFO queues support unlimited throughput  
B) FIFO queues guarantee exactly-once processing and strict message ordering  
C) FIFO queues do not support dead letter queues  
D) FIFO queue names can be any valid SQS queue name  

---

### 10
A developer writes a Lambda handler that initializes a DynamoDB client inside the handler function (not in global scope). Performance is degraded on every invocation.

What explains this behavior?

A) DynamoDB throttling on every request  
B) Cold starts occur on every invocation because the client is recreated each time  
C) The SDK cannot reuse connections when initialized inside the handler  
D) Lambda does not cache anything between invocations  

---

### 11
A developer needs to implement retry logic when calling an external payment API that occasionally returns HTTP 503 errors.

Which pattern should be implemented in application code?

A) Retry immediately in an infinite loop until success  
B) Exponential backoff with jitter and a maximum retry count  
C) Store failed requests in S3 and process manually  
D) Use Step Functions exclusively for all HTTP calls  

---

### 12
A Lambda function is triggered by DynamoDB Streams. Some records fail processing while others in the same batch succeed.

How can the developer report partial batch failures?

A) Return a `batchItemFailures` list from the Lambda handler  
B) Delete the DynamoDB stream and recreate it  
C) Configure a dead letter queue on the DynamoDB table  
D) Use synchronous invocation instead of stream-based  

---

### 13
An API Gateway REST API uses a Cognito User Pool authorizer. Where does the Lambda function access authenticated user information?

A) `event.headers.Authorization`  
B) `event.requestContext.authorizer.claims`  
C) `event.body.userId`  
D) `context.identity.cognitoIdentityId`  

---

### 14
A developer needs to process real-time clickstream data with custom analytics logic before storing results in S3.

Which service should ingest the streaming data?

A) SQS Standard queue  
B) Amazon Kinesis Data Streams  
C) Amazon SNS  
D) AWS DataSync  

---

### 15
A serverless application uses EventBridge to route custom application events. A rule should trigger a Lambda function only when order events have an amount greater than $500.

How should the developer configure this?

A) Filter in Lambda code after receiving all events  
B) Configure an EventBridge rule with event pattern matching on the amount field  
C) Use SNS message filtering on a topic subscribed to by Lambda  
D) Configure SQS message attributes and filter in Lambda  

---

## Answer Key

See [answers.md](answers.md)
