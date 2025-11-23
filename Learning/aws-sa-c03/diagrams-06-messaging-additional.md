# AWS SAA-C03 - Messaging & Additional Services Flow Diagrams

## SNS vs SQS vs EventBridge Decision

```mermaid
flowchart TD
    Start([Message/Event Service]) --> Pattern{Communication Pattern?}
    
    Pattern --> |Pub/Sub<br/>Fan-out| PubSub[SNS - Simple Notification Service<br/>---<br/>📢 Publish-Subscribe<br/>🎯 1-to-Many<br/>⚡ Push-based<br/>🔔 Real-time Notifications<br/>---<br/>Features:<br/>• Topic-based<br/>• Multiple Subscribers<br/>• Filter Policies<br/>• Message Attributes<br/>• FIFO Topics<br/>---<br/>Protocols:<br/>• HTTP/HTTPS<br/>• Email/Email-JSON<br/>• SMS<br/>• SQS<br/>• Lambda<br/>• Mobile Push<br/>---<br/>💡 Notification Pattern]
    
    Pattern --> |Queue<br/>Decoupling| Queue[SQS - Simple Queue Service<br/>---<br/>📬 Message Queue<br/>🎯 1-to-1 Async<br/>📊 Pull-based<br/>⏱️ Buffering & Retry<br/>---<br/>Features:<br/>• Message Persistence<br/>• Dead Letter Queue<br/>• Visibility Timeout<br/>• Delay Queues<br/>• Long Polling<br/>---<br/>Types:<br/>• Standard: Best-effort order<br/>• FIFO: Exactly-once, ordered<br/>---<br/>💡 Decoupling Pattern]
    
    Pattern --> |Event-driven<br/>Complex Routing| EventDriven[EventBridge<br/>---<br/>🎯 Event Bus Service<br/>🔄 Complex Routing<br/>📊 Event Filtering<br/>🤖 Schema Registry<br/>---<br/>Features:<br/>• Event Rules<br/>• Content-based Filtering<br/>• Multiple Targets<br/>• Archive & Replay<br/>• Cross-Account Events<br/>---<br/>Sources:<br/>• AWS Services<br/>• SaaS Partners<br/>• Custom Applications<br/>---<br/>💡 Serverless Integration]
    
    PubSub --> SNSDetails[SNS Configuration<br/>---<br/>Topic Types:<br/>1️⃣ Standard Topic<br/>   • Unlimited Throughput<br/>   • Best-effort Ordering<br/>   • At-least-once Delivery<br/>---<br/>2️⃣ FIFO Topic<br/>   • Ordered Messages<br/>   • Exactly-once Delivery<br/>   • 300 msg/sec Default<br/>   • 3,000 msg/sec Batching<br/>---<br/>Message Size: 256 KB<br/>Retention: No persistence<br/>---<br/>💰 Pricing:<br/>• $0.50 per million requests<br/>• HTTP/S: $0.06 per 100k<br/>• Data Transfer charges]
    
    Queue --> SQSDetails[SQS Configuration<br/>---<br/>Standard Queue:<br/>📊 Unlimited Throughput<br/>⚡ At-least-once Delivery<br/>🔄 Best-effort Ordering<br/>💰 Lowest Cost<br/>---<br/>FIFO Queue:<br/>📊 3,000 msg/sec<br/>✅ Exactly-once Processing<br/>📋 Strict Ordering<br/>🔑 Deduplication ID<br/>🎯 Message Group ID<br/>💰 Higher Cost<br/>---<br/>Message Size: 256 KB<br/>Extended: Up to 2 GB via S3<br/>Retention: 1 min - 14 days<br/>Default: 4 days]
    
    EventDriven --> EBDetails[EventBridge Details<br/>---<br/>Event Buses:<br/>1️⃣ Default Bus AWS Events<br/>2️⃣ Custom Bus Your Events<br/>3️⃣ Partner Bus SaaS<br/>---<br/>Event Rules:<br/>• Event Pattern Matching<br/>• Schedule Cron/Rate<br/>• Content Filtering<br/>---<br/>Targets 5 per rule:<br/>• Lambda<br/>• Step Functions<br/>• SNS/SQS<br/>• Kinesis<br/>• ECS Tasks<br/>• 30+ Services<br/>---<br/>💰 $1 per million events]
    
    SNSDetails --> SNSUseCase[SNS Use Cases<br/>---<br/>✅ Application Alerts<br/>✅ Mobile Notifications<br/>✅ System Notifications<br/>✅ Fan-out to Services<br/>✅ SMS Alerts<br/>✅ Email Notifications<br/>---<br/>Patterns:<br/>SNS → SQS Fan-out<br/>SNS → Lambda Processing<br/>SNS → HTTP Webhooks<br/>---<br/>💡 Real-time Notifications]
    
    SQSDetails --> SQSUseCase[SQS Use Cases<br/>---<br/>✅ Decouple Microservices<br/>✅ Buffer Write Operations<br/>✅ Batch Processing<br/>✅ Async Task Processing<br/>✅ Load Leveling<br/>✅ Retry Logic<br/>---<br/>Patterns:<br/>Producer → SQS → Consumer<br/>SNS → SQS → Lambda<br/>Web → SQS → Workers<br/>---<br/>💡 Reliable Messaging]
    
    EBDetails --> EBUseCase[EventBridge Use Cases<br/>---<br/>✅ Serverless Workflows<br/>✅ Cross-Account Events<br/>✅ SaaS Integration<br/>✅ Event Replay<br/>✅ Scheduled Tasks<br/>✅ Complex Routing<br/>---<br/>Patterns:<br/>AWS Service → EventBridge → Multiple Targets<br/>Custom App → EventBridge → Orchestration<br/>Schedule → EventBridge → Lambda<br/>---<br/>💡 Event-Driven Architecture]
    
    style PubSub fill:#FF6B6B
    style Queue fill:#4CAF50
    style EventDriven fill:#2196F3
```

## SQS Queue Configuration Deep Dive

```mermaid
flowchart TD
    Start([Create SQS Queue]) --> QueueType{Queue Type?}
    
    QueueType --> |Unordered<br/>High Throughput| Standard[Standard Queue<br/>---<br/>⚡ Unlimited Throughput<br/>📊 At-least-once Delivery<br/>🔄 Best-effort Ordering<br/>💡 May have Duplicates<br/>---<br/>Performance:<br/>• Nearly Unlimited TPS<br/>• Low Latency <10ms<br/>---<br/>💰 Most Cost-Effective<br/>💡 Default Choice]
    
    QueueType --> |Ordered<br/>Exactly-once| FIFO[FIFO Queue<br/>---<br/>📋 Strict Ordering<br/>✅ Exactly-once Processing<br/>🎯 Message Grouping<br/>🔑 Deduplication<br/>---<br/>Performance:<br/>• 300 msgs/sec Default<br/>• 3,000 msgs/sec Batching<br/>---<br/>Name: Must end with .fifo<br/>💰 Higher Cost<br/>💡 Critical Ordering]
    
    Standard --> Settings
    FIFO --> Settings
    
    Settings[Queue Settings<br/>---<br/>📊 Message Retention:<br/>• Default: 4 Days<br/>• Min: 1 Minute<br/>• Max: 14 Days<br/>---<br/>📏 Message Size:<br/>• Max: 256 KB<br/>• Extended via S3: 2 GB<br/>---<br/>⏱️ Visibility Timeout:<br/>• Default: 30 Seconds<br/>• Max: 12 Hours<br/>---<br/>⏳ Delivery Delay:<br/>• 0 - 15 Minutes<br/>• Per Queue or Message]
    
    Settings --> VisibilityTimeout[Visibility Timeout<br/>---<br/>🎯 Hide During Processing<br/>⏱️ Consumer Processing Time<br/>🔄 Reappear if Not Deleted<br/>---<br/>Process:<br/>1️⃣ Consumer Receives Message<br/>2️⃣ Message Hidden Timeout<br/>3️⃣ Consumer Processes<br/>4️⃣ Consumer Deletes<br/>---<br/>If Not Deleted:<br/>⏱️ After Timeout Expires<br/>🔄 Visible Again<br/>📊 Receive Count Increments<br/>---<br/>Best Practice:<br/>Set > Max Processing Time<br/>Use ChangeMessageVisibility]
    
    VisibilityTimeout --> Polling{Polling Method?}
    
    Polling --> |Default<br/>Immediate| ShortPoll[Short Polling<br/>---<br/>⚡ Returns Immediately<br/>📊 Samples Subset of Servers<br/>💡 Empty Response Possible<br/>---<br/>WaitTimeSeconds: 0<br/>---<br/>Characteristics:<br/>• More API Calls<br/>• Higher Cost<br/>• May Miss Messages<br/>• Lower Latency<br/>---<br/>❌ Not Recommended<br/>💡 Use Long Polling]
    
    Polling --> |Recommended<br/>Wait for Messages| LongPoll[Long Polling<br/>---<br/>⏱️ Wait for Messages<br/>📊 Queries All Servers<br/>💰 Reduces API Calls<br/>✅ Fewer Empty Responses<br/>---<br/>WaitTimeSeconds: 1-20<br/>Recommended: 20<br/>---<br/>Benefits:<br/>• Lower Cost<br/>• Reduced Empty Responses<br/>• Better for Consumers<br/>---<br/>✅ Best Practice<br/>💡 Always Enable]
    
    ShortPoll --> DLQ
    LongPoll --> DLQ
    
    DLQ[Dead Letter Queue DLQ<br/>---<br/>⚰️ Failed Message Handling<br/>🔄 After Max Receives<br/>📊 Troubleshooting Aid<br/>---<br/>Configuration:<br/>• Source Queue<br/>• DLQ Target<br/>• maxReceiveCount: 1-1000<br/>---<br/>Process:<br/>1️⃣ Message Fails Processing<br/>2️⃣ Receive Count Increments<br/>3️⃣ Exceeds maxReceiveCount<br/>4️⃣ Moved to DLQ<br/>---<br/>DLQ Retention:<br/>Same as Source<br/>---<br/>💡 Essential for Production]
    
    DLQ --> Redrive[Redrive Policy<br/>---<br/>🔄 Move Back from DLQ<br/>🔧 After Issue Fixed<br/>---<br/>Redrive Options:<br/>1️⃣ Redrive to Source<br/>2️⃣ Redrive to Custom Queue<br/>---<br/>Use Cases:<br/>• Bug Fixed<br/>• Service Restored<br/>• Reprocess Messages<br/>---<br/>Console Feature:<br/>Redrive Messages Button]
    
    Redrive --> DelayQueue[Delay Queues<br/>---<br/>⏳ Postpone Delivery<br/>⏱️ 0 - 15 Minutes<br/>---<br/>Levels:<br/>1️⃣ Queue-level Default<br/>2️⃣ Message-level Override<br/>---<br/>Use Cases:<br/>• Rate Limiting<br/>• Time-based Processing<br/>• Staged Workflows<br/>---<br/>Example:<br/>Order → 5 min delay → Process]
    
    DelayQueue --> MessageAttributes[Message Attributes<br/>---<br/>🏷️ Metadata Key-Value<br/>📊 Up to 10 Attributes<br/>💡 Filter & Route<br/>---<br/>Types:<br/>• String<br/>• Number<br/>• Binary<br/>---<br/>Use Cases:<br/>• Message Filtering<br/>• Routing Logic<br/>• Processing Hints<br/>• Priority Handling<br/>---<br/>Not Counted in Size]
    
    MessageAttributes --> Security[Security Features<br/>---<br/>🔐 Encryption at Rest:<br/>• SSE-SQS AWS Managed<br/>• SSE-KMS Customer Key<br/>---<br/>🔐 Encryption in Transit:<br/>• HTTPS Endpoints<br/>---<br/>🛡️ Access Control:<br/>• IAM Policies<br/>• SQS Access Policies<br/>• VPC Endpoints<br/>---<br/>📋 CloudTrail Logging:<br/>• API Call Audit<br/>---<br/>💡 Enable for Production]
    
    Security --> Monitoring[SQS Monitoring<br/>---<br/>📊 CloudWatch Metrics:<br/>• ApproximateNumberOfMessages<br/>• ApproximateAgeOfOldestMessage<br/>• NumberOfMessagesSent<br/>• NumberOfMessagesReceived<br/>• NumberOfMessagesDeleted<br/>• NumberOfEmptyReceives<br/>---<br/>⚠️ Alarms:<br/>• Queue Depth High<br/>• Old Messages Stuck<br/>• Consumer Lag<br/>---<br/>💡 Monitor Queue Health]
    
    style Standard fill:#4CAF50
    style FIFO fill:#FF6B6B
    style LongPoll fill:#2196F3
    style DLQ fill:#FFC107
```

## Step Functions State Machine

```mermaid
flowchart TD
    Start([Start Execution]) --> StateMachine[AWS Step Functions<br/>---<br/>🔄 Orchestration Service<br/>📊 Visual Workflow<br/>🎯 Serverless Coordination<br/>---<br/>Types:<br/>1️⃣ Standard Workflows<br/>2️⃣ Express Workflows]
    
    StateMachine --> WorkflowType{Workflow Type?}
    
    WorkflowType --> |Long-running<br/>Exactly-once| StandardWF[Standard Workflows<br/>---<br/>⏱️ Max Duration: 1 Year<br/>✅ Exactly-once Execution<br/>📊 Full Execution History<br/>💾 Audit Trail<br/>---<br/>Features:<br/>• Visual Debugging<br/>• Step-by-step Execution<br/>• Automatic Retries<br/>• Error Handling<br/>---<br/>💰 Pricing:<br/>$0.025 per 1,000 transitions<br/>---<br/>💡 Long-running Processes]
    
    WorkflowType --> |High-volume<br/>At-least-once| ExpressWF[Express Workflows<br/>---<br/>⏱️ Max Duration: 5 Minutes<br/>📊 At-least-once Execution<br/>⚡ High Throughput<br/>💰 Low Cost<br/>---<br/>Sub-types:<br/>• Synchronous: Wait for result<br/>• Asynchronous: Fire & forget<br/>---<br/>💰 Pricing:<br/>$1 per 1M executions<br/>$0.00001667 per GB-second<br/>---<br/>💡 IoT, Streaming, Mobile]
    
    StandardWF --> States
    ExpressWF --> States
    
    States[State Types<br/>---<br/>Available States:]
    
    States --> Task[Task State<br/>---<br/>⚙️ Do Work<br/>🎯 Single Unit<br/>---<br/>Integrations:<br/>• Lambda Function<br/>• ECS/Fargate Task<br/>• Batch Job<br/>• SNS/SQS<br/>• DynamoDB<br/>• Glue Job<br/>• SageMaker<br/>• Step Functions Nested<br/>---<br/>💡 Most Common State]
    
    States --> Choice[Choice State<br/>---<br/>🔀 Conditional Logic<br/>📊 Branch Execution<br/>---<br/>Operators:<br/>• StringEquals<br/>• NumericGreaterThan<br/>• BooleanEquals<br/>• TimestampEquals<br/>• And/Or/Not<br/>---<br/>Example:<br/>If status == "approved"<br/>  → ProcessOrder<br/>Else<br/>  → RejectOrder]
    
    States --> Parallel[Parallel State<br/>---<br/>⚡ Concurrent Execution<br/>🔄 Multiple Branches<br/>⏱️ Wait for All<br/>---<br/>Use Cases:<br/>• Independent Tasks<br/>• Fan-out Processing<br/>• Parallel API Calls<br/>---<br/>Example:<br/>Process Order:<br/>├─ Update Inventory<br/>├─ Charge Payment<br/>└─ Send Notification]
    
    States --> Wait[Wait State<br/>---<br/>⏱️ Delay Execution<br/>---<br/>Wait Types:<br/>1️⃣ Seconds: Fixed Duration<br/>2️⃣ Timestamp: Until Time<br/>3️⃣ SecondsPath: Dynamic<br/>4️⃣ TimestampPath: Dynamic<br/>---<br/>Use Cases:<br/>• Rate Limiting<br/>• Polling Intervals<br/>• Scheduled Actions]
    
    States --> Succeed[Succeed State<br/>---<br/>✅ Successful Termination<br/>🎯 End Execution<br/>💡 Explicit Success]
    
    States --> Fail[Fail State<br/>---<br/>❌ Failed Termination<br/>⚠️ Error & Cause<br/>💡 Explicit Failure]
    
    States --> Pass[Pass State<br/>---<br/>📊 Transform Data<br/>🔄 Pass Through<br/>💡 Testing & Debugging]
    
    States --> Map[Map State<br/>---<br/>🔄 Iterate Over Items<br/>📊 Process Array<br/>⚡ Parallel Processing<br/>---<br/>Configuration:<br/>• MaxConcurrency<br/>• Iterator Definition<br/>---<br/>Example:<br/>For each item in orders:<br/>  ProcessOrder item]
    
    Task --> ErrorHandling[Error Handling<br/>---<br/>🔄 Retry Configuration:<br/>• ErrorEquals: Error Types<br/>• IntervalSeconds: Delay<br/>• MaxAttempts: Retry Count<br/>• BackoffRate: Multiplier<br/>---<br/>⚠️ Catch Configuration:<br/>• ErrorEquals: Error Types<br/>• Next: Fallback State<br/>• ResultPath: Error Info<br/>---<br/>Error Types:<br/>• States.ALL<br/>• States.Timeout<br/>• States.TaskFailed<br/>• Custom Errors]
    
    ErrorHandling --> Integration[Service Integrations<br/>---<br/>Integration Patterns:<br/>---<br/>1️⃣ Request-Response Default<br/>   • Call & Continue<br/>   • Async Processing<br/>---<br/>2️⃣ Run Job .sync<br/>   • Wait for Completion<br/>   • Sync Processing<br/>---<br/>3️⃣ Wait for Callback .waitForTaskToken<br/>   • Pause Until Callback<br/>   • Human Approval<br/>   • External System]
    
    Integration --> UseCases[Step Functions Use Cases<br/>---<br/>✅ Order Processing:<br/>├─ Validate Order<br/>├─ Check Inventory<br/>├─ Process Payment<br/>├─ Ship Order<br/>└─ Send Confirmation<br/>---<br/>✅ Data Processing:<br/>├─ Extract from S3<br/>├─ Transform with Lambda<br/>├─ Load to Database<br/>└─ Send Report<br/>---<br/>✅ Human Approval:<br/>├─ Submit Request<br/>├─ Wait for Approval<br/>├─ Process if Approved<br/>└─ Notify Result<br/>---<br/>💡 Complex Workflows]
    
    style StandardWF fill:#4CAF50
    style ExpressWF fill:#FF6B6B
    style Task fill:#2196F3
    style Parallel fill:#9C27B0
```

## API Gateway Architecture

```mermaid
flowchart LR
    Client([API Client<br/>Web/Mobile/IoT]) --> APIGW[API Gateway<br/>---<br/>🚪 Entry Point<br/>🔒 Security<br/>⚡ Throttling<br/>💰 Pricing Model]
    
    APIGW --> APIType{API Type?}
    
    APIType --> REST[REST API<br/>---<br/>📡 RESTful APIs<br/>🌐 HTTP Protocol<br/>🎯 Full Features<br/>---<br/>Endpoint Types:<br/>• Edge-Optimized<br/>• Regional<br/>• Private<br/>---<br/>Features:<br/>• Resource Policies<br/>• Usage Plans<br/>• API Keys<br/>• Request Validation<br/>• SDK Generation<br/>---<br/>💰 $3.50 per million<br/>💡 Most Flexible]
    
    APIType --> HTTP[HTTP API<br/>---<br/>⚡ Low Latency<br/>💰 70% Cheaper<br/>🎯 Simplified<br/>---<br/>Features:<br/>• OIDC/OAuth2<br/>• CORS Built-in<br/>• Auto-deploy<br/>---<br/>Missing:<br/>❌ Usage Plans<br/>❌ API Keys<br/>❌ Request Validation<br/>---<br/>💰 $1.00 per million<br/>💡 Modern APIs]
    
    APIType --> WebSocket[WebSocket API<br/>---<br/>🔄 Bi-directional<br/>⚡ Real-time<br/>🎯 Persistent Connection<br/>---<br/>Routes:<br/>• $connect<br/>• $disconnect<br/>• $default<br/>• Custom routes<br/>---<br/>Use Cases:<br/>• Chat Applications<br/>• Gaming<br/>• Trading<br/>• Collaboration<br/>---<br/>💰 $1.00 per million<br/>💡 Real-time Apps]
    
    REST --> Integration{Backend Integration?}
    HTTP --> Integration
    
    Integration --> Lambda[Lambda Integration<br/>---<br/>⚙️ AWS Lambda Function<br/>🎯 Serverless Backend<br/>---<br/>Types:<br/>1️⃣ Lambda Proxy Default<br/>   • Pass All Data<br/>   • Lambda Returns Format<br/>---<br/>2️⃣ Lambda Custom<br/>   • Transform Request<br/>   • Transform Response<br/>---<br/>💡 Most Common]
    
    Integration --> AWSAPI[AWS Service Integration<br/>---<br/>🔗 Direct AWS Service<br/>📊 No Lambda Needed<br/>---<br/>Services:<br/>• DynamoDB<br/>• SNS/SQS<br/>• S3<br/>• Step Functions<br/>• Kinesis<br/>---<br/>Benefits:<br/>• Lower Latency<br/>• Lower Cost<br/>• Simplified<br/>---<br/>💡 Simple Integrations]
    
    Integration --> HTTP_Backend[HTTP Integration<br/>---<br/>🌐 HTTP Endpoint<br/>💻 Any HTTP Backend<br/>---<br/>Targets:<br/>• On-premises<br/>• EC2<br/>• ALB/NLB<br/>• Other Cloud<br/>• 3rd Party APIs<br/>---<br/>Types:<br/>• HTTP Proxy<br/>• HTTP Custom<br/>---<br/>💡 Existing Services]
    
    Integration --> Mock[Mock Integration<br/>---<br/>🧪 Testing<br/>📝 Development<br/>💡 No Backend Needed<br/>---<br/>Returns:<br/>• Static Response<br/>• Configurable<br/>---<br/>Use Cases:<br/>• API Development<br/>• Frontend Testing<br/>• Demonstrations]
    
    Lambda --> Features
    AWSAPI --> Features
    HTTP_Backend --> Features
    Mock --> Features
    
    Features[API Gateway Features<br/>---<br/>🔒 Security:<br/>• IAM Authorization<br/>• Cognito User Pools<br/>• Lambda Authorizer<br/>• API Keys<br/>• Resource Policies<br/>• WAF Integration<br/>---<br/>⚡ Performance:<br/>• Caching 0.5GB-237GB<br/>• Throttling<br/>• Request/Response Transform<br/>---<br/>📊 Monitoring:<br/>• CloudWatch Logs<br/>• CloudWatch Metrics<br/>• X-Ray Tracing<br/>• Access Logs]
    
    Features --> Throttling[Throttling & Quotas<br/>---<br/>Account Limits:<br/>📊 10,000 RPS Default<br/>📈 Burst: 5,000 Requests<br/>---<br/>Levels:<br/>1️⃣ Account Level<br/>2️⃣ API/Stage Level<br/>3️⃣ Method Level<br/>4️⃣ Usage Plan Level<br/>---<br/>Errors:<br/>• 429 Too Many Requests<br/>---<br/>Best Practice:<br/>• Set Limits<br/>• Use Usage Plans<br/>• Monitor CloudWatch]
    
    Throttling --> Caching[Response Caching<br/>---<br/>💾 Cache API Responses<br/>⚡ Reduce Backend Calls<br/>💰 Lower Costs<br/>---<br/>Cache Sizes:<br/>• 0.5 GB - 237 GB<br/>---<br/>TTL:<br/>• 0 - 3,600 Seconds<br/>• Default: 300 Seconds<br/>---<br/>Invalidation:<br/>• Flush Entire Cache<br/>• Per-Client Optional<br/>---<br/>💰 Hourly Charges<br/>💡 Read-Heavy APIs]
    
    Caching --> Stages[Deployment Stages<br/>---<br/>🎯 Environment Separation<br/>🔄 Version Management<br/>---<br/>Common Stages:<br/>• dev<br/>• test<br/>• staging<br/>• prod<br/>---<br/>Stage Variables:<br/>• Environment Config<br/>• Backend URLs<br/>• Lambda Aliases<br/>---<br/>Features:<br/>• Stage-level Settings<br/>• Canary Deployments<br/>• Stage Overrides]
    
    Stages --> Canary[Canary Deployments<br/>---<br/>🐦 Gradual Rollout<br/>📊 Traffic Splitting<br/>⚠️ Risk Mitigation<br/>---<br/>Configuration:<br/>• % Traffic to Canary<br/>• 0-50% Recommended<br/>• Stage Variables<br/>---<br/>Process:<br/>1️⃣ Deploy to Canary<br/>2️⃣ Monitor Metrics<br/>3️⃣ Promote or Rollback<br/>---<br/>💡 Production Deployments]
    
    style REST fill:#4CAF50
    style HTTP fill:#2196F3
    style Lambda fill:#FF6B6B
    style Caching fill:#FFC107
```

## Exam Scenarios Summary

```mermaid
mindmap
  root((AWS SAA-C03<br/>Key Scenarios))
    High Availability
      Multi-AZ RDS
      ALB + Auto Scaling
      S3 Cross-Region Replication
      Route 53 Failover
      Aurora Global Database
    Cost Optimization
      Reserved Instances
      Spot Instances
      S3 Intelligent-Tiering
      Lambda vs EC2
      CloudFront for Static
      RDS Reserved Instances
    Performance
      CloudFront CDN
      ElastiCache Redis/Memcached
      DynamoDB DAX
      EBS Provisioned IOPS
      Read Replicas
      Lambda Provisioned Concurrency
    Security
      IAM Roles not Keys
      KMS Encryption
      VPC Private Subnets
      Security Groups Layered
      CloudTrail Enabled
      S3 Block Public Access
    Disaster Recovery
      Backup to S3
      Cross-Region Replication
      Multi-Region Deployment
      Route 53 Failover
      Aurora Global Tables
      DynamoDB Global Tables
    Decoupling
      SQS Queues
      SNS Topics
      EventBridge
      Step Functions
      Lambda Async
      API Gateway
    Scalability
      Auto Scaling Groups
      DynamoDB On-Demand
      Lambda Auto-Scale
      Aurora Serverless
      S3 Unlimited
      CloudFront
    Monitoring
      CloudWatch Metrics
      CloudWatch Alarms
      CloudWatch Logs
      X-Ray Tracing
      Config Rules
      CloudTrail Audit
```

## Common Architecture Patterns

```mermaid
flowchart TB
    subgraph Pattern1 [Three-Tier Web App]
        User1([Users]) --> CF1[CloudFront]
        CF1 --> ALB1[Application<br/>Load Balancer]
        ALB1 --> ASG1[Auto Scaling<br/>Group]
        ASG1 --> RDS1[(RDS Multi-AZ<br/>Primary + Standby)]
        ASG1 --> ElastiCache1[(ElastiCache<br/>Session Store)]
        S3_1[S3 Bucket<br/>Static Assets] --> CF1
    end
    
    subgraph Pattern2 [Serverless App]
        User2([Users]) --> CF2[CloudFront]
        CF2 --> S3_2[S3 Static<br/>Website]
        S3_2 --> APIGW[API Gateway]
        APIGW --> Lambda[Lambda<br/>Functions]
        Lambda --> DDB[(DynamoDB<br/>Tables)]
        Lambda --> S3_3[S3<br/>Data Storage]
    end
    
    subgraph Pattern3 [Event-Driven]
        Source[Event Source<br/>S3, DynamoDB] --> EventBridge[EventBridge<br/>Event Bus]
        EventBridge --> Lambda3[Lambda<br/>Processing]
        EventBridge --> SQS3[SQS<br/>Queue]
        EventBridge --> SNS3[SNS<br/>Notifications]
        SQS3 --> EC2_3[EC2<br/>Workers]
        Lambda3 --> DDB3[(DynamoDB)]
    end
    
    subgraph Pattern4 [Data Processing]
        S3Source[S3<br/>Data Lake] --> Glue[AWS Glue<br/>ETL]
        Glue --> S3Processed[S3<br/>Processed Data]
        S3Processed --> Athena[Athena<br/>SQL Queries]
        S3Processed --> Redshift[(Redshift<br/>Data Warehouse)]
        Athena --> QuickSight[QuickSight<br/>BI Dashboards]
        Redshift --> QuickSight
    end
    
    style Pattern1 fill:#e1f5e1
    style Pattern2 fill:#e1e5f5
    style Pattern3 fill:#f5e1e1
    style Pattern4 fill:#f5f5e1
```
