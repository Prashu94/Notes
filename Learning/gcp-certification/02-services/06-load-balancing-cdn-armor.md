# Load balancing, CDN, DNS edge, and Cloud Armor

ACE 2.3. PCA 1.3 and 2.1. DNS itself is in the VPC chapter. This chapter is how user traffic arrives.

## Decision table

Google’s current names are **Application Load Balancer** (layer 7), **Proxy Network Load Balancer** (layer 4 proxy), and **Passthrough Network Load Balancer** (layer 4, client IP preserved). Older exam stems still say “HTTP(S) load balancer”, “SSL proxy”, “TCP proxy”, “network load balancer”.

| Need | Product | Scope |
| --- | --- | --- |
| HTTPS for a website or API, URL map, Cloud CDN, Cloud Armor, serverless | Global external Application Load Balancer | Global. Premium tier. |
| Same, but users and backends in one region only, Standard tier allowed | Regional external Application Load Balancer | Regional |
| Internal microservice HTTP | Regional internal Application Load Balancer | Regional |
| Non-HTTP TCP with TLS terminated at the proxy, or TCP proxy | External proxy Network Load Balancer | Global or regional |
| Preserve client source IP, TCP or UDP, any port, no proxy | External passthrough Network Load Balancer | Regional |
| Internal TCP/UDP, preserve source IP | Internal passthrough Network Load Balancer | Regional |
| Multi-region active-active web | Global external Application Load Balancer plus backends in several regions | Global |

Backend types: instance groups, zonal NEGs (VMs or containers), serverless NEGs (Cloud Run, App Engine, Cloud Run functions), hybrid NEGs (on-prem via Interconnect or VPN), Private Service Connect NEGs.

Health checks are required for managed instance group backends. Serverless NEGs do not use the same VM health check.

```bash
gcloud compute health-checks create http web-hc --port=80 --request-path=/healthz

gcloud compute backend-services create web-bes \
  --protocol=HTTP --port-name=http --health-checks=web-hc \
  --global --load-balancing-scheme=EXTERNAL_MANAGED \
  --enable-cdn

gcloud compute backend-services add-backend web-bes \
  --instance-group=web-mig --instance-group-region="$REGION" \
  --global

gcloud compute url-maps create web-map --default-service=web-bes

gcloud compute target-http-proxies create web-proxy --url-map=web-map

gcloud compute forwarding-rules create web-fr \
  --global --target-http-proxy=web-proxy --ports=80 \
  --address=lb-ip
```

For HTTPS, create an SSL certificate (Google-managed needs a domain you control) and a target HTTPS proxy. HTTP-to-HTTPS redirect is a separate URL map and forwarding rule.

Internal passthrough is the answer for “database VIP inside the VPC” when you are not using the database’s own managed endpoint. Most managed databases do not need you to build this.

## Cloud CDN and Media CDN

Cloud CDN caches HTTP(S) responses at the edge, in front of an external Application Load Balancer or a backend bucket (Cloud Storage).

Use it for static objects, images, and cacheable API GETs. Do not cache personalized responses unless the cache key includes the right header or cookie, and you meant to.

**Media CDN** is the video-scale CDN. Pick it when the stem is large-object video delivery, not a normal website. Altostrat-style media libraries often want Cloud CDN or Media CDN plus Cloud Storage, not a Filestore mounted worldwide.

```bash
gcloud compute backend-buckets create static-bb \
  --gcs-bucket-name=BUCKET --enable-cdn

gcloud compute url-maps add-path-matcher web-map \
  --path-matcher-name=static \
  --default-service=web-bes \
  --backend-bucket-path-rules="/assets/*=static-bb"
```

Cache invalidation:

```bash
gcloud compute url-maps invalidate-cdn-cache web-map --path="/assets/*"
```

## Cloud Armor

Attaches to a backend service of an external Application Load Balancer. It does not attach to a passthrough network load balancer.

- Google’s DDoS protection on global load balancers is already there. Cloud Armor is the policy you write: geo, IP allow and deny, preconfigured WAF (OWASP), rate limiting, bot management.
- Named a **security policy**, bound to the backend service.
- Adaptive protection looks for layer-7 anomalies.

```bash
gcloud compute security-policies create edge --description="web"
gcloud compute security-policies rules create 1000 \
  --security-policy=edge \
  --expression="origin.region_code == 'CN'" \
  --action=deny-403

gcloud compute security-policies rules create 2000 \
  --security-policy=edge \
  --expression="evaluatePreconfiguredWaf('xss-v33-stable')" \
  --action=deny-403

gcloud compute backend-services update web-bes --global --security-policy=edge
```

If the stem says “block a country and SQL injection on the public site”, the pair is global external Application Load Balancer plus Cloud Armor. A VPC firewall cannot see HTTP paths.

## SSL, certificates, domains

- **Certificate Manager** and Google-managed certificates terminate TLS at the load balancer.
- **Cloud DNS** points the domain at the global anycast address.
- **mTLS** at the load balancer is for API clients that present certificates. It is a PCA recognition item.
- Internal TLS can terminate at the internal Application Load Balancer or at the pod.

## Service Extensions and Cloud Service Mesh

Service Extensions (plugins on the load-balancing data path) are recognition. Cloud Service Mesh is east-west. The external load balancer is north-south. Do not merge them in an answer unless the stem has both internet clients and service-to-service policy.

## Exercises

1. UDP game traffic, client IP must be visible to the server, one region. Which load balancer?
2. A public website needs a WAF and caching of `/static`. Which two products, in front of what?
3. Cloud Run is the only backend, plus Cloud Armor. What NEG do you add?
4. Why can Cloud Armor not be the answer for an internal passthrough load balancer?

### Answers

1. External passthrough Network Load Balancer (regional network load balancer).
2. Global external Application Load Balancer, Cloud Armor on the backend service, Cloud CDN on the static backend bucket or backend service.
3. A serverless NEG pointing at the Cloud Run service, attached to an external Application Load Balancer, then the Armor policy on that backend service.
4. Armor policies attach to Application Load Balancer backend services. Passthrough does not terminate HTTP and does not host that policy.
