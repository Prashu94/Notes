# Module 11: Thread Safety - Synchronization and Locks

## Table of Contents
1. [Thread Safety Fundamentals](#thread-safety-fundamentals)
2. [Race Conditions](#race-conditions)
3. [Synchronized Keyword](#synchronized-keyword)
4. [Volatile Keyword](#volatile-keyword)
5. [Atomic Variables](#atomic-variables)
6. [Lock Interface](#lock-interface)
7. [ReentrantLock](#reentrantlock)
8. [ReadWriteLock](#readwritelock)
9. [Best Practices](#best-practices)
10. [Summary and Exam Tips](#summary-and-exam-tips)

---

## Thread Safety Fundamentals

**Thread-safe** code produces correct results when accessed by multiple threads simultaneously.

### Thread Safety Issues

```java
class Counter {
    private int count = 0;
    
    // NOT thread-safe
    public void increment() {
        count++;  // Three operations: read, increment, write
    }
    
    public int getCount() {
        return count;
    }
}

// Race condition demonstration
Counter counter = new Counter();

Thread t1 = new Thread(() -> {
    for (int i = 0; i < 1000; i++) {
        counter.increment();
    }
});

Thread t2 = new Thread(() -> {
    for (int i = 0; i < 1000; i++) {
        counter.increment();
    }
});

t1.start();
t2.start();
t1.join();
t2.join();

System.out.println(counter.getCount()); // Expected: 2000, Actual: varies (1500-2000)
```

### Why Thread Safety Matters

```java
// Shared mutable state = danger
class BankAccount {
    private double balance = 1000;
    
    // NOT thread-safe
    public void withdraw(double amount) {
        if (balance >= amount) {
            // Context switch can happen here!
            balance -= amount;
        }
    }
}

// Two threads withdrawing simultaneously
BankAccount account = new BankAccount();

Thread t1 = new Thread(() -> account.withdraw(600));
Thread t2 = new Thread(() -> account.withdraw(600));

t1.start();
t2.start();
// Both threads see balance = 1000, both withdraw 600
// Final balance = -200 (should be 400 or 1000)
```

---

## Race Conditions

**Race condition**: Multiple threads access shared data, and outcome depends on execution timing.

### Example: Lost Updates

```java
class VisitorCounter {
    private int visitors = 0;
    
    // Race condition
    public void recordVisit() {
        int current = visitors;     // Thread 1: reads 0
                                     // Thread 2: reads 0
        visitors = current + 1;      // Thread 1: writes 1
                                     // Thread 2: writes 1 (should be 2!)
    }
}

// Demonstration
VisitorCounter counter = new VisitorCounter();

List<Thread> threads = new ArrayList<>();
for (int i = 0; i < 10; i++) {
    Thread t = new Thread(() -> {
        for (int j = 0; j < 1000; j++) {
            counter.recordVisit();
        }
    });
    threads.add(t);
    t.start();
}

for (Thread t : threads) {
    t.join();
}

System.out.println("Expected: 10000, Actual: " + counter.visitors);
// Actual: varies, always less than 10000
```

### Check-Then-Act Race Condition

```java
class LazyInitializer {
    private Resource resource;
    
    // Race condition
    public Resource getResource() {
        if (resource == null) {           // Thread 1: checks, null
                                           // Thread 2: checks, null
            resource = new Resource();     // Thread 1: creates
                                           // Thread 2: creates (duplicate!)
        }
        return resource;
    }
}
```

---

## Synchronized Keyword

**synchronized** provides **mutual exclusion** - only one thread executes synchronized code at a time.

### Synchronized Methods

```java
class Counter {
    private int count = 0;
    
    // Thread-safe: synchronized method
    public synchronized void increment() {
        count++;
    }
    
    public synchronized int getCount() {
        return count;
    }
}

// Usage
Counter counter = new Counter();

Thread t1 = new Thread(() -> {
    for (int i = 0; i < 1000; i++) {
        counter.increment();
    }
});

Thread t2 = new Thread(() -> {
    for (int i = 0; i < 1000; i++) {
        counter.increment();
    }
});

t1.start();
t2.start();
t1.join();
t2.join();

System.out.println(counter.getCount()); // Always 2000
```

### Synchronized Blocks

```java
class BankAccount {
    private double balance = 1000;
    private final Object lock = new Object();
    
    public void withdraw(double amount) {
        synchronized (lock) {
            if (balance >= amount) {
                balance -= amount;
            }
        }
    }
    
    public void deposit(double amount) {
        synchronized (lock) {
            balance += amount;
        }
    }
    
    public double getBalance() {
        synchronized (lock) {
            return balance;
        }
    }
}
```

### Static Synchronization

```java
class IdGenerator {
    private static int nextId = 0;
    
    // Synchronized on class object
    public static synchronized int generateId() {
        return nextId++;
    }
    
    // Equivalent to
    public static int generateId2() {
        synchronized (IdGenerator.class) {
            return nextId++;
        }
    }
}
```

### Intrinsic Locks

```java
class LockDemo {
    private int value = 0;
    
    // Locks on 'this'
    public synchronized void method1() {
        value++;
    }
    
    // Also locks on 'this'
    public void method2() {
        synchronized (this) {
            value++;
        }
    }
    
    // Different lock
    private final Object lock = new Object();
    public void method3() {
        synchronized (lock) {
            value++;
        }
    }
}
```

### Reentrancy

```java
class ReentrantDemo {
    private int count = 0;
    
    public synchronized void increment() {
        count++;
        if (count < 10) {
            increment();  // Reentrant: same thread can acquire lock again
        }
    }
}
```

---

## Volatile Keyword

**volatile** ensures **visibility** of variable changes across threads.

### Without Volatile

```java
class StopThread {
    private boolean stopRequested = false;  // NOT volatile
    
    public void run() {
        while (!stopRequested) {
            // Thread may cache stopRequested = false
            // Never sees update from other thread!
        }
        System.out.println("Stopped");
    }
    
    public void stop() {
        stopRequested = true;  // Update may not be visible
    }
}

// Thread may run forever!
StopThread task = new StopThread();
Thread thread = new Thread(task::run);
thread.start();
Thread.sleep(1000);
task.stop();  // Thread may never see this!
```

### With Volatile

```java
class StopThread {
    private volatile boolean stopRequested = false;  // VOLATILE
    
    public void run() {
        while (!stopRequested) {
            // Always reads from main memory
            // Sees updates immediately
        }
        System.out.println("Stopped");
    }
    
    public void stop() {
        stopRequested = true;  // Immediately visible to all threads
    }
}

// Works correctly
StopThread task = new StopThread();
Thread thread = new Thread(task::run);
thread.start();
Thread.sleep(1000);
task.stop();  // Thread sees this and stops
```

### Volatile vs Synchronized

```java
class VolatileDemo {
    // ✅ GOOD: volatile for flags
    private volatile boolean flag = false;
    
    public void setFlag(boolean value) {
        flag = value;  // Simple write - volatile sufficient
    }
    
    public boolean getFlag() {
        return flag;  // Simple read - volatile sufficient
    }
}

class SynchronizedDemo {
    // ✅ GOOD: synchronized for compound operations
    private int count = 0;  // NOT volatile
    
    public synchronized void increment() {
        count++;  // Read-modify-write - needs synchronization
    }
    
    public synchronized int getCount() {
        return count;
    }
}
```

### Volatile Limitations

```java
class VolatileLimitations {
    private volatile int count = 0;
    
    // ❌ NOT thread-safe even with volatile
    public void increment() {
        count++;  // Compound operation: read, increment, write
                  // Volatile doesn't make this atomic!
    }
    
    // ✅ Needs synchronization
    public synchronized void incrementSafe() {
        count++;
    }
}
```

---

## Atomic Variables

**Atomic classes** provide lock-free thread-safe operations on single variables.

### AtomicInteger

```java
import java.util.concurrent.atomic.AtomicInteger;

class Counter {
    private AtomicInteger count = new AtomicInteger(0);
    
    public void increment() {
        count.incrementAndGet();  // Atomic
    }
    
    public int getCount() {
        return count.get();
    }
}

// Usage
Counter counter = new Counter();

List<Thread> threads = new ArrayList<>();
for (int i = 0; i < 10; i++) {
    Thread t = new Thread(() -> {
        for (int j = 0; j < 1000; j++) {
            counter.increment();
        }
    });
    threads.add(t);
    t.start();
}

for (Thread t : threads) {
    t.join();
}

System.out.println(counter.getCount()); // Always 10000
```

### Common Atomic Operations

```java
AtomicInteger atomic = new AtomicInteger(0);

// Get and increment
int old = atomic.getAndIncrement();  // Returns old value, then increments

// Increment and get
int new = atomic.incrementAndGet();  // Increments, then returns new value

// Get and add
int old2 = atomic.getAndAdd(5);  // Adds 5, returns old value

// Add and get
int new2 = atomic.addAndGet(5);  // Adds 5, returns new value

// Compare and set
boolean success = atomic.compareAndSet(10, 20);  // If value is 10, set to 20

// Get and set
int old3 = atomic.getAndSet(100);  // Sets to 100, returns old value

// Update with function
atomic.updateAndGet(x -> x * 2);  // Doubles value

// Accumulate
atomic.accumulateAndGet(5, (current, update) -> current + update);
```

### Other Atomic Classes

```java
// AtomicLong
AtomicLong atomicLong = new AtomicLong(0);
atomicLong.incrementAndGet();

// AtomicBoolean
AtomicBoolean atomicBoolean = new AtomicBoolean(false);
boolean oldValue = atomicBoolean.getAndSet(true);

// AtomicReference
class Person {
    String name;
    Person(String name) { this.name = name; }
}

AtomicReference<Person> atomicRef = new AtomicReference<>(new Person("Alice"));
Person old = atomicRef.getAndSet(new Person("Bob"));

// Compare and swap
atomicRef.compareAndSet(old, new Person("Charlie"));
```

---

## Lock Interface

**Lock** provides more flexible locking than synchronized.

### Basic Lock Usage

```java
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

class Counter {
    private int count = 0;
    private Lock lock = new ReentrantLock();
    
    public void increment() {
        lock.lock();
        try {
            count++;
        } finally {
            lock.unlock();  // MUST unlock in finally
        }
    }
    
    public int getCount() {
        lock.lock();
        try {
            return count;
        } finally {
            lock.unlock();
        }
    }
}
```

### tryLock()

```java
class BankAccount {
    private double balance = 1000;
    private Lock lock = new ReentrantLock();
    
    public boolean transfer(BankAccount target, double amount) {
        // Try to acquire both locks
        if (this.lock.tryLock()) {
            try {
                if (target.lock.tryLock()) {
                    try {
                        this.balance -= amount;
                        target.balance += amount;
                        return true;
                    } finally {
                        target.lock.unlock();
                    }
                }
            } finally {
                this.lock.unlock();
            }
        }
        return false;  // Couldn't acquire locks
    }
    
    // tryLock with timeout
    public boolean transferWithTimeout(BankAccount target, double amount) 
            throws InterruptedException {
        if (this.lock.tryLock(1, TimeUnit.SECONDS)) {
            try {
                if (target.lock.tryLock(1, TimeUnit.SECONDS)) {
                    try {
                        this.balance -= amount;
                        target.balance += amount;
                        return true;
                    } finally {
                        target.lock.unlock();
                    }
                }
            } finally {
                this.lock.unlock();
            }
        }
        return false;
    }
}
```

---

## ReentrantLock

**ReentrantLock** is a reentrant mutual exclusion lock.

### Features

```java
import java.util.concurrent.locks.ReentrantLock;

class LockFeatures {
    private ReentrantLock lock = new ReentrantLock();
    
    public void demonstrateFeatures() {
        // Check if locked
        boolean isLocked = lock.isLocked();
        
        // Check if current thread holds lock
        boolean isHeldByCurrentThread = lock.isHeldByCurrentThread();
        
        // Get hold count (reentrant)
        lock.lock();
        lock.lock();  // Reentrant
        int holds = lock.getHoldCount();  // 2
        lock.unlock();
        lock.unlock();
        
        // Fair vs unfair lock
        ReentrantLock fairLock = new ReentrantLock(true);  // Fair
        ReentrantLock unfairLock = new ReentrantLock(false); // Unfair (default)
    }
}
```

### Condition Variables

```java
import java.util.concurrent.locks.Condition;

class BoundedBuffer<T> {
    private Queue<T> queue = new LinkedList<>();
    private int capacity;
    private ReentrantLock lock = new ReentrantLock();
    private Condition notFull = lock.newCondition();
    private Condition notEmpty = lock.newCondition();
    
    public BoundedBuffer(int capacity) {
        this.capacity = capacity;
    }
    
    public void put(T item) throws InterruptedException {
        lock.lock();
        try {
            while (queue.size() == capacity) {
                notFull.await();  // Wait until not full
            }
            queue.add(item);
            notEmpty.signal();  // Signal that queue is not empty
        } finally {
            lock.unlock();
        }
    }
    
    public T take() throws InterruptedException {
        lock.lock();
        try {
            while (queue.isEmpty()) {
                notEmpty.await();  // Wait until not empty
            }
            T item = queue.remove();
            notFull.signal();  // Signal that queue is not full
            return item;
        } finally {
            lock.unlock();
        }
    }
}
```

---

## ReadWriteLock

**ReadWriteLock** allows multiple readers or single writer.

### Basic Usage

```java
import java.util.concurrent.locks.ReadWriteLock;
import java.util.concurrent.locks.ReentrantReadWriteLock;

class SharedResource {
    private String data = "";
    private ReadWriteLock rwLock = new ReentrantReadWriteLock();
    
    // Multiple threads can read simultaneously
    public String read() {
        rwLock.readLock().lock();
        try {
            return data;
        } finally {
            rwLock.readLock().unlock();
        }
    }
    
    // Only one thread can write
    public void write(String newData) {
        rwLock.writeLock().lock();
        try {
            data = newData;
        } finally {
            rwLock.writeLock().unlock();
        }
    }
}
```

### Read-Heavy Workloads

```java
class Cache<K, V> {
    private Map<K, V> map = new HashMap<>();
    private ReadWriteLock lock = new ReentrantReadWriteLock();
    
    public V get(K key) {
        lock.readLock().lock();
        try {
            return map.get(key);  // Multiple readers allowed
        } finally {
            lock.readLock().unlock();
        }
    }
    
    public void put(K key, V value) {
        lock.writeLock().lock();
        try {
            map.put(key, value);  // Exclusive write access
        } finally {
            lock.writeLock().unlock();
        }
    }
    
    public void clear() {
        lock.writeLock().lock();
        try {
            map.clear();
        } finally {
            lock.writeLock().unlock();
        }
    }
}
```

---

## Best Practices

### 1. Always Unlock in Finally

```java
// ✅ GOOD
Lock lock = new ReentrantLock();
lock.lock();
try {
    // Critical section
} finally {
    lock.unlock();  // Always unlocks
}

// ❌ BAD
lock.lock();
// Critical section
lock.unlock();  // May not execute if exception thrown
```

### 2. Keep Synchronized Blocks Small

```java
// ❌ BAD - long critical section
public synchronized void processData() {
    readFromDatabase();      // Slow I/O
    performCalculation();    // CPU intensive
    writeToDatabase();       // Slow I/O
}

// ✅ GOOD - minimize critical section
public void processData() {
    Data data = readFromDatabase();
    Result result = performCalculation(data);
    
    synchronized (this) {
        // Only synchronize what's necessary
        updateSharedState(result);
    }
}
```

### 3. Use Atomic Variables for Simple Cases

```java
// ❌ BAD - synchronized for simple counter
private int count = 0;
public synchronized void increment() {
    count++;
}

// ✅ GOOD - atomic variable
private AtomicInteger count = new AtomicInteger(0);
public void increment() {
    count.incrementAndGet();
}
```

### 4. Prefer Higher-Level Utilities

```java
// ❌ BAD - manual synchronization
class ThreadSafeList<T> {
    private List<T> list = new ArrayList<>();
    
    public synchronized void add(T item) {
        list.add(item);
    }
}

// ✅ GOOD - use concurrent collection
import java.util.concurrent.CopyOnWriteArrayList;

List<T> list = new CopyOnWriteArrayList<>();
list.add(item);  // Thread-safe
```

---

## Summary and Exam Tips

### Key Concepts

- **synchronized**: Mutual exclusion, locks on object/class
- **volatile**: Visibility guarantee, no atomicity
- **Atomic classes**: Lock-free thread-safe operations
- **Lock**: More flexible than synchronized
- **ReadWriteLock**: Multiple readers, exclusive writer

### Comparison Table

| Feature | synchronized | volatile | Atomic | Lock |
|---------|--------------|----------|--------|------|
| Mutual Exclusion | ✅ | ❌ | ✅ | ✅ |
| Visibility | ✅ | ✅ | ✅ | ✅ |
| Compound Operations | ✅ | ❌ | ✅ | ✅ |
| tryLock | ❌ | ❌ | ❌ | ✅ |
| Interruptible | ❌ | ❌ | ❌ | ✅ |
| Fair/Unfair | Unfair | N/A | N/A | Both |

### Exam Tips

- `synchronized` locks on **this** (instance methods) or **Class object** (static methods)
- `volatile` ensures **visibility**, NOT **atomicity**
- `count++` is NOT atomic, even with volatile
- Always unlock in **finally** block
- `AtomicInteger.incrementAndGet()` is atomic
- `ReadWriteLock` allows **multiple readers** OR **single writer**
- `tryLock()` returns immediately, `lock()` blocks
- Reentrant lock can be acquired multiple times by same thread

---

**Previous:** [Practice Questions - Threads and Executors](29-practice-questions.md)  
**Next:** [Practice Questions - Thread Safety](30-practice-questions.md)
