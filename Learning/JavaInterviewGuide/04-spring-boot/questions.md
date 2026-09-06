# Spring Boot — 62 Senior Interview Questions

**Bar:** Auto-configuration, proxies, transactions, security, and production ops — not "what is `@RestController`".

---

### 1. What happens from `main()` to first request?

**Short answer:** `SpringApplication.run` bootstraps the environment, refreshes an `ApplicationContext`, applies auto-configuration, starts an embedded web server, registers `DispatcherServlet`, and fires lifecycle events before the app accepts traffic. Failures during this phase are startup failures — preferable to a half-initialized service.

#### What it is
The path from `public static void main` to handling HTTP is Spring Boot's opinionated startup pipeline. It replaces manual XML/Java configuration with convention, embedded servers, and conditional beans. At senior level, interviewers want the problem statement before the pattern name.

#### How it works (internals)
1. **Environment preparation:** `application.yml`, profiles, env vars, and `PropertySource` precedence are assembled. 2. **Context creation:** For servlet apps, typically `AnnotationConfigServletWebServerApplicationContext`. 3. **Source loading:** `@SpringBootApplication` combines `@Configuration`, `@EnableAutoConfiguration`, and `@ComponentScan`. 4. **Context refresh:** Bean definitions register; `BeanFactoryPostProcessor`s run; beans instantiate; `BeanPostProcessor`s wrap proxies (AOP, `@Transactional`). 5. **Web server:** Embedded Tomcat/Jetty/Undertow starts; `DispatcherServlet` maps to `/`. 6. **Ready signal:** `ApplicationReadyEvent` fires after the server listens. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss. Production debugging usually crosses logs, metrics, and condition reports—not just source code.

#### When to use / when NOT to use
Use this model for production microservices and monoliths alike. Avoid fighting it with manual servlet setup unless you have a legacy constraint. For CLI/batch, use non-web `SpringApplication` with `WebApplicationType.NONE`.

#### Production example
A payment service on Kubernetes: startup probes wait for `/actuator/health/readiness` after migrations complete. If Kafka auto-config fails (missing broker), the pod crashes and restarts rather than serving 500s. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- Putting `@SpringBootApplication` in a root package that accidentally scans third-party jars; assuming startup success means DB connectivity (lazy init hides failures); ignoring `ConditionEvaluationReport` when beans are missing. This often appears only under concurrent load or after deploy when negative paths were never tested.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** What is the difference between `ApplicationContextInitializedEvent` and `ApplicationReadyEvent`?
**A:** `ApplicationContextInitializedEvent` fires after context is prepared but before refresh completes—early environment tweaks only. `ApplicationReadyEvent` fires after embedded server listens and context is fully refreshed—use for readiness probes after Flyway. `ApplicationStartedEvent` is between them post-refresh. K8s readiness on wrong event causes traffic before DB migrations finish.

**Q:** How does lazy initialization change startup vs first-request latency?
**A:** `spring.main.lazy-initialization=true` delays bean creation until first use—faster startup, slower first request (cold path pays creation + JIT). Misleading in dev: startup 'succeeds' while first prod request times out creating heavy beans. Measure first-request p99 after enabling. Prefer explicit `@Lazy` on specific beans over global lazy init in production unless startup SLO demands it.

**Q:** What happens if two `@Primary` beans exist?
**A:** Spring throws `NoUniqueBeanDefinitionException` if multiple `@Primary` beans match—there can be only one primary per type (per context). Fix: remove duplicate `@Primary`, use `@Qualifier`, or split into separate injection points. In tests, `@MockBean` + `@Primary` on mock is common. Document which bean is canonical in module README—silent duplicate primaries fail at runtime not compile time.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving What happens from `main()` to first request?. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: `SpringApplication.run` bootstraps the environment, refreshes an `ApplicationContext`, applies auto-configuration, starts an embedded web server, registers `DispatcherServlet`, and fires lifecycle events before the app accepts traffic.. A payment service on Kubernetes: startup probes wait for `/actuator/health/readiness` after migrations complete. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```java
@SpringBootApplication
public class PaymentApplication {
    public static void main(String[] args) {
        SpringApplication.run(PaymentApplication.class, args);
    }
}
```

---

### 2. How does auto-configuration work?

**Short answer:** Auto-configuration registers beans only when classpath and property conditions match. Your explicit `@Bean` definitions usually win via `@ConditionalOnMissingBean`. Debug with `--debug` or the actuator conditions report.

#### What it is
Auto-configuration is a set of `@Configuration` classes loaded via `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` (Boot 3) or `spring.factories` (Boot 2). It wires sensible defaults for DataSource, Jackson, Security, etc. At senior level, interviewers want the problem statement before the pattern name.

#### How it works (internals)
Each auto-config class uses `@ConditionalOnClass`, `@ConditionalOnMissingBean`, `@ConditionalOnProperty`, `@ConditionalOnWebApplication`, and ordering annotations (`@AutoConfigureBefore/After/Order`). Spring evaluates conditions during context refresh and skips non-matching configs. User `@Configuration` classes are processed alongside auto-config; explicit beans override defaults. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss.

#### When to use / when NOT to use
Rely on auto-config for standard stacks. Exclude specific configs when they conflict (`@SpringBootApplication(exclude = ...)`). Do not `@ComponentScan` entire dependency trees — that pulls in unintended `@Component`s.

#### Production example
You need a custom `ObjectMapper` but keep Boot's HTTP message converters. Define one `@Bean ObjectMapper` — auto-config backs off. You need two DataSources: exclude `DataSourceAutoConfiguration` and wire both manually with `@Primary`. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback.

#### Common mistakes
- Assuming auto-config runs after your beans (order matters); enabling a starter without understanding what it brings; copying `@EnableAutoConfiguration` lists from blogs for Boot 2 onto Boot 3. This often appears only under concurrent load or after deploy when negative paths were never tested.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** How do `@ConditionalOnClass` and `@ConditionalOnMissingClass` differ?
**A:** `@ConditionalOnClass` registers config when listed classes are on classpath—enables optional integrations (Kafka, Redis). `@ConditionalOnMissingClass` registers when classes are absent—fallback paths. Both are evaluated at context refresh; typos cause silent skip. Debug with `--debug` ConditionEvaluationReport. Wrong classpath in fat-jar manifests causes 'works locally, fails in prod'.

**Q:** What is `@ImportAutoConfiguration` for?
**A:** `@ImportAutoConfiguration` pulls specific auto-configuration classes into a custom library or test without full `@EnableAutoConfiguration`. Use in custom starters: your `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` lists configs, consumers add your starter dependency. Tests use it to load only needed slices. Do not duplicate Boot's full auto-config list—import only what your starter owns.

**Q:** How would you write a custom starter?
**A:** A custom starter is a jar with: (1) `@Configuration` auto-config classes with `@ConditionalOn*` guards, (2) `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` (Boot 3), (3) optional `spring-boot-configuration-processor` metadata for IDE hints. Publish internal starter for shared Kafka/observability wiring. Version alongside Boot BOM. Test with `@ImportAutoConfiguration` and slice tests before consumers adopt.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving How does auto-configuration work?. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: Auto-configuration registers beans only when classpath and property conditions match.. You need a custom `ObjectMapper` but keep Boot's HTTP message converters. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```yaml
debug: true  # logs ConditionEvaluationReport
logging.level.org.springframework.boot.autoconfigure: DEBUG
```

---

### 3. `@SpringBootApplication(scanBasePackages=...)` pitfalls.

**Short answer:** Component scan defaults to the annotated class's package and sub-packages. Misplaced application classes or multi-module layouts cause "bean not found" at runtime. Tests using slices intentionally scan less.

#### What it is
`@SpringBootApplication` drives `@ComponentScan`. `scanBasePackages` and `scanBasePackageClasses` widen or narrow where Spring looks for `@Component`, `@Service`, `@Repository`, and `@Configuration`. At senior level, interviewers want the problem statement before the pattern name.

#### How it works (internals)
Spring's classpath scanning builds candidate component definitions. Only classes under the scan root become beans unless imported explicitly (`@Import`, `@EntityScan`, `@EnableJpaRepositories`). Auto-configuration is separate from component scan. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss.

#### When to use / when NOT to use
Set explicit scan roots in multi-module monoliths (`com.acme.orders.api`, `com.acme.orders.impl`). Avoid scanning `com` or vendor packages. Prefer modular boundaries over one giant scan.

#### Production example
Main class in `com.acme.Application` but JPA entities in `com.acme.domain` — fine. Config in `com.acme.infra.kafka` — fine if under `com.acme`. Shared library with `@Component` in `com.acme.lib` accidentally scanned if you set `scanBasePackages = "com.acme"`. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback.

#### Common mistakes
- Placing the main class in a shallow package; forgetting `@EntityScan` when entities sit outside the default scan; expecting `@WebMvcTest` to load repository beans. This often appears only under concurrent load or after deploy when negative paths were never tested.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** Difference between `@ComponentScan` and `@SpringBootApplication` defaults?
**A:** `@SpringBootApplication` is `@Configuration` + `@EnableAutoConfiguration` + `@ComponentScan` on the annotated class's package by default. Standalone `@ComponentScan` only registers components—it does not enable auto-config. Widening `scanBasePackages` pulls in accidental `@Component`s from libraries. `@EntityScan` and `@EnableJpaRepositories` are separate—entities/repos outside scan root need explicit roots.

**Q:** How do `@EntityScan` and `@EnableJpaRepositories` relate?
**A:** `@ComponentScan` does not register JPA entities or Spring Data repository interfaces. `@EntityScan(basePackages=...)` registers `@Entity` classes; `@EnableJpaRepositories` registers repository beans. Both are required when domain packages sit outside the `@SpringBootApplication` package subtree—common in multi-module monoliths. Auto-config still needs a DataSource on classpath; scan annotations only register types. Forgetting `@EntityScan` produces 'Not a managed type' at runtime despite compile success.

**Q:** What is `@Import` vs scan?
**A:** `@ComponentScan` discovers annotated classes under configured package roots automatically. `@Import` explicitly registers known `@Configuration` classes—ideal for modular monoliths where you control modules but do not want to widen scan to all of `com.acme`. Use `@Import` for internal feature modules; scan for convention-based bootstrapping. Combining both is normal: scan the app package, `@Import` infrastructure modules. Widening scan to vendor jars is an anti-pattern—explicit `@Import` or starter dependencies are safer.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving `@SpringBootApplication(scanBasePackages=...)` pitfalls. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: Component scan defaults to the annotated class's package and sub-packages.. Main class in `com.acme.Application` but JPA entities in `com.acme.domain` — fine. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

---

### 4. Bean lifecycle and `@PostConstruct` vs `InitializingBean` vs constructor.

**Short answer:** Beans are constructed, injected, then initialized via `@PostConstruct` or `afterPropertiesSet`, then used, then destroyed via `@PreDestroy`. Prefer constructor injection; use lifecycle callbacks for setup that needs fully injected dependencies.

#### What it is
Spring manages a bean's lifecycle from definition through destruction. Initialization hooks run after dependency injection completes. At senior level, interviewers want the problem statement before the pattern name.

#### How it works (internals)
Order: instantiate (constructor) → populate properties / constructor args → `BeanPostProcessor` before init → `@PostConstruct` / `InitializingBean.afterPropertiesSet()` / custom `init-method` → BPP after init → bean ready. Shutdown: `@PreDestroy` / `DisposableBean`. `@DependsOn` forces creation order but hides design smells. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss.

#### When to use / when NOT to use
Constructor for required dependencies and immutability. `@PostConstruct` for validation or lightweight startup that needs injected collaborators. Avoid heavy I/O or thread starts in init without graceful shutdown hooks.

#### Production example
A cache warmer `@PostConstruct` loads reference data — acceptable if fast and idempotent. A Kafka producer started in `@PostConstruct` without `@PreDestroy` close leaks connections on redeploy. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- Calling `@Transactional` methods from `@PostConstruct` (proxy not fully ready in some cases); circular dependencies "fixed" with `@PostConstruct` ordering; starting background threads without lifecycle management. This often appears only under concurrent load or after deploy when negative paths were never tested.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** What is a `BeanPostProcessor` vs `InitializingBean`?
**A:** On 'What is a `BeanPostProcessor` vs `InitializingBean`': anchor the answer in Bean lifecycle and `@PostConstruct` vs `InitializingBean` vs constructor.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** How does prototype scope change destruction?
**A:** Prototype beans are not fully destroyed by the container—no callback chain when garbage-collected. Singletons holding prototype references may leak if prototype is stateful. Use `DisposableBean` on prototype but do not rely on container tracking every instance. Prefer request scope with proxy for request-bound state instead of long-lived prototype graphs.

**Q:** What is `@Lazy` impact on lifecycle?
**A:** `@Lazy` on injection creates a proxy; real bean initializes on first method call. Breaks circular dependency at startup but defers failure to first use. On `@Bean` methods, `@Lazy` defers factory execution. Not a substitute for redesign—fix cycles with extracted collaborator or events. Prototype + lazy combinations confuse teams—document behavior in ADR.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Bean lifecycle and `@PostConstruct` vs `InitializingBean` vs constructor. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: Beans are constructed, injected, then initialized via `@PostConstruct` or `afterPropertiesSet`, then used, then destroyed via `@PreDestroy`.. A cache warmer `@PostConstruct` loads reference data — acceptable if fast and idempotent. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

---

### 5. Why field injection is a senior smell.

**Short answer:** Field injection hides dependencies, prevents `final` fields, complicates unit testing, and enables circular dependency workarounds. Constructor injection makes dependencies explicit and fails fast at startup.

#### What it is
`@Autowired` on fields is a legacy pattern where Spring sets fields via reflection after object construction. At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
Constructor injection resolves dependencies during instantiation — missing beans fail context refresh. Field injection creates the object first, then injects — allowing partially constructed objects in edge cases. Setter injection allows optional/mutable dependencies. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss.

#### When to use / when NOT to use
Always prefer constructor injection in services. Setter injection only for optional config. Field injection: avoid in production code; acceptable in tests with `@Autowired` on the test class itself.

#### Production example
A `OrderService` with five `@Autowired` fields — unit tests need reflection or Spring context. Refactored to constructor: tests pass mocks directly; immutability prevents accidental reassignment. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- Using `@Autowired(required = false)` to paper over missing config; combining field injection with `@Transactional` self-invocation confusion; Lombok `@RequiredArgsConstructor` forgotten when adding new deps. This often appears only under concurrent load or after deploy when negative paths were never tested.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** How does Spring handle circular dependencies in Boot 2.6+?
**A:** Boot 2.6+ disallows circular references by default—context refresh fails fast. Fixes: extract shared dependency, constructor refactor, `ObjectProvider`, or event decoupling. `@Lazy` is a band-aid. Kotlin `lateinit` does not remove the cycle. CI must use same `allow-circular-references` setting as production—never only in dev profile.

**Q:** Is `@Autowired` on constructor still needed with one constructor?
**A:** On 'Is `@Autowired` on constructor still needed with one constructor': anchor the answer in Why field injection is a senior smell.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Kotlin and injection patterns?
**A:** On 'Kotlin and injection patterns': anchor the answer in Why field injection is a senior smell.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Why field injection is a senior smell. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: Field injection hides dependencies, prevents `final` fields, complicates unit testing, and enables circular dependency workarounds.. A `OrderService` with five `@Autowired` fields — unit tests need reflection or Spring context. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

---

### 6. Proxy mechanics of `@Transactional`.

**Short answer:** Spring wraps `@Transactional` beans in a proxy that starts/commits/rolls back transactions around public methods invoked through the proxy. Self-invocation and non-public methods bypass the proxy — a classic production bug. Connection pool exhaustion often traces to transaction boundaries that span HTTP or messaging I/O. Self-invocation bypasses the proxy—split beans or inject self via interface when TX must apply.

#### What it is
Declarative transactions are implemented via AOP proxies (JDK interface proxy or CGLIB subclass), not by modifying your class bytecode directly. At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
`TransactionInterceptor` consults `PlatformTransactionManager` (usually `JpaTransactionManager` + Hikari). Default propagation `REQUIRED` joins existing TX or creates new. Default rollback: unchecked exceptions only. `readOnly=true` hints flush mode and can optimize JDBC. Proxy must be outermost for `@Transactional` + `@Cacheable` ordering to matter.

#### When to use / when NOT to use
Place `@Transactional` on service/use-case layer methods, kept short. Not on controllers, repositories (Spring Data handles its own), or entities. Use programmatic `TransactionTemplate` when flow is non-linear.

#### Production example
`OrderService.placeOrder()` is transactional; it calls private `validate()` internally — validation runs outside TX if called via `this.validate()`. Fix: inject self via interface, split bean, or move validation before transactional boundary. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- Expecting rollback on caught-and-swallowed exceptions; `@Transactional` on interface method without proxy seeing concrete class; long transactions holding DB connections during HTTP calls. This often appears only under concurrent load or after deploy when negative paths were never tested.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** JDK proxy vs CGLIB — when each?
**A:** JDK dynamic proxies require an interface—proxy implements same interfaces. CGLIB subclasses concrete classes when no interface (`proxyTargetClass=true`). `final` methods/classes cannot be proxied by CGLIB. Spring Boot defaults to CGLIB for class-based beans. Add service interfaces for testability and predictable JDK proxies. Log `spring.aop.proxy-target-class` when debugging TX not applying.

**Q:** Does `@Transactional` work on `final` methods?
**A:** No—`@Transactional` on `final` methods is ignored because CGLIB cannot override final methods; JDK proxies only intercept interface methods. Same for `private` methods—no proxy interception. Keep `@Transactional` on public service methods called through the Spring proxy. Self-invocation via `this.` also bypasses proxy.

**Q:** Interaction with `REQUIRES_NEW` and connection pools?
**A:** `REQUIRES_NEW` suspends outer TX and allocates a second connection from Hikari—briefly two connections per request thread. Under load this exhausts pools and causes deadlocks if nested chains are deep. Use only for audit/error logs that must commit when business TX rolls back. Monitor `hikaricp.connections.active` when introducing `REQUIRES_NEW`.

#### Scenario probe
**Situation:** On-call: orders show inconsistent state after a deploy affecting Proxy mechanics of `@Transactional`. Symptoms appear only under concurrent load; rollback is available but root cause is unclear.

**Model answer:** I start from: Spring wraps `@Transactional` beans in a proxy that starts/commits/rolls back transactions around public methods invoked through the proxy.. `OrderService.placeOrder()` is transactional; it calls private `validate()` internally — validation runs outside TX if called via `this.validate()`. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```java
@Service
public class OrderService {
    @Transactional(rollbackFor = Exception.class)
    public void placeOrder(OrderRequest req) { /* ... */ }
}
```

---

### 7. Transaction propagation (know this table cold).

**Short answer:** Propagation defines how a method participates in an existing transaction. `REQUIRED` is default; `REQUIRES_NEW` suspends and opens a new TX — useful for audit logs but dangerous for pool exhaustion and deadlocks. Connection pool exhaustion often traces to transaction boundaries that span HTTP or messaging I/O.

#### What it is
Propagation is a transaction attribute controlling boundary nesting when multiple `@Transactional` methods call each other. At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
Framework defaults and proxy ordering change runtime behavior in ways unit tests miss. Production debugging usually crosses logs, metrics, and condition reports—not just source code. Connection pool exhaustion often traces to transaction boundaries that span HTTP or messaging I/O.

#### When to use / when NOT to use
Pick the smallest pattern that meets SLOs; over-abstraction becomes its own incident source. State what you rejected and why—trade-off honesty beats pattern maximalism. Connection pool exhaustion often traces to transaction boundaries that span HTTP or messaging I/O.

#### Production example
We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever. Connection pool exhaustion often traces to transaction boundaries that span HTTP or messaging I/O.

#### Common mistakes
- This often appears only under concurrent load or after deploy when negative paths were never tested.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** What happens with `REQUIRES_NEW` + outer rollback?
**A:** On 'What happens with `REQUIRES_NEW` + outer rollback': Propagation is a transaction attribute controlling boundary nesting when multiple `@Transactional` methods call each other.

**Q:** Does `NOT_SUPPORTED` clear the persistence context?
**A:** On 'Does `NOT_SUPPORTED` clear the persistence context': Propagation is a transaction attribute controlling boundary nesting when multiple `@Transactional` methods call each other.

**Q:** ChainedTransactionManager pitfalls?
**A:** Top risk on 'Transaction propagation (know this table cold).': hidden coupling under load. Mitigate with fail-fast startup, metrics on the failure mode, and a runbook step tested in game day.

#### Scenario probe
**Situation:** On-call: orders show inconsistent state after a deploy affecting Transaction propagation (know this table cold). Symptoms appear only under concurrent load; rollback is available but root cause is unclear.

**Model answer:** I start from: Propagation defines how a method participates in an existing transaction..  I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

---

### 8. Isolation levels in Spring/`@Transactional`.

**Short answer:** `@Transactional(isolation = ...)` maps to JDBC isolation levels. Defaults follow the database (Postgres `READ COMMITTED`, Oracle historically `READ COMMITTED`). Raising isolation globally causes contention — prefer optimistic locking for lost updates. Connection pool exhaustion often traces to transaction boundaries that span HTTP or messaging I/O.

#### What it is
Isolation controls visibility of concurrent transactions' changes — dirty reads, non-repeatable reads, phantoms. At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
Spring sets isolation on the JDBC connection via `Connection.setTransactionIsolation`. Levels: DEFAULT, READ_UNCOMMITTED, READ_COMMITTED, REPEATABLE_READ, SERIALIZABLE. Actual behavior is DB-specific (e.g., Postgres MVCC vs SQL Server locking). Framework defaults and proxy ordering change runtime behavior in ways unit tests miss.

#### When to use / when NOT to use
Use DEFAULT unless you have measured anomalies. Bump isolation for specific critical reads, not application-wide. Prefer `@Version` optimistic locking over SERIALIZABLE for hot rows.

#### Production example
Inventory count job uses `REPEATABLE_READ` for consistent snapshot within one report TX — acceptable for batch. User-facing checkout stays `READ COMMITTED` + `@Version` on `Inventory` entity. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- Assuming `@Transactional(readOnly=true)` prevents writes; believing REPEATABLE_READ eliminates all phantoms on every DB; setting SERIALIZABLE without load testing. This often appears only under concurrent load or after deploy when negative paths were never tested.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** Difference between isolation and `@Lock(PESSIMISTIC_WRITE)`?
**A:** On 'Difference between isolation and `@Lock(PESSIMISTIC_WRITE)`': anchor the answer in Isolation levels in Spring/`@Transactional`.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** How does Postgres handle phantom reads?
**A:** On 'How does Postgres handle phantom reads': anchor the answer in Isolation levels in Spring/`@Transactional`.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Read-only transaction routing to replicas?
**A:** On 'Read-only transaction routing to replicas': anchor the answer in Isolation levels in Spring/`@Transactional`.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** On-call: orders show inconsistent state after a deploy affecting Isolation levels in Spring/`@Transactional`. Symptoms appear only under concurrent load; rollback is available but root cause is unclear.

**Model answer:** I start from: `@Transactional(isolation = ...)` maps to JDBC isolation levels.. Inventory count job uses `REPEATABLE_READ` for consistent snapshot within one report TX — acceptable for batch. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

---

### 9. `rollbackFor`, `noRollbackFor`, and wrapping exceptions.

**Short answer:** Spring rolls back on unchecked exceptions by default — not checked exceptions. Catching an exception inside a transactional method prevents rollback unless you rethrow or set `rollbackFor`. This is a top-10 production bug.

#### What it is
Rollback rules define which exceptions mark the transaction for rollback at commit time. At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
`TransactionInterceptor` completes with `rollbackOnly` flag set on matching exceptions. If you catch `RuntimeException` and return normally, Spring commits. Wrapping in `Exception` without `rollbackFor` also commits. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss.

#### When to use / when NOT to use
Use `rollbackFor = Exception.class` when business rules require rollback on checked exceptions. Use `noRollbackFor` sparingly for intentional partial success (rare). Prefer domain unchecked exceptions.

#### Production example
Service catches `PaymentDeclinedException`, logs, returns error DTO — DB shows order as PLACED while payment failed. Fix: don't catch inside TX boundary, or rethrow, or use `rollbackFor`. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- Swallowing exceptions; assuming `@Transactional` rolls back on `IOException`; testing only happy path in integration tests. This often appears only under concurrent load or after deploy when negative paths were never tested.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** What is `setRollbackOnly()` programmatically?
**A:** Call `TransactionStatus.setRollbackOnly()` when you catch an exception for logging but must abort the TX—then exit without committing. Alternative: rethrow as unchecked. Without rollback-only, caught `RuntimeException` still commits if you return normally—classic orders-PLACED/payment-failed bug. Integration test: force failure, assert DB unchanged.

**Q:** How do test `@Transactional` rollbacks interact with `@TransactionalEventListener`?
**A:** On 'How do test `@Transactional` rollbacks interact with `@TransactionalEventListener`': anchor the answer in `rollbackFor`, `noRollbackFor`, and wrapping exceptions.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Spring vs JTA rollback rules?
**A:** On 'Spring vs JTA rollback rules': anchor the answer in `rollbackFor`, `noRollbackFor`, and wrapping exceptions.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving `rollbackFor`, `noRollbackFor`, and wrapping exceptions. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: Spring rolls back on unchecked exceptions by default — not checked exceptions.. Service catches `PaymentDeclinedException`, logs, returns error DTO — DB shows order as PLACED while payment failed. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```java
@Transactional(rollbackFor = {PaymentException.class, IOException.class})
public void charge(Order order) { /* ... */ }
```

---

### 10. Transactional Event Listener.

**Short answer:** `@TransactionalEventListener` runs handlers tied to transaction phases — typically `AFTER_COMMIT` for side effects like email or Kafka. It is not a durability guarantee; use outbox for reliable delivery. Connection pool exhaustion often traces to transaction boundaries that span HTTP or messaging I/O.

#### What it is
Application events (`ApplicationEventPublisher`) with phase-aware delivery relative to transaction commit/rollback. At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
Phases: `AFTER_COMMIT`, `AFTER_ROLLBACK`, `AFTER_COMPLETION`, `BEFORE_COMMIT`. Default falls back to `@EventListener` behavior if no TX. Handler runs on caller thread unless `@Async`. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss.

#### When to use / when NOT to use
`AFTER_COMMIT` for notifications that must not fire on rollback. For Kafka/external systems requiring exactly-once effect, use transactional outbox in same DB TX, not bare listener. Pick the smallest pattern that meets SLOs; over-abstraction becomes its own incident source.

#### Production example
Order saved in TX; `OrderCreatedEvent` published; `@TransactionalEventListener(AFTER_COMMIT)` triggers email. JVM dies after commit before listener — email lost. Outbox row inserted in same TX; separate poller publishes to Kafka. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback.

#### Common mistakes
- Using `@EventListener` expecting after-commit semantics; heavy work in listener blocking commit completion; assuming `@Async` listener ordering. This often appears only under concurrent load or after deploy when negative paths were never tested.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** Outbox pattern vs transactional listener?
**A:** `@TransactionalEventListener(AFTER_COMMIT)` is in-process only—JVM death after commit loses the event. Transactional outbox writes event row in same DB TX as business data; poller publishes with retry. Choose outbox for inventory, email, Kafka when durability matters. Listener is fine for non-critical notifications with accepted loss risk.

**Q:** `BEFORE_COMMIT` use cases?
**A:** On '`BEFORE_COMMIT` use cases': anchor the answer in Transactional Event Listener.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Interaction with `@Transactional(propagation = REQUIRES_NEW)`?
**A:** `REQUIRES_NEW` suspends outer TX and allocates a second connection from Hikari—briefly two connections per request thread. Under load this exhausts pools and causes deadlocks if nested chains are deep. Use only for audit/error logs that must commit when business TX rolls back. Monitor `hikaricp.connections.active` when introducing `REQUIRES_NEW`.

#### Scenario probe
**Situation:** On-call: orders show inconsistent state after a deploy affecting Transactional Event Listener. Symptoms appear only under concurrent load; rollback is available but root cause is unclear.

**Model answer:** I start from: `@TransactionalEventListener` runs handlers tied to transaction phases — typically `AFTER_COMMIT` for side effects like email or Kafka.. Order saved in TX; `OrderCreatedEvent` published; `@TransactionalEventListener(AFTER_COMMIT)` triggers email. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

---

### 11. Open Session In View.

**Short answer:** OSIV keeps the JPA `EntityManager` open through view rendering, enabling lazy loading in controllers/JSP. It hides N+1 problems and holds DB connections longer — seniors often disable it and fix fetch plans.

#### What it is
`OpenEntityManagerInViewFilter` (enabled by default in Spring Boot MVC) extends the persistence context lifetime to the full HTTP request. At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
Without OSIV, the persistence context closes when the `@Transactional` service method returns. With OSIV, it stays open until the response completes — lazy associations load on access in the web layer. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss. Production debugging usually crosses logs, metrics, and condition reports—not just source code.

#### When to use / when NOT to use
Disable in APIs returning DTOs (`spring.jpa.open-in-view=false`). Enable only if you truly render entity graphs in views and accept the trade-off. Pick the smallest pattern that meets SLOs; over-abstraction becomes its own incident source.

#### Production example
REST endpoint returns `Order` entity; JSON serialization triggers lazy `order.getLines()` — N+1 in the converter, connection held 200ms. Fix: `@EntityGraph`, DTO projection, OSIV off. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- Blaming Hibernate for N+1 while OSIV masks it in dev; connection pool exhaustion under load with OSIV + slow clients. This often appears only under concurrent load or after deploy when negative paths were never tested.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** How does OSIV interact with `@Transactional` read-only services?
**A:** OSIV extends `EntityManager` lifetime through HTTP response—lazy loads work in JSON serialization but hold DB connections and hide N+1. Disable `spring.jpa.open-in-view=false` for APIs returning DTOs. Fix with `@EntityGraph`, fetch joins, or projections. Measure connection hold time—OSIV + slow clients starve Hikari pools.

**Q:** WebFlux and OSIV?
**A:** OSIV extends `EntityManager` lifetime through HTTP response—lazy loads work in JSON serialization but hold DB connections and hide N+1. Disable `spring.jpa.open-in-view=false` for APIs returning DTOs. Fix with `@EntityGraph`, fetch joins, or projections. Measure connection hold time—OSIV + slow clients starve Hikari pools.

**Q:** Measuring connection hold time?
**A:** On 'Measuring connection hold time': anchor the answer in Open Session In View.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Open Session In View. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: OSIV keeps the JPA `EntityManager` open through view rendering, enabling lazy loading in controllers/JSP.. REST endpoint returns `Order` entity; JSON serialization triggers lazy `order.getLines()` — N+1 in the converter, connection held 200ms. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```yaml
spring.jpa.open-in-view: false
```

---

### 12. `@Transactional` on REST controllers — yes or no?

**Short answer:** Usually no. Transactions belong at the service/use-case boundary, kept as short as possible. Controllers should map HTTP, validate input, and delegate — not own business transactions. Connection pool exhaustion often traces to transaction boundaries that span HTTP or messaging I/O.

#### What it is
An anti-pattern where `@RestController` methods are annotated `@Transactional`, stretching TX boundaries across serialization and external I/O. At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
If the controller method is transactional, the TX opens before service logic and may remain open during response writing — tying up a pooled connection and increasing deadlock risk. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss. Production debugging usually crosses logs, metrics, and condition reports—not just source code. Connection pool exhaustion often traces to transaction boundaries that span HTTP or messaging I/O.

#### When to use / when NOT to use
Never for typical REST. Rare exception: ultra-thin CRUD prototype — still refactor before prod. Use `@Transactional` on services; controllers stay free of persistence concerns.

#### Production example
Controller calls payment gateway inside `@Transactional` method — 3-second HTTP hold on DB connection while Hikari pool starves. Move gateway call outside TX; only DB work inside. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- Copy-paste from tutorials; combining `@Transactional` with `@Cacheable` on controller; thinking read-only controller TX is "free.". This often appears only under concurrent load or after deploy when negative paths were never tested.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** Where should read-only transactions live?
**A:** On 'Where should read-only transactions live': anchor the answer in `@Transactional` on REST controllers—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Layered architecture vs hexagonal — where is the boundary?
**A:** On 'Layered architecture vs hexagonal — where is the boundary': anchor the answer in `@Transactional` on REST controllers—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** `@Transactional` on repository custom impl?
**A:** On '`@Transactional` on repository custom impl': anchor the answer in `@Transactional` on REST controllers—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** On-call: orders show inconsistent state after a deploy affecting `@Transactional` on REST controllers. Symptoms appear only under concurrent load; rollback is available but root cause is unclear.

**Model answer:** I start from: Usually no.. Controller calls payment gateway inside `@Transactional` method — 3-second HTTP hold on DB connection while Hikari pool starves. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

---

### 13. Spring Data repository internals.

**Short answer:** Spring Data JPA creates JDK proxies implementing your repository interface. Query methods are parsed or use `@Query`; default impl is `SimpleJpaRepository`. Derived query names can explode into bad joins — prefer explicit fetch plans and projections.

#### What it is
Repository interfaces are factory-generated beans bridging domain-oriented APIs to `EntityManager` queries. At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
`RepositoryFactorySupport` builds proxies. Method name parsing (`findByStatusAndCreatedAtAfter`) generates JPQL. Custom fragments compose via `{Repo}Custom` + `{Repo}CustomImpl`. Projections map to DTOs/interfaces. `@Modifying` queries need `@Transactional` on the calling service.

#### When to use / when NOT to use
Use derived queries for simple predicates. Switch to `@Query`, Specifications, or Blaze-Persistence for complex SQL. `@EntityGraph` / JOIN FETCH for fetch plans; never rely on EAGER globally.

#### Production example
`findByCustomerId` returns orders with lazy lines — N+1 in service loop. Add `@EntityGraph(attributePaths = "lines")` or interface projection `OrderSummary`. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- `save()` on detached graphs causing extra SELECTs; `@Query` native without pagination on large tables; interface projections causing N+1 with nested graphs. This often appears only under concurrent load or after deploy when negative paths were never tested.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** How does `@Modifying(clearAutomatically = true)` work?
**A:** On 'How does `@Modifying(clearAutomatically = true)` work': anchor the answer in Spring Data repository internals.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Difference between `Slice` and `Page`?
**A:** On 'Difference between `Slice` and `Page`': anchor the answer in Spring Data repository internals.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Custom repository fragment wiring?
**A:** On 'Custom repository fragment wiring': anchor the answer in Spring Data repository internals.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Spring Data repository internals. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: Spring Data JPA creates JDK proxies implementing your repository interface.. `findByCustomerId` returns orders with lazy lines — N+1 in service loop. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

---

### 14. `@Async` gotchas.

**Short answer:** `@Async` requires `@EnableAsync`, proxy invocation, and a proper `TaskExecutor` — not `SimpleAsyncTaskExecutor` in production. Exceptions and MDC/trace context don't propagate automatically.

#### What it is
Spring's abstraction for running methods on a thread pool asynchronously, returning `void`, `Future`, or `CompletableFuture`. At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
`AsyncAnnotationBeanPostProcessor` wraps beans; calls must go through proxy. Default executor may spawn unbounded threads. Exception handler is `AsyncUncaughtExceptionHandler` — easy to miss failures on `void` methods. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss.

#### When to use / when NOT to use
Use for fire-and-forget or parallelizing independent I/O with bounded pools. Don't use to "fix" slow transactions. For reliable background work, prefer message queues.

#### Production example
Configure `ThreadPoolTaskExecutor` with core/max pool, queue, and `TaskDecorator` copying MDC/trace IDs. `@Async` method returns `CompletableFuture` for composition with timeouts. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- Self-invocation skipping async; `@Async` + `@Transactional` ordering confusion; unbounded thread creation under load. This often appears only under concurrent load or after deploy when negative paths were never tested.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** How to propagate security context to async threads?
**A:** On 'How to propagate security context to async threads': anchor the answer in `@Async` gotchas.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Virtual threads with `@Async` in Boot 3.2+?
**A:** On 'Virtual threads with `@Async` in Boot 3.2+': anchor the answer in `@Async` gotchas.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Difference from `@Scheduled`?
**A:** On 'Difference from `@Scheduled`': anchor the answer in `@Async` gotchas.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving `@Async` gotchas. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: `@Async` requires `@EnableAsync`, proxy invocation, and a proper `TaskExecutor` — not `SimpleAsyncTaskExecutor` in production.. Configure `ThreadPoolTaskExecutor` with core/max pool, queue, and `TaskDecorator` copying MDC/trace IDs. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```java
@Configuration
@EnableAsync
public class AsyncConfig implements AsyncConfigurer {
    @Override
    public Executor getAsyncExecutor() {
        ThreadPoolTaskExecutor ex = new ThreadPoolTaskExecutor();
        ex.setCorePoolSize(8);
        ex.setMaxPoolSize(32);
        ex.initialize();
        return ex;
    }
}
```

---

### 15. Bean scopes: singleton, prototype, request, session.

**Short answer:** Default singleton — one instance per container. Prototype creates new instances per lookup, not per injection into singletons. Request/session scopes need a web context and scoped proxies when injected into singletons.

#### What it is
Scope defines bean lifecycle and visibility — container-wide, per-request, or per-prototype instantiation. At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
Singleton: created once at startup (unless lazy). Prototype: new object each `getBean` or `@Lookup`. Request/session: stored in `RequestContextHolder`; injected into singleton via `@Scope(proxyMode = TARGET_CLASS)` proxy delegating per request. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss.

#### When to use / when NOT to use
Singleton for stateless services. Request scope for request-specific state (rare — prefer method args). Avoid storing request data in singleton fields.

#### Production example
`UserContext` as request-scoped bean injected into singleton service via proxy — each call resolves current user. Storing `UserContext` in a singleton `HashMap` — thread-safety disaster. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- Expecting prototype injection into singleton to create new instance each method call; forgetting scoped proxy; session scope in stateless APIs. This often appears only under concurrent load or after deploy when negative paths were never tested.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** `ObjectFactory` vs `Provider` vs `@Lookup`?
**A:** On '`ObjectFactory` vs `Provider` vs `@Lookup`': anchor the answer in Bean scopes: singleton, prototype, request, session.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** WebFlux request scope differences?
**A:** On 'WebFlux request scope differences': anchor the answer in Bean scopes: singleton, prototype, request, session.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Custom scope implementation?
**A:** On 'Custom scope implementation': anchor the answer in Bean scopes: singleton, prototype, request, session.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Bean scopes: singleton, prototype, request, session. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: Default singleton — one instance per container.. `UserContext` as request-scoped bean injected into singleton service via proxy — each call resolves current user. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

---

### 16. Configuration properties: `@ConfigurationProperties` vs `@Value`.

**Short answer:** Use `@ConfigurationProperties` for structured, validated, bindable config with metadata. Reserve `@Value` for single properties or SpEL. Never log secrets; sanitize actuator exposure.

#### What it is
Two mechanisms binding external configuration (yaml, env vars) to Java objects or fields. At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
`@ConfigurationProperties` uses relaxed binding (`spring.datasource.url` → `SPRING_DATASOURCE_URL`). Boot 3 supports constructor binding for immutability. `@ConfigurationPropertiesBinding` for custom converters. `@Value` injects at bean post-process time — no nested object binding without manual work.

#### When to use / when NOT to use
Properties classes for service config, feature flags, connection settings. `@Value` for one-off toggles. Always `@Validated` + JSR-303 on properties classes handling prod config.

#### Production example
`KafkaProperties` with nested `consumer`/`producer`, validated `@Min` poll intervals, documented via `spring-boot-configuration-processor` for IDE hints. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- Mutable properties beans mutated at runtime; secrets in git yaml; relying on `@Value` defaults without documenting in config server. This often appears only under concurrent load or after deploy when negative paths were never tested.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** `@ConfigurationPropertiesScan` vs `@EnableConfigurationProperties`?
**A:** On '`@ConfigurationPropertiesScan` vs `@EnableConfigurationProperties`': anchor the answer in Configuration properties: `@ConfigurationProperties` vs `@Value`.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** How does relaxed binding handle lists?
**A:** On 'How does relaxed binding handle lists': anchor the answer in Configuration properties: `@ConfigurationProperties` vs `@Value`.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Immutable `@ConstructorBinding`?
**A:** On 'Immutable `@ConstructorBinding`': anchor the answer in Configuration properties: `@ConfigurationProperties` vs `@Value`.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Configuration properties: `@ConfigurationProperties` vs `@Value`. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: Use `@ConfigurationProperties` for structured, validated, bindable config with metadata.. `KafkaProperties` with nested `consumer`/`producer`, validated `@Min` poll intervals, documented via `spring-boot-configuration-processor` for IDE hints. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```java
@ConfigurationProperties(prefix = "app.payment")
@Validated
public record PaymentProperties(
    @NotNull URI gatewayUrl,
    @Min(1000) int timeoutMs) {}
```

---

### 17. Profiles and 12-factor config.

**Short answer:** Profiles activate environment-specific beans and property files. Precedence: env vars override yaml. In Kubernetes, prefer ConfigMaps/Secrets over profile explosion — config is data, not code branches.

#### What it is
Spring profiles (`dev`, `staging`, `prod`) conditionally enable beans and property sources via `@Profile` and `application-{profile}.yml`. At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
`spring.profiles.active` selects profiles. Boot 2.4+ uses `spring.config.import` and `spring.config.activate.on-profile`. Environment variables highest precedence in externalized config. `@Profile` on `@Bean` methods gates infrastructure.

#### When to use / when NOT to use
Profiles for local vs integration test vs prod differences. Avoid ten profiles mirroring every tenant — use property values instead. 12-factor: store config in environment, not image. Pick the smallest pattern that meets SLOs; over-abstraction becomes its own incident source.

#### Production example
K8s Deployment sets `SPRING_PROFILES_ACTIVE=prod`, mounts secrets for DB password, ConfigMap for feature flags. No `application-prod.yml` with credentials in git. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- Baking secrets into jar; conflicting profile order; `@Profile("!prod")` surprises in tests. This often appears only under concurrent load or after deploy when negative paths were never tested.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** Config import order in Boot 2.4+?
**A:** On 'Config import order in Boot 2.4+': anchor the answer in Profiles and 12-factor config.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Spring Cloud Config vs K8s native?
**A:** On 'Spring Cloud Config vs K8s native': anchor the answer in Profiles and 12-factor config.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Testing with `@ActiveProfiles`?
**A:** On 'Testing with `@ActiveProfiles`': anchor the answer in Profiles and 12-factor config.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Profiles and 12-factor config. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: Profiles activate environment-specific beans and property files.. K8s Deployment sets `SPRING_PROFILES_ACTIVE=prod`, mounts secrets for DB password, ConfigMap for feature flags. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

---

### 18. Actuator: what you expose and what you must not.

**Short answer:** Actuator exposes operational endpoints — health, metrics, env, heapdump. Lock down management port, authentication, and exposure in production. Distinguish liveness (process alive) from readiness (can serve traffic).

#### What it is
Production-ready features for monitoring and managing Spring Boot applications via HTTP/JMX. At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
Endpoints mapped under `/actuator` by default. `management.endpoints.web.exposure.include` controls visibility. Custom `HealthIndicator`s aggregate subsystem status. Kubernetes probes target `/actuator/health/liveness` and `/readiness`.

#### When to use / when NOT to use
Expose health and prometheus metrics internally. Never public heapdump, env, or shutdown without auth. Separate management port on `:8081` behind network policy.

#### Production example
Payment service: readiness fails while Flyway migration runs; liveness passes. Prometheus scrapes `/actuator/prometheus` on internal network only. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- Exposing `*` endpoints to the internet; health check hitting downstream DB without timeout — cascading pod kills; logging actuator responses with secrets. This often appears only under concurrent load or after deploy when negative paths were never tested.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** Custom health indicator vs `@ReadinessState`?
**A:** On 'Custom health indicator vs `@ReadinessState`': anchor the answer in Actuator: what you expose and what you must not.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Micrometer registry customization?
**A:** On 'Micrometer registry customization': anchor the answer in Actuator: what you expose and what you must not.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Actuator security with Spring Security 6?
**A:** On 'Actuator security with Spring Security 6': anchor the answer in Actuator: what you expose and what you must not.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Actuator: what you expose and what you must not. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: Actuator exposes operational endpoints — health, metrics, env, heapdump.. Payment service: readiness fails while Flyway migration runs; liveness passes. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```yaml
management:
  server.port: 8081
  endpoints.web.exposure.include: health,prometheus
  endpoint.health.probes.enabled: true
```

---

### 19. Micrometer + tracing.

**Short answer:** Micrometer abstracts metrics (timers, counters, gauges) exported to Prometheus/Datadog. Micrometer Tracing bridges to OpenTelemetry for distributed traces. Control cardinality — never put unbounded labels like `userId` on metric names.

#### What it is
Observability instrumentation built into Spring Boot 3 via Micrometer and optional tracing bridges. At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
Auto-config registers `MeterRegistry`; `@Timed`, `@Counted`, HTTP/client metrics auto-instrumented. Tracing propagates W3C `traceparent` headers; MDC fields `traceId`/`spanId` for log correlation. Histograms vs percentiles — client-side aggregation cost. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss.

#### When to use / when NOT to use
Always metrics on services. Tracing sample rate in prod (e.g., 1–10%) to control cost. Business KPIs as counters (orders_completed) alongside technical metrics.

#### Production example
Alert on burn rate of 5xx timer, not CPU alone. Trace shows checkout slow due to inventory Feign call — tune timeout and bulkhead. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- High-cardinality tags crashing Prometheus; creating custom `ObjectMapper` breaking trace propagation; duplicating metrics at app and sidecar. This often appears only under concurrent load or after deploy when negative paths were never tested.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** Difference between histogram and summary in Prometheus?
**A:** On 'Difference between histogram and summary in Prometheus': anchor the answer in Micrometer + tracing.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** OpenTelemetry vs Brave?
**A:** On 'OpenTelemetry vs Brave': anchor the answer in Micrometer + tracing.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** `@Observed` annotation?
**A:** On '`@Observed` annotation': anchor the answer in Micrometer + tracing.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Micrometer + tracing. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: Micrometer abstracts metrics (timers, counters, gauges) exported to Prometheus/Datadog.. Alert on burn rate of 5xx timer, not CPU alone. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

---

### 20. Spring Security filter chain (Servlet).

**Short answer:** Security is a ordered filter chain before `DispatcherServlet`. Configure via `SecurityFilterChain` bean — authentication filters, authorization, exception translation. Stateless JWT APIs often disable sessions and CSRF with understood trade-offs. Fail-closed auth and explicit audience validation prevent subtle token confusion attacks.

#### What it is
Servlet filters implementing authentication and authorization cross-cutting concerns for every HTTP request. At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
Key filters: `SecurityContextHolderFilter`, logout, username/password or `BearerTokenAuthenticationFilter`, `ExceptionTranslationFilter`, `AuthorizationFilter`. `SecurityContext` stored in `ThreadLocal`. CSRF protects cookie-based sessions; less relevant for pure Bearer token APIs. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss.

#### When to use / when NOT to use
One `SecurityFilterChain` per security model (API vs actuator). Multiple chains ordered by `@Order`. Don't disable security globally in prod "temporarily."

#### Production example
Resource server validates JWT issuer/audience; actuator on separate port with mTLS. CORS configured at gateway, not as substitute for auth. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- Disabling CSRF on cookie-session SPA without token; permissive `permitAll` on admin paths; storing JWT in localStorage without XSS plan. This often appears only under concurrent load or after deploy when negative paths were never tested.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** Filter order relative to `OncePerRequestFilter`?
**A:** On 'Filter order relative to `OncePerRequestFilter`': anchor the answer in Spring Security filter chain (Servlet).—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** OAuth2 login vs resource server?
**A:** On 'OAuth2 login vs resource server': anchor the answer in Spring Security filter chain (Servlet).—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Method security filter interaction?
**A:** On 'Method security filter interaction': anchor the answer in Spring Security filter chain (Servlet).—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Security review flags auth gaps after a SPA release related to Spring Security filter chain (Servlet). Some users report intermittent 403; tokens appear valid in logs.

**Model answer:** I start from: Security is a ordered filter chain before `DispatcherServlet`.. Resource server validates JWT issuer/audience; actuator on separate port with mTLS. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

---

### 21. Method security vs HTTP security.

**Short answer:** HTTP security (`authorizeHttpRequests`) is the first gate. Method security (`@PreAuthorize`, `@Secured`) adds defense in depth on service methods. Both use proxies — enable with `@EnableMethodSecurity`. Fail-closed auth and explicit audience validation prevent subtle token confusion attacks.

#### What it is
Layered authorization — URL patterns vs fine-grained expression-based checks on beans. At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
`MethodSecurityInterceptor` evaluates SpEL before method invocation. Requires authenticated principal in `SecurityContext`. `@PostAuthorize` filters return values. `@PreFilter`/`@PostFilter` for collections.

#### When to use / when NOT to use
URL rules for coarse paths (`/admin/**`). Method security when multiple callers (HTTP, scheduler, messaging) hit same service. Avoid slow SpEL calling external services per request.

#### Production example
`/api/orders/**` authenticated; `OrderService.cancel()` requires `@PreAuthorize("hasRole('ADMIN') or @orderAuth.isOwner(#id)")`. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever. Fail-closed auth and explicit audience validation prevent subtle token confusion attacks.

#### Common mistakes
- Only HTTP security while `@Scheduled` job calls service directly; complex SpEL untested; forgetting `@EnableMethodSecurity`. This often appears only under concurrent load or after deploy when negative paths were never tested.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** Custom `PermissionEvaluator`?
**A:** On 'Custom `PermissionEvaluator`': anchor the answer in Method security vs HTTP security.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** `@WithMockUser` testing limits?
**A:** On '`@WithMockUser` testing limits': anchor the answer in Method security vs HTTP security.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Securing `@Async` methods?
**A:** On 'Securing `@Async` methods': anchor the answer in Method security vs HTTP security.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Security review flags auth gaps after a SPA release related to Method security vs HTTP security. Some users report intermittent 403; tokens appear valid in logs.

**Model answer:** I start from: HTTP security (`authorizeHttpRequests`) is the first gate.. `/api/orders/**` authenticated; `OrderService.cancel()` requires `@PreAuthorize("hasRole('ADMIN') or @orderAuth.isOwner(#id)")`. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

---

### 22. Password storage.

**Short answer:** Use `DelegatingPasswordEncoder` with adaptive hashes (BCrypt, Argon2, scrypt). Never SHA-256/MD5. Support algorithm migration via `{id}` prefix in stored hash.

#### What it is
Spring Security's password encoding abstraction for safe credential storage at rest. At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
`BCryptPasswordEncoder` includes salt and cost factor. `DelegatingPasswordEncoder` parses `{bcrypt}` prefix to select encoder — enables upgrading algorithms on next login. `PasswordEncoder.matches` is timing-safe. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss.

#### When to use / when NOT to use
Always hash passwords you control. For OAuth-only apps, you may not store passwords at all. Argon2 preferred on new systems if JVM/library support available.

#### Production example
User logs in with legacy `{sha256}` hash — matches, re-encode to `{bcrypt}` on success. Admin forces reset after breach. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- Storing plaintext; same salt for all users; logging password on failed login debug. This often appears only under concurrent load or after deploy when negative paths were never tested.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** Pepper vs salt?
**A:** On 'Pepper vs salt': anchor the answer in Password storage.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Password strength vs hash cost?
**A:** On 'Password strength vs hash cost': anchor the answer in Password storage.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Integration with Passkeys/WebAuthn?
**A:** On 'Integration with Passkeys/WebAuthn': anchor the answer in Password storage.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Password storage. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: Use `DelegatingPasswordEncoder` with adaptive hashes (BCrypt, Argon2, scrypt).. User logs in with legacy `{sha256}` hash — matches, re-encode to `{bcrypt}` on success. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

---

### 23. OAuth2 resource server vs client.

**Short answer:** Resource server validates access tokens on APIs (`issuer-uri`, scopes). OAuth2 client obtains tokens for outbound calls (authorization code, client credentials). BFF pattern uses confidential client at edge with token relay. Fail-closed auth and explicit audience validation prevent subtle token confusion attacks.

#### What it is
Two roles in OAuth2/OIDC — protecting APIs vs acting on behalf of users or services to call other APIs. At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
Resource server: `JwtDecoder` validates signature, `exp`, `iss`, `aud`. Client: `OAuth2AuthorizedClientManager` handles token refresh. Spring Security 6 consolidates configuration via `SecurityFilterChain`. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss.

#### When to use / when NOT to use
Resource server for microservice APIs behind gateway. Client credentials for service-to-service without user context. Avoid passing user access token to every downstream service — use token exchange or internal identity.

#### Production example
SPA → BFF (auth code + PKCE) → internal services with mTLS + service JWT. User JWT never reaches inventory service directly. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- Skipping audience validation; long-lived refresh tokens in mobile without rotation; treating ID token as access token. This often appears only under concurrent load or after deploy when negative paths were never tested.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** PKCE flow details?
**A:** On 'PKCE flow details': anchor the answer in OAuth2 resource server vs client.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** JWT vs opaque token introspection?
**A:** On 'JWT vs opaque token introspection': anchor the answer in OAuth2 resource server vs client.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Spring Authorization Server?
**A:** On 'Spring Authorization Server': anchor the answer in OAuth2 resource server vs client.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Security review flags auth gaps after a SPA release related to OAuth2 resource server vs client. Some users report intermittent 403; tokens appear valid in logs.

**Model answer:** I start from: Resource server validates access tokens on APIs (`issuer-uri`, scopes).. SPA → BFF (auth code + PKCE) → internal services with mTLS + service JWT. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

---

### 24. Validation: `@Valid` vs `@Validated`, groups.

**Short answer:** `@Valid` triggers Bean Validation on controller parameters. `@Validated` enables validation groups and works on `@ConfigurationProperties`. Validate business invariants in the domain layer, not only JSON shape.

#### What it is
JSR-380 (Jakarta Validation) integration for declarative constraint checking. At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
`MethodValidationPostProcessor` handles `@Validated` on classes. Groups (`Create`, `Update`) select constraint subsets. `@Valid` cascades to nested objects. Hibernate Validator is the reference implementation.

#### When to use / when NOT to use
Input DTO validation at boundary. Domain rules (sufficient balance) in entities/services. Don't rely on UI-only validation.

#### Production example
`CreateOrderRequest` validated at controller; `Order.place()` enforces invariants throwing domain exceptions mapped to 409 by `@ControllerAdvice`. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- `@Valid` on interface projection; validating entities with lazy fields triggering loads; duplicate validation annotations diverging. This often appears only under concurrent load or after deploy when negative paths were never tested.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** Custom constraint validators?
**A:** On 'Custom constraint validators': anchor the answer in Validation: `@Valid` vs `@Validated`, groups.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Programmatic `Validator` usage?
**A:** On 'Programmatic `Validator` usage': anchor the answer in Validation: `@Valid` vs `@Validated`, groups.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Validation in WebFlux?
**A:** On 'Validation in WebFlux': anchor the answer in Validation: `@Valid` vs `@Validated`, groups.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Validation: `@Valid` vs `@Validated`, groups. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: `@Valid` triggers Bean Validation on controller parameters.. `CreateOrderRequest` validated at controller; `Order.place()` enforces invariants throwing domain exceptions mapped to 409 by `@ControllerAdvice`. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

---

### 25. Exception handling: `@ControllerAdvice`.

**Short answer:** Centralize mapping from domain and framework exceptions to HTTP status and problem details (RFC 7807). Log with correlation IDs; never leak stack traces to clients.

#### What it is
Global `@ExceptionHandler` methods across controllers for consistent API error responses. At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
`ExceptionHandlerExceptionResolver` invokes advice methods based on exception type. `ProblemDetail` (Spring 6) builds standardized JSON errors. Order matters — most specific handler wins. Async/MVC error handling needs `@ExceptionHandler` on `@ControllerAdvice` with proper scope.

#### When to use / when NOT to use
One `@RestControllerAdvice` per API surface. Map validation to 400, not found to 404, conflict to 409, unexpected to 500 with generic message. Pick the smallest pattern that meets SLOs; over-abstraction becomes its own incident source.

#### Production example
`InsufficientInventoryException` → 409 with problem type URI, traceId header, no internal SQL in body. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- Catch-all swallowing root cause in logs; returning 200 with error envelope; inconsistent error schema across services. This often appears only under concurrent load or after deploy when negative paths were never tested.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** `HandlerExceptionResolver` chain order?
**A:** On '`HandlerExceptionResolver` chain order': anchor the answer in Exception handling: `@ControllerAdvice`.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Security exceptions handling?
**A:** On 'Security exceptions handling': anchor the answer in Exception handling: `@ControllerAdvice`.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** WebFlux `@ControllerAdvice` differences?
**A:** On 'WebFlux `@ControllerAdvice` differences': anchor the answer in Exception handling: `@ControllerAdvice`.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Exception handling: `@ControllerAdvice`. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: Centralize mapping from domain and framework exceptions to HTTP status and problem details (RFC 7807).. `InsufficientInventoryException` → 409 with problem type URI, traceId header, no internal SQL in body. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```java
@RestControllerAdvice
public class ApiExceptionHandler {
    @ExceptionHandler(InsufficientInventoryException.class)
    ResponseEntity<ProblemDetail> handle(InsufficientInventoryException ex) {
        ProblemDetail pd = ProblemDetail.forStatusAndDetail(
            HttpStatus.CONFLICT, ex.getMessage());
        return ResponseEntity.status(HttpStatus.CONFLICT).body(pd);
    }
}
```

---

### 26. Content negotiation and `HttpMessageConverter`.

**Short answer:** Spring MVC selects `HttpMessageConverter` implementations based on `Content-Type`, `Accept`, and registered converters. Jackson handles JSON by default — customize via `Jackson2ObjectMapperBuilderCustomizer`, not a stray unused `ObjectMapper` bean.

#### What it is
The mechanism translating HTTP bodies to/from Java objects in `@RequestBody` and `@ResponseBody` handling. At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
`RequestMappingHandlerAdapter` negotiates media types. `MappingJackson2HttpMessageConverter` uses the context's primary `ObjectMapper`. Custom converters register via `WebMvcConfigurer.extendMessageConverters`. `@JsonView` filters serialization per endpoint.

#### When to use / when NOT to use
JSON for APIs; XML only when required. Prefer ISO-8601 dates over epoch timestamps unless contract demands millis. Use problem+json for errors consistently.

#### Production example
Global customizer registers `JavaTimeModule`, disables `WRITE_DATES_AS_TIMESTAMPS`, ignores unknown properties on inbound DTOs only (not global if unsafe). We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- This often appears only under concurrent load or after deploy when negative paths were never tested.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** Custom `HttpMessageConverter` registration?
**A:** On 'Custom `HttpMessageConverter` registration': anchor the answer in Content negotiation and `HttpMessageConverter`.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Two `ObjectMapper` beans — which wins?
**A:** On 'Two `ObjectMapper` beans — which wins': anchor the answer in Content negotiation and `HttpMessageConverter`.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** JSON views and API versioning?
**A:** On 'JSON views and API versioning': anchor the answer in Content negotiation and `HttpMessageConverter`.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Content negotiation and `HttpMessageConverter`. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: Spring MVC selects `HttpMessageConverter` implementations based on `Content-Type`, `Accept`, and registered converters.. Global customizer registers `JavaTimeModule`, disables `WRITE_DATES_AS_TIMESTAMPS`, ignores unknown properties on inbound DTOs only (not global if unsafe). I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

---

### 27. Filter vs Interceptor vs ControllerAdvice vs AOP.

**Short answer:** Filters wrap the servlet container earliest; interceptors run in Spring MVC after handler mapping; `@ControllerAdvice` handles exceptions; AOP proxies any Spring bean method. Choose the outermost layer that has the data you need. Self-invocation bypasses the proxy—split beans or inject self via interface when TX must apply.

#### What it is
Four extension points at different layers of the request and bean lifecycle. At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
Filter: `FilterChain`, sees static resources. HandlerInterceptor: `preHandle/postHandle/afterCompletion` around controller. Advice: exception translation only (unless `@ModelAttribute`). AOP: `@Around` on service/repository methods via proxy.

#### When to use / when NOT to use
Filter for tracing, security headers, request logging with raw servlet access. Interceptor for MVC-specific auth checks. AOP for transactions, caching, metrics on services — not HTTP.

#### Production example
Filter adds trace ID to MDC; interceptor rejects deprecated API version header; AOP `@Timed` on service layer; advice maps exceptions. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever. Self-invocation bypasses the proxy—split beans or inject self via interface when TX must apply.

#### Common mistakes
- This often appears only under concurrent load or after deploy when negative paths were never tested.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** Where to put correlation ID — filter or interceptor?
**A:** On 'Where to put correlation ID — filter or interceptor': anchor the answer in Filter vs Interceptor vs ControllerAdvice vs AOP.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Can AOP see HTTP headers?
**A:** On 'Can AOP see HTTP headers': anchor the answer in Filter vs Interceptor vs ControllerAdvice vs AOP.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Ordering `@Order` across layers?
**A:** On 'Ordering `@Order` across layers': anchor the answer in Filter vs Interceptor vs ControllerAdvice vs AOP.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Filter vs Interceptor vs ControllerAdvice vs AOP. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: Filters wrap the servlet container earliest; interceptors run in Spring MVC after handler mapping; `@ControllerAdvice` handles exceptions; AOP proxies any Spring bean method.. Filter adds trace ID to MDC; interceptor rejects deprecated API version header; AOP `@Timed` on service layer; advice maps exceptions. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

---

### 28. WebFlux vs MVC. When would you switch?

**Short answer:** Default to MVC — especially with virtual threads for blocking I/O concurrency. Choose WebFlux for streaming, backpressure, and fully reactive stacks (R2DBC). Never block JDBC on the Netty event loop.

#### What it is
Two web stacks: Servlet (MVC) vs Reactive (WebFlux on Netty). At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
MVC: thread-per-request (or virtual thread). WebFlux: event loop + reactive types (`Mono`/`Flux`). Blocking call on event loop thread stalls all requests on that thread. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss.

#### When to use / when NOT to use
MVC + JDBC + JPA for most enterprise apps. WebFlux when end-to-end reactive or SSE/streaming at scale. Don't choose WebFlux for "performance" without reactive drivers.

#### Production example
Telemetry ingestion with WebFlux + Kafka reactive producer. Order management stays MVC + virtual threads + Hikari. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- This often appears only under concurrent load or after deploy when negative paths were never tested.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** Blockhound / thread-bound issues in WebFlux?
**A:** On 'Blockhound / thread-bound issues in WebFlux': anchor the answer in WebFlux vs MVC. When would you switch?—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** When is MVC + virtual threads enough?
**A:** On 'When is MVC + virtual threads enough': anchor the answer in WebFlux vs MVC. When would you switch?—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** R2DBC vs blocking JDBC in reactive?
**A:** On 'R2DBC vs blocking JDBC in reactive': anchor the answer in WebFlux vs MVC. When would you switch?—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving WebFlux vs MVC. When would you switch?. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: Default to MVC — especially with virtual threads for blocking I/O concurrency.. Telemetry ingestion with WebFlux + Kafka reactive producer. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

---

### 29. RestClient / WebClient / Feign / RestTemplate.

**Short answer:** `RestTemplate` is maintenance mode. Use `RestClient` (Boot 3.2+) for sync, `WebClient` for reactive, OpenFeign for declarative Spring Cloud clients. Always configure timeouts, connection pools, retries (idempotent only), and metrics.

#### What it is
HTTP client options for inter-service and external API calls from Spring applications. At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
RestClient builds on `RestTemplate` infrastructure with fluent API. WebClient uses Reactor Netty client with backpressure. Feign generates interfaces with Spring Cloud LoadBalancer integration. Resilience4j wraps retries/circuit breakers.

#### When to use / when NOT to use
RestClient for simple sync calls inside MVC services. Feign when many similar internal APIs. WebClient for parallel fan-out with reactive composition. Never retry non-idempotent POST blindly.

#### Production example
Feign client to inventory with 2s connect/read timeout, retry on 503 for GET only, Micrometer metrics, custom error decoder mapping 404 to domain exception. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- This often appears only under concurrent load or after deploy when negative paths were never tested.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** Feign vs RestClient in Boot 3?
**A:** On 'Feign vs RestClient in Boot 3': anchor the answer in RestClient / WebClient / Feign / RestTemplate.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Connection pooling for WebClient?
**A:** On 'Connection pooling for WebClient': anchor the answer in RestClient / WebClient / Feign / RestTemplate.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** When is RestTemplate still OK?
**A:** On 'When is RestTemplate still OK': anchor the answer in RestClient / WebClient / Feign / RestTemplate.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving RestClient / WebClient / Feign / RestTemplate. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: `RestTemplate` is maintenance mode.. Feign client to inventory with 2s connect/read timeout, retry on 503 for GET only, Micrometer metrics, custom error decoder mapping 404 to domain exception. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

---

### 30. `@Scheduled` and clustering.

**Short answer:** `@Scheduled` runs on every JVM instance — in a cluster, all pods fire unless you add distributed locking (ShedLock), Quartz cluster, K8s Job, or leader election. In microservices, the same idea often appears at the network boundary as well as inside a single JVM.

#### What it is
Spring's in-process scheduler for cron/fixed-rate/fixed-delay tasks. At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
`@EnableScheduling` registers `ScheduledAnnotationBeanPostProcessor`. Default single-thread scheduler — configure `TaskScheduler` bean for pool. No cross-node coordination built in. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss.

#### When to use / when NOT to use
Single-instance dev or truly idempotent frequent tasks with external dedup. Production multi-replica: ShedLock + JDBC/Redis or move job to K8s CronJob. Pick the smallest pattern that meets SLOs; over-abstraction becomes its own incident source.

#### Production example
Nightly reconciliation: K8s CronJob invokes admin endpoint once. Hourly cache refresh: ShedLock ensures one winner across 6 pods. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- Duplicate emails/invoices in prod; long `@Scheduled` method blocking scheduler thread; no misfire policy understanding. This often appears only under concurrent load or after deploy when negative paths were never tested.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** ShedLock vs Quartz cluster?
**A:** On 'ShedLock vs Quartz cluster': anchor the answer in `@Scheduled` and clustering.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** `@Scheduled` with virtual threads?
**A:** On '`@Scheduled` with virtual threads': anchor the answer in `@Scheduled` and clustering.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Timezone in cron expressions?
**A:** On 'Timezone in cron expressions': anchor the answer in `@Scheduled` and clustering.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving `@Scheduled` and clustering. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: `@Scheduled` runs on every JVM instance — in a cluster, all pods fire unless you add distributed locking (ShedLock), Quartz cluster, K8s Job, or leader election.. Nightly reconciliation: K8s CronJob invokes admin endpoint once. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```java
@Scheduled(cron = "0 0 2 * * *", zone = "UTC")
@SchedulerLock(name = "nightlyReconcile", lockAtMostFor = "PT30M")
public void reconcile() { /* ... */ }
```

---

### 31. Testing slices: `@SpringBootTest` vs `@WebMvcTest` vs `@DataJpaTest`.

**Short answer:** `@SpringBootTest` loads full context — integration tests. `@WebMvcTest` slices MVC layer with mocked services. `@DataJpaTest` slices JPA with in-memory or Testcontainers DB. Pick the narrowest slice that proves your change.

#### What it is
Test annotations configuring partial application contexts for faster, focused tests. At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
Slice tests exclude unrelated auto-config via `@AutoConfigure...` imports. `@MockBean`/`@MockitoBean` (Boot 3.4) replaces collaborators. `@Transactional` on tests rolls back DB changes — hides after-commit listeners. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss.

#### When to use / when NOT to use
Unit tests without Spring when possible. `@WebMvcTest` for controller contract. Testcontainers for Kafka/Postgres integration matching prod. Never hit real prod from CI.

#### Production example
Controller test: `@WebMvcTest(OrderController)` + `@MockitoBean OrderService`. Repository query test: `@DataJpaTest` + Testcontainers Postgres. End-to-end: one `@SpringBootTest` journey with WireMock. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback.

#### Common mistakes
- This often appears only under concurrent load or after deploy when negative paths were never tested.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** When to use `@SpringBootTest` vs slice tests?
**A:** On 'When to use `@SpringBootTest` vs slice tests': anchor the answer in Testing slices: `@SpringBootTest` vs `@WebMvcTest` vs `@DataJpaTest`.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** `@MockBean` vs `@Mock`?
**A:** On '`@MockBean` vs `@Mock`': anchor the answer in Testing slices: `@SpringBootTest` vs `@WebMvcTest` vs `@DataJpaTest`.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Testcontainers for integration?
**A:** On 'Testcontainers for integration': anchor the answer in Testing slices: `@SpringBootTest` vs `@WebMvcTest` vs `@DataJpaTest`.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Testing slices: `@SpringBootTest` vs `@WebMvcTest` vs `@DataJpaTest`. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: `@SpringBootTest` loads full context — integration tests.. Controller test: `@WebMvcTest(OrderController)` + `@MockitoBean OrderService`. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

---

### 32. `@DirtiesContext` as a smell.

**Short answer:** `@DirtiesContext` forces Spring to rebuild the context between tests — slow and indicates shared mutable state. Fix test isolation instead of resetting the world.

#### What it is
Test annotation marking the application context dirty after a test method/class, triggering reload. At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
Spring TestContext Framework caches contexts by configuration key. `@DirtiesContext` evicts cache entry — next test pays full startup cost. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss. Production debugging usually crosses logs, metrics, and condition reports—not just source code.

#### When to use / when NOT to use
Last resort when testing `@Cacheable` eviction or static singleton pollution. Prefer `@DynamicPropertySource`, fresh test data, or separate test classes. Pick the smallest pattern that meets SLOs; over-abstraction becomes its own incident source.

#### Production example
Test mutates global `@PostConstruct` static cache — refactor to injectable cache bean cleared in `@AfterEach` instead of `@DirtiesContext`. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- This often appears only under concurrent load or after deploy when negative paths were never tested.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** Why is `@DirtiesContext` slow?
**A:** On 'Why is `@DirtiesContext` slow': anchor the answer in `@DirtiesContext` as a smell.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Alternative isolation strategies?
**A:** On 'Alternative isolation strategies': anchor the answer in `@DirtiesContext` as a smell.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Shared context in integration tests?
**A:** On 'Shared context in integration tests': anchor the answer in `@DirtiesContext` as a smell.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving `@DirtiesContext` as a smell. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: `@DirtiesContext` forces Spring to rebuild the context between tests — slow and indicates shared mutable state.. Test mutates global `@PostConstruct` static cache — refactor to injectable cache bean cleared in `@AfterEach` instead of `@DirtiesContext`. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

---

### 33. Embedded server: Tomcat threads, connection timeout, max connections.

**Short answer:** Tune `server.tomcat.threads.max`, accept queue, and connection timeouts based on load tests — not defaults. Virtual threads (`spring.threads.virtual.enabled`) improve blocking I/O scalability on Java 21+.

#### What it is
Embedded Tomcat (default) thread and connection management for incoming HTTP. At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
Worker threads handle requests; accept queue buffers when threads busy. `connection-timeout` limits idle connections. Virtual threads map many logical tasks to fewer carrier threads — good for blocking JDBC/HTTP client work. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss.

#### When to use / when NOT to use
Tune with realistic load including downstream latency. Enable virtual threads for I/O-bound MVC apps on Java 21. CPU-bound work still needs sizing by cores.

#### Production example
Load test shows thread pool saturation at 200 RPS — increase threads modestly, fix slow DB query, enable virtual threads, set `server.tomcat.accept-count` with monitoring. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- Max threads = 10000 without pool/DB capacity; ignoring keep-alive connection pile-up; no correlation with Hikari pool size. This often appears only under concurrent load or after deploy when negative paths were never tested.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** Relationship Tomcat threads vs Hikari pool?
**A:** On 'Relationship Tomcat threads vs Hikari pool': anchor the answer in Embedded server: Tomcat threads, connection timeout, max connections.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Undertow vs Tomcat tuning?
**A:** On 'Undertow vs Tomcat tuning': anchor the answer in Embedded server: Tomcat threads, connection timeout, max connections.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** HTTP/2 and connection limits?
**A:** On 'HTTP/2 and connection limits': anchor the answer in Embedded server: Tomcat threads, connection timeout, max connections.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Embedded server: Tomcat threads, connection timeout, max connections. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: Tune `server.tomcat.threads.max`, accept queue, and connection timeouts based on load tests — not defaults.. Load test shows thread pool saturation at 200 RPS — increase threads modestly, fix slow DB query, enable virtual threads, set `server.tomcat.accept-count` with monitoring. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```yaml
server:
  tomcat:
    threads.max: 200
    accept-count: 100
    connection-timeout: 20s
spring.threads.virtual.enabled: true
```

---

### 34. Graceful shutdown sequence.

**Short answer:** On SIGTERM, stop accepting new work, drain in-flight requests, commit Kafka offsets, close connection pools, then exit. Combine `server.shutdown=graceful`, K8s preStop, and readiness failure.

#### What it is
Coordinated application shutdown avoiding dropped requests and corrupted in-flight transactions during deploys. At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
Boot graceful shutdown stops connector, waits for active requests up to timeout. `SmartLifecycle` beans stop in phases. Kafka listener containers need `stopImmediate=false` and sufficient timeout to finish poll batch. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss.

#### When to use / when NOT to use
Always in Kubernetes. Set `terminationGracePeriodSeconds` > graceful timeout + preStop sleep. Register custom shutdown hooks for non-Spring resources.

#### Production example
preStop: sleep 5s → readiness fails → LB drains → graceful shutdown 30s → Kafka consumer commits → Hikari closes. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- This often appears only under concurrent load or after deploy when negative paths were never tested.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** Tomcat graceful vs immediate shutdown?
**A:** On 'Tomcat graceful vs immediate shutdown': anchor the answer in Graceful shutdown sequence.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** K8s preStop hook pattern?
**A:** On 'K8s preStop hook pattern': anchor the answer in Graceful shutdown sequence.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Kafka consumer stop timeout?
**A:** On 'Kafka consumer stop timeout': anchor the answer in Graceful shutdown sequence.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Graceful shutdown sequence. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: On SIGTERM, stop accepting new work, drain in-flight requests, commit Kafka offsets, close connection pools, then exit.. preStop: sleep 5s → readiness fails → LB drains → graceful shutdown 30s → Kafka consumer commits → Hikari closes. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

---

### 35. Multi-datasource / multi-tx manager.

**Short answer:** Multiple `DataSource`s require explicit `@Primary`, separate `LocalContainerEntityManagerFactoryBean`, and `@Transactional("otherTxManager")` matching the manager name. No real 2PC across DBs — use saga/outbox patterns.

#### What it is
Configuration pattern for applications accessing more than one relational database. At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
Each EMF gets its own `JpaTransactionManager`. `@Transactional` defaults to `@Primary` manager. `ChainedTransactionManager` commits sequentially — partial commit possible on failure. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss.

#### When to use / when NOT to use
Legitimate bounded contexts in modular monolith or read replica routing — not cross-service joins. Avoid dual writes without distributed consistency strategy. Pick the smallest pattern that meets SLOs; over-abstraction becomes its own incident source.

#### Production example
Orders DB primary; reporting read replica with `@Transactional(readOnly=true)` routing via `AbstractRoutingDataSource`. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- This often appears only under concurrent load or after deploy when negative paths were never tested.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** ChainedTransactionManager pitfalls?
**A:** On 'ChainedTransactionManager pitfalls': anchor the answer in Multi-datasource / multi-tx manager.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** `@Transactional(transactionManager=...)`?
**A:** On '`@Transactional(transactionManager=...)`': anchor the answer in Multi-datasource / multi-tx manager.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Read replica routing?
**A:** On 'Read replica routing': anchor the answer in Multi-datasource / multi-tx manager.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Multi-datasource / multi-tx manager. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: Multiple `DataSource`s require explicit `@Primary`, separate `LocalContainerEntityManagerFactoryBean`, and `@Transactional("otherTxManager")` matching the manager name.. Orders DB primary; reporting read replica with `@Transactional(readOnly=true)` routing via `AbstractRoutingDataSource`. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

---

### 36. Flyway/Liquibase in Boot.

**Short answer:** Schema migrations should be reviewed, versioned, and immutable once applied. Prefer K8s init containers/Jobs for migrations so runtime app doesn't need DDL credentials.

#### What it is
Database migration tools integrated via Spring Boot auto-configuration on startup. At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
Flyway runs scripts from `classpath:db/migration` ordered by version. Checksum validation detects tampering. Baseline for brownfield. Liquibase offers XML/YAML changesets with rollback support (use carefully in prod).

#### When to use / when NOT to use
Flyway for SQL-first teams. Never `ddl-auto=update` in prod. Expand/contract pattern for zero-downtime column changes.

#### Production example
Init container runs Flyway with elevated creds; app user read/write DML only. Migration adds nullable column (expand), app deploy reads/writes, backfill job, then NOT NULL + contract in later release. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- This often appears only under concurrent load or after deploy when negative paths were never tested.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** Flyway vs Liquibase in teams?
**A:** On 'Flyway vs Liquibase in teams': anchor the answer in Flyway/Liquibase in Boot.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Migrations in init container vs app startup?
**A:** On 'Migrations in init container vs app startup': anchor the answer in Flyway/Liquibase in Boot.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Rollback strategy?
**A:** On 'Rollback strategy': anchor the answer in Flyway/Liquibase in Boot.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Flyway/Liquibase in Boot. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: Schema migrations should be reviewed, versioned, and immutable once applied.. Init container runs Flyway with elevated creds; app user read/write DML only. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

---

### 37. Caching: `@Cacheable` and eviction.

**Short answer:** Spring Cache abstraction uses proxies — `@Cacheable`, `@CacheEvict`, `@CachePut`. Provider matters: Caffeine local vs Redis distributed. Cache DTOs, not JPA entities; watch stampede and TTL leaks.

#### What it is
Declarative caching on bean methods integrated with JCache, Caffeine, Redis, etc. At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
`CacheInterceptor` evaluates SpEL keys/conditions. `@Cacheable(sync=true)` on Caffeine reduces stampede. Redis cache needs serialization strategy — JSON/Kryo pitfalls with entities and lazy fields. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss.

#### When to use / when NOT to use
Reference data, expensive computed reads. Not for strongly consistent financial balances without TTL/invalidation discipline. `@CacheEvict` on writes.

#### Production example
Product catalog `@Cacheable("products")` with 15m TTL; `@CacheEvict` on admin update; Redis with tenant prefix in key. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- This often appears only under concurrent load or after deploy when negative paths were never tested.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** `@Cacheable` on repository?
**A:** On '`@Cacheable` on repository': anchor the answer in Caching: `@Cacheable` and eviction.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Cache stampede mitigation?
**A:** On 'Cache stampede mitigation': anchor the answer in Caching: `@Cacheable` and eviction.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Redis vs Caffeine local cache?
**A:** On 'Redis vs Caffeine local cache': anchor the answer in Caching: `@Cacheable` and eviction.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Caching: `@Cacheable` and eviction. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: Spring Cache abstraction uses proxies — `@Cacheable`, `@CacheEvict`, `@CachePut`.. Product catalog `@Cacheable("products")` with 15m TTL; `@CacheEvict` on admin update; Redis with tenant prefix in key. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

---

### 38. Spring Boot DevTools and why prod must disable.

**Short answer:** DevTools enables automatic restart and disables caching for fast local iteration. It must never ship on production classpath — accidental inclusion causes restarts and performance issues.

#### What it is
Development-only starter providing restart classloader and LiveReload. At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
Two classloaders: base (dependencies) vs restart (your code). Property defaults differ (`spring.cache.type=none`). Maven `optional=true` helps exclude from transitive deps. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss.

#### When to use / when NOT to use
Local dev only. Verify prod image/jar excludes `spring-boot-devtools`. CI prod-like tests without DevTools.

#### Production example
Security scan fails build if DevTools in production BOM. Dockerfile uses `spring-boot:repackage` without dev profile deps. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- This often appears only under concurrent load or after deploy when negative paths were never tested.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** DevTools remote restart risks?
**A:** On 'DevTools remote restart risks': anchor the answer in Spring Boot DevTools and why prod must disable.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** How to verify DevTools absent in prod image?
**A:** On 'How to verify DevTools absent in prod image': anchor the answer in Spring Boot DevTools and why prod must disable.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** LiveReload in containers?
**A:** On 'LiveReload in containers': anchor the answer in Spring Boot DevTools and why prod must disable.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Spring Boot DevTools and why prod must disable. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: DevTools enables automatic restart and disables caching for fast local iteration.. Security scan fails build if DevTools in production BOM. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

---

### 39. Fat jar vs layered jar vs native image.

**Short answer:** Fat jars nest dependencies for single-artifact deploy. Layered jars optimize Docker cache (deps vs app layer). GraalVM native images start fast but require closed-world analysis — heavy Hibernate/Spring apps often struggle.

#### What it is
Packaging strategies affecting deploy size, startup time, and build complexity. At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
`JarLauncher` loads nested jars from `BOOT-INF/lib`. Layered layout splits dependencies/application for `docker build` cache hits. Native image AOT compiles with reachability metadata for reflection/resources. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss.

#### When to use / when NOT to use
Layered jar for containerized microservices. Native for CLI, Lambda cold start — evaluate case-by-case for large Spring Data apps. Pick the smallest pattern that meets SLOs; over-abstraction becomes its own incident source.

#### Production example
CI builds layered jar; Dockerfile copies layers separately — rebuild app layer in 10s when only code changes. Native skipped after POC showed 3-week reflection config maintenance. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- This often appears only under concurrent load or after deploy when negative paths were never tested.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** Layered Docker cache benefits?
**A:** On 'Layered Docker cache benefits': anchor the answer in Fat jar vs layered jar vs native image.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** GraalVM native image trade-offs?
**A:** On 'GraalVM native image trade-offs': anchor the answer in Fat jar vs layered jar vs native image.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** CDS / class data sharing?
**A:** On 'CDS / class data sharing': anchor the answer in Fat jar vs layered jar vs native image.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Fat jar vs layered jar vs native image. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: Fat jars nest dependencies for single-artifact deploy.. CI builds layered jar; Dockerfile copies layers separately — rebuild app layer in 10s when only code changes. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

---

### 40. Circular dependency: how Boot 2.6+ changed the world.

**Short answer:** Spring Boot 2.6+ prohibits circular dependencies by default. Fix design — split beans, introduce events, or extract shared collaborator — rather than `@Lazy` band-aids.

#### What it is
When bean A depends on B and B depends on A, context creation cannot resolve order without workaround. At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
Previously Spring could inject proxies to break cycles. Default `spring.main.allow-circular-references=false` fails fast at startup with clear error. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss. Production debugging usually crosses logs, metrics, and condition reports—not just source code.

#### When to use / when NOT to use
Never accept circular deps in new code. `@Lazy` on one constructor param as temporary migration only. Event-driven decoupling for bidirectional domain coupling.

#### Production example
`OrderService` ↔ `PaymentService` cycle broken by extracting `OrderPaymentCoordinator` or publishing `OrderPlacedEvent`. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- This often appears only under concurrent load or after deploy when negative paths were never tested.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** ObjectProvider vs `@Lazy`?
**A:** On 'ObjectProvider vs `@Lazy`': anchor the answer in Circular dependency: how Boot 2.6+ changed the world.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Constructor cycle refactor patterns?
**A:** On 'Constructor cycle refactor patterns': anchor the answer in Circular dependency: how Boot 2.6+ changed the world.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Kotlin lateinit circular deps?
**A:** On 'Kotlin lateinit circular deps': anchor the answer in Circular dependency: how Boot 2.6+ changed the world.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Circular dependency: how Boot 2.6+ changed the world. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: Spring Boot 2.6+ prohibits circular dependencies by default.. `OrderService` ↔ `PaymentService` cycle broken by extracting `OrderPaymentCoordinator` or publishing `OrderPlacedEvent`. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

---

### 41. `ApplicationRunner` vs `CommandLineRunner` vs `InitializingBean`.

**Short answer:** Runners execute once after context is fully started — good for startup tasks needing all beans. Prefer Flyway for schema; use runners for cache warm-up or diagnostics, not critical migrations.

#### What it is
Functional interfaces invoked by `SpringApplication` after refresh completes. At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
`ApplicationRunner` receives `ApplicationArguments`; `CommandLineRunner` raw args. Ordered via `@Order`. Failures prevent ready state if uncaught. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss.

#### When to use / when NOT to use
One-shot startup logic (seed dev data). Avoid long blocking work delaying readiness. Don't replace Flyway or K8s Jobs.

#### Production example
Dev profile runner seeds test merchants; prod runner validates required env vars and exits non-zero if misconfigured. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- This often appears only under concurrent load or after deploy when negative paths were never tested.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** Order of ApplicationRunner execution?
**A:** On 'Order of ApplicationRunner execution': anchor the answer in `ApplicationRunner` vs `CommandLineRunner` vs `InitializingBean`.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Run migrations in runner vs Flyway?
**A:** On 'Run migrations in runner vs Flyway': anchor the answer in `ApplicationRunner` vs `CommandLineRunner` vs `InitializingBean`.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Fail-fast on runner exception?
**A:** On 'Fail-fast on runner exception': anchor the answer in `ApplicationRunner` vs `CommandLineRunner` vs `InitializingBean`.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving `ApplicationRunner` vs `CommandLineRunner` vs `InitializingBean`. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: Runners execute once after context is fully started — good for startup tasks needing all beans.. Dev profile runner seeds test merchants; prod runner validates required env vars and exits non-zero if misconfigured. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

---

### 42. Internationalization and time.

**Short answer:** Use `LocaleResolver` and message sources for i18n. Store instants in UTC (`timestamptz`); inject `Clock` for testable time. Never scatter `new Date()` or `LocalDateTime.now()` without zone strategy.

#### What it is
Locale-aware messaging and correct temporal handling across zones and DST. At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
`MessageSource` resolves keys with locale. `Accept-Language` header drives locale in REST. JPA maps `Instant` to UTC timestamps. `Clock.systemUTC()` bean swapped in tests.

#### When to use / when NOT to use
User-facing messages externalized in properties files. API contracts document timezone (always UTC ISO-8601 recommended). Pick the smallest pattern that meets SLOs; over-abstraction becomes its own incident source.

#### Production example
Promotion ends `2026-12-31T23:59:59Z` stored as `Instant`; UI converts to user zone. Tests use fixed `Clock` at boundary instant. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- This often appears only under concurrent load or after deploy when negative paths were never tested.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** `@JsonFormat` vs global Jackson config?
**A:** On '`@JsonFormat` vs global Jackson config': anchor the answer in Internationalization and time.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Store UTC in DB always?
**A:** On 'Store UTC in DB always': anchor the answer in Internationalization and time.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** User timezone in audit logs?
**A:** On 'User timezone in audit logs': anchor the answer in Internationalization and time.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Internationalization and time. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: Use `LocaleResolver` and message sources for i18n.. Promotion ends `2026-12-31T23:59:59Z` stored as `Instant`; UI converts to user zone. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

---

### 43. File upload limits and streaming.

**Short answer:** Configure multipart limits; stream large files to object storage — never load gigabytes into `byte[]`. Validate type, scan for malware, authorize per tenant.

#### What it is
Handling `multipart/form-data` uploads in Spring MVC/WebFlux. At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
`StandardServletMultipartResolver` buffers to disk above threshold. `spring.servlet.multipart.max-file-size` and `max-request-size` enforce limits. `MultipartFile.getInputStream()` for streaming to S3/GCS client. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss.

#### When to use / when NOT to use
Direct upload to blob store with pre-signed URLs for very large files. Sync upload through app only when size bounded and scanned. Pick the smallest pattern that meets SLOs; over-abstraction becomes its own incident source.

#### Production example
10MB limit for avatar images; stream to S3 via `TransferManager`; async virus scan via queue on `ObjectCreated` event. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- This often appears only under concurrent load or after deploy when negative paths were never tested.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** Multipart vs streaming upload?
**A:** On 'Multipart vs streaming upload': anchor the answer in File upload limits and streaming.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Virus scan in pipeline?
**A:** On 'Virus scan in pipeline': anchor the answer in File upload limits and streaming.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** S3 presigned vs server upload?
**A:** On 'S3 presigned vs server upload': anchor the answer in File upload limits and streaming.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving File upload limits and streaming. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: Configure multipart limits; stream large files to object storage — never load gigabytes into `byte[]`.. 10MB limit for avatar images; stream to S3 via `TransferManager`; async virus scan via queue on `ObjectCreated` event. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

---

### 44. WebSocket / STOMP in Spring.

**Short answer:** Spring WebSocket + STOMP provides messaging over WebSocket with broker abstraction. In-memory broker doesn't scale horizontally — use RabbitMQ/ActiveMQ relay for multi-instance fan-out.

#### What it is
Real-time bidirectional communication for dashboards, chat, live updates. At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
Handshake upgrades HTTP to WebSocket. STOMP frames routed to `@MessageMapping` methods. Simple broker `/topic`, `/queue` in single node. External broker relay shares subscriptions across pods.

#### When to use / when NOT to use
WebSocket when server push needed; SSE simpler for one-way streams. Authenticate at CONNECT; authorize destinations. Pick the smallest pattern that meets SLOs; over-abstraction becomes its own incident source.

#### Production example
Live order status: client subscribes `/topic/orders/{id}`; service publishes on state change via `SimpMessagingTemplate`. Rabbit relay for 10 pod replicas. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- This often appears only under concurrent load or after deploy when negative paths were never tested.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** STOMP broker relay vs simple broker?
**A:** On 'STOMP broker relay vs simple broker': anchor the answer in WebSocket / STOMP in Spring.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** WebSocket auth with JWT?
**A:** On 'WebSocket auth with JWT': anchor the answer in WebSocket / STOMP in Spring.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Scale WebSocket on K8s?
**A:** On 'Scale WebSocket on K8s': anchor the answer in WebSocket / STOMP in Spring.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving WebSocket / STOMP in Spring. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: Spring WebSocket + STOMP provides messaging over WebSocket with broker abstraction.. Live order status: client subscribes `/topic/orders/{id}`; service publishes on state change via `SimpMessagingTemplate`. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

---

### 45. How do you debug "No qualifying bean"?

**Short answer:** Trace component scan roots, missing `@Configuration`, failed `@Conditional` auto-config, active profile, test slice exclusions, duplicate beans needing `@Qualifier`, and classpath/module dependencies. In microservices, the same idea often appears at the network boundary as well as inside a single JVM.

#### What it is
The systematic diagnosis of `NoSuchBeanDefinitionException` or `NoUniqueBeanDefinitionException` at startup or test time. At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
Check `ConditionEvaluationReport` (--debug). Verify `@ComponentScan` includes bean's package. Auto-config skipped if `@ConditionalOnClass` false. Test slices exclude beans intentionally.

#### When to use / when NOT to use
Apply structured checklist before random `@Import`. Fix root cause — don't `@Autowired(required=false)` production deps. Pick the smallest pattern that meets SLOs; over-abstraction becomes its own incident source.

#### Production example
Kafka listener fails: `KafkaTemplate` missing because `spring-kafka` not on classpath of that module — add dependency or exclude listener config in profile. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- This often appears only under concurrent load or after deploy when negative paths were never tested.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** Read `ConditionEvaluationReport`?
**A:** On 'Read `ConditionEvaluationReport`': anchor the answer in How do you debug "No qualifying bean"?—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** `@ConditionalOnMissingBean` debugging?
**A:** On '`@ConditionalOnMissingBean` debugging': anchor the answer in How do you debug "No qualifying bean"?—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Bean overriding in Boot 2.1+?
**A:** On 'Bean overriding in Boot 2.1+': anchor the answer in How do you debug "No qualifying bean"?—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving How do you debug "No qualifying bean"?. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: Trace component scan roots, missing `@Configuration`, failed `@Conditional` auto-config, active profile, test slice exclusions, duplicate beans needing `@Qualifier`, and classpath/module dependencies.. Kafka listener fails: `KafkaTemplate` missing because `spring-kafka` not on classpath of that module — add dependency or exclude listener config in profile. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

---

### 46. `BeanPostProcessor` vs `BeanFactoryPostProcessor`.

**Short answer:** `BeanFactoryPostProcessor` mutates bean definitions before instantiation (configuration class processing). `BeanPostProcessor` wraps/modifies bean instances (AOP auto-proxy creation). Both power Spring's magic — use sparingly in application code.

#### What it is
Extension hooks at definition-time vs instance-time in the container lifecycle. At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
`ConfigurationClassPostProcessor` parses `@Configuration` and `@Bean` methods — a BFPP. `AnnotationAwareAspectJAutoProxyCreator` is a BPP creating proxies. Order annotations control interaction. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss.

#### When to use / when NOT to use
Framework/library authors use these; application teams rarely implement custom ones. Prefer standard extension points (advice, filters, customizers). Pick the smallest pattern that meets SLOs; over-abstraction becomes its own incident source.

#### Production example
Third-party library registers BPP adding metrics to all `@Repository` beans — understand ordering if your BPP also wraps repositories. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- This often appears only under concurrent load or after deploy when negative paths were never tested.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** `InstantiationAwareBeanPostProcessor`?
**A:** On '`InstantiationAwareBeanPostProcessor`': anchor the answer in `BeanPostProcessor` vs `BeanFactoryPostProcessor`.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** `@Role(ROLE_INFRASTRUCTURE)`?
**A:** On '`@Role(ROLE_INFRASTRUCTURE)`': anchor the answer in `BeanPostProcessor` vs `BeanFactoryPostProcessor`.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** CGLIB `@Configuration` enhancement?
**A:** On 'CGLIB `@Configuration` enhancement': anchor the answer in `BeanPostProcessor` vs `BeanFactoryPostProcessor`.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving `BeanPostProcessor` vs `BeanFactoryPostProcessor`. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: `BeanFactoryPostProcessor` mutates bean definitions before instantiation (configuration class processing).. Third-party library registers BPP adding metrics to all `@Repository` beans — understand ordering if your BPP also wraps repositories. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

---

### 47. `@Transactional` + Kafka listener.

**Short answer:** Align Kafka acknowledgment with DB transaction boundaries deliberately. Common pattern: process in TX, commit DB, then ack — crash between requires idempotent consumer. EOS needs transactional producer + `read_committed` + idempotent handlers. At-least-once delivery and idempotent handlers are non-negotiable across service boundaries.

#### What it is
Integrating Spring Kafka listener container transactions with JPA/JDBC work. At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
`ChainedKafkaTransactionManager` or separate TX with manual ack. `AckMode.MANUAL`/`RECORD` vs auto. Idempotent producer and consumer store dedupe keys. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss.

#### When to use / when NOT to use
Transactional outbox for reliable publish. Kafka EOS within broker segment only — not across HTTP. Idempotency keys on consumer side always.

#### Production example
Consumer reads `OrderCreated`; upsert read model in `@Transactional` method; ack after commit; on redelivery, unique constraint + idempotent upsert succeeds. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever. At-least-once delivery and idempotent handlers are non-negotiable across service boundaries.

#### Common mistakes
- This often appears only under concurrent load or after deploy when negative paths were never tested.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** Outbox vs Kafka TX?
**A:** On 'Outbox vs Kafka TX': anchor the answer in `@Transactional` + Kafka listener.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** `DefaultErrorHandler` and DLT?
**A:** On '`DefaultErrorHandler` and DLT': anchor the answer in `@Transactional` + Kafka listener.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Exactly-once semantics limits?
**A:** On 'Exactly-once semantics limits': anchor the answer in `@Transactional` + Kafka listener.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** On-call: orders show inconsistent state after a deploy affecting `@Transactional` + Kafka listener. Symptoms appear only under concurrent load; rollback is available but root cause is unclear.

**Model answer:** I start from: Align Kafka acknowledgment with DB transaction boundaries deliberately.. Consumer reads `OrderCreated`; upsert read model in `@Transactional` method; ack after commit; on redelivery, unique constraint + idempotent upsert succeeds. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

---

### 48. Security headers and CSRF for a React SPA.

**Short answer:** Bearer tokens in memory reduce CSRF risk vs cookie sessions. If using cookies, set `HttpOnly`, `SameSite`, and CSRF tokens. Add CSP, HSTS at gateway; CORS allowlist exact origins — never `*` with credentials. Fail-closed auth and explicit audience validation prevent subtle token confusion attacks.

#### What it is
Browser security mechanisms for SPA + API architectures. At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
CSRF protects cookie-authenticated mutating requests. JWT in Authorization header not automatically sent by browser — different threat model (XSS stealing token). Spring Security `csrf()` config and `headers()` for CSP/frame options. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss.

#### When to use / when NOT to use
Disable CSRF for stateless JWT APIs with eyes open. Enable for session-cookie auth. CORS is not a substitute for authentication.

#### Production example
BFF sets `HttpOnly` session cookie; SPA includes CSRF header from meta tag. API gateway adds HSTS and strict CSP. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- This often appears only under concurrent load or after deploy when negative paths were never tested.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** SameSite=Lax vs Strict?
**A:** On 'SameSite=Lax vs Strict': anchor the answer in Security headers and CSRF for a React SPA.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Double-submit cookie pattern?
**A:** On 'Double-submit cookie pattern': anchor the answer in Security headers and CSRF for a React SPA.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** OAuth PKCE for SPA?
**A:** On 'OAuth PKCE for SPA': anchor the answer in Security headers and CSRF for a React SPA.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Security review flags auth gaps after a SPA release related to Security headers and CSRF for a React SPA. Some users report intermittent 403; tokens appear valid in logs.

**Model answer:** I start from: Bearer tokens in memory reduce CSRF risk vs cookie sessions.. BFF sets `HttpOnly` session cookie; SPA includes CSRF header from meta tag. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

---

### 49. Configuration in Kubernetes.

**Short answer:** Inject config via env vars from ConfigMap/Secret, mounted files, or `SPRING_APPLICATION_JSON`. Reload requires restart or Spring Cloud Kubernetes refresh — prefer immutable pods with rolled deploys.

#### What it is
Externalized configuration pattern for Spring Boot on Kubernetes. At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
Relaxed binding maps env to properties. Secrets base64-encoded at rest — still protect RBAC. Volume-mounted `application.yaml` overlays defaults. Hash annotation triggers rollout on ConfigMap change.

#### When to use / when NOT to use
ConfigMap for non-secret toggles; Secret for credentials via CSI/driver when possible. Spring Cloud Config Server only when centralized dynamic config truly needed. Pick the smallest pattern that meets SLOs; over-abstraction becomes its own incident source.

#### Production example
Deployment env: `SPRING_DATASOURCE_URL` from Secret; feature flags ConfigMap mounted at `/config/application.yaml`; pod template annotation checksum restarts on flag change. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- This often appears only under concurrent load or after deploy when negative paths were never tested.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** External Secrets Operator?
**A:** On 'External Secrets Operator': anchor the answer in Configuration in Kubernetes.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** `@RefreshScope` pitfalls?
**A:** On '`@RefreshScope` pitfalls': anchor the answer in Configuration in Kubernetes.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Config vs secret rotation without downtime?
**A:** On 'Config vs secret rotation without downtime': anchor the answer in Configuration in Kubernetes.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Configuration in Kubernetes. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: Inject config via env vars from ConfigMap/Secret, mounted files, or `SPRING_APPLICATION_JSON`.. Deployment env: `SPRING_DATASOURCE_URL` from Secret; feature flags ConfigMap mounted at `/config/application.yaml`; pod template annotation checksum restarts on flag change. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

---

### 50. What "Spring Boot internals" means at 10 years.

**Short answer:** A senior engineer explains proxy types, filter vs interceptor vs AOP ordering, tunes Tomcat+Hikari+Kafka together, disables OSIV intentionally, designs transaction boundaries, reads condition reports, secures actuators, and tells war stories where swallowed exceptions committed bad data. In microservices, the same idea often appears at the network boundary as well as inside a single JVM.

#### What it is
The cumulative depth expected of experienced Spring Boot practitioners — not API trivia, but operational and architectural fluency. At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
Auto-config conditions, AOP proxy chains, transaction synchronization, servlet filter ordering, and observability hooks interlock in production systems. Debugging crosses layers: metrics → traces → logs → condition report → SQL stats. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss. Production debugging usually crosses logs, metrics, and condition reports—not just source code.

#### When to use / when NOT to use
Apply this depth when designing services, reviewing incidents, and mentoring — not when a CRUD prototype suffices. Pick the smallest pattern that meets SLOs; over-abstraction becomes its own incident source. State what you rejected and why—trade-off honesty beats pattern maximalism.

#### Production example
Incident: orders stuck PLACED — trace shows TX committed after caught `PaymentException`; fix rollback rules; add integration test asserting DB state on decline; disable OSIV; add outbox for `OrderPlaced` events. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- Junior answers: "Spring is magic"; senior gap: can't explain why `@Transactional` failed on self-call or why pool exhausted. This often appears only under concurrent load or after deploy when negative paths were never tested.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** Whiteboard request lifecycle with security and TX?
**A:** Client → ingress/gateway → servlet filter chain (security, trace ID) → `DispatcherServlet` → handler interceptor → `@Controller` → service `@Transactional` boundary → repository → DB. Response path serializes DTO (not entity with OSIV lazy loads). Security context from JWT validated in resource server filter. Mention where TX opens/commits and where connection returns to pool—after service method, not after JSON write if OSIV off.

**Q:** Design order service with idempotency and outbox?
**A:** On 'Design order service with idempotency and outbox': anchor the answer in What "Spring Boot internals" means at 10 years.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Boot 2 → 3 migration pitfalls?
**A:** Jakarta namespace (`javax.*` → `jakarta.*`), Spring Security 6 lambda DSL, removal of deprecated properties, `spring-boot-starter-parent` 3.x baseline Java 17. PathPatternParser default, changes to `spring.config.import`, circular references disallowed by default. Run OpenRewrite or Boot migration guide; fix `javax.annotation` imports; retest security filter chains and actuator exposure.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving What "Spring Boot internals" means at 10 years. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: A senior engineer explains proxy types, filter vs interceptor vs AOP ordering, tunes Tomcat+Hikari+Kafka together, disables OSIV intentionally, designs transaction boundaries, reads condition reports, secures actuators, and tells war stories where swallowed exceptions committed bad data.. Incident: orders stuck PLACED — trace shows TX committed after caught `PaymentException`; fix rollback rules; add integration test asserting DB state on decline; disable OSIV; add outbox for `OrderPlaced` events. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```bash
java -jar app.jar --debug 2>&1 | grep "CONDITIONS EVALUATION REPORT"
spring.jpa.open-in-view=false
management.endpoint.health.show-details=when_authorized
```

That's the senior Spring interview.

---

### 51. Spring Batch: chunk-oriented processing, skip/retry, job parameters.

**Short answer:** Spring Batch models ETL as Job → Step → ItemReader/Processor/Writer with chunk commits (e.g., 500 rows per TX). Skip policies tolerate bad records; retry with backoff handles transient failures. Job parameters (`@JobParameter`) make runs idempotent — same job name + params cannot re-run unless `RunIdIncrementer` or new param. Seniors design restartability: persisted step execution state survives JVM crash.

#### What it is
Batch framework for high-volume, fault-tolerant offline processing integrated with Spring transaction and data access. Chunk step: read until chunk size, process, write, commit, repeat.

#### How it works (internals)
`ChunkOrientedTasklet` drives loop; `PlatformTransactionManager` commits per chunk. Skip limit throws `SkipLimitExceededException` when exceeded. RetryTemplate wraps processor/writer for `DataAccessException`. JobRepository stores metadata in JDBC — restart from last successful chunk boundary.

#### When to use / when NOT to use
Nightly ingestion, reconciliation, bulk migration — Batch. Real-time streaming — Kafka Streams or reactive pipeline. Do not use Batch for single-row CRUD triggered by HTTP.

#### Production example
Settlement file 2M rows: chunk 1000, skip policy for malformed lines up to 0.1%, retry 3x on deadlock. Job param `fileDate=2026-09-05` prevents accidental double load. Failed job restarts from step 3 chunk 450 after pod OOM — no duplicate settlements due to idempotent writer keys.

#### Common mistakes
Chunk size equals entire file in one TX — long locks and OOM. No job parameters — reruns duplicate output. Skip without dead-letter file — silent data loss audit gap.

#### Interview follow-ups (with model answers)

**Q:** Chunk size vs connection pool?
**A:** Each chunk holds one connection for TX duration — chunk commit releases. Rule of thumb: chunk processing time < few seconds; pool size must support parallel steps if partitioned step runs. Large chunks increase rollback blast radius on failure. Tune with step execution metrics: read count, skip count, commit interval.

**Q:** Parallel steps and partitioning?
**A:** Master step partitions by key range (order id mod N); slave steps run on thread pool or remote workers. Requires idempotent partition boundaries and merge strategy. Grid size matches available workers; oversubscribing partitions starves pool without throughput gain.

#### Scenario probe

Nightly batch reprocessed same file after operator rerun without new job parameter — duplicate payments posted.

**Model answer:** JobInstance uniqueness is job name + parameters — rerunning identical params fails or no-ops depending on config; operator used `RunIdIncrementer` thinking it was safe. Fix: business idempotency on paymentId in writer; block rerun unless `force=true` param with audit; document runbook. Add integration test asserting second launch with same fileDate skips or fails closed.

#### Code / config (when useful)

```java
@Bean
Step ingestStep(JobRepository repo, PlatformTransactionManager tx) {
    return new StepBuilder("ingest", repo)
        .<Input, Output>chunk(500, tx)
        .reader(reader()).processor(processor()).writer(writer())
        .faultTolerant().skip(BadRecordException.class).skipLimit(100)
        .retry(DeadlockLoserDataAccessException.class).retryLimit(3)
        .build();
}
```

---

### 52. Spring Integration: channels, adapters, idempotent receivers.

**Short answer:** Spring Integration implements enterprise integration patterns: Message channels connect endpoints; adapters bridge external systems (JMS, SFTP, HTTP). Idempotent receiver deduplicates using metadata store (`JdbcMessageStore`) so redelivered messages skip processing. Use for file drops, legacy MQ bridges, and complex routing — not for simple REST CRUD.

#### What it is
Message-driven middleware in Spring: `MessageChannel`, `@ServiceActivator`, transformers, filters, gateways abstracting plumbing from domain handlers.

#### How it works (internals)
DirectChannel synchronous handoff; QueueChannel buffers; PublishSubscribeChannel broadcasts. Inbound channel adapter polls SFTP or listens JMS; outbound sends reply. Idempotent interceptor checks message id against store before handler; on duplicate, discards or routes to DLQ audit.

#### When to use / when NOT to use
Multi-protocol ingestion (SFTP + JMS + HTTP webhook) with enrichment pipeline — Integration. Single Kafka consumer with Spring Kafka — skip Integration unless needed for DSL consistency across legacy flows.

#### Production example
Bank statement files: SFTP inbound adapter → virus scan channel → parser → JPA persist; idempotent key = file hash + line number in metadata store. Redelivery after crash does not double-book transactions.

#### Common mistakes
Unbounded QueueChannel without backpressure — OOM. No idempotency on at-least-once sources. Business logic in transformer spaghetti — keep handlers thin.

#### Interview follow-ups (with model answers)

**Q:** Integration vs Kafka-only architecture?
**A:** Kafka for event backbone and replay; Integration for edge adapters (SFTP, email) and content-based routing to multiple sinks without writing boilerplate polling threads. Can publish from Integration gateway to Kafka topic as bridge. Choose based on team familiarity and operational tooling — not religion.

**Q:** Error channel and DLQ?
**A:** `errorChannel` global handler for failed messages; route to DLQ channel with header enrichment (original stack, correlation id). Retry advice on transient errors with exponential backoff. Monitor DLQ depth alert like any queue.

#### Scenario probe

JMS redelivery after handler threw post-commit exception — customer charged twice.

**Model answer:** Handler not idempotent; JMS redelivers. Add idempotent receiver with business key in JDBC store checked in same TX as side effect, or outbox pattern. Integration `IdempotentReceiverInterceptor` + transactional handler. Test: simulate exception after write, redeliver, assert single charge.

---

### 53. Spring Modulith: modules, events, `@ApplicationModuleTest`.

**Short answer:** Spring Modulith structures monolith into named modules with enforced boundaries (`@ApplicationModule`, package-info) and documents architecture via generated diagrams. Module events (`ApplicationModuleListener`) replace ad-hoc Spring `@EventListener` cross-package calls with explicit API. `@ApplicationModuleTest` bootstraps slice of one module for fast integration tests. Use to prevent big-ball-of-mud before splitting microservices.

#### What it is
Modular monolith toolkit: ArchUnit-style verification at build time, event-based inter-module communication, test slices per module.

#### How it works (internals)
Modules declared in `package-info.java` or `@Modulithic`; Spring Modulith detects cycles and illegal dependencies. Events published within module boundary; listeners in other modules consume published API types only. `@ApplicationModuleTest` loads minimal context for `orders` module without pulling `billing` internals.

#### When to use / when NOT to use
Growing monolith with 5+ teams touching same repo — Modulith guardrails. Greenfield two-service app — overkill. Stepping stone to extract module to microservice when boundary already clean.

#### Production example
E-commerce monolith: `catalog`, `cart`, `checkout` modules; checkout listens to `CartFinalized` event only through published event type; ArchUnit fails build if checkout imports `catalog.internal`. Module test runs checkout flow in 8s vs 90s full context.

#### Common mistakes
Treating modules as folders without enforcement — drift returns. Synchronous `@TransactionalEventListener` across modules — hidden coupling. Extracting microservice before stable module API — duplicates pain.

#### Interview follow-ups (with model answers)

**Q:** Modulith vs microservices?
**A:** Modulith keeps deployment single unit with modular discipline — lower ops cost, same process calls become events later. Microservices add network failure modes. Modulith is migration path: prove boundaries, then extract hottest module. Interviewers want honest trade-off not microservice maximalism.

**Q:** How are module events different from generic Spring events?
**A:** Modulith documents and validates event types as module API; tooling generates event catalog and ASCII/PlantUML diagrams. Encourages immutable event records and versioned schemas preparing for Kafka extraction.

#### Scenario probe

Build fails after developer imported `com.acme.billing.internal.repo` from orders module — intended?

**Model answer:** Yes — Modulith verification catches illegal dependency before merge. Fix: expose billing port interface in billing API package; orders calls billing service facade or listens to invoice event. Teaches that "same repo" does not mean "same module boundary."

---

### 54. Resilience4j with Spring Boot 3 (`resilience4j-spring-boot3`).

**Short answer:** Resilience4j provides circuit breaker, rate limiter, bulkhead, retry, time limiter as functional decorators with metrics. Spring Boot 3 starter binds YAML config to named instances and AOP annotations (`@CircuitBreaker`, `@Bulkhead`). Prefer bulkhead + timeout before blind retry on payment paths. Expose health indicators and Micrometer metrics for breaker state transitions.

#### What it is
Lightweight fault-tolerance library replacing Hystrix; integrates with Spring Boot 3 via `resilience4j-spring-boot3` and optional Micrometer/Prometheus.

#### How it works (internals)
Circuit states CLOSED/OPEN/HALF_OPEN; failure rate threshold opens circuit; wait duration in open then probe. Bulkhead limits concurrent calls; excess fails fast. AOP aspect wraps `@CircuitBreaker(name="payments")` methods; config in `application.yml` under `resilience4j.circuitbreaker.instances.payments`.

#### When to use / when NOT to use
External dependency protection (fraud API, legacy mainframe). Not for masking DB pool exhaustion — fix pool and queries. Combine retry only on idempotent reads or with idempotency keys.

#### Production example
Fraud service breaker: 50% failure rate over 10 calls opens 30s; fallback returns manual review queue. Bulkhead 20 concurrent — prevents fraud slowness consuming all Tomcat threads. Grafana alert on `resilience4j.circuitbreaker.state{name="fraud"} == OPEN`.

#### Common mistakes
Retry on non-idempotent POST without key — duplicates. Circuit breaker on internal DB — hides root cause. Default configs copied from blog — never tuned to SLA.

#### Interview follow-ups (with model answers)

**Q:** Resilience4j vs Spring Cloud Circuit Breaker abstraction?
**A:** Spring Cloud Circuit Breaker provides facade over Resilience4j or others — use if multi-impl needed. Direct Resilience4j fine for Boot-only services. Know YAML keys and metric names regardless of facade.

**Q:** Half-open probe storm?
**A:** `permittedNumberOfCallsInHalfOpenState` limits probes; without it, traffic floods recovering dependency. Tune `slowCallDurationThreshold` to treat latency as failure — critical for soft outages.

#### Scenario probe

Breaker stuck OPEN after dependency recovered — users permanently on fallback.

**Model answer:** `waitDurationInOpenState` too long or health check not wired to force half-open. Verify metrics transition; add integration test flipping mock failure to success. Document manual `transitionToClosed` via actuator if supported, or redeploy with reset. Root fix: half-open permits and dependency synthetic canary.

#### Code / config (when useful)

```yaml
resilience4j.circuitbreaker.instances.fraud:
  slidingWindowSize: 20
  failureRateThreshold: 50
  waitDurationInOpenState: 30s
  permittedNumberOfCallsInHalfOpenState: 5
```

---

### 55. SpringDoc OpenAPI 3 + springdoc-openapi-starter-webmvc-ui.

**Short answer:** SpringDoc generates OpenAPI 3 spec from Spring MVC controllers, `@Schema` annotations, and security config at `/v3/api-docs`. `springdoc-openapi-starter-webmvc-ui` serves Swagger UI. Prefer annotation + java record DTOs for accurate schemas; disable in prod or protect with auth. Contract-first teams export spec for consumer-driven tests.

#### What it is
Replacement for Springfox on Boot 3 / Jakarta — auto-configures OpenAPI grouped by packages, supports OAuth2, problem details, Pageable.

#### How it works (internals)
`OpenAPIService` introspects `RequestMappingHandlerMapping`, builds paths/components. `@Operation`, `@ApiResponse` enrich docs. UI at `/swagger-ui.html` or `/swagger-ui/index.html` depending on version. `springdoc.api-docs.enabled=false` in prod profile.

#### When to use / when NOT to use
Internal API catalog, partner integration, codegen for clients. Public internet prod without auth — security risk. Alternative: export spec in CI artifact only.

#### Production example
Partner onboarding uses published `/v3/api-docs.yaml` from staging; breaking change fails CI consumer contract test. Prod disables UI; gateway serves cached spec to authorized partners only.

#### Common mistakes
Returning entities with lazy fields — schema lies or triggers OSIV. Missing `@Schema(requiredMode=REQUIRED)` on validation annotations mismatch. Springfox migration without updating `@Api` to `@Tag`.

#### Interview follow-ups (with model answers)

**Q:** SpringDoc vs manual OpenAPI YAML?
**A:** Code-first SpringDoc stays DRY with controllers — drift if annotations neglected. Spec-first OpenAPI generator for greenfield public APIs with strict review. Hybrid: generate baseline, commit spec, diff in PR.

**Q:** Hiding internal endpoints?
**A:** `@Hidden` on controller/method; or `GroupedOpenApi` beans exposing public subset. Actuator and admin paths excluded via `springdoc.paths-to-exclude`.

#### Scenario probe

Swagger UI exposed on prod domain — scanner finds admin endpoints with weak auth.

**Model answer:** Disable springdoc in prod profile; restrict via network policy; separate management port. Security review checklist: no UI on public ingress, spec does not document internal ops routes. Pen test finding closed in same release.

---

### 56. Spring Boot 3 AOT/native image constraints checklist.

**Short answer:** AOT processing (`spring-aot-maven-plugin`) and GraalVM native image require closed-world assumptions: no classpath scanning surprises, no dynamic proxies without hints, no CGLIB beans without registration. Checklist: run `nativeTest`, register reflection for Jackson types, replace `@PropertySource` dynamic features, verify Flyway/Liquibase, test PGO in CI. Native wins cold start and memory; loses peak throughput and debugging ease.

#### What it is
Spring Boot 3.0+ ahead-of-time compilation for GraalVM native executables — common for serverless and edge, not default for all monoliths.

#### How it works (internals)
Build time analyzes bean definitions; generates static config; `RuntimeHints` register reflection/proxy/resource needs. Native image `--initialize-at-build-time` for logging frameworks per docs. Spring Boot 3.2+ improved reachability metadata via tracing agent in CI.

#### When to use / when NOT to use
Lambda, Knative, CLI tools needing <100ms startup — native. Heavy dynamic Groovy, bytecode gen, unknown third-party reflection — JVM mode. Measure before mandate: some apps 30% slower peak on native.

#### Production example
Auth microservice on AWS Lambda native: cold start 80ms vs 4s JVM. Required `RuntimeHintsRegistrar` for custom JWT parser reflection. Batch job stayed JVM — long-running throughput mattered more.

#### Common mistakes
Assuming same `-D` flags work without testing native. Missing hint for `@ConfigurationProperties` binding on record — silent default failures. No CI native build — prod-only discovery of incompatibility.

#### Interview follow-ups (with model answers)

**Q:** Key differences from JVM deployment?
**A:** No JIT peak optimization same way; classpath fixed at build; thread dumps and some agents limited. G1 vs native memory profile differs — load test both. Rollback plan must include JVM artifact parallel track until native proven.

**Q:** How to find missing reflection hints?
**A:** Run app with GraalVM tracing agent during integration tests; merge `reflect-config.json`. Spring Boot 3.3+ `spring-boot-test-native` and reachability metadata reduce manual work. Fail CI on native test suite red.

#### Scenario probe

Native build succeeds but `@PostConstruct` config reads env var unavailable at build time — wrong datasource URL baked in.

**Model answer:** Confused build-time vs runtime property — native image embeds some defaults incorrectly if `@Value` resolved too early. Use runtime hints and documented property binding patterns; verify with testcontainer against real env injection. Checklist item: smoke test native binary with prod-like env file in CI.

---

### 57. `@ControllerAdvice` + RFC 9457 Problem Details (Spring 6.1+).

**Short answer:** Spring 6.1+ aligns error responses with RFC 9457 Problem Details (`application/problem+json`): `type`, `title`, `status`, `detail`, `instance`. `@ControllerAdvice` with `@ExceptionHandler` returning `ProblemDetail` or `ResponseEntity<ProblemDetail>` gives consistent API errors without leaking stack traces. Map domain exceptions to stable `type` URIs for client branching.

#### What it is
Standard JSON error envelope replacing ad-hoc `{ "error": "..." }` maps; integrates with Spring MVC and WebFlux exception handlers.

#### How it works (internals)
`ProblemDetail.forStatusAndDetail(HttpStatus.CONFLICT, "Stock insufficient")`; set `setType(URI.create("https://api.example.com/problems/out-of-stock"))`; add custom properties via `setProperty`. `@ControllerAdvice` ordered handlers; security exceptions may need separate advice with higher precedence.

#### When to use / when NOT to use
All public REST APIs should use problem details for 4xx/5xx. Internal admin tools may stay plain text. Do not put PII in `detail` — log server-side only.

#### Production example
Order API returns 409 problem with type `inventory-conflict` — mobile app shows localized message from type mapping, not raw English detail. Global handler logs exception id matching `instance` field for support tickets.

#### Common mistakes
Returning stack trace in extension field in prod. Different error shapes per controller — breaks clients. Missing `Content-Type: application/problem+json`.

#### Interview follow-ups (with model answers)

**Q:** Problem Details vs `@Valid` field errors?
**A:** Validation can return 400 ProblemDetail with `invalid-params` extension array (Spring's `MethodArgumentNotValidException` handler pattern). Keep one advice class for consistency. RFC 7807 legacy vs 9457 — Spring 6.1 documents migration; know both URIs in older clients.

**Q:** Ordering multiple `@ControllerAdvice`?
**A:** `@Order(Ordered.HIGHEST_PRECEDENCE)` on specific domain advice; generic `Exception` handler lowest. Security access denied may need `@RestControllerAdvice` scoped to package.

#### Scenario probe

Pen test: 500 errors include full SQL in JSON body from uncaught `DataIntegrityViolationException`.

**Model answer:** Add `@ExceptionHandler` mapping to generic 409/400 problem without SQL; log full cause with correlation id. Enable `server.error.include-message=never` in prod. Regression test asserts response body has no `SQLException` substring.

#### Code / config (when useful)

```java
@ExceptionHandler(OutOfStockException.class)
ProblemDetail handle(OutOfStockException ex, HttpServletRequest req) {
    var pd = ProblemDetail.forStatusAndDetail(CONFLICT, "Insufficient stock");
    pd.setType(URI.create("https://example.com/problems/out-of-stock"));
    pd.setInstance(URI.create(req.getRequestURI()));
    return pd;
}
```

---

### 58. Spring Boot Actuator custom metrics and `@Observed`.

**Short answer:** Register custom Micrometer metrics via `MeterRegistry` (`Counter`, `Timer`, `Gauge`) or declarative `@Observed(name="orders.place")` on service methods (Micrometer Observation API). Expose via `/actuator/prometheus` for alerting. Name metrics consistently (`app.orders.placed`); tag with low cardinality (tenant tier, not user id).

#### What it is
Actuator brings production observability endpoints; Micrometer is facade; `@Observed` (AOP) creates span + timer around methods when observation registry present.

#### How it works (internals)
`@Observed` processed by `ObservedAspect`; creates `Observation` with name, contextual tags, supports `@SpanTag` on parameters. Custom beans: `registry.counter("payments.declined", "reason", code).increment()`. Bind to OpenTelemetry exporter in Boot 3.2+ observability stack.

#### When to use / when NOT to use
Business KPIs (orders placed, payment failures) as custom metrics — essential. `@Observed` on every private method — noise. High-cardinality tags — Prometheus explosion.

#### Production example
`@Observed(name="checkout.place", contextualName="checkout")` on service — traces link to payment client span. Custom counter `checkout.inventory.shortage` drives product alert separate from infra CPU alerts.

#### Common mistakes
Metric names without convention — duplicate counters. Timer on synchronous code without recording exceptions. Exposing all actuator endpoints publicly.

#### Interview follow-ups (with model answers)

**Q:** `@Timed` vs `@Observed`?
**A:** `@Timed` legacy Micrometer timer only. `@Observed` unifies metrics + tracing (Observation API) — prefer in Boot 3.2+. Migrate `@Timed` gradually; both can coexist during transition.

**Q:** Testing custom metrics?
**A:** `@SpringBootTest` autowire `MeterRegistry`, assert `registry.find("app.orders.placed").counter().count() == 1` after action. Use `simple` registry in unit tests; Testcontainers not required for metric unit tests.

#### Scenario probe

Dashboard shows payment success rate drop but infra green — no business metrics existed.

**Model answer:** Only JVM/HTTP metrics — cannot see decline reason. Add counters by outcome and `@Observed` on payment client; SLO dashboard on business metric. Incident would have pinpointed fraud provider errors in minutes. Postmortem action: metric checklist in definition of done.

---

### 59. Testcontainers: `@ServiceConnection` and reusable containers.

**Short answer:** Spring Boot 3.1+ `@ServiceConnection` on `@Container static PostgreSQLContainer` auto-wires JDBC URL/credentials to `DataSource` without manual `@DynamicPropertySource`. Reusable containers (`withReuse(true)` + `testcontainers.reuse.enable=true`) speed local dev but risk state leakage — isolate tests with `@Transactional` rollback or dedicated schemas. CI should not rely on reuse unless container hygiene enforced.

#### What it is
Integration tests against real Postgres/Kafka/Redis via Docker; ServiceConnection eliminates boilerplate property wiring.

#### How it works (internals)
Testcontainers spins Docker image; `@ServiceConnection` registers `ConnectionDetails` bean consumed by Boot auto-config. Reuse keeps container running between test JVM restarts on developer machine. `@Testcontainers(disabledWithoutDocker = true)` skips gracefully on CI without Docker.

#### When to use / when NOT to use
Repository/integration tests needing dialect-specific SQL — Testcontainers. Pure unit tests with mocks — no container. H2 for Oracle-specific SQL — false confidence.

#### Production example
CI pipeline runs `@SpringBootTest` with `@ServiceConnection PostgreSQL` — catches `jsonb` query bug H2 missed. Developers enable reuse locally cutting suite from 4min to 90s; CI fresh container each run for determinism.

#### Common mistakes
Shared mutable data across tests without cleanup — flaky CI. Reuse in CI without parallel job isolation — cross-job pollution if misconfigured. Hard-coded latest tag — pin image digest for reproducibility.

#### Interview follow-ups (with model answers)

**Q:** `@DynamicPropertySource` still needed?
**A:** For custom props not covered by ServiceConnection — yes. Kafka custom listeners may need both `@ServiceConnection` and additional properties. Legacy tests migrate by deleting manual JDBC URL boilerplate.

**Q:** Testcontainers vs embedded DB?
**A:** Embedded lacks Oracle/SQL Server semantics; Testcontainers heavier but faithful. Balance: module tests on Testcontainers; fast unit tests on mocks. Nightly full suite with all containers.

#### Scenario probe

Flaky CI: order test passes alone, fails in full suite — duplicate email constraint.

**Model answer:** Shared Postgres without `@Transactional` rollback or `@Sql` cleanup — reusable container retains data. Fix: `@Transactional` on test, unique data per test (`UUID` email), or `@BeforeEach` truncate. Disable reuse in CI; document local reuse trade-off.

---

### 60. Spring Boot layered JAR and Docker buildpacks.

**Short answer:** Layered JAR (`spring-boot-maven-plugin` `layers.enabled=true`) splits dependencies, snapshot dependencies, application code, and loader — Docker copies layers separately for cache-friendly rebuilds. Cloud Native Buildpacks (`pack build` or `bootBuildImage`) produce OCI images without handwritten Dockerfile, applying security patches via builder updates. Seniors choose layers + buildpacks for faster CI; pin builder image version.

#### What it is
Boot repackages fat JAR with layer index; buildpacks detect JVM app and assemble runnable image with reproducible layers.

#### How it works (internals)
`java -Djarmode=layertools -jar app.jar extract` shows layers. Dockerfile `COPY` each layer in order — deps change rarely, app layer rebuilds fast. `bootBuildImage` uses Paketo builder; sets memory, BP_JVM_VERSION, env vars. SBOM and CVE scanning integrated in modern builders.

#### When to use / when NOT to use
Frequent deploys of large deps (Spring) — layered cache win. Custom OS packages or non-JVM sidecar — Dockerfile still needed. Regulated images requiring full Dockerfile audit — document buildpack SBOM.

#### Production example
CI image rebuild drops from 6min to 90s when only app code changes — layered JAR in Kaniko. Production uses `bootBuildImage` with pinned `paketobuildpacks/builder-jammy-base:0.4.x`; weekly builder bump for CVE patches without app code change.

#### Common mistakes
Single COPY fat JAR — no cache benefit. Unpinned buildpack builder — non-reproducible builds. Forgetting to set container memory limits matching JVM ergonomics flags.

#### Interview follow-ups (with model answers)

**Q:** Layered JAR vs jlink custom runtime?
**A:** Layers optimize Docker cache; jlink shrinks JVM modules — orthogonal. Can combine trimmed JRE base image with layered app layers. jlink maintenance higher — use when image size SLO strict (edge devices).

**Q:** bootBuildImage vs Dockerfile multistage?
**A:** Buildpacks reduce Dockerfile drift and encode JVM best practices; less control over exact OS layout. Multistage Dockerfile when platform team mandates golden base image from internal registry with buildpack incompatible policies.

#### Scenario probe

Docker builds slow — every commit re-downloads 200MB deps layer because pom changed snapshot version daily.

**Model answer:** Separate snapshot deps layer still invalidates if snapshot timestamp always new — pin snapshot or use release deps in CI. Layered layout puts snapshots in own layer so release deps cache persists. Consider dependency cache in CI (Maven `.m2`) plus layered JAR. Measure layer diff with `layertools`.

---

### 61. Spring Security 6 lambda DSL and multiple filter chains.

**Short answer:** Spring Security 6 removes `and()` chaining for lambda DSL: `http.securityMatcher("/api/**").authorizeHttpRequests auth -> auth.requestMatchers(...).permitAll()...)`. Multiple `@Bean SecurityFilterChain` ordered with `@Order` — e.g., chain 1 for actuator on management port, chain 2 for OAuth2 API, chain 3 for session admin UI. Matcher specificity matters — first matching chain wins.

#### What it is
Security configuration as composable filter chains replacing WebSecurityConfigurerAdapter removed in Security 6.

#### How it works (internals)
Each `SecurityFilterChain` bean applies to requests matching `securityMatcher`. `@Order(1)` highest precedence. Resource server JWT chain separate from form login chain. CORS, CSRF disabled per chain as needed — API stateless vs browser session differ.

#### When to use / when NOT to use
Split actuator, API, and static content security policies — multiple chains. Simple single REST API with JWT — one chain suffices. Do not duplicate filters across chains unintentionally.

#### Production example
Management port 8081: `@Order(1)` chain permits health from internal CIDR only; main port 8080: OAuth2 resource server for `/api/**`; `/admin/**` form login chain `@Order(2)` with session. Misconfigured matcher once exposed actuator — fixed with port-specific chain.

#### Common mistakes
Missing `@Order` — unpredictable chain selection. Overly broad `securityMatcher("/**")` on first chain shadowing others. CSRF enabled on stateless API breaking POST clients.

#### Interview follow-ups (with model answers)

**Q:** Migrate from `WebSecurityConfigurerAdapter`?
**A:** Extract `@Bean SecurityFilterChain`; replace `authorizeRequests` with `authorizeHttpRequests`; use lambda for csrf, session, oauth2ResourceServer. Remove `@EnableGlobalMethodSecurity` for `@EnableMethodSecurity`. Integration tests with `@WithMockUser` still work.

**Q:** How to test multiple chains?
**A:** `@SpringBootTest(webEnvironment=RANDOM_PORT)` with separate `TestRestTemplate` calls to management vs main port; or `@AutoConfigureMockMvc` with header/host matching matcher. `@Import(SecurityConfig.class)` slice tests per chain.

#### Scenario probe

After Security 6 migration, Swagger and API public but admin routes return 401 for legitimate session users.

**Model answer:** New chain order swapped — API chain matches `/admin/**` with denyAll before form-login chain runs. Fix matchers: narrow API chain to `/api/**` only; admin chain `@Order(2)` with `requestMatchers("/admin/**").authenticated()`. Add MockMvc tests per path class.

---

### 62. Spring Boot configuration metadata and `spring-boot-configuration-processor`.

**Short answer:** `@ConfigurationProperties` classes annotated with `@ConfigurationPropertiesScan` generate JSON metadata via `spring-boot-configuration-processor` at compile time — IDE autocomplete for `application.yml` keys and deprecation warnings. Documents default values, types, and `additional-spring-configuration-metadata.json` for manual hints. Seniors enforce processor on all custom starter modules; missing processor causes silent typos in prod yaml.

#### What it is
Annotation processor emitting `META-INF/spring-configuration-metadata.json` consumed by IDE and Boot configuration report.

#### How it works (internals)
Add processor dependency optional scope; build generates metadata from `@ConfigurationProperties` fields and `@DefaultValue` on constructor params (records). Supplement with `additional-spring-configuration-metadata.json` for map keys or third-party prefixes. `spring-configuration-metadata.json` validated in CI with `spring-boot-configuration-processor` + config docs site generation optional.

#### When to use / when NOT to use
Every internal library exposing Boot properties — processor mandatory. One-off `@Value` — metadata optional. Public starter without metadata — poor developer experience and ops typos.

#### Production example
Typo `app.payment.timeout-ms=30000` vs correct `app.payments` caught in IDE before commit; prod incident avoided. Custom starter documents 40 properties with descriptions visible in VS Code Spring Boot extension.

#### Common mistakes
Processor not on annotation processor path — no JSON generated. Relaxed binding confusion (`myProp` vs `my-prop`) without IDE hints. Primitive boolean defaults hiding missing yaml — pair with `@Validated` `@NotNull` on wrappers.

#### Interview follow-ups (with model answers)

**Q:** `additional-spring-configuration-metadata.json` when?
**A:** Map structures, legacy property names deprecation mapping, or properties bound outside `@ConfigurationProperties`. Documents `deprecation` replacement keys for Boot 2→3 migrations. Keeps IDE and reference docs aligned.

**Q:** Relaxed binding rules?
**A:** `kebab-case`, `camelCase`, `environment_variable` equivalent for same property; `@ConfigurationProperties(prefix="app.db")` binds `app.db.jdbc-url`. Metadata shows canonical form; relaxed binding applies at runtime only — typos in prefix still fail silently without validation.

#### Scenario probe

Production uses default pool size 10 because yaml key `spring.datasource.hikari.maximum-pool-size` misspelled — no startup failure.

**Model answer:** Enable `spring-boot-configuration-processor` and fail unknown keys with `spring.configuration.validate=true` (Boot 3.4+) or custom `EnvironmentPostProcessor`. Bind Hikari via `@ConfigurationProperties` record with required fields. Add unit test loading yaml asserting pool size bean value.

#### Code / config (when useful)

```xml
<dependency>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-configuration-processor</artifactId>
  <optional>true</optional>
</dependency>
```

---

## Scenario-based interview drills

### S1. Orders PLACED while payment declined — transaction swallowed

**Situation:** Payment service: OrderService.placeOrder @Transactional catches PaymentDeclinedException, returns 400 JSON, DB shows PLACED. Customer charged nothing but warehouse picks order.

**What they're testing:** @Transactional rollback rules, exception handling boundaries.

**How to structure your answer:**
- Why TX committed
- Where to catch exceptions
- Integration test asserting DB state
- rollbackFor configuration

**Model answer:** Spring rolls back on unchecked exceptions by default — caught PaymentDeclinedException never propagates, so TX commits. Fix: don't catch inside transactional method; use @ControllerAdvice for HTTP mapping; or rethrow; or rollbackFor. Integration test: decline payment mock → assert order status not PLACED. Add metric for 'declined but persisted' — should be zero. Code review rule: no catch of payment exceptions inside @Transactional without setRollbackOnly.

**Common weak answers:** Adding rollbackFor without fixing catch boundary.

**Follow-up probes (with answers):**

**Q:** setRollbackOnly() when?
**A:** When you must catch for logging but still abort TX — mark rollbackOnly then throw or exit without commit.

---

### S2. Hikari pool exhausted under Black Friday load

**Situation:** Spring Boot monolith: 20 pods, maxPoolSize 10 each, Postgres max_connections 200. OSIV on, slow mobile clients. Pool timeout errors spike; readiness fails.

**What they're testing:** Connection hold time, OSIV, pool sizing, Tomcat threads.

**How to structure your answer:**
- Math: pods × pool vs DB limit
- OSIV and long requests
- Transaction boundary shortening
- Read replica routing

**Model answer:** 200 connections / 20 pods = 10 max only if no admin or migration connections — already at edge. OSIV holds connection from service return through JSON serialization — disable spring.jpa.open-in-view=false. Use DTO projections and @EntityGraph; never lazy load in controller. Shorten @Transactional scope; don't call HTTP inside TX. Consider pgbouncer, read replicas for reports, scale connection limit with infra review.

**Common weak answers:** Only increasing pool size per pod.

**Follow-up probes (with answers):**

**Q:** OSIV and read-only TX?
**A:** Read-only still holds connection until response complete with OSIV — disable for APIs.

---

### S3. @Async fire-and-forget loses payment failures

**Situation:** Email receipt sent @Async void after order; async thread throws SMTP error — no log alert, customer thinks order failed and reorders.

**What they're testing:** @Async exception handling, MDC propagation, reliable delivery.

**How to structure your answer:**
- AsyncUncaughtExceptionHandler
- TaskExecutor configuration
- Queue vs async for receipts
- Observability on async path

**Model answer:** void @Async swallows exceptions to caller — configure AsyncUncaughtExceptionHandler with alert. Use bounded ThreadPoolTaskExecutor not SimpleAsyncTaskExecutor. TaskDecorator copies MDC/traceId. For money-adjacent side effects prefer outbox + worker with retry/DLT not bare @Async. Metrics on async failure rate; integration test that forces SMTP failure and asserts alert.

**Common weak answers:** Assuming @Async exceptions bubble to controller.

**Follow-up probes (with answers):**

**Q:** Virtual threads @Async Boot 3.2+?
**A:** Can simplify blocking I/O async but still need executor config and exception handler — not magic reliability.

---

### S4. Actuator /env exposed — credential leak

**Situation:** Security scan finds public /actuator/env with SPRING_DATASOURCE_PASSWORD visible. Heapdump endpoint enabled on same port as API.

**What they're testing:** Actuator exposure, management port, security.

**How to structure your answer:**
- Immediate containment
- management.endpoints.web.exposure
- Separate management port and network policy
- Secret rotation

**Model answer:** Immediate: block public access via WAF, rotate credentials, disable heapdump/env exposure. management.server.port separate; bind internal only; exposure.include=health,prometheus only. Spring Security 6 restricts actuator with role ACTUATOR. Never log env at DEBUG in prod. CI policy fails build if management.endpoints.web.exposure.include contains '*'.

**Common weak answers:** Auth on actuator but same port as app without network segmentation.

**Follow-up probes (with answers):**

**Q:** Liveness vs readiness?
**A:** Liveness: JVM up; readiness: can serve traffic — DB/Kafka checks belong readiness with timeout.

---

### S5. Self-invocation bypasses @Transactional

**Situation:** OrderService.placeOrder calls this.saveAudit() @Transactional REQUIRES_NEW — audit never persists separately; outer rollback rolls back audit too.

**What they're testing:** Proxy mechanics, self-invocation, bean splitting.

**How to structure your answer:**
- Why proxy skipped
- Fix patterns: inject self, separate bean
- exposeProxy=true
- Test proving separate TX

**Model answer:** this.saveAudit() is direct call on target object, not proxy — REQUIRES_NEW ignored. Inject AuditService separate bean or self via interface. exposeProxy=true + AopContext.currentProxy() works but is smell. Integration test: force outer rollback, assert audit row exists when REQUIRES_NEW correct. Code review: grep for 'this.' inside @Transactional services.

**Common weak answers:** Making methods public without proxy call path fix.

**Follow-up probes (with answers):**

**Q:** JDK vs CGLIB proxy?
**A:** JDK needs interface; CGLIB subclasses concrete — final methods cannot be proxied.

---

### S6. Kafka listener ack before DB commit

**Situation:** Consumer @Transactional processes order, manual ack after method start but before commit due to wrong AckMode — crash loses message, order never created.

**What they're testing:** Kafka TX alignment, ack mode, idempotency.

**How to structure your answer:**
- Ack timing vs commit
- Idempotent consumer design
- Outbox alternative
- DLT for poison messages

**Model answer:** Ack must follow successful DB commit — use MANUAL_IMMEDIATE after TX or transactional Kafka with eyes open. On redelivery, idempotent upsert on orderId. Outbox in same TX as business write; poller publishes — crash-safe. DefaultErrorHandler with DLT for poison messages; alert on DLT growth. Chaos test: kill pod mid-processing, assert no lost orders.

**Common weak answers:** Auto ack with rollback-on-failure expectation.

**Follow-up probes (with answers):**

**Q:** Outbox vs Kafka TX?
**A:** Kafka EOS within broker; cross-service exactly-once needs outbox + idempotent consumers.

---

### S7. Circular dependency allowed in dev, fails in Boot 2.6+ prod

**Situation:** A→B→C→A cycle; spring.main.allow-circular-references=true in dev profile only. Prod strict mode fails context refresh on deploy Friday.

**What they're testing:** Circular dependencies, @Lazy, design fix.

**How to structure your answer:**
- Why cycle exists
- Break with constructor refactor or event
- Lazy as temporary band-aid
- Fail-fast in CI matching prod

**Model answer:** Cycles hide design smell — extract shared collaborator D or use event decoupling. @Lazy breaks cycle at startup but delays failure to first call. CI must use same allow-circular-references=false as prod. Refactor: PaymentService and NotificationService both need OrderReader port implemented by OrderQueryService. Document in ADR why cycle removed.

**Common weak answers:** Permanent allow-circular-references in prod.

**Follow-up probes (with answers):**

**Q:** ObjectProvider vs @Lazy?
**A:** ObjectProvider defers lookup explicitly; clearer than field @Lazy on half the graph.

---

### S8. @Cacheable + @Transactional ordering surprise

**Situation:** Product price updated in DB but API returns stale cache; @Cacheable on @Transactional service method, self-invocation from update method bypasses cache evict.

**What they're testing:** AOP order, cache eviction, proxy boundaries.

**How to structure your answer:**
- Proxy order @Order on aspects
- @CacheEvict on update path
- Self-invocation and cache
- TTL vs explicit eviction for money

**Model answer:** Caching aspect may run outside TX depending on order — understand @Order on custom aspects. Put @CacheEvict on update method called through proxy from controller. For prices use short TTL + evict on write; never infinite cache on financial data. Integration test: update price → read API returns new value. Micrometer cache hit/miss metrics.

**Common weak answers:** Clear all cache manually in prod without root cause.

**Follow-up probes (with answers):**

**Q:** @Cacheable on repository?
**A:** Possible but evict boundaries blur — prefer service layer cache for business keys.

---

### S9. Graceful shutdown kills in-flight Kafka consumers

**Situation:** K8s rollout sets terminationGracePeriodSeconds 30 but consumer processing takes 2 min; SIGTERM stops container, rebalance storm, duplicate processing.

**What they're testing:** Graceful shutdown, server.shutdown, listener container stop timeout.

**How to structure your answer:**
- Spring Boot graceful shutdown config
- K8s preStop hook
- Consumer cooperative rebalance
- Processing timeout vs grace period

**Model answer:** server.shutdown=graceful; spring.lifecycle.timeout-per-shutdown-phase=60s; align with K8s grace. KafkaListenerContainer stops polling, waits in-flight records, then closes. preStop sleep briefly before SIGTERM to remove from load balancer first. Idempotent consumer handles duplicates from rebalance. If processing > grace, reduce batch size or increase grace — don't pretend 30s is enough.

**Common weak answers:** Immediate SIGKILL with no shutdown hook.

**Follow-up probes (with answers):**

**Q:** Tomcat graceful vs immediate?
**A:** Graceful stops accepting new HTTP, completes in-flight — pair with K8s readiness removal.

---

### S10. Multi-datasource @Transactional wrong manager

**Situation:** Reporting @Transactional on secondary DataSource still joins primary TX — writes go to wrong DB silently in tests with single DB.

**What they're testing:** Multi-tx manager, @Transactional qualifier, ChainedTransactionManager pitfalls.

**How to structure your answer:**
- transactionManager attribute
- Test with two Testcontainers
- Read-only routing pattern
- Avoid chained TX unless necessary

**Model answer:** Each DataSource needs PlatformTransactionManager bean; @Transactional(transactionManager='reportingTx') explicit. Integration test with two databases proves isolation. Read-only replica routing via AbstractRoutingDataSource — TX still one manager. ChainedTransactionManager is last resort — partial commit failure is nightmare. Document which beans use which manager in module README.

**Common weak answers:** Assuming @Primary transaction manager applies everywhere.

**Follow-up probes (with answers):**

**Q:** ChainedTransactionManager pitfalls?
**A:** Partial commit — first commits second fails; prefer saga/outbox across DBs.

---

