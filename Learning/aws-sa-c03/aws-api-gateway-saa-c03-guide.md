# AWS API Gateway - SAA-C03 Certification Guide

## Table of Contents
1. [Introduction and Overview](#introduction-and-overview)
2. [API Gateway Types](#api-gateway-types)
3. [Core Features and Integrations](#core-features-and-integrations)
4. [Security Features](#security-features)
5. [Monitoring and Logging](#monitoring-and-logging)
6. [Deployment and Stages](#deployment-and-stages)
7. [Cost Optimization and Best Practices](#cost-optimization-and-best-practices)
8. [Exam-Focused Key Points](#exam-focused-key-points)
9. [AWS CLI Commands Reference](#aws-cli-commands-reference)
10. [Common Scenarios and Use Cases](#common-scenarios-and-use-cases)

---

## Introduction and Overview

### What is Amazon API Gateway?

Amazon API Gateway is a fully managed service that makes it easy for developers to create, publish, maintain, monitor, and secure APIs at any scale. It acts as a "front door" for applications to access data, business logic, or functionality from backend services, such as workloads running on Amazon EC2, code running on AWS Lambda, web applications, or real-time communication apps.

### Key Benefits for SAA-C03 Context

1. **Serverless Architecture**: Enables building serverless applications when combined with Lambda
2. **Scalability**: Automatically scales to handle traffic spikes without manual intervention
3. **Cost-Effectiveness**: Pay-per-use pricing model with no upfront costs
4. **Security**: Built-in security features including authentication, authorization, and DDoS protection
5. **Integration**: Seamless integration with AWS services and third-party systems
6. **Monitoring**: Native CloudWatch integration for comprehensive monitoring

### Core Architecture Components

- **API**: A collection of resources and methods integrated with backend HTTP endpoints or AWS services
- **Resources**: Logical entities that an API exposes (e.g., `/users`, `/orders`)
- **Methods**: HTTP verbs (GET, POST, PUT, DELETE) that define operations on resources
- **Stages**: Named references to deployments of an API
- **Models**: Data schemas used for request/response validation and documentation

### When to Use API Gateway

✅ **Use API Gateway when:**
- Building microservices architectures
- Creating serverless applications with Lambda
- Need centralized API management and security
- Require request/response transformation
- Want built-in caching and throttling
- Need detailed API analytics and monitoring

❌ **Consider alternatives when:**
- Ultra-low latency requirements (consider ALB)
- Simple proxy scenarios without API features
- Internal-only APIs within VPC (consider private APIs or ALB)

---

## API Gateway Types

### 1. REST APIs

**Overview**: Feature-rich APIs with comprehensive management capabilities, supporting OpenAPI specifications.

**Key Features**:
- Request/response transformation
- SDK generation
- API caching
- Request validation
- Documentation generation
- Custom domain names with SSL/TLS

**Integration Types**:
- **Lambda Function**: Direct integration with AWS Lambda
- **HTTP**: Integration with HTTP endpoints
- **AWS Service**: Direct integration with AWS services (S3, DynamoDB, etc.)
- **Mock**: Return static responses without backend calls
- **VPC Link**: Connect to resources in VPC

**Pricing**: Pay per API call + data transfer

**Use Cases**:
- Complex API requirements with transformations
- Need for caching and detailed request validation
- SDK generation for mobile/web applications
- Legacy system integration

### 2. HTTP APIs

**Overview**: Optimized for serverless workloads and HTTP backends, offering better performance and lower cost than REST APIs.

**Key Features**:
- Native OpenID Connect and OAuth 2.0 support
- Built-in CORS support
- Automatic deployments
- Better performance (up to 70% cost reduction vs REST APIs)
- JWT authorizers

**Limitations Compared to REST APIs**:
- No request/response transformation
- No caching
- No SDK generation
- No request validation

**Integration Types**:
- Lambda functions
- HTTP endpoints
- AWS services (limited compared to REST APIs)

**Use Cases**:
- Simple proxy to Lambda functions
- Cost-sensitive applications
- Serverless-first architectures
- Modern authentication requirements

### 3. WebSocket APIs

**Overview**: Enable real-time, full-duplex communication between clients and backend services.

**Key Features**:
- Persistent connections
- Real-time messaging
- Route-based message handling
- Integration with Lambda, HTTP endpoints, AWS services

**Connection Management**:
- **$connect**: Handle new connection requests
- **$disconnect**: Handle connection terminations
- **$default**: Handle messages not matching specific routes
- **Custom routes**: Handle specific message types

**Use Cases**:
- Real-time chat applications
- Live notifications and updates
- Gaming applications
- IoT device communication
- Financial trading platforms

### Comparison Matrix

| Feature | REST API | HTTP API | WebSocket API |
|---------|----------|----------|---------------|
| Cost | Higher | Lower (up to 70% savings) | Per connection + message |
| Performance | Standard | Optimized | Real-time |
| Caching | ✅ | ❌ | ❌ |
| Request Validation | ✅ | ❌ | ❌ |
| Transformations | ✅ | ❌ | Limited |
| SDK Generation | ✅ | ❌ | ❌ |
| CORS | Manual setup | Built-in | N/A |
| Auth Methods | Multiple | JWT, OAuth 2.0 | Custom, IAM |
| Use Case | Complex APIs | Simple proxies | Real-time apps |

---

## Core Features and Integrations

### Request and Response Handling

#### Request Processing Flow
1. **Client Request** → API Gateway receives the request
2. **Authentication/Authorization** → Validates credentials and permissions
3. **Request Validation** → Validates request against defined schema (REST API only)
4. **Request Transformation** → Transforms request format if needed (REST API only)
5. **Backend Integration** → Forwards request to backend service
6. **Response Transformation** → Transforms response format if needed (REST API only)
7. **Client Response** → Returns response to client

#### Request Validation (REST APIs)
- **Schema Validation**: Validate request body against JSON schema
- **Parameter Validation**: Validate query parameters, headers, path parameters
- **Required Fields**: Ensure required fields are present
- **Data Types**: Validate field data types and formats

```json
{
  "$schema": "http://json-schema.org/draft-04/schema#",
  "title": "User Schema",
  "type": "object",
  "properties": {
    "name": { "type": "string", "minLength": 1 },
    "email": { "type": "string", "format": "email" },
    "age": { "type": "integer", "minimum": 0 }
  },
  "required": ["name", "email"]
}
```

### Caching (REST APIs Only)

#### Cache Configuration
- **Cache Key**: Based on request parameters, headers, or query strings
- **TTL (Time To Live)**: 0 seconds to 1 hour (3600 seconds)
- **Cache Capacity**: 0.5GB, 1.6GB, 6.1GB, 13.5GB, 28.4GB, 58.2GB, 118GB, 237GB
- **Per-Key Invalidation**: Invalidate specific cache entries
- **Cache Encryption**: Data encrypted at rest and in transit

#### Cache Benefits
- **Performance**: Reduced latency for cached responses
- **Cost Savings**: Reduced backend calls
- **Scalability**: Handle traffic spikes with cached responses

### Request Throttling

#### Throttling Levels
1. **Account Level**: Default limits across all APIs
2. **Stage Level**: Limits for specific deployment stages  
3. **Method Level**: Limits for individual API methods
4. **Client Level**: Per-client limits using API keys or usage plans

#### Throttling Parameters
- **Rate**: Requests per second (steady-state rate)
- **Burst**: Maximum requests in burst period
- **Quota**: Total requests allowed over specified time period

#### Throttling Responses
- **429 Too Many Requests**: When rate limits exceeded
- **Retry-After Header**: Indicates when client can retry

### AWS Service Integrations

#### Direct Service Integration
API Gateway can directly integrate with AWS services without Lambda:

**Supported Services**:
- **DynamoDB**: Read/write operations
- **S3**: Object operations, presigned URLs
- **SNS**: Publish messages
- **SQS**: Send messages
- **Step Functions**: Start executions
- **Kinesis**: Put records
- **CloudWatch**: Put metrics

**Example: DynamoDB Integration**
```json
{
  "httpMethod": "POST",
  "resourcePath": "/users",
  "integrationHttpMethod": "POST",
  "type": "AWS",
  "uri": "arn:aws:apigateway:region:dynamodb:action/PutItem",
  "credentials": "arn:aws:iam::account:role/APIGatewayDynamoDBRole"
}
```

#### Lambda Integration Types

**Lambda Proxy Integration** (Recommended):
- Lambda receives entire request object
- Lambda must return specific response format
- Simpler configuration, more flexible

**Lambda Custom Integration**:
- Configure request/response mapping
- More control over data transformation
- More complex configuration

### Request/Response Transformation (REST APIs)

#### Velocity Template Language (VTL)
Used for mapping templates to transform requests/responses:

**Request Mapping Example**:
```vtl
{
  "userId": "$input.params('id')",
  "body": $input.json('$'),
  "headers": {
    #foreach($header in $input.params().header.keySet())
    "$header": "$util.escapeJavaScript($input.params().header.get($header))"
    #if($foreach.hasNext),#end
    #end
  }
}
```

**Response Mapping Example**:
```vtl
{
  "message": "$input.path('$.message')",
  "statusCode": 200,
  "timestamp": "$context.requestTime"
}
```

### Error Handling

#### Gateway Responses
- **4XX Client Errors**: Bad request, unauthorized, forbidden, not found
- **5XX Server Errors**: Internal server error, bad gateway, service unavailable
- **Gateway Timeout**: 29-second timeout limit

#### Custom Error Responses
- Customize error message format
- Add custom headers
- Transform error responses using VTL templates

### CORS (Cross-Origin Resource Sharing)

#### REST APIs - Manual Configuration
```json
{
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key",
  "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS"
}
```

#### HTTP APIs - Built-in Support
- Automatic OPTIONS method handling
- Configurable CORS settings
- Preflight request support

---

## Security Features

### Authentication Methods

#### 1. IAM Authentication
**How it works**:
- Uses AWS Signature Version 4 (SigV4) signing process
- Requests signed with AWS credentials (Access Key ID + Secret Access Key)
- API Gateway verifies signature and IAM permissions

**Use Cases**:
- Internal AWS services communication
- Admin/management APIs
- Backend-to-backend communication

**Benefits**:
- No additional infrastructure required
- Leverages existing IAM policies
- Fine-grained permissions

**Limitations**:
- Requires AWS SDK or manual signature creation
- Not suitable for public-facing APIs

#### 2. Cognito User Pools
**How it works**:
- Users authenticate with Cognito User Pool
- Receive JWT tokens (ID token, access token)
- API Gateway validates JWT token signature and claims

**Use Cases**:
- User-facing applications
- Mobile and web applications
- Social identity federation

**Configuration**:
```json
{
  "type": "COGNITO_USER_POOLS",
  "authorizerUri": "arn:aws:cognito-idp:region:account:userpool/pool-id",
  "identitySource": "method.request.header.Authorization"
}
```

#### 3. Lambda Authorizers (Custom Authorizers)

**Token-based Authorizer**:
- Receives bearer token
- Returns IAM policy and principal ID
- Supports caching for performance

**Request-based Authorizer**:
- Receives entire request context
- More flexible but no caching
- Useful for complex authorization logic

**Example Lambda Authorizer Response**:
```json
{
  "principalId": "user123",
  "policyDocument": {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Action": "execute-api:Invoke",
        "Effect": "Allow",
        "Resource": "arn:aws:execute-api:region:account:api-id/stage/method/resource-path"
      }
    ]
  },
  "context": {
    "stringKey": "value",
    "numberKey": 123,
    "booleanKey": true
  }
}
```

#### 4. API Keys

**Purpose**: 
- Identify API clients
- Enable usage tracking and quotas
- Not for authentication (use with other auth methods)

**Usage Plans**:
- Associate API keys with usage plans
- Define throttling and quota limits
- Monitor usage per client

### Authorization Strategies

#### Resource-Based Policies
Control access at the API level using IAM policy language:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::account:user/username"
      },
      "Action": "execute-api:Invoke",
      "Resource": "arn:aws:execute-api:region:account:api-id/*",
      "Condition": {
        "IpAddress": {
          "aws:sourceIp": "203.0.113.0/24"
        }
      }
    }
  ]
}
```

#### Method-Level Authorization
- Configure authorization per HTTP method
- Combine multiple authorization types
- Override API-level settings

### Security Best Practices

#### 1. Defense in Depth
- **API Gateway**: Authentication and authorization
- **Backend Services**: Additional validation and authorization
- **Network**: VPC endpoints, security groups
- **Data**: Encryption at rest and in transit

#### 2. Least Privilege Access
- Minimal IAM permissions for API Gateway execution role
- Specific resource ARNs in policies
- Time-bound access tokens

#### 3. Input Validation
- Request validation in API Gateway
- Additional validation in backend services
- Sanitize user inputs

#### 4. Rate Limiting and Throttling
- Protect against DDoS attacks
- Prevent resource exhaustion
- Fair usage across clients

### SSL/TLS and Certificates

#### Default Domain
- AWS provides default HTTPS endpoint
- Uses AWS managed certificates
- Format: `https://{api-id}.execute-api.{region}.amazonaws.com`

#### Custom Domain Names
- Use your own domain (e.g., `api.example.com`)
- Requires SSL certificate from:
  - AWS Certificate Manager (ACM) - Recommended
  - Third-party certificate authorities

#### Certificate Requirements
- **Regional APIs**: Certificate in same region as API
- **Edge-Optimized**: Certificate must be in `us-east-1`
- **Wildcard certificates**: Supported for subdomains

### VPC Integration

#### Private APIs
- Accessible only from within VPC
- Uses VPC endpoints for API Gateway
- Network isolation from internet

#### VPC Links
- Connect API Gateway to resources in private subnets
- Supports Network Load Balancer (NLB) targets
- Enables hybrid architectures

### WAF Integration

#### Web Application Firewall Protection
- Protect against common web exploits
- SQL injection and XSS prevention
- Rate-based rules for DDoS protection
- Geographic restrictions

#### WAF Rules
- AWS Managed Rules
- Custom rules based on conditions
- IP whitelisting/blacklisting
- Request size limits

### Secrets Management

#### API Key Security
- Rotate API keys regularly
- Store securely (never in code)
- Use AWS Secrets Manager for key storage

#### Authentication Tokens
- Short-lived tokens preferred
- Secure token storage in clients
- Token refresh mechanisms

---

## Monitoring and Logging

### CloudWatch Integration

#### Default Metrics (No Additional Cost)
- **CacheHitCount/CacheMissCount**: Cache performance metrics
- **Count**: Number of API calls
- **IntegrationLatency**: Backend integration response time
- **Latency**: Total API Gateway response time
- **4XXError/5XXError**: Client and server error counts

#### Detailed Metrics (Additional Cost)
- Per-stage metrics
- Per-method metrics
- Per-resource metrics
- More granular monitoring

#### Custom Metrics
- Use CloudWatch PutMetric API
- Track business-specific KPIs
- Integration with Lambda for custom metrics

### X-Ray Tracing

#### Distributed Tracing Benefits
- **End-to-end visibility**: Track requests across services
- **Performance analysis**: Identify bottlenecks
- **Error diagnosis**: Trace errors to specific components
- **Service map**: Visual representation of service dependencies

#### Configuration
- Enable X-Ray tracing per stage
- Sampling rules control trace collection
- Integration with Lambda automatic
- Custom segments for detailed tracing

#### Trace Information
- Request/response details
- Integration latency breakdown
- Error annotations
- Custom annotations and metadata

### Access Logging

#### CloudWatch Logs Integration
API Gateway can write detailed access logs to CloudWatch Logs:

**Log Format Variables**:
```
$requestId $requestTime $httpMethod $resourcePath $status $responseLength $requestTime $error.message $error.messageString $context.requestId
```

**Custom Log Format Example**:
```json
{
  "requestId": "$context.requestId",
  "ip": "$context.identity.sourceIp", 
  "caller": "$context.identity.caller",
  "user": "$context.identity.user",
  "requestTime": "$context.requestTime",
  "httpMethod": "$context.httpMethod",
  "resourcePath": "$context.resourcePath",
  "status": "$context.status",
  "protocol": "$context.protocol",
  "responseLength": "$context.responseLength"
}
```

#### Kinesis Data Firehose Integration
- Stream logs to S3, Redshift, or Elasticsearch
- Real-time log processing
- Cost-effective for high-volume logging

### Alarms and Notifications

#### CloudWatch Alarms
**Common Alarm Scenarios**:
- High error rates (4XX/5XX errors)
- Latency thresholds exceeded
- Throttling events
- Cache hit ratio below threshold

**Example Alarm Configuration**:
```json
{
  "AlarmName": "APIGateway-HighErrorRate",
  "MetricName": "4XXError",
  "Namespace": "AWS/ApiGateway",
  "Statistic": "Sum",
  "Period": 300,
  "EvaluationPeriods": 2,
  "Threshold": 10,
  "ComparisonOperator": "GreaterThanThreshold"
}
```

#### SNS Integration
- Send notifications to email, SMS, or other endpoints
- Trigger automated remediation via Lambda
- Integration with ticketing systems

### Performance Monitoring

#### Key Performance Indicators (KPIs)
1. **Availability**: Uptime percentage
2. **Latency**: Response time percentiles (P50, P95, P99)
3. **Throughput**: Requests per second
4. **Error Rate**: Percentage of failed requests
5. **Cache Efficiency**: Hit ratio for cached responses

#### Dashboard Creation
- CloudWatch Dashboards for visualization
- Custom widgets for specific metrics
- Real-time monitoring capabilities
- Historical trend analysis

### Debugging and Troubleshooting

#### Execution Logs
- Detailed request/response logs
- Integration execution details
- Error messages and stack traces
- Performance timing information

#### Common Issues and Solutions

**High Latency**:
- Check integration latency vs API Gateway latency
- Optimize backend services
- Implement caching strategies
- Review VTL template performance

**4XX Errors**:
- Validate request format
- Check authorization configuration
- Review input validation rules
- Verify API key configuration

**5XX Errors**:
- Check backend service health
- Review IAM permissions
- Verify integration configuration
- Monitor timeout settings

**Cache Issues**:
- Verify cache key configuration
- Check TTL settings
- Monitor cache hit/miss ratio
- Review cache invalidation strategies

### Operational Excellence

#### Automated Monitoring
- Infrastructure as Code for monitoring setup
- Automated alerting based on thresholds
- Self-healing mechanisms where possible
- Proactive monitoring strategies

#### Log Analysis
- Use CloudWatch Insights for log queries
- Pattern recognition for anomaly detection
- Correlation analysis across services
- Performance trend identification

#### Continuous Improvement
- Regular review of monitoring metrics
- Optimization based on usage patterns
- Capacity planning using historical data
- Performance benchmarking

---

## Deployment and Stages

### Stage Concept

#### What are Stages?
Stages are named references to deployments of your API. They enable you to:
- Deploy different versions of your API
- Manage multiple environments (dev, staging, prod)
- Control access and configurations per environment
- Implement canary deployments

#### Stage Configuration
Each stage maintains its own:
- **Deployment snapshot**: Specific version of API configuration
- **Stage variables**: Environment-specific configuration values
- **Throttling settings**: Rate and burst limits
- **Caching configuration**: Cache settings and TTL
- **Logging level**: CloudWatch logging verbosity
- **Client certificates**: For backend authentication

### Deployment Process

#### Manual Deployment
1. **Create Deployment**: Snapshot current API configuration
2. **Associate with Stage**: Deploy to existing or new stage
3. **Configure Stage Settings**: Set variables, throttling, etc.
4. **Test and Validate**: Ensure deployment works correctly

#### Automated Deployment
- **CI/CD Integration**: AWS CodePipeline, CodeDeploy
- **Infrastructure as Code**: CloudFormation, CDK, Terraform
- **Blue/Green Deployments**: Zero-downtime deployments
- **Rollback Capabilities**: Quick reversion to previous versions

### Stage Variables

#### Purpose and Benefits
- **Environment Configuration**: Different values per environment
- **Backend Endpoints**: Point to different backend services
- **Lambda Function Versions**: Use different function versions/aliases
- **Feature Flags**: Enable/disable features per environment

#### Usage Examples

**Lambda Integration with Aliases**:
```
# Stage Variable: lambdaAlias
# Integration URI: arn:aws:apigateway:region:lambda:path/2015-03-31/functions/arn:aws:lambda:region:account:function:myFunction:${stageVariables.lambdaAlias}/invocations
```

**HTTP Backend Selection**:
```
# Stage Variable: backendUrl
# Integration URI: ${stageVariables.backendUrl}/api/users
```

**Configuration Values**:
```json
{
  "dev": {
    "dbEndpoint": "dev-db.example.com",
    "cacheEnabled": "false",
    "logLevel": "DEBUG"
  },
  "prod": {
    "dbEndpoint": "prod-db.example.com", 
    "cacheEnabled": "true",
    "logLevel": "ERROR"
  }
}
```

### Canary Deployments

#### How Canary Deployments Work
1. **Deploy to Canary**: Deploy new version to canary stage
2. **Traffic Splitting**: Route percentage of traffic to canary
3. **Monitor Metrics**: Watch error rates, latency, business metrics
4. **Promote or Rollback**: Based on canary performance

#### Configuration
- **Canary Weight**: Percentage of traffic (0-100%)
- **Stage Variables Override**: Different configuration for canary
- **Separate Monitoring**: Independent metrics and logs
- **Automated Promotion**: Based on CloudWatch alarms

#### Best Practices
- **Start Small**: Begin with 5-10% traffic
- **Monitor Closely**: Watch key metrics continuously  
- **Quick Rollback**: Automated rollback on issues
- **Business Impact**: Monitor business KPIs, not just technical metrics

### Environment Management

#### Multi-Environment Strategy

**Development Environment**:
- Relaxed security for testing
- Detailed logging enabled
- Lower throttling limits
- Mock integrations for cost savings

**Staging Environment**:
- Production-like configuration
- Full integration testing
- Performance testing
- Security validation

**Production Environment**:
- Strict security controls
- Optimized performance settings
- Comprehensive monitoring
- Disaster recovery planning

#### Environment Promotion
```
Development → Staging → Production
     ↓            ↓         ↓
   Feature     Integration  Release
   Testing       Testing    Validation
```

### Version Management

#### API Versioning Strategies

**Path-Based Versioning**:
```
/v1/users
/v2/users
```

**Header-Based Versioning**:
```
Accept: application/vnd.api+json;version=1
Accept: application/vnd.api+json;version=2
```

**Query Parameter Versioning**:
```
/users?version=1
/users?version=2
```

#### Backward Compatibility
- **Deprecation Strategy**: Gradual phase-out of old versions
- **Migration Path**: Clear upgrade instructions
- **Support Timeline**: Define support lifecycle
- **Breaking Changes**: Minimize and communicate clearly

### Blue/Green Deployments

#### Implementation with API Gateway
1. **Blue Environment**: Current production version
2. **Green Environment**: New version deployment
3. **DNS Switch**: Route traffic to green environment
4. **Validation**: Monitor green environment
5. **Rollback Option**: Quick switch back to blue if issues

#### Benefits
- **Zero Downtime**: Instant traffic switching
- **Easy Rollback**: Quick reversion capability
- **Full Testing**: Test complete environment before switch
- **Risk Mitigation**: Isolated environments reduce risk

### Deployment Automation

#### CI/CD Pipeline Integration

**Pipeline Stages**:
1. **Source Control**: Code commit triggers pipeline
2. **Build**: Package API definitions and code
3. **Test**: Automated testing (unit, integration)
4. **Deploy to Staging**: Automated staging deployment
5. **Acceptance Tests**: Automated validation
6. **Production Deployment**: Manual approval + automated deploy
7. **Monitoring**: Post-deployment validation

**Tools and Services**:
- **AWS CodePipeline**: Orchestrate deployment workflow
- **AWS CodeBuild**: Build and test automation
- **AWS CodeDeploy**: Application deployment
- **AWS SAM**: Serverless application model
- **AWS CDK**: Infrastructure as code

#### Infrastructure as Code

**CloudFormation Template Example**:
```yaml
Resources:
  ApiGateway:
    Type: AWS::ApiGateway::RestApi
    Properties:
      Name: MyAPI
      
  ApiDeployment:
    Type: AWS::ApiGateway::Deployment
    Properties:
      RestApiId: !Ref ApiGateway
      StageName: !Ref Environment
      
  ApiStage:
    Type: AWS::ApiGateway::Stage
    Properties:
      RestApiId: !Ref ApiGateway
      DeploymentId: !Ref ApiDeployment
      StageName: !Ref Environment
      Variables:
        environment: !Ref Environment
```

### Rollback Strategies

#### Immediate Rollback
- Change DNS/load balancer routing
- Revert to previous stage deployment
- Update stage variables to previous values

#### Gradual Rollback
- Reduce canary traffic percentage
- Monitor for improvement
- Complete rollback if issues persist

#### Disaster Recovery
- Cross-region API deployment
- Route 53 health checks
- Automated failover procedures
- Data synchronization strategies

---

## Cost Optimization and Best Practices

### Pricing Models

#### REST API Pricing
- **API Calls**: $3.50 per million API calls (first 333 million calls/month)
- **Data Transfer**: Standard AWS data transfer rates
- **Caching**: $0.02 per hour for 0.5GB cache, scaling up to $3.80/hour for 237GB
- **Request/Response Data**: $0.09 per GB for first 10TB

#### HTTP API Pricing  
- **API Calls**: $1.00 per million API calls (first 300 million calls/month)
- **Data Transfer**: Standard AWS data transfer rates
- **Up to 70% cost savings** compared to REST APIs for simple use cases

#### WebSocket API Pricing
- **Connection Minutes**: $0.25 per million connection minutes
- **Messages**: $1.00 per million messages (up to 32KB each)
- **Data Transfer**: Standard rates apply

### Cost Optimization Strategies

#### 1. Choose the Right API Type

**Use HTTP APIs when:**
- Simple proxy to Lambda functions
- Cost is primary concern
- No need for advanced features (caching, transformations)
- Modern authentication requirements (JWT, OAuth 2.0)

**Use REST APIs when:**
- Need caching capabilities
- Require request/response transformations
- Complex integration requirements
- SDK generation needed

#### 2. Implement Caching Effectively

**Cache Strategy**:
```
High-frequency, low-change data → Long TTL (30+ minutes)
Medium-frequency data → Medium TTL (5-15 minutes)  
Dynamic, user-specific data → Short TTL (1-5 minutes) or no caching
```

**Cache Key Optimization**:
- Include only necessary parameters in cache key
- Avoid user-specific data in cache keys for shared content
- Use stage variables for environment-specific cache keys

#### 3. Optimize Data Transfer

**Response Size Optimization**:
- Use response filtering to return only required fields
- Implement pagination for large data sets
- Use compression (gzip) for large responses
- Consider GraphQL for flexible data queries

**Request Optimization**:
- Validate requests early to reduce backend calls
- Use efficient data formats (JSON over XML)
- Implement request batching where possible

#### 4. Efficient Backend Integration

**Direct Service Integration**:
- Use direct AWS service integration instead of Lambda for simple operations
- Reduces Lambda execution costs
- Eliminates intermediate processing overhead

**Lambda Optimization**:
- Right-size Lambda functions
- Use provisioned concurrency judiciously
- Optimize cold start times
- Leverage Lambda layers for shared code

#### 5. Usage Plans and Throttling

**Cost Control Through Throttling**:
- Implement usage plans to control costs per client
- Set burst limits to prevent cost spikes
- Use API keys for client identification and limiting
- Monitor usage patterns and adjust limits accordingly

### Architectural Best Practices

#### 1. Microservices Architecture

**API Design Principles**:
- **Single Responsibility**: Each API serves a specific business function
- **Autonomous Services**: APIs can be developed and deployed independently
- **Data Ownership**: Each service owns its data and database
- **Stateless Design**: APIs should be stateless for better scalability

**Benefits for SAA-C03**:
- Improved scalability and availability
- Technology diversity (different services can use different technologies)
- Team autonomy and faster development
- Better fault isolation

#### 2. Security by Design

**Defense in Depth**:
```
Internet → WAF → API Gateway → VPC → Backend Services → Data Layer
   ↑         ↑        ↑          ↑         ↑             ↑
DDoS    Web App   API Auth   Network   Service      Encryption
Protection Firewall & Author   Security  Security    at Rest
```

**Zero Trust Architecture**:
- Authenticate and authorize every request
- Encrypt data in transit and at rest
- Monitor and log all access
- Apply least privilege principles

#### 3. High Availability and Resilience

**Multi-Region Architecture**:
```
Primary Region:
- API Gateway (Primary)
- Backend Services
- Database (Primary)

Secondary Region:
- API Gateway (Standby)
- Backend Services
- Database (Read Replica/Standby)

Route 53 Health Checks → Automatic Failover
```

**Fault Tolerance Patterns**:
- **Circuit Breaker**: Prevent cascade failures
- **Retry with Backoff**: Handle transient failures
- **Bulkhead**: Isolate critical resources
- **Timeout**: Prevent resource exhaustion

#### 4. Performance Optimization

**Latency Reduction Techniques**:
- **Edge Optimization**: Use CloudFront distribution
- **Regional APIs**: Deploy closer to users
- **Caching**: Implement multi-level caching strategy
- **Connection Pooling**: Optimize backend connections

**Caching Strategy**:
```
Level 1: API Gateway Cache (seconds to minutes)
Level 2: Application Cache (minutes to hours)
Level 3: Database Cache (hours to days)
Level 4: CDN Cache (hours to days)
```

### Monitoring and Operational Excellence

#### 1. Observability Strategy

**Three Pillars of Observability**:
- **Metrics**: Quantitative measurements (latency, throughput, errors)
- **Logs**: Detailed event records for debugging
- **Traces**: Request flow across distributed systems

**Key Metrics to Track**:
- API response times (P50, P95, P99)
- Error rates by type and endpoint
- Throughput and concurrent users
- Cache hit ratios
- Backend service health

#### 2. Automated Operations

**Infrastructure as Code**:
```yaml
# Example: Terraform for API Gateway
resource "aws_api_gateway_rest_api" "main" {
  name = var.api_name
  
  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

resource "aws_api_gateway_stage" "prod" {
  stage_name    = "prod"
  rest_api_id   = aws_api_gateway_rest_api.main.id
  deployment_id = aws_api_gateway_deployment.main.id
  
  cache_cluster_enabled = true
  cache_cluster_size   = "0.5"
  
  xray_tracing_enabled = true
}
```

**Automated Scaling and Healing**:
- Auto Scaling for backend services
- Health checks and automatic replacement
- Automated backup and disaster recovery
- Self-healing infrastructure patterns

#### 3. Continuous Improvement

**Performance Optimization Cycle**:
1. **Measure**: Collect performance metrics
2. **Analyze**: Identify bottlenecks and optimization opportunities
3. **Optimize**: Implement improvements
4. **Validate**: Measure impact of changes
5. **Repeat**: Continuous optimization process

### Integration Patterns

#### 1. Event-Driven Architecture

**API Gateway + EventBridge Pattern**:
```
API Request → API Gateway → Lambda → EventBridge → Multiple Consumers
```

**Benefits**:
- Decoupled services
- Asynchronous processing
- Event replay capabilities
- Multiple subscribers to events

#### 2. CQRS (Command Query Responsibility Segregation)

**Pattern Implementation**:
```
Write API → Command Handler → Write Database
Read API → Query Handler → Read Database (Materialized Views)
```

**Benefits**:
- Optimized read and write operations
- Independent scaling
- Better performance for complex queries

#### 3. API Gateway as Backend for Frontend (BFF)

**Mobile BFF vs Web BFF**:
```
Mobile App → Mobile BFF (API Gateway) → Microservices
Web App → Web BFF (API Gateway) → Microservices
```

**Benefits**:
- Tailored APIs for different client types
- Reduced over-fetching
- Better client experience
- Independent evolution of client-specific APIs

### Compliance and Governance

#### 1. Data Protection and Privacy

**GDPR/CCPA Considerations**:
- Data minimization in API responses
- Right to be forgotten implementation
- Data anonymization in logs
- Consent management integration

#### 2. API Governance

**Governance Framework**:
- **API Design Standards**: Consistent API design patterns
- **Security Policies**: Mandatory security controls
- **Performance Standards**: SLA requirements
- **Documentation Requirements**: API documentation standards
- **Lifecycle Management**: API versioning and deprecation policies

#### 3. Audit and Compliance

**Compliance Monitoring**:
- Access logs for audit trails
- API usage tracking
- Security event monitoring
- Compliance reporting automation

---

## Exam-Focused Key Points

### Critical Concepts for SAA-C03

#### 1. API Gateway Types - When to Use What

**REST APIs** - Choose when:
- ✅ Need caching capabilities
- ✅ Require request/response transformations (VTL)
- ✅ SDK generation required
- ✅ Complex integration patterns
- ✅ Request validation needed
- ❌ Cost is primary concern

**HTTP APIs** - Choose when:
- ✅ Cost optimization (70% cheaper)
- ✅ Simple Lambda proxy integration
- ✅ Modern authentication (JWT, OAuth 2.0)
- ✅ Built-in CORS support needed
- ❌ Need caching or transformations
- ❌ Require SDK generation

**WebSocket APIs** - Choose when:
- ✅ Real-time bidirectional communication
- ✅ Chat applications, gaming, IoT
- ✅ Live updates and notifications
- ❌ Traditional request-response patterns

#### 2. Security Models - Authentication vs Authorization

**Authentication Methods (Who you are)**:
- **IAM**: Internal AWS services, admin APIs
- **Cognito User Pools**: User-facing applications
- **Lambda Authorizers**: Custom authentication logic
- **API Keys**: Client identification (not authentication!)

**Authorization (What you can do)**:
- **Resource Policies**: Control access at API level
- **IAM Policies**: Fine-grained permissions
- **Cognito Groups**: Role-based access control
- **Custom Authorization**: Lambda authorizer policies

#### 3. Integration Patterns

**Lambda Integration Types**:
```
Lambda Proxy Integration (Recommended):
- Lambda receives full request context
- Must return specific response format
- Simpler configuration

Lambda Custom Integration:
- Configure request/response mapping
- More control, more complexity
- Use when transformation needed
```

**Direct AWS Service Integration**:
- No Lambda required for simple operations
- Cost-effective for basic CRUD operations
- Supports DynamoDB, S3, SNS, SQS, etc.
- Requires IAM roles for service access

#### 4. Caching Strategy (REST APIs Only)

**Cache Configuration**:
- TTL: 0 seconds to 1 hour (3600 seconds)
- Sizes: 0.5GB to 237GB
- Per-key invalidation supported
- Stage-level and method-level configuration

**Cache Key Components**:
- Query parameters
- Headers
- Path parameters
- Request context variables

#### 5. Throttling and Usage Plans

**Throttling Hierarchy** (most specific wins):
```
1. Client-level throttling (highest priority)
2. Method-level throttling
3. Stage-level throttling  
4. Account-level throttling (lowest priority)
```

**Usage Plan Components**:
- API Keys for client identification
- Throttling limits (rate + burst)
- Quota limits (requests per period)
- Associated API stages

### Common Exam Scenarios

#### Scenario 1: Serverless Web Application
**Requirements**: Frontend → API Gateway → Lambda → DynamoDB

**Key Decisions**:
- **API Type**: HTTP API for cost optimization
- **Authentication**: Cognito User Pools for user management
- **CORS**: Enable built-in CORS for browser requests
- **Caching**: Not available with HTTP APIs
- **Monitoring**: CloudWatch + X-Ray for observability

#### Scenario 2: Microservices Architecture
**Requirements**: Multiple services behind single API endpoint

**Key Decisions**:
- **API Type**: REST API for advanced features
- **Integration**: Lambda proxy integration per service
- **Security**: API Keys + Lambda authorizers
- **Caching**: Cache stable reference data
- **Deployment**: Stages for dev/staging/prod environments

#### Scenario 3: Legacy System Integration
**Requirements**: Expose legacy SOAP services as REST APIs

**Key Decisions**:
- **API Type**: REST API for transformation capabilities
- **Integration**: HTTP integration with VTL mapping
- **Security**: IAM authentication for internal access
- **Transformation**: SOAP to REST conversion using VTL
- **Error Handling**: Custom error responses

#### Scenario 4: Real-time Chat Application
**Requirements**: Bidirectional real-time communication

**Key Decisions**:
- **API Type**: WebSocket API mandatory
- **Routes**: $connect, $disconnect, $default, custom routes
- **Authentication**: Custom authorizer or IAM
- **Backend**: Lambda for message processing
- **Storage**: DynamoDB for connection management

#### Scenario 5: High-Volume Public API
**Requirements**: Handle millions of requests, cost-effective

**Key Decisions**:
- **API Type**: HTTP API for cost optimization
- **Caching**: Use CloudFront for additional caching layer
- **Throttling**: Implement usage plans and API keys
- **Monitoring**: Detailed CloudWatch metrics
- **Security**: Rate limiting + WAF integration

### Performance and Scaling Considerations

#### Latency Optimization
**Edge-Optimized vs Regional**:
- **Edge-Optimized**: Use CloudFront, better for global users
- **Regional**: Lower latency for regional users, VPC integration

**Timeout Limits**:
- **API Gateway**: 29 seconds maximum
- **Lambda**: 15 minutes maximum (but API Gateway timeout applies)
- **HTTP Integration**: Configure appropriate timeouts

#### Concurrent Connections
- **REST/HTTP APIs**: No explicit connection limits
- **WebSocket APIs**: 100,000 concurrent connections per region
- **Backend Scaling**: Ensure backend can handle API Gateway scale

#### Regional Considerations
- **Multi-Region Deployment**: For disaster recovery
- **Route 53**: Health checks and failover
- **Data Synchronization**: Cross-region replication
- **Certificate Management**: Regional certificates for regional APIs

### Cost Optimization Exam Tips

#### Cost Comparison Questions
When asked about cost optimization:
1. **HTTP APIs are 70% cheaper** than REST APIs for simple use cases
2. **Caching reduces backend calls** and associated costs
3. **Direct service integration** eliminates Lambda costs
4. **Usage plans prevent cost overruns** through throttling

#### Free Tier Benefits
- **REST APIs**: 1 million API calls per month for 12 months
- **HTTP APIs**: 1 million API calls per month for 12 months
- **Data Transfer**: 1GB per month across all services

### Security Exam Focus Areas

#### Common Security Scenarios
1. **Mobile App Authentication**: Use Cognito User Pools
2. **Machine-to-Machine**: Use IAM roles and policies
3. **Third-Party Integration**: API Keys + Lambda authorizers
4. **Internal Services**: Resource policies with VPC conditions

#### Security Best Practices for Exam
- **Never use API Keys alone for authentication**
- **Always encrypt data in transit** (HTTPS enforced by default)
- **Implement least privilege access** in IAM policies
- **Use WAF for DDoS protection** on public APIs
- **Enable logging and monitoring** for security auditing

### Troubleshooting Common Issues

#### HTTP Status Codes
- **400 Bad Request**: Invalid request format or parameters
- **401 Unauthorized**: Authentication failed
- **403 Forbidden**: Authorization failed (authenticated but no permission)
- **429 Too Many Requests**: Throttling limits exceeded
- **502 Bad Gateway**: Backend integration error
- **504 Gateway Timeout**: Backend timeout (29-second limit)

#### Integration Errors
- **Lambda Function Error**: Check function logs in CloudWatch
- **Timeout Error**: Verify backend response time < 29 seconds
- **Permission Error**: Check IAM roles and resource policies
- **VPC Integration**: Ensure proper VPC configuration and routing

---

## AWS CLI Commands Reference

This section provides comprehensive AWS CLI commands for managing API Gateway REST APIs, deployments, authorizers, and related operations.

### Create REST APIs

```bash
# Create a new REST API
aws apigateway create-rest-api \
    --name "MyAPI" \
    --description "My REST API" \
    --endpoint-configuration types=REGIONAL

# Create a REST API with edge-optimized endpoint
aws apigateway create-rest-api \
    --name "MyEdgeAPI" \
    --endpoint-configuration types=EDGE

# Create a private REST API
aws apigateway create-rest-api \
    --name "MyPrivateAPI" \
    --endpoint-configuration types=PRIVATE \
    --policy file://resource-policy.json

# Create REST API with API key source
aws apigateway create-rest-api \
    --name "MyAPI" \
    --api-key-source HEADER

# Create REST API with minimum compression size
aws apigateway create-rest-api \
    --name "MyAPI" \
    --minimum-compression-size 1024

# Get all REST APIs
aws apigateway get-rest-apis

# Get a specific REST API
aws apigateway get-rest-api \
    --rest-api-id abc123

# Update REST API
aws apigateway update-rest-api \
    --rest-api-id abc123 \
    --patch-operations op=replace,path=/name,value="UpdatedAPI"

# Delete REST API
aws apigateway delete-rest-api \
    --rest-api-id abc123
```

### Create Resources and Methods

```bash
# Get the root resource ID
aws apigateway get-resources \
    --rest-api-id abc123 \
    --query 'items[?path==`/`].id' \
    --output text

# Create a new resource
aws apigateway create-resource \
    --rest-api-id abc123 \
    --parent-id root-id \
    --path-part users

# Create a nested resource
aws apigateway create-resource \
    --rest-api-id abc123 \
    --parent-id users-resource-id \
    --path-part "{userId}"

# List all resources
aws apigateway get-resources \
    --rest-api-id abc123

# Get a specific resource
aws apigateway get-resource \
    --rest-api-id abc123 \
    --resource-id resource-id

# Create GET method
aws apigateway put-method \
    --rest-api-id abc123 \
    --resource-id resource-id \
    --http-method GET \
    --authorization-type NONE

# Create method with API key required
aws apigateway put-method \
    --rest-api-id abc123 \
    --resource-id resource-id \
    --http-method POST \
    --authorization-type NONE \
    --api-key-required

# Create method with custom authorizer
aws apigateway put-method \
    --rest-api-id abc123 \
    --resource-id resource-id \
    --http-method POST \
    --authorization-type CUSTOM \
    --authorizer-id authorizer-id

# Create method with IAM authorization
aws apigateway put-method \
    --rest-api-id abc123 \
    --resource-id resource-id \
    --http-method GET \
    --authorization-type AWS_IAM

# Create method with Cognito authorization
aws apigateway put-method \
    --rest-api-id abc123 \
    --resource-id resource-id \
    --http-method POST \
    --authorization-type COGNITO_USER_POOLS \
    --authorizer-id authorizer-id

# Set up Lambda integration
aws apigateway put-integration \
    --rest-api-id abc123 \
    --resource-id resource-id \
    --http-method POST \
    --type AWS_PROXY \
    --integration-http-method POST \
    --uri "arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:123456789012:function:MyFunction/invocations"

# Set up HTTP integration
aws apigateway put-integration \
    --rest-api-id abc123 \
    --resource-id resource-id \
    --http-method GET \
    --type HTTP \
    --integration-http-method GET \
    --uri "https://example.com/api/resource"

# Set up HTTP proxy integration
aws apigateway put-integration \
    --rest-api-id abc123 \
    --resource-id resource-id \
    --http-method ANY \
    --type HTTP_PROXY \
    --integration-http-method ANY \
    --uri "https://example.com/{proxy}"

# Set up AWS service integration (e.g., S3)
aws apigateway put-integration \
    --rest-api-id abc123 \
    --resource-id resource-id \
    --http-method GET \
    --type AWS \
    --integration-http-method GET \
    --uri "arn:aws:apigateway:us-east-1:s3:path/bucket-name/object-key" \
    --credentials "arn:aws:iam::123456789012:role/APIGatewayS3Role"

# Set up mock integration
aws apigateway put-integration \
    --rest-api-id abc123 \
    --resource-id resource-id \
    --http-method GET \
    --type MOCK \
    --request-templates '{"application/json":"{\"statusCode\": 200}"}'

# Create method response
aws apigateway put-method-response \
    --rest-api-id abc123 \
    --resource-id resource-id \
    --http-method GET \
    --status-code 200 \
    --response-models '{"application/json":"Empty"}'

# Create integration response
aws apigateway put-integration-response \
    --rest-api-id abc123 \
    --resource-id resource-id \
    --http-method GET \
    --status-code 200 \
    --selection-pattern ""

# Delete method
aws apigateway delete-method \
    --rest-api-id abc123 \
    --resource-id resource-id \
    --http-method GET

# Delete resource
aws apigateway delete-resource \
    --rest-api-id abc123 \
    --resource-id resource-id
```

### Deploy APIs (Stages)

```bash
# Create a deployment
aws apigateway create-deployment \
    --rest-api-id abc123 \
    --stage-name prod

# Create deployment with description
aws apigateway create-deployment \
    --rest-api-id abc123 \
    --stage-name prod \
    --description "Production deployment v1.0"

# Create deployment with stage description
aws apigateway create-deployment \
    --rest-api-id abc123 \
    --stage-name prod \
    --stage-description "Production stage" \
    --description "Initial production deployment"

# Create deployment with variables
aws apigateway create-deployment \
    --rest-api-id abc123 \
    --stage-name prod \
    --variables lambdaAlias=prod,environment=production

# Get deployments
aws apigateway get-deployments \
    --rest-api-id abc123

# Get a specific deployment
aws apigateway get-deployment \
    --rest-api-id abc123 \
    --deployment-id deployment-id

# Create a stage
aws apigateway create-stage \
    --rest-api-id abc123 \
    --stage-name staging \
    --deployment-id deployment-id

# Create stage with cache settings
aws apigateway create-stage \
    --rest-api-id abc123 \
    --stage-name prod \
    --deployment-id deployment-id \
    --cache-cluster-enabled \
    --cache-cluster-size 0.5

# Create stage with throttling
aws apigateway create-stage \
    --rest-api-id abc123 \
    --stage-name prod \
    --deployment-id deployment-id \
    --throttle-settings rateLimit=1000,burstLimit=2000

# Get stages
aws apigateway get-stages \
    --rest-api-id abc123

# Get a specific stage
aws apigateway get-stage \
    --rest-api-id abc123 \
    --stage-name prod

# Update stage settings
aws apigateway update-stage \
    --rest-api-id abc123 \
    --stage-name prod \
    --patch-operations op=replace,path=/cacheClusterEnabled,value=true

# Enable CloudWatch logging for stage
aws apigateway update-stage \
    --rest-api-id abc123 \
    --stage-name prod \
    --patch-operations \
        op=replace,path=/*/*/logging/loglevel,value=INFO \
        op=replace,path=/*/*/logging/dataTrace,value=true

# Enable X-Ray tracing
aws apigateway update-stage \
    --rest-api-id abc123 \
    --stage-name prod \
    --patch-operations op=replace,path=/tracingEnabled,value=true

# Set stage variables
aws apigateway update-stage \
    --rest-api-id abc123 \
    --stage-name prod \
    --patch-operations \
        op=replace,path=/variables/lambdaAlias,value=prod \
        op=replace,path=/variables/environment,value=production

# Delete stage
aws apigateway delete-stage \
    --rest-api-id abc123 \
    --stage-name staging

# Delete deployment
aws apigateway delete-deployment \
    --rest-api-id abc123 \
    --deployment-id deployment-id
```

### Create and Configure Authorizers

```bash
# Create Lambda authorizer (TOKEN type)
aws apigateway create-authorizer \
    --rest-api-id abc123 \
    --name "MyLambdaAuthorizer" \
    --type TOKEN \
    --authorizer-uri "arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:123456789012:function:MyAuthFunction/invocations" \
    --authorizer-credentials "arn:aws:iam::123456789012:role/APIGatewayAuthRole" \
    --identity-source "method.request.header.Authorization"

# Create Lambda authorizer (REQUEST type)
aws apigateway create-authorizer \
    --rest-api-id abc123 \
    --name "RequestAuthorizer" \
    --type REQUEST \
    --authorizer-uri "arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:123456789012:function:MyAuthFunction/invocations" \
    --identity-source "method.request.header.Authorization,context.sourceIp"

# Create Cognito User Pool authorizer
aws apigateway create-authorizer \
    --rest-api-id abc123 \
    --name "CognitoAuthorizer" \
    --type COGNITO_USER_POOLS \
    --provider-arns "arn:aws:cognito-idp:us-east-1:123456789012:userpool/us-east-1_ABC123" \
    --identity-source "method.request.header.Authorization"

# Create authorizer with caching
aws apigateway create-authorizer \
    --rest-api-id abc123 \
    --name "CachedAuthorizer" \
    --type TOKEN \
    --authorizer-uri "arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:123456789012:function:MyAuthFunction/invocations" \
    --identity-source "method.request.header.Authorization" \
    --authorizer-result-ttl-in-seconds 300

# List authorizers
aws apigateway get-authorizers \
    --rest-api-id abc123

# Get a specific authorizer
aws apigateway get-authorizer \
    --rest-api-id abc123 \
    --authorizer-id authorizer-id

# Update authorizer
aws apigateway update-authorizer \
    --rest-api-id abc123 \
    --authorizer-id authorizer-id \
    --patch-operations op=replace,path=/authorizerResultTtlInSeconds,value=600

# Delete authorizer
aws apigateway delete-authorizer \
    --rest-api-id abc123 \
    --authorizer-id authorizer-id
```

### API Keys and Usage Plans

```bash
# Create an API key
aws apigateway create-api-key \
    --name "MyAPIKey" \
    --description "API key for external partners" \
    --enabled

# Create API key with value
aws apigateway create-api-key \
    --name "MyAPIKey" \
    --value "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6" \
    --enabled

# Get all API keys
aws apigateway get-api-keys

# Get API keys with name filter
aws apigateway get-api-keys \
    --name-query "Partner"

# Get a specific API key
aws apigateway get-api-key \
    --api-key key-id \
    --include-value

# Update API key
aws apigateway update-api-key \
    --api-key key-id \
    --patch-operations op=replace,path=/enabled,value=false

# Delete API key
aws apigateway delete-api-key \
    --api-key key-id

# Create usage plan
aws apigateway create-usage-plan \
    --name "BasicPlan" \
    --description "Basic usage plan" \
    --throttle rateLimit=100,burstLimit=200 \
    --quota limit=10000,period=MONTH

# Create usage plan with API stages
aws apigateway create-usage-plan \
    --name "PremiumPlan" \
    --api-stages apiId=abc123,stage=prod \
    --throttle rateLimit=1000,burstLimit=2000 \
    --quota limit=100000,period=MONTH,offset=0

# Get usage plans
aws apigateway get-usage-plans

# Get a specific usage plan
aws apigateway get-usage-plan \
    --usage-plan-id plan-id

# Update usage plan
aws apigateway update-usage-plan \
    --usage-plan-id plan-id \
    --patch-operations \
        op=replace,path=/throttle/rateLimit,value=500 \
        op=replace,path=/quota/limit,value=50000

# Delete usage plan
aws apigateway delete-usage-plan \
    --usage-plan-id plan-id

# Create usage plan key (associate API key with usage plan)
aws apigateway create-usage-plan-key \
    --usage-plan-id plan-id \
    --key-id key-id \
    --key-type API_KEY

# Get usage plan keys
aws apigateway get-usage-plan-keys \
    --usage-plan-id plan-id

# Get usage (API key usage statistics)
aws apigateway get-usage \
    --usage-plan-id plan-id \
    --start-date "2024-01-01" \
    --end-date "2024-01-31"

# Get usage for specific API key
aws apigateway get-usage \
    --usage-plan-id plan-id \
    --key-id key-id \
    --start-date "2024-01-01" \
    --end-date "2024-01-31"

# Delete usage plan key
aws apigateway delete-usage-plan-key \
    --usage-plan-id plan-id \
    --key-id key-id
```

### Custom Domains

```bash
# Create custom domain name
aws apigateway create-domain-name \
    --domain-name api.example.com \
    --certificate-arn "arn:aws:acm:us-east-1:123456789012:certificate/abc123" \
    --endpoint-configuration types=REGIONAL \
    --regional-certificate-arn "arn:aws:acm:us-east-1:123456789012:certificate/abc123"

# Create edge-optimized custom domain
aws apigateway create-domain-name \
    --domain-name api.example.com \
    --certificate-arn "arn:aws:acm:us-east-1:123456789012:certificate/abc123" \
    --endpoint-configuration types=EDGE

# Create custom domain with security policy
aws apigateway create-domain-name \
    --domain-name api.example.com \
    --certificate-arn "arn:aws:acm:us-east-1:123456789012:certificate/abc123" \
    --security-policy TLS_1_2 \
    --endpoint-configuration types=REGIONAL

# Get custom domain names
aws apigateway get-domain-names

# Get a specific custom domain
aws apigateway get-domain-name \
    --domain-name api.example.com

# Update custom domain
aws apigateway update-domain-name \
    --domain-name api.example.com \
    --patch-operations op=replace,path=/certificateArn,value="arn:aws:acm:us-east-1:123456789012:certificate/new-cert"

# Delete custom domain
aws apigateway delete-domain-name \
    --domain-name api.example.com

# Create base path mapping
aws apigateway create-base-path-mapping \
    --domain-name api.example.com \
    --rest-api-id abc123 \
    --stage prod

# Create base path mapping with base path
aws apigateway create-base-path-mapping \
    --domain-name api.example.com \
    --rest-api-id abc123 \
    --stage prod \
    --base-path v1

# Get base path mappings
aws apigateway get-base-path-mappings \
    --domain-name api.example.com

# Get a specific base path mapping
aws apigateway get-base-path-mapping \
    --domain-name api.example.com \
    --base-path v1

# Update base path mapping
aws apigateway update-base-path-mapping \
    --domain-name api.example.com \
    --base-path v1 \
    --patch-operations op=replace,path=/stage,value=staging

# Delete base path mapping
aws apigateway delete-base-path-mapping \
    --domain-name api.example.com \
    --base-path v1
```

### Request and Response Transformations

```bash
# Create request validator
aws apigateway create-request-validator \
    --rest-api-id abc123 \
    --name "BodyValidator" \
    --validate-request-body

# Create request validator for parameters
aws apigateway create-request-validator \
    --rest-api-id abc123 \
    --name "ParamsValidator" \
    --validate-request-parameters

# Create full request validator
aws apigateway create-request-validator \
    --rest-api-id abc123 \
    --name "FullValidator" \
    --validate-request-body \
    --validate-request-parameters

# Get request validators
aws apigateway get-request-validators \
    --rest-api-id abc123

# Update method to use request validator
aws apigateway update-method \
    --rest-api-id abc123 \
    --resource-id resource-id \
    --http-method POST \
    --patch-operations op=replace,path=/requestValidatorId,value=validator-id

# Create model for request/response
aws apigateway create-model \
    --rest-api-id abc123 \
    --name "UserModel" \
    --content-type "application/json" \
    --schema file://user-schema.json

# Get models
aws apigateway get-models \
    --rest-api-id abc123

# Get a specific model
aws apigateway get-model \
    --rest-api-id abc123 \
    --model-name UserModel

# Delete model
aws apigateway delete-model \
    --rest-api-id abc123 \
    --model-name UserModel

# Update integration with request template
aws apigateway update-integration \
    --rest-api-id abc123 \
    --resource-id resource-id \
    --http-method POST \
    --patch-operations op=replace,path=/requestTemplates~1application~1json,value='{"body": $input.json("$")}'

# Update integration response with response template
aws apigateway update-integration-response \
    --rest-api-id abc123 \
    --resource-id resource-id \
    --http-method GET \
    --status-code 200 \
    --patch-operations op=replace,path=/responseTemplates~1application~1json,value='{"message": "Success"}'
```

### Throttling and Quotas

```bash
# Set account-level throttle settings
aws apigateway update-account \
    --patch-operations \
        op=replace,path=/throttle/rateLimit,value=10000 \
        op=replace,path=/throttle/burstLimit,value=5000

# Get account settings
aws apigateway get-account

# Set stage-level throttle settings
aws apigateway update-stage \
    --rest-api-id abc123 \
    --stage-name prod \
    --patch-operations \
        op=replace,path=/throttle/rateLimit,value=1000 \
        op=replace,path=/throttle/burstLimit,value=2000

# Set method-level throttle settings
aws apigateway update-stage \
    --rest-api-id abc123 \
    --stage-name prod \
    --patch-operations \
        op=replace,path=/*/GET/throttle/rateLimit,value=500 \
        op=replace,path=/*/POST/throttle/burstLimit,value=1000

# Set throttle for specific resource method
aws apigateway update-stage \
    --rest-api-id abc123 \
    --stage-name prod \
    --patch-operations \
        op=replace,path=/~1users~1{id}/GET/throttle/rateLimit,value=100
```

### CloudWatch Logging

```bash
# Enable CloudWatch logs for API Gateway (account level)
aws apigateway update-account \
    --patch-operations op=add,path=/cloudwatchRoleArn,value="arn:aws:iam::123456789012:role/APIGatewayCloudWatchRole"

# Enable execution logging for stage
aws apigateway update-stage \
    --rest-api-id abc123 \
    --stage-name prod \
    --patch-operations \
        op=replace,path=/*/*/logging/loglevel,value=INFO \
        op=replace,path=/*/*/logging/dataTrace,value=true \
        op=replace,path=/*/*/metrics/enabled,value=true

# Enable access logging for stage
aws apigateway update-stage \
    --rest-api-id abc123 \
    --stage-name prod \
    --patch-operations \
        op=replace,path=/accessLogSettings/destinationArn,value="arn:aws:logs:us-east-1:123456789012:log-group:api-gateway-logs" \
        op=replace,path=/accessLogSettings/format,value='$context.requestId'

# Disable logging
aws apigateway update-stage \
    --rest-api-id abc123 \
    --stage-name prod \
    --patch-operations \
        op=replace,path=/*/*/logging/loglevel,value=OFF \
        op=replace,path=/*/*/logging/dataTrace,value=false
```

### Export and Import APIs (Swagger/OpenAPI)

```bash
# Export API as Swagger/OpenAPI 2.0
aws apigateway get-export \
    --rest-api-id abc123 \
    --stage-name prod \
    --export-type swagger \
    --accepts application/json \
    swagger.json

# Export API as OpenAPI 3.0
aws apigateway get-export \
    --rest-api-id abc123 \
    --stage-name prod \
    --export-type oas30 \
    --accepts application/json \
    openapi.json

# Export API with extensions
aws apigateway get-export \
    --rest-api-id abc123 \
    --stage-name prod \
    --export-type oas30 \
    --parameters extensions='integrations' \
    openapi-full.json

# Export API with API Gateway extensions and postman collection
aws apigateway get-export \
    --rest-api-id abc123 \
    --stage-name prod \
    --export-type swagger \
    --parameters extensions='apigateway' \
    --accepts application/json \
    swagger-with-extensions.json

# Import API from Swagger file (creates new API)
aws apigateway import-rest-api \
    --body file://swagger.json

# Import API with fail on warnings
aws apigateway import-rest-api \
    --fail-on-warnings \
    --body file://swagger.json

# Import API with parameters
aws apigateway import-rest-api \
    --parameters endpointConfigurationTypes=REGIONAL \
    --body file://swagger.json

# Update existing API from Swagger file
aws apigateway put-rest-api \
    --rest-api-id abc123 \
    --mode merge \
    --body file://swagger.json

# Overwrite existing API from Swagger file
aws apigateway put-rest-api \
    --rest-api-id abc123 \
    --mode overwrite \
    --body file://swagger.json

# Update API with fail on warnings
aws apigateway put-rest-api \
    --rest-api-id abc123 \
    --mode merge \
    --fail-on-warnings \
    --body file://swagger.json
```

### Test Invoke Method

```bash
# Test invoke a method
aws apigateway test-invoke-method \
    --rest-api-id abc123 \
    --resource-id resource-id \
    --http-method GET

# Test invoke with path parameters
aws apigateway test-invoke-method \
    --rest-api-id abc123 \
    --resource-id resource-id \
    --http-method GET \
    --path-with-query-string "/users/123"

# Test invoke with query string
aws apigateway test-invoke-method \
    --rest-api-id abc123 \
    --resource-id resource-id \
    --http-method GET \
    --path-with-query-string "/users?status=active&limit=10"

# Test invoke with headers
aws apigateway test-invoke-method \
    --rest-api-id abc123 \
    --resource-id resource-id \
    --http-method POST \
    --headers '{"Content-Type":"application/json","Authorization":"Bearer token123"}'

# Test invoke with body
aws apigateway test-invoke-method \
    --rest-api-id abc123 \
    --resource-id resource-id \
    --http-method POST \
    --body '{"name":"John","email":"john@example.com"}'

# Test invoke with stage variables
aws apigateway test-invoke-method \
    --rest-api-id abc123 \
    --resource-id resource-id \
    --http-method GET \
    --stage-variables '{"lambdaAlias":"dev"}'

# Test invoke with client certificate
aws apigateway test-invoke-method \
    --rest-api-id abc123 \
    --resource-id resource-id \
    --http-method GET \
    --client-certificate-id cert-id
```

### Generate SDK

```bash
# Generate JavaScript SDK
aws apigateway get-sdk \
    --rest-api-id abc123 \
    --stage-name prod \
    --sdk-type javascript \
    javascript-sdk.zip

# Generate Android SDK
aws apigateway get-sdk \
    --rest-api-id abc123 \
    --stage-name prod \
    --sdk-type android \
    android-sdk.zip

# Generate iOS SDK (Objective-C)
aws apigateway get-sdk \
    --rest-api-id abc123 \
    --stage-name prod \
    --sdk-type objectivec \
    ios-sdk.zip

# Generate iOS SDK (Swift)
aws apigateway get-sdk \
    --rest-api-id abc123 \
    --stage-name prod \
    --sdk-type swift \
    swift-sdk.zip

# Generate Java SDK
aws apigateway get-sdk \
    --rest-api-id abc123 \
    --stage-name prod \
    --sdk-type java \
    java-sdk.zip

# Generate Ruby SDK
aws apigateway get-sdk \
    --rest-api-id abc123 \
    --stage-name prod \
    --sdk-type ruby \
    ruby-sdk.zip

# Generate SDK with parameters
aws apigateway get-sdk \
    --rest-api-id abc123 \
    --stage-name prod \
    --sdk-type javascript \
    --parameters serviceName='MyAPI' \
    javascript-sdk.zip

# Get available SDK types
aws apigateway get-sdk-types

# Get specific SDK type details
aws apigateway get-sdk-type \
    --id javascript
```

### Additional Useful Commands

```bash
# Get API Gateway resource policy
aws apigateway get-rest-api \
    --rest-api-id abc123 \
    --query 'policy' \
    --output text

# Update resource policy
aws apigateway update-rest-api \
    --rest-api-id abc123 \
    --patch-operations op=replace,path=/policy,value=file://resource-policy.json

# Create VPC Link for private integrations
aws apigateway create-vpc-link \
    --name "MyVPCLink" \
    --target-arns "arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/net/my-nlb/abc123"

# Get VPC links
aws apigateway get-vpc-links

# Get specific VPC link
aws apigateway get-vpc-link \
    --vpc-link-id vpc-link-id

# Delete VPC link
aws apigateway delete-vpc-link \
    --vpc-link-id vpc-link-id

# Create client certificate
aws apigateway generate-client-certificate \
    --description "Client certificate for backend authentication"

# Get client certificates
aws apigateway get-client-certificates

# Get specific client certificate
aws apigateway get-client-certificate \
    --client-certificate-id cert-id

# Delete client certificate
aws apigateway delete-client-certificate \
    --client-certificate-id cert-id

# Flush stage cache
aws apigateway flush-stage-cache \
    --rest-api-id abc123 \
    --stage-name prod

# Tag API
aws apigateway tag-resource \
    --resource-arn "arn:aws:apigateway:us-east-1::/restapis/abc123" \
    --tags Environment=Production,Owner=TeamA

# Get tags
aws apigateway get-tags \
    --resource-arn "arn:aws:apigateway:us-east-1::/restapis/abc123"

# Untag API
aws apigateway untag-resource \
    --resource-arn "arn:aws:apigateway:us-east-1::/restapis/abc123" \
    --tag-keys Environment Owner
```

### Common Query Patterns

```bash
# Get all REST API IDs and names
aws apigateway get-rest-apis \
    --query 'items[*].[id,name]' \
    --output table

# Get root resource ID for an API
aws apigateway get-resources \
    --rest-api-id abc123 \
    --query 'items[?path==`/`].id' \
    --output text

# List all resources with their paths
aws apigateway get-resources \
    --rest-api-id abc123 \
    --query 'items[*].[path,id]' \
    --output table

# Get deployment ID for a stage
aws apigateway get-stage \
    --rest-api-id abc123 \
    --stage-name prod \
    --query 'deploymentId' \
    --output text

# Get API endpoint URL
aws apigateway get-rest-api \
    --rest-api-id abc123 \
    --query 'id' \
    --output text | \
    xargs -I {} echo "https://{}.execute-api.us-east-1.amazonaws.com/prod"

# Check if API key is enabled
aws apigateway get-api-key \
    --api-key key-id \
    --query 'enabled' \
    --output text

# Get usage plan quota
aws apigateway get-usage-plan \
    --usage-plan-id plan-id \
    --query 'quota' \
    --output json
```

---

## Common Scenarios and Use Cases

### Enterprise Integration Patterns

#### 1. API Gateway as Enterprise Service Bus
**Scenario**: Large enterprise with multiple backend systems needing unified API access.

**Architecture**:
```
External Clients → API Gateway → Multiple Backend Services
                      ↓
                  Routing Logic
                      ↓
              ┌─────────────────┐
              │ Legacy SOAP     │
              │ Modern REST     │
              │ Database Direct │
              │ File Systems    │
              └─────────────────┘
```

**Implementation**:
- Use REST API for transformation capabilities
- VTL templates for format conversion (XML ↔ JSON)
- Lambda authorizers for complex authorization
- Caching for frequently accessed reference data
- API keys and usage plans for client management

#### 2. Partner API Ecosystem
**Scenario**: Expose internal services to external partners with different access levels.

**Key Requirements**:
- Tiered access based on partner level (Bronze, Silver, Gold)
- Different rate limits per partner
- Audit trail of all partner API usage
- SLA monitoring and reporting

**Solution Architecture**:
- API Keys linked to usage plans for each tier
- CloudWatch detailed monitoring per partner
- Lambda authorizers for partner-specific business rules
- Custom domains for white-label partner experience

### Modern Application Patterns

#### 3. Serverless E-commerce Platform
**Scenario**: Build scalable e-commerce platform with microservices architecture.

**Services Architecture**:
```
API Gateway (HTTP API)
├── /auth → Cognito + Lambda (Authentication)
├── /products → Lambda → DynamoDB (Product Catalog)
├── /cart → Lambda → DynamoDB (Shopping Cart)
├── /orders → Lambda → DynamoDB + SQS (Order Processing)
├── /payments → Lambda → Third-party Payment API
└── /notifications → Lambda → SNS (Email/SMS)
```

**Key Decisions**:
- HTTP API for cost optimization (70% savings)
- Cognito User Pools for customer authentication
- API Gateway direct DynamoDB integration for simple reads
- Lambda for complex business logic
- SQS for asynchronous order processing

#### 4. Mobile Backend as a Service (MBaaS)
**Scenario**: Mobile app backend supporting iOS and Android applications.

**Requirements**:
- User authentication and authorization
- Push notifications
- File upload/download
- Offline sync capabilities
- Real-time features (chat, notifications)

**Architecture Components**:
```
Mobile Apps → API Gateway → Backend Services
    ↓
┌─ REST API (CRUD operations)
├─ WebSocket API (real-time features) 
└─ Cognito (user management)
    ↓
Backend Services:
├─ Lambda (business logic)
├─ DynamoDB (user data, app state)
├─ S3 (file storage with presigned URLs)
├─ SNS (push notifications)
└─ AppSync (GraphQL for complex queries)
```

### Data Processing and Analytics

#### 5. IoT Data Ingestion Platform
**Scenario**: Collect and process data from thousands of IoT devices.

**Challenges**:
- High volume, variable traffic patterns
- Device authentication and authorization
- Data transformation and routing
- Real-time processing requirements

**Solution Architecture**:
```
IoT Devices → API Gateway (HTTP API) → Kinesis Data Streams
                   ↓
           Certificate-based auth
                   ↓
        Lambda (data transformation)
                   ↓
         ┌─ Kinesis Analytics (real-time)
         ├─ Kinesis Firehose → S3 (batch)
         └─ DynamoDB (device state)
```

**Implementation Details**:
- HTTP API for cost-effective device communication
- IAM roles for device authentication
- API Gateway → Kinesis integration for high throughput
- Lambda for data validation and enrichment

#### 6. Real-time Analytics Dashboard
**Scenario**: Provide real-time analytics dashboard for business users.

**Requirements**:
- Sub-second data freshness
- High concurrent user support
- Complex aggregation queries
- Interactive drill-down capabilities

**Architecture**:
```
Dashboard (Web) → API Gateway → Lambda → ElastiCache Redis
       ↓                           ↓
WebSocket API              Real-time data pipeline:
(live updates)             Kinesis → Lambda → Redis
```

**Key Features**:
- REST API for initial data load and queries
- WebSocket API for real-time updates
- ElastiCache Redis for fast analytics queries
- Lambda for aggregation and caching logic

### Legacy System Modernization

#### 7. Mainframe Integration
**Scenario**: Expose legacy mainframe applications through modern REST APIs.

**Legacy Constraints**:
- COBOL applications with fixed-format data
- Batch processing windows
- Limited concurrent connections
- Custom protocols (not HTTP)

**Modernization Strategy**:
```
Modern Apps → API Gateway (REST) → Lambda → SQS → Legacy Adapter → Mainframe
                    ↓                           ↓
            Request transformation      Async processing
            Response caching           Queue management
```

**Implementation**:
- REST API for request/response transformation using VTL
- Caching to reduce mainframe load
- SQS for asynchronous processing during batch windows
- Lambda for protocol translation and error handling

#### 8. Microservices Decomposition
**Scenario**: Gradually decompose monolithic application into microservices.

**Migration Strategy - Strangler Fig Pattern**:
```
Phase 1: API Gateway → Monolith (all traffic)
Phase 2: API Gateway → Mix (some endpoints to microservices)
Phase 3: API Gateway → Microservices (monolith retired)
```

**Route-based Migration**:
```javascript
// API Gateway routing logic
if (request.path.startsWith('/users')) {
    // Route to new User Service
    return userMicroservice.handle(request);
} else if (request.path.startsWith('/orders')) {
    // Route to new Order Service  
    return orderMicroservice.handle(request);
} else {
    // Route to legacy monolith
    return monolith.handle(request);
}
```

### Security and Compliance Scenarios

#### 9. HIPAA-Compliant Healthcare API
**Scenario**: Healthcare data API requiring HIPAA compliance.

**Compliance Requirements**:
- End-to-end encryption
- Audit logging of all access
- Access controls and authorization
- Data anonymization capabilities

**Security Architecture**:
```
Healthcare Apps → WAF → API Gateway → VPC → HIPAA-compliant services
       ↓              ↓         ↓        ↓
   Strong auth   DDoS protect  Audit logs  Encrypted data
   (Multi-factor)  Geo-blocking  CloudTrail   KMS encryption
```

**Implementation**:
- Cognito with MFA for user authentication
- Lambda authorizers for RBAC (doctor, nurse, admin roles)
- VPC endpoints for private communication
- CloudTrail for comprehensive audit logging
- KMS encryption for data at rest and in transit

#### 10. Financial Services API (PCI DSS)
**Scenario**: Payment processing API requiring PCI DSS compliance.

**Security Controls**:
- Tokenization of sensitive data
- Network segmentation
- Strong authentication and authorization
- Comprehensive logging and monitoring

**Architecture**:
```
Payment Apps → CloudFront (WAF) → API Gateway → Lambda → Secure Vault
                    ↓                  ↓           ↓         ↓
              Rate limiting      IAM auth    Tokenization  Encrypted storage
              IP whitelisting    API keys    Data masking  HSM key management
```

### Performance and Scale Scenarios

#### 11. High-Frequency Trading API
**Scenario**: Ultra-low latency API for financial trading applications.

**Performance Requirements**:
- Sub-millisecond response times
- 99.99% availability
- Handle traffic spikes during market events
- Global distribution for worldwide traders

**Optimization Strategy**:
```
Global Users → Route 53 (latency routing) → Regional API Gateways
                           ↓
              Edge-optimized endpoints with CloudFront
                           ↓
               Direct AWS service integrations
                           ↓
                    ElastiCache (microsecond latency)
```

**Key Optimizations**:
- Regional API deployments in major financial centers
- Direct DynamoDB integration (no Lambda overhead)
- DAX (DynamoDB Accelerator) for microsecond latency
- ElastiCache Redis for real-time market data

#### 12. Global Content Distribution
**Scenario**: Content API serving millions of users worldwide.

**Scaling Challenges**:
- Global user base with varying latency requirements
- Content localization and personalization
- Peak traffic during events (10x normal load)
- Cost optimization across regions

**Global Architecture**:
```
Users Worldwide → CloudFront (Edge Caching)
                      ↓
            Route 53 (Geolocation routing)
                      ↓
     Regional API Gateways (US, EU, APAC)
                      ↓
        Regional Lambda + DynamoDB Global Tables
```

**Performance Optimizations**:
- Edge-optimized API Gateway with CloudFront
- Multi-level caching (CloudFront + API Gateway + Application)
- DynamoDB Global Tables for low-latency global access
- Regional Lambda deployments for localized processing

### Exam Strategy Tips

#### Pattern Recognition
When analyzing exam scenarios, identify:

1. **Traffic Patterns**: High/low volume, predictable/variable, global/regional
2. **Security Requirements**: Public/private, authentication needs, compliance
3. **Performance Needs**: Latency requirements, scalability needs
4. **Cost Constraints**: Budget limitations, optimization opportunities
5. **Integration Complexity**: Simple proxy vs. transformation needs

#### Decision Framework
```
Is it real-time bidirectional? → WebSocket API
Is cost the primary concern? → HTTP API  
Need advanced features? → REST API
Need caching? → REST API (only option)
Need transformations? → REST API + VTL
Simple Lambda proxy? → HTTP API
Complex auth logic? → Lambda Authorizers
User-facing auth? → Cognito User Pools
Internal AWS services? → IAM Authentication
```

#### Cost-Performance Trade-offs
- **Cheapest**: HTTP API + Direct service integration
- **Most Features**: REST API + Lambda integration + Caching
- **Best Performance**: Edge-optimized + Multi-level caching + Regional deployment
- **Highest Security**: Private API + VPC endpoints + WAF + Lambda authorizers
