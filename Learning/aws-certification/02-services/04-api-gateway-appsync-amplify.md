# API Gateway, AppSync, and Amplify

SAA 2.1 (API creation). DVA 1.1.6, 3.2.3, 3.4.2, 3.4.10. SAP uses API Gateway as the front door in a new design and rarely asks Amplify details.

Official:

- https://docs.aws.amazon.com/apigateway/latest/developerguide/welcome.html
- https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-vs-rest.html
- https://docs.aws.amazon.com/appsync/latest/devguide/what-is-appsync.html
- https://docs.aws.amazon.com/amplify/latest/userguide/welcome.html

## Three front doors

| Door | Pick it when |
| --- | --- |
| API Gateway REST | API keys, usage plans, request validation, mapping templates, caching, WAF, resource policies, the full older feature set |
| API Gateway HTTP API | Lower cost and latency, JWT authorizer, Lambda and HTTP proxy, OIDC. You do not need the REST-only features |
| ALB | The caller is inside the VPC or you already have an ALB and the routes are simple HTTP to ECS or Lambda. No usage plans |
| AppSync | GraphQL, several data sources in one query, mobile clients that want subscriptions over WebSocket |
| Amplify | A web or mobile app that wants hosting, auth, and an API generated together. The fastest path, and the least control |
| Function URL | One Lambda, IAM or NONE auth, no stages, no WAF on the URL itself unless you put CloudFront in front |

"Least operational overhead" for a single function and a team that accepts no API management is a function URL or an HTTP API. A partner who needs a key and a quota is REST plus a usage plan.

## REST versus HTTP API, the features that decide it

| Feature | REST | HTTP API |
| --- | --- | --- |
| Usage plans and API keys | Yes | No |
| Caching | Yes | No. Use CloudFront |
| Mapping templates and VTL | Yes | No. Lambda proxy or a parameter mapping |
| Request validation | Yes | Limited |
| WAF | Yes | Yes, in current regional HTTP APIs. Confirm if the stem is old. CloudFront plus WAF always works |
| Cognito and Lambda authorizers | Yes | JWT and Lambda authorizers |
| Private API via interface endpoint | Yes | VPC links for private integrations. Private API product is the REST feature |
| Price | Higher | Lower |

## Integrations

Lambda proxy puts the HTTP request in the event and expects `{statusCode, headers, body}` back. Custom integration uses mapping templates and you set the status from the template. Proxy is what you want unless the backend is not Lambda and cannot speak HTTP.

| Integration | Use |
| --- | --- |
| Lambda proxy | Application code |
| HTTP proxy | An existing HTTP service or an ALB |
| AWS service (REST) | Call S3, DynamoDB, Step Functions directly. No Lambda. IAM in the method. Good when the transform is trivial |
| VPC link | A private ALB or NLB or Cloud Map service. The API stays public or private while the target stays private |
| Mock | A test response without a backend |

Async: the method returns 202 and the work goes to SQS or Step Functions. API Gateway's 29-second integration timeout is why.

## Stages, variables, domains

A stage is `dev` or `prod` on the same API, with its own throttle, logs, and stage variables. A stage variable can be a Lambda alias ARN. Changing it shifts the stage to a new alias without a new deployment package. That is DVA skill 3.4.10.

Canary on a REST stage sends a percent of traffic to a new deployment. Rollback is setting the percent to zero.

Custom domains: ACM in the same Region for regional APIs. For edge-optimized REST APIs the cert is in us-east-1. Base-path mappings send `api.example.com/orders` to one stage and `/billing` to another.

```bash
aws apigateway create-stage --rest-api-id "$API" --stage-name prod --deployment-id "$DEP"
aws apigateway update-stage --rest-api-id "$API" --stage-name prod \
  --patch-operations op=replace,path=/variables/alias,value=live
```

## Auth

| Method | What the caller presents | What it authorizes |
| --- | --- | --- |
| IAM | SigV4 | `execute-api:Invoke`. Good for service-to-service |
| Cognito user pool | JWT | The user. Scopes map to methods |
| Lambda authorizer | A token or request parameters | Anything you can code. Cache the result on the token |
| JWT authorizer (HTTP API) | A JWT from any OIDC issuer | Issuer and audience |
| API key | A key header | A usage plan. Not authentication. Anyone with the key is that plan. Do not use a key as a user identity |
| Resource policy | The caller's principal or VPC or IP | A private API or an allow-list of accounts |

NONE on a function URL is public. The exam will offer it as a trap next to IAM auth.

## Throttling and caching

Account-level throttle, stage throttle, method throttle, usage plan throttle. A usage plan is how you give partner A 100 requests per second and partner B 10. WAF rate-based rules are the coarser edge limit and also stop floods that never should reach the method.

REST caching keys on the method, the path, query strings, and headers you list. If `Authorization` is not in the key, user A's response can be served to user B. If it is in the key, the cache hit rate collapses. Cache public GET responses. Do not cache personalized ones at the API layer. Cache them in the app with a tenant key if you must.

## AppSync

GraphQL schema, resolvers, data sources (DynamoDB, Lambda, Aurora, HTTP, OpenSearch, EventBridge). Pipeline resolvers chain them. Subscriptions are WebSockets. Cognito, IAM, OIDC, or a Lambda authorizer protects the API. AppSync is the answer when the client needs to ask for a shape of data and you would otherwise write a backend-for-frontend. It is the wrong answer when the client is a simple REST partner with a usage plan.

## Amplify

Hosting for a static web app with CI from a branch, Amplify Auth on Cognito, Amplify Data on AppSync or a REST API, and a backend environment per branch. DVA 3.3.3 names Amplify branches as an environment mechanism. Use Amplify when the stem is a front-end team and speed. Use CDK or SAM when the stem is a platform team that wants reviewable infrastructure.

Device Farm is on the SAA in-scope list for real-device tests. It is not how you deploy.

## Exercises

1. Partners need an API key and a daily quota. Lambda is the backend. REST or HTTP API?
2. The same API serves `dev` and `prod`. Prod must call the `live` alias and dev the `staging` alias without two code packages. What feature?
3. Users report seeing another user's account JSON on a GET that API Gateway caches. What was included in the cache key, and what should have been?
4. A mobile client needs one round trip that reads a profile from DynamoDB and the last five orders from Aurora, plus live order updates. Which front door?
5. The integration takes 40 seconds. API Gateway returns an error. The Lambda is still running. How do you redesign the HTTP contract?

## Answers

1. REST API, usage plan, API key. HTTP APIs do not have usage plans.
2. Stage variables that hold the alias, and the integration points at the variable. Or two stages of one API.
3. The cache key did not include the authorization header or a user identifier, so a shared response was stored. Remove caching for that method or include the user dimension and accept a low hit rate. Better: do not cache private payloads at the edge of the API.
4. AppSync, with DynamoDB and Aurora data sources and a subscription on the order. API Gateway would be two calls and a separate WebSocket API.
5. Return 202 with a job id, push the work to SQS or Step Functions, and let the client poll or subscribe. Do not raise the Lambda timeout and hope API Gateway waits. It will not wait past its integration limit.

## REST, HTTP, and WebSocket

| API | You pay the complexity for | You refuse it when |
| --- | --- | --- |
| REST | API keys, usage plans, request validators, mapping templates, AWS service integrations, resource policies | The backend is Lambda and you do not need those features. HTTP APIs are cheaper |
| HTTP | Lambda proxy, JWT authorizers, a lower price | You need a usage plan or a mapping template |
| WebSocket | A persistent connection, clients that must receive pushes | A request-response CRUD API. That is HTTP |

Proxy integration passes the request through and expects your status code. Custom integration uses a mapping template (VTL on REST) to reshape the body before and after. A Lambda that returns a Python dict where `body` should be a string produces a 502. A handler that returns 200 after a failed write produces a green client and a lying alarm.

Endpoint types on REST: regional (the default you want behind CloudFront or for clients in one Region), edge-optimized (a CloudFront distribution API Gateway creates, older), and private (reachable only from a VPC through an interface endpoint). A private API plus a resource policy that allows the VPC endpoint is the "no public API" answer. An HTTP API does not offer the same private endpoint story. Read the stem's API type before you promise a private REST feature.

## Auth, throttle, cache

| Caller | Authorizer |
| --- | --- |
| User pool JWT | Cognito or JWT authorizer. Verify issuer, audience, signature, expiry |
| IAM principal | `AWS_IAM`. SigV4. The caller's identity policy and the API's resource policy |
| A token you own that is not Cognito | Lambda authorizer. Cache the result only as long as you can tolerate a revoked token |
| A public webhook | None, plus a signature check you write, or a usage plan if they are partners with keys |

Usage plans and API keys are a REST feature. They are not authentication. A key in a query string will leak into logs. Put it in a header if you must use keys, and prefer IAM or JWT for anything that identifies a person.

Stage throttling protects you. Usage-plan throttling protects you from one partner. Account-level limits still exist. A WAF rate-based rule is the HTTP abuse control in front. Caching is per stage and per method. The cache key must vary on whatever changes the body. Authorization headers omitted from the key are how one user sees another's JSON. Do not cache a method that returns private data unless you have a reason and a key that includes the user. TTL and encryption of the cache are stage settings.

Stage variables point one API at different Lambda aliases or table names per stage. They are not a secret store. Anyone who can read the API configuration can read them.

## AppSync and Amplify

AppSync is GraphQL. Resolvers read DynamoDB, relational sources, or Lambda. Subscriptions are the live-update path. Use it when the client needs a shape you do not want to turn into five REST calls, or when the stem says GraphQL. Do not rewrite a simple CRUD API onto GraphQL for fashion. Authorization is Cognito, IAM, OIDC, or an API key. An API key is the least appropriate for user-specific data.

Amplify hosts a front end per branch and wires Cognito and an API. It is the front-end team's speed path. A platform team that wants reviewable infrastructure uses CDK or SAM. Device Farm is real-device testing. It is on the SAA list and it is not a deploy tool.

## The 29-second contract

The integration timeout is about 29 seconds. The Lambda can be configured for 15 minutes and still be abandoned by the client. Long work: return 202, enqueue, poll or subscribe. Timeouts that are shorter than the downstream's p99 are an outage you deployed. Timeouts that are longer than the gateway will wait are theater.

Mutual TLS on a custom domain is the "clients must present a certificate" control. WAF attaches to the API. Shield Standard covers the edge when the API is behind CloudFront. Access logs should not print the body or the Authorization header.

## More exercises

6. A private REST API is still reachable from the internet. What did you leave as the endpoint type?
7. A Lambda authorizer caches for an hour. You revoke a user and they keep calling. What setting?
8. Dev and prod are two stages. A secret was stored in a stage variable. Who can read it?
9. The method is `GET /orders/{id}` and caching is on. Two users requested different ids and got the same body. What is missing from the cache key?
10. The stem says GraphQL subscriptions for order status, plus a REST partner who only needs a usage plan. Do you force one API type?

## Answers

6. Regional or edge, with a resource policy that still allows the public, or no resource policy. A private API is only reachable through the interface endpoint. The resource policy should allow that endpoint and deny the rest.
7. Lower the authorizer result TTL. An hour is how long a revoked token still works. Five minutes or less if revocation has to be felt the same day. Zero checks every call and costs more.
8. Anyone who can `apigateway:GET` on that API. Move the secret to Secrets Manager. The stage variable can hold the secret's name, not the secret.
9. The path parameter was not part of the cache key, so different ids shared one entry. Include the id, and do not cache the method at all if the body is private to the caller.
10. No. AppSync for the subscription client. A REST API with a usage plan for the partner. One product that is bad at the other's feature is how both clients suffer.
