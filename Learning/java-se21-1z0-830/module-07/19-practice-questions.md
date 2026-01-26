# Module 7: Functional Interfaces - Practice Questions

## Practice Questions (20)

### Question 1
Which is a valid functional interface?
A)
```java
@FunctionalInterface
interface A {
    void method1();
    void method2();
}
```
B)
```java
@FunctionalInterface
interface B {
    void method();
    default void defaultMethod() { }
}
```
C)
```java
@FunctionalInterface
interface C {
    default void method() { }
}
```
D)
```java
interface D {
    void method1();
    void method2();
}
```

**Answer: B)**

**Explanation**: A functional interface must have exactly ONE abstract method. It can have any number of default or static methods. Option B has one abstract method (`method()`) and one default method, making it a valid functional interface. Option A has two abstract methods, Option C has zero abstract methods, and Option D has two abstract methods (invalid for functional interface).

---

### Question 2
What is the output?
```java
import java.util.function.Predicate;

public class Test {
    public static void main(String[] args) {
        Predicate<String> isEmpty = String::isEmpty;
        System.out.println(isEmpty.test("Hello"));
    }
}
```
A) true  
B) false  
C) Compilation error  
D) Hello

**Answer: B) false**

**Explanation**: `Predicate<T>` has a `test()` method that returns boolean. `String::isEmpty` is a method reference that checks if a string is empty. "Hello" is not empty, so `isEmpty.test("Hello")` returns false.

---

### Question 3
Which functional interface should be used for this lambda?
```java
? operation = (a, b) -> a + b;
```
A) `Function<Integer, Integer>`  
B) `UnaryOperator<Integer>`  
C) `BinaryOperator<Integer>`  
D) `BiFunction<Integer, Integer, Integer>`

**Answer: C) BinaryOperator<Integer>** (or D)

**Explanation**: The lambda takes two parameters and returns a result. `BinaryOperator<Integer>` is the best fit because it represents an operation on two operands of the same type producing a result of the same type. `BiFunction<Integer, Integer, Integer>` would also work but `BinaryOperator` is more specific and preferred.

---

### Question 4
What is the result?
```java
import java.util.function.Consumer;

public class Test {
    public static void main(String[] args) {
        Consumer<String> print = s -> System.out.print(s + " ");
        Consumer<String> upper = s -> System.out.print(s.toUpperCase() + " ");
        
        Consumer<String> both = print.andThen(upper);
        both.accept("java");
    }
}
```
A) java JAVA  
B) JAVA java  
C) java  
D) Compilation error

**Answer: A) java JAVA**

**Explanation**: The `andThen()` method chains consumers. First `print` is executed (prints "java "), then `upper` is executed (prints "JAVA "). The output is "java JAVA ".

---

### Question 5
Which statement about @FunctionalInterface is TRUE?
A) It's required for all functional interfaces  
B) It ensures the interface has exactly one abstract method  
C) It prevents default methods in the interface  
D) It makes methods automatically private

**Answer: B) It ensures the interface has exactly one abstract method**

**Explanation**: The `@FunctionalInterface` annotation is optional but recommended. It causes a compilation error if the interface doesn't meet the functional interface criteria (exactly one abstract method). It doesn't prevent default/static methods and is not required (though recommended).

---

### Question 6
What is the output?
```java
import java.util.function.Supplier;

public class Test {
    public static void main(String[] args) {
        Supplier<Double> random = Math::random;
        System.out.println(random.get() >= 0);
    }
}
```
A) true  
B) false  
C) Random number  
D) Compilation error

**Answer: A) true**

**Explanation**: `Supplier<T>` provides a value with no input. `Math::random` returns a double between 0.0 (inclusive) and 1.0 (exclusive), which is always >= 0. Therefore, the comparison always returns true.

---

### Question 7
Which is the correct functional interface for transforming a String to its length?
```java
? lengthFunction = String::length;
```
A) `Predicate<String>`  
B) `Consumer<String>`  
C) `Function<String, Integer>`  
D) `Supplier<Integer>`

**Answer: C) `Function<String, Integer>`**

**Explanation**: `Function<T, R>` takes an input of type T and produces an output of type R. `String::length` takes a String and returns an Integer (length), so `Function<String, Integer>` is correct. Predicate returns boolean, Consumer returns void, and Supplier takes no input.

---

### Question 8
What is the result?
```java
import java.util.function.UnaryOperator;

public class Test {
    public static void main(String[] args) {
        UnaryOperator<Integer> square = n -> n * n;
        UnaryOperator<Integer> increment = n -> n + 1;
        
        UnaryOperator<Integer> combined = square.andThen(increment);
        System.out.println(combined.apply(5));
    }
}
```
A) 25  
B) 26  
C) 36  
D) 30

**Answer: B) 26**

**Explanation**: `andThen()` chains operations. First `square` is applied (5 * 5 = 25), then `increment` is applied to the result (25 + 1 = 26). The final output is 26.

---

### Question 9
Which primitive functional interface should be used to avoid boxing?
```java
? isEven = n -> n % 2 == 0;
```
A) `Predicate<Integer>`  
B) `IntPredicate`  
C) `Function<Integer, Boolean>`  
D) `IntFunction<Boolean>`

**Answer: B) `IntPredicate`**

**Explanation**: `IntPredicate` is a primitive specialization that tests an int value and returns boolean, avoiding the boxing overhead of `Predicate<Integer>`. Using primitive specializations is more efficient for primitive types.

---

### Question 10
What is the output?
```java
import java.util.function.BiFunction;

public class Test {
    public static void main(String[] args) {
        BiFunction<String, String, Integer> totalLength = 
            (s1, s2) -> s1.length() + s2.length();
        
        System.out.println(totalLength.apply("Java", "SE"));
    }
}
```
A) 4  
B) 6  
C) JavaSE  
D) Compilation error

**Answer: B) 6**

**Explanation**: `BiFunction<T, U, R>` takes two inputs (T and U) and produces one output (R). This lambda takes two strings, gets their lengths (4 and 2), and returns the sum: 4 + 2 = 6.

---

### Question 11
Which method reference is INVALID?
A) `String::length`  
B) `System.out::println`  
C) `Integer::parseInt`  
D) `String::new()`

**Answer: D) `String::new()`**

**Explanation**: Constructor references don't use parentheses. The correct syntax is `String::new`, not `String::new()`. All other options are valid method references (instance method, instance method of specific object, and static method).

---

### Question 12
What is the result?
```java
import java.util.function.Function;

public class Test {
    public static void main(String[] args) {
        Function<String, Integer> length = String::length;
        Function<Integer, Integer> square = n -> n * n;
        
        Function<String, Integer> combined = length.andThen(square);
        System.out.println(combined.apply("Java"));
    }
}
```
A) 4  
B) 16  
C) Compilation error  
D) JavaJava

**Answer: B) 16**

**Explanation**: `andThen()` chains functions. First `length` is applied to "Java" (returns 4), then `square` is applied to 4 (returns 16). The result is 4^2 = 16.

---

### Question 13
Which functional interface has a method that returns void?
A) `Predicate<T>`  
B) `Function<T, R>`  
C) `Consumer<T>`  
D) `Supplier<T>`

**Answer: C) `Consumer<T>`**

**Explanation**: `Consumer<T>` has an `accept(T t)` method that returns void. It's used for operations that consume a value but don't return anything. Predicate returns boolean, Function returns R, and Supplier returns T.

---

### Question 14
What happens when you compile this code?
```java
@FunctionalInterface
interface MyInterface {
    void method1();
    default void method2() { }
    static void method3() { }
    void method4();  // Line X
}
```
A) Compiles successfully  
B) Compilation error at Line X  
C) @FunctionalInterface must be removed  
D) Both B and C

**Answer: D) Both B and C**

**Explanation**: The interface has TWO abstract methods (`method1()` and `method4()`), violating the functional interface requirement of exactly one abstract method. With `@FunctionalInterface`, this causes a compilation error. Removing the annotation would allow compilation but it wouldn't be a functional interface.

---

### Question 15
What is the output?
```java
import java.util.function.IntUnaryOperator;

public class Test {
    public static void main(String[] args) {
        IntUnaryOperator op = n -> n * 2;
        System.out.println(op.applyAsInt(5));
    }
}
```
A) 5  
B) 10  
C) 7  
D) Compilation error

**Answer: B) 10**

**Explanation**: `IntUnaryOperator` is a primitive specialization of `UnaryOperator` for int values. It has an `applyAsInt(int)` method. The lambda doubles the input: 5 * 2 = 10.

---

### Question 16
Which is TRUE about BiPredicate?
```java
BiPredicate<String, Integer> check = (s, len) -> s.length() == len;
```
A) Takes one parameter and returns boolean  
B) Takes two parameters and returns boolean  
C) Takes two parameters and returns Object  
D) Takes no parameters and returns boolean

**Answer: B) Takes two parameters and returns boolean**

**Explanation**: `BiPredicate<T, U>` is a functional interface that takes two parameters (types T and U) and returns a boolean. It's the two-parameter version of `Predicate<T>`.

---

### Question 17
What is the result?
```java
import java.util.function.Predicate;

public class Test {
    public static void main(String[] args) {
        Predicate<Integer> isEven = n -> n % 2 == 0;
        Predicate<Integer> isPositive = n -> n > 0;
        
        Predicate<Integer> combined = isEven.and(isPositive);
        System.out.println(combined.test(4));
    }
}
```
A) true  
B) false  
C) Compilation error  
D) 4

**Answer: A) true**

**Explanation**: The `and()` method combines predicates with logical AND. The value 4 is even (true) AND positive (true), so the combined predicate returns true.

---

### Question 18
Which functional interface should be used for a no-argument method that returns a value?
A) `Consumer<T>`  
B) `Supplier<T>`  
C) `Function<T, R>`  
D) `Predicate<T>`

**Answer: B) `Supplier<T>`**

**Explanation**: `Supplier<T>` has a `get()` method that takes no parameters and returns a value of type T. It's used for providing or supplying values. Consumer takes a parameter and returns void, Function takes a parameter and returns a value, Predicate takes a parameter and returns boolean.

---

### Question 19
What is the output?
```java
import java.util.function.IntSupplier;

public class Test {
    public static void main(String[] args) {
        IntSupplier supplier = () -> 42;
        System.out.println(supplier.getAsInt());
    }
}
```
A) 42  
B) 0  
C) Compilation error  
D) Random number

**Answer: A) 42**

**Explanation**: `IntSupplier` is a primitive specialization of Supplier for int values. It has a `getAsInt()` method that returns int. The lambda returns 42, which is printed.

---

### Question 20
Which is TRUE about functional interfaces and lambdas?
A) Lambdas can only be used with @FunctionalInterface annotated interfaces  
B) Lambdas provide a concise way to implement functional interfaces  
C) Functional interfaces must have exactly two abstract methods  
D) Lambdas cannot access variables from enclosing scope

**Answer: B) Lambdas provide a concise way to implement functional interfaces**

**Explanation**: Lambdas are a concise syntax for implementing functional interfaces. The @FunctionalInterface annotation is optional (A is false), functional interfaces have exactly ONE abstract method (C is false), and lambdas can access effectively final variables from enclosing scope (D is false).

---

## Answer Summary
1. B  2. B  3. C  4. A  5. B  
6. A  7. C  8. B  9. B  10. B  
11. D  12. B  13. C  14. D  15. B  
16. B  17. A  18. B  19. A  20. B
