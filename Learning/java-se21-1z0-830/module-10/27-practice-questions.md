# Module 10: Practice Questions - Stream Operations

## Questions (20)

---

### Question 1
```java
Stream.of(1, 2, 3, 4, 5)
      .filter(n -> n > 2)
      .map(n -> n * 2);
```
What is the result?

**A)** Prints 6, 8, 10  
**B)** Returns Stream<Integer> with 6, 8, 10  
**C)** Compilation error  
**D)** Nothing happens

**Answer: D)**

**Explanation:** No **terminal operation** is called. `filter()` and `map()` are intermediate operations (lazy). Without a terminal operation like `forEach()` or `collect()`, nothing executes.

```java
// To execute:
Stream.of(1, 2, 3, 4, 5)
      .filter(n -> n > 2)
      .map(n -> n * 2)
      .forEach(System.out::println); // Now executes
```

---

### Question 2
```java
List<String> names = Arrays.asList("Alice", "Bob", "Charlie");
long count = names.stream()
    .map(String::toUpperCase)
    .count();
System.out.println(count);
```
What is printed?

**A)** 0  
**B)** 3  
**C)** 15  
**D)** Compilation error

**Answer: B)**

**Explanation:** `count()` returns the number of elements in the stream. `map()` doesn't change the count, just transforms elements. Output: 3

---

### Question 3
```java
List<List<String>> nested = Arrays.asList(
    Arrays.asList("a", "b"),
    Arrays.asList("c", "d", "e")
);

List<String> result = nested.stream()
    .map(List::stream)
    .collect(Collectors.toList());
```
What type is `result`?

**A)** `List<String>`  
**B)** `List<Stream<String>>`  
**C)** Compilation error  
**D)** `Stream<String>`

**Answer: B)**

**Explanation:** `map(List::stream)` transforms each `List<String>` to `Stream<String>`, creating `Stream<Stream<String>>`. Collecting gives `List<Stream<String>>`.

```java
// To flatten, use flatMap:
List<String> flattened = nested.stream()
    .flatMap(List::stream)
    .collect(Collectors.toList()); // ["a", "b", "c", "d", "e"]
```

---

### Question 4
```java
List<Integer> numbers = Arrays.asList(5, 2, 8, 1, 9);
Optional<Integer> max = numbers.stream()
    .max(Comparator.naturalOrder());
System.out.println(max.get());
```
What is printed?

**A)** 1  
**B)** 5  
**C)** 9  
**D)** NoSuchElementException

**Answer: C)**

**Explanation:** `max()` with natural order finds the maximum value: 9. `get()` retrieves it (safe here since list is non-empty).

---

### Question 5
```java
Stream.of("a", "b", "c")
      .peek(s -> System.out.print(s + "1 "))
      .peek(s -> System.out.print(s + "2 "))
      .forEach(s -> System.out.print(s + "3 "));
```
What is printed?

**A)** a1 a2 a3 b1 b2 b3 c1 c2 c3  
**B)** a1 b1 c1 a2 b2 c2 a3 b3 c3  
**C)** a1 a2 a3  
**D)** Compilation error

**Answer: A)**

**Explanation:** Operations execute **element-by-element** through the pipeline. For "a": peek1, peek2, forEach. Then "b", then "c".

---

### Question 6
```java
List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5);
int result = numbers.stream()
    .reduce(1, (a, b) -> a * b);
System.out.println(result);
```
What is printed?

**A)** 15  
**B)** 120  
**C)** 1  
**D)** 0

**Answer: B)**

**Explanation:** `reduce(1, (a, b) -> a * b)` multiplies all elements starting with identity 1:
1 * 1 = 1, 1 * 2 = 2, 2 * 3 = 6, 6 * 4 = 24, 24 * 5 = **120**

---

### Question 7
```java
List<String> names = Arrays.asList("Alice", "Bob", "Charlie", "David");
boolean result = names.stream()
    .anyMatch(n -> n.length() > 10);
System.out.println(result);
```
What is printed?

**A)** true  
**B)** false  
**C)** Compilation error  
**D)** NoSuchElementException

**Answer: B)**

**Explanation:** None of the names have length > 10. `anyMatch()` returns **false** when no element matches.

---

### Question 8
```java
IntStream.rangeClosed(1, 5)
         .map(n -> n * 2)
         .filter(n -> n > 5)
         .forEach(System.out::print);
```
What is printed?

**A)** 2468  
**B)** 2468 10  
**C)** 2 4 6 8 10  
**D)** 6810

**Answer: D)**

**Explanation:**
- `rangeClosed(1, 5)`: 1, 2, 3, 4, 5
- `map(n -> n * 2)`: 2, 4, 6, 8, 10
- `filter(n -> n > 5)`: 6, 8, 10
- Output: **6810**

---

### Question 9
```java
List<String> words = Arrays.asList("apple", "banana", "cherry");
String result = words.stream()
    .reduce((a, b) -> a + "," + b)
    .orElse("");
System.out.println(result);
```
What is printed?

**A)** apple,banana,cherry  
**B)** ,apple,banana,cherry  
**C)** apple, banana, cherry  
**D)** Compilation error

**Answer: A)**

**Explanation:** `reduce()` without identity combines elements: "apple" + "," + "banana" = "apple,banana", then "apple,banana" + "," + "cherry" = "apple,banana,cherry"

---

### Question 10
```java
List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5);
numbers.stream()
       .filter(n -> n % 2 == 0)
       .map(n -> n * 2)
       .forEach(System.out::print);
```
What is printed?

**A)** 48  
**B)** 84  
**C)** 2468  
**D)** Nothing

**Answer: A)**

**Explanation:**
- Filter evens: 2, 4
- Map (*2): 4, 8
- Output: **48**

---

### Question 11
```java
Stream.of("a", "bb", "ccc")
      .flatMap(s -> Stream.of(s.split("")))
      .forEach(System.out::print);
```
What is printed?

**A)** abbccc  
**B)** a b b c c c  
**C)** abc  
**D)** Compilation error

**Answer: A)**

**Explanation:** `split("")` splits each string into characters:
- "a" → ["a"]
- "bb" → ["b", "b"]
- "ccc" → ["c", "c", "c"]

`flatMap()` flattens: a, b, b, c, c, c → **abbccc**

---

### Question 12
```java
List<Integer> numbers = Arrays.asList(3, 1, 4, 1, 5, 9, 2, 6);
List<Integer> result = numbers.stream()
    .distinct()
    .sorted()
    .limit(3)
    .collect(Collectors.toList());
System.out.println(result);
```
What is printed?

**A)** [1, 2, 3]  
**B)** [3, 1, 4]  
**C)** [1, 4, 5]  
**D)** [1, 1, 2]

**Answer: A)**

**Explanation:**
- `distinct()`: [3, 1, 4, 5, 9, 2, 6]
- `sorted()`: [1, 2, 3, 4, 5, 6, 9]
- `limit(3)`: [1, 2, 3]

---

### Question 13
```java
List<String> names = Arrays.asList("Alice", "Bob", "Charlie");
boolean result = names.stream()
    .noneMatch(n -> n.startsWith("Z"));
System.out.println(result);
```
What is printed?

**A)** true  
**B)** false  
**C)** Compilation error  
**D)** NoSuchElementException

**Answer: A)**

**Explanation:** `noneMatch()` returns **true** when NO element matches. None start with "Z", so result is **true**.

---

### Question 14
```java
IntStream.of(1, 2, 3, 4, 5)
         .skip(2)
         .limit(2)
         .forEach(System.out::print);
```
What is printed?

**A)** 12  
**B)** 34  
**C)** 345  
**D)** 45

**Answer: B)**

**Explanation:**
- Start: 1, 2, 3, 4, 5
- `skip(2)`: 3, 4, 5
- `limit(2)`: 3, 4
- Output: **34**

---

### Question 15
```java
List<Integer> numbers = Arrays.asList();
Optional<Integer> max = numbers.stream()
    .max(Comparator.naturalOrder());
System.out.println(max.isPresent());
```
What is printed?

**A)** true  
**B)** false  
**C)** NullPointerException  
**D)** NoSuchElementException

**Answer: B)**

**Explanation:** Empty stream. `max()` returns **empty Optional**. `isPresent()` returns **false**.

---

### Question 16
```java
Stream.of(1, 2, 3, 4, 5, 6)
      .takeWhile(n -> n < 4)
      .forEach(System.out::print);
```
What is printed?

**A)** 123  
**B)** 123456  
**C)** 456  
**D)** 1234

**Answer: A)**

**Explanation:** `takeWhile()` takes elements **while predicate is true**. Takes 1, 2, 3, stops at 4 (4 < 4 is false).

---

### Question 17
```java
List<String> words = Arrays.asList("apple", "banana", "cherry");
String result = words.stream()
    .reduce("Start", (a, b) -> a + "-" + b);
System.out.println(result);
```
What is printed?

**A)** apple-banana-cherry  
**B)** Start-apple-banana-cherry  
**C)** -apple-banana-cherry  
**D)** Compilation error

**Answer: B)**

**Explanation:** `reduce()` with identity "Start":
- "Start" + "-" + "apple" = "Start-apple"
- "Start-apple" + "-" + "banana" = "Start-apple-banana"
- "Start-apple-banana" + "-" + "cherry" = **"Start-apple-banana-cherry"**

---

### Question 18
```java
List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5);
boolean result = numbers.stream()
    .allMatch(n -> n > 0);
System.out.println(result);
```
What is printed?

**A)** true  
**B)** false  
**C)** Compilation error  
**D)** 0

**Answer: A)**

**Explanation:** `allMatch()` returns **true** if ALL elements match. All numbers are > 0, so **true**.

---

### Question 19
```java
Stream.of("a", "b", "c")
      .map(String::toUpperCase)
      .sorted()
      .findFirst()
      .ifPresent(System.out::println);
```
What is printed?

**A)** A  
**B)** C  
**C)** ABC  
**D)** Nothing

**Answer: A)**

**Explanation:**
- `map()`: "A", "B", "C"
- `sorted()`: "A", "B", "C" (already sorted)
- `findFirst()`: Optional["A"]
- `ifPresent()`: prints **"A"**

---

### Question 20
```java
IntStream.range(1, 10)
         .filter(n -> {
             System.out.print(n + " ");
             return n % 2 == 0;
         })
         .findFirst()
         .ifPresent(System.out::println);
```
What is printed?

**A)** 1 2 3 4 5 6 7 8 9 2  
**B)** 1 2 \n 2  
**C)** 1 2 2  
**D)** 2

**Answer: B)** (1 2 on one line, then 2 on next line)

**Explanation:** `findFirst()` **short-circuits**. Checks 1 (odd, continue), checks 2 (even, found). Prints "1 2 " from filter, then "2" from ifPresent.

---

## Score Interpretation

- **18-20 correct**: Excellent! You master stream operations.
- **15-17 correct**: Good understanding. Review flatMap and reduce.
- **12-14 correct**: Fair grasp. Study intermediate vs terminal operations.
- **Below 12**: Need more practice. Review all stream operation types.

---

**Previous:** [Theory - Stream Operations](27-stream-operations.md)  
**Next:** [Theory - Collectors](28-collectors.md)
