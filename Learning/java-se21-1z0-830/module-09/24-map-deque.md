# Module 9: Arrays and Collections - Map and Deque

## Table of Contents
1. [Map Interface](#map-interface)
2. [HashMap](#hashmap)
3. [LinkedHashMap](#linkedhashmap)
4. [TreeMap](#treemap)
5. [Map Operations and Methods](#map-operations-and-methods)
6. [Deque Interface](#deque-interface)
7. [ArrayDeque](#arraydeque)
8. [Queue vs Deque](#queue-vs-deque)
9. [Best Practices](#best-practices)

---

## Map Interface

**Map** is an object that maps **keys to values**. A map cannot contain duplicate keys; each key can map to at most one value.

### Map Characteristics

```java
// Not part of Collection hierarchy
// Stores key-value pairs
// No duplicate keys allowed
// Each key maps to one value
Map<String, Integer> map = new HashMap<>();
map.put("Alice", 30);
map.put("Bob", 25);
map.put("Alice", 31); // Replaces previous value
System.out.println(map.get("Alice")); // 31
```

### Map Hierarchy

```
Map (interface)
├── HashMap
├── LinkedHashMap
└── SortedMap (interface)
    └── TreeMap
```

---

## HashMap

**HashMap** is a **hash table** implementation of Map. It provides **constant-time** performance for basic operations.

### HashMap Characteristics

- **No duplicate keys**
- **One null key allowed**
- **Multiple null values allowed**
- **No order guarantee**
- **Best performance**: O(1) for get/put
- **Not synchronized**

### HashMap Creation and Basic Operations

```java
// Creating HashMap
Map<String, Integer> map = new HashMap<>();

// Adding entries
map.put("Alice", 30);
map.put("Bob", 25);
map.put("Charlie", 35);

// Retrieving values
Integer age = map.get("Alice");  // 30
Integer missing = map.get("David"); // null

// Checking existence
boolean hasAlice = map.containsKey("Alice");    // true
boolean hasAge30 = map.containsValue(30);       // true

// Size
int size = map.size();  // 3
boolean empty = map.isEmpty();  // false

// Removing
Integer removed = map.remove("Bob");  // Returns 25
map.clear();  // Removes all entries

// With initial capacity and load factor
Map<String, Integer> optimized = new HashMap<>(16, 0.75f);
```

### HashMap Advanced Operations (Java 8+)

```java
Map<String, Integer> scores = new HashMap<>();

// putIfAbsent - only adds if key doesn't exist
scores.put("Alice", 90);
scores.putIfAbsent("Alice", 95);  // Doesn't replace, returns 90
scores.putIfAbsent("Bob", 85);    // Adds, returns null

// getOrDefault - returns default if key not found
int score = scores.getOrDefault("Charlie", 0);  // 0

// replace methods
scores.replace("Alice", 92);  // Replace value
scores.replace("Alice", 92, 95);  // Replace only if current value is 92

// compute methods
scores.compute("Alice", (k, v) -> v == null ? 100 : v + 5);  // 97
scores.computeIfAbsent("David", k -> 80);  // Adds David:80
scores.computeIfPresent("Alice", (k, v) -> v + 3);  // 100

// merge - combines values
scores.merge("Alice", 10, Integer::sum);  // Adds 10 to existing value
scores.merge("Eve", 75, Integer::sum);    // Adds new entry

// forEach
scores.forEach((name, score) -> 
    System.out.println(name + ": " + score));

// replaceAll
scores.replaceAll((name, score) -> score + 5);  // Add 5 to all scores
```

### Iterating Over HashMap

```java
Map<String, Integer> map = new HashMap<>();
map.put("A", 1);
map.put("B", 2);
map.put("C", 3);

// Method 1: Using entrySet() - MOST EFFICIENT
for (Map.Entry<String, Integer> entry : map.entrySet()) {
    System.out.println(entry.getKey() + " = " + entry.getValue());
}

// Method 2: Using keySet()
for (String key : map.keySet()) {
    Integer value = map.get(key);
    System.out.println(key + " = " + value);
}

// Method 3: Using values()
for (Integer value : map.values()) {
    System.out.println(value);
}

// Method 4: Using forEach (Java 8+)
map.forEach((k, v) -> System.out.println(k + " = " + v));

// Method 5: Using Stream API
map.entrySet().stream()
   .forEach(e -> System.out.println(e.getKey() + " = " + e.getValue()));
```

### HashMap with Custom Objects as Keys

```java
class Person {
    private String name;
    private int age;
    
    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    // MUST override both equals() and hashCode()
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Person)) return false;
        Person person = (Person) o;
        return age == person.age && 
               Objects.equals(name, person.name);
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(name, age);
    }
}

Map<Person, String> personMap = new HashMap<>();
Person p1 = new Person("Alice", 30);
personMap.put(p1, "Engineer");

Person p2 = new Person("Alice", 30);
System.out.println(personMap.get(p2));  // "Engineer"
// Works because equals() and hashCode() are properly overridden
```

---

## LinkedHashMap

**LinkedHashMap** maintains a **doubly-linked list** of entries in **insertion order** (or access order).

### LinkedHashMap Characteristics

- **Insertion order maintained**
- **One null key allowed**
- **Multiple null values allowed**
- **Slightly slower than HashMap**
- **Can be configured for access order**

### LinkedHashMap Usage

```java
// Maintains insertion order
Map<String, Integer> map = new LinkedHashMap<>();
map.put("Zebra", 1);
map.put("Apple", 2);
map.put("Mango", 3);

// Iteration is in insertion order
map.forEach((k, v) -> System.out.print(k + " "));
// Output: Zebra Apple Mango

// Access-order mode (for LRU cache)
Map<String, Integer> accessOrderMap = new LinkedHashMap<>(16, 0.75f, true);
accessOrderMap.put("A", 1);
accessOrderMap.put("B", 2);
accessOrderMap.put("C", 3);

accessOrderMap.get("A");  // Access A
// Order is now: B, C, A (A moved to end)
```

### LRU Cache Implementation

```java
class LRUCache<K, V> extends LinkedHashMap<K, V> {
    private final int capacity;
    
    public LRUCache(int capacity) {
        super(capacity, 0.75f, true);  // access-order mode
        this.capacity = capacity;
    }
    
    @Override
    protected boolean removeEldestEntry(Map.Entry<K, V> eldest) {
        return size() > capacity;  // Remove oldest when size exceeds capacity
    }
}

LRUCache<String, Integer> cache = new LRUCache<>(3);
cache.put("A", 1);
cache.put("B", 2);
cache.put("C", 3);
cache.put("D", 4);  // A is removed (eldest)
System.out.println(cache);  // {B=2, C=3, D=4}
```

---

## TreeMap

**TreeMap** is a **Red-Black tree** implementation of NavigableMap. Keys are stored in **sorted order**.

### TreeMap Characteristics

- **Sorted order**: Natural ordering or custom Comparator
- **No null keys**: NullPointerException (null values allowed)
- **Slower operations**: O(log n) for get/put
- **NavigableMap operations**: floor, ceiling, higher, lower

### TreeMap Usage

```java
// Natural ordering (alphabetical for String)
Map<String, Integer> map = new TreeMap<>();
map.put("Charlie", 3);
map.put("Alice", 1);
map.put("Bob", 2);

System.out.println(map);
// {Alice=1, Bob=2, Charlie=3} - sorted by key

// Custom comparator (reverse order)
Map<String, Integer> reverseMap = new TreeMap<>(Comparator.reverseOrder());
reverseMap.put("A", 1);
reverseMap.put("C", 3);
reverseMap.put("B", 2);

System.out.println(reverseMap);
// {C=3, B=2, A=1}

// Integer keys - natural ordering
Map<Integer, String> numbers = new TreeMap<>();
numbers.put(3, "Three");
numbers.put(1, "One");
numbers.put(2, "Two");
System.out.println(numbers);
// {1=One, 2=Two, 3=Three}
```

### NavigableMap Operations

```java
NavigableMap<Integer, String> map = new TreeMap<>();
map.put(1, "One");
map.put(3, "Three");
map.put(5, "Five");
map.put(7, "Seven");
map.put(9, "Nine");

// Navigation methods
Map.Entry<Integer, String> first = map.firstEntry();  // 1=One
Map.Entry<Integer, String> last = map.lastEntry();    // 9=Nine
Integer firstKey = map.firstKey();  // 1
Integer lastKey = map.lastKey();    // 9

// Ceiling, floor, higher, lower
Integer ceiling = map.ceilingKey(4);   // 5 (>= 4)
Integer floor = map.floorKey(4);       // 3 (<= 4)
Integer higher = map.higherKey(5);     // 7 (> 5)
Integer lower = map.lowerKey(5);       // 3 (< 5)

// Poll operations
Map.Entry<Integer, String> pollFirst = map.pollFirstEntry();  // Removes 1=One
Map.Entry<Integer, String> pollLast = map.pollLastEntry();    // Removes 9=Nine

// Range views
NavigableMap<Integer, String> headMap = map.headMap(5, true);  // <= 5
NavigableMap<Integer, String> tailMap = map.tailMap(5, false); // > 5
NavigableMap<Integer, String> subMap = map.subMap(3, true, 7, true); // [3,7]

// Descending operations
NavigableMap<Integer, String> descending = map.descendingMap();
System.out.println(descending);  // {7=Seven, 5=Five, 3=Three}
```

---

## Map Operations and Methods

### Common Map Methods Summary

```java
Map<String, Integer> map = new HashMap<>();

// Adding/Updating
map.put(key, value);              // Add or replace
map.putAll(anotherMap);           // Add all from another map
map.putIfAbsent(key, value);      // Add only if absent (Java 8+)

// Retrieving
V value = map.get(key);           // Get value, null if absent
V value = map.getOrDefault(key, defaultValue); // Java 8+

// Removing
map.remove(key);                  // Remove by key
map.remove(key, value);           // Remove only if value matches (Java 8+)
map.clear();                      // Remove all

// Querying
boolean has = map.containsKey(key);
boolean has = map.containsValue(value);
int size = map.size();
boolean empty = map.isEmpty();

// Views
Set<K> keys = map.keySet();
Collection<V> values = map.values();
Set<Map.Entry<K, V>> entries = map.entrySet();

// Functional operations (Java 8+)
map.forEach((k, v) -> { /* ... */ });
map.replaceAll((k, v) -> newValue);
map.compute(key, (k, v) -> newValue);
map.computeIfAbsent(key, k -> newValue);
map.computeIfPresent(key, (k, v) -> newValue);
map.merge(key, value, (oldVal, newVal) -> mergedValue);
```

### Map Factory Methods (Java 9+)

```java
// Empty map
Map<String, Integer> empty = Map.of();

// Up to 10 entries
Map<String, Integer> small = Map.of(
    "A", 1,
    "B", 2,
    "C", 3
);

// More than 10 entries
Map<String, Integer> large = Map.ofEntries(
    Map.entry("A", 1),
    Map.entry("B", 2),
    Map.entry("C", 3),
    Map.entry("D", 4)
);

// All are immutable
// small.put("D", 4); // UnsupportedOperationException
```

---

## Deque Interface

**Deque** (Double Ended Queue) supports element insertion and removal at **both ends**.

### Deque Characteristics

```java
// Extends Queue interface
// Can be used as FIFO (queue) or LIFO (stack)
// Supports operations at both ends
Deque<String> deque = new ArrayDeque<>();
deque.addFirst("A");  // Add at front
deque.addLast("B");   // Add at end
```

### Deque Methods

```java
Deque<String> deque = new ArrayDeque<>();

// Adding elements
deque.addFirst("A");      // Add at front, throws exception if fails
deque.addLast("B");       // Add at end, throws exception if fails
deque.offerFirst("C");    // Add at front, returns false if fails
deque.offerLast("D");     // Add at end, returns false if fails

// Removing elements
String first = deque.removeFirst();  // Remove from front, throws if empty
String last = deque.removeLast();    // Remove from end, throws if empty
String first2 = deque.pollFirst();   // Remove from front, returns null if empty
String last2 = deque.pollLast();     // Remove from end, returns null if empty

// Examining elements (without removing)
String peek1 = deque.getFirst();     // Get first, throws if empty
String peek2 = deque.getLast();      // Get last, throws if empty
String peek3 = deque.peekFirst();    // Get first, returns null if empty
String peek4 = deque.peekLast();     // Get last, returns null if empty
```

### Deque as Stack (LIFO)

```java
Deque<String> stack = new ArrayDeque<>();

// Stack operations
stack.push("A");    // Add to front (same as addFirst)
stack.push("B");
stack.push("C");

String top = stack.peek();  // C (doesn't remove)
String popped = stack.pop(); // C (removes)

System.out.println(stack);  // [B, A]

// Equivalent to:
// push(e)    -> addFirst(e)
// pop()      -> removeFirst()
// peek()     -> peekFirst()
```

### Deque as Queue (FIFO)

```java
Deque<String> queue = new ArrayDeque<>();

// Queue operations (FIFO)
queue.offer("A");   // Add to end (same as offerLast)
queue.offer("B");
queue.offer("C");

String front = queue.peek();  // A (doesn't remove)
String served = queue.poll(); // A (removes from front)

System.out.println(queue);  // [B, C]

// Equivalent to:
// offer(e)   -> offerLast(e)
// poll()     -> pollFirst()
// peek()     -> peekFirst()
```

---

## ArrayDeque

**ArrayDeque** is a **resizable-array** implementation of Deque. It's faster than LinkedList for most operations.

### ArrayDeque Characteristics

- **No capacity restrictions**
- **Faster than LinkedList** (no node overhead)
- **Not thread-safe**
- **No null elements allowed**
- **More efficient than Stack**

### ArrayDeque Usage

```java
// General deque operations
Deque<Integer> deque = new ArrayDeque<>();
deque.addFirst(1);    // [1]
deque.addLast(2);     // [1, 2]
deque.addFirst(0);    // [0, 1, 2]
deque.addLast(3);     // [0, 1, 2, 3]

System.out.println(deque.removeFirst());  // 0
System.out.println(deque.removeLast());   // 3
System.out.println(deque);  // [1, 2]

// As a stack (preferred over Stack class)
Deque<String> stack = new ArrayDeque<>();
stack.push("A");
stack.push("B");
String top = stack.pop();

// As a queue (preferred over LinkedList for queue)
Deque<String> queue = new ArrayDeque<>();
queue.offer("First");
queue.offer("Second");
String served = queue.poll();

// Initial capacity
Deque<String> large = new ArrayDeque<>(100);
```

---

## Queue vs Deque

### Queue Interface (FIFO)

```java
Queue<String> queue = new LinkedList<>();  // or ArrayDeque

// Adding (at end)
queue.offer("A");   // Preferred (returns false if fails)
queue.add("B");     // Throws exception if fails

// Removing (from front)
String e1 = queue.poll();   // Returns null if empty
String e2 = queue.remove(); // Throws exception if empty

// Examining (front element)
String e3 = queue.peek();   // Returns null if empty
String e4 = queue.element(); // Throws exception if empty
```

### Method Comparison

| Operation | Throws Exception | Returns Special Value |
|-----------|------------------|----------------------|
| **Insert (end)** | add(e) | offer(e) - returns false |
| **Remove (front)** | remove() | poll() - returns null |
| **Examine (front)** | element() | peek() - returns null |

---

## Best Practices

### Choosing the Right Map

```java
// Use HashMap when:
// - Order doesn't matter
// - Fast access needed
// - General-purpose map
Map<String, Integer> general = new HashMap<>();

// Use LinkedHashMap when:
// - Insertion order matters
// - Predictable iteration order needed
// - Implementing LRU cache
Map<String, Integer> ordered = new LinkedHashMap<>();

// Use TreeMap when:
// - Sorted order needed
// - Range queries needed
// - NavigableMap operations needed
Map<Integer, String> sorted = new TreeMap<>();
```

### Choosing the Right Queue/Deque

```java
// Use ArrayDeque when:
// - Need stack or queue
// - No null elements
// - Better performance than LinkedList
Deque<String> preferred = new ArrayDeque<>();

// Use LinkedList when:
// - Need both List and Deque operations
// - Null elements needed
Deque<String> listDeque = new LinkedList<>();

// Don't use Stack class - use ArrayDeque instead
Deque<String> stack = new ArrayDeque<>();  // Preferred
Stack<String> oldStack = new Stack<>();     // Avoid
```

### Common Patterns

```java
// 1. Counting occurrences
Map<String, Integer> frequency = new HashMap<>();
for (String word : words) {
    frequency.merge(word, 1, Integer::sum);
}

// 2. Grouping by category
Map<Category, List<Item>> groups = new HashMap<>();
for (Item item : items) {
    groups.computeIfAbsent(item.getCategory(), k -> new ArrayList<>())
          .add(item);
}

// 3. Default values
Map<String, Integer> scores = new HashMap<>();
int score = scores.getOrDefault("Alice", 0);

// 4. Conditional updates
scores.putIfAbsent("Bob", 100);
scores.computeIfPresent("Alice", (k, v) -> v + 10);

// 5. BFS with queue
Queue<Node> queue = new ArrayDeque<>();
queue.offer(root);
while (!queue.isEmpty()) {
    Node current = queue.poll();
    // Process current
    queue.addAll(current.getChildren());
}

// 6. DFS with stack
Deque<Node> stack = new ArrayDeque<>();
stack.push(root);
while (!stack.isEmpty()) {
    Node current = stack.pop();
    // Process current
    stack.addAll(current.getChildren());
}
```

### Performance Comparison

| Collection | Get/Access | Put/Add | Remove | Notes |
|-----------|-----------|---------|--------|-------|
| HashMap | O(1) | O(1) | O(1) | Best general purpose |
| LinkedHashMap | O(1) | O(1) | O(1) | Maintains order |
| TreeMap | O(log n) | O(log n) | O(log n) | Sorted order |
| ArrayDeque | O(1) | O(1) amortized | O(1) | Best stack/queue |
| LinkedList | O(n) | O(1) at ends | O(1) at ends | Use for List ops |

---

## Summary

### Key Takeaways

1. **Map**: Stores key-value pairs, no duplicate keys
2. **HashMap**: Fast, no order, allows one null key
3. **LinkedHashMap**: Maintains insertion order
4. **TreeMap**: Sorted order, no null keys
5. **Deque**: Double-ended queue, supports both ends
6. **ArrayDeque**: Best choice for stack/queue implementations

### Important Points for Exam

```java
// Map allows null keys/values (except TreeMap for keys)
Map<String, String> map = new HashMap<>();
map.put(null, "value");  // OK
map.put("key", null);    // OK

// TreeMap: no null keys
Map<String, String> treeMap = new TreeMap<>();
// treeMap.put(null, "value"); // NullPointerException!

// ArrayDeque: no null elements
Deque<String> deque = new ArrayDeque<>();
// deque.offer(null); // NullPointerException!

// Must override equals() and hashCode() for custom key objects
// Use entrySet() for efficient map iteration
// Prefer ArrayDeque over Stack and LinkedList for stack/queue
```

---

**Previous:** [Practice Questions - List and Set](23-practice-questions.md)  
**Next:** [Practice Questions - Map and Deque](24-practice-questions.md)
