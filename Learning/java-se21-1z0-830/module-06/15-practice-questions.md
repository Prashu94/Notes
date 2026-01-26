# Module 6: Pattern Matching and Sealed Classes - Practice Questions

## Practice Questions (20)

### Question 1
What is the output? (Java 16+)
```java
Object obj = "Hello";

if (obj instanceof String str) {
    System.out.print(str.length() + " ");
}
System.out.print(str.toUpperCase());
```
A) 5 HELLO  
B) Compilation error  
C) 5  
D) Runtime error

**Answer: B) Compilation error**

**Explanation**: The pattern variable `str` is only in scope within the if block where the instanceof check is true. Outside the if block, `str` is not defined, causing a compilation error on the line attempting `str.toUpperCase()`. Pattern variables have flow-scoped visibility.

---

### Question 2
Which statement about pattern matching for instanceof is TRUE?
```java
if (obj instanceof String str && str.length() > 5) {
    // Code here
}
```
A) This will not compile  
B) str is only in scope if both conditions are true  
C) str is not in scope for the length() check  
D) Pattern variables cannot be used with logical operators

**Answer: B) str is only in scope if both conditions are true**

**Explanation**: With the logical AND operator (&&), if the first condition (instanceof) is true, str is bound and can be used in the second condition. The pattern variable is in scope for the rest of the condition and the if block because the instanceof must be true for the entire expression to be true.

---

### Question 3
What happens with this code? (Java 16+)
```java
Object obj = Integer.valueOf(42);

if (obj instanceof String str || str.isEmpty()) {
    System.out.println("Process");
}
```
A) Prints "Process"  
B) No output  
C) Compilation error  
D) Runtime error

**Answer: C) Compilation error**

**Explanation**: When using logical OR (||), the pattern variable might not be initialized (if the instanceof is false, the right side might still be evaluated). Since `str` might not be assigned when evaluating `str.isEmpty()`, the compiler rejects this code. Pattern variables cannot be safely used with OR operators.

---

### Question 4
What is the output? (Java 21)
```java
public static String describe(Object obj) {
    return switch (obj) {
        case Integer i when i > 10 -> "Large integer";
        case Integer i -> "Small integer";
        case String s -> "String";
        default -> "Other";
    };
}

public static void main(String[] args) {
    System.out.println(describe(15));
}
```
A) Small integer  
B) Large integer  
C) Other  
D) Compilation error

**Answer: B) Large integer**

**Explanation**: Pattern matching for switch with guards allows conditional patterns. The value 15 matches the first case (`Integer i when i > 10`) because 15 is an Integer and 15 > 10 is true. Guards (when clauses) provide additional conditions for pattern matching.

---

### Question 5
Which code demonstrates correct sealed class syntax?
A)
```java
sealed class Shape permits Circle, Rectangle { }
final class Circle extends Shape { }
final class Rectangle extends Shape { }
```
B)
```java
sealed class Shape { }
class Circle extends Shape { }
class Rectangle extends Shape { }
```
C)
```java
sealed class Shape permits Circle, Rectangle { }
class Circle extends Shape { }
class Rectangle extends Shape { }
```
D)
```java
final sealed class Shape permits Circle, Rectangle { }
final class Circle extends Shape { }
```

**Answer: A)**

**Explanation**: Correct sealed class syntax requires: 1) Use `permits` to declare allowed subclasses, 2) Subclasses must be final, sealed, or non-sealed. Option B is wrong (no permits), Option C is wrong (subclasses must be final/sealed/non-sealed), Option D is wrong (cannot be both final and sealed).

---

### Question 6
What is true about this sealed interface? (Java 17+)
```java
sealed interface Animal permits Dog, Cat { }
final class Dog implements Animal { }
final class Cat implements Animal { }
class Bird implements Animal { }  // Line X
```
A) Line X compiles successfully  
B) Line X causes a compilation error  
C) Line X runs but throws an exception  
D) sealed interfaces cannot have implementations

**Answer: B) Line X causes a compilation error**

**Explanation**: Sealed interfaces restrict which classes can implement them. Only the classes listed in the `permits` clause (Dog and Cat) can implement Animal. Bird is not permitted, so Line X causes a compilation error. Sealed interfaces enforce a closed set of implementations.

---

### Question 7
What is the output? (Java 21)
```java
public static void process(String str) {
    switch (str) {
        case null -> System.out.print("A");
        case "HELLO" -> System.out.print("B");
        default -> System.out.print("C");
    }
}

public static void main(String[] args) {
    process(null);
    process("HELLO");
}
```
A) BC  
B) AB  
C) AC  
D) NullPointerException

**Answer: B) AB**

**Explanation**: Pattern matching switch expressions in Java 21 can handle null explicitly. The first call `process(null)` matches the `case null` and prints "A". The second call `process("HELLO")` matches the second case and prints "B", resulting in "AB".

---

### Question 8
Which subclass declaration is INVALID for a sealed class?
```java
sealed class Vehicle permits Car, Truck, Bike { }
```
A) `final class Car extends Vehicle { }`  
B) `sealed class Truck extends Vehicle permits PickupTruck { }`  
C) `non-sealed class Bike extends Vehicle { }`  
D) `class Car extends Vehicle { }`

**Answer: D) `class Car extends Vehicle { }`**

**Explanation**: Subclasses of a sealed class must be explicitly declared as `final`, `sealed`, or `non-sealed`. A regular class declaration (without any of these modifiers) is not allowed. Options A, B, and C all use the required modifiers.

---

### Question 9
What happens when you compile this code? (Java 21)
```java
sealed interface Expr permits Const, Add { }
record Const(int value) implements Expr { }
record Add(Expr left, Expr right) implements Expr { }

public static int eval(Expr expr) {
    return switch (expr) {
        case Const(int value) -> value;
        case Add(Expr left, Expr right) -> eval(left) + eval(right);
    };
}
```
A) Compilation error: missing default case  
B) Compilation error: invalid record pattern  
C) Compiles successfully  
D) Runtime error

**Answer: C) Compiles successfully**

**Explanation**: When using sealed types with pattern matching, the compiler can verify exhaustiveness. Since `Expr` is sealed and permits only `Const` and `Add`, and both are handled in the switch, no default case is needed. This is one of the major benefits of sealed classes—exhaustiveness checking.

---

### Question 10
What is the output? (Java 16+)
```java
Object obj = "Java";

if (!(obj instanceof String str)) {
    System.out.print("A");
} else {
    System.out.print("B" + str);
}
```
A) A  
B) BJava  
C) Compilation error  
D) Runtime error

**Answer: B) BJava**

**Explanation**: When instanceof is negated, the pattern variable is NOT in scope in the if block (where the condition is true), but IS in scope in the else block (where the instanceof would have been true). Since obj is a String, the negated condition is false, the else block executes, and "BJava" is printed.

---

### Question 11
Which statement about sealed classes is FALSE?
A) Sealed classes restrict which classes can extend them  
B) All subclasses of a sealed class must be in the same module or package  
C) Sealed classes cannot have constructors  
D) Permitted subclasses must be final, sealed, or non-sealed

**Answer: C) Sealed classes cannot have constructors**

**Explanation**: Sealed classes CAN have constructors, just like regular classes. All other statements are true: sealed classes do restrict inheritance (A), subclasses must be accessible from the sealed class (B), and permitted subclasses must use one of the three modifiers (D).

---

### Question 12
What is the result? (Java 21)
```java
public static String process(Number num) {
    return switch (num) {
        case Integer i when i > 100 -> "Big";
        case Integer i -> "Small";
        case Double d -> "Double";
        default -> "Other";
    };
}

public static void main(String[] args) {
    System.out.println(process(50));
}
```
A) Big  
B) Small  
C) Other  
D) Compilation error

**Answer: B) Small**

**Explanation**: The value 50 is an Integer, so it's tested against the Integer patterns. The first case requires i > 100, which is false for 50. The second case matches any Integer without a guard, so it matches, returning "Small". Guards allow adding conditions to patterns.

---

### Question 13
What happens with this sealed class hierarchy? (Java 17+)
```java
sealed class A permits B { }
non-sealed class B extends A { }
class C extends B { }
class D extends A { }  // Line X
```
A) Compiles successfully  
B) Compilation error at Line X  
C) Compilation error in class B  
D) Runtime error

**Answer: B) Compilation error at Line X**

**Explanation**: Class `B` is declared `non-sealed`, which means anyone can extend it (so `C extends B` is fine). However, class `D` tries to extend `A` directly, which is not allowed because `D` is not in the permits clause. Only `B` can extend `A`. Line X causes a compilation error.

---

### Question 14
What is the output? (Java 21)
```java
record Point(int x, int y) { }

public static void process(Object obj) {
    if (obj instanceof Point(int x, int y)) {
        System.out.println(x + y);
    }
}

public static void main(String[] args) {
    process(new Point(3, 4));
}
```
A) 34  
B) 7  
C) Point(3, 4)  
D) Compilation error

**Answer: B) 7**

**Explanation**: This demonstrates record patterns (Java 21). The pattern `Point(int x, int y)` deconstructs the Point record, extracting the x and y components. The values 3 and 4 are extracted and summed (3 + 4 = 7). Record patterns allow pattern matching to destructure records.

---

### Question 15
Which pattern matching switch is INCORRECT? (Java 21)
A)
```java
switch (obj) {
    case String s -> process(s);
    case Integer i -> process(i);
    default -> processOther();
}
```
B)
```java
switch (obj) {
    case null -> handleNull();
    case String s -> process(s);
    default -> processOther();
}
```
C)
```java
switch (obj) {
    case Object o -> process(o);
    case String s -> process(s);
    default -> processOther();
}
```
D)
```java
switch (obj) {
    case String s when s.length() > 5 -> processLong(s);
    case String s -> processShort(s);
    default -> processOther();
}
```

**Answer: C)**

**Explanation**: In pattern matching switch, more specific patterns must come before more general ones. `Object o` is the most general pattern and matches everything, making all subsequent cases unreachable. This violates the dominance rules and causes a compilation error. Pattern order matters!

---

### Question 16
What is true about this code? (Java 17+)
```java
// File: Shape.java
sealed class Shape { }
final class Circle extends Shape { }
final class Rectangle extends Shape { }
```
A) Must use permits clause  
B) permits clause is optional  
C) Compilation error  
D) Rectangle cannot be final

**Answer: B) permits clause is optional**

**Explanation**: When all permitted subclasses are declared in the same file as the sealed class, the `permits` clause is optional. The compiler can infer which classes are permitted from the file. This is a convenience feature for small sealed hierarchies.

---

### Question 17
What happens when you run this code? (Java 21)
```java
sealed interface Result permits Success, Error { }
record Success(String data) implements Result { }
record Error(String message) implements Result { }

public static void handle(Result result) {
    switch (result) {
        case Success(String data) -> System.out.println(data);
        case Error(String message) -> System.err.println(message);
    }
}

public static void main(String[] args) {
    handle(new Success("OK"));
}
```
A) Prints "OK" to standard output  
B) Prints "OK" to error output  
C) Compilation error: missing default  
D) Runtime error

**Answer: A) Prints "OK" to standard output**

**Explanation**: This demonstrates sealed types with exhaustive pattern matching. The sealed interface has only two permitted implementations, and both are handled in the switch. The compiler verifies exhaustiveness, so no default is needed. `Success("OK")` matches the first case, printing "OK" to stdout.

---

### Question 18
What is the output? (Java 16+)
```java
Object obj = 42;

String result = obj instanceof Integer i ? "Int: " + i : "Other";
System.out.println(result);
```
A) Int: 42  
B) Other  
C) Compilation error  
D) 42

**Answer: A) Int: 42**

**Explanation**: Pattern matching for instanceof works in ternary operators. The pattern variable `i` is in scope in the true branch of the ternary operator. Since obj is an Integer, it matches, `i` is bound to the value 42, and "Int: 42" is printed.

---

### Question 19
Which sealed class declaration is VALID? (Java 17+)
A) `sealed class A permits B, C { }` where B and C are in different modules  
B) `sealed class A permits B { }` where B is a concrete class (not final/sealed/non-sealed)  
C) `final sealed class A permits B { }`  
D) `sealed class A permits B { }` where `final class B extends A { }` in same package

**Answer: D) `sealed class A permits B { }` where `final class B extends A { }` in same package**

**Explanation**: Permitted classes must be accessible from the sealed class (same package or module), and must be final, sealed, or non-sealed. Option A is invalid (different modules requires explicit access), Option B is invalid (B must be final/sealed/non-sealed), Option C is invalid (cannot be both final and sealed).

---

### Question 20
What is the output? (Java 21)
```java
public static String check(Object obj) {
    return switch (obj) {
        case String s when s.isEmpty() -> "Empty";
        case String s when s.length() < 5 -> "Short";
        case String s -> "Long";
        case Integer i -> "Number";
        case null -> "Null";
        default -> "Other";
    };
}

public static void main(String[] args) {
    System.out.print(check("Hi"));
    System.out.print(check(""));
}
```
A) ShortEmpty  
B) LongEmpty  
C) EmptyShort  
D) Compilation error

**Answer: A) ShortEmpty**

**Explanation**: Guards (when clauses) are evaluated in order. For "Hi" (length 2), the first guard (isEmpty) is false, the second guard (length < 5) is true, so "Short" is printed. For "" (empty string), the first guard (isEmpty) is true, so "Empty" is printed. Result: "ShortEmpty".

---

## Answer Summary
1. B  2. B  3. C  4. B  5. A  
6. B  7. B  8. D  9. C  10. B  
11. C  12. B  13. B  14. B  15. C  
16. B  17. A  18. A  19. D  20. A
