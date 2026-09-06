# Design Patterns — 50 Senior Interview Questions

**Bar:** Name the pattern, draw it, then say when it **hurts**. Spring and microservices are pattern catalogs — interviewers expect that mapping.

---

### 1. What is a design pattern vs an architecture pattern vs a language feature?

**Short answer:** Design patterns (GoF) describe class/object collaboration at code level — Strategy, Factory, Observer. Architecture patterns operate at system scale — hexagonal, saga, CQRS. Modern Java language features (records, sealed types, streams) often replace boilerplate patterns. Seniors choose by intent and trade-offs, not UML nostalgia.

#### What it is
Patterns are reusable solutions to recurring problems in context. Design patterns live in one codebase; architecture patterns span services, data, and deployment. Language features can encode pattern intent directly.

#### How it works (internals)
GoF catalog (1994) predates DI frameworks, reactive stacks, and cloud-native patterns. Spring `@Transactional` is Proxy; Kafka is Observer evolved into log-based pub/sub. Records replace Builder for simple immutable DTOs. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss.

#### When to use / when NOT to use
Name the problem first: "I need interchangeable algorithms" → Strategy. "I need distributed transaction" → saga, not Singleton. Don't pattern-match every class to GoF.

#### Production example
Fee calculation: Strategy (map of calculators) not Interpreter — only four formulas. API versioning: anti-corruption layer at integration boundary, not Facade over entire monolith. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- "We use MVC" as architecture without explaining boundaries. Implementing Abstract Factory for `new ArrayList()`. Choosing CQRS for a 3-table CRUD app.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** Which GoF patterns does Spring embody?
**A:** Spring is a pattern runtime, not just DI. Proxy: `@Transactional`, `@Async`, `@Cacheable` via JDK/CGLIB. Factory: `@Bean` methods and `FactoryBean`. Singleton: default bean scope per context. Observer: `ApplicationEventPublisher`. Template Method: `JdbcTemplate`, `KafkaTemplate`. Chain of Responsibility: servlet and security filter chains. Strategy: conditional beans and handler maps. Seniors map framework features to patterns to debug proxies and ordering—not to recite GoF.

**Q:** When does a pattern become an anti-pattern?
**A:** When context changed but the solution stayed—complexity without reducing incidents. CQRS for three-table CRUD, sagas inside a monolith that needs local TX, or Kafka for 10 events/day are signals. Resume-driven architecture without boundary justification is common. Detection: deploy fear, unclear ownership, tests only on happy path. Senior response: name the anti-pattern, cite measurable pain (MTTR, defect rate), propose smaller fix.

**Q:** Enterprise patterns (Fowler) vs GoF?
**A:** GoF (1994) is object collaboration inside one process—Strategy, Observer, Proxy. Fowler's enterprise patterns address persistence and service layers—Repository, Unit of Work, Gateway. Microservices patterns (saga, outbox, CQRS) are system-scale. In interviews map Spring `@Transactional` to Proxy, `JdbcTemplate` to Template Method, and outbox to enterprise integration—not every problem is GoF.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving What is a design pattern vs an architecture pattern vs a language feature?. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: Design patterns (GoF) describe class/object collaboration at code level — Strategy, Factory, Observer.. Fee calculation: Strategy (map of calculators) not Interpreter — only four formulas. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```java
// Language feature replaces Visitor for simple cases
sealed interface Payment permits Card, Wire, Crypto {}
int fee(Payment p) {
    return switch (p) {
        case Card c -> cardFee(c);
        case Wire w -> wireFee(w);
        case Crypto c -> cryptoFee(c);
    };
}
```

---

### 2. Singleton — forms and why Spring made it boring.

**Short answer:** Singleton ensures one instance per scope. Forms: eager static, holder idiom, enum, DCL + volatile. Problems: hidden global state, test difficulty, classloader duplicates in app servers, serialization surprises. Spring's default singleton scope is one instance per container — prefer `@Bean` over hand-rolled singletons.

#### What it is
A creational pattern guaranteeing a single instance and global access point. In Spring, "singleton" means container-managed lifecycle, not JVM-global necessarily. At senior level, interviewers want the problem statement before the pattern name.

#### How it works (internals)
Holder idiom uses class-init lock. Enum singleton is serialization-safe. Spring creates one bean per context; multiple contexts (parent/child) can have duplicate "singletons." Framework defaults and proxy ordering change runtime behavior in ways unit tests miss.

#### When to use / when NOT to use
Don't write singletons in DI apps. Outside Spring (CLI tools, SDK internals), holder or enum. Never singleton for request-scoped or tenant state.

#### Production example
Legacy SDK exposes `ConnectionManager.getInstance()` — tests can't mock. Refactor to constructor injection of interface; Spring `@Bean` with test `@MockBean`. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- DCL without volatile. Storing mutable global state in singleton. Two WARs in app server → two singleton instances.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** Singleton vs static utility class?
**A:** Singleton controls instance lifecycle—one object, potentially mutable state, global visibility. Static utility classes have no instance; only stateless helpers belong there (e.g., formatting). In Spring apps prefer `@Bean` singleton scope over hand-rolled singletons—testable and container-managed. Enum singleton is serialization-safe for non-DI code. Static utilities cannot be mocked without bytecode tricks; constructor injection of an interface replaces both patterns in services.

**Q:** How to test singleton code?
**A:** Never test the singleton pattern itself—test behavior through injected interfaces. Refactor `getInstance()` callers to constructor injection; use `@MockBean` or plain mocks in unit tests. For legacy SDK singletons, wrap behind a port interface in an adapter and fake the port. Integration tests verify Spring wiring once; unit tests should not boot the container. If you must test holder idiom, reset state between tests or use dedicated test classloaders—usually a smell.

**Q:** Prototype scope in Spring?
**A:** Spring prototype creates a new bean per `getBean()` or per injection point when combined with scoped proxy—not a deep copy of object graphs. Injecting prototype into singleton gives one prototype instance at singleton creation unless you use `ObjectProvider` or `@Lookup` for per-call instances. Do not confuse with GoF Prototype deep-copy semantics. For per-request state in web apps, request scope with proxy is usually clearer than prototype hacks.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Singleton. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: Singleton ensures one instance per scope.. Legacy SDK exposes `ConnectionManager.getInstance()` — tests can't mock. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```java
public enum ConfigHolder {
    INSTANCE;
    public Properties get() { return props; }
}
```

---

### 3. Factory Method vs Abstract Factory vs Spring `FactoryBean`.

**Short answer:** Factory Method: subclass decides which product to instantiate (`createParser()`). Abstract Factory: family of related products (UI toolkit Win/Mac). Spring `@Bean` methods and `FactoryBean` are container-managed factories. Use when construction is non-trivial — SDK clients, strategy from config — not for `new ArrayList()`.

#### What it is
Creational patterns that encapsulate object creation. Factory Method defers to subclass; Abstract Factory creates product families without naming concrete classes. At senior level, interviewers want the problem statement before the pattern name.

#### How it works (internals)
Spring scans `@Configuration` classes, invokes `@Bean` methods once (singleton) or per lookup (prototype). `FactoryBean<T>` produces objects where the bean itself is a factory (`&beanName` for factory, `beanName` for product). Framework defaults and proxy ordering change runtime behavior in ways unit tests miss. Production debugging usually crosses logs, metrics, and condition reports—not just source code.

#### When to use / when NOT to use
Factory when: conditional implementation, complex init, hiding third-party types. Skip when constructor injection of a single concrete class is clear. Pick the smallest pattern that meets SLOs; over-abstraction becomes its own incident source.

#### Production example
```java @Bean PaymentGateway gateway(@Value("${payment.provider}") String provider) { return switch (provider) { case "stripe" -> new StripeGateway(props); case "mock" -> new MockGateway(); default -> throw new IllegalStateException(provider); }; } ``` We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- God factory with 50 `if/else` branches. Leaking concrete SDK types into domain layer.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** `ObjectProvider` vs `@Bean`?
**A:** On '`ObjectProvider` vs `@Bean`': anchor the answer in Factory Method vs Abstract Factory vs Spring `FactoryBean`.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Factory vs Builder?
**A:** Factory encapsulates which concrete type to instantiate—often one coherent product family from config (`PaymentGateway` from provider name). Builder constructs one complex object step-by-step with optional fields and validation at `build()`. Factory answers 'which implementation'; Builder answers 'how to assemble this instance safely'. Use Factory for strategy selection; Builder for 6+ optional DTO fields. Do not Factory a single `new ArrayList()`.

**Q:** How does Spring decide bean name?
**A:** Default bean name is the `@Bean` method name or decapitalized simple class name for `@Component`. `@Qualifier` or `@Primary` disambiguate collisions. `@Bean(name=...)` overrides explicitly. Two `@Bean` methods returning same type need qualifiers—otherwise `NoUniqueBeanDefinitionException` at startup (fail-fast). Custom `BeanNameGenerator` only for advanced scan scenarios.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Factory Method vs Abstract Factory vs Spring `FactoryBean`. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: Factory Method: subclass decides which product to instantiate (`createParser()`).. ```java @Bean PaymentGateway gateway(@Value("${payment.provider}") String provider) { return switch (provider) { case "stripe" -> new StripeGateway(props); case "mock" -> new MockGateway(); default -> throw new IllegalStateException(provider); }; } ``` I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```java
@Configuration
class ClientConfig {
    @Bean
    S3Client s3Client(AwsCredentialsProvider creds) {
        return S3Client.builder().credentialsProvider(creds).build();
    }
}
```

---

### 4. Builder — when records aren't enough.

**Short answer:** Builder constructs complex objects step-by-step with optional fields and validation at `build()`. Records excel at simple immutable data carriers; Builder wins with many optional parameters, cross-field validation, and immutable products with defaults. Lombok `@Builder` is convenient but allows nulls unless you validate.

#### What it is
Creational pattern separating construction from representation. Eliminates telescoping constructors. At senior level, interviewers want the problem statement before the pattern name.

#### How it works (internals)
Fluent API returns `this`; `build()` calls private constructor. Java records support compact constructors for validation but poor optional-field ergonomics without builder. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss. Production debugging usually crosses logs, metrics, and condition reports—not just source code.

#### When to use / when NOT to use
Builder: 6+ optional fields, immutable domain objects. Record: DTOs with all required fields. Don't Builder Hibernate entities — bypasses required invariants and lazy-loading assumptions.

#### Production example
`CheckoutRequest` with shipping, billing, promo, gift message — Builder validates "gift message requires gift flag" at build time. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- Mutable builder leaked and reused across threads. No validation in `build()` — invalid objects exist briefly.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** Builder vs telescoping constructors?
**A:** On 'Builder vs telescoping constructors': anchor the answer in Builder—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Records with `with*` copy methods?
**A:** On 'Records with `with*` copy methods': anchor the answer in Builder—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Step builder pattern?
**A:** On 'Step builder pattern': anchor the answer in Builder—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Builder. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: Builder constructs complex objects step-by-step with optional fields and validation at `build()`.. `CheckoutRequest` with shipping, billing, promo, gift message — Builder validates "gift message requires gift flag" at build time. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```java
Order order = Order.builder()
    .customerId(id)
    .lineItems(items)
    .promoCode(code)
    .build(); // validates here
```

---

### 5. Prototype vs `clone` vs copy constructor.

**Short answer:** Prototype pattern copies an existing instance instead of building from scratch. Java's `Cloneable` is widely considered broken (shallow copy, `clone()` on Object). Prefer copy constructors, factory methods, or MapStruct. Spring prototype scope creates new bean per `getBean()` — not a deep copy of mutable graphs.

#### What it is
Creational pattern: `newInstance` from prototype. Useful when object creation is expensive and variations are similar. At senior level, interviewers want the problem statement before the pattern name.

#### How it works (internals)
`Object.clone()` shallow-copies references — nested mutable state shared. Deep copy requires explicit logic. MapStruct generates mapping code at compile time. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss.

#### When to use / when NOT to use
Prototype for game entities, document templates. Copy ctor for domain value objects. Spring prototype for stateful per-request beans (rare).

#### Production example
Invoice template cloned per customer with `Invoice.copyFrom(template)` — deep copies line item list. Not `Object.clone()`. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- Assuming Spring prototype scope deep-clones dependencies. `Cloneable` without `super.clone()` contract.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** Deep vs shallow copy?
**A:** On 'Deep vs shallow copy': anchor the answer in Prototype vs `clone` vs copy constructor.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Serialization as clone?
**A:** On 'Serialization as clone': anchor the answer in Prototype vs `clone` vs copy constructor.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Prototype vs flyweight?
**A:** On 'Prototype vs flyweight': anchor the answer in Prototype vs `clone` vs copy constructor.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Prototype vs `clone` vs copy constructor. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: Prototype pattern copies an existing instance instead of building from scratch.. Invoice template cloned per customer with `Invoice.copyFrom(template)` — deep copies line item list. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```java
public Invoice(Invoice other) {
    this.id = UUID.randomUUID();
    this.lines = other.lines.stream().map(LineItem::copy).toList();
}
```

---

### 6. Adapter (your integration layer).

**Short answer:** Adapter converts one interface into another expected by clients. Your hexagonal "outbound adapter" wraps Stripe SDK behind `PaymentPort`. Keeps domain free of vendor types. Don't leak adapter DTOs into core domain.

#### What it is
Structural pattern for integrating incompatible APIs — legacy SOAP, third-party REST, cloud SDKs. At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
Adapter implements your port interface, delegates to adaptee, translates types and errors. Two forms: object adapter (composition) and class adapter (inheritance — rare in Java). Framework defaults and proxy ordering change runtime behavior in ways unit tests miss. Production debugging usually crosses logs, metrics, and condition reports—not just source code.

#### When to use / when NOT to use
Every external integration boundary. Not needed for internal modules sharing same model. ACL (anti-corruption layer) is adapter with translation logic.

#### Production example
`StripePaymentAdapter implements PaymentPort` — maps `ChargeRequest` to Stripe API, maps Stripe exceptions to domain `PaymentFailed`. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- Adapter that grows into god class with business logic. Exposing Stripe `PaymentIntent` in REST API.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** Adapter vs Facade?
**A:** On 'Adapter vs Facade': anchor the answer in Adapter (your integration layer).—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Hexagonal ports naming?
**A:** On 'Hexagonal ports naming': anchor the answer in Adapter (your integration layer).—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Testing adapters?
**A:** On 'Testing adapters': anchor the answer in Adapter (your integration layer).—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Adapter (your integration layer). Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: Adapter converts one interface into another expected by clients.. `StripePaymentAdapter implements PaymentPort` — maps `ChargeRequest` to Stripe API, maps Stripe exceptions to domain `PaymentFailed`. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```java
class StripeAdapter implements PaymentPort {
    private final StripeClient stripe;
    public Result pay(Money amount) {
        return map(stripe.charge(toStripe(amount)));
    }
}
```

---

### 7. Bridge vs Adapter.

**Short answer:** Adapter retrofits an existing incompatible interface. Bridge intentionally separates abstraction from implementation so both can vary independently (e.g., shape + renderer). Bridge is design-time; Adapter is integration-time. Bridge is rare in typical CRUD; common in drivers and graphics.

#### What it is
Bridge decouples interface hierarchy from implementation hierarchy. Adapter makes one class fit another's expected interface. At senior level, interviewers want the problem statement before the pattern name.

#### How it works (internals)
Bridge: `Abstraction` holds `Implementor` reference — composition. Adapter: wraps `Adaptee` to match `Target`. Intent differs: bridge for planned variation, adapter for legacy mismatch. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss.

#### When to use / when NOT to use
Bridge when you have two dimensions of change (notification channel × formatter). Adapter for every third-party SDK. Don't bridge a single implementation.

#### Production example
Notification system: `Notifier` bridge to `EmailSender`, `SmsSender` — swap senders without changing notifier API. Stripe integration is Adapter, not Bridge. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- Calling every wrapper an adapter. Over-abstracting one SMTP implementation as Bridge.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** Bridge vs Strategy?
**A:** On 'Bridge vs Strategy': anchor the answer in Bridge vs Adapter.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** JDBC DriverManager as bridge?
**A:** On 'JDBC DriverManager as bridge': anchor the answer in Bridge vs Adapter.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** When is Adapter enough?
**A:** On 'When is Adapter enough': anchor the answer in Bridge vs Adapter.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Bridge vs Adapter. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: Adapter retrofits an existing incompatible interface.. Notification system: `Notifier` bridge to `EmailSender`, `SmsSender` — swap senders without changing notifier API. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```java
abstract class Notifier {
    protected final MessageSender sender;
    Notifier(MessageSender sender) { this.sender = sender; }
}
```

---

### 8. Composite.

**Short answer:** Composite treats individual objects and compositions uniformly — tree structures where leaf and container share interface. Examples: UI components, org charts, file systems, rule trees. Operations recurse the tree. Watch stack overflow on deep trees; flatten for huge hierarchies.

#### What it is
Structural pattern for part-whole hierarchies. Client calls `operation()` on root without knowing leaf vs composite. At senior level, interviewers want the problem statement before the pattern name.

#### How it works (internals)
`Component` interface with `add`, `remove`, `getChildren` (optional on leaf — throws or no-op). Composite stores child list; leaf implements behavior directly. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss. Production debugging usually crosses logs, metrics, and condition reports—not just source code.

#### When to use / when NOT to use
Tree-structured domain: permissions, categories, approval chains. Not flat lists. For million-node trees, use adjacency list + iterative traversal, not deep recursion.

#### Production example
Product category tree: `Category` composite contains subcategories and products. `getTotalStock()` recurses. Admin UI renders same interface for leaf SKU and folder. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback.

#### Common mistakes
- Leaf implementing `addChild` that throws — API smell; consider separate interfaces. Unbounded recursion depth.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** Composite vs inheritance tree?
**A:** On 'Composite vs inheritance tree': anchor the answer in Composite.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Visitor on composite?
**A:** On 'Visitor on composite': anchor the answer in Composite.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Database storage for composite?
**A:** On 'Database storage for composite': anchor the answer in Composite.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Composite. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: Composite treats individual objects and compositions uniformly — tree structures where leaf and container share interface.. Product category tree: `Category` composite contains subcategories and products. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```java
interface OrgUnit {
    int headcount();
}
class Team implements OrgUnit { /* leaf */ }
class Department implements OrgUnit {
    List<OrgUnit> children;
    public int headcount() {
        return children.stream().mapToInt(OrgUnit::headcount).sum();
    }
}
```

---

### 9. Decorator vs Proxy vs Wrapper.

**Short answer:** Same structure (wrap interface), different intent. Decorator adds behavior (`BufferedInputStream`). Proxy controls access — lazy load, security, remote, logging (AOP). Wrapper is informal alias. Spring `@Transactional` is a proxy, not a decorator in GoF sense.

#### What it is
Structural patterns using composition to extend or mediate object behavior without subclass explosion. At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
Decorator and Proxy both implement same interface as delegate. Decorator chains multiple layers; Proxy often single-purpose gatekeeper. JDK dynamic proxy vs CGLIB subclass for Spring AOP. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss.

#### When to use / when NOT to use
Decorator for composable enhancements. Proxy for cross-cutting infrastructure. Don't subclass for every combination — prefer composition.

#### Production example
`CachingProductRepository` decorates `JpaProductRepository`. `@Cacheable` proxy adds cache layer via AOP — self-invocation skips proxy (classic bug). We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- Confusing naming — calling security filter a "decorator." Expecting `@Transactional` on private methods. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** Spring AOP proxy types?
**A:** On 'Spring AOP proxy types': anchor the answer in Decorator vs Proxy vs Wrapper.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Decorator vs subclass?
**A:** On 'Decorator vs subclass': anchor the answer in Decorator vs Proxy vs Wrapper.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Smart pointer proxy?
**A:** On 'Smart pointer proxy': anchor the answer in Decorator vs Proxy vs Wrapper.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Decorator vs Proxy vs Wrapper. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: Same structure (wrap interface), different intent.. `CachingProductRepository` decorates `JpaProductRepository`. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```java
class TimingDecorator implements Service {
    private final Service delegate;
    public Result call(Request r) {
        long t = System.nanoTime();
        try { return delegate.call(r); }
        finally { log(t); }
    }
}
```

---

### 10. How does Spring AOP relate to Proxy and Decorator?

**Short answer:** Spring AOP wraps beans in JDK dynamic proxies (interfaces) or CGLIB subclasses (classes) — a proxy chain of interceptors resembling decorators. `@Transactional`, `@Async`, `@Cacheable` are proxy-based advice. Limitations: no `final`/private methods, no same-class self-invocation. AspectJ weaving is compile/load-time alternative.

#### What it is
AOP applies cross-cutting concerns via proxies at runtime (default) or bytecode weaving (AspectJ). At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
`AnnotationAwareAspectJAutoProxyCreator` creates proxy. Interceptors form chain — each calls `invocation.proceed()`. Order matters (`@Order`). `@EnableAspectJAutoProxy(proxyTargetClass=true)` forces CGLIB.

#### When to use / when NOT to use
AOP for infra concerns (tx, cache, metrics). Business rules belong in domain code, not aspects — unless truly cross-cutting audit. Pick the smallest pattern that meets SLOs; over-abstraction becomes its own incident source.

#### Production example
Custom `@Timed` aspect records Micrometer metrics around `@RestController` methods. Transaction aspect opens/commits JDBC connection per service method. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- `this.internal()` bypasses proxy — inject self or split bean. Heavy logic in aspects — hard to test.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** AspectJ vs Spring AOP?
**A:** On 'AspectJ vs Spring AOP': anchor the answer in How does Spring AOP relate to Proxy and Decorator?—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** `exposeProxy=true` use case?
**A:** On '`exposeProxy=true` use case': anchor the answer in How does Spring AOP relate to Proxy and Decorator?—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Performance of proxy overhead?
**A:** On 'Performance of proxy overhead': anchor the answer in How does Spring AOP relate to Proxy and Decorator?—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving How does Spring AOP relate to Proxy and Decorator?. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: Spring AOP wraps beans in JDK dynamic proxies (interfaces) or CGLIB subclasses (classes) — a proxy chain of interceptors resembling decorators.. Custom `@Timed` aspect records Micrometer metrics around `@RestController` methods. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```java
@Aspect
@Component
class LoggingAspect {
    @Around("@annotation(Timed)")
    Object log(ProceedingJoinPoint pjp) throws Throwable {
        // decorator-like chain
        return pjp.proceed();
    }
}
```

---

### 11. Facade.

**Short answer:** Facade provides a simplified coarse API over a complex subsystem. `CheckoutFacade` orchestrates cart, inventory, payment. Microservices BFF is a facade pattern at network boundary. Risk: god facade re-centralizes monolith logic — keep facades thin, delegate to domain services.

#### What it is
Structural pattern reducing coupling between clients and many subsystem classes. Not a pass-through CRUD layer unless orchestration is real. At senior level, interviewers want the problem statement before the pattern name.

#### How it works (internals)
Facade knows subsystem APIs, sequences calls, aggregates errors. BFF adds aggregation, auth translation, response shaping for mobile vs web. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss. Production debugging usually crosses logs, metrics, and condition reports—not just source code.

#### When to use / when NOT to use
Multi-step workflows clients shouldn't know about. Not for every service layer — avoid anemic facade over one repository. Pick the smallest pattern that meets SLOs; over-abstraction becomes its own incident source.

#### Production example
Mobile BFF calls order, catalog, and user services; returns single `CheckoutView` DTO. Web may call services directly with GraphQL. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- Facade with business rules that belong in domain. Facade calling facade — distributed monolith.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** Facade vs API Gateway?
**A:** On 'Facade vs API Gateway': anchor the answer in Facade.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Facade vs Mediator?
**A:** On 'Facade vs Mediator': anchor the answer in Facade.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** When does BFF hurt?
**A:** On 'When does BFF hurt': anchor the answer in Facade.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Facade. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: Facade provides a simplified coarse API over a complex subsystem.. Mobile BFF calls order, catalog, and user services; returns single `CheckoutView` DTO. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```java
@Service
class CheckoutFacade {
    Result checkout(CheckoutCmd cmd) {
        reserveInventory(cmd);
        chargePayment(cmd);
        createOrder(cmd);
        return Result.ok();
    }
}
```

---

### 12. Flyweight.

**Short answer:** Flyweight shares intrinsic immutable state across many objects to save memory. Examples: `Integer.valueOf` cache, enum values, interned strings, font glyphs. Extrinsic state stays outside. Don't flyweight mutable objects or unbounded user-generated strings — memory leak.

#### What it is
Structural pattern for fine-grained object sharing when many instances differ only in extrinsic (context) state. At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
Factory maintains pool of flyweights keyed by intrinsic state. Client passes extrinsic state to methods. Thread-safe pool for concurrent access. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss.

#### When to use / when NOT to use
Large numbers of similar objects (game tiles, text rendering). Not for unique user records. Bounded, known intrinsic sets only.

#### Production example
Status code enum in API responses — shared instances. Custom intern pool for 20 known country codes, not for user emails. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- `String.intern()` on arbitrary user input — perm gen / heap pressure. Flyweight with mutable intrinsic state.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** Flyweight vs cache?
**A:** On 'Flyweight vs cache': anchor the answer in Flyweight.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Integer cache range?
**A:** On 'Integer cache range': anchor the answer in Flyweight.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Object pool vs flyweight?
**A:** On 'Object pool vs flyweight': anchor the answer in Flyweight.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Flyweight. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: Flyweight shares intrinsic immutable state across many objects to save memory.. Status code enum in API responses — shared instances. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```java
class GlyphFactory {
    private static final Map<Character, Glyph> cache = new ConcurrentHashMap<>();
    static Glyph get(char c) {
        return cache.computeIfAbsent(c, Glyph::new);
    }
}
```

---

### 13. Proxy types: virtual, remote, protection, smart.

**Short answer:** Virtual proxy delays expensive creation (Hibernate lazy load, `@Lazy` bean). Remote proxy stands in for network object (Feign client). Protection proxy enforces security. Smart proxy adds reference counting or caching. Hibernate bytecode enhancement is virtual proxy for lazy fields without subclassing entity.

#### What it is
Proxy subtypes by purpose — all control access to real subject. Spring and ORM use proxies extensively. At senior level, interviewers want the problem statement before the pattern name.

#### How it works (internals)
Virtual: load on first method call. Remote: serialize requests. Protection: check roles before delegate. JDK proxy requires interface; CGLIB subclasses concrete classes.

#### When to use / when NOT to use
Lazy load for large graphs — but fix N+1 with fetch joins in hot paths. Remote proxy auto-generated by OpenFeign. Don't double-proxy without reason.

#### Production example
`@Lazy PaymentService` breaks circular dependency at startup — proxy injected, real bean on first use. Feign `UserClient` is remote proxy. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- Lazy load in loop → N+1 queries. Assuming `@Lazy` fixes design — it's a band-aid.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** Hibernate lazy vs `@Lazy` Spring?
**A:** On 'Hibernate lazy vs `@Lazy` Spring': anchor the answer in Proxy types: virtual, remote, protection, smart.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Feign vs manual HTTP client?
**A:** On 'Feign vs manual HTTP client': anchor the answer in Proxy types: virtual, remote, protection, smart.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Proxy performance?
**A:** On 'Proxy performance': anchor the answer in Proxy types: virtual, remote, protection, smart.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Proxy types: virtual, remote, protection, smart. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: Virtual proxy delays expensive creation (Hibernate lazy load, `@Lazy` bean).. `@Lazy PaymentService` breaks circular dependency at startup — proxy injected, real bean on first use. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```java
@FeignClient(name = "users")
interface UserClient {
    @GetMapping("/users/{id}")
    UserDto get(@PathVariable String id);
}
```

---

### 14. Chain of Responsibility.

**Short answer:** Chain passes request along handlers until one processes it — servlet filters, Spring Security filter chain, logging pipelines. Order matters (`@Order`, `FilterRegistrationBean`). Don't chain two steps that should be one method. Failure mode: handler swallows request, no response.

#### What it is
Behavioral pattern decoupling sender from receivers. Each handler decides to process or pass to `next`. At senior level, interviewers want the problem statement before the pattern name.

#### How it works (internals)
Spring Security: `SecurityFilterChain` ordered list. Servlet spec: filter chain before `DispatcherServlet`. Each link calls `chain.doFilter()`. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss.

#### When to use / when NOT to use
Cross-cutting HTTP pipeline (auth, MDC, CORS). Not for simple if/else business routing — use Strategy. Keep chains fast; fail-closed on auth.

#### Production example
Custom filter chain: correlation ID → auth → rate limit → controller. Rate limit short-circuits with 429 without hitting controller. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- Wrong filter order (CORS after auth failure). Handler forgets to call `next` — silent drop.
- On-call sees symptoms two hops from root cause—correlation IDs and integration tests close that gap.
- Juniors optimize happy path; seniors design for rollback, idempotency, and observable failure modes.

#### Interview follow-ups (with model answers)

**Q:** Filter vs Interceptor vs Aspect?
**A:** On 'Filter vs Interceptor vs Aspect': anchor the answer in Chain of Responsibility.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** How to test filter chain?
**A:** On 'How to test filter chain': anchor the answer in Chain of Responsibility.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Gateway filters vs servlet filters?
**A:** On 'Gateway filters vs servlet filters': anchor the answer in Chain of Responsibility.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Chain of Responsibility. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: Chain passes request along handlers until one processes it — servlet filters, Spring Security filter chain, logging pipelines.. Custom filter chain: correlation ID → auth → rate limit → controller. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```java
@Component
@Order(1)
class CorrelationFilter extends OncePerRequestFilter {
    protected void doFilterInternal(...) {
        MDC.put("traceId", id);
        chain.doFilter(request, response);
        MDC.clear();
    }
}
```

---

### 15. Command.

**Short answer:** **Command** encapsulates a request as an object — enabling queueing, undo, audit, and deferred execution. At architecture scale, **CQRS commands** are the same idea: `PlaceOrderCommand` with a dedicated handler, not a void service method lost to history. `Runnable` is an impoverished command (no args, no undo). Store commands for replay only if you **version** the schema.

#### What it is
Behavioral pattern: `Command` interface with `execute()` (and optionally `undo()`); invoker triggers without knowing receiver details. Macro commands batch operations. CQRS command handlers are enterprise-scale commands.

#### How it works (internals)
Invoker → command → receiver. Thread pools and job queues execute command objects. Event sourcing may append commands as facts — overlap with Event pattern but commands express intent, events express outcome. Spring can map HTTP POST body to command record and dispatch to `@Service` handler method.

#### When to use / when NOT to use
Use when you need **audit trail**, async job queue, undo, or uniform handling of many operations. CQRS when write model complexity warrants explicit commands. Skip command objects for simple CRUD with no replay or queue requirement — don't wrap every setter.

#### Production example
Admin bulk price update: commands serialized to SQS with idempotency key; worker deserializes `UpdatePriceCommand` and executes handler; audit table stores who/when/what. Payment capture queued as command; failure retries without double charge when key dedupes at gateway. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- Commands with **side effects in constructor** — replay breaks. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.
- No **versioning** on stored commands after schema change — can't replay safely. On-call engineers see ambiguous errors because the symptom is two hops away from the root cause.
- Giant `switch(command.type)` god handler — use polymorphic handler map. The fix is usually explicit boundaries, fail-fast startup, and an integration test that asserts the negative case.
- Confusing **domain events** (past tense) with commands (intent). This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.

#### Interview follow-ups (with model answers)

**Q:** Command vs Event in event-driven architecture?
**A:** On 'Command vs Event in event-driven architecture': anchor the answer in Command.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** How do you implement undo without memento?
**A:** On 'How do you implement undo without memento': anchor the answer in Command.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Where does idempotency live — command or handler?
**A:** On 'Where does idempotency live — command or handler': anchor the answer in Command.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Command. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: **Command** encapsulates a request as an object — enabling queueing, undo, audit, and deferred execution.. Admin bulk price update: commands serialized to SQS with idempotency key; worker deserializes `UpdatePriceCommand` and executes handler; audit table stores who/when/what. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```java
public record PlaceOrderCommand(UUID cartId, IdempotencyKey key) {}

@Component
public class PlaceOrderHandler {
    @Transactional
    public OrderId handle(PlaceOrderCommand cmd) {
        /* execute + audit log */
        return orderId;
    }
}
```

---

### 16. Interpreter.

**Short answer:** **Interpreter** defines a grammar and evaluates sentences — regex engines, **SpEL**, SQL parsers, rule DSLs. Powerful for configurable business rules; dangerous when user input becomes code (**SpEL injection**, arbitrary eval). Don't build an interpreter for what SQL or a mature rules engine already solves.

#### What it is
Behavioral pattern: grammar symbols form an AST; each node implements `interpret(context)`. Composite often models expression trees. Industrial forms: ANTLR parsers, Drools, Spring Expression Language.

#### How it works (internals)
Lexer tokenizes input; parser builds AST; evaluator walks tree with context (variables, functions). Spring `@Value("#{...}")` and `@PreAuthorize` use SpEL interpreter. Sandbox with whitelisted functions and properties for user-facing rules. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss.

#### When to use / when NOT to use
Use when rules change frequently and controlled expression language beats redeploy — with security review. Avoid hand-rolled interpreters for four hardcoded `if` conditions — use Strategy. Never expose raw SpEL/Groovy on unsanitized user input.

#### Production example
Promo engine evaluates `"cart.total > 100 && region == 'EU'"` via sandboxed expression language with whitelisted properties only. Fraud rules DSL compiled to AST; hot path may compile to bytecode after validation. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- **SpEL injection** via user-controlled expression strings — RCE risk. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.
- Interpreter without **resource limits** — infinite loops in user rules. On-call engineers see ambiguous errors because the symptom is two hops away from the root cause.
- Reimplementing SQL reporting in custom interpreter. The fix is usually explicit boundaries, fail-fast startup, and an integration test that asserts the negative case.
- No tests for grammar edge cases — parse succeeds, semantics wrong. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.

#### Interview follow-ups (with model answers)

**Q:** Interpreter vs Strategy vs Specification?
**A:** On 'Interpreter vs Strategy vs Specification': anchor the answer in Interpreter.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** How do you secure SpEL in Spring?
**A:** On 'How do you secure SpEL in Spring': anchor the answer in Interpreter.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** When compile AST to bytecode instead of interpret?
**A:** On 'When compile AST to bytecode instead of interpret': anchor the answer in Interpreter.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Interpreter. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: **Interpreter** defines a grammar and evaluates sentences — regex engines, **SpEL**, SQL parsers, rule DSLs.. Promo engine evaluates `"cart.total > 100 && region == 'EU'"` via sandboxed expression language with whitelisted properties only. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```java
ExpressionParser parser = new SpelExpressionParser();
StandardEvaluationContext ctx = new StandardEvaluationContext();
ctx.setVariable("cart", cart);
Boolean ok = parser.parseExpression("total > 100").getValue(ctx, Boolean.class);
// Never: parseExpression(userSuppliedString) without strict sandbox
```

---

### 17. Iterator vs Stream vs Spliterator.

**Short answer:** **Iterator** is pull-based sequential access (`hasNext`/`next`). **Stream** is a declarative pipeline with lazy intermediate ops and terminal reduction. **Spliterator** splits sources for parallel streams and reports characteristics (ORDERED, SIZED). Fail-fast iterators vs concurrent collections — know what breaks when you mutate during traversal.

#### What it is
- **Iterator (GoF):** Traverse collection without exposing internal representation. - **Stream:** Functional operations — map/filter/collect; not a data structure. - **Spliterator:** Splitting API backing streams and parallel fork/join execution. At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
Iterator mutates cursor; `ConcurrentModificationException` on structural change during enhanced-for on `ArrayList`. Stream laziness: intermediate ops fuse until terminal `collect`/`forEach`. Spliterator `trySplit()` enables parallelism; `ORDERED` preserves encounter order. Don't reuse closed streams. Primitive streams avoid boxing.

#### When to use / when NOT to use
Iterator for manual control, legacy APIs, or custom collections. Stream for transformations and aggregation — clearer intent. Parallel stream only on **large**, CPU-bound, side-effect-free in-memory data. Avoid parallel in request handlers and on IO-bound work.

#### Production example
Export 500k rows: repository returns `Stream<Entity>` with fetch size; service method `@Transactional` consumes stream inside boundary; map to DTO, write CSV sequentially to preserve order and connection lifecycle. In-memory filter of 50 items — plain loop or stream, not `parallelStream()`. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- **Parallel stream** on shared mutable state — race conditions. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.
- Stream not closed when backed by JDBC/resource — leak. On-call engineers see ambiguous errors because the symptom is two hops away from the root cause.
- Exposing internal `List` iterator allowing external structural modification. The fix is usually explicit boundaries, fail-fast startup, and an integration test that asserts the negative case.
- `parallelStream()` in servlet thread for small lists — slower than loop. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.

#### Interview follow-ups (with model answers)

**Q:** Fail-fast vs fail-safe vs weakly consistent iterators?
**A:** On 'Fail-fast vs fail-safe vs weakly consistent iterators': anchor the answer in Iterator vs Stream vs Spliterator.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** When is parallel stream slower than sequential?
**A:** On 'When is parallel stream slower than sequential': anchor the answer in Iterator vs Stream vs Spliterator.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Custom `Spliterator` — what characteristics to set?
**A:** On 'Custom `Spliterator` — what characteristics to set': anchor the answer in Iterator vs Stream vs Spliterator.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Iterator vs Stream vs Spliterator. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: **Iterator** is pull-based sequential access (`hasNext`/`next`). **Stream** is a declarative pipeline with lazy intermediate ops and terminal reduction. **Spliterator** splits sources for parallel streams and reports characteristics (ORDERED, SIZED).. Export 500k rows: repository returns `Stream<Entity>` with fetch size; service method `@Transactional` consumes stream inside boundary; map to DTO, write CSV sequentially to preserve order and connection lifecycle. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```java
try (Stream<Order> orders = orderRepository.streamByStatus(Status.OPEN)) {
    orders.map(this::toDto).forEach(csvWriter::write);
}
// Document contract: stream must be consumed inside transaction/session
```

---

### 18. Mediator.

**Short answer:** **Mediator** centralizes communication between colleagues so they don't reference each other directly — air-traffic control for UI widgets or chat rooms. **Spring `ApplicationEventPublisher`** acts as an in-process mediator for domain events. Risk: the mediator becomes a **god object** that owns everyone's routing and business rules.

#### What it is
Behavioral pattern: colleagues send messages to a mediator; mediator dispatches to the right handler. Reduces N×N coupling to N×1 compared to peers calling each other directly. At senior level, interviewers want the problem statement before the pattern name.

#### How it works (internals)
Colleagues register with or inject the mediator. Spring's event bus: publisher publishes typed events; `@EventListener` methods receive them — synchronous by default, `@Async` for background. Kafka topics are mediators at system scale. Differs from Observer: observer list is on the subject; mediator is a separate hub.

#### When to use / when NOT to use
Use when many components interact in complex ways (wizard dialogs, cockpit UIs). Prefer **domain events with clear payloads** over a single mega-mediator class. At service boundaries, use the broker — don't duplicate in-process events and Kafka without a clear ownership line.

#### Production example
`OrderService` publishes `OrderPlacedEvent` after commit; inventory, email, and analytics listeners react without `OrderService` importing every downstream type. UI `DialogMediator` coordinates validation panels without cross-references between Swing/JavaFX components. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- Mediator accumulates **domain invariants** — should route, not rule. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.
- Synchronous listener chains on the HTTP thread — hidden latency graph. On-call engineers see ambiguous errors because the symptom is two hops away from the root cause.
- Circular events: A triggers B triggers A — infinite loops. The fix is usually explicit boundaries, fail-fast startup, and an integration test that asserts the negative case.
- Testing requires mocking the entire mediator instead of individual listeners. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.

#### Interview follow-ups (with model answers)

**Q:** Mediator vs Observer vs Event Bus — one line each?
**A:** On 'Mediator vs Observer vs Event Bus — one line each': anchor the answer in Mediator.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** When do you graduate from `ApplicationEvent` to Kafka?
**A:** On 'When do you graduate from `ApplicationEvent` to Kafka': anchor the answer in Mediator.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** How do you enforce listener ordering?
**A:** On 'How do you enforce listener ordering': anchor the answer in Mediator.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Mediator. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: **Mediator** centralizes communication between colleagues so they don't reference each other directly — air-traffic control for UI widgets or chat rooms. **Spring `ApplicationEventPublisher`** acts as an in-process mediator for domain events.. `OrderService` publishes `OrderPlacedEvent` after commit; inventory, email, and analytics listeners react without `OrderService` importing every downstream type. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```java
@Service
@RequiredArgsConstructor
public class OrderService {
    private final ApplicationEventPublisher events;
    @Transactional
    public void place(Order order) {
        orderRepository.save(order);
        events.publishEvent(new OrderPlacedEvent(order.id()));
    }
}
```

---

### 19. Memento.

**Short answer:** **Memento** captures object state for **restore/undo** without exposing internals — originator creates snapshots; caretaker stores history. **Event sourcing** stores events not snapshots, but periodic snapshots are mementos that speed replay. Long-lived mementos hurt when **serialization versions** drift across deploys.

#### What it is
Behavioral pattern: externalize state to a memento object; restore later. Caretaker should not mutate memento contents (immutable mementos preferred). At senior level, interviewers want the problem statement before the pattern name.

#### How it works (internals)
Originator copies internal fields to memento on `save()`; `restore(memento)` replaces state. Undo stacks push/pop mementos. Event sourcing rebuilds from events; snapshot at sequence N is a memento checkpoint. GDPR: mementos may contain PII — retention and encryption apply.

#### When to use / when NOT to use
Undo stacks, draft autosave, game checkpoints. Avoid serializing huge object graphs on every keystroke. Prefer append-only event log when audit and replay are first-class requirements.

#### Production example
Collaborative doc editor: memento every 30 seconds and per edit batch for undo. Ledger service: nightly balance snapshot memento so rebuilding from events completes under one second for statements. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- **Mutable memento** — caretaker or bug corrupts originator state. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.
- Java serialization mementos across **version upgrades** — `InvalidClassException` in prod. On-call engineers see ambiguous errors because the symptom is two hops away from the root cause.
- Unbounded undo history — memory leak in long sessions. The fix is usually explicit boundaries, fail-fast startup, and an integration test that asserts the negative case.
- Confusing memento export with **API DTO** sent to clients. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.

#### Interview follow-ups (with model answers)

**Q:** Memento vs Command undo — how do they combine?
**A:** On 'Memento vs Command undo — how do they combine': anchor the answer in Memento.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Snapshot strategy in event sourcing?
**A:** On 'Snapshot strategy in event sourcing': anchor the answer in Memento.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Immutable memento design in Java?
**A:** On 'Immutable memento design in Java': anchor the answer in Memento.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Memento. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: **Memento** captures object state for **restore/undo** without exposing internals — originator creates snapshots; caretaker stores history. **Event sourcing** stores events not snapshots, but periodic snapshots are mementos that speed replay.. Collaborative doc editor: memento every 30 seconds and per edit batch for undo. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```java
public final class Editor {
    private String text = "";
    public Memento save() { return new Memento(text); }
    public void restore(Memento m) { this.text = m.text(); }
    public record Memento(String text) {}
}
```

---

### 20. Observer vs Pub/Sub vs Kafka.

**Short answer:** **Observer** is in-process: subject maintains listeners and notifies on change — forget to unsubscribe and you leak. **Pub/Sub** adds a **broker/topic** between publishers and subscribers. **Kafka** is a durable partitioned log with consumer groups — replay, ordering per partition, and at-least-once semantics — not classic Observer. Don't expect in-process observer durability across transaction boundaries. At-least-once delivery and idempotent handlers are non-negotiable across service boundaries.

#### What it is
- **Observer (GoF):** One-to-many dependency; subject pushes updates. - **Pub/Sub:** Indirection via topic; publishers don't know subscribers. - **Kafka:** Distributed log; consumers track offsets; groups scale consumption horizontally. At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
Observer: `addListener` / `notify` — sync or async executor. Spring `ApplicationEvent` + `@EventListener`. Kafka: partitions, replication, rebalance on consumer join/leave. **Transactional outbox** bridges DB commit with Kafka publish. `@TransactionalEventListener(AFTER_COMMIT)` still isn't broker-durable if the JVM dies before publish.

#### When to use / when NOT to use
ApplicationEvent for same-JVM side effects that can be async. Kafka for cross-service integration, audit, replay, fan-out. Don't use observer for critical cross-service workflows without outbox. Don't use Kafka for trivial same-request callbacks — ops cost is real.

#### Production example
In-process: `OrderPlacedEvent` triggers email listener on async executor. Cross-service: order service writes outbox row in same TX; relay publishes to `orders.placed`; inventory and analytics consume with idempotent handlers keyed by `orderId`. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- **Listener leaks** in long-lived contexts or hot redeploy. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.
- Publishing to Kafka **before** DB commit — consumers see ghost data. On-call engineers see ambiguous errors because the symptom is two hops away from the root cause.
- Consumer **rebalance** during slow processing — duplicate or missed processing without idempotency. The fix is usually explicit boundaries, fail-fast startup, and an integration test that asserts the negative case.
- Treating Kafka like a fire-and-forget queue with no key design for ordering. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.

#### Interview follow-ups (with model answers)

**Q:** How does `@TransactionalEventListener` differ from `@EventListener`?
**A:** On 'How does `@TransactionalEventListener` differ from `@EventListener`': anchor the answer in Observer vs Pub/Sub vs Kafka.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Consumer group vs competing consumers vs fan-out?
**A:** On 'Consumer group vs competing consumers vs fan-out': anchor the answer in Observer vs Pub/Sub vs Kafka.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** At-least-once delivery — where does idempotency live?
**A:** On 'At-least-once delivery — where does idempotency live': anchor the answer in Observer vs Pub/Sub vs Kafka.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** On-call: orders show inconsistent state after a deploy affecting Observer vs Pub/Sub vs Kafka. Symptoms appear only under concurrent load; rollback is available but root cause is unclear.

**Model answer:** I start from: **Observer** is in-process: subject maintains listeners and notifies on change — forget to unsubscribe and you leak. **Pub/Sub** adds a **broker/topic** between publishers and subscribers. **Kafka** is a durable partitioned log with consumer groups — replay, ordering per partition, and at-least-once semantics — not classic Observer.. In-process: `OrderPlacedEvent` triggers email listener on async executor. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```java
@TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
public void onOrderPlaced(OrderPlacedEvent e) {
    kafkaTemplate.send("orders.placed", e.orderId().toString(), e);
}
```

---

### 21. State vs Strategy.

**Short answer:** **Strategy** swaps **interchangeable algorithms** (payment method, sorting). **State** changes **behavior as the object's lifecycle phase changes** — order NEW → PAID → SHIPPED with illegal transitions rejected. Strategy is usually injected; State transitions are often internal. A 400-line `if (status ==)` is a missing State pattern — or a sign you need an explicit state machine.

#### What it is
- **Strategy:** Context delegates to strategy interface; client picks algorithm at setup or runtime. - **State:** Object delegates to state object; transitions replace current state reference. Same structure (polymorphism); **intent** differs: algorithm vs lifecycle protocol. At senior level, interviewers want the problem statement before the pattern name.

#### How it works (internals)
State: `OrderContext.pay()` delegates to `DraftState` or `PaidState`; illegal ops throw or return errors. Strategy: `Map<FeeType, FeeCalculator>` with no transition graph. Sealed classes + switch are lightweight State in Java 21. Spring State Machine for complex workflows — often overkill for four states.

#### When to use / when NOT to use
Strategy when behavior variants are independent of object phase. State when **legal operations depend on lifecycle**. Simple enum + switch OK for three stable states. Don't import a state machine framework for a CRUD status column.

#### Production example
Order aggregate: `DraftState`, `PaidState`, `ShippedState` — `cancel()` only in Draft/Paid. Fee rules: Strategy map by product type — no state transitions, just dispatch. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- **Mutable singleton strategy** holding request state — thread safety bug. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.
- State transitions **not persisted** — restart loses phase. On-call engineers see ambiguous errors because the symptom is two hops away from the root cause.
- God `switch(status)` spanning the service layer — untestable. The fix is usually explicit boundaries, fail-fast startup, and an integration test that asserts the negative case.
- Confusing domain **state** with **saga orchestration** across services. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.

#### Interview follow-ups (with model answers)

**Q:** State pattern vs enum + exhaustive switch?
**A:** On 'State pattern vs enum + exhaustive switch': anchor the answer in State vs Strategy.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** When would Spring State Machine be justified?
**A:** On 'When would Spring State Machine be justified': anchor the answer in State vs Strategy.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** How is current state stored in event sourcing?
**A:** On 'How is current state stored in event sourcing': anchor the answer in State vs Strategy.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving State vs Strategy. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: **Strategy** swaps **interchangeable algorithms** (payment method, sorting). **State** changes **behavior as the object's lifecycle phase changes** — order NEW → PAID → SHIPPED with illegal transitions rejected.. Order aggregate: `DraftState`, `PaidState`, `ShippedState` — `cancel()` only in Draft/Paid. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```java
sealed interface OrderState permits Draft, Paid, Shipped {
    OrderState pay(Order o);
}
final class Draft implements OrderState {
    public OrderState pay(Order o) { /* charge */ return new Paid(); }
}
```

---

### 22. Strategy in Spring.

**Short answer:** Spring makes **Strategy** routine: interface + multiple `@Component` implementations, inject `List<Strategy>` or build a `Map<Key, Strategy>` for dispatch. Prefer registry map over `switch` on type strings. Watch **prototype vs singleton** if strategies hold mutable per-request fields.

#### What it is
Behavioral pattern via DI: algorithms as beans; runtime selection from config, request parameter, or enum key. At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
`@Autowired List<PaymentStrategy>` collects all implementations. Custom `@Bean` folds list into `Map<PaymentType, PaymentStrategy>`. `@Qualifier` and `@Primary` disambiguate. `@ConditionalOnProperty` selects impl per profile. Fail closed when key missing — don't silently default to wrong calculator.

#### When to use / when NOT to use
Add new variants without modifying existing classes (Open/Closed). Avoid strategy explosion — fifty one-liner classes may be one data-driven rules table. Don't strategy-wrap every method variant.

#### Production example
`Map<Country, TaxCalculator>` in checkout; new country = new `@Component` + tests; `CheckoutService` unchanged. Feature flag picks `LegacyPricingStrategy` vs `ExperimentalPricingStrategy` via `@ConditionalOnProperty`. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- **`switch` on class name** instead of enum key — fragile refactors. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.
- Mutable fields on **singleton** strategy — bleeds across requests. On-call engineers see ambiguous errors because the symptom is two hops away from the root cause.
- Missing strategy for new enum value — wrong default at runtime. The fix is usually explicit boundaries, fail-fast startup, and an integration test that asserts the negative case.
- Circular dependencies between strategies — extract shared helper. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.

#### Interview follow-ups (with model answers)

**Q:** `List` injection vs explicit Map `@Bean`?
**A:** On '`List` injection vs explicit Map `@Bean`': anchor the answer in Strategy in Spring.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** How do you test all strategies uniformly?
**A:** On 'How do you test all strategies uniformly': anchor the answer in Strategy in Spring.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Strategy vs Chain of Responsibility for validation?
**A:** On 'Strategy vs Chain of Responsibility for validation': anchor the answer in Strategy in Spring.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Strategy in Spring. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: Spring makes **Strategy** routine: interface + multiple `@Component` implementations, inject `List<Strategy>` or build a `Map<Key, Strategy>` for dispatch.. `Map<Country, TaxCalculator>` in checkout; new country = new `@Component` + tests; `CheckoutService` unchanged. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```java
@Component
public class FeeRegistry {
    private final Map<FeeType, FeeCalculator> byType;
    public FeeRegistry(List<FeeCalculator> all) {
        this.byType = all.stream().collect(toMap(FeeCalculator::type, identity()));
    }
    public FeeCalculator get(FeeType t) {
        return Optional.ofNullable(byType.get(t))
            .orElseThrow(() -> new IllegalArgumentException(t.name()));
    }
}
```

---

### 23. Template Method vs Callback vs Strategy.

**Short answer:** **Template Method** defines algorithm skeleton in a base class; subclasses override hooks — historical `JdbcTemplate` style. **Callback** passes a functional hook (`TransactionCallback`, `RowMapper`) — composition-friendly. **Strategy** swaps a whole algorithm object. Modern Java favors **composition** (Strategy/callback) over inheritance templates.

#### What it is
- **Template Method:** Inheritance — `final template()` calls overridable `hook()`. - **Callback:** Framework invokes your lambda at the variable step. - **Strategy:** Injected object replaces algorithm entirely. At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
Template Method: fragile base class — superclass changes break subclasses. Spring `JdbcTemplate`, `KafkaTemplate`, `RestTemplate` use callbacks for variable steps while framework owns resource lifecycle. Hibernate `Session.doWork(ConnectionCallback)` same idea. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss.

#### When to use / when NOT to use
Framework templates for infra (JDBC, messaging). Strategy + DI for domain algorithms. Avoid deep template inheritance trees in application code — prefer callbacks or strategy.

#### Production example
`jdbcTemplate.query(sql, rowMapper)` — template handles connection and cleanup; callback maps rows. Export pipeline uses `ExportStrategy` instead of subclassing `AbstractExporter` with twelve hook methods. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- Deep inheritance for **business rules** — tight coupling to base class. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.
- Callback throwing checked exceptions through lambdas — awkward APIs. On-call engineers see ambiguous errors because the symptom is two hops away from the root cause.
- Subclass overriding **non-hook** methods — breaks Liskov. The fix is usually explicit boundaries, fail-fast startup, and an integration test that asserts the negative case.
- Calling hook methods out of order from subclass. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.

#### Interview follow-ups (with model answers)

**Q:** Is `JdbcTemplate` Template Method or Callback?
**A:** On 'Is `JdbcTemplate` Template Method or Callback': anchor the answer in Template Method vs Callback vs Strategy.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Fragile base class — example?
**A:** On 'Fragile base class — example': anchor the answer in Template Method vs Callback vs Strategy.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** When is subclassing still justified in 2026?
**A:** On 'When is subclassing still justified in 2026': anchor the answer in Template Method vs Callback vs Strategy.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Template Method vs Callback vs Strategy. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: **Template Method** defines algorithm skeleton in a base class; subclasses override hooks — historical `JdbcTemplate` style. **Callback** passes a functional hook (`TransactionCallback`, `RowMapper`) — composition-friendly. **Strategy** swaps a whole algorithm object.. `jdbcTemplate.query(sql, rowMapper)` — template handles connection and cleanup; callback maps rows. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```java
jdbcTemplate.query(
    "select id, total from orders",
    (rs, row) -> new OrderSummary(rs.getLong("id"), rs.getBigDecimal("total")));
```

---

### 24. Visitor vs pattern matching on sealed types.

**Short answer:** **Visitor** adds operations across a stable type hierarchy via **double dispatch** — new operation = new visitor class. **Sealed types + switch** (Java 21) replace many visitors with exhaustive, readable dispatch. Keep Visitor when operations are added often, types are stable, and you want the compiler to force updates when types change.

#### What it is
Behavioral pattern: `element.accept(visitor)` calls `visitor.visitConcrete(this)`. Trade-off: new operations without changing elements vs new element types break all visitors. At senior level, interviewers want the problem statement before the pattern name.

#### How it works (internals)
Double dispatch resolves both runtime types. Sealed hierarchy + pattern matching: compiler checks exhaustiveness when permits are closed. AST compilers still use visitors; business DTO hierarchies often don't need them anymore. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss.

#### When to use / when NOT to use
Visitor for ASTs, document models, frequent new operations. Sealed switch for domain variants with few operations that evolve with types. Avoid visitor on DTOs that change every sprint.

#### Production example
Tax AST: `visit(AddExpr)`, `visit(MultExpr)` — new optimization pass = new visitor class. Payment method sealed interface: add `Wallet` → compiler lists missing switch cases. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- Visitor on **unstable hierarchy** — every new type breaks all visitors. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.
- Non-exhaustive switch without sealed — `default` swallows bugs. On-call engineers see ambiguous errors because the symptom is two hops away from the root cause.
- Visitor with side effects everywhere — hard to test and reason about. The fix is usually explicit boundaries, fail-fast startup, and an integration test that asserts the negative case.
- Using visitor because interviews expect it — sealed switch is idiomatic Java now. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.

#### Interview follow-ups (with model answers)

**Q:** Explain double dispatch in one sentence.?
**A:** On 'Explain double dispatch in one sentence.': anchor the answer in Visitor vs pattern matching on sealed types.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** When does Visitor still beat switch?
**A:** On 'When does Visitor still beat switch': anchor the answer in Visitor vs pattern matching on sealed types.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** What is the expression problem?
**A:** On 'What is the expression problem': anchor the answer in Visitor vs pattern matching on sealed types.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Visitor vs pattern matching on sealed types. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: **Visitor** adds operations across a stable type hierarchy via **double dispatch** — new operation = new visitor class. **Sealed types + switch** (Java 21) replace many visitors with exhaustive, readable dispatch.. Tax AST: `visit(AddExpr)`, `visit(MultExpr)` — new optimization pass = new visitor class. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```java
sealed interface Expr permits Add, Lit {}
record Add(Expr left, Expr right) implements Expr {}
record Lit(int value) implements Expr {}

int eval(Expr e) {
    return switch (e) {
        case Add(var l, var r) -> eval(l) + eval(r);
        case Lit(var v) -> v;
    };
}
```

---

### 25. Null Object.

**Short answer:** **Null Object** provides a do-nothing or safe-default implementation instead of `null` — `Collections.emptyList()`, no-op loggers, `Optional`-adjacent defaults. Eliminates null checks when absence is valid behavior. Don't use null object to **swallow errors** that should fail loudly — no-op payment gateway in prod is an incident.

#### What it is
Behavioral pattern: implement the interface with benign behavior; clients always invoke methods without null guards. At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
Prefer singleton immutable null objects. Spring injects no-op implementations via `@ConditionalOnProperty` for optional features. `Map.getOrDefault(key, NoOpTimer.INSTANCE)` avoids null returns. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss.

#### When to use / when NOT to use
Valid when missing feature is OK (analytics off in dev). Fail fast when missing payment provider or auth. Return `List.of()` instead of null from collection APIs.

#### Production example
Feature flag off: inject `NoOpAnalytics` — checkout code unchanged, no null checks. Optional audit sink uses null object in local profile; prod wires real Kafka publisher. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- Null object **hides misconfiguration** — prod silently drops payments. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.
- Allocating new no-op per call unnecessarily. On-call engineers see ambiguous errors because the symptom is two hops away from the root cause.
- Null object where **Optional** expresses missing data better. The fix is usually explicit boundaries, fail-fast startup, and an integration test that asserts the negative case.
- No-op that discards ERROR-level logs. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.

#### Interview follow-ups (with model answers)

**Q:** Null Object vs Optional vs sentinel values?
**A:** On 'Null Object vs Optional vs sentinel values': anchor the answer in Null Object.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Is `Collections.emptyList()` a Null Object?
**A:** On 'Is `Collections.emptyList()` a Null Object': anchor the answer in Null Object.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** How do you verify real impl is wired in prod?
**A:** On 'How do you verify real impl is wired in prod': anchor the answer in Null Object.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Null Object. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: **Null Object** provides a do-nothing or safe-default implementation instead of `null` — `Collections.emptyList()`, no-op loggers, `Optional`-adjacent defaults.. Feature flag off: inject `NoOpAnalytics` — checkout code unchanged, no null checks. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```java
public interface Notifier { void send(String msg); }
public enum NoOpNotifier implements Notifier {
    INSTANCE;
    public void send(String msg) {}
}
```

---

### 26. Object pool.

**Short answer:** **Object pool** reuses expensive-to-create objects — **JDBC pools**, HTTP client pools, thread pools. Pooling trades memory and complexity for latency caps and resource limits. Don't pool cheap JVM objects; pool **scarce external** resources with validation, eviction, and leak detection.

#### What it is
Creational/infra pattern: borrow → use → return. HikariCP, Apache HttpClient pool, `ExecutorService`. At senior level, interviewers want the problem statement before the pattern name.

#### How it works (internals)
Idle queue; borrow blocks or fails when exhausted; return resets state (`rollback`, clear MDC). Hikari housekeeper validates idle connections, max lifetime, leak detection threshold. Size pools from metrics — not copy-paste `maximumPoolSize=1000`. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss.

#### When to use / when NOT to use
Pool DB connections, sockets, threads, large buffers. Skip pooling DTOs and `StringBuilder` — allocation is cheap. Separate pools per dependency for bulkhead isolation.

#### Production example
Hikari `maximumPoolSize=20` per service instance; Feign HTTP pool per downstream host; batch job on dedicated executor so export doesn't starve API Tomcat threads. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- **Connection leak** — missing try-with-resources. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.
- Pool × instances **exceeds DB max_connections**. On-call engineers see ambiguous errors because the symptom is two hops away from the root cause.
- Returning **dirty** object to pool — stale state for next borrower. The fix is usually explicit boundaries, fail-fast startup, and an integration test that asserts the negative case.
- Treating Hibernate `Session` like a borrow-from-pool in app code. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.

#### Interview follow-ups (with model answers)

**Q:** Hikari tuning — what knobs matter?
**A:** On 'Hikari tuning — what knobs matter': anchor the answer in Object pool.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** How does leak detection work?
**A:** On 'How does leak detection work': anchor the answer in Object pool.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Object pool vs Flyweight?
**A:** On 'Object pool vs Flyweight': anchor the answer in Object pool.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Object pool. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: **Object pool** reuses expensive-to-create objects — **JDBC pools**, HTTP client pools, thread pools.. Hikari `maximumPoolSize=20` per service instance; Feign HTTP pool per downstream host; batch job on dedicated executor so export doesn't starve API Tomcat threads. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```yaml
spring:
  datasource:
    hikari:
      maximum-pool-size: 20
      connection-timeout: 3000
      leak-detection-threshold: 60000
```

---

### 27. Dependency Injection as a pattern.

**Short answer:** **Dependency Injection** implements **Inversion of Control** — dependencies supplied from outside rather than `new` inside the class. **Constructor injection** for required immutable deps; field injection harms tests. Circular dependencies signal design problems — fix with events or extracted collaborator, not `@Lazy` forever.

#### What it is
Hollywood principle: don't call us, we'll call you. Depend on abstractions; container wires implementations. Foundation of Spring and testable Java services.

#### How it works (internals)
Spring resolves `@Component` graph at startup (or `@Lazy`). `@Primary`, `@Qualifier`, `@Conditional` disambiguate. `ObjectProvider<T>` for lazy or optional lookup. Prototype bean in singleton graph — new instance per injection point.

#### When to use / when NOT to use
Inject collaborators in Spring services — never `new` infrastructure in domain. Manual `new` OK for value objects inside factories. Avoid service locator (`context.getBean()` everywhere).

#### Production example
`OrderService(PaymentPort payment, InventoryPort inventory, MeterRegistry metrics)` — final fields, trivial `@Mock` unit tests without Spring context. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- **Field injection** — non-final fields, hidden required deps. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.
- Optional `@Autowired` everywhere — null at runtime vs fail-fast startup. On-call engineers see ambiguous errors because the symptom is two hops away from the root cause.
- `@Lazy` band-aid on circular deps without refactoring. The fix is usually explicit boundaries, fail-fast startup, and an integration test that asserts the negative case.
- Injecting `JpaRepository` into controllers — boundary leak. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.

#### Interview follow-ups (with model answers)

**Q:** Constructor vs setter vs field — Spring recommendation?
**A:** On 'Constructor vs setter vs field — Spring recommendation': anchor the answer in Dependency Injection as a pattern.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Clean ways to break circular dependencies?
**A:** Boot 2.6+ disallows circular references by default—context refresh fails fast. Fixes: extract shared dependency, constructor refactor, `ObjectProvider`, or event decoupling. `@Lazy` is a band-aid. Kotlin `lateinit` does not remove the cycle. CI must use same `allow-circular-references` setting as production—never only in dev profile.

**Q:** `@Lazy` vs `ObjectProvider`?
**A:** On '`@Lazy` vs `ObjectProvider`': anchor the answer in Dependency Injection as a pattern.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Dependency Injection as a pattern. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: **Dependency Injection** implements **Inversion of Control** — dependencies supplied from outside rather than `new` inside the class. **Constructor injection** for required immutable deps; field injection harms tests.. `OrderService(PaymentPort payment, InventoryPort inventory, MeterRegistry metrics)` — final fields, trivial `@Mock` unit tests without Spring context. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```java
@Service
public class OrderService {
    private final PaymentPort payment;
    public OrderService(PaymentPort payment) { this.payment = payment; }
}
```

---

### 28. Repository vs DAO vs Active Record.

**Short answer:** **DAO** is table-oriented persistence. **Repository** is **aggregate-shaped** (DDD) — loads/saves consistency boundaries. **Active Record** merges entity and persistence — convenient in Rails, fights Hibernate **Unit of Work** in rich domains. Spring Data JPA generates repositories — still leaky if controllers call `JpaRepository` directly.

#### What it is
- **DAO:** CRUD on rows — `OrderDao.insert(row)`. - **Repository:** `OrderRepository.save(orderAggregate)` — domain language. - **Active Record:** `order.save()` on entity — anemic domain risk. At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
Spring Data proxy at runtime; query methods from names or `@Query`. Custom fragments for complex queries. Flush/detach semantics still leak ORM behavior into design discussions. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss.

#### When to use / when NOT to use
Repository per aggregate root in DDD services. DAO fine in simple JDBC apps. Avoid Active Record in Java when domain logic is non-trivial — persistence belongs in adapter.

#### Production example
`OrderRepository` loads order + line items as aggregate; `save` within one transaction. Read side uses separate JDBC projection DAO (CQRS lite) — not the same interface as write repository. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- Business rules in `@Query` — anemic domain + fat repository. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.
- `JpaRepository` in REST controller — N+1 and over-exposure. On-call engineers see ambiguous errors because the symptom is two hops away from the root cause.
- Generic god repository for entire schema. The fix is usually explicit boundaries, fail-fast startup, and an integration test that asserts the negative case.
- Returning `@Entity` as JSON with lazy associations. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.

#### Interview follow-ups (with model answers)

**Q:** Where do specifications live?
**A:** On 'Where do specifications live': anchor the answer in Repository vs DAO vs Active Record.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Repository vs DAO naming — does it matter?
**A:** On 'Repository vs DAO naming — does it matter': anchor the answer in Repository vs DAO vs Active Record.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Testing repositories without full integration DB?
**A:** On 'Testing repositories without full integration DB': anchor the answer in Repository vs DAO vs Active Record.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Repository vs DAO vs Active Record. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: **DAO** is table-oriented persistence. **Repository** is **aggregate-shaped** (DDD) — loads/saves consistency boundaries. **Active Record** merges entity and persistence — convenient in Rails, fights Hibernate **Unit of Work** in rich domains.. `OrderRepository` loads order + line items as aggregate; `save` within one transaction. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```java
public interface OrderRepository extends JpaRepository<Order, UUID> {
    @EntityGraph(attributePaths = "lines")
    Optional<Order> findWithLinesById(UUID id);
}
```

---

### 29. Unit of Work (Hibernate Session).

**Short answer:** **Unit of Work** tracks objects read/modified in a business transaction and **flushes once** at commit — Hibernate `Session` / JPA `EntityManager` inside `@Transactional`. Dirty checking avoids manual UPDATE per field. Don't open a session per loop iteration; don't share a session across threads.

#### What it is
Fowler enterprise pattern: register changes during a transaction; single commit coordinates persistence. Maps to ORM persistence context. At senior level, interviewers want the problem statement before the pattern name.

#### How it works (internals)
Identity map within session. Flush before query syncs DB. `@Transactional` binds session to thread in Spring. `clear()` detaches all — use in batch chunks. Read-only `@Transactional(readOnly=true)` optimizes read paths.

#### When to use / when NOT to use
One `@Transactional` per cohesive use case write. Avoid long transactions spanning user think time. Batch: chunk with flush/clear every N rows.

#### Production example
`transferFunds()` debits/credits in one transaction — single flush, atomic commit. Import job: new transaction every 50 rows to avoid huge persistence context. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- Session-per-operation in loop — slow, inconsistent. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.
- **`LazyInitializationException`** outside boundary. On-call engineers see ambiguous errors because the symptom is two hops away from the root cause.
- External HTTP inside long `@Transactional` — holds DB locks. The fix is usually explicit boundaries, fail-fast startup, and an integration test that asserts the negative case.
- `merge` vs `persist` confusion on detached graphs. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.

#### Interview follow-ups (with model answers)

**Q:** What triggers flush in Hibernate?
**A:** On 'What triggers flush in Hibernate': anchor the answer in Unit of Work (Hibernate Session).—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** How does read-only transaction help?
**A:** On 'How does read-only transaction help': anchor the answer in Unit of Work (Hibernate Session).—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Unit of Work vs Identity Map relationship?
**A:** On 'Unit of Work vs Identity Map relationship': anchor the answer in Unit of Work (Hibernate Session).—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Unit of Work (Hibernate Session). Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: **Unit of Work** tracks objects read/modified in a business transaction and **flushes once** at commit — Hibernate `Session` / JPA `EntityManager` inside `@Transactional`.. `transferFunds()` debits/credits in one transaction — single flush, atomic commit. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```java
@Transactional
public void transfer(UUID from, UUID to, Money amount) {
    var a = accounts.findById(from).orElseThrow();
    var b = accounts.findById(to).orElseThrow();
    a.debit(amount);
    b.credit(amount);
}
```

---

### 30. Identity Map.

**Short answer:** **Identity Map** ensures **one in-memory instance per id** inside a persistence context — why two `find` calls return `==` same reference. Breaks when mixing detached instances with managed ones; `merge` semantics confuse teams that don't understand the session boundary.

#### What it is
Fowler pattern: map id → object within Unit of Work. Hibernate first-level cache is identity map per session. At senior level, interviewers want the problem statement before the pattern name.

#### How it works (internals)
Session key `(EntityType, id)` → instance. Prevents duplicate inconsistent representations. Second-level cache shares across sessions with consistency trade-offs. Detached entity from prior request is different object until merged.

#### When to use / when NOT to use
Automatic in ORM — understand it, don't reimplement. Clear session in long batches to prevent map growth. Never rely on `==` across transactions or JVMs.

#### Production example
Same request: two helpers both `find(orderId)` — see same managed `Order`, dirty changes visible without re-fetch. Worker without session always explicit load. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- Confusing **`equals`** business equality with identity map identity. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.
- Storing managed entities in **static** map — leak across requests. On-call engineers see ambiguous errors because the symptom is two hops away from the root cause.
- `merge` while old detached copy still referenced in UI layer. The fix is usually explicit boundaries, fail-fast startup, and an integration test that asserts the negative case.
- Batch job without `clear()` — OOM from map size. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.

#### Interview follow-ups (with model answers)

**Q:** First-level vs second-level cache?
**A:** On 'First-level vs second-level cache': anchor the answer in Identity Map.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Why `==` in one session but not two?
**A:** On 'Why `==` in one session but not two': anchor the answer in Identity Map.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Identity map vs DTO projection queries?
**A:** On 'Identity map vs DTO projection queries': anchor the answer in Identity Map.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Identity Map. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: **Identity Map** ensures **one in-memory instance per id** inside a persistence context — why two `find` calls return `==` same reference.. Same request: two helpers both `find(orderId)` — see same managed `Order`, dirty changes visible without re-fetch. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```java
@Transactional
public void demo(EntityManager em) {
    Order a = em.find(Order.class, id);
    Order b = em.find(Order.class, id);
    assert a == b;
}
```

---

### 31. Lazy Load vs eager — pattern and trap.

**Short answer:** **Lazy loading** uses **virtual proxy** to defer association fetch until access. **Eager** loads immediately — cartesian product and slow queries. Trap: **N+1** and **`LazyInitializationException`** after session closes; fix with fetch join, `@EntityGraph`, or DTO query — not **OpenSessionInView** as a lifestyle.

#### What it is
ORM loading strategy: when to hit DB for associations. Lazy = proxy; eager = join or secondary select at load time. At senior level, interviewers want the problem statement before the pattern name.

#### How it works (internals)
Bytecode enhancement or JDK proxy on lazy associations. N+1: 100 orders + 100 customer queries. `@BatchSize` mitigates. `JOIN FETCH` loads in one query. OSIV keeps session open through view — masks design smell, ties DB to HTTP thread.

#### When to use / when NOT to use
Lazy default for collections. API layer: explicit fetch plan or DTO query per endpoint. Don't lazy-load in Kafka consumer after transaction ended.

#### Production example
List API: `@Query` with `join fetch o.customer`. Detail: entity graph. Removed OSIV; CI test fails on `LazyInitializationException` if boundary wrong. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback.

#### Common mistakes
- **`FetchType.EAGER`** on collections — accidental full graph. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.
- Global **OSIV** — long connections, hidden N+1. On-call engineers see ambiguous errors because the symptom is two hops away from the root cause.
- JSON serialization triggering lazy load — 500 in prod. The fix is usually explicit boundaries, fail-fast startup, and an integration test that asserts the negative case.
- Pagination + fetch join on collection — wrong row counts. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.

#### Interview follow-ups (with model answers)

**Q:** Explain N+1 with SQL counts.?
**A:** On 'Explain N+1 with SQL counts.': anchor the answer in Lazy Load vs eager—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** `@EntityGraph` vs `JOIN FETCH`?
**A:** On '`@EntityGraph` vs `JOIN FETCH`': anchor the answer in Lazy Load vs eager—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** When is eager correct?
**A:** On 'When is eager correct': anchor the answer in Lazy Load vs eager—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Lazy Load vs eager. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: **Lazy loading** uses **virtual proxy** to defer association fetch until access. **Eager** loads immediately — cartesian product and slow queries.. List API: `@Query` with `join fetch o.customer`. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```java
@Query("select o from Order o join fetch o.customer where o.status = :s")
List<Order> findOpenWithCustomer(@Param("s") Status status);
```

---

### 32. Circuit Breaker (Resilience4j).

**Short answer:** **Circuit breaker** stops calling a failing dependency after threshold — **Closed → Open → Half-open** probe. **Resilience4j** integrates with Spring Boot (`@CircuitBreaker`). Pair with **timeouts** and **bulkheads**; breaker with no fallback still yields bad UX if users only see opaque 500s. Tune breakers and retries from production metrics, not defaults—retry storms amplify outages.

#### What it is
Stability pattern: fail fast when dependency unhealthy; allow recovery probes. Not GoF — microservices resilience catalog. At senior level, interviewers want the problem statement before the pattern name.

#### How it works (internals)
Sliding window counts failures/slow calls. Open: fail immediately. Half-open: trial calls; success closes, failure reopens. Resilience4j registry + Micrometer metrics. Combine with `@TimeLimiter` for async caps.

#### When to use / when NOT to use
Wrap remote HTTP/gRPC dependencies — not local CPU methods. Tune from SLO data. Don't open breaker on DB without distinguishing transient blip vs sustained outage.

#### Production example
`@CircuitBreaker(name = "inventory", fallbackMethod = "fallback")` on Feign — open after 50% failures in 10s; fallback returns cached stock or degraded banner. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever. Tune breakers and retries from production metrics, not defaults—retry storms amplify outages.

#### Common mistakes
- Counting business **404** as failure — opens breaker wrongly. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.
- **Shared breaker name** across unrelated calls. On-call engineers see ambiguous errors because the symptom is two hops away from the root cause.
- Fallback hiding **zero inventory** dangerously. The fix is usually explicit boundaries, fail-fast startup, and an integration test that asserts the negative case.
- Half-open too aggressive — flapping. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.

#### Interview follow-ups (with model answers)

**Q:** Half-open — who decides success?
**A:** In Resilience4j, half-open allows a probe call after wait duration in open state—success closes breaker, failure reopens. Tune `permittedNumberOfCallsInHalfOpenState` and slow-call thresholds. Too aggressive half-open flaps during partner maintenance. Alert on state transitions; correlate with downstream 503 rate.

**Q:** Breaker vs retry — decorator order?
**A:** On 'Breaker vs retry — decorator order': anchor the answer in Circuit Breaker (Resilience4j).—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Tuning without production fire?
**A:** Tune sliding window size, failure rate threshold, slow-call duration, and wait in open state from metrics—not defaults. Exclude business 404 from failure counts. Name breakers per dependency, not globally. Run game days: open breaker deliberately and verify fallback UX. Document partner maintenance calendar to avoid flapping half-open probes.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Circuit Breaker (Resilience4j). Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: **Circuit breaker** stops calling a failing dependency after threshold — **Closed → Open → Half-open** probe. **Resilience4j** integrates with Spring Boot (`@CircuitBreaker`).. `@CircuitBreaker(name = "inventory", fallbackMethod = "fallback")` on Feign — open after 50% failures in 10s; fallback returns cached stock or degraded banner. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```java
@CircuitBreaker(name = "payments", fallbackMethod = "payFallback")
public PaymentResult charge(Money amount) { return client.charge(amount); }

private PaymentResult payFallback(Money amount, Throwable t) {
    return PaymentResult.degraded("payments unavailable");
}
```

```yaml
resilience4j.circuitbreaker.instances.payments:
  slidingWindowSize: 20
  failureRateThreshold: 50
  waitDurationInOpenState: 30s
```

---

### 33. Bulkhead.

**Short answer:** **Bulkhead** isolates resources so one failing compartment doesn't sink the ship — separate **thread pools**, semaphores, or connection pools per dependency. Tomcat threads vs async pool vs Hikari vs Feign limits are bulkheads when sized independently. One shared oversized pool lets one slow downstream block everything. Tune breakers and retries from production metrics, not defaults—retry storms amplify outages.

#### What it is
Resilience pattern: limit blast radius of overload. Hystrix thread pools per command; Resilience4j `@Bulkhead`. At senior level, interviewers want the problem statement before the pattern name.

#### How it works (internals)
Cap concurrent calls to dependency X; excess fails fast or queues with bound. K8s CPU/memory limits are pod-level bulkheads. Virtual threads still need backpressure on external IO. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss.

#### When to use / when NOT to use
Multiple downstream dependencies share JVM threads — size independently. Don't create fifty pools of size 1 — ops nightmare. Combine with timeout and circuit breaker.

#### Production example
Inventory limited to 30 concurrent via bulkhead; payment 20; reporting on separate executor — slow export doesn't exhaust API threads. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever. Tune breakers and retries from production metrics, not defaults—retry storms amplify outages.

#### Common mistakes
- **One giant Tomcat pool** — no isolation. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.
- Unbounded bulkhead queue — memory exhaustion. On-call engineers see ambiguous errors because the symptom is two hops away from the root cause.
- Ignoring rejections in metrics — silent failures. The fix is usually explicit boundaries, fail-fast startup, and an integration test that asserts the negative case.

#### Interview follow-ups (with model answers)

**Q:** Bulkhead vs rate limiter vs circuit breaker?
**A:** On 'Bulkhead vs rate limiter vs circuit breaker': anchor the answer in Bulkhead.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Virtual threads and bulkhead design?
**A:** On 'Virtual threads and bulkhead design': anchor the answer in Bulkhead.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Semaphore vs thread pool bulkhead?
**A:** On 'Semaphore vs thread pool bulkhead': anchor the answer in Bulkhead.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Bulkhead. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: **Bulkhead** isolates resources so one failing compartment doesn't sink the ship — separate **thread pools**, semaphores, or connection pools per dependency.. Inventory limited to 30 concurrent via bulkhead; payment 20; reporting on separate executor — slow export doesn't exhaust API threads. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```java
@Bulkhead(name = "inventory", type = Bulkhead.Type.SEMAPHORE)
public StockLevel checkStock(String sku) { return inventoryClient.getStock(sku); }
```

---

### 34. Retry with jitter vs amplifying outages.

**Short answer:** Blind **retries** during outages create **retry storms**. Use **exponential backoff + jitter**, **retry budgets**, and retry only **idempotent** operations (or with idempotency keys). Resilience4j `@Retry` needs max attempts and exception allowlist — not infinite `@Retryable`. Tune breakers and retries from production metrics, not defaults—retry storms amplify outages.

#### What it is
Resilience pattern: recover transient failures vs amplify sustained outages. Jitter desynchronizes retry waves (thundering herd on recovery). At senior level, interviewers want the problem statement before the pattern name.

#### How it works (internals)
Backoff 100ms, 200ms, 400ms + random jitter. Idempotency keys on POST. HTTP 429/503 with `Retry-After`. **Retry at one layer only** — app + mesh + client triples load. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss.

#### When to use / when NOT to use
Retry network blips on GET and idempotent writes. Don't retry 400 validation errors. Cap attempts; alert on budget exhaustion. Disable retries globally via flag during incidents.

#### Production example
Feign: max 3 attempts, 500ms + jitter, only `IOException` and 503. Payment POST sends `Idempotency-Key`; provider dedupes. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- Retry all **500** including overloaded DB. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.
- No jitter — synchronized waves. On-call engineers see ambiguous errors because the symptom is two hops away from the root cause.
- Retries in **service and gateway** — 9× attempts. The fix is usually explicit boundaries, fail-fast startup, and an integration test that asserts the negative case.
- Retry non-idempotent create without dedup — double charges. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.

#### Interview follow-ups (with model answers)

**Q:** Idempotency key storage — how long?
**A:** On 'Idempotency key storage — how long': anchor the answer in Retry with jitter vs amplifying outages.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** gRPC retry vs REST?
**A:** On 'gRPC retry vs REST': anchor the answer in Retry with jitter vs amplifying outages.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** When should Kafka consumer not retry?
**A:** On 'When should Kafka consumer not retry': anchor the answer in Retry with jitter vs amplifying outages.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Retry with jitter vs amplifying outages. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: Blind **retries** during outages create **retry storms**.. Feign: max 3 attempts, 500ms + jitter, only `IOException` and 503. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```yaml
resilience4j.retry.instances.inventory:
  maxAttempts: 3
  waitDuration: 500ms
  enableExponentialBackoff: true
  exponentialBackoffMultiplier: 2
  randomizedWaitFactor: 0.5
```

---

### 35. Saga (choreography vs orchestration).

**Short answer:** **Saga** coordinates **long-lived business transactions** across services via **local transactions + compensations** — no 2PC. **Choreography:** services react to events (loose, hard to trace). **Orchestration:** central conductor (clear flow, ops visibility). Real work: timeouts, idempotency, stuck-saga tooling, compensations that aren't perfect undo. At-least-once delivery and idempotent handlers are non-negotiable across service boundaries.

#### What it is
Architecture pattern: each step commits locally; failure runs compensating transactions. Temporal/Camunda for orchestration; events for choreography. At senior level, interviewers want the problem statement before the pattern name.

#### How it works (internals)
Happy path: order → reserve → charge → ship. Failure after charge: refund + release inventory. At-least-once messages + idempotent handlers. Orchestrator state machine vs event chains without correlation IDs.

#### When to use / when NOT to use
Multi-service processes without shared DB. Avoid saga inside single-service `@Transactional` workflow. Don't use XA 2PC across cloud microservices.

#### Production example
Choreography: `OrderPlaced` → inventory reserves; `PaymentCaptured` → shipping. Orchestration: `OrderSagaOrchestrator` with compensations; dashboard for stuck `AWAITING_PAYMENT > 1h`. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- **No compensation** — partial state forever. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.
- Compensating **un-shippable** physical goods — forward correction instead. On-call engineers see ambiguous errors because the symptom is two hops away from the root cause.
- Missing **timeout** — saga waits indefinitely. The fix is usually explicit boundaries, fail-fast startup, and an integration test that asserts the negative case.
- Choreography without **correlation id** — ops blind. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.

#### Interview follow-ups (with model answers)

**Q:** Saga vs 2PC vs outbox?
**A:** 2PC across microservices is fragile and rarely used in cloud-native stacks. Saga uses local TX + compensating steps—choreography or orchestration. Outbox solves reliable publish from one service's DB. Pick saga for multi-step business flows; outbox for single-writer event emission; avoid 2PC unless forced by legacy mainframe.

**Q:** Temporal — what problem does it solve?
**A:** Distributed sagas need explicit timeouts, correlation IDs, and compensations idempotent on replay. Choreography scales until stuck-state detection becomes weekly ops work—then add orchestrator or reconciliation cron. Never publish before local commit. Test compensation paths, not only happy path. Monitor per-step lag and DLQ depth.

**Q:** Testing compensations?
**A:** Distributed sagas need explicit timeouts, correlation IDs, and compensations idempotent on replay. Choreography scales until stuck-state detection becomes weekly ops work—then add orchestrator or reconciliation cron. Never publish before local commit. Test compensation paths, not only happy path. Monitor per-step lag and DLQ depth.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Saga (choreography vs orchestration). Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: **Saga** coordinates **long-lived business transactions** across services via **local transactions + compensations** — no 2PC. **Choreography:** services react to events (loose, hard to trace). **Orchestration:** central conductor (clear flow, ops visibility).. Choreography: `OrderPlaced` → inventory reserves; `PaymentCaptured` → shipping. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```java
public void run(OrderSaga saga) {
    try {
        inventory.reserve(saga.orderId());
        payment.charge(saga);
        saga.complete();
    } catch (Exception e) {
        compensation.refundIfNeeded(saga);
        compensation.releaseInventory(saga);
        saga.fail(e);
    }
}
```

---

### 36. Outbox / Transactional messaging.

**Short answer:** **Transactional outbox** writes business data and an **outbox row in the same DB transaction**; a relay publishes to Kafka — avoids **dual-write** (DB committed, message lost). Alternative: **CDC (Debezium)** streams WAL changes. Both beat publish-after-commit without atomicity. At-least-once delivery and idempotent handlers are non-negotiable across service boundaries.

#### What it is
Microservices pattern for reliable event publication: local consistency between state and message intent. At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
In TX: `INSERT order` + `INSERT outbox(payload)`. Relay polls or Debezium tails WAL; publish; mark sent. Idempotent consumers handle duplicates. `@TransactionalEventListener` alone doesn't survive crash before publish.

#### When to use / when NOT to use
Must atomically persist and notify others. Skip for loss-tolerant metrics. CDC when platform runs Kafka Connect; outbox table when app team owns relay.

#### Production example
Save order + outbox `OrderPlaced`; relay publishes with key=orderId; inventory idempotent on orderId. Debezium alternative on same table. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- Publish **before** commit — ghost orders. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.
- No consumer **idempotency** — duplicate shipments. On-call engineers see ambiguous errors because the symptom is two hops away from the root cause.
- Single-thread relay bottleneck without partition strategy. The fix is usually explicit boundaries, fail-fast startup, and an integration test that asserts the negative case.
- Huge payloads in outbox — store reference only. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.

#### Interview follow-ups (with model answers)

**Q:** Outbox vs inbox pattern?
**A:** On 'Outbox vs inbox pattern': anchor the answer in Outbox / Transactional messaging.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Debezium ordering per partition key?
**A:** On 'Debezium ordering per partition key': anchor the answer in Outbox / Transactional messaging.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Poison outbox row handling?
**A:** On 'Poison outbox row handling': anchor the answer in Outbox / Transactional messaging.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** On-call: orders show inconsistent state after a deploy affecting Outbox / Transactional messaging. Symptoms appear only under concurrent load; rollback is available but root cause is unclear.

**Model answer:** I start from: **Transactional outbox** writes business data and an **outbox row in the same DB transaction**; a relay publishes to Kafka — avoids **dual-write** (DB committed, message lost).. Save order + outbox `OrderPlaced`; relay publishes with key=orderId; inventory idempotent on orderId. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```java
@Transactional
public void placeOrder(Order order) {
    orders.save(order);
    outbox.save(new OutboxEvent("OrderPlaced", order.id(), toJson(order)));
}
```

---

### 37. CQRS.

**Short answer:** **CQRS** separates **command (write) model** from **query (read) model** — different shapes, stores, or scaling. Not always two databases; often separate projections and read-optimized queries while writes go through aggregates. Cost: **eventual consistency** and duplicated logic if undisciplined. Don't CQRS a three-table admin CRUD app.

#### What it is
Greg Young pattern: commands mutate; queries never mutate (ideally). Write side domain model; read side denormalized views. At senior level, interviewers want the problem statement before the pattern name.

#### How it works (internals)
Events or sync jobs update read store. Separate API endpoints or GraphQL resolvers. CQRS + Event Sourcing often paired but not mandatory. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss.

#### When to use / when NOT to use
Read/write load or shape diverges sharply — dashboards, search, high-write + heavy reads. Skip when one normalized schema serves both well. Pick the smallest pattern that meets SLOs; over-abstraction becomes its own incident source.

#### Production example
Write: `PlaceOrderCommand` → PostgreSQL normalized. Read: `OrderSummaryView` in Redis updated from `OrderPlaced` — list page never joins eight tables. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- Two models, **no sync strategy** — stale reads surprise users. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.
- CQRS excuse for **no domain model** on write side. On-call engineers see ambiguous errors because the symptom is two hops away from the root cause.
- Duplicated **validation** in read and write paths. The fix is usually explicit boundaries, fail-fast startup, and an integration test that asserts the negative case.

#### Interview follow-ups (with model answers)

**Q:** CQRS without event sourcing — viable?
**A:** On 'CQRS without event sourcing — viable': anchor the answer in CQRS.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** How stale can reads be?
**A:** On 'How stale can reads be': anchor the answer in CQRS.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Command vs query validation boundaries?
**A:** On 'Command vs query validation boundaries': anchor the answer in CQRS.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving CQRS. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: **CQRS** separates **command (write) model** from **query (read) model** — different shapes, stores, or scaling.. Write: `PlaceOrderCommand` → PostgreSQL normalized. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```java
@Service class OrderCommandService { /* mutate + emit */ }
@Repository class OrderSummaryDao {
    List<OrderSummaryRow> findForCustomer(UUID id); // read-optimized
}
```

---

### 38. Event Sourcing.

**Short answer:** **Event Sourcing** stores **events as the source of truth** and folds them into current state — audit and replay built in. Hard parts: **schema versioning**, GDPR erasure, snapshots, upcasters. Often "audit table + current state" is enough; full ES is rarely the default starting point.

#### What it is
Architecture pattern: append-only event log per aggregate; state = fold(events). Snapshots are performance mementos. At senior level, interviewers want the problem statement before the pattern name.

#### How it works (internals)
Commands produce events; event store append; projections rebuild read models. Upcasters migrate old event schemas. Competing consumers on projection topics. GDPR: tombstone events or crypto-shredding strategies — not trivial deletes.

#### When to use / when NOT to use
Audit, regulatory replay, complex temporal queries on history. Avoid for simple CRUD with no replay requirement — operational complexity is high. Pick the smallest pattern that meets SLOs; over-abstraction becomes its own incident source.

#### Production example
Bank account: `MoneyDeposited`, `MoneyWithdrawn` events; balance projection updated asynchronously; monthly snapshot speeds rebuild for statements. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- Events as **mutable** rows — destroys audit story. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.
- No **version** on event payload — can't replay after refactor. On-call engineers see ambiguous errors because the symptom is two hops away from the root cause.
- Projection lag with **no UX** for eventual consistency. The fix is usually explicit boundaries, fail-fast startup, and an integration test that asserts the negative case.
- Storing huge blobs in events — reference external storage. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.

#### Interview follow-ups (with model answers)

**Q:** Event sourcing vs audit log table?
**A:** On 'Event sourcing vs audit log table': anchor the answer in Event Sourcing.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Snapshot frequency trade-offs?
**A:** On 'Snapshot frequency trade-offs': anchor the answer in Event Sourcing.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** How do you delete user data under GDPR?
**A:** On 'How do you delete user data under GDPR': anchor the answer in Event Sourcing.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Event Sourcing. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: **Event Sourcing** stores **events as the source of truth** and folds them into current state — audit and replay built in.. Bank account: `MoneyDeposited`, `MoneyWithdrawn` events; balance projection updated asynchronously; monthly snapshot speeds rebuild for statements. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```java
// Event store append (sketch)
eventStore.append(accountId, new MoneyDeposited(amount, Instant.now()));
AccountState state = events.fold(AccountState.empty(), AccountState::apply);
```

---

### 39. Hexagonal / Ports & Adapters.

**Short answer:** **Hexagonal architecture** puts **domain in the center**; **ports** (interfaces) define what the app needs and offers; **adapters** implement REST, JPA, Kafka, SDKs. Test domain without Spring. Controllers are **inbound** adapters; repositories and Feign clients are **outbound**. Seniors draw this instead of a layer cake leaking JPA into REST.

#### What it is
Alistair Cockburn architecture pattern: application core isolated from technology choices. Also called ports and adapters. At senior level, interviewers want the problem statement before the pattern name.

#### How it works (internals)
Inbound port: use case interface (`PlaceOrderUseCase`). Inbound adapter: REST controller calls use case. Outbound port: `PaymentPort`. Outbound adapter: `StripeAdapter`. Dependency rule: adapters depend on core, not reverse.

#### When to use / when NOT to use
Non-trivial domain with multiple integrations and test requirements. Skip heavy ceremony for throwaway prototypes — still keep domain free of SDK imports. Pick the smallest pattern that meets SLOs; over-abstraction becomes its own incident source.

#### Production example
`OrderService` (domain) depends on `PaymentPort` and `OrderRepository` interfaces; `OrderController` and `StripeAdapter` live in adapter packages; domain tests run pure JUnit without `@SpringBootTest`. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- **Anemic domain** inside hexagon — ports with no behavior. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.
- Domain importing **`@Entity`** — JPA adapter leak. On-call engineers see ambiguous errors because the symptom is two hops away from the root cause.
- One adapter package mixing inbound and outbound with no boundaries. The fix is usually explicit boundaries, fail-fast startup, and an integration test that asserts the negative case.
- Drawing hexagonal slides but **package structure** is `controller/service/repository` only. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.

#### Interview follow-ups (with model answers)

**Q:** Hexagonal vs layered vs clean architecture?
**A:** On 'Hexagonal vs layered vs clean architecture': anchor the answer in Hexagonal / Ports & Adapters.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Where does `@Transactional` live?
**A:** On 'Where does `@Transactional` live': anchor the answer in Hexagonal / Ports & Adapters.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** How big should a port interface be?
**A:** On 'How big should a port interface be': anchor the answer in Hexagonal / Ports & Adapters.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Hexagonal / Ports & Adapters. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: **Hexagonal architecture** puts **domain in the center**; **ports** (interfaces) define what the app needs and offers; **adapters** implement REST, JPA, Kafka, SDKs.. `OrderService` (domain) depends on `PaymentPort` and `OrderRepository` interfaces; `OrderController` and `StripeAdapter` live in adapter packages; domain tests run pure JUnit without `@SpringBootTest`. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```java
// domain/port
public interface PaymentPort { PaymentResult charge(Money amount, IdempotencyKey key); }

// adapter/outbound
@Component
class StripeAdapter implements PaymentPort { /* SDK calls */ }
```

---

### 40. Anti-corruption layer.

**Short answer:** **Anti-corruption layer (ACL)** is an adapter that translates a **legacy or foreign bounded context** so your domain model stays clean — essential in bank integrations and strangler migrations. Stronger intent than generic Adapter: **protect your model** from their nouns leaking in.

#### What it is
DDD strategic pattern: translation boundary between contexts with incompatible models. Often combined with Facade toward your core. At senior level, interviewers want the problem statement before the pattern name.

#### How it works (internals)
ACL maps their IDs, statuses, and error codes to your ubiquitous language. May cache, batch, or normalize idempotency. Tests use recorded fixtures from legacy responses — not live mainframe in CI. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss.

#### When to use / when NOT to use
Integrating ERP, mainframe, partner API with alien model. Don't ACL-wrap your own modules — refactor instead. ACL at edge, not copy-paste mapping in every service method.

#### Production example
`LegacyLedgerAcl` implements `LedgerPort`: COBOL account codes → `AccountId`, SOAP faults → `LedgerUnavailableException`. Domain never sees WSDL types. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- ACL grows to **second domain** with business rules duplicated. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.
- Mapping in controller instead of dedicated ACL type. On-call engineers see ambiguous errors because the symptom is two hops away from the root cause.
- No **versioning** when legacy API changes silently. The fix is usually explicit boundaries, fail-fast startup, and an integration test that asserts the negative case.
- ACL bypassed by "quick" direct SDK call in one feature team. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.

#### Interview follow-ups (with model answers)

**Q:** ACL vs Adapter vs Facade?
**A:** On 'ACL vs Adapter vs Facade': anchor the answer in Anti-corruption layer.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Where does ACL sit in hexagonal diagram?
**A:** On 'Where does ACL sit in hexagonal diagram': anchor the answer in Anti-corruption layer.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Strangler fig and ACL together?
**A:** On 'Strangler fig and ACL together': anchor the answer in Anti-corruption layer.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Anti-corruption layer. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: **Anti-corruption layer (ACL)** is an adapter that translates a **legacy or foreign bounded context** so your domain model stays clean — essential in bank integrations and strangler migrations.. `LegacyLedgerAcl` implements `LedgerPort`: COBOL account codes → `AccountId`, SOAP faults → `LedgerUnavailableException`. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```java
@Component
public class LegacyLedgerAcl implements LedgerPort {
    public Balance getBalance(AccountId id) {
        var raw = soapClient.fetchBalance(toLegacyCode(id));
        return new Balance(raw.getAmount(), Currency.of(raw.getCcy()));
    }
}
```

---

### 41. Strangler Fig.

**Short answer:** **Strangler Fig** incrementally replaces a monolith by **routing traffic** to new services while old system shrinks — proxy by route, extract capability, repeat. Requires **data ownership plan** — two writers to same tables without migration strategy is how outages are born.

#### What it is
Martin Fowler migration pattern named after strangler vines replacing a tree. Often implemented with API gateway, feature flags, or reverse proxy path rules. At senior level, interviewers want the problem statement before the pattern name.

#### How it works (internals)
Identify seam (e.g. catalog browse vs checkout). New service handles slice; gateway routes `/catalog/**` to new stack. Sync or CDC migrates data; cutover with dual-write period or read-from-new/write-to-both with reconciliation. Decommission old module when traffic and data moved.

#### When to use / when NOT to use
Legacy monolith blocking delivery; clear bounded contexts emerging. Avoid big-bang rewrite. Don't strangler without observability on both paths — you won't know what's still on legacy.

#### Production example
Monolith `shop.war`: nginx routes `/api/v2/products` to `catalog-service`; v1 still monolith. After 6 months, product DB owned by catalog-service; monolith reads via ACL HTTP until removed. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- **Dual write** without reconciliation — divergent truth. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.
- Strangling **without tests** on parity between old and new paths. On-call engineers see ambiguous errors because the symptom is two hops away from the root cause.
- Feature flag forever — never decommission legacy. The fix is usually explicit boundaries, fail-fast startup, and an integration test that asserts the negative case.
- Shared database as integration — distributed monolith in new clothes. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.

#### Interview follow-ups (with model answers)

**Q:** Strangler vs branch by abstraction?
**A:** On 'Strangler vs branch by abstraction': anchor the answer in Strangler Fig.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** How do you verify behavioral parity?
**A:** On 'How do you verify behavioral parity': anchor the answer in Strangler Fig.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Database migration strategies during strangler?
**A:** On 'Database migration strategies during strangler': anchor the answer in Strangler Fig.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Strangler Fig. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: **Strangler Fig** incrementally replaces a monolith by **routing traffic** to new services while old system shrinks — proxy by route, extract capability, repeat.. Monolith `shop.war`: nginx routes `/api/v2/products` to `catalog-service`; v1 still monolith. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```yaml
# Gateway route sketch
spring:
  cloud:
    gateway:
      routes:
        - id: catalog-v2
          uri: lb://catalog-service
          predicates: [Path=/api/v2/products/**]
```

---

### 42. Sidecar.

**Short answer:** **Sidecar** runs a **companion process** alongside your app container — Envoy proxy, log shipper, service mesh agent. Offloads TLS, retries, telemetry from app code. Cost: extra CPU/memory per pod and hop latency — know **Istio sidecar** vs **ambient mesh** trade-offs at interview depth.

#### What it is
Cloud-native deployment pattern: auxiliary container in same pod (K8s) or host agent pattern. Not GoF — infrastructure pattern catalog. At senior level, interviewers want the problem statement before the pattern name.

#### How it works (internals)
App container talks to localhost sidecar; sidecar handles mTLS, L7 routing, access logs. Mesh injects sidecar via mutating webhook. Ambient mesh moves L4/L7 to node level — fewer sidecars, different ops model. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss.

#### When to use / when NOT to use
Platform team standardizes observability and mTLS via sidecar. Avoid duplicating retries/TLS in app **and** sidecar without policy. Small services on tight memory budget — sidecar overhead matters.

#### Production example
Spring Boot pod: app + Envoy sidecar; app uses plain HTTP to `127.0.0.1:15001`; mesh handles mTLS to downstream. Fluent Bit sidecar ships logs — app writes stdout only. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- **Double retry** in Resilience4j and mesh — amplified load. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.
- Sidecar resource limits too low — OOMKill kills traffic. On-call engineers see ambiguous errors because the symptom is two hops away from the root cause.
- Debugging production without knowing traffic goes through sidecar. The fix is usually explicit boundaries, fail-fast startup, and an integration test that asserts the negative case.
- Sidecar on every job pod including short CronJobs — waste. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.

#### Interview follow-ups (with model answers)

**Q:** Sidecar vs ambassador pattern?
**A:** On 'Sidecar vs ambassador pattern': anchor the answer in Sidecar.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Istio sidecar vs ambient — when which?
**A:** On 'Istio sidecar vs ambient — when which': anchor the answer in Sidecar.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** What stays in app vs sidecar for retries?
**A:** On 'What stays in app vs sidecar for retries': anchor the answer in Sidecar.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Sidecar. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: **Sidecar** runs a **companion process** alongside your app container — Envoy proxy, log shipper, service mesh agent.. Spring Boot pod: app + Envoy sidecar; app uses plain HTTP to `127.0.0.1:15001`; mesh handles mTLS to downstream. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```yaml
# Pod with sidecar (simplified)
containers:
  - name: app
    image: order-service:1.2.0
  - name: envoy
    image: envoyproxy/envoy:v1.28
```

---

### 43. Ambassador vs Adapter at the edge.

**Short answer:** **Ambassador** is an **out-of-process proxy** (often sidecar) that handles connection pooling, retries, TLS to remote services on behalf of the app. **Adapter** is **in-process translation** of APIs. Don't duplicate retry/TLS policy in application **and** ambassador without an explicit ownership rule.

#### What it is
- **Ambassador (cloud pattern):** Client-side proxy helper — smart outbound proxy. - **Adapter (GoF):** Interface translation inside your codebase. Ambassador at network edge; Adapter at code boundary. At senior level, interviewers want the problem statement before the pattern name.

#### How it works (internals)
Ambassador container co-located with app; app calls localhost; ambassador speaks mTLS to cluster services. Adapter class implements your port wrapping SDK. Overlap: both "hide remote complexity" — ambassador at wire, adapter at types. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss.

#### When to use / when NOT to use
Ambassador when platform owns outbound reliability (mesh, API gateway client patterns). Adapter when mapping vendor model to domain port. Pick **one owner** for retries — typically platform ambassador OR app Resilience4j, not both blindly.

#### Production example
App Resilience4j disabled for mesh-managed routes; `PaymentPort` adapter maps Stripe SDK to domain. Local dev without mesh: adapter includes timeouts; prod mesh handles mTLS. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- Ambassador + Feign retry + gateway retry — triple storm. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.
- Using ambassador name for **in-process** wrapper — confuses interviewers. On-call engineers see ambiguous errors because the symptom is two hops away from the root cause.
- No timeout on ambassador → blocked threads in app container. The fix is usually explicit boundaries, fail-fast startup, and an integration test that asserts the negative case.

#### Interview follow-ups (with model answers)

**Q:** Ambassador vs sidecar — same thing?
**A:** On 'Ambassador vs sidecar — same thing': anchor the answer in Ambassador vs Adapter at the edge.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Where does Adapter end and ACL begin?
**A:** On 'Where does Adapter end and ACL begin': anchor the answer in Ambassador vs Adapter at the edge.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Client-side load balancing vs ambassador?
**A:** On 'Client-side load balancing vs ambassador': anchor the answer in Ambassador vs Adapter at the edge.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Ambassador vs Adapter at the edge. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: **Ambassador** is an **out-of-process proxy** (often sidecar) that handles connection pooling, retries, TLS to remote services on behalf of the app. **Adapter** is **in-process translation** of APIs.. App Resilience4j disabled for mesh-managed routes; `PaymentPort` adapter maps Stripe SDK to domain. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```java
// In-process Adapter (not Ambassador)
@Component
class StripeAdapter implements PaymentPort { /* translate + call SDK */ }
// Outbound mTLS/retries often in mesh sidecar — not duplicated here in prod
```

---

### 44. MVC / MVVM in React vs Spring MVC.

**Short answer:** **Spring MVC:** `DispatcherServlet` → `@Controller` → view/JSON; server owns validation and source of truth. **React:** UI as function of props/state; "MVVM" often means stores (Redux, Zustand) binding view to view-model. Don't put **business invariants only in React** — server must enforce rules; client validation is UX only.

#### What it is
- **MVC:** Model (data/rules), View (presentation), Controller (input coordination). - **MVVM:** ViewModel exposes bindable state; View binds declaratively (XAML, modern frontend stores). Patterns for separating UI from logic — different stacks, same interview trap: where invariants live. At senior level, interviewers want the problem statement before the pattern name.

#### How it works (internals)
Spring MVC: front controller (`DispatcherServlet`), handler mapping, `@RestController` returns DTO JSON — view is client. React: components + hooks; global store as view-model. BFF may aggregate for specific client MVVM needs. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss.

#### When to use / when NOT to use
Server MVC/BFF for authoritative writes and auth. Rich client MVVM for interactive UX — still call APIs for mutations. Don't duplicate fee calculation logic only in frontend "because MVVM."

#### Production example
Checkout SPA (React + Redux): displays cart from BFF; `PlaceOrder` POST to Spring controller re-validates price, inventory, payment — client state is optimistic UI only. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- **Fat controller** with business rules — should be use case/domain. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.
- Redux as **only** source of truth for money amounts. On-call engineers see ambiguous errors because the symptom is two hops away from the root cause.
- Spring MVC returning `@Entity` — lazy load and coupling. The fix is usually explicit boundaries, fail-fast startup, and an integration test that asserts the negative case.
- Confusing **component state** with domain model. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.

#### Interview follow-ups (with model answers)

**Q:** Front Controller role in Spring MVC?
**A:** On 'Front Controller role in Spring MVC': anchor the answer in MVC / MVVM in React vs Spring MVC.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Where does validation run — Bean Validation on DTO?
**A:** On 'Where does validation run — Bean Validation on DTO': anchor the answer in MVC / MVVM in React vs Spring MVC.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** BFF and MVC — how do they relate?
**A:** On 'BFF and MVC — how do they relate': anchor the answer in MVC / MVVM in React vs Spring MVC.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving MVC / MVVM in React vs Spring MVC. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: **Spring MVC:** `DispatcherServlet` → `@Controller` → view/JSON; server owns validation and source of truth. **React:** UI as function of props/state; "MVVM" often means stores (Redux, Zustand) binding view to view-model.. Checkout SPA (React + Redux): displays cart from BFF; `PlaceOrder` POST to Spring controller re-validates price, inventory, payment — client state is optimistic UI only. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```java
@RestController
@RequiredArgsConstructor
public class OrderController {
    private final PlaceOrderUseCase placeOrder;
    @PostMapping("/orders")
    public OrderConfirmation place(@Valid @RequestBody PlaceOrderRequest req) {
        return placeOrder.execute(req.toCommand());
    }
}
```

---

### 45. Front Controller.

**Short answer:** **Front Controller** funnels all requests through **one entry point** that dispatches to handlers — **`DispatcherServlet`** in Spring MVC. Enables centralized routing, filters, and cross-cutting concerns before business logic. Servlet filters and Spring Security sit **in front of** the front controller.

#### What it is
Enterprise/J2EE pattern: single controller receives all requests, delegates to action/handler. Spring's `DispatcherServlet` is canonical in Java web apps. At senior level, interviewers want the problem statement before the pattern name.

#### How it works (internals)
HTTP → filter chain → `DispatcherServlet` → `HandlerMapping` finds `@Controller` method → `HandlerAdapter` invokes → `ViewResolver` or `@ResponseBody` message converter. Error handling via `@ControllerAdvice`. Same pattern at gateway layer (Spring Cloud Gateway) for microservices edge. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss.

#### When to use / when NOT to use
Standard for servlet-based web frameworks — you get it with Spring Boot. Alternative stacks (WebFlux functional routes) still have a central router — same idea. Don't bypass front controller with random servlets per feature without reason.

#### Production example
All `/api/**` hits `DispatcherServlet`; security filter authenticates JWT; controller methods mapped by path and HTTP verb; global exception handler returns Problem Details JSON. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- Multiple servlets each with own security — inconsistent auth. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.
- Heavy logic in `DispatcherServlet` customization — use filters/advice. On-call engineers see ambiguous errors because the symptom is two hops away from the root cause.
- Confusing **API Gateway** front controller with **DispatcherServlet** — two layers in microservices. The fix is usually explicit boundaries, fail-fast startup, and an integration test that asserts the negative case.

#### Interview follow-ups (with model answers)

**Q:** DispatcherServlet vs Filter chain order?
**A:** On 'DispatcherServlet vs Filter chain order': anchor the answer in Front Controller.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** `@ControllerAdvice` and front controller?
**A:** On '`@ControllerAdvice` and front controller': anchor the answer in Front Controller.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** WebFlux `RouterFunction` — still front controller?
**A:** On 'WebFlux `RouterFunction` — still front controller': anchor the answer in Front Controller.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Front Controller. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: **Front Controller** funnels all requests through **one entry point** that dispatches to handlers — **`DispatcherServlet`** in Spring MVC.. All `/api/**` hits `DispatcherServlet`; security filter authenticates JWT; controller methods mapped by path and HTTP verb; global exception handler returns Problem Details JSON. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```java
@SpringBootApplication
public class App { /* DispatcherServlet auto-configured */ }

@RestController
public class HealthController {
    @GetMapping("/health") String health() { return "ok"; }
}
```

---

### 46. Intercepting Filter.

**Short answer:** **Intercepting Filter** runs **cross-cutting HTTP concerns** in a chain before/after the servlet — auth, CORS, MDC/trace IDs, rate limiting. Same family as servlet **Filter** and Spring Security's `SecurityFilterChain`. Keep filters **fast**; security filters should **fail closed**.

#### What it is
J2EE/enterprise pattern: pluggable filters intercept requests/responses. Spring `OncePerRequestFilter`, `HandlerInterceptor` (MVC layer, post-filter). At senior level, interviewers want the problem statement before the pattern name.

#### How it works (internals)
Filter chain order via `@Order` or `FilterRegistrationBean`. Each filter calls `chain.doFilter()` to continue or short-circuit response. Spring Security inserts ~15 filters. Gateway filters (SCG) are intercepting filters at edge.

#### When to use / when NOT to use
Auth, tracing, request logging, tenant resolution in filters — not business rules. Avoid heavy DB calls in filters on every request without cache. Don't put transaction boundaries in filters.

#### Production example
`CorrelationIdFilter` → `JwtAuthFilter` → `TenantFilter` → `DispatcherServlet`. Rate limit filter returns 429 before hitting Tomcat threads for abusive clients. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- Forgot **`chain.doFilter()`** — blank response. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.
- Wrong **`@Order`** — security bypass. On-call engineers see ambiguous errors because the symptom is two hops away from the root cause.
- Mutable **static state** in filter — thread safety. The fix is usually explicit boundaries, fail-fast startup, and an integration test that asserts the negative case.
- Business discount logic in filter because "it's cross-cutting" — wrong layer. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.

#### Interview follow-ups (with model answers)

**Q:** Filter vs HandlerInterceptor vs Gateway filter?
**A:** On 'Filter vs HandlerInterceptor vs Gateway filter': anchor the answer in Intercepting Filter.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Fail-open vs fail-closed for auth filter?
**A:** On 'Fail-open vs fail-closed for auth filter': anchor the answer in Intercepting Filter.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Testing filter chain in Spring?
**A:** On 'Testing filter chain in Spring': anchor the answer in Intercepting Filter.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Intercepting Filter. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: **Intercepting Filter** runs **cross-cutting HTTP concerns** in a chain before/after the servlet — auth, CORS, MDC/trace IDs, rate limiting.. `CorrelationIdFilter` → `JwtAuthFilter` → `TenantFilter` → `DispatcherServlet`. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```java
@Component
@Order(1)
public class CorrelationIdFilter extends OncePerRequestFilter {
    protected void doFilterInternal(HttpServletRequest req, HttpServletResponse res, FilterChain chain)
            throws ServletException, IOException {
        MDC.put("traceId", Optional.ofNullable(req.getHeader("X-Trace-Id")).orElse(UUID.randomUUID().toString()));
        try { chain.doFilter(req, res); } finally { MDC.clear(); }
    }
}
```

---

### 47. Data Transfer Object vs Entity.

**Short answer:** **DTO** is a **stable API shape** for boundaries — records, MapStruct targets, OpenAPI schemas. **Entity** carries **persistence and domain invariants** — JPA `@Entity`, lazy associations, lifecycle. Never expose entities as REST JSON — lazy loops, over-exposure, and coupling to schema changes.

#### What it is
- **DTO (EE pattern):** Serializable carrier across layers/network; no behavior or minimal behavior. - **Entity:** Object mapped to DB row; part of ORM identity map and unit of work. At senior level, interviewers want the problem statement before the pattern name. In Spring Boot microservices this often appears at both code and integration boundaries.

#### How it works (internals)
Controller accepts `PlaceOrderRequest` DTO → maps to domain command → service loads `Order` entity → persists → maps to `OrderConfirmation` DTO response. MapStruct generates mappers at compile time. Entities managed inside `@Transactional`; DTOs safe outside session. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss.

#### When to use / when NOT to use
DTO at every external boundary (REST, Kafka message schema, gRPC). Entity inside persistence adapter and domain core if rich model. Shared DTO between services via published schema (Avro/JSON Schema) — not shared entity classes.

#### Production example
`GET /orders/{id}` returns `OrderDetailDto` built by query projection — not `Order` entity with lazy `customer` that triggers N+1 or serializes password hash field. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- **`@Entity` on REST** — OpenAPI documents DB schema; accidental lazy load. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.
- DTO **equals entity field-for-field** with no thought — leaks internal IDs and flags. On-call engineers see ambiguous errors because the symptom is two hops away from the root cause.
- Mutating DTO reused as command without validation. The fix is usually explicit boundaries, fail-fast startup, and an integration test that asserts the negative case.
- MapStruct mapping **entity graph** with lazy collections in mapper — session errors. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.

#### Interview follow-ups (with model answers)

**Q:** DTO vs VO vs domain model?
**A:** On 'DTO vs VO vs domain model': anchor the answer in Data Transfer Object vs Entity.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** MapStruct vs manual mapping — when which?
**A:** On 'MapStruct vs manual mapping — when which': anchor the answer in Data Transfer Object vs Entity.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Projection query vs load entity + map?
**A:** On 'Projection query vs load entity + map': anchor the answer in Data Transfer Object vs Entity.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Data Transfer Object vs Entity. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: **DTO** is a **stable API shape** for boundaries — records, MapStruct targets, OpenAPI schemas. **Entity** carries **persistence and domain invariants** — JPA `@Entity`, lazy associations, lifecycle.. `GET /orders/{id}` returns `OrderDetailDto` built by query projection — not `Order` entity with lazy `customer` that triggers N+1 or serializes password hash field. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```java
public record OrderDetailDto(UUID id, String status, Money total, String customerName) {}

@GetMapping("/orders/{id}")
public OrderDetailDto get(@PathVariable UUID id) {
    return orderQueries.findDetail(id); // JDBC/JPA projection, not Entity
}
```

---

### 48. Specification (DDD).

**Short answer:** **Specification** composes **reusable business predicates** — for queries ("active premium customers") and domain rules ("order eligible for refund"). Spring Data **`JpaSpecificationExecutor`**, QueryDSL, or hand-rolled `Specification<T>` with `and`/`or`/`not`. Don't build a generic query language attackers can turn into injection or full table scans.

#### What it is
DDD pattern: predicate object encapsulating rule; combinable (`AndSpec`, `OrSpec`). Fowler enterprise pattern overlapping with Strategy for boolean conditions. At senior level, interviewers want the problem statement before the pattern name.

#### How it works (internals)
`Specification<Order>` implements `toPredicate(Root, CriteriaQuery, CriteriaBuilder)` for JPA. Domain specs pure Java: `satisfiedBy(order)` for in-memory checks. Same rule reused in repository query and domain validation — single source of truth if disciplined. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss.

#### When to use / when NOT to use
Complex filtering reused across use cases; eligibility rules referenced from multiple services. Skip for one-off `WHERE status = 'OPEN'`. Never expose arbitrary spec builder to end users.

#### Production example
`OrderEligibleForRefundSpec` used in REST validation and `OrderRepository.findAll(spec)` for batch job — same business definition. Composed: `new ActiveCustomerSpec().and(new PremiumTierSpec())`. We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback. Alerts covered the known failure mode instead of assuming the happy path forever.

#### Common mistakes
- Spec logic **duplicated** in JPQL and Java — drift. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.
- User-facing **dynamic spec** from query params — SQL injection via sort/filter. On-call engineers see ambiguous errors because the symptom is two hops away from the root cause.
- Generic spec framework **over-engineered** for three filters. The fix is usually explicit boundaries, fail-fast startup, and an integration test that asserts the negative case.
- Spec that can't use index — production full table scan. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.

#### Interview follow-ups (with model answers)

**Q:** Specification vs Criteria API vs QueryDSL?
**A:** On 'Specification vs Criteria API vs QueryDSL': anchor the answer in Specification (DDD).—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Sharing specs between microservices?
**A:** On 'Sharing specs between microservices': anchor the answer in Specification (DDD).—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** Specification vs Policy pattern?
**A:** On 'Specification vs Policy pattern': anchor the answer in Specification (DDD).—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Specification (DDD). Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: **Specification** composes **reusable business predicates** — for queries ("active premium customers") and domain rules ("order eligible for refund").. `OrderEligibleForRefundSpec` used in REST validation and `OrderRepository.findAll(spec)` for batch job — same business definition. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```java
public class OpenOrderSpec implements Specification<Order> {
    public Predicate toPredicate(Root<Order> root, CriteriaQuery<?> q, CriteriaBuilder cb) {
        return cb.equal(root.get("status"), Status.OPEN);
    }
}

// repository.findAll(new OpenOrderSpec().and(new CustomerSpec(customerId)));
```

---

### 49. Anti-patterns they want you to trash.

**Short answer:** Seniors name anti-patterns with **war stories**: God class, anemic domain while claiming DDD, gold plating, premature AbstractSingletonProxyFactoryBean abstraction, copy-paste `BaseService`, catching `Exception`, returning `null` from collections, **distributed monolith** (chatty sync + shared DB), and **Smart UI** (logic only in frontend). Interviewers want pattern name + why it hurt + what you did instead.

#### What it is
Anti-patterns are recurring solutions that **fail** in context — often corrupted design patterns. Microservices era adds: shared database integration, saga without compensation, cache-aside without invalidation strategy. At senior level, interviewers want the problem statement before the pattern name.

#### How it works (internals)
Anti-patterns persist due to schedule pressure, resume-driven development, and resume-driven architecture ("we need Kafka"). Detection: high coupling, untestable code, incidents at 2 a.m., deploy fear. Framework defaults and proxy ordering change runtime behavior in ways unit tests miss. Production debugging usually crosses logs, metrics, and condition reports—not just source code.

#### When to use / when NOT to use
Call them out in design review with alternatives — not as buzzword bingo. Replace God class with cohesive types and use cases. Replace shared DB with API + events. Replace catch-Exception with specific handling and structured errors.

#### Production example
"We had `BaseService` with 40 `@Autowired` fields — every service extended it. Replaced with constructor-injected use cases and ports; test time dropped 60%. Shared `orders` table between three services caused lock contention — introduced outbox + owned schema per service." We tied the decision to a measurable outcome: fewer duplicate charges, lower MTTR, or clearer rollback.

#### Common mistakes
- Labeling any large class **God object** without suggesting seam. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.
- Anti-pattern rant without **measurable** pain (MTTR, defect rate). On-call engineers see ambiguous errors because the symptom is two hops away from the root cause.
- Throwing DDD terms while keeping anemic model — interviewer catches mismatch. The fix is usually explicit boundaries, fail-fast startup, and an integration test that asserts the negative case.
- Microservices for **organizational politics** not boundaries — distributed monolith. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.

#### Interview follow-ups (with model answers)

**Q:** Anemic domain model — always bad?
**A:** On 'Anemic domain model — always bad': anchor the answer in Anti-patterns they want you to trash.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** When is inheritance OK?
**A:** On 'When is inheritance OK': anchor the answer in Anti-patterns they want you to trash.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** How do you refactor God class incrementally?
**A:** On 'How do you refactor God class incrementally': anchor the answer in Anti-patterns they want you to trash.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving Anti-patterns they want you to trash. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: Seniors name anti-patterns with **war stories**: God class, anemic domain while claiming DDD, gold plating, premature AbstractSingletonProxyFactoryBean abstraction, copy-paste `BaseService`, catching `Exception`, returning `null` from collections, **distributed monolith** (chatty sync + shared DB), and **Smart UI** (logic only in frontend).. "We had `BaseService` with 40 `@Autowired` fields — every service extended it. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```java
// Anti-pattern sketch — don't
public abstract class BaseService {
    @Autowired protected OrderRepo orders;
    @Autowired protected PaymentRepo payments;
    // ... 38 more
}

// Prefer: focused use case with explicit deps
public class PlaceOrderUseCase {
    private final OrderRepository orders;
    private final PaymentPort payment;
    public PlaceOrderUseCase(OrderRepository orders, PaymentPort payment) { ... }
}
```

---

### 50. How a senior talks about patterns in an interview.

**Short answer:** Structure answers as **pattern + context + alternative + risk**: "We used Strategy for fee calculation because finance changes rates without deploys — injected map of calculators. We rejected a rule engine because four formulas didn't justify SPEL. Risk: missing calculator for new product type — we fail closed with exhaustive enum tests." Draw when helpful; say when the pattern **hurts**.

#### What it is
Communication pattern, not GoF: demonstrate judgment, not catalog recitation. Map to Spring/cloud where interviewers live — `@Transactional` is Proxy, outbox is microservices pattern, not academic trivia. At senior level, interviewers want the problem statement before the pattern name.

#### How it works (internals)
2–3 minute arc: (1) problem, (2) pattern choice, (3) trade-off rejected, (4) operational reality (tests, metrics, failure mode). Mention team constraints — "two-week deadline → Facade over subsystem, not full strangler yet." Framework defaults and proxy ordering change runtime behavior in ways unit tests miss. Production debugging usually crosses logs, metrics, and condition reports—not just source code.

#### When to use / when NOT to use
Always frame patterns as **decisions under constraints**. Never claim perfect architecture — seniors discuss evolution and debt openly. Pick the smallest pattern that meets SLOs; over-abstraction becomes its own incident source.

#### Production example
"We didn't event-source orders — audit table + state was enough. We did outbox to inventory because dual-write caused lost events twice. Circuit breaker on legacy pricing SOAP — half-open probes every 30s; fallback to cached price list with banner. Pain point: breaker opened during their planned maintenance we didn't know about — now calendar in runbook."

#### Common mistakes
- Reciting GoF list without **your** code reference. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.
- "We use microservices therefore we use all patterns.". On-call engineers see ambiguous errors because the symptom is two hops away from the root cause.
- No mention of **failure** or monitoring. The fix is usually explicit boundaries, fail-fast startup, and an integration test that asserts the negative case.
- Drawing UML for 5 minutes without saying when **not** to use it. This often surfaces only under load or after a deploy when assumptions about scope and lifecycle were never tested.

#### Interview follow-ups (with model answers)

**Q:** Tell me about a pattern you **removed** — why?
**A:** On 'Tell me about a pattern you **removed** — why': anchor the answer in How a senior talks about patterns in an interview.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** What pattern would you add next quarter?
**A:** On 'What pattern would you add next quarter': anchor the answer in How a senior talks about patterns in an interview.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

**Q:** How do you prevent pattern over-engineering in PR review?
**A:** On 'How do you prevent pattern over-engineering in PR review': anchor the answer in How a senior talks about patterns in an interview.—name mechanism, production trade-off, and failure mode. Cite a concrete Spring Boot or microservices example from your experience. State what you would not do and which metric or alert proves the design works. Interviewers reward operational detail (rollback, idempotency, pool exhaustion) over textbook definitions alone.

#### Scenario probe
**Situation:** Post-release: p99 latency rises on code paths involving How a senior talks about patterns in an interview. Error budget burns; team needs root cause before rollback window closes.

**Model answer:** I start from: Structure answers as **pattern + context + alternative + risk**: "We used Strategy for fee calculation because finance changes rates without deploys — injected map of calculators.. "We didn't event-source orders — audit table + state was enough. I correlate logs/traces, verify framework boundaries (proxies, filters, TX scope), and check whether we fail open or closed. Short-term: feature flag, breaker tuning, or scale consumers; long-term: align code with the intended pattern and add a regression test plus alert on the failure mode.

#### Code / config (when useful)

```text
Interview sentence template:
"We applied [PATTERN] to [PROBLEM] because [CONSTRAINT].
We considered [ALTERNATIVE] but rejected it because [REASON].
The operational risk is [RISK]; we mitigate with [TEST/METRIC/RUNBOOK]."
```

---

---

## Scenario-based interview drills

### S1. Checkout saga stuck after payment capture

**Situation:** E-commerce platform: Order service captures payment, publishes OrderPaid, inventory reserves stock, shipping never starts. 2,400 orders stuck PAID for 45 minutes. Choreography via Kafka; no central orchestrator.

**What they're testing:** Saga compensation, idempotency, observability across services.

**How to structure your answer:**
- State diagram of saga steps and which service owns each transition
- How you detect stuck sagas (timeout, correlation ID, DLQ)
- Compensation vs forward-fix for physical goods
- Idempotency on payment capture replay

**Model answer:** I start with correlation IDs in logs and a saga timeout dashboard — orders in PAID without InventoryReserved within N minutes. Likely causes: consumer lag, poison message, or publish-before-commit ghost events. I check inventory consumer group lag and DLQ depth. If inventory handler throws on a new SKU mapping, messages retry until max — orders pile up. Short-term: pause consumer, fix mapping, replay from offset with idempotent reserve keyed by orderId. Long-term: add orchestrated timeout job or saga manager that marks orders NEEDS_ATTENTION and alerts ops. Payment capture must be idempotent — replay cannot double-charge. Compensation for digital goods may refund; for shipped goods forward-fix is safer. I document per-step timeouts and runbook for 'stuck PAID' with exact kafka-consumer-group commands.

**Common weak answers:** Blaming Kafka without correlation IDs; proposing 2PC across Postgres and Kafka.

**Follow-up probes (with answers):**

**Q:** Choreography vs orchestration for this flow?
**A:** Choreography works at moderate complexity if every step emits well-versioned events and timeouts are explicit. I move to orchestration when stuck-state detection becomes a weekly ops task — a state machine or saga table with scheduled reconciliation is easier to reason about than distributed hope. Hybrid: choreography for happy path, orchestrator cron for timeout and escalation.

---

### S2. Circuit breaker flapping on legacy pricing SOAP

**Situation:** Pricing service calls legacy SOAP endpoint via Feign + Resilience4j. During partner maintenance, breaker opens; storefront shows stale prices. Breaker half-open probes every 5s; partner still down — flapping alerts.

**What they're testing:** Circuit breaker tuning, fallback safety, calendar integration.

**How to structure your answer:**
- Failure vs slow-call thresholds
- Fallback data freshness and customer communication
- Half-open probe rate vs partner capacity
- Runbook linkage to partner maintenance calendar

**Model answer:** Flapping means half-open succeeds briefly then fails — or failure rate hovers at threshold. I widen slow-call threshold if timeouts are misclassified as failures, and increase wait duration in open state so we do not hammer a down dependency. Fallback to cached price list must expose freshness metadata to UI — banner 'prices may be delayed' beats silent wrong checkout. Integrate partner maintenance calendar into runbook; suppress or pre-open breaker during known windows. Metrics: breaker state transitions, fallback invocation rate, price delta between live and cache. Post-incident: negotiate SLA or migrate to REST with bulkhead isolation.

**Common weak answers:** Disabling breaker entirely; fallback to zero price.

**Follow-up probes (with answers):**

**Q:** Should business 404 count as failure?
**A:** No — record-not-found is often expected and should not trip the breaker. Configure ignoreExceptions for domain not-found types; count only transport errors and 5xx as failures.

---

### S3. Outbox poller duplicate events after DB failover

**Situation:** Order service uses transactional outbox. After Aurora failover, poller republishes 12k OrderCreated events. Downstream inventory double-reserves until caught.

**What they're testing:** Transactional outbox, idempotent consumers, failover behavior.

**How to structure your answer:**
- Outbox schema and publishing semantics
- Why failover caused duplicates
- Consumer idempotency design
- Poller state and exactly-once illusion

**Model answer:** Outbox guarantees at-least-once from DB to broker if poller marks rows published after ack. Failover may reset in-flight poller state or cause double publish if mark-published and kafka send are not atomic. Consumers must dedupe on eventId or business key with unique constraint on processed_events. I audit poller for SELECT FOR UPDATE SKIP LOCKED pattern and single-leader election. Replay storm: pause inventory consumer, backfill dedupe table, replay with idempotent reserve. Long-term: monitor duplicate rate metric; chaos-test DB failover quarterly.

**Common weak answers:** Claiming Kafka EOS fixes cross-service duplicates without consumer idempotency.

**Follow-up probes (with answers):**

**Q:** Outbox vs @TransactionalEventListener?
**A:** Listener AFTER_COMMIT is in-memory — JVM death loses event. Outbox row commits with business data; separate poller gives durability and retry.

---

### S4. God Facade BFF becomes distributed monolith

**Situation:** Mobile BFF grows to 40 endpoints, calls 8 services synchronously, owns business rules copied from domain. Deploy coupling — any downstream change breaks BFF. p99 2.8s on home feed.

**What they're testing:** Facade boundaries, aggregation patterns, team topology.

**How to structure your answer:**
- What belongs in BFF vs domain services
- Sync vs async aggregation
- Caching and GraphQL considerations
- Strangler path off the god facade

**Model answer:** BFF should shape responses and auth translation, not own inventory or pricing rules. I inventory methods with domain logic — move to owning services, expose stable read APIs or materialized views. Home feed: parallel async calls with bounded timeouts, partial response with degraded sections, edge cache for catalog snippets. Introduce API composition layer or GraphQL only if client variance justifies operational cost. Team topology: BFF team should not be bottleneck for every domain change — contract tests and versioned DTOs. Measure per-dependency contribution to p99; bulkhead thread pools per downstream.

**Common weak answers:** Adding more synchronous calls and caching without fixing ownership.

**Follow-up probes (with answers):**

**Q:** When does BFF hurt?
**A:** When it becomes the only place business rules live and every feature needs BFF deploy — you rebuilt the monolith over HTTP.

---

### S5. CQRS read model hours behind writes

**Situation:** Orders CQRS: write Postgres, read Elasticsearch. Support sees 'order not found' while customer has confirmation email. Consumer lag 90 minutes after Black Friday.

**What they're testing:** CQRS consistency model, consumer scaling, support tooling.

**How to structure your answer:**
- Expected consistency vs bug
- Lag detection and alerting
- Read-your-writes UX patterns
- When CQRS was wrong choice

**Model answer:** CQRS is eventual consistency by design — support tooling must query write model by ID or show 'sync pending' state. 90-minute lag is operational failure: scale consumers, fix poison partition, add lag alert on consumer group. UX: after place order, read from write API or include read model version in response. Black Friday: pre-scale ES indexing pipeline, prioritize order events topic, temporary fat consumers. If business required strong read-after-write everywhere, CQRS was wrong — use synchronized read or don't split stores.

**Common weak answers:** Promising strong consistency across ES and Postgres.

**Follow-up probes (with answers):**

**Q:** When is CQRS worth it?
**A:** Read/write shape divergence, independent scaling, or complex reporting — not for 3-table CRUD.

---

### S6. Strategy map missing new product type at runtime

**Situation:** Fee calculation uses injected Map<ProductType, FeeStrategy>. New BNPL product launched; enum added, strategy bean forgotten. Production defaults to zero fee for 6 hours.

**What they're testing:** Strategy registration, fail-closed design, enum exhaustiveness.

**How to structure your answer:**
- How missing strategy surfaced
- Fail-closed vs fail-open default
- Startup validation vs runtime
- Testing all enum values

**Model answer:** Silent default is fail-open — worst for money. I require explicit strategy per ProductType: startup fails if map incomplete, or computeIfAbsent throws IllegalStateException. Spring: collect List<FeeStrategy> into Map keyed by type in @Configuration with validation. Tests: parameterized test every enum value has strategy; arch unit test no switch default. Alert on 'unknown product type' log metric — should never fire. Post-incident: backfill fees via batch job and reconciliation report.

**Common weak answers:** Returning zero fee as default; only manual QA for new products.

**Follow-up probes (with answers):**

**Q:** List injection vs explicit Map bean?
**A:** Explicit Map bean with validation at startup beats silent List collect — fails fast in CI not prod.

---

### S7. Hexagonal ports leak JPA into domain

**Situation:** Claimed hexagonal architecture but domain entities are @Entity with Hibernate annotations. Team cannot test pricing rules without H2; bounded context polluted.

**What they're testing:** Hexagonal boundaries, adapter placement, testability.

**How to structure your answer:**
- What leaked and why it matters
- Refactor seams without big bang
- Port interface design
- Persistence adapter responsibilities

**Model answer:** Domain model should be framework-free; JPA entities belong in adapter module as persistence models mapped to domain. Incremental path: introduce Order domain record and OrderJpaEntity with mapper in adapter; keep API stable. Ports: OrderRepository interface in domain with save/findById; adapter implements with Spring Data. Unit test pricing on pure domain; adapter integration test with Testcontainers. Interview point: hexagonal is about dependency direction, not folder names.

**Common weak answers:** Renaming packages without changing dependencies.

**Follow-up probes (with answers):**

**Q:** Repository vs DAO in hexagonal?
**A:** Repository port speaks domain language; DAO/adapter speaks SQL/JPA — same adapter, different naming discipline.

---

### S8. Retry storm amplifies payment gateway outage

**Situation:** All microservices retry 3x on 503 from payment gateway. Gateway recovers but immediate retry wave triggers rate limit — cascading failures. No jitter; retries at gateway and service.

**What they're testing:** Retry policy, idempotency, layered retries.

**How to structure your answer:**
- Retry budget per layer
- Jitter and exponential backoff
- Idempotency keys on POST
- Circuit breaker interaction

**Model answer:** Retries multiply: 50 services × 3 retries × concurrent requests = outage amplifier. Policy: retry only idempotent ops or POST with Idempotency-Key; max 2 retries with full jitter; breaker opens after failure rate threshold. Single retry layer — pick gateway OR client, not both. Payment APIs: use provider idempotency key stored 24h minimum. Dashboard retry rate per dependency; alert when retry ratio > baseline during incident.

**Common weak answers:** Infinite retries on Kafka consumer for poison message.

**Follow-up probes (with answers):**

**Q:** When should Kafka consumer not retry?
**A:** Poison message: after N tries route to DLT, fix code, replay manually — infinite retry blocks partition.

---

### S9. Anti-corruption layer becomes god adapter

**Situation:** ACL for legacy billing SOAP grows to 8k lines — business rules, caching, retries, reporting. Every billing change requires ACL deploy. Incidents when ACL cache serves stale tax rates.

**What they're testing:** ACL scope, caching invalidation, strangler fig.

**How to structure your answer:**
- What belongs in ACL vs new billing service
- Cache TTL and invalidation
- Strangler milestones
- Testing ACL translations

**Model answer:** ACL translates models and protocols — not home for pricing policy. Extract tax rules to domain service behind port; ACL only maps SOAP XML ↔ domain commands. Cache: versioned tax tables with event-driven invalidation, never infinite TTL on money data. Strangler: new customers on REST billing, legacy on SOAP through thinning ACL. Contract tests from recorded SOAP fixtures; alert on translation error rate.

**Common weak answers:** Adding features to ACL because SOAP is hard.

**Follow-up probes (with answers):**

**Q:** ACL vs Facade?
**A:** ACL translates foreign model at integration boundary; Facade simplifies internal subsystem — different intent.

---

### S10. Event sourcing replay breaks after schema change

**Situation:** Order aggregate event-sourced. V2 event adds mandatory field; replay of V1 events fails in staging. Production migration scheduled next week.

**What they're testing:** Event versioning, upcasting, migration strategy.

**How to structure your answer:**
- Versioning strategy (upcaster, dual write)
- Replay testing in CI
- Snapshot strategy
- When not to event source

**Model answer:** Never break replay — add OrderCreatedV2 with upcaster from V1 filling default for new field. CI job replays production snapshot into empty store nightly. Snapshots every N events reduce replay time; snapshot schema also versioned. If team lacks versioning discipline, event sourcing was premature — audit table + state machine may suffice. Deploy: dual-write new events only after upcaster deployed; no in-place edit of historical events.

**Common weak answers:** Editing historical events in place; skipping replay tests.

**Follow-up probes (with answers):**

**Q:** Event sourcing vs audit table?
**A:** Event sourcing replays to derive state; audit is supplementary log — choose based on replay need not hype.

---

## Full pattern catalog (181 patterns)

All patterns from the [Java Design Patterns catalog](https://java-design-patterns.com/patterns/) have **scenario-based Q&A** in **[pattern-catalog.md](./pattern-catalog.md)** (P001–P181). Use that file when an interviewer names a pattern from the catalog or asks "how would you apply X in production?"

## Pattern → Spring / Cloud cheat sheet

| Pattern | Where you already use it |
|---------|--------------------------|
| Proxy | `@Transactional`, `@Async`, `@Cacheable` |
| Template Method | `JdbcTemplate`, `KafkaTemplate` |
| Observer | `ApplicationEvent` |
| Factory | `@Bean`, `ObjectFactory` |
| Builder | `UriComponentsBuilder`, Lombok |
| Adapter | Controllers, Kafka listeners |
| Facade | BFF, service layer |
| Chain | Security filters |
| Circuit breaker | Resilience4j |
| Saga / Outbox | Microservices |
---
