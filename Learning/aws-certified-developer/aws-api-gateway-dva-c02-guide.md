# Amazon API Gateway — DVA-C02 Developer Guide

REST API management for serverless and microservice backends. Heavily tested with Lambda and Cognito integration.

**Official docs:** [Amazon API Gateway Developer Guide](https://docs.aws.amazon.com/apigateway/latest/developerguide/welcome.html)

---

## Core Concepts

```
Client → API Gateway → Integration (Lambda, HTTP, AWS service)
              │
              ├── Stage (dev, prod)
              ├── Deployment (immutable snapshot)
              ├── Method (GET, POST, etc.)
              ├── Resource (/users/{id})
              └── Authorizer (Cognito, IAM, Lambda)
```

### API Types

| Type | Use case | Exam focus |
|------|----------|------------|
| **REST API** | Full-featured, Lambda proxy | ⭐ Primary exam focus |
| **HTTP API** | Lower cost, lower latency, simpler | Awareness |
| **WebSocket API** | Real-time bidirectional | Awareness |

---

## Lambda Proxy Integration (Most Common)

API Gateway passes **entire request** to Lambda; Lambda returns **API response format**.

**Event structure (key fields):**
```python
def lambda_handler(event, context):
    http_method = event['httpMethod']           # GET, POST
    path = event['path']                         # /users/123
    path_params = event['pathParameters']        # {'id': '123'}
    query_params = event['queryStringParameters'] # {'page': '1'}
    headers = event['headers']
    body = event.get('body')                     # JSON string
    claims = event.get('requestContext', {}).get('authorizer', {}).get('claims', {})
```

**Required response format:**
```python
return {
    'statusCode': 200,
    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
    'body': json.dumps({'userId': '123', 'name': 'Alice'})
}
```

---

## Stages and Deployments

| Concept | Description |
|---------|-------------|
| **Deployment** | Immutable snapshot of API configuration |
| **Stage** | Named pointer to deployment (`dev`, `prod`, `v1`) |
| **Stage variables** | Key-value config per stage (`{lambdaAlias: prod}`) |
| **Canary release** | Gradual traffic shift to new deployment |

**Critical:** Changes to API don't take effect until you **create a deployment** and **assign to stage**.

### Stage Variables with Lambda

Integration URI:
```
arn:aws:lambda:us-east-1:123456789012:function:MyFunction:${stageVariables.lambdaAlias}
```

`dev` stage: `lambdaAlias=dev` → `$LATEST`  
`prod` stage: `lambdaAlias=prod` → Alias `prod`

---

## Authorization

| Authorizer | Validates | Header | Use case |
|------------|-----------|--------|----------|
| **NONE** | Open (use other auth) | — | Public endpoints |
| **IAM (AWS Signature V4)** | AWS credentials | Authorization | Service-to-service |
| **Cognito User Pool** | JWT token | Authorization: Bearer | User-facing apps |
| **Lambda authorizer** | Custom logic | Token or request | Custom auth schemes |

### Cognito Authorizer Flow

```
1. User authenticates with Cognito User Pool → JWT access token
2. Client: Authorization: Bearer eyJhbG...
3. API Gateway validates JWT (signature, expiry, audience)
4. Lambda receives claims in event.requestContext.authorizer.claims
```

---

## Request Validation

```yaml
# Enable validator on method
RequestValidatorId: !Ref BodyValidator
RequestModels:
  application/json: !Ref OrderModel
```

Returns **400 Bad Request** before invoking Lambda if validation fails — saves Lambda invocations.

---

## Caching

| Setting | Description |
|---------|-------------|
| Enable caching | Per-stage, per-method |
| Cache key | Query params, headers (configurable) |
| TTL | 0–3600 seconds (default 300) |
| Encryption | Optional at rest |
| Invalidate | Flush entire stage cache or per-key |

**Exam:** "Reduce DynamoDB reads for repeated GET requests" → API Gateway caching.

---

## Throttling

| Level | Default | Purpose |
|-------|---------|---------|
| **Account** | 10,000 RPS (can increase) | Overall API limit |
| **Stage** | Configurable | Per-environment limits |
| **Method** | Configurable | Protect specific endpoints |
| **Usage plan + API key** | Per-client limits | Rate limit external consumers |

Returns **429 Too Many Requests** when exceeded.

---

## CORS

For browser clients, API must return CORS headers:

**Option 1:** Enable CORS in API Gateway console (adds OPTIONS method)

**Option 2:** Return from Lambda:
```python
return {
    'statusCode': 200,
    'headers': {
        'Access-Control-Allow-Origin': 'https://myapp.com',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization'
    },
    'body': json.dumps(data)
}
```

---

## AWS Service Integration (No Lambda)

Direct integration with AWS services:
- **DynamoDB** — PutItem, GetItem via VTL mapping templates
- **S3** — GetObject
- **Step Functions** — StartExecution
- **SQS** — SendMessage

Use when simple CRUD without custom logic — lower latency and cost than Lambda.

---

## Exam Scenarios

| Scenario | Answer |
|----------|--------|
| Pass full HTTP request to Lambda | Lambda proxy integration |
| Different Lambda versions per environment | Stage variables + Lambda aliases |
| Authenticate users with JWT | Cognito User Pool authorizer |
| Service-to-service auth | IAM authorization (SigV4) |
| Reduce repeated GET load on backend | API Gateway caching |
| Rate limit external API consumers | Usage plans + API keys |
| Custom token validation | Lambda authorizer |
| API changes not visible | Must deploy to stage |
| Lambda returns 502 | Lambda exception or timeout (>29s sync limit) |

---

## Related Guides

- [Lambda Guide](aws-lambda-dva-c02-guide.md)
- [Security Guide](aws-security-dva-c02-guide.md) — Cognito integration
- [Concepts Deep Dive](CONCEPTS-DEEP-DIVE.md#api-gateway-integration-patterns)
