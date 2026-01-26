# Module 10: Stream Operations - Intermediate and Terminal

## Table of Contents
1. [Intermediate Operations Overview](#intermediate-operations-overview)
2. [Filtering Operations](#filtering-operations)
3. [Mapping Operations](#mapping-operations)
4. [Sorting and Distinct](#sorting-and-distinct)
5. [Limiting and Skipping](#limiting-and-skipping)
6. [Peeking](#peeking)
7. [Terminal Operations Overview](#terminal-operations-overview)
8. [Collection Operations](#collection-operations)
9. [Reduction Operations](#reduction-operations)
10. [Matching and Finding](#matching-and-finding)
11. [Iteration Operations](#iteration-operations)
12. [Summary and Best Practices](#summary-and-best-practices)

---

## Intermediate Operations Overview

**Intermediate operations** return a new stream and are **lazy** - they don't execute until a terminal operation is invoked.

### Key Characteristics

```java
List<String> names = Arrays.asList("Alice", "Bob", "Charlie", "David");

// These don't execute yet
Stream<String> stream = names.stream()
    .filter(n -> {
        System.out.println("Filtering: " + n);
        return n.length() > 3;
    })
    .map(n -> {
        System.out.println("Mapping: " + n);
        return n.toUpperCase();
    });

System.out.println("No output yet - operations are lazy");

// Terminal operation triggers execution
List<String> result = stream.collect(Collectors.toList());
// Now prints:
// Filtering: Alice
// Mapping: Alice
// Filtering: Bob
// Filtering: Charlie
// Mapping: Charlie
// Filtering: David
// Mapping: David
```

### Common Intermediate Operations

| Operation | Description | Returns |
|-----------|-------------|---------|
| `filter()` | Filters elements based on predicate | Stream |
| `map()` | Transforms elements | Stream |
| `flatMap()` | Flattens nested streams | Stream |
| `distinct()` | Removes duplicates | Stream |
| `sorted()` | Sorts elements | Stream |
| `peek()` | Performs action without modifying stream | Stream |
| `limit()` | Limits stream size | Stream |
| `skip()` | Skips first n elements | Stream |
| `takeWhile()` | Takes while predicate is true | Stream |
| `dropWhile()` | Drops while predicate is true | Stream |

---

## Filtering Operations

### filter()

Keeps elements that match the predicate.

```java
List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9, 10);

// Filter even numbers
List<Integer> evens = numbers.stream()
    .filter(n -> n % 2 == 0)
    .collect(Collectors.toList());
System.out.println(evens); // [2, 4, 6, 8, 10]

// Chain multiple filters
List<Integer> filtered = numbers.stream()
    .filter(n -> n > 3)
    .filter(n -> n < 8)
    .filter(n -> n % 2 == 0)
    .collect(Collectors.toList());
System.out.println(filtered); // [4, 6]
```

### distinct()

Removes duplicate elements using `equals()`.

```java
List<Integer> numbers = Arrays.asList(1, 2, 2, 3, 3, 3, 4, 4, 5);

List<Integer> unique = numbers.stream()
    .distinct()
    .collect(Collectors.toList());
System.out.println(unique); // [1, 2, 3, 4, 5]

// Distinct with custom objects
class Person {
    String name;
    int age;
    
    Person(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Person)) return false;
        Person person = (Person) o;
        return age == person.age && Objects.equals(name, person.name);
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(name, age);
    }
}

List<Person> people = Arrays.asList(
    new Person("Alice", 25),
    new Person("Bob", 30),
    new Person("Alice", 25)
);

List<Person> uniquePeople = people.stream()
    .distinct()
    .collect(Collectors.toList());
System.out.println(uniquePeople.size()); // 2
```

### takeWhile() and dropWhile() (Java 9+)

`takeWhile()` takes elements while predicate is true, then stops.
`dropWhile()` drops elements while predicate is true, then takes the rest.

```java
List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9, 10);

// Take while less than 5
List<Integer> taken = numbers.stream()
    .takeWhile(n -> n < 5)
    .collect(Collectors.toList());
System.out.println(taken); // [1, 2, 3, 4]

// Drop while less than 5
List<Integer> dropped = numbers.stream()
    .dropWhile(n -> n < 5)
    .collect(Collectors.toList());
System.out.println(dropped); // [5, 6, 7, 8, 9, 10]

// Important: Stops at first false
List<Integer> numbers2 = Arrays.asList(1, 3, 5, 2, 4, 6);
List<Integer> taken2 = numbers2.stream()
    .takeWhile(n -> n < 5)
    .collect(Collectors.toList());
System.out.println(taken2); // [1, 3] - stops at 5, doesn't continue
```

---

## Mapping Operations

### map()

Transforms each element to another value.

```java
List<String> names = Arrays.asList("alice", "bob", "charlie");

// Convert to uppercase
List<String> upper = names.stream()
    .map(String::toUpperCase)
    .collect(Collectors.toList());
System.out.println(upper); // [ALICE, BOB, CHARLIE]

// Extract lengths
List<Integer> lengths = names.stream()
    .map(String::length)
    .collect(Collectors.toList());
System.out.println(lengths); // [5, 3, 7]

// Complex transformation
class Employee {
    String name;
    double salary;
    
    Employee(String name, double salary) {
        this.name = name;
        this.salary = salary;
    }
}

class EmployeeDTO {
    String name;
    String salaryRange;
    
    EmployeeDTO(String name, String salaryRange) {
        this.name = name;
        this.salaryRange = salaryRange;
    }
}

List<Employee> employees = Arrays.asList(
    new Employee("Alice", 50000),
    new Employee("Bob", 75000),
    new Employee("Charlie", 100000)
);

List<EmployeeDTO> dtos = employees.stream()
    .map(e -> new EmployeeDTO(
        e.name,
        e.salary < 60000 ? "Low" : e.salary < 90000 ? "Medium" : "High"
    ))
    .collect(Collectors.toList());
```

### mapToInt(), mapToLong(), mapToDouble()

Convert to primitive streams for better performance.

```java
List<String> numbers = Arrays.asList("1", "2", "3", "4", "5");

// Parse to int
int sum = numbers.stream()
    .mapToInt(Integer::parseInt)
    .sum();
System.out.println(sum); // 15

// Calculate average
OptionalDouble avg = numbers.stream()
    .mapToInt(Integer::parseInt)
    .average();
System.out.println(avg.getAsDouble()); // 3.0

// Complex example
List<Employee> employees = Arrays.asList(
    new Employee("Alice", 50000),
    new Employee("Bob", 75000),
    new Employee("Charlie", 100000)
);

double totalSalary = employees.stream()
    .mapToDouble(e -> e.salary)
    .sum();
System.out.println(totalSalary); // 225000.0

DoubleSummaryStatistics stats = employees.stream()
    .mapToDouble(e -> e.salary)
    .summaryStatistics();
System.out.println("Average: " + stats.getAverage()); // 75000.0
System.out.println("Max: " + stats.getMax()); // 100000.0
```

### flatMap()

Flattens nested structures into a single stream.

```java
// Flatten list of lists
List<List<Integer>> nestedList = Arrays.asList(
    Arrays.asList(1, 2, 3),
    Arrays.asList(4, 5),
    Arrays.asList(6, 7, 8, 9)
);

List<Integer> flattened = nestedList.stream()
    .flatMap(List::stream)
    .collect(Collectors.toList());
System.out.println(flattened); // [1, 2, 3, 4, 5, 6, 7, 8, 9]

// Split sentences into words
List<String> sentences = Arrays.asList(
    "Hello World",
    "Java Streams",
    "Are Powerful"
);

List<String> words = sentences.stream()
    .flatMap(s -> Arrays.stream(s.split(" ")))
    .collect(Collectors.toList());
System.out.println(words); // [Hello, World, Java, Streams, Are, Powerful]

// Flatten optional values
List<Optional<String>> optionals = Arrays.asList(
    Optional.of("A"),
    Optional.empty(),
    Optional.of("B"),
    Optional.empty(),
    Optional.of("C")
);

List<String> values = optionals.stream()
    .flatMap(Optional::stream) // Java 9+
    .collect(Collectors.toList());
System.out.println(values); // [A, B, C]

// Complex: flatten department employees
class Department {
    String name;
    List<Employee> employees;
    
    Department(String name, List<Employee> employees) {
        this.name = name;
        this.employees = employees;
    }
}

List<Department> departments = Arrays.asList(
    new Department("IT", Arrays.asList(
        new Employee("Alice", 50000),
        new Employee("Bob", 75000)
    )),
    new Department("HR", Arrays.asList(
        new Employee("Charlie", 60000)
    ))
);

List<Employee> allEmployees = departments.stream()
    .flatMap(d -> d.employees.stream())
    .collect(Collectors.toList());
```

### flatMapToInt(), flatMapToLong(), flatMapToDouble()

Flatten to primitive streams.

```java
List<int[]> arrays = Arrays.asList(
    new int[]{1, 2, 3},
    new int[]{4, 5},
    new int[]{6, 7, 8}
);

int sum = arrays.stream()
    .flatMapToInt(Arrays::stream)
    .sum();
System.out.println(sum); // 36
```

---

## Sorting and Distinct

### sorted()

Sorts elements in natural order or with a comparator.

```java
// Natural order
List<Integer> numbers = Arrays.asList(5, 2, 8, 1, 9, 3);
List<Integer> sorted = numbers.stream()
    .sorted()
    .collect(Collectors.toList());
System.out.println(sorted); // [1, 2, 3, 5, 8, 9]

// Reverse order
List<Integer> reversed = numbers.stream()
    .sorted(Comparator.reverseOrder())
    .collect(Collectors.toList());
System.out.println(reversed); // [9, 8, 5, 3, 2, 1]

// Custom comparator
List<String> names = Arrays.asList("Alice", "Bob", "Charlie", "David");

// Sort by length
List<String> byLength = names.stream()
    .sorted(Comparator.comparing(String::length))
    .collect(Collectors.toList());
System.out.println(byLength); // [Bob, Alice, David, Charlie]

// Sort by length, then alphabetically
List<String> combined = names.stream()
    .sorted(Comparator.comparing(String::length)
        .thenComparing(Comparator.naturalOrder()))
    .collect(Collectors.toList());

// Complex sorting
class Employee {
    String name;
    int age;
    double salary;
    
    Employee(String name, int age, double salary) {
        this.name = name;
        this.age = age;
        this.salary = salary;
    }
}

List<Employee> employees = Arrays.asList(
    new Employee("Alice", 30, 50000),
    new Employee("Bob", 25, 75000),
    new Employee("Charlie", 30, 60000)
);

// Sort by age, then by salary descending
List<Employee> sortedEmp = employees.stream()
    .sorted(Comparator.comparing(Employee::getAge)
        .thenComparing(Comparator.comparing(Employee::getSalary).reversed()))
    .collect(Collectors.toList());
```

---

## Limiting and Skipping

### limit()

Limits the stream to specified number of elements.

```java
List<Integer> numbers = IntStream.rangeClosed(1, 100)
    .boxed()
    .collect(Collectors.toList());

// First 10 numbers
List<Integer> first10 = numbers.stream()
    .limit(10)
    .collect(Collectors.toList());
System.out.println(first10); // [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

// Short-circuit with infinite streams
List<Integer> firstFive = Stream.iterate(1, n -> n + 1)
    .limit(5)
    .collect(Collectors.toList());
System.out.println(firstFive); // [1, 2, 3, 4, 5]
```

### skip()

Skips the first n elements.

```java
List<Integer> numbers = IntStream.rangeClosed(1, 10)
    .boxed()
    .collect(Collectors.toList());

// Skip first 5
List<Integer> skipped = numbers.stream()
    .skip(5)
    .collect(Collectors.toList());
System.out.println(skipped); // [6, 7, 8, 9, 10]

// Pagination with skip and limit
int pageSize = 3;
int pageNumber = 2; // 0-indexed

List<Integer> page = numbers.stream()
    .skip(pageNumber * pageSize)
    .limit(pageSize)
    .collect(Collectors.toList());
System.out.println(page); // [7, 8, 9]
```

---

## Peeking

### peek()

Performs an action on each element without modifying the stream. Useful for debugging.

```java
List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5);

List<Integer> result = numbers.stream()
    .peek(n -> System.out.println("Original: " + n))
    .map(n -> n * 2)
    .peek(n -> System.out.println("After map: " + n))
    .filter(n -> n > 5)
    .peek(n -> System.out.println("After filter: " + n))
    .collect(Collectors.toList());

// Output:
// Original: 1
// After map: 2
// Original: 2
// After map: 4
// Original: 3
// After map: 6
// After filter: 6
// ... etc

System.out.println("Final: " + result); // [6, 8, 10]
```

**Important:** `peek()` is intended for debugging. Don't use it for business logic as execution depends on terminal operations.

```java
// BAD - side effects in peek
List<String> names = new ArrayList<>();
Stream.of("a", "b", "c")
    .peek(names::add) // DON'T DO THIS
    .filter(s -> s.length() > 1);
// names might be empty if no terminal operation

// GOOD - use forEach
Stream.of("a", "b", "c")
    .filter(s -> s.length() > 1)
    .forEach(names::add);
```

---

## Terminal Operations Overview

**Terminal operations** produce a result or side-effect and consume the stream.

### Common Terminal Operations

| Operation | Description | Returns |
|-----------|-------------|---------|
| `collect()` | Collects into collection | Collection |
| `forEach()` | Performs action on each element | void |
| `forEachOrdered()` | Ordered forEach | void |
| `toArray()` | Converts to array | Array |
| `reduce()` | Reduces to single value | Optional/value |
| `count()` | Counts elements | long |
| `min()`/`max()` | Finds min/max | Optional |
| `findFirst()`/`findAny()` | Finds element | Optional |
| `anyMatch()`/`allMatch()`/`noneMatch()` | Tests predicate | boolean |
| `sum()`/`average()` | Primitive operations | int/long/double |

---

## Collection Operations

### collect() with Collectors

Converts stream to collections.

```java
List<String> names = Arrays.asList("Alice", "Bob", "Charlie");

// To List
List<String> list = names.stream()
    .collect(Collectors.toList());

// To Set
Set<String> set = names.stream()
    .collect(Collectors.toSet());

// To specific collection
ArrayList<String> arrayList = names.stream()
    .collect(Collectors.toCollection(ArrayList::new));

LinkedHashSet<String> linkedSet = names.stream()
    .collect(Collectors.toCollection(LinkedHashSet::new));

TreeSet<String> treeSet = names.stream()
    .collect(Collectors.toCollection(TreeSet::new));
```

### toArray()

Converts stream to array.

```java
List<String> names = Arrays.asList("Alice", "Bob", "Charlie");

// Object array
Object[] objArray = names.stream().toArray();

// Typed array
String[] strArray = names.stream().toArray(String[]::new);

// With transformation
Integer[] lengths = names.stream()
    .map(String::length)
    .toArray(Integer[]::new);
System.out.println(Arrays.toString(lengths)); // [5, 3, 7]
```

---

## Reduction Operations

### reduce()

Combines elements using an associative accumulation function.

```java
List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5);

// Sum with identity
int sum = numbers.stream()
    .reduce(0, (a, b) -> a + b);
System.out.println(sum); // 15

// Using Integer::sum
int sum2 = numbers.stream()
    .reduce(0, Integer::sum);

// Product
int product = numbers.stream()
    .reduce(1, (a, b) -> a * b);
System.out.println(product); // 120

// Without identity - returns Optional
Optional<Integer> max = numbers.stream()
    .reduce((a, b) -> a > b ? a : b);
max.ifPresent(System.out::println); // 5

// Using Math methods
Optional<Integer> max2 = numbers.stream()
    .reduce(Integer::max);

Optional<Integer> min = numbers.stream()
    .reduce(Integer::min);

// String concatenation
List<String> words = Arrays.asList("Java", "Stream", "API");
String combined = words.stream()
    .reduce("", (a, b) -> a + b);
System.out.println(combined); // JavaStreamAPI

// With delimiter
String joined = words.stream()
    .reduce("", (a, b) -> a.isEmpty() ? b : a + ", " + b);
System.out.println(joined); // Java, Stream, API
```

### count()

Counts elements in the stream.

```java
List<String> names = Arrays.asList("Alice", "Bob", "Charlie", "David");

long count = names.stream()
    .filter(n -> n.length() > 3)
    .count();
System.out.println(count); // 3

// Empty stream
long emptyCount = Stream.empty().count();
System.out.println(emptyCount); // 0
```

### min() and max()

Finds minimum or maximum element.

```java
List<Integer> numbers = Arrays.asList(5, 2, 8, 1, 9, 3);

// Natural order
Optional<Integer> min = numbers.stream().min(Comparator.naturalOrder());
Optional<Integer> max = numbers.stream().max(Comparator.naturalOrder());

min.ifPresent(n -> System.out.println("Min: " + n)); // 1
max.ifPresent(n -> System.out.println("Max: " + n)); // 9

// Custom comparator
class Employee {
    String name;
    double salary;
    
    Employee(String name, double salary) {
        this.name = name;
        this.salary = salary;
    }
}

List<Employee> employees = Arrays.asList(
    new Employee("Alice", 50000),
    new Employee("Bob", 75000),
    new Employee("Charlie", 100000)
);

Optional<Employee> highestPaid = employees.stream()
    .max(Comparator.comparing(e -> e.salary));

highestPaid.ifPresent(e -> System.out.println(e.name)); // Charlie
```

---

## Matching and Finding

### anyMatch(), allMatch(), noneMatch()

Test predicates on stream elements.

```java
List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5);

// anyMatch - at least one matches
boolean hasEven = numbers.stream()
    .anyMatch(n -> n % 2 == 0);
System.out.println(hasEven); // true

// allMatch - all match
boolean allPositive = numbers.stream()
    .allMatch(n -> n > 0);
System.out.println(allPositive); // true

boolean allEven = numbers.stream()
    .allMatch(n -> n % 2 == 0);
System.out.println(allEven); // false

// noneMatch - none match
boolean noneNegative = numbers.stream()
    .noneMatch(n -> n < 0);
System.out.println(noneNegative); // true

// Short-circuiting
Stream.of(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
    .peek(n -> System.out.println("Checking: " + n))
    .anyMatch(n -> n > 5);
// Only checks until 6, then stops
```

### findFirst() and findAny()

Finds an element in the stream.

```java
List<String> names = Arrays.asList("Alice", "Bob", "Charlie", "David");

// findFirst - first element
Optional<String> first = names.stream()
    .filter(n -> n.startsWith("C"))
    .findFirst();
first.ifPresent(System.out::println); // Charlie

// findAny - any element (useful for parallel streams)
Optional<String> any = names.stream()
    .filter(n -> n.length() > 3)
    .findAny();
any.ifPresent(System.out::println); // Alice (or any matching element)

// With parallel streams
Optional<String> anyParallel = names.parallelStream()
    .filter(n -> n.length() > 3)
    .findAny();
// Result is non-deterministic in parallel

// Empty stream
Optional<String> notFound = names.stream()
    .filter(n -> n.startsWith("Z"))
    .findFirst();
System.out.println(notFound.isPresent()); // false
```

---

## Iteration Operations

### forEach()

Performs action on each element.

```java
List<String> names = Arrays.asList("Alice", "Bob", "Charlie");

// Print each name
names.stream().forEach(System.out::println);

// Multiple statements
names.stream().forEach(name -> {
    String upper = name.toUpperCase();
    System.out.println(upper);
});

// Order not guaranteed in parallel
names.parallelStream().forEach(System.out::println);
// Output order is unpredictable
```

### forEachOrdered()

Maintains encounter order even in parallel streams.

```java
List<String> names = Arrays.asList("Alice", "Bob", "Charlie");

// Parallel but ordered
names.parallelStream()
    .forEachOrdered(System.out::println);
// Always prints: Alice, Bob, Charlie (in order)

// Compare with forEach
System.out.println("forEach (parallel):");
names.parallelStream().forEach(System.out::println);
// May print in any order

System.out.println("forEachOrdered (parallel):");
names.parallelStream().forEachOrdered(System.out::println);
// Always in order
```

---

## Summary and Best Practices

### Operation Pipeline Flow

```java
List<String> result = Stream.of("a", "bb", "ccc", "dddd", "eeeee")
    // Intermediate operations (lazy)
    .filter(s -> s.length() > 2)      // Filter
    .map(String::toUpperCase)          // Transform
    .sorted()                          // Sort
    .distinct()                        // Remove duplicates
    .peek(System.out::println)         // Debug
    .limit(3)                          // Limit
    // Terminal operation (eager)
    .collect(Collectors.toList());     // Collect
```

### Best Practices

1. **Choose appropriate operations:**
   ```java
   // GOOD - filter before map
   list.stream()
       .filter(s -> s.length() > 3)
       .map(String::toUpperCase)
       .collect(Collectors.toList());
   
   // BAD - map before filter (wastes transformations)
   list.stream()
       .map(String::toUpperCase)
       .filter(s -> s.length() > 3)
       .collect(Collectors.toList());
   ```

2. **Use primitive streams when possible:**
   ```java
   // GOOD
   int sum = list.stream()
       .mapToInt(Integer::intValue)
       .sum();
   
   // BAD - boxing overhead
   int sum2 = list.stream()
       .reduce(0, Integer::sum);
   ```

3. **Avoid stateful operations in parallel streams:**
   ```java
   // BAD - thread-unsafe
   List<String> result = new ArrayList<>();
   list.parallelStream()
       .forEach(result::add); // Race condition!
   
   // GOOD
   List<String> result2 = list.parallelStream()
       .collect(Collectors.toList());
   ```

4. **Use method references:**
   ```java
   // GOOD
   names.stream().map(String::toUpperCase)
   
   // Less clear
   names.stream().map(n -> n.toUpperCase())
   ```

5. **Handle Optional properly:**
   ```java
   // GOOD
   stream.findFirst()
       .ifPresent(System.out::println);
   
   // Or with default
   String result = stream.findFirst()
       .orElse("Not found");
   
   // BAD - defeats purpose of Optional
   if (stream.findFirst().isPresent()) {
       String value = stream.findFirst().get(); // Stream already consumed!
   }
   ```

### Exam Tips

- Intermediate operations are **lazy** and return streams
- Terminal operations are **eager** and consume streams
- Streams can only be used **once**
- `anyMatch()`, `allMatch()`, `noneMatch()` are **short-circuiting**
- `findFirst()` and `findAny()` are **short-circuiting**
- `forEach()` doesn't guarantee order in parallel; use `forEachOrdered()`
- `reduce()` without identity returns `Optional`
- `min()` and `max()` always return `Optional`
- `peek()` is for debugging, not business logic
- `flatMap()` flattens nested structures

---

**Previous:** [Practice Questions - Stream API Basics](26-practice-questions.md)  
**Next:** [Practice Questions - Stream Operations](27-practice-questions.md)
