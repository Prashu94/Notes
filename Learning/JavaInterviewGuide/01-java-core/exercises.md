# Java Core — Practical Exercises

**How to use:** Type, run, break. Progress **Basic → Intermediate → Hard**.

| Tier | Count | Focus |
|------|-------|-------|
| Basic | 10 | Syntax, APIs, small runnable mains |
| Intermediate | 10 | Bugs, JVM behavior, trade-offs |
| Hard | 8 | Production incidents, tuning, design |
| **Deep-dive** | **5** | **Q51–Q85 topics: concurrency, NIO, JVM tooling** |

---

# Part A — Basic

## Exercise 1 — Autoboxing `==` trap

**Difficulty:** Basic

**Task:** Run the program and explain every line of output. Rewrite the comparisons using the correct API.

**Solution:**

```java
public class Boxing {
    public static void main(String[] args) {
        Integer a = 127;
        Integer b = 127;
        Integer c = 128;
        Integer d = 128;
        System.out.println(a == b);       // true  (Integer cache: -128..127)
        System.out.println(c == d);       // false (distinct objects)
        System.out.println(c.equals(d));  // true  (value equality)

        Integer e = null;
        try {
            int x = e; // unboxing NPE
        } catch (NullPointerException npe) {
            System.out.println("unboxing NPE");
        }
    }
}
```

**Senior takeaway:** Never use `==` on wrappers in production; enable `-Xlint:boxing` and prefer primitives in hot loops.

---

## Exercise 2 — PECS: copy numbers between lists

**Difficulty:** Basic

**Task:** Write `copy` so `List<Integer>` can flow into `List<Object>` but not the reverse.

**Solution:**

```java
import java.util.ArrayList;
import java.util.List;

public class Pecs {
    public static void copy(List<? extends Number> src, List<? super Number> dest) {
        for (Number n : src) dest.add(n);
    }

    public static void main(String[] args) {
        List<Integer> ints = List.of(1, 2, 3);
        List<Object> sink = new ArrayList<>();
        copy(ints, sink);
        System.out.println(sink); // [1, 2, 3]
        // copy(sink, ints); // does not compile — Producer Extends, Consumer Super
    }
}
```

**Senior takeaway:** PECS is the standard pattern for generic utility methods; violating it at compile time prevents heap pollution.

---

## Exercise 3 — Records as immutable events

**Difficulty:** Basic

**Task:** Define a record with compact constructor validation. Instantiate and print it.

**Solution:**

```java
import java.time.Instant;
import java.util.Objects;

public record OrderPlaced(String orderId, String customerId, long amountCents, Instant at) {
    public OrderPlaced {
        Objects.requireNonNull(orderId, "orderId");
        Objects.requireNonNull(customerId, "customerId");
        Objects.requireNonNull(at, "at");
        if (amountCents <= 0) throw new IllegalArgumentException("amount must be positive");
    }

    public static void main(String[] args) {
        var evt = new OrderPlaced("ORD-1", "CUST-9", 4999L, Instant.now());
        System.out.println(evt);
        // evt.orderId = "x"; // does not compile — immutable
    }
}
```

**Senior takeaway:** Records are ideal Kafka/event payloads; pair with Jackson record support or explicit DTO mapping.

---

## Exercise 4 — try-with-resources and suppressed exceptions

**Difficulty:** Basic

**Task:** Run and list close order, primary exception, and suppressed exceptions.

**Solution:**

```java
public class SuppressedDemo implements AutoCloseable {
    private final String name;
    private final boolean throwOnClose;

    SuppressedDemo(String name, boolean throwOnClose) {
        this.name = name;
        this.throwOnClose = throwOnClose;
    }

    @Override
    public void close() {
        System.out.println("close " + name);
        if (throwOnClose) throw new RuntimeException("close failed: " + name);
    }

    public static void main(String[] args) {
        try (var a = new SuppressedDemo("A", true);
             var b = new SuppressedDemo("B", true)) {
            throw new RuntimeException("body");
        } catch (RuntimeException e) {
            System.out.println("primary: " + e.getMessage());
            for (Throwable s : e.getSuppressed()) {
                System.out.println("suppressed: " + s.getMessage());
            }
        }
    }
}
```

Expected: closes B then A (reverse declaration); primary `body`; suppressed close failures on A and B.

**Senior takeaway:** JDBC + stream close failures often hide the real SQLException in suppressed — always log `getSuppressed()`.

---

## Exercise 5 — Collections: List vs Set behavior

**Difficulty:** Basic

**Task:** Show duplicate handling in `ArrayList` vs `HashSet`, and stable iteration order in `LinkedHashSet`.

**Solution:**

```java
import java.util.ArrayList;
import java.util.HashSet;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;

public class CollectionsBasics {
    public static void main(String[] args) {
        List<String> list = new ArrayList<>();
        list.add("a");
        list.add("b");
        list.add("a");
        System.out.println("list size=" + list.size()); // 3

        Set<String> hash = new HashSet<>(list);
        System.out.println("hashSet=" + hash); // order undefined, size 2

        Set<String> linked = new LinkedHashSet<>(list);
        System.out.println("linkedHashSet=" + linked); // [a, b] insertion order
    }
}
```

**Senior takeaway:** Choose collection by access pattern — `List` for duplicates/order-by-index, `Set` for uniqueness, `LinkedHashSet` when you need predictable iteration.

---

## Exercise 6 — HashMap: get, put, and null keys

**Difficulty:** Basic

**Task:** Demonstrate one null key and multiple null values. Explain `get` vs `getOrDefault`.

**Solution:**

```java
import java.util.HashMap;
import java.util.Map;

public class HashMapBasics {
    public static void main(String[] args) {
        Map<String, Integer> map = new HashMap<>();
        map.put(null, 0);
        map.put("a", 1);
        map.put("b", null);

        System.out.println(map.get(null));           // 0
        System.out.println(map.containsKey("b"));    // true
        System.out.println(map.get("b"));            // null
        System.out.println(map.getOrDefault("b", -1)); // null (key exists!)
        System.out.println(map.getOrDefault("z", -1)); // -1
    }
}
```

**Senior takeaway:** `getOrDefault` does not distinguish "missing key" from "mapped to null" — use `containsKey` when null is a valid value.

---

## Exercise 7 — Streams: filter, map, collect

**Difficulty:** Basic

**Task:** From a list of names, print uppercase names longer than 3 characters, sorted.

**Solution:**

```java
import java.util.Comparator;
import java.util.List;

public class StreamBasics {
    public static void main(String[] args) {
        List<String> names = List.of("amy", "bob", "carol", "dan", "eve");

        List<String> result = names.stream()
                .filter(n -> n.length() > 3)
                .map(String::toUpperCase)
                .sorted(Comparator.naturalOrder())
                .toList();

        System.out.println(result); // [CAROL]
    }
}
```

**Senior takeaway:** Streams excel at declarative transforms; for tight primitive loops, a `for` may still win — measure with JMH before "optimizing."

---

## Exercise 8 — Optional: lazy vs eager defaults

**Difficulty:** Basic

**Task:** Show why `orElse` is dangerous with expensive defaults; fix with `orElseGet`.

**Solution:**

```java
import java.util.Optional;

public class OptionalBasics {
    static String expensiveDefault() {
        System.out.println("building default...");
        return "DEFAULT";
    }

    public static void main(String[] args) {
        Optional<String> present = Optional.of("ok");
        System.out.println(present.orElse(expensiveDefault()));       // prints building... even though value present
        System.out.println(present.orElseGet(expensiveDefault));      // no building...

        Optional<String> empty = Optional.empty();
        System.out.println(empty.orElseGet(expensiveDefault));        // builds only when empty
    }
}
```

**Senior takeaway:** Never chain `Optional.get()` in production; prefer `orElseGet`, `ifPresent`, or map to a result type.

---

## Exercise 9 — Immutability: `List.of` vs mutable lists

**Difficulty:** Basic

**Task:** Show that `List.of` rejects nulls and mutation; wrap a mutable list defensively.

**Solution:**

```java
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class ImmutabilityBasics {
    public static void main(String[] args) {
        List<String> immutable = List.of("a", "b");
        try {
            immutable.add("c");
        } catch (UnsupportedOperationException e) {
            System.out.println("List.of is immutable");
        }

        List<String> mutable = new ArrayList<>(List.of("x", "y"));
        mutable.add("z");
        System.out.println(mutable);

        List<String> view = Collections.unmodifiableList(mutable);
        try {
            view.add("w");
        } catch (UnsupportedOperationException e) {
            System.out.println("unmodifiable view blocks callers");
        }
        mutable.add("w"); // underlying list still mutable — shallow immutability
        System.out.println(view);
    }
}
```

**Senior takeaway:** `Collections.unmodifiable*` is a view, not a copy — expose `List.copyOf` or records for true defensive copies across API boundaries.

---

## Exercise 10 — JPMS: read `module-info.java`

**Difficulty:** Basic

**Task:** Create a two-module project (`app` requires `logging`). Run with module path.

**Solution:**

`logging/src/module-info.java`:

```java
module logging {
    exports logging;
}
```

`logging/src/logging/Logger.java`:

```java
package logging;

public final class Logger {
    public static void info(String msg) { System.out.println("[INFO] " + msg); }
}
```

`app/src/module-info.java`:

```java
module app {
    requires logging;
}
```

`app/src/app/Main.java`:

```java
package app;

import logging.Logger;

public class Main {
    public static void main(String[] args) {
        Logger.info("hello modules");
    }
}
```

Commands (from project root):

```bash
javac -d out/logging logging/src/module-info.java logging/src/logging/Logger.java
javac --module-path out/logging -d out/app app/src/module-info.java app/src/app/Main.java
java --module-path out/app:out/logging -m app/app.Main
```

Expected output: `[INFO] hello modules`

**Senior takeaway:** JPMS enforces boundaries at compile and runtime; split packages and illegal reflective access are common migration pain points.

---

# Part B — Intermediate

## Exercise 11 — equals/hashCode: lost HashMap keys

**Difficulty:** Intermediate

**Task:** Show why mutating a key after `put` makes `get` return null while `size` stays 1. Fix with a record.

**Solution:**

```java
import java.util.HashMap;
import java.util.Map;
import java.util.Objects;

public class MutableKeyDemo {
    static final class EmployeeKey {
        int id;
        String dept;

        EmployeeKey(int id, String dept) {
            this.id = id;
            this.dept = dept;
        }

        @Override
        public boolean equals(Object o) {
            if (this == o) return true;
            if (!(o instanceof EmployeeKey that)) return false;
            return id == that.id && Objects.equals(dept, that.dept);
        }

        @Override
        public int hashCode() {
            return Objects.hash(id, dept);
        }
    }

    public static void main(String[] args) {
        Map<EmployeeKey, String> map = new HashMap<>();
        EmployeeKey key = new EmployeeKey(1, "ENG");
        map.put(key, "Prashant");

        System.out.println("before mutate: " + map.get(key)); // Prashant
        key.dept = "SALES";
        System.out.println("after mutate: " + map.get(key));  // often null
        System.out.println("size: " + map.size());            // 1 — orphaned bucket

        record ImmutableKey(int id, String dept) {}
        Map<ImmutableKey, String> safe = new HashMap<>();
        safe.put(new ImmutableKey(1, "ENG"), "Prashant");
        System.out.println(safe.get(new ImmutableKey(1, "ENG"))); // Prashant
    }
}
```

**Senior takeaway:** JPA entities with generated IDs used as `HashMap` keys reproduce this bug — use business keys or internal IDs only after assignment.

---

## Exercise 12 — Bad `hashCode`: collision stress

**Difficulty:** Intermediate

**Task:** Insert 50k entries with constant `hashCode`, time it, then fix and compare.

**Solution:**

```java
import java.util.HashMap;
import java.util.Objects;

public class BadHash {
    record Collider(int id) {
        @Override
        public int hashCode() {
            return 42; // adversarial — all in one bucket
        }
    }

    record GoodKey(int id) {
        @Override
        public int hashCode() {
            return Objects.hash(id);
        }
    }

    static long bench(Runnable r) {
        long t0 = System.nanoTime();
        r.run();
        return System.nanoTime() - t0;
    }

    public static void main(String[] args) {
        long badNs = bench(() -> {
            var map = new HashMap<Collider, Integer>();
            for (int i = 0; i < 50_000; i++) map.put(new Collider(i), i);
        });
        long goodNs = bench(() -> {
            var map = new HashMap<GoodKey, Integer>();
            for (int i = 0; i < 50_000; i++) map.put(new GoodKey(i), i);
        });
        System.out.println("bad ns:  " + badNs);
        System.out.println("good ns: " + goodNs);
    }
}
```

**Senior takeaway:** After 8 collisions at capacity ≥ 64, HashMap treeifies bins — still O(log n) per op; never ship hand-rolled `hashCode` that ignores fields.

---

## Exercise 13 — Memory leak via static unbounded cache

**Difficulty:** Intermediate

**Task:** Simulate a leak, then bound with size + TTL (Caffeine or `LinkedHashMap`).

**Solution (JDK-only bounded LRU):**

```java
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.UUID;

public class CacheLeak {
    static final Map<String, byte[]> LEAK = new java.util.HashMap<>();

    static final Map<String, byte[]> BOUNDED = new LinkedHashMap<>(16, 0.75f, true) {
        @Override
        protected boolean removeEldestEntry(Map.Entry<String, byte[]> eldest) {
            return size() > 1_000;
        }
    };

    public static void main(String[] args) {
        for (int i = 0; i < 100_000; i++) {
            LEAK.put(UUID.randomUUID().toString(), new byte[10_000]);
            BOUNDED.put(UUID.randomUUID().toString(), new byte[10_000]);
        }
        System.out.println("LEAK size: " + LEAK.size());       // 100_000
        System.out.println("BOUNDED size: " + BOUNDED.size());   // 1_000
    }
}
```

Inspect with VisualVM: `LEAK` dominates heap; `BOUNDED` stays flat.

**Senior takeaway:** Static `Map` caches are the #1 accidental OOM in long-lived services — always cap entries, bytes, or TTL.

---

## Exercise 14 — Stream vs loop: allocation trade-off

**Difficulty:** Intermediate

**Task:** Sum 10k ints with a loop and with `IntStream`; compare allocations (JFR or `-XX:+PrintGC` on a larger run).

**Solution:**

```java
import java.util.Arrays;
import java.util.stream.IntStream;

public class StreamVsLoop {
    static final int N = 10_000_000;
    static final int[] data = IntStream.range(0, N).toArray();

    static int loopSum() {
        int s = 0;
        for (int v : data) s += v;
        return s;
    }

    static int streamSum() {
        return Arrays.stream(data).sum();
    }

    public static void main(String[] args) {
        long t0 = System.nanoTime();
        int a = loopSum();
        long t1 = System.nanoTime();
        int b = streamSum();
        long t2 = System.nanoTime();
        System.out.println("loop:   " + (t1 - t0) + " ns, sum=" + a);
        System.out.println("stream: " + (t2 - t1) + " ns, sum=" + b);
    }
}
```

For JMH: add `jmh-core` + annotation processor and benchmark `Mode.AverageTime`.

**Senior takeaway:** Primitive arrays favor loops; boxed `Stream<Integer>` allocates per element — profile before banning streams in business code.

---

## Exercise 15 — Classloader leak via static listener list

**Difficulty:** Intermediate

**Task:** Register plugins into a static list; explain why instances never GC. Fix with weak references or explicit unregister.

**Solution:**

```java
import java.lang.ref.WeakReference;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

public class ListenerLeak {
    static final List<Runnable> GLOBAL = new ArrayList<>();

    static class Plugin {
        byte[] payload = new byte[1_000_000];
        void registerBad() {
            GLOBAL.add(this::onEvent); // captures Plugin.this — leak
        }
        void onEvent() { }
    }

    // Fix sketch: store WeakReference<Plugin> and prune on register
    static final List<WeakReference<Plugin>> WEAK = new ArrayList<>();

    static void registerGood(Plugin p) {
        WEAK.add(new WeakReference<>(p));
        WEAK.removeIf(ref -> ref.get() == null);
    }

    public static void main(String[] args) {
        for (int i = 0; i < 100; i++) new Plugin().registerBad();
        System.out.println("GLOBAL listeners: " + GLOBAL.size()); // 100 — plugins pinned
    }
}
```

**Senior takeaway:** Hot-redeploy in Tomcat fails when plugin classloaders are pinned by static registries — always `remove()` in `close()` / `@PreDestroy`.

---

## Exercise 16 — Exception wrapping and cause chains

**Difficulty:** Intermediate

**Task:** Wrap a checked exception without losing the cause; log and unwrap correctly.

**Solution:**

```java
public class ExceptionChain {
    static void readFile() {
        try {
            throw new java.io.IOException("disk full");
        } catch (java.io.IOException e) {
            throw new RuntimeException("import failed", e); // preserve cause
        }
    }

    public static void main(String[] args) {
        try {
            readFile();
        } catch (RuntimeException e) {
            System.out.println("message: " + e.getMessage());
            System.out.println("cause:   " + e.getCause().getMessage());
            e.printStackTrace();
        }
    }
}
```

**Senior takeaway:** `throw new RuntimeException(e.getMessage())` without cause destroys RCA — always pass `e` as the second constructor arg.

---

## Exercise 17 — `ConcurrentModificationException` during iteration

**Difficulty:** Intermediate

**Task:** Trigger CME on a for-each; fix with iterator `remove` or `removeIf`.

**Solution:**

```java
import java.util.ArrayList;
import java.util.List;

public class CmeDemo {
    public static void main(String[] args) {
        List<Integer> nums = new ArrayList<>(List.of(1, 2, 3, 4, 5));

        try {
            for (int n : nums) {
                if (n % 2 == 0) nums.remove(Integer.valueOf(n)); // CME
            }
        } catch (java.util.ConcurrentModificationException e) {
            System.out.println("CME: " + e.getClass().getSimpleName());
        }

        nums = new ArrayList<>(List.of(1, 2, 3, 4, 5));
        nums.removeIf(n -> n % 2 == 0);
        System.out.println(nums); // [1, 3, 5]
    }
}
```

**Senior takeaway:** Structural changes during enhanced for-each are undefined — use `Iterator.remove`, `removeIf`, or copy-then-replace.

---

## Exercise 18 — `Collectors.groupingBy` with downstream collectors

**Difficulty:** Intermediate

**Task:** Group orders by status and sum amounts; handle empty groups.

**Solution:**

```java
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

public class GroupingDemo {
    record Order(String status, long cents) {}

    public static void main(String[] args) {
        List<Order> orders = List.of(
                new Order("NEW", 100),
                new Order("SHIPPED", 200),
                new Order("NEW", 50),
                new Order("CANCELLED", 75)
        );

        Map<String, Long> totals = orders.stream()
                .collect(Collectors.groupingBy(
                        Order::status,
                        Collectors.summingLong(Order::cents)
                ));

        System.out.println(totals); // {NEW=150, SHIPPED=200, CANCELLED=75}
    }
}
```

**Senior takeaway:** `groupingBy` without a downstream collector returns `List<T>` per key — specify `counting`, `summing`, or `mapping` for aggregation APIs.

---

## Exercise 19 — Read a GC log snippet

**Difficulty:** Intermediate

**Task:** Answer the four questions below from this G1 young pause.

```
[gc,start] GC(12) Pause Young (Normal) (G1 Evacuation Pause)
[gc] GC(12)  8192M->6124M(16384M)  245.221ms
```

**Solution (written answers):**

1. **Young or full?** Young (Normal) evacuation — not mixed/full.
2. **245ms vs 200ms p99 SLO?** Unacceptable for a synchronous request path; tail latency will breach SLO.
3. **Knobs:** Reduce allocation rate (biggest lever), `-XX:MaxGCPauseMillis` (soft goal), right-size heap, avoid humongous objects (> half region size).
4. **Collect next:** Allocation flame graph (async-profiler/JFR), humongous region stats, live-set after full GC, request correlation.

**Senior takeaway:** `8192M->6124M` on young GC implies massive short-lived allocation — fix the app before chasing GC flags.

---

## Exercise 20 — Safe publication without `volatile`

**Difficulty:** Intermediate

**Task:** Show unsafe publication of a holder; fix with `volatile`, `final` fields in immutable holder, or `AtomicReference`.

**Solution:**

```java
import java.util.concurrent.atomic.AtomicReference;

public class SafePublication {
    // BUG: reader may see default field values
    static Holder unsafe;

    static final class Holder {
        final int n;
        Holder(int n) { this.n = n; }
    }

    static volatile Holder safeVolatile;
    static final AtomicReference<Holder> safeAtomic = new AtomicReference<>();

    static void writerVolatile() {
        safeVolatile = new Holder(42);
    }

    static void writerAtomic() {
        safeAtomic.set(new Holder(42));
    }

    public static void main(String[] args) throws Exception {
        var t = new Thread(() -> {
            while (safeAtomic.get() == null) Thread.onSpinWait();
            if (safeAtomic.get().n != 42) throw new AssertionError("visibility bug");
            System.out.println("published ok: " + safeAtomic.get().n);
        });
        t.start();
        writerAtomic();
        t.join();
    }
}
```

**Senior takeaway:** DCL without `volatile` is broken; prefer immutable objects with final fields published via safe constructs.

---

# Part C — Hard (production scenarios)

## Exercise 21 — On-call: `OutOfMemoryError: Java heap space`

**Difficulty:** Hard

**Task:** Given `-Xmx512m` and a service that caches PDF renders, write the first 5 commands/steps you run and what you look for.

**Solution (runbook steps):**

```bash
# 1. Confirm process and flags
jcmd <pid> VM.flags
jcmd <pid> GC.heap_info

# 2. Heap dump (preferably live objects only)
jcmd <pid> GC.heap_dump /tmp/heap.hprof

# 3. Thread dump (rule out blocking vs leak)
jcmd <pid> Thread.print

# 4. Quick histogram without full MAT
jmap -histo:live <pid> | head -30

# 5. Correlate with recent deploy / traffic spike in metrics
```

Toy reproducer:

```java
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

public class HeapOom {
    static final Map<String, byte[]> CACHE = new HashMap<>();

    public static void main(String[] args) {
        while (true) {
            CACHE.put(UUID.randomUUID().toString(), new byte[5_000_000]);
        }
    }
}
```

Run: `java -Xmx64m HeapOom` → expect `OutOfMemoryError: Java heap space`. MAT dominator tree should show `byte[]` retained by `CACHE`.

**Senior takeaway:** OOM RCA order: dominator tree → who retains → which deploy introduced retention — not "just increase heap."

---

## Exercise 22 — On-call: G1 pause regression after deploy

**Difficulty:** Hard

**Task:** p99 latency jumped from 80ms to 400ms; GC log shows frequent young pauses > 200ms. List tuning changes in priority order and anti-patterns.

**Solution (priority order):**

1. **Stop the bleeding:** roll back if correlated with deploy.
2. **Reduce allocation:** find new JSON serialization, logging, or per-request `byte[]` buffers (flame graph).
3. **Heap sizing:** insufficient heap increases GC frequency — measure old-gen occupancy, not guess.
4. **Flags (after fixing allocation):** `-XX:MaxGCPauseMillis=200` (soft), consider `-XX:G1HeapRegionSize` if humongous objects appear in logs.
5. **Collector switch:** for large heaps + strict latency, evaluate ZGC/Shenandoah in staging.

Anti-patterns: raising heap without fixing leak; enabling aggressive `-XX:+AlwaysPreTouch` on tiny containers; tuning without before/after JFR.

**Senior takeaway:** G1 pause goals are hints, not contracts — allocation rate dominates; tune the app first.

---

## Exercise 23 — Metaspace OOM from dynamic proxies

**Difficulty:** Hard

**Task:** Explain why repeated `Proxy.newProxyInstance` in a loop can exhaust metaspace. Reproduce sketch and fix.

**Solution:**

```java
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;

public class MetaspaceProxy {
    interface Svc { String ping(); }

    public static void main(String[] args) {
        InvocationHandler h = (p, m, a) -> "ok";
        for (int i = 0; i < 1_000_000; i++) {
            Proxy.newProxyInstance(
                    Svc.class.getClassLoader(),
                    new Class<?>[]{Svc.class},
                    h
            );
            if (i % 100_000 == 0) System.out.println("created " + i);
        }
    }
}
```

Run with small metaspace: `java -XX:MaxMetaspaceSize=32m MetaspaceProxy`

Expected: `OutOfMemoryError: Metaspace`

Fix: cache proxy classes per interface/handler signature; avoid generating unique proxy classes per request.

**Senior takeaway:** Metaspace leaks look like classloader leaks — each redeploy + reflective codegen can pin thousands of classes.

---

## Exercise 24 — Tomcat redeploy: classloader leak RCA

**Difficulty:** Hard

**Task:** After 50 redeploys, permgen/metaspace grows. Write a checklist of common retainers and how to find them in a heap dump.

**Solution (checklist + code smell):**

| Retainer | Symptom in dump | Fix |
|----------|-----------------|-----|
| Static `Map` of listeners | Old `WebappClassLoader` dominator | `remove` in `@PreDestroy` |
| JDBC driver registered | `DriverManager` holds loader | `deregisterDriver` on shutdown |
| `Thread` started by app | Thread still RUNNABLE | Shutdown hook / `contextDestroyed` |
| `java.beans.Introspector` cache | BeanInfo from old loader | `Introspector.flushCaches()` |

Code smell (from Exercise 15):

```java
static final List<Runnable> CALLBACKS = new ArrayList<>();
void onDeploy() { CALLBACKS.add(this::handle); } // pins WebappClassLoader
```

**Senior takeaway:** "Restart fixes it" means something is pinned — find the path from GC root to dead classloader.

---

## Exercise 25 — LRU cache: design for production

**Difficulty:** Hard

**Task:** Implement LRU with `LinkedHashMap`, explain why it is not thread-safe, and describe the production replacement.

**Solution:**

```java
import java.util.LinkedHashMap;
import java.util.Map;

public class Lru<K, V> extends LinkedHashMap<K, V> {
    private final int cap;

    public Lru(int cap) {
        super(cap, 0.75f, true); // accessOrder = true
        this.cap = cap;
    }

    @Override
    protected boolean removeEldestEntry(Map.Entry<K, V> eldest) {
        return size() > cap;
    }

    public static void main(String[] args) {
        var lru = new Lru<Integer, String>(2);
        lru.put(1, "a");
        lru.put(2, "b");
        lru.get(1);       // mark 1 recently used
        lru.put(3, "c");  // evicts 2
        System.out.println(lru); // {1=a, 3=c}
    }
}
```

Production: Caffeine with `maximumSize`, `expireAfterWrite`, and W-TinyLFU eviction. Concurrent access: single Caffeine instance (thread-safe) or `LinkedHashMap` + `ReentrantReadWriteLock` if rolling your own.

**Senior takeaway:** Interview LRU proves you know `removeEldestEntry`; production needs concurrency, statistics, and async refresh.

---

## Exercise 26 — JPMS incident: `IllegalAccessError` at runtime

**Difficulty:** Hard

**Task:** App runs on classpath in IDE but fails on module path with illegal deep reflection. Diagnose and fix.

**Solution:**

Symptom:

```
java.lang.IllegalAccessError: class app.Main cannot access class com.fasterxml.jackson.databind.ObjectMapper
```

Root cause: Jackson internal packages not exported to `app`; or `--add-opens` missing for framework reflection.

Fix options:

1. Stay on classpath (not ideal long-term).
2. Add `requires com.fasterxml.jackson.databind;` and use public API only.
3. For frameworks (Hibernate, Spring): add JVM args documented by the framework:

```bash
java --add-opens java.base/java.lang=ALL-UNNAMED \
     --add-modules ALL-SYSTEM \
     -m app/app.Main
```

**Senior takeaway:** Modular JARs fail at runtime when libraries use deep reflection — treat `--add-opens` as a migration bridge, not architecture.

---

## Exercise 27 — G1 humongous object allocation spike

**Difficulty:** Hard

**Task:** A service allocates 3MB `byte[]` per request; heap is 8GB, region size 4MB. Explain GC impact and mitigation.

**Solution:**

Analysis:
- Objects > 50% of region size are **humongous** — allocated in separate regions, often not efficiently collected in young GC.
- 3MB arrays with 4MB regions → humongous → fragment old gen, increase full GC pressure.
- Logs may show `Humongous regions: X->Y`.

Mitigations:
1. Stream processing / chunking — avoid single giant arrays.
2. Increase region size (`-XX:G1HeapRegionSize=8m`) only after measuring — trade-off with waste.
3. Pool buffers with bounded size (careful with thread safety).
4. Consider off-heap / direct buffers for I/O with explicit lifecycle.

Repro sketch:

```java
public class Humongous {
    public static void main(String[] args) {
        java.util.List<byte[]> keep = new java.util.ArrayList<>();
        for (int i = 0; i < 200; i++) {
            keep.add(new byte[3 * 1024 * 1024]); // 3 MiB each
        }
        System.out.println("allocated " + keep.size() + " humongous-ish arrays");
    }
}
```

Run with `-Xlog:gc* -XX:G1HeapRegionSize=4m` and observe humongous region mentions.

**Senior takeaway:** "We increased heap but GC got worse" often means humongous allocations — fix object sizing, not only `-Xmx`.

---

## Exercise 28 — JPA `equals`/`hashCode` production bug

**Difficulty:** Hard

**Task:** Entity uses database ID in `equals`/`hashCode` but ID is 0 before persist. Show duplicate Set entries and fix.

**Solution:**

```java
import java.util.HashSet;
import java.util.Objects;
import java.util.Set;

public class JpaEqualsBug {
    static class Order {
        Long id; // null/0 before flush
        String sku;

        Order(String sku) { this.sku = sku; }

        @Override
        public boolean equals(Object o) {
            if (this == o) return true;
            if (!(o instanceof Order that)) return false;
            return Objects.equals(id, that.id); // BUG: both null id → equal
        }

        @Override
        public int hashCode() {
            return Objects.hash(id); // all hash to 0
        }
    }

    static class FixedOrder {
        Long id;
        String sku;

        FixedOrder(String sku) { this.sku = sku; }

        @Override
        public boolean equals(Object o) {
            if (this == o) return true;
            if (!(o instanceof FixedOrder that)) return false;
            if (id != null && that.id != null) return id.equals(that.id);
            return Objects.equals(sku, that.sku); // business key when transient
        }

        @Override
        public int hashCode() {
            return id != null ? Objects.hash(id) : Objects.hash(sku);
        }
    }

    public static void main(String[] args) {
        Set<Order> bad = new HashSet<>();
        bad.add(new Order("ABC"));
        bad.add(new Order("ABC"));
        System.out.println("buggy set size: " + bad.size()); // 1 — collapsed distinct transients

        Set<FixedOrder> good = new HashSet<>();
        good.add(new FixedOrder("ABC"));
        good.add(new FixedOrder("ABC"));
        System.out.println("fixed set size: " + good.size()); // 1 correctly (same sku)
    }
}
```

**Senior takeaway:** Hibernate identity vs business equality — use `@Id` only after assignment, or stable business keys in `equals`/`hashCode` for transient entities.

---

# Part D — Deep-dive (Q51–Q85)

## Exercise 29 — `CompletableFuture` composition

**Difficulty:** Basic

**Task:** Chain two async calls: fetch customer ID, then fetch orders. Use `thenCompose`. Handle failure with `exceptionally`.

**Solution:**

```java
CompletableFuture<String> customerId = CompletableFuture.supplyAsync(() -> lookupCustomerId("prashant@corp.com"));
CompletableFuture<List<String>> orders = customerId.thenCompose(id ->
        CompletableFuture.supplyAsync(() -> fetchOrders(id)));
String result = orders.exceptionally(ex -> List.of("ERROR:" + ex.getMessage())).join();
System.out.println(result);
```

**Senior takeaway:** `thenCompose` for dependent async steps; never block on `.get()` without timeout in request threads — use virtual threads or reactive stack.

---

## Exercise 30 — `ThreadPoolExecutor` sizing

**Difficulty:** Intermediate

**Task:** Given 200ms average HTTP latency, 50 concurrent users, 8 cores — compute pool size using `N = U * (1 + W/C)` with U=0.8, W/C=25. Configure a bounded queue.

**Solution:**

```java
int cores = 8;
double utilization = 0.8;
double waitToCompute = 25.0; // 200ms wait / 8ms compute (example)
int poolSize = (int) Math.ceil(cores * utilization * (1 + waitToCompute));
ExecutorService pool = new ThreadPoolExecutor(
        poolSize, poolSize, 60, TimeUnit.SECONDS,
        new ArrayBlockingQueue<>(100),
        new ThreadPoolExecutor.CallerRunsPolicy());
```

**Senior takeaway:** Unbounded queues hide overload — pair pool metrics with queue depth alerts; CallerRunsPolicy applies backpressure.

---

## Exercise 31 — NIO.2 file walk and filter

**Difficulty:** Intermediate

**Task:** List all `.log` files under `/var/log` modified in the last 24 hours using `Files.walk` and `BasicFileAttributes`.

**Solution:**

```java
Instant cutoff = Instant.now().minus(Duration.ofHours(24));
try (var stream = Files.walk(Path.of("/var/log"))) {
    stream.filter(Files::isRegularFile)
          .filter(p -> p.toString().endsWith(".log"))
          .filter(p -> {
              try {
                  return Files.getLastModifiedTime(p).toInstant().isAfter(cutoff);
              } catch (IOException e) { return false; }
          })
          .forEach(System.out::println);
}
```

**Senior takeaway:** Always use try-with-resources on `Stream<Path>` from `Files.walk` — leaking streams holds directory handles open.

---

## Exercise 32 — JFR pinning event analysis

**Difficulty:** Hard

**Task:** Start a JVM with `-XX:StartFlightRecording=filename=rec.jfr,settings=profile`. Run code that pins a virtual thread on `synchronized`. List pinning events with `jfr print`.

**Solution:**

```bash
java -XX:StartFlightRecording=filename=rec.jfr,settings=profile -jar app.jar
# after load:
jfr print --events jdk.VirtualThreadPinned rec.jfr | head -20
```

```java
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    executor.submit(() -> {
        synchronized (LOCK) { Thread.sleep(100); } // pins carrier
    }).get();
}
```

**Senior takeaway:** Pinning shows up in JFR before thread dumps; fix with `ReentrantLock` or move blocking work off pinned sections.

---

## Exercise 33 — Heap dump dominator tree (MAT workflow)

**Difficulty:** Hard

**Task:** Simulate a leak with a static `Map` holding 10k byte arrays. Take heap dump. Write the MAT steps to find the dominator path.

**Solution:**

```java
static final Map<String, byte[]> LEAK = new HashMap<>();
public static void main(String[] args) {
    for (int i = 0; i < 10_000; i++) LEAK.put("k" + i, new byte[100_000]);
    Thread.sleep(Long.MAX_VALUE); // jcmd dump while running
}
```

```bash
jcmd <pid> GC.heap_dump /tmp/leak.hprof
```

MAT steps: Open dump → **Leak Suspects** → **Dominator Tree** → sort by retained heap → follow path to `LEAK` static field → OQL: `SELECT * FROM java.util.HashMap m WHERE m.@objectId = <id>`.

**Senior takeaway:** Dominator tree answers "what is keeping this alive?" — faster than browsing all `byte[]` instances in a 4GB heap.

---

## Weekend challenge

1. Generate a heap dump from Exercise 13 (`jcmd <pid> GC.heap_dump`) and find the dominator path to `byte[]` in Eclipse MAT.
2. Run Exercise 10 modules project and break it by removing `exports` — document the exact compiler error.
3. Audit one real service: list every `equals`/`hashCode`, static cache, and `Optional.get()` — file issues for any smell.
