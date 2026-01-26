# Module 11: Concurrent Collections

## Table of Contents
1. [Introduction to Concurrent Collections](#introduction-to-concurrent-collections)
2. [ConcurrentHashMap](#concurrenthashmap)
3. [CopyOnWriteArrayList](#copyonwritearraylist)
4. [CopyOnWriteArraySet](#copyonwritearrayset)
5. [ConcurrentLinkedQueue](#concurrentlinkedqueue)
6. [BlockingQueue Implementations](#blockingqueue-implementations)
7. [ConcurrentSkipListMap and ConcurrentSkipListSet](#concurrentskiplistmap-and-concurrentskiplistset)
8. [Thread-Safe Collections Comparison](#thread-safe-collections-comparison)
9. [Best Practices](#best-practices)
10. [Summary and Exam Tips](#summary-and-exam-tips)

---

## Introduction to Concurrent Collections

**Concurrent collections** are thread-safe collections designed for concurrent access without external synchronization.

### Why Not Collections.synchronizedXxx()?

```java
// ❌ BAD: Synchronized wrapper
List<String> list = Collections.synchronizedList(new ArrayList<>());

// Entire collection locked for each operation
list.add("A");  // Locks entire list
list.get(0);    // Locks entire list
// Poor performance under high concurrency

// Also requires external synchronization for iteration
synchronized (list) {
    for (String s : list) {
        System.out.println(s);
    }
}

// ✅ GOOD: Concurrent collection
List<String> concurrentList = new CopyOnWriteArrayList<>();
concurrentList.add("A");  // Lock-free
concurrentList.get(0);    // Lock-free
// Safe iteration without external synchronization
for (String s : concurrentList) {
    System.out.println(s);
}
```

### Common Concurrent Collections

| Collection | Description | Best Use Case |
|------------|-------------|---------------|
| `ConcurrentHashMap` | Lock-striped hash map | General-purpose concurrent map |
| `CopyOnWriteArrayList` | Copy-on-write list | Read-heavy, rare writes |
| `CopyOnWriteArraySet` | Copy-on-write set | Read-heavy, rare writes |
| `ConcurrentLinkedQueue` | Lock-free queue | Producer-consumer |
| `LinkedBlockingQueue` | Blocking queue | Producer-consumer with blocking |
| `ArrayBlockingQueue` | Bounded blocking queue | Fixed-size buffer |
| `PriorityBlockingQueue` | Priority queue | Task scheduling |
| `ConcurrentSkipListMap` | Sorted concurrent map | Concurrent sorted map |

---

## ConcurrentHashMap

**ConcurrentHashMap** is a thread-safe hash map with better concurrency than synchronized map.

### Basic Operations

```java
import java.util.concurrent.ConcurrentHashMap;

ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>();

// Thread-safe operations
map.put("Alice", 25);
map.put("Bob", 30);
map.put("Charlie", 35);

Integer age = map.get("Alice");  // 25

// putIfAbsent - atomic operation
Integer prev = map.putIfAbsent("David", 40);
// Returns null if key didn't exist, otherwise returns existing value

// replace - atomic replace
boolean replaced = map.replace("Alice", 25, 26);  // Replace if current value is 25

// remove - atomic remove
boolean removed = map.remove("Bob", 30);  // Remove only if value is 30

// Size
int size = map.size();
```

### Atomic Compound Operations

```java
ConcurrentHashMap<String, Integer> scores = new ConcurrentHashMap<>();

// compute - compute new value atomically
scores.put("Alice", 100);
scores.compute("Alice", (key, value) -> value == null ? 1 : value + 10);
// Alice: 110

// computeIfAbsent - compute if key absent
scores.computeIfAbsent("Bob", key -> 50);
// Bob: 50 (only if Bob wasn't in map)

// computeIfPresent - compute if key present
scores.computeIfPresent("Alice", (key, value) -> value + 5);
// Alice: 115

// merge - merge value with existing
scores.merge("Alice", 10, (oldVal, newVal) -> oldVal + newVal);
// Alice: 125 (115 + 10)

// If key doesn't exist, uses provided value
scores.merge("Charlie", 20, (oldVal, newVal) -> oldVal + newVal);
// Charlie: 20
```

### Iteration

```java
ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>();
map.put("A", 1);
map.put("B", 2);
map.put("C", 3);

// Safe concurrent iteration - weakly consistent
for (Map.Entry<String, Integer> entry : map.entrySet()) {
    System.out.println(entry.getKey() + ": " + entry.getValue());
}

// forEach
map.forEach((key, value) -> {
    System.out.println(key + " = " + value);
});

// Parallel operations (Java 8+)
map.forEach(2, (key, value) -> {  // parallelismThreshold
    System.out.println(key + " = " + value);
});

// search - returns first matching result
String result = map.search(2, (key, value) -> {
    return value > 2 ? key : null;
});
System.out.println(result);  // C

// reduce
Integer sum = map.reduce(2,
    (key, value) -> value,  // transformer
    (v1, v2) -> v1 + v2      // reducer
);
System.out.println(sum);  // 6
```

### Thread-Safe Counter Example

```java
class PageViewCounter {
    private ConcurrentHashMap<String, AtomicInteger> counters = new ConcurrentHashMap<>();
    
    public void recordView(String page) {
        counters.computeIfAbsent(page, k -> new AtomicInteger(0))
                .incrementAndGet();
    }
    
    public int getViews(String page) {
        AtomicInteger counter = counters.get(page);
        return counter == null ? 0 : counter.get();
    }
    
    public Map<String, Integer> getAllViews() {
        Map<String, Integer> snapshot = new HashMap<>();
        counters.forEach((page, counter) -> {
            snapshot.put(page, counter.get());
        });
        return snapshot;
    }
}
```

---

## CopyOnWriteArrayList

**CopyOnWriteArrayList** creates a new copy of the list on every write. Excellent for read-heavy workloads.

### Basic Operations

```java
import java.util.concurrent.CopyOnWriteArrayList;

CopyOnWriteArrayList<String> list = new CopyOnWriteArrayList<>();

// Write operations - create new copy
list.add("A");
list.add("B");
list.add("C");

// Read operations - no locking
String first = list.get(0);  // Fast, no lock

// Remove
list.remove("B");

// Size
int size = list.size();
```

### Iteration Safety

```java
CopyOnWriteArrayList<String> list = new CopyOnWriteArrayList<>();
list.add("A");
list.add("B");
list.add("C");

// Safe concurrent iteration - snapshot
for (String s : list) {
    // Iterates over snapshot - modifications don't affect iteration
    list.add("D");  // OK - doesn't throw ConcurrentModificationException
    System.out.println(s);
}
// Prints: A, B, C (D is not in iteration snapshot)

System.out.println(list);  // [A, B, C, D, D, D]
```

### When to Use

```java
// ✅ GOOD: Read-heavy workload
class EventListeners {
    private List<EventListener> listeners = new CopyOnWriteArrayList<>();
    
    public void addListener(EventListener listener) {
        listeners.add(listener);  // Rare operation
    }
    
    public void fireEvent(Event event) {
        for (EventListener listener : listeners) {
            listener.onEvent(event);  // Frequent operation
        }
    }
}

// ❌ BAD: Write-heavy workload (too many copies)
class Logger {
    private List<String> logs = new CopyOnWriteArrayList<>();  // BAD choice
    
    public void log(String message) {
        logs.add(message);  // Frequent - creates many copies!
    }
}
```

---

## CopyOnWriteArraySet

**CopyOnWriteArraySet** is a set backed by CopyOnWriteArrayList.

### Basic Operations

```java
import java.util.concurrent.CopyOnWriteArraySet;

CopyOnWriteArraySet<String> set = new CopyOnWriteArraySet<>();

// Add elements
set.add("A");
set.add("B");
set.add("A");  // Duplicate - not added

System.out.println(set.size());  // 2

// Contains
boolean hasA = set.contains("A");  // true

// Remove
set.remove("B");

// Iteration - safe, snapshot
for (String s : set) {
    set.add("C");  // OK
    System.out.println(s);
}
```

### Use Case

```java
class SubscriptionManager {
    private Set<Subscriber> subscribers = new CopyOnWriteArraySet<>();
    
    public void subscribe(Subscriber sub) {
        subscribers.add(sub);  // Infrequent
    }
    
    public void unsubscribe(Subscriber sub) {
        subscribers.remove(sub);  // Infrequent
    }
    
    public void notifyAll(Message msg) {
        for (Subscriber sub : subscribers) {
            sub.receive(msg);  // Frequent reads
        }
    }
}
```

---

## ConcurrentLinkedQueue

**ConcurrentLinkedQueue** is an unbounded lock-free queue.

### Basic Operations

```java
import java.util.concurrent.ConcurrentLinkedQueue;

ConcurrentLinkedQueue<String> queue = new ConcurrentLinkedQueue<>();

// Add elements
queue.offer("A");
queue.offer("B");
queue.offer("C");

// Retrieve and remove head
String head = queue.poll();  // "A"

// Peek without removing
String peek = queue.peek();  // "B"

// Size (O(n) operation - avoid if possible)
int size = queue.size();

// Empty check
boolean isEmpty = queue.isEmpty();
```

### Producer-Consumer Pattern

```java
class TaskProcessor {
    private ConcurrentLinkedQueue<Task> taskQueue = new ConcurrentLinkedQueue<>();
    private volatile boolean running = true;
    
    // Producer
    public void submitTask(Task task) {
        taskQueue.offer(task);
    }
    
    // Consumer
    public void processTasks() {
        while (running) {
            Task task = taskQueue.poll();
            if (task != null) {
                task.execute();
            } else {
                try {
                    Thread.sleep(100);  // Wait for tasks
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    break;
                }
            }
        }
    }
    
    public void shutdown() {
        running = false;
    }
}
```

---

## BlockingQueue Implementations

**BlockingQueue** provides blocking operations for producer-consumer scenarios.

### LinkedBlockingQueue

Unbounded (or optionally bounded) blocking queue.

```java
import java.util.concurrent.LinkedBlockingQueue;

LinkedBlockingQueue<String> queue = new LinkedBlockingQueue<>();

// Producer
new Thread(() -> {
    try {
        queue.put("Task 1");  // Blocks if queue full (won't happen for unbounded)
        queue.put("Task 2");
        queue.put("Task 3");
    } catch (InterruptedException e) {
        Thread.currentThread().interrupt();
    }
}).start();

// Consumer
new Thread(() -> {
    try {
        String task = queue.take();  // Blocks if queue empty
        System.out.println("Processing: " + task);
    } catch (InterruptedException e) {
        Thread.currentThread().interrupt();
    }
}).start();
```

### ArrayBlockingQueue

**Bounded** blocking queue backed by array.

```java
import java.util.concurrent.ArrayBlockingQueue;

// Bounded queue - capacity 10
ArrayBlockingQueue<String> queue = new ArrayBlockingQueue<>(10);

// put - blocks if full
new Thread(() -> {
    try {
        for (int i = 0; i < 20; i++) {
            queue.put("Item " + i);  // Blocks when queue reaches 10
            System.out.println("Added: Item " + i);
        }
    } catch (InterruptedException e) {
        Thread.currentThread().interrupt();
    }
}).start();

// take - blocks if empty
new Thread(() -> {
    try {
        while (true) {
            String item = queue.take();  // Blocks when queue empty
            System.out.println("Consumed: " + item);
            Thread.sleep(100);  // Simulate processing
        }
    } catch (InterruptedException e) {
        Thread.currentThread().interrupt();
    }
}).start();
```

### PriorityBlockingQueue

Unbounded queue with priority ordering.

```java
import java.util.concurrent.PriorityBlockingQueue;

class Task implements Comparable<Task> {
    String name;
    int priority;
    
    Task(String name, int priority) {
        this.name = name;
        this.priority = priority;
    }
    
    @Override
    public int compareTo(Task other) {
        return Integer.compare(other.priority, this.priority);  // Higher priority first
    }
}

PriorityBlockingQueue<Task> queue = new PriorityBlockingQueue<>();

queue.put(new Task("Low", 1));
queue.put(new Task("High", 10));
queue.put(new Task("Medium", 5));

Task task = queue.take();
System.out.println(task.name);  // "High" - highest priority
```

### Blocking Operations

```java
BlockingQueue<String> queue = new LinkedBlockingQueue<>();

// put() - blocks if full
queue.put("Item");

// take() - blocks if empty
String item = queue.take();

// offer() with timeout - waits up to timeout
boolean added = queue.offer("Item", 2, TimeUnit.SECONDS);

// poll() with timeout - waits up to timeout
String polled = queue.poll(2, TimeUnit.SECONDS);

// Non-blocking variants
boolean offered = queue.offer("Item");  // Returns false if can't add immediately
String peek = queue.poll();  // Returns null if empty
```

---

## ConcurrentSkipListMap and ConcurrentSkipListSet

### ConcurrentSkipListMap

Concurrent sorted map.

```java
import java.util.concurrent.ConcurrentSkipListMap;

ConcurrentSkipListMap<Integer, String> map = new ConcurrentSkipListMap<>();

map.put(3, "Three");
map.put(1, "One");
map.put(2, "Two");

// Sorted iteration
for (Map.Entry<Integer, String> entry : map.entrySet()) {
    System.out.println(entry.getKey() + ": " + entry.getValue());
}
// Output: 1: One, 2: Two, 3: Three

// NavigableMap operations
Integer firstKey = map.firstKey();  // 1
Integer lastKey = map.lastKey();    // 3

Map.Entry<Integer, String> lower = map.lowerEntry(2);  // 1: One
Map.Entry<Integer, String> higher = map.higherEntry(2); // 3: Three

// Submap
ConcurrentNavigableMap<Integer, String> subMap = map.subMap(1, 3);
```

### ConcurrentSkipListSet

Concurrent sorted set.

```java
import java.util.concurrent.ConcurrentSkipListSet;

ConcurrentSkipListSet<Integer> set = new ConcurrentSkipListSet<>();

set.add(5);
set.add(2);
set.add(8);
set.add(1);

// Sorted iteration
for (Integer num : set) {
    System.out.println(num);
}
// Output: 1, 2, 5, 8

// NavigableSet operations
Integer first = set.first();   // 1
Integer last = set.last();     // 8
Integer lower = set.lower(5);  // 2
Integer higher = set.higher(5); // 8
```

---

## Thread-Safe Collections Comparison

### Performance Characteristics

| Collection | Read | Write | Iteration | Sorted |
|------------|------|-------|-----------|--------|
| `ConcurrentHashMap` | Fast | Fast | Weakly consistent | No |
| `CopyOnWriteArrayList` | Fast | Slow | Snapshot | No |
| `ConcurrentLinkedQueue` | Fast | Fast | Weakly consistent | No |
| `LinkedBlockingQueue` | Fast | Fast (blocks) | Weakly consistent | No |
| `ConcurrentSkipListMap` | Fast | Fast | Weakly consistent | Yes |

### When to Use What

```java
// Concurrent map - general purpose
Map<K, V> map = new ConcurrentHashMap<>();

// Sorted concurrent map
NavigableMap<K, V> sortedMap = new ConcurrentSkipListMap<>();

// Read-heavy list (rare writes)
List<T> list = new CopyOnWriteArrayList<>();

// Producer-consumer (non-blocking)
Queue<T> queue = new ConcurrentLinkedQueue<>();

// Producer-consumer (blocking)
BlockingQueue<T> blockingQueue = new LinkedBlockingQueue<>();

// Bounded buffer
BlockingQueue<T> bounded = new ArrayBlockingQueue<>(100);

// Priority queue
BlockingQueue<T> priority = new PriorityBlockingQueue<>();
```

---

## Best Practices

### 1. Choose Appropriate Collection

```java
// ✅ Read-heavy: CopyOnWriteArrayList
List<Listener> listeners = new CopyOnWriteArrayList<>();

// ✅ General purpose map: ConcurrentHashMap
Map<String, Data> cache = new ConcurrentHashMap<>();

// ✅ Producer-consumer: BlockingQueue
BlockingQueue<Task> tasks = new LinkedBlockingQueue<>();
```

### 2. Avoid size() in Production

```java
// ❌ BAD - size() is O(n) for ConcurrentLinkedQueue
if (queue.size() > 0) {
    queue.poll();
}

// ✅ GOOD - use isEmpty() or try poll()
String item = queue.poll();
if (item != null) {
    // Process
}
```

### 3. Use Atomic Methods

```java
ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>();

// ❌ BAD - race condition
if (!map.containsKey("count")) {
    map.put("count", 0);
}

// ✅ GOOD - atomic
map.putIfAbsent("count", 0);

// ❌ BAD - not atomic
Integer value = map.get("count");
map.put("count", value + 1);

// ✅ GOOD - atomic
map.compute("count", (k, v) -> v == null ? 1 : v + 1);
```

### 4. Understand Weak Consistency

```java
ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>();
map.put("A", 1);
map.put("B", 2);

// Iteration may not reflect concurrent modifications
for (String key : map.keySet()) {
    map.put("C", 3);  // May or may not appear in iteration
}
```

---

## Summary and Exam Tips

### Key Concepts

- **ConcurrentHashMap**: Lock-striped, high concurrency
- **CopyOnWriteArrayList**: Copy-on-write, read-heavy
- **BlockingQueue**: Producer-consumer with blocking
- **ConcurrentLinkedQueue**: Lock-free non-blocking queue
- **ConcurrentSkipListMap**: Concurrent sorted map

### Exam Tips

- `ConcurrentHashMap` provides **atomic** `putIfAbsent()`, `remove(key, value)`, `replace()`
- `CopyOnWriteArrayList` **never** throws `ConcurrentModificationException`
- `BlockingQueue.take()` **blocks** if empty
- `BlockingQueue.put()` **blocks** if full (bounded queues)
- `ConcurrentLinkedQueue` is **unbounded** and **non-blocking**
- Concurrent collections have **weakly consistent** iterators
- `Collections.synchronizedList()` requires **external synchronization** for iteration
- `ConcurrentHashMap.size()` is approximate
- `CopyOnWriteArrayList` is best for **read-heavy, rare write** scenarios

---

**Previous:** [Practice Questions - Thread Safety](30-practice-questions.md)  
**Next:** [Practice Questions - Concurrent Collections](31-practice-questions.md)
