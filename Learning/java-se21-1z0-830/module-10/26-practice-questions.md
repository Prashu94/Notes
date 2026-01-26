# Module 10: Practice Questions - Stream API Basics

## Questions (20)

---

### Question 1
```java
Stream<String> stream = Stream.of("a", "b", "c");
stream.forEach(System.out::println);
stream.forEach(System.out::println);
```
What happens?

**A)** Prints abc twice  
**B)** Prints abc once  
**C)** IllegalStateException at runtime  
**D)** Compilation error

**Answer: C)**

**Explanation:** Streams can only be consumed **once**. After the first `forEach`, the stream is closed. The second `forEach` throws `IllegalStateException: stream has already been operated upon or closed`.

```java
// Correct way - create new stream
Stream.of("a", "b", "c").forEach(System.out::println);
Stream.of("a", "b", "c").forEach(System.out::println); // OK
```

---

### Question 2
```java
IntStream stream = IntStream.range(1, 5);
System.out.println(stream.sum());
```
What is the output?

**A)** 15  
**B)** 10  
**C)** 5  
**D)** Compilation error

**Answer: B)**

**Explanation:** `IntStream.range(1, 5)` creates a stream with elements 1, 2, 3, 4 (end is **exclusive**). Sum = 1 + 2 + 3 + 4 = 10.

```java
IntStream.range(1, 5);      // 1, 2, 3, 4 (exclusive end)
IntStream.rangeClosed(1, 5); // 1, 2, 3, 4, 5 (inclusive end)
```

---

### Question 3
```java
List<String> list = Arrays.asList("a", "b", "c");
Stream<String> stream = list.stream()
    .filter(s -> s.length() > 1);
System.out.println("Stream created");
```
What happens when this code runs?

**A)** Prints "Stream created" and filters the list  
**B)** Filters the list then prints  
**C)** Prints "Stream created" without filtering  
**D)** Compilation error

**Answer: C)**

**Explanation:** Intermediate operations like `filter()` are **lazy**. They don't execute until a terminal operation is called. Only "Stream created" is printed.

```java
// To trigger execution, add terminal operation
stream.forEach(System.out::println); // Now filter executes
```

---

### Question 4
```java
Stream<Integer> stream = Stream.iterate(1, n -> n + 1);
List<Integer> result = stream.limit(5).collect(Collectors.toList());
System.out.println(result);
```
What is printed?

**A)** [1, 2, 3, 4, 5]  
**B)** [1]  
**C)** Infinite loop  
**D)** Compilation error

**Answer: A)**

**Explanation:** `Stream.iterate()` creates an **infinite** stream starting at 1, incrementing by 1. `limit(5)` is a **short-circuit** operation that takes only the first 5 elements.

---

### Question 5
```java
List<Integer> numbers = Arrays.asList(1, 2, 3);
Stream<Integer> stream = numbers.stream();
numbers.add(4);
stream.forEach(System.out::print);
```
What happens?

**A)** Prints 1234  
**B)** Prints 123  
**C)** UnsupportedOperationException  
**D)** ConcurrentModificationException

**Answer: C)**

**Explanation:** `Arrays.asList()` returns a **fixed-size** list. Calling `add()` throws `UnsupportedOperationException`. The stream is never consumed.

```java
// To create mutable list:
List<Integer> numbers = new ArrayList<>(Arrays.asList(1, 2, 3));
```

---

### Question 6
Which creates a parallel stream?

**A)** `list.stream().parallel()`  
**B)** `list.parallelStream()`  
**C)** Both A and B  
**D)** Neither

**Answer: C)**

**Explanation:** Both methods create parallel streams. `parallel()` converts an existing stream to parallel, while `parallelStream()` creates a parallel stream directly.

```java
list.stream().parallel().forEach(System.out::println);
list.parallelStream().forEach(System.out::println);
```

---

### Question 7
```java
IntStream.rangeClosed(1, 5).average();
```
What type is returned?

**A)** `double`  
**B)** `Optional<Double>`  
**C)** `OptionalDouble`  
**D)** `Double`

**Answer: C)**

**Explanation:** Primitive stream methods like `average()`, `min()`, `max()` return primitive Optional types: `OptionalDouble`, `OptionalInt`, or `OptionalLong`.

```java
OptionalDouble avg = IntStream.rangeClosed(1, 5).average();
System.out.println(avg.getAsDouble()); // 3.0
```

---

### Question 8
```java
Stream<String> stream = Stream.empty();
long count = stream.count();
System.out.println(count);
```
What is the output?

**A)** 0  
**B)** -1  
**C)** NullPointerException  
**D)** Compilation error

**Answer: A)**

**Explanation:** `Stream.empty()` creates an empty stream. `count()` returns 0 for an empty stream.

---

### Question 9
```java
List<String> names = Arrays.asList("Alice", "Bob", "Charlie");
names.stream()
     .filter(n -> n.length() > 3)
     .forEach(System.out::println);
```
What is printed?

**A)** Alice Bob Charlie  
**B)** Alice Charlie  
**C)** Bob  
**D)** Nothing

**Answer: B)**

**Explanation:** `filter()` keeps elements where the predicate is true. "Alice" (5 chars) and "Charlie" (7 chars) have length > 3. "Bob" (3 chars) is filtered out.

---

### Question 10
```java
IntStream stream = IntStream.of(1, 2, 3, 4, 5);
int sum = stream.sum();
int count = stream.count();
```
What happens?

**A)** sum=15, count=5  
**B)** Compilation error  
**C)** IllegalStateException at runtime  
**D)** sum=15, count=0

**Answer: C)**

**Explanation:** `sum()` is a **terminal operation** that consumes the stream. Calling `count()` on an already-consumed stream throws `IllegalStateException`.

```java
// Correct way - create new streams or collect statistics
IntSummaryStatistics stats = IntStream.of(1, 2, 3, 4, 5).summaryStatistics();
int sum = (int) stats.getSum();
long count = stats.getCount();
```

---

### Question 11
```java
Stream<Integer> stream = Stream.generate(() -> 5);
stream.forEach(System.out::println);
```
What happens?

**A)** Prints 5 once  
**B)** Prints 5 five times  
**C)** Infinite loop  
**D)** Compilation error

**Answer: C)**

**Explanation:** `Stream.generate()` creates an **infinite** stream. Without `limit()`, `forEach()` runs forever printing 5.

```java
// Correct way - limit the stream
Stream.generate(() -> 5).limit(10).forEach(System.out::println);
```

---

### Question 12
```java
List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5);
Stream<Integer> stream = numbers.stream()
    .peek(n -> System.out.print(n + " "))
    .filter(n -> n % 2 == 0);
```
What is printed?

**A)** 1 2 3 4 5  
**B)** 2 4  
**C)** Nothing  
**D)** Compilation error

**Answer: C)**

**Explanation:** `peek()` and `filter()` are **intermediate operations** (lazy). Without a **terminal operation**, nothing is executed or printed.

```java
// Add terminal operation
stream.collect(Collectors.toList()); // Now prints: 1 2 3 4 5
```

---

### Question 13
What is the output?
```java
IntStream.range(1, 4)
         .map(n -> n * 2)
         .forEach(System.out::print);
```

**A)** 123  
**B)** 246  
**C)** 2468  
**D)** 468

**Answer: B)**

**Explanation:** `range(1, 4)` produces 1, 2, 3. `map(n -> n * 2)` transforms to 2, 4, 6. Output: 246

---

### Question 14
```java
Stream<String> stream1 = Stream.of("a", "b");
Stream<String> stream2 = Stream.of("c", "d");
Stream<String> combined = Stream.concat(stream1, stream2);
combined.forEach(System.out::print);
```
What is printed?

**A)** ab  
**B)** cd  
**C)** abcd  
**D)** Compilation error

**Answer: C)**

**Explanation:** `Stream.concat()` concatenates two streams. The result contains all elements from both streams in order.

---

### Question 15
```java
List<Integer> list = Arrays.asList(3, 1, 4, 1, 5);
IntStream intStream = list.stream().mapToInt(Integer::intValue);
```
What type is `intStream`?

**A)** `Stream<Integer>`  
**B)** `IntStream`  
**C)** `Stream<int>`  
**D)** Compilation error

**Answer: B)**

**Explanation:** `mapToInt()` converts `Stream<Integer>` to `IntStream` to avoid boxing overhead.

```java
// IntStream provides primitive-specific operations
int sum = intStream.sum(); // More efficient than Stream<Integer>
```

---

### Question 16
```java
Stream<String> stream = Stream.of("a", "b", "c");
stream.filter(s -> s.equals("b"));
System.out.println(stream.count());
```
What is the output?

**A)** 1  
**B)** 3  
**C)** 0  
**D)** Compilation error

**Answer: D)**

**Explanation:** `filter()` returns a **new stream**. The original `stream` reference doesn't change. Then `count()` is called on the original unfiltered stream, but `filter()` result was not assigned, so this is a logic error. Actually, this compiles but `count()` returns 3 (original stream elements).

Wait, let me reconsider:

Actually, the code **compiles** but has a logical issue. The `filter()` creates a new stream but it's not assigned. `stream.count()` counts the original stream (3 elements). So the answer is **B) 3**.

Let me correct:

**Answer: B) 3**

**Explanation:** `filter()` creates a new stream, but since it's not assigned, the original `stream` is unchanged. `count()` counts all 3 elements: "a", "b", "c".

```java
// Correct way
long count = stream.filter(s -> s.equals("b")).count(); // 1
```

---

### Question 17
```java
List<String> list = List.of("a", "b", "c");
Stream<String> stream = list.stream();
list.remove("b");
stream.forEach(System.out::print);
```
What happens?

**A)** Prints abc  
**B)** Prints ac  
**C)** UnsupportedOperationException  
**D)** ConcurrentModificationException

**Answer: C)**

**Explanation:** `List.of()` creates an **immutable** list. Calling `remove()` throws `UnsupportedOperationException`. The stream is never consumed.

---

### Question 18
```java
OptionalDouble average = IntStream.range(1, 1).average();
System.out.println(average.isPresent());
```
What is printed?

**A)** true  
**B)** false  
**C)** NullPointerException  
**D)** Compilation error

**Answer: B)**

**Explanation:** `range(1, 1)` creates an **empty** stream (start == end with exclusive end). `average()` on an empty stream returns an empty `OptionalDouble`. `isPresent()` returns false.

```java
IntStream.range(1, 1).count(); // 0
```

---

### Question 19
```java
Stream.of("a", "b", "c")
      .parallel()
      .forEach(System.out::print);
```
Which statement is true?

**A)** Always prints "abc"  
**B)** Order is unpredictable  
**C)** Prints "cba"  
**D)** Compilation error

**Answer: B)**

**Explanation:** Parallel streams process elements concurrently. `forEach()` doesn't guarantee order. To preserve order, use `forEachOrdered()`.

```java
// Preserve order in parallel stream
Stream.of("a", "b", "c").parallel().forEachOrdered(System.out::print); // abc
```

---

### Question 20
```java
IntSummaryStatistics stats = IntStream.of(1, 2, 3, 4, 5)
    .summaryStatistics();
System.out.println(stats.getMax());
```
What is printed?

**A)** 1  
**B)** 5  
**C)** 15  
**D)** Compilation error

**Answer: B)**

**Explanation:** `summaryStatistics()` collects count, sum, min, max, and average. `getMax()` returns the maximum value, which is 5.

```java
stats.getMin();     // 1
stats.getMax();     // 5
stats.getSum();     // 15
stats.getAverage(); // 3.0
stats.getCount();   // 5
```

---

## Score Interpretation

- **18-20 correct**: Excellent! You understand Stream API fundamentals.
- **15-17 correct**: Good grasp. Review lazy evaluation and stream consumption.
- **12-14 correct**: Fair. Study stream lifecycle and characteristics.
- **Below 12**: Need more practice. Review all Stream API basics thoroughly.

---

**Previous:** [Theory - Stream API Basics](26-stream-api-basics.md)  
**Next:** [Theory - Stream Operations](27-stream-operations.md)
