# Module 10: Practice Questions - Lambda Expressions

## Questions (20)

---

### Question 1
```java
Runnable r = () -> System.out.println("Hello");
r.run();
```
What is the output?

**A)** Hello  
**B)** Compilation error  
**C)** Runtime exception  
**D)** Nothing is printed

**Answer: A)**

**Explanation:** The lambda expression `() -> System.out.println("Hello")` is a valid implementation of the `Runnable` functional interface. When `run()` is called, it prints "Hello".

---

### Question 2
```java
Function<String, Integer> f = s -> s.length();
System.out.println(f.apply("Lambda"));
```
What is printed?

**A)** 4  
**B)** 6  
**C)** Lambda  
**D)** Compilation error

**Answer: B)**

**Explanation:** The lambda takes a String and returns its length. "Lambda" has 6 characters, so 6 is printed.

---

### Question 3
```java
int x = 10;
Runnable r = () -> System.out.println(x);
x = 20;
r.run();
```
What happens?

**A)** Prints 10  
**B)** Prints 20  
**C)** Compilation error  
**D)** Runtime exception

**Answer: C)**

**Explanation:** Local variables captured by lambdas must be **effectively final**. Since `x` is modified after the lambda is defined, it's not effectively final, causing a compilation error.

---

### Question 4
Which is the correct lambda for `Predicate<String>`?

**A)** `s -> s.length()`  
**B)** `s -> s.isEmpty()`  
**C)** `s -> s.toUpperCase()`  
**D)** `s -> System.out.println(s)`

**Answer: B)**

**Explanation:** `Predicate<T>` has a method `boolean test(T t)`, so it must return a boolean. Only option B returns a boolean.

---

### Question 5
```java
List<String> list = Arrays.asList("A", "B", "C");
list.forEach(s -> System.out.print(s + " "));
```
What is the output?

**A)** A B C  
**B)** ABC  
**C)** [A, B, C]  
**D)** Compilation error

**Answer: A)**

**Explanation:** The `forEach` method accepts a `Consumer<String>`. The lambda prints each element followed by a space.

---

### Question 6
What is the method reference equivalent of `s -> s.toUpperCase()`?

**A)** `String::toUpperCase`  
**B)** `String.toUpperCase`  
**C)** `toUpperCase::String`  
**D)** `s::toUpperCase`

**Answer: A)**

**Explanation:** `String::toUpperCase` is an instance method reference on an arbitrary object of type String.

---

### Question 7
```java
BinaryOperator<Integer> add = (a, b) -> a + b;
System.out.println(add.apply(5, 3));
```
What is printed?

**A)** 5  
**B)** 3  
**C)** 8  
**D)** Compilation error

**Answer: C)**

**Explanation:** `BinaryOperator<T>` takes two arguments of the same type and returns a result of that type. 5 + 3 = 8.

---

### Question 8
```java
Supplier<Integer> s = () -> 42;
System.out.println(s.get());
```
What is the output?

**A)** 0  
**B)** 42  
**C)** null  
**D)** Compilation error

**Answer: B)**

**Explanation:** `Supplier<T>` has a `get()` method that returns a value. The lambda returns 42.

---

### Question 9
Which functional interface should be used for a lambda that takes two integers and returns an integer?

**A)** `Function<Integer, Integer>`  
**B)** `UnaryOperator<Integer>`  
**C)** `BinaryOperator<Integer>`  
**D)** `Predicate<Integer>`

**Answer: C)**

**Explanation:** `BinaryOperator<T>` takes two arguments of type T and returns a result of type T, which matches the requirement.

---

### Question 10
```java
Consumer<String> c1 = s -> System.out.print(s);
Consumer<String> c2 = s -> System.out.print("!");
Consumer<String> both = c1.andThen(c2);
both.accept("Hello");
```
What is printed?

**A)** Hello  
**B)** !  
**C)** Hello!  
**D)** !Hello

**Answer: C)**

**Explanation:** `andThen()` chains consumers. First `c1` prints "Hello", then `c2` prints "!".

---

### Question 11
```java
List<String> list = Arrays.asList("a", "b", "c");
list.forEach(System.out::println);
```
What type of method reference is `System.out::println`?

**A)** Static method reference  
**B)** Instance method reference on specific object  
**C)** Instance method reference on arbitrary object  
**D)** Constructor reference

**Answer: B)**

**Explanation:** `System.out` is a specific object, and `println` is called on it, making this an instance method reference on a specific object.

---

### Question 12
```java
Function<Integer, Integer> f = x -> x * 2;
Function<Integer, Integer> g = x -> x + 1;
Function<Integer, Integer> h = f.andThen(g);
System.out.println(h.apply(5));
```
What is the output?

**A)** 10  
**B)** 11  
**C)** 12  
**D)** 6

**Answer: B)**

**Explanation:** `andThen()` applies f first (5 * 2 = 10), then applies g (10 + 1 = 11).

---

### Question 13
Which of the following is NOT a valid lambda expression?

**A)** `() -> {}`  
**B)** `x -> x + 1`  
**C)** `(int x) -> x * 2`  
**D)** `x, y -> x + y`

**Answer: D)**

**Explanation:** Multiple parameters must be enclosed in parentheses: `(x, y) -> x + y`.

---

### Question 14
```java
Predicate<String> p = s -> s.length() > 5;
System.out.println(p.test("Lambda"));
```
What is printed?

**A)** true  
**B)** false  
**C)** 6  
**D)** Compilation error

**Answer: A)**

**Explanation:** "Lambda" has length 6, which is greater than 5, so the predicate returns true.

---

### Question 15
What is the constructor reference equivalent of `() -> new ArrayList<>()`?

**A)** `ArrayList::new`  
**B)** `new::ArrayList`  
**C)** `ArrayList.new`  
**D)** `new ArrayList`

**Answer: A)**

**Explanation:** `ArrayList::new` is the constructor reference syntax.

---

### Question 16
```java
BiFunction<Integer, Integer, Integer> max = (a, b) -> a > b ? a : b;
System.out.println(max.apply(10, 20));
```
What is the output?

**A)** 10  
**B)** 20  
**C)** 30  
**D)** Compilation error

**Answer: B)**

**Explanation:** The lambda returns the maximum of two integers. 20 is greater than 10.

---

### Question 17
```java
private int value = 100;

public void test() {
    Runnable r = () -> {
        System.out.println(this.value);
    };
    r.run();
}
```
What does `this` refer to in the lambda?

**A)** The Runnable instance  
**B)** The enclosing class instance  
**C)** null  
**D)** Compilation error

**Answer: B)**

**Explanation:** In lambdas, `this` refers to the enclosing class instance, not the lambda itself.

---

### Question 18
```java
List<String> list = Arrays.asList("1", "2", "3");
list.replaceAll(s -> s + "0");
System.out.println(list);
```
What is printed?

**A)** [1, 2, 3]  
**B)** [10, 20, 30]  
**C)** [1, 0, 2, 0, 3, 0]  
**D)** Compilation error

**Answer: B)**

**Explanation:** `replaceAll()` takes a `UnaryOperator` and replaces each element. Each string is concatenated with "0".

---

### Question 19
Which statement is true about lambda expressions?

**A)** They can have multiple abstract methods  
**B)** They require explicit return type declaration  
**C)** They can access effectively final local variables  
**D)** They create a new class file

**Answer: C)**

**Explanation:** Lambdas can access local variables that are effectively final. They work with functional interfaces (single abstract method), use type inference, and use invokedynamic (not separate class files).

---

### Question 20
```java
Comparator<String> c = (s1, s2) -> s1.length() - s2.length();
List<String> list = Arrays.asList("zzz", "a", "bb");
list.sort(c);
System.out.println(list);
```
What is the output?

**A)** [a, bb, zzz]  
**B)** [zzz, bb, a]  
**C)** [a, zzz, bb]  
**D)** [bb, a, zzz]

**Answer: A)**

**Explanation:** The comparator sorts by length: "a" (1), "bb" (2), "zzz" (3).

---

## Score Interpretation

- **18-20 correct**: Excellent! You've mastered lambda expressions.
- **15-17 correct**: Good understanding. Review areas you missed.
- **12-14 correct**: Fair. Study the theory and practice more.
- **Below 12**: Need more practice. Review all concepts thoroughly.

---

**Previous:** [Theory - Lambda Expressions](25-lambda-expressions.md)  
**Next:** [Theory - Stream API Basics](26-stream-api-basics.md)
