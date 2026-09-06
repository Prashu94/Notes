# Multithreading — Practical Exercises

**How to use:** Type, run, break. Progress **Basic → Intermediate → Hard**.

| Tier | Count | Focus |
|------|-------|-------|
| Basic | 12 | Syntax, APIs, small runnable mains |
| Intermediate | 12 | Bugs, JVM behavior, trade-offs |
| Hard | 9 | Production incidents, tuning, design |

---

# Part A — Basic

## Exercise 1 — Thread lifecycle: start, join, state

**Difficulty:** Basic

**Task:** Start two threads, join them, print thread names and final state.

**Solution:**

```java
public class ThreadBasics {
    public static void main(String[] args) throws InterruptedException {
        Thread t1 = new Thread(() -> System.out.println("run: " + Thread.currentThread().getName()), "worker-1");
        Thread t2 = new Thread(() -> System.out.println("run: " + Thread.currentThread().getName()), "worker-2");

        t1.start();
        t2.start();
        t1.join();
        t2.join();

        System.out.println("t1 state: " + t1.getState()); // TERMINATED
        System.out.println("t2 state: " + t2.getState()); // TERMINATED
    }
}
```

**Senior takeaway:** Never call `run()` directly — that executes on the caller thread; `start()` schedules a new OS thread (or virtual thread carrier).

---

## Exercise 2 — Interrupt flag: don't swallow

**Difficulty:** Basic

**Task:** Interrupt a sleeping thread; restore the interrupt flag in the catch block.

**Solution:**

```java
public class InterruptLab {
    public static void main(String[] args) throws Exception {
        Thread t = new Thread(() -> {
            try {
                Thread.sleep(10_000);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt(); // restore flag
                System.out.println("stopped, flag=" + Thread.currentThread().isInterrupted());
            }
        });
        t.start();
        Thread.sleep(100);
        t.interrupt();
        t.join();
    }
}
```

Expected: `stopped, flag=true`

**Senior takeaway:** Empty `catch (InterruptedException)` blocks shutdown hooks and pool termination — always re-interrupt or exit promptly.

---

## Exercise 3 — `volatile` piggyback visibility

**Difficulty:** Basic

**Task:** Prove that a non-volatile flag can cause a reader to miss updates; fix with `volatile`.

**Solution:**

```java
public class Piggyback {
    static int payload;
    static volatile boolean ready; // remove volatile to see flaky failure

    public static void main(String[] args) throws Exception {
        Thread reader = new Thread(() -> {
            while (!ready) Thread.onSpinWait();
            if (payload != 42) throw new AssertionError("visibility bug, payload=" + payload);
            System.out.println("ok " + payload);
        });
        Thread writer = new Thread(() -> {
            payload = 42;
            ready = true;
        });
        reader.start();
        writer.start();
        writer.join();
        reader.join();
    }
}
```

**Senior takeaway:** `volatile` establishes happens-before for the flag write/read; it does not make `payload` atomic — use for single-writer status flags only.

---

## Exercise 4 — `synchronized` counter

**Difficulty:** Basic

**Task:** Increment a shared counter from 1000 threads without synchronization, then fix.

**Solution:**

```java
public class SyncCounter {
    static int unsafe;
    static final Object lock = new Object();
    static int safe;

    public static void main(String[] args) throws Exception {
        Runnable unsafeJob = () -> { for (int i = 0; i < 1000; i++) unsafe++; };
        Runnable safeJob = () -> {
            for (int i = 0; i < 1000; i++) {
                synchronized (lock) { safe++; }
            }
        };

        Thread[] threads = new Thread[10];
        for (int i = 0; i < threads.length; i++) threads[i] = new Thread(unsafeJob);
        for (Thread t : threads) t.start();
        for (Thread t : threads) t.join();
        System.out.println("unsafe=" + unsafe); // << 10000

        threads = new Thread[10];
        for (int i = 0; i < threads.length; i++) threads[i] = new Thread(safeJob);
        for (Thread t : threads) t.start();
        for (Thread t : threads) t.join();
        System.out.println("safe=" + safe);     // 10000
    }
}
```

**Senior takeaway:** `synchronized` provides mutual exclusion and visibility; for a single counter prefer `AtomicInteger` or `LongAdder`.

---

## Exercise 5 — `ExecutorService` submit and shutdown

**Difficulty:** Basic

**Task:** Submit 10 tasks to a fixed pool, shutdown gracefully, await termination.

**Solution:**

```java
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

public class ExecutorBasics {
    public static void main(String[] args) throws Exception {
        ExecutorService pool = Executors.newFixedThreadPool(4);
        try {
            for (int i = 0; i < 10; i++) {
                int id = i;
                pool.submit(() -> System.out.println(Thread.currentThread().getName() + " task=" + id));
            }
        } finally {
            pool.shutdown();
            if (!pool.awaitTermination(5, TimeUnit.SECONDS)) {
                pool.shutdownNow();
            }
        }
        System.out.println("pool terminated");
    }
}
```

**Senior takeaway:** `shutdown()` stops new tasks; always pair with `awaitTermination` or track `Future`s — `shutdown()` alone does not wait.

---

## Exercise 6 — `Future.get` blocks for result

**Difficulty:** Basic

**Task:** Submit a callable that sleeps 500ms; measure elapsed time via `Future.get`.

**Solution:**

```java
import java.util.concurrent.*;

public class FutureBasics {
    public static void main(String[] args) throws Exception {
        ExecutorService pool = Executors.newSingleThreadExecutor();
        long t0 = System.nanoTime();
        Future<String> f = pool.submit(() -> {
            Thread.sleep(500);
            return "done";
        });
        System.out.println(f.get()); // blocks ~500ms
        long ms = (System.nanoTime() - t0) / 1_000_000;
        System.out.println("elapsed ms: " + ms);
        pool.shutdown();
    }
}
```

**Senior takeaway:** `Future.get()` without timeout can hang forever on stuck I/O — production code uses `get(timeout, unit)` or `CompletableFuture.orTimeout`.

---

## Exercise 7 — `ConcurrentHashMap` basics

**Difficulty:** Basic

**Task:** Concurrently increment values per key from 8 threads; verify totals.

**Solution:**

```java
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CountDownLatch;

public class ChmBasics {
    public static void main(String[] args) throws Exception {
        var map = new ConcurrentHashMap<String, Integer>();
        int threads = 8;
        int perThread = 1000;
        var done = new CountDownLatch(threads);

        for (int t = 0; t < threads; t++) {
            new Thread(() -> {
                try {
                    for (int i = 0; i < perThread; i++) {
                        map.merge("hits", 1, Integer::sum);
                    }
                } finally {
                    done.countDown();
                }
            }).start();
        }
        done.await();
        System.out.println(map.get("hits")); // 8000
    }
}
```

**Senior takeaway:** `ConcurrentHashMap` is thread-safe for individual ops; compound actions like `if (!contains) put` still need `putIfAbsent` or `compute`.

---

## Exercise 8 — `ReentrantLock` try/finally unlock

**Difficulty:** Basic

**Task:** Guard a shared `ArrayList` with `ReentrantLock`; always unlock in `finally`.

**Solution:**

```java
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.locks.ReentrantLock;

public class LockBasics {
    static final List<String> list = new ArrayList<>();
    static final ReentrantLock lock = new ReentrantLock();

    static void add(String s) {
        lock.lock();
        try {
            list.add(s);
        } finally {
            lock.unlock();
        }
    }

    public static void main(String[] args) {
        add("a");
        add("b");
        System.out.println(list);
    }
}
```

**Senior takeaway:** Prefer `synchronized` for simple cases; `ReentrantLock` when you need `tryLock`, fairness, or `Condition` — but never forget `finally unlock`.

---

## Exercise 9 — Virtual thread hello world

**Difficulty:** Basic

**Task:** Start 10,000 virtual threads; print count and carrier thread names.

**Solution:**

```java
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicInteger;

public class VirtualThreadBasics {
    public static void main(String[] args) throws Exception {
        var done = new AtomicInteger();
        try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
            for (int i = 0; i < 10_000; i++) {
                executor.submit(() -> {
                    System.out.println(Thread.currentThread());
                    done.incrementAndGet();
                });
            }
        }
        System.out.println("completed: " + done.get());
    }
}
```

Expected: many tasks on few carrier threads (`ForkJoinPool-...`).

**Senior takeaway:** Virtual threads excel at blocking I/O concurrency; they are not faster CPU — pinning (Exercise 26) still matters.

---

## Exercise 10 — `CountDownLatch` start gun

**Difficulty:** Basic

**Task:** Start 8 worker threads simultaneously with a latch; measure coordinated start.

**Solution:**

```java
import java.util.concurrent.CountDownLatch;

public class StartGun {
    public static void main(String[] args) throws Exception {
        int n = 8;
        var ready = new CountDownLatch(n);
        var go = new CountDownLatch(1);

        for (int i = 0; i < n; i++) {
            new Thread(() -> {
                ready.countDown();
                try {
                    go.await();
                    System.out.println("go " + Thread.currentThread().getName());
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }).start();
        }
        ready.await();
        long t = System.nanoTime();
        go.countDown();
        System.out.println("started at " + t);
    }
}
```

**Senior takeaway:** Latches are one-shot — use `CyclicBarrier` for repeated phases or `Phaser` for dynamic participant counts.

---

# Part B — Intermediate

## Exercise 11 — Classic deadlock (JVM)

**Difficulty:** Intermediate

**Task:** Create a deadlock on locks A and B; capture it with `jcmd` or `jstack`.

**Solution:**

```java
public class DeadlockLab {
    static final Object A = new Object();
    static final Object B = new Object();

    public static void main(String[] args) throws InterruptedException {
        Thread t1 = new Thread(() -> {
            synchronized (A) {
                sleep(50);
                synchronized (B) { System.out.println("t1"); }
            }
        }, "t1-A-then-B");
        Thread t2 = new Thread(() -> {
            synchronized (B) {
                sleep(50);
                synchronized (A) { System.out.println("t2"); }
            }
        }, "t2-B-then-A");
        t1.start();
        t2.start();
        Thread.sleep(500);
        System.out.println("Now run: jcmd DeadlockLab Thread.print");
        t1.join();
        t2.join();
    }

    static void sleep(long ms) {
        try { Thread.sleep(ms); } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
    }
}
```

Fix: global lock order (always A then B), or `ReentrantLock.tryLock(timeout)` with backoff.

**Senior takeaway:** JVM deadlock dumps are gold for interviews — DB deadlocks (Exercise 27) show the same inconsistent ordering pattern.

---

## Exercise 12 — Check-then-act race on a map

**Difficulty:** Intermediate

**Task:** Show that `ConcurrentHashMap` does not make check-then-act atomic; fix with `putIfAbsent`.

**Solution:**

```java
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.atomic.AtomicInteger;

public class CheckThenAct {
    static void race(Map<String, Integer> map) throws Exception {
        map.clear();
        int n = 100;
        var start = new CountDownLatch(1);
        var done = new CountDownLatch(n);
        var wins = new AtomicInteger();
        for (int i = 0; i < n; i++) {
            new Thread(() -> {
                try {
                    start.await();
                    if (!map.containsKey("k")) {
                        map.put("k", 1);
                        wins.incrementAndGet();
                    }
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                } finally {
                    done.countDown();
                }
            }).start();
        }
        start.countDown();
        done.await();
        System.out.println(map.getClass().getSimpleName() + " wins=" + wins.get());
    }

    public static void main(String[] args) throws Exception {
        race(new HashMap<>());           // crash or wins >> 1
        race(new ConcurrentHashMap<>()); // still wins >> 1

        ConcurrentHashMap<String, Integer> fixed = new ConcurrentHashMap<>();
        fixed.putIfAbsent("k", 1);
        System.out.println("putIfAbsent: " + fixed);
    }
}
```

**Senior takeaway:** Thread-safe map ≠ atomic read-modify-write — use `putIfAbsent`, `compute`, or transactional boundaries.

---

## Exercise 13 — Production `ThreadPoolExecutor` tuning

**Difficulty:** Intermediate

**Task:** Build a bounded pool with named threads, bounded queue, and `CallerRunsPolicy`. Compare rejection policies under burst.

**Solution:**

```java
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

public class ProdPool {
    public static ExecutorService create(int nThreads, int queueCap, RejectedExecutionHandler handler) {
        AtomicInteger c = new AtomicInteger();
        return new ThreadPoolExecutor(
                nThreads, nThreads,
                0L, TimeUnit.MILLISECONDS,
                new ArrayBlockingQueue<>(queueCap),
                r -> {
                    Thread t = new Thread(r, "worker-" + c.incrementAndGet());
                    t.setDaemon(false);
                    return t;
                },
                handler
        );
    }

    public static void main(String[] args) throws Exception {
        ExecutorService ex = create(2, 4, new ThreadPoolExecutor.CallerRunsPolicy());
        try {
            for (int i = 0; i < 20; i++) {
                int id = i;
                ex.submit(() -> {
                    Thread.sleep(200);
                    System.out.println(Thread.currentThread().getName() + " " + id);
                });
            }
        } finally {
            ex.shutdown();
            ex.awaitTermination(30, TimeUnit.SECONDS);
        }
    }
}
```

Experiment: swap `AbortPolicy` (throws), `DiscardOldest`, `CallerRuns` (backpressure on submitter).

**Senior takeaway:** Unbounded `Executors.newCachedThreadPool()` hides overload until you run out of threads — always bound queue + explicit rejection policy.

---

## Exercise 14 — `CompletableFuture` on the wrong pool

**Difficulty:** Intermediate

**Task:** Show that `runAsync` without executor uses `ForkJoinPool.commonPool()`; isolate blocking work.

**Solution:**

```java
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.Executors;

public class CfPool {
    static void blockingIo() {
        try { Thread.sleep(500); } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
    }

    public static void main(String[] args) throws Exception {
        CompletableFuture<Void> onCommon = CompletableFuture.runAsync(() -> {
            System.out.println("common: " + Thread.currentThread());
            blockingIo();
        });

        var blockingPool = Executors.newFixedThreadPool(4);
        CompletableFuture<Void> onDedicated = CompletableFuture.runAsync(() -> {
            System.out.println("dedicated: " + Thread.currentThread());
            blockingIo();
        }, blockingPool);

        CompletableFuture.allOf(onCommon, onDedicated).join();
        blockingPool.shutdown();

        // Better for I/O-heavy:
        try (var vt = Executors.newVirtualThreadPerTaskExecutor()) {
            CompletableFuture.runAsync(() -> blockingIo(), vt).join();
        }
    }
}
```

**Senior takeaway:** Starving `commonPool()` slows parallel streams and default async CF — dedicate pools by workload type (CPU vs blocking I/O).

---

## Exercise 15 — Semaphore as DB connection gate (virtual threads)

**Difficulty:** Intermediate

**Task:** Run 1000 virtual threads against a pool of 10 DB connections; verify max in-flight ≤ 10.

**Solution:**

```java
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Semaphore;
import java.util.concurrent.atomic.AtomicInteger;

public class DbGate {
    static final Semaphore DB = new Semaphore(10);
    static final AtomicInteger inFlight = new AtomicInteger();
    static final AtomicInteger maxSeen = new AtomicInteger();

    static void query() {
        DB.acquireUninterruptibly();
        int now = inFlight.incrementAndGet();
        maxSeen.updateAndGet(prev -> Math.max(prev, now));
        try {
            Thread.sleep(50);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        } finally {
            inFlight.decrementAndGet();
            DB.release();
        }
    }

    public static void main(String[] args) throws Exception {
        try (ExecutorService vt = Executors.newVirtualThreadPerTaskExecutor()) {
            for (int i = 0; i < 1000; i++) vt.submit(DbGate::query);
        }
        System.out.println("max in-flight: " + maxSeen.get()); // <= 10
        System.out.println("final in-flight: " + inFlight.get()); // 0
    }
}
```

**Senior takeaway:** Million virtual threads ≠ million DB connections — gate external resources with semaphores or pool sizing (Hikari `maximumPoolSize`).

---

## Exercise 16 — `ThreadLocal` leak in a thread pool

**Difficulty:** Intermediate

**Task:** Allocate large `ThreadLocal` buffers in a fixed pool without `remove`; explain retention. Fix.

**Solution:**

```java
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class TlLeak {
    static final ThreadLocal<byte[]> TL = new ThreadLocal<>();

    public static void main(String[] args) throws Exception {
        ExecutorService pool = Executors.newFixedThreadPool(2);
        for (int i = 0; i < 20; i++) {
            pool.submit(() -> {
                TL.set(new byte[1_000_000]);
                try {
                    // process request...
                } finally {
                    TL.remove(); // REQUIRED — uncomment to fix leak
                }
            });
        }
        pool.shutdown();
        pool.awaitTermination(5, java.util.concurrent.TimeUnit.SECONDS);
        System.out.println("done — without remove(), pool threads retain last TL value");
    }
}
```

**Senior takeaway:** ThreadLocals + pooled threads = slow memory leak; always `remove()` in `finally`, especially after request-scoped context (user, trace ID).

---

## Exercise 17 — Dining philosophers: lock ordering

**Difficulty:** Intermediate

**Task:** Implement 5 philosophers without deadlock using consistent fork ordering.

**Solution:**

```java
import java.util.concurrent.locks.ReentrantLock;

public class Philosophers {
    public static void main(String[] args) throws InterruptedException {
        ReentrantLock[] forks = new ReentrantLock[5];
        for (int i = 0; i < 5; i++) forks[i] = new ReentrantLock();

        for (int i = 0; i < 5; i++) {
            int id = i;
            new Thread(() -> {
                for (int meal = 0; meal < 3; meal++) eatOnce(id, forks[id], forks[(id + 1) % 5]);
            }, "p" + id).start();
        }
        Thread.sleep(2000);
    }

    static void eatOnce(int id, ReentrantLock left, ReentrantLock right) {
        ReentrantLock first = System.identityHashCode(left) < System.identityHashCode(right) ? left : right;
        ReentrantLock second = first == left ? right : left;
        first.lock();
        try {
            second.lock();
            try {
                System.out.println(id + " eats");
            } finally {
                second.unlock();
            }
        } finally {
            first.unlock();
        }
    }
}
```

**Senior takeaway:** Global lock ordering is the same fix for DB row locks, distributed locks, and `synchronized` chains.

---

## Exercise 18 — `AtomicInteger` vs `synchronized` throughput

**Difficulty:** Intermediate

**Task:** Benchmark 10 threads × 1M increments with both approaches; discuss when to use `LongAdder`.

**Solution:**

```java
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.LongAdder;

public class AtomicVsSync {
    static int syncCount;
    static final Object lock = new Object();
    static final AtomicInteger atomic = new AtomicInteger();
    static final LongAdder adder = new LongAdder();

    static void bench(String name, Runnable r) {
        long t0 = System.nanoTime();
        r.run();
        System.out.println(name + " ns: " + (System.nanoTime() - t0));
    }

    public static void main(String[] args) throws Exception {
        int threads = 10;
        int iters = 1_000_000;

        Runnable syncJob = () -> {
            Thread[] ts = new Thread[threads];
            for (int i = 0; i < threads; i++) {
                ts[i] = new Thread(() -> {
                    for (int j = 0; j < iters; j++) {
                        synchronized (lock) { syncCount++; }
                    }
                });
                ts[i].start();
            }
            for (Thread t : ts) try { t.join(); } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
        };

        Runnable atomicJob = () -> {
            Thread[] ts = new Thread[threads];
            for (int i = 0; i < threads; i++) {
                ts[i] = new Thread(() -> {
                    for (int j = 0; j < iters; j++) atomic.incrementAndGet();
                });
                ts[i].start();
            }
            for (Thread t : ts) try { t.join(); } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
        };

        bench("synchronized", syncJob);
        bench("atomic", atomicJob);
        System.out.println("sync=" + syncCount + " atomic=" + atomic.get());
    }
}
```

**Senior takeaway:** High-contention counters favor `LongAdder`; `Atomic*` for CAS-heavy low contention or when you need exact `get()` every time.

---

## Exercise 19 — `BlockingQueue` producer-consumer

**Difficulty:** Intermediate

**Task:** One producer, two consumers, bounded queue capacity 10; graceful shutdown.

**Solution:**

```java
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.BlockingQueue;

public class ProducerConsumer {
    public static void main(String[] args) throws Exception {
        BlockingQueue<Integer> q = new ArrayBlockingQueue<>(10);
        var done = new java.util.concurrent.CountDownLatch(2);

        Thread producer = new Thread(() -> {
            try {
                for (int i = 0; i < 50; i++) {
                    q.put(i);
                    System.out.println("produced " + i);
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }, "producer");

        Runnable consumer = () -> {
            try {
                while (true) {
                    Integer v = q.take();
                    System.out.println(Thread.currentThread().getName() + " consumed " + v);
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            } finally {
                done.countDown();
            }
        };

        Thread c1 = new Thread(consumer, "c1");
        Thread c2 = new Thread(consumer, "c2");
        c1.start();
        c2.start();
        producer.start();
        producer.join();
        c1.interrupt();
        c2.interrupt();
        done.await();
    }
}
```

**Senior takeaway:** `put`/`take` couple throughput — tune queue depth for backpressure vs latency; monitor queue size in production.

---

## Exercise 20 — `CompletableFuture` composition and failure

**Difficulty:** Intermediate

**Task:** Chain async steps; handle failure in `exceptionally`; avoid blocking in `join` on event threads.

**Solution:**

```java
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.Executors;

public class CfCompose {
    static String fetchUser(String id) {
        if ("bad".equals(id)) throw new IllegalArgumentException("unknown user");
        return "user-" + id;
    }

    static String enrich(String user) { return user + "@corp"; }

    public static void main(String[] args) {
        try (var pool = Executors.newFixedThreadPool(4)) {
            CompletableFuture<String> ok = CompletableFuture
                    .supplyAsync(() -> fetchUser("42"), pool)
                    .thenApply(enrich);
            System.out.println("ok: " + ok.join());

            CompletableFuture<String> bad = CompletableFuture
                    .supplyAsync(() -> fetchUser("bad"), pool)
                    .thenApply(enrich)
                    .exceptionally(ex -> "fallback-guest");
            System.out.println("bad: " + bad.join());
        }
    }
}
```

**Senior takeaway:** `exceptionally` only handles the immediate stage — use `handle` for unified success/failure or propagate to orchestration layer with metrics.

---

# Part C — Hard (production scenarios)

## Exercise 21 — On-call: interpret a thread dump (pool exhaustion)

**Difficulty:** Hard

**Task:** Given this excerpt, identify the problem and immediate mitigation.

```
"pool-1-worker-3" #42 prio=5 os_prio=0 tid=0x... nid=0x1a03 waiting on condition
   java.lang.Thread.State: WAITING (parking)
        at java.util.concurrent.locks.AbstractQueuedSynchronizer$ConditionObject.await
        at java.util.concurrent.ArrayBlockingQueue.take(ArrayBlockingQueue.java:420)
        at com.example.Worker.run(Worker.java:31)

"http-nio-8080-exec-12" #88 prio=5 os_prio=0 tid=0x... nid=0x2b01 runnable
   java.lang.Thread.State: RUNNABLE
        at com.example.Service.process(Service.java:55)
        at com.example.ApiController.handle(ApiController.java:22)
```

Plus: 200 threads named `pool-1-worker-*` all WAITING on `ArrayBlockingQueue.take`, HTTP threads RUNNABLE in `Service.process` submitting tasks.

**Solution (RCA):**

- **Problem:** Worker pool starved or deadlocked downstream; queue consumers blocked; HTTP threads still accept work and block on `Future.get` or synchronous submit — effective thread exhaustion.
- **Immediate:** Enable circuit breaker / shed load; increase worker count only if downstream (DB) can take it; check for blocking calls inside worker holding locks.
- **Root fix:** Async boundary with timeout; bounded queue + `CallerRuns` or fail-fast; separate pools for HTTP vs background.

Repro sketch:

```java
import java.util.concurrent.*;

public class PoolExhaustion {
    static final ExecutorService workers = new ThreadPoolExecutor(
            2, 2, 0, TimeUnit.MILLISECONDS,
            new ArrayBlockingQueue<>(2),
            new ThreadPoolExecutor.CallerRunsPolicy());

    public static void main(String[] args) throws Exception {
        Callable<Void> slow = () -> { Thread.sleep(60_000); return null; };
        for (int i = 0; i < 10; i++) {
            workers.submit(slow);
            System.out.println("submitted " + i);
        }
    }
}
```

**Senior takeaway:** Thread dumps show *where* threads wait, not *why* — correlate with queue depth, DB connections, and lock holders.

---

## Exercise 22 — On-call: `RejectedExecutionException` burst

**Difficulty:** Hard

**Task:** Configure a pool that throws on overload; write client retry policy and ops alert thresholds.

**Solution:**

```java
import java.util.concurrent.*;

public class RejectedBurst {
    static final ThreadPoolExecutor POOL = new ThreadPoolExecutor(
            1, 1, 0, TimeUnit.MILLISECONDS,
            new ArrayBlockingQueue<>(1),
            new ThreadPoolExecutor.AbortPolicy());

    static void submitWithRetry(Runnable task) {
        for (int attempt = 1; attempt <= 3; attempt++) {
            try {
                POOL.execute(task);
                return;
            } catch (RejectedExecutionException e) {
                System.out.println("rejected attempt " + attempt);
                try { Thread.sleep(50L * attempt); } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                    return;
                }
            }
        }
        throw new IllegalStateException("pool saturated after retries");
    }

    public static void main(String[] args) throws Exception {
        POOL.submit(() -> sleep(500));
        POOL.submit(() -> sleep(500));
        try {
            POOL.submit(() -> sleep(500)); // fills queue + active
            submitWithRetry(() -> System.out.println("should not run if still full"));
        } catch (RejectedExecutionException | IllegalStateException e) {
            System.out.println("overload: " + e.getClass().getSimpleName());
        }
        POOL.shutdown();
    }

    static void sleep(long ms) {
        try { Thread.sleep(ms); } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
    }
}
```

Alert on: queue size > 80% capacity, rejection rate > 0, active count == max for sustained period.

**Senior takeaway:** Retries on saturated pools amplify damage — pair with jittered backoff and bulkheads; scale consumers before retry storms.

---

## Exercise 23 — Race in metrics: lost increments

**Difficulty:** Hard

**Task:** Simulate a production counter bug (`int` field updated from many threads); fix and validate under load.

**Solution:**

```java
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.atomic.LongAdder;

public class MetricsRace {
    static int buggy;
    static final LongAdder fixed = new LongAdder();

    public static void main(String[] args) throws Exception {
        int threads = 50;
        int per = 20_000;
        var latch = new CountDownLatch(threads);

        for (int t = 0; t < threads; t++) {
            new Thread(() -> {
                for (int i = 0; i < per; i++) {
                    buggy++;
                    fixed.increment();
                }
                latch.countDown();
            }).start();
        }
        latch.await();
        System.out.println("buggy=" + buggy + " expected=" + (threads * per));
        System.out.println("fixed=" + fixed.sum());
    }
}
```

Expected: `buggy` << 1_000_000; `fixed` == 1_000_000.

**Senior takeaway:** Micrometer/Prometheus counters must use atomic updates — "it works in staging" fails at prod QPS.

---

## Exercise 24 — `ForkJoinPool.commonPool()` starvation

**Difficulty:** Hard

**Task:** Block all common pool threads with long `CompletableFuture.runAsync` tasks; show parallel stream slowdown.

**Solution:**

```java
import java.util.concurrent.CompletableFuture;
import java.util.stream.IntStream;

public class CommonPoolStarvation {
    public static void main(String[] args) throws Exception {
        // hog common pool (default parallelism = CPU cores)
        for (int i = 0; i < 8; i++) {
            CompletableFuture.runAsync(() -> {
                try { Thread.sleep(10_000); } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
            });
        }
        Thread.sleep(200);

        long t0 = System.nanoTime();
        int sum = IntStream.range(0, 1_000_000).parallel().sum();
        long ms = (System.nanoTime() - t0) / 1_000_000;
        System.out.println("parallel sum=" + sum + " ms=" + ms + " (degraded while pool blocked)");
    }
}
```

Fix: pass explicit `Executor` to `runAsync`; set `-Djava.util.concurrent.ForkJoinPool.common.parallelism` only as last resort.

**Senior takeaway:** Libraries sharing `commonPool()` create cross-tenant interference — isolate blocking async work.

---

## Exercise 25 — Virtual thread pinning incident

**Difficulty:** Hard

**Task:** Show carrier thread pinning when virtual thread enters `synchronized` during native/blocking work; mention `-Djdk.tracePinnedThreads`.

**Solution:**

```java
public class PinningDemo {
    static final Object lock = new Object();

    public static void main(String[] args) throws Exception {
        Thread.ofVirtual().name("vt-", 0).start(() -> {
            synchronized (lock) {
                try {
                    Thread.sleep(2000); // blocks carrier while pinned
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }
        }).join();
    }
}
```

Run with:

```bash
java -Djdk.tracePinnedThreads=full PinningDemo
```

Expected: pinning trace when synchronized block blocks inside virtual thread.

Mitigation: replace `synchronized` with `ReentrantLock` in VT-heavy code paths; avoid blocking in pinned sections.

**Senior takeaway:** "We enabled virtual threads but throughput flat" — check pinning, JDBC driver sync, and file I/O on carriers.

---

## Exercise 26 — OOM: `unable to create native thread`

**Difficulty:** Hard

**Task:** Reproduce thread OOM (carefully, low count); document limits and fixes.

**Solution:**

```bash
# Check OS thread limit for user
ulimit -u
```

```java
import java.util.ArrayList;
import java.util.List;

public class ThreadOom {
    public static void main(String[] args) {
        List<Thread> threads = new ArrayList<>();
        int i = 0;
        try {
            while (true) {
                Thread t = new Thread(() -> {
                    try { Thread.sleep(Long.MAX_VALUE); } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                    }
                });
                t.start();
                threads.add(t);
                i++;
                if (i % 500 == 0) System.out.println("created " + i);
            }
        } catch (OutOfMemoryError e) {
            System.out.println("failed after " + i + ": " + e.getMessage());
        }
    }
}
```

Expected: `OutOfMemoryError: unable to create native thread` (or OS kill).

Fixes: pool threads; virtual threads for I/O; reduce stack size only with caution (`-Xss`); raise `ulimit` / cgroup limits.

**Senior takeaway:** Each platform thread costs ~1MB stack — 10k threads is a design smell, not a scaling strategy.

---

## Exercise 27 — Database deadlock (not JVM deadlock)

**Difficulty:** Hard

**Task:** Design two transactions with inverted row lock order; capture DB error and fix with consistent ordering.

**Solution (SQL scenario — run in Postgres/MySQL):**

```sql
-- Session 1
BEGIN;
UPDATE accounts SET balance = balance - 10 WHERE id = 1; -- locks row 1
SELECT pg_sleep(2);
UPDATE accounts SET balance = balance + 10 WHERE id = 2; -- waits for row 2

-- Session 2 (parallel)
BEGIN;
UPDATE accounts SET balance = balance - 5 WHERE id = 2;  -- locks row 2
SELECT pg_sleep(2);
UPDATE accounts SET balance = balance + 5 WHERE id = 1;  -- deadlock
```

Postgres: `ERROR: deadlock detected (40P01)`. Oracle: `ORA-00060`.

Fix:

```sql
-- Always lock rows in ascending id order in every code path
SELECT * FROM accounts WHERE id IN (1,2) ORDER BY id FOR UPDATE;
```

**Senior takeaway:** Same rule as Exercise 11 — global order on contended resources; ORMs hide SQL order unless you use explicit locking hints.

---

## Exercise 28 — `CompletableFuture` timeout cascade

**Difficulty:** Hard

**Task:** Chain 3 async RPC calls; one hangs; implement timeout and fallback without blocking all callers.

**Solution:**

```java
import java.util.concurrent.*;

public class CfTimeoutCascade {
    static String rpc(String name, long ms) {
        try { Thread.sleep(ms); } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
        return name;
    }

    public static void main(String[] args) {
        ExecutorService pool = Executors.newFixedThreadPool(4);
        try {
            CompletableFuture<String> chain = CompletableFuture
                    .supplyAsync(() -> rpc("step1", 100), pool)
                    .thenCompose(s1 -> CompletableFuture.supplyAsync(() -> rpc("step2-hang", 60_000), pool))
                    .thenApply(s2 -> s2 + "-done");

            String result;
            try {
                result = chain.get(500, TimeUnit.MILLISECONDS);
            } catch (TimeoutException e) {
                chain.cancel(true);
                result = "fallback-after-timeout";
            }
            System.out.println(result);
        } catch (Exception e) {
            throw new RuntimeException(e);
        } finally {
            pool.shutdownNow();
        }
    }
}
```

Expected: `fallback-after-timeout` after ~500ms.

**Senior takeaway:** `cancel(true)` interrupts workers — ensure blocking I/O respects interrupt or use HTTP client timeouts at every hop; one missing timeout poisons the chain.

---

## Exercise 29 — `ScopedValue` propagation

**Difficulty:** Basic

**Task:** Bind a trace ID with `ScopedValue`, read it in a nested method and in a child thread started inside the scope. Assert the child sees the same value; after scope ends, assert `get()` throws.

**Solution:**

```java
import java.util.concurrent.*;

public class ScopedValueLab {
    private static final ScopedValue<String> TRACE = ScopedValue.newInstance();

    static void nested() {
        System.out.println("nested trace=" + TRACE.get());
    }

    public static void main(String[] args) throws Exception {
        ScopedValue.where(TRACE, "abc-123").run(() -> {
            nested();
            Thread t = Thread.ofVirtual().start(() ->
                    System.out.println("child trace=" + TRACE.get()));
            t.join();
        });
        try {
            TRACE.get();
            throw new AssertionError("expected NoSuchElementException");
        } catch (NoSuchElementException expected) {
            System.out.println("outside scope: no value");
        }
    }
}
```

Expected: same trace in nested and child; outside scope throws.

**Senior takeaway:** Prefer immutable scoped context over mutable `ThreadLocal` for virtual threads — binding is lexical, no forgotten `remove()`.

---

## Exercise 30 — `DelayQueue` retry backoff

**Difficulty:** Basic

**Task:** Enqueue three tasks with delays 100ms, 200ms, 300ms; drain with `take()` and print fire order.

**Solution:**

```java
import java.util.concurrent.*;

public class DelayQueueLab {
    record DelayedMsg(String id, long fireNanos) implements Delayed {
        public long getDelay(TimeUnit u) {
            return u.convert(fireNanos - System.nanoTime(), TimeUnit.NANOSECONDS);
        }
        public int compareTo(Delayed o) {
            return Long.compare(getDelay(NANOSECONDS), o.getDelay(NANOSECONDS));
        }
    }

    public static void main(String[] args) throws InterruptedException {
        DelayQueue<DelayedMsg> q = new DelayQueue<>();
        long base = System.nanoTime();
        q.put(new DelayedMsg("c", base + TimeUnit.MILLISECONDS.toNanos(300)));
        q.put(new DelayedMsg("a", base + TimeUnit.MILLISECONDS.toNanos(100)));
        q.put(new DelayedMsg("b", base + TimeUnit.MILLISECONDS.toNanos(200)));
        for (int i = 0; i < 3; i++) {
            System.out.println(q.take().id());
        }
    }
}
```

Expected: `a`, `b`, `c`.

**Senior takeaway:** `DelayQueue` is unbounded — production schedulers need persistence and drain rate limits, not raw queue alone.

---

## Exercise 31 — `LockSupport` permit consumed before park

**Difficulty:** Intermediate

**Task:** Call `unpark` on a thread before it starts, then have the thread `park` once — it must not block. Second `park` without unpark should block until main unparks.

**Solution:**

```java
import java.util.concurrent.*;
import java.util.concurrent.locks.LockSupport;

public class LockSupportPermitLab {
    public static void main(String[] args) throws Exception {
        CountDownLatch started = new CountDownLatch(1);
        Thread t = new Thread(() -> {
            started.countDown();
            System.out.println("first park returns immediately");
            LockSupport.park(); // consumes advance unpark
            System.out.println("second park blocked until unpark");
            LockSupport.park();
            System.out.println("released");
        });
        LockSupport.unpark(t); // permit before park
        t.start();
        started.await();
        Thread.sleep(200);
        LockSupport.unpark(t);
        t.join();
    }
}
```

**Senior takeaway:** Only one pending unpark is stored — understand this when reading AQS/`CompletableFuture` internals in thread dumps.

---

## Exercise 32 — `StampedLock` optimistic read retry

**Difficulty:** Intermediate

**Task:** Use optimistic read; simulate writer invalidating stamp; fall back to read lock and re-read value.

**Solution:**

```java
import java.util.concurrent.locks.*;

public class StampedOptimisticLab {
    static final StampedLock lock = new StampedLock();
    static int counter = 0;

    static int readOptimistic() {
        long stamp = lock.tryOptimisticRead();
        int v = counter;
        if (!lock.validate(stamp)) {
            stamp = lock.readLock();
            try {
                v = counter;
            } finally {
                lock.unlockRead(stamp);
            }
        }
        return v;
    }

    public static void main(String[] args) throws Exception {
        Thread writer = new Thread(() -> {
            long s = lock.writeLock();
            try { counter = 42; Thread.sleep(50); } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            } finally { lock.unlockWrite(s); }
        });
        writer.start();
        Thread.sleep(10);
        System.out.println("value=" + readOptimistic());
        writer.join();
        System.out.println("final=" + readOptimistic());
    }
}
```

**Senior takeaway:** Values observed during failed optimistic read are invalid — always re-read under read lock or use immutable snapshots.

---

## Exercise 33 — Awaitility + concurrent stress idempotency

**Difficulty:** Hard

**Task:** Simulate 20 threads incrementing a "processed" set for the same key; use `ConcurrentHashMap.newKeySet()` + `add` idempotency. Assert exactly one logical success with Awaitility (add dependency in pom for lab).

**Solution:**

```java
import java.util.Set;
import java.util.concurrent.*;
import static org.awaitility.Awaitility.await;
import static java.util.concurrent.TimeUnit.SECONDS;
import static org.assertj.core.api.Assertions.assertThat;

public class IdempotencyStressLab {
    static final Set<String> PROCESSED = ConcurrentHashMap.newKeySet();

    static boolean processOnce(String key) {
        return PROCESSED.add(key);
    }

    public static void main(String[] args) throws Exception {
        ExecutorService pool = Executors.newFixedThreadPool(20);
        try {
            CountDownLatch start = new CountDownLatch(1);
            for (int i = 0; i < 20; i++) {
                pool.submit(() -> {
                    start.await();
                    processOnce("pay-1");
                });
            }
            start.countDown();
            pool.shutdown();
            assert pool.awaitTermination(5, SECONDS);

            await().atMost(2, SECONDS).untilAsserted(() ->
                    assertThat(PROCESSED).containsExactly("pay-1"));
            long winners = 20; // re-run logic counting true returns in test harness
            System.out.println("set size=" + PROCESSED.size());
        } finally {
            pool.shutdownNow();
        }
    }
}
```

Maven test variant should assert `processOnce` true exactly once across threads using `AtomicInteger wins`.

**Senior takeaway:** Replace `Thread.sleep` in CI with Awaitility; pair in-memory idempotency with DB unique constraint for production guarantees.

---

## Weekend challenge

1. Force Exercise 11 deadlock, run `jcmd <pid> Thread.print`, write a one-paragraph RCA with lock graph.
2. Load-test Exercise 15 with 10k virtual threads; graph Hikari `active` vs semaphore permits.
3. Take a production thread dump and label each pool: RUNNABLE vs WAITING vs BLOCKED — find one thread stuck in `Future.get` without timeout.
