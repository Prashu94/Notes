# Module 11: Practice Questions - Thread Safety

## Questions (20)

---

### Question 1
```java
class Counter {
    private int count = 0;
    
    public void increment() {
        count++;
    }
}
```
Is this thread-safe?

**A)** Yes  
**B)** No - needs synchronized  
**C)** Yes if count is volatile  
**D)** Depends on JVM

**Answer: B)**

**Explanation:** `count++` is three operations (read, increment, write). Multiple threads can interleave, causing lost updates. Needs **synchronized** or **Atomic**.

```java
// Fix 1: synchronized
public synchronized void increment() {
    count++;
}

// Fix 2: AtomicInteger
private AtomicInteger count = new AtomicInteger(0);
public void increment() {
    count.incrementAndGet();
}
```

---

### Question 2
```java
class Flag {
    private boolean stop = false;
    
    public void setStop() {
        stop = true;
    }
    
    public boolean isStop() {
        return stop;
    }
}
```
What's the problem?

**A)** No problem  
**B)** Needs synchronized  
**C)** stop should be volatile  
**D)** Needs AtomicBoolean

**Answer: C)**

**Explanation:** Threads may **cache** `stop` value. Changes may not be visible. Use **volatile** for visibility.

```java
private volatile boolean stop = false;
```

---

### Question 3
```java
class Counter {
    private volatile int count = 0;
    
    public void increment() {
        count++;
    }
}
```
Is this thread-safe?

**A)** Yes - volatile ensures thread safety  
**B)** No - volatile doesn't make count++ atomic  
**C)** Yes if single threaded  
**D)** Compilation error

**Answer: B)**

**Explanation:** **volatile** ensures visibility, NOT atomicity. `count++` is still compound operation (not atomic).

---

### Question 4
```java
class Demo {
    private int x = 0;
    
    public synchronized void method1() {
        x++;
    }
    
    public void method2() {
        synchronized (this) {
            x++;
        }
    }
}
```
What's true about the locks?

**A)** Different locks  
**B)** Same lock (this)  
**C)** method1 locks on class, method2 on instance  
**D)** Compilation error

**Answer: B)**

**Explanation:** Both lock on **this**. `synchronized` method locks on instance (`this`).

---

### Question 5
```java
AtomicInteger atomic = new AtomicInteger(0);
atomic.incrementAndGet();
```
What value does `incrementAndGet()` return?

**A)** 0  
**B)** 1  
**C)** Depends on thread count  
**D)** Compilation error

**Answer: B)**

**Explanation:** `incrementAndGet()` increments **then returns new value**. 0 → 1, returns **1**.

```java
getAndIncrement(); // Returns old value (0), then increments
incrementAndGet(); // Increments, then returns new value (1)
```

---

### Question 6
```java
Lock lock = new ReentrantLock();
lock.lock();
// Critical section
lock.unlock();
```
What's wrong?

**A)** Nothing  
**B)** Should use synchronized  
**C)** unlock() should be in finally  
**D)** Needs tryLock()

**Answer: C)**

**Explanation:** If exception occurs, `unlock()` won't execute. **Always unlock in finally**.

```java
lock.lock();
try {
    // Critical section
} finally {
    lock.unlock();
}
```

---

### Question 7
```java
ReadWriteLock rwLock = new ReentrantReadWriteLock();
rwLock.readLock().lock();
rwLock.readLock().lock();
```
What happens?

**A)** Deadlock  
**B)** IllegalMonitorStateException  
**C)** Works - reentrant  
**D)** Second lock blocks

**Answer: C)**

**Explanation:** ReadWriteLock is **reentrant**. Same thread can acquire read lock multiple times.

---

### Question 8
```java
class Demo {
    private static int x = 0;
    
    public static synchronized void increment() {
        x++;
    }
}
```
What lock does `increment()` acquire?

**A)** this  
**B)** Demo.class  
**C)** x  
**D)** No lock

**Answer: B)**

**Explanation:** **Static synchronized** methods lock on **Class object** (`Demo.class`).

---

### Question 9
```java
AtomicInteger count = new AtomicInteger(10);
boolean result = count.compareAndSet(10, 20);
System.out.println(count.get());
```
What is printed?

**A)** 10  
**B)** 20  
**C)** true  
**D)** false

**Answer: B)**

**Explanation:** `compareAndSet(10, 20)` checks if value is 10 (yes), sets to 20. Prints **20**.

---

### Question 10
```java
Lock lock = new ReentrantLock();
if (lock.tryLock()) {
    try {
        // Critical section
    } finally {
        lock.unlock();
    }
}
```
When does `tryLock()` return false?

**A)** Never  
**B)** If lock held by another thread  
**C)** If lock held by current thread  
**D)** Always

**Answer: B)**

**Explanation:** `tryLock()` returns **false** if lock is **already held** by another thread. Returns **true** if acquired.

---

### Question 11
```java
class Demo {
    public synchronized void method1() {
        method2();
    }
    
    public synchronized void method2() {
        System.out.println("OK");
    }
}
```
What happens when thread calls `method1()`?

**A)** Deadlock  
**B)** Prints "OK"  
**C)** IllegalMonitorStateException  
**D)** Blocks indefinitely

**Answer: B)**

**Explanation:** Synchronized methods are **reentrant**. Same thread can acquire same lock multiple times. Prints **"OK"**.

---

### Question 12
```java
volatile int x = 0;
volatile int y = 0;

// Thread 1
x = 1;
y = 1;

// Thread 2
if (y == 1) {
    assert x == 1;
}
```
Can the assertion fail?

**A)** Yes  
**B)** No - volatile prevents reordering  
**C)** Only in Java 8  
**D)** Compilation error

**Answer: B)**

**Explanation:** **volatile** provides **happens-before** guarantee. If Thread 2 sees `y == 1`, it sees `x == 1` too.

---

### Question 13
```java
Lock lock = new ReentrantLock();
lock.lock();
lock.lock();
lock.unlock();
```
What is the lock state?

**A)** Unlocked  
**B)** Locked  
**C)** IllegalMonitorStateException  
**D)** Deadlock

**Answer: B)**

**Explanation:** Lock acquired **twice** (reentrant), unlocked **once**. Hold count = 1, still **locked**.

```java
lock.lock();   // Hold count = 1
lock.lock();   // Hold count = 2
lock.unlock(); // Hold count = 1 (still locked)
lock.unlock(); // Hold count = 0 (unlocked)
```

---

### Question 14
```java
ReadWriteLock rwLock = new ReentrantReadWriteLock();

// Thread 1
rwLock.readLock().lock();

// Thread 2
rwLock.readLock().lock();
```
What happens to Thread 2?

**A)** Blocks  
**B)** Acquires lock (multiple readers allowed)  
**C)** IllegalMonitorStateException  
**D)** Deadlock

**Answer: B)**

**Explanation:** **Multiple readers** can acquire read lock simultaneously. Thread 2 acquires lock.

---

### Question 15
```java
ReadWriteLock rwLock = new ReentrantReadWriteLock();

// Thread 1
rwLock.readLock().lock();

// Thread 2
rwLock.writeLock().lock();
```
What happens to Thread 2?

**A)** Acquires lock  
**B)** Blocks (waits for read lock release)  
**C)** IllegalMonitorStateException  
**D)** Returns false

**Answer: B)**

**Explanation:** **Write lock** is exclusive. Thread 2 **blocks** until read lock is released.

---

### Question 16
```java
AtomicBoolean flag = new AtomicBoolean(false);
boolean old = flag.getAndSet(true);
System.out.println(old);
```
What is printed?

**A)** true  
**B)** false  
**C)** null  
**D)** Compilation error

**Answer: B)**

**Explanation:** `getAndSet(true)` returns **old value** (false), then sets to true. Prints **false**.

---

### Question 17
```java
Lock lock = new ReentrantLock();
boolean acquired = lock.tryLock(2, TimeUnit.SECONDS);
```
What does this do?

**A)** Returns immediately  
**B)** Waits up to 2 seconds to acquire lock  
**C)** Waits exactly 2 seconds  
**D)** Compilation error

**Answer: B)**

**Explanation:** `tryLock(timeout)` waits **up to** specified time to acquire lock. Returns true if acquired, false if timeout.

---

### Question 18
```java
class Demo {
    private int x = 0;
    private Object lock = new Object();
    
    public void method1() {
        synchronized (lock) {
            x++;
        }
    }
    
    public synchronized void method2() {
        x++;
    }
}
```
Can `method1()` and `method2()` execute simultaneously?

**A)** No  
**B)** Yes - different locks  
**C)** Only if called by different threads  
**D)** Compilation error

**Answer: B)**

**Explanation:** `method1()` locks on `lock` object. `method2()` locks on `this`. **Different locks**, can execute simultaneously.

---

### Question 19
```java
AtomicInteger count = new AtomicInteger(5);
int result = count.updateAndGet(x -> x * 2);
System.out.println(result);
```
What is printed?

**A)** 5  
**B)** 10  
**C)** 15  
**D)** Compilation error

**Answer: B)**

**Explanation:** `updateAndGet(x -> x * 2)` updates value (5 * 2 = 10) and returns new value. Prints **10**.

---

### Question 20
```java
class Counter {
    private int count = 0;
    
    public synchronized int increment() {
        return ++count;
    }
    
    public int getCount() {
        return count;
    }
}
```
Is this thread-safe?

**A)** Yes  
**B)** No - getCount() not synchronized  
**C)** Yes if count is volatile  
**D)** Only for single-threaded use

**Answer: B)**

**Explanation:** `getCount()` is **not synchronized**. May return stale value or see partial update. Should be synchronized.

```java
public synchronized int getCount() {
    return count;
}
```

---

## Score Interpretation

- **18-20 correct**: Excellent! You master thread safety.
- **15-17 correct**: Good understanding. Review volatile vs synchronized.
- **12-14 correct**: Fair grasp. Study atomic variables and locks.
- **Below 12**: Need more practice. Review all synchronization mechanisms.

---

**Previous:** [Theory - Thread Safety](30-thread-safety.md)  
**Next:** [Theory - Concurrent Collections](31-concurrent-collections.md)
