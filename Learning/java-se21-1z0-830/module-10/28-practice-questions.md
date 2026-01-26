# Module 10: Practice Questions - Collectors

## Questions (20)

---

### Question 1
```java
List<String> names = Arrays.asList("Alice", "Bob", "Charlie");
String result = names.stream()
    .collect(Collectors.joining());
System.out.println(result);
```
What is printed?

**A)** Alice, Bob, Charlie  
**B)** AliceBobCharlie  
**C)** [Alice, Bob, Charlie]  
**D)** Compilation error

**Answer: B)**

**Explanation:** `joining()` without arguments concatenates strings with **no delimiter**. Output: **AliceBobCharlie**

```java
// With delimiter
names.stream().collect(Collectors.joining(", ")); // Alice, Bob, Charlie

// With delimiter, prefix, suffix
names.stream().collect(Collectors.joining(", ", "[", "]")); // [Alice, Bob, Charlie]
```

---

### Question 2
```java
List<Integer> numbers = Arrays.asList(1, 2, 2, 3, 3, 3);
Set<Integer> result = numbers.stream()
    .collect(Collectors.toSet());
System.out.println(result.size());
```
What is printed?

**A)** 6  
**B)** 3  
**C)** 4  
**D)** Compilation error

**Answer: B)**

**Explanation:** `toSet()` removes duplicates. Unique elements: 1, 2, 3. Size: **3**

---

### Question 3
```java
class Employee {
    String name;
    String dept;
    Employee(String name, String dept) {
        this.name = name;
        this.dept = dept;
    }
}

List<Employee> employees = Arrays.asList(
    new Employee("Alice", "IT"),
    new Employee("Bob", "HR"),
    new Employee("Charlie", "IT")
);

Map<String, Long> result = employees.stream()
    .collect(Collectors.groupingBy(
        e -> e.dept,
        Collectors.counting()
    ));
System.out.println(result.get("IT"));
```
What is printed?

**A)** 1  
**B)** 2  
**C)** 3  
**D)** null

**Answer: B)**

**Explanation:** `groupingBy()` with `counting()` counts employees per department. IT has Alice and Charlie: **2**

---

### Question 4
```java
List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5);
IntSummaryStatistics stats = numbers.stream()
    .collect(Collectors.summarizingInt(Integer::intValue));
System.out.println(stats.getSum());
```
What is printed?

**A)** 5  
**B)** 15  
**C)** 3.0  
**D)** Compilation error

**Answer: B)**

**Explanation:** `summarizingInt()` collects statistics. Sum of 1+2+3+4+5 = **15**

---

### Question 5
```java
List<String> words = Arrays.asList("apple", "banana", "cherry");
Map<Integer, String> result = words.stream()
    .collect(Collectors.toMap(
        String::length,
        s -> s
    ));
```
What happens?

**A)** Creates map {5=apple, 6=banana, 6=cherry}  
**B)** Creates map {5=apple, 6=cherry}  
**C)** IllegalStateException at runtime  
**D)** Compilation error

**Answer: C)**

**Explanation:** "banana" and "cherry" both have length 6. **Duplicate keys** without merge function throw `IllegalStateException`.

```java
// Fix with merge function
Map<Integer, String> fixed = words.stream()
    .collect(Collectors.toMap(
        String::length,
        s -> s,
        (existing, replacement) -> existing  // Keep first
    ));
```

---

### Question 6
```java
List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5, 6);
Map<Boolean, List<Integer>> result = numbers.stream()
    .collect(Collectors.partitioningBy(n -> n % 2 == 0));
System.out.println(result.get(false).size());
```
What is printed?

**A)** 2  
**B)** 3  
**C)** 4  
**D)** 6

**Answer: B)**

**Explanation:** `partitioningBy()` splits by predicate. `false` partition contains odd numbers: 1, 3, 5. Size: **3**

---

### Question 7
```java
List<String> names = Arrays.asList("Alice", "Bob");
List<String> result = names.stream()
    .collect(Collectors.toCollection(LinkedList::new));
```
What type is `result`?

**A)** `List<String>`  
**B)** `LinkedList<String>`  
**C)** `ArrayList<String>`  
**D)** Compilation error

**Answer: B)**

**Explanation:** `toCollection(LinkedList::new)` returns **LinkedList<String>**. The variable type declaration uses the more specific type.

---

### Question 8
```java
List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5);
Double average = numbers.stream()
    .collect(Collectors.averagingInt(Integer::intValue));
System.out.println(average);
```
What is printed?

**A)** 3  
**B)** 3.0  
**C)** 15  
**D)** Compilation error

**Answer: B)**

**Explanation:** `averagingInt()` returns **Double**. Average of 1,2,3,4,5 is (1+2+3+4+5)/5 = **3.0**

---

### Question 9
```java
List<String> names = Arrays.asList("Alice", "Bob", "Charlie");
Map<String, List<String>> result = names.stream()
    .collect(Collectors.groupingBy(s -> s.substring(0, 1)));
System.out.println(result.size());
```
What is printed?

**A)** 1  
**B)** 2  
**C)** 3  
**D)** Compilation error

**Answer: C)**

**Explanation:** Groups by first character: "A" → [Alice], "B" → [Bob], "C" → [Charlie]. **3 groups**.

---

### Question 10
```java
List<Integer> empty = Arrays.asList();
Integer sum = empty.stream()
    .collect(Collectors.summingInt(Integer::intValue));
System.out.println(sum);
```
What is printed?

**A)** null  
**B)** 0  
**C)** NullPointerException  
**D)** Compilation error

**Answer: B)**

**Explanation:** `summingInt()` on empty stream returns **0** (identity value for sum).

---

### Question 11
```java
List<String> words = Arrays.asList("a", "bb", "ccc");
Map<Integer, List<String>> result = words.stream()
    .collect(Collectors.groupingBy(String::length));
System.out.println(result.get(2));
```
What is printed?

**A)** [bb]  
**B)** bb  
**C)** null  
**D)** [a, bb]

**Answer: A)**

**Explanation:** Groups by length. Length 2 has only "bb". Result is **List** containing **[bb]**.

---

### Question 12
```java
List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5);
Map<Boolean, List<Integer>> result = numbers.stream()
    .collect(Collectors.partitioningBy(n -> n > 10));
System.out.println(result.get(true));
```
What is printed?

**A)** []  
**B)** null  
**C)** [1, 2, 3, 4, 5]  
**D)** Compilation error

**Answer: A)**

**Explanation:** `partitioningBy()` always creates **both** true and false keys. No numbers > 10, so `true` maps to **empty list []**.

---

### Question 13
```java
List<String> names = Arrays.asList("Alice", "Bob", "Alice");
Map<String, Integer> result = names.stream()
    .collect(Collectors.toMap(
        s -> s,
        s -> 1,
        (a, b) -> a + b
    ));
System.out.println(result.get("Alice"));
```
What is printed?

**A)** 1  
**B)** 2  
**C)** 3  
**D)** IllegalStateException

**Answer: B)**

**Explanation:** Merge function `(a, b) -> a + b` handles duplicates. "Alice" appears twice: 1 + 1 = **2**

---

### Question 14
```java
List<Integer> numbers = Arrays.asList(5, 2, 8, 1, 9);
Optional<Integer> max = numbers.stream()
    .collect(Collectors.maxBy(Comparator.naturalOrder()));
System.out.println(max.get());
```
What is printed?

**A)** 1  
**B)** 5  
**C)** 9  
**D)** Compilation error

**Answer: C)**

**Explanation:** `maxBy()` with natural order finds maximum: **9**. Returns `Optional<Integer>`.

---

### Question 15
```java
class Employee {
    String dept;
    double salary;
    Employee(String dept, double salary) {
        this.dept = dept;
        this.salary = salary;
    }
}

List<Employee> employees = Arrays.asList(
    new Employee("IT", 50000),
    new Employee("IT", 75000),
    new Employee("HR", 60000)
);

Map<String, Double> result = employees.stream()
    .collect(Collectors.groupingBy(
        e -> e.dept,
        Collectors.summingDouble(e -> e.salary)
    ));
System.out.println(result.get("IT"));
```
What is printed?

**A)** 50000.0  
**B)** 75000.0  
**C)** 125000.0  
**D)** 2.0

**Answer: C)**

**Explanation:** `summingDouble()` sums salaries per department. IT: 50000 + 75000 = **125000.0**

---

### Question 16
```java
List<String> names = Arrays.asList("Alice", "Bob", "Charlie");
String result = names.stream()
    .collect(Collectors.joining(", ", "Names: ", "."));
System.out.println(result);
```
What is printed?

**A)** Alice, Bob, Charlie  
**B)** Names: Alice, Bob, Charlie.  
**C)** Names: Alice, Bob, Charlie  
**D)** [Names: Alice, Bob, Charlie.]

**Answer: B)**

**Explanation:** `joining(delimiter, prefix, suffix)` adds "Names: " at start, ", " between elements, "." at end: **Names: Alice, Bob, Charlie.**

---

### Question 17
```java
List<Integer> numbers = Arrays.asList();
IntSummaryStatistics stats = numbers.stream()
    .collect(Collectors.summarizingInt(Integer::intValue));
System.out.println(stats.getCount());
```
What is printed?

**A)** 0  
**B)** null  
**C)** -1  
**D)** NullPointerException

**Answer: A)**

**Explanation:** Empty stream. `summarizingInt()` returns statistics with count = **0**.

---

### Question 18
```java
List<String> words = Arrays.asList("apple", "banana", "cherry");
Map<String, String> result = words.stream()
    .collect(Collectors.toMap(
        s -> s.substring(0, 1),
        s -> s.toUpperCase(),
        (s1, s2) -> s1 + ", " + s2
    ));
System.out.println(result.get("c"));
```
What is printed?

**A)** cherry  
**B)** CHERRY  
**C)** c  
**D)** null

**Answer: B)**

**Explanation:** Key is first character "c", value is uppercase "CHERRY". Only one word starts with "c", so no merge. Result: **CHERRY**

---

### Question 19
```java
List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5, 6);
Map<Boolean, Long> result = numbers.stream()
    .collect(Collectors.partitioningBy(
        n -> n % 2 == 0,
        Collectors.counting()
    ));
System.out.println(result.get(true));
```
What is printed?

**A)** 2  
**B)** 3  
**C)** 4  
**D)** 6

**Answer: B)**

**Explanation:** `partitioningBy()` with `counting()` counts elements in each partition. Even numbers (2, 4, 6): **3**

---

### Question 20
```java
List<String> names = Arrays.asList("Alice", "Bob", "Charlie");
Map<Integer, String> result = names.stream()
    .collect(Collectors.toMap(
        String::length,
        Function.identity(),
        (s1, s2) -> s1
    ));
System.out.println(result.get(5));
```
What is printed?

**A)** Alice  
**B)** AliceCharlie  
**C)** Charlie  
**D)** null

**Answer: A)**

**Explanation:** Both "Alice" and "Charlie" have length 5. Merge function `(s1, s2) -> s1` **keeps the first**: **Alice**

---

## Score Interpretation

- **18-20 correct**: Excellent! You've mastered Collectors.
- **15-17 correct**: Good understanding. Review groupingBy and partitioningBy.
- **12-14 correct**: Fair grasp. Study toMap merge functions and downstream collectors.
- **Below 12**: Need more practice. Review all Collector types thoroughly.

---

**Previous:** [Theory - Collectors](28-collectors.md)  
**Next:** Module 11 - Concurrency
