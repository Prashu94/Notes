# Edge: Route 53, CloudFront, Global Accelerator, WAF, Shield

SAA 1.2, 2.2, 3.4. SAP 2.2 and 3.3.

Official:

- https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/routing-policy.html
- https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/Introduction.html
- https://docs.aws.amazon.com/global-accelerator/latest/dg/what-is-global-accelerator.html
- https://docs.aws.amazon.com/waf/latest/developerguide/what-is-aws-waf.html
- https://docs.aws.amazon.com/waf/latest/developerguide/shield-chapter.html

## Route 53 policies

| Policy | Use |
| --- | --- |
| Simple | One answer. No health check logic |
| Failover | Primary and secondary. Active-passive |
| Weighted | Percentages. Canary, migration cutover |
| Latency | Lowest latency Region for that user. Active-active |
| Geolocation | Continent, country, or state. Legal routing of users |
| Geoproximity | Bias. Requires Traffic Flow |
| IP-based | A CIDR of clients, such as a partner office |
| Multivalue | Several healthy answers. Not a load balancer |
| ARC routing controls | You flip the control. Use it when health checks lie |

Alias records point at AWS resources (ALB, CloudFront, S3 website, API Gateway, Global Accelerator) and are free of the usual query charge at the apex. A CNAME cannot sit at the zone apex. Use an alias.

Private hosted zones are for names inside VPCs. They are not how the public internet finds you.

Health checks watch an endpoint, another health check, or a CloudWatch alarm. Failover records need them. A TTL of 300 keeps a change from sticking for a day. Do not set a day-long TTL on a record you plan to fail over.

## CloudFront versus Global Accelerator

| | CloudFront | Global Accelerator |
| --- | --- | --- |
| Cache | Yes | No |
| Protocol | HTTP and HTTPS | TCP and UDP, and HTTP |
| Address | Changes with the edge | Two static anycast IPs |
| Typical stem | Static and cacheable HTTP, WAF at the edge | Gaming, IoT, non-HTTP, fast Regional failover, a stable IP for a firewall allow-list |

Origin access control (OAC) is how CloudFront reads a private S3 bucket. The older origin access identity still appears in old templates. New designs use OAC. Do not make the bucket public so CloudFront can read it.

Cache keys: path, query strings you name, headers you name, cookies you name. Putting `Authorization` in the key stops a shared cache from leaking a user. It also stops the cache from hitting. Cache the public object. Do not cache the account JSON.

Certificates for CloudFront are in us-east-1. Certificates for a regional ALB are in the ALB's Region.

## Load balancers

| Balancer | Pick it |
| --- | --- |
| ALB | HTTP, path and host rules, Lambda targets, Cognito on the listener, one balancer for many apps |
| NLB | TCP, UDP, TLS, static IP, extreme performance, the front of a PrivateLink service |
| Gateway Load Balancer | A fleet of firewall appliances. GENEVE. Not your app router |
| CLB | Legacy. Do not choose it for a new design |

ALB needs two AZs. Cross-zone load balancing is on by default for ALB. For NLB it is a choice and it has a data charge. Idle timeout and sticky sessions are the app-compatibility knobs. Sticky sessions are the compromise when session state is on the instance.

## WAF and Shield

Shield Standard is on for CloudFront and Route 53 and the load balancers. Shield Advanced is the paid product: the response team, cost protection on some resource types, and tighter integration. Pick Advanced when the stem is a large public estate or they name the DRT. Do not pick it to "turn on DDoS protection" for a tiny internal app. Standard is already there.

WAF attaches to CloudFront, ALB, API Gateway, and AppSync. Managed rule groups, rate-based rules, bot control, a SQL injection group. A rule on the ALB does not see cache hits at CloudFront. Put the ACL on the distribution if that is the user path.

Firewall Manager pushes WAF, Shield Advanced, security groups, and Network Firewall policies across an organization. It is the "one security team, many accounts" answer. It needs Organizations.

## Commands

```bash
aws route53 list-hosted-zones
aws route53 change-resource-record-sets --hosted-zone-id "$ZONE" --change-batch file://failover.json
aws cloudfront create-distribution --distribution-config file://cf.json
aws wafv2 list-web-acls --scope CLOUDFRONT --region us-east-1
aws elbv2 create-load-balancer --name app --subnets "$PUB_A" "$PUB_B" --security-groups "$SG" --type application
```

CloudFront WAF scope is `CLOUDFRONT` and the call is made against us-east-1. Regional ALB WAF scope is `REGIONAL`.

## Exercises

1. A game uses UDP and the publisher's firewall can allow only two IPs. CloudFront or Global Accelerator?
2. A failover record points at an ALB. The TTL is 86400. The AZ is fine and the Region is not. Why does failover feel slow even after the health check fails?
3. Users get each other's profile JSON from a CloudFront cache. What was wrong with the cache key?
4. WAF on the ALB, CloudFront in front with caching. A SQL injection payload is served from cache. Where must the ACL live to see that request the first time, and where must it live to see requests CloudFront still forwards?

## Answers

1. Global Accelerator. Two static anycast IPs. CloudFront is not the UDP answer and does not give you that stable pair as the product's point.
2. Resolvers will keep the old answer for up to a day. Lower the TTL before you depend on failover. Health checks do not purge the world's caches.
3. The cache key did not include a user identifier or the authorization header, so one response was stored for many users. Stop caching that path, or include the user dimension and accept that it will rarely hit.
4. On CloudFront, so the first request is inspected before it is stored. An ALB ACL only sees what CloudFront forwards to the origin. A cached error or a cached page never reaches the ALB.

## Route 53, the routing policies

A public hosted zone answers the internet. A private hosted zone answers associated VPCs and does not leak to the internet. Peering two VPCs does not associate the zone. Health checks are optional and are what make failover mean something.

| Policy | You are doing | The trap |
| --- | --- | --- |
| Simple | One answer, no health check | You thought it would fail over. It will not |
| Failover | Primary and secondary, the primary has a health check | The TTL is a day, so the world keeps the old answer. Or the health check is TCP and the app is returning 500 |
| Weighted | A percentage, which is how you shift a migration | Weights with no health check keep sending traffic at a dead endpoint |
| Latency | The lowest-latency healthy Region | You wanted a country-specific legal answer. That is geolocation |
| Geolocation | Content or an endpoint chosen by the user's location | You wanted performance. A user in a country you did not list gets the default record, which you forgot to create |
| Geoproximity | Latency plus a bias you set | Rare. Do not pick it when geolocation or latency is the plain fit |
| Multivalue | Several healthy answers | Not a load balancer. Clients pick. There is no connection draining |
| Alias | A Route 53 record aimed at an AWS resource such as an ALB or CloudFront, at the zone apex | A CNAME at the apex, which DNS does not allow. The alias is the answer for `example.com` to an ALB |

A health check from outside the VPC cannot see a private IP. You health-check the public endpoint, or you use a CloudWatch alarm as the health check for a private resource. Failover without a health check never moves. ARC routing controls are the Professional tool when the health check would stay green during a gray failure.

## CloudFront

An origin is S3 or a custom origin (ALB, HTTP server). Origin access control is how an S3 origin stays private and CloudFront is the only reader. The old origin access identity is the legacy version. A public bucket plus CloudFront fails Domain 1.

Cache policies decide the TTL and the cache key. A long TTL is right for an image that changes monthly, and you invalidate or you change the object key when it does change. A TTL of zero is right for a response that must not be stored. The cache key must include whatever makes the response vary: a header, a cookie, a query string. If it does not include the user, user A's profile is user B's profile. Caching a response that contains a secret is the same bug.

Certificates for a custom domain are ACM in `us-east-1`. The origin can be in any Region. Field-level encryption and signed URLs or signed cookies are the "only some clients may fetch this private content" feature. Signed URLs are not presigned S3 URLs, though both are time-limited capabilities. A signed CloudFront URL still goes through the distribution.

Origin failover uses an origin group. The secondary origin is used when the primary fails the health criteria. That is HTTP failover, not UDP, and not a replacement for a second-Region database.

Price classes drop expensive edges. They are a cost answer when the users are not in those geographies. They are the wrong answer when users in those geographies are the stem.

## Global Accelerator

Two static anycast IPs, on the AWS edge network, forwarding TCP or UDP to Regional endpoints. No cache. Failover between Regions is on the order of seconds and does not wait for DNS TTL. Use it for games, IoT, UDP, non-cacheable traffic, and any stem that says the client allow-lists IP addresses. Do not use it to cache images. Do not use CloudFront for UDP.

You can put CloudFront behind a design and Accelerator in front of a different design. You rarely stack them because someone said both words. Pick from the protocol and the cache.

## WAF and Shield

WAF inspects HTTP. It attaches to CloudFront, ALB, API Gateway, and AppSync. It does not attach to an NLB or to a network interface. Managed rule groups cover the common SQL injection and bad-bot sets. A rate-based rule is the abuse limit. Custom rules match a header, an IP set, or a body. A web ACL on the ALB does not see what CloudFront served from cache. Put the ACL on the distribution if that is the front door. Scope `CLOUDFRONT` is only in `us-east-1`. Scope `REGIONAL` is in the ALB's Region. Firewall Manager pushes the same web ACL across accounts.

Shield Standard is already on CloudFront and Route 53. You do not buy it. Shield Advanced adds the response team, cost protection, and stronger integration with a WAF, and it is an organization-scale purchase. A single small site with no cost-protection sentence does not need Advanced. A security group is not a DDoS product.

## Load balancers, only the edge decisions

ALB is HTTP and the usual origin behind CloudFront or the usual front door without CloudFront. It needs two subnets in two AZs. NLB is TCP and UDP and the static IP, and it is what PrivateLink requires. Gateway Load Balancer is appliances. CloudFront in front of an ALB is the global HTTP design. Global Accelerator in front of an NLB is the global non-HTTP design. An ALB with a public IP per instance behind it is the design you delete.

## More exercises

5. `example.com` must point at an ALB. A CNAME was rejected. What record do you create?
6. Geolocation sends European users to the EU stack. Users in a country you did not configure get NXDOMAIN. What record is missing?
7. Shield Advanced is proposed for one static site on S3 and CloudFront, with no uptime credit requirement. What is already protecting it?
8. A private API in a VPC must fail over in DNS when a CloudWatch alarm fires. The health check cannot connect to the private IP. What do you attach the failover record to?
9. Signed CloudFront URLs or an S3 presigned URL: the bucket is private, the only path should be CloudFront, and the client must not learn the S3 URL.

## Answers

5. An alias A or AAAA record aimed at the ALB. DNS forbids a CNAME at the zone apex. The alias is the Route 53 feature that looks like a CNAME and works at the apex, and it is free of the usual query charge when it targets an AWS alias target.
6. A default geolocation record. Without it, unmatched locations do not fall through to the EU or US record. They fail.
7. Shield Standard, which is already on CloudFront. WAF if they have an HTTP threat. Advanced is the answer when they ask for the response team or for cost protection. It is not the default for a static site.
8. A health check that is based on the CloudWatch alarm, not on an HTTP probe of the private IP. Route 53's public checkers cannot see inside the VPC. Calculated health checks and CloudWatch-alarm health checks are the private-resource pattern.
9. A signed CloudFront URL or a signed cookie, with origin access control so the bucket rejects everyone except the distribution. An S3 presigned URL bypasses CloudFront and hands the client the bucket path. That fails "the only path is CloudFront."
