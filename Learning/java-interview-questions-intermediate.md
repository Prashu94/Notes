# Java Interview Questions - Intermediate Concepts

## 1. What is exception handling in Java? Explain the exception hierarchy.

**Answer:**

Exception handling is a mechanism to handle runtime errors and maintain normal application flow.

**Exception Hierarchy:**
```
Throwable
├── Error (Unchecked - JVM errors)
│   ├── OutOfMemoryError
│   ├── StackOverflowError
│   └── VirtualMachineError
└── Exception
    ├── RuntimeException (Unchecked)
    │   ├── NullPointerException
    │   ├── ArrayIndexOutOfBoundsException
    │   ├── ArithmeticException
    │   ├── IllegalArgumentException
    │   └── ClassCastException
    └── Checked Exceptions
        ├── IOException
        ├── SQLException
        ├── ClassNotFoundException
        └── InterruptedException
```

**Checked vs Unchecked Exceptions:**

| Feature | Checked Exception | Unchecked Exception |
|---------|------------------|---------------------|
| **Check Time** | Compile-time | Runtime |
| **Handling** | Must handle or declare | Optional |
| **Extends** | Exception (not RuntimeException) | RuntimeException |
| **Examples** | IOException, SQLException | NullPointerException, ArithmeticException |

**Exception Handling Keywords:**

```java
try {
    // Code that may throw exception
    int result = 10 / 0;
} catch (ArithmeticException e) {
    // Handle specific exception
    System.out.println("Cannot divide by zero");
} catch (Exception e) {
    // Handle general exception
    System.out.println("General exception: " + e.getMessage());
} finally {
    // Always executes (cleanup code)
    System.out.println("Finally block executed");
}
```

**Multiple Catch Blocks:**
```java
try {
    String str = null;
    System.out.println(str.length());  // NullPointerException
    int[] arr = new int[5];
    arr[10] = 50;  // ArrayIndexOutOfBoundsException
} catch (NullPointerException e) {
    System.out.println("Null pointer: " + e);
} catch (ArrayIndexOutOfBoundsException e) {
    System.out.println("Array index: " + e);
} catch (Exception e) {
    System.out.println("General: " + e);
}
```

**Multi-catch (Java 7+):**
```java
try {
    // Some code
} catch (IOException | SQLException e) {
    System.out.println("Exception: " + e);
}
```

**throw vs throws:**
```java
// throw - to throw an exception explicitly
void validate(int age) {
    if (age < 18) {
        throw new IllegalArgumentException("Age must be 18+");
    }
}

// throws - to declare exceptions
void readFile() throws IOException {
    FileReader file = new FileReader("test.txt");
}
```

**Custom Exception:**
```java
class InsufficientFundsException extends Exception {
    public InsufficientFundsException(String message) {
        super(message);
    }
}

class BankAccount {
    private double balance;
    
    void withdraw(double amount) throws InsufficientFundsException {
        if (amount > balance) {
            throw new InsufficientFundsException("Balance too low");
        }
        balance -= amount;
    }
}
```

**Try-with-resources (Java 7+):**
```java
try (FileReader fr = new FileReader("file.txt");
     BufferedReader br = new BufferedReader(fr)) {
    String line = br.readLine();
} catch (IOException e) {
    e.printStackTrace();
}
// Resources automatically closed
```

---

## 2. What are the differences between final, finally, and finalize?

**Answer:**

**final keyword:**
- Used with variables, methods, and classes
- Final variable: Value cannot be changed (constant)
- Final method: Cannot be overridden
- Final class: Cannot be inherited

```java
// Final variable
final int MAX_VALUE = 100;
// MAX_VALUE = 200;  // Error

// Final method
class Parent {
    final void display() {
        System.out.println("Final method");
    }
}

class Child extends Parent {
    // void display() { }  // Error: Cannot override
}

// Final class
final class ImmutableClass {
    // Cannot be extended
}

// class SubClass extends ImmutableClass { }  // Error
```

**finally block:**
- Used with try-catch
- Always executes (except System.exit())
- Used for cleanup code

```java
try {
    int result = 10 / 0;
} catch (Exception e) {
    System.out.println("Exception caught");
    return;  // Finally still executes
} finally {
    System.out.println("Finally block executed");
}
```

**finalize() method:**
- Called by garbage collector before object destruction
- Deprecated in Java 9
- Not guaranteed to execute

```java
class Example {
    @Override
    protected void finalize() throws Throwable {
        try {
            System.out.println("Cleanup before GC");
        } finally {
            super.finalize();
        }
    }
}
```

**Comparison:**

| Aspect | final | finally | finalize() |
|--------|-------|---------|------------|
| **Type** | Keyword | Block | Method |
| **Purpose** | Restrict modification | Cleanup after try-catch | Cleanup before GC |
| **Usage** | Variables, methods, classes | Exception handling | Object destruction |
| **Execution** | N/A | Always (almost) | Not guaranteed |

---

## 3. What is garbage collection in Java?

**Answer:**

Garbage Collection (GC) is the automatic process of reclaiming memory by destroying unused objects.

**How it Works:**
- JVM automatically identifies unreferenced objects
- Reclaims memory occupied by them
- Prevents memory leaks

**When Object Becomes Eligible for GC:**
1. No references pointing to it
2. All references go out of scope
3. Reference is set to null
4. Object is created inside a method (local)

**Ways to Make Object Eligible:**

```java
// 1. Nullifying reference
Employee emp = new Employee();
emp = null;  // Eligible for GC

// 2. Re-assigning reference
Employee emp1 = new Employee();
Employee emp2 = new Employee();
emp1 = emp2;  // First object eligible for GC

// 3. Anonymous object
new Employee();  // Immediately eligible

// 4. Island of isolation
class Employee {
    Employee next;
}
Employee e1 = new Employee();
Employee e2 = new Employee();
e1.next = e2;
e2.next = e1;
e1 = null;
e2 = null;  // Both eligible (circular reference)
```

**Requesting GC:**
```java
// 1. Using System class
System.gc();

// 2. Using Runtime class
Runtime.getRuntime().gc();

// Note: These are requests, JVM may choose not to run GC
```

**finalize() Method:**
```java
class Demo {
    @Override
    protected void finalize() throws Throwable {
        System.out.println("Garbage collector called");
        System.out.println("Object garbage collected: " + this);
    }
}

Demo d1 = new Demo();
d1 = null;
System.gc();  // Request GC
```

**GC Algorithms:**
1. **Serial GC**: Single thread, small applications
2. **Parallel GC**: Multiple threads, multi-core systems
3. **CMS (Concurrent Mark Sweep)**: Low latency
4. **G1 (Garbage First)**: Large heaps, predictable pauses
5. **ZGC/Shenandoah**: Ultra-low latency (Java 11+)

**Memory Areas:**
- **Young Generation**: New objects (Eden, Survivor spaces)
- **Old Generation**: Long-lived objects
- **Permanent/Metaspace**: Class metadata

**Benefits:**
- Automatic memory management
- Prevents memory leaks
- Reduces programmer burden
- Improves application reliability

**Disadvantages:**
- Unpredictable timing
- May cause performance overhead
- Stop-the-world pauses

---

## 4. What are wrapper classes in Java?

**Answer:**

Wrapper classes convert primitive types into objects and provide utility methods.

**Primitive to Wrapper Mapping:**

| Primitive | Wrapper Class |
|-----------|---------------|
| byte | Byte |
| short | Short |
| int | Integer |
| long | Long |
| float | Float |
| double | Double |
| char | Character |
| boolean | Boolean |

**Creating Wrapper Objects:**

```java
// Using constructor (deprecated in Java 9+)
Integer i1 = new Integer(10);

// Using valueOf() - preferred
Integer i2 = Integer.valueOf(10);

// Autoboxing (Java 5+)
Integer i3 = 10;  // Automatic conversion
```

**Autoboxing and Unboxing:**

```java
// Autoboxing: primitive to wrapper
int num = 10;
Integer obj = num;  // Automatic boxing

// Unboxing: wrapper to primitive
Integer obj2 = 20;
int num2 = obj2;  // Automatic unboxing

// In collections (only objects allowed)
ArrayList<Integer> list = new ArrayList<>();
list.add(5);  // Autoboxing
int value = list.get(0);  // Unboxing
```

**Utility Methods:**

```java
// String to primitive/wrapper
int num1 = Integer.parseInt("123");
Integer num2 = Integer.valueOf("123");

// Primitive to String
String str1 = Integer.toString(123);
String str2 = String.valueOf(123);

// Compare
Integer a = 10, b = 20;
System.out.println(a.compareTo(b));  // -1 (a < b)

// Min/Max values
System.out.println(Integer.MAX_VALUE);  // 2147483647
System.out.println(Integer.MIN_VALUE);  // -2147483648

// Type conversion
Integer num = 100;
double d = num.doubleValue();
byte b = num.byteValue();
```

**Integer Cache:**

```java
// Integer caching: -128 to 127
Integer i1 = 127;
Integer i2 = 127;
System.out.println(i1 == i2);  // true (same object from cache)

Integer i3 = 128;
Integer i4 = 128;
System.out.println(i3 == i4);  // false (different objects)

// Always use equals() for comparison
System.out.println(i3.equals(i4));  // true
```

**Why Wrapper Classes:**
- Collections require objects
- Generics work only with objects
- Null value representation
- Utility methods for conversion
- Serialization support

**Immutability:**
```java
Integer num = 10;
num = 20;  // Creates new object, doesn't modify existing
```

---

## 5. What are Java Collections? Explain the Collection Framework hierarchy.

**Answer:**

Java Collections Framework provides architecture to store and manipulate groups of objects.

**Collection Hierarchy:**

```
Collection (I)
├── List (I)
│   ├── ArrayList (C)
│   ├── LinkedList (C)
│   ├── Vector (C)
│   └── Stack (C)
├── Set (I)
│   ├── HashSet (C)
│   ├── LinkedHashSet (C)
│   └── SortedSet (I)
│       └── TreeSet (C)
└── Queue (I)
    ├── PriorityQueue (C)
    ├── Deque (I)
    │   ├── ArrayDeque (C)
    │   └── LinkedList (C)

Map (I) - Separate hierarchy
├── HashMap (C)
├── LinkedHashMap (C)
├── Hashtable (C)
├── SortedMap (I)
│   └── TreeMap (C)
└── WeakHashMap (C)

(I) = Interface, (C) = Class
```

**Core Interfaces:**

**1. Collection Interface:**
```java
Collection<String> collection = new ArrayList<>();
collection.add("Java");
collection.remove("Java");
collection.contains("Java");
collection.size();
collection.clear();
```

**2. List Interface (Ordered, allows duplicates):**
```java
List<String> list = new ArrayList<>();
list.add("A");
list.add("B");
list.add(0, "C");  // Insert at index
list.get(0);       // Access by index
list.set(0, "D");  // Replace
list.indexOf("B"); // Find index
```

**3. Set Interface (No duplicates, unordered):**
```java
Set<String> set = new HashSet<>();
set.add("A");
set.add("B");
set.add("A");  // Ignored (duplicate)
System.out.println(set.size());  // 2
```

**4. Queue Interface (FIFO):**
```java
Queue<String> queue = new LinkedList<>();
queue.offer("A");  // Add to end
queue.offer("B");
queue.poll();      // Remove from front
queue.peek();      // View front element
```

**5. Map Interface (Key-Value pairs):**
```java
Map<String, Integer> map = new HashMap<>();
map.put("John", 25);
map.put("Jane", 30);
map.get("John");           // 25
map.containsKey("John");   // true
map.containsValue(25);     // true
map.remove("John");
```

**Common Methods:**

```java
// Iteration
List<String> list = Arrays.asList("A", "B", "C");

// 1. For-each loop
for (String item : list) {
    System.out.println(item);
}

// 2. Iterator
Iterator<String> iterator = list.iterator();
while (iterator.hasNext()) {
    System.out.println(iterator.next());
}

// 3. forEach (Java 8+)
list.forEach(item -> System.out.println(item));

// 4. Stream API (Java 8+)
list.stream().forEach(System.out::println);
```

**Utility Classes:**

```java
// Collections class
List<Integer> list = new ArrayList<>(Arrays.asList(3, 1, 4, 1, 5));
Collections.sort(list);              // Sort
Collections.reverse(list);           // Reverse
Collections.shuffle(list);           // Shuffle
Collections.max(list);               // Maximum
Collections.min(list);               // Minimum
Collections.frequency(list, 1);      // Count occurrences

// Arrays class
int[] arr = {3, 1, 4, 1, 5};
Arrays.sort(arr);                    // Sort
Arrays.binarySearch(arr, 4);         // Binary search
Arrays.toString(arr);                // To string
List<Integer> list2 = Arrays.asList(1, 2, 3);
```

---

## 6. What is the difference between ArrayList and LinkedList?

**Answer:**

| Feature | ArrayList | LinkedList |
|---------|-----------|------------|
| **Data Structure** | Dynamic array | Doubly linked list |
| **Random Access** | Fast O(1) | Slow O(n) |
| **Insertion/Deletion** | Slow O(n) | Fast O(1) |
| **Memory** | Less (only data) | More (data + pointers) |
| **Cache Performance** | Better | Worse |
| **Best For** | Read operations | Write operations |
| **Implements** | List, RandomAccess | List, Deque, Queue |

**Internal Implementation:**

```java
// ArrayList - Dynamic Array
class ArrayList<E> {
    private Object[] elementData;
    private int size;
    
    // When capacity exceeded, creates new larger array
    // and copies elements
}

// LinkedList - Doubly Linked List
class LinkedList<E> {
    private Node<E> first;
    private Node<E> last;
    
    private static class Node<E> {
        E item;
        Node<E> next;
        Node<E> prev;
    }
}
```

**Performance Comparison:**

```java
// ArrayList - Fast get, slow add/remove
List<Integer> arrayList = new ArrayList<>();
arrayList.add(10);           // O(1) amortized
arrayList.get(0);            // O(1)
arrayList.remove(0);         // O(n) - shifts elements
arrayList.add(0, 5);         // O(n) - shifts elements

// LinkedList - Slow get, fast add/remove at ends
List<Integer> linkedList = new LinkedList<>();
linkedList.add(10);          // O(1)
linkedList.get(0);           // O(n) - traverses list
linkedList.remove(0);        // O(1)
linkedList.add(0, 5);        // O(1)
```

**When to Use:**

**ArrayList:**
- Frequent read operations
- Random access needed
- Memory efficiency important
- Iterating through elements
- Default choice for most cases

**LinkedList:**
- Frequent insertions/deletions at beginning/end
- Queue/Deque operations
- No random access needed
- Memory not a concern

**Example:**

```java
// ArrayList for reading
List<String> names = new ArrayList<>();
names.add("Alice");
names.add("Bob");
names.add("Charlie");
String first = names.get(0);  // Fast

// LinkedList for queue operations
Queue<String> queue = new LinkedList<>();
queue.offer("Task1");
queue.offer("Task2");
String task = queue.poll();  // Fast removal from front
```

---

## 7. What is the difference between HashMap and Hashtable?

**Answer:**

| Feature | HashMap | Hashtable |
|---------|---------|-----------|
| **Synchronization** | Not synchronized | Synchronized |
| **Thread-Safety** | Not thread-safe | Thread-safe |
| **Null Keys** | One null key allowed | Not allowed |
| **Null Values** | Multiple null values | Not allowed |
| **Performance** | Faster | Slower (due to sync) |
| **Iteration** | Fail-fast iterator | Fail-safe enumerator |
| **Since** | Java 1.2 | Java 1.0 (legacy) |
| **Inheritance** | Extends AbstractMap | Extends Dictionary |

**Examples:**

```java
// HashMap - Not thread-safe, allows null
HashMap<String, Integer> hashMap = new HashMap<>();
hashMap.put("John", 25);
hashMap.put(null, 30);     // OK
hashMap.put("Jane", null); // OK
hashMap.put(null, 35);     // Replaces previous null key

// Hashtable - Thread-safe, no null
Hashtable<String, Integer> hashtable = new Hashtable<>();
hashtable.put("John", 25);
// hashtable.put(null, 30);     // NullPointerException
// hashtable.put("Jane", null); // NullPointerException
```

**Thread-Safety:**

```java
// HashMap - Manual synchronization needed
Map<String, Integer> map = Collections.synchronizedMap(new HashMap<>());

// Or use ConcurrentHashMap (better performance)
Map<String, Integer> concurrentMap = new ConcurrentHashMap<>();
```

**Performance:**

```java
// HashMap - Faster (no synchronization overhead)
long start = System.currentTimeMillis();
Map<Integer, String> hashMap = new HashMap<>();
for (int i = 0; i < 1000000; i++) {
    hashMap.put(i, "Value" + i);
}
long end = System.currentTimeMillis();
System.out.println("HashMap: " + (end - start) + "ms");

// Hashtable - Slower
start = System.currentTimeMillis();
Map<Integer, String> hashtable = new Hashtable<>();
for (int i = 0; i < 1000000; i++) {
    hashtable.put(i, "Value" + i);
}
end = System.currentTimeMillis();
System.out.println("Hashtable: " + (end - start) + "ms");
```

**When to Use:**
- **HashMap**: Single-threaded applications (most common)
- **Hashtable**: Legacy code (avoid in new code)
- **ConcurrentHashMap**: Multi-threaded applications (preferred over Hashtable)

---

## 8. What is the difference between HashSet and TreeSet?

**Answer:**

| Feature | HashSet | TreeSet |
|---------|---------|---------|
| **Data Structure** | Hash table | Red-Black Tree |
| **Order** | No order | Sorted (natural/comparator) |
| **Null Elements** | One null allowed | No null (Java 7+) |
| **Performance** | O(1) add, remove, contains | O(log n) add, remove, contains |
| **Duplicates** | Not allowed | Not allowed |
| **Memory** | Less overhead | More (tree nodes) |
| **Implements** | Set | SortedSet, NavigableSet |

**Examples:**

```java
// HashSet - Unordered, fast
Set<String> hashSet = new HashSet<>();
hashSet.add("C");
hashSet.add("A");
hashSet.add("B");
System.out.println(hashSet);  // [A, B, C] or any order

// TreeSet - Sorted, slower
Set<String> treeSet = new TreeSet<>();
treeSet.add("C");
treeSet.add("A");
treeSet.add("B");
System.out.println(treeSet);  // [A, B, C] always sorted
```

**TreeSet with Comparator:**

```java
// Custom sorting
Set<String> treeSet = new TreeSet<>(Comparator.reverseOrder());
treeSet.add("Apple");
treeSet.add("Banana");
treeSet.add("Cherry");
System.out.println(treeSet);  // [Cherry, Banana, Apple]

// Custom object sorting
class Person implements Comparable<Person> {
    String name;
    int age;
    
    @Override
    public int compareTo(Person other) {
        return this.age - other.age;
    }
}

Set<Person> persons = new TreeSet<>();
persons.add(new Person("John", 30));
persons.add(new Person("Alice", 25));
// Automatically sorted by age
```

**NavigableSet Operations (TreeSet):**

```java
TreeSet<Integer> set = new TreeSet<>();
set.add(10);
set.add(20);
set.add(30);
set.add(40);

System.out.println(set.first());      // 10
System.out.println(set.last());       // 40
System.out.println(set.lower(30));    // 20 (< 30)
System.out.println(set.higher(30));   // 40 (> 30)
System.out.println(set.floor(25));    // 20 (<= 25)
System.out.println(set.ceiling(25));  // 30 (>= 25)
System.out.println(set.headSet(30));  // [10, 20]
System.out.println(set.tailSet(30));  // [30, 40]
System.out.println(set.subSet(20, 40)); // [20, 30]
```

**When to Use:**
- **HashSet**: Fast operations, no ordering needed
- **TreeSet**: Sorted elements needed, range operations
- **LinkedHashSet**: Insertion order preservation needed

---

## 9. How does HashMap work internally?

**Answer:**

HashMap uses hash table (array of buckets) with linked list/tree for collision handling.

**Key Concepts:**

**1. Hashing:**
- Converts key to integer (hash code)
- Used to determine bucket index

**2. Bucket:**
- Array index where entry is stored
- Multiple entries can map to same bucket (collision)

**3. Load Factor:**
- Threshold for resizing (default 0.75)
- When size > capacity * load factor, resize

**4. Capacity:**
- Number of buckets in hash table
- Default initial capacity: 16

**Internal Structure:**

```java
class HashMap<K,V> {
    transient Node<K,V>[] table;  // Array of buckets
    
    static class Node<K,V> {
        final int hash;
        final K key;
        V value;
        Node<K,V> next;  // For linked list
    }
}
```

**Put Operation:**

```java
public V put(K key, V value) {
    // 1. Calculate hash code
    int hash = key.hashCode();
    
    // 2. Calculate bucket index
    int index = hash & (table.length - 1);
    
    // 3. Check if key exists (update value)
    for (Node<K,V> node = table[index]; node != null; node = node.next) {
        if (node.key.equals(key)) {
            V oldValue = node.value;
            node.value = value;
            return oldValue;
        }
    }
    
    // 4. Add new entry
    addEntry(hash, key, value, index);
    return null;
}
```

**Get Operation:**

```java
public V get(Object key) {
    // 1. Calculate hash code
    int hash = key.hashCode();
    
    // 2. Calculate bucket index
    int index = hash & (table.length - 1);
    
    // 3. Search in linked list/tree
    for (Node<K,V> node = table[index]; node != null; node = node.next) {
        if (node.key.equals(key)) {
            return node.value;
        }
    }
    
    return null;  // Not found
}
```

**Collision Handling:**

**Before Java 8:**
- Linked list for all collisions
- O(n) worst case for get/put

**Java 8+:**
- Linked list converts to balanced tree when size > 8
- Tree converts back to list when size < 6
- O(log n) worst case

```java
// Example: Collision
class BadHash {
    @Override
    public int hashCode() {
        return 1;  // All objects have same hash
    }
}

Map<BadHash, String> map = new HashMap<>();
map.put(new BadHash(), "A");
map.put(new BadHash(), "B");  // Collision, stored in same bucket
```

**Resizing:**

```java
// When size > capacity * loadFactor
// 1. Create new array (double size)
// 2. Rehash all entries
// 3. Move to new array

HashMap<String, Integer> map = new HashMap<>(16, 0.75f);
// Resizes when size > 16 * 0.75 = 12
```

**Why Override hashCode() and equals():**

```java
class Employee {
    int id;
    String name;
    
    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (!(obj instanceof Employee)) return false;
        Employee emp = (Employee) obj;
        return id == emp.id && name.equals(emp.name);
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(id, name);
    }
}

// Without proper hashCode/equals
Employee e1 = new Employee(1, "John");
Employee e2 = new Employee(1, "John");

Map<Employee, String> map = new HashMap<>();
map.put(e1, "Manager");
System.out.println(map.get(e2));  // null (without proper equals/hashCode)
```

**Best Practices:**
- Override both hashCode() and equals()
- Use immutable keys
- Choose appropriate initial capacity
- Consider load factor for performance vs memory

---

## 10. What is the difference between Comparable and Comparator?

**Answer:**

Both are used for sorting objects, but they differ in approach and usage.

**Comparable Interface:**
- Single sorting sequence
- Modifies the class itself
- Found in java.lang package
- compareTo() method

**Comparator Interface:**
- Multiple sorting sequences
- Separate class for comparison
- Found in java.util package
- compare() method

**Detailed Comparison:**

| Feature | Comparable | Comparator |
|---------|------------|------------|
| **Package** | java.lang | java.util |
| **Method** | compareTo(T obj) | compare(T o1, T o2) |
| **Sorting Logic** | In the class itself | Separate class |
| **Modification** | Modifies class | No class modification |
| **Sequences** | Single sorting | Multiple sorting |
| **Collections.sort()** | sort(List) | sort(List, Comparator) |

**Comparable Example:**

```java
class Student implements Comparable<Student> {
    int rollNo;
    String name;
    int age;
    
    Student(int rollNo, String name, int age) {
        this.rollNo = rollNo;
        this.name = name;
        this.age = age;
    }
    
    // Natural ordering by rollNo
    @Override
    public int compareTo(Student other) {
        return this.rollNo - other.rollNo;
    }
}

// Usage
List<Student> students = new ArrayList<>();
students.add(new Student(3, "John", 20));
students.add(new Student(1, "Alice", 22));
students.add(new Student(2, "Bob", 21));

Collections.sort(students);  // Sorted by rollNo
```

**Comparator Examples:**

```java
// 1. Sort by name
class NameComparator implements Comparator<Student> {
    @Override
    public int compare(Student s1, Student s2) {
        return s1.name.compareTo(s2.name);
    }
}

// 2. Sort by age
class AgeComparator implements Comparator<Student> {
    @Override
    public int compare(Student s1, Student s2) {
        return s1.age - s2.age;
    }
}

// Usage
List<Student> students = new ArrayList<>();
students.add(new Student(3, "John", 20));
students.add(new Student(1, "Alice", 22));
students.add(new Student(2, "Bob", 21));

Collections.sort(students, new NameComparator());  // Sort by name
Collections.sort(students, new AgeComparator());   // Sort by age
```

**Java 8+ Lambda Expressions:**

```java
// Comparator with lambda
Collections.sort(students, (s1, s2) -> s1.name.compareTo(s2.name));

// Using Comparator static methods
Collections.sort(students, Comparator.comparing(s -> s.name));
students.sort(Comparator.comparing(Student::getName));

// Reverse order
students.sort(Comparator.comparing(Student::getAge).reversed());

// Multiple fields
students.sort(Comparator
    .comparing(Student::getAge)
    .thenComparing(Student::getName));

// Null-safe comparator
students.sort(Comparator
    .nullsFirst(Comparator.comparing(Student::getName)));
```

**When to Use:**
- **Comparable**: Natural ordering, single sorting logic
- **Comparator**: Multiple sorting criteria, external sorting logic

---

## 11. What are generics in Java?

**Answer:**

Generics enable types (classes and interfaces) to be parameters when defining classes, interfaces, and methods.

**Benefits:**
- Type safety at compile time
- No type casting needed
- Code reusability
- Implements generic algorithms

**Before Generics (Java 1.4):**

```java
List list = new ArrayList();
list.add("Hello");
list.add(10);  // No compile-time error

String str = (String) list.get(0);  // Type casting needed
String str2 = (String) list.get(1); // Runtime ClassCastException
```

**With Generics (Java 5+):**

```java
List<String> list = new ArrayList<>();
list.add("Hello");
// list.add(10);  // Compile-time error

String str = list.get(0);  // No casting needed
```

**Generic Class:**

```java
class Box<T> {
    private T value;
    
    public void set(T value) {
        this.value = value;
    }
    
    public T get() {
        return value;
    }
}

// Usage
Box<Integer> intBox = new Box<>();
intBox.set(10);
Integer value = intBox.get();

Box<String> strBox = new Box<>();
strBox.set("Hello");
String str = strBox.get();
```

**Generic Method:**

```java
class Util {
    // Generic method
    public static <T> void printArray(T[] array) {
        for (T element : array) {
            System.out.print(element + " ");
        }
    }
}

// Usage
Integer[] intArray = {1, 2, 3};
String[] strArray = {"A", "B", "C"};

Util.printArray(intArray);  // 1 2 3
Util.printArray(strArray);  // A B C
```

**Bounded Type Parameters:**

```java
// Upper bound (extends)
class NumberBox<T extends Number> {
    private T value;
    
    public void set(T value) {
        this.value = value;
    }
    
    public double getDoubleValue() {
        return value.doubleValue();  // Number method available
    }
}

// Usage
NumberBox<Integer> intBox = new NumberBox<>();  // OK
NumberBox<Double> doubleBox = new NumberBox<>();  // OK
// NumberBox<String> strBox = new NumberBox<>();  // Error

// Multiple bounds
class MultiBox<T extends Number & Comparable<T>> {
    // T must be Number and Comparable
}
```

**Wildcards:**

```java
// 1. Unbounded wildcard (?)
public void printList(List<?> list) {
    for (Object obj : list) {
        System.out.println(obj);
    }
}

// 2. Upper bounded wildcard (? extends Type)
public double sumNumbers(List<? extends Number> list) {
    double sum = 0;
    for (Number num : list) {
        sum += num.doubleValue();
    }
    return sum;
}

List<Integer> intList = Arrays.asList(1, 2, 3);
List<Double> doubleList = Arrays.asList(1.1, 2.2, 3.3);
sumNumbers(intList);    // OK
sumNumbers(doubleList); // OK

// 3. Lower bounded wildcard (? super Type)
public void addNumbers(List<? super Integer> list) {
    list.add(10);  // Can add Integer or subclasses
}

List<Number> numList = new ArrayList<>();
List<Object> objList = new ArrayList<>();
addNumbers(numList);  // OK
addNumbers(objList);  // OK
```

**Generic Interface:**

```java
interface Pair<K, V> {
    K getKey();
    V getValue();
}

class OrderedPair<K, V> implements Pair<K, V> {
    private K key;
    private V value;
    
    public OrderedPair(K key, V value) {
        this.key = key;
        this.value = value;
    }
    
    public K getKey() { return key; }
    public V getValue() { return value; }
}

// Usage
Pair<String, Integer> pair = new OrderedPair<>("Age", 25);
```

**Type Erasure:**

```java
// At compile time: List<String>
// At runtime: List (type information erased)

// This is why you can't do:
// new T();  // Error
// T[] array = new T[10];  // Error
// if (obj instanceof T) { }  // Error
```

---

## 12. What is multithreading in Java? Explain thread lifecycle.

**Answer:**

Multithreading is concurrent execution of multiple threads to maximize CPU utilization.

**Thread Lifecycle:**

```
New --> Runnable <--> Running --> Terminated
              |                     ^
              v                     |
            Blocked/Waiting/Timed Waiting
```

**States:**

1. **New**: Thread created but not started
2. **Runnable**: Ready to run, waiting for CPU
3. **Running**: Executing
4. **Blocked/Waiting**: Waiting for resource/notification
5. **Terminated**: Completed execution

**Creating Threads:**

**Method 1: Extending Thread Class**

```java
class MyThread extends Thread {
    @Override
    public void run() {
        for (int i = 0; i < 5; i++) {
            System.out.println(Thread.currentThread().getName() + ": " + i);
        }
    }
}

// Usage
MyThread t1 = new MyThread();
t1.start();  // Starts new thread
```

**Method 2: Implementing Runnable Interface (Preferred)**

```java
class MyRunnable implements Runnable {
    @Override
    public void run() {
        for (int i = 0; i < 5; i++) {
            System.out.println(Thread.currentThread().getName() + ": " + i);
        }
    }
}

// Usage
Thread t1 = new Thread(new MyRunnable());
t1.start();

// Or with lambda (Java 8+)
Thread t2 = new Thread(() -> {
    for (int i = 0; i < 5; i++) {
        System.out.println(Thread.currentThread().getName() + ": " + i);
    }
});
t2.start();
```

**Thread Methods:**

```java
Thread thread = new Thread(() -> {
    System.out.println("Thread running");
});

// Starting thread
thread.start();

// Getting thread info
thread.getName();
thread.getId();
thread.getPriority();
thread.getState();
thread.isAlive();

// Setting thread properties
thread.setName("MyThread");
thread.setPriority(Thread.MAX_PRIORITY);  // 1-10

// Sleep (pauses current thread)
Thread.sleep(1000);  // 1 second

// Join (wait for thread to die)
thread.join();
thread.join(1000);  // Wait max 1 second

// Interrupt
thread.interrupt();
thread.isInterrupted();
```

**Thread Priority:**

```java
Thread t1 = new Thread(() -> System.out.println("Task 1"));
Thread t2 = new Thread(() -> System.out.println("Task 2"));

t1.setPriority(Thread.MIN_PRIORITY);   // 1
t2.setPriority(Thread.MAX_PRIORITY);   // 10
// Thread.NORM_PRIORITY = 5 (default)

t1.start();
t2.start();
```

**Daemon Thread:**

```java
Thread daemon = new Thread(() -> {
    while (true) {
        System.out.println("Daemon running");
        try {
            Thread.sleep(1000);
        } catch (InterruptedException e) {
            break;
        }
    }
});

daemon.setDaemon(true);  // Must be set before start()
daemon.start();

// Daemon threads terminate when all user threads finish
```

**Thread Pool (ExecutorService):**

```java
// Fixed thread pool
ExecutorService executor = Executors.newFixedThreadPool(5);

for (int i = 0; i < 10; i++) {
    final int taskId = i;
    executor.submit(() -> {
        System.out.println("Task " + taskId + " by " + 
                          Thread.currentThread().getName());
    });
}

executor.shutdown();  // Graceful shutdown
// executor.shutdownNow();  // Immediate shutdown
```

**Why Runnable over Thread:**
- Can extend other classes (Java doesn't support multiple inheritance)
- Better separation of task from thread
- Can be used with ExecutorService
- More flexible and reusable

---

## 13. What is synchronization in Java?

**Answer:**

Synchronization controls access to shared resources by multiple threads to prevent data inconsistency.

**Why Synchronization:**

```java
// Without synchronization - Race condition
class Counter {
    private int count = 0;
    
    public void increment() {
        count++;  // Not atomic: read, increment, write
    }
    
    public int getCount() {
        return count;
    }
}

// Multiple threads incrementing
Counter counter = new Counter();
Thread t1 = new Thread(() -> {
    for (int i = 0; i < 1000; i++) counter.increment();
});
Thread t2 = new Thread(() -> {
    for (int i = 0; i < 1000; i++) counter.increment();
});

t1.start();
t2.start();
t1.join();
t2.join();

System.out.println(counter.getCount());  // May not be 2000!
```

**Types of Synchronization:**

**1. Method Synchronization:**

```java
class Counter {
    private int count = 0;
    
    // Synchronized method
    public synchronized void increment() {
        count++;
    }
    
    public synchronized int getCount() {
        return count;
    }
}

// Now thread-safe - output will be 2000
```

**2. Block Synchronization:**

```java
class Counter {
    private int count = 0;
    private Object lock = new Object();
    
    public void increment() {
        // Only synchronize critical section
        synchronized(lock) {
            count++;
        }
    }
}

// Or synchronize on this
class Counter {
    private int count = 0;
    
    public void increment() {
        synchronized(this) {
            count++;
        }
    }
}
```

**3. Static Synchronization:**

```java
class Counter {
    private static int count = 0;
    
    // Synchronized on class object
    public static synchronized void increment() {
        count++;
    }
}

// Or
class Counter {
    private static int count = 0;
    
    public static void increment() {
        synchronized(Counter.class) {
            count++;
        }
    }
}
```

**Inter-thread Communication:**

```java
class SharedResource {
    private int data;
    private boolean available = false;
    
    public synchronized void produce(int value) {
        while (available) {
            try {
                wait();  // Wait for consumer
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
        
        data = value;
        available = true;
        System.out.println("Produced: " + value);
        notify();  // Notify consumer
    }
    
    public synchronized int consume() {
        while (!available) {
            try {
                wait();  // Wait for producer
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
        
        available = false;
        System.out.println("Consumed: " + data);
        notify();  // Notify producer
        return data;
    }
}

// Producer thread
new Thread(() -> {
    SharedResource resource = new SharedResource();
    for (int i = 0; i < 5; i++) {
        resource.produce(i);
    }
}).start();

// Consumer thread
new Thread(() -> {
    SharedResource resource = new SharedResource();
    for (int i = 0; i < 5; i++) {
        resource.consume();
    }
}).start();
```

**Lock Interface (java.util.concurrent.locks):**

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
            lock.unlock();  // Always unlock in finally
        }
    }
}
```

**Deadlock:**

```java
// Deadlock example
class Resource1 {
    synchronized void method1(Resource2 r2) {
        System.out.println("Resource1: method1");
        r2.method2();
    }
    
    synchronized void method2() {
        System.out.println("Resource1: method2");
    }
}

class Resource2 {
    synchronized void method1(Resource1 r1) {
        System.out.println("Resource2: method1");
        r1.method2();
    }
    
    synchronized void method2() {
        System.out.println("Resource2: method2");
    }
}

// Thread 1: r1.method1(r2) - locks r1, waits for r2
// Thread 2: r2.method1(r1) - locks r2, waits for r1
// Deadlock!
```

**Avoiding Deadlock:**
- Lock ordering
- Lock timeout
- Deadlock detection

---

## 14. What are lambda expressions in Java 8?

**Answer:**

Lambda expressions enable functional programming in Java by providing concise syntax for anonymous functions.

**Syntax:**
```
(parameters) -> expression
(parameters) -> { statements; }
```

**Before Lambda (Anonymous Class):**

```java
// Runnable
Runnable r = new Runnable() {
    @Override
    public void run() {
        System.out.println("Running");
    }
};

// Comparator
List<String> list = Arrays.asList("C", "A", "B");
Collections.sort(list, new Comparator<String>() {
    @Override
    public int compare(String s1, String s2) {
        return s1.compareTo(s2);
    }
});
```

**With Lambda:**

```java
// Runnable
Runnable r = () -> System.out.println("Running");

// Comparator
List<String> list = Arrays.asList("C", "A", "B");
Collections.sort(list, (s1, s2) -> s1.compareTo(s2));
// Or even simpler
Collections.sort(list, String::compareTo);
```

**Lambda Syntax Examples:**

```java
// No parameters
() -> System.out.println("Hello")

// One parameter (parentheses optional)
x -> x * x
(x) -> x * x

// Multiple parameters
(x, y) -> x + y

// With type declaration
(int x, int y) -> x + y

// Multiple statements (braces required)
(x, y) -> {
    int sum = x + y;
    return sum;
}

// Return statement (explicit)
(x, y) -> { return x + y; }
```

**Functional Interface:**

```java
// Interface with single abstract method
@FunctionalInterface
interface Calculator {
    int calculate(int a, int b);
}

// Usage
Calculator add = (a, b) -> a + b;
Calculator subtract = (a, b) -> a - b;
Calculator multiply = (a, b) -> a * b;

System.out.println(add.calculate(5, 3));       // 8
System.out.println(subtract.calculate(5, 3));  // 2
System.out.println(multiply.calculate(5, 3));  // 15
```

**Built-in Functional Interfaces:**

```java
// 1. Predicate<T> - boolean test(T t)
Predicate<Integer> isEven = n -> n % 2 == 0;
System.out.println(isEven.test(4));  // true

// 2. Function<T,R> - R apply(T t)
Function<String, Integer> length = s -> s.length();
System.out.println(length.apply("Hello"));  // 5

// 3. Consumer<T> - void accept(T t)
Consumer<String> print = s -> System.out.println(s);
print.accept("Hello");  // Hello

// 4. Supplier<T> - T get()
Supplier<Double> random = () -> Math.random();
System.out.println(random.get());  // Random number

// 5. BiFunction<T,U,R> - R apply(T t, U u)
BiFunction<Integer, Integer, Integer> add = (a, b) -> a + b;
System.out.println(add.apply(5, 3));  // 8
```

**Method References:**

```java
// Static method reference
Function<String, Integer> parser = Integer::parseInt;
System.out.println(parser.apply("123"));  // 123

// Instance method reference
String str = "Hello";
Supplier<Integer> lengthSupplier = str::length;
System.out.println(lengthSupplier.get());  // 5

// Constructor reference
Supplier<ArrayList<String>> listSupplier = ArrayList::new;
ArrayList<String> list = listSupplier.get();
```

**Lambda with Collections:**

```java
List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5);

// forEach
numbers.forEach(n -> System.out.println(n));
numbers.forEach(System.out::println);

// removeIf
numbers.removeIf(n -> n % 2 == 0);  // Remove even numbers

// replaceAll
numbers.replaceAll(n -> n * 2);  // Double each element

// sort
numbers.sort((a, b) -> a - b);
```

**Benefits:**
- Concise code
- Functional programming support
- Better readability (when used properly)
- Enables Stream API

---

## 15. What is Stream API in Java 8?

**Answer:**

Stream API provides functional-style operations on collections for processing data declaratively.

**Key Features:**
- Not a data structure
- Doesn't modify source
- Lazy evaluation
- Can be infinite
- Consumable (use once)

**Creating Streams:**

```java
// 1. From Collection
List<String> list = Arrays.asList("A", "B", "C");
Stream<String> stream1 = list.stream();

// 2. From Array
String[] array = {"A", "B", "C"};
Stream<String> stream2 = Arrays.stream(array);

// 3. Stream.of()
Stream<String> stream3 = Stream.of("A", "B", "C");

// 4. Stream.generate()
Stream<Double> randomStream = Stream.generate(Math::random);

// 5. Stream.iterate()
Stream<Integer> numbers = Stream.iterate(0, n -> n + 1);

// 6. From File
Stream<String> lines = Files.lines(Paths.get("file.txt"));
```

**Intermediate Operations (return Stream):**

```java
List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9, 10);

// filter - Select elements
numbers.stream()
    .filter(n -> n % 2 == 0)
    .forEach(System.out::println);  // 2, 4, 6, 8, 10

// map - Transform elements
numbers.stream()
    .map(n -> n * n)
    .forEach(System.out::println);  // 1, 4, 9, 16, 25...

// flatMap - Flatten nested structures
List<List<Integer>> nested = Arrays.asList(
    Arrays.asList(1, 2),
    Arrays.asList(3, 4)
);
nested.stream()
    .flatMap(list -> list.stream())
    .forEach(System.out::println);  // 1, 2, 3, 4

// distinct - Remove duplicates
Arrays.asList(1, 2, 2, 3, 3, 3).stream()
    .distinct()
    .forEach(System.out::println);  // 1, 2, 3

// sorted - Sort elements
Arrays.asList(3, 1, 4, 1, 5).stream()
    .sorted()
    .forEach(System.out::println);  // 1, 1, 3, 4, 5

// limit - Limit size
numbers.stream()
    .limit(5)
    .forEach(System.out::println);  // 1, 2, 3, 4, 5

// skip - Skip elements
numbers.stream()
    .skip(5)
    .forEach(System.out::println);  // 6, 7, 8, 9, 10

// peek - Perform action without consuming
numbers.stream()
    .peek(n -> System.out.println("Processing: " + n))
    .map(n -> n * n)
    .forEach(System.out::println);
```

**Terminal Operations (return result):**

```java
List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5);

// forEach - Iterate
numbers.stream().forEach(System.out::println);

// collect - Collect to collection
List<Integer> squares = numbers.stream()
    .map(n -> n * n)
    .collect(Collectors.toList());

Set<Integer> set = numbers.stream()
    .collect(Collectors.toSet());

// toArray - Convert to array
Integer[] array = numbers.stream()
    .toArray(Integer[]::new);

// reduce - Reduce to single value
int sum = numbers.stream()
    .reduce(0, (a, b) -> a + b);

int product = numbers.stream()
    .reduce(1, (a, b) -> a * b);

// count - Count elements
long count = numbers.stream()
    .filter(n -> n % 2 == 0)
    .count();

// min/max - Find min/max
Optional<Integer> min = numbers.stream().min(Integer::compareTo);
Optional<Integer> max = numbers.stream().max(Integer::compareTo);

// anyMatch/allMatch/noneMatch - Test elements
boolean hasEven = numbers.stream().anyMatch(n -> n % 2 == 0);
boolean allPositive = numbers.stream().allMatch(n -> n > 0);
boolean noneNegative = numbers.stream().noneMatch(n -> n < 0);

// findFirst/findAny - Find element
Optional<Integer> first = numbers.stream().findFirst();
Optional<Integer> any = numbers.stream().findAny();
```

**Collectors:**

```java
List<String> names = Arrays.asList("Alice", "Bob", "Charlie", "David");

// toList/toSet
List<String> list = names.stream().collect(Collectors.toList());
Set<String> set = names.stream().collect(Collectors.toSet());

// joining - Concatenate strings
String result = names.stream()
    .collect(Collectors.joining(", "));  // "Alice, Bob, Charlie, David"

// groupingBy - Group elements
Map<Integer, List<String>> byLength = names.stream()
    .collect(Collectors.groupingBy(String::length));
// {3=[Bob], 5=[Alice, David], 7=[Charlie]}

// partitioningBy - Partition by predicate
Map<Boolean, List<Integer>> partition = numbers.stream()
    .collect(Collectors.partitioningBy(n -> n % 2 == 0));
// {false=[1, 3, 5], true=[2, 4]}

// counting
long count = names.stream()
    .collect(Collectors.counting());

// summingInt/averagingInt
int totalLength = names.stream()
    .collect(Collectors.summingInt(String::length));

double avgLength = names.stream()
    .collect(Collectors.averagingInt(String::length));

// summarizingInt - Get statistics
IntSummaryStatistics stats = numbers.stream()
    .collect(Collectors.summarizingInt(Integer::intValue));
System.out.println(stats.getMax());
System.out.println(stats.getAverage());
```

**Complex Example:**

```java
class Employee {
    String name;
    String department;
    int salary;
    // constructor, getters
}

List<Employee> employees = Arrays.asList(
    new Employee("Alice", "IT", 80000),
    new Employee("Bob", "HR", 60000),
    new Employee("Charlie", "IT", 90000),
    new Employee("David", "HR", 70000)
);

// Average salary by department
Map<String, Double> avgSalaryByDept = employees.stream()
    .collect(Collectors.groupingBy(
        Employee::getDepartment,
        Collectors.averagingInt(Employee::getSalary)
    ));

// Highest paid employee
Optional<Employee> highestPaid = employees.stream()
    .max(Comparator.comparing(Employee::getSalary));

// Names of IT employees with salary > 80000
List<String> itHighEarners = employees.stream()
    .filter(e -> e.getDepartment().equals("IT"))
    .filter(e -> e.getSalary() > 80000)
    .map(Employee::getName)
    .collect(Collectors.toList());
```

**Parallel Streams:**

```java
// Sequential stream
long sum = numbers.stream()
    .mapToInt(Integer::intValue)
    .sum();

// Parallel stream (uses multiple threads)
long parallelSum = numbers.parallelStream()
    .mapToInt(Integer::intValue)
    .sum();
```

**Benefits:**
- Declarative code
- Easier to parallelize
- Lazy evaluation (performance)
- Functional programming style
