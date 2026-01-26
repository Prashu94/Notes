# Module 9: Arrays and Collections - List and Set

## Table of Contents
1. [Collections Framework Overview](#collections-framework-overview)
2. [List Interface](#list-interface)
3. [ArrayList](#arraylist)
4. [LinkedList](#linkedlist)
5. [Vector and Stack](#vector-and-stack)
6. [Set Interface](#set-interface)
7. [HashSet](#hashset)
8. [LinkedHashSet](#linkedhashset)
9. [TreeSet](#treeset)
10. [Comparison and Best Practices](#comparison-and-best-practices)

---

## Collections Framework Overview

The **Java Collections Framework** provides a unified architecture for representing and manipulating collections. It includes interfaces, implementations, and algorithms.

### Core Interfaces Hierarchy

```
Collection (interface)
├── List (interface) - Ordered, allows duplicates
│   ├── ArrayList
│   ├── LinkedList
│   └── Vector
│       └── Stack
├── Set (interface) - No duplicates
│   ├── HashSet
│   ├── LinkedHashSet
│   └── SortedSet (interface)
│       └── TreeSet
└── Queue (interface) - FIFO processing
    └── Deque (interface)
```

### Key Points
- All collections are **generic** (e.g., `List<String>`)
- All extend `Collection<E>` except `Map`
- Prefer **interface types** for variable declarations

---

## List Interface

**List** is an **ordered collection** (also called a **sequence**) that allows duplicate elements and provides **positional access**.

### List Characteristics

```java
// Ordered - maintains insertion order
// Duplicates allowed
// Index-based access (0-based)
List<String> list = new ArrayList<>();
list.add("Apple");      // index 0
list.add("Banana");     // index 1
list.add("Apple");      // index 2 - duplicate allowed
System.out.println(list.get(0)); // Apple
```

### Common List Methods

```java
List<String> list = new ArrayList<>();

// Adding elements
list.add("A");              // Add at end
list.add(0, "B");          // Add at index 0
list.addAll(anotherList);  // Add all from another collection

// Accessing elements
String first = list.get(0);        // Get by index
int index = list.indexOf("A");     // First occurrence
int lastIndex = list.lastIndexOf("A"); // Last occurrence

// Updating elements
list.set(0, "C");          // Replace element at index 0

// Removing elements
list.remove(0);            // Remove by index
list.remove("A");          // Remove by object (first occurrence)
list.clear();              // Remove all

// Querying
int size = list.size();
boolean isEmpty = list.isEmpty();
boolean contains = list.contains("A");

// Iteration
for (String item : list) {
    System.out.println(item);
}

list.forEach(item -> System.out.println(item));
```

---

## ArrayList

**ArrayList** is a **resizable array** implementation of the List interface. It's the most commonly used List implementation.

### ArrayList Characteristics

- **Dynamic size**: Grows automatically
- **Random access**: O(1) for get/set operations
- **Slow insertion/deletion**: O(n) in middle
- **Not synchronized**: Not thread-safe
- **Allows null elements**

### ArrayList Creation

```java
// Default capacity (10)
List<String> list1 = new ArrayList<>();

// With initial capacity
List<String> list2 = new ArrayList<>(20);

// From another collection
List<String> list3 = new ArrayList<>(Arrays.asList("A", "B", "C"));

// Using List.of() - immutable (Java 9+)
List<String> immutable = List.of("A", "B", "C");

// Using Arrays.asList() - fixed-size
List<String> fixedSize = Arrays.asList("A", "B", "C");
```

### ArrayList Operations

```java
List<Integer> numbers = new ArrayList<>();

// Adding
numbers.add(10);
numbers.add(20);
numbers.add(1, 15);  // Insert at index 1
System.out.println(numbers); // [10, 15, 20]

// Bulk operations
numbers.addAll(List.of(30, 40));
System.out.println(numbers); // [10, 15, 20, 30, 40]

// Accessing
int first = numbers.get(0);        // 10
int last = numbers.get(numbers.size() - 1); // 40

// Searching
int index = numbers.indexOf(20);   // 2
boolean has = numbers.contains(15); // true

// Removing
numbers.remove(Integer.valueOf(15)); // Remove object 15
numbers.remove(0);                   // Remove at index 0
System.out.println(numbers); // [20, 30, 40]

// Replacing
numbers.set(0, 25);
System.out.println(numbers); // [25, 30, 40]

// Sorting
Collections.sort(numbers);
// Or using List.sort()
numbers.sort(Comparator.naturalOrder());
numbers.sort(Comparator.reverseOrder());
```

### ArrayList Capacity Management

```java
ArrayList<String> list = new ArrayList<>(5);
System.out.println(list.size()); // 0 (number of elements)

// ensureCapacity - hints to avoid multiple resizings
list.ensureCapacity(100);

// trimToSize - reduces capacity to current size
list.add("A");
list.add("B");
list.trimToSize(); // Capacity now 2
```

---

## LinkedList

**LinkedList** is a **doubly-linked list** implementation of List and Deque interfaces.

### LinkedList Characteristics

- **Dynamic size**
- **Fast insertion/deletion**: O(1) at ends, O(n) in middle
- **Slow random access**: O(n) for get/set
- **Not synchronized**
- **Implements Deque**: Can be used as stack or queue

### LinkedList vs ArrayList

```java
// LinkedList creation
List<String> linkedList = new LinkedList<>();

// Better for frequent insertions/deletions
LinkedList<String> list = new LinkedList<>();
list.addFirst("First");   // O(1)
list.addLast("Last");     // O(1)
list.add(1, "Middle");    // O(n)

// Deque operations
list.offerFirst("New First");
list.offerLast("New Last");
String first = list.pollFirst(); // Remove and return first
String last = list.pollLast();   // Remove and return last

// Queue operations (FIFO)
list.offer("A");  // Add to end
list.offer("B");
String element = list.poll(); // Remove from front
```

### When to Use LinkedList

```java
// Use LinkedList when:
// 1. Frequent insertions/deletions at beginning/end
LinkedList<String> queue = new LinkedList<>();
queue.addFirst("High Priority");

// 2. Implementing stack (LIFO)
LinkedList<String> stack = new LinkedList<>();
stack.push("A");
stack.push("B");
String top = stack.pop();

// 3. Implementing queue (FIFO)
LinkedList<String> fifo = new LinkedList<>();
fifo.offer("First");
fifo.offer("Second");
String served = fifo.poll();

// Use ArrayList when:
// - Random access is frequent
// - Memory is a concern (LinkedList has node overhead)
// - Iteration performance matters
```

---

## Vector and Stack

**Vector** is a legacy synchronized version of ArrayList. **Stack** extends Vector.

### Vector

```java
// Legacy - generally avoid in new code
Vector<String> vector = new Vector<>();
vector.add("A");
vector.addElement("B");  // Legacy method

// Synchronized but slower than ArrayList
// Use Collections.synchronizedList() instead
List<String> syncList = Collections.synchronizedList(new ArrayList<>());
```

### Stack

```java
// Legacy stack implementation
Stack<String> stack = new Stack<>();
stack.push("A");
stack.push("B");
stack.push("C");

String top = stack.peek();  // C (doesn't remove)
String popped = stack.pop(); // C (removes)
boolean empty = stack.isEmpty();
int position = stack.search("A"); // Distance from top (3)

// Modern alternative - use Deque
Deque<String> modernStack = new ArrayDeque<>();
modernStack.push("A");
String element = modernStack.pop();
```

---

## Set Interface

**Set** is a collection that **does not allow duplicate elements**. It models the mathematical set abstraction.

### Set Characteristics

```java
// No duplicates allowed
// No guaranteed order (except LinkedHashSet and TreeSet)
// At most one null element (except TreeSet)
Set<String> set = new HashSet<>();
set.add("Apple");
set.add("Banana");
set.add("Apple");  // Won't be added - duplicate
System.out.println(set.size()); // 2
```

### Common Set Methods

```java
Set<String> set = new HashSet<>();

// Adding
set.add("A");
boolean added = set.add("B");   // true
added = set.add("A");           // false - duplicate

// Querying
boolean contains = set.contains("A");
int size = set.size();
boolean isEmpty = set.isEmpty();

// Removing
set.remove("A");
set.clear();

// Set operations
Set<Integer> set1 = new HashSet<>(Set.of(1, 2, 3, 4));
Set<Integer> set2 = new HashSet<>(Set.of(3, 4, 5, 6));

// Union
Set<Integer> union = new HashSet<>(set1);
union.addAll(set2);  // {1, 2, 3, 4, 5, 6}

// Intersection
Set<Integer> intersection = new HashSet<>(set1);
intersection.retainAll(set2);  // {3, 4}

// Difference
Set<Integer> difference = new HashSet<>(set1);
difference.removeAll(set2);  // {1, 2}

// Subset check
boolean isSubset = set1.containsAll(set2); // false
```

---

## HashSet

**HashSet** is a **hash table** implementation of Set. It offers **constant-time** performance for basic operations.

### HashSet Characteristics

- **No duplicates**
- **No order guarantee**: Order may change over time
- **Allows null**: One null element
- **Best performance**: O(1) for add, remove, contains
- **Not synchronized**

### HashSet Usage

```java
Set<String> set = new HashSet<>();

// Adding elements
set.add("Zebra");
set.add("Apple");
set.add("Mango");
set.add("Apple");  // Duplicate - not added

System.out.println(set); // Order not guaranteed
// Possible output: [Mango, Apple, Zebra]

// With initial capacity and load factor
Set<String> optimized = new HashSet<>(16, 0.75f);

// From collection
Set<Integer> numbers = new HashSet<>(Arrays.asList(1, 2, 3, 2, 1));
System.out.println(numbers); // [1, 2, 3]

// Checking membership
if (set.contains("Apple")) {
    System.out.println("Found");
}

// Removing
set.remove("Apple");

// Iterating
for (String item : set) {
    System.out.println(item);
}

set.forEach(System.out::println);
```

### HashSet with Custom Objects

```java
class Person {
    private String name;
    private int age;
    
    // Must override equals() and hashCode()
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

Set<Person> people = new HashSet<>();
people.add(new Person("Alice", 30));
people.add(new Person("Alice", 30)); // Duplicate - not added
System.out.println(people.size()); // 1
```

---

## LinkedHashSet

**LinkedHashSet** maintains a **doubly-linked list** running through all entries, maintaining **insertion order**.

### LinkedHashSet Characteristics

- **No duplicates**
- **Insertion order maintained**
- **Slightly slower than HashSet**
- **Allows null**

### LinkedHashSet Usage

```java
Set<String> set = new LinkedHashSet<>();

set.add("Zebra");
set.add("Apple");
set.add("Mango");
set.add("Banana");

System.out.println(set); 
// [Zebra, Apple, Mango, Banana] - insertion order maintained

// Iteration is in insertion order
for (String fruit : set) {
    System.out.println(fruit);
}

// Use case: Removing duplicates while preserving order
List<String> list = Arrays.asList("A", "B", "A", "C", "B");
Set<String> uniqueOrdered = new LinkedHashSet<>(list);
System.out.println(uniqueOrdered); // [A, B, C]
```

---

## TreeSet

**TreeSet** is a **Red-Black tree** implementation of NavigableSet. Elements are stored in **sorted order**.

### TreeSet Characteristics

- **No duplicates**
- **Sorted order**: Natural ordering or custom Comparator
- **No null elements**: NullPointerException
- **Slower operations**: O(log n) for add, remove, contains
- **NavigableSet operations**: floor, ceiling, higher, lower

### TreeSet Usage

```java
// Natural ordering
Set<Integer> numbers = new TreeSet<>();
numbers.add(5);
numbers.add(1);
numbers.add(3);
numbers.add(2);

System.out.println(numbers); // [1, 2, 3, 5] - sorted

// Custom comparator (reverse order)
Set<String> names = new TreeSet<>(Comparator.reverseOrder());
names.add("Charlie");
names.add("Alice");
names.add("Bob");

System.out.println(names); // [Charlie, Bob, Alice]

// String natural ordering (lexicographic)
Set<String> words = new TreeSet<>();
words.add("apple");
words.add("Zebra");
words.add("banana");
System.out.println(words); // [Zebra, apple, banana]
// Note: Uppercase before lowercase in natural ordering
```

### NavigableSet Operations

```java
NavigableSet<Integer> set = new TreeSet<>(Set.of(1, 3, 5, 7, 9));

// Range views
SortedSet<Integer> headSet = set.headSet(5);  // [1, 3]
SortedSet<Integer> tailSet = set.tailSet(5);  // [5, 7, 9]
SortedSet<Integer> subSet = set.subSet(3, 8); // [3, 5, 7]

// Navigation methods
Integer first = set.first();        // 1
Integer last = set.last();          // 9
Integer lower = set.lower(5);       // 3 (< 5)
Integer floor = set.floor(5);       // 5 (<= 5)
Integer ceiling = set.ceiling(5);   // 5 (>= 5)
Integer higher = set.higher(5);     // 7 (> 5)

// Poll operations
Integer pollFirst = set.pollFirst(); // Removes and returns 1
Integer pollLast = set.pollLast();   // Removes and returns 9

// Descending operations
NavigableSet<Integer> descending = set.descendingSet();
System.out.println(descending); // [7, 5, 3]
```

---

## Comparison and Best Practices

### List Implementations Comparison

| Feature | ArrayList | LinkedList | Vector |
|---------|-----------|------------|--------|
| Random Access | O(1) | O(n) | O(1) |
| Insert/Delete (middle) | O(n) | O(n) | O(n) |
| Insert/Delete (ends) | O(1) amortized | O(1) | O(1) |
| Memory Overhead | Low | High (node objects) | Low |
| Thread-Safe | No | No | Yes |
| Performance | Fast | Slower for access | Slow (synchronized) |

### Set Implementations Comparison

| Feature | HashSet | LinkedHashSet | TreeSet |
|---------|---------|---------------|---------|
| Order | No order | Insertion order | Sorted |
| Performance | O(1) | O(1) | O(log n) |
| Null Elements | One null | One null | No null |
| Use Case | General purpose | Order matters | Sorted data |

### Choosing the Right Collection

```java
// Use ArrayList when:
// - Random access is frequent
// - Few insertions/deletions in middle
List<String> arrayList = new ArrayList<>();

// Use LinkedList when:
// - Frequent insertions/deletions
// - Implementing queue or deque
List<String> linkedList = new LinkedList<>();

// Use HashSet when:
// - Uniqueness required
// - Order doesn't matter
// - Fast lookups needed
Set<String> hashSet = new HashSet<>();

// Use LinkedHashSet when:
// - Uniqueness required
// - Insertion order matters
Set<String> linkedHashSet = new LinkedHashSet<>();

// Use TreeSet when:
// - Uniqueness required
// - Sorted order needed
// - Range queries needed
Set<Integer> treeSet = new TreeSet<>();
```

### Best Practices

```java
// 1. Use interface types for declarations
List<String> list = new ArrayList<>();  // Good
ArrayList<String> list2 = new ArrayList<>(); // Avoid

// 2. Initialize with capacity if size is known
List<String> largeList = new ArrayList<>(1000);

// 3. Use immutable collections when appropriate
List<String> immutable = List.of("A", "B", "C");
Set<Integer> immutableSet = Set.of(1, 2, 3);

// 4. Use diamond operator for type inference
List<String> names = new ArrayList<>(); // Not new ArrayList<String>()

// 5. Prefer for-each for iteration
for (String name : names) {
    System.out.println(name);
}

// 6. Remove during iteration using Iterator
Iterator<String> iterator = names.iterator();
while (iterator.hasNext()) {
    String name = iterator.next();
    if (name.startsWith("A")) {
        iterator.remove(); // Safe removal
    }
}

// 7. Use removeIf() for conditional removal (Java 8+)
names.removeIf(name -> name.startsWith("A"));

// 8. Override equals() and hashCode() for custom objects in Set/Map
class Custom {
    @Override
    public boolean equals(Object o) { /* ... */ return false; }
    @Override
    public int hashCode() { /* ... */ return 0; }
}
```

### Common Pitfalls

```java
// 1. Modifying list during iteration
List<String> list = new ArrayList<>(List.of("A", "B", "C"));
for (String item : list) {
    if (item.equals("B")) {
        // list.remove(item); // ConcurrentModificationException!
    }
}

// Solution: Use Iterator or removeIf()
list.removeIf(item -> item.equals("B"));

// 2. Using == instead of equals()
String s1 = new String("test");
String s2 = new String("test");
// list.contains(s1) uses equals(), not ==

// 3. Not overriding equals/hashCode for Set
class Person {
    String name;
    // Missing equals() and hashCode()
}
Set<Person> set = new HashSet<>();
set.add(new Person("Alice"));
set.add(new Person("Alice")); // Both added! (should be duplicate)

// 4. TreeSet with non-comparable objects
Set<Person> treeSet = new TreeSet<>();
// treeSet.add(new Person("Alice")); // ClassCastException!
// Solution: Provide Comparator or implement Comparable
```

---

## Summary

### Key Takeaways

1. **List**: Ordered, allows duplicates, index-based access
2. **ArrayList**: Best for random access, dynamic array
3. **LinkedList**: Best for insertions/deletions, implements Deque
4. **Set**: No duplicates, unordered (except LinkedHashSet, TreeSet)
5. **HashSet**: Fast, no order guarantee
6. **LinkedHashSet**: Maintains insertion order
7. **TreeSet**: Sorted order, NavigableSet operations

### Interface-Based Programming

Always declare collections using interface types:
```java
List<String> list = new ArrayList<>();   // Good
Set<Integer> set = new HashSet<>();      // Good
```

### Thread Safety

None of these implementations are synchronized. For thread-safe collections:
```java
List<String> syncList = Collections.synchronizedList(new ArrayList<>());
Set<String> syncSet = Collections.synchronizedSet(new HashSet<>());
// Or use concurrent collections from java.util.concurrent
```

---

**Next:** [Practice Questions - List and Set](23-practice-questions.md)
