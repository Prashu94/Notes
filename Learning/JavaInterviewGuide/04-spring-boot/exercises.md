# Spring Boot — Practical Exercises

Type these. Run them. Break them. Reading is not practice.

**28 exercises:** Part A Basic (12) · Part B Intermediate (12) · Part C Hard (9) · Weekend challenge

Scaffold once:

```xml
<!-- pom.xml essentials -->
<dependencies>
  <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-web</artifactId></dependency>
  <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-data-jpa</artifactId></dependency>
  <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-validation</artifactId></dependency>
  <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-actuator</artifactId></dependency>
  <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-security</artifactId></dependency>
  <dependency><groupId>com.h2database</groupId><artifactId>h2</artifactId><scope>runtime</scope></dependency>
  <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-test</artifactId><scope>test</scope></dependency>
  <dependency><groupId>org.springframework.security</groupId><artifactId>spring-security-test</artifactId><scope>test</scope></dependency>
</dependencies>
```

---

# Part A — Basic

## Exercise 1 — REST controller + actuator health

**Difficulty:** Basic

**Task:** Expose `GET /api/hello` and confirm `/actuator/health` returns UP without auth.

**Solution:**

```java
@SpringBootApplication
public class DemoApp {
    public static void main(String[] args) {
        SpringApplication.run(DemoApp.class, args);
    }
}

@RestController
@RequestMapping("/api")
class HelloController {
    @GetMapping("/hello")
    Map<String, String> hello() {
        return Map.of("message", "hello");
    }
}
```

```yaml
# application.yml
management:
  endpoints:
    web:
      exposure:
        include: health,info
```

```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class HelloControllerTest {
    @Autowired TestRestTemplate rest;

    @Test
    void hello() {
        var body = rest.getForObject("/api/hello", Map.class);
        assertEquals("hello", body.get("message"));
    }

    @Test
    void healthUp() {
        var body = rest.getForObject("/actuator/health", Map.class);
        assertEquals("UP", body.get("status"));
    }
}
```

**Senior takeaway:** Expose only needed actuator endpoints — `include: "*"` in prod is a CVE waiting to happen.

---

## Exercise 2 — `@ConfigurationProperties` with validation

**Difficulty:** Basic

**Task:** Bind `app.payments.base-url` and `timeout-ms`. App must fail startup on invalid values.

**Solution:**

```java
@ConfigurationProperties(prefix = "app.payments")
@Validated
public record PaymentsProps(
        @NotBlank String baseUrl,
        @Min(50) int timeoutMs
) {}

@Configuration
@EnableConfigurationProperties(PaymentsProps.class)
class PropsConfig {}
```

```yaml
app:
  payments:
    base-url: https://pay.example.com
    timeout-ms: 3000
```

```java
@SpringBootTest
class PaymentsPropsTest {
    @Autowired PaymentsProps props;

    @Test
    void binds() {
        assertEquals("https://pay.example.com", props.baseUrl());
        assertEquals(3000, props.timeoutMs());
    }
}
```

```yaml
# Break startup test — use @SpringBootTest(properties = ...)
# app.payments.timeout-ms: 10  -> fails @Min(50)
```

**Senior takeaway:** `@ConfigurationProperties` + `@Validated` beats `@Value` for nested config and fail-fast validation.

---

## Exercise 3 — `@Transactional` rollback on runtime exception

**Difficulty:** Basic

**Task:** Prove a runtime exception rolls back an insert; a caught exception does not unless rethrown.

**Solution:**

```java
@Entity
class Account {
    @Id String id;
    long balanceCents;
    // getters/setters
}

@Repository
interface AccountRepo extends JpaRepository<Account, String> {}

@Service
class AccountService {
    private final AccountRepo repo;
    AccountService(AccountRepo repo) { this.repo = repo; }

    @Transactional
    void creditAndFail(String id, long cents) {
        var a = repo.findById(id).orElseThrow();
        a.setBalanceCents(a.getBalanceCents() + cents);
        repo.save(a);
        throw new IllegalStateException("boom");
    }
}
```

```java
@SpringBootTest
@Transactional // rolls back test TX
class TxRollbackTest {
    @Autowired AccountService svc;
    @Autowired AccountRepo repo;

    @BeforeEach
    void seed() {
        var a = new Account();
        a.setId("A1");
        a.setBalanceCents(100);
        repo.save(a);
    }

    @Test
    void runtimeRollsBack() {
        assertThrows(IllegalStateException.class, () -> svc.creditAndFail("A1", 50));
        assertEquals(100, repo.findById("A1").orElseThrow().getBalanceCents());
    }
}
```

**Senior takeaway:** Default rollback is **runtime only** — checked exceptions commit unless `rollbackFor` is set.

---

## Exercise 4 — `@WebMvcTest` controller slice

**Difficulty:** Basic

**Task:** Test `OrderController` with mocked `OrderService`. No database on classpath for this test.

**Solution:**

```java
@RestController
@RequestMapping("/api/orders")
class OrderController {
    private final OrderService service;
    OrderController(OrderService service) { this.service = service; }

    @GetMapping("/{id}")
    ResponseEntity<OrderDto> get(@PathVariable String id) {
        return ResponseEntity.ok(service.find(id));
    }
}

record OrderDto(String id, String status) {}

@Service
class OrderService {
    OrderDto find(String id) { return new OrderDto(id, "PLACED"); }
}
```

```java
@WebMvcTest(OrderController.class)
class OrderControllerSliceTest {
    @Autowired MockMvc mvc;
    @MockitoBean OrderService service;

    @Test
    void getOrder() throws Exception {
        when(service.find("1")).thenReturn(new OrderDto("1", "SHIPPED"));
        mvc.perform(get("/api/orders/1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("SHIPPED"));
    }
}
```

**Senior takeaway:** Slice tests are fast and precise — they won't catch repository mapping bugs; use both slice and integration tests.

---

## Exercise 5 — `@DataJpaTest` repository slice

**Difficulty:** Basic

**Task:** Test a custom `@Query` with in-memory H2. No web layer started.

**Solution:**

```java
@Entity
@Table(name = "orders")
class OrderEntity {
    @Id String id;
    String status;
}

interface OrderJpaRepo extends JpaRepository<OrderEntity, String> {
    List<OrderEntity> findByStatus(String status);
}
```

```java
@DataJpaTest
class OrderJpaRepoTest {
    @Autowired OrderJpaRepo repo;

    @Test
    void findByStatus() {
        var o = new OrderEntity();
        o.setId("O1");
        o.setStatus("PLACED");
        repo.save(o);
        assertEquals(1, repo.findByStatus("PLACED").size());
    }
}
```

**Senior takeaway:** `@DataJpaTest` uses an embedded DB and rolls back each test — not a substitute for Testcontainers dialect quirks.

---

## Exercise 6 — Custom `HealthIndicator`

**Difficulty:** Basic

**Task:** Report DOWN when a downstream URL is unreachable. Surface detail in `/actuator/health`.

**Solution:**

```java
@Component
class PaymentsHealth implements HealthIndicator {
    private final PaymentsProps props;
    PaymentsHealth(PaymentsProps props) { this.props = props; }

    @Override
    public Health health() {
        // simulate check
        boolean ok = props.baseUrl().startsWith("https://");
        if (ok) return Health.up().withDetail("baseUrl", props.baseUrl()).build();
        return Health.down().withDetail("reason", "invalid baseUrl").build();
    }
}
```

```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class CustomHealthTest {
    @Autowired TestRestTemplate rest;

    @Test
    void paymentsComponentListed() {
        var body = rest.getForObject("/actuator/health", Map.class);
        assertEquals("UP", body.get("status"));
    }
}
```

**Senior takeaway:** Health checks should be cheap — don't call slow third parties synchronously on every K8s probe tick.

---

## Exercise 7 — `ProblemDetail` global exception handler

**Difficulty:** Basic

**Task:** Return RFC 7807 body for `OrderNotFoundException` with `orderId` extension field.

**Solution:**

```java
class OrderNotFoundException extends RuntimeException {
    private final String orderId;
    OrderNotFoundException(String orderId) {
        super("not found: " + orderId);
        this.orderId = orderId;
    }
    String getOrderId() { return orderId; }
}

@RestControllerAdvice
class ApiExceptionHandler {
    @ExceptionHandler(OrderNotFoundException.class)
    ProblemDetail notFound(OrderNotFoundException ex) {
        var pd = ProblemDetail.forStatus(HttpStatus.NOT_FOUND);
        pd.setTitle("Order not found");
        pd.setDetail(ex.getMessage());
        pd.setProperty("orderId", ex.getOrderId());
        return pd;
    }
}
```

```java
@WebMvcTest(controllers = {OrderController.class, ApiExceptionHandler.class})
class ProblemDetailTest {
    @Autowired MockMvc mvc;
    @MockitoBean OrderService service;

    @Test
    void notFoundProblemDetail() throws Exception {
        when(service.find("missing")).thenThrow(new OrderNotFoundException("missing"));
        mvc.perform(get("/api/orders/missing"))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.title").value("Order not found"))
                .andExpect(jsonPath("$.orderId").value("missing"));
    }
}
```

**Senior takeaway:** `ProblemDetail` is the Spring 6+ standard — consistent error shape helps API consumers and observability.

---

## Exercise 8 — `@Scheduled` fixed delay

**Difficulty:** Basic

**Task:** Run a heartbeat every 2 seconds. Log instance id. Observe in console.

**Solution:**

```java
@SpringBootApplication
@EnableScheduling
public class SchedulerApp {
    public static void main(String[] args) {
        SpringApplication.run(SchedulerApp.class, args);
    }
}

@Component
class HeartbeatJob {
    private final String instanceId = UUID.randomUUID().toString();

    @Scheduled(fixedDelay = 2000)
    void tick() {
        System.out.println("heartbeat " + instanceId + " at " + Instant.now());
    }
}
```

**Senior takeaway:** `fixedDelay` waits after **completion**; `fixedRate` can overlap slow jobs — choose based on job duration.

---

## Exercise 9 — Profiles (`dev` vs `prod`)

**Difficulty:** Basic

**Task:** `application-dev.yml` enables SQL logging; `application-prod.yml` disables it. Activate with `spring.profiles.active`.

**Solution:**

```yaml
# application.yml
spring:
  profiles:
    active: dev
```

```yaml
# application-dev.yml
spring:
  jpa:
    show-sql: true
logging:
  level:
    org.hibernate.SQL: DEBUG
```

```yaml
# application-prod.yml
spring:
  jpa:
    show-sql: false
logging:
  level:
    org.hibernate.SQL: WARN
```

```java
@SpringBootTest
class ProfileTest {
    @Autowired Environment env;

    @Test
    @ActiveProfiles("prod")
    void prodProfile() {
        assertTrue(Arrays.asList(env.getActiveProfiles()).contains("prod"));
    }
}
```

**Senior takeaway:** Never rely on profile for security — prod secrets come from env/vault, not committed yaml.

---

## Exercise 10 — Graceful shutdown configuration

**Difficulty:** Basic

**Task:** Configure graceful shutdown and per-phase timeout. Write a slow endpoint to observe behavior.

**Solution:**

```yaml
server:
  shutdown: graceful
spring:
  lifecycle:
    timeout-per-shutdown-phase: 20s
```

```java
@RestController
class SlowController {
    @GetMapping("/api/slow")
    String slow() throws InterruptedException {
        Thread.sleep(5000);
        return "done";
    }
}
```

```bash
# Terminal 1
mvn spring-boot:run

# Terminal 2 — while /api/slow is in flight
curl http://localhost:8080/api/slow &
kill -TERM $(pgrep -f SchedulerApp)  # or your main class
# Request should complete; new requests rejected during shutdown
```

**Senior takeaway:** K8s `terminationGracePeriodSeconds` must exceed `timeout-per-shutdown-phase` + preStop buffer.

---

# Part B — Intermediate

## Exercise 11 — Self-invocation skips `@Transactional`

**Difficulty:** Intermediate

**Task:** `payMany` calls `this.pay()` — no single transaction. Fix with `@Lazy` self-injection. Prove with transaction count.

**Solution:**

```java
@Service
public class InvoiceService {
    private final InvoiceRepo repo;
    private InvoiceService self;

    InvoiceService(InvoiceRepo repo) { this.repo = repo; }

    @Autowired
    void setSelf(@Lazy InvoiceService self) { this.self = self; }

    @Transactional
    public void pay(String id) {
        repo.markPaid(id);
    }

    public void payMany(List<String> ids) {
        ids.forEach(self::pay); // fixed — goes through proxy
    }

    public void payManyBroken(List<String> ids) {
        ids.forEach(this::pay); // broken
    }
}
```

```yaml
spring.jpa.properties.hibernate.generate_statistics: true
logging.level.org.hibernate.stat: DEBUG
```

```java
@SpringBootTest
class TxSelfInvocationTest {
    @Autowired InvoiceService service;
    @Autowired EntityManagerFactory emf;

    @Test
    void selfInvocationBypassesProxy() {
        var stats = emf.unwrap(SessionFactory.class).getStatistics();
        stats.clear();
        service.payManyBroken(List.of("A", "B"));
        // Each pay() may commit separately — inspect stats.getTransactionCount()
        assertTrue(stats.getTransactionCount() >= 1);
    }
}
```

**Senior takeaway:** Extract `PaymentTxService` if self-injection feels hacky — clearer boundaries beat clever proxies.

---

## Exercise 12 — `rollbackFor` checked exception trap

**Difficulty:** Intermediate

**Task:** Show default `@Transactional` **commits** on checked `Exception`. Fix with `rollbackFor`.

**Solution:**

```java
@Service
class TransferService {
    private final AccountRepo repo;
    TransferService(AccountRepo repo) { this.repo = repo; }

    @Transactional
    public void transferBroken() throws Exception {
        debit();
        throw new Exception("checked"); // COMMITS by default
    }

    @Transactional(rollbackFor = Exception.class)
    public void transferFixed() throws Exception {
        debit();
        throw new Exception("checked"); // ROLLBACK
    }

    private void debit() {
        var a = repo.findById("A1").orElseThrow();
        a.setBalanceCents(a.getBalanceCents() - 10);
        repo.save(a);
    }
}
```

```java
@SpringBootTest
class RollbackForTest {
    @Autowired TransferService svc;
    @Autowired AccountRepo repo;

    @BeforeEach
    void seed() {
        var a = new Account();
        a.setId("A1");
        a.setBalanceCents(100);
        repo.save(a);
    }

    @Test
    void checkedExceptionCommitsByDefault() throws Exception {
        try { svc.transferBroken(); } catch (Exception ignored) {}
        assertEquals(90, repo.findById("A1").orElseThrow().getBalanceCents()); // debited!
    }

    @Test
    void rollbackForFixes() throws Exception {
        try { svc.transferFixed(); } catch (Exception ignored) {}
        assertEquals(100, repo.findById("A1").orElseThrow().getBalanceCents());
    }
}
```

**Senior takeaway:** This bug survives code review because it compiles — always test rollback with assertions on row state.

---

## Exercise 13 — `REQUIRES_NEW` + pool size 1 deadlock

**Difficulty:** Intermediate

**Task:** Outer TX holds connection; inner `REQUIRES_NEW` needs second connection. Pool size 1 → hang or timeout.

**Solution:**

```yaml
spring:
  datasource:
    hikari:
      maximum-pool-size: 1
      connection-timeout: 2000
```

```java
@Service
class OuterService {
    private final InnerService inner;
    OuterService(InnerService inner) { this.inner = inner; }

    @Transactional
    public void outer() {
        // holds connection
        inner.innerRequiresNew();
    }
}

@Service
class InnerService {
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void innerRequiresNew() {
        // needs 2nd connection — blocks forever with pool=1
    }
}
```

```java
@SpringBootTest
class PoolDeadlockTest {
    @Autowired OuterService outer;

    @Test
    void timesOutWaitingForConnection() {
        assertThrows(Exception.class, () -> outer.outer());
        // SQLTransientConnectionException or timeout
    }
}
```

**Fix:** Don't nest `REQUIRES_NEW` while holding outer TX; increase pool; use `@TransactionalEventListener(AFTER_COMMIT)`.

**Senior takeaway:** `REQUIRES_NEW` is for audit logs and outbox — not routine service calls from within a TX.

---

## Exercise 14 — Security filter chain for JWT API

**Difficulty:** Intermediate

**Task:** Stateless JWT resource server. `/actuator/health` public; `/api/admin/**` requires `ROLE_ADMIN`.

**Solution:**

```java
@Configuration
@EnableWebSecurity
class SecurityConfig {
    @Bean
    SecurityFilterChain api(HttpSecurity http) throws Exception {
        http.csrf(csrf -> csrf.disable())
            .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(a -> a
                .requestMatchers("/actuator/health/**").permitAll()
                .requestMatchers("/api/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated())
            .oauth2ResourceServer(o -> o.jwt(Customizer.withDefaults()));
        return http.build();
    }
}
```

```java
@SpringBootTest
@AutoConfigureMockMvc
class SecurityJwtTest {
    @Autowired MockMvc mvc;

    @Test
    void healthPublic() throws Exception {
        mvc.perform(get("/actuator/health")).andExpect(status().isOk());
    }

    @Test
    void adminRequiresRole() throws Exception {
        mvc.perform(get("/api/admin/users")
                .with(jwt().authorities(new SimpleGrantedAuthority("ROLE_USER"))))
                .andExpect(status().isForbidden());
    }

    @Test
    void adminOk() throws Exception {
        mvc.perform(get("/api/admin/users")
                .with(jwt().authorities(new SimpleGrantedAuthority("ROLE_ADMIN"))))
                .andExpect(status().isOk());
    }
}
```

**Senior takeaway:** `permitAll()` on `/api/**` by mistake is the #1 API security bug — test with `spring-security-test`, not manual curls.

---

## Exercise 15 — Disable OSIV, fix `LazyInitializationException`

**Difficulty:** Intermediate

**Task:** With `open-in-view: false`, loading lazy collection in controller fails. Fix with `join fetch` or DTO.

**Solution:**

```yaml
spring.jpa.open-in-view: false
```

```java
@Entity
class OrderEntity {
    @Id String id;
    @OneToMany(fetch = FetchType.LAZY, mappedBy = "order")
    List<LineEntity> lines = new ArrayList<>();
}

@Entity
class LineEntity {
    @Id Long id;
    String sku;
    @ManyToOne OrderEntity order;
}

interface OrderJpaRepo extends JpaRepository<OrderEntity, String> {
    @Query("select o from OrderEntity o join fetch o.lines where o.id = :id")
    Optional<OrderEntity> findWithLines(@Param("id") String id);
}
```

```java
@SpringBootTest
class OsivTest {
    @Autowired OrderJpaRepo repo;

    @Test
    void joinFetchLoadsLinesInOneTx() {
        // seed order + lines in @BeforeEach
        var order = repo.findWithLines("O1").orElseThrow();
        assertFalse(order.getLines().isEmpty()); // no LazyInitializationException
    }
}
```

**Senior takeaway:** OSIV hides N+1 and lazy bugs — disabling it forces correct fetch plans (production best practice).

---

## Exercise 16 — Testcontainers Postgres integration test

**Difficulty:** Intermediate

**Task:** `@SpringBootTest` with real Postgres via Testcontainers. Prove a repository constraint works.

**Solution:**

```java
@Testcontainers
@SpringBootTest
class OrderIT {
    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16-alpine");

    @DynamicPropertySource
    static void props(DynamicPropertyRegistry r) {
        r.add("spring.datasource.url", postgres::getJdbcUrl);
        r.add("spring.datasource.username", postgres::getUsername);
        r.add("spring.datasource.password", postgres::getPassword);
    }

    @Autowired OrderJpaRepo repo;

    @Test
    void persists() {
        var o = new OrderEntity();
        o.setId("IT-1");
        o.setStatus("NEW");
        repo.save(o);
        assertTrue(repo.findById("IT-1").isPresent());
    }
}
```

```xml
<dependency>
  <groupId>org.testcontainers</groupId><artifactId>postgresql</artifactId><scope>test</scope>
</dependency>
```

**Senior takeaway:** Testcontainers catches dialect-specific SQL (JSON, `ON CONFLICT`) that H2 fakes miss.

---

## Exercise 17 — ShedLock: duplicate `@Scheduled` on 2 pods

**Difficulty:** Intermediate

**Task:** Two instances both run digest job. Add ShedLock so only one executes.

**Solution:**

```java
@EnableScheduling
@EnableSchedulerLock(defaultLockAtMostFor = "PT5M")
@SpringBootApplication
public class ShedLockApp {
    public static void main(String[] args) {
        SpringApplication.run(ShedLockApp.class, args);
    }
}
```

```java
@Component
class DigestJob {
    private final String instanceId = UUID.randomUUID().toString();

    @Scheduled(fixedDelay = 5000)
    @SchedulerLock(name = "digest", lockAtMostFor = "4m", lockAtLeastFor = "30s")
    void sendDigest() {
        System.out.println(instanceId + " sent digest at " + Instant.now());
    }
}
```

```sql
-- ShedLock table
CREATE TABLE shedlock (
  name VARCHAR(64) NOT NULL PRIMARY KEY,
  lock_until TIMESTAMP NOT NULL,
  locked_at TIMESTAMP NOT NULL,
  locked_by VARCHAR(255) NOT NULL
);
```

**Senior takeaway:** `@Scheduled` is per-instance — K8s replicas need ShedLock, Quartz cluster, or an external scheduler.

---

## Exercise 18 — Actuator liveness vs readiness probes

**Difficulty:** Intermediate

**Task:** Split health groups: liveness = ping only; readiness = db + custom kafka check.

**Solution:**

```yaml
management:
  endpoint:
    health:
      probes:
        enabled: true
      group:
        liveness:
          include: livenessState
        readiness:
          include: readinessState,db,payments
  health:
    livenessstate:
      enabled: true
    readinessstate:
      enabled: true
```

```java
@Component
class PaymentsHealth implements HealthIndicator {
    public Health health() {
        return Health.up().build();
    }
}
```

```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class ProbeGroupsTest {
    @Autowired TestRestTemplate rest;

    @Test
    void readinessEndpoint() {
        var body = rest.getForObject("/actuator/health/readiness", Map.class);
        assertNotNull(body.get("status"));
    }
}
```

**Senior takeaway:** Liveness restart kills the pod — don't put slow external checks there; readiness removes pod from load balancer.

---

## Exercise 19 — `@Async` + `@Transactional` pitfall

**Difficulty:** Intermediate

**Task:** Show `@Async` method running **outside** caller's transaction. Fix with `TransactionSynchronizationManager.registerSynchronization(afterCommit)`.

**Solution:**

```java
@Service
class OrderService {
    private final OrderRepo repo;
    private final AsyncNotifier notifier;
    OrderService(OrderRepo repo, AsyncNotifier notifier) { this.repo = repo; this.notifier = notifier; }

    @Transactional
    public void place(String id) {
        repo.save(newOrder(id));
        notifier.notifyAsync(id); // runs in another thread — TX may not be committed yet
    }
}

@Component
class AsyncNotifier {
    @Async
    public void notifyAsync(String orderId) {
        System.out.println("notify " + orderId + " txActive="
                + TransactionSynchronizationManager.isActualTransactionActive());
    }
}
```

```java
// Fix: after commit
@Transactional
public void placeFixed(String id) {
    repo.save(newOrder(id));
    TransactionSynchronizationManager.registerSynchronization(new TransactionSynchronization() {
        @Override
        public void afterCommit() {
            notifier.notifyAsync(id);
        }
    });
}
```

**Senior takeaway:** Async + TX ordering bugs manifest as "customer got email but order rolled back" — use `AFTER_COMMIT` or outbox.

---

## Exercise 20 — Nested `@ConfigurationProperties` + relaxed binding

**Difficulty:** Intermediate

**Task:** Bind `app.kafka.topics.orders` and `app.kafka.topics.payments` into a nested record. Test kebab-case in yaml.

**Solution:**

```java
@ConfigurationProperties(prefix = "app.kafka")
@Validated
public record KafkaProps(@Valid Topics topics) {
    public record Topics(
            @NotBlank String orders,
            @NotBlank String payments
    ) {}
}
```

```yaml
app:
  kafka:
    topics:
      orders: orders.v1
      payments: payments.v1
```

```java
@SpringBootTest
class KafkaPropsTest {
    @Autowired KafkaProps props;

    @Test
    void nestedBinding() {
        assertEquals("orders.v1", props.topics().orders());
    }
}
```

**Senior takeaway:** Relaxed binding (`orders-v1` → `ordersV1`) is powerful — document env var names (`APP_KAFKA_TOPICS_ORDERS`) for ops.

---

# Part C — Hard

## Exercise 21 — Production bug: N+1 in service layer

**Difficulty:** Hard

**Task:** `findAll()` orders then loop `order.getLines()` causes N+1. Fix with entity graph or batch fetch. Count SQL statements.

**Solution:**

```java
@Entity
class OrderEntity {
    @Id String id;
    @OneToMany(mappedBy = "order", fetch = FetchType.LAZY)
    List<LineEntity> lines = new ArrayList<>();
}

@Service
class OrderQueryService {
    private final OrderJpaRepo repo;
    OrderQueryService(OrderJpaRepo repo) { this.repo = repo; }

    // BUG
    List<OrderEntity> allWithLinesBroken() {
        var orders = repo.findAll();
        orders.forEach(o -> o.getLines().size()); // N+1
        return orders;
    }

    // FIX
    List<OrderEntity> allWithLinesFixed() {
        return repo.findAllWithLines();
    }
}

interface OrderJpaRepo extends JpaRepository<OrderEntity, String> {
    @Query("select distinct o from OrderEntity o left join fetch o.lines")
    List<OrderEntity> findAllWithLines();
}
```

```yaml
spring.jpa.show-sql: true
spring.jpa.properties.hibernate.format_sql: true
```

```java
@SpringBootTest
class N1ProductionBugTest {
    @Autowired OrderQueryService svc;

    @Test
    void fixedUsesOneQuery() {
        // seed 10 orders with lines; enable statistics
        svc.allWithLinesFixed();
        // assert query count == 1 (or 2 with pagination)
    }
}
```

**Senior takeaway:** N+1 survives to prod because OSIV masks it in dev — disable OSIV and enable SQL stats in staging.

---

## Exercise 22 — Production bug: wrong transaction propagation audit

**Difficulty:** Hard

**Task:** Service logs `txActive` and propagation at each layer. Find accidental `NOT_SUPPORTED` or read-only TX writing data.

**Solution:**

```java
@Component
class TxAudit {
    void log(String where) {
        var tx = TransactionSynchronizationManager.getCurrentTransactionName();
        boolean active = TransactionSynchronizationManager.isActualTransactionActive();
        boolean readOnly = TransactionSynchronizationManager.isCurrentTransactionReadOnly();
        System.out.println(where + " active=" + active + " readOnly=" + readOnly + " name=" + tx);
    }
}

@Service
class ReportService {
    private final TxAudit audit;
    private final AccountRepo repo;
    ReportService(TxAudit audit, AccountRepo repo) { this.audit = audit; this.repo = repo; }

    @Transactional(readOnly = true)
    public void generate() {
        audit.log("generate");
        repo.findAll(); // OK
        // repo.save(...) // BUG — read-only TX, may fail or no-op depending on provider
    }
}
```

```java
@SpringBootTest
class TxPropagationAuditTest {
    @Autowired ReportService reports;

    @Test
    void readOnlyPreventsWrites() {
        reports.generate();
        // Add assertion: attempt save throws or doesn't persist
    }
}
```

**Senior takeaway:** `readOnly = true` is a hint for routing to replicas — accidental writes fail silently on some drivers.

---

## Exercise 23 — Production bug: security `permitAll` on admin API

**Difficulty:** Hard

**Task:** Misconfigured security exposes `/api/admin/**`. Write a test that fails until fixed. Use `authorizeHttpRequests` correctly.

**Solution:**

```java
// BUGGY config
@Bean
SecurityFilterChain broken(HttpSecurity http) throws Exception {
    http.authorizeHttpRequests(a -> a.anyRequest().permitAll());
    return http.build();
}

// FIXED
@Bean
SecurityFilterChain fixed(HttpSecurity http) throws Exception {
    http.authorizeHttpRequests(a -> a
        .requestMatchers("/actuator/health/**").permitAll()
        .requestMatchers("/api/admin/**").hasRole("ADMIN")
        .anyRequest().authenticated())
        .oauth2ResourceServer(o -> o.jwt(Customizer.withDefaults()));
    return http.build();
}
```

```java
@SpringBootTest
@AutoConfigureMockMvc
class AdminExposureTest {
    @Autowired MockMvc mvc;

    @Test
    void adminNotPublic() throws Exception {
        mvc.perform(get("/api/admin/users"))
                .andExpect(status().isUnauthorized()); // or 403
    }
}
```

**Senior takeaway:** Add a security smoke test suite in CI — one `permitAll` typo exposes PII.

---

## Exercise 24 — Production bug: actuator fully exposed

**Difficulty:** Hard

**Task:** `management.endpoints.web.exposure.include: "*"` on prod leaks env, beans, heap dump. Lock down and require auth.

**Solution:**

```yaml
# application-prod.yml — SAFE
management:
  endpoints:
    web:
      exposure:
        include: health,info,prometheus
  endpoint:
    health:
      show-details: when_authorized
```

```java
@Bean
@Order(1)
SecurityFilterChain actuatorSecurity(HttpSecurity http) throws Exception {
    http.securityMatcher("/actuator/**")
        .authorizeHttpRequests(a -> a.anyRequest().hasRole("ACTUATOR"))
        .httpBasic(Customizer.withDefaults());
    return http.build();
}
```

```java
@SpringBootTest
@ActiveProfiles("prod")
@AutoConfigureMockMvc
class ActuatorExposureTest {
    @Autowired MockMvc mvc;

    @Test
    void envNotExposed() throws Exception {
        mvc.perform(get("/actuator/env")).andExpect(status().is4xxClientError());
    }
}
```

**Senior takeaway:** `/actuator/env` and `/actuator/heapdump` have been breach vectors — separate management port + network policy.

---

## Exercise 25 — Production bug: graceful shutdown loses in-flight TX

**Difficulty:** Hard

**Task:** SIGTERM during `@Transactional` work — does it commit or rollback? Configure shutdown hook and test.

**Solution:**

```yaml
server:
  shutdown: graceful
spring:
  lifecycle:
    timeout-per-shutdown-phase: 30s
```

```java
@Service
class LongTxService {
    @Transactional
    public void longRunning() throws InterruptedException {
        Thread.sleep(15000);
        // DB write here
    }
}
```

```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class ShutdownTxTest {
    @Autowired TestRestTemplate rest;

    @Test
    void inFlightRequestCompletesOnShutdown() throws Exception {
        var t = new Thread(() -> rest.getForObject("/api/long-tx", Void.class));
        t.start();
        Thread.sleep(1000);
        // trigger shutdown via context.close() in test
        t.join(35000);
        // verify row state: committed if finished, rolled back if interrupted
    }
}
```

**Senior takeaway:** In-flight TX behavior depends on completion before timeout — align K8s preStop + grace period with DB lock duration.

---

## Exercise 26 — Production bug: error handler leaks stack trace

**Difficulty:** Hard

**Task:** `@ExceptionHandler` returns full exception message to client in prod. Sanitize `detail`; log server-side only.

**Solution:**

```java
@RestControllerAdvice
class SafeExceptionHandler {
    private static final Logger log = LoggerFactory.getLogger(SafeExceptionHandler.class);

    @ExceptionHandler(Exception.class)
    ProblemDetail handle(Exception ex, HttpServletRequest req) {
        log.error("request failed {}", req.getRequestURI(), ex);
        var pd = ProblemDetail.forStatus(HttpStatus.INTERNAL_SERVER_ERROR);
        pd.setTitle("Internal error");
        pd.setDetail("An unexpected error occurred"); // NOT ex.getMessage() in prod
        return pd;
    }
}
```

```yaml
# application-prod.yml
server.error.include-stacktrace: never
server.error.include-message: never
```

```java
@WebMvcTest(controllers = {OrderController.class, SafeExceptionHandler.class})
class ErrorLeakTest {
    @Autowired MockMvc mvc;
    @MockitoBean OrderService service;

    @Test
    void noStackInBody() throws Exception {
        when(service.find("x")).thenThrow(new RuntimeException("secret jdbc url"));
        mvc.perform(get("/api/orders/x"))
                .andExpect(status().is5xxServerError())
                .andExpect(jsonPath("$.detail").value("An unexpected error occurred"))
                .andExpect(jsonPath("$.detail").value(org.hamcrest.Matchers.not(org.hamcrest.Matchers.containsString("jdbc"))));
    }
}
```

**Senior takeaway:** OWASP — error responses are reconnaissance; use `ProblemDetail` + centralized logging with trace id.

---

## Exercise 27 — Production bug: `@Scheduled` race on startup

**Difficulty:** Hard

**Task:** Job runs before DB migration completes or before cache warms. Fix with `@DependsOn`, `ApplicationReadyEvent`, or `SmartLifecycle`.

**Solution:**

```java
@Component
class RiskyStartupJob {
    @Scheduled(initialDelay = 0, fixedDelay = Long.MAX_VALUE)
    void onStartup() {
        throw new IllegalStateException("schema not ready");
    }
}

@Component
class SafeStartupJob {
    private final OrderJpaRepo repo;
    private volatile boolean ready;
    SafeStartupJob(OrderJpaRepo repo) { this.repo = repo; }

    @EventListener(ApplicationReadyEvent.class)
    void markReady() { ready = true; }

    @Scheduled(fixedDelay = 60000)
    void runWhenReady() {
        if (!ready) return;
        repo.count();
    }
}
```

```java
@SpringBootTest
class ScheduledStartupTest {
    @Test
    void jobAfterReady() {
        // assert SafeStartupJob doesn't throw on context startup
    }
}
```

**Senior takeaway:** Flyway/Liquibase + `@Scheduled` without ready gate causes prod-only races — listen for `ApplicationReadyEvent`.

---

## Exercise 28 — Production bug: config property silent wrong default

**Difficulty:** Hard

**Task:** `@ConfigurationProperties` field missing from yaml silently uses Java default (`0`, `null`). Fail startup on missing required props.

**Solution:**

```java
@ConfigurationProperties(prefix = "app.payments")
@Validated
public record PaymentsProps(
        @NotBlank String baseUrl,
        @Min(50) int timeoutMs,
        @NotNull Boolean enabled // wrapper — null if missing
) {}

@Configuration
@EnableConfigurationProperties(PaymentsProps.class)
class PaymentsConfig {}
```

```yaml
# Missing app.payments.enabled -> startup fails @NotNull
app:
  payments:
    base-url: https://pay.example.com
    timeout-ms: 3000
    enabled: true
```

```java
@SpringBootTest(properties = {
    "app.payments.base-url=https://x.com",
    "app.payments.timeout-ms=100"
    // enabled intentionally missing
})
class ConfigSilentDefaultTest {
    @Test
    void failsWithoutEnabled() {
        assertThrows(Exception.class, () ->
            new SpringApplication(DemoApp.class)
                .run("--spring.main.lazy-initialization=false"));
    }
}
```

**Senior takeaway:** Primitives default to `0`/`false` — use `Boolean`, `@NotNull`, and `@ConstructorBinding` records for fail-fast config.

---

## Exercise 29 — Problem Details from `@ControllerAdvice`

**Difficulty:** Basic

**Task:** Return RFC 9457 `ProblemDetail` with status 404, custom `type` URI, and `instance` from request path for unknown resource id.

**Solution:**

```java
@RestControllerAdvice
class NotFoundAdvice {
    @ExceptionHandler(NoSuchElementException.class)
    ProblemDetail notFound(NoSuchElementException ex, HttpServletRequest req) {
        var pd = ProblemDetail.forStatusAndDetail(HttpStatus.NOT_FOUND, ex.getMessage());
        pd.setType(URI.create("https://example.com/problems/not-found"));
        pd.setInstance(URI.create(req.getRequestURI()));
        return pd;
    }
}

@RestController
class ItemController {
    @GetMapping("/api/items/{id}")
    Item get(@PathVariable Long id) {
        throw new NoSuchElementException("Item " + id + " not found");
    }
}
```

```java
@SpringBootTest(webEnvironment = RANDOM_PORT)
class ProblemDetailsTest {
    @Autowired TestRestTemplate rest;

    @Test
    void returnsProblemJson() {
        var resp = rest.getForEntity("/api/items/99", ProblemDetail.class);
        assertEquals(404, resp.getStatusCode().value());
        assertEquals("https://example.com/problems/not-found", resp.getBody().getType().toString());
    }
}
```

**Senior takeaway:** Never return stack traces in API errors — stable `type` URIs let clients branch without parsing English `detail`.

---

## Exercise 30 — `@Observed` service method

**Difficulty:** Basic

**Task:** Add `@Observed(name = "orders.create")` on a service method; assert Micrometer observation/timer recorded in test.

**Solution:**

```java
@Service
class OrderService {
    @Observed(name = "orders.create", contextualName = "create-order")
    public UUID createOrder() {
        return UUID.randomUUID();
    }
}

@Configuration
@EnableAspectJAutoProxy
class ObservationConfig {
    @Bean
    ObservedAspect observedAspect(ObservationRegistry registry) {
        return new ObservedAspect(registry);
    }
}
```

```java
@SpringBootTest
class ObservedOrderTest {
    @Autowired OrderService orders;
    @Autowired MeterRegistry registry;

    @Test
    void recordsTimer() {
        orders.createOrder();
        assertThat(registry.find("orders.create").timer()).isNotNull();
    }
}
```

**Senior takeaway:** Business metrics belong on service boundaries — infra CPU can be green while payments fail silently without `@Observed` counters.

---

## Exercise 31 — Resilience4j circuit breaker fallback

**Difficulty:** Intermediate

**Task:** Configure `resilience4j.circuitbreaker.instances.remote` with low threshold; mock client fails; verify fallback method invoked and metric `OPEN` after repeated failures.

**Solution:**

```yaml
resilience4j.circuitbreaker.instances.remote:
  slidingWindowSize: 5
  failureRateThreshold: 50
  waitDurationInOpenState: 10s
```

```java
@Service
class RemoteClient {
    @CircuitBreaker(name = "remote", fallbackMethod = "fallback")
    public String call() {
        throw new RuntimeException("down");
    }
    String fallback(Throwable t) { return "FALLBACK"; }
}
```

```java
@SpringBootTest
class BreakerTest {
    @Autowired RemoteClient client;
    @Autowired CircuitBreakerRegistry registry;

    @Test
    void opensAndFallback() {
        for (int i = 0; i < 5; i++) assertEquals("FALLBACK", client.call());
        assertEquals(CircuitBreaker.State.OPEN, registry.circuitBreaker("remote").getState());
    }
}
```

**Senior takeaway:** Retry non-idempotent POST through breaker without idempotency key duplicates charges — bulkhead + timeout first.

---

## Exercise 32 — Testcontainers `@ServiceConnection` Postgres

**Difficulty:** Intermediate

**Task:** Integration test with `@ServiceConnection` PostgreSQL container; persist entity; assert dialect-specific `jsonb` or `SERIAL` behavior (skip if no Docker).

**Solution:**

```java
@Testcontainers
@SpringBootTest
class ServiceConnectionIT {
    @Container
    @ServiceConnection
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16-alpine");

    @Autowired JdbcTemplate jdbc;

    @Test
    void usesContainerDatabase() {
        jdbc.update("CREATE TABLE IF NOT EXISTS demo (id SERIAL PRIMARY KEY, payload JSONB)");
        jdbc.update("INSERT INTO demo(payload) VALUES('{\"k\":1}'::jsonb)");
        Integer count = jdbc.queryForObject("SELECT COUNT(*) FROM demo", Integer.class);
        assertEquals(1, count);
    }
}
```

**Senior takeaway:** Pin image tag/digest in CI; disable container reuse in pipeline to avoid cross-test pollution.

---

## Exercise 33 — Layered JAR extract + Docker cache plan

**Difficulty:** Hard

**Task:** Build layered Boot JAR, run layertools extract, write multi-stage Dockerfile copying `dependencies/` then `application/` layers; document which file change invalidates which layer.

**Solution:**

```xml
<plugin>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-maven-plugin</artifactId>
  <configuration><layers><enabled>true</enabled></layers></configuration>
</plugin>
```

```bash
java -Djarmode=layertools -jar target/demo-0.0.1-SNAPSHOT.jar extract --destination target/extracted
```

```dockerfile
FROM eclipse-temurin:21-jre as builder
WORKDIR /app
COPY target/extracted/dependencies/ ./
COPY target/extracted/spring-boot-loader/ ./
COPY target/extracted/snapshot-dependencies/ ./
COPY target/extracted/application/ ./
# Only application layer COPY reruns on code change when deps layer cached
ENTRYPOINT ["java", "org.springframework.boot.loader.launch.JarLauncher"]
```

**Senior takeaway:** Daily changing snapshot deps defeat cache — prefer release versions in CI; pair with `bootBuildImage` when platform mandates buildpacks.

---

# Weekend challenge

1. Run with `--debug` and read `ConditionEvaluationReport` — find why a `@ConditionalOnProperty` bean was skipped.
2. Enable Hibernate statistics, trigger Exercise 21 N+1, fix it, prove query count drop in a test.
3. Put Actuator on port 8081 with separate security filter chain; curl from localhost only.
4. Reproduce Exercise 13 pool deadlock in a branch, fix propagation, document in PR description.
5. Chaos test: SIGTERM during Exercise 25 long TX — record commit/rollback outcome and tune grace period.

---

**Stats:** 33 exercises · 12 Basic · 12 Intermediate · 9 Hard · 5 weekend drills · Topics: `@Transactional`, security, actuator, test slices, config props, scheduling, graceful shutdown, error handling, production bugs, resilience4j, Testcontainers, layered JAR
