# Practice Test 04 — Answers

1. **B** — X-Ray shows where time is spent across services and identifies bottlenecks.
2. **B** — Logs Insights provides SQL-like queries against CloudWatch Logs.
3. **A** — Reserved concurrency of 0 throttles all invocations; low reserved limits cap max concurrency.
4. **B** — IteratorAge measures lag between record arrival and processing — high value = backlog.
5. **A** — EMF embeds metrics in structured log lines; CloudWatch extracts them automatically.
6. **B** — Provisioned Concurrency keeps execution environments warm, eliminating cold starts.
7. **B** — Lambda billing = memory × duration; faster execution at higher memory can reduce total cost (Power Tuning).
8. **B** — Structured JSON with request/correlation IDs enables effective Logs Insights queries.
9. **B** — Fault = 4xx client error; Error = 5xx server/unhandled exception in X-Ray terminology.
10. **A** — CloudWatch Alarm on Errors metric → SNS topic → email/SMS/Lambda notification.
11. **B** — Cache key derived from configured request parameters; identical keys return cached response.
12. **B** — DAX is an in-memory cache specifically for DynamoDB with microsecond latency.
13. **B** — Filter policies prevent delivering irrelevant messages to subscribers, reducing Lambda invocations.
14. **B** — Private subnet Lambda needs NAT Gateway for internet or VPC endpoints for AWS service APIs.
15. **B** — CloudFormation stack events show exactly which resource failed and why during deployment.
