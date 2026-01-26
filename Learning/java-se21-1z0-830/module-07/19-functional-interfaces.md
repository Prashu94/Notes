# Functional Interfaces

## Introduction

A functional interface is an interface with exactly one abstract method (SAM - Single Abstract Method). Functional interfaces enable the use of lambda expressions and method references, which are key features of functional programming in Java. Introduced prominently in Java 8, they form the foundation for working with the Stream API and modern Java programming patterns.

## What is a Functional Interface?

A functional interface must have:
- **Exactly one abstract method**
- Can have any number of default methods
- Can have any number of static methods
- Can have any number of private methods (Java 9+)

### @FunctionalInterface Annotation

While optional, this annotation ensures the interface meets the functional interface contract:

```java
@FunctionalInterface
interface Calculator {
    int calculate(int a, int b);  // Single abstract method
}

// Usage with lambda
public class FunctionalInterfaceDemo {
    public static void main(String[] args) {
        Calculator add = (a, b) -> a + b;
        Calculator multiply = (a, b) -> a * b;
        
        System.out.println(add.calculate(5, 3));       // 8
        System.out.println(multiply.calculate(5, 3));  // 15
    }
}
```

### Functional Interface with Default Methods

```java
@FunctionalInterface
interface Processor {
    // Single abstract method
    String process(String input);
    
    // Default methods don't count toward the abstract method count
    default String processWithPrefix(String input) {
        return "Processed: " + process(input);
    }
    
    default String processMultiple(String... inputs) {
        return Arrays.stream(inputs)
            .map(this::process)
            .collect(Collectors.joining(", "));
    }
}

public class DefaultMethodDemo {
    public static void main(String[] args) {
        Processor toUpperCase = String::toUpperCase;
        
        System.out.println(toUpperCase.process("hello"));  // HELLO
        System.out.println(toUpperCase.processWithPrefix("hello"));  // Processed: HELLO
    }
}
```

## Built-in Functional Interfaces (java.util.function)

Java provides many pre-defined functional interfaces in the `java.util.function` package:

### Predicate<T>

Tests a condition and returns boolean:

```java
import java.util.function.Predicate;

public class PredicateDemo {
    public static void main(String[] args) {
        Predicate<String> isEmpty = String::isEmpty;
        Predicate<String> isLong = s -> s.length() > 10;
        Predicate<Integer> isEven = n -> n % 2 == 0;
        
        System.out.println(isEmpty.test(""));       // true
        System.out.println(isEmpty.test("hello"));  // false
        System.out.println(isEven.test(4));         // true
        
        // Combining predicates
        Predicate<String> isNotEmpty = isEmpty.negate();
        Predicate<String> isShortAndNotEmpty = isNotEmpty.and(s -> s.length() < 5);
        
        System.out.println(isShortAndNotEmpty.test("hi"));  // true
    }
}
```

### Function<T, R>

Transforms input of type T to output of type R:

```java
import java.util.function.Function;

public class FunctionDemo {
    public static void main(String[] args) {
        Function<String, Integer> stringLength = String::length;
        Function<Integer, Integer> square = n -> n * n;
        Function<String, String> toUpper = String::toUpperCase;
        
        System.out.println(stringLength.apply("Hello"));  // 5
        System.out.println(square.apply(4));              // 16
        
        // Chaining functions
        Function<String, Integer> lengthSquared = stringLength.andThen(square);
        System.out.println(lengthSquared.apply("Java"));  // 16 (4^2)
        
        // Composing functions
        Function<Integer, String> intToString = Object::toString;
        Function<String, Integer> parseAndSquare = intToString.compose(square);
    }
}
```

### Consumer<T>

Accepts input and performs an action (returns void):

```java
import java.util.function.Consumer;

public class ConsumerDemo {
    public static void main(String[] args) {
        Consumer<String> print = System.out::println;
        Consumer<String> printUpper = s -> System.out.println(s.toUpperCase());
        
        print.accept("Hello");       // Hello
        printUpper.accept("Hello");  // HELLO
        
        // Chaining consumers
        Consumer<String> printBoth = print.andThen(printUpper);
        printBoth.accept("Java");
        // Output:
        // Java
        // JAVA
        
        // Using with collections
        List<String> names = List.of("Alice", "Bob", "Charlie");
        names.forEach(print);
    }
}
```

### Supplier<T>

Provides a value with no input:

```java
import java.util.function.Supplier;

public class SupplierDemo {
    public static void main(String[] args) {
        Supplier<Double> randomValue = Math::random;
        Supplier<String> greeting = () -> "Hello, World!";
        Supplier<LocalDateTime> currentTime = LocalDateTime::now;
        
        System.out.println(randomValue.get());
        System.out.println(greeting.get());
        System.out.println(currentTime.get());
        
        // Lazy evaluation
        Supplier<List<String>> expensiveOperation = () -> {
            System.out.println("Computing...");
            return List.of("Result");
        };
        
        // Not executed until get() is called
        System.out.println("Before get");
        List<String> result = expensiveOperation.get();  // Now it executes
        System.out.println("After get");
    }
}
```

### UnaryOperator<T>

Special case of Function where input and output types are the same:

```java
import java.util.function.UnaryOperator;

public class UnaryOperatorDemo {
    public static void main(String[] args) {
        UnaryOperator<String> toUpper = String::toUpperCase;
        UnaryOperator<Integer> square = n -> n * n;
        UnaryOperator<Integer> increment = n -> n + 1;
        
        System.out.println(toUpper.apply("hello"));  // HELLO
        System.out.println(square.apply(5));         // 25
        
        // Chaining
        UnaryOperator<Integer> squareThenIncrement = square.andThen(increment);
        System.out.println(squareThenIncrement.apply(5));  // 26 (5^2 + 1)
    }
}
```

### BinaryOperator<T>

Special case of BiFunction where both inputs and output are the same type:

```java
import java.util.function.BinaryOperator;

public class BinaryOperatorDemo {
    public static void main(String[] args) {
        BinaryOperator<Integer> add = (a, b) -> a + b;
        BinaryOperator<Integer> max = Integer::max;
        BinaryOperator<String> concat = (s1, s2) -> s1 + s2;
        
        System.out.println(add.apply(5, 3));        // 8
        System.out.println(max.apply(5, 3));        // 5
        System.out.println(concat.apply("Hello", " World"));  // Hello World
        
        // Using with Stream reduce
        List<Integer> numbers = List.of(1, 2, 3, 4, 5);
        int sum = numbers.stream().reduce(0, add);
        System.out.println(sum);  // 15
    }
}
```

## Primitive Functional Interfaces

To avoid boxing/unboxing overhead, Java provides primitive-specialized functional interfaces:

### IntPredicate, LongPredicate, DoublePredicate

```java
import java.util.function.*;

public class PrimitivePredicateDemo {
    public static void main(String[] args) {
        IntPredicate isEven = n -> n % 2 == 0;
        LongPredicate isPositive = n -> n > 0;
        DoublePredicate isZero = d -> d == 0.0;
        
        System.out.println(isEven.test(4));        // true
        System.out.println(isPositive.test(-5L));  // false
        System.out.println(isZero.test(0.0));      // true
    }
}
```

### IntFunction, IntToDoubleFunction, etc.

```java
import java.util.function.*;

public class PrimitiveFunctionDemo {
    public static void main(String[] args) {
        IntFunction<String> intToString = i -> "Number: " + i;
        IntToDoubleFunction sqrt = Math::sqrt;
        ToIntFunction<String> stringLength = String::length;
        
        System.out.println(intToString.apply(42));    // Number: 42
        System.out.println(sqrt.applyAsDouble(16));   // 4.0
        System.out.println(stringLength.applyAsInt("Hello"));  // 5
    }
}
```

### IntConsumer, IntSupplier, IntUnaryOperator, IntBinaryOperator

```java
import java.util.function.*;

public class PrimitiveOtherDemo {
    public static void main(String[] args) {
        IntConsumer printInt = System.out::println;
        IntSupplier random = () -> (int)(Math.random() * 100);
        IntUnaryOperator square = n -> n * n;
        IntBinaryOperator add = (a, b) -> a + b;
        
        printInt.accept(42);
        System.out.println(random.getAsInt());
        System.out.println(square.applyAsInt(5));   // 25
        System.out.println(add.applyAsInt(3, 7));   // 10
    }
}
```

## BiFunction and BiPredicate

For operations with two inputs:

```java
import java.util.function.*;

public class BiFunctionDemo {
    public static void main(String[] args) {
        // BiFunction<T, U, R> - two inputs, one output
        BiFunction<String, String, Integer> totalLength = 
            (s1, s2) -> s1.length() + s2.length();
        
        BiFunction<Integer, Integer, String> sumToString = 
            (a, b) -> "Sum: " + (a + b);
        
        System.out.println(totalLength.apply("Hello", "World"));  // 10
        System.out.println(sumToString.apply(5, 3));              // Sum: 8
        
        // BiPredicate<T, U> - two inputs, boolean output
        BiPredicate<String, Integer> lengthEquals = 
            (s, len) -> s.length() == len;
        
        BiPredicate<Integer, Integer> isGreater = 
            (a, b) -> a > b;
        
        System.out.println(lengthEquals.test("Hello", 5));  // true
        System.out.println(isGreater.test(10, 5));          // true
    }
}
```

## Custom Functional Interfaces

You can create your own functional interfaces for specific needs:

```java
@FunctionalInterface
interface TriFunction<T, U, V, R> {
    R apply(T t, U u, V v);
}

@FunctionalInterface
interface Validator<T> {
    boolean validate(T value);
    
    default Validator<T> and(Validator<T> other) {
        return value -> this.validate(value) && other.validate(value);
    }
    
    default Validator<T> or(Validator<T> other) {
        return value -> this.validate(value) || other.validate(value);
    }
}

public class CustomFunctionalInterfaceDemo {
    public static void main(String[] args) {
        TriFunction<Integer, Integer, Integer, Integer> sum = 
            (a, b, c) -> a + b + c;
        
        System.out.println(sum.apply(1, 2, 3));  // 6
        
        Validator<String> notEmpty = s -> !s.isEmpty();
        Validator<String> lengthCheck = s -> s.length() >= 3;
        Validator<String> combined = notEmpty.and(lengthCheck);
        
        System.out.println(combined.validate("Hello"));  // true
        System.out.println(combined.validate("Hi"));     // false
    }
}
```

## Method References with Functional Interfaces

Method references provide a compact way to create functional interface instances:

### Reference to Static Method

```java
Function<String, Integer> parser1 = s -> Integer.parseInt(s);
Function<String, Integer> parser2 = Integer::parseInt;  // Method reference

BiFunction<Integer, Integer, Integer> max1 = (a, b) -> Math.max(a, b);
BiFunction<Integer, Integer, Integer> max2 = Math::max;  // Method reference
```

### Reference to Instance Method

```java
String str = "Hello";
Supplier<String> upper1 = () -> str.toUpperCase();
Supplier<String> upper2 = str::toUpperCase;  // Method reference

List<String> list = Arrays.asList("a", "b", "c");
Consumer<String> add1 = s -> list.add(s);
Consumer<String> add2 = list::add;  // Method reference
```

### Reference to Instance Method of Arbitrary Object

```java
Function<String, Integer> length1 = s -> s.length();
Function<String, Integer> length2 = String::length;  // Method reference

BiPredicate<String, String> equals1 = (s1, s2) -> s1.equals(s2);
BiPredicate<String, String> equals2 = String::equals;  // Method reference
```

### Reference to Constructor

```java
Supplier<List<String>> list1 = () -> new ArrayList<>();
Supplier<List<String>> list2 = ArrayList::new;  // Constructor reference

Function<String, Person> create1 = name -> new Person(name);
Function<String, Person> create2 = Person::new;  // Constructor reference
```

## Functional Interfaces in Stream API

Functional interfaces are heavily used in the Stream API:

```java
import java.util.stream.*;

public class StreamFunctionalInterfaceDemo {
    public static void main(String[] args) {
        List<String> names = List.of("Alice", "Bob", "Charlie", "David");
        
        // Predicate in filter
        List<String> shortNames = names.stream()
            .filter(name -> name.length() < 6)  // Predicate<String>
            .collect(Collectors.toList());
        
        // Function in map
        List<Integer> lengths = names.stream()
            .map(String::length)  // Function<String, Integer>
            .collect(Collectors.toList());
        
        // Consumer in forEach
        names.stream()
            .forEach(System.out::println);  // Consumer<String>
        
        // BinaryOperator in reduce
        int totalLength = names.stream()
            .map(String::length)
            .reduce(0, Integer::sum);  // BinaryOperator<Integer>
        
        System.out.println("Total length: " + totalLength);
    }
}
```

## Common Patterns

### Factory Pattern

```java
@FunctionalInterface
interface Factory<T> {
    T create();
}

public class FactoryPattern {
    public static void main(String[] args) {
        Factory<List<String>> listFactory = ArrayList::new;
        Factory<Set<Integer>> setFactory = HashSet::new;
        
        List<String> list = listFactory.create();
        Set<Integer> set = setFactory.create();
    }
}
```

### Strategy Pattern

```java
@FunctionalInterface
interface PaymentStrategy {
    void pay(double amount);
}

public class StrategyPattern {
    public static void processPayment(double amount, PaymentStrategy strategy) {
        strategy.pay(amount);
    }
    
    public static void main(String[] args) {
        processPayment(100.0, amt -> System.out.println("Cash: $" + amt));
        processPayment(200.0, amt -> System.out.println("Card: $" + amt));
        processPayment(300.0, amt -> System.out.println("PayPal: $" + amt));
    }
}
```

### Callback Pattern

```java
@FunctionalInterface
interface Callback {
    void onComplete(String result);
}

public class CallbackPattern {
    public static void fetchData(String url, Callback callback) {
        // Simulate async operation
        new Thread(() -> {
            try {
                Thread.sleep(1000);
                callback.onComplete("Data from " + url);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }).start();
    }
    
    public static void main(String[] args) throws InterruptedException {
        fetchData("https://api.example.com", 
            result -> System.out.println("Received: " + result));
        
        Thread.sleep(2000);  // Wait for callback
    }
}
```

## Best Practices

### 1. Use Standard Functional Interfaces When Possible

```java
// Bad - reinventing the wheel
@FunctionalInterface
interface StringProcessor {
    String process(String input);
}

// Good - use built-in Function
Function<String, String> processor = String::toUpperCase;
```

### 2. Use Primitive Specializations to Avoid Boxing

```java
// Less efficient - boxing overhead
Function<Integer, Integer> square = n -> n * n;

// More efficient - no boxing
IntUnaryOperator square = n -> n * n;
```

### 3. Keep Lambdas Short and Readable

```java
// Bad - too complex
Predicate<String> complex = s -> {
    if (s == null) return false;
    if (s.isEmpty()) return false;
    if (s.length() < 3) return false;
    return s.matches("[a-zA-Z]+");
};

// Good - extract to method
Predicate<String> isValidName = ValidationUtils::isValidName;
```

## Summary

- **Functional interfaces** have exactly one abstract method (SAM)
- **@FunctionalInterface** annotation ensures functional interface contract
- Java provides many built-in functional interfaces in **java.util.function**
- **Predicate<T>**: condition testing (T → boolean)
- **Function<T, R>**: transformation (T → R)
- **Consumer<T>**: action on input (T → void)
- **Supplier<T>**: provides value (() → T)
- **UnaryOperator<T>**: same-type transformation (T → T)
- **BinaryOperator<T>**: same-type binary operation ((T, T) → T)
- **Primitive specializations** avoid boxing overhead (IntPredicate, LongFunction, etc.)
- Functional interfaces enable **lambda expressions** and **method references**
- Heavily used in **Stream API** for data processing
- Support functional programming patterns: **strategy, factory, callback**
