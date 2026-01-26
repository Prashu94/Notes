# Module 7: Interfaces - Practice Questions

## Practice Questions (20)

### Question 1
Which statement about interfaces is TRUE?
```java
interface Animal {
    void makeSound();
    int MAX_AGE = 100;
}
```
A) MAX_AGE can be modified by implementing classes  
B) makeSound() is implicitly public and abstract  
C) Interfaces can be instantiated  
D) makeSound() must be declared public abstract explicitly

**Answer: B) makeSound() is implicitly public and abstract**

**Explanation**: Interface methods are implicitly public and abstract. You don't need to specify these keywords (though you can). MAX_AGE is public static final and cannot be modified (A is false). Interfaces cannot be instantiated (C is false). The keywords are implicit, not required (D is false).

---

### Question 2
What is the output?
```java
interface Vehicle {
    default void start() {
        System.out.print("Starting ");
    }
}

class Car implements Vehicle {
    public void start() {
        System.out.print("Car starting ");
    }
}

public class Test {
    public static void main(String[] args) {
        Vehicle v = new Car();
        v.start();
    }
}
```
A) Starting  
B) Car starting  
C) Starting Car starting  
D) Compilation error

**Answer: B) Car starting**

**Explanation**: Default methods in interfaces can be overridden by implementing classes. The `Car` class overrides the `start()` method, so when called through a `Vehicle` reference, the overridden method in `Car` is executed due to polymorphism.

---

### Question 3
Which interface declaration will NOT compile?
A)
```java
interface A {
    void method();
}
```
B)
```java
interface B {
    default void method() {
        System.out.println("Default");
    }
}
```
C)
```java
interface C {
    private void method() {
        System.out.println("Private");
    }
}
```
D)
```java
interface D {
    static void method() {
        System.out.println("Static");
    }
}
```

**Answer: C)**

**Explanation**: Interface methods must be public unless they're private helper methods for default methods (Java 9+). However, a standalone private method must be either a helper for default/static methods or have a body. Option C shows a private method without a body, which is invalid. Private methods in interfaces must have implementations.

---

### Question 4
What is the result?
```java
interface Calculator {
    static int add(int a, int b) {
        return a + b;
    }
}

class MyCalculator implements Calculator {
}

public class Test {
    public static void main(String[] args) {
        MyCalculator calc = new MyCalculator();
        System.out.println(calc.add(5, 3));
    }
}
```
A) 8  
B) 0  
C) Compilation error  
D) Runtime error

**Answer: C) Compilation error**

**Explanation**: Static methods in interfaces are NOT inherited by implementing classes. They belong to the interface itself and must be called using the interface name: `Calculator.add(5, 3)`. Trying to call them through an instance or implementing class causes a compilation error.

---

### Question 5
Which is a valid implementation?
```java
interface Flyable {
    void fly();
}

interface Swimmable {
    void swim();
}
```
A) `class Duck implements Flyable { public void fly() {} }`  
B) `class Duck implements Flyable, Swimmable { public void fly() {} }`  
C) `class Duck implements Flyable, Swimmable { public void fly() {} public void swim() {} }`  
D) `abstract class Duck implements Flyable, Swimmable { }`

**Answer: C)**

**Explanation**: When a class implements multiple interfaces, it must provide implementations for all abstract methods from all interfaces. Option A is valid but incomplete for this scenario. Option B missing `swim()` implementation. Option C correctly implements both methods. Option D would compile (abstract class can delay implementation) but doesn't fulfill "valid implementation" requirement.

---

### Question 6
What happens when you compile this code?
```java
interface Animal {
    int MAX_AGE = 100;
}

class Dog implements Animal {
    void setMaxAge() {
        MAX_AGE = 150;  // Line X
    }
}
```
A) Compiles successfully  
B) Compilation error at Line X  
C) Runtime error at Line X  
D) MAX_AGE is successfully updated

**Answer: B) Compilation error at Line X**

**Explanation**: Fields in interfaces are implicitly `public static final`, making them constants. You cannot modify a final variable after initialization. Attempting to assign a new value to `MAX_AGE` results in a compilation error.

---

### Question 7
What is the output? (Java 8+)
```java
interface A {
    default void print() {
        System.out.print("A ");
    }
}

interface B {
    default void print() {
        System.out.print("B ");
    }
}

class C implements A, B {
    public void print() {
        A.super.print();
        B.super.print();
    }
}

public class Test {
    public static void main(String[] args) {
        new C().print();
    }
}
```
A) A  
B) B  
C) A B  
D) Compilation error

**Answer: C) A B**

**Explanation**: When a class implements multiple interfaces with conflicting default methods, it must override the method to resolve the ambiguity. Inside the override, you can explicitly call specific interface default methods using `InterfaceName.super.methodName()`. This code calls both, printing "A B".

---

### Question 8
Which statement about functional interfaces is TRUE?
```java
@FunctionalInterface
interface Calculator {
    int calculate(int a, int b);
}
```
A) Functional interfaces cannot have default methods  
B) Functional interfaces must have exactly one abstract method  
C) Functional interfaces cannot have static methods  
D) The @FunctionalInterface annotation is required

**Answer: B) Functional interfaces must have exactly one abstract method**

**Explanation**: A functional interface has exactly one abstract method (Single Abstract Method interface). They can have default methods, static methods, and private methods. The `@FunctionalInterface` annotation is optional but recommended—it causes a compilation error if the interface doesn't meet the functional interface contract.

---

### Question 9
What is the result?
```java
interface Vehicle {
    void start();
}

public class Test {
    public static void main(String[] args) {
        Vehicle v = new Vehicle();  // Line X
        v.start();
    }
}
```
A) Compiles and runs successfully  
B) Compilation error at Line X  
C) Runtime error at Line X  
D) NullPointerException

**Answer: B) Compilation error at Line X**

**Explanation**: Interfaces cannot be instantiated directly. You must create an instance of a class that implements the interface. Line X attempts to use `new Vehicle()`, which is illegal. You can reference implementing classes through interface types, but cannot instantiate the interface itself.

---

### Question 10
What is the output? (Java 9+)
```java
interface Logger {
    private String format(String msg) {
        return "[LOG] " + msg;
    }
    
    default void log(String message) {
        System.out.println(format(message));
    }
}

class MyLogger implements Logger { }

public class Test {
    public static void main(String[] args) {
        new MyLogger().log("Hello");
    }
}
```
A) Hello  
B) [LOG] Hello  
C) Compilation error  
D) Runtime error

**Answer: B) [LOG] Hello**

**Explanation**: Java 9 introduced private methods in interfaces to enable code reuse between default methods. The private `format()` method is called by the default `log()` method. `MyLogger` inherits the default `log()` method, which uses the private helper method to format the output.

---

### Question 11
Which interface declaration is INVALID?
A)
```java
interface A extends B, C { }
```
B)
```java
interface B {
    int getValue();
    default String getName() { return "B"; }
}
```
C)
```java
interface C {
    private void helper() { }
    static int count = 0;
}
```
D)
```java
interface D {
    void method();
    static void utility() { }
}
```

**Answer: C)**

**Explanation**: Interface fields are implicitly `public static final` and must be initialized. `static int count = 0;` would be valid if it's a constant, but attempting to change it later would fail. More critically, interface fields cannot just be `static`—they must be `final`. Option A is valid (interface extending multiple interfaces), Option B is valid (abstract and default method), Option D is valid (abstract and static method).

---

### Question 12
What happens with this code?
```java
interface Animal {
    default void eat() {
        System.out.print("Eating ");
    }
}

class Dog implements Animal {
    void eat() {  // Line X
        System.out.print("Dog eating ");
    }
}
```
A) Compiles successfully  
B) Compilation error at Line X: method must be public  
C) Runtime error  
D) Prints "Eating Dog eating"

**Answer: B) Compilation error at Line X: method must be public**

**Explanation**: When overriding a method from an interface (including default methods), you cannot reduce the visibility. Interface methods are implicitly public, so the implementing class must declare the method as public. Using package-private (no modifier) reduces visibility, causing a compilation error.

---

### Question 13
What is true about marker interfaces?
```java
interface Serializable {
    // No methods or fields
}
```
A) Marker interfaces must have at least one method  
B) Marker interfaces are used to tag or mark classes  
C) Marker interfaces cannot be implemented  
D) Marker interfaces are deprecated in modern Java

**Answer: B) Marker interfaces are used to tag or mark classes**

**Explanation**: Marker interfaces have no methods or fields and serve to mark or tag a class for a specific purpose. Java's `Serializable` is a classic example—it marks a class as being eligible for serialization. They don't provide methods but signal to frameworks/compilers that the class has certain capabilities.

---

### Question 14
What is the output?
```java
interface A {
    default void print() {
        System.out.print("A");
    }
}

interface B extends A {
    default void print() {
        System.out.print("B");
    }
}

class C implements B {
}

public class Test {
    public static void main(String[] args) {
        new C().print();
    }
}
```
A) A  
B) B  
C) AB  
D) Compilation error

**Answer: B) B**

**Explanation**: When an interface extends another interface and overrides a default method, the more specific interface's method is used. Interface B extends A and overrides `print()`. Class C implements B, so it inherits B's version of `print()`. This demonstrates the "subtype wins" rule for default method resolution.

---

### Question 15
Which code correctly calls a static method from an interface?
```java
interface Utils {
    static String format(String s) {
        return s.toUpperCase();
    }
}

class Helper implements Utils { }
```
A) `Helper.format("hello")`  
B) `new Helper().format("hello")`  
C) `Utils.format("hello")`  
D) `format("hello")`

**Answer: C) `Utils.format("hello")`**

**Explanation**: Static methods in interfaces must be called using the interface name, not through implementing classes or instances. Unlike default methods, static methods are not inherited. Option C is the only correct way to call the static method.

---

### Question 16
What is required to make this code compile?
```java
@FunctionalInterface
interface Processor {
    void process(String input);
    void validate(String input);  // Line X
}
```
A) Remove Line X  
B) Remove @FunctionalInterface annotation  
C) Make validate() a default method  
D) Either A, B, or C

**Answer: D) Either A, B, or C**

**Explanation**: Functional interfaces must have exactly ONE abstract method. This interface has two abstract methods, violating the functional interface contract. You can fix it by: removing one abstract method (A), removing the annotation to stop enforcing the rule (B), or making one method a default method (C). Any of these would make the code compile.

---

### Question 17
What is the result?
```java
class Parent {
    public void display() {
        System.out.print("Parent ");
    }
}

interface MyInterface {
    default void display() {
        System.out.print("Interface ");
    }
}

class Child extends Parent implements MyInterface {
}

public class Test {
    public static void main(String[] args) {
        new Child().display();
    }
}
```
A) Parent  
B) Interface  
C) Parent Interface  
D) Compilation error

**Answer: A) Parent**

**Explanation**: When there's a conflict between a class method and an interface default method, the class method wins. This is the "class wins over interface" rule. Child inherits `display()` from Parent, and even though it implements MyInterface with a default `display()`, the Parent class method takes precedence.

---

### Question 18
Which statement about interface constants is TRUE?
```java
interface Config {
    int MAX_SIZE = 100;
    String NAME = "App";
}
```
A) MAX_SIZE and NAME are instance variables  
B) MAX_SIZE and NAME are public static final  
C) MAX_SIZE can be modified by implementing classes  
D) NAME must be declared as public static final explicitly

**Answer: B) MAX_SIZE and NAME are public static final**

**Explanation**: All fields in interfaces are implicitly `public static final` constants. You don't need to explicitly declare these modifiers (though you can). They cannot be modified, are shared across all implementing classes, and are accessed statically.

---

### Question 19
What happens when you compile this code?
```java
interface A {
    default void method() {
        System.out.println("A");
    }
}

interface B {
    default void method() {
        System.out.println("B");
    }
}

class C implements A, B {
    // Missing override
}
```
A) Compiles successfully, uses A's method  
B) Compiles successfully, uses B's method  
C) Compilation error: must override method  
D) Runtime error when calling method

**Answer: C) Compilation error: must override method**

**Explanation**: When a class implements multiple interfaces with conflicting default methods (same signature), the class MUST override the method to resolve the ambiguity. The compiler cannot automatically choose which default method to use. Class C must provide its own implementation or explicitly call one of the super methods.

---

### Question 20
What is true about this interface? (Java 8+)
```java
interface Service {
    void execute();
    
    default void start() {
        System.out.println("Starting");
    }
    
    static void initialize() {
        System.out.println("Initializing");
    }
    
    private void log(String msg) {
        System.out.println("LOG: " + msg);
    }
}
```
A) This interface cannot compile  
B) Implementing classes must implement all four methods  
C) Implementing classes must implement only execute()  
D) Private methods in interfaces require Java 8+

**Answer: C) Implementing classes must implement only execute()**

**Explanation**: Implementing classes must provide implementations only for abstract methods. `execute()` is abstract (must implement), `start()` is default (inherited), `initialize()` is static (not inherited), and `log()` is private (not accessible). Only `execute()` requires implementation. Note: private methods in interfaces require Java 9+, not Java 8.

---

## Answer Summary
1. B  2. B  3. C  4. C  5. C  
6. B  7. C  8. B  9. B  10. B  
11. C  12. B  13. B  14. B  15. C  
16. D  17. A  18. B  19. C  20. C
