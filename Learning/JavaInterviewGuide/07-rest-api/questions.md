# REST API Design — 50 Senior Interview Questions

**Bar:** Contracts, idempotency, error semantics, evolution. CRUD mapping is the floor.

---

### 1. REST vs RPC vs HTTP-as-transport.

**Short answer:** REST models resources with uniform HTTP verbs and standard status semantics; RPC names procedures (`POST /createOrder`); HTTP-as-transport just uses HTTP without REST constraints. Most production JSON APIs are pragmatic hybrids—consistency matters more than purity. Document the contract in OpenAPI with examples and enforce it in CI with contract tests. Pair HTTP semantics with observability: correlation ids, structured Problem Details, and SLO dashboards on p99 latency.

#### What it is

REST (Representational State Transfer) treats URLs as nouns (resources) and uses GET/PUT/PATCH/DELETE with predictable semantics. RPC-style APIs expose actions as endpoints or method names. HTTP-as-transport means you carry JSON over HTTP but ignore safe/idempotent rules, caching, and resource modeling.

#### How it works (internals)

REST relies on stateless requests, representations (JSON), and optional hypermedia. RPC often maps 1:1 to service methods—gRPC, SOAP, or `POST /doPayment`. Spring `@RestController` can implement either; the framework does not enforce REST. Caches, proxies, and CDNs only help when you follow verb semantics (especially GET safety).

#### When to use / when NOT to use

Use REST when you want cacheable reads, clear CRUD, and public contracts. Use RPC when the domain is action-heavy (payments capture, workflow transitions) or when an internal gRPC mesh already exists. Do not claim HATEOAS if every client hardcodes paths from OpenAPI.

#### Production example

An order service exposes `GET /orders/{id}` and `POST /orders` with 201 + Location. A legacy billing integration uses `POST /billing/charge` (RPC) behind an API gateway that still returns Problem Details and idempotency keys—same transport, different style, documented explicitly. Runbooks should name the status codes, headers, and idempotency behavior operators will see during incidents.

#### Common mistakes

Calling every JSON API 'RESTful' while using POST for everything. Mixing styles in one surface (`GET /orders` but `POST /getOrderById`). Ignoring HTTP semantics and then wondering why CDN caching breaks authenticated reads.

#### Interview follow-ups (with model answers)

**Q:** How would you expose a state transition like 'cancel order' in a REST-consistent way?
**A:** For «REST vs RPC vs HTTP-as-transport.», idempotency is not optional decoration — it is part of the HTTP contract clients rely on when gateways retry or mobile apps replay requests. I store idempotency keys with a unique constraint, return the same response body on replay, and document TTL in OpenAPI. Spring `@RestController` advice maps domain exceptions to RFC 7807 Problem Details with stable `type` URIs. In staging I replay recorded traffic and run openapi-diff on every PR so breaking changes fail CI before partners see them.

**Q:** When would you choose gRPC internally and REST at the edge?
**A:** The follow-on risk for «When would you choose gRPC internally and REST at the edge» is inconsistent behavior across versions — v1 clients still calling deprecated fields while v2 expects structured money objects. I version via URL prefix or vendor media type, add `Sunset` and `Deprecation` headers, and metric traffic by version label. Spring validation groups separate create vs update DTOs; `@ControllerAdvice` ensures 409 on conflict instead of silent overwrites. Operators need runbook steps: which status codes are retryable, which require a new Idempotency-Key, and how BFF translates upstream errors without double-wrapping JSON.

**Q:** What breaks if GET is not safe?
**A:** Trade-off framing for «What breaks if GET is not safe»: optimize for integrator stability over internal convenience. Public APIs get cursor pagination, explicit error envelopes, rate-limit headers, and contract tests; internal admin endpoints may use offset pages but still need authz and tracing. I walk one real endpoint through the checklist: safe GET, idempotent PUT/DELETE, POST with keys for money paths, ETag on updates, and OpenAPI examples for 400/404/409/412. If I cannot explain retry semantics to a mobile engineer in two minutes, the design is not ready for production.

#### Scenario probe

**Situation:** After a release, traffic on endpoints touching «REST vs RPC vs HTTP-as-transport.» shows rising p99 latency and occasional duplicate side effects; mobile clients retry on gateway timeouts and support sees mismatched error JSON across services.

**Model answer:** I treat this as a contract and retry problem first, not a 'scale up pods' problem. I capture `X-Request-Id` across BFF and downstream services, compare Problem Details shapes, and replay a failing call with the same `Idempotency-Key` to see if POST is safe. Context: An order service exposes `GET /orders/{id}` and `POST /orders` with 201 + Location. A legacy billing integration uses `POST /billing/charge` (RPC) behind an API gateway that still returns Problem Deta. I verify GET safety, idempotent PUT/DELETE behavior, and whether Spring controllers return 409/412 instead of silent overwrites. OpenAPI diff against last release tells me if a field became required without a version bump. Short-term: tighten gateway timeouts with retry only on idempotent methods, fix error envelope in shared `@ControllerAdvice`. Long-term: contract tests, versioned DTOs, metrics on duplicate idempotency hits, and runbook steps for on-call.

#### Code / config (when useful)
```java
@PostMapping("/orders/{id}/cancellation")
public ResponseEntity<OrderDto> cancel(@PathVariable UUID id) {
    return ResponseEntity.ok(orderService.cancel(id));
}
```

---

### 2. Resource modeling: nouns, not verbs.

**Short answer:** URLs identify resources (`/orders`, `/customers/{id}`), not actions. Non-CRUD operations become sub-resources or POST to a well-named action under a resource. Keep nesting shallow—two or three levels is usually enough. Document the contract in OpenAPI with examples and enforce it in CI with contract tests.

#### What it is

Resource modeling is how you name and structure URIs so clients can predict endpoints. Nouns represent things in your domain; HTTP verbs express what to do with them. This sits at the boundary between HTTP transport, Spring MVC dispatch, and client SDK expectations.

#### How it works (internals)

Collections use plural nouns (`/orders`). Items use path segments (`/orders/{orderId}/line-items`). Actions that are not simple CRUD become subordinate resources (`POST /orders/{id}/cancellation`) rather than verbs in the path (`/cancelOrder`).

#### When to use / when NOT to use

Use noun-based paths for anything you will document in OpenAPI and cache. Avoid deep trees (`/orgs/1/teams/2/projects/3/tasks/4`)—prefer flat IDs with query filters or embed summaries. Do not create a resource for every internal service method.

#### Production example

E-commerce API: `POST /payments` creates a payment resource; `GET /payments/{id}` polls status. Refunds are `POST /payments/{id}/refunds`, not `POST /refundPayment`. Spring maps `@GetMapping("/orders/{id}")` on an `OrderController`.

#### Common mistakes

Verb endpoints (`/searchOrders`, `/updateStatus`). Inconsistent pluralization (`/order` vs `/orders`). Encoding business workflow steps as five nested path segments instead of a flat resource with state.

#### Interview follow-ups (with model answers)

**Q:** How do you model 'archive' vs 'delete'?
**A:** For «Resource modeling: nouns, not verbs.», OpenAPI is not optional decoration — it is part of the HTTP contract clients rely on when gateways retry or mobile apps replay requests. I store idempotency keys with a unique constraint, return the same response body on replay, and document TTL in OpenAPI. Spring `@RestController` advice maps domain exceptions to RFC 7807 Problem Details with stable `type` URIs. In staging I replay recorded traffic and run openapi-diff on every PR so breaking changes fail CI before partners see them.

**Q:** When is a sub-resource better than a query parameter?
**A:** The follow-on risk for «When is a sub-resource better than a query parameter» is inconsistent behavior across versions — v1 clients still calling deprecated fields while v2 expects structured money objects. I version via URL prefix or vendor media type, add `Sunset` and `Deprecation` headers, and metric traffic by version label. Spring validation groups separate create vs update DTOs; `@ControllerAdvice` ensures 409 on conflict instead of silent overwrites. Operators need runbook steps: which status codes are retryable, which require a new Idempotency-Key, and how BFF translates upstream errors without double-wrapping JSON.

**Q:** How do you avoid god-resources that expose 40 operations?
**A:** Trade-off framing for «How do you avoid god-resources that expose 40 operations»: optimize for integrator stability over internal convenience. Public APIs get cursor pagination, explicit error envelopes, rate-limit headers, and contract tests; internal admin endpoints may use offset pages but still need authz and tracing. I walk one real endpoint through the checklist: safe GET, idempotent PUT/DELETE, POST with keys for money paths, ETag on updates, and OpenAPI examples for 400/404/409/412. If I cannot explain retry semantics to a mobile engineer in two minutes, the design is not ready for production.

#### Scenario probe

**Situation:** After a release, traffic on endpoints touching «Resource modeling: nouns, not verbs.» shows rising p99 latency and occasional duplicate side effects; mobile clients retry on gateway timeouts and support sees mismatched error JSON across services.

**Model answer:** I treat this as a contract and retry problem first, not a 'scale up pods' problem. I capture `X-Request-Id` across BFF and downstream services, compare Problem Details shapes, and replay a failing call with the same `Idempotency-Key` to see if POST is safe. Context: E-commerce API: `POST /payments` creates a payment resource; `GET /payments/{id}` polls status. Refunds are `POST /payments/{id}/refunds`, not `POST /refundPayment`. Spring maps `@GetMapping("/orders/. I verify GET safety, idempotent PUT/DELETE behavior, and whether Spring controllers return 409/412 instead of silent overwrites. OpenAPI diff against last release tells me if a field became required without a version bump. Short-term: tighten gateway timeouts with retry only on idempotent methods, fix error envelope in shared `@ControllerAdvice`. Long-term: contract tests, versioned DTOs, metrics on duplicate idempotency hits, and runbook steps for on-call.

---

### 3. GET must be safe; PUT/DELETE idempotent; POST not necessarily.

**Short answer:** Safe methods (GET, HEAD, OPTIONS) must not change server state except harmless side effects like logging. Idempotent methods (PUT, DELETE) produce the same final state if repeated. POST is neither safe nor idempotent—retries can duplicate unless you add idempotency keys. Document the contract in OpenAPI with examples and enforce it in CI with contract tests.

#### What it is

HTTP method semantics are part of your contract. Clients, caches, and intermediaries assume GET never charges a card or sends email. Idempotency lets retries succeed without double effects.

#### How it works (internals)

A safe GET can be prefetched by browsers and cached by CDNs when Cache-Control allows. PUT replacing `/orders/{id}` with the same body twice leaves one order. DELETE twice should leave the resource absent (204). POST `POST /orders` creates a new resource each time unless deduplicated.

#### When to use / when NOT to use

Never put mutations on GET—even for 'simple' admin tools. Use POST with Idempotency-Key for payments and order creation. Use PUT/DELETE when clients or gateways may retry on network blips.

#### Production example

Checkout service: `GET /cart` is read-only. `POST /orders` creates orders; mobile clients send `Idempotency-Key` because POST retries are common on flaky networks. Spring Security audit logs still run on GET—that is acceptable.

#### Common mistakes

GET endpoint that marks notifications read. Assuming POST is idempotent because 'we only call it once.' Returning 200 with a body on DELETE when 204 is clearer. Teams often discover these failures only after mobile clients retry on flaky networks or CDNs cache a non-safe GET.

#### Interview follow-ups (with model answers)

**Q:** Is PATCH idempotent?
**A:** For «GET must be safe; PUT/DELETE idempotent; POST not necessarily.», Spring controllers is not optional decoration — it is part of the HTTP contract clients rely on when gateways retry or mobile apps replay requests. I store idempotency keys with a unique constraint, return the same response body on replay, and document TTL in OpenAPI. Spring `@RestController` advice maps domain exceptions to RFC 7807 Problem Details with stable `type` URIs. In staging I replay recorded traffic and run openapi-diff on every PR so breaking changes fail CI before partners see them.

**Q:** How do caches treat POST?
**A:** The follow-on risk for «How do caches treat POST» is inconsistent behavior across versions — v1 clients still calling deprecated fields while v2 expects structured money objects. I version via URL prefix or vendor media type, add `Sunset` and `Deprecation` headers, and metric traffic by version label. Spring validation groups separate create vs update DTOs; `@ControllerAdvice` ensures 409 on conflict instead of silent overwrites. Operators need runbook steps: which status codes are retryable, which require a new Idempotency-Key, and how BFF translates upstream errors without double-wrapping JSON.

**Q:** What status should a duplicate idempotent POST return?
**A:** Trade-off framing for «What status should a duplicate idempotent POST return»: optimize for integrator stability over internal convenience. Public APIs get cursor pagination, explicit error envelopes, rate-limit headers, and contract tests; internal admin endpoints may use offset pages but still need authz and tracing. I walk one real endpoint through the checklist: safe GET, idempotent PUT/DELETE, POST with keys for money paths, ETag on updates, and OpenAPI examples for 400/404/409/412. If I cannot explain retry semantics to a mobile engineer in two minutes, the design is not ready for production.

#### Scenario probe

**Situation:** After a release, traffic on endpoints touching «GET must be safe; PUT/DELETE idempotent; POST not necessarily.» shows rising p99 latency and occasional duplicate side effects; mobile clients retry on gateway timeouts and support sees mismatched error JSON across services.

**Model answer:** I treat this as a contract and retry problem first, not a 'scale up pods' problem. I capture `X-Request-Id` across BFF and downstream services, compare Problem Details shapes, and replay a failing call with the same `Idempotency-Key` to see if POST is safe. Context: Checkout service: `GET /cart` is read-only. `POST /orders` creates orders; mobile clients send `Idempotency-Key` because POST retries are common on flaky networks. Spring Security audit logs still run. I verify GET safety, idempotent PUT/DELETE behavior, and whether Spring controllers return 409/412 instead of silent overwrites. OpenAPI diff against last release tells me if a field became required without a version bump. Short-term: tighten gateway timeouts with retry only on idempotent methods, fix error envelope in shared `@ControllerAdvice`. Long-term: contract tests, versioned DTOs, metrics on duplicate idempotency hits, and runbook steps for on-call.

---

### 4. PUT vs PATCH vs POST.

**Short answer:** PUT replaces the entire resource at a known URI and is idempotent. PATCH applies a partial update (JSON Merge Patch or JSON Patch). POST creates a resource or triggers a controller action when the target URI is not fully known upfront. Document the contract in OpenAPI with examples and enforce it in CI with contract tests.

#### What it is

These verbs differ in scope and idempotency. PUT is 'set this resource to this representation.' PATCH is 'change these fields.' POST is the catch-all for creation and non-idempotent operations. This sits at the boundary between HTTP transport, Spring MVC dispatch, and client SDK expectations.

#### How it works (internals)

PUT sends a full representation; null/absent fields may clear data depending on your contract—document it. PATCH with RFC 7396 merge patch merges top-level keys; RFC 6902 JSON Patch sends operations (`add`, `remove`, `replace`). Spring supports both via `HttpMessageConverter` and `@PatchMapping`.

#### When to use / when NOT to use

PUT when clients send full objects (settings screens). PATCH for sparse mobile updates. POST for `POST /orders` (server assigns id) or search. PUT create-at-client-id (`PUT /orders/{uuid}`) is valid and idempotent for offline-first apps.

#### Production example

Profile API: `PATCH /users/me` with `{"displayName": "Ada"}` updates one field. Admin bulk replace uses `PUT /users/{id}` with full `UserDto`. Order placement stays `POST /orders` with 201.

#### Common mistakes

Using POST for updates because PATCH is 'hard.' PATCH without defining null vs omitted semantics. PUT that only updates changed fields silently—clients cannot tell full vs partial. Teams often discover these failures only after mobile clients retry on flaky networks or CDNs cache a non-safe GET.

#### Interview follow-ups (with model answers)

**Q:** JSON Merge Patch vs JSON Patch—which do you standardize on?
**A:** For «PUT vs PATCH vs POST.», versioning is not optional decoration — it is part of the HTTP contract clients rely on when gateways retry or mobile apps replay requests. I store idempotency keys with a unique constraint, return the same response body on replay, and document TTL in OpenAPI. Spring `@RestController` advice maps domain exceptions to RFC 7807 Problem Details with stable `type` URIs. In staging I replay recorded traffic and run openapi-diff on every PR so breaking changes fail CI before partners see them.

**Q:** How do you handle PATCH on nested collections?
**A:** The follow-on risk for «How do you handle PATCH on nested collections» is inconsistent behavior across versions — v1 clients still calling deprecated fields while v2 expects structured money objects. I version via URL prefix or vendor media type, add `Sunset` and `Deprecation` headers, and metric traffic by version label. Spring validation groups separate create vs update DTOs; `@ControllerAdvice` ensures 409 on conflict instead of silent overwrites. Operators need runbook steps: which status codes are retryable, which require a new Idempotency-Key, and how BFF translates upstream errors without double-wrapping JSON.

**Q:** PUT create-if-absent vs 409 if exists?
**A:** Trade-off framing for «PUT create-if-absent vs 409 if exists»: optimize for integrator stability over internal convenience. Public APIs get cursor pagination, explicit error envelopes, rate-limit headers, and contract tests; internal admin endpoints may use offset pages but still need authz and tracing. I walk one real endpoint through the checklist: safe GET, idempotent PUT/DELETE, POST with keys for money paths, ETag on updates, and OpenAPI examples for 400/404/409/412. If I cannot explain retry semantics to a mobile engineer in two minutes, the design is not ready for production.

#### Scenario probe

**Situation:** After a release, traffic on endpoints touching «PUT vs PATCH vs POST.» shows rising p99 latency and occasional duplicate side effects; mobile clients retry on gateway timeouts and support sees mismatched error JSON across services.

**Model answer:** I treat this as a contract and retry problem first, not a 'scale up pods' problem. I capture `X-Request-Id` across BFF and downstream services, compare Problem Details shapes, and replay a failing call with the same `Idempotency-Key` to see if POST is safe. Context: Profile API: `PATCH /users/me` with `{"displayName": "Ada"}` updates one field. Admin bulk replace uses `PUT /users/{id}` with full `UserDto`. Order placement stays `POST /orders` with 201. I verify GET safety, idempotent PUT/DELETE behavior, and whether Spring controllers return 409/412 instead of silent overwrites. OpenAPI diff against last release tells me if a field became required without a version bump. Short-term: tighten gateway timeouts with retry only on idempotent methods, fix error envelope in shared `@ControllerAdvice`. Long-term: contract tests, versioned DTOs, metrics on duplicate idempotency hits, and runbook steps for on-call.

#### Code / config (when useful)
```java
@PatchMapping(path = "/orders/{id}", consumes = "application/merge-patch+json")
public OrderDto patch(@PathVariable UUID id, @RequestBody JsonMergePatch patch) {
    return orderService.applyPatch(id, patch);
}
```

---

### 5. Idempotency-Key header (IETF draft practice).

**Short answer:** Clients send a unique `Idempotency-Key` on POST (and sometimes PATCH) so retries replay the stored response instead of executing twice. The server stores key + request fingerprint + response for 24–72 hours. Concurrent duplicates return 409 or block until the first completes. Document the contract in OpenAPI with examples and enforce it in CI with contract tests.

#### What it is

Idempotency keys are a client-generated token (UUID) that lets payment and order APIs survive retries without double charges. The pattern is widely used (Stripe, etc.) and documented in IETF drafts. This sits at the boundary between HTTP transport, Spring MVC dispatch, and client SDK expectations.

#### How it works (internals)

On first request, persist `(tenant, key, method, path, bodyHash)` in Redis or DB with status IN_PROGRESS. Execute business logic, store response status/body, mark COMPLETED. Retry with same key returns cached response; mismatched body with same key returns 422.

#### When to use / when NOT to use

Mandatory for money movement, inventory holds, and any POST where duplicate side effects are unacceptable. Skip for read-only analytics POST or idempotent PUT. Not a substitute for GET safety.

#### Production example

Spring filter reads `Idempotency-Key`, checks Redis, short-circuits if complete, or acquires a lock. Payment gateway timeout causes client retry—second request returns original 201 with same `paymentId`. Runbooks should name the status codes, headers, and idempotency behavior operators will see during incidents.

#### Common mistakes

Keys scoped globally instead of per tenant/API key. No TTL—table grows forever. Returning 500 on retry after success was persisted. Ignoring concurrent in-flight requests.

#### Interview follow-ups (with model answers)

**Q:** How do you hash the request body for conflict detection?
**A:** For «Idempotency-Key header (IETF draft practice).», idempotency is not optional decoration — it is part of the HTTP contract clients rely on when gateways retry or mobile apps replay requests. I store idempotency keys with a unique constraint, return the same response body on replay, and document TTL in OpenAPI. Spring `@RestController` advice maps domain exceptions to RFC 7807 Problem Details with stable `type` URIs. In staging I replay recorded traffic and run openapi-diff on every PR so breaking changes fail CI before partners see them.

**Q:** What if the first attempt times out but eventually succeeds?
**A:** The follow-on risk for «What if the first attempt times out but eventually succeeds» is inconsistent behavior across versions — v1 clients still calling deprecated fields while v2 expects structured money objects. I version via URL prefix or vendor media type, add `Sunset` and `Deprecation` headers, and metric traffic by version label. Spring validation groups separate create vs update DTOs; `@ControllerAdvice` ensures 409 on conflict instead of silent overwrites. Operators need runbook steps: which status codes are retryable, which require a new Idempotency-Key, and how BFF translates upstream errors without double-wrapping JSON.

**Q:** Idempotency-Key vs If-Match—when each?
**A:** Trade-off framing for «Idempotency-Key vs If-Match—when each»: optimize for integrator stability over internal convenience. Public APIs get cursor pagination, explicit error envelopes, rate-limit headers, and contract tests; internal admin endpoints may use offset pages but still need authz and tracing. I walk one real endpoint through the checklist: safe GET, idempotent PUT/DELETE, POST with keys for money paths, ETag on updates, and OpenAPI examples for 400/404/409/412. If I cannot explain retry semantics to a mobile engineer in two minutes, the design is not ready for production.

#### Scenario probe

**Situation:** After a release, traffic on endpoints touching «Idempotency-Key header (IETF draft practice).» shows rising p99 latency and occasional duplicate side effects; mobile clients retry on gateway timeouts and support sees mismatched error JSON across services.

**Model answer:** I treat this as a contract and retry problem first, not a 'scale up pods' problem. I capture `X-Request-Id` across BFF and downstream services, compare Problem Details shapes, and replay a failing call with the same `Idempotency-Key` to see if POST is safe. Context: Spring filter reads `Idempotency-Key`, checks Redis, short-circuits if complete, or acquires a lock. Payment gateway timeout causes client retry—second request returns original 201 with same `paymentI. I verify GET safety, idempotent PUT/DELETE behavior, and whether Spring controllers return 409/412 instead of silent overwrites. OpenAPI diff against last release tells me if a field became required without a version bump. Short-term: tighten gateway timeouts with retry only on idempotent methods, fix error envelope in shared `@ControllerAdvice`. Long-term: contract tests, versioned DTOs, metrics on duplicate idempotency hits, and runbook steps for on-call.

#### Code / config (when useful)
```java
@PostMapping("/payments")
public ResponseEntity<PaymentDto> pay(
    @RequestHeader("Idempotency-Key") String key,
    @RequestBody PaymentRequest req) {
  return idempotencyService.execute(key, () -> paymentService.charge(req));
}
```

---

### 6. Status codes you must not mix up.

**Short answer:** Use 201 for creation (with Location), 202 for async acceptance, 204 for success without body. Distinguish 400 (bad input) from 401 (unauthenticated) and 403 (forbidden). Use 404 for missing resources, 409 for conflicts, 412 for stale ETags, 429 for rate limits, 503 when dependencies are down. Document the contract in OpenAPI with examples and enforce it in CI with contract tests.

#### What it is

HTTP status codes communicate outcome class to clients, proxies, and retry logic. They are part of your API contract as much as JSON fields. This sits at the boundary between HTTP transport, Spring MVC dispatch, and client SDK expectations.

#### How it works (internals)

2xx success, 4xx client fault (usually no retry), 5xx server fault (retry with backoff). 401 triggers login flows; 403 means authenticated but denied. 422 is sometimes used for semantic validation; many teams use 400 with structured errors instead. Spring maps requests through `DispatcherServlet`, `HandlerMapping`, and `HttpMessageConverter` chains before your service layer runs.

#### When to use / when NOT to use

Map domain errors consistently—do not return 200 with `{error: true}`. Use 503 + `Retry-After` when the DB is unavailable; 500 for unexpected bugs. 404 vs 403: hide existence of other tenants' resources with 404 if policy requires. Prefer explicit documentation and gateway policies over tribal knowledge about which endpoints are safe to retry.

#### Production example

Order API returns 409 when cancelling a shipped order, 412 when `If-Match` ETag is stale, 429 when API gateway quota exceeded. Spring `@ResponseStatus` and `ProblemDetail` keep handlers uniform. Runbooks should name the status codes, headers, and idempotency behavior operators will see during incidents.

#### Common mistakes

401 for wrong password on a resource (should be 403 in some designs). 500 for validation errors. 200 for everything to 'simplify' mobile parsing. Teams often discover these failures only after mobile clients retry on flaky networks or CDNs cache a non-safe GET.

#### Interview follow-ups (with model answers)

**Q:** 404 vs 403 for BOLA—what do you return?
**A:** For «Status codes you must not mix up.», OpenAPI is not optional decoration — it is part of the HTTP contract clients rely on when gateways retry or mobile apps replay requests. I store idempotency keys with a unique constraint, return the same response body on replay, and document TTL in OpenAPI. Spring `@RestController` advice maps domain exceptions to RFC 7807 Problem Details with stable `type` URIs. In staging I replay recorded traffic and run openapi-diff on every PR so breaking changes fail CI before partners see them.

**Q:** When is 202 better than 201?
**A:** The follow-on risk for «When is 202 better than 201» is inconsistent behavior across versions — v1 clients still calling deprecated fields while v2 expects structured money objects. I version via URL prefix or vendor media type, add `Sunset` and `Deprecation` headers, and metric traffic by version label. Spring validation groups separate create vs update DTOs; `@ControllerAdvice` ensures 409 on conflict instead of silent overwrites. Operators need runbook steps: which status codes are retryable, which require a new Idempotency-Key, and how BFF translates upstream errors without double-wrapping JSON.

**Q:** Should gateway translate upstream 502 to 503?
**A:** Trade-off framing for «Should gateway translate upstream 502 to 503»: optimize for integrator stability over internal convenience. Public APIs get cursor pagination, explicit error envelopes, rate-limit headers, and contract tests; internal admin endpoints may use offset pages but still need authz and tracing. I walk one real endpoint through the checklist: safe GET, idempotent PUT/DELETE, POST with keys for money paths, ETag on updates, and OpenAPI examples for 400/404/409/412. If I cannot explain retry semantics to a mobile engineer in two minutes, the design is not ready for production.

#### Scenario probe

**Situation:** After a release, traffic on endpoints touching «Status codes you must not mix up.» shows rising p99 latency and occasional duplicate side effects; mobile clients retry on gateway timeouts and support sees mismatched error JSON across services.

**Model answer:** I treat this as a contract and retry problem first, not a 'scale up pods' problem. I capture `X-Request-Id` across BFF and downstream services, compare Problem Details shapes, and replay a failing call with the same `Idempotency-Key` to see if POST is safe. Context: Order API returns 409 when cancelling a shipped order, 412 when `If-Match` ETag is stale, 429 when API gateway quota exceeded. Spring `@ResponseStatus` and `ProblemDetail` keep handlers uniform. I verify GET safety, idempotent PUT/DELETE behavior, and whether Spring controllers return 409/412 instead of silent overwrites. OpenAPI diff against last release tells me if a field became required without a version bump. Short-term: tighten gateway timeouts with retry only on idempotent methods, fix error envelope in shared `@ControllerAdvice`. Long-term: contract tests, versioned DTOs, metrics on duplicate idempotency hits, and runbook steps for on-call.

---

### 7. RFC 7807 Problem Details.

**Short answer:** RFC 7807 defines `application/problem+json` with `type`, `title`, `status`, `detail`, and `instance` for machine- and human-readable errors. Spring Boot 3 provides `ProblemDetail` and `@ControllerAdvice` integration. Document the contract in OpenAPI with examples and enforce it in CI with contract tests. Pair HTTP semantics with observability: correlation ids, structured Problem Details, and SLO dashboards on p99 latency.

#### What it is

Problem Details standardize error bodies so clients do not parse ad-hoc `{message, code}` shapes per service. This sits at the boundary between HTTP transport, Spring MVC dispatch, and client SDK expectations.

#### How it works (internals)

`type` is a URI identifying the problem (often docs link). `title` is short and stable; `detail` is request-specific. Extensions add `errors[]` for field validation. Content-Type must be `application/problem+json`.

#### When to use / when NOT to use

Use across all public and partner APIs. Internal services can share the same envelope for BFF consistency. Do not wrap Problem Details inside another `{data, error}` gateway shell.

#### Production example

`@RestControllerAdvice` maps `OrderNotFoundException` to ProblemDetail with type `https://api.example.com/problems/order-not-found`, status 404, and `traceId` extension from MDC. Runbooks should name the status codes, headers, and idempotency behavior operators will see during incidents.

#### Common mistakes

Leaking stack traces in `detail`. Using generic `type` for every error. Inconsistent Content-Type (`application/json` with problem shape).

#### Interview follow-ups (with model answers)

**Q:** How do you internationalize `title` vs `detail`?
**A:** For «RFC 7807 Problem Details.», Spring controllers is not optional decoration — it is part of the HTTP contract clients rely on when gateways retry or mobile apps replay requests. I store idempotency keys with a unique constraint, return the same response body on replay, and document TTL in OpenAPI. Spring `@RestController` advice maps domain exceptions to RFC 7807 Problem Details with stable `type` URIs. In staging I replay recorded traffic and run openapi-diff on every PR so breaking changes fail CI before partners see them.

**Q:** Problem Details vs OAuth error format?
**A:** The follow-on risk for «Problem Details vs OAuth error format» is inconsistent behavior across versions — v1 clients still calling deprecated fields while v2 expects structured money objects. I version via URL prefix or vendor media type, add `Sunset` and `Deprecation` headers, and metric traffic by version label. Spring validation groups separate create vs update DTOs; `@ControllerAdvice` ensures 409 on conflict instead of silent overwrites. Operators need runbook steps: which status codes are retryable, which require a new Idempotency-Key, and how BFF translates upstream errors without double-wrapping JSON.

**Q:** How does Springdoc document error responses?
**A:** Trade-off framing for «How does Springdoc document error responses»: optimize for integrator stability over internal convenience. Public APIs get cursor pagination, explicit error envelopes, rate-limit headers, and contract tests; internal admin endpoints may use offset pages but still need authz and tracing. I walk one real endpoint through the checklist: safe GET, idempotent PUT/DELETE, POST with keys for money paths, ETag on updates, and OpenAPI examples for 400/404/409/412. If I cannot explain retry semantics to a mobile engineer in two minutes, the design is not ready for production.

#### Scenario probe

**Situation:** After a release, traffic on endpoints touching «RFC 7807 Problem Details.» shows rising p99 latency and occasional duplicate side effects; mobile clients retry on gateway timeouts and support sees mismatched error JSON across services.

**Model answer:** I treat this as a contract and retry problem first, not a 'scale up pods' problem. I capture `X-Request-Id` across BFF and downstream services, compare Problem Details shapes, and replay a failing call with the same `Idempotency-Key` to see if POST is safe. Context: `@RestControllerAdvice` maps `OrderNotFoundException` to ProblemDetail with type `https://api.example.com/problems/order-not-found`, status 404, and `traceId` extension from MDC. I verify GET safety, idempotent PUT/DELETE behavior, and whether Spring controllers return 409/412 instead of silent overwrites. OpenAPI diff against last release tells me if a field became required without a version bump. Short-term: tighten gateway timeouts with retry only on idempotent methods, fix error envelope in shared `@ControllerAdvice`. Long-term: contract tests, versioned DTOs, metrics on duplicate idempotency hits, and runbook steps for on-call.

#### Code / config (when useful)
```java
@ExceptionHandler(OrderNotFoundException.class)
ProblemDetail handle(OrderNotFoundException ex, HttpServletRequest req) {
  var pd = ProblemDetail.forStatusAndDetail(NOT_FOUND, ex.getMessage());
  pd.setType(URI.create("https://api.example.com/problems/order-not-found"));
  pd.setInstance(URI.create(req.getRequestURI()));
  return pd;
}
```

---

### 8. Validation errors: field-level.

**Short answer:** Return an array of field-level errors with `field`, `code`, and `message` so clients can highlight form inputs. Support multiple simultaneous violations—not just the first failure. Use stable codes for i18n; messages can be localized via Accept-Language. Document the contract in OpenAPI with examples and enforce it in CI with contract tests.

#### What it is

Field-level validation errors extend Problem Details (or sit in an `errors` extension) to tie server constraints to UI fields. This sits at the boundary between HTTP transport, Spring MVC dispatch, and client SDK expectations.

#### How it works (internals)

Spring `MethodArgumentNotValidException` exposes `BindingResult` with `FieldError` list. Map to `{field: "shipping.address.zip", code: "INVALID_FORMAT", message: "..."}`. OpenAPI documents constraints; runtime returns them on 400.

#### When to use / when NOT to use

Always for create/update endpoints consumed by forms. For machine clients, codes matter more than English messages. Do not use field errors for authorization failures—use 403 Problem Detail.

#### Production example

Checkout API validates `PaymentRequest` with Jakarta Bean Validation; `@ControllerAdvice` flattens to Problem Detail with `errors` array. React maps `field` paths to form inputs. Runbooks should name the status codes, headers, and idempotency behavior operators will see during incidents.

#### Common mistakes

Single string error for ten invalid fields. Returning 500 when validation fails. Field paths that do not match client JSON structure (`address.zip` vs `shippingAddress.zipCode`).

#### Interview follow-ups (with model answers)

**Q:** How do you validate nested objects and collections?
**A:** For «Validation errors: field-level.», versioning is not optional decoration — it is part of the HTTP contract clients rely on when gateways retry or mobile apps replay requests. I store idempotency keys with a unique constraint, return the same response body on replay, and document TTL in OpenAPI. Spring `@RestController` advice maps domain exceptions to RFC 7807 Problem Details with stable `type` URIs. In staging I replay recorded traffic and run openapi-diff on every PR so breaking changes fail CI before partners see them.

**Q:** Custom validators vs service-layer rules?
**A:** The follow-on risk for «Custom validators vs service-layer rules» is inconsistent behavior across versions — v1 clients still calling deprecated fields while v2 expects structured money objects. I version via URL prefix or vendor media type, add `Sunset` and `Deprecation` headers, and metric traffic by version label. Spring validation groups separate create vs update DTOs; `@ControllerAdvice` ensures 409 on conflict instead of silent overwrites. Operators need runbook steps: which status codes are retryable, which require a new Idempotency-Key, and how BFF translates upstream errors without double-wrapping JSON.

**Q:** 422 vs 400 for validation?
**A:** Trade-off framing for «422 vs 400 for validation»: optimize for integrator stability over internal convenience. Public APIs get cursor pagination, explicit error envelopes, rate-limit headers, and contract tests; internal admin endpoints may use offset pages but still need authz and tracing. I walk one real endpoint through the checklist: safe GET, idempotent PUT/DELETE, POST with keys for money paths, ETag on updates, and OpenAPI examples for 400/404/409/412. If I cannot explain retry semantics to a mobile engineer in two minutes, the design is not ready for production.

#### Scenario probe

**Situation:** After a release, traffic on endpoints touching «Validation errors: field-level.» shows rising p99 latency and occasional duplicate side effects; mobile clients retry on gateway timeouts and support sees mismatched error JSON across services.

**Model answer:** I treat this as a contract and retry problem first, not a 'scale up pods' problem. I capture `X-Request-Id` across BFF and downstream services, compare Problem Details shapes, and replay a failing call with the same `Idempotency-Key` to see if POST is safe. Context: Checkout API validates `PaymentRequest` with Jakarta Bean Validation; `@ControllerAdvice` flattens to Problem Detail with `errors` array. React maps `field` paths to form inputs. I verify GET safety, idempotent PUT/DELETE behavior, and whether Spring controllers return 409/412 instead of silent overwrites. OpenAPI diff against last release tells me if a field became required without a version bump. Short-term: tighten gateway timeouts with retry only on idempotent methods, fix error envelope in shared `@ControllerAdvice`. Long-term: contract tests, versioned DTOs, metrics on duplicate idempotency hits, and runbook steps for on-call.

#### Code / config (when useful)
```java
record FieldError(String field, String code, String message) {}

pd.setProperty("errors", bindingResult.getFieldErrors().stream()
    .map(fe -> new FieldError(fe.getField(), fe.getCode(), fe.getDefaultMessage()))
    .toList());
```

---

### 9. Pagination: offset vs cursor.

**Short answer:** Offset (`?page=3&size=20`) is simple but unstable under concurrent inserts and slow at deep offsets. Cursor (keyset) pagination uses an opaque token from the last row—stable, fast, but no arbitrary page jumps. Total counts are optional and expensive. Document the contract in OpenAPI with examples and enforce it in CI with contract tests.

#### What it is

Pagination limits response size for collections. Offset uses LIMIT/OFFSET; cursor uses indexed columns (`created_at`, `id`) from the previous page. This sits at the boundary between HTTP transport, Spring MVC dispatch, and client SDK expectations.

#### How it works (internals)

Offset: `SELECT * FROM orders ORDER BY created_at DESC LIMIT 20 OFFSET 40`—scans skipped rows. Cursor: `WHERE (created_at, id) < (:ts, :id) ORDER BY created_at DESC, id DESC LIMIT 20` using a composite index. Return `next_cursor` or Link header.

#### When to use / when NOT to use

Offset for admin UIs with small datasets and page numbers. Cursor for high-volume feeds, mobile infinite scroll, and replicated DBs. Avoid OFFSET 100000 in production.

#### Production example

Order history API returns `{items, nextCursor}`; cursor encodes `base64(createdAt|id)`. Spring Data `KeysetScrollPosition` or custom repository query. Runbooks should name the status codes, headers, and idempotency behavior operators will see during incidents.

#### Common mistakes

Exposing raw DB ids as cursors (enumeration). No max page size—clients request `size=10000`. Offset pagination on tables without sort index.

#### Interview follow-ups (with model answers)

**Q:** How do you paginate with filters?
**A:** For «Pagination: offset vs cursor.», idempotency is not optional decoration — it is part of the HTTP contract clients rely on when gateways retry or mobile apps replay requests. I store idempotency keys with a unique constraint, return the same response body on replay, and document TTL in OpenAPI. Spring `@RestController` advice maps domain exceptions to RFC 7807 Problem Details with stable `type` URIs. In staging I replay recorded traffic and run openapi-diff on every PR so breaking changes fail CI before partners see them.

**Q:** Expose total count or not?
**A:** The follow-on risk for «Expose total count or not» is inconsistent behavior across versions — v1 clients still calling deprecated fields while v2 expects structured money objects. I version via URL prefix or vendor media type, add `Sunset` and `Deprecation` headers, and metric traffic by version label. Spring validation groups separate create vs update DTOs; `@ControllerAdvice` ensures 409 on conflict instead of silent overwrites. Operators need runbook steps: which status codes are retryable, which require a new Idempotency-Key, and how BFF translates upstream errors without double-wrapping JSON.

**Q:** Bidirectional cursors for chat?
**A:** Trade-off framing for «Bidirectional cursors for chat»: optimize for integrator stability over internal convenience. Public APIs get cursor pagination, explicit error envelopes, rate-limit headers, and contract tests; internal admin endpoints may use offset pages but still need authz and tracing. I walk one real endpoint through the checklist: safe GET, idempotent PUT/DELETE, POST with keys for money paths, ETag on updates, and OpenAPI examples for 400/404/409/412. If I cannot explain retry semantics to a mobile engineer in two minutes, the design is not ready for production.

#### Scenario probe

**Situation:** After a release, traffic on endpoints touching «Pagination: offset vs cursor.» shows rising p99 latency and occasional duplicate side effects; mobile clients retry on gateway timeouts and support sees mismatched error JSON across services.

**Model answer:** I treat this as a contract and retry problem first, not a 'scale up pods' problem. I capture `X-Request-Id` across BFF and downstream services, compare Problem Details shapes, and replay a failing call with the same `Idempotency-Key` to see if POST is safe. Context: Order history API returns `{items, nextCursor}`; cursor encodes `base64(createdAt|id)`. Spring Data `KeysetScrollPosition` or custom repository query. I verify GET safety, idempotent PUT/DELETE behavior, and whether Spring controllers return 409/412 instead of silent overwrites. OpenAPI diff against last release tells me if a field became required without a version bump. Short-term: tighten gateway timeouts with retry only on idempotent methods, fix error envelope in shared `@ControllerAdvice`. Long-term: contract tests, versioned DTOs, metrics on duplicate idempotency hits, and runbook steps for on-call.

---

### 10. Filtering, sorting, sparse fieldsets.

**Short answer:** Use query parameters for filters (`status=OPEN`), sort (`sort=-createdAt`), and sparse fieldsets (`fields=id,status`). Whitelist sortable columns and filterable fields to prevent SQL injection and full-table scans. Document the contract in OpenAPI with examples and enforce it in CI with contract tests. Pair HTTP semantics with observability: correlation ids, structured Problem Details, and SLO dashboards on p99 latency.

#### What it is

Collection tuning lets clients narrow results without new endpoints. It must be bounded and indexed. This sits at the boundary between HTTP transport, Spring MVC dispatch, and client SDK expectations.

#### How it works (internals)

Parse `sort` into an allowlist map (`createdAt` -> `created_at`). Reject unknown fields with 400. `fields` projects DTOs or SELECT columns. Combine with pagination caps (`size` max 100).

#### When to use / when NOT to use

Use for list endpoints with predictable indexes. Do not expose arbitrary SQL-like queries in GET—use POST search for complex cases. Sparse fieldsets help mobile list views.

#### Production example

`GET /orders?status=SHIPPED&sort=-createdAt&fields=id,status,total` backed by composite index on `(tenant_id, status, created_at)`. Spring `@RequestParam` + specification pattern. Runbooks should name the status codes, headers, and idempotency behavior operators will see during incidents.

#### Common mistakes

Passing `sort=rawColumn` into SQL. Unbounded OR filters. Returning full entity graphs when `fields` was requested.

#### Interview follow-ups (with model answers)

**Q:** How do you implement multi-field sort?
**A:** For «Filtering, sorting, sparse fieldsets.», OpenAPI is not optional decoration — it is part of the HTTP contract clients rely on when gateways retry or mobile apps replay requests. I store idempotency keys with a unique constraint, return the same response body on replay, and document TTL in OpenAPI. Spring `@RestController` advice maps domain exceptions to RFC 7807 Problem Details with stable `type` URIs. In staging I replay recorded traffic and run openapi-diff on every PR so breaking changes fail CI before partners see them.

**Q:** GraphQL-style fields vs query param?
**A:** The follow-on risk for «GraphQL-style fields vs query param» is inconsistent behavior across versions — v1 clients still calling deprecated fields while v2 expects structured money objects. I version via URL prefix or vendor media type, add `Sunset` and `Deprecation` headers, and metric traffic by version label. Spring validation groups separate create vs update DTOs; `@ControllerAdvice` ensures 409 on conflict instead of silent overwrites. Operators need runbook steps: which status codes are retryable, which require a new Idempotency-Key, and how BFF translates upstream errors without double-wrapping JSON.

**Q:** How do filters interact with cursor pagination?
**A:** Trade-off framing for «How do filters interact with cursor pagination»: optimize for integrator stability over internal convenience. Public APIs get cursor pagination, explicit error envelopes, rate-limit headers, and contract tests; internal admin endpoints may use offset pages but still need authz and tracing. I walk one real endpoint through the checklist: safe GET, idempotent PUT/DELETE, POST with keys for money paths, ETag on updates, and OpenAPI examples for 400/404/409/412. If I cannot explain retry semantics to a mobile engineer in two minutes, the design is not ready for production.

#### Scenario probe

**Situation:** After a release, traffic on endpoints touching «Filtering, sorting, sparse fieldsets.» shows rising p99 latency and occasional duplicate side effects; mobile clients retry on gateway timeouts and support sees mismatched error JSON across services.

**Model answer:** I treat this as a contract and retry problem first, not a 'scale up pods' problem. I capture `X-Request-Id` across BFF and downstream services, compare Problem Details shapes, and replay a failing call with the same `Idempotency-Key` to see if POST is safe. Context: `GET /orders?status=SHIPPED&sort=-createdAt&fields=id,status,total` backed by composite index on `(tenant_id, status, created_at)`. Spring `@RequestParam` + specification pattern. I verify GET safety, idempotent PUT/DELETE behavior, and whether Spring controllers return 409/412 instead of silent overwrites. OpenAPI diff against last release tells me if a field became required without a version bump. Short-term: tighten gateway timeouts with retry only on idempotent methods, fix error envelope in shared `@ControllerAdvice`. Long-term: contract tests, versioned DTOs, metrics on duplicate idempotency hits, and runbook steps for on-call.

---

### 11. Versioning strategies.

**Short answer:** Common approaches are URI prefix (`/v1/orders`), custom media types (`Accept: application/vnd.example.v2+json`), or header-based versioning. Breaking changes require a new version plus deprecation headers (`Deprecation`, `Sunset`). Prefer additive evolution without a version bump when possible. Document the contract in OpenAPI with examples and enforce it in CI with contract tests.

#### What it is

API versioning is how you evolve contracts without breaking existing clients. The version can appear in the URL, headers, or content type. This sits at the boundary between HTTP transport, Spring MVC dispatch, and client SDK expectations.

#### How it works (internals)

URI versioning is explicit and easy to route at the gateway—`/v1` and `/v2` map to different Spring `@RequestMapping` packages or controller classes. Media-type versioning keeps URLs stable but complicates caching (Vary on Accept). Additive-only changes (new optional fields) avoid versioning entirely.

#### When to use / when NOT to use

URI `/v1` for public partner APIs where clarity beats purity. Media types when you must keep one URL for legal or cache reasons. Internal APIs can coordinate breaking changes with deploys—still document them.

#### Production example

Public payments API runs `/v1/payments` and `/v2/payments` in parallel for 12 months. Gateway adds `Deprecation: true` and `Sunset: Sat, 01 Mar 2027 00:00:00 GMT` on v1 responses while metrics track remaining traffic. Runbooks should name the status codes, headers, and idempotency behavior operators will see during incidents.

#### Common mistakes

Breaking changes without a version. Two versioning schemes at once (URL and header). Never sunsetting old versions. Versioning every minor field addition.

#### Interview follow-ups (with model answers)

**Q:** How do you route versions in Spring Cloud Gateway?
**A:** For «Versioning strategies.», Spring controllers is not optional decoration — it is part of the HTTP contract clients rely on when gateways retry or mobile apps replay requests. I store idempotency keys with a unique constraint, return the same response body on replay, and document TTL in OpenAPI. Spring `@RestController` advice maps domain exceptions to RFC 7807 Problem Details with stable `type` URIs. In staging I replay recorded traffic and run openapi-diff on every PR so breaking changes fail CI before partners see them.

**Q:** Version in OpenAPI—one spec or many?
**A:** The follow-on risk for «Version in OpenAPI—one spec or many» is inconsistent behavior across versions — v1 clients still calling deprecated fields while v2 expects structured money objects. I version via URL prefix or vendor media type, add `Sunset` and `Deprecation` headers, and metric traffic by version label. Spring validation groups separate create vs update DTOs; `@ControllerAdvice` ensures 409 on conflict instead of silent overwrites. Operators need runbook steps: which status codes are retryable, which require a new Idempotency-Key, and how BFF translates upstream errors without double-wrapping JSON.

**Q:** How long do you support deprecated versions?
**A:** Trade-off framing for «How long do you support deprecated versions»: optimize for integrator stability over internal convenience. Public APIs get cursor pagination, explicit error envelopes, rate-limit headers, and contract tests; internal admin endpoints may use offset pages but still need authz and tracing. I walk one real endpoint through the checklist: safe GET, idempotent PUT/DELETE, POST with keys for money paths, ETag on updates, and OpenAPI examples for 400/404/409/412. If I cannot explain retry semantics to a mobile engineer in two minutes, the design is not ready for production.

#### Scenario probe

**Situation:** After a release, traffic on endpoints touching «Versioning strategies.» shows rising p99 latency and occasional duplicate side effects; mobile clients retry on gateway timeouts and support sees mismatched error JSON across services.

**Model answer:** I treat this as a contract and retry problem first, not a 'scale up pods' problem. I capture `X-Request-Id` across BFF and downstream services, compare Problem Details shapes, and replay a failing call with the same `Idempotency-Key` to see if POST is safe. Context: Public payments API runs `/v1/payments` and `/v2/payments` in parallel for 12 months. Gateway adds `Deprecation: true` and `Sunset: Sat, 01 Mar 2027 00:00:00 GMT` on v1 responses while metrics track r. I verify GET safety, idempotent PUT/DELETE behavior, and whether Spring controllers return 409/412 instead of silent overwrites. OpenAPI diff against last release tells me if a field became required without a version bump. Short-term: tighten gateway timeouts with retry only on idempotent methods, fix error envelope in shared `@ControllerAdvice`. Long-term: contract tests, versioned DTOs, metrics on duplicate idempotency hits, and runbook steps for on-call.

---

### 12. Backward compatible JSON changes.

**Short answer:** Safe changes: add optional fields, add enum values clients should tolerate, widen formats carefully. Unsafe: remove or rename fields, change types, reuse field names with new meaning. Clients must ignore unknown fields (Postel's law). Document the contract in OpenAPI with examples and enforce it in CI with contract tests.

#### What it is

Backward compatibility means old clients keep working against new servers. Forward compatibility means new clients tolerate old servers—harder, plan feature detection. This sits at the boundary between HTTP transport, Spring MVC dispatch, and client SDK expectations.

#### How it works (internals)

Jackson deserializes unknown properties as ignored by default (`FAIL_ON_UNKNOWN_PROPERTIES` false for APIs). New fields get `@JsonProperty` and OpenAPI `required: false`. Enum additions should not break clients that switch on string values without a default branch.

#### When to use / when NOT to use

Always design public APIs for additive evolution. Use expand-contract for internal events too. Breaking changes require version bump and migration guide.

#### Production example

OrderDto adds `estimatedDeliveryDate` as optional; mobile apps from last year ignore it. Never rename `total` to `amount`—add `amount` alongside with deprecation note, then remove in v2. Runbooks should name the status codes, headers, and idempotency behavior operators will see during incidents.

#### Common mistakes

Tightening validation on existing fields (max length 500 → 100). Changing `id` from number to string. Reusing `status` enum value for a different meaning.

#### Interview follow-ups (with model answers)

**Q:** How do you test compatibility?
**A:** For «Backward compatible JSON changes.», versioning is not optional decoration — it is part of the HTTP contract clients rely on when gateways retry or mobile apps replay requests. I store idempotency keys with a unique constraint, return the same response body on replay, and document TTL in OpenAPI. Spring `@RestController` advice maps domain exceptions to RFC 7807 Problem Details with stable `type` URIs. In staging I replay recorded traffic and run openapi-diff on every PR so breaking changes fail CI before partners see them.

**Q:** Nullable new fields vs absent?
**A:** The follow-on risk for «Nullable new fields vs absent» is inconsistent behavior across versions — v1 clients still calling deprecated fields while v2 expects structured money objects. I version via URL prefix or vendor media type, add `Sunset` and `Deprecation` headers, and metric traffic by version label. Spring validation groups separate create vs update DTOs; `@ControllerAdvice` ensures 409 on conflict instead of silent overwrites. Operators need runbook steps: which status codes are retryable, which require a new Idempotency-Key, and how BFF translates upstream errors without double-wrapping JSON.

**Q:** Protobuf vs JSON evolution?
**A:** Trade-off framing for «Protobuf vs JSON evolution»: optimize for integrator stability over internal convenience. Public APIs get cursor pagination, explicit error envelopes, rate-limit headers, and contract tests; internal admin endpoints may use offset pages but still need authz and tracing. I walk one real endpoint through the checklist: safe GET, idempotent PUT/DELETE, POST with keys for money paths, ETag on updates, and OpenAPI examples for 400/404/409/412. If I cannot explain retry semantics to a mobile engineer in two minutes, the design is not ready for production.

#### Scenario probe

**Situation:** After a release, traffic on endpoints touching «Backward compatible JSON changes.» shows rising p99 latency and occasional duplicate side effects; mobile clients retry on gateway timeouts and support sees mismatched error JSON across services.

**Model answer:** I treat this as a contract and retry problem first, not a 'scale up pods' problem. I capture `X-Request-Id` across BFF and downstream services, compare Problem Details shapes, and replay a failing call with the same `Idempotency-Key` to see if POST is safe. Context: OrderDto adds `estimatedDeliveryDate` as optional; mobile apps from last year ignore it. Never rename `total` to `amount`—add `amount` alongside with deprecation note, then remove in v2. I verify GET safety, idempotent PUT/DELETE behavior, and whether Spring controllers return 409/412 instead of silent overwrites. OpenAPI diff against last release tells me if a field became required without a version bump. Short-term: tighten gateway timeouts with retry only on idempotent methods, fix error envelope in shared `@ControllerAdvice`. Long-term: contract tests, versioned DTOs, metrics on duplicate idempotency hits, and runbook steps for on-call.

---

### 13. ETag / If-Match optimistic concurrency.

**Short answer:** ETag is an opaque version token returned on GET; clients send `If-Match` on PUT/PATCH/DELETE. If the resource changed, return 412 Precondition Failed instead of last-write-wins. Essential for collaborative edits and inventory updates. Document the contract in OpenAPI with examples and enforce it in CI with contract tests.

#### What it is

Optimistic concurrency control uses HTTP conditional headers to detect stale writes without long DB locks. This sits at the boundary between HTTP transport, Spring MVC dispatch, and client SDK expectations.

#### How it works (internals)

ETag can be a hash of representation or a version column (`W/"3"` weak vs strong). Server compares If-Match to current ETag before update. Spring `ShallowEtagHeaderFilter` or manual `@RequestHeader If-Match` with version column in UPDATE WHERE.

#### When to use / when NOT to use

Use when concurrent updates cause real business harm—orders, stock, config. Skip for append-only logs or single-writer resources. Prefer explicit documentation and gateway policies over tribal knowledge about which endpoints are safe to retry.

#### Production example

Warehouse API: GET `/inventory/{sku}` returns `ETag: "v17"`. PATCH with stale `If-Match: "v16"` returns 412 Problem Detail; client refreshes and retries. Runbooks should name the status codes, headers, and idempotency behavior operators will see during incidents.

#### Common mistakes

ETag based on mutable computed fields. No If-Match on PATCH. Using last-modified alone without handling clock skew.

#### Interview follow-ups (with model answers)

**Q:** Weak vs strong ETag?
**A:** For «ETag / If-Match optimistic concurrency.», idempotency is not optional decoration — it is part of the HTTP contract clients rely on when gateways retry or mobile apps replay requests. I store idempotency keys with a unique constraint, return the same response body on replay, and document TTL in OpenAPI. Spring `@RestController` advice maps domain exceptions to RFC 7807 Problem Details with stable `type` URIs. In staging I replay recorded traffic and run openapi-diff on every PR so breaking changes fail CI before partners see them.

**Q:** ETag on collections?
**A:** The follow-on risk for «ETag on collections» is inconsistent behavior across versions — v1 clients still calling deprecated fields while v2 expects structured money objects. I version via URL prefix or vendor media type, add `Sunset` and `Deprecation` headers, and metric traffic by version label. Spring validation groups separate create vs update DTOs; `@ControllerAdvice` ensures 409 on conflict instead of silent overwrites. Operators need runbook steps: which status codes are retryable, which require a new Idempotency-Key, and how BFF translates upstream errors without double-wrapping JSON.

**Q:** How does this interact with caching?
**A:** Trade-off framing for «How does this interact with caching»: optimize for integrator stability over internal convenience. Public APIs get cursor pagination, explicit error envelopes, rate-limit headers, and contract tests; internal admin endpoints may use offset pages but still need authz and tracing. I walk one real endpoint through the checklist: safe GET, idempotent PUT/DELETE, POST with keys for money paths, ETag on updates, and OpenAPI examples for 400/404/409/412. If I cannot explain retry semantics to a mobile engineer in two minutes, the design is not ready for production.

#### Scenario probe

**Situation:** After a release, traffic on endpoints touching «ETag / If-Match optimistic concurrency.» shows rising p99 latency and occasional duplicate side effects; mobile clients retry on gateway timeouts and support sees mismatched error JSON across services.

**Model answer:** I treat this as a contract and retry problem first, not a 'scale up pods' problem. I capture `X-Request-Id` across BFF and downstream services, compare Problem Details shapes, and replay a failing call with the same `Idempotency-Key` to see if POST is safe. Context: Warehouse API: GET `/inventory/{sku}` returns `ETag: "v17"`. PATCH with stale `If-Match: "v16"` returns 412 Problem Detail; client refreshes and retries. I verify GET safety, idempotent PUT/DELETE behavior, and whether Spring controllers return 409/412 instead of silent overwrites. OpenAPI diff against last release tells me if a field became required without a version bump. Short-term: tighten gateway timeouts with retry only on idempotent methods, fix error envelope in shared `@ControllerAdvice`. Long-term: contract tests, versioned DTOs, metrics on duplicate idempotency hits, and runbook steps for on-call.

#### Code / config (when useful)
```java
@PutMapping("/inventory/{sku}")
ResponseEntity<InventoryDto> update(
    @PathVariable String sku,
    @RequestHeader("If-Match") String etag,
    @RequestBody InventoryDto body) {
  return inventoryService.updateIfMatch(sku, etag, body);
}
```

---

### 14. Caching: Cache-Control, Vary, Authorization.

**Short answer:** Set `Cache-Control: private, no-store` for personalized data; `public, max-age=...` only for truly public GETs. `Vary` tells caches which request headers affect the response. Never cache authenticated responses at shared CDNs without careful Vary and tenant isolation. Document the contract in OpenAPI with examples and enforce it in CI with contract tests.

#### What it is

HTTP caching lets browsers and CDNs reuse responses. Misconfigured caching leaks user data or serves stale authz decisions. This sits at the boundary between HTTP transport, Spring MVC dispatch, and client SDK expectations.

#### How it works (internals)

Cache-Control directives control store/revalidate. ETag enables 304 Not Modified. `Vary: Authorization, Accept-Language` prevents serving user A's response to user B. `Authorization` in requests usually implies `private` or `no-store`.

#### When to use / when NOT to use

CDN-cache static product catalogs and public docs. BFF responses with user-specific data: `private` or no cache. Use ETag for large GET that changes infrequently.

#### Production example

Product catalog `GET /products/{id}`: `Cache-Control: public, max-age=300` at edge. `GET /me/orders`: `Cache-Control: private, no-store` plus JWT in Authorization—never `s-maxage` at shared cache. Runbooks should name the status codes, headers, and idempotency behavior operators will see during incidents.

#### Common mistakes

Caching 200 responses with Set-Cookie. Forgetting Vary when content differs by Accept or tenant header. Using ETag without Cache-Control semantics.

#### Interview follow-ups (with model answers)

**Q:** CDN cache key design?
**A:** For «Caching: Cache-Control, Vary, Authorization.», OpenAPI is not optional decoration — it is part of the HTTP contract clients rely on when gateways retry or mobile apps replay requests. I store idempotency keys with a unique constraint, return the same response body on replay, and document TTL in OpenAPI. Spring `@RestController` advice maps domain exceptions to RFC 7807 Problem Details with stable `type` URIs. In staging I replay recorded traffic and run openapi-diff on every PR so breaking changes fail CI before partners see them.

**Q:** Stale-while-revalidate?
**A:** The follow-on risk for «Stale-while-revalidate» is inconsistent behavior across versions — v1 clients still calling deprecated fields while v2 expects structured money objects. I version via URL prefix or vendor media type, add `Sunset` and `Deprecation` headers, and metric traffic by version label. Spring validation groups separate create vs update DTOs; `@ControllerAdvice` ensures 409 on conflict instead of silent overwrites. Operators need runbook steps: which status codes are retryable, which require a new Idempotency-Key, and how BFF translates upstream errors without double-wrapping JSON.

**Q:** How Spring handles conditional GET?
**A:** Trade-off framing for «How Spring handles conditional GET»: optimize for integrator stability over internal convenience. Public APIs get cursor pagination, explicit error envelopes, rate-limit headers, and contract tests; internal admin endpoints may use offset pages but still need authz and tracing. I walk one real endpoint through the checklist: safe GET, idempotent PUT/DELETE, POST with keys for money paths, ETag on updates, and OpenAPI examples for 400/404/409/412. If I cannot explain retry semantics to a mobile engineer in two minutes, the design is not ready for production.

#### Scenario probe

**Situation:** After a release, traffic on endpoints touching «Caching: Cache-Control, Vary, Authorization.» shows rising p99 latency and occasional duplicate side effects; mobile clients retry on gateway timeouts and support sees mismatched error JSON across services.

**Model answer:** I treat this as a contract and retry problem first, not a 'scale up pods' problem. I capture `X-Request-Id` across BFF and downstream services, compare Problem Details shapes, and replay a failing call with the same `Idempotency-Key` to see if POST is safe. Context: Product catalog `GET /products/{id}`: `Cache-Control: public, max-age=300` at edge. `GET /me/orders`: `Cache-Control: private, no-store` plus JWT in Authorization—never `s-maxage` at shared cache. I verify GET safety, idempotent PUT/DELETE behavior, and whether Spring controllers return 409/412 instead of silent overwrites. OpenAPI diff against last release tells me if a field became required without a version bump. Short-term: tighten gateway timeouts with retry only on idempotent methods, fix error envelope in shared `@ControllerAdvice`. Long-term: contract tests, versioned DTOs, metrics on duplicate idempotency hits, and runbook steps for on-call.

---

### 15. HATEOAS — when it's worth it.

**Short answer:** HATEOAS embeds links (`self`, `next`, `cancel`) in responses so clients discover actions dynamically. Valuable for long-lived public APIs and generic clients; rarely worth the tax for internal SPAs that ship with OpenAPI and hardcoded routes. Document the contract in OpenAPI with examples and enforce it in CI with contract tests. Pair HTTP semantics with observability: correlation ids, structured Problem Details, and SLO dashboards on p99 latency.

#### What it is

Hypermedia as the Engine of Application State means the API tells the client what it can do next via links, not out-of-band documentation alone. This sits at the boundary between HTTP transport, Spring MVC dispatch, and client SDK expectations.

#### How it works (internals)

Spring HATEOAS wraps DTOs in `EntityModel` with `Link.of(...)`. Clients follow `rel` links instead of constructing URLs. Requires stable link relation names and versioning discipline.

#### When to use / when NOT to use

Public platforms with third-party integrators who cannot redeploy when URLs change. Skip for React+BFF where the frontend and backend deploy together—OpenAPI + typed client is simpler. Prefer explicit documentation and gateway policies over tribal knowledge about which endpoints are safe to retry.

#### Production example

Partner integration API returns order with `_links.cancel` only when status allows cancellation—UI enables button based on link presence. Internal admin SPA uses OpenAPI-generated TypeScript client instead. Runbooks should name the status codes, headers, and idempotency behavior operators will see during incidents.

#### Common mistakes

Half-HATEOAS (some links, some hardcoded). Links without documented rel names. Performance cost of assembling links on hot list endpoints.

#### Interview follow-ups (with model answers)

**Q:** JSON-LD vs simple _links?
**A:** For «HATEOAS — when it's worth it.», Spring controllers is not optional decoration — it is part of the HTTP contract clients rely on when gateways retry or mobile apps replay requests. I store idempotency keys with a unique constraint, return the same response body on replay, and document TTL in OpenAPI. Spring `@RestController` advice maps domain exceptions to RFC 7807 Problem Details with stable `type` URIs. In staging I replay recorded traffic and run openapi-diff on every PR so breaking changes fail CI before partners see them.

**Q:** HATEOAS and OpenAPI together?
**A:** The follow-on risk for «HATEOAS and OpenAPI together» is inconsistent behavior across versions — v1 clients still calling deprecated fields while v2 expects structured money objects. I version via URL prefix or vendor media type, add `Sunset` and `Deprecation` headers, and metric traffic by version label. Spring validation groups separate create vs update DTOs; `@ControllerAdvice` ensures 409 on conflict instead of silent overwrites. Operators need runbook steps: which status codes are retryable, which require a new Idempotency-Key, and how BFF translates upstream errors without double-wrapping JSON.

**Q:** Link relations registry?
**A:** Trade-off framing for «Link relations registry»: optimize for integrator stability over internal convenience. Public APIs get cursor pagination, explicit error envelopes, rate-limit headers, and contract tests; internal admin endpoints may use offset pages but still need authz and tracing. I walk one real endpoint through the checklist: safe GET, idempotent PUT/DELETE, POST with keys for money paths, ETag on updates, and OpenAPI examples for 400/404/409/412. If I cannot explain retry semantics to a mobile engineer in two minutes, the design is not ready for production.

#### Scenario probe

**Situation:** After a release, traffic on endpoints touching «HATEOAS — when it's worth it.» shows rising p99 latency and occasional duplicate side effects; mobile clients retry on gateway timeouts and support sees mismatched error JSON across services.

**Model answer:** I treat this as a contract and retry problem first, not a 'scale up pods' problem. I capture `X-Request-Id` across BFF and downstream services, compare Problem Details shapes, and replay a failing call with the same `Idempotency-Key` to see if POST is safe. Context: Partner integration API returns order with `_links.cancel` only when status allows cancellation—UI enables button based on link presence. Internal admin SPA uses OpenAPI-generated TypeScript client in. I verify GET safety, idempotent PUT/DELETE behavior, and whether Spring controllers return 409/412 instead of silent overwrites. OpenAPI diff against last release tells me if a field became required without a version bump. Short-term: tighten gateway timeouts with retry only on idempotent methods, fix error envelope in shared `@ControllerAdvice`. Long-term: contract tests, versioned DTOs, metrics on duplicate idempotency hits, and runbook steps for on-call.

---

### 16. OpenAPI as a contract.

**Short answer:** OpenAPI is the machine-readable contract for paths, schemas, errors, and auth. Pick spec-first or code-first (`springdoc-openapi`)—not both diverging. Use it for codegen, contract tests, and breaking-change CI gates. Document the contract in OpenAPI with examples and enforce it in CI with contract tests.

#### What it is

OpenAPI (Swagger) documents REST APIs and enables client/server generation and validation. This sits at the boundary between HTTP transport, Spring MVC dispatch, and client SDK expectations.

#### How it works (internals)

springdoc scans `@RestController` annotations and emits OpenAPI 3. Spec-first teams maintain `openapi.yaml` and generate Spring interfaces. Diff tools (oasdiff, openapi-diff) fail CI on breaking changes.

#### When to use / when NOT to use

Mandatory for public and partner APIs. Internal services benefit from shared schemas. BFF can consume backend OpenAPI for type-safe clients.

#### Production example

Repo holds `api/openapi.yaml`; PR checks run openapi-diff against main. React app generates types with `openapi-typescript`. Spring implements generated interfaces—single source of truth.

#### Common mistakes

Annotations drift from reality. No examples in spec. Publishing OpenAPI without documenting error responses and pagination.

#### Interview follow-ups (with model answers)

**Q:** How do you version OpenAPI?
**A:** For «OpenAPI as a contract.», versioning is not optional decoration — it is part of the HTTP contract clients rely on when gateways retry or mobile apps replay requests. I store idempotency keys with a unique constraint, return the same response body on replay, and document TTL in OpenAPI. Spring `@RestController` advice maps domain exceptions to RFC 7807 Problem Details with stable `type` URIs. In staging I replay recorded traffic and run openapi-diff on every PR so breaking changes fail CI before partners see them.

**Q:** springdoc vs springfox?
**A:** The follow-on risk for «springdoc vs springfox» is inconsistent behavior across versions — v1 clients still calling deprecated fields while v2 expects structured money objects. I version via URL prefix or vendor media type, add `Sunset` and `Deprecation` headers, and metric traffic by version label. Spring validation groups separate create vs update DTOs; `@ControllerAdvice` ensures 409 on conflict instead of silent overwrites. Operators need runbook steps: which status codes are retryable, which require a new Idempotency-Key, and how BFF translates upstream errors without double-wrapping JSON.

**Q:** Contract tests with Pact vs OpenAPI?
**A:** Trade-off framing for «Contract tests with Pact vs OpenAPI»: optimize for integrator stability over internal convenience. Public APIs get cursor pagination, explicit error envelopes, rate-limit headers, and contract tests; internal admin endpoints may use offset pages but still need authz and tracing. I walk one real endpoint through the checklist: safe GET, idempotent PUT/DELETE, POST with keys for money paths, ETag on updates, and OpenAPI examples for 400/404/409/412. If I cannot explain retry semantics to a mobile engineer in two minutes, the design is not ready for production.

#### Scenario probe

**Situation:** After a release, traffic on endpoints touching «OpenAPI as a contract.» shows rising p99 latency and occasional duplicate side effects; mobile clients retry on gateway timeouts and support sees mismatched error JSON across services.

**Model answer:** I treat this as a contract and retry problem first, not a 'scale up pods' problem. I capture `X-Request-Id` across BFF and downstream services, compare Problem Details shapes, and replay a failing call with the same `Idempotency-Key` to see if POST is safe. Context: Repo holds `api/openapi.yaml`; PR checks run openapi-diff against main. React app generates types with `openapi-typescript`. Spring implements generated interfaces—single source of truth. I verify GET safety, idempotent PUT/DELETE behavior, and whether Spring controllers return 409/412 instead of silent overwrites. OpenAPI diff against last release tells me if a field became required without a version bump. Short-term: tighten gateway timeouts with retry only on idempotent methods, fix error envelope in shared `@ControllerAdvice`. Long-term: contract tests, versioned DTOs, metrics on duplicate idempotency hits, and runbook steps for on-call.

---

### 17. File uploads.

**Short answer:** Small files: `multipart/form-data` to the API with size limits and virus scan. Large files: return presigned URL (S3/Azure Blob SAS) for direct client-to-storage upload, then `POST /uploads/{id}/complete` to register metadata. Never base64 huge files in JSON. Document the contract in OpenAPI with examples and enforce it in CI with contract tests.

#### What it is

File upload design balances simplicity, memory use, security, and throughput. This sits at the boundary between HTTP transport, Spring MVC dispatch, and client SDK expectations.

#### How it works (internals)

Spring `MultipartFile` streams to temp or storage; configure `spring.servlet.multipart.max-file-size`. Presigned URLs offload bytes from app servers; API only issues tokens and validates completion callbacks. Spring maps requests through `DispatcherServlet`, `HandlerMapping`, and `HttpMessageConverter` chains before your service layer runs.

#### When to use / when NOT to use

Multipart for avatars and documents under a few MB. Presigned for video, bulk imports, backups. Always validate content-type, size, and scan before marking available.

#### Production example

Invoice upload: client calls `POST /uploads` → receives `{uploadUrl, uploadId}` → PUTs PDF to S3 → calls `POST /uploads/{id}/complete` → async virus scan → webhook on success. Runbooks should name the status codes, headers, and idempotency behavior operators will see during incidents.

#### Common mistakes

Loading 50MB into heap via `@RequestBody`. No extension/MIME validation. Public bucket ACLs on user uploads.

#### Interview follow-ups (with model answers)

**Q:** Chunked/resumable uploads?
**A:** For «File uploads.», idempotency is not optional decoration — it is part of the HTTP contract clients rely on when gateways retry or mobile apps replay requests. I store idempotency keys with a unique constraint, return the same response body on replay, and document TTL in OpenAPI. Spring `@RestController` advice maps domain exceptions to RFC 7807 Problem Details with stable `type` URIs. In staging I replay recorded traffic and run openapi-diff on every PR so breaking changes fail CI before partners see them.

**Q:** virus scan sync vs async?
**A:** The follow-on risk for «virus scan sync vs async» is inconsistent behavior across versions — v1 clients still calling deprecated fields while v2 expects structured money objects. I version via URL prefix or vendor media type, add `Sunset` and `Deprecation` headers, and metric traffic by version label. Spring validation groups separate create vs update DTOs; `@ControllerAdvice` ensures 409 on conflict instead of silent overwrites. Operators need runbook steps: which status codes are retryable, which require a new Idempotency-Key, and how BFF translates upstream errors without double-wrapping JSON.

**Q:** Content-Disposition handling?
**A:** Trade-off framing for «Content-Disposition handling»: optimize for integrator stability over internal convenience. Public APIs get cursor pagination, explicit error envelopes, rate-limit headers, and contract tests; internal admin endpoints may use offset pages but still need authz and tracing. I walk one real endpoint through the checklist: safe GET, idempotent PUT/DELETE, POST with keys for money paths, ETag on updates, and OpenAPI examples for 400/404/409/412. If I cannot explain retry semantics to a mobile engineer in two minutes, the design is not ready for production.

#### Scenario probe

**Situation:** After a release, traffic on endpoints touching «File uploads.» shows rising p99 latency and occasional duplicate side effects; mobile clients retry on gateway timeouts and support sees mismatched error JSON across services.

**Model answer:** I treat this as a contract and retry problem first, not a 'scale up pods' problem. I capture `X-Request-Id` across BFF and downstream services, compare Problem Details shapes, and replay a failing call with the same `Idempotency-Key` to see if POST is safe. Context: Invoice upload: client calls `POST /uploads` → receives `{uploadUrl, uploadId}` → PUTs PDF to S3 → calls `POST /uploads/{id}/complete` → async virus scan → webhook on success. I verify GET safety, idempotent PUT/DELETE behavior, and whether Spring controllers return 409/412 instead of silent overwrites. OpenAPI diff against last release tells me if a field became required without a version bump. Short-term: tighten gateway timeouts with retry only on idempotent methods, fix error envelope in shared `@ControllerAdvice`. Long-term: contract tests, versioned DTOs, metrics on duplicate idempotency hits, and runbook steps for on-call.

#### Code / config (when useful)
```java
@PostMapping(value="/documents", consumes=MediaType.MULTIPART_FORM_DATA_VALUE)
public DocumentDto upload(@RequestPart("file") MultipartFile file) {
  return documentService.store(file);
}
```

---

### 18. Long-running operations.

**Short answer:** Return `202 Accepted` with `Location: /operations/{id}` (or task resource) instead of blocking HTTP for minutes. Clients poll the operation status or receive a webhook on completion. Gateway timeouts will kill long-held connections. Document the contract in OpenAPI with examples and enforce it in CI with contract tests.

#### What it is

Long-running operations model async work—exports, provisioning, batch imports—as first-class resources with lifecycle. This sits at the boundary between HTTP transport, Spring MVC dispatch, and client SDK expectations.

#### How it works (internals)

POST starts work, persists operation record (PENDING → RUNNING → SUCCEEDED/FAILED), returns 202. GET `/operations/{id}` returns status and result link. Use message queue or `@Async` worker; virtual threads do not remove timeout limits at the load balancer.

#### When to use / when NOT to use

Any job over ~30 seconds or unpredictable duration. Sync 200 only when work is reliably sub-second. Prefer explicit documentation and gateway policies over tribal knowledge about which endpoints are safe to retry.

#### Production example

Report generation: `POST /reports` → 202 + `operationId`. Worker builds CSV in S3; GET returns `{status: SUCCEEDED, downloadUrl}`. ALB idle timeout stays 60s; no problem.

#### Common mistakes

Blocking servlet thread for 10 minutes. 200 OK before work finishes. No operation id for status tracking. Teams often discover these failures only after mobile clients retry on flaky networks or CDNs cache a non-safe GET.

#### Interview follow-ups (with model answers)

**Q:** Poll vs webhook vs SSE?
**A:** For «Long-running operations.», OpenAPI is not optional decoration — it is part of the HTTP contract clients rely on when gateways retry or mobile apps replay requests. I store idempotency keys with a unique constraint, return the same response body on replay, and document TTL in OpenAPI. Spring `@RestController` advice maps domain exceptions to RFC 7807 Problem Details with stable `type` URIs. In staging I replay recorded traffic and run openapi-diff on every PR so breaking changes fail CI before partners see them.

**Q:** Cancellation of long jobs?
**A:** The follow-on risk for «Cancellation of long jobs» is inconsistent behavior across versions — v1 clients still calling deprecated fields while v2 expects structured money objects. I version via URL prefix or vendor media type, add `Sunset` and `Deprecation` headers, and metric traffic by version label. Spring validation groups separate create vs update DTOs; `@ControllerAdvice` ensures 409 on conflict instead of silent overwrites. Operators need runbook steps: which status codes are retryable, which require a new Idempotency-Key, and how BFF translates upstream errors without double-wrapping JSON.

**Q:** 202 vs 201 for async create?
**A:** Trade-off framing for «202 vs 201 for async create»: optimize for integrator stability over internal convenience. Public APIs get cursor pagination, explicit error envelopes, rate-limit headers, and contract tests; internal admin endpoints may use offset pages but still need authz and tracing. I walk one real endpoint through the checklist: safe GET, idempotent PUT/DELETE, POST with keys for money paths, ETag on updates, and OpenAPI examples for 400/404/409/412. If I cannot explain retry semantics to a mobile engineer in two minutes, the design is not ready for production.

#### Scenario probe

**Situation:** After a release, traffic on endpoints touching «Long-running operations.» shows rising p99 latency and occasional duplicate side effects; mobile clients retry on gateway timeouts and support sees mismatched error JSON across services.

**Model answer:** I treat this as a contract and retry problem first, not a 'scale up pods' problem. I capture `X-Request-Id` across BFF and downstream services, compare Problem Details shapes, and replay a failing call with the same `Idempotency-Key` to see if POST is safe. Context: Report generation: `POST /reports` → 202 + `operationId`. Worker builds CSV in S3; GET returns `{status: SUCCEEDED, downloadUrl}`. ALB idle timeout stays 60s; no problem. I verify GET safety, idempotent PUT/DELETE behavior, and whether Spring controllers return 409/412 instead of silent overwrites. OpenAPI diff against last release tells me if a field became required without a version bump. Short-term: tighten gateway timeouts with retry only on idempotent methods, fix error envelope in shared `@ControllerAdvice`. Long-term: contract tests, versioned DTOs, metrics on duplicate idempotency hits, and runbook steps for on-call.

---

### 19. Webhooks.

**Short answer:** Webhooks are server-to-server HTTP callbacks on events. Sign payloads (HMAC-SHA256), include timestamp for replay protection, retry with exponential backoff, and design receivers to be idempotent. Rotate secrets without dropping events. Document the contract in OpenAPI with examples and enforce it in CI with contract tests.

#### What it is

Webhooks push notifications to integrators instead of forcing constant polling. This sits at the boundary between HTTP transport, Spring MVC dispatch, and client SDK expectations.

#### How it works (internals)

Sender POSTs JSON with headers `X-Signature`, `X-Timestamp`. Receiver verifies signature within skew window, dedupes by event id, returns 2xx quickly and processes async. Failed deliveries retry; dead-letter after N attempts.

#### When to use / when NOT to use

Payment status, order shipped, async job complete. Prefer webhooks over polling for partner SLAs. Prefer explicit documentation and gateway policies over tribal knowledge about which endpoints are safe to retry.

#### Production example

Stripe-style: each tenant has webhook secret; events stored with `eventId`; receiver uses `@Transactional` idempotent insert on `processed_events` table. Runbooks should name the status codes, headers, and idempotency behavior operators will see during incidents.

#### Common mistakes

No signature verification. Retrying non-idempotent side effects. Blocking handler causing sender timeouts and infinite retries.

#### Interview follow-ups (with model answers)

**Q:** Webhook vs message queue for partners?
**A:** For «Webhooks.», Spring controllers is not optional decoration — it is part of the HTTP contract clients rely on when gateways retry or mobile apps replay requests. I store idempotency keys with a unique constraint, return the same response body on replay, and document TTL in OpenAPI. Spring `@RestController` advice maps domain exceptions to RFC 7807 Problem Details with stable `type` URIs. In staging I replay recorded traffic and run openapi-diff on every PR so breaking changes fail CI before partners see them.

**Q:** Ordering guarantees?
**A:** The follow-on risk for «Ordering guarantees» is inconsistent behavior across versions — v1 clients still calling deprecated fields while v2 expects structured money objects. I version via URL prefix or vendor media type, add `Sunset` and `Deprecation` headers, and metric traffic by version label. Spring validation groups separate create vs update DTOs; `@ControllerAdvice` ensures 409 on conflict instead of silent overwrites. Operators need runbook steps: which status codes are retryable, which require a new Idempotency-Key, and how BFF translates upstream errors without double-wrapping JSON.

**Q:** How to test webhooks locally?
**A:** Trade-off framing for «How to test webhooks locally»: optimize for integrator stability over internal convenience. Public APIs get cursor pagination, explicit error envelopes, rate-limit headers, and contract tests; internal admin endpoints may use offset pages but still need authz and tracing. I walk one real endpoint through the checklist: safe GET, idempotent PUT/DELETE, POST with keys for money paths, ETag on updates, and OpenAPI examples for 400/404/409/412. If I cannot explain retry semantics to a mobile engineer in two minutes, the design is not ready for production.

#### Scenario probe

**Situation:** After a release, traffic on endpoints touching «Webhooks.» shows rising p99 latency and occasional duplicate side effects; mobile clients retry on gateway timeouts and support sees mismatched error JSON across services.

**Model answer:** I treat this as a contract and retry problem first, not a 'scale up pods' problem. I capture `X-Request-Id` across BFF and downstream services, compare Problem Details shapes, and replay a failing call with the same `Idempotency-Key` to see if POST is safe. Context: Stripe-style: each tenant has webhook secret; events stored with `eventId`; receiver uses `@Transactional` idempotent insert on `processed_events` table. I verify GET safety, idempotent PUT/DELETE behavior, and whether Spring controllers return 409/412 instead of silent overwrites. OpenAPI diff against last release tells me if a field became required without a version bump. Short-term: tighten gateway timeouts with retry only on idempotent methods, fix error envelope in shared `@ControllerAdvice`. Long-term: contract tests, versioned DTOs, metrics on duplicate idempotency hits, and runbook steps for on-call.

---

### 20. CORS.

**Short answer:** CORS is browser-enforced cross-origin policy—not API authentication. Allowlist specific origins; `Access-Control-Allow-Credentials: true` forbids `*`. Preflight OPTIONS must return allowed methods and headers. Server-to-server calls ignore CORS.

#### What it is

Cross-Origin Resource Sharing lets browsers call APIs on a different domain when the server explicitly permits it. This sits at the boundary between HTTP transport, Spring MVC dispatch, and client SDK expectations.

#### How it works (internals)

Browser sends OPTIONS preflight for non-simple requests (custom headers, JSON with credentials). Server responds with `Access-Control-Allow-Origin`, `Allow-Methods`, `Allow-Headers`. Spring `@CrossOrigin` or `CorsConfigurationSource` in Security filter chain.

#### When to use / when NOT to use

Configure when SPA (React on `app.example.com`) calls API (`api.example.com`). Mobile and backend clients do not need CORS. Prefer explicit documentation and gateway policies over tribal knowledge about which endpoints are safe to retry.

#### Production example

Spring Security `corsConfigurationSource` allowlists `https://app.example.com` in prod, `http://localhost:3000` in dev. JWT in Authorization listed in allowed headers. Runbooks should name the status codes, headers, and idempotency behavior operators will see during incidents.

#### Common mistakes

`*` with credentials. CORS as substitute for auth. Forgetting preflight on new custom headers.

#### Interview follow-ups (with model answers)

**Q:** CORS vs CSRF?
**A:** For «CORS.», versioning is not optional decoration — it is part of the HTTP contract clients rely on when gateways retry or mobile apps replay requests. I store idempotency keys with a unique constraint, return the same response body on replay, and document TTL in OpenAPI. Spring `@RestController` advice maps domain exceptions to RFC 7807 Problem Details with stable `type` URIs. In staging I replay recorded traffic and run openapi-diff on every PR so breaking changes fail CI before partners see them.

**Q:** SameSite cookies with CORS?
**A:** The follow-on risk for «SameSite cookies with CORS» is inconsistent behavior across versions — v1 clients still calling deprecated fields while v2 expects structured money objects. I version via URL prefix or vendor media type, add `Sunset` and `Deprecation` headers, and metric traffic by version label. Spring validation groups separate create vs update DTOs; `@ControllerAdvice` ensures 409 on conflict instead of silent overwrites. Operators need runbook steps: which status codes are retryable, which require a new Idempotency-Key, and how BFF translates upstream errors without double-wrapping JSON.

**Q:** Gateway CORS vs service CORS?
**A:** Trade-off framing for «Gateway CORS vs service CORS»: optimize for integrator stability over internal convenience. Public APIs get cursor pagination, explicit error envelopes, rate-limit headers, and contract tests; internal admin endpoints may use offset pages but still need authz and tracing. I walk one real endpoint through the checklist: safe GET, idempotent PUT/DELETE, POST with keys for money paths, ETag on updates, and OpenAPI examples for 400/404/409/412. If I cannot explain retry semantics to a mobile engineer in two minutes, the design is not ready for production.

#### Scenario probe

**Situation:** After a release, traffic on endpoints touching «CORS.» shows rising p99 latency and occasional duplicate side effects; mobile clients retry on gateway timeouts and support sees mismatched error JSON across services.

**Model answer:** I treat this as a contract and retry problem first, not a 'scale up pods' problem. I capture `X-Request-Id` across BFF and downstream services, compare Problem Details shapes, and replay a failing call with the same `Idempotency-Key` to see if POST is safe. Context: Spring Security `corsConfigurationSource` allowlists `https://app.example.com` in prod, `http://localhost:3000` in dev. JWT in Authorization listed in allowed headers. I verify GET safety, idempotent PUT/DELETE behavior, and whether Spring controllers return 409/412 instead of silent overwrites. OpenAPI diff against last release tells me if a field became required without a version bump. Short-term: tighten gateway timeouts with retry only on idempotent methods, fix error envelope in shared `@ControllerAdvice`. Long-term: contract tests, versioned DTOs, metrics on duplicate idempotency hits, and runbook steps for on-call.

---

### 21. Rate limiting headers.

**Short answer:** Return standardized rate limit headers (`RateLimit-Limit`, `RateLimit-Remaining`, `RateLimit-Reset` per IETF draft) or common `X-RateLimit-*` variants. Respond with 429 Too Many Requests and optional `Retry-After`. Limit per API key, user, tenant, and IP. Document the contract in OpenAPI with examples and enforce it in CI with contract tests.

#### What it is

Rate limiting protects availability and fair usage; headers let clients backoff gracefully. This sits at the boundary between HTTP transport, Spring MVC dispatch, and client SDK expectations.

#### How it works (internals)

Gateway or Redis token bucket tracks quotas. On each response, decrement remaining. 429 when exhausted. Expensive endpoints get lower limits than cheap GETs.

#### When to use / when NOT to use

All public APIs and sensitive internal endpoints (login, search). Different tiers for partner SLAs. Prefer explicit documentation and gateway policies over tribal knowledge about which endpoints are safe to retry.

#### Production example

Kong/Spring Cloud Gateway applies 1000 req/min per API key; response includes `RateLimit-Remaining: 847`. Burst allowance for checkout spikes. Runbooks should name the status codes, headers, and idempotency behavior operators will see during incidents.

#### Common mistakes

429 without Retry-After. Same limit for list and heavy export. No distinction between authenticated users sharing one IP.

#### Interview follow-ups (with model answers)

**Q:** Token bucket vs sliding window?
**A:** For «Rate limiting headers.», idempotency is not optional decoration — it is part of the HTTP contract clients rely on when gateways retry or mobile apps replay requests. I store idempotency keys with a unique constraint, return the same response body on replay, and document TTL in OpenAPI. Spring `@RestController` advice maps domain exceptions to RFC 7807 Problem Details with stable `type` URIs. In staging I replay recorded traffic and run openapi-diff on every PR so breaking changes fail CI before partners see them.

**Q:** Rate limit at edge vs app?
**A:** The follow-on risk for «Rate limit at edge vs app» is inconsistent behavior across versions — v1 clients still calling deprecated fields while v2 expects structured money objects. I version via URL prefix or vendor media type, add `Sunset` and `Deprecation` headers, and metric traffic by version label. Spring validation groups separate create vs update DTOs; `@ControllerAdvice` ensures 409 on conflict instead of silent overwrites. Operators need runbook steps: which status codes are retryable, which require a new Idempotency-Key, and how BFF translates upstream errors without double-wrapping JSON.

**Q:** How to handle distributed limits?
**A:** Trade-off framing for «How to handle distributed limits»: optimize for integrator stability over internal convenience. Public APIs get cursor pagination, explicit error envelopes, rate-limit headers, and contract tests; internal admin endpoints may use offset pages but still need authz and tracing. I walk one real endpoint through the checklist: safe GET, idempotent PUT/DELETE, POST with keys for money paths, ETag on updates, and OpenAPI examples for 400/404/409/412. If I cannot explain retry semantics to a mobile engineer in two minutes, the design is not ready for production.

#### Scenario probe

**Situation:** After a release, traffic on endpoints touching «Rate limiting headers.» shows rising p99 latency and occasional duplicate side effects; mobile clients retry on gateway timeouts and support sees mismatched error JSON across services.

**Model answer:** I treat this as a contract and retry problem first, not a 'scale up pods' problem. I capture `X-Request-Id` across BFF and downstream services, compare Problem Details shapes, and replay a failing call with the same `Idempotency-Key` to see if POST is safe. Context: Kong/Spring Cloud Gateway applies 1000 req/min per API key; response includes `RateLimit-Remaining: 847`. Burst allowance for checkout spikes. I verify GET safety, idempotent PUT/DELETE behavior, and whether Spring controllers return 409/412 instead of silent overwrites. OpenAPI diff against last release tells me if a field became required without a version bump. Short-term: tighten gateway timeouts with retry only on idempotent methods, fix error envelope in shared `@ControllerAdvice`. Long-term: contract tests, versioned DTOs, metrics on duplicate idempotency hits, and runbook steps for on-call.

---

### 22. Bulk APIs.

**Short answer:** Batch endpoints like `POST /orders:batch` or `POST /orders/bulk` accept arrays with a enforced max size. Document whether one transaction or per-item commits. Partial success: HTTP 207 Multi-Status or 200 with `{succeeded[], failed[]}`—pick one and stick to it. Document the contract in OpenAPI with examples and enforce it in CI with contract tests.

#### What it is

Bulk APIs reduce chatty clients but increase blast radius and complexity. This sits at the boundary between HTTP transport, Spring MVC dispatch, and client SDK expectations.

#### How it works (internals)

Validate entire payload, process items with idempotency keys per row where needed. Spring validates `List<CreateOrderRequest>` with `@Size(max=100)`. Return per-item error codes without failing silent items.

#### When to use / when NOT to use

Integrations importing catalog rows or syncing CRM updates. Avoid bulk for user-facing single actions. Prefer explicit documentation and gateway policies over tribal knowledge about which endpoints are safe to retry.

#### Production example

ERP posts 50 orders; 48 succeed, 2 fail validation—response 200 with `failures[{index, code, detail}]`. DB uses per-item transactions so one bad row does not roll back 49 good orders. Runbooks should name the status codes, headers, and idempotency behavior operators will see during incidents.

#### Common mistakes

Unbounded batch size. All-or-nothing without documenting it. No idempotency on bulk POST retries.

#### Interview follow-ups (with model answers)

**Q:** Sync bulk vs async 202?
**A:** For «Bulk APIs.», OpenAPI is not optional decoration — it is part of the HTTP contract clients rely on when gateways retry or mobile apps replay requests. I store idempotency keys with a unique constraint, return the same response body on replay, and document TTL in OpenAPI. Spring `@RestController` advice maps domain exceptions to RFC 7807 Problem Details with stable `type` URIs. In staging I replay recorded traffic and run openapi-diff on every PR so breaking changes fail CI before partners see them.

**Q:** GraphQL mutations vs REST bulk?
**A:** The follow-on risk for «GraphQL mutations vs REST bulk» is inconsistent behavior across versions — v1 clients still calling deprecated fields while v2 expects structured money objects. I version via URL prefix or vendor media type, add `Sunset` and `Deprecation` headers, and metric traffic by version label. Spring validation groups separate create vs update DTOs; `@ControllerAdvice` ensures 409 on conflict instead of silent overwrites. Operators need runbook steps: which status codes are retryable, which require a new Idempotency-Key, and how BFF translates upstream errors without double-wrapping JSON.

**Q:** Ordering guarantees in batch?
**A:** Trade-off framing for «Ordering guarantees in batch»: optimize for integrator stability over internal convenience. Public APIs get cursor pagination, explicit error envelopes, rate-limit headers, and contract tests; internal admin endpoints may use offset pages but still need authz and tracing. I walk one real endpoint through the checklist: safe GET, idempotent PUT/DELETE, POST with keys for money paths, ETag on updates, and OpenAPI examples for 400/404/409/412. If I cannot explain retry semantics to a mobile engineer in two minutes, the design is not ready for production.

#### Scenario probe

**Situation:** After a release, traffic on endpoints touching «Bulk APIs.» shows rising p99 latency and occasional duplicate side effects; mobile clients retry on gateway timeouts and support sees mismatched error JSON across services.

**Model answer:** I treat this as a contract and retry problem first, not a 'scale up pods' problem. I capture `X-Request-Id` across BFF and downstream services, compare Problem Details shapes, and replay a failing call with the same `Idempotency-Key` to see if POST is safe. Context: ERP posts 50 orders; 48 succeed, 2 fail validation—response 200 with `failures[{index, code, detail}]`. DB uses per-item transactions so one bad row does not roll back 49 good orders. I verify GET safety, idempotent PUT/DELETE behavior, and whether Spring controllers return 409/412 instead of silent overwrites. OpenAPI diff against last release tells me if a field became required without a version bump. Short-term: tighten gateway timeouts with retry only on idempotent methods, fix error envelope in shared `@ControllerAdvice`. Long-term: contract tests, versioned DTOs, metrics on duplicate idempotency hits, and runbook steps for on-call.

---

### 23. Search vs GET collection.

**Short answer:** Simple filters belong on `GET /orders?status=OPEN`. Complex search with nested criteria, full-text, or large filter objects use `POST /orders/search` with JSON body—trades cacheability for expressiveness. Back search with Elasticsearch/OpenSearch behind your service boundary. Document the contract in OpenAPI with examples and enforce it in CI with contract tests.

#### What it is

Collection GET is for bounded, cache-friendly queries; search POST is for rich queries that do not fit query strings. This sits at the boundary between HTTP transport, Spring MVC dispatch, and client SDK expectations.

#### How it works (internals)

GET query strings hit URL length limits (~2K) and are awkward for nested AND/OR. POST search returns same DTO shape as list but is not cache-safe by default. Translate DSL to indexed queries—never raw SQL from client.

#### When to use / when NOT to use

GET for CRUD list screens with a few filters. POST search for admin consoles, analytics filters, geo+text combos. Prefer explicit documentation and gateway policies over tribal knowledge about which endpoints are safe to retry.

#### Production example

`POST /orders/search` body `{status: ["OPEN","PAID"], createdAfter: "...", q: "widget"}` → service queries OpenSearch, returns paginated OrderSummaryDto. Runbooks should name the status codes, headers, and idempotency behavior operators will see during incidents.

#### Common mistakes

PUTting search criteria in GET with 5KB query string. Exposing Elasticsearch DSL directly. No pagination on search results.

#### Interview follow-ups (with model answers)

**Q:** Cache POST search?
**A:** For «Search vs GET collection.», Spring controllers is not optional decoration — it is part of the HTTP contract clients rely on when gateways retry or mobile apps replay requests. I store idempotency keys with a unique constraint, return the same response body on replay, and document TTL in OpenAPI. Spring `@RestController` advice maps domain exceptions to RFC 7807 Problem Details with stable `type` URIs. In staging I replay recorded traffic and run openapi-diff on every PR so breaking changes fail CI before partners see them.

**Q:** GET + RSQL/ FIQL?
**A:** The follow-on risk for «GET + RSQL/ FIQL» is inconsistent behavior across versions — v1 clients still calling deprecated fields while v2 expects structured money objects. I version via URL prefix or vendor media type, add `Sunset` and `Deprecation` headers, and metric traffic by version label. Spring validation groups separate create vs update DTOs; `@ControllerAdvice` ensures 409 on conflict instead of silent overwrites. Operators need runbook steps: which status codes are retryable, which require a new Idempotency-Key, and how BFF translates upstream errors without double-wrapping JSON.

**Q:** Search relevance vs sort?
**A:** Trade-off framing for «Search relevance vs sort»: optimize for integrator stability over internal convenience. Public APIs get cursor pagination, explicit error envelopes, rate-limit headers, and contract tests; internal admin endpoints may use offset pages but still need authz and tracing. I walk one real endpoint through the checklist: safe GET, idempotent PUT/DELETE, POST with keys for money paths, ETag on updates, and OpenAPI examples for 400/404/409/412. If I cannot explain retry semantics to a mobile engineer in two minutes, the design is not ready for production.

#### Scenario probe

**Situation:** After a release, traffic on endpoints touching «Search vs GET collection.» shows rising p99 latency and occasional duplicate side effects; mobile clients retry on gateway timeouts and support sees mismatched error JSON across services.

**Model answer:** I treat this as a contract and retry problem first, not a 'scale up pods' problem. I capture `X-Request-Id` across BFF and downstream services, compare Problem Details shapes, and replay a failing call with the same `Idempotency-Key` to see if POST is safe. Context: `POST /orders/search` body `{status: ["OPEN","PAID"], createdAfter: "...", q: "widget"}` → service queries OpenSearch, returns paginated OrderSummaryDto. I verify GET safety, idempotent PUT/DELETE behavior, and whether Spring controllers return 409/412 instead of silent overwrites. OpenAPI diff against last release tells me if a field became required without a version bump. Short-term: tighten gateway timeouts with retry only on idempotent methods, fix error envelope in shared `@ControllerAdvice`. Long-term: contract tests, versioned DTOs, metrics on duplicate idempotency hits, and runbook steps for on-call.

---

### 24. GraphQL vs REST for a Java+React app.

**Short answer:** GraphQL gives clients one round-trip and shaped responses; cost is N+1 resolvers, harder HTTP caching, and per-field authorization. REST with a BFF is often enough for React apps. Choose GraphQL when many clients need different shapes and you invest in DataLoader and schema governance. Document the contract in OpenAPI with examples and enforce it in CI with contract tests.

#### What it is

GraphQL is a query language and runtime; REST is resource-oriented HTTP with multiple endpoints. This sits at the boundary between HTTP transport, Spring MVC dispatch, and client SDK expectations.

#### How it works (internals)

GraphQL single endpoint POST; resolvers map to services. DataLoader batches DB calls. REST uses multiple GETs or sparse fieldsets; React Query caches by URL. Spring: REST is native; GraphQL via Spring for GraphQL.

#### When to use / when NOT to use

GraphQL for mobile+web+partners with divergent data needs. REST+BFF when one team owns UI and API and deploys together. Prefer explicit documentation and gateway policies over tribal knowledge about which endpoints are safe to retry.

#### Production example

Marketplace with third-party apps: GraphQL public API. Internal React admin: BFF REST aggregating three microservices—simpler ops, standard JWT middleware. Runbooks should name the status codes, headers, and idempotency behavior operators will see during incidents.

#### Common mistakes

GraphQL without query depth/cost limits (DoS). REST returning 4MB graphs per list row. GraphQL to avoid designing REST resources.

#### Interview follow-ups (with model answers)

**Q:** BFF pattern details?
**A:** For «GraphQL vs REST for a Java+React app.», versioning is not optional decoration — it is part of the HTTP contract clients rely on when gateways retry or mobile apps replay requests. I store idempotency keys with a unique constraint, return the same response body on replay, and document TTL in OpenAPI. Spring `@RestController` advice maps domain exceptions to RFC 7807 Problem Details with stable `type` URIs. In staging I replay recorded traffic and run openapi-diff on every PR so breaking changes fail CI before partners see them.

**Q:** GraphQL subscriptions?
**A:** The follow-on risk for «GraphQL subscriptions» is inconsistent behavior across versions — v1 clients still calling deprecated fields while v2 expects structured money objects. I version via URL prefix or vendor media type, add `Sunset` and `Deprecation` headers, and metric traffic by version label. Spring validation groups separate create vs update DTOs; `@ControllerAdvice` ensures 409 on conflict instead of silent overwrites. Operators need runbook steps: which status codes are retryable, which require a new Idempotency-Key, and how BFF translates upstream errors without double-wrapping JSON.

**Q:** Codegen OpenAPI vs GraphQL schema?
**A:** Trade-off framing for «Codegen OpenAPI vs GraphQL schema»: optimize for integrator stability over internal convenience. Public APIs get cursor pagination, explicit error envelopes, rate-limit headers, and contract tests; internal admin endpoints may use offset pages but still need authz and tracing. I walk one real endpoint through the checklist: safe GET, idempotent PUT/DELETE, POST with keys for money paths, ETag on updates, and OpenAPI examples for 400/404/409/412. If I cannot explain retry semantics to a mobile engineer in two minutes, the design is not ready for production.

#### Scenario probe

**Situation:** After a release, traffic on endpoints touching «GraphQL vs REST for a Java+React app.» shows rising p99 latency and occasional duplicate side effects; mobile clients retry on gateway timeouts and support sees mismatched error JSON across services.

**Model answer:** I treat this as a contract and retry problem first, not a 'scale up pods' problem. I capture `X-Request-Id` across BFF and downstream services, compare Problem Details shapes, and replay a failing call with the same `Idempotency-Key` to see if POST is safe. Context: Marketplace with third-party apps: GraphQL public API. Internal React admin: BFF REST aggregating three microservices—simpler ops, standard JWT middleware. I verify GET safety, idempotent PUT/DELETE behavior, and whether Spring controllers return 409/412 instead of silent overwrites. OpenAPI diff against last release tells me if a field became required without a version bump. Short-term: tighten gateway timeouts with retry only on idempotent methods, fix error envelope in shared `@ControllerAdvice`. Long-term: contract tests, versioned DTOs, metrics on duplicate idempotency hits, and runbook steps for on-call.

---

### 25. gRPC-JSON transcoding.

**Short answer:** Run gRPC internally for performance and strong contracts; expose REST/JSON at the edge via transcoding (Envoy, gRPC-Gateway, Spring gRPC JSON transcoding). You maintain proto as source of truth but must keep HTTP semantics (status codes, errors) correct at the boundary. Document the contract in OpenAPI with examples and enforce it in CI with contract tests. Pair HTTP semantics with observability: correlation ids, structured Problem Details, and SLO dashboards on p99 latency.

#### What it is

Transcoding maps gRPC methods to HTTP JSON for browsers and legacy clients while keeping gRPC between services. This sits at the boundary between HTTP transport, Spring MVC dispatch, and client SDK expectations.

#### How it works (internals)

Proto defines messages; annotations (`google.api.http`) map RPC to REST paths. Gateway translates JSON ↔ protobuf. Two surfaces can drift if annotations lag proto changes.

#### When to use / when NOT to use

Polyglot microservices mesh with Java gRPC servers and public REST consumers. Less valuable for monolith-only shops. Prefer explicit documentation and gateway policies over tribal knowledge about which endpoints are safe to retry.

#### Production example

Order service speaks gRPC on port 9090; Envoy ingress exposes `GET /v1/orders/{id}` transcoded to `GetOrder` RPC. Problem Details mapped from `google.rpc.Status`. Runbooks should name the status codes, headers, and idempotency behavior operators will see during incidents.

#### Common mistakes

Leaking gRPC error codes without HTTP mapping. Maintaining separate REST DTOs and proto by hand. Ignoring streaming semantics at JSON boundary.

#### Interview follow-ups (with model answers)

**Q:** gRPC vs REST performance?
**A:** For «gRPC-JSON transcoding.», idempotency is not optional decoration — it is part of the HTTP contract clients rely on when gateways retry or mobile apps replay requests. I store idempotency keys with a unique constraint, return the same response body on replay, and document TTL in OpenAPI. Spring `@RestController` advice maps domain exceptions to RFC 7807 Problem Details with stable `type` URIs. In staging I replay recorded traffic and run openapi-diff on every PR so breaking changes fail CI before partners see them.

**Q:** When proto is not enough for REST?
**A:** The follow-on risk for «When proto is not enough for REST» is inconsistent behavior across versions — v1 clients still calling deprecated fields while v2 expects structured money objects. I version via URL prefix or vendor media type, add `Sunset` and `Deprecation` headers, and metric traffic by version label. Spring validation groups separate create vs update DTOs; `@ControllerAdvice` ensures 409 on conflict instead of silent overwrites. Operators need runbook steps: which status codes are retryable, which require a new Idempotency-Key, and how BFF translates upstream errors without double-wrapping JSON.

**Q:** mTLS between services?
**A:** Trade-off framing for «mTLS between services»: optimize for integrator stability over internal convenience. Public APIs get cursor pagination, explicit error envelopes, rate-limit headers, and contract tests; internal admin endpoints may use offset pages but still need authz and tracing. I walk one real endpoint through the checklist: safe GET, idempotent PUT/DELETE, POST with keys for money paths, ETag on updates, and OpenAPI examples for 400/404/409/412. If I cannot explain retry semantics to a mobile engineer in two minutes, the design is not ready for production.

#### Scenario probe

**Situation:** After a release, traffic on endpoints touching «gRPC-JSON transcoding.» shows rising p99 latency and occasional duplicate side effects; mobile clients retry on gateway timeouts and support sees mismatched error JSON across services.

**Model answer:** I treat this as a contract and retry problem first, not a 'scale up pods' problem. I capture `X-Request-Id` across BFF and downstream services, compare Problem Details shapes, and replay a failing call with the same `Idempotency-Key` to see if POST is safe. Context: Order service speaks gRPC on port 9090; Envoy ingress exposes `GET /v1/orders/{id}` transcoded to `GetOrder` RPC. Problem Details mapped from `google.rpc.Status`. I verify GET safety, idempotent PUT/DELETE behavior, and whether Spring controllers return 409/412 instead of silent overwrites. OpenAPI diff against last release tells me if a field became required without a version bump. Short-term: tighten gateway timeouts with retry only on idempotent methods, fix error envelope in shared `@ControllerAdvice`. Long-term: contract tests, versioned DTOs, metrics on duplicate idempotency hits, and runbook steps for on-call.

---

### 26. Security: BOLA/IDOR.

**Short answer:** Broken Object Level Authorization means callers access objects they should not—`GET /orders/123` when 123 belongs to another user. Every request must authorize the specific resource id, not just authenticate the caller. This is the top API vulnerability in OWASP API Security. Document the contract in OpenAPI with examples and enforce it in CI with contract tests.

#### What it is

BOLA (Broken Object Level Authorization) / IDOR (Insecure Direct Object Reference) is failing to check ownership or role on each object access. This sits at the boundary between HTTP transport, Spring MVC dispatch, and client SDK expectations.

#### How it works (internals)

Extract principal from JWT; query with `WHERE id = ? AND tenant_id = ? AND owner_id = ?`. Spring `@PreAuthorize` on service method with ownership check—not just role. Automated tests swap user A's token against user B's ids.

#### When to use / when NOT to use

Every endpoint with an id in the path or body. Admin bypass must be explicit and audited. Prefer explicit documentation and gateway policies over tribal knowledge about which endpoints are safe to retry.

#### Production example

`orderRepository.findByIdAndCustomerId(id, principal.getCustomerId())` or empty → 404. Horizontal privilege tests in CI with two fixture users. Runbooks should name the status codes, headers, and idempotency behavior operators will see during incidents.

#### Common mistakes

Checking JWT validity only. Relying on UI to hide buttons. Sequential ids without authz ('enumerate and steal').

#### Interview follow-ups (with model answers)

**Q:** 404 vs 403 for unauthorized object?
**A:** For «Security: BOLA/IDOR.», OpenAPI is not optional decoration — it is part of the HTTP contract clients rely on when gateways retry or mobile apps replay requests. I store idempotency keys with a unique constraint, return the same response body on replay, and document TTL in OpenAPI. Spring `@RestController` advice maps domain exceptions to RFC 7807 Problem Details with stable `type` URIs. In staging I replay recorded traffic and run openapi-diff on every PR so breaking changes fail CI before partners see them.

**Q:** ABAC vs ownership check?
**A:** The follow-on risk for «ABAC vs ownership check» is inconsistent behavior across versions — v1 clients still calling deprecated fields while v2 expects structured money objects. I version via URL prefix or vendor media type, add `Sunset` and `Deprecation` headers, and metric traffic by version label. Spring validation groups separate create vs update DTOs; `@ControllerAdvice` ensures 409 on conflict instead of silent overwrites. Operators need runbook steps: which status codes are retryable, which require a new Idempotency-Key, and how BFF translates upstream errors without double-wrapping JSON.

**Q:** How to test BOLA systematically?
**A:** Trade-off framing for «How to test BOLA systematically»: optimize for integrator stability over internal convenience. Public APIs get cursor pagination, explicit error envelopes, rate-limit headers, and contract tests; internal admin endpoints may use offset pages but still need authz and tracing. I walk one real endpoint through the checklist: safe GET, idempotent PUT/DELETE, POST with keys for money paths, ETag on updates, and OpenAPI examples for 400/404/409/412. If I cannot explain retry semantics to a mobile engineer in two minutes, the design is not ready for production.

#### Scenario probe

**Situation:** After a release, traffic on endpoints touching «Security: BOLA/IDOR.» shows rising p99 latency and occasional duplicate side effects; mobile clients retry on gateway timeouts and support sees mismatched error JSON across services.

**Model answer:** I treat this as a contract and retry problem first, not a 'scale up pods' problem. I capture `X-Request-Id` across BFF and downstream services, compare Problem Details shapes, and replay a failing call with the same `Idempotency-Key` to see if POST is safe. Context: `orderRepository.findByIdAndCustomerId(id, principal.getCustomerId())` or empty → 404. Horizontal privilege tests in CI with two fixture users. I verify GET safety, idempotent PUT/DELETE behavior, and whether Spring controllers return 409/412 instead of silent overwrites. OpenAPI diff against last release tells me if a field became required without a version bump. Short-term: tighten gateway timeouts with retry only on idempotent methods, fix error envelope in shared `@ControllerAdvice`. Long-term: contract tests, versioned DTOs, metrics on duplicate idempotency hits, and runbook steps for on-call.

---

### 27. Mass assignment.

**Short answer:** Mass assignment binds client JSON directly into domain entities, letting attackers set privileged fields (`role: ADMIN`, `price: 0`). Use separate request DTOs for input; never expose JPA entity on `@RequestBody`. Whitelist writable fields explicitly. Document the contract in OpenAPI with examples and enforce it in CI with contract tests.

#### What it is

Mass assignment is unintended field binding from client input to server models. This sits at the boundary between HTTP transport, Spring MVC dispatch, and client SDK expectations.

#### How it works (internals)

Spring binds JSON to `@RequestBody OrderCreateRequest` with only safe fields; service maps to entity. `@JsonIgnoreProperties(ignoreUnknown = true)` on DTOs. MapStruct or manual mapping to entity—no `BeanUtils.copyProperties(entity, request)` blindly.

#### When to use / when NOT to use

Always separate create/update DTOs from persistence models. Especially dangerous with `PATCH` and partial updates. Prefer explicit documentation and gateway policies over tribal knowledge about which endpoints are safe to retry.

#### Production example

User update DTO has `displayName` only; `role` changed via admin API with separate `RoleChangeRequest` and audit log. Entity `User` never appears in controller signature. Runbooks should name the status codes, headers, and idempotency behavior operators will see during incidents.

#### Common mistakes

Returning entity with lazy fields as JSON. `@RequestBody User user` on public API. OpenAPI exposing internal fields as writable.

#### Interview follow-ups (with model answers)

**Q:** MapStruct vs manual mapping?
**A:** For «Mass assignment.», Spring controllers is not optional decoration — it is part of the HTTP contract clients rely on when gateways retry or mobile apps replay requests. I store idempotency keys with a unique constraint, return the same response body on replay, and document TTL in OpenAPI. Spring `@RestController` advice maps domain exceptions to RFC 7807 Problem Details with stable `type` URIs. In staging I replay recorded traffic and run openapi-diff on every PR so breaking changes fail CI before partners see them.

**Q:** Partial update DTO design?
**A:** The follow-on risk for «Partial update DTO design» is inconsistent behavior across versions — v1 clients still calling deprecated fields while v2 expects structured money objects. I version via URL prefix or vendor media type, add `Sunset` and `Deprecation` headers, and metric traffic by version label. Spring validation groups separate create vs update DTOs; `@ControllerAdvice` ensures 409 on conflict instead of silent overwrites. Operators need runbook steps: which status codes are retryable, which require a new Idempotency-Key, and how BFF translates upstream errors without double-wrapping JSON.

**Q:** Jackson polymorphic gadgets?
**A:** Trade-off framing for «Jackson polymorphic gadgets»: optimize for integrator stability over internal convenience. Public APIs get cursor pagination, explicit error envelopes, rate-limit headers, and contract tests; internal admin endpoints may use offset pages but still need authz and tracing. I walk one real endpoint through the checklist: safe GET, idempotent PUT/DELETE, POST with keys for money paths, ETag on updates, and OpenAPI examples for 400/404/409/412. If I cannot explain retry semantics to a mobile engineer in two minutes, the design is not ready for production.

#### Scenario probe

**Situation:** After a release, traffic on endpoints touching «Mass assignment.» shows rising p99 latency and occasional duplicate side effects; mobile clients retry on gateway timeouts and support sees mismatched error JSON across services.

**Model answer:** I treat this as a contract and retry problem first, not a 'scale up pods' problem. I capture `X-Request-Id` across BFF and downstream services, compare Problem Details shapes, and replay a failing call with the same `Idempotency-Key` to see if POST is safe. Context: User update DTO has `displayName` only; `role` changed via admin API with separate `RoleChangeRequest` and audit log. Entity `User` never appears in controller signature. I verify GET safety, idempotent PUT/DELETE behavior, and whether Spring controllers return 409/412 instead of silent overwrites. OpenAPI diff against last release tells me if a field became required without a version bump. Short-term: tighten gateway timeouts with retry only on idempotent methods, fix error envelope in shared `@ControllerAdvice`. Long-term: contract tests, versioned DTOs, metrics on duplicate idempotency hits, and runbook steps for on-call.

---

### 28. SQL injection / JSON injection / log injection.

**Short answer:** Use parameterized queries (JPA, JDBC `?` binds)—never concatenate user input into SQL. Sanitize or structured-log user data to prevent log forging (CRLF). Disable dangerous Jackson default typing; validate JSON schema size and depth. Document the contract in OpenAPI with examples and enforce it in CI with contract tests.

#### What it is

Injection attacks smuggle executable fragments through inputs interpreted as code, queries, or log lines. This sits at the boundary between HTTP transport, Spring MVC dispatch, and client SDK expectations.

#### How it works (internals)

JPA `@Query` with named parameters; Criteria API. For dynamic sort, allowlist columns. Logging: use parameterized SLF4J `log.info("user={}", sanitize(user))`. JSON: reject `__proto__` style keys if relevant; limit parser depth.

#### When to use / when NOT to use

Always. Any dynamic SQL, logging of headers/URLs, or polymorphic deserialization paths. Prefer explicit documentation and gateway policies over tribal knowledge about which endpoints are safe to retry.

#### Production example

Search sort field mapped via `ALLOWED_SORT.get(param)` not string concat. Security review blocks `enableDefaultTyping` in Jackson—historical RCE vector. Runbooks should name the status codes, headers, and idempotency behavior operators will see during incidents.

#### Common mistakes

Native query with `${userInput}`. Logging full Authorization header. Trusting client Content-Type without validation.

#### Interview follow-ups (with model answers)

**Q:** JPA vs JDBC injection?
**A:** For «SQL injection / JSON injection / log injection.», versioning is not optional decoration — it is part of the HTTP contract clients rely on when gateways retry or mobile apps replay requests. I store idempotency keys with a unique constraint, return the same response body on replay, and document TTL in OpenAPI. Spring `@RestController` advice maps domain exceptions to RFC 7807 Problem Details with stable `type` URIs. In staging I replay recorded traffic and run openapi-diff on every PR so breaking changes fail CI before partners see them.

**Q:** Log4j JNDI lesson?
**A:** The follow-on risk for «Log4j JNDI lesson» is inconsistent behavior across versions — v1 clients still calling deprecated fields while v2 expects structured money objects. I version via URL prefix or vendor media type, add `Sunset` and `Deprecation` headers, and metric traffic by version label. Spring validation groups separate create vs update DTOs; `@ControllerAdvice` ensures 409 on conflict instead of silent overwrites. Operators need runbook steps: which status codes are retryable, which require a new Idempotency-Key, and how BFF translates upstream errors without double-wrapping JSON.

**Q:** NoSQL injection in Mongo?
**A:** Trade-off framing for «NoSQL injection in Mongo»: optimize for integrator stability over internal convenience. Public APIs get cursor pagination, explicit error envelopes, rate-limit headers, and contract tests; internal admin endpoints may use offset pages but still need authz and tracing. I walk one real endpoint through the checklist: safe GET, idempotent PUT/DELETE, POST with keys for money paths, ETag on updates, and OpenAPI examples for 400/404/409/412. If I cannot explain retry semantics to a mobile engineer in two minutes, the design is not ready for production.

#### Scenario probe

**Situation:** After a release, traffic on endpoints touching «SQL injection / JSON injection / log injection.» shows rising p99 latency and occasional duplicate side effects; mobile clients retry on gateway timeouts and support sees mismatched error JSON across services.

**Model answer:** I treat this as a contract and retry problem first, not a 'scale up pods' problem. I capture `X-Request-Id` across BFF and downstream services, compare Problem Details shapes, and replay a failing call with the same `Idempotency-Key` to see if POST is safe. Context: Search sort field mapped via `ALLOWED_SORT.get(param)` not string concat. Security review blocks `enableDefaultTyping` in Jackson—historical RCE vector. I verify GET safety, idempotent PUT/DELETE behavior, and whether Spring controllers return 409/412 instead of silent overwrites. OpenAPI diff against last release tells me if a field became required without a version bump. Short-term: tighten gateway timeouts with retry only on idempotent methods, fix error envelope in shared `@ControllerAdvice`. Long-term: contract tests, versioned DTOs, metrics on duplicate idempotency hits, and runbook steps for on-call.

---

### 29. SSRF from URL fields.

**Short answer:** User-supplied URLs (webhooks, avatar fetch, import-from-url) can probe internal networks (`169.254.169.254`, localhost). Block private IP ranges, metadata endpoints, and non-HTTP schemes. Prefer allowlists over blocklists. Document the contract in OpenAPI with examples and enforce it in CI with contract tests.

#### What it is

Server-Side Request Forgery tricks your server into calling attacker-chosen URLs, often reaching internal services. This sits at the boundary between HTTP transport, Spring MVC dispatch, and client SDK expectations.

#### How it works (internals)

Resolve DNS, validate IP against deny list (RFC1918, link-local, cloud metadata). Use dedicated egress proxy with policy. Fetch with timeouts, no redirects to internal hosts, disable file:// and gopher://.

#### When to use / when NOT to use

Any API field accepting URL—webhook registration, PDF render from URL, image proxy. Prefer explicit documentation and gateway policies over tribal knowledge about which endpoints are safe to retry.

#### Production example

Webhook URL validator resolves hostname, rejects if IP in `169.254.0.0/16` or `127.0.0.0/8`. Fetch runs in isolated worker with no cloud IAM credentials. Runbooks should name the status codes, headers, and idempotency behavior operators will see during incidents.

#### Common mistakes

Blacklist-only (bypass with DNS rebinding). Following unlimited redirects. SSRF in PDF generators and OG scrapers.

#### Interview follow-ups (with model answers)

**Q:** DNS rebinding mitigations?
**A:** For «SSRF from URL fields.», idempotency is not optional decoration — it is part of the HTTP contract clients rely on when gateways retry or mobile apps replay requests. I store idempotency keys with a unique constraint, return the same response body on replay, and document TTL in OpenAPI. Spring `@RestController` advice maps domain exceptions to RFC 7807 Problem Details with stable `type` URIs. In staging I replay recorded traffic and run openapi-diff on every PR so breaking changes fail CI before partners see them.

**Q:** Allowlist partner domains?
**A:** The follow-on risk for «Allowlist partner domains» is inconsistent behavior across versions — v1 clients still calling deprecated fields while v2 expects structured money objects. I version via URL prefix or vendor media type, add `Sunset` and `Deprecation` headers, and metric traffic by version label. Spring validation groups separate create vs update DTOs; `@ControllerAdvice` ensures 409 on conflict instead of silent overwrites. Operators need runbook steps: which status codes are retryable, which require a new Idempotency-Key, and how BFF translates upstream errors without double-wrapping JSON.

**Q:** SSRF in Kubernetes?
**A:** Trade-off framing for «SSRF in Kubernetes»: optimize for integrator stability over internal convenience. Public APIs get cursor pagination, explicit error envelopes, rate-limit headers, and contract tests; internal admin endpoints may use offset pages but still need authz and tracing. I walk one real endpoint through the checklist: safe GET, idempotent PUT/DELETE, POST with keys for money paths, ETag on updates, and OpenAPI examples for 400/404/409/412. If I cannot explain retry semantics to a mobile engineer in two minutes, the design is not ready for production.

#### Scenario probe

**Situation:** After a release, traffic on endpoints touching «SSRF from URL fields.» shows rising p99 latency and occasional duplicate side effects; mobile clients retry on gateway timeouts and support sees mismatched error JSON across services.

**Model answer:** I treat this as a contract and retry problem first, not a 'scale up pods' problem. I capture `X-Request-Id` across BFF and downstream services, compare Problem Details shapes, and replay a failing call with the same `Idempotency-Key` to see if POST is safe. Context: Webhook URL validator resolves hostname, rejects if IP in `169.254.0.0/16` or `127.0.0.0/8`. Fetch runs in isolated worker with no cloud IAM credentials. I verify GET safety, idempotent PUT/DELETE behavior, and whether Spring controllers return 409/412 instead of silent overwrites. OpenAPI diff against last release tells me if a field became required without a version bump. Short-term: tighten gateway timeouts with retry only on idempotent methods, fix error envelope in shared `@ControllerAdvice`. Long-term: contract tests, versioned DTOs, metrics on duplicate idempotency hits, and runbook steps for on-call.

---

### 30. TLS, HSTS, mTLS.

**Short answer:** TLS encrypts traffic in transit—terminate at edge with modern cipher suites. HSTS tells browsers to use HTTPS only. mTLS authenticates service-to-service clients with certificates. Do not send sensitive data plaintext inside 'trusted' networks without justification. Document the contract in OpenAPI with examples and enforce it in CI with contract tests.

#### What it is

Transport security protects confidentiality and integrity; mTLS adds mutual authentication between services. This sits at the boundary between HTTP transport, Spring MVC dispatch, and client SDK expectations.

#### How it works (internals)

Ingress handles TLS 1.2+; cert rotation via cert-manager. HSTS header `Strict-Transport-Security: max-age=31536000; includeSubDomains`. mTLS in mesh (Istio) or Spring Boot `server.ssl.client-auth=need` for partner APIs. Spring maps requests through `DispatcherServlet`, `HandlerMapping`, and `HttpMessageConverter` chains before your service layer runs.

#### When to use / when NOT to use

TLS everywhere public. mTLS for zero-trust service mesh and B2B APIs. HSTS on all production web properties. Prefer explicit documentation and gateway policies over tribal knowledge about which endpoints are safe to retry.

#### Production example

Public API behind ALB with ACM cert; pod-to-pod mTLS via Istio; partner integration requires client cert registered in API gateway. Runbooks should name the status codes, headers, and idempotency behavior operators will see during incidents.

#### Common mistakes

TLS terminated at edge then HTTP to pods on shared network. Expired certs without monitoring. Weak TLS versions for 'compat'.

#### Interview follow-ups (with model answers)

**Q:** TLS passthrough vs terminate?
**A:** For «TLS, HSTS, mTLS.», OpenAPI is not optional decoration — it is part of the HTTP contract clients rely on when gateways retry or mobile apps replay requests. I store idempotency keys with a unique constraint, return the same response body on replay, and document TTL in OpenAPI. Spring `@RestController` advice maps domain exceptions to RFC 7807 Problem Details with stable `type` URIs. In staging I replay recorded traffic and run openapi-diff on every PR so breaking changes fail CI before partners see them.

**Q:** Certificate pinning?
**A:** The follow-on risk for «Certificate pinning» is inconsistent behavior across versions — v1 clients still calling deprecated fields while v2 expects structured money objects. I version via URL prefix or vendor media type, add `Sunset` and `Deprecation` headers, and metric traffic by version label. Spring validation groups separate create vs update DTOs; `@ControllerAdvice` ensures 409 on conflict instead of silent overwrites. Operators need runbook steps: which status codes are retryable, which require a new Idempotency-Key, and how BFF translates upstream errors without double-wrapping JSON.

**Q:** Let's Encrypt rotation?
**A:** Trade-off framing for «Let's Encrypt rotation»: optimize for integrator stability over internal convenience. Public APIs get cursor pagination, explicit error envelopes, rate-limit headers, and contract tests; internal admin endpoints may use offset pages but still need authz and tracing. I walk one real endpoint through the checklist: safe GET, idempotent PUT/DELETE, POST with keys for money paths, ETag on updates, and OpenAPI examples for 400/404/409/412. If I cannot explain retry semantics to a mobile engineer in two minutes, the design is not ready for production.

#### Scenario probe

**Situation:** After a release, traffic on endpoints touching «TLS, HSTS, mTLS.» shows rising p99 latency and occasional duplicate side effects; mobile clients retry on gateway timeouts and support sees mismatched error JSON across services.

**Model answer:** I treat this as a contract and retry problem first, not a 'scale up pods' problem. I capture `X-Request-Id` across BFF and downstream services, compare Problem Details shapes, and replay a failing call with the same `Idempotency-Key` to see if POST is safe. Context: Public API behind ALB with ACM cert; pod-to-pod mTLS via Istio; partner integration requires client cert registered in API gateway. I verify GET safety, idempotent PUT/DELETE behavior, and whether Spring controllers return 409/412 instead of silent overwrites. OpenAPI diff against last release tells me if a field became required without a version bump. Short-term: tighten gateway timeouts with retry only on idempotent methods, fix error envelope in shared `@ControllerAdvice`. Long-term: contract tests, versioned DTOs, metrics on duplicate idempotency hits, and runbook steps for on-call.

---

### 31. Content types and versioning via media type.

**Short answer:** Use explicit `Content-Type` and `Accept` headers—typically `application/json; charset=utf-8`. Version via vendor media types (`application/vnd.example.v2+json`) when avoiding URL versions. Reject unknown charsets and do not rely on content sniffing. Document the contract in OpenAPI with examples and enforce it in CI with contract tests.

#### What it is

Media types tell clients and servers how to parse bodies; vendor types embed API version in the format identifier. This sits at the boundary between HTTP transport, Spring MVC dispatch, and client SDK expectations.

#### How it works (internals)

Spring `consumes`/`produces` on mappings; `HttpMessageConverter` selects Jackson for JSON. Custom `application/vnd.acme.orders.v2+json` registered with separate DTO mappers if needed. `ContentNegotiation` resolves Accept header.

#### When to use / when NOT to use

Standard JSON for most APIs. Vendor media types when URLs must stay frozen (legal, long-cache) but schema evolves. Prefer explicit documentation and gateway policies over tribal knowledge about which endpoints are safe to retry.

#### Production example

v1 clients send `Accept: application/vnd.shop.orders.v1+json`; gateway routes to legacy controller package. v2 uses v2 DTO with new money fields as structured object. Runbooks should name the status codes, headers, and idempotency behavior operators will see during incidents.

#### Common mistakes

Missing charset causing mojibake. `*/*` accept on server without testing. Two versions sharing same media type.

#### Interview follow-ups (with model answers)

**Q:** Content negotiation in Spring?
**A:** For «Content types and versioning via media type.», Spring controllers is not optional decoration — it is part of the HTTP contract clients rely on when gateways retry or mobile apps replay requests. I store idempotency keys with a unique constraint, return the same response body on replay, and document TTL in OpenAPI. Spring `@RestController` advice maps domain exceptions to RFC 7807 Problem Details with stable `type` URIs. In staging I replay recorded traffic and run openapi-diff on every PR so breaking changes fail CI before partners see them.

**Q:** JSON vs application/problem+json?
**A:** The follow-on risk for «JSON vs application/problem+json» is inconsistent behavior across versions — v1 clients still calling deprecated fields while v2 expects structured money objects. I version via URL prefix or vendor media type, add `Sunset` and `Deprecation` headers, and metric traffic by version label. Spring validation groups separate create vs update DTOs; `@ControllerAdvice` ensures 409 on conflict instead of silent overwrites. Operators need runbook steps: which status codes are retryable, which require a new Idempotency-Key, and how BFF translates upstream errors without double-wrapping JSON.

**Q:** When vendor types beat /v2 URL?
**A:** Trade-off framing for «When vendor types beat /v2 URL»: optimize for integrator stability over internal convenience. Public APIs get cursor pagination, explicit error envelopes, rate-limit headers, and contract tests; internal admin endpoints may use offset pages but still need authz and tracing. I walk one real endpoint through the checklist: safe GET, idempotent PUT/DELETE, POST with keys for money paths, ETag on updates, and OpenAPI examples for 400/404/409/412. If I cannot explain retry semantics to a mobile engineer in two minutes, the design is not ready for production.

#### Scenario probe

**Situation:** After a release, traffic on endpoints touching «Content types and versioning via media type.» shows rising p99 latency and occasional duplicate side effects; mobile clients retry on gateway timeouts and support sees mismatched error JSON across services.

**Model answer:** I treat this as a contract and retry problem first, not a 'scale up pods' problem. I capture `X-Request-Id` across BFF and downstream services, compare Problem Details shapes, and replay a failing call with the same `Idempotency-Key` to see if POST is safe. Context: v1 clients send `Accept: application/vnd.shop.orders.v1+json`; gateway routes to legacy controller package. v2 uses v2 DTO with new money fields as structured object. I verify GET safety, idempotent PUT/DELETE behavior, and whether Spring controllers return 409/412 instead of silent overwrites. OpenAPI diff against last release tells me if a field became required without a version bump. Short-term: tighten gateway timeouts with retry only on idempotent methods, fix error envelope in shared `@ControllerAdvice`. Long-term: contract tests, versioned DTOs, metrics on duplicate idempotency hits, and runbook steps for on-call.

---

### 32. Date formats.

**Short answer:** Use ISO-8601 in UTC with offset or `Z` suffix: `2026-09-05T10:30:00Z`. Document whether instants or local wall times. In Java prefer `Instant` for timestamps; `OffsetDateTime` when zone matters. Avoid ambiguous epoch millis without documenting unit.

#### What it is

Consistent date serialization prevents timezone bugs across services and clients. This sits at the boundary between HTTP transport, Spring MVC dispatch, and client SDK expectations.

#### How it works (internals)

Jackson `JavaTimeModule` serializes `Instant` as ISO-8601 by default. Configure `ObjectMapper` globally—do not mix `Date`, `long`, and `String` across endpoints. OpenAPI `format: date-time` documents expectation.

#### When to use / when NOT to use

Always ISO-8601 for APIs. Local dates (`2026-09-05`) only for calendar dates without time (birthdays, billing periods). Prefer explicit documentation and gateway policies over tribal knowledge about which endpoints are safe to retry.

#### Production example

All API timestamps are `Instant` stored UTC in DB (`timestamptz`). React parses with `date-fns` assuming Zulu. Legacy field `createdAtMillis` deprecated in favor of `createdAt`.

#### Common mistakes

Server local timezone in JSON without offset. Mixing seconds and milliseconds epoch. `new Date()` in JSON as ambiguous string.

#### Interview follow-ups (with model answers)

**Q:** Instant vs ZonedDateTime?
**A:** For «Date formats.», versioning is not optional decoration — it is part of the HTTP contract clients rely on when gateways retry or mobile apps replay requests. I store idempotency keys with a unique constraint, return the same response body on replay, and document TTL in OpenAPI. Spring `@RestController` advice maps domain exceptions to RFC 7807 Problem Details with stable `type` URIs. In staging I replay recorded traffic and run openapi-diff on every PR so breaking changes fail CI before partners see them.

**Q:** How do you handle DST for appointments?
**A:** The follow-on risk for «How do you handle DST for appointments» is inconsistent behavior across versions — v1 clients still calling deprecated fields while v2 expects structured money objects. I version via URL prefix or vendor media type, add `Sunset` and `Deprecation` headers, and metric traffic by version label. Spring validation groups separate create vs update DTOs; `@ControllerAdvice` ensures 409 on conflict instead of silent overwrites. Operators need runbook steps: which status codes are retryable, which require a new Idempotency-Key, and how BFF translates upstream errors without double-wrapping JSON.

**Q:** Database timestamptz vs timestamp?
**A:** Trade-off framing for «Database timestamptz vs timestamp»: optimize for integrator stability over internal convenience. Public APIs get cursor pagination, explicit error envelopes, rate-limit headers, and contract tests; internal admin endpoints may use offset pages but still need authz and tracing. I walk one real endpoint through the checklist: safe GET, idempotent PUT/DELETE, POST with keys for money paths, ETag on updates, and OpenAPI examples for 400/404/409/412. If I cannot explain retry semantics to a mobile engineer in two minutes, the design is not ready for production.

#### Scenario probe

**Situation:** After a release, traffic on endpoints touching «Date formats.» shows rising p99 latency and occasional duplicate side effects; mobile clients retry on gateway timeouts and support sees mismatched error JSON across services.

**Model answer:** I treat this as a contract and retry problem first, not a 'scale up pods' problem. I capture `X-Request-Id` across BFF and downstream services, compare Problem Details shapes, and replay a failing call with the same `Idempotency-Key` to see if POST is safe. Context: All API timestamps are `Instant` stored UTC in DB (`timestamptz`). React parses with `date-fns` assuming Zulu. Legacy field `createdAtMillis` deprecated in favor of `createdAt`. I verify GET safety, idempotent PUT/DELETE behavior, and whether Spring controllers return 409/412 instead of silent overwrites. OpenAPI diff against last release tells me if a field became required without a version bump. Short-term: tighten gateway timeouts with retry only on idempotent methods, fix error envelope in shared `@ControllerAdvice`. Long-term: contract tests, versioned DTOs, metrics on duplicate idempotency hits, and runbook steps for on-call.

#### Code / config (when useful)
```java
@Bean
ObjectMapper objectMapper() {
  return JsonMapper.builder()
      .addModule(new JavaTimeModule())
      .disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS)
      .build();
}
```

---

### 33. Null vs omitted vs empty.

**Short answer:** Document semantics: omitted field in PATCH means 'leave unchanged'; `null` may mean 'clear value' if you support it; empty string `` is a value, not absence. OpenAPI `required` vs `nullable` must match runtime behavior. Document the contract in OpenAPI with examples and enforce it in CI with contract tests. Pair HTTP semantics with observability: correlation ids, structured Problem Details, and SLO dashboards on p99 latency.

#### What it is

JSON null, omission, and empty collections carry different meanings—clients and servers must agree. This sits at the boundary between HTTP transport, Spring MVC dispatch, and client SDK expectations.

#### How it works (internals)

Jackson `JsonInclude.NON_NULL` omits nulls on output. PATCH merge patch: absent key = no change; null = set null. For lists, define whether `[]` clears or `null` clears vs omit = unchanged.

#### When to use / when NOT to use

Critical for PATCH and partial updates. Create (POST) often treats omitted optional fields as null/default. Prefer explicit documentation and gateway policies over tribal knowledge about which endpoints are safe to retry.

#### Production example

Profile PATCH: omit phone → unchanged; JSON null on phone → delete; empty string → validation error. Documented in OpenAPI with examples. Runbooks should name the status codes, headers, and idempotency behavior operators will see during incidents.

#### Common mistakes

Inconsistent null handling across endpoints. Using null for 'empty list' without documenting. Clients cannot distinguish missing from null when both omitted in responses.

#### Interview follow-ups (with model answers)

**Q:** JsonNullable in OpenAPI 3?
**A:** For «Null vs omitted vs empty.», idempotency is not optional decoration — it is part of the HTTP contract clients rely on when gateways retry or mobile apps replay requests. I store idempotency keys with a unique constraint, return the same response body on replay, and document TTL in OpenAPI. Spring `@RestController` advice maps domain exceptions to RFC 7807 Problem Details with stable `type` URIs. In staging I replay recorded traffic and run openapi-diff on every PR so breaking changes fail CI before partners see them.

**Q:** Optional vs nullable in Java records?
**A:** The follow-on risk for «Optional vs nullable in Java records» is inconsistent behavior across versions — v1 clients still calling deprecated fields while v2 expects structured money objects. I version via URL prefix or vendor media type, add `Sunset` and `Deprecation` headers, and metric traffic by version label. Spring validation groups separate create vs update DTOs; `@ControllerAdvice` ensures 409 on conflict instead of silent overwrites. Operators need runbook steps: which status codes are retryable, which require a new Idempotency-Key, and how BFF translates upstream errors without double-wrapping JSON.

**Q:** Database NULL vs empty string?
**A:** Trade-off framing for «Database NULL vs empty string»: optimize for integrator stability over internal convenience. Public APIs get cursor pagination, explicit error envelopes, rate-limit headers, and contract tests; internal admin endpoints may use offset pages but still need authz and tracing. I walk one real endpoint through the checklist: safe GET, idempotent PUT/DELETE, POST with keys for money paths, ETag on updates, and OpenAPI examples for 400/404/409/412. If I cannot explain retry semantics to a mobile engineer in two minutes, the design is not ready for production.

#### Scenario probe

**Situation:** After a release, traffic on endpoints touching «Null vs omitted vs empty.» shows rising p99 latency and occasional duplicate side effects; mobile clients retry on gateway timeouts and support sees mismatched error JSON across services.

**Model answer:** I treat this as a contract and retry problem first, not a 'scale up pods' problem. I capture `X-Request-Id` across BFF and downstream services, compare Problem Details shapes, and replay a failing call with the same `Idempotency-Key` to see if POST is safe. Context: Profile PATCH: omit phone → unchanged; JSON null on phone → delete; empty string → validation error. Documented in OpenAPI with examples. I verify GET safety, idempotent PUT/DELETE behavior, and whether Spring controllers return 409/412 instead of silent overwrites. OpenAPI diff against last release tells me if a field became required without a version bump. Short-term: tighten gateway timeouts with retry only on idempotent methods, fix error envelope in shared `@ControllerAdvice`. Long-term: contract tests, versioned DTOs, metrics on duplicate idempotency hits, and runbook steps for on-call.

---

### 34. Hypermedia pagination links.

**Short answer:** Return pagination links (`rel=next`, `prev`, `first`) in Link header or `_links` object so clients follow opaque cursors instead of constructing page math. Cursor tokens should be opaque (signed or encrypted) to prevent tampering. Document the contract in OpenAPI with examples and enforce it in CI with contract tests. Pair HTTP semantics with observability: correlation ids, structured Problem Details, and SLO dashboards on p99 latency.

#### What it is

Hypermedia pagination embeds navigation in the response rather than requiring clients to build URLs. This sits at the boundary between HTTP transport, Spring MVC dispatch, and client SDK expectations.

#### How it works (internals)

RFC 8288 Link header: `Link: <https://api.example.com/orders?cursor=abc>; rel="next"`. Spring HATEOAS `PagedModel` adds links. Cursor encodes last-seen sort key, base64url-encoded.

#### When to use / when NOT to use

Public APIs and mobile clients benefit from stable next links. Internal apps may use simple `nextCursor` JSON field. Prefer explicit documentation and gateway policies over tribal knowledge about which endpoints are safe to retry.

#### Production example

Orders list returns `{items, _links: {next: {href: "...?cursor=eyJ..."}}}`. Cursor is HMAC-signed payload with expiry. Runbooks should name the status codes, headers, and idempotency behavior operators will see during incidents.

#### Common mistakes

Exposing raw SQL offset in cursor. No `rel` names standardization. next link without HTTPS. Teams often discover these failures only after mobile clients retry on flaky networks or CDNs cache a non-safe GET.

#### Interview follow-ups (with model answers)

**Q:** Link header vs JSON _links?
**A:** For «Hypermedia pagination links.», OpenAPI is not optional decoration — it is part of the HTTP contract clients rely on when gateways retry or mobile apps replay requests. I store idempotency keys with a unique constraint, return the same response body on replay, and document TTL in OpenAPI. Spring `@RestController` advice maps domain exceptions to RFC 7807 Problem Details with stable `type` URIs. In staging I replay recorded traffic and run openapi-diff on every PR so breaking changes fail CI before partners see them.

**Q:** Cursor signing?
**A:** The follow-on risk for «Cursor signing» is inconsistent behavior across versions — v1 clients still calling deprecated fields while v2 expects structured money objects. I version via URL prefix or vendor media type, add `Sunset` and `Deprecation` headers, and metric traffic by version label. Spring validation groups separate create vs update DTOs; `@ControllerAdvice` ensures 409 on conflict instead of silent overwrites. Operators need runbook steps: which status codes are retryable, which require a new Idempotency-Key, and how BFF translates upstream errors without double-wrapping JSON.

**Q:** RFC 5988 vs 8288?
**A:** Trade-off framing for «RFC 5988 vs 8288»: optimize for integrator stability over internal convenience. Public APIs get cursor pagination, explicit error envelopes, rate-limit headers, and contract tests; internal admin endpoints may use offset pages but still need authz and tracing. I walk one real endpoint through the checklist: safe GET, idempotent PUT/DELETE, POST with keys for money paths, ETag on updates, and OpenAPI examples for 400/404/409/412. If I cannot explain retry semantics to a mobile engineer in two minutes, the design is not ready for production.

#### Scenario probe

**Situation:** After a release, traffic on endpoints touching «Hypermedia pagination links.» shows rising p99 latency and occasional duplicate side effects; mobile clients retry on gateway timeouts and support sees mismatched error JSON across services.

**Model answer:** I treat this as a contract and retry problem first, not a 'scale up pods' problem. I capture `X-Request-Id` across BFF and downstream services, compare Problem Details shapes, and replay a failing call with the same `Idempotency-Key` to see if POST is safe. Context: Orders list returns `{items, _links: {next: {href: "...?cursor=eyJ..."}}}`. Cursor is HMAC-signed payload with expiry. I verify GET safety, idempotent PUT/DELETE behavior, and whether Spring controllers return 409/412 instead of silent overwrites. OpenAPI diff against last release tells me if a field became required without a version bump. Short-term: tighten gateway timeouts with retry only on idempotent methods, fix error envelope in shared `@ControllerAdvice`. Long-term: contract tests, versioned DTOs, metrics on duplicate idempotency hits, and runbook steps for on-call.

---

### 35. HEAD and OPTIONS.

**Short answer:** HEAD returns headers like GET without body—useful for existence checks and ETag without payload cost. OPTIONS answers CORS preflight and allowed methods. Implement HEAD if GET is expensive; Spring often supports it automatically for mapped GET. Document the contract in OpenAPI with examples and enforce it in CI with contract tests.

#### What it is

HEAD and OPTIONS are HTTP methods with specialized roles in caching, CORS, and metadata probes. This sits at the boundary between HTTP transport, Spring MVC dispatch, and client SDK expectations.

#### How it works (internals)

HEAD should match GET status and headers (including Content-Length logic). OPTIONS for CORS returns `Access-Control-*`. Spring MVC dispatches HEAD to GET handlers when HEAD not explicitly mapped.

#### When to use / when NOT to use

HEAD before large downloads to check ETag/Last-Modified. OPTIONS required for browser CORS on non-simple requests. Prefer explicit documentation and gateway policies over tribal knowledge about which endpoints are safe to retry.

#### Production example

CDN uses HEAD on `/assets/report.pdf` for `If-None-Match`. API gateway responds OPTIONS for SPA preflight before POST with Authorization. Runbooks should name the status codes, headers, and idempotency behavior operators will see during incidents.

#### Common mistakes

HEAD runs full GET business logic including side effects (must not). OPTIONS missing on new custom headers. Different ETag on HEAD vs GET.

#### Interview follow-ups (with model answers)

**Q:** HEAD for health checks?
**A:** For «HEAD and OPTIONS.», Spring controllers is not optional decoration — it is part of the HTTP contract clients rely on when gateways retry or mobile apps replay requests. I store idempotency keys with a unique constraint, return the same response body on replay, and document TTL in OpenAPI. Spring `@RestController` advice maps domain exceptions to RFC 7807 Problem Details with stable `type` URIs. In staging I replay recorded traffic and run openapi-diff on every PR so breaking changes fail CI before partners see them.

**Q:** OPTIONS on 404?
**A:** The follow-on risk for «OPTIONS on 404» is inconsistent behavior across versions — v1 clients still calling deprecated fields while v2 expects structured money objects. I version via URL prefix or vendor media type, add `Sunset` and `Deprecation` headers, and metric traffic by version label. Spring validation groups separate create vs update DTOs; `@ControllerAdvice` ensures 409 on conflict instead of silent overwrites. Operators need runbook steps: which status codes are retryable, which require a new Idempotency-Key, and how BFF translates upstream errors without double-wrapping JSON.

**Q:** Spring Security and OPTIONS?
**A:** Trade-off framing for «Spring Security and OPTIONS»: optimize for integrator stability over internal convenience. Public APIs get cursor pagination, explicit error envelopes, rate-limit headers, and contract tests; internal admin endpoints may use offset pages but still need authz and tracing. I walk one real endpoint through the checklist: safe GET, idempotent PUT/DELETE, POST with keys for money paths, ETag on updates, and OpenAPI examples for 400/404/409/412. If I cannot explain retry semantics to a mobile engineer in two minutes, the design is not ready for production.

#### Scenario probe

**Situation:** After a release, traffic on endpoints touching «HEAD and OPTIONS.» shows rising p99 latency and occasional duplicate side effects; mobile clients retry on gateway timeouts and support sees mismatched error JSON across services.

**Model answer:** I treat this as a contract and retry problem first, not a 'scale up pods' problem. I capture `X-Request-Id` across BFF and downstream services, compare Problem Details shapes, and replay a failing call with the same `Idempotency-Key` to see if POST is safe. Context: CDN uses HEAD on `/assets/report.pdf` for `If-None-Match`. API gateway responds OPTIONS for SPA preflight before POST with Authorization. I verify GET safety, idempotent PUT/DELETE behavior, and whether Spring controllers return 409/412 instead of silent overwrites. OpenAPI diff against last release tells me if a field became required without a version bump. Short-term: tighten gateway timeouts with retry only on idempotent methods, fix error envelope in shared `@ControllerAdvice`. Long-term: contract tests, versioned DTOs, metrics on duplicate idempotency hits, and runbook steps for on-call.

---

### 36. Consistency of error envelopes.

**Short answer:** One error shape across services—typically RFC 7807 Problem Details with extensions (`traceId`, `errors[]`). Gateways should not double-wrap errors. Propagate correlation id in `X-Request-Id` header and error body for support tickets. Document the contract in OpenAPI with examples and enforce it in CI with contract tests.

#### What it is

Consistent error envelopes let clients, BFFs, and observability tools parse failures uniformly. This sits at the boundary between HTTP transport, Spring MVC dispatch, and client SDK expectations.

#### How it works (internals)

Shared library provides `@ControllerAdvice` base class. MDC stores trace id from incoming header or generated UUID; filter adds to response. BFF maps downstream 4xx/5xx to same schema without nesting `{error: {error: ...}}`.

#### When to use / when NOT to use

Mandatory multi-service estates. Even monoliths benefit from one pattern documented in OpenAPI. Prefer explicit documentation and gateway policies over tribal knowledge about which endpoints are safe to retry.

#### Production example

All services return Problem Detail; BFF forwards `type` and `detail` unchanged, adds `upstream: orders-service`. Kibana searches by `traceId` across logs. Runbooks should name the status codes, headers, and idempotency behavior operators will see during incidents.

#### Common mistakes

HTML error pages from gateway on API routes. Different JSON shapes per team. Swallowing downstream detail.

#### Interview follow-ups (with model answers)

**Q:** Error catalog with stable type URIs?
**A:** For «Consistency of error envelopes.», versioning is not optional decoration — it is part of the HTTP contract clients rely on when gateways retry or mobile apps replay requests. I store idempotency keys with a unique constraint, return the same response body on replay, and document TTL in OpenAPI. Spring `@RestController` advice maps domain exceptions to RFC 7807 Problem Details with stable `type` URIs. In staging I replay recorded traffic and run openapi-diff on every PR so breaking changes fail CI before partners see them.

**Q:** i18n for errors?
**A:** The follow-on risk for «i18n for errors» is inconsistent behavior across versions — v1 clients still calling deprecated fields while v2 expects structured money objects. I version via URL prefix or vendor media type, add `Sunset` and `Deprecation` headers, and metric traffic by version label. Spring validation groups separate create vs update DTOs; `@ControllerAdvice` ensures 409 on conflict instead of silent overwrites. Operators need runbook steps: which status codes are retryable, which require a new Idempotency-Key, and how BFF translates upstream errors without double-wrapping JSON.

**Q:** Map exceptions to types centrally?
**A:** Trade-off framing for «Map exceptions to types centrally»: optimize for integrator stability over internal convenience. Public APIs get cursor pagination, explicit error envelopes, rate-limit headers, and contract tests; internal admin endpoints may use offset pages but still need authz and tracing. I walk one real endpoint through the checklist: safe GET, idempotent PUT/DELETE, POST with keys for money paths, ETag on updates, and OpenAPI examples for 400/404/409/412. If I cannot explain retry semantics to a mobile engineer in two minutes, the design is not ready for production.

#### Scenario probe

**Situation:** After a release, traffic on endpoints touching «Consistency of error envelopes.» shows rising p99 latency and occasional duplicate side effects; mobile clients retry on gateway timeouts and support sees mismatched error JSON across services.

**Model answer:** I treat this as a contract and retry problem first, not a 'scale up pods' problem. I capture `X-Request-Id` across BFF and downstream services, compare Problem Details shapes, and replay a failing call with the same `Idempotency-Key` to see if POST is safe. Context: All services return Problem Detail; BFF forwards `type` and `detail` unchanged, adds `upstream: orders-service`. Kibana searches by `traceId` across logs. I verify GET safety, idempotent PUT/DELETE behavior, and whether Spring controllers return 409/412 instead of silent overwrites. OpenAPI diff against last release tells me if a field became required without a version bump. Short-term: tighten gateway timeouts with retry only on idempotent methods, fix error envelope in shared `@ControllerAdvice`. Long-term: contract tests, versioned DTOs, metrics on duplicate idempotency hits, and runbook steps for on-call.

---

### 37. Idempotent delete.

**Short answer:** DELETE should be idempotent: deleting an already-deleted resource returns 204 No Content (or 200) rather than 404—pick one policy and document it. Repeated DELETE must not error or change state further. Document the contract in OpenAPI with examples and enforce it in CI with contract tests. Pair HTTP semantics with observability: correlation ids, structured Problem Details, and SLO dashboards on p99 latency.

#### What it is

Idempotent delete means multiple identical DELETE requests have the same effect as one. This sits at the boundary between HTTP transport, Spring MVC dispatch, and client SDK expectations.

#### How it works (internals)

Soft-delete: second DELETE returns 204; resource remains tombstoned. Hard-delete: second DELETE still 204—client cannot tell if first delete succeeded. Some APIs use 404 to hide existence—less idempotent-friendly.

#### When to use / when NOT to use

Prefer 204 on repeat for retry-safe clients and network failures. 404 only if revealing existence is a security concern and retries are handled elsewhere. Prefer explicit documentation and gateway policies over tribal knowledge about which endpoints are safe to retry.

#### Production example

Order cancel uses DELETE `/orders/{id}`; first call 204, retry after timeout also 204. Metrics do not double-count cancellation. Runbooks should name the status codes, headers, and idempotency behavior operators will see during incidents.

#### Common mistakes

404 on second delete causing client retry loops. DELETE that toggles state. Non-idempotent side effects (email on every DELETE attempt).

#### Interview follow-ups (with model answers)

**Q:** DELETE vs POST cancel?
**A:** For «Idempotent delete.», idempotency is not optional decoration — it is part of the HTTP contract clients rely on when gateways retry or mobile apps replay requests. I store idempotency keys with a unique constraint, return the same response body on replay, and document TTL in OpenAPI. Spring `@RestController` advice maps domain exceptions to RFC 7807 Problem Details with stable `type` URIs. In staging I replay recorded traffic and run openapi-diff on every PR so breaking changes fail CI before partners see them.

**Q:** Soft delete idempotency?
**A:** The follow-on risk for «Soft delete idempotency» is inconsistent behavior across versions — v1 clients still calling deprecated fields while v2 expects structured money objects. I version via URL prefix or vendor media type, add `Sunset` and `Deprecation` headers, and metric traffic by version label. Spring validation groups separate create vs update DTOs; `@ControllerAdvice` ensures 409 on conflict instead of silent overwrites. Operators need runbook steps: which status codes are retryable, which require a new Idempotency-Key, and how BFF translates upstream errors without double-wrapping JSON.

**Q:** Cascade delete semantics?
**A:** Trade-off framing for «Cascade delete semantics»: optimize for integrator stability over internal convenience. Public APIs get cursor pagination, explicit error envelopes, rate-limit headers, and contract tests; internal admin endpoints may use offset pages but still need authz and tracing. I walk one real endpoint through the checklist: safe GET, idempotent PUT/DELETE, POST with keys for money paths, ETag on updates, and OpenAPI examples for 400/404/409/412. If I cannot explain retry semantics to a mobile engineer in two minutes, the design is not ready for production.

#### Scenario probe

**Situation:** After a release, traffic on endpoints touching «Idempotent delete.» shows rising p99 latency and occasional duplicate side effects; mobile clients retry on gateway timeouts and support sees mismatched error JSON across services.

**Model answer:** I treat this as a contract and retry problem first, not a 'scale up pods' problem. I capture `X-Request-Id` across BFF and downstream services, compare Problem Details shapes, and replay a failing call with the same `Idempotency-Key` to see if POST is safe. Context: Order cancel uses DELETE `/orders/{id}`; first call 204, retry after timeout also 204. Metrics do not double-count cancellation. I verify GET safety, idempotent PUT/DELETE behavior, and whether Spring controllers return 409/412 instead of silent overwrites. OpenAPI diff against last release tells me if a field became required without a version bump. Short-term: tighten gateway timeouts with retry only on idempotent methods, fix error envelope in shared `@ControllerAdvice`. Long-term: contract tests, versioned DTOs, metrics on duplicate idempotency hits, and runbook steps for on-call.

---

### 38. Soft delete in REST.

**Short answer:** DELETE sets `deletedAt` or `active=false` instead of removing rows. GET by id returns 404 for deleted resources to external clients. Admins may use `?includeDeleted=true`. Unique constraints apply only to non-deleted rows.

#### What it is

Soft delete preserves data for audit and recovery while behaving like delete in the public API. This sits at the boundary between HTTP transport, Spring MVC dispatch, and client SDK expectations.

#### How it works (internals)

JPA `@SQLDelete` + `@Where(clause = "deleted_at IS NULL")` or explicit service flag. List endpoints exclude deleted by default. Restore via admin `POST /orders/{id}/restore` if product requires.

#### When to use / when NOT to use

Regulated data, audit trails, accidental delete recovery. Pair with retention jobs for hard purge after legal hold. Prefer explicit documentation and gateway policies over tribal knowledge about which endpoints are safe to retry.

#### Production example

Customer DELETE `/users/me` soft-deletes; login fails; support restores within 30 days via admin API. Partial unique index `WHERE deleted_at IS NULL` on email. Runbooks should name the status codes, headers, and idempotency behavior operators will see during incidents.

#### Common mistakes

Leaking soft-deleted records in list APIs. Foreign keys blocking soft delete. DELETE still running hard SQL.

#### Interview follow-ups (with model answers)

**Q:** GDPR right to erasure vs soft delete?
**A:** For «Soft delete in REST.», OpenAPI is not optional decoration — it is part of the HTTP contract clients rely on when gateways retry or mobile apps replay requests. I store idempotency keys with a unique constraint, return the same response body on replay, and document TTL in OpenAPI. Spring `@RestController` advice maps domain exceptions to RFC 7807 Problem Details with stable `type` URIs. In staging I replay recorded traffic and run openapi-diff on every PR so breaking changes fail CI before partners see them.

**Q:** Unique constraint patterns?
**A:** The follow-on risk for «Unique constraint patterns» is inconsistent behavior across versions — v1 clients still calling deprecated fields while v2 expects structured money objects. I version via URL prefix or vendor media type, add `Sunset` and `Deprecation` headers, and metric traffic by version label. Spring validation groups separate create vs update DTOs; `@ControllerAdvice` ensures 409 on conflict instead of silent overwrites. Operators need runbook steps: which status codes are retryable, which require a new Idempotency-Key, and how BFF translates upstream errors without double-wrapping JSON.

**Q:** Expose deletedAt in API?
**A:** Trade-off framing for «Expose deletedAt in API»: optimize for integrator stability over internal convenience. Public APIs get cursor pagination, explicit error envelopes, rate-limit headers, and contract tests; internal admin endpoints may use offset pages but still need authz and tracing. I walk one real endpoint through the checklist: safe GET, idempotent PUT/DELETE, POST with keys for money paths, ETag on updates, and OpenAPI examples for 400/404/409/412. If I cannot explain retry semantics to a mobile engineer in two minutes, the design is not ready for production.

#### Scenario probe

**Situation:** After a release, traffic on endpoints touching «Soft delete in REST.» shows rising p99 latency and occasional duplicate side effects; mobile clients retry on gateway timeouts and support sees mismatched error JSON across services.

**Model answer:** I treat this as a contract and retry problem first, not a 'scale up pods' problem. I capture `X-Request-Id` across BFF and downstream services, compare Problem Details shapes, and replay a failing call with the same `Idempotency-Key` to see if POST is safe. Context: Customer DELETE `/users/me` soft-deletes; login fails; support restores within 30 days via admin API. Partial unique index `WHERE deleted_at IS NULL` on email. I verify GET safety, idempotent PUT/DELETE behavior, and whether Spring controllers return 409/412 instead of silent overwrites. OpenAPI diff against last release tells me if a field became required without a version bump. Short-term: tighten gateway timeouts with retry only on idempotent methods, fix error envelope in shared `@ControllerAdvice`. Long-term: contract tests, versioned DTOs, metrics on duplicate idempotency hits, and runbook steps for on-call.

---

### 39. Multi-tenant APIs.

**Short answer:** Derive tenant from authenticated token (claim or subject)—never trust `tenantId` in the request body without verification. Use subdomain, path prefix, or header only as hints resolved after auth. Every query filters by `tenant_id`. Document the contract in OpenAPI with examples and enforce it in CI with contract tests.

#### What it is

Multi-tenant APIs isolate data per customer organization on shared infrastructure. This sits at the boundary between HTTP transport, Spring MVC dispatch, and client SDK expectations.

#### How it works (internals)

JWT contains `tenant_id`; `TenantContext` filter sets ThreadLocal for repositories. `@PreAuthorize` checks tenant matches resource. Row-level security in Postgres optional second layer.

#### When to use / when NOT to use

SaaS with shared schema or schema-per-tenant. Header `X-Tenant-Id` only after mapping API key → tenant. Prefer explicit documentation and gateway policies over tribal knowledge about which endpoints are safe to retry.

#### Production example

Spring filter sets tenant from JWT claim tid; OrderRepository methods always include tenant predicate. Cross-tenant access returns 404. Runbooks should name the status codes, headers, and idempotency behavior operators will see during incidents.

#### Common mistakes

Client-supplied tenant header without authz. Missing tenant filter in one repository method. Sequential ids enumerable across tenants.

#### Interview follow-ups (with model answers)

**Q:** Schema per tenant vs shared?
**A:** For «Multi-tenant APIs.», Spring controllers is not optional decoration — it is part of the HTTP contract clients rely on when gateways retry or mobile apps replay requests. I store idempotency keys with a unique constraint, return the same response body on replay, and document TTL in OpenAPI. Spring `@RestController` advice maps domain exceptions to RFC 7807 Problem Details with stable `type` URIs. In staging I replay recorded traffic and run openapi-diff on every PR so breaking changes fail CI before partners see them.

**Q:** Tenant in URL path?
**A:** The follow-on risk for «Tenant in URL path» is inconsistent behavior across versions — v1 clients still calling deprecated fields while v2 expects structured money objects. I version via URL prefix or vendor media type, add `Sunset` and `Deprecation` headers, and metric traffic by version label. Spring validation groups separate create vs update DTOs; `@ControllerAdvice` ensures 409 on conflict instead of silent overwrites. Operators need runbook steps: which status codes are retryable, which require a new Idempotency-Key, and how BFF translates upstream errors without double-wrapping JSON.

**Q:** Noisy neighbor rate limits?
**A:** Trade-off framing for «Noisy neighbor rate limits»: optimize for integrator stability over internal convenience. Public APIs get cursor pagination, explicit error envelopes, rate-limit headers, and contract tests; internal admin endpoints may use offset pages but still need authz and tracing. I walk one real endpoint through the checklist: safe GET, idempotent PUT/DELETE, POST with keys for money paths, ETag on updates, and OpenAPI examples for 400/404/409/412. If I cannot explain retry semantics to a mobile engineer in two minutes, the design is not ready for production.

#### Scenario probe

**Situation:** After a release, traffic on endpoints touching «Multi-tenant APIs.» shows rising p99 latency and occasional duplicate side effects; mobile clients retry on gateway timeouts and support sees mismatched error JSON across services.

**Model answer:** I treat this as a contract and retry problem first, not a 'scale up pods' problem. I capture `X-Request-Id` across BFF and downstream services, compare Problem Details shapes, and replay a failing call with the same `Idempotency-Key` to see if POST is safe. Context: Spring filter sets tenant from JWT claim tid; OrderRepository methods always include tenant predicate. Cross-tenant access returns 404. I verify GET safety, idempotent PUT/DELETE behavior, and whether Spring controllers return 409/412 instead of silent overwrites. OpenAPI diff against last release tells me if a field became required without a version bump. Short-term: tighten gateway timeouts with retry only on idempotent methods, fix error envelope in shared `@ControllerAdvice`. Long-term: contract tests, versioned DTOs, metrics on duplicate idempotency hits, and runbook steps for on-call.

#### Code / config (when useful)
```java
@Entity
@FilterDef(name = "tenantFilter", parameters = @ParamDef(name = "tenantId", type = String.class))
@Filter(name = "tenantFilter", condition = "tenant_id = :tenantId")
public class Order { ... }
```

---

### 40. Backward compatibility testing.

**Short answer:** Replay recorded requests from old clients against new server builds. Use consumer-driven contracts (Pact), OpenAPI diff in CI, and fixture JSON from production (sanitized). Do not only test the latest mobile app version. Document the contract in OpenAPI with examples and enforce it in CI with contract tests.

#### What it is

Compatibility testing proves new servers still satisfy old client expectations. This sits at the boundary between HTTP transport, Spring MVC dispatch, and client SDK expectations.

#### How it works (internals)

Golden files: request/response pairs in repo; RestAssured asserts status and JSON subset match. Pact verifies provider satisfies consumer expectations. openapi-diff fails on breaking schema changes. Spring maps requests through `DispatcherServlet`, `HandlerMapping`, and `HttpMessageConverter` chains before your service layer runs.

#### When to use / when NOT to use

Before every public API release. Internal APIs when multiple deployables consume them. Prefer explicit documentation and gateway policies over tribal knowledge about which endpoints are safe to retry.

#### Production example

CI job runs 200 legacy Pact interactions + OpenAPI breaking change gate. Staging canary gets traffic shadow from logged prod requests (PII stripped). Runbooks should name the status codes, headers, and idempotency behavior operators will see during incidents.

#### Common mistakes

Testing only happy path. Removing field without major version. No contract test for error shapes.

#### Interview follow-ups (with model answers)

**Q:** Pact vs OpenAPI diff?
**A:** For «Backward compatibility testing.», versioning is not optional decoration — it is part of the HTTP contract clients rely on when gateways retry or mobile apps replay requests. I store idempotency keys with a unique constraint, return the same response body on replay, and document TTL in OpenAPI. Spring `@RestController` advice maps domain exceptions to RFC 7807 Problem Details with stable `type` URIs. In staging I replay recorded traffic and run openapi-diff on every PR so breaking changes fail CI before partners see them.

**Q:** Record-replay in production?
**A:** The follow-on risk for «Record-replay in production» is inconsistent behavior across versions — v1 clients still calling deprecated fields while v2 expects structured money objects. I version via URL prefix or vendor media type, add `Sunset` and `Deprecation` headers, and metric traffic by version label. Spring validation groups separate create vs update DTOs; `@ControllerAdvice` ensures 409 on conflict instead of silent overwrites. Operators need runbook steps: which status codes are retryable, which require a new Idempotency-Key, and how BFF translates upstream errors without double-wrapping JSON.

**Q:** How to version test fixtures?
**A:** Trade-off framing for «How to version test fixtures»: optimize for integrator stability over internal convenience. Public APIs get cursor pagination, explicit error envelopes, rate-limit headers, and contract tests; internal admin endpoints may use offset pages but still need authz and tracing. I walk one real endpoint through the checklist: safe GET, idempotent PUT/DELETE, POST with keys for money paths, ETag on updates, and OpenAPI examples for 400/404/409/412. If I cannot explain retry semantics to a mobile engineer in two minutes, the design is not ready for production.

#### Scenario probe

**Situation:** After a release, traffic on endpoints touching «Backward compatibility testing.» shows rising p99 latency and occasional duplicate side effects; mobile clients retry on gateway timeouts and support sees mismatched error JSON across services.

**Model answer:** I treat this as a contract and retry problem first, not a 'scale up pods' problem. I capture `X-Request-Id` across BFF and downstream services, compare Problem Details shapes, and replay a failing call with the same `Idempotency-Key` to see if POST is safe. Context: CI job runs 200 legacy Pact interactions + OpenAPI breaking change gate. Staging canary gets traffic shadow from logged prod requests (PII stripped). I verify GET safety, idempotent PUT/DELETE behavior, and whether Spring controllers return 409/412 instead of silent overwrites. OpenAPI diff against last release tells me if a field became required without a version bump. Short-term: tighten gateway timeouts with retry only on idempotent methods, fix error envelope in shared `@ControllerAdvice`. Long-term: contract tests, versioned DTOs, metrics on duplicate idempotency hits, and runbook steps for on-call.

---

### 41. Spring `@RequestBody` vs `InputStream`.

**Short answer:** `@RequestBody` deserializes the entire payload into objects—convenient but memory-bound. For large uploads or streaming JSON lines, use `InputStream` or `HttpInputMessage` and parse incrementally. Set max request size at connector and Spring level. Document the contract in OpenAPI with examples and enforce it in CI with contract tests.

#### What it is

The choice affects memory footprint, latency, and how you validate input. This sits at the boundary between HTTP transport, Spring MVC dispatch, and client SDK expectations.

#### How it works (internals)

`@RequestBody` uses `HttpMessageConverter` (Jackson) loading full byte array. `InputStream` in controller streams to storage or Jackson `JsonParser` token stream. Tomcat `maxSwallowSize` and `server.tomcat.max-http-form-post-size` cap abuse.

#### When to use / when NOT to use

RequestBody for normal REST DTOs under a few MB. InputStream for bulk import, webhook relay, or proxy pass-through. Prefer explicit documentation and gateway policies over tribal knowledge about which endpoints are safe to retry.

#### Production example

NDJSON import endpoint reads `InputStream` line-by-line, batches 500 rows to DB. Standard CRUD keeps `@RequestBody OrderDto`. Runbooks should name the status codes, headers, and idempotency behavior operators will see during incidents.

#### Common mistakes

50MB JSON array via RequestBody on small pods. No size limit at gateway. Parsing twice (stream then bind).

#### Interview follow-ups (with model answers)

**Q:** Reactive WebFlux for streaming?
**A:** For «Spring `@RequestBody` vs `InputStream`.», idempotency is not optional decoration — it is part of the HTTP contract clients rely on when gateways retry or mobile apps replay requests. I store idempotency keys with a unique constraint, return the same response body on replay, and document TTL in OpenAPI. Spring `@RestController` advice maps domain exceptions to RFC 7807 Problem Details with stable `type` URIs. In staging I replay recorded traffic and run openapi-diff on every PR so breaking changes fail CI before partners see them.

**Q:** Multipart vs raw stream?
**A:** The follow-on risk for «Multipart vs raw stream» is inconsistent behavior across versions — v1 clients still calling deprecated fields while v2 expects structured money objects. I version via URL prefix or vendor media type, add `Sunset` and `Deprecation` headers, and metric traffic by version label. Spring validation groups separate create vs update DTOs; `@ControllerAdvice` ensures 409 on conflict instead of silent overwrites. Operators need runbook steps: which status codes are retryable, which require a new Idempotency-Key, and how BFF translates upstream errors without double-wrapping JSON.

**Q:** Validation on streamed JSON?
**A:** Trade-off framing for «Validation on streamed JSON»: optimize for integrator stability over internal convenience. Public APIs get cursor pagination, explicit error envelopes, rate-limit headers, and contract tests; internal admin endpoints may use offset pages but still need authz and tracing. I walk one real endpoint through the checklist: safe GET, idempotent PUT/DELETE, POST with keys for money paths, ETag on updates, and OpenAPI examples for 400/404/409/412. If I cannot explain retry semantics to a mobile engineer in two minutes, the design is not ready for production.

#### Scenario probe

**Situation:** After a release, traffic on endpoints touching «Spring `@RequestBody` vs `InputStream`.» shows rising p99 latency and occasional duplicate side effects; mobile clients retry on gateway timeouts and support sees mismatched error JSON across services.

**Model answer:** I treat this as a contract and retry problem first, not a 'scale up pods' problem. I capture `X-Request-Id` across BFF and downstream services, compare Problem Details shapes, and replay a failing call with the same `Idempotency-Key` to see if POST is safe. Context: NDJSON import endpoint reads `InputStream` line-by-line, batches 500 rows to DB. Standard CRUD keeps `@RequestBody OrderDto`. I verify GET safety, idempotent PUT/DELETE behavior, and whether Spring controllers return 409/412 instead of silent overwrites. OpenAPI diff against last release tells me if a field became required without a version bump. Short-term: tighten gateway timeouts with retry only on idempotent methods, fix error envelope in shared `@ControllerAdvice`. Long-term: contract tests, versioned DTOs, metrics on duplicate idempotency hits, and runbook steps for on-call.

---

### 42. Async MVC / `DeferredResult` / virtual threads.

**Short answer:** Async MVC (`DeferredResult`, `Callable`, `WebAsyncTask`) frees Tomcat threads while waiting on I/O. Virtual threads (Java 21) let you write blocking code cheaply—but still set request timeouts and do not block for unbounded work. Document the contract in OpenAPI with examples and enforce it in CI with contract tests. Pair HTTP semantics with observability: correlation ids, structured Problem Details, and SLO dashboards on p99 latency.

#### What it is

Async models improve scalability when threads wait on external services; virtual threads reduce thread overhead. This sits at the boundary between HTTP transport, Spring MVC dispatch, and client SDK expectations.

#### How it works (internals)

Register `DeferredResult`, call external API on another thread, complete when done. Virtual threads: `spring.threads.virtual.enabled=true`; blocking JDBC may work but pin carriers if native code blocks. Gateway timeout still applies.

#### When to use / when NOT to use

Legacy servlet stack calling slow HTTP clients. Virtual threads for high concurrency blocking style. Prefer message-driven 202 for very long work.

#### Production example

Spring Boot 3.2+ with virtual threads serves 5k concurrent blocking calls to fraud API; `DeferredResult` used for legacy CompletableFuture integration during migration. Runbooks should name the status codes, headers, and idempotency behavior operators will see during incidents.

#### Common mistakes

Async without timeout—leaked requests. Assuming virtual threads remove need for 202 pattern on 10-minute jobs. Blocking on `ForkJoinPool.commonPool()`.

#### Interview follow-ups (with model answers)

**Q:** WebFlux vs virtual threads?
**A:** For «Async MVC / `DeferredResult` / virtual threads.», OpenAPI is not optional decoration — it is part of the HTTP contract clients rely on when gateways retry or mobile apps replay requests. I store idempotency keys with a unique constraint, return the same response body on replay, and document TTL in OpenAPI. Spring `@RestController` advice maps domain exceptions to RFC 7807 Problem Details with stable `type` URIs. In staging I replay recorded traffic and run openapi-diff on every PR so breaking changes fail CI before partners see them.

**Q:** ThreadLocal with virtual threads?
**A:** The follow-on risk for «ThreadLocal with virtual threads» is inconsistent behavior across versions — v1 clients still calling deprecated fields while v2 expects structured money objects. I version via URL prefix or vendor media type, add `Sunset` and `Deprecation` headers, and metric traffic by version label. Spring validation groups separate create vs update DTOs; `@ControllerAdvice` ensures 409 on conflict instead of silent overwrites. Operators need runbook steps: which status codes are retryable, which require a new Idempotency-Key, and how BFF translates upstream errors without double-wrapping JSON.

**Q:** How to set async timeout?
**A:** Trade-off framing for «How to set async timeout»: optimize for integrator stability over internal convenience. Public APIs get cursor pagination, explicit error envelopes, rate-limit headers, and contract tests; internal admin endpoints may use offset pages but still need authz and tracing. I walk one real endpoint through the checklist: safe GET, idempotent PUT/DELETE, POST with keys for money paths, ETag on updates, and OpenAPI examples for 400/404/409/412. If I cannot explain retry semantics to a mobile engineer in two minutes, the design is not ready for production.

#### Scenario probe

**Situation:** After a release, traffic on endpoints touching «Async MVC / `DeferredResult` / virtual threads.» shows rising p99 latency and occasional duplicate side effects; mobile clients retry on gateway timeouts and support sees mismatched error JSON across services.

**Model answer:** I treat this as a contract and retry problem first, not a 'scale up pods' problem. I capture `X-Request-Id` across BFF and downstream services, compare Problem Details shapes, and replay a failing call with the same `Idempotency-Key` to see if POST is safe. Context: Spring Boot 3.2+ with virtual threads serves 5k concurrent blocking calls to fraud API; `DeferredResult` used for legacy CompletableFuture integration during migration. I verify GET safety, idempotent PUT/DELETE behavior, and whether Spring controllers return 409/412 instead of silent overwrites. OpenAPI diff against last release tells me if a field became required without a version bump. Short-term: tighten gateway timeouts with retry only on idempotent methods, fix error envelope in shared `@ControllerAdvice`. Long-term: contract tests, versioned DTOs, metrics on duplicate idempotency hits, and runbook steps for on-call.

---

### 43. API keys vs JWT vs session.

**Short answer:** API keys identify machine clients—store hashed, rotate, scope per tenant. JWTs are stateless bearer tokens with short TTL; revocation needs denylist or refresh rotation. Sessions are server-side state ideal for browser BFF with CSRF protection. Document the contract in OpenAPI with examples and enforce it in CI with contract tests.

#### What it is

Authentication mechanisms trade off simplicity, revocation, and client type (machine vs human). This sits at the boundary between HTTP transport, Spring MVC dispatch, and client SDK expectations.

#### How it works (internals)

API key in header `X-Api-Key` mapped to tenant in DB (hash compare). JWT signed RS256, validated per request; refresh token in HttpOnly cookie. Session ID in cookie, Redis session store, Spring Session.

#### When to use / when NOT to use

API keys for partners and scripts. JWT for microservice and mobile. Session cookie for same-site React BFF.

#### Production example

Public API: API key + rate limit. Mobile: OAuth2 JWT access token 15min. Web: BFF session cookie, BFF calls backend with service JWT.

#### Common mistakes

Long-lived JWT without rotation. API keys in query strings (logged). Session without CSRF on cookie APIs.

#### Interview follow-ups (with model answers)

**Q:** OAuth2 opaque vs JWT?
**A:** For «API keys vs JWT vs session.», Spring controllers is not optional decoration — it is part of the HTTP contract clients rely on when gateways retry or mobile apps replay requests. I store idempotency keys with a unique constraint, return the same response body on replay, and document TTL in OpenAPI. Spring `@RestController` advice maps domain exceptions to RFC 7807 Problem Details with stable `type` URIs. In staging I replay recorded traffic and run openapi-diff on every PR so breaking changes fail CI before partners see them.

**Q:** mTLS plus API key?
**A:** The follow-on risk for «mTLS plus API key» is inconsistent behavior across versions — v1 clients still calling deprecated fields while v2 expects structured money objects. I version via URL prefix or vendor media type, add `Sunset` and `Deprecation` headers, and metric traffic by version label. Spring validation groups separate create vs update DTOs; `@ControllerAdvice` ensures 409 on conflict instead of silent overwrites. Operators need runbook steps: which status codes are retryable, which require a new Idempotency-Key, and how BFF translates upstream errors without double-wrapping JSON.

**Q:** How to revoke JWT instantly?
**A:** Trade-off framing for «How to revoke JWT instantly»: optimize for integrator stability over internal convenience. Public APIs get cursor pagination, explicit error envelopes, rate-limit headers, and contract tests; internal admin endpoints may use offset pages but still need authz and tracing. I walk one real endpoint through the checklist: safe GET, idempotent PUT/DELETE, POST with keys for money paths, ETag on updates, and OpenAPI examples for 400/404/409/412. If I cannot explain retry semantics to a mobile engineer in two minutes, the design is not ready for production.

#### Scenario probe

**Situation:** After a release, traffic on endpoints touching «API keys vs JWT vs session.» shows rising p99 latency and occasional duplicate side effects; mobile clients retry on gateway timeouts and support sees mismatched error JSON across services.

**Model answer:** I treat this as a contract and retry problem first, not a 'scale up pods' problem. I capture `X-Request-Id` across BFF and downstream services, compare Problem Details shapes, and replay a failing call with the same `Idempotency-Key` to see if POST is safe. Context: Public API: API key + rate limit. Mobile: OAuth2 JWT access token 15min. Web: BFF session cookie, BFF calls backend with service JWT. I verify GET safety, idempotent PUT/DELETE behavior, and whether Spring controllers return 409/412 instead of silent overwrites. OpenAPI diff against last release tells me if a field became required without a version bump. Short-term: tighten gateway timeouts with retry only on idempotent methods, fix error envelope in shared `@ControllerAdvice`. Long-term: contract tests, versioned DTOs, metrics on duplicate idempotency hits, and runbook steps for on-call.

---

### 44. Over-fetching and under-fetching.

**Short answer:** Over-fetching returns huge object graphs (order + 50 line items + customer history) for a list screen. Under-fetching causes N+1 client calls. Fix with summary DTOs, sparse fieldsets, dedicated list endpoints, or BFF aggregation—not lazy-loading accidents over JSON. Document the contract in OpenAPI with examples and enforce it in CI with contract tests.

#### What it is

Fetch tuning balances payload size, round trips, and server query efficiency. This sits at the boundary between HTTP transport, Spring MVC dispatch, and client SDK expectations.

#### How it works (internals)

List endpoint returns `OrderSummaryDto` only. `?fields=` projection or GraphQL. Hibernate: `@EntityGraph` or DTO query—never rely on `OpenEntityManagerInView` to silently load relations in JSON serializer.

#### When to use / when NOT to use

Design list vs detail resources explicitly. Mobile on poor networks needs small payloads. Prefer explicit documentation and gateway policies over tribal knowledge about which endpoints are safe to retry.

#### Production example

`GET /orders` returns id, status, total, createdAt. `GET /orders/{id}` returns full detail. BFF composes dashboard in one call from three summary endpoints.

#### Common mistakes

Returning JPA entity with lazy collections → 4MB JSON or LazyInitializationException. Chatty mobile app with 20 sequential GETs. Teams often discover these failures only after mobile clients retry on flaky networks or CDNs cache a non-safe GET.

#### Interview follow-ups (with model answers)

**Q:** N+1 in Hibernate logs?
**A:** For «Over-fetching and under-fetching.», versioning is not optional decoration — it is part of the HTTP contract clients rely on when gateways retry or mobile apps replay requests. I store idempotency keys with a unique constraint, return the same response body on replay, and document TTL in OpenAPI. Spring `@RestController` advice maps domain exceptions to RFC 7807 Problem Details with stable `type` URIs. In staging I replay recorded traffic and run openapi-diff on every PR so breaking changes fail CI before partners see them.

**Q:** BFF vs expand param?
**A:** The follow-on risk for «BFF vs expand param» is inconsistent behavior across versions — v1 clients still calling deprecated fields while v2 expects structured money objects. I version via URL prefix or vendor media type, add `Sunset` and `Deprecation` headers, and metric traffic by version label. Spring validation groups separate create vs update DTOs; `@ControllerAdvice` ensures 409 on conflict instead of silent overwrites. Operators need runbook steps: which status codes are retryable, which require a new Idempotency-Key, and how BFF translates upstream errors without double-wrapping JSON.

**Q:** GraphQL DataLoader?
**A:** Trade-off framing for «GraphQL DataLoader»: optimize for integrator stability over internal convenience. Public APIs get cursor pagination, explicit error envelopes, rate-limit headers, and contract tests; internal admin endpoints may use offset pages but still need authz and tracing. I walk one real endpoint through the checklist: safe GET, idempotent PUT/DELETE, POST with keys for money paths, ETag on updates, and OpenAPI examples for 400/404/409/412. If I cannot explain retry semantics to a mobile engineer in two minutes, the design is not ready for production.

#### Scenario probe

**Situation:** After a release, traffic on endpoints touching «Over-fetching and under-fetching.» shows rising p99 latency and occasional duplicate side effects; mobile clients retry on gateway timeouts and support sees mismatched error JSON across services.

**Model answer:** I treat this as a contract and retry problem first, not a 'scale up pods' problem. I capture `X-Request-Id` across BFF and downstream services, compare Problem Details shapes, and replay a failing call with the same `Idempotency-Key` to see if POST is safe. Context: `GET /orders` returns id, status, total, createdAt. `GET /orders/{id}` returns full detail. BFF composes dashboard in one call from three summary endpoints. I verify GET safety, idempotent PUT/DELETE behavior, and whether Spring controllers return 409/412 instead of silent overwrites. OpenAPI diff against last release tells me if a field became required without a version bump. Short-term: tighten gateway timeouts with retry only on idempotent methods, fix error envelope in shared `@ControllerAdvice`. Long-term: contract tests, versioned DTOs, metrics on duplicate idempotency hits, and runbook steps for on-call.

---

### 45. Redirects 301/302/307/308.

**Short answer:** 301/302 historically caused clients to rewrite POST to GET on redirect. 307 and 308 preserve the original method and body. APIs rarely redirect POST; use 301/308 for permanent URL moves on GET resources. Document the contract in OpenAPI with examples and enforce it in CI with contract tests. Pair HTTP semantics with observability: correlation ids, structured Problem Details, and SLO dashboards on p99 latency.

#### What it is

Redirects tell clients to retry at another URL; method preservation matters for non-GET verbs. This sits at the boundary between HTTP transport, Spring MVC dispatch, and client SDK expectations.

#### How it works (internals)

301 Moved Permanently, 302 Found (temporary, method may change in practice), 307 Temporary Redirect (method preserved), 308 Permanent Redirect (method preserved). Spring `RedirectView` or `ResponseEntity.status(308).location(uri)`. Spring maps requests through `DispatcherServlet`, `HandlerMapping`, and `HttpMessageConverter` chains before your service layer runs.

#### When to use / when NOT to use

301/308 when deprecating `/v1/orders` path to `/v2/orders` for GET. Avoid redirects in API error flows—use Problem Details. Prefer explicit documentation and gateway policies over tribal knowledge about which endpoints are safe to retry.

#### Production example

Documentation URL redirect 308 to new path. API version migration uses gateway routing, not 302 on POST bodies. Runbooks should name the status codes, headers, and idempotency behavior operators will see during incidents.

#### Common mistakes

302 after POST losing body. Infinite redirect loops. Redirect without HTTPS upgrade discipline.

#### Interview follow-ups (with model answers)

**Q:** SEO vs API redirects?
**A:** For «Redirects 301/302/307/308.», idempotency is not optional decoration — it is part of the HTTP contract clients rely on when gateways retry or mobile apps replay requests. I store idempotency keys with a unique constraint, return the same response body on replay, and document TTL in OpenAPI. Spring `@RestController` advice maps domain exceptions to RFC 7807 Problem Details with stable `type` URIs. In staging I replay recorded traffic and run openapi-diff on every PR so breaking changes fail CI before partners see them.

**Q:** Gateway vs app redirect?
**A:** The follow-on risk for «Gateway vs app redirect» is inconsistent behavior across versions — v1 clients still calling deprecated fields while v2 expects structured money objects. I version via URL prefix or vendor media type, add `Sunset` and `Deprecation` headers, and metric traffic by version label. Spring validation groups separate create vs update DTOs; `@ControllerAdvice` ensures 409 on conflict instead of silent overwrites. Operators need runbook steps: which status codes are retryable, which require a new Idempotency-Key, and how BFF translates upstream errors without double-wrapping JSON.

**Q:** How browsers differ on 307?
**A:** Trade-off framing for «How browsers differ on 307»: optimize for integrator stability over internal convenience. Public APIs get cursor pagination, explicit error envelopes, rate-limit headers, and contract tests; internal admin endpoints may use offset pages but still need authz and tracing. I walk one real endpoint through the checklist: safe GET, idempotent PUT/DELETE, POST with keys for money paths, ETag on updates, and OpenAPI examples for 400/404/409/412. If I cannot explain retry semantics to a mobile engineer in two minutes, the design is not ready for production.

#### Scenario probe

**Situation:** After a release, traffic on endpoints touching «Redirects 301/302/307/308.» shows rising p99 latency and occasional duplicate side effects; mobile clients retry on gateway timeouts and support sees mismatched error JSON across services.

**Model answer:** I treat this as a contract and retry problem first, not a 'scale up pods' problem. I capture `X-Request-Id` across BFF and downstream services, compare Problem Details shapes, and replay a failing call with the same `Idempotency-Key` to see if POST is safe. Context: Documentation URL redirect 308 to new path. API version migration uses gateway routing, not 302 on POST bodies. I verify GET safety, idempotent PUT/DELETE behavior, and whether Spring controllers return 409/412 instead of silent overwrites. OpenAPI diff against last release tells me if a field became required without a version bump. Short-term: tighten gateway timeouts with retry only on idempotent methods, fix error envelope in shared `@ControllerAdvice`. Long-term: contract tests, versioned DTOs, metrics on duplicate idempotency hits, and runbook steps for on-call.

---

### 46. Health vs readiness vs "deep health".

**Short answer:** Liveness (`/actuator/health/liveness`)—is the process alive? Restart if not. Readiness—can it serve traffic (DB connected)? Deep health checks dependencies but belongs on admin endpoints, not liveness—flapping deps cause cascade pod kills.

#### What it is

Kubernetes and load balancers probe different health dimensions; conflating them causes outages. This sits at the boundary between HTTP transport, Spring MVC dispatch, and client SDK expectations.

#### How it works (internals)

Spring Boot Actuator health groups: liveness minimal (heap OK), readiness includes DataSource ping. Deep check: Kafka, remote HTTP—expose `/actuator/health` detail only internally or with auth. Spring maps requests through `DispatcherServlet`, `HandlerMapping`, and `HttpMessageConverter` chains before your service layer runs.

#### When to use / when NOT to use

Liveness: JVM up. Readiness: remove from LB when DB down. Deep: status page and ops dashboards—not liveness probe.

#### Production example

K8s liveness hits `/actuator/health/liveness`; readiness checks DB. Public status page uses cached synthetic check, not raw actuator with stack info. Runbooks should name the status codes, headers, and idempotency behavior operators will see during incidents.

#### Common mistakes

Kafka check on liveness → restart storm. Public `/health` exposing env details. Readiness always UP while returning 500 on real requests.

#### Interview follow-ups (with model answers)

**Q:** Startup probe?
**A:** For «Health vs readiness vs "deep health".», OpenAPI is not optional decoration — it is part of the HTTP contract clients rely on when gateways retry or mobile apps replay requests. I store idempotency keys with a unique constraint, return the same response body on replay, and document TTL in OpenAPI. Spring `@RestController` advice maps domain exceptions to RFC 7807 Problem Details with stable `type` URIs. In staging I replay recorded traffic and run openapi-diff on every PR so breaking changes fail CI before partners see them.

**Q:** Actuator security?
**A:** The follow-on risk for «Actuator security» is inconsistent behavior across versions — v1 clients still calling deprecated fields while v2 expects structured money objects. I version via URL prefix or vendor media type, add `Sunset` and `Deprecation` headers, and metric traffic by version label. Spring validation groups separate create vs update DTOs; `@ControllerAdvice` ensures 409 on conflict instead of silent overwrites. Operators need runbook steps: which status codes are retryable, which require a new Idempotency-Key, and how BFF translates upstream errors without double-wrapping JSON.

**Q:** Synthetic vs component health?
**A:** Trade-off framing for «Synthetic vs component health»: optimize for integrator stability over internal convenience. Public APIs get cursor pagination, explicit error envelopes, rate-limit headers, and contract tests; internal admin endpoints may use offset pages but still need authz and tracing. I walk one real endpoint through the checklist: safe GET, idempotent PUT/DELETE, POST with keys for money paths, ETag on updates, and OpenAPI examples for 400/404/409/412. If I cannot explain retry semantics to a mobile engineer in two minutes, the design is not ready for production.

#### Scenario probe

**Situation:** After a release, traffic on endpoints touching «Health vs readiness vs "deep health".» shows rising p99 latency and occasional duplicate side effects; mobile clients retry on gateway timeouts and support sees mismatched error JSON across services.

**Model answer:** I treat this as a contract and retry problem first, not a 'scale up pods' problem. I capture `X-Request-Id` across BFF and downstream services, compare Problem Details shapes, and replay a failing call with the same `Idempotency-Key` to see if POST is safe. Context: K8s liveness hits `/actuator/health/liveness`; readiness checks DB. Public status page uses cached synthetic check, not raw actuator with stack info. I verify GET safety, idempotent PUT/DELETE behavior, and whether Spring controllers return 409/412 instead of silent overwrites. OpenAPI diff against last release tells me if a field became required without a version bump. Short-term: tighten gateway timeouts with retry only on idempotent methods, fix error envelope in shared `@ControllerAdvice`. Long-term: contract tests, versioned DTOs, metrics on duplicate idempotency hits, and runbook steps for on-call.

---

### 47. Changelog and deprecation.

**Short answer:** Document every change in a public changelog. Signal deprecation with `Deprecation: true` and `Sunset` HTTP headers plus OpenAPI `deprecated: true`. Monitor old version usage, email integrators, then disable with lead time. Document the contract in OpenAPI with examples and enforce it in CI with contract tests.

#### What it is

Deprecation is the controlled process of retiring API surface without surprise breakage. This sits at the boundary between HTTP transport, Spring MVC dispatch, and client SDK expectations.

#### How it works (internals)

RFC 8594 Sunset header gives end date. Metrics label traffic by API version. Feature flags gate removal. Spring interceptor adds headers on v1 controllers.

#### When to use / when NOT to use

Any breaking or behavior-changing release on public APIs. Internal APIs still deserve changelog for sibling teams. Prefer explicit documentation and gateway policies over tribal knowledge about which endpoints are safe to retry.

#### Production example

v1 sunset announced 6 months ahead; dashboard shows 2% traffic remaining; final week 429 with migration link; then 410 Gone. Runbooks should name the status codes, headers, and idempotency behavior operators will see during incidents.

#### Common mistakes

Silent breaking change. Deprecation header without docs. No metric on who still calls old fields.

#### Interview follow-ups (with model answers)

**Q:** 410 Gone vs 404?
**A:** For «Changelog and deprecation.», Spring controllers is not optional decoration — it is part of the HTTP contract clients rely on when gateways retry or mobile apps replay requests. I store idempotency keys with a unique constraint, return the same response body on replay, and document TTL in OpenAPI. Spring `@RestController` advice maps domain exceptions to RFC 7807 Problem Details with stable `type` URIs. In staging I replay recorded traffic and run openapi-diff on every PR so breaking changes fail CI before partners see them.

**Q:** Email vs header notification?
**A:** The follow-on risk for «Email vs header notification» is inconsistent behavior across versions — v1 clients still calling deprecated fields while v2 expects structured money objects. I version via URL prefix or vendor media type, add `Sunset` and `Deprecation` headers, and metric traffic by version label. Spring validation groups separate create vs update DTOs; `@ControllerAdvice` ensures 409 on conflict instead of silent overwrites. Operators need runbook steps: which status codes are retryable, which require a new Idempotency-Key, and how BFF translates upstream errors without double-wrapping JSON.

**Q:** OpenAPI deprecated fields?
**A:** Trade-off framing for «OpenAPI deprecated fields»: optimize for integrator stability over internal convenience. Public APIs get cursor pagination, explicit error envelopes, rate-limit headers, and contract tests; internal admin endpoints may use offset pages but still need authz and tracing. I walk one real endpoint through the checklist: safe GET, idempotent PUT/DELETE, POST with keys for money paths, ETag on updates, and OpenAPI examples for 400/404/409/412. If I cannot explain retry semantics to a mobile engineer in two minutes, the design is not ready for production.

#### Scenario probe

**Situation:** After a release, traffic on endpoints touching «Changelog and deprecation.» shows rising p99 latency and occasional duplicate side effects; mobile clients retry on gateway timeouts and support sees mismatched error JSON across services.

**Model answer:** I treat this as a contract and retry problem first, not a 'scale up pods' problem. I capture `X-Request-Id` across BFF and downstream services, compare Problem Details shapes, and replay a failing call with the same `Idempotency-Key` to see if POST is safe. Context: v1 sunset announced 6 months ahead; dashboard shows 2% traffic remaining; final week 429 with migration link; then 410 Gone. I verify GET safety, idempotent PUT/DELETE behavior, and whether Spring controllers return 409/412 instead of silent overwrites. OpenAPI diff against last release tells me if a field became required without a version bump. Short-term: tighten gateway timeouts with retry only on idempotent methods, fix error envelope in shared `@ControllerAdvice`. Long-term: contract tests, versioned DTOs, metrics on duplicate idempotency hits, and runbook steps for on-call.

---

### 48. Testing REST.

**Short answer:** Layer tests: `@WebMvcTest` for mapping and serialization; `@SpringBootTest` + MockMvc or RestAssured for integration; contract tests for consumers; load tests for p99 latency and error rate under dependency failure. Document the contract in OpenAPI with examples and enforce it in CI with contract tests. Pair HTTP semantics with observability: correlation ids, structured Problem Details, and SLO dashboards on p99 latency. The senior trade-off is client ergonomics versus operability — retries, caching, and evolution must be designed together.

#### What it is

REST testing validates HTTP contract, not just service unit logic. This sits at the boundary between HTTP transport, Spring MVC dispatch, and client SDK expectations.

#### How it works (internals)

MockMvc `perform(get(...)).andExpect(status().isOk())`. Testcontainers for real DB. WireMock for downstream 503 chaos. RestAssured for fluent API assertions. Security tests with `@WithMockUser` and negative cases.

#### When to use / when NOT to use

WebMvcTest per controller; few full-stack tests for critical paths; contract in CI for providers. Prefer explicit documentation and gateway policies over tribal knowledge about which endpoints are safe to retry.

#### Production example

PR runs WebMvcTest + Testcontainers integration + Pact verify. Weekly k6 load test on checkout path; alert if p99 > 500ms or 5xx > 0.1%. Runbooks should name the status codes, headers, and idempotency behavior operators will see during incidents.

#### Common mistakes

Only mocking service layer—wrong status code mapping ships. No test for Problem Detail shape. Flaky tests with real clock.

#### Interview follow-ups (with model answers)

**Q:** Testcontainers vs H2?
**A:** For «Testing REST.», versioning is not optional decoration — it is part of the HTTP contract clients rely on when gateways retry or mobile apps replay requests. I store idempotency keys with a unique constraint, return the same response body on replay, and document TTL in OpenAPI. Spring `@RestController` advice maps domain exceptions to RFC 7807 Problem Details with stable `type` URIs. In staging I replay recorded traffic and run openapi-diff on every PR so breaking changes fail CI before partners see them.

**Q:** Testing security rules?
**A:** The follow-on risk for «Testing security rules» is inconsistent behavior across versions — v1 clients still calling deprecated fields while v2 expects structured money objects. I version via URL prefix or vendor media type, add `Sunset` and `Deprecation` headers, and metric traffic by version label. Spring validation groups separate create vs update DTOs; `@ControllerAdvice` ensures 409 on conflict instead of silent overwrites. Operators need runbook steps: which status codes are retryable, which require a new Idempotency-Key, and how BFF translates upstream errors without double-wrapping JSON.

**Q:** Snapshot testing JSON?
**A:** Trade-off framing for «Snapshot testing JSON»: optimize for integrator stability over internal convenience. Public APIs get cursor pagination, explicit error envelopes, rate-limit headers, and contract tests; internal admin endpoints may use offset pages but still need authz and tracing. I walk one real endpoint through the checklist: safe GET, idempotent PUT/DELETE, POST with keys for money paths, ETag on updates, and OpenAPI examples for 400/404/409/412. If I cannot explain retry semantics to a mobile engineer in two minutes, the design is not ready for production.

#### Scenario probe

**Situation:** After a release, traffic on endpoints touching «Testing REST.» shows rising p99 latency and occasional duplicate side effects; mobile clients retry on gateway timeouts and support sees mismatched error JSON across services.

**Model answer:** I treat this as a contract and retry problem first, not a 'scale up pods' problem. I capture `X-Request-Id` across BFF and downstream services, compare Problem Details shapes, and replay a failing call with the same `Idempotency-Key` to see if POST is safe. Context: PR runs WebMvcTest + Testcontainers integration + Pact verify. Weekly k6 load test on checkout path; alert if p99 > 500ms or 5xx > 0.1%. I verify GET safety, idempotent PUT/DELETE behavior, and whether Spring controllers return 409/412 instead of silent overwrites. OpenAPI diff against last release tells me if a field became required without a version bump. Short-term: tighten gateway timeouts with retry only on idempotent methods, fix error envelope in shared `@ControllerAdvice`. Long-term: contract tests, versioned DTOs, metrics on duplicate idempotency hits, and runbook steps for on-call.

#### Code / config (when useful)
```java
@WebMvcTest(OrderController.class)
class OrderControllerTest {
  @Test void getOrder() throws Exception {
    mockMvc.perform(get("/orders/{id}", id))
        .andExpect(status().isOk())
        .andExpect(jsonPath("$.status").value("OPEN"));
  }
}
```

---

### 49. Public API vs internal.

**Short answer:** Public APIs promise stability, versioning, rate limits, abuse protection, and thorough docs. Internal APIs can move faster with coordinated deploys—but still need authz, observability, and contract tests. Never treat 'internal' as 'no security'. Document the contract in OpenAPI with examples and enforce it in CI with contract tests.

#### What it is

The audience determines change velocity, hardening, and operational rigor. This sits at the boundary between HTTP transport, Spring MVC dispatch, and client SDK expectations.

#### How it works (internals)

Public: API gateway, WAF, API keys, SLA, changelog. Internal: mTLS mesh, service JWT, simpler pagination. Same Problem Details and tracing headers across both.

#### When to use / when NOT to use

Split gateways or path prefixes (`api.example.com` vs `internal`). Internal admin tools still need BOLA checks. Prefer explicit documentation and gateway policies over tribal knowledge about which endpoints are safe to retry.

#### Production example

Public partner API on Apigee with quota. Internal `order-service` gRPC only in mesh; BFF is the sole REST exposure to React. Runbooks should name the status codes, headers, and idempotency behavior operators will see during incidents.

#### Common mistakes

Exposing internal actuator publicly. Internal API with no auth because 'VPN'. Different error formats per service.

#### Interview follow-ups (with model answers)

**Q:** Zero trust internal?
**A:** For «Public API vs internal.», idempotency is not optional decoration — it is part of the HTTP contract clients rely on when gateways retry or mobile apps replay requests. I store idempotency keys with a unique constraint, return the same response body on replay, and document TTL in OpenAPI. Spring `@RestController` advice maps domain exceptions to RFC 7807 Problem Details with stable `type` URIs. In staging I replay recorded traffic and run openapi-diff on every PR so breaking changes fail CI before partners see them.

**Q:** When to publish internal API?
**A:** The follow-on risk for «When to publish internal API» is inconsistent behavior across versions — v1 clients still calling deprecated fields while v2 expects structured money objects. I version via URL prefix or vendor media type, add `Sunset` and `Deprecation` headers, and metric traffic by version label. Spring validation groups separate create vs update DTOs; `@ControllerAdvice` ensures 409 on conflict instead of silent overwrites. Operators need runbook steps: which status codes are retryable, which require a new Idempotency-Key, and how BFF translates upstream errors without double-wrapping JSON.

**Q:** BFF as security boundary?
**A:** Trade-off framing for «BFF as security boundary»: optimize for integrator stability over internal convenience. Public APIs get cursor pagination, explicit error envelopes, rate-limit headers, and contract tests; internal admin endpoints may use offset pages but still need authz and tracing. I walk one real endpoint through the checklist: safe GET, idempotent PUT/DELETE, POST with keys for money paths, ETag on updates, and OpenAPI examples for 400/404/409/412. If I cannot explain retry semantics to a mobile engineer in two minutes, the design is not ready for production.

#### Scenario probe

**Situation:** After a release, traffic on endpoints touching «Public API vs internal.» shows rising p99 latency and occasional duplicate side effects; mobile clients retry on gateway timeouts and support sees mismatched error JSON across services.

**Model answer:** I treat this as a contract and retry problem first, not a 'scale up pods' problem. I capture `X-Request-Id` across BFF and downstream services, compare Problem Details shapes, and replay a failing call with the same `Idempotency-Key` to see if POST is safe. Context: Public partner API on Apigee with quota. Internal `order-service` gRPC only in mesh; BFF is the sole REST exposure to React. I verify GET safety, idempotent PUT/DELETE behavior, and whether Spring controllers return 409/412 instead of silent overwrites. OpenAPI diff against last release tells me if a field became required without a version bump. Short-term: tighten gateway timeouts with retry only on idempotent methods, fix error envelope in shared `@ControllerAdvice`. Long-term: contract tests, versioned DTOs, metrics on duplicate idempotency hits, and runbook steps for on-call.

---

### 50. Senior REST design review checklist.

**Short answer:** Review resource naming, HTTP semantics, status codes, idempotency, pagination, error envelope, per-object authz, versioning, OpenAPI with examples, p99 budget, payload size limits, tracing headers, and rate limits. Walk one API you designed through the list—that is the interview exercise. Document the contract in OpenAPI with examples and enforce it in CI with contract tests. Pair HTTP semantics with observability: correlation ids, structured Problem Details, and SLO dashboards on p99 latency.

#### What it is

A design review checklist catches contract and operability issues before production. This sits at the boundary between HTTP transport, Spring MVC dispatch, and client SDK expectations.

#### How it works (internals)

Walk through happy path, error paths, retry behavior, and evolution story. Load-test list endpoints. Security: BOLA tests, mass assignment, injection. Ops: health probes, metrics, SLOs.

#### When to use / when NOT to use

Before any public launch, major version, or security-sensitive feature (payments, PII). Prefer explicit documentation and gateway policies over tribal knowledge about which endpoints are safe to retry.

#### Production example

Design doc links OpenAPI PR; reviewer signs off on idempotency for POST /payments, cursor pagination, Problem Details, 409 on conflict, ETag on updates, 50ms p99 budget for GET list. Runbooks should name the status codes, headers, and idempotency behavior operators will see during incidents.

#### Common mistakes

Checklist as checkbox theater without examples. Skipping authz review. No performance budget for list endpoints.

#### Interview follow-ups (with model answers)

**Q:** Walk me through an API you designed.?
**A:** For «Senior REST design review checklist.», OpenAPI is not optional decoration — it is part of the HTTP contract clients rely on when gateways retry or mobile apps replay requests. I store idempotency keys with a unique constraint, return the same response body on replay, and document TTL in OpenAPI. Spring `@RestController` advice maps domain exceptions to RFC 7807 Problem Details with stable `type` URIs. In staging I replay recorded traffic and run openapi-diff on every PR so breaking changes fail CI before partners see them.

**Q:** What would you change in our current API?
**A:** The follow-on risk for «What would you change in our current API» is inconsistent behavior across versions — v1 clients still calling deprecated fields while v2 expects structured money objects. I version via URL prefix or vendor media type, add `Sunset` and `Deprecation` headers, and metric traffic by version label. Spring validation groups separate create vs update DTOs; `@ControllerAdvice` ensures 409 on conflict instead of silent overwrites. Operators need runbook steps: which status codes are retryable, which require a new Idempotency-Key, and how BFF translates upstream errors without double-wrapping JSON.

**Q:** How do you prioritize checklist items under deadline?
**A:** Trade-off framing for «How do you prioritize checklist items under deadline»: optimize for integrator stability over internal convenience. Public APIs get cursor pagination, explicit error envelopes, rate-limit headers, and contract tests; internal admin endpoints may use offset pages but still need authz and tracing. I walk one real endpoint through the checklist: safe GET, idempotent PUT/DELETE, POST with keys for money paths, ETag on updates, and OpenAPI examples for 400/404/409/412. If I cannot explain retry semantics to a mobile engineer in two minutes, the design is not ready for production.

#### Scenario probe

**Situation:** After a release, traffic on endpoints touching «Senior REST design review checklist.» shows rising p99 latency and occasional duplicate side effects; mobile clients retry on gateway timeouts and support sees mismatched error JSON across services.

**Model answer:** I treat this as a contract and retry problem first, not a 'scale up pods' problem. I capture `X-Request-Id` across BFF and downstream services, compare Problem Details shapes, and replay a failing call with the same `Idempotency-Key` to see if POST is safe. Context: Design doc links OpenAPI PR; reviewer signs off on idempotency for POST /payments, cursor pagination, Problem Details, 409 on conflict, ETag on updates, 50ms p99 budget for GET list. I verify GET safety, idempotent PUT/DELETE behavior, and whether Spring controllers return 409/412 instead of silent overwrites. OpenAPI diff against last release tells me if a field became required without a version bump. Short-term: tighten gateway timeouts with retry only on idempotent methods, fix error envelope in shared `@ControllerAdvice`. Long-term: contract tests, versioned DTOs, metrics on duplicate idempotency hits, and runbook steps for on-call.

---

## Deep-dive additions (Q51–Q55)

API style decisions, hypermedia, webhooks, monetization, and enterprise payload standards.

---

### 51. gRPC vs REST vs GraphQL — decision framework for Java teams

**Short answer:** **REST** (HTTP/JSON) wins for public APIs, browser clients, and broad tooling. **gRPC** (HTTP/2, Protobuf) wins for low-latency internal service-to-service on JVM with strong typing and streaming. **GraphQL** wins when many clients need different field subsets from one graph — with discipline (DataLoader, complexity limits). Default Java microservices: REST or gRPC internal + REST at edge; add GraphQL BFF only when mobile/web field explosion justifies ops cost. Trade-off: gRPC/GraphQL need gateways and codegen; REST is verbose but universal.

#### What it is
REST maps resources to URLs with standard verbs; Spring MVC / WebFlux is the default Java stack. gRPC uses `.proto` contracts, `grpc-spring-boot-starter`, stub clients — no JSON overhead, bidirectional streams. GraphQL exposes one endpoint; clients query shape — resolvers call backend REST/gRPC. Decision sits at **integration boundary**: who consumes, latency budget, schema evolution, and team skill.

#### How it works (internals)
gRPC: Netty transport, Protobuf serialization, HTTP/2 multiplexing, deadline propagation via `Context`. REST: Jackson JSON, OpenAPI for docs, HTTP caching with ETags. GraphQL: schema stitching, N+1 risk without DataLoader batching, query depth/complexity limits to prevent DoS. Spring Boot 3 supports virtual threads — gRPC blocking stubs less painful; still prefer async for high fan-out.

#### When to use / when NOT to use
| Choose | When |
|--------|------|
| REST | Public API, third parties, CDN cacheable GET, simple CRUD |
| gRPC | Internal Java/Go services, streaming, <10ms p99, large payloads |
| GraphQL | Mobile BFF with variable fields; not for money-path orchestration |

Avoid gRPC to browser without grpc-web gateway. Avoid GraphQL without query cost limits — one deep query can DDOS your microservices.

#### Production example
Platform standard: internal `inventory-service` ↔ `order-service` on gRPC with Protobuf; APIM exposes REST `POST /orders` to partners. Mobile team wanted GraphQL — built `mobile-bff` with DataLoader batching product IDs, complexity limit 200, timeout 3s. Latency dropped vs 8 REST round-trips; ops added Grafana on resolver duration per field.

#### Common mistakes
- GraphQL mutations orchestrating sagas across 5 services without central state.
- gRPC without deadline — hung calls block thread pools.
- REST APIs without versioning for mobile apps that never upgrade.
- Mixing JSON and Protobuf for same contract without registry.

#### Interview follow-ups (with model answers)

**Q:** Can Spring Boot expose both REST and gRPC?
**A:** Yes — same service implements `@GrpcService` and `@RestController` sharing domain layer. Keep DTO mapping separate; generate gRPC from proto in CI. Health checks and metrics for both ports. Document that REST is for edge compatibility, gRPC for internal SLO.

**Q:** When would you reject GraphQL?
**A:** When team lacks operational maturity (no complexity limits, no tracing per resolver), when clients are few and stable (REST + OpenAPI suffices), or when write paths need saga orchestration better suited to explicit REST/gRPC workflows.

#### Scenario probe
CTO mandates GraphQL for all microservices to "reduce endpoints." Response?

**Model answer:** GraphQL at BFF layer only; domain services stay REST/gRPC with clear ownership. Mandating GraphQL everywhere couples schema to all teams, complicates versioning, and centralizes failure. Propose mobile BFF pilot with metrics; keep payment on REST with idempotency keys.

#### Code / config (when useful)

```protobuf
// inventory.proto
service InventoryService {
  rpc ReserveStock(ReserveRequest) returns (ReserveResponse);
}
```

```java
@GrpcService
class InventoryGrpc extends InventoryServiceGrpc.InventoryServiceImplBase {
  @Override
  public void reserveStock(ReserveRequest req, StreamObserver<ReserveResponse> obs) {
    var result = service.reserve(req.getOrderId(), req.getSku(), req.getQty());
    obs.onNext(ReserveResponse.newBuilder().setOk(result).build());
    obs.onCompleted();
  }
}
```

---

### 52. HATEOAS and hypermedia — when it still matters

**Short answer:** **HATEOAS** (Hypermedia as the Engine of Application State) embeds links (`_links`) in responses so clients discover actions dynamically — `rel: cancel`, `href: /orders/1/cancel`. It still matters for **long-lived public APIs**, **workflow APIs** (payments, approvals), and **evolving clients you do not control** — less for mobile apps with shipped binaries that prefer stable OpenAPI contracts. Spring HATEOAS provides `EntityModel` and `Link` builders. Trade-off: discoverability vs payload size and client complexity.

#### What it is
REST purists use hypermedia to decouple client from URL construction — server drives valid next states. HAL and JSON-LD are common formats. In Java, `spring-boot-starter-hateoas` wraps resources with links. Contrasts with **OpenAPI-first** where clients codegen fixed paths. Hypermedia shines when server controls state machine (order: placed → paid → shipped).

#### How it works (internals)
Controller returns `EntityModel<Order>` with `linkTo(methodOn(OrderController.class).cancel(id)).withRel("cancel")` only when transition legal. Client parses `_links` array — no hardcoded `/cancel` path. Spring Data REST auto-exposes hateoas for entities. Conditional links prevent illegal operations (no cancel after ship). Caching: links may change per state — ETag on resource.

#### When to use / when NOT to use
Use for partner APIs with multi-year integration, government/open data APIs, or internal workflow engines. Skip for high-performance mobile JSON APIs where every byte counts and app version ties to known endpoints. Hybrid: Problem Details + link to `help` doc is lightweight hypermedia.

#### Production example
B2B procurement API returns order with `_links`: `self`, `approve` (manager only), `reject`, `submit-invoice`. Partner integration survives URL restructuring because they follow `rel` not paths. Mobile consumer app uses fixed OpenAPI v2 — separate surface, no HATEOAS — documented in API catalog.

#### Common mistakes
- Links to actions that return 403 without documenting auth in `rel` or problem type.
- HATEOAS without consistent media type (`application/hal+json`).
- Clients ignore `_links` — wasted effort; survey consumers first.
- Every CRUD resource hypermedia — overkill for static catalogs.

#### Interview follow-ups (with model answers)

**Q:** HATEOAS vs OpenAPI — pick one?
**A:** Not mutually exclusive. OpenAPI documents contract; HATEOAS adds runtime discoverability for stateful resources. Public workflow API: both — OpenAPI for schema, HAL links for valid transitions. Internal microservices: OpenAPI/gRPC usually enough.

**Q:** How do you version hypermedia APIs?
**A:** Version media type or URL prefix (`/v2/orders`); links generated from version-aware controllers. Deprecation link `rel: deprecation` pointing to migration guide. Never break `rel` names — add new `rel` for new actions.

#### Scenario probe
Partner asks why `POST /orders/5/cancel` returns 404 but list response had no cancel link.

**Model answer:** Order state no longer allows cancel — HATEOAS omits link when illegal. Document that clients must not construct URLs; 404 on stale action is correct. Improve: return 409 with Problem Details `type` explaining state if client POSTs anyway.

#### Code / config (when useful)

```java
@GetMapping("/orders/{id}")
EntityModel<OrderDto> get(@PathVariable UUID id) {
    var order = service.find(id);
    var model = EntityModel.of(OrderDto.from(order));
    if (order.canCancel()) {
        model.add(linkTo(methodOn(OrderController.class).cancel(id)).withRel("cancel"));
    }
    return model;
}
```

---

### 53. Webhooks: signing, retries, idempotency, replay protection

**Short answer:** **Webhooks** push events to subscriber URLs (`POST` on payment captured). Security: **HMAC signature** (Stripe-style `Stripe-Signature` header), **timestamp tolerance** against replay, **idempotency** on `eventId`, and **HTTPS only**. Subscribers return 2xx quickly and process async; publishers retry with exponential backoff on 5xx/timeout. Java: verify signature in filter before controller; store processed event IDs. Trade-off: at-least-once delivery means subscribers must dedupe — publisher cannot assume single delivery.

#### What it is
Webhooks invert polling — SaaS notifies your `https://api.example.com/webhooks/stripe`. Publisher signs payload with shared secret; subscriber validates and acknowledges. Critical for payments (Stripe, Adyen), CI (GitHub), and internal event bridges. Spring `@RestController` endpoint with raw body string for signature verification (before JSON parse mutates bytes).

#### How it works (internals)
Signature: `HMAC-SHA256(secret, timestamp + "." + body)` compared constant-time. Reject if `|now - timestamp| > 5 min` (replay window). Idempotency: `INSERT INTO webhook_events (id, ...) ON CONFLICT DO NOTHING`; process only if insert succeeded. Publisher retries 3–72h with jitter; subscriber must be fast — queue to `@Async` or Kafka after 200 OK. Idempotency-Key header optional for subscriber-initiated replays.

#### When to use / when NOT to use
Use when integrators need near-real-time notifications. Prefer Kafka/SQS for internal systems you control. Webhooks for external partners without message broker access. Always document retry policy and signing algorithm in developer portal.

#### Production example
`payment-gateway` sends `payment.captured` webhook; Spring filter verifies HMAC, rejects replay >300s old. Service enqueues to Kafka, returns 200 in 40ms. Duplicate delivery same `eventId` hits unique constraint — skipped with metric `webhook.duplicate`. Incident: subscriber returned 500 slowly — gateway retried 50 times; fix async handoff and 200-with-queue pattern.

#### Common mistakes
- Parsing JSON before signature verify — whitespace breaks HMAC.
- No timestamp check — replay attack with captured payload.
- Long synchronous processing in webhook handler — timeouts cause retry storm.
- Logging full payload with PII.

#### Interview follow-ups (with model answers)

**Q:** How do subscribers test webhooks locally?
**A:** Stripe CLI `stripe listen --forward-to localhost:8080/webhooks` or ngrok with signing secret in dev profile. Integration tests use fixed secret + golden payload bytes for HMAC assertion. Never disable signature verify in prod profile.

**Q:** Webhook vs SSE vs WebSocket?
**A:** Webhooks are server-to-server push over HTTP POST — ideal for backend integration. SSE/WebSocket for browser real-time UI. Choose webhooks when subscriber is your API, not end-user browser.

#### Scenario probe
Attacker replays yesterday's signed webhook; finance double-credits account.

**Model answer:** Missing timestamp tolerance or idempotency on `eventId`. Add both; rotate signing secret if leaked. Reconcile ledger against payment provider API nightly to detect duplicates.

#### Code / config (when useful)

```java
void verifyStripe(String payload, String sigHeader, String secret) {
    var parts = parseSigHeader(sigHeader);
    if (Math.abs(Instant.now().getEpochSecond() - parts.timestamp()) > 300)
        throw new SecurityException("replay");
    var expected = hmacSha256(secret, parts.timestamp() + "." + payload);
    if (!MessageDigest.isEqual(expected, parts.v1()))
        throw new SecurityException("bad signature");
}
```

---

### 54. API monetization: quotas, API keys, usage plans (APIM-style)

**Short answer:** **API monetization** packages access into **products** with **usage plans**: rate limits (calls/min), quotas (calls/month), and optional billing tiers. **API keys** or **subscription IDs** identify the consumer; gateway (Azure APIM, Kong, AWS API Gateway) enforces limits before traffic hits Spring Boot. Java services trust gateway-injected headers (`Ocp-Apim-Subscription-Key`, `X-Consumer-Id`) after gateway auth. Trade-off: gateway coupling versus protecting origin from abuse and enabling commercial API products.

#### What it is
Azure API Management: **API** → **Product** (e.g., Gold) → **Subscription** (key) → policies (`rate-limit`, `quota`, `jwt-validate`). Partners subscribe; keys rotate without redeploying backend. Usage analytics export to App Insights or billing system. Internal microservices may use lighter rate limits at Ingress; external monetization needs SKU catalog and overage handling.

#### How it works (internals)
APIM policy pipeline: inbound `rate-limit-by-key` (calls per 60s), `quota-by-key` (monthly), `validate-jwt` for OAuth partners. Counter stored in APIM Redis; 429 with `Retry-After` when exceeded. Backend receives `X-Forwarded-For` and subscription context headers — log for chargeback. Spring can second-limit per tenant with Bucket4j if defense in depth. Overage: webhook to billing or hard block per product terms.

#### When to use / when NOT to use
Use when selling API access or multi-tenant SaaS with tiered limits. Internal-only east-west traffic: mesh quotas or K8s rate limits may suffice. Do not implement billing solely in application memory without gateway — attackers bypass if they reach origin directly — network policy block direct origin access.

#### Production example
Partner "Gold" plan: 1000 req/min, 1M/month quota on `GET /rates`. APIM returns 429 at 1001st call in minute; dashboard shows usage 78% mid-month — sales upsell trigger. Spring Boot trusts only traffic from APIM private IP; direct pod access denied. Free tier key throttled to 10 req/min — protects shared Postgres.

#### Common mistakes
- API keys in query strings — logged in access logs.
- No per-subscription metrics — cannot debug "who DDoSed us."
- Quota reset timezone confusion for global customers.
- Backend ignores 429 contract — partners get inconsistent errors.

#### Interview follow-ups (with model answers)

**Q:** API key vs OAuth client credentials?
**A:** API keys identify subscription/plan — simple for server-to-server partners. OAuth client credentials for scoped access and token expiry — better for enterprise SSO integrations. Many products offer both: key for quick start, OAuth for production.

**Q:** How prevent key sharing abuse?
**A:** Bind key to allowed IP ranges, mutual TLS, or JWT issued after partner auth. Anomaly detection on usage patterns (geo velocity). Rotate keys on schedule; audit key creation in portal.

#### Scenario probe
Partner exceeds quota but claims "we need burst for go-live." Architecture response?

**Model answer:** Temporary quota increase via APIM policy override with expiry date and exec approval — not permanent disable. Offer paid burst tier. Origin still protected; monitor post-go-live to revert or upgrade contract.

#### Code / config (when useful)

```xml
<!-- Azure APIM inbound policy snippet -->
<rate-limit-by-key calls="1000" renewal-period="60" counter-key="@(context.Subscription.Id)" />
<quota-by-key calls="1000000" renewal-period="2629800" counter-key="@(context.Subscription.Id)" />
```

---

### 55. JSON:API / OData vs plain REST for enterprise clients

**Short answer:** **JSON:API** standardizes compound documents, sparse fieldsets, and `included` relationships — good for consistent client libraries. **OData** (`$filter`, `$orderby`, `$expand`) exposes queryable SQL-like HTTP — powerful for ERP/analytics integrators, dangerous if exposed without row-level security and query cost limits. **Plain REST** with OpenAPI stays simplest for most Java teams. Choose JSON:API/OData when enterprise buyers mandate standard; otherwise plain REST + documented pagination filters avoids foot-guns. Trade-off: standards reduce custom doc burden versus query abuse and implementation complexity.

#### What it is
JSON:API (`application/vnd.api+json`): resources with `type`, `id`, `relationships`, pagination links. OData v4: Microsoft ecosystem, SAP integrations, `$select` projection. Spring: `jsonapi-resources` libraries or **Olingo** OData4 for Spring. Plain REST: query params `?status=active&sort=-createdAt` you control explicitly.

#### How it works (internals)
OData parses `$filter` into expression tree — ORM translation risk (SQL injection if buggy). Must cap `$top`, deny `$expand` on large relations, enforce auth filter injection (`tenantId eq 'x'`). JSON:API compound documents reduce round-trips but serializers must handle inclusion rules. Plain REST: you implement only needed query params — smaller attack surface.

#### When to use / when NOT to use
| Standard | Fit |
|----------|-----|
| OData | Enterprise ERP integrations, Power BI, known filter grammar |
| JSON:API | Public API consistency across many resource types |
| Plain REST | Mobile, startups, internal microservices, faster delivery |

Never expose raw OData on multi-tenant data without mandatory tenant filter in interceptor.

#### Production example
Bank exports accounts API — two Fortune 500 clients required OData for Excel Power Query. Team added OData read-only endpoint on read replica with `$top` max 100, blocked `$expand=transactions`, row-level security via `TenantContext` in Olingo custom handler. Mobile app continues plain REST `/v2/accounts` — two surfaces, shared domain service.

#### Common mistakes
- OData `$filter` allowing unindexed columns — DB meltdown.
- JSON:API over-nesting — payloads larger than plain REST.
- Two incompatible pagination styles in one API.
- Implementing full OData write without PATCH semantics testing.

#### Interview follow-ups (with model answers)

**Q:** How do you secure OData endpoints?
**A:** Read replica only, `$top` cap, allowlist filterable fields, inject tenant predicate server-side (ignore client tenant filter), query timeout 5s, authZ per entity set. Audit log expensive queries. Integration test: `$filter` injection attempts fail.

**Q:** JSON:API vs GraphQL for flexible reads?
**A:** JSON:API is REST-constrained with standard pagination/inclusion; GraphQL is client-shaped queries with higher ops risk. JSON:API easier to cache at CDN; GraphQL needs persisted queries or complexity limits.

#### Scenario probe
Sales sold "full OData" on your CRUD API; prod DB CPU 100% after client ships `$filter` on unindexed column.

**Model answer:** Emergency: block OData endpoint at gateway, allowlist indexed fields, add read replica. Long-term: documented supported filters, query plan monitoring, sales alignment on "OData subset" not arbitrary SQL.

#### Code / config (when useful)

```java
// Plain REST — explicit safe query surface
@GetMapping("/orders")
Page<OrderDto> list(
    @RequestParam Optional<OrderStatus> status,
    @PageableDefault(size = 50, sort = "createdAt", direction = DESC) Pageable page) {
    return service.find(status, page);
}
```

---

## Scenario-based interview drills

### S1. Double charge after mobile payment retry

**Situation:** Checkout `POST /payments` times out at the gateway; iOS retries with the same body but without `Idempotency-Key`. Two pods process near-simultaneous requests; customer sees two captures in the card statement.

**What they're testing:** Idempotency design, concurrency, HTTP retry semantics, Spring controller boundaries, observability.

**How to structure your answer:**
- Acknowledge duplicate side effect risk on POST
- Describe durable idempotency store with unique constraint
- Explain concurrent request handling
- Cover gateway/client guidance and metrics

**Model answer:** Root cause is treating POST as fire-and-forget while clients and gateways retry on ambiguous outcomes. I implement server-side idempotency keyed by `(tenant_id, idempotency_key)` with a unique index — not an in-memory map. Flow: begin transaction, insert idempotency row `PENDING`; on duplicate key, read existing outcome and return the same HTTP status and body. Only one thread proceeds to call the payment provider, forwarding the same key so the PSP deduplicates too. Store request hash; mismatch on same key returns 409. Spring `@RestController` returns 201 on first success, 200 on replay. Document in OpenAPI that mobile must send `Idempotency-Key` on every payment create. Gateway policy: retry only when key present. Metrics: `idempotency_replay_total`, alert on collision spikes. Support runbook searches by key. Post-incident: integration test with two parallel RestAssured calls proving single capture. Never blame 'the network' without fixing contract and storage. Reconciliation job compares ledger to PSP settlements nightly.

**Common weak answers:** 'Use Redis TTL.' 'Client should not retry.' No unique constraint or race discussion.

**Follow-up probes (with answers):**

**Q:** How long to retain idempotency keys?
**A:** Typically 24–72 hours for HTTP POST — enough for mobile background retries; archive outcomes if audit requires longer.

**Q:** 409 vs 200 on replay?
**A:** 200/201 with identical body is friendlier to generic retry libraries; 409 only when the same key arrives with a different payload hash.

---

### S2. OpenAPI breaking change ships Friday

**Situation:** Partner integration team pages you: `required` field added to `OrderDto` without a version bump; their CI contract tests failed after your Thursday deploy. Traffic still hits `/v1/orders`.

**What they're testing:** OpenAPI as contract, backward compatibility, CI gates, versioning policy.

**How to structure your answer:**
- Classify breaking vs safe change
- Immediate mitigation for partners
- CI prevention
- Long-term versioning

**Model answer:** Adding a required JSON field on a live version is a breaking change — full stop. Immediate mitigation: hotfix making the field optional with server-side default, or feature-flagged validation only on `/v2`. Communicate with partners via changelog and status page; do not silently fix only your own mobile app. CI must run openapi-diff (or Buf breaking rules) on every PR against the published spec; Pact or golden JSON fixtures catch response shape drift. Version policy: additive changes on v1; breaking changes only on v2 with `Sunset` header on v1 endpoints. Springdoc publishes examples for error responses too — partners parse Problem Details, not stack traces. Post-incident ADR: no Friday deploys for public contract; required-field changes need major version label and migration guide. Senior answer names tools, rollback, and partner comms — not 'we updated the DTO'. Record traffic-weighted OpenAPI coverage in the release checklist.

**Common weak answers:** 'They should read Slack.' 'Just bump version tomorrow.' No openapi-diff mention.

**Follow-up probes (with answers):**

**Q:** Nullable vs required in OpenAPI 3?
**A:** Use `required` array and `nullable` carefully; document PATCH omission vs null semantics.

**Q:** Consumer-driven contracts?
**A:** Pact complements OpenAPI — verifies provider satisfies real consumer expectations, not just schema shape.

---

### S3. v1 sunset with lingering traffic

**Situation:** Six months after announcing v1 sunset, metrics show 8% of order traffic still on `/v1/orders`. Product wants to pull the plug Monday; legal says partners had written notice.

**What they're testing:** API versioning, deprecation headers, metrics, communication, risk management.

**How to structure your answer:**
- Measure who still calls v1
- Staged enforcement
- Migration support
- Final removal criteria

**Model answer:** I never hard-delete a version on a calendar whim without traffic attribution. First, break down v1 calls by API key, tenant, and User-Agent — often one legacy batch job remains. Contact owners with diff doc and deadline extension only if business-critical. Staged enforcement: `Deprecation` and `Sunset` headers already sent; next add structured warning field in JSON for v1 responses; then 429 with `Retry-After` and migration link; finally 410 Gone with Problem Detail pointing to v2 OpenAPI. Spring routes v1 controllers in a separate package for clean removal. Maintain compatibility tests until traffic <0.1% for two weeks. Rollback plan: keep v1 read-only shadow behind feature flag one more sprint if a bank partner slips. Document in changelog and email integrators — headers alone are insufficient. Senior judgment balances velocity with contractual notice periods. Dashboard per-version SLOs prevent silent regressions during migration.

**Common weak answers:** 'Turn it off.' No metrics, no staged 429/410, no partner identification.

**Follow-up probes (with answers):**

**Q:** URL vs header versioning?
**A:** URL prefix is clearest for caching and routing; vendor media types when URLs must stay frozen.

**Q:** 410 Gone vs 404?
**A:** 410 signals intentional retirement with migration docs; 404 hides existence — pick per security policy.

---

### S4. Gateway timeout causes duplicate orders

**Situation:** Apigee times out `POST /orders` at 30s while fulfillment takes 45s on peak. Clients retry; warehouse sees duplicate picks for the same customer basket.

**What they're testing:** Long-running POST vs 202 pattern, idempotency, gateway timeouts, async workflows.

**How to structure your answer:**
- Explain why POST retry duplicated work
- Immediate containment
- Correct async pattern
- Client contract update

**Model answer:** A synchronous POST that exceeds gateway timeout is a retry trap. Immediate containment: enable `Idempotency-Key` on order create (if missing) and dedupe warehouse messages by `orderId`. Correct design: `POST /orders` returns 202 Accepted with `Location: /orders/{id}` and `status=PENDING` when work exceeds a few seconds; client polls or subscribes via webhook. Spring `@Async` or outbox publishes fulfillment after DB commit — HTTP thread freed under 200ms. Align gateway, Tomcat, and downstream timeouts: gateway > client < server processing budget for sync paths only. OpenAPI documents which operations are sync vs async. Metrics on `order_duplicate_prevented_total`. Post-fix load test proves 60s fulfillment does not hold HTTP connections. Senior point: not every operation belongs in a request-response thread. BFF translates 202 + poll into mobile-friendly UX with progress states.

**Common weak answers:** 'Increase timeout to 120s.' 'Disable retries.' No 202 or idempotency.

**Follow-up probes (with answers):**

**Q:** 202 vs 201?
**A:** 201 when resource is created synchronously; 202 when accepted for processing — include status URI.

**Q:** Webhook vs poll?
**A:** Webhooks for partners; mobile poll with exponential backoff and ETag on status resource.

---

### S5. ETag conflict storm on concurrent edits

**Situation:** Admin UI loads order, two operators edit different fields; both PUT without `If-Match`. Last write wins silently drops one change. Support escalations follow.

**What they're testing:** Optimistic concurrency, 412 Precondition Failed, Spring MVC headers, UX for merge.

**How to structure your answer:**
- Name lost-update problem
- ETag/If-Match mechanism
- Spring implementation
- UX for conflict resolution

**Model answer:** Lost updates happen when PUT behaves as blind replace. I expose weak ETag from `version` or hash of representation; `PUT` and `PATCH` require `If-Match`. On mismatch return 412 with Problem Detail and current representation so UI can merge. Spring: compare header to `order.getVersion()` before service update; never rely on client-sent version in body alone (mass assignment risk). Document in OpenAPI example flows. For high-contention resources, consider PATCH with JSON Patch ops per field. Metrics on 412 rate — spike means UX or training issue. Integration test: two parallel PUTs, second gets 412. Alternative: field-level timestamps — heavier. Senior answer connects HTTP precondition semantics to operator trust; silent overwrite is a production bug, not 'user error'. BFF can translate 412 into a three-way merge dialog for React admin.

**Common weak answers:** 'Use pessimistic locks everywhere.' 'Tell users to refresh.' No If-Match or 412.

**Follow-up probes (with answers):**

**Q:** Strong vs weak ETag?
**A:** Weak ETags are fine for JSON version integers; strong when byte-identical matters.

**Q:** PATCH with If-Match?
**A:** Yes — partial updates must respect the same concurrency token as PUT.

---

### S6. Inconsistent error envelopes across services

**Situation:** React app parses errors inconsistently: `order-service` returns RFC 7807, `inventory-service` returns `{message: ...}`, gateway sometimes HTML 502.

**What they're testing:** Problem Details, BFF aggregation, gateway configuration, shared libraries.

**How to structure your answer:**
- Standardize on one schema
- Shared Spring advice
- Gateway/BFF behavior
- Observability with traceId

**Model answer:** Inconsistent errors break client UX and on-call search. Standard: RFC 7807 with extensions `traceId`, `errors[]` for validation. Shared internal library provides base `@ControllerAdvice`; each service adds domain `type` URIs. BFF must forward downstream Problem Details without nesting `{error: {error: ...}}`. Gateway maps upstream 502/503 to JSON Problem Detail, never HTML maintenance pages on `/api/*`. Propagate `X-Request-Id` from edge through MDC. OpenAPI documents all 4xx/5xx with examples. CI contract test asserts error shape per endpoint. Runbook: Kibana search by `traceId`. Migration: inventory-service ships adapter translating legacy shape during one sprint. Senior architects invest in one error story — cheaper than every frontend branch parsing five formats. Error catalog wiki links stable type URIs to runbook steps.

**Common weak answers:** 'Frontend handles all variants.' '502 is fine as HTML.' No shared library.

**Follow-up probes (with answers):**

**Q:** i18n for errors?
**A:** Keep machine `type` stable; localize `title` client-side or via `Accept-Language` on BFF.

**Q:** OAuth errors vs Problem Details?
**A:** OAuth token endpoint keeps OAuth format; business APIs use Problem Details consistently.

---

### S7. CORS preflight blocks SPA rollout

**Situation:** New React admin on `admin.example.com` calls `api.example.com`; browser shows CORS failure on `POST` with `Authorization` and custom `X-Tenant-Id`. Backend team says 'works in Postman'.

**What they're testing:** CORS, OPTIONS, Spring Security, gateway vs app responsibility.

**How to structure your answer:**
- Explain preflight trigger
- OPTIONS handling
- Spring Security config
- Never use * with credentials

**Model answer:** Postman is not a browser — non-simple requests with custom headers trigger OPTIONS preflight. `Authorization` + `X-Tenant-Id` requires `Access-Control-Allow-Headers` listing both, `Allow-Methods` including POST, and explicit `Allow-Origin` matching `https://admin.example.com` — not `*` when cookies or credentials used. Spring Security must permit OPTIONS without auth while still protecting POST. Prefer configuring CORS at API gateway for consistency; app-level `CorsConfigurationSource` as backup. Return 204 on OPTIONS quickly — do not route to heavy controllers. Document allowed origins per environment. Test with browser devtools, not curl alone. Senior note: CORS is browser enforcement, not a substitute for authz — still validate JWT and tenant on every POST. Staging uses distinct origins to catch misconfiguration before prod.

**Common weak answers:** 'Disable CORS.' '* origin with credentials.' 'Use JSONP.'

**Follow-up probes (with answers):**

**Q:** Gateway vs Spring CORS?
**A:** Gateway centralizes; app-level for local dev — avoid duplicate conflicting headers.

**Q:** OPTIONS on 404?
**A:** Preflight must hit a handler — 404 on OPTIONS blocks the real request.

---

### S8. Cursor pagination duplicates after concurrent inserts

**Situation:** Mobile feed uses offset pagination on `GET /events`; users report duplicate items after live sports scores insert rapidly during matches.

**What they're testing:** Offset vs cursor, stable sort keys, OpenAPI documentation.

**How to structure your answer:**
- Explain offset instability
- Keyset/cursor design
- Opaque signed cursor
- Drop or document total count

**Model answer:** Offset pagination skips/duplicates when rows shift under concurrent inserts — classic feed bug. Fix: keyset pagination on `(created_at, id)` with tiebreaker; `WHERE (created_at, id) < (:cAt, :cId) ORDER BY ... LIMIT 20`. Encode opaque base64url cursor — HMAC-signed to prevent tampering. OpenAPI documents `next` link; no arbitrary page jumps on mobile. Spring service builds cursor from last row; repository query uses composite predicate. Do not expose raw offsets on high-write tables. Optional `prev` for admin only. Integration test: insert rows between pages, assert no duplicates. Senior trade-off: cursors complicate 'jump to page 5' admin UIs — separate admin endpoint with offset and warning. Index `(created_at DESC, id DESC)` must match sort order exactly.

**Common weak answers:** 'Increase page size.' 'Cache feed.' Still using OFFSET on live table.

**Follow-up probes (with answers):**

**Q:** Sign cursors?
**A:** HMAC with server secret prevents clients forging early pages or scraping offsets.

**Q:** Multi-column sort?
**A:** Include all sort keys in cursor predicate with lexicographic comparison.

---

### S9. Rate limit without Retry-After hammers API

**Situation:** Partner batch job receives 429 without `Retry-After`; their script immediately retries 10k times, amplifying outage. Your API returns plain text 'Too Many Requests'.

**What they're testing:** Rate limiting headers, 429 semantics, Problem Details, partner guidance.

**How to structure your answer:**
- Correct 429 response shape
- Retry-After and backoff
- Token bucket vs sliding window
- Partner documentation

**Model answer:** 429 must be machine-actionable: RFC 7807 Problem Detail, `Retry-After` seconds or HTTP-date, optional `X-RateLimit-Remaining` headers. Plain text invites dumb retry loops. Gateway (Kong/Apigee) enforces quota per API key; Spring filter as second layer. Document exponential backoff with jitter in partner guide. Differentiate soft limit (429) from hard ban (403). Metrics on 429 per tenant — alert if one key dominates. OpenAPI example for 429. Senior ops: during incident, temporarily raise quota for critical partner only via config, not code deploy. Load test validates limiter under burst. Never rate-limit health/readiness probes. Idempotency keys still required — 429 retry must not duplicate POST side effects.

**Common weak answers:** 'Ban their API key.' No Retry-After. HTML or plain text 429.

**Follow-up probes (with answers):**

**Q:** Global vs per-tenant limits?
**A:** Per-tenant fairness; global circuit when DB unhealthy.

**Q:** 429 vs 503?
**A:** 429 client exceeded quota; 503 server overload — different retry policies.

---

### S10. Senior REST design review for payments API

**Situation:** Team asks you to review greenfield `POST /payments`, `GET /payments/{id}`, refunds, and webhooks before public beta. Design doc is two pages with endpoint list only.

**What they're testing:** Holistic REST design, security, operability, checklist depth.

**How to structure your answer:**
- Resource model and verbs
- Idempotency and status codes
- Errors, pagination, versioning
- Security and SLOs

**Model answer:** I walk the checklist aloud: Resources — payments and refunds as nouns; cancellations as sub-resource POST. POST /payments requires `Idempotency-Key`, returns 201 + Location; replays return same body. GET safe; no mutations via query params. PATCH not used for money state — explicit POST transitions with 409 on invalid state machine. RFC 7807 everywhere; validation errors field-scoped. Webhooks signed HMAC with replay protection. OpenAPI with examples for 400/404/409/412/429. Auth: OAuth2 client credentials for partners; BOLA tests on every id path. Pagination cursor on list; rate limits documented. Version in /v1 prefix; changelog process. Observability: traceId, metrics on latency and error rate per endpoint. p99 budget 300ms read, 1s write sync or 202 async. Load test and contract tests in CI. I decline beta until idempotency store and reconciliation job exist — payments without dedupe is not shippable. Design review output is annotated OpenAPI PR, not slide deck only.

**Common weak answers:** 'Looks fine.' 'Add endpoints later.' No idempotency, BOLA, or error envelope.

**Follow-up probes (with answers):**

**Q:** Biggest red flag?
**A:** POST payments without durable idempotency and without documented retry semantics.

**Q:** Webhook vs poll?
**A:** Webhooks for partners with signing; poll status for mobile when push unavailable.

---
