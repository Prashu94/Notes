# Java Multithreading & Concurrency — 62 Senior Interview Questions

**Bar:** You can design concurrency, prove safety (JMM), and debug dumps. "I use synchronized" is junior.

---

### 1. What is a happens-before relationship? Give three edges.

**Short answer:**
If action A happens-before B, thread observing B is guaranteed to see A's writes. Key edges: program order within a thread; unlock on monitor M happens-before subsequent lock on M; volatile write happens-before subsequent volatile read; thread start happens-before run; thread end happens-before join. Happens-before is the JMM partial order that defines visibility — without an HB edge, another thread may see stale or reordered writes.

#### What it is
Happens-before is the Java Memory Model's partial ordering that defines visibility and ordering guarantees between actions in different threads. Happens-before is not wall-clock time — it is a formal guarantee compilers and CPUs must respect for visibility and ordering.

#### How it works (internals)
Without happens-before, compilers and CPUs may reorder memory operations; another thread can see stale or inconsistent state. JUC utilities establish HB through volatile fields, locks, and concurrent collection operations. Without HB, the JVM may reorder stores and another thread may observe a flag before the data it guards.

#### When to use / when NOT to use
Reason about every field published across threads: which HB edge connects writer to reader? If none, you have a data race or need synchronization. For every field published across threads, ask which HB edge connects writer to reader — if none, you have a data race.

#### Production example
A worker sets `volatile boolean done` after writing results to a plain array — readers polling `done` see consistent results because volatile write releases prior writes. Without volatile, readers may see `done=true` but stale data. Worker sets volatile done=true after writing results to a plain array — readers polling done see consistent data because the volatile write releases prior stores.

#### Common mistakes
Assuming 'I sleep 100ms so it must be visible.' Using non-volatile flag for shutdown. Ignoring HB when using thread pools. Assuming Thread.sleep makes writes visible. Using a non-volatile shutdown flag. Ignoring HB when submitting work to thread pools.

#### Interview follow-ups (with model answers)

**Q:** Is happens-before transitive?
**A:** Yes — if A happens-before B and B happens-before C, then A happens-before C. This is how you chain edges: thread start happens-before the first action in the child, actions in the child happen-before thread join in the parent. In production you reason about publication protocols: write payload fields, then volatile publish a ready flag — readers who see ready=true are guaranteed to see the payload writes. Without transitivity you could not compose safe patterns from primitive edges. jcstress and litmus tests exist precisely because developers mis-chain edges and get rare visibility bugs that only appear under ARM or aggressive compiler optimization.

**Q:** Does ConcurrentHashMap establish happens-before?
**A:** Yes for individual operations — a successful put happens-before a subsequent get of the same key by another thread. That does not make compound check-then-act sequences safe: if (!map.containsKey(k)) map.put(k, v) can still race because containsKey and put are separate operations without a single atomic invariant. In cache-loading code use computeIfAbsent, not get-then-put. For iteration, CHM provides weak consistency — iterators reflect state at some point since creation but do not throw CME. Do not assume size() is exact under concurrency.

**Q:** Difference between happens-before and wall-clock before?
**A:** Wall-clock before is physical time — HB is a logical ordering guarantee independent of clocks. Thread A may set a field at T=100ms and Thread B may read at T=50ms on a skewed clock yet still see the write if HB exists. Conversely, A may write at T=10 and B read at T=1000 without HB and still see stale null. This is why 'I added a sleep' never fixes concurrency bugs in code review. Production debugging uses HB reasoning in thread dumps and JMM-aware fixes, not timing heuristics.

#### Scenario probe

A metrics aggregator uses a plain boolean ready flag. Under load, dashboards show ready=true but stale counter values — reproduces only on ARM Graviton, never locally on Intel.

Classic missing HB edge: writer sets counters then ready=true without volatile on ready. Reader sees reordered ready before counter writes. Fix: volatile boolean ready or AtomicReference<Snapshot> publishing immutable snapshot. Add jcstress test for publication pattern. Document the HB chain in code review checklist for any cross-thread flag.

---

### 2. Data race vs race condition.

**Short answer:**
A data race is concurrent access to a non-volatile field with at least one write and no happens-before — undefined behavior in JMM. A race condition is a logic bug where correctness depends on interleaving even when individual operations are atomic. Data race: concurrent access to a non-volatile field with at least one write and no happens-before — JMM undefined behavior. Race condition: logic bug where correctness depends on interleaving even when individual ops are atomic.

#### What it is
Data races are about memory model violations; race conditions are about application invariants. Data races are memory-model violations; race conditions are application invariant violations.

#### How it works (internals)
You can have race conditions without data races: `if (!map.containsKey(k)) map.put(k, v)` on ConcurrentHashMap is atomic per op but still wrong. Fixing data races with volatile doesn't fix check-then-act logic. Fixing data races with volatile does not fix check-then-act. Use atomic compound ops: putIfAbsent, compute, merge.

#### When to use / when NOT to use
Eliminate data races with synchronization or concurrent types. Fix race conditions with atomic compound ops (`putIfAbsent`, `compute`).

#### Production example
Duplicate webhook processing: two threads both pass `if (!processed)` before either sets flag — business duplicate charge. Fix: DB unique constraint or `computeIfAbsent` with idempotency key. Fix: DB unique constraint or computeIfAbsent with idempotency key.

#### Common mistakes
Calling code thread-safe because it uses ConcurrentHashMap. Confusing no CME with no races.

#### Interview follow-ups (with model answers)

**Q:** Can jcstress detect data races?
**A:** jcstress runs litmus tests across thread interleavings and JVM configurations to observe outcomes forbidden by the JMM. It finds visibility and reordering bugs, not business logic races. Pair jcstress on custom lock-free code with integration tests that hammer check-then-act paths. In CI, run jcstress on release candidates for teams shipping custom queues or off-heap structures. For application services, ArchUnit plus load tests on idempotency keys catch more production races than jcstress alone. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Race condition vs deadlock — how do symptoms differ?
**A:** Race conditions produce wrong data intermittently — duplicate charges, lost updates, inconsistent reads — threads remain RUNNABLE or WAITING normally. Deadlock freezes progress in a circular lock wait — jstack shows BLOCKED cycle. Races need logic fixes and idempotency; deadlocks need lock ordering. Both can coexist: race causes duplicate work, deadlock during cleanup. Thread dumps help deadlock; metrics and audit logs help races. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** How do you fix check-then-act races in production?
**A:** Replace get-then-put with computeIfAbsent or putIfAbsent on CHM. For DB-backed idempotency, use INSERT with unique constraint on idempotency_key and treat DuplicateKeyException as success. For distributed systems, compare-and-set in Redis with WATCH/MULTI or Redisson RMap with atomic compute. Never rely on synchronized block around only the check if the act spans I/O outside the lock. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Payment webhook handler uses ConcurrentHashMap to dedupe by eventId. Finance still sees duplicate captures at 0.01% rate under peak.

containsKey then put is not atomic — both threads pass the check. Fix: processed.computeIfAbsent(eventId, k -> { charge(); return true; }) or DB unique on event_id with ON CONFLICT DO NOTHING. Add integration test firing 100 parallel webhooks for same id. Alert on duplicate key rate, not just error rate.

---

### 3. Thread lifecycle and why `stop()`/`suspend()` died.

**Short answer:**
Threads progress NEW → RUNNABLE → BLOCKED/WAITING/TIMED_WAITING → TERMINATED. `stop()` and `suspend()` were deprecated because they leave monitors and objects inconsistent. Interrupt is cooperative: set flag, `InterruptedException` on blocking calls, restore interrupt if catching without rethrow. Thread lifecycle: NEW → RUNNABLE → BLOCKED/WAITING/TIMED_WAITING → TERMINATED.

#### What it is
Thread lifecycle APIs reflect safe cooperation vs forced termination.

#### How it works (internals)
`Thread.stop()` could kill a thread holding a lock mid-critical-section. `suspend()` without matching `resume` deadlocks. `interrupt()` sets a status bit; blocking methods check it and throw IE. NIO and `Lock.lockInterruptibly` participate.

#### When to use / when NOT to use
Never call stop/suspend. Use interrupt + shutdown flags + `ExecutorService.shutdownNow` with timeout drain. Use interrupt plus shutdown flags plus ExecutorService.shutdownNow with timeout drain.

#### Production example
Batch worker checks `Thread.interrupted()` in loop; on shutdown, pool calls `shutdownNow()` — worker saves checkpoint and exits cleanly. Batch worker checks Thread.interrupted() in loop; on shutdown pool calls shutdownNow() — worker saves checkpoint and exits cleanly.

#### Common mistakes
Swallowing InterruptedException without restoring interrupt. Expecting interrupt to kill CPU spin loop without checking flag. Using Thread.stop in tests.

#### Interview follow-ups (with model answers)

**Q:** Difference between interrupt and a volatile shutdown flag?
**A:** Interrupt is standard for blocking APIs — sleep, wait, BlockingQueue.take, lockInterruptibly throw IE or return early. Volatile shutdown flag works for cooperative loops that poll state. Best practice: combine both — volatile flag for application semantics, interrupt to unblock parked threads during shutdownNow. Virtual threads respond to interrupt when parked on j.u.c; pinning on synchronized JDBC may delay response. Document which mechanism each long-running task respects. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** How do virtual threads handle interrupt?
**A:** Virtual threads check interrupt when parking/unmounting. Blocking on java.util.concurrent usually unmounts the carrier. Pinning occurs with synchronized blocks around native JDBC or some legacy libraries — carrier stays busy and interrupt may not promptly stop work. Monitor JFR VirtualThreadPinned events. Prefer ReentrantLock over synchronized in virtual-thread code paths that block. Spring Boot 3.2+ virtual thread mode needs pin-rate dashboards. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** park/unpark vs wait/notify?
**A:** LockSupport.park/unpark are the low-level primitives behind j.u.c locks — no monitor required, unpark is not lost if issued before park (permit model). wait/notify require holding the intrinsic monitor and are bound to condition queues. j.u.c Condition.await/signal mirror wait/notify with ReentrantLock. In thread dumps, park appears in LockSupport.park — normal for pool idle workers. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Deploy hangs for 10 minutes — Kubernetes liveness fails. Thread dump shows batch workers WAITING on queue.take() despite shutdown hook running.

shutdown() was called but not shutdownNow — workers blocked on take never see interrupt. Fix: shutdownNow, interrupt workers, awaitTermination with timeout, then force exit. Long-term: use poll(timeout) in loop checking shutdown flag. Add metric for graceful shutdown duration and alert when awaitTermination exceeds SLO.

---

### 4. How does `synchronized` work in HotSpot?

**Short answer:**
HotSpot stores lock state in the object mark word: lightweight CAS lock, inflation to OS monitor (fat lock) on contention. `synchronized` is reentrant. Prefer it for simple mutual exclusion; use `ReentrantLock` for tryLock, fairness, and multiple conditions.

#### What it is
Intrinsic locks map to object headers and optional OS mutexes under contention.

#### How it works (internals)
Biased locking (reduced/removed in recent JDKs) optimized uncontended locks. Thin lock uses CAS on mark word. Contention inflates to monitor with wait set. JVM can perform lock coarsening and escape-analysis elision.

#### When to use / when NOT to use
Use synchronized for short critical sections. ReentrantLock when you need timed or interruptible lock acquisition.

#### Production example
High contention on synchronized cache refresh — thread dump shows BLOCKED on same monitor. Narrow critical section or switch to per-key locks.

#### Common mistakes
synchronized on public methods exposing `this` as lock. Long I/O inside synchronized block. Assuming synchronized fixes visibility without holding lock for reads.

#### Interview follow-ups (with model answers)

**Q:** What is lock inflation cost?
**A:** Uncontended synchronized is cheap — biased/thin lock via CAS on mark word. Under contention, JVM inflates to a heavyweight monitor backed by OS mutex — context switches and kernel scheduling. Inflation is one-way for that object until lock is released and deflation may occur later. High BLOCKED counts in dumps on one monitor signal inflation hotspot. Fix: shrink critical section, strip lock from read path with immutable snapshot, or shard locks by key. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** What is biased locking status in JDK 21?
**A:** Biased locking was disabled by default in JDK 15 and removed in JDK 21 — do not cite biased locking as a modern optimization. Current HotSpot uses lightweight locking with stack-based lock records where possible. Interview answer should reflect post-21 reality: thin locks, inflation, lock coarsening, escape analysis elision. Check JFR LockClass events for contention hotspots. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Monitor vs ReentrantLock in JFR?
**A:** JFR jdk.JavaMonitorEnter and JavaMonitorWait show intrinsic lock contention. ReentrantLock appears as java.util.concurrent locks in thread dumps with lock hex address. Both show BLOCKED threads. ReentrantLock adds tryLock timeout metrics you implement yourself. For production triage, correlate monitor name in stack with class — synchronized methods on popular singletons are frequent culprits. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Catalog service p99 spikes at peak. jstack shows 80 threads BLOCKED waiting for monitor on CacheManager.class.

Static synchronized refresh holds class lock while reloading 50MB config from S3 — all readers block. Fix: AtomicReference<ImmutableConfig> swap after load completes off-lock; readers never take mutex. Or StampedLock for read-heavy path. JFR LockClass on CacheManager confirms contention.

---

### 5. `ReentrantLock` vs `synchronized` vs `StampedLock`.

**Short answer:**
ReentrantLock offers the same exclusion as synchronized with tryLock, fairness, interruptible lock, and multiple Conditions. StampedLock adds optimistic reads for read-heavy workloads but is not reentrant and is easy to misuse. ReentrantLock offers tryLock, fairness, interruptible lock, and multiple Conditions versus synchronized.

#### What it is
Three locking APIs with different ergonomics and performance profiles.

#### How it works (internals)
Fair ReentrantLock queues waiters — less starvation, lower throughput. StampedLock: `tryOptimisticRead` then validate stamp; downgrade/upgrade paths are tricky. Never block between optimistic read and validate.

#### When to use / when NOT to use
Default to synchronized or unfair ReentrantLock. StampedLock only after profiling read-heavy critical sections.

#### Production example
Config service read 1000:1 vs write — StampedLock optimistic reads cut lock time 60%. Write path still uses write lock.

#### Common mistakes
StampedLock mixed with synchronized on same data. Fair lock enabled globally 'for justice.' Forgetting unlock in finally with ReentrantLock. Fair lock enabled globally.

#### Interview follow-ups (with model answers)

**Q:** When is ReadWriteLock better than StampedLock?
**A:** ReentrantReadWriteLock is reentrant and familiar — good when reads dominate and critical sections are long enough to amortize lock overhead. StampedLock optimistic reads win on microsecond-scale read paths with rare writes. ReadWriteLock upgrade from read to write is tricky and can deadlock. Often immutable snapshot or AtomicReference beats both for config. Measure with JMH before adopting either. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** What happens when StampedLock validate fails?
**A:** Optimistic read returns a stamp; validate checks no write occurred. On failure, upgrade to readLock or retry optimistic read. If you block or perform I/O between optimistic read and validate, writers can slip in and you read inconsistent state. Pattern: read fields into locals under optimistic stamp, validate, use locals — on failure retry. Never hold optimistic stamp across alien method calls. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Lock vs synchronized JVM support?
**A:** synchronized is JVM intrinsic — optimizer understands monitor boundaries for coarsening and elision. ReentrantLock is library code atop AQS — more flexible, slightly more overhead uncontended. Both inflate under contention. synchronized cannot do tryLock timeout — use ReentrantLock for bounded waits on admin paths. Always unlock in finally with ReentrantLock. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Team adds fair ReentrantLock(true) to pricing engine 'for fairness'. Throughput drops 25% at same CPU.

Fair lock enforces strict queueing — barging prevented, latency for all readers rises. Fix: revert to unfair lock; use AtomicReference<PriceTable> immutable snapshot for reads. Fair lock only if profiling shows measurable starvation on specific low-priority thread — never global default.

---

### 6. Explain `volatile` with a shutdown flag and why `i++` is still wrong.

**Short answer:**
`volatile boolean shutdown` lets readers see the writer's update without locking. `volatile int c; c++` remains wrong — read-modify-write is not atomic. Use `AtomicInteger` or `LongAdder` for counters. volatile boolean shutdown lets readers see writer update without locking. volatile boolean shutdown lets readers see writer update without locking. volatile boolean shutdown lets readers see writer update without locking. volatile boolean shutdown lets readers see writer update without locking. volatile boolean shutdown lets readers see writer update without locking.

#### What it is
Volatile provides visibility and ordering for a single variable, not atomicity of compound operations.

#### How it works (internals)
Volatile write is a release; volatile read is acquire — prior writes in writer thread can't be reordered after the volatile write. Readers see flag and piggybacked data if writer protocol is correct. i++ is three operations — lost updates under contention. Volatile write is release; volatile read is acquire — prior writes in writer thread cannot reorder after volatile write.

#### When to use / when NOT to use
Volatile for status flags and one-shot publication patterns. Atomics for counters. Locks for multi-field invariants.

#### Production example
Graceful shutdown: main sets `volatile shutdown=true`; workers observe and exit loops. Request counter uses `LongAdder`, not volatile int. Graceful shutdown: main sets volatile shutdown=true; workers observe and exit loops. Request counter uses LongAdder, not volatile int.

#### Common mistakes
volatile fixes all concurrency. volatile long/double without understanding 32-bit JVM history (less issue on modern). Using volatile on compound object graph. volatile fixes all concurrency. Using volatile on compound object graphs without safe publication protocol.

#### Interview follow-ups (with model answers)

**Q:** Explain the piggyback publication pattern.
**A:** Writer fills plain fields, then volatile-writes a ready flag. Reader reads ready; if true, reads plain fields — HB from volatile write ensures reader sees writer's prior stores. Requires reader never to use data when ready is false. Alternative: publish immutable record via AtomicReference swap — cleaner for services. Piggyback is common in hand-rolled ring buffers; prefer j.u.c abstractions in application code. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** volatile vs AtomicBoolean for shutdown flag?
**A:** Both provide visibility for single-bit semantics. AtomicBoolean adds CAS for compare-and-set transitions — useful for one-shot init or flip-if-not-set. Plain volatile boolean suffices for shutdown=true idempotent write. AtomicBoolean shines when multiple threads race to set first-responder flag. Do not use AtomicBoolean thinking it fixes compound state — only the reference itself is atomic. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** False sharing with volatile fields?
**A:** Two volatile counters on adjacent fields may share a cache line — cores invalidate each other on unrelated updates. LongAdder stripes internally to reduce false sharing. @Contended pads fields in expert scenarios. If hot counters plateau below core count, check layout with JMH and perf counters before blaming lock contention. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Global volatile int requestCount undercounts by 15% at 10k RPS — dashboards disagree with access logs.

c++ is three ops — lost updates under contention. Fix: LongAdder per endpoint or Micrometer Counter. volatile does not make RMW atomic. Load test after fix; add unit test with 32 threads incrementing 100k each asserting exact sum.

---

### 7. CAS, ABA, and `AtomicStampedReference`.

**Short answer:**
Compare-and-swap atomically updates if current value matches expected. ABA problem: value goes A→B→A, CAS succeeds but structure changed (e.g., reused nodes). `AtomicStampedReference` tags versions to detect ABA. CAS atomically updates if current value matches expected — foundation of lock-free algorithms and atomics.

#### What it is
CAS is the foundation of lock-free algorithms and java.util.concurrent atomics. CAS is the hardware primitive behind java.util.concurrent atomics.

#### How it works (internals)
Failed CAS loops retry — can cause livelock under extreme contention (LongAdder stripes). ABA matters in lock-free stacks/queues with node reuse. For simple counters, AtomicInteger suffices.

#### When to use / when NOT to use
Use atomics for counters and references. Reach for stamped references only in lock-free structures you own. Atomics for counters and references. Stamped references only in lock-free structures you own and test with jcstress.

#### Production example
Lock-free stack in academic exercise hits ABA — stamped reference fixes. Production metrics use LongAdder, not lock-free list. Lock-free stack exercise hits ABA with node pool reuse — AtomicStampedReference fixes. Production metrics use LongAdder, not hand-rolled lock-free lists.

#### Common mistakes
Spinning forever on CAS without backoff. Assuming AtomicReference prevents all races on object fields inside referent. Assuming AtomicReference prevents races on fields inside the referent.

#### Interview follow-ups (with model answers)

**Q:** compareAndSet vs getAndAdd?
**A:** compareAndSet sets if current equals expected — boolean success. getAndAdd atomically adds and returns previous value — no retry loop needed for increment. Use getAndAdd for counters. compareAndSet for state machines and lock-free transitions. getAndUpdate and accumulate on AtomicInteger compose RMW in one JVM op. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** When to choose LongAdder over AtomicInteger?
**A:** High write contention on single counter — LongAdder stripes across cells, sums on longValue() for read. AtomicInteger better for low contention or when you need exact immediate read every time. Micrometer counters use LongAdder internally. At millions of increments per second across cores, LongAdder scales; AtomicInteger plateaus. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Hazard pointers overview?
**A:** Memory reclamation technique in native lock-free code — defer freeing nodes until no thread can still reference them. Java uses GC so hazard pointers rarely appear in app code. ABA in Java more relevant with object pools reusing node wrappers. Prefer j.u.c queues over hand-rolled Michael-Scott unless you are building infrastructure. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Custom lock-free job queue reuses Node objects from a pool. Rare duplicate job execution after GC pressure — cannot reproduce in dev.

Classic ABA on lock-free stack with pooled nodes. CAS sees same reference twice while list structure changed. Fix: AtomicStampedReference with version, or stop pooling nodes, or use LinkedBlockingQueue. Add jcstress test. Production lesson: do not hand-roll lock-free without formal testing.

---

### 8. `synchronized` reentrancy and deadlock.

**Short answer:**
The same thread can re-acquire a lock it already holds. Deadlock is circular wait: T1 holds A waits B, T2 holds B waits A. Avoid via lock ordering, tryLock with timeout, smaller critical sections, and never calling alien code while holding locks. Reentrancy: same thread re-acquires lock it already holds — enables recursive synchronized methods.

#### What it is
Reentrancy enables recursive synchronized methods; deadlock is a design and discipline failure. Reentrancy is a feature; deadlock is a design failure.

#### How it works (internals)
JVM tracks lock count for reentrant acquisition. Deadlock detection in thread dumps lists cycle. Lock ordering graph must be acyclic. 'Open calls' while holding locks invite callbacks that re-enter.

#### When to use / when NOT to use
Document global lock order for multi-lock protocols. Use `tryLock( timeout )` for optional recovery.

#### Production example
Service holds DB connection lock then calls user callback that re-enters service — deadlock. Fix: release lock before callback or copy data needed.

#### Common mistakes
Locking on `this` publicly. Different lock order in two code paths. Ignoring tryLock timeout handling.

#### Interview follow-ups (with model answers)

**Q:** Deadlock vs livelock?
**A:** Deadlock: threads BLOCKED in cycle — no CPU progress. Livelock: threads RUNNABLE responding to each other — high CPU, no business progress — polite retry loops yielding immediately. Fix livelock with randomized exponential backoff. Deadlock fix is lock ordering or breaking the cycle. Thread dumps distinguish them — all BLOCKED vs all RUNNABLE in retry. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Database deadlock vs JVM deadlock?
**A:** JVM deadlock is monitor cycle visible in jstack. DB deadlock is row/page lock cycle — Oracle v$session, Postgres pg_locks. App can hold JVM lock while waiting on DB and vice versa — need both dumps. Fix DB with consistent index access order; fix JVM with lock hierarchy. XA transactions compound both layers. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Lock dependency visualizer tools?
**A:** jstack and jcmd print Java deadlocks. IDE plugins and FindBugs detect lock-order inversions statically. ArchUnit custom rules enforce lock hierarchy in CI. For runtime, JFR LockClass events show hot monitors. Document ordered lock IDs in ARCHITECTURE.md for multi-lock protocols. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

OrderService and PaymentClient deadlock after new callback feature. jstack shows cycle on orderLock and paymentLock.

Callback path acquires paymentLock then calls OrderService which takes orderLock while main path holds orderLock then payment. Fix: global order — always acquire orderLock before paymentLock. Extract callback to async queue processed without holding orderLock. Add stress test with CyclicBarrier reproducing opposite order 500 times.

---

### 9. Livelock vs deadlock vs starvation.

**Short answer:**
Deadlock: threads blocked forever in circular wait. Livelock: threads actively respond to each other but make no progress (polite stepping aside). Starvation: thread never acquires resource due to unfair scheduling or priority.

#### What it is
Three failure modes of concurrent progress with different symptoms and fixes. Three failure modes with different symptoms, dumps, and fixes.

#### How it works (internals)
Deadlock needs lock cycle break. Livelock needs randomized backoff or state machine progress. Starvation needs fair locks or separate pools — fair locks hurt throughput.

#### When to use / when NOT to use
Diagnose from thread dumps: deadlock section vs all RUNNABLE retrying vs one thread never running. Diagnose from dumps: deadlock section vs all RUNNABLE retrying vs one thread never running.

#### Production example
Two retry loops both yield immediately — livelock at 100% CPU. Adding exponential backoff fixes. Low-priority housekeeping thread starved by unfair lock — switch pool or fair lock for that path only.

#### Common mistakes
Confusing high CPU livelock with deadlock. Enabling fair locks everywhere. Ignoring thread priority in legacy code.

#### Interview follow-ups (with model answers)

**Q:** Resource starvation in thread pool?
**A:** Queue grows while core threads busy — tasks at tail starve if unbounded queue hides problem. Fixed pool with bounded queue and CallerRunsPolicy surfaces backpressure. Separate bulkhead pools so report jobs cannot starve payment tasks. Monitor queue depth and oldest task age — not just active count. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** What is lock barging?
**A:** Unfair lock allows incoming thread to acquire before queued waiters — higher throughput, possible starvation. Fair lock prevents barging. synchronized is unfair. Do not enable fair unless profiling proves starvation — most 'starvation' is pool misconfiguration. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Priority inversion in Java?
**A:** Java thread priorities are hints — JVM and OS may ignore. Priority inversion classic in RTOS less common in Java servers. Similar effect: low-priority task holds lock high-priority task needs. Fix: shorten critical sections, avoid priority APIs, use dedicated executors for latency-sensitive work. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Two payment retry services at 100% CPU, zero throughput — each backs off 1ms and immediately retries the same contested row.

Livelock not deadlock — threads RUNNABLE in synchronized retry. Fix: randomized exponential backoff with jitter, circuit breaker, or DB SELECT FOR UPDATE SKIP LOCKED. Alert on retry rate without success counter increment.

---

### 10. ThreadLocal: uses and leaks.

**Short answer:**
ThreadLocal maps each thread to a hidden value — MDC logging, security context, legacy per-thread formatters. Thread pools reuse threads; failing to `remove()` leaks values and classloaders. Virtual threads make ThreadLocal costly at massive scale — prefer ScopedValue (Java 21+).

#### What it is
ThreadLocal provides thread confinement without passing context parameters.

#### How it works (internals)
Implementation: each `Thread` has a `ThreadLocalMap`. `get`/`set`/`remove`. Pool thread retains last request's user id without remove — authorization bug. InheritableThreadLocal copies to child threads (dangerous with pools).

#### When to use / when NOT to use
Always `try/finally { threadLocal.remove(); }` in servlet filters and task wrappers. Use `TaskDecorator` for async. Always try/finally threadLocal.remove() in servlet filters and task wrappers. TaskDecorator for async.

#### Production example
After security audit, filter adds `finally { SecurityContextHolder.clearContext(); }` — fixes cross-tenant data leak in pooled threads. Security audit: filter adds finally SecurityContextHolder.clearContext() — fixes cross-tenant data leak in pooled threads.

#### Common mistakes
ThreadLocal for everything global. SimpleDateFormat in ThreadLocal instead of DateTimeFormatter. Millions of virtual threads each with heavy ThreadLocal.

#### Interview follow-ups (with model answers)

**Q:** ScopedValue vs ThreadLocal?
**A:** ScopedValue (Java 21+) binds values to dynamic scope — immutable during scope, cheap with virtual threads, no remove() leak if used with try-with-resources pattern. ThreadLocal persists on pooled thread until remove. For new code on JDK 21+, prefer ScopedValue for request context. ThreadLocal remains for legacy frameworks — Spring Security still uses ThreadLocal with clear in filter. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** What is TransmittableThreadLocal?
**A:** Alibaba TTL propagates ThreadLocal across thread pool boundaries by wrapping Runnable/Callable to copy parent context to worker. Use when executor does not support TaskDecorator and you need MDC across @Async. Micrometer ContextPropagation is the Spring-ecosystem alternative. Test async paths — missing traceId in logs is the symptom. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** ThreadLocal and memory leaks?
**A:** ThreadLocalMap holds entries keyed by weak ThreadLocal ref but values are strong — if thread lives forever (pool) and remove() skipped, value leaks until thread dies. ClassLoader leaks in Tomcat redeploy when ThreadLocal holds app classloader ref. Always remove in finally. heap dump dominator tree on ThreadLocal$Entry finds leaks. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Multi-tenant SaaS shows User A data in User B session intermittently — only on high traffic, never in single-user tests.

Pooled http-nio thread retained TenantContext ThreadLocal from prior request. Fix: servlet filter finally TenantContext.clear(). Add TaskDecorator on all executors. Integration test: 50 parallel tenants assert isolation. Security incident severity — document in SOC2 controls.

#### Code / config (when useful)
```java
try {
    MDC.put("traceId", traceId);
    chain.doFilter(request, response);
} finally {
    MDC.clear();
}
```

---

### 11. ExecutorService taxonomy.

**Short answer:**
`newFixedThreadPool`: bounded threads, unbounded `LinkedBlockingQueue` — queue can OOM. `newCachedThreadPool`: unbounded threads — exhausts native memory. `newSingleThreadExecutor`: ordered single worker. `ForkJoinPool`: work-stealing for CPU tasks. Production needs named threads, bounded queues, rejection policies, and `afterExecute` error handling.

#### What it is
Executor frameworks map tasks to threads with different scaling and queuing semantics.

#### How it works (internals)
Fixed pool blocks at queue capacity with default AbortPolicy. CallerRunsPolicy pushes work back to submitter thread — backpressure. ScheduledThreadPoolExecutor for delayed tasks. Never use unbounded executors in services.

#### When to use / when NOT to use
Configure explicit `ThreadPoolExecutor` with core/max, bounded queue, named factory, metrics. Wrap for MDC propagation. Configure explicit ThreadPoolExecutor with core/max, bounded queue, named factory, metrics.

#### Production example
Custom pool: core 20, max 40, `ArrayBlockingQueue(500)`, `CallerRunsPolicy`, Micrometer binder — rejects surface as 503 when saturated. Custom pool: core 20, max 40, ArrayBlockingQueue(500), CallerRunsPolicy, Micrometer binder — rejects surface as 503 when saturated.

#### Common mistakes
Executors.newFixedThreadPool in production. Ignoring exceptions swallowed in run(). Default thread names in dumps.

#### Interview follow-ups (with model answers)

**Q:** ThreadPoolExecutor parameters explained?
**A:** corePoolSize: threads kept alive. maximumPoolSize: cap under load. keepAliveTime: idle excess thread TTL. workQueue: bounded vs unbounded determines OOM vs reject. Rejection policy: Abort throws, CallerRuns backpressure, Discard silent loss. prestartAllCoreThreads for latency-sensitive. Allow core thread timeout to shrink after burst. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Why not common pool for blocking I/O?
**A:** ForkJoinPool.commonPool() sized for CPU work — blocking JDBC starves parallel streams and CompletableFuture default executor. Dedicated cached or fixed pool for blocking. Virtual threads change platform thread math but not connection limits. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Graceful shutdown sequence?
**A:** shutdown() — no new tasks, finish queued. awaitTermination(timeout). shutdownNow() — interrupt workers, return pending list. Cancel in-flight with cooperation. Spring @PreDestroy should call shutdown and await. Log pending task count on timeout. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Microservice OOM after traffic 3x — heap dump shows millions of Runnable in LinkedBlockingQueue from Executors.newFixedThreadPool.

Factory uses unbounded queue — tasks accumulate faster than processing. Fix: ArrayBlockingQueue with CallerRunsPolicy or bounded queue plus 503. Right-size pool from JDBC and downstream limits. Alert queue depth > 80% capacity.

---

### 12. Design a production thread pool for HTTP + JDBC.

**Short answer:**
Tomcat request threads (or virtual threads) must not assume unlimited DB concurrency. Size platform pools near acceptable DB connections (e.g., Hikari 20). Use bounded queues and 503 on overflow. Timeouts on HTTP and SQL. Separate CPU-bound pools from blocking I/O.

#### What it is
Thread pool design aligns application concurrency with scarce downstream resources.

#### How it works (internals)
Classic formula threads ≈ cores × (1 + wait/compute) is a starting point only. JDBC pool is the real limiter. Virtual threads decouple HTTP concurrency from OS threads but not from connections.

#### When to use / when NOT to use
Measure pool active count, queue depth, connection wait time. Shed load before OOM.

#### Production example
Hikari max 25, Tomcat max 200 platform threads caused 175 threads blocked on `getConnection`. Move to 50 Tomcat threads + queue or virtual threads + semaphore limiting concurrent DB work to 25. Hikari max 25, Tomcat max 200 caused 175 threads blocked on getConnection. Fix: 50 Tomcat threads plus queue or virtual threads plus semaphore limiting DB to 25.

#### Common mistakes
200 threads because 'more is faster.' No connection timeout. Running reports on request thread pool. 200 threads because more is faster. No connection timeout. Running reports on request thread pool.

#### Interview follow-ups (with model answers)

**Q:** Virtual threads plus JDBC — what changes?
**A:** Many virtual threads can block on getConnection without 200 platform threads — but Hikari still caps at 25 connections. Use semaphore or smaller effective concurrency for DB work. Watch VirtualThreadPinned if synchronized JDBC driver pins carriers. Connection wait time metric becomes the alert, not thread count. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Semaphore vs smaller pool for DB limiting?
**A:** Semaphore caps concurrent DB operations across larger HTTP pool — flexible. Smaller Tomcat pool is simpler but caps total request concurrency. Often combine: virtual threads for HTTP, Semaphore(25) around repository layer. Bulkhead pattern isolates DB from CPU work. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Bulkhead pattern in Spring?
**A:** Resilience4j @Bulkhead on repository calls limits concurrent invocations. Separate thread pool per dependency. Prevents one slow Oracle call from consuming all Tomcat threads. Pair with timeout and circuit breaker. Configure from prod metrics — start with connection pool size as bulkhead limit. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Spring Boot app: Tomcat 200 threads, Hikari 20 connections, p99 8s at moderate load — CPU 30%.

180 threads blocked in HikariDataSource.getConnection — thread pool exceeds connection pool. Fix: reduce Tomcat max, enable virtual threads with semaphore(20) on @Transactional service, or increase Hikari only if Oracle supports it. Add connection-timeout and pending-thread metric. 503 when semaphore unavailable.

---

### 13. `Future` vs `CompletableFuture` vs `StructuredTaskScope`.

**Short answer:**
`Future` blocks on `get()`. `CompletableFuture` composes async pipelines but defaults to `ForkJoinPool.commonPool()` — never block there. Always pass a dedicated executor. Java 21 `StructuredTaskScope` ties subtask lifetime to scope with cancellation propagation.

#### What it is
Three APIs for async results with different composition and lifecycle guarantees.

#### How it works (internals)
CF: `thenApply`, `allOf`, `orTimeout`. Common pool starvation affects parallel streams and default CF. Structured concurrency: open scope, fork tasks, join or cancel all on failure/timeout.

#### When to use / when NOT to use
Use CF with custom executor for service calls. StructuredTaskScope for fan-out with deadline. Avoid fire-and-forget CF without exception handler.

#### Production example
Fetch user, orders, prefs in parallel via StructuredTaskScope with 2s deadline — one failure cancels siblings. CF uses `billingExecutor` bean, not commonPool. CF uses billingExecutor bean.

#### Common mistakes
supplyAsync without executor. get() on servlet thread without timeout. Ignoring exceptionally().

#### Interview follow-ups (with model answers)

**Q:** Structured concurrency preview status?
**A:** StructuredTaskScope in JDK 21+ as preview/incubating — check current JDK release notes. Pattern: try (var scope = new StructuredTaskScope.ShutdownOnFailure()) { var f1 = scope.fork(...); scope.join(); } — failure cancels peers. Adopt for fan-out microservice aggregation with deadline. Spring 6 does not replace this — use in service layer for orchestration. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** CompletableFuture vs reactive Mono?
**A:** CF is pull-oriented composition with thread-per-stage if using default executor. Mono is lazy reactive stream with event-loop friendly if no block. Do not block Mono on servlet thread. CF fits imperative Spring services; WebFlux fits reactive stack. Mixing block() in reactive chain is footgun. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** cancel(true) behavior on Future?
**A:** interrupts running thread if task started — cooperative. Does not stop non-interruptible work. CF cancel propagates to dependent stages if configured. shutdownNow on pool interrupts all workers. Document which tasks respond to interrupt. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Checkout aggregates 5 downstream calls via CompletableFuture.supplyAsync() — no executor arg. Nightly batch parallelStream slows checkout at 6pm.

Both starve ForkJoinPool.commonPool(). Fix: dedicated ExecutorService bean per domain — checkoutExecutor with 20 threads, bulkhead batch job on batchExecutor. Pass executor to every supplyAsync. Monitor common pool queue depth — should be idle in prod.

---

### 14. Common ForkJoinPool footgun.

**Short answer:**
`parallelStream()`, `CompletableFuture.supplyAsync` without executor, and bounded elastic schedulers misused for blocking work all starve `ForkJoinPool.commonPool()` — hurting every other parallel task and sometimes request handling. parallelStream(), supplyAsync without executor, and blocking on common pool starve shared JVM resource. Common pool size ≈ CPUs − 1 — blocking JDBC inside parallelStream blocks workers for all. Isolate blocking work on dedicated pools. parallelStream(), supplyAsync without executor, and blocking on common pool starve shared JVM resource. parallelStream(), supplyAsync without executor, and blocking on common pool starve shared JVM resource. parallelStream(), supplyAsync without executor, and blocking on common pool starve shared JVM resource. parallelStream(), supplyAsync without executor, and blocking on common pool starve shared JVM resource.

#### What it is
The common pool is a shared JVM resource — treating it as a general executor is a production incident. ForkJoinPool.commonPool() is shared — treating it as general executor causes incidents.

#### How it works (internals)
Common pool size ≈ CPUs − 1. Blocking JDBC inside `parallelStream` blocks a worker — other parallel work stalls. Same for Reactor `publishOn(boundedElastic)` with blocking calls without care.

#### When to use / when NOT to use
Isolate blocking work on dedicated cached/fixed pools. Reserve common pool for CPU-bound parallel streams if used at all. Never default supplyAsync for I/O.

#### Production example
Incident: checkout latency spikes when nightly job runs `orders.parallelStream()` doing HTTP enrichment on commonPool. Fix: dedicated `ExecutorService` with 10 threads. Checkout latency spikes when nightly job runs orders.parallelStream() doing HTTP on commonPool. Fix: dedicated ExecutorService.

#### Common mistakes
parallelStream in @RestController by default. Blocking in supplyAsync(). Assuming parallel always faster.

#### Interview follow-ups (with model answers)

**Q:** Custom ForkJoinPool for parallelStream?
**A:** ForkJoinPool customPool = new ForkJoinPool(4); customPool.submit(() -> list.parallelStream()...).get() — isolates from common pool. Rarely needed — prefer explicit executor mapping list to CompletableFuture.allOf. parallelStream hard to test and tune. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** commonPool parallelism flag?
**A:** -Djava.util.concurrent.ForkJoinPool.common.parallelism=N sets pool size. Raising it does not fix blocking — multiplies blocked threads. Per-task ForkJoinPool for CPU stages only. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Work stealing vs dedicated executor?
**A:** Work stealing excels at CPU-bound divisible tasks with short tasks. Blocking work defeats stealing — workers park, pool starves. Dedicated fixed pool with bounded queue for I/O — predictable saturation behavior. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

@RestController returns orders.parallelStream().map(this::enrichViaHttp)... — p99 degrades when any other team uses parallelStream in same JVM.

Shared common pool contention. Fix: remove parallelStream from request path; use dedicated executor with bulkhead and timeout per enrich call. Or sequential if N small. Code review ban parallelStream in controller layer.

---

### 15. BlockingQueue implementations.

**Short answer:**
`ArrayBlockingQueue`: bounded array, optional fairness. `LinkedBlockingQueue`: optionally bounded, two-lock design. `SynchronousQueue`: handoff, zero capacity — `CachedThreadPool`. `PriorityBlockingQueue` and `DelayQueue` for scheduling. Always bound producer-consumer queues.

#### What it is
BlockingQueue is the standard bounded buffer between producers and consumers.

#### How it works (internals)
put/take block at capacity/empty. offer/poll with timeout enable degradation. Fairness reduces throughput. SynchronousQueue pairs producer directly with consumer thread.

#### When to use / when NOT to use
ArrayBlockingQueue for fixed capacity worker pools. Linked when you need higher throughput and known bound. Linked when higher throughput and known bound.

#### Production example
Ingest pipeline: `ArrayBlockingQueue(10_000)` + `CallerRunsPolicy` — Kafka consumer pauses when downstream full. Ingest pipeline: ArrayBlockingQueue(10_000) plus CallerRunsPolicy — Kafka consumer pauses when downstream full.

#### Common mistakes
Integer.MAX_VALUE capacity LinkedBlockingQueue in fixed thread pool factory. Unbounded DelayQueue memory growth.

#### Interview follow-ups (with model answers)

**Q:** BlockingQueue vs Disruptor?
**A:** Disruptor: ring buffer, wait strategies, ultra-low latency, more complex API. BlockingQueue sufficient for most Spring services. Disruptor for HFT-style in-process pipelines. Disruptor requires careful producer type and backpressure design. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** poll vs take?
**A:** take blocks indefinitely until element available — use in dedicated consumer loops with shutdown flag. poll with timeout allows checking shutdown between waits. put blocks; offer returns false or times out — use offer for degrading producers under load. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** TransferQueue?
**A:** LinkedTransferQueue — producer may block until consumer takes — synchronous handoff variant. SynchronousQueue is zero-capacity TransferQueue. Useful when you want backpressure to slow producer to consumer pace. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Kafka consumer lag grows unbounded — downstream executor uses Executors.newFixedThreadPool(50) with default unbounded queue.

Tasks enqueue faster than processing — memory grows, GC pauses, consumer appears slow. Fix: bounded queue, CallerRunsPolicy pauses poll loop, or pause consumer when queue > threshold. Metric: queue size and consumer lag correlated.

---

### 16. ConcurrentHashMap compound operations.

**Short answer:**
`putIfAbsent`, `compute`, `computeIfAbsent`, and `merge` are atomic per key. `if (map.get(k)==null) map.put(k,v)` is not. `computeIfAbsent` mapping function must be fast and must not recursively modify the same map. putIfAbsent, compute, computeIfAbsent, merge are atomic per key. putIfAbsent, compute, computeIfAbsent, merge are atomic per key. putIfAbsent, compute, computeIfAbsent, merge are atomic per key. putIfAbsent, compute, computeIfAbsent, merge are atomic per key. putIfAbsent, compute, computeIfAbsent, merge are atomic per key.

#### What it is
ConcurrentHashMap provides atomic single-key operations but not arbitrary multi-key transactions. CHM provides atomic single-key operations but not arbitrary multi-key transactions.

#### How it works (internals)
Bin-level locking/CAS in Java 8+ enables atomic compute without locking whole map. Recursive computation on same map can deadlock (RecursiveUpdate). Size is an estimate under concurrency.

#### When to use / when NOT to use
Use compute* methods for cache loading and counters. Don't nest map modifications inside compute callbacks. Use compute* for cache loading and counters. Do not nest map modifications inside compute callbacks.

#### Production example
Idempotent cache: `cache.computeIfAbsent(key, k -> loadFromDb(k))` prevents duplicate loads versus check-then-put races. Idempotent cache: cache.computeIfAbsent(key, k -> loadFromDb(k)) prevents duplicate loads versus check-then-put races.

#### Common mistakes
computeIfAbsent calls another key's compute on same map — deadlock in prod. Long DB call inside compute blocks other keys in the same bin. computeIfAbsent calls another key compute on same map — deadlock. Long DB call inside compute blocks bin.

#### Interview follow-ups (with model answers)

**Q:** CHM vs synchronized HashMap?
**A:** CHM: concurrent reads, striped writes, no whole-map lock. synchronized HashMap or Collections.synchronizedMap requires external sync for iteration and compounds. Never use HashMap shared across threads. CHM size is estimate — do not use for strict capacity enforcement without extra sync. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** computeIfAbsent thundering herd?
**A:** Only one thread computes per key — others block on that bin. For expensive load, use LoadingCache with refreshAfterWrite or external single-flight pattern. Long compute blocks other keys in same bin — hash to spread hot keys. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** merge for counters?
**A:** map.merge(key, 1, Integer::sum) atomically increments per key — better than get-put race. For high contention counters on few keys, LongAdder per key or Redis. merge suits per-entity tallies in memory. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Service deadlocks rarely under load — thread dump shows threads in ConcurrentHashMap.computeIfAbsent waiting on each other.

Mapping function for key A calls computeIfAbsent on key B while B's function calls A — RecursiveUpdate deadlock. Fix: load outside compute into local, then putIfAbsent; or separate cache loader service. Code review: no nested CHM compute on same map instance.

---

### 17. CopyOnWriteArrayList vs ConcurrentLinkedQueue.

**Short answer:**
CopyOnWriteArrayList snapshots the array on write — iterators never throw CME, readers don't block; writes are O(n). ConcurrentLinkedQueue is an unbounded lock-free M&S queue — high throughput, non-blocking `poll`, no blocking `take`. CopyOnWriteArrayList snapshots array on write — iterators never throw CME, writes O(n). ConcurrentLinkedQueue: unbounded lock-free M&S queue — high throughput, no blocking take.

#### What it is
Two concurrent collection styles optimized for opposite read/write ratios. Two collection styles optimized for opposite read/write ratios.

#### How it works (internals)
COWAL suits event listener lists updated rarely. CLQ for producer-consumer without capacity bound — pair with backpressure elsewhere. For blocking consumers use `LinkedBlockingQueue`.

#### When to use / when NOT to use
COWAL for read-mostly registries. CLQ for lock-free handoff when you handle overflow policy externally. COWAL for event listener lists updated rarely. CLQ when unbounded queue acceptable with drop policy elsewhere.

#### Production example
Spring event listeners in COWAL — dispatch during fireEvent is snapshot-consistent. Metrics queue uses CLQ between threads with separate drop policy when full. Metrics handoff uses CLQ with separate drop policy.

#### Common mistakes
COWAL for frequently updated cache. CLQ without memory bound under flood. Expecting CLQ size to be cheap.

#### Interview follow-ups (with model answers)

**Q:** COWAL iterator staleness?
**A:** Iterator reflects snapshot at creation time — may miss concurrent adds, never sees concurrent removes after snapshot. Safe for fire-and-forget listener dispatch. Do not use iterator for strict latest-view requirements. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** CLQ size() linear?
**A:** size() walks entire queue — O(n) — do not call in hot metrics loop. isEmpty() is constant time. For bounded size tracking, maintain separate AtomicInteger with offer/poll discipline. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** BlockingDeque choices?
**A:** LinkedBlockingDeque for work-stealing worker pools with take from both ends. ArrayBlockingDeque fixed capacity. Prefer over CLQ when consumers need blocking take with timeout for shutdown. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Team uses CopyOnWriteArrayList as hot cache updated 1000/sec — CPU 90%, GC churn.

Every write copies entire array — wrong structure. Fix: Caffeine cache or CHM with TTL. COWAL only when writes << reads (listeners, feature flags). JFR ObjectAllocationInNewTLAB shows massive byte[] from COWAL.

---

### 18. CountDownLatch vs CyclicBarrier vs Phaser vs Semaphore.

**Short answer:**
CountDownLatch: one-shot; threads await until count reaches zero. CyclicBarrier: N threads rendezvous, reusable. Phaser: dynamic parties and phased computation. Semaphore: permit pool limiting concurrency.

#### What it is
Coordination primitives for startup gates, phased work, and resource limiting.

#### How it works (internals)
Latch count only decreases; barrier cycles. Phaser supports dynamic registration. Semaphore `acquire/release` unlike latch await. Exchanger for two-thread handoff.

#### When to use / when NOT to use
Latch to start N workers after setup (count 1) and await completion (count N). Semaphore to cap concurrent DB migrations. Latch for start gate and await completion.

#### Production example
Integration test: main counts down start latch; 10 workers process; completion latch awaits N finished tasks.

#### Common mistakes
Using latch where barrier needed for repeated phases. Semaphore forget release — permit leak. CyclicBarrier brokenBarrierAction ignored.

#### Interview follow-ups (with model answers)

**Q:** Phaser vs ForkJoin?
**A:** Phaser coordinates explicit phases with dynamic party count — bulk parallel pipelines with variable workers. ForkJoinPool for recursive divide-conquer CPU work. Phaser for simulation ticks or multi-stage ETL where parties join mid-flight. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Fair semaphore?
**A:** new Semaphore(n, true) queues acquirers FIFO — reduces starvation, lower throughput. Default unfair like locks. Use fair when permit starvation caused incident — rare. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Latch vs join all threads?
**A:** CountDownLatch decouples counter from thread count — one thread can countDown multiple times. join requires per-thread completion. Latch works with thread pools where threads are reused — count tasks not threads. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

DB migration tool allows 50 parallel Flyway workers — Oracle ORA-00060 deadlocks multiply. Team added Semaphore(5) but still fails after 2 hours.

Permit leak — worker throws before release in finally. Fix: try { acquire } finally { release }. Monitor availablePermits metric. Semaphore matches connection budget; fair optional.

---

### 19. ReadWriteLock when it helps and when it doesn't.

**Short answer:**
ReadWriteLock helps when reads dominate and critical sections are long enough to amortize lock overhead. Often a simple mutex is faster due to JVM optimizations and cache effects. StampedLock optimistic reads can win — measure first.

#### What it is
Read/write locks allow concurrent readers OR one writer — not magic scalability. RW lock allows concurrent readers OR one writer — not automatic scalability.

#### How it works (internals)
Write lock excludes all readers. Read lock blocks writers. Lock upgrade/downgrade protocols are error-prone. Short critical sections: synchronized may beat RW lock due to lower bookkeeping.

#### When to use / when NOT to use
Profile before adopting RW lock. Consider immutable snapshots for read-heavy config. Profile before RW lock.

#### Production example
RW lock added to 50-line synchronized block — throughput unchanged; removed as complexity without gain. StampedLock won on read-heavy tariff table. RW lock on 50-line synchronized block — throughput unchanged; removed.

#### Common mistakes
Upgrade lock without protocol — deadlock. Read lock then calling alien code that writes. Fair RW lock on hot path.

#### Interview follow-ups (with model answers)

**Q:** StampedLock vs ReentrantReadWriteLock?
**A:** RRW: reentrant, readLock/writeLock familiar API. StampedLock: optimistic reads, no reentrancy, better read throughput microbenchmarks. StampedLock harder to maintain. Start with synchronized or AtomicReference immutable copy. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** When does mutex beat RW lock?
**A:** Short critical sections — lock acquire cost dominates. RW lock bookkeeping exceeds benefit under microsecond holds. Profiling shows synchronized faster on single-field read/write. JVM lock coarsening helps synchronized. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Read-only immutable copy pattern?
**A:** AtomicReference<ImmutableConfig> — writers build new instance, atomic swap. Readers never take lock. Copy-on-write for config is production default over RW lock. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Tariff service added ReentrantReadWriteLock — read:write 500:1 but p99 unchanged. CPU slightly higher.

Critical section too short — lock overhead dominates. Fix: AtomicReference<TariffTable> updated hourly, reads lock-free. Or StampedLock optimistic after JMH proof. Remove RW lock complexity.

---

### 20. False sharing.

**Short answer:**
False sharing occurs when independent variables sit on the same CPU cache line; cores invalidate each other on unrelated writes. Fix with padding, `@Contended`, or striped counters like `LongAdder`. False sharing: independent variables on same cache line — cores invalidate each other on unrelated writes. Fix with padding, @Contended, or striped counters like LongAdder.

#### What it is
False sharing is a hardware-level performance bug invisible in source logic. Cache lines ~64 bytes are coherence units — layout matters for hot counters.

#### How it works (internals)
Cache lines (~64 bytes) are coherence units. Two `AtomicLong` counters adjacent in an array may ping-pong the line. JFR shows high cache miss rate with low logical contention.

#### When to use / when NOT to use
Use LongAdder for hot counters. `@Contended` (JVM flag) pads fields in JDK internal code — use sparingly in app code. LongAdder for hot counters. @Contended sparingly with JVM flag.

#### Production example
Throughput plateaus at 8 threads on 16-core box — counters in single `long[]`. Padding array elements or LongAdder restores scaling. Padding or LongAdder restores scaling.

#### Common mistakes
Blaming locks when false sharing. Excessive @Contended everywhere. Ignoring layout in off-heap structures.

#### Interview follow-ups (with model answers)

**Q:** @Contended requirements?
**A:** JVM flag -XX:-RestrictContended may be needed for user code. JDK uses @Contended internally. Padding manually with long fields between hot counters works. JMH with multiple threads required to detect. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** JMH false sharing detection?
**A:** Benchmark array of padded vs unpadded AtomicLong with @Threads(16). Unpadded shows throughput collapse as threads increase. Include perfasm or JFR during JMH fork. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Array vs LongAdder layout?
**A:** LongAdder stripes across cells reducing same-line contention. AtomicLong array without padding shares lines between indices. Prefer LongAdder per metric in Micrometer. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Custom metrics array AtomicLong[64] indexed by threadId — scaling stops at 8 cores, no lock contention in JFR.

False sharing on cache line spanning multiple array elements. Fix: LongAdder per thread, or pad to 64 bytes per counter, or @Contended wrapper. Re-run JMH — expect linear scaling to core count.

---

### 21. Memory barriers / fences at a practical level.

**Short answer:**
Application code rarely emits fences directly — `volatile`, locks, and `VarHandle` access modes provide acquire/release semantics. Understand them when reading lock-free code or JNI. Understand fences when reading lock-free code or JNI.

#### What it is
Memory barriers constrain reordering of loads/stores across threads.

#### How it works (internals)
Volatile write = release; volatile read = acquire. `VarHandle` offers opaque/acquire/release/volatile modes for expert APIs. `Unsafe` deprecated path — migrate to VarHandle.

#### When to use / when NOT to use
Use JUC abstractions; don't hand-roll fences unless implementing lock-free structures with tests (jcstress). Use j.u.c abstractions. VarHandle for expert off-heap and lock-free structures with tests.

#### Production example
Lock-free ring buffer uses VarHandle ordered writes — documented HB between producer and consumer indices.

#### Common mistakes
Copying C++ fence patterns unnecessarily. Assuming volatile on one field protects unrelated fields without protocol.

#### Interview follow-ups (with model answers)

**Q:** VarHandle vs AtomicInteger?
**A:** AtomicInteger is boxed counter with familiar API. VarHandle operates on plain fields and arrays with chosen memory ordering — no object header overhead. Use VarHandle for off-heap MemorySegment coordination. Mis-ordering causes subtle bugs — prefer atomics in app code. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** StoreStore vs LoadLoad?
**A:** StoreStore: prior stores not reordered after barrier store. LoadLoad: subsequent loads not reordered before barrier load. volatile write has release (StoreStore + StoreLoad). Full fence is StoreStore + StoreLoad + LoadLoad + LoadStore. synchronized entry/exit provides full fence semantics. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Do you need fences with synchronized?
**A:** synchronized release on exit and acquire on entry provide full memory barrier — all prior writes visible to next holder. Reason to use volatile inside synchronized block is rare — usually redundant unless lock-free mix. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Vendor JNI library documents 'memory fence required after writeIndex' — team adds Thread.yield() 'for visibility'.

Yield is not a memory barrier. Fix: use library's VarHandle API or wrap with volatile index field. If stuck with JNI, document happens-before via AtomicInteger for index. jcstress test producer-consumer visibility.

---

### 22. Double-checked locking — write the correct form.

**Short answer:**
Double-checked locking requires a `volatile` instance field so readers don't see a partially constructed object. Local variable copy reduces volatile reads. Prefer initialization-on-demand holder or injection over hand-rolled singletons. DCL requires volatile instance field — readers must not see partially constructed object.

#### What it is
DCL is a lazy initialization pattern with a subtle JMM pitfall without volatile. Lazy initialization with subtle JMM pitfall without volatile.

#### How it works (internals)
First null check avoids locking after init. Synchronized block creates instance. Volatile publish ensures safe publication. Holder idiom uses class init lock — simpler and safe.

#### When to use / when NOT to use
Avoid DCL in application code — use Spring scope or enum/holder. Know it for interviews and legacy code review. Avoid DCL in application code — Spring @Component or enum holder. Know for interviews and legacy review.

#### Production example
Legacy singleton caused rare field-null — volatile on instance fixed. New code uses `@Component` singleton. Legacy singleton rare field-null — volatile on instance fixed. New code uses @Component singleton.

#### Common mistakes
DCL without volatile. Partially constructed this escape. Testing DCL only on single-core machine.

#### Interview follow-ups (with model answers)

**Q:** Why local variable copy in DCL?
**A:** Read volatile instance once into local — if non-null return without second volatile read. Inside synchronized, double-check local against instance before create — prevents multiple instantiation if two threads pass first check. Reduces volatile read traffic on hot path after init. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** enum singleton benefits?
**A:** Effective Java item 3 — JVM guarantees single instance, serialization-safe, reflection-safe. Preferred over DCL for true singletons. Not suitable for Spring-managed beans with injection. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Is DCL ever needed in Spring?
**A:** No — Spring container manages singleton scope thread-safely. DCL appears in legacy SDKs and lazy static holders. Review third-party libs for broken DCL without volatile when upgrading JDK. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Legacy payment SDK singleton returns non-null but getProcessor() is null once per million calls on multi-socket server.

Broken DCL without volatile — reader sees reference before constructor completes. Fix: volatile instance field or migrate to Spring bean. Add stress test 32 threads getInstance 1M iterations assert invariants.

#### Code / config (when useful)
```java
class Holder {
  private static volatile Foo instance;
  static Foo get() {
    Foo local = instance;
    if (local == null) {
      synchronized (Holder.class) {
        local = instance;
        if (local == null) instance = local = new Foo();
      }
    }
    return local;
  }
}
```

---

### 23. InterruptedException protocol.

**Short answer:**
Blocking methods throw InterruptedException and clear interrupt status. Catch only if you can abort; otherwise restore interrupt with `Thread.currentThread().interrupt()` and rethrow or exit. Thread pool shutdown uses interrupt — tasks must cooperate.

#### What it is
Interrupt is a cooperative cancellation signal, not a hard kill. Interrupt is cooperative cancellation, not hard kill.

#### How it works (internals)
Sleep, wait, join, BlockingQueue.take, lockInterruptibly respond to interrupt. Swallowing IE stops cancellation propagation. JDBC Statement.cancel is separate from thread interrupt.

#### When to use / when NOT to use
At API boundary: either propagate IE or convert to unchecked with cause. In worker loops: check interrupted flag and exit. At API boundary: propagate IE or convert to unchecked with cause. Worker loops check flag and exit.

#### Production example
Worker catches IE during shutdown, restores interrupt, returns — pool `awaitTermination` completes. Swallowing IE caused hung deploy. Swallowing caused hung deploy.

#### Common mistakes
Empty catch InterruptedException. Ignoring interrupt in long computation. Expecting interrupt during synchronized block without lockInterruptibly.

#### Interview follow-ups (with model answers)

**Q:** shutdownNow vs shutdown?
**A:** shutdown: orderly — no new tasks, finish queue. shutdownNow: interrupt workers, return pending tasks. Use shutdown first, awaitTermination, then shutdownNow for force. Spring lifecycle should mirror this. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Virtual thread interrupt?
**A:** Interrupt unmounts virtual thread from carrier when parked on interruptible blocking. Pinned threads may delay. Check pinned count in JFR during shutdown tests. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Reactive cancel vs interrupt?
**A:** Subscription.cancel stops reactive stream — no thread interrupt unless subscribeOn scheduler uses threads. BlockHound detects block in reactive. Do not mix blocking JDBC in reactive chain without bounded elastic with care. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Kubernetes deploy times out — old pods Terminating 15 min. Thread dump shows workers in TIMED_WAITING on HTTP call, interrupt status false.

Worker caught InterruptedException, logged, continued without restore or exit. Fix: on IE restore interrupt and break loop. HTTP client must use interruptible calls or cancel via Call.cancel. Test deploy rollback under load.

---

### 24. How does `synchronized` interact with wait/notify?

**Short answer:**
You must hold the monitor to call `wait`/`notify`. `wait` releases monitor and parks. `notify` wakes one waiter; prefer `notifyAll` unless protocol guarantees one waiter. Always `while (!condition) wait()` — spurious wakeups and lost signals otherwise.

#### What it is
wait/notify implement condition queues bound to intrinsic locks. wait/notify implement condition queues bound to intrinsic locks. wait/notify implement condition queues bound to intrinsic locks. wait/notify implement condition queues bound to intrinsic locks. wait/notify implement condition queues bound to intrinsic locks. wait/notify implement condition queues bound to intrinsic locks.

#### How it works (internals)
State changes and wait checks must use same lock. Signaling before wait without holding lock causes lost wakeup. `notifyAll` avoids starvation when multiple conditions share one lock (still use while loops per condition).

#### When to use / when NOT to use
Prefer `BlockingQueue` and `Condition` objects with ReentrantLock for new designs. Prefer BlockingQueue and Condition with ReentrantLock for new designs.

#### Production example
Buffer: `synchronized(lock) { while (empty) lock.wait(); }` — correct. `if (empty) wait` misses signal. Buffer: synchronized(lock) { while (empty) lock.wait(); } — correct. if (empty) wait misses signal.

#### Common mistakes
if instead of while. notify without holding lock.

#### Interview follow-ups (with model answers)

**Q:** Condition vs wait?
**A:** ReentrantLock.newCondition() gives multiple condition queues per lock — signal only payment waiters not inventory waiters. await/signal like wait/notify with tryLock support. Cleaner than one monitor multiple conditions. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Object.wait timeout?
**A:** wait(millis) returns on notify, interrupt, or timeout — always re-check condition in while loop. Use for shutdown polling instead of infinite wait. prefer poll(timeout) on BlockingQueue for new code. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Why spurious wakeup?
**A:** JVM allows thread to return from wait without notify — POSIX legacy. while loop is mandatory defense. Also handles another thread stealing resource between notify and re-acquire. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Legacy inventory pool double-allocates slots under Black Friday — synchronized wait/notify on Pool.

Used if (slotAvailable) wait() not while. Spurious wakeup or stolen slot proceeds without valid reservation. Fix: while (!tryReserve()) pool.wait() with notifyAll, or replace with ArrayBlockingQueue of permits. Load test 500 concurrent reservations.

---

### 25. Lock-free vs wait-free vs blocking.

**Short answer:**
Blocking: threads may park on locks. Lock-free: system-wide progress — at least one thread completes in finite steps. Wait-free: every thread progresses in bounded steps per operation. Lock-free ≠ always faster — CAS retry storms hurt.

#### What it is
Progress guarantees classify concurrent algorithms for reasoning and selection.

#### How it works (internals)
Most production code is blocking with clear invariants. Lock-free queues for ultra-low latency niche. Wait-free rare in app code.

#### When to use / when NOT to use
Start blocking + correct. Optimize to lock-free only with profiling and jcstress tests. Start blocking and correct.

#### Production example
Team replaced blocking queue with lock-free for 'performance' — p99 worse due to CAS contention; reverted. Team replaced BlockingQueue with lock-free for performance — p99 worse from CAS contention; reverted.

#### Common mistakes
Assuming lock-free is wait-free. No backoff on CAS spin. Complexity without measurement.

#### Interview follow-ups (with model answers)

**Q:** Michael-Scott queue?
**A:** Classic lock-free FIFO linked queue — CAS on head/tail. ConcurrentLinkedQueue is based on this family. ABA matters with node reuse. j.u.c implementation battle-tested — do not reimplement. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** When is blocking preferable?
**A:** When simplicity, clear invariants, and BlockingQueue backpressure matter more than microsecond latency. Payment orchestration, Kafka consumers, JDBC — blocking with bounds is production default. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Disruptor wait strategy?
**A:** Disruptor consumers wait on ring buffer with BlockingWaitStrategy, YieldingWaitStrategy, or BusySpinWaitStrategy — latency vs CPU trade-off. Not lock-free vs blocking in JMM sense but scheduling strategy for consumer progress. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Trading desk asks for lock-free order book 'for latency'. JMH shows p50 improved 2µs but p99 worse 10x under contention.

CAS retry storms on hot symbols hurt tail latency. Fix: stay with striped locks or single-writer actor per symbol. Lock-free wins only with measured tail under production contention. Present p99/p999 not just p50.

---

### 26. Thread dump: BLOCKED vs WAITING vs TIMED_WAITING.

**Short answer:**
BLOCKED: waiting to enter synchronized monitor or ReentrantLock. WAITING: wait, join, park without timeout. TIMED_WAITING: sleep, timed wait, poll with timeout. RUNNABLE may be running or blocked in native I/O — correlate with DB and network metrics.

#### What it is
Thread states in dumps explain what threads are waiting on. Thread dump states are the on-call map between JVM parking, monitors, and blocked native I/O.

#### How it works (internals)
`- waiting to lock <0x...>` shows monitor. `java.util.concurrent.locks.LockSupport.park` common in j.u.c. Socket read shows RUNNABLE in Java but blocked in kernel.

#### When to use / when NOT to use
Take multiple dumps. Match BLOCKED stacks to pool exhaustion or deadlock. Use during p99 spikes and pool saturation — never conclude from a single snapshot.

#### Production example
All http-nio BLOCKED on Hikari pool — not deadlock, capacity. TIMED_WAITING on `parkNanos` — normal pool idle. All http-nio BLOCKED on Hikari — pool capacity issue, not lock tuning.

#### Common mistakes
Treating all RUNNABLE as CPU busy. One dump conclusion. Ignoring 'parking to wait for' lock name.

#### Interview follow-ups (with model answers)

**Q:** How do you read jcmd Thread.print output under load without stopping the JVM?
**A:** Run `jcmd <pid> Thread.print` or `jstack` on the pod — both are safe on Linux if you accept brief I/O for the output file. Capture three samples two seconds apart and diff thread names plus lock hex addresses. Pipe to a timestamped file with pod and namespace; correlate BLOCKED stacks with Hikari pending threads, Kafka consumer lag, and Redis pool metrics in Grafana. On Kubernetes, `kubectl exec` into the app container with the same JDK build, or use an ephemeral debug container. Avoid kill -9 before capture — you lose the evidence chain for postmortem. For frequent sampling, prefer JFR thread dump events over full prints every minute. Document which executor bean name appears in thread names so on-call does not guess from obfuscated stacks.

**Q:** How do virtual threads appear in a thread dump compared to platform threads?
**A:** Virtual threads appear as separate entries with carrier thread references in JDK 21+ dumps — many virtual threads may share few carrier platform threads. A blocked virtual thread on JDBC usually unmounts from the carrier; if pinned by synchronized blocks or native JDBC, the carrier stays busy and JFR reports VirtualThreadPinned events. Do not panic at ten thousand parked virtual threads; panic when all carriers are RUNNABLE with growing request queues. Tune `jdk.virtualThreadScheduler.parallelism` after enabling `spring.threads.virtual.enabled`. Remediation for pinning differs from adding Tomcat max threads — remove unnecessary synchronized wrappers around JDBC first.

**Q:** When is TIMED_WAITING healthy versus a sign of trouble?
**A:** TIMED_WAITING on `LockSupport.parkNanos` inside `ThreadPoolExecutor` is often an idle worker waiting for work — healthy at low utilization. Trouble when every http-nio thread is TIMED_WAITING on `Future.get()` without a gateway-aligned timeout, or when a `CountDownLatch` never reaches zero during deploy. Kafka consumer TIMED_WAITING on poll timeout is normal; TIMED_WAITING forever on a misconfigured join is not. Trend active pool count, queue depth, and dump state together — healthy systems show state movement between dumps. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Saturday 2 a.m.: checkout p99 is 12s. Tomcat threads are at max. jstack shows all http-nio threads RUNNABLE in `socketRead0` on payment-gateway HTTPS.

This is outbound I/O wait masquerading as RUNNABLE, not a Java deadlock. Correlate with gateway latency and HTTP client connection-pool metrics — likely causes are pool too small, missing connect/read timeout, DNS stall, or TLS retry after cert rotation. Immediate mitigation: enable circuit breaker shedding, shorten timeouts, scale replicas if CPU is low. A second dump with unchanged stacks confirms kernel I/O block. Permanent fix: bounded async client pool, bulkhead between payment and catalog calls, propagate per-request deadlines from the gateway. Post-incident: alert when all threads are in socketRead0 and track client pool pending acquire count.

---

### 27. How do you debug a production deadlock at 2 a.m.?

**Short answer:**
Capture `jcmd <pid> Thread.print` — JVM reports Java deadlocks. Identify cycle, restart if customer-impacting, then fix lock ordering. Add tryLock timeouts and stress tests. Check accidental locking on HashMap.

#### What it is
Deadlock response is detect, mitigate, root-cause, prevent recurrence. Production deadlock response is detect, mitigate, fix lock ordering, prevent recurrence.

#### How it works (internals)
Kill -3 on Linux sends SIGQUIT for thread dump (legacy). Fix: global lock order, shrink critical sections, concurrent collections. jcstress reproduces JMM bugs; stress tests reproduce lock cycles. jcmd reports monitor cycles with hex addresses; match stacks to code via lock names. jcmd reports monitor cycles with hex addresses; match stacks to code via lock names. jcmd reports monitor cycles with hex addresses; match stacks to code via lock names. jcmd reports monitor cycles with hex addresses; match stacks to code via lock names. jcmd reports monitor cycles with hex addresses; match stacks to code via lock names.

#### When to use / when NOT to use
Runbook: dump → identify → scale/restart → patch → chaos test. Alert on thread pool blocked count. Runbook: dump → identify → restart if customer-impacting → patch → stress test.

#### Production example
Deadlock between `OrderService` and `PaymentClient` callback — reorder to acquire payment lock before order lock consistently. OrderService/PaymentClient callback lock inversion — global lock order document.

#### Common mistakes
Restart without capture — lose evidence. Fair locks as band-aid. Deadlock in DB only visible in SQL trace.

#### Interview follow-ups (with model answers)

**Q:** What are JVM deadlock detection limits and when does it miss problems?
**A:** HotSpot detects cycles of threads waiting on monitors it knows about — synchronized and ReentrantLock deadlocks. It does not detect livelock, starvation, DB row locks, or HTTP cross-service waits. It may miss deadlocks if threads are not fully blocked when the dump is taken. Always manually scan for BLOCKED threads waiting on each other's monitors even when JVM reports none. Cross-service deadlocks need distributed tracing and DB session views, not jstack alone. Save three dumps before restart and add ArchUnit lock-order tests for in-process code paths.

**Q:** Describe a tryLock timeout recovery pattern for non-critical sections.
**A:** Use `ReentrantLock.tryLock(200, TimeUnit.MILLISECONDS)` on background config refresh — on timeout, skip refresh and serve stale config rather than block request threads. Log the lock holder thread name once per minute and increment metric `lock_acquire_timeout`. For admin operations, return 503 with Retry-After if the lock cannot be acquired. In Kafka consumers, call `consumer.pause` on timeout rather than blocking the poll loop indefinitely. Never spin on tryLock in http-nio threads without an overall deadline aligned to the gateway timeout.

**Q:** How do you reproduce a rare lock-order deadlock before shipping a fix?
**A:** Write an integration test with two threads acquiring two locks in opposite order under a `CyclicBarrier` — thread A: lock1→lock2, thread B: lock2→lock1, loop with `@RepeatedTest(500)`. Add jcstress if JMM visibility is involved. In staging, run Gatling while manually triggering the callback path that caused the production cycle. Document the lock hierarchy in ARCHITECTURE.md and enforce via code review checklist for new callback paths. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Ledger service freezes after deploy. jstack shows deadlock between `InventoryService` and `KafkaProducer` callback.

Classic lock-order inversion: inventory holds `inventoryLock` then sends a Kafka message; the producer callback synchronizes on the same lock. Mitigate: save dump, rolling restart, disable synchronous callback via feature flag if available. Fix: remove synchronized from callback, use a concurrent handoff queue per sku, never call `kafkaTemplate.send` while holding a domain monitor. Add tryLock with timeout on the hot path for graceful degradation. Regression: stress test with mock callback re-entry. Postmortem: ArchUnit rule forbidding `@KafkaListener` methods that synchronize on domain locks.

---

### 28. HashMap in concurrent use — failure modes.

**Short answer:**
Concurrent HashMap use without synchronization causes lost updates, infinite loop (Java 7 resize), null entries, and ConcurrentModificationException on iterate. Fix: ConcurrentHashMap, confinement, or synchronized access to all operations including iteration. Wrapping with synchronizedMap does not make compound iterate+modify safe without external sync.

#### What it is
HashMap is not thread-safe — period.

#### How it works (internals)
Java 8+ resize is safer than Java 7 but still corrupts under races. Wrapping with synchronizedMap still requires external sync for compound iterations.

#### When to use / when NOT to use
Default to CHM for shared maps. Single-threaded ownership is valid pattern. Default shared map to ConcurrentHashMap; use confinement when single-threaded ownership is clear.

#### Production example
Scheduler shared HashMap across threads — rare lost tasks. CHM + putIfAbsent fixes.

#### Common mistakes
Collections.synchronizedMap then iterate without external sync. Assume read-only HashMap is safe if no writes (writes elsewhere still race). synchronizedMap then iterate without external sync; assuming read-only races are safe with a background writer. synchronizedMap then iterate without external sync; assuming read-only races are safe with a background writer. synchronizedMap then iterate without external sync; assuming read-only races are safe with a background writer. synchronizedMap then iterate without external sync; assuming read-only races are safe with a background writer. synchronizedMap then iterate without external sync; assuming read-only races are safe with a background writer.

#### Interview follow-ups (with model answers)

**Q:** What iteration guarantees does ConcurrentHashMap provide?
**A:** CHM iterators are weakly consistent — they reflect map state at some point at or since iterator creation, throw no ConcurrentModificationException, but may or may not see very recent writes. `size()` and `isEmpty()` are approximate under concurrency. Bulk `forEach`, `search`, and `reduce` operations are often safer than manual iteration for reports. For a strict point-in-time snapshot for billing reconciliation, copy entries under a lock or use an immutable snapshot reference swapped atomically. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Why does ConcurrentHashMap not allow null keys or values?
**A:** Null is ambiguous in concurrent `get` — you cannot distinguish absent key from null value without extra synchronization. Doug Lea's design avoids that ambiguity entirely. When migrating from HashMap, latent null bugs may surface as NPE. Use `Optional` wrapper values or a sentinel object for 'no value' semantics in caches and registries. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** When is per-thread HashMap confinement better than ConcurrentHashMap?
**A:** Request-scoped aggregation: build a HashMap in a single request thread, then pass an immutable copy downstream — zero coordination overhead. ForkJoin tasks with a local HashMap merged once at the end beats a shared CHM for CPU-bound counting when merge is infrequent. A Kafka consumer with one thread per partition can use HashMap for in-poll-batch dedupe because no other thread touches that map. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

After traffic doubling, a job scheduler intermittently drops tasks with no error logs. Twenty `@Scheduled` readers iterate a HashMap while one thread writes.

Concurrent read during write on plain HashMap is undefined behavior — not always CME, sometimes silent skipped keys. Fix: `ConcurrentHashMap` for the shared registry, or `CopyOnWriteArrayList` of immutable job snapshots refreshed each tick. Add a metric comparing scheduled register count versus execute count. Short-term: synchronize the entire iterate block if the tick is infrequent and the map is small. Load test with fifty schedulers across pods before closing the ticket.

---

### 29. Work stealing vs dedicated threads.

**Short answer:**
ForkJoin work-stealing splits tasks; idle workers steal from busy deques — great for CPU-bound divide-and-conquer. Dedicated threads isolate workloads — better for blocking I/O, predictable latency, partition affinity (Kafka consumer per partition). Work stealing excels at CPU divide-and-conquer; dedicated threads excel at blocking I/O and Kafka ordering. Blocking a ForkJoinPool worker stalls steals globally.

#### What it is
Scheduler choice matches task shape: CPU parallel vs blocking or pinned work. Scheduler topology must match task shape.

#### How it works (internals)
Stealing fails when tasks block — workers stall, steals block too. Dedicated thread per partition preserves ordering and simplifies offset management. FJP deque: owner LIFO, thief FIFO — breaks when tasks block.

#### When to use / when NOT to use
CPU batch: FJP. Kafka consumer, netty event loop: dedicated. Don't block FJP workers.

#### Production example
Moved blocking enrichment off commonPool to dedicated 16-thread pool — parallel report job stable. Moved blocking HTTP off commonPool — report p99 stable.

#### Common mistakes
CachedThreadPool for Kafka consumers. FJP for JDBC. Stealing across tenants without isolation.

#### Interview follow-ups (with model answers)

**Q:** How do you size ForkJoinPool parallelism for batch ETL?
**A:** Start at `availableProcessors()` for pure CPU transforms; use JFR — if GC or I/O waits dominate, more parallelism adds contention without gain. High steal rate with low throughput means tasks are too fine-grained or blocking inside `compute()`. Name the pool in thread dumps. Use a separate blocking-I/O executor to feed CPU work queues. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Why is one thread per Kafka partition a common pattern?
**A:** A single consumer thread per assigned partition preserves record order without extra locking and pairs naturally with offset commit semantics. Scale horizontally via more partitions and consumers, not more threads per partition unless you have an explicit merge step. Cooperative sticky assignor reduces rebalance churn when adding pods during deploy. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Virtual threads versus work stealing for HTTP request handling?
**A:** Virtual threads give economical thread-per-request for blocking stacks — Tomcat on virtual threads mounts many requests on few carriers. Work stealing is the wrong model for typical request handlers. Do not replace Kafka partition discipline with a flood of virtual threads on a single consumer instance. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Pricing service uses `parallelStream()` in a REST controller to call a rules engine per line item.

At lunch peak unrelated APIs slow down because `parallelStream` uses the JVM commonPool — blocking rule calls stall all FJP workers globally. Fix: sequential stream in the request path or a dedicated bounded executor; nightly repricing may use a named FJP. ArchUnit ban on `parallelStream` in controller packages.

---

### 30. Visibility of `final` fields.

**Short answer:**
After constructor completes without `this` escape, `final` fields are visible to any thread that sees the reference — safe publication of immutables. Non-final fields need additional HB edges. Final fields are safely published when the constructor completes without this-escape. final on a reference does not make mutable internals thread-safe.

#### What it is
Final field safe publication is a JMM guarantee for properly constructed objects. JMM final-field safe publication underpins immutable DTOs and records.

#### How it works (internals)
JVM freezes final field values at end of ctor for reader guarantees. Starting thread from ctor that reads `this` breaks guarantee.

#### When to use / when NOT to use
Make DTOs immutable with final fields. Don't leak `this` during construction. Immutable Kafka messages; never leak `this` from a constructor.

#### Production example
Singleton holder with final fields — safe lazy init. Ctor starts thread using partially constructed `this` — visibility bug. Holder idiom safe; thread started in ctor saw stale non-final config.

#### Common mistakes
final on reference only — mutable list inside still unsafe. Assuming all fields final without defensive copy. final List without unmodifiable wrap; records with mutable array fields exposed. final List without unmodifiable wrap; records with mutable array fields exposed. final List without unmodifiable wrap; records with mutable array fields exposed. final List without unmodifiable wrap; records with mutable array fields exposed. final List without unmodifiable wrap; records with mutable array fields exposed.

#### Interview follow-ups (with model answers)

**Q:** What is this-escape in a constructor and how do you prevent it?
**A:** Publishing `this` before the constructor completes — registering a listener, starting a thread, storing in a global map — lets another thread see default values for non-final fields. Prevent with factory methods, static holder idiom, or `@PostConstruct` after Spring injection. Serialization and reflection can break guarantees for security-sensitive singletons. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** How do final fields compare to volatile for one-shot publication?
**A:** A volatile write on a reference publishes with piggyback if the reader uses an acquire pattern. Final fields give a stronger guarantee for the fields themselves once the object is correctly published. Ongoing mutation needs locks or a new immutable snapshot — final does not help after construction completes. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Are Java records automatically safe for cross-thread messaging?
**A:** Records are shallowly immutable — copy collections in the compact constructor with `List.copyOf`. Safe publication still requires a happens-before edge when handing the record to another thread. Records excel as Kafka event payloads when handlers do not share mutable session state. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Config service publishes `ConfigHolder` from its constructor via a static registry before fields are assigned.

this-escape: a registry thread reads the holder while `enabledFeatures` is still default null. Fix: static factory that builds fully then registers, or `@PostConstruct` after `@Value` injection. Prefer `AtomicReference<ImmutableConfig>` swap on refresh.

---

### 31. `synchronized` on `this` vs private final lock object.

**Short answer:**
Synchronizing on `this` exposes your lock to clients who can synchronize on your instance and deadlock with you. Use `private final Object lock = new Object()` or private ReentrantLock. Never lock on interned strings or boxed integers. Synchronizing on `this` lets clients deadlock with you; use `private final Object lock`.

#### What it is
Lock object choice affects composability and contention scope. Lock object identity is part of your concurrency API.

#### How it works (internals)
Public API synchronized methods use `this` — unavoidable exposure. Internal sections should use private locks. String.intern and Integer cache create global accidental contention.

#### When to use / when NOT to use
Private final lock for all internal synchronization. Document if monitor is part of public contract. Private final lock for internal mutable state; document public synchronized methods as API contract.

#### Production example
Deadlock between library syncing on passed Integer(1) and app using same — use dedicated lock objects. Library synced on `Integer(1)` collided with app using literal 1.

#### Common mistakes
Lock on `getClass()` in static context confusion. Client can call synchronized method reentrantly badly. String literal lock.

#### Interview follow-ups (with model answers)

**Q:** When should you choose ReentrantLock over a private Object monitor?
**A:** ReentrantLock when you need tryLock with timeout, lockInterruptibly, fairness toggle, or multiple Condition queues. Private Object monitor is lighter for simple mutual exclusion. On some JDK versions ReentrantLock may reduce virtual-thread carrier pinning versus synchronized — verify with JFR on your stack. Always unlock in `finally`. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** How do you document lock ordering across microservices?
**A:** In-process: ArchUnit or a static lock-order enum. Cross-service: avoid nested distributed locks — use Kafka partition-key ordering or saga choreography. If Redisson is required, use a single key namespace with lease and watchdog; document acquisition order A→B→C in the runbook. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** What is monitor inflation and when does it hurt latency?
**A:** Uncontended locks use thin CAS on the mark word; contention inflates to a heavyweight OS monitor. High churn on one hot lock shows many BLOCKED threads and p99 spikes. Fix by shrinking critical sections, sharding locks, or using LongAdder instead of a synchronized counter. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

A third-party SDK synchronizes on `userId.toString()` while your app locks on the same interned tenant id string.

String intern locks are JVM-wide — unrelated subsystems serialize accidentally and may deadlock across callbacks. Fix: fork SDK config, wrap calls on a dedicated executor with timeout, or replace the SDK. Code search for `synchronized` on String in CI.

---

### 32. Bounded vs unbounded task submission — backpressure.

**Short answer:**
Unbounded queues hide overload until heap OOM. Bounded queue + rejection policy applies backpressure: CallerRuns slows producers, Abort throws (map to 503), Discard loses work (rare). Reactive systems use demand; Kafka consumers pause. Unbounded queues hide overload until OOM; bounded queue plus rejection policy applies backpressure.

#### What it is
Backpressure is explicit flow control when producers outpace consumers.

#### How it works (internals)
ThreadPoolExecutor queue capacity is the buffer. Metrics on queue size predict incidents. CallerRuns runs task on submitter — can block HTTP thread if misconfigured.

#### When to use / when NOT to use
Always bound. Choose policy matching SLA: shed load vs slow down vs fail fast. Always bound async paths; Kafka `consumer.pause` when downstream queue exceeds 80%.

#### Production example
Kafka ingest: pause consumer when downstream queue > 80% — prevents OOM. HTTP: 503 when pool saturated. Ingest OOM after marketing push — unbounded @Async queue fixed with ArrayBlockingQueue(500).

#### Common mistakes
LinkedBlockingQueue default Integer.MAX_VALUE. Ignoring rejection handler exceptions. Unbounded @Async executor.

#### Interview follow-ups (with model answers)

**Q:** How does reactive backpressure differ from ThreadPoolExecutor rejection?
**A:** Reactive stacks propagate demand via subscription — a slow subscriber reduces upstream rate. Thread pool rejection is coarser: fail, discard, or run on the caller when the buffer is full. Bridge carefully: blocking JDBC at the end of a reactive chain without a bounded scheduler still blows thread counts. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** When is CallerRunsPolicy correct versus AbortPolicy?
**A:** CallerRuns slows producers naturally — acceptable when the producer is an internal batch worker. Dangerous when the producer is an http-nio thread. AbortPolicy with a mapped 503 and Retry-After protects user-facing SLAs. Document the policy per executor bean in the service README. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** How do you implement the bulkhead pattern with bounded queues?
**A:** Separate executor per dependency so catalog slowness cannot exhaust payment threads. Combine with a semaphore limiting concurrent calls to fragile downstreams. Resilience4j bulkhead metrics on rejected and available concurrent calls. Test by killing the catalog dependency while payment stays green. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Order API at 2k rps uses default `@Async` for audit logging; heap grows until Full GC pause 40s during a flash sale.

SimpleAsyncTaskExecutor or an unbounded queue creates unbounded Runnable objects. Fix: named `auditExecutor` with ArrayBlockingQueue, or publish to a Kafka audit topic so HTTP only enqueues a record. Alert on queue depth above 70%.

---

### 33. Virtual threads: pinning, pooling, and JDBC.

**Short answer:**
Virtual threads mount on carrier pool; blocking I/O usually unmounts. Pinning from synchronized/native holds carrier — reduces scalability. Don't pool virtual threads; pool connections. Spring Boot 3.2+ enables virtual threads; still bound DB with pool and semaphores.

#### What it is
Virtual threads change thread-per-request economics, not connection limits. Virtual threads change thread economics, not connection limits.

#### How it works (internals)
JFR shows pinned events. ReentrantLock may avoid pinning vs synchronized on some JDK versions. Millions of virtual threads increase memory — still need limits.

#### When to use / when NOT to use
Enable for blocking stacks after load test. Monitor carrier pool and pin rate. Hikari size stays small.

#### Production example
10k virtual threads, 20 connections — queue at pool, acceptable. Pinning on custom synchronized JDBC wrapper — switch to ReentrantLock. 10k virtual threads, Hikari max 30 — queue at pool acceptable; pinning on synchronized JDBC wrapper fixed with ReentrantLock. 10k virtual threads, Hikari max 30 — queue at pool acceptable; pinning on synchronized JDBC wrapper fixed with ReentrantLock. 10k virtual threads, Hikari max 30 — queue at pool acceptable; pinning on synchronized JDBC wrapper fixed with ReentrantLock. 10k virtual threads, Hikari max 30 — queue at pool acceptable; pinning on synchronized JDBC wrapper fixed with ReentrantLock. 10k virtual threads, Hikari max 30 — queue at pool acceptable; pinning on synchronized JDBC wrapper fixed with ReentrantLock.

#### Common mistakes
10k connections because virtual threads. Pooling virtual threads. Ignoring pinned thread warnings.

#### Interview follow-ups (with model answers)

**Q:** What does spring.threads.virtual.enabled change in Spring Boot 3.2+?
**A:** Configures Tomcat to use virtual threads per request — higher concurrent blocking throughput with lower memory than a large platform pool. `@Async` and `@Scheduled` still use their TaskExecutor beans unless separately configured. MDC and SecurityContext need TaskDecorator on those executors. Load test with realistic JDBC latency. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** How many carrier threads should you configure?
**A:** Default equals available processors — usually fine for I/O-heavy workloads. Increase if JFR shows carriers constantly RUNNABLE with CPU headroom and pinning is not the cause. Property `jdk.virtualThreadScheduler.parallelism` tunes the scheduler. Keep a separate platform pool for CPU-bound work. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** How does StructuredTaskScope interact with virtual threads?
**A:** StructuredTaskScope forks subtasks with structured lifetime — shutdown on timeout cancels unfinished children. Pairs well with parallel blocking fetches with a deadline. Still align JDBC `queryTimeout` with the scope deadline. Not a replacement for resilience patterns on external dependencies. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Team enables virtual threads and doubles traffic; CPU is low but latency is high; JFR shows 40% pinned threads during JDBC.

A legacy DAO wraps the entire query in synchronized for 'thread safety' — pins the carrier for the full query. Remove synchronized, rely on the connection pool, or switch to ReentrantLock with short hold. Upgrade the JDBC driver if SSL pins in native code.

---

### 34. Race on lazy init of a cache.

**Short answer:**
Use `computeIfAbsent`, Caffeine loading cache, or correct DCL with volatile for expensive singletons. Beware thundering herd — multiple threads loading same key; Caffeine singleflight coalesces loads. Lazy cache init is check-then-act — use Caffeine, CHM computeIfAbsent, or correct DCL with volatile. Thundering herd: many threads miss the same key without singleflight coalescing.

#### What it is
Lazy cache initialization is a classic check-then-act race. Lazy cache initialization is a classic race and stampede problem.

#### How it works (internals)
CHM computeIfAbsent atomizes per key. Long load inside compute blocks bin. Caffeine `AsyncCache` or refreshAfterWrite for stale-while-revalidate.

#### When to use / when NOT to use
Prefer Caffeine over hand-rolled CHM cache for TTL, size, stats. Prefer Caffeine with TTL and size over hand-rolled CHM caches.

#### Production example
100 threads miss cache — without coalescing, 100 DB hits. Caffeine load coalescing → 1 query. 100 threads cold start — Caffeine load coalescing reduced DB from 100 queries to 1. 100 threads cold start — Caffeine load coalescing reduced DB from 100 queries to 1. 100 threads cold start — Caffeine load coalescing reduced DB from 100 queries to 1. 100 threads cold start — Caffeine load coalescing reduced DB from 100 queries to 1. 100 threads cold start — Caffeine load coalescing reduced DB from 100 queries to 1.

#### Common mistakes
get then put race. computeIfAbsent recursive map update. No TTL on unbounded cache. get then put race; recursive computeIfAbsent; no TTL on unbounded cache. get then put race; recursive computeIfAbsent; no TTL on unbounded cache. get then put race; recursive computeIfAbsent; no TTL on unbounded cache. get then put race; recursive computeIfAbsent; no TTL on unbounded cache. get then put race; recursive computeIfAbsent; no TTL on unbounded cache.

#### Interview follow-ups (with model answers)

**Q:** Caffeine versus ConcurrentHashMap for application cache?
**A:** Caffeine provides eviction, TTL, refresh, stats, and singleflight load coalescing — production-grade. CHM computeIfAbsent is a building block but lacks policy and thundering-herd protection without extra code. Micrometer integrates Caffeine metrics for hit-rate dashboards on hot keys. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Explain refreshAfterWrite versus expireAfterWrite.
**A:** expireAfterWrite removes the entry after TTL — the next get triggers a synchronous load unless async refresh is configured. refreshAfterWrite serves a stale value while an async reload runs — good for config that tolerates slight staleness. Document the staleness SLA for pricing or authZ caches. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** What is the singleflight pattern?
**A:** Only one in-flight load per key — concurrent missers wait on the same CompletableFuture or Caffeine internal lock. Prevents database stampede on hot key eviction or deploy cold start. Always handle load failure — do not cache negative results forever without TTL. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

FX rate cache uses `if (!map.containsKey(ccy)) map.put(ccy, restTemplate.get(...))`.

Check-then-act race — two threads both miss and call the API. Fix: `cache.get(ccy, k -> client.fetch(k))` with Caffeine, expireAfterWrite 60s, and integration test with fifty concurrent threads asserting one downstream call via MockWebServer.

---

### 35. How do you test concurrent code?

**Short answer:**
Use JCStress for JMM litmus tests, stress tests with barriers, Lincheck for Kotlin/Java, soak tests in staging. Extract sequential core for unit tests; keep concurrent shell thin. Never `Thread.sleep(100)` as sole synchronization. Unit tests alone miss races — use jcstress, stress harnesses, and soak tests in staging.

#### What it is
Concurrent correctness needs targeted tools — unit tests alone miss races.

#### How it works (internals)
jcstress explores allowed outcomes per JMM. Stress harness runs millions of interleavings. Code review for publication and lock order. TLA+ for protocols when worth it.

#### When to use / when NOT to use
Add jcstress module for lock-free code. Integration stress with fixed thread count and assertions on invariants. jcstress module for lock-free code; integration stress with fixed thread count and invariant assertions. jcstress module for lock-free code; integration stress with fixed thread count and invariant assertions. jcstress module for lock-free code; integration stress with fixed thread count and invariant assertions. jcstress module for lock-free code; integration stress with fixed thread count and invariant assertions. jcstress module for lock-free code; integration stress with fixed thread count and invariant assertions.

#### Production example
Race in idempotency cache found by 24h stress test — fixed with putIfAbsent. JCStress proved DCL broken without volatile. Idempotency cache race found after 24h Gatling soak — fixed with putIfAbsent.

#### Common mistakes
Sleep hoping for ordering. Single-threaded tests 'proving' concurrency. Ignoring thread pool in @SpringBootTest.

#### Interview follow-ups (with model answers)

**Q:** When do you add jcstress versus an integration stress test?
**A:** jcstress for memory model and lock-free atomics — small litmus tests with many iterations. Integration stress for lock ordering, pools, and Spring proxy paths with realistic stacks. Use both: jcstress for algorithm, Testcontainers Kafka plus twenty threads for handler idempotency. Flaky sleep-based tests are worse than no tests. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** How do you use Lincheck for custom concurrent structures?
**A:** Lincheck runs algorithms with explored interleavings on a single JVM — good for queues and stacks you implement. Annotate operations; the tool finds invariant violations. Cheaper than hand-writing jcstress for complex ADTs. Not a replacement for production soak when the system is open. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** What concurrency chaos experiments belong in staging?
**A:** Kill pod mid-Kafka poll; double consumer group during deploy; slow DB with toxiproxy while load test runs. Verify graceful shutdown drains the queue, no duplicate charge, MDC present in async logs. Document pass criteria before prod enable. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Team claims `@Transactional` payment service is thread-safe; QA single-thread tests pass; Black Friday double capture on same idempotency key.

Transaction boundary does not serialize two HTTP threads — both read unpaid, both charge. Need DB unique constraint on idempotency key plus putIfAbsent or SELECT FOR UPDATE. Fifty-thread JUnit with same key asserting one success. Staging soak two hours before event.

---

### 36. Happens-before and `volatile` one-way: why a non-volatile write before a volatile write is visible.

**Short answer:**
Volatile write acts as release fence: prior writes in that thread cannot be reordered after it. A later volatile read (acquire) in another thread sees the flag and those prior writes — piggyback pattern for status + payload fields. Volatile write is a release: prior plain writes in that thread cannot reorder after it. Piggyback: writer fills payload then `volatile ready=true`; reader must check ready before payload.

#### What it is
Volatile publishes not just the volatile field but prior writes in program order before the write. Volatile publishes more than the volatile field when used as a handoff flag.

#### How it works (internals)
Writer: update payload fields, then `volatile ready=true`. Reader: if `ready`, read payload — safe if no further writer mutation without another HB. Reader must not read payload before checking ready.

#### When to use / when NOT to use
Use for one-writer handoff. For ongoing updates, use locks or immutable snapshots. One-writer handoff; not for multi-writer payload mutation without synchronization.

#### Production example
Message buffer: writer fills array, sets volatile sequence. Reader waits for sequence then reads — lock-free single consumer. Ring buffer: writer fills slots, publishes volatile sequence; consumer waits then reads.

#### Common mistakes
Reader reads payload before ready flag. Writer mutates payload after ready without sync. Assuming piggyback works with multiple writers unsynchronized.

#### Interview follow-ups (with model answers)

**Q:** Explain release-acquire pairing in happens-before terms.
**A:** A release action ensures prior writes in the thread are visible to a thread performing the matching acquire that synchronizes-with it. The pair must be on the same volatile or lock — arbitrary plain reads after acquire see released writes. VarHandle release/acquire modes fine-tune for experts; volatile is the portable default. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** When should you use VarHandle instead of volatile?
**A:** VarHandle gives fine-grained access modes and atomic CAS on fields without sun.misc.Unsafe in application code. Use when implementing lock-free structures. For business DTO handoff, a volatile boolean remains clearer. Records and final fields often eliminate the need. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Can piggyback replace synchronized for a metrics snapshot?
**A:** Single writer builds a new int array snapshot and assigns to a volatile reference — readers see old or new, never torn if the array is immutable after publish. Better: AtomicReference<ImmutableSnapshot>. Reusing and mutating the same array after publish is wrong. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Telemetry sets `volatile boolean batchReady` after filling a reused `double[]` samples array.

Writer mutates while reader may read mid-update. Fix: swap `AtomicReference<double[]>` to a new array each tick. Never mutate an array after publishing its reference.

---

### 37. Atomic array vs LongAdder vs striped locks.

**Short answer:**
Single hot AtomicLong suffers CAS retries under contention. LongAdder stripes across cells — great for metrics counters, approximate sum. Striped locks partition keys across lock array for map-like structures. Hot AtomicLong suffers CAS retry storms; LongAdder stripes across cells for metrics throughput.

#### What it is
Contention sharding trades accuracy or memory for throughput. Contention sharding trades memory and approximate reads for write throughput.

#### How it works (internals)
LongAdder.sum() is not atomic snapshot mid-update — fine for metrics. AtomicIntegerArray for sparse per-slot counters. Striped lock on hash bucket reduces single lock dominance.

#### When to use / when NOT to use
Micrometer counters use LongAdder. Per-key locks in custom cache when CHM bin still hot. Micrometer counters use LongAdder; striped locks when CHM bin is still hot.

#### Production example
Global AtomicLong request counter at 50k RPS — CPU on CAS. LongAdder flat CPU. Global AtomicLong at 50k RPS burned CPU; LongAdder flattened CPU.

#### Common mistakes
LongAdder for financial totals requiring exact audit mid-flight. Wrong stripe count tuning. LongAdder for financial audit mid-flight exact sum; wrong stripe count tuning.

#### Interview follow-ups (with model answers)

**Q:** When is AtomicLong still correct over LongAdder?
**A:** When you need atomic read-modify-write, compare-and-set workflows, or an exact value at any instant for business logic. LongAdder sum() is not atomic under concurrent adds — fine for metrics, wrong for account balance. Low contention counters may stay AtomicLong for simplicity. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** How do striped locks work in Guava Striped?
**A:** hash(key) % N selects a lock from an array — reduces probability two unrelated keys share a lock versus one global lock. Too few stripes: residual contention. Too many: memory and cache miss. Power-of-two stripe count for fast masking. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Describe Striped64 internals briefly.
**A:** LongAdder extends Striped64 — base cell plus array of cells created on contention, padded to reduce false sharing. Cells grow lazily; sum collapses all cells. Helps interpret JFR when profiling counter hot spots at high RPS. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Rate limiter uses single AtomicInteger per API key in CHM at 100k rps on one hot partner key.

CAS retry on one counter serializes increments — CPU flame graph shows increment hot. Fix: LongAdder per sliding window, or Redis token bucket for distributed limit. Load test single key before multi-key.

---

### 38. Thread interruption vs cancellation of a task graph.

**Short answer:**
Interrupt is per-thread signal. CompletableFuture `cancel(true)` interrupts running task. Reactive uses subscription dispose. End-to-end cancellation needs HTTP client cancel, SQL timeout, and cooperative checks — not interrupt alone.

#### What it is
Cancellation is a protocol across layers; interrupt is one mechanism.

#### How it works (internals)
Blocking methods throw IE on interrupt. Non-blocking work must poll interrupted flag. Kafka `wakeup()`, Reactor `dispose()`, Servlet async timeout — align semantics.

#### When to use / when NOT to use
Propagate deadline from gateway to DB query timeout. On cancel, close resources in finally. User cancel upload, request timeout, deploy shutdown — close resources in finally.

#### Production example
User cancels upload — server interrupts worker, closes InputStream, deletes partial S3 multipart. CF cancel without closing HTTP client leaves socket open. CF.cancel without closing HttpClient left socket open until fix in finally on interrupt.

#### Common mistakes
Assuming interrupt stops CPU loop. Ignoring IE in Callable. No timeout on get().

#### Interview follow-ups (with model answers)

**Q:** What does Future.cancel(false) versus cancel(true) do?
**A:** cancel(false) prevents run if not started; a running task continues. cancel(true) interrupts a running thread if in an interruptible blocking call. Non-interruptible native code may ignore interrupt until exit. Always pair with timeout on get() and explicit resource close in finally. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** How does StructuredTaskScope help cancellation?
**A:** ShutdownOnTimeout or explicit shutdown cancels forked subtasks — structured lifetime ensures children do not leak after parent deadline. Fits request-scoped parallel fetches with a 2s SLA. Combine with virtual threads for blocking branches. Align JDBC queryTimeout with scope deadline. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** How is gRPC cancellation propagated?
**A:** Client cancel sends cancellation; server onCancel must stop work and release resources. Map to the same trace id in logs. Blocking stub in a thread needs interrupt or deadline-exceeded status check in a loop. Missing onCancel handler is a common leak source. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Mobile client aborts large PDF download; server keeps generating six minutes; Tomcat threads exhausted.

Broken cancellation chain — wire Servlet async timeout to task.cancel(true), JDBC statement cancel, delete temp file in finally. Propagate X-Request-Deadline. Test abort mid-stream asserts DB query cancelled within five seconds.

---

### 39. Why `Collections.synchronizedList` iterators still need external sync.

**Short answer:**
Each list method is synchronized, but iteration is multiple method calls — another thread can modify between calls, causing CME or skewed views. Wrap `synchronized(list) { for (...) }` or use concurrent collection. synchronizedList synchronizes each method — iteration is multiple calls with a gap for concurrent modification. Wrap synchronized(list){ for } or use a concurrent collection or snapshot. synchronizedList synchronizes each method — iteration is multiple calls with a gap for concurrent modification. synchronizedList synchronizes each method — iteration is multiple calls with a gap for concurrent modification. synchronizedList synchronizes each method — iteration is multiple calls with a gap for concurrent modification. synchronizedList synchronizes each method — iteration is multiple calls with a gap for concurrent modification.

#### What it is
Per-method synchronization does not make compound operations atomic.

#### How it works (internals)
Iterator's hasNext/next are separate synchronized entries — gap for concurrent remove. CHM iterators are weakly consistent without CME. Iterator hasNext/next are separate synchronized entries — gap for concurrent remove.

#### When to use / when NOT to use
Prefer concurrent collections for shared iteration. Copy-on-write snapshot if rare writes. Concurrent collections for shared iteration; CopyOnWrite for rare writes frequent reads.

#### Production example
Parallel @Scheduled jobs iterated synchronizedList — intermittent CME. Switched to snapshot `List.copyOf` each tick.

#### Common mistakes
Assuming synchronizedList is fully thread-safe for all uses. foreach remove without iterator remove.

#### Interview follow-ups (with model answers)

**Q:** Vector versus Collections.synchronizedList?
**A:** Both synchronize individual methods — same iteration problem. Vector is legacy and slower. Prefer ArrayList with explicit lock or a concurrent alternative. Neither replaces snapshot or CHM for concurrent iteration. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** When is CopyOnWriteArrayList the right choice?
**A:** Read-heavy, write-rare listener lists — copy backing array on write; iterators see snapshot at creation. Writes are O(n) — fine when listeners update hourly. Wrong for a high-frequency work queue. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Is stream() on a concurrent collection safe?
**A:** Sequential stream on CHM is weakly consistent — OK for read-only reporting if staleness is acceptable. Side effects on shared state remain unsafe. Collect to immutable list first for billing reconciliation requiring point-in-time. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Admin UI iterates synchronizedList of active sessions while SessionManager adds/removes on each login.

Iteration without external sync while manager mutates — CME or skewed view. Fix: List.copyOf under short lock, or ConcurrentHashMap.newKeySet with snapshot per request. Never expose internal list to JSP for direct iteration.

---

### 40. Immutability as a concurrency strategy.

**Short answer:**
Immutable data shared after safe publication needs no locks for readers. Copy-on-write config snapshots, record messages, and single-writer threads eliminate most shared mutable state. Immutability moves complexity to construction and publication.

#### What it is
Immutability moves complexity to construction and publication, simplifying concurrent access. Primary concurrency strategy in event-driven Java services.

#### How it works (internals)
Replace mutable shared Order with new immutable Order on each change (or persistent data structure). Config reload: atomic reference to immutable Config snapshot. AtomicReference swap to new immutable Config on refresh.

#### When to use / when NOT to use
Default to immutable messages between threads. One writer thread per aggregate is valid DDD pattern. Immutable Kafka messages; one writer thread per aggregate is valid DDD.

#### Production example
Event sourcing: events are immutable records — handlers process without locks on event data. Config AtomicReference<ImmutableConfig> swap on refresh. Event sourcing: immutable event records — handlers process without locks on event data.

#### Common mistakes
Immutable object with mutable List field exposed. 'Immutable' entity with JPA setters. Copy-on-write on huge graph every read. Immutable object with exposed mutable List; JPA entity called immutable with setters.

#### Interview follow-ups (with model answers)

**Q:** What persistent collections exist for Java?
**A:** Guava Immutable collections for snapshots; Vavr or Eclipse Collections for structural sharing on large trees. Most Spring services use AtomicReference<ImmutableMap> — measure before adopting persistent structures. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** How do records help message bus design?
**A:** Compact immutable carriers with equals/hashCode — ideal Kafka payload after deserialization. Pair with schema registry for evolution. Validation in compact constructor. Do not put mutable HttpServletRequest in a record. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Explain read-copy-update in Java terms.
**A:** Readers read current immutable snapshot reference without lock. Writer builds new snapshot, atomic swap — readers see old or new, never torn. Write frequency must be low; high write rate makes copies expensive. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Team marks Order @Immutable Lombok but passes managed entity to @Async notification.

Persistence context mutates fields; async thread sees stale or mid-flush state. Map to immutable OrderView record before async handoff. ArchUnit: @Async methods only accept records or primitives.

---

### 41. Actor model vs shared-memory threads.

**Short answer:**
Actors (Akka): no shared mutable state, mailbox, message passing, supervision. Shared-memory: faster local access, harder reasoning. Kafka partition consumer resembles actor — single thread per partition, ordered mailbox. Actors isolate state behind a mailbox — no shared mutable fields; Kafka partition consumer is actor-like.

#### What it is
Concurrency models trade performance vs understandability. Concurrency model choice: message passing versus locks on shared structures.

#### How it works (internals)
Actor mailbox overflow if consumer slow — backpressure needed. Shared memory needs locks/CHM. Virtual thread + queue is middle ground.

#### When to use / when NOT to use
Actors for complex state machines with isolation. Shared memory for high-performance in-process caches with clear locking. Actors for complex state machines; CHM for read-heavy pricing cache with clear locking.

#### Production example
Payment orchestration in Akka — each payment id is actor, no cross-actor mutable state. In-process pricing cache uses CHM with compute.

#### Common mistakes
Actor for everything overhead. Shared mutable state in actor between messages without protocol. Ignoring mailbox bounds.

#### Interview follow-ups (with model answers)

**Q:** Akka versus virtual threads for new greenfield service?
**A:** Virtual threads simplify blocking Spring on one JVM. Akka when you need cluster sharding, supervision, and location transparency. Many teams use Kafka as distributed mailbox instead of Akka remoting. Hybrid: Spring plus Kafka partition ordering gives actor semantics without cluster ops. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Reactive streams versus actor model?
**A:** Reactive: declarative pipeline with backpressure in the protocol. Actors: opaque state plus behavior with per-actor ordering. Spring WebFlux without discipline blocking on JDBC fails — actors do not fix blocking either. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** How is Kafka partition like an actor?
**A:** Single consumer thread processes partition messages sequentially — mailbox ordering per key if keyed. Rebalance is actor migration — cooperative sticky assignor minimizes churn. Poison message needs DLQ like actor supervision strategy. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Architect proposes Akka for entire order service; team runs Spring Boot monolith; p99 target 50ms.

Full Akka rewrite is high risk — Kafka plus partition-key orderId plus single-thread consumer achieves isolation. Use actor only for dispute workflow. Shared catalog stays CHM. Virtual threads for HTTP if blocking. Pilot one bounded context.

---

### 42. Parallel streams: when they are wrong in a Spring service.

**Short answer:**
parallelStream uses commonPool — blocks other requests, bad for blocking I/O, high setup cost on small lists, swallows exceptions in wrapped RuntimeException. Use dedicated FJP or sequential loop unless CPU-bound and measured. parallelStream uses commonPool — blocks other requests, bad for I/O, high setup cost on small lists. Almost never in Tomcat request thread; dedicated FJP for measured CPU batch off critical path. parallelStream uses commonPool — blocks other requests, bad for I/O, high setup cost on small lists. parallelStream uses commonPool — blocks other requests, bad for I/O, high setup cost on small lists. parallelStream uses commonPool — blocks other requests, bad for I/O, high setup cost on small lists. parallelStream uses commonPool — blocks other requests, bad for I/O, high setup cost on small lists.

#### What it is
Parallel streams are not free parallelism for typical web service request handling. Parallel streams are fork-join sugar — not general server parallelism.

#### How it works (internals)
Spliterator splits collection; combiner merges — must be associative. Small N: overhead dominates. Blocking in mapper stalls common pool workers.

#### When to use / when NOT to use
CPU-bound batch job off request path: maybe parallel with custom pool. Request handler: almost never. CPU-bound transform on large in-memory collection in batch job after profiling.

#### Production example
Removed parallelStream from REST enrichment calling HTTP — p99 dropped 200ms. Batch report uses dedicated executor instead. Removed parallelStream REST enrichment calling HTTP — p99 dropped 200ms.

#### Common mistakes
parallelStream in Tomcat request. Side effects in forEach on shared list. Assuming parallel always uses all cores efficiently.

#### Interview follow-ups (with model answers)

**Q:** How do you use custom ForkJoinPool with parallel stream?
**A:** Submit to custom pool: ForkJoinPool customPool = new ForkJoinPool(8); customPool.submit(() -> list.parallelStream()...).get(); always shutdown in finally. Still avoid blocking I/O inside mapper. Document benchmark numbers justifying parallelism. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** What Spliterator characteristics matter?
**A:** ORDERED, SIZED, SUBSIZED, CONCURRENT affect split strategy. ArrayList spliterator efficient; linked structures split poorly. CONCURRENT source allows parallel only if side-effect free — wrong IMMUTABLE assumption causes races. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Stream API versus reactive for service composition?
**A:** Stream is pull synchronous — one thread unless parallelStream. Reactive for async non-blocking with backpressure. Spring MVC blocking service should use CompletableFuture or virtual threads with explicit executor, not parallelStream on request path. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Junior adds orders.parallelStream().forEach(this::sendKafka) in @Scheduled export.

commonPool threads block on send; unrelated APIs slow. Fix sequential batch or KafkaTemplate async API on dedicated executor. Ban parallelStream in service package via Sonar.

---

### 43. `Thread.yield`, `sleep(0)`, and spinning.

**Short answer:**
`Thread.yield()` hints scheduler — no guarantee. `sleep(0)` may yield to another thread. `Thread.onSpinWait()` hints CPU for short spins. Wrong spinning burns CPU especially in cgroup CPU limits.

#### What it is
Thread scheduling hints are subtle and platform-dependent. Scheduling hints are not synchronization primitives.

#### How it works (internals)
Spin-wait only when hold time is nanoseconds and contention is rare. Long spin in container with 0.5 CPU quota wastes quota. LockSupport.parkNanos with exponential backoff caps spin.

#### When to use / when NOT to use
Prefer lock park/unpark, BlockingQueue, or backoff. onSpinWait in tight lock-free retry with cap. Spin only when hold time is nanoseconds and contention rare.

#### Production example
Lock-free retry with exponential backoff + onSpinWait capped — balances latency and CPU. Lock-free retry with capped onSpinWait then parkNanos — balanced latency and CPU.

#### Common mistakes
yield in correctness protocol. Infinite spin on CAS. sleep(0) for 'mutex'. yield in correctness protocol; infinite spin on CAS; sleep(0) as mutex. yield in correctness protocol; infinite spin on CAS; sleep(0) as mutex. yield in correctness protocol; infinite spin on CAS; sleep(0) as mutex. yield in correctness protocol; infinite spin on CAS; sleep(0) as mutex. yield in correctness protocol; infinite spin on CAS; sleep(0) as mutex.

#### Interview follow-ups (with model answers)

**Q:** When should you use LockSupport.parkNanos?
**A:** After failed tryAcquire in custom lock — park releases CPU until unpark or timeout. Prefer over Thread.sleep for lock implementations. Virtual threads: favor block over spin sooner than on platform threads. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Busy-wait versus block for low-latency queue?
**A:** Busy-wait wins only at nanosecond latency with dedicated cores — rare in Spring services. Blocking with park saves cloud CPU billing. Profile under production cgroup limits not dev laptop. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** ScheduledExecutorService versus Thread.sleep in retry?
**A:** ScheduledExecutor avoids blocking pool thread sleeping — schedules retry callback. Resilience4j retry uses scheduler. For tests use Awaitility not sleep hoping for race. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Custom rate limiter spins while(!tryAcquire()) on 0.5 CPU K8s limit.

Spin burns throttled quota — latency worse than blocking. Fix parkNanos backoff or Semaphore.acquire with timeout. JFR shows hot spin method.

---

### 44. Class initialization lock.

**Short answer:**
JVM holds lock per class during `<clinit>` — thread-safe static init. Holder idiom relies on this. Static init cycles can deadlock. Avoid heavy I/O in static blocks.

#### What it is
Class initialization is JVM-synchronized once per class loader.

#### How it works (internals)
First active use triggers clinit. Deadlock: class A static refs B, B static refs A during init. Failures in clinit become ExceptionInInitializerError.

#### When to use / when NOT to use
Keep static init minimal. Lazy holder for singletons. Don't call external services in clinit.

#### Production example
Deadlock in test: two classes static-init circular dependency — refactor to break cycle. Test deadlock: ClassA static refs B while B static refs A — refactor to break cycle.

#### Common mistakes
Network call in static block slowing first request. Class init failure opaque in prod. Network call in static block on first request; opaque clinit failure in prod.

#### Interview follow-ups (with model answers)

**Q:** Is holder idiom still safe on modern JDK?
**A:** Yes — inner static class loads lazily on getInstance; JVM class init lock ensures thread-safe single init. Preferred over DCL complexity. Enum singleton also clinit-safe and serialization-safe. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** When exactly does class initialization run?
**A:** Before first active use: new instance, static field access, reflection. Not when merely referencing compile-time constant if inlined. Interface default methods trigger interface init. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Static init versus Spring @PostConstruct?
**A:** Spring manages bean lifecycle after context up — @PostConstruct after injection. Static init on first class touch may run before Spring context — avoid coupling Spring to static blocks. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

PaymentGatewayClient static block reads AWS Secrets Manager on class load; first request after deploy takes 45s.

Clinit blocks thread loading class — all requests needing client stall together. Fix lazy Spring bean @PostConstruct; readiness probe should call endpoint using client.

---

### 45. Daemon threads.

**Short answer:**
Daemon threads don't prevent JVM exit when only daemons remain. Don't run critical work as daemon without shutdown hooks. Spring-managed executors should be non-daemon with graceful shutdown on context stop. Daemon threads do not keep JVM alive — wrong for work that must complete on shutdown.

#### What it is
Daemon flag affects JVM lifecycle, not priority or scheduling.

#### How it works (internals)
Background housekeeping as daemon OK if acceptable to stop abruptly on exit. Payment processing — non-daemon with drain on shutdown. setDaemon(true) on thread or ThreadFactory — Boot graceful shutdown awaits non-daemon pools. setDaemon(true) on thread or ThreadFactory — Boot graceful shutdown awaits non-daemon pools. setDaemon(true) on thread or ThreadFactory — Boot graceful shutdown awaits non-daemon pools. setDaemon(true) on thread or ThreadFactory — Boot graceful shutdown awaits non-daemon pools. setDaemon(true) on thread or ThreadFactory — Boot graceful shutdown awaits non-daemon pools.

#### When to use / when NOT to use
Configure executor threads non-daemon in Spring `@Bean(destroyMethod=shutdown)`. Register shutdown hook for flush. Configure executor beans with awaitTermination; K8s preStop for drain.

#### Production example
Daemon executor dropped in-flight Kafka acks on SIGTERM — changed to graceful shutdown with timeout.

#### Common mistakes
setDaemon(true) to 'fix' hung shutdown. Daemon for request processing. No awaitTermination on shutdown.

#### Interview follow-ups (with model answers)

**Q:** How does Spring Boot graceful shutdown work?
**A:** server.shutdown=graceful stops accepting new requests, waits in-flight, stops context. spring.lifecycle.timeout-per-shutdown-phase configures wait. TaskExecutor beans need shutdown and awaitTermination. K8s terminationGracePeriodSeconds must exceed drain budget. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** SIGTERM handling in Kubernetes?
**A:** Kube sends SIGTERM, removes endpoint, waits grace, SIGKILL. preStop sleep gives LB time to drain. App must finish in-flight within grace. Daemon threads may die mid-work if JVM exits early. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Daemon versus user thread on JVM exit?
**A:** When all user threads end, JVM exits even if daemons remain — daemons terminated abruptly. addShutdownHook for flush metrics buffer. Do not rely on daemon for financial commit completion. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Dev sets executor.setDaemon(true) for fast IDE stop; ships to prod; SIGTERM during deploy loses audit events.

Daemon threads terminate without drain. Fix non-daemon pool, graceful shutdown, Kafka producer flush in shutdown hook. Profile separates dev quick-stop from prod drain.

---

### 46. How does Spring `@Async` actually run?

**Short answer:**
`@Async` proxy submits method to `TaskExecutor` — return type can be void, Future, or CompletableFuture. Self-invocation bypasses proxy. Exceptions on void methods go to `AsyncUncaughtExceptionHandler`. Must configure executor — default may spawn unbounded threads.

#### What it is
Spring async is AOP around TaskExecutor submission, not magic threading. Spring async is executor delegation with proxy semantics.

#### How it works (internals)
Enable `@EnableAsync`. Specify `@Async("beanName")` on executor. Caller thread returns immediately; work runs on pool thread. Transaction and security context don't propagate unless TaskDecorator configured.

#### When to use / when NOT to use
Use for fire-and-forget side effects with explicit executor and error handler. Not for parallel same-request joins without CF return. Fire-and-forget side effects with explicit error handler — not parallel same-request without CF return.

#### Production example
Email send @Async on `mailExecutor` — MDC copied via TaskDecorator. Self-call async didn't run — fixed with self-injection. Email @Async on mailExecutor with MDC TaskDecorator; self-call async didn't run until self-injection.

#### Common mistakes
Default SimpleAsyncTaskExecutor unbounded threads. @Async on private method. Expecting @Transactional on async method same TX. Default unbounded executor; @Async on private method; @Transactional expecting same TX on async.

#### Interview follow-ups (with model answers)

**Q:** How do you configure TaskDecorator for MDC propagation?
**A:** TaskDecorator copies MDC map and SecurityContext to worker in decorate(Runnable), clears in finally. Register on ThreadPoolTaskExecutor. Micrometer ContextSnapshot offers unified propagation. Test async integration log contains traceId. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** @Async versus @Scheduled for background work?
**A:** @Scheduled for periodic cron — overlap on multiple pods unless ShedLock. @Async for event-triggered fire-and-forget. Kafka scheduled jobs preferred for distributed cron at scale. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Virtual threads with @Async?
**A:** Configure VirtualThreadTaskExecutor in Spring 6.1+ for blocking async side effects. Still bound downstream resources. MDC propagation same requirement. Load test async path separately from HTTP. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

NotificationService @Async called from same class saveOrder() without proxy.

Self-invocation bypasses proxy — @Async ignored. Fix inject self interface, separate bean, or ApplicationEventPublisher after commit. Register AsyncUncaughtExceptionHandler.

---

### 47. Context propagation (MDC, SecurityContext, request id).

**Short answer:**
Thread pools don't copy ThreadLocal — MDC trace id and SecurityContext vanish in @Async and reactive threads unless TaskDecorator, Micrometer ContextSnapshot, Reactor Context, or TransmittableThreadLocal propagate them. Thread pools do not copy ThreadLocal — MDC and SecurityContext lost in @Async without propagation. Standardize TaskDecorator, Micrometer ContextSnapshot, or Reactor Context.

#### What it is
Request context is thread-local by default; async breaks the chain. Request context is thread-bound; async breaks the chain unless bridged.

#### How it works (internals)
Filter sets MDC; worker thread must inherit or explicitly copy. Spring Security ContextHolder is ThreadLocal. Reactor hooks for reactive stack.

#### When to use / when NOT to use
Standardize TaskDecorator on all executors. Test async path logs contain traceId. Every executor bean gets decorator; test async logs for correlation id.

#### Production example
Production bug: @Async logs missing correlation id — TaskDecorator added to async executor bean. @Async logs missing traceId — TaskDecorator on asyncExecutor fixed. @Async logs missing traceId — TaskDecorator on asyncExecutor fixed. @Async logs missing traceId — TaskDecorator on asyncExecutor fixed. @Async logs missing traceId — TaskDecorator on asyncExecutor fixed. @Async logs missing traceId — TaskDecorator on asyncExecutor fixed.

#### Common mistakes
Assuming InheritableThreadLocal works with pools. Forgetting clear MDC in finally on worker. Reactive without contextRestore.

#### Interview follow-ups (with model answers)

**Q:** How does Micrometer context propagation work?
**A:** ContextRegistry wraps Runnable to capture and restore ThreadLocalSnapshot across boundaries. Integrates MDC, Observation, Tracing when configured. Spring Boot 3 observability auto-config helps. Verify Kafka listener and @Async paths in integration test. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** OpenTelemetry baggage versus MDC?
**A:** Baggage propagates across service boundaries in trace headers. MDC is logging-local unless copied to baggage. Align keys so logs and traces join in Grafana. Do not put PII in baggage. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Context propagation with virtual threads?
**A:** Carrier thread reuse means MDC leak if not cleared in finally — same as platform pools. Test virtual thread executor same as classic pool. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Support cannot correlate payment failure logs across microservices; @Async fraud check lacks X-Request-Id.

Broken chain at async boundary. Fix TaskDecorator plus Feign interceptor reading Observation. Kafka consumer interceptor restores MDC. E2E WebTestClient asserts async log appender contains request id.

---

### 48. Lock fairness vs barging.

**Short answer:**
Unfair locks allow barging — incoming thread may acquire before queued waiters, higher throughput. Fair locks enforce queue order — reduces starvation, worse throughput and latency tail for lucky threads. Unfair ReentrantLock allows barging — higher throughput; fair lock reduces starvation, hurts throughput. synchronized is unfair; enable fair only when measured starvation.

#### What it is
Fairness is a ReentrantLock configuration trade-off, not a moral choice. Fairness is ReentrantLock configuration trade-off.

#### How it works (internals)
Default ReentrantLock is unfair. `new ReentrantLock(true)` fair. synchronized is unfair. Starvation rare except low-priority threads or extreme contention.

#### When to use / when NOT to use
Don't enable fair unless measured starvation. Prefer separate pools over fair global lock. Don't enable fair unless profiled starvation; dedicate pools over fair global lock.

#### Production example
Fair lock enabled globally — throughput dropped 15%; reverted, fixed starvation by dedicating admin pool. fair=true globally dropped throughput 15%; fixed starvation by dedicated admin pool. fair=true globally dropped throughput 15%; fixed starvation by dedicated admin pool. fair=true globally dropped throughput 15%; fixed starvation by dedicated admin pool. fair=true globally dropped throughput 15%; fixed starvation by dedicated admin pool. fair=true globally dropped throughput 15%; fixed starvation by dedicated admin pool.

#### Common mistakes
fair=true everywhere. Expecting synchronized fair. Ignoring barging as 'bug'.

#### Interview follow-ups (with model answers)

**Q:** When does thread starvation actually happen?
**A:** Rare with default locks — extreme contention where low-priority thread never wins queue. More common: pool exhaustion leaving tasks queued forever. Fix pool sizing before fair lock. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** ReadWriteLock fairness implications?
**A:** Fair RW lock prevents writer starvation but increases reader delay. StampedLock has no fairness. Often copy-on-write eliminates RW lock need. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Priority queue versus fair lock?
**A:** PriorityBlockingQueue schedules task priority — different from mutex fairness. Kafka partition ordering is per-key fairness for events. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Ops enables fair ReentrantLock on global config lock; p99 rises 40% for all services sharing config refresh.

Fair lock serializes readers and writers strictly. Fix revert unfair, AtomicReference<ImmutableConfig> for reads without lock. Config read should not take mutex at all.

---

### 49. `synchronized` method vs block — monitor identity.

**Short answer:**
Instance synchronized method uses `this`; static synchronized uses Class object. Synchronized block chooses monitor explicitly. Mixing monitors across classes in different orders causes deadlock. Instance synchronized method locks this; static locks Class object.

#### What it is
Monitor identity defines which lock object threads compete for. Monitor identity defines contention domain.

#### How it works (internals)
Two classes synchronizing on each other's Class literals in opposite order — deadlock. Block scope minimizes hold time. Mixing monitors across classes in opposite orders causes deadlock.

#### When to use / when NOT to use
Use private final lock in blocks. Document public synchronized methods as part of API contract. Private final lock in blocks; document public synchronized methods.

#### Production example
Library A syncs on A.class then B.class; library B reverses — rare integration deadlock. Library A syncs A.class then B.class; partner library reverses — integration deadlock.

#### Common mistakes
synchronized on mutable object field as lock. Public this sync enabling client deadlock. synchronized on mutable field reference; public this sync enabling client deadlock. synchronized on mutable field reference; public this sync enabling client deadlock. synchronized on mutable field reference; public this sync enabling client deadlock. synchronized on mutable field reference; public this sync enabling client deadlock. synchronized on mutable field reference; public this sync enabling client deadlock.

#### Interview follow-ups (with model answers)

**Q:** Static versus instance synchronized method?
**A:** Static sync on Class object of declaring class — one lock per class per classloader. Instance sync on instance — per object. Subclass inherits synchronized methods with same monitor rules. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Is Class object unique across classloaders?
**A:** No — two classloaders loading same name get different Class objects and different locks. Plugin architectures need explicit named lock objects for coordination. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** ReentrantLock versus class lock for static state?
**A:** private static final ReentrantLock clearer than synchronized static — tryLock timeout possible. Prefer static lock field over class literal if multiple static resources. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Vendor JAR syncs on Payment.class; your code syncs Payment.class then Order.class in opposite order with vendor Order then Payment.

Cross-library class lock ordering inversion. Fix private final locks; serialize vendor access through single-thread executor with timeout. Full classpath deadlock harness in integration env.

---

### 50. Senior concurrency design checklist.

**Short answer:**
Prefer isolation over shared mutation; bound queues and pools; timeouts and cancellation everywhere; no I/O under locks; document invariants per mutex; immutable messages; measure contention (JFR); prove HB for published fields; named threads + MDC; graceful shutdown drain then interrupt. Senior checklist: isolation over shared mutation, bound queues and pools, timeouts and cancellation everywhere. No I/O under locks; immutable messages; JFR contention; named threads plus MDC; graceful shutdown drain.

#### What it is
A senior checklist turns concurrency from ad hoc synchronized blocks into engineered systems. Engineering discipline turning ad hoc synchronized into reviewable concurrent systems.

#### How it works (internals)
Kafka rebalance + thread dump + CHM compute on whiteboard demonstrates operational depth. Checklist catches 80% of production incidents before ship. Whiteboard Kafka rebalance plus thread dump plus CHM compute demonstrates staff depth.

#### When to use / when NOT to use
Use in design reviews and incident postmortems. Teach juniors the checklist with real stories. New service template, arch review gate, incident RCA actions.

#### Production example
Team template for new service: executor beans with bounds, TaskDecorator, shutdown hook, jcstress for custom lock-free queue — passes arch review. Team template: bounded executors, TaskDecorator, shutdown hook, jcstress for custom queue — passes arch review.

#### Common mistakes
Skipping checklist 'for MVP.' Unbounded anywhere. No shutdown story. Locks without documented invariant.

#### Interview follow-ups (with model answers)

**Q:** Bulkhead versus timeout — when each?
**A:** Timeout limits wait for one call. Bulkhead limits concurrent calls — prevents one dependency consuming all threads. Use together: bulkhead 20 concurrent, each call 2s timeout. Without bulkhead, hundred timeouts still tie hundred threads until timeout fires. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** How does Little's law apply to thread pools?
**A:** L = lambda W: average requests in system equals arrival rate times residence time. Pool queue grows linearly with slow tasks even at moderate arrival rate. Bounded queue makes L visible; unbounded hides until OOM. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** What changes on concurrency checklist with virtual threads?
**A:** Less platform pool sizing angst for I/O; add pin rate monitoring, still bound JDBC and semaphores. MDC propagation unchanged. Do not remove cancellation, immutability, or idempotency items. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

#### Scenario probe

Staff interview: whiteboard payment ingestion — Kafka, Spring, Oracle, 5k tps.

Walk checklist: partition by paymentId; manual ack after idempotent write; bounded fraud HTTP executor; virtual threads after pin test; MDC from consumer interceptor; graceful shutdown; no parallelStream; LongAdder metrics; immutable PaymentEvent record. Backpressure pause consumer when downstream queue full.

---

### 51. `ScopedValue` (Java 21) vs `ThreadLocal` — structured context propagation.

**Short answer:** `ScopedValue` binds immutable context for a lexical scope and propagates automatically to child threads and structured concurrency tasks without per-thread map overhead. `ThreadLocal` is mutable, heap-heavy, and leaks in pools unless removed in `finally`. Prefer `ScopedValue` for request/trace/user context in virtual-thread-heavy services; keep `ThreadLocal` only for legacy libraries or thread-pool task decorators that cannot migrate yet.

#### What it is
Both carry per-execution context (trace ID, tenant, security principal) across call stacks. `ThreadLocal` stores values in a thread-local map keyed by the `ThreadLocal` instance. `ScopedValue` (JEP 446, finalized in Java 21+) binds values to a dynamic scope: `ScopedValue.where(KEY, value).run(() -> { ... })`.

#### How it works (internals)
`ScopedValue` is immutable for the bound scope; reads are fast and the JVM can optimize away map lookups. StructuredTaskScope and virtual threads inherit bound scoped values when tasks are forked. `ThreadLocal.set()` mutates a `ThreadLocalMap` on each carrier or platform thread — forgotten `remove()` causes wrong tenant data on the next pooled task and retains references across requests.

#### When to use / when NOT to use
Use `ScopedValue` for new code with structured concurrency, virtual threads, and immutable context snapshots. Do not use `ScopedValue` for mutable counters or caches — it is read-only per binding. Keep `ThreadLocal` when integrating with older frameworks that expect `ThreadLocal` MDC bridges until they add scoped-value support.

#### Production example
Payment API on Java 21: replace Logback MDC `ThreadLocal` with `ScopedValue<RequestContext>` at servlet filter entry; fraud scoring fork uses `StructuredTaskScope` and reads the same tenantId without explicit copy. Load test shows fewer GC pauses and zero cross-tenant leakage after removing forgotten `MDC.clear()` in async paths.

#### Common mistakes
Treating `ScopedValue` like a mutable map — rebinding requires a new `where` scope. Migrating only half the stack so async code still uses `ThreadLocal`. Assuming virtual threads fix `ThreadLocal` leaks — carriers still need cleanup on platform thread pools.

#### Interview follow-ups (with model answers)

**Q:** Can you set a `ScopedValue` mid-request like `ThreadLocal.set()`?
**A:** No — you bind once per scope with `ScopedValue.where` and run/call a Runnable/Callable. Updates require nesting a new binding. That immutability is the safety feature: downstream code cannot silently swap tenant context. For layered frameworks, compose bindings: outer request ID, inner span ID via nested `where` calls. This matches how structured concurrency expects inherited context without mutation races.

**Q:** How does Micrometer/tracing integrate with `ScopedValue`?
**A:** Modern observation APIs propagate context through `ContextSnapshot` or scoped carriers; Spring Boot 3.2+ observation registry can bridge to MDC for logging while using scoped propagation internally. In migration, use a `TaskDecorator` on platform pools and scoped binding at HTTP entry for virtual-thread executors. Verify with integration test: fork task, assert same traceId in logs without manual copy.

#### Scenario probe

A multi-tenant SaaS on Tomcat platform threads switched to virtual threads but kept Logback MDC via `ThreadLocal`. After deploy, 0.3% of requests log under the wrong `tenantId`.

**Model answer:** Root cause is async fraud call on a platform pool without `MDC.setContextMap` copy and missing clear on return — amplified under higher concurrency with virtual threads mounting on fewer carriers. Fix: bind `ScopedValue<TenantContext>` at filter boundary; ensure all executors use structured tasks or explicit context snapshot; add assertion test that fires 10k parallel requests and validates log tenant matches JWT. Remove `ThreadLocal` from hot path once tracing vendor supports scoped propagation.

#### Code / config (when useful)

```java
private static final ScopedValue<String> TRACE = ScopedValue.newInstance();

void handle(Request req) {
    ScopedValue.where(TRACE, req.traceId()).run(() -> {
        repository.save(order); // downstream reads TRACE.get()
    });
}
```

---

### 52. `LockSupport.park`/`unpark` vs `wait`/`notify` — when used internally.

**Short answer:** `LockSupport` parks/unparks threads without requiring a monitor lock — it is the primitive beneath `AbstractQueuedSynchronizer`, `ForkJoinPool`, and many lock implementations. `wait`/`notify` require holding the object's monitor and tie waiting to intrinsic locking. You rarely call `park` in application code, but seniors must read thread dumps showing `park`/`Unsafe.park` and know unpark permits can be consumed before park arrives.

#### What it is
`LockSupport.park()` blocks the current thread until unpark or interrupt; `unpark(thread)` grants a permit. `Object.wait()` releases the monitor and waits on the object's wait set; `notify()` wakes one waiter. Both are low-level blocking primitives with different coupling to monitors.

#### How it works (internals)
AQS `acquire` loops use `LockSupport.park` when CAS fails. `unpark` is not cumulative beyond one permit — spurious wakeups are handled by re-checking condition in a loop. `wait`/`notify` must run inside `synchronized(obj)` or throw `IllegalMonitorStateException`. Thread dumps show `java.util.concurrent.locks.LockSupport.park` for JUC locks vs `Object.wait` for intrinsic waits.

#### When to use / when NOT to use
Application code: prefer `Condition`, `Semaphore`, `BlockingQueue`, or `Phaser` — not raw `park`. Use `wait`/`notify` only in legacy code or teaching; production uses `java.util.concurrent`. Read `LockSupport` when debugging custom synchronizers or third-party libraries built on AQS.

#### Production example
On-call thread dump during Kafka consumer pause: hundreds of threads in `LockSupport.park` on `AbstractQueuedSynchronizer$ConditionObject` — normal backpressure on a bounded queue, not deadlock. Misread as deadlock because stack lacks `BLOCKED` on monitors. Contrast with `wait` on `Object` in old JDBC pool — indicates legacy pool implementation.

#### Common mistakes
Calling `unpark` before `park` and assuming multiple permits stack — only one pending permit. Using `park` without checking interrupt status and loop condition. Replacing `wait`/`notify` with `park` manually instead of higher-level abstractions.

#### Interview follow-ups (with model answers)

**Q:** Why does AQS use `LockSupport` instead of `wait`/`notify`?
**A:** AQS manages its own CLH queue of wait nodes independent of any single object's monitor. `LockSupport` decouples parking from intrinsic locks, enabling shared/exclusive modes, timeouts (`parkNanos`), and fair ordering. `wait` would require every lock user to synchronize on one object, defeating flexible lock designs. This is why `ReentrantLock` conditions use `Condition.await()` built on the same AQS machinery.

**Q:** What does `Unsafe.park` in a dump mean?
**A:** HotSpot maps `LockSupport.park` to JVM internal `Unsafe.park` — normal for blocked JUC threads. Check the parker's target: `AbstractQueuedSynchronizer`, `ForkJoinPool`, `CompletableFuture`, or Netty event loop. If RUNNABLE threads are zero and business is stalled, look for missing unpark/signal — often a bug in custom lock or forgotten `countDown`.

#### Scenario probe

Custom rate limiter uses `synchronized` + `wait`/`notify`. Under load, threads miss notifications and stall until timeout.

**Model answer:** Classic missed signal: notify before wait without holding correct monitor ordering, or notify one while multiple waiters needed. Replace with `ReentrantLock` + `Condition` or `Semaphore`/`RateLimiter` (Guava/resilience4j). If keeping custom code, use `while (!condition) condition.await()` inside lock. Thread dump would show `Object.wait` on limiter monitor — migrate to JUC for timeout and fairness support.

---

### 53. `Exchanger` and `Phaser` advanced use cases.

**Short answer:** `Exchanger` synchronizes a pair of threads at a rendezvous point, swapping produced buffers — ideal for dual-thread pipeline handoff. `Phaser` is a reusable dynamic barrier: parties register/deregister at runtime, supports tiered phases and `onAdvance` termination. Use `Exchanger` for single-producer/single-consumer buffer swap; use `Phaser` for staged parallel pipelines (ETL phases, simulation ticks) where participant count varies per phase.

#### What it is
`Exchanger<V>` blocks until another thread exchanges values at the same sync point. `Phaser` replaces fixed `CyclicBarrier` party counts with dynamic registration, phase numbers, and optional `onAdvance` hook to short-circuit further phases.

#### How it works (internals)
`Exchanger` uses `Arena` slots with spin then park — only two threads pair per exchange; others wait for next slot. `Phaser.arriveAndAwaitAdvance()` increments arrived count; when parties reach registered count for current phase, phase advances and waiting threads release. `register()`/`bulkRegister()` adjust next phase requirements; `arriveAndDeregister()` removes a party without blocking.

#### When to use / when NOT to use
`Exchanger`: exactly two threads, equal-rate handoff (compression thread ↔ IO thread). Not for N-way barriers or many producers. `Phaser`: multi-stage fork/join with variable workers (map-reduce stages, game server tick). Not when a simple `CountDownLatch` or `CompletableFuture.allOf` suffices — less code, same outcome.

#### Production example
Log ingestion: parser thread fills byte[] buffer, writer thread flushes to disk — `Exchanger` swaps empty/full buffers without shared queue allocation. ETL job: phase 1 extract (8 threads), phase 2 transform (4 threads), phase 3 load (2 threads) — one `Phaser` with per-stage `onAdvance` shrinking registered parties and logging phase metrics.

#### Common mistakes
Using `Exchanger` with thread pool >2 threads — extra threads block indefinitely without partner. Forgetting `Phaser` party count after worker failure — phase never advances; use `forceTermination` or register deregister on failure. Choosing `CyclicBarrier` when workers join/leave between batches.

#### Interview follow-ups (with model answers)

**Q:** `Phaser` vs `CyclicBarrier` — when is dynamic registration worth it?
**A:** When worker count changes between iterations — e.g., Kafka partition assignment changes consumers mid-job, or fork-join tasks spawn uneven subtasks per phase. `CyclicBarrier` requires fixed parties at construction; mismatch causes permanent hang. `Phaser` lets failed worker `arriveAndDeregister` so phase can complete with reduced count if business allows partial results.

**Q:** Exchanger and false sharing / allocation?
**A:** Exchange passes reference to pre-allocated buffer — zero-copy handoff if buffers reused. Avoid exchanging small objects per record — synchronization cost dominates. Pair with thread affinity (two dedicated threads) for NIC capture pipelines. Measure: if exchange time > work time, batch more data per swap.

#### Scenario probe

Batch analytics job uses `CyclicBarrier(8)` but Spark-style stages sometimes run 6 executors after node loss — job hangs at barrier.

**Model answer:** Replace with `Phaser`: register parties equal to live executors each stage; on worker loss, deregister failed party or use `onAdvance` to abort phase and retry slice on remaining nodes. Add timeout on `awaitAdvance` (via `getPhase()` polling + deadline) and alert when phase duration exceeds SLO. Document that partial stage completion may require idempotent sink writes.

---

### 54. `DelayQueue` and scheduled task systems.

**Short answer:** `DelayQueue` is an unbounded `BlockingQueue` of `Delayed` elements ordered by remaining delay — used internally by `ScheduledThreadPoolExecutor`. Production schedulers add persistence, misfire policies, and distributed leadership; in-JVM `DelayQueue` alone loses tasks on crash. Use it for in-memory retry backoff and rate-limited work queues; use Quartz/Spring `@Scheduled` + DB or Kafka delayed topics for durable schedules.

#### What it is
Elements implement `Delayed` with `getDelay(TimeUnit)` and `compareTo` consistent with delay ordering. `take()` blocks until head element's delay expires. `ScheduledThreadPoolExecutor` uses `DelayedWorkQueue` (subclass of `DelayQueue`).

#### How it works (internals)
`DelayQueue` uses `PriorityQueue` ordered by delay; `take()` parks on `Condition` until earliest element eligible. `offer` is O(log n); no capacity bound — memory risk if producers outpace consumers. Clock uses `System.nanoTime()` for monotonic delay, not wall clock — immune to DST jumps but not to long GC pauses delaying firing.

#### When to use / when NOT to use
In-memory delayed retries, circuit-breaker half-open probes, token bucket refill scheduling inside one JVM. Not for cross-node cron, legal audit schedules, or tasks that must survive restart — persist schedule externally. Combine with bounded executor so expired tasks do not unboundedly accumulate.

#### Production example
Order service: failed webhook retries enqueued as `DelayedTask` with exponential backoff in `DelayQueue`; worker pool drains to HTTP client with bulkhead. On deploy, queue loss accepted for non-critical notifications; payment retry uses DB `next_retry_at` polled by ShedLock leader instead.

#### Common mistakes
Unbounded `DelayQueue` during outage — millions of delayed retries OOM heap. Using wall-clock `System.currentTimeMillis()` in custom `Delayed` while queue assumes nano semantics inconsistently. Single-thread scheduled executor for CPU-heavy jobs — blocks all other schedules.

#### Interview follow-ups (with model answers)

**Q:** How does Spring `@Scheduled` differ from raw `DelayQueue`?
**A:** Spring scheduling uses `TaskScheduler` (often `ThreadPoolTaskScheduler` backed by scheduled executor) with cron/fixedDelay triggers — tasks are methods, not serializable events. No built-in persistence unless Spring Batch or Quartz integrated. For cluster-safe cron, use ShedLock, Quartz JDBC, or K8s CronJob. `DelayQueue` is lower-level building block inside executor, not a distributed scheduler.

**Q:** Misfire handling when JVM pauses for GC?
**A:** After long pause, all expired delays fire in burst when thread wakes — thundering herd. Mitigate: jitter in `getDelay`, rate-limit drain loop, separate pools for retry vs user-facing. Monitor queue size metric; alert when depth grows monotonically.

#### Scenario probe

In-memory retry queue after 2-hour GC pause delivers 50k webhooks simultaneously and triggers partner rate limit ban.

**Model answer:** Root cause: `DelayQueue` dump on resume with no drain throttle. Fix: cap concurrent outbound HTTP with semaphore; persist retry schedule to DB with `next_attempt`; on wake, spread delays with random jitter. Long-term: move retries to Kafka with `retry.topic` and consumer pause, or external scheduler. Keep in-memory queue only for sub-second debouncing.

#### Code / config (when useful)

```java
record RetryTask(String id, long fireAtNanos) implements Delayed {
    public long getDelay(TimeUnit u) {
        return u.convert(fireAtNanos - System.nanoTime(), TimeUnit.NANOSECONDS);
    }
    public int compareTo(Delayed o) { return Long.compare(getDelay(NANOSECONDS), o.getDelay(NANOSECONDS)); }
}
```

---

### 55. Thread pool observability: Micrometer metrics, queue depth alerts.

**Short answer:** Expose pool active count, pool size, queue depth, completed tasks, and rejection rate via Micrometer — bind `ExecutorServiceMetrics.monitor(registry, executor, "payments")` or custom gauges on `ThreadPoolExecutor`. Alert on sustained queue depth >70% capacity and rising rejection count; correlate with Tomcat/Hikari saturation. Thread dumps alone are lagging; metrics show trend before pool exhaustion.

#### What it is
Observability for executors translates queueing theory into dashboards: Little's law (L = λW) applied to thread pools. Micrometer tags metrics by pool name; Prometheus/Grafana scrape `/actuator/prometheus`.

#### How it works (internals)
`ThreadPoolExecutor` exposes `getQueue().size()`, `getActiveCount()`, `getCompletedTaskCount()`. `ExecutorServiceMetrics` registers gauges and timers around submitted tasks. Virtual-thread executors report different semantics — platform carrier pool vs unbounded virtual task count; monitor `jdk.VirtualThreadScheduler` JMX and pin events separately.

#### When to use / when NOT to use
Every production bounded pool gets metrics and alerts — no exceptions. Do not alert on active=maximum alone during known batch windows without baseline. Pair pool metrics with downstream latency and DB pool wait time for causal chain.

#### Production example
Fraud scoring pool queue depth Grafana alert fires at 500/1000 for 5 minutes — on-call scales pods and finds slow external API; temporary bulkhead reduction prevents total checkout failure. Post-incident: add `executor.rejected` counter and dashboard panel for `@Async` pool vs HTTP worker pool separately.

#### Common mistakes
Monitoring only CPU while queue grows — threads blocked on I/O show low CPU. Using default pool names — impossible to map metric to bean. No alert on `RejectedExecutionException` rate — first signal of death spiral.

#### Interview follow-ups (with model answers)

**Q:** Which Micrometer metrics for `ForkJoinPool.commonPool()`?
**A:** Common pool is harder to bind — use JMX `ForkJoinPool` MBean (`getQueuedSubmissionCount`, `getRunningThreadCount`) or avoid common pool for blocking work. Prefer dedicated injected executors with explicit Micrometer bind. For `parallelStream`, metric indirectly via latency and common pool JMX in JVM dashboard.

**Q:** Alert threshold for queue depth?
**A:** Relative to bounded queue capacity and drain rate: alert when depth >70% for N minutes AND task age p99 rises. Static threshold on unbounded queue useless — alert on derivative of queue size and OOM risk via heap. Include rejection counter >0 sustained as SEV2.

#### Scenario probe

Checkout p99 spikes; CPU normal. Thread dump shows all Tomcat threads in `RUNNABLE` on HTTP client calls, but root cause is `@Async` pool queue full causing synchronous fallback path.

**Model answer:** Trace shows order placement blocking on `Future.get()` without timeout when async pool saturated. Metrics would show `executor.queue.size` pegged and `rejected` incrementing. Fix: remove blocking get, use CompletableFuture callback, enlarge pool modestly, bulkhead fraud calls separately. Add Micrometer bind at bean creation and alert before user-visible latency degrades.

---

### 56. Virtual thread scheduler and carrier thread pool tuning (`jdk.virtualThreadScheduler`).

**Short answer:** Virtual threads mount on a small platform-thread carrier pool (default ~# CPUs). Tuning `-Djdk.virtualThreadScheduler.parallelism=N` increases carriers when workloads mix CPU and blocking I/O; `-Djdk.virtualThreadScheduler.maxPoolSize` caps carriers (Java 21+). Too few carriers starve CPU work; too many increases context switching without benefit. Measure carrier utilization and pin rate before tuning — defaults suit most I/O-bound Spring services.

#### What it is
The virtual thread scheduler (ForkJoinPool-based in current JDK) schedules runnable virtual threads onto carrier platform threads. When virtual thread blocks on I/O, it unmounts, freeing carrier for another virtual thread.

#### How it works (internals)
System properties: `jdk.virtualThreadScheduler.parallelism` (default = available processors), `jdk.virtualThreadScheduler.maxPoolSize` (default 256 cap). Carrier pool is separate from `ForkJoinPool.commonPool()`. CPU-bound work on virtual threads can pin carriers — consider platform threads for compute-heavy tasks.

#### When to use / when NOT to use
Increase parallelism when profiling shows carrier pool fully utilized AND virtual threads ready but not running, with low pin rate. Do not set max pool size arbitrarily high on CPU-bound apps — use platform thread pool for compute. Re-test after JDBC driver upgrade — blocking behavior affects carrier demand.

#### Production example
Spring Boot 3.2 on Java 21: 200 RPS I/O service fine on defaults. Batch reconciliation mixing CSV parse (CPU) and DB I/O raised parallelism from 8 to 16 carriers — p99 dropped 40% with pin rate <1%. Documented JVM flags in K8s deployment manifest.

#### Common mistakes
Setting parallelism = 200 thinking it matches virtual thread count — carriers are not 1:1 with requests. Ignoring `ForkJoinPool.commonPool` still used by parallelStream on same cores. Tuning without JFR scheduler events — guessing from thread count in dump.

#### Interview follow-ups (with model answers)

**Q:** Relationship to Tomcat virtual thread executor?
**A:** Tomcat 10.1+ `virtual` executor creates new virtual thread per request — scheduler carriers handle all mounted virtual threads across Tomcat and application code. Heavy `@Async` on platform pool still competes for CPUs separately. Align Tomcat max connections with DB pool — virtual threads cheap but connections are not.

**Q:** When to reduce default parallelism?
**A:** Rare — mostly when co-locating with CPU-heavy agents on small instances and carriers contend with GC threads. More often fix pin sources (synchronized blocks, native JNI) than shrink carriers. If carriers idle while work queues, problem is downstream bottleneck not scheduler size.

#### Scenario probe

After enabling virtual threads, latency improves but CPU pegs at 100% on 4-core pods with low RPS — carriers thrashing.

**Model answer:** Profile shows CPU-bound JSON validation on every request running on virtual threads — mounts consume all carriers. Fix: move validation to platform pool with bounded queue or optimize parser; reduce scheduler parallelism only after moving CPU work off virtual threads. Add JFR `jdk.VirtualThreadSubmitFailed` and carrier utilization metrics.

---

### 57. Pinning detection runbook: JFR event `jdk.VirtualThreadPinned`.

**Short answer:** Pinning occurs when a virtual thread blocks while holding a monitor or inside native code, blocking its carrier. Enable JFR event `jdk.VirtualThreadPinned` (threshold 20ms default) in prod short windows or continuous in staging. Runbook: capture JFR during incident → identify stack with `synchronized` or JDBC driver → replace with `ReentrantLock`, unpinned driver, or platform thread for that section.

#### What it is
Virtual thread pinning defeats scalability — one pinned virtual thread occupies a carrier for entire critical section. JFR records pin start/end with stack trace and duration.

#### How it works (internals)
Start JFR: `jcmd <pid> JFR.start name=pin settings=profile duration=60s filename=pins.jfr` with event enabled in `.jfc` template. Analyze in JDK Mission Control — filter `VirtualThreadPinned` by duration and stack. Common culprits: `synchronized` methods in hot path, old MySQL connector, file I/O inside synchronized logger.

#### When to use / when NOT to use
Run pinning profiling before major virtual-thread migration and after dependency upgrades. Continuous prod sampling with low overhead acceptable if pin rate SLO exists. Do not ignore short pins <1ms at massive scale — aggregate time matters.

#### Production example
Staging load test: JFR shows 12% request time in pins on `com.mysql.cj.jdbc.ConnectionImpl` synchronized block — upgrade connector version documented as virtual-thread-friendly; pin rate drops to 0.2%. Prod canary monitors `jvm.virtual_threads.pinned` custom metric from periodic JFR micro-samples.

#### Common mistakes
Assuming `-Djdk.tracePinnedThreads=full` in prod without overhead plan — diagnostic only. Fixing one synchronized block while missing others in same call chain. Moving all JDBC to platform threads without measuring — over-correction wastes virtual thread benefits.

#### Interview follow-ups (with model answers)

**Q:** Difference between pinned and mounted?
**A:** Mounted virtual thread runs on carrier — normal. Pinned virtual thread cannot unmount while blocked inside synchronized/native — carrier blocked too. Thread dump may show virtual thread as carrier platform thread name — confusing without JFR.

**Q:** Runbook first five minutes?
**A:** Confirm symptom (latency, carrier 100%). Start 60s JFR with VirtualThreadPinned. Identify top stack frames. Check recent dependency or synchronized code deploy. Mitigate: rollback, increase carriers temporarily, or route affected endpoint to platform pool. Open ticket to replace pin source; add regression JFR test in CI load gate.

#### Scenario probe

Production virtual-thread service: p99 8s, carriers all busy, few RUNNABLE platform threads, no obvious deadlock.

**Model answer:** JFR pinning report shows file append inside `synchronized` log appender during high traffic. Fix: async appender without global lock or structured logging agent. Validate pin rate <0.5% in load test before promote. Document in runbook: "high p99 + full carriers + low DB wait → run JFR pin profile."

---

### 58. `StructuredTaskScope.ShutdownOnFailure` vs `ShutdownOnSuccess`.

**Short answer:** Both are structured concurrency scopes (Java 21+ preview, finalized in 22+) that fork subtasks and join with policy. `ShutdownOnFailure` cancels siblings and closes scope when any subtask fails — fan-out RPC where one failure aborts all. `ShutdownOnSuccess` shuts down when first subtask succeeds — race redundant providers (fastest DNS, mirror fetch). Pick policy matching business invariant: all-or-nothing vs first-win.

#### What it is
StructuredTaskScope ensures subtasks lifetime nested within scope — no orphaned tasks after scope closes. Shutdown policies automate cancellation on failure or first success.

#### How it works (internals)
Try-with-resources on scope; `fork` returns `Subtask`; `join` waits per policy. On failure policy, first exception triggers `shutdown()` interrupting other forks. On success policy, first successful result triggers shutdown — other tasks receive interruption. Requires preview flag until your JDK version ships final API.

#### When to use / when NOT to use
`ShutdownOnFailure`: parallel validate-then-commit steps where partial success is wrong. `ShutdownOnSuccess`: hedge requests, multi-region read fallback. Not for open-ended pipelines — use executor + CompletableFuture with explicit composition if policies do not fit.

#### Production example
Pricing service calls three vendor APIs in parallel with `ShutdownOnSuccess` — first quote under 200ms wins; others cancelled to save quota. Inventory reservation uses `ShutdownOnFailure` — payment + hold + fraud must all succeed or entire scope rolls back compensations.

#### Common mistakes
Using `ShutdownOnSuccess` when all results needed for merge — loses data. Swallowing interrupt in fork body — scope cannot shut down tasks. Forgetting scope is single-shot — create new scope per request.

#### Interview follow-ups (with model answers)

**Q:** vs `CompletableFuture.anyOf` / `allOf`?
**A:** StructuredTaskScope ties thread lifecycle to lexical scope — interrupt propagation and cancellation on close are explicit. CompletableFuture is flexible but easier to leak tasks without timeout or executor. Prefer structured scope for request-scoped fan-out in Java 21+; CF when integrating async libraries.

**Q:** Exception handling in `ShutdownOnFailure`?
**A:** After join, iterate subtasks — failed subtask exposes exception; scope may throw `StructuredTaskScope.FailedException` wrapping first failure. Map to domain error at API boundary; log suppressed sibling failures for audit.

#### Scenario probe

Parallel KYC checks: if document verify fails, identity and sanctions checks should stop immediately to avoid duplicate PII processing fees.

**Model answer:** Use `ShutdownOnFailure` scope; fork three checks; any failure closes scope and interrupts others. Return aggregated error to client. Contrast with `allOf` without cancellation — slow checks continue burning vendor API cost. Test with injected failure on second fork asserting third never completes (Mockito timeout or counter).

---

### 59. `java.util.concurrent` vs `j.u.c.atomic` vs `VarHandle` (Java 9+).

**Short answer:** `j.u.c` provides high-level concurrent structures and executors — prefer for most application code. `j.u.c.atomic` offers lock-free counters and references (`AtomicInteger`, `AtomicReference`) with CAS loops. `VarHandle` is the expert escape hatch for fine-grained field/array element access with memory ordering modes — used by frameworks and low-latency libraries, rarely in business services. Reach for atomics before VarHandle; reach for locks/structures before atomics when invariants span multiple fields.

#### What it is
Three layers: structured concurrency utilities, atomic wrappers on volatile + CAS, and raw VarHandle API replacing unsafe field access for expert tuning.

#### How it works (internals)
Atomics use `compareAndSet` with spin on contention. `VarHandle` supports `get`, `set`, `compareAndSet`, and explicit `MemoryOrder` (plain, opaque, release/acquire, volatile). Multiple VarHandle operations can compose field-wise atomicity without locking whole object — hard to prove correct.

#### When to use / when NOT to use
Counters/metrics: `LongAdder` / atomics. Concurrent maps: `ConcurrentHashMap`. Expert lock-free queues or off-heap: VarHandle with formal verification. Do not use VarHandle in CRUD services — maintenance cost exceeds benefit.

#### Production example
Metrics: `LongAdder` for request counts — scales better than `AtomicInteger`. Custom lock-free ring buffer in internal SDK uses VarHandle on array elements with acquire/release — not copied to product microservices. Code review rejects VarHandle in payment service PR.

#### Common mistakes
Using `AtomicInteger` for compound state (status + count) — torn reads. VarHandle with wrong memory order — subtle visibility bugs. Replacing all synchronized with atomics without proving invariant safety.

#### Interview follow-ups (with model answers)

**Q:** VarHandle vs `Unsafe`?
**A:** VarHandle is supported replacement for reflective unsafe field ops — same underlying mechanics, safer API, memory order explicit. Libraries migrating from Unsafe to VarHandle for JDK compatibility. Application devs should not touch either for business logic.

**Q:** When `LongAdder` over `AtomicLong`?
**A:** High write contention on counter — LongAdder stripes cells reducing CAS failures. Read `sum()` more expensive and not linearizable snapshot — fine for metrics, wrong for strict global sequence generation. Use AtomicLong when every increment must be exact readable value immediately.

#### Scenario probe

Developer replaces `synchronized` balance update with two separate `AtomicInteger` fields for dollars and cents — double-spend race under load.

**Model answer:** Invariant spans fields — need synchronized block, single `AtomicReference<Money>`, or transactional DB update. Atomics per field do not compose. Interview lesson: choose abstraction level matching invariant boundary; VarHandle only if proven lock-free algorithm with tests (jcstress).

---

### 60. `StampedLock` optimistic read failure paths.

**Short answer:** `StampedLock` offers optimistic read (`tryOptimisticRead`) — fast path without lock if no writer interfered; validate with `validate(stamp)` or upgrade to read lock. On validation failure, retry optimistic or fall back to read lock — failure path must not assume optimistic read saw consistent state. Use for read-heavy caches with rare writes; avoid for write-heavy or lock ordering with other locks.

#### What it is
Three modes: write, read, optimistic read. Optimistic returns stamp without blocking; writer invalidates optimistic stamps.

#### How it works (internals)
`long stamp = lock.tryOptimisticRead(); read fields; if (!lock.validate(stamp)) { stamp = lock.readLock(); try { ... } finally { unlockRead(stamp); } }`. Writer exclusive — blocks optimistic and read. Not reentrant — reentrant attempt deadlocks. No fairness — can starve writers under heavy optimistic readers if writers rare anyway OK.

#### When to use / when NOT to use
In-memory config cache: 99.9% reads, optimistic path saves lock overhead. Not for banking balances or when writers frequent — validation failure loop wastes CPU. Never use with other locks in fixed order without careful deadlock analysis — StampedLock not well-behaved in lock ordering.

#### Production example
Feature flag snapshot: optimistic read of immutable config reference; on validate fail, acquire read lock and copy pointer to local variable. Writes publish new immutable config object under write lock — readers see old or new, never torn map.

#### Common mistakes
Using values read during optimistic phase after validate fails without re-read. Calling `unlockWrite` with read stamp — corrupts lock state. Using StampedLock in virtual-thread code with long validate loops — consider immutable snapshot + volatile publish instead.

#### Interview follow-ups (with model answers)

**Q:** Optimistic vs `ReadWriteLock`?
**A:** ReadWriteLock always acquires lock metadata — higher overhead for uncontended reads. Optimistic avoids lock when no writer — but retry on failure. If write rate > few percent, optimistic retries dominate — RW lock or immutable copy simpler.

**Q:** Is optimistic read linearizable?
**A:** No — validate only guarantees no write between optimistic start and validate; compound operations across fields still need read lock or immutable snapshot. Do not check-then-act on optimistic values without re-read under read lock.

#### Scenario probe

Cache uses optimistic read; under deploy flag flip burst, CPU spikes from validate failures while writers churn.

**Model answer:** Switch hot path to volatile reference to immutable snapshot updated atomically on write — readers never lock. StampedLock optimistic for micro-optimization not worth churn during writes. Monitor validate failure rate; if >5%, change strategy.

#### Code / config (when useful)

```java
long stamp = lock.tryOptimisticRead();
var cfg = configRef;
if (!lock.validate(stamp)) {
    stamp = lock.readLock();
    try { cfg = configRef; } finally { lock.unlockRead(stamp); }
}
```

---

### 61. Backpressure with `Semaphore` + reactive bridge to blocking JDBC.

**Short answer:** Reactive streams (WebFlux, R2DBC) propagate demand via `request(n)`; blocking JDBC blocks threads. Bridge with bounded `Semaphore` matching Hikari pool size — acquire before `subscribeOn(boundedElastic)` or wrap blocking call limiting in-flight JDBC work. Without semaphore, unlimited `flatMap` concurrency exhausts connections and stalls. Semaphore permits = pool size minus headroom for admin threads.

#### What it is
Backpressure limits in-flight work so producers do not outrun consumer capacity. Semaphore is counting gate for blocking sections in hybrid reactive/blocking architectures.

#### How it works (internals)
`Semaphore(poolSize - 2).acquire()` before blocking repository call; release in `finally`. Reactor: `flatMap(x -> Mono.fromCallable(() -> jdbc(x)).subscribeOn(blockingPool), concurrency)` where concurrency matches permits. Project Reactor `limitRate` does not help inside blocking JDBC without semaphore — elastic pool still spawns many blocked threads.

#### When to use / when NOT to use
Hybrid services calling legacy JDBC from WebFlux endpoints — mandatory pattern. Full R2DBC stack — semaphore less central but still limit concurrent TX. Do not set permits >> pool — waiters hold threads anyway; permits should track real connection budget.

#### Production example
Report API on WebFlux calls Oracle via JdbcTemplate: semaphore 18 permits, Hikari max 20. Under spike, `acquire` waits with timeout — API returns 503 with Retry-After instead of connection timeout cascade. Metrics: `jdbc.inflight` gauge from available permits.

#### Common mistakes
Unbounded `Schedulers.boundedElastic()` with JDBC — thousands of blocked threads. Semaphore released in wrong thread after reactive chain — use `doFinally`. Matching semaphore to Tomcat threads not pool size — still exhausts DB.

#### Interview follow-ups (with model answers)

**Q:** Why not block in reactive thread at all?
**A:** Blocking on event loop thread stalls all requests on that loop — never call JDBC on parallel/ single scheduler. Offload to bounded pool AND limit concurrency with semaphore aligned to pool. Better long-term: R2DBC or separate sync microservice.

**Q:** `tryAcquire` with timeout vs block?
**A:** `tryAcquire(500, MS)` enables fail-fast under overload — preserves latency SLO for accepted requests. Indefinite acquire queues unbounded waiters on platform threads — hidden queue like unbounded thread pool. Return 503 and shed load when timeout.

#### Scenario probe

WebFlux migration: DB pool exhausted, event loop threads show BLOCKED on JDBC in thread dump.

**Model answer:** Missing backpressure — `flatMap` concurrency 256 with pool 10. Fix semaphore permits, reduce flatMap concurrency, move JDBC to dedicated `@Async` sync service with queue. Load test proves stable pool active count under 2x traffic. Document hybrid architecture debt until R2DBC.

---

### 62. Concurrency testing with `Awaitility` and stress tests.

**Short answer:** Unit tests with `Thread.sleep` are flaky; `Awaitility.await()` polls condition with timeout and backoff until invariant holds or fails with diagnostics. Combine with jcstress for JMM litmus tests, and bounded stress loops (ExecutorService + CountDownLatch) for race reproduction. CI: short Awaitility timeouts locally; longer in nightly stress job. Prove fixes with test that failed before fix.

#### What it is
Awaitility is DSL for asynchronous/eventual assertions in tests. Stress tests hammer concurrent API under fixed thread count seeking invariant violations or exceptions.

#### How it works (internals)
`await().atMost(5, SECONDS).untilAsserted(() -> assertThat(counter.get()).isEqualTo(100))` — polls until true. jcstress runs many thread interleavings on OpenJDK harness. Integrate stress as separate Maven profile to avoid slowing PR builds.

#### When to use / when NOT to use
Any test involving `CompletableFuture`, executor callbacks, cache expiration, or virtual threads — Awaitility over sleep. jcstress for custom atomics/lock-free structures. Not replacement for property-based tests (jqwik) for logic — complementary.

#### Production example
Idempotency cache test: 50 threads submit same key; Awaitility waits until exactly one DB insert recorded and others hit cache — caught race before prod. jcstress on custom MPMC queue shipped only after CHM baseline comparison passed.

#### Common mistakes
`await()` without `untilAsserted` swallowing assertion message. Stress test without bounded time — CI hang. Flaky pass rate 95% ignored — race still ships.

#### Interview follow-ups (with model answers)

**Q:** Awaitility vs `@RepeatedTest`?
**A:** RepeatedTest reruns whole test hoping to catch race — wasteful and still misses rare interleavings. Awaitility handles intentional async delay. For races, use stress with many threads + latch start gun + Awaitility on final state.

**Q:** jcstress in CI cost?
**A:** Run in nightly or manual workflow — minutes of CPU. PR gate runs focused jcstress mode on changed classes only. Failing jcstress is P0 — JMM bug not fixable by retry.

#### Scenario probe

CI flaky: payment idempotency test passes locally, fails 5% on Jenkins with duplicate key on rare runs.

**Model answer:** Replace sleep with Awaitility on DB row count; add stress profile 100 parallel submits with same idempotency key; reproduce duplicate; fix with DB unique constraint + `INSERT ON CONFLICT` or synchronized idempotency store. Document stress job in README; fail build if duplicate detected once in 1000 iterations.

#### Code / config (when useful)

```java
await().atMost(10, SECONDS).pollInterval(50, MILLISECONDS)
    .untilAsserted(() -> assertThat(repo.countByPaymentId(id)).isEqualTo(1));
```

---

## Scenario-based interview drills

### S1. Kafka rebalance storm duplicates settlement events during rolling deploy

**Situation:** Payments settlement service runs 24 Spring Kafka consumers on 8 partitions. During rolling deploy, the consumer group rebalances four times in two minutes. Finance reports duplicate settlement rows for the same paymentId with matching amounts. Consumers use auto-commit with at-least-once processing and no idempotency table.

**What they're testing:** Kafka rebalance semantics, cooperative sticky assignor, manual ack, idempotent consumer design, on-call triage.

**How to structure your answer:**
- Correlate duplicate timing with REVOKED/ASSIGNED rebalance logs
- Explain auto-commit replay window where offsets commit after processing or vice versa
- Design idempotent write with unique paymentId constraint and processed_events audit
- Reduce rebalance churn: static group.instance.id, cooperative-sticky assignor, graceful leave
- Chaos test kill pod mid-batch in staging with Testcontainers Kafka

**Model answer:** I start by correlating duplicate settlement timestamps with consumer group rebalance events in Kafka logs and Grafana — if duplicates cluster around partition revocation, this is a consumption semantics problem, not an Oracle bug. With auto-commit, a consumer can process a batch, lose the partition on rebalance before commit, and another consumer replays the same offsets — duplicates mean replay, not silent loss. Immediate mitigation: pause deploys, enable cooperative-sticky assignor, set adequate session.timeout.ms, and assign static group.instance.id per pod so rolling restart does not churn the entire group. Permanent fix: manual acknowledgment only after the database transaction commits; insert settlement with a unique constraint on paymentId — on DuplicateKeyException, log and ack the offset as already processed. Store consumer group, topic, partition, and offset in processed_events for audit. Processing must be idempotent: UPDATE ... WHERE status=PENDING, not blind INSERT. Test by killing a pod mid-batch in staging under load and asserting no duplicate money movement. Postmortem action: never auto-commit on money paths; alert when rebalance rate exceeds threshold per hour.

**Common weak answers:** Blame Kafka for duplicating messages without fixing the consumer; enable EOS without DB idempotency; disable rolling deploy; dedupe only in finance spreadsheets.

**Follow-up probes (with answers):**

**Q:** Would Kafka exactly-once transactions solve this without DB changes?
**A:** Kafka EOS only helps when all side effects stay inside the broker transactional boundary. Oracle settlement is outside that boundary — you still need a unique business key and idempotent JDBC upsert. EOS reduces duplicate reads from the consumer but never replaces database authority for money movement. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** How do you test rebalance behavior before the next deploy?
**A:** Chaos test: scale consumers 24 to 12 to 24 during sustained load, inject pod kill mid-poll, assert settlement row count equals unique paymentIds. Monitor consumer group state API during the test. Run in staging with production-like partition count and message rate. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

---

### S2. HikariCP pool exhaustion after Spring Boot 3 virtual threads enablement

**Situation:** After upgrading to Spring Boot 3.2 with virtual threads enabled, checkout API p99 jumps from 200ms to 8s. Thread dumps show thousands of virtual threads parked on HikariPool.getConnection. Database CPU is 30 percent while active connections peg at maxPoolSize=20. Traffic tripled because the team assumed virtual threads removed the need for pool tuning.

**What they're testing:** Virtual thread scalability limits, connection pool sizing, pinning, HTTP edge backpressure.

**How to structure your answer:**
- Prove bottleneck is connection pool not database CPU
- Explain virtual threads increase concurrent waiters not connection capacity
- Apply bulkhead and connectionTimeout with fail-fast 503
- Scan JFR for pinning prolonging connection hold time
- Load test maximum sustainable RPS before re-enabling marketing traffic

**Model answer:** Virtual threads removed the platform thread cap so two thousand concurrent requests can each block on getConnection — but Oracle still accepts only twenty sessions from this service instance. Parked virtual threads on Hikari are healthy parking, not deadlock; the bug is missing backpressure at the application edge. I pull Hikari metrics: pending threads, connection acquire time, and timeout rate. If a leak is suspected, enable leakDetectionThreshold temporarily and audit try-with-resources on every JDBC path. Short-term: add a resilience4j bulkhead limiting concurrent checkout calls to roughly twenty-five and return 503 with Retry-After when the bulkhead is full — better than an eight-second queue. Medium-term: right-size the pool with the DBA based on total session budget divided by replica count; set connectionTimeout to two seconds. Fix connections held across @Async or a @Transactional boundary that spans an HTTP call — a common regression after enabling virtual threads. Scan JFR for VirtualThreadPinned events if hold time remains high. Load test proves maximum sustainable RPS with the chosen pool size before marketing turns traffic back on.

**Common weak answers:** Set maxPoolSize to five hundred; disable virtual threads without analysis; increase database CPU only; blame Hikari as a bug.

**Follow-up probes (with answers):**

**Q:** Should pool size match virtual thread count?
**A:** No — pool size is negotiated with the DBA from database max sessions and service replica count. Virtual threads mean many waiters; the pool stays small; excess requests must queue at the app boundary with timeout, not unbounded park. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** What JDBC patterns leak connections under virtual threads?
**A:** Opening a connection before @Async without closing; ThreadLocal connection holders incompatible with carrier reuse; streaming a ResultSet while holding a connection across a slow client read. Audit @Transactional boundaries and use a DataSource proxy in staging. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

---

### S3. Redisson lock lease expires mid-transfer — double debit across two pods

**Situation:** Transfer service uses a Redis Redisson lock with a 30-second lease to guard account debit and credit. During a GC pause and slow Oracle call, the lock expires and a second pod acquires the lock and repeats the transfer. Customers see a double debit; Redis logs show two sequential lock holders, not simultaneous ones.

**What they're testing:** Distributed lock limitations, lease versus watchdog, fencing tokens, database as source of truth.

**How to structure your answer:**
- Explain lock lease expired before work finished
- Move idempotency to database unique transferId
- Use fencing token stored with row update
- Shrink critical section — no HTTP inside lock
- Chaos test pause JVM 45 seconds during transfer

**Model answer:** Distributed locks are coordination hints, not transactions — if the lease expires, another process can enter the critical section while the first is still running after a long STW GC pause. Redisson watchdog extends the lease while the JVM is healthy but cannot extend through a hung thread indefinitely. I confirm the timeline with lock hold duration histogram versus lease length and Oracle slow-query logs. Immediate stop to double-spend: database unique constraint on transferIdempotencyKey so the second insert fails. Proper pattern: begin a database transaction, SELECT account FOR UPDATE, verify transfer does not exist, insert movement rows, commit — lock scope stays minimal. If Redis is used for cross-service coordination, store a fencing token in the account row and reject updates with an older token. Reduce the critical section: no HTTP calls inside the lock. Alert on lock wait time and transfer duration p99. Post-incident chaos: pause the JVM forty-five seconds mid-transfer and assert only one debit.

**Common weak answers:** Increase lease to ten minutes and hope; trust watchdog blindly; add a second Redis lock; ignore database constraints entirely.

**Follow-up probes (with answers):**

**Q:** When is a Redisson lock appropriate in Spring microservices?
**A:** Coarse coordination such as nightly batch leader election, cache stampede singleflight across pods, or short-lived non-money resource reservations. Not for multi-step financial transfers without database idempotency and row-level authority. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** How do you implement a fencing token with Spring Data JPA?
**A:** Store a monotonic fence column on the account; lock acquisition returns a token; execute UPDATE ... WHERE id=? AND fence < :token and verify rows updated equals one. A stale worker's commit fails and must abort the business action. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

---

### S4. CompletableFuture.allOf timeout does not stop JDBC — executor queue exhaust

**Situation:** Order enrichment calls catalog, fraud, and loyalty via CompletableFuture.supplyAsync on a shared executor. A gateway timeout adds orTimeout(3s) on allOf but downstream catalog JDBC still runs 30 seconds per call. After a marketing push, the executor queue holds fifty thousand tasks while http threads return 504 and database connections stay busy.

**What they're testing:** Cancellation propagation, executor bounds, orTimeout limitations, bulkhead per dependency.

**How to structure your answer:**
- Clarify orTimeout completes exceptionally but does not interrupt running tasks by default
- Cancel(true) plus JDBC statement cancel and queryTimeout
- Separate bounded executors per dependency
- Resilience4j TimeLimiter and Bulkhead on catalog client
- Load test with slow catalog dependency via toxiproxy

**Model answer:** CompletableFuture.orTimeout on allOf only marks the composed future failed — the catalog task already submitted to the executor keeps running unless explicitly cancelled and unless JDBC respects interrupt. This is the classic timeout-at-edge-work-continues resource leak. Thread dumps show catalog enrichment tasks still in socketRead0 or JDBC while users see 504. Fix: dedicated catalogExecutor with core, max, and queue cap — rejection triggers a fallback response, not an unbounded queue. Wrap each async call with CompletableFuture.supplyAsync(..., catalogExecutor).orTimeout(2, SECONDS); on timeout, cancel(true) and set queryTimeout=2s on the connection. Resilience4j TimeLimiter plus Bulkhead on the catalog client bean is cleaner than raw CompletableFuture for Spring services. Never share one CachedThreadPool for all enrichments — fraud slowness must not starve catalog. Return a partial order with a degraded flag when non-critical enrichment fails. Metrics: executor queue depth, timed-out stage count, active JDBC connections. Integration test with toxiproxy delay proves the pool does not exhaust after one thousand requests.

**Common weak answers:** Increase gateway timeout to sixty seconds only; add orTimeout without cancel; bigger executor without bounds; blame CompletableFuture as broken.

**Follow-up probes (with answers):**

**Q:** Does Java 21 StructuredTaskScope fix this pattern?
**A:** ShutdownOnTimeout cancels forked tasks when the scope closes — better structure, but JDBC still needs queryTimeout and an interrupt-aware driver. Use one scope per request with a deadline aligned to the gateway. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** How do you implement degraded mode in Spring MVC?
**A:** When the circuit breaker is open, return a cached catalog snapshot, increment enrichment_degraded metric, and do not block order creation on a loyalty points lookup failure. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

---

### S5. ShedLock missing — @Scheduled refund job runs on all twelve pods

**Situation:** Refund reconciliation uses @Scheduled(cron = '0 0 2 * * *') on every Kubernetes pod — twelve instances. Customers receive duplicate refund credits overnight. The job is @Transactional but has no unique guard; logs show twelve overlapping executions at 02:00:01.

**What they're testing:** Distributed scheduling, ShedLock, idempotent batch design, Kafka as cron alternative.

**How to structure your answer:**
- Identify horizontal scale multiplied scheduled side effects
- Immediate disable cron except one pod or feature flag
- Add ShedLock JDBC with lockAtMostFor
- Idempotent batch keyed by settlement batchId
- Long-term Kafka scheduled topic or external scheduler

**Model answer:** @Scheduled is in-process — scaling replicas scales cron executions unless coordinated. @Transactional does not serialize across JVMs — twelve threads can all pass a 'no refund yet' check in a race window. Immediate mitigation: run scheduler profile on one deployment, or disable cron via ConfigMap until the fix ships. Add ShedLock with @SchedulerLock on refundJob, JDBC lockProvider, lockAtLeastFor to prevent rapid re-run, lockAtMostFor to prevent stuck locks. Business fix: refund table unique on (orderId, refundType); job inserts with ON CONFLICT DO NOTHING. Reconcile duplicates already sent via finance DLQ. Architecture review: high-volume scheduled work should be a Kafka message produced once by an external cron. Test five replicas in staging and assert single execution via audit log count. Alert if refund_job_start metric count exceeds one per window.

**Common weak answers:** Reduce replicas to one forever; rely on @Transactional alone; manual ops runbook only; ignore because cron is a dev concern.

**Follow-up probes (with answers):**

**Q:** ShedLock JDBC versus Redis provider?
**A:** JDBC uses the same Oracle — fewer moving parts with row-level lock on the shedlock table; Redis offers faster lock operations but another failure domain. Pick based on existing infrastructure and clock skew tolerance on lockAtMostFor. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** How would Kafka replace this cron?
**A:** An external scheduler or Kubernetes CronJob publishes one RefundBatchRequested event; a single consumer group processes it — natural single-flight per partition key batchDate. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

---

### S6. WebFlux event loop blocked by JDBC — latency cliff at 200 rps

**Situation:** A team migrated one endpoint to WebFlux for performance but the repository still uses blocking JdbcTemplate inside map. The endpoint works in development; at 200 rps p99 reaches 12 seconds and event-loop threads show BLOCKED on JDBC. Netty runs few event-loop threads — one blocked loop stalls many connections.

**What they're testing:** Reactive threading model, block() anti-pattern, boundedElastic bridge, architectural boundary.

**How to structure your answer:**
- Explain blocking on the event loop is catastrophic
- Options: revert to MVC plus virtual threads, boundedElastic with cap, or R2DBC
- Never block inside flatMap without publishOn
- Add BlockHound test rule in CI
- Pick a consistent stack per service in an ADR

**Model answer:** WebFlux assumes a non-blocking event loop — blocking JDBC holds one of few loop threads, stalling all connections assigned to it. Low traffic in development masked the issue; under load the latency cliff is the signature pattern. Reactor BlockHound in CI catches blockOnJdbc on a reactor thread. Fix options ranked: revert the endpoint to Spring MVC with virtual threads if the goal is throughput on a blocking stack — honest architecture. Wrap JDBC in Mono.fromCallable(...).subscribeOn(Schedulers.boundedElastic()) with a tight concurrency limit — a bridge pattern, not free scalability. Migrate the read path to R2DBC only after validating transactional semantics — high effort. Short-term rate limit the endpoint and scale replicas — loops still block but spread load. Long-term: reactive gateway plus blocking microservice via WebClient is valid; hybrid blocking inside WebFlux controller is not. Add a BlockHound test rule failing the build on jdbc in a reactor thread.

**Common weak answers:** Add more event loops; disable BlockHound in production; use parallelStream in WebFlux; ignore because reactive is always faster.

**Follow-up probes (with answers):**

**Q:** When is a boundedElastic bridge acceptable?
**A:** As a migration stepping stone for a small number of blocking calls with a strict concurrency cap, monitoring, and a plan to move to R2DBC or MVC — not as the end state for a hot path. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Virtual threads with WebFlux?
**A:** Different models — do not mix casually. Spring MVC plus virtual threads is often simpler for JDBC-heavy services than a WebFlux bridge. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

---

### S7. Transactional outbox publisher crash — double Kafka publish after recovery

**Situation:** Order service writes an outbox table in the same transaction as the order; a separate @Scheduled publisher polls, sends to Kafka, then marks SENT. A pod crashes after kafka send succeeds but before UPDATE outbox SET status=SENT. Restart republishes the same event and downstream fulfillment ships a duplicate package.

**What they're testing:** Outbox pattern correctness, idempotent consumer, publish marking order, crash window.

**How to structure your answer:**
- Draw transaction boundary and crash window between send and mark
- Accept at-least-once publish if consumers are idempotent
- Mark IN_FLIGHT before send; mark SENT after broker ack
- Downstream dedupe by eventId UUID
- Consider Debezium CDC outbox alternative

**Model answer:** Outbox guarantees at-least-once delivery to the broker — a crash after send before mark means republish on recovery; that is expected behavior, not a Kafka defect. The bug is downstream treating the event as exactly-once without deduplication. Verify the outbox row is still PENDING after crash while Kafka already has the message — replay is correct. Publisher improvements: update status to IN_FLIGHT in the same transaction before send using SELECT FOR UPDATE SKIP LOCKED polling; after successful broker ack, mark SENT in a new transaction; if crash occurs between, republish is safe when the consumer is idempotent on eventId. Fulfillment service stores processed_event_ids with a unique constraint — second delivery is a no-op. Alternative: Debezium CDC outbox eliminates the polling scheduler. Metrics: outbox_pending_age, publish_retry_count, consumer_duplicate_skipped. Test: kill the publisher pod after simulated broker ack and assert single fulfillment.

**Common weak answers:** Turn off outbox and dual-write order plus Kafka; believe exactly-once without consumer dedupe; delete the outbox row before send ack is confirmed.

**Follow-up probes (with answers):**

**Q:** Debezium versus polling publisher trade-offs?
**A:** Debezium offers lower latency and no scheduler lock but adds connector operations complexity; polling is simpler with higher lag and requires ShedLock on the scheduler — choose per team ops maturity. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Should outbox mark SENT before or after Kafka ack?
**A:** After ack — marking before risks a lost message if send fails; marking after risks duplicate on crash, which consumers must handle; that is industry standard for outbox. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

---

### S8. Micrometer counter double-registration race — billing metrics wrong on deploy

**Situation:** A custom MeterRegistry counter is created in @PostConstruct with a name including tenantId from a config refresh thread. During hot reload, two threads register the same meter name — intermittent IllegalArgumentException in logs and lost billing event counts during the deploy window. Finance dashboard under-reports usage by eight percent on deploy days.

**What they're testing:** MeterRegistry thread safety, counter versus LongAdder, lazy registration, config refresh concurrency.

**How to structure your answer:**
- Identify concurrent registration of the same meter id
- Register all meters at startup with static tag keys
- Use LongAdder local aggregate flushed periodically
- Do not recreate MeterRegistry beans on @RefreshScope
- Canary deploy compares billing metric sum to DB audit rows

**Model answer:** Micrometer MeterRegistry is thread-safe for increment on an existing meter but registering duplicate name-plus-tags throws or behaves inconsistently depending on registry implementation. Hot config refresh recreating counters races with request threads incrementing the old meter reference. Fix: register all meters at applicationReadyEvent with static tag keys; use tenant as a tag value, not a separate meter name per tenant unless cardinality is bounded and documented. For hot-path billing, keep a local LongAdder per tenant in ConcurrentHashMap and flush to Micrometer every ten seconds to reduce registry contention. Config refresh should swap business rules atomically — never recreate MeterRegistry beans. Use @RefreshScope carefully — a scoped proxy meter bean is a common footgun. CI stress test: parallel refresh plus increment. Canary deploy compares billing metric sum to database audit table row count. Alert on meter registration exception rate.

**Common weak answers:** Synchronize the entire request on meter register; disable metrics; create a new registry per tenant; ignore eight percent as rounding error.

**Follow-up probes (with answers):**

**Q:** What is cardinality explosion with per-tenant meters?
**A:** Thousands of unique meter names crash Prometheus — use limited tags and aggregate; follow observability team policy on high-cardinality labels. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** Describe a LongAdder flush pattern for billing.
**A:** ConcurrentHashMap of tenant to LongAdder; scheduled task sums into registry.counter('billing.events', 'tenant', t).increment(flushAmount) using a documented flush interval. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

---

### S9. Kubernetes liveness kills pod mid-batch — Kafka offset not committed

**Situation:** An invoice batch consumer processes ten thousand messages per poll; processing takes four minutes. Liveness probe hits /actuator/health returning DOWN while the consumer is busy. Kubernetes restarts the pod every ninety seconds; messages are reprocessed, some invoices emailed twice, and consumer lag oscillates.

**What they're testing:** Liveness versus readiness, max.poll.interval.ms, graceful batch design, health indicators.

**How to structure your answer:**
- Separate liveness from long processing work
- Reduce batch size or pause consumption during long work
- Set max.poll.interval.ms above worst-case batch duration
- Idempotent invoice send by invoiceId
- Fix health endpoint to not block on consumer thread

**Model answer:** Liveness should detect deadlock, not long legitimate work — if health check waits for the consumer thread, Kubernetes kills the pod during a normal batch. Symptom: pod restart count correlates with lag spikes and duplicate side effects. Kafka consumer heartbeat: max.poll.interval.ms must exceed maximum time between poll() calls — four minutes of processing without poll triggers rebalance too. Fix batch design: poll smaller batches, process with pause and resume, or break work into chunks with poll in the loop. Never run four minutes of work between poll() calls on a hot consumer. Health: liveness is a lightweight ping; readiness may include consumer subscription active and recent successful poll timestamp, not batch completion. Idempotent invoice email via unique invoiceId in the provider dedupe field. Tune terminationGracePeriodSeconds for in-flight batch drain on deploy. Load test the full batch path with Kubernetes probes enabled.

**Common weak answers:** Disable liveness entirely; set max.poll.interval to infinite; ignore duplicates; use single-message poll without a throughput plan.

**Follow-up probes (with answers):**

**Q:** How do you structure a long batch with a Kafka consumer?
**A:** Poll records, hand off to a bounded executor, pause the partition until futures complete, then commit synchronously — or use incremental ack per message with an idempotent handler. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** What should a Kafka listener health indicator check?
**A:** That the listener container is running and the last successful poll timestamp is within threshold — not waiting for an entire batch job to finish. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

---

### S10. Design review: real-time fraud scoring for card authorization — 80ms SLA

**Situation:** You are staff engineer in design review for a new fraud service. The authorization path receives ISO8583-derived JSON and must call a rules engine and Redis feature store, returning decline or approve in 80ms p99. Peak load is five hundred thousand authorizations per hour. The team proposes @Async rules plus WebSocket callback to the issuer.

**What they're testing:** End-to-end latency design, synchronous versus misplaced async, pooling, caching, failure modes.

**How to structure your answer:**
- Reject async callback for inline authorization SLA
- Bound parallel feature fetches with a deadline budget
- Redis pipeline, local Caffeine L1, circuit breaker on rules engine
- Document fail-open versus fail-closed policy
- Prove 80ms p99 with Gatling and JFR in performance CI

**Model answer:** Authorization inline with the issuer waiting cannot be @Async callback — that pattern suits notifications, not an auth decision with an 80ms p99 SLA. I design a synchronous hot path: virtual threads or a small platform pool serving HTTP, total budget eighty milliseconds with ten milliseconds gateway overhead leaving seventy for the service. Decompose: Redis feature fetch pipelined targeting fifteen milliseconds, rules engine HTTP forty milliseconds with a thirty-five millisecond timeout and circuit breaker, local Caffeine for merchant risk tier about one millisecond on hit. Parallel CompletableFuture for independent features with orTimeout on a fifty millisecond total budget — cancel outstanding on breach; fail closed or approve with elevated risk per a documented policy signed by risk officers. No Kafka on the critical path — async only for audit via outbox after the response is sent. Connection pools: Redis lettuce pool fifty, rules HTTP pool one hundred per instance, bulkhead eighty concurrent scoring calls. Warm caches on startup; no lazy init on first request. Load test five hundred thousand per hour shape with Gatling proving p99; chaos inject rules engine two hundred millisecond latency and measure decline rate metric. On-call dashboard: sub-span latency, breaker state, Redis timeout rate.

**Common weak answers:** Accept @Async callback; unbounded parallelStream to rules; no timeout because rules are usually fast; put Kafka on the auth path for scalability.

**Follow-up probes (with answers):**

**Q:** Fail-open versus fail-closed when Redis is unavailable?
**A:** Fail-closed declines more transactions — revenue loss but fraud contained; fail-open approves — a business and regulatory choice documented and tested; never silent default without risk officer sign-off. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

**Q:** How do you prove 80ms in CI?
**A:** Performance test gate on main with a fixed load profile; compare p99 to baseline; profile JFR in the perf environment for lock or GC pauses — unit tests alone are insufficient. On-call, I capture evidence before restart, tie the fix to a measurable metric, and add a regression test or alert so the same failure mode is caught before the next SLO breach.

---
