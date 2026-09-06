# Design Patterns — Practical Exercises

Type these. Run them. Break them. Reading is not practice.

**28 exercises:** Part A Basic (10) · Part B Intermediate (10) · Part C Hard (8) · Weekend challenge

---

# Part A — Basic

## Exercise 1 — Strategy: fee calculator (enum-safe)

**Difficulty:** Basic

**Task:** Implement a `FeeService` that picks a fee algorithm by `ProductType` without `switch`. Fail fast at startup if any enum value lacks a strategy.

**Solution:**

```java
import java.util.EnumMap;
import java.util.List;
import java.util.Map;

enum ProductType { RETAIL, WHOLESALE, INTERNAL }

interface FeeCalc { ProductType type(); long feeCents(long amount); }

final class RetailFee implements FeeCalc {
    public ProductType type() { return ProductType.RETAIL; }
    public long feeCents(long amount) { return Math.max(30, amount * 2 / 100); }
}

final class WholesaleFee implements FeeCalc {
    public ProductType type() { return ProductType.WHOLESALE; }
    public long feeCents(long amount) { return 50; }
}

final class InternalFee implements FeeCalc {
    public ProductType type() { return ProductType.INTERNAL; }
    public long feeCents(long amount) { return 0; }
}

final class FeeService {
    private final Map<ProductType, FeeCalc> byType = new EnumMap<>(ProductType.class);

    FeeService(List<FeeCalc> calcs) {
        for (FeeCalc c : calcs) {
            if (byType.put(c.type(), c) != null) throw new IllegalStateException("dup " + c.type());
        }
        if (byType.size() != ProductType.values().length)
            throw new IllegalStateException("missing calculator");
    }

    long fee(ProductType t, long amount) {
        return byType.get(t).feeCents(amount);
    }

    public static void main(String[] args) {
        var svc = new FeeService(List.of(new RetailFee(), new WholesaleFee(), new InternalFee()));
        System.out.println(svc.fee(ProductType.RETAIL, 10_000)); // 200
        System.out.println(svc.fee(ProductType.WHOLESALE, 10_000)); // 50
    }
}
```

**Senior takeaway:** Spring does the same with `List<FeeCalc>` injection into an `EnumMap` registry — new product types fail at startup, not in prod.

---

## Exercise 2 — Factory Method: notification channel

**Difficulty:** Basic

**Task:** Each channel (`Email`, `Sms`) knows how to create its own `Notification`. No central `switch` on type strings.

**Solution:**

```java
interface Notification { void send(String to, String body); }

final class EmailNotification implements Notification {
    public void send(String to, String body) { System.out.println("EMAIL to=" + to + " body=" + body); }
}

final class SmsNotification implements Notification {
    public void send(String to, String body) { System.out.println("SMS to=" + to + " body=" + body); }
}

interface NotificationFactory { Notification create(); }

final class EmailFactory implements NotificationFactory {
    public Notification create() { return new EmailNotification(); }
}

final class SmsFactory implements NotificationFactory {
    public Notification create() { return new SmsNotification(); }
}

final class NotifyApp {
    public static void main(String[] args) {
        NotificationFactory factory = new EmailFactory();
        factory.create().send("user@corp.com", "order shipped");
    }
}
```

**Senior takeaway:** `@Bean` methods in `@Configuration` are factory methods — the container is the factory registry.

---

## Exercise 3 — Singleton: enum (thread-safe, serialization-safe)

**Difficulty:** Basic

**Task:** Implement a config holder as an enum singleton. Prove reflection cannot create a second instance easily (document why enum wins over double-checked locking).

**Solution:**

```java
enum AppConfig {
    INSTANCE;

    private volatile String region = "us-east-1";

    String region() { return region; }
    void setRegion(String r) { this.region = r; }
}

public class EnumSingletonDemo {
    public static void main(String[] args) {
        AppConfig.INSTANCE.setRegion("eu-west-1");
        System.out.println(AppConfig.INSTANCE.region());
        System.out.println(AppConfig.INSTANCE == AppConfig.INSTANCE); // true
    }
}
```

**Senior takeaway:** Prefer a Spring `@ConfigurationProperties` bean over hand-rolled singletons — testability beats the pattern.

---

## Exercise 4 — Observer: in-memory event bus

**Difficulty:** Basic

**Task:** `OrderPlaced` events fan out to `InventoryListener` and `EmailListener` without the publisher knowing subscribers.

**Solution:**

```java
import java.util.ArrayList;
import java.util.List;
import java.util.function.Consumer;

record OrderPlaced(String orderId, long amountCents) {}

final class EventBus {
    private final List<Consumer<OrderPlaced>> listeners = new ArrayList<>();

    void subscribe(Consumer<OrderPlaced> l) { listeners.add(l); }

    void publish(OrderPlaced e) {
        for (var l : listeners) l.accept(e);
    }
}

final class InventoryListener {
    void on(OrderPlaced e) { System.out.println("reserve stock " + e.orderId()); }
}

final class EmailListener {
    void on(OrderPlaced e) { System.out.println("email receipt " + e.orderId()); }
}

public class ObserverDemo {
    public static void main(String[] args) {
        var bus = new EventBus();
        var inv = new InventoryListener();
        var mail = new EmailListener();
        bus.subscribe(inv::on);
        bus.subscribe(mail::on);
        bus.publish(new OrderPlaced("ORD-1", 4999));
    }
}
```

**Senior takeaway:** Spring `ApplicationEventPublisher` + `@EventListener` is the production version; use `@TransactionalEventListener(phase = AFTER_COMMIT)` for side effects.

---

## Exercise 5 — Adapter: legacy XML name check

**Difficulty:** Basic

**Task:** Wrap `LegacyNameCheck.checkName(String xml)` behind a clean `NameCheckPort`. Domain code never sees XML.

**Solution:**

```java
// legacy jar
final class LegacyNameCheck {
    String checkName(String xml) {
        return xml.contains("BLOCKED") ? "SANCTIONED" : "CLEAR";
    }
}

interface NameCheckPort { boolean isSanctioned(String legalName); }

final class LegacyNameCheckAdapter implements NameCheckPort {
    private final LegacyNameCheck client = new LegacyNameCheck();

    public boolean isSanctioned(String legalName) {
        String xml = "<name>" + escape(legalName) + "</name>";
        return "SANCTIONED".equals(client.checkName(xml));
    }

    private static String escape(String s) {
        return s.replace("&", "&amp;").replace("<", "&lt;");
    }
}

public class AdapterDemo {
    public static void main(String[] args) {
        NameCheckPort port = new LegacyNameCheckAdapter();
        System.out.println(port.isSanctioned("BLOCKED CORP")); // true
        System.out.println(port.isSanctioned("ACME INC")); // false
    }
}
```

**Senior takeaway:** Adapters belong at the boundary (hexagonal port). Tests use a fake `NameCheckPort`, not the legacy client.

---

## Exercise 6 — Decorator: audit + timing around a port

**Difficulty:** Basic

**Task:** Stack decorators around `PaymentPort` without modifying `StripeAdapter`.

**Solution:**

```java
interface PaymentPort { String charge(String customerId, long cents); }

final class StripeAdapter implements PaymentPort {
    public String charge(String customerId, long cents) { return "ch_123"; }
}

final class TimingDecorator implements PaymentPort {
    private final PaymentPort inner;
    TimingDecorator(PaymentPort inner) { this.inner = inner; }
    public String charge(String customerId, long cents) {
        long t0 = System.nanoTime();
        try {
            return inner.charge(customerId, cents);
        } finally {
            System.out.println("charge ns=" + (System.nanoTime() - t0));
        }
    }
}

final class AuditDecorator implements PaymentPort {
    private final PaymentPort inner;
    AuditDecorator(PaymentPort inner) { this.inner = inner; }
    public String charge(String customerId, long cents) {
        System.out.println("audit customer=" + customerId + " cents=" + cents);
        return inner.charge(customerId, cents);
    }
}

public class DecoratorDemo {
    public static void main(String[] args) {
        PaymentPort port = new AuditDecorator(new TimingDecorator(new StripeAdapter()));
        System.out.println(port.charge("cust-1", 1000));
    }
}
```

**Senior takeaway:** Spring AOP `@Around` is decorator via proxy — same stacking idea, same self-invocation trap.

---

## Exercise 7 — Template Method: ETL skeleton

**Difficulty:** Basic

**Task:** `EtlJob` defines `extract → transform → load` order; subclasses only fill steps.

**Solution:**

```java
abstract class EtlJob {
    public final void run() {
        var raw = extract();
        var clean = transform(raw);
        load(clean);
    }
    abstract String extract();
    abstract String transform(String raw);
    abstract void load(String data);
}

final class UserExportJob extends EtlJob {
    String extract() { return "id,name\n1,Ada"; }
    String transform(String raw) { return raw.toUpperCase(); }
    void load(String data) { System.out.println("loaded:\n" + data); }
}

public class TemplateDemo {
    public static void main(String[] args) {
        new UserExportJob().run();
    }
}
```

**Senior takeaway:** Prefer composition (`JobRunner` + lambdas) when you need flexible step ordering — template method inheritance is rigid.

---

## Exercise 8 — Builder: immutable order

**Difficulty:** Basic

**Task:** Build an `Order` with validation (non-empty lines, positive total) using a fluent builder.

**Solution:**

```java
import java.util.ArrayList;
import java.util.List;

final class Order {
    private final String customerId;
    private final List<String> lines;
    private final long totalCents;

    private Order(String customerId, List<String> lines, long totalCents) {
        this.customerId = customerId;
        this.lines = List.copyOf(lines);
        this.totalCents = totalCents;
    }

    static Builder builder() { return new Builder(); }

    static final class Builder {
        private String customerId;
        private final List<String> lines = new ArrayList<>();
        private long totalCents;

        Builder customerId(String id) { this.customerId = id; return this; }
        Builder line(String sku) { lines.add(sku); return this; }
        Builder totalCents(long c) { this.totalCents = c; return this; }

        Order build() {
            if (customerId == null || customerId.isBlank()) throw new IllegalStateException("customer");
            if (lines.isEmpty()) throw new IllegalStateException("lines");
            if (totalCents <= 0) throw new IllegalStateException("total");
            return new Order(customerId, lines, totalCents);
        }
    }

    @Override public String toString() {
        return "Order{customer=" + customerId + ", lines=" + lines + ", total=" + totalCents + "}";
    }
}

public class BuilderDemo {
    public static void main(String[] args) {
        var o = Order.builder().customerId("c-1").line("SKU-A").totalCents(999).build();
        System.out.println(o);
    }
}
```

**Senior takeaway:** Records + compact constructor validation often replace builders for simple DTOs; use builder when optional fields are numerous.

---

## Exercise 9 — Prototype: document clone

**Difficulty:** Basic

**Task:** Clone a `ReportTemplate` (deep copy of mutable fields) so edits to the clone do not affect the original.

**Solution:**

```java
import java.util.ArrayList;
import java.util.List;

final class ReportTemplate implements Cloneable {
    String title;
    List<String> sections = new ArrayList<>();

    ReportTemplate(String title, List<String> sections) {
        this.title = title;
        this.sections = new ArrayList<>(sections);
    }

    @Override
    public ReportTemplate clone() {
        try {
            ReportTemplate copy = (ReportTemplate) super.clone();
            copy.sections = new ArrayList<>(this.sections);
            return copy;
        } catch (CloneNotSupportedException e) {
            throw new AssertionError(e);
        }
    }
}

public class PrototypeDemo {
    public static void main(String[] args) {
        var original = new ReportTemplate("Q1", List.of("Revenue", "Costs"));
        var draft = original.clone();
        draft.sections.add("Forecast");
        System.out.println(original.sections); // [Revenue, Costs]
        System.out.println(draft.sections);    // [Revenue, Costs, Forecast]
    }
}
```

**Senior takeaway:** Prefer copy constructors or records over `Cloneable` — the interface is a JDK footgun.

---

## Exercise 10 — Facade: simplified payments API

**Difficulty:** Basic

**Task:** Hide `FraudCheck`, `Ledger`, and `Gateway` behind one `CheckoutFacade.checkout()` call.

**Solution:**

```java
final class FraudCheck {
    void scan(String customerId, long cents) {
        if (cents > 1_000_000) throw new IllegalStateException("fraud");
    }
}

final class Ledger {
    void debit(String customerId, long cents) { System.out.println("debit " + customerId + " " + cents); }
}

final class Gateway {
    String charge(long cents) { return "gw-" + cents; }
}

final class CheckoutFacade {
    private final FraudCheck fraud = new FraudCheck();
    private final Ledger ledger = new Ledger();
    private final Gateway gateway = new Gateway();

    String checkout(String customerId, long cents) {
        fraud.scan(customerId, cents);
        ledger.debit(customerId, cents);
        return gateway.charge(cents);
    }
}

public class FacadeDemo {
    public static void main(String[] args) {
        System.out.println(new CheckoutFacade().checkout("c-9", 2500));
    }
}
```

**Senior takeaway:** A Spring `@Service` orchestrating repositories and clients is often a facade — keep it thin; business rules belong in domain services.

---

# Part B — Intermediate

## Exercise 11 — Proxy: JDK dynamic proxy for logging

**Difficulty:** Intermediate

**Task:** Wrap `PaymentPort` with `Proxy.newProxyInstance` to log method name and args. Compare with manual decorator from Exercise 6.

**Solution:**

```java
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;

interface PaymentPort { String charge(String customerId, long cents); }

final class StripeAdapter implements PaymentPort {
    public String charge(String customerId, long cents) { return "ch_123"; }
}

final class LoggingHandler implements InvocationHandler {
    private final Object target;
    LoggingHandler(Object target) { this.target = target; }

    public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
        System.out.println("call " + method.getName() + " args=" + java.util.Arrays.toString(args));
        return method.invoke(target, args);
    }
}

public class JdkProxyDemo {
    public static void main(String[] args) {
        PaymentPort real = new StripeAdapter();
        PaymentPort proxy = (PaymentPort) Proxy.newProxyInstance(
                PaymentPort.class.getClassLoader(),
                new Class<?>[]{PaymentPort.class},
                new LoggingHandler(real));
        System.out.println(proxy.charge("c-1", 500));
    }
}
```

**Senior takeaway:** Spring `@Transactional` uses CGLIB/JDK proxies — only **external** calls through the proxy get advice; `this.pay()` bypasses it.

---

## Exercise 12 — Chain of Responsibility: validation pipeline

**Difficulty:** Intermediate

**Task:** Build a chain `NotBlank → MaxLength → Regex` for usernames. Each link can pass or throw.

**Solution:**

```java
import java.util.function.UnaryOperator;
import java.util.regex.Pattern;

abstract class Validator implements UnaryOperator<String> {
    private Validator next;

    Validator link(Validator n) { this.next = n; return n; }

    @Override
    public final String apply(String value) {
        validate(value);
        return next == null ? value : next.apply(value);
    }

    abstract void validate(String value);
}

final class NotBlank extends Validator {
    void validate(String v) {
        if (v == null || v.isBlank()) throw new IllegalArgumentException("blank");
    }
}

final class MaxLen extends Validator {
    private final int max;
    MaxLen(int max) { this.max = max; }
    void validate(String v) {
        if (v.length() > max) throw new IllegalArgumentException("too long");
    }
}

final class UsernamePattern extends Validator {
    private static final Pattern P = Pattern.compile("[a-z0-9_]{3,20}");
    void validate(String v) {
        if (!P.matcher(v).matches()) throw new IllegalArgumentException("pattern");
    }
}

public class ChainDemo {
    public static void main(String[] args) {
        var head = new NotBlank();
        head.link(new MaxLen(20)).link(new UsernamePattern());
        System.out.println(head.apply("ada_lovelace"));
    }
}
```

**Senior takeaway:** `SecurityFilterChain` is chain of responsibility — order matters; one mis-ordered filter breaks auth.

---

## Exercise 13 — State: order lifecycle without a framework

**Difficulty:** Intermediate

**Task:** Model `Draft → Paid → Shipped` and `Cancelled` with illegal transitions throwing.

**Solution:**

```java
sealed interface OrderState permits Draft, Paid, Shipped, Cancelled {}
record Draft() implements OrderState {}
record Paid(String paymentId) implements OrderState {}
record Shipped(String tracking) implements OrderState {}
record Cancelled(String reason) implements OrderState {}

final class Order {
    private OrderState state = new Draft();

    void pay(String paymentId) {
        if (!(state instanceof Draft)) throw new IllegalStateException("cannot pay from " + state);
        state = new Paid(paymentId);
    }

    void ship(String tracking) {
        if (!(state instanceof Paid)) throw new IllegalStateException("cannot ship from " + state);
        state = new Shipped(tracking);
    }

    void cancel(String reason) {
        switch (state) {
            case Shipped s -> throw new IllegalStateException("already shipped");
            default -> state = new Cancelled(reason);
        }
    }

    OrderState state() { return state; }
}

public class StateDemo {
    public static void main(String[] args) {
        var o = new Order();
        o.pay("pay-1");
        o.ship("TRK-9");
        System.out.println(o.state());
    }
}
```

**Senior takeaway:** Sealed types + pattern matching often replace State classes — use explicit state objects when transitions carry data or side effects.

---

## Exercise 14 — Spring Strategy registry (`List` injection)

**Difficulty:** Intermediate

**Task:** Wire multiple `ShippingRateStrategy` beans into a registry. Adding a new `ShippingMode` enum value without a bean must fail startup.

**Solution:**

```java
// Plain-Java equivalent of Spring wiring (run as main)
import java.util.EnumMap;
import java.util.List;
import java.util.Map;

enum ShippingMode { STANDARD, EXPRESS }

interface ShippingRateStrategy {
    ShippingMode mode();
    long rateCents(long weightGrams);
}

final class StandardRate implements ShippingRateStrategy {
    public ShippingMode mode() { return ShippingMode.STANDARD; }
    public long rateCents(long w) { return 500 + w / 10; }
}

final class ExpressRate implements ShippingRateStrategy {
    public ShippingMode mode() { return ShippingMode.EXPRESS; }
    public long rateCents(long w) { return 1500 + w / 5; }
}

final class ShippingRegistry {
    private final Map<ShippingMode, ShippingRateStrategy> map = new EnumMap<>(ShippingMode.class);

    ShippingRegistry(List<ShippingRateStrategy> strategies) {
        for (var s : strategies) {
            if (map.put(s.mode(), s) != null) throw new IllegalStateException("dup " + s.mode());
        }
        if (map.size() != ShippingMode.values().length)
            throw new IllegalStateException("missing strategy");
    }

    long quote(ShippingMode m, long weight) { return map.get(m).rateCents(weight); }
}

/*
@SpringBootApplication
class App {}
@Component class StandardRate implements ShippingRateStrategy { ... }
@Component class ExpressRate implements ShippingRateStrategy { ... }
@Service
class ShippingRegistry {
    ShippingRegistry(List<ShippingRateStrategy> strategies) { ... }
}
*/

public class SpringStrategyDemo {
    public static void main(String[] args) {
        var reg = new ShippingRegistry(List.of(new StandardRate(), new ExpressRate()));
        System.out.println(reg.quote(ShippingMode.EXPRESS, 1000));
    }
}
```

**Senior takeaway:** `List<MyStrategy>` + `EnumMap` is the Spring-native strategy registry — no `@Qualifier` spaghetti.

---

## Exercise 15 — Spring Factory: `@Configuration` beans

**Difficulty:** Intermediate

**Task:** A factory method chooses `PaymentPort` implementation from a property (`stripe` vs `fake`). Show conditional `@Bean`.

**Solution:**

```java
// Runnable simulation — in Spring, PaymentConfig is @Configuration
interface PaymentPort { String charge(long cents); }

final class StripePort implements PaymentPort {
    public String charge(long cents) { return "stripe:" + cents; }
}

final class FakePort implements PaymentPort {
    public String charge(long cents) { return "fake:" + cents; }
}

final class PaymentConfig {
    PaymentPort paymentPort(String provider) {
        return "stripe".equalsIgnoreCase(provider) ? new StripePort() : new FakePort();
    }
}

public class FactoryBeanDemo {
    public static void main(String[] args) {
        var cfg = new PaymentConfig();
        PaymentPort port = cfg.paymentPort(System.getenv().getOrDefault("PAY_PROVIDER", "fake"));
        System.out.println(port.charge(100));
    }
}
```

```java
// Spring version
/*
@Configuration
class PaymentConfig {
    @Bean
    @ConditionalOnProperty(name = "app.payments.provider", havingValue = "stripe")
    PaymentPort stripe() { return new StripePort(); }

    @Bean
    @ConditionalOnProperty(name = "app.payments.provider", havingValue = "fake", matchIfMissing = true)
    PaymentPort fake() { return new FakePort(); }
}
*/
```

**Senior takeaway:** Factory methods + `@ConditionalOn*` beat `if (profile)` in `@PostConstruct` — beans you don't need are never created.

---

## Exercise 16 — Template Method vs composition

**Difficulty:** Intermediate

**Task:** Rewrite a template-method ETL (Exercise 7) using a `JobRunner` and lambdas. Write a unit test that stubs `extract` only.

**Solution:**

```java
import java.util.function.Consumer;
import java.util.function.Function;
import java.util.function.Supplier;

final class JobRunner {
    <T, R> void run(Supplier<T> extract, Function<T, R> transform, Consumer<R> load) {
        R out = transform.apply(extract.get());
        load.accept(out);
    }
}

public class CompositionDemo {
    public static void main(String[] args) {
        var runner = new JobRunner();
        runner.run(
                () -> "id,name\n1,Ada",
                raw -> raw.toUpperCase(),
                data -> System.out.println("loaded:\n" + data)
        );
    }
}
```

```java
// JUnit 5
/*
@Test
void transformOnly() {
    var runner = new JobRunner();
    AtomicReference<String> loaded = new AtomicReference<>();
    runner.run(() -> "x", s -> s + "-OK", loaded::set);
    assertEquals("x-OK", loaded.get());
}
*/
```

**Senior takeaway:** Composition + DI is easier to test and extend than inheritance — template method is for frameworks (JUnit, Servlet), not app code.

---

## Exercise 17 — Observer: Spring `ApplicationEventPublisher`

**Difficulty:** Intermediate

**Task:** Publish `OrderPlaced` after DB commit. Listener sends email. Show `@TransactionalEventListener(phase = AFTER_COMMIT)`.

**Solution:**

```java
// Plain Java: commit-then-publish simulation
final class Tx {
    private final Runnable work;
    private final Runnable afterCommit;
    Tx(Runnable work, Runnable afterCommit) { this.work = work; this.afterCommit = afterCommit; }
    void run() {
        work.run();
        afterCommit.run(); // AFTER_COMMIT
    }
}

record OrderPlaced(String orderId) {}

public class AfterCommitDemo {
    public static void main(String[] args) {
        new Tx(
                () -> System.out.println("INSERT order"),
                () -> System.out.println("EVENT OrderPlaced -> send email")
        ).run();
    }
}
```

```java
/*
@Service
class OrderService {
    private final ApplicationEventPublisher events;
    @Transactional
    void place(String id) {
        // save...
        events.publishEvent(new OrderPlaced(id));
    }
}

@Component
class EmailOnOrder {
    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    void on(OrderPlaced e) { mailer.send(e.orderId()); }
}
*/
```

**Senior takeaway:** Publishing before commit risks email for a rolled-back order — `AFTER_COMMIT` is the fix.

---

## Exercise 18 — Flyweight: character glyph pool

**Difficulty:** Intermediate

**Task:** Share immutable `Glyph` instances for repeated characters in a document renderer.

**Solution:**

```java
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

final class Glyph {
    private final char ch;
    private final String font;
    Glyph(char ch, String font) { this.ch = ch; this.font = font; }
    void render() { System.out.println(font + ":" + ch); }
}

final class GlyphFactory {
    private final Map<String, Glyph> pool = new ConcurrentHashMap<>();

    Glyph get(char ch, String font) {
        String key = font + ":" + ch;
        return pool.computeIfAbsent(key, k -> new Glyph(ch, font));
    }

    int poolSize() { return pool.size(); }
}

public class FlyweightDemo {
    public static void main(String[] args) {
        var factory = new GlyphFactory();
        "hello".chars().forEach(c -> factory.get((char) c, "Arial").render());
        System.out.println("pool size=" + factory.poolSize()); // 4 (h,e,l,o)
    }
}
```

**Senior takeaway:** `Integer.valueOf` caching and connection pool metadata are flyweights — only when many instances share heavy immutable state.

---

## Exercise 19 — Command: undoable text editor

**Difficulty:** Intermediate

**Task:** Implement `AppendCommand` with `execute` and `undo`. Maintain a command stack.

**Solution:**

```java
import java.util.ArrayDeque;
import java.util.Deque;

interface Command { void execute(); void undo(); }

final class TextBuffer {
    private final StringBuilder sb = new StringBuilder();
    void append(String s) { sb.append(s); }
    void deleteLast(int n) { sb.setLength(sb.length() - n); }
    String text() { return sb.toString(); }
}

final class AppendCommand implements Command {
    private final TextBuffer buf;
    private final String text;
    AppendCommand(TextBuffer buf, String text) { this.buf = buf; this.text = text; }
    public void execute() { buf.append(text); }
    public void undo() { buf.deleteLast(text.length()); }
}

final class CommandStack {
    private final Deque<Command> done = new ArrayDeque<>();
    void run(Command c) { c.execute(); done.push(c); }
    void undo() { if (!done.isEmpty()) done.pop().undo(); }
}

public class CommandDemo {
    public static void main(String[] args) {
        var buf = new TextBuffer();
        var stack = new CommandStack();
        stack.run(new AppendCommand(buf, "Hello"));
        stack.run(new AppendCommand(buf, " World"));
        System.out.println(buf.text());
        stack.undo();
        System.out.println(buf.text()); // Hello
    }
}
```

**Senior takeaway:** CQRS command handlers are the enterprise Command pattern — keep commands immutable and idempotent where possible.

---

## Exercise 20 — Composite: file-system tree

**Difficulty:** Intermediate

**Task:** `File` and `Directory` both implement `Node` with `size()`. Sum sizes recursively.

**Solution:**

```java
import java.util.ArrayList;
import java.util.List;

interface FsNode { long sizeBytes(); }

final class FileNode implements FsNode {
    private final long size;
    FileNode(long size) { this.size = size; }
    public long sizeBytes() { return size; }
}

final class DirectoryNode implements FsNode {
    private final List<FsNode> children = new ArrayList<>();
    void add(FsNode n) { children.add(n); }
    public long sizeBytes() {
        return children.stream().mapToLong(FsNode::sizeBytes).sum();
    }
}

public class CompositeDemo {
    public static void main(String[] args) {
        var root = new DirectoryNode();
        root.add(new FileNode(100));
        var sub = new DirectoryNode();
        sub.add(new FileNode(50));
        root.add(sub);
        System.out.println(root.sizeBytes()); // 150
    }
}
```

**Senior takeaway:** Composite shines for tree structures (menus, org charts) — don't use it for flat lists with one item type.

---

# Part C — Hard

## Exercise 21 — Proxy self-invocation (`@Transactional` bypass)

**Difficulty:** Hard

**Task:** Demonstrate `payMany` calling `this.pay()` skips the transactional proxy. Fix with self-injection or extracted `PaymentTxService`. Write a test proving connection count.

**Solution:**

```java
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;

// Simulates Spring proxy: only external calls are advised
interface InvoiceApi { void pay(String id); void payMany(List<String> ids); }

final class RealInvoiceService implements InvoiceApi {
    private final AtomicInteger txCount = new AtomicInteger();

    public void pay(String id) {
        txCount.incrementAndGet();
        System.out.println("TX pay " + id);
    }

    public void payMany(List<String> ids) {
        ids.forEach(this::pay); // BYPASS — same object, no proxy
    }

    int txCount() { return txCount.get(); }
}

final class TransactionalProxy implements InvoiceApi {
    private final RealInvoiceService target;
    TransactionalProxy(RealInvoiceService target) { this.target = target; }

    public void pay(String id) { target.pay(id); } // advised

    public void payMany(List<String> ids) {
        ids.forEach(this::pay); // FIXED — goes through proxy
    }
}

public class SelfInvocationDemo {
    public static void main(String[] args) {
        var real = new RealInvoiceService();
        real.payMany(List.of("a", "b", "c"));
        System.out.println("broken tx count=" + real.txCount()); // 3 (no outer TX)

        var fixed = new TransactionalProxy(new RealInvoiceService());
        fixed.payMany(List.of("a", "b", "c"));
    }
}
```

```java
/*
@Service
public class InvoiceService {
    @Autowired @Lazy InvoiceService self;
    @Transactional public void pay(String id) { ... }
    public void payMany(List<String> ids) { ids.forEach(self::pay); }
}
*/
```

**Senior takeaway:** Any cross-cutting concern via proxy (cache, security, TX) has the same `this.` bug — extract a collaborator bean.

---

## Exercise 22 — Outbox pattern (transactional publish)

**Difficulty:** Hard

**Task:** In one transaction, insert `orders` + `outbox` row. A poller publishes unpublished rows. No dual-write to Kafka outside the DB transaction.

**Solution:**

```sql
CREATE TABLE orders (
  id VARCHAR(36) PRIMARY KEY,
  status VARCHAR(20) NOT NULL
);

CREATE TABLE outbox (
  id VARCHAR(36) PRIMARY KEY,
  aggregate_type VARCHAR(50) NOT NULL,
  aggregate_id VARCHAR(36) NOT NULL,
  event_type VARCHAR(80) NOT NULL,
  payload TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL,
  published_at TIMESTAMP NULL
);
```

```java
import java.time.Instant;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

record OutboxRow(String id, String aggregateId, String eventType, String payload, Instant createdAt) {}

final class InMemoryDb {
    final Map<String, String> orders = new ConcurrentHashMap<>();
    final List<OutboxRow> outbox = Collections.synchronizedList(new ArrayList<>());
}

final class OrderService {
    private final InMemoryDb db;
    OrderService(InMemoryDb db) { this.db = db; }

    void placeOrder(String orderId) {
        // @Transactional
        db.orders.put(orderId, "PLACED");
        db.outbox.add(new OutboxRow(
                UUID.randomUUID().toString(), orderId, "OrderPlaced",
                "{\"orderId\":\"" + orderId + "\"}", Instant.now()));
    }
}

final class OutboxPoller {
    private final InMemoryDb db;
    OutboxPoller(InMemoryDb db) { this.db = db; }

    int publishPending() {
        int n = 0;
        for (var row : List.copyOf(db.outbox)) {
            if (row.id() != null) {
                System.out.println("KAFKA publish " + row.payload());
                db.outbox.remove(row);
                n++;
            }
        }
        return n;
    }
}

public class OutboxDemo {
    public static void main(String[] args) {
        var db = new InMemoryDb();
        var svc = new OrderService(db);
        svc.placeOrder("ORD-42");
        System.out.println("outbox pending=" + db.outbox.size());
        new OutboxPoller(db).publishPending();
        System.out.println("outbox pending=" + db.outbox.size());
    }
}
```

**Senior takeaway:** Outbox + Debezium or polling is how you avoid "saved to DB but Kafka publish failed" — the pattern matters more than the library.

---

## Exercise 23 — Circuit breaker (understand, then use Resilience4j)

**Difficulty:** Hard

**Task:** Implement a minimal breaker (closed → open → half-open). Then note what Resilience4j adds (metrics, decorators, Spring Boot integration).

**Solution:**

```java
import java.time.Instant;
import java.util.concurrent.atomic.AtomicInteger;

final class Breaker {
    enum State { CLOSED, OPEN, HALF }
    private volatile State state = State.CLOSED;
    private final AtomicInteger failures = new AtomicInteger();
    private volatile Instant openedAt = Instant.EPOCH;
    private final int threshold;
    private final long openMs;

    Breaker(int threshold, long openMs) {
        this.threshold = threshold;
        this.openMs = openMs;
    }

    <T> T execute(java.util.concurrent.Callable<T> c) throws Exception {
        if (state == State.OPEN) {
            if (Instant.now().toEpochMilli() - openedAt.toEpochMilli() > openMs) state = State.HALF;
            else throw new IllegalStateException("circuit open");
        }
        try {
            T r = c.call();
            failures.set(0);
            state = State.CLOSED;
            return r;
        } catch (Exception e) {
            if (failures.incrementAndGet() >= threshold || state == State.HALF) {
                state = State.OPEN;
                openedAt = Instant.now();
            }
            throw e;
        }
    }
}

final class FlakyRemote {
    private int calls;
    String call() {
        if (++calls <= 3) throw new RuntimeException("timeout");
        return "ok";
    }
}

public class BreakerDemo {
    public static void main(String[] args) throws Exception {
        var remote = new FlakyRemote();
        var breaker = new Breaker(2, 1000);
        for (int i = 0; i < 5; i++) {
            try {
                System.out.println(breaker.execute(remote::call));
            } catch (Exception e) {
                System.out.println("fail: " + e.getMessage());
            }
        }
    }
}
```

**Senior takeaway:** Breakers protect **your** thread pool, not the downstream — pair with timeouts, bulkheads, and retry only for idempotent ops.

---

## Exercise 24 — Anti-pattern: God Service refactor

**Difficulty:** Hard

**Task:** Given a 400-line `OrderGodService` that validates, prices, charges, emails, and updates inventory, split into ports + facades. Show before/after package layout.

**Solution (after):**

```java
interface PricingPort { long price(String sku, int qty); }
interface PaymentPort { void charge(String customerId, long cents); }
interface InventoryPort { void reserve(String sku, int qty); }
interface MailPort { void sendReceipt(String orderId); }

final class OrderApplicationService {
    private final PricingPort pricing;
    private final PaymentPort payments;
    private final InventoryPort inventory;
    private final MailPort mail;

    OrderApplicationService(PricingPort p, PaymentPort pay, InventoryPort inv, MailPort m) {
        this.pricing = p; this.payments = pay; this.inventory = inv; this.mail = m;
    }

    String place(String customerId, String sku, int qty) {
        long cents = pricing.price(sku, qty);
        String orderId = "ORD-" + System.nanoTime();
        inventory.reserve(sku, qty);
        payments.charge(customerId, cents);
        mail.sendReceipt(orderId);
        return orderId;
    }
}

// Each port has one adapter + fake for tests
public class GodServiceRefactorDemo {
    public static void main(String[] args) {
        var svc = new OrderApplicationService(
                (sku, qty) -> 1000L * qty,
                (c, cents) -> System.out.println("charged " + cents),
                (sku, qty) -> System.out.println("reserved " + sku),
                id -> System.out.println("mail " + id)
        );
        System.out.println(svc.place("c-1", "SKU-A", 2));
    }
}
```

**Senior takeaway:** "God service" is missing boundaries — hexagonal ports force single responsibility and test doubles.

---

## Exercise 25 — Anti-pattern: singleton global mutable state

**Difficulty:** Hard

**Task:** Show a `ConnectionManager.getInstance()` that breaks tests and hides lifecycle. Replace with DI + container-managed singleton scope.

**Solution:**

```java
// BAD
final class BadConnectionManager {
    private static final BadConnectionManager INSTANCE = new BadConnectionManager();
    private String jdbcUrl = "jdbc:prod";
    static BadConnectionManager getInstance() { return INSTANCE; }
    String url() { return jdbcUrl; }
    void setUrl(String u) { jdbcUrl = u; } // tests mutate prod singleton
}

// GOOD — one instance per app, injected
interface DataSourceConfig { String jdbcUrl(); }

final class AppDataSource implements DataSourceConfig {
    private final String jdbcUrl;
    AppDataSource(String jdbcUrl) { this.jdbcUrl = jdbcUrl; }
    public String jdbcUrl() { return jdbcUrl; }
}

public class SingletonAntiPatternDemo {
    public static void main(String[] args) {
        BadConnectionManager.getInstance().setUrl("jdbc:test");
        System.out.println(BadConnectionManager.getInstance().url()); // leaks between tests

        var good = new AppDataSource("jdbc:test");
        System.out.println(good.jdbcUrl());
    }
}
```

**Senior takeaway:** Spring `@Bean` default scope is singleton — that's DI singleton, not `static getInstance()` global state.

---

## Exercise 26 — When NOT to use a pattern (YAGNI)

**Difficulty:** Hard

**Task:** For each scenario, justify **no pattern** or a simpler alternative: (1) one payment provider, (2) two-state flag, (3) CRUD with no variation points.

**Solution:**

```java
// (1) One provider — direct call, no Strategy
final class StripeClient {
    String charge(long cents) { return "ch_" + cents; }
}

// (2) Two states — boolean or enum, no State hierarchy
enum JobStatus { PENDING, DONE }

// (3) CRUD — repository + service, no AbstractFactory
record UserDto(String id, String name) {}

interface UserRepository { Optional<UserDto> findById(String id); }

final class UserService {
    private final UserRepository repo;
    UserService(UserRepository repo) { this.repo = repo; }
    UserDto get(String id) { return repo.findById(id).orElseThrow(); }
}
```

**Senior takeaway:** Interviewers want judgment — "I'd start with a method, extract Strategy when the second implementation arrives."

---

## Exercise 27 — Refactor switch-on-type to sealed + pattern matching

**Difficulty:** Hard

**Task:** Replace `if (shape instanceof Circle)` chain with sealed `Shape` and `switch` expression. Discuss when Visitor still wins (many operations, stable types).

**Solution:**

```java
sealed interface Shape permits Circle, Rectangle {}
record Circle(double r) implements Shape {}
record Rectangle(double w, double h) implements Shape {}

final class Area {
    static double of(Shape s) {
        return switch (s) {
            case Circle c -> Math.PI * c.r() * c.r();
            case Rectangle r -> r.w() * r.h();
        };
    }
}

public class SealedRefactorDemo {
    public static void main(String[] args) {
        System.out.println(Area.of(new Circle(2)));
        System.out.println(Area.of(new Rectangle(3, 4)));
    }
}
```

**Senior takeaway:** Sealed + switch is the modern replacement for visitor-heavy ASTs **until** you add many operations — then Visitor or double dispatch returns.

---

## Exercise 28 — Pattern scavenger hunt + over-application audit

**Difficulty:** Hard

**Task:** In a Spring Boot app (or this checklist), map 10 real locations to patterns. Flag one **unnecessary** pattern you would remove.

**Solution:**

| Location | Pattern | Keep? |
|----------|---------|-------|
| `@RestController` | Front Controller + Adapter | Yes |
| `@Transactional` service | Proxy + Unit of Work | Yes |
| `KafkaTemplate.send` | Template Method | Yes |
| `PasswordEncoder` beans | Strategy | Yes |
| `SecurityFilterChain` | Chain of Responsibility | Yes |
| `ApplicationEventPublisher` | Observer | Yes |
| `@Configuration` `@Bean` | Factory Method | Yes |
| `CacheManager` wrapper | Proxy / Decorator | Yes |
| `AbstractRoutingDataSource` | Strategy | Yes |
| Custom `AbstractFactory` for 2 DTOs | Abstract Factory | **Remove** — use mapper |

```bash
# Drill: list all @Transactional, @Cacheable, @EventListener in your repo
rg '@Transactional|@Cacheable|@EventListener' src/ --glob '*.java'
```

**Senior takeaway:** Patterns are vocabulary for code review — over-application (factory for every DTO) is as bad as none.

---

# Weekend challenge

1. Implement Exercise 21 with a real `@SpringBootTest`, H2, and `DataSourceUtils.getConnection()` counting — prove `this::pay` vs `self::pay`.
2. Add Resilience4j circuit breaker around a `@FeignClient` and graph state transitions in Actuator metrics.
3. Pick one God Service in your codebase; draw ports and adapters on paper, then extract one port with a fake test.
4. Find one `switch (type)` string dispatch and refactor to sealed types or Strategy — measure lines deleted.
5. Write a one-page "when we don't use patterns here" doc for your team (onboarding gold).

---

**Stats:** 28 exercises · 10 Basic · 10 Intermediate · 8 Hard · 5 weekend drills · Topics: GoF (plain Java), Spring (strategy, factory, template, proxy, observer, chain), anti-patterns, when NOT to use
