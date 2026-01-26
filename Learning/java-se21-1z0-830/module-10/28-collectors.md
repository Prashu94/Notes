# Module 10: Collectors - Advanced Stream Collection

## Table of Contents
1. [Collectors Overview](#collectors-overview)
2. [Basic Collectors](#basic-collectors)
3. [Joining Collectors](#joining-collectors)
4. [Grouping Collectors](#grouping-collectors)
5. [Partitioning Collectors](#partitioning-collectors)
6. [Summary Statistics](#summary-statistics)
7. [Downstream Collectors](#downstream-collectors)
8. [Custom Collectors](#custom-collectors)
9. [Teeing Collector (Java 12+)](#teeing-collector-java-12)
10. [Advanced Patterns](#advanced-patterns)
11. [Summary and Best Practices](#summary-and-best-practices)

---

## Collectors Overview

**Collectors** are pre-built reduction operations used with `collect()` terminal operation to accumulate stream elements into collections, strings, or summary statistics.

### Basic Syntax

```java
List<String> names = Arrays.asList("Alice", "Bob", "Charlie");

// Using collector
List<String> result = names.stream()
    .collect(Collectors.toList());

// Equivalent to
List<String> result2 = names.stream()
    .collect(ArrayList::new, ArrayList::add, ArrayList::addAll);
```

### Common Collectors

| Collector | Description | Example |
|-----------|-------------|---------|
| `toList()` | Collects to List | `Collectors.toList()` |
| `toSet()` | Collects to Set | `Collectors.toSet()` |
| `toMap()` | Collects to Map | `Collectors.toMap(k, v)` |
| `joining()` | Joins strings | `Collectors.joining(",")` |
| `counting()` | Counts elements | `Collectors.counting()` |
| `summingInt()` | Sums integers | `Collectors.summingInt(f)` |
| `averagingInt()` | Averages integers | `Collectors.averagingInt(f)` |
| `groupingBy()` | Groups elements | `Collectors.groupingBy(f)` |
| `partitioningBy()` | Partitions by predicate | `Collectors.partitioningBy(p)` |

---

## Basic Collectors

### toList(), toSet(), toCollection()

```java
List<String> names = Arrays.asList("Alice", "Bob", "Charlie", "Alice");

// To List
List<String> list = names.stream()
    .collect(Collectors.toList());
System.out.println(list); // [Alice, Bob, Charlie, Alice]

// To Set (removes duplicates)
Set<String> set = names.stream()
    .collect(Collectors.toSet());
System.out.println(set); // [Alice, Bob, Charlie]

// To specific collection type
ArrayList<String> arrayList = names.stream()
    .collect(Collectors.toCollection(ArrayList::new));

LinkedHashSet<String> linkedSet = names.stream()
    .collect(Collectors.toCollection(LinkedHashSet::new));

TreeSet<String> treeSet = names.stream()
    .collect(Collectors.toCollection(TreeSet::new));
System.out.println(treeSet); // [Alice, Bob, Charlie] - sorted

// To immutable list (Java 10+)
List<String> immutable = names.stream()
    .collect(Collectors.toUnmodifiableList());
```

### toMap()

Collects elements into a Map.

```java
class Employee {
    int id;
    String name;
    double salary;
    
    Employee(int id, String name, double salary) {
        this.id = id;
        this.name = name;
        this.salary = salary;
    }
}

List<Employee> employees = Arrays.asList(
    new Employee(1, "Alice", 50000),
    new Employee(2, "Bob", 75000),
    new Employee(3, "Charlie", 100000)
);

// Basic: key and value mappers
Map<Integer, String> idToName = employees.stream()
    .collect(Collectors.toMap(
        e -> e.id,          // key mapper
        e -> e.name         // value mapper
    ));
System.out.println(idToName); // {1=Alice, 2=Bob, 3=Charlie}

// With method references
Map<Integer, String> idToName2 = employees.stream()
    .collect(Collectors.toMap(
        Employee::getId,
        Employee::getName
    ));

// Map to entire object
Map<Integer, Employee> idToEmployee = employees.stream()
    .collect(Collectors.toMap(
        Employee::getId,
        e -> e              // or Function.identity()
    ));

// Handle duplicate keys with merge function
List<String> names = Arrays.asList("Alice", "Bob", "Alice", "Charlie");
Map<String, Integer> nameCount = names.stream()
    .collect(Collectors.toMap(
        name -> name,                    // key
        name -> 1,                       // value
        (existing, newValue) -> existing + newValue  // merge function
    ));
System.out.println(nameCount); // {Alice=2, Bob=1, Charlie=1}

// Specify Map implementation
Map<Integer, String> treeMap = employees.stream()
    .collect(Collectors.toMap(
        Employee::getId,
        Employee::getName,
        (e1, e2) -> e1,
        TreeMap::new
    ));
```

---

## Joining Collectors

### joining()

Concatenates strings with optional delimiter, prefix, and suffix.

```java
List<String> names = Arrays.asList("Alice", "Bob", "Charlie");

// Simple joining
String joined = names.stream()
    .collect(Collectors.joining());
System.out.println(joined); // AliceBobCharlie

// With delimiter
String withDelimiter = names.stream()
    .collect(Collectors.joining(", "));
System.out.println(withDelimiter); // Alice, Bob, Charlie

// With delimiter, prefix, and suffix
String formatted = names.stream()
    .collect(Collectors.joining(", ", "[", "]"));
System.out.println(formatted); // [Alice, Bob, Charlie]

// Complex example: format employee names
List<Employee> employees = Arrays.asList(
    new Employee(1, "Alice", 50000),
    new Employee(2, "Bob", 75000),
    new Employee(3, "Charlie", 100000)
);

String employeeNames = employees.stream()
    .map(Employee::getName)
    .collect(Collectors.joining(", ", "Employees: ", "."));
System.out.println(employeeNames); // Employees: Alice, Bob, Charlie.

// With transformation
String upperNames = names.stream()
    .map(String::toUpperCase)
    .collect(Collectors.joining(" | "));
System.out.println(upperNames); // ALICE | BOB | CHARLIE
```

---

## Grouping Collectors

### groupingBy()

Groups elements by a classifier function.

```java
class Employee {
    String name;
    String department;
    double salary;
    
    Employee(String name, String department, double salary) {
        this.name = name;
        this.department = department;
        this.salary = salary;
    }
}

List<Employee> employees = Arrays.asList(
    new Employee("Alice", "IT", 50000),
    new Employee("Bob", "HR", 60000),
    new Employee("Charlie", "IT", 75000),
    new Employee("David", "HR", 55000),
    new Employee("Eve", "IT", 80000)
);

// Basic grouping by department
Map<String, List<Employee>> byDept = employees.stream()
    .collect(Collectors.groupingBy(Employee::getDepartment));

System.out.println(byDept);
// {IT=[Alice, Charlie, Eve], HR=[Bob, David]}

// Count employees per department
Map<String, Long> countByDept = employees.stream()
    .collect(Collectors.groupingBy(
        Employee::getDepartment,
        Collectors.counting()
    ));
System.out.println(countByDept); // {IT=3, HR=2}

// Sum salaries by department
Map<String, Double> salaryByDept = employees.stream()
    .collect(Collectors.groupingBy(
        Employee::getDepartment,
        Collectors.summingDouble(Employee::getSalary)
    ));
System.out.println(salaryByDept); // {IT=205000.0, HR=115000.0}

// Average salary by department
Map<String, Double> avgSalaryByDept = employees.stream()
    .collect(Collectors.groupingBy(
        Employee::getDepartment,
        Collectors.averagingDouble(Employee::getSalary)
    ));
System.out.println(avgSalaryByDept); // {IT=68333.33, HR=57500.0}

// Get names only per department
Map<String, List<String>> namesByDept = employees.stream()
    .collect(Collectors.groupingBy(
        Employee::getDepartment,
        Collectors.mapping(
            Employee::getName,
            Collectors.toList()
        )
    ));
System.out.println(namesByDept);
// {IT=[Alice, Charlie, Eve], HR=[Bob, David]}

// Join names per department
Map<String, String> joinedNames = employees.stream()
    .collect(Collectors.groupingBy(
        Employee::getDepartment,
        Collectors.mapping(
            Employee::getName,
            Collectors.joining(", ")
        )
    ));
System.out.println(joinedNames);
// {IT=Alice, Charlie, Eve, HR=Bob, David}

// Multi-level grouping
class Transaction {
    String category;
    String type;
    double amount;
    
    Transaction(String category, String type, double amount) {
        this.category = category;
        this.type = type;
        this.amount = amount;
    }
}

List<Transaction> transactions = Arrays.asList(
    new Transaction("Food", "Debit", 50),
    new Transaction("Food", "Credit", 100),
    new Transaction("Transport", "Debit", 30),
    new Transaction("Transport", "Credit", 80)
);

Map<String, Map<String, List<Transaction>>> grouped = transactions.stream()
    .collect(Collectors.groupingBy(
        Transaction::getCategory,
        Collectors.groupingBy(Transaction::getType)
    ));

// {Food={Debit=[...], Credit=[...]}, Transport={Debit=[...], Credit=[...]}}

// Custom Map implementation
Map<String, List<Employee>> sortedMap = employees.stream()
    .collect(Collectors.groupingBy(
        Employee::getDepartment,
        TreeMap::new,              // Map supplier
        Collectors.toList()
    ));
```

---

## Partitioning Collectors

### partitioningBy()

Partitions elements into two groups based on a predicate (true/false).

```java
List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9, 10);

// Partition by even/odd
Map<Boolean, List<Integer>> evenOdd = numbers.stream()
    .collect(Collectors.partitioningBy(n -> n % 2 == 0));

System.out.println(evenOdd.get(true));  // [2, 4, 6, 8, 10]
System.out.println(evenOdd.get(false)); // [1, 3, 5, 7, 9]

// Count in each partition
Map<Boolean, Long> counts = numbers.stream()
    .collect(Collectors.partitioningBy(
        n -> n % 2 == 0,
        Collectors.counting()
    ));
System.out.println(counts); // {false=5, true=5}

// Employees example
List<Employee> employees = Arrays.asList(
    new Employee("Alice", "IT", 50000),
    new Employee("Bob", "HR", 60000),
    new Employee("Charlie", "IT", 75000)
);

// Partition by salary >= 60000
Map<Boolean, List<Employee>> salaryPartition = employees.stream()
    .collect(Collectors.partitioningBy(e -> e.salary >= 60000));

// Get high earners
List<Employee> highEarners = salaryPartition.get(true);
List<Employee> lowEarners = salaryPartition.get(false);

// Average salary in each partition
Map<Boolean, Double> avgSalary = employees.stream()
    .collect(Collectors.partitioningBy(
        e -> e.salary >= 60000,
        Collectors.averagingDouble(Employee::getSalary)
    ));

// Names in each partition
Map<Boolean, List<String>> namePartition = employees.stream()
    .collect(Collectors.partitioningBy(
        e -> e.salary >= 60000,
        Collectors.mapping(
            Employee::getName,
            Collectors.toList()
        )
    ));
```

---

## Summary Statistics

### summarizingInt(), summarizingLong(), summarizingDouble()

Collects count, sum, min, max, and average in one pass.

```java
List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9, 10);

IntSummaryStatistics stats = numbers.stream()
    .collect(Collectors.summarizingInt(Integer::intValue));

System.out.println("Count: " + stats.getCount());       // 10
System.out.println("Sum: " + stats.getSum());           // 55
System.out.println("Min: " + stats.getMin());           // 1
System.out.println("Max: " + stats.getMax());           // 10
System.out.println("Average: " + stats.getAverage());   // 5.5

// Employee salaries
List<Employee> employees = Arrays.asList(
    new Employee("Alice", "IT", 50000),
    new Employee("Bob", "HR", 60000),
    new Employee("Charlie", "IT", 75000),
    new Employee("David", "HR", 55000)
);

DoubleSummaryStatistics salaryStats = employees.stream()
    .collect(Collectors.summarizingDouble(Employee::getSalary));

System.out.println("Total Salary: " + salaryStats.getSum());      // 240000.0
System.out.println("Average Salary: " + salaryStats.getAverage()); // 60000.0
System.out.println("Highest Salary: " + salaryStats.getMax());     // 75000.0
System.out.println("Lowest Salary: " + salaryStats.getMin());      // 50000.0

// Per department statistics
Map<String, DoubleSummaryStatistics> statsByDept = employees.stream()
    .collect(Collectors.groupingBy(
        Employee::getDepartment,
        Collectors.summarizingDouble(Employee::getSalary)
    ));

statsByDept.forEach((dept, deptStats) -> {
    System.out.println(dept + " - Avg: " + deptStats.getAverage());
});
```

---

## Downstream Collectors

### mapping()

Transforms elements before collecting with another collector.

```java
List<Employee> employees = Arrays.asList(
    new Employee("Alice", "IT", 50000),
    new Employee("Bob", "HR", 60000),
    new Employee("Charlie", "IT", 75000)
);

// Collect names by department
Map<String, List<String>> namesByDept = employees.stream()
    .collect(Collectors.groupingBy(
        Employee::getDepartment,
        Collectors.mapping(Employee::getName, Collectors.toList())
    ));

// Collect unique departments
Set<String> departments = employees.stream()
    .collect(Collectors.mapping(Employee::getDepartment, Collectors.toSet()));
```

### filtering() (Java 9+)

Filters elements before collecting.

```java
// High earners by department
Map<String, List<Employee>> highEarnersByDept = employees.stream()
    .collect(Collectors.groupingBy(
        Employee::getDepartment,
        Collectors.filtering(
            e -> e.salary > 55000,
            Collectors.toList()
        )
    ));
```

### flatMapping() (Java 9+)

Flattens elements before collecting.

```java
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
        new Employee("Alice", "IT", 50000),
        new Employee("Charlie", "IT", 75000)
    )),
    new Department("HR", Arrays.asList(
        new Employee("Bob", "HR", 60000)
    ))
);

// All employee names across departments
Set<String> allNames = departments.stream()
    .collect(Collectors.flatMapping(
        d -> d.employees.stream().map(Employee::getName),
        Collectors.toSet()
    ));
```

---

## Custom Collectors

### Creating Custom Collectors

```java
// Custom collector to collect even and odd numbers
class EvenOddCollector implements Collector<Integer, Map<String, List<Integer>>, Map<String, List<Integer>>> {
    
    @Override
    public Supplier<Map<String, List<Integer>>> supplier() {
        return () -> {
            Map<String, List<Integer>> map = new HashMap<>();
            map.put("even", new ArrayList<>());
            map.put("odd", new ArrayList<>());
            return map;
        };
    }
    
    @Override
    public BiConsumer<Map<String, List<Integer>>, Integer> accumulator() {
        return (map, num) -> {
            if (num % 2 == 0) {
                map.get("even").add(num);
            } else {
                map.get("odd").add(num);
            }
        };
    }
    
    @Override
    public BinaryOperator<Map<String, List<Integer>>> combiner() {
        return (map1, map2) -> {
            map1.get("even").addAll(map2.get("even"));
            map1.get("odd").addAll(map2.get("odd"));
            return map1;
        };
    }
    
    @Override
    public Function<Map<String, List<Integer>>, Map<String, List<Integer>>> finisher() {
        return Function.identity();
    }
    
    @Override
    public Set<Characteristics> characteristics() {
        return Collections.singleton(Characteristics.IDENTITY_FINISH);
    }
}

// Usage
List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9, 10);
Map<String, List<Integer>> result = numbers.stream()
    .collect(new EvenOddCollector());
System.out.println(result); // {even=[2, 4, 6, 8, 10], odd=[1, 3, 5, 7, 9]}

// Using Collector.of() for simpler custom collectors
Collector<Integer, ?, Map<String, List<Integer>>> evenOddCollector = 
    Collector.of(
        () -> {
            Map<String, List<Integer>> map = new HashMap<>();
            map.put("even", new ArrayList<>());
            map.put("odd", new ArrayList<>());
            return map;
        },
        (map, num) -> {
            if (num % 2 == 0) map.get("even").add(num);
            else map.get("odd").add(num);
        },
        (map1, map2) -> {
            map1.get("even").addAll(map2.get("even"));
            map1.get("odd").addAll(map2.get("odd"));
            return map1;
        }
    );
```

---

## Teeing Collector (Java 12+)

### teeing()

Applies two collectors and merges results.

```java
List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9, 10);

// Calculate sum and count in one pass
record SumAndCount(int sum, long count) {}

SumAndCount result = numbers.stream()
    .collect(Collectors.teeing(
        Collectors.summingInt(Integer::intValue),
        Collectors.counting(),
        SumAndCount::new
    ));

System.out.println("Sum: " + result.sum());     // 55
System.out.println("Count: " + result.count()); // 10

// Min and max in one pass
record MinMax(Optional<Integer> min, Optional<Integer> max) {}

MinMax minMax = numbers.stream()
    .collect(Collectors.teeing(
        Collectors.minBy(Comparator.naturalOrder()),
        Collectors.maxBy(Comparator.naturalOrder()),
        MinMax::new
    ));

// Average using teeing
Double average = numbers.stream()
    .collect(Collectors.teeing(
        Collectors.summingInt(Integer::intValue),
        Collectors.counting(),
        (sum, count) -> (double) sum / count
    ));
```

---

## Advanced Patterns

### Complex Grouping and Collecting

```java
class Transaction {
    String customer;
    String product;
    double amount;
    LocalDate date;
    
    Transaction(String customer, String product, double amount, LocalDate date) {
        this.customer = customer;
        this.product = product;
        this.amount = amount;
        this.date = date;
    }
}

List<Transaction> transactions = Arrays.asList(
    new Transaction("Alice", "Laptop", 1000, LocalDate.of(2024, 1, 15)),
    new Transaction("Bob", "Mouse", 25, LocalDate.of(2024, 1, 20)),
    new Transaction("Alice", "Keyboard", 75, LocalDate.of(2024, 2, 10)),
    new Transaction("Charlie", "Monitor", 300, LocalDate.of(2024, 2, 15))
);

// Total spent by customer
Map<String, Double> totalByCustomer = transactions.stream()
    .collect(Collectors.groupingBy(
        Transaction::getCustomer,
        Collectors.summingDouble(Transaction::getAmount)
    ));

// Transactions by month
Map<Integer, List<Transaction>> byMonth = transactions.stream()
    .collect(Collectors.groupingBy(
        t -> t.date.getMonthValue()
    ));

// Top spender
Optional<Map.Entry<String, Double>> topSpender = totalByCustomer.entrySet()
    .stream()
    .max(Map.Entry.comparingByValue());

// Products bought by each customer
Map<String, Set<String>> productsByCustomer = transactions.stream()
    .collect(Collectors.groupingBy(
        Transaction::getCustomer,
        Collectors.mapping(
            Transaction::getProduct,
            Collectors.toSet()
        )
    ));
```

---

## Summary and Best Practices

### Choosing the Right Collector

```java
// Single collection: toList(), toSet()
List<String> names = stream.collect(Collectors.toList());

// Joining strings: joining()
String csv = stream.collect(Collectors.joining(","));

// Grouping: groupingBy()
Map<String, List<T>> grouped = stream.collect(Collectors.groupingBy(classifier));

// Boolean split: partitioningBy()
Map<Boolean, List<T>> partitioned = stream.collect(Collectors.partitioningBy(predicate));

// Statistics: summarizingInt/Long/Double()
IntSummaryStatistics stats = stream.collect(Collectors.summarizingInt(mapper));

// Custom: toMap() with merge function
Map<K, V> map = stream.collect(Collectors.toMap(k, v, mergeFunction));
```

### Performance Tips

1. **Use primitive collectors when possible:**
   ```java
   // GOOD
   int sum = stream.collect(Collectors.summingInt(Integer::intValue));
   
   // LESS EFFICIENT
   int sum2 = stream.mapToInt(Integer::intValue).sum();
   ```

2. **Avoid unnecessary downstream collectors:**
   ```java
   // GOOD
   Map<String, Long> counts = stream.collect(Collectors.groupingBy(f, Collectors.counting()));
   
   // BAD - creates intermediate lists
   Map<String, Integer> counts2 = stream.collect(Collectors.groupingBy(f))
       .entrySet().stream()
       .collect(Collectors.toMap(Map.Entry::getKey, e -> e.getValue().size()));
   ```

3. **Use concurrent collectors for parallel streams:**
   ```java
   Map<String, List<T>> concurrent = stream.parallel()
       .collect(Collectors.groupingByConcurrent(classifier));
   ```

### Exam Tips

- `toList()` and `toSet()` don't guarantee implementation type
- `toMap()` throws `IllegalStateException` on duplicate keys without merge function
- `groupingBy()` returns `HashMap` by default
- `partitioningBy()` always returns `Map<Boolean, List>` with both true/false keys
- `summarizing*()` collectors perform single-pass aggregation
- `mapping()` and `filtering()` are downstream collectors
- `teeing()` (Java 12+) combines two collectors
- Collectors are **mutable reduction** operations

---

**Previous:** [Practice Questions - Stream Operations](27-practice-questions.md)  
**Next:** [Practice Questions - Collectors](28-practice-questions.md)
