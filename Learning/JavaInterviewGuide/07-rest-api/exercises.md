# REST API — Practical Exercises

Type these. Run them. Break them. Reading is not practice.

**Structure:** Part A (Basic) · Part B (Intermediate) · Part C (Hard) · Weekend challenge  
**Stack:** Spring Boot 3, `springdoc-openapi`, `curl`, Testcontainers Postgres optional.

---

# Part A — Basic (10)

## Exercise 1 — CRUD skeleton with correct status codes

**Task:** Implement `POST /orders` (201 + `Location`), `GET /orders/{id}` (200/404), `DELETE /orders/{id}` (204).

**Solution:**

```java
@RestController
@RequestMapping("/orders")
class OrderController {
    private final OrderService service;

    OrderController(OrderService service) { this.service = service; }

    @PostMapping
    ResponseEntity<OrderDto> create(@Valid @RequestBody CreateOrderRequest req) {
        Order order = service.create(req);
        URI location = URI.create("/orders/" + order.getId());
        return ResponseEntity.created(location).body(OrderDto.from(order));
    }

    @GetMapping("/{id}")
    OrderDto get(@PathVariable String id) {
        return service.find(id)
                .map(OrderDto::from)
                .orElseThrow(() -> new OrderNotFoundException(id));
    }

    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    void delete(@PathVariable String id) {
        service.delete(id);
    }
}
```

```bash
curl -s -X POST localhost:8080/orders \
  -H 'Content-Type: application/json' \
  -d '{"customerId":"c1","amountCents":5000}' -D - | head
# HTTP/1.1 201
# Location: /orders/ord_abc123
```

**Senior takeaway:** `201 Created` without `Location` is a common review comment.

---

## Exercise 2 — Bean Validation on the request body

**Task:** Reject invalid payloads with `400` and field-level errors.

**Solution:**

```java
public record CreateOrderRequest(
        @NotBlank String customerId,
        @Positive long amountCents,
        @Size(max = 3) List<@NotBlank String> skus
) {}
```

```java
@RestControllerAdvice
class ValidationAdvice {
    @ExceptionHandler(MethodArgumentNotValidException.class)
    ResponseEntity<Map<String, Object>> handle(MethodArgumentNotValidException ex) {
        var fields = ex.getBindingResult().getFieldErrors().stream()
                .map(fe -> Map.of("field", fe.getField(), "message", fe.getDefaultMessage()))
                .toList();
        return ResponseEntity.badRequest().body(Map.of(
                "title", "Validation failed",
                "status", 400,
                "errors", fields));
    }
}
```

```bash
curl -s -X POST localhost:8080/orders \
  -H 'Content-Type: application/json' \
  -d '{"customerId":"","amountCents":-1}' | jq
```

---

## Exercise 3 — Offset pagination with `Pageable`

**Task:** `GET /orders?page=0&size=20&sort=createdAt,desc` returns a page envelope.

**Solution:**

```java
@GetMapping
Page<OrderDto> list(@PageableDefault(size = 20, sort = "createdAt", direction = DESC) Pageable pageable) {
    return service.findAll(pageable).map(OrderDto::from);
}
```

```bash
curl -s 'localhost:8080/orders?page=0&size=5&sort=createdAt,desc' | jq '.content,.totalElements'
```

Response shape: `{ "content": [...], "totalElements": 42, "totalPages": 9, "number": 0, "size": 5 }`.

**Senior takeaway:** Offset pagination degrades on deep pages (`OFFSET 100000`). Use keyset for feeds.

---

## Exercise 4 — Filtering with query parameters

**Task:** `GET /orders?status=PENDING&customerId=c1` — validate enum, reject unknown status.

**Solution:**

```java
@GetMapping
Page<OrderDto> list(
        @RequestParam(required = false) OrderStatus status,
        @RequestParam(required = false) String customerId,
        Pageable pageable) {
    return service.findBy(status, customerId, pageable).map(OrderDto::from);
}
```

```java
// Repository
Page<Order> findByStatusAndCustomerId(OrderStatus status, String customerId, Pageable p);
Page<Order> findByStatus(OrderStatus status, Pageable p);
Page<Order> findByCustomerId(String customerId, Pageable p);
Page<Order> findAll(Pageable p);
```

```bash
curl -s 'localhost:8080/orders?status=PENDING&customerId=c1&size=10'
curl -s 'localhost:8080/orders?status=BOGUS'  # 400 — Spring fails enum bind
```

---

## Exercise 5 — `PUT` full replace vs `PATCH` partial update

**Task:** `PUT` replaces the whole resource; `PATCH` updates only `status`.

**Solution:**

```java
@PutMapping("/{id}")
OrderDto replace(@PathVariable String id, @Valid @RequestBody ReplaceOrderRequest req) {
    return OrderDto.from(service.replace(id, req));
}

@PatchMapping("/{id}")
OrderDto patch(@PathVariable String id, @RequestBody Map<String, Object> patch) {
    if (patch.containsKey("status")) {
        return OrderDto.from(service.updateStatus(id, OrderStatus.valueOf(patch.get("status").toString())));
    }
    throw new BadRequestException("Only status patch supported");
}
```

```bash
curl -s -X PUT localhost:8080/orders/ord_1 \
  -H 'Content-Type: application/json' \
  -d '{"customerId":"c1","amountCents":9000,"status":"PENDING"}'

curl -s -X PATCH localhost:8080/orders/ord_1 \
  -H 'Content-Type: application/json' \
  -d '{"status":"SHIPPED"}'
```

---

## Exercise 6 — Consistent 404 via `@ResponseStatus` + domain exception

**Task:** Never return `200` with `{ "error": "not found" }`.

**Solution:**

```java
@ResponseStatus(HttpStatus.NOT_FOUND)
class OrderNotFoundException extends RuntimeException {
    OrderNotFoundException(String id) { super("Order not found: " + id); }
}

@RestControllerAdvice
class ApiExceptionAdvice {
    @ExceptionHandler(OrderNotFoundException.class)
    ProblemDetail notFound(OrderNotFoundException ex) {
        return ProblemDetail.forStatusAndDetail(NOT_FOUND, ex.getMessage());
    }
}
```

```bash
curl -s -o /dev/null -w '%{http_code}\n' localhost:8080/orders/missing  # 404
```

---

## Exercise 7 — `Content-Type` enforcement

**Task:** Reject `POST` with `text/plain` body.

**Solution:**

```java
@PostMapping(consumes = MediaType.APPLICATION_JSON_VALUE, produces = MediaType.APPLICATION_JSON_VALUE)
ResponseEntity<OrderDto> create(@Valid @RequestBody CreateOrderRequest req) { ... }
```

```bash
curl -s -X POST localhost:8080/orders \
  -H 'Content-Type: text/plain' -d 'hello' -w '\n%{http_code}\n'
# 415 Unsupported Media Type
```

---

## Exercise 8 — Minimal OpenAPI spec (design first)

**Task:** Write `openapi.yaml` for the order CRUD before coding.

**Solution:**

```yaml
openapi: 3.1.0
info:
  title: Order API
  version: 1.0.0
paths:
  /orders:
    get:
      parameters:
        - in: query
          name: page
          schema: { type: integer, default: 0 }
        - in: query
          name: size
          schema: { type: integer, default: 20, maximum: 100 }
      responses:
        '200':
          description: Page of orders
    post:
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateOrderRequest'
      responses:
        '201':
          description: Created
          headers:
            Location:
              schema: { type: string }
  /orders/{id}:
    get:
      parameters:
        - in: path
          name: id
          required: true
          schema: { type: string }
      responses:
        '200': { description: OK }
        '404': { description: Not found }
components:
  schemas:
    CreateOrderRequest:
      type: object
      required: [customerId, amountCents]
      properties:
        customerId: { type: string }
        amountCents: { type: integer, minimum: 1 }
```

---

## Exercise 9 — HATEOAS-style `self` link (optional but interview-friendly)

**Task:** Include `_links.self` in responses.

**Solution:**

```java
public record OrderDto(String id, String status, long amountCents, Map<String, LinkDto> links) {
    static OrderDto from(Order o) {
        return new OrderDto(o.getId(), o.getStatus().name(), o.getAmountCents(),
                Map.of("self", new LinkDto("/orders/" + o.getId())));
    }
}
record LinkDto(String href) {}
```

```bash
curl -s localhost:8080/orders/ord_1 | jq '._links // .links'
```

---

## Exercise 10 — Health vs readiness

**Task:** Expose `/actuator/health` (liveness) and a custom readiness that checks DB.

**Solution:**

```yaml
management:
  endpoint:
    health:
      probes:
        enabled: true
  health:
    readinessstate:
      enabled: true
```

```java
@Component
class DbReadinessIndicator implements HealthIndicator {
    private final JdbcTemplate jdbc;
    DbReadinessIndicator(JdbcTemplate jdbc) { this.jdbc = jdbc; }

    @Override
    public Health health() {
        jdbc.queryForObject("SELECT 1", Integer.class);
        return Health.up().build();
    }
}
```

```bash
curl -s localhost:8080/actuator/health/readiness | jq
```

---

# Part B — Intermediate (10)

## Exercise 11 — RFC 7807 Problem Details for all errors

**Task:** Map validation, not-found, and conflict to `application/problem+json`.

**Solution:**

```java
@RestControllerAdvice
class ProblemDetailsAdvice {
    @ExceptionHandler(MethodArgumentNotValidException.class)
    ProblemDetail validation(MethodArgumentNotValidException ex) {
        var pd = ProblemDetail.forStatus(BAD_REQUEST);
        pd.setTitle("Validation failed");
        pd.setType(URI.create("https://api.example.com/problems/validation"));
        pd.setProperty("errors", ex.getBindingResult().getFieldErrors().stream()
                .map(fe -> Map.of("field", fe.getField(), "message", Objects.toString(fe.getDefaultMessage())))
                .toList());
        return pd;
    }

    @ExceptionHandler(OrderNotFoundException.class)
    ProblemDetail notFound(OrderNotFoundException ex) {
        var pd = ProblemDetail.forStatus(NOT_FOUND);
        pd.setTitle("Order not found");
        pd.setDetail(ex.getMessage());
        return pd;
    }

    @ExceptionHandler(OrderConflictException.class)
    ProblemDetail conflict(OrderConflictException ex) {
        var pd = ProblemDetail.forStatus(CONFLICT);
        pd.setTitle("Conflict");
        pd.setDetail(ex.getMessage());
        return pd;
    }
}
```

```bash
curl -s -H 'Accept: application/problem+json' localhost:8080/orders/x | jq
```

---

## Exercise 12 — Idempotent `POST` with `Idempotency-Key`

**Task:** Replay same key + body → same `201`. Different body → `409`.

**Solution:**

```java
@Entity
@Table(name = "idempotency_records")
class IdempotencyRecord {
    @Id String key;
    String requestHash;
    int responseStatus;
    @Column(columnDefinition = "text") String responseBody;
    Instant createdAt;
}

@Component
class IdempotencyFilter extends OncePerRequestFilter {
    private final IdempotencyRepository repo;
    private final ObjectMapper mapper;

    @Override
    protected void doFilterInternal(HttpServletRequest req, HttpServletResponse res, FilterChain chain)
            throws ServletException, IOException {
        if (!"POST".equalsIgnoreCase(req.getMethod())) {
            chain.doFilter(req, res);
            return;
        }
        String key = req.getHeader("Idempotency-Key");
        if (key == null || key.isBlank()) {
            chain.doFilter(req, res);
            return;
        }
        byte[] body = req.getInputStream().readAllBytes();
        String hash = DigestUtils.sha256Hex(body);
        var cached = repo.findById(key);
        if (cached.isPresent()) {
            var rec = cached.get();
            if (!rec.getRequestHash().equals(hash)) {
                res.setStatus(409);
                res.getWriter().write("{\"title\":\"Idempotency key reused with different body\"}");
                return;
            }
            res.setStatus(rec.getResponseStatus());
            res.setContentType("application/json");
            res.getWriter().write(rec.getResponseBody());
            return;
        }
        var wrapped = new ContentCachingResponseWrapper(res);
        chain.doFilter(new CachedBodyRequestWrapper(req, body), wrapped);
        if (wrapped.getStatus() == 201) {
            repo.save(new IdempotencyRecord(key, hash, 201,
                    new String(wrapped.getContentAsByteArray()), Instant.now()));
        }
        wrapped.copyBodyToResponse();
    }
}
```

```bash
KEY=$(uuidgen)
curl -s -X POST localhost:8080/orders -H "Idempotency-Key: $KEY" \
  -H 'Content-Type: application/json' -d '{"customerId":"c1","amountCents":100}' | jq .id

curl -s -X POST localhost:8080/orders -H "Idempotency-Key: $KEY" \
  -H 'Content-Type: application/json' -d '{"customerId":"c1","amountCents":100}' | jq .id
# same id

curl -s -o /dev/null -w '%{http_code}\n' -X POST localhost:8080/orders -H "Idempotency-Key: $KEY" \
  -H 'Content-Type: application/json' -d '{"customerId":"c1","amountCents":999}'
# 409
```

---

## Exercise 13 — Cursor (keyset) pagination

**Task:** `GET /orders?cursor=...&limit=20` — opaque Base64 cursor, stable under inserts.

**Solution:**

```java
public record OrderCursor(Instant createdAt, String id) {}

@GetMapping
CursorPage<OrderDto> list(
        @RequestParam(required = false) String cursor,
        @RequestParam(defaultValue = "20") @Max(100) int limit) {
    OrderCursor c = cursor == null ? null : decode(cursor);
    List<Order> rows = repo.findKeyset(c, limit + 1);
    boolean hasMore = rows.size() > limit;
    if (hasMore) rows = rows.subList(0, limit);
    String next = hasMore ? encode(new OrderCursor(
            rows.get(rows.size() - 1).getCreatedAt(),
            rows.get(rows.size() - 1).getId())) : null;
    return new CursorPage<>(rows.stream().map(OrderDto::from).toList(), next);
}

static String encode(OrderCursor c) {
    return Base64.getUrlEncoder().withoutPadding().encodeToString(
            new ObjectMapper().writeValueAsBytes(c));
}
```

```sql
-- OrderRepository native query
SELECT * FROM orders
 WHERE (:cursorTs IS NULL AND :cursorId IS NULL)
    OR (created_at, id) < (:cursorTs, :cursorId)
 ORDER BY created_at DESC, id DESC
 FETCH FIRST :limit ROWS ONLY;
```

```bash
curl -s 'localhost:8080/orders?limit=2' | jq '{items: .items | length, nextCursor}'
curl -s "localhost:8080/orders?limit=2&cursor=$(curl -s 'localhost:8080/orders?limit=2' | jq -r .nextCursor)"
```

---

## Exercise 14 — ETag + `If-Match` optimistic concurrency

**Task:** `PUT` with stale ETag returns `412 Precondition Failed`.

**Solution:**

```java
@GetMapping("/{id}")
ResponseEntity<OrderDto> get(@PathVariable String id) {
    Order o = service.load(id);
    return ResponseEntity.ok()
            .eTag("\"" + o.getVersion() + "\"")
            .body(OrderDto.from(o));
}

@PutMapping("/{id}")
ResponseEntity<OrderDto> update(
        @PathVariable String id,
        @RequestHeader(value = "If-Match", required = false) String ifMatch,
        @Valid @RequestBody ReplaceOrderRequest req) {
    Order o = service.load(id);
    String current = "\"" + o.getVersion() + "\"";
    if (ifMatch != null && !ifMatch.equals(current)) {
        return ResponseEntity.status(PRECONDITION_FAILED).build();
    }
    Order updated = service.replace(id, req);
    return ResponseEntity.ok()
            .eTag("\"" + updated.getVersion() + "\"")
            .body(OrderDto.from(updated));
}
```

```bash
ETAG=$(curl -s -D - localhost:8080/orders/ord_1 -o /dev/null | awk '/^ETag:/ {print $2}' | tr -d '\r')
curl -s -X PUT localhost:8080/orders/ord_1 -H "If-Match: $ETAG" \
  -H 'Content-Type: application/json' \
  -d '{"customerId":"c1","amountCents":5000,"status":"PENDING"}' -w '\n%{http_code}\n'

curl -s -o /dev/null -w '%{http_code}\n' -X PUT localhost:8080/orders/ord_1 -H 'If-Match: "0"' \
  -H 'Content-Type: application/json' -d '{"customerId":"c1","amountCents":5000,"status":"PENDING"}'
# 412
```

---

## Exercise 15 — API versioning: URL prefix vs `Accept` header

**Task:** Support `/v1/orders` and `/v2/orders` (v2 adds `currency` field).

**Solution:**

```java
@RestController
@RequestMapping("/v1/orders")
class OrderV1Controller { /* existing DTO */ }

@RestController
@RequestMapping("/v2/orders")
class OrderV2Controller {
    @GetMapping("/{id}")
    OrderV2Dto get(@PathVariable String id) {
        return OrderV2Dto.from(service.load(id)); // includes currency
    }
}
```

Alternative header versioning:

```java
@GetMapping(value = "/orders/{id}", headers = "Accept=application/vnd.example.order.v2+json")
OrderV2Dto getV2(@PathVariable String id) { ... }
```

```bash
curl -s localhost:8080/v1/orders/ord_1 | jq keys
curl -s localhost:8080/v2/orders/ord_1 | jq keys
```

**Senior takeaway:** URL versioning is easier for caches and clients; header versioning keeps URLs stable.

---

## Exercise 16 — BOLA (broken object-level authorization)

**Task:** User A cannot read User B's order. Return `404` (hide existence) or `403` — pick one, test it.

**Solution:**

```java
@GetMapping("/{id}")
OrderDto get(@PathVariable String id, @AuthenticationPrincipal Jwt jwt) {
    String subject = jwt.getSubject();
    Order o = service.load(id);
    if (!o.getCustomerId().equals(subject)) {
        throw new OrderNotFoundException(id); // 404 — no leak
    }
    return OrderDto.from(o);
}
```

```java
@Test
void userBCannotReadUserAOrder() {
    String orderId = createOrderAs("userA");
    mockMvc.perform(get("/orders/" + orderId).header("Authorization", bearer("userB")))
            .andExpect(status().isNotFound());
}
```

---

## Exercise 17 — Sub-resource action: `POST /orders/{id}/cancellation`

**Task:** Return `409` if already shipped; `404` if missing.

**Solution:**

```java
@PostMapping("/{id}/cancellation")
ResponseEntity<Void> cancel(@PathVariable String id) {
    service.cancel(id);
    return ResponseEntity.noContent().build();
}

// Service
void cancel(String id) {
    Order o = load(id);
    if (o.getStatus() == SHIPPED) throw new OrderConflictException("Cannot cancel shipped order");
    o.setStatus(CANCELLED);
    repo.save(o);
}
```

```bash
curl -s -X POST localhost:8080/orders/ord_shipped/cancellation -w '\n%{http_code}\n'  # 409
curl -s -X POST localhost:8080/orders/ord_pending/cancellation -w '\n%{http_code}\n'    # 204
```

---

## Exercise 18 — Long-running job: `202 Accepted` + status poll

**Task:** `POST /reports` → `202` + `/reports/{id}`; poll until `200` with download URL.

**Solution:**

```java
@PostMapping("/reports")
ResponseEntity<ReportStatusDto> start(@Valid @RequestBody ReportRequest req) {
    String id = reportService.enqueue(req);
    return ResponseEntity.accepted()
            .location(URI.create("/reports/" + id))
            .body(new ReportStatusDto(id, "PENDING", null));
}

@GetMapping("/reports/{id}")
ResponseEntity<ReportStatusDto> status(@PathVariable String id) {
    ReportJob job = reportService.get(id);
    if (job.getStatus() == PENDING || job.getStatus() == RUNNING) {
        return ResponseEntity.status(ACCEPTED).body(ReportStatusDto.from(job));
    }
    return ResponseEntity.ok(ReportStatusDto.from(job)); // includes downloadUrl
}
```

```bash
LOC=$(curl -s -D - -X POST localhost:8080/reports \
  -H 'Content-Type: application/json' -d '{"from":"2026-01-01","to":"2026-01-31"}' \
  | awk '/^Location:/ {print $2}' | tr -d '\r')
curl -s "$LOC" | jq .status
```

---

## Exercise 19 — OpenAPI drift CI gate

**Task:** Fail build if committed `openapi.yaml` differs from runtime spec.

**Solution:**

```xml
<!-- pom.xml: springdoc -->
<dependency>
  <groupId>org.springdoc</groupId>
  <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
  <version>2.6.0</version>
</dependency>
```

```bash
# scripts/check-openapi.sh
./mvnw -q spring-boot:start -Dspring-boot.run.arguments=--server.port=18080 &
PID=$!
sleep 15
curl -s localhost:18080/v3/api-docs.yaml -o /tmp/generated.yaml
diff -u openapi.yaml /tmp/generated.yaml
kill $PID
```

---

## Exercise 20 — Review and rewrite a bad API

**Task:** Given legacy endpoints, produce RESTful replacements and explain each change.

**Bad API:**

```
GET /getOrders?userId=1
POST /updateOrderStatus
POST /deleteOrder
```

**Solution (rewrite):**

```
GET    /users/{userId}/orders          # noun resources, GET for reads
PATCH  /orders/{id}  { "status": "..." }  # PATCH partial update, id in path
DELETE /orders/{id}                    # DELETE for removal, not POST
```

| Change | Why |
|--------|-----|
| `/getOrders` → `GET /users/{id}/orders` | HTTP method expresses action; no verb in URL |
| `POST /updateOrderStatus` → `PATCH /orders/{id}` | Updates are PATCH/PUT on the resource |
| `POST /deleteOrder` → `DELETE /orders/{id}` | DELETE is idempotent and semantic |
| `userId` query → path param | Scopes collection to parent resource |

Practice narrating this in 3 minutes out loud.

---

# Part C — Hard (8)

## Exercise 21 — Concurrent PUT race (two clients, one wins)

**Task:** Two parallel PUTs with the same ETag: one `200`, one `412`.

**Solution:**

```java
@Test
void concurrentPut_onePreconditionFailed() throws Exception {
    String id = createOrder();
    String etag = fetchEtag(id);

    var t1 = CompletableFuture.runAsync(() -> putWithEtag(id, etag, 5000));
    var t2 = CompletableFuture.runAsync(() -> putWithEtag(id, etag, 6000));
    CompletableFuture.allOf(t1, t2).join();

    int s1 = t1.get(); // implementation returns status code
    int s2 = t2.get();
    assertThat(Set.of(s1, s2)).containsExactlyInAnyOrder(200, 412);
}
```

Use `@Version` on JPA entity or `UPDATE ... WHERE version = :v` in SQL for the actual guard.

---

## Exercise 22 — Idempotency across retries + network timeout

**Task:** Client times out after server persisted `201`. Retry must not create a second order.

**Solution:** Combine Exercise 12 with client-generated `Idempotency-Key` (UUID v4). Server stores response for 24h.

```java
@Entity
class IdempotencyRecord {
    @Id String key;
    Instant expiresAt;
    // ...
}

// Cleanup job
@Scheduled(cron = "0 */15 * * * *")
void purgeExpired() {
    repo.deleteByExpiresAtBefore(Instant.now());
}
```

```bash
KEY=$(uuidgen)
curl -m 1 -X POST localhost:8080/orders -H "Idempotency-Key: $KEY" \
  -H 'Content-Type: application/json' -d '{"customerId":"c1","amountCents":100}' || true
curl -s -X POST localhost:8080/orders -H "Idempotency-Key: $KEY" \
  -H 'Content-Type: application/json' -d '{"customerId":"c1","amountCents":100}' | jq .id
```

---

## Exercise 23 — Full Order API OpenAPI with Problem Details schemas

**Task:** Complete spec for CRUD, cancellation, pagination, idempotency header, all error responses.

**Solution (excerpt):**

```yaml
paths:
  /orders:
    post:
      parameters:
        - in: header
          name: Idempotency-Key
          schema: { type: string, format: uuid }
      responses:
        '201': { description: Created }
        '400':
          content:
            application/problem+json:
              schema: { $ref: '#/components/schemas/Problem' }
        '409':
          content:
            application/problem+json:
              schema: { $ref: '#/components/schemas/Problem' }
  /orders/{id}/cancellation:
    post:
      responses:
        '204': { description: Cancelled }
        '409': { description: Already shipped }
components:
  schemas:
    Problem:
      type: object
      required: [type, title, status]
      properties:
        type: { type: string, format: uri }
        title: { type: string }
        status: { type: integer }
        detail: { type: string }
        errors:
          type: array
          items:
            type: object
            properties:
              field: { type: string }
              message: { type: string }
```

---

## Exercise 24 — Pagination at scale: explain OFFSET vs keyset

**Task:** Benchmark `OFFSET 100000 LIMIT 20` vs keyset. Document in a comment block for interview.

**Solution:**

```sql
-- SLOW: scans and discards 100k rows
SELECT * FROM orders ORDER BY created_at DESC OFFSET 100000 FETCH FIRST 20 ROWS ONLY;

-- FAST: uses index (created_at DESC, id DESC)
SELECT * FROM orders
 WHERE (created_at, id) < (:ts, :id)
 ORDER BY created_at DESC, id DESC
 FETCH FIRST 20 ROWS ONLY;

CREATE INDEX ix_orders_created_id ON orders (created_at DESC, id DESC);
```

On a 1M-row table, OFFSET p99 often > 500ms; keyset stays < 10ms with the right index.

---

## Exercise 25 — Conditional GET with `If-None-Match`

**Task:** Return `304 Not Modified` when ETag matches — save bandwidth on mobile clients.

**Solution:**

```java
@GetMapping("/{id}")
ResponseEntity<OrderDto> get(@PathVariable String id,
        @RequestHeader(value = "If-None-Match", required = false) String ifNoneMatch) {
    Order o = service.load(id);
    String etag = "\"" + o.getVersion() + "\"";
    if (etag.equals(ifNoneMatch)) {
        return ResponseEntity.status(NOT_MODIFIED).eTag(etag).build();
    }
    return ResponseEntity.ok().eTag(etag).body(OrderDto.from(o));
}
```

```bash
ETAG=$(curl -s -D - localhost:8080/orders/ord_1 -o /dev/null | awk '/^ETag:/ {print $2}' | tr -d '\r')
curl -s -o /dev/null -w '%{http_code}\n' -H "If-None-Match: $ETAG" localhost:8080/orders/ord_1
# 304
```

---

## Exercise 26 — Rate limiting response headers

**Task:** Return `429` with `Retry-After` when limit exceeded.

**Solution:**

```java
@Component
class RateLimitFilter extends OncePerRequestFilter {
    private final Bucket bucket = Bucket.builder()
            .addLimit(Bandwidth.classic(100, Refill.intervally(100, Duration.ofMinutes(1))))
            .build();

    @Override
    protected void doFilterInternal(HttpServletRequest req, HttpServletResponse res, FilterChain chain)
            throws ServletException, IOException {
        if (!bucket.tryConsume(1)) {
            res.setStatus(429);
            res.setHeader("Retry-After", "60");
            res.setContentType("application/problem+json");
            res.getWriter().write("{\"title\":\"Too Many Requests\",\"status\":429}");
            return;
        }
        res.setHeader("X-RateLimit-Remaining", String.valueOf(bucket.getAvailableTokens()));
        chain.doFilter(req, res);
    }
}
```

---

## Exercise 27 — Version migration: sunset `v1` with `Deprecation` header

**Task:** `v1` responses include `Deprecation: true` and `Link: </v2/orders>; rel="successor-version"`.

**Solution:**

```java
@GetMapping("/{id}")
ResponseEntity<OrderDto> getV1(@PathVariable String id) {
    return ResponseEntity.ok()
            .header("Deprecation", "true")
            .header("Link", "</v2/orders/" + id + ">; rel=\"successor-version\"")
            .body(OrderDto.from(service.load(id)));
}
```

Document migration timeline in `CHANGELOG.md`.

---

## Exercise 28 — PR review: fix “200 on error” anti-pattern

**Task:** Refactor this controller; write the test that proves the fix.

**Broken:**

```java
@GetMapping("/orders/{id}")
Map<String, Object> get(@PathVariable String id) {
    return service.find(id)
            .map(o -> Map.of("success", true, "data", o))
            .orElse(Map.of("success", false, "error", "not found")); // always 200!
}
```

**Solution:**

```java
@GetMapping("/orders/{id}")
OrderDto get(@PathVariable String id) {
    return OrderDto.from(service.load(id)); // throws OrderNotFoundException → 404
}

@Test
void missingOrder_returns404() throws Exception {
    mockMvc.perform(get("/orders/nope"))
            .andExpect(status().isNotFound())
            .andExpect(jsonPath("$.title").value("Order not found"));
}
```

---

## Exercise 29 — gRPC reserve-stock service (local)

**Difficulty:** Intermediate

**Task:** Add a `inventory.proto` with `ReserveStock` RPC. Implement `@GrpcService` in Spring Boot and a `grpcurl` client call from CLI.

**Solution:**

```bash
grpcurl -plaintext -d '{"orderId":"o1","sku":"W1","qty":2}' \
  localhost:9090 inventory.InventoryService/ReserveStock
```

**Senior takeaway:** gRPC fits internal JVM calls with deadlines; keep REST at the edge for partners.

---

## Exercise 30 — HAL links for cancellable orders

**Difficulty:** Basic

**Task:** Return `EntityModel<OrderDto>` with `cancel` link only when `status == PLACED`. Integration test: placed order has link; shipped order does not.

**Solution:**

```java
if (order.status() == PLACED) {
    model.add(linkTo(methodOn(OrderController.class).cancel(id)).withRel("cancel"));
}
```

**Senior takeaway:** HATEOAS documents valid transitions — clients follow `rel`, not guessed URLs.

---

## Exercise 31 — Stripe-style webhook HMAC verify

**Difficulty:** Hard

**Task:** Implement webhook endpoint verifying `HMAC-SHA256` over `timestamp.body`, rejecting replays >5 minutes. Store `eventId` idempotently before processing.

**Solution:**

```java
@PostMapping("/webhooks/payments")
ResponseEntity<Void> receive(@RequestBody String raw, @RequestHeader("X-Signature") String sig) {
    verifier.verify(raw, sig);
    var event = mapper.readValue(raw, PaymentEvent.class);
    if (!inbox.tryInsert(event.id())) return ResponseEntity.ok().build();
    queue.publish(event);
    return ResponseEntity.ok().build();
}
```

**Senior takeaway:** Verify signature on raw bytes, return 200 fast, dedupe on `eventId` — publishers retry aggressively.

---

## Exercise 32 — Bucket4j rate limit per API key

**Difficulty:** Intermediate

**Task:** Spring filter rate-limits `X-Api-Key` to 100 requests/minute; return 429 with `Retry-After`.

**Solution:**

```java
private final Cache<String, Bucket> buckets = Caffeine.newBuilder()
    .expireAfterAccess(Duration.ofHours(1))
    .build(key -> Bucket.builder()
        .addLimit(Bandwidth.classic(100, Refill.intervally(100, Duration.ofMinutes(1))))
        .build());

if (!buckets.get(apiKey).tryConsume(1)) {
    res.setStatus(429);
    res.setHeader("Retry-After", "60");
    return;
}
```

**Senior takeaway:** Rate limits belong at gateway for monetization; in-app Bucket4j is defense-in-depth when origin could be reached directly.

---

## Exercise 33 — Safe list endpoint (no OData foot-gun)

**Difficulty:** Basic

**Task:** Design `GET /orders` with explicit `status`, `createdAfter`, cursor pagination — reject unknown query params with 400. Test that `?foo=bar` fails.

**Solution:**

```java
@GetMapping("/orders")
Page<OrderDto> list(@Valid OrderListCriteria criteria, Pageable page) {
    return service.list(criteria, page);
}

public record OrderListCriteria(Optional<OrderStatus> status, Optional<Instant> createdAfter) {}
```

```java
@Test
void unknownQueryParam_returns400() throws Exception {
    mockMvc.perform(get("/orders").param("foo", "bar"))
        .andExpect(status().isBadRequest());
}
```

**Senior takeaway:** Plain REST with allowlisted filters beats open OData unless you can cap query cost and enforce row-level security.

---

# Weekend challenge

1. Implement the full Order API (Exercises 1–18) in a scratch Spring Boot project with Testcontainers Postgres.
2. Run `scripts/check-openapi.sh` in CI; fix any drift.
3. Load-test cursor pagination vs offset with `k6` — graph latency at page 1 vs page 5000.
4. Record a 5-minute Loom: explain idempotency keys, ETags, and Problem Details as if to a junior on your team.
