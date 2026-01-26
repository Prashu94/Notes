# Module 11: Practice Questions - Concurrent Collections

## Questions (20)

---

### Question 1
```java
ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>();
map.put("A", 1);
map.putIfAbsent("A", 2);
System.out.println(map.get("A"));
```
What is printed?

**A)** 1  
**B)** 2  
**C)** null  
**D)** Compilation error

**Answer: A)**

**Explanation:** `putIfAbsent()` only puts if key **doesn't exist**. Key "A" already exists with value 1. Prints **1**.

---

### Question 2
```java
CopyOnWriteArrayList<String> list = new CopyOnWriteArrayList<>();
list.add("A");
list.add("B");

for (String s : list) {
    list.add("C");
}
```
What happens?

**A)** ConcurrentModificationException  
**B)** Infinite loop  
**C)** Prints A, B  
**D)** Prints A, B, C

**Answer: C)**

**Explanation:** Iterator uses **snapshot** of list at iteration start. Modifications don't affect iteration. Prints **A, B**.

---

### Question 3
```java
BlockingQueue<String> queue = new LinkedBlockingQueue<>();
String item = queue.poll();
System.out.println(item);
```
What is printed?

**A)** ""  
**B)** null  
**C)** Blocks indefinitely  
**D)** NoSuchElementException

**Answer: B)**

**Explanation:** `poll()` returns **null** if queue is empty (non-blocking). `take()` would block.

---

### Question 4
```java
ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>();
map.put("A", 1);
map.compute("A", (k, v) -> v + 10);
System.out.println(map.get("A"));
```
What is printed?

**A)** 1  
**B)** 11  
**C)** 10  
**D)** NullPointerException

**Answer: B)**

**Explanation:** `compute()` atomically computes new value. 1 + 10 = **11**.

---

### Question 5
```java
BlockingQueue<String> queue = new ArrayBlockingQueue<>(2);
queue.put("A");
queue.put("B");
queue.put("C");
```
What happens?

**A)** All three added  
**B)** Only A and B added  
**C)** Blocks on third put  
**D)** IllegalStateException

**Answer: C)**

**Explanation:** `ArrayBlockingQueue(2)` has capacity 2. Third `put()` **blocks** until space available.

---

### Question 6
```java
CopyOnWriteArrayList<String> list = new CopyOnWriteArrayList<>();
list.add("A");
list.add("B");
list.remove("A");
```
What happens internally?

**A)** Modifies existing array  
**B)** Creates new copy of array  
**C)** Locks the array  
**D)** Throws exception

**Answer: B)**

**Explanation:** Every **write operation** (add, remove, set) creates a **new copy** of the underlying array.

---

### Question 7
```java
ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>();
map.put("A", 1);
boolean removed = map.remove("A", 2);
System.out.println(removed);
```
What is printed?

**A)** true  
**B)** false  
**C)** NullPointerException  
**D)** Compilation error

**Answer: B)**

**Explanation:** `remove(key, value)` only removes if **value matches**. Value is 1, not 2. Returns **false**.

---

### Question 8
```java
BlockingQueue<String> queue = new LinkedBlockingQueue<>();
boolean added = queue.offer("A", 2, TimeUnit.SECONDS);
System.out.println(added);
```
What is printed?

**A)** true  
**B)** false  
**C)** Blocks for 2 seconds  
**D)** Compilation error

**Answer: A)**

**Explanation:** Queue is empty (not full). `offer()` adds immediately without waiting. Returns **true**.

---

### Question 9
```java
List<String> list = Collections.synchronizedList(new ArrayList<>());
list.add("A");
list.add("B");

for (String s : list) {
    System.out.println(s);
}
```
Is this thread-safe?

**A)** Yes  
**B)** No - iteration needs synchronization  
**C)** Yes if single-threaded  
**D)** Depends on JVM

**Answer: B)**

**Explanation:** `synchronizedList` requires **external synchronization** for iteration.

```java
// Correct
synchronized (list) {
    for (String s : list) {
        System.out.println(s);
    }
}
```

---

### Question 10
```java
ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>();
map.put("A", 1);
Integer value = map.merge("A", 10, (old, new) -> old + new);
System.out.println(value);
```
What is printed?

**A)** 1  
**B)** 10  
**C)** 11  
**D)** null

**Answer: C)**

**Explanation:** `merge()` combines old value (1) with new value (10) using merger function: 1 + 10 = **11**.

---

### Question 11
```java
ConcurrentLinkedQueue<String> queue = new ConcurrentLinkedQueue<>();
queue.offer("A");
queue.offer("B");
System.out.println(queue.size());
```
What's true about `size()`?

**A)** O(1) constant time  
**B)** O(n) linear time  
**C)** Returns approximate size  
**D)** Both B and C

**Answer: B)**

**Explanation:** `ConcurrentLinkedQueue.size()` is **O(n)** - traverses entire queue. Should avoid in performance-critical code.

---

### Question 12
```java
CopyOnWriteArraySet<String> set = new CopyOnWriteArraySet<>();
set.add("A");
set.add("B");
set.add("A");
System.out.println(set.size());
```
What is printed?

**A)** 1  
**B)** 2  
**C)** 3  
**D)** Compilation error

**Answer: B)**

**Explanation:** Set doesn't allow duplicates. Second "A" not added. Size = **2** (A and B).

---

### Question 13
```java
BlockingQueue<String> queue = new LinkedBlockingQueue<>();
queue.put("A");
String item = queue.take();
String item2 = queue.take();
```
What happens at `item2 = queue.take()`?

**A)** Returns null  
**B)** Throws NoSuchElementException  
**C)** Blocks indefinitely  
**D)** Returns empty string

**Answer: C)**

**Explanation:** `take()` **blocks** if queue is empty. Second `take()` blocks waiting for element.

---

### Question 14
```java
ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>();
Integer value = map.computeIfAbsent("A", k -> 10);
System.out.println(value);
```
What is printed?

**A)** null  
**B)** 0  
**C)** 10  
**D)** Compilation error

**Answer: C)**

**Explanation:** `computeIfAbsent()` computes value if key absent. Key "A" doesn't exist, computes 10. Prints **10**.

---

### Question 15
```java
PriorityBlockingQueue<Integer> queue = new PriorityBlockingQueue<>();
queue.put(5);
queue.put(2);
queue.put(8);
System.out.println(queue.take());
```
What is printed?

**A)** 5  
**B)** 2  
**C)** 8  
**D)** Unpredictable

**Answer: B)**

**Explanation:** `PriorityBlockingQueue` orders by natural order (or comparator). **Smallest** first: **2**.

---

### Question 16
```java
ConcurrentSkipListMap<Integer, String> map = new ConcurrentSkipListMap<>();
map.put(3, "C");
map.put(1, "A");
map.put(2, "B");

for (Integer key : map.keySet()) {
    System.out.print(key);
}
```
What is printed?

**A)** 312  
**B)** 123  
**C)** 321  
**D)** Unpredictable

**Answer: B)**

**Explanation:** `ConcurrentSkipListMap` is **sorted**. Iterates in ascending key order: **123**.

---

### Question 17
```java
ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>();
map.put("A", 1);
boolean replaced = map.replace("A", 1, 10);
System.out.println(map.get("A"));
```
What is printed?

**A)** 1  
**B)** 10  
**C)** null  
**D)** Compilation error

**Answer: B)**

**Explanation:** `replace(key, oldValue, newValue)` replaces if current value matches oldValue. 1 == 1, replaces with 10. Prints **10**.

---

### Question 18
```java
CopyOnWriteArrayList<String> list = new CopyOnWriteArrayList<>();
list.add("A");

Iterator<String> iter = list.iterator();
list.add("B");
while (iter.hasNext()) {
    System.out.println(iter.next());
}
```
What is printed?

**A)** A, B  
**B)** A  
**C)** B  
**D)** ConcurrentModificationException

**Answer: B)**

**Explanation:** Iterator uses **snapshot** created when iterator() was called. "B" added after, not in snapshot. Prints **A**.

---

### Question 19
```java
BlockingQueue<String> queue = new ArrayBlockingQueue<>(2);
boolean offered = queue.offer("A");
queue.offer("B");
boolean offered2 = queue.offer("C");
System.out.println(offered2);
```
What is printed?

**A)** true  
**B)** false  
**C)** Blocks  
**D)** IllegalStateException

**Answer: B)**

**Explanation:** Capacity is 2. A and B added. `offer("C")` can't add (queue full), returns **false** immediately (non-blocking).

---

### Question 20
```java
ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>();
map.put("A", 1);
Integer result = map.computeIfPresent("A", (k, v) -> v * 2);
System.out.println(result);
```
What is printed?

**A)** 1  
**B)** 2  
**C)** null  
**D)** NullPointerException

**Answer: B)**

**Explanation:** `computeIfPresent()` computes new value if key present. 1 * 2 = **2**.

---

## Score Interpretation

- **18-20 correct**: Excellent! You master concurrent collections.
- **15-17 correct**: Good understanding. Review blocking operations.
- **12-14 correct**: Fair grasp. Study ConcurrentHashMap atomic methods.
- **Below 12**: Need more practice. Review all concurrent collection types.

---

**Previous:** [Theory - Concurrent Collections](31-concurrent-collections.md)  
**Next:** Module 12 - I/O and NIO.2

---

## Module 11 Complete! ✅

You've completed Module 11 on Concurrency covering:
- Platform threads vs Virtual threads (Java 21)
- Runnable vs Callable
- ExecutorService and thread pools
- Thread safety with synchronized, volatile, atomic
- Locks and ReadWriteLock
- Concurrent collections (ConcurrentHashMap, CopyOnWriteArrayList, BlockingQueue)

**Total Questions: 60** (20 per topic)
**Total Pages: ~150+** of comprehensive concurrency content

**Next Module:** I/O and NIO.2 - File operations, streams, and Path API
