# Module 9: Practice Questions - Map and Deque

## Questions (20)

---

### Question 1
```java
Map<String, Integer> map = new HashMap<>();
map.put("A", 1);
map.put("B", 2);
map.put("A", 3);
System.out.println(map.size());
```

What is the output?

**A)** 2  
**B)** 3  
**C)** 1  
**D)** Compilation error

---

### Question 2
```java
Map<String, Integer> map = new HashMap<>();
map.put("Alice", 30);
Integer age = map.get("Bob");
System.out.println(age);
```

What is printed?

**A)** 0  
**B)** null  
**C)** NullPointerException  
**D)** Compilation error

---

### Question 3
```java
Map<Integer, String> map = new TreeMap<>();
map.put(3, "Three");
map.put(1, "One");
map.put(2, "Two");
System.out.println(map);
```

What is the output?

**A)** {3=Three, 1=One, 2=Two}  
**B)** {1=One, 2=Two, 3=Three}  
**C)** {2=Two, 1=One, 3=Three}  
**D)** Order is unpredictable

---

### Question 4
```java
Map<String, Integer> map = new LinkedHashMap<>();
map.put("Z", 1);
map.put("A", 2);
map.put("M", 3);
System.out.println(map);
```

What is printed?

**A)** {A=2, M=3, Z=1}  
**B)** {Z=1, A=2, M=3}  
**C)** {M=3, A=2, Z=1}  
**D)** Order is unpredictable

---

### Question 5
```java
Map<String, String> map = new TreeMap<>();
map.put(null, "value");
System.out.println(map);
```

What happens?

**A)** Prints {null=value}  
**B)** Prints {}  
**C)** NullPointerException at runtime  
**D)** Compilation error

---

### Question 6
```java
Map<String, Integer> map = new HashMap<>();
map.put("A", 1);
map.putIfAbsent("A", 2);
map.putIfAbsent("B", 3);
System.out.println(map);
```

What is the output?

**A)** {A=2, B=3}  
**B)** {A=1, B=3}  
**C)** {A=1}  
**D)** Compilation error

---

### Question 7
```java
Deque<String> deque = new ArrayDeque<>();
deque.push("A");
deque.push("B");
deque.push("C");
System.out.println(deque.pop());
```

What is printed?

**A)** A  
**B)** B  
**C)** C  
**D)** Compilation error

---

### Question 8
```java
Deque<String> queue = new ArrayDeque<>();
queue.offer("A");
queue.offer("B");
queue.offer("C");
System.out.println(queue.poll());
```

What is the output?

**A)** A  
**B)** B  
**C)** C  
**D)** Compilation error

---

### Question 9
```java
Map<String, Integer> map = new HashMap<>();
map.put("A", 10);
map.merge("A", 5, Integer::sum);
System.out.println(map.get("A"));
```

What is printed?

**A)** 5  
**B)** 10  
**C)** 15  
**D)** Compilation error

---

### Question 10
```java
Deque<Integer> deque = new ArrayDeque<>();
deque.offer(null);
System.out.println(deque);
```

What happens?

**A)** Prints [null]  
**B)** Prints []  
**C)** NullPointerException at runtime  
**D)** Compilation error

---

### Question 11
```java
Map<String, Integer> map = new HashMap<>();
map.put("A", 1);
map.put("B", 2);
int size = map.values().size();
System.out.println(size);
```

What is the output?

**A)** 0  
**B)** 1  
**C)** 2  
**D)** Compilation error

---

### Question 12
```java
NavigableMap<Integer, String> map = new TreeMap<>();
map.put(1, "One");
map.put(3, "Three");
map.put(5, "Five");
Integer key = map.ceilingKey(4);
System.out.println(key);
```

What is printed?

**A)** 3  
**B)** 4  
**C)** 5  
**D)** null

---

### Question 13
```java
Map<String, Integer> map = Map.of("A", 1, "B", 2);
map.put("C", 3);
System.out.println(map);
```

What happens?

**A)** Prints {A=1, B=2, C=3}  
**B)** Compilation error  
**C)** UnsupportedOperationException at runtime  
**D)** NullPointerException

---

### Question 14
```java
Deque<String> deque = new ArrayDeque<>();
deque.addFirst("A");
deque.addLast("B");
deque.addFirst("C");
System.out.println(deque);
```

What is the output?

**A)** [A, B, C]  
**B)** [C, A, B]  
**C)** [B, A, C]  
**D)** [C, B, A]

---

### Question 15
```java
Map<String, Integer> map = new HashMap<>();
map.put("A", 10);
int value = map.getOrDefault("B", 5);
System.out.println(value);
```

What is printed?

**A)** 0  
**B)** 5  
**C)** 10  
**D)** null

---

### Question 16
```java
Map<String, Integer> map = new HashMap<>();
map.put("A", 1);
map.put("B", 2);
map.remove("A");
System.out.println(map.size());
```

What is the output?

**A)** 0  
**B)** 1  
**C)** 2  
**D)** Compilation error

---

### Question 17
```java
Deque<String> deque = new ArrayDeque<>();
deque.addFirst("A");
deque.addLast("B");
String result = deque.peekFirst();
System.out.println(deque.size());
```

What is printed?

**A)** 0  
**B)** 1  
**C)** 2  
**D)** 3

---

### Question 18
```java
Map<String, Integer> map = new HashMap<>();
map.put("A", 1);
boolean hasB = map.containsKey("B");
System.out.println(hasB);
```

What is the output?

**A)** true  
**B)** false  
**C)** NullPointerException  
**D)** Compilation error

---

### Question 19
```java
Map<String, Integer> map = new HashMap<>();
map.put("A", 10);
map.compute("A", (k, v) -> v + 5);
System.out.println(map.get("A"));
```

What is printed?

**A)** 5  
**B)** 10  
**C)** 15  
**D)** Compilation error

---

### Question 20
```java
Deque<Integer> stack = new ArrayDeque<>();
stack.push(1);
stack.push(2);
stack.push(3);
int value = stack.peek();
System.out.println(stack.size());
```

What is the output?

**A)** 2  
**B)** 3  
**C)** 4  
**D)** Compilation error

---

## Answers and Explanations

### Answer 1: **A)** 2

**Explanation:**  
Maps do not allow duplicate keys. When you put "A" twice, the second value (3) replaces the first value (1). The map contains 2 entries: {A=3, B=2}.

```java
Map<String, Integer> map = new HashMap<>();
map.put("A", 1);  // {A=1}
map.put("B", 2);  // {A=1, B=2}
map.put("A", 3);  // {A=3, B=2} - replaces value
System.out.println(map.size()); // 2
```

---

### Answer 2: **B)** null

**Explanation:**  
When you try to get a value for a key that doesn't exist, `get()` returns `null`.

```java
Map<String, Integer> map = new HashMap<>();
map.put("Alice", 30);
Integer age = map.get("Bob");  // null (key doesn't exist)

// To avoid null, use getOrDefault()
int age2 = map.getOrDefault("Bob", 0);  // 0
```

---

### Answer 3: **B)** {1=One, 2=Two, 3=Three}

**Explanation:**  
`TreeMap` maintains entries in **sorted order** by keys (natural ordering for Integer).

```java
Map<Integer, String> map = new TreeMap<>();
map.put(3, "Three");  // {3=Three}
map.put(1, "One");    // {1=One, 3=Three}
map.put(2, "Two");    // {1=One, 2=Two, 3=Three}
```

---

### Answer 4: **B)** {Z=1, A=2, M=3}

**Explanation:**  
`LinkedHashMap` maintains **insertion order**.

```java
Map<String, Integer> map = new LinkedHashMap<>();
map.put("Z", 1);  // {Z=1}
map.put("A", 2);  // {Z=1, A=2}
map.put("M", 3);  // {Z=1, A=2, M=3}
```

---

### Answer 5: **C)** NullPointerException at runtime

**Explanation:**  
`TreeMap` does **not allow null keys** because it needs to compare keys for sorting.

```java
Map<String, String> treeMap = new TreeMap<>();
// treeMap.put(null, "value"); // NullPointerException!

// HashMap allows one null key
Map<String, String> hashMap = new HashMap<>();
hashMap.put(null, "value");  // OK
```

---

### Answer 6: **B)** {A=1, B=3}

**Explanation:**  
`putIfAbsent()` only adds the entry if the key is **not already present**.

```java
Map<String, Integer> map = new HashMap<>();
map.put("A", 1);           // {A=1}
map.putIfAbsent("A", 2);   // No change - A exists, {A=1}
map.putIfAbsent("B", 3);   // {A=1, B=3} - B doesn't exist
```

---

### Answer 7: **C)** C

**Explanation:**  
`push()` adds to the **front** (like a stack - LIFO). `pop()` removes from the front.

```java
Deque<String> deque = new ArrayDeque<>();
deque.push("A");  // [A]
deque.push("B");  // [B, A]
deque.push("C");  // [C, B, A]
System.out.println(deque.pop());  // C (removes from front)
```

---

### Answer 8: **A)** A

**Explanation:**  
`offer()` adds to the **end**. `poll()` removes from the **front** (FIFO - queue behavior).

```java
Deque<String> queue = new ArrayDeque<>();
queue.offer("A");  // [A]
queue.offer("B");  // [A, B]
queue.offer("C");  // [A, B, C]
System.out.println(queue.poll());  // A (removes from front)
```

---

### Answer 9: **C)** 15

**Explanation:**  
`merge()` combines the existing value with the new value using the provided function.

```java
Map<String, Integer> map = new HashMap<>();
map.put("A", 10);
// merge("A", 5, Integer::sum) -> 10 + 5 = 15
map.merge("A", 5, Integer::sum);
System.out.println(map.get("A"));  // 15
```

---

### Answer 10: **C)** NullPointerException at runtime

**Explanation:**  
`ArrayDeque` does **not allow null elements**.

```java
Deque<Integer> deque = new ArrayDeque<>();
// deque.offer(null);  // NullPointerException!

// LinkedList allows null
Deque<Integer> linkedDeque = new LinkedList<>();
linkedDeque.offer(null);  // OK
```

---

### Answer 11: **C)** 2

**Explanation:**  
`map.values()` returns a Collection view of all values. The map has 2 entries, so there are 2 values.

```java
Map<String, Integer> map = new HashMap<>();
map.put("A", 1);
map.put("B", 2);
Collection<Integer> values = map.values();  // [1, 2]
int size = values.size();  // 2
```

---

### Answer 12: **C)** 5

**Explanation:**  
`ceilingKey(4)` returns the **smallest key >= 4**, which is 5.

```java
NavigableMap<Integer, String> map = new TreeMap<>();
map.put(1, "One");
map.put(3, "Three");
map.put(5, "Five");

// ceilingKey(4) -> 5 (smallest >= 4)
// floorKey(4) -> 3 (largest <= 4)
// higherKey(4) -> 5 (smallest > 4)
// lowerKey(4) -> 3 (largest < 4)
```

---

### Answer 13: **C)** UnsupportedOperationException at runtime

**Explanation:**  
`Map.of()` creates an **immutable map**. Any modification operation throws `UnsupportedOperationException`.

```java
Map<String, Integer> immutable = Map.of("A", 1, "B", 2);
// immutable.put("C", 3);  // UnsupportedOperationException!

// To create mutable:
Map<String, Integer> mutable = new HashMap<>(Map.of("A", 1, "B", 2));
mutable.put("C", 3);  // OK
```

---

### Answer 14: **B)** [C, A, B]

**Explanation:**  
`addFirst()` adds to the **front**, `addLast()` adds to the **end**.

```java
Deque<String> deque = new ArrayDeque<>();
deque.addFirst("A");  // [A]
deque.addLast("B");   // [A, B]
deque.addFirst("C");  // [C, A, B]
```

---

### Answer 15: **B)** 5

**Explanation:**  
`getOrDefault()` returns the **default value** (5) when the key ("B") is not found.

```java
Map<String, Integer> map = new HashMap<>();
map.put("A", 10);
int value = map.getOrDefault("B", 5);  // 5 (B doesn't exist)
int value2 = map.getOrDefault("A", 5); // 10 (A exists)
```

---

### Answer 16: **B)** 1

**Explanation:**  
`remove()` removes the entry with the specified key. The map originally had 2 entries; after removing "A", it has 1 entry.

```java
Map<String, Integer> map = new HashMap<>();
map.put("A", 1);  // {A=1}
map.put("B", 2);  // {A=1, B=2}
map.remove("A");  // {B=2}
System.out.println(map.size());  // 1
```

---

### Answer 17: **C)** 2

**Explanation:**  
`peekFirst()` **examines** the first element without removing it. The deque still has 2 elements.

```java
Deque<String> deque = new ArrayDeque<>();
deque.addFirst("A");  // [A]
deque.addLast("B");   // [A, B]
String result = deque.peekFirst();  // "A" (doesn't remove)
System.out.println(deque.size());   // 2
```

---

### Answer 18: **B)** false

**Explanation:**  
`containsKey()` checks if the map contains the specified key. "B" is not in the map.

```java
Map<String, Integer> map = new HashMap<>();
map.put("A", 1);
boolean hasA = map.containsKey("A");  // true
boolean hasB = map.containsKey("B");  // false
```

---

### Answer 19: **C)** 15

**Explanation:**  
`compute()` recalculates the value for the specified key using the provided function.

```java
Map<String, Integer> map = new HashMap<>();
map.put("A", 10);
// compute("A", (k, v) -> v + 5) -> 10 + 5 = 15
map.compute("A", (k, v) -> v + 5);
System.out.println(map.get("A"));  // 15
```

---

### Answer 20: **B)** 3

**Explanation:**  
`peek()` examines the top element **without removing** it. The stack still has 3 elements.

```java
Deque<Integer> stack = new ArrayDeque<>();
stack.push(1);  // [1]
stack.push(2);  // [2, 1]
stack.push(3);  // [3, 2, 1]
int value = stack.peek();  // 3 (doesn't remove)
System.out.println(stack.size());  // 3
```

---

## Score Interpretation

- **18-20 correct**: Excellent! You have mastered Map and Deque collections.
- **15-17 correct**: Good understanding. Review the topics you missed.
- **12-14 correct**: Fair. Study the theory again and practice more.
- **Below 12**: Need more practice. Review all concepts thoroughly.

---

**Previous:** [Theory - Map and Deque](24-map-deque.md)  
**Next:** [Module 10 - Streams and Lambda](../module-10/25-lambda-expressions.md)
