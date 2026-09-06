# Java Core & J2EE — 50 Senior Interview Questions

**Bar:** Internals, cost model, and production judgment. If you only recite APIs, you fail a 10-year loop.

---

### 1. Explain the JVM memory layout in a modern HotSpot JVM (Java 17+).

**Short answer:**
A HotSpot process splits memory into the Java heap (young + old, region-based under G1/ZGC), Metaspace for class metadata, Code Cache for JIT, per-thread stacks, and native/direct memory outside the heap. RSS can exceed heap when direct buffers, Metaspace, or thread stacks grow unchecked. RSS often exceeds `-Xmx` because Metaspace, Code Cache, thread stacks, and direct buffers live outside the heap. G1 and ZGC use regions — young/old ratio knobs from the CMS era do not apply the same way.

#### What it is
The JVM memory model is not 'one big heap.' The heap holds object instances; since Java 7 the string pool lives on the heap too. Metaspace (native, unbounded by default) replaced PermGen for class metadata. Code Cache stores compiled machine code. Each platform thread has a stack (`-Xss`). Direct `ByteBuffer` and JNI allocations sit in native memory and do not count toward `-Xmx`.

#### How it works (internals)
G1 and ZGC organize the heap into regions rather than a rigid contiguous young/old split. Young collections copy survivors; old collections mark/sweep or compact concurrently depending on the collector. Compressed oops (`-XX:+UseCompressedOops`) shrink object headers on 64-bit JVMs. `-XX:MaxMetaspaceSize` caps class metadata growth. Thread stacks multiply: 1 MB default × thousands of platform threads is a real OOM vector.

#### When to use / when NOT to use
Know this layout when tuning Kubernetes pods, diagnosing OOMKilled, or explaining why 'heap is 4 GB but RSS is 8 GB.' Use Metaspace caps in long-lived services with dynamic class loading. Monitor direct memory for Netty/gRPC services. Set Metaspace and direct-memory caps on long-lived Spring Boot pods with dynamic class loading or gRPC clients.

#### Production example
A payment gateway on G1 with 8 GB heap shows healthy GC but pod RSS climbs to 12 GB. Heap dump shows modest objects; `jcmd VM.native_memory summary` reveals direct buffer growth from an HTTP client that never releases pooled buffers. Fix: bound buffer pools; set `-XX:MaxDirectMemorySize`.

#### Common mistakes
Tuning only `-Xmx` while ignoring Metaspace and direct memory. Assuming young/old ratio knobs from CMS era apply to G1. Creating unbounded platform thread pools without counting stack memory.

#### Interview follow-ups (with model answers)

**Q:** What is the difference between heap OOM and Metaspace OOM?
**A:** Heap OOM means no contiguous space for new object allocations — often a leak, undersized heap, or humongous objects in G1. Metaspace OOM means class metadata cannot grow — typical after repeated hot deploys, Groovy/bytecode generation, or unbounded dynamic proxies. Heap dumps show dominator trees of objects; Metaspace issues need `jmap -clstats` or NMT. Fixes differ: heap tuning or leak fix vs clearing classloader roots or capping/codegen audit. In Spring Boot fat jars, Metaspace grows slowly with CGLIB proxies — set `-XX:MaxMetaspaceSize` in prod to fail fast instead of slow RSS creep.

**Q:** How do humongous objects work in G1?
**A:** Objects larger than half a G1 region (default region size scales with heap) are allocated in humongous regions spanning multiple contiguous regions. They bypass normal young-gen copying and can trigger expensive concurrent marking if many accumulate. Kafka consumers deserializing large byte arrays or ORMs hydrating wide graphs are common sources. Mitigation: stream processing, smaller DTOs, increase region size deliberately after measurement, or reduce allocation rate. Humongous objects are a frequent cause of 'heap looks fine but GC pauses spike' in analytics services.

**Q:** Why does RSS not drop immediately after a full GC?
**A:** The JVM often retains freed heap pages from the OS allocator — `MADV_DONTNEED` behavior varies by glibc and `-XX:+AlwaysPreTouch`. Native memory (direct buffers, Metaspace, thread stacks) is unaffected by heap GC. Container RSS includes memory the JVM holds for future allocations to avoid syscall cost. Use NMT and OS-level metrics together; do not expect RSS to track heap used 1:1. After incidents, restart may be the only way to return memory to the OS quickly on some JDK/glibc combinations.

#### Scenario probe

Your Spring Boot payment service runs fine in staging with 2 GB heap. In production on Kubernetes, pods get OOMKilled at 4 GB limit while JVM metrics show only 2.5 GB heap used. Thread dump shows 3,000 platform threads.

This is classic off-heap and stack memory underestimation. Calculate: 3,000 threads × 1 MB default stack ≈ 3 GB before Metaspace and direct memory. Staging likely has lower concurrency. Enable virtual threads (Boot 3.2+) or reduce Tomcat `maxThreads`, set `-Xss256k` only after measurement, cap `-XX:MaxDirectMemorySize`, and raise pod memory limit with evidence from `jcmd VM.native_memory summary`. Do not only increase `-Xmx` — that worsens the problem.

#### Code / config (when useful)
```text
# Typical production flags (starting point — measure first)
-XX:+UseG1GC
-Xms4g -Xmx4g
-XX:MaxMetaspaceSize=256m
-XX:MaxDirectMemorySize=512m
-Xlog:gc*:file=gc.log:time,uptime:filecount=5,filesize=20M
```

---

### 2. How does garbage collection actually reclaim an object?

**Short answer:**
GC reclaims objects unreachable from GC roots (stack locals, static fields, JNI handles, active threads). The collector does not free on reference count; it traces the object graph, then copies (young) or marks-sweeps/compacts (old). `finalize()` and `Cleaner` run only after unreachable — never rely on them for correctness.

#### What it is
Garbage collection answers: 'Is any live thread or root still holding a reference?' Roots include JVM stacks, statics, monitor registers, and JNI global refs. Once unreachable, the object is a collection candidate — not necessarily freed immediately. GC roots include stack locals, static fields, JNI handles, and active thread references.

#### How it works (internals)
Young GC (minor) typically copies live objects from Eden to Survivor spaces, aging them toward the old generation. Old GC marks live objects, sweeps dead ones, and may compact to fight fragmentation. Reference types matter: strong refs prevent collection; soft refs survive until memory pressure; weak refs for canonical maps; phantom refs pair with `Cleaner` for native resource release.

#### When to use / when NOT to use
Design caches with explicit bounds (Caffeine size + TTL) rather than hoping GC will save you. Use soft references only when you understand eviction under pressure. Prefer try-with-resources over finalizers.

#### Production example
An order service caches customer profiles in a static `HashMap` with strong references. Old gen grows monotonically; full GC pauses spike. Replacing with Caffeine `maximumSize(10_000).expireAfterWrite(1h)` lets entries evict predictably; GC reclaims unused entries.

#### Common mistakes
Believing 'setting a field to null helps GC' in hot loops (usually noise). Using finalizers for socket/file cleanup. Holding references in static collections 'just in case.'

#### Interview follow-ups (with model answers)

**Q:** What are GC roots in a heap dump?
**A:** GC roots are the entry points the collector traces from: local variables on thread stacks, static fields, JNI global references, objects used as synchronization monitors, and JVM internal tables. In Eclipse MAT, dominator tree and 'Path to GC roots' explain why an object is still live. Production leaks often show a `ThreadLocal` or static `ConcurrentHashMap` as the root holding finished request context. Knowing roots separates 'memory leak' from 'legitimate cache' and guides whether to fix code or tune eviction. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** When does an object move from young to old gen?
**A:** After surviving enough minor collections — typically when tenuring threshold is met or Survivor space is full. Large objects may go directly to old gen. Allocation rate and survivor sizing matter: if minor GC is too infrequent, a burst of short-lived objects can promote unnecessarily. `-XX:+PrintTenuringDistribution` (or JFR) shows ages. In services with request-scoped garbage, tuning survivor ratio reduces premature promotion that fills old gen and triggers costly mixed collections. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** How does `System.gc()` behave in production?
**A:** It is a hint — HotSpot may run a full GC but is not required to. Many teams set `-XX:+DisableExplicitGC` because libraries call `System.gc()` (RMI, some JDBC drivers), causing surprise STW pauses. ZGC and G1 may ignore or partially honor it. Never call it in application code for 'cleanup.' If you see explicit GC in logs, find the caller. For direct buffer cleanup, prefer bounded pools and `MaxDirectMemorySize` over forcing GC. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

After a Black Friday deploy, your Kafka consumer lag is fine but old-gen heap climbs 200 MB per hour until full GC pauses hit 3 seconds. Heap dump shows millions of `CustomerProfile` instances.

Trace GC roots: likely a static cache or `ThreadLocal` in a `@Component` holding profiles after message processing. Caffeine or bounded cache with TTL fixes retention; verify listeners clear context in `finally`. Check whether error handlers stash the payload in a static retry map. GC tuning cannot fix a leak — prove reachability first, then fix the root reference. Add heap-after-full-GC metric alert.

---

### 3. Compare Serial, Parallel, G1, ZGC, and Shenandoah. When do you pick each?

**Short answer:**
Serial is single-threaded STW for tiny heaps. Parallel maximizes throughput with multi-thread STW. G1 is the JDK 9+ default with pause goals on regions. ZGC and Shenandoah target sub-millisecond to low-millisecond pauses on large heaps at the cost of more CPU and barriers. Pick from metrics, not blog posts.

#### What it is
Garbage collectors trade throughput, pause time, and memory overhead differently. Serial/Parallel are generational stop-the-world collectors. G1 divides the heap into regions and collects incrementally toward a pause target. ZGC and Shenandoah relocate objects concurrently with colored pointers or Brooks pointers.

#### How it works (internals)
Serial: one GC thread, minimal footprint — sidecar containers with one CPU. Parallel (`-XX:+UseParallelGC`): batch jobs where pauses are acceptable. G1: general-purpose services, default for most Spring Boot apps. ZGC/Shenandoah: latency-sensitive services with multi-GB heaps and strict p99 pause SLOs. All require GC logging and load testing before switching.

#### When to use / when NOT to use
Start with G1 unless you have measured pause problems or very large heaps. Move to ZGC when p99 GC pause drives SLA breaches. Avoid exotic collectors on tiny heaps — overhead dominates.

#### Production example
A trading analytics service on 32 GB heap sees G1 p99 pauses of 80 ms during market open. After enabling ZGC (`-XX:+UseZGC`) and load testing, p99 drops to 2 ms; CPU rises 8%. The team documents the trade-off and keeps G1 on low-traffic admin services.

#### Common mistakes
Switching collectors without baseline GC logs. Ignoring humongous allocations in G1. Expecting ZGC to fix allocation leaks.

#### Interview follow-ups (with model answers)

**Q:** What JVM flags tune G1 pause goals?
**A:** `-XX:MaxGCPauseMillis` sets the soft pause target (default 200 ms). `-XX:G1HeapRegionSize` affects humongous thresholds. `-XX:InitiatingHeapOccupancyPercent` controls when concurrent marking starts. `-XX:G1ReservePercent` reserves space for evacuation. Pair with `-Xlog:gc*` and JFR `jdk.GCPhasePause`. Tuning without logs is guesswork. For Kafka consumers, correlate `max.poll.interval.ms` with worst-case pause plus processing time — GC flags alone cannot fix poll timeouts. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** How do you read `-Xlog:gc*` output?
**A:** Look for pause type (Young, Mixed, Full), duration, heap before/after, and cause. Mixed collections indicate old-gen reclamation. Long pauses with small reclaimed bytes suggest remark or humongous issues, not 'need more heap.' Compare p50/p99 across deploys. Tools like GCeasy or GCEraser help at scale. In incidents, align GC timestamps with Kafka rebalance or HTTP timeout logs — often the smoking gun. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** When is Parallel GC still appropriate?
**A:** Batch ETL, offline report generation, and single-tenant jobs where throughput beats tail latency. Small heaps on constrained CI runners. Some data pipelines prefer Parallel over G1 when pauses are acceptable and total wall-clock time matters. Do not use on latency-sensitive APIs without measuring. JDK 17+ defaults to G1 — switching to Parallel is a deliberate regression in pause profile for throughput wins. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Your Spring Boot checkout API on JDK 17 defaults to G1 with 4 GB heap. P99 latency SLO is 50 ms but metrics show 120 ms spikes every few minutes correlated with GC. Product refuses a larger heap.

Pull `-Xlog:gc*` and JFR GC phases — if spikes are young GC under 30 ms, the problem may be allocation rate or safepoint TTSP, not collector choice. If mixed/remark pauses dominate, tune IHOP, reduce humongous allocations, or trial ZGC on canary pods. Measure CPU headroom before ZGC. Also audit JDBC result set sizes and JSON serialization — allocation pressure often beats collector tuning. Document before/after with identical load test.

#### Code / config (when useful)
```text
| Collector    | Pause model              | Typical use              |
|--------------|--------------------------|--------------------------|
| Serial       | STW, single thread       | 1 CPU, small heap        |
| Parallel     | STW, multi-thread        | Batch, throughput        |
| G1           | Region-based, goal pauses| Default services         |
| ZGC          | Concurrent, low pause    | Large heap, tight SLO    |
| Shenandoah   | Concurrent compact       | Similar to ZGC           |
```

---

### 4. What is a safepoint and why do "GC pauses" sometimes include non-GC time?

**Short answer:**
A safepoint is when all mutator threads reach a known state so the VM can run GC, deoptimization, biased-lock revocation, or thread dumps. Long 'GC pauses' often include time-to-safepoint (TTSP) when threads are stuck in counted loops or JNI — not actual collection work. Safepoints let the VM stop mutators for GC roots, deoptimization, and biased-lock revocation. Long 'GC pauses' may be time-to-safepoint (TTSP) while one thread spins in a counted loop.

#### What it is
Safepoints coordinate the JVM with running application threads. At poll sites (loop back-edges, method returns), threads check whether a safepoint is requested and park if needed. Threads poll at loop back-edges and method returns; if a thread never polls, others wait.

#### How it works (internals)
Operations that need a consistent view of thread stacks — GC roots, deopt, some JVMTI events — require safepoints. If a thread runs a tight loop without polls or blocks in native code, other threads wait at the safepoint, inflating pause time. GC logs may show `ttsp` separately from actual GC duration.

#### When to use / when NOT to use
Diagnose safepoint issues when GC logs show huge pauses but little collection work, or when `jcmd Thread.print` hangs. Fix hot loops, reduce JNI time, or upgrade JDK (biased locking changes over versions). Investigate safepoints when GC logs show huge pauses but tiny collection work.

#### Production example
A metrics aggregator shows 200 ms 'GC' pauses every minute but young-gen collections are tiny. `-Xlog:safepoint` reveals 180 ms TTSP while one thread spins in a `while(true)` busy loop without safepoint polls. Refactoring to `Thread.onSpinWait()` with periodic checks or restructuring the loop fixes tail latency.

#### Common mistakes
Blaming the garbage collector for all STW time. Ignoring safepoint logs. Running heavy work in `<clinit>` or static init that blocks class loading.

#### Interview follow-ups (with model answers)

**Q:** What is `-XX:+UnlockDiagnosticVMOptions -XX:+LogVMOutput` used for?
**A:** Diagnostic VM logging prints low-level safepoint, compilation, and VM operation details to `hotspot_pid.log`. Useful in expert escalations when standard GC logs are insufficient. Heavy overhead — never leave on in prod continuously. Often combined with `-XX:LogFile` and specific `Trace*` flags. Prefer JFR `jdk.SafepointBegin`/`jdk.SafepointState` for lighter production capture. Know it exists; reach for it when TTSP is suspected and JFR is inconclusive. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** How does JNI affect safepoints?
**A:** Threads in native code cannot poll safepoints until they return to Java. Long JNI calls (compression, crypto, some drivers) delay safepoint synchronization — all mutators may wait at the next global safepoint. This looks like a GC pause in coarse metrics. Fix: shorten native work, move off hot paths, or use async APIs. With virtual threads, pinning during synchronized JNI magnifies carrier starvation — another reason to prefer `ReentrantLock` in blocking I/O paths on Loom. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Difference between cooperative and forced safepoint?
**A:** Cooperative safepoints rely on threads polling and parking voluntarily. If a thread is stuck, the VM may eventually force a safepoint via mechanisms that interrupt execution — slower and noisier. Forced safepoints show up as long TTSP in logs. Production goal: all threads reach safepoints quickly via normal polls. Chronic forced safepoints indicate bug-level loops or blocking native code. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Production APM blames 'GC pause' for 300 ms stalls every 30 seconds on a pricing engine. GC logs show young GC taking 5 ms. One CPU core pinned at 100% on each pod.

Enable `-Xlog:safepoint` and thread profiling — likely TTSP from a spin loop in a price refresh thread or custom lock-free structure without safepoint polls. Refactor to `Thread.sleep`/`onSpinWait` with backoff, or move refresh to scheduled executor. Do not tune G1 further. Add JFR safepoint events to continuous profiling. This pattern fools teams into heap tuning for weeks.

---

### 5. Explain JIT: interpreter, C1, C2, and tiered compilation.

**Short answer:**
Bytecode starts in the interpreter. Hot methods compile with C1 (fast, light optimizations) then C2 (aggressive inlining, escape analysis). Tiered compilation uses both. Deoptimization returns to interpreter when speculative assumptions fail. Cold pods have worse latency until warmup.

#### What it is
The JIT (Just-In-Time) compiler turns hot bytecode into native machine code. The interpreter handles cold code cheaply; compilation cost is amortized over many invocations. C1 compiles fast with light opts; C2 does inlining, escape analysis, and lock elision.

#### How it works (internals)
C1 compiles quickly with basic optimizations. C2 spends more compile time on inlining, loop unrolling, escape analysis, and lock elision. Tiered mode (`-XX:+TieredCompilation`, default) escalates hot methods through tiers. Uncommon traps deoptimize when class hierarchy changes or a null appears where C2 assumed non-null. CDS and AOT/native-image attack cold-start; microbenchmarks need JMH with warmup.

#### When to use / when NOT to use
Expect warmup after deploy or scale-out. Use JMH for performance claims. Do not disable tiered compilation without measurement.

#### Production example
After a blue-green deploy, p99 latency on checkout is 3× higher for ten minutes. JFR shows heavy interpreter time until C2 compiles `PricingEngine.applyDiscounts`. The team adds a readiness probe that runs synthetic pricing requests before marking pods ready.

#### Common mistakes
Microbenchmarking without warmup. Assuming `-client` vs `-server` still exists (removed). Disabling C2 globally to 'reduce CPU' and killing throughput.

#### Interview follow-ups (with model answers)

**Q:** What is escape analysis?
**A:** C2 analyzes whether object references escape their allocating method or thread. Non-escaping objects may be scalar-replaced (no heap allocation), and locks on them elided. Critical for understanding why microbenchmarks differ from prod — logging or storing objects in fields defeats escape. See question 6 for depth. In JFR, look for low allocation rate in hot methods after warmup. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** How does deoptimization show up in JFR?
**A:** JFR events `jdk.Deoptimization` and `jdk.Compilation` show when optimized code is invalidated and interpreter re-enters. Common triggers: class loading changing CHA assumptions, uncommon null, or OSR (on-stack replacement) failures. Spikes after deploy correlate with new code paths. If deopt rate stays high, investigate megamorphic call sites or unstable class hierarchies — fix design, not `-XX:CompileThreshold` first. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** What is Graal JIT vs C2?
**A:** Graal is an alternative optimizing compiler (used in GraalVM native-image and some JDK builds). Standard HotSpot on Oracle/OpenJDK JDK 17 uses C2 for peak performance. Graal may compile faster with different inlining heuristics — workload-dependent. For typical Spring Boot on Temurin 17, C2 remains default. Graal matters for native-image AOT, not routine monolith tuning. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

You scale checkout from 10 to 50 pods during a sale. New pods show 400 ms p99 for the first 8 minutes while old pods stay at 80 ms. CPU is low; GC is quiet.

Classic JIT cold start — interpreter and C1 until hot methods compile. Add readiness gate executing representative checkout flows (pricing, tax, fraud checks) until p99 stabilizes. Consider CDS (`-XX:SharedArchiveFile`) for faster class load, and avoid massive per-deploy classpath churn. Do not mark pods ready on TCP health alone. Compare JFR `jdk.ExecutionSample` interpreter vs compiled ratio on new pods.

---

### 6. What does escape analysis buy you?

**Short answer:**
If the compiler proves an object never escapes a method or thread, C2 can scalar-replace it (no heap allocation), eliminate locks on that object, and stack-allocate fields. Tiny helper objects in hot loops are often free — until they escape via fields, callbacks, or non-inlined calls. Escape analysis lets C2 eliminate allocations and locks when objects stay method-local. Defeating inlining — logging lambdas, virtual calls, or storing in fields — brings allocations back.

#### What it is
Escape analysis is a JIT optimization that tracks whether object references leave their allocating scope. The compiler tracks whether references escape via return, fields, or unknown callbacks. Scalar replacement stores fields in registers/stack slots instead of heap objects.

#### How it works (internals)
No escape means the object is thread-local and method-local. C2 may remove the allocation entirely, storing fields in registers or stack slots. Synchronized blocks on non-escaping objects can be elided. Once the reference is stored in a field, passed to unknown code, or returned, escape analysis fails and real heap allocation occurs.

#### When to use / when NOT to use
Write clear hot paths; let the JIT optimize. Do not micro-manage allocations unless profiling shows allocation pressure. Avoid defeating inlining with huge methods or virtual calls in inner loops.

#### Production example
A serialization hot path allocates a small `StringBuilder` wrapper per field. Profiler shows zero allocation after C2 warms — scalar replacement. Adding logging that captures the wrapper in a lambda forces escape; allocations return and throughput drops 15%.

#### Common mistakes
Assuming 'new is always expensive.' Creating objects in hot paths 'to help GC' with pooling when escape analysis already eliminates them. Defeating inlining and blaming the GC. Object pools for tiny short-lived helpers 'because allocation is slow' — often slower than elision.

#### Interview follow-ups (with model answers)

**Q:** How do you see eliminated allocations in JFR?
**A:** Compare `jdk.ObjectAllocationInNewTLAB` and `jdk.ObjectAllocationOutsideTLAB` before and after warmup on the same workload. If allocation rate drops while throughput rises, C2 likely elided allocations. `-XX:+PrintCompilation` with `-XX:+UnlockDiagnosticVMOptions` can show escape analysis decisions in debug builds. Production: JFR is the practical tool. Zero-allocation hot loops after warmup are a sign escape analysis is working. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Does escape analysis work with virtual threads?
**A:** Yes — escape analysis is per compiled method, independent of thread type. Virtual threads change scheduling, not JIT optimizations. Pinning can block carriers but does not disable escape analysis. Allocation pressure from millions of short-lived virtual thread stacks is a separate concern — carriers still run compiled code. Profile mounted vs unmounted time separately from allocation metrics. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Relation to lock elision?
**A:** If escape analysis proves a lock object is thread-local and non-escaping, the JIT may remove lock acquire/release entirely. Biased locking removal in newer JDKs shifts some behavior, but elision still applies to non-escaping locks. Defeating escape — storing locked object in a field — restores real locking cost. Contended locks on shared objects never elide. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Your team pools 10,000 `ParseContext` objects in a Kafka deserialization path to 'reduce GC.' After pooling, throughput is worse and CPU is higher.

Measure allocations with JFR — likely C2 already scalar-replaced `ParseContext` when pooling was added, defeat inlining with pool synchronization, and add contention. Remove pool, restore simple stack allocation, keep hot parser method small. Re-profile: if allocations return, check whether polymorphic deserializers or logging captures references. Pool only when profiling proves long-lived reuse beats allocation on old gen.

---

### 7. `==` vs `equals` vs `hashCode` — the contract, and how you break HashMap.

**Short answer:**
`==` compares references (or primitive values). `equals` defines logical equality. The contract: equal objects must have equal `hashCode`; hash codes must stay stable while an object is a key in a hash map. Mutating key fields after insert loses the entry.

#### What it is
Object equality underpins collections, caching, and domain modeling. `equals`/`hashCode` must be consistent for hash-based structures. `==` compares references; `equals` defines logical equality for objects.

#### How it works (internals)
HashMap hashes the key, finds a bin, then compares with `equals`. If you override `equals` without `hashCode`, equal objects may land in different bins. If `hashCode` uses a mutable field and you change it after `put`, `get` returns null even though the entry exists — a 'lost' mapping. JPA entities with null id at insert then assigned id break `Set` membership.

#### When to use / when NOT to use
Use immutable value types (records) as map keys. Override both methods together. Never use mutable entities as `HashSet` keys.

#### Production example
A `User` entity in a `Set` uses `equals`/`hashCode` on database id. Before persist, id is null — all users collide in one bucket. After flush, hash changes and duplicates appear in the set. Fix: use business key or don't put entities in sets until persisted.

#### Common mistakes
Using `==` on boxed integers outside cache range. Mutating Lombok `@Data` entities used as keys. Implementing `equals` with only id while `hashCode` uses all fields.

#### Interview follow-ups (with model answers)

**Q:** Why does `HashMap` use `equals` after `hashCode`?
**A:** Hash codes narrow the search to a bin; collisions (distinct keys with same hash or index) require `equals` to find the exact key. Without `equals`, collisions would be indistinguishable. Poor `hashCode` increases chain length but `equals` still ensures correctness. This is why mutable keys are dangerous — hash index computed at insert may not match later lookup. Production caches keyed by mutable `StringBuilder` content fail mysteriously. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Can two unequal objects share a hash code?
**A:** Yes — hash collisions are expected; `equals` disambiguates. Extreme collision rates (constant `hashCode`) degrade to linked-list traversal O(n). HashDoS historically targeted this; treeification mitigates long bins in Java 8+. Still fix broken `hashCode`. Security-sensitive maps may use seeding (`HashMap` internal hash spread). On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** How do records handle equals/hashCode?
**A:** Compiler generates `equals`, `hashCode`, and `toString` from components — shallow on references. Nested mutability still breaks immutability guarantees. Records are ideal for Kafka keys and cache entries when components are themselves immutable value types. Do not use records for JPA entities without understanding identity vs value semantics. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

A dedup `Set<Order>` in your Kafka consumer silently allows duplicate processing after Hibernate assigns database ids mid-batch.

Orders entered the set with null id — shared hash bucket. After `save()`, id changes, `Set` thinks they're new. Fix: dedup on `businessOrderId` (immutable UUID from message) not JPA surrogate key. Use `ConcurrentHashMap.putIfAbsent` on business key. Add test: persist mid-batch and assert dedup holds. This bug surfaces only under batch persistence, not unit tests with pre-assigned ids.

#### Code / config (when useful)
```java
@Override
public boolean equals(Object o) {
    if (this == o) return true;
    if (!(o instanceof OrderKey that)) return false;
    return Objects.equals(orderId, that.orderId);
}
@Override
public int hashCode() {
    return Objects.hash(orderId);
}
```

---

### 8. Why is `String` interned, and when is intern() a footgun?

**Short answer:**
String literals and `intern()` place strings in the string pool (on-heap since Java 7). Interning deduplicates bounded repeated values but can pin unbounded unique strings forever and add pool contention. Never intern user-generated text. String pool deduplicates literals and `intern()` results — on-heap since Java 7.

#### What it is
The string pool is a special collection of unique string instances shared across the JVM. Literals like `"ACTIVE"` are automatically interned at compile/load time. `intern()` returns canonical instance from pool — `==` safe only for interned strings.

#### How it works (internals)
Literals like `"ACTIVE"` are automatically interned. `String.intern()` adds a copy to the pool if absent, returning the canonical instance. JDK 7+ moved the pool to the heap, so interned strings participate in GC like other objects — but while interned they are strongly reachable from the pool.

#### When to use / when NOT to use
Intern only measured, bounded enums/status codes with heavy duplication. Prefer static final constants or enums instead of runtime `intern()`. Prefer `enum` or `static final` constants over runtime `intern()` for status codes.

#### Production example
A log parser calls `line.intern()` on every token to 'save memory.' Unique tokens explode Metaspace/heap retention; GC cannot reclaim them. Removing `intern()` and using a bounded Guava cache for known tokens cuts memory 40%. Log parser calls `line.intern()` on every token — unique tokens explode retention.

#### Common mistakes
Interning request IDs, emails, or JSON keys. Assuming intern is free synchronization. Using `==` on non-interned strings expecting value equality.

#### Interview follow-ups (with model answers)

**Q:** Where is the string pool in Java 17?
**A:** On the Java heap — moved from PermGen in Java 7. Interned strings are ordinary objects collected when no longer referenced from pool or application. Pool itself is a weakly held structure in the heap (implementation details vary by JDK). They participate in GC like other objects but stay while interned. Metaspace is unrelated to string pooling in modern JDKs. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** How does `String.concat` vs `+` work?
**A:** Simple `+` with compile-time constants may use `invokedynamic` string concat (Java 9+). Runtime concat builds new strings — not auto-interned. `String.concat` creates new instance unless optimized. Neither interns result. For hot paths, `StringBuilder` still wins for many appends. Do not intern concat results. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Impact of intern on GC?
**A:** Reduces duplicate char[] for repeated values — fewer objects. But unbounded interning increases old-gen occupancy and remark work — GC runs more often on a larger live set. Net negative for high-cardinality data. Measure retention and GC pause before/after. Prefer explicit bounded caches with eviction. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Microservice memory grows linearly with request volume over days despite flat traffic. Heap dump shows millions of distinct `String` instances referenced from `StringTable`.

Search for `intern()` on dynamic data — often added to 'optimize' Kafka headers or log tags. Remove intern; use `enum` for known values; for bounded vocab use Caffeine cache with max size. Restart to clear pool; deploy fix. Add code review rule banning `intern()` except in approved utilities. RSS should stabilize within one GC cycle after fix.

---

### 9. How do generics work? What is erasure, and what survives at runtime?

**Short answer:**
Type parameters are erased to their bounds at compile time — usually `Object` or the declared bound. You cannot `new T()`, overload on `List<String>` vs `List<Integer>`, or call `T.class` without a `Class<T>` token. PECS governs wildcards; arrays remain reified and covariant (unsafe). Type parameters erase to bounds at compile time — runtime sees raw `List`, not `List<String>`.

#### What it is
Generics add compile-time type safety without reifying type parameters in bytecode (with exceptions like some reflective APIs). Compiler inserts casts and bridge methods; you cannot `new T()` or `instanceof List<String>`. Type tokens (`Class<T>`, Jackson `TypeReference`) recover generic info at boundaries.

#### How it works (internals)
The compiler inserts casts and bridge methods. At runtime `List<String>` is just `List`. Type tokens (`Class<T>`, Guava `TypeToken`, Jackson `TypeReference`) recover type info when needed. `? extends T` is a producer (read); `? super T` is a consumer (write) — PECS.

#### When to use / when NOT to use
Use generics for API clarity. Pass `Class<T>` or `TypeReference` for serialization frameworks. Avoid raw types and unchecked casts at system boundaries.

#### Production example
A REST client deserializes `List<OrderDto>` with Jackson `TypeReference<List<OrderDto>>` because erasure loses the generic type at runtime. Using raw `List` caused `LinkedHashMap` elements instead of DTOs in production. REST client deserializes `List<OrderDto>` with Jackson `TypeReference` — raw `List` yielded `LinkedHashMap` elements.

#### Common mistakes
Casting `(List<String>) list` without validation. Using generics on static fields incorrectly. Expecting `instanceof List<String>` at runtime.

#### Interview follow-ups (with model answers)

**Q:** What is heap pollution?
**A:** Storing a `List<Integer>` in a raw `List` reference then reading as `List<String>` compiles with warnings but throws `ClassCastException` at runtime when accessing elements. Common after legacy integration with unchecked casts. Fix: eliminate raw types, use `@SuppressWarnings` only at proven-safe boundaries with comments. Enable `-Xlint:unchecked` in CI. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** How does `List<?>` differ from `List<Object>`?
**A:** `List<?>` is an unknown subtype — you can read as `Object` but cannot add (except null). `List<Object>` accepts any object add but is not a supertype of `List<String>` in Java's invariant generics. API design: use `List<? extends Foo>` to accept any list of Foo subtypes for reading. Confusing them breaks APIs and causes compile errors in sensible client code. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Reified generics in other languages?
**A:** C# and Kotlin retain type parameters at runtime — no erasure. Java chose erasure for backward compatibility with pre-generics bytecode. Trade-off: cleaner migration but need type tokens at serialization boundaries. Kotlin on JVM inherits erasure for Java interop. Spring's `ParameterizedTypeReference` exists because of this gap. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Kafka consumer uses `ObjectMapper.readValue(payload, List.class)` for `List<PaymentEvent>`. Tests pass with single events; prod intermittently throws `ClassCastException` on map access.

Erasure lost element type — Jackson deserializes to `LinkedHashMap`. Fix: `TypeReference<List<PaymentEvent>>` or `JavaType` from factory. Add contract test with realistic JSON array. Audit all message listeners for raw `List.class`/`Map.class`. Consider Avro/Protobuf to eliminate JSON type guessing.

---

### 10. Why are arrays covariant and generics invariant? Give a production bug.

**Short answer:**
Arrays are covariant: `String[]` is an `Object[]`, so assigning an `Integer` through an `Object[]` reference throws `ArrayStoreException` at runtime. Generics are invariant: `List<String>` is not a `List<Object>` — the compiler forbids the unsound assignment. Bugs still happen via raw types and unchecked casts. Arrays are covariant at runtime — `ArrayStoreException` if wrong element type stored.

#### What it is
Covariance and invariance control how subtyping flows through composite types. Arrays carry runtime element type; generic type parameters are erased. Covariant arrays enabled Java 1.0 flexibility; generics chose compile-time safety.

#### How it works (internals)
Arrays carry runtime element type; generics erase element type. Covariant arrays enabled `Object[] objects = new String[10]; objects[0] = 1` to compile with runtime failure. Generics chose safety at compile time. Production bugs: deserializing JSON to raw `List`, then casting elements; passing `List<String>` where `List<Object>` expected via unchecked cast.

#### When to use / when NOT to use
Prefer `List<T>` over arrays in public APIs. Use `@SuppressWarnings` only at proven-safe boundaries with comments. Prefer `List<T>` in public APIs over arrays for domain data.

#### Production example
A legacy integration passes `Object[]` into a method expecting `String[]` because 'strings are objects.' Under load, bad data inserts an `Integer`; `ArrayStoreException` kills the batch job. Migrating to `List<String>` catches the bug at compile time. Legacy integration passes `Object[]` where `String[]` expected — `Integer` in batch kills job with `ArrayStoreException`.

#### Common mistakes
Using arrays in public APIs for 'performance' without measurement. Unchecked cast from raw collections after JSON parse. Assuming generics and arrays behave the same.

#### Interview follow-ups (with model answers)

**Q:** Why doesn't Java have `List<String>[]`?
**A:** Generic arrays would require runtime checks incompatible with erasure — `List<String>[]` and `List<Integer>[]` erase to same runtime type, allowing `ArrayStoreException`-like bugs on lists. Language designers banned generic array creation. Use `List<List<String>>` or arrays of raw type with unchecked warnings at single boundary. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** What is `@SafeVarargs` for?
**A:** Suppresses heap pollution warnings on varargs methods that do not leak the generic array (e.g., `List.of` factory internals). Apply only when method is final/private and does not store the array. Misuse hides real pollution. Code review should verify no retention of `Object[]` created from varargs. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Covariant return types on overrides?
**A:** Subclass may return narrower type — `OrderRepository find()` returning `JpaOrderRepository`. Separate feature from array covariance. Compiler generates bridge methods. Useful in Spring Data-style APIs. Does not affect generic erasure rules on parameters. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Batch importer accepts `Object[] row` from CSV plugin and casts to `String[]` before validation. Under production data, row 40,000 contains a numeric zip code as `Integer`.

`ArrayStoreException` kills entire nightly batch. Fix: use `List<String>` end-to-end, validate cell types per column schema, or coerce with explicit parsing. Never rely on covariant array assignment for untrusted data. Add fuzz tests with mixed types. Spring Batch item readers should emit typed records, not `Object[]`.

---

### 11. Checked vs unchecked exceptions. What do you throw in a Spring service?

**Short answer:**
Checked exceptions force catch-or-declare at compile time; unchecked (`RuntimeException`) propagate without declaration. In Spring services, prefer unchecked domain exceptions translated by `@ControllerAdvice` to HTTP responses. Wrap third-party checked exceptions at adapter boundaries; never swallow or use exceptions for control flow in hot paths. Spring services favor unchecked domain exceptions mapped by `@ControllerAdvice` — not checked leaks.

#### What it is
Java's exception hierarchy splits predictable external failures (checked) from programming errors and most business failures (unchecked). Checked exceptions force catch-or-declare; unchecked propagate without signature pollution. Exceptions allocate and walk stack — expensive for control flow in hot loops.

#### How it works (internals)
Checked exceptions appear in method signatures; callers must handle or declare. Unchecked bypass compile-time handling. Spring MVC and most modern frameworks favor unchecked for service layers because checked exceptions leak through every layer and encourage empty catch blocks. Stack walks and object allocation make exceptions expensive in tight loops.

#### When to use / when NOT to use
Use checked at true API boundaries (file I/O libraries, JDBC in low-level code). Use unchecked in domain/services. Preserve cause chains; log once at the boundary, not on every rethrow.

#### Production example
A payment adapter wraps `IOException` from a legacy SDK in `PaymentGatewayException` (unchecked) at the repository boundary. The service throws `InsufficientFundsException`; `@ControllerAdvice` maps it to 402. Domain code never declares `throws IOException`.

#### Common mistakes
Catching `Exception` and returning null. Logging and rethrowing (duplicate logs). Using exceptions for expected validation in loops.

#### Interview follow-ups (with model answers)

**Q:** Would you catch `OutOfMemoryError`?
**A:** Generally no for recovery — JVM state may be corrupt. Possible last-resort hook to log context before exit in controlled environments. Do not catch to 'continue' business processing. Fix heap, leaks, or limits. Some frameworks catch `Error` to abort request only — document risk. Operational response: restart pod, heap dump if `-XX:+HeapDumpOnOutOfMemoryError` configured. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Difference between `Error` and `Exception`?
**A:** `Error` subclasses (`OutOfMemoryError`, `StackOverflowError`) indicate serious JVM/resource problems — rarely caught. `Exception` is recoverable application-level (`IOException`, business rules). `RuntimeException` is unchecked exception branch. Spring does not translate `Error` to 500 meaningfully — process may die. Teach teams not to extend `Error` for business cases. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** How does Spring translate exceptions to Problem Details?
**A:** Spring 6 `ResponseEntityExceptionHandler` and `@ExceptionHandler` produce `ProblemDetail` (RFC 7807). Add `@ControllerAdvice` methods per domain exception with `type`, `title`, `status`, `detail`. Consistent across services when shared library defines base handler. Better than stringly `message` fields for API consumers. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Legacy integration forces `throws SQLException` through five service layers. Developers catch, log, and return `Optional.empty()` — finance reports silent data loss.

Refactor: JDBC stays in `@Repository`; wrap `SQLException` in unchecked `DataAccessException` at repository boundary (Spring does this for `JdbcTemplate`). Domain throws business exceptions only. Controller advice maps to HTTP. Add ArchUnit rule: no `SQLException` above infrastructure package. Audit catch blocks that swallow — replace with propagate or structured error result.

---

### 12. `try-with-resources` and the suppressed exception chain.

**Short answer:**
Try-with-resources closes `AutoCloseable` in reverse order of declaration. If both the body and `close()` throw, the close exception is added as suppressed on the primary — visible via `getSuppressed()`. Always implement `close()` idempotently. Try-with-resources closes in reverse declaration order; close exceptions become suppressed.

#### What it is
Try-with-resources (Java 7+) is syntactic sugar for safe resource cleanup without manual finally blocks. Compiler generates try-finally calling `AutoCloseable.close()` on each resource. Multiple resources: last declared closes first — important for Connection then Statement ordering.

#### How it works (internals)
The compiler generates a try-finally that calls `close()` on each resource. Suppressed exceptions preserve both failure modes — critical when a JDBC connection fails to close after a query error. Multiple resources close last-declared first.

#### When to use / when NOT to use
Use for Connection, Statement, InputStream, any AutoCloseable. Prefer one resource per try when clarity matters; multiple is fine when lifetimes align. Always for Connection, Statement, InputStream, S3 clients, any `AutoCloseable`.

#### Production example
A batch job opens `Connection` and `PreparedStatement`. Query throws `SQLException`; `close()` on the connection also throws. The caller sees the query exception with the close exception suppressed — full story in logs via `Throwable.getSuppressed()`.

#### Common mistakes
Swallowing close exceptions manually in finally (try-with-resources handles it). Non-idempotent `close()` throwing on second call. Forgetting that resources must be effectively final.

#### Interview follow-ups (with model answers)

**Q:** Can you use try-with-resources on custom types?
**A:** Yes — implement `AutoCloseable` (or `Closeable` for IO). Spring beans are usually not closed per request — use for per-operation clients. Kafka producers may be long-lived; do not wrap singleton in try-with-resources per message. Pattern fits row-level JDBC, file uploads, temporary HTTP clients. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** What implements `AutoCloseable` vs `Closeable`?
**A:** `Closeable` extends `AutoCloseable` and adds `IOException` on close. Try-with-resources accepts both. `Closeable`'s contract allows interrupting blocked IO on close. Use `Closeable` for streams; `AutoCloseable` for anything needing cleanup. JDBC 4+ connections implement `AutoCloseable`. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** How does Kotlin `use` compare?
**A:** Kotlin stdlib `use` is try-with-resources for `Closeable` — inline lambda, suppressed exceptions same as Java. Interop with Java resources is seamless. Prefer `use` in Kotlin services for per-request streams. Spring Kotlin codebases still use Hikari connections from pool via `use` in repository methods. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Incident report shows primary `SQLException: connection closed` but root cause unclear. Logs omit nested exception. Batch used manual finally that logged and swallowed close errors.

Reproduce with try-with-resources on Connection + PreparedStatement; force failure on execute and on close (mock). Assert `getSuppressed()` length > 0. Fix logging to iterate `Throwable.getSuppressed()`. Replace manual finally across batch module. Pool metrics may show leak from aborted closes hidden by swallow — recheck active connection count.

#### Code / config (when useful)
```java
try (Connection conn = dataSource.getConnection();
         PreparedStatement ps = conn.prepareStatement(sql)) {
    ps.executeUpdate();
} // both closed; suppressed chain preserved
```

---

### 13. How does `ClassLoader` delegation work? What is a leak?

**Short answer:**
ClassLoaders use parent-first delegation: bootstrap → platform → application. Child loaders ask parents before defining classes. Classloader leaks happen when static caches or ThreadLocals hold classes from a redeployed webapp loader — Metaspace grows until OOM after N redeploys. Parent-first delegation: bootstrap → platform → application — child asks parent before defining.

#### What it is
Class loaders isolate bytecode namespaces. Each loaded class is owned by exactly one loader.

#### How it works (internals)
Parent-first prevents core JDK classes from being replaced by app copies. Servlet containers historically used child-first for WAR isolation. Spring Boot's `LaunchedURLClassLoader` loads nested jars from the fat jar. Leaks: `static Map` caching reflectively loaded classes; ThreadLocal without `remove()` on pooled threads holding references to unloaded webapp classes.

#### When to use / when NOT to use
Diagnose with `jmap -clstats`, heap dumps showing classloader dominators, and Metaspace graphs. Fix: remove listeners, clear ThreadLocals, bound caches.

#### Production example
After 50 hot deploys on Tomcat without restart, Metaspace hits 512 MB cap. Heap dump shows thousands of duplicate `com.acme.OrderService` classes from different `WebappClassLoader` instances rooted in a static `ConcurrentHashMap` event bus. Clearing the bus on context destroy fixes it.

#### Common mistakes
Storing classes in static singletons across redeploys. Assuming fat-jar apps cannot classloader-leak (they can with agents and dynamic codegen). Ignoring `spring-boot-devtools` restart classloader in dev.

#### Interview follow-ups (with model answers)

**Q:** What is the bootstrap classloader?
**A:** Loads core JDK classes (`java.*`) from `lib/modules` — native C++ part of JVM, not a Java `ClassLoader` instance. Platform loader (Java 9+) loads platform modules. Application loader loads classpath. `null` context classloader tricks in old libraries still appear in production stack traces. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** How does OSGi differ from delegation?
**A:** OSGi uses module bundles with explicit imports/exports and can use buddy/class-space rules — not parent-first. Java EE servers approximated isolation with hierarchical loaders. Spring Boot fat jar flattens to one app loader unless using custom layering. Know your deployment model when debugging `ClassNotFoundException` vs `LinkageError`. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** What is `Thread.contextClassLoader` for?
**A:** Frameworks (JAXB, JDBC drivers, Kafka serializers) load SPI implementations from thread context loader — not necessarily the defining loader of your code. Wrong context causes `ServiceConfigurationError` in containers. Spring sets context loader on worker threads; async `@Async` must propagate or set explicitly. Virtual threads inherit context — verify in Loom migrations. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

SaaS admin UI allows plugin hot-reload. After 30 reloads, Metaspace stable but old-gen grows; full GC ineffective. Heap dump shows classloaders for plugins v1–v30 all reachable.

Plugin registry static `Map<String, PluginClassLoader>` never removes old entries. Fix: on reload, close loader (if custom), remove from map, clear ThreadLocals referencing plugin classes, deregister JMX beans. Use isolated `URLClassLoader` per plugin version with weak references if needed. Add integration test: 50 reload cycles, assert Metaspace plateaus.

---

### 14. What changed from Java 8 to 17 that a senior must know?

**Short answer:**
Records, sealed classes, text blocks, switch expressions, `var`, modules (JPMS), HTTP Client, G1 default, removal of Java EE from JDK, Nashorn gone, CMS removed, strong encapsulation (`--add-opens`), and the path to virtual threads in 21. Migration touches `javax`→Jakarta, illegal reflective access, and bytecode library upgrades. Java 8→17: records, sealed classes, modules, G1 default, `javax`→Jakarta, strong encapsulation. Plan migration with BOM upgrades, `--add-opens` as temporary debt, and JDK 17 CI before prod.

#### What it is
Java 8→17 is a multi-release jump affecting language, runtime, GC, and ecosystem dependencies. PermGen gone — Metaspace; CMS removed; Nashorn removed. JPMS encapsulates `sun.*` — Hibernate, Lombok, Mockito needed updates or opens.

#### How it works (internals)
Language: records, sealed types, pattern matching evolution, text blocks. Runtime: G1 default, ZGC production-ready, PermGen gone (Metaspace). Modules encapsulate `sun.*` internals — Hibernate, Lombok, Mockito need `--add-opens` or updates. Java EE APIs removed from JDK — use Jakarta artifacts. Nashorn removed; use GraalJS or external engine.

#### When to use / when NOT to use
Plan migration with enforcer rules, multi-release testing, and dependency BOMs. Don't skip 11/17 intermediate breakage in libraries. Run enforcer rules on minimum Java and dependency versions in CI.

#### Production example
A Spring Boot 2.7 app on Java 8 moves to 17: replace `javax.persistence` with `jakarta.persistence`, upgrade Hibernate 6, add `--add-opens java.base/java.lang=ALL-UNNAMED` temporarily, run with `-Werror` on deprecation. CI runs on 17 before prod cutover. Spring Boot 2.7 on Java 8 → 17: `jakarta.persistence`, Hibernate 6, temporary `--add-opens java.base/java.lang=ALL-UNNAMED`.

#### Common mistakes
Assuming 'Java is backward compatible' for the whole ecosystem. Ignoring reflective access warnings. Staying on Java 8 'because it works' without security patch plan.

#### Interview follow-ups (with model answers)

**Q:** What is Project Loom's status in 21?
**A:** Virtual threads are final in Java 21 — preview in 19/20. Spring Boot 3.2+ integrates with Tomcat/Undertow virtual thread executors. Structured concurrency APIs evolved — check JEP status for your exact 21 patch. Migration path: JDK 17 LTS first, then 21 for Loom — do not jump 8→21 without dependency audit. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Differences between Java 11 and 17 LTS?
**A:** 17 adds sealed classes, records (14+), pattern matching for `instanceof`, macOS AArch64 support, new GC defaults maturity. 11 removed Java EE modules, introduced `var`, HTTP client. Both LTS — 17 is current migration target for Spring Boot 3. Security patches for 8 ended for public updates — commercial risk on 8. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** How does jlink help container images?
**A:** jlink builds custom JRE with only required modules — smaller attack surface and image size. Spring Boot layered jars often still ship full JRE via base image. Useful for CLI tools and microservices without full desktop modules. Graal native-image is separate path for instant startup. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Enterprise mandates JDK 17 in 90 days. Boot 2.7 monolith uses Hibernate 5, `javax.*`, Mockito inline, and a shaded JAR reflecting into `sun.misc.Unsafe`.

Sequence: upgrade to Boot 3.2 + Jakarta namespace, Hibernate 6, replace reflective hacks with supported APIs, run parallel JDK 17 CI with `-illegal-access=deny` to surface issues. Budget `--add-opens` per library with owners and expiry. Load test and canary. Do not big-bang — use strangler for modules still on `javax.validation` transitive deps.

---

### 15. Java 21: virtual threads vs platform threads. When do you still use a pool?

**Short answer:**
Virtual threads are cheap, JVM-scheduled continuations mounted on a small carrier pool — ideal for blocking I/O (JDBC, HTTP). Platform threads remain for CPU-bound work and when you must limit scarce in-process parallelism. Connection pools, not thread pools, throttle database access. Virtual threads: cheap continuations on small carrier pool — ideal for blocking JDBC/HTTP.

#### What it is
Virtual threads (Project Loom) decouple application concurrency from OS thread count. Blocking virtual thread unmounts from carrier; carrier runs another virtual thread. Pinning: `synchronized` or JNI during block holds carrier — limits scalability.

#### How it works (internals)
Blocking a virtual thread unmounts it from the carrier; the carrier runs another virtual thread. Pinning occurs when synchronized blocks or native JNI hold the carrier during blocking I/O — avoid long synchronized around JDBC. Don't pool virtual threads; create per task. Structured concurrency (Java 21) ties subtask lifetimes to scopes.

#### When to use / when NOT to use
Enable virtual threads for request-per-thread Spring Boot 3.2+ blocking stacks. Keep bounded platform pools for CPU pools and legacy libraries that pin. Semaphore-limit DB concurrency regardless of thread count.

#### Production example
Tomcat with 10,000 virtual threads and Hikari pool of 20: requests queue at the pool, not by spawning 10,000 connections. p99 improves vs 200 platform threads blocking on I/O. CPU-bound report generation stays on a fixed `ExecutorService` of size `cores`. Tomcat with 10,000 virtual threads, Hikari pool 20 — requests queue at pool not connections.

#### Common mistakes
Replacing Hikari sizing with 'more virtual threads.' Using `synchronized` around long JDBC calls on JDK versions with pinning. Pooling virtual threads.

#### Interview follow-ups (with model answers)

**Q:** What is structured concurrency?
**A:** JEP 453+ (scope varies by release) ties subtask lifetimes to parent scope — failure cancels siblings. `StructuredTaskScope` simplifies fan-out HTTP/JDBC with clean cancellation. Replaces ad-hoc `ExecutorService` + manual `Future` cancel. Use for parallel calls within one request; combine with virtual threads for blocking I/O subtasks. Error handling is clearer than raw `CompletableFuture` chains in some cases. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** How does pinning show in JFR?
**A:** JFR `jdk.VirtualThreadPinned` events flag when carrier blocked by synchronized/native while virtual thread mounted. High pin rate → reduce `synchronized` around JDBC, prefer `ReentrantLock`, upgrade drivers. Pinning is the main Loom footgun in legacy Spring code using synchronized caches on hot paths. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Spring Boot property for virtual threads?
**A:** `spring.threads.virtual.enabled=true` (Boot 3.2+). Also configure Tomcat `max-http-request-header-size` etc. separately. `@Async` requires `TaskExecutor` configured for virtual threads if desired. Verify JDBC driver and Redis client are blocking-safe — most are. Load test with realistic connection pool limits. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

You enable virtual threads on order API; throughput improves but p99 worsens. Thread dump shows few carriers and many pinned virtual threads blocked in `synchronized` around a shared cache.

Replace synchronized cache with `ConcurrentHashMap` or Caffeine (thread-safe by design). Re-profile pinning events in JFR. Do not disable virtual threads wholesale — fix pin points. If legacy lib requires synchronized internally, isolate calls on small platform pool. Measure carriers = default `Runtime.getRuntime().availableProcessors()`.

#### Code / config (when useful)
```yaml
// Spring Boot 3.2+
spring.threads.virtual.enabled=true
```

---

### 16. Explain `Optional` usage that seniors accept vs reject.

**Short answer:**
Accept `Optional` as a return type when absence is meaningful; chain with `map`/`flatMap`; use `orElseGet` for lazy defaults. Reject Optional fields, JSON DTO properties, parameters, bare `get()`, and `orElse(expensive())` which evaluates eagerly. Accept `Optional` as return type for 'maybe absent'; reject as field, parameter, or JSON DTO property. Use `orElseGet` for lazy defaults — `orElse(expensive())` always runs.

#### What it is
`Optional` is a container for absent values — not a general-purpose null replacement. `Optional` is a container for absence — not a general null replacement. Serialization frameworks need modules for Optional — JSON usually uses null or omitted field.

#### How it works (internals)
Intended for return types to force callers to handle absence. Serialization frameworks don't treat Optional as standard JSON null semantics without modules. Parameters should use overloads or nullable with validation. `orElseGet(Supplier)` defers computation; `orElse` runs always.

#### When to use / when NOT to use
Return Optional from service methods that may not find an entity. Use empty list instead of `Optional<List>`. At boundaries, convert to nullable or 404.

#### Production example
`findOrderById` returns `Optional<Order>`; controller does `orElseThrow(() -> new NotFoundException(id))` mapping to 404. DTO does not use `Optional<String> email` — uses plain `String` or omits field.

#### Common mistakes
Optional everywhere 'to avoid null.' `optional.get()` in production. Optional in JPA entity fields. `optional.get()` in production — use `orElseThrow` with meaningful exception.

#### Interview follow-ups (with model answers)

**Q:** Is `Optional` serializable?
**A:** Not reliably — `Optional` does not implement `Serializable` in standard JDK. Jackson has datatype module; Kafka Avro has no Optional — use union or nullable. Do not put Optional on messages crossing service boundaries. Convert to nullable at DTO boundary. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Performance cost of Optional?
**A:** Small object allocation per return — negligible in typical Spring request scope. Hot inner loops may prefer nullable or sentinel. Do not micro-optimize unless JFR shows allocation pressure from Optional churn. Readability and API intent usually dominate. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Kotlin nullable vs Java Optional?
**A:** Kotlin `String?` is language-integrated; Java uses Optional or annotations (Checker Framework, JetBrains). Interop: Kotlin callers use `orNull()` extensions. In Java APIs exposed to Kotlin, nullable parameters with `@Nullable` annotation are idiomatic. Optional as parameter is anti-pattern in both ecosystems. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Public API team adds `Optional<Address> billingAddress` to shared Kafka Avro schema. Consumers in Python and older Java break; schema registry compatibility checks fail.

Revert to nullable union or explicit `boolean hasBillingAddress` + `Address`. Optional is Java API sugar, not wire format. Document: Optional only on internal service method returns. Add ArchUnit ban on Optional in `*.dto.*` and generated schema classes.

---

### 17. HashMap internals (Java 8+). What happens under resize and collision?

**Short answer:**
HashMap uses a power-of-two array of bins. Collisions chain as linked lists; bins treeify to red-black trees when length > 8 and table ≥ 64. Resize doubles capacity and rehashes. Not thread-safe — concurrent use loses updates or throws CME on iterators.

#### What it is
HashMap is the default associative array — O(1) average get/put with a good hash function. Index `(n - 1) & hash` spreads high bits of `hashCode()`. Load factor 0.75 triggers resize doubling — rehash is costly at large size.

#### How it works (internals)
Index = `(n - 1) & hash` where hash spreads high bits of `hashCode()`. Poor `hashCode` → long bins → O(n) lookups. Treeification caps worst-case bin length. Load factor 0.75 triggers resize. Java 8+ fixed Java 7 infinite loop on concurrent resize but still unsafe without external sync or ConcurrentHashMap.

#### When to use / when NOT to use
Size initial capacity if you know approximate entries (`new HashMap<>(expectedSize * 4 / 3)`). Use immutable keys. Never share HashMap across threads without synchronization.

#### Production example
A cache keyed by mutable `StringBuilder` content mutates after insert — entries become unreachable in the map. Switching to immutable `String` keys fixes 'random cache misses.' Cache keyed by mutable `StringBuilder` — mutate after insert, entries 'lost'.

#### Common mistakes
Custom `hashCode` returning constant. Mutating keys. Using HashMap in @Scheduled job shared across threads without CHM.

#### Interview follow-ups (with model answers)

**Q:** Why power-of-two capacity?
**A:** Bitmask `(n-1) & hash` is fast versus modulo prime. Requires good hash spread — high bits mixed in. Resize doubles capacity — amortized O(1) but spike on rehash. Initial capacity should be next power of two via table size calculation in constructor. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** When does treeify revert to list?
**A:** When tree bin shrinks below threshold 6 after removal — untreeify to save memory. Rare in steady state unless churn is high. Treeification needs `Comparable` keys or supplied `Comparator` — otherwise ClassCastException at treeify time for incomparable keys. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** LinkedHashMap vs HashMap iteration order?
**A:** LinkedHashMap maintains doubly-linked list for insertion-order or access-order iteration. Slightly more memory. Use for LRU caches with `removeEldestEntry`. HashMap iteration order is undefined and changes on resize — never depend on it in prod logic. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

In-memory rate limiter `HashMap<String, Counter>` shared across Tomcat threads shows under-counting under load — some requests bypass limit.

Classic lost update race — not CME because no iteration. Migrate to `ConcurrentHashMap` and atomic `compute` on counter. Or shard maps per thread. Never 'fix' with `Collections.synchronizedMap` without understanding compound check-then-act — use `computeIfAbsent`. Add stress test with 50 threads.

---

### 18. ConcurrentHashMap vs Collections.synchronizedMap vs Hashtable.

**Short answer:**
ConcurrentHashMap offers concurrent reads and fine-grained locking/CAS per bin — no whole-map lock. `synchronizedMap` wraps every method with one lock. `Hashtable` is legacy synchronized throughout. CHM disallows null keys/values; compound check-then-act needs `compute`/`putIfAbsent`.

#### What it is
Choosing the right concurrent map prevents scalability bottlenecks and subtle races. CHM disallows null keys/values — `NullPointerException` by design. Hashtable is legacy — use CHM for new code.

#### How it works (internals)
CHM Java 8+ locks at bin level or uses CAS for some operations. Iterators are weakly consistent. `synchronizedMap` serializes all access — simple but coarse. `Hashtable` is obsolete; use CHM.

#### When to use / when NOT to use
Default to CHM for shared mutable maps. Use synchronizedMap only for legacy or when you need to synchronize iteration manually anyway. Default shared mutable map in Spring `@Component` caches and metrics registries.

#### Production example
A rate limiter map migrated from `Collections.synchronizedMap` to CHM; throughput under 50 threads rises 8×. `putIfAbsent` replaces `if (!contains) put` race. Rate limiter migrated from `synchronizedMap` to CHM — throughput under 50 threads rises 8×.

#### Common mistakes
Iterating CHM while assuming snapshot consistency for size. `get` then `put` instead of atomic `compute`. Null keys in CHM (NPE).

#### Interview follow-ups (with model answers)

**Q:** How does CHM size() work?
**A:** Counts elements by summing bins — approximate under concurrent mutation. Do not use for strict capacity enforcement without external sync. For metrics, slight inaccuracy is OK. For financial limits, use atomic primitives or DB constraint. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** CHM vs ConcurrentSkipListMap?
**A:** Skip list map is sorted/concurrent — O(log n) with `Comparable` keys. Use for time-ordered expiring keys or range scans. CHM is faster for general get/put without ordering. Pick by need for `NavigableMap` concurrent API. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Why no nulls in CHM?
**A:** Ambiguity: `get` returning null means missing or null value — Doug Lea chose ban null values to avoid double interpretation. Use optional wrapper types or sentinel objects if needed. Spring cache abstraction hides this but underlying CHM still applies. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Idempotency store uses CHM `processedIds` with `if (!map.containsKey(id)) { process(); map.put(id, true); }`. Rare duplicate charges still occur.

Race between contains and put — two threads process same id. Fix: `putIfAbsent(id, TRUE) == null` gate before process, or `computeIfAbsent`. Better: DB unique constraint on idempotency key as source of truth; CHM as optimization only. Kafka consumers need store surviving rebalance — consider Redis.

---

### 19. ArrayList vs LinkedList vs CopyOnWriteArrayList.

**Short answer:**
ArrayList: contiguous array, O(1) amortized append, great cache locality — default choice. LinkedList: doubly-linked nodes, poor cache behavior — almost never right; use ArrayDeque for queues. CopyOnWriteArrayList: snapshot iterators, copies array on write — great for rare-write listener lists. ArrayList: default choice — cache-friendly contiguous array, O(1) amortized append.

#### What it is
List implementation choice affects CPU, memory, and concurrency semantics. LinkedList: doubly-linked nodes, poor cache locality — use `ArrayDeque` for queue/stack. COWAL: snapshot iterators, copy array on every write — O(n) write cost.

#### How it works (internals)
ArrayList resize doubles internal array. LinkedList allocates per element. COWAL readers never block; writers pay copy cost — O(n) per mutation. Frequent writes to COWAL destroy performance.

#### When to use / when NOT to use
ArrayList for 99% of lists. COWAL for event listener registries updated rarely. ArrayDeque as stack/queue.

#### Production example
Spring application event listeners stored in COWAL — reads during event dispatch are lock-free. Replacing LinkedList in a hot insertion-middle path with ArrayList cut CPU 30% in profiling. Event listeners in COWAL — dispatch reads without lock.

#### Common mistakes
Choosing LinkedList 'because insert is O(1)' ignoring traversal cost. Using COWAL as a general concurrent list. Forgetting ArrayList is not thread-safe.

#### Interview follow-ups (with model answers)

**Q:** What is RandomAccess marker interface?
**A:** Tag on ArrayList and others signaling O(1) indexed access. Algorithms like `Collections.sort` may choose different strategies. No methods — documentation for callers. LinkedList does not implement it. Minor but shows JVM/library contract awareness. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Vector vs ArrayList?
**A:** Vector is synchronized legacy — slower than ArrayList + external sync or CHM. Do not use Vector in new code. Use `Collections.synchronizedList` if simple sync needed, or concurrent structures. Kafka internal buffers use specialized structures — not Vector. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** When is LinkedList justified?
**A:** Rarely — algorithm coursework or legacy APIs. If frequent head/tail ops without random access, `ArrayDeque`. If concurrent queue, `ConcurrentLinkedQueue` or `LinkedBlockingQueue`. Profiling should prove LinkedList — default skepticism is correct. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Team picks LinkedList for order book 'because inserts are O(1).' Production profiling shows 40% CPU in `ListIterator` traversal during matching.

Switch to ArrayList if inserts are append-mostly, or tree/map structure if ordered by price. LinkedList node allocation hurts GC. If concurrency needed, separate structure — `ConcurrentSkipListMap` for book. Measure before/after with realistic market data replay.

---

### 20. HashSet vs TreeSet vs LinkedHashSet vs EnumSet.

**Short answer:**
HashSet: unordered, O(1) average. TreeSet: sorted, O(log n), needs Comparable/Comparator. LinkedHashSet: insertion-order iteration. EnumSet: bit vector over enum ordinals — extremely fast for enum domains.

#### What it is
Set implementations differ in ordering guarantees and performance characteristics. HashSet backed by HashMap; TreeSet by red-black TreeMap. LinkedHashSet preserves insertion order with small overhead.

#### How it works (internals)
HashSet backed by HashMap. TreeSet by TreeMap (red-black tree). LinkedHashSet maintains doubly-linked entries for order. EnumSet uses bit masks — all operations O(1) for enum cardinality.

#### When to use / when NOT to use
HashSet for general uniqueness. TreeSet when you need sorted traversal or range queries. EnumSet for enum flags. LinkedHashSet when order matters and uniqueness required.

#### Production example
Permission checks use `EnumSet.of(Role.ADMIN, Role.OPS)` for compact storage and fast `contains`. TreeSet used for scheduling tasks ordered by next run time.

#### Common mistakes
TreeSet with `compareTo` inconsistent with `equals` — duplicates slip in. Using HashSet with mutable keys. IdentityHashSet when you need `==` semantics — rare.

#### Interview follow-ups (with model answers)

**Q:** What is BitSet vs EnumSet?
**A:** BitSet is general-purpose bit vector — not type-safe for enums. EnumSet is enum-specific, faster and clearer API. Use EnumSet for domain flags; BitSet for arbitrary large bit indices (Bloom filter internals, etc.). On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** NavigableSet methods?
**A:** `lower`, `floor`, `ceiling`, `higher`, `pollFirst`, `descendingSet` — TreeSet implements NavigableSet. Useful for time-window queries on sorted keys. Kafka timestamp indexing sometimes uses tree structures — know API for interviews. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Set vs List contains performance?
**A:** HashSet O(1) average vs List O(n). For membership-heavy paths (dedup, permission checks), Set is mandatory. Converting List to Set once for repeated lookups wins. Do not call `list.contains` in nested loops on large data. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Scheduler uses TreeSet<Task> comparing only `scheduledTime`. Two tasks same time — one silently dropped from set.

`compareTo` returns 0 for different tasks — TreeSet treats as duplicate. Fix: compare time then taskId as tiebreaker. Or use `PriorityQueue` with explicit tie-breaking. Add unit test with colliding timestamps. Financial scheduling bugs are Sev-1.

---

### 21. Fail-fast vs fail-safe iterators.

**Short answer:**
Fail-fast iterators (ArrayList, HashMap) check `modCount` and throw `ConcurrentModificationException` on structural change during iteration — best-effort, not a concurrency guarantee. Weakly consistent iterators (CHM, COW) may reflect partial updates and never throw CME. Fail-fast iterators check `modCount` — CME on structural change during enhanced-for. Weakly consistent iterators (CHM, COW) never throw CME but may skip/duplicate elements.

#### What it is
Iterator behavior defines what happens when a collection mutates during traversal. Structural change: add/remove altering size — `set` on ListIterator is OK on list. Another thread modifying unsynchronized collection can corrupt without CME.

#### How it works (internals)
Enhanced for-loop uses iterator under the hood. Remove via `Iterator.remove()` only — not `collection.remove()` during foreach. Fail-fast detects single-threaded misuse; another thread modifying without sync can still corrupt HashMap.

#### When to use / when NOT to use
Use iterator remove or collect-then-remove pattern. For concurrent mutation, use concurrent collections or external synchronization. Use `removeIf` for bulk predicate removal on single-threaded lists.

#### Production example
A scheduled job iterates `orders` with foreach and removes cancelled orders via `orders.remove(o)` — CME in prod. Fix: `orders.removeIf(Order::isCancelled)` or iterator.remove(). Scheduled job foreach over `orders` and `orders.remove(o)` — CME in prod.

#### Common mistakes
Assuming CME means multi-threading (can be same-thread bug). Modifying sublist backing list unexpectedly. Using parallelStream while mutating source.

#### Interview follow-ups (with model answers)

**Q:** Is CME guaranteed in all cases?
**A:** No — best-effort single-thread detection. Concurrent unsynchronized modification may corrupt without CME. Do not rely on CME as concurrency guard. Use proper concurrent collections. CME is a debugging aid for misuse. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** How does removeIf work internally?
**A:** Uses iterator under hood with batch remove — O(n) single pass, safe for ArrayList. More efficient than manual iterator loop for large lists. For concurrent collections, use their specific bulk removal APIs. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** ConcurrentModificationException vs corruption?
**A:** CME is fail-fast throw — no silent corruption on single-threaded detected case. Undetected concurrent HashMap mutation can lose entries or infinite loop historically — worse than CME. CHM avoids CME by weak consistency, not by making compound ops atomic. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

REST export streams large `List<Invoice>` while background job removes paid invoices from same ArrayList injected as singleton.

Intermittent CME or skipped rows in export. Fix: copy snapshot `List.copyOf(invoices)` for export, or synchronize, or use COWAL if reads dominate. Spring singleton `@Component` List field is shared mutable state — anti-pattern. Scope per-request or immutable snapshots.

---

### 22. Comparable vs Comparator. Sorting stability.

**Short answer:**
`Comparable` defines natural order on the class (`compareTo`). `Comparator` is external, multiple per type. Java's `List.sort` and `Collections.sort` are stable — equal compareTo elements keep relative order. Inconsistent compareTo/equals breaks TreeSet/TreeMap.

#### What it is
Ordering contracts affect sorting, trees, and priority queues. TreeSet/TreeMap require compare consistent with equals for set semantics. `Comparator.comparing` chains fields with `thenComparing`.

#### How it works (internals)
Stable sort preserves order among equal elements — important for multi-key sorts done in stages. `Comparator.comparing` chains fields. `compareTo` returning 0 for unequal objects (e.g., different ids, same sort key) causes Set duplicates.

#### When to use / when NOT to use
Implement Comparable for obvious natural order (dates, money with scale). Use Comparator for alternate sorts. Document tie-breaking.

#### Production example
TreeSet of `Money` compares only amount; two different currency objects with same amount collapse to one — financial bug. Fix: compare currency then amount, or don't use TreeSet. TreeSet of `Money` comparing only amount — two currencies same amount collapse.

#### Common mistakes
Subtracting ints in compareTo (overflow). Returning (int)(a - b) for longs. Inconsistent with equals in TreeMap keys.

#### Interview follow-ups (with model answers)

**Q:** TimSort complexity?
**A:** O(n log n) worst case, often faster on partially ordered data — exploits runs. Stable. Java 7+ uses TimSort for object arrays. Important for multi-key stable sorts done in stages (sort by date then id). On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Comparator vs Comparable for DB ORDER BY?
**A:** DB sort is separate — JPA `Sort` maps to SQL. Comparable on entity can leak ORM concerns — prefer explicit query order. In-memory sort of loaded collection uses Comparable/Comparator. Keep consistent with SQL to avoid surprise pagination bugs. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** reversed() and thenComparing?
**A:** `Comparator.comparing(Foo::getDate).reversed().thenComparing(Foo::getId)` — declarative multi-key sort. Null handling via `nullsFirst`. Prefer over manual compareTo spaghetti in services. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Kafka replay orders events by `Comparator.comparing(Event::timestamp)` for reconciliation. Events with identical timestamp appear out of order vs primary topic — reconciliation false positives.

Stability preserves input order among equal timestamps only if sort is stable and single sort pass. Add `thenComparing(Event::getOffset)` or sequence id. Document total order contract. DB reconciliation should use composite cursor (timestamp, id).

---

### 23. Deep vs shallow copy. Why Cloneable is considered broken.

**Short answer:**
Shallow copy shares nested mutable references; deep copy duplicates the graph. `Cloneable` is a marker with protected `Object.clone()` — shallow by default, easy to leak mutable internals, and awkward with inheritance. Shallow copy shares nested references; deep copy duplicates the object graph. Cloneable is broken — copy constructors, records, MapStruct preferred.

#### What it is
Copy semantics matter for DTOs, defensive programming, and thread-safe snapshots. `Object.clone()` default is shallow; Cloneable is marker without enforcement. Serialization clone is slow and brittle — avoid unless measured need.

#### How it works (internals)
Cloneable doesn't enforce `clone()` implementation; subclasses break symmetry. Copy constructors, static factories, records, and mapping tools (MapStruct) are clearer. Document whether nested collections are copied.

#### When to use / when NOT to use
Use immutable values where possible. Copy constructors for mutable graphs. Jackson clone via serialize/deserialize only when necessary and measured.

#### Production example
A config object cloned shallowly shares the mutable `List<String> endpoints` — one service mutates, all clones see change. Deep copy via constructor copying `List.copyOf(endpoints)`. Config cloned shallowly — shared `List<String> endpoints` mutated by one tenant affects all.

#### Common mistakes
Implementing Cloneable because IDE generated it. Deep clone via serialization (slow, brittle). Forgetting to copy mutable fields in record compact constructor.

#### Interview follow-ups (with model answers)

**Q:** How do records handle nested mutability?
**A:** Shallow copy of reference fields — caller mutating nested list mutates record semantics. Use compact constructor: `this.items = List.copyOf(items);`. Document depth. Records are not automatic deep immutability. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** MapStruct mapping vs clone?
**A:** MapStruct generates explicit field copy at compile time — configurable depth, ignores lazy Hibernate proxies if configured. Clearer than Cloneable. Use for DTO ↔ entity boundaries. Not a substitute for domain-driven immutable snapshots. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Copy-on-write snapshots?
**A:** COW data structures (CopyOnWriteArrayList) give snapshot iteration without full graph copy. For domain snapshots, immutable copy with `List.copyOf` or persistent data structures. Kafka consumer offset commit after processing is snapshot boundary — related concept. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Multi-tenant SaaS passes `TenantConfig` clone to plugins; one plugin adds endpoint to list, another tenant receives traffic to wrong URL.

Shallow clone shared mutable list. Fix: deep copy collections in copy constructor, or immutable config with `List.copyOf` on build. Audit all `clone()` usages. Plugins get read-only view interface. Add test: mutate after clone, assert isolation.

---

### 24. Immutability: how do you make a class actually immutable?

**Short answer:**
Make the class `final` (or sealed), all fields `final`, no setters, defensive copies of mutable constructor args and getters, never leak `this` during construction, no mutable statics. Records are a good default for value types; use `List.copyOf` for collection fields. True immutability: final class, final fields, defensive copies in/out, no leaking `this`. Records + `List.copyOf` are good defaults for value types and Kafka message bodies.

#### What it is
True immutability enables safe sharing across threads without locks. Unmodifiable wrappers (`List.of`) prevent caller mutation but don't stop internal mutation if reference escapes.

#### How it works (internals)
If you expose an internal `List` or `Date` directly, callers can mutate your 'immutable' object. Defensive copy on way in and way out. Subclasses must not add mutable state. Initialization-on-demand holder pattern relies on immutability for safe publication.

#### When to use / when NOT to use
Prefer records for DTOs and domain values. Guava `ImmutableList` for internal storage. Avoid 'immutable' beans with Lombok `@Setter`.

#### Production example
`OrderSnapshot` record copies `List<LineItem>` with `List.copyOf(items)` in compact constructor — callers cannot mutate internal state via getter.

#### Common mistakes
Final fields referencing mutable arrays without copy. Returning internal Date reference. Spring beans claimed immutable but `@RefreshScope` mutates.

#### Interview follow-ups (with model answers)

**Q:** Immutable vs unmodifiable?
**A:** Immutable: no state change ever after construction. Unmodifiable view: underlying collection may still change if another reference mutates backing list. `Collections.unmodifiableList` is view — not true immutability. `List.copyOf` creates immutable copy if elements themselves immutable. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Can Hibernate entities be immutable?
**A:** Yes with `@Immutable` entity and no setters — read-only queries. Updates require re-fetch or separate command model. Good for reporting replicas. Mutable entities remain default for OLTP. Do not confuse immutable entity with immutable value object in DDD. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Value objects in DDD?
**A:** Identified by attributes not id — money, address, date range. Immutable, side-effect free, equality by value. Records fit well. Entities have lifecycle; value objects replace by new instance on change. Kafka events should be value-style immutable payloads. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Team marks config bean `@ConfigurationProperties` as immutable with final fields but exposes `List<String> brokers` getter returning internal list. Consumer sorts list in place — production outage.

Defensive copy in getter: `List.copyOf(brokers)` or return immutable copy at bind time. Better: record wrapper `BrokerList` with validated factory. Spring Boot 3 supports `@ConfigurationProperties` on records. Code review checklist for mutable getters on 'immutable' types.

---

### 25. `final`, `finally`, `finalize` — still asked, still failed.

**Short answer:**
`final` prevents reassignment, overriding, or subclassing. `finally` runs on normal or exceptional exit unless JVM kill, infinite loop, or `System.exit`. `finalize` is deprecated — use try-with-resources or `Cleaner` for native cleanup. `final`: no reassignment, override, or subclass (class). `finally`: always runs unless kill/exit.

#### What it is
Three similar keywords with completely different roles in the language and JVM. Three unrelated keywords — interview trap for senior candidates. Final fields have safe publication semantics if `this` doesn't escape constructor.

#### How it works (internals)
`final` fields have JMM safe-publication semantics after constructor completes if `this` doesn't escape. `finally` executes even when try returns — watch for exceptions masking return values if finally also throws. Finalizers run unpredictably on GC thread — too late for sockets.

#### When to use / when NOT to use
Use final for fields and immutability. Finally for cleanup when try-with-resources isn't enough. Never override finalize.

#### Production example
Resource cleanup moved from finalize to try-with-resources on `FileInputStream` — fd closed promptly, not when GC feels like it. DB connection cleanup moved from finalize to try-with-resources — fds close promptly. Connection pool exhaustion from finalize-delayed close eliminated.

#### Common mistakes
Relying on finalize to close DB connections. Returning from try while finally throws — suppressed. Assuming final means thread-safe (only the reference is fixed).

#### Interview follow-ups (with model answers)

**Q:** What is try-with-resources vs finally?
**A:** Try-with-resources generates correct close with suppressed exceptions — preferred for AutoCloseable. Finally needed when logic doesn't fit TWR or multiple exit paths without resources. TWR is syntactic sugar over try-finally — compiler generated code is correct pattern to emulate manually. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Final parameters — style value?
**A:** Compile-time documentation — not reflected in bytecode for callers. Useful in short methods and constructors. IDE plugins enforce. No runtime immutability effect on passed object reference. Style choice in modern codebases. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Cleaner vs PhantomReference?
**A:** `java.lang.Cleaner` (Java 9+) registers action when object becomes phantom reachable — replaces finalize for native peer cleanup. More predictable than finalize but still GC-dependent — prefer explicit close for scarce resources. Direct ByteBuffer uses Cleaner internally. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Legacy JDBC wrapper overrides `finalize()` to close connection. Under load, DB reports max connections reached while heap is healthy.

Connections returned to pool only after GC — far slower than request rate. Remove finalize; use try-with-resources or pool `evict` on checkout timeout. Hikari leak detection logs unclosed connections. Migrate wrapper to `AutoCloseable`. Incident fix is config + code, not bigger pool alone.

---

### 26. Overload vs override. What is signature, and what about return types / exceptions?

**Short answer:**
Override: same name and erased parameter types, runtime dispatch, covariant return allowed, cannot broaden checked exceptions. Overload: same name, different parameters, compile-time resolution. `static` methods hide, not override. `private` methods don't participate in polymorphism.

#### What it is
Method resolution rules determine which implementation runs and what the compiler accepts. JVM signature is name plus erased parameter types; return types and checked exceptions are compile-time constraints.

#### How it works (internals)
Virtual dispatch uses vtable for instance methods. Overload resolution picks the most specific applicable signature — boxing puzzles (`int` vs `Integer` vs `Object`) cause surprises. Bridge methods preserve generics override symmetry.

#### When to use / when NOT to use
Avoid ambiguous overload sets. Use `@Override` annotation. Prefer clear parameter types over many overloads.

#### Production example
Adding `void process(Order o)` and `void process(Object o)` — autoboxing makes `process(1)` ambiguous compile error. Remove overload or rename. Payments SDK `process(long)` vs `process(Long)` — Kafka consumers hit wrong overload after upgrade until tests assert dispatch.

#### Common mistakes
Assuming static override. Hiding instead of overriding in subclass — surprise when called on super type. Overload resolution with varargs and arrays.

#### Interview follow-ups (with model answers)

**Q:** What is a bridge method and when does the compiler generate one?
**A:** When a subclass overrides a generic method with a more specific return type, the compiler emits a synthetic bridge method with the erased return type that forwards to the real override. For example, `List<String> get()` overriding `List get()` produces a bridge `List get()` that casts and delegates. Without bridges, bytecode verification would reject covariant returns on generic hierarchies. In production you rarely see them unless decompiling framework stubs, but they explain duplicate method names in stack traces. They matter for reflection and bytecode agents matching methods by descriptor — agents must account for synthetics.

**Q:** Can you override a private method in a subclass?
**A:** No — private methods are not virtual. A subclass can declare the same signature, but that is a new method; `@Override` will not compile. Dispatch uses the reference type's declared methods. This trips up developers copying template methods from abstract bases. In Spring proxies, only public/protected methods on the proxied bean are intercepted — 'overriding' a private helper does nothing for AOP. At runtime, calling through a superclass reference never invokes the subclass private method unless called from within that subclass.

**Q:** How does overload resolution interact with autoboxing and varargs?
**A:** The compiler applies phases: exact match, widening primitives, autoboxing, varargs. A call like `foo(1)` may match `foo(int)`, `foo(long)`, `foo(Integer)`, or `foo(Object...)` depending on overloads — ambiguity is a compile error. Adding `foo(int...)` can change which method wins. In API design, avoid overload sets differing only by `int` vs `Integer` vs `long`. When migrating code, explicit casts document intent and prevent accidental dispatch changes across JDK versions. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Your team ships `EventPublisher` with `publish(OrderEvent)` and `publish(Object)`. After a release, some `OrderEvent` payloads route to a dead-letter handler. Unit tests still pass.

Overload resolution bound `publish(Object)` when callers pass `null` or ambiguous types after a refactor. Fix: rename overload, delete catch-all, or use sealed `Event` hierarchy with single entry point. Add ArchUnit forbidding `publish(Object)` on domain publishers. Integration tests must exercise each overload with realistic types — overloads are compile-time only.

---

### 27. Why is `Object` wait/notify on the same monitor as synchronized?

**Short answer:**
Condition queues are bound to a specific monitor. `wait()` releases the monitor and parks until `notify`/`notifyAll`; wakees must re-acquire. Always wait in a `while (!condition)` loop. Prefer `java.util.concurrent` locks and queues over raw wait/notify.

#### What it is
wait/notify is the low-level condition variable API tied to intrinsic locks. Condition queues are per-monitor — wait and notify must use the same intrinsic lock.

#### How it works (internals)
Calling `wait()` without holding the monitor throws `IllegalMonitorStateException`. `notify` wakes one arbitrary waiter; `notifyAll` is safer unless you prove single waiter. Spurious wakeups require loop re-check. Lost wakeup if you notify before wait without holding same lock protocol.

#### When to use / when NOT to use
Use `BlockingQueue`, `CountDownLatch`, `Phaser` for new code. wait/notify only when maintaining legacy or studying JMM. Greenfield code uses `BlockingQueue` or `Lock.newCondition()` — reserve wait/notify for legacy.

#### Production example
Legacy buffer pool uses `synchronized(buffer) { while (empty) buffer.wait(); }` — correct loop pattern. New code uses `ArrayBlockingQueue.take()`. Inventory pool used `if (empty) wait()` — duplicate reservations under Black Friday until replaced with `ArrayBlockingQueue`.

#### Common mistakes
if instead of while around wait. notify without holding lock. Using wait/notify on separate Boolean flag without synchronization. `notify()` without holding the monitor — `IllegalMonitorStateException` or swallowed errors.

#### Interview follow-ups (with model answers)

**Q:** When should you use `notify` vs `notifyAll`?
**A:** Use `notifyAll` unless you prove exactly one waiter and a single condition predicate. `notify` wakes one arbitrary thread; multiple waiters on different logical conditions sharing one monitor can sleep forever. Bounded buffers with one lock need `notifyAll` or two `Condition` objects via `ReentrantLock`. In production, prefer `ArrayBlockingQueue`. If you must use wait/notify, document the invariant. `notify` micro-optimization has caused P1 incidents when conditions were not truly singular. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** How does `Lock.newCondition()` compare to intrinsic wait/notify?
**A:** `ReentrantLock` supports multiple `Condition` objects per lock — separate wait sets avoid waking the wrong waiter. `await()`/`signal()` mirror wait/notify but require holding the lock and support timed/interruptible waits. Fair locks reduce starvation at throughput cost. Choose `Lock`+`Condition` for try-lock, fairness, or multiple conditions — e.g., custom connection pools. For most services, `BlockingQueue` is simpler and harder to misuse than hand-rolled wait/notify. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Why do spurious wakeups exist and how do you defend against them?
**A:** JVM monitors permit spurious wakeups — threads may return from `wait` without `notify`. Defense: always re-evaluate the condition in a `while` loop while holding the lock. This also handles another thread stealing the resource between wakeup and re-acquisition. Never assume `wait` implies the predicate is true. Code review should flag `if` around `wait`. Wrap legacy wait/notify pools behind a class enforcing the loop pattern. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Legacy reservation service uses synchronized wait/notify on `ReservationPool`. Black Friday reports double-charges; thread dumps show many WAITING on one monitor.

Pool used `if (slotAvailable) wait()` instead of `while`, so spurious wakeups and stolen slots let threads proceed without valid reservations. Some threads called `notify` outside synchronized block. Fix: `LinkedBlockingQueue` of tokens or `while (!tryReserve()) pool.wait()` with `notifyAll`. Add wait-time metrics and load-test contended reservations.

---

### 28. Serialization: what breaks, and what do you use instead?

**Short answer:**
Java native serialization is insecure (gadget chains), brittle (`serialVersionUID`), and slow. Never deserialize untrusted bytes. Prefer JSON (Jackson), Protobuf, or Avro. If forced: allowlists, `ObjectInputFilter`, minimal type graphs.

#### What it is
Serialization converts object graphs to bytes for storage or transport. Gadget chains turn innocent `readObject` into RCE — Commons Collections made this famous.

#### How it works (internals)
Deserialization can instantiate arbitrary classes via reflection — gadget chains execute attacker code. `serialVersionUID` mismatches break compatibility. Records and enums serialize more predictably but don't fix security alone.

#### When to use / when NOT to use
Use schema-driven formats at API and cache boundaries. Avoid RMI and Java serialization over the network. API boundaries use Avro, Protobuf, or JSON — not Java native serialization.

#### Production example
Legacy session replication used Java serialization — security audit mandates JSON + signed tokens. `ObjectInputFilter` blocks non-allowlisted classes as defense in depth. Session replication sunset after pen-test RCE on session blobs — migrated to signed JWT plus Redis.

#### Common mistakes
Deserializing Kafka messages with `ObjectInputStream`. Changing class shape without UID plan. Serializable entities with lazy Hibernate proxies.

#### Interview follow-ups (with model answers)

**Q:** What is `serialVersionUID` and when must you change it?
**A:** `serialVersionUID` fingerprints compatible evolution of serializable classes. Undeclared UID is computed from fields — any change can break old blobs. Declare explicitly for rolling upgrades reading cache/session data. Changing UID invalidates old bytes — plan flush or dual-read. For new systems, avoid Java serialization. If stuck, document optional-field rules and test round-trip across N and N-1 in CI. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** How do you secure deserialization in a legacy Java service?
**A:** Eliminate `ObjectInputStream` on untrusted inputs first. If unavoidable, set global `ObjectInputFilter` allowlisting types, limit array sizes and graph depth. Prefer JSON with Jackson default typing disabled. Scan dependencies for gadget classes. Audit Redis and session stores for Java-serialized values. Migration: dual-write JSON, cutover readers, delete Java serialization path. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** How does Jackson polymorphic typing differ from Java serialization risk?
**A:** `@JsonTypeInfo` can deserialize attacker-chosen classes if subtypes are unrestricted — gadget risk via setter chains. Use `@JsonSubTypes`, allowlists, or sealed hierarchies. Avoid `enableDefaultTyping`. Kafka events should use Avro with Schema Registry. Java serialization is worse because the entire classpath is potential gadgets. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Order service deserializes Java blobs from Redis written by an older microservice. Pen test achieves RCE in staging.

Root cause: `ObjectInputStream` without filtering plus Commons Collections on classpath. Disable reader, flush Redis, deploy allowlist interim. Permanent: JSON or Kryo with explicit registration, Avro on Kafka. Treat Java-serialized bytes as executable — format migration beats filter tuning alone.

---

### 29. Reflection vs MethodHandles vs invokedynamic.

**Short answer:**
Reflection inspects and invokes members dynamically — flexible but slower and breaks encapsulation. MethodHandles are JVM-aware callable references used by the language. `invokedynamic` bytecode backs lambdas, string concat, and some dynamic languages. JDK 17+ restricts `setAccessible` on JDK internals — budget `--add-opens` with removal tickets.

#### What it is
Three mechanisms for late-bound invocation with different performance and security profiles. Reflection inspects at runtime; MethodHandles are JVM-verified call sites; invokedynamic backs lambdas.

#### How it works (internals)
Reflection walks metadata and checks access each call — mitigated by `setAccessible` (restricted on JDK 17+). MethodHandles respect access rules after lookup. Lambdas compile to private static methods + invokedynamic bootstrap. Frameworks (Spring, Hibernate) still reflect — `--add-opens` documents the pain.

#### When to use / when NOT to use
Prefer MethodHandles or generated code for hot dynamic dispatch. Reflection fine for frameworks at startup, not per-request hot paths. Prefer MapStruct and annotation processors in hot paths; reflection for wiring only.

#### Production example
Spring creates beans via reflection once at startup — acceptable. Per-request reflective `Method.invoke` for validation — replaced with compiled Bean Validation. Boot 3 on JDK 17 failed Hibernate init until ORM upgrade removed blanket `java.base` opens.

#### Common mistakes
Reflective access to private JDK internals without migration plan. Assuming reflection is 'free' at runtime. Ignoring module encapsulation errors after JDK upgrade.

#### Interview follow-ups (with model answers)

**Q:** What is LambdaMetafactory and how does it relate to invokedynamic?
**A:** Lambdas compile to `invokedynamic` bootstrapped by `LambdaMetafactory.metafactory`, linking a synthetic private method to a functional interface once. Later invocations are near-direct — faster than allocating anonymous classes. MethodHandles implement linkage. Explains lambda serialization fragility and synthetic names in stack traces. Frameworks use the same mechanism for string concat (Java 9+) and pattern matching internals. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** When would you choose VarHandle over AtomicInteger?
**A:** VarHandle exposes CAS and memory ordering on plain fields without boxing — for off-heap structures and expert concurrent code. `AtomicInteger` is the default for counters. Choose VarHandle when a field must stay inline or coordinate with `MemorySegment`. Misuse causes ordering bugs — stick to atomics unless JFR proves field-level contention. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** How does Spring MVC avoid reflection on every controller invocation?
**A:** At startup Spring builds cached `InvocableHandlerMethod` with resolved resolvers and converters. Request threads dispatch through precomputed adapters — reflection cost is paid once. Contrast with per-request `Method.invoke` dominating CPU at high QPS. Keep handler methods public on proxied beans. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Payments API on Boot 2.7/JDK 11 works; JDK 17 mandate causes crash-loop with `InaccessibleObjectException` in Hibernate metadata build.

Hibernate 5 reflects into encapsulated packages. Upgrade to Hibernate 6 aligned with Boot; remove copy-pasted `--add-opens` from only some environments. Run JDK 17 CI before cutover. Minimal targeted opens with owner and expiry — not permanent security posture.

---

### 30. How do lambdas capture variables? Why effectively final?

**Short answer:**
Lambdas capture locals that are final or effectively final — the compiler copies values into synthetic fields because the lambda may outlive the stack frame. Capturing `this` retains the outer instance. Method references improve clarity; checked exceptions need wrapping. Lambdas capture effectively final locals by copying into synthetic fields.

#### What it is
Lambdas are instances of functional interfaces with captured closure state. Functional-interface instance with optional closure; method references when signature matches.

#### How it works (internals)
Effectively final means no reassignment after initialization. For locals, bytecode stores copies — mutations after capture aren't seen. Instance method references capture `this`. Serialization of lambdas is fragile.

#### When to use / when NOT to use
Keep lambdas short; extract to methods for testability. Don't capture large mutable structures. Extract non-trivial bodies to named methods; wrap checked exceptions explicitly.

#### Production example
Listener lambda captures `userId` (effectively final) from loop variable — correct. Reassigning `userId` in loop breaks compilation. Accidental `this` capture in long-lived callback leaks outer Activity/Context in Android patterns.

#### Common mistakes
Trying to mutate captured int without AtomicInteger. Throwing checked exceptions from lambda without try/catch wrapper. Serializable lambdas in distributed cache.

#### Interview follow-ups (with model answers)

**Q:** Lambda vs anonymous inner class — what changes at bytecode level?
**A:** Anonymous classes generate new class per site and may capture `this`. Lambdas use invokedynamic — less allocation and metadata. Serialization differs: lambda classes are synthetic and fragile. Inner classes still needed for multiple interfaces. Stack traces show `$$Lambda$` — learn to read them in incidents. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** What is captured `this` and when is it dangerous?
**A:** Instance method references keep the outer object alive on static registries — including datasources and mis-scoped request fields. Dangerous in Android Activities, servlet filters, Guava callbacks. Fix: pass IDs only, weak listeners, unregister on destroy. Heap dumps show `$Lambda` retaining giant contexts. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** How do you handle checked exceptions inside lambdas?
**A:** Functional interfaces do not declare checked exceptions. Wrap and rethrow unchecked, or custom functional interface with `throws`. Streams cannot throw checked — extract methods or use `flatMap`. Avoid blanket `@SneakyThrows` on production services. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Heap dump shows 2 GB path from Guava cache through `PaymentService$$Lambda` to full Spring context. Traffic flat.

`@PostConstruct` registered `this::onSettlementEvent` on global bus without deregister — each redeploy leaked a context. Fix: narrow delegate, weak listeners, ArchUnit banning instance refs in static registries.

---

### 31. Stream API: intermediate vs terminal, laziness, and when streams hurt.

**Short answer:**
Intermediate ops build a lazy pipeline; terminal ops trigger execution. Stateful ops (`sorted`, `distinct`) buffer. `parallel()` uses common ForkJoinPool — dangerous in servlet containers with blocking tasks. Prefer loops for tiny collections; streams for declarative transforms without shared mutation.

#### What it is
Streams are a functional-style sequence API over collections and other sources. Intermediate ops fuse lazily; stateful ops buffer; terminal ops drive execution.

#### How it works (internals)
Pipeline fusion avoids intermediate materialization where possible. Short-circuit ops (`findFirst`, `anyMatch`) stop early. Parallel streams split via spliterator — overhead dominates small inputs. `forEach` with side effects on shared state races.

#### When to use / when NOT to use
Use streams for readable filter/map/collect chains. Avoid parallel streams in request threads unless CPU-bound and measured with dedicated pool. Sequential streams for small collections; parallel only for measured CPU-bound batch on dedicated pool.

#### Production example
Replacing a 5-element validation loop with stream — readability win, no perf gain. Parallel stream on 10M rows for CPU-bound aggregation — wins on dedicated FJP, loses when run on Tomcat common pool blocking on JDBC. Parallel validation over 200 items blocked on Redis — starved company-wide ForkJoin work.

#### Common mistakes
Mutating external list in forEach. parallelStream in @Transactional service. Using stream for simple indexed loop. Side-effect `forEach` on shared `ArrayList` — use `collect(toList())`.

#### Interview follow-ups (with model answers)

**Q:** What spliterator characteristics matter for parallel performance?
**A:** `SIZED` and `SUBSIZED` enable good task granularity. `ORDERED` limits parallelism. `ArrayList` splits well; `LinkedList` does not. Unknown-size IO streams hurt parallel. Custom sources must implement `trySplit` honestly. Low steal rate in JFR means stay sequential. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** findFirst vs findAny in a parallel stream?
**A:** `findFirst` preserves order — costlier in parallel. `findAny` is cheaper when order irrelevant. Both short-circuit. `findAny` is non-deterministic — fine for idempotent pick, wrong for audit. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** When do streams lose to a plain for-loop?
**A:** Tiny collections pay pipeline setup cost. Hot numeric loops should stay imperative unless readability wins measurably. Profile before parallelizing. Senior teams ban parallel streams in request handlers via ArchUnit. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Batch job in order service uses `orders.parallelStream()` to aggregate revenue; unrelated APIs timeout company-wide.

Common pool workers blocked on Hikari inside mapper — noisy neighbor. Move batch to dedicated pool or SQL `GROUP BY`. Lint-ban `parallelStream` in service packages.

---

### 32. `reduce` vs `collect`. Why collectors matter.

**Short answer:**
`reduce` folds values (prefer immutable identity). `collect` uses `Collector` with supplier, accumulator, combiner, finisher — correct for mutable containers (`toList`, `groupingBy`). Parallel streams require associative accumulators. Parallel `collect` needs associative combiner — wrong combiner corrupts finance totals silently.

#### What it is
Reduction summarizes streams into optional values or collections. `reduce` folds to one value; `collect` uses supplier, accumulator, combiner, finisher.

#### How it works (internals)
`Collectors.toList()` uses mutable accumulation with combiner for parallel. `groupingBy` is SQL GROUP BY. `reducing` and `summarizingInt` for stats. Wrong combiner breaks parallel correctness.

#### When to use / when NOT to use
Use collect for grouping and aggregation. Use reduce for optional scalar folds (max, sum with identity). `toUnmodifiableList()` when exposing aggregated results to callers.

#### Production example
Sales report: `orders.stream().collect(groupingBy(Order::region, summingInt(Order::amount)))` replaces manual HashMap merge. Parallel `reduce` with mutable `ArrayList` accumulator duplicated transactions until `groupingBy` fix.

#### Common mistakes
Mutable shared accumulator in parallel reduce. `toList()` on parallel without understanding combiner. Collecting to immutable list then mutating.

#### Interview follow-ups (with model answers)

**Q:** When do you write a custom Collector?
**A:** When built-ins cannot express accumulation — rolling stats, trie builds, sorted merges. Implement four functions; mark `UNORDERED` if order irrelevant. Test combiner associativity. Prefer SQL or Flink for heavy aggregation in services. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** How do downstream collectors work in groupingBy?
**A:** `groupingBy(classifier, downstream)` applies second collector per bucket — `counting()`, `summingInt()`, nested grouping. Models SQL `GROUP BY` in memory. Null keys NPE unless custom map factory. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** What is Collectors.teeing useful for?
**A:** Runs two collectors on same elements, merges results — min and max in one pass. Merger must handle parallel partials. Useful for metrics; overuse hurts readability. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Settlement job parallel-streams millions of rows via `reduce` merging maps; amounts disagree with Oracle intermittently.

Combiner mutated shared map — parallel splits lost updates. Fix: `groupingBy` + `summingLong` or SQL `SUM`. Replay test comparing stream vs SQL totals.

---

### 33. Autoboxing pitfalls.

**Short answer:**
Autoboxing hides allocations in loops, enables `==` bugs on Integers outside −128..127 cache, NPE on unboxing null, and GC pressure from boxed primitives in hot paths. Integer cache is −128..127 — never compare boxed IDs with `==` above that range.

#### What it is
Primitives and wrapper types convert implicitly — with performance and correctness costs. Autoboxing hides allocations in collections — JFR exposes them quickly.

#### How it works (internals)
JVM caches small integers. `Integer a=127; Integer b=127; a==b` may be true; at 128, false. Unboxing null throws NPE. Collections of `Integer` allocate per add.

#### When to use / when NOT to use
Use primitives in hot loops. `Map` with primitive keys via Eclipse Collections/FastUtil only after profiling. Null-safe unboxing with `Objects.requireNonNull`.

#### Production example
Tight loop summing `List<Integer>` — 50% time in allocation. Switch to `int[]` or IntStream.sum(). `==` on `Long` transaction IDs caused rare reconciliation mismatches until `Objects.equals`.

#### Common mistakes
== on boxed Long ids. Null Integer in arithmetic. Stream of boxed primitives without need.

#### Interview follow-ups (with model answers)

**Q:** What is the future of value types in Java?
**A:** Project Valhalla introduces inline types and generic specialization over primitives — watch JDK releases. Until then use FastUtil/Eclipse Collections after profiling. Not a reason for premature off-heap hacks. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** int vs Integer in generics and APIs?
**A:** Generics require reference types. Use primitive `long` in signatures when null absent. Normalize boxed JDBC/JPA returns at boundaries. Mixed math boxes repeatedly in tight loops. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Record with Integer vs int — design guidance?
**A:** Prefer primitives when null invalid; use `OptionalInt` or validate in compact constructor. `Integer` for optional DTO fields — align JSON null vs missing with OpenAPI. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Reconciliation unmatched trades 0.3% after release; IDs above 127 fail in cache dedup. Tests used small numbers.

Developer used `==` on `Integer` keys — works for −128..127 cache only. Fix: `Set<Long>` or `Objects.equals`. SpotBugs `ReferenceEquality` plus regression IDs 126, 128, 999_999.

---

### 34. `StringBuilder` vs `StringBuffer` vs concat.

**Short answer:**
`StringBuffer` is synchronized — rarely needed. `StringBuilder` for manual loops. Compiler uses `invokedynamic` string concat (Java 9+) or StringBuilder in bytecode. Reuse builders in hot loops; use parameterized logging to avoid string work when log level disabled.

#### What it is
String concatenation strategies affect allocations and thread safety. `StringBuilder` mutable not thread-safe; `StringBuffer` synchronized — almost never needed.

#### How it works (internals)
Single `+` in compile time may fold to constant. Loop concat without builder creates O(n²) copies. `StringBuffer` thread-safe overhead unnecessary unless sharing across threads.

#### When to use / when NOT to use
StringBuilder in tight loops. `+` for few compile-time constants. Never StringBuffer unless shared mutable builder (almost never).

#### Production example
Logging: `log.debug("order=" + order)` always builds string — use `log.debug("order={}", order)`. Access log `+` in loop allocated 40% young gen — `StringBuilder` reuse cut GC frequency.

#### Common mistakes
StringBuffer 'for safety.' Concat in loop. StringBuilder not reused when profiling shows allocation hotspot. `StringBuffer` on local variable 'for safety'.

#### Interview follow-ups (with model answers)

**Q:** What bytecode does string concatenation generate today?
**A:** Java 9+ uses `invokedynamic` + `StringConcatFactory`. Loops still need manual `StringBuilder` when profiling shows hotspots. JFR `ObjectAllocation` finds concat sites. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Text blocks and indentation — practical pitfalls?
**A:** Incidental indentation stripped by closing triple-quote position. Use `stripIndent()` for SQL/JSON logs. No secrets in source text blocks. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** When is StringJoiner preferable to StringBuilder?
**A:** Delimiters, prefixes, suffixes for protocols and CSV fragments. `String.join` and `Collectors.joining` cover most cases. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Audit API builds 50k-row CSV via `result = result + row` on servlet thread — p99 and young GC spike at month-end.

Quadratic copies. Fix: sized `StringBuilder` or stream to `OutputStream`. Better: streaming response and S3 multipart — do not materialize giant strings.

---

### 35. I/O: blocking streams vs NIO vs NIO.2 vs virtual threads.

**Short answer:**
`java.io` blocking streams are simple — one thread per connection historically. NIO (channels, selectors, ByteBuffers) powers Netty. NIO.2 adds `Path`, async file channels. Virtual threads make blocking I/O acceptable again at app layer; Netty still wins for extreme connection counts per CPU.

#### What it is
Java I/O evolved from stream abstraction to channel/buffer model to async file APIs. java.io blocks platform threads; NIO multiplexes; NIO.2 adds Path API; virtual threads remount on block. java.io blocks platform threads; NIO multiplexes; NIO.2 adds Path API; virtual threads remount on block. java.io blocks platform threads; NIO multiplexes; NIO.2 adds Path API; virtual threads remount on block. java.io blocks platform threads; NIO multiplexes; NIO.2 adds Path API; virtual threads remount on block. java.io blocks platform threads; NIO multiplexes; NIO.2 adds Path API; virtual threads remount on block.

#### How it works (internals)
Blocking read ties platform thread to socket. Selector multiplexes many channels on few threads. Direct buffers live off-heap. Virtual threads mount/unmount on blocking — Tomcat can handle more concurrent blocking requests.

#### When to use / when NOT to use
Use blocking + virtual threads for typical Spring JDBC/HTTP. Netty for high-concurrency gateways. Always set socket and read timeouts.

#### Production example
Migration from WebFlux to virtual-thread MVC for team productivity — blocking JDBC acceptable with 5k virtual threads and pool of 30 DB connections. WebFlux to virtual-thread MVC — 8× concurrent requests, DB pool still bottleneck at 30 connections.

#### Common mistakes
Unbounded threads before virtual threads. Direct buffers without release. Mixing async servlet API with blocking JDBC on same thread assumptions.

#### Interview follow-ups (with model answers)

**Q:** Selector vs epoll — what does the JVM use?
**A:** NIO `Selector` maps to epoll on Linux, kqueue on macOS. Selector thread waits on many channels with one syscall. Virtual threads mount/unmount on block — integration is JDK-internal. App devs still set socket timeouts on blocking reads. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** When is FileChannel.transferTo the right tool?
**A:** Zero-copy sendfile from file to socket — static files, replication-style workloads. Measure on your OS/JDK; prefer presigned S3 URLs for multi-GB downloads from JVM. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** How do you choose an HTTP client in 2025 Java services?
**A:** Java 11+ `HttpClient`, Apache HC5, OkHttp — all fine with tuned pools. Virtual threads pair with blocking clients if downstream limits respected. Set connect/read timeouts; retry only idempotent calls with jitter. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Virtual threads on Tomcat 10.1 raise throughput then plateau — low CPU, high latency, JFR shows pinning.

Code holds `synchronized` around JDBC or legacy JNI SSL — carriers block. Fix: `ReentrantLock`, upgrade libs, or small platform pool for pinned work. Right-size Hikari — 10k virtual threads cannot share 20 DB connections.

---

### 36. JDBC basics a Java interviewer still expects.

**Short answer:**
Driver → Connection (pooled) → PreparedStatement (parameterized) → ResultSet. Always bind parameters; use HikariCP; close via try-with-resources; transactions via `setAutoCommit(false)`; set fetch size for large reads; never hold connections across remote calls. Connection pool is real concurrency limit — virtual threads do not create more DB capacity.

#### What it is
JDBC is the low-level database access API underlying JPA and Spring Data. JDBC underlies JPA — debugging returns to SQL, timeouts, transactions.

#### How it works (internals)
PreparedStatement prevents SQL injection and enables plan cache. Connection pool sizes the real concurrency limit. Fetch size streams results instead of loading all rows. Timeouts: `setQueryTimeout`, socket timeout on URL.

#### When to use / when NOT to use
Know JDBC even when using JPA — debugging requires SQL and connection semantics. try-with-resources; never hold connections across HTTP or Kafka poll intervals. try-with-resources; never hold connections across HTTP or Kafka poll intervals. try-with-resources; never hold connections across HTTP or Kafka poll intervals. try-with-resources; never hold connections across HTTP or Kafka poll intervals. try-with-resources; never hold connections across HTTP or Kafka poll intervals.

#### Production example
Leak detection: thread holds Connection 5 minutes during HTTP call to payment API — Hikari warns. Fix: shorten transaction; call payment after commit. Hikari leak detection: connection held 4 min during Feign inside `@Transactional` — split txn from remote call.

#### Common mistakes
String concat SQL. `SELECT *` on huge table without fetch size. One connection per request without pool.

#### Interview follow-ups (with model answers)

**Q:** Statement vs PreparedStatement caching at the driver?
**A:** PreparedStatement enables plan cache per bind signature. Client pooling (`useServerPrepStmts`) reduces parse overhead. ORM logging that inlines values defeats prepare. Measure parse time in pg_stat_statements before tuning. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** How does Hikari validate connections?
**A:** `isValid(timeout)` or lightweight test query on checkout after idle. `maxLifetime` below DB idle timeout. Leak detection logs borrower stacks — invaluable. Pool size from measured DB capacity, not myths. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** JPA vs JDBC — when do you drop to JDBC?
**A:** Bulk ingest, reporting with hints, streaming cursors, vendor bulk copy. Keep JDBC behind repository — not in controllers. Staff engineers use both: ORM for CRUD, JDBC for pathological corners. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Kafka lag on `payment-settled`; DB CPU 95%; virtual threads blocked in `ResultSet.next`.

Wide JPA query without fetch size/index — N+1 via lazy load. Fix: projection, index on `settlement_id`, reduce `max.poll.records`, query timeout. Pause consumer when pool wait high.

#### Code / config (when useful)
```java
try (Connection c = dataSource.getConnection();
     PreparedStatement ps = c.prepareStatement(
         "SELECT id, status FROM orders WHERE tenant_id = ?")) {
    ps.setLong(1, tenantId);
    ps.setFetchSize(500);
    try (ResultSet rs = ps.executeQuery()) {
        while (rs.next()) { /* process */ }
    }
}
```

---

### 37. J2EE / Jakarta EE map for Spring people.

**Short answer:**
Jakarta EE covers Servlet, JSP, JPA, Bean Validation, JMS, JAX-RS, JTA, JNDI, security. Spring Boot embeds a servlet container and reimplements DI, transactions, and security without a full app server. APIs moved `javax.*` → `jakarta.*` in EE 9. Boot embeds Servlet — you still deploy `jakarta.servlet.Filter` without WebLogic.

#### What it is
Java/Jakarta EE is the standard enterprise stack; Spring is a popular alternative programming model. Jakarta EE specs; Spring is opinionated model on Servlet, JPA, JMS.

#### How it works (internals)
Spring Boot uses Tomcat/Jetty/Undertow (servlet container) plus Spring modules. You still touch `jakarta.servlet` filters. Full app servers (WebLogic, Liberty) provide admin, clustering, JNDI — heavier ops. Banks may still run them for compliance.

#### When to use / when NOT to use
Spring developers should know what EE provides to integrate (JMS, JTA) and why teams left monolithic app servers. Know EE for JMS, JTA XA, certified stacks in regulated estates.

#### Production example
Team debates WebLogic vs Boot: Boot wins for dev velocity and container deploy; JTA XA still needed — use Atomikos or move to outbox pattern. IBM MQ via Spring JMS on embedded Tomcat — same jakarta.jms as WebLogic listener.

#### Common mistakes
Thinking Spring replaces servlet spec entirely. Ignoring jakarta migration. Assuming JNDI in cloud-native apps.

#### Interview follow-ups (with model answers)

**Q:** What is Eclipse MicroProfile?
**A:** Extensions for microservices — Config, Health, Metrics, OpenAPI, Fault Tolerance on Quarkus/Liberty. Spring parallels in Actuator/Cloud. Useful for hybrid K8s health integration. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Quarkus vs Spring Boot?
**A:** Quarkus: startup/memory, native image. Spring: ecosystem breadth. Choose Quarkus for Knative edge; Spring for enterprise integration surface. Test Hibernate/Kafka adapters on both before migration. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** When is full application server justified?
**A:** Certified EE profiles, centralized JNDI, XA across EAR modules, legacy EJB. Banks containerize Liberty while new services use Boot — hybrid is normal. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Vendor library is `javax.servlet`; Boot 3 is `jakarta.servlet`. Shaded build passes; prod `ClassNotFoundException` in filter chain.

Binary incompatibility at runtime. Upgrade vendor, fork, or sidecar. Ban javax shading without filter integration tests. Track EE migration as dependency graph.

---

### 38. Servlet filter vs interceptor vs listener. Thread model.

**Short answer:**
Servlet Filter wraps request/response in the servlet chain before dispatch. Spring HandlerInterceptor runs after handler mapping. Listeners observe context lifecycle events. Traditionally one request = one thread; async servlet and WebFlux change the model.

#### What it is
Cross-cutting request handling exists at servlet and Spring MVC layers. Filters wrap request; interceptors after mapping; listeners observe lifecycle.

#### How it works (internals)
Filters see all requests (static, errors). Interceptors see dispatched handler routes. `ServletContextListener` starts background tasks on deploy — must shut down on destroy. Async servlet releases container thread but callback thread needs context propagation.

#### When to use / when NOT to use
Security headers and tracing in filters; authorization annotations in Spring Security; business pre-checks in interceptors sparingly. Tracing in filters; auth in Security; not business rules in filters.

#### Production example
Request ID filter sets MDC; forgotten cleanup on async thread — logs missing trace id. `TaskDecorator` copies MDC to @Async threads. @Async lost trace ID until `TaskDecorator` copied MDC. @Async lost trace ID until `TaskDecorator` copied MDC. @Async lost trace ID until `TaskDecorator` copied MDC. @Async lost trace ID until `TaskDecorator` copied MDC. @Async lost trace ID until `TaskDecorator` copied MDC.

#### Common mistakes
Heavy logic in filters. Static request state without cleanup. Assuming interceptor runs for `@ControllerAdvice` errors.

#### Interview follow-ups (with model answers)

**Q:** How is filter order determined in Spring Boot?
**A:** `@Order` on `FilterRegistrationBean` — lower runs earlier. Security chain is separate ordered list. Document order when multiple filters mutate wrappers. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Why OncePerRequestFilter?
**A:** Forwards re-invoke filters — without guard, tracing runs twice. Extend it for custom servlet filters unless per-dispatch behavior intended. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** WebFlux WebFilter equivalent?
**A:** `WebFilter` with Reactor `Context` — not thread-local MDC. Virtual-thread MVC still uses servlet filters for tracing. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Tenant A JWT sometimes authorizes tenant B data — only on async endpoints.

Filter stored tenant in `ThreadLocal`; async workers reused dirty threads. Fix: `TaskDecorator`, Micrometer context propagation, integration test across async boundary.

---

### 39. What is the Java Memory Model (JMM) at a usable level?

**Short answer:**
Without synchronization, compilers and CPUs reorder reads/writes. `volatile` gives visibility and ordering for one variable. `synchronized` and locks provide mutual exclusion and happens-before. `final` fields are safely published after construction. `java.util.concurrent` atomics use CAS + volatile semantics.

#### What it is
The JMM defines which values a thread may observe when another thread writes memory. JMM defines observable writes — not sequential consistency for all programs.

#### How it works (internals)
Happens-before edges: unlock→lock, volatile write→read, thread start/join, concurrent collection actions. Data races on non-volatile fields have undefined behavior for visibility. DCL singleton needs volatile instance field.

#### When to use / when NOT to use
Use concurrent utilities instead of DIY volatile flags for compound state. Document synchronization protocol for every shared field. Use `java.util.concurrent`; document invariants for raw fields.

#### Production example
Intermittent null in partially constructed singleton without volatile — classic JMM bug fixed by holder idiom or volatile. Config flag without volatile — stale feature toggles across pods until restart.

#### Common mistakes
'It works on my laptop' concurrency. Using volatile for i++. Ignoring safe publication when passing objects between threads.

#### Interview follow-ups (with model answers)

**Q:** Sequential consistency vs JMM?
**A:** Programmers assume global program order — JMM allows reorder without happens-before. `volatile`/`synchronized` create fences. `final` fields safe after ctor if `this` did not escape. Use j.u.c. instead of DIY reasoning. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** How does ConcurrentHashMap establish happens-before?
**A:** Internal sync — `put` happens-before `get` of same key for visibility of published object. Not for multi-key compound invariants. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** What is jcstress?
**A:** OpenJDK harness for concurrent algorithm outcomes under JMM. Library authors run it; product teams rarely unless building lock-free structures. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Rate limiter uses plain `boolean enabled` toggled from admin thread; requests read millions of times — limits ignored seconds after disable.

Missing happens-before — stale cache lines. Fix: `volatile` or `AtomicBoolean`; better immutable config snapshot via volatile reference. Stress-test, not unit-test alone.

---

### 40. `volatile` vs `AtomicInteger` vs `synchronized`.

**Short answer:**
`volatile` ensures visibility, not atomic read-modify-write. `AtomicInteger` uses CAS for atomic updates. `synchronized` provides exclusion and visibility for arbitrary critical sections. `LongAdder` beats `AtomicLong` under contention — stripes updates.

#### What it is
Three tools for shared mutable state with different scope and cost. volatile visibility; atomics CAS; synchronized multi-field invariants. volatile visibility; atomics CAS; synchronized multi-field invariants. volatile visibility; atomics CAS; synchronized multi-field invariants. volatile visibility; atomics CAS; synchronized multi-field invariants. volatile visibility; atomics CAS; synchronized multi-field invariants.

#### How it works (internals)
Shutdown flag: volatile boolean suffices. Counter under contention: `LongAdder` often beats `AtomicLong`. Complex invariants spanning fields: synchronized or lock.

#### When to use / when NOT to use
Simplest correct tool. Don't synchronize entire methods when a narrow block or atomic suffices. Narrowest tool: volatile flag, atomic counter, lock for compound state.

#### Production example
Metrics: `LongAdder` for request counts; volatile for config version flag read on every request. Global `AtomicLong` metrics — `LongAdder` cut CAS failures under burst.

#### Common mistakes
volatile for i++. synchronized for every getter on immutable cache. AtomicLong hot spot under 100 threads. synchronized on every getter of immutable cache. synchronized on every getter of immutable cache. synchronized on every getter of immutable cache. synchronized on every getter of immutable cache. synchronized on every getter of immutable cache.

#### Interview follow-ups (with model answers)

**Q:** LongAdder vs AtomicLong?
**A:** `LongAdder` stripes increments; `sum()` not atomic with concurrent updates — fine for metrics, wrong for strict accounting. Switch when JFR shows failed CAS on `AtomicLong`. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** When is synchronized faster than atomics?
**A:** Short low-contention sections with biased locking. Compound multi-field updates cheaper than CAS retry loops. Long synchronized blocks pin virtual threads — measure. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** VarHandle in application code?
**A:** Rare — off-heap rings, lock-free queues. Most services should not use VarHandle directly. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Fraud scoring uses shared `AtomicInteger` at 80k TPS — CPU on CAS failures, scores lag.

Hot atomic is coherence bottleneck. Fix: `LongAdder` shards or partition by customer in stream processor. Validate staleness acceptable for fraud use case.

---

### 41. Why is Double-Checked Locking hard, and how do you singleton correctly?

**Short answer:**
Without volatile on the instance field, another thread can see a partially constructed object after DCL. Correct: volatile instance + DCL, initialization-on-demand holder idiom, or enum singleton. In Spring, the container manages singleton scope. Prefer Spring singleton scope over hand-rolled DCL — testability wins.

#### What it is
DCL attempts lazy initialization with minimal synchronization. DCL without volatile publishes partially constructed object.

#### How it works (internals)
First check avoids locking after init. Second check inside lock creates the object. Without volatile, writes can be reordered exposing uninitialized fields. Holder idiom uses class initialization lock — lazy and simple.

#### When to use / when NOT to use
Prefer dependency injection over hand-rolled singletons. If truly needed, use enum or holder. Enum singleton for constants; DI for services.

#### Production example
Hand-rolled cache singleton caused rare NPE on field — volatile fixed. Spring `@Service` replaces entire pattern. SDK DCL without volatile — rare NPE on field; holder idiom patched.

#### Common mistakes
DCL without volatile. Enum singleton with mutable state. Testing nightmare with global singleton.

#### Interview follow-ups (with model answers)

**Q:** Explain Bill Pugh singleton.
**A:** Static nested `Holder` with `static final` instance — class init is JVM-synchronized, lazy, no hot-path sync. Preferred over hand DCL. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Enum singleton and serialization?
**A:** JVM guarantees single instance per enum constant on deserialization. Keep enums immutable. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Spring prototype vs singleton?
**A:** Singletons must be thread-safe. Prototype per injection is expensive if misused per request. Mis-scoped beans leak cross-tenant data in SaaS. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Licensing client DCL TCP pool — rare null parser delegate on multi-core K8s nodes.

Partial publication without volatile. Fix: holder idiom or Spring injection; startup health validates parser before traffic.

#### Code / config (when useful)
```java
private static class Holder {
    static final Config INSTANCE = new Config();
}
public static Config get() { return Holder.INSTANCE; }
```

---

### 42. SPI, ServiceLoader, and Spring factories.

**Short answer:**
SPI lets core APIs discover implementations at runtime via `META-INF/services`. `ServiceLoader` loads them lazily. JDBC drivers, charset providers, and logging bridges use SPI. Spring Boot uses `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` for auto-config — same discovery idea, different mechanism.

#### What it is
Service Provider Interface is a plugin architecture: interface in the API module, implementations on the classpath, discovered without hardcoding class names. SPI discovers implementations from classpath at runtime.

#### How it works (internals)
`ServiceLoader.load(MyService.class)` reads `META-INF/services/com.example.MyService` — one implementation class name per line. Instantiates via no-arg constructor. Spring Boot 3 lists `@Configuration` classes in `AutoConfiguration.imports`; Boot 2 used `META-INF/spring.factories`. `@ConditionalOnClass` / `@ConditionalOnProperty` gate which auto-config applies.

#### When to use / when NOT to use
- **SPI:** Library extension points (payment providers, export formats, codecs).
- **Spring auto-config:** Framework integration and starters.
- Don't use SPI when compile-time DI is sufficient.
- Debug missing beans with `--debug` or `ConditionEvaluationReport`. SPI for plugins; Spring `@Conditional` for auto-config.

#### Production example
Internal platform defines `PaymentGateway` SPI. Each bank integration JAR ships `META-INF/services/...PaymentGateway`. Runtime selects implementation by config without recompiling core. When a bean is missing after upgrade, check `AutoConfiguration.imports` and `@ConditionalOn*` predicates.

#### Common mistakes
- Missing `META-INF/services` file — `ServiceLoader` returns empty silently.
- Multiple providers without selection logic.
- Confusing Spring `@Autowired` wiring with SPI classpath discovery. Multiple providers without selection — nondeterministic order.

#### Interview follow-ups (with model answers)

**Q:** How does JDBC 4+ auto-load drivers?
**A:** `META-INF/services/java.sql.Driver` — `DriverManager` uses `ServiceLoader`. Missing JAR means ClassNotFoundException for driver class. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** spring.factories vs AutoConfiguration.imports?
**A:** Boot 3 `AutoConfiguration.imports` for faster startup. Missing entry — bean never loads; use `--debug` or `ConditionEvaluationReport`. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** JPMS `provides`/`uses` vs SPI?
**A:** Module `provides` stronger encapsulation than classpath SPI. Hybrid Boot apps rarely modularize app JAR but watch split packages. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Invoice service cannot find `TaxCalculator` SPI in prod; tests used all-in-one JAR.

Missing services file or plugin layer in image. Contract test `ServiceLoader.load` count; fail startup if zero required providers.

#### Code / config (when useful)
```java
ServiceLoader<PaymentGateway> loaders = ServiceLoader.load(PaymentGateway.class);
for (PaymentGateway gw : loaders) {
    if (gw.supports(currency)) return gw;
}
throw new IllegalStateException("No gateway for " + currency);
```

---

### 43. Modules (JPMS). Do Spring Boot apps use them?

**Short answer:**
JPMS (`module-info.java`) defines explicit `requires`, `exports`, and `opens` at compile and runtime. Most Spring Boot apps stay on the classpath as unnamed modules. You still feel JPMS because JDK 9+ encapsulates internal APIs — libraries using deep reflection need `--add-opens` or upgrades. Boot fat JARs stay unnamed modules — JPMS bites via encapsulated JDK APIs.

#### What it is
The Java Platform Module System adds strong encapsulation to the JDK and optional modular applications. It explains much of the friction migrating Spring apps to JDK 17+. JPMS: requires, exports, opens, optional jlink.

#### How it works (internals)
`module-info.java` declares dependencies and exported packages. Classpath JARs become the **unnamed module** — can read all exported JDK packages. **Split packages** (same package in two JARs) are illegal on the module path. `opens` grants reflective access for frameworks like Hibernate. `jlink` can build trimmed runtimes — rare for Spring monoliths.

#### When to use / when NOT to use
- **Modularize:** New libraries, CLI tools, custom JDK images.
- **Postpone:** Typical Spring Boot fat JAR on classpath.
- **Must understand:** `--add-opens`, `InaccessibleObjectException`, dependency upgrades.
- Document temporary opens in runbooks with removal tickets. Modularize libraries; postpone app module-info until deps clean.

#### Production example
Boot 3 on JDK 17 fails at startup: `InaccessibleObjectException: module java.base does not open java.lang.reflect`. Hibernate 5.x reflects into JDK internals. Fix: upgrade to Hibernate 6.x; interim `--add-opens java.base/java.lang.reflect=ALL-UNNAMED` in the deployment manifest with a dated removal task.

#### Common mistakes
- Blanket `--add-opens java.base/java.lang=ALL-UNNAMED` left in production forever.
- Adding `module-info.java` to the app while dependencies are not modular (split package hell).
- Assuming JPMS is required to run Java 17. App `module-info` with non-modular classpath — split package hell.

#### Interview follow-ups (with model answers)

**Q:** Named vs unnamed module?
**A:** Classpath JARs without module-info are unnamed — read exported JDK packages. Named modules have explicit boundaries. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** exports vs opens?
**A:** `exports` for API; `opens` for deep reflection (Hibernate). Precise `opens pkg to module` beats blanket opens. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Mix classpath and module path?
**A:** Yes — hybrid common. Wrong mix causes `module not found` or split package. jlink needs modular graph. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

jlink runtime for Boot CLI missing cglib — fat JAR on full JDK worked.

jlink omitted reflective deps. Use `jdeps` or ship full JRE for monoliths — jlink for small utilities only.

#### Code / config (when useful)
```bash
java --add-opens java.base/java.lang.reflect=ALL-UNNAMED \
     -jar myapp.jar
```

---

### 44. Records vs Lombok `@Value` vs JavaBeans.

**Short answer:**
Records are shallowly immutable value types with a canonical constructor, accessors, and generated `equals`/`hashCode`/`toString`. Lombok `@Value` is similar but annotation-processor based with weaker debugger support. JavaBeans are mutable with no-args constructors and setters — what JPA/Hibernate traditionally expect. Records use `name()` not `getName()` — align Jackson/MapStruct at boundaries.

#### What it is
Three patterns for data carriers at different layers: API/DTO (records), boilerplate reduction (Lombok), persistence/framework integration (beans). Records shallow immutable; Lombok compile-time; JavaBeans for JPA lifecycle.

#### How it works (internals)
Records: `final` class, `final` fields, accessor `name()` not `getName()`. Compact constructor validates invariants. Cannot extend classes (implicitly extend `Record`). Lombok generates methods at compile time — stack traces show synthetic code. JavaBeans: default ctor + setters so Hibernate can instantiate then hydrate from DB.

#### When to use / when NOT to use
- **Records:** REST request/response, Kafka events, command objects, map keys.
- **Lombok:** Teams already standardized on it for mutable services with builders.
- **JavaBeans / entities:** JPA entities with lifecycle and lazy loading.
- **Avoid:** Records as JPA entities without understanding Hibernate 6 limitations; `@Data` on entities with generated `equals`/`hashCode` on mutable collections. Records for DTOs/events; entities stay beans without lazy equals/hashCode.

#### Production example
REST API uses `record CreateOrderRequest(@NotNull String customerId, List<LineItem> items) {}` — Jackson deserializes via canonical constructor. JPA `OrderEntity` remains a JavaBean with `@Entity`, private setters, and Lombok `@Getter` only. Clear boundary between wire format and persistence model.

#### Common mistakes
- Mutable `List` in a record without `List.copyOf` in compact constructor.
- Expecting `getName()` on a record accessor.
- `@EqualsAndHashCode` on JPA entity including lazy `OneToMany` collection. `@Data` on entity with `OneToMany` in equals/hashCode.

#### Interview follow-ups (with model answers)

**Q:** Can records implement interfaces?
**A:** Yes — cannot extend classes (extend `Record`). Sealed interfaces + records for ADTs. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Jackson deserialize records?
**A:** 2.12+ canonical ctor — need `-parameters` or `@JsonProperty`. Test round-trip in contract tests. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Hibernate 6 records as entities?
**A:** Limited — prefer `@Embeddable`/projections. Root `@Entity` as record still experimental. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

DTO records cause Jackson `UnrecognizedPropertyException` on snake_case vs camelCase.

Align `@JsonNaming` or `@JsonProperty` when switching from Lombok beans. `FAIL_ON_UNKNOWN_PROPERTIES` in CI.

#### Code / config (when useful)
```java
public record Money(BigDecimal amount, Currency currency) {
  public Money {
    Objects.requireNonNull(amount);
    Objects.requireNonNull(currency);
    amount = amount.setScale(2, RoundingMode.HALF_UP);
  }
}
```

---

### 45. Sealed classes and pattern matching — why they matter in domain models.

**Short answer:**
Sealed classes restrict which types can extend them, enabling exhaustive `switch` with pattern matching. Combined with records, they model algebraic data types (sum types) in Java — replacing boolean flags, type codes, and visitor boilerplate for closed hierarchies like payment methods or workflow states. Sealed + exhaustive `switch` — compiler forces updates for new subtypes.

#### What it is
Sealed types (Java 17) plus pattern matching for `switch` (Java 21) bring ADT-style modeling to domain layers — the same expressiveness Scala/Rust developers take for granted. Closed extension — algebraic data types in Java.

#### How it works (internals)
```java
public sealed interface Payment permits CardPayment, WirePayment, WalletPayment {}
public record CardPayment(String last4) implements Payment {}
```
The compiler knows all permitted subtypes. `switch` without `default` can be exhaustive — adding `CryptoPayment` forces compile errors in every switch. Pattern matching deconstructs records: `case CardPayment(var last4) -> ...`.

#### When to use / when NOT to use
- **Use:** Closed domain variants (order states, AST nodes, notification channels).
- **Avoid:** Open plugin hierarchies meant for external extension — use interfaces + SPI instead.
- Prefer over `if (type.equals("CARD"))` string discriminators and giant if-else chains. Closed domains; SPI for open plugin extension.

#### Production example
Replace `OrderStatus` enum carrying optional fields with a sealed hierarchy: `record Shipped(TrackingNumber tracking) implements OrderState`. Fulfillment service uses exhaustive switch — compiler catches missing cases when a new `Cancelled` state ships. Pair with Jackson `@JsonSubTypes` for API serialization.

#### Common mistakes
- Forgetting `permits` clause or using `non-sealed` breaking exhaustiveness.
- Using sealed types for JPA entities Hibernate must subclass-proxy.
- Missing `@JsonSubTypes` — API deserialization breaks on polymorphic JSON. Missing `@JsonSubTypes` on sealed API types.

#### Interview follow-ups (with model answers)

**Q:** sealed vs final?
**A:** `final` forbids all subclasses. `sealed` permits listed only — controlled extension and exhaustiveness. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Pattern matching instanceof vs switch?
**A:** Switch patterns combine type test and deconstruction — exhaustive on sealed hierarchies. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** When is visitor still better?
**A:** Open hierarchies extended externally without recompiling core — visitor adds behavior without modifying types. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

`if (type.equals("PROMO"))` chains missed `LOYALTY_BUNDLE` in refunds — revenue leakage.

Migrate to sealed `PricingRule` + exhaustive switch + `@JsonSubTypes`. Mutation test pricing module.

#### Code / config (when useful)
```java
String label = switch (payment) {
    case CardPayment(var last4) -> "Card ending " + last4;
    case WirePayment(var iban)   -> "Wire " + iban;
    case WalletPayment w         -> "Wallet " + w.provider();
};
```

---

### 46. How do you find a memory leak in production Java?

**Short answer:**
Symptoms include climbing old gen or Metaspace, increasing GC frequency, and eventual OOM. Capture GC logs, heap dumps, and native memory summaries. Analyze with Eclipse MAT or VisualVM — dominator tree, leak suspects, paths to GC roots. Common culprits: unbounded caches, ThreadLocal, classloader leaks, listener lists, and off-heap buffers.

#### What it is
A Java "memory leak" means objects are unreachable from application code but still reachable from GC roots — they should have been collected but something retains them. Strong references retain 'dead' objects — GC cannot reclaim.

#### How it works (internals)
1. **Monitor:** heap/Metaspace trends, GC pause frequency, `jcmd VM.native_memory summary`.
2. **Capture:** `jcmd <pid> GC.heap_dump` or `-XX:+HeapDumpOnOutOfMemoryError`.
3. **Analyze:** dominator tree (what retains the most bytes), compare histograms over time, trace paths to GC roots.
4. **Classify:** cache, ThreadLocal, classloader, direct `ByteBuffer`, static collection. NMT separates Metaspace/direct from heap dominators.

#### When to use / when NOT to use
Set `HeapDumpOnOutOfMemoryError` and GC logging proactively. Don't restart immediately on OOM — capture the dump first. Bound caches with Caffeine (`maximumSize` + `expireAfterWrite`). Fix the reference, don't just raise `-Xmx`.

#### Production example
Old gen grows 100 MB/day; Full GC every hour. Heap dump shows 4 GB in a `ConcurrentHashMap` "temporary" report cache with no eviction. Fix: Caffeine `maximumSize(10_000).expireAfterWrite(1, HOURS)`. Separate incident: Metaspace leak from Groovy script engine reloading classes — fix by caching compiled scripts.

#### Common mistakes
- Increasing heap instead of fixing the retaining reference.
- Chasing heap when RSS growth is direct memory or Metaspace.
- Deleting dump files before analysis completes. Raise `-Xmx` on leaking cache.

#### Interview follow-ups (with model answers)

**Q:** Dominator tree vs histogram?
**A:** Histogram counts per class; dominator tree shows who retains bytes — follow to GC roots. MAT leak suspects automates patterns. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** ThreadLocal leak detection?
**A:** Long-lived pool threads retain ThreadLocal entries — `remove()` in finally. Async breaks thread affinity — avoid ThreadLocal for tenant. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** jmap vs jcmd heap dump?
**A:** `jcmd GC.heap_dump` preferred JDK 8+. Same user as JVM in containers. Multi-GB dumps need disk space. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

RSS +200 MB/day; heap flat after GC; Metaspace cap Friday night.

Classloader leak from dynamic scripts. NMT trace, cache compiled scripts, `MaxMetaspaceSize` alert below OOM.

#### Code / config (when useful)
```bash
-XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/var/log/heapdump.hprof
-Xlog:gc*:file=/var/log/gc.log:time,uptime,level,tags
jcmd <pid> GC.heap_dump /tmp/heap.hprof
```

---

### 47. How do you read a thread dump?

**Short answer:**
Capture with `jcmd Thread.print` or `jstack`. Classify threads: RUNNABLE (executing or in native code), BLOCKED (waiting for a monitor), WAITING/TIMED_WAITING (parks, joins, latches). Find lock chains and deadlocks. Pair with CPU profiling — RUNNABLE threads may be spinning, not making progress.

#### What it is
A thread dump is a point-in-time snapshot of every JVM thread's stack trace, state, and lock relationships — essential for deadlocks, pool exhaustion, and stuck I/O. Thread name, state, stack, locks — deadlocks and pool exhaustion.

#### How it works (internals)
Each thread entry shows name, state, stack frames, and lock info (`- locked`, `- waiting to lock`). The JVM prints a deadlock section when detected. Compare dumps 30 seconds apart: same stack on a RUNNABLE thread means stuck, not slow. `http-nio-*` blocked in `socketRead0` on JDBC points to pool or query issues. `ForkJoinPool` saturation suggests abusive `parallelStream()` or `CompletableFuture` defaults.

#### When to use / when NOT to use
Take dumps under load during an incident, not on an idle system. Capture three dumps spaced apart. Correlate with metrics: DB connection count, HTTP latency, pool active threads. Automate capture in Kubernetes via `kubectl exec` + `jcmd`.

#### Production example
API timeouts during checkout peak. Thread dump shows 180/200 `http-nio` threads in `socketRead0` waiting on the database; 20 BLOCKED on `HikariPool.getConnection`. Root cause: missing index on `orders(customer_id)` plus pool size 20. Fix: add index, set query timeout, cautiously tune pool — threads were waiting, not leaking.

#### Common mistakes
- Drawing conclusions from a single dump during a spike.
- Ignoring BLOCKED threads waiting on pool internal locks.
- Treating all RUNNABLE threads as healthy (CPU spin vs real work). Single dump during spike misread as deadlock.

#### Interview follow-ups (with model answers)

**Q:** Deadlock vs livelock?
**A:** Deadlock: circular lock wait — JVM may print deadlock section. Livelock: active retries without progress — needs backoff jitter. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Find lock holder?
**A:** Match `waiting to lock` and `locked` hex addresses in jstack. FastThread parses automatically. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Virtual threads in dumps?
**A:** `java.lang.VirtualThread` entries with carrier at bottom when mounted. Mass WAITING on JDBC may be pool wait, not deadlock. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

All APIs slow; CPU 20%; DB connections maxed; no deadlock in one dump.

Slow query holds pool — others BLOCKED in `getConnection`. Three dumps same stack. Kill query, index, timeouts. Dump + `pg_stat_activity`, not dump alone.

#### Code / config (when useful)
```bash
jcmd <pid> Thread.print > threaddump-$(date +%s).txt
# Linux: kill -3 <pid>  (SIGQUIT — also triggers dump)
```

---

### 48. What is "safe publication"?

**Short answer:**
Safe publication means another thread observing a reference sees the object fully constructed — not default field values or reordered writes. Mechanisms include static initializers, `volatile` references, synchronization, `final` fields (when `this` doesn't escape), and handing off via concurrent collections. Publication without happens-before — visibility bug separate from post-publication races.

#### What it is
Safe publication is a JMM concept: making a shared object visible to other threads together with the writes that constructed it. Unsafe publication is a visibility bug distinct from data races on already-published mutable fields. Readers must see fully constructed state with the reference.

#### How it works (internals)
Thread A constructs `Config`, assigns to a plain field. Thread B may read a non-null reference while `Config` fields still show default values — the reference was published before construction completed. Fixes establish **happens-before**: `volatile` write/read, `synchronized` unlock/lock, `ConcurrentHashMap.put`, `BlockingQueue.put`, static initializer. `final` fields are visible after ctor completes if `this` did not escape during construction.

#### When to use / when NOT to use
- Prefer **immutable objects** + safe publication over publishing mutable objects.
- Don't pass `this` from a constructor to another thread or event bus.
- Use `ExecutorService.submit()` for handoff — the queue provides happens-before.
- `volatile` reference swap for immutable config snapshots is a common pattern. No `this` escape from constructor.

#### Production example
A lazy cache publishes `HashMap` without synchronization — rare `null` values from partially visible `CacheEntry` objects under load. Fix: store an immutable `Map.copyOf` snapshot in a `volatile` field after building, or use `ConcurrentHashMap` from the start. Lazy `HashMap` cache without sync — rare null entries until volatile `Map.copyOf`.

#### Common mistakes
- Assuming "I assigned the field last in the constructor, so it's safe."
- `this`-escape in constructor (registering `this` with a bus before init completes).
- DCL singleton without `volatile`. Assume ctor final assignment is visible without volatile.

#### Interview follow-ups (with model answers)

**Q:** Happens-before and safe publication?
**A:** HB edge between construction writes and reader access: static init, volatile, synchronized, concurrent handoff, thread join. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Why final fields special?
**A:** Visible after ctor completes if `this` did not escape. Records rely on final components. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** this-escape example?
**A:** Ctor registers `this` on event bus before fields set — callback sees nulls. Use factory or `@PostConstruct`. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Config loader serves stale JDBC URLs after secret rotation — some threads only.

Unsafe publication of plain field. Fix: volatile immutable `Config` swap or `@RefreshScope`. Version metric per request detects skew.

#### Code / config (when useful)
```java
private volatile Config config;

void reload() {
    Config built = loadFully();  // construct completely first
    this.config = built;         // volatile write publishes safely
}
```

---

### 49. Annotation processing vs runtime annotations.

**Short answer:**
Annotations have retention policies: SOURCE (compile-only, e.g. Lombok), CLASS (bytecode only), RUNTIME (reflection-visible, e.g. Spring `@Component`). Annotation processors generate code at compile time — faster runtime, harder "where did this come from?" debugging. Runtime annotations power framework wiring at the cost of reflection (usually cached after startup).

#### What it is
Annotations attach metadata to code for compilers, bytecode tools, and runtime frameworks. Understanding retention and processing model explains missing generated code and mysterious bean creation. Annotations: SOURCE, CLASS, RUNTIME — different consumers.

#### How it works (internals)
`@Retention(RetentionPolicy.RUNTIME)` stores annotation data in class files for reflection. `SOURCE` is stripped after compile (Lombok rewrites AST). Annotation processors run in compiler rounds — MapStruct generates mapper implementations, Lombok generates getters. Spring scans the classpath at startup for `@Component`, `@Configuration`, `@Autowired`. `@Inherited` applies only to class-level annotations on subclasses, not to overridden methods.

#### When to use / when NOT to use
- **Compile-time (MapStruct, Immutables):** Type-safe mappers, less runtime cost.
- **Runtime (Spring, JPA, JAX-RS):** DI, ORM mapping, REST routing.
- Enable annotation processing in IDE and CI — builds can succeed in Maven but fail in IntelliJ without it.
- Don't use runtime reflection in inner loops when generation works. Compile-time mappers; runtime Spring/JPA wiring.

#### Production example
MapStruct `@Mapper` generates `OrderMapperImpl` at compile time — mapping is plain Java, fast, step-through debuggable. A teammate adds Lombok `@Slf4j` but IDE annotation processing is off — "cannot find symbol: log" locally while CI passes. Fix: enable annotation processing in IDE settings; document in README.

#### Common mistakes
- Expecting `@Transactional` on a private method to work (Spring AOP proxies need public methods on proxied beans).
- `@Data` on JPA entity generating `equals`/`hashCode` on lazy collections.
- Confusing Lombok SOURCE retention with runtime behavior. `@Transactional` on private method — proxy never intercepts.

#### Interview follow-ups (with model answers)

**Q:** How Spring finds @Component?
**A:** Classpath scanning ASM metadata at startup. Spring 6 context index speeds fat JAR. `@SpringBootApplication` enables scan. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Spring meta-annotations?
**A:** `@SpringBootApplication` composes `@Configuration`, `@EnableAutoConfiguration`, `@ComponentScan`. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** APT vs ByteBuddy?
**A:** APT generates source (MapStruct). ByteBuddy enhances at runtime (Hibernate proxies). APT easier to debug. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

`@Audited` AOP works in test slice, not deployed WAR.

Retention CLASS not RUNTIME, or pointcut missed module. Fix RUNTIME, component scan, integration test on WAR.

#### Code / config (when useful)
```java
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
public @interface Audited {
    String action() default "";
}
```

---

### 50. What Java skills separate 10-year engineers from 5-year?

**Short answer:**
Ten-year engineers reason about cost models (allocations, GC, syscalls), concurrency (JMM, real races), and operations (GC logs, heap dumps, JFR). They design APIs for immutability and clear failure modes, know library internals, and make migration judgments (8→17→21, Jakarta, virtual threads) with measured rollout — not blog-driven rewrites. Ten-year bar: connect memory, GC, JMM, ops in one incident narrative.

#### What it is
A meta-question about seniority signals: connecting language features to production behavior, team velocity, and incident response — not trivia recall. Seniority = cost models, failure stories, migration judgment, restraint.

#### How it works (internals)
**Five-year profile:** Knows APIs, Spring annotations, CRUD, basic collections Big-O.
**Ten-year profile:**
- **Cost model:** Allocations in hot paths, cache locality, when Big-O lies.
- **Concurrency:** Happens-before, why DCL broke, when CHM beats synchronized.
- **Operations:** GC logs, safepoint issues, Metaspace vs heap, thread dumps under fire.
- **Design:** Immutable DTOs, error boundaries, backward-compatible API evolution.
- **Restraint:** No custom collections, no parallel streams by default, no premature reactive rewrites.
- **Internals:** HashMap treeify, stream fusion, classloader leak patterns.
- **Migration:** javax→jakarta, `--add-opens`, virtual thread pinning assessment with JFR. JFR before guessing; bounded caches; idempotent APIs; measurable rollouts.

#### When to use / when NOT to use
Demonstrate depth with **failure stories** in interviews — "we had Metaspace OOM after redeploy" beats reciting definitions. Whiteboard HashMap + G1 pause + happens-before from one coherent incident. Avoid buzzword lists without trade-offs.

#### Production example
Candidate walks the panel through a production incident: parallel stream in a servlet saturated the common ForkJoinPool; thread dump showed blocked `http-nio` threads; fix was removing `parallel()` and pushing aggregation to SQL. Demonstrates cost model, ops tooling, and judgment — passes the staff loop. ForkJoinPool incident + thread dump + SQL fix beat collector trivia recitation.

#### Common mistakes
- Reciting API docs without trade-offs or failure modes.
- Claiming "Java is slow" without JFR evidence.
- Proposing reactive rewrites when virtual threads solve blocking I/O cheaper.
- Treating ops skills as "not my job." Buzzwords without 'what broke?' follow-up answers.

#### Interview follow-ups (with model answers)

**Q:** JVM production incident end-to-end?
**A:** Timeline: alert, ranked hypotheses, GC log/JFR/heap/thread dump, root cause, fix, guardrails. Numbers: p99, heap, pool wait. Weak: 'we restarted.' On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** JDK 21 virtual-thread rollout plan?
**A:** Baseline pinning JFR on 17. Staging load test JDBC/Redis blocking. Inventory synchronized/JNI. Canary AZ; separate thread vs DB scaling. Rollback documented. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Reject Hibernate for JDBC when?
**A:** Bulk ETL, streaming exports, pathological ORM SQL. JDBC behind repository. Reject JDBC-everywhere when domain needs persistence context — profiler decides. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Whiteboard how memory layout, GC choice, JMM, and leak hunt connect — not four definitions.

RSS rise → GC old gen growth → dump dominator cache via ThreadLocal → thread dump pool retention → JMM explains cross-pod stale visibility. Fix bounds, clear ThreadLocal, volatile config. Integration is the staff bar.

---

## Deep-dive additions (Q51–Q85)

These extend the core 50 with topics seniors must know: deep concurrency, Java 16–21 language features, NIO.2, JVM tooling, and packaging.

---

### 51. `ReentrantLock` vs `synchronized` — fairness, interruptibility, `tryLock`, `Condition`

**Short answer:**
`ReentrantLock` is an explicit lock from `java.util.concurrent.locks` offering fairness, interruptible acquisition, timed `tryLock`, and multiple `Condition` variables per lock — none of which `synchronized` provides. `synchronized` is cheaper in the uncontended path because the JVM biases and inflates monitors without a library object, and it releases on exception/return automatically so you cannot leak it. Use `ReentrantLock` only when you need one of its extra powers; otherwise prefer `synchronized` (or, on Java 21+, virtual-thread-friendly code that avoids `synchronized` on the hot path). The biggest production gotcha is forgetting to `unlock()` in `finally`.

#### What it is
`ReentrantLock` is a reentrant mutual-exclusion lock with the same memory semantics as `synchronized`, but exposed as a library class with extended semantics. `synchronized` is a JVM-level monitor built into every object; lock acquisition is implicit at the bytecode level (`monitorenter`/`monitorexit`). Both are reentrant — the holding thread can re-enter without deadlock, with a hold count.

#### How it works (internals)
`ReentrantLock` is backed by an `AbstractQueuedSynchronizer` (AQS): a CLH-variant wait queue of `Node`s parked with `LockSupport.park`. Fair mode (`new ReentrantLock(true)`) serves waiters FIFO; non-fair (default) lets a new arrival barge in, improving throughput. `lockInterruptibly()` throws `InterruptedException` if interrupted while waiting; `tryLock(time, unit)` times out. `Condition.newCondition()` returns a separate wait-set so you can signal specific predicates — `synchronized` has only one wait-set per monitor (`wait`/`notify`).

#### When to use / when NOT to use
Use `ReentrantLock` when you need: interruptible lock acquisition (cancellation), timed `tryLock` (deadlock avoidance in bounded backpressure), multiple `Condition` queues (producer/consumer with separate signals), or fairness. Use `synchronized` for simple critical sections, especially short and uncontended. On virtual threads, prefer `ReentrantLock` over `synchronized` if the section can block on I/O or another thread — `synchronized` pins virtual threads.

#### Production example
A Kafka consumer worker pool used `synchronized` on a shared offset commit path; one thread doing a 200 ms DB call pinned the virtual-thread carrier. Switching to `ReentrantLock` with `tryLock(5, SECONDS)` let callers fall back to a deferred commit queue instead of blocking — eliminating pinning JFR events and cutting p99 commit latency from 1.8 s to 90 ms. The fairness knob was unnecessary; non-fair throughput was 2× higher.

#### Common mistakes
- Calling `lock()` without a `try/finally unlock()` — guaranteed deadlock on first exception.
- Holding the lock across `condition.await()` without a `while` loop on the predicate (spurious wakeups).
- Using fair lock "to be nice" — throughput collapses under contention; prefer fair only when starvation is observed.
- Mixing `synchronized` and `ReentrantLock` on the same logical state — no happens-before between them.

#### Interview follow-ups (with model answers)

**Q:** Why does `synchronized` pin virtual threads but `ReentrantLock` does not?
**A:** `synchronized` is implemented in the JVM with a fixed carrier-thread association in HotSpot; a blocked monitor wait parks the platform carrier, which holds any virtual thread running on it. `ReentrantLock` parks via `LockSupport` on the virtual thread itself, freeing the carrier to run others. JFR `jdk.VirtualThreadPinned` events expose this. On Java 21, replace `synchronized` blocks that can hold across I/O or another thread with `ReentrantLock`, or restructure to keep critical sections CPU-only. The JIT can sometimes elide short `synchronized`, but never assume it for blocking calls. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** When is fair `ReentrantLock` actually worth it?
**A:** Rarely. Fair mode prevents barging but adds context-switch cost — measured 2–10× lower throughput under contention. Use it when starvation is observed in production (a thread stuck waiting while newer arrivals keep winning), in low-contention but latency-sensitive paths where worst-case matters more than average, or in protocols requiring strict ordering. Most servers want non-fair; the JVM's bias toward recent holders improves cache locality. If you reach for fair "to be safe," measure first. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

A trading gateway uses `synchronized` on an order book snapshot to serialize reads and writes. Under load, p99 read latency spikes to 400 ms with no GC pressure. Thread dumps show dozens of threads BLOCKED on the same monitor. What do you do?

Diagnosis: the lock is contended and held across a slow write path (network I/O to downstream exchange). Move to `ReentrantLock` with a `ReadWriteLock` semantics — or better, a `StampedLock` for optimistic reads — so readers don't block each other. Shorten the write critical section: snapshot the mutation, then publish via volatile reference, leaving I/O outside the lock. Add JFR pinning events to the canary. Validate with a load test reproducing 5k orders/s. If the write path is rare, copy-on-write snapshot + volatile publish eliminates the lock entirely. Document the trade-off: optimistic reads require validating the stamp and retrying on write — only acceptable if readers are idempotent.

#### Code / config (when useful)
```java
private final ReentrantLock lock = new ReentrantLock();
private final Condition notEmpty = lock.newCondition();

public T take() throws InterruptedException {
    lock.lockInterruptibly();
    try {
        while (queue.isEmpty()) notEmpty.await();
        return queue.poll();
    } finally {
        lock.unlock();
    }
}
```


### 52. `ReadWriteLock` vs `StampedLock` — optimistic reads, when stamped wins

**Short answer:**
`ReadWriteLock` allows many concurrent readers or one writer; reads block writes and each other acquire the read lock serially. `StampedLock` adds an **optimistic read** path: read without acquiring a lock, then validate a stamp; if no write happened, you read consistently with zero CAS overhead. `StampedLock` wins on read-heavy workloads (e.g., 100:1 read:write) where optimistic validation succeeds almost always. It is **not** reentrant — a thread holding the read lock cannot acquire the write lock — so it is unsuitable for general-purpose cache APIs that may re-enter.

#### What it is
Both are read/write locks allowing concurrent readers, exclusive writers. `ReentrantReadWriteLock` is reentrant, supports `Condition`, and is the safe default. `StampedLock` (Java 8) returns a `long` stamp on lock acquisition; optimistic reads call `tryOptimisticRead()` returning a stamp, do the read, then `validate(stamp)` — if validation passes, the read was consistent with respect to the latest write.

#### How it works (internals)
`ReentrantReadWriteLock` uses AQS with a single state int split into high 16 bits (reader count) and low 16 bits (writer count). First-reader optimization avoids CAS for the first reader. `StampedLock` uses a long state: a version counter (bits) plus a writer bit. Optimistic read works by reading the state twice — once before, once after the data read — and comparing. No acquire means no queue, no park. The cost is the validation must include memory barriers; on x86 this is cheap, on weakly-ordered ARM still cheap but ordered.

#### When to use / when NOT to use
Use `StampedLock` for read-mostly state with non-reentrant access — config snapshots, geographic data, market data caches. Use `ReentrantReadWriteLock` when you need reentrancy, `Condition`, or fairness, or when callers may upgrade read→write (which neither supports cleanly). Avoid `StampedLock` for write-heavy or 50/50 workloads — optimistic validation fails often, forcing fallback to pessimistic read which is slower than `ReentrantReadWriteLock`.

#### Production example
A reference-data service serves 50k reads/s vs 1 write/min. `ReentrantReadWriteLock` showed 30 µs read latency dominated by read-lock CAS contention. Switching to `StampedLock` optimistic reads dropped read latency to 3 µs (no CAS, just two volatile reads + validate). Validation failed 0.001% of the time, falling back to `readLock()`. The write path used `writeLock()` to publish a new immutable snapshot — readers never block.

#### Common mistakes
- Using `StampedLock` with reentrant code — deadlock on read→write upgrade.
- Forgetting to call `validate()` after optimistic read — silent torn reads.
- Holding the write lock across I/O — defeats the entire purpose.
- Treating `StampedLock` as a drop-in replacement — it lacks `Condition` and reentrancy.

#### Interview follow-ups (with model answers)

**Q:** What happens if `validate()` returns false?
**A:** The optimistic read saw a write in flight or just completed — your locally-read fields may be torn or stale. You must retry: either loop `tryOptimisticRead()` again, or escalate to `readLock()` for a pessimistic read. The pattern is `long stamp = lock.tryOptimisticRead(); ...read fields...; if (!lock.validate(stamp)) { stamp = lock.readLock(); try { ...read again... } finally { lock.unlockRead(stamp); } }`. Never act on unvalidated optimistic reads. In read-heavy workloads, fallback is rare (<0.1%) so the pessimistic cost is amortized. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Why is `StampedLock` not reentrant and why does that matter?
**A:** A reentrant read lock lets the same thread acquire it twice; `StampedLock` does not, so a method that takes the read lock and calls another method that also takes it deadlocks. This makes it unsafe for general-purpose APIs where callers may compose. The JDK designers chose non-reentrancy for performance — reentrancy requires per-thread reader counts, which costs CAS on every acquire. Use `ReentrantReadWriteLock` for composable APIs, `StampedLock` for tight internal hot paths. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Your FX rate cache uses `ReentrantReadWriteLock`. Reads are 10k QPS, writes once per second from a market data feed. Read latency is 50 µs; CPU is 70% on lock acquire. Walk through your optimization.

Replace with `StampedLock` optimistic reads. Validate against the stamp; on failure (write interleaved), retry optimistic or escalate to `readLock`. Writes use `writeLock()` to swap an immutable `Map` reference. Because the value is an immutable snapshot, readers don't need to copy. Measure: optimistic success rate, fallback rate, p99 read latency. Expected 10× read speedup. If writes were more frequent (10/s), validate failures would dominate — keep `ReentrantReadWriteLock`. Document: `StampedLock` is not reentrant; do not call any method from inside a read section that itself acquires the lock. Add a load test at 5× current QPS to confirm no regression. Track `jdk.Lock` JFR events.

#### Code / config (when useful)
```java
private final StampedLock lock = new StampedLock();
private volatile Map<String, Rate> rates = Map.of();

public Rate get(String ccy) {
    long stamp = lock.tryOptimisticRead();
    Map<String, Rate> snapshot = rates;
    if (!lock.validate(stamp)) {
        stamp = lock.readLock();
        try { snapshot = rates; }
        finally { lock.unlockRead(stamp); }
    }
    return snapshot.get(ccy);
}
```


### 53. `ThreadPoolExecutor` internals: queue types, rejection policies, sizing rules

**Short answer:**
`ThreadPoolExecutor` runs submitted tasks on a pool of worker threads, queueing when saturated and rejecting when the queue is full. The sizing rule `N = threads × utilization × (1 + wait/compute)` (Brian Goetz) gives the steady-state thread count for a given CPU target. The default `Executors.newFixedThreadPool` uses an unbounded `LinkedBlockingQueue` — it never rejects but silently absorbs unbounded backlog, a classic OOM vector. Production pools should always be constructed explicitly with a bounded queue, named threads, and a deliberate rejection policy.

#### What it is
A `ThreadPoolExecutor` has: a core pool size, a max pool size, a work queue, a thread factory, a keep-alive time, and a rejection handler. Submit order: if pool < core, start a new thread; else enqueue; if queue full and pool < max, start a new thread; else reject. The default `AbortPolicy` throws `RejectedExecutionException`; `CallerRunsPolicy` runs on the caller (backpressure); `DiscardPolicy` silently drops.

#### How it works (internals)
Workers live in a `HashSet<Worker>`; each `Worker` extends `AbstractQueuedSynchronizer` and wraps a thread. The queue is the bottleneck choice: `SynchronousQueue` for cached pools (hand-off, no buffering), `ArrayBlockingQueue` (bounded, array-backed, FIFO), `LinkedBlockingQueue` (optionally bounded, linked nodes, higher throughput), `PriorityBlockingQueue` (priority order). `beforeExecute`/`afterExecute` hooks allow tracing. Threads die after keep-alive idle if pool > core. `allowCoreThreadTimeOut(true)` lets core threads die too.

#### When to use / when NOT to use
Always construct `ThreadPoolExecutor` directly with bounded queue, named threads, and explicit rejection. Never use `Executors.newFixedThreadPool`/`newCachedThreadPool` in production — unbounded queues hide backpressure. For I/O-bound work, size using `N = target_utilization × cores × (1 + wait/compute)`; for pure CPU, `N ≈ cores`. For Java 21+ I/O, prefer virtual threads over a hand-tuned pool — they scale to millions.

#### Production example
A Spring `@Async` pool used `Executors.newFixedThreadPool(200)` with unbounded queue for inbound webhook fan-out. A downstream slowdown caused queue to grow to 2M tasks, heap to 6 GB, eventual OOM. Replaced with `ThreadPoolExecutor(50, 200, 60s, new ArrayBlockingQueue(2000), namedFactory, new CallerRunsPolicy())`. Caller-runs applied natural backpressure to the webhook ingress; p99 webhook latency degraded gracefully instead of OOM-killing the pod.

#### Common mistakes
- Using `Executors.newFixedThreadPool` — unbounded `LinkedBlockingQueue` hides backlog until OOM.
- Sizing CPU-bound pools at 4× cores "for safety" — context switches dominate.
- `DiscardPolicy` silently dropping tasks in a payment pipeline.
- Not naming threads — thread dumps are useless when everything is `pool-3-thread-7`.

#### Interview follow-ups (with model answers)

**Q:** Derive the Goetz thread-sizing formula.
**A:** For steady state, CPU utilization = (busy threads × compute_time) / (total threads × (compute_time + wait_time)). Solving for threads to hit a target utilization U: `N = U × cores × (1 + wait/compute)`. If a request does 50 ms compute and 150 ms DB wait, on 8 cores at 80% utilization: `N = 0.8 × 8 × (1 + 150/50) = 0.8 × 8 × 4 = 25.6`. This is a starting point; measure with JFR and tune. The formula assumes uniform tasks; mixed workloads need separate pools. On virtual threads, you don't size for I/O wait — the JVM handles it. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** When is `CallerRunsPolicy` the right choice?
**A:** When the submitter is the right place to apply backpressure — typically an ingress thread that can slow down without cascading failure. Caller-runs blocks the submitter, naturally throttling upstream. It's wrong when the submitter is a critical thread that must not block (e.g., a Kafka poll thread — it will hit `max.poll.interval.ms` and rebalance). For async pipelines, prefer `Abort` with retry to a dead-letter queue, or a custom handler that publishes to Kafka. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

A payment service has 8 cores, requests do 20 ms CPU + 180 ms DB call. You're asked to size the request thread pool. Walk through it.

Apply Goetz: `N = 0.9 × 8 × (1 + 180/20) = 0.9 × 8 × 10 = 72`. But HikariCP maxPool is 20 — 72 threads competing for 20 connections means 52 threads block on the pool, wasting stacks. Two options: (1) cap threads at Hikari size + small slack (25), accept lower CPU utilization; (2) raise Hikari to 72 if DB can handle it (check DB CPU). On Java 21, virtual threads eliminate the dilemma — millions of VTs share the 20 connections, blocking cheaply. Validate with JFR: measure actual wait/compute, not estimates. Document: the formula is a starting point; the real constraint is the downstream resource (DB connections, downstream HTTP pool). Add a load test at 2× expected QPS.

#### Code / config (when useful)
```java
new ThreadPoolExecutor(
    50, 200, 60, TimeUnit.SECONDS,
    new ArrayBlockingQueue<>(2000),
    new ThreadFactoryBuilder().setNameFormat("webhook-%d").build(),
    new ThreadPoolExecutor.CallerRunsPolicy());
```


### 54. `CompletableFuture` composition: `thenCompose` vs `thenCombine`, `allOf`/`anyOf`, exception handling

**Short answer:**
`CompletableFuture` is the JDK's composable future: `thenCompose` flattens nested futures (monadic bind, sequential async deps), `thenCombine` zips two futures into one value, `allOf` waits for all (returns `void`, you reduce results yourself), `anyOf` returns the first to complete. Exceptions propagate through the pipeline unless you handle them with `handle` (can recover and produce a value), `exceptionally` (catch-only recovery), or `whenComplete` (side-effect, cannot replace the value). The classic mistake is using `thenApplyAsync` everywhere, which adds queueing overhead without parallelism.

#### What it is
A `CompletableFuture<T>` is a future you can both complete and chain on. Unlike `Future.get()` (blocking poll), you register callbacks that fire when the result is ready. Composition methods return new futures, forming a DAG. The default async executor is the common `ForkJoinPool` — fine for CPU work, wrong for blocking I/O.

#### How it works (internals)
Each stage holds a `Completion` graph; on completion, dependent stages are triggered. `thenCompose(fn)` calls `fn` returning another `CompletableFuture`, then flattens — equivalent to `flatMap`. `thenCombine(other, biFn)` waits for both, applies the bi-function. `allOf(cf...)` completes when all complete (or one fails); to collect results you map over the inputs. `anyOf(cf...)` completes with the first result (or first failure). Exceptions short-circuit downstream unless a handler intercepts; `handle((value, ex) -> ...)` transforms both; `exceptionally(ex -> ...)` only catches; `whenComplete((v, ex) -> ...)` observes without changing the result.

#### When to use / when NOT to use
Use `CompletableFuture` for fan-out/fan-in of independent async calls (e.g., calling 3 microservices in parallel and merging). Always pass an explicit executor for blocking I/O — never rely on the common pool for DB/HTTP calls. Avoid deep `CompletableFuture` chains; they become unreadable and stack-trace-unfriendly. For structured, cancellable concurrency on Java 21, prefer `StructuredTaskScope`.

#### Production example
An order enrichment service calls customer, inventory, and pricing services in parallel. `CompletableFuture.allOf(customerFuture, inventoryFuture, pricingFuture).thenApply(...)`. The pricing call occasionally fails; `exceptionally(ex -> fallbackPrice)` returns a cached price instead of failing the whole order. p99 enrichment dropped from 300 ms (sequential) to 110 ms (parallel). Explicit `ForkJoinPool.commonPool()` was replaced with a bounded HTTP executor to avoid starving other common-pool users.

#### Common mistakes
- Using `thenApplyAsync` for CPU-only transforms — extra queueing cost, no parallelism gain.
- Forgetting `exceptionally`/`handle` — one failure fails the whole pipeline and propagates as `CompletionException`.
- Blocking on `cf.get()` inside a `CompletableFuture` chain — defeats the purpose; use `thenCompose`.
- Relying on the common `ForkJoinPool` for blocking I/O — saturates and starves parallel streams.

#### Interview follow-ups (with model answers)

**Q:** `thenCompose` vs `thenApply` — what's the difference?
**A:** `thenApply` takes a `Function<T, U>` and returns `CompletableFuture<U>` — synchronous transform, like `map`. `thenCompose` takes `Function<T, CompletableFuture<U>>` and returns `CompletableFuture<U>` — it flattens, like `flatMap`. Use `thenCompose` when the next step is itself async (returns a future); otherwise you get `CompletableFuture<CompletableFuture<U>>`. This is the monad bind operation. Most pipelines mix both: `thenApply` for CPU transforms, `thenCompose` for async deps. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** How do you handle partial failures in `allOf`?
**A:** `allOf` completes exceptionally if any input fails — you lose all results. To tolerate partial failure, wrap each future with `exceptionally(ex -> null)` or a sentinel, then collect. Or use `anyOf` for first-success semantics. For "wait for all, collect successes, log failures," use a custom collector over the input futures with per-future `handle`. `StructuredTaskScope` on Java 21 makes this explicit: `ShutdownOnSuccess` vs `ShutdownOnFailure` policies. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

A checkout service calls 4 promo services in parallel via `CompletableFuture.allOf`. One promo service has 5% error rate; the whole checkout fails 5% of the time. How do you fix it?

Wrap each promo call with `.handle((promo, ex) -> ex != null ? Promo.empty() : promo)` so failures degrade to "no promo" instead of failing checkout. If a promo is required, mark it as such and only wrap optional ones. Add a per-service timeout with `orTimeout(500, MS)` so a slow promo doesn't stall checkout. Log failures with a counter so you can alert on rising error rates. Validate with chaos test: kill one promo pod, verify checkout still succeeds. Document the degradation contract with the business — "no promo" must be acceptable. On Java 21, consider `StructuredTaskScope.ShutdownOnFailure` for cleaner cancellation semantics.

#### Code / config (when useful)
```java
CompletableFuture<Order> order = CompletableFuture
    .supplyAsync(this::fetchCustomer, httpPool)
    .thenCombine(CompletableFuture.supplyAsync(this::fetchInventory, httpPool),
                (c, i) -> new Order(c, i))
    .exceptionally(ex -> { log.warn("enrich failed", ex); return Order.empty(); });
```


### 55. `CountDownLatch` vs `CyclicBarrier` vs `Phaser` — one-shot vs reusable vs tree

**Short answer:**
`CountDownLatch` is a one-shot gate: N threads count down, others await; once zero, never resets. `CyclicBarrier` is reusable: N threads await at the barrier, all released together, then it resets for the next round. `Phaser` is the most general: supports dynamic parties, tree structure (sub-phasers), and per-phase registration. Pick `CountDownLatch` for "wait for N initialization steps," `CyclicBarrier` for "N workers sync between rounds," `Phaser` for variable participation or hierarchical parallel algorithms.

#### What it is
All three are `java.util.concurrent` synchronization primitives. `CountDownLatch` is initialized with a count; `countDown()` decrements, `await()` blocks until zero. `CyclicBarrier` is initialized with a party count; `await()` blocks until N threads reach it, then all proceed; optionally runs a barrier action. `Phaser` supports `register()`/`arriveAndDeregister()`, multiple phases (numbered), and tree composition via `Phaser(parent)`.

#### How it works (internals)
`CountDownLatch` uses AQS with a shared state = count; `await` parks until state reaches 0. `CyclicBarrier` uses a `ReentrantLock` + `Condition` and a generation flag to handle reset; the last arrival runs the barrier action and signals waiters. `Phaser` uses a state long with bits for phase, parties, arrived, and unarrived; supports bulk operations and tree-based coordination for fork-join style parallelism.

#### When to use / when NOT to use
`CountDownLatch`: service startup waiting for config, schema, and pool ready. `CyclicBarrier`: parallel simulation rounds where all workers must sync. `Phaser`: rare — when parties join/leave dynamically (e.g., recursive divide-and-conquer). Avoid `Phaser` for simple cases; its API is complex and easy to misuse. For "wait for all of N async results," prefer `CompletableFuture.allOf` or `StructuredTaskScope`.

#### Production example
A batch job runs 8 worker threads in rounds; each round all workers process a partition then sync to swap buffers. `CyclicBarrier(8, () -> swapBuffers())` cleanly handles this. Earlier the team used a `CountDownLatch` re-instantiated each round — race-prone and slow. A startup service uses `CountDownLatch(3)` for config, schema, and pool readiness; main thread awaits, then opens the health check. `Phaser` was used once for a variable-arity recursive parser.

#### Common mistakes
- Reinstantiating `CountDownLatch` each round — use `CyclicBarrier`.
- Calling `countDown()` in a `finally` that may not be reached — latch never reaches zero.
- Using `Phaser` when `CyclicBarrier` suffices — over-engineering.
- Not handling `InterruptedException` from `await()` — swallowed interrupts break cancellation.

#### Interview follow-ups (with model answers)

**Q:** Why is `CountDownLatch` not resettable?
**A:** It's a one-shot gate by design — AQS state is monotonic. The use case is "wait for N initialization events," not repeated synchronization. Resetting would require a separate coordination primitive, which is what `CyclicBarrier` is. The asymmetry is intentional: `CountDownLatch` is for one-to-many (one initializer signals many waiters) or many-to-one (many workers signal one waiter); `CyclicBarrier` is for peer-to-peer (N peers sync). On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** When does `Phaser` actually earn its complexity?
**A:** When parties dynamically join or leave — recursive fork-join algorithms, tree-structured parallelism where sub-tasks have their own synchronization, or when you need phase numbers to coordinate multi-step protocols. `Phaser` supports `register()` mid-phase and `arriveAndAwaitAdvance()` returning the phase number. For fixed-party round-based sync, `CyclicBarrier` is simpler and faster. Most production code never needs `Phaser`; if you reach for it, justify with a concrete dynamic-participation example. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

A service must wait for: schema migration, Kafka consumer assignment, and a warm-up cache load before accepting traffic. Walk through the synchronization design.

Use `CountDownLatch(3)` initialized at startup; each subsystem calls `countDown()` in its ready callback. The HTTP server's `await()` blocks with a 60 s timeout — if it elapses, fail fast and let Kubernetes restart the pod. Don't use `CyclicBarrier` — these are not peer workers syncing; they're independent one-shot events. Add a startup health check that returns 503 until the latch is zero, so the load balancer doesn't route traffic to an unready pod. Log each `countDown` with timing so you can identify which subsystem is slow. On Java 21, `StructuredTaskScope` could model this as concurrent sub-tasks with shutdown-on-failure, but `CountDownLatch` is simpler for one-shot readiness.


### 56. `Semaphore` as rate limiter and DB connection gate

**Short answer:**
A `Semaphore` maintains N permits; `acquire()` blocks until one is available, `release()` returns one. It's the simplest way to bound concurrent access to a resource — DB connections, outbound HTTP to a rate-limited API, or a thread pool substitute. Unlike a fixed thread pool, a semaphore lets you reuse existing threads (e.g., servlet threads) and just gate how many can pass. `tryAcquire(timeout)` is non-blocking and ideal for backpressure. Permits are not tied to threads — any thread can release a permit acquired by another, which is powerful but easy to misuse.

#### What it is
`Semaphore(int permits)` and `Semaphore(int permits, boolean fair)` create a counting semaphore. `acquire()` decrements, blocking if zero; `release()` increments. Fair mode serves waiters FIFO. `tryAcquire()` returns immediately; `tryAcquire(timeout, unit)` waits. `acquireUninterruptibly()` ignores interrupts.

#### How it works (internals)
`Semaphore` is built on AQS shared mode. State = permit count. `acquire` is `acquireSharedInterruptibly(1)`: if state ≥ 1, decrement; else park in the AQS queue. `release` increments and signals the head waiter. Fair mode checks the queue first; non-fair lets a new acquirer barge. Permits are just integers — there's no concept of "ownership" (unlike locks), so a release without a matching acquire is legal and increases available permits.

#### When to use / when NOT to use
Use as a bounded concurrency gate for blocking calls reusing existing threads (e.g., Tomcat threads calling a rate-limited downstream). Use as a poor-man's rate limiter when paired with a scheduled refill (token bucket). Don't use as a substitute for connection pools — HikariCP does connection lifecycle, validation, and leak detection; a semaphore only counts. Don't release without acquiring in a `finally` — that increments permits beyond the bound.

#### Production example
A payment gateway calls a bank API with a 50 RPS limit. A `Semaphore(50)` plus a scheduled task that refills permits every 100 ms (5 permits per refill) implements a token bucket. Each request acquires a permit before calling the bank; `tryAcquire(2, SECONDS)` returns 503 with a Retry-After header on timeout. This is far cheaper than a full rate-limiter library and survives bank-side rate changes via config. p99 gateway latency stayed under 200 ms while raw RPS was capped cleanly.

#### Common mistakes
- `release()` in a `finally` without a matching `acquire()` — inflates permits.
- Using non-fair semaphores when starvation is observed — switch to fair.
- Treating permits as "owned" — they aren't; any thread can release.
- Not pairing with a timeout — indefinite `acquire()` cascades failures.

#### Interview follow-ups (with model answers)

**Q:** How would you build a token bucket rate limiter with a `Semaphore`?
**A:** Initialize `Semaphore(capacity)` where capacity is the bucket size. A scheduled task refills permits at the rate (e.g., 50 per second) by calling `release(rate)` — but cap so permits never exceed capacity. Callers `tryAcquire(1)` before doing the rate-limited work; on failure, return 429/503 with Retry-After. For multi-instance, this only limits per-pod; you need a Redis-based limiter (e.g., Redisson, Lua script with INCR + EXPIRE) for global limits. The semaphore approach is good for single-pod protection of downstream services. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Why use a `Semaphore` instead of just a bounded thread pool?
**A:** A thread pool owns the threads; if you already have a servlet container with 200 threads, you don't want another pool. A semaphore lets you reuse those 200 threads but cap how many can pass through to a downstream resource — e.g., 20 concurrent calls to a slow API. It also lets you gate non-thread resources (file handles, DB connections in legacy code). Thread pools are better when you need queueing, rejection, and lifecycle management; semaphores are better when you have threads and just need a count. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Your Spring MVC service has 200 Tomcat threads. A new feature calls a slow partner API; you want to cap concurrent partner calls at 20 without spawning a separate thread pool. Design it.

Inject a `Semaphore(20)` bean. In the controller method, `if (!sem.tryAcquire(2, SECONDS)) return ResponseEntity.status(503).header("Retry-After", "2").build();` then `try { return callPartner(); } finally { sem.release(); }`. This caps concurrent partner calls at 20, reuses Tomcat threads, and applies backpressure via 503. Add a metric `partner_concurrent` and `partner_rejected` to track utilization. If 503s rise, partner is slow — add a circuit breaker (Resilience4j) so repeated failures fail fast. Validate with a load test: 200 concurrent requests, expect 20 to proceed and 180 to wait or 503 after 2 s. Document: the semaphore does not queue retries; clients must retry with jitter.


### 57. `ThreadLocal` — leaks in app servers, `InheritableThreadLocal`, when `ScopedValue` (Java 21) replaces it

**Short answer:**
`ThreadLocal` stores per-thread state — useful for non-thread-safe objects reused across calls (e.g., `SimpleDateFormat`) or request-scoped context. The classic leak: thread pools outlive requests, so `ThreadLocal` values survive indefinitely, holding classloaders and causing Metaspace OOM on hot redeploy. `InheritableThreadLocal` propagates to child threads but is unreliable with pools (children inherit the creator's value, not the submitter's). Java 21's `ScopedValue` (preview, stable in 22+) is the modern replacement: immutable, bounded lifetime, automatically cleaned up, and safe for virtual threads.

#### What it is
`ThreadLocal<T>` is a per-thread map keyed by the `ThreadLocal` instance. `get()`/`set()` access the current thread's value. `InheritableThreadLocal` copies parent values to child threads at construction. `ScopedValue` (JEP 446, 21 preview → 23 stable) is a value bound for the duration of a `ScopedValue.where(v, x).run(() -> ...)`, automatically unbound when the run completes.

#### How it works (internals)
Each `Thread` has a `ThreadLocalMap` (open-addressing hash table) referencing `ThreadLocal` weak keys and strong values. The leak: the value strongly references a classloader, the `ThreadLocal` key is weakly held, but if the entry survives (thread pool), the classloader is retained. `InheritableThreadLocal` uses a separate map consulted at thread construction. `ScopedValue` stores values in a thread's `ScopedValueBindings` stack; bindings are pushed/popped, so lifetime is bounded and immutable — no per-thread map pollution.

#### When to use / when NOT to use
Use `ThreadLocal` for genuinely per-thread reusable state (formatters, byte buffers) with explicit cleanup. Never use for request-scoped context in a thread pool — leaks. Use `ScopedValue` for request-scoped immutable context (tenant ID, trace ID, principal) on Java 21+. For passing context to async tasks, prefer explicit parameters or `ScopedValue` over `ThreadLocal` (which doesn't propagate across executors anyway).

#### Production example
A legacy service used `ThreadLocal<UserContext>` in a Tomcat thread pool; after redeploy, heap dumps showed thousands of `WebappClassLoader` instances retained by stale `ThreadLocal` entries. Fix: replace with request-scoped bean (Spring `RequestScope`) and clear in a `finally` filter. On Java 21+, migrate to `ScopedValue` for the trace ID and tenant context — no leak risk, virtual-thread friendly. Metaspace stabilized at 80 MB vs climbing to 500 MB.

#### Common mistakes
- `ThreadLocal` in a thread pool without `remove()` in `finally`.
- Using `InheritableThreadLocal` to propagate request context to async tasks — it doesn't work with executors.
- Storing mutable shared objects in `ThreadLocal` — defeats isolation.
- Using `ThreadLocal` where a method parameter would do — hidden coupling.

#### Interview follow-ups (with model answers)

**Q:** Why does `ThreadLocal` leak in app servers and how do you fix it?
**A:** Thread pools outlive requests; `ThreadLocal` values set during a request survive in the thread's `ThreadLocalMap`. The value references a classloader (e.g., a request-scoped bean), which references loaded classes — Metaspace grows until OOM. Fix: call `remove()` in a `finally` filter at request end; use `RequestScope` beans instead; or migrate to `ScopedValue` whose bounded lifetime auto-cleans. Detect with MAT classloader-leak report or `jcmd VM.classloader_stats`. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Why does `ScopedValue` replace `ThreadLocal` for request context?
**A:** `ScopedValue` is immutable and bounded — bound it for a `run`, it's automatically unbound on exit, no manual `remove()`. It's safe for virtual threads (no per-thread map pollution) and supports nested bindings cleanly. `ThreadLocal` is mutable, unbounded, and leaks in pools. `ScopedValue` does NOT replace `ThreadLocal` for reusable per-thread objects (formatters, buffers) — those are genuinely per-thread state. For request-scoped immutable context (trace, tenant, principal), `ScopedValue` is the modern choice. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Your service uses `ThreadLocal<TraceId>` set in a servlet filter. After migrating to virtual threads, you notice trace IDs leak across requests intermittently. Diagnose.

Virtual threads are pooled by the carrier; a `ThreadLocal` set on a virtual thread is per-virtual-thread, so it shouldn't leak — unless you're using `InheritableThreadLocal` or setting it on the carrier. More likely: the filter's `finally` doesn't call `remove()` on an exception path, and the virtual thread is reused (it isn't, but the symptom suggests platform-thread code). Migrate to `ScopedValue.where(TRACE_ID, id).run(() -> filterChain.doFilter(...))` — bound for the request, auto-cleaned, no `remove()` needed. Verify with a load test that mixes trace IDs and asserts no cross-contamination. Document: `ScopedValue` is immutable; if you need to update the trace ID mid-request (rare), use a `ScopedValue` of a mutable holder.


### 58. Virtual-thread pinning: `synchronized` blocks, JNI, `Object.wait` — detect with `jfr` and fix with `ReentrantLock`

**Short answer:**
Virtual threads pin their carrier platform thread when they block inside `synchronized`, during JNI calls, or in `Object.wait()`. While pinned, the carrier can't run other virtual threads, defeating the scalability win. JFR emits `jdk.VirtualThreadPinned` events with the stack; `-Djdk.tracePinnedThreads=true` logs full stacks on first pin. Fix by replacing `synchronized` with `ReentrantLock` on hot paths, avoiding JNI in the blocking section, or using `LockSupport`-based primitives. Pinning is not fatal — it's a perf cliff under contention.

#### What it is
A pinned virtual thread is bound to its carrier; the JVM cannot unmount it to schedule another virtual thread on that carrier. Pinning happens in three cases: (1) `synchronized` block/method, (2) JNI native frames on the stack, (3) `Object.wait()`. While pinned, the carrier is blocked, so the effective virtual-thread concurrency drops to the carrier count.

#### How it works (internals)
HotSpot's virtual-thread scheduler (a work-stealing `ForkJoinPool` of carrier threads) unmounts a virtual thread at blocking points by parking it via `Continuation.yield`. `synchronized` uses monitor inflation tied to the carrier thread, so the JVM cannot yield inside it. JNI frames have native state the JVM can't relocate. `Object.wait` releases the monitor but the wait queue is tied to the carrier. `ReentrantLock` uses `LockSupport.park` on the virtual thread directly, so it can yield cleanly.

#### When to use / when NOT to use
Always audit for pinning before deploying virtual threads in production. Replace `synchronized` on hot I/O paths with `ReentrantLock`. For native code, ensure the JNI call doesn't span a blocking wait. Pinning in cold paths (e.g., startup) is acceptable. Use `-Djdk.tracePinnedThreads=short` in staging to catch the worst offenders.

#### Production example
A service migrated to virtual threads saw throughput plateau at 2k req/s instead of the expected 10k. JFR `jdk.VirtualThreadPinned` showed 95% of carriers pinned inside `synchronized` on a `BufferedReader` wrapper. Replacing with `ReentrantLock` in the wrapper (or unwrapping to use `Reader` directly) lifted throughput to 9k req/s. The pinning events dropped from 100/s to 0.1/s.

#### Common mistakes
- Deploying virtual threads without a pinning audit.
- Assuming `synchronized` on a "fast" path is safe — it's safe for correctness but pins.
- Ignoring JNI in legacy libraries (e.g., Zip, crypto) that block.
- Treating pinning as a bug — it's a perf characteristic; measure before fixing.

#### Interview follow-ups (with model answers)

**Q:** How do you detect virtual-thread pinning in production?
**A:** Enable JFR with `jdk.VirtualThreadPinned` events — they fire on every pin with the stack trace. For staging, `-Djdk.tracePinnedThreads=short` logs the first N pins to stderr. In production, JFR with a low threshold (`-XX:StartFlightRecording=filename=...,settings=profile`) captures pins without measurable overhead. Filter events by stack to find the worst offenders. A pin rate > carriers × 10/s is a red flag. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** When is pinning acceptable?
**A:** When the pinned section is short and uncontended — a `synchronized` block that does a few field reads is pinned for microseconds, negligible. Pinning matters when the section blocks on I/O, network, or another thread. JNI calls that return quickly (e.g., a hash computation) are fine; JNI that blocks (e.g., a native HTTP call) is not. `Object.wait` is rare in modern code. The rule: pinning in CPU-only sections is fine; pinning across blocking calls is the problem. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

After migrating to virtual threads, your HTTP client throughput is 3k req/s on 4 carriers; you expected 12k. JFR shows pins in `synchronized` on a `Socket.getInputStream()` wrapper. Walk through the fix.

The wrapper synchronizes on `this` to guard a shared buffer; under virtual threads, this pins. Replace `synchronized` with `ReentrantLock` — same semantics, no pinning. If the wrapper is third-party, switch to the JDK's `HttpClient` (built for virtual threads) or unwrap. Validate: re-run the load test, expect 12k req/s. Add a JFR-based regression alert on pin rate. Document: pinning is not a correctness bug; the wrapper still works, just slowly. For new code, prefer `HttpClient` over `HttpURLConnection` on virtual threads. If you can't remove the wrapper, bound its use to a non-virtual-thread pool.

#### Code / config (when useful)
```text
# JFR pinning audit
-XX:StartFlightRecording=filename=pin.jfr,settings=profile,maxsize=200m
-Djdk.tracePinnedThreads=short   # staging only
```


### 59. `StructuredTaskScope` (Java 21) — shutdown-on-failure, structured concurrency vs `CompletableFuture`

**Short answer:**
`StructuredTaskScope` (JEP 453, preview in 21, stable in 24+) is the modern alternative to `CompletableFuture` for fan-out work. You open a scope, fork subtasks, then join — the scope guarantees all subtasks complete (or are cancelled) before the block exits. `ShutdownOnFailure` cancels remaining subtasks when any fails; `ShutdownOnSuccess` returns the first success and cancels the rest. The win: lifetimes are lexically scoped, cancellation is automatic, and the call stack reflects the concurrency structure — unlike `CompletableFuture`'s unbounded DAG.

#### What it is
A `StructuredTaskScope<T>` is a try-with-resources construct. Inside, `scope.fork(() -> ...)` starts a virtual thread running the task. `scope.join()` waits for all to finish; `scope.shutdown()` cancels all. Policies: `ShutdownOnFailure` (join throws if any failed, cancels rest), `ShutdownOnSuccess` (returns first success, cancels rest). Subtasks return `Subtask<T>` with `get()` after join.

#### How it works (internals)
Each `fork` creates a virtual thread tied to the scope. The scope tracks outstanding subtasks. On `shutdown`, the scope interrupts all unfinished subtasks. `join` blocks until all subtasks reach a terminal state. The scope's lifetime is bounded by the try-with-resources block, so leaked subtasks are impossible — if the block exits, all subtasks are cancelled. This is the "structured concurrency" principle: dynamic extent = concurrency extent.

#### When to use / when NOT to use
Use `StructuredTaskScope` for fan-out/fan-in of independent calls where you want automatic cancellation and clear lifetimes. Use `CompletableFuture` for long-lived pipelines, callbacks, or when you need to compose results without blocking. `StructuredTaskScope` requires virtual threads (it forks virtual threads), so it's a Java 21+ feature. For simple parallel calls with explicit cancellation, it's clearer than `CompletableFuture`.

#### Production example
A checkout service forks 4 enrichment calls (customer, inventory, pricing, promo) inside a `ShutdownOnFailure` scope. If pricing fails, the scope cancels the others — no wasted work, no leak. With `CompletableFuture.allOf`, a failure leaves the other calls running until they complete or fail. The structured version reads top-to-bottom, mirrors the call stack, and makes cancellation automatic. p99 stayed the same, but the cancellation cleanup eliminated 200ms of wasted downstream calls on partial failures.

#### Common mistakes
- Forking platform-thread-blocking work — `StructuredTaskScope` is designed for virtual threads.
- Forgetting `join()` before reading `Subtask.get()` — throws.
- Using `ShutdownOnSuccess` when you actually need all results.
- Treating it as a drop-in for `CompletableFuture` — different model, no callbacks.

#### Interview follow-ups (with model answers)

**Q:** `StructuredTaskScope` vs `CompletableFuture` — when each?
**A:** `StructuredTaskScope` for bounded fan-out with automatic cancellation and clear lifetimes — the call stack reflects the structure, and a failure cancels siblings. `CompletableFuture` for long-lived pipelines, callback chains, or when you compose results without blocking (e.g., returning a future from a service). `StructuredTaskScope` requires virtual threads; `CompletableFuture` works on any executor. For new code on Java 21+, prefer `StructuredTaskScope` for "do these N things in parallel and combine"; prefer `CompletableFuture` for "build a pipeline of async stages." On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** How does `ShutdownOnFailure` propagate cancellation?
**A:** When a subtask fails, the policy calls `scope.shutdown()`, which interrupts all other subtasks. Virtual threads respond to interruption at blocking points (I/O, sleep, park). If a subtask is mid-CPU work, it continues until the next blocking point — interruption is cooperative. The scope's `join()` then throws `ExecutionException` wrapping the first failure. The try-with-resources block ensures the scope is closed even if `join` throws. This is cleaner than `CompletableFuture.cancel(true)` which only marks the future cancelled, not the underlying work. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

A product-detail service calls 5 microservices in parallel. With `CompletableFuture.allOf`, a slow inventory call delays the whole response; the team wants to fail fast if any call exceeds 500 ms. Design with `StructuredTaskScope`.

Open a `ShutdownOnFailure` scope with a 500 ms deadline (use `scope.joinUntil(Instant.now().plusMillis(500))`). Fork each call as a subtask. If any fails or the deadline hits, the scope shuts down remaining subtasks. After join, check each `Subtask.state()` — `SUCCESS` to read the result, `FAILED` for the exception, `UNAVAILABLE` for cancelled-by-shutdown. Return a partial response if business allows, or fail the request. Add per-call timeouts as defense in depth. Validate with chaos: kill one service, verify the scope cancels others within 50 ms. Document: `joinUntil` throws `TimeoutException` if the deadline hits; catch and shut down explicitly.

#### Code / config (when useful)
```java
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    Subtask<Customer> c = scope.fork(() -> fetchCustomer(id));
    Subtask<Inventory> i = scope.fork(() -> fetchInventory(id));
    scope.joinUntil(Instant.now().plusMillis(500));
    return new Product(c.get(), i.get());
}
```


### 60. `@Contended` and false sharing — cache lines, `@Contended` padding, when it matters

**Short answer:**
False sharing occurs when two threads write to different variables that happen to live on the same CPU cache line (typically 64 bytes). Each write invalidates the other core's cache, causing cache-line ping-pong and dramatic slowdown — 10× or more on hot counters. `@Contended` (JDK 8u, `jdk.internal.vm.annotation.Contended`) pads the field with empty bytes so it occupies its own cache line. It's only useful for hot, write-heavy fields shared across cores — counters in `LongAdder`-style code, disruptor sequences, JCTools queues. Most code doesn't need it; misapplying it just wastes memory.

#### What it is
A CPU cache line is 64 bytes on most x86/ARM. If two fields share a line and are written by different cores, each write invalidates the other's cached copy — the line bounces between caches even though the threads don't logically share data. `@Contended` tells the JVM to pad the field to a full cache line, isolating it. `LongAdder` uses this internally with its `Cell` array.

#### How it works (internals)
`@Contended` on a field adds ~128 bytes of padding before and after (configurable via `-XX:RestrictContended`). Without `-XX:-RestrictContended` (default on), only trusted JDK classes get padding; user code needs `-XX:-RestrictContended` or the annotation is a no-op. Padding is per-instance for instance fields, per-class for static. The JVM lays out objects with padding gaps. False sharing is detected by perf counters (`perf c2c` on Linux) or by JFR cache-event profiling.

#### When to use / when NOT to use
Use `@Contended` only for hot, write-heavy fields contended across cores — high-throughput counters, ring-buffer sequences, lock-free queue heads/tails. Don't use for read-mostly fields, single-threaded state, or low-throughput counters — `AtomicLong` is fine. Measure before and after; if you can't show a perf delta, remove it. Most application code never needs it.

#### Production example
A metrics library used `AtomicLong` for a request counter on a 32-core service doing 200k req/s. The counter showed 40% CPU in `perf c2c` due to false sharing. Switching to `LongAdder` (which uses `@Contended` cells internally) dropped counter CPU to 2%. The same fix applies to custom ring buffers — padding the producer and consumer sequence fields eliminated 30% of cache misses in a Disruptor-style queue.

#### Common mistakes
- Applying `@Contended` without `-XX:-RestrictContended` — silently no-op.
- Padding read-only fields — no benefit, wasted memory.
- Using it on every field of a class — defeats the purpose; only hot fields matter.
- Not measuring — false sharing is often a red herring.

#### Interview follow-ups (with model answers)

**Q:** How do you detect false sharing in production?
**A:** On Linux, `perf c2c` shows cache-line transfers between cores — high HITM (hit-modified) on a line indicates false sharing. JFR with `perf` integration can correlate. A simpler heuristic: a hot counter shows disproportionate CPU vs the rest of the method, and removing the counter drops CPU. Or pad the field with 7 longs before/after and measure — if perf jumps, it was false sharing. `LongAdder` is the standard fix for counters. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Why does `@Contended` need `-XX:-RestrictContended` for user code?
**A:** Padding wastes memory (128 bytes per padded field per instance), so the JDK restricts it to trusted classes by default. User code must opt in with `-XX:-RestrictContended` (or the equivalent module-open flag on modularized code). Without it, the annotation is silently ignored. This is a footgun — the code compiles and runs but gets no padding. For libraries, document the flag requirement. For most apps, prefer `LongAdder` (already padded internally) over hand-rolling `@Contended`. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Your high-throughput order processor uses a custom ring buffer with `volatile long producerSeq` and `volatile long consumerSeq` as adjacent fields. At 1M ops/s on 16 cores, throughput plateaus at 300k. Diagnose.

False sharing: the two sequence fields share a cache line, and the producer and consumer cores invalidate each other's cache on every write. Pad them: declare 7 `long` padding fields (or use `@Contended` with `-XX:-RestrictContended`) between and around the sequences. Expected 3–5× throughput gain. Better: use JCTools' `MpscArrayQueue` or LMAX Disruptor, which already pad. Validate with `perf c2c` showing reduced HITM. Document: padding is per-instance, so a single shared ring buffer benefits; per-request buffers don't need it. Add a regression test that asserts throughput under contention.


### 61. `WeakHashMap` vs `IdentityHashMap` vs `EnumMap` — when each, performance

**Short answer:**
`WeakHashMap` keys are weakly held — entries vanish when the key is GC'd, useful for canonicalizing auxiliary data attached to objects you don't own. `IdentityHashMap` uses `==` instead of `equals()` — for object-graph traversal, serialization, and any case where distinct instances must stay distinct even if `equals` says they're the same. `EnumMap` is a specialized `Map` for enum keys — a flat array indexed by enum ordinal, 2–10× faster and far smaller than `HashMap`. Pick by intent: canonicalization → weak, identity → serialization/cycle detection, enum → always prefer `EnumMap` over `HashMap` for enum keys.

#### What it is
`WeakHashMap` extends `AbstractMap` with `WeakReference` keys; entries are eligible for GC when the key is no longer strongly reachable. `IdentityHashMap` uses `System.identityHashCode` and `==` — it deliberately violates `Map`'s general contract (which requires `equals`). `EnumMap` is an array-backed map keyed by a single enum type — O(1) get/put with no hashing.

#### How it works (internals)
`WeakHashMap` maintains a `ReferenceQueue` of cleared keys; on each operation it expunges stale entries. The value is held strongly, so if the value references the key, you have a self-loop preventing GC — use `WeakReference` on the value or a separate canonicalization structure. `IdentityHashMap` is an open-addressing table with linear probing, no `hashCode` calls. `EnumMap` has a `K[]` keys array of size `enum.values().length` and a `boolean[]` has-flags, plus a `V[]` values — zero hashing, zero collisions.

#### When to use / when NOT to use
`WeakHashMap`: attach metadata to objects you don't control (e.g., classloader → stats). `IdentityHashMap`: serialization, deep-copy cycle detection, object-graph algorithms where `equals` would coalesce distinct nodes. `EnumMap`: any time keys are enum — it's strictly better than `HashMap`. Never use `IdentityHashMap` as a general-purpose map — its `equals` semantics break `Map` contracts.

#### Production example
A serialization framework used `HashMap` for cycle detection — coalesced equal-but-distinct objects caused incorrect graphs. Switching to `IdentityHashMap` fixed it. A config system used `HashMap<MyEnum, Config>` — switching to `EnumMap` cut 60% of the map's memory and 3× faster lookups in a hot path. A monitoring agent used `WeakHashMap<ClassLoader, Stats>` to attach stats without preventing classloader GC — clean shutdown of dynamic apps.

#### Common mistakes
- Using `WeakHashMap` for caching — entries vanish under memory pressure unpredictably; use Caffeine.
- `WeakHashMap` value referencing the key — prevents GC; use a weak value or restructure.
- `IdentityHashMap` as a general map — breaks `equals` contract.
- `HashMap<Enum, ...>` when `EnumMap` is available — wasteful.

#### Interview follow-ups (with model answers)

**Q:** Why is `WeakHashMap` a poor cache?
**A:** Entries are reclaimed when the key is GC'd, which is unpredictable — under memory pressure, all entries may vanish; under no pressure, they linger forever. Caches need explicit size and TTL policies, which `WeakHashMap` doesn't provide. Use Caffeine with `maximumSize` and `expireAfterWrite`. `WeakHashMap` is appropriate for canonicalizing auxiliary data tied to an object's lifetime (e.g., a per-classloader stats map), not for caching results. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Why is `EnumMap` faster than `HashMap` for enum keys?
**A:** `EnumMap` indexes a flat array by the enum ordinal — get/put is `values[ordinal]`, no hashing, no collisions, no equals. `HashMap` hashes the enum (constant hashCode, but still computes bucket), probes, and calls `equals` (enum `equals` is `==`, fast but still a branch). `EnumMap` also uses ~50% less memory (no `Node` objects, no resize). For hot paths with enum keys, the speedup is 2–10×. Always prefer `EnumMap` when keys are a single enum type. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

A config service stores per-environment settings keyed by `Environment` enum in a `HashMap`. The hot path does 500k lookups/s. How do you optimize, and what are the trade-offs?

Switch to `EnumMap<Environment, Settings>`. Lookups drop from ~30 ns (hash + equals) to ~5 ns (array index). Memory drops from ~200 bytes (HashMap with 4 entries) to ~80 bytes. No trade-offs — `EnumMap` is strictly better for enum keys. If the map is constructed once and read concurrently, `EnumMap` is not thread-safe; wrap in `CopyOnWriteArrayList`-style or use a volatile reference to an immutable snapshot. If keys are a mix of enums (rare), you can't use `EnumMap` — fall back to `HashMap`. Add a JMH benchmark to confirm the gain. Document: `EnumSet` is the analogous win for enum sets.


### 62. `PriorityQueue` vs `ArrayDeque` — heap vs ring buffer, `Deque` contract

**Short answer:**
`PriorityQueue` is a binary heap — `offer`/`poll` are O(log n), ordered by `Comparator`/natural ordering; the head is always the smallest. `ArrayDeque` is a circular array — `offer`/`poll` are O(1) amortized, FIFO or LIFO (it implements `Deque`). Use `PriorityQueue` when you need ordering (top-k, scheduler, Dijkstra); use `ArrayDeque` when you need a queue or stack with O(1) ops and don't care about ordering. `ArrayDeque` is also the modern replacement for `Stack` (which extends `Vector` and is synchronized overhead).

#### What it is
`PriorityQueue<E>` is an unbounded priority queue backed by a growable array arranged as a min-heap (or max-heap with reversed comparator). `ArrayDeque<E>` is a resizable circular array implementing `Deque` — supports both ends in O(1). Neither is thread-safe; use `PriorityBlockingQueue` or `ConcurrentLinkedDeque` for concurrency.

#### How it works (internals)
`PriorityQueue` sifts up on insert (compare with parent, swap), sifts down on poll (compare with children, swap) — O(log n). No indexing by priority; iteration order is undefined (not sorted). `ArrayDeque` maintains `head` and `tail` indices into a circular array; doubles in size when full. No shifting on add/remove at ends — just index arithmetic mod length. Memory: `ArrayDeque` is a single array of objects; `PriorityQueue` is a single array but with heap-ordering overhead.

#### When to use / when NOT to use
`PriorityQueue`: top-k streaming, scheduler by deadline, A* / Dijkstra. `ArrayDeque`: BFS queue, stack (use `addFirst`/`pollFirst`), work-stealing local queue. Don't use `PriorityQueue` if you need sorted iteration — use a `TreeSet`. Don't use `ArrayDeque` for `null` elements (it rejects them). Don't use `Stack` (legacy, synchronized).

#### Production example
A rate-limited scheduler uses `PriorityQueue<Task>` ordered by next-run time; `poll` returns the next due task in O(log n). A work queue for a single-threaded worker uses `ArrayDeque<Job>` — FIFO with O(1) ops, no comparator overhead. The team replaced `Stack<Frame>` with `ArrayDeque` (used as a stack via `addLast`/`pollLast`) — eliminated synchronization overhead from `Stack`'s `Vector` parent.

#### Common mistakes
- Iterating `PriorityQueue` expecting sorted order — it's not; use `TreeSet` or sort a list.
- Using `ArrayDeque` for `null` elements — throws NPE.
- Using `Stack` (legacy synchronized) instead of `ArrayDeque` as a stack.
- Adding to `PriorityQueue` with a `Comparator` that changes — heap invariant breaks.

#### Interview follow-ups (with model answers)

**Q:** Why is iterating a `PriorityQueue` not sorted?
**A:** The heap invariant only guarantees the head is the minimum — the rest of the array is in heap order (parent ≤ children), not sorted order. Iteration walks the underlying array, which is heap-ordered, not sorted. If you need sorted iteration, use a `TreeSet` (O(log n) iteration in order) or collect to a list and sort. For "give me the top-k," poll k times from `PriorityQueue` — that's O(k log n), correct. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** When is `ArrayDeque` better than `LinkedList` as a queue?
**A:** `ArrayDeque` is a circular array — O(1) ops, no per-element node allocation, better cache locality. `LinkedList` is a doubly linked list — O(1) ops but each `add` allocates a `Node` (more GC pressure, worse cache behavior). `ArrayDeque` is faster in nearly all cases. `LinkedList` wins only when you need to remove from the middle (rare for a queue) or when you need stable iterators. For BFS, work queues, and stacks, `ArrayDeque` is the default. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

You need a top-10 leaderboard updated 1M times/s from a stream of scores. Walk through the design.

Use a `PriorityQueue<Integer>` of size 10 as a min-heap. For each score: if size < 10, offer; else if score > peek (the current min of top-10), poll then offer. Each op is O(log 10) ≈ O(1). For 1M/s, this is fine single-threaded. For parallelism, shard by score range or use a `ConcurrentSkipListMap` if you need concurrent updates. Don't use a sorted list — O(n) insert. Don't use a `TreeSet` if scores can duplicate — `TreeSet` dedupes; use a heap with a count or a `TreeMap<Integer, Integer>` (count per score). Validate with a load test. Document: the heap holds the top-10; iteration is not sorted, so for display, sort the 10 elements.


### 63. Concurrent queues: `LinkedBlockingQueue` vs `ArrayBlockingQueue` vs `SynchronousQueue` vs `DelayQueue`

**Short answer:**
`ArrayBlockingQueue` is a bounded array-backed FIFO — single `ReentrantLock` for producers and consumers; allocation-free; ideal when you need a hard bound. `LinkedBlockingQueue` is a linked-node FIFO — separate locks for head and tail (higher throughput under contention), but each `offer` allocates a `Node`. `SynchronousQueue` has zero capacity — each `put` blocks for a matching `take` (hand-off); used by `cachedThreadPool`. `DelayQueue` orders by delay — elements become available after their `getDelay` elapses; used for scheduled retries and TTL-based eviction. Pick by backpressure, throughput, and allocation profile.

#### What it is
All four implement `BlockingQueue` and are thread-safe. `ArrayBlockingQueue(int)` is bounded; `LinkedBlockingQueue` is optionally bounded (default `Integer.MAX_VALUE` — dangerous). `SynchronousQueue` is a zero-capacity rendezvous channel. `DelayQueue<E extends Delayed>` blocks on `take` until the earliest-delayed element is due.

#### How it works (internals)
`ArrayBlockingQueue` uses one `ReentrantLock` + two `Condition` (notFull, notEmpty) — producers and consumers contend on the same lock, but no allocation. `LinkedBlockingQueue` uses two locks (putLock, takeLock) — producers and consumers proceed in parallel, but each `offer` allocates a `Node`. `SynchronousQueue` uses transferer (dual stack or queue) — `put` finds a waiting `take` or blocks. `DelayQueue` uses a `PriorityQueue` ordered by `getDelay`; the leader thread waits on the earliest due, others wait — avoids thundering herd.

#### When to use / when NOT to use
`ArrayBlockingQueue`: bounded producer-consumer with allocation pressure concerns. `LinkedBlockingQueue`: high-throughput unbounded or large-bound queue where allocation is OK. `SynchronousQueue`: hand-off semantics, no buffering (e.g., direct hand-off executors). `DelayQueue`: scheduled retries, TTL caches, deadline schedulers. Always bound `LinkedBlockingQueue` in production — unbounded hides backpressure.

#### Production example
A Kafka consumer used `LinkedBlockingQueue` unbounded for in-flight work — under downstream slowdown, queue grew to 1M, heap to 8 GB, OOM. Replaced with `ArrayBlockingQueue(1000)` — bounded, allocation-free, backpressure to the consumer. A retry scheduler used `DelayQueue<RetryTask>` — each task's `getDelay` returns time until next attempt; a single consumer thread polls, sleeps until due, and re-enqueues with exponential backoff. `SynchronousQueue` was used for a direct-handoff executor — each submit blocks for an idle worker.

#### Common mistakes
- Unbounded `LinkedBlockingQueue` — hides backlog until OOM.
- Using `SynchronousQueue` with a fixed pool — `submit` blocks until a worker is free; can deadlock.
- `DelayQueue` with a single consumer and many due-at-once tasks — thundering herd; use the leader pattern (built-in).
- Comparing `DelayQueue` elements by `equals` — it uses `getDelay` ordering, not `equals`.

#### Interview follow-ups (with model answers)

**Q:** Why does `ArrayBlockingQueue` use one lock but `LinkedBlockingQueue` uses two?
**A:** `ArrayBlockingQueue` is a contiguous array — head and tail indices can interleave, so a single lock is simpler and avoids corruption. `LinkedBlockingQueue` is a linked list — head and tail are independent nodes, so separate locks allow producers and consumers to operate in parallel, boosting throughput under contention. The cost: each `offer` allocates a `Node`. For high-throughput unbounded queues, `LinkedBlockingQueue` wins; for bounded, allocation-sensitive, or low-contention, `ArrayBlockingQueue` wins. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** How does `DelayQueue` avoid the thundering herd on a due element?
**A:** The leader-follower pattern: the first thread to find a due element becomes the leader and waits on a `Condition` for its delay; other threads wait on a separate `available` signal. When the leader takes the element, it signals the next thread, which becomes the new leader. This means only one thread is waiting on the head at a time — no thundering herd. The implementation is in `DelayQueue.take()`. For custom schedulers, this is the right pattern; rolling your own with a `PriorityQueue` and `notifyAll` will herd. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Your retry service uses a `ScheduledExecutorService` but retries are dynamic (added at runtime with computed delays). The team wants a queue-based design. Walk through it.

Use `DelayQueue<RetryTask>` where `RetryTask implements Delayed`. `getDelay(unit)` returns `nextAttemptTime - now` in the requested unit. `compareTo` orders by `nextAttemptTime`. A single consumer thread calls `take()` (blocks until due), processes, and if more retries remain, re-enqueues with `nextAttemptTime = now + backoff`. For high throughput, use N consumer threads — `DelayQueue` handles concurrent `take` via leader-follower. Bound the queue (subclass or wrap) to prevent unbounded growth under poison-message scenarios. Add a metric on queue depth and due-rate. Validate with a chaos test: enqueue 10k retries at staggered delays, verify no herd and no missed retries. Document: `DelayQueue` is not a scheduler replacement for fixed-rate tasks; use `ScheduledExecutor` for those.


### 64. `Map.computeIfAbsent` / `merge` / `putIfAbsent` — atomic ops, the cache pattern and its recursion trap

**Short answer:**
`putIfAbsent(k, v)` atomically puts only if absent. `computeIfAbsent(k, fn)` atomically computes and inserts if absent, returning the value. `merge(k, v, remappingFn)` atomically combines the existing value with `v` via the remapping function, or inserts `v` if absent. All three are atomic on `ConcurrentHashMap` (per-bin lock) but not on `HashMap` (no concurrency guarantee). The cache pattern: `map.computeIfAbsent(key, this::loadFromDb)`. The recursion trap: if `loadFromDb` mutates the same map (e.g., recursively loads related keys), `ConcurrentHashMap` throws `IllegalStateException` because the bin is locked during computation; `HashMap` may corrupt.

#### What it is
These are default methods on `Map` (Java 8+) providing atomic get-then-put semantics. On `ConcurrentHashMap`, they're truly atomic (bin-locked). On `HashMap`, they're not thread-safe but still avoid the get-check-put race in single-threaded code. `merge` is the most general — it handles both insert and update with one function.

#### How it works (internals)
`ConcurrentHashMap.computeIfAbsent` locks the bin, checks for the key, calls the function, inserts, releases. The bin lock means the function must not modify the same bin — recursive `computeIfAbsent` on the same key throws `IllegalStateException("Recursive update")`; on a different key in the same bin, it deadlocks in older JDKs (fixed in 9+). `merge` is similar but the function receives the existing value and the new value. `putIfAbsent` is the simplest — no function call, just a value.

#### When to use / when NOT to use
Use `computeIfAbsent` for lazy-cache initialization, `merge` for counters/aggregations, `putIfAbsent` for simple defaults. Avoid the recursive-cache trap: if the loader mutates the map, use a separate `ConcurrentHashMap` or load first, then put. For high-contention caches, prefer Caffeine (which handles loading, eviction, and refresh without these traps).

#### Production example
A counter service used `merge(key, 1L, Long::sum)` on a `ConcurrentHashMap` — atomic increments across threads, no `synchronized`. A cache used `computeIfAbsent(id, this::loadUser)` — clean lazy loading. A bug: `loadUser` called `computeIfAbsent` on the same map for related users, occasionally throwing `IllegalStateException`. Fix: load related users outside the function, or use a separate cache. Replacing with Caffeine `loadingCache` eliminated the trap and added TTL/size bounds.

#### Common mistakes
- Recursive `computeIfAbsent` on the same map — `IllegalStateException` or deadlock.
- Using `computeIfAbsent` on `HashMap` from multiple threads — not atomic.
- `merge` with a function that returns `null` — removes the entry (surprising).
- `computeIfAbsent` returning `null` — does not insert (avoids null values), but returns null.

#### Interview follow-ups (with model answers)

**Q:** Why does `ConcurrentHashMap.computeIfAbsent` throw on recursive update?
**A:** The bin is locked during the function call; if the function calls `computeIfAbsent` on the same bin, it would re-enter the lock — `ReentrantLock` allows re-entry, but the JDK explicitly detects this and throws `IllegalStateException("Recursive update")` to prevent infinite loops and inconsistent state. For nested loads (loading a user loads related users), use a separate map, or load outside the function. Caffeine's `LoadingCache` handles this correctly because it locks per-entry, not per-bin. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** When does `merge` return null and what happens?
**A:** If the remapping function returns null, `merge` removes the key from the map (treating it as "no longer needed"). This is by spec — `merge` is for combining, and a null result signals removal. If you want to keep a zero value (e.g., a counter that goes to 0), return the value, not null. For counters, `merge(key, 1L, Long::sum)` is safe — `Long::sum` never returns null. The trap is custom remappers like `(old, n) -> old == 0 ? null : old + n` — this removes the entry when the counter hits 0. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

A request-scoped counter uses `ConcurrentHashMap<String, Long>` with `merge(key, 1L, Long::sum)`. Under load, you see occasional `Long` values exceeding 1M for a key that should be at most 1k. Diagnose.

`merge` is atomic per key, so values can't exceed the actual count unless the map is being shared across requests (not request-scoped) or the same logical counter is being incremented from multiple requests. Check: is the map a static field or a shared bean? If so, it's accumulating across requests. Fix: scope the map per request (e.g., a `RequestScope` bean or a `ThreadLocal`/`ScopedValue`). If the count is genuinely high, add logging to see who increments. Also check: is `merge` being called with a non-atomic remapper that re-reads the map? `Long::sum` is fine; custom lambdas that read the map again are not. Validate with a unit test that increments 1k times from 10 threads and asserts the final value.

#### Code / config (when useful)
```java
// Atomic counter
counts.merge(key, 1L, Long::sum);

// Lazy cache (avoid recursion!)
cache.computeIfAbsent(id, this::loadUser);
```


### 65. `Spliterator` — `tryAdvance`/`forEachRemaining`, `IMMUTABLE`/`CONCURRENT` characteristics, parallel streams

**Short answer:**
A `Spliterator<T>` is the internal iteration primitive behind streams — it lets the stream pipeline pull elements one at a time (`tryAdvance`) or in bulk (`forEachRemaining`), and split itself in two for parallel processing (`trySplit`). Characteristics like `IMMUTABLE`, `CONCURRENT`, `NONNULL`, `SORTED`, `SIZED` tell the stream what optimizations are safe. `CONCURRENT` means the source is thread-safe under concurrent modification; `IMMUTABLE` means it won't change at all. A `HashSet` spliterator is `DISTINCT` + `SIZED`; a `ConcurrentHashMap` spliterator is `CONCURRENT` + `NONNULL`. Parallel streams split the spliterator recursively (fork-join) — bad splitting (e.g., linked list) kills parallel speedup.

#### What it is
`Spliterator` is the iterator's spiritual successor — designed for internal iteration and parallel decomposition. `tryAdvance(consumer)` processes one element, returns false if exhausted. `forEachRemaining(consumer)` processes all (bulk). `trySplit()` returns a new spliterator for the left half, leaving the right for `this`. `estimateSize()` and `characteristics()` guide optimization.

#### How it works (internals)
Parallel streams use `trySplit` recursively until the spliterator is small (below the threshold), then `forEachRemaining` each chunk on a `ForkJoinPool` worker. Good spliterators (arrays, `ArrayList`) split evenly — O(1) per split, balanced trees. Bad spliterators (`LinkedList`, `Stream.iterate`) split poorly — one side is empty or tiny, parallelism is wasted. `IMMUTABLE` lets the stream skip synchronization; `CONCURRENT` allows concurrent modification without `ConcurrentModificationException`; `SIZED` lets `collect` pre-size the result.

#### When to use / when NOT to use
Implement `Spliterator` for custom collections or data sources (e.g., a database cursor that pages). Use characteristics honestly — lying breaks stream optimizations or causes races. Avoid parallel streams on `LinkedList`, `Stream.iterate`, `BufferedReader.lines` — splitting is poor. For CPU-bound work on a sized source, parallel streams can win; for I/O or small data, sequential is faster.

#### Production example
A custom `ResultSetSpliterator` for a JDBC cursor used `IMMUTABLE` + `NONNULL` and split by row-range, enabling parallel stream processing of a 10M-row export. The team measured 4× speedup on 8 cores vs sequential. A bug: a `LinkedList` parallel stream was 2× slower than sequential — switching to an `ArrayList` (or `Stream.of(list.toArray())`) fixed it. A `ConcurrentHashMap` source used `CONCURRENT` correctly, allowing a parallel stream during writes.

#### Common mistakes
- Parallel stream on `LinkedList` or `Stream.iterate` — poor splitting.
- Lying about `SIZED` — `collect` pre-sizes wrong, resizes.
- `IMMUTABLE` on a mutable source — race conditions.
- Using parallel streams for I/O — saturates the common pool, starves other parallel work.

#### Interview follow-ups (with model answers)

**Q:** Why is a parallel stream on a `LinkedList` slow?
**A:** `LinkedList.spliterator()` splits by halving the list — but to reach the midpoint, it must traverse half the nodes (O(n)), and the split is uneven because removing the left half leaves the right half starting from the middle. The traversal cost dominates the parallelism gain. `ArrayList.spliterator()` splits by array index — O(1), perfectly balanced. For parallel work, convert to an array or `ArrayList`, or use a custom spliterator that splits by index. The general rule: parallel streams win on sized, array-backed sources with CPU-bound work. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** What does the `CONCURRENT` characteristic promise?
**A:** The source can be safely modified during stream execution without `ConcurrentModificationException` — the spliterator reflects some elements added/removed during traversal. `ConcurrentHashMap`'s spliterator is `CONCURRENT` + `NONNULL` + `DISTINCT` (for keys). It does NOT promise a consistent snapshot — elements added during the stream may or may not be seen. For a snapshot, use `toArray()` first or a `Stream` over a copy. `IMMUTABLE` is stronger — no modifications at all. Lying about `CONCURRENT` on a `HashMap` source causes races. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

A reporting service processes a 50M-row table via `ResultSet` streaming and wants parallel processing. Design the spliterator.

Implement `ResultSetSpliterator` with `tryAdvance` calling `rs.next()` and `trySplit` returning a new spliterator for a row-range (using `LIMIT`/`OFFSET` or a primary-key range — avoid `OFFSET` for large offsets; use keyset pagination). Characteristics: `IMMUTABLE` (the cursor is read-only) + `NONNULL` + `SIZED` (if you know the count). Split threshold: 10k rows per chunk. Use `StreamSupport.stream(spliterator, parallel)` with a custom `ForkJoinPool` (not the common pool — avoid starving other services). Measure: 8 cores should give 4–6× speedup if the per-row work is CPU-bound. If I/O-bound (DB calls per row), parallel won't help — batch instead. Document: `ResultSet` is not thread-safe; each split must open its own connection/statement.


### 66. `enum` deep: abstract methods, implementing interfaces, `EnumMap`/`EnumSet`, `Enum.values()` allocation

**Short answer:**
An `enum` is a special class: it implicitly extends `java.lang.Enum`, can have constructors, fields, methods, abstract methods (per-constant implementations), and implement interfaces. `EnumMap` and `EnumSet` are specialized collections that use the enum ordinal as a backing array index — far faster and smaller than `HashMap`/`HashSet`. `Enum.values()` returns a new array each call (clone of the internal array) — a hidden allocation in hot loops; cache it (`MyEnum[] VALUES = values()`) or use `EnumSet.allOf`. Enums are singletons across classloaders only within one loader — two loaders loading the same enum get distinct instances.

#### What it is
`enum` types are compile-time-known sets of instances. Each constant is a static final instance of the enum class. Abstract methods on the enum are implemented per-constant (anonymous subclasses). Enums can implement interfaces but cannot extend a class (they already extend `Enum`). `EnumMap`/`EnumSet` are JDK collections specialized for enum keys/elements.

#### How it works (internals)
`Enum.values()` is a synthetic method that clones the internal `$VALUES` array — O(n) allocation each call. `Enum.valueOf(name)` does a switch on a hash of the name — O(1). `Enum.ordinal()` returns the index in the values array. `EnumMap` is a `V[]` indexed by ordinal; `EnumSet` is a bitset (regular enum) or `long` bitset (up to 64 elements) — `EnumSet.of(...)` is a single `long` mask. `Enum` constants are initialized in static init; `Enum.ordinal` is set by the JVM.

#### When to use / when NOT to use
Use enums for fixed sets (states, types, categories). Use abstract methods for per-constant behavior (strategy pattern) instead of switch-on-enum. Use `EnumMap`/`EnumSet` for any enum-keyed collection. Avoid `Enum.values()` in hot loops — cache it. Avoid enums for open sets (config values that change) — use a registry or DB lookup. Be careful with enum constants that reference each other in constructors — order matters.

#### Production example
A payment-status enum used abstract methods for `isTerminal()` and `nextStates()` — clean per-state behavior, no switch. A state machine used `EnumMap<State, List<Transition>>` — O(1) lookup, 80% less memory than `HashMap`. A hot path called `Status.values()` per request — switching to a cached `VALUES` array cut 5% allocation in a 100k QPS service. A bug: an enum constructor referenced another constant not yet initialized — NPE at class load; fixed by moving the reference to a method.

#### Common mistakes
- `Enum.values()` in a hot loop — allocation.
- Enum constructor referencing another constant — initialization order.
- `EnumMap` with a `null` key — NPE (no null keys for enums).
- Using `==` vs `equals` for enums — `==` is safe and faster; `equals` is `==` for enums.

#### Interview follow-ups (with model answers)

**Q:** Why does `Enum.values()` allocate, and how do you avoid it?
**A:** `values()` is a synthetic method that clones the internal `$VALUES` array to prevent callers from mutating it. Each call allocates a new array of size `n` — in a hot loop at 100k QPS, that's 100k arrays/sec. Cache it: `private static final MyEnum[] VALUES = values();` (in the enum) or `EnumSet.allOf(MyEnum.class)` for iteration. For `valueOf(name)`, there's no allocation (switch on hash). For `ordinal()`, no allocation. The fix is trivial but easy to miss. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** How do abstract methods on enums work?
**A:** Each enum constant can implement an abstract method as an anonymous subclass — the compiler generates a separate inner class per constant that overrides the method. So `enum Op { ADD { int apply(int a, int b) { return a + b; } }, SUB { ... } }; abstract int apply(int a, int b);` creates two anonymous subclasses. This is the strategy pattern with compile-time-known strategies. The cost: one extra class per constant (minor). The benefit: no switch, type-safe, easy to add a new constant (the compiler forces you to implement the method). On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

A state machine uses `Map<State, List<Transition>>` with `State` enum. The map is built at startup and read 1M times/s. Optimize.

Switch to `EnumMap<State, List<Transition>>` — array-indexed lookup, no hashing, no boxing. Build with `new EnumMap<>(State.class)` and `put`. For the value, use `List.of(...)` (immutable) if no runtime mutation. If transitions are also keyed by enum, use `EnumMap<State, EnumMap<Event, State>>` — nested arrays, O(1) double lookup. Measure: 2–3× faster than `HashMap`. Avoid `Enum.values()` in the build loop — cache `State[] VALUES = State.values()`. Document: `EnumMap` is not thread-safe; if read concurrently after build, wrap in unmodifiable or use volatile reference. Validate with a JMH benchmark.

#### Code / config (when useful)
```java
public enum Operation {
    ADD { public int apply(int a, int b) { return a + b; } },
    SUB { public int apply(int a, int b) { return a - b; } };
    public abstract int apply(int a, int b);
}
private static final State[] STATES = State.values(); // cache
```


### 67. Nested classes: member vs static vs local vs anonymous — the `Outer.this` capture and memory leak

**Short answer:**
A **member (inner) class** holds an implicit reference to the enclosing instance (`Outer.this`) — it can't exist without one, and that reference is a leak vector if the inner outlives the outer. A **static nested class** does not hold the outer reference — use this by default. A **local class** is declared inside a method; it captures local variables (must be final/effectively final). An **anonymous class** is a local class without a name — pre-lambda, used for one-off implementations. The classic leak: an anonymous `Runnable` submitted to a long-lived executor captures `this` (the outer activity/servlet), preventing GC. Prefer static nested classes or lambdas (which don't capture `this` unless they reference instance fields).

#### What it is
Java has four kinds of nested classes: member inner (non-static), static nested, local (in a method), anonymous (local without a name). Each has different capture and instantiation semantics. Lambdas (Java 8+) often replace anonymous classes and have different capture rules — they capture `this` only if they reference instance state.

#### How it works (internals)
A member inner class has a synthetic `this$0` field set at construction — you must construct it via `outer.new Inner()`. A static nested class has no `this$0`. Local/anonymous classes capture local variables by copying them into synthetic fields (must be final to avoid visibility issues — the copy is fixed). Lambdas capture `this` only if they reference instance fields/methods; they capture local variables via `invokedynamic` and `LambdaMetafactory`, which can avoid the synthetic class allocation.

#### When to use / when NOT to use
Default to static nested — no outer reference, no leak. Use member inner only when you genuinely need the outer instance. Use local/anonymous for one-off implementations (prefer lambdas for functional interfaces). Never submit an anonymous `Runnable`/`Callable` capturing `this` to a long-lived executor without clearing the reference. In Android, anonymous handlers leaking `Activity` are the canonical memory leak.

#### Production example
A Spring `@Service` had an anonymous `Runnable` submitted to a scheduled executor for retry; it captured `this` (the service) and a request-scoped DTO. The executor outlived the request, holding the DTO and its classloader. Fix: extract a static nested class taking the DTO as a constructor param, or use a lambda that captures only the DTO. The leak disappeared; heap stabilized. In a servlet, an anonymous `HttpSessionListener` capturing `this` prevented session GC.

#### Common mistakes
- Member inner class submitted to a long-lived executor — leaks outer.
- Anonymous class capturing `this` when a static nested would do.
- Local class capturing a mutable local — compile error; use `AtomicReference` or a one-element array (or refactor).
- Assuming lambdas don't capture `this` — they do if they reference instance fields.

#### Interview follow-ups (with model answers)

**Q:** Why does a member inner class hold a reference to the outer instance?
**A:** The compiler adds a synthetic `this$0` field set in the constructor, so the inner can call outer instance methods and access outer fields. Construction requires an outer instance: `outer.new Inner()`. This is why a member inner can't be instantiated in a static context (no outer). The reference is a leak vector if the inner outlives the outer — e.g., a long-lived executor holding a `Runnable` that's a member inner. Static nested classes avoid this. Lambdas capture `this` only if they reference instance state, so they're often safer. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Why must local variables captured by local/anonymous classes be final?
**A:** The captured variable is copied into a synthetic field of the class at construction. If the local could change after capture, the copy would be stale — the class would see the old value, not the new one. Java enforces final (or effectively final) to make this consistent. For mutable state, use a holder (`AtomicReference`, `int[1]`, or a custom class) and capture the holder (final reference, mutable contents). Lambdas have the same rule. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

A Spring `@Component` registers an anonymous `ServletContextListener` in a `@PostConstruct` that captures `this` to access a `Map` cache. After redeploy, heap dumps show the old component retained. Diagnose and fix.

The listener is registered with the servlet context (long-lived) and holds `this` (the component). On redeploy, the servlet context still references the old listener, which references the old component and its classloader — classic Metaspace leak. Fix: extract a static nested class that takes the cache as a constructor param (or a reference to a shared bean), so it doesn't capture the component. Or register the listener in a `ServletContextInitializer` with proper deregistration in `contextDestroyed`. Or use a `WeakReference` to the cache. Best: don't store state in the component; use a `ConcurrentHashMap` bean that's explicitly cleared. Validate with a hot-redeploy test (30 deploys, assert Metaspace stable). Document: any long-lived registration holding `this` is a leak.


### 68. Pattern matching for switch (Java 21): exhaustiveness, null handling, guarded patterns, dominance errors

**Short answer:**
Java 21's pattern switch (`switch (x) { case Integer i -> ...; case String s when s.length() > 3 -> ...; }`) lets you match types, bind variables, and add guards (`when`). It's exhaustive if all possible types are covered — for sealed hierarchies, the compiler knows; for `Object`, you need a `default`. `null` is NOT matched by type patterns (it falls to `default` or throws `NullPointerException` if no `case null`); you can add `case null -> ...` to handle it explicitly. Guarded patterns (`when`) are evaluated after the type match; a later unguarded pattern can dominate an earlier guarded one — the compiler errors. Switch expressions (returning a value) require exhaustiveness; switch statements don't (but fall-through still applies).

#### What it is
Pattern matching for switch (JEP 441, final in 21) combines type patterns, guarded patterns, and null handling in switch. Type patterns bind the matched value to a variable. Guards (`when`) refine the match. Exhaustiveness is checked for sealed types and switch expressions. `case null` is a new explicit case for null.

#### How it works (internals)
The compiler desugars type-pattern switch to `if` chains with `instanceof` and binding, or to a `typeSwitch` bootstrap for better performance. Sealed types allow exhaustiveness checking — the compiler knows all permitted subtypes. Guards are evaluated after the type match succeeds; if the guard fails, the case doesn't match and the next is tried. Dominance: an unguarded `case Number n` dominates `case Integer i when i > 0` because the guard might fail; the compiler errors. `case null` must be explicit — without it, null throws NPE before any case is tried.

#### When to use / when NOT to use
Use pattern switch for type-based dispatch (visitor replacement), sealed hierarchies, and replacing `if-else` chains of `instanceof`. Use guards for refinement. Always handle `null` explicitly if it's a valid input. Avoid deep guards — they're hard to read; extract a method. For switch expressions, ensure exhaustiveness (sealed types or a `default`).

#### Production example
A payment event handler used a chain of `if (event instanceof PaymentCreated pc) ... else if ...`. Switching to pattern switch with a sealed `PaymentEvent` hierarchy made the code exhaustive-checked (compiler errors if a new event type is added without a case) and 30% faster (the `typeSwitch` bootstrap). A bug: a guard `case Refund r when r.amount() > 0` was placed after `case Refund r` — dominance error; reordering fixed it.

#### Common mistakes
- Forgetting `case null` — NPE on null input.
- Guarded case after unguarded same-type — dominance error.
- Switch expression without exhaustiveness — compile error (good) or missing `default`.
- Using `when` for non-trivial logic — extract a method for readability.

#### Interview follow-ups (with model answers)

**Q:** How does exhaustiveness work for sealed types in switch?
**A:** For a sealed type with `permits A, B, C`, the compiler knows all subtypes. A switch covering `A`, `B`, `C` is exhaustive — no `default` needed. Adding a new subtype `D` to the sealed interface forces all switches to add `case D` or a `default` — compile errors guide you. This is the visitor pattern without the visitor boilerplate. For non-sealed types (e.g., `Object`), you need a `default` or cover all reachable types. Switch expressions always require exhaustiveness; switch statements don't but fall through. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** What is the dominance rule for guarded patterns?
**A:** A pattern A dominates pattern B if every value matching B also matches A. So `case Number n` dominates `case Integer i when i > 0` (every `Integer > 0` is a `Number`). The compiler errors if a dominated case appears after a dominating one — it would be unreachable. Fix: order specific cases (guarded) before general ones (unguarded). The rule ensures no case is silently unreachable. Guards are evaluated after the type match, so a failing guard falls through to the next case — important for ordering. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

A service handles a sealed `PaymentEvent` with `Created`, `Refunded`, `Failed`. Refunds above 1000 need extra logging. Write the switch and explain.

```java
return switch (event) {
    case Created c -> "Created " + c.id();
    case Refunded r when r.amount().compareTo(BigDecimal.valueOf(1000)) > 0 -> {
        log.warn("Large refund {}", r);
        yield "Large refund " + r.id();
    }
    case Refunded r -> "Refunded " + r.id();
    case Failed f -> "Failed " + f.reason();
};
```
The guarded `Refunded` case must come before the unguarded one (dominance). No `default` needed — sealed type is exhaustive. No `case null` — `event` is non-null by contract; if null is possible, add `case null -> throw new IllegalArgumentException()`. Validate with a unit test covering all cases including the guard boundary (amount = 1000 vs 1001). Document: the switch expression returns a value, so exhaustiveness is enforced.


### 69. Record patterns (Java 21): destructuring nested records in switch, with var

**Short answer:**
Record patterns (JEP 440, final in 21) let you destructure a record into its components in one step: `if (o instanceof Point(int x, int y))`. They nest: `case Rectangle(Point(int x1, int y1), Point(int x2, int y2)) -> ...`. With `var`, you can omit types: `Point(var x, var y)`. In switch, record patterns combine with type patterns and guards for powerful dispatch. The pattern fails if the value isn't the record type or if a nested pattern fails; the compiler infers types from the record header. Record patterns make data-oriented code read like the data shape.

#### What it is
A record pattern matches a record and binds its components to names. It's the destructuring counterpart to the record's constructor. Nested record patterns destructure components that are themselves records. Type inference via `var` lets you omit component types. Record patterns work in `instanceof` and `switch`.

#### How it works (internals)
The compiler translates `Point(int x, int y)` into `instanceof Point p && x = p.x() && y = p.y()` (with accessor calls). Nested patterns chain accessor calls. The pattern fails fast if any component pattern fails. For switch, record patterns combine with type patterns: `case Point(int x, int y) -> ...`. Exhaustiveness applies to sealed record hierarchies. The accessor calls are inlined by the JIT in hot paths.

#### When to use / when NOT to use
Use record patterns for clean destructuring of records, especially nested ones. Use `var` for brevity when the type is obvious. Avoid record patterns on classes with many components — readability suffers. For non-record classes, use type patterns (`instanceof Foo f`). Record patterns shine in switch over sealed record hierarchies — exhaustive, readable, compiler-checked.

#### Production example
A geometry service used nested `if` chains to extract coordinates; switching to nested record patterns (`case Box(Point(var x1, var y1), Point(var x2, var y2)) -> ...`) made the code half as long and self-documenting. A parser used record patterns to walk an AST (sealed `Node` with `Number`, `BinOp`, `Var`) — exhaustive switch, no casts, no visitor boilerplate. The compiler caught a missing `Var` case when a new node type was added.

#### Common mistakes
- Using record patterns on non-record classes — compile error.
- Forgetting nested patterns can fail — the outer match succeeds, inner fails, the whole pattern fails (correct but surprising).
- Omitting `var` when types are unclear — hurts readability.
- Not using sealed hierarchies — loses exhaustiveness checking.

#### Interview follow-ups (with model answers)

**Q:** How do nested record patterns work and when do they fail?
**A:** `case Rectangle(Point(int x1, int y1), Point(int x2, int y2))` first matches if the value is a `Rectangle`, then matches each component as a `Point`, then binds `x1, y1, x2, y2`. If any nested pattern fails (e.g., a component is null or not a `Point`), the whole pattern fails and the next case is tried. This is "pattern decomposition" — the compiler generates accessor calls and recursive checks. For null components, the pattern fails (null doesn't match `Point(int, int)`); handle null with a guard or a separate case. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** When should you use `var` in record patterns?
**A:** Use `var` when the component type is obvious from context — `Point(var x, var y)` is clear; `Point(int x, int y)` is redundant. Use explicit types when inference would be ambiguous or when you want to document the type. `var` is required for nested patterns where the inner type is inferred from the outer record's component type. Mixing `var` and explicit types in one pattern is allowed. The readability rule: if a reader would have to look up the type, spell it out; otherwise, use `var`. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

An AST evaluator handles a sealed `Node` with `Num(int value)`, `BinOp(Node left, Op op, Node right)`, `Var(String name)`. Write an eval switch using record patterns.

```java
int eval(Node n) {
    return switch (n) {
        case Num(int v) -> v;
        case BinOp(Node l, Op op, Node r) -> switch (op) {
            case ADD -> eval(l) + eval(r);
            case SUB -> eval(l) - eval(r);
            case MUL -> eval(l) * eval(r);
            case DIV -> eval(l) / eval(r);
        };
        case Var(String name) -> env.getOrDefault(name, 0);
    };
}
```
The outer switch is exhaustive (sealed `Node`). The inner switch over `Op` (enum) is exhaustive. No casts, no visitor. The nested `BinOp(Node l, Op op, Node r)` destructures in one line. Add `case null` if `n` can be null. Validate with unit tests covering each `Op` and nested expressions. Document: record patterns make the AST walk read like the grammar.


### 70. Text blocks, switch expressions, `yield` — migration from pre-Java-14

**Short answer:**
Text blocks (Java 15, `"""..."""`) replace string concatenation for multi-line strings — SQL, JSON, HTML — with no escape noise. Switch expressions (Java 14, `switch (x) -> value`) return a value, use arrow labels (no fall-through), and require exhaustiveness. `yield` returns a value from a block in a switch expression (`case X -> { ...; yield value; }`). Migration from pre-14: replace `String + "\n" + ...` with text blocks, replace `switch` statements with `if`/`return` chains or switch expressions for value-returning dispatch. Both reduce boilerplate and bugs (no fall-through, no missing `break`).

#### What it is
Text blocks are triple-quoted strings with incidental whitespace handling (trailing whitespace stripped, controllable indentation via the closing delimiter position). Switch expressions are switch that returns a value; arrow labels (`->`) don't fall through; `yield` returns from a block. Both are language features, not library changes.

#### How it works (internals)
Text blocks are compiled to a `String` constant with the same interning as string literals — no runtime cost. The compiler computes the incidental whitespace by aligning to the closing `"""` position. Switch expressions desugar to `LookupSwitch` or `TableSwitch` bytecode like switch statements; the difference is exhaustiveness checking and `yield` (a value return). `yield` is a restricted identifier (not a keyword) — you can still use `yield` as a variable name elsewhere.

#### When to use / when NOT to use
Use text blocks for any multi-line string literal — SQL, JSON, HTML, YAML, error messages. Use switch expressions for value-returning dispatch; switch statements for side-effecting dispatch. Use `yield` only when a case needs a block (multiple statements); for single expressions, use `case X -> value`. Avoid text blocks for single-line strings — regular literals are clearer.

#### Production example
A service had a 200-line SQL query built with `String + "\n" + ...` — unreadable, error-prone. Switching to a text block made it editable and reviewable. A state-to-string dispatch used a switch statement with `return` in each case; switching to a switch expression with arrow labels removed 4 `break` bugs and made exhaustiveness compiler-checked. A `yield` was used in one case that needed logging before returning.

#### Common mistakes
- Forgetting `yield` in a block case — compile error (good).
- Mixing `:` and `->` labels in one switch — compile error.
- Text block trailing whitespace stripped — use `\s` to preserve.
- Switch expression without exhaustiveness — compile error (good).

#### Interview follow-ups (with model answers)

**Q:** How does text block indentation work?
**A:** The compiler finds the least-indented line (excluding blank lines) and removes that many leading spaces from all lines — this is "incidental whitespace." The position of the closing `"""` controls the baseline: if it's on its own line, the indentation of that line is the baseline. To preserve trailing whitespace, use `\s` (escaped space). To preserve leading whitespace beyond the baseline, use `String.indent(n)` or `stripIndent`. The feature is designed so the text block looks right in the source and produces the right string. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** When do you use `yield` vs `-> value` in a switch expression?
**A:** Use `case X -> value` for single-expression cases — concise, no block. Use `case X -> { ...; yield value; }` when the case needs statements (logging, computation, validation) before returning. `yield` is the value-returning counterpart to `return` in a method. You cannot use `return` in a switch expression case (it would return from the enclosing method, not the switch). `yield` is a restricted identifier — valid as a variable name elsewhere, but in a switch expression block, it's the yield statement. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

A legacy service has 50 SQL queries as concatenated strings and a state-dispatch method with switch statements and `return` in each case. Walk through the migration to Java 17.

For SQL: convert each to a text block — `String sql = """ SELECT ... FROM ... WHERE ... """;`. The text block preserves newlines and indentation, making the SQL readable and editable. Test each query after conversion (the string content changes — whitespace handling). For state dispatch: convert the switch statement to a switch expression with arrow labels — `return switch (state) { case A -> "active"; case B -> "pending"; ... };`. Add a `default` if not exhaustive, or make the state enum sealed. Replace `return` in each case with `-> value`; for cases needing logging, use `case X -> { log...; yield value; }`. Validate with unit tests. Document: switch expressions are exhaustive-checked, so adding a new state forces all switches to handle it.

#### Code / config (when useful)
```java
String sql = """
    SELECT id, name
    FROM users
    WHERE active = true
    """;
String label = switch (state) {
    case ACTIVE -> "Active";
    case PENDING -> { log.debug("Pending"); yield "Pending"; }
    case CLOSED -> "Closed";
};
```


### 71. `var` and type inference: local vars, lambda params, `var` in enhanced `for`, when it hurts readability

**Short answer:**
`var` (Java 10) infers the local variable type from the initializer — no runtime change, just less boilerplate. It works for locals with initializers, `try`-with-resources, enhanced `for` loops (`for (var x : list)`), and lambda formal parameters (`(var a, var b) -> ...`, needed only when you annotate). It does NOT work for fields, method return types, method parameters (without lambda), or uninitialized locals. Use `var` when the type is obvious from the initializer (`var list = new ArrayList<String>()`) or the variable name carries the type (`var user = ...`). Avoid `var` when the inferred type is non-obvious (`var result = process()` — what type?) or when the type matters for correctness (`var prices = new float[0]` — float vs double).

#### What it is
`var` is a reserved type name (not a keyword) that tells the compiler to infer the type. The inferred type is the static type of the initializer — no runtime change, no dynamic typing. `var` is local-only; fields and method signatures still need explicit types (for API clarity and binary compatibility).

#### How it works (internals)
The compiler infers the type from the initializer expression's static type. For generics, inference applies (`var list = new ArrayList<>()` infers `ArrayList<Object>` unless the initializer has more info). For lambdas, `var` on formal params enables annotations (`(@Nullable var x) -> ...`). The JVM sees the inferred type in bytecode — no `var` marker. `var` cannot be used for `null` initializers (no type to infer).

#### When to use / when NOT to use
Use `var` when the type is obvious (`new`, literals, casts) or the name carries the type. Use `var` in `for` loops and `try`-with-resources. Avoid `var` when the type is non-obvious from the right-hand side (`process()` returns what?), when it hides upcasting (`var list = new ArrayList<String>()` — you get `ArrayList`, not `List`), or when the type matters for readability (interface vs implementation). For public API, fields and method signatures must be explicit.

#### Production example
A service used `var` everywhere for brevity; a code review found `var status = request.getStatus()` returned `Optional<Status>` — readers assumed `Status`, leading to NPE on `.map`. Fix: explicit `Optional<Status> status = ...` for clarity. A team adopted the rule "use `var` when the initializer is `new`, a literal, or a factory with the type in the name." This balanced brevity and clarity. Hot paths benefited from `var` reducing visual noise.

#### Common mistakes
- `var list = new ArrayList<String>()` — inferred as `ArrayList`, not `List` — locks the implementation.
- `var result = service.process()` — type unclear, hurts readability.
- Using `var` for fields — compile error (fields need explicit types).
- `var x = null` — compile error (no type to infer).

#### Interview follow-ups (with model answers)

**Q:** When does `var` hurt readability?
**A:** When the inferred type is non-obvious — `var result = service.process()` doesn't tell the reader if `result` is a `User`, `Optional<User>`, or `CompletableFuture<User>`. The variable name doesn't always carry the type. Also, `var list = new ArrayList<String>()` infers `ArrayList`, not `List`, locking the implementation. The rule: use `var` when the type is obvious from the initializer (`new`, literals, casts) or the variable name carries the type (`var user = ...`). For everything else, spell out the type. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Why can't `var` be used for fields or method parameters?
**A:** Fields and method signatures are part of the API contract — explicit types document the contract and ensure binary compatibility. Inferring field types from initializers would make the type depend on the initializer, which could change without API intent. Method parameters have no initializer to infer from. `var` is local-only by design — locals are implementation details, not contract. For lambdas, `var` on formal params is allowed (for annotations), but the type is still inferred from the functional interface. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

A code review flags `var result = service.process(request)` as unclear. The reviewer wants explicit type. The author argues `var` is fine. Resolve.

The issue is the initializer (`service.process(...)`) doesn't reveal the type — a reader has to look up `process`'s return type. If it's `Optional<User>`, the reader might miss the `Optional` and call `.getName()` directly (NPE). If the variable name carried the type (`var userOpt = ...`), `var` would be fine. Or spell it out: `Optional<User> result = ...`. The team rule: use `var` when the type is obvious from the initializer or the variable name; otherwise, explicit. Document the rule in the style guide. For this case, either rename to `userOpt` or use explicit `Optional<User>`. The goal is reader clarity, not character count. Validate with a quick team poll on readability.


### 72. `Stream.toList()` (Java 16) vs `Collectors.toList()` vs `Collectors.toUnmodifiableList()` — mutability and nulls

**Short answer:**
`Stream.toList()` (Java 16) returns an unmodifiable list — concise, no `Collectors` import, but the implementation is an immutable `ArrayList`-like (no `null` elements allowed, throws NPE on `null`). `Collectors.toList()` returns a mutable `ArrayList` (implementation detail, not guaranteed) — allows `null` but is mutable, so callers can modify. `Collectors.toUnmodifiableList()` (Java 10) returns an unmodifiable list — same as `toList()` but explicit and supports `null`? No — it throws NPE on `null` too. Pick by intent: `toList()` for the common case (immutable, no nulls), `Collectors.toList()` if you need to mutate after, `Collectors.toUnmodifiableList()` for explicit immutability on older code.

#### What it is
`Stream.toList()` is an instance method on `Stream` (Java 16+) that collects to an unmodifiable list. `Collectors.toList()` is the older collector returning a mutable list (implementation-defined). `Collectors.toUnmodifiableList()` is the explicit unmodifiable collector (Java 10+). All three throw NPE on `null` elements except `Collectors.toList()` (which allows nulls).

#### How it works (internals)
`Stream.toList()` uses a private `ImmutableCollections.listFromStream` that avoids the `ArrayList` allocation when the size is known (from a `SIZED` spliterator) — it allocates the exact-size array directly. `Collectors.toList()` always allocates an `ArrayList` and copies. `Collectors.toUnmodifiableList()` allocates an immutable list. The mutability difference: `toList()` and `toUnmodifiableList()` throw `UnsupportedOperationException` on `add`/`set`; `Collectors.toList()` allows mutation.

#### When to use / when NOT to use
Use `Stream.toList()` for the common case — immutable result, no nulls, concise. Use `Collectors.toList()` if you need to mutate the result after (rare — usually a code smell). Use `Collectors.toUnmodifiableList()` for explicit immutability on pre-16 code or when you want the intent explicit. If your stream may contain nulls, use `Collectors.toList()` (or filter nulls first — usually cleaner).

#### Production example
A service returned `stream.map(...).collect(Collectors.toList())` and downstream code mutated it — a bug when the team switched to `toList()` (immutable, threw `UnsupportedOperationException`). Fix: the downstream mutation was a bug; the list was meant to be a result, not a working copy. Switching to `toList()` caught the mutation at runtime (test failure) and the team fixed the downstream code. A separate case: a stream contained nulls (legacy); `toList()` threw NPE. Fix: filter nulls first, or use `Collectors.toList()` if nulls are valid.

#### Common mistakes
- Switching `Collectors.toList()` to `toList()` without checking for nulls — NPE.
- Switching to `toList()` when downstream mutates — `UnsupportedOperationException`.
- Assuming `Collectors.toList()` is immutable — it's mutable.
- Using `toList()` for a list you intend to sort in place — it's immutable; sort before collecting.

#### Interview follow-ups (with model answers)

**Q:** What's the difference between `Stream.toList()` and `Collectors.toUnmodifiableList()`?
**A:** Both return unmodifiable lists that throw NPE on nulls. `Stream.toList()` (Java 16+) is an instance method — concise, no import. `Collectors.toUnmodifiableList()` (Java 10+) is a collector — explicit, works with `collect()`. `Stream.toList()` can be slightly more efficient for sized streams (allocates exact size). Behavior is otherwise identical. Use `toList()` for new code; use `toUnmodifiableList()` if you're on pre-16 or want the intent explicit. Neither allows nulls; neither allows mutation. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** When would you use `Collectors.toList()` over `Stream.toList()`?
**A:** When you need to mutate the result after collecting — e.g., adding elements, sorting in place, or passing to a method that mutates. This is rare and often a code smell (the list should be a result, not a working copy). Also when the stream may contain nulls — `Collectors.toList()` allows nulls, `Stream.toList()` throws NPE. For most code, `Stream.toList()` is the right choice — immutable, concise, efficient. If you find yourself reaching for `Collectors.toList()` to mutate, consider whether the mutation is necessary. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

A team migrates from `Collectors.toList()` to `Stream.toList()` across a 100-class codebase. After deploy, one service throws `UnsupportedOperationException` and another throws NPE. Diagnose and fix.

The `UnsupportedOperationException` is downstream code mutating the collected list — `list.add(...)` or `list.sort(...)`. Fix: either revert that call to `Collectors.toList()` (if mutation is intentional) or fix the downstream code to not mutate (usually correct — the list is a result). The NPE is a stream element that's null — `Stream.toList()` rejects nulls. Fix: filter nulls first (`stream.filter(Objects::nonNull).toList()`) or revert to `Collectors.toList()` if nulls are valid. Add a regression test for both cases. Document the migration rule: `toList()` is immutable and null-rejecting; audit downstream mutation and null elements before switching. Validate with a canary deploy.


### 73. `@FunctionalInterface` — marker, multi-method interfaces and default methods, `Predicate`/`Consumer`/`Function`/`Supplier`/`BiFunction`/`UnaryOperator`

**Short answer:**
`@FunctionalInterface` is a marker annotation (optional) indicating an interface with exactly one abstract method — eligible for lambda conversion. The interface can have multiple `default` and `static` methods; only one abstract (unimplemented) method counts. The JDK's core functional interfaces: `Function<T, R>` (T→R), `Predicate<T>` (T→boolean), `Consumer<T>` (T→void), `Supplier<T>` (→T), `BiFunction<T, U, R>` (T,U→R), `UnaryOperator<T>` (T→T, a `Function` shortcut), `BinaryOperator<T>` (T,T→T). `@FunctionalInterface` is not required — the compiler infers functional-ness from the single-abstract-method rule — but it documents intent and catches accidental additions.

#### What it is
A functional interface has exactly one abstract method. It can extend `java.lang.Object` methods (those don't count — e.g., `Comparator` has `equals` from Object, but it's still functional). `default` and `static` methods don't count. The annotation `@FunctionalInterface` is optional but recommended — it makes the contract explicit and the compiler errors if you add a second abstract method.

#### How it works (internals)
A lambda targeting a functional interface is compiled to an `invokedynamic` call with a `LambdaMetafactory` bootstrap. The factory generates a class at runtime (or via `indy` condy in newer JDKs) implementing the interface's single abstract method, capturing the lambda's free variables. Method references (`String::length`) are similar. The interface's single abstract method's signature determines the lambda's signature. `default` methods are inherited via the interface's vtable.

#### When to use / when NOT to use
Annotate your own functional interfaces with `@FunctionalInterface` — documents intent, catches accidental second methods. Use the JDK's built-in interfaces (`Function`, `Predicate`, etc.) instead of creating your own when they fit. Create your own only when the name adds clarity (e.g., `RetryPolicy` extends `Predicate<Exception>`). Avoid functional interfaces with too many defaults — they become hard to reason about.

#### Production example
A retry library defined `@FunctionalInterface interface RetryPolicy { boolean shouldRetry(Throwable t, int attempt); }` — clear, lambda-friendly (`(t, n) -> n < 3`). A team created `Transformer<T, R>` extending `Function<T, R>` for domain clarity — `Transformer<Order, OrderDto>`. A bug: a "functional" interface had two abstract methods (a refactor added one); without `@FunctionalInterface`, the lambda broke at the call site, not the interface. Adding the annotation caught it at the interface.

#### Common mistakes
- Not annotating — second abstract method silently breaks lambdas at call sites.
- Creating a new functional interface when `Function`/`Predicate` would do — name pollution.
- Forgetting `Object` methods (`equals`, `hashCode`, `toString`) don't count — they're inherited.
- Functional interfaces with checked exceptions — lambdas can't throw checked exceptions unless the method declares them.

#### Interview follow-ups (with model answers)

**Q:** Why is `@FunctionalInterface` optional, and when does it matter?
**A:** The compiler treats any interface with one abstract method as functional, with or without the annotation. The annotation does two things: documents intent (this is meant to be used with lambdas) and causes a compile error if someone adds a second abstract method. Without it, a refactor adding a second method breaks lambdas at the call site (confusing error). With it, the error is at the interface (clear). Always annotate your own functional interfaces. The JDK's `Function`, `Predicate`, etc. are annotated. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** How do `default` methods affect functional interfaces?
**A:** `default` methods don't count toward the single-abstract-method limit — a functional interface can have many defaults. This lets you add helper methods to a functional interface without breaking it. For example, `Function` has `andThen` and `compose` as defaults. The single abstract method (`apply`) is what lambdas implement. `static` methods also don't count. The rule: exactly one abstract (non-default, non-static, non-Object) method. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

A team defines `interface Validator<T> { boolean validate(T t); default Validator<T> and(Validator<T> other) { return t -> validate(t) && other.validate(t); } }`. Is this a good functional interface? Walk through.

Yes — it's a functional interface with one abstract method (`validate`) and a `default` for composition. The `and` default returns a lambda combining two validators — clean, composable. Annotate with `@FunctionalInterface` to lock the contract. The `and` method is a fluent combinator, like `Predicate.and`. Consider also `or`, `negate` defaults. The interface name `Validator` is clearer than `Predicate<T>` for domain code. Trade-off: creating a new interface vs reusing `Predicate<T>` — if the domain uses "validator" terminology, the named interface aids readability. Validate with a unit test: `Validator<String> nonEmpty = s -> !s.isEmpty(); Validator<String> short_ = s -> s.length() < 10; var v = nonEmpty.and(short_); assert v.validate("hi")`.


### 74. Default methods: diamond conflict resolution, `super` syntax, the `Object`-method redeclaration rule

**Short answer:**
Default methods (Java 8) let interfaces have method bodies. When a class inherits the same default method from two interfaces (diamond), it must override and disambiguate with `Interface.super.method()`. `Object` methods (`equals`, `hashCode`, `toString`) cannot be defaults — redeclaring them in an interface as default is a compile error (they must be abstract or inherited from Object). The conflict resolution rule: class methods win over interface defaults; among interfaces, the most specific (subinterface) wins; otherwise, the class must override.

#### What it is
A `default` method in an interface has a body and is inherited by implementing classes. It enables interface evolution — adding a method to an existing interface without breaking implementations. Conflicts arise when two interfaces provide defaults for the same method; the implementing class must disambiguate.

#### How it works (internals)
Resolution order: (1) class (concrete or abstract) methods win over interface defaults; (2) among interfaces, the most specific (subinterface) default wins; (3) if no specificity (true diamond), the class must override and call `Interface.super.method()` explicitly. `Object` methods (`equals`, `hashCode`, `toString`, `getClass`, `clone`, `finalize`) cannot be defaults — every class already inherits them from `Object`, and the JVM treats them specially. Redeclaring `equals` as default is a compile error; redeclaring as abstract is allowed (forces implementors to override).

#### When to use / when NOT to use
Use default methods for interface evolution (adding a method to an existing interface) and for combinators (`Function.andThen`, `Predicate.and`). Avoid defaults for core behavior — prefer abstract methods so implementors are explicit. Don't use defaults to share code across unrelated interfaces — that's a trait/mixin pattern Java doesn't fully support; composition is clearer. For `Object` methods, use a helper class or composition, not a default.

#### Production example
A library added `default Optional<T> findFirst(Predicate<T> p)` to a `Repository` interface — existing implementations kept working. A class implementing two interfaces with conflicting `default Optional<T> findFirst(...)` had to override and call `RepoA.super.findFirst(p).or(() -> RepoB.super.findFirst(p))`. A bug: a team added `default boolean equals(Object o)` to an interface — compile error; they moved the logic to a static helper. A mixin-style default `default Validated validate()` was confusing; refactored to a separate `Validator` interface.

#### Common mistakes
- `default equals`/`hashCode`/`toString` — compile error.
- Diamond conflict without override — compile error.
- Using defaults for core behavior — implementors miss the contract.
- Defaults calling other interface methods that aren't yet implemented — works but surprising.

#### Interview follow-ups (with model answers)

**Q:** How is a diamond conflict resolved?
**A:** If a class implements two interfaces with the same default method, the compiler errors: "class inherits unrelated defaults." The class must override the method and can call either parent via `Interface.super.method()`. If one interface extends the other, the subinterface's default wins (more specific) — no override needed. Class methods always win over interface defaults. The rule prioritizes explicit implementations (class) over inherited (interface), and specific (subinterface) over general. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Why can't `equals`/`hashCode`/`toString` be default methods?
**A:** Every class inherits these from `Object`, and the JVM treats them specially (e.g., `equals` is used in collections, `hashCode` in hashing). Allowing interfaces to override them as defaults would create ambiguity — does the default or the Object implementation win? The designers chose to forbid interface defaults for Object methods to keep the inheritance model simple. You can redeclare them as abstract in an interface (forcing implementors to override), but not as default. For shared `equals`/`hashCode` logic, use a static helper or composition. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

A class implements two interfaces, both with `default Optional<T> find(Predicate<T> p)` returning different defaults. The class should try the first, fall back to the second. Write the override.

```java
@Override
public Optional<T> find(Predicate<T> p) {
    return A.super.find(p).or(() -> B.super.find(p));
}
```
The `A.super.find(p)` syntax calls interface A's default explicitly. The `or(() -> B.super.find(p))` lazily falls back to B. This resolves the diamond. If A extends B (A is more specific), A's default wins automatically — no override needed. If the class has its own `find`, it wins over both. Document: the override is required only for true diamonds (no specificity). Validate with a unit test: A returns empty, B returns a value, the combined `find` returns B's value. Add a test for both empty. The pattern composes defaults cleanly.


### 75. NIO.2 `Files` / `Path` / `FileSystem` / `WatchService` — replacing `java.io.File`

**Short answer:**
NIO.2 (Java 7) replaces `java.io.File` with `Path` (a sequence of name elements), `Files` (operations on paths), `FileSystem` (a provider of paths — default OS, or zip/jar), and `WatchService` (file change events). `Path` is platform-aware and composable (`resolve`, `relativize`, `normalize`). `Files` provides `readAllBytes`, `lines`, `copy`, `move`, `delete`, `walk` (recursive), with `CopyOption`/`OpenOption` flags. `WatchService` polls the OS for directory changes (create/modify/delete). `java.io.File` is legacy — use `Path` for new code; `File.toPath()` bridges.

#### What it is
`Path` is an immutable, hierarchical path object. `Files` is a utility class with static methods operating on `Path`. `FileSystem` is the abstraction over a file system (default OS, or a custom provider like `jar:file:...`). `WatchService` registers directories for change events. Together they replace `java.io.File`'s awkward API (returning `boolean` instead of throwing, no path manipulation, no attributes).

#### How it works (internals)
`Path` is backed by a `FileSystem` provider; the default provider uses native OS calls. `Files.walk` uses a `Stream<Path>` backed by a `Spliterator` over directory entries — must be closed (try-with-resources). `WatchService` uses OS event APIs (inotify on Linux, FSEvents on macOS, ReadDirectoryChangesW on Windows) where available, polling otherwise. `Files.lines` uses a buffered reader with UTF-8 default and lazy stream — good for large files. `Files.copy` supports `REPLACE_EXISTING`, `COPY_ATTRIBUTES`, `NOFOLLOW_LINKS`.

#### When to use / when NOT to use
Use `Path`/`Files` for all new file code — `java.io.File` is legacy. Use `Files.lines` for streaming large files (don't `readAllLines` on a 10 GB file). Use `Files.walk` for recursive traversal (try-with-resources). Use `WatchService` for directory monitoring — but be aware of OS limitations (event coalescing, no recursive watch on some platforms). For high-throughput, consider `ByteBuffer`/`FileChannel` directly.

#### Production example
A service used `java.io.File` and `BufferedReader` to read a config file; switching to `Files.readString(Path.of(config))` was one line and handled UTF-8. A log processor used `Files.lines(path)` to stream a 5 GB log — no OOM. A config watcher used `WatchService` to reload config on change — but events coalesced under rapid saves; the team added a debounce. A bug: `Files.walk` was not closed, leaking file handles; fixed with try-with-resources.

#### Common mistakes
- Using `java.io.File` in new code — `Path` is the modern API.
- `Files.readAllLines` on a large file — OOM; use `Files.lines`.
- Not closing `Files.walk`/`Files.lines` streams — file handle leak.
- `WatchService` without debounce — events fire rapidly on saves.

#### Interview follow-ups (with model answers)

**Q:** How does `WatchService` work and what are its limitations?
**A:** `WatchService` registers directories for `ENTRY_CREATE`, `ENTRY_MODIFY`, `ENTRY_DELETE` events. It uses OS event APIs (inotify/FSEvents/ReadDirectoryChangesW) where available — efficient, no polling. Limitations: (1) not recursive by default — you must register each subdirectory (or re-register on create); (2) events coalesce — multiple writes may fire one event; (3) some OSes don't report the modified file's name reliably; (4) no event ordering guarantees. For robust config reload, debounce (e.g., 500 ms) and re-read the file on each event. For recursive watch, walk and register on startup, re-register new directories on create. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** When would you use `FileChannel`/`ByteBuffer` over `Files`?
**A:** For high-throughput binary I/O — `FileChannel` with a direct `ByteBuffer` can use zero-copy `transferTo` to send file contents to a socket without user-space copies. `Files.copy` uses a streaming copy with a heap buffer — fine for most cases, but for large files or hot paths, `FileChannel` is faster. `FileChannel.map` maps a file region into memory (`MappedByteBuffer`) — useful for random access to large files. For text, `Files.lines` is simpler and good enough. Use `FileChannel` when profiling shows `Files.copy` is a bottleneck. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

A service reads a 2 GB CSV nightly and processes each row. The legacy code uses `BufferedReader` and `readLine` in a loop, taking 90 seconds. Optimize.

Use `Files.lines(Path.of(csv))` — same I/O but cleaner, try-with-resources, UTF-8 default. The 90s is likely I/O-bound, not API-bound. To speed up: (1) parallelize with a `Stream` over `Files.lines().parallel()` — but check the spliterator (line-based, splits poorly); better to chunk by byte range and parallelize chunks. (2) Use `BufferedReader` with a larger buffer (`new BufferedReader(reader, 1 << 16)`). (3) If parsing is CPU-bound, use a parallel stream over a byte-range split (each chunk reads its range, handles partial lines at boundaries). (4) For SSDs, sequential read is fast; the bottleneck is parsing — parallelize parsing. Measure with JFR. Document: `Files.lines` is sequential; for parallelism, split by byte range. Validate with a benchmark.

#### Code / config (when useful)
```java
try (var lines = Files.lines(Path.of("data.csv"))) {
    lines.map(this::parse).filter(Objects::nonNull).forEach(this::process);
}
try (var watcher = FileSystems.getDefault().newWatchService()) {
    Path dir = Path.of("./config");
    dir.register(watcher, ENTRY_MODIFY);
    WatchKey key = watcher.take();
    key.pollEvents().forEach(e -> reload(dir.resolve((Path) e.context())));
    key.reset();
}
```


### 76. `ByteBuffer`: heap vs direct, `allocateDirect`, zero-copy `transferTo`, when native I/O wins

**Short answer:**
A `ByteBuffer` is a fixed-size byte array with read/write position and limit. Heap buffers (`ByteBuffer.allocate(n)`) live on the Java heap — cheap to allocate, GC moves them, but every I/O syscall requires a copy to a native buffer. Direct buffers (`ByteBuffer.allocateDirect(n)`) live in native memory outside the heap — no per-syscall copy, faster for large I/O, but expensive to allocate and not GC'd quickly (rely on `Cleaner`). Zero-copy `FileChannel.transferTo` sends file bytes directly to a socket channel without user-space copies. Use direct buffers for large, long-lived I/O buffers (Netty, gRPC); use heap buffers for small, short-lived ones.

#### What it is
`ByteBuffer` is the NIO buffer for raw bytes. Heap buffers are backed by a `byte[]` on the heap. Direct buffers are backed by native memory (malloc'd). Both have `position`, `limit`, `capacity` markers for read/write. `FileChannel` and `SocketChannel` read/write `ByteBuffer`s. `transferTo` is a zero-copy file-to-channel method.

#### How it works (internals)
Heap buffer I/O: the JVM copies the heap `byte[]` to a temporary native buffer, then calls the syscall — two copies (heap→native→kernel). Direct buffer I/O: the JVM passes the native pointer directly to the syscall — one copy (native→kernel), or zero-copy with `transferTo` (kernel pages the file directly to the socket). Direct buffers are tracked by `Cleaner`/`PhantomReference`; GC reclaims them lazily, so they can linger. `-XX:MaxDirectMemorySize` caps native buffer total.

#### When to use / when NOT to use
Use direct buffers for large, long-lived I/O buffers in hot paths (Netty channels, gRPC, file-to-socket transfer). Use heap buffers for small, short-lived buffers (parsing, in-memory transforms). Use `transferTo` for file-to-socket (e.g., serving static files). Avoid direct buffers for one-off small reads — allocation cost dominates. Always bound direct memory with `-XX:MaxDirectMemorySize` in Netty/gRPC services.

#### Production example
A file server used `Files.copy` to send a 1 GB file — 12 seconds. Switching to `FileChannel.transferTo` (zero-copy) dropped it to 4 seconds — no user-space copies. A Netty service used heap buffers for request parsing — 30% CPU on heap→native copies; switching to pooled direct buffers (Netty's `PooledByteBufAllocator`) cut CPU to 10%. A bug: a service allocated direct buffers per request without pooling — direct memory grew to 2 GB, OOM'd; fix: pool with Netty or use heap buffers.

#### Common mistakes
- Direct buffers per request without pooling — direct memory leak.
- Not setting `-XX:MaxDirectMemorySize` — unbounded native growth, OOMKilled.
- Using heap buffers for large I/O — per-syscall copy dominates.
- Forgetting `flip()` after write before read — wrong position/limit.

#### Interview follow-ups (with model answers)

**Q:** When does zero-copy `transferTo` help?
**A:** `FileChannel.transferTo(position, count, WritableByteChannel)` asks the kernel to send file bytes directly to a socket (or another channel) without copying to user space. On Linux, it uses `sendfile(2)`. The win: for large files, you avoid two copies (kernel→user→kernel) — the kernel pages the file directly to the socket. Best for static file serving, CDN origins, and proxying large responses. Not applicable for in-memory data (no file). The file must be on a local filesystem (or a network FS that supports sendfile). On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Why are direct buffers not freed immediately on GC?
**A:** Direct buffers are tracked by `Cleaner` (or `PhantomReference` in older JDKs). GC must run to enqueue the reference, then the cleaner frees the native memory. If GC doesn't run (low heap pressure), native memory grows. This is why Netty pools direct buffers — to avoid allocation/GC churn. `-XX:MaxDirectMemorySize` caps the total; when exceeded, System.gc() is called (a known issue — set `-XX:+DisableExplicitGC` carefully). For services with high direct buffer churn, pool them. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

A Netty HTTP service has 5k req/s, each reading a 1 MB request body. Direct memory grows to 4 GB. Diagnose.

Each request allocates a direct buffer (1 MB) for the body. At 5k req/s, that's 5 GB/s of allocation. GC can't keep up — direct memory grows until `-XX:MaxDirectMemorySize` is hit (or OOM). Fix: use Netty's `PooledByteBufAllocator` (default in recent Netty) — buffers are pooled and reused, not allocated per request. Or use heap buffers for parsing (the per-syscall copy is acceptable at this size). Verify with `jcmd VM.native_memory summary` showing direct buffer growth. Add `-XX:MaxDirectMemorySize=2g` as a cap. Validate with a load test: direct memory should stabilize at the pool size, not grow. Document: pool direct buffers in high-throughput services; never allocate per request.

#### Code / config (when useful)
```java
// Zero-copy file to socket
try (var fc = FileChannel.open(Path.of("big.bin"));
     var sc = new SocketChannel(...)) {
    fc.transferTo(0, fc.size(), sc);
}

// Direct buffer for I/O
ByteBuffer buf = ByteBuffer.allocateDirect(8192);
channel.read(buf);
buf.flip();
process(buf);
```


### 77. FFM (Foreign Function & Memory API, Java 22) vs JNI — `MemorySegment`, `Linker`, downcalls, when to migrate

**Short answer:**
The Foreign Function & Memory API (FFM, JEP 454, final in Java 22) replaces JNI for most native interop. `Linker` finds and calls native functions (`Linker.nativeLinker().downcallHandle(...)`); `MemorySegment` is a typed, bounded off-heap memory region (safer than `ByteBuffer`); `SymbolLookup` loads a shared library. Unlike JNI, FFM doesn't require writing C glue or `.h` headers, has lower per-call overhead, and supports safe deallocation via `Arena`. Migrate from JNI when you need to call a native library (e.g., a crypto or ML library) — FFM is far less boilerplate and safer. Keep JNI for code that needs JVM-internal access (e.g., `DefineClass`) or where FFM's safety model is too restrictive.

#### What it is
FFM has two parts: `java.lang.foreign` (memory) and `java.lang.foreign.Linker` (function calls). `MemorySegment` is a bounded region of off-heap memory with a lifetime (`Arena`). `Linker` calls native functions via method handles. `SymbolLookup` loads a `.so`/`.dylib`/`.dll`. The API is "JNA without the JVM crash risk" — type-safe, bounds-checked, no manual `free`.

#### How it works (internals)
`Linker.downcallHandle` returns a `MethodHandle` for a native function; calling it invokes the function via libffi-style dispatch (HotSpot uses its own ABI-aware linker). `MemorySegment` accesses are bounds-checked at runtime; out-of-bounds throws `IndexOutOfBoundsException`. `Arena` controls lifetime — `Arena.ofConfined()` for single-thread, `Arena.ofShared()` for multi-thread; closing the arena frees all segments. The C memory layout is described via `ValueLayout`/`SequenceLayout`/`GroupLayout`, enabling structured access without manual offset math.

#### When to use / when NOT to use
Use FFM to call native libraries from Java — crypto, ML, system APIs, legacy C code. Far less boilerplate than JNI (no C glue, no headers), safer (bounds-checked, lifetime-managed). Migrate JNI code that's pure function calls (no JVM-internal access). Keep JNI for code needing `JNIEnv` internals (e.g., `DefineClass`, `GetObjectClass` for reflection), or where the FFM safety model is too restrictive (raw pointer arithmetic). FFM is production-ready in 22+; earlier versions are preview.

#### Production example
A crypto service called OpenSSL via JNI — 500 lines of C glue, manual memory management, occasional JVM crashes on misuse. Migrating to FFM: 50 lines of Java, no C, `Linker.nativeLinker().downcallHandle(...)` for `EVP_EncryptInit_ex`, `MemorySegment` for buffers, `Arena.ofConfined()` for per-call lifetime. Per-call overhead dropped 30% (no JNI transition), crashes eliminated (bounds-checked). A team called a Rust library via FFM — clean interop without JNI's C-only model.

#### Common mistakes
- Using FFM on pre-22 JDK — preview API, requires `--enable-preview`.
- Forgetting to close `Arena` — native memory leak.
- Using `Arena.ofConfined()` across threads — throws.
- Lying about layout — silent misread or bounds error.

#### Interview follow-ups (with model answers)

**Q:** Why is FFM safer than JNI?
**A:** JNI lets C code do anything — dereference null, overflow buffers, call `DefineClass` — and the JVM crashes. FFM bounds-checks every `MemorySegment` access, manages lifetimes via `Arena` (no manual `free`, no use-after-free), and uses `MethodHandle` dispatch (type-checked at link time). The C side never sees the JVM — it just receives and returns values. The trade-off: FFM can't do JVM-internal operations (e.g., define a class); for those, JNI is still needed. For pure function calls, FFM is strictly better. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** When would you keep JNI over FFM?
**A:** When you need JVM-internal access — `DefineClass`, `GetObjectClass` for reflection, custom classloaders, JVMTI. When the native code needs to call back into Java with complex state (FFM supports upcalls but they're more verbose). When you have an existing JNI codebase that works and migration cost outweighs benefit. When FFM's safety model is too restrictive (raw pointer arithmetic, unbounded access). For new native interop, FFM is the default. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

A Java service needs to call a Rust library (`libparser.so`) to parse a binary format. Walk through the FFM integration.

Load the library: `SymbolLookup lib = SymbolLookup.libraryLookup("libparser.so", Arena.global())`. Get the linker: `Linker linker = Linker.nativeLinker()`. Find the function: `MethodHandle parse = linker.downcallHandle(lib.findOrThrow("parse").get(), FunctionDescriptor.of(JAVA_LONG, ADDRESS, JAVA_LONG))`. Allocate a buffer: `try (var arena = Arena.ofConfined()) { MemorySegment input = arena.allocate(JAVA_BYTE, data.length); input.copyFrom(MemorySegment.ofArray(data)); long result = (long) parse.invoke(input, data.length); }`. The arena frees the buffer on close. No C glue, no headers. Validate with a unit test comparing output to a reference. Document: `Arena.ofConfined()` is single-thread; if the native code spawns threads, use `Arena.ofShared()`. Add `--enable-native-access=ALL-UNNAMED` on the command line.

#### Code / config (when useful)
```java
try (var arena = Arena.ofConfined()) {
    Linker linker = Linker.nativeLinker();
    SymbolLookup lib = SymbolLookup.libraryLookup("libfoo.so", Arena.global());
    MethodHandle strlen = linker.downcallHandle(
        lib.findOrThrow("strlen"),
        FunctionDescriptor.of(JAVA_LONG, ADDRESS));
    MemorySegment str = arena.allocateUtf8String("hello");
    long len = (long) strlen.invoke(str);
}
```


### 78. `Process` / `ProcessHandle` (Java 9+) — replacing `Runtime.exec` pitfalls

**Short answer:**
`ProcessBuilder` (Java 5+, refined in 9+) replaces `Runtime.exec` — it lets you set working directory, environment, redirect output, and chain input. `Process` is the running program; `ProcessHandle` (Java 9+) gives you its PID, parent, children, info (CPU time, command, start time), and `onExit()` (a `CompletableFuture`). The classic `Runtime.exec` pitfalls: not reading stdout/stderr (process blocks when buffer fills), not closing stdin, shell injection (passing a string instead of an array), and zombie processes (not `waitFor`).

#### What it is
`ProcessBuilder` builds a process with command, env, working dir, redirects. `Process.start()` returns a `Process`. `ProcessHandle.current()` gives the current process; `ProcessHandle.of(pid)` looks up by PID; `process.descendants()`/`children()` walk the tree. `Process.onExit()` returns a `CompletableFuture<Process>` for async completion.

#### How it works (internals)
`ProcessBuilder.start()` forks and execs the OS process. The JVM holds pipes for stdin/stdout/stderr; the OS buffers them (typically 64 KB). If the parent doesn't read stdout/stderr, the child blocks on a full buffer — the classic deadlock. `ProcessHandle` uses OS APIs (procfs on Linux, task_for_pid on macOS) for info; some info may be unavailable without elevated permissions. `onExit` is backed by a thread that `waitFor`s and completes the future.

#### When to use / when NOT to use
Use `ProcessBuilder` for spawning external processes — tools, scripts, converters. Always: read stdout/stderr (or redirect to file/null), close stdin, `waitFor` (or `onExit`), and pass command as a list (never a single string with shell). Use `ProcessHandle` for process introspection (PID, parent, children) and graceful shutdown (kill descendants). Avoid spawning processes in hot paths — fork/exec is expensive; prefer a library or service.

#### Production example
A service used `Runtime.exec("convert " + filename)` — shell injection (filenames with `;` ran arbitrary commands) and stdout not read (process blocked). Fix: `new ProcessBuilder("convert", filename).redirectErrorStream(true).start()`, read stdout fully, `waitFor`. A service spawned a worker process and didn't kill descendants on shutdown — zombies; fix: `ProcessHandle.current().descendants().forEach(ProcessHandle::destroyForcibly)` in a shutdown hook. A bug: stdin not closed — child waited for EOF forever.

#### Common mistakes
- `Runtime.exec(String)` — shell injection; use `ProcessBuilder` with a list.
- Not reading stdout/stderr — process deadlocks on full buffer.
- Not closing stdin — child waits for EOF.
- Not `waitFor` — zombie processes.

#### Interview follow-ups (with model answers)

**Q:** Why does `Runtime.exec` deadlock if you don't read stdout?
**A:** The OS buffers the child's stdout/stderr in a pipe (typically 64 KB). If the parent doesn't read, the buffer fills, and the child blocks on the next write — deadlock if the parent is waiting for the child to exit. The fix: always read stdout and stderr (in separate threads if both, or use `redirectErrorStream(true)` to merge). Or redirect to a file: `pb.redirectOutput(File)`. Or use `pb.inheritIO()` to share the parent's streams. The same applies to stdin — close it if the child doesn't need input, or it may wait for EOF. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** How do you kill a process tree on shutdown?
**A:** Use `ProcessHandle`: `Process p = pb.start(); ... Runtime.getRuntime().addShutdownHook(new Thread(() -> p.descendants().forEach(ProcessHandle::destroyForcibly))); p.onExit().thenRun(() -> ...)`. `descendants()` returns all descendants (children, grandchildren); `destroyForcibly` sends SIGKILL. Note: `p.destroy()` sends SIGTERM (graceful); `destroyForcibly` sends SIGKILL. On Linux, process groups can also be used (start with `setsid`), but `ProcessHandle` is portable. Always kill descendants if the child spawns its own children. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

A service spawns an image converter (`convert`) per request. Under load, processes pile up and the JVM hangs. Diagnose and fix.

The service likely isn't reading stdout/stderr — `convert` blocks on a full buffer, the parent waits for `waitFor`, deadlock. Fix: use `ProcessBuilder` with `redirectErrorStream(true)`, read stdout fully in a thread (or `pb.redirectOutput(File)`), close stdin, `waitFor` with a timeout (use `onExit().get(30, SECONDS)`). Add a process pool or queue to bound concurrency — spawning per request is expensive (fork/exec ~10 ms each). Better: use a Java library (TwelveMonkeys, ImageIO) instead of spawning a process. Validate with a load test: 100 concurrent requests, no hangs. Document: always read stdout/stderr, always close stdin, always `waitFor` with timeout. Add a metric on process spawn count and duration.

#### Code / config (when useful)
```java
Process p = new ProcessBuilder("convert", in, out)
    .redirectErrorStream(true)
    .start();
try (var out = p.getInputStream()) {
    out.transferTo(System.out);
}
if (!p.waitFor(30, TimeUnit.SECONDS)) p.destroyForcibly();
```


### 79. JFR / `jcmd` / async-profiler — production profiling without attach overhead

**Short answer:**
Java Flight Recorder (JFR) is the built-in low-overhead profiler (≤1% in production) recording events (GC, allocation, lock contention, I/O, method samples) to a `.jfr` file. `jcmd` is the command-line tool to control a running JVM (start/stop JFR, dump heap, thread dump, native memory). async-profiler is a third-party sampling profiler (CPU, allocation, lock) with <1% overhead, producing flame graphs. JFR is the default for production profiling — start it always-on with `StartFlightRecording`; async-profiler for deep CPU/allocation flame graphs when JFR isn't enough.

#### What it is
JFR is a HotSpot feature (open-source since JDK 11) that records structured events to a binary file, analyzed with JDK Mission Control (JMC) or `jfr print`. `jcmd` is the universal JVM control tool (replaces `jmap`/`jstack` for many uses). async-profiler is a `perf`-based sampling profiler that produces flame graphs, with agents for CPU, allocation, lock, and wall-clock profiling.

#### How it works (internals)
JFR uses thread-local buffers written to a global ring buffer, flushed to disk periodically — no global lock on the hot path, so overhead is <1%. Events include `jdk.GCPhasePause`, `jdk.ObjectAllocationSample`, `jdk.JavaMonitorEnter`, `jdk.FileRead`, `jdk.SocketRead`, and method samples (`jdk.ExecutionSample`). `jcmd` sends commands via the JVM's attach mechanism (a Unix domain socket). async-profiler uses `perf_event_open` on Linux to sample kernel + user stacks, avoiding the JVM's safepoint bias (HotSpot samples at safepoints, missing inlined methods).

#### When to use / when NOT to use
Always-on JFR in production: `-XX:StartFlightRecording=filename=...,settings=profile,maxsize=200m,maxage=24h`. Use `jcmd` for on-demand dumps (heap, thread, JFR). Use async-profiler for CPU/allocation flame graphs when JFR's view isn't enough, especially for native frames or off-CPU analysis. Avoid `jstack`/`jmap` in production — they trigger safepoints; prefer `jcmd Thread.print` and JFR.

#### Production example
A service had p99 spikes; JFR `jdk.GCPhasePause` showed 200 ms G1 pauses correlated with humongous allocations from a Kafka deserializer. Fix: smaller batches. A service showed high CPU; async-profiler flame graph revealed 40% in `String.getBytes` from JSON serialization — switched to a binary format. A team used `jmap -histo` in prod — it triggered a 500 ms safepoint; switching to `jcmd GC.class_histogram` (concurrent) eliminated the pause.

#### Common mistakes
- Not running JFR always-on — you miss the incident window.
- Using `jmap`/`jstack` in production — safepoint pauses.
- async-profiler without `--framebuf` — dropped samples on hot paths.
- JFR with `settings=profile` for long runs — large files; use `maxsize`/`maxage`.

#### Interview follow-ups (with model answers)

**Q:** How do you start JFR in production and what overhead does it add?
**A:** `-XX:StartFlightRecording=filename=/var/log/app.jfr,settings=profile,maxsize=200m,maxage=24h,dumponexit=true`. Overhead is <1% CPU in profile mode (more events), <0.1% in default mode. JFR uses thread-local buffers, so no global lock. The `maxsize`/`maxage` rotate the file. Always-on JFR is the recommended setup — you capture incidents that already happened. Analyze with JDK Mission Control (GUI) or `jfr print --events jdk.GCPhasePause app.jfr`. For ad-hoc recording: `jcmd PID JFR.start name=rec duration=60s filename=/tmp/r.jfr`. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** When is async-profiler better than JFR?
**A:** For CPU/allocation flame graphs with native frames — async-profiler uses `perf_event_open`, sampling kernel + user stacks without safepoint bias. JFR's method samples are at safepoints, missing inlined methods and some native frames. async-profiler also does wall-clock profiling (off-CPU analysis — what's blocking), which JFR doesn't directly. async-profiler produces flame graphs directly (`--flame`); JFR needs JMC or `jfr print` + a flame graph tool. For always-on production, JFR is better (structured events, low overhead); for deep one-off analysis, async-profiler. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

A service has intermittent 500 ms p99 spikes with no GC pressure. JFR is always-on. Walk through the diagnosis.

Pull the JFR file covering the spike window (`jcmd PID JFR.dump name=rec filename=/tmp/spike.jfr`). In JMC, filter `jdk.GCPhasePause` — confirm no GC pause. Check `jdk.JavaMonitorEnter` — lock contention? Check `jdk.SocketRead`/`jdk.FileRead` — slow I/O? Check `jdk.ExecutionSample` during the spike — what method is hot? If nothing, the spike may be off-CPU (blocking) — use async-profiler in wall-clock mode (`-e wall`) to find what's blocking. Common culprits: a slow downstream call (check `jdk.SocketRead`), a synchronized block (check `jdk.JavaMonitorEnter`), or a safepoint (check `jdk.SafepointBegin`). Document the timeline: alert time, spike time, JFR event correlation. Add a regression alert on the metric. Validate the fix with a load test reproducing the spike.

#### Code / config (when useful)
```text
-XX:StartFlightRecording=filename=/var/log/app.jfr,settings=profile,maxsize=200m,maxage=24h,dumponexit=true
# On-demand:
jcmd PID JFR.start duration=60s filename=/tmp/r.jfr
jcmd PID Thread.print                # thread dump (concurrent)
jcmd PID GC.class_histogram          # class histogram (no safepoint)
```


### 80. Heap dump analysis with Eclipse MAT — dominator tree, GC roots, leak suspects, `OQL`

**Short answer:**
Eclipse Memory Analyzer Tool (MAT) is the standard heap dump analyzer. The **dominator tree** shows objects that retain the most shallow/retained heap — the biggest retainers are leak suspects. **GC roots** are entry points (stack, statics, JNI, threads) — an object unreachable from roots is collectable. **Leak suspects** is MAT's automated report identifying likely leaks (large retained sets, suspicious classloaders). **OQL** (Object Query Language) is SQL-like querying of heap objects (`SELECT * FROM java.lang.String WHERE count > 1000`). Workflow: open `.hprof`, run leak suspects, drill into dominator tree, find the path to GC roots, fix the reference.

#### What it is
MAT parses `.hprof` heap dumps (from `jcmd GC.heap_dump`, `jmap -dump`, or `-XX:+HeapDumpOnOutOfMemoryError`). It builds indexes (dominator tree, inbound/outbound references) for fast queries. The leak suspects report is a heuristic analysis. OQL is a query language for ad-hoc analysis.

#### How it works (internals)
The dominator tree is computed by a reachability analysis: object A dominates B if every path to B goes through A. Retained heap is the memory freed if A were collected. GC roots are: stack locals, static fields, JNI global refs, monitor-locked objects, JVM internal tables. MAT's leak suspects look for: large single retainers, duplicate classloaders, large collections, `ThreadLocal` retention. OQL queries the parsed object graph using a SQL-like syntax with `FROM` (class), `WHERE` (predicate), `SELECT` (fields).

#### When to use / when NOT to use
Use MAT for any heap leak investigation — open the dump, run leak suspects, drill down. Use OQL for targeted queries ("find all `HashMap` entries with key containing 'cache'"). Use the dominator tree to find the biggest retainers. Avoid MAT for very large dumps (>32 GB) without enough heap (MAT needs ~2× the dump size). For production, capture with `jcmd` (no safepoint pause) and analyze offline.

#### Production example
A service OOM'd after 7 days; `-XX:+HeapDumpOnOutOfMemoryError` produced a 4 GB dump. MAT leak suspects: a `ConcurrentHashMap` retaining 2 GB of `CustomerProfile` objects, retained by a static `Cache` field. Path to GC roots: `Cache` → `profiles` map → entries. Fix: replace with Caffeine (bounded, TTL). A classloader leak showed 50 `WebappClassLoader` instances in MAT — confirmed hot-deploy leak; fixed by deregistering drivers. OQL found all `String` instances > 10k chars — a deserializer caching huge strings.

#### Common mistakes
- Not capturing a dump before restart — the leak is gone.
- MAT without enough heap — fails on large dumps (use `-Xmx8g` for MAT).
- Stopping at "leak suspects" — drill into the dominator tree and path to roots.
- Ignoring duplicate classloaders — Metaspace leak, not heap.

#### Interview follow-ups (with model answers)

**Q:** What is the dominator tree and how do you use it?
**A:** The dominator tree shows objects that retain the most memory. Object A dominates B if every path from a GC root to B goes through A. The retained heap of A is the memory freed if A were collected. In MAT, sort by retained heap — the top entries are the biggest retainers. Drill into a retainer to see its children (dominated objects). For a leak, find the largest retainer, then "Path to GC Roots" → "exclude weak/soft references" to see what's holding it. The path tells you the code to fix. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** How do you use OQL in MAT?
**A:** OQL is SQL-like: `SELECT * FROM java.util.HashMap WHERE size() > 10000` finds large maps. `SELECT s, s.count FROM java.lang.String s WHERE s.count > 10000` finds large strings. `SELECT * FROM com.example.Cache` finds all instances of a class. OQL supports `FROM` (class or `java.lang.Object` for all), `WHERE` (JavaScript-like predicates), `SELECT` (fields or `*`). It's useful for targeted queries that the dominator tree doesn't surface. For complex analysis, combine OQL with the dominator tree and path-to-roots. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

A service OOM'd; you have a 6 GB heap dump. Walk through the analysis in MAT.

Open in MAT with `-Xmx12g` (2× dump size). Run "Leak Suspects" report — it identifies the largest retainer. Drill into the dominator tree, sort by retained heap. The top retainer is a `ConcurrentHashMap` retaining 4 GB. Right-click → "Path to GC Roots" → "exclude weak/soft references" — shows the path: `Cache` (static field) → `profiles` map → entries. The static field is the leak. Fix: replace with Caffeine (bounded, TTL), or clear the map on a schedule. If the leak is a classloader (Metaspace), check "Duplicate Classes" report — multiple `WebappClassLoader` instances indicate hot-deploy leak. Use OQL to find specific objects: `SELECT * FROM com.example.Customer WHERE id > 1000000`. Document the timeline: alert → dump → analysis → fix. Add a heap-after-full-GC metric alert to catch the next leak early.

#### Code / config (when useful)
```text
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/var/log/oom.hprof
# On-demand:
jcmd PID GC.heap_dump /tmp/heap.hprof
# MAT launch: MemoryAnalyzer.ini
-Xmx12g
```


### 81. `jlink` / `jmod` / `jpackage` — custom runtime images and native installers

**Short answer:**
`jlink` (Java 9+) assembles a custom JRE from selected modules — a 40 MB image instead of a 200 MB JDK, with only the modules your app needs. `jmod` is the module file format (`.jmod`) used by `jlink`; the JDK itself ships as `.jmod` files. `jpackage` (Java 14+) wraps a `jlink`-produced runtime + your app into a platform-native installer (`.deb`, `.rpm`, `.msi`, `.pkg`, `.dmg`, `.exe`). Use `jlink` for container images (smaller base) and CLI tools; use `jpackage` for desktop apps and on-prem server installs.

#### What it is
`jlink` takes a list of modules (from the JDK's `.jmod` files and your app's modular JAR) and produces a self-contained `bin/java` + `lib/` runtime. `jmod` is the format for module binaries (compiled classes, native libs, config); `jmod create` builds one. `jpackage` wraps the runtime + app into a native installer with launcher scripts and icons.

#### How it works (internals)
`jlink` reads `.jmod` files, resolves module dependencies (transitive), strips debug info (optional), and writes a `bin/java` + `lib/modules` image. The image is platform-specific (cross-targeting requires the target platform's `.jmod` files via `--module-path`). `jpackage` uses platform tools (WiX on Windows, `dpkg-deb`/`rpmbuild` on Linux, `pkgbuild` on macOS) to build the installer; it embeds the `jlink` image and a launcher that runs `java -m myapp`.

#### When to use / when NOT to use
Use `jlink` for: container images (smaller, faster startup), CLI tools (single download), embedded devices (minimal footprint). Use `jpackage` for: desktop apps (native installer with uninstaller), on-prem server installs (ops-friendly). Don't use `jlink` if your app uses reflection on non-modular code — `jlink` can't know what to include; use `jlink` with `--add-modules` carefully or stick with a full JDK. For Spring Boot, AOT + native image (GraalVM) is an alternative for minimal footprint.

#### Production example
A CLI tool shipped as a 200 MB JDK + 5 MB JAR. Switching to `jlink --add-modules java.base,java.net,java.nio --launcher mycli=myapp/cli --output mycli-image` produced a 40 MB self-contained binary. A desktop app used `jpackage --type msi --module-path ... --name MyApp --input app.jar --main-jar app.jar` to produce a Windows installer with uninstaller. A container image dropped from 200 MB (full JDK) to 50 MB (`jlink` image), speeding deploys.

#### Common mistakes
- `jlink` with reflection-heavy apps — missing modules at runtime.
- Not cross-targeting — `jlink` on Linux for a Windows target needs Windows `.jmod` files.
- Forgetting `--strip-debug` — larger image.
- `jpackage` without a launcher — the installer runs but the app doesn't launch.

#### Interview follow-ups (with model answers)

**Q:** How do you handle reflection with `jlink`?
**A:** `jlink` does closed-world analysis — it includes only the modules you list and their transitive deps. If your app reflects on a class in a module not in the graph, you get `ClassNotFoundException` at runtime. Solutions: (1) explicitly `--add-modules` the modules you reflect on; (2) use a `module-info` that requires them; (3) for libraries that reflect (Spring, Hibernate), use `--add-modules ALL-MODULE-PATH` or stick with a full JDK. For Spring Boot, use AOT processing (3.1+) which reduces reflection, making `jlink`/native image viable. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** When is `jpackage` worth using over a Docker image?
**A:** For desktop apps (end-users install via `.msi`/`.dmg` with uninstaller) and on-prem server installs (ops team installs via `.rpm` with systemd integration). `jpackage` produces a native installer with launcher, icons, and uninstaller — a polished experience. For cloud-native services, a Docker image (with a `jlink` base) is simpler. `jpackage` is also useful for distributing a service as a `.rpm`/`.deb` for ops teams that prefer package managers over containers. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

A CLI tool needs to ship as a single download for Linux, macOS, and Windows. Walk through the build.

For each platform, run `jlink` with the target platform's JDK `.jmod` files (cross-targeting): `jlink --module-path $TARGET_JDK/jmods --add-modules java.base,java.net --launcher mycli=myapp/cli --strip-debug --compress=2 --output mycli-$OS`. The result is a self-contained directory with `bin/mycli` and `bin/java`. Zip and distribute. For native installers, use `jpackage --type deb` (Linux), `--type pkg` (macOS), `--type msi` (Windows), with `--module-path` and `--main-jar`. CI builds all three platforms (use Docker for cross-targeting or per-platform runners). Document: `jlink` images are platform-specific; one per OS. Validate by running the CLI on each platform. Add a smoke test in CI.

#### Code / config (when useful)
```bash
jlink --module-path $JAVA_HOME/jmods:app \
  --add-modules myapp.cli \
  --launcher mycli=myapp/cli \
  --strip-debug --compress=2 \
  --output mycli-image

jpackage --type msi --name MyApp --input app --main-jar app.jar \
  --runtime-image mycli-image --win-menu
```


### 82. CDS / AppCDS / `UseStringDeduplication` / `CompactStrings` — startup and footprint

**Short answer:**
Class Data Sharing (CDS) pre-processes JDK classes into a shared archive (`classes.jsa`) mapped at startup — faster startup, smaller per-JVM footprint. Application CDS (AppCDS) extends this to your app's classes. `UseStringDeduplication` (G1) dedupes equal `String` values to one backing `byte[]`, cutting heap for string-heavy apps. `CompactStrings` (default on since 9) stores strings as Latin-1 (1 byte/char) when possible instead of UTF-16 (2 bytes/char) — ~50% heap reduction for ASCII-heavy apps. All four reduce footprint or startup with low runtime cost.

#### What it is
CDS: JDK classes archived into a shared memory-mapped file. AppCDS: app classes archived too. `UseStringDeduplication`: G1 scans the heap for duplicate `String` values and points them to the same `byte[]`. `CompactStrings`: `String` internal storage is `byte[]` with a coder flag (Latin-1 or UTF-16), not `char[]`.

#### How it works (internals)
CDS: `-Xshare:dump` produces `classes.jsa`; `-Xshare:on` (default) maps it at startup, skipping class loading for archived classes. AppCDS: `-XX:DumpLoadedClassList` then `-Xshare:dump -XX:SharedArchiveFile=app.jsa` with the class list. `UseStringDeduplication`: G1's concurrent phase scans for duplicate `String.value` arrays and updates references — small CPU cost, big heap win for string-heavy apps. `CompactStrings`: `String` uses `byte[] value` + `byte coder`; Latin-1 strings use 1 byte/char, UTF-16 uses 2; most ASCII strings stay Latin-1.

#### When to use / when NOT to use
Enable CDS/AppCDS for short-lived JVMs (CLI, serverless, microservices) — startup win. Enable `UseStringDeduplication` for string-heavy services (caches, logs, JSON) — measure heap reduction vs CPU. `CompactStrings` is on by default — keep it; disable only if your strings are mostly non-Latin-1 (rare). For containers, AppCDS reduces per-pod memory.

#### Production example
A CLI tool startup dropped from 1.2 s to 400 ms with AppCDS — the archive pre-loaded 5000 classes. A cache service with 50 M `String` entries enabled `UseStringDeduplication` — heap dropped from 8 GB to 5 GB, CPU rose 3%. A JSON-heavy service relied on `CompactStrings` (default) — 40% heap reduction vs pre-9. A team disabled `CompactStrings` for a Chinese-text service (UTF-16) — no benefit, restored.

#### Common mistakes
- Not using AppCDS for short-lived JVMs — missing startup win.
- `UseStringDeduplication` on CPU-bound apps — small heap win, CPU cost.
- Disabling `CompactStrings` unnecessarily — most apps benefit.
- CDS archive out of date (different JDK) — JVM falls back to no-share, no error.

#### Interview follow-ups (with model answers)

**Q:** How do you set up AppCDS for a Spring Boot app?
**A:** Run the app once with `-XX:DumpLoadedClassList=classes.lst` to capture the class list. Then `java -Xshare:dump -XX:SharedArchiveFile=app.jsa -XX:SharedClassListFile=classes.lst -cp app.jar`. Run with `-Xshare:on -XX:SharedArchiveFile=app.jsa`. For Spring Boot 3.1+ with AOT, the class list is more stable (less reflection). Measure startup before/after — typically 30–50% faster. In containers, bake the archive into the image. The archive must match the JDK version; rebuild on JDK updates. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** When is `UseStringDeduplication` worth it?
**A:** When your app has many duplicate strings (caches, JSON keys, log messages) and heap is a constraint. G1's dedup scans the heap concurrently and points duplicate `String.value` arrays to one — big heap win for string-heavy apps (30–50% reduction). The CPU cost is small (1–3%). It's not worth it for CPU-bound apps with few duplicates, or for non-G1 collectors (it's G1-only; ZGC/Shenandoah have their own). Measure heap before/after. With `CompactStrings` (default), dedup is less impactful (Latin-1 strings are already small). On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

A serverless function (AWS Lambda) has 2 s cold starts; the team wants sub-500 ms. Walk through the optimization.

Use AppCDS: capture the class list, dump the archive, and configure the Lambda to load it. Expected 30–50% startup reduction. Combine with SnapStart (if on Java 21+): SnapStart snapshots the JVM after init, restoring on cold start — sub-100 ms. If SnapStart isn't available, AppCDS + `CompactStrings` (default) + minimal class loading. Measure with `java -Xlog:class+load` to see how many classes load on cold start. Reduce class loading: avoid reflection-heavy libraries, use AOT (Spring Boot 3.1+). Validate with a cold-start benchmark. Document: AppCDS archive must match the JDK; rebuild on updates. For Lambda, bake the archive into the layer.

#### Code / config (when useful)
```bash
# AppCDS
java -XX:DumpLoadedClassList=classes.lst -cp app.jar -jar app.jar
java -Xshare:dump -XX:SharedArchiveFile=app.jsa \
     -XX:SharedClassListFile=classes.lst -cp app.jar
java -Xshare:on -XX:SharedArchiveFile=app.jsa -cp app.jar -jar app.jar

# String dedup (G1)
-XX:+UseStringDeduplication
```


### 83. GraalVM native image + Spring AOT — closed-world analysis, reflection config, when native wins

**Short answer:**
GraalVM Native Image compiles Java ahead-of-time to a standalone native binary — closed-world analysis means it only includes reachable code, eliminating the JIT and class loading at runtime. Startup is milliseconds, footprint is megabytes, but peak throughput is lower (no JIT) and build time is long. Reflection config (`reflect-config.json`, `resource-config.json`) is required for any reflection the analysis can't see — Spring's AOT processing (3.1+) generates this automatically. Native wins for: short-lived functions (CLI, serverless), constrained memory (containers, edge), and instant-start requirements. It loses for: long-running throughput-bound services (no JIT peak), heavy reflection, or fast-changing code (rebuild is slow).

#### What it is
Native Image is GraalVM's AOT compiler: it analyzes the application at build time, resolves all reachable classes/methods, and produces a native binary with a SubstrateVM runtime. No JIT, no class loading, no bytecode interpretation at runtime. Spring AOT (3.1+) pre-processes the app to reduce reflection (generates concrete bean definitions, reflection configs), making Spring apps native-compatible.

#### How it works (internals)
At build time, Native Image starts from a main entry point, performs reachability analysis (static initializers, virtual calls, reflection, JNI), and includes only reachable code. Reflection must be declared in `reflect-config.json` (or auto-generated by AOT) — the analysis can't see dynamic `Class.forName`. The binary uses SubstrateVM (a minimal GC, no JIT). Peak throughput is 10–30% lower than HotSpot+JIT because there's no profile-guided optimization. Build time is minutes (vs seconds for a JAR). Spring AOT generates `META-INF/native-image/*.json` configs and AOT bean definitions.

#### When to use / when NOT to use
Use native for: serverless (Lambda cold start), CLI tools (instant start), constrained memory (containers, edge), and instant-start requirements (Kubernetes scale-to-zero). Avoid for: long-running throughput-bound services (no JIT peak), heavy reflection (config burden), fast-changing code (slow rebuilds), or apps needing dynamic class loading. For Spring Boot 3.1+, AOT makes native viable; measure throughput vs startup trade-off.

#### Production example
A Lambda function had 3 s cold starts (JVM init + Spring context). With Spring AOT + GraalVM native, cold start dropped to 50 ms — sub-100 ms including container init. Trade-off: peak throughput was 15% lower (no JIT), but for a request-scoped Lambda, that's acceptable. A CLI tool shipped as a 20 MB native binary with instant start. A long-running service tried native — throughput dropped 20%, reverted to HotSpot.

#### Common mistakes
- Native for a long-running throughput-bound service — no JIT peak.
- Missing reflection config — runtime errors.
- Not measuring peak throughput — native is slower for sustained load.
- Slow rebuilds in the dev loop — use native only for prod builds.

#### Interview follow-ups (with model answers)

**Q:** When does native image lose to HotSpot?
**A:** For long-running, throughput-bound services: native has no JIT, so peak throughput is 10–30% lower than HotSpot after warmup. HotSpot's C2 JIT profile-guided optimization beats AOT for sustained load. Native also struggles with heavy reflection (config burden) and dynamic class loading (not supported). For serverless, CLI, or scale-to-zero, native wins (instant start, small footprint). For a service running for days at high QPS, HotSpot wins. Measure both for your workload. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** How does Spring AOT make native viable?
**A:** Spring traditionally uses heavy reflection (bean creation, `@Configuration` proxies, `@Conditional`). Native Image can't see this reflection, so you'd hand-write `reflect-config.json` for hundreds of classes. Spring AOT (3.1+) processes the context at build time, generating concrete bean definitions and reflection configs (`META-INF/native-image/*.json`), reducing runtime reflection. This makes Spring apps native-compatible without manual config. Combined with GraalVM Native Image Build Tools (Maven/Gradle plugins), `mvn -Pnative package` produces a native binary. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

A Kubernetes service scales to zero; cold starts are 8 s (JVM + Spring context). The team wants sub-1 s. Walk through the native image migration.

Use Spring Boot 3.1+ with AOT. Add the GraalVM Native Image Maven plugin: `mvn -Pnative -Dnative-image.build=package`. The build produces a native binary. Test: cold start should be <500 ms. Measure peak throughput — expect 10–30% lower than HotSpot. If the service is request-scoped and scales to zero, the trade-off is worth it. Audit for reflection: third-party libraries may need manual `reflect-config.json` entries (use the Tracing Agent: `java -agentlib:native-image-agent=config-output-dir=... -jar app.jar` to capture configs). Test thoroughly — native doesn't load classes dynamically. Validate with a load test comparing HotSpot vs native on cold start and sustained throughput. Document: native is for scale-to-zero; for always-on, HotSpot wins. Add a CI build for native to catch config drift.

#### Code / config (when useful)
```bash
# Spring Boot 3.1+ native build
mvn -Pnative -Dnative-image.build=package
# Tracing agent to capture reflection config
java -agentlib:native-image-agent=config-output-dir=src/main/resources/META-INF/native-image \
     -jar target/app.jar
```


### 84. `SecurityManager` deprecation (Java 17+) — what replaces it for sandboxing

**Short answer:**
`SecurityManager` is deprecated for removal (JEP 411, Java 17) because it's complex, rarely used correctly, and incompatible with modern Java features (records, sealed types, modules). It was designed for applets and untrusted code — a model that's no longer relevant. For sandboxing untrusted code, the replacement is **OS-level isolation**: containers (Docker/Podman), separate processes, or VMs. For privileged operations in trusted code, use `AccessController` (also deprecated) replaced by **module boundaries** (`ModuleLayer`, `--add-opens` controlled by the deployer) and library-level permission checks. There's no direct in-JVM sandbox replacement — the industry moved to OS-level isolation.

#### What it is
`SecurityManager` checked permissions before privileged operations (file I/O, network, reflection). `AccessController.doPrivileged` ran a block with elevated permissions. The deprecation (JEP 411) removed the ability to set a custom `SecurityManager` at runtime; full removal is targeted for a later release. The JDK still uses an internal `SecurityManager` for some checks, but apps can't rely on it.

#### How it works (internals)
`SecurityManager.checkPermission(perm)` was called before each privileged operation; a `Policy` granted permissions per code source (URL). The model assumed code from different URLs had different trust — broken by modules (code is identified by module, not URL) and by the reality that all app code runs in one trust domain. The deprecation removes `System.setSecurityManager`, `Policy.setPolicy`, and `AccessController.doPrivileged` (the latter still works in JDK 21 but is deprecated).

#### When to use / when NOT to use
For untrusted code (plugins, scripts): use OS isolation — a container per tenant, a separate process, or a VM. For privileged operations in trusted code: use module boundaries (`ModuleLayer.defineModules` with restricted `--add-opens`), or library-level checks (e.g., a custom permission check before a sensitive method). For Java agents and instrumentation: use the `java.lang.instrument` API with explicit deployer consent (`-javaagent`). Never rely on `SecurityManager` in new code.

#### Production example
A multi-tenant service ran user-uploaded scripts in a `SecurityManager` sandbox — complex, leaky, and broken by Java modules. Migrated to a container-per-tenant model: each tenant's script runs in a Docker container with seccomp/AppArmor, network egress restricted, CPU/memory bounded. Simpler, more secure, and aligned with industry practice. A library used `AccessController.doPrivileged` for a privileged file read — replaced with an explicit permission check (custom annotation + check) and module-level `requires` to gate access.

#### Common mistakes
- Using `SecurityManager` in new code — deprecated, will be removed.
- Assuming `AccessController` is the replacement — it's also deprecated.
- Sandboxing in-JVM without OS isolation — escapes are common.
- Not updating `SecurityManager`-based libraries — they'll break on removal.

#### Interview follow-ups (with model answers)

**Q:** Why was `SecurityManager` deprecated, and what's the replacement?
**A:** It was complex, rarely used correctly (most apps set it to `null` or a permissive policy), incompatible with modules (code identity changed from URL to module), and the threat model (untrusted applets) is gone. The replacement is OS-level isolation: containers, separate processes, or VMs for untrusted code; module boundaries (`ModuleLayer`, `--add-opens`) for trusted-code privilege. There's no in-JVM sandbox replacement — the JDK team decided the JVM isn't the right boundary for untrusted code. For libraries, use explicit permission checks, not `AccessController`. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** How do you sandbox user-uploaded scripts without `SecurityManager`?
**A:** OS isolation: run each script in a container (Docker/Podman) with seccomp (limit syscalls), AppArmor/SELinux (MAC), network egress restricted (iptables/NetworkPolicy), CPU/memory bounded (cgroups), and a timeout. For GraalVM polyglot, use the `Context` API with resource limits (`Context.newBuilder().allowHostAccess(HostAccess.NONE)`) — a language-level sandbox for embedded scripts. For Java scripts, use a separate JVM process with restricted `--add-opens` and module layer. The JVM itself is not a security boundary. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

A SaaS lets users upload custom rules (Java snippets) executed server-side. The team used `SecurityManager` to sandbox. With deprecation, what's the migration?

Migrate to OS isolation: each rule execution runs in a short-lived container (Docker, gVisor for stronger isolation, or Firecracker microVM) with: seccomp profile (only necessary syscalls), no network egress (or restricted to allowlist), CPU/memory/time bounds (cgroups + timeout), read-only filesystem except a scratch dir. For high-throughput, use a warm pool of containers. For GraalVM polyglot (if rules are JS/Python), use the `Context` API with `HostAccess.NONE` and resource limits — faster than container-per-rule. For Java rules, consider a separate JVM process with a restricted module layer. Document: the JVM is not a security boundary; rely on OS/kernel isolation. Validate with a penetration test (try to escape the sandbox). Add monitoring on rule execution time and resource use.

### 85. `jar` manifest, `Class-Path`, `Main-Class`, sealed packages, multi-release JARs

**Short answer:**
A JAR's `META-INF/MANIFEST.MF` carries metadata: `Main-Class` (entry point for `java -jar`), `Class-Path` (relative URLs for dependent JARs, used by `java -jar`), `Sealed: true` (sealed packages — a package can be sealed to prevent splits across JARs, important for `instanceof` consistency). Multi-release JARs (Java 9+) have `META-INF/versions/<N>/` per-version overrides — a class can have a Java 9 version using `StackWalker` and a Java 8 base version, the JVM loads the highest matching version. `jar` tool and `maven-jar-plugin` generate these. Sealed packages are now superseded by modules (`module-info`), but still useful for non-modular libraries.

#### What it is
The manifest is a text file (RFC 822-style headers) in `META-INF/MANIFEST.MF`. Key attributes: `Manifest-Version`, `Main-Class`, `Class-Path`, `Sealed`, `Implementation-Version`, `Build-Jdk`. Multi-release JARs add `Multi-Release: true` to the manifest and per-version overrides in `META-INF/versions/N/`. Sealed packages declare `Sealed: true` in the manifest's per-package sections.

#### How it works (internals)
`java -jar app.jar` reads `Main-Class`, loads it, calls `main(String[])`. `Class-Path` adds the listed JARs to the classpath (only with `-jar`, not `-cp`). Sealed packages: a class loaded from a sealed package must come from the same JAR — prevents split packages (two JARs with the same package), which breaks `instanceof` and module resolution. Multi-release: the JVM, when running on version N, loads classes from `META-INF/versions/N/` if present, falling back to the base. The `jar` tool's `--release N` flag compiles for version N and places the result in `versions/N/`.

#### When to use / when NOT to use
Use `Main-Class` for executable JARs (`java -jar`). Use `Class-Path` only with `-jar` (rare; prefer a fat JAR or classpath). Use sealed packages for libraries that must prevent splits (e.g., a security library). Use multi-release JARs when a library supports multiple Java versions with version-specific optimizations (e.g., `StackWalker` on 9+, fallback on 8). Avoid `Class-Path` in fat JARs — Spring Boot's loader uses its own layout.

#### Production example
A library supported Java 8 and 9+ — a multi-release JAR had the base `Optional.class` (Java 8 fallback) and `META-INF/versions/9/Optional.class` using `StackWalker` for faster stack inspection. The JVM loaded the 9+ version on Java 9+, the base on 8. A security library sealed its packages to prevent a malicious JAR from injecting classes into its namespace. A CLI tool used `Main-Class` for `java -jar tool.jar` — one-command launch.

#### Common mistakes
- `Class-Path` with `-cp` (ignored — only works with `-jar`).
- Multi-release JAR with mismatched API between versions — `NoSuchMethodError` on the wrong version.
- Sealed package without `Sealed: true` in manifest — not actually sealed.
- Forgetting `Multi-Release: true` in manifest — overrides ignored.

#### Interview follow-ups (with model answers)

**Q:** How do multi-release JARs work and when are they useful?
**A:** A multi-release JAR has `Multi-Release: true` in the manifest and per-version overrides in `META-INF/versions/N/`. When running on Java N or higher, the JVM loads the override; on a lower version, the base. This lets a library support Java 8 with a base class and Java 9+ with a version using `StackWalker`, `ProcessHandle`, or other new APIs — same JAR, no separate builds. The override must have the same API (same public methods) as the base, or you get `NoSuchMethodError` when the wrong version loads. Build with `jar --release N` or the `maven-jar-plugin`'s `multiRelease` config. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** What are sealed packages and why do they matter?
**A:** A sealed package (`Sealed: true` in the manifest's per-package section) prevents the package from being split across multiple JARs — all classes in the package must come from the same JAR. This matters for security (a malicious JAR can't inject a class into a sealed package) and for `instanceof` consistency (split packages can cause `ClassCastException` when the same package is loaded from two JARs with different classloaders). Modules (`module-info`) make packages sealed by default and forbid split packages — the modern approach. For non-modular libraries, sealed packages are still useful. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

A library supports Java 8 and 17+. The team wants to use `ProcessHandle` (Java 9+) for process info on 9+ and a fallback on 8. Walk through the multi-release JAR build.

Create the base `ProcessInfo` class in `src/main/java` (Java 8 compatible) using `ManagementFactory` for process info. Create the override in `src/main/java9/com/lib/ProcessInfo.java` using `ProcessHandle.current()`. Configure `maven-jar-plugin` with `multiRelease: true` and `manifestEntries: Multi-Release: true`. The build places the Java 9 version in `META-INF/versions/9/com/lib/ProcessInfo.class`. On Java 8, the base loads; on Java 9+, the override. Both must have the same public API. Test on both Java versions. Document: multi-release JARs are a maintenance burden — only use them if you must support old Java versions; for new libraries, target Java 17+ and skip the override. Validate with a CI matrix on Java 8 and 17.

#### Code / config (when useful)
```text
Manifest-Version: 1.0
Main-Class: com.example.Main
Class-Path: lib/dep1.jar lib/dep2.jar
Multi-Release: true
Sealed: true

Name: com/example/security/
Sealed: true
```

## Scenario-based interview drills

### S1. Kafka consumer rebalance storm during coordinated JVM pause

**Situation:** A settlement service consumes 40 partitions from `ledger-posted` with `max.poll.interval.ms=300000`. During market close, G1 remark pauses exceed 90 seconds on half the pods while legacy pods misconfigured. Consumer group enters continuous rebalance; duplicate settlement messages hit downstream idempotency gaps and finance opens a Sev-1.

**What they're testing:** Whether you connect JVM pause telemetry to Kafka consumer liveness, understand at-least-once semantics under rebalance, and can design processing that survives duplicate delivery without blaming 'Kafka is flaky.'

**How to structure your answer:**
- Stabilize consumer group first — pause processing flag, drain in-flight, avoid mass session timeout.
- Correlate `-Xlog:gc*` pause timestamps with consumer `RevokePartitions` / `Member failed` logs.
- Separate GC tuning from application fix — remark pauses vs long synchronous DB work in poll loop.
- Harden idempotency — business key dedup table, outbox, or transactional consume pattern.
- Post-incident: JFR GC pause alerts, reduce `max.poll.records`, move heavy work async with pause/resume.

**Model answer:** I would start by stopping the bleeding: temporarily scale consumers down to a stable subset or increase `session.timeout.ms` only as a tactical measure while knowing it masks slow processing. Pull GC logs from affected pods and overlay with Kafka consumer logs — if rebalance begins within seconds of remark pauses, the root cause is stop-the-world exceeding `max.poll.interval.ms`, not broker issues. On legacy pods still on Parallel GC with undersized heap, full GCs during close-of-market traffic amplify the problem; unify JVM flags before micro-tuning consumer properties. Application-side, inspect the poll loop: anti-pattern is one poll handling thousands of ledger rows with synchronous JDBC and HTTP calls to a pricing service — even without GC, that exceeds interval. Refactor to process smaller batches, commit offsets after idempotent write to `settlement_id` unique constraint, and use a dedup store keyed by business idempotency key. For duplicates already released, run reconciliation job comparing Kafka offsets to settlement table. Long-term, enable JFR `jdk.GCHeapSummary` and Micrometer consumer lag alert with GC pause correlation dashboard. Document that EOS Kafka transactions do not span JDBC without complex coupling — outbox plus idempotent consumer is industry default. Communication: hourly updates with lag metrics and duplicate count estimate.

**Common weak answers:** Restarting all consumers repeatedly, increasing heap without GC log review, disabling idempotency checks 'temporarily,' or proposing 'switch to batch Kafka' without addressing poll interval math.

**Follow-up probes (with answers):**

**Q:** Would you lower `max.poll.interval.ms` to fail faster?
**A:** No — lowering makes benign slow batches trigger rebalance faster, worsening storms. Increase interval only as tactical relief while fixing processing time and GC. The correct knob is faster per-poll work, smaller batches, and GC pause reduction. Fail-fast on interval is for detecting stuck threads, not compensating for daily remark pauses. Pair with processing timeout alerts on business operations instead. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** How do you prove duplicates came from rebalance vs producer retry?
**A:** Compare duplicate `settlement_id` records with same payload but different consumer offset metadata stored in audit columns. Producer retries typically share offset progression anomalies in logs; rebalance duplicates often correlate with `onPartitionsRevoked` without commit. Trace id in headers helps separate client HTTP retries from consumer redelivery. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

---

### S2. Micrometer tag cardinality explosion after tenant-aware metrics

**Situation:** Engineering adds `tenant_id` and `user_id` tags to every HTTP server metric in a multi-tenant SaaS billing API. Within 48 hours Prometheus scrape times out, Grafana dashboards freeze, and the metrics sidecar OOMs — application pods look healthy while observability is blind during month-end billing.

**What they're testing:** Production observability hygiene — knowing metrics are not free logs, cardinality limits, and how Spring Boot Actuator/Micrometer defaults interact with Prometheus remote write.

**How to structure your answer:**
- Identify cardinality source — list top metric series count in Prometheus TSDB stats.
- Immediate mitigation — drop high-cardinality tags via relabel or revert deployment.
- Design low-cardinality alternatives — tenant tier, shard, region, not raw user id.
- Use logs/traces for per-tenant debugging — exemplars and trace sampling.
- Governance — code review checklist, `MeterFilter` max tags, integration test on series count.

**Model answer:** First I would confirm TSDB head series growth correlates with the deploy via `prometheus_tsdb_head_series` and identify the offending meter — likely `http.server.requests` with unbounded `user_id`. Immediate mitigation: roll forward a hotfix removing `user_id` tag or apply Prometheus `metric_relabel_configs` to drop that label until code fixed — observability partial beats total blindness. Educate the team: every unique tag combination creates a new time series; 100k active users means 100k series per metric name per endpoint — multiplied across status codes and URIs it explodes. Correct pattern: tag `tenant_tier` (free/pro/enterprise) or hashed `tenant_shard` (0..31) for sampling debugging, not raw tenant UUID on every timer. For per-tenant SLA disputes, use structured logs with tenant id or tracing with tail sampling — Jaeger/Tempo tolerates higher cardinality than Prometheus. Implement `MeterFilter` denylist in a shared library; ArchUnit test forbids `tag("user_id"` in codebase. Add CI smoke that scrapes actuator `/prometheus` and asserts series count below threshold. Post-incident, run office hours on RED metrics vs debugging dimensions. Document allowed tag keys in platform standards — violations fail PR check.

**Common weak answers:** Increasing Prometheus memory indefinitely, deleting all metrics, or saying 'Grafana problem not Java' without addressing tag design in Micrometer registration code.

**Follow-up probes (with answers):**

**Q:** How would you debug a single tenant's latency without user_id on metrics?
**A:** Enable trace sampling boosted for that tenant via baggage or `tenant_id` in OpenTelemetry span attributes — tracing backends handle higher cardinality better. Alternatively structured JSON logs filtered in Loki/Datadog. For repeatable tests, synthetic canary tenant with dedicated low-cardinality metric `canary.request.duration`. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Can MeterFilter fix this in platform code?
**A:** Yes — a shared auto-configuration can strip denylisted tags or cap URI cardinality by templating `/api/orders/{id}`. Spring 6+ path patterns help. Platform team ships library; services must not register custom tags without approval. Filters run at registry level — catches third-party libs too if configured globally. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

---

### S3. Outbox relay double-publishes after database failover

**Situation:** An order service uses transactional outbox: insert order and outbox row in one DB transaction; a relay process polls outbox and publishes to Kafka. After Aurora failover, customers receive duplicate `OrderCreated` events — downstream inventory reserves stock twice until warehouse alerts fire.

**What they're testing:** Distributed consistency patterns — outbox correctness, relay idempotency, failover behavior, and consumer-side dedup — beyond textbook 'use Kafka exactly once.'

**How to structure your answer:**
- Confirm duplicate event metadata — same `outbox_id`, different publish attempt timestamps.
- Classify relay behavior — at-least-once publish is expected; downstream must dedup.
- Fix relay — mark published with unique constraint, use `FOR UPDATE SKIP LOCKED` polling.
- Fix consumers — idempotent handlers keyed by `order_id` or event id.
- Failover runbook — pause relay during DB role confusion if needed.

**Model answer:** Transactional outbox guarantees the event row exists iff order commits — it does not guarantee exactly-once delivery to Kafka. After Aurora failover, the relay may re-read unpublished rows or crash after publish but before DELETE/mark published, causing duplicate emits — this is normal at-least-once semantics. I would verify outbox schema has `published_at` and `publish_attempt` with unique Kafka message key stored. Relay should UPDATE row to PUBLISHED in same transaction as ack or use de-dupe producer idempotence only as partial help — consumers still need business idempotency. Inventory service should `INSERT reservation (order_id)` with unique constraint and treat duplicate key as success. Add metric `outbox.republish.count` when relay re-sends same id. During failover, enable relay circuit breaker if DB DNS flaps — better delayed orders than duplicate shipments. Long-term, consider CDC (Debezium) from outbox table for log-based emit — still at-least-once but clearer offset semantics. Post-incident review: was mark-published in same DB as outbox? Was relay using auto-commit JDBC? Document that EOS Kafka transactions do not span JDBC commit without complex coupling — outbox plus idempotent consumer is industry default. Finance sign-off on duplicate detection SLA.

**Common weak answers:** Blaming Aurora, enabling Kafka exactly-once without JDBC alignment, or deleting outbox rows before confirming broker ack — loses events instead of fixing dedup.

**Follow-up probes (with answers):**

**Q:** Would Debezium eliminate duplicates?
**A:** No — CDC is at-least-once too; failover can replay binlog segments. It reduces polling relay races but consumers still need idempotency. Debezium simplifies ordering per table partition key. Choose CDC for scale; keep idempotent consumer either way. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Where should dedup state live?
**A:** Downstream service owning side effects — inventory DB unique on `order_id`. Optionally short-TTL dedup cache in Redis for cross-service fanout. Outbox relay dedup alone insufficient if multiple relay instances race — use row-level lock or lease column with expiry. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

---

### S4. Istio sidecar plus Hikari pool mismatch causes connection resets

**Situation:** Microservices on Kubernetes behind Istio mTLS expose REST APIs. After enabling a 15-second idle timeout on the sidecar, intermittent `SQLException: Connection reset` spikes appear in payment-capture service — only on paths calling `risk-scoring`, not on health checks.

**What they're testing:** Network stack plus JDBC interaction — idle connection management, keepalive, pool validation, and debugging layered timeouts in service mesh environments.

**How to structure your answer:**
- Map timeout chain — sidecar, load balancer, DB idle, Hikari maxLifetime.
- Compare failing stack traces — reset on checkout vs mid-query.
- Align Hikari `maxLifetime` and `keepaliveTime` below sidecar idle timeout.
- Validate connections on checkout with `isValid`.
- Document mesh timeout standards per platform team.

**Model answer:** Connection reset on pooled JDBC often means the TCP connection was silently closed by an intermediate layer while Hikari still believed it live. Istio/envoy idle timeout at 15s closes unused outbound connections from payment-capture to risk-scoring if the pool holds connections without traffic — next checkout sends query on dead socket and gets reset. Health checks stay warm; bursty scoring calls see failures. Fix: set Hikari `maxLifetime` and `keepaliveTime` relative to sidecar idle — recycle before intermediary kills. For HTTP clients to risk-scoring, configure OkHttp/Apache pool idle timeout and retry only idempotent calls. Enable JDBC4 `isValid(1)` on checkout. Platform fix: standardize mesh `idle_timeout` above app pool recycle or enable TCP keepalive via DestinationRule. Reproduce in staging with artificial idle sleep between requests. Add metric `hikari.connections.timeout` and log SQLState 08006. Post-incident: diagram all timeouts on one slide per service — mesh, LB, client, server, DB. Senior engineers know JDBC errors often originate in network path, not Oracle misconfiguration.

**Common weak answers:** Only increasing Hikari pool size, disabling Istio, or retrying non-idempotent payment POSTs without understanding idle connection lifecycle.

**Follow-up probes (with answers):**

**Q:** Should maxLifetime be less than DB wait_timeout?
**A:** Yes — Hikari docs recommend maxLifetime several seconds below DB/network idle kill. Order: sidecar idle < LB idle < Hikari maxLifetime < DB wait_timeout — all documented with actual values per environment. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** How to test without production traffic?
**A:** Integration test: borrow connection, sleep past sidecar idle, run simple query — expect failure before fix, pass after keepalive/maxLifetime tuning. Chaos mesh fault injection on idle connections. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

---

### S5. Liquibase migration locks checkout table through peak hour

**Situation:** A deploy runs Liquibase `addColumn` with default on `orders` (80M rows) during business hours on PostgreSQL. Within minutes checkout error rate hits 100% — threads BLOCKED in Hikari waiting for connections; DB shows `ACCESS EXCLUSIVE` lock on `orders` from migration session.

**What they're testing:** Schema migration operational safety — online DDL strategies, lock modes, blue/green deploy discipline, and JDBC transaction impact — not just 'Liquibase is declarative.'

**How to structure your answer:**
- Stop deploy pipeline — cancel migration if possible (`pg_cancel_backend`).
- Assess lock queue — long transactions block DDL and vice versa.
- Choose online strategy — add nullable column, backfill async, add default in app.
- Run heavy DDL in maintenance window or use pg-osc patterns.
- Add CI lint blocking dangerous Liquibase changesets on large tables.

**Model answer:** PostgreSQL `ADD COLUMN ... DEFAULT` on huge tables can hold ACCESS EXCLUSIVE lock blocking all reads/writes — checkout dies. Immediate action: identify migration PID, cancel if safe, verify lock released, scale connections down to reduce pile-up, communicate ETA. Correct approach for zero-downtime: add nullable column without default in fast metadata-only operation (PG 11+ optimized for constant default but still plan carefully), deploy app writing new field, backfill in batches with `WHERE new_col IS NULL LIMIT n`, then add constraint/default if needed. Never run unreviewed Liquibase on hot tables in auto-deploy — require DBA review tag `risk:high`. Use expand-contract pattern across releases. Application threads blocked in pool are symptom — root cause is DDL lock duration. Post-incident: pipeline gate requiring `lock_timeout` session variable in migration connection so migration fails fast instead of holding hours. Train teams on difference between H2 tests and PG prod.

**Common weak answers:** Scaling pods to 'handle errors,' killing app servers without killing migration, or adding index without `CONCURRENTLY` on production PostgreSQL.

**Follow-up probes (with answers):**

**Q:** Does PostgreSQL 11+ make DEFAULT instant?
**A:** Constant defaults can be metadata-only in many cases — but validation and NOT NULL still risk locks. Always test on production-sized clone. `VALIDATE CONSTRAINT` later splits work. Never assume H2 integration test timing applies. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** How prevent recurrence in CI?
**A:** Liquibase custom rule flagging `addColumn` with `defaultValue` on tables above row threshold without batch backfill plan. Mandatory DBA approval label on migration PRs touching core tables. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

---

### S6. Caffeine cache stampede after hot-key TTL expiry

**Situation:** Product catalog service caches SKU prices in Caffeine with 60s TTL. A flash sale SKU becomes a hot key; when TTL expires, 500 virtual threads simultaneously miss cache and hammer pricing Oracle — DB CPU pegs, catalog API returns 503, and cart abandonment spikes.

**What they're testing:** Cache design under load — stampede/thundering herd, single-flight loading, TTL jitter, and separating hot path read from authoritative write.

**How to structure your answer:**
- Confirm stampede pattern — miss spike aligned to TTL boundary in metrics.
- Immediate — extend TTL for hot keys or serve stale-while-revalidate.
- Implement `LoadingCache` with automatic single-flight per key.
- Add jitter to TTL, randomize refresh, consider pre-warm job.
- Rate limit origin requests per key at DB layer.

**Model answer:** Classic cache stampede: many threads see expired entry simultaneously and all query DB. Caffeine `LoadingCache.get(key)` coalesces loads per key — only one loader runs, others wait — fix if currently using manual `getIfPresent` then load pattern. Enable `refreshAfterWrite` with async reload so most threads see stale value while one refreshes — stale-while-revalidate. Add TTL jitter (`60s + random(0,10)`) to prevent synchronized expiry across pods — each JVM still needs single-flight locally; for cross-pod coalescing use brief Redis lock or request coalescing proxy. Immediate incident: bump TTL on known sale SKUs via feature flag config, enable read replica routing for pricing queries, shed load with 429 on non-critical endpoints. Long-term: push price updates via Kafka to invalidate specific keys instead of short TTL polling DB. Monitor `cache.load.duration` p99 and miss rate per key tag (bounded — hash sku to bucket). Load test must include TTL expiry boundary, not just steady hit ratio. Senior point: virtual threads increase concurrent stampede magnitude — cache correctness is concurrency control.

**Common weak answers:** Disabling cache entirely, infinite TTL without invalidation strategy, or synchronizing entire service method creating global bottleneck.

**Follow-up probes (with answers):**

**Q:** Redis vs local Caffeine for this case?
**A:** Local Caffeine with single-flight handles per-JVM stampede; Redis adds network but enables shared invalidation on price change events. Hybrid: Caffeine L1 plus Redis L2 for hot catalog with event-driven eviction. Choose based on consistency SLA — flash sale may tolerate 1s stale with refreshAfterWrite. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** How to load test stampede?
**A:** Chaos test: force `invalidateAll` under 500 concurrent virtual threads in Gatling, measure DB connection count and p99. Assert single query per key per pod via DB audit or query log sampling. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

---

### S7. Kubernetes liveness probe kills pods during long G1 remark

**Situation:** Order API on JDK 17 G1 with 6 GB heap runs in Kubernetes. During daily traffic ramp, pods restart in a loop — liveness probe `/actuator/health/liveness` times out at 1s while JVM logs show remark pauses up to 3s. Readiness stays UP briefly then liveness kills the pod mid-GC.

**What they're testing:** K8s probe semantics vs JVM pause behavior — difference between liveness and readiness, when to tune GC vs probe thresholds, and avoiding death spirals during partial outages.

**How to structure your answer:**
- Verify restart reason `Liveness probe failed` in pod events.
- Correlate pause times from GC log with probe failure timestamps.
- Adjust probe: separate liveness simplicity, increase timeout cautiously.
- Tune G1 `MaxGCPauseMillis` and heap or switch collector if SLO demands.
- Ensure DB checks not on liveness group.

**Model answer:** Liveness should mean 'process deadlocked beyond recovery' — not 'GC paused for 2 seconds.' If `/actuator/health/liveness` hits the JVM during STW remark, Tomcat threads cannot respond — kubelet kills pod, amplifying load on survivors, causing more GC — death spiral. Fix split: liveness endpoint ultra-light (ping) or use `startupProbe` for slow start only; readiness removes pod from Service endpoints when dependencies unhealthy — not for GC pauses usually. Increase `timeoutSeconds` and `failureThreshold` on liveness only after proving not masking real deadlocks — e.g., 5s timeout, 3 failures. Primary fix: reduce pause via heap right-sizing, IHOP tuning, eliminate allocation spikes, or ZGC if p99 pause SLO strict. Enable JFR `jdk.GCPhasePause` in staging. Do not disable liveness entirely — instead use custom indicator that avoids heavy health checks. Actuator 3 separates liveness/readiness — ensure DB check not on liveness group. Document that K8s restarts are expensive — rolling restart during GC incident worsens customer impact. Post-fix dashboard: GC pause p99 overlay pod restart count.

**Common weak answers:** Disabling liveness permanently, only increasing heap without GC log analysis, or putting full dependency check on liveness including Kafka and Oracle.

**Follow-up probes (with answers):**

**Q:** Should readiness fail on GC pause?
**A:** Usually no — transient pause should not drain all pods from load balancer simultaneously. Readiness fails on sustained inability to serve — dependency down, thread pool exhausted. GC tuning addresses pause; readiness flapping on pause causes uneven load. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** When switch to ZGC?
**A:** When remark/old-gen pauses breach SLO after allocation and heap tuning, and CPU overhead acceptable — validate under production-like load on JDK 21. Not first knob — measure first. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

---

### S8. Spring @Async self-invocation bypasses transaction and audit

**Situation:** Compliance requires audit log insert in same transaction as payment capture. Developer adds `@Async @Transactional` method `saveAudit()` called via `this.saveAudit()` from same service class. Audits missing intermittently; payments commit; examiners find gaps during SOC review.

**What they're testing:** Spring AOP proxy mechanics — self-invocation, async thread transaction propagation, and choosing `@TransactionalEventListener` or explicit bean separation.

**How to structure your answer:**
- Reproduce — audit row absent when async expected present.
- Explain proxy bypass — `this.` calls skip Spring enhancement.
- Fix architecture — separate `AuditService` bean, or event listener AFTER_COMMIT.
- Verify transaction manager on async executor thread if truly needed.
- Add integration test asserting audit count matches payment count.

**Model answer:** Spring `@Async` and `@Transactional` apply via JDK/CGLIB proxies around injected beans. Internal `this.saveAudit()` is a direct call on raw object — no async, no transaction boundary you think you configured. Sometimes audit runs in caller thread without proper txn sync; sometimes never runs if exception swallowed. Correct patterns: inject `AuditService` self or separate component and call through proxy; use `@TransactionalEventListener(phase = AFTER_COMMIT)` on domain event so audit only after payment commits; or synchronous audit in same transaction if latency acceptable. If async required, configure `DelegatingSecurityContextAsyncTaskExecutor` carefully — async txn rarely same as caller unless `REQUIRES_NEW` on dedicated executor. Compliance fix: integration test with Testcontainers asserting row count; enable spring transaction debug logging in staging. Document in team wiki with diagram of proxy call vs self call. SOC remediation: backfill missing audits from Kafka `payment-captured` topic if retained. Senior lesson: magic annotations fail silently — arch tests enforcing no `@Async` on same class caller.

**Common weak answers:** Adding `@EnableAsync` again, making method public without proxy call, or disabling compliance checks 'temporarily' without backfill plan.

**Follow-up probes (with answers):**

**Q:** Does `AopContext.currentProxy()` help?
**A:** It works but couples code to Spring — injecting separate bean is cleaner. `exposeProxy=true` required. Use sparingly; prefer event-driven AFTER_COMMIT for audit side effects. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** TransactionalEventListener vs outbox?
**A:** AFTER_COMMIT listener runs in same JVM after commit — can still lose message if process crashes before audit insert completes. For guaranteed audit, outbox in same transaction as payment then relay — stronger compliance posture. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

---

### S9. Feign client retry storm amplifies payment gateway outage

**Situation:** Checkout calls `payment-gateway` via OpenFeign with default retry on 503 and 3s read timeout. Gateway degrades under card network blip; Feign retries 3× per request across 200 pods — effective traffic multiplies 600×, gateway never recovers, circuit breaker absent, Hikari pools exhaust.

**What they're testing:** Resilience patterns — retry safety, idempotency keys, circuit breakers, bulkhead isolation, and understanding retry is load multiplication during incidents.

**How to structure your answer:**
- Stop retries first — feature flag or deploy retry disable.
- Assess idempotency — POST payment without key is dangerous to retry.
- Add Resilience4j circuit breaker plus time limiter plus bulkhead.
- Retry only idempotent GET/status with exponential backoff jitter.
- Load shed at gateway edge; queue async capture if business allows.

**Model answer:** Retries during outage are positive feedback loops — each failing checkout generates N attempts increasing load on already failing dependency. Immediate: disable Feign retry via config `spring.cloud.openfeign.client.config.default.retryer: never` or Resilience4j disable — gateway gets breathing room. Permanent: retry only when idempotency-Key header on payment authorize makes duplicate safe; use GET for status polling with capped backoff jitter. Wrap Feign with circuit breaker — open after error rate threshold, fail fast to user-friendly 'payments temporarily unavailable' instead of hanging threads. Bulkhead limits concurrent calls to gateway per service — protects Hikari from thread starvation. Separate connection pools for gateway HTTP vs DB. Monitor `resilience4j.circuitbreaker.state` and `feign.Client` timings. Chaos test: inject 503, verify no retry storm. Business alignment: async payment capture with webhook completion may tolerate brief gateway outage better than synchronous retry spam. Post-incident KPI: peak RPS to gateway during incident vs normal. Senior engineers quantify amplification factor before enabling retries anywhere.

**Common weak answers:** Increasing retry count 'to improve success,' scaling gateway without stopping retries, or retrying POST without idempotency key.

**Follow-up probes (with answers):**

**Q:** Is gRPC retry safer?
**A:** Only with idempotency tokens and transparent retry policies knowing which RPCs are safe. Same amplification physics — defaults dangerous. Prefer deadline propagation and breaker. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** How communicate degraded mode to users?
**A:** Queue order with `PAYMENT_PENDING` state, show honest UI message, complete via webhook — better than 30s spinner holding servlet threads. Product must accept async completion SLA. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

---

### S10. Classloader leak on Tomcat hot-deploy staging mirrors production

**Situation:** An insurance claims app on Tomcat 9 allows hot redeploy in staging without restart. After 30 deploys, Metaspace OOM kills the JVM; heap dump shows thousands of duplicate `com.claims.AppConfig` classes and JDBC drivers registered but not deregistered. QA insists hot-deploy matches ops habit before weekly production maintenance windows.

**What they're testing:** Classloader lifecycle — Metaspace leaks from redeploy, JDBC driver registration, ThreadLocal in thread pools, and why containers should immutable-deploy instead of hot-deploy.

**How to structure your answer:**
- Explain old generation class objects retained by thread pools and drivers.
- Capture Metaspace trend vs deploy count — linear growth confirms leak.
- Fix staging to cold restart or use external container orchestration.
- Code hygiene — `ServletContextListener` shutdown hooks, deregister drivers, stop threads.
- Align prod/staging deploy model — immutable image replace, not WAR redeploy.

**Model answer:** Each Tomcat hot redeploy creates new WebappClassLoader while old loader remains reachable if any thread, static field, or JDBC `DriverManager` registration holds reference — classic Metaspace leak. Duplicate `AppConfig` classes prove loaders not collected. JDBC drivers loaded in static init register with `DriverManager` in system classloader — leak across redeploy unless `deregisterDriver` on destroy. Thread pools created in `@WebListener` without `shutdown` keep old classes alive. Fix staging practice: stop hot-deploy; use Kubernetes rolling replace of immutable image — matches production anyway. Short-term: restart Tomcat nightly in staging; add `ServletContextListener` contextDestroyed stopping executors, clearing ThreadLocals, deregistering drivers. Use Spring Boot executable JAR on K8s instead of WAR on shared Tomcat if possible. Analyze with Eclipse MAT 'classloader leak' report and `jcmd VM.classloader_stats`. Educate QA: staging fidelity on deploy mechanism matters more than hot-deploy speed — Metaspace leaks take hours; tests missing if only five deploys per day. Production weekly maintenance restart masked leak — staging amplified it. Document mandatory contextDestroyed checklist for any manual thread or cache.

**Common weak answers:** Only raising `MaxMetaspaceSize`, ignoring driver deregistration, or accepting hot-deploy because 'staging is different' without fixing root references.

**Follow-up probes (with answers):**

**Q:** Why do JDBC drivers leak classloaders?
**A:** `DriverManager` static set holds driver instances referencing webapp classloader. Tomcat `JdbcLeakPrevention` listener helps. Prefer Hikari managing driver in container-managed DS outside WAR. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Boot executable JAR on Tomcat vs embedded?
**A:** Embedded Tomcat in Boot one classloader per process — redeploy equals pod replace, cleaner lifecycle. External Tomcat WAR multi-app sharing requires strict destroy hygiene — legacy pattern fading for cloud-native Java. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

---

## Rapid-fire follow-ups they will add

- Why is `Byte[]` worse than `byte[]`? (Boxing every element; poor cache locality; use primitive arrays.)
- Difference between `Error` and `Exception`? Would you catch `OutOfMemoryError`? (Almost never; log and fail fast so orchestrator restarts the pod.)
- `String` vs `StringBuilder` in a recursive function? (Recursion depth × string immutability = O(n²) copies; use `StringBuilder` passed down.)
- Why `LinkedHashMap` for LRU? What's wrong with it under concurrency? (Access-order + `removeEldestEntry`; not thread-safe — use Caffeine.)
- Can you override a `static` method? (No — static methods hide; binding is compile-time.)
- What does `strictfp` do? (Legacy FP consistency across platforms; rarely relevant today.)
- Explain `PhantomReference` vs `WeakReference` for off-heap. (Weak: object collectable; phantom: enqueued after finalize when memory is reclaimable — used with `Cleaner`.)
- Why is `Stack` a bad class? (Extends legacy `Vector`; synchronized overhead; use `ArrayDeque`.)
- `IdentityHashMap` use case? (Reference equality — object graph traversal, serialization frameworks, cycle detection.)
- When is `TreeMap` better than sorting a list? (Repeated ordered lookups, `subMap`/`headMap` range queries — not a one-time sort.)
