# Microservices — Practical Exercises

Type these. Run them. Break them. Reading is not practice.

**Structure:** Part A (Basic) · Part B (Intermediate) · Part C (Hard — production failures with Testcontainers/Spring)

---

# Part A — Basic

## Exercise 1 — Draw service boundaries (e-commerce)

**Difficulty:** Basic

**Task:** On paper, split an e-commerce monolith into bounded contexts: Order, Inventory, Payment, Shipping. List each service's owned data, APIs, and events. No shared database tables.

**Solution:**

```
┌─────────────┐     OrderPlaced      ┌──────────────┐
│ Order Svc   │ ───────────────────► │ Inventory    │
│ orders DB   │                      │ inventory DB │
└──────┬──────┘                      └──────┬───────┘
       │ StockReserved                      │
       ▼                                    ▼
┌─────────────┐     PaymentCaptured  ┌──────────────┐
│ Payment Svc │ ◄─────────────────── │ (events)     │
│ payments DB │                      └──────────────┘
└─────────────┘
```

| Service   | Owns                         | REST (examples)              | Events emitted        |
|-----------|------------------------------|------------------------------|-----------------------|
| Order     | `orders`, `order_lines`      | `POST /orders`, `GET /orders/{id}` | `OrderPlaced`, `OrderCancelled` |
| Inventory | `stock`, `reservations`      | `POST /reservations`         | `StockReserved`, `StockRejected` |
| Payment   | `payments`, `refunds`        | `POST /payments`             | `PaymentCaptured`, `PaymentFailed` |
| Shipping  | `shipments`                  | `POST /shipments`            | `ShipmentCreated`     |

**Rule:** Order service stores `productId` + snapshot price — never JOINs inventory tables.

**Senior takeaway:** Boundaries follow **business capability + data ownership**, not team org chart. If two services write the same row, you don't have microservices — you have a distributed monolith.

---

## Exercise 2 — Two Spring Boot services over HTTP

**Difficulty:** Basic

**Task:** Create `catalog-service` (port 8081) and `pricing-service` (port 8082). Catalog calls pricing via `RestClient` to enrich a product response.

**Solution:**

```java
// pricing-service
@RestController
@RequestMapping("/prices")
class PriceController {
    @GetMapping("/{sku}")
    PriceDto get(@PathVariable String sku) {
        return new PriceDto(sku, new BigDecimal("29.99"), "USD");
    }
}
public record PriceDto(String sku, BigDecimal amount, String currency) {}
```

```java
// catalog-service
@Configuration
class RestClientConfig {
    @Bean
    RestClient pricingClient(@Value("${pricing.base-url}") String baseUrl) {
        return RestClient.builder().baseUrl(baseUrl).build();
    }
}

@Service
class CatalogService {
    private final RestClient pricing;

    CatalogService(RestClient pricingClient) {
        this.pricing = pricingClient;
    }

    ProductView getProduct(String sku) {
        var price = pricing.get()
                .uri("/prices/{sku}", sku)
                .retrieve()
                .body(PriceDto.class);
        return new ProductView(sku, "Widget", price.amount(), price.currency());
    }
}
public record ProductView(String sku, String name, BigDecimal price, String currency) {}
```

```yaml
# catalog application.yml
pricing:
  base-url: http://localhost:8082
```

```java
@SpringBootTest(webEnvironment = RANDOM_PORT)
class CatalogIntegrationTest {
    @Autowired TestRestTemplate rest;

    @Test
    void enrichesWithPrice() {
        var view = rest.getForObject("/products/SKU-1", ProductView.class);
        assertThat(view.price()).isEqualByComparingTo("29.99");
    }
}
```

**Senior takeaway:** Synchronous HTTP coupling is fine for read paths with timeouts. Every outbound call needs a **deadline** — default infinite waits become cascading outages.

---

## Exercise 3 — Environment-specific config

**Difficulty:** Basic

**Task:** Externalize `inventory.base-url`, `payment.timeout-ms`, and feature flag `saga.enabled` per profile (`local`, `staging`, `prod`).

**Solution:**

```yaml
# application.yml
app:
  inventory:
    base-url: http://localhost:8083
  payment:
    timeout-ms: 2000
  saga:
    enabled: false

---
spring.config.activate.on-profile: prod
app:
  inventory:
    base-url: https://inventory.internal
  payment:
    timeout-ms: 500
  saga:
    enabled: true
```

```java
@ConfigurationProperties(prefix = "app")
public record AppConfig(Inventory inventory, Payment payment, Saga saga) {
    public record Inventory(String baseUrl) {}
    public record Payment(long timeoutMs) {}
    public record Saga(boolean enabled) {}
}

@SpringBootApplication
@EnableConfigurationProperties(AppConfig.class)
public class OrderApp {}
```

```java
@Service
class PaymentClient {
    private final RestClient client;
    private final long timeoutMs;

    PaymentClient(AppConfig config) {
        this.timeoutMs = config.payment().timeoutMs();
        this.client = RestClient.builder()
                .baseUrl(config.inventory().baseUrl())
                .build();
    }
}
```

**Senior takeaway:** Twelve-factor config in env vars for secrets; non-secret tuning in profile YAML. **Never** bake prod URLs into code — mis-deployed profile takes down prod weekly in real teams.

---

## Exercise 4 — Liveness vs readiness probes

**Difficulty:** Basic

**Task:** Configure Spring Boot Actuator health groups. Readiness includes DB check; liveness is lightweight ping only.

**Solution:**

```yaml
management:
  endpoint:
    health:
      probes:
        enabled: true
      group:
        liveness:
          include: ping
        readiness:
          include: db,diskSpace
  endpoints:
    web:
      exposure:
        include: health,info
```

```java
@Component
class InventoryHealthIndicator implements HealthIndicator {
    private final RestClient inventory;

    InventoryHealthIndicator(RestClient inventoryClient) {
        this.inventory = inventoryClient;
    }

    @Override
    public Health health() {
        try {
            inventory.get().uri("/actuator/health").retrieve().toBodilessEntity();
            return Health.up().build();
        } catch (Exception e) {
            return Health.down(e).withDetail("dependency", "inventory").build();
        }
    }
}
```

```yaml
management.endpoint.health.group.readiness.include: db,inventoryHealth
```

**Senior takeaway:** Liveness failure → kube **restarts** pod. Readiness failure → removed from LB. Putting slow downstream checks on liveness causes restart storms — keep liveness dumb.

---

## Exercise 5 — Client timeout on `RestClient`

**Difficulty:** Basic

**Task:** Call a slow endpoint (2s delay). Set 500ms connect + read timeout. Assert `ResourceAccessException` / timeout, not hang.

**Solution:**

```java
@Bean
RestClient slowAwareClient() {
    var factory = new JdkClientHttpRequestFactory();
    factory.setConnectTimeout(Duration.ofMillis(500));
    factory.setReadTimeout(Duration.ofMillis(500));

    return RestClient.builder()
            .baseUrl("http://localhost:8089")
            .requestFactory(factory)
            .build();
}
```

```java
@Test
void timesOutFast() {
    wireMock.stubFor(get("/slow").willReturn(
            aResponse().withFixedDelay(2000).withBody("ok")));

    assertThatThrownBy(() -> client.get().uri("/slow").retrieve().toBodilessEntity())
            .isInstanceOf(ResourceAccessException.class);
}
```

**Senior takeaway:** Timeout is not optional — it's the difference between one slow dependency and a **fleet-wide thread starvation**. Set timeouts shorter than upstream gateway timeout.

---

## Exercise 6 — API Gateway route (Spring Cloud Gateway)

**Difficulty:** Basic

**Task:** Route `/api/orders/**` → `order-service:8080`, `/api/catalog/**` → `catalog-service:8081`. Strip `/api` prefix.

**Solution:**

```yaml
# gateway application.yml
spring:
  cloud:
    gateway:
      routes:
        - id: orders
          uri: http://order-service:8080
          predicates:
            - Path=/api/orders/**
          filters:
            - StripPrefix=1
            - name: RequestRateLimiter
              args:
                redis-rate-limiter.replenishRate: 100
                redis-rate-limiter.burstCapacity: 200
        - id: catalog
          uri: http://catalog-service:8081
          predicates:
            - Path=/api/catalog/**
          filters:
            - StripPrefix=1
```

```java
@SpringBootTest(webEnvironment = RANDOM_PORT)
class GatewayRouteTest {
    @Autowired WebTestClient client;

    @Test
    void routesOrders() {
        client.get().uri("/api/orders/1")
                .exchange()
                .expectStatus().isOk();
    }
}
```

**Senior takeaway:** Gateway centralizes cross-cutting concerns (auth, rate limit, routing). Business logic stays in services — gateway is not a second BFF unless you have a deliberate aggregation layer.

---

## Exercise 7 — Correlation ID in logs (MDC)

**Difficulty:** Basic

**Task:** Accept `X-Correlation-Id` header (or generate UUID). Put in MDC; log it on every line. Forward to downstream calls.

**Solution:**

```java
@Component
public class CorrelationFilter extends OncePerRequestFilter {
    static final String HEADER = "X-Correlation-Id";
    static final String MDC_KEY = "correlationId";

    @Override
    protected void doFilterInternal(HttpServletRequest req, HttpServletResponse res,
                                    FilterChain chain) throws ServletException, IOException {
        String id = Optional.ofNullable(req.getHeader(HEADER))
                .filter(s -> !s.isBlank())
                .orElse(UUID.randomUUID().toString());
        MDC.put(MDC_KEY, id);
        res.setHeader(HEADER, id);
        try {
            chain.doFilter(req, res);
        } finally {
            MDC.remove(MDC_KEY);
        }
    }
}
```

```xml
<!-- logback-spring.xml -->
<pattern>%d{ISO8601} [%thread] %-5level %logger{36} [cid=%X{correlationId}] - %msg%n</pattern>
```

```java
client.get()
    .uri("/inventory/reserve")
    .header("X-Correlation-Id", MDC.get("correlationId"))
    .retrieve()
    .toBodilessEntity();
```

**Senior takeaway:** Correlation ID is the minimum viable observability — grep across 12 pods without it is impossible. Upgrade to W3C `traceparent` (Exercise 15) for distributed traces.

---

## Exercise 8 — Idempotency key table design

**Difficulty:** Basic

**Task:** Design `idempotency_record` for `POST /payments`. Unique key per client request; store response for replay.

**Solution:**

```java
@Entity
@Table(name = "idempotency_record")
public class IdempotencyRecord {
    @Id
    private String key;           // client Idempotency-Key header

  @Column(nullable = false)
    private String requestHash;   // SHA-256 of canonical body

    private int httpStatus;
    @Column(columnDefinition = "text")
    private String responseBody;

    private Instant createdAt = Instant.now();
    @Column(nullable = false)
    private Instant expiresAt;    // TTL 24h
}
```

```sql
CREATE UNIQUE INDEX uk_idempotency_key ON idempotency_record(key);
CREATE INDEX idx_idempotency_expires ON idempotency_record(expires_at);
```

```java
// Lookup logic sketch
Optional<IdempotencyRecord> existing = repo.findById(key);
if (existing.isPresent()) {
    if (!existing.get().getRequestHash().equals(hash)) {
        throw new ConflictException("key reused with different body");
    }
    return replay(existing.get());
}
```

**Senior takeaway:** Idempotency keys turn **at-least-once** networks into **effectively-once** for clients. Store response body + status, not just "processed" boolean — clients need the same 201 payload on retry.

---

## Exercise 9 — Event catalog for order saga

**Difficulty:** Basic

**Task:** Document events for a checkout saga: producer, consumers, schema compatibility mode.

**Solution:**

| Event            | Producer  | Consumers              | Key fields                          | Compatibility |
|------------------|-----------|------------------------|-------------------------------------|---------------|
| `OrderPlaced`    | order     | inventory, analytics   | `orderId`, `lines[]`, `customerId`  | BACKWARD      |
| `StockReserved`  | inventory | order, warehouse       | `orderId`, `reservationId`          | BACKWARD      |
| `StockRejected`  | inventory | order                  | `orderId`, `reason`                 | BACKWARD      |
| `PaymentCaptured`| payment   | order, billing         | `orderId`, `paymentId`, `amount`    | BACKWARD      |
| `PaymentFailed`  | payment   | order                  | `orderId`, `reason`                 | BACKWARD      |
| `OrderConfirmed` | order     | shipping, email        | `orderId`, `confirmedAt`            | FULL          |
| `OrderCancelled` | order     | inventory, payment     | `orderId`, `reason`                 | BACKWARD      |

```json
{
  "type": "OrderPlaced",
  "orderId": "ord_123",
  "customerId": "cus_456",
  "lines": [{ "sku": "SKU-1", "qty": 2, "priceCents": 1999 }]
}
```

**Senior takeaway:** Event catalog is a contract between teams — bring it to interviews. `BACKWARD` = new consumers tolerate old events; never remove fields without version bump.

---

## Exercise 10 — Graceful shutdown

**Difficulty:** Basic

**Task:** Configure graceful shutdown. On SIGTERM, stop accepting new requests, finish in-flight (up to 30s), then exit.

**Solution:**

```yaml
server:
  shutdown: graceful

spring:
  lifecycle:
    timeout-per-shutdown-phase: 30s
```

```java
@Component
class DrainFilter extends OncePerRequestFilter {
    private final AtomicBoolean accepting = new AtomicBoolean(true);

    @EventListener
    void onShutdown(ContextClosedEvent e) {
        accepting.set(false);
    }

    @Override
    protected void doFilterInternal(HttpServletRequest req, HttpServletResponse res,
                                    FilterChain chain) throws ServletException, IOException {
        if (!accepting.get()) {
            res.setStatus(HttpStatus.SERVICE_UNAVAILABLE.value());
            return;
        }
        chain.doFilter(req, res);
    }
}
```

```bash
# local drill
kill -SIGTERM <pid>
# watch logs: "Commencing graceful shutdown"
```

**Senior takeaway:** K8s sends SIGTERM before removing pod from Service endpoints (if preStop + readiness configured). Long requests need graceful drain or they'll be cut mid-flight.

---

# Part B — Intermediate

## Exercise 11 — Resilience4j circuit breaker (basic)

**Difficulty:** Intermediate

**Task:** Wrap inventory call with circuit breaker. After 5 failures in 10 calls, open for 5s. Return fallback `StockUnknown`.

**Solution:**

```xml
<dependency>
  <groupId>io.github.resilience4j</groupId>
  <artifactId>resilience4j-spring-boot3</artifactId>
</dependency>
```

```yaml
resilience4j.circuitbreaker:
  instances:
    inventory:
      slidingWindowSize: 10
      minimumNumberOfCalls: 5
      failureRateThreshold: 50
      waitDurationInOpenState: 5s
      permittedNumberOfCallsInHalfOpenState: 3
```

```java
@Service
public class InventoryGateway {
    private final RestClient client;
    private final CircuitBreaker cb;

    public InventoryGateway(RestClient inventoryClient, CircuitBreakerRegistry registry) {
        this.client = inventoryClient;
        this.cb = registry.circuitBreaker("inventory");
    }

    public StockStatus check(String sku) {
        return cb.executeSupplier(() ->
                client.get().uri("/stock/{sku}", sku).retrieve().body(StockStatus.class));
    }

    public StockStatus checkWithFallback(String sku) {
        return Try.ofSupplier(cb.decorateSupplier(() ->
                client.get().uri("/stock/{sku}", sku).retrieve().body(StockStatus.class)))
            .recover(CallNotPermittedException.class, e -> StockStatus.unknown(sku))
            .get();
    }
}
```

```java
@Test
void circuitOpensAfterFailures() {
    wireMock.stubFor(get(urlMatching("/stock/.*"))
            .willReturn(aResponse().withStatus(500)));
    IntStream.range(0, 6).forEach(i -> gateway.checkWithFallback("SKU-1"));
    assertThat(cb.getState()).isEqualTo(CircuitBreaker.State.OPEN);
}
```

**Senior takeaway:** Circuit breaker protects **your** thread pool, not the downstream. Fallback must be semantically safe — `StockUnknown` ≠ `InStock`.

---

## Exercise 12 — Retry + bulkhead (Resilience4j)

**Difficulty:** Intermediate

**Task:** Retry inventory GET max 2 times (only on 503). Limit concurrent inventory calls to 10 via bulkhead. Prove retry storm is contained.

**Solution:**

```yaml
resilience4j.retry:
  instances:
    inventory:
      maxAttempts: 3
      waitDuration: 100ms
      enableExponentialBackoff: true
      retryExceptions:
        - org.springframework.web.client.HttpServerErrorException

resilience4j.bulkhead:
  instances:
    inventory:
      maxConcurrentCalls: 10
      maxWaitDuration: 0
```

```java
@CircuitBreaker(name = "inventory")
@Retry(name = "inventory")
@Bulkhead(name = "inventory")
public StockStatus check(String sku) { /* ... */ }
```

```java
@Test
void bulkheadRejectsWhenSaturated() throws Exception {
    wireMock.stubFor(get("/stock/X").willReturn(aResponse().withFixedDelay(2000)));
    ExecutorService exec = Executors.newFixedThreadPool(20);
    var results = new ConcurrentLinkedQueue<>();
    for (int i = 0; i < 20; i++) {
        exec.submit(() -> {
            try { results.add(gateway.check("X")); }
            catch (BulkheadFullException e) { results.add("rejected"); }
        });
    }
    Thread.sleep(500);
    assertThat(results).contains("rejected");
}
```

**Senior takeaway:** Retry without bulkhead multiplies load on a failing dependency — you DDoS your own recovery. `maxWaitDuration: 0` fails fast instead of queueing threads.

---

## Exercise 13 — Saga orchestration sketch (orders)

**Difficulty:** Intermediate

**Task:** Implement happy-path saga: `POST /orders` → reserve stock → capture payment → confirm order. Use in-memory state machine (no 2PC).

**Solution:**

```java
public enum SagaState { PENDING, STOCK_RESERVED, PAID, CONFIRMED, CANCELLED }

@Entity
public class Order {
    @Id private String id;
    @Enumerated(EnumType.STRING) private SagaState state;
    private long amountCents;
}

@Service
public class OrderSagaOrchestrator {
    @Transactional
    public Order place(CreateOrder cmd) {
        var order = orderRepo.save(new Order(cmd.id(), SagaState.PENDING, cmd.amountCents()));
        inventoryClient.reserve(cmd.id(), cmd.lines());
        order.setState(SagaState.STOCK_RESERVED);
        paymentClient.capture(cmd.id(), cmd.amountCents());
        order.setState(SagaState.PAID);
        order.setState(SagaState.CONFIRMED);
        return order;
    }

    @Transactional
    public void compensate(String orderId) {
        var order = orderRepo.findById(orderId).orElseThrow();
        if (order.getState().ordinal() >= SagaState.PAID.ordinal()) {
            paymentClient.refund(orderId);
        }
        if (order.getState().ordinal() >= SagaState.STOCK_RESERVED.ordinal()) {
            inventoryClient.release(orderId);
        }
        order.setState(SagaState.CANCELLED);
    }
}
```

```java
@Test
void happyPath() {
    var order = orchestrator.place(new CreateOrder("ord-1", lines, 5000));
    assertThat(order.getState()).isEqualTo(SagaState.CONFIRMED);
}
```

**Senior takeaway:** Orchestration is easier to debug; choreography scales teams better. Both need **compensations** and idempotent steps — saga state machine is the audit trail.

---

## Exercise 14 — Outbox pattern vs dual-write

**Difficulty:** Intermediate

**Task:** Show broken dual-write (DB + Kafka). Fix with transactional outbox table + publisher.

**Solution:**

```java
// BROKEN
@Transactional
public void create(Order o) {
    orderRepo.save(o);
    kafka.send("orders", o.id(), o); // separate system — crash gap
}

// FIXED
@Entity
public class OutboxEvent {
    @Id @GeneratedValue private Long id;
    private String aggregateId;
    private String type;
    @Column(columnDefinition = "text") private String payload;
    private Instant createdAt = Instant.now();
    private boolean published;
}

@Transactional
public void create(Order o) {
    orderRepo.save(o);
    outboxRepo.save(new OutboxEvent(o.id(), "OrderPlaced", toJson(o)));
}

@Scheduled(fixedDelay = 1000)
@Transactional
public void publishOutbox() {
    var batch = outboxRepo.findTop100ByPublishedFalse();
    for (var e : batch) {
        kafka.send("orders", e.getAggregateId(), e.getPayload());
        e.setPublished(true);
    }
}
```

```java
@Test
void outboxSurvivesCrashBeforePublish() {
    orderService.create(order);
    assertThat(outboxRepo.count()).isEqualTo(1);
    assertThat(outboxRepo.findAll().get(0).isPublished()).isFalse();
    publisher.publishOutbox();
    assertThat(outboxRepo.findAll().get(0).isPublished()).isTrue();
}
```

**Senior takeaway:** Dual-write is the most common distributed systems bug. Outbox gives **same-transaction** durability; publisher retries are safe with consumer idempotency.

---

## Exercise 15 — Distributed tracing (Micrometer Tracing)

**Difficulty:** Intermediate

**Task:** Propagate W3C `traceparent` across two services. Verify same `traceId` in both logs and Zipkin/Jaeger UI.

**Solution:**

```xml
<dependency>
  <groupId>io.micrometer</groupId>
  <artifactId>micrometer-tracing-bridge-brave</artifactId>
</dependency>
<dependency>
  <groupId>io.zipkin.reporter2</groupId>
  <artifactId>zipkin-reporter-brave</artifactId>
</dependency>
```

```yaml
management:
  tracing:
    sampling:
      probability: 1.0
  zipkin:
    tracing:
      endpoint: http://localhost:9411/api/v2/spans
```

```java
// order-service calls inventory — trace propagates automatically via RestClient bean
@Bean
RestClient tracedClient(RestClient.Builder builder) {
    return builder.build(); // auto-instrumented when micrometer-tracing on classpath
}

@RestController
class OrderController {
    @GetMapping("/orders/{id}/stock-check")
    String check(@PathVariable String id) {
        log.info("checking stock for {}", id); // includes traceId/spanId
        return inventoryClient.checkStock(id);
    }
}
```

```bash
docker run -d -p 9411:9411 openzipkin/zipkin
curl http://localhost:8080/orders/1/stock-check
# open http://localhost:9411 — single trace, two spans
```

**Senior takeaway:** Traces without propagation across async/Kafka boundaries are half-useful. Always verify `traceparent` on outbound messages and thread-pool handoffs.

---

## Exercise 16 — Gateway JWT validation + route auth

**Difficulty:** Intermediate

**Task:** Spring Cloud Gateway validates JWT on `/api/orders/**`. `/api/catalog/**` is public. Invalid token → 401 at gateway, never hits order-service.

**Solution:**

```yaml
spring:
  security:
    oauth2:
      resourceserver:
        jwt:
          issuer-uri: https://auth.example.com/realms/shop
```

```java
@Bean
SecurityWebFilterChain springSecurityFilterChain(ServerHttpSecurity http) {
    return http
            .csrf(ServerHttpSecurity.CsrfSpec::disable)
            .authorizeExchange(ex -> ex
                    .pathMatchers("/api/catalog/**").permitAll()
                    .pathMatchers("/api/orders/**").authenticated()
                    .anyExchange().denyAll())
            .oauth2ResourceServer(o -> o.jwt(Customizer.withDefaults()))
            .build();
}
```

```java
@Test
void gatewayRejectsMissingToken() {
    webClient.get().uri("/api/orders/1")
            .exchange()
            .expectStatus().isUnauthorized();
}

@Test
void gatewayPassesValidToken() {
    webClient.get().uri("/api/orders/1")
            .header(HttpHeaders.AUTHORIZATION, "Bearer " + validJwt())
            .exchange()
            .expectStatus().isOk();
}
```

**Senior takeaway:** Auth at gateway reduces attack surface but services should still validate scopes for defense-in-depth. Never trust internal network alone.

---

## Exercise 17 — Idempotency filter implementation

**Difficulty:** Intermediate

**Task:** Implement servlet filter for `Idempotency-Key` on `POST /payments`. Same key + body → cached response; same key + different body → 409.

**Solution:**

```java
@Component
@Order(Ordered.HIGHEST_PRECEDENCE + 10)
public class IdempotencyFilter extends OncePerRequestFilter {
    private final IdempotencyRepository repo;
    private final ObjectMapper mapper;

    @Override
    protected void doFilterInternal(HttpServletRequest req, HttpServletResponse res,
                                    FilterChain chain) throws ServletException, IOException {
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
        String hash = sha256(body);
        var existing = repo.findById(key);
        if (existing.isPresent()) {
            if (!existing.get().getRequestHash().equals(hash)) {
                res.sendError(409, "Idempotency key reused with different payload");
                return;
            }
            res.setStatus(existing.get().getHttpStatus());
            res.getWriter().write(existing.get().getResponseBody());
            return;
        }

        var wrapped = new ContentCachingResponseWrapper(res);
        chain.doFilter(new CachedBodyRequest(req, body), wrapped);

        repo.save(new IdempotencyRecord(key, hash, wrapped.getStatus(),
                new String(wrapped.getContentAsByteArray()), Instant.now().plus(24, ChronoUnit.HOURS)));
        wrapped.copyBodyToResponse();
    }
}
```

```java
@Test
void replayReturnsSameResponse() {
    var headers = new HttpHeaders();
    headers.set("Idempotency-Key", "pay-1");
    var body = Map.of("orderId", "ord-1", "amountCents", 1000);

    var r1 = rest.postForEntity("/payments", new HttpEntity<>(body, headers), PaymentResponse.class);
    var r2 = rest.postForEntity("/payments", new HttpEntity<>(body, headers), PaymentResponse.class);

    assertThat(r2.getStatusCode()).isEqualTo(r1.getStatusCode());
    assertThat(r2.getBody().paymentId()).isEqualTo(r1.getBody().paymentId());
}
```

**Senior takeaway:** Idempotency must be **transactional with business logic** — store record in same DB TX as payment row, or use unique constraint on `payment_idempotency_key` column.

---

## Exercise 18 — Fan-out N+1 HTTP and aggregator fix

**Difficulty:** Intermediate

**Task:** BFF calls `GET /users/{id}`, then N `GET /orders?user=`, then N `GET /payments`. Measure latency. Fix with `GET /users/{id}/dashboard` read model or parallel `CompletableFuture` with bulk endpoints.

**Solution:**

```java
// BROKEN — sequential N+1
public Dashboard broken(String userId) {
    User u = userClient.get(userId);
    List<Order> orders = orderClient.byUser(userId);
    List<Payment> payments = new ArrayList<>();
    for (Order o : orders) {
        payments.add(paymentClient.byOrder(o.id())); // N calls
    }
    return new Dashboard(u, orders, payments);
}

// FIX A — aggregator endpoint (preferred)
@GetMapping("/users/{id}/dashboard")
Dashboard dashboard(@PathVariable String id) {
    return dashboardRepo.findByUserId(id); // denormalized read model from events
}

// FIX B — parallel bulk
public Dashboard parallel(String userId) {
    var user = CompletableFuture.supplyAsync(() -> userClient.get(userId));
    var orders = CompletableFuture.supplyAsync(() -> orderClient.byUser(userId));
    return orders.thenCombine(user, (o, u) -> {
        var orderIds = o.stream().map(Order::id).toList();
        var payments = paymentClient.byOrders(orderIds); // single bulk call
        return new Dashboard(u, o, payments);
    }).join();
}
```

```java
@Test
void aggregatorBeatsFanOut() {
    long brokenMs = time(() -> bff.broken("u1"));
    long fixedMs = time(() -> bff.dashboard("u1"));
    assertThat(fixedMs).isLessThan(brokenMs / 3);
}
```

**Senior takeaway:** Chatty BFFs don't scale — event-sourced read models or bulk APIs are the fix. Parallel HTTP helps latency but not load; prefer one read per page.

---

# Part C — Hard (production failures)

## Exercise 19 — Circuit breaker opens during failure storm (Testcontainers + WireMock)

**Difficulty:** Hard

**Task:** Inventory returns 500. 100 concurrent order placements trip circuit breaker. Prove orders fail fast (< 50ms) instead of hanging 30s. Half-open probe recovers when inventory heals.

**Solution:**

```java
@Testcontainers
@SpringBootTest
class CircuitBreakerStormTest {
    @RegisterExtension
    static WireMockExtension inventory = WireMockExtension.newInstance()
            .options(wireMockConfig().dynamicPort())
            .build();

    @DynamicPropertySource
    static void props(DynamicPropertyRegistry r) {
        r.add("inventory.base-url", inventory::baseUrl);
    }

    @Test
    void failsFastWhenCircuitOpen() throws Exception {
        inventory.stubFor(get("/stock/SKU-1").willReturn(aResponse().withStatus(500)));

        // trip breaker
        IntStream.range(0, 20).parallel().forEach(i -> Try.run(() -> gateway.check("SKU-1")));

        long start = System.nanoTime();
        assertThatThrownBy(() -> gateway.check("SKU-1"))
                .isInstanceOf(CallNotPermittedException.class);
        long ms = (System.nanoTime() - start) / 1_000_000;
        assertThat(ms).isLessThan(50);

        // heal
        inventory.stubFor(get("/stock/SKU-1").willReturn(okJson("{\"available\":10}")));
        Thread.sleep(6000); // waitDurationInOpenState
        assertThat(gateway.check("SKU-1").available()).isEqualTo(10);
    }
}
```

**Senior takeaway:** Without circuit breaker, thread pools queue unbounded waits — p99 explodes, health checks fail, K8s restarts healthy pods. Fail-fast is a feature.

---

## Exercise 20 — Saga compensation failure (Testcontainers)

**Difficulty:** Hard

**Task:** Payment fails after stock reserved. Compensation must release stock. Simulate inventory release endpoint returning 500 once — retry must eventually release; order ends `CANCELLED`, not stuck `STOCK_RESERVED`.

**Solution:**

```java
@Test
void compensationRetriesUntilStockReleased() {
    inventory.stubFor(post("/reservations").willReturn(created()));
    inventory.stubFor(delete(urlMatching("/reservations/ord-1"))
            .inScenario("release")
            .whenScenarioStateIs(STARTED)
            .willReturn(serverError())
            .willSetStateTo("retry"));
    inventory.stubFor(delete(urlMatching("/reservations/ord-1"))
            .inScenario("release")
            .whenScenarioStateIs("retry")
            .willReturn(ok()));

    payment.stubFor(post("/capture").willReturn(serverError()));

    orchestrator.place(new CreateOrder("ord-1", lines, 5000));

    await().atMost(10, SECONDS).until(() ->
            orderRepo.findById("ord-1").map(Order::getState).orElseThrow() == SagaState.CANCELLED);

    inventory.verify(2, deleteRequestedFor(urlMatching("/reservations/ord-1")));
}
```

```java
@Retry(name = "compensation")
public void releaseStock(String orderId) {
    inventoryClient.release(orderId);
}
```

**Senior takeaway:** Compensating transactions fail too — saga must retry compensations with idempotent `DELETE /reservations/{orderId}`. Stuck sagas need a **reaper** job and alerting on non-terminal states > 15 min.

---

## Exercise 21 — Retry storm exhausts thread pool (Testcontainers)

**Difficulty:** Hard

**Task:** Downstream delay 2s. Client timeout 1s, retry 3×, 100 concurrent users. Hikari + Tomcat threads exhausted. Fix: timeout 300ms, retry 0 on GET, bulkhead 20, circuit breaker.

**Solution:**

```java
@Test
void retryStormExhaustsPool() throws Exception {
    wireMock.stubFor(get("/data").willReturn(aResponse().withFixedDelay(2000)));

    // broken config: retry 3, timeout 1000ms, pool 50
    ExecutorService users = Executors.newFixedThreadPool(100);
    var latch = new CountDownLatch(100);
    var errors = new AtomicInteger();
    for (int i = 0; i < 100; i++) {
        users.submit(() -> {
            try { brokenClient.fetch(); } catch (Exception e) { errors.incrementAndGet(); }
            finally { latch.countDown(); }
        });
    }
    latch.await(30, SECONDS);
    assertThat(meterRegistry.get("hikaricp.connections.active").gauge().value())
            .isGreaterThan(45); // pool saturated

    // fixed: no retry, 300ms timeout, bulkhead 20, CB
    assertThat(fixedClient.fetchBulkhead()).doesNotThrowAnyException();
}
```

```yaml
resilience4j.retry.instances.inventory.maxAttempts: 1  # no retry
resilience4j.bulkhead.instances.inventory.maxConcurrentCalls: 20
```

**Senior takeaway:** Retries multiply traffic geometrically during incidents — 100 clients × 3 retries = 400 calls to a dying service. Retry only safe/idempotent ops; never retry into saturation.

---

## Exercise 22 — Config refresh misconfiguration incident (Spring Cloud)

**Difficulty:** Hard

**Task:** `@RefreshScope` bean reads `payment.timeout-ms`. Ops updates config server value but bean holds stale 5000ms. Prove timeout unchanged until `/actuator/refresh`. Fix with `@ConfigurationProperties` record + proper refresh or restart policy.

**Solution:**

```java
@Component
@RefreshScope // footgun if not refreshed
public class StalePaymentConfig {
    @Value("${app.payment.timeout-ms}")
    private long timeoutMs;
    public long timeout() { return timeoutMs; }
}

// BETTER — immutable snapshot per startup or explicit refresh
@ConfigurationProperties(prefix = "app.payment")
public record PaymentProps(long timeoutMs) {}
```

```java
@Test
void staleConfigUntilRefresh() {
    assertThat(staleConfig.timeout()).isEqualTo(5000);
    environment.setProperty("app.payment.timeout-ms", "500");
    assertThat(staleConfig.timeout()).isEqualTo(5000); // STALE

    contextRefresher.refresh();
    assertThat(staleConfig.timeout()).isEqualTo(500); // after refresh
}
```

**Senior takeaway:** Dynamic config without deployment discipline causes "we changed the flag but nothing happened" incidents. Prefer immutable config per release; if using refresh, automate it and test `@RefreshScope` beans explicitly.

---

## Exercise 23 — Missing trace propagation on `@Async` (Testcontainers + Zipkin)

**Difficulty:** Hard

**Task:** HTTP request creates async outbox publish. Zipkin shows broken trace — child span orphaned. Fix with `ContextSnapshot` / `@Async` decorator propagating tracing context.

**Solution:**

```java
// BROKEN
@Async
public void publishAsync(OutboxEvent e) {
    kafka.send(e.topic(), e.payload()); // new traceId
}

// FIXED
@Bean
TaskDecorator tracingTaskDecorator(Tracer tracer) {
    return runnable -> {
        var current = tracer.currentTraceContext().context();
        return () -> {
            try (var scope = tracer.currentTraceContext().maybeScope(current)) {
                runnable.run();
            }
        };
    };
}

@Bean
Executor asyncExecutor(TaskDecorator tracingTaskDecorator) {
    var exec = new ThreadPoolTaskExecutor();
    exec.setTaskDecorator(tracingTaskDecorator);
    exec.initialize();
    return exec;
}
```

```java
@Test
void asyncSpanLinkedToParent(SpanExportingTest spanExporter) {
    rest.getForEntity("/orders", String.class);
    await().untilAsserted(() ->
            assertThat(spanExporter.getSpans())
                    .anyMatch(s -> s.getName().equals("kafka-send")
                            && s.getParentId() != null));
}
```

**Senior takeaway:** Every thread hop (async, Kafka listener, `CompletableFuture`) breaks traces unless you propagate context. Broken traces in prod = blind during incidents.

---

## Exercise 24 — Duplicate payment on retry (Testcontainers + Postgres)

**Difficulty:** Hard

**Task:** Client retries `POST /payments` on timeout. Without idempotency, customer charged twice. Implement idempotency + unique DB constraint on `(order_id)` where status = CAPTURED.

**Solution:**

```sql
CREATE UNIQUE INDEX uk_payment_order_captured
    ON payment (order_id) WHERE status = 'CAPTURED';
```

```java
@Transactional
public PaymentResponse capture(CaptureRequest req, String idempotencyKey) {
    var existing = idempotencyRepo.findById(idempotencyKey);
    if (existing.isPresent()) return deserialize(existing.get());

    if (paymentRepo.existsByOrderIdAndStatus(req.orderId(), CAPTURED)) {
        return paymentRepo.findByOrderId(req.orderId()).map(this::toResponse).orElseThrow();
    }

    var payment = paymentRepo.save(new Payment(req.orderId(), req.amountCents(), CAPTURED));
    idempotencyRepo.save(record(idempotencyKey, payment));
    return toResponse(payment);
}
```

```java
@Test
void duplicateRetryChargesOnce() {
    wireMock.stubFor(post("/gateway/charge")
            .willReturn(aResponse().withFixedDelay(3000))); // client times out, retries

    var headers = Map.of("Idempotency-Key", "pay-retry-1");
    Try.run(() -> client.capture(req, headers)); // timeout
    var r2 = client.capture(req, headers); // retry

    assertThat(paymentRepo.count()).isEqualTo(1);
    assertThat(r2.paymentId()).isNotNull();
}
```

**Senior takeaway:** Timeouts mean "unknown result" — client **must** retry with same idempotency key. Server must dedupe at DB constraint level, not just application check (race between two pods).

---

## Exercise 25 — Gateway timeout shorter than service chain (Testcontainers)

**Difficulty:** Hard

**Task:** Gateway timeout 3s. Order → inventory (2s) → pricing (2s) sequential = 4s. Client gets 504; backend still completes → double side effects. Fix: parallel calls, reduce timeouts, or async 202 pattern.

**Solution:**

```java
// BROKEN — sequential 4s chain behind 3s gateway
public OrderView create(CreateOrder req) {
    inventoryClient.reserve(req);  // 2s
    pricingClient.validate(req);   // 2s
    return orderRepo.save(toOrder(req));
}

// FIXED — parallel + tighter budgets
public OrderView create(CreateOrder req) {
    var reserve = CompletableFuture.runAsync(() -> inventoryClient.reserve(req));
    var price = CompletableFuture.runAsync(() -> pricingClient.validate(req));
    CompletableFuture.allOf(reserve, price).orTimeout(2, SECONDS).join();
    return orderRepo.save(toOrder(req));
}
```

```yaml
spring.cloud.gateway.httpclient.response-timeout: 5s
# per-route metadata or resilience timeouts < gateway
```

```java
@Test
void parallelChainWithinGatewayBudget() {
    inventory.stubFor(post("/reserve").willReturn(ok().withFixedDelay(1800)));
    pricing.stubFor(post("/validate").willReturn(ok().withFixedDelay(1800)));

    var response = webClient.post().uri("/api/orders").bodyValue(req).exchange();
    response.expectStatus().isCreated(); // completes ~1.8s not 3.6s
}
```

**Senior takeaway:** 504 from gateway doesn't mean backend failed — it means **client gave up**. Design for timeout ambiguity: idempotency, async status polling, or saga with correlation id.

---

## Exercise 26 — Bulkhead failure: one tenant kills all (Testcontainers)

**Difficulty:** Hard

**Task:** No bulkhead: tenant A sends 200 slow requests, tenant B's fast requests time out. Add per-tenant bulkhead (Resilience4j) or rate limit at gateway.

**Solution:**

```java
@Bean
BulkheadRegistry tenantBulkheads() {
    BulkheadConfig config = BulkheadConfig.custom()
            .maxConcurrentCalls(10)
            .maxWaitDuration(Duration.ZERO)
            .build();
    return BulkheadRegistry.of(Map.of(
            "tenant-a", config,
            "tenant-b", config
    ));
}

public Response handle(String tenantId, Request req) {
    Bulkhead bh = bulkheadRegistry.bulkhead("tenant-" + tenantId);
    return bh.executeSupplier(() -> process(req));
}
```

```java
@Test
void tenantIsolation() throws Exception {
    wireMock.stubFor(post("/work").willReturn(ok().withFixedDelay(5000)));

    // flood tenant-a
    IntStream.range(0, 50).parallel().forEach(i ->
            Try.run(() -> service.handle("a", req)));

    // tenant-b should still succeed quickly
    long ms = time(() -> service.handle("b", req));
    assertThat(ms).isLessThan(1000);
}
```

**Senior takeaway:** Fairness is a reliability requirement. Noisy neighbor on shared pools is a production outage pattern — isolate by tenant, endpoint, or priority queue.

---

## Exercise 27 — Wrong profile deploys prod credentials to staging (Testcontainers)

**Difficulty:** Hard

**Task:** `application-prod.yml` sets real payment gateway URL. Pod starts with `SPRING_PROFILES_ACTIVE=prod,staging` typo — charges real cards in QA. Fix: config validation, separate secrets, fail startup on forbidden hostnames in non-prod.

**Solution:**

```java
@Component
@Profile("!prod")
public class NonProdPaymentGuard {
    NonProdPaymentGuard(@Value("${payment.gateway-url}") String url) {
        if (url.contains("api.stripe.com") && !url.contains("sandbox")) {
            throw new IllegalStateException(
                    "Refusing to start: production payment URL in non-prod profile");
        }
    }
}
```

```yaml
# staging
payment:
  gateway-url: https://sandbox.payment.example.com

# prod — from vault/env only, never in git
```

```java
@Test
void refusesProdUrlInStagingProfile() {
    assertThatThrownBy(() -> new SpringApplicationBuilder(App.class)
            .profiles("staging")
            .properties("payment.gateway-url=https://api.stripe.com/v1")
            .run())
            .hasMessageContaining("Refusing to start");
}
```

**Senior takeaway:** Config bugs are security incidents. Validate dangerous properties at startup; use separate secret namespaces per environment; never share payment keys across profiles.

---

## Exercise 28 — Read-your-writes replica lag (Testcontainers)

**Difficulty:** Hard

**Task:** Write order to primary, immediate read from replica returns stale `PENDING` instead of `CONFIRMED`. Fix: read-after-write routing to primary for 2s or sticky session hint.

**Solution:**

```java
public class RoutingDataSource extends AbstractRoutingDataSource {
    private static final ThreadLocal<Boolean> PRIMARY = ThreadLocal.withInitial(() -> false);

    static void usePrimary() { PRIMARY.set(true); }
    static void clear() { PRIMARY.remove(); }

    @Override
    protected Object determineCurrentLookupKey() {
        return PRIMARY.get() ? "primary" : "replica";
    }
}

@Service
public class OrderQueryService {
    @Transactional(readOnly = true)
    public Order get(String id, boolean afterWrite) {
        if (afterWrite) RoutingDataSource.usePrimary();
        try {
            return orderRepo.findById(id).orElseThrow();
        } finally {
            RoutingDataSource.clear();
        }
    }
}

@RestController
class OrderController {
    @PostMapping("/orders")
    ResponseEntity<Order> create(@RequestBody CreateOrder req) {
        var order = orderService.create(req);
        return ResponseEntity.created(URI.create("/orders/" + order.id()))
                .header("X-Read-Primary", "true") // client hint
                .body(order);
    }
}
```

```java
@Test
void readAfterWriteUsesPrimary(Testcontainers Postgres primary, Postgres replica) {
    var created = rest.postForEntity("/orders", req, Order.class).getBody();
    // simulate replica lag
    Thread.sleep(100);
    var read = orderService.get(created.id(), true);
    assertThat(read.status()).isEqualTo(CONFIRMED); // not stale PENDING from replica
}
```

**Senior takeaway:** Replica routing for read scale breaks UX on read-your-writes. Route recent writes to primary (session flag, cookie, or `X-Read-Primary` header) — or accept eventual consistency in API contract.

---

## Exercise 29 — Chaos Mesh pod-kill during checkout load test

**Difficulty:** Hard

**Task:** Deploy `order-service` and `payment-service` to a local kind cluster with Litmus or Chaos Mesh installed. Run a k6 load test on `POST /checkout`. Execute `PodChaos` killing 50% of payment pods for 2 minutes. Document error rate, recovery time, and one fix if duplicates or timeouts spike.

**Solution:**

```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: PodChaos
metadata:
  name: payment-kill
  namespace: default
spec:
  action: pod-kill
  mode: fixed-percent
  value: "50"
  duration: "2m"
  selector:
    namespaces: [default]
    labelSelectors:
      app: payment-service
```

```bash
k6 run --vus 50 --duration 3m checkout-load.js
# Watch: kubectl get pods -w -l app=payment-service
# Metrics: payment_errors_total, checkout_p99_latency
```

**Abort rule:** Stop chaos if checkout 5xx rate > 5% for 60s (Prometheus alert or manual).

**Senior takeaway:** Chaos proves whether retries, idempotency keys, and HPA actually work — not whether WireMock returns 503. Always pair experiments with hypotheses and observability.

---

## Exercise 30 — Istio VirtualService canary split (local)

**Difficulty:** Intermediate

**Task:** Install Istio on kind. Deploy `pricing-service` stable and canary (v1/v2 different prices). Route 90/10 traffic via `VirtualService` + `DestinationRule` subsets. Call from a curl loop and verify ~10% responses show canary price.

**Solution:**

```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: pricing
spec:
  host: pricing-service
  subsets:
    - name: stable
      labels: { version: v1 }
    - name: canary
      labels: { version: v2 }
---
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: pricing
spec:
  hosts: [pricing-service]
  http:
    - route:
        - destination: { host: pricing-service, subset: stable }
          weight: 90
        - destination: { host: pricing-service, subset: canary }
          weight: 10
```

```bash
for i in $(seq 1 100); do curl -s pricing-service/prices/SKU1 | jq .version; done | sort | uniq -c
```

**Senior takeaway:** Mesh traffic split replaces custom load-balancer hacks; keep business logic out of Envoy — only routing weights and timeouts.

---

## Exercise 31 — Cell router tenant mapping (in-memory)

**Difficulty:** Intermediate

**Task:** Implement a `CellRouter` that maps `tenantId → cellId` from a registry. Spring filter reads JWT `tenant_id`, sets `X-Cell-Id` header, and rejects unknown tenants with 404. Unit-test that `tenant-a` routes to `cell-1`.

**Solution:**

```java
@Component
public class CellRouter {
    private final Map<String, String> tenantToCell = Map.of(
        "tenant-a", "cell-1",
        "tenant-b", "cell-2");

    public String resolveCell(String tenantId) {
        return tenantToCell.get(tenantId);
    }
}

@Component
@Order(Ordered.HIGHEST_PRECEDENCE)
class CellRoutingFilter extends OncePerRequestFilter {
    private final CellRouter router;

    @Override
    protected void doFilterInternal(HttpServletRequest req, HttpServletResponse res, FilterChain chain)
            throws ServletException, IOException {
        String tenant = extractTenant(req);
        String cell = router.resolveCell(tenant);
        if (cell == null) {
            res.sendError(HttpServletResponse.SC_NOT_FOUND, "Unknown tenant");
            return;
        }
        chain.doFilter(new CellHeaderRequestWrapper(req, cell), res);
    }
}
```

**Senior takeaway:** Cell routing belongs at the edge with a consistent registry — not hardcoded in every microservice.

---

## Exercise 32 — Pact consumer test for pricing client

**Difficulty:** Hard

**Task:** Add a Pact consumer test for `checkout-service` calling `GET /prices/{sku}`. Publish pact to a local broker (or file). Write provider verification skeleton for `pricing-service`.

**Solution:**

```java
@ExtendWith(PactConsumerTestExt.class)
@PactTestFor(providerName = "pricing-service", port = "8089")
class PricingPactConsumerTest {
    @Pact(consumer = "checkout-service")
    RequestResponsePact pact(PactDslWithProvider builder) {
        return builder
            .given("sku WIDGET-1 exists")
            .uponReceiving("fetch price")
            .path("/prices/WIDGET-1")
            .method("GET")
            .willRespondWith()
            .status(200)
            .body(new PactDslJsonBody()
                .stringType("sku", "WIDGET-1")
                .decimalType("amount"))
            .toPact();
    }

    @Test
    void fetchPrice(MockServer mockServer) {
        var client = RestClient.builder().baseUrl(mockServer.getUrl()).build();
        var body = client.get().uri("/prices/WIDGET-1").retrieve().body(PriceDto.class);
        assertThat(body.amount()).isNotNull();
    }
}
```

```bash
./gradlew pactPublish  # or pact-broker publish target/pacts
```

**Senior takeaway:** Contract tests block breaking provider changes at merge time — cheaper than Friday integration-env surprises.

---

## Exercise 33 — Modular monolith ArchUnit boundary

**Difficulty:** Intermediate

**Task:** In a multi-module Gradle project (`order`, `catalog`, `catalog-api`), add ArchUnit test: `order` must not depend on `catalog` internals — only `catalog.api`.

**Solution:**

```java
@AnalyzeClasses(packages = "com.shop")
class ModuleBoundaryTest {
    @ArchTest
    static final ArchRule order_must_not_touch_catalog_impl =
        noClasses().that().resideInAPackage("..order..")
            .should().dependOnClassesThat().resideInAPackage("..catalog..")
            .because("order uses catalog-api only");

    @ArchTest
    static final ArchRule order_may_use_catalog_api =
        classes().that().resideInAPackage("..order..")
            .should().onlyDependOnClassesThat()
            .resideInAnyPackage("..order..", "..catalog.api..", "java..", "org.springframework..");
}
```

**Senior takeaway:** ArchUnit turns modular monolith boundaries into CI failures — the escape hatch for later HTTP extraction.

---

## Weekend drill

1. Implement the full order saga with outbox + compensation; kill payment mid-flow and prove stock released.
2. Add Micrometer Tracing end-to-end (gateway → order → inventory) and find one broken async span.
3. Load-test with 100 concurrent users against a failing downstream; tune circuit breaker until p99 < 500ms.
4. Write your event catalog and bring it to your next system design interview.
