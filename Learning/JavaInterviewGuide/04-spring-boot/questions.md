# Spring Boot — 92 Senior Interview Questions (78 core + 14 Spring Security deep-dive)

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
**A:** A `BeanPostProcessor` is a container-wide hook that can wrap or modify any bean before and after initialization—AOP proxies, `@Autowired` processing, and `@Transactional` all use BPPs. `InitializingBean.afterPropertiesSet()` is a single-bean callback after injection on that bean only. In production I use `@PostConstruct` on services for idempotent startup (cache warmers) and reserve BPPs for framework-style cross-cutting. Misunderstanding the order causes bugs like calling a transactional method from `@PostConstruct` before the TX proxy exists. I verify lifecycle with an integration test and `ConditionEvaluationReport` when beans look uninitialized at first request.

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
**A:** No—since Spring 4.3, a single constructor on a class managed by the container is autowired implicitly. I still add `@Autowired` on multi-constructor classes to mark which one to use, or when the class might be instantiated outside Spring in tests. In Kotlin, the primary constructor is injected without the annotation. Production pitfall: package-private constructors or classes outside the scan root fail at startup with `NoSuchBeanDefinitionException`, not a missing `@Autowired`. I enforce constructor injection via ArchUnit and code review—field injection hides dependencies and breaks immutability under concurrent load.

**Q:** Kotlin and injection patterns?
**A:** Kotlin data classes and `@Service` work well with constructor injection—the primary constructor parameters become dependencies. Use `@ConfigurationProperties` records with constructor binding for immutable config. Avoid `@Autowired lateinit var` except in `@Configuration` edge cases; it hides missing beans until runtime. For optional deps, `ObjectProvider<T>` or nullable constructor params with `@Autowired(required=false)` are clearer. In a mixed Java/Kotlin monolith I keep Spring stereotypes on Kotlin classes and use `@JvmOverloads` when Java callers need multiple constructors. Circular deps still fail on Boot 2.6+—fix with extracted interfaces, not `lateinit` workarounds.

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
**A:** The inner `REQUIRES_NEW` transaction commits independently when its method returns successfully—even if the outer transaction rolls back afterward. That is why we use it for audit logs that must survive business failure. The trade-off is two Hikari connections briefly held per call and no atomicity across boundaries. In a payment service, an audit row committed via `REQUIRES_NEW` remains while the order TX rolls back on fraud decline—exactly what we want. I never nest `REQUIRES_NEW` chains deeply; pool exhaustion showed up in metrics as `hikaricp.connections.pending` spiking during checkout peaks.

**Q:** Does `NOT_SUPPORTED` clear the persistence context?
**A:** Yes—`NOT_SUPPORTED` suspends any existing transaction and runs the method non-transactionally. The `EntityManager` persistence context from the suspended TX is not active; lazy loads and dirty entities from the outer scope are invisible inside the method. I use it sparingly for reporting calls that must not join a long-running TX, or external HTTP that should not hold a DB connection. Returning to the outer TX resumes the original context. Production bug: calling a `NOT_SUPPORTED` helper mid-service and expecting unflushed entity changes to propagate—they won't. Test with `@DataJpaTest` and explicit flush boundaries.

**Q:** ChainedTransactionManager pitfalls?
**A:** ChainedTransactionManager commits managers sequentially—if the second commit fails, the first is already committed with no rollback. That is not two-phase commit. I avoid it for cross-database writes; use saga/outbox instead. Where I have seen it: legacy reporting DB plus orders DB in one modular monolith—partial commits caused reconciliation nightmares. Read-replica routing with a single manager is safer than chaining. If you must chain, keep operations idempotent, alert on partial failure, and never use it for money movement. Boot docs deprecate it for good reason—treat as code smell in design review.

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
**A:** Isolation level (`@Transactional(isolation=...)`) applies to the whole transaction via JDBC `setTransactionIsolation`—it governs what concurrent TXs can read (dirty reads, phantoms) using MVCC or locking depending on Postgres settings. `@Lock(PESSIMISTIC_WRITE)` is a JPA row-level `SELECT FOR UPDATE` on a specific query or entity load within the TX. I raise isolation only for batch snapshots; for hot inventory rows I use optimistic `@Version` first, then pessimistic lock on the final decrement query. SERIALIZABLE globally killed throughput on our checkout service—measured 40% contention before reverting to READ COMMITTED plus row locks.

**Q:** How does Postgres handle phantom reads?
**A:** Postgres default READ COMMITTED prevents dirty reads via MVCC snapshots but allows non-repeatable reads and phantoms within a statement's visibility rules. REPEATABLE READ and SERIALIZABLE use stronger snapshot isolation; SERIALIZABLE detects serialization anomalies and may throw `40001` requiring retry. Spring's `@Transactional(isolation=SERIALIZABLE)` maps to JDBC but you must handle `SerializationFailureException` with retry in the service layer. I do not set SERIALIZABLE app-wide—only on reconciliation jobs. For user-facing APIs, `@Version` on `Inventory` plus idempotent reserve operations gave us correctness without global serialization retries choking Hikari under flash sales.

**Q:** Read-only transaction routing to replicas?
**A:** Spring's `AbstractRoutingDataSource` switches JDBC targets based on a thread-local key—typically set by an AOP aspect when `@Transactional(readOnly=true)` is active. Replica lag means a read after write may return stale data; I never route post-mutation reads to replicas in the same user flow. Connection pools are per datasource—size replica pools for read traffic separately from primary. In K8s, replica endpoints come from ConfigMap; health checks must verify replica connectivity without marking the pod ready if routing is broken. Integration tests with Testcontainers primary only miss routing bugs—add a test profile with two URLs or mock the router.

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
**A:** Default `@Transactional` on `@SpringBootTest` rolls back after each test method—the database changes never commit, so `AFTER_COMMIT` listeners never fire. That hides production bugs where listeners assume committed state. I use `@Commit` on specific tests that verify after-commit behavior, or `@TransactionalEventListener` integration tests without class-level rollback. `BEFORE_COMMIT` listeners still run inside the test TX boundary. For Kafka outbox tests, I assert outbox rows exist before rollback or use Testcontainers without test TX rollback. Document in the test README which tests require commit semantics so juniors do not wonder why emails are never 'sent' in tests.

**Q:** Spring vs JTA rollback rules?
**A:** Spring's `TransactionInterceptor` rolls back on unchecked exceptions by default; checked exceptions commit unless `rollbackFor` is set. JTA (Java EE) historically rolled back on any `RuntimeException` and often on checked `Exception` depending on container—behavior differs. Mixing `JtaTransactionManager` with Spring declarative TX requires knowing your app server rules. In Boot microservices we use `JpaTransactionManager` + Hikari, not full JTA, unless XA is explicitly required—and I avoid XA. `rollbackFor = Exception.class` on payment services is common when business exceptions are checked. Always integration-test: force failure, assert DB unchanged, assert outbox not published on rollback.

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
**A:** Rare but real: last-moment validation that must see uncommitted work in the same TX—aggregating line totals before commit, or flushing audit fields onto the entity graph. I used it once to compute a checksum over order lines already persisted in the current TX. Do not publish to Kafka or send email on `BEFORE_COMMIT`—rollback still possible after the listener runs. Heavy work here extends connection hold time and risks Hikari starvation. Prefer `BEFORE_COMMIT` only for in-TX consistency checks; side effects belong in `AFTER_COMMIT` with outbox for durability. If the listener throws, the whole TX rolls back—treat it like business logic.

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
**A:** Enable Hikari metrics: `hikaricp.connections.usage` timer and `hikaricp.connections.active` gauge in Micrometer/Prometheus. Correlate with HTTP server request timers—if connection usage p99 exceeds service method p99, OSIV or controller-level TX is holding connections through serialization. JDBC proxy logging (`log4jdbc`, datasource-proxy) shows acquire-to-release per request in staging. I add a custom Micrometer timer around `@Transactional` service methods in hot paths during incidents. K8s symptom: pool exhausted while CPU is low—thread dump shows threads in Jackson serialization or Feign calls inside TX. Fix boundary, not pool size alone.

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
**A:** On the service/use-case layer methods that execute queries—never on REST controllers. `@Transactional(readOnly=true)` hints Hibernate to skip flush and can route to replicas via a routing datasource. Controllers should delegate in one line; putting readOnly on the controller still opens the TX before response writing if OSIV is on, holding connections. In hexagonal terms, the application service owns the unit of work; adapters (web, messaging) stay thin. I annotate `OrderQueryService.getSummary()` readOnly, with `@EntityGraph` fetch plans inside that boundary. ArchUnit rule: no `@Transactional` on classes in `..api..` or `..controller..` packages.

**Q:** Layered architecture vs hexagonal — where is the boundary?
**A:** The transaction boundary sits on application services (use cases), not on web adapters or infrastructure. Hexagonal: inbound HTTP adapter calls `PlaceOrderUseCase`; the use case is `@Transactional` and orchestrates domain plus outbound ports. Layered: controller → service → repository follows the same rule—the service layer owns TX. Repositories participate in the caller's TX; they do not define business boundaries. Anti-pattern: `@Transactional` on controller because 'it is the entry point.' In production, stretching TX to the HTTP layer tied Hikari connections to payment gateway latency—moving TX to `OrderService` cut pool wait 60%. Ports stay interface-only; TX stays where business atomicity is defined.

**Q:** `@Transactional` on repository custom impl?
**A:** Spring Data custom fragments (`OrderRepositoryCustomImpl`) can be `@Transactional` when the fragment defines its own atomic unit—bulk `@Modifying` updates are the common case. Default simple repository methods join the calling service TX. I put `@Transactional` on the custom impl class or method when it runs multiple modifying queries that must be atomic together. Do not duplicate TX on both service and repository unless propagation is intentional. Pitfall: `@Modifying` without TX throws at runtime; `@Transactional` on a private method in the impl is ignored—must be public on the Spring proxy. Test with `@DataJpaTest` importing the custom fragment.

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
**A:** After a bulk JPQL/SQL update, Hibernate's persistence context may contain stale entity snapshots. `clearAutomatically=true` clears the `EntityManager` after the modifying query so subsequent loads fetch fresh rows. Without it, a `findById` in the same TX returns the old in-memory state—caused a production bug where status stayed OPEN after a bulk cancel query. `flushAutomatically=true` flushes pending changes before the update so the SQL sees current dirty entities. Both require an active transaction—annotate the service or custom repository impl. I always pair modifying queries with integration tests asserting entity state after the update in the same TX.

**Q:** Difference between `Slice` and `Page`?
**A:** `Page<T>` runs a COUNT query for total elements—expensive on large tables with complex joins. `Slice<T>` fetches `pageSize+1` rows to detect `hasNext` without counting—ideal for infinite scroll APIs. I return `Slice<OrderSummary>` from customer order history; admin dashboards needing 'page 47 of 200' use `Page` with indexed predicates only. Never `Page` on a 50M-row table without covering indexes—the COUNT scan killed our reporting API. Spring Data passes `Pageable` through; document in OpenAPI whether clients get total count. For Kafka replay pagination, Slice-style cursoring with `(createdAt, id)` keyset beats OFFSET Page.

**Q:** Custom repository fragment wiring?
**A:** Define `OrderRepository extends JpaRepository<Order, Long>, OrderRepositoryCustom`. Implement `OrderRepositoryCustomImpl` (suffix `Impl` required) in the same package, annotated `@PersistenceContext EntityManager`. Spring Data's `RepositoryFactory` composes the proxy delegating custom methods to the impl. Fragment name must match: `FooCustom` + `FooCustomImpl`. I use fragments for complex native SQL or Criteria API too heavy for `@Query`. Pitfall: impl not in scanned package—methods throw at runtime. Multiple datasources need `@Qualifier` on the `EntityManager`. Test the fragment with `@DataJpaTest` and Testcontainers Postgres, not mocked EM.

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
**A:** `SecurityContextHolder` is thread-local—`@Async` workers start with empty context. Register a `TaskDecorator` on `ThreadPoolTaskExecutor` that copies `SecurityContextHolder.getContext()` before `run()` and clears in `finally`. For `DelegatingSecurityContextAsyncTaskExecutor`, Spring provides this wrapper. JWT claims needed downstream should be explicit method args, not relied upon from context in async code. In K8s, scheduled jobs have no user—use service accounts or system principals. I audit async entry points in security review: `@Async` email after order must not execute with elevated privileges from a leaked admin context. Pair with MDC decorator for trace IDs.

**Q:** Virtual threads with `@Async` in Boot 3.2+?
**A:** Boot 3.2+ enables `spring.threads.virtual.enabled=true` for Tomcat; `@Async` still needs its own executor—virtual threads are not automatic on `@Async` unless you configure `SimpleAsyncTaskExecutor` with `setVirtualThreads(true)` or a custom executor using `Executors.newVirtualThreadPerTaskExecutor()`. Virtual threads help blocking I/O on async workers without platform thread explosion. Caveat: pinning on synchronized blocks or native JDBC drivers can negate benefits—test with JFR. I do not replace Kafka consumers with virtual-thread `@Async` without measuring; carrier thread pinning showed up under load. Pin thread pool metrics either way.

**Q:** Difference from `@Scheduled`?
**A:** `@Async` is event-driven—invoked when another bean calls the async method, returns immediately to caller. `@Scheduled` is time-driven—cron/fixedRate on every pod unless distributed lock added. Async handles 'send email after this request'; scheduled handles 'reconcile at 2am UTC.' Both need explicit executors in production; both lose security/MDC context without decorators. `@Scheduled` on three K8s replicas fires three times—use ShedLock or CronJob. `@Async` void methods swallow exceptions to `AsyncUncaughtExceptionHandler`—easy to miss failures. I choose messaging (Kafka) over `@Async` when durability matters; `@Async` for best-effort side effects only.

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
**A:** All three solve 'give me a new or scoped instance' from a singleton. `ObjectFactory<T>` and `Provider<T>` (JSR-330) lazily resolve from the container—useful for prototype or request-scoped beans injected into singletons. `@Lookup` on an abstract `@Component` method creates a subclass at runtime that delegates `getBean` per call—clean for prototype-per-operation. I prefer `ObjectProvider<OrderBuilder>` constructor injection in services over `@Lookup` magic. Production pitfall: calling `getObject()` in a loop without understanding scope—prototype spam or request-scope leak outside HTTP. Request-scoped beans still need `proxyMode=TARGET_CLASS` when injected into singletons.

**Q:** WebFlux request scope differences?
**A:** Servlet request scope uses `RequestContextHolder` thread-local; WebFlux is reactive—no thread-per-request guarantee. Request-scoped beans need `RequestScope` with Reactor context propagation, or pass values explicitly through `Mono` chains. `@RequestScope` `@Component` injected into a WebFlux controller singleton fails or behaves incorrectly without scoped proxy—and even then thread hopping breaks naive holders. I store correlation ID in Reactor `Context` via `Hooks.enableAutomaticContextPropagation()` in Boot 3.2+. Do not port MVC `@RequestScope UserContext` to WebFlux by annotation alone. Security context uses `ReactiveSecurityContextHolder`, not `SecurityContextHolder`.

**Q:** Custom scope implementation?
**A:** Implement `Scope` interface (`get`, `remove`, `registerDestructionCallback`) and register via `ConfigurableBeanFactory.registerScope("tenant", new TenantScope())`. Use `@Scope("tenant")` with `ScopedProxyMode.TARGET_CLASS` when injecting into singletons. Real example: multi-tenant SaaS holding tenant config per request—better solved with explicit `TenantContext` record passed as method arg in modern code. Custom scopes complicate testing and AOT/native hints. I have only implemented custom scope once; default request/session plus explicit context objects cover 99% of cases. Document destruction callbacks or leak memory on redeploy in long-lived pools.

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
**A:** `@ConfigurationPropertiesScan` on `@SpringBootApplication` discovers all `@ConfigurationProperties` types in scanned packages—zero boilerplate for many property classes. `@EnableConfigurationProperties(FooProperties.class)` explicitly registers specific types—preferred in libraries and tests importing one config slice. Starters use `@EnableConfigurationProperties` in auto-config to avoid scanning consumer packages. I use scan in monolith apps with dozens of property records; explicit enable in integration tests loading one module. Both require `spring-boot-configuration-processor` for IDE metadata. Missing registration means empty defaults silently—validate with `@Validated` and required fields.

**Q:** How does relaxed binding handle lists?
**A:** Lists bind from indexed yaml (`app.hosts[0]=a`, `app.hosts[1]=b`), comma-separated env vars (`APP_HOSTS=a,b`), or yaml array syntax. Maps use bracket notation (`app.map.key=value`). Relaxed binding accepts `jdbc-url`, `jdbcUrl`, `JDBC_URL` for the same field. Pitfall: empty string env var may bind as `[""]` not empty list—test in staging. Complex nested lists in records need constructor binding for immutability. I document canonical keys in `additional-spring-configuration-metadata.json` so K8s ConfigMap keys match. Wrong list binding caused Kafka bootstrap servers to be a single string with commas—not split—until we fixed the property type to `List<String>`.

**Q:** Immutable `@ConstructorBinding`?
**A:** Boot 3 binds `@ConfigurationProperties` records and immutable classes via constructor parameters—`@ConstructorBinding` on the type or implicit for records. Fields are final; no setter mutation at runtime. Constructor param names must match properties (or `@Name` on parameters with `-parameters` compiler flag). I use `record KafkaProps(String bootstrapServers, int retries) {}` with `@Validated` for fail-fast startup. Immutable config prevents on-call 'hot fix' mutating properties beans in debugger. Pair with `@ConfigurationPropertiesScan` and processor for IDE support. Migration from Lombok `@Data` properties: convert to record, fix tests expecting setters.

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
**A:** Boot 2.4+ changed config tree: `application.properties`, profile-specific files, then `spring.config.import` of optional/required locations. Imports process in declaration order; later overrides earlier for same key. `spring.config.import=optional:configtree:/etc/config/` for K8s mounted volumes. `spring.config.activate.on-profile=prod` in imported files. Precedence: command-line args > env vars > imported files > jar defaults. Pitfall: importing before profile activates—wrong file loaded. I use `optional:` prefix so missing local vault does not crash dev. Document order in README; debug with `GET /actuator/env` or `--debug` logging of `ConfigDataEnvironment`.

**Q:** Spring Cloud Config vs K8s native?
**A:** Spring Cloud Config Server centralizes git-backed config with refresh bus—great for VM estates and many non-K8s services. K8s native: ConfigMaps and Secrets mounted as env or files, External Secrets Operator for vault sync, no extra config server to operate. I choose K8s-native for workloads already on EKS/GKE—fewer moving parts, GitOps via Argo CD applies manifests. Spring Cloud Config still wins when polyglot apps share one config repo or you need encryption `@cipher` workflows without vault. Hybrid happens during migration—Boot apps read mounted yaml, legacy uses config server. Either way: secrets never in git, reload without rebuild via mounted volume + `spring.cloud.kubernetes.reload`.

**Q:** Testing with `@ActiveProfiles`?
**A:** `@ActiveProfiles("test")` activates `application-test.yml`—in-memory H2, WireMock stubs, disabled security. Use `@DynamicPropertySource` for Testcontainers JDBC URLs that are not known at compile time. `@TestPropertySource` for one-off overrides. Pitfall: `@ActiveProfiles` on a base class affects all subclasses—flaky when one test needs prod-like settings. I prefer `@Import(TestContainersConfig.class)` over profile explosion. CI must set the same profiles as local defaults documented in CONTRIBUTING. `@ActiveProfiles` does not replace `@Transactional` rollback—combine thoughtfully. For `@ConfigurationProperties` validation tests, activate profile that mirrors prod constraints.

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
**A:** Custom `HealthIndicator` beans contribute to `/actuator/health` with UP/DOWN and details—use for Kafka lag, downstream dependency checks, migration status. `ReadinessState` (ApplicationAvailability) is a coarse ACCEPTING_TRAFFIC vs REFUSING_TRAFFIC signal K8s probes use—Boot sets REFUSING during startup then ACCEPTING when ready. I implement `HealthIndicator` for 'can we process payments' (DB + PSP reachable); use `AvailabilityChangeEvent` to refuse traffic during graceful drain. Do not put slow checks on liveness—pod restart loops. Readiness failure removes pod from Service endpoints; liveness failure kills the container. Separate management port keeps probe traffic off main threads.

**Q:** Micrometer registry customization?
**A:** Register custom `MeterRegistryCustomizer<MeterRegistry>` beans to add common tags (`application`, `environment`, `pod`). Bind additional registries for dual export (Prometheus + Datadog). `management.metrics.export.prometheus.enabled=true` exposes scrape endpoint. High-cardinality tags belong nowhere—use `MeterFilter.denyNameStartsWith` or max tag limits. I customize histogram buckets for SLA-aligned SLO dashboards. Custom `Clock` for testing timers. Pitfall: creating a second `MeterRegistry` bean breaks auto-config—customize the primary. In K8s, Prometheus Operator scrapes pod annotations; verify labels match alert rules after registry customization.

**Q:** Actuator security with Spring Security 6?
**A:** Expose actuator on separate management port (`management.server.port=8081`) with network policy restricting ingress. Main `SecurityFilterChain` should not `permitAll` `/actuator/**` on the public port. Second chain `@Order(1)` on management port: `requestMatchers(EndpointRequest.toAnyEndpoint()).hasRole("ACTUATOR")` with HTTP basic or mTLS. Spring Boot 3 integrates `EndpointRequest` helpers. Disable env, heapdump, shutdown in prod via `management.endpoint.*.enabled=false`. Health and prometheus often stay open to internal CIDR only. I have seen scanners exploit public `/actuator/env`—immediate incident. Pair with OAuth2 client credentials for ops tools scraping metrics.

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
**A:** Histograms bucket observations client-side (`le` tags) and allow `_bucket`, `_sum`, `_count` series—Prometheus computes quantiles with `histogram_quantile`. Summaries pre-compute quantiles client-side (`quantile` tag)—not aggregatable across pods in older patterns. Micrometer timers export as histograms by default for Prometheus registry with configurable SLA buckets. I use histograms for HTTP latency across replicas; avoid Summary for cluster-wide p99. High bucket count increases cardinality—choose sensible `minimumExpectedValue`/`maximumExpectedValue`. Grafana dashboards use recording rules on histograms for consistent SLO burn rates.

**Q:** OpenTelemetry vs Brave?
**A:** Brave is Zipkin's tracing library—mature, focused on tracing. OpenTelemetry (OTel) is vendor-neutral standard for traces, metrics, logs with unified SDK. Spring Boot 3.2+ Micrometer Tracing supports OTel exporter and Brave bridge. I default OTel for new services—collector fans out to Jaeger/Datadog without code changes. Brave still appears in legacy Spring Cloud Sleuth migrations. Auto-configuration propagates W3C `traceparent` on RestClient/WebClient when on classpath. Pitfall: mixing propagators across services breaks trace linking. Sample at 5-10% in prod; 100% in staging. Verify with exemplars linking metrics to traces in Prometheus 2.40+.

**Q:** `@Observed` annotation?
**A:** Micrometer Observation API annotation—`@Observed(name="orders.place")` on service methods creates a span (if tracing enabled) and timer with consistent naming. Replaces ad-hoc `@Timed` plus manual span creation. Contextual name appears in logs/traces. Parameters annotated `@SpanTag` become low-cardinality tags—never tag userId on high-QPS paths. Requires `ObservedAspect` bean—Boot auto-configures when aspect on classpath. I use on checkout and payment client boundaries for SLO dashboards. Test by asserting `ObservationRegistry` receives observations in slice tests. Prefer `@Observed` over custom AOP for standard observability—less boilerplate, integrates with OpenTelemetry export.

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
**A:** Servlet filters run in registration order before `DispatcherServlet`. Spring Security filter chain is itself a `Filter`—custom `OncePerRequestFilter` should sit relative to security depending on need: correlation ID before security (log all requests), tenant resolution after authentication (need principal). Use `FilterRegistrationBean` with `setOrder(Ordered.HIGHEST_PRECEDENCE + 10)` or `SecurityFilterChain` DSL `addFilterBefore/After`. `@Order` on `@Component` filter works but explicit registration is clearer. I place MDC correlation filter at highest precedence; body caching filter after security for authenticated audit. Wrong order: security rejects before correlation ID set—on-call cannot trace 401 storms.

**Q:** OAuth2 login vs resource server?
**A:** OAuth2 login (client) redirects browser users through authorization code flow, establishes session or issues tokens at BFF—human authentication. Resource server validates Bearer JWT on APIs—machine-to-machine and SPA API calls. Same app can host both with separate `SecurityFilterChain` beans: `@Order(1)` API JWT chain on `/api/**`, `@Order(2)` login chain on `/login/**`. Confusing them: putting `oauth2Login()` on stateless API enables session cookies clients do not expect. Production: SPA uses PKCE against BFF; microservices are resource servers only with `issuer-uri` and audience validation. Actuator on separate port with different chain.

**Q:** Method security filter interaction?
**A:** HTTP security filters authenticate and populate `SecurityContext` before `DispatcherServlet` invokes the controller. Method security (`@PreAuthorize`) runs via AOP proxy on the service bean—after the controller delegated. Order: Filter chain → Controller → Secured service proxy. `@PreAuthorize` never runs if controller calls repository directly bypassing secured service. `@EnableMethodSecurity` required in Boot 3. Scheduler/Kafka listeners need `@PreAuthorize` on service methods too—HTTP security does not apply. `SecurityContext` must be propagated to async/Kafka threads via delegating wrappers. Test method security with `@WithMockUser` on service tests, not only MockMvc.

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
**A:** Implement `PermissionEvaluator` with `hasPermission(Authentication, Object target, Object permission)` for domain ACLs—`@PreAuthorize("hasPermission(#orderId, 'Order', 'cancel')")`. Register via `@EnableMethodSecurity` and expose as bean named `permissionEvaluator`. Load target entity inside evaluator—keep DB lookup fast or cache; slow SpEL kills latency. I use for multi-tenant row ownership checks beyond coarse roles. Pitfall: N+1 permission checks in list endpoints—batch evaluate or push filter to query. Integration test with `@WithMockUser` and seeded ACL rows. Do not call external auth service synchronously per request without circuit breaker.

**Q:** `@WithMockUser` testing limits?
**A:** `@WithMockUser` sets `SecurityContext` with synthetic principal—it does not test JWT parsing, issuer validation, or custom `Converter` logic. Use for service-layer `@PreAuthorize` unit tests. For HTTP contract, use `@AutoConfigureMockMvc` + `SecurityMockMvcRequestPostProcessors.jwt()` (Spring Security 5.3+) to build realistic JWT authorities. `@WithMockUser(roles="ADMIN")` maps to `ROLE_ADMIN`—know the `ROLE_` prefix default. Does not populate method-security custom beans unless `@Import` security config. I layer tests: MockMvc with JWT for controllers, `@WithMockUser` for service, Testcontainers-keycloak smoke for end-to-end quarterly.

**Q:** Securing `@Async` methods?
**A:** `@PreAuthorize` on `@Async` methods does not run when you call `asyncService.send()` from within the same class—self-invocation bypasses proxy. Caller must invoke through injected proxy. Security context is not on async thread unless `DelegatingSecurityContextAsyncTaskExecutor` or `TaskDecorator` copies context—and copying user context to async may be wrong for elevated jobs. I prefer passing explicit `Principal` or `tenantId` as method args to async methods rather than relying on `SecurityContextHolder`. Audit async operations with service account identity for system tasks. Never `@Async` + `@PreAuthorize` as sole gate for destructive operations without idempotency keys.

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
**A:** Salt is per-password random value stored alongside hash—prevents rainbow tables, unique per user. Pepper is a secret key stored outside the database (HSM, vault)—same for all passwords, adds defense if DB exfiltrated without pepper. BCrypt embeds salt in the hash string; pepper must be applied in custom `PasswordEncoder` before BCrypt if used—Spring's `BCryptPasswordEncoder` does not include pepper by default. I rely on strong adaptive hash + unique salt + vault-protected pepper only for high-threat credentials. Rotating pepper requires rehash strategy. Never log or commit pepper. Argon2 with proper parameters often sufficient without pepper if DB and app secrets are separated.

**Q:** Password strength vs hash cost?
**A:** Password policy (length, breach list, MFA) reduces guessable inputs; hash cost (BCrypt strength, Argon2 memory/time) slows offline cracking if hash leaks. High BCrypt strength (12+) increases CPU per login—vulnerable to DoS on login endpoint under burst. I tune cost so p99 login hashing stays under 250ms on prod hardware; pair with rate limiting and CAPTCHA after failures. `DelegatingPasswordEncoder` upgrades weak legacy hashes on successful login. Strength policy without adaptive hash is worthless—MD5 with 20-char password still dies in hours. Monitor login latency after cost bump; K8s HPA does not help CPU-bound password verify on single thread per request.

**Q:** Integration with Passkeys/WebAuthn?
**A:** Passkeys use WebAuthn/FIDO2—public key crypto, no password stored. Spring Security 6.4+ adds passkey support via `WebAuthnConfigurer` alongside traditional login. Flow: register credential, authenticate with challenge-response; store `PublicKeyCredential` entity linked to user. Passwordless reduces credential-stuffing risk; fallback recovery codes required. BFF must serve WebAuthn ceremony over HTTPS with correct `rpId`. I would not build custom crypto—use Spring Security module or Keycloak passkey support. Migration: offer passkey enrollment while `DelegatingPasswordEncoder` still handles legacy passwords. Audit credential lifecycle on device loss.

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
**A:** Proof Key for Code Exchange: client generates `code_verifier` (random), sends SHA256 `code_challenge` with authorization request; token endpoint requires original `code_verifier` matching challenge—prevents stolen authorization code replay from mobile/deep-link intercept. Required for public clients (SPA, mobile) without client secret. Spring Authorization Server and `oauth2Client` support PKCE parameters. BFF with confidential client may still use PKCE for defense in depth. `S256` method is standard. Misconfiguration: accepting token exchange without verifier validation—OAuth server audit finding. Test with OAuth2 test client in integration suite.

**Q:** JWT vs opaque token introspection?
**A:** JWT access tokens are self-contained—resource server validates signature, `exp`, `iss`, `aud` locally without call to auth server. Opaque tokens require introspection endpoint (`/oauth2/introspect`) per request—higher latency, central revocation. I use JWT for internal microservices with short TTL (5-15 min) and key rotation via JWKS. Opaque fits when immediate revocation is mandatory and call volume is low. Spring Resource Server `JwtDecoder` caches JWKS with refresh. Pitfall: JWT without audience check—token for service A accepted by service B. Opaque introspection needs circuit breaker—auth server outage should not fail open.

**Q:** Spring Authorization Server?
**A:** SAS is Spring's OAuth2/OIDC authorization server—embed in Boot app for internal IdP, issues JWT access tokens, supports authorization code, client credentials, refresh. Alternative to Keycloak when you need tight Spring integration and minimal footprint. You own HA, key rotation, user store, and compliance. I choose SAS for internal service-to-service token minting in greenfield; Keycloak for enterprise SSO, LDAP, admin UI. SAS 1.x aligns with Security 6 lambda DSL. Production: run SAS cluster behind load balancer, HSM for signing keys, database for consent and refresh tokens. Not a drop-in for social login without extra work.

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
**A:** Implement `ConstraintValidator<MyAnnotation, MyType>` as Spring bean for DI—validate cross-field rules (`endDate` after `startDate`) or call repository for uniqueness. Register on field or class with `@Constraint(validatedBy=...)`. `@Valid` on controller param triggers validation; groups via `@Validated(Create.class)`. Keep validators fast—remote calls belong in service layer with circuit breaker, not sync validator. I use custom validator for ISO country + currency pairs on payment DTOs. Test with `Validator` bean directly in unit tests. Pitfall: validator not a Spring bean when instantiated only via `Validation.buildDefaultValidatorFactory()`—use `@Autowired` constructor in Boot context.

**Q:** Programmatic `Validator` usage?
**A:** Inject `jakarta.validation.Validator` and call `validator.validate(dto, CreateGroup.class)` in service when validation depends on runtime state not expressible on controller boundary—wizard steps, Kafka message processing. Collect `ConstraintViolation` set and map to domain errors. Useful in batch jobs importing CSV before persist. Does not replace controller `@Valid`—duplicate validation at boundary and domain if invariants differ. I validate Kafka `OrderCreated` events programmatically before side effects—HTTP annotations never run. Performance: cache `ValidatorFactory`—inject singleton `Validator` only.

**Q:** Validation in WebFlux?
**A:** Use `@Valid` on handler method parameters with `WebFluxConfigurer` enabling validation—returns 400 via `WebExchangeBindException` handled in `@ControllerAdvice`. `@Validated` on controller class enables method-level validation on service called from reactive chain—still blocking unless validated on `Mono` via `flatMap` with manual validator. Kotlin coroutines and WebFlux need `awaitSingle` patterns—do not block event loop validating. Custom validators must not call blocking JDBC—use reactive repository or validate earlier in MVC adapter. I keep WebFlux APIs thin; heavy validation on incoming DTO before `Mono` pipeline starts. Problem Details for `WebExchangeBindException` match MVC consistency.

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
**A:** Spring MVC resolves exceptions through ordered `HandlerExceptionResolver` beans: `ExceptionHandlerExceptionResolver` (`@ExceptionHandler`) runs before `ResponseStatusExceptionResolver` and default resolver. `@ControllerAdvice` with `@Order(Ordered.HIGHEST_PRECEDENCE)` wins over generic handlers. `ResponseEntityExceptionHandler` base class ordering matters for validation vs custom domain exceptions. Security's `ExceptionTranslationFilter` handles auth before MVC for filter-chain failures. I put specific domain handlers (`InsufficientInventoryException`) above catch-all `Exception`. WebFlux uses `HandlerExceptionResolver` reactive counterparts—different chain. Debug with logging `WARN` on unresolved exceptions—often means handler not matching subclass.

**Q:** Security exceptions handling?
**A:** `AccessDeniedException` and `AuthenticationException` are handled by Spring Security's filter chain `ExceptionTranslationFilter`—redirect to login or 401/403 JSON depending on `AuthenticationEntryPoint` and `AccessDeniedHandler`. `@ControllerAdvice` does not catch exceptions thrown in filters—configure `server.error` and security handlers separately. For APIs, use `BearerTokenAuthenticationEntryPoint` returning 401 problem+json. Method security `AccessDeniedException` propagates to MVC if thrown from controller-called service—`@ExceptionHandler` can map it. I customize `AccessDeniedHandler` to log principal and resource without stack trace to client. Test with MockMvc `csrf` and JWT missing/expired scenarios independently.

**Q:** WebFlux `@ControllerAdvice` differences?
**A:** `@ControllerAdvice` applies to `@RestController` on WebFlux but exception types differ: `WebExchangeBindException` instead of `MethodArgumentNotValidException`, `ResponseStatusException` handling via reactive adapter. Handlers can return `Mono<ResponseEntity<ProblemDetail>>` for async error bodies. `@ExceptionHandler` methods must not block—no JDBC in advice. Global error attributes use `ErrorAttributes` reactive implementation. Same `@Order` rules for multiple advice beans. I keep shared problem-detail mapping in a base class with MVC and WebFlux subclasses if both stacks coexist during migration. Security filter exceptions still bypass advice.

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
**A:** Implement `HttpMessageConverter` or extend `AbstractHttpMessageConverter`, register via `WebMvcConfigurer.extendMessageConverters` (append) or `configureMessageConverters` (replace defaults—dangerous). Use for proprietary binary formats, CSV export, or `application/problem+json` customization. Order in converter list matters—first match wins on `canRead`/`canWrite`. Boot auto-configures Jackson—customize via `Jackson2ObjectMapperBuilderCustomizer` before writing custom converter. I added Avro converter once for internal event API—kept JSON for public. Test with `MockMvc` asserting Content-Type and round-trip. Wrong registration replaces Jackson entirely—breaks all JSON endpoints.

**Q:** Two `ObjectMapper` beans — which wins?
**A:** Boot auto-configures a primary `ObjectMapper` for HTTP message conversion unless you define `@Bean ObjectMapper` without `@Primary`—then ambiguity or override depends on `@ConditionalOnMissingBean`. Multiple `@Bean ObjectMapper` without `@Primary` causes `NoUniqueBeanDefinitionException` or unpredictable injection. HTTP layer uses the one wired into `MappingJackson2HttpMessageConverter`. Custom `ObjectMapper` for Redis/Kafka should be `@Qualifier("redisMapper")` separate bean—not `@Primary`. I customize via `Jackson2ObjectMapperBuilderCustomizer` to keep single source of truth. Pitfall: Feign and RestClient pick different mappers if not sharing builder—date format drift between services.

**Q:** JSON views and API versioning?
**A:** `@JsonView` on controller methods filters serialized fields per view class—useful for admin vs public summary on same DTO without duplicate types. Combine with API versioning: `/v1` returns `PublicView`, `/v2` adds fields in `DetailedView`. Requires `@JsonView` on controller and view class annotations on DTO fields. OpenAPI must document per-version schemas—springdoc needs separate groups or manual `@Schema` per view. I prefer separate DTO records per major version for clarity over views—views obscure compile-time safety. Views help incremental additive changes within same version when clients use Jackson views explicitly.

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
**A:** Filter—earliest point, covers all requests including static resources and failed security paths. `OncePerRequestFilter` sets MDC `correlationId` from `X-Request-Id` header or generates UUID, echoes in response header. Interceptor runs after handler mapping—misses filter-chain rejections and is MVC-only (not WebFlux filter equivalent without `WebFilter`). I use servlet filter at `Ordered.HIGHEST_PRECEDENCE` plus `TaskDecorator` for async. Ingress controller (nginx/Envoy) may generate ID—honor incoming header for distributed traces. Always `MDC.clear()` in `finally`—Tomcat thread pool leak caused wrong customer data in logs.

**Q:** Can AOP see HTTP headers?
**A:** Not directly—AOP `@Around` on service methods has no `HttpServletRequest` unless you inject `RequestContextHolder.getRequestAttributes()` (servlet) or pass headers as method args. Cleaner: filter/interceptor extracts headers into MDC or request-scoped bean, service reads context. `@RequestHeader` only on controller methods. Anti-pattern: injecting `HttpServletRequest` into singleton service—thread safety nightmare. For tracing, rely on Micrometer observation propagation rather than AOP reading headers. WebFlux: Reactor Context, not thread-local request. Design services header-agnostic; pass `tenantId` explicitly from controller.

**Q:** Ordering `@Order` across layers?
**A:** Filters use `FilterRegistrationBean` order or `@Order` on `@Component` filters—lower runs earlier. Security filter chain is separate ordered list inside `SecurityFilterChain`. HandlerInterceptors use `order` in `WebMvcConfigurer.addInterceptors`. `@ControllerAdvice` uses `@Order` for exception handler precedence. AOP aspects use `@Order` on aspect class—lower wraps outer (transactions often order 0). They are independent namespaces—`@Order(1)` on filter ≠ `@Order(1)` on advice. Document in ADR: correlation filter HIGHEST, security default, MVC interceptor after security. Cross-layer bugs: MDC cleared in interceptor `afterCompletion` while async still running.

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
**A:** BlockHound detects blocking calls on Netty event loop threads—`jdbcTemplate.query`, `Thread.sleep`, synchronized file I/O inside reactive operators stall all connections on that loop. Run BlockHound in CI on WebFlux integration tests. Fix: `subscribeOn(Schedulers.boundedElastic())` for blocking sections or move blocking work to MVC with virtual threads. R2DBC and reactive Redis avoid blocking; mixing JPA in WebFlux without offload is architectural mistake. Production symptom: latency spikes correlated with single-thread event loop at 100% in reactor metrics. I default new services to MVC + virtual threads unless end-to-end reactive justified.

**Q:** When is MVC + virtual threads enough?
**A:** When workload is blocking I/O—JDBC/JPA, RestClient, file I/O—and you do not need SSE/streaming at massive scale on few cores. Boot 3.2+ `spring.threads.virtual.enabled=true` lets Tomcat use virtual threads; Hikari and HTTP clients block carriers but scale to thousands of concurrent requests. Simpler ops than WebFlux—same `@Transactional`, same Spring Data, same debugging. I chose MVC + virtual threads for order service processing 2k RPS with Postgres—p99 matched WebFlux prototype without reactive rewrite. Not enough for backpressure-heavy streaming ingestion—keep WebFlux or Kafka Streams there.

**Q:** R2DBC vs blocking JDBC in reactive?
**A:** R2DBC is non-blocking relational driver—fits WebFlux end-to-end without blocking event loop. Blocking JDBC on WebFlux requires `Schedulers.boundedElastic()`—adds thread hop overhead and loses reactive benefits. JPA/Hibernate has no first-class reactive story—use R2DBC templates or Spring Data R2DBC entities separately from JPA domain. I use R2DBC for read-heavy telemetry API; JPA remains on MVC write path in hybrid only with clear module split. Transactions: `TransactionalOperator` reactive vs `@Transactional` blocking—do not mix in one request. Connection pool sizing differs—R2DBC pools are smaller, multiplexed.

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
**A:** OpenFeign (`@FeignClient`) is Spring Cloud declarative client with load balancer integration—extra dependency, mature ecosystem. RestClient + HTTP interface (`@HttpExchange`) is Spring Framework native in Boot 3.2+—fewer layers, shared `RestClient.Builder` with timeouts and observation. I migrate internal sync calls to HTTP interfaces; keep Feign if platform starter standardizes resilience and service discovery. Feign fallbacks are deprecated patterns—use Resilience4j at call site. Both need explicit timeout and error mapping. Greenfield Boot 4 internal mesh: native HTTP services; Feign only if org mandates Spring Cloud BOM.

**Q:** Connection pooling for WebClient?
**A:** Configure `ReactorClientHttpConnector` with `ConnectionProvider.builder("inventory").maxConnections(500).pendingAcquireMaxCount(1000).build()`—default pool is small. Timeouts via `HttpClient.responseTimeout` and `option(ChannelOption.CONNECT_TIMEOUT_MILLIS)`. One `WebClient` bean per downstream host shares pool—do not create new builder per request. Micrometer metrics on pool pending acquire alert saturation before thread issues. For sync-looking code using WebClient, `.block()` still uses pool—size for peak concurrent blocks. In K8s, pool per pod × replicas must not exceed downstream server `max_connections`.

**Q:** When is RestTemplate still OK?
**A:** Legacy codebases and quick internal scripts—`RestTemplate` works but is in maintenance mode. Acceptable short-term in stable modules not on hot path during Boot 3 migration. New code: `RestClient` with fluent API and observation. RestTemplate shares connection pool via `ClientHttpRequestFactory`—must configure `HttpComponentsClientHttpRequestFactory` pooling explicitly or every call opens new connection. I allow RestTemplate only with sunset ticket and ban in ArchUnit for `..api..` packages. Security patches still apply—no functional freeze but no new features. Migration: mechanical replace with RestClient builder bean.

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
**A:** ShedLock: lightweight JDBC/Redis lock around existing `@Scheduled` method—one pod wins, minimal infra. Quartz cluster: full job scheduler with misfire policies, persistent triggers, UI—heavier ops. I use ShedLock for hourly cache refresh across 6 K8s replicas—5 lines config. Quartz when complex cron dependencies, job history audit, or pausing job groups required. Neither replaces idempotent job design—lock failure or double-fire still possible on TTL edge cases. ShedLock `lockAtMostFor` prevents zombie lock holder after pod kill. K8s CronJob is alternative for infrequent batch—no in-JVM scheduler at all.

**Q:** `@Scheduled` with virtual threads?
**A:** Configure `TaskScheduler` bean using `SimpleAsyncTaskScheduler` with virtual threads (`setVirtualThreads(true)` in Boot 3.2+) or custom `ScheduledExecutorService` backed by virtual thread factory. Default single-thread scheduler blocks long jobs—always define pool. Virtual threads help when scheduled task does blocking HTTP/JDBC—many overlapping schedules do not exhaust platform threads. Still need ShedLock in cluster—virtual threads do not coordinate pods. Monitor task duration—`@Scheduled` fixedRate queues next run even if previous still running unless configured otherwise. I set `fixedDelay` for reconciliation to avoid overlap.

**Q:** Timezone in cron expressions?
**A:** Spring `@Scheduled(cron="0 0 2 * * *", zone="UTC")`—zone attribute mandatory for global services; default is server JVM timezone—pods in different regions fire at different instants without explicit zone. K8s CronJob uses controller timezone unless `timeZone` field set (K8s 1.27+). DST transitions cause skipped or doubled runs—prefer UTC for financial jobs. Document cron meaning in comment; use external scheduler for complex calendars. I store `zone` in config property for audit. Integration test with `Clock` fixed instant verifying trigger logic separately from scheduler.

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
**A:** `@SpringBootTest` loads full context—use sparingly for end-to-end journeys (place order → Kafka → email). `@WebMvcTest` for controller HTTP contract with mocked services—fast. `@DataJpaTest` for repository SQL with Testcontainers. Rule: one or two full context tests per module; dozens of slices. CI time explodes when every test is `@SpringBootTest`—14 minutes to 3 minutes after slice migration on our repo. `@SpringBootTest(webEnvironment=NONE)` for bean wiring smoke without servlet. New feature: slice first, add integration test only if cross-cutting concern untested.

**Q:** `@MockBean` vs `@Mock`?
**A:** `@Mock` (Mockito) injects mock in plain unit test—no Spring context. `@MockBean`/`@MockitoBean` (Boot 3.4) replaces bean in Spring test context—required for `@WebMvcTest` and `@SpringBootTest` partial wiring. `@MockBean` on field in slice test registers mock in context; `@InjectMocks` service test uses `@Mock` collaborators without Spring. Pitfall: `@MockBean` resets context cache key—can slow suite if overused on base class. I use pure Mockito for domain logic; `@MockitoBean OrderService` only in `@WebMvcTest`. Verify interactions with `verify(mock)` either way.

**Q:** Testcontainers for integration?
**A:** Real Postgres/Kafka/Redis in Docker via Testcontainers—`@ServiceConnection` auto-wires Boot 3.1+ without `@DynamicPropertySource` boilerplate. Catches dialect-specific SQL, JSONB, and driver bugs H2 misses. CI needs Docker-in-Docker or privileged runner. Reuse locally (`testcontainers.reuse.enable=true`) speeds dev; disable reuse in CI for isolation. Pin image versions/digests—`postgres:16-alpine` not `latest`. Parallel test classes need Ryuk or container per class—flaky shared state otherwise. Cost: slower than slices—run integration in separate CI stage nightly if PR time critical.

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
**A:** Spring Test caches application context by configuration key—first test pays startup, siblings reuse. `@DirtiesContext` evicts cache after test, forcing full context rebuild—next test pays 5-30 seconds again. With 50 tests annotated, suite becomes minutes. Indicates tests mutate shared singleton state—fix root cause instead. Alternatives: `@BeforeEach` reset data, `@Sql` cleanup, separate test classes with different profiles only when necessary. I removed `@DirtiesContext` from cache tests by injecting `CacheManager` and `clear()` in teardown—suite dropped 8 minutes. Use only for `@Cacheable` eviction integration verifying annotation behavior once.

**Q:** Alternative isolation strategies?
**A:** Prefer `@Transactional` rollback on `@DataJpaTest` for DB isolation. Unique UUIDs per test for natural keys. `@Sql(scripts="/cleanup.sql", executionPhase=AFTER_TEST_METHOD)`. `@DynamicPropertySource` random ports. Separate `@Nested` classes share context config but own cleanup hooks. Testcontainers: TRUNCATE in `@BeforeEach` faster than context restart. For Kafka: unique topic per test class with `@Autowired AdminClient` delete. Never mutate static `@PostConstruct` caches—refactor to bean. Parallel CI: fork per module, not `@DirtiesContext` per method.

**Q:** Shared context in integration tests?
**A:** Spring caches context when test class configuration identical—`@Import`, profiles, properties must match to share. Put common `@Import(TestContainersConfig.class)` on abstract base—one startup per module. `@MockBean` in base class affects all subclasses' context key—avoid unless intentional. `@TestPropertySource` differences split cache. I document 'context slices' in test package README. Anti-pattern: different `@MockBean` per test method forces new context—use `@MockitoBean` programmatic or pure Mockito. Measure with `-Dspring.test.context.cache.maxSize` logging in debug when suite slow.

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
**A:** Each active request needing DB holds one Hikari connection for TX duration. If `server.tomcat.threads.max=200` and `maximum-pool-size=10`, 190 threads block waiting on pool—p99 explodes. Rule of thumb: pool size ≥ expected concurrent DB-bound requests, not Tomcat max. Virtual threads increase concurrent requests but DB connections remain bottleneck—size pool for DB capacity, limit Tomcat or use semaphores. I alert when `hikaricp.connections.pending > 0` sustained. Load test correlates thread dump blocked on `getConnection` with Tomcat active count. Fix slow queries before raising pool to 100.

**Q:** Undertow vs Tomcat tuning?
**A:** Boot supports Tomcat (default), Jetty, Undertow via starter swap. Undertow uses XNIO workers—different knobs than Tomcat `threads.max`. Tuning is not drop-in—load test after switch. I stay on Tomcat for ecosystem familiarity and virtual thread support path. Undertow historically smaller memory footprint—consider if measured. HTTP/2 and TLS settings differ. Switching servers for 'performance' without profiling is guesswork. K8s: same Hikari/Tomcat thread relationship regardless of server—connection math unchanged. Document server choice in ADR; ops runbooks must match.

**Q:** HTTP/2 and connection limits?
**A:** HTTP/2 multiplexes streams on one TCP connection—fewer connections from client, but server still processes concurrent streams per connection. Tomcat `maxConnections` and `maxKeepAliveRequests` affect connection reuse. ALPN TLS required. Behind ingress, HTTP/2 to client and HTTP/1.1 to pod is common—pool sizing on outbound RestClient still matters. Pitfall: assuming HTTP/2 removes need for thread pool—it reduces connection count, not CPU work. Enable only after cert and cipher audit. Monitor `tomcat.connections.current` and stream reset rates.

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
**A:** `server.shutdown=graceful` stops accepting new connections, waits for in-flight requests up to `spring.lifecycle.timeout-per-shutdown-phase`. Immediate kills active requests—502 during K8s rollouts. Graceful pairs with `terminationGracePeriodSeconds` > shutdown timeout + preStop delay. Without graceful, deploy during traffic causes payment duplicates if client retries. I set 30s graceful, 45s K8s grace, preStop sleep 5s for LB drain. Virtual threads still need graceful drain—carrier threads finish work. Test rollout under load in staging with chaos mesh SIGTERM.

**Q:** K8s preStop hook pattern?
**A:** preStop: `sleep 5` or HTTP call to fail readiness before SIGTERM—lets Service endpoints remove pod from load balancer while still processing in-flight requests. Sequence: preStop sleep → readiness probe fails → endpoints update → graceful shutdown starts. Without sleep, race sends traffic to terminating pod. Combine with `server.shutdown=graceful`. For Kafka consumers, preStop should trigger listener stop and offset commit—use `KafkaListenerEndpointRegistry`. Document hook in Helm chart; tune sleep from LB propagation measurement (AWS ALB ~5s).

**Q:** Kafka consumer stop timeout?
**A:** Spring Kafka `KafkaMessageListenerContainer.stop()` waits for in-flight records up to `setShutdownTimeout`—default may be too short for long processing. On SIGTERM, Boot graceful shutdown stops containers; insufficient timeout causes rebalance storm and duplicate processing. Set `spring.kafka.listener.shutdown-timeout` aligned with max processing time per poll batch. Idempotent consumer or outbox required regardless. I use 30s shutdown, 60s K8s grace. `stopImmediate=true` loses in-flight work—only for force kill. Monitor consumer lag during deploys—spike indicates insufficient drain.

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
**A:** ChainedTransactionManager commits managers sequentially—if the second commit fails, the first is already committed with no rollback. That is not two-phase commit. I avoid it for cross-database writes; use saga/outbox instead. Where I have seen it: legacy reporting DB plus orders DB in one modular monolith—partial commits caused reconciliation nightmares. Read-replica routing with a single manager is safer than chaining. If you must chain, keep operations idempotent, alert on partial failure, and never use it for money movement. Boot docs deprecate it for good reason—treat as code smell in design review.

**Q:** `@Transactional(transactionManager=...)`?
**A:** When multiple `PlatformTransactionManager` beans exist, `@Transactional` without qualifier uses `@Primary` manager—silent wrong DB writes. Specify `@Transactional("ordersTransactionManager")` matching bean name on service methods touching that datasource. Each EMF needs its own manager and `@EnableJpaRepositories` `transactionManagerRef`. Integration test must wire both datasources or miss bug. Read-only replica routing sometimes uses same manager with routing datasource—no qualifier needed. Document manager names in module README. ArchUnit can enforce repository package uses correct manager qualifier.

**Q:** Read replica routing?
**A:** `AbstractRoutingDataSource` with `determineCurrentLookupKey()` reading thread-local set by `@Transactional(readOnly=true)` aspect routes SELECT to replica. Writes must hit primary—aspect sets key false for readOnly=false. Lag: user updates profile then immediate read may show stale email—stick to primary for read-after-write flows. Separate Hikari pools per target—size replica pool for read traffic. Health check replica connectivity. Failover: if replica down, route reads to primary with circuit breaker. Test routing with two Testcontainers or mock lookup key assertions.

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
**A:** Flyway: SQL-first, versioned `V1__desc.sql`, simple mental model, checksum enforcement—my default for Spring teams. Liquibase: XML/YAML changesets, built-in rollback declarations (use cautiously in prod), better for DBA review workflows preferring abstract changes. Both integrate with Boot auto-config. Pick one per org—mixing both is chaos. Flyway community edition sufficient for most; Liquibase Pro for drift detection enterprise features. CI runs migrate against Testcontainers clone of prod schema. Immutable applied migrations—never edit V3 after release.

**Q:** Migrations in init container vs app startup?
**A:** Init container (K8s Job or pod initContainer) runs Flyway with DDL credentials before app pods start—app user lacks CREATE TABLE. Prevents race when 10 replicas start simultaneously all running migrate. App startup migrate simpler for small teams—use Flyway distributed lock. I prefer init Job in prod, app-start migrate in dev. Readiness fails until migrations complete if app runs them—coordinate probe timing. Secrets for migration user in K8s Secret, rotated separately. Rollback: forward-only migrations plus compensating script—Flyway undo rarely in prod.

**Q:** Rollback strategy?
**A:** Application rollback: redeploy previous image—schema must be backward compatible (expand/contract). Flyway has no automatic down in community—write forward fix `V4_1__revert_column.sql` instead of editing history. Liquibase rollback tags possible but risky on large tables—prefer expand/contract. Feature flags decouple code rollback from schema. I never `DROP COLUMN` same release as code stop using it. Database restore from backup is disaster recovery, not deploy rollback. Test rollback drill quarterly: deploy N+1, rollback N with migrated schema.

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
**A:** Technically works on Spring Data proxy methods but couples caching to persistence layer—eviction scattered, key semantics unclear. I cache at service layer returning DTOs—clear TTL and `@CacheEvict` on admin update methods. Repository cache caches entities—Hibernate lazy/session issues when cached entity rehydrated outside TX. `@Cacheable(sync=true)` on hot product lookup prevents stampede. Redis keys need tenant prefix. Pitfall: caching `Page` results with wrong key missing pageable params. ArchUnit: no `@Cacheable` on `..repository..` packages.

**Q:** Cache stampede mitigation?
**A:** Thundering herd when hot key expires—all threads hit DB simultaneously. Caffeine `@Cacheable(sync=true)` single-flights reload per key. Redis: probabilistic early expiration, jittered TTL, or locking with `SETNX`. Application-level: prewarm cache on deploy, background refresh before expiry. I set TTL 15m with refresh at 14m for product catalog. Monitor cache miss spike metric after expiry. For financial balances, do not cache—consistency beats performance. Hazelcast near-cache has similar stampede patterns—configure accordingly.

**Q:** Redis vs Caffeine local cache?
**A:** Caffeine: in-process, microsecond latency, no network partition—per-pod inconsistent view acceptable for reference data. Redis: shared across replicas, pub/sub eviction, survives pod restart—use for user session or rate limiting across cluster. I default Caffeine for catalog metadata; Redis when invalidation must reach all pods immediately after admin update. Hybrid: Caffeine L1 with Redis L2—complexity cost. Serialize DTOs to Redis, not JPA entities. Monitor Redis memory and key cardinality; Caffeine `maximumSize` and `expireAfterWrite`.

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
**A:** Spring DevTools remote restart opens a tunnel allowing classpath reload from IDE—never enable in prod or staging exposed to network. Attack surface: remote code reload equals RCE if endpoint reachable. `spring.devtools.remote.secret` required if used locally against shared dev server. I exclude `spring-boot-devtools` from prod Maven profile with `optional` dependency scope verify in CI—SBOM check. Accidental prod inclusion happened via parent POM—container escape via devtools restart. Use JRebel only in local IDE, not server-side DevTools remote.

**Q:** How to verify DevTools absent in prod image?
**A:** Maven: `mvn dependency:tree -Dincludes=org.springframework.boot:spring-boot-devtools` on prod profile must be empty. CI step: `jar tf app.jar | grep devtools` fails build if found. Actuator `/actuator/conditions` shows DevTools auto-config negative in prod. Gradle `bootJar` exclude configuration. Image scan with Trivy for devtools artifact. I add ArchUnit or script gate in pipeline—blocked release once when starter pulled transitively. `optional=true` on devtools dependency in pom—not enough alone if another module declares it.

**Q:** LiveReload in containers?
**A:** DevTools LiveReload websocket watches classpath—meaningless in Docker/K8s where code is baked in image. Disable `spring.devtools.livereload.enabled=false` in containerized dev environments using mounted volumes if weird restarts occur. Only useful: local `spring-boot:run` with IDE compile-on-save. In K8s dev namespaces with skaffold sync, LiveReload conflicts with hot sync—pick one workflow. Prod: ensure livereload port 35729 not exposed in Dockerfile EXPOSE. Security scanners flag open reload ports.

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
**A:** Spring Boot layered JAR splits dependencies, snapshot deps, application code, loader—Docker COPY each layer separately. App code changes rebuild only thin application layer; deps cached weeks. CI Kaniko/GitHub Actions cache cuts image build 6min→90sec in our pipeline. Enable `layers.enabled` on `spring-boot-maven-plugin`, use Paketo or Dockerfile from `layertools extract`. Pitfall: changing SNAPSHOT parent daily invalidates snapshot layer—use release versions for stable cache. Measure with build metrics; not worth complexity for tiny apps deploying monthly.

**Q:** GraalVM native image trade-offs?
**A:** Pros: 50-200ms cold start, lower memory RSS—ideal Lambda/Knative. Cons: longer build (10-20min), reflection/proxy hints maintenance, lower peak throughput on some workloads, harder debugging. Spring AOT processes beans at build time—no runtime classpath surprises. I use native for auth edge service; batch payroll stays JVM. PGO improves performance—collect profiles in staging. Rollback path: keep JVM image in same registry tag family. Native incompatible with some agents (bytecode weaving)—verify before mandate.

**Q:** CDS / class data sharing?
**A:** JVM Class Data Sharing archives loaded classes—faster startup on JVM mode without full native compile. Spring Boot 3.3+ documents CDS training run: `java -XX:ArchiveClassesAtExit=app.jsa -jar app.jar` then `-XX:SharedArchiveFile=app.jsa`. Middle ground between plain JVM and native—30-40% startup improvement measured on our API. Works with containers—bake `.jsa` into image layer. Not a substitute for native when memory floor critical. Re-run CDS training when dependency upgrades significantly.

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
**A:** `ObjectProvider<T>` injects lazy accessor—`getObject()` resolves when called, no proxy subclass of your service. `@Lazy` on injection creates proxy delaying bean init until first method call—can break circular deps but defers errors. I prefer `ObjectProvider<PaymentClient>` for optional or prototype deps—explicit call site. `@Lazy` on `@Bean` defers factory method—different semantics. Both beat field injection. Production: `ObjectProvider` when handling optional feature flags; `@Lazy` last resort for cycle breaking with ADR documenting debt.

**Q:** Constructor cycle refactor patterns?
**A:** Extract shared dependency into third bean both services need. Introduce event (`ApplicationEventPublisher`) for one direction async decoupling. Use `ObjectProvider` or `@Lazy` on one side—band-aid. Interface segregation: split fat service into read vs write beans. Boot 2.6+ fails fast on cycles—good forcing function. I refactored `OrderService`↔`PaymentService` cycle via `PaymentPort` interface implemented by third adapter. Never `spring.main.allow-circular-references=true` in prod. Kotlin `lateinit` does not fix design—same graph.

**Q:** Kotlin lateinit circular deps?
**A:** Kotlin constructor injection fails on cycle same as Java—`lateinit var` field injection 'fixes' compile but hides cycle and breaks testability. `by lazy` delegate on injected property still needs graph resolution. Proper fix: redesign boundaries. Spring allows `@Lazy` on constructor param in Kotlin. I enforce primary constructor injection in detekt rule; no `@Autowired lateinit` in services. Circular dependency in Boot 3 fails at startup—translate to architecture discussion in interviews. `ObjectProvider` in constructor is idiomatic Kotlin compromise.

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
**A:** All `ApplicationRunner` and `CommandLineRunner` beans run after context refresh, before `ApplicationReadyEvent`. Order via `@Order` on runner bean—lower first. Multiple runners without `@Order` follow registration order—undefined across config classes. `ApplicationRunner` receives `ApplicationArguments` for parsed flags. Do not run long blocking work without timeout—delays K8s readiness. I use order 1 for config validation, order 2 for cache warm, Flyway already ran earlier. Fail-fast: throw from runner prevents ready signal—pod CrashLoop until fixed.

**Q:** Run migrations in runner vs Flyway?
**A:** Flyway/Liquibase auto-config runs during context startup before JPA init—correct place for schema. `ApplicationRunner` for data seeding dev/test only—not DDL. Mixing DDL in runner bypasses checksum tracking and races multi-pod deploy. Init container Flyway + runner seed in dev profile acceptable. Production: migrations in Job/initContainer; runners only for non-schema startup tasks (feature flag sync). If runner migrates, second pod may double-apply without distributed lock. Keep schema tool authoritative; runners for idempotent reference data load with profile guard.

**Q:** Fail-fast on runner exception?
**A:** Uncaught exception in `ApplicationRunner` fails startup—pod does not reach ready—correct for misconfiguration (missing vault secret). Distinguish fatal vs deferrable: validate required URLs in runner throw; optional telemetry register log warning. K8s CrashLoopBackoff alerts team—ensure error message clear in logs. I throw when Kafka topic ACL missing; do not throw when optional metrics exporter down. `@Order` critical validators first. Integration test: assert context fails when required property missing. Opposite anti-pattern: swallow in runner, serve 500 on every request.

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
**A:** Global `Jackson2ObjectMapperBuilderCustomizer` sets ISO-8601 dates, timezone UTC for all API serialization—consistent contract. `@JsonFormat` on field overrides for legacy exceptions—document in OpenAPI. Mixing causes mobile client bugs when one endpoint returns epoch millis. I globalize `JavaTimeModule` + `WRITE_DATES_AS_TIMESTAMPS disabled`; `@JsonFormat` only for external integration DTOs matching vendor format. Custom `ObjectMapper` for Redis must not drift from HTTP mapper without reason. Contract tests assert date format per endpoint.

**Q:** Store UTC in DB always?
**A:** Yes—`timestamptz` in Postgres stores UTC internally; JDBC with `Instant` or `OffsetDateTime` UTC avoids DST bugs. Display conversion happens in UI with user zone. JPA `Instant` maps cleanly; `LocalDateTime` without zone caused DST incident in billing window. Hibernate `@CreationTimestamp` on `Instant` field. Scheduled jobs cron in UTC. Audit logs store UTC + user zone header if needed for support. Never rely on server JVM default zone—explicit `ZoneOffset.UTC` in code and DB connection params.

**Q:** User timezone in audit logs?
**A:** Store event time UTC in DB; log MDC fields `userTimezone=America/Chicago` from `Accept-Language` or user profile for support interpretation. Do not convert stored UTC to user zone in DB column—query nightmares. API returns ISO instant; client formats local. For scheduled 'end of business day' per tenant, store tenant zone in config, compute with `ZonedDateTime`. Audit CSV export includes both UTC and localized column for regulators. Kotlin `kotlinx-datetime` or `java.time` only—no `Date`.

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
**A:** Multipart `MultipartFile` buffers in memory or disk threshold—fine for small admin uploads. Large files: stream `InputStream` to S3 via `WebClient` or AWS SDK async without loading byte array—Tomcat `max-swallow-size` and `spring.servlet.multipart.max-file-size` tuned. Virus scan stream through pipeline. REST direct upload hits app pods—prefer presigned S3 URL so bytes bypass API. WebFlux `DataBuffer` streaming for chunked. OOM incident: 200MB multipart default heap load—switched to presigned POST.

**Q:** Virus scan in pipeline?
**A:** Scan before persist or async quarantine—ClamAV sidecar, S3 trigger Lambda, or commercial API. Sync scan in request thread adds latency—return 202 Accepted after staging to quarantine bucket, scan, then promote. Block EICAR test in CI. Spring Integration SFTP adapter routes to scan channel before JPA persist. Fail closed: infected file never reaches object store. Log scan result with correlation id; no PII in alert. K8s: scan job as init step for user uploads metadata only until CLEAN.

**Q:** S3 presigned vs server upload?
**A:** Presigned URL: client PUTs directly to S3—scales bandwidth off API pods, shorter request path. Server upload: simpler auth, virus scan inline, but Tomcat threads and memory suffer. I use presigned for mobile photo upload; server proxy only when contract requires hiding bucket. Presigned TTL short (15min), content-type and size conditions in policy. Spring generates via `S3Presigner`. Audit `objectKey` in DB after client confirms upload callback. CORS on bucket for browser PUT.

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
**A:** Simple broker: in-memory per instance—dev only, breaks with multiple pods. StompBrokerRelay connects to RabbitMQ/ActiveMQ—shared subscriptions across K8s replicas. Relay config `setRelayHost`, login, virtual host. WebSocket session still sticky or use user destination prefixes carefully. Production chat/notifications use relay; demo uses simple. Heartbeats and disconnect handling differ. Scale relay cluster independently of API pods. Security: authenticate CONNECT frame; authorize SUBSCRIBE per destination.

**Q:** WebSocket auth with JWT?
**A:** Pass token in CONNECT `Authorization` header or query param (query leaks in logs—prefer header or STOMP header). Spring Security messaging `ChannelInterceptor` validates JWT on inbound messages. HTTP session upgrade vs pure JWT stateless—BFF often uses session cookie for WS same-origin. Token expiry mid-session: send STOMP ERROR and force client refresh. Do not trust client-provided userId in frame—derive from validated principal. CORS and CSRF differ for WS—configure `WebSocketSecurity`. Rate limit message frequency per session.

**Q:** Scale WebSocket on K8s?
**A:** Sticky sessions on ingress (sessionAffinity) or externalize subscription state to broker relay—stateless pods preferred with relay. HPA on CPU not sufficient—connection count limits per pod (`server.tomcat.max-connections`). Horizontal scale adds pods; relay RabbitMQ must handle fanout. Use Redis pub/sub for simple broadcast if no STOMP. Monitor open WebSocket gauge per pod; drain on rollout with graceful close. Service mesh WebSocket upgrade timeouts must align. I cap 10k connections/pod with load test validation.

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
**A:** Run with `--debug` or set `logging.level.org.springframework.boot.autoconfigure=DEBUG`—logs full condition evaluation at startup. Actuator `/actuator/conditions` shows which auto-config matched and why beans skipped—essential when Kafka or DataSource missing. In prod, enable conditions endpoint only on management port internally. Report shows `@ConditionalOnClass` failures—wrong classpath in fat jar. I save report output in CI startup test comparing golden file for accidental auto-config drift. Faster than guessing why Redis beans absent.

**Q:** `@ConditionalOnMissingBean` debugging?
**A:** Bean exists earlier than expected—your auto-config backs off silently. Duplicate `@Bean` from scan + auto-config—`@ConditionalOnMissingBean` on auto-config side loses. Use `spring.main.allow-bean-definition-overriding=false` (default) to fail on duplicate. Debug: `BeanFactory.getBeanDefinitionNames()` or conditions report. Custom starter must use `@AutoConfigureAfter` ordering so user beans register first. Test: assert your `@Bean` wins with `@SpringBootTest` and `ApplicationContext` assert single `ObjectMapper`. Common: test `@MockBean` replaces bean triggering missing condition in prod only.

**Q:** Bean overriding in Boot 2.1+?
**A:** Boot 2.1+ disables bean definition overriding by default—two `@Bean` same type fails fast at startup. Previously last bean won silently—dangerous. Enable overriding only in tests if needed (`spring.main.allow-bean-definition-overriding=true`). Auto-config uses `@ConditionalOnMissingBean` instead of overriding. Custom starter should not define `@Bean` user is meant to replace without condition. Failure message lists conflicting definitions—fix by `@Primary`, `@Qualifier`, or remove duplicate. I prefer explicit `@Qualifier` over overriding.

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
**A:** Extends `BeanPostProcessor` with earlier hooks: `postProcessBeforeInstantiation` can return proxy replacing bean before construction—AOP infrastructure uses this. Rare in application code—framework internals (`AbstractAutoProxyCreator`). Misuse breaks bean lifecycle expectations. Seniors recognize name when reading Spring source debugging why bean not constructed. Application devs use standard BPP `postProcessAfterInitialization` for wrapping. If interviewer asks, tie to how `@Transactional` proxy is applied before your constructor body on subclass proxy.

**Q:** `@Role(ROLE_INFRASTRUCTURE)`?
**A:** Marks bean as infrastructure—not counted in some post-processor scans, avoids certain circular dependency checks. Framework beans use `ROLE_INFRASTRUCTURE`; application beans default `ROLE_APPLICATION`. Custom `BeanPostProcessor` should declare `@Role(ROLE_INFRASTRUCTURE)` so it is not post-processed by itself infinitely. Rarely set on user services—misuse hides beans from tooling. Configuration class enhancement and `AutowiredAnnotationBeanPostProcessor` are infrastructure role examples. Know for reading Spring internals and custom starter development.

**Q:** CGLIB `@Configuration` enhancement?
**A:** `@Configuration` classes are CGLIB-subclassed so `@Bean` method inter-calls return singleton from context—not new instances. `proxyBeanMethods=false` (Boot 2.2+) skips enhancement—faster startup, but `@Bean` method calls create new objects unless refactored to direct `@Bean` injection. Lite mode for simple config without inter-bean calls. Full mode required when `@Bean` method A calls `@Bean` method B expecting same instance. Native image requires `proxyBeanMethods=false` often—restructure config. Interview trap: calling `@Bean` method from `@Component` bypasses enhancement.

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
**A:** Kafka transactions (`read_committed`) coordinate produce with consume in same broker TX—limited to Kafka,  max  transactional.id per producer, operational complexity. Transactional outbox: write business row + outbox row in same DB TX; separate poller publishes to Kafka—works with any DB, true atomicity with domain data. I choose outbox for order events; Kafka TX only for stream processing entirely inside Kafka. Outbox handles DB + Kafka dual-write problem. Debezium CDC on outbox table is alternative poller. Never bare `@TransactionalEventListener` alone for money events.

**Q:** `DefaultErrorHandler` and DLT?
**A:** Spring Kafka `DefaultErrorHandler` with `DeadLetterPublishingRecoverer` sends failed records to DLT topic after retry backoff exhaustion. Configure `FixedBackOff` max attempts; serializer same as main topic. DLT consumer for manual triage or alert. Distinguish retryable (`DataAccessException`) vs non-retryable (`SerializationException`) with `DefaultErrorClassifier`. Without DLT, poison pill blocks partition. I monitor DLT lag and set retention 14 days. Idempotent processing still required—retries duplicate. Pair with Micrometer error handler metrics.

**Q:** Exactly-once semantics limits?
**A:** True exactly-once end-to-end (HTTP → DB → Kafka → consumer) is impossible without distributed transactions across heterogeneous systems—marketing term. Practical: idempotent consumer + outbox + dedup key gives 'effectively once.' Kafka EOS is once per transactional.id within broker cluster only. DB unique constraint on `eventId` catches duplicates. I document SLAs as at-least-once with idempotent handlers. Sagas compensate on duplicate detection. Interview: honest about limits, then describe outbox, keys, and DLT—not magic Kafka flag.

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
**A:** `SameSite=Strict` cookies never sent on cross-site navigation—best CSRF protection but breaks OAuth redirect return from IdP (no session cookie on landing). `Lax` sends on top-level GET navigations—default for Chrome, works for login redirect flows. `None` requires `Secure` flag—needed for embedded cross-site iframes rare in APIs. Spring Session cookie config `server.servlet.session.cookie.same-site=lax` for BFF. API-only JWT in Authorization header unaffected. Misconfigured Strict broke our Google login until we diagnosed cookie not sent on callback.

**Q:** Double-submit cookie pattern?
**A:** CSRF defense for SPA: server sets non-httpOnly cookie with random token; client reads cookie JavaScript value, sends same value in header; server compares—attacker cross-site cannot read cookie to forge header. Spring Security CSRF with cookie repository supports this for stateless-ish SPAs. Pure JWT APIs without cookies skip CSRF. Not needed for Bearer-only mobile APIs. Combine with SameSite=Lax for defense in depth on session apps. Rotate token per session; validate on state-changing methods not GET.

**Q:** OAuth PKCE for SPA?
**A:** Public SPA cannot hold client secret—authorization code flow with PKCE (`S256` challenge) prevents stolen code replay. Spring Authorization Server and Okta/Keycloak support `code_challenge` parameters. BFF pattern avoids exposing tokens in browser—preferred over pure SPA calling token endpoint. Never implicit flow—deprecated insecure. Refresh token rotation with short access TTL limits exposure. CORS on token endpoint locked to SPA origin. I test PKCE negative case: token exchange without verifier must fail 400.

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
**A:** ESO syncs secrets from AWS Secrets Manager/Vault/GCP into K8s `Secret` objects on schedule—GitOps friendly, no secrets in git. Boot mounts as env vars or `spring.config.import=kubernetes:`. Rotation: ESO updates Secret; pod restart or `spring-cloud-kubernetes` reload for hot refresh. Compare to Sealed Secrets (encrypted in git) vs ESO (runtime pull). I use ESO for DB passwords and Kafka certs; ConfigMap for non-secret config. Audit RBAC who can read Secret; restrict ESO service account.

**Q:** `@RefreshScope` pitfalls?
**A:** Cloud `@RefreshScope` creates proxy reloading beans on `/actuator/refresh`—breaks singleton assumptions, drops in-flight state, problematic for DataSource pools mid-traffic. Beans with connections need dispose/recreate carefully—Hikari leak if wrong. Prefer K8s rolling restart on ConfigMap change over live refresh for prod. Refresh race: half pods old config half new during rollout anyway. I avoid `@RefreshScope` on Kafka listeners and schedulers—duplicate consumers. Use for feature flags only with acceptance of brief inconsistency or combine with traffic drain.

**Q:** Config vs secret rotation without downtime?
**A:** ConfigMap change → rolling restart pods (Helm upgrade) with `maxUnavailable=0`—readiness gates new config. Secrets: ESO updates → trigger rolling restart via Reloader annotation `secret.reloader.stakater.com/reload`. Dual-sign JWT keys: auth server publishes JWKS with two keys, retire old after TTL exceeds max token life. DB password: create second user, rolling deploy switch datasource, revoke old. Never single-step password swap without two-phase. Kafka certs: truststore with both CAs during migration. Document runbook timing vs token TTL.

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
**A:** POST `/orders` accepts `Idempotency-Key` header—unique constraint on `(tenantId, key)` returns 200 with same body on replay. Service TX: insert order + insert outbox event `OrderCreated` same commit. Poller reads outbox, publishes Kafka, marks sent. Payment call outside TX with idempotent PSP key. Status machine: PENDING→CONFIRMED→SHIPPED with optimistic lock. K8s HPA on consumer lag. Readiness after Flyway. Trace id in MDC. Failure: PSP timeout leaves PENDING—reconciler job queries PSP. No `@Transactional` on controller; no OSIV.

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
**A:** Circuit breaker OPEN→HALF_OPEN allows limited probes (`permittedNumberOfCallsInHalfOpenState`). If all pods probe simultaneously when wait duration expires, recovering dependency gets thundering herd—reopens circuit. Stagger with jitter on `waitDurationInOpenState` per instance or use random backoff in Resilience4j. Monitor half-open call rate. Synthetic canary from one pod before full traffic. I tune fraud API breaker: 3 half-open calls per pod max. Alert on flapping OPEN/HALF_OPEN state changes—indicates threshold too aggressive.

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
**A:** springdoc `@Hidden` on internal controllers; `GroupedOpenApi` exposes only `/api/public/**`. Network policy blocks `/internal/**` from ingress—defense in depth. Actuator on management port not in public DNS. Admin routes separate Spring Security chain with IP allowlist. OpenAPI publish subset artifact to partners—full spec internal only. Pen test verifies scanner cannot reach actuator from internet. `@Profile("!prod")` on dev-only controllers. API gateway path-based routing strips internal paths from edge.

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
**A:** `@Order(Ordered.HIGHEST_PRECEDENCE)` on specific advice handling `ValidationException`; generic `Exception` handler `@Order(LOWEST_PRECEDENCE)`. More specific exception types in higher-precedence beans. `@RestControllerAdvice(basePackageClasses=ApiV2.class)` scopes advice. Security `AccessDeniedException` handler in security-advice before generic. Conflicts: two handlers for same exception—unpredictable without order. Integration test throws each exception type asserts correct status/body. Document advice beans in module graph—six advices caused wrong ProblemDetail schema until ordered.

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
**A:** `@Timed` (Micrometer) records timer metric only—legacy. `@Observed` uses Observation API—unified metrics + distributed tracing span with one annotation. Boot 3.2+ prefers `@Observed` on service boundaries; links to OpenTelemetry exporter. Migrate gradually; both coexist. `@Timed` lacks contextual span name in traces. Custom `ObservationRegistry` filters add low-cardinality tags. Test with `TestObservationRegistry` assert. Do not annotate every private method—SLO on user-facing operations only.

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
**A:** H2/HSQL embedded: fast, no Docker, wrong dialect—JSONB, Postgres locks, and sequence behavior differ. Testcontainers Postgres: 3-5s startup, faithful SQL, `@ServiceConnection` wiring. I use H2 only for pure JPA unit tests without native SQL; Testcontainers for repository integration in CI. Embedded Kafka exists but flaky—Testcontainers Kafka or `@EmbeddedKafka` limited. Cost: CI Docker required. Reuse locally; fresh in CI. Embedded wins speed for TDD loop; Testcontainers wins release confidence—run both tiers in pyramid.

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

### 63. Spring Core IoC and Dependency Injection — `ApplicationContext`, `@Component` vs `@Bean`, when to use each

**Short answer:** The IoC container (`ApplicationContext`) owns bean lifecycle: it reads definitions, resolves dependencies, applies post-processors, and injects collaborators. `@Component` (and stereotypes) registers classes discovered by component scan; `@Bean` methods on `@Configuration` register objects you construct manually. Use scan for your domain services; use `@Bean` for third-party types, conditional wiring, and multi-step factory logic. Mixing both without clear module boundaries creates duplicate beans and brittle tests.

#### What it is
Inversion of Control means objects don't `new` their dependencies — the container wires them. `ApplicationContext` is the production-facing IoC container: it extends `BeanFactory` with event publishing, resource loading, and environment abstraction. Dependency injection is how collaborators arrive — constructor injection is the default and the only style I recommend for required dependencies.

#### How it works (internals)
On refresh, Spring registers `BeanDefinition`s from component scanning, `@Import`, and `@Bean` methods. `AutowiredAnnotationBeanPostProcessor` resolves `@Autowired`/`@Qualifier` on constructors. `@Configuration` classes are CGLIB-proxied so `@Bean` method calls return singletons from the context, not new instances. `ApplicationContext` publishes lifecycle events (`ContextRefreshedEvent`, `ContextClosedEvent`) and shuts down disposable beans on stop. Boot's `SpringApplication` chooses `AnnotationConfigServletWebServerApplicationContext` for servlet apps.

#### When to use / when NOT to use
`@Component` on your own `@Service`, `@Repository`, `@Controller` classes in scanned packages — standard. `@Bean` when you wrap a `RestClient`, `ObjectMapper`, `SecurityFilterChain`, or vendor client you don't control. Don't `@Component` library classes you don't own. Don't put business logic in `@Configuration` — keep config classes thin.

#### Production example
Payments module: `PaymentService` is `@Service` (scanned). `StripeClient` comes from a `@Bean` method that reads API keys from `@ConfigurationProperties` and builds an HTTP client with timeouts. Integration tests replace the `@Bean` with a `@TestConfiguration` stub without touching production scan paths. On-call never hunts "why are there two `ObjectMapper` beans" because only one module owns Jackson wiring.

#### Common mistakes
- Scanning too wide (`com` root) and pulling accidental `@Component`s from libraries.
- Calling `@Bean` methods from regular classes — bypasses singleton semantics.
- Field injection in services — hard to test and hides required dependencies.
- Expecting `@Component` on a class outside the scan root to magically appear.

#### Interview follow-ups (with model answers)

**Q:** What is the difference between `BeanFactory` and `ApplicationContext`?
**A:** `BeanFactory` is the low-level registry: getBean, scopes, post-processors. `ApplicationContext` adds enterprise features — internationalization, event propagation, automatic `BeanPostProcessor` registration, and graceful shutdown hooks. In Boot you almost never touch `BeanFactory` directly; you autowire from the context. When debugging "bean exists in debugger but `@Autowired` fails," check you're in the same context (parent/child contexts in some legacy setups) and that the bean name/type actually matches the injection point.

**Q:** Why prefer constructor injection over `@Autowired` fields?
**A:** Constructor injection makes dependencies explicit and immutable — the object is unusable without them, which is what you want for required collaborators. Fields can be null if someone `new`s the class outside Spring or forgets `@Autowired` on a test. Constructor injection also plays cleanly with `@RequiredArgsConstructor` and records. I still use `@Autowired` on optional `@Bean` method parameters in `@Configuration` classes where it reads naturally, but service layer stays constructor-only.

**Q:** Can you have `@Component` and `@Bean` for the same type?
**A:** Yes, and that's how you get `NoUniqueBeanDefinitionException` at startup or the wrong implementation at runtime. Example: auto-config registers a `RestClient.Builder` bean and your `@Configuration` also defines one without `@ConditionalOnMissingBean`. Fix by excluding auto-config, marking yours `@Primary`, or injecting `@Qualifier("customRestClient")`. In code review I ask: "who owns this bean?" — one owner per type per context unless the duplicate is intentional and documented.

#### Scenario probe
**Situation:** Multi-module monolith: `billing-api` and `billing-impl` both define `@Bean ObjectMapper`. Checkout service gets non-deterministic JSON (snake_case vs camelCase) depending on which module's bean wins `@Primary`.

**Model answer:** Two `ObjectMapper` beans with no `@Qualifier` on injection points — Spring picks `@Primary` if exactly one exists; otherwise fails or picks by name if `@Autowired` field name matches. I'd consolidate Jackson config in one `observability-config` module, expose a single `@Bean`, and delete the duplicate. Add an `@SpringBootTest` that asserts `ObjectMapper` property naming strategy. Short-term: `@Qualifier("apiObjectMapper")` on the REST layer only. Long-term: enforce ArchUnit rule — only one `ObjectMapper` bean definition in the application context.

#### Code / config (when useful)

```java
@Configuration
class HttpClientsConfig {
    @Bean
    RestClient paymentsRestClient(RestClient.Builder builder, PaymentsProps props) {
        return builder.baseUrl(props.baseUrl()).build();
    }
}

@Service
class PaymentService {
    private final PaymentRepo repo;
    private final RestClient paymentsClient;

    PaymentService(PaymentRepo repo, @Qualifier("paymentsRestClient") RestClient paymentsClient) {
        this.repo = repo;
        this.paymentsClient = paymentsClient;
    }
}
```

---

### 64. `@Primary`, `@Qualifier`, and `NoUniqueBeanDefinitionException` — resolution order

**Short answer:** When multiple beans match an injection type, Spring fails with `NoUniqueBeanDefinitionException` unless you disambiguate. Resolution order: `@Qualifier` on the injection point (or parameter name if `@Autowired` and `-parameters` compiler flag), then `@Primary` if exactly one primary exists, then fall back to bean name matching the field/parameter name. Multiple `@Primary` beans of the same type still fail. Design explicit qualifiers for parallel implementations — "primary" is a last resort, not architecture.

#### What it is
Spring's type-based injection assumes one bean per type unless you annotate alternatives. `@Primary` marks the default when several candidates exist. `@Qualifier` (or custom qualifier annotations meta-annotated with `@Qualifier`) pins a specific bean. `NoUniqueBeanDefinitionException` is the guardrail — treat it as a design smell, not an inconvenience to `@Primary` away.

#### How it works (internals)
`DefaultListableBeanFactory` collects candidate beans for the required type, filters by qualifier metadata, then applies `Primary` precedence rules. `@Autowired` on constructor records uses parameter names as implicit qualifiers when compiled with `-parameters`. Custom stereotypes like `@CacheRedis` + `@Qualifier("redis")` improve readability over string literals. In tests, `@MockBean` replaces by type; multiple mocks of same type need `@Qualifier` on the production injection point.

#### When to use / when NOT to use
Use `@Qualifier` when you intentionally run two implementations (S3 vs local file storage, Kafka vs in-memory bus). Use `@Primary` for the production default when a test/mock bean also exists — common pattern: `@MockBean` in slice tests without touching prod code. Avoid `@Primary` on two production beans of the same type — future devs will add a third and break silently if someone adds another `@Primary`.

#### Production example
Notification service injects `MessageSender` — production `@Primary` bean is `SqsMessageSender`; `dev` profile registers `@Qualifier("console") ConsoleMessageSender` and controllers in dev use `@Qualifier` explicitly. Staging uses `@Primary` SQS with a sandbox queue URL from properties. Integration tests `@Import` a `@TestConfiguration` with `@Bean @Qualifier("fake")` and inject that qualifier in the class under test — no global `@Primary` fight.

#### Common mistakes
- Slapping `@Primary` on every duplicate instead of naming qualifiers.
- Two `@Primary` beans after a merge — startup failure in CI only.
- Relying on `@Order` to pick beans — order does not resolve injection ambiguity.
- Forgetting `@Qualifier` on `@Bean` method return when multiple beans share an interface.

#### Interview follow-ups (with model answers)

**Q:** What happens with `@Autowired List<PaymentGateway>`?
**A:** Spring injects all beans assignable to `PaymentGateway` — no `NoUniqueBeanDefinitionException` because the dependency is a collection, not a single bean. Useful for strategy chains (run all fraud checks). Order is `@Order` on beans or `Ordered` interface unless you sort explicitly. Watch for accidentally including a `@Profile("test")` bean in prod if profiles misconfigured. For optional single choice among many, prefer explicit `@Qualifier` or a factory that selects by property.

**Q:** How do custom qualifier annotations help?
**A:** Meta-annotate `@interface AwsQueue` with `@Qualifier("aws")` — injection points use `@AwsQueue MessageSender sender` instead of magic strings that typo at runtime. Refactoring renames stay compile-safe. Teams publish qualifier annotations in the API module alongside the interface. Same pattern for `@ReadOnly DataSource` vs `@Write DataSource` in CQRS layouts — clearer than two `@Qualifier` strings in every repository.

**Q:** How does `@MockBean` interact with `@Primary` production beans?
**A:** `@MockBean` registers a mock in the test context and replaces the existing bean definition for that type (or named bean if specified). Your production `@Primary` is irrelevant — the mock wins in the test slice. If you have two real beans and only mock one, you may still need `@Qualifier` on the subject under test. For multiple beans of same type, use `@MockBean(name = "sqsSender")` matching the `@Bean` method name. Verify with `@Autowired ApplicationContext` and `getBeanNamesForType` when tests behave oddly.

#### Scenario probe
**Situation:** After adding a caching wrapper, `CacheableUserService` and `UserService` both implement `UserService` interface. Login endpoint fails at startup with `NoUniqueBeanDefinitionException`.

**Model answer:** Decorator pattern registered both concrete and interface beans as injectable types. Options: inject concrete `UserServiceImpl` only internally; make the cache wrapper `@Primary` and the delegate `@Qualifier("delegate")`; or don't expose the inner bean as a top-level `@Service` — use `@Bean` method that returns the decorated instance as the sole `UserService`. I prefer one `@Bean UserService userService(Delegate d, CacheManager c)` composing the stack — only one bean of type `UserService` in the context. Add startup test asserting single bean count for `UserService.class`.

#### Code / config (when useful)

```java
@Primary
@Service
class S3StorageClient implements StorageClient { /* ... */ }

@Service
@Qualifier("local")
class LocalStorageClient implements StorageClient { /* ... */ }

@Service
class ArchiveService {
    ArchiveService(@Qualifier("local") StorageClient storage) { /* dev path */ }
}
```

---

### 65. Maven dependency management for Spring Boot — BOM, starters, dependency convergence

**Short answer:** Import `spring-boot-dependencies` BOM in `dependencyManagement` so every Spring artifact shares one tested version line. Starters are curated dependency bundles — `spring-boot-starter-web` pulls Tomcat, Jackson, Spring MVC without listing versions. Dependency convergence means one version of Netty, Jackson, and SLF4J on the runtime classpath; Maven Enforcer or `mvn dependency:tree` catches conflicts Boot's BOM already resolved. Seniors own the BOM version — bumping Boot without aligning plugins (`spring-boot-maven-plugin`, compiler release) causes subtle breakage.

#### What it is
Maven BOM (Bill of Materials) is a POM that only lists `dependencyManagement` entries — versions without pulling jars. Spring Boot's parent POM or imported BOM pins compatible sets. Starters are not frameworks themselves; they're opinionated dependency aggregates plus auto-configuration entry points.

#### How it works (internals)
Your app POM declares `spring-boot-starter-data-jpa` without version — BOM supplies it. Transitive dependencies inherit managed versions unless you override explicitly. `spring-boot-starter-parent` also sets plugin versions, Java release, resource filtering, and surefire defaults. Multi-module builds import BOM once in parent `dependencyManagement`; children declare starters only. `mvn dependency:tree -Dverbose` shows omitted conflicts — Boot's dependency management already chose winners for known clashes.

#### When to use / when NOT to use
Always align internal microservices on the same Boot BOM minor line for shared libraries. Override a managed version only with a documented CVE fix and regression tests — e.g., forced `netty` patch. Don't copy-paste version numbers on every `org.springframework` artifact — you will drift. Don't import two BOMs that manage the same artifacts (Spring Boot + Spring Cloud BOM is coordinated via Spring Cloud release train — use compatible matrix).

#### Production example
Platform team publishes `company-parent:4.0.1` importing `spring-boot-dependencies:4.0.1` and `spring-cloud-dependencies:2025.0.0`. Services inherit parent; security patch bumps parent patch version once, forty services rebuild. CI runs `dependency:analyze` and OWASP dependency-check against the resolved tree. Incident: rogue `jackson-databind` 2.14 pulled by old SDK — enforcer rule fails build until SDK upgraded or excluded with approval.

#### Common mistakes
- Declaring `spring-boot-starter-web` and manually adding conflicting `spring-webmvc` version.
- Missing `spring-boot-maven-plugin` repackage goal — deploy thin jar missing dependencies.
- Using `spring-boot-starter-parent` in library modules — libraries should import BOM only, not inherit plugin config meant for apps.
- Ignoring `dependency:tree` after adding a fat client SDK — brings duplicate logging bindings.

#### Interview follow-ups (with model answers)

**Q:** Parent POM vs BOM import — when which?
**A:** `spring-boot-starter-parent` is convenient for single deployable apps — plugin management, test defaults, property placeholders like `${spring-boot.version}`. Corporate setups often use `spring-boot-dependencies` BOM import in company parent so library modules aren't forced to inherit repackage plugin config. Libraries import BOM for versions only; executable modules add `spring-boot-maven-plugin`. I choose parent for greenfield microservice repos; BOM import for monorepo with ten non-Boot library jars plus two Boot apps.

**Q:** How do you diagnose `NoClassDefFoundError` after a Boot upgrade?
**A:** Compare `dependency:tree` before and after on the failing module — look for evicted or downgraded artifacts. Check release notes for removed modules (javax→jakarta migrations already burned teams once). Run `mvn -q dependency:build-classpath` and inspect duplicate jars. Common culprits: mixing Boot 3 and Boot 4 starters, old `spring-security-test`, or shading that strips `META-INF/spring` auto-config files. Fix by aligning BOM, not random `+` version bumps on one coordinate.

**Q:** What is dependency convergence and how do you enforce it?
**A:** Convergence means every transitive path resolves to the same version for a given artifact — Maven picks nearest-wins by default, which may not be Boot's tested combo. `maven-enforcer-plugin` `dependencyConvergence` rule fails the build on conflicts. Spring Boot's BOM already converges the Spring ecosystem; your job is third-party SDKs. In Gradle terms it's `platform('org.springframework.boot:spring-boot-dependencies')` — same idea. Document any intentional overrides in `dependencyManagement` with comment linking CVE ticket.

#### Scenario probe
**Situation:** Service passes CI but fails in prod with `LoggerFactory is not a Logback LoggerContext` — works locally in IDE.

**Model answer:** Classpath has both `logback-classic` and `slf4j-simple` or old `log4j-over-slf4j` bridge from a new vendor jar. Local IDE module path differed from fat jar order. Run `mvn dependency:tree | grep slf4j` and exclude transitive `slf4j-simple` from the SDK. Boot's `spring-boot-starter-logging` expects Logback — don't swap without excluding defaults. Add enforcer ban on `slf4j-log4j12`. Rebuild layered jar and verify with `java -jar` locally before promote — IDE classpath lies.

#### Code / config (when useful)

```xml
<parent>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-starter-parent</artifactId>
  <version>4.0.1</version>
</parent>
<dependencies>
  <dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
  </dependency>
</dependencies>
```

---

### 66. Spring AOP deep dive — `@Aspect`, `@Around`/`@Before`/`@AfterReturning`, pointcut expressions, self-invocation bypass

**Short answer:** Spring AOP wraps beans in JDK or CGLIB proxies to run cross-cutting advice — transactions, security, metrics, logging. `@Aspect` classes define pointcuts (`execution`, `@annotation`, `within`) and advice types: `@Before`/`@AfterReturning` for side hooks, `@Around` for full control including proceeding or short-circuiting. Proxies apply only to external calls through the Spring bean — `this.internal()` self-invocation skips advice, same failure mode as `@Transactional`. Prefer `@Around` sparingly — it's powerful but easy to swallow exceptions or forget `proceed()`.

#### What it is
Aspect-Oriented Programming separates concerns that cut across layers (logging every service method, auditing writes). Spring AOP is proxy-based, not compile-time AspectJ weaving by default — only public methods on Spring-managed beans are advised unless you use `aspectj-maven-plugin` load-time weaving.

#### How it works (internals)
`@EnableAspectJAutoProxy` (auto in Boot) registers `AnnotationAwareAspectJAutoProxyCreator` as a `BeanPostProcessor`. Matching advices wrap the target in a proxy. JDK proxy if interface-based; CGLIB subclass if concrete class. Pointcut expressions filter methods — `execution(* com.acme..service.*.*(..))` is common but broad. `@annotation(com.acme.Logged)` is safer. Order of multiple aspects: `@Order` on aspect class — lower runs first for `@Before`, reverse for `@After`.

#### When to use / when NOT to use
Use for observability (`@Observed` is built on this), authorization annotations, retry wrappers, and audit trails. Don't AOP-map every line of business logic — debugging through opaque proxies frustrates teams. Don't rely on AOP for transaction boundaries without understanding proxy limits — extract a collaborator if self-invocation is required.

#### Production example
`@Aspect` `@Around("@annotation(Audited)")` records who changed loan status — runs on `LoanService.approve()` called from controller, not when `approve()` calls internal `validate()` on `this`. Team fixed audit gap by moving validation to a separate `@Component` or calling self through injected proxy (`@Lazy LoanService self`). Latency added ~200µs per call — acceptable vs manual audit in every method.

#### Common mistakes
- Pointcut too broad — accidentally advises repositories and doubles SQL logging.
- `@Around` not calling `joinPoint.proceed()` — silent no-op methods.
- Swallowing exceptions in aspect — breaks transaction rollback.
- Expecting `final` methods or private methods to be advised with standard Spring AOP — they aren't.

#### Interview follow-ups (with model answers)

**Q:** JDK proxy vs CGLIB — how does Spring choose?
**A:** If the bean implements an interface and you inject the interface type, JDK dynamic proxy is typical. Concrete class injection without interface forces CGLIB subclass — needs non-final class and non-final methods. CGLIB can't advise `final` methods; JDK can't proxy classes without interfaces. In Boot 3+, most services are concrete classes — CGLIB is common. `spring.aop.proxy-target-class=true` forces CGLIB globally. Misunderstanding this causes "advice works in unit test with subclass but not in prod injection" when test manually subclasses but prod uses interface proxy.

**Q:** How do you test aspects without starting full MVC?
**A:** `@SpringBootTest` with a minimal `@Configuration` importing your `@Aspect` and `@EnableAspectJAutoProxy`, plus a dummy `@Service` with the target annotation. Or use AspectJ compile-time weaving in isolated module — heavier. Assert side effects: mock `AuditRepository` injected into aspect, invoke service through Spring context (not `new`), verify insert called. Direct `new Service()` bypasses proxy — common test bug.

**Q:** What's the fix for self-invocation bypassing `@Transactional` or `@Cacheable`?
**A:** Same as transactions: inject self `@Lazy MyService self` and call `self.cachedMethod()`, extract logic to another bean (`PaymentValidator`), or switch to AspectJ LTW if you truly need in-class calls advised — rare. I push for separate bean — clearest in code review. Document in team guide: "no `this.` calls for advised methods." ArchUnit can flag internal calls if you're strict.

#### Scenario probe
**Situation:** Performance `@Around` on `com.acme..*Service.*` adds timing logs. P99 spikes but logs show service methods fast — DB still slow.

**Model answer:** Aspect measures proxy entry/exit only — doesn't see time inside downstream JDBC unless you also advise repository layer or use tracing. Broad pointcut accidentally matched `*Service` in integration package wrapping HTTP clients — double-counting. Narrow to `@annotation(Timed)` on business methods. Replace log-per-request aspect with Micrometer `@Observed` and distributed tracing for cross-layer timing. If aspect runs `@Before` security check that hits DB on every call, that's the real regression — review advice body, not just pointcut.

#### Code / config (when useful)

```java
@Aspect
@Component
@Order(1)
class PerformanceLoggingAspect {
    private static final Logger log = LoggerFactory.getLogger(PerformanceLoggingAspect.class);

    @Around("@annotation(Timed)")
    Object logTiming(ProceedingJoinPoint pjp, Timed timed) throws Throwable {
        long start = System.nanoTime();
        try {
            return pjp.proceed();
        } finally {
            long ms = (System.nanoTime() - start) / 1_000_000;
            log.info("method={} tookMs={}", timed.value(), ms);
        }
    }
}
```

---

### 67. Logback configuration in Spring Boot — `logback-spring.xml`, structured JSON logging, MDC, correlation IDs

**Short answer:** Boot defaults to Logback via `spring-boot-starter-logging`. Use `logback-spring.xml` (not plain `logback.xml`) so Spring can expand `springProperty` and respect profiles. Structured JSON logs (Logstash encoder or Logback 1.5+ JSON layout) feed ELK/Datadog parsers. MDC (`Mapped Diagnostic Context`) carries per-request keys like `traceId` and `userId` on the logging thread — propagate via filter or observability bridge. Correlation IDs must enter MDC at the edge and copy to async threads manually or via `TaskDecorator`.

#### What it is
Logging in Boot is SLF4J API over Logback implementation unless you exclude and swap (not recommended without ops buy-in). `logback-spring.xml` integrates with Spring's logging system initialization order. MDC is a thread-local map included in log patterns or JSON output.

#### How it works (internals)
`LoggingApplicationListener` sets up log levels from `application.yml` before context refresh. `logback-spring.xml` supports `<springProfile name="prod">` blocks. JSON appenders emit one object per line — stack traces as nested fields. Servlet `Filter` reads `X-Request-Id` or generates UUID, `MDC.put("correlationId", id)`, `MDC.clear()` in finally. Micrometer Tracing (Boot 3.2+) bridges trace/span ids into MDC automatically when configured. Async `@Async` loses MDC unless `TaskDecorator` copies context.

#### When to use / when NOT to use
JSON logs in centralized observability stacks — yes. Plain text in local dev — readability wins. MDC for correlation — always at HTTP/Kafka boundaries. Don't put high-cardinality data (full JWT, email) in MDC — it lands in indexes and may violate privacy. Profile-specific appenders: console pretty in `dev`, JSON file or stdout in `prod`.

#### Production example
API gateway sends `traceparent`; Boot filter maps to MDC `traceId`. JSON logs ship to OpenSearch — on-call searches `traceId:abc` across twelve services. Payment failure investigation links user complaint to exact pod logs without grep across plain-text formats. Async notification worker uses `TaskDecorator` copying MDC — without it, email job logs showed blank correlation id and slowed incident response.

#### Common mistakes
- Using `logback.xml` — Spring profile extensions ignored; properties not resolved early.
- Forgetting `MDC.clear()` in filter — thread pool reuse leaks ids across requests.
- Logging PII into structured fields indexed forever.
- `%X{correlationId}` in pattern but never populated — false confidence.

#### Interview follow-ups (with model answers)

**Q:** `logback.xml` vs `logback-spring.xml`?
**A:** Plain `logback.xml` loads too early — Spring Boot can't use `<springProperty>` or `<springProfile>` reliably. `logback-spring.xml` is picked up by Boot's logging initialization with Spring extensions enabled. If you must use `logback.xml`, you lose profile-conditional appenders unless you duplicate files. I only ship `logback-spring.xml` in templates. `logging.config` property can point to external file mounted in K8s for ops-owned tweaks without rebuild.

**Q:** How do correlation IDs propagate to `@Async` and `@Scheduled` jobs?
**A:** HTTP filter sets MDC on request thread. `@Async` runs on `TaskExecutor` worker — MDC empty unless you register `TaskDecorator` that copies `MDC.getCopyOfContextMap()` before run and restores/clears after. Same for reactive WebFlux — use Reactor `Context` propagation hooks, not thread MDC alone. Scheduled jobs aren't request-scoped — generate a batch correlation id at job start. Kafka consumers: read header `correlationId` in listener and set MDC at entry.

**Q:** How do you tune log levels per package in prod without restart?
**A:** Boot Actuator `loggers` endpoint can change levels at runtime if exposed securely — `POST /actuator/loggers/com.acme.payments` with `{"configuredLevel":"DEBUG"}` temporarily. Permanent config lives in `application-prod.yml` under `logging.level.*`. Prefer brief debug on specific package during incident, then revert via GitOps. Never leave `org.hibernate.SQL: DEBUG` globally in prod — volume and PII risk. Spring Boot 4 continues externalized logging config — verify actuator exposure after upgrades.

#### Scenario probe
**Situation:** ELK shows duplicate log lines with swapped correlation IDs under load — support tickets match wrong customer sessions.

**Model answer:** Classic thread-pool MDC leak: filter sets MDC but tomcat worker thread returned to pool without `clear()`, next request inherits previous id. Fix filter `finally { MDC.clear(); }`. Also check async paths missing decorator. Reproduce with JMeter concurrent requests asserting unique ids in log file grep. Add integration test spinning two parallel MockMvc calls with different headers, parse captured logs. Post-incident: lint rule in PR template — any `MDC.put` must have paired clear in same filter/job scope.

#### Code / config (when useful)

```xml
<!-- src/main/resources/logback-spring.xml -->
<configuration>
  <springProperty name="APP_NAME" source="spring.application.name"/>
  <appender name="JSON" class="ch.qos.logback.core.ConsoleAppender">
    <encoder class="net.logstash.logback.encoder.LogstashEncoder">
      <customFields>{"service":"${APP_NAME}"}</customFields>
    </encoder>
  </appender>
  <springProfile name="prod">
    <root level="INFO"><appender-ref ref="JSON"/></root>
  </springProfile>
</configuration>
```

```java
@Component
class CorrelationIdFilter extends OncePerRequestFilter {
    @Override
    protected void doFilterInternal(HttpServletRequest req, HttpServletResponse res, FilterChain chain)
            throws ServletException, IOException {
        String id = Optional.ofNullable(req.getHeader("X-Request-Id")).orElse(UUID.randomUUID().toString());
        MDC.put("correlationId", id);
        res.setHeader("X-Request-Id", id);
        try { chain.doFilter(req, res); } finally { MDC.clear(); }
    }
}
```

---

### 68. MapStruct vs ModelMapper vs manual DTO mapping — performance and correctness

**Short answer:** MapStruct generates compile-time mapper implementations — fast, type-safe, refactor-friendly, best default for entity↔DTO in Spring services. ModelMapper uses reflection at runtime — flexible for prototypes but slower, failures surface at runtime not compile time. Manual mapping is verbose but explicit — good for small graphs or when mapping logic is business rules, not field copy. Seniors pick MapStruct for hot paths and API layers; avoid reflection mappers on high-QPS list endpoints.

#### What it is
DTO mapping translates persistence models to API contracts decoupling JPA entities from JSON shape and lazy-loading traps. MapStruct is an annotation processor (`@Mapper`) emitting `OrderMapperImpl` at compile time. ModelMapper is a library that introspects getters/setters. Manual mapping means hand-written conversion methods or constructors.

#### How it works (internals)
MapStruct `@Mapping(source="createdAt", target="placedOn")` generates code like your hand-written mapper — no reflection in hot loop. Spring component model: `@Mapper(componentModel = "spring")` makes mappers injectable beans. ModelMapper builds configuration graph at startup, maps by convention — ambiguous fields need explicit `TypeMap`. Manual mapping in service: `new OrderDto(o.getId(), o.getStatus())` — IDE refactoring catches renamed fields if constructor breaks compile.

#### When to use / when NOT to use
MapStruct for REST APIs, Kafka events, batch exports with stable schemas. Manual when mapping encodes rules ("status EXTERNAL maps to customer-visible OPEN"). ModelMapper only for throwaway admin tools or demos — I wouldn't start new prod services on it. Never return JPA entities from controllers — mapping layer is mandatory regardless of tool.

#### Production example
Order search returns 5k rows/sec — switched ModelMapper to MapStruct, CPU on API pods dropped 18%, p99 improved 40ms. Compile failed when `OrderEntity.totalCents` renamed — caught in CI. Nested `CustomerEntity` mapped with `@Mapping(target="customerEmail", source="customer.email")`. Edge case `null` customer handled with `NullValuePropertyMappingStrategy.IGNORE` — explicit policy, not NPE at runtime.

#### Common mistakes
- MapStruct mapper with circular references — stack overflow or infinite loop in generated code.
- Mapping lazy collections triggering N+1 inside mapper if entity not initialized.
- ModelMapper `strict` mode off — silent null mismatches after field rename.
- Sharing one giant mapper interface for entire domain — split by aggregate.

#### Interview follow-ups (with model answers)

**Q:** How does MapStruct handle nested objects and collections?
**A:** Declare helper mapper methods or use `@Mapper(uses = AddressMapper.class)` for composition. Collections map element-wise if element mappers exist — `List<LineDto> map(List<LineEntity> lines)`. For partial updates, `@MappingTarget` on update methods merges into existing entity — useful in PATCH handlers. Custom methods with `@Named` handle enums and money types. Test generated impl via `@SpringBootTest` injecting mapper — no need to mock MapStruct itself if compile succeeded.

**Q:** MapStruct vs Jackson `ObjectMapper.convertValue`?
**A:** Jackson converts bean properties by JSON rules — great for `Map` to POJO, terrible for entity graphs with bidirectional JPA links and lazy proxies. `convertValue` can trigger serialization of Hibernate internals or lazy loads. MapStruct only touches fields you map — no accidental graph walk. For API request DTO to domain command, either is fine; for entity to DTO outbound, MapStruct or explicit factory. Never `objectMapper.convertValue(entity, Map.class)` on managed entities in prod.

**Q:** When is manual mapping worth the boilerplate?
**A:** Ten-field aggregate with three conditional rules — manual `toDto` in record static factory is clearer than ten `@Mapping` expressions. Domain events where mapping is really policy ("if fraudHold, mask customer name") belong in domain code, not generated mapper. Team onboarding: manual is obvious in debugger; MapStruct impl is generated in `target/generated-sources` — juniors must know to open it when debugging wrong field. Hybrid: MapStruct for boring fields, `@AfterMapping` default method for rules.

#### Scenario probe
**Situation:** After Hibernate upgrade, API intermittently returns `{"hibernateLazyInitializer":...}` in JSON for order detail endpoint.

**Model answer:** Controller returned `OrderEntity` directly or MapStruct accessed lazy `customer` outside transaction. Fix: map to `OrderDetailDto` inside `@Transactional` read service with join fetch, or `@Mapping` only scalar fields. OSIV masked bug in dev. Add ArchUnit `noRestControllersDependOnEntities` and contract test asserting JSON has no `hibernate` keys. Long-term: MapStruct DTO layer is non-negotiable boundary.

#### Code / config (when useful)

```java
@Mapper(componentModel = "spring", unmappedTargetPolicy = ReportingPolicy.ERROR)
public interface OrderMapper {
    @Mapping(target = "customerEmail", source = "customer.email")
    OrderSummaryDto toSummary(OrderEntity entity);
}
```

---

### 69. HTTP Service Client (Spring 6.1+) vs RestClient vs WebClient — declarative interface clients

**Short answer:** Spring 6.1+ HTTP Service interfaces (`@HttpExchange`, `@GetExchange`) let you declare REST clients as Java interfaces — Boot auto-configures a proxy implementation from `RestClient` or `WebClient` adapter. `RestClient` is synchronous, fluent, replacement for blocking `RestTemplate` — default for MVC services. `WebClient` is reactive/non-blocking — use with WebFlux or when thread pool exhaustion is the bottleneck. Pick interface clients for internal microservice contracts; imperative `RestClient` for one-off dynamic URLs.

#### What it is
Declarative HTTP clients reduce boilerplate — no manual path building per method. Spring Framework's HTTP interface support is native (not Feign) — integrates with Boot 3.2+ `@ImportHttpServices` / auto-configuration in 3.4+. Under the hood, `HttpServiceProxyFactory` creates JDK proxy translating interface methods to HTTP calls.

#### How it works (internals)
Define `@HttpExchange(url = "/api/users") interface UserClient { @GetExchange("/{id}") UserDto get(@PathVariable String id); }`. Register via `@ImportHttpServices(basePackages="com.acme.clients")` and provide `RestClientAdapter` or `WebClientAdapter`. Boot 4 streamlines builder beans and observation hooks. Error handling: `RestClientResponseException` on 4xx/5xx — map in wrapper or custom factory. Unlike OpenFeign, no annotation processor code generation — runtime proxy only.

#### When to use / when NOT to use
`RestClient` + HTTP interfaces for typical Spring MVC microservices calling few internal REST APIs synchronously. `WebClient` when already on reactive stack or calling slow IO-bound external APIs at high concurrency without growing thread pools. Avoid WebClient in classic JDBC-heavy service "for performance" without end-to-end reactive pipeline — you block somewhere anyway. Feign still valid in Spring Cloud ecosystems — know migration path to native HTTP services reducing dependencies.

#### Production example
Inventory service declares `PricingHttpClient` interface; Boot wires `RestClient` with base URL from config, OAuth2 interceptor from security, and Micrometer observation for trace propagation. Contract tests use MockWebServer asserting paths. Previous Feign client duplicated DTOs and hid timeout config — native interface shares DTO module and explicit `RestClient.Builder` bean with 2s read timeout. Incident root cause: missing retry — added at `RestClient` level with idempotent GET only.

#### Common mistakes
- HTTP interface without base URL bean — fails at runtime with obscure proxy error.
- Mixing WebClient adapter in blocking service and calling `.block()` everywhere — worse than RestClient.
- No timeout on builder — default infinite hang ties up threads.
- Interface method names unrelated to paths — fine, but document for reviewers.

#### Interview follow-ups (with model answers)

**Q:** How does this compare to OpenFeign?
**A:** Feign brings Spring Cloud contract, encoder/decoder plugins, and historical `@FeignClient` ergonomics — extra dependency and another abstraction. Spring HTTP interfaces are framework-native, thinner, align with `RestClient` observability. Migration: replace `@FeignClient` interface with `@HttpExchange`, register import, reuse DTOs. Lose Feign-specific fallbacks — use Resilience4j at call site or wrapper service. For greenfield Boot 4 internal calls, I default native; keep Feign only if platform standardizes it with shared starters.

**Q:** How do you add auth headers and error mapping?
**A:** Configure `RestClient.Builder` with `requestInterceptor` adding Bearer token from `OAuth2AuthorizedClientManager` or static API key from vault. Centralize in `@Configuration` bean consumed by `HttpServiceProxyFactory`. Map 404 to optional empty via status handlers on RestClient — or catch `RestClientResponseException` in facade layer translating to domain exceptions. Don't scatter try/catch per interface method — one error decoder style component.

**Q:** RestClient vs RestTemplate in Boot 4?
**A:** `RestTemplate` is maintenance mode — RestClient is the modern synchronous API with fluent builder, status handlers, and first-class observation. Existing RestTemplate beans still work but new code should use RestClient. Migration is mechanical: `restTemplate.getForObject(url, Dto.class)` → `restClient.get().uri(url).retrieve().body(Dto.class)`. HTTP interfaces sit on top — you rarely call RestClient manually except dynamic URLs.

#### Scenario probe
**Situation:** Checkout service thread pool maxed at 200 threads during flash sale — all blocked on inventory HTTP calls.

**Model answer:** Synchronous `RestClient` per request ties thread to downstream latency. Fixes: reduce timeouts so failures fail fast; bulkhead limiting concurrent inventory calls; cache read-only stock snapshots; or move hot path to async messaging. Switching to WebClient alone without reactive DB doesn't help if service still blocks on `.block()`. Measure: thread dump shows hundreds in `socketRead0`. Right fix: precomputed availability in Redis + event-driven reserve, HTTP call only at confirm. Interface client stays — tuning is resilience and architecture.

#### Code / config (when useful)

```java
@HttpExchange(url = "${inventory.base-url}")
public interface InventoryClient {
    @GetExchange("/api/stock/{sku}")
    StockDto getStock(@PathVariable String sku);
}

@Configuration
class ClientConfig {
    @Bean
    InventoryClient inventoryClient(RestClient.Builder builder,
                                    @Value("${inventory.base-url}") String baseUrl) {
        RestClient client = builder.baseUrl(baseUrl).build();
        return HttpServiceProxyFactory.builderFor(RestClientAdapter.create(client))
                .build().createClient(InventoryClient.class);
    }
}
```

---

### 70. OpenAPI / Swagger with springdoc-openapi — contract-first vs code-first, CI drift gate

**Short answer:** springdoc-openapi generates OpenAPI 3 docs from Spring MVC controllers at runtime (`/v3/api-docs`) and serves Swagger UI. Code-first: annotations (`@Operation`, `@Schema`) on existing controllers — fast, risks doc drift from behavior. Contract-first: author `openapi.yaml`, generate server stubs or validate responses against spec in CI. Seniors gate merges with breaking-change detection (`openapi-diff`) and publish spec as artifact for consumer teams.

#### What it is
OpenAPI describes REST contracts — paths, schemas, security schemes. springdoc replaces older Springfox (incompatible with Boot 3+). It introspects `@RequestMapping`, return types, validation annotations, and security requirements to build the spec.

#### How it works (internals)
`springdoc-openapi-starter-webmvc-ui` on classpath auto-registers `OpenApiResource`. Grouped APIs via `GroupedOpenApi.builder().group("public").pathsToMatch("/api/**")`. Customizers tweak info block and servers. Contract-first: OpenAPI Generator produces interfaces; implement in `@RestController`. CI step: boot app test slice or `springdoc-openapi-maven-plugin` exports static JSON compared to committed `openapi.yaml` — fail on diff.

#### When to use / when NOT to use
Code-first for internal agile teams shipping together. Contract-first when mobile or partner teams consume API before implementation completes, or regulatory audit needs signed spec version. Disable Swagger UI in prod (`springdoc.swagger-ui.enabled=false`) — expose docs via internal portal or CI artifact only. Don't treat generated spec as legal contract without validation tests.

#### Production example
Public payments API: spec in repo `api/payments-v2.yaml`, CI runs breaking change check against main artifact — PR adding required field without version bump fails. Runtime springdoc on staging validates controllers still match committed spec via Schemathesis fuzz tests. Partner onboarding downloads same YAML from S3 versioned bucket — no "works on my Swagger UI" surprises.

#### Common mistakes
- Springfox on Boot 3 — dead end; migrate springdoc.
- Exposing `/swagger-ui.html` on prod internet — reconnaissance and try-it-out CSRF vectors.
- Relying on default schemas hiding `@JsonIgnore` security fields — audit serialized output separately.
- No semver on API — breaking DTO change ships silently.

#### Interview follow-ups (with model answers)

**Q:** How do you document security schemes (JWT, OAuth2)?
**A:** springdoc reads Spring Security filter chains and `@SecurityRequirement` on controllers. Configure `components.securitySchemes` via `OpenAPI` bean customizer with OAuth2 flows matching authorization server. For API keys, document header name consistent with filter. Integration test: `MockMvc` + springdoc endpoint asserts `security` array present on protected paths. Mismatch between doc and actual 401 behavior erodes partner trust — smoke test anonymous call returns 401 on protected route.

**Q:** What is a practical CI drift gate?
**A:** Pipeline job boots app with `@SpringBootTest`, curls `/v3/api-docs`, normalizes JSON, `diff` against `specs/api.json` in repo. Alternatively `openapi-diff` between PR artifact and released version fails on breaking changes (removed endpoint, new required request field). Allow additive changes on same major version per team policy. Store spec in Git — PR that changes controller without spec update is incomplete. Pair with consumer contract tests in client repos.

**Q:** Code-first pain points?
**A:** Generated spec includes internal admin endpoints if scan too broad — use `GroupedOpenApi` packages filter. Return type `ResponseEntity<Object>` loses schema precision — prefer concrete DTO types. Polymorphic types need `@Schema(oneOf=...)`. Hidden query params on record controllers need `@Parameter`. Drift happens when developer changes field name but not `@Schema(description)` — diff gate catches only if spec regenerated in CI; enforce `mvn verify` hook exporting spec.

#### Scenario probe
**Situation:** Mobile team built against Swagger UI; prod returns extra wrapper field and different date format — app crashes parsing.

**Model answer:** Code-first doc showed idealized DTO; actual serialization used `@JsonFormat` globally and `ResponseAdvice` wrapping payloads. Fix: contract tests asserting JSON Schema from exported OpenAPI against sample responses; align `ObjectMapper` config with documented format (ISO-8601 instant). Adopt explicit API version prefix `/v2` and contract-first for mobile boundary. springdoc `spring.jackson` customization documented in spec `format` fields. Postmortem: CI Schemathesis against staging blocking promote.

#### Code / config (when useful)

```yaml
springdoc:
  api-docs.path: /v3/api-docs
  swagger-ui.enabled: false # prod profile
```

---

### 71. JPA Auditing — `@EnableJpaAuditing`, `@CreatedDate`, `@LastModifiedBy`, auditor aware

**Short answer:** Spring Data JPA auditing auto-populates audit fields on persist/update — `@CreatedDate`, `@LastModifiedDate`, `@CreatedBy`, `@LastModifiedBy` on `@Entity` fields driven by `AuditingEntityListener`. Enable with `@EnableJpaAuditing` on a config class. `AuditorAware<T>` supplies current principal for `*By` fields — typically username from `SecurityContext`. Requires knowing who is "current user" in async and batch contexts where SecurityContext is empty.

#### What it is
Audit columns answer compliance questions: who created row, when last changed. Spring Data sets timestamps via `DateTimeProvider` (injectable `Clock` for tests) and user fields via your `AuditorAware` bean.

#### How it works (internals)
`AuditingEntityListener` is JPA entity listener triggered on `@PrePersist`/`@PreUpdate` equivalents through Spring Data machinery. `@CreatedDate` only on insert; `@LastModifiedDate` on insert and update. `AuditorAware.getCurrentAuditor()` returns `Optional` — empty optional leaves `*By` null unless you fail closed. Works with `OffsetDateTime` preferred over legacy `Date`. Combine with `@EntityListeners` carefully — ordering with other listeners matters for custom logic.

#### When to use / when NOT to use
Use on business tables needing SOX/GDPR audit trail. Don't replace domain event sourcing — auditing is row metadata, not full history. For high-write tables, consider DB triggers or append-only audit log if JPA listener overhead or missed async updates are concerns. Disable or override in bulk migration jobs with `AuditorAware` returning `system-migration`.

#### Production example
`LoanApplication` entity has `@CreatedBy` / `@LastModifiedBy` — `SecurityAuditorAware` reads JWT `sub` claim. Support dashboard shows last editor on disputed applications. Batch nightly job uses `@Async` with `DelegatingSecurityContextRunnable` so auditor isn't blank. Test uses `@WithMockUser` and asserts `createdBy` equals `testuser` after repository save.

#### Common mistakes
- Forgot `@EnableJpaAuditing` — fields stay null silently.
- `AuditorAware` returns empty in Kafka listener — all rows `createdBy` null.
- Mutable `Date` fields instead of `Instant`/`OffsetDateTime` — timezone bugs.
- Expecting audit on native query `UPDATE` bypassing entity lifecycle — it won't fire.

#### Interview follow-ups (with model answers)

**Q:** How do you test auditing without security context?
**A:** Provide test `@Configuration` with `AuditorAware<String>` returning `Optional.of("test-auditor")` and fixed `DateTimeProvider` using `Clock.fixed`. `@DataJpaTest` + `@Import(JpaAuditingConfig.class)` save entity, assert fields. For `@WithMockUser`, enable security test slice. Don't rely on production `AuditorAware` hitting empty optional — assert non-null in tests that matter for compliance.

**Q:** AuditorAware in scheduled jobs and system actions?
**A:** SecurityContext empty — return `Optional.of("SYSTEM")` or dedicated service account name from job context MDC. Better: pass initiating user id into job payload when user triggered async work. Document that `LastModifiedBy` during batch is `batch-reconcile` not human — auditors understand if consistent. Avoid impersonating real users incorrectly.

**Q:** `@CreatedDate` with database default `CURRENT_TIMESTAMP`?
**A:** Pick one source of truth — JPA auditing or DB default, not both fighting. I prefer application `OffsetDateTime` with UTC clock for cross-region consistency. DB default useful when non-JPA writers exist — then skip `@CreatedDate` and use `@Column(insertable=false, updatable=false)` read-only mapping of DB default. Mixed writers (JPA + analytics ETL) need aligned semantics or audit columns lie.

#### Scenario probe
**Situation:** Compliance audit finds 40% of `last_modified_by` null on payment adjustments after microservice split.

**Model answer:** New payment service Kafka consumer updates JPA entities without SecurityContext — `AuditorAware` returned empty. Fix: propagate `userId` in event header, set `SecurityContext` in listener interceptor or custom `AuditorAware` reading header from `ThreadLocal` event context. Backfill unknown rows with migration script tagged `UNKNOWN_LEGACY`. Add test: publish event with user header, assert `lastModifiedBy`. Prevention: auditing checklist item for every non-HTTP entry point.

#### Code / config (when useful)

```java
@Entity
@EntityListeners(AuditingEntityListener.class)
class Invoice {
    @CreatedDate private Instant createdAt;
    @LastModifiedBy private String lastModifiedBy;
}

@Configuration
@EnableJpaAuditing(auditorAwareRef = "springSecurityAuditor")
class JpaAuditConfig {}

@Component
class SpringSecurityAuditor implements AuditorAware<String> {
    public Optional<String> getCurrentAuditor() {
        return Optional.ofNullable(SecurityContextHolder.getContext().getAuthentication())
                .filter(Authentication::isAuthenticated)
                .map(Authentication::getName);
    }
}
```

---

### 72. Global validation — `@Valid`, `@Validated`, custom validators, `MethodValidationPostProcessor`

**Short answer:** Bean Validation (Jakarta) on request DTOs via `@Valid` triggers constraint annotations before controller body binding completes. `@Validated` on classes enables method-level validation (`@NotNull` on service parameters) through AOP and `MethodValidationPostProcessor`. Custom constraints (`@Constraint` + `ConstraintValidator`) encode domain rules reusable across layers. Return 400 Problem Details with field errors from `@ControllerAdvice` handling `MethodArgumentNotValidException` — one shape for clients.

#### What it is
Validation separates syntactic input checks (`@Email`, `@Size`) from business invariants (often in domain services). Spring MVC calls `Validator` after data binding; method validation wraps proxied beans for `@Validated` service interfaces.

#### How it works (internals)
`@Valid` on `@RequestBody OrderRequest req` cascades to nested `@Valid` fields. `@Validated` with groups (`@NotNull(groups=Admin.class)`) limits which constraints run per endpoint via `@Validated(Admin.class)` on controller. `MethodValidationPostProcessor` creates proxy advising `@Validated` beans — violations throw `ConstraintViolationException`. Custom validator implements `ConstraintValidator<Annotation, Type>` registered via annotation's `validatedBy`. Boot auto-configures validation when `spring-boot-starter-validation` present.

#### When to use / when NOT to use
DTO validation at edge — always for public APIs. Method validation on service public API when multiple entry points (HTTP, Kafka, scheduler) must enforce same parameter rules. Don't duplicate every rule in controller and entity — DTO for input shape, entity for persistence invariants, domain for cross-field rules. Heavy validation hitting DB belongs in service with transaction, not annotation alone.

#### Production example
`CreateOrderRequest` with `@Valid` nested `AddressDto` and custom `@ValidSku` on line items. Service interface `@Validated` ensures `cancelOrder(@NotBlank String orderId, @Positive long version)` on internal calls too. Global handler maps field errors to RFC 9457 `invalid-params` extension. Pen test found no stack traces — only structured validation messages.

#### Common mistakes
- `@Valid` missing on nested object — child constraints skipped.
- `@Validated` on class without `spring-boot-starter-validation` — silent no-op in some setups.
- Validating JPA entities on persist instead of DTO — leaks persistence into API and causes lazy-load validation.
- Custom validator with injected `@Autowired` repo — must be Spring-managed validator bean (`SpringConstraintValidatorFactory`).

#### Interview follow-ups (with model answers)

**Q:** `@Valid` vs `@Validated`?
**A:** `@Valid` is Jakarta standard for object graph cascade — use on request parameters and fields. `@Validated` is Spring's variant supporting validation groups and required on class for method-level parameter validation. Controller method: `@Valid @RequestBody`. Service class: `@Validated` at type level plus `@NotNull` on method args. They complement — `@Validated` on controller for group selection without replacing `@Valid` on body. Interview trap: only `@Validated` on `@RequestBody` without `@Valid` — constraints may not run.

**Q:** How do custom validators access Spring beans?
**A:** Implement `ConstraintValidator` and inject dependencies via constructor — register validator as Spring bean and use `@Constraint(validatedBy = MyValidator.class)` with `SpringConstraintValidatorFactory` (Boot default). For complex rules (SKU exists in catalog), validator calls read-only repository — keep it side-effect free and fast; don't write DB in validator. Alternative: validate in service after quick syntactic checks — clearer for multi-step rules.

**Q:** How to return consistent validation errors?
**A:** `@RestControllerAdvice` handler for `MethodArgumentNotValidException` builds `ProblemDetail` status 400, iterates `ex.getBindingResult().getFieldErrors()` into list of `{field, message, rejectedValue redacted}`. For `ConstraintViolationException` from method validation, map `ex.getConstraintViolations()` similarly. Log full detail server-side with correlation id; redact PII from client payload. Contract test asserts unknown field typo returns 400 not 500.

#### Scenario probe
**Situation:** API accepts negative transfer amount despite `@Positive` on DTO — fraud attempt succeeds in staging.

**Model answer:** Controller used raw `Map` or wrong DTO type without `@Valid`, or validation group not activated. Fix: `@Valid @RequestBody TransferRequest`, ensure `amount` field has `@Positive`, add MockMvc test posting `-1` expecting 400. If service layer should defend too, add `@Validated` on `TransferService.transfer(@Positive BigDecimal amount)`. Defense in depth: edge validation for UX, domain service for invariants. Alert on validation failure rate spike — can indicate attack fuzzing.

#### Code / config (when useful)

```java
@RestControllerAdvice
class ValidationAdvice {
    @ExceptionHandler(MethodArgumentNotValidException.class)
    ProblemDetail handle(MethodArgumentNotValidException ex) {
        var pd = ProblemDetail.forStatus(BAD_REQUEST);
        pd.setProperty("errors", ex.getBindingResult().getFieldErrors().stream()
                .map(fe -> Map.of("field", fe.getField(), "message", fe.getDefaultMessage()))
                .toList());
        return pd;
    }
}
```

---

### 73. Web scopes — request, session, application scope beans in Spring MVC

**Short answer:** Default Spring bean scope is singleton (one per application context) — safe for stateless services. `request` scope creates one bean instance per HTTP request — good for request-scoped context objects, expensive to misuse for heavy services. `session` scope ties bean lifecycle to HTTP session — rare in stateless JWT APIs; still appears in legacy portals. Application scope (`singleton`) holds shared caches; request/session beans need proxy injection (`@Scope(proxyMode=TARGET_CLASS)`) when injected into singletons.

#### What it is
Scopes define bean lifecycle boundary. Web scopes require active `WebApplicationContext`. Spring creates scoped beans in the web container's request/session storage. Singleton holding direct reference to request-scoped bean without proxy is a lifecycle bug — singleton outlives request.

#### How it works (internals)
`@Scope(WebApplicationContext.SCOPE_REQUEST)` registers `RequestScope` via `RequestContextListener` or `DispatcherServlet`. Injection into singleton uses scoped proxy — each method call fetches current request's instance. Session scope similar with `HttpSession`. Application scope in Spring is really singleton — the name collides with ServletContext `application` scope; in Spring MVC docs "application scope" often means ServletContext-scoped bean (`@Scope("application")` in web context). Prototype scope: new instance every injection — different from request scope.

#### When to use / when NOT to use
Request scope for per-request user context holder (prefer immutable record set in filter over mutable bean). Session scope for shopping cart in server-rendered apps — not for REST JWT services. Default singleton for everything else. In Boot 4 stateless APIs, interview answer: "we don't use session scope; authentication is SecurityContext per request."

#### Production example
Legacy admin portal: `UserPreferencesBean` session-scoped stores UI settings. New REST API refactor replaced with client-side state and JWT claims — removed session beans, horizontal scale without sticky sessions. Remaining request-scoped `TenantContext` populated by filter from header — injected into singleton services via proxy. Load test proved no session affinity required on K8s ingress.

#### Common mistakes
- Session-scoped beans in microservices behind JWT — breaks stateless scaling.
- Forgetting scoped proxy — `NullPointerException` or stale request data.
- Storing large graphs in session — memory leak until timeout.
- Using request scope for DB connections — use transaction instead.

#### Interview follow-ups (with model answers)

**Q:** How does scoped proxy work?
**A:** Spring injects a CGLIB proxy implementing the bean interface. When you call `tenantContext.getTenantId()` on singleton service, proxy delegates to `Scope` registry fetching bean for current `RequestAttributes`. Without `proxyMode=TARGET_CLASS` or `INTERFACES`, singleton captures one request bean at creation — wrong. Debug: log `tenantContext.getClass().getName()` — should end in `$$EnhancerBySpringCGLIB`. Request must be active — calling scoped bean from `@Async` thread without request context fails.

**Q:** Request scope vs `ThreadLocal` tenant holder?
**A:** Both track per-request data. Request-scoped bean is Spring-managed, testable with `RequestContextHolder.setRequestAttributes` mock. ThreadLocal utility class is lighter but manual cleanup risks leaks in thread pools. I use filter + record parameter passing for new code; request-scoped bean when many injection points need same context. Reactive WebFlux: neither thread-bound — use Reactor `Context`. Don't mix ThreadLocal tenant with WebFlux without propagation hooks.

**Q:** Session scope with Spring Security?
**A:** SecurityContext is stored in session by default for form login — stateful. Session-scoped user shopping cart coexists. JWT stateless config sets `SessionCreationPolicy.STATELESS` — no HTTP session created, session scope beans useless. Hybrid apps (JSP + API) sometimes need careful partition — API stateless, MVC session for browser. Sticky sessions or session replication if you must keep session scope in clustered legacy app.

#### Scenario probe
**Situation:** Random users see other tenants' data after load increase post-deploy — only on pod receiving mixed traffic.

**Model answer:** Singleton service field held mutable `TenantContext` request bean without scoped proxy — race under concurrent requests on same pod. Fix `@Scope(value = WebApplicationContext.SCOPE_REQUEST, proxyMode = ScopedProxyMode.TARGET_CLASS)` or pass tenant id as method argument from filter. Immediate mitigation: scale to one thread per pod unrealistic — code fix required. Add concurrent integration test firing two tenants same endpoint asserting isolation. Root cause class: storing request state in singleton fields — forbidden pattern.

#### Code / config (when useful)

```java
@Component
@Scope(value = WebApplicationContext.SCOPE_REQUEST, proxyMode = ScopedProxyMode.TARGET_CLASS)
class RequestTenantContext {
    private String tenantId;
    public void setTenantId(String id) { this.tenantId = id; }
    public String getTenantId() { return tenantId; }
}
```

---

### 74. Spring Boot logging levels per package and profile-specific logback

**Short answer:** Set `logging.level.org.hibernate.SQL=DEBUG` in `application.yml` for quick package tuning without XML. Profile-specific blocks in `logback-spring.xml` switch appenders and formats — console pretty for `dev`, JSON for `prod`. Boot's `LoggingSystem` applies yaml levels over logback defaults at startup; Actuator `loggers` endpoint toggles at runtime if secured. Order matters: `logback-spring.xml` `<logger>` elements and yaml can overlap — know which wins (yaml external config usually adjusts after base logback loads).

#### What it is
Logging configuration spans Boot properties (simple per-package levels) and Logback XML (appenders, encoders, rolling policies). Profiles (`spring.profiles.active`) select beans and logback `<springProfile>` sections together for environment-appropriate observability.

#### How it works (internals)
`logging.level.root=INFO` and `logging.level.com.acme.payments=DEBUG` map to Logback logger levels via `LoggingApplicationListener`. `logback-spring.xml` can define appenders per profile: `<springProfile name="dev"><root><appender-ref ref="CONSOLE"/></root></springProfile>`. `logging.config=classpath:logback-spring.xml` explicit override. File appenders with `rollingPolicy` size/time — ops mount volume for `/var/log/app`. Structured logging profile uses JSON appender reference only in prod profile block.

#### When to use / when NOT to use
Yaml levels for temporary debug during incident — package granular. logback-spring.xml for appenders, third-party library noise filtering, and PII masking layouts. Don't commit `DEBUG` on root in `application-prod.yml`. Don't rely on console logs in K8s without JSON — aggregation parsers break.

#### Production example
`application-prod.yml` sets `logging.level.root=WARN`, `com.acme=INFO`, `org.springframework.web=WARN`. `logback-spring.xml` prod profile ships JSON to stdout for Fluent Bit. `dev` profile enables `CONSOLE` pattern with color and `org.hibernate.orm.jdbc.bind=TRACE` for SQL params locally only. On-call temporarily bumps `com.acme.payments.client` to DEBUG via actuator during provider outage — reverts after.

#### Common mistakes
- DEBUG on `org.springframework` packages in prod — cost and noise.
- logback.xml without spring extensions — can't use `<springProfile>`.
- Assuming yaml changes reload without restart unless using actuator endpoint.
- Duplicate appenders causing double log lines.

#### Interview follow-ups (with model answers)

**Q:** How do yaml logging levels interact with logback-spring.xml?
**A:** Boot loads logback-spring.xml first for appenders and default logger levels, then applies `application.yml` `logging.level.*` via LoggingSystem — typically yaml overrides XML logger levels at runtime init. If something doesn't change, check `logging.config` pointing to external file bypassing Boot property binding. For full control, set levels only in XML OR only in yaml — mixing is fine if team knows precedence. `logging.group.tomcat=org.apache.catalina,...` bundles packages (Boot feature) for ops-friendly toggles.

**Q:** Profile-specific logback example pattern?
**A:** Single `logback-spring.xml` with three `<springProfile>` sections: `dev` console human-readable, `staging` console JSON for pre-prod parser validation, `prod` JSON stdout plus async wrapper appender for throughput. Activate via `SPRING_PROFILES_ACTIVE`. Never ship dev appenders to prod — CI lints `logback-spring.xml` ensuring prod profile exists. Test: `@SpringBootTest` with `@ActiveProfiles("prod")` asserts root logger references JSON appender programmatically if needed.

**Q:** Actuator loggers endpoint risks?
**A:** `POST /actuator/loggers/{name}` changes levels live — powerful for incidents, dangerous if exposed publicly attacker sets `org.springframework.security=TRACE` flooding logs or learns internals. Restrict with separate management port, network policy, and `hasRole('ACTUATOR_ADMIN')`. Audit changes. Some teams disable in prod entirely and use feature-flagged redeploy for debug — trade MTTR for security. Document runbook: who can bump levels and for how long.

#### Scenario probe
**Situation:** Prod log volume tripled after Boot upgrade — bill spike; no code changes in team repo.

**Model answer:** Default logging level or package mapping changed in Boot 4 parent — new auto-config logs INFO where WARN before. Diff `application-prod.yml` and release notes. Run pod with `--debug` once in staging comparing effective levels. Fix: explicit `logging.level.org.springframework.boot.autoconfigure=WARN` and review `logback-spring.xml` root. Add log volume metric alert per service. Regression: compare log bytes per request in canary deployment gate.

#### Code / config (when useful)

```yaml
# application-prod.yml
logging:
  level:
    root: WARN
    com.acme: INFO
    org.hibernate.SQL: WARN
```

---

### 75. AWS Elastic Beanstalk + RDS deployment pattern (contrast with Azure App Service)

**Short answer:** Elastic Beanstalk is AWS PaaS wrapping EC2 (or single container) — upload jar/zip or Docker, EB handles capacity, load balancer, rolling deploy. RDS PostgreSQL sits outside EB environment — bind via env vars `SPRING_DATASOURCE_URL` from EB environment properties or Secrets Manager. Azure App Service is similar PaaS on Windows/Linux plan with deployment slots and VNet integration. Contrast: EB more IaC-friendly with `.ebextensions`; App Service tighter GitHub Actions and Key Vault refs — both need external managed DB, not file-system state.

#### What it is
PaaS deployment for Spring Boot fat JAR without managing Kubernetes. EB `Procfile` or Java platform runs `java -jar`. RDS provides managed relational DB with backups and Multi-AZ. App Service runs jar with `java -jar` startup command or container image on Linux plan.

#### How it works (internals)
EB environment = load balancer + auto scaling group + platform version. Deploy artifact to S3, EB versions roll out with health checks hitting `/actuator/health`. RDS in same VPC security group allowing EB instances ingress 5432. Spring reads `SPRING_DATASOURCE_*` and `SERVER_PORT=5000` (EB nginx proxy). App Service: configure `WEBSITES_PORT`, connection strings in Configuration blade map to env vars. Both: stateless app instances, horizontal scale, sticky sessions optional (avoid for JWT APIs).

#### When to use / when NOT to use
EB/App Service when team lacks K8s ops capacity — faster path for monolith or few services. Move to EKS/AKS when custom networking, service mesh, or multi-tenant density required. RDS always external — never H2 on EB disk for prod. Blue/green: EB immutable updates; App Service deployment slots swap.

#### Production example
Spring Boot 4 monolith on EB Java 21 platform, RDS Postgres 16 Multi-AZ, secrets from AWS Secrets Manager rotated quarterly. Health check `/actuator/health/readiness` includes DB indicator — failed deploy rolls back automatically. Sister product on Azure App Service Premium v3 with VNet integration to Azure Database for PostgreSQL — Key Vault reference for datasource password. EB team likes `.ebextensions/nginx.conf` tweaks; Azure team uses slot swap for zero-downtime.

#### Common mistakes
- Ephemeral local disk treated as persistent — uploads lost on scale-in.
- RDS security group open to `0.0.0.0/0`.
- Missing connection pool sizing for small EB instances — exhaust RDS connections at scale.
- App Service always-on disabled on free tier — cold start SLA miss.

#### Interview follow-ups (with model answers)

**Q:** How do you configure Spring Boot datasource on EB without baking secrets into jar?
**A:** EB environment properties: `SPRING_DATASOURCE_URL`, `USERNAME`, `PASSWORD` from console or IaC (CloudFormation/Terraform). Better: reference Secrets Manager secret JSON keys as env vars via EB config or init script. Never commit `application-prod.yml` with passwords. Rotate secret — EB rolling restart picks new values. Validate with Flyway migrate on startup and readiness only UP after success. IAM role on EC2 instance fetches secret — no static AWS keys in jar.

**Q:** EB vs EKS for Spring Boot microservices?
**A:** EB wins time-to-prod for one or few deployables — platform handles AMI patches on managed updates. EKS wins service density, custom sidecars, and standardized platform team offering for dozens of services. Cost crossover depends on scale — many small services often cheaper on K8s with shared nodes. EB Docker platform still one container per instance typically — not same as K8s pod packing. Hybrid: start EB, extract to EKS when ingress/mesh needs mature.

**Q:** Azure App Service differences that bite Spring devs?
**A:** Deployment slots share App Service plan resources — load test slot before swap. `WEBSITES_ENABLE_APP_SERVICE_STORAGE` false for stateless. Java version pin in `WEBSITE_JAVA_VERSION`. VNet integration required for private PostgreSQL Flexible Server. Unlike EB `.ebextensions`, use startup script or container for custom JVM flags (`-XX:MaxRAMPercentage`). Actuator on management port may need App Service health check path configuration — default `/` insufficient if security blocks.

#### Scenario probe
**Situation:** EB deploy green but users 502 — actuator health UP on instance port, ALB unhealthy.

**Model answer:** Spring listening 8080 but EB nginx expects 5000, or health check path `/` returns 401 due to security while `/actuator/health` open. Fix `SERVER_PORT` and EB load balancer health check URL to `/actuator/health`. Security config must permit health from VPC only. Check target group timeout vs slow startup — increase health check grace during Flyway. Azure parallel: slot swap failed because readiness probed wrong path. Document platform port mapping in runbook — classic PaaS footgun.

#### Code / config (when useful)

```yaml
server:
  port: ${PORT:5000}
spring:
  datasource:
    url: ${SPRING_DATASOURCE_URL}
    username: ${SPRING_DATASOURCE_USERNAME}
    password: ${SPRING_DATASOURCE_PASSWORD}
```

---

### 76. Lombok in Spring projects — what helps vs what hurts (entities, builders, `@Slf4j`)

**Short answer:** Lombok reduces boilerplate — `@Slf4j`, `@RequiredArgsConstructor`, and `@Builder` on immutable commands are productivity wins. On JPA entities, `@Data` hurts: breaks equals/hashCode on generated ids, eager `toString` pulls lazy collections, and `@EqualsAndHashCode` on mutable entities causes subtle Set bugs. Prefer explicit entities or `@Getter/@Setter` only; never `@Data` on `@Entity`. `@Builder` on JPA entities fights no-args constructor requirement — use factory methods or separate command DTOs.

#### What it is
Lombok annotation processor generates bytecode at compile time — constructors, getters, loggers. Spring and JPA rely on reflection for entity instantiation (no-args ctor) and sometimes field access. Lombok interplays with MapStruct and Jackson if accessors exist as expected.

#### How it works (internals)
`@RequiredArgsConstructor` creates constructor for `final` fields — ideal for constructor injection without `@Autowired`. `@Slf4j` adds `private static final Logger log`. `@Data` bundles `@Getter/@Setter/@EqualsAndHashCode/@ToString/@RequiredArgsConstructor` — too much for entities. `@Builder` generates builder pattern — for DTOs/commands great; JPA needs `@AllArgsConstructor` + `@NoArgsConstructor` plus `@Builder` with care (`@Builder.Default` for collections). Delombok in IDE helps debugging generated code.

#### When to use / when NOT to use
Use on services, configuration properties records companions, Kafka events, DTOs. Avoid `@Data`/`@EqualsAndHashCode` on entities; avoid `@Builder` on graph-heavy JPA models. In Boot 4 Java 21+, records replace many immutable DTO Lombok cases. Team standard: Lombok allowed except entity layer uses minimal annotations.

#### Production example
Team banned `@Data` on entities after production incident: `hashCode` on unset `id` broke `Set<OrderLine>` dedup in memory before persist. Services use `@RequiredArgsConstructor` + `@Slf4j` exclusively — code review bot rejects `@Data` on `@Entity`. Command objects use `@Builder` for test ergonomics. MapStruct mappers compile clean with Lombok `@Getter` on entities.

#### Common mistakes
- `@Data` on `@Entity` — Hibernate session issues and bad equals.
- `@Builder` without no-args ctor on entity — JPA startup failure.
- `@Slf4j` on class renamed but log lines copy-pasted with old name — minor.
- Lombok + `@Jacksonized` confusion on immutable types — pick one pattern.

#### Interview follow-ups (with model answers)

**Q:** Safe Lombok pattern for JPA entity?
**A:** `@Getter` `@Setter` on fields or package-private setters; explicit `equals/hashCode` on business key (`uuid` assigned at creation) or don't use entities in Sets. `@NoArgsConstructor(protected)` for JPA. Skip `@ToString` or exclude associations with `@ToString.Exclude` to avoid lazy load in logs. Many teams hand-write entities — clarity over brevity. If using Lombok, static analysis rule: no `@Data` on classes annotated `@Entity`.

**Q:** `@RequiredArgsConstructor` vs `@Autowired` field injection?
**A:** `@RequiredArgsConstructor` on `@Service` generates constructor for final dependencies — Spring 4.3+ single constructor auto-wires without annotation. Immutable, test-friendly, fails fast if dependency missing at compile... actually missing bean still runtime. Cleaner than `@Autowired` fields. For optional dependencies, use explicit constructor with `@Nullable` or `ObjectProvider<T>`. I standardize services on required args constructor pattern company-wide.

**Q:** Lombok and MapStruct/Jackson together?
**A:** Enable `lombok-mapstruct-binding` annotation processor order so MapStruct sees generated getters. Jackson deserializes via constructor/`@JsonProperty` on records or `@Builder` with `@Jacksonized` (Lombok experimental) for immutable JSON types. Mixed Lombok `@Value` DTOs work if getters exist. Debugging: delombok `target/generated-sources/delombok` or IDE plugin shows effective source. Upgrade Lombok version when moving Java 21/23 — processor compatibility matters.

#### Scenario probe
**Situation:** Intermittent `LazyInitializationException` in logs after adding `@ToString` on `OrderEntity` for debugging.

**Model answer:** `@ToString` included `lines` lazy collection — logging entity in service triggered load outside session or infinite recursion. Remove `@ToString` or exclude associations. Lesson: Lombok convenience on JPA types has ORM side effects. Replace debug log with `order.getId()` only. Code review guideline: no entity toString in prod logging. Incident closed after reverting annotation — no code logic bug, tooling footgun.

#### Code / config (when useful)

```java
@Slf4j
@Service
@RequiredArgsConstructor
public class OrderService {
    private final OrderRepo repo;

    public void place(String id) {
        log.info("Placing order {}", id);
        repo.save(new OrderEntity(id));
    }
}
```

---

### 77. `ConditionEvaluationReport` and `@ConditionalOn*` debugging in production

**Short answer:** When a bean is missing or wrong auto-config loaded, `ConditionEvaluationReport` explains which `@ConditionalOn*` expressions matched or failed. Enable via `--debug`, `logging.level.org.springframework.boot.autoconfigure=DEBUG`, or Actuator `/actuator/conditions` (secure it). In production incidents, capture report from staging repro first — enabling full debug in prod is noisy. Seniors read "Negative matches" and "Unconditional classes" sections to find excluded DataSource or Security auto-config.

#### What it is
Boot's condition evaluation logs structured report at startup listing auto-configuration classes and why each applied or backed off. `@ConditionalOnProperty`, `@ConditionalOnClass`, `@ConditionalOnBean`, `@ConditionalOnMissingBean` drive the decision tree.

#### How it works (internals)
`SpringBootCondition` implementations evaluate `ConditionContext` — environment properties, classpath, existing bean definitions. Report grouped into positive matches, negative matches, exclusions. `@AutoConfigureBefore/After` ordering affects final bean set not individual condition truth. `spring.autoconfigure.exclude` property force-disables configs. Custom starters must use precise conditions to avoid activating in wrong apps.

#### When to use / when NOT to use
First tool for "Kafka auto-config didn't run" or "two DataSource beans." Staging repro with `--debug` before prod change. Actuator conditions endpoint for running pod snapshot without restart if enabled. Don't leave `debug=true` globally in prod — log volume and potential sensitive classpath info in logs.

#### Production example
Service missing `MeterRegistry` customizer — report showed `MetricsAutoConfiguration` negative match: `@ConditionalOnClass` missing wrong artifact after refactor. Another incident: `@ConditionalOnProperty(name="feature.x", havingValue="true")` failed because env var `FEATURE_X=true` with relaxed binding mismatch on property key typo. Fixed property key, added test asserting bean present when flag on.

#### Common mistakes
- Assuming bean missing means not scanned — actually auto-config negative match.
- `@ConditionalOnMissingBean` on wrong type — custom bean prevents default silently.
- Copy-paste `@Profile` and `@ConditionalOnProperty` overlapping — neither activates.
- Ignoring report exclusions list in release notes upgrade.

#### Interview follow-ups (with model answers)

**Q:** How to access report without `--debug` flood?
**A:** `logging.level.org.springframework.boot.autoconfigure.logging.ConditionEvaluationReportLoggingListener=DEBUG` narrows output. Actuator `conditions` endpoint returns JSON report if `management.endpoint.conditions.enabled=true` and exposed securely — rare in prod, common in staging namespace. For CI, `ApplicationContextRunner` test captures conditions programmatically via `getBean(ConditionEvaluationReport.class)` in Boot test support — assert Kafka config applied when property set. Targeted over global debug.

**Q:** `@ConditionalOnMissingBean` gotcha?
**A:** Your `@Bean` of type `ObjectMapper` causes Jackson auto-config to back off entirely — sometimes you wanted only customizer, not replace defaults. Define `@Bean` `@ConditionalOnMissingBean` only in custom config if extending defaults. Order matters: user config processed with auto-config — explicit `@Bean` wins. Test: remove custom bean, verify auto-config restores. Document "if you define X, you own full configuration."

**Q:** Debugging in K8s prod pod?
**A:** Prefer staging replica with same image and env ConfigMap. If must prod: exec ephemeral debug container or toggle env `LOGGING_LEVEL_ORG_SPRINGFRAMEWORK_BOOT_AUTOCONFIGURE=DEBUG` and rolling restart one canary pod, scrape startup logs from init window only. Fetch `/actuator/conditions` if management port on localhost sidecar. Never paste full report externally — may list internal class names. Post-incident: add bean presence integration test.

#### Scenario probe
**Situation:** After Boot 4 upgrade, Redis cache beans absent — app runs but no caching, higher DB load.

**Model answer:** `ConditionEvaluationReport` negative: `@ConditionalOnClass` failed because `spring-boot-starter-data-redis` removed from pom during BOM migration. Or `@ConditionalOnProperty(cache.type=redis)` but property now `spring.cache.type`. Diff report between Boot 3 and 4 staging startup. Fix dependency and property key per migration guide. Add `@EnabledIf` integration test verifying `CacheManager` bean type `RedisCacheManager`. Canary metric: cache hit ratio alert fired — how we detected.

#### Code / config (when useful)

```yaml
debug: true # local only
logging:
  level:
    org.springframework.boot.autoconfigure: DEBUG
```

---

### 78. Spring Boot 4 / Spring Framework 7 migration notes seniors should know

**Short answer:** Boot 4 / Framework 7 continue Jakarta EE 11 baseline, Java 17 minimum (21 recommended), and refined observability-first defaults. Expect dependency renames, stricter null-safety APIs, Security 7 filter chain DSL stabilization, and removal of long-deprecated APIs (`RestTemplate` guidance, legacy bootstrap). Migration: bump BOM, run `dependency:tree`, fix compile breaks in custom starters, re-run `ConditionEvaluationReport` diff, and validate native image if used. Treat modularization of Spring jars and configuration property renames as the hidden work — not just version number.

#### What it is
Major Spring release train aligning Boot, Framework, Security, Data, and Cloud compatibility matrix. Seniors plan multi-module upgrades with canary service, library BOM publish, and rollback artifact retained.

#### How it works (internals)
Parent POM 4.x imports Framework 7.x — bytecode and reflection hints may change for GraalVM. Auto-configuration classes move packages occasionally — custom `@ImportAutoConfiguration` lists need update. Security 7: lambda DSL only, removed deprecated methods from Security 5 era. Jackson 3.x trajectory (verify release notes at upgrade time) may affect `ObjectMapper` customizers. JPA 3.2 / Hibernate alignment — schema validate mode stricter. Property migrator: `spring-boot-properties-migrator` dependency logs renames at startup (temporary).

#### When to use / when NOT to use
Upgrade when platform needs CVE fixes, Java 21 runtime, or native image improvements — not because number incremented. Stay on N-1 if Spring Cloud train not ready for your mesh config. Always read release notes for breaking changes in areas you use (OAuth2, WebFlux, Batch).

#### Production example
Platform upgraded forty services Boot 3.4 → 4.0: common breaks — `spring.security.oauth2.resourceserver` property renames, custom `WebSecurityConfigurerAdapter` remnants finally removed, Flyway 10 config keys. Canary order-service ran two weeks; found Micrometer metric tag limit change. Rollback procedure: previous jar in EB/App Service version label. Post-upgrade enforcer banned `javax.*` imports reappearing from old libs.

#### Common mistakes
- Upgrading Boot without Spring Cloud compatible release train.
- Skipping integration tests — condition report diffs only in prod.
- Assuming Feign/ Springfox still work — migrate to HTTP interfaces and springdoc.
- Ignoring Hibernate schema validation failures until deploy night.

#### Interview follow-ups (with model answers)

**Q:** Practical upgrade checklist?
**A:** (1) Read Boot 4 release notes and Framework 7 breaking changes appendix. (2) Bump parent BOM, run `mvn -q clean verify`. (3) Add `spring-boot-properties-migrator`, fix logged renames. (4) Run Testcontainers integration suite. (5) Compare actuator conditions report staging old vs new. (6) Load test critical paths. (7) Update internal starters and archetype. (8) Plan rollback artifact and DB migration compatibility. (9) Native image build if applicable. (10) Communicate Cloud BOM version pin to teams.

**Q:** Java version implications?
**A:** Boot 4 expects Java 17+; platform standard Java 21 for virtual threads and improved GC. Remove `--illegal-access` hacks from Java 8 era. Update CI Docker base image `eclipse-temurin:21-jre`. Some agents (old APM) may need updates for JDK 21 bytecode. Record types and pattern matching clean up DTO code — optional refactor during upgrade, not required. Verify JVM flags in EB/K8s deployment manifests.

**Q:** What breaks custom Spring Boot starters?
**A:** Auto-configuration registration file still `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` — verify no `spring.factories` leftover Boot 2 style. Renamed configuration properties break consumers — semver major on your starter. `@ConditionalOnClass` strings must reference classes still on classpath after your dependency changes. Integration test your starter against sample app on Boot 4 before publishing to Nexus. Document migration guide for downstream teams.

#### Scenario probe
**Situation:** Boot 4 upgrade PR green in CI but OAuth2 resource server 401s all tokens in staging — issuer unchanged.

**Model answer:** Spring Security 7 resource server JWT decoder auto-config now requires updated property namespace or `jwk-set-uri` vs issuer-uri behavior tightened. Old `spring.security.oauth2.resourceserver.jwt.issuer-uri` typo masked by fallback removed. Compare Security filter chain beans conditions report. Fix properties per migration guide; add MockMvc test with sample JWT from staging IdP. CI gap: unit tests mocked security — add smoke test with real token fixture rotated weekly.

#### Code / config (when useful)

```xml
<dependency>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-properties-migrator</artifactId>
  <scope>runtime</scope>
</dependency>
```

---

### 79. Encoding vs hashing vs encryption — BCrypt, AES, Base64 in security context.

**Short answer:** Encoding (Base64) is reversible representation — not security. Hashing (BCrypt, Argon2) is one-way with salt for passwords — verify with `matches`, never decrypt. Encryption (AES) is reversible with a key — use for data at rest or field-level PII, not for passwords. Confusing the three causes audit failures and breach amplification.

#### What it is
Three distinct transforms applied in banking apps: Base64 for transport-safe strings, adaptive hashing for credentials in the `customers` table, AES-GCM for encrypting account numbers or PAN tokens at rest. Spring Security's `PasswordEncoder` covers hashing only — not encryption.

#### How it works (internals)
BCrypt embeds cost factor and salt in the stored string (`$2a$12$...`). `BCryptPasswordEncoder.encode` generates new salt each call; `matches` is constant-time. AES requires key management (KMS, rotation). Base64 decodes to original bytes — anyone with the string can recover data. JWT payloads are Base64URL-encoded JSON — that is not encryption; anyone can read claims without the signature key.

#### When to use / when NOT to use
Hash passwords with BCrypt/Argon2. Encrypt reversible secrets (SSN token, card surrogate) with AES and envelope encryption. Base64 for binary-in-JSON only. Never "encrypt" passwords with AES "because we can decrypt for support" — use reset flows instead.

#### Production example
EazyBank-style monolith stored customer PIN as Base64 — pen test decoded all PINs in minutes. Remediation: BCrypt for credentials, AES-GCM column encryption for national ID with key in Azure Key Vault, JWT claims carry only `sub` and roles — no account numbers. Login latency rose 40ms from BCrypt cost 12 — acceptable vs breach cost.

#### Common mistakes
- MD5/SHA-256 without salt for passwords — rainbow tables break them in hours.
- Calling Base64 "encryption" in architecture diagrams — auditors flag immediately.
- Same AES key in `application.yml` across environments — one leak decrypts prod.
- Storing BCrypt output then Base64-encoding it "for safety" — pointless overhead.

#### Interview follow-ups (with model answers)

**Q:** Why not encrypt passwords with AES if we store the key in a vault?
**A:** Encryption implies decryption — any key compromise or insider with decrypt permission exposes all passwords. Hashing is verify-only: attacker with DB dump still faces per-password brute force bounded by BCrypt cost. Vault access becomes single point of failure. Industry standard (NIST, OWASP) mandates salted adaptive hashing for memorized secrets; encryption is for data you must read back (account metadata, tokens at rest).

**Q:** How do you pick BCrypt strength vs login latency SLO?
**A:** Benchmark `matches` on prod-sized hardware at p99 — target under 200ms per login including DB lookup. Cost factor 10–12 is typical in 2024; raise gradually as hardware improves. Use `DelegatingPasswordEncoder` so you can bump `{bcrypt}` cost for new encodes without invalidating existing hashes. Monitor auth endpoint latency after changes; load-test login during peak (month-end statements).

**Q:** Where does Base64 appear legitimately in a Spring Security stack?
**A:** JWT header/payload segments are Base64URL — signature is what provides integrity. HTTP Basic credentials are Base64 of `user:pass` — transport must be TLS. PEM-encoded RSA public keys for JWT verification. None of these replace hashing for stored passwords; teach teams that "encoded" ≠ "protected."

#### Scenario probe
**Situation:** EazyBank mobile team stores the JWT in `localStorage` and claims it is "encrypted" because they Base64-wrap the token before saving. Security review is next week.

**Model answer:** Base64 offers zero confidentiality — any XSS script reads `localStorage` and decodes instantly. Real fixes: short-lived access token in memory, refresh via HttpOnly `SameSite=Strict` cookie on BFF, or PKCE OAuth with token in memory only. If they insist on storage, use Web Crypto with a non-extractable key — still inferior to cookie+BFF. I would document threat model (XSS vs CSRF), align with Q90/Q91, and add ZAP scan to CI blocking release until `localStorage` token pattern is removed.

#### Code / config (when useful)

```java
@Bean
PasswordEncoder passwordEncoder() {
    return new BCryptPasswordEncoder(12); // hashing — not encryption
}

// Field-level encryption — separate concern, KMS-backed key
@Bean
StringEncryptor panEncryptor(@Value("${vault.pan-key}") String key) {
    return new AES256TextEncryptor(key); // reversible — never for passwords
}
```

---

### 80. `PasswordEncoder` hierarchy — BCrypt, Argon2, delegating encoder for migrations.

**Short answer:** Spring Security's `PasswordEncoder` interface abstracts `encode` and `matches`. `BCryptPasswordEncoder` is the default workhorse; `Argon2PasswordEncoder` wins on modern hardware when native libs available. `DelegatingPasswordEncoder` stores `{id}encodedValue` so multiple algorithms coexist — critical for zero-downtime hash upgrades after acquisitions or legacy SHA migrations.

#### What it is
The encoder hierarchy lives in `spring-security-crypto`. Boot auto-config does not pick your encoder for custom `UserDetailsService` — you declare `@Bean PasswordEncoder`. Delegating encoder is the production pattern when user tables span merged banks with different historical hash formats.

#### How it works (internals)
`DelegatingPasswordEncoder` maps id prefix (`bcrypt`, `argon2`, `pbkdf2`) to delegate encoders. `matches(raw, "{bcrypt}$2a$...")` routes to BCrypt. `encode` uses `defaultIdForEncode` — set to `bcrypt` or `argon2`. `PasswordEncoderFactories.createDelegatingPasswordEncoder()` registers BCrypt, LDAP, PBKDF2, scrypt, Argon2. On successful login, re-encode with preferred algorithm and update row — lazy migration without mass password reset.

#### When to use / when NOT to use
Always inject `PasswordEncoder` — never `new BCryptPasswordEncoder()` scattered in services. Use delegating encoder when any legacy hash exists. Argon2 for greenfield if ops approve native dependency. Do not register weak ids (`noop`, `sha256`) in prod delegating map except during controlled migration windows.

#### Production example
EazyBank acquired RegionalCU — 2M users with `{SHA-256}` unsalted hashes. `DelegatingPasswordEncoder` registers `sha256` legacy delegate for `matches` only; `defaultIdForEncode` is `bcrypt`. On login, `AuthenticationProvider` success handler rewrites hash to `{bcrypt}`. After 18 months, 94% migrated; remaining forced reset email. No big-bang outage.

#### Common mistakes
- Single `BCryptPasswordEncoder` bean — cannot verify legacy `{ldap}` hashes after LDAP cutover.
- Re-encoding on every login even when already `{bcrypt}` — unnecessary DB writes.
- Setting `defaultIdForEncode` to `noop` in dev and shipping same config to prod.
- Comparing hashes with `String.equals` instead of `passwordEncoder.matches`.

#### Interview follow-ups (with model answers)

**Q:** How do you implement lazy migration in `AuthenticationProvider`?
**A:** After `passwordEncoder.matches` succeeds, check if stored hash starts with preferred id (`{bcrypt}`). If not, call `encode(rawPassword)` with delegating encoder's default id, persist via `UserRepository`, all inside the same transaction as last-login update. Log migration metric `auth.password.reencoded`. Never re-encode on failed login — prevents oracle timing attacks on migration state. Feature-flag mass migration job only for dormant accounts with secure reset link.

**Q:** Argon2 vs BCrypt in JVM microservices?
**A:** Argon2id resists GPU cracking better at equal wall-clock cost; `Argon2PasswordEncoder.defaultsForSpringSecurity_v5_8()` needs Bouncy Castle. BCrypt is universally understood by auditors and ops. For high-value banking, Argon2 with tuned memory (64MB) is defensible if you load-test pod memory. Hybrid: delegating encoder with `argon2` default, `bcrypt` delegate for existing rows.

**Q:** What if you inherit plaintext passwords from a vendor dump?
**A:** Force password reset — never "hash on first login" without notifying user. Import users with `accountLocked=true` and `{bcrypt}` random placeholder impossible to guess. Send reset link via verified channel. Plaintext import is a compliance incident — document in SOC2 timeline. `matches` against plaintext should never exist in prod delegating map.

#### Scenario probe
**Situation:** EazyBank loans microservice copies `User` entities from core banking with MD5 password column. Team proposes one-time batch `BCrypt.encode` job over MD5 strings without user interaction.

**Model answer:** Double-hashing MD5 does not recover original password — users cannot login with their real password because you hashed the hash, not the plaintext. Correct path: delegating encoder with custom `md5` delegate for `matches(plain, md5(plain))` OR force reset. Batch re-encode to BCrypt only after successful login with correct plain. Communicate to compliance; MD5 delegate is temporary with sunset date. Add integration test proving legacy user can login once and stored value becomes `{bcrypt}`.

#### Code / config (when useful)

```java
@Bean
PasswordEncoder passwordEncoder() {
    var bcrypt = new BCryptPasswordEncoder(12);
    var argon2 = Argon2PasswordEncoder.defaultsForSpringSecurity_v5_8();
    Map<String, PasswordEncoder> encoders = Map.of(
        "bcrypt", bcrypt,
        "argon2", argon2
    );
    var delegating = new DelegatingPasswordEncoder("bcrypt", encoders);
    delegating.setDefaultPasswordEncoderForMatches(bcrypt);
    return delegating;
}
```

---

### 81. Spring Security filter chain order — `SecurityFilterChain`, `OncePerRequestFilter`, where JWT filter sits.

**Short answer:** Each `SecurityFilterChain` is an ordered list of servlet filters registered before `DispatcherServlet`. JWT authentication belongs after `SecurityContextHolderFilter` and before `UsernamePasswordAuthenticationFilter` / `AuthorizationFilter` — typically via `addFilterBefore(jwtFilter, UsernamePasswordAuthenticationFilter.class)`. Custom filters should extend `OncePerRequestFilter` to avoid double execution on forwards. Wrong order yields anonymous users passing authorization or CSRF blocking preflight.

#### What it is
Spring Security 6 replaces `WebSecurityConfigurerAdapter` with `@Bean SecurityFilterChain`. Multiple chains use `@Order` and `securityMatcher`. Understanding filter order is how you debug "token present but 403" in EazyBank's API gateway and account services.

#### How it works (internals)
Notable default order: `DisableEncodeUrlFilter` → `SecurityContextHolderFilter` → `HeaderWriterFilter` → `CsrfFilter` → `LogoutFilter` → `UsernamePasswordAuthenticationFilter` → `DefaultLoginPageGeneratingFilter` → `AuthorizationFilter` → ... → `FilterSecurityInterceptor` (legacy name in logs). Resource server adds `BearerTokenAuthenticationFilter` near authentication slot. `ExceptionTranslationFilter` converts `AuthenticationException` to 401 and `AccessDeniedException` to 403. `OncePerRequestFilter` stores request attribute to skip re-entry on `RequestDispatcher.forward`.

#### When to use / when NOT to use
One chain for stateless JWT API; separate chain for actuator or form login. Insert custom filters at explicit anchor points — never `addFilter` at end without understanding authorization timing. Do not parse JWT in a random `@Component` filter outside security chain — breaks test utilities and consistent error handling.

#### Production example
EazyBank accounts API: `@Order(1)` chain matches `/api/**`, disables CSRF, stateless session, `oauth2ResourceServer().jwt()`. Custom `TenantFilter` extends `OncePerRequestFilter`, extracts `X-Tenant-Id`, validates against JWT claim, placed after bearer filter. Bug: tenant filter before bearer — `SecurityContext` empty, all requests 401. Fixed order; added `FilterRegistrationBean` integration test logging filter order at DEBUG.

#### Common mistakes
- JWT filter after `AuthorizationFilter` — authorization runs as anonymous.
- Forgot `shouldNotFilter` for `/actuator/health` — health flaps under bad tokens.
- Multiple chains matching `/**` — first `@Order` wins, shadowing admin form login.
- Not using `OncePerRequestFilter` — double JWT parse on error dispatch, 2x DB hits.

#### Interview follow-ups (with model answers)

**Q:** How do you log the effective filter order in a Boot integration test?
**A:** Enable `logging.level.org.springframework.security=DEBUG` and inspect `Will secure any request with filters:` line at startup. Alternatively inject `FilterChainProxy` in test, call `getFilters("/api/accounts")`, assert index of your filter relative to `BearerTokenAuthenticationFilter`. Snapshot filter names in test to catch accidental reorder during Security 6 lambda DSL refactors. CI fails if custom JWT filter index > authorization filter.

**Q:** `addFilterBefore` vs `addFilterAfter` vs security DSL `oauth2ResourceServer`?
**A:** `oauth2ResourceServer().jwt()` registers `BearerTokenAuthenticationFilter` at the correct default position — prefer it over hand-rolled JWT filter when issuer is standard OIDC. Use `addFilterBefore` for tenant, MDC, or rate-limit filters that need `SecurityContext` populated or intentionally run before bearer validation. Custom bearer parsing duplicates Nimbus decoder maintenance — only when legacy HMAC tokens predate IdP.

**Q:** How does filter order interact with CORS preflight OPTIONS?
**A:** `CorsFilter` runs early; preflight must return 200 before JWT filter rejects missing Authorization. Misconfiguration: JWT filter requires Bearer on OPTIONS — browser blocks SPA login. Fix: `requestMatchers(HttpMethod.OPTIONS, "/**").permitAll()` or ensure `CorsFilter` short-circuits. EazyBank React app symptom: CORS error in console but root cause is JWT filter on OPTIONS.

#### Scenario probe
**Situation:** After Security 6 migration, EazyBank transfer API returns 403 for valid JWT. Logs show `AuthorizationFilter` denied before `BearerTokenAuthenticationFilter` appears in the chain dump.

**Model answer:** Filter registration order bug — likely custom `SecurityFilterChain` used `addFilterAfter(authorizationFilter, jwtFilter)` or missing `oauth2ResourceServer` entirely. Fix: `http.oauth2ResourceServer(oauth2 -> oauth2.jwt(Customizer.withDefaults()))` OR `addFilterBefore(jwtFilter, UsernamePasswordAuthenticationFilter.class)`. Verify with DEBUG startup log. Add `@AutoConfigureMockMvc` test with `jwt()` post-processor asserting 200 on `/api/transfers`. Document chain diagram in ADR for future migrations.

#### Code / config (when useful)

```java
@Bean
SecurityFilterChain apiChain(HttpSecurity http, JwtAuthFilter jwtFilter) throws Exception {
    http.securityMatcher("/api/**")
        .csrf(csrf -> csrf.disable())
        .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
        .authorizeHttpRequests(a -> a
            .requestMatchers("/api/public/**").permitAll()
            .anyRequest().authenticated())
        .addFilterBefore(jwtFilter, UsernamePasswordAuthenticationFilter.class);
    return http.build();
}

@Component
class JwtAuthFilter extends OncePerRequestFilter {
    @Override
    protected void doFilterInternal(HttpServletRequest req, HttpServletResponse res, FilterChain chain)
            throws ServletException, IOException {
        // parse Bearer, set SecurityContext
        chain.doFilter(req, res);
    }
}
```

---

### 82. Custom `AuthenticationProvider` and `UserDetailsService` with database roles.

**Short answer:** `UserDetailsService` loads user identity and `GrantedAuthority` list from DB (users, roles, permissions tables). `AuthenticationProvider` performs credential validation — default is `DaoAuthenticationProvider` with `PasswordEncoder`. Custom providers handle MFA, API keys, or legacy mainframe ticket validation. Both register via `AuthenticationManager` built from `AuthenticationConfiguration`.

#### What it is
The authentication architecture behind EazyBank login: `customers` join `user_roles` join `roles`, exposed as `ROLE_CUSTOMER`, `ROLE_TELLER`. Separating loading (`UserDetailsService`) from verification (`AuthenticationProvider`) lets you swap LDAP for DB without rewriting authorization rules.

#### How it works (internals)
`DaoAuthenticationProvider.supports(UsernamePasswordAuthenticationToken)` loads user via `UserDetailsService.loadUserByUsername`, checks `PasswordEncoder.matches`, populates authenticated token with authorities. `User` entity implements `UserDetails` or map to `User.builder().username().password().roles("CUSTOMER")`. Method security and `hasRole` expect `ROLE_` prefix unless `GrantedAuthorityDefaults` strips it. `ProviderManager` iterates providers until one supports token type.

#### When to use / when NOT to use
Default DAO provider for username/password. Custom provider when second factor or risk score gates login. `UserDetailsService` always DB-backed for banking — avoid hardcoded `InMemoryUserDetailsManager` beyond local dev. JDBC `JdbcUserDetailsManager` for simple schemas; JPA for rich domain.

#### Production example
EazyBank: `BankUserDetailsService` loads customer by email, attaches roles from `customer_roles` and fine-grained `ACCOUNT_READ` permissions as `GrantedAuthority`. Custom `RiskAwareAuthenticationProvider` wraps DAO — calls fraud API before `success`. Failed risk returns `LockedException`. Audit table records provider class name and role list hash for SOC2.

#### Common mistakes
- Returning authorities without `ROLE_` prefix then wondering why `hasRole("ADMIN")` fails.
- `@Transactional` on `loadUserByUsername` with lazy roles collection — `LazyInitializationException` in filter thread.
- N+1 query loading roles per login — cache role map with TTL, not per-request join explosion.
- Custom provider not calling `hideUserNotFoundExceptions` — username enumeration via timing.

#### Interview follow-ups (with model answers)

**Q:** How do you map DB permissions to Spring authorities for hundreds of fine-grained rights?
**A:** Store permission codes (`TRANSFER_CREATE`, `LOAN_APPROVE`) as `GrantedAuthority` strings without ROLE prefix; use `@PreAuthorize("hasAuthority('TRANSFER_CREATE')")`. Roles become groupings in DB; permissions expanded at login or cached in JWT claims with size limit. Avoid putting 200 permissions in JWT — use role + method-level DB check via custom `@permissionChecker`. Refresh authorities on role change with short access token TTL (5–15 min).

**Q:** Testing custom `AuthenticationProvider` without MVC?
**A:** `@SpringBootTest` autowire `AuthenticationManager`, call `authenticate(new UsernamePasswordAuthenticationToken(user, pass))`, assert `Authentication.isAuthenticated()` and authority count. Mock fraud client in `@TestConfiguration` replacing provider bean. Negative tests: bad password, locked account, missing role. Use `@Sql` to seed users/roles in H2 or Testcontainers Postgres.

**Q:** Multiple authentication types in one app?
**A:** Register multiple providers on `ProviderManager`: `DaoAuthenticationProvider` for form login, custom `ApiKeyAuthenticationProvider` for B2B, `JwtAuthenticationProvider` usually handled by resource server filter instead. Each implements `supports(Class<?>)`. Separate filter chains: `/api/partner/**` reads API key header; `/api/customer/**` uses JWT.

#### Scenario probe
**Situation:** EazyBank teller dashboard: users with `TELLER` role in DB get 403 on `/api/teller/customers`. `UserDetailsService` logs show authorities `[TELLER]` not `[ROLE_TELLER]`.

**Model answer:** `hasRole("TELLER")` expands to `ROLE_TELLER` authority check. Fix: prefix in service `new SimpleGrantedAuthority("ROLE_" + role.getName())` or configure `GrantedAuthorityDefaults` with empty role prefix consistently across app and JWT claim mapping. Add MockMvc test with `@WithUserDetails` or JWT mock asserting teller endpoint 200. Regression: authority contract documented for IdP group → role sync job.

#### Code / config (when useful)

```java
@Service
class BankUserDetailsService implements UserDetailsService {
    private final CustomerRepository customers;
    BankUserDetailsService(CustomerRepository customers) { this.customers = customers; }

    @Override
    @Transactional(readOnly = true)
    public UserDetails loadUserByUsername(String email) {
        var c = customers.findByEmailWithRoles(email).orElseThrow(() -> new UsernameNotFoundException(email));
        var authorities = c.getRoles().stream()
            .map(r -> new SimpleGrantedAuthority("ROLE_" + r.getName()))
            .toList();
        return User.builder().username(c.getEmail()).password(c.getPasswordHash()).authorities(authorities).build();
    }
}
```

---

### 83. JWT structure — header, payload, signature; validation steps; clock skew; key rotation.

**Short answer:** JWT is `header.payload.signature` (Base64URL). Header declares alg (`RS256`); payload holds claims (`sub`, `exp`, `iss`, `aud`, roles); signature proves integrity with HMAC secret or RSA private key. Validation: parse, verify signature, check `exp`/`nbf` with clock skew, validate `iss` and `aud`, then trust claims. Key rotation via JWKS `kid` header matching IdP key set — never skip audience validation.

#### What it is
Token format used by EazyBank SPA after login and between microservices. Spring's `NimbusJwtDecoder` fetches JWKS from `issuer-uri` and caches keys. Understanding structure separates "decode" (readable JSON) from "validate" (cryptographically trusted).

#### How it works (internals)
Validation steps: (1) parse JWS, (2) reject `alg=none`, (3) verify signature with key for `kid`, (4) validate temporal claims with `JwtValidators.createDefaultWithIssuer` plus clock skew (`ClockSkew` ~60s), (5) validate `aud` contains this API's client id, (6) optional custom validators for `tenant_id`. Rotation: IdP publishes new key in JWKS, old `kid` still valid during overlap; decoder refreshes on unknown `kid` or schedule. Symmetric HS256: rotation means distributing new secret to all services atomically — prefer RS256 + JWKS.

#### When to use / when NOT to use
Short-lived access JWT (5–15 min) + refresh token for SPAs. Do not put PII or PAN in payload — claims are readable. Avoid HS256 shared secret across 20 microservices — one leak compromises all. Use opaque tokens + introspection only when revocation latency requirement beats JWT performance.

#### Production example
EazyBank Keycloak realm rotates RSA keys every 90 days with 24h overlap. Accounts service `spring.security.oauth2.resourceserver.jwt.issuer-uri` points to realm. Incident: mobile clocks skewed 3 minutes — fixed with 60s skew, not disabling `exp`. Custom validator rejected tokens missing `aud=accounts-api` — caught tokens issued for admin client being replayed on customer API.

#### Common mistakes
- Trusting payload after `Base64.decode` without signature verify — attacker crafts admin role.
- No `aud` check — token for one client works on all services.
- Infinite TTL access token "for UX" — stolen token valid until manual revoke.
- Logging full JWT in access logs — credentials in claims leak to Splunk.

#### Interview follow-ups (with model answers)

**Q:** How do you configure clock skew in Spring Security 6?
**A:** `JwtValidators.createDefaultWithIssuer(issuer)` uses default skew; customize via `NimbusJwtDecoder.withJwkSetUri(uri).clockSkew(Duration.ofSeconds(60))` then `decoder.setJwtValidator(new DelegatingOAuth2TokenValidator<>(issuerValidator, audienceValidator))`. Mobile banking sees skew on cellular networks — 30–60s is typical. Monitor `JwtValidationException` metrics tagged `invalid_exp` vs `invalid_signature` to separate clock drift from attacks.

**Q:** Walk through key rotation with zero downtime.
**A:** IdP adds new JWK with new `kid`, signs new tokens with it, keeps old key in JWKS for existing token lifetimes. Resource servers cache JWKS — `NimbusJwtDecoder` refreshes on signature failure or periodic poll. Overlap window ≥ max access token TTL. After window, remove old key. Automate with Keycloak "keys" tab or SAS `JwkSet` rotation. Run integration test firing tokens signed by both keys during overlap simulation.

**Q:** Where do roles live — JWT claim vs `UserDetailsService` reload?
**A:** JWT `realm_access.roles` or custom `roles` claim for coarse authorization — fast, no DB per request. Sensitive banking actions (wire transfer > $10k) re-check DB or policy service despite JWT role. Role change propagation delay = access token TTL — admin revokes role, user retains until exp unless you maintain token blocklist (Redis) for high-security events.

#### Scenario probe
**Situation:** EazyBank pen test replays a valid customer JWT against the internal `loan-origination` API and succeeds — same Keycloak realm, different audience.

**Model answer:** Loan service validated `iss` and signature but not `aud`. Fix: `OAuth2TokenValidator<Jwt>` checking `aud` contains `loan-api` client id; reject at decoder. Keycloak: separate clients per service with audience mappers. Add negative integration test with token minted for `accounts-api` client calling loan endpoints — expect 401. Document in zero-trust matrix: every resource server validates audience, not just gateway.

#### Code / config (when useful)

```java
@Bean
JwtDecoder jwtDecoder(@Value("${spring.security.oauth2.resourceserver.jwt.issuer-uri}") String issuer) {
    var decoder = (NimbusJwtDecoder) JwtDecoders.fromIssuerLocation(issuer);
    OAuth2TokenValidator<Jwt> withAudience = new JwtClaimValidator<List<String>>(
        "aud", aud -> aud != null && aud.contains("accounts-api"));
    decoder.setJwtValidator(new DelegatingOAuth2TokenValidator<>(
        JwtValidators.createDefaultWithIssuer(issuer), withAudience));
    return decoder;
}
```

---

### 84. OAuth 2.0 grant types — authorization code + PKCE, client credentials, refresh token; when each.

**Short answer:** Authorization code + PKCE is for user-facing clients (SPA, mobile) — user consents, client never sees user password. Client credentials is machine-to-machine — no user context, service identity only. Refresh token extends sessions without re-login — store securely, rotate, bind to client. Implicit/password grants are deprecated — reject in new EazyBank designs.

#### What it is
OAuth2 defines how clients obtain access tokens from authorization server (Keycloak, Auth0, SAS). Grant type choice drives threat model for EazyBank channels: React SPA, iOS app, nightly batch posting to general ledger.

#### How it works (internals)
Auth code + PKCE: client generates `code_verifier`/`code_challenge`, redirects user to `/authorize`, receives `code`, exchanges at `/token` with verifier — prevents intercepted code replay. Client credentials: `grant_type=client_credentials` with `client_id`/`client_secret` (or mTLS) for service JWT with `sub=service-account`. Refresh token: `grant_type=refresh_token` returns new access token; rotation issues new refresh and invalidates old. Spring: `spring-boot-starter-oauth2-client` for outbound; resource server for inbound validation.

#### When to use / when NOT to use
PKCE auth code for SPA/mobile — always. Client credentials for account-aggregator → core banking sync job. Refresh tokens for long-lived sessions with rotation — not in browser localStorage. Never auth code without PKCE for public clients. Resource owner password grant only in legacy migration with sunset plan.

#### Production example
EazyBank React SPA uses PKCE against Keycloak public client `eazybank-ui`. BFF optional pattern: confidential server exchanges code, sets HttpOnly session. `statement-print` batch service uses client credentials, gets token scoped `statements:generate` only. Refresh rotation caught stolen refresh — reuse detection revoked family.

#### Common mistakes
- SPA as confidential client with embedded secret — secret extracted from bundle.
- Client credentials token passed to browser — full service privileges exposed.
- Refresh token in `localStorage` — XSS exfiltration; use HttpOnly cookie on BFF.
- Same scopes for user and service tokens — blast radius on leak.

#### Interview follow-ups (with model answers)

**Q:** Why PKCE for SPA if redirect URI is `https://app.eazybank.com`?
**A:** Public clients cannot hold secrets — any native app or SPA binary is untrusted. PKCE proves the same party that started authorize flow exchanges the code, mitigating interception on custom URL schemes or compromised redirect handlers. Auth code alone is replayable by malware registering same redirect on mobile. PKCE is mandatory in OAuth 2.1 for all clients including confidential for defense in depth.

**Q:** How does refresh token rotation detect theft?
**A:** Authorization server issues new refresh on each use, invalidates previous. Attacker and legitimate user race — second presentation triggers `invalid_grant` and revokes entire refresh token family. EazyBank configures Keycloak "Revoke Refresh Token" and reuse detection. Client must persist new refresh atomically. Monitor `refresh_token_reuse` alerts — possible XSS or device compromise.

**Q:** Client credentials vs user token for microservice A calling B calling C?
**A:** User delegation: pass user JWT only to services needing user context (audit trail). Service identity: A uses client credentials to call B with `sub=service-a`, B trusts policy on service identity not end-user role. User token propagation leaks privileges and couples lifetimes. Token exchange (RFC 8693) when A needs constrained delegation — advanced pattern for banking federations.

#### Scenario probe
**Situation:** EazyBank mobile Android app uses `client_secret` baked in APK to get tokens via client credentials — no user login screen for "faster UX."

**Model answer:** Unacceptable — all users share service identity, no per-customer audit, secret extractable via APK decompile. Fix: OAuth auth code + PKCE with custom URI scheme or App Links, per-user tokens, optional biometric unlock storing refresh in EncryptedSharedPreferences. Play Store review may flag embedded secrets. Pen test finding: critical; block release, rotate leaked secret, invalidate issued tokens.

#### Code / config (when useful)

```yaml
spring:
  security:
    oauth2:
      client:
        registration:
          eazybank-batch:
            client-id: statement-batch
            client-secret: ${BATCH_CLIENT_SECRET}
            authorization-grant-type: client_credentials
            scope: statements:generate
```

---

### 85. OpenID Connect vs OAuth2 — ID token vs access token, `openid` scope, userinfo endpoint.

**Short answer:** OAuth2 authorizes access to resources (access token). OpenID Connect adds identity layer: `openid` scope yields ID token (JWT about the user) plus access token. ID token is for client authentication of user identity (`sub`, `email`); access token is for calling APIs (`/userinfo` or resource servers). Never send ID token to downstream microservices as bearer — wrong token type.

#### What it is
OIDC sits on OAuth2 flows EazyBank uses at login. Keycloak issues both tokens at `/token` endpoint. React SPA displays "Welcome, Jane" from ID token claims; calls `/api/accounts` with access token.

#### How it works (internals)
ID token: JWT signed by IdP, contains `iss`, `sub`, `aud` (client id), `exp`, `nonce` (binds to auth request). Validated by client library only — not for API authorization. Access token: may be JWT or opaque; scopes like `accounts:read`. `userinfo` endpoint returns claims given valid access token with `openid` scope. `nonce` prevents replay in implicit/hybrid legacy flows; still good practice in auth code. Spring Security OIDC login: `oauth2Login()` validates ID token, creates session; resource server validates access token separately.

#### When to use / when NOT to use
Request `openid profile email` for login UI. API calls always use access token with resource-specific scopes. BFF validates ID token once at login; SPA never needs to parse ID token if server renders session. Do not put authorization decisions on ID token roles in microservices — access token carries API scopes.

#### Production example
EazyBank SPA misconfigured axios to send `id_token` to accounts API — API rejected (wrong `aud`, no `accounts:read` scope). Fix: separate storage — access token for API, ID token discarded after extracting display name. `userinfo` used only when access token lacks profile claims. Keycloak mapper adds `customer_id` to access token for correlation.

#### Common mistakes
- Using ID token as `Authorization: Bearer` on APIs — common SPA bug.
- Skipping `nonce` validation — OIDC hybrid attacks in older tutorials.
- Trusting `email` claim in ID token without verification when email scope not verified.
- Confusing `sub` across realms — same email, different `sub` per realm.

#### Interview follow-ups (with model answers)

**Q:** What does Spring Security validate on OIDC login vs resource server JWT?
**A:** `oauth2Login()` uses `OidcIdTokenValidator` — checks `iss`, `aud`, `exp`, `nonce` against client registration. Resource server `jwt()` validator checks access token `iss`, `aud` (resource), scopes, signature. Different validators, different `aud` values. Mixing configs causes "login works, API 401". Integration test both paths. IdP must issue access tokens as JWT for stateless microservices or use introspection.

**Q:** When call `/userinfo` vs read claims from ID token?
**A:** ID token carries baseline claims at login time — sufficient for display. `/userinfo` when access token is opaque or claims updated server-side (role change) without re-login. Rate-limit userinfo — not per API request. EazyBank caches userinfo in BFF session at login, refreshes on schedule. Per-request userinfo adds latency and IdP load.

**Q:** How does `openid` scope change token response?
**A:** Without `openid`, OAuth2 returns only access token (pure authorization). With `openid`, response includes `id_token` and often `token_type`, `expires_in`, `refresh_token`. Authorization server must support OIDC metadata at `/.well-known/openid-configuration`. Spring client `scope: openid,profile,email` in `application.yml`.

#### Scenario probe
**Situation:** EazyBank security architect asks why React app stores both tokens in sessionStorage and sends whichever is longer to microservices "for convenience."

**Model answer:** ID token is shorter-lived and wrong audience — APIs must reject it; using longer token invites developers to pick wrong one. Standardize: access token only in API layer; ID token parse once at login for UI; or eliminate SPA token handling via BFF server session. Add API gateway policy rejecting tokens without `typ` or with `at_hash` ID-token-only markers. ESLint rule blocking `id_token` in fetch wrappers.

#### Code / config (when useful)

```yaml
spring:
  security:
    oauth2:
      client:
        registration:
          eazybank:
            scope: openid, profile, email, accounts:read
        provider:
          eazybank:
            issuer-uri: https://auth.eazybank.com/realms/eazybank
```

---

### 86. OAuth2 Resource Server with Spring Security 6 — `jwt` decoder, issuer-uri, audience validation.

**Short answer:** Add `spring-boot-starter-oauth2-resource-server`, configure `spring.security.oauth2.resourceserver.jwt.issuer-uri`, Spring builds `JwtDecoder` from OIDC metadata and JWKS. Lambda DSL: `http.oauth2ResourceServer(oauth2 -> oauth2.jwt(Customizer.withDefaults()))`. Always add audience validator — issuer alone is insufficient. Multi-tenant: multiple decoders or custom `AuthenticationManagerResolver`.

#### What it is
How EazyBank account, loan, and card microservices accept the same Keycloak-issued access tokens without shared session store. Replaces homemade JWT filters with framework integration, `BearerTokenAuthenticationFilter`, and `JwtAuthenticationConverter` for authorities.

#### How it works (internals)
`issuer-uri` triggers discovery of `jwks_uri`, builds `NimbusJwtDecoder`. `BearerTokenAuthenticationFilter` extracts token, `JwtAuthenticationProvider` validates, populates `JwtAuthenticationToken` with `Jwt` principal. Authorities from `realm_access.roles` via `JwtAuthenticationConverter` or custom `Converter<Jwt, AbstractAuthenticationToken>`. Properties: `jwk-set-uri` when issuer discovery blocked. `opaque` introspection via `spring.security.oauth2.resourceserver.opaquetoken.introspection-uri` for non-JWT tokens.

#### When to use / when NOT to use
Stateless API tier behind gateway — resource server per service. Not for server-side rendered form login — use `oauth2Login`. Introspection when tokens are opaque or immediate revocation required. Do not disable issuer validation "for local dev" in prod profile.

#### Production example
`accounts-service`: `issuer-uri` Keycloak realm, audience `accounts-api`, roles mapped to `ROLE_*`. Gateway also validates JWT — defense in depth, not sole check. Staging misconfiguration pointed to prod issuer — tokens cross-environment; fixed with env-specific issuer env vars and startup test asserting realm hostname.

#### Common mistakes
- `permitAll()` on `/api/**` while resource server configured — security theater.
- Role converter expects `roles` claim but Keycloak sends `realm_access.roles` nested JSON.
- No clock skew — mobile clients fail at token boundary.
- Trusting gateway stripping Authorization — internal east-west calls must still authenticate.

#### Interview follow-ups (with model answers)

**Q:** Map Keycloak roles to `GrantedAuthority` in Spring Security 6?
**A:** `@Bean JwtAuthenticationConverter jwtAuthenticationConverter()` — set `JwtGrantedAuthoritiesConverter` with `setAuthoritiesClaimName("realm_access.roles")` won't work on nested claim; use custom converter parsing `Map realmAccess = jwt.getClaim("realm_access")`. Or Keycloak mapper flattening `roles` top-level array. Test with `@AutoConfigureMockMvc` and `jwt().authorities(new SimpleGrantedAuthority("ROLE_CUSTOMER"))`. Document claim shape in API README.

**Q:** Multiple issuers (acquired bank still on legacy IdP)?
**A:** `authenticationManagerResolver` on `oauth2ResourceServer` selecting decoder by `iss` claim or separate `securityMatcher` chains per URL prefix. Each chain its own `JwtDecoder` bean. Migration: tokens from both issuers valid during 6-month overlap. Metrics per issuer for sunset tracking.

**Q:** `jwk-set-uri` vs `issuer-uri`?
**A:** `issuer-uri` preferred — validates issuer claim matches discovery document. `jwk-set-uri` alone when issuer metadata unavailable but keys known — must add explicit issuer validator. Corporate TLS intercept proxies sometimes block discovery — pin `jwk-set-uri` with corporate root CA trust store in JVM.

#### Scenario probe
**Situation:** EazyBank cards API returns 401 for all requests after Keycloak upgrade. Logs: `The iss claim is not valid`.

**Model answer:** Issuer string mismatch — Keycloak now `https://auth.eazybank.com/realms/eazybank` but service still expects trailing slash or old hostname. Fix `issuer-uri` to exact `iss` in token (copy from jwt.io decode). Add startup `ApplicationRunner` fetching test token in staging. Keycloak hostname migration checklist: update all `issuer-uri`, gateway rules, and mobile app auth config simultaneously.

#### Code / config (when useful)

```yaml
spring:
  security:
    oauth2:
      resourceserver:
        jwt:
          issuer-uri: https://auth.eazybank.com/realms/eazybank
```

```java
@Bean
SecurityFilterChain api(HttpSecurity http) throws Exception {
    http.securityMatcher("/api/**")
        .authorizeHttpRequests(a -> a.anyRequest().authenticated())
        .oauth2ResourceServer(o -> o.jwt(Customizer.withDefaults()));
    return http.build();
}
```

---

### 87. OAuth2 Client — login with Google/GitHub (social login) in Spring Boot + React SPA.

**Short answer:** Spring Boot as OAuth2 client handles authorization code flow with `spring-boot-starter-oauth2-client` — `oauth2Login()` for browser redirects or BFF session. React SPA either redirects to Boot login endpoint or uses PKCE directly against IdP. Social login (Google/GitHub) federates identity — map external `sub` to internal customer record; still issue your own session or token for EazyBank APIs.

#### What it is
EazyBank "Sign in with Google" for retail customers who lack native credentials. Boot registers Google `client-id`/`client-secret`, exposes `/oauth2/authorization/google`. React either full-page redirect to Boot or uses `@react-oauth/google` with backend token exchange on BFF.

#### How it works (internals)
`OAuth2AuthorizationRequestRedirectFilter` starts flow; `OAuth2LoginAuthenticationFilter` completes callback, exchanges code, creates `OidcUser` or `OAuth2User`. `OAuth2UserService` loads attributes; custom `OidcUserService` links Google `sub` to `customers.google_id`. Session cookie `JSESSIONID` for server-side session or Boot returns JWT to SPA via secure endpoint post-login. CORS + `oauth2Login().defaultSuccessUrl` for SPA deep links. CSRF enabled for cookie session login flow.

#### When to use / when NOT to use
Social login for low-friction retail onboarding. Not for teller/admin — use corporate IdP SAML/OIDC with MFA. BFF pattern when SPA cannot hold secrets. Avoid embedding Google client secret in React — always server-side exchange.

#### Production example
EazyBank: Boot BFF `oauth2Login`, success handler creates local customer if `google_sub` new, issues HttpOnly session + CSRF token header for SPA. React queries `/api/me` with credentials. GitHub login only for developer portal — separate `SecurityFilterChain` `@Order(2)`. Account linking prevents duplicate emails — merge flow with MFA verification.

#### Common mistakes
- SPA handles Google secret — immediate credential leak.
- Not verifying Google `email_verified` before account creation — attacker Google account owns victim email.
- Same `client-id` for web and mobile without separate redirect URIs — Google rejects or open redirect.
- Forgetting CORS `allowCredentials` for cookie session from `localhost:3000`.

#### Interview follow-ups (with model answers)

**Q:** BFF oauth2Login vs SPA PKCE direct to Keycloak with Google broker?
**A:** Keycloak Google identity provider brokering centralizes federation — SPA PKCE to Keycloak, Keycloak handles Google, issues EazyBank-branded tokens. BFF oauth2Login simplifies SPA (no token handling) but couples UI to Boot session scale-out (Redis session). Retail EazyBank chose Keycloak broker for consistent JWT across web/mobile; corporate users skip Google on same realm via conditional auth flow.

**Q:** How link Google account to existing EazyBank customer?
**A:** On login, lookup by verified email — if exists, prompt MFA then attach `google_sub`. If email collision unverified, deny link. Store `federated_identity` table (provider, sub, customer_id). Never auto-merge solely on email without proof. Audit log `FEDERATED_LINK` for compliance.

**Q:** Logout with social login and SPA?
**A:** Clear server session (`/logout`), clear SPA state, optionally OIDC RP-initiated logout redirecting to Keycloak/Google end session endpoint. Front-channel logout across tabs via session cookie expiry. JWT SPA: discard access/refresh client-side plus call revoke endpoint. Test back-button does not resurrect session from cache.

#### Scenario probe
**Situation:** EazyBank adds Google login; React devs call Google token endpoint from browser with client secret in `.env` committed to git.

**Model answer:** Rotate secret immediately; move to BFF or Keycloak broker. Browser is public client — PKCE only, no secret. Gitleaks in CI blocks commits. Architecture review: all OAuth exchanges server-side or via IdP broker. Pen test before marketing campaign. Customer comms if repo was public.

#### Code / config (when useful)

```yaml
spring:
  security:
    oauth2:
      client:
        registration:
          google:
            client-id: ${GOOGLE_CLIENT_ID}
            client-secret: ${GOOGLE_CLIENT_SECRET}
            scope: openid, profile, email
        provider:
          google:
            issuer-uri: https://accounts.google.com
```

```java
http.oauth2Login(o -> o.successHandler((req, res, auth) -> {
    // link or create EazyBank customer, establish session
}));
```

---

### 88. Keycloak as Authorization Server — realms, clients, roles, integrating Spring Resource Server.

**Short answer:** Keycloak realm is isolated tenant (EazyBank prod vs dev). Clients represent apps (SPA public, microservice confidential). Realm roles and client roles map to JWT claims. Spring integrates via `issuer-uri` pointing to `https://<host>/realms/<realm>`. Admin console manages users, brokers Google, themes, brute-force policies — production IdP without building SAS.

#### What it is
EazyBank runs Keycloak cluster for OIDC/OAuth2 across 12 microservices and React SPA. Realm `eazybank` holds customers and employees as separate user federations or groups. Each microservice is resource server client with audience mapper.

#### How it works (internals)
Realm exports JSON for GitOps. Client: `eazybank-ui` public with PKCE, `accounts-service` bearer-only or confidential for service accounts. Roles: `customer`, `teller` assigned realm-wide; fine scopes as client roles `accounts:read`. Protocol mappers add `customer_id` to access token. Spring `issuer-uri` validates against realm certs. Service account client credentials for batch jobs. Keycloak authorization services optional for policy UMA — many banks use app-level `@PreAuthorize` instead.

#### When to use / when NOT to use
Keycloak when you need admin UI, federation, HA IdP quickly. Not when ultra-lightweight edge auth suffices. SAS when embedding auth in same deployment pipeline without separate ops team — see Q89. Always separate realms per environment — never share prod realm with dev.

#### Production example
EazyBank Keycloak on K8s with Postgres, 3-node Infinispan cache. Realm roles synced from HR LDAP for tellers. `accounts-service` YAML `issuer-uri: https://auth.eazybank.com/realms/eazybank`. Client scope `accounts:read` required for `/api/accounts`. DR drill: realm export restore under 30 minutes RTO.

#### Common mistakes
- Bearer-only client misconfigured — token exchange fails for service accounts.
- Public client with "Client authentication ON" — breaks PKCE SPA.
- Roles not in access token — only ID token — microservices 403.
- Single realm for prod and UAT — UAT token works on prod API.

#### Interview follow-ups (with model answers)

**Q:** Steps to onboard a new microservice to Keycloak?
**A:** Create client `loan-api` bearer-only or confidential, enable service accounts if needed, define client roles/scopes, add audience mapper to access token, configure Spring `issuer-uri` and audience validator, assign realm roles to users/groups, export realm JSON to Git, add integration test with Testcontainers Keycloak or `@MockBean JwtDecoder`. Document required scopes per endpoint in OpenAPI.

**Q:** Keycloak HA and session affinity?
**A:** Production: multiple Keycloak pods, shared database, Infinispan distributed cache for sessions. Sticky sessions less critical for JWT resource servers (stateless). Admin console changes propagate via DB — cache invalidation matters. Backup realm exports nightly. Monitor login error rate and brute-force lockouts.

**Q:** How separate customer vs employee identities?
**A:** Separate realms (`eazybank-customers`, `eazybank-staff`) or single realm with top-level groups and auth flows (browser flow with MFA for staff). Customers get Google broker; staff get SAML corporate IdP. JWT `azp` or `groups` claim drives route policies. Cross-realm token rejected by resource server issuer check.

#### Scenario probe
**Situation:** New EazyBank intern enables "Full Scope Allowed" on public SPA client "for easier dev" — reaches production config drift.

**Model answer:** Critical misconfiguration — any token for UI client carries all scopes including admin. Remediation: disable full scope, assign explicit client scopes minimum `openid accounts:read`, enable client policy enforcement, audit Keycloak config with Terraform/keycloak-config-cli in CI. Rotate all active tokens. Incident review: prod realm changes only via pipeline, dev uses separate realm. Spring services still validate audience/scopes — defense in depth.

#### Code / config (when useful)

```yaml
spring:
  security:
    oauth2:
      resourceserver:
        jwt:
          issuer-uri: https://auth.eazybank.com/realms/eazybank
# Keycloak client: audience mapper -> accounts-api
```

---

### 89. Spring Authorization Server (SAS) vs Keycloak — build vs buy for internal APIs.

**Short answer:** Spring Authorization Server is embeddable OAuth2/OIDC server in your JVM app — full control, same release train as Boot services, ops burden on your team. Keycloak is productized IdP with UI, federation, HA patterns — faster for heterogeneous clients. For EazyBank internal service-to-service only, SAS or managed cloud IdP; for customer-facing login + social + admin UI, Keycloak/Azure AD B2C wins.

#### What it is
Build-vs-buy for token issuance. SAS (`spring-authorization-server`) implements authorization code, client credentials, refresh, OIDC — you host and harden it. Keycloak ships user management, themes, brute-force, LDAP/Kerberos federation.

#### How it works (internals)
SAS: `@Configuration` `AuthorizationServerSettings`, registered clients in DB, `JWKSource` for signing keys, integrates with Spring Security filter chains at `/oauth2/token`. Keycloak: WAR/Quarkus distro, realm JSON, admin REST API. SAS fits "auth microservice" in mesh; Keycloak fits enterprise IAM hub. SAS 1.3+ on Spring Security 6; migration from deprecated Spring Security OAuth project complete.

#### When to use / when NOT to use
SAS: small org, all Spring, internal APIs, want minimal moving parts, team owns security patching. Keycloak: multiple tech stacks, need GUI user admin, social brokers, compliance asks for COTS IdP. Neither: use Auth0/Okta/Cognito when cloud managed acceptable. Avoid SAS if you need SAML legacy tomorrow without building it.

#### Production example
EazyBank internal ledger APIs used SAS in one cluster — 3 pods, Postgres client store, GitOps for registered clients. Customer channel on Keycloak for UX and Google login. SAS team on-call rotation merged with payments team; Keycloak owned by platform IAM. SAS saved license cost; cost 2 FTE ops vs Keycloak 0.5 FTE with vendor support contract.

#### Common mistakes
- SAS in every microservice — anti-pattern; one auth service only.
- Underestimating Keycloak JVM/memory footprint on small clusters.
- No HA plan for SAS — single pod becomes outage for all logins.
- Choosing SAS to "avoid Keycloak complexity" then rebuilding user admin UI.

#### Interview follow-ups (with model answers)

**Q:** What does SAS implement that you must build yourself vs Keycloak bundled?
**A:** SAS gives OAuth2/OIDC endpoints, client registration API, JWK rotation hooks — you build user store UI, federation, password policies, rate limiting, geo-blocking, admin audit GUI. Keycloak includes those plus themes and account management console. SAS customization is Java config; Keycloak is SPIs and themes. Compliance questionnaires often favor Keycloak's established track record unless SAS deployment documented with same controls.

**Q:** Can EazyBank run both SAS and Keycloak?
**A:** Yes — common split: Keycloak customer realm issues tokens; internal mesh trusts both issuers during migration via `authenticationManagerResolver`. Long term one issuer reduces client confusion. Token exchange between them is possible but adds complexity — prefer single issuer per audience.

**Q:** Licensing and support considerations?
**A:** SAS Apache 2.0 — no license fee; engineering time is cost. Keycloak open source + Red Hat build for support SLA. Banking procurement may require supported product for IdP tier. Document RACI: who patches CVE in auth tier within 72 hours.

#### Scenario probe
**Situation:** CTO asks team to replace Keycloak with SAS in 6 weeks to "reduce infrastructure" while keeping Google login, teller LDAP, and customer self-registration.

**Model answer:** Scope mismatch — SAS does not replace Keycloak features out of box. Estimate: SAS endpoints 4 weeks, user admin UI 8+ weeks, Google federation custom 4 weeks, LDAP 2 weeks, HA hardening ongoing. Recommend keep Keycloak for customer/employee identity; optional SAS only for machine clients if license driver. Present TCO: FTE vs Keycloak ops cost. Phased: SAS for `batch-*` client credentials only. Risk: failed login project blocks all channels.

#### Code / config (when useful)

```java
@Configuration
@EnableWebSecurity
public class AuthorizationServerConfig {
    @Bean
    @Order(Ordered.HIGHEST_PRECEDENCE)
    SecurityFilterChain authServerSecurity(HttpSecurity http) throws Exception {
        OAuth2AuthorizationServerConfiguration.applyDefaultSecurity(http);
        return http.getOrBuild();
    }
}
```

---

### 90. CSRF for session apps vs stateless JWT APIs — when `csrf().disable()` is acceptable.

**Short answer:** CSRF protects cookie-authenticated browsers from forged mutating requests — attacker site triggers victim browser to send session cookie. Stateless JWT in `Authorization` header is not automatically attached by browser — CSRF risk lower. `csrf().disable()` acceptable for pure Bearer-token APIs with no session cookies; never disable for cookie-session SPA or form login without alternative CSRF defense.

#### What it is
Cross-site request forgery threat model difference between EazyBank classic servlet session teller app and React+JWT accounts API. Spring's `CsrfFilter` expects token on POST/PUT/DELETE for session auth.

#### How it works (internals)
CSRF token in session or cookie `XSRF-TOKEN` mirrored to header `X-XSRF-TOKEN`. `CookieCsrfTokenRepository.withHttpOnlyFalse()` for SPA JS read. Double-submit cookie pattern. JWT APIs: browser does not attach `Authorization` on cross-origin form submit unless attacker JS runs — that's XSS, not CSRF. Hybrid BFF: HttpOnly session cookie + CSRF required — do not disable. `csrf().ignoringRequestMatchers("/api/webhook/**")` for HMAC-signed webhooks only.

#### When to use / when NOT to use
Disable CSRF: stateless REST with Bearer only, no cookies, mobile native APIs. Enable CSRF: session cookies, `JSESSIONID`, remember-me, Spring Security form login. SPA with cookie auth on BFF — enable CSRF. "We're HTTPS so safe" — wrong threat.

#### Production example
EazyBank accounts API (JWT): `csrf.disable()`, CORS allowlist. Teller BFF (session cookie): CSRF token in meta tag, React `axios` default header. Pen test flagged CSRF disabled on `/api/teller/transfer` — investigation found session cookie still used; re-enabled CSRF, 403 without header — incident prevented.

#### Common mistakes
- Disable CSRF because "API" while `oauth2Login` session cookie active.
- CSRF disabled + `SameSite=None` session cookie without other defenses.
- Webhook endpoints CSRF-exempt without HMAC signature verification.
- Copying `csrf().disable()` from JWT tutorial into BFF cookie app.

#### Interview follow-ups (with model answers)

**Q:** How configure CSRF for React + Spring session BFF?
**A:** `CookieCsrfTokenRepository.withHttpOnlyFalse()`, expose token via `CsrfTokenRequestAttributeHandler` and response header `X-XSRF-TOKEN`. React reads cookie or header on bootstrap, sends `X-XSRF-TOKEN` on mutating requests with `credentials: 'include'`. Test with MockMvc `csrf()` post-processor. Spring Security 6 lambda: `http.csrf(csrf -> csrf.csrfTokenRepository(CookieCsrfTokenRepository.withHttpOnlyFalse()))`.

**Q:** Double-submit cookie vs synchronizer token pattern?
**A:** Synchronizer stores token server session — stronger binding. Double-submit sets readable cookie + header must match — stateless-friendly for SPA. Banking BFF often uses synchronizer in server session for teller apps. Double-submit vulnerable if attacker controls subdomain cookie — scope cookies with `__Host-` prefix and strict Path.

**Q:** GraphQL POST with JWT — CSRF?
**A:** Bearer in header — disable CSRF OK. GraphQL over cookie session — enable CSRF on POST `/graphql`. Same-origin policy not sufficient — CSRF is cross-site with cookies sent. Document in API security baseline per transport.

#### Scenario probe
**Situation:** EazyBank merges JWT mobile API and cookie-based teller portal into one `SecurityFilterChain` with `csrf().disable()` globally.

**Model answer:** Teller portal vulnerable — attacker's site POSTs transfer using victim's session cookie. Split chains: `@Order(1)` `/api/mobile/**` stateless JWT csrf off; `@Order(2)` `/teller/**` session csrf on. Or uniform BFF with CSRF for all browser routes. Add ZAP CSRF scan in CI for teller URLs. Hotfix: enable CSRF on session matcher immediately.

#### Code / config (when useful)

```java
// JWT API chain
http.securityMatcher("/api/**")
    .csrf(csrf -> csrf.disable())
    .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS));

// BFF session chain
http.securityMatcher("/teller/**")
    .csrf(Customizer.withDefaults())
    .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.IF_REQUIRED));
```

---

### 91. CORS configuration — `CorsConfigurationSource`, preflight, credentials with cookies.

**Short answer:** CORS is browser-enforced cross-origin policy — server returns `Access-Control-Allow-Origin` (specific origin, not `*` with credentials), methods, headers. `CorsConfigurationSource` bean registers rules per path. Preflight `OPTIONS` must succeed before SPA sends `Authorization` or cookies with `credentials: 'include'`. Misconfigured CORS blocks EazyBank React dev and prod; overpermissive CORS is not auth bypass but aids attacker origins.

#### What it is
React `localhost:3000` or `https://app.eazybank.com` calling `https://api.eazybank.com`. Spring `CorsFilter` handles preflight. Separate from authentication — CORS only affects browsers, not curl/Postman.

#### How it works (internals)
Browser sends `OPTIONS` with `Access-Control-Request-Method` and headers. Server responds `204` with allowed origin. `allowCredentials(true)` requires explicit origin list — `*` illegal with credentials. `CorsConfigurationSource` via `http.cors(c -> c.configurationSource(source))`. `@CrossOrigin` on controllers for fine-grained — prefer central config for consistency. Gateway may set CORS instead of each service — avoid duplicate conflicting headers.

#### When to use / when NOT to use
Central `CorsConfigurationSource` for all `/api/**`. Allowlist prod + staging origins — never `*`. Do not rely on CORS alone for security. Server-to-server calls ignore CORS. WebFlux `CorsWebFilter` equivalent.

#### Production example
EazyBank: `allowedOrigins` `https://app.eazybank.com`, `https://staging.eazybank.com`, dev profile adds `http://localhost:3000`. `allowCredentials(true)` for BFF cookies. Bug: production only listed app origin but marketing subdomain `https://promo.eazybank.com` needed API — added via change request, not wildcard. Preflight cache `maxAge` 3600 reduces OPTIONS traffic.

#### Common mistakes
- `allowedOrigins("*")` with `allowCredentials(true)` — browser rejects all requests.
- JWT filter requires Authorization on OPTIONS — CORS preflight fails.
- Duplicate CORS headers from gateway and service — browser confusion.
- Forgetting `exposedHeaders` for `X-XSRF-TOKEN` read by SPA.

#### Interview follow-ups (with model answers)

**Q:** Spring Security 6 CORS bean example for SPA + cookies?
**A:** `CorsConfiguration cfg = new CorsConfiguration(); cfg.setAllowedOrigins(List.of("https://app.eazybank.com")); cfg.setAllowedMethods(List.of("GET","POST","PUT","DELETE","OPTIONS")); cfg.setAllowedHeaders(List.of("*")); cfg.setAllowCredentials(true); cfg.setExposedHeaders(List.of("X-XSRF-TOKEN")); UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource(); source.registerCorsConfiguration("/api/**", cfg);` Wire in `http.cors(c -> c.configurationSource(source))`. Test OPTIONS with MockMvc `options("/api/accounts").header("Origin", ...).header("Access-Control-Request-Method","GET")`.

**Q:** CORS at API gateway vs microservice?
**A:** Prefer gateway handles CORS once — services omit duplicate. Exception: multi-team mesh without unified gateway — each service allowlists same origins via shared config server YAML. Inconsistent lists cause "works in dev via gateway, fails direct service call" during debugging.

**Q:** Does CORS protect against stolen JWT?
**A:** No — CORS prevents browser scripts on evil.com reading responses from api.eazybank.com; attacker with token uses curl server-side. CORS is not API firewall. Still allowlist origins to reduce browser-based token exfiltration via XSS on lesser origins sharing API — narrow blast radius.

#### Scenario probe
**Situation:** EazyBank React staging shows "CORS error" on login after enabling `credentials: 'include'` — worked before with Bearer-only.

**Model answer:** Backend missing `Allow-Credentials: true` or origin not allowlisted. Fix `allowCredentials(true)` and exact staging origin — not `*`. Ensure `Set-Cookie` uses `SameSite=None; Secure` for cross-site cookie if SPA and API on different subdomains. Verify OPTIONS returns 200 without auth. JWT filter `shouldNotFilter` for OPTIONS. Document dev/staging/prod origin triple in config server.

#### Code / config (when useful)

```java
@Bean
CorsConfigurationSource corsConfigurationSource() {
    CorsConfiguration config = new CorsConfiguration();
    config.setAllowedOrigins(List.of("https://app.eazybank.com", "http://localhost:3000"));
    config.setAllowedMethods(List.of("GET", "POST", "PUT", "DELETE", "OPTIONS"));
    config.setAllowCredentials(true);
    config.setAllowedHeaders(List.of("Authorization", "Content-Type", "X-XSRF-TOKEN"));
    var source = new UrlBasedCorsConfigurationSource();
    source.registerCorsConfiguration("/api/**", config);
    return source;
}
```

---

### 92. Method security — `@PreAuthorize`, `@PostAuthorize`, SpEL, `@EnableMethodSecurity`.

**Short answer:** Method security adds authorization on `@Service`/`@Repository` methods after authentication — defense when HTTP path rules are insufficient or non-HTTP callers exist (`@Scheduled`, Kafka). Enable with `@EnableMethodSecurity`. `@PreAuthorize` checks before invoke; `@PostAuthorize` filters return value (e.g., account belongs to user). SpEL calls beans like `@authz.canViewAccount(#id)` — keep expressions testable and fast.

#### What it is
EazyBank `AccountService.getBalance(accountId)` — HTTP secured `/api/accounts/**` but scheduler and message listener also call service. `@PreAuthorize("hasRole('CUSTOMER') and @accountSecurity.isOwner(authentication.name, #accountId)")` enforces row-level security consistently.

#### How it works (internals)
`MethodSecurityInterceptor` AOP around methods. `@EnableMethodSecurity(prePostEnabled = true)` registers advisors. `SecurityContextHolder` supplies `Authentication` in SpEL as `authentication` or `@authentication`. `@PostAuthorize("returnObject.customerId == authentication.name")` prevents IDOR on returned DTO. `@PreFilter`/`@PostFilter` for collections. JDK proxy vs CGLIB — public methods on concrete classes required for CGLIB. `@Secured("ROLE_TELLER")` legacy — prefer `@PreAuthorize` for SpEL.

#### When to use / when NOT to use
Use for row-level and multi-channel authorization. HTTP rules for coarse `/api/admin/**`. Avoid heavy DB calls in SpEL every invocation — cache ownership or embed in JWT with short TTL for read paths. Do not `@PreAuthorize` on repositories if it causes self-invocation bypass — secure service layer.

#### Production example
EazyBank: `TransferService.initiate` requires `@PreAuthorize("@transferPolicy.allow(#req)")` bean calling rules engine. Teller override role bypasses amount limit via separate expression. Kafka consumer calls same service — method security blocks unsigned messages lacking system role. Tests: `@WithMockUser` + `@SpringBootTest` negative case IDOR account 12345 as wrong customer.

#### Common mistakes
- `@EnableMethodSecurity` missing — annotations no-op silently in prod.
- `private` `@PreAuthorize` methods — ignored by Spring AOP.
- SpEL calls external HTTP per request — latency and failure modes.
- Only HTTP security — `@Scheduled` job invokes service without user context → bypass.

#### Interview follow-ups (with model answers)

**Q:** Custom bean in SpEL for account ownership?
**A:** `@Component("accountSecurity") class AccountSecurity { boolean isOwner(String username, Long accountId) { return accountRepo.existsByIdAndCustomerEmail(accountId, username); } }` — `@PreAuthorize("@accountSecurity.isOwner(authentication.name, #accountId)")`. Unit test bean with mocked repo. Consider caching ownership 60s for read-heavy dashboards — invalidate on transfer. Log deny events for fraud analytics.

**Q:** `@PostAuthorize` vs filtering in controller?
**A:** `@PostAuthorize` centralizes authorization on return object — prevents service called from multiple controllers leaking data. Controller filter duplicates logic. `returnObject` SpEL works on entity/DTO. For collections, `@PostFilter("filterObject.customerId == authentication.principal.customerId")` — expensive on large lists; prefer query-level `WHERE customer_id = ?`.

**Q:** Test method security without full HTTP?
**A:** `@SpringBootTest` + `@EnableMethodSecurity` on test config, invoke service bean expecting `AccessDeniedException`. `@WithMockUser(roles="CUSTOMER")` sets context. For SpEL bean, `@MockitoBean AccountSecurity` when testing expression wiring. `@PreAuthorize` on controller works with `@WebMvcTest` + `spring-security-test`.

#### Scenario probe
**Situation:** EazyBank customer API passes pen test HTTP rules but analyst accesses another customer's account by guessing UUID in `GET /api/accounts/{id}` — controller returns 200.

**Model answer:** URL authenticated but no object-level check — classic IDOR. Add `@PreAuthorize("@accountSecurity.isOwner(authentication.name, #id)")` on service method controller calls. Repository query must include `customer_id` filter — defense in depth. Add automated test iterating customers cannot read neighbor IDs. Audit logs include denied `@PreAuthorize` evaluations. Optional: UUID alone insufficient — use non-guessable ids plus ownership.

#### Code / config (when useful)

```java
@Configuration
@EnableMethodSecurity(prePostEnabled = true)
class MethodSecurityConfig {}

@Service
class AccountService {
    @PreAuthorize("hasRole('CUSTOMER') and @accountSecurity.isOwner(authentication.name, #accountId)")
    public AccountDto getAccount(Long accountId) {
        return mapper.toDto(accountRepo.findById(accountId).orElseThrow());
    }
}
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

