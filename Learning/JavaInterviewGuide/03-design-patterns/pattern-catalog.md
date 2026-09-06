# Design Pattern Catalog — Scenario-Based Q&A (181 patterns)

**Source:** [Java Design Patterns catalog](https://java-design-patterns.com/patterns/) (iluwatar, MIT licensed).

**How to use:** After the 50 senior interview questions in [questions.md](./questions.md), drill individual patterns here. Each entry has a **production scenario** and **model answer** you can speak for 2–3 minutes.

**Index:** P001–P045 (Creational → Decorator) · P046–P090 (Delegation → Lockable Object) · P091–P135 (MapReduce → Property) · P136–P181 (Prototype → Write-Ahead Log)

---

# Design Pattern Catalog — Part 1 (P001–P045)

Scenario-based senior interview Q&A aligned with [java-design-patterns.com](https://java-design-patterns.com/patterns/).

---

### P001. Abstract Document

**Category:** Structural
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/abstract-document/)

**Short answer:** Abstract Document stores hierarchical data in a loosely typed property map while exposing typed trait interfaces for safe access. It shines when product schemas evolve weekly—new attributes land without migrations or class explosions. Trade-off: you lose compile-time guarantees on keys and pay casting/validation cost at read time. It hurts when auditors demand rigid schemas, when ORM mapping is simpler, or when runtime type errors in production are unacceptable.

#### Scenario (interview)
**Situation:** Your Azure-hosted insurance quoting service ingests JSON from three partner APIs (motor, home, travel) with overlapping but inconsistent fields. Product owners add optional riders mid-sprint. The team debates subclassing `Quote` per product line versus a flexible document model behind Spring `@RestController` endpoints.
**What they're testing:** Whether you can model semi-structured domain data without an inheritance tree; awareness of validation and schema drift.
**Model answer:** I'd model each quote as an `AbstractDocument` backed by a `Map<String,Object>` with trait interfaces like `HasPremium`, `HasCoverageLimits`, and `HasRiders`. Incoming partner JSON maps directly into the document; typed views give underwriters readable accessors without fifty POJO variants. Validation runs at the boundary—Bean Validation on extracted traits, JSON Schema for unknown partners. When motor adds `telematicsDiscount`, we extend a trait interface; existing code compiles because absent keys return `Optional.empty()`. I would not use this for ledger postings or regulated policy storage—that stays in normalized JPA entities. For the quote aggregation layer feeding Kafka to pricing engines, the flexibility outweighs the loss of static typing. I'd add contract tests per partner schema and metrics on unknown keys so drift is visible before quotes fail silently.

#### What it is
Abstract Document separates storage (key-value tree) from typed access (trait interfaces). Documents can nest children as sub-documents. It is essentially a strongly typed façade over dynamic maps—common in CMS, config, and integration payloads.

#### When to use / when NOT
- **Use** when entity shapes vary by type/version and change frequently without DB migrations.
- **Use** when you need one traversal mechanism over heterogeneous trees (quotes, content nodes, feature flags).
- **NOT** when financial correctness requires enforced invariants at compile time—use records/entities.
- **NOT** when query patterns need SQL indexes on every attribute—normalize instead.
- **NOT** when team lacks discipline for boundary validation; dynamic maps become bug factories.

#### Java / Spring example
```java
public class PolicyQuote extends AbstractDocument implements HasPremium, HasProductCode {
    public PolicyQuote(Map<String, Object> props) { super(props); }
}
// Spring: ObjectMapper converts partner JSON → Map → PolicyQuote at @ControllerAdvice boundary
```

#### Common mistakes
- Treating the property map as the system of record without versioning or migration strategy.
- Skipping validation because "it's flexible"—runtime `ClassCastException` in production.
- Creating a trait interface per partner instead of per domain concept, reintroducing duplication.

#### Follow-up (with answer)
**Q:** How do you prevent two teams from using different keys for the same concept?
**A:** Establish a canonical key registry (enum or schema repo) and enforce it in CI with JSON Schema or Avro contracts. Trait interfaces reference only canonical keys; adapters normalize partner-specific names at ingress. For Kafka, publish schema-registry subjects so consumers reject unknown fields. Code review checks that new traits don't duplicate semantics. This keeps flexibility at the edges while the domain vocabulary stays stable.

---

### P002. Abstract Factory

**Category:** Creational
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/abstract-factory/)

**Short answer:** Abstract Factory provides an interface for creating families of related objects without naming concrete classes. It enforces consistency—Azure Service Bus clients and serializers from the same factory can't be mismatched. Trade-off: every new product in the family touches the factory hierarchy. It hurts for single implementations, when Spring `@ConditionalOnProperty` already selects beans, or when families rarely need to stay in sync.

#### Scenario (interview)
**Situation:** A payments platform supports card, ACH, and open-banking rails. Each rail needs `PaymentGateway`, `IdempotencyStore`, `WebhookVerifier`, and `ReconciliationExporter` that must be vendor-consistent (Stripe family vs Adyen family). Spring Boot multi-tenant config picks the family per merchant at runtime.
**What they're testing:** Family consistency vs simple Factory Method; configuration-driven object graphs.
**Model answer:** I'd define `PaymentPlatformFactory` with methods `createGateway()`, `createIdempotencyStore()`, `createWebhookVerifier()`, and `createReconciliationExporter()`. Implementations `StripePlatformFactory` and `AdyenPlatformFactory` ensure no Stripe gateway pairs with an Adyen verifier—a mistake that caused a production incident at my last team. Spring registers one factory bean per `payment.vendor` property; `PaymentOrchestrator` depends only on the interface. Adding Pix in Brazil means a new factory implementation, not scattered `if/else` in services. I wouldn't use Abstract Factory for a single `RestTemplate` or one-off S3 client—`@Bean` methods suffice. Integration tests spin each factory with WireMock stubs. The interview trap is conflating this with Factory Method: here the unit of consistency is the entire family, not one product type.

#### What it is
Abstract Factory encapsulates creation of multiple related products behind one interface. Clients depend on abstractions for both the factory and products. It pairs naturally with dependency injection when vendor or environment switches entire stacks.

#### When to use / when NOT
- **Use** when products must be used together and mixing implementations is a defect.
- **Use** when switching environments (cloud vendor, DB dialect) replaces whole subgraphs.
- **NOT** for one or two unrelated objects—use Factory Method or `@Bean`.
- **NOT** when Spring profiles already express the matrix cleanly without extra interfaces.
- **NOT** when new product types appear weekly—factory interface becomes a change bottleneck.

#### Java / Spring example
```java
public interface MessagingFactory {
    TopicPublisher publisher();
    TopicSubscriber subscriber();
    DeadLetterHandler dlq();
}
// @Configuration @ConditionalOnProperty("messaging.provider=azure")
class AzureServiceBusMessagingFactory implements MessagingFactory { ... }
```

#### Common mistakes
- Exploding factories for every class instead of true product families.
- Returning concrete types from factory methods, breaking test doubles.
- Forgetting thread-safety when factories cache expensive clients (HTTP connection pools).

#### Follow-up (with answer)
**Q:** Abstract Factory vs Factory Method in Spring?
**A:** Factory Method is one product per creator—`ConnectionFactory.createConnection()`. Abstract Factory creates coordinated sets. In Spring, a `@Configuration` class with multiple `@Bean` methods is often an implicit abstract factory when beans are `@ConditionalOn` the same property. Explicit Abstract Factory helps when the family must be selected atomically at runtime per tenant, not at context startup. Choose explicit interfaces when integration tests need to swap entire stacks without reloading the context.

---

### P003. Active Object

**Category:** Concurrency
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/active-object/)

**Short answer:** Active Object decouples method invocation from execution: calls enqueue on a service object's scheduler thread, returning futures or callbacks. Callers avoid blocking and explicit locking on shared state. Trade-off: harder debugging, ordering guarantees must be designed, and latency adds queue depth. It hurts for CPU-bound parallel work better served by `ForkJoinPool` or when synchronous semantics are required for transactions.

#### Scenario (interview)
**Situation:** A Spring service maintains an in-memory order book for a trading simulation consumed via WebSocket. Multiple Kafka consumers update bids; REST clients query best price. Contention on `synchronized` blocks causes p99 spikes under load tests on Azure AKS.
**What they're testing:** Thread confinement, async invocation, and when not to sprinkle locks everywhere.
**Model answer:** I'd wrap the order book in an Active Object: public methods like `submitBid` and `getBestBid` serialize through a dedicated single-thread executor owning all mutable state. Kafka listener threads enqueue updates; they receive `CompletableFuture` or fire-and-forget with backpressure via bounded queue. WebSocket broadcast reads snapshots immutable after each scheduler tick—no locks on hot path for readers. This differs from `@Async` on every method because state mutation stays on one thread by construction. I'd size the queue, monitor rejection policy, and document that `getBestBid` is eventually consistent within milliseconds. For persistence to Cosmos DB, a separate outbox thread drains committed snapshots. I would not Active-Object a stateless REST controller—that's just unnecessary indirection.

#### What it is
An Active Object has a method queue and a scheduler thread that executes requests sequentially against internal state. The proxy seen by clients forwards calls asynchronously. It combines Actor-like confinement with familiar OO method syntax.

#### When to use / when NOT
- **Use** when one shared mutable resource receives high concurrent updates and lock contention dominates.
- **Use** when callers should never block on internal serialization logic.
- **NOT** for embarrassingly parallel workloads across independent keys—use sharded actors or parallel streams.
- **NOT** when methods must participate in JTA transactions spanning threads.
- **NOT** when call ordering across different method types must be strictly interleaved with external systems without a formal protocol.

#### Java / Spring example
```java
public class OrderBookProxy implements OrderBook {
    private final OrderBookImpl servant = new OrderBookImpl();
    private final ExecutorService scheduler = Executors.newSingleThreadExecutor();
    public CompletableFuture<Quote> bestBid() {
        return CompletableFuture.supplyAsync(servant::bestBid, scheduler);
    }
}
```

#### Common mistakes
- Unbounded queue growth when producers outpace the scheduler—no backpressure.
- Blocking inside scheduled tasks (`Future.get()` on same executor) causing deadlock.
- Assuming Active Object equals `@Async`—Spring async uses pool threads without serializing state access.

#### Follow-up (with answer)
**Q:** How does Active Object compare to the Actor Model?
**A:** Both serialize access to internal state on a mailbox thread. Actors emphasize message passing and location transparency; Active Object keeps method-call ergonomics with futures. In Akka/Pekko you'd send `SubmitBid` messages; Active Object feels more Java-native for teams avoiding actor frameworks. Choose actors for distributed systems and supervision hierarchies; Active Object for single-JVM confinement with minimal framework commitment.

---

### P004. Actor Model

**Category:** Concurrency
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/actor-model/)

**Short answer:** The Actor Model treats concurrent entities as isolated units communicating only via asynchronous messages—no shared mutable state. It scales across threads and nodes with location-transparent addressing. Trade-off: eventual consistency, message ordering rules, and distributed debugging complexity. It hurts inside a simple CRUD monolith, when you need synchronous two-phase commit, or when the team lacks operational maturity for mailbox backlog monitoring.

#### Scenario (interview)
**Situation:** A fraud-detection pipeline on Azure processes payment events from Kafka. Each `accountId` must serialize scoring state, but accounts number in the millions. You evaluate Pekko Cluster vs cramming everything into a single `@Service` with `ConcurrentHashMap`.
**What they're testing:** Sharding, failure isolation, and message-driven design at scale.
**Model answer:** I'd shard account state by `accountId` hash into cluster entities—each account actor holds rolling velocity counters and device fingerprints. Kafka consumers become message routers: `ScorePayment` commands to the right shard, replies via `ask` pattern with timeout for synchronous API edges. Failed actors restart with supervision strategy; poison messages go to dead-letter topic. This beats a global lock map because hot accounts don't block cold ones, and we scale nodes horizontally. REST fraud checks use temporary ask actors with circuit breakers when shards are unreachable. I wouldn't actor-model a read-mostly product catalog—cache + DB is fine. Operational must-haves: mailbox depth metrics, stash capacity for burst traffic, and idempotent message handling for Kafka redelivery.

#### What it is
Actors encapsulate state and behavior; other actors send immutable messages to their mailbox. A dispatcher processes messages one at a time per actor instance. Supervision hierarchies define restart policies on failure.

#### When to use / when NOT
- **Use** for high-concurrency domain objects with natural identity keys (user, account, device).
- **Use** when you need cluster sharding and location-transparent scaling.
- **NOT** for request/response CRUD with mostly stateless services.
- **NOT** when strong cross-entity transactional invariants dominate—use saga orchestration explicitly.
- **NOT** without investment in observability (tracing message flows is harder than stack traces).

#### Java / Spring example
```java
// Apache Pekko
Behaviors.receiveMessage(ScorePayment cmd -> {
    state = scorer.apply(state, cmd);
    cmd.replyTo().tell(new ScoreResult(state.risk()));
    return Behaviors.same();
});
```

#### Common mistakes
- Blocking inside actors (`Thread.sleep`, JDBC) starving the dispatcher—use pipe-to-future patterns.
- Sharing mutable objects between actors instead of immutable messages.
- Ignoring at-least-once delivery—handlers must be idempotent.

#### Follow-up (with answer)
**Q:** How do you integrate actors with Spring Boot transaction boundaries?
**A:** Keep transactional JDBC/JPA outside actors or isolate DB access in pool-backed futures piped back as messages. An actor should not hold an open Hibernate session across messages. Typical pattern: actor decides, sends `PersistDecision` to a repository actor or calls a transactional service via `Patterns.ask` with a dedicated executor. Sagas coordinate multi-actor workflows with compensating messages instead of XA transactions.

---

### P005. Acyclic Visitor

**Category:** Behavioral
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/acyclic-visitor/)

**Short answer:** Acyclic Visitor extends Visitor by splitting visit methods across visitor interfaces so the element hierarchy doesn't force every visitor to depend on all element types—dependency graph stays acyclic. New element types don't break unrelated visitors. Trade-off: more interfaces, `instanceof` or dispatch helpers, and less compile-time exhaustiveness than sealed types. It hurts when Java 17+ `switch` on sealed hierarchies gives cleaner type-safe dispatch.

#### Scenario (interview)
**Situation:** A tax reporting module walks an AST of ledger entries (`Invoice`, `CreditNote`, `FxAdjustment`, `IntercompanyTransfer`). Compliance adds new entry types quarterly. The classic Visitor forced every report visitor to recompile when legal added `CarbonLevyEntry`, breaking unrelated export pipelines.
**What they're testing:** Open/closed principle vs Visitor rigidity; dependency management in large codebases.
**Model answer:** I'd define `LedgerVisitor` as a marker and small role interfaces: `InvoiceVisitor`, `CreditNoteVisitor`, etc. Each report implements only interfaces it cares about—`VatReportVisitor implements InvoiceVisitor, CreditNoteVisitor`. `accept` double-dispatches: element calls `visitor.visit(this)` only if visitor implements the matching sub-interface. Adding `CarbonLevyEntry` introduces `CarbonLevyVisitor`; VAT reports unchanged. This prevented our Maven reactor from rebuilding twelve modules per regulatory tweak. Modern alternative: sealed `LedgerEntry` with pattern-matching switch in each report—I'd choose Acyclic Visitor when third-party plugins implement visitors you don't control. Performance is fine for batch reporting; not for nanosecond hot loops.

#### What it is
Acyclic Visitor decomposes the monolithic Visitor interface into fine-grained visit interfaces. Elements test which visit interface a visitor supports before dispatching. The acyclic property means no circular dependencies between visitor and element packages.

#### When to use / when NOT
- **Use** when element hierarchy is stable but visitor types proliferate independently.
- **Use** in plugin architectures where modules can't depend on all element classes.
- **NOT** when sealed types + exhaustive switch covers all cases in one codebase.
- **NOT** for two or three node types—plain polymorphism is simpler.
- **NOT** when visitors must guarantee handling every element type at compile time.

#### Java / Spring example
```java
public interface InvoiceVisitor { void visit(Invoice i); }
public class Invoice implements LedgerEntry {
    public void accept(LedgerVisitor v) {
        if (v instanceof InvoiceVisitor iv) iv.visit(this);
    }
}
```

#### Common mistakes
- Forgetting to update `accept` when adding elements—silent skip instead of compile error.
- Spraying `instanceof` in business logic outside the accept method.
- Duplicating dispatch logic instead of a small `VisitorDispatcher` helper.

#### Follow-up (with answer)
**Q:** Acyclic Visitor vs double dispatch with sealed classes?
**A:** Sealed hierarchies with pattern matching give compile-time exhaustiveness when you own all types in one module. Acyclic Visitor wins when visitors live in separate JARs (plugins, country packs) that cannot depend on every entry class. For JDK 21+ internal reporting, I'd default to sealed `LedgerEntry`; for extensible partner tax plugins, Acyclic Visitor remains the pragmatic choice.

---

### P006. Adapter

**Category:** Structural
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/adapter/)

**Short answer:** Adapter translates one interface into another clients already expect—wrap a legacy or third-party API behind your port. It contains translation, error mapping, and sometimes retry semantics at the boundary. Trade-off: the adapter can become a god-class if it absorbs business rules. It hurts when you should fix the upstream contract, or when multiple adapters duplicate orchestration that belongs in an anti-corruption layer.

#### Scenario (interview)
**Situation:** Your Spring Boot order service exposes `InventoryPort.reserve(OrderLine)`. Operations acquired a warehouse whose REST API uses `POST /allocations` with XML bodies and session cookies—nothing like your internal port. Kafka-driven fulfillment must not rewrite the core domain.
**What they're testing:** Boundary isolation, mapping complexity, and where translation stops.
**Model answer:** I'd implement `LegacyWarehouseInventoryAdapter implements InventoryPort`. It maps `OrderLine` to their allocation schema, manages session renewal, translates `409 CONFLICT` to `InsufficientStockException`, and maps their `allocationId` to our `ReservationId` value object. Resilience4j retry handles transient 503s; metrics tag `adapter=legacy-warehouse`. Domain services stay ignorant of XML and cookies. Unit tests use WireMock fixtures recorded from staging. I'd resist putting promo-pricing logic in the adapter—that belongs in domain services. If five more warehouses share patterns, extract shared mapping utilities but keep per-vendor adapter classes. This is structural glue, not architecture: for semantic mismatch at scale, elevate to Anti-Corruption Layer with explicit bounded context translation.

#### What it is
Adapter implements the target interface by delegating to an adaptee, converting calls and data shapes. Object adapter uses composition; class adapter uses inheritance (rare in Java). It's the workhorse of integration code.

#### When to use / when NOT
- **Use** when you cannot change a third-party or legacy API but need a stable internal contract.
- **Use** at hexagonal architecture ports for infrastructure implementations.
- **NOT** when you own both sides—change the API instead.
- **NOT** when translation requires rich domain re-modeling—use ACL + dedicated translators.
- **NOT** when a generated OpenAPI client already matches your port with thin configuration.

#### Java / Spring example
```java
@Component
class AzureBlobStorageAdapter implements DocumentStoragePort {
    private final BlobServiceClient client;
    public URI upload(Document doc) { /* map + delegate */ }
}
```

#### Common mistakes
- Leaking adaptee types (returning vendor SDK objects from port methods).
- Swallowing exceptions without mapping to domain error taxonomy.
- Caching adapter state that should be request-scoped (stale auth tokens).

#### Follow-up (with answer)
**Q:** Adapter vs Facade?
**A:** Adapter changes interface to match what the client expects—one legacy class, one target port. Facade simplifies a subsystem of many classes behind a coarse API for convenience. An adapter makes `LegacyWarehouse` look like `InventoryPort`; a facade might expose `fulfillment()` bundling inventory, shipping, and label printing. You often combine them: facade internally uses multiple adapters.

---

### P007. Ambassador

**Category:** Structural
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/ambassador/)

**Short answer:** Ambassador is a specialized proxy that offloads cross-cutting remote-call concerns—retries, circuit breaking, logging, connection pooling—from the client to a local representative. The remote service interface stays unchanged; the ambassador sits in-process. Trade-off: extra hop and configuration duplication if you also have a service mesh. It hurts when Istio/Linkerd already handle retries uniformly, or for in-process calls with no remote failure modes.

#### Scenario (interview)
**Situation:** Microservices on AKS call a legacy mainframe pricing COBOL bridge via HTTP. Every team copied retry loops and timeout tuning into their `RestTemplate` beans. Incidents show thundering herds when the mainframe degrades.
**What they're testing:** Client-side resilience patterns vs mesh; DRY for remote access.
**Model answer:** I'd introduce `PricingServiceAmbassador implements PricingService` wrapping the real HTTP client. It centralizes Resilience4j circuit breaker, exponential backoff, bulkhead limiting concurrent mainframe calls, and structured logging with correlation IDs from MDC. Application services inject `PricingService`—they never configure retries. Ambassador tracks failure rates and half-open probes; when open, fail fast with cached tariff tables or degraded pricing flag. This differs from a generic Adapter because the remote contract is already correct—we add operational behavior. With a service mesh handling retries, I'd slim the ambassador to metrics and request shaping only. Integration tests verify breaker opens after N failures. Senior point: one ambassador per remote dependency, not one mega-wrapper for all HTTP.

#### What it is
Ambassador acts as an in-process representative for a remote service, handling network-related reliability and observability. It's a Proxy focused on distributed systems ergonomics rather than lazy loading or access control.

#### When to use / when NOT
- **Use** for legacy or fragile remote dependencies shared by many callers.
- **Use** when you need consistent retry/breaker policy without a mesh.
- **NOT** when a service mesh or API gateway owns resilience uniformly.
- **NOT** for local in-JVM beans—plain DI without network concerns.
- **NOT** when retrying non-idempotent POSTs without explicit idempotency keys.

#### Java / Spring example
```java
@Component
class CreditBureauAmbassador implements CreditBureauPort {
    private final RemoteCreditBureau remote;
    private final CircuitBreaker breaker = CircuitBreaker.ofDefaults("bureau");
    public CreditReport fetch(String ssn) {
        return breaker.executeSupplier(() -> remote.fetch(ssn));
    }
}
```

#### Common mistakes
- Retrying non-idempotent operations blindly, causing duplicate side effects.
- Hiding breaker state from callers that need to surface degraded-mode UX.
- Duplicating mesh retry policies, amplifying retry storms.

#### Follow-up (with answer)
**Q:** Ambassador vs Sidecar pattern?
**A:** Ambassador is a library/process-local proxy your code instantiates; Sidecar is a separate container (Envoy, Dapr) colocated with the pod handling traffic transparently. Ambassador gives language-native APIs and unit-testable policies; Sidecar works across polyglot services without per-language SDKs. Many teams use both—mesh for L4/L7 routing, ambassador for domain-aware fallbacks like stale cache pricing.

---

### P008. Anti-Corruption Layer

**Category:** Architectural
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/anti-corruption-layer/)

**Short answer:** An Anti-Corruption Layer (ACL) translates between bounded contexts so upstream model pollution doesn't infect your domain. It is thicker than an adapter—explicit translators, facades, and sometimes event reification. Trade-off: maintenance of mapping as both sides evolve, latency, and duplicate data representations. It hurts when teams share a canonical model legitimately, or when the integration is a one-field lookup with no semantic drift.

#### Scenario (interview)
**Situation:** Your `Billing` context uses rich aggregates (`Subscription`, `Invoice`, `TaxLine`). Salesforce remains the CRM source of truth with flat `Opportunity` objects and picklists that don't match your enums. Product wants bidirectional sync via Kafka and Azure Event Hubs without Billing importing Salesforce SDK types.
**What they're testing:** DDD boundaries, translation ownership, and long-term evolution.
**Model answer:** I'd place an ACL module between contexts: `CrmSalesforceFacade` exposes use-case methods (`syncClosedWonDeal`), internal translators map `Opportunity` DTOs to `SubscriptionDraft` commands, and anti-corruption enums isolate picklist magic strings. Kafka consumers in the ACL layer publish domain events Billing understands—`DealQualifiedForBilling`—never raw Salesforce change events. Billing developers never import `com.salesforce.*`. When CRM adds custom fields, only ACL tests break. I'd version translators, keep mapping tables for enum drift in DB, and reject "just use their model in our service" shortcuts that caused a prior `$0 invoice` bug from misread stage codes. ACL is not a dumping ground for all integration code—business rules about *when* to bill stay in Billing; ACL answers *what does this foreign thing mean*.

#### What it is
ACL is a strategic DDD pattern: a translating layer that converts foreign models into your ubiquitous language. It often combines facades, adapters, and dedicated translator classes with explicit tests for semantic mapping.

#### When to use / when NOT
- **Use** when integrating legacy or partner systems with incompatible domain models.
- **Use** when multiple teams own contexts and shared libraries would couple them.
- **NOT** for internal modules sharing a kernel domain model.
- **NOT** when generated clients already align semantically with your aggregates.
- **NOT** as excuse to duplicate business rules that should move to one context.

#### Java / Spring example
```java
// acl-salesforce module
public class OpportunityToSubscriptionTranslator {
    public SubscriptionDraft translate(OpportunityDto opp) { /* semantic mapping */ }
}
```

#### Common mistakes
- Thin ACL that's just DTO copy—missing semantic translation (currency, timezone, status).
- Letting foreign IDs leak as primary keys in your aggregates.
- No contract tests when external schema changes silently.

#### Follow-up (with answer)
**Q:** ACL vs hexagonal port-adapter?
**A:** Hexagonal architecture defines ports and adapters as a structural style; ACL is a strategic boundary pattern with explicit translation philosophy. Every ACL uses adapters; not every adapter is an ACL. ACL implies semantic re-modeling and protection from foreign concepts; a simple S3 adapter maps API shapes without defending a bounded context. Name ACL when organizational boundaries and model corruption risk justify a dedicated module and team ownership.

---

### P009. Arrange/Act/Assert

**Category:** Testing
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/arrange-act-assert/)

**Short answer:** Arrange/Act/Assert (AAA) structures tests into setup, execution, and verification phases for readability and single-behavior focus. It reduces tests that accidentally assert setup side effects. Trade-off: verbose for trivial tests; discipline required to keep one logical act. It hurts when tests are really integration scenarios needing Given/When/Then narrative for BDD stakeholders, or when excessive arrange blocks hide missing test fixtures.

#### Scenario (interview)
**Situation:** A Spring Kafka consumer test suite flakily fails in CI. Tests interleave `mockMvc` setup, message publishing, and assertions in random order. New hires can't tell whether failure is arrange pollution or production bug.
**What they're testing:** Test craftsmanship, maintainability, and senior influence on engineering standards.
**Model answer:** I'd mandate AAA with blank-line separators and naming: `shouldEmitRefund_whenChargebackReceived`. Arrange: build `ChargebackEvent`, stub `PaymentRepository`, load `@SpringBootTest` context minimal slice. Act: publish to embedded Kafka topic, await `Awaitility` on outbox. Assert: verify `RefundCommand` published, `Payment` status `REFUNDED`, no further interactions on mocks. Forbidden: asserting mock behavior in arrange, multiple acts without separate tests. For complex domains, extract `ChargebackFixtures` and `KafkaTestSupport`—arrange stays readable. BDD `Given/When/Then` maps 1:1 to AAA for Cucumber glue. I'd fix flakiness by scoping one consumer group per test and deterministic clocks. Senior bar: tests document behavior; AAA makes the story scannable in PR review under time pressure.

#### What it is
AAA is a test organization pattern: prepare state, invoke system under test once, verify outcomes. It aligns with single assertion concept philosophically though multiple related asserts on one act are fine.

#### When to use / when NOT
- **Use** for unit and integration tests where clarity reduces maintenance cost.
- **Use** in code review standards for teams above ~10 engineers.
- **NOT** as dogma forbidding helper methods that obscure the three phases.
- **NOT** when property-based tests interleave generation—use explicit structure in callbacks.
- **NOT** replacing descriptive BDD scenarios where product owners read feature files.

#### Java / Spring example
```java
@Test
void shouldRejectExpiredToken() {
  // Arrange
  var token = jwtFactory.expiredFor("user-1");
  // Act
  var result = authService.validate(token);
  // Assert
  assertThat(result).isFailure().satisfies(e -> assertThat(e).isInstanceOf(TokenExpiredException.class));
}
```

#### Common mistakes
- Multiple acts in one test masking which behavior broke.
- Asserting on mocks before invoking the system under test.
- Giant arrange blocks without fixtures—copy-paste drift.

#### Follow-up (with answer)
**Q:** AAA vs Given/When/Then—is one better?
**A:** They're structurally identical; BDD names suit stakeholder-readable scenarios in Gherkin, while AAA suits developer-facing JUnit. In Spring projects I use AAA in unit tests and Given/When/Then in Cucumber features for cross-team specs. Consistency matters more than label—never mix random ordering. Extract builders when arrange exceeds ~15 lines.

---

### P010. Async Method Invocation

**Category:** Concurrency
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/async-method-invocation/)

**Short answer:** Async Method Invocation returns immediately with a future or callback while work runs on another thread. It improves throughput for I/O-bound workflows but shifts complexity to composition, error handling, and context propagation. Trade-off: broken `ThreadLocal` (security, tracing), lost transaction boundaries. It hurts when the operation is fast CPU work, when callers always need synchronous results, or when `@Async` is sprinkled without a custom executor policy.

#### Scenario (interview)
**Situation:** Order confirmation must email the customer, push to CRM, and warm analytics caches. Synchronous Spring `@RestController` p99 hit 2.8s on Azure because `sendEmail` waited on SendGrid. Product insists API returns `202` with `orderId` immediately.
**What they're testing:** Spring `@Async`, `CompletableFuture` composition, MDC/trace propagation, failure compensation.
**Model answer:** I'd refactor post-commit side effects to async invocation: `@TransactionalEventListener(phase = AFTER_COMMIT)` triggers `OrderSideEffectOrchestrator` methods returning `CompletableFuture<Void>`. Custom `TaskExecutor` with MDC decorator propagates trace IDs to child threads; Micrometer context snapshot for `@Async`. API returns after DB commit; `CompletableFuture.allOf` handles email+CRM in parallel with per-task exception logging to DLQ—not silent swallow. Failed email doesn't roll back order—that's the point—but alerts fire and retry job picks up. I configure pool sizes separately from Tomcat threads to avoid starvation. Never `@Async` self-invocation without proxy exposure. For Kafka, prefer publish event and let consumers async—async method invocation suits in-process fan-out before extraction.

#### What it is
Async Method Invocation decouples caller thread from execution thread using futures, callbacks, or message queues. In Java/Spring it's commonly `@Async`, `CompletableFuture.supplyAsync`, or reactive `Mono`.

#### When to use / when NOT
- **Use** for fire-and-forget or parallelizable side effects after a definitive commit.
- **Use** when client latency SLA is tighter than downstream dependency latency.
- **NOT** inside the same DB transaction—you'll read uncommitted state or lose rollback semantics.
- **NOT** without defined error handling—unhandled async exceptions disappear.
- **NOT** when ordering guarantees matter unless you serialize on a dedicated executor.

#### Java / Spring example
```java
@Async("notificationExecutor")
public CompletableFuture<Void> sendReceipt(Order order) {
    mailClient.send(order);
    return CompletableFuture.completedFuture(null);
}
```

#### Common mistakes
- Calling `@Async` methods from same class (no proxy, runs synchronously).
- Losing Spring Security context and MDC on worker threads.
- Unbounded default `SimpleAsyncTaskExecutor` creating threads per call.

#### Follow-up (with answer)
**Q:** `@Async` vs reactive WebFlux for the same problem?
**A:** `@Async` fits imperative Spring MVC codebases needing incremental async without rewriting stacks. WebFlux shines for high-concurrency I/O with backpressure end-to-end. Choose `@Async` when 80% of code is blocking JDBC today and migration cost is high; choose reactive when Netty pipeline and non-blocking drivers are already standard. Hybrid is valid: MVC controller returns 202, `@Async` orchestrates, Kafka for durable async.

---

### P011. Backends For Frontends

**Category:** Microservices
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/backends-for-frontends/)

**Short answer:** Backends For Frontends (BFF) dedicates an API layer per client experience—mobile, web, partner—aggregating microservices into shapes each UI needs. It prevents one generic API from over-fetching or leaking internal domain churn. Trade-off: more deployables, duplicated aggregation logic if discipline slips. It hurts for a single SPA with stable needs, when GraphQL federation solves aggregation cleanly, or when BFFs become thick business layers duplicating domain rules.

#### Scenario (interview)
**Situation:** A retail bank has iOS, Android, and branch-teller web apps hitting the same Spring Cloud Gateway routes. Mobile needs lightweight account summaries; teller UI needs full audit trails and override workflows. Mobile releases weekly; core `AccountService` cannot break for every screen field tweak.
**What they're testing:** API composition, team topology, and avoiding god-gateway anti-patterns.
**Model answer:** I'd deploy `mobile-bff` and `teller-bff` as separate Spring Boot apps behind Azure API Management. Mobile BFF aggregates `AccountService`, `CardService`, and `RewardsService` into one `AccountDashboardDto` with field filtering and aggressive caching; teller BFF adds `AuditService` and privileged endpoints with stricter auth. Core services stay client-agnostic REST with stable contracts. BFF owns presentation concerns—date formatting, combining nicknames—not interest calculation. GraphQL is an option for mobile, but BFF with OpenAPI gives clearer ownership per squad. I'd guard against BFF calling BFF chains and enforce timeouts per downstream. Contract tests from mobile consumer-driven contracts validate BFF responses. When logic creeps in ("mobile gets a different overdraft rule"), that's a domain smell—push back to shared services.

#### What it is
BFF is an experience-specific backend that orchestrates calls to microservices and shapes responses for one client type. Sam Newman popularized it as part of microservices UX strategy; each channel team often owns its BFF.

#### When to use / when NOT
- **Use** when client needs diverge materially in payload shape, auth, or release cadence.
- **Use** to shield mobile from chatty microservice graphs.
- **NOT** for one admin UI and one public API with identical shapes.
- **NOT** when a federated GraphQL layer with field-level auth is already invested.
- **NOT** as a place for transactional business rules—keep domain in core services.

#### Java / Spring example
```java
@RestController
class MobileAccountBffController {
    public AccountDashboard mobileDashboard(String customerId) {
        return aggregator.build(customerId, FieldSet.MOBILE_SUMMARY);
    }
}
```

#### Common mistakes
- BFF becomes a second monolith with business logic and database access.
- N+1 HTTP calls to microservices without batch endpoints or caching.
- Sharing one BFF across mobile and web, defeating the pattern's purpose.

#### Follow-up (with answer)
**Q:** BFF vs API Gateway—where does each stop?
**A:** API Gateway handles cross-cutting ingress: TLS termination, rate limiting, JWT validation, routing. BFF sits behind or beside gateway as an application service composing domain APIs for one client. Gateway shouldn't know mobile needs `AccountDashboard`; BFF shouldn't replace WAF policies. Azure APIM routes `/mobile/*` to mobile-bff; gateway policies apply uniformly. Keep gateway thin; keep BFF replaceable per channel team.

---

### P012. Backpressure

**Category:** Performance
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/backpressure/)

**Short answer:** Backpressure signals slow consumers to producers so fast sources don't overwhelm memory or downstream systems. In reactive streams it's first-class; in imperative code it's bounded queues and drop/reject policies. Trade-off: added latency, dropped work, or complex flow-control tuning. It hurts when misapplied to batch ETL that should simply scale consumers, or when blocking the producer causes deadlock in synchronous pipelines.

#### Scenario (interview)
**Situation:** A Kafka consumer group ingesting IoT telemetry on Azure processes 200k msgs/sec peaks. During deploy, one pod lag spikes; without limits, in-memory `LinkedBlockingQueue` in a custom aggregator OOMKilled the JVM and poisoned the consumer group.
**What they're testing:** Reactive vs imperative flow control, Kafka pause/resume, operational limits.
**Model answer:** I'd implement backpressure at multiple layers. Kafka consumer: reduce `max.poll.records`, tune `fetch.max.bytes`, and use `consumer.pause()` when internal queue exceeds watermark—resume when drained. Processing pipeline uses Reactor `Flux` with `onBackpressureBuffer` bounded strategy or drops with metrics for shed load. For Spring `@KafkaListener`, separate poll thread from processing executor with bounded queue and `CallerRunsPolicy` so producer naturally slows. Alert on lag, queue depth, and shed count—not just CPU. During incidents, idempotent processing lets safe replay after catch-up. I wouldn't block Kafka poll thread indefinitely—that triggers rebalance storms. Senior nuance: backpressure is a policy choice (buffer, drop latest, sample) agreed with product for telemetry vs payments.

#### What it is
Backpressure is a flow-control mechanism where downstream demand regulates upstream production. It prevents unbounded buffering and cascading failures when producers outpace consumers.

#### When to use / when NOT
- **Use** in streaming pipelines with variable production/consumption rates.
- **Use** when memory is finite and message loss or sampling is acceptable under overload.
- **NOT** when every message must be processed and the fix is horizontal scale-out.
- **NOT** without metrics—operators can't tune what they can't see.
- **NOT** by unbounded `LinkedBlockingQueue` pretending to be a solution.

#### Java / Spring example
```java
kafkaReceiver.receive()
    .limitRate(500)
    .onBackpressureBuffer(10_000, BufferOverflowStrategy.DROP_LATEST)
    .flatMap(this::process, 32);
```

#### Common mistakes
- Unbounded queues between stages masking consumer slowness until OOM.
- Pausing Kafka consumer without monitoring rebalance risk.
- Applying drop policies to financial events without business sign-off.

#### Follow-up (with answer)
**Q:** How do you test backpressure behavior?
**A:** Load tests with artificially slow consumers—inject `Thread.sleep` or limited executor pools—and assert queue caps, shed metrics, and no OOM. Chaos experiments pause downstream Azure Service Bus subscribers while producers run. Unit-test bounded queue rejection paths. Verify recovery: after consumer speeds up, lag drains without duplicate side effects if processing is idempotent.

---

### P013. Balking

**Category:** Concurrency
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/balking/)

**Short answer:** Balking refuses to act when conditions aren't right—return immediately instead of blocking or queuing. Common for "only one refresh at a time" or rejecting calls while shutting down. Trade-off: callers must handle rejection or retry; can surprise API consumers expecting blocking. It hurts when work must never be dropped—use queuing or backpressure instead—or when rejection storms need coordinated retry jitter.

#### Scenario (interview)
**Situation:** A Spring `@Scheduled` job refreshes FX rates into a local Caffeine cache. User requests also trigger refresh on stale miss. During market volatility, hundreds of threads hit `refresh()` simultaneously, hammering the external ECB API and getting rate-limited.
**What they're testing:** Non-blocking coordination, `AtomicBoolean`/`tryLock` patterns, graceful degradation.
**Model answer:** I'd implement balking on `FxRateCache.refreshIfStale()`: if another thread is refreshing (`AtomicBoolean` compareAndSet), return immediately—serving slightly stale rates within SLA—or return `Optional.empty()` for strict paths. Only the winning thread calls ECB API; others balk. This differs from `synchronized` wait which queues threads and amplifies load. On shutdown, `Lifecycle` sets `accepting=false` and new refreshes balk while in-flight completes. Metrics: `fx_refresh_balked_total`. For trading desk needing fresh rates, expose explicit `forceRefresh()` with separate bulkhead. Balking fits optional enhancement work; payment authorization that must queue belongs on a proper executor with backpressure, not silent balk.

#### What it is
Balking checks preconditions (lock held, wrong state, shutdown) and exits early without executing the operation. It's the opposite of blocking until ready—fail fast or no-op instead.

#### When to use / when NOT
- **Use** when duplicate concurrent work is wasteful and stale data is acceptable briefly.
- **Use** during graceful shutdown to reject new work while draining in-flight.
- **NOT** when every request must eventually be processed—queue instead.
- **NOT** without documenting client-visible behavior (HTTP 503 vs silent stale read).
- **NOT** as lazy substitute for proper single-flight caching without metrics.

#### Java / Spring example
```java
public Optional<Rates> refreshIfStale() {
    if (!refreshing.compareAndSet(false, true)) return Optional.ofNullable(cached);
    try { return Optional.of(fetchAndStore()); }
    finally { refreshing.set(false); }
}
```

#### Common mistakes
- Balking without returning useful fallback data—users see errors unnecessarily.
- Using balk for financial correctness paths that require exactly-once processing.
- Race between check and act without atomic guard.

#### Follow-up (with answer)
**Q:** Balking vs double-checked locking for cache refresh?
**A:** Double-checked locking ensures one initializer with others waiting for result—appropriate when stale miss is unacceptable. Balking lets waiters proceed immediately with old data or skip work—appropriate when duplicate refresh is pure waste. Choose balk for high-churn optional caches; choose single-flight future (`CompletableFuture` dedup) when all waiters need the fresh value without N API calls.

---

### P014. Bloc

**Category:** Behavioral
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/bloc/)

**Short answer:** Bloc (Business Logic Component) separates presentation from business logic via event-driven state transitions—UI dispatches events, Bloc emits states. Originating in Flutter, the pattern applies wherever unidirectional data flow reduces UI bugs. Trade-off: boilerplate for simple screens, learning curve for imperative UI teams. It hurts for trivial forms, server-rendered Thymeleaf pages, or when Redux/MVI already standardize the frontend.

#### Scenario (interview)
**Situation:** A bank's Android and internal React admin panel both consume the same loan-application workflow API. Product reports inconsistent UI states—spinners stuck, double-submit—because each client mutates local state ad hoc. Architects propose a shared state machine contract.
**What they're testing:** Unidirectional flow, testability of UI logic, cross-platform consistency.
**Model answer:** On mobile I'd adopt Bloc: events like `SubmitIncome`, `UploadDocument` flow into `LoanApplicationBloc`, which calls Spring APIs and emits states `Loading`, `ValidationError`, `Submitted`. UI is a pure function of state—no `setLoading(true)` scattered in fragments. Business rules (minimum income, doc completeness) live in Bloc, unit-tested without Espresso. For React admin, equivalent pattern is Redux Toolkit slice or XState machine mirroring the same state names for supportability. Server remains source of truth for persistence; Bloc handles optimistic UI and error recovery. I wouldn't Bloc a static settings page. Kafka events for backend workflow don't replace client Bloc—they notify when server state advances. Senior point: align event/state names with OpenAPI and workflow engine states to reduce translation bugs.

#### What it is
Bloc manages state transitions in response to events, exposing streams of states to the UI. It enforces unidirectional data flow: Event → Bloc → State → UI, with UI sending only events back.

#### When to use / when NOT
- **Use** for multi-step workflows with complex async UI state.
- **Use** when you need testable presentation logic independent of widgets.
- **NOT** for read-only dashboards with no interaction state machine.
- **NOT** when team is small and MVVM with LiveData/Signals suffices.
- **NOT** duplicating server workflow rules that should be authoritative in backend.

#### Java / Spring example
```java
// Server-side analogue for SSE-driven admin UI
class ApplicationWorkflowEngine {
    State on(Event e, State current) { return switch (e) { case Submit s -> validate(s); ... }; }
}
```

#### Common mistakes
- Putting HTTP calls directly in UI instead of Bloc layer.
- God-bloc handling unrelated features—split by bounded screen scope.
- State explosion without sealed hierarchy or union types for impossible states.

#### Follow-up (with answer)
**Q:** Bloc vs MVVM on Android with Spring backend?
**A:** MVVM binds ViewModel observables to UI; Bloc is stricter event-in/state-out with explicit transition logs. Bloc excels when auditability of transitions matters (finance flows) and tests target event sequences. MVVM is lighter for CRUD lists. With Spring, keep domain validation server-side; Bloc handles presentation validation and orchestrates API calls, never trusting client-only rules for compliance.

---

### P015. Bridge

**Category:** Structural
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/bridge/)

**Short answer:** Bridge splits abstraction from implementation so both can vary independently—`Notification` abstraction with `EmailSender`/`SmsSender` implementations without N×M subclass explosion. Trade-off: indirection and more interfaces upfront. It hurts when only one implementation exists, when Spring `@Qualifier` solves the matrix, or when abstraction/implementation aren't truly independent axes.

#### Scenario (interview)
**Situation:** A compliance platform sends alerts as email, SMS, Teams, or ServiceNow tickets. Each channel has prod/sandbox implementations (SendGrid vs Mailhog, real Twilio vs stub). Product adds `EscalatedAlert` vs `InformationalAlert` types with different templates but same delivery channels.
**What they're testing:** Composition over inheritance, avoiding `EscalatedEmailAlert`, `EscalatedSmsAlert` class explosion.
**Model answer:** I'd model `Alert` abstraction with `render()` and composed `DeliveryChannel` implementation interface (`send(payload)`). `EscalatedAlert` and `InformationalAlert` are refinements; `SendGridChannel`, `TwilioChannel` implement delivery. Spring injects channel beans per profile—`@Profile("prod")`. New channel adds one implementation, not subclasses per alert type. This is Bridge, not Strategy alone, because alert type hierarchy and channel hierarchy vary independently. Tests use in-memory `CapturingChannel`. Anti-pattern: if only email ever exists, YAGNI—single service class. Bridge pays off when we've already lived through combinatorial subclass pain during a multi-region Azure rollout with different vendors per geography.

#### What it is
Bridge decouples an abstraction hierarchy from an implementation hierarchy via composition (bridge reference). Changes on one side don't force changes on the other.

#### When to use / when NOT
- **Use** when two dimensions of variation multiply (type × channel, UI × platform).
- **Use** when implementations must be swapped at runtime or via configuration.
- **NOT** for single-axis variation—Strategy on one interface is enough.
- **NOT** when abstraction and implementation lifecycle are always tied.
- **NOT** before the second axis appears—introduce Bridge at second channel, not speculatively.

#### Java / Spring example
```java
abstract class Alert {
    protected final DeliveryChannel channel;
    abstract RenderedBody render();
    final void dispatch() { channel.send(render()); }
}
```

#### Common mistakes
- Confusing Bridge with Adapter—Bridge designs for variation upfront; Adapter fixes mismatch after the fact.
- Leaking implementation types through abstraction API.
- Creating parallel hierarchies that always change together—unnecessary indirection.

#### Follow-up (with answer)
**Q:** Bridge vs Strategy?
**A:** Strategy swaps one algorithm inside a class; Bridge separates two orthogonal hierarchies that evolve independently. If `Alert` only differed by sort algorithm, Strategy fits. When alert *types* and delivery *channels* both grow, Bridge's composed implementation reference is the right model. Test: can you add a new channel without new alert subclasses? If yes, Bridge is working.

---

### P016. Builder

**Category:** Creational
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/builder/)

**Short answer:** Builder constructs complex objects step-by-step, enforcing invariants before `build()` and improving readability for many optional fields. Trade-off: extra classes; Java records with compact constructors often suffice for simple immutables. It hurts for two-field DTOs, when telescoping constructors are still readable, or when mutable builders leak into domain models that should be value objects.

#### Scenario (interview)
**Situation:** A Kafka `PaymentInitiated` event requires 18 fields including nested `Money`, `Party`, regulatory tags, and idempotency metadata. Constructors became unreadable; half the team used factory methods with `null` for unused fields, causing serialization bugs in Azure Schema Registry.
**What they're testing:** Immutability, validation at construction, fluent APIs vs Lombok `@Builder` pitfalls.
**Model answer:** I'd introduce `PaymentInitiatedEvent.builder()` with fluent methods, required fields in `build()` validation (`idempotencyKey` non-null, `amount` positive), and nested builders for `Party`. Jackson deserializes via `@JsonPOJOBuilder` or records with `@JsonDeserialize`. Prefer Java record builder (JEP 508 style) or explicit class over Lombok when defaults must be illegal—Lombok won't stop `amount(-1)`. For test data, `PaymentInitiatedEvent.builder().defaultsForTest().build()` centralizes fixtures. I wouldn't builder a `String` wrapper. When fields drop below ~6 with few optionals, record constructor is clearer. Document that builders are not thread-safe during construction; build once, pass immutable result to Kafka producer.

#### What it is
Builder separates construction from representation, allowing staged assembly and validation. Gang-of-Four Builder; in Java ecosystem often fluent inner static class or Lombok-generated.

#### When to use / when NOT
- **Use** for objects with many optional parameters and validation rules.
- **Use** when construction order matters or derived fields compute at build time.
- **NOT** for simple records with 3-4 required fields.
- **NOT** when MapStruct/JSON mapping can populate immutable constructors directly.
- **NOT** exposing mutable builder instances from domain APIs.

#### Java / Spring example
```java
var event = PaymentInitiatedEvent.builder()
    .idempotencyKey(key)
    .amount(Money.of("USD", 100))
    .debtor(Party.builder().iban("DE89...").build())
    .build();
```

#### Common mistakes
- Forgetting validation in `build()`, allowing illegal objects.
- Reusing builder instances across tests without `clear()`.
- Lombok `@Builder` on JPA entities encouraging mutable domain models.

#### Follow-up (with answer)
**Q:** Builder vs factory when constructing Kafka events?
**A:** Factory encapsulates *which* event to create (`forRefund`, `forCapture`); Builder handles *how* to assemble one variant with many optional fields. Combine them: static factory methods return pre-configured builders. Factory answers business intent; Builder answers combinatorial field assembly. Don't put Kafka serialization logic inside builder—keep mapping in `KafkaTemplate` converters.

---

### P017. Business Delegate

**Category:** Enterprise
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/business-delegate/)

**Short answer:** Business Delegate hides complexity of remote business services from presentation tier—caching lookups, combining calls, translating exceptions to UI-friendly errors. It thins controllers and JSPs/servlets in classic Java EE; in Spring it's often a `@Service` façade. Trade-off: extra layer that can absorb business logic inappropriately. It hurts when it's a pass-through adding no value, or when it duplicates `@Controller` + domain service responsibilities in modern layered apps.

#### Scenario (interview)
**Situation:** A legacy Spring MVC trade blotter JSP calls three EJB-era remote services for positions, limits, and market data. Controllers grew to 400 lines with retry logic and exception translation. Team migrates to REST but keeps JSP interim layer on Azure VMSS.
**What they're testing:** Layering discipline, façade vs domain service, migration from Java EE patterns.
**Model answer:** I'd extract `TradeBlotterDelegate` (or `TradeBlotterApplicationService`) injected into controllers. It orchestrates `PositionService`, `LimitService`, `MarketDataClient`, maps `RemoteException` and HTTP 502 to `BlotterViewModel` errors, and caches market snapshots for 500ms to protect UI refresh storms. Controllers only bind request params and return view names. This is Business Delegate in spirit—presentation-facing orchestration without domain rules like margin calculation, which stay in domain services. As we retire JSP for React, the delegate becomes REST BFF methods. I'd kill pass-through delegates that only forward one call. Integration tests mock downstream at delegate boundary. Senior trap: don't let delegate own transactions spanning unrelated aggregates—that belongs in domain layer with clear aggregate boundaries.

#### What it is
Business Delegate is a presentation-tier intermediary that reduces coupling between UI and business subsystems, handling lookup, invocation, and partial aggregation of remote or local services.

#### When to use / when NOT
- **Use** when UI layer would otherwise know remote service locations and error protocols.
- **Use** during legacy EE migration to isolate obsolete APIs.
- **NOT** when Spring `@RestController` + thin `@Service` already provides clean layering.
- **NOT** as junk drawer for business rules—rename to application service and own domain properly.
- **NOT** duplicating Spring Cloud OpenFeign resilience already in clients without added semantics.

#### Java / Spring example
```java
@Service
class OrderBusinessDelegate {
    BlotterView loadBlotter(String deskId) {
        var positions = positionPort.forDesk(deskId);
        var limits = limitPort.forDesk(deskId);
        return mapper.toView(positions, limits);
    }
}
```

#### Common mistakes
- Delegate performs domain calculations—fat façade anti-pattern.
- One mega-delegate for entire application instead of feature-scoped services.
- Synchronous aggregation without timeouts, blocking UI threads.

#### Follow-up (with answer)
**Q:** Business Delegate vs Application Service in DDD?
**A:** Application Service orchestrates use cases at domain boundary with transactional semantics; Business Delegate historically sat closer to presentation handling remote lookup/exception cosmetics. In modern Spring, merge concepts into feature-scoped application services injected into controllers. Keep the name "delegate" only when the primary job is shielding UI from remote plumbing, not executing domain workflows.

---

### P018. Bytecode

**Category:** Performance
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/bytecode/)

**Short answer:** The Bytecode pattern implements a small instruction set interpreted at runtime—useful for rules engines, query planners, and sandboxed scripting without `eval()`. Trade-off: build/interpret infrastructure, debugging indirection, security sandbox requirements. It hurts when Spring EL or Drools already solve rules, when scripts are rare, or when team lacks expertise to secure arbitrary bytecode execution.

#### Scenario (interview)
**Situation:** A pricing engine on Azure must let business analysts define promotion rules deployed weekly without JVM restarts. Groovy `eval` was banned by security after RCE scare. Engineering evaluates compiling DSL to custom bytecode vs embedding DMN.
**What they're testing:** Safe customization, interpreter design, vs off-the-shelf rule engines.
**Model answer:** I'd design a constrained DSL compiling to an instruction array—`LOAD_FIELD`, `COMPARE`, `BRANCH`, `APPLY_DISCOUNT`—interpreted by `PromotionVm` with no reflection or network opcodes. Rules version in Git, validated in CI, published to blob storage; pods hot-reload instruction sets. Sandboxing: max steps counter, no heap allocation opcodes, whitelist field accessors on `OrderContext`. Compared to DMN: bytecode is lighter if rules are simple arithmetic; DMN wins for analyst-friendly tables and FEEL. Debugging via disassembler logging and correlation to source line maps. Performance beats parsing AST each request after compile step. I wouldn't hand-roll if compliance mandates BRMS audit trail—use Drools/DMN. Unit tests execute bytecode fixtures per promotion scenario.

#### What it is
Bytecode pattern represents program logic as portable instructions executed by a virtual machine loop. It decouples rule authoring from JVM bytecode generation (though ASM can target real bytecode for performance).

#### When to use / when NOT
- **Use** for user-defined logic needing sandboxing and hot reload.
- **Use** when expression trees are too slow to interpret naively each call.
- **NOT** when DMN/CEL/Spring Expression Language meets requirements with support.
- **NOT** without opcode budget and security review—Turing-complete means trouble.
- **NOT** for one `if (vip)` branch—hardcode it.

#### Java / Spring example
```java
enum Op { LOAD, CMP, MUL, RET }
record Instr(Op op, int arg) {}
class PromotionVm {
    Money run(Instr[] code, OrderContext ctx) { /* fetch-decode-execute */ }
}
```

#### Common mistakes
- Exposing Turing-complete language without resource limits.
- No versioning—silent behavior change when rules reload mid-request.
- Debugging nightmare without source maps back to DSL text.

#### Follow-up (with answer)
**Q:** Custom bytecode vs compiling to JVM bytecode with ASM?
**A:** Custom interpreter opcodes are easier to sandbox and port across languages; JVM bytecode via ASM runs faster but inherits JVM security model complexities. Hybrid: compile DSL to your VM for analyst rules; ASM only for inner-loop math after profiling proves bottleneck. For Azure multi-tenant SaaS, custom VM with step limits is safer default.

---

### P019. Caching

**Category:** Performance
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/caching/)

**Short answer:** Caching stores expensive computation or remote reads for faster reuse—in-process (Caffeine), distributed (Redis), or CDN. Trade-off: staleness, invalidation complexity, memory cost, thundering herd on expiry. It hurts when consistency is paramount without TTL discipline, when caching hides upstream performance debt, or when `@Cacheable` on mutable entities causes cross-tenant leaks without careful key design.

#### Scenario (interview)
**Situation:** Product catalog API backed by Cosmos DB sees 40k RPS from mobile BFF on Azure. p99 latency acceptable but RU costs spike. Engineers slapped `@Cacheable` on `ProductService` but stale prices after Kafka `PriceChanged` events caused checkout failures and revenue loss.
**What they're testing:** Cache-aside vs write-through, invalidation, multi-layer cache, stampede protection.
**Model answer:** I'd implement cache-aside with Caffeine L1 and Redis L2 keyed by `tenantId:productId`. TTL is safety net; primary invalidation listens to Kafka `PriceChanged` via `@KafkaListener` evicting keys and publishing local cache invalidation via Redis pub/sub for pod coherence. `sync=true` on Caffeine load or single-flight wrapper prevents thundering herd on hot SKU expiry. Never cache personalized prices without customer dimension in key—learned after cross-tenant leak scare. Metrics: hit ratio, load time, eviction rate. For read-heavy static attributes (description, images), longer TTL; for inventory, shorter or no cache. Document stale-while-revalidate for BFF if product accepts 30s lag. Don't cache errors—Resilience4j circuit open shouldn't poison cache.

#### What it is
Caching pattern copies data to faster storage closer to consumer, trading freshness for latency and throughput. Strategies include cache-aside, read-through, write-through, and write-behind.

#### When to use / when NOT
- **Use** for read-heavy, relatively stable data with measurable DB/API cost.
- **Use** with explicit invalidation or TTL aligned to business tolerance.
- **NOT** for strongly consistent financial balances without careful design.
- **NOT** when payload is unique per request—cache miss rate ~100%.
- **NOT** without monitoring—silent wrong TTL burns money and trust.

#### Java / Spring example
```java
@Cacheable(value = "products", key = "#tenant + ':' + #id", sync = true)
public ProductView getProduct(String tenant, String id) { ... }

@CacheEvict(value = "products", key = "#event.tenant + ':' + #event.productId")
void onPriceChanged(PriceChanged event) { }
```

#### Common mistakes
- Caching mutable JPA entities—stale associations and session bugs.
- Missing tenant/user in cache key—security incident.
- Thundering herd on hot key expiry without single-flight or probabilistic early refresh.

#### Follow-up (with answer)
**Q:** When is distributed cache worse than scaling the database?
**A:** When hit ratio is low, data churn is high, or invalidation fan-out costs exceed DB read replicas. Redis adds ops burden and failure mode. Run the math: RU/RPS saved vs Redis cluster cost and incident complexity. Sometimes Cosmos autoscale + proper indexing beats cache layers for moderate traffic. Cache wins on fan-out read amplification from BFF aggregation.

---

### P020. Callback

**Category:** Behavioral
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/callback/)

**Short answer:** Callback passes executable code to run when an event completes—inversion of control for async notification. Java uses functional interfaces, `CompletableFuture`, and framework hooks. Trade-off: callback hell without composition; error propagation gets lost. It hurts when reactive streams or structured concurrency clarify async graphs, or when synchronous template methods suffice.

#### Scenario (interview)
**Situation:** Spring Integration polls Azure Blob for incoming SWIFT payment files. Processing is parse → validate → post to ledger → archive. Original design used nested `BlobClient.downloadWithResponse` callbacks; failures in step three left orphaned files and untraceable stack traces.
**What they're testing:** Async composition, error handling, migration to CompletableFuture or reactive pipelines.
**Model answer:** I'd refactor to explicit callbacks via `CompletableFuture` chain or Spring Integration flow with `IntegrationFlow` error channel—not anonymous inner callbacks three levels deep. Success callback posts to `LedgerService` then moves blob; failure callback routes to quarantine prefix and emits `PaymentIngestFailed` Kafka event with correlation ID. For testability, inject `Consumer<ParseResult>` hooks instead of hardcoded lambdas. Modern alternative: Project Reactor `Mono` with `flatMap` and `onErrorResume`. Callback pattern fits framework extension points (`JdbcTemplate` RowMapper, Hibernate interceptors) where inversion of control is intentional. Senior rule: if callbacks exceed two levels, compose with futures or workflow engine (Temporal). Always propagate MDC/trace context into async callback threads.

#### What it is
Callback registers code invoked later when work completes or an event fires. It inverts flow: library calls your code instead of you polling the library.

#### When to use / when NOT
- **Use** for framework hooks, async I/O completion, and plugin extension points.
- **Use** when one-shot notification is simpler than polling.
- **NOT** when deep nesting emerges—compose with `thenCompose` or reactive operators.
- **NOT** for business workflow orchestration spanning days—use saga/workflow engine.
- **NOT** without unified error handler—swallowed callback exceptions are common outages.

#### Java / Spring example
```java
blobClient.downloadStream((data, offset, count) -> parser.feed(data, offset, count));
// Prefer:
CompletableFuture.supplyAsync(() -> parse(blob))
    .thenCompose(this::postToLedger)
    .whenComplete((r, ex) -> archiveOrQuarantine(blob, ex));
```

#### Common mistakes
- Callback hell without future composition.
- Running heavy work on Netty/event-loop callback thread blocking I/O.
- Ignoring cancellation when caller times out.

#### Follow-up (with answer)
**Q:** Callback vs Observer for domain events?
**A:** Callback is typically one-to-one completion notification; Observer is publish-subscribe to many listeners for domain occurrences. Spring `ApplicationEventPublisher` is Observer; `CompletableFuture.whenComplete` is Callback. Use Observer when multiple subsystems react to `OrderPlaced`; use Callback when blob download finishes and only one pipeline continues.

---

### P021. Chain of Responsibility

**Category:** Behavioral
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/chain-of-responsibility/)

**Short answer:** Chain of Responsibility passes a request along a chain of handlers until one processes it—ideal for pipelines where steps are optional or ordered. Servlet filters and Spring Security are canonical examples. Trade-off: debugging which link failed, ensuring chain termination, and avoiding duplicate processing. It hurts when a fixed pipeline with clear stages is simpler as explicit orchestration code.

#### Scenario (interview)
**Situation:** A loan approval workflow in Spring must run fraud check, income verification, regulatory hold, and manual underwriter escalation in configurable order per product. Hardcoded `if` chains in `LoanService` became unmaintainable when compliance reordered steps for EU vs US products.
**What they're testing:** Composable handlers, early exit vs pass-through, configuration-driven pipelines.
**Model answer:** I'd model each step as `ApprovalHandler` with `handle(LoanContext)` returning `CONTINUE`, `APPROVED`, or `REJECTED`. Handlers link via Spring `@Order` or explicit `setNext` built from YAML product config. `FraudHandler` rejects outright; `IncomeHandler` may request docs and stop chain pending user action. Context carries immutable `LoanApplication` plus audit trail entries per handler. Kafka emits `LoanDecisionPending` when chain suspends. Unlike Strategy (pick one algorithm), multiple handlers may inspect but only one decides terminal state. Integration tests run chains per product profile. I'd avoid anonymous chains in hot paths without metrics per handler latency. Spring Security filter chain is the reference architecture—borrow its `OncePerRequestFilter` discipline. Don't use chain for simple sequential ETL—plain methods are clearer.

#### What it is
Chain of Responsibility links handlers so each either handles the request or forwards to the next. The sender doesn't know which handler will process it, enabling dynamic composition.

#### When to use / when NOT
- **Use** when multiple objects might handle a request and set isn't known upfront.
- **Use** for cross-cutting pipelines (auth, validation, enrichment) with plug-in steps.
- **NOT** when exactly one handler always runs—call it directly.
- **NOT** without tracing—which handler acted must be observable in logs.
- **NOT** when order changes require business approval without configuration audit trail.

#### Java / Spring example
```java
@Component @Order(20)
class FraudCheckHandler extends ApprovalHandler {
    protected Result doHandle(LoanContext ctx) {
        return fraudService.score(ctx) > threshold ? rejected("fraud") : CONTINUE;
    }
}
```

#### Common mistakes
- Handler forgets to call `next`, silently dropping requests.
- Mutable shared context mutated unpredictably by parallel handlers.
- Chain order implicit in `@Order` integers with gaps causing surprise precedence.

#### Follow-up (with answer)
**Q:** Chain of Responsibility vs Pipeline pattern in Camel/Spring Integration?
**A:** Both move messages through stages. Chain of Responsibility emphasizes first-handler-wins or optional handling with early exit; integration pipelines emphasize transform-enrich-route with all stages typically executing. Use CoR for approval gates; use Camel for data movement between systems. You can combine: Camel route with CoR bean for business decision substeps.

---

### P022. Circuit Breaker

**Category:** Microservices
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/circuit-breaker/)

**Short answer:** Circuit Breaker stops calling a failing dependency after thresholds trip, failing fast and allowing recovery—prevents cascade and resource exhaustion. States: closed, open, half-open probe. Trade-off: stale fallbacks, tuning sensitivity, and users seeing degraded features. It hurts on low-traffic services where statistical significance is weak, or when breakers hide systemic issues without alerting.

#### Scenario (interview)
**Situation:** Checkout calls a third-party address validation API on Azure. During their outage, your pods exhausted HTTP connection pools retrying, causing full site degradation. Product wants graceful degradation: allow checkout with unchecked address flag.
**What they're testing:** Resilience4j tuning, fallbacks, half-open behavior, monitoring.
**Model answer:** I'd wrap the client with Resilience4j `@CircuitBreaker(name="address-validation")` plus time limiter and bulkhead. After 50% failure rate over 20 calls in sliding window, breaker opens—`validate()` immediately returns `ValidationSkipped.FALLBACK` and logs metric `breaker_open`. Half-open allows 3 probe calls; success closes breaker. Fallback is not silent—UI shows banner, order tagged for manual review Kafka event. Separate thread pool bulkhead so validation slowness doesn't starve payment calls. Dashboards on state transitions; PagerDuty when open > 5 min. I wouldn't breaker internal DB calls—fix the DB. Tune per dependency: idempotent GETs may retry; payment POSTs need breaker + idempotency keys. Chaos test in staging by toxiproxy latency injection.

#### What it is
Circuit Breaker monitors call failures and opens the circuit to block further calls for a cooldown, then tests recovery with limited probes. Michael Nygard popularized it in Release It!

#### When to use / when NOT
- **Use** for remote dependencies with failure modes that amplify (timeouts, thread blocking).
- **Use** with defined fallback or fail-fast user messaging.
- **NOT** for in-process deterministic code paths.
- **NOT** without metrics on open state—operators fly blind.
- **NOT** sharing one breaker across unrelated endpoints on same host.

#### Java / Spring example
```java
@CircuitBreaker(name = "addressApi", fallbackMethod = "fallbackValidate")
public ValidationResult validate(Address a) { return client.validate(a); }
```

#### Common mistakes
- Breaker on wrong exception types—counting business 404 as failure.
- Fallback performing same failing call recursively.
- Global breaker name causing one bad endpoint to trip all calls to host.

#### Follow-up (with answer)
**Q:** Circuit breaker vs retry—aren't retries enough?
**A:** Retries help transient blips; during sustained outage retries multiply load on victim and caller (retry storm). Breaker stops hammering failed dependency and preserves caller resources. Best practice: limited retries with jitter *inside* closed breaker, then open on sustained failure. Service mesh retries need aligned breaker policies to avoid amplification.

---

### P023. Clean Architecture

**Category:** Architectural
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/clean-architecture/)

**Short answer:** Clean Architecture organizes code in concentric layers with dependency rule: inner domain knows nothing of Spring, Kafka, or Azure. Use cases orchestrate entities; adapters implement ports. Trade-off: more modules/boilerplate, mapping overhead, junior onboarding friction. It hurts in early MVPs, CRUD apps with no domain complexity, or when "clean" becomes anemic services with no real boundaries.

#### Scenario (interview)
**Situation:** A 6-year Spring monolith mixes JPA annotations on domain classes, `@RestController` calling repositories directly, and Kafka listeners importing DTOs from API package. Team plans strangler migration to microservices for `Billing` without rewriting everything at once.
**What they're testing:** Dependency inversion, ports/adapters, pragmatic migration—not textbook purity.
**Model answer:** I'd carve `billing-domain` (entities, value objects, domain services), `billing-application` (use cases like `IssueInvoice`), `billing-adapters` (JPA, Kafka, REST). Domain has zero Spring imports. `IssueInvoiceUseCase` depends on `InvoiceRepository` port; `JpaInvoiceRepository` implements it. REST controller maps DTO → command → use case → DTO. Strangler: new features only through use cases; legacy paths wrapped gradually. Test pyramid: domain unit tests without `@SpringBootTest`. Anti-pattern to avoid: anemic `InvoiceService` that's just CRUD with no ubiquitous language. Clean Architecture pays off when regulatory audit demands testable core rules independent of infrastructure. For simple config CRUD, package-by-feature without layers is fine. Package structure in repo enforces ArchUnit rules in CI.

#### What it is
Clean Architecture (Uncle Bob) separates enterprise business rules from application rules from interface adapters and frameworks. The dependency rule points inward—details depend on abstractions defined by the core.

#### When to use / when NOT
- **Use** when domain complexity, compliance, or longevity justify isolation from frameworks.
- **Use** when multiple delivery mechanisms (REST, Kafka, batch) share core logic.
- **NOT** for prototypes where speed beats structure.
- **NOT** when "use case per endpoint" creates 200 pass-through classes.
- **NOT** without team buy-in—half-migrated clean architecture is worse than consistent simple layering.

#### Java / Spring example
```java
// application module
public class IssueInvoice {
    public InvoiceId execute(IssueInvoiceCommand cmd) {
        var invoice = Invoice.issue(cmd.lines(), clock);
        return repository.save(invoice).id();
    }
}
```

#### Common mistakes
- Domain entities annotated `@Entity` coupling to Hibernate.
- Use cases returning JPA entities to controllers—leaking persistence.
- ArchUnit rules absent—structure erodes in three sprints.

#### Follow-up (with answer)
**Q:** Clean Architecture vs hexagonal—practical difference?
**A:** Hexagonal emphasizes ports and adapters metaphor; Clean Architecture emphasizes layer rings and dependency rule. In Spring projects they're implemented the same way: domain center, `application` orchestration, `infrastructure` adapters. Debating names wastes time—enforce dependency direction and testable core. Hexagonal name helps teams grok "plug in Kafka adapter."

---

### P024. Client Session

**Category:** Enterprise
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/client-session/)

**Short answer:** Client Session maintains per-client conversational state across multiple server requests—shopping cart, wizard progress, auth context—often via server-side session or token-bound state store. Trade-off: stickiness, expiration, and horizontal scale complexity. It hurts in stateless JWT-only APIs where all state should be client-held or in domain aggregates, or when sessions become undeclared caches of huge object graphs.

#### Scenario (interview)
**Situation:** A B2B procurement portal on Azure App Service lets buyers build multi-step RFQs across days. Spring Session stored in Redis holds draft line items. After scale-out without Redis, users lost carts on round-robin to different VMs.
**What they're testing:** Stateful vs stateless design, Spring Session, Redis, session fixation security.
**Model answer:** I'd use Spring Session with Redis backing and `spring.session.redis.namespace` per environment. `ClientSession` facade encapsulates `RFQDraft` keyed by `sessionId` + `buyerOrgId`—never trust session alone for tenant isolation. TTL 7 days with sliding refresh on activity; serialize compact DTO not full entity graph. For API clients, replace cookie session with `draftToken` UUID stored server-side same store. Security: regenerate session ID post-login against fixation; mark cookies `Secure`, `HttpOnly`, `SameSite`. Kafka persists `RFQSubmitted` then clear session draft. Don't store PII beyond necessity—GDPR deletion must purge Redis keys. Alternative for mobile: client-held encrypted state with server signature if offline matters. Senior point: session is UX convenience, not system of record—persist business truth to DB on meaningful milestones.

#### What it is
Client Session pattern tracks state associated with a particular client interaction across requests. Implementation ranges from HTTP sessions to token-scoped server stores to client-side state with server validation.

#### When to use / when NOT
- **Use** for multi-step flows where re-fetching all state each request is costly or awkward.
- **Use** when server must control sensitive draft data clients shouldn't tamper with.
- **NOT** when REST statelessness and resource-oriented design suffice.
- **NOT** for long-term business state—belongs in database aggregates.
- **NOT** without eviction policy—Redis memory leaks from abandoned sessions.

#### Java / Spring example
```java
@Component
class RfqClientSession {
    void addLine(HttpSession session, LineItem line) {
        var draft = (RfqDraft) session.getAttribute("rfq");
        session.setAttribute("rfq", draft.withLine(line));
    }
}
```

#### Common mistakes
- Storing Hibernate entities in session—serialization and stale data bugs.
- Session affinity assumed without shared store in scaled deployments.
- Missing tenant scoping—session collision across organizations.

#### Follow-up (with answer)
**Q:** Server session vs JWT for SPA + Spring API?
**A:** JWT suits stateless horizontal scale and mobile APIs but bloats with claims and complicates revocation. Server session (Redis) suits sensitive draft state, instant logout, and smaller cookies. Hybrid: short-lived JWT for auth, server-side draft store keyed by subject. For B2B procurement with long workflows, I'd pick Redis session over 4KB JWT carts.

---

### P025. Collecting Parameter

**Category:** Behavioral
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/collecting-parameter/)

**Short answer:** Collecting Parameter accumulates intermediate results through a parameter object passed across processing stages—avoiding excessive return-value threading. Trade-off: mutable collector objects if not careful; can hide pure functional pipelines. It hurts when immutable stream pipelines or explicit return tuples are clearer, or when the collector becomes a god-object absorbing unrelated fields.

#### Scenario (interview)
**Situation:** A nightly Spring Batch job reconciles Kafka payment events with Azure SQL ledger entries. Each step (dedupe, FX convert, fee allocate, GL code assign) needs prior step outputs. Developers threaded 12 local variables through private methods; tests couldn't construct mid-pipeline state.
**What they're testing:** Pipeline state management, batch step composition, testability.
**Model answer:** I'd introduce `ReconciliationCollector` immutable-style builder passed through steps: `dedupe(collector)`, `applyFx(collector)`, `allocateFees(collector)`. Each step returns new collector instance (or records with `with*` methods) carrying `List<MatchedPair>`, `List<Exception>`, running totals. Spring Batch `ItemProcessor` chain or composed functions in one `Tasklet` with clear step logging reading collector snapshot. Compared to Collection Pipeline (functional), Collecting Parameter fits imperative batch with side effects writing to SQL mid-flight. Unit tests seed collector at any stage. Avoid public mutable lists—encapsulate append via methods that validate invariants. When pipeline stabilizes, consider extracting pure functions and retiring collector for stream pipeline.

#### What it is
Collecting Parameter passes a accumulating object through a sequence of operations that enrich it. Kent Beck pattern for multi-step computations where each step adds to shared context.

#### When to use / when NOT
- **Use** for multi-phase batch/report generation with shared accumulating context.
- **Use** when method signatures would otherwise grow unwieldy with out-parameters.
- **NOT** when functional pipeline with `stream().reduce()` is natural and team prefers it.
- **NOT** when collector accretes unrelated concerns—split collectors per workflow.
- **NOT** for single-step transforms—just return the value.

#### Java / Spring example
```java
ReconciliationCollector c = ReconciliationCollector.empty(input);
c = dedupeStep.process(c);
c = fxStep.process(c);
c = glCodingStep.process(c);
reportWriter.write(c.matchedPairs());
```

#### Common mistakes
- Public mutable fields in collector—race conditions in parallel batch.
- Collector reused across unrelated jobs without reset.
- No snapshot/serialization for failure recovery mid-batch.

#### Follow-up (with answer)
**Q:** Collecting Parameter vs Context Object pattern?
**A:** Context Object typically carries request-scoped ambient data (user, locale, trace) for services; Collecting Parameter carries workflow computation results across algorithm steps. `ReconciliationCollector` is algorithm state; `RequestContext` is cross-cutting invocation metadata. Don't merge them—one changes per business run, the other per HTTP request.

---

### P026. Collection Pipeline

**Category:** Behavioral
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/collection-pipeline/)

**Short answer:** Collection Pipeline chains higher-order operations—filter, map, reduce—over collections for declarative data transformation. Java Streams embody it; lazy evaluation enables short-circuiting. Trade-off: debugging stack traces, primitive boxing, and parallel stream misuse. It hurts for I/O-bound steps (use reactive or explicit loops), very large data (stream to DB cursor), or when imperative code is clearer to the team maintaining it.

#### Scenario (interview)
**Situation:** A risk dashboard aggregates 50k open trades from Kafka compacted topic into exposure by desk and currency for a Spring `@Scheduled` report emailed to CRO. Original nested loops had off-by-one currency double-count bugs.
**What they're testing:** Streams fluency, grouping, reducing, when *not* to parallelize.
**Model answer:** I'd pipeline: `trades.stream().filter(Trade::isOpen).collect(groupingBy(Trade::desk, groupingBy(Trade::currency, summarizingDouble(Trade::notional))))` then map to immutable `ExposureRow` records. Intermediate `peek` only behind debug flag—never in prod logs at 50k scale. No `parallelStream()` on shared Kafka-fed list during concurrent updates—race. For DB-sourced millions of rows, use cursor/stream from JDBC, not `List` in memory. Readable extraction: private methods `openTrades()`, `groupByDeskCurrency()`. Compare to Collecting Parameter when steps have side effects writing files—pipeline stays pure until terminal `forEach` sending email. Unit test with fixture trades asserting EUR desk exposure math. Senior smell: 40-operation single stream—break named substeps.

#### What it is
Collection Pipeline models computation as sequence of operations on collections, each passing output to next. Functional style emphasizes immutability and expressiveness over index loops.

#### When to use / when NOT
- **Use** for in-memory transforms, reporting, and validation chains.
- **Use** when declarative intent beats nested loops for readability.
- **NOT** for IO interleaved transforms—side effects belong outside pipeline.
- **NOT** `parallelStream()` on small collections or ordered-sensitive ops without benchmarking.
- **NOT** when team consistently produces unreadable stream chains—train or use loops.

#### Java / Spring example
```java
List<ExposureRow> rows = trades.stream()
    .filter(Trade::isOpen)
    .collect(groupingBy(Trade::desk, groupingBy(Trade::currency, summingDouble(Trade::notional))))
    .entrySet().stream()
    .flatMap(deskEntry -> toRows(deskEntry.getKey(), deskEntry.getValue()))
    .toList();
```

#### Common mistakes
- Side effects inside `map`/`forEach` mutating external state unpredictably.
- `Optional` abuse in chains—`.get()` without `orElseThrow` message.
- Parallel streams on common `ForkJoinPool` starving other work.

#### Follow-up (with answer)
**Q:** Stream pipeline vs SQL for aggregation?
**A:** Push aggregation to SQL when data already in database and volume exceeds memory—`GROUP BY` beats loading 50k rows if it's millions. In-memory pipeline suits event-sourced projections already in Kafka state store or preloaded cache. Rule: aggregate closest to data; streams for application-layer shaping after bounded fetch.

---

### P027. Combinator

**Category:** Behavioral
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/combinator/)

**Short answer:** Combinators compose small functions into larger behaviors without imperative glue—parsing, validation, and reactive operators are classic domains. Trade-off: steep abstraction curve and stack-heavy debug traces. It hurts when team readability suffers, or when Java's verbosity makes combinators more ceremony than insight compared to Kotlin or Haskell.

#### Scenario (interview)
**Situation:** An API gateway validation layer must compose rules: schema check, signature verify, rate limit token, geo allowlist. Each rule returns `ValidationResult` combinable with short-circuit on first failure. Engineers copy-pasted `if` chains per endpoint.
**What they're testing:** Functional composition, reusability, parser-style thinking in Java.
**Model answer:** I'd define `Validator<T>` as functional interface with combinator methods `and`, `or`, `map`—`signatureValidator.and(schemaValidator).and(geoValidator)`. `and` short-circuits on first `invalid` with accumulated errors optional. Spring `@Bean` provides composed validators per route via `RouterFunction` metadata. Similar to Vavr `Validation` combinators or Apache Commons Validator composition. For JSON Schema, combine structural validator with business combinator `amountPositive`. Tests: each combinator unit-tested, composition property-tested with fastCheck-style random inputs if budget allows. Don't combinatorize two rules total—overkill. Reactive parallel: `Mono.zip` composes async validators. Senior boundary: combinators for pure validation; imperative for I/O with clear error channels.

#### What it is
Combinator pattern builds complex operations by combining simpler functions according to fixed rules (and, or, sequence). Common in parsers, functional validation, and reactive libraries (`flatMap`, `zip`).

#### When to use / when NOT
- **Use** when many small reusable predicates assemble differently per context.
- **Use** for parser/interpreter DSL internals.
- **NOT** for one-off three-condition `if` in controller.
- **NOT** without team fluency—unreadable combinator towers.
- **NOT** mixing side-effecting functions in supposedly pure combinator chains.

#### Java / Spring example
```java
Validator<PaymentRequest> pipeline =
    Validator.combine(Validator::notNull)
        .and(PaymentRequest::hasPositiveAmount)
        .and(req -> hmacValid(req));
```

#### Common mistakes
- Combinators that swallow error context—always carry reason codes.
- Deep nesting without named intermediate validators.
- Using combinators for database transactions—wrong abstraction level.

#### Follow-up (with answer)
**Q:** Combinators in Java vs sealed interfaces for validation?
**A:** Sealed `ValidationRule` with pattern switch gives exhaustive compile-time checks when rule set is closed. Combinators win when rules are dynamically composed per tenant from plugin registry. Hybrid: sealed rules *within* tenant packs, combinator orchestrates packs at runtime.

---

### P028. Command

**Category:** Behavioral
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/command/)

**Short answer:** Command encapsulates a request as an object—enabling queueing, logging, undo, and decoupling invoker from receiver. In enterprise Java it's CQRS commands, job payloads, and transactional outbox messages. Trade-off: class proliferation for simple operations. It hurts when anemic command DTOs duplicate service method signatures without adding audit or async benefits.

#### Scenario (interview)
**Situation:** A warehouse management API must support undo for inventory adjustments, audit who issued transfers, and replay failed Kafka commands after partition rebalance. Direct service method calls left no durable intent log.
**What they're testing:** Command objects, handlers, idempotency, audit trail, undo semantics.
**Model answer:** I'd model `AdjustInventoryCommand` with `sku`, `delta`, `reason`, `commandId`, `issuedBy`. `CommandHandler<AdjustInventoryCommand>` executes inside `@Transactional` aggregate, appends to event store, publishes to Kafka outbox. Invoker (`InventoryController` or message listener) dispatches to handler registry. Undo stores compensating `ReverseAdjustmentCommand` linked to original ID—not memory undo stack. Idempotency: dedupe table on `commandId`. This separates HTTP adapter from domain action enabling CLI and Kafka to share handler. Contrast with Command pattern for UI macros—same encapsulation idea. Don't create commands for every getter. Saga orchestration composes commands across services. Tests invoke handler directly with fixture commands, no MockMvc required for domain coverage.

#### What it is
Command turns requests into objects with `execute()` (or handler dispatch), parameterizing clients with queues, logging, and undo. Invoker doesn't know receiver details.

#### When to use / when NOT
- **Use** when operations need audit, async queueing, retry, or undo/redo.
- **Use** for CQRS write side and job scheduling payloads.
- **NOT** for read-only queries—use Query objects or plain methods.
- **NOT** when command DTO mirrors service method 1:1 with no cross-cutting benefit.
- **NOT** without idempotency when commands traverse Kafka.

#### Java / Spring example
```java
record AdjustInventoryCommand(UUID commandId, String sku, int delta, String reason) {}
@Component
class AdjustInventoryHandler implements CommandHandler<AdjustInventoryCommand> {
    public void handle(AdjustInventoryCommand cmd) { ... }
}
```

#### Common mistakes
- Commands carrying entity references instead of IDs—serialization pain.
- Handler executes without transactional boundary—partial updates.
- Undo implemented as mutation hack instead of explicit compensating command.

#### Follow-up (with answer)
**Q:** Command pattern vs event sourcing events?
**A:** Commands express intent to change state (`AdjustInventory`); events record what happened (`InventoryAdjusted`). Command handlers validate and decide; events are immutable facts appended to log. Handler may emit events. Don't publish commands to Kafka as domain truth—publish events or use command bus only internally with outbox for reliability.

---

### P029. Commander

**Category:** Behavioral
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/commander/)

**Short answer:** Commander manages a queue of Command objects executed sequentially—often on a background thread with failure isolation per command. Trade-off: ordering guarantees, queue persistence, and stale command rejection. It hurts when immediate synchronous execution is required, or when a full workflow engine (Temporal) is already justified.

#### Scenario (interview)
**Situation:** A trading desk UI batches order amendments during volatile markets. Each click enqueues amend requests; network blips caused out-of-order arrival at OMS. Need single-threaded execution per instrument with ability to cancel pending amends on disconnect.
**What they're testing:** Command queue, serial execution, vs raw `@Async` chaos.
**Model answer:** I'd implement `InstrumentCommander` per symbol: `ConcurrentLinkedQueue<TradingCommand>` drained by dedicated executor thread. UI submits `AmendOrderCommand`; commander executes FIFO, catches exceptions per command without killing queue. On disconnect, `flushPending()` issues `CancelPendingAmends`. Persist queue to Redis for crash recovery if regulatory requires—otherwise in-memory with user re-submit. Differs from Command pattern alone: Commander adds scheduling semantics. Kafka partition key per instrument achieves similar ordering cross-service; Commander is in-process before gateway. Compare to Active Object—both serialize, but Commander queues discrete command objects with cancel/clear API. Metrics: queue depth, command latency, failure rate. Don't Commander global orders—shard per instrument.

#### What it is
Commander combines Command pattern with a queue and scheduler executing commands one-by-one (or with defined concurrency). Often used in UI macro systems and serialized mutation pipelines.

#### When to use / when NOT
- **Use** when operations must be serialized per resource but submitted concurrently.
- **Use** when users enqueue work and continue interacting.
- **NOT** when Kafka partition ordering + idempotent consumers already serialize.
- **NOT** for parallelizable independent operations—unnecessary bottleneck.
- **NOT** without bounded queue—memory risk on UI spam clicking.

#### Java / Spring example
```java
class InstrumentCommander {
    private final Queue<Command> queue = new ConcurrentLinkedQueue<>();
  void submit(Command c) { queue.add(c); drain(); }
  private void drain() { while (running) { Optional.ofNullable(queue.poll()).ifPresent(Command::execute); } }
}
```

#### Common mistakes
- Unbounded queue during market open—reject with backpressure to UI.
- Commands holding stale market data—validate freshness at execution time.
- Sharing one commander globally across unrelated domains.

#### Follow-up (with answer)
**Q:** Commander vs Actor mailbox for order amends?
**A:** Both FIFO per shard. Actor adds supervision, distribution, and location transparency across JVMs. Commander suits single-node desktop/OMS plugin before messages hit Kafka. Once cross-service, use Kafka keyed partitioning or actor cluster—not in-process Commander on each pod without coordination.

---

### P030. Command Query Responsibility Segregation (CQRS)

**Category:** Architectural
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/cqrs/)

**Short answer:** CQRS separates read models from write models—commands mutate authoritative store; queries hit optimized projections. Enables independent scaling and schema shapes. Trade-off: eventual consistency, projection lag, operational complexity. It hurts for simple CRUD, when strong read-your-writes isn't negotiable without heavy sync, or resume-driven CQRS without read/write asymmetry.

#### Scenario (interview)
**Situation:** An e-commerce platform on Azure has write-heavy checkout but product search needs Elasticsearch facets, inventory counts, and personalization—joining 12 normalized tables per search times out. Team considers CQRS with Kafka projections.
**What they're testing:** Consistency windows, projection rebuild, when CQRS is justified.
**Model answer:** I'd keep authoritative writes in PostgreSQL `Order`, `Inventory` aggregates via command handlers. Publish `OrderPlaced`, `StockReserved` events to Kafka; consumers update Elasticsearch product index and Redis inventory counters—query side. Search API reads only projections, never joins OLTP. UI shows "confirming availability" for 1-2s after cart submit if projection lags—product sign-off required. Rebuild projection from event log via compacted topic replay on schema change. Not full Event Sourcing required—CQRS can snapshot from CDC Debezium if events immature. Avoid CQRS for admin CRUD on tax codes—no read scaling pain. Monitor projection lag alert > 5s. Separate deployables optional—start modular monolith packages `catalog-write` vs `catalog-read`. Test consistency boundaries explicitly in QA chaos.

#### What it is
CQRS splits command (state mutation) and query (data retrieval) into separate models and often separate stores/handlers. Greg Young pattern; pairs naturally with event-driven projections.

#### When to use / when NOT
- **Use** when read patterns differ radically from write model (search, dashboards, reports).
- **Use** when read scale exceeds write and caching isn't enough.
- **NOT** for simple domain with symmetric CRUD.
- **NOT** without strategy for projection lag and failure recovery.
- **NOT** duplicating business rules on read side—projections are derived only.

#### Java / Spring example
```java
// Write
orderCommandHandler.handle(new PlaceOrderCommand(...));
// Read
ProductSearchView search(String q) { return elasticsearchRepo.search(q); }
```

#### Common mistakes
- Query side mutating state—breaks mental model and causes bugs.
- No monitoring of consumer lag—silent stale search results.
- CQRS + shared database tables defeating separation purpose.

#### Follow-up (with answer)
**Q:** CQRS without Event Sourcing—viable?
**A:** Absolutely. CDC from OLTP tables or transactional outbox events can feed projections without event-sourced aggregates. Event Sourcing adds audit and temporal queries but increases storage and versioning complexity. Choose CQRS alone when projections can rebuild from current row state plus changelog; add ES when complete history and temporal replay justify cost.

---

### P031. Component

**Category:** Structural
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/component/)

**Short answer:** Component composes behavior through interfaces rather than deep inheritance trees—objects implement multiple role interfaces (`Printable`, `Serializable`, `Comparable`) and clients depend on the roles they need. Trade-off: interface discovery and default method diamond conflicts. It hurts when a single cohesive class suffices, or when composition-delegation without interface segregation is clearer.

#### Scenario (interview)
**Situation:** A document management system has `Contract`, `Invoice`, and `Policy` entities sharing some capabilities (signable, versionable, archivable) but not others. Inheritance from `AbstractDocument` forced invoices to carry signing methods they don't support, throwing `UnsupportedOperationException`.
**What they're testing:** Interface segregation, composition over inheritance, role modeling.
**Model answer:** I'd refactor to `Contract implements Signable, Versionable, Archivable`, `Invoice implements Versionable, Archivable` only—no fat superclass. Shared logic in package-private helpers or default interface methods on `Versionable` delegating to `VersionStore` component injected at construction. Spring wires `ArchivingService` where `@Autowired` list of `Archivable` beans needed for nightly Azure Blob migration. Clients depend on `Signable` interface when executing e-sign workflow, not concrete `Contract`. This is Component pattern—building objects from composable interface roles. Contrast Composite (tree structure) and Decorator (wrapping). ArchUnit enforces invoices never appear in `Signable` injection points. Migration: deprecate `AbstractDocument` throws, move shared `documentId` to composed `DocumentCore` value object.

#### What it is
Component pattern structures objects as compositions of interface-defined roles rather than monolithic class hierarchies. Clients interact through the specific component interfaces they require.

#### When to use / when NOT
- **Use** when entities share partial behaviors, not full "is-a" taxonomy.
- **Use** to avoid Liskov violations from empty overridden methods.
- **NOT** when single inheritance hierarchy truly models domain taxonomy.
- **NOT** when interface explosion creates 40 one-method interfaces—group thoughtfully.
- **NOT** duplicating Decorator—component defines intrinsic roles, decorator adds layers dynamically.

#### Java / Spring example
```java
public class Contract implements DocumentCore, Signable, Versionable {
    private final DocumentCore core;
    private final SigningDelegate signer;
}
```

#### Common mistakes
- Marker interfaces with no behavior—use annotations or explicit types.
- God interface `Document` with 30 methods all entities implement partially.
- Confusing with Spring `@Component` stereotype annotation—different concept.

#### Follow-up (with answer)
**Q:** Component vs Trait interfaces in Abstract Document?
**A:** Abstract Document traits (`HasPrice`) attach typed views to dynamic property bags; Component pattern composes static interface roles on concrete classes. Traits suit schema-flexible documents; Component suits fixed domain types with optional capability sets. Both avoid inheritance explosion—choose based on static vs dynamic schema needs.

---

### P032. Composite

**Category:** Structural
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/composite/)

**Short answer:** Composite treats individual objects and compositions uniformly—tree structures where leaf and composite share interface (`OrganizationUnit`, `MenuItem`). Clients call `getTotal()` without `instanceof` checks. Trade-off: transparency can violate leaf/composite semantics (adding child to leaf). It hurts for shallow two-level structures, or when ORM mapping recursive trees causes N+1 and lazy-load pain.

#### Scenario (interview)
**Situation:** A permissions system models `Role`, `RoleGroup` (contains roles and nested groups), and enterprise-wide `PolicyBundle`. Authorization walks the tree to collect effective permissions for Spring Security `GrantedAuthority`. Flattening to DB rows broke inheritance from parent org units on Azure AD sync.
**What they're testing:** Recursive structures, uniform API, cycle detection, performance of tree walks.
**Model answer:** I'd model `PermissionNode` interface with `children()`, `permissions()`, `effectivePermissions()`; `RoleLeaf` and `GroupComposite` implement it. `GroupComposite.effectivePermissions()` merges children recursively with memoization cache keyed by node version. Spring `PermissionEvaluator` calls root composite built from repository per request—cache in Caffeine with TTL invalidation on Kafka `PermissionChanged`. Prevent cycles at mutation time via graph visit set. Don't expose `addChild` on leaves—separate `MutableComposite` builder or domain service for admin mutations. For persistence, adjacency list or closure table in SQL; load tree in one query where possible. Contrast Composite Entity (J2EE persistence facade). Unit test deep nesting and empty groups. If tree depth always 2, YAGNI—flat list with parentId suffices.

#### What it is
Composite composes objects into tree structures representing part-whole hierarchies. Clients treat individual and composite nodes through the same interface.

#### When to use / when NOT
- **Use** for recursive structures: org charts, UI menus, file systems, BOMs.
- **Use** when client code should ignore leaf vs branch distinction.
- **NOT** for shallow parent-child without uniform operations.
- **NOT** without strategy to load/persist tree efficiently.
- **NOT** when only traversal differs—Visitor may pair better than forcing uniform API.

#### Java / Spring example
```java
interface PermissionNode {
    Set<Permission> effectivePermissions();
    Stream<PermissionNode> children();
}
class GroupComposite implements PermissionNode { ... }
```

#### Common mistakes
- Leaf nodes implementing `addChild` throwing runtime exception at wrong abstraction level.
- Unbounded recursion without cycle detection—stack overflow.
- Loading entire enterprise tree per request—cache materialized effective permissions.

#### Follow-up (with answer)
**Q:** Composite tree in JPA—how to avoid N+1?
**A:** Use `@EntityGraph` or fetch join for bounded depth, closure table for deep hierarchies, or materialized path column for subtree queries. Often better: compute effective permissions asynchronously on change, store flat expansion table for O(1) auth lookup, keep composite only in admin UI mutation API.

---

### P033. Composite Entity

**Category:** Enterprise
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/composite-entity/)

**Short answer:** Composite Entity implements a coarse-grained business object from multiple fine-grained persistent entities—hiding composition and transaction boundaries from remote clients. Classic Java EE pattern for EJB entity beans; in Spring often a domain aggregate root with `@OneToMany`. Trade-off: over-fetching, lazy-load surprises, and anemic composite if logic leaks to services. It hurts when microservices should split aggregates, or when composite is just a DTO join without behavior.

#### Scenario (interview)
**Situation:** A customer profile screen loads `Customer`, `Addresses`, `Preferences`, `KycStatus` from separate tables. Remote mobile clients made four REST calls causing inconsistent snapshots mid-update during KYC refresh on Azure.
**What they're testing:** Aggregate design, transactional consistency, API granularity.
**Model answer:** I'd expose `CustomerProfile` composite entity as single REST resource backed by aggregate root `Customer` with embedded value objects and child collections loaded in one `@Transactional` read—Spring Data `@EntityGraph` on repository. Writes go through `CustomerProfileService.update()` enforcing invariants across children atomically. Remote clients see one versioned snapshot; ETag for optimistic concurrency on root. Internally JPA maps composite—not separate microservice calls per child table. This differs from Composite View (presentation assembly) and DTO (transport). Split to microservices only when scale boundaries demand—until then composite entity reduces chatty API. Beware lazy initialization outside transaction—`@Transactional(readOnly=true)` on service facade. Event `CustomerProfileUpdated` published after commit for search index.

#### What it is
Composite Entity presents a cluster of dependent persistent objects as one unit for higher layers, managing persistence and consistency of the cluster as a whole.

#### When to use / when NOT
- **Use** when business treats object cluster as single consistency boundary.
- **Use** to reduce remote round-trips in distributed object designs.
- **NOT** when children belong to different bounded contexts—split services.
- **NOT** when composite grows unbounded—performance and contention suffer.
- **NOT** as excuse for 50-table god aggregate—model right-sized roots.

#### Java / Spring example
```java
@Entity
class Customer { // aggregate root
    @OneToMany(cascade = ALL, orphanRemoval = true) List<Address> addresses;
    @Embedded Preferences preferences;
}
```

#### Common mistakes
- Exposing JPA composite directly on REST—leak lazy collections.
- Cross-aggregate references by entity instead of ID—cascade nightmares.
- Loading composite for list screens—use read-optimized projection instead.

#### Follow-up (with answer)
**Q:** Composite Entity vs DTO aggregation in BFF?
**A:** Composite Entity maintains transactional consistency in write model—one aggregate, one transaction. BFF aggregates multiple service DTOs for read convenience without unified consistency—eventual consistency across calls. Use composite entity inside a service boundary; use BFF aggregation across services with explicit staleness acceptance.

---

### P034. Composite View

**Category:** UI
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/composite-view/)

**Short answer:** Composite View assembles a page from reusable subviews (header, nav, portlet) with a template composing layout—JSP tiles, Thymeleaf fragments, Facelets. Trade-off: indirection in layout debugging; duplicate composition in SPA era. It hurts when frontend is pure React with component tree—server-side composite view adds little.

#### Scenario (interview)
**Situation:** A bank's internal ops portal still uses Spring MVC + Thymeleaf. Each of 40 pages duplicated sidebar, compliance footer, and alert banner markup. Marketing updates footer legal text requiring 40 file edits and missed pages in audits.
**What they're testing:** DRY in server-rendered UI, layout composition, fragment caching.
**Model answer:** I'd introduce Thymeleaf layout dialect: `layout.html` defines `header`, `sidebar`, `content`, `footer` fragments; pages `th:replace` content slot only. `CompositeViewResolver` pattern maps logical view names to fragment assemblies—`dashboard` = `header + opsSidebar + dashboardContent + complianceFooter`. Cache static fragments at CDN edge for public pages; internal pages personalize sidebar via Spring Security `sec:authorize` in fragment. Contrast with Composite pattern—Composite View is presentation-tier part-whole assembly, not domain tree. Migration path: extract same fragment boundaries to React layout components when SPA strangler proceeds. Don't composite-view a JSON API—wrong tier. Integration test render key pages assert footer compliance version present.

#### What it is
Composite View builds display pages by assembling atomic subviews into a template hierarchy. It centralizes layout changes and promotes reusable UI components in server-side rendering stacks.

#### When to use / when NOT
- **Use** for server-rendered MVC with repeated chrome/layout.
- **Use** when legal/branding blocks must update atomically site-wide.
- **NOT** for SPA where React/Vue component layout replaces server tiles.
- **NOT** when each page layout is radically unique—composition overhead.
- **NOT** mixing business logic in view fragments—keep thin.

#### Java / Spring example
```html
<!-- layout.html -->
<div th:fragment="page(content)">
  <div th:replace="fragments/header :: header"></div>
  <div th:replace="${content}"></div>
  <div th:replace="fragments/compliance-footer :: footer"></div>
</div>
```

#### Common mistakes
- Fragments with hidden DB calls—N+1 render time.
- Overlapping composite view frameworks (Tiles + Thymeleaf dialect) confusing ownership.
- Cached fragments containing user-specific data—cache leak across sessions.

#### Follow-up (with answer)
**Q:** Composite View vs Spring `@ControllerAdvice` Model attributes?
**A:** `@ControllerAdvice` injects shared model data (user name, alerts) into controllers; Composite View handles structural HTML assembly. Use both: advice for data, layout dialect for markup skeleton. Don't put layout HTML in advice—mixes concerns.

---

### P035. Context Object

**Category:** Enterprise
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/context-object/)

**Short answer:** Context Object encapsulates request-scoped state—user, tenant, locale, correlation ID—in a first-class object passed or stored in `ThreadLocal`/MDC instead of long parameter lists. Trade-off: hidden implicit context complicates testing and async propagation. It hurts when used as junk drawer for unrelated globals, or when explicit parameter passing would keep flows traceable.

#### Scenario (interview)
**Situation:** A multi-tenant Spring service passes `tenantId`, `userId`, `correlationId`, and `DataResidency` through 15 method layers after Azure AD JWT validation. Refactors keep missing a parameter; logs can't correlate Kafka consumers with HTTP requests.
**What they're testing:** Request scope, MDC, `ThreadLocal` pitfalls, reactive context propagation.
**Model answer:** I'd introduce immutable `RequestContext` built in `OncePerRequestFilter` from JWT claims and headers, stored in `RequestContextHolder` (ThreadLocal) and copied to SLF4J MDC. Service methods access `RequestContext.current().tenantId()` instead of parameter drilling. Kafka producers embed context in headers via `ProducerInterceptor`; consumers rebuild context in listener interceptor. For `@Async`, use `TaskDecorator` copying context to worker thread—clear in `finally`. Reactive: Reactor `Context`. Ban mutable context fields—new request builds new object. Don't store heavy domain objects in context—IDs only. ArchUnit fails methods with `tenantId` param after migration. Testing: `RequestContextRunner.execute(ctx, () -> ...)` utility. Context Object is not a replacement for explicit security checks—still validate authorization at boundary.

#### What it is
Context Object holds ambient information about a processing call available to collaborators without passing through every method signature. Common in Java EE and observability stacks via MDC.

#### When to use / when NOT
- **Use** for cross-cutting request metadata used deep in call stack.
- **Use** when correlation/tracing must propagate to logs and messages.
- **NOT** for business domain state—use aggregates and commands.
- **NOT** without async/reactive propagation strategy.
- **NOT** as static mutable singleton—testing nightmare.

#### Java / Spring example
```java
public record RequestContext(String tenantId, String userId, String correlationId) {
    private static final ThreadLocal<RequestContext> CURRENT = new ThreadLocal<>();
    public static RequestContext current() { return requireNonNull(CURRENT.get()); }
}
```

#### Common mistakes
- Forgetting to clear ThreadLocal on servlet exit—pool thread leaks tenant.
- Storing `SecurityContext` duplicates inconsistently with Spring Security.
- Context object mutable mid-request—race in async branches.

#### Follow-up (with answer)
**Q:** Context Object vs Spring `RequestScope` beans?
**A:** Request-scoped beans are DI-managed objects living one HTTP request—good for user-specific services. Context Object is lightweight immutable data carrier for IDs and metadata. Use request scope for stateful request collaborators; use context record for tracing/tenant propagation into static utilities and Kafka headers without injecting everywhere.

---

### P036. Converter

**Category:** Structural
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/converter/)

**Short answer:** Converter translates between representation types—entity to DTO, API model to domain, external XML to internal record—keeping mapping logic isolated. Trade-off: mapping maintenance on schema change; MapStruct helps but isn't magic. It hurts when converter absorbs business rules that belong in domain, or when 1:1 identical types duplicate for no reason.

#### Scenario (interview)
**Situation:** Integration with a legacy COBOL bridge exposes `LegacyPaymentDto` with cents as `String` and dates as `YYYYMMDD`. Domain uses `Money` value object and `Instant`. Mapping code scattered across three services caused duplicate rounding bugs on Azure settlement reports.
**What they're testing:** Single responsibility of mapping, MapStruct, bidirectional vs unidirectional conversion.
**Model answer:** I'd centralize `LegacyPaymentConverter` with explicit methods `toDomain(LegacyPaymentDto)` and `toLegacy(Payment)`—bidirectional only where needed. MapStruct `@Mapper` for boilerplate; hand-code rounding policy in `@AfterMapping` with unit tests on half-up vs banker's rounding. Controllers never touch legacy DTOs—adapter layer converts at boundary. Version converters when legacy schema bumps (`LegacyPaymentConverterV2`). No validation logic beyond format—business validation stays in domain factory `Payment.create()`. Kafka consumers use same converter from Avro to domain to avoid drift. Contrast Data Mapper (persistence layer). Document lossy conversions (timezone midnight assumption). Senior smell: converter calling repositories—it's transform only.

#### What it is
Converter pattern encapsulates transformation between two types without either type knowing about the other. Often implemented as stateless classes or MapStruct generated mappers.

#### When to use / when NOT
- **Use** at layer boundaries: API ↔ domain ↔ persistence ↔ messaging.
- **Use** when representations diverge but concepts align.
- **NOT** when types are identical—use one type.
- **NOT** when mapping encodes business decisions—move to domain service.
- **NOT** fifty one-line converters—consolidate by bounded context.

#### Java / Spring example
```java
@Mapper(componentModel = "spring")
interface PaymentConverter {
    @Mapping(target = "amount", expression = "java(Money.of(dto.currency(), dto.amountCents()))")
    Payment toDomain(LegacyPaymentDto dto);
}
```

#### Common mistakes
- Null-handling inconsistency between inbound and outbound converters.
- Leaking MapStruct generated types into domain package.
- Converter invoked inside entity—wrong direction of dependency.

#### Follow-up (with answer)
**Q:** Converter vs Anti-Corruption Layer translator?
**A:** Converter handles structural field mapping; ACL translator handles semantic remapping (status enums, implicit defaults, foreign workflows). ACL may use multiple converters internally. If mismatch is only `String date` → `Instant`, converter suffices. If legacy `status=9` means `ChargebackInitiated`, that's ACL semantic translation with documented mapping table.

---

### P037. Curiously Recurring Template Pattern (CRTP)

**Category:** Structural
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/curiously-recurring-template-pattern/)

**Short answer:** CRTP has a base class parameterized by the concrete subclass (`abstract class Expr<T extends Expr<T>>`) enabling fluent method chaining and compile-time polymorphism without virtual dispatch overhead—common in builders and expression APIs. Java lacks true CRTP but emulates via generics and self-type bounds. Trade-off: generic signature complexity confuses IDEs and juniors. It hurts when simple inheritance or composition is clearer, or when runtime plugin polymorphism is required.

#### Scenario (interview)
**Situation:** A internal query DSL for Spring Data specifications needs fluent `where().and().or()` with type-safe column references. Early design used raw `Specification` subclasses losing fluent return type; callers cast results unsafely.
**What they're testing:** Self-bounded generics, fluent APIs, type safety vs ergonomics.
**Model answer:** I'd model `abstract class Expr<E extends Expr<E>>` with methods returning `E` via `(E) this` suppressed cast pattern—or safer `protected abstract E self()`. `StringExpr extends Expr<StringExpr>` adds `contains(String)` returning `StringExpr` not `Expr<?>`. This is Java emulation of CRTP for fluent APIs without visitor overhead. Hibernate Criteria successor JPA Criteria is verbose—internal DSL justifies pattern. Don't CRTP a simple `UserBuilder`—Lombok `@Accessors(chain=true)` enough. Beware serialization and subclass explosion. Alternative: sealed interface `Expr` with records per node—JDK 21 may replace CRTP DSL for closed hierarchies. Unit test compile-time failures via separate compilation test source if critical.

#### What it is
CRTP binds a base class to its derived class through generic self-type parameter, enabling static polymorphism and fluent APIs where methods return the concrete subtype.

#### When to use / when NOT
- **Use** for fluent DSL builders needing subtype-returning methods.
- **Use** when closed hierarchy and performance discourage virtual calls (rare in Java business code).
- **NOT** for open-ended plugin systems needing runtime subtype discovery.
- **NOT** when generics erasure makes pattern feel like clever hack without real gain.
- **NOT** for teams uncomfortable maintaining self-bounded generics.

#### Java / Spring example
```java
abstract class Expr<E extends Expr<E>> {
    @SuppressWarnings("unchecked")
    protected E self() { return (E) this; }
    E and(Expr<?> other) { /* combine */ return self(); }
}
class StringExpr extends Expr<StringExpr> {
    StringExpr contains(String s) { return self(); }
}
```

#### Common mistakes
- Unchecked cast in `self()` without documented contract subclasses must follow.
- CRTP hierarchy too deep—use composition with sealed types instead.
- Expecting CRTP to eliminate reflection in frameworks that still need it.

#### Follow-up (with answer)
**Q:** CRTP vs Template Method pattern?
**A:** Template Method uses inheritance + overridden hooks with runtime dispatch; CRTP uses compile-time self-type for fluent chaining and sometimes inline-friendly calls. Template Method fits algorithm skeleton with varying steps; CRTP fits API ergonomics in DSLs. Spring's `JdbcTemplate` is Template Method, not CRTP.

---

### P038. Currying

**Category:** Behavioral
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/currying/)

**Short answer:** Currying transforms a function of multiple arguments into a sequence of unary functions—enabling partial application and configuration reuse. Java lacks native currying but emulates with lambdas and `Function` composition. Trade-off: readability cost for imperative teams; debugging nested lambdas. It hurts when all arguments are always available at call site, or when plain method with defaults is clearer.

#### Scenario (interview)
**Situation:** A reporting framework applies filters (`tenant`, `dateRange`, `productLine`) to many report generators. Each report repeated `filter(tenant, start, end, line)` with same tenant and dates per HTTP request on Spring MVC admin portal.
**What they're testing:** Functional style in Java, partial application, configuration without global state.
**Model answer:** I'd curry filter factory: `Function<String, Function<LocalDate, Function<LocalDate, Function<String, Predicate<Row>>>>> buildFilter` or use a small `FilterBuilder` record capturing tenant once per request. Controller resolves tenant from security context, produces `ReportContext.withTenant(tenant)` returning pre-bound `Predicate<Row>` for product line selection. Vavr `Function3.curried()` reduces boilerplate if library allowed. Avoid storing partially applied functions in static fields—request scope only. Contrast with Collecting Parameter—currying configures behavior, not accumulates results. For 2-arg cases, don't curry—`BiFunction` direct. Tests verify partial application fixes tenant so report code can't accidentally cross tenants. Senior: currying shines configuring Kafka `Consumer` serde per topic in `@Bean` factory methods chaining config.

#### What it is
Currying decomposes `f(a,b,c)` into `f(a)(b)(c)` each returning a function until final application. Enables partial application fixing some arguments early.

#### When to use / when NOT
- **Use** when configuring families of functions sharing most parameters.
- **Use** in functional DSLs and higher-order configuration.
- **NOT** for typical service methods with 3 args called once.
- **NOT** without team readability standards—document patterns.
- **NOT** mixing curried and uncurried overloads inconsistently.

#### Java / Spring example
```java
Function<String, Function<LocalDate, Predicate<Sale>>> salesFilter =
    tenant -> date -> sale -> sale.tenant().equals(tenant) && !sale.date().isBefore(date);
var todayForAcme = salesFilter.apply("acme").apply(LocalDate.now());
```

#### Common mistakes
- Currying for ceremony without reused partial configs.
- Capturing mutable variables in lambdas used as curried stages.
- Exception handling lost inside nested function returns.

#### Follow-up (with answer)
**Q:** Currying vs builder for report configuration?
**A:** Builder accumulates named optional parameters into one config object—imperative, readable for Java teams. Currying fixes positional arguments progressively—functional, compact for function pipelines. Use builder for 8+ optional report params with defaults; use currying when generating families of predicates from a fixed prefix (tenant, date) applied across functional report pipeline.

---

### P039. DAO Factory

**Category:** Enterprise
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/dao-factory/)

**Short answer:** DAO Factory creates and dispatches DAO implementations per persistence technology or schema—`CustomerDao` for Oracle vs PostgreSQL, or per tenant schema. Trade-off: factory indirection and duplicate DAO interfaces if over-abstracted. It hurts when Spring Data JPA repositories already provide factory-like wiring, or when only one database ever exists.

#### Scenario (interview)
**Situation:** A SaaS platform on Azure offers dedicated schema per enterprise tenant and shared schema for SMB. Some tenants require read replicas routed for reporting DAOs. Team manually `@Autowired` wrong `JdbcTemplate` bean twice causing cross-tenant data leak in staging.
**What they're testing:** Multi-tenancy persistence routing, factory selection, security isolation.
**Model answer:** I'd implement `DaoFactory` interface `CustomerDao customerDao()` resolved per `RequestContext.tenant()`—implementations `DedicatedSchemaDaoFactory`, `SharedSchemaDaoFactory` chosen by tenant metadata registry. Spring `@Configuration` provides prototype-scoped factory bean or `AbstractRoutingDataSource` with `DaoFactory` wrapping connection lookup. Reporting path returns read-replica bound DAO from same factory family. Unit tests mock factory per tenant profile. Don't factory-create DAO per call without pooling—cache per-request in context. Modern alt: Hibernate `MULTI_TENANT` discriminator reduces custom factory but dedicated schema still needs routing. DAO Factory differs from Abstract Factory product family—here focus is persistence technology/tenant dimension. Code review blocks direct `JdbcTemplate` injection in domain services.

#### What it is
DAO Factory encapsulates creation of DAO objects, hiding which concrete persistence implementation or connection strategy is used.

#### When to use / when NOT
- **Use** when multiple persistence configs, vendors, or tenant routing strategies coexist.
- **Use** to centralize DAO instantiation policy.
- **NOT** when Spring Data single `JpaRepository` interface suffices.
- **NOT** factory per table—one factory per persistence boundary.
- **NOT** without tests proving tenant A cannot get tenant B DAO.

#### Java / Spring example
```java
interface DaoFactory {
    CustomerDao customerDao();
    OrderDao orderDao();
}
@Component
class TenantDaoFactoryProvider {
    DaoFactory forTenant(String tenantId) { ... }
}
```

#### Common mistakes
- Factory returning new connection per DAO method—pool exhaustion.
- Leaking concrete JDBC DAO types through factory interface.
- Singleton factory holding tenant-specific state without request scope.

#### Follow-up (with answer)
**Q:** DAO Factory vs Spring `AbstractRoutingDataSource`?
**A:** Routing datasource switches JDBC connection per lookup key; DAO Factory selects DAO implementation class possibly wrapping different templates. Often combine: routing datasource handles connection; factory provides domain-specific DAO with correct SQL dialect quirks. Factory answers "which DAO API"; routing answers "which database."

---

### P040. Data Access Object (DAO)

**Category:** Enterprise
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/dao/)

**Short answer:** DAO encapsulates persistence operations for an entity or table—CRUD and queries—isolating business logic from SQL/JPA details. Trade-off: anemic DAO becoming SQL dumping ground; overlap with Repository in DDD. It hurts when DAO exposes persistence primitives to domain (`ResultSet`), or when Spring Data makes hand-rolled DAO redundant boilerplate.

#### Scenario (interview)
**Situation:** Legacy module uses JDBC DAOs with raw SQL; newer module uses Spring Data JPA. `OrderService` mixes both, with transaction boundaries spanning DAO calls causing partial commits when JDBC auto-commit leaked.
**What they're testing:** Persistence encapsulation, migration strategy, Repository vs DAO naming.
**Model answer:** I'd define `OrderDao` interface in domain port package with methods `Optional<Order> findById(OrderId id)`, `void save(Order)`—no SQL in service. `JdbcOrderDao` implements with named parameters; future `JpaOrderDao` or repository adapter behind same port during strangler migration. All DAO calls participate in Spring `@Transactional` service boundary. Map `ResultSet` to domain inside DAO via Data Mapper, not in service. Query methods express intent (`findOpenByCustomer`) not `select *`. For read-heavy search, separate `OrderQueryDao` CQRS-style. Don't return JPA entities from DAO if domain is POJO—map at boundary. Integration tests with Testcontainers PostgreSQL per DAO implementation. Senior: rename to Repository if team uses DDD ubiquitous language—pattern intent identical.

#### What it is
DAO provides abstract interface to data store operations, allowing business layer to remain persistence-ignorant. Core J2EE pattern; DDD Repository supersedes naming in many codebases.

#### When to use / when NOT
- **Use** when encapsulating SQL/JPA complexity behind intention-revealing methods.
- **Use** in legacy JDBC codebases or custom stores (Cosmos, Redis) without Spring Data.
- **NOT** exposing generic `save(Object)` CRUD for every table without domain meaning.
- **NOT** duplicating Spring Data derived queries in hand DAO without reason.
- **NOT** DAO calling DAO in chains—use service or query object.

#### Java / Spring example
```java
public interface OrderDao {
    Optional<Order> findById(OrderId id);
    void save(Order order);
}
@Repository
class JdbcOrderDao implements OrderDao { /* SQL + row mapper */ }
```

#### Common mistakes
- DAO methods returning `Map<String,Object>`—no type safety.
- Business validation inside DAO—belongs in domain.
- One DAO class per table with joins scattered in services—leaky abstraction.

#### Follow-up (with answer)
**Q:** DAO vs Repository in DDD Spring projects?
**A:** Repository is collection-like aggregate persistence abstraction speaking domain language; DAO is lower-level data access often table-oriented. Implement Repository using DAO internally or merge when Spring Data `JpaRepository` is the aggregate repository. Interview answer: same encapsulation goal—Repository emphasizes aggregate boundary and ubiquitous language; DAO emphasizes technology hiding.

---

### P041. Data Bus

**Category:** Architectural
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/data-bus/)

**Short answer:** Data Bus broadcasts data to all subscribed components without sender knowing receivers—event bus, message broker pub/sub. Decouples producers from consumers temporally and spatially. Trade-off: debugging flow, ordering guarantees, and schema evolution. It hurts for request/response workflows needing synchronous answers, or when a point-to-point queue would prevent accidental fan-out.

#### Scenario (interview)
**Situation:** After order placement, analytics, fraud scoring, warehouse allocation, and email service all need `OrderPlaced` notification. Point-to-point REST callbacks caused cascading timeouts when analytics lagged during Black Friday on Azure.
**What they're testing:** Pub/sub vs queues, Kafka topics, idempotent consumers, schema registry.
**Model answer:** I'd publish `OrderPlaced` to Kafka topic `orders.events` with Avro schema in Registry—data bus semantics. Independent consumer groups: fraud, warehouse, email, analytics each subscribe without order service knowing endpoints. Slow analytics doesn't block fulfillment consumer on separate group lag. Use key=orderId for partition ordering per order. Idempotent consumers with `processed_events` table dedupe. Contrast Event-driven vs Data Bus naming—here broadcast intent matters. Not for `getOrderStatus` query—REST or materialized view. Dead-letter topic + retry policy per consumer. Document that bus is at-least-once—design handlers accordingly. Spring Cloud Stream or raw `KafkaTemplate` both fine; avoid dual-write without outbox.

#### What it is
Data Bus pattern distributes data to multiple recipients through shared communication channel. Implementations include in-memory event bus, Guava EventBus, or distributed Kafka/Azure Event Hubs.

#### When to use / when NOT
- **Use** when one state change triggers many independent reactions.
- **Use** when producers shouldn't know consumers (organizational decoupling).
- **NOT** when synchronous aggregated response required—use orchestration or scatter-gather.
- **NOT** without schema governance on evolving events.
- **NOT** in-process EventBus for cross-service communication—use broker.

#### Java / Spring example
```java
kafkaTemplate.send("orders.events", orderId, new OrderPlacedEvent(orderId, lines));
// Consumers: @KafkaListener topics = "orders.events", groupId = "warehouse"
```

#### Common mistakes
- Treating Kafka as fire-and-forget without consumer monitoring.
- Shared consumer group causing messages consumed once total instead of per service.
- Publishing huge payloads—bus carries references/events, not bulk BLOBs.

#### Follow-up (with answer)
**Q:** Data Bus vs Mediator pattern?
**A:** Mediator coordinates colleagues through central object often synchronously in-process (e.g., dialog components). Data Bus is asynchronous broadcast infrastructure—senders don't know if anyone listens. Mediator encapsulates interaction protocol; Data Bus provides transport decoupling. Use Mediator within a service boundary; Data Bus across services.

---

### P042. Data Locality

**Category:** Performance
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/data-locality/)

**Short answer:** Data Locality places computation near data to minimize network transfer—cache on app node, partition Kafka by key, colocate Azure Function with storage account region. Trade-off: consistency, cache invalidation, and uneven hot partitions. It hurts when data is inherently global, when local copies stale dangerously, or when premature sharding adds ops burden before metrics justify it.

#### Scenario (interview)
**Situation:** A fraud scoring service reads customer profile from Cosmos DB in East US on every payment event consumed from Kafka. Cross-region RTT adds 40ms; at 8k TPS, RU costs and latency breach SLA. Events originate from payment service in same region.
**What they're testing:** Caching, partitioning, affinity, CAP trade-offs.
**Model answer:** I'd pursue locality at three levels. Co-locate fraud consumers in East US same region as Cosmos account—deployment topology. Partition Kafka by `customerId` so one consumer instance tends to process same customers, enabling local Caffeine cache with high hit ratio. Preload hot customer profiles via compacted changelog topic mirroring Cosmos—compute near data in memory. For truly hot keys, consider sharding profile store per partition. Measure hit ratio before distributed cache cluster. Trade-off: stale profile acceptable for velocity checks if snapshot timestamp in event triggers refresh on mismatch. Don't replicate entire Cosmos globally for this alone—evaluate regional active-active need separately. Data Locality pattern from HPC applies to microservices via affinity scheduling on AKS `nodeSelector` and stateful sets.

#### What it is
Data Locality optimizes by reducing distance between processing code and data storage—geographic, network hop, or memory hierarchy—improving latency and throughput.

#### When to use / when NOT
- **Use** when profiling shows network/IO dominates CPU-bound work.
- **Use** for stream processing with keyed state (Kafka Streams, Flink).
- **NOT** when strong global consistency requires single central store anyway.
- **NOT** caching without invalidation strategy on authoritative updates.
- **NOT** sharding before identifying actual hot key distribution.

#### Java / Spring example
```java
@KafkaListener(topics = "payments", groupId = "fraud",
    properties = "max.poll.records=500")
void onPayment(ConsumerRecord<String, PaymentEvent> rec) {
    var profile = localCache.get(rec.key(), () -> cosmos.load(rec.key()));
}
```

#### Common mistakes
- Assuming colocation without verifying cloud region config in IaC.
- Hot partition skew—one key dominates Kafka partition.
- Local cache ignoring tenant isolation in keys.

#### Follow-up (with answer)
**Q:** Data locality vs CDN for static product catalog?
**A:** CDN provides edge locality for read-mostly static assets—different mechanism, same principle. Application data locality uses regional DB replicas, keyed caching, and co-located compute. Use CDN for images/CSS; use data locality patterns for transactional customer state and stream processing state stores.

---

### P043. Data Mapper

**Category:** Enterprise
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/data-mapper/)

**Short answer:** Data Mapper moves data between domain objects and database without either knowing about the other—separate mapper layer handles SQL/ResultSet ↔ entity. Trade-off: mapping code volume; ORM blurs lines if entities are JPA-annotated. It hurts when anemic domain with `@Entity` on everything already couples layers, or when MapStruct could live in repository adapter without full Mapper pattern ceremony.

#### Scenario (interview)
**Situation:** Domain team insists pure POJO aggregates without JPA annotations; infrastructure team owns SQL tuned for Azure SQL partitioning. `Order` aggregate spans `orders`, `order_lines`, `order_taxes` tables. Developers annotated entities anyway "for speed," breaking Clean Architecture dependency rule.
**What they're testing:** Persistence ignorance, mapper ownership, aggregate hydration, Unit of Work.
**Model answer:** I'd implement `OrderDataMapper` with `Order find(OrderId id)` loading joined rows into single aggregate via private assembly methods, and `void insert/update(Order)` diffing aggregate state to SQL statements. No JPA—JdbcClient or jOOQ in infrastructure module. Domain `Order` has behavior `order.ship()` enforcing invariants. Mapper knows table layout; domain knows nothing of columns. Unit of Work (`SqlSession` or custom) tracks dirty aggregates in `@Transactional` service, commits via mapper flush. Contrast Active Record (Rails style) and ORM automatic mapping. Test mapper with Testcontainers using fixture SQL. Performance: batch line inserts, avoid SELECT N+1 with controlled joins. When team matures, Hibernate can implement same mapper interface behind adapter—domain unchanged.

#### What it is
Data Mapper (Fowler) is independent layer translating between in-memory domain objects and database. Gateway to persistence keeps domain model persistence-ignorant.

#### When to use / when NOT
- **Use** when domain must stay free of persistence framework annotations.
- **Use** when SQL complexity exceeds comfortable JPA mapping.
- **NOT** when simple CRUD and Spring Data JPA accelerates delivery without domain complexity.
- **NOT** hand-rolling mapper for 200 tables without codegen—consider jOOQ/ORM.
- **NOT** mapper containing business rules—mapping only.

#### Java / Spring example
```java
class OrderDataMapper {
    Order findById(OrderId id) { /* join query → Order aggregate */ }
    void update(Order order) { /* diff lines, taxes → SQL */ }
}
```

#### Common mistakes
- Mapper exposing `ResultSet` or `Row` to domain layer.
- Identity map missing—duplicate aggregate instances in same transaction.
- Mapping lazy collections triggering N+1 outside transaction.

#### Follow-up (with answer)
**Q:** Data Mapper vs Repository pattern?
**A:** Repository is domain-facing collection abstraction (`find`, `save`); Data Mapper is infrastructure technique Repository implementation uses internally. Public port is Repository; Data Mapper is how you fulfill it without annotating domain. Spring Data JPA repository is not Data Mapper—it's ORM-backed unless you custom `@Override` methods with EntityManager and manual mapping.

---

### P044. Data Transfer Object (DTO)

**Category:** Enterprise
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/data-transfer-object/)

**Short answer:** DTO carries data across process or layer boundaries—API responses, Kafka messages, batch files—without behavior, optimized for serialization. Trade-off: mapping proliferation and duplicate schema with domain model. It hurts when DTOs leak into domain logic, when identical to entity with no boundary benefit, or when versioning neglected breaking mobile clients.

#### Scenario (interview)
**Situation:** Spring `@RestController` returned JPA `Customer` entities directly; Hibernate lazy-load caused `LazyInitializationException` in production and exposed internal `passwordHash` field in JSON to mobile app. OpenAPI spec drifted from actual responses after field renames.
**What they're testing:** API contract stability, mapping, security field exclusion, versioning.
**Model answer:** I'd introduce `CustomerSummaryDto` and `CustomerDetailDto` for read paths—records with explicit fields, no lazy proxies. MapStruct from domain or projection query in service layer. Never serialize entities. Password and internal flags excluded by construction, not `@JsonIgnore` on entity. Version API `/v2/customers` with new DTO when breaking; deprecate v1 with sunset header. Kafka events use `Avro` generated DTOs from schema registry, not domain classes—evolution rules enforced. DTOs are immutable records validated at boundary. Contrast with domain entity behavior—`Customer.activate()` stays in domain, DTO only carries `status` string for wire. Contract tests (Pact) lock mobile expectations. Over-DTOing internal service calls inside monolith—use domain objects; DTOs at trust boundaries only.

#### What it is
DTO is serializable bag of fields transferring data between subsytems without exposing internal object model. Fowler pattern for remote/EJB boundaries; still essential at API edges.

#### When to use / when NOT
- **Use** at API, messaging, and integration boundaries.
- **Use** when response shape intentionally differs from domain (field subsets, flattening).
- **NOT** for in-process calls within same module—use domain types.
- **NOT** duplicating entity 1:1 indefinitely—consolidate views (`Summary`, `Detail`).
- **NOT** putting business logic methods on DTOs—slippery to anemic domain elsewhere.

#### Java / Spring example
```java
public record CustomerSummaryDto(String id, String displayName, String tier) {}
// Controller
return customerService.get(id).map(mapper::toSummaryDto);
```

#### Common mistakes
- Mutable DTOs with setters used as domain stand-in.
- One mega `CustomerDto` for every endpoint—over/under-fetching.
- Forgetting API versioning when DTO fields change semantics.

#### Follow-up (with answer)
**Q:** DTO vs Java record as domain value object?
**A:** Records can be value objects inside domain with behavior and invariants. DTOs live at boundary—serialization-shaped, validation for wire format, no domain behavior. A `MoneyDto` with `String amount` is wire format; domain `Money` value object has `add()` and currency rules. Don't reuse wire DTO as domain type to skip mapping—couples API changes to domain.

---

### P045. Decorator

**Category:** Structural
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/decorator/)

**Short answer:** Decorator wraps an object to add responsibilities dynamically without subclass explosion—`BufferedInputStream`, caching wrappers, `@Transactional` proxies. Trade-off: deep wrapper chains complicate debugging and ordering. It hurts when Spring AOP already provides cross-cutting decorators, or when composition order bugs cause subtle double-charging.

#### Scenario (interview)
**Situation:** `PricingService` needs optional behaviors: audit logging, metrics, caching, and rate limiting depending on merchant tier. Subclassing `CachingAuditedPricingService` combinatorics reached eight classes. Some merchants got double-counted metrics when two decorators both wrapped calls incorrectly.
**What they're testing:** Open/closed principle, decorator ordering, Spring `@Primary` vs manual composition, vs Proxy pattern.
**Model answer:** I'd keep `PricingService` interface with core `StandardPricingService` implementation. Decorators implement same interface, delegate to wrapped instance: `MetricsPricingDecorator`, `CachingPricingDecorator`, `AuditPricingDecorator`. Spring `@Configuration` builds bean via ordered composition based on merchant config flags—or use `BeanPostProcessor` sparingly. Order matters: cache outside metrics if cache hit shouldn't count as business call; document order in bean factory method. Java IO-style constructor injection of delegate. Contrast with subclassing—add new decorator class, no change to core. Spring `@Cacheable` is declarative decorator via AOP proxy—understand you're already using pattern. Test each decorator in isolation with mock delegate. Don't decorator across transaction boundary without understanding self-invocation—interface injection required.

#### What it is
Decorator attaches additional responsibilities to object dynamically by wrapping it with decorator classes sharing the same interface. Alternative to subclassing for feature combination.

#### When to use / when NOT
- **Use** when behaviors combine optionally and orthogonally (cache + log + secure).
- **Use** when adding features at runtime per configuration.
- **NOT** when Spring AOP annotations express same with less boilerplate.
- **NOT** when order-dependent stacking isn't documented—production surprises.
- **NOT** subclassing when only one fixed combination ever exists.

#### Java / Spring example
```java
PricingService bean = new AuditPricingDecorator(
    new CachingPricingDecorator(
        new StandardPricingService(), cache), auditLog);
```

#### Common mistakes
- Decorator not implementing full interface—Liskov break on new interface methods.
- Double-wrapping same decorator via Spring misconfiguration.
- Stateful decorators shared singleton across tenants without keying state.

#### Follow-up (with answer)
**Q:** Decorator vs Proxy pattern?
**A:** Structurally identical—wrap delegate, same interface. Intent differs: Decorator adds responsibilities (cache, compress); Proxy controls access (lazy load, security, remote). `CachingPricingDecorator` adds behavior; `RemotePricingProxy` manages remote access. Spring transactional JDK proxy is Proxy; manually wrapping with cache is Decorator. Interview: mention intent, accept structural similarity.

---



# Design Patterns Catalog — Part 2 (P046–P090)

Scenario-based senior interview Q&A aligned with [java-design-patterns.com](https://java-design-patterns.com/patterns/).

---

### P046. Delegation

**Category:** Behavioral  
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/delegation/)

**Short answer:** Delegation forwards work to a collaborator instead of inheriting behavior. It favors composition over inheritance, keeps classes focused, and makes swapping implementations testable. Trade-off: indirection and wiring overhead. It hurts when you delegate everything through one god object or leak the delegate's API through pass-through methods that add no value.

#### Scenario (interview)
**Situation:** A payments team owns `PaymentProcessor` that extends a vendor SDK class. Every SDK upgrade breaks compilation because overrides are scattered across fee calculation, idempotency keys, and webhook parsing. QA cannot stub the vendor in integration tests.
**What they're testing:** Can you refactor inheritance into delegation without changing external contracts?
**Model answer:** I would stop subclassing the vendor SDK. `PaymentProcessor` becomes a thin domain service that owns a `PaymentPort` interface; an `AdyenAdapter` delegates to the SDK while the domain speaks in our types. Public methods on the processor delegate one concern each—`authorize()` delegates to port, `buildIdempotencyKey()` stays in domain. Spring wires `@Primary AdyenAdapter` in prod and `FakePaymentPort` in tests. I audit for "inheritance for reuse only"—if we're not specializing lifecycle, delegation wins. Rollout: introduce port behind feature flag, run shadow traffic comparing old subclass vs new delegate, then delete extends. Metrics: compile-time coupling (imports of vendor in domain module should hit zero), test time without Testcontainers, and chargeback rate unchanged. If delegates become pass-through chains, I collapse to a single façade port rather than delegate-of-delegate.

#### What it is
An object handles a request by assigning responsibility to another object (the delegate). The delegator implements the same interface or a subset and forwards calls. It encodes "has-a" specialization instead of "is-a" extension.

#### When to use / when NOT
- **Use:** Vendor SDK integration, policy objects, decorating without full Decorator chain, splitting god classes.
- **NOT:** When Liskov specialization genuinely requires polymorphic subtype identity (rare in Spring services). Not when a single line call adds no boundary—inline instead.

#### Java / Spring example

```java
@Service
class PaymentProcessor {
    private final PaymentPort port;
    PaymentProcessor(PaymentPort port) { this.port = port; }
    public AuthResult authorize(PaymentCommand cmd) {
        return port.authorize(cmd.withIdempotencyKey(domainKey(cmd)));
    }
}
```

#### Common mistakes
- Pass-through methods on every SDK method—no domain boundary.
- Delegating to mutable singletons shared across tenants.
- Confusing Delegation with Proxy—proxy adds control; delegation assigns core work.

#### Follow-up (with answer)
**Q:** Delegation vs Decorator?
**A:** Decorator wraps to add responsibilities (logging, caching) while preserving interface and stacking layers. Delegation assigns core behavior to a collaborator—the delegator may not mirror the full delegate API. In Spring, `@Transactional` proxy is Decorator; a service forwarding to `PaymentPort` is Delegation. Choose Decorator when cross-cutting wraps many implementations; choose Delegation when replacing inheritance and isolating a vendor.

---

### P047. Dependency Injection

**Category:** Architectural  
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/dependency-injection/)

**Short answer:** Dependency Injection supplies collaborators from outside rather than constructing them inside. Inversion of Control containers (Spring) manage lifecycle, scope, and wiring. Trade-off: startup complexity and framework magic. It hurts when constructors take 15 parameters, when field injection hides dependencies, or when `@Autowired` on everything masks missing domain boundaries.

#### Scenario (interview)
**Situation:** A monolith's `OrderService` does `new RestTemplate()`, reads DB URLs from static util, and pulls `TenantContext.get()` everywhere. Multi-tenant rollout fails because test profile accidentally hits prod fraud API. On-call cannot mock dependencies during incident replay.
**What they're testing:** Do you understand DI as a design discipline, not just `@Autowired`?
**Model answer:** I'd treat DI as constructor-injected ports, not annotation sprawl. Extract `FraudClient`, `OrderRepository`, `Clock`, and `TenantResolver` interfaces; `OrderService` gets them via constructor—immutable, explicit, testable. Spring `@Configuration` binds implementations per profile: `WireMockFraudClient` in test, real client in prod with Resilience4j wrapper. Kill static `TenantContext` in domain—pass `TenantId` as method args from a web filter. For the incident, I'd verify no `new` on infrastructure in domain module via ArchUnit. Scope matters: singleton fraud client with connection pool, request-scoped tenant holder as filter attribute not static ThreadLocal without cleanup. Rollout: module-by-module constructor injection, fail build on field `@Autowired` in new code. Success metrics: unit test coverage without `@SpringBootTest`, zero cross-tenant fraud calls in audit logs, faster CI (tests run in milliseconds not seconds).

#### What it is
Objects receive their dependencies via constructor, setter, or interface injection rather than creating them. A container resolves the object graph, manages scopes, and applies cross-cutting proxies.

#### When to use / when NOT
- **Use:** Any service with external I/O, testability requirements, environment-specific implementations.
- **NOT:** Pure value objects, one-off CLI scripts, or trivial `main()`—manual wiring is fine.

#### Java / Spring example

```java
@Service
class OrderService {
    private final OrderRepository repo;
    private final FraudClient fraud;
    OrderService(OrderRepository repo, FraudClient fraud) {
        this.repo = repo; this.fraud = fraud;
    }
}
```

#### Common mistakes
- Field injection in services (hidden deps, final fields impossible).
- Injecting concrete SDK types into domain.
- God `@Configuration` with 200 `@Bean` methods and no modular boundaries.

#### Follow-up (with answer)
**Q:** Constructor injection vs `@Lookup` / `ObjectProvider`?
**A:** Constructor injection is default for required, stable dependencies—clear, testable, immutable. Use `ObjectProvider<PrototypeBean>` or `@Lookup` when a singleton needs a fresh prototype per operation (e.g., stateful formatter). Avoid injecting `ApplicationContext` directly—that's Service Locator in disguise. Prefer explicit factory bean when creation logic is non-trivial.

---

### P048. Dirty Flag

**Category:** Performance  
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/dirty-flag/)

**Short answer:** Dirty Flag tracks whether cached derived state is stale and recomputes only when needed. It avoids redundant expensive work on every read. Trade-off: invalidation bugs and thread-safety complexity. It hurts when the flag is never cleared, when every field write marks everything dirty, or when "lazy recompute on read" blocks user threads under load.

#### Scenario (interview)
**Situation:** A pricing dashboard recomputes `MarginReport` from 40k line items on every REST poll—CPU pegs at month-end. Developers add `@Cacheable` but cache never invalidates when underlying deals change; traders see stale margins for two hours.
**What they're testing:** Can you design explicit invalidation instead of blind caching?
**Model answer:** I'd model `DealBook` with a `revision` counter and `MarginReport` holding `computedAtRevision`. Any mutating command increments revision and sets `marginDirty=true` on the aggregate root—no recompute yet. On read, if dirty or revision mismatch, recompute once synchronously or via async job depending on SLA; then clear dirty and store snapshot revision. For month-end spikes, recompute async on write batch completion and serve last good snapshot with `stale-while-revalidate` header. Thread-safety: single writer per aggregate, readers see atomic snapshot reference. I'd avoid `@Cacheable` without TTL + event eviction—here domain dirty flag is precise. Metrics: recompute count per hour (should track writes not polls), p99 read latency, staleness alert if served revision lags > N seconds after write. Tests: mutate deal, assert dirty, read triggers single compute, second read hits cache.

#### What it is
A boolean (or version) marks in-memory derived data as outdated. Mutations set the flag; readers check it before using cached results and refresh if needed.

#### When to use / when NOT
- **Use:** Expensive derived views, UI models, in-memory aggregates, game state meshes.
- **NOT:** When source of truth is always external—query the DB. Not when invalidation graph is huge—use event stream or CQRS projection instead.

#### Java / Spring example

```java
class DealBook {
    private long revision;
    private boolean marginDirty = true;
    private volatile MarginReport cached;
    MarginReport margin() {
        if (marginDirty) { cached = compute(); marginDirty = false; }
        return cached;
    }
    void apply(DealEvent e) { applyInternal(e); revision++; marginDirty = true; }
}
```

#### Common mistakes
- Forgetting to set dirty on one of seven mutation paths.
- Non-volatile dirty flag with unsynchronized reads— torn visibility.
- Recomputing on every read "just to be safe"—defeats the pattern.

#### Follow-up (with answer)
**Q:** Dirty flag vs JPA `@Cache` vs Redis?
**A:** Dirty flag suits in-process derived state tied to a single aggregate instance—precise invalidation, no network. JPA second-level cache helps entity graphs but invalidation across nodes is coarse. Redis fits shared cross-instance read models with TTL or pub/sub eviction. Pick dirty flag when recompute is local and cheap enough; pick external cache when multiple pods serve the same hot read model.

---

### P049. Domain Model

**Category:** Enterprise  
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/domain-model/)

**Short answer:** Domain Model puts business rules inside rich objects rather than anemic data holders plus service procedures. Entities, value objects, and aggregates enforce invariants at creation and mutation. Trade-off: ORM impedance and learning curve. It hurts when every rule lives in `*Service` with public setters on entities, or when you model every DB column as an entity with no behavioral cohesion.

#### Scenario (interview)
**Situation:** `LoanApplication` is a JPA entity with public setters; `LoanService` is 2,400 lines validating status transitions, computing LTV, and sending emails. Two teams add conflicting rules—one allows approve at 95% LTV for VIP, another rejects at 90%. Production approves a loan that compliance later reverses manually.
**What they're testing:** Can you move invariants into the domain without fighting JPA?
**Model answer:** I'd identify `LoanApplication` as aggregate root—status transitions become methods: `approve(UnderwriterId, Policy)` checks LTV, VIP tier, and regulatory caps inside the entity, throwing domain exceptions on violation. Value objects: `LtvRatio`, `Money`, `UnderwriterDecision` immutable. External calls (email, credit bureau) stay in application services after domain emits domain events. JPA: package-private setters, `@Embeddable` for value types, avoid bidirectional graphs that break invariants. Policy for VIP: inject `LendingPolicy` interface into method, not if-else in service. Audit trail via `@Embedded` decision metadata. Rollout: strangler on `approve()` path first—service delegates to entity method; ArchUnit forbids `setStatus` outside aggregate package. Metrics: manual compliance reversals drop, cyclomatic complexity in service falls, unit tests on aggregate run without Spring. Interview point: rich model doesn't mean entity calls Kafka—keep side effects at edges.

#### What it is
An object model where domain objects contain both data and behavior representing business concepts. Services orchestrate use cases; entities enforce rules and protect consistency boundaries.

#### When to use / when NOT
- **Use:** Complex business rules, regulated domains, long-lived products where rules evolve.
- **NOT:** Simple CRUD admin screens—Transaction Script + DTO is fine. Not when team lacks DDD vocabulary and deadline is two weeks.

#### Java / Spring example

```java
@Entity
class LoanApplication {
    @Embedded private LtvRatio ltv;
    public void approve(UnderwriterId id, LendingPolicy policy) {
        if (!policy.allows(ltv, tier)) throw new DomainRuleException("LTV");
        this.status = Status.APPROVED;
        registerEvent(new LoanApproved(id));
    }
}
```

#### Common mistakes
- Anemic entities + obese services—pattern in name only.
- Domain calling `EntityManager` or HTTP clients directly.
- One giant aggregate spanning entire order graph—locking nightmares.

#### Follow-up (with answer)
**Q:** Domain Model vs Transaction Script?
**A:** Transaction Script organizes logic in procedures per use case—fast for simple apps. Domain Model embeds rules in objects—better when rules multiply and intersect. Switch when change requests repeatedly touch the same 3k-line service or bug class is "invalid state reachable." Keep scripts for reporting ETL; use rich model for core revenue and compliance paths.

---

### P050. Double Buffer

**Category:** Concurrency  
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/double-buffer/)

**Short answer:** Double Buffer uses two copies of data—one displayed/consumed, one written—then swaps atomically. Producers and consumers don't block each other on the same buffer. Trade-off: memory duplication and swap coordination. It hurts when buffers are huge and swap copies instead of pointer swap, or when readers see torn partially-updated state without atomic publish.

#### Scenario (interview)
**Situation:** A real-time risk dashboard serves `ExposureSnapshot` to 500 websocket clients while a batch job recomputes exposures from Kafka ticks. Current design uses one `ConcurrentHashMap` mutated in place—clients occasionally see negative exposure when half the sectors updated.
**What they're testing:** Do you understand publish-snapshot vs mutate-in-place?
**Model answer:** I'd maintain two immutable snapshots: `active` and `staging`. The Kafka consumer builds a new immutable `ExposureSnapshot` in staging off the hot path—no partial visibility. When complete, atomically swap reference: `active = staging; staging = rebuildEmpty()`. Websocket layer always serializes `active`—readers never lock. Use volatile reference or `AtomicReference<ExposureSnapshot>` for swap. Memory: structural sharing (persistent collections or copy-on-write sector maps) so swap isn't full clone of 2GB. Backpressure: if compute lags ticks, coalesce updates and skip intermediate frames—SLO is consistent snapshot not every tick. Metrics: swap latency, staleness age of active, allocation rate. Don't double-buffer tiny config—overkill. For Spring, expose snapshot as `@Scheduled` rebuild + atomic publish, not `@Cacheable` mutate. Incident fix: immediate switch to immutable snapshots stopped torn reads without stopping tick ingestion.

#### What it is
Two buffers alternate roles: one is read while the other is written. After the write completes, roles swap so readers always see a consistent complete version.

#### When to use / when NOT
- **Use:** Graphics frames, high-frequency read dashboards, telemetry ring buffers with consistent views.
- **NOT:** Single writer single reader queue—use disruptor or blocking queue. Not when data must be strongly consistent with DB—read from store.

#### Java / Spring example

```java
class SnapshotPublisher {
    private volatile ExposureSnapshot active = ExposureSnapshot.empty();
    void publish(ExposureSnapshot next) { this.active = next; }
    ExposureSnapshot current() { return active; }
}
```

#### Common mistakes
- Mutating the "inactive" buffer that's still referenced by slow readers.
- Deep-copying megabytes every tick instead of immutable structural sharing.
- Swapping without happens-before—readers see null or mixed fields.

#### Follow-up (with answer)
**Q:** Double buffer vs Copy-on-Write collections?
**A:** Copy-on-write (e.g., `CopyOnWriteArrayList`) fits small, rarely mutated lists read often. Double buffer fits large computed snapshots rebuilt wholesale. Both publish immutable views; double buffer makes the rebuild/swap explicit for frame-sized data. For sector maps, COW per key or persistent data structures often beat full double buffer.

---

### P051. Double-Checked Locking

**Category:** Concurrency  
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/double-checked-locking/)

**Short answer:** Double-Checked Locking lazily initializes a singleton with a volatile check outside synchronized block to avoid lock cost after init. In Java, broken without `volatile` due to instruction reordering. Trade-off: subtle memory model bugs. It hurts in 2026 when Spring, holder idiom, or `enum` singleton already solve the problem—you're optimizing nanoseconds on cold paths.

#### Scenario (interview)
**Situation:** A legacy metrics library uses DCL for `MetricRegistry.getInstance()`. After JDK upgrade, rare NPE in prod on ARM Graviton instances—registry partially constructed. Team debates adding more `synchronized` blocks.
**What they're testing:** Do you know JMM fixes and modern alternatives?
**Model answer:** Root cause is classic broken DCL: instance reference published before field init visible to other threads without `volatile`. Fix options ranked: (1) delete singleton—inject `MetricRegistry` as Spring bean; (2) holder idiom—static holder class init is JVM-synchronized; (3) enum singleton; (4) if DCL must stay, `private static volatile MetricRegistry instance` with synchronized init block. I'd not add nested locks—that hides the design smell. For library code not under Spring, holder idiom is clearest. Reproduce with `-XX:-UseBiasedLocking` stress test and JCStress before/after. Document why DCL exists—if only for lazy init of heavy SDK, prefer `Supplier<MetricRegistry>` injected once at startup. Metrics: NPE rate on registry access (should zero), startup time unchanged. Senior message: DCL is interview trivia; production Java avoids it unless profiling proves lazy init matters and alternatives don't fit OSGi/classloader constraints.

#### What it is
Check instance null without lock; if null, synchronize, check again, construct once. Requires `volatile` in Java so published object is fully constructed to all threads.

#### When to use / when NOT
- **Use:** Rarely—lazy singleton without container in non-Spring embedded agents.
- **NOT:** Spring beans, enum singleton cases, anything testable via DI. Never without `volatile`.

#### Java / Spring example

```java
// Prefer holder idiom over DCL
class MetricRegistryHolder {
    static class Holder {
        static final MetricRegistry INSTANCE = new MetricRegistry();
    }
    static MetricRegistry get() { return Holder.INSTANCE; }
}
```

#### Common mistakes
- Missing `volatile` on instance field.
- DCL on non-immutable singleton with post-construct mutation visible early.
- Using DCL in clustered services expecting one global instance—each JVM still has one.

#### Follow-up (with answer)
**Q:** Why did DCL break before Java 5 memory model?
**A:** Without volatile, another thread could see non-null reference to partially constructed object due to reordering of constructor and field write. Java 5+ volatile write/read establishes happens-before. Still prefer initialization-on-demand holder because it's simpler and JVM guarantees class init safety without developer juggling volatile.

---

### P052. Double Dispatch

**Category:** Behavioral  
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/double-dispatch/)

**Short answer:** Double Dispatch resolves behavior based on two runtime types—typically `visitor.visit(element)` where overload picks both visitor and element type. It replaces chained `instanceof` when adding new operations is frequent. Trade-off: Visitor rigidity when adding new element types. It hurts when you apply Visitor for two types once—use polymorphism or sealed switch instead.

#### Scenario (interview)
**Situation:** A tax export pipeline must render `Invoice`, `CreditNote`, and `DebitNote` into XML, PDF, and new MT940 bank format. Each exporter is a nest of `if (doc instanceof Invoice)` duplicated across three classes—adding MT940 required editing nine methods.
**What they're testing:** Can you refactor to Visitor without breaking domain module dependencies?
**Model answer:** I'd define `TaxDocument` accept method: `void accept(TaxDocumentVisitor v)` implemented per concrete doc type—that's first dispatch. Visitor interface has `visit(Invoice)`, `visit(CreditNote)`, `visit(DebitNote)`—second dispatch via overload resolution. `Mt940Exporter implements TaxDocumentVisitor` adds new operation without touching document classes if types stable. If new document types arrive often (regulatory), Visitor hurts—use sealed interface + exhaustive switch (Java 21) for operations instead. Keep documents in domain module; visitors in infrastructure export module to avoid dependency inversion violation. Rollout: introduce visitor alongside old instanceof, golden-file tests per format, delete instanceof when parity proven. Performance: virtual calls negligible vs I/O; avoid megamorphic visitor chains hot in inner loop. Follow-up trap: adding `ProFormaInvoice` breaks all visitors—plan for sealed hierarchy and compiler-checked switch when types evolve.

#### What it is
Two polymorphic dispatches select the correct method: object accepts visitor, visitor method overload resolves on concrete type pair. Classic GoF Visitor pattern implements double dispatch in single-dispatch languages.

#### When to use / when NOT
- **Use:** Stable type hierarchy, many operations over same types (export, validate, price).
- **NOT:** Frequently added types—switch on sealed types or polymorphic methods per type instead.

#### Java / Spring example

```java
sealed interface TaxDocument permits Invoice, CreditNote {
    void accept(TaxDocumentVisitor v);
}
record Invoice(Money total) implements TaxDocument {
    public void accept(TaxDocumentVisitor v) { v.visit(this); }
}
```

#### Common mistakes
- Visitor in domain core pulling in PDF libraries—wrong module direction.
- Non-exhaustive visitor when new subtype added—silent fall-through.
- Using double dispatch for two variants total—over-engineering.

#### Follow-up (with answer)
**Q:** Visitor vs sealed switch vs instanceof chain?
**A:** Instanceof chains rot fastest. Sealed switch with exhaustiveness is best when operations add often and types stable in Java 17+. Visitor when operations add often and you can't recompile all switches centrally (plugins). Prefer polymorphic method on each type when only one operation varies—`document.toMt940()` keeps it simple.

---

### P053. Dynamic Proxy

**Category:** Structural  
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/dynamic-proxy/)

**Short answer:** Dynamic Proxy creates runtime wrapper objects implementing interfaces without compile-time subclasses. JDK proxies use interfaces; CGLIB subclasses concrete classes. Spring AOP, `@Transactional`, and Micrometer timing rely on it. Trade-off: debugging stack traces, self-invocation bypass, final method limits. It hurts when teams `@Transactional` private methods wondering why TX never starts.

#### Scenario (interview)
**Situation:** After enabling `@Cacheable` on repository interfaces, some calls hit DB every time. Developer added `@Transactional` on private helper in same class—partial commits corrupt inventory during flash sale.
**What they're testing:** Do you understand proxy boundaries and Spring AOP mechanics?
**Model answer:** Spring wraps beans in JDK dynamic proxy (interface) or CGLIB subclass (concrete class). Interceptors run only on external calls through proxy—`this.saveHelper()` inside same class bypasses `@Transactional` and `@Cacheable`. Fix: move helper to another bean, use self-injection `@Lazy`, or AspectJ compile-time weaving for true join points. For cache misses, verify proxy is created—`@Cacheable` on package-private method of class without interface may miss unless CGLIB enabled; `spring.aop.proxy-target-class=true`. I'd add integration test asserting transaction rollback on forced failure through public method. Metrics: cache hit ratio, unexpected DB QPS during sale. For debugging, log `AopUtils.isAopProxy(bean)` and proxy class name in staging. Senior insight: Dynamic Proxy is feature, not pattern to hand-roll except for RPC stubs—prefer Spring's abstraction. Document "no transactional private methods" in team ADR.

#### What it is
Runtime-generated proxy implements same interface as target, delegating calls through `InvocationHandler` that can add behavior before/after. Enables cross-cutting without modifying target source.

#### When to use / when NOT
- **Use:** Framework cross-cutting—TX, security, metrics, remoting stubs.
- **NOT:** Core business rules—belongs in domain code. Not when AspectJ CTW already mandated for performance.

#### Java / Spring example

```java
// Spring handles proxy; manual JDK proxy for illustration
PaymentPort proxy = (PaymentPort) Proxy.newProxyInstance(
    cl, new Class[]{PaymentPort.class},
    (p, m, args) -> { log(m); return m.invoke(target, args); });
```

#### Common mistakes
- Self-invocation expecting intercepted behavior.
- Caching/final methods on CGLIB target—cannot override.
- Assuming `@Transactional` on controller—TX boundary should be service layer.

#### Follow-up (with answer)
**Q:** JDK proxy vs CGLIB vs AspectJ?
**A:** JDK proxy requires interface, lighter, standard for Spring Data repos. CGLIB subclasses concrete classes—needs non-final methods, extra metadata. AspectJ weaving weaves bytecode directly—works on self-invocation and private methods if configured, higher build complexity. Default Spring Boot uses CGLIB when no interface—know which applies when debugging TX.

---

### P054. Event Aggregator

**Category:** Behavioral  
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/event-aggregator/)

**Short answer:** Event Aggregator decouples many publishers from many subscribers via central hub—publishers don't know subscribers. Spring `ApplicationEventPublisher`, Guava EventBus, and UI event buses follow this. Trade-off: hub becomes bottleneck and ordering/global policy choke point. It hurts when aggregator handles business logic instead of routing, or when synchronous bus blocks request threads on slow listeners.

#### Scenario (interview)
**Situation:** Order placement publishes `OrderCreated`, `InventoryReserved`, `PaymentCaptured` from three services directly to twelve email, analytics, and warehouse listeners—circular Kafka imports and duplicate event handling during replays.
**What they're testing:** Can you centralize fan-out without turning hub into god service?
**Model answer:** I'd introduce domain event aggregator at application boundary—not a microservice yet, an in-process `OrderLifecycleBus` or lightweight Kafka topic `order.events` with schema registry. Publishers emit canonical envelope `{type, orderId, payload, correlationId}` once; aggregator routes to subscribed channels asynchronously. Listeners register by event type; aggregator does no business rules except validation and idempotency key dedup. Move from direct Kafka fan-out from each service to outbox + single publish per aggregate transaction. For cross-service, Kafka with consumer groups per downstream replaces bespoke aggregator service unless you need content-based routing rules centralized. Async mandatory—`@EventListener` default sync blocked HTTP during Black Friday when analytics listener ran 800ms SQL. Use `@Async` or transactional outbox to worker. Metrics: listener lag, duplicate delivery rate, hub error queue depth. Anti-pattern: aggregator that calculates shipping— that's domain service. Test: publish once, assert each subscriber exactly once with idempotent consumer pattern.

#### What it is
Central mediator receives events from publishers and notifies subscribers without direct coupling. Subscribers register interest; publishers remain unaware of consumers.

#### When to use / when NOT
- **Use:** UI component coordination, in-process domain events, bridging modules without dependency tangles.
- **NOT:** Cross-service choreography needing durability—use message broker with outbox. Not when two parties only—direct call simpler.

#### Java / Spring example

```java
@Component
class OrderEventAggregator {
    private final ApplicationEventPublisher bus;
    void on(OrderCreated e) { bus.publishEvent(e); } // subscribers @EventListener
}
```

#### Common mistakes
- Synchronous listeners doing I/O on request thread.
- Business logic inside aggregator routing layer.
- No idempotency when replaying events from log.

#### Follow-up (with answer)
**Q:** Event Aggregator vs Mediator vs Kafka?
**A:** Mediator coordinates colleague objects on complex workflows with reciprocal awareness abstracted. Event Aggregator is publish-subscribe—publishers don't know subscribers. Kafka is distributed durable aggregator with log retention; in-process bus is for monolith modularity. Choose Kafka when failure isolation and replay matter; choose in-process for same JVM decoupling with outbox escape hatch.

---

### P055. Event-Based Asynchronous

**Category:** Concurrency  
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/event-based-asynchronous/)

**Short answer:** Event-Based Asynchronous initiates long operations without blocking caller; completion arrives via callback, future, or event. Spring `@Async`, CompletableFuture, and reactive streams embody this. Trade-off: error propagation, tracing, and backpressure complexity. It hurts when fire-and-forget loses failure signals until reconciliation job finds silent drops.

#### Scenario (interview)
**Situation:** Customer onboarding API calls credit bureau synchronously—p99 12s, thread pool exhausted under marketing campaign. Team wraps call in `@Async` but clients still poll status because no completion contract exists; MDC trace IDs vanish in async threads.
**What they're testing:** Can you design async with observability and client contract?
**Model answer:** I'd model onboarding as command returning `202 Accepted` with `jobId` and subscribe to completion via webhook or SSE polling backed by job store—not naked `@Async void`. Credit check runs on bounded `@Async` executor with queue depth metrics; propagate trace via `TaskDecorator` copying MDC. Completion publishes `OnboardingCompleted` event to aggregator; failed async writes `FAILED` with reason to `onboarding_jobs` table—never swallow exceptions in void async. Client contract: status endpoint reads job row; idempotent retry on same `Idempotency-Key` returns same jobId. Resilience: bulkhead separate executor from HTTP pool; timeout on bureau call; circuit breaker. Compare Event-Based Async to messaging—if SLA > 30s or volume high, outbox to Kafka worker instead of in-memory async. Metrics: async queue depth, failed job rate, trace continuity (% spans linked). Load test proves HTTP threads flat while workers scale. This pattern is initiation + callback/event, not "make it async and hope."

#### What it is
Caller starts operation and continues; system signals completion asynchronously through handler, future, or message. Separates invocation thread from execution thread.

#### When to use / when NOT
- **Use:** External slow I/O, parallel fan-out, UI responsiveness.
- **NOT:** When caller needs result immediately for same request. Not when transactional consistency required in same request without saga.

#### Java / Spring example

```java
@Async("onboardingExecutor")
public CompletableFuture<CreditResult> checkCredit(AppId id) {
    return CompletableFuture.completedFuture(bureau.pull(id));
}
```

#### Common mistakes
- `@Async` on self-invocation (no proxy, still sync).
- Unbounded executor queue masking overload until OOM.
- Lost exceptions in void async methods.

#### Follow-up (with answer)
**Q:** `@Async` vs message queue worker?
**A:** `@Async` suits same-process short tasks with retry and moderate volume—simple but dies with pod restart. Message queue gives durability, replay, cross-service scaling—prefer when work must survive crashes or processing exceeds seconds/minutes. Hybrid: HTTP accepts job, outbox publishes to Kafka worker—best production durability.

---

### P056. Event-Driven Architecture

**Category:** Architectural  
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/event-driven-architecture/)

**Short answer:** Event-Driven Architecture (EDA) propagates state changes as events so consumers react asynchronously and independently. It enables loose coupling, scalability, and audit trails. Trade-off: eventual consistency, debugging difficulty, schema evolution. It hurts when events carry no contract, when synchronous REST is replaced without reason, or when there's no idempotent consumer strategy.

#### Scenario (interview)
**Situation:** Retail platform replatformed to "event-driven"—every REST call now emits 14 events, inventory and shipping disagree during peak, support cannot trace order state, and consumers process messages out of order causing double shipments.
**What they're testing:** Can you design EDA with boundaries, ordering, and observability?
**Model answer:** EDA isn't "Kafka everywhere." I'd define bounded contexts publishing facts after local commit via outbox: `OrderPlaced`, `PaymentAuthorized`—past tense, immutable, versioned Avro/Protobuf schema. Key by `orderId` for partition ordering; consumers idempotent with `(eventId)` store. Sagas coordinate cross-aggregate flows—don't chain fifteen `@EventListener` sync calls pretending it's EDA. Read models via projections; UI reads materialized view tolerating seconds lag with clear UX. Observability: OpenTelemetry trace context in event headers, correlationId from command through all consumers—support portal joins log by orderId. Fix double ship: `ShipmentRequested` consumer checks idempotency + current aggregate state machine illegal transition guard. Schema: compatibility BACKWARD, contract tests in CI. When NOT event-driven: read-your-writes checkout confirmation—synchronous query on command result OK. Metrics: consumer lag, duplicate processing rate, reconciliation diff between inventory projection and DB. Rollout strangler: one bounded context at a time, keep REST read until projection validated.

#### What it is
System components communicate by producing and consuming events representing things that happened. Producers don't target specific consumers; infrastructure routes events to interested services.

#### When to use / when NOT
- **Use:** Multi-team scale, audit/replay needs, heterogeneous consumers, peak decoupling.
- **NOT:** Strong consistency core banking transfer without saga design. Not small CRUD with one team.

#### Java / Spring example

```java
// Outbox publisher after TX commit
@Transactional
void placeOrder(Order cmd) {
    orderRepo.save(order);
    outbox.publish(new OrderPlaced(order.id(), order.total()));
}
```

#### Common mistakes
- Chatty events without schema registry.
- Missing partition key—ordering breaks.
- Consumers with side effects before idempotency check.

#### Follow-up (with answer)
**Q:** Event notification vs event-carried state transfer?
**A:** Notification carries minimal ID—consumers callback for data (coupling, load). Event-carried state transfer embeds data needed—reduces calls but bloats payload and complicates PII. Prefer notification + query API for large graphs; carry state for small immutable facts. Document choice per event type in schema repo.

---

### P057. Event Queue

**Category:** Concurrency  
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/event-queue/)

**Short answer:** Event Queue buffers events between producer and consumer threads, decoupling timing and absorbing bursts. `BlockingQueue`, LMAX Disruptor, and Kafka are scaled variants. Trade-off: latency, ordering guarantees, and overflow policy. It hurts when unbounded queue hides backpressure until GC death, or when consumers assume FIFO across keys that require per-entity ordering.

#### Scenario (interview)
**Situation:** Fraud scoring moved to async queue between API gateway and scorer service. During flash sale, `LinkedBlockingQueue` with Integer.MAX_VALUE capacity grows to 2M events—GC pause kills latency; legitimate orders flagged late after stock gone.
**What they're testing:** Do you size queues and define drop vs backpressure policy?
**Model answer:** Unbounded queue is anti-pattern—it converts overload into memory crisis and stale decisions. I'd use bounded `ArrayBlockingQueue` or Disruptor with configured capacity aligned to scorer throughput × acceptable lag (e.g., 5s at peak RPS). Producers use `offer` with timeout; on full, apply policy: shed load with 429 to client for non-critical paths, or sample keep VIP tenant priority queue. Separate queues per tenant tier if SLA differs. Fraud specifically needs freshness—drop stale events older than 2s with metric `fraud_events_dropped_stale`. Consumer pool sized from profiling, not `availableProcessors()`. For cross-service, Kafka retention replaces in-memory queue with consumer lag alerts. Ordering: partition by `customerId` if sequence matters. Spring: `@Async` queue capacity exposed in config, Actuator metric on queue size. Load test validates bounded behavior—memory flat, latency predictable degradation not cliff. Post-incident: replace unbounded queue, add backpressure to gateway via reactive or semaphore.

#### What it is
Producers enqueue events; consumers dequeue and process asynchronously. The queue smooths burstiness and separates thread lifecycles.

#### When to use / when NOT
- **Use:** Producer faster than consumer, UI event pumps, worker pools, log ingestion buffers.
- **NOT:** When synchronous acknowledgment required before HTTP response without async UX design.

#### Java / Spring example

```java
BlockingQueue<FraudEvent> q = new ArrayBlockingQueue<>(10_000);
void offer(FraudEvent e) {
    if (!q.offer(e, 50, TimeUnit.MILLISECONDS)) meter("dropped").increment();
}
```

#### Common mistakes
- Default unbounded `LinkedBlockingQueue`.
- Single consumer assumed when ordering per key required.
- No monitoring on queue depth—surprise outages.

#### Follow-up (with answer)
**Q:** Event Queue vs message broker?
**A:** In-process queue is fast, volatile, single JVM—great for thread handoff. Broker adds durability, multi-consumer groups, replay—needed cross-service. Don't Kafka a thread pool handoff inside one service unless you need crash recovery of queued work.

---

### P058. Event Sourcing

**Category:** Architectural  
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/event-sourcing/)

**Short answer:** Event Sourcing persists state changes as append-only events; current state is fold of events or snapshot + delta. Enables audit, temporal queries, and replay. Trade-off: storage, projection complexity, deleting PII. It hurts when applied to entire monolith CRUD or when snapshots never compact and replay takes minutes.

#### Scenario (interview)
**Situation:** Fintech ledger team event-sources every account; balance query reads 400k events for whale accounts—statement generation timeout. Auditors love history; customers hate 30s app load. Someone "fixed" by caching balance in Redis without invalidation strategy.
**What they're testing:** Can you operate event sourcing with snapshots and projections?
**Model answer:** Event sourcing stores facts: `MoneyDeposited`, `TransferInitiated`—not current row overwrite. Read path can't replay 400k events synchronously— I'd snapshot every N events or nightly: `AccountSnapshot{version, balance}` plus replay only events after snapshot version. Projections: `AccountBalanceReadModel` updated synchronously in same transaction as append (transactional outbox) or async consumer for UI. Queries hit read model; event store for audit/replay tooling. Compaction/archival: move events older than retention to cold storage with legal hold exceptions. PII: crypto-shred keys on GDPR delete with tombstone events—never pretend immutability exempts GDPR. Whitespace: not every entity sourced—use for ledger, order lifecycle; keep product catalog as CRUD. Tech: Axon, EventStoreDB, or Kafka compacted topics with careful design. Metrics: replay time p99, snapshot lag, projection drift checks comparing balance sum to events fold in batch job. Fix whale account: snapshot at version 380k, replay 20k—sub-second.

#### What it is
Application state is derived from sequence of domain events stored append-only. Commands generate events; aggregates rebuild by applying events in order.

#### When to use / when NOT
- **Use:** Audit-critical domains, financial ledgers, collaborative editing, debugging time travel.
- **NOT:** Simple reference data, report-only tables, teams without ops maturity for projections.

#### Java / Spring example

```java
class Account {
    void apply(MoneyDeposited e) { balance = balance.plus(e.amount()); }
    static Account fromEvents(List<Event> events) {
        var a = new Account();
        events.forEach(a::apply);
        return a;
    }
}
```

#### Common mistakes
- No snapshot strategy—replay death spiral.
- Events as integration payload without domain meaning.
- Updating events in place—breaks audit trust.

#### Follow-up (with answer)
**Q:** Event sourcing vs audit table?
**A:** Audit table logs changes alongside mutable row—simpler, dual write risk. Event sourcing makes events source of truth—stronger replay/consistency model, higher complexity. Choose audit table for compliance log on CRUD; choose sourcing when business logic and integrations rebuild from history.

---

### P059. Execute Around

**Category:** Behavioral  
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/execute-around/)

**Short answer:** Execute Around runs custom code between setup and teardown around a callback—open resource, execute, close/finally. JDBC template, try-with-resources, and AOP `@Around` advice embody it. Trade-off: hiding control flow. It hurts when nested execute-around obscures transaction boundaries or swallows exceptions without rethrow.

#### Scenario (interview)
**Situation:** Developers copy-paste S3 upload boilerplate—assume role, open client, upload, close—across 30 services. Three incidents from leaked clients exhausting file descriptors; one from swallowed `IOException` returning success to user.
**What they're testing:** Can you extract uniform resource lifecycle wrapper?
**Model answer:** Execute Around method accepts callback: `s3Template.withClient(client -> client.putObject(...))` where template handles STS assume role, client build, timeout, and guaranteed `close()` in finally. Same pattern as Spring `JdbcTemplate.query`—framework owns ceremony, business lambda owns core logic. Use try-with-resources inside template for `S3Client`. Never catch `IOException` without rethrow or mapped domain exception—caller must know failure. For transactions, `@Transactional` is execute-around on service method—don't nest manual try/finally TX inside another. Metrics: active client count, FD usage, upload error rate. Rollout: introduce `ObjectStorageTemplate` bean, codemod services one team at a time, ArchUnit ban direct `S3Client.builder()` outside infra module. Testing: inject fake template executing callback with in-memory store. Senior nuance: callback shouldn't escape client reference for async use after method returns—that breaks lifecycle contract.

#### What it is
A method performs pre/post work (acquire, release, logging, TX) and invokes supplied code in the middle. Inverts control so boilerplate stays DRY and consistent.

#### When to use / when NOT
- **Use:** Resource management, consistent logging/metrics around operations, JDBC/HTTP/file patterns.
- **NOT:** One-line operations where wrapper adds no invariant—YAGNI.

#### Java / Spring example

```java
class S3Template {
    <T> T withClient(Function<S3Client, T> work) {
        try (S3Client c = clientFactory.create()) { return work.apply(c); }
    }
}
```

#### Common mistakes
- Callback storing client in field for later async use.
- Catching Exception, logging, returning null—silent failure.
- Deep nesting of multiple execute-around wrappers unreadable.

#### Follow-up (with answer)
**Q:** Execute Around vs Template Method?
**A:** Template Method subclasses override steps in base class hierarchy—compile-time binding. Execute Around passes callback/lambda—composition, no inheritance. Prefer execute-around with functional callback in Java; Template Method when framework owns class extension points (Servlet `service()`).

---

### P060. Extension Objects

**Category:** Structural  
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/extension-objects/)

**Short answer:** Extension Objects attach optional behavior to core objects via separate extension interface map—avoid bloating base class with every variant. Common in plugin systems and document models (style extensions). Trade-off: indirection and discoverability. It hurts when every call routes through `getExtension()` without type safety or when extensions mutate shared core state unsafely.

#### Scenario (interview)
**Situation:** A CMS `ContentNode` base class accumulated 40 optional fields for video, podcast, and legal hold behaviors—subclass explosion and Hibernate JOIN FETCH nightmares. New "interactive quiz" type requires yet another subclass of `Article`, `Page`, `Module`.
**What they're testing:** Can you refactor optional features to extensions without plugin framework overkill?
**Model answer:** Core `ContentNode` keeps identity, title, publish state—stable. Behaviors live in `ContentExtension` keyed by type: `node.extension(VideoExtension.class)` returns optional capabilities—duration, transcoding status. Registry maps extension type to factory per node type compatibility. Persistence: `@ElementCollection Map<String, ExtensionPayload>` JSON or separate `content_extension` table—avoid nullable columns per feature. Adding quiz: new `QuizExtension` class + registry entry, no change to `Article` inheritance. API layer composes DTO from core + requested extensions. Contrast with Decorator—extensions are data-backed optional facets, not wrapping chains. Thread-safety: extensions immutable value objects; mutations via domain commands on aggregate. Migration: extract video fields to `VideoExtension` populated from legacy columns, deprecate columns behind flag. Metrics: Hibernate query width reduced, deploy frequency for new content types up. Pitfall: stringly typed extension keys—use typed interface + class token. Don't use Extension Objects when only two subtypes ever—sealed hierarchy simpler.

#### What it is
Core object exposes mechanism to retrieve extension objects implementing optional interfaces. Features attach dynamically without subclassing core for every combination.

#### When to use / when NOT
- **Use:** Product lines with combinable optional features, plugin architectures, document/editor models.
- **NOT:** Two stable subtypes—use inheritance or composition directly.

#### Java / Spring example

```java
interface ContentNode {
    <T extends ContentExtension> Optional<T> extension(Class<T> type);
}
record VideoExtension(Duration length, URI manifest) implements ContentExtension {}
```

#### Common mistakes
- God extension map without schema versioning.
- Extensions bypass aggregate invariants on core node.
- ClassCastException from wrong extension type—missing Optional handling.

#### Follow-up (with answer)
**Q:** Extension Objects vs Decorator vs Entity-Attribute-Value?
**A:** Decorator wraps behavior dynamically in layers—good for cross-cutting stacks. EAV is DB anti-pattern for queryability. Extension Objects typed optional facets registered per entity—middle ground for CMS product features. Choose EAV never for hot paths; choose extensions when features combine unpredictably but need typed APIs.

---

### P061. Facade

**Category:** Structural  
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/facade/)

**Short answer:** Facade provides a simplified interface to a complex subsystem—one entry point hiding many collaborators. Spring `@Service` orchestration layers often act as facades over repositories and clients. Trade-off: facades become god services if they accumulate domain rules. It hurts when the "facade" is just pass-through with no simplification or when every controller calls subsystem classes directly bypassing it.

#### Scenario (interview)
**Situation:** Mobile BFF team exposes checkout requiring seven internal calls—inventory, pricing, tax, fraud, payment, loyalty, shipping. Latency spikes; each new app version duplicates orchestration with slightly different error handling; partial failures leave orphaned payment holds.
**What they're testing:** Can you design a facade that simplifies without owning all domain logic?
**Model answer:** I'd introduce `CheckoutFacade` (or BFF service) as thin orchestrator—NOT domain rule owner. It coordinates: validate cart via `CartService`, reserve inventory via command, call `PricingEngine`, invoke `PaymentPort` with idempotency key, compensate on failure via saga orchestrator. Facade returns unified `CheckoutResult` DTO mapping internal errors to stable client codes. Parallelize independent calls with structured concurrency or CompletableFuture with deadline; sequential where invariants require—payment after inventory hold. Domain rules stay in respective services; facade only sequences and aggregates. Anti-corruption: facade translates mobile-specific "express checkout" into internal commands without leaking SDK types. Resilience: Resilience4j bulkheads per downstream; single retry policy here not in every client. Testing: contract tests against wiremock downstreams; chaos inject payment timeout verifying hold release. Metrics: end-to-end checkout success, per-step latency attribution. Pitfall: 800-line facade—split by use case (`GuestCheckoutFacade`, `SubscriptionCheckoutFacade`). Facade ≠ monolith service layer dumping ground.

#### What it is
A unified interface wraps multiple subsystem classes, reducing coupling for clients and presenting a coarse-grained operation aligned with user tasks.

#### When to use / when NOT
- **Use:** Complex subsystem graphs, BFF/API aggregation, legacy modernization entry point.
- **NOT:** When client needs only one subsystem call—call directly. Not as excuse to skip domain boundaries.

#### Java / Spring example

```java
@Service
class CheckoutFacade {
    CheckoutResult checkout(CheckoutCommand cmd) {
        var hold = inventory.reserve(cmd.lines());
        try { return payment.charge(cmd.withHold(hold)); }
        catch (Exception e) { inventory.release(hold); throw e; }
    }
}
```

#### Common mistakes
- Facade containing pricing formulas—belongs in domain.
- Leaking all subsystem exceptions raw to API consumer.
- One facade for entire company—unmaintainable god class.

#### Follow-up (with answer)
**Q:** Facade vs API Gateway vs BFF?
**A:** Facade is code-level simplification in one app. API Gateway is edge infrastructure—routing, TLS, rate limits. BFF is facade per client channel optimizing payloads. Gateway shouldn't orchestrate seven domain calls—that's BFF/facade service behind gateway. Layer responsibilities: gateway secures/routes, BFF aggregates, domain services decide rules.

---

### P062. Factory

**Category:** Creational  
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/factory/)

**Short answer:** Factory encapsulates object creation behind an interface or method, hiding concrete types and construction steps. Spring `@Bean` methods and `Supplier` patterns are factories. Trade-off: indirection when only one implementation exists. It hurts when factory switches on string config grow to 40 branches without strategy map or when tests forget to register test double in factory.

#### Scenario (interview)
**Situation:** Multi-region deployment needs different `BlobStorageClient` implementations—Azure Blob in EU, S3 in US, filesystem in dev. Developers scatter `if (region.equals("eu"))` across upload services; one path still writes prod data to dev filesystem after misconfigured property.
**What they're testing:** Can you centralize creation with environment-safe wiring?
**Model answer:** Single `StorageClientFactory` or Spring `@Configuration` `@Bean` method selects implementation from `RegionProperties` validated at startup—fail if prod profile allows filesystem. Factory returns `StorageClient` interface; callers unaware of Azure vs S3. Use `@Profile("prod-eu")` config classes when wiring differs substantially, or strategy map `Map<Region, StorageClient>` for clarity. Validate beans with `@PostConstruct` asserting no filesystem in prod. Testing: `@TestConfiguration` supplies in-memory factory without touching real cloud. Observability: log chosen backend at info once per pod start, metric tag `storage=azure|s3`. Migration: extract creation from services to factory, ArchUnit rule `noImport(com.azure)` outside infra module. Factory Method vs Simple Factory: here static/simple factory method or bean method suffices—no subclass extension needed. Document property matrix in runbook. Incident prevention beats cleverness—misconfig should fail fast at context refresh not first customer upload.

#### What it is
Dedicated creator (class/method) instantiates products implementing common interface, centralizing `new` and conditional logic away from business code.

#### When to use / when NOT
- **Use:** Conditional implementations, complex init, hiding third-party constructors.
- **NOT:** Single implementation forever—inject concrete if YAGNI. Not for every DTO—use `new`.

#### Java / Spring example

```java
@Configuration
class StorageConfig {
    @Bean StorageClient storage(RegionProperties p) {
        return switch (p.backend()) {
            case AZURE -> new AzureBlobClient(p.connection());
            case S3 -> new S3Client(p.bucket());
            case LOCAL -> new LocalFsClient(p.path());
        };
    }
}
```

#### Common mistakes
- Factory returning concrete types to domain layer.
- Silent default to unsafe dev implementation in prod.
- Factory doing business validation beyond construction readiness.

#### Follow-up (with answer)
**Q:** Factory vs Abstract Factory in Spring?
**A:** Simple factory picks one implementation from config. Abstract Factory creates families of related objects (e.g., Win UI button + checkbox together). Spring rarely needs classic Abstract Factory—multiple `@Configuration` profile classes achieve family swap. Use Abstract Factory when products must stay consistent as a set per tenant skin.

---

### P063. Factory Kit

**Category:** Creational  
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/factory-kit/)

**Short answer:** Factory Kit pre-registers prototype instances or builders keyed by identifier, producing new objects via clone/build without switching on types at runtime. Useful for plugin catalogs and weapon/item registries in configurable systems. Trade-off: registration lifecycle and thread-safe maps. It hurts when prototypes are mutable and cloned objects share state, causing cross-tenant leakage.

#### Scenario (interview)
**Situation:** A low-code workflow engine lets consultants register 200 step templates—email, HTTP call, approval—in JSON. Runtime `StepFactory` uses giant switch; adding custom client steps requires core deploy. Consultants duplicate step configs because factory can't register extensions dynamically.
**What they're testing:** Can you design extensible registration without classpath scanning chaos?
**Model answer:** Factory Kit: each step type registers a prototype or `StepBuilder` in kit at startup—`kit.register("http", HttpStepPrototype)`. `kit.create("http", config)` clones prototype and applies config immutably. Client extensions ship as Spring `@Component` implementing `StepRegistrar` adding to kit on context refresh—no core switch edit. Prototypes must be immutable templates; per-instance state applied in builder `configure(JsonNode)`. Thread-safe `ConcurrentHashMap` for registry; validate duplicate IDs fail startup. Contrast Abstract Factory—kit is dynamic catalog not compile-time family. Security: whitelist allowed step types per tenant; sandbox HTTP steps network policy. Testing: register fake step in test kit. Migration from switch: move each case to registrar bean, integration test parity on golden workflows. Pitfall: shallow clone of mutable lists—use copy constructor. Metrics: plugin registration count, step instantiation errors. Senior angle: Factory Kit enables product extensibility; govern with semver on step schema.

#### What it is
Registry maps keys to prototype objects or factories; `create(key)` clones or builds configured instance. Combines prototype registration with factory access.

#### When to use / when NOT
- **Use:** Plugin catalogs, game entities, configurable pipelines, extensible parsers.
- **NOT:** Two implementations from config—simple Factory enough.

#### Java / Spring example

```java
class StepKit {
    private final Map<String, Supplier<WorkflowStep>> registry = new ConcurrentHashMap<>();
    void register(String id, Supplier<WorkflowStep> proto) { registry.put(id, proto); }
    WorkflowStep create(String id) { return registry.get(id).get(); }
}
```

#### Common mistakes
- Mutable prototypes shared across created instances.
- No validation on unknown keys—NPE in prod.
- Registration order dependencies hidden across beans.

#### Follow-up (with answer)
**Q:** Factory Kit vs ServiceLoader vs Spring `@Autowired List`?
**A:** ServiceLoader discovers JDK META-INF plugins—classpath static. Spring autowires all `StepRegistrar` beans—idiomatic in Boot apps with lifecycle and conditional beans. Factory Kit adds keyed lookup and prototype cloning semantics explicit in API. Combine: registrars populate kit bean at startup.

---

### P064. Factory Method

**Category:** Creational  
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/factory-method/)

**Short answer:** Factory Method lets subclass or strategy decide which concrete product to instantiate via overridable creator method. It decouples client code from concrete classes. Trade-off: extra type hierarchy. It hurts when every variation gets a subclass instead of a strategy map, or when static factory method hides behind misleading name `getInstance()` returning new object each call.

#### Scenario (interview)
**Situation:** Report export module supports PDF, XLSX, and CSV. Original design: `ReportExporter exporter = new PdfExporter()` in controller. Product asks for customer-branded PDF with watermark per tenant—team adds `TenantPdfExporter extends PdfExporter` tree depth four.
**What they're testing:** Can you apply Factory Method with composition not inheritance explosion?
**Model answer:** Define `ReportExporter` interface and `ReportExporterFactory.create(Format, TenantTheme)`—creator method may delegate to strategy map rather than literal subclass override per GoF, idiomatic in Java. `PdfExporter`, `XlsxExporter` implement interface; watermark decorator wraps PDF for branded tenants inside factory method, not subclass chain. Spring: `@Bean ReportExporterFactory` injecting list of exporters keyed by format. Open/closed: add `ParquetExporter` by new class + register, no change to controller. Controller depends on factory interface only. Testing: mock factory returns fake exporter verifying controller passes correct command. Contrast Simple Factory—Factory Method emphasizes extensibility point subclass/framework overrides (`TemplateMethod` export pipeline calls abstract `createWriter()`). Avoid `new` in domain services—inject factory when format chosen at runtime from user input. Metrics: export failure by format, time to add new format (organizational metric). If only one format ever—skip pattern; here three formats + tenant variants justify factory method creator.

#### What it is
Base class or framework defines method that calls abstract/virtual creator to obtain product; subclasses or strategies supply concrete product type without changing client algorithm structure.

#### When to use / when NOT
- **Use:** Framework extension points, format/transport selection, plugin creation hooks.
- **NOT:** Single product, known at compile time—direct injection.

#### Java / Spring example

```java
interface ReportExporterFactory {
    ReportExporter create(ExportFormat format, TenantId tenant);
}
class DefaultReportExporterFactory implements ReportExporterFactory {
    public ReportExporter create(ExportFormat f, TenantId t) {
        return switch (f) {
            case PDF -> new BrandedPdfExporter(themeOf(t));
            case CSV -> new CsvExporter();
        };
    }
}
```

#### Common mistakes
- Subclass per tenant instead of strategy parameter.
- Factory method returning new instance while name implies singleton.
- Creator method doing heavy I/O at every call—cache templates.

#### Follow-up (with answer)
**Q:** Factory Method vs Abstract Factory vs Builder for reports?
**A:** Factory Method selects which exporter implements same interface. Abstract Factory would also produce matching `ReportMetadataWriter` family per vendor stack—overkill here. Builder assembles one complex report object field-by-field—not selection among implementations. Pick Factory Method when variation is which implementation; Builder when one PDF with many optional sections.

---

### P065. Fallback

**Category:** Behavioral  
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/fallback/)

**Short answer:** Fallback provides alternate behavior when primary path fails or is unavailable—cached stale data, default provider, degraded feature. Resilience4j `@Fallback` and Hystrix commands popularized it. Trade-off: masking root cause if fallback hides outages; stale data risk. It hurts when fallback silently returns zeros in financial contexts or when secondary path never tested until primary dies.

#### Scenario (interview)
**Situation:** Product detail page calls recommendation service; on timeout returns empty list—conversion drops 8% but no alerts fire because HTTP 200. Primary outage during holiday goes unnoticed for six hours; fallback cache expired empty.
**What they're testing:** Can you design observable, tested degradation?
**Model answer:** Fallback must be explicit tier: (1) primary live recommendations, (2) cached last-good personalized list with `X-Degraded: cache` header, (3) static category bestsellers, (4) fail visible if all fail for premium SLA tenants. Implement with Resilience4j `@CircuitBreaker` + `@Fallback` method `recommendFallback()` reading Caffeine cache populated on successful primary calls—not empty list masquerading as success. Metrics: `recommendations.fallback.tier` counter, alert if tier≠primary >5min. Test fallback in CI: WireMock primary 503, assert secondary path returns non-empty and header set. Business sign-off on stale duration—finance may forbid stale prices but marketing accepts 1h old recs. Don't fallback across tenant boundaries—cache key includes tenantId. Document runbook: primary fix vs intentional degrade switch. For payments, no silent fallback to alternate gateway without idempotency audit—different pattern (fail or queued retry). Senior point: fallback is product decision with SLO, not catch(Exception) return null.

#### What it is
When primary operation fails, predefined secondary logic executes—alternative service, cached value, simplified response—maintaining partial functionality.

#### When to use / when NOT
- **Use:** Non-critical enrichments, read-mostly data with acceptable staleness, multi-provider redundancy.
- **NOT:** Monetary authorization, inventory deduction, safety checks—fail closed or queue.

#### Java / Spring example

```java
@CircuitBreaker(name = "recs", fallbackMethod = "cachedRecs")
List<Item> recommend(UserId u) { return recClient.fetch(u); }
List<Item> cachedRecs(UserId u, Throwable t) { return cache.get(u).orElse(BESTSELLERS); }
```

#### Common mistakes
- Fallback returning success with empty/wrong data—no alert.
- Untested fallback path rotting over years.
- Fallback calling same broken dependency differently named.

#### Follow-up (with answer)
**Q:** Fallback vs Retry vs Circuit Breaker?
**A:** Retry handles transient blips on same dependency. Circuit breaker stops hammering failing dependency and fast-fails or routes to fallback. Fallback is alternate behavior when primary fails or breaker open. Compose: retry twice, then breaker opens, then fallback cache; alert on breaker state.

---

### P066. Fan-Out/Fan-In

**Category:** Concurrency  
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/fan-out-fan-in/)

**Short answer:** Fan-Out/Fan-In splits work to parallel workers (fan-out) then aggregates results (fan-in). CompletableFuture `allOf`, parallel streams, and map-reduce pipelines use it. Trade-off: coordination overhead and partial failure aggregation. It hurts when fan-out to 500 threads on 8 cores thrashes, or when fan-in blocks forever waiting for one stuck shard.

#### Scenario (interview)
**Situation:** Order pricing must fetch tax, FX, promo, and shipping quotes from four providers for international checkout. Sequential calls sum to 900ms p99; team parallelized with raw `new Thread` per request—thread count exploded under load, fan-in occasionally NPE on partial results.
**What they're testing:** Can you orchestrate bounded parallel fan-out with timeout and merge?
**Model answer:** Fan-out: submit four tasks to dedicated `ExecutorService` (fixed pool sized to provider count + headroom), each wrapped with timeout and circuit breaker. Use `CompletableFuture.supplyAsync(..., pool)` capturing MDC context. Fan-in: `CompletableFuture.allOf(...).orTimeout(800ms, MILLISECONDS)` then combine with explicit merge function building `PricingBundle`—handle partial: if tax fails, fail checkout (hard dependency); if promo fails, proceed with zero discount and flag degraded. Never bare `join()` without timeout on user thread. Avoid `parallelStream()` for I/O—ForkJoinPool common pool wrong for blocking calls. Bulkhead per provider thread limits. Metrics: per-provider latency, fan-in timeout rate, thread pool saturation. Testing: chaos one provider slow, assert fan-in completes within SLA with correct degradation policy. For larger fan-out (100 SKUs price lookup), batch API if provider supports—fan-out N HTTP calls only when necessary. Azure/Spring: `@Async` only with named executor, not default. Document merge associativity for testability.

#### What it is
Divide input into parallel subtasks processed independently, then collect and merge outputs into unified result. Classic divide-and-conquer at request scope.

#### When to use / when NOT
- **Use:** Independent I/O calls, batch enrichment, map-reduce style aggregation.
- **NOT:** Strict sequential transactions depending on prior step outcome without compensation design.

#### Java / Spring example

```java
var tax = supplyAsync(() -> taxClient.quote(cart), pool);
var fx  = supplyAsync(() -> fxClient.rate(cart), pool);
PricingBundle fanIn = allOf(tax, fx).orTimeout(800, MS)
    .thenApply(v -> merge(tax.join(), fx.join())).join();
```

#### Common mistakes
- `parallelStream()` for blocking HTTP.
- No timeout on fan-in— hung request.
- Mutable shared accumulator during fan-in without synchronization.

#### Follow-up (with answer)
**Q:** Fan-out/fan-in vs scatter-gather in messaging?
**A:** In-process fan-out uses threads/futures—low latency, same JVM failure domain. Scatter-gather via Kafka topics scales cross-service but adds ms-s latency and ops complexity. Use in-process for checkout enrichment; use messaging when workers scale independently or work survives pod death.

---

### P067. Feature Toggle

**Category:** Architectural  
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/feature-toggle/)

**Short answer:** Feature Toggle (feature flags) switches behavior at runtime without deploy—release, experiment, ops kill-switch, permission. LaunchDarkly, Unleash, and Spring `@ConditionalOnProperty` variants apply. Trade-off: combinatorial test matrix and stale flags becoming permanent ifs. It hurts when flags bypass security checks long after launch or when ten nested toggles make behavior undebuggable.

#### Scenario (interview)
**Situation:** `if (featureFlags.isNewCheckoutEnabled(tenant))` scattered in 47 files; flag left on for beta tenants 18 months; incident when old path untested breaks rollback; GDPR issue when experimental analytics flag enabled for EU without consent check.
**What they're testing:** Can you govern flags with lifecycle and observability?
**Model answer:** Centralize toggle evaluation in small `FeaturePolicy` service—not raw flag client in controllers. Flag types: release (short-lived), ops kill-switch, permission (tenant entitlements), experiment (with consent). Lifecycle ADR: owner, creation date, removal ticket, max TTL 90 days for release flags. CI runs both paths for critical flags or uses contract tests matrix. Unleash/LaunchDarkly with targeting rules; log evaluation decision at debug with flag version in structured logs for support. Rollback during incident: ops toggle off new checkout without redeploy—verify old path in staging weekly via synthetic test. Remove dead code when flag permanent—merge paths, delete flag to avoid dual maintenance. EU analytics experiment gated on consent record lookup, not boolean alone. Metrics: flag evaluation count, error rate split by variant, count of flags older than SLA. ArchUnit fail build on direct SDK import outside policy module. Senior message: flags are deployment tool, not design substitute—don't flag-architect two divergent systems forever.

#### What it is
Runtime configuration selects code paths or features without redeployment. Evaluation uses context—user, tenant, region, percentage rollout.

#### When to use / when NOT
- **Use:** Progressive rollout, A/B tests, emergency disable, tenant entitlements.
- **NOT:** Long-term configuration (use config service). Not for secrets or security roles alone.

#### Java / Spring example

```java
@Component
class FeaturePolicy {
    boolean newCheckout(TenantId t) {
        return flags.isEnabled("new-checkout", context(t));
    }
}
```

#### Common mistakes
- Permanent flags becoming alternate architectures.
- Client-side only gating for security features.
- No metrics comparing variant error rates.

#### Follow-up (with answer)
**Q:** Feature toggle vs `@Profile` vs configuration property?
**A:** `@Profile` selects beans at startup—requires redeploy/restart. Properties change with refresh scope but coarse. Feature toggles evaluate per request with targeting and instant flip—runtime ops. Use profile for environment differences (dev/prod), toggles for gradual user-facing rollout within same prod deployment.

---

### P068. Filterer

**Category:** Behavioral  
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/filterer/)

**Short answer:** Filterer applies chain or pipeline of predicates to screen objects from collection or stream—composable `and`/`or` filters. Java Stream `filter`, Spring `HandlerFilter`, and security matcher chains relate. Trade-off: performance if filters re-query DB each step. It hurts when filter order causes full table scan repeatedly or when business rules duplicated across HTTP layer and repository.

#### Scenario (interview)
**Situation:** Admin product search accepts 12 optional criteria—category, price band, stock, region legality, tenant visibility. Each criterion implemented as separate SQL fragment concatenated in controller; SQL injection scare and wrong results when filters applied in wrong order full-scanning 10M rows.
**What they're testing:** Can you compose filters safely and push predicates to database?
**Model answer:** Model `ProductFilter` as composable predicate interface with `and`, `or`, `not`—like Stream but domain typed. `CatalogService.search(ProductFilter f, Pageable p)` translates filter AST to JPA Specification or Criteria API single query—one DB round trip. Filters: `InCategory`, `PriceBetween`, `VisibleToTenant` each implement `toSpec(Specification<Product>)`. Order optimization: most selective filter first via planner hints or mandatory indexed predicate on tenantId always applied. Never string-concat SQL in controller. Reuse same filter objects in export job and REST API—DRY rules. Security: tenant visibility filter applied in service layer mandatorily, not optional query param. Testing: unit test each filter spec; integration test combination parity. Metrics: slow query log on search, index usage. Contrast Chain of Responsibility—filterer focuses on inclusion/exclusion set, not passing request along handlers. For in-memory collections, Stream pipeline fine; for DB, push down predicates.

#### What it is
Objects or lambdas test elements against criteria; composite filters combine criteria declaratively to produce filtered subset.

#### When to use / when NOT
- **Use:** Search, authorization scopes, validation pipelines, stream processing.
- **NOT:** Complex joins better expressed as one query by query author—don't over-abstract.

#### Java / Spring example

```java
ProductFilter f = new InCategory("electronics")
    .and(new PriceBetween(min, max))
    .and(new VisibleToTenant(tenantId));
return repo.findAll(f.toSpec(), page);
```

#### Common mistakes
- Filtering in memory after fetching 100k DB rows.
- Optional tenant filter—cross-tenant data leak.
- Non-composable duplicate if statements per endpoint.

#### Follow-up (with answer)
**Q:** Filterer vs Specification pattern vs Query Object?
**A:** Specification is typed composable predicate translating to SQL—Filterer pattern name aligns with composable criteria objects. Query Object encapsulates whole query as object—better for fixed reports. Use composable Specification for dynamic admin search; Query Object for named complex report queries.

---

### P069. Fluent Interface

**Category:** Behavioral  
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/fluent-interface/)

**Short answer:** Fluent Interface chains method calls readable as prose—each method returns `this` or next builder step. Stream API, QueryDSL, and test fixtures use fluency. Trade-off: discoverability in IDE vs readable stack traces. It hurts when fluent chain hides side effects, mandatory steps, or when invalid states are reachable mid-chain.

#### Scenario (interview)
**Situation:** Test data setup uses `OrderBuilder.customer(x).line(y).ship(z).build()` but teams can call `build()` without payment method—tests pass while production NPEs. Another team built fluent HTTP client that executes on every chained method causing duplicate POSTs in retry logic.
**What they're testing:** Do you know typed builders and stage interfaces for fluency with safety?
**Model answer:** Fluent doesn't mean one mutable builder class—use staged interfaces: `OrderDraft` → after `withCustomer()` returns `OrderLinesStage` requiring `addLine()` before `CheckoutStage` exposes `build()`. Compiler enforces order; fluency preserved. For HTTP client, separate `RequestSpec` (fluent config) from `execute()` terminal—no network I/O until terminal method. Immutability: each fluent step returns new instance if multi-threaded test parallelism. Production APIs: public REST stays JSON—not fluent. Internal use: migration scripts, test fixtures, query builders (QueryDSL). Document side-effect-free chaining in Javadoc. Anti-pattern: `SecurityContext.enableAdmin().disableAudit().run()`—dangerous fluent power without scope block. Prefer `try (AdminContext c = AdminContext.open())` for auto-close. Metrics N/A for tests; for query builder log slow generated SQL. Review fluent APIs in PR for terminal method clarity and invalid state prevention using types not runtime checks.

#### What it is
API design where methods return receiver or next builder type enabling chained calls reading like natural language sentences.

#### When to use / when NOT
- **Use:** Test builders, DSLs, query construction, configuration with many optional params.
- **NOT:** Simple two-parameter methods. Not public domain entities—behavior belongs in methods not chain gimmicks.

#### Java / Spring example

```java
Order order = Order.builder()
    .customer(cust)
    .line(line1)
    .paymentMethod(PM.CARD)
    .build();
```

#### Common mistakes
- Fluent builder missing required field validation until runtime.
- Side effects in non-terminal chain methods.
- Returning same mutable this in concurrent context.

#### Follow-up (with answer)
**Q:** Fluent Interface vs Builder pattern?
**A:** Builder often uses fluent chaining but focuses on constructing complex object stepwise with `build()` validation. Fluent Interface is broader API style—including query DSLs not necessarily "builders." All good builders are fluent; not all fluent APIs are safe builders—add staged types for safety.

---

### P070. Flux

**Category:** Architectural  
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/flux/)

**Short answer:** Flux unidirectional data flow: actions → dispatcher → stores → views. State changes flow one direction; views dispatch actions, never mutate store directly. Frontend Redux follows Flux; backend analogs are event-sourced projections with command bus. Trade-off: boilerplate and tracing action chains. It hurts when "Flux" backend duplicates frontend store naively without concurrency model.

#### Scenario (interview)
**Situation:** SPA inventory dashboard shows stale counts—developers mutate shared singleton `InventoryStore` from websocket handler and REST poll simultaneously; race fixes with synchronized blocks cause UI freezes; no single source of truth for "who changed quantity."
**What they're testing:** Can you explain Flux discipline and backend separation?
**Model answer:** Flux mandates: View dispatches `ACTION_RESERVE_STOCK` → Dispatcher routes to Store reducer → Store emits new immutable state → View subscribes re-render. Fix frontend: Redux/Zustand with single reducer handling all inventory mutations; websocket messages translated to actions, never direct store field assign. Backend isn't Flux store—API accepts commands, persists, publishes events; SPA reduces events to state. Error: mirroring entire domain in client Flux store—client holds view model only, server authoritative. For Java backend parallel, consider command bus + projection read model (CQRS-lite), not global mutable singleton. Testing: action/reducer unit tests pure functions; integration test websocket → action → state path. Performance: selector memoization prevents re-render storms. If team confused Flux with Observer—Observer allows many directions; Flux enforces one-way loop preventing spaghetti sync. Document action schema versioning. Incident retro: direct mutation bypassed dispatcher—lint rule forbid `store.quantity =`. Senior scope: apply Flux on client state complexity; server uses domain model + events.

#### What it is
Architectural pattern for UI state: actions describe intent, dispatcher centralizes routing, stores hold state and apply reducers, views render and dispatch new actions.

#### When to use / when NOT
- **Use:** Complex interactive UI with shared mutable view state, time-travel debugging needs.
- **NOT:** Simple forms with server round-trip HTML. Not server-side substitute for domain model.

#### Java / Spring example

```java
// Backend dispatches domain events; frontend Flux reduces them
@PostMapping("/commands/reserve")
void reserve(@RequestBody ReserveCmd cmd) {
    inventoryService.reserve(cmd); // authoritative
}
```

#### Common mistakes
- Mutating store outside reducer/dispatcher.
- Duplicating authoritative business rules only in client reducer.
- Mega-reducer god switch without slice reducers.

#### Follow-up (with answer)
**Q:** Flux vs MVC vs MVVM?
**A:** MVC controller mediates; view can bind model various ways—bidirectional risk. MVVM two-way binding convenient but hard to trace updates. Flux strict unidirectional—predictable debugging at cost of ceremony. Pick Flux/Redux when shared client state complexity high; MVC/MVVM fine for simpler screens.

---

### P071. Flyweight

**Category:** Structural  
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/flyweight/)

**Short answer:** Flyweight shares intrinsic immutable state among many objects to save memory—extrinsic state passed at use time. `Integer.valueOf` cache and string interning illustrate it. Trade-off: complexity and thread-safe pool management. It hurts when attempting to flyweight mutable objects or when pool lookup cost exceeds memory saved for small catalogs.

#### Scenario (interview)
**Situation:** GIS rendering service models 4 million map tiles each carrying duplicate `TerrainType` metadata objects—heap OOM on 8GB pods. Junior dev clones terrain enum per tile "for isolation"; GC thrashes during pan/zoom.
**What they're testing:** Can you separate intrinsic/extrinsic state and pool safely?
**Model answer:** Identify intrinsic state: `TerrainType` color, elevation rules, render shader id—immutable, shared. Extrinsic: tile coordinates, zoom level, selection highlight—per tile. `TerrainFlyweightFactory.get(TerrainKind)` returns cached instance from concurrent map; tiles store reference + extrinsic coords only. Use enum for finite terrain kinds—simplest flyweight in Java. If dynamic catalog, pool with size bound and miss creating new immutable flyweight interned. Don't flyweight mutable `UserPreferences` on tile—wrong split. Measure: heap drop from 6GB to 400MB, GC pause down. Thread-safety: flyweights immutable after publish; pool `computeIfAbsent`. Watch identity: compare flyweight reference equality in debug. Alternative: store terrain kind id byte per tile, resolve metadata at render from array table—Flyweight intent same. Not worth flyweight for 20 country codes—enum sufficient. Metrics: heap per session, factory cache hit rate. Spring: `@Component` factory bean holding pools, not prototype scope abuse.

#### What it is
Share common intrinsic state among many fine-grained objects via factory pool; extrinsic context supplied by client at operation time.

#### When to use / when NOT
- **Use:** Massive object counts with repeated metadata, graphics glyphs, repeated config tokens.
- **NOT:** Few instances or mostly unique state—normal objects fine.

#### Java / Spring example

```java
enum TerrainType { WATER, FOREST, URBAN; /* intrinsic render data */ }
record Tile(int x, int y, TerrainType terrain) {} // terrain shared enum
```

#### Common mistakes
- Putting mutable extrinsic state inside flyweight.
- Unbounded pool without eviction for dynamic keys—memory leak.
- Synchronizing entire render path on factory lookup.

#### Follow-up (with answer)
**Q:** Flyweight vs Object Pool?
**A:** Flyweight shares immutable intrinsic state many times—same instance many contexts. Object pool reuses mutable expensive objects (connections, threads) returned after use. Flyweight never "returned"; pool objects reset between borrows. Don't pool short-lived DTOs—pool connections.

---

### P072. Fork/Join

**Category:** Concurrency  
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/fork-join/)

**Short answer:** Fork/Join recursively splits tasks into subtasks executed on work-stealing pool, joining results. Java `ForkJoinPool` and `parallelStream` use it for CPU-bound divide-and-conquer. Trade-off: task granularity—too small adds overhead, too large loses parallelism. It hurts when blocking I/O runs on common pool starving `parallelStream` elsewhere.

#### Scenario (interview)
**Situation:** Batch job aggregates daily risk vectors for 50k portfolios using `parallelStream()` on REST fetch per portfolio—common ForkJoinPool starved, other services' CPU tasks timeout, job wall time worse than sequential.
**What they're testing:** Do you match pool type to workload and size tasks correctly?
**Model answer:** Fork/Join excels CPU-bound recursive work—matrix math, in-memory aggregation trees—not blocking HTTP. Move I/O to dedicated `ExecutorService` with async fan-out (pattern 066) or batch API. For CPU aggregation after data loaded: custom `ForkJoinPool(16)` isolated from common pool, `RecursiveTask` splitting portfolio list until chunk ~200 items, join sums—don't use default common pool in library code. Threshold tuning: if split cost > work, stop splitting. `parallelStream()` only on pure CPU in same codebase aware of pool contention—or replace with explicit pool.submit. Metrics: pool queue length, stolen task count, speedup vs sequential. Spring Batch: partition step with local threading model clearer for ops. If data already in memory array, Fork/Join sum doubles throughput on 16 core—validated in JFR. Document: never block inside ForkJoinTask. Alternative: virtual threads for I/O aggregation Java 21—different pattern. Fix incident by separating I/O executor from CPU join stage pipeline.

#### What it is
Work-stealing framework recursively decomposes task into subtasks forked on pool threads; join combines partial results upward.

#### When to use / when NOT
- **Use:** CPU-heavy divide-conquer, large in-memory scans, parallel merge sort.
- **NOT:** Blocking network/disk I/O on ForkJoinPool.commonPool().

#### Java / Spring example

```java
ForkJoinPool pool = new ForkJoinPool(16);
long total = pool.invoke(new SumPortfoliosTask(portfolios, 0, n));
```

#### Common mistakes
- `parallelStream()` for blocking calls.
- Tiny tasks—scheduling overhead dominates.
- Shared mutable accumulator in join without proper combining.

#### Follow-up (with answer)
**Q:** Fork/Join vs virtual threads for batch?
**A:** Virtual threads excel massive blocking I/O concurrency cheaply. Fork/Join excels CPU parallel decomposition with work stealing. Hybrid pipeline: virtual threads fetch data, single ForkJoinPool aggregates in memory—best of both for mixed batch jobs.

---

### P073. Front Controller

**Category:** Architectural  
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/front-controller/)

**Short answer:** Front Controller centralizes request handling—routing, auth, logging—before delegating to views or commands. Spring `DispatcherServlet`, JAX-RS application class, and MVC `@Controller` layer embody it. Trade-off: controller bloat if business logic creeps in. It hurts when `@Controller` methods contain SQL and transaction rules bypassing service layer.

#### Scenario (interview)
**Situation:** Legacy servlet app has 40 servlets each duplicating auth, locale, and CSRF checks; security patch updated 12 servlets missing 4—CVE reopened. Migration to Spring MVC stalled because team puts business logic in `@RestController` 300 lines each.
**What they're testing:** Can you structure front controller with filters and thin controllers?
**Model answer:** Front Controller = `DispatcherServlet` + filter chain + `@Controller` mapping. Centralize cross-cutting in `OncePerRequestFilter` auth, MDC, CSRF, tenant resolution—never per servlet. Controllers only: validate input DTO, call application service, map response—max ~30 lines. `@ControllerAdvice` handles errors uniformly. Routing via `@RequestMapping` replaces servlet map in web.xml. Migration strangler: wrap legacy servlets behind controller delegating temporarily. Security patch once in filter fixes all routes. Contrast with Page Controller per view—Front Controller one entry dispatches many actions. For REST API, OpenAPI documents controller surface; business in `@Service`. Metrics: filter latency, controller vs service time in tracing spans. Review PRs rejecting repository injection in controllers. Spring Security filter chain order documented—auth before tenant filter. Senior mapping: Front Controller is why Spring web apps aren't 200 servlets—leverage it instead of fighting with fat controllers.

#### What it is
Single handler receives all requests, applies common processing, dispatches to appropriate downstream handler or view based on route/action.

#### When to use / when NOT
- **Use:** Web MVC frameworks, unified auth/logging/routing, multi-action applications.
- **NOT:** Single-endpoint microservice needing only one route—still use controller but pattern overhead minimal discussion.

#### Java / Spring example

```java
@RestController
@RequestMapping("/orders")
class OrderController {
    @PostMapping OrderDto create(@Valid CreateOrder cmd) {
        return mapper.toDto(orderService.create(cmd));
    }
}
```

#### Common mistakes
- Business logic and transactions in controller.
- Bypassing filter chain for "internal" endpoints exposed publicly.
- Per-endpoint copy-paste validation instead of `@Valid` + advice.

#### Follow-up (with answer)
**Q:** Front Controller vs Filter vs Interceptor?
**A:** Filter is servlet spec outermost wrapping dispatcher—auth, encoding. HandlerInterceptor runs inside Spring MVC around controller—model prep, handler timing. Front Controller orchestrates dispatch; filters/interceptors are mechanisms implementing cross-cutting before/after controller. Order matters for security—document filter chain.

---

### P074. Function Composition

**Category:** Behavioral  
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/function-composition/)

**Short answer:** Function Composition builds complex behavior by combining small pure functions—output of one feeds next. Java `Function.compose/andThen`, streams, and reactive operators apply it. Trade-off: debugging stack depth and opaque lambda names. It hurts when composed pipeline hides side effects or when one step throws without contextual error mapping.

#### Scenario (interview)
**Situation:** Pricing pipeline refactored to "functional style": `validate.andThen(enrich).andThen(calculate).andThen(format)` but production errors show `NullPointerException` at `lambda$step3$7` with no SKU context; junior added DB call inside `enrich` breaking purity and testability.
**What they're testing:** Can you compose functions with observability and clear boundaries?
**Model answer:** Keep steps pure where possible: `Function<PricingContext, PricingContext>` immutable context carrying SKU, errors accumulate in context instead of throws for business failures. Name functions: `Function<PricingContext, PricingContext> enrichTax = ctx -> ...`—not anonymous lambdas in long chain. Compose with `enrichTax.andThen(applyPromo).andThen(finalize)`; wrap pipeline with `composeWithTracing(stepName)` logging input hash and duration per step. Side effects (DB rate fetch) isolated in explicit port called from impure boundary function, not hidden in "pure" step—tests use stub port. Error reporting: context records `List<PricingIssue>`; terminal step maps to API response. Contrast with Chain of Responsibility—composition is functional chaining without linked objects. Use streams for collection pipelines; function composition for single object transformation stages. Metrics: per-step timing in Micrometer via decorated functions. Rollback readability: pipeline builder class documents order statically. Senior take: composition reduces branching if disciplined; without naming and tracing, worse than clear sequential code.

#### What it is
Combine functions f and g into h where h(x) = g(f(x)). Enables reusable pipeline stages without subclassing.

#### When to use / when NOT
- **Use:** Data transformation pipelines, validation chains, FP-friendly domains.
- **NOT:** Heavy side-effect workflows better as explicit service methods with TX boundaries.

#### Java / Spring example

```java
Function<Order, Order> pipeline =
    validate.andThen(enrichTax).andThen(applyPromo);
Order priced = pipeline.apply(order);
```

#### Common mistakes
- Hidden I/O in "pure" pipeline steps.
- Anonymous lambdas in prod stack traces.
- Composing without short-circuit on first validation error.

#### Follow-up (with answer)
**Q:** Function composition vs Chain of Responsibility?
**A:** Chain passes request object along linked handlers—OOP, dynamic reorder. Function composition static pipeline of transformations—predictable order, easier testing with pure functions. Use chain when handlers optional/runtime ordered; use composition for fixed transformation pipeline on immutable context.

---

### P075. Game Loop

**Category:** Performance  
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/game-loop/)

**Short answer:** Game Loop repeatedly processes input, updates state, and renders—fixed or variable timestep. Backend analogs: scheduled tick processors, simulation engines, and market data refresh cycles. Trade-off: CPU use when idle vs lag when tick overloaded. It hurts when loop runs unbounded work per tick causing spiral of death, or when fixed timestep not compensated for slow frames.

#### Scenario (interview)
**Situation:** Trading sim engine uses `while(true)` loop on server thread processing market ticks, order matching, and risk recalc—under load tick duration exceeds interval, queue backs up, simulated time diverges from wall clock, orders execute in wrong sequence.
**What they're testing:** Can you design fixed timestep loop with catch-up limits?
**Model answer:** Classic game loop phases per tick: poll events → update simulation → publish snapshot. Use fixed dt (e.g., 50ms sim step) with accumulator: measure real elapsed, while accumulator >= dt and catch-up ticks < MAX_CATCH_UP, run update(dt), subtract dt. Exceed MAX_CATCH_UP: drop or merge ticks with metric `sim_ticks_dropped`—better than unbounded catch-up freeze. Separate I/O thread feeds event queue; loop thread single-writer on sim state—aligns Active Object. Never block loop on HTTP—async feeds. Spring: `@Scheduled(fixedRate)` often wrong for sim—use dedicated thread `ScheduledExecutorService` with drift correction. Render/publish phase double-buffers snapshot for websocket clients (pattern 050). Profiling: tick time histogram p99 < interval. Variable timestep only if sim allows—finance sim usually fixed for determinism. Testing: replay event log expecting deterministic outcomes. Contrast Event Queue—loop consumes queue each tick deliberately. For non-game backend (IoT aggregation), same loop pattern aggregates sensor batches per second with SLA on max staleness.

#### What it is
Continuous cycle driving simulation or interactive system: read input, update model by timestep, output state, repeat—fixed or variable delta time.

#### When to use / when NOT
- **Use:** Simulations, games, real-time dashboards driven by tick, physics engines.
- **NOT:** Request-driven CRUD—event loop waste. Use message-driven or reactive instead.

#### Java / Spring example

```java
void runLoop() {
    double acc = 0;
    long last = nanoTime();
    while (running) {
        acc += (nanoTime() - last) / 1e9;
        last = nanoTime();
        int caught = 0;
        while (acc >= DT && caught++ < MAX_CATCH_UP) { update(DT); acc -= DT; }
        publishSnapshot();
    }
}
```

#### Common mistakes
- Unbounded catch-up spiral when update slower than tick rate.
- Heavy I/O on loop thread.
- Non-deterministic random/time in replay-tested sim without injection.

#### Follow-up (with answer)
**Q:** Game loop vs event-driven reactive?
**A:** Game loop time-centric—progresses world each tick regardless of events. Reactive event-centric—work when messages arrive. Market sim often hybrid: loop advances time, events queued between ticks. Pick loop when time itself is domain driver; pick reactive when sporadic messages dominate.

---

### P076. Gateway

**Category:** Enterprise  
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/gateway/)

**Short answer:** Gateway encapsulates access to external system—translate, isolate, retry—so domain speaks local idioms not vendor APIs. Fowler's Gateway differs from API Gateway edge routing; it's anti-corruption at integration boundary. Trade-off: gateway class becoming dumping ground for all HTTP clients. It hurts when domain imports vendor SDK types or when gateway caches stale external state without TTL policy.

#### Scenario (interview)
**Situation:** Domain services import Stripe SDK directly—30 classes touch `PaymentIntent`. Stripe API version bump breaks half the monolith; tests require Stripe test keys in CI; switching to Adyen projected 6-month refactor touching domain.
**What they're testing:** Can you build payment gateway port with translation and resilience?
**Model answer:** Define domain port `PaymentGateway { PaymentResult charge(Money amount, PaymentMethod pm, IdempotencyKey key); }`. Infra module `StripePaymentGateway` adapts SDK, maps Stripe errors to domain `PaymentDeclined`, `GatewayUnavailable`. Domain never imports com.stripe. Gateway handles idempotency header, retry only on idempotent safe errors, circuit breaker, structured logging with correlation id—not business rules like refund eligibility. Tests: fake gateway in domain unit tests; contract tests against Stripe mock in infra module nightly. Version pin SDK in gateway module only; upgrade isolated. Second provider: `AdyenPaymentGateway implements PaymentGateway`, Spring `@Primary` swap via config. Anti-corruption: translate webhook payloads to domain events in separate `StripeWebhookAdapter`, not controller parsing JSON into domain. Metrics: decline rate, latency, breaker state. Don't confuse with Microservices API Gateway at edge—this is domain integration Gateway pattern. Rollout: extract interface, move SDK calls behind adapter, ArchUnit enforce. Senior payoff: vendor migration touches one module.

#### What it is
Object that wraps external subsystem API, providing simplified domain-friendly interface and handling translation, communication, and sometimes caching of remote calls.

#### When to use / when NOT
- **Use:** Every external system—payments, CRM, legacy mainframe, email provider.
- **NOT:** Internal module calls within same bounded context—use domain service directly.

#### Java / Spring example

```java
interface PaymentGateway { PaymentResult charge(ChargeRequest req); }
@Component
class StripePaymentGateway implements PaymentGateway {
    public PaymentResult charge(ChargeRequest req) { /* map + SDK */ }
}
```

#### Common mistakes
- Leaking vendor types through port interface.
- Gateway performing domain validation belonging in aggregate.
- No timeout/retry policy—cascading hangs.

#### Follow-up (with answer)
**Q:** Gateway (Fowler) vs Anti-Corruption Layer vs Adapter?
**A:** Gateway focuses on remote API access simplification. ACL broader boundary protecting domain model from foreign model—may include gateway plus translators and facades. Adapter makes one interface fit another—gateway often contains adapter mapping. In practice combine: `StripePaymentGateway` is gateway + adapter; ACL is the whole infra boundary module.

---

### P077. Guarded Suspension

**Category:** Concurrency  
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/guarded-suspension/)

**Short answer:** Guarded Suspension blocks until precondition true—wait on condition with lock, proceed when guard satisfied. `wait/notify`, `BlockingQueue.take`, and `Object.wait` with predicate loops implement it. Trade-off: missed signals, spurious wakeup, deadlock if guard wrong. It hurts when holding lock during slow work or when using `wait()` without while loop rechecking guard.

#### Scenario (interview)
**Situation:** Worker pool custom queue uses `if (queue.isEmpty()) wait()` without loop—spurious wakeups cause `NoSuchElementException`; producer notifies before consumer waits losing signal; occasional deadlock when consumer holds lock during file upload.
**What they're testing:** Do you know correct wait/notify and prefer JDK concurrent utilities?
**Model answer:** Guarded suspension: lock → while (!guard) wait() → work → unlock. Always while not if for spurious wakeup. `synchronized(monitor) { while (queue.isEmpty()) monitor.wait(); item = queue.remove(); }` producer `synchronized { queue.add(x); monitor.notifyAll(); }`. Better: replace hand-rolled with `BlockingQueue.take/put`— JDK implements guarded suspension correctly. Never call wait outside synchronized—IllegalMonitorStateException. Don't perform upload while holding monitor—copy item reference, exit lock, then upload. Lost wakeup if notify before wait without holding same lock order—use queue abstraction. For multiple conditions, `ReentrantLock` with `Condition` per guard. Metrics: wait time, queue depth. Spring `@Async` worker consuming blocking queue is idiomatic guarded handoff. If condition is "cache loaded," use `CountDownLatch` or `CompletableFuture` instead of raw wait. Incident fix: refactor to `ArrayBlockingQueue`, delete notify bugs. Senior default: don't hand-roll unless JFR proves queue bottleneck needing custom structure.

#### What it is
Thread suspends efficiently until guard predicate true, then resumes work atomically under proper locking—classic monitor pattern.

#### When to use / when NOT
- **Use:** Producer-consumer handoff, waiting for initialization complete, rendezvous points.
- **NOT:** Short busy-wait cases—use spin only with evidence. Prefer higher-level concurrent structures.

#### Java / Spring example

```java
void consume() throws InterruptedException {
    Item item = queue.take(); // guarded suspension inside JDK
    process(item);
}
```

#### Common mistakes
- `if` instead of `while` before wait.
- notify instead of notifyAll when multiple waiters with different guards.
- Holding lock during slow I/O while others wait on guard.

#### Follow-up (with answer)
**Q:** Guarded Suspension vs Balking vs Spinlock?
**A:** Guarded suspension blocks until ready—efficient when wait long. Balking returns immediately if guard false—use when retry later OK (log buffer full skip). Spinlock busy-waits short periods—rare in business apps. BlockingQueue implements guarded suspension for producer-consumer.

---

### P078. Half-Sync/Half-Async

**Category:** Architectural  
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/half-sync-half-async/)

**Short answer:** Half-Sync/Half-Async (HS/HA) separates synchronous service layer from asynchronous processing via queue—sync front accepts work quickly, async back handles slow steps. Servlet + JMS worker and Nginx + app server follow spirit. Trade-off: consistency between sync response and async completion. It hurts when client assumes synchronous outcome but async worker fails silently hours later.

#### Scenario (interview)
**Situation:** Loan origination API saves application synchronously then should run credit pull, document OCR, and underwriting async. Current design runs all sync—timeouts. Quick fix `@Async` loses failure notifications; applicants see "submitted" but credit never pulled.
**What they're testing:** Can you design HS/HA with status contract and durable queue?
**Model answer:** Sync half: validate, persist `Application` status `RECEIVED`, enqueue `OriginationJob` to durable queue (SQS/Kafka/outbox), return `202` with tracking id—fast. Async half: worker pool pulls jobs, runs credit/OCR/underwriting, updates status, publishes events. Client polls `/status/{id}` or webhook on completion—explicit contract. Outbox pattern ensures DB row and message atomic—no lost jobs if crash after save. Never `@Async void` without persistence. Sync half stays in request thread minimal work; async half scales independently on worker service. Failure: job retry with backoff, DLQ after N tries, alert ops, status `FAILED` visible to applicant. MDC trace propagated in message headers. Contrast Active Object—HS/HA often cross-process. Metrics: queue lag, job success rate, time RECEIVED→DECISION. Spring: `@Transactional` save + outbox relay; `@KafkaListener` async half. Don't HS/HA a read query—only multi-step slow workflows. Regulatory audit: job history table with timestamps.

#### What it is
Architecture splits synchronous interaction path from asynchronous processing path connected by bounded buffer/queue, optimizing responsiveness and throughput separately.

#### When to use / when NOT
- **Use:** Long workflows after quick acknowledgment—onboarding, claims, media processing.
- **NOT:** Need synchronous result in same HTTP request without async UX design.

#### Java / Spring example

```java
@Transactional
ApplicationId submit(ApplicationForm f) {
    var id = repo.save(new Application(RECEIVED, f)).id();
    outbox.send(new OriginationJob(id));
    return id;
}
@KafkaListener void process(OriginationJob job) { /* async half */ }
```

#### Common mistakes
- Fire-and-forget async without durable queue.
- Sync response implies final approval when only queued.
- Shared mutable state between halves without versioning.

#### Follow-up (with answer)
**Q:** HS/HA vs full reactive (WebFlux)?
**A:** HS/HA explicitly dual model sync accept + async workers—simple mental model for teams from servlet background. Full reactive non-blocking end-to-end reduces threads but complexity high. Choose HS/HA with outbox for durable workflows; reactive when sustained high concurrency same-process I/O multiplexing justified.

---

### P079. Health Check

**Category:** Microservices  
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/health-check/)

**Short answer:** Health Check exposes endpoint reporting readiness/liveness of service and dependencies. Spring Boot Actuator `/actuator/health`, Kubernetes probes, and load balancer checks use it. Trade-off: shallow ping vs deep check causing probe-induced outages. It hurts when liveness kills pod on slow dependency blip, or when health always UP hiding broken DB pool.

#### Scenario (interview)
**Situation:** K8s liveness probe hits `/actuator/health` including full DB migration check and Kafka consumer lag—dependency blip restarts all pods simultaneously, amplifying outage. Separate issue: broken deploy marked healthy because health only returns static UP.
**What they're testing:** Can you split liveness, readiness, and optional deep checks?
**Model answer:** Liveness: cheap—JVM up, thread not deadlocked (`/actuator/health/liveness`)—failure means restart pod. Readiness: can serve traffic—DB connection pool ping, critical cache reachable (`/readiness`)—failure removes from LB, no restart. Deep checks: dependency versions, migration level—run in CI deploy gate or admin endpoint, NOT liveness. Custom `HealthIndicator` for Kafka: readiness fails if consumer lag > threshold for 5min, not instant blip—use `@ReadinessState` with debouncing. Don't call external payment API in health—rate limits and coupling. Spring Boot 3 probes: `management.endpoint.health.probes.enabled=true`. Metrics tie health state to alerts. Incident: liveness including Kafka caused restart storm—fix split probes, increase `failureThreshold`. Startup probe for slow Spring context. Document what each probe validates; on-call runbook maps probe fail to action (restart vs scale vs fix dependency). Senior: health models failure domains—process vs dependency vs business sanity.

#### What it is
Component or endpoint periodically evaluated to report whether system can operate correctly—binary or detailed contributor status for orchestrators.

#### When to use / when NOT
- **Use:** Kubernetes, load balancers, orchestration, automated rollback triggers.
- **NOT:** Expensive business validation in hot probe path. Not as substitute for metrics/alerts.

#### Java / Spring example

```java
@Component
class DbReadiness implements HealthIndicator {
    public Health health() {
        return pool.ping() ? Health.up().build() : Health.down().build();
    }
}
```

#### Common mistakes
- Liveness probe calling slow external services.
- Single monolithic health for all concerns.
- Health UP while application misconfigured (missing bean caught only on first request).

#### Follow-up (with answer)
**Q:** Liveness vs readiness vs startup probe?
**A:** Startup allows slow boot before liveness/readiness enforced. Liveness: process wedged—restart. Readiness: temporarily can't serve—remove from traffic without restart. Misconfigured liveness on dependency failure causes crash loop amplifying outages—readiness should absorb transient dependency issues.

---

### P080. Hexagonal Architecture

**Category:** Architectural  
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/hexagonal-architecture/)

**Short answer:** Hexagonal Architecture (Ports and Adapters) places domain at center; ports define interfaces; adapters connect UI, DB, messaging. Dependency points inward—domain has zero infra imports. Trade-off: more modules and mapping boilerplate. It hurts when "hexagonal" folder layout exists but domain imports JPA annotations everywhere, or when every CRUD gets four adapters nobody tests.

#### Scenario (interview)
**Situation:** Team reorganized packages to `domain`, `adapter.in`, `adapter.out` but `Order` entity has `@ManyToOne`, REST DTOs in domain package, and use cases call `RestTemplate` directly. Architect claims hexagonal; onboarding devs confused with no benefit over layered monolith.
**What they're testing:** Can you enforce ports/adapters with dependency rules?
**Model answer:** Hexagonal intent: domain pure Java—`Order` aggregate, `PlaceOrderUseCase`, port interfaces `OrderRepository`, `PaymentGateway`, `PublishEvent`. Adapters: `JpaOrderRepository`, `StripeAdapter`, `KafkaEventPublisher`, `OrderRestController` calling use case. Domain module Gradle dependency graph: domain depends on nothing infra; application depends domain; adapters depend application+domain. JPA annotations on persistence entity in adapter module mapped to domain aggregate via mapper— or use separate persistence model if purity strict. Incoming adapter translates HTTP→command; outgoing implements port. ArchUnit: `domain.. should not depend on ..spring..` or `..jakarta..`. Testing: use case unit tests with fake ports—no Spring. Value emerges in regulated or long-lived systems with multiple channels (REST, batch, Kafka) sharing use cases. Don't hexagonal a 5-endpoint internal tool—layered enough. Migration: extract use case from service, introduce port interface, move JPA to adapter one aggregate at a time. Metrics: domain test runtime seconds, count of infra imports in domain zero. Interview trap: package names ≠ architecture—dependency direction proves it.

#### What it is
Application core isolated from external concerns via ports (interfaces) implemented by adapters for driving (UI) and driven (persistence, messaging) sides.

#### When to use / when NOT
- **Use:** Long-lived domains, multiple delivery mechanisms, testability without containers, vendor swap.
- **NOT:** Throwaway prototype, tiny CRUD with one REST surface.

#### Java / Spring example

```java
// domain
interface OrderRepository { void save(Order o); }
class PlaceOrderService {
    PlaceOrderService(OrderRepository repo, PaymentGateway pay) { ... }
}
// adapter
@Component
class JpaOrderRepository implements OrderRepository { ... }
```

#### Common mistakes
- Anemic ports mirroring entire JPA repository 1:1 without domain language.
- Domain depending on Spring stereotypes.
- Mapping explosion without codegen or clear boundaries.

#### Follow-up (with answer)
**Q:** Hexagonal vs Layered vs Clean Architecture?
**A:** Layered: presentation → business → data—dependencies often downward leaking. Hexagonal: symmetric adapters around core via ports. Clean Architecture similar rings with explicit use case layer. All share dependency inversion; hexagonal emphasizes equal treatment of UI and DB as peers plugging into core. Pick based on team vocabulary—enforce with module boundaries either way.

---

### P081. Identity Map

**Category:** Enterprise  
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/identity-map/)

**Short answer:** Identity Map ensures one in-memory instance per database identity within unit of work—avoid duplicate objects representing same row. JPA first-level cache is Identity Map. Trade-off: stale reads within long session, memory growth. It hurts when detached entities bypass map causing duplicate updates, or when long `@Transactional` request holds map and stale data conflicts.

#### Scenario (interview)
**Situation:** Same HTTP request loads `Customer id=42` via repository find twice in different services—without identity map, two instances diverge (address updated in one, old in other), last write wins loses change silently in same request scope.
**What they're testing:** Do you understand JPA persistence context as Identity Map and TX boundaries?
**Model answer:** Within `@Transactional` persistence context, `em.find(42)` and query returning id=42 yield same instance—Identity Map keyed by primary key. Problem case: two transactions in one request—second load creates new instance; or `@Transactional(propagation=REQUIRES_NEW)` breaks identity continuity. Fix: align transaction boundary to request use case; avoid multiple TX for single user action unless intentional. Don't disable L1 cache to "always fresh"—performance hit; use `@Modifying(clearAutomatically=true)` or `refresh()` when needed. Long conversations: extended persistence context (Open Session In View anti-pattern) keeps map alive—stale reads and memory—prefer DTO exit or short TX. Testing: same EntityManager, load twice, assert `assertSame(a,b)`. Distributed: Identity Map per JVM only—cross-pod consistency via DB versioning (`@Version`), not shared map. Pattern explicitly useful in hand-rolled ORM or batch loaders merging rows—manual `Map<Long, Customer> identityMap` during import. Metrics: persistence context size in debug, optimistic lock exceptions signal concurrent identity conflict.

#### What it is
Registry tracking loaded objects by key; lookup returns existing instance instead of creating duplicate for same identity.

#### When to use / when NOT
- **Use:** ORM session, unit of work, batch import deduplication within process.
- **NOT:** Cross-request global cache—that's second-level cache with different consistency semantics.

#### Java / Spring example

```java
@Transactional
void updateCustomer(Long id, Address addr) {
    Customer c1 = repo.findById(id).orElseThrow();
    Customer c2 = repo.findById(id).orElseThrow();
    assert c1 == c2; // same persistence context instance
    c1.setAddress(addr);
}
```

#### Common mistakes
- Multiple transactions per request breaking identity guarantee.
- OSIV holding identity map across render phase with writes interleaved.
- Expecting Identity Map coherence across microservices—impossible.

#### Follow-up (with answer)
**Q:** Identity Map vs second-level cache vs HTTP cache?
**A:** Identity Map: per persistence context/session, guarantees object identity within UoW. Second-level cache: shared across sessions in JVM, entity data cache not identity guarantee across contexts. HTTP cache: cross-request API responses. Choose Identity Map behavior via JPA session scope; don't confuse L2 cache as Identity Map.

---

### P082. Immutable

**Category:** Behavioral  
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/immutable/)

**Short answer:** Immutable objects never change after construction—thread-safe sharing, reliable hash keys, easier reasoning. Java records, `final` fields, unmodifiable collections, and defensive copies implement it. Trade-off: copying cost and awkward "updates" requiring new instances. It hurts when shallow immutability exposes mutable list internals, or when giant object graphs copy every minor change.

#### Scenario (interview)
**Situation:** Shared `PricingContext` POJO mutated in parallel stream pipeline—intermittent wrong totals under load. Team added `synchronized` everywhere hurting throughput; `Money` class has mutable `BigDecimal amount` field.
**What they're testing:** Can you design immutable value objects and transformation pipelines?
**Model answer:** Make `Money`, `LineItem`, `PricingContext` immutable—records with compact constructors validating invariants, collections wrapped `List.copyOf()`. Updates return new instances: `context.withPromo(promo)` copying structure sharing unchanged fields. Parallel streams safe without locks. Enforce: no setters, package-private ctor + factory `Money.of(amount, currency)`. Beware shallow immutability: `record Cart(List<Item> items)` must copy list in ctor. Persistence: JPA entities often mutable by ORM requirement—keep immutable model in domain, map at boundary; don't pretend Hibernate entity is immutable without `@Immutable` read-only semantics. For high churn UI state, structural sharing libraries optional. Testing: mutate attempt throws or no-op; hash stable for map keys. Metrics: lock contention drop after immutability refactor. Java 21 records reduce boilerplate. Senior: immutability at value object and message/event layers; aggregates may mutate internally but expose immutable snapshots outward.

#### What it is
Object state fixed at creation; operations producing change return new objects rather than modifying existing.

#### When to use / when NOT
- **Use:** Value objects, money, coordinates, events, DTOs crossing threads, cache keys.
- **NOT:** JPA write-heavy entities (use separate immutable domain snapshot). Not when profiling proves copy cost dominates.

#### Java / Spring example

```java
record Money(BigDecimal amount, Currency currency) {
    Money { amount = amount.stripTrailingZeros(); }
    Money add(Money other) { return new Money(amount.add(other.amount), currency); }
}
```

#### Common mistakes
- Immutable record holding mutable List passed from caller.
- `Date`/`Calendar` mutable fields in "immutable" class.
- Defensive copy omitted on getter returning internal array.

#### Follow-up (with answer)
**Q:** Immutable vs defensive copy vs unmodifiable view?
**A:** Immutable object never changes; all fields immutable. Defensive copy on construction/getter protects internal state but object might still have setters elsewhere. `Collections.unmodifiableList` view fails if backing list mutated—prefer copy at construction for true immutability. Records + `List.copyOf` idiomatic Java.

---

### P083. Intercepting Filter

**Category:** Enterprise  
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/intercepting-filter/)

**Short answer:** Intercepting Filter chains servlet filters or Spring HandlerInterceptors processing request/response before/after target—auth, logging, compression. Composable ordering defines pipeline. Trade-off: opaque order dependencies and debugging filter chains. It hurts when security filter runs after controller already executed business logic due to wrong `@Order`.

#### Scenario (interview)
**Situation:** New tenant isolation filter added but registered after `DispatcherServlet` mapping in wrong order—requests hit controller with wrong tenant schema before filter sets context; GDPR data leak across tenants for 2 hours until rollback.
**What they're testing:** Do you understand filter chain order and Spring Security integration?
**Model answer:** Intercepting Filter pattern: request passes chain of filters each optionally short-circuit before servlet/controller. Tenant filter must run early—before security auth if tenant from JWT, after auth if tenant from principal—document explicit order via `@Order(Ordered.HIGHEST_PRECEDENCE + 10)` or `FilterRegistrationBean#setOrder`. Spring Security is itself filter chain—custom tenant filter often via `OncePerRequestFilter` in security chain `addFilterAfter`. Test: MockMvc verify wrong tenant cannot access resource even if header spoofed. Filters lightweight—no DB heavy query; cache tenant metadata. Response path: filters can wrap response for compression/logging. Contrast AOP `@Aspect`—filters servlet layer before Spring MVC; AOP around beans after dispatch. Metrics: filter latency per name in tracing. Incident: wrong order fixed by integration test asserting `TenantContext` set before controller invoked—`FilterChainProxy` order diagram in wiki. Don't duplicate auth in filter and annotation inconsistently.

#### What it is
Chain of processing components intercepts requests/responses, each performing preprocessing/postprocessing before delegating to next or target.

#### When to use / when NOT
- **Use:** Cross-cutting web concerns—auth, MDC, CORS, rate limit at edge of request handling.
- **NOT:** Business rules belonging in domain service—filter only establishes context.

#### Java / Spring example

```java
@Component
@Order(Ordered.HIGHEST_PRECEDENCE + 20)
class TenantFilter extends OncePerRequestFilter {
    protected void doFilterInternal(req, res, chain) {
        TenantContext.set(resolve(req));
        try { chain.doFilter(req, res); } finally { TenantContext.clear(); }
    }
}
```

#### Common mistakes
- ThreadLocal tenant not cleared in finally—pool leak across tenants.
- Wrong filter order vs security chain.
- Heavy work in filter blocking all requests.

#### Follow-up (with answer)
**Q:** Filter vs HandlerInterceptor vs AOP `@Around`?
**A:** Servlet Filter runs before Spring MVC dispatch—earliest web hook. HandlerInterceptor wraps controller handler only—needs Spring MVC context. AOP `@Around` any Spring bean method—service layer cross-cutting. Auth tenant at filter; controller timing at interceptor; `@Transactional` at AOP. Choose layer matching concern scope.

---

### P084. Interpreter

**Category:** Behavioral  
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/interpreter/)

**Short answer:** Interpreter defines grammar as classes and interprets sentences by walking expression tree—`Expression` hierarchy with `interpret(context)`. Use for small DSLs, rules, query languages. Trade-off: class explosion per grammar symbol. It hurts when team builds Interpreter for complex language better served by parser generator (ANTLR) or when performance requires compilation not tree walk.

#### Scenario (interview)
**Situation:** Promotions team encodes rules as strings `"cart.total > 100 AND customer.tier == GOLD"` evaluated via nested `split("AND")` hack—bugs with operator precedence, quotes, and injection via crafted customer names breaking eval.
**What they're testing:** Can you propose safe rule evaluation architecture?
**Model answer:** For limited boolean promo DSL, Interpreter pattern: parse string to AST (`AndExpr`, `CompareExpr`, `FieldExpr`), each node implements `boolean eval(PromoContext ctx)`. Parser hand-written recursive descent or ANTLR generating parser—Interpreter classes mirror grammar terminals/nonterminals. Sandboxed context exposes only safe fields—no reflection on arbitrary objects. NOT `ScriptEngineManager` JavaScript on user strings—security nightmare. For 4 rules, hard-code Strategy map; Interpreter justified when business users author dozens of combinable rules stored in DB. Cache parsed AST per rule id version. Performance: tree walk fine for checkout once; compile to bytecode or decision table if millions evals/sec. Testing: table-driven AST cases, property tests on parser. Migration: parse old strings to AST, validate, store serialized AST. Alternative: DMN engine (Camunda) if enterprise rule management needed. Senior: know when Interpreter ends and proper language tooling begins—grammar complexity threshold.

#### What it is
Represent grammar rules as classes; build abstract syntax tree; interpret by recursive eval on tree nodes for given context.

#### When to use / when NOT
- **Use:** Small expression languages, config formulas, access control policies with stable grammar.
- **NOT:** General-purpose scripting, large language—use parser generator + maybe bytecode.

#### Java / Spring example

```java
sealed interface PromoExpr permits AndExpr, CompareExpr {
    boolean eval(PromoContext ctx);
}
record AndExpr(PromoExpr left, PromoExpr right) implements PromoExpr {
    public boolean eval(PromoContext ctx) { return left.eval(ctx) && right.eval(ctx); }
}
```

#### Common mistakes
- Eval with `eval()` on user string via scripting engine.
- No grammar versioning—silent behavior change on deploy.
- Class per token without shared composition structure—unmaintainable.

#### Follow-up (with answer)
**Q:** Interpreter vs Strategy vs Rule Engine (Drools)?
**A:** Strategy selects one algorithm from fixed set in code. Interpreter parses expressions into evaluable tree—rules as data. Drools adds RETe optimization, forward chaining, tooling—for hundreds of interacting rules. Start Interpreter/AST for tens of rules; graduate to DMN/Drools when non-devs manage rule lifecycle at scale.

---

### P085. Iterator

**Category:** Behavioral  
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/iterator/)

**Short answer:** Iterator provides uniform sequential access to aggregate internals without exposing representation. Java `Iterable`, `Iterator`, enhanced for-loop, and streams build on it. Trade-off: concurrent modification if collection mutates during iteration. It hurts when custom iterator exposes internal mutable structure violating encapsulation, or when lazy iterator hides expensive I/O per `next()` without documentation.

#### Scenario (interview)
**Situation:** Custom `PaginatedOrderIterator` hits database on every `hasNext()` in reporting job—job estimated 10 minutes runs 14 hours. Another team returns live `ArrayList` iterator from domain aggregate allowing external remove during iteration corrupting invariants.
**What they're testing:** Do you design lazy iterators, fail-fast, and batch fetch?
**Model answer:** Iterator should hide pagination: fetch page of 500 on construction and when page exhausted—amortize DB calls. `hasNext()` must not query DB every call—cache page iterator state. For domain aggregate, don't expose internal list iterator—provide `for (LineItem item : order.lines())` returning unmodifiable view or read-only iterator enforcing fail-fast via snapshot copy on first iteration if mutations rare. Concurrent modification: `ConcurrentModificationException` or immutable snapshot for report generation. Java Stream over paginated source: custom `Spliterator` batching JDBC `setFetchSize`. Reporting job: Spring Data `Stream<Order>` with `@Transactional(readOnly=true)` must close stream in try-with-resources—leak cursors. Metrics: query count per report job should be O(pages) not O(records). Alternative: keyset pagination iterator for stable large dataset vs offset. Senior: Iterator pattern everyday via for-each; custom when traversing composite tree or paged remote API uniformly.

#### What it is
Object encapsulating traversal logic over collection/composite, providing `hasNext/next` without revealing underlying structure.

#### When to use / when NOT
- **Use:** Uniform traversal of custom structures, lazy paged access, composite trees.
- **NOT:** Simple `List` already iterable—use directly unless hiding pagination.

#### Java / Spring example

```java
class OrderPageIterator implements Iterator<Order> {
    public boolean hasNext() { ensurePageLoaded(); return index < page.size() || fetchNextPage(); }
}
```

#### Common mistakes
- O(n) DB round trip per `next()`.
- Returning modifiable internal collection iterator.
- Stream opened without close on large JDBC result.

#### Follow-up (with answer)
**Q:** Iterator vs Stream vs external pagination API?
**A:** Iterator imperative, single-pass, lazy—good custom control. Stream functional pipeline with ops chain—parallel cautiously. External pagination API explicit page tokens—clients handle; internal Iterator hides for domain traversal. Use Stream for collection transforms; Iterator for bespoke paged/enumeration encapsulation.

---

### P086. Layered Architecture

**Category:** Architectural  
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/layered-architecture/)

**Short answer:** Layered Architecture organizes code into horizontal layers—presentation, business, persistence—with dependencies typically downward. Classic Spring MVC + Service + Repository stack. Trade-off: layer violation and anemic domain if layers become procedural passthrough. It hurts when every change touches three layers of DTO mapping with no business win, or when presentation calls JDBC "just once."

#### Scenario (interview)
**Situation:** Enterprise app strictly enforces Controller→Service→Repository but Service layer is 100% pass-through to repository; domain rules duplicated in controller validation and SQL stored procedures; new feature requires 12 DTO mappings for one field change.
**What they're testing:** Can you critique layers and propose meaningful boundaries?
**Model answer:** Layers are means not religion—each layer should add value. Presentation: HTTP/validation/DTO mapping. Application service: orchestration, TX boundaries, authorization checks. Domain: invariants (or rich entities). Persistence: ORM/SQL. Anti-pattern: service methods `return repo.findX()` only—collapse or move orchestration up/down consciously. Stored procedures duplicating Java rules—pick single source of truth. Reduce DTO churn: record types, MapStruct, or expose read models via query layer bypassing full stack for reads (CQRS-lite) when mapping cost dominates. Allow controller→application service only; forbid controller→repository via ArchUnit. When microservice extracted, layer becomes service boundary—don't distribute anemic layers across network. Metrics: feature lead time, defect rate in business rules. Evolution path: layered monolith healthy with rich domain; anemic layers signal push logic into domain or simplify stack. Interview answer: acknowledge layered Spring default, enforce dependency rules, refactor pass-through services when mapping cost exceeds benefit—not blindly add hexagonal everywhere.

#### What it is
System partitioned into stacked layers each with role; upper layers call lower, not reverse—classic n-tier enterprise structure.

#### When to use / when NOT
- **Use:** Enterprise CRUD/modernization, teams familiar with Spring structure, moderate complexity.
- **NOT:** High-scale read/write split needing independent scale—consider CQRS/microservices instead of thicker layers.

#### Java / Spring example

```java
@RestController class OrderController { /* DTO in/out */ }
@Service class OrderService { @Transactional Order place(OrderCmd c) { ... } }
interface OrderRepository extends JpaRepository<OrderEntity, Long> {}
```

#### Common mistakes
- Repository calls from controller "just once."
- Business logic split across SQL, service, controller inconsistently.
- Layer packages without dependency enforcement—fiction.

#### Follow-up (with answer)
**Q:** Layered vs hexagonal vs clean—when stay layered?
**A:** Stay layered when team productive, domain moderate, single delivery channel, ArchUnit prevents leaks. Move ports/adapters when multiple channels, heavy vendor swap, or domain purity pays test dividends. Layers can contain hexagonal inner structure—compatible not exclusive.

---

### P087. Lazy Loading

**Category:** Performance  
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/lazy-loading/)

**Short answer:** Lazy Loading defers expensive load until first access—JPA `@ManyToOne(fetch=LAZY)`, Hibernate proxies, `Supplier` memoization. Trade-off: N+1 queries and LazyInitializationException outside session. It hurts when lazy associations accessed in loop causing hundreds of queries, or when OSIV masks problem until production load.

#### Scenario (interview)
**Situation:** Order list API returns 200 orders; Jackson serializes lazy `Customer` on each—2001 SQL queries, p99 8s. Developer enables `spring.jpa.open-in-view=true` fixing LazyInitializationException but hides N+1 until Black Friday.
**What they're testing:** Can you fix fetch plan not OSIV band-aid?
**Model answer:** Lazy loading intent: don't load customer until accessed—good default for unused associations. Fix N+1: `@EntityGraph(attributePaths="customer")` on query, or JOIN FETCH in JPQL, or batch size `@BatchSize(25)` on collection, or DTO projection query selecting needed columns only—best for read API. Disable OSIV for APIs—fail fast in dev on lazy access outside TX forcing explicit fetch plan. Write path: lazy OK inside `@Transactional` service method touching association once. Virtual threads don't fix N+1—still 2001 queries. Metrics: Hibernate statistics query count per request, datasource pool usage. GraphQL/DataLoader batching another lazy batch pattern. Document which endpoints eager fetch vs projection. Incident: replace entity return with `OrderSummaryDto` query joining customer name column only—1 query. LazyInitializationException solution is correct TX boundary + fetch join, not OSIV globally. Senior Hibernate answer always mentions fetch plan and read vs write path.

#### What it is
Proxy or placeholder loads real data on first access transparently to caller, spreading load cost until needed.

#### When to use / when NOT
- **Use:** Large object graphs rarely fully traversed, expensive optional associations.
- **NOT:** Hot path always needing association—eager fetch or projection instead.

#### Java / Spring example

```java
@Query("select o from Order o join fetch o.customer where o.id = :id")
Optional<Order> findWithCustomer(Long id);
```

#### Common mistakes
- OSIV masking N+1 in APIs.
- Lazy collection serialized to JSON triggering full load.
- Eager everything "to be safe"—memory and join explosion.

#### Follow-up (with answer)
**Q:** Lazy loading vs `@EntityGraph` vs DTO projection?
**A:** Lazy default defer load. EntityGraph declaratively eager for specific query without global eager mapping. DTO projection avoids entity and lazy entirely—best for read APIs. Pick projection for list screens; entity graph for detail needing full aggregate in TX.

---

### P088. Leader Election

**Category:** Concurrency  
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/leader-election/)

**Short answer:** Leader Election selects one coordinator among peers for exclusive work—scheduler tick, partition processing, config writes. Kubernetes lease, Curator `LeaderSelector`, Redis Redlock variants apply. Trade-off: split-brain if election flawed, failover delay. It hurts when two leaders run simultaneously corrupting data, or when election churn on GC pauses causes constant leadership flip.

#### Scenario (interview)
**Situation:** Three Spring Boot pods run `@Scheduled` invoice batch nightly—all three process same invoices, triple-charging customers until reconciliation catches it. Quick fix `@ConditionalOnProperty leader=true` on one pod manually—fails on deploy when wrong pod flagged.
**What they're testing:** Can you implement distributed leader election with fencing?
**Model answer:** Only leader runs batch: ShedLock with JDBC/Redis backing `@SchedulerLock`, or Curator ZooKeeper `LeaderSelector`, or K8s Lease API. Lock must have TTL + heartbeat—leader renews; if dies, follower acquires after TTL. Fencing: DB update includes `leaderEpoch` token stored in ZooKeeper— stale leader can't write after losing leadership (compare-and-set on epoch). ShedLock simple for many Spring shops: `@SchedulerLock(name="invoiceBatch", lockAtMostFor="PT30M")`. Metrics: leadership held duration, failed lock attempts, duplicate batch detection alert (should zero). Avoid naive DB `UPDATE locks SET holder=pod WHERE holder IS NULL` without fencing—split brain possible. Test: kill leader pod mid-batch, verify single completion without duplicate. Document manual leader property anti-pattern removed. For Kafka consumers, partition assignment not same as leader election but related—one consumer per partition. Azure Service Bus session handler similar exclusivity. Senior: leader election for singleton work across cluster; scale workers horizontally for partitionable work instead.

#### What it is
Distributed protocol ensures at most one node acts as coordinator at a time, with failover when leader fails.

#### When to use / when NOT
- **Use:** Singleton scheduled jobs, global sequence writers, coordinated migration runners.
- **NOT:** Embarrassingly parallel work—partition instead of electing leader doing all.

#### Java / Spring example

```java
@Scheduled(cron = "0 2 * * *")
@SchedulerLock(name = "invoiceBatch", lockAtLeastFor = "PT5M", lockAtMostFor = "PT1H")
void runBatch() { /* only leader executes */ }
```

#### Common mistakes
- Manual config flag leader without automatic failover.
- Lock without TTL—dead leader blocks forever.
- No fencing token on downstream writes.

#### Follow-up (with answer)
**Q:** Leader election vs distributed lock vs Kafka consumer group?
**A:** Leader election picks one coordinator role. Distributed lock serializes critical section any holder. Kafka consumer group assigns partition consumption—parallelism with one consumer per partition. Use election for one global job; use partitions for scalable parallel processing of sharded workload.

---

### P089. Leader-Followers

**Category:** Concurrency  
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/leader-followers/)

**Short answer:** Leader-Followers thread pool pattern: leader thread waits on event source, promotes follower to leader on event, processes or delegates while new follower joins pool. Efficient for high-concurrency servers handling many similar events. Trade-off: complex thread role switching vs simpler thread-per-request. It hurts when misapplied to blocking CRUD apps where platform thread pool suffices, or when leader dies without promoting follower leaving pool stuck.

#### Scenario (interview)
**Situation:** Custom TCP gateway built Leader-Followers for 50k persistent connections; after JDK upgrade rare bug leaves no leader thread accepting connections—accept queue fills silently; team lacks expertise to debug role promotion.
**What they're testing:** Do you know when bespoke LF pool beats Netty/virtual threads?
**Model answer:** Leader-Followers: one thread blocks on `select/accept`, on event hands off and follower becomes new leader—minimizes context switch for connection storms. Appropriate for custom high-perf servers (game servers, proprietary protocols). For HTTP Spring Boot, use Netty (WebFlux) or virtual threads platform—don't hand-roll LF unless benchmarks prove need. If maintaining LF gateway: instrument state machine LEADER/WAITING/PROCESSING, assert invariant exactly one leader blocked on accept, watchdog alerts if no leader 5s. Promotion on event must be atomic under lock; follower pool pre-warmed. Failure mode in incident: promotion bug when handler throws before promoting—use finally block to ensure new leader. Migration path: replace custom LF with Netty EventLoopGroup—battle-tested same pattern abstractly. Compare Active Object—LF focuses thread pool roles for many similar events; Active Object single-thread executor per component. Metrics: accept queue depth, leader promotion rate, idle followers. Senior advice: recognize pattern in Netty internals; don't implement for typical REST microservice—operational cost exceeds benefit.

#### What it is
Thread pool where one leader waits for work on input source; upon event, leader promotes follower to leader and handles event—recycling threads without per-request thread creation.

#### When to use / when NOT
- **Use:** High-performance event-driven servers, many short-lived similar events, custom NIO servers.
- **NOT:** Typical Spring MVC blocking stack—use container thread pool or virtual threads.

#### Java / Spring example

```java
// Conceptual — production: prefer Netty EventLoop
void leaderLoop() {
    while (running) {
        Event e = source.waitForEvent(); // leader blocks
        Follower f = promoteFollowerToLeader();
        pool.execute(() -> handle(e));
    }
}
```

#### Common mistakes
- Missing promotion on exception path—pool stuck.
- Building LF for 100 req/s REST—unnecessary complexity.
- Confusing with Master-Worker batch pattern.

#### Follow-up (with answer)
**Q:** Leader-Followers vs thread pool vs reactive event loop?
**A:** Classic thread pool: any idle worker takes task from queue. Leader-Followers specialized for event demultiplexing with single acceptor role. Reactive Netty event loop is refined LF-like model for I/O. Use Netty/reactive before custom LF; use platform/virtual threads for blocking Spring MVC simplicity.

---

### P090. Lockable Object

**Category:** Concurrency  
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/lockable-object/)

**Short answer:** Lockable Object encapsulates lock acquisition/release with object state—methods acquire lock internally or via `withLock` API ensuring consistent locking discipline. Contrast ad-hoc locking on shared mutable object from outside. Trade-off: coarse lock limits concurrency. It hurts when lock held across I/O blocking other threads, or when dual locking orders cause deadlock between two lockable objects.

#### Scenario (interview)
**Situation:** Shared `AccountBalance` mutated from transfer service, interest job, and webhook handler—each synchronizes on different monitors (`balance` object vs `Account.class` vs `this` in service)—race conditions produce negative balance intermittently.
**What they're testing:** Can you centralize locking on lockable domain object with clear protocol?
**Model answer:** Make `Account` Lockable Object: all mutations through `synchronized void debit(Money m)` / `credit` methods or `ReentrantLock` private with `executeLocked(Runnable)`—external code cannot mutate fields directly. Single lock per aggregate instance—aligns DDD aggregate consistency boundary. Transfer between accounts: lock ordering by `accountId` ascending to prevent deadlock: `lock(a1,a2) { a1.debit; a2.credit; }` helper on domain service. Don't lock during fraud API call—copy intent, release lock, call external, re-lock confirm (or use saga). Interest batch: partition accounts by id shard processing reducing contention vs global lock. Metrics: lock wait time, deadlock detection thread dump playbooks. Prefer `@Version` optimistic locking for JPA concurrent updates with retry on `OptimisticLockException`—Lockable Object in-memory for single JVM aggregate cache or non-JPA domain. Testing: concurrent stress `ExecutorService` 100 threads transfer random accounts assert sum conserved. Refactor: private fields, all mutation via lockable methods, forbid setters. Senior: Lockable Object makes lock policy explicit; optimistic concurrency often scales better across DB than pessimistic synchronized in cluster.

#### What it is
Object owning synchronization primitive; operations on object acquire its lock internally maintaining invariants under concurrency.

#### When to use / when NOT
- **Use:** In-memory aggregate cache, game state object, finetuned mutable domain object in single JVM hot path.
- **NOT:** Cluster-wide consistency—use DB transactions/optimistic locking. Not lock during external calls.

#### Java / Spring example

```java
class Account {
    private final ReentrantLock lock = new ReentrantLock();
    private Money balance;
    void debit(Money m) {
        lock.lock();
        try { balance = balance.minus(m); }
        finally { lock.unlock(); }
    }
}
```

#### Common mistakes
- External code locking wrong monitor inconsistently.
- Lock held during network I/O.
- Deadlock transferring between accounts without lock ordering.

#### Follow-up (with answer)
**Q:** Lockable Object vs synchronized methods vs optimistic `@Version`?
**A:** Lockable Object centralizes pessimistic lock policy on object. `synchronized` methods same if all access through methods. Optimistic `@Version` detects conflicts at commit—better multi-instance DB-backed aggregates. Use in-memory Lockable for single-node hot state; optimistic for persisted entities across pods.

---



# Design Pattern Catalog — Part 3 (P091–P135)

Scenario-based senior interview Q&A aligned with [java-design-patterns.com](https://java-design-patterns.com/patterns/).

---

### P091. MapReduce

**Category:** Architectural / Performance
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/map-reduce/)

**Short answer:** MapReduce splits large datasets into independent map tasks that emit key-value pairs, shuffles/grouping by key, then reduces aggregates in parallel. It scales horizontally on Hadoop/Spark but hurts when work is not embarrassingly parallel, when shuffle I/O dominates, or when you need low-latency OLTP instead of batch analytics.

#### Scenario (interview)
**Situation:** A payments risk team must compute merchant chargeback rates across 400M transactions stored in S3. The nightly JDBC job on a single RDS read replica misses the SLA by three hours and spikes I/O.
**What they're testing:** Whether you recognize embarrassingly parallel aggregation vs. forcing SQL on one node.
**Model answer:** I would stop scaling the monolithic SQL job and adopt MapReduce semantics—either Spark on EMR or a managed pipeline. Each map task reads a partition of transaction files, emits `(merchantId, {count, chargebacks})` pairs. Shuffle groups by merchantId; reduce sums numerators and denominators. Map tasks must be stateless and idempotent so failed workers replay safely. I'd colocate compute with data (same region/bucket prefix) to avoid egress. For skewed merchants, I'd apply combiners in the map phase and optional salting on hot keys. Output lands in Parquet for the dashboard. I would not MapReduce a 500-row admin report—that is framework tourism. Success metric: job completes within the 90-minute window with predictable cost per TB scanned.

#### What it is
A distributed data-processing model: map transforms records into intermediate key-value pairs; shuffle groups keys; reduce aggregates per key. Hadoop made it famous; Spark generalizes it with in-memory DAGs.

#### When to use / when NOT
- **Use:** TB+ batch analytics, log aggregation, ETL where tasks partition cleanly and failures are recoverable.
- **Use:** Horizontal scale matters more than single-record latency.
- **NOT:** OLTP lookups, tight sub-second APIs, or graphs requiring iterative global state without careful design.
- **NOT:** When shuffle cost exceeds compute—consider stream processing or pre-aggregated rollups.

#### Java / Spring example
```java
// Spark-style word count — map → reduceByKey
JavaPairRDD<String, Integer> counts = sc.textFile("s3://txn/")
    .flatMapToPair(line -> Arrays.stream(line.split(","))
        .map(w -> new Tuple2<>(w, 1)).iterator())
    .reduceByKey(Integer::sum);
```

#### Common mistakes
- Running MapReduce on datasets that fit in one machine's RAM—operational tax without benefit.
- Ignoring key skew; one reducer becomes a straggler and blows the SLA.
- Treating map output as durable truth without idempotent reduce side effects.

#### Follow-up (with answer)
**Q:** MapReduce vs stream processing (Flink/Kafka Streams)?
**A:** MapReduce (batch) optimizes throughput over bounded datasets with checkpointed stages; latency is minutes to hours. Stream processing handles unbounded events with windowed aggregation and millisecond-to-second latency. Choose batch when correctness and cost per TB matter and freshness can be T+1. Choose streams when fraud detection or inventory must react within seconds. Hybrid: stream for near-real-time signals, nightly MapReduce for reconciliation and audit-grade totals.

---

### P092. Marker Interface

**Category:** Structural / Enterprise
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/marker-interface/)

**Short answer:** A marker interface has no methods—it tags types for frameworks or APIs (`Serializable`, `Cloneable`). It communicates intent at compile time but is largely superseded by annotations and sealed types. It hurts when used as a security boundary or when runtime checks replace explicit capability models.

#### Scenario (interview)
**Situation:** A legacy audit module serializes any object implementing `Auditable` (empty interface) to an immutable log. A developer marks `UserSession` as `Auditable`; sessions contain JWT secrets and get persisted to cold storage.
**What they're testing:** Whether you treat marker interfaces as documentation vs. enforcement.
**Model answer:** I'd treat the marker as a compile-time hint only—not a security control. First, I'd inventory types implementing `Auditable` and remove the marker from anything carrying credentials. Replace the marker with an annotation `@AuditableEntity` plus an explicit `AuditSerializer` that whitelists fields, or use Jackson views. For framework integration (e.g., JPA entity listeners), prefer `@EntityListeners(AuditListener.class)` over empty interfaces. If we keep a marker for API clarity, enforce serialization through a single gateway that rejects non-whitelisted fields. I'd add ArchUnit tests: classes implementing `Auditable` must not declare fields annotated `@Secret`. Rollout: feature flag on the new serializer, diff old vs. new audit payloads in staging. The incident shows markers tag intent but never substitute for policy and code review.

#### What it is
An interface declaring no methods, used to mark classes for special treatment by JVM, frameworks, or conventions.

#### When to use / when NOT
- **Use:** Legacy APIs (`Serializable`), framework hooks where annotations did not exist.
- **Use:** Rarely today—prefer annotations with retention and attributes.
- **NOT:** Authorization, validation, or "this is safe to log" guarantees.
- **NOT:** When sealed interfaces + records express domain variants more clearly.

#### Java / Spring example
```java
public interface DomainEvent {} // prefer sealed interface or @DomainEvent annotation

@Target(TYPE) @Retention(RUNTIME)
public @interface EventSourcedAggregate {}
```

#### Common mistakes
- Assuming `Serializable` implies safe or versioned persistence.
- Spraying marker interfaces across DTOs without a single enforcement point.
- Using markers instead of explicit capability interfaces with behavior.

#### Follow-up (with answer)
**Q:** Marker interface vs annotation?
**A:** Markers participate in type system checks (`instanceof`, generics bounds) but carry no metadata. Annotations attach attributes (`@Transactional(readOnly=true)`) and integrate with Spring AOP, validation, and documentation generators. Modern Spring favors annotations; markers remain for JVM contracts like `Serializable`. For domain tagging, sealed types plus records give exhaustiveness in switch expressions—stronger than empty interfaces.

---

### P093. Master-Worker

**Category:** Concurrency / Architectural
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/master-worker/)

**Short answer:** A master decomposes work and assigns tasks to worker pool; workers report results. It parallelizes CPU-bound or I/O-bound batches but hurts when the master becomes a bottleneck, task granularity is wrong, or failure/retry semantics are undefined.

#### Scenario (interview)
**Situation:** An insurance quoting service recalculates premiums for 2M policies after a rate-table change. A single `@Scheduled` job loops policies sequentially; the batch window is 6 hours.
**What they're testing:** Task decomposition, back-pressure, and idempotent workers.
**Model answer:** I'd introduce a master-worker topology without rewriting business rules. The master reads policy IDs in chunks of 500 from a cursor table, enqueues `RecalcTask(policyId, rateVersion)` to SQS or an internal `BlockingQueue`, and tracks completion in a `batch_run` table. Workers—Spring `@Async` pool or Kubernetes jobs—pull tasks, load policy + rate table shard, compute premium, persist with optimistic lock on `rateVersion`. Master monitors lag and scales workers horizontally. Tasks must be idempotent: same `(policyId, rateVersion)` yields same write. On worker crash, visibility timeout redelivers. I'd cap in-flight tasks to avoid DB connection storms and use bulkhead thread pools per tenant. Master does not compute premiums—it only schedules and aggregates metrics. If master dies, another instance resumes from cursor checkpoint. NOT master-worker for a single 200-policy hotfix—run inline.

#### What it is
Coordinator (master) splits a job into subtasks; workers execute independently; master collects outcomes or tracks progress.

#### When to use / when NOT
- **Use:** Embarrassingly parallel batch work, image/PDF processing, Monte Carlo simulations.
- **Use:** Work items are homogeneous and retry-safe.
- **NOT:** Strong ordering required across entire dataset without partitioning strategy.
- **NOT:** Master holds all state in memory for unbounded queues.

#### Java / Spring example
```java
@Service
class RecalcMaster {
  void dispatch(List<Long> ids) {
    ids.forEach(id -> queue.send(new RecalcTask(id, rateVersion)));
  }
}
@Service
class RecalcWorker {
  @JmsListener(destination = "recalc")
  void handle(RecalcTask t) { premiumService.recalc(t.policyId(), t.version()); }
}
```

#### Common mistakes
- Master performing heavy computation—becomes serial bottleneck.
- No poison-message handling; one bad policy blocks the batch forever.
- Shared mutable worker state causing race conditions.

#### Follow-up (with answer)
**Q:** Master-Worker vs Fork/Join?
**A:** Fork/Join splits recursive tasks in-process with work-stealing (`ForkJoinPool`)—great for CPU-bound divide-and-conquer on one JVM. Master-Worker spans processes/containers with explicit queues—better for I/O-heavy, heterogeneous, or cloud-scaled batches. Use Fork/Join inside a worker for sub-task parallelism; use Master-Worker for cross-node durability and independent scaling of workers.

---

### P094. Mediator

**Category:** Behavioral
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/mediator/)

**Short answer:** Mediator centralizes communication between colleagues so they do not reference each other directly—reducing N² coupling. Spring's event bus, MVC front controller, and chat room examples fit. It hurts when the mediator becomes a god object owning all business rules.

#### Scenario (interview)
**Situation:** A trade booking screen has `OrderForm`, `RiskPanel`, `ComplianceChecklist`, and `PricingWidget` each calling the others directly. Adding a sanctions check requires editing four classes; QA finds regression loops (price update triggers risk which triggers price).
**What they're testing:** Decoupling UI/workflow coordination without an omnibus service class.
**Model answer:** I'd introduce a `BookingSessionMediator` (or Spring `@Controller` orchestration layer) that owns workflow state transitions. Widgets emit intents: `OnSymbolChanged`, `OnQuantityChanged`—they never call sibling widgets. Mediator invokes domain services (`RiskService`, `ComplianceService`, `PricingService`) and publishes view updates via a single DTO snapshot. For backend symmetry, an application service plays mediator between aggregates—domain objects don't ping each other across bounded contexts. I'd keep mediators thin: no SQL, no pricing formulas—only coordination and mapping. Guard against god-object drift with ArchUnit: UI components must not depend on each other. If workflow grows complex, promote to a state machine (Spring Statemachine or explicit enum transitions) where the mediator delegates transitions. Trade-off: one place to debug; mitigate with unit tests per transition.

#### What it is
An object encapsulating how a set of objects interact; colleagues communicate only through the mediator.

#### When to use / when NOT
- **Use:** Many-to-many interaction webs (UI dashboards, wizard flows, chat rooms).
- **Use:** You need to change interaction rules without touching every colleague.
- **NOT:** Simple two-object callbacks—direct reference is clearer.
- **NOT:** Mediator accumulates domain logic—extract to domain services.

#### Java / Spring example
```java
@Component
class BookingMediator {
  BookingViewModel onEvent(BookingEvent e, BookingViewModel vm) {
    return switch (e) {
      case SymbolChanged s -> vm.withPrice(pricing.quote(s.symbol()));
      case QuantityChanged q -> vm.withRisk(risk.assess(vm));
    };
  }
}
```

#### Common mistakes
- Mediator with 2,000-line switch statements—sign to extract state machine.
- Colleagues still reaching around mediator via static singletons.
- Confusing Mediator with Facade—Facade simplifies subsystem API; Mediator manages bidirectional collaboration.

#### Follow-up (with answer)
**Q:** Mediator vs Observer?
**A:** Observer: subject notifies dependents of state changes—often one-to-many broadcast. Mediator: all parties send messages through a hub that may apply routing rules and may not broadcast everything. You can combine them: mediator receives colleague events and selectively notifies others (mediator uses observer internally). In Spring, `ApplicationEventPublisher` is observer-flavored; an `@Controller` orchestrating multiple `@Service` calls is mediator-flavored application layer.

---

### P095. Memento

**Category:** Behavioral
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/memento/)

**Short answer:** Memento captures an object's internal state externally so it can be restored later without breaking encapsulation. Undo stacks, transactional drafts, and game saves use it. It hurts when snapshots are huge, frequent, or stored without versioning/migration strategy.

#### Scenario (interview)
**Situation:** A loan origination wizard lets officers edit 12 sections across days. Users complain that "Save draft" sometimes loses co-borrower data after a deploy changed field names.
**What they're testing:** Encapsulated snapshots, caretaker separation, and schema evolution.
**Model answer:** I'd model each wizard session with a `LoanApplicationOriginator` that produces immutable `LoanApplicationMemento` snapshots containing only serializable state—no services or EntityManager references. A `DraftCaretaker` persists mementos to DB or Redis with `schemaVersion` and `userId`. Restore validates version: if deploy bumped schema, run a migration function on memento JSON before rehydrating. Snapshots are deep copies of value objects—never JPA entities in memento (lazy-loading surprises). Limit history to last N saves to control storage. For undo within a session, stack mementos in memory. Expose narrow interface: originator creates/restores; caretaker stores; clients never mutate memento internals. Audit trail: each memento gets hash + timestamp. I'd add integration test: save draft on version 3, deploy version 4 migrator, restore succeeds. Anti-pattern: cloning entire Hibernate session as "memento."

#### What it is
Three roles: Originator creates/restores from memento; Memento stores state; Caretaker holds mementos without inspecting internals.

#### When to use / when NOT
- **Use:** Undo/redo, draft autosave, simulation rollback.
- **Use:** State reconstruction must not expose internal invariants.
- **NOT:** Full DB entity versioning—use event sourcing or audit tables instead.
- **NOT:** Massive object graphs snapshotted every keystroke.

#### Java / Spring example
```java
record LoanMemento(int schemaVersion, String jsonPayload) {}
class LoanOriginator {
  LoanMemento save() { return new LoanMemento(4, mapper.writeValueAsString(state)); }
  void restore(LoanMemento m) { state = mapper.readValue(m.jsonPayload(), State.class); }
}
```

#### Common mistakes
- Memento holding live mutable references shared with originator.
- No version field—deploy breaks restore silently.
- Caretaker exposing memento internals to UI layer.

#### Follow-up (with answer)
**Q:** Memento vs Command for undo?
**A:** Command stores the operation (execute/undo methods)—memory efficient when undo is inverse of discrete commands. Memento stores full state snapshot—simpler when operations are not easily invertible or state is small. Hybrid: Command pattern with memento captured only at checkpoints. For collaborative editing, operational transform/CRDT beats naive memento stacking.

---

### P096. Metadata Mapping

**Category:** Enterprise / Structural
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/metadata-mapping/)

**Short answer:** Metadata Mapping externalizes object-relational mapping rules (tables, columns, relationships) into metadata descriptors rather than scattering annotations or XML blindly. Hibernate's `Metadata` API and Spring Data's mapping layer embody this. It hurts when metadata duplicates source-of-truth or lacks validation at build time.

#### Scenario (interview)
**Situation:** A multi-tenant SaaS supports custom fields per tenant. Engineers add `@Column` on entity subclasses per tenant; schema migrations conflict and Hibernate startup fails in prod for tenant 47.
**What they're testing:** Separating mapping metadata from entity classes for dynamic schemas.
**Model answer:** I'd stop annotating tenant-specific columns on shared entities. Introduce a metadata mapping layer: core `Customer` entity maps fixed columns; tenant extensions described in a `TenantFieldDefinition` table (name, type, constraints). A `MetadataMappingRegistry` builds runtime mapping fragments or uses JSON/JSONB columns with validated schemas. For reporting, materialized views per heavy tenant rather than dynamic DDL. Build-time: validate metadata JSON with JSON Schema in CI. Runtime: cache compiled mapping per tenant with TTL and eviction on admin change. Hibernate 6 programmatic mapping or Spring Data JDBC with explicit `RowMapper` may be simpler than dynamic JPA entities. Migration strategy: additive metadata only; never drop tenant field without archive job. Document that metadata mapping trades flexibility for operational complexity—monitor query plans when JSON predicates explode.

#### What it is
Mapping between domain objects and persistence structures is defined as data/metadata, enabling generic engines to interpret and apply it.

#### When to use / when NOT
- **Use:** Dynamic schemas, code generators, multi-tenant custom attributes.
- **Use:** Same persistence engine serves many mapping variants.
- **NOT:** Stable schema with ten entities—`@Entity` annotations suffice.
- **NOT:** Metadata edited in prod without validation pipeline.

#### Java / Spring example
```java
// Hibernate MetadataSources programmatic mapping
Metadata metadata = new MetadataSources(cfg)
    .addAnnotatedClass(Customer.class)
    .getMetadataBuilder()
    .applyTenantMapping(tenantId, extensionDefs)
    .build();
```

#### Common mistakes
- Duplicating mapping in annotations AND XML AND metadata tables.
- Dynamic SQL without index strategy—full table scans on JSON paths.
- No cache invalidation when tenant metadata changes.

#### Follow-up (with answer)
**Q:** Metadata Mapping vs Data Mapper pattern?
**A:** Data Mapper (Fowler) is the role: separate mapper objects translate entity ↔ row. Metadata Mapping is how those mappers get their rules—external descriptors rather than hard-coded field lists. Hibernate combines both: `Session` is mapper engine; annotations/`hbm.xml`/programmatic metadata supply rules. Custom SaaS often needs metadata-driven mappers because rules change without redeploy.

---

### P097. Microservices Aggregator

**Category:** Microservices / Architectural
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/microservices-aggregator/)

**Short answer:** An aggregator service calls multiple downstream microservices and combines responses into one composite DTO for clients—often behind API Gateway. It reduces client chattiness but hurts when it becomes a synchronous fan-out bottleneck without timeouts, partial failure handling, or caching.

#### Scenario (interview)
**Situation:** Mobile app product detail page needs price, inventory, reviews, and recommendations from four services. Client orchestration causes four round trips on 3G; p95 latency is 2.8s with cascading failures when inventory is slow.
**What they're testing:** Server-side aggregation, resilience, and graceful degradation.
**Model answer:** I'd build a `ProductDetailAggregator` behind the API Gateway—not in the mobile app. Single `/products/{id}/detail` endpoint fan-outs in parallel via `CompletableFuture` or WebClient with bounded timeouts (300ms inventory, 200ms reviews). Use circuit breakers per dependency; return partial payload with `inventoryStatus: UNKNOWN` rather than 500 when inventory fails—business decides if page is sellable. Cache stable slices (reviews) with short TTL; never cache price/inventory together without version keys. Propagate `traceparent` and `X-Tenant-Id` on all calls. Consider GraphQL only if clients need field selection; otherwise REST aggregator is simpler to operate. Load test aggregator, not each service in isolation—thread pool exhaustion shows up here first. Anti-pattern: aggregator writing to other services' databases to "speed up" reads.

#### What it is
A dedicated service (or gateway route handler) that invokes multiple microservices and merges their data into a unified response.

#### When to use / when NOT
- **Use:** Mobile/BFF needs one view model from many sources.
- **Use:** You want to hide service topology churn from clients.
- **NOT:** Simple CRUD from one bounded context.
- **NOT:** Aggregation requires distributed transactions—use saga/async composition instead.

#### Java / Spring example
```java
@GetMapping("/products/{id}/detail")
Mono<ProductDetail> detail(@PathVariable String id) {
  return Mono.zip(
      pricingClient.price(id).timeout(Duration.ofMillis(200)),
      inventoryClient.stock(id).timeout(Duration.ofMillis(300)),
      reviewsClient.summary(id).onErrorReturn(Reviews.empty())
  ).map(t -> ProductDetail.merge(t.getT1(), t.getT2(), t.getT3()));
}
```

#### Common mistakes
- Sequential REST calls multiplying latency.
- No fallback or partial response strategy—one slow dependency kills page.
- Aggregator owning business invariants that belong in domain services.

#### Follow-up (with answer)
**Q:** Aggregator vs API Gateway?
**A:** Gateway is cross-cutting entry point: routing, auth, rate limits, TLS termination. Aggregator is a business composition concern—may live as a route handler in gateway (BFF) or as separate `product-composite` service. Small teams often combine them; at scale, separate BFF per client channel (mobile vs. partner API) prevents one aggregation schema from constraining all clients.

---

### P098. Microservices API Gateway

**Category:** Microservices / Architectural
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/microservices-api-gateway/)

**Short answer:** API Gateway is the single north-south entry for clients—routing, auth, throttling, SSL, and sometimes aggregation. Spring Cloud Gateway and Kong are common. It hurts as a single point of failure, bottleneck, or god-config if every business rule lands in gateway filters.

#### Scenario (interview)
**Situation:** After splitting a monolith into 18 services, mobile clients hold 18 base URLs and JWT validation is duplicated in three services with drift—one service still accepts expired tokens.
**What they're testing:** Centralized edge concerns vs. pushing domain logic to gateway.
**Model answer:** I'd deploy Spring Cloud Gateway (or managed APIM) as the only public HTTPS endpoint. Route `/orders/**` → order-service via service discovery with path rewrite. JWT validation filter runs once at edge; downstream services trust mTLS or internal signed headers—not re-parse JWT unless zero-trust mandates. Add rate limiting per API key, request size limits, and WAF rules. Correlation ID injected at gateway and forwarded. Gateway stays dumb about business: no order pricing in filters. High availability: two gateway replicas minimum, health checks, config from GitOps. For local dev, same routes via docker-compose. Document break-glass: if gateway misroutes, feature flag to bypass specific route to previous monolith path. Monitor gateway p99 separately from services—CPU on TLS and JSON transforms adds up. BFF aggregation can live in gateway app module but keep packages separated.

#### What it is
A reverse proxy fronting microservices, providing unified client access and cross-cutting edge policies.

#### When to use / when NOT
- **Use:** Multiple internal services, external clients, need central auth/throttle/logging.
- **Use:** Hide internal topology and enable blue/green at routing layer.
- **NOT:** Two-service internal system behind VPN—YAGNI.
- **NOT:** Gateway implements domain workflows—becomes unmaintainable.

#### Java / Spring example
```yaml
# application.yml — Spring Cloud Gateway
spring.cloud.gateway.routes:
  - id: orders
    uri: lb://order-service
    predicates: [ Path=/api/orders/** ]
    filters: [ TokenRelay, RequestRateLimiter ]
```

#### Common mistakes
- Business logic in Groovy/SpEL gateway filters.
- No HA—gateway downtime kills entire platform perception.
- Terminating auth at gateway but services trust all internal traffic blindly.

#### Follow-up (with answer)
**Q:** API Gateway vs Service Mesh?
**A:** Gateway handles north-south (client → cluster) traffic policies at the edge. Service mesh (Istio/Linkerd) handles east-west (service → service) with sidecars: retries, mTLS, telemetry. They complement: gateway for external API surface; mesh for internal reliability. Duplicating same policies in both creates config drift—document ownership boundaries.

---

### P099. Microservices Client-Side UI Composition

**Category:** Microservices / UI
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/microservices-client-side-ui-composition/)

**Short answer:** Each microservice ships UI fragments (Web Components, Module Federation) composed in the browser—teams deploy UI independently. It enables autonomous squads but hurts with inconsistent design systems, performance waterfalls, and shared auth/session complexity.

#### Scenario (interview)
**Situation:** A bank portal merges account, loans, and investments modules owned by three teams. Monolithic SPA releases monthly; teams want independent deploys but the shell breaks when loan widget expects React 18 and investments still on React 17.
**What they're testing:** Module federation, contract testing, and shell orchestration.
**Model answer:** I'd adopt a shell app (single-spa or webpack Module Federation) loading remote entries at runtime from each team's CDN. Shared design system published as `@bank/ui-tokens` semver contract—breaking changes require major bump and shell compatibility matrix. Each micro-frontend exposes a mount contract: `{ mount(el, props), unmount }` with props for locale, auth token, theme. Shell handles routing, SSO, and global error boundary—not business data joins. Cross-widget communication via custom events or lightweight pub/sub bus, not direct imports between remotes. Performance budget: shell loads skeleton in 200ms; remotes lazy-load on route. CI contract tests: shell integration against pinned remote versions in staging before prod promotion. Fallback: if remote fails, show degraded card with link to legacy page. NOT client-side composition for SEO-critical marketing pages—SSR shell may be required.

#### What it is
Front-end architecture where independently deployable UI modules are assembled client-side into a cohesive application experience.

#### When to use / when NOT
- **Use:** Large org, many teams, independent release cadence for UI slices.
- **Use:** Clear bounded contexts map to UI widgets.
- **NOT:** Small product with one frontend team—monolith SPA is simpler.
- **NOT:** Heavy cross-widget transactional flows without server orchestration.

#### Java / Spring example
```javascript
// Shell — Module Federation host
const Loans = await import('loansApp/LoanWidget');
Loans.mount(document.getElementById('loans'), { token, locale });
// Each remote built/deployed independently; API via same gateway
```

#### Common mistakes
- Duplicating React/Vue in every remote—inflates bundle size 3×.
- No version compatibility matrix—prod shell loads incompatible remote.
- Micro-frontends calling each other's APIs directly bypassing gateway policies.

#### Follow-up (with answer)
**Q:** Client-side composition vs BFF aggregation?
**A:** Client-side composition splits UI ownership; browser may still call multiple APIs (waterfall risk). BFF/server aggregator reduces client calls but centralizes backend team. Common hybrid: shell + federated UI widgets each calling their own service through gateway, with aggregator only for tightly coupled read models (product detail). Choose based on team topology and latency budget—not fashion.

---

### P100. Microservices Distributed Tracing

**Category:** Microservices / Observability
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/microservices-distributed-tracing/)

**Short answer:** Distributed tracing propagates trace/span IDs across services to reconstruct request paths (OpenTelemetry, Zipkin, Jaeger). Essential for debugging latency in microservices; hurts when sampling is wrong, baggage is abused, or PII lands in span attributes.

#### Scenario (interview)
**Situation:** Checkout p99 regressed from 800ms to 2.1s after adding fraud and loyalty services. Logs exist per service but on-call cannot correlate; support tickets cite "random slowness."
**What they're testing:** OpenTelemetry propagation, span design, and operational use of traces.
**Model answer:** I'd instrument all services with OpenTelemetry SDK—auto-instrument Spring Web, WebClient, JDBC, Kafka. Propagate W3C `traceparent` from API Gateway through async messages (inject into Kafka headers). Each outbound call becomes a child span; name spans by operation (`POST /payments/authorize`) not class names. Enable tail-based sampling in prod (keep errors and slow traces) while head-sample 10% success paths. Dashboard: trace waterfall showing fraud service adds 900ms on 30% of checkouts—root cause. Add span attributes: `tenant.id`, `payment.method`—never PAN or email. Link traces to structured logs via `trace_id` in log MDC. Runbooks: on-call searches Jaeger by `checkout.trace` facet. Load test verifies tracing overhead <3%. Anti-pattern: enabling 100% trace export to expensive backend without retention policy.

#### What it is
End-to-end visibility mechanism assigning trace IDs to requests and span IDs to operations, exported to a tracing backend.

#### When to use / when NOT
- **Use:** Any multi-hop synchronous/async microservice flow.
- **Use:** Latency SLO debugging and dependency mapping.
- **NOT:** Single monolith with one process—simple logging may suffice initially.
- **NOT:** Without log correlation and sampling strategy—cost and noise explode.

#### Java / Spring example
```xml
<!-- micrometer-tracing-bridge-otel + opentelemetry-exporter-otlp -->
```
```java
// MDC auto-populated; manual span
span.setAttribute("order.id", orderId);
```

#### Common mistakes
- Broken context propagation across `@Async` or reactive threads.
- Span per DAO row—trace storage explosion.
- Storing PII in span tags violating compliance.

#### Follow-up (with answer)
**Q:** Tracing vs logging vs metrics?
**A:** Metrics: aggregated counters/histograms (request rate, p99)—cheap, alert-friendly. Logs: discrete events with context—great for errors, expensive at high volume. Traces: single request journey across services—best for latency decomposition. Mature ops uses all three linked by trace_id. Golden signals (latency, traffic, errors, saturation) come from metrics; traces explain which hop saturated.

---

### P101. Microservices Idempotent Consumer

**Category:** Microservices / Enterprise
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/microservices-idempotent-consumer/)

**Short answer:** Idempotent consumers process the same message multiple times without duplicate side effects—critical with at-least-once delivery (Kafka, SQS). Store processed message IDs or use natural idempotency keys. It hurts when dedup store is unbounded, TTL too short, or business logic is inherently non-idempotent without compensation.

#### Scenario (interview)
**Situation:** `PaymentCaptured` events from Kafka occasionally redeliver after consumer rebalance. Finance reports duplicate shipment triggers—two labels for one order—costing $40k/month in shipping.
**What they're testing:** At-least-once semantics, dedup strategy, and outbox alignment.
**Model answer:** I'd assume at-least-once delivery always. Every consumer records `(eventId, consumerGroup)` in a processed_events table with unique constraint before side effects, or uses Redis SETNX with 7-day TTL for high volume. Business operations keyed by idempotency key: `shipment.create(orderId, captureEventId)`—second call returns existing label ID. Wrap DB writes in transaction: insert idempotency row + insert shipment row together; duplicate insert fails fast. For external APIs (carrier), pass idempotency header. Monitor duplicate detection rate—spike indicates broker or consumer bug. Pair with transactional outbox on producer side so events aren't lost. NOT exactly-once Kafka myth without idempotent design. Load test rebalance during peak. Document that idempotency TTL must exceed max redelivery window.

#### What it is
Message consumer designed so repeated processing of the same message produces the same system state as processing once.

#### When to use / when NOT
- **Use:** Kafka, Rabbit, SQS with at-least-once or redelivery.
- **Use:** Side effects: money movement, inventory, emails, webhooks.
- **NOT:** Pure read-only projections where duplicates only waste CPU—still often dedup for cost.
- **NOT:** Without durable dedup store—memory-only dedup fails on restart.

#### Java / Spring example
```java
@KafkaListener(topics = "payment-captured")
@Transactional
void on(PaymentCaptured e) {
  if (processedRepo.existsById(e.eventId())) return;
  processedRepo.save(new ProcessedEvent(e.eventId()));
  shipmentService.createIfAbsent(e.orderId(), e.eventId());
}
```

#### Common mistakes
- Check-then-act race without unique DB constraint.
- Idempotency key = timestamp—collisions and misses.
- Side effect before dedup record—crash causes duplicate.

#### Follow-up (with answer)
**Q:** Idempotent consumer vs saga?
**A:** Idempotent consumer prevents duplicate execution of the same step when messages redeliver. Saga orchestrates multi-step distributed transactions with compensations when a later step fails. Use both: saga defines workflow; each step handler is idempotent. Idempotency alone does not rollback a completed payment if inventory fails—you need compensating events.

---

### P102. Microservices Log Aggregation

**Category:** Microservices / Observability
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/microservices-log-aggregation/)

**Short answer:** Centralize logs from all services into a searchable platform (ELK, Loki, CloudWatch)—correlate by trace/request ID. Essential at scale; hurts with unstructured logs, missing correlation IDs, or hot indices without retention tiers.

#### Scenario (interview)
**Situation:** During a Sev-1, engineers SSH into 40 pods grep-ing logs; incident takes 4 hours to find root cause—a misconfigured feature flag in one AZ only.
**What they're testing:** Structured logging, correlation, and operational query patterns.
**Model answer:** I'd mandate JSON structured logs to stdout—container platform ships to OpenSearch/Loki. Every log line includes `trace_id`, `span_id`, `service`, `env`, `tenant_id` via MDC populated at gateway. Use log levels discipline: INFO for business milestones, DEBUG off in prod except scoped dynamic toggle. Index hot logs 7 days, warm 30, cold S3 archive for compliance. Dashboards pre-built: error rate by service, flag evaluation logs. On-call runbook: search `trace_id:"abc"` across all indexes—single pane. Avoid logging secrets/PII; hash user IDs. Cost control: sampling DEBUG, drop health-check noise at collector. Spring Boot: Logback JSON encoder + Micrometer tracing bridge. Validate in CI that new code doesn't log raw request bodies. Incident retro: without aggregation, MTTR scales linearly with pod count—unacceptable.

#### What it is
Collecting, transporting, indexing, and querying distributed service logs in a central observability stack.

#### When to use / when NOT
- **Use:** More than a handful of deployable units or ephemeral containers.
- **Use:** Compliance audit trails across services.
- **NOT:** Local dev single process—tail one file is fine.
- **NOT:** Without correlation strategy—central pile of text worse than grep on one box.

#### Java / Spring example
```xml
<!-- logstash-logback-encoder -->
```
```java
log.info("payment authorized orderId={} amount={}", orderId, amount);
// MDC: traceId from ObservationRegistry
```

#### Common mistakes
- String-concatenated logs impossible to query (`"User " + user + " paid"`).
- Different timestamp formats/timezones across services.
- Logging full payloads including PCI data.

#### Follow-up (with answer)
**Q:** Log aggregation vs distributed tracing?
**A:** Logs answer "what happened" with detail and stack traces; traces answer "where time went" across hops. Link them with shared trace_id in log MDC. Use traces for latency incidents; logs for logic errors and audit. Neither replaces metrics for alerting—combine all three in incident workflow.

---

### P103. Microservices Messaging

**Category:** Microservices / Architectural
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/microservices-messaging/)

**Short answer:** Async message brokers decouple services—publishers emit events/commands; consumers react at their pace. Enables resilience and scale but hurts when used for synchronous request/response disguised as messaging, ordering is assumed without keys, or schemas evolve without compatibility rules.

#### Scenario (interview)
**Situation:** Order service synchronously REST-calls inventory, payment, and notification during checkout—cascade failures when notification service is down block revenue.
**What they're testing:** Event-driven decoupling, failure isolation, and consistency trade-offs.
**Model answer:** I'd refactor checkout to command/event messaging. Synchronous path: validate cart + reserve payment authorization only. Publish `OrderPlaced` to Kafka after DB commit (transactional outbox). Inventory consumer reserves stock; on failure publishes `OrderRejected` triggering payment void saga. Notification consumer sends email—lag acceptable. Use Avro/Protobuf with Schema Registry; consumers backward-compatible. Partition by `orderId` for ordering per order. DLQ for poison messages with alert. Document eventual consistency: UI shows "processing" until `OrderConfirmed`. NOT messaging for read-your-writes queries—use sync read API or CQRS projection. Monitor consumer lag and rebalance storms. Spring: `@KafkaListener` + `KafkaTemplate` + outbox table polled by Debezium or custom scheduler.

#### What it is
Inter-service communication through durable asynchronous messages rather than direct synchronous HTTP coupling.

#### When to use / when NOT
- **Use:** Notify many subscribers, buffer load spikes, long-running workflows.
- **Use:** Teams need independent deploy and failure domains.
- **NOT:** Simple query/response needing immediate answer—use HTTP/gRPC.
- **NOT:** Distributed monolith—all logic in one giant consumer chain.

#### Java / Spring example
```java
@Transactional
void placeOrder(Order o) {
  orderRepo.save(o);
  outboxRepo.save(OutboxEvent.orderPlaced(o));
}
@Scheduled void publishOutbox() { /* relay to Kafka */ }
```

#### Common mistakes
- Dual writes: DB commit then Kafka send without outbox—lost messages.
- Chatty request-reply over Kafka mimicking REST with worse ergonomics.
- No schema evolution plan—producer deploy breaks consumers.

#### Follow-up (with answer)
**Q:** Messaging vs event sourcing?
**A:** Messaging is transport between services—events may be ephemeral notifications. Event sourcing stores state as immutable event log—the event store is system of record. You often use messaging to propagate events sourced from one aggregate to others. ES without idempotent consumers and projection rebuild strategy is painful ops.

---

### P104. Microservices Self-Registration

**Category:** Microservices / Architectural
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/microservices-self-registration/)

**Short answer:** Services register their network location with a discovery registry (Eureka, Consul) on startup—clients resolve logical names to instances. Enables dynamic scaling but hurts when registry is SPOF, stale registrations linger, or Kubernetes DNS already suffices.

#### Scenario (interview)
**Situation:** Hardcoded service URLs in 12 repos break every blue/green deploy; staging accidentally hits prod payment service after IP reuse.
**What they're testing:** Service discovery, health checks, and config hygiene.
**Model answer:** I'd enable self-registration with Spring Cloud `@EnableDiscoveryClient` on each service and Eureka/Consul cluster in HA. On startup, service registers `PAYMENT-SERVICE` with host, port, health URL; sends heartbeats; deregisters on graceful shutdown. Consumers use `@LoadBalanced RestTemplate` or OpenFeign `@FeignClient(name="payment-service")`—no URLs in code. Health actuator `/actuator/health` must reflect readiness—not just JVM up. In Kubernetes-native stacks, prefer K8s Services + DNS over Eureka unless multi-cluster discovery needed. Stale instance handling: shorten lease; clients retry on connection failure. CI blocks `http://10.` literals in source. Migration: register monolith alias during strangler fig. Monitor registry quorum and registration rate spikes during deploys.

#### What it is
Microservice announces itself to a service registry at startup; other services discover instances dynamically.

#### When to use / when NOT
- **Use:** Dynamic IPs/ports, frequent scaling, cloud VMs without stable DNS.
- **Use:** Client-side load balancing across instances.
- **NOT:** K8s with stable ClusterIP and service mesh—native DNS often enough.
- **NOT:** Single static instance forever—discovery adds moving parts.

#### Java / Spring example
```java
@SpringBootApplication
@EnableDiscoveryClient
public class PaymentApplication { }

@FeignClient(name = "inventory-service")
interface InventoryClient { @GetMapping("/stock/{sku}") int stock(@PathVariable String sku); }
```

#### Common mistakes
- Registering before app ready—traffic routed to starting instance.
- No graceful shutdown deregister—connection errors during deploy.
- Eureka single node in prod—registry outage blinds cluster.

#### Follow-up (with answer)
**Q:** Self-registration vs third-party registration (K8s)?
**A:** Self-registration: app pushes metadata to registry (Eureka client). Third-party: platform (K8s controller) registers on app's behalf. K8s + CoreDNS is third-party model—less app code, fits container lifecycle. Eureka self-registration shines on VM/bare-metal Spring Cloud estates. Don't run both blindly—pick one discovery source of truth.

---

### P105. Model-View-Controller (MVC)

**Category:** UI / Architectural
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/model-view-controller/)

**Short answer:** MVC separates domain state (Model), presentation (View), and input handling (Controller). Spring MVC maps HTTP to controllers returning views or JSON. It hurts when controllers swell with business logic or "Model" becomes anemic DTO bag with SQL in controllers.

#### Scenario (interview)
**Situation:** A Spring `@RestController` for claims grows to 2,400 lines—SQL, validation, PDF generation, and email in one class. Unit tests require `@WebMvcTest` booting half the context.
**What they're testing:** Layer boundaries and where business logic lives.
**Model answer:** I'd enforce MVC boundaries strictly. Controller: HTTP concerns only—parse request, authorize, call application service, map to response DTO, set status codes. Model: domain entities + domain services inside application layer—not JSP anymore but same idea. View: JSON via Jackson or Thymeleaf for server-rendered pages. Extract `ClaimSubmissionService` with transactional boundaries; controller method under 30 lines. Validation: `@Valid` on request DTO at edge; domain invariants in entity methods. For read models, separate query service (CQRS-lite) so controllers don't compose SQL. ArchUnit rule: controllers must not depend on repositories directly. Refactor incrementally: extract one endpoint at a time with characterization tests. MVC is not an excuse to skip hexagonal ports—controller is adapter inbound.

#### What it is
Presentation pattern dividing responsibilities: Model holds data/logic, View renders, Controller mediates user input and updates Model/View.

#### When to use / when NOT
- **Use:** Web apps and APIs needing clear request handling separation.
- **Use:** Server-side rendering or REST with Spring MVC/DispatcherServlet.
- **NOT:** Rich SPA where server controller is thin static file server only—client MVC matters more.
- **NOT:** Fat controllers—symptom of missing application layer.

#### Java / Spring example
```java
@RestController
@RequestMapping("/claims")
class ClaimController {
  private final ClaimAppService claims;
  @PostMapping
  ResponseEntity<ClaimResponse> submit(@Valid @RequestBody SubmitClaimRequest req) {
    return ResponseEntity.status(CREATED).body(ClaimResponse.from(claims.submit(req)));
  }
}
```

#### Common mistakes
- Controller `@Transactional` with repository calls—logic trapped in web layer.
- Using entity as JSON response—lazy-load exceptions and coupling.
- Confusing Spring MVC with domain Model in DDD—name collision causes design drift.

#### Follow-up (with answer)
**Q:** MVC vs layered architecture in Spring?
**A:** MVC addresses presentation interaction; layered (controller → service → repository) addresses enterprise separation. Spring apps combine both: MVC controllers are inbound adapters; `@Service` is application layer; `@Repository` is persistence. Clean/hexagonal naming replaces "Model" with domain + use cases but same separation intent.

---

### P106. Model-View-Intent (MVI)

**Category:** UI / Behavioral
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/model-view-intent/)

**Short answer:** MVI unifies state in a single immutable ViewState; Intents (user actions) reduce to new state via pure reducer-like functions—popular in Android/Kotlin flows. It hurts with boilerplate for simple screens or when side effects are scattered outside the effect handler.

#### Scenario (interview)
**Situation:** An Android trading app built with MVP shows race conditions—price tick updates UI while user submits order, showing stale confirmation.
**What they're testing:** Unidirectional data flow and single source of truth.
**Model answer:** I'd migrate critical flows to MVI. Define `TradingState` immutable data class: `{ quote, orderDraft, submissionStatus, error }`. User actions sealed as `Intent`: `RefreshQuote`, `SetQuantity`, `SubmitOrder`. Reducer `(state, intent) -> state` is pure; async work in `Effect` channel—repository calls emit `Intent.ResultLoaded`. UI renders only from latest `StateFlow`. Single pipeline prevents stale UI: submit uses quote version embedded in state snapshot. Side effects isolated in ViewModel scope with structured concurrency. Test reducer without Robolectric. For Spring-backed REST, mobile MVI still applies on client; server remains stateless. Don't MVI a settings toggle screen—MVP or MVVM sufficient. Document state machine for `submissionStatus`: Idle → Submitting → Success/Error with no illegal transitions.

#### What it is
Unidirectional UI architecture: Intent → Model reduces state → View renders state; loop repeats.

#### When to use / when NOT
- **Use:** Complex UI with concurrent updates, need reproducible state transitions.
- **Use:** Android/Kotlin Multiplatform with reactive streams.
- **NOT:** Simple forms with minimal state—overhead exceeds benefit.
- **NOT:** Reducer performs I/O—keep pure; effects separate.

#### Java / Spring example
```kotlin
// Kotlin Android — concept applies client-side
data class State(val items: List<Item>, val loading: Boolean)
fun reduce(state: State, intent: Intent): State = when (intent) {
  is Load -> state.copy(loading = true)
  is Loaded -> state.copy(items = intent.items, loading = false)
}
```

#### Common mistakes
- Mutating state in View layer bypassing reducer.
- Giant reducer switch mixing unrelated features—split stores.
- No distinction between one-time events (snackbar) and state—use channel/effect.

#### Follow-up (with answer)
**Q:** MVI vs MVVM?
**A:** MVVM: View binds to ViewModel exposing observable fields—multiple mutable streams possible. MVI: single immutable state stream; intents are explicit events. MVI enforces stricter unidirectional flow—better for complex concurrent UI. MVVM faster to ship for CRUD screens. Both beat MVP on Android when using StateFlow/LiveData correctly.

---

### P107. Model-View-Presenter (MVP)

**Category:** UI / Behavioral
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/model-view-presenter/)

**Short answer:** MVP: View is passive; Presenter orchestrates Model and updates View through interface—common in legacy Android/Swing. Presenter is testable without UI but hurts when Presenter becomes god class or holds lifecycle-aware references causing leaks.

#### Scenario (interview)
**Situation:** Swing desktop app for lab instruments—technicians report UI freezes during calibration; profiling shows EDT blocked by JDBC in view click handlers.
**What they're testing:** Passive view, presenter threading, testability.
**Model answer:** I'd extract `CalibrationPresenter` implementing `CalibrationView` interface callbacks. View only renders: `showProgress()`, `showResult(CalibrationDto)`—no SQL. Presenter loads data on background executor, marshals results to EDT via `SwingUtilities.invokeLater`. Model layer wraps instrument SDK + repository. Unit test presenter with mock view verifying call order. Presenter lifecycle bound to view window—weak references or explicit detach on close to prevent leaks. For new modules, consider MVVM/MVI; MVP fits passive Swing views well. Anti-pattern: presenter importing `JTable` directly. Instrumentation: assert no JDBC on EDT thread in tests. Gradual refactor: move one screen at a time; keep presenter thin—delegate domain rules to service.

#### What it is
UI pattern where Presenter contains presentation logic; View implements passive interface; Model provides data/domain operations.

#### When to use / when NOT
- **Use:** Passive views (Swing, early Android), heavy presenter unit testing.
- **Use:** Clear mock boundary for view in tests.
- **NOT:** Modern Android with ViewBinding/Lifecycle—MVVM/MVI preferred.
- **NOT:** Presenter knows widget types—breaks passive view.

#### Java / Spring example
```java
class OrderPresenter {
  private final OrderView view;
  private final OrderService model;
  void onSubmit(String id) {
    model.find(id).ifPresentOrElse(view::showOrder, () -> view.showError("Not found"));
  }
}
interface OrderView { void showOrder(Order o); void showError(String msg); }
```

#### Common mistakes
- Presenter holding Activity/Fragment reference after destroy.
- Business rules duplicated in presenter and service.
- View calling model directly—breaks MVP triangle.

#### Follow-up (with answer)
**Q:** MVP vs MVC in web apps?
**A:** Web MVC: controller often thin, view is template, model server-side. MVP: presenter explicitly drives passive view—common in desktop/mobile. Spring `@Controller` is MVC terminology but many teams treat it as MVP-like when presenter logic sits in `@Service` and view is Thymeleaf/JSON. Key test: can you unit test presentation logic without servlet container?

---

### P108. Model-View-ViewModel (MVVM)

**Category:** UI / Behavioral
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/model-view-viewmodel/)

**Short answer:** ViewModel exposes observable state/commands for View binding—data binding syncs UI (WPF, Android, Vue). Separates presentation state from View lifecycle. Hurts when ViewModel knows View APIs, two-way binding creates debug hell, or server-side MVVM confused with client pattern.

#### Scenario (interview)
**Situation:** WPF ops dashboard binds 50 properties; null reference exceptions in XAML code-behind; QA cannot reproduce—race between async load and tab switch.
**What they're testing:** Observable state, binding, command pattern, lifecycle.
**Model answer:** I'd move all presentation state to `DashboardViewModel` implementing `INotifyPropertyChanged` or using CommunityToolkit.Mvvm `[ObservableProperty]`. View XAML binds `{Binding ActiveAlerts}` with zero code-behind except InitializeComponent. Async loads update ViewModel on dispatcher; `IsBusy` gates UI. Commands (`RelayCommand`) trigger service calls—no click handlers in View. ViewModel never references `TextBox` types. Unit test ViewModel with mock `IAlertService`. For partial updates, expose immutable snapshot objects to reduce spurious change notifications. Server-side Spring app: MVVM term usually applies to frontend (Angular/Vue); backend exposes ViewModels as DTOs shaped for UI—not entities. Document binding errors fail at design time where possible. If bindings spaghetti, step toward MVI single state object.

#### What it is
ViewModel mediates between Model and View, exposing bindable properties and commands; View observes ViewModel.

#### When to use / when NOT
- **Use:** Data-binding frameworks (WPF, Android Jetpack, Vue reactive).
- **Use:** UI state survives rotation/config changes (Android ViewModel scope).
- **NOT:** Simple server-rendered forms without client binding framework.
- **NOT:** ViewModel imports UI toolkit classes.

#### Java / Spring example
```kotlin
// Android Jetpack ViewModel
class AccountViewModel(repo: AccountRepository) : ViewModel() {
  val balance = repo.balanceFlow().stateIn(viewModelScope, WhileSubscribed(5000), 0.0)
}
```

#### Common mistakes
- Logic in XAML/code-behind bypassing ViewModel.
- Two-way binding on fields user didn't edit—unexpected overwrites.
- ViewModel doing navigation without abstraction—hard to test.

#### Follow-up (with answer)
**Q:** MVVM on server (Spring) — valid?
**A:** Strict MVVM is UI pattern. Spring teams say "ViewModel" for response DTOs tailored to screens—that's presentation DTO or BFF output, not classic MVVM binding. Acceptable naming if team distinguishes from domain model. True MVVM requires observable binding on client; server returns JSON state snapshots.

---

### P109. Monad

**Category:** Behavioral / Functional
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/monad/)

**Short answer:** A monad wraps values with context (Optional, CompletableFuture, Stream) and flatMaps computations without nested null/async hell. In Java, `Optional`, `Stream`, and reactive types embody monadic bind. It hurts when used for field types in DTOs, forced everywhere for style, or confused with "must use functional programming."

#### Scenario (interview)
**Situation:** Payment pipeline nests five `if (x != null)` blocks across async HTTP calls; junior dev adds `Optional.of(null)` NPE in prod.
**What they're testing:** Composition of nullable/async steps without pyramid of doom.
**Model answer:** I'd refactor the pipeline monadically using `CompletableFuture` composition or Project Reactor `Mono`. Each step returns `Mono<PaymentResult>`; chain with `flatMap`—short-circuits on empty/error without null checks. For synchronous validation, `Optional` chain is fine internally but never expose `Optional` in REST DTOs (Jackson pain). Centralize error mapping in one `onErrorMap` to domain exceptions. Document that monad here means composable bind, not Haskell evangelism. Test each step with stubbed clients; integration test full chain. Avoid `Optional.get()` without `orElseThrow`. If team unfamiliar with reactive, `CompletableFuture` may be gentler than full WebFlux migration. Measure thread usage—blocking inside `flatMap` on event loop is fatal.

#### What it is
Design pattern/type class structuring sequential computations with context—bind (flatMap) chains steps while preserving context (presence, async, list, error).

#### When to use / when NOT
- **Use:** Chaining nullable, async, or error-prone steps cleanly.
- **Use:** Stream/Optional/Reactor already in stack.
- **NOT:** Every method returns `Optional` as parameter/field API smell.
- **NOT:** Team lacks reactive debugging skills—operational cost real.

#### Java / Spring example
```java
Mono<Receipt> flow = validate(req)
    .flatMap(this::authorize)
    .flatMap(this::capture)
    .flatMap(this::emitReceipt);
```

#### Common mistakes
- `Optional.of(null)` and `Optional.get()` without check.
- Blocking `.block()` in WebFlux request thread.
- Monadic chain without timeout on external calls—hangs forever.

#### Follow-up (with answer)
**Q:** Is Optional a monad in Java?
**A:** Optional implements monad-like `flatMap/map/filter` for presence context—it is not a general-purpose container for fields or collections. Use for return types representing absence; avoid Optional parameters and serialized JSON fields. CompletableFuture and Stream are more impactful monads in server Java for async and collection pipelines.

---

### P110. Money

**Category:** Enterprise / Domain
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/money/)

**Short answer:** Money pattern models amount + currency as value object—never use `double` for currency. Joda-Money, Moneta, or custom immutable type prevents rounding and FX bugs. Hurts when persisted as strings without scale rules or arithmetic mixes currencies silently.

#### Scenario (interview)
**Situation:** A billing service stores prices as `double`; month-end reconciliation shows $0.01 drift on 40k invoices and angry CFO; one bug added USD + EUR amounts returning 150.00 mystery total.
**What they're testing:** Value objects, scale, currency safety, persistence mapping.
**Model answer:** I'd introduce `Money` value object: immutable `(BigDecimal amount, Currency currency)` with scale 2 for USD/EUR per currency table. All arithmetic checks currency match or routes through `FxService` producing new Money. Never use binary floating point. Persist as `amount_minor_units BIGINT + currency_code CHAR(3)` or DECIMAL(19,4). Jackson serializer to string `"USD 12.34"` for API; never raw number without currency. Rounding mode explicit: HALF_UP for invoices, bankers for interest—document per domain. Unit tests: `0.1 + 0.2` equals `0.30` exactly. Migration: backfill DECIMAL columns; run parallel compare job flagging drift. Hibernate `@Embeddable MoneyEmbeddable`. Anti-pattern: `BigDecimal` scattered without currency tag—same class of bug.

#### What it is
Domain value object encapsulating monetary amount and currency with safe arithmetic and formatting rules.

#### When to use / when NOT
- **Use:** Any financial, billing, ledger, tax calculation.
- **Use:** Multi-currency systems with explicit conversion service.
- **NOT:** Scientific metrics unrelated to money—use Quantity with unit.
- **NOT:** `double` "just for display" that sneaks into totals.

#### Java / Spring example
```java
public record Money(BigDecimal amount, Currency currency) {
  public Money add(Money other) {
    if (!currency.equals(other.currency)) throw new CurrencyMismatchException();
    return new Money(amount.add(other.amount), currency);
  }
}
```

#### Common mistakes
- Storing FX rate without timestamp—disputes on historical amounts.
- JSON `{ "amount": 10.999 }` without scale normalization.
- Using float in JDBC and wondering about penny ghosts.

#### Follow-up (with answer)
**Q:** Money pattern vs Martin Fowler's Money (PoEAA)?
**A:** Same concept: Money as value object in domain layer, mapped to DB columns, never primitive obsession. Fowler adds integration with accounting patterns (ledger entries reference Money). In microservices, agree ISO currency codes and minor units across services—contract tests on Money JSON schema prevent incompatible payloads.

---

### P111. Monitor

**Category:** Concurrency
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/monitor/)

**Short answer:** Monitor synchronizes access to shared state—only one thread executes monitor methods at a time; `wait/notify` coordinate conditions. Java's `synchronized` methods and `ReentrantLock` + `Condition` implement monitors. Hurts when locks are held during I/O, nested lock ordering causes deadlock, or `wait` without loop re-check.

#### Scenario (interview)
**Situation:** A bounded in-memory job queue uses `ArrayList` with manual sync; under load, workers spin, lose notifications, and duplicate jobs process—inventory counts drift.
**What they're testing:** Intrinsic locks, condition queues, invariants, `while` not `if` around wait.
**Model answer:** I'd replace ad-hoc sync with a proper monitor object encapsulating queue state. Private lock + `Condition notEmpty/notFull`; producers `await(notFull)` when at capacity, consumers `await(notEmpty)` when empty—always in `while` loop re-checking condition after wakeup. Critical section only mutates queue structure—never call external HTTP inside synchronized block. Use `BlockingQueue` implementation (`LinkedBlockingQueue`) in production Java rather than hand-rolled monitor unless teaching. If custom monitor needed, document lock ordering across multiple monitors to prevent deadlock. Metrics: queue depth, wait time. Stress test verifies no lost signal under `notifyAll` storms. For distributed work, monitor pattern is in-process only—don't confuse with distributed lock (Redis). Java `synchronized` methods on `enqueue/dequeue` are monitor pattern simplified.

#### What it is
Concurrency pattern where an object exposes synchronized methods; lock + condition variables guard shared data invariants.

#### When to use / when NOT
- **Use:** In-process shared mutable structures (buffers, caches, connection pools internals).
- **Use:** Complex wait conditions beyond simple `BlockingQueue` API.
- **NOT:** Distributed coordination—use consensus/locks at infrastructure layer.
- **NOT:** Long I/O under lock—blocks all threads.

#### Java / Spring example
```java
class BoundedBuffer<T> {
  private final Queue<T> q = new ArrayDeque<>();
  private final ReentrantLock lock = new ReentrantLock();
  private final Condition notEmpty = lock.newCondition();
  void put(T item) throws InterruptedException {
    lock.lock();
    try { while (q.size() == CAP) notFull.await(); q.add(item); notEmpty.signal(); }
    finally { lock.unlock(); }
  }
}
```

#### Common mistakes
- `if (empty) wait()` instead of `while (empty) wait()`—spurious wakeup bugs.
- Calling `wait()` without holding lock—`IllegalMonitorStateException`.
- `notify()` when `notifyAll()` needed—missed wakeups.

#### Follow-up (with answer)
**Q:** Monitor vs Actor model?
**A:** Monitor: threads share memory, coordinate with locks—low overhead, risk of deadlock/races if misused. Actor: no shared mutable state; message passing serializes access per actor—scales across cores/machines but adds messaging overhead. Use monitors for high-performance in-JVM structures; actors (Akka, Pekko) for distributed agents with isolation.

---

### P112. Monolithic Architecture

**Category:** Architectural
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/monolithic-architecture/)

**Short answer:** Monolith deploys as single unit—shared process, DB, release cadence. Simplest ops and refactors until scale/org pain appears. Hurts when forced microservices prematurely or when monolith becomes unmodular big ball of mud without internal boundaries.

#### Scenario (interview)
**Situation:** Series B startup debates microservices after reading HN; 8 engineers, 50k DAU, one PostgreSQL. CTO wants 12 services before product-market fit.
**What they're testing:** When monolith is correct; modular monolith as middle path.
**Model answer:** I'd keep a deployable monolith with strict modular boundaries—Gradle modules or packages per bounded context, database schemas namespaced, no cross-module entity JPA relationships. Single Spring Boot jar, one CI pipeline, one rollback lever. Extract services only on evidence: independent scaling (CPU on search only), different SLO (payments isolation), or team autonomy blocking releases—not resume-driven architecture. Use feature flags and strangler fig when extraction time comes. Invest in observability and test pyramid inside monolith first—microservices multiply failure modes 10×. If deploy fear exists, fix CI/CD and module tests before splitting network. Document extraction triggers: sustained team >15 on same codebase, blast radius incidents, regulatory isolation need. Modular monolith beats distributed ball of mud.

#### What it is
System architecture where all components run in one application process/deployment artifact, typically sharing data stores.

#### When to use / when NOT
- **Use:** Small/medium teams, early product, strong consistency needs, simple ops.
- **Use:** Modular monolith with clear package boundaries for future extraction.
- **NOT:** Independent scaling of one hot component proves bottleneck on monolith CPU.
- **NOT:** Monolith excuse for no boundaries—still apply DDD modules.

#### Java / Spring example
```java
// Single Spring Boot app — modules by package
com.acme.orders.*   // no @Autowired of com.acme.billing internals
com.acme.billing.*
// shared-kernel only for IDs/events
```

#### Common mistakes
- Shared mutable database tables across domains—extraction impossible later.
- Microservices for 3-person team—ops tax kills velocity.
- No integration tests because "it's all one app"—regressions still ship.

#### Follow-up (with answer)
**Q:** Modular monolith vs microservices?
**A:** Modular monolith: one deploy, enforced module boundaries (ArchUnit), possibly single DB with schema separation. Microservices: separate deploy, network boundary, distributed data. Same domain modeling; different deployment topology. Extract when module boundary stable and operational benefit clear—not when code is messy (fix modularity first).

---

### P113. Monostate

**Category:** Creational
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/monostate/)

**Short answer:** Monostate: many instances share static/global state—behaviorally like singleton but typed as new objects. `java.lang.System` or logging context sometimes resemble this. Hurts with hidden global mutation, test pollution, and classloader issues in app servers.

#### Scenario (interview)
**Situation:** Developers instantiate `new TenantContext()` everywhere assuming isolation; all instances read same static `currentTenant` mutated by async requests—tenant A sees tenant B data in SaaS app.
**What they're testing:** Global state hazards vs explicit context propagation.
**Model answer:** I'd eliminate Monostate anti-pattern for tenant context. Replace static `currentTenant` with request-scoped bean or `ThreadLocal` cleared in filter finally block—or better, pass `TenantId` explicitly through service methods (explicit is better). For MDC logging, use scoped context with reactive `Context` in WebFlux. If legacy Monostate API must remain, document thread safety and forbid `@Async` without context propagation. Tests fail mysteriously when static state leaks order—use `@DirtiesContext` or ban static mutable fields via ArchUnit. Monostate acceptable for truly JVM-global constants (timezone data) with immutability. Spring `@Scope("request")` TenantContext is not Monostate—each request new instance with injected tenant from JWT. Incident fix: grep static mutable fields; prioritize security-boundary code.

#### What it is
Pattern where all instances of a class share the same static state—appear as separate objects but behave as one global state.

#### When to use / when NOT
- **Use:** Rarely intentionally—prefer explicit singleton or injected context.
- **Use:** Read-only global registries initialized once at startup (careful).
- **NOT:** Multi-tenant request state—use scoped DI or explicit parameters.
- **NOT:** Unit tests needing isolation—static state leaks between tests.

#### Java / Spring example
```java
// Anti-pattern
class BadTenantCtx {
  private static Tenant current;
  public void set(Tenant t) { current = t; } // global mutation
}
// Prefer
record RequestContext(TenantId tenantId) {}
```

#### Common mistakes
- Static mutable fields in web apps with thread pools.
- Assuming `new Object()` implies new isolated state in Monostate.
- Forgetting to clear ThreadLocal in finally—memory leaks in Tomcat.

#### Follow-up (with answer)
**Q:** Monostate vs Singleton?
**A:** Singleton: one instance globally, API enforces `getInstance()`. Monostate: unlimited instances, shared static backing—easier to misuse because `new` looks innocent. Both problematic for testability; Spring singleton scope is container-managed single instance per context—not JVM static Monostate. Prefer injection over either hand-rolled pattern.

---

### P114. Multiton

**Category:** Creational
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/multiton/)

**Short answer:** Multiton maintains one instance per key (enum map of singletons)—like per-tenant or per-locale config holders. Useful for finite named instances; hurts when keys unbounded (memory leak) or instances hold request-scoped data.

#### Scenario (interview)
**Situation:** App caches `DatabaseDialectHelper.getInstance(vendor)` in static map for postgres, oracle, mysql; someone passes dynamic tenant shard URLs as key—map grows unbounded until OOM.
**What they're testing:** Bounded key sets, lifecycle, vs Spring bean maps.
**Model answer:** I'd restrict Multiton to finite enum keys: `Dialect.POSTGRES`, `Dialect.ORACLE`—pre-initialized in static block. For tenant-specific connections, use Spring `@Bean` per datasource with Hikari pool—not Multiton map keyed by tenantId (unbounded). If Multiton needed for plugin registry, use `ConcurrentHashMap` with max size + LRU eviction or immutable pre-wired map at startup. Expose interface; hide getInstance behind factory injected in tests. Document that Multiton is not cache—unbounded keys belong in Caffeine with TTL. Monitor map size metric if any dynamic Multiton exists. Migration: replace `getInstance(tenant)` with injected `TenantRoutingDataSource` delegating by context.

#### What it is
Creational pattern managing a map of named instances—at most one object per key.

#### When to use / when NOT
- **Use:** Fixed catalog of variants (parsers per format, dialect per DB vendor).
- **Use:** Expensive immutable helpers shared per key.
- **NOT:** Unbounded or user-generated keys—use cache with eviction.
- **NOT:** Request-scoped identity—use DI scopes.

#### Java / Spring example
```java
enum FormatParser {
  JSON { Parser create() { return new JsonParser(); } },
  XML  { Parser create() { return new XmlParser(); } };
  private final Parser instance = create();
  public Parser get() { return instance; }
}
```

#### Common mistakes
- Dynamic keys without eviction—Multiton becomes memory leak.
- Synchronized getInstance bottleneck on hot path—use enum or preinit.
- Multiton holding mutable request state shared across threads.

#### Follow-up (with answer)
**Q:** Multiton vs Flyweight?
**A:** Multiton: one instance per key for identity distinction (parser per type). Flyweight: shared intrinsic state across many logical objects (glyph character cache)—extrinsic state passed per use. Flyweight optimizes memory for huge populations; Multiton caps instance count to key catalog size. Both use maps; intent differs.

---

### P115. Mute Idiom

**Category:** Behavioral / UI
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/mute-idiom/)

**Short answer:** Mute idiom provides no-op implementation of an interface so callers can disable behavior without null checks—`Collections.emptyList()`, logging NOP, disabled feature stub. Hurts when mute hides misconfiguration or silent failures mask production bugs.

#### Scenario (interview)
**Situation:** Audit logging interface implemented as `NoOpAuditLogger` in dev; prod misconfig leaves NoOp bean active for 3 weeks—compliance audit fails.
**What they're testing:** Safe defaults, profile-specific wiring, fail-fast on missing prod config.
**Model answer:** I'd use mute idiom for optional cross-cutting concerns in tests and local dev only. Define `AuditLogger` interface; `Slf4jAuditLogger` in prod profile; `NoOpAuditLogger` in `@Profile("local")`. Prod startup fails if audit sink URL missing—never silently mute compliance paths. For feature toggles, mute implementation when flag off but metric `audit.events.dropped` increments so silence is visible. Tests inject NoOp to avoid side effects. Document difference between mute (intentional disable) and null (bug). Spring `@ConditionalOnProperty` wires real impl only when enabled. Alert if prod logger bean class name contains NoOp. Anti-pattern: returning mute from factory on exception swallowing config errors.

#### What it is
Object-oriented pattern supplying do-nothing implementation satisfying interface contract without effect.

#### When to use / when NOT
- **Use:** Optional plugins, test doubles, feature-off code paths without null.
- **Use:** Default stub until real implementation configured.
- **NOT:** Regulated audit/security paths in production without explicit approval.
- **NOT:** Mute masking initialization failure—fail fast instead.

#### Java / Spring example
```java
interface MetricsSink { void increment(String name); }
class NoOpMetricsSink implements MetricsSink { public void increment(String n) {} }
@Bean @Profile("prod") MetricsSink sink() { return new DatadogSink(apiKey); }
```

#### Common mistakes
- Prod accidentally wired to NoOp—no logs indicate problem.
- Mute implementation throws away errors callers assume recorded.
- Interface so large NoOp must implement 40 methods—split interface (ISP).

#### Follow-up (with answer)
**Q:** Mute idiom vs Null Object pattern?
**A:** Closely related—Null Object is behavioral pattern with full semantic object replacing null checks; Mute idiom emphasizes no-op side effects (logging, metrics). Same implementation often serves both names. Choose explicit bean profiles over returning null from factory.

---

### P116. Naked Objects

**Category:** Architectural / UI
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/naked-objects/)

**Short answer:** Naked Objects auto-generates UI from domain objects exposed directly—framework introspects entities for CRUD screens. Accelerates internal admin apps but hurts for public UX, rich validation flows, and when domain leaks presentation concerns.

#### Scenario (interview)
**Situation:** Internal ops team builds Naked Objects framework on JPA entities; product wants customer-facing portal with branding, wizard flows, and field-level permissions—generated UI unusable.
**What they're testing:** Domain-driven UI limits, when auto-UI fits.
**Model answer:** I'd scope Naked Objects to internal admin/back-office with trusted power users only—expose aggregates via REST metadata API; Angular admin shell renders forms from schema. Domain entities stay persistence-annotated but never leak to public API—DTO projection required for external. Add authorization annotations interpreted by framework to hide actions. For customer portal, abandon naked approach—build intentional UX with MVP/MVVM. Version entity metadata for backward-compatible admin screens. Pitfall: lazy-loaded collections in auto UI cause N+1 and accidental data exposure—use fetch plans and field allowlists. Framework generates equals hash on all fields—PII in list views. Success: ops configures new entity admin in hours not weeks. Know when to graduate off naked objects—first external user milestone.

#### What it is
Architectural pattern rendering user interface automatically from domain object structure and behavior introspection.

#### When to use / when NOT
- **Use:** Rapid internal CRUD, prototypes, admin consoles on stable domain model.
- **Use:** Domain model is carefully designed with invariants in entities.
- **NOT:** Customer-facing polished UX, mobile-first, marketing sites.
- **NOT:** Complex multi-step workflows with branching logic.

#### Java / Spring example
```java
@Entity
public class WarehouseItem {
  @Title public String getSku() { return sku; }
  @Action public void relocate(String bin) { /* domain logic */ }
}
// Framework renders list/detail from annotations
```

#### Common mistakes
- Exposing entire entity graph including internal flags/password hashes.
- No authorization on auto-generated actions—any user invokes any method.
- Performance: unbounded list screens without pagination defaults.

#### Follow-up (with answer)
**Q:** Naked Objects vs REST + OpenAPI codegen?
**A:** Naked Objects couples UI directly to domain object methods—fast for homogenous admin UIs. OpenAPI codegen decouples: server exposes contract, client generates typed client—better for heterogeneous clients and public APIs. Many teams use OpenAPI + low-code admin (Retool) instead of full Naked Objects framework maintenance.

---

### P117. Notification

**Category:** Enterprise / Integration
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/notification/)

**Short answer:** Notification pattern sends one-way async messages to external systems (email, SMS, webhooks) decoupled from core transaction—often via outbox/events. Hurts when notifications block main flow, duplicate sends on retry without idempotency, or template rendering failures roll back business TX.

#### Scenario (interview)
**Situation:** Order confirmation email sent inside `@Transactional` order save; SMTP timeout rolls back paid order—customer charged, no order record.
**What they're testing:** After-commit delivery, outbox, idempotent notification consumers.
**Model answer:** I'd decouple notification from order transaction. On order save, insert `NotificationOutbox` row same TX; after commit listener or poller publishes `OrderConfirmed` event. Notification service consumes, renders template, calls SendGrid with idempotency key `orderId+template`. Failures retry with backoff; DLQ after N attempts—order remains valid. Use `@TransactionalEventListener(phase = AFTER_COMMIT)` for lightweight cases. Never block HTTP response on SMTP. Template service versioned; rendering errors don't poison order aggregate. Track delivery status separately (`PENDING/SENT/FAILED`). Compliance: unsubscribe link in marketing emails separate transactional channel. Metrics: time from order to email sent p95. Customer support queries notification log by orderId—not order table joins SendGrid.

#### What it is
Integration pattern emitting one-way informational messages to people or systems outside core domain workflow.

#### When to use / when NOT
- **Use:** Email/SMS/push/webhook side effects after domain events.
- **Use:** Multiple notification channels subscribe to same event.
- **NOT:** Synchronous requirement inside same DB transaction as core write.
- **NOT:** Request/response to external system needing answer—use gateway/client.

#### Java / Spring example
```java
@TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
void on(OrderConfirmed e) { kafka.send("notifications", new EmailCommand(e.orderId())); }
```

#### Common mistakes
- SMTP in transaction—dual failure modes.
- No idempotency—retries duplicate "your order shipped" emails.
- PII in notification logs without retention policy.

#### Follow-up (with answer)
**Q:** Notification vs Observer?
**A:** Observer: in-process subscribers react to subject state change synchronously or in same app. Notification: cross-boundary one-way messages to external channels or services—async, at-least-once, idempotent. Domain event may trigger both: in-process projection update (observer-like) and Kafka notification command.

---

### P118. Null Object

**Category:** Behavioral
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/null-object/)

**Short answer:** Null Object implements interface with benign do-nothing or default behavior—eliminates null checks. `Collections.emptyList()`, optional strategy noop. Hurts when null object hides missing configuration or returns success for dangerous operations.

#### Scenario (interview)
**Situation:** Discount pipeline calls `DiscountPolicy.apply()`; null policy causes NPE in prod for B2B accounts without promotion; dev fixes with `if (policy != null)` scattered in 14 places.
**What they're testing:** Polymorphism over null, default behavior object.
**Model answer:** I'd introduce `DiscountPolicy` interface with `Money apply(Money subtotal)` and `NoDiscountPolicy` returning subtotal unchanged—always inject non-null policy (default bean). Spring `@Autowired DiscountPolicy` never Optional empty—wire `NoDiscountPolicy` as `@Primary` fallback or explicit config per account type. For B2B, inject `VolumeDiscountPolicy` when contract exists. Removes defensive null checks; strategy map returns policy or NoDiscount. Unit test verifies NoDiscount identity behavior. Contrast with mute idiom: Null Object represents valid business "no discount" not disabled feature. Don't use Null Object for missing required dependencies—fail startup instead. Document in API that policy is never null; static analysis bans null returns.

#### What it is
Behavioral pattern providing object implementing interface with neutral behavior instead of using null reference.

#### When to use / when NOT
- **Use:** Optional behavior with safe default (no discount, no op listener).
- **Use:** Eliminating repetitive null guard clauses in hot paths.
- **NOT:** Required collaborator missing—fail fast, not silent noop.
- **NOT:** Null object that silently skips security checks.

#### Java / Spring example
```java
interface DiscountPolicy { Money apply(Money subtotal); }
class NoDiscount implements DiscountPolicy {
  public Money apply(Money s) { return s; }
}
```

#### Common mistakes
- Null Object doing too much—becomes hidden business logic.
- Returning null from factory when misconfigured instead of real impl.
- Null Object mutable shared singleton with state—must stay stateless.

#### Follow-up (with answer)
**Q:** Null Object vs Optional?
**A:** Optional wraps absence at call site—good for return values meaning "not found." Null Object replaces null reference with polymorphic instance—good for injected strategies always invoked. Combine: repository returns Optional<Entity>; service maps empty to Null Object policy for downstream uniform calls—not Optional in every layer.

---

### P119. Object Mother

**Category:** Testing
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/object-mother/)

**Short answer:** Object Mother factory methods create pre-configured test domain objects (`aValidOrder()`, `aCancelledShipment()`). Reduces test setup duplication vs raw constructors. Hurts when mothers become god factories with combinatorial explosion or prod code depends on test mothers.

#### Scenario (interview)
**Situation:** 200 integration tests each build `Order` with 15 fields; schema change breaks 180 tests; developers copy-paste stale builders with illegal states passing compile but failing validation at runtime.
**What they're testing:** Test data factories, meaningful defaults, domain-valid fixtures.
**Model answer:** I'd create `OrderMother` in test sources with fluent methods: `OrderMother.validStandardOrder()`, `.withStatus(CANCELLED)`, `.forTenant("acme")`. Mothers encode valid defaults matching domain invariants—always passes `OrderValidator`. Schema change updates one mother method. Avoid mothers in `main`—test scope only. For complex graphs, compose mothers: `CustomerMother.withOrders(2)`. Contrast Test Data Builder when many optional permutations—mother for common cases, builder for edge combos. Document naming: `a*` vs `valid*` convention. CI rule: tests must not construct entities via `new Order()` directly except mother unit tests. Pair with `@Sql` scripts only for JDBC IT—not for unit tests. Mothers speed readability: test asserts behavior not setup noise.

#### What it is
Testing pattern: dedicated factory class producing ready-made test objects with sensible defaults and named variants.

#### When to use / when NOT
- **Use:** Repeated complex object graphs in tests; enforce valid defaults.
- **Use:** Integration tests needing consistent seed entities.
- **NOT:** Production code importing test mothers—keep test scope.
- **NOT:** 50-parameter mother—use builder pattern in tests instead.

#### Java / Spring example
```java
class OrderMother {
  static Order validPaidOrder() {
    return Order.builder().status(PAID).lines(List.of(line("SKU1", 2))).build();
  }
}
```

#### Common mistakes
- Mothers creating invalid illegal states used by many tests—false confidence.
- Shared mutable mother instances modified by tests—order flaky tests.
- Mothers duplicating production factory logic—drift over time.

#### Follow-up (with answer)
**Q:** Object Mother vs Builder vs Factory in tests?
**A:** Object Mother: named scenarios (`validCancelledOrder`). Builder: step-by-step customization for rare cases. Factory: generic create with random data (easy-random) for fuzz.property tests. Start with mothers for 80% cases; add test builders when combinations explode. Production Factory Method unrelated—don't reuse prod factory in tests if it hides test intent.

---

### P120. Object Pool

**Category:** Creational / Performance
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/object-pool/)

**Short answer:** Object Pool reuses expensive-to-create objects (connections, threads, parsers) instead of allocate/release per use. JDBC pools (HikariCP) are canonical. Hurts when pool sizing wrong, objects not reset on return, or pooling cheap objects adds overhead.

#### Scenario (interview)
**Situation:** Service creates new `DocumentBuilder` and SSL context per XML request; GC pauses spike under load; team proposes pooling custom `SecureXmlParser` instances.
**What they're testing:** Pool lifecycle, reset state, sizing, vs JVM/library pooling.
**Model answer:** I'd profile first—confirm parser creation dominates. If yes, pool with Apache Commons Pool or custom `BlockingQueue` of reset parsers—`returnObject` must clear internal state and entity resolver to prevent XXE carryover. Cap pool size; block with timeout rather than unbounded queue. For DB, rely on HikariCP not hand-rolled pool. Metrics: pool active/idle, wait time, exhausted events. Don't pool mutable objects without factory reset. SSL context pool rarely needed—reuse single context bean. Load test validates pool size vs connection count formula (threads × avg concurrent queries). Anti-pattern: pooling lightweight DTOs. Document borrow-return in try-finally; leak detection thread logs offenders. Spring manages many pools—don't duplicate.

#### What it is
Creational pattern maintaining set of initialized objects ready for reuse, avoiding repeated instantiation cost.

#### When to use / when NOT
- **Use:** Expensive construction (DB connections, network clients, large buffers).
- **Use:** Object creation rate exceeds GC/CPU budget.
- **NOT:** Cheap immutable objects—pool adds synchronization tax.
- **NOT:** Objects hard to reset to clean state—risk state leakage.

#### Java / Spring example
```java
// HikariCP — production standard
@Bean DataSource dataSource() {
  HikariConfig cfg = new HikariConfig();
  cfg.setMaximumPoolSize(20);
  return new HikariDataSource(cfg);
}
```

#### Common mistakes
- Pool size = number of threads × 10 without measurement—DB max connections exceeded.
- Returning dirty object to pool—next borrower sees previous tenant data.
- Not closing borrowed resource—pool exhaustion outage.

#### Follow-up (with answer)
**Q:** Object pool vs Flyweight?
**A:** Object pool: reuse mutable expensive instances—borrow, use, return reset. Flyweight: share immutable intrinsic state across many uses—no return semantics. Connection pool reuses connections; Flyweight shares character glyph data. Pool manages lifecycle and exhaustion; Flyweight manages memory deduplication.

---

### P121. Observer

**Category:** Behavioral
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/observer/)

**Short answer:** Observer defines one-to-many dependency: subject notifies observers on state change—`java.util.Observer` (deprecated), Swing listeners, Spring `ApplicationEvent`, reactive streams. Hurts with unexpected update order, memory leaks from forgotten unsubscribe, or synchronous observers blocking subject.

#### Scenario (interview)
**Situation:** Order service publishes domain events; six `@EventListener` methods run synchronously in same thread—inventory lock + email + analytics adds 800ms to checkout HTTP response.
**What they're testing:** Sync vs async observation, event granularity, listener registration lifecycle.
**Model answer:** I'd audit observer topology. Domain raises fine-grained events (`OrderPaid`) inside aggregate; application layer publishes after commit. Move non-critical listeners (`AnalyticsListener`, `EmailListener`) to `@Async` or Kafka after outbox—checkout responds after payment + inventory only. Critical path listeners stay synchronous and transactional. Prevent infinite loops: listener must not mutate same aggregate re-firing event without guard. Use `@TransactionalEventListener(AFTER_COMMIT)` for integration side effects. Document listener ordering—avoid relying on `@Order` spaghetti; split to explicit saga if order matters. Memory: unregister WebSocket observers on disconnect. For high fan-out, log-based Kafka is Observer at scale. Test with listener stubs measuring checkout latency budget 200ms.

#### What it is
Behavioral pattern where subject maintains observer list and notifies them automatically of state changes.

#### When to use / when NOT
- **Use:** Decouple event producers from multiple reacting components.
- **Use:** UI binding, domain events, Spring application events.
- **NOT:** Complex orchestrated workflows—use saga/state machine.
- **NOT:** Observers performing heavy I/O synchronously on hot path.

#### Java / Spring example
```java
// Spring Observer
applicationEventPublisher.publishEvent(new OrderPaidEvent(orderId));
@EventListener @Async void on(OrderPaidEvent e) { emailService.sendReceipt(e.orderId()); }
```

#### Common mistakes
- Listener throws—rolls back entire transaction unexpectedly.
- Forgotten unsubscribe—mobile/WebSocket memory leak.
- God subject notifying 40 observers—split bounded contexts.

#### Follow-up (with answer)
**Q:** Observer vs Pub/Sub (Kafka)?
**A:** Observer typically in-process, synchronous or async thread, tight coupling to JVM lifecycle. Pub/Sub crosses process boundaries, durable log, consumer groups—Observer pattern distributed and at-least-once. Evolve from Spring events to Kafka when fan-out crosses services or needs replay. Same conceptual model; different operational profile.

---

### P122. Onion Architecture

**Category:** Architectural
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/onion-architecture/)

**Short answer:** Onion Architecture arranges dependencies inward: domain core without outward deps; application services; infrastructure adapters outer. Aligns with ports/adapters and DDD. Hurts when "domain" becomes anemic or outer rings leak into entities via JPA annotations everywhere.

#### Scenario (interview)
**Situation:** "Hexagonal migration" stalled—domain package imports Spring Data, REST DTOs in entity package, ArchUnit rules fail on every PR; team blames onion architecture for slowdown.
**What they're testing:** Dependency rule, rich domain, adapter placement.
**Model answer:** I'd reset onion layers pragmatically. Inner core: pure Java aggregates, value objects, domain services—zero Spring/JPA imports. Application layer orchestrates use cases, defines port interfaces (`OrderRepository`, `PaymentGateway`). Infrastructure implements ports with JPA, RestTemplate, Kafka adapters in outer module. Persistence mapping: JPA entity in infrastructure maps to/from domain aggregate—Anti-Corruption inside adapter, not `@Entity` on domain class if team mature enough. Gradle module dependencies point inward only. Fix failing migration by strangling: new use cases onion-clean; legacy touched only when needed. ArchUnit `domain.should().notDependOn("org.springframework")` enforced in CI. Onion not dogma—allow `@Transactional` on application service in same module initially. Success: domain unit tests run in milliseconds without Spring context.

#### What it is
Architecture style concentric layers with domain model at center; outer layers depend on inner, never reverse.

#### When to use / when NOT
- **Use:** Complex domain rules worth isolating from frameworks.
- **Use:** Long-lived systems where persistence/UI technology changes.
- **NOT:** Simple CRUD with no domain logic—layer ceremony slows delivery.
- **NOT:** Domain polluted with framework annotations without mapping layer.

#### Java / Spring example
```
order-domain/          (no Spring)
order-application/     (use cases, ports)
order-infrastructure/  (JPA adapters, REST controllers)
order-boot/            (Spring Boot main)
```

#### Common mistakes
- Anemic domain—all logic in `@Service`, entities are bags.
- Domain depending on infrastructure "just for `@Entity`."
- 4 Gradle modules for 5-endpoint app—over-segmentation.

#### Follow-up (with answer)
**Q:** Onion vs Clean vs Hexagonal?
**A:** Same family: dependency inversion toward domain. Hexagonal emphasizes ports/adapters metaphor; Clean adds explicit use case/interactor ring; Onion concentric circles. Pick one vocabulary for team; enforce dependency rule consistently. Spring Boot can host all rings in packages before splitting modules.

---

### P123. Optimistic Offline Lock

**Category:** Enterprise / Concurrency
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/optimistic-offline-lock/)

**Short answer:** Optimistic offline lock detects concurrent edits via version column/timestamp at commit—user edits offline copy, commit fails if stale. JPA `@Version` embodies this. Hurts when users lose long edits without merge UI or when hot aggregates retry storm under write contention.

#### Scenario (interview)
**Situation:** Field technicians edit work orders offline in tablet app; sync on reconnect silently overwrites newer server changes—dispatch assigns wrong crew; legal incident.
**What they're testing:** Version tokens, conflict detection, merge/resubmit UX, not pessimistic DB locks offline.
**Model answer:** I'd implement optimistic offline lock: each work order has `version` integer incremented on server save. Client caches `{id, version, payload}` offline. On sync, PUT includes `If-Match: version`; server compares—match saves version+1; mismatch returns 409 Conflict with server snapshot. Client shows merge UI: side-by-side diff, user picks fields or rebases. Never last-write-wins silently. JPA `@Version` on entity auto-increments; catch `OptimisticLockException` map to 409. For long offline windows, business may require supervisor override with audit log—not blind force. Retry storm on hot row: exponential backoff + human queue. Document that optimistic fits read-mostly contested writes; pessimistic lock for financial ledger hot rows. Integration test: two clients version 3, first commits wins, second gets conflict.

#### What it is
Concurrency control allowing offline/working-copy edits while detecting conflicts at synchronization via version check rather than holding DB locks offline.

#### When to use / when NOT
- **Use:** Mobile/offline editors, long user think time, read-heavy write-occasional.
- **Use:** HTTP APIs with ETag/`If-Match` semantics.
- **NOT:** High-contention financial invariants needing serial writes—pessimistic or saga.
- **NOT:** Without user-facing conflict resolution—data loss guaranteed.

#### Java / Spring example
```java
@Entity
class WorkOrder {
  @Version private Long version;
}
// Controller
@PutMapping("/{id}")
ResponseEntity<?> update(@PathVariable Long id, @RequestHeader("If-Match") long v, @RequestBody Dto dto) {
  try { return ok(service.update(id, v, dto)); }
  catch (OptimisticLockException e) { return status(CONFLICT).body(serverState(id)); }
}
```

#### Common mistakes
- Missing `@Version`—lost updates silently.
- 409 without server body—client cannot merge.
- Retrying optimistic lock failure infinitely on same version—user must refresh.

#### Follow-up (with answer)
**Q:** Optimistic offline lock vs pessimistic lock?
**A:** Optimistic: no lock during edit; conflict at commit—scales for offline/long sessions. Pessimistic: lock row on read (`SELECT FOR UPDATE`)—prevents conflict but blocks others and impossible offline. Hybrid: optimistic with short-lived pessimistic for checkout "seat hold" windows.

---

### P124. Page Controller

**Category:** Enterprise / UI
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/page-controller/)

**Short answer:** Page Controller handles HTTP request for one page/action—classic Spring `@Controller` one class per screen or REST resource group. Simple and explicit; hurts when duplicated logic across pages or controller becomes transaction script god file.

#### Scenario (interview)
**Situation:** Insurance portal has 80 Thymeleaf pages each with dedicated controller; premium calculation duplicated in 6 page controllers with divergent tax rules.
**What they're testing:** Front controller vs page controller, extracting application services.
**Model answer:** I'd keep Page Controller for HTTP/view mapping but extract shared use cases to `PremiumCalculationService`. Each page controller: authenticate, bind form, call one application method, choose view name—no tax math in controller. Shared wizard steps may use one controller with step param or separate page controllers sharing service—prefer clarity over DRY obsession for unrelated pages. Front Controller (`DispatcherServlet`) already routes; Page Controller is endpoint class per page in Fowler sense. For REST JSON APIs, page becomes resource controller (`ClaimController`) still page-like granularity. Refactor duplicate blocks by composition not inheritance mega-base-controller. Test services unit-level; `@WebMvcTest` per controller smoke. When many pages share identical flow, consider task controller pattern—not premature merge of unrelated screens.

#### What it is
Pattern assigning one controller object responsibility for all actions on a logical page or related screen flow.

#### When to use / when NOT
- **Use:** Server-rendered MVC, clear page-to-endpoint mapping.
- **Use:** Teams want obvious place to find screen logic entry point.
- **NOT:** Heavy shared orchestration—extract application service layer.
- **NOT:** Single-page app where server has one HTML shell only.

#### Java / Spring example
```java
@Controller
@RequestMapping("/claims/submit")
class SubmitClaimPageController {
  @GetMapping fun form(Model m) { m.addAttribute("form", new SubmitClaimForm()); return "claims/submit"; }
  @PostMapping fun submit(@Valid SubmitClaimForm f) { claimService.submit(f); return "redirect:/claims/confirmation"; }
}
```

#### Common mistakes
- Business logic and SQL inside page controller methods.
- Copy-paste validation across pages instead of domain validation once.
- 40 endpoints in one "page" controller—split by bounded screen.

#### Follow-up (with answer)
**Q:** Page Controller vs Front Controller?
**A:** Front Controller is single entry (`DispatcherServlet`) dispatching to handlers. Page Controller is design choice: one handler class per page vs one class for entire site. Spring combines both: Front Controller servlet routes to many Page Controller `@RequestMapping` classes. Confusion arises calling `DispatcherServlet` "Front Controller" while each `@RestController` is Page Controller for its resource.

---

### P125. Page Object

**Category:** Testing
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/page-object/)

**Short answer:** Page Object encapsulates UI locators and interactions for one screen in test code—Selenium/Playwright best practice. Tests read `loginPage.submit(user, pass)` not raw XPath. Hurts when page objects know assertions, share mutable state, or mirror every DOM element causing brittle mega-classes.

#### Scenario (interview)
**Situation:** E2E suite has 900 XPath strings duplicated; UI redesign breaks 120 tests; QA spends days updating selectors not scenarios.
**What they're testing:** Test maintainability, encapsulation, fluent interfaces for flows.
**Model answer:** I'd introduce Page Objects per screen: `LoginPage`, `CheckoutPage` with locators private, methods `enterCredentials`, `submit`, `assertErrorVisible` optional (prefer assertions in test not page). Use stable `data-testid` attributes agreed with frontend team—not CSS classes that change with theme. Compose flows: `CheckoutFlow.completePurchase(cart)` orchestrates multiple page objects. No sleeps—explicit waits inside page methods. Parallel tests: page objects stateless; WebDriver injected per test. Version page objects with app major releases. Anti-pattern: page object 800 lines mirroring entire DOM—model user-visible components only. CI runs smoke E2E on page object covered paths nightly. When micro-frontends, page object per remote widget boundary. Document that page object is test adapter—not production pattern.

#### What it is
Testing pattern mapping web/application page to class exposing methods representing user actions and queries.

#### When to use / when NOT
- **Use:** UI/E2E automation with Selenium, Playwright, Cypress wrappers.
- **Use:** Frequent UI changes requiring centralized locator updates.
- **NOT:** Unit tests of business logic—no browser needed.
- **NOT:** Page objects containing test assertions about unrelated pages—keep focused.

#### Java / Spring example
```java
class LoginPage {
  private final WebDriver driver;
  LoginPage enterUser(String u) { driver.findElement(byTestId("username")).sendKeys(u); return this; }
  HomePage submit() { driver.findElement(byTestId("login-btn")).click(); return new HomePage(driver); }
}
```

#### Common mistakes
- Public WebElement fields exposing locators to tests.
- Thread.sleep instead of expected conditions in page methods.
- One Page Object for entire SPA—unmaintainable.

#### Follow-up (with answer)
**Q:** Page Object vs Screenplay pattern?
**A:** Page Object organizes by UI page; Screenplay organizes by actor/tasks (`Actor.attemptsTo(Login.with(creds))`) composing interactions and questions. Screenplay scales better for complex BDD flows; Page Object simpler for small teams. Can combine: tasks use page objects internally.

---

### P126. Parameter Object

**Category:** Structural / Enterprise
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/parameter-object/)

**Short answer:** Parameter Object replaces long parameter lists with single object carrying related values—improves readability, validation, and evolution. Java records excel here. Hurts when god parameter bag crosses unrelated concerns or mutable object reused unsafely across threads.

#### Scenario (interview)
**Situation:** `searchProducts(String q, int page, int size, String sort, boolean inStock, BigDecimal minPrice, BigDecimal maxPrice, List<String> categories, String tenantId, Locale locale)` called from 30 places—signature change breaks compile across monolith monthly.
**What they're testing:** API evolution, validation grouping, records/DTOs.
**Model answer:** I'd introduce `ProductSearchCriteria` record with builder validating invariants (`page >= 0`, `minPrice <= maxPrice`). Method becomes `search(ProductSearchCriteria c)`—add filter fields without changing arity. Map HTTP query params to criteria in controller once via `@ModelAttribute` or custom resolver. Immutability prevents caller mutating after validation. Split if needed: `Pagination` + `PriceRange` value objects composed inside criteria—not one 40-field bag. For optional filters use `Optional` fields or nullable with explicit semantics documented. Serialization: stable JSON names for API version N. ArchUnit: no method with >5 parameters in service layer. Refactor incrementally: overload old method delegating to record wrapper deprecated one release.

#### What it is
Refactoring/cl pattern bundling group of related parameters into single object passed to methods.

#### When to use / when NOT
- **Use:** 4+ related parameters, shared validation, evolving API surface.
- **Use:** Cross-cutting query filters, report options, connection configs.
- **NOT:** Single primitive parameter—wrapper noise.
- **NOT:** Unrelated fields lumped together—split criteria objects.

#### Java / Spring example
```java
public record ProductSearchCriteria(
    String query, PageRequest page, PriceRange price, Set<Category> categories, TenantId tenant) {
  public ProductSearchCriteria {
    Objects.requireNonNull(tenant);
    if (price != null && price.min().compareTo(price.max()) > 0) throw new IllegalArgumentException();
  }
}
```

#### Common mistakes
- Mutable parameter object modified after validation bypasses checks.
- Parameter object used as domain entity—mapping confusion.
- God `SearchCriteria` for entire app—namespace by use case.

#### Follow-up (with answer)
**Q:** Parameter Object vs Builder?
**A:** Parameter Object groups call parameters for one method invocation—often immutable record. Builder constructs complex object stepwise—may be same type (`Criteria.builder()`). Use builder when many optional fields and staged validation; use record when all fields known at call site. They combine: `ProductSearchCriteria.builder()...build()`.

---

### P127. Partial Response

**Category:** Microservices / Enterprise
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/partial-response/)

**Short answer:** Partial Response returns subset of resource fields client selects—GraphQL fields, REST `?fields=`, Google partial response pattern—reduces payload and join cost. Hurts when field selection bypasses authorization, exposes internal graph, or ORM dynamic projection creates N+1 queries.

#### Scenario (interview)
**Situation:** Mobile app downloads full `Customer` JSON (80 fields, nested orders) for list screen needing name + status only—battery and data usage complaints; backend CPU high serializing unused graphs.
**What they're testing:** Field masks, sparse fieldsets, auth on projected fields, performance.
**Model answer:** I'd add sparse fieldset support: `GET /customers/{id}?fields=id,name,status` parsed into allowed projection set whitelist—not free-text JSONPath. Controller maps to DTO projection or JPA `@EntityGraph` tuned per field set—not lazy load entire aggregate. Authorization: each field maps to permission; deny internal fields even if requested. Document OpenAPI field parameter; codegen client passes minimal sets per screen. For list vs detail endpoints, separate read models (CQRS) often simpler than universal partial response. Monitor query count per request—partial response with bad ORM triggers N+1. GraphQL alternative if many clients need different shapes—operational cost higher. Cache key includes fields hash. Reject unknown fields with 400 in strict mode.

#### What it is
API pattern allowing clients to specify which parts of a resource representation they need in response.

#### When to use / when NOT
- **Use:** Mobile/low-bandwidth clients, large aggregates, varied client shapes.
- **Use:** Expensive computed fields omitted unless requested.
- **NOT:** Simple stable API with one consumer shape—fixed DTO cheaper.
- **NOT:** Without field-level security audit—data leak vector.

#### Java / Spring example
```java
@GetMapping("/customers/{id}")
CustomerView get(@PathVariable UUID id, @RequestParam Set<String> fields) {
  fieldAuth.verify(fields);
  return customerQuery.project(id, FieldSet.parse(fields, CUSTOMER_WHITELIST));
}
```

#### Common mistakes
- Reflection magic loading entire entity then stripping fields—no perf win.
- Allowing `fields=passwordHash` through oversight.
- Unbounded field combinations untested—combinatorial bugs.

#### Follow-up (with answer)
**Q:** Partial response vs GraphQL?
**A:** Partial response adds field selection to REST endpoints—simpler infra, one resource at a time. GraphQL single endpoint composes nested graph client-defined—flexible but needs resolver perf discipline and complexity limits. Choose REST partial for few endpoints/mobile savings; GraphQL when many client teams need diverse nested queries.

---

### P128. Pipeline

**Category:** Behavioral / Architectural
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/pipeline/)

**Short answer:** Pipeline chains processing stages—each stage transforms/pass data to next (Servlet filters, Stream pipeline, ETL steps). Enables composable processing; hurts when stages share hidden mutable state, error handling inconsistent, or debugging opaque intermediate values.

#### Scenario (interview)
**Situation:** Fraud check runs as 900-line method with sequential if-blocks; adding device fingerprint step requires editing core method; tests brittle.
**What they're testing:** Stage isolation, composability, short-circuit, observability per stage.
**Model answer:** I'd refactor to pipeline of `FraudCheckStage` interfaces: `VelocityCheck`, `DeviceReputation`, `SanctionsScreen`, each returning `StageResult(PASS|FAIL|REVIEW, metadata)`. Pipeline executor runs ordered stages, stops on FAIL unless configured continue-for-audit. Context object immutable passed stage-to-stage accumulates evidence. Spring: list of stage beans `@Order` or explicit chain config. Log/trace each stage latency. Unit test each stage; integration test pipeline with stub stages. Parallel stages where independent via `CompletableFuture` fork—merge results. Contrast Chain of Responsibility (handler may not consume) vs Pipeline (every stage processes same carrier). For HTTP, Servlet filter chain is pipeline pattern. Avoid mutable static context—tenant bleed risk.

#### What it is
Architectural pattern decomposing processing into sequential stages connected by data flow between them.

#### When to use / when NOT
- **Use:** Multi-step transformations with clear ordering (ETL, validation chains, filters).
- **Use:** Add/remove/reorder stages without rewriting monolith method.
- **NOT:** Stages heavily intertwined needing shared rollback saga—orchestrator pattern.
- **NOT:** Two-step flow—direct method calls clearer.

#### Java / Spring example
```java
class FraudPipeline {
  private final List<FraudStage> stages;
  FraudDecision run(FraudContext ctx) {
    for (var s : stages) {
      var r = s.apply(ctx);
      if (r.terminal()) return r.decision();
    }
    return FraudDecision.APPROVE;
  }
}
```

#### Common mistakes
- Stages mutating shared global state.
- Swallowed exceptions mid-pipeline—silent approve fraud.
- No metrics per stage—cannot find slow check.

#### Follow-up (with answer)
**Q:** Pipeline vs Chain of Responsibility?
**A:** Chain: each handler decides pass to next or handle exclusively—often one handler wins (support tiers). Pipeline: all stages process same data carrier in fixed sequence—assembly line. Servlet filters behave as both: ordered pipeline where each filter can short-circuit response.

---

### P129. Poison Pill

**Category:** Concurrency / Integration
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/poison-pill/)

**Short answer:** Poison Pill is sentinel message telling consumer threads to terminate gracefully—used to shutdown worker pools processing queues. Hurts when pill processed twice, lost on crash, or confused with business messages without distinct type/markers.

#### Scenario (interview)
**Situation:** Batch import workers listen on `BlockingQueue`; ops deploys shutdown script calling `System.exit`—in-flight rows corrupt; on restart duplicate imports charge customers twice.
**What they're testing:** Graceful shutdown, sentinel messages, drain semantics.
**Model answer:** I'd implement poison pill shutdown: master enqueues special `PoisonPill.INSTANCE` per worker queue (or one pill per consumer thread in shared queue with count). Worker loop: `take()` message, if pill break loop after finishing current item only—never poison mid-transaction; use in-flight counter or complete current task first. Alternative Java: `ExecutorService.shutdown()` + `awaitTermination` with timeout—prefer standard APIs over custom pills when possible. If Kafka consumer, poison pill pattern maps to consumer `wakeup()` and cooperative rebalance—not literal message. Distinguish pill type in sealed hierarchy—never string `"POISON"`. Integration test: queue 1000 tasks + pill, assert all processed before exit. Monitor stuck workers not consuming pill after deploy SIGTERM. Kubernetes preStop hook triggers graceful drain before kill.

#### What it is
Concurrency shutdown pattern sending special message through queue signaling consumer threads to exit cleanly after processing prior work.

#### When to use / when NOT
- **Use:** Custom worker threads blocked on queue `take()`.
- **Use:** Graceful batch job termination without killing mid-task.
- **NOT:** Modern `ExecutorService` lifecycle suffices—use shutdown hooks.
- **NOT:** Pill indistinguishable from domain messages—type safety required.

#### Java / Spring example
```java
while (true) {
  Object msg = queue.take();
  if (msg == PoisonPill.INSTANCE) break;
  process((WorkItem) msg);
}
```

#### Common mistakes
- One pill for N workers on shared queue—only one thread exits.
- Poison before in-flight work completes—partial batch corruption.
- Literal poison string collides with user data.

#### Follow-up (with answer)
**Q:** Poison pill vs graceful shutdown hook?
**A:** Poison pill actively unblocks queue consumers waiting on `take()`. JVM shutdown hook runs on SIGTERM but doesn't unblock blocked threads unless coordinated. Best practice: combine `@PreDestroy` stopping accept + poison pills + `awaitTermination` timeout + force shutdown logging remaining tasks.

---

### P130. Polling Pub/Sub

**Category:** Microservices / Integration
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/polling-publisher/)

**Short answer:** Polling Pub/Sub: publisher periodically polls source for changes and publishes to broker; subscribers consume async—bridges systems without push webhooks. Hurts with poll interval vs latency trade-off, duplicate publishes without cursor, and missing updates if clock skew on timestamps.

#### Scenario (interview)
**Situation:** ERP vendor offers no webhooks; integration team polls FTP folder every minute for CSV orders; peak launch misses 15-minute SLA because poll interval fixed; duplicate files reprocessed.
**What they're testing:** Cursor/idempotency, adaptive polling, event envelope.
**Model answer:** I'd implement polling publisher as dedicated adapter service: `@Scheduled` polls ERP export table by `lastModified > cursor` stored in DB—not full folder scan. On new rows, publish `OrderImported` to Kafka with idempotency key `erpOrderId`. Subscribers process async. Adaptive interval: increase frequency during business hours, backoff at night—metrics-driven. File-based: track processed file hash + line offset cursor. Never rely on file mtime alone—clock skew. DLQ poison CSV rows. Compare to webhook push when vendor adds it—same subscriber, swap adapter. Latency SLA 30s → poll interval 10s with jitter. Document at-least-once: subscribers idempotent. Spring `@Scheduled` + ShedLock prevents duplicate pollers in clustered deploy.

#### What it is
Integration pattern where producer polls data source periodically and publishes detected changes to pub/sub channel for subscribers.

#### When to use / when NOT
- **Use:** Legacy systems without push notifications, FTP drops, DB changelogs.
- **Use:** Controlled pull rate needed for fragile upstream.
- **NOT:** Real-time sub-second requirements with push available.
- **NOT:** Full table scan each poll on huge tables—cursor mandatory.

#### Java / Spring example
```java
@Scheduled(fixedDelayString = "${erp.poll.ms}")
@SchedulerLock(name = "erpPoll")
void pollAndPublish() {
  var batch = erpClient.fetchSince(cursorRepo.get());
  batch.forEach(row -> kafka.send("orders", row.toEvent()));
  cursorRepo.advance(batch.maxTimestamp());
}
```

#### Common mistakes
- No distributed lock—multiple instances duplicate publish.
- Cursor not advanced atomically with publish—gap or replay.
- Fixed slow poll missing business SLA without monitoring lag metric.

#### Follow-up (with answer)
**Q:** Polling pub/sub vs CDC (Debezium)?
**A:** Polling: application queries source on schedule—simple, higher latency, load on source. CDC: database transaction log tailing—near-real-time, lower source impact, infra complexity. Migrate from polling to CDC when SLA tightens and team can operate Kafka Connect. Same subscriber contracts if events normalized.

---

### P131. Presentation Model

**Category:** UI / Behavioral
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/presentation-model/)

**Short answer:** Presentation Model (Application Model) holds UI-tailored state and commands separate from domain model—View binds to it. Reduces view logic; differs from DTO by including presentation behavior. Hurts when presentation model duplicates domain rules or becomes out of sync with domain changes.

#### Scenario (interview)
**Situation:** Thymeleaf templates call domain entity getters triggering lazy loads and exposing `order.internalRiskScore` to HTML; designers need formatted currency strings and disabled submit state logic cluttering templates.
**What they're testing:** UI state separation, binding, not anemic duplicate of entity.
**Model answer:** I'd introduce `CheckoutPresentationModel` per screen: formatted labels, `submitEnabled` computed from domain validation service, no persistence annotations. Controller loads domain `Order`, maps to presentation model via mapper (`OrderCheckoutMapper`), adds view-only flags (`showPromoBanner`). Template binds only presentation model—never entity. Presentation model may call read-only domain queries but not mutate entities directly—controller invokes application service on submit. For REST SPA, same concept as BFF response ViewModel JSON. Keep mapping explicit MapStruct—not manual 200 lines. Version presentation fields independently of domain schema. Test presentation model logic unit without rendering HTML. Anti-pattern: presentation model performing DB access. When domain field removed, mapper compile fails—good fast feedback.

#### What it is
UI pattern class tailored to single view/screen holding data and behavior for presentation, separate from domain model.

#### When to use / when NOT
- **Use:** Server-rendered MVC needing rich view state without fat templates.
- **Use:** Formatting, enabled/disabled flags, wizard step state.
- **NOT:** Simple CRUD showing entity fields verbatim—DTO enough.
- **NOT:** Reimplementing domain validation rules diverging from domain layer.

#### Java / Spring example
```java
class CheckoutPresentationModel {
  private final String totalDisplay;
  private final boolean submitEnabled;
  static CheckoutPresentationModel from(Order order, ValidationResult v) { /* map */ }
}
// model.addAttribute("checkout", CheckoutPresentationModel.from(...));
```

#### Common mistakes
- Presentation model IS entity with `@Entity`—leaks persistence to view.
- Business rule change updated in domain only—UI shows wrong submit state.
- Mega presentation model shared across unrelated screens—split per view.

#### Follow-up (with answer)
**Q:** Presentation Model vs ViewModel (MVVM)?
**A:** Presentation Model (Fowler): server-side screen logic for template binding. MVVM ViewModel: client-side observable state often with two-way binding. Same separation intent; different tier. Spring MVC Presentation Model + Thymeleaf parallels Android MVVM on device.

---

### P132. Private Class Data

**Category:** Structural
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/private-class-data/)

**Short answer:** Private Class Data copies mutable state into holder object so original object shares defensive copy semantics—limits mutation after construction phase. Rare in Java where immutability/records preferred. Hurts when over-applied to already immutable objects or copy cost ignored on large graphs.

#### Scenario (interview)
**Situation:** `GameCharacter` constructed then enters combat mode; stats should freeze at encounter start but buffs elsewhere mutate shared `Stats` object—players exploit changing max HP mid-fight.
**What they're testing:** Immutability snapshot, defensive copy, initialization vs runtime mutation phases.
**Model answer:** I'd apply Private Class Data pattern at combat start: extract current stats into immutable `CombatStatsSnapshot` private static holder attached to encounter record; combat logic reads snapshot only. Original character continues leveling outside combat with mutable stats. Implementation: package-private `CharacterData` class holds fields; `GameCharacter` facade delegates read during combat to frozen copy. Alternatively Java records replace much of this pattern—`CombatStatsSnapshot record` copied at encounter begin. Document phase transition: `enterCombat()` creates snapshot via defensive copy of collections (`List.copyOf`). Tests verify mutating live stats doesn't affect ongoing combat. Don't deep-copy entire world—only boundary snapshot. For configuration objects post-init freeze, `Collections.unmodifiableMap` suffices simpler than full pattern name.

#### What it is
Structural pattern storing mutable data in separate private holder class initialized at construction end to control/postpone mutation of internal state.

#### When to use / when NOT
- **Use:** Object has init phase then should become logically immutable.
- **Use:** Protect shared references from external mutation after handoff.
- **NOT:** Already using immutable records/value objects—pattern redundant.
- **NOT:** Large object graphs copied frequently—performance cost.

#### Java / Spring example
```java
class CombatEncounter {
  private final CombatStatsSnapshot stats; // private class data snapshot
  CombatEncounter(GameCharacter c) { this.stats = CombatStatsSnapshot.freeze(c.currentStats()); }
}
record CombatStatsSnapshot(int hp, int maxHp) {
  static CombatStatsSnapshot freeze(Stats s) { return new CombatStatsSnapshot(s.hp(), s.maxHp()); }
}
```

#### Common mistakes
- Shallow copy of nested mutable lists—snapshot still mutates.
- Confusing with Protected Variations—different intent.
- Applying pattern name without actual copy—reference shared.

#### Follow-up (with answer)
**Q:** Private Class Data vs immutable object?
**A:** Immutable object: always unmodifiable after creation. Private Class Data: mutable during build, then freezes by copying into holder—useful for multi-phase initialization. Java records + builders often replace both; pattern name survives in legacy C++ contexts and design pattern interviews.

---

### P133. Producer-Consumer

**Category:** Concurrency
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/producer-consumer/)

**Short answer:** Producer-Consumer decouples work creation from processing via bounded buffer queue—classic threading pattern. `BlockingQueue`, `@Async`, Kafka all embody it. Hurts when queue unbounded (OOM), consumers slower than producers without backpressure, or poison messages stall consumers.

#### Scenario (interview)
**Situation:** Image upload API saves file synchronously then resizes 4 variants—upload p99 12s; thread pool queue grows unbounded during marketing campaign until JVM OOM.
**What they're testing:** Bounded queue, backpressure, async workers, rejection policy.
**Model answer:** I'd split upload (producer) from processing (consumer). HTTP handler validates, stores blob to S3, enqueues `ResizeJob` on bounded `BlockingQueue` or SQS with visibility timeout—returns 202 Accepted with job ID immediately. Worker pool consumers pull jobs, resize, update DB status. Bounded queue applies backpressure: when full, API returns 503 Retry-After—protects JVM. Monitor queue depth alert. Idempotent consumers keyed by uploadId. Scale consumers horizontally independent of API pods. `@Async` alone without bounded queue repeats OOM—use explicit queue or message broker. Thread pool `CallerRunsPolicy` slows producers synchronously as last resort. Integration test overload scenario. Kafka variant when need replay and multi-subscriber audit trail.

#### What it is
Concurrency pattern where producers enqueue items and consumers dequeue/process independently through shared buffer.

#### When to use / when NOT
- **Use:** Slow consumers, burst traffic, decouple API latency from heavy work.
- **Use:** Parallelize work across pool with safe handoff.
- **NOT:** Synchronous work mandatory for client response—keep inline.
- **NOT:** Unbounded in-memory queue on public endpoint—OOM risk.

#### Java / Spring example
```java
BlockingQueue<ResizeJob> queue = new ArrayBlockingQueue<>(1000);
// producer
void upload(File f) { if (!queue.offer(job)) throw new ServiceUnavailableException(); }
// consumer threads
while (running) { worker.process(queue.take()); }
```

#### Common mistakes
- `LinkedBlockingQueue` default unbounded capacity—silent OOM.
- Consumer exception kills thread silently—pool drains to zero.
- No dead-letter path for permanently failing jobs.

#### Follow-up (with answer)
**Q:** Producer-Consumer vs Message Queue (Kafka)?
**A:** In-process `BlockingQueue`: low latency, lost on crash, single JVM scale. Kafka producer-consumer: durable, replayable, cross-service—higher latency and ops. Choose in-process for same-service offload; broker when durability, multiple services, or crash recovery required.

---

### P134. Promise

**Category:** Concurrency / Behavioral
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/promise/)

**Short answer:** Promise represents future result of async operation—`CompletableFuture`, `Future`, reactive `Mono`. Enables non-blocking composition. Hurts when blocking `.get()` on event threads, unhandled exceptional completion, or promise chains without timeout/cancellation.

#### Scenario (interview)
**Situation:** Portal aggregates five microservice calls with `@Async CompletableFuture` but UI thread blocked on `future.get()` without timeout—Tomcat threads exhausted during downstream outage; cascading 503s.
**What they're testing:** Non-blocking composition, timeouts, exception handling, thread pool isolation.
**Model answer:** I'd never block servlet threads on open-ended `get()`. Compose with `CompletableFuture.allOf(...).orTimeout(2, SECONDS)` then map to response—or migrate hot path to WebFlux `Mono.zip`. Each downstream call wrapped with circuit breaker and fallback. Handle `CompletionException` unwrap root cause; return partial response not hang. Dedicated `@Async` executor with bounded queue sized for Tomcat thread count—not `ForkJoinPool.commonPool()`. Propagate cancellation: client disconnect cancels downstream if supported. Log slow stage from `whenComplete` timing. For Java 21+, virtual threads ease blocking style but still need timeouts. Document async all the way vs block at edge trade-off. Load test proves thread pool stable when dependency 10s slow.

#### What it is
Pattern object acting as placeholder for result of asynchronous computation eventually available.

#### When to use / when NOT
- **Use:** Parallel independent I/O, async notification of completion.
- **Use:** Compose multiple async steps without callback hell.
- **NOT:** Simple sequential code with no I/O overlap—complexity unjustified.
- **NOT:** Blocking waits on limited thread pools without timeout.

#### Java / Spring example
```java
CompletableFuture<Quote> q = supplyAsync(() -> pricing.fetch(id), ioPool);
CompletableFuture<Stock> s = supplyAsync(() -> inventory.fetch(id), ioPool);
return q.thenCombine(s, QuoteView::merge).orTimeout(800, MILLISECONDS);
```

#### Common mistakes
- `get()` without timeout on HTTP worker thread.
- Swallowed failed future—never joined, error silent.
- Shared mutable result written by multiple async tasks without sync.

#### Follow-up (with answer)
**Q:** Promise vs Callback?
**A:** Callback: pass function invoked on completion—nested callbacks pyramid. Promise/Future: object representing eventual value chainable with `thenApply/thenCompose`—flatter composition. Reactive streams add backpressure; bare CompletableFuture lacks it—use Reactor for streaming many events.

---

### P135. Property

**Category:** Behavioral / Enterprise
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/property/)

**Short answer:** Property pattern (Fowler) exposes attribute via explicit get/set protocol often with change notification—JavaBeans `PropertyChangeSupport`, observable fields. Enables GUI binding and audit. Hurts when anemic public setters break invariants or change events fire in wrong order during batch updates.

#### Scenario (interview)
**Situation:** Swing config panel binds to `AppSettings` JavaBean; changing "region" must reload "timezone" options; manual listener spaghetti causes infinite update loop and UI freeze.
**What they're testing:** Observable properties, bounded change events, batch update discipline.
**Model answer:** I'd model settings as property objects with change support: `Property<Region> region` firing `PropertyChangeEvent` after valid set. Dependent property `timezone` listens to region changes via single mediator rule—not mutual listeners. Batch updates: `beginBatch()` suppresses events until `commitBatch()` fires single composite change—prevents partial UI states. Validate in setter before fire—invalid region never notifies. For Spring, `@ConfigurationProperties` with `@Validated` replaces manual bean property pattern for config—not domain aggregates. Domain invariants enforced in aggregate methods not public setters. Modern UI: reactive streams (`BehaviorSubject`) replace JavaBeans in new code; Property pattern still relevant for legacy Swing/JavaFX and JPA entity listeners on field access if using property access type cautiously. Test listener invoked once per logical change. Document event order deterministic.

#### What it is
Pattern treating object attributes as first-class objects or observable pairs (get/set) with optional change notification to dependents.

#### When to use / when NOT
- **Use:** UI data binding needing change events, visual editors, IDE plugins.
- **Use:** Cross-field dependency in forms (country → state list).
- **NOT:** Simple immutable value objects—no setters needed.
- **NOT:** Public setters on domain entities violating aggregate encapsulation.

#### Java / Spring example
```java
class AppSettings {
  private final PropertyChangeSupport pcs = new PropertyChangeSupport(this);
  void setRegion(Region r) {
    Region old = this.region; validate(r); this.region = r;
    pcs.firePropertyChange("region", old, r);
  }
}
```

#### Common mistakes
- Bidirectional property listeners infinite loop.
- Firing change event before validation completes—observers see illegal state.
- Exposing mutable collection via getter—change without event.

#### Follow-up (with answer)
**Q:** Property pattern vs Observer?
**A:** Property pattern is specialized Observer on attribute granularity—fine-grained field change events. Observer often coarser subject-level notification. JavaBeans bridges both: property change is observer on bean fields. Domain events (DDD) are business-meaningful changes, not every setter—prefer domain events over property spam for core model.

---



# Design Pattern Catalog — Part 4 (P136–P181)

Scenario-based senior interview Q&A aligned with [java-design-patterns.com](https://java-design-patterns.com/patterns/). Patterns 136–181.

---

### P136. Prototype

**Category:** Creational
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/prototype/)

**Short answer:** Prototype creates new objects by cloning an existing instance instead of calling constructors. It shines when initialization is expensive, state combinations are fixed at runtime, or you want to avoid parallel factory hierarchies. Trade-off: deep-copy semantics are easy to get wrong—shallow clones leak mutable shared references. In Spring, prototype scope is lifecycle cloning, not GoF deep copy; don't confuse them.

#### Scenario (interview)
**Situation:** A fraud-detection platform lets analysts compose investigation "playbooks"—each playbook bundles 40+ rule nodes, ML feature vectors, and threshold maps. Creating a playbook from XML takes ~800ms because it hydrates reference data from Redis. Analysts fork playbooks dozens of times per shift to test variants. Your team proposes caching deserialized templates and cloning them per fork.
**What they're testing:** Whether you recognize Prototype vs Factory, understand clone depth, and can reason about performance without hiding correctness bugs.
**Model answer:** I'd treat each published playbook as the prototype—a fully initialized, immutable template registered in a `PlaybookRegistry`. Forking calls `prototype.deepCopy()` then applies analyst deltas on the copy. The expensive work—parsing DSL, warming feature caches—runs once at template publish, not per fork. I'd implement copy via dedicated copy constructors or a mapper, not blind `Object.clone()`, because rule graphs contain shared `List`/`Map` references and optional circular links between nodes. For persistence, the fork gets a new ID and version; the prototype stays read-only. I'd benchmark: target fork latency under 5ms p99. I'd add contract tests that mutate a fork and assert the prototype graph is unchanged. If analysts only need shallow forks (rename + two threshold tweaks), a structural-sharing approach (copy-on-write maps) beats full deep clone. I'd document when `@Scope("prototype")` in Spring is wrong here—it gives a new bean per injection, not a cloned domain graph.

#### What it is
Prototype specifies object creation by copying a prototypical instance. Clients ask for a clone with optional post-clone customization. It decouples clients from concrete classes and expensive construction sequences.

#### When to use / when NOT
- **Use:** Expensive initialization; many instances differing only slightly; runtime-determined concrete types; avoiding factory class explosion.
- **NOT:** Simple POJOs where `new` is cheap; when immutability + builder is clearer; when deep-copy cost exceeds construction; when you cannot guarantee clone correctness across the object graph.

#### Java / Spring example
```java
public final class Playbook implements Cloneable {
    private final Map<String, RuleNode> nodes;
    public Playbook deepCopy() {
        var copy = new Playbook();
        nodes.forEach((k, v) -> copy.nodes.put(k, v.copy()));
        return copy;
    }
}
// Spring: prototype bean scope for per-request beans, not deep domain clone
```

#### Common mistakes
- Shallow `clone()` on graphs with nested collections—silent cross-instance mutation.
- Using Spring prototype scope expecting GoF deep-copy semantics.
- Cloning mutable singletons (DB connections, clients) embedded in the prototype.

#### Follow-up (with answer)
**Q:** Prototype vs Flyweight?
**A:** Flyweight shares intrinsic immutable state across many fine-grained objects (glyphs, icons) to save memory; extrinsic state is passed in at use time. Prototype creates independent instances by copying a template—each clone owns its state (possibly after customization). Use Flyweight when thousands of near-identical lightweight objects exist; use Prototype when each instance is a distinct editable copy of a heavy template. They can combine: Flyweight for shared rule definitions, Prototype to assemble a full playbook from references plus copied overrides.

---

### P137. Proxy

**Category:** Structural
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/proxy/)

**Short answer:** Proxy provides a surrogate controlling access to another object—adding lazy loading, security, logging, remoting, or transactions without changing the real subject's interface. Spring's entire declarative stack (`@Transactional`, `@Cacheable`, `@Async`) is proxy-based. Trade-off: proxy pitfalls—self-invocation bypasses advice, `final` methods aren't intercepted, and debugging stack traces get noisy.

#### Scenario (interview)
**Situation:** After enabling `@Cacheable` on `PricingService.getQuote()`, QA reports quotes never refresh when the underlying rate table updates. Developers added `@CacheEvict` on the admin endpoint, but bulk imports still serve stale prices for 15 minutes. Logs show cache hits on the same key even immediately after import.
**What they're testing:** Understanding that Spring AOP wraps beans in proxies, how cache keys work, and whether they can trace call paths that bypass the proxy.
**Model answer:** First hypothesis: self-invocation. If `importRates()` inside `PricingService` calls `this.getQuote()` directly, that call never passes through the CGLIB/JDK proxy—so `@Cacheable` and `@CacheEvict` on sibling methods may not interact as expected unless eviction is explicit on the import path. I'd confirm with a breakpoint on the proxy subclass. Second: cache key mismatch—import evicts `rates:EUR` but quotes cache on `quote:EUR:SKU123`. I'd align key strategy or use `@CacheEvict(allEntries=true)` on import with acceptance of brief thundering herd. Third: multiple bean instances—two `PricingService` beans in different contexts. I'd grep for duplicate `@Service` definitions and verify `@Primary`. Long-term fix: extract caching to a separate `QuoteCachePort` bean injected into `PricingService` so all access routes through one proxied collaborator; never call cached methods via `this`. Add integration test that imports rates then asserts cache miss on next quote. Document that `final` methods and constructors are never advised.

#### What it is
Proxy implements the same interface as the real subject and delegates calls, inserting behavior before/after/around delegation. Variants include virtual (lazy), protection, remote, and smart reference proxies.

#### When to use / when NOT
- **Use:** Cross-cutting concerns on narrow interfaces; lazy initialization; access control; remote service stubs.
- **NOT:** When bytecode weaving or manual decorator chains are simpler; when the interface is too wide (god service); when you need advice on private/final methods without AspectJ LTW.

#### Java / Spring example
```java
@Service
public class PricingService {
    @Cacheable("quotes")
    public Money getQuote(String sku) { ... }
}
// Spring creates CGLIB subclass proxy at runtime
```

#### Common mistakes
- Calling `@Transactional`/`@Cacheable` methods from `this`—advice skipped.
- Assuming JDK proxy works when bean doesn't implement an interface.
- Logging only the target class—hides proxy layer in production traces.

#### Follow-up (with answer)
**Q:** JDK dynamic proxy vs CGLIB?
**A:** JDK proxies require an interface and use `java.lang.reflect.Proxy`—only interface methods are intercepted. CGLIB subclasses the concrete class (cannot proxy `final` classes/methods). Spring Boot 2.x+ defaults to CGLIB for class-based beans even with interfaces, to avoid self-invocation surprises on concrete methods. Choose JDK when you want strict interface-only exposure; CGLIB when advising concrete classes. For `record` or `final` services, extract an interface or use AspectJ compile-time weaving.

---

### P138. Publish-Subscribe

**Category:** Architectural
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/publish-subscribe/)

**Short answer:** Publishers emit events to a topic or channel without knowing subscribers; subscribers register interest and receive copies asynchronously. It decouples producers from consumers in time and space. Trade-off: ordering, delivery guarantees, and schema evolution become infrastructure problems—at-least-once delivery requires idempotent consumers.

#### Scenario (interview)
**Situation:** Order placement in your e-commerce monolith currently calls inventory, billing, and email services synchronously. Peak traffic causes cascading timeouts when the email provider slows down. The architect proposes Kafka topics: `order.placed`, with three consumer groups.
**What they're testing:** Pub/sub vs point-to-point, consumer independence, failure isolation, and event contract design.
**Model answer:** Pub/sub fits because one business fact—order placed—fans out to multiple autonomous reactions without the order service enumerating them. Each consumer group (inventory, billing, notifications) scales independently; email lag no longer blocks checkout. I'd publish a versioned `OrderPlaced` envelope with orderId, customerId, line items, and correlationId—never the full ORM entity. Partition by `orderId` so per-order events stay ordered. Set retention aligned with replay needs (7 days minimum for reprocessing). Consumers must be idempotent: billing keys on `orderId`, inventory uses reservation tokens. I'd reject dual-write—use transactional outbox from the order DB so publish is atomic with commit. Observability: lag per consumer group, DLQ for poison messages, schema registry for Avro/JSON Schema. I'd keep a synchronous read path only for what checkout UX needs (payment authorization); everything else async. Rollout: shadow consumers reading mirrored events before cutover.

#### What it is
Publish-Subscribe defines a one-to-many dependency: when an event is published, all interested subscribers are notified indirectly through an event bus, broker, or topic.

#### When to use / when NOT
- **Use:** Multiple independent reactions to one event; temporal decoupling; burst absorption with durable logs.
- **NOT:** Request/response workflows needing immediate aggregated reply; when strong ordering across all subscribers is required without careful partitioning; two-party command flows better suited to queues.

#### Java / Spring example
```java
@Service
public class OrderEventPublisher {
    private final KafkaTemplate<String, OrderPlacedEvent> kafka;
    public void publish(OrderPlacedEvent e) {
        kafka.send("order.placed", e.orderId(), e);
    }
}
@KafkaListener(topics = "order.placed", groupId = "billing")
public void onOrderPlaced(OrderPlacedEvent e) { ... }
```

#### Common mistakes
- Publishing JPA entities with lazy fields—serialization bombs.
- One shared consumer group for all subscribers—messages load-balanced, not broadcast.
- No idempotency keys—duplicate events double-charge or double-ship.

#### Follow-up (with answer)
**Q:** Pub/sub vs Event Aggregator?
**A:** Pub/sub broadcasts the same event to many subscribers via a broker topic—each subscriber sees every message (per group semantics). Event Aggregator is in-process: multiple domain objects publish fine-grained events to a central mediator that composes higher-level events for UI or workflows. Use Kafka pub/sub across services; use Aggregator when a desktop/UI module needs one consolidated "cart updated" from price, tax, and shipping sub-events without network hops.

---

### P139. Queue-Based Load Leveling

**Category:** Architectural
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/queue-based-load-leveling/)

**Short answer:** Queue-Based Load Leveling inserts a buffer queue between bursty producers and capacity-limited consumers so spikes are absorbed and processed at a sustainable rate. It protects downstream databases and partner APIs from overload. Trade-off: added latency, queue depth monitoring, and poison-message handling become operational requirements.

#### Scenario (interview)
**Situation:** Your tax-filing API accepts uploads during the April deadline minute—50k requests in 60 seconds—but the OCR worker fleet processes only 200 docs/minute. During the spike, connection pools exhaust and Postgres rejects connections; even after the spike, the system stays unhealthy for an hour.
**What they're testing:** Whether you separate acceptance from processing and design for sustained throughput vs peak ingress.
**Model answer:** I'd decouple ingest from processing with Queue-Based Load Leveling. The API validates auth, stores the blob in object storage, enqueues a lightweight job (`{submissionId, s3Key}`) to SQS/Azure Service Bus, and returns `202 Accepted` with a status URL—never blocking on OCR. Workers pull at their sustainable rate (200/min), scaling on queue depth metrics. Back-pressure: API rate-limits new enqueues if queue age exceeds SLA (e.g., 4 hours). DLQ for malformed files after three retries. Idempotency: submissionId as dedup key. I'd size the queue for the full spike volume without dropping—50k messages is trivial for managed queues. Alerts on `ApproximateAgeOfOldestMessage` and worker error rate. Compare to scaling workers infinitely: OCR is CPU-heavy and costly; leveling smooths utilization. Document customer-facing ETA based on queue position. This is not the same as pub/sub fan-out—here one job maps to one worker processing pipeline.

#### What it is
Producers send work items to a queue; consumers process at their own pace. The queue acts as a shock absorber between variable arrival rates and fixed processing capacity.

#### When to use / when NOT
- **Use:** Bursty traffic vs steady backend; protecting fragile downstream systems; async workflows with acceptable latency.
- **NOT:** Synchronous user-facing paths needing immediate results; when queue becomes unbounded without drop policy; trivial CRUD with uniform load.

#### Java / Spring example
```java
@PostMapping("/submissions")
public ResponseEntity<Accepted> submit(@RequestBody Meta m) {
    var id = store.upload(m);
    queue.send(new OcrJob(id));
    return ResponseEntity.accepted().body(new Accepted(id, statusUrl(id)));
}
@JmsListener(destination = "ocr.jobs", concurrency = "5-20")
void process(OcrJob job) { ocrService.run(job); }
```

#### Common mistakes
- Synchronous processing in the HTTP thread—defeats the pattern.
- No visibility into queue depth—silent SLA breaches.
- Unbounded retries on poison pills—blocks the whole queue.

#### Follow-up (with answer)
**Q:** How does this differ from backpressure in reactive streams?
**A:** Queue-Based Load Leveling is an architectural pattern using durable middleware (SQS, Rabbit, Kafka) to decouple services over time—producers may never block, accepting eventual processing. Reactive backpressure is a protocol within a streaming pipeline (Reactor `request(n)`) where downstream signals readiness to upstream in-process or over network protocols like RSocket. Use queues for cross-service spike absorption with minutes-hours latency tolerance; use backpressure for fine-grained flow control within a streaming pipeline where participants cooperate on the same reactive chain.

---

### P140. Rate Limiting

**Category:** Performance
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/rate-limiting/)

**Short answer:** Rate Limiting caps how many requests a client, tenant, or endpoint can execute in a time window—protecting capacity and ensuring fair use. Algorithms include token bucket, leaky bucket, fixed/sliding window. Trade-off: wrong limits frustrate legitimate bursts; distributed rate limiting needs shared state (Redis) and clock skew awareness.

#### Scenario (interview)
**Situation:** A partner integration hammers your `GET /rates` API at 10k RPS, starving mobile app users. API Gateway has no per-client limits. DB CPU pegs at 95%, p99 latency jumps from 40ms to 3s, and SRE pages on connection pool exhaustion.
**What they're testing:** Practical rate-limit design—where to enforce, algorithm choice, response semantics, and tenant fairness.
**Model answer:** I'd implement Rate Limiting at the edge (API Gateway or Envoy) and reinforce in the service for defense in depth. Per API key: token bucket allowing 100 RPS sustained with burst to 200—partners get contracted quotas; mobile uses a separate pool. Redis `INCR` with sliding window or Redisson `RRateLimiter` for cluster-wide counts. On exceed: `429 Too Many Requests` with `Retry-After` header and structured error body—never silent drops. I'd add priority tiers: internal callers exempt via mTLS identity, not IP allowlists alone. Metrics: rejected rate per client, limiter latency. For read-heavy `/rates`, combine with caching so allowed requests don't all hit DB. I'd review whether 10k RPS is abuse or a missing bulk endpoint—maybe offer `/rates/bulk` with lower quota. Load-test limits before Black Friday. Document that rate limiting differs from throttling (which may queue/delay rather than reject) and from circuit breaking (which protects callers from failing downstream).

#### What it is
Rate Limiting controls the frequency of operations in a defined window per key (IP, API key, user, tenant). It prevents resource exhaustion and enforces commercial/API contract tiers.

#### When to use / when NOT
- **Use:** Public APIs; expensive endpoints; multi-tenant fairness; DDoS mitigation layer.
- **NOT:** Internal service-to-service calls with mutual auth and capacity planning already solved; when queuing delayed processing is preferable (see Throttling).

#### Java / Spring example
```java
@RateLimiter(name = "rates", fallbackMethod = "ratesFallback")
public Quote getRates(String pair) { ... }

// Bucket4j + Redis for distributed limits
Bandwidth limit = Bandwidth.classic(100, Refill.greedy(100, Duration.ofSeconds(1)));
```

#### Common mistakes
- Per-instance in-memory limits—useless behind load balancers with 20 pods.
- Returning `500` instead of `429`—clients retry aggressively.
- Same limit for reads and writes—writes need tighter caps.

#### Follow-up (with answer)
**Q:** Token bucket vs sliding window?
**A:** Token bucket accumulates tokens at a fixed rate up to a cap—allows controlled bursts (partners sync overnight batches). Sliding window counts requests in a rolling time interval—smoother boundary behavior, no burst above window max. Fixed window is simpler but suffers spike at window edges (999 requests at 00:59 and 999 at 01:00). For APIs with contractual burst tolerance, token bucket; for strict "no more than N per minute ever," sliding window log or Redis sorted sets.

---

### P141. Reactor

**Category:** Concurrency
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/reactor/)

**Short answer:** Reactor demultiplexes I/O events on a single or few threads—handlers register interest, the event loop dispatches when sockets are readable/writable. Netty, NIO `Selector`, and Project Reactor build on this model. Trade-off: never block the event loop; CPU-bound work must offload to worker pools or latency spikes hit all connections.

#### Scenario (interview)
**Situation:** Your Spring WebFlux payment gateway handles 20k concurrent connections on four event-loop threads. After adding synchronous JDBC fraud checks inside the request handler, throughput collapses and health checks flap—even though CPU is only 30%.
**What they're testing:** Reactor/event-loop discipline, non-blocking I/O vs blocking calls, and where to offload work.
**Model answer:** The regression is classic Reactor misuse: blocking JDBC on the Netty event loop thread stalls all channels bound to that loop. I'd move fraud checks to a bounded `Schedulers.boundedElastic()` pool or switch to R2DBC/WebClient for non-blocking I/O. Rule: event-loop threads only do fast state machine transitions—decode, route, schedule async work, compose responses. I'd audit with BlockHound in tests to catch accidental blocking. For unavoidable blocking (legacy SOAP), isolate behind a dedicated thread pool with queue limits and circuit breaker—never the default loop. Metrics: event-loop blocked time (Netty `io.netty.util.concurrent`), pool queue depth, end-to-end latency. Architecture option: keep WebFlux edge, call blocking fraud service via `@Async` worker with timeout. I'd document team guidelines: no `Thread.sleep`, no `.block()` in controllers, no synchronized JDBC. Compare to thread-per-request: Reactor wins on connection count, loses if the stack is accidentally blocking end-to-end.

#### What it is
Reactor pattern uses an event demultiplexer (selector/epoll) and dispatcher loop to handle many I/O channels with few threads. Handlers react to readiness events rather than blocking per connection.

#### When to use / when NOT
- **Use:** High-concurrency I/O-bound servers; WebSockets; proxy/gateway tiers; when connection count >> thread count.
- **NOT:** CPU-heavy request pipelines without worker offload; teams without non-blocking discipline; simple low-traffic CRUD where servlet stack suffices.

#### Java / Spring example
```java
@RestController
public class PayController {
    public Mono<Receipt> pay(@RequestBody Payment p) {
        return fraudClient.check(p)           // non-blocking WebClient
            .flatMap(ok -> ledgerClient.charge(p));
    }
}
// Netty event loop under the hood
```

#### Common mistakes
- Blocking calls on event-loop threads—catastrophic latency amplification.
- Unbounded `flatMap` concurrency—overwhelms downstream.
- Mixing MVC and WebFlux in same app without understanding classpath conflicts.

#### Follow-up (with answer)
**Q:** Reactor vs Proactor?
**A:** Reactor notifies handlers when I/O is *ready*—the application performs the actual read/write (Java NIO `Selector`). Proactor initiates async I/O and notifies when the operation *completes* (IOCP on Windows, some AIO APIs). Netty blends both: loop signals readiness, but pipelines can use async completion handlers. In interviews, "Reactor" often means the event-loop architecture broadly; precision matters when discussing OS primitives vs framework patterns.

---

### P142. Registry

**Category:** Enterprise
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/registry/)

**Short answer:** Registry is a well-known global index mapping keys (names, IDs, types) to objects or metadata—service instances, serializers, handlers, prototypes. It centralizes lookup and avoids scattering `new`/`switch` logic. Trade-off: registries become god maps without lifecycle rules; mutable global registries hurt testability.

#### Scenario (interview)
**Situation:** Your claims platform supports 28 insurer adapters, each keyed by `payerId`. New engineers add `if/else` branches in `ClaimsRouter` for every onboarding. Tests require booting all adapters; a typo in payer code fails at runtime in production.
**What they're testing:** Replacing conditional routing with registration, startup validation, and safe extensibility.
**Model answer:** I'd introduce a `PayerAdapterRegistry` populated at startup—each adapter implements `PayerAdapter` and registers via Spring `@Component` + custom `RegistryPostProcessor` or simple `Map<String, PayerAdapter>` injection of `List<PayerAdapter>`. Lookup: `registry.get(payerId)` throws `UnknownPayerException` at route time; fail-fast at startup if duplicate keys or missing mandatory payers for enabled tenants. New insurers ship a JAR with adapter bean—no edits to `ClaimsRouter`. For dynamic onboarding, back registry with DB config but cache read-only snapshots refreshed on event. Testing: mock registry with single adapter—no full classpath. I'd distinguish Registry from Service Locator: registry is often immutable after init and injected, not queried statically. Observability: log payer resolution on every claim with adapter version. Document thread-safety if hot-reload is required—copy-on-write map swap beats synchronized `HashMap`.

#### What it is
Registry maintains a lookup table from identifiers to objects or factories. Clients resolve dependencies or strategies by key without hard-coding concrete types.

#### When to use / when NOT
- **Use:** Plugin architectures; strategy resolution by code; prototype/template catalogs; serializer/handler tables.
- **NOT:** General DI replacement; mutable global singletons without clear ownership; when `Map` injection in constructor is enough without ceremony.

#### Java / Spring example
```java
@Component
public class PayerAdapterRegistry {
    private final Map<String, PayerAdapter> byId;
    public PayerAdapterRegistry(List<PayerAdapter> adapters) {
        this.byId = adapters.stream()
            .collect(Collectors.toUnmodifiableMap(PayerAdapter::payerId, a -> a));
    }
    public PayerAdapter get(String payerId) {
        return Optional.ofNullable(byId.get(payerId))
            .orElseThrow(() -> new UnknownPayerException(payerId));
    }
}
```

#### Common mistakes
- Static mutable `HashMap`—race conditions and test pollution.
- Registering half-initialized objects—fail at startup instead.
- Using registry for request-scoped state—wrong lifecycle.

#### Follow-up (with answer)
**Q:** Registry vs Abstract Factory?
**A:** Abstract Factory creates families of related products behind one factory interface—emphasis on object creation. Registry is a lookup table—may hold instances, classes, or lambdas; it doesn't imply product families. You might register `AbstractFactory` implementations by region in a registry. Use factory when construction logic is cohesive; use registry when many independent plugins register themselves by key.

---

### P143. Repository

**Category:** Enterprise
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/repository/)

**Short answer:** Repository mediates between domain and data mapping, presenting a collection-like API for aggregates—`findById`, `save`, `delete`—hiding SQL/JPA details. It keeps domain pure and persistence replaceable. Trade-off: anemic repositories that leak query language (`findByStatusAndDate`) become DAOs with extra steps; aggregate boundaries matter.

#### Scenario (interview)
**Situation:** `OrderRepository` exposes 47 query methods; services call `findByCustomerAndStatusAndDateRange` directly. Domain `Order` entity is `@Entity` with JPA annotations everywhere. Unit tests need `@DataJpaTest` for any service test.
**What they're testing:** Repository as aggregate persistence boundary vs query dumping ground; domain-driven persistence design.
**Model answer:** I'd refactor toward Repository as port for the `Order` aggregate root only—`Optional<Order> byId(OrderId)`, `void save(Order)`, `void remove(Order)`. Cross-aggregate queries move to read models (CQRS) or specification objects explicitly named `OrderQueryPort` for reporting—not bloated repository interfaces. Strip JPA from domain: `Order` is pure; `OrderJpaEntity` + mapper in infrastructure. Services depend on `OrderRepository` interface in domain module. Tests use in-memory fake implementing the port. Complex list screens get dedicated `OrderSummaryProjection` queries via `@Query` in infra, not 30 derived method names on one interface. I'd enforce: one repository per aggregate root; no `save` on child entities directly. Transaction boundaries at application service layer. This aligns with Fowler's Repository—not Spring Data magic `@Repository` on every table. Migration path: extract interface, move Spring Data impl to `infra`, deprecate leaky query methods per screen.

#### What it is
Repository encapsulates persistence and retrieval of domain objects, mimicking an in-memory collection while delegating to data mapping (JPA, JDBC, NoSQL).

#### When to use / when NOT
- **Use:** Domain-driven design; swappable persistence; testability via fakes; clear aggregate persistence.
- **NOT:** Simple CRUD with no domain model—Transaction Script + DAO may suffice; when repository mirrors every DB table 1:1 without aggregate thinking.

#### Java / Spring example
```java
// domain port
public interface OrderRepository {
    Optional<Order> findById(OrderId id);
    void save(Order order);
}
// infra
@Repository
class JpaOrderRepository implements OrderRepository {
    private final OrderJpaRepository jpa;
    public void save(Order order) { jpa.save(mapper.toEntity(order)); }
}
```

#### Common mistakes
- Repository per table instead of per aggregate—broken invariants.
- Exposing `Page<Entity>` with 15 joins—belongs in query side.
- Domain depending on Spring Data interfaces—layer violation.

#### Follow-up (with answer)
**Q:** Spring Data JPA repository vs DDD Repository?
**A:** Spring Data generates implementation from interface method names—convenient but tempts query sprawl on entity types. DDD Repository is a domain concept: collection semantics for aggregate roots, explicit about consistency boundaries. Bridge them: domain defines `OrderRepository` port; infrastructure adapter wraps `JpaRepository<OrderJpaEntity, UUID>` plus mapper. Never let domain extend `JpaRepository`—that's DAO with extra annotations.

---

### P144. Resource Acquisition Is Initialization (RAII)

**Category:** Performance
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/raii/)

**Short answer:** RAII binds resource lifetime to object lifetime—acquire in constructor, release in destructor/finalizer scope exit. Java lacks deterministic destructors, so the idiom maps to try-with-resources, `AutoCloseable`, and scope-bound clients. Trade-off: relying on `finalize()` or forgetting to close wrappers still leaks pools and file handles.

#### Scenario (interview)
**Situation:** Production logs show "Connection is not available, request timed out after 30000ms" on HikariCP during batch jobs. Heap dump reveals 12k idle JDBC connections held by worker threads that acquired connections but never returned them after early `return` on validation failures.
**What they're testing:** Resource lifecycle discipline in Java without C++ destructors.
**Model answer:** This is RAII failure in Java terms—resources acquired without guaranteed release on all exit paths. I'd audit every `getConnection()` and ensure try-with-resources or Spring `@Transactional` boundaries own the lifecycle. For manual JDBC: `try (Connection c = dataSource.getConnection(); PreparedStatement ps = ...) { ... }`. For custom locks/semaphores, wrap in `AutoCloseable` helper: `try (var lease = pool.acquire()) { ... }` where `close()` releases. Never store connection in instance fields across requests. Batch jobs: one transaction per chunk, not one connection for entire 6-hour run. Enable Hikari leak detection (`leakDetectionThreshold`) in staging to catch offenders. Static analysis: SpotBugs resource leak rules. Educate team: Java RAII = lexical scope via try-with-resources, not GC. For reactive code, use `using()` operator to bind subscription lifecycle. Metrics: pool active vs idle, thread dump on timeout.

#### What it is
RAII ties resource acquisition to object initialization and release to scope destruction. In Java, `AutoCloseable` + try-with-resources emulates deterministic cleanup when leaving a block.

#### When to use / when NOT
- **Use:** Files, sockets, DB connections, locks, native handles; any scarce resource.
- **NOT:** Long-lived pooled resources where close means return-to-pool—use pool APIs correctly; relying on `finalize()` (deprecated/unreliable).

#### Java / Spring example
```java
try (InputStream in = s3Client.getObject(bucket, key);
     OutputStream out = new FileOutputStream(dest)) {
    in.transferTo(out);
}
// Spring @Transactional: connection bound to thread, released after method
```

#### Common mistakes
- Catching exception inside try-with-resources then swallowing—close still runs, but state may be inconsistent.
- Holding connections across async boundaries—thread handoff loses TX scope.
- Custom resources without `AutoCloseable`—callers forget manual cleanup.

#### Follow-up (with answer)
**Q:** How does RAII relate to Execute Around?
**A:** Execute Around wraps resource setup/teardown around a callback—`template.execute(conn -> { ... })`—Spring's `JdbcTemplate` and try-with-resources both embody it. RAII is the C++ lifetime binding concept; Execute Around is the Java functional pattern achieving the same guarantee. Prefer try-with-resources for simple scope; Execute Around when framework controls acquisition (transaction manager opens connection before your lambda).

---

### P145. Retry

**Category:** Microservices
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/retry/)

**Short answer:** Retry re-executes failed operations when failures are transient—network blips, 503s, deadlock rollbacks. Requires exponential backoff, jitter, max attempts, and idempotency keys. Trade-off: blind retries amplify outages ("retry storm") and duplicate side effects without idempotent design.

#### Scenario (interview)
**Situation:** Payment capture calls a card processor; intermittent `503` causes Spring Retry to attempt 5 times instantly, triggering processor rate limits. Worse, two captures succeed for one checkout—customer charged twice.
**What they're testing:** Retry policy design, idempotency, which errors are retryable, and backoff.
**Model answer:** I'd classify errors: retry `503`, `429`, connect timeouts; never retry `400`, `402`, `404`, or business declines. Configure exponential backoff with jitter—e.g., 200ms, 400ms, 800ms ± random—max 3 attempts, total deadline under checkout UX SLA (8s). Use Resilience4j `@Retry` or Spring Retry with custom `RetryPolicy`. Idempotency: send `Idempotency-Key: checkoutId` header; processor returns same result on replay. Persist outbound attempt log before call—state machine `PENDING/SUCCEEDED/FAILED` prevents duplicate capture on client retry + server retry overlap. Circuit breaker opens when error rate spikes—stop retrying into a fire. Alert on retry exhaustion rate. I'd separate user-initiated resubmit from automatic retry. Tests: wiremock 503 twice then 200—single charge. Document that messaging consumers also retry—same idempotency keys end-to-end.

#### What it is
Retry intercepts failures and re-invokes an operation according to policy until success or exhaustion. It assumes failures are temporary and operations are safe to repeat.

#### When to use / when NOT
- **Use:** Transient network/infra failures; idempotent reads; deadlock retry on DB.
- **NOT:** Non-idempotent writes without keys; permanent errors; when circuit breaker indicates systemic failure; infinite retry without backoff.

#### Java / Spring example
```java
@Retry(name = "payments", fallbackMethod = "captureFallback")
public CaptureResult capture(CaptureRequest req) {
    return processorClient.capture(req.withIdempotencyKey(req.checkoutId()));
}
// resilience4j.yml: exponentialBackoff, maxAttempts: 3, enableExponentialBackoff: true
```

#### Common mistakes
- Retrying on timeout without knowing if server processed—needs idempotency query.
- No jitter—synchronized retries hammer recovering service.
- Retry on all `Exception`—masks programming bugs.

#### Follow-up (with answer)
**Q:** Retry vs Circuit Breaker?
**A:** Retry handles transient single-call failure—try again locally. Circuit breaker stops calling a failing dependency entirely after threshold failures, fast-failing while it recovers—protects both caller and callee. Compose: retry bounded attempts per call, breaker opens on sustained failure rate. Never infinite retry through a closed breaker—fail fast and surface degraded UX.

---

### P146. Role Object

**Category:** Structural
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/role-object/)

**Short answer:** Role Object models dynamic behavior by attaching role objects to a core entity at runtime—`Customer` plays `Borrower`, `Investor`, `Guarantor` roles—instead of deep inheritance trees. Roles can be added/removed as business state changes. Trade-off: indirection and consistency rules across roles require clear orchestration.

#### Scenario (interview)
**Situation:** A banking `Account` hierarchy has `SavingsAccount`, `LoanAccount`, `BrokerageAccount`, and now product wants joint accounts that combine savings + overdraft + brokerage features. Subclass explosion makes `JointPremiumAccount extends SavingsAccount` unmaintainable; duplicate identity fields across roles.
**What they're testing:** Composition over inheritance for evolving product matrices; runtime feature attachment.
**Model answer:** I'd refactor to a core `Party` or `Account` identity with pluggable `Role` objects: `SavingsRole`, `CreditLineRole`, `TradingRole`, each encapsulating state and behavior for that capability. An account holds `Set<Role>`; operations dispatch to the responsible role—`account.role(CreditLineRole.class).draw(amount)`. Opening overdraft attaches `CreditLineRole`; closing removes it after settlement. Benefits: product bundles are role combinations, not new classes; same customer entity plays `Borrower` on one account and `Guarantor` on another. Persistence: roles as separate tables keyed by accountId + roleType, or JSON column with typed deserialization. Validation: incompatible roles rejected at attach time (no two conflicting trading policies). Testing: attach mock roles without subclass zoo. Contrast with Type Object for data-driven variety; Role Object for behavior bundles. Migration: extract methods from subclasses into role classes incrementally.

#### What it is
Role Object attaches and detaches role instances to a core object at runtime. The core delegates behavior to attached roles, supporting flexible combination without inheritance explosion.

#### When to use / when NOT
- **Use:** Objects changing behavior over lifetime; product feature matrices; same entity in multiple contextual roles.
- **NOT:** Stable type hierarchies with few variants; when simple composition or strategy per method suffices; overkill for CRUD entities.

#### Java / Spring example
```java
public class Account {
    private final Map<Class<? extends Role>, Role> roles = new HashMap<>();
    public <R extends Role> R role(Class<R> type) {
        return type.cast(roles.get(type));
    }
    public void attach(Role role) { roles.put(role.getClass(), role); }
}
```

#### Common mistakes
- God core object that knows every role's internals—roles should encapsulate.
- No validation on incompatible role combinations.
- Persisting roles without versioned schema—upgrade pain.

#### Follow-up (with answer)
**Q:** Role Object vs Decorator?
**A:** Decorator wraps an object to add layered behavior transparently—stackable, usually same interface, often at decoration time. Role Object models domain roles with identity (`Borrower`, `Admin`) attached/detached over lifecycle—core knows it has roles. Decorator is structural wrapping; Role Object is domain modeling for dynamic classification. Use Decorator for cross-cutting enrichment; Role Object for business hats an entity wears.

---

### P147. Rule Engine

**Category:** Behavioral
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/rule-engine/)

**Short answer:** Rule Engine externalizes business rules into declarative facts + rules evaluated by an engine—Drools, Easy Rules—so policy changes don't require code deploys. Supports complex boolean networks, scoring, eligibility. Trade-off: rule debugging, test data setup, and performance profiling are harder than plain code for simple logic.

#### Scenario (interview)
**Situation:** Insurance underwriting has 300+ eligibility rules changed weekly by actuaries. Developers merge `if` chains daily; production incidents trace to wrong operator precedence in nested conditions copied from spreadsheets.
**What they're testing:** When externalized rules beat code; governance, testing, and hot-reload boundaries.
**Model answer:** I'd introduce a Rule Engine with actuary-owned rule sets versioned in Git (`underwriting-v2024-09.drl` or decision tables). Facts: `Applicant`, `PolicyRequest`, `RiskScore`. Rules express spreadsheet logic declaratively with salience and agenda groups for phases (knockout → rating → exceptions). CI runs golden-file tests: given fact fixtures, assert decision and premium band. Runtime: load ruleset version pinned per quote session—reproducibility for audits. Performance: Rete algorithm caches for repeated facts; benchmark p99 under peak quote volume; fall back to compiled rule subsets for hot paths. I'd keep regulatory constants in code, not rules—separation of law vs policy. Observability: explain trace (`why declined?`) for customer service. Anti-pattern: entire application in rules—use for volatile decision logic only. Compare to hardcoded Strategy map—rules win when non-devs maintain logic and combinatorics explode.

#### What it is
Rule Engine separates rule definitions from execution infrastructure. Facts enter a working memory; rules fire when conditions match, producing actions or derived facts.

#### When to use / when NOT
- **Use:** Complex, changing business rules; expert-maintained policies; eligibility/scoring/fraud patterns.
- **NOT:** Few stable rules better as code; when team lacks rule governance; ultra-low-latency paths without profiling.

#### Java / Spring example
```java
@Service
public class UnderwritingService {
    private final KieContainer kie;
    public Decision evaluate(ApplicantFacts facts) {
        var session = kie.newKieSession();
        session.insert(facts);
        session.fireAllRules();
        return facts.getDecision();
    }
}
```

#### Common mistakes
- No version pinning—audit cannot reproduce old decisions.
- Rules calling external HTTP synchronously—non-deterministic, slow.
- Missing explanation/trace—CS cannot answer decline reasons.

#### Follow-up (with answer)
**Q:** Rule Engine vs Strategy pattern?
**A:** Strategy encapsulates interchangeable algorithms in code classes selected at runtime—developers own change cycle. Rule Engine externalizes declarative conditions/actions often editable by domain experts with engine semantics (salience, RETE). Use Strategy for 4–8 stable algorithms; Rule Engine for hundreds of volatile rules with non-developer authors. Hybrid: engine outputs strategy key, code executes side effects.

---

### P148. Saga

**Category:** Microservices
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/saga/)

**Short answer:** Saga manages distributed transactions as a sequence of local transactions with compensating actions on failure—no 2PC. Choreography (events) or orchestration (coordinator) coordinates steps across services. Trade-off: eventual consistency, complex failure modes, and compensations must be business-meaningful, not just DB rollback.

#### Scenario (interview)
**Situation:** Trip booking reserves flight, hotel, and car across three microservices. Hotel reservation succeeds; car rental fails—flight ticket already issued. Users demand no orphan charges; finance requires audit trail of partial bookings.
**What they're testing:** Distributed TX without XA; compensation design; orchestration vs choreography choice.
**Model answer:** I'd model Trip Booking as a Saga with steps: reserve flight → reserve hotel → reserve car → capture payment, each a local TX in its service. On car rental failure, run compensations in reverse: cancel hotel, cancel flight (or convert to credit per policy). Orchestration via `TripSagaOrchestrator` state machine persisted in `saga_instances` table—clear visibility vs event-only choreography where failure detection is harder. Each step idempotent with `sagaId` + `stepId`. Compensations are business operations (`CancelFlightCommand`), not DELETE rows—may incur fees. Timeout per step; after TTL, auto-compensate. Never hold DB locks across services. Outbox events drive async steps where possible. UX: `PENDING` status with webhook on completion/failure. Tests: fail each step, assert compensations called once. Compare to 2PC: saga accepts temporary inconsistency windows—UI must communicate. Choose orchestration when flow is complex; choreography when steps are loosely coupled and few.

#### What it is
Saga is a long-lived transaction split into local transactions. If a step fails, previous steps are undone via compensating transactions that semantically reverse effects.

#### When to use / when NOT
- **Use:** Microservices spanning multiple databases; long-running business processes; when 2PC unavailable.
- **NOT:** Single monolith with one database—use `@Transactional`; when strong immediate consistency is mandatory everywhere.

#### Java / Spring example
```java
@Service
public class TripSagaOrchestrator {
    @Transactional
    public void onStepFailed(SagaId id, Step step) {
        sagaRepo.find(id).compensateFrom(step); // publish Cancel* commands
    }
}
```

#### Common mistakes
- Compensations that can't run twice—not idempotent.
- Missing timeout handling—sagas stuck IN_PROGRESS forever.
- Choreography without correlation—can't trace failure across services.

#### Follow-up (with answer)
**Q:** Saga vs Two-Phase Commit?
**A:** 2PC blocks resources until coordinator commits—all participants atomically visible, poor availability, rarely used across microservices. Saga commits each step locally immediately, accepting temporary inconsistency until completion or compensation—better availability, harder application logic. Use saga for inter-service workflows; local `@Transactional` inside each step. Consumers must tolerate in-between states.

---

### P149. Separated Interface

**Category:** Enterprise
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/separated-interface/)

**Short answer:** Separated Interface places the interface in a different package/module from its implementation so dependents compile only against the contract—domain doesn't depend on infrastructure. Hexagonal ports are separated interfaces. Trade-off: more modules and mapping; avoid interface-per-class ceremony without boundary value.

#### Scenario (interview)
**Situation:** Your domain module imports `spring-data-jpa`, AWS SDK, and Stripe client JARs because service interfaces reference `JpaRepository`, `S3Object`, and Stripe types. A lightweight CLI tool that should reuse domain logic pulls 200MB of dependencies and fails license review.
**What they're testing:** Dependency direction, modular architecture, and port/adapter boundaries.
**Model answer:** I'd apply Separated Interface: define `PaymentPort`, `ObjectStoragePort`, `OrderRepository` in `domain`/`application` module with only JDK types and domain models. Implementations `StripePaymentAdapter`, `S3StorageAdapter`, `JpaOrderRepository` live in `infrastructure` module depending inward. Domain compiles with zero framework deps. CLI depends only on `application` + in-memory fakes for integration tests. Package naming: `com.acme.order.application.port.out.PaymentPort`. No leakage of `ResponseEntity`, `@Entity`, or SDK builders across boundary—map at adapter edge. Enforce with ArchUnit: `domain..` must not depend on `infra..` or `org.springframework..`. Each port justified by test substitution or alternate impl—not every class needs interface. Version ports when breaking; adapters shim multiple SDK versions. This is Fowler's Separated Interface, foundation of ports in hexagonal architecture.

#### What it is
Separated Interface defines a contract in one layer/package and implements it elsewhere, ensuring clients depend on abstractions physically decoupled from implementation details.

#### When to use / when NOT
- **Use:** Hexagonal/clean architecture; multiple implementations; publishing domain jars without infra; test doubles.
- **NOT:** Single-module toy apps; interface mirroring one class with no alternate impl or testing benefit.

#### Java / Spring example
```java
// module: application
public interface PaymentPort {
    PaymentResult charge(Money amount, CustomerId customer);
}
// module: infrastructure
@Component
class StripePaymentAdapter implements PaymentPort { ... }
```

#### Common mistakes
- Interface polluted with framework types—boundary not clean.
- Domain calling `new StripePaymentAdapter()`—defeats separation.
- One giant `Service` interface—split by use case ports.

#### Follow-up (with answer)
**Q:** Separated Interface vs Dependency Injection?
**A:** Separated Interface is a structural pattern—where the interface lives relative to implementation. Dependency Injection is how implementations are supplied at runtime—constructor injection, Spring beans. You typically combine them: port interface in domain, adapter impl in infra, injected by DI container. Separated Interface without DI still works manually in tests; DI without separation often colocates interface and impl in same package with less modular enforcement.

---

### P150. Serialized Entity

**Category:** Enterprise
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/serialized-entity/)

**Short answer:** Serialized Entity stores an object graph as a serialized blob (JSON, XML, Java serialization) in a single DB column—useful for snapshotting, audit, or schema-flexible document fragments. Trade-off: querying inside the blob is awkward; migration requires deserialization transforms; avoid Java native serialization for security.

#### Scenario (interview)
**Situation:** Compliance requires storing the exact quote configuration shown to the customer at bind time—30 nested objects, optional riders, jurisdiction-specific riders added weekly. Relational normalization would mean 12 join tables versioned per state regulatory change.
**What they're testing:** When blob snapshot beats normalized schema; immutability, audit, and read patterns.
**Model answer:** I'd persist a `QuoteSnapshot` as Serialized Entity—`quote_bind_events` table with `id`, `policyId`, `boundAt`, `schemaVersion`, `payload JSONB`. On bind, serialize immutable DTO graph (not live JPA entity) to JSON with version tag. Reads for disputes deserialize by version—maintain `QuoteSnapshotReaderV3` for old payloads. Never update blob in place; append new snapshot rows. Index metadata columns (`policyId`, `boundAt`) for lookup; use JSONB operators only for analytics, not hot path. Reject Java serialization—RCE risk, opaque. Migration: upcast pipeline when `schemaVersion < current`. Contrast with Serialized LOB for large docs; this is bounded domain snapshot. Tests: golden JSON fixtures per version. If regulators need queryable fields, promote only those columns, keep rest in blob. Document that ORM `@Lob` on entity graph causes lazy-load surprises—serialize explicit DTO in service layer.

#### What it is
Serialized Entity persists a complete object structure as a serialized form in the database, treating the blob as the authoritative stored representation of that graph at a point in time.

#### When to use / when NOT
- **Use:** Audit snapshots; infrequently queried document state; rapid schema evolution on nested optional data.
- **NOT:** Primary query dimensions inside nested data; frequently updated partial fields; when relational model is stable and reportable.

#### Java / Spring example
```java
@Entity
class QuoteBindEvent {
    @Column(columnDefinition = "jsonb")
    private String snapshotJson; // written via objectMapper.writeValueAsString(dto)
    private int schemaVersion;
}
```

#### Common mistakes
- Serializing JPA entities with lazy collections—`LazyInitializationException` or huge graphs.
- Java native `ObjectOutputStream`—security and compatibility nightmares.
- Updating snapshots instead of appending—breaks audit trail.

#### Follow-up (with answer)
**Q:** Serialized Entity vs Event Sourcing?
**A:** Serialized Entity stores a point-in-time state snapshot as one blob—optimized for "what did they see then?" Event Sourcing stores immutable sequence of domain events that replay to current state—optimized for temporal queries and rebuilding projections. Snapshots can complement event sourcing as performance optimization. Use serialized entity for legal/audit freeze; event sourcing for full history and multiple read models.

---

### P151. Serialized LOB

**Category:** Enterprise
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/serialized-lob/)

**Short answer:** Serialized LOB stores large opaque objects—PDFs, images, XML payloads, big JSON documents—as Large Objects in the database (BLOB/CLOB) or delegates to object storage while keeping a reference LOB. Trade-off: DB bloat, backup/restore cost, and streaming performance—often better suited to S3 with DB metadata only.

#### Scenario (interview)
**Situation:** Medical records store DICOM imaging studies inline as `BYTEA` in Postgres. Database size triples yearly; nightly backups miss the SLA window; radiologist viewer loads entire 400MB study into heap even for thumbnail view.
**What they're testing:** LOB storage trade-offs, streaming, and when DB is wrong place for large binaries.
**Model answer:** Serialized LOB pattern here means persisting large serialized content as a LOB field—but at 400MB per study, I'd split: metadata + series index in relational tables, bulk pixels in object storage (S3/Azure Blob) with content-addressed keys, DB holds `storageKey`, `checksum`, `sizeBytes`, `contentType`. Viewer requests byte-range reads from storage API, not full LOB load. If regulatory mandate requires DB residency, use Postgres Large Objects with streaming `InputStream`, never `byte[]` in entity. Hibernate: `@Lob` with `Blob` lazy; `MaterializedBlob` only for small docs. Migration: background job copies BYTEA to S3, replaces with pointer, verify checksum. Backup strategy separates blob store lifecycle policies. For moderate XML config (<64KB), inline CLOB is fine. Monitor connection hold time during LOB reads—long transactions block pool. Serialized LOB differs from Serialized Entity—LOB emphasizes size/opaque bytes, not domain object graphs.

#### What it is
Serialized LOB persists large binary or character objects as database LOB types or serialized large payloads, optionally streaming rather than materializing entirely in memory.

#### When to use / when NOT
- **Use:** Moderate-size documents tied transactionally to row; legacy systems requiring DB residency; atomic row+blob commit.
- **NOT:** Multi-MB media at scale—object storage + metadata; when content needs CDN edge delivery.

#### Java / Spring example
```java
@Entity
class ImagingStudy {
    private String objectStorageKey; // preferred
    private Long sizeBytes;
    // legacy: @Lob @Basic(fetch = LAZY) private Blob dicomBlob;
}
```

#### Common mistakes
- Loading full LOB into `byte[]` on every list query—select metadata only.
- Storing videos in DB because "transactions are easier"—operational tax for years.
- No checksum—silent corruption undetected.

#### Follow-up (with answer)
**Q:** When is DB LOB still correct?
**A:** When blob and row must commit atomically in one DB transaction under strict compliance, blob is small (<1MB), access is infrequent, and ops team accepts backup cost. Medical billing PDFs (200KB) inline can be simpler than S3 for a small clinic app. Re-evaluate when backup duration or restore RTO degrades—signal to externalize.

---

### P152. Servant

**Category:** Behavioral
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/servant/)

**Short answer:** Servant separates behavior from classes in a hierarchy by placing operations in a separate servant class that acts on multiple target types—avoiding bloated base classes. Common in graphics ("draw all shapes") or batch operations across unrelated entities. Trade-off: servant can become a god class without cohesive operation grouping.

#### Scenario (interview)
**Situation:** `Exportable` interface with `toCsv()` implemented by 22 domain types. Half override with blank stubs; adding `toParquet()` forces touching every class. Some entities shouldn't export PII fields but inherited default exports everything.
**What they're testing:** Moving cross-cutting multi-type operations out of domain classes; cohesion vs coupling.
**Model answer:** I'd replace per-class export methods with Export Servant: `ClaimExportServant`, `PolicyExportServant` know how to render each type without those types implementing export interface. Domain stays pure; servant uses public getters or visitor-like dispatch `export(Object entity, ExportFormat fmt)`. PII rules centralized in `PiiMaskingServant` applied before write. Adding Parquet means new `ParquetExportServant`, not 22 file edits. For polymorphic collections: registry maps `Class<?>` to exporter function. Testing: servant unit tests with fixture entities—no stub `toCsv()` on domain. Contrast Facade: servant operates on many types with shared algorithm; facade simplifies one subsystem API. Watch servant size—split by bounded context (`BillingExportServant` vs `ClaimsExportServant`). Anti-pattern: servant reaching private fields via reflection—use intentional read interfaces or DTO projection.

#### What it is
Servant defines an object that performs an operation on behalf of other objects across a set of classes, keeping targets ignorant of the operation and avoiding a common superclass for behavior.

#### When to use / when NOT
- **Use:** Operations spanning many unrelated classes; batch utilities; keeping domain free of presentation/export concerns.
- **NOT:** Behavior intrinsic to one type—belongs on the class; when Visitor with stable type hierarchy is clearer.

#### Java / Spring example
```java
@Component
public class ClaimExportServant {
    public void writeCsv(Claim claim, Writer out) {
        csv.writeRow(claim.id(), mask(claim.ssn()), claim.amount());
    }
}
```

#### Common mistakes
- Servant with business rules that belong in domain services—layer confusion.
- One mega `UtilityService` for all cross-type ops—split by capability.
- Breaking encapsulation via reflection instead of projection DTOs.

#### Follow-up (with answer)
**Q:** Servant vs Visitor?
**A:** Visitor distributes double-dispatch across a stable element hierarchy—each element `accept(Visitor)`. Servant centralizes operation in one class operating on heterogeneous objects without requiring elements to know visitor protocol—often via overloads or registry. Visitor excels when types are fixed and operations vary; Servant when types vary widely and one operation (export, validate batch) crosses them without modifying types.

---

### P153. Server Session

**Category:** Enterprise
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/server-session/)

**Short answer:** Server Session stores client interaction state on the server keyed by session ID—shopping carts, auth context, multi-step wizards—while the client holds only a token (cookie). Trade-off: sticky sessions or distributed session stores needed at scale; stateful servers complicate horizontal scaling without Redis session replication.

#### Scenario (interview)
**Situation:** After scaling Spring Boot from 4 to 40 pods behind a load balancer, users randomly lose shopping carts and MFA step-up resets mid-flow. Sessions were default in-memory Tomcat sessions with no affinity.
**What they're testing:** Session clustering, stateless JWT vs server session, and what belongs in session.
**Model answer:** Root cause: non-replicated Server Session state on individual pods—next request hits another pod with empty session. Fixes in order: (1) Externalize session to Redis via Spring Session—`spring-session-data-redis`, same session ID across pods. (2) Minimize session payload—store `cartId` UUID referencing DB/Redis cart, not full line items in session. (3) Short TTL + sliding renewal; explicit logout invalidates server-side. (4) For MFA wizard, prefer signed state token or `step-up` cache keyed by `sub+device` rather than bloated session. Avoid sticky sessions alone—they mask problem and hurt failover. Security: `HttpOnly`, `Secure`, `SameSite` cookies; rotate session ID on login. Contrast Client Session (state on client)—server session when data must not leak/tamper on client. Metrics: session creation rate, Redis memory, serialization size. I'd document max session attributes and forbid storing non-serializable service beans in session (common leak).

#### What it is
Server Session maintains per-user state on the server between HTTP requests, identified by a session token, enabling stateful interactions over stateless HTTP.

#### When to use / when NOT
- **Use:** Multi-step flows; server-side cart; sensitive interim state; CSRF tokens bound to session.
- **NOT:** Everything in JWT bloating cookies; microservices sharing monolith session without boundary; long-lived large objects in session.

#### Java / Spring example
```java
@EnableRedisHttpSession(maxInactiveIntervalInSeconds = 1800)
public class SessionConfig {}
// controller: session.setAttribute("cartId", cartId);
```

#### Common mistakes
- Storing large object graphs in session—serialization cost on every request.
- Relying on sticky sessions without external store—pod death loses session.
- Putting Spring singleton beans in session—memory leak and stale state.

#### Follow-up (with answer)
**Q:** Server Session vs JWT stateless auth?
**A:** Server Session keeps authoritative state server-side; client holds opaque ID—good for revocable sessions, small cookies, sensitive cart data. JWT embeds claims client-side—scales horizontally without session store but harder to revoke instantly and tempts storing too much in token. Hybrid: short-lived JWT for identity + server session or Redis for volatile workflow state. Choose session when you need immediate invalidation and minimal client exposure.

---

### P154. Service Layer

**Category:** Enterprise
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/service-layer/)

**Short answer:** Service Layer defines an application's boundary of business operations—transaction boundaries, orchestration, authorization—sitting above domain model and below presentation. Controllers stay thin; repositories stay persistence-focused. Trade-off: anemic services that only delegate to DAOs add indirection without encapsulating rules.

#### Scenario (interview)
**Situation:** REST controllers contain 200-line `placeOrder` methods with `@Transactional`, discount logic, inventory calls, and email triggers. Duplicate order placement logic exists in a Kafka consumer and a batch reprocessor.
**What they're testing:** Layering discipline, transaction demarcation, reuse across entry points.
**Model answer:** I'd extract `OrderApplicationService.placeOrder(PlaceOrderCommand)` as the Service Layer—single orchestration point for all entry channels. Controller: validate HTTP, map DTO → command, call service, map result. Service: start TX, load aggregates via repositories, invoke domain methods (`order.applyDiscount()`), call ports (inventory, payment), publish domain events, commit. Kafka consumer maps event → same command—no duplicated rules. Transaction boundary on service public methods only; domain stays TX-agnostic. Authorization: `@PreAuthorize` on service or policy objects inside service—not scattered in controllers. Service Layer is not a god class: split by use case (`OrderPlacementService`, `OrderCancellationService`). Avoid anemic domain—if `if (stock < qty)` lives only in service, push to `OrderLine.reserve()`. Integration tests hit service with test containers; controller tests mock service. Fowler's Service Layer coordinates; domain holds invariants.

#### What it is
Service Layer encapsulates business logic, defines transaction boundaries, and coordinates domain objects and infrastructure without containing presentation or persistence details.

#### When to use / when NOT
- **Use:** Enterprise apps with clear use cases; multiple UI/API entry points; transaction orchestration.
- **NOT:** Domain logic-less CRUD pass-through—consider Transaction Script; reactive pipelines where layer boundaries blur intentionally.

#### Java / Spring example
```java
@Service
@Transactional
public class OrderApplicationService {
    public OrderId placeOrder(PlaceOrderCommand cmd) {
        var order = Order.create(cmd);
        inventoryPort.reserve(order);
        orders.save(order);
        events.publish(new OrderPlaced(order.id()));
        return order.id();
    }
}
```

#### Common mistakes
- Fat controllers, anemic domain—business rules in web layer.
- Multiple `@Transactional` nested services with wrong propagation—partial commits.
- Service calling service in circles—extract domain or split bounded contexts.
- Leaking `HttpServletRequest` into service layer—presentation pollution.
- One `BusinessService` class for entire application—unmaintainable.

#### Follow-up (with answer)
**Q:** Service Layer vs Domain Model?
**A:** Domain Model places behavior on entities/value objects; Service Layer coordinates them for application use cases. Services should be thin orchestrators when domain is rich—fat services signal anemic domain. Transaction Script skips rich domain and puts procedural logic in service methods—OK for simple apps. Senior choice: rich domain + slim application services for complex invariants; Transaction Script for reporting ETL.

---

### P155. Service Locator

**Category:** Enterprise
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/service-locator/)

**Short answer:** Service Locator provides a global registry where code requests dependencies by name/type at runtime—`ServiceLocator.get(PaymentGateway.class)`—instead of constructor injection. Trade-off: hides dependencies, hurts testability, and obscures required collaborators—considered anti-pattern in modern Spring apps favoring explicit DI.

#### Scenario (interview)
**Situation:** Legacy module uses `ServiceLocator.getInstance().lookup("PaymentService")` inside static helpers. New Spring beans can't be tested without bootstrapping the legacy locator; NPEs occur when lookup order wrong during startup.
**What they're testing:** Why Service Locator fell out of favor; migration path to DI without big-bang rewrite.
**Model answer:** Service Locator was a bridge before DI containers—global indirection couples callers to locator infrastructure and string names. I'd strangle: wrap locator lookups in adapter beans `@Component` implementing domain ports, injected via constructor in new code. For static helpers, pass dependencies as parameters or replace with injectable `@Component` services. Bridge pattern: Spring `ServiceLocatorFactoryBean` only at legacy boundary, shrinking over time. Tests: replace locator with test registry pre-populated with mocks—still worse than `@MockBean`. Document anti-pattern risks: hidden deps (can't see constructor), runtime failures vs compile-time, singleton assumptions. JNDI in Java EE was enterprise Service Locator—same critique. Never introduce new Service Locator in greenfield Spring—use constructor injection. If framework forces it (old EJB), isolate behind port interface. Metrics: count remaining `lookup(` calls sprint over sprint.

#### What it is
Service Locator is a central registry that components query to obtain dependencies dynamically, decoupling callers from concrete instantiation but coupling them to the locator mechanism.

#### When to use / when NOT
- **Use:** Legacy integration; plugin containers where DI unavailable; rare factory bridges.
- **NOT:** New Spring applications; when testability and explicit dependencies matter; static call sites.

#### Java / Spring example
```java
// legacy — avoid in new code
PaymentService ps = ServiceLocator.getInstance().get(PaymentService.class);
// modern replacement
@RequiredArgsConstructor
class CheckoutService { private final PaymentService payments; }
```

#### Common mistakes
- Static `getInstance()` in domain logic—untestable without global state.
- String-based JNDI names—refactor breaks at runtime.
- Mixing locator and injection in same class—double wiring confusion.

#### Follow-up (with answer)
**Q:** Service Locator vs Dependency Injection?
**A:** DI pushes dependencies into object at construction—explicit, testable, fail at startup if missing. Service Locator pulls dependencies when needed—implicit, caller depends on locator infrastructure. DI inverts control to container; locator inverts to global registry anti-pattern in Martin Fowler's critique. Prefer DI; use locator only as migration shim behind interfaces.

---

### P156. Service Stub

**Category:** Structural
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/service-stub/)

**Short answer:** Service Stub provides a local stand-in with the same interface as a remote service—returning canned data, recording calls, or simulating latency—for development and testing before the real service exists or is reachable. Trade-off: stubs drift from production contract without contract tests (Pact).

#### Scenario (interview)
**Situation:** Mobile team builds checkout against a payments API still in development. They point to a hand-written stub returning always-success; go-live week reveals field `captureMode` is required and amounts must be minor units—production rejects every transaction.
**What they're testing:** Stub fidelity, contract-driven development, and environment switching.
**Model answer:** I'd formalize Service Stub as versioned contract implementation: OpenAPI/Protobuf spec is source of truth; stub generated or validated against spec (WireMock, Prism). Stub lives in test scope and `local` profile Spring bean `@Primary` implementing `PaymentPort`. Record-replay: capture prod-like traffic in lower env for realistic stubs. CI runs consumer contract tests (Pact) so stub and real service both satisfy consumer expectations. Config switch: `payment.provider=stub|real` via properties—never compile-time flags. Stub simulates failures too—timeouts, 402, idempotency replay—not only happy path. Document divergence policy: when API changes, update spec → stub → service in same PR. For remote Proxy stub (RPC), use same DTOs as client library—no parallel class hierarchy. Before go-live, run integration suite against sandbox real API nightly. Service Stub differs from Mock in tests—stub is deployable fake service; mock is in-process test double.

#### What it is
Service Stub implements a service interface locally with predetermined or configurable responses, substituting for unavailable or expensive remote dependencies.

#### When to use / when NOT
- **Use:** Parallel development; offline dev; integration test harness; chaos/latency simulation.
- **NOT:** Production path without clear profile guard; stubs without contract validation—silent drift.

#### Java / Spring example
```java
@Profile("local")
@Primary
@Component
class StubPaymentAdapter implements PaymentPort {
    public CaptureResult capture(CaptureRequest r) {
        return CaptureResult.approved(r.idempotencyKey());
    }
}
```

#### Common mistakes
- Stub DTOs diverge from client SDK types.
- Happy-path-only stub—misses error handling until prod.
- Stub accidentally deployed to prod—profile misconfiguration.

#### Follow-up (with answer)
**Q:** Stub vs Mock vs Fake?
**A:** Mock is in-process test double with verification expectations (Mockito)—no network. Stub returns canned responses without behavior verification—WireMock HTTP server. Fake has working logic (in-memory H2 repo)—heavier but realistic. Service Stub usually means substitutable remote stand-in, often HTTP-level. Choose mock for unit tests; stub/fake for component tests; contract tests bind stub to real API.

---

### P157. Service to Worker

**Category:** Concurrency
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/service-to-worker/)

**Short answer:** Service to Worker splits request handling: a service layer coordinates and delegates CPU or I/O intensive work to a worker layer (often thread pool), keeping the service thin for dispatch and composition. Common in servlet + worker pool or front controller + `ExecutorService`. Trade-off: thread pool sizing and queue bounds determine whether you absorb load or reject work.

#### Scenario (interview)
**Situation:** Image upload API accepts files synchronously, runs virus scan + resize on the request thread. Under marketing campaign, Tomcat threads exhaust at 200 concurrent uploads; health checks fail even though CPU has headroom waiting on disk I/O.
**What they're testing:** Separating acceptance from worker execution; pool tuning; async response patterns.
**Model answer:** Apply Service to Worker: `UploadService` validates auth, stores raw file to temp storage, submits `ProcessImageJob` to bounded `ThreadPoolExecutor`, returns `202` with job ID. `ImageWorker` pulls jobs—scan, resize, move to CDN path, update status table. Service thread freed in milliseconds. Pool: core 16, max 32, queue 500, `CallerRunsPolicy` or reject with 503 when saturated—never unbounded queue hiding overload. Separate pools for CPU resize vs I/O scan if mixed workloads. Contrast Half-Sync/Half-Async: service synchronous to client optionally waits on `CompletableFuture` for small jobs. Observability: queue depth, worker utilization, job age. Idempotent job processing on retry. For Spring, `@Async` on worker methods with custom executor bean—not default unbounded simple async. Failure: service updates job `FAILED` with reason; client polls status endpoint. This pattern differs from Queue-Based Load Leveling when workers are in-process threads vs external queue consumers—but often combined with message queue for durability.

#### What it is
Service to Worker decouples coordination logic (service) from execution logic (worker), typically dispatching tasks to a worker tier or pool while the service handles orchestration and response assembly.

#### When to use / when NOT
- **Use:** Request thread must stay short; heterogeneous task steps; mixed I/O and CPU in background.
- **NOT:** Trivial fast operations where thread handoff overhead dominates; when durable queue needed across restarts—in-process workers alone insufficient.

#### Java / Spring example
```java
@Service
public class UploadService {
    private final ExecutorService workers;
    public JobId submit(MultipartFile f) {
        var id = store.save(f);
        workers.submit(() -> imageWorker.process(id));
        return id;
    }
}
```

#### Common mistakes
- `Executors.newCachedThreadPool()`—unbounded thread explosion.
- Sharing pool between unrelated domains—no isolation.
- No back-pressure when queue fills—OOM instead of reject.

#### Follow-up (with answer)
**Q:** Service to Worker vs Master-Worker?
**A:** Service to Worker emphasizes application layering—service coordinates, workers execute tasks, often same JVM. Master-Worker is parallel decomposition—master splits work into subtasks for homogeneous workers (ForkJoin, map reduce). Master-Worker focuses on divide-and-conquer parallelism; Service to Worker on not blocking the entry thread. Can combine: service submits to master which fans out to worker pool.

---

### P158. Session Facade

**Category:** Enterprise
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/session-facade/)

**Short answer:** Session Facade is a coarse-grained session bean (historically EJB) exposing a simplified API over fine-grained domain objects and transactions—one `placeOrder()` instead of clients manipulating five entities. In modern Spring, `@Transactional` application services play this role. Trade-off: facade can become god service without use-case splitting.

#### Scenario (interview)
**Situation:** A Swing desktop client (legacy) makes 40 remote EJB calls per screen load—network chattiness kills UX. Team debates fine-grained REST resources vs one BFF endpoint.
**What they're testing:** Coarse-grained API design, transaction boundaries, and chatty interface anti-pattern remediation.
**Model answer:** Session Facade pattern: expose `OrderSessionFacade.getOrderDashboard(orderId)` returning aggregated DTO—customer, lines, shipments, payments—in one `@Transactional(readOnly=true)` server round-trip. Internally facade orchestrates domain objects/repositories; client never calls `LineItemEntity` remotely. Modern equivalent: Spring `@RestController` delegates to `OrderQueryService` returning view model—not anemic CRUD on every table. Write side: `placeOrder` command on facade with single TX boundary. DTO sized for screen—no lazy-load over wire. For microservices, BFF is Session Facade per client channel. Performance: batch fetches, join queries, cache read models. Avoid facade leaking persistence entities—map to DTO. Split facades by actor (`CustomerOrderFacade`, `AdminOrderFacade`) not one 3k-line class. Historical EJB stateful session bean distinction: prefer stateless facade + client holds ID. Tests: facade integration test covers orchestration; domain unit tests stay below.

#### What it is
Session Facade provides a unified coarse-grained interface to a subsystem's business logic, typically controlling transaction demarcation and hiding interactions among domain objects.

#### When to use / when NOT
- **Use:** Remote clients needing few round-trips; complex multi-entity operations; clear use-case entry points.
- **NOT:** Exposing every table as CRUD then also a facade—pick granularity deliberately; internal in-process calls don't need facade over facade.

#### Java / Spring example
```java
@Service
@Transactional(readOnly = true)
public class OrderSessionFacade {
    public OrderDashboardView loadDashboard(OrderId id) {
        var order = orders.findById(id).orElseThrow();
        return mapper.toDashboard(order, shipments.forOrder(id), payments.forOrder(id));
    }
}
```

#### Common mistakes
- Returning JPA entities with lazy collections—serialization failures.
- One facade for entire enterprise—bounded context violation.
- Long-running work inside facade TX—holds DB locks.

#### Follow-up (with answer)
**Q:** Session Facade vs Facade (GoF)?
**A:** GoF Facade simplifies any subsystem interface (library, module). Session Facade is enterprise variant tied to session/transaction boundaries and coarse-grained remote access—historically stateful EJB session. Spring `@Service` application service is the modern Session Facade without EJB container. Both hide complexity; Session Facade additionally owns TX and remote granularity concerns.

---

### P159. Sharding

**Category:** Architectural
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/sharding/)

**Short answer:** Sharding partitions data across multiple databases by a shard key—`tenantId`, `userId`, geographic region—so each shard holds a subset, scaling write throughput and storage beyond single-node limits. Trade-off: cross-shard queries, resharding, and distributed transactions become hard—design shard key early.

#### Scenario (interview)
**Situation:** Multi-tenant SaaS on single Postgres hits 2TB and 8k write TPS; vertical scaling maxed. Largest tenant alone is 30% of data. Queries always filter by `tenant_id` except nightly global analytics job.
**What they're testing:** Shard key selection, tenant isolation, cross-shard operations, and migration strategy.
**Model answer:** I'd shard by `tenantId`—matches access pattern, keeps tenant data co-located, supports per-tenant export/compliance delete. Routing layer: `ShardResolver.tenant(tenantId) → DataSource`. Hibernate ShardingSphere or application-level `TenantRoutingDataSource`. Hot large tenant: sub-shard by `tenantId + hash(bucket)` to split one whale. Cross-shard analytics: async ETL to warehouse (Snowflake), not cross-shard JOIN in OLTP. Resharding: dual-write + backfill + cutover with consistency checks—never big-bang weekend unless rehearsed. Avoid shard key that causes hotspots—`country=US` for 90% traffic. Global sequences: UUID or snowflake IDs, not per-shard auto-increment collisions. Tests: integration per shard; chaos kill one shard—others unaffected. Document no foreign keys across shards—reference by ID only. Sharding vs read replicas: replicas help read scale, not write/storage ceiling.

#### What it is
Sharding horizontally partitions data across multiple independent databases, routing operations by a shard key so each shard contains a disjoint subset.

#### When to use / when NOT
- **Use:** Write/storage limits exceeded; natural partition key in queries; tenant isolation requirements.
- **NOT:** Small data; frequent cross-shard joins; before exhausting simpler scale options (indexes, replicas, archiving).

#### Java / Spring example
```java
@Component
public class TenantShardResolver {
    public DataSource resolve(TenantId tenant) {
        return shards.get(consistentHash(tenant.value()));
    }
}
```

#### Common mistakes
- Wrong shard key—resharding painful.
- Cross-shard ACID expectations—use saga or per-shard TX.
- Monotonic auto-increment IDs colliding across shards.

#### Follow-up (with answer)
**Q:** Sharding vs partitioning (Postgres table partitioning)?
**A:** Table partitioning splits one logical table inside one database instance—helps manageability and prune scans, limited write scale-out. Sharding splits across multiple DB instances—true horizontal scale for writes and storage. Partitioning first for time-series archive; sharding when single node capacity insufficient despite partitioning.

---

### P160. Single Table Inheritance

**Category:** Enterprise
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/single-table-inheritance/)

**Short answer:** Single Table Inheritance maps an entire class hierarchy to one database table with a discriminator column distinguishing subtypes—simple queries, but sparse nullable columns for subtype-specific fields. Trade-off: table width, null pollution, and index inefficiency as subtypes diverge.

#### Scenario (interview)
**Situation:** `Notification` hierarchy (`Email`, `Sms`, `Push`) mapped with JPA `@Inheritance(SINGLE_TABLE)`. Table has 40 columns; most rows null in 35 columns. Index on `phoneNumber` useless because 95% rows are email type.
**What they're testing:** JPA inheritance strategies, schema evolution, and query performance.
**Model answer:** Single Table Inheritance fits when subtypes share most fields and polymorphic queries are frequent—`SELECT * FROM notification WHERE user_id=?` returns mixed types. Here subtype-specific fields dominate—I'd migrate to `@Inheritance(JOINED)` or separate tables with `Notification` base + type-specific tables, or abandon inheritance mapping for composition (`notification` + `email_details`). Short-term: partial indexes per discriminator (`WHERE type='SMS'`) on Postgres. Hibernate discriminator: `@DiscriminatorColumn(name="type")`. Watch `@NotNull` on subtype fields—can't enforce in DB for single table. Reporting: materialized view per type. If only 3 shared columns and 10 unique each, single table is wrong—column count and row width bloat buffer pool. Migration: add joined tables, backfill, switch `@Inheritance`, drop nullable columns in phased release. Alternative: JSON column for variant payload with schema version—flexible but weaker DB constraints.

#### What it is
Single Table Inheritance stores all classes in an inheritance hierarchy in one table, using a type discriminator to indicate which subclass each row represents.

#### When to use / when NOT
- **Use:** Few subtype-specific fields; frequent polymorphic loads; simple schema.
- **NOT:** Many subtype-only columns; large hierarchy divergence; strict per-type constraints.

#### Java / Spring example
```java
@Entity
@Inheritance(strategy = InheritanceType.SINGLE_TABLE)
@DiscriminatorColumn(name = "notification_type")
public abstract class Notification { ... }
@Entity @DiscriminatorValue("EMAIL")
public class EmailNotification extends Notification { ... }
```

#### Common mistakes
- Forgetting discriminator in manual SQL inserts—orphan type null.
- Unique constraints on subtype column affecting all rows.
- Assuming `@NotNull` on subclass field enforces for all types.

#### Follow-up (with answer)
**Q:** SINGLE_TABLE vs JOINED vs TABLE_PER_CLASS?
**A:** SINGLE_TABLE: one table, nullable subtype columns, fast polymorphic read, wide sparse table. JOINED: base + subclass tables, normalized, joins on load, good for divergent fields. TABLE_PER_CLASS: each concrete class full table, no discriminator, polymorphic queries UNION expensive. Default lean hierarchy → SINGLE_TABLE; divergent fields → JOINED; rarely TABLE_PER_CLASS.

---

### P161. Table Inheritance

**Category:** Enterprise
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/table-inheritance/)

**Short answer:** Table Inheritance (class table inheritance) maps supertypes and subtypes to related tables joined on primary key—normalized alternative to single table. Subtype tables hold only specific columns. Trade-off: joins on every polymorphic load; ORM configuration complexity.

#### Scenario (interview)
**Situation:** Product catalog has `Product` base with `Book`, `Electronics`, `Subscription` subtypes—radically different attributes (ISBN vs wattage vs billing period). Single-table model exceeded 80 columns; analysts complain about null rates in warehouse extracts.
**What they're testing:** Modeling inheritance in relational schema; JOINED strategy benefits and query plans.
**Model answer:** Table Inheritance via JOINED: `product(id, name, price)`, `book(product_id, isbn, author)`, `electronics(product_id, wattage)`, `subscription(product_id, period_months)`. JPA `@Inheritance(JOINED)` generates LEFT JOIN loads—acceptable with proper FK indexes on `product_id`. Polymorphic query `findAllProducts()` joins all subtype tables—use DTO projections or separate read models for listing pages showing only `name, price, type`. Writes: insert base row then subtype row in one TX. Warehouse ETL: denormalize to flat fact table nightly—OLTP stays normalized. Contrast Single Table: we eliminated sparse columns. Contrast Table Per Class: shared `product` attributes not duplicated. Migration from single table: split columns into subtype tables, populate by discriminator, drop moved columns. N+1 risk on collections—batch fetch or entity graph. When inheritance is wrong altogether, replace with `product` + `product_attributes` JSON or typed extension table keyed by `kind`.

#### What it is
Table Inheritance represents an object hierarchy with a base table for common fields and separate tables for subclass-specific fields, linked by shared primary keys.

#### When to use / when NOT
- **Use:** Subtypes with distinct field sets; normalization matters; constraints per subtype table.
- **NOT:** Deep polymorphic lists without projection strategy; when all subtypes nearly identical—single table simpler.

#### Java / Spring example
```java
@Entity
@Inheritance(strategy = InheritanceType.JOINED)
public abstract class Product { @Id private Long id; }
@Entity
public class Book extends Product { private String isbn; }
```

#### Common mistakes
- Polymorphic listing loading full joins for 1M rows—paginate with type filter.
- Missing index on subtype FK—seq scans on joins.
- Multiple inheritance levels—ORM mapping pain; favor composition.

#### Follow-up (with answer)
**Q:** When is composition better than table inheritance?
**A:** When subtypes share little behavior and fields vary arbitrarily—`product` + `book_details` optional 1:1 avoids ORM inheritance entirely. Composition eases adding new types without altering base mapper. Use table inheritance when true polymorphic domain behavior (`product.ship()`) and shared lifecycle justify joined model.

---

### P162. Table Module

**Category:** Enterprise
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/table-module/)

**Short answer:** Table Module organizes domain logic around one database table—a class encapsulating all access and behavior for that table—common in Table Data Gateway style before rich domain models. Trade-off: procedural table-centric design fights DDD aggregates spanning tables.

#### Scenario (interview)
**Situation:** Reporting team maintains 200-line SQL in five places for `invoice_line` calculations. A `InvoiceLineTableModule` class exists but controllers also query JDBC directly; tax rule change requires hunting all copies.
**What they're testing:** Centralizing table-oriented logic vs anemic scattered SQL.
**Model answer:** I'd strengthen `InvoiceLineTableModule` as single gateway for `invoice_line`—methods `findByInvoice`, `computeTaxedTotal`, `insertBatch`, encapsulating SQL/JdbcTemplate. All modules depend on it, not raw table access. Not quite Repository (aggregate-focused)—Table Module is one table, record-oriented, may return row DTOs not `Invoice` aggregate. Fits legacy schema where table maps cleanly to business artifact. Coexist with domain layer: Table Module in infra; application service composes multiple modules for use cases spanning tables. Refactor duplicated SQL into module private methods; expose intention-revealing names. Testing: in-memory DB against module. Migration path toward Repository: when `Invoice` aggregate solidifies, module becomes private impl detail behind `InvoiceRepository`. Avoid Table Module god for every table in 500-table schema—group by bounded context (`BillingTables` package). Document difference from Active Record pattern—Table Module separates table ops from record object.

#### What it is
Table Module assigns one module class responsibility for all operations on a single table—queries, updates, and table-specific business rules—organizing procedural data access by table.

#### When to use / when NOT
- **Use:** Legacy table-aligned schema; reporting ETL; thin domain with SQL-heavy rules per table.
- **NOT:** Rich DDD aggregates spanning tables—use Repository + domain model; when ORM entity-per-table already duplicates module.

#### Java / Spring example
```java
@Repository
public class InvoiceLineTableModule {
    private final JdbcTemplate jdbc;
    public BigDecimal computeTaxedTotal(long invoiceId) {
        return jdbc.queryForObject("SELECT SUM(...)", BigDecimal.class, invoiceId);
    }
}
```

#### Common mistakes
- Table Module calling another table module in circles—extract use-case service.
- Exposing `ResultSet` to callers—return typed records.
- Business invariants split across modules without orchestration—lost transactions.

#### Follow-up (with answer)
**Q:** Table Module vs DAO?
**A:** DAO is CRUD interface per entity/table—thin persistence. Table Module may include richer table-specific computations and batch operations beyond CRUD—organizational unit for all logic touching that table. Overlap is high; Table Module emphasizes Fowler's record-set gateway grouping behavior with data access for one table.

---

### P163. Template Method

**Category:** Behavioral
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/template-method/)

**Short answer:** Template Method defines algorithm skeleton in a base class with hooks/steps overridden by subclasses—`process()` calls `validate()`, `execute()`, `cleanup()` in fixed order. Spring's `JdbcTemplate`, `RestTemplate` callback hooks echo this. Trade-off: inheritance locks behavior into class hierarchy—composition with strategy often more flexible.

#### Scenario (interview)
**Situation:** Three payment providers share flow: validate request → authorize → capture → emit receipt, but fraud checks and receipt format differ. Team copy-pasted full methods with one line different—bugs fixed in two providers only.
**What they're testing:** Extracting invariant algorithm structure; hooks vs duplication; Spring template classes.
**Model answer:** I'd implement `AbstractPaymentProcessor` with `final processPayment()` calling `validate()`, `authorize()`, `capture()`, `buildReceipt()`—subclasses override hooks, not sequence. Shared TX logging and metrics in base template method. Provider-specific: `StripeProcessor extends AbstractPaymentProcessor` overrides `authorize()`. Alternative without inheritance: compose `PaymentPipeline` with ordered `Step` lambdas—prefer when variations explode. Spring parallel: `JdbcTemplate.query` fixes connection/statement lifecycle; you supply `RowMapper` hook. Testing: test base enforces order—subclass spy verifies `authorize` before `capture`. Beware fragile base class problem—subclasses depend on superclass step timing. Document which methods are `final`. For 2 providers, template method wins; for 20, strategy map may beat hierarchy. Hook methods default no-op in base for optional steps.

#### What it is
Template Method declares the steps of an algorithm in a base class, deferring some steps to subclasses while preventing subclasses from changing overall structure.

#### When to use / when NOT
- **Use:** Stable algorithm sequence with varying steps; framework callbacks; eliminating duplicated control flow.
- **NOT:** Highly variable algorithm order; when composition avoids inheritance rigidity; few lines differ—use strategy.

#### Java / Spring example
```java
public abstract class AbstractPaymentProcessor {
    public final Receipt process(Payment p) {
        validate(p); authorize(p); capture(p); return buildReceipt(p);
    }
    protected abstract void authorize(Payment p);
}
```

#### Common mistakes
- Subclass overriding `process()`—breaks template contract; mark `final`.
- Too many abstract methods—subclass burden; use optional hooks with defaults.
- Template in domain with infra steps—layer violation.

#### Follow-up (with answer)
**Q:** Template Method vs Strategy?
**A:** Template Method uses inheritance—base class owns algorithm structure, subclasses fill steps. Strategy composes interchangeable algorithms via interface injection—runtime swap without subclassing. Template fits fixed sequence; Strategy fits whole-algorithm replacement. Spring `JdbcTemplate` is template; injected `RowMapper` is strategy hook.

---

### P164. Template View

**Category:** UI
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/template-view/)

**Short answer:** Template View renders pages by embedding dynamic data in a fixed markup template—JSP, Thymeleaf, Mustache—separating presentation structure from controller logic. Trade-off: logic sneaking into templates (`<% if %>` spaghetti) erodes maintainability; keep views dumb.

#### Scenario (interview)
**Situation:** Thymeleaf invoices call static utility methods and run pricing logic inline. Designers can't edit layout without breaking totals; unit tests don't cover template math—customer invoices show wrong tax in edge locales.
**What they're testing:** View/controller separation, View Helper pattern synergy, and testability of presentation.
**Model answer:** Template View should only bind precomputed model attributes—`InvoiceViewModel` with `total`, `taxLines`, `formattedDate` built in controller or View Helper service. Template: `<span th:text="${invoice.total}">`—no `th:with` doing arithmetic. Pricing logic moves to `InvoicePresentationService` covered by JUnit. Designers edit HTML structure; Java owns numbers. For i18n, message keys in template, formatting via `#numbers.formatDecimal` on already-rounded values. Reusable layout: Thymeleaf fragments for header/footer (template composition). Contrast Template Method in domain—different pattern. Security: never trust template to escape—use contextual escaping, CSP. Testing: render template with mock model in slice test or snapshot HTML. SPA migration: Template View becomes API + client template—same separation principle. Anti-pattern: JSP scriptlets—legacy teams still maintain; strangle to Thymeleaf/React gradually.

#### What it is
Template View generates HTML or UI by substituting data into a predefined template file, keeping page structure static and logic minimal in the view layer.

#### When to use / when NOT
- **Use:** Server-rendered UIs; email HTML generation; predictable page layouts.
- **NOT:** Highly interactive apps needing rich client state—SPA component model; when templates become second programming language.

#### Java / Spring example
```html
<!-- invoice.html -->
<tr th:each="line : ${invoice.lines}">
  <td th:text="${line.description}"/>
  <td th:text="${line.amount}"/>
</tr>
```

#### Common mistakes
- Business rules in template language—untested.
- Giant monolithic template—extract fragments/partials.
- Passing JPA entities with lazy fields into view—LazyInitializationException.

#### Follow-up (with answer)
**Q:** Template View vs View Helper?
**A:** Template View is the markup file with placeholders. View Helper is Java object/formatting adapter preparing display logic (`formatCurrency`, breadcrumb builder) so templates stay thin. Use View Helper when same formatting used across multiple templates; keep helpers presentation-specific, not domain rules.

---

### P165. Thread-Pool Executor

**Category:** Concurrency
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/thread-pool-executor/)

**Short answer:** Thread-Pool Executor maintains a pool of reusable worker threads processing tasks from a queue—amortizing thread creation cost and bounding concurrency. `ExecutorService`, ForkJoinPool, and `@Async` pools embody this. Trade-off: misconfigured pool size and unbounded queues cause latency spikes or `OutOfMemoryError`.

#### Scenario (interview)
**Situation:** `@Async` defaults process export jobs; Black Friday triggers 50k exports; heap OOM from queued `Runnable` objects holding full result sets; GC pause kills API latency.
**What they're testing:** Pool sizing, queue bounds, rejection policies, and separating async workloads.
**Model answer:** Thread-Pool Executor needs explicit bounds: dedicated `exportExecutor` with `corePoolSize=8`, `maxPoolSize=16`, `queueCapacity=200`, `RejectedExecutionHandler` returning 503 or persisting job to DB queue instead of unbounded `LinkedBlockingQueue`. Never `Executors.newCachedThreadPool()` for bursty workloads—unbounded threads. Never share export pool with `@Async` email sends—isolation prevents starvation. Task design: runnable holds job ID, loads data inside worker—don't capture huge lists in closure. Monitor: pool active count, queue size, task duration—Micrometer `executor.*`. Graceful shutdown: `awaitTermination` on deploy. For CPU-bound work, pool size ≈ cores; I/O-bound higher with profiling. Spring: `@EnableAsync` + named `ThreadPoolTaskExecutor` bean injected by qualifier. Overflow path: write to SQS when pool saturated—Queue-Based Load Leveling combo. Load test before peak. Document `@Async` self-invocation doesn't async unless proxied.

#### What it is
Thread-Pool Executor manages a fixed or elastic set of threads that execute submitted tasks from a work queue, recycling threads to avoid per-task creation overhead.

#### When to use / when NOT
- **Use:** Many short-lived async tasks; bounding parallel work; server-side background processing.
- **NOT:** Long blocking tasks without queue limit; CPU work sized wrong—blocks all pool threads; one-shot `new Thread()` per task at scale.

#### Java / Spring example
```java
@Bean("exportExecutor")
public Executor exportExecutor() {
    var t = new ThreadPoolTaskExecutor();
    t.setCorePoolSize(8); t.setMaxPoolSize(16); t.setQueueCapacity(200);
    t.setRejectedExecutionHandler(new ThreadPoolExecutor.CallerRunsPolicy());
    t.initialize(); return t;
}
```

#### Common mistakes
- Default unbounded queue + fixed threads—memory exhaustion.
- Same pool for CPU and blocking I/O—wrong sizing for both.
- No MDC/correlation propagation to worker threads—broken traces.

#### Follow-up (with answer)
**Q:** `CallerRunsPolicy` vs `AbortPolicy`?
**A:** CallerRuns runs rejected task on submitting thread—back-pressure but slows caller (often HTTP thread). Abort throws `RejectedExecutionException`—fail fast, caller must handle (queue to DB, 503). Use CallerRuns sparingly; prefer bounded queue + explicit overflow to durable queue. Abort clearer for APIs returning errors to clients.

---

### P166. Thread-Specific Storage

**Category:** Concurrency
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/thread-specific-storage/)

**Short answer:** Thread-Specific Storage gives each thread its own copy of a variable—`ThreadLocal` in Java—avoiding synchronization for per-request context like user ID, locale, or DB connection in legacy code. Trade-off: memory leaks in thread pools if not `remove()`d; async handoff loses ThreadLocal unless explicitly propagated.

#### Scenario (interview)
**Situation:** Custom `ThreadLocal<SecurityContext>` holds tenant ID for multi-tenant routing. After adopting `@Async` and WebFlux, some requests write to wrong tenant schema; thread pool reuse leaks admin context into customer requests.
**What they're testing:** ThreadLocal lifecycle, pool thread reuse hazards, and MDC propagation in async.
**Model answer:** Thread-Specific Storage via `ThreadLocal` works only when same thread handles entire request—classic servlet model. Pool threads retain last value unless `finally { TENANT.remove(); }` after each request—filter must clear on exit. `@Async` child thread doesn't inherit parent ThreadLocal—use `TaskDecorator` copying context to worker or pass `TenantId` explicitly as method arg (preferred). WebFlux: ThreadLocal is anti-pattern—use `Reactor Context`. Security: never trust ThreadLocal set early without re-validating on each DB call. Prefer explicit `TenantContext` parameter over hidden global state in new code. MDC logging: `MDC.put` + clear in filter; Spring Security `SecurityContextHolder` uses ThreadLocal—`MODE_INHERITABLETHREADLOCAL` only for child threads, not pool. Memory leak: thread pool + ThreadLocal without remove holds references to large objects until thread dies. Migration: replace ThreadLocal with request-scoped bean or `ScopedValue` (Java 21+) where appropriate. Audit all async entry points for context propagation.

#### What it is
Thread-Specific Storage associates data with the executing thread so each thread sees its own instance without locks—typically implemented via `ThreadLocal` in Java.

#### When to use / when NOT
- **Use:** Per-thread non-shared context in thread-per-request models; avoiding lock contention on read-mostly context.
- **NOT:** Cross-thread async without propagation; shared mutable state; long-lived thread pools without cleanup.

#### Java / Spring example
```java
public final class TenantContext {
    private static final ThreadLocal<String> CURRENT = new ThreadLocal<>();
    public static void set(String tenant) { CURRENT.set(tenant); }
    public static void clear() { CURRENT.remove(); }
}
// Filter: try { set... } finally { clear(); }
```

#### Common mistakes
- No `remove()` in finally—tenant bleed across requests.
- Assuming `@Async` inherits ThreadLocal—silent wrong-tenant writes.
- Storing heavy objects in ThreadLocal on pooled threads—memory leak.

#### Follow-up (with answer)
**Q:** ThreadLocal vs `ScopedValue` (Java 21)?
**A:** ThreadLocal persists until removed—error-prone with virtual threads and pools. ScopedValue binds immutable context for lexical scope with structured propagation to child tasks—safer for new concurrent code. Prefer ScopedValue or explicit parameters as Java evolves; ThreadLocal remains ubiquitous in Spring Security/MDC legacy paths—always clear in filters.

---

### P167. Throttling

**Category:** Performance
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/throttling/)

**Short answer:** Throttling slows down request processing when load exceeds threshold—delaying or shedding work gradually—rather than hard rejecting like rate limiting. Protects downstream while allowing some throughput. Trade-off: increased latency under load; clients need timeout/retry discipline.

#### Scenario (interview)
**Situation:** Internal pricing engine must serve all callers but degrades gracefully when CPU > 80%. Hard 429 rate limits break SLA with treasury batch jobs that must complete overnight. Product wants "slow down, don't fail" behavior.
**What they're testing:** Throttling vs rate limiting; adaptive concurrency; graceful degradation.
**Model answer:** I'd implement Throttling at service ingress: adaptive semaphore limiting concurrent in-flight pricing requests—when CPU high, reduce permits from 100 to 30; excess requests wait in fair queue with max wait 2s then 503. Contrast Rate Limiting: rejects at 100 RPS regardless of processing time. Throttling matches resource consumption—long-running requests count against concurrency budget. Resilience4j `Bulkhead` limits parallel calls; combine with `TimeLimiter`. Client-side: exponential backoff on slow responses. Batch jobs get dedicated low-priority queue throttled separately from interactive tier—weighted fair queuing. Metrics: wait time in throttle queue, dropped after timeout. Not the same as caching—throttle still computes, just fewer parallel. API gateway may do connection throttling (slow read). Document UX impact—p99 latency rises before errors. Load test throttle thresholds. Avoid unbounded wait queues—bounded delay then reject.

#### What it is
Throttling controls execution rate by delaying or limiting concurrent operations when system load approaches capacity, smoothing demand instead of immediate hard failure.

#### When to use / when NOT
- **Use:** Protect CPU/memory-bound internals; must serve all clients eventually; gradual degradation acceptable.
- **NOT:** When fast-fail and client retry is cheaper; strict contractual RPS caps—rate limiting clearer.

#### Java / Spring example
```java
Semaphore inflight = new Semaphore(50);
public Quote price(Request r) throws InterruptedException {
    if (!inflight.tryAcquire(2, TimeUnit.SECONDS)) throw new OverloadedException();
    try { return engine.compute(r); } finally { inflight.release(); }
}
```

#### Common mistakes
- Unbounded wait queue—latency explosion, memory growth.
- Throttling without informing clients—hidden timeouts.
- Same throttle for batch and interactive—SLA conflict.

#### Follow-up (with answer)
**Q:** Throttling vs Backpressure?
**A:** Throttling proactively limits admission based on local metrics (CPU, queue depth, semaphores). Backpressure is reactive flow control in streaming pipelines—downstream signals upstream to slow emission (Reactor `request(n)`). Throttling often at service boundary; backpressure within reactive chain. Both reduce overload; different mechanisms and stacks.

---

### P168. Tolerant Reader

**Category:** Microservices
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/tolerant-reader/)

**Short answer:** Tolerant Reader consumes another service's API defensively—ignoring unknown fields, defaulting missing optional data, not failing on schema extensions—enabling independent service evolution. Trade-off: silent ignorance of important new fields if not monitored; requires discipline on required vs optional semantics.

#### Scenario (interview)
**Situation:** Billing service deserializes Order events with strict Jackson `FAIL_ON_UNKNOWN_PROPERTIES`. Orders team adds `carbonOffsetFee` field; billing deploys fine but old billing pods crash-loop on replay until all upgraded simultaneously.
**What they're testing:** Consumer-side schema evolution, Postel's law, and compatibility modes.
**Model answer:** Billing should be Tolerant Reader: `objectMapper.disable(FAIL_ON_UNKNOWN_PROPERTIES)` for integration DTOs; ignore unknown JSON fields; treat new optional fields with defaults (`carbonOffsetFee` defaults 0 until billing supports invoicing it). Never bind foreign API DTOs to internal domain directly—anti-corruption layer maps subset needed. Version events: `schemaVersion` field; consumer handles N and N-1. Logging: metric `unknown_fields_seen` at debug, not error. Strict validation only on fields billing requires for correctness. Provider publishes additive changes; breaking changes need new topic/version contract. Pact consumer tests verify required fields present, not full equality. Replay Kafka from offset with old messages—tolerant reader survives. Document fields billing intentionally ignores vs depends on. Contrast with sharing JAR of event classes—couples deploy cadence. Feature flag new fee handling when ready to read `carbonOffsetFee`.

#### What it is
Tolerant Reader parses external messages leniently—accepting superset schemas—so producers can evolve without synchronized consumer deployments.

#### When to use / when NOT
- **Use:** Cross-team microservice integration; event consumption; public API clients.
- **NOT:** Security-critical fields where unknown data must reject; internal monolith modules sharing strict types.

#### Java / Spring example
```java
@JsonIgnoreProperties(ignoreUnknown = true)
public record OrderEventV1(String orderId, BigDecimal amount) {}
// mapper ignores carbonOffsetFee until V2 handler added
```

#### Common mistakes
- Shared tight DTO jar coupling all services—brittle deploys.
- Silently ignoring fields that should trigger new behavior—monitor schema registry.
- Deserializing into `Map` everywhere—loses type safety without care.

#### Follow-up (with answer)
**Q:** Tolerant Reader vs Anti-Corruption Layer?
**A:** Tolerant Reader is deserialization policy—ignore unknown, default missing. Anti-Corruption Layer is broader translation boundary translating foreign model to your domain language. ACL often includes tolerant reader plus explicit mapping and semantic reinterpretation. Use both at integration edges.

---

### P169. Trampoline

**Category:** Performance
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/trampoline/)

**Short answer:** Trampoline converts recursive calls into iterative loops using continuations—avoiding stack overflow on deep recursion in functional style. In Java, manual trampoline or libraries simulate tail-call optimization absent from JVM. Trade-off: readability cost vs stack safety for deeply nested structures.

#### Scenario (interview)
**Situation:** XML depth validator recursively walks 50k nested elements; `StackOverflowError` in production on adversarial partner payloads. Team considers increasing `-Xss` thread stack size.
**What they're testing:** Recursion limits, trampoline/iterative refactor, and security against deeply nested input.
**Model answer:** Increasing stack is band-aid—Trampoline refactor: recursive `validate(Node n)` returns `Trampoline<ValidationResult>` where tail calls return `Trampoline.suspend(() -> validate(child))` and driver loop `while (t != done) t = t.jump()`. Or pragmatic: iterative explicit stack `Deque<Node>` simulating recursion—often clearer in Java than pure trampoline. Limit max depth 1000—reject early with 400. Partner SLA caps payload size and nesting. For functional pipelines, Vavr `Trampoline` utility. Contrast: tail-recursive languages compile to loop; Java needs manual pattern. Also fix parser—SAX streaming vs DOM building full tree. Security: billion laughs attack—entity expansion limits. Tests: generate 10k depth fixture. Performance: iterative usually faster than deep recursion even before overflow. Document max depth in API contract.

#### What it is
Trampoline pattern executes recursive logic without growing the call stack by bouncing through a trampoline function that iteratively invokes continuations until completion.

#### When to use / when NOT
- **Use:** Deep recursive traversals; functional-style tail calls in Java; avoiding stack overflow.
- **NOT:** Shallow recursion; when simple loop with explicit stack is more readable; performance-critical paths where loop wins clearly.

#### Java / Spring example
```java
// iterative equivalent — preferred in Java
Deque<Node> stack = new ArrayDeque<>();
stack.push(root);
while (!stack.isEmpty()) { var n = stack.pop(); ... }
```

#### Common mistakes
- Raising `-Xss` globally—memory × thread count explosion.
- DOM parser loading untrusted huge XML—use streaming.
- Trampoline obfuscation when `while` loop suffices.

#### Follow-up (with answer)
**Q:** Why doesn't JVM optimize tail recursion?
**A:** JVM bytecode lacks tail-call optimization guarantee—recursive call still consumes stack frame. Project Loom virtual threads help concurrency not tail calls. Java idioms: iterative loops, explicit stacks, or trampoline libraries for deep recursion. JEP discussions continue; don't rely on TCO in production Java today.

---

### P170. Transactional Outbox

**Category:** Microservices
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/transactional-outbox/)

**Short answer:** Transactional Outbox writes business data and outbound event rows in the same local DB transaction; a separate publisher relays outbox rows to the message broker—eliminating dual-write inconsistency. Trade-off: eventual publish latency; consumers need idempotency; outbox table requires retention/cleanup.

#### Scenario (interview)
**Situation:** Order service saves order then publishes `OrderCreated` to Kafka. Broker blip causes lost events—warehouse never ships. Retry on publish after DB commit creates orphan orders without events, or duplicate events on partial failures.
**What they're testing:** Reliable event publishing without XA; at-least-once semantics; Debezium vs polling publisher.
**Model answer:** Transactional Outbox: in same `@Transactional` as `orderRepository.save`, insert `outbox_events(eventType, payload, status=PENDING)`. Commit atomically—never call Kafka inside TX. `OutboxPublisher` polls `PENDING` rows (or Debezium CDC on outbox table) and publishes to Kafka, marks `PROCESSED`. Duplicate publish possible—consumers idempotent on `eventId`. Ordering: partition by `orderId`. Cleanup job archives processed rows > 7 days. Latency: poll interval 1s acceptable for fulfillment. Compare naive dual-write: commit then publish—crash between loses event. XA Kafka transaction: operational pain. Idempotency key in outbox prevents duplicate insert on request retry. Observability: lag metric `now() - created_at` for oldest pending. Schema: payload JSON with version. Testing: kill broker mid-publish, assert event eventually delivered after recovery.

#### What it is
Transactional Outbox atomically persists domain changes and event records together, then asynchronously dispatches events to external brokers from the outbox table.

#### When to use / when NOT
- **Use:** Microservices emitting integration events; need DB-broker consistency; avoiding 2PC.
- **NOT:** In-process Spring events only; fire-and-forget analytics with loss acceptable.

#### Java / Spring example
```java
@Transactional
public Order createOrder(CreateOrder cmd) {
    var order = orders.save(Order.from(cmd));
    outbox.save(OutboxEvent.pending("OrderCreated", order.id(), payload(order)));
    return order;
}
```

#### Common mistakes
- Publishing Kafka inside `@Transactional` before commit—consumers see uncommitted data.
- No idempotent consumer—duplicate shipments.
- Unbounded outbox table—no archival.

#### Follow-up (with answer)
**Q:** Polling publisher vs Debezium CDC outbox?
**A:** Polling: simple scheduled query, slight latency, app owns publish logic. Debezium reads DB WAL—lower latency, infra complexity, broker coupling to DB replication. Polling fine for many teams; CDC at scale or strict latency. Both require idempotent consumers.

---

### P171. Transaction Script

**Category:** Enterprise
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/transaction-script/)

**Short answer:** Transaction Script organizes business logic as procedural scripts—one method per use case manipulating records/DAOs directly—without rich domain objects. Fast for simple CRUD apps. Trade-off: logic duplication and conditionals sprawl as rules complexify—migrate to Domain Model when pain appears.

#### Scenario (interview)
**Situation:** Internal admin tool has 15 tables, 40 screens, simple validations. Junior team built rich `OrderAggregate` with events; 6 months later, 80% methods are getters/setters and bugs come from forgotten invariant checks scattered in services.
**What they're testing:** Right pattern for complexity level; when DDD overkill hurts velocity.
**Model answer:** For this admin CRUD with shallow rules, Transaction Script is appropriate: `OrderService.cancelOrder(id)` runs procedural steps—load row, check status enum, update status, insert audit log—no `OrderAggregate`. One class per area with `@Transactional` methods mirroring use cases. DAOs/ Spring Data repos return entities or records; business rules as `if` in script until complexity threshold. Smell to migrate: same rule in 3 scripts, cyclomatic complexity >15, non-trivial invariants. Then extract domain methods incrementally—not big-bang DDD. Transaction Script + Service Layer is Fowler's simple path. Testing: script integration tests against DB. Contrast Domain Model: behavior on objects. Reporting ETL often transaction script forever. Don't force Event Sourcing here. Document team guideline: start script, refactor to domain when third duplication of rule.

#### What it is
Transaction Script implements each business transaction as a single procedural procedure operating on passive data structures, typically one method per application use case.

#### When to use / when NOT
- **Use:** Simple applications; admin tools; MVPs; read-heavy CRUD with few invariants.
- **NOT:** Complex domain with many interacting rules—Domain Model + Service Layer wins.

#### Java / Spring example
```java
@Service @Transactional
public class CancelOrderScript {
    public void cancel(long orderId) {
        var o = orders.findById(orderId).orElseThrow();
        if (o.getStatus() != OPEN) throw new IllegalStateException();
        o.setStatus(CANCELLED); audit.log("cancel", orderId);
    }
}
```

#### Common mistakes
- DDD ceremony on trivial apps—velocity loss.
- Copy-paste scripts—extract shared procedures.
- Missing `@Transactional` on multi-step script—partial updates.

#### Follow-up (with answer)
**Q:** When to graduate from Transaction Script to Domain Model?
**A:** When invariants involve multiple fields/objects consistently, rules duplicate across scripts, or testing requires elaborate setup because state is only validatable through DB. Rule of three: third copy of same condition triggers domain extraction. Not headcount or buzzword—measurable complexity and defect rate.

---

### P172. Twin

**Category:** Structural
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/twin/)

**Short answer:** Twin pattern simulates multiple inheritance by splitting a class into two sibling classes implementing the same interface—each twin holds half the behavior—coordinated to present one logical object. Rare in Java (no MI). Trade-off: complex coordination; modern Java favors composition, interfaces with default methods, or delegation.

#### Scenario (interview)
**Situation:** Legacy integration requires class to be both `Serializable` Java bean and extend third-party `VendorWidget` (final). Subclassing impossible; copying vendor code violates license. Team proposes duplicate wrapper classes diverging over time.
**What they're testing:** Creative structural workarounds; composition vs inheritance limits in Java.
**Model answer:** Twin pattern: define `WidgetFacade` interface combining both APIs. `VendorTwin` extends/wraps `VendorWidget` delegating vendor methods; `SerializableTwin` holds serializable state; both implement `WidgetFacade` and reference each other for coordinated updates—mutations on one sync to other. Client sees single facade composing twins. Rare—usually simpler: composition with adapter wrapping vendor, separate DTO for serialization—not twin. Modern alt: record for state + delegation to vendor instance; Jackson mixin for serialization.customize. Twin justified when two inheritance hierarchies must merge without MI—simulation research, GUI frameworks. Document sync protocol—risk of inconsistent twins. Testing: mutation on A visible on B. Maintenance cost high—prefer anti-corruption adapter isolating vendor. Interview answer: know pattern exists, recommend composition first; twin last resort.

#### What it is
Twin provides two coordinated objects that together implement a combined interface that would otherwise require multiple inheritance, keeping sibling twins in sync.

#### When to use / when NOT
- **Use:** Rare MI simulation; legacy interop constraints; framework mandates parallel hierarchies.
- **NOT:** Normal Java design—composition, delegation, adapters solve most cases.

#### Java / Spring example
```java
public class WidgetTwin implements WidgetFacade {
    private final VendorTwin vendorPart;
    private final StateTwin statePart;
    // coordinate mutations across both
}
```

#### Common mistakes
- Twins drifting out of sync—subtle bugs.
- Choosing twin when adapter suffices—over-engineering.
- Complex bidirectional references—memory leaks.

#### Follow-up (with answer)
**Q:** Twin vs Mixin (default interface methods)?
**A:** Java 8+ default methods allow mixin-like behavior on interfaces—partial code sharing without twin coordination. Twin splits two class hierarchies into synchronized siblings; mixins compose interface behavior into implementors. Prefer mixins and delegation in modern Java; twin is historical workaround for MI absence.

---

### P173. Type Object

**Category:** Creational
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/type-object/)

**Short answer:** Type Object separates an object's type data from instances—`MonsterType` defines base stats; each `Monster` references its type object, enabling runtime-defined types without subclass explosion. Game configs and product catalogs use this heavily. Trade-off: behavior in type vs instance confusion; may need strategy per type for complex actions.

#### Scenario (interview)
**Situation:** Insurance product engine adds new product variants weekly—team creates `TravelPolicy`, `PetPolicy` subclasses; deploy required for each new deductible table row marketing invents in CMS.
**What they're testing:** Data-driven types vs class hierarchy; runtime configuration from DB/CMS.
**Model answer:** Type Object pattern: `ProductType` entity loaded from DB—`code`, `basePremiumFormula`, `coverageLimits`, `ridersAllowed`. `Policy` instance holds `ProductType type` reference + instance-specific overrides (insured age, dates). New product = CMS row + rule config, no Java subclass. Behavior: `type.calculatePremium(facts)` or rule engine keyed by `type.code`. Validation schema per type in JSON. Cache `ProductType` read-only snapshots; version on policy bind references `productTypeVersion`. Contrast class hierarchy—subclass per product doesn't scale for SaaS insurance. Contrast Role Object—type object is static catalog metadata; roles attach dynamic capabilities. Migration: extract shared fields to `ProductType`, deprecate subclasses. Testing: fixture types in JSON. Watch: don't put instance state on type object—shared mutable type corrupts all instances.

#### What it is
Type Object moves type-specific data and behavior definitions into separate type objects that instances reference, enabling new types at runtime without new classes.

#### When to use / when NOT
- **Use:** Many variants defined by data; CMS-driven catalogs; games/simulations with archetypes.
- **NOT:** Few stable types with distinct code behavior—subclasses clearer; when type and instance boundaries blur.

#### Java / Spring example
```java
public class Policy {
    private final ProductType productType;
    public Money premium(Facts f) { return productType.rate(f, endorsements); }
}
```

#### Common mistakes
- Mutable shared `ProductType` singleton—race and corruption.
- All behavior in strings/scripts without tests—governance gap.
- Confusing Type Object with Entity subtype inheritance mapping.

#### Follow-up (with answer)
**Q:** Type Object vs Strategy?
**A:** Type Object bundles data + metadata defining a category instances reference—many instances share one type object. Strategy injects interchangeable algorithm for one behavior point. Combine: `ProductType` holds reference to `PremiumStrategy` for that product line. Type Object answers "what kind"; Strategy answers "which algorithm now."

---

### P174. Unit of Work

**Category:** Enterprise
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/unit-of-work/)

**Short answer:** Unit of Work tracks new, dirty, and deleted objects during a business transaction and commits all changes atomically in one flush—coordinating with Identity Map to avoid duplicate loads. JPA `EntityManager` and Hibernate session implement UoW implicitly. Trade-off: long-lived UoW causes stale state and memory growth; scope must match transaction.

#### Scenario (interview)
**Situation:** Developers call `repository.save()` after every field change in a loop updating 500 `OrderLine` rows—500 INSERT/UPDATE round-trips, transaction timeout. Another team holds `EntityManager` open across remote HTTP calls—LazyInitializationException and connection pool exhaustion.
**What they're testing:** UoW flush timing, transaction boundary, dirty checking, batch commits.
**Model answer:** Unit of Work: load and mutate 500 lines in one `@Transactional` method without intermediate `save()`—JPA dirty checking flushes once at commit (enable `jdbc.batch_size`). UoW tracks identity—same `orderId` load twice returns same instance in persistence context. Don't span UoW across HTTP—request-scoped TX. Explicit pattern: Fowler's `UnitOfWork.registerNew/Dirty/Deleted` + `commit()`—ORM does this internally. For non-ORM: implement `ChangeSet` collector committing in single JDBC batch. Anti-pattern: `saveAll` per item in loop without batching. Read-only TX for queries—no UoW write tracking. Testing: `@Transactional` rollback in tests keeps UoW isolated. Compare Identity Map—UoW includes commit orchestration. Open Session In View anti-pattern extends UoW to view layer—masks lazy issues, holds connections. Document one TX per application service method.

#### What it is
Unit of Work maintains a list of objects affected by a business transaction and coordinates writing out changes and resolving concurrency problems in a single commit operation.

#### When to use / when NOT
- **Use:** ORM-based apps (implicit); manual when batching multiple DAO changes atomically; aggregate persistence.
- **NOT:** Autocommit per statement workflows; long-running processes without clear commit boundary.

#### Java / Spring example
```java
@Transactional
public void bulkAdjust(List<LineId> ids, Money delta) {
    ids.forEach(id -> lines.findById(id).adjust(delta)); // single flush at end
}
```

#### Common mistakes
- `save()` in loop—defeats batching and UoW.
- Extended persistence context across requests—OSIV abuse.
- Multiple UoW/EntityManager instances—duplicate identity.

#### Follow-up (with answer)
**Q:** Unit of Work vs Repository?
**A:** Repository abstracts collection-like persistence for aggregates. Unit of Work tracks transactional changes across repositories/entities and commits once. In JPA, EntityManager is UoW; repositories are facades over it. Application service defines UoW boundary via `@Transactional`; repositories participate inside.

---

### P175. Update Method

**Category:** Enterprise
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/update-method/)

**Short answer:** Update Method (game loop pattern) processes entities each tick by calling `update()` on all objects in a collection—simulations, schedulers, polling aggregates. Separates per-frame/per-cycle behavior from initialization. Trade-off: O(n) every tick; hard to optimize inactive entities without spatial partitioning or dirty flags.

#### Scenario (interview)
**Situation:** Fleet tracking simulates 100k vehicle positions every 5 seconds calling `vehicle.update()` regardless of movement. CPU pegs; 90% vehicles parked overnight still processed.
**What they're testing:** Game-loop/update batching; active vs idle entity optimization; scheduling patterns.
**Model answer:** Update Method runs `for (entity : world) entity.update(dt)` each simulation tick. Optimize: only `ActiveVehicle` subset in update list—parked vehicles removed until `ignitionOn` event re-registers. Spatial index for collision checks subset, not full scan. Batch DB writes: accumulate position deltas, flush every N ticks. Parallelize partitionable updates on ForkJoin where no shared state. Contrast Event-Driven: position updates on GPS message only—better for real world IoT at rest. Update Method fits continuous simulation (games, physics). Spring `@Scheduled` polling health checks is update method—don't poll healthy services every second; exponential backoff. Dirty Flag pattern skips update if state unchanged. Metrics: tick duration, entities processed. Cap max entities per tick with fairness queue. Document dt handling—fixed timestep vs variable. For 100k idle, event-driven wins; for game loop, active set optimization essential.

#### What it is
Update Method invokes a periodic update operation on all participating objects in a system, advancing simulation or polling state on a fixed tick.

#### When to use / when NOT
- **Use:** Simulations; game loops; periodic batch reconciliation; animation frames.
- **NOT:** Event-driven domains where work happens on change only; massive idle populations without filtering.

#### Java / Spring example
```java
@Scheduled(fixedRate = 5000)
public void tick() {
    activeVehicles.forEach(v -> v.update(elapsed));
}
```

#### Common mistakes
- Updating entire collection including idle entities—CPU waste.
- Unbounded work per tick—misses real-time deadline.
- Shared mutable state across parallel updates—race conditions.

#### Follow-up (with answer)
**Q:** Update Method vs Event-Driven Architecture?
**A:** Update Method pulls all entities forward on clock tick—simple, predictable, can waste work. Event-driven pushes changes when signals arrive—efficient for sparse activity, complex ordering. Hybrid: event updates position, periodic update reconciles drift. Choose based on activity density and latency requirements.

---

### P176. Value Object

**Category:** Enterprise
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/value-object/)

**Short answer:** Value Object models immutable concepts defined by attributes, not identity—`Money`, `Email`, `DateRange`—equality by value, no lifecycle. Java records excel here. Trade-off: conflating value objects with entities causes identity bugs (updating "the same email" on two people).

#### Scenario (interview)
**Situation:** `String email` on `Customer` allows `"user@domain.com"` and `"USER@domain.com"` as different; refund logic compares `double amount` with `==`; address changes mutate shared reference used as map key—HashMap corruption.
**What they're testing:** DDD value types, immutability, equality, and using records/value types at boundaries.
**Model answer:** Introduce Value Objects: `Email` record normalizes lowercase in constructor, rejects invalid; `Money` of minor units `long` with `add` returning new instance; `Address` immutable record. Entities (`Customer`) identified by `CustomerId` UUID; replace email by creating new `Email` value, not mutating string in place. Map keys: never mutable VO; if must key by address, immutable record OK. JPA: `@Embeddable` for `Money`, `Address`—stored inline. Compare amounts with `equals`, never `==` on doubles—`Money` prevents. Collections: `Set<Email>` works with value equality. Migration: wrap primitives incrementally at API boundary. Lombok `@Value` or Java 16+ records. Testing: equality symmetry, validation on construct. Anti-pattern: entity with only value fields no identity—maybe should be value. Value objects side-effect free—domain events come from entities.

#### What it is
Value Object is an immutable object without conceptual identity whose equality depends solely on its attribute values, representing descriptive aspects of the domain.

#### When to use / when NOT
- **Use:** Money, quantities, dates, addresses, codes; validation at construction; composite values in entities.
- **NOT:** Objects requiring tracking over time with same ID—entities; mutable cached aggregates.

#### Java / Spring example
```java
public record Money(long minorUnits, Currency currency) {
    public Money add(Money other) {
        if (!currency.equals(other.currency)) throw new IllegalArgumentException();
        return new Money(minorUnits + other.minorUnits, currency);
    }
}
```

#### Common mistakes
- Mutable value types—breaks equality and collections.
- Using primitive `double` for money—rounding bugs.
- Value object with database-generated ID—it's an entity.

#### Follow-up (with answer)
**Q:** Value Object vs Entity?
**A:** Entity has identity persisting through attribute changes (`Customer` same ID after address change). Value Object replaces entirely when attributes change—new `Address` instance. Entities have lifecycle; values are swapped. ORM: entity has own table/ID; embeddable value columns inline.

---

### P177. Version Number

**Category:** Enterprise
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/version-number/)

**Short answer:** Version Number (optimistic locking) detects concurrent updates by incrementing a version column on each successful write—`UPDATE ... WHERE id=? AND version=?`; zero rows updated means conflict. JPA `@Version` automates this. Trade-off: clients must handle `OptimisticLockException` with retry or merge UX.

#### Scenario (interview)
**Situation:** Two support agents edit same ticket; last save wins silently—first agent's notes vanish. Product demands conflict notification, not silent overwrite. DB has no locking column.
**What they're testing:** Optimistic vs pessimistic locking; lost update problem; UX on conflict.
**Model answer:** Add `@Version Long version` on `Ticket` entity—JPA increments on update, throws `OptimisticLockException` if stale. Client sends `version` from load; server rejects mismatch with `409 Conflict` and diff payload. Agent B refreshes and merges. Alternative: pessimistic `SELECT FOR UPDATE` for high-contention financial rows—blocks rather than fails. Version Number cheaper for read-heavy tickets. Retry: only idempotent updates with user prompt, not blind auto-retry. API: ETag header mirroring version for REST. Bulk update: watch partial batch failures. Testing: two threads update same row—one wins, one excepts. Don't use `updated_at` alone without compare-and-set—clock skew issues; version integer deterministic. Hibernate also supports timestamp `@Version` but integer clearer. Document merge strategy for text fields—append notes don't lose. Event sourcing uses stream version similarly.

#### What it is
Version Number optimistic concurrency control attaches a monotonically increasing version to each record, rejecting updates when the version doesn't match the value read.

#### When to use / when NOT
- **Use:** Concurrent edits on same aggregate; read-mostly with occasional writes; avoiding long DB locks.
- **NOT:** High-conflict write hotspots needing pessimistic lock; when last-write-wins acceptable.

#### Java / Spring example
```java
@Entity
public class Ticket {
    @Version private Long version;
}
// OptimisticLockException → @ControllerAdvice → 409
```

#### Common mistakes
- Catching exception and retrying without user merge—data loss still possible.
- No version in API—clients can't send expected version.
- Using wall-clock `updatedAt` as sole guard without atomic compare.

#### Follow-up (with answer)
**Q:** Optimistic vs pessimistic locking?
**A:** Optimistic (version number) assumes conflict rare—commit fails if another writer won. Pessimistic locks row on read until TX end—prevents conflict, reduces throughput, deadlock risk. Use optimistic for collaborative editing with retry UX; pessimistic for inventory deduction or seat booking with high contention.

---

### P178. View Helper

**Category:** UI
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/view-helper/)

**Short answer:** View Helper encapsulates presentation logic—formatting dates, building menus, composing view models—keeping templates dumb. In Spring MVC, dedicated presenter/assembler classes or Thymeleaf `@bean` utilities. Trade-off: scattering helpers without clear naming becomes junk drawer package.

#### Scenario (interview)
**Situation:** JSP pages duplicate 30 lines formatting currency per locale and building breadcrumb trails; changing corporate date format requires editing 40 templates.
**What they're testing:** Separation of presentation logic from template and domain; testability of formatting.
**Model answer:** Extract `InvoiceViewHelper` (or `InvoiceViewAssembler`) with `formatMoney(Money, Locale)`, `breadcrumbs(Invoice)`, `statusBadge(OrderStatus)` returning display DTOs. Controller: `model.addAttribute("view", helper.build(invoice))`. Templates bind `view.totalDisplay` only. Unit test helper without rendering HTML. Spring: `@Component` helper injected in controller—not static util soup. i18n: helper uses `MessageSource`. Contrast domain service—View Helper knows UI concerns (badge colors, sort order for nav), not business rules. Multiple templates share helper—DRY. Don't put SQL in view helper—belongs in query service. For REST JSON APIs, same assembler produces response DTO—View Helper generalizes to Presentation Model. Legacy JSP: `<%@ taglib %>` custom tags wrapping helper. Document package `...web.view` vs `...application`.

#### What it is
View Helper centralizes display-oriented logic and adapter code used by views, preventing duplication and logic in template markup.

#### When to use / when NOT
- **Use:** Formatting, navigation chrome, composite read models for screens; shared across templates.
- **NOT:** Business invariants or transactional logic—belongs in domain/application layer.

#### Java / Spring example
```java
@Component
public class InvoiceViewHelper {
    public InvoiceViewModel build(Invoice inv, Locale locale) {
        return new InvoiceViewModel(formatter.format(inv.total(), locale), ...);
    }
}
```

#### Common mistakes
- Helper calling repositories—fat helper becomes service layer leak.
- Static util classes untested—use injectable components.
- Domain calculations duplicated in helper and service—single source of truth.

#### Follow-up (with answer)
**Q:** View Helper vs DTO?
**A:** DTO transports data shape across layers—may be anemic records. View Helper contains logic producing view-tailored DTO (ViewModel)—formatting, sorting for display, derived labels. ViewModel is output of helper; helper is the behavior assembling it.

---

### P179. Virtual Proxy

**Category:** Structural
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/virtual-proxy/)

**Short answer:** Virtual Proxy delays creation or loading of expensive real object until actually needed—lazy initialization, lazy associations, remote stub loading on first access. Hibernate lazy proxies are canonical. Trade-off: `LazyInitializationException` when accessed outside session; N+1 query surprises.

#### Scenario (interview)
**Situation:** `GET /customers` list endpoint returns 500 customers; Hibernate issues 501 queries loading `orders` collection on each row because JSON serializer touched lazy `orders` field.
**What they're testing:** Lazy loading proxy behavior, DTO projection, fetch joins, and Open Session In View pitfalls.
**Model answer:** Virtual Proxy: Hibernate replaces `orders` with lazy collection proxy until accessed—serializer triggered N+1. Fix: don't expose entity—map to `CustomerSummaryDto` without orders field. Or `@EntityGraph(attributePaths={"..."})` only when needed. `JOIN FETCH` in dedicated query for detail endpoint. Disable OSIV—fail fast in dev on lazy access in view layer. For expensive service clients, virtual proxy bean loads real client on first method call—double-checked locking or Spring `@Lazy` injection. `@Lazy @Autowired ExpensiveClient` delays init until use. Metrics: query count per request via datasource proxy. Detail vs list endpoints different fetch strategies—virtual proxy fine for detail on demand. Batch size `@BatchSize(50)` mitigates N+1 if must lazy load. Document API contract: list never includes orders. Testing: assert query count with `@DataJpaTest` statistics.

#### What it is
Virtual Proxy acts as placeholder for expensive-to-create object, delegating to real subject when client invokes operations that require full initialization.

#### When to use / when NOT
- **Use:** Costly object graphs; remote objects; large binary/metadata load on demand.
- **NOT:** Cheap objects—premature indirection; when eager fetch known required—load upfront.

#### Java / Spring example
```java
@Entity
public class Customer {
    @OneToMany(fetch = FetchType.LAZY) // virtual collection proxy
    private List<Order> orders;
}
@Service
public class ReportService(@Lazy HeavyAnalyticsClient analytics) { ... }
```

#### Common mistakes
- Serializing lazy proxies to JSON—N+1 or exception.
- `@Lazy` on everything—debugging pain, hidden I/O.
- Accessing lazy relations after session closed.

#### Follow-up (with answer)
**Q:** Virtual Proxy vs Lazy Loading pattern?
**A:** Virtual Proxy is GoF structural pattern—placeholder object with same interface. Lazy Loading is persistence tactic deferring data fetch—ORM implements via virtual proxy subclasses (`Customer$HibernateProxy`). Lazy Loading is how Virtual Proxy manifests in JPA; conceptually aligned.

---

### P180. Visitor

**Category:** Behavioral
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/visitor/)

**Short answer:** Visitor separates algorithms from object structure—double dispatch `element.accept(visitor)` lets new operations without changing element classes. Ideal for stable hierarchies (AST, tax forms) with many operations. Trade-off: adding new element types requires updating all visitors—violates open-closed for types.

#### Scenario (interview)
**Situation:** Tax document AST has `IncomeNode`, `DeductionNode`, `CreditNode`. Need export to JSON, XML, and IRS validator—team adds `toJson()` methods on each node class; nodes bloated with unrelated concerns.
**What they're testing:** Double dispatch, when Visitor beats instanceof chains, sealed types alternative in modern Java.
**Model answer:** Refactor to Visitor: `interface TaxNode { void accept(TaxVisitor v); }`—`JsonExportVisitor`, `XmlExportVisitor`, `IrsValidationVisitor` each implement `visitIncome`, `visitDeduction`, etc. Add new export format = new visitor class, zero node edits. Nodes stay data + `accept` only. When hierarchy stable, operations vary—Visitor wins. When node types frequently added—Visitor hurts; consider sealed interface + pattern switch (Java 21) for fewer operations. Double dispatch: `node.accept(visitor)` calls `visitor.visitIncome(this)`. Performance: avoid reflection-based visitor. Spring batch: different visitors for pipeline stages on same document tree. Testing: each visitor isolated unit tests. Contrast Interpreter—Visitor operates on structure, doesn't interpret grammar. Acyclic Visitor if dependency cycles between visitor types. Document trade-off table for team when to add node vs visitor.

#### What it is
Visitor lets you define new operations on elements of an object structure without changing the element classes, using accept/visit double dispatch.

#### When to use / when NOT
- **Use:** Stable class hierarchy; many distinct operations across types; compiler/AST/export pipelines.
- **NOT:** Frequently changing element types; simple two-type hierarchy—`switch` or polymorphism enough.

#### Java / Spring example
```java
public interface TaxVisitor {
    void visitIncome(IncomeNode n);
    void visitDeduction(DeductionNode n);
}
public class JsonExportVisitor implements TaxVisitor { ... }
```

#### Common mistakes
- Visitor when hierarchy unstable—constant visitor churn.
- Exposing internal node children publicly for visitor—breaks encapsulation.
- Ignoring sealed types/switch as simpler modern alternative.

#### Follow-up (with answer)
**Q:** Visitor vs `switch` on sealed types?
**A:** Java sealed hierarchies + exhaustive switch replace Visitor for moderate operation count without visitor class proliferation. Visitor still wins when operations are large classes with state, many operations, or need open extension in libraries. Sealed switch keeps logic colocated; Visitor distributes across classes. Choose based on change frequency: types vs operations.

---

### P181. Write-Ahead Log

**Category:** Enterprise
**Catalog:** [java-design-patterns.com](https://java-design-patterns.com/patterns/write-ahead-log/)

**Short answer:** Write-Ahead Log (WAL) appends changes to a sequential log before applying to main storage—enabling crash recovery, replication, and audit. Databases, Kafka, and Raft use WAL. Trade-off: log durability and compaction/retention management; replay time on recovery.

#### Scenario (interview)
**Situation:** Custom in-memory account ledger loses all balances on JVM crash mid-batch transfer. Team debates snapshotting full state to Postgres every second vs rebuilding from events.
**What they're testing:** Durability, recovery, WAL vs snapshot trade-offs, alignment with event sourcing.
**Model answer:** Implement Write-Ahead Log: before mutating in-memory `Map<Account, Balance>`, append `TransferEntry(debit, credit, amount, txId)` to durable log (Kafka topic or append-only file with `fsync`). On startup, replay log entries idempotently applying to rebuild state. Periodic snapshot checkpoint every N entries or T minutes—recovery replays snapshot + tail of log since checkpoint. WAL gives total order and crash safety—if crash after log append but before memory update, replay fixes; if before append, operation lost (client retries). Use `txId` idempotency. Contrast snapshot-only every second—may lose last second or corrupt mid-write without WAL. Kafka IS a distributed WAL for streams. Size management: log compaction keyed by account retains latest balance per key if using compacted topic. Tests: kill -9 after append, restart, balances consistent. Metrics: replay duration, log lag. Don't confuse with Transactional Outbox—outbox integrates services; WAL is storage engine durability pattern. For full audit, retain immutable log; snapshots only optimization.

#### What it is
Write-Ahead Log records intended changes to an append-only durable log before they are applied to primary data structures, allowing recovery by replaying the log after failure.

#### When to use / when NOT
- **Use:** Custom storage engines; in-memory state needing durability; replication primary; audit trail.
- **NOT:** Simple CRUD with ACID database already providing WAL internally; when replay cost exceeds snapshot-only tolerance without checkpoints.

#### Java / Spring example
```java
public void transfer(AccountId from, AccountId to, Money amt) {
    var entry = new LogEntry(txId(), from, to, amt);
    wal.append(entry);           // fsync before
    ledger.apply(entry);         // mutate memory
}
```

#### Common mistakes
- Applying memory before durable log—crash loses consistency.
- Unbounded log without snapshot/compaction—slow recovery.
- Non-idempotent replay—double apply on recovery duplicates money.

#### Follow-up (with answer)
**Q:** WAL vs Event Sourcing?
**A:** WAL is infrastructure pattern for durability and recovery—log entries may be low-level physical changes. Event Sourcing stores domain events as source of truth for business state and projections. Event sourcing often uses WAL/Kafka underneath. WAL focuses on crash safety; event sourcing on domain history and multiple read models. You can event-source without custom WAL if database provides durability; custom in-memory engines need WAL.

---

*End of Part 4 — Patterns P136–P181*


