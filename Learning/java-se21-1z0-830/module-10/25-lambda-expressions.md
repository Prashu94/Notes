# Module 10: Streams and Lambda - Lambda Expressions

## Table of Contents
1. [Introduction to Lambda Expressions](#introduction-to-lambda-expressions)
2. [Lambda Syntax](#lambda-syntax)
3. [Functional Interfaces](#functional-interfaces)
4. [Method References](#method-references)
5. [Variable Capture and Scope](#variable-capture-and-scope)
6. [Common Use Cases](#common-use-cases)
7. [Best Practices](#best-practices)

---

## Introduction to Lambda Expressions

**Lambda expressions** are a concise way to represent anonymous functions (methods without names). Introduced in Java 8, they enable **functional programming** and make code more readable and maintainable.

### Why Lambda Expressions?

```java
// Before Java 8 - Anonymous Inner Class
Runnable r1 = new Runnable() {
    @Override
    public void run() {
        System.out.println("Hello World");
    }
};

// Java 8+ - Lambda Expression
Runnable r2 = () -> System.out.println("Hello World");

// Before - Comparator
Collections.sort(names, new Comparator<String>() {
    @Override
    public int compare(String s1, String s2) {
        return s1.compareTo(s2);
    }
});

// After - Lambda
Collections.sort(names, (s1, s2) -> s1.compareTo(s2));

// Even better - Method Reference
Collections.sort(names, String::compareTo);
```

### Key Benefits

- **Concise syntax**: Less boilerplate code
- **Improved readability**: Focus on behavior, not syntax
- **Functional programming**: Treat functions as first-class citizens
- **Stream API enabler**: Powers modern data processing
- **Better performance**: Potential for lazy evaluation and parallelization

---

## Lambda Syntax

### Basic Syntax

```java
// General form
(parameters) -> expression
(parameters) -> { statements; }

// No parameters
() -> System.out.println("Hello")

// Single parameter (parentheses optional)
x -> x * x
(x) -> x * x

// Multiple parameters
(x, y) -> x + y

// Single statement (no braces needed)
x -> x * 2

// Multiple statements (braces required)
x -> {
    int result = x * 2;
    System.out.println(result);
    return result;
}

// Explicit type declaration
(int x, int y) -> x + y

// Type inference (preferred)
(x, y) -> x + y
```

### Lambda Expression Examples

```java
import java.util.function.*;

public class LambdaSyntaxDemo {
    public static void main(String[] args) {
        // No parameters, no return value
        Runnable task = () -> System.out.println("Task executed");
        task.run();
        
        // One parameter, return value
        Function<String, Integer> length = s -> s.length();
        System.out.println(length.apply("Hello")); // 5
        
        // Two parameters, return value
        BiFunction<Integer, Integer, Integer> add = (a, b) -> a + b;
        System.out.println(add.apply(5, 3)); // 8
        
        // Multiple statements
        Function<Integer, Integer> factorial = n -> {
            int result = 1;
            for (int i = 1; i <= n; i++) {
                result *= i;
            }
            return result;
        };
        System.out.println(factorial.apply(5)); // 120
        
        // With explicit types
        BiPredicate<String, Integer> lengthCheck = 
            (String s, Integer len) -> s.length() == len;
        System.out.println(lengthCheck.test("Java", 4)); // true
    }
}
```

---

## Functional Interfaces

Lambda expressions work with **functional interfaces** - interfaces with exactly **one abstract method** (SAM - Single Abstract Method).

### Built-in Functional Interfaces

```java
import java.util.function.*;

public class FunctionalInterfaceDemo {
    public static void main(String[] args) {
        // Predicate<T> - T -> boolean
        Predicate<Integer> isEven = n -> n % 2 == 0;
        System.out.println(isEven.test(4)); // true
        
        // Function<T, R> - T -> R
        Function<String, Integer> length = s -> s.length();
        System.out.println(length.apply("Lambda")); // 6
        
        // Consumer<T> - T -> void
        Consumer<String> print = s -> System.out.println(s);
        print.accept("Hello"); // Hello
        
        // Supplier<T> - () -> T
        Supplier<Double> random = () -> Math.random();
        System.out.println(random.get());
        
        // UnaryOperator<T> - T -> T
        UnaryOperator<Integer> square = n -> n * n;
        System.out.println(square.apply(5)); // 25
        
        // BinaryOperator<T> - (T, T) -> T
        BinaryOperator<Integer> max = (a, b) -> a > b ? a : b;
        System.out.println(max.apply(10, 20)); // 20
        
        // BiFunction<T, U, R> - (T, U) -> R
        BiFunction<String, String, Integer> totalLength = 
            (s1, s2) -> s1.length() + s2.length();
        System.out.println(totalLength.apply("Hello", "World")); // 10
        
        // BiPredicate<T, U> - (T, U) -> boolean
        BiPredicate<String, String> startsWith = 
            (str, prefix) -> str.startsWith(prefix);
        System.out.println(startsWith.test("Lambda", "Lam")); // true
    }
}
```

### Custom Functional Interfaces

```java
@FunctionalInterface
interface Calculator {
    int calculate(int a, int b);
    
    // Can have default methods
    default void printResult(int a, int b) {
        System.out.println("Result: " + calculate(a, b));
    }
}

@FunctionalInterface
interface StringProcessor {
    String process(String input);
}

public class CustomFunctionalInterfaceDemo {
    public static void main(String[] args) {
        Calculator add = (a, b) -> a + b;
        Calculator multiply = (a, b) -> a * b;
        
        System.out.println(add.calculate(5, 3));      // 8
        System.out.println(multiply.calculate(5, 3)); // 15
        add.printResult(10, 20);                      // Result: 30
        
        StringProcessor toUpper = s -> s.toUpperCase();
        StringProcessor reverse = s -> new StringBuilder(s).reverse().toString();
        
        System.out.println(toUpper.process("hello"));   // HELLO
        System.out.println(reverse.process("hello"));   // olleh
    }
}
```

---

## Method References

**Method references** are shorthand notation for lambda expressions that only call a single method.

### Types of Method References

```java
import java.util.*;
import java.util.function.*;

public class MethodReferenceDemo {
    public static void main(String[] args) {
        List<String> names = Arrays.asList("Alice", "Bob", "Charlie");
        
        // 1. Static method reference - ClassName::staticMethod
        Function<String, Integer> parser1 = s -> Integer.parseInt(s);
        Function<String, Integer> parser2 = Integer::parseInt; // Method reference
        
        BiFunction<Integer, Integer, Integer> max1 = (a, b) -> Math.max(a, b);
        BiFunction<Integer, Integer, Integer> max2 = Math::max;
        
        // 2. Instance method reference on specific object - object::instanceMethod
        String prefix = "Hello, ";
        Function<String, String> greeter1 = s -> prefix.concat(s);
        Function<String, String> greeter2 = prefix::concat;
        
        // 3. Instance method reference on arbitrary object - ClassName::instanceMethod
        Function<String, String> toUpper1 = s -> s.toUpperCase();
        Function<String, String> toUpper2 = String::toUpperCase;
        
        // Usage with collections
        names.forEach(s -> System.out.println(s)); // Lambda
        names.forEach(System.out::println);         // Method reference
        
        // Comparator
        names.sort((s1, s2) -> s1.compareTo(s2)); // Lambda
        names.sort(String::compareTo);             // Method reference
        
        // 4. Constructor reference - ClassName::new
        Supplier<ArrayList<String>> list1 = () -> new ArrayList<>();
        Supplier<ArrayList<String>> list2 = ArrayList::new;
        
        Function<Integer, ArrayList<String>> listWithSize1 = 
            size -> new ArrayList<>(size);
        Function<Integer, ArrayList<String>> listWithSize2 = ArrayList::new;
        
        // Array constructor reference
        Function<Integer, String[]> arrayCreator1 = size -> new String[size];
        Function<Integer, String[]> arrayCreator2 = String[]::new;
    }
}
```

### When to Use Method References

```java
// Use method reference when lambda just calls one method
List<String> list = Arrays.asList("a", "b", "c");

// Good - method reference
list.forEach(System.out::println);

// Less concise - lambda
list.forEach(s -> System.out.println(s));

// Use lambda when additional logic is needed
list.forEach(s -> System.out.println("Item: " + s));

// Chaining operations
Function<String, String> trimAndUpper = 
    String::trim.andThen(String::toUpperCase);
```

---

## Variable Capture and Scope

Lambdas can access variables from their enclosing scope, but with restrictions.

### Effectively Final Variables

```java
public class VariableCaptureDemo {
    public static void main(String[] args) {
        int x = 10; // Effectively final (not modified)
        
        // Lambda can access x
        Runnable r = () -> System.out.println("x = " + x);
        r.run(); // x = 10
        
        // x = 20; // ERROR: would make x not effectively final
        
        // Local variables must be effectively final
        int y = 5;
        Consumer<Integer> consumer = n -> {
            System.out.println(n + y); // OK - y is effectively final
            // y++; // ERROR: can't modify captured variable
        };
        consumer.accept(10);
    }
}
```

### Instance Variables and Static Variables

```java
public class ScopeDemo {
    private int instanceVar = 100;
    private static int staticVar = 200;
    
    public void demonstrateScope() {
        int localVar = 300; // Effectively final
        
        Runnable r = () -> {
            // Can access and modify instance variables
            System.out.println("Instance: " + instanceVar);
            instanceVar++;
            
            // Can access and modify static variables
            System.out.println("Static: " + staticVar);
            staticVar++;
            
            // Can only read local variables (must be effectively final)
            System.out.println("Local: " + localVar);
            // localVar++; // ERROR: can't modify
        };
        
        r.run();
        System.out.println("After lambda: " + instanceVar); // 101
    }
    
    public static void main(String[] args) {
        new ScopeDemo().demonstrateScope();
    }
}
```

### The 'this' Keyword

```java
public class ThisKeywordDemo {
    private String message = "Instance method";
    
    public void demonstrateThis() {
        // In lambda, 'this' refers to enclosing class instance
        Runnable r = () -> {
            System.out.println(this.message); // Refers to ThisKeywordDemo.this
            System.out.println(this.getClass().getName());
        };
        r.run();
        
        // In anonymous class, 'this' refers to the anonymous class instance
        Runnable r2 = new Runnable() {
            @Override
            public void run() {
                // System.out.println(this.message); // ERROR: no message field
                System.out.println(this.getClass().getName()); // Different class
            }
        };
        r2.run();
    }
    
    public static void main(String[] args) {
        new ThisKeywordDemo().demonstrateThis();
    }
}
```

---

## Common Use Cases

### Collections Processing

```java
import java.util.*;

public class CollectionLambdaDemo {
    public static void main(String[] args) {
        List<String> names = new ArrayList<>(
            Arrays.asList("Alice", "Bob", "Charlie", "David", "Eve")
        );
        
        // forEach
        names.forEach(name -> System.out.println(name));
        names.forEach(System.out::println); // Method reference
        
        // removeIf
        names.removeIf(name -> name.length() < 4);
        System.out.println(names); // [Alice, Charlie, David]
        
        // replaceAll
        names.replaceAll(name -> name.toUpperCase());
        System.out.println(names); // [ALICE, CHARLIE, DAVID]
        
        // sort
        names.sort((s1, s2) -> s1.compareTo(s2));
        names.sort(String::compareTo);
        names.sort(Comparator.naturalOrder());
        names.sort(Comparator.reverseOrder());
    }
}
```

### Map Operations

```java
import java.util.*;

public class MapLambdaDemo {
    public static void main(String[] args) {
        Map<String, Integer> scores = new HashMap<>();
        scores.put("Alice", 90);
        scores.put("Bob", 85);
        scores.put("Charlie", 95);
        
        // forEach
        scores.forEach((name, score) -> 
            System.out.println(name + ": " + score)
        );
        
        // replaceAll
        scores.replaceAll((name, score) -> score + 5);
        
        // compute
        scores.compute("Alice", (name, score) -> score + 10);
        
        // computeIfAbsent
        scores.computeIfAbsent("David", name -> 80);
        
        // merge
        scores.merge("Alice", 5, (oldVal, newVal) -> oldVal + newVal);
        
        System.out.println(scores);
    }
}
```

### Comparators

```java
import java.util.*;

class Person {
    String name;
    int age;
    
    Person(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    public String toString() {
        return name + "(" + age + ")";
    }
}

public class ComparatorLambdaDemo {
    public static void main(String[] args) {
        List<Person> people = Arrays.asList(
            new Person("Alice", 30),
            new Person("Bob", 25),
            new Person("Charlie", 30),
            new Person("David", 28)
        );
        
        // Sort by age
        people.sort((p1, p2) -> p1.age - p2.age);
        people.sort(Comparator.comparingInt(p -> p.age));
        
        // Sort by name
        people.sort((p1, p2) -> p1.name.compareTo(p2.name));
        people.sort(Comparator.comparing(p -> p.name));
        
        // Sort by age, then name
        people.sort(Comparator.comparingInt((Person p) -> p.age)
                              .thenComparing(p -> p.name));
        
        // Reverse order
        people.sort(Comparator.comparingInt((Person p) -> p.age).reversed());
        
        System.out.println(people);
    }
}
```

### Thread Creation

```java
public class ThreadLambdaDemo {
    public static void main(String[] args) {
        // Traditional way
        Thread t1 = new Thread(new Runnable() {
            @Override
            public void run() {
                System.out.println("Thread 1");
            }
        });
        
        // Lambda way
        Thread t2 = new Thread(() -> System.out.println("Thread 2"));
        
        // With multiple statements
        Thread t3 = new Thread(() -> {
            System.out.println("Starting thread 3");
            try {
                Thread.sleep(1000);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            System.out.println("Thread 3 completed");
        });
        
        t1.start();
        t2.start();
        t3.start();
    }
}
```

---

## Best Practices

### 1. Keep Lambdas Short and Simple

```java
// Good - simple lambda
list.forEach(item -> System.out.println(item));

// Bad - too complex
list.forEach(item -> {
    if (item != null && !item.isEmpty()) {
        String processed = item.trim().toUpperCase();
        if (processed.length() > 5) {
            System.out.println("Long: " + processed);
        } else {
            System.out.println("Short: " + processed);
        }
    }
});

// Better - extract to method
list.forEach(this::processAndPrint);

private void processAndPrint(String item) {
    if (item != null && !item.isEmpty()) {
        String processed = item.trim().toUpperCase();
        System.out.println((processed.length() > 5 ? "Long: " : "Short: ") + processed);
    }
}
```

### 2. Prefer Method References

```java
// Less concise
list.forEach(s -> System.out.println(s));
list.sort((s1, s2) -> s1.compareTo(s2));

// Better - method references
list.forEach(System.out::println);
list.sort(String::compareTo);
```

### 3. Use Standard Functional Interfaces

```java
// Don't create custom interfaces when standard ones exist
@FunctionalInterface
interface StringTransformer {
    String transform(String s);
}

// Better - use Function<String, String>
Function<String, String> transformer = String::toUpperCase;
```

### 4. Be Careful with Side Effects

```java
// Bad - modifying external state
int[] sum = {0};
list.forEach(n -> sum[0] += n); // Fragile and not thread-safe

// Better - use reduce
int total = list.stream().reduce(0, Integer::sum);
```

### 5. Type Inference vs Explicit Types

```java
// Prefer type inference
BiFunction<String, String, Integer> totalLength = (s1, s2) -> s1.length() + s2.length();

// Only use explicit types when needed for clarity
BiFunction<String, String, Integer> totalLength2 = 
    (String s1, String s2) -> s1.length() + s2.length();
```

---

## Summary

### Key Points

- **Lambda expressions** provide concise syntax for anonymous functions
- Work with **functional interfaces** (single abstract method)
- Syntax: `(parameters) -> expression` or `(parameters) -> { statements }`
- **Method references** are shorthand for simple lambdas
- Can capture **effectively final** local variables
- Common uses: collections, comparators, threads, Stream API

### Lambda vs Anonymous Class

| Feature | Lambda | Anonymous Class |
|---------|--------|-----------------|
| Syntax | Concise | Verbose |
| 'this' keyword | Enclosing class | Anonymous class |
| Compilation | invokedynamic | Separate class file |
| Scope | Lexical scoping | Own scope |
| Can implement | Single abstract method | Multiple methods, fields |

### Important for Exam

```java
// Lambda can only be used with functional interfaces
Runnable r = () -> System.out.println("OK");

// Local variables must be effectively final
int x = 10;
Runnable r2 = () -> System.out.println(x); // OK
// x = 20; // Would cause compilation error in lambda

// Method reference types
Integer::parseInt           // Static method
"Hello"::concat            // Instance method on specific object
String::toUpperCase        // Instance method on arbitrary object
ArrayList::new             // Constructor
```

---

**Next:** [Practice Questions - Lambda Expressions](25-practice-questions.md)
