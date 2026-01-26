# Module 10: Streams and Lambda - Stream API Basics

## Table of Contents
1. [Introduction to Stream API](#introduction-to-stream-api)
2. [Stream Creation](#stream-creation)
3. [Stream Characteristics](#stream-characteristics)
4. [Stream Pipeline Structure](#stream-pipeline-structure)
5. [Primitive Streams](#primitive-streams)
6. [Parallel Streams](#parallel-streams)
7. [Lazy Evaluation](#lazy-evaluation)
8. [Best Practices](#best-practices)

---

## Introduction to Stream API

The **Stream API**, introduced in Java 8, provides a functional approach to processing collections of data. Streams enable **declarative programming** - you specify **what** to do, not **how** to do it.

### What is a Stream?

A **stream** is a sequence of elements supporting sequential and parallel aggregate operations. It's NOT a data structure but a **pipeline** for processing data.

```java
import java.util.*;
import java.util.stream.*;

public class StreamIntro {
    public static void main(String[] args) {
        List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9, 10);
        
        // Traditional approach (imperative)
        List<Integer> evenSquares = new ArrayList<>();
        for (Integer num : numbers) {
            if (num % 2 == 0) {
                evenSquares.add(num * num);
            }
        }
        System.out.println(evenSquares); // [4, 16, 36, 64, 100]
        
        // Stream API approach (declarative)
        List<Integer> result = numbers.stream()
            .filter(n -> n % 2 == 0)      // Keep even numbers
            .map(n -> n * n)              // Square them
            .collect(Collectors.toList()); // Collect to list
        System.out.println(result); // [4, 16, 36, 64, 100]
    }
}
```

### Key Characteristics

- **Not a data structure**: Doesn't store elements
- **Functional**: Operations don't modify the source
- **Lazy**: Intermediate operations are not executed until terminal operation
- **Possibly unbounded**: Can represent infinite sequences
- **Consumable**: Can be traversed only once

```java
Stream<String> stream = Stream.of("a", "b", "c");
stream.forEach(System.out::println); // OK

// stream.forEach(System.out::println); // IllegalStateException - stream already consumed
```

---

## Stream Creation

### From Collections

```java
import java.util.*;
import java.util.stream.*;

public class StreamCreation {
    public static void main(String[] args) {
        // From List
        List<String> list = Arrays.asList("a", "b", "c");
        Stream<String> streamFromList = list.stream();
        
        // From Set
        Set<Integer> set = new HashSet<>(Arrays.asList(1, 2, 3));
        Stream<Integer> streamFromSet = set.stream();
        
        // From Map (via entries, keys, or values)
        Map<String, Integer> map = new HashMap<>();
        map.put("a", 1);
        map.put("b", 2);
        
        Stream<Map.Entry<String, Integer>> entryStream = map.entrySet().stream();
        Stream<String> keyStream = map.keySet().stream();
        Stream<Integer> valueStream = map.values().stream();
    }
}
```

### From Arrays

```java
public class ArrayStreams {
    public static void main(String[] args) {
        // From array using Arrays.stream()
        String[] array = {"Java", "Python", "C++", "JavaScript"};
        Stream<String> stream1 = Arrays.stream(array);
        
        // From array range
        int[] numbers = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};
        IntStream stream2 = Arrays.stream(numbers, 2, 7); // Elements from index 2 to 6
        stream2.forEach(System.out::println); // 3, 4, 5, 6, 7
        
        // From varargs using Stream.of()
        Stream<String> stream3 = Stream.of("a", "b", "c", "d");
    }
}
```

### Using Stream.of()

```java
public class StreamOfDemo {
    public static void main(String[] args) {
        // Create stream from individual elements
        Stream<String> stream1 = Stream.of("Apple", "Banana", "Cherry");
        
        // Create stream from array
        String[] fruits = {"Orange", "Grape", "Mango"};
        Stream<String> stream2 = Stream.of(fruits);
        
        // Single element stream
        Stream<String> stream3 = Stream.of("Single");
        
        // Empty stream
        Stream<String> emptyStream = Stream.empty();
    }
}
```

### Stream Builders

```java
public class StreamBuilderDemo {
    public static void main(String[] args) {
        // Using Stream.Builder
        Stream.Builder<String> builder = Stream.builder();
        builder.add("Alice");
        builder.add("Bob");
        builder.add("Charlie");
        Stream<String> stream = builder.build();
        
        // Fluent style
        Stream<Integer> numbers = Stream.<Integer>builder()
            .add(1)
            .add(2)
            .add(3)
            .build();
        
        numbers.forEach(System.out::println);
    }
}
```

### Generate and Iterate

```java
public class InfiniteStreams {
    public static void main(String[] args) {
        // Stream.generate() - infinite stream
        Stream<Double> randomNumbers = Stream.generate(Math::random);
        randomNumbers.limit(5).forEach(System.out::println);
        
        // Stream.iterate() - infinite stream with seed
        Stream<Integer> evenNumbers = Stream.iterate(0, n -> n + 2);
        evenNumbers.limit(10).forEach(System.out::println); // 0, 2, 4, 6, ... 18
        
        // Stream.iterate() with predicate (Java 9+)
        Stream<Integer> limitedStream = Stream.iterate(1, n -> n <= 100, n -> n * 2);
        limitedStream.forEach(System.out::println); // 1, 2, 4, 8, 16, 32, 64
    }
}
```

### From Files

```java
import java.nio.file.*;
import java.io.IOException;

public class FileStreams {
    public static void main(String[] args) throws IOException {
        // Read all lines from file
        Stream<String> lines = Files.lines(Paths.get("file.txt"));
        lines.forEach(System.out::println);
        lines.close(); // Important!
        
        // With try-with-resources
        try (Stream<String> fileLines = Files.lines(Paths.get("data.txt"))) {
            fileLines.filter(line -> line.contains("Java"))
                    .forEach(System.out::println);
        }
        
        // List files in directory
        try (Stream<Path> paths = Files.list(Paths.get("."))) {
            paths.filter(Files::isRegularFile)
                 .forEach(System.out::println);
        }
    }
}
```

### Other Stream Sources

```java
public class OtherStreamSources {
    public static void main(String[] args) {
        // From String characters (Java 9+)
        "Hello".chars()
               .mapToObj(c -> (char) c)
               .forEach(System.out::println);
        
        // From regex split
        String text = "Java,Python,C++,JavaScript";
        Stream<String> languages = java.util.regex.Pattern.compile(",")
            .splitAsStream(text);
        
        // From Optional
        Optional<String> optional = Optional.of("value");
        Stream<String> optionalStream = optional.stream();
        
        // Concatenate streams
        Stream<String> stream1 = Stream.of("a", "b");
        Stream<String> stream2 = Stream.of("c", "d");
        Stream<String> combined = Stream.concat(stream1, stream2);
        combined.forEach(System.out::println); // a, b, c, d
    }
}
```

---

## Stream Characteristics

### Ordered vs Unordered

```java
public class StreamOrdering {
    public static void main(String[] args) {
        // List maintains order
        List<String> list = Arrays.asList("a", "b", "c");
        list.stream().forEach(System.out::print); // abc
        
        // Set may not maintain order
        Set<String> set = new HashSet<>(Arrays.asList("a", "b", "c"));
        set.stream().forEach(System.out::print); // Order not guaranteed
        
        // LinkedHashSet maintains insertion order
        Set<String> linkedSet = new LinkedHashSet<>(Arrays.asList("c", "b", "a"));
        linkedSet.stream().forEach(System.out::print); // cba
        
        // Unordered stream
        Stream<String> unordered = Stream.of("x", "y", "z").unordered();
    }
}
```

### Sequential vs Parallel

```java
public class SequentialVsParallel {
    public static void main(String[] args) {
        List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8);
        
        // Sequential stream (default)
        numbers.stream()
               .forEach(n -> System.out.println(Thread.currentThread().getName() + ": " + n));
        
        // Parallel stream
        numbers.parallelStream()
               .forEach(n -> System.out.println(Thread.currentThread().getName() + ": " + n));
        
        // Convert to parallel
        numbers.stream()
               .parallel()
               .forEach(System.out::println);
        
        // Check if parallel
        boolean isParallel = numbers.parallelStream().isParallel(); // true
    }
}
```

---

## Stream Pipeline Structure

A stream pipeline consists of:
1. **Source**: Where the stream comes from
2. **Intermediate operations**: Transform the stream (lazy)
3. **Terminal operation**: Produces a result or side effect (eager)

```java
public class StreamPipeline {
    public static void main(String[] args) {
        List<String> names = Arrays.asList("Alice", "Bob", "Charlie", "David", "Eve");
        
        // Complete pipeline
        List<String> result = names.stream()              // Source
            .filter(name -> name.length() > 3)            // Intermediate
            .map(String::toUpperCase)                     // Intermediate
            .sorted()                                     // Intermediate
            .collect(Collectors.toList());                // Terminal
        
        System.out.println(result); // [ALICE, CHARLIE, DAVID]
    }
}
```

### Intermediate Operations (Lazy)

```java
public class IntermediateOperations {
    public static void main(String[] args) {
        List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5);
        
        // These operations are NOT executed yet
        Stream<Integer> stream = numbers.stream()
            .filter(n -> {
                System.out.println("Filtering: " + n);
                return n % 2 == 0;
            })
            .map(n -> {
                System.out.println("Mapping: " + n);
                return n * 2;
            });
        
        System.out.println("Pipeline created, nothing printed yet");
        
        // Terminal operation triggers execution
        System.out.println("Collecting...");
        List<Integer> result = stream.collect(Collectors.toList());
        
        // Output shows filter and map executed together for each element
    }
}
```

### Terminal Operations (Eager)

```java
public class TerminalOperations {
    public static void main(String[] args) {
        List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5);
        
        // forEach - void
        numbers.stream().forEach(System.out::println);
        
        // collect - collects to collection
        List<Integer> collected = numbers.stream().collect(Collectors.toList());
        
        // reduce - reduces to single value
        int sum = numbers.stream().reduce(0, Integer::sum);
        
        // count - returns long
        long count = numbers.stream().count();
        
        // anyMatch, allMatch, noneMatch - return boolean
        boolean hasEven = numbers.stream().anyMatch(n -> n % 2 == 0);
        
        // findFirst, findAny - return Optional
        Optional<Integer> first = numbers.stream().findFirst();
        
        // min, max - return Optional
        Optional<Integer> max = numbers.stream().max(Integer::compareTo);
        
        // toArray - converts to array
        Integer[] array = numbers.stream().toArray(Integer[]::new);
    }
}
```

---

## Primitive Streams

Special stream types for primitive values to avoid boxing/unboxing overhead.

### IntStream, LongStream, DoubleStream

```java
import java.util.stream.*;

public class PrimitiveStreams {
    public static void main(String[] args) {
        // IntStream - for int values
        IntStream intStream1 = IntStream.of(1, 2, 3, 4, 5);
        IntStream intStream2 = IntStream.range(1, 5);      // 1, 2, 3, 4 (exclusive end)
        IntStream intStream3 = IntStream.rangeClosed(1, 5); // 1, 2, 3, 4, 5 (inclusive)
        
        // LongStream - for long values
        LongStream longStream = LongStream.range(1L, 1000000L);
        
        // DoubleStream - for double values
        DoubleStream doubleStream = DoubleStream.of(1.1, 2.2, 3.3);
        
        // Generate infinite streams
        IntStream infiniteInts = IntStream.iterate(0, n -> n + 2);
        DoubleStream randomDoubles = DoubleStream.generate(Math::random);
    }
}
```

### Primitive Stream Operations

```java
public class PrimitiveStreamOps {
    public static void main(String[] args) {
        IntStream numbers = IntStream.rangeClosed(1, 10);
        
        // sum - returns primitive
        int sum = numbers.sum(); // 55
        
        // average - returns OptionalDouble
        OptionalDouble avg = IntStream.rangeClosed(1, 10).average();
        System.out.println(avg.getAsDouble()); // 5.5
        
        // min, max - returns OptionalInt
        OptionalInt min = IntStream.of(3, 1, 4, 1, 5).min();
        OptionalInt max = IntStream.of(3, 1, 4, 1, 5).max();
        
        // summaryStatistics - all statistics at once
        IntSummaryStatistics stats = IntStream.rangeClosed(1, 100).summaryStatistics();
        System.out.println("Count: " + stats.getCount());
        System.out.println("Sum: " + stats.getSum());
        System.out.println("Min: " + stats.getMin());
        System.out.println("Max: " + stats.getMax());
        System.out.println("Average: " + stats.getAverage());
    }
}
```

### Converting Between Stream Types

```java
public class StreamConversion {
    public static void main(String[] args) {
        // Primitive to Object stream
        Stream<Integer> objectStream = IntStream.rangeClosed(1, 5)
            .boxed(); // IntStream -> Stream<Integer>
        
        // Object to primitive stream
        List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5);
        IntStream intStream = numbers.stream()
            .mapToInt(Integer::intValue); // Stream<Integer> -> IntStream
        
        // Map to different primitive type
        DoubleStream doubles = IntStream.rangeClosed(1, 5)
            .mapToDouble(n -> n * 1.5);
        
        LongStream longs = IntStream.rangeClosed(1, 5)
            .mapToLong(n -> n * 100L);
        
        // FlatMap variants
        IntStream flatMapped = Stream.of(
            Arrays.asList(1, 2),
            Arrays.asList(3, 4, 5)
        ).flatMapToInt(list -> list.stream().mapToInt(Integer::intValue));
    }
}
```

---

## Parallel Streams

Parallel streams use multiple threads to process elements concurrently.

### Creating Parallel Streams

```java
public class ParallelStreamCreation {
    public static void main(String[] args) {
        List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9, 10);
        
        // Method 1: parallelStream()
        numbers.parallelStream()
               .forEach(System.out::println);
        
        // Method 2: parallel() on existing stream
        numbers.stream()
               .parallel()
               .forEach(System.out::println);
        
        // Convert back to sequential
        numbers.parallelStream()
               .sequential()
               .forEach(System.out::println);
    }
}
```

### When to Use Parallel Streams

```java
import java.time.*;

public class ParallelPerformance {
    public static void main(String[] args) {
        List<Integer> largeList = IntStream.rangeClosed(1, 1_000_000)
            .boxed()
            .collect(Collectors.toList());
        
        // Sequential processing
        Instant start1 = Instant.now();
        long sum1 = largeList.stream()
            .mapToLong(Integer::longValue)
            .sum();
        Instant end1 = Instant.now();
        System.out.println("Sequential: " + Duration.between(start1, end1).toMillis() + "ms");
        
        // Parallel processing
        Instant start2 = Instant.now();
        long sum2 = largeList.parallelStream()
            .mapToLong(Integer::longValue)
            .sum();
        Instant end2 = Instant.now();
        System.out.println("Parallel: " + Duration.between(start2, end2).toMillis() + "ms");
        
        // Good use cases for parallel streams:
        // - Large datasets
        // - CPU-intensive operations
        // - Independent operations (no shared state)
        
        // Avoid parallel streams when:
        // - Small datasets (overhead > benefit)
        // - I/O operations
        // - Operations modifying shared state
    }
}
```

### Parallel Stream Gotchas

```java
public class ParallelStreamIssues {
    public static void main(String[] args) {
        List<Integer> numbers = IntStream.rangeClosed(1, 10)
            .boxed()
            .collect(Collectors.toList());
        
        // BAD: Non-thread-safe collection
        List<Integer> results = new ArrayList<>();
        numbers.parallelStream()
               .forEach(results::add); // Race condition!
        System.out.println(results.size()); // May not be 10
        
        // GOOD: Use collect
        List<Integer> safeResults = numbers.parallelStream()
            .collect(Collectors.toList());
        
        // BAD: Order may not be preserved
        numbers.parallelStream()
               .forEach(System.out::print); // Order unpredictable
        
        // GOOD: Use forEachOrdered
        numbers.parallelStream()
               .forEachOrdered(System.out::print); // Preserves order
    }
}
```

---

## Lazy Evaluation

Intermediate operations are **lazy** - they don't execute until a terminal operation is called.

### Demonstrating Lazy Evaluation

```java
public class LazyEvaluation {
    public static void main(String[] args) {
        List<String> names = Arrays.asList("Alice", "Bob", "Charlie", "David");
        
        // Creating the pipeline - NO execution yet
        System.out.println("Creating pipeline...");
        Stream<String> stream = names.stream()
            .filter(name -> {
                System.out.println("Filtering: " + name);
                return name.length() > 3;
            })
            .map(name -> {
                System.out.println("Mapping: " + name);
                return name.toUpperCase();
            });
        
        System.out.println("Pipeline created, but nothing executed yet!");
        
        // Terminal operation triggers execution
        System.out.println("\nCalling terminal operation...");
        List<String> result = stream.collect(Collectors.toList());
        
        System.out.println("\nResult: " + result);
    }
}
```

### Short-Circuit Operations

Some operations can **short-circuit**, meaning they don't need to process all elements.

```java
public class ShortCircuiting {
    public static void main(String[] args) {
        List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9, 10);
        
        // findFirst - stops after finding first match
        Optional<Integer> first = numbers.stream()
            .filter(n -> {
                System.out.println("Checking: " + n);
                return n > 5;
            })
            .findFirst();
        System.out.println("First: " + first.get()); // Only checks 1-6
        
        // limit - processes only n elements
        numbers.stream()
               .peek(n -> System.out.println("Processing: " + n))
               .limit(3)
               .forEach(System.out::println); // Only processes 3 elements
        
        // anyMatch - stops when condition is true
        boolean hasEven = numbers.stream()
            .peek(n -> System.out.println("Checking: " + n))
            .anyMatch(n -> n % 2 == 0); // Stops at 2
        
        // takeWhile (Java 9+) - takes elements while condition is true
        List<Integer> taken = Stream.of(1, 2, 3, 4, 5, 1, 2, 3)
            .takeWhile(n -> n < 4)
            .collect(Collectors.toList()); // [1, 2, 3]
        
        // dropWhile (Java 9+) - drops elements while condition is true
        List<Integer> dropped = Stream.of(1, 2, 3, 4, 5, 1, 2, 3)
            .dropWhile(n -> n < 4)
            .collect(Collectors.toList()); // [4, 5, 1, 2, 3]
    }
}
```

---

## Best Practices

### 1. Choose Appropriate Stream Type

```java
public class StreamTypeChoice {
    public static void main(String[] args) {
        // BAD: Boxing overhead
        Stream<Integer> stream1 = Stream.of(1, 2, 3, 4, 5);
        int sum1 = stream1.mapToInt(Integer::intValue).sum();
        
        // GOOD: Use primitive stream directly
        int sum2 = IntStream.rangeClosed(1, 5).sum();
        
        // BAD: Creating stream just for single operation
        List<String> names = Arrays.asList("Alice", "Bob");
        names.stream().forEach(System.out::println);
        
        // GOOD: Use forEach directly
        names.forEach(System.out::println);
    }
}
```

### 2. Avoid Side Effects

```java
public class AvoidSideEffects {
    public static void main(String[] args) {
        List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5);
        
        // BAD: Modifying external state
        List<Integer> evenNumbers = new ArrayList<>();
        numbers.stream()
               .filter(n -> n % 2 == 0)
               .forEach(evenNumbers::add); // Side effect!
        
        // GOOD: Use collect
        List<Integer> evens = numbers.stream()
            .filter(n -> n % 2 == 0)
            .collect(Collectors.toList());
    }
}
```

### 3. Close Streams When Necessary

```java
import java.nio.file.*;
import java.io.IOException;

public class CloseStreams {
    public static void main(String[] args) {
        // BAD: Stream not closed
        try {
            Stream<String> lines = Files.lines(Paths.get("file.txt"));
            lines.forEach(System.out::println);
            // lines.close(); // Might forget
        } catch (IOException e) {
            e.printStackTrace();
        }
        
        // GOOD: Try-with-resources
        try (Stream<String> lines = Files.lines(Paths.get("file.txt"))) {
            lines.forEach(System.out::println);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
```

### 4. Use Method References

```java
public class MethodReferences {
    public static void main(String[] args) {
        List<String> names = Arrays.asList("Alice", "Bob", "Charlie");
        
        // Less concise
        names.stream()
             .map(name -> name.toUpperCase())
             .forEach(name -> System.out.println(name));
        
        // Better
        names.stream()
             .map(String::toUpperCase)
             .forEach(System.out::println);
    }
}
```

### 5. Understand Stream Consumption

```java
public class StreamConsumption {
    public static void main(String[] args) {
        List<String> names = Arrays.asList("Alice", "Bob", "Charlie");
        
        // Create stream
        Stream<String> stream = names.stream();
        
        // First terminal operation - OK
        long count = stream.count();
        
        // Second terminal operation - ERROR!
        // stream.forEach(System.out::println); // IllegalStateException
        
        // Solution: Create new stream
        names.stream().forEach(System.out::println);
    }
}
```

---

## Summary

### Key Points

- **Stream**: Sequence of elements supporting functional-style operations
- **Not a data structure**: Pipeline for processing data from a source
- **Creation**: From collections, arrays, files, generators, etc.
- **Pipeline**: Source → Intermediate operations (lazy) → Terminal operation (eager)
- **Primitive streams**: IntStream, LongStream, DoubleStream (avoid boxing)
- **Parallel streams**: For large datasets and CPU-intensive operations
- **Lazy evaluation**: Operations don't execute until terminal operation
- **Consumable**: Can only be used once

### Stream Lifecycle

```java
List<String> data = Arrays.asList("a", "b", "c");

// 1. Create stream
Stream<String> stream = data.stream();

// 2. Apply intermediate operations (lazy)
stream = stream.filter(s -> s.length() > 1)
               .map(String::toUpperCase);

// 3. Apply terminal operation (triggers execution)
List<String> result = stream.collect(Collectors.toList());

// 4. Stream is now consumed and cannot be reused
```

### Important for Exam

```java
// Streams are not reusable
Stream<String> stream = Stream.of("a", "b", "c");
stream.forEach(System.out::println); // OK
// stream.count(); // IllegalStateException

// Primitive streams avoid boxing
IntStream.range(1, 100).sum(); // Efficient
Stream.of(1, 2, 3).mapToInt(Integer::intValue).sum(); // Less efficient

// Parallel streams may not preserve order
List.of(1, 2, 3).parallelStream().forEach(System.out::print); // Order not guaranteed
List.of(1, 2, 3).parallelStream().forEachOrdered(System.out::print); // Order preserved

// Close streams from I/O sources
try (Stream<String> lines = Files.lines(path)) {
    // Use stream
} // Automatically closed
```

---

**Previous:** [Practice Questions - Lambda Expressions](25-practice-questions.md)  
**Next:** [Practice Questions - Stream API Basics](26-practice-questions.md)
